#!/usr/bin/env python
#
# Author: Ben Flaggs
# License: BSD 2-clause
# Last Change: Mon Nov 25, 2019 at 01:29 AM -0500

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

mirror_bp_netlist = input_dir / Path("mirror_backplane.net")
inner_bb_netlist = input_dir / Path("inner_bb.net")
inner_bb_to_mirror_bp_mapping_filename = output_dir / Path("InnerBBMirrorBPMapping.csv")


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
# MirrorBPHopper = CurrentFlow([r"^R\d", r"^RT\d", r"^C\d"])
#MirrorBPHopper = CurrentFlow([r"^R\d", r"^RT\d"])
MirrorBPHopper = CurrentFlow([r"^RT\d", r"^RBSP_\d", r"^R\d", r"^NT\d+"])

PcadReader.make_equivalent_nets_identical(
    mirror_bp_descr, MirrorBPHopper.do(mirror_bp_descr)
)


#############
# Filtering #
#############

#mirror_custom_bb_result = filter_comp(
#    mirror_custom_bb_descr, r"^J_PT_\d+|^J_1V5_\d+|^J_2V5_\d+|^JT0$|^JT1$|^JT2$"
#)

inner_bb_result = filter_comp(
    inner_bb_descr, r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$"
)

#mirror_bp_result = filter_comp(mirror_bp_descr,
#                               r"^JP\d|^JD\d|^JT0$|^JT1$|^JT2$")
mirror_bp_result = filter_comp(mirror_bp_descr,
                               r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$")

# Inner BB #####################################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later as GND is the current
# problem)

filter_inner_bb_throw_out = post_filter_any(
    lambda x: x[1] not in ["9", "10", "16", "17", "18", "19", "20", "24", "25",
                           "26", "27", "28", "29", "30"]
)
inner_bb_result_list = list(filter(filter_inner_bb_throw_out,
                                   inner_bb_result))

# Mirror Backplane #############################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later as GND is the current
# problem)

filter_bp_throw_gnd = post_filter_any(lambda x: x[1] not in ["29"])
mirror_bp_result_list = list(filter(filter_bp_throw_gnd, mirror_bp_result))


##################################################
# Find Mirror BB to Mirror Backplane Connections #
##################################################

# Inner BB -> Mirror Backplane ################################################

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

# THE ABOVE WORKS ALTHOUGH IT SAYS THAT SOME NETS GO TO GROUND WHEN THEY
# SHOULDN'T As of now, I know that the "..._2V5_SENSE_..." lines all go to GND
# when they actually don't These all go to "GND" because they have ""ClassName"
# "NetTie"" listed underneath their net names


#################
# Output to csv #
#################

# Inner BB -> Mirror Backplane (short?) ######################

write_to_csv(
    inner_bb_to_mirror_bp_mapping_filename,
    inner_bb_to_mirror_bp_map,
    ["Inner BB net", "Inner BB connector",
     "Mirror Backplane net"],
)
