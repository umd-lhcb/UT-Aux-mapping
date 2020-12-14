#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 05:51 AM +0100

import re

from pathlib import Path

from pyUTM.common import jp_depop_true
from pyUTM.io import PcadNaiveReader
from pyUTM.io import write_to_csv

from UT_Aux_mapping.const import input_dir, output_dir
from UT_Aux_mapping.const import jp_hybrid_name_inverse
from UT_Aux_mapping.helpers import ppp_netname_regulator, parse_net_jp
from UT_Aux_mapping.helpers import ppp_sort
from UT_Aux_mapping.helpers import gen_filename
from UT_Aux_mapping.tabular import write_to_latex_ppp

true_p2b2_netlist = input_dir / Path('true_p2b2.net')
ppp_netlist = input_dir / Path('ppp.net')

variants = ['Full', 'Partial', 'Depopulated']
colors = ['Red', 'Green', 'White']
jpus = ['JPU'+str(i) for i in range(1, 4)]

colors_dict = dict(zip(variants, colors))
output_csv = {var: output_dir / gen_filename(__file__, var) for var in variants}
output_tex = {var: output_dir / gen_filename(__file__, var, 'tex')
              for var in variants}


def jpu_cable_length(var, jpu,
                     base_length={
                         'Full': 130, 'Partial': 100, 'Depopulated': 70},
                     adj_length={'JPU3': -20, 'JPU2': -10, 'JPU1': 0}):
    return base_length[var]+adj_length[jpu]


cable_length = {var: {jpu+' - '+str(pin): jpu_cable_length(var, jpu)
                      for jpu in jpus for pin in range(1, 31)}
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
            jpu_pin = jpu[0] + ' - ' + jpu[1]

            parsed_net = parse_net_jp(net)
            depop = jp_depop_true[parsed_net.jp][
                jp_hybrid_name_inverse[parsed_net.hyb]]

            row.append(ppp_comp[0]+' - '+ppp_comp[1])
            row.append(jpu_pin)
            row.append(net)
            row.append(ppp_name_errata_inverse[net])
            row.append(depop)
            row.append(cable_length[var][jpu_pin])

            true_p2b2_to_ppp[var].append(row)

        except KeyError:
            print("Warning: net {} doesn't match any net in P2B2. This is like an error in PPP".format(net))

        except IndexError:
            print("Warning: net {} doesn't have a matching JPU".format(net))


#################
# Write to file #
#################

headers = ['PPP', 'P2B2', 'netname', 'netname (PPP)', 'Depop?', 'Length [cm]']


for var, data in true_p2b2_to_ppp.items():
    data.sort(key=lambda x: ppp_sort(x[1]))
    write_to_csv(output_csv[var], data, headers)
    write_to_latex_ppp(
        output_tex[var], 'C-TOP-MAG-TRUE-'+var.upper(),
        data,
        headers[0:3]+headers[5:]+['Cut', 'Labeled', 'Soldered'],
        colors_dict[var]
    )
