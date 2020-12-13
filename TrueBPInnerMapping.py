#!/usr/bin/env python
#
# Author: Ben Flaggs
# License: BSD 2-clause
# Last Change: Sun Dec 13, 2020 at 11:31 PM +0100

from pathlib import Path

from pyUTM.io import PcadNaiveReader
from pyUTM.io import write_to_csv

from UT_Aux_mapping.const import input_dir, output_dir
from UT_Aux_mapping.helpers import gen_filename
from UT_Aux_mapping.helpers import filter_comp
from UT_Aux_mapping.helpers import post_filter_any
from UT_Aux_mapping.helpers import make_comp_netname_dict

true_bp_netlist = input_dir / Path("true_backplane.net")
inner_bb_netlist = input_dir / Path("inner_bb.net")
inner_bb_to_true_bp_mapping_filename = output_dir / Path(gen_filename(__file__))


#####################
# Read all netlists #
#####################

InnerBBReader = PcadNaiveReader(inner_bb_netlist)
inner_bb_descr = InnerBBReader.read()

TrueBPReader = PcadNaiveReader(true_bp_netlist)
true_bp_descr = TrueBPReader.read()


#############
# Filtering #
#############

inner_bb_result = filter_comp(
    inner_bb_descr, r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$"
)

true_bp_result = filter_comp(true_bp_descr,
                             r"^JP\d+|^JD\d+|^JPL0$|^JPL1$|^JPL2$")

# Inner BB #####################################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later, for now we want to trace
# the GNDs to make sure they stay as GNDs)

filter_inner_bb_throw_out = post_filter_any(
    lambda x: x[1] not in ["9", "10", "16", "17", "18", "19", "20", "24", "25",
                           "26", "27", "28", "29", "30"]
)
inner_bb_result_list = list(filter(filter_inner_bb_throw_out, inner_bb_result))

# True Backplane ###############################################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later, for now we want to trace
# the GNDs to make sure they stay as GNDs)

filter_bp_throw_gnd = post_filter_any(lambda x: x[1] not in ["29"])
true_bp_result_list = list(filter(filter_bp_throw_gnd, true_bp_result))


###############################################
# Find Inner BB to True Backplane Connections #
###############################################

# Inner BB -> True Backplane ###################################################

inner_bb_ref = make_comp_netname_dict(inner_bb_descr)
true_bp_ref = make_comp_netname_dict(true_bp_descr)

list_comp_inner_bb = list(inner_bb_ref.keys())
list_nets_inner_bb = list(map(lambda x: x.replace(' ', ''),
                              inner_bb_ref.values()))

list_comp_bp = list(true_bp_ref.keys())
list_nets_bp = list(true_bp_ref.values())

inner_bb_to_true_bp_map = []

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

            inner_bb_to_true_bp_map.append(row)


#################
# Output to csv #
#################

# Inner BB -> True Backplane (short?) ##########################################

write_to_csv(
    inner_bb_to_true_bp_mapping_filename,
    inner_bb_to_true_bp_map,
    ["Inner BB net", "Inner BB connector",
     "True Backplane net"],
)
