#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 02:26 AM +0100

import re

from pathlib import Path

from pyUTM.common import jp_depop_true
from pyUTM.io import PcadNaiveReader
from pyUTM.io import write_to_csv

from UT_Aux_mapping.const import input_dir, output_dir
from UT_Aux_mapping.const import jp_hybrid_name_inverse
from UT_Aux_mapping.helpers import ppp_netname_regulator, parse_net_jp
from UT_Aux_mapping.helpers import gen_filename

true_p2b2_netlist = input_dir / Path('true_p2b2.net')
ppp_netlist = input_dir / Path('ppp.net')

variants = ['Full', 'Partial', 'Depopulated']

output_csv = {var: output_dir / gen_filename(__file__, var) for var in variants}
output_tex = {var: output_dir / gen_filename(__file__, var, 'tex')
              for var in variants}


#####################
# Read all netlists #
#####################

TrueP2B2Reader = PcadNaiveReader(true_p2b2_netlist)
true_p2b2_descr = TrueP2B2Reader.read()

PPPReader = PcadNaiveReader(ppp_netlist)
ppp_descr = PPPReader.read()


############################################################
# Fix PPP netname irregularities and only keep JPU entries #
############################################################

# This stores name before and after the fix
ppp_name_errata = {k: ppp_netname_regulator(k) for k in ppp_descr.keys()}
ppp_name_errata_inverse = dict(map(reversed, ppp_name_errata.items()))
ppp_descr = {ppp_name_errata[k]: v for k, v in ppp_descr.items()}

# For this part, only the JPU connectors are relevant
ppp_descr = {k: v for k, v in ppp_descr.items() if 'JPU' in k}


################
# Find matches #
################

true_p2b2_to_ppp = {var: [] for var in variants}

for net, ppp_comp_list in ppp_descr.items():
    for idx, var in enumerate(variants):
        try:
            row = []

            p2b2_comp = true_p2b2_descr[net]
            ppp_comp = ppp_comp_list[idx]

            jpu = [comp for comp in p2b2_comp
                   if bool(re.search(r'^JPU\d', comp[0]))][0]

            parsed_net = parse_net_jp(net)
            depop = jp_depop_true[parsed_net.jp][
                jp_hybrid_name_inverse[parsed_net.hyb]]

            row.append(ppp_comp[0]+' - '+ppp_comp[1])
            row.append(jpu[0]+' - '+jpu[1])
            row.append(net)
            row.append(ppp_name_errata_inverse[net])
            row.append(str(depop))

            true_p2b2_to_ppp[var].append(row)

        except KeyError:
            print("Warning: net {} doesn't match any net in P2B2. This is like an error in PPP".format(net))

        except IndexError:
            print("Warning: net {} doesn't have a matching JPU".format(net))


#################
# Write to file #
#################

for var, data in true_p2b2_to_ppp.items():
    write_to_csv(output_csv[var], data,
                 ['PPP', 'P2B2', 'netname', 'netname (PPP)', 'Depop?'])