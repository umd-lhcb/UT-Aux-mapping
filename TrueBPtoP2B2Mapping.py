#!/usr/bin/env python
#
# Author: Ben Flaggs
# License: BSD 2-clause
# Last Change: Sun Dec 13, 2020 at 11:31 PM +0100

from pathlib import Path

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.io import write_to_csv
from pyUTM.sim import CurrentFlow

from UT_Aux_mapping.const import input_dir, output_dir
from UT_Aux_mapping.helpers import gen_filename
from UT_Aux_mapping.helpers import filter_comp
from UT_Aux_mapping.helpers import post_filter_any

true_bp_netlist = input_dir / Path("true_backplane.net")
true_p2b2_netlist = input_dir / Path("true_p2b2.net")

inner_bb_to_true_p2b2_mapping_filename = output_dir / \
    Path(gen_filename(__file__))

#####################
# Read all netlists #
#####################

# Default net hopping should work for Inner BB.
NetHopper = CurrentFlow()

TrueBPReader = PcadNaiveReader(true_bp_netlist)
true_bp_descr = TrueBPReader.read()

# TrueBPHopper = CurrentFlow([PLACE COMPONENTS TO TREAT AS COPPER HERE])

# This CurrentFlow maps the nets accurately and outputs exactly what we want
# to the final .csv file in the "output" directory.
TrueBPHopper = CurrentFlow([r"^RT\d"])

# This CurrentFlow maps the nets accurately but it lists out the incorrect final
# net name for the True Backplane. This is because of the resistors (RXXX)
# being treated as copper. Treating these components as copper means that the
# signal will continue to be traced further in the board resulting in a CORRECT
# net name but this is NOT the FINAL net name that we want when tracing.
# TrueBPHopper = CurrentFlow([r"^RT\d", r"^RBSP_\d", r"^R\d", r"^NT\d+"])

PcadReader.make_equivalent_nets_identical(
    true_bp_descr, TrueBPHopper.do(true_bp_descr)
)

# Default net hopping should also work for True P2B2.
TrueP2B2Reader = PcadReader(true_p2b2_netlist)
true_p2b2_descr = TrueP2B2Reader.read(NetHopper)


#############
# Filtering #
#############

true_bp_result = filter_comp(true_bp_descr,
                             r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$")

true_p2b2_result = filter_comp(
    true_p2b2_descr, r"^JP_JPL_+|^JP_JPU_+|^JP_PT_+|^JPU1$|^JPU2$|^JPU3$"
)

# True Backplane ###############################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later, for now we want to trace
# the GNDs to make sure they stay as GNDs)

filter_bp_throw_gnd = post_filter_any(lambda x: x[1] not in ["29"])
true_bp_result_list = list(filter(filter_bp_throw_gnd, true_bp_result))

# True P2B2 ####################################################################
# NOT USED IN FINDING CONNECTIONS (throw out DRAIN later)

filter_p2b2_throw_drain = post_filter_any(lambda x: x[0] not in ["DW1", "DW2"])
true_p2b2_result_list = list(filter(filter_p2b2_throw_drain, true_p2b2_result))


############################################################
# Find Inner BB to True Backplane to True P2B2 Connections #
############################################################

inner_bb_to_true_p2b2_map = []


#################
# Output to csv #
#################

# True Backplane -> True P2B2 -> Outer BB ######################################

write_to_csv(
    inner_bb_to_true_p2b2_mapping_filename,
    inner_bb_to_true_p2b2_map,
    ["Inner BB net", "Inner BB connector",
     "True Backplane net", "True Backplane connector",
     "True P2B2 net"],
)
