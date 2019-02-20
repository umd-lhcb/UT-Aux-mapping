#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Wed Feb 20, 2019 at 03:36 AM -0500

import re

from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, './pyUTM')

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.sim import CurrentFlow

input_dir = Path('input')
output_dir = Path('output')

comet_netlist = input_dir / Path('comet.net')
comet_db_netlist = input_dir / Path('comet_db.net')
path_finder_netlist = input_dir / Path('path_finder.net')
dcb_netlist = input_dir / Path('dcb.net')

debug_comet_mapping_filename = output_dir / Path('DebugCometMapping.csv')


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

                key[0] = key[0].replace(strip_kw, '')
                value[0] = value[0].replace(strip_kw, '')

                result[tuple(key)] = tuple(value)

    return result


def make_comp_comp_dict_bidirectional(nested):
    # NOTE: Here 'nested' should be a nx2 tensor
    result = {}

    for key1, key2 in nested:
        result[key1] = key2
        result[key2] = key1

    return result


# Output #######################################################################

def write_mapping_to_csv(filename, data,
                         header=['COMET connector', 'COMET FPGA'],
                         mode='w', eol='\n'):
    with open(filename, mode) as f:
        f.write(','.join(header) + eol)
        for row in data:
            f.write(','.join(row) + eol)


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
path_finder_result = filter_comp(path_finder_descr, '^JD10$|^COMET')
dcb_result = filter_comp(dcb_descr)

# COMET ########################################################################

# GND is not useful
filter_comet_throw_gnd = post_filter_any(
    lambda x: x[1] not in ['SHIELD1', 'SHIELD2'])
comet_result = filter(filter_comet_throw_gnd, comet_result)

# Remove the 6 pairs of special differential lines. We'll add them back later.
filter_comet_throw_special_diff = post_filter_any(
    lambda x: not (
        x[0] == 'IC3_1' and
        x[1] in ['112', '113', '114', '115', '116', '117', '159', '160', '161',
                 '163', '164', '165']
    )
)
comet_result = list(filter(filter_comet_throw_special_diff, comet_result))


# COMET DB #####################################################################

# Remove GND for COMET DB as well
comet_db_result = filter(filter_comet_throw_gnd, comet_db_result)

# DIFF_TERM_STV is not useful
filter_comet_db_throw_diff_term = post_filter_any(lambda x: x != ('J4', '5'))
comet_db_result = filter(filter_comet_db_throw_diff_term, comet_db_result)

# Remove RJ45-related connections
filter_comet_db_throw_rj45 = post_filter_any(
    lambda x: x != ('J6', '26') and x != ('J6', '31'))
comet_db_result = list(filter(filter_comet_db_throw_rj45, comet_db_result))


####################################
# Find COMET J1 to COMET J4 and J6 #
####################################

comet_j1_to_j4 = make_comp_comp_dict(comet_result, 'J1', 'J4_1')
comet_j1_to_j6 = make_comp_comp_dict(comet_result, 'J1', 'J6_1')
comet_j4_to_fpga = make_comp_comp_dict(comet_result, 'J4_1', 'IC3_1')
comet_j6_to_fpga = make_comp_comp_dict(comet_result, 'J6_1', 'IC3_1')

# Add 6 pairs of special differential connections back
comet_j6_to_fpga[('J6', '11')] = ('IC3', '112')
comet_j6_to_fpga[('J6', '17')] = ('IC3', '113')
comet_j6_to_fpga[('J6', '13')] = ('IC3', '114')
comet_j6_to_fpga[('J6', '19')] = ('IC3', '115')
comet_j6_to_fpga[('J6', '25')] = ('IC3', '116')
comet_j6_to_fpga[('J6', '27')] = ('IC3', '117')
comet_j6_to_fpga[('J6', '68')] = ('IC3', '159')
comet_j6_to_fpga[('J6', '70')] = ('IC3', '160')
comet_j6_to_fpga[('J6', '74')] = ('IC3', '161')
comet_j6_to_fpga[('J6', '76')] = ('IC3', '163')
comet_j6_to_fpga[('J6', '80')] = ('IC3', '164')
comet_j6_to_fpga[('J6', '82')] = ('IC3', '165')

# Combine dictionaries to make queries easier
comet_j1_to_j4_j6 = {**comet_j1_to_j4, **comet_j1_to_j6}
comet_j4_j6_to_fpga = {**comet_j4_to_fpga, **comet_j6_to_fpga}


###############################################
# Find COMET DB connections between J4 and J6 #
###############################################

comet_db_j4_bto_j6 = make_comp_comp_dict_bidirectional(comet_db_result)


########################################
# Find COMET to Pathfinder connections #
########################################

pathfinder_comet_a_j1_to_jd10 = make_comp_comp_dict(path_finder_result,
                                                    'COMET_A_J1', 'JD10')


####################
# Make connections #
####################

connections = defaultdict(list)

# COMET -> COMET DB -> COMET ###################################################

comet_j1_to_fpga = {}

for j1_pin, comet_pin in comet_j1_to_j4_j6.items():
    # NOTE: It seems that no pin conversion required for J4 COMET and COMET DB,
    # but for J6, x on COMET is x+1 on COMET DB.
    if comet_pin[0] == 'J4':
        comet_db_pin = comet_db_j4_bto_j6[comet_pin]
    else:
        comet_db_pin = comet_db_j4_bto_j6[('J6', str(int(comet_pin[1])+1))]
        comet_db_pin = ('J6', str(int(comet_db_pin[1])+1))

    comet_j1_to_fpga[j1_pin] = comet_j4_j6_to_fpga[comet_db_pin]


#################
# Output to csv #
#################

# Debug ########################################################################

comet_j1_fpga_data = [('-'.join(key), '-'.join(value))
                      for key, value in comet_j1_to_fpga.items()]
comet_j1_fpga_data.sort(key=lambda x: int(x[0].split('-')[1]))

write_mapping_to_csv(debug_comet_mapping_filename, comet_j1_fpga_data)
