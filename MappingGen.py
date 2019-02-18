#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Mon Feb 18, 2019 at 03:46 PM -0500

import re

from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, './pyUTM')

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.sim import CurrentFlow

input_dir = Path('input')

comet_netlist = input_dir / Path('comet.net')
comet_db_netlist = input_dir / Path('comet_db.net')
path_finder_netlist = input_dir / Path('path_finder.net')
dcb_netlist = input_dir / Path('dcb.net')


###########
# Helpers #
###########

# Regularize input #############################################################

def split_rn(descr, regexp=r'^RN\d+_\d$'):
    rn_split_dict = {
        '1': 'A',
        '8': 'A',
        '2': 'B',
        '7': 'B',
        '3': 'C',
        '6': 'C',
        '4': 'D',
        '5': 'D'
    }
    result = defaultdict(list)

    for net, comps in descr.items():
        for c in comps:
            if bool(re.search(regexp, c[0])):
                new_c = list(c)
                new_c[0] += rn_split_dict[c[1]]
                result[net].append(tuple(new_c))

            else:
                result[net].append(c)

    return dict(result)


# Filtering ####################################################################

def filter_comp(descr, regexp=r'^J\d+|^IC3_1+'):
    filtered = []

    for net, comps in descr.items():
        processed_comps = [x for x in comps if bool(re.match(regexp, x[0]))]

        # Can't figure out any relationship if a list contains only a single
        # item.
        # We also do deduplication here.
        # Also make sure there's at least a connector component.
        if len(processed_comps) > 1 and processed_comps not in filtered \
                and True in map(lambda x: x[0].startswith('J'),
                                processed_comps):
            filtered.append(processed_comps)

    return filtered


def post_filter_exist(functor):
    def filter_functor(l):
        return True if True in map(functor, l) else False

    return filter_functor


def post_filter_any(functor):
    def filter_functor(l):
        return False if False in map(functor, l) else True

    return filter_functor


# Make dictionaries to find connectivity between components  ###################

def make_comp_netname_dict(descr):
    result = {}

    for net, comps in descr.items():
        for c in comps:
            result[c] = net

    return result


def make_comp_comp_dict(nested, key_comp, value_comp, strip_kw='_1'):
    result = {}

    for comps in nested:
        key_candidates = list(filter(lambda x: x[0] == key_comp, comps))
        value_candidates = list(filter(lambda x: x[0] == value_comp, comps))

        if key_candidates and value_candidates:
            if len(key_candidates) > 1 or len(value_candidates) > 1:
                raise ValueError(
                    'Unable to construct a bijection for key: {}, value: {}'.format(
                        key_candidates, value_candidates
                    ))
            else:
                # We want to strip out the '_1' part
                key = list(key_candidates[0])
                value = list(value_candidates[0])

                key[0] = key[0].strip(strip_kw)
                value[0] = value[0].strip(strip_kw)

                result[tuple(key)] = tuple(value)

    return result


#####################
# Read all netlists #
#####################

# NOTE: Net hopping won't work for COMET, nor COMET DB, because of the special
# resistors RNXX that have 8 legs, instead of 2.
CometHopper = CurrentFlow([r'^R\d+', r'^NT\d+', r'^RN\d+_\d[ABCD]', r'^C\d+'])
CometDBHopper = CurrentFlow([r'^R\d+', r'^NT\d+', r'^RN\d+[ABCD]'])

CometReader = PcadNaiveReader(comet_netlist)
CometDBReader = PcadNaiveReader(comet_db_netlist)

comet_descr = split_rn(CometReader.read())
comet_db_descr = split_rn(
    CometDBReader.read(),
    regexp=r'^RN((?!5$|6$|9$|12$|15$|18$|21$|24$|27$|39$|30$|33$|36$)\d+)$'
)

# Manually do net hopping for COMET and COMET DB.
PcadReader.make_equivalent_nets_identical(
    comet_descr, CometHopper.do(comet_descr))
PcadReader.make_equivalent_nets_identical(
    comet_db_descr, CometDBHopper.do(comet_db_descr))

# Default net hopping should work for Pathfinder and DCB.
NetHopper = CurrentFlow()

PathFinderReader = PcadReader(path_finder_netlist)
DcbReader = PcadReader(dcb_netlist)

path_finder_descr = PathFinderReader.read(NetHopper)
dcb_descr = DcbReader.read(NetHopper)


#############
# Filtering #
#############

comet_result = filter_comp(comet_descr, '^J4_1$|^J6_1$|^J1$|^IC3_1$')
comet_db_result = filter_comp(comet_db_descr, '^J4|^J6')
path_finder_result = filter_comp(path_finder_descr)
dcb_result = filter_comp(dcb_descr)

# GND is not useful
filter_comet_throw_gnd = post_filter_any(
    lambda x: x[1] not in ['SHIELD1', 'SHIELD2'])

comet_result = filter(filter_comet_throw_gnd, comet_result)
# comet_db_result = list(filter(filter_throw_gnd, comet_db_result))

# Remove the 6 pairs of special differential lines. We'll add them back later.
filter_comet_throw_special_diff = post_filter_any(
    lambda x: not (
        x[0] == 'IC3_1' and
        x[1] in ['112', '113', '114', '115', '116', '117', '159', '160', '161',
                 '163', '164', '165']
    )
)

comet_result = list(filter(filter_comet_throw_special_diff, comet_result))

# Remove GND for COMET DB as well
comet_db_result = list(filter(filter_comet_throw_gnd, comet_db_result))


####################################
# Find COMET J1 to COMET J4 and J6 #
####################################

comet_j1_j4 = make_comp_comp_dict(comet_result, 'J1', 'J4_1')
comet_j1_j6 = make_comp_comp_dict(comet_result, 'J1', 'J6_1')
comet_j4_fpga = make_comp_comp_dict(comet_result, 'J4_1', 'IC3_1')
comet_j6_fpga = make_comp_comp_dict(comet_result, 'J6_1', 'IC3_1')

# Add 6 pairs of special differential connections back
comet_j6_fpga[('IC3', '112')] = ('J6', '11')
comet_j6_fpga[('IC3', '113')] = ('J6', '17')
comet_j6_fpga[('IC3', '114')] = ('J6', '13')
comet_j6_fpga[('IC3', '115')] = ('J6', '19')
comet_j6_fpga[('IC3', '116')] = ('J6', '25')
comet_j6_fpga[('IC3', '117')] = ('J6', '27')
comet_j6_fpga[('IC3', '159')] = ('J6', '68')
comet_j6_fpga[('IC3', '160')] = ('J6', '70')
comet_j6_fpga[('IC3', '161')] = ('J6', '74')
comet_j6_fpga[('IC3', '163')] = ('J6', '76')
comet_j6_fpga[('IC3', '164')] = ('J6', '80')
comet_j6_fpga[('IC3', '165')] = ('J6', '82')


###############################################
# Find COMET DB connections between J4 and J6 #
###############################################

comet_db_j4_j6 = make_comp_comp_dict(comet_db_result, 'J4', 'J6')
comet_db_j6_j4 = make_comp_comp_dict(comet_db_result, 'J6', 'J4')
