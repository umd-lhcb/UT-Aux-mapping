#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Feb 15, 2019 at 03:58 PM -0500

import re

from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, './pyUTM')

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.sim import CurrentFlow

input_dir = Path('input')

comet_netlist = input_dir / Path('comet.net')
comet_daughter_netlist = input_dir / Path('comet_daughter.net')
path_finder_netlist = input_dir / Path('path_finder.net')
dcb_netlist = input_dir / Path('dcb.net')


###########
# Helpers #
###########

# Regularize input #############################################################

def split_rn(descr, regexp=r'^RN\d+$'):
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
            if bool(re.search(regexp), c[0]):
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


def make_comp_comp_dict(nested, key_comp, value_comp):
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
                result[key_candidates[0]] = value_candidates[0]

    return result


#####################
# Read all netlists #
#####################

# NOTE: Net hopping won't work for COMET, nor COMET DB, because of the special
# resistors RNXX that have 8 legs, instead of 2.
comethopper = CurrentFlow([r'^R\d+', r'^C\d+', r'^NT\d+', r'^RN\d+[ABCD]'])

CometReader = PcadNaiveReader(comet_netlist)
CometDaughterReader = PcadNaiveReader(comet_daughter_netlist)

comet_descr = split_rn(CometReader.read())
comet_daughter_descr = split_rn(CometDaughterReader.read())

# Manually do net hopping for COMET and COMET DB.
comet_descr = PcadReader.make_equivalent_nets_identical(
    comet_descr, comethopper.do(comet_descr))
comet_daughter_descr = PcadReader.make_equivalent_nets_identical(
    comet_daughter_descr, comethopper.do(comet_daughter_descr))

# Default net hopping should work for Pathfinder and DCB.
nethopper = CurrentFlow()

PathFinderReader = PcadReader(path_finder_netlist)
DcbReader = PcadReader(dcb_netlist)

path_finder_descr = PathFinderReader.read(nethopper)
dcb_descr = DcbReader.read(nethopper)


#############
# Filtering #
#############

comet_result = filter_comp(comet_descr, '^J4_1$|^J6_1$|^J1$|^IC3_1$')
path_finder_result = filter_comp(path_finder_descr)
dcb_result = filter_comp(dcb_descr)

# GND is not useful
filter_comet_throw_gnd = post_filter_any(
    lambda x: x[1] not in ['SHIELD1', 'SHIELD2'])
comet_result = list(filter(filter_comet_throw_gnd, comet_result))


####################################
# Find COMET J1 to COMET J4 and J6 #
####################################

comet_j1_j4 = make_comp_comp_dict(comet_result, 'J1', 'J4_1')
comet_j1_j6 = make_comp_comp_dict(comet_result, 'J1', 'J6_1')
comet_fpga_j4 = make_comp_comp_dict(comet_result, 'J4_1', 'IC3_1')
comet_fpga_j6 = make_comp_comp_dict(comet_result, 'J6_1', 'IC3_1')


##############################################
# Find connection between COMET and COMET DB #
##############################################

comet_ref = make_comp_netname_dict(comet_descr)
comet_daughter_ref = make_comp_netname_dict(comet_daughter_descr)
