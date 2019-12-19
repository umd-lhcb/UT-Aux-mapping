#!/usr/bin/env python
#
# Author: Ben Flaggs
# License: BSD 2-clause
# Last Change: Wed Dec 18, 2019 at 11:10 PM -0500

from pathlib import Path

import sys
sys.path.insert(0, "./pyUTM")

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.io import write_to_csv
from pyUTM.sim import CurrentFlow

from UT_Aux_mapping.const import input_dir, output_dir
from UT_Aux_mapping.helpers import gen_filename
from UT_Aux_mapping.helpers import filter_comp
from UT_Aux_mapping.helpers import post_filter_any
from UT_Aux_mapping.helpers import make_comp_netname_dict

mirror_bp_netlist = input_dir / Path("mirror_backplane.net")
inner_bb_netlist = input_dir / Path("inner_bb.net")
inner_bb_to_mirror_bp_mapping_filename = output_dir / \
    Path(gen_filename(__file__))


#####################
# Read all netlists #
#####################

# Default net hopping should work for Custom BB.
NetHopper = CurrentFlow()

InnerBBReader = PcadReader(inner_bb_netlist)
inner_bb_descr = InnerBBReader.read(NetHopper)

MirrorBPReader = PcadNaiveReader(mirror_bp_netlist)
mirror_bp_descr = MirrorBPReader.read()

# MirrorBPHopper = CurrentFlow([PLACE COMPONENTS TO TREAT AS COPPER HERE])

# This CurrentFlow maps the nets accurately and outputs exactly what we want
# to the final .csv file in the "output" directory.
MirrorBPHopper = CurrentFlow([r"^RT\d"])

# This CurrentFlow maps the nets accurately but it lists out the incorrect final
# net name for the Mirror Backplane. This is because of the resistors (RXXX)
# being treated as copper. Treating these components as copper means that the
# signal will continue to be traced further in the board resulting in a CORRECT
# net name but this is NOT the FINAL net name that we want when tracing.
# MirrorBPHopper = CurrentFlow([r"^RT\d", r"^RBSP_\d", r"^R\d", r"^NT\d+"])

PcadReader.make_equivalent_nets_identical(
    mirror_bp_descr, MirrorBPHopper.do(mirror_bp_descr)
)


#############
# Filtering #
#############

inner_bb_result = filter_comp(
    inner_bb_descr, r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$"
)

mirror_bp_result = filter_comp(mirror_bp_descr,
                               r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$")

# Inner BB #####################################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later, for now we want to trace
# the GNDs to make sure they stay as GNDs)

filter_inner_bb_throw_out = post_filter_any(
    lambda x: x[1] not in ["9", "10", "16", "17", "18", "19", "20", "24", "25",
                           "26", "27", "28", "29", "30"]
)
inner_bb_result_list = list(filter(filter_inner_bb_throw_out,
                                   inner_bb_result))

# Mirror Backplane #############################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later, for now we want to trace
# the GNDs to make sure they stay as GNDs)

filter_bp_throw_gnd = post_filter_any(lambda x: x[1] not in ["29"])
mirror_bp_result_list = list(filter(filter_bp_throw_gnd, mirror_bp_result))


##################################################
# Find Inner BB to Mirror Backplane Connections #
##################################################

# Inner BB -> Mirror Backplane #################################################

inner_bb_ref = make_comp_netname_dict(inner_bb_descr)
mirror_bp_ref = make_comp_netname_dict(mirror_bp_descr)

compnames_inner_bb = inner_bb_ref.keys()
netnames_inner_bb = inner_bb_ref.values()
list_comp_inner_bb = list(compnames_inner_bb)
list_nets_inner_bb = list(netnames_inner_bb)


compnames_mirror_bp = mirror_bp_ref.keys()
netnames_mirror_bp = mirror_bp_ref.values()
list_comp_bp = list(compnames_mirror_bp)
list_nets_bp = list(netnames_mirror_bp)

inner_bb_to_mirror_bp_map = []

for i in range(len(list_nets_inner_bb)):
    row = []
    for j in range(len(list_nets_bp)):
        if (
            list_comp_inner_bb[i][0] == list_comp_bp[j][0] and
            list_comp_inner_bb[i][1] == list_comp_bp[j][1]
        ):
            row.append(list_nets_inner_bb[i])
            row.append("-".join(list_comp_inner_bb[i]))
            row.append(list_nets_bp[j])

            inner_bb_to_mirror_bp_map.append(row)


#################
# Output to csv #
#################

# Inner BB -> Mirror Backplane (short?) ########################################

write_to_csv(
    inner_bb_to_mirror_bp_mapping_filename,
    inner_bb_to_mirror_bp_map,
    ["Inner BB net", "Inner BB connector",
     "Mirror Backplane net"],
)
