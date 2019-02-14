#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Wed Feb 13, 2019 at 11:26 PM -0500

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

def filter_comp(descr, regexp=r'^J\d+_1|^IC3_1+'):
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


def post_filter(functor):
    def filter_functor(l):
        return True if True in map(functor, l) else False

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

comet_result = filter_comp(comet_descr)
comet_daughter_result = filter_comp(comet_daughter_descr, r'^J\d+')
path_finder_result = filter_comp(path_finder_descr, r'^J\d+')
dcb_result = filter_comp(dcb_descr, r'^J\d+')


##################
# Post filtering #
##################

comet_filter = post_filter(lambda x: 'IC3_1' in x[0])
comet_result = list(filter(comet_filter, comet_result))
