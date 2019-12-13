#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Fri Dec 13, 2019 at 02:24 PM -0500

from pathlib import Path

import sys
sys.path.insert(0, "./pyUTM")

from pyUTM.io import PcadNaiveReader
from pyUTM.sim import CurrentFlow

from CometDcbMapping import input_dir

true_bp_netlist = input_dir / Path("mirror_backplane.net")


#################
# True BP debug #
#################

TrueBPReader = PcadNaiveReader(true_bp_netlist)
TrueBPHopper = CurrentFlow([r'^R\d+', r'^RBSP_\d+', r'^RB_\d+', r'^RSB_\d+'])
true_nets_hopped = TrueBPHopper.do()
