#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Sun Dec 13, 2020 at 11:29 PM +0100

import re

from pathlib import Path

from pyUTM.io import PcadNaiveReader
from pyUTM.sim import CurrentFlow

from UT_Aux_mapping.const import input_dir

true_bp_netlist = input_dir / Path("mirror_backplane.net")


###########
# Helpers #
###########

def filter_netname(nets, name):
    for n in nets:
        if re.search(name, n):
            return True
    return False


def netname_printout(nets, name):
    for n in nets:
        if re.search(name, n):
            print(n)


#################
# True BP debug #
#################

TrueBPReader = PcadNaiveReader(true_bp_netlist)
true_bp_descr = TrueBPReader.read()

TrueBPHopper = CurrentFlow([r'^R\d+', r'^RSP_\d+'])
true_nets_hopped = TrueBPHopper.do(true_bp_descr)
