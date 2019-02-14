#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Wed Feb 13, 2019 at 09:46 PM -0500

import re

from pathlib import Path

import sys
sys.path.insert(0, './pyUTM')

from pyUTM.io import PcadReader
from pyUTM.sim import CurrentFlow

input_dir = Path('input')

comet_netlist = input_dir / Path('comet.net')
comet_daughter_netlist = input_dir / Path('comet_daughter.net')
dcb_netlist = input_dir / Path('dcb.net')
path_finder_netlist = input_dir / Path('path_finder.net')


###########
# Helpers #
###########

def filter_comp(descr, regexp=r'^J\d+|^RN\d+'):
    filtered = {}

    for net, comps in descr.items():
        filtered_comps = [x for x in comps if bool(re.match(regexp, x[0]))]

        # Can't figure out any relationship if a list contains only a single
        # item.
        if len(filtered_comps) > 1:
            filtered[net] = filter_comp

    return filtered


#####################
# Read all netlists #
#####################

nethopper = CurrentFlow()

CometReader = PcadReader(comet_netlist)
CometDaughterReader = PcadReader(comet_daughter_netlist)
DcbReader = PcadReader(dcb_netlist)
PathFinderReader = PcadReader(path_finder_netlist)

comet_descr = CometReader.read(nethopper)
comet_daughter_descr = CometDaughterReader.read(nethopper)
dcb_descr = DcbReader.read(nethopper)
path_finder_descr = PathFinderReader.read(nethopper)


#############################################
# Find FPGA pins and inter-board connectors #
#############################################

comet_result = filter_comp(comet_descr)
comet_daughte_result = filter_comp(comet_daughter_descr)
dcb_result = filter_comp(dcb_descr)
path_finder_result = filter_comp(path_finder_descr)
