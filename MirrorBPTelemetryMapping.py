#!/usr/bin/env python
#
# Author: Ben Flaggs
# License: BSD 2-clause
# Last Change: Wed Dec 18, 2019 at 11:05 PM -0500

from pathlib import Path

import sys
sys.path.insert(0, "./pyUTM")

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.io import write_to_csv
from pyUTM.sim import CurrentFlow

from UT_Aux_mapping.const import input_dir, output_dir
from UT_Aux_mapping.helpers import filter_comp
from UT_Aux_mapping.helpers import post_filter_any
from UT_Aux_mapping.helpers import make_comp_netname_dict
from UT_Aux_mapping.helpers import gen_filename

mirror_bp_netlist = input_dir / Path("mirror_backplane.net")
mirror_custom_bb_netlist = input_dir / Path("mirror_custom_telemetry_bb.net")
mirror_bb_to_bp_mapping_filename = output_dir / Path(gen_filename(__file__))


#####################
# Read all netlists #
#####################

# Default net hopping should work for Custom BB.
NetHopper = CurrentFlow()

MirrorCustomBBReader = PcadReader(mirror_custom_bb_netlist)
mirror_custom_bb_descr = MirrorCustomBBReader.read(NetHopper)

MirrorBPReader = PcadNaiveReader(mirror_bp_netlist)
mirror_bp_descr = MirrorBPReader.read()

# MirrorBPHopper = CurrentFlow([PLACE COMPONENTS TO TREAT AS COPPER HERE])
MirrorBPHopper = CurrentFlow([r"^R\d", r"^RT\d", r"^C\d"])

PcadReader.make_equivalent_nets_identical(
    mirror_bp_descr, MirrorBPHopper.do(mirror_bp_descr)
)


#############
# Filtering #
#############

mirror_custom_bb_result = filter_comp(
    mirror_custom_bb_descr, r"^J_PT_\d+|^J_1V5_\d+|^J_2V5_\d+|^JT0$|^JT1$|^JT2$"
)

mirror_bp_result = filter_comp(mirror_bp_descr,
                               r"^JP\d|^JD\d|^JT0$|^JT1$|^JT2$")

# Mirror Custom BB #############################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later as GND is the current
# problem)

filter_bb_throw_out = post_filter_any(lambda x: x[1] not in ["S1", "S2", "29"])
mirror_custom_bb_result_list = list(filter(filter_bb_throw_out,
                                           mirror_custom_bb_result))

# Mirror Backplane #############################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later as GND is the current
# problem)

filter_bp_throw_gnd = post_filter_any(lambda x: x[1] not in ["29"])
mirror_bp_result_list = list(filter(filter_bp_throw_gnd, mirror_bp_result))


##################################################
# Find Mirror BB to Mirror Backplane Connections #
##################################################

# Mirror Custom Telemetry BB -> Mirror Backplane ###############################

mirror_bb_ref = make_comp_netname_dict(mirror_custom_bb_descr)
mirror_bp_ref = make_comp_netname_dict(mirror_bp_descr)

compnames_mirror_bb = mirror_bb_ref.keys()
netnames_mirror_bb = mirror_bb_ref.values()
list_comp_bb = list(compnames_mirror_bb)
list_nets_bb = list(netnames_mirror_bb)

compnames_mirror_bp = mirror_bp_ref.keys()
netnames_mirror_bp = mirror_bp_ref.values()
list_comp_bp = list(compnames_mirror_bp)
list_nets_bp = list(netnames_mirror_bp)

mirror_bb_to_mirror_bp_map = []

for i in range(len(list_nets_bb)):
    row = []
    for j in range(len(list_nets_bp)):
        if (
            list_comp_bb[i][0] == list_comp_bp[j][0] and
            list_comp_bb[i][1] == list_comp_bp[j][1]
        ):

            row.append(list_nets_bb[i])
            row.append("-".join(list_comp_bb[i]))
            row.append(list_nets_bp[j])

            mirror_bb_to_mirror_bp_map.append(row)

# THE ABOVE WORKS ALTHOUGH IT SAYS THAT SOME NETS GO TO GROUND WHEN THEY
# SHOULDN'T As of now, I know that the "..._2V5_SENSE_..." lines all go to GND
# when they actually don't These all go to "GND" because they have ""ClassName"
# "NetTie"" listed underneath their net names


#################
# Output to csv #
#################

# Mirror Custom Telemetry BB -> Mirror Backplane (short?) ######################

write_to_csv(
    mirror_bb_to_bp_mapping_filename,
    mirror_bb_to_mirror_bp_map,
    ["Mirror Telemetry BB net", "Telemetry BB connector",
     "Mirror Backplane net"],
)
