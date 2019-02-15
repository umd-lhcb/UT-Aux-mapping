#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Feb 15, 2019 at 02:06 AM -0500

import re

from pathlib import Path

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

def make_comp_dict(descr):
    result = {}

    return result


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


#####################
# Read all netlists #
#####################

nethopper = CurrentFlow()


CometReader = PcadReader(comet_netlist)

# NOTE: Net hopping won't work for COMET DB, because of the special resistors
# RNXX that have 4 legs, instead of 2.
CometDaughterReader = PcadNaiveReader(comet_daughter_netlist)

PathFinderReader = PcadReader(path_finder_netlist)
DcbReader = PcadReader(dcb_netlist)

comet_descr = CometReader.read(nethopper)
comet_daughter_descr = CometDaughterReader.read()
path_finder_descr = PathFinderReader.read(nethopper)
dcb_descr = DcbReader.read(nethopper)


#############
# Filtering #
#############

comet_result = filter_comp(comet_descr, '^J4_1$|^J6_1$|^J1$|^IC3_1$')
path_finder_result = filter_comp(path_finder_descr)
dcb_result = filter_comp(dcb_descr)

# GND is not useful
comet_throw_gnd = post_filter_any(lambda x: x[1] not in ['SHIELD1', 'SHIELD2'])
comet_result = list(filter(comet_throw_gnd, comet_result))


####################################
# Find COMET J1 to COMET J4 and J6 #
####################################
