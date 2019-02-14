#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Wed Feb 13, 2019 at 09:28 PM -0500

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

comet_result = [x for x in comet_descr if bool(re.match(r'^J\d+|^RN\d+', x[0]))]
comet_daughte_result = [x for x in comet_daughter_descr
                        if bool(re.match(r'^J\d+|^RN\d+', x[0]))]
dcb_result = [x for x in dcb_descr if bool(re.match(r'^J\d+', x[0]))]
path_finder_result = [x for x in path_finder_descr
                      if bool(re.match(r'^J\d+', x[0]))]
