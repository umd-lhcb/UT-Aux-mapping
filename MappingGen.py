#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Thu Feb 14, 2019 at 05:09 PM -0500

import re

from pathlib import Path

import sys
sys.path.insert(0, './pyUTM')

from pyUTM.io import PcadReader
from pyUTM.sim import CurrentFlow

input_dir = Path('input')

comet_netlist = input_dir / Path('comet.net')
comet_daughter_netlist = input_dir / Path('comet_daughter.net')
path_finder_netlist = input_dir / Path('path_finder.net')
dcb_netlist = input_dir / Path('dcb.net')


###########
# Helpers #
###########

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
CometDaughterReader = PcadReader(comet_daughter_netlist)
PathFinderReader = PcadReader(path_finder_netlist)
DcbReader = PcadReader(dcb_netlist)

comet_descr = CometReader.read(nethopper)
comet_daughter_descr = CometDaughterReader.read(nethopper)
path_finder_descr = PathFinderReader.read(nethopper)
dcb_descr = DcbReader.read(nethopper)


#############################################
# Find FPGA pins and inter-board connectors #
#############################################

comet_result = filter_comp(comet_descr, '^J4_1$|^J6_1$|^J1$|^IC3_1$')
comet_daughter_result = filter_comp(comet_daughter_descr)
path_finder_result = filter_comp(path_finder_descr)
dcb_result = filter_comp(dcb_descr)

# GND is not useful
comet_throw_gnd = post_filter_any(lambda x: x[1] not in ['SHIELD1', 'SHIELD2'])
comet_result = list(filter(comet_throw_gnd, comet_result))


################################
# Find COMET J1 to COMET DB J4 #
################################
