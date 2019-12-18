#!/usr/bin/env python
#
# Author: Ben Flaggs
# License: BSD 2-clause
# Last Change: Wed Dec 18, 2019 at 04:33 PM -0500

from pathlib import Path

import sys
sys.path.insert(0, "./pyUTM")

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.io import write_to_csv
from pyUTM.sim import CurrentFlow

from CometDcbMapping import input_dir, output_dir
from CometDcbMapping import filter_comp
from CometDcbMapping import post_filter_any
from CometDcbMapping import make_comp_netname_dict

true_bp_netlist = input_dir / Path("true_backplane.net")
inner_bb_netlist = input_dir / Path("inner_bb.net")
true_p2b2_netlist = input_dir / Path("true_p2b2.net")

inner_bb_to_true_bp_mapping_filename = output_dir / Path("InnerBBTrueBPMapping.csv")
inner_bb_to_true_p2b2_mapping_filename = output_dir / Path("InnerBBTrueP2B2Mapping.csv")

#####################
# Read all netlists #
#####################

# Default net hopping should work for Inner BB.
NetHopper = CurrentFlow()

InnerBBReader = PcadReader(inner_bb_netlist)
inner_bb_descr = InnerBBReader.read(NetHopper)

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

inner_bb_result = filter_comp(
    inner_bb_descr, r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$"
)

true_bp_result = filter_comp(true_bp_descr,
                             r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$")

true_p2b2_result = filter_comp(
    true_p2b2_descr, r"^JP_JPL_+|^JP_JPU_+|^JP_PT_+|^JPU1$|^JPU2$|^JPU3$"
)

# Inner BB #####################################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later, for now we want to trace
# the GNDs to make sure they stay as GNDs)

filter_inner_bb_throw_out = post_filter_any(
    lambda x: x[1] not in ["9", "10", "16", "17", "18", "19", "20", "24", "25",
                           "26", "27", "28", "29", "30"]
)
inner_bb_result_list = list(filter(filter_inner_bb_throw_out,
                                   inner_bb_result))

# True Backplane #############################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later, for now we want to trace
# the GNDs to make sure they stay as GNDs)

filter_bp_throw_gnd = post_filter_any(lambda x: x[1] not in ["29"])
true_bp_result_list = list(filter(filter_bp_throw_gnd, true_bp_result))

# True P2B2 ##################################################################
# NOT USED IN FINDING CONNECTIONS (throw out DRAIN later)

filter_p2b2_throw_drain = post_filter_any(lambda x: x[0] not in ["DW1", "DW2"])
true_p2b2_result_list = list(filter(filter_p2b2_throw_drain, true_p2b2_result))


##################################################
# Find Inner BB to True Backplane Connections #
##################################################

# Inner BB -> True Backplane ################################################

inner_bb_ref = make_comp_netname_dict(inner_bb_descr)
true_bp_ref = make_comp_netname_dict(true_bp_descr)

compnames_inner_bb = inner_bb_ref.keys()
netnames_inner_bb = inner_bb_ref.values()
list_comp_inner_bb = list(compnames_inner_bb)
list_nets_inner_bb = list(netnames_inner_bb)


compnames_true_bp = true_bp_ref.keys()
netnames_true_bp = true_bp_ref.values()
list_comp_bp = list(compnames_true_bp)
list_nets_bp = list(netnames_true_bp)

true_p2b2_ref = make_comp_netname_dict(true_p2b2_descr)

compnames_true_p2b2 = true_p2b2_ref.keys()
netnames_true_p2b2 = true_p2b2_ref.values()
list_comp_p2b2 = list(compnames_true_p2b2)
list_nets_p2b2 = list(netnames_true_p2b2)

inner_bb_to_true_bp_map = []
inner_bb_to_true_p2b2_map = []

for i in range(len(list_nets_inner_bb)):
    row = []
    row_larger = []
    for j in range(len(list_nets_bp)):
        if (
            list_comp_inner_bb[i][0] == list_comp_bp[j][0] and
            list_comp_inner_bb[i][1] == list_comp_bp[j][1]
        ):

            row.append(list_nets_inner_bb[i])
            row.append("-".join(list_comp_inner_bb[i]))
            row.append(list_nets_bp[j])

            inner_bb_to_true_bp_map.append(row)

            row_larger.append(list_nets_inner_bb[i])
            row_larger.append("-".join(list_comp_inner_bb[i]))
            row_larger.append(list_nets_bp[j])

            inner_bb_to_true_p2b2_map.append(row_larger)


for k in range(len(list_nets_bp)):

    int_bp_comp_name = list_comp_bp[k][0]
    test_int_bp_comp_name = list(int_bp_comp_name)

    if (test_int_bp_comp_name[1] == "S"):
        test_int_bp_comp_name[1] = "P"

    updated_int_bp_comp_name = "".join(test_int_bp_comp_name)

    for m in range(len(list_nets_p2b2)):
        if (
            updated_int_bp_comp_name == list_comp_p2b2[m][0] and
            list_comp_bp[k][1] == list_comp_p2b2[m][1]
        ):

            for n in range(len(inner_bb_to_true_p2b2_map)):
                if (inner_bb_to_true_p2b2_map[n][2] == list_nets_bp[k]):

                    inner_bb_to_true_p2b2_map[n].append(list_comp_p2b2[m][0])
                    inner_bb_to_true_p2b2_map[n].append(list_nets_p2b2[m])


############################################################
# Find Inner BB to True Backplane to True P2B2 Connections #
############################################################


#################
# Output to csv #
#################

# Inner BB -> True Backplane (short?) ######################

write_to_csv(
    inner_bb_to_true_bp_mapping_filename,
    inner_bb_to_true_bp_map,
    ["Inner BB net", "Inner BB connector",
     "True Backplane net"],
)

# Inner BB -> True Backplane -> True P2B2 ##################

write_to_csv(
    inner_bb_to_true_p2b2_mapping_filename,
    inner_bb_to_true_p2b2_map,
    ["Inner BB net", "Inner BB connector",
     "True Backplane net", "True Backplane connector",
     "True P2B2 net"],
)
