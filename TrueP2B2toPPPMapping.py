#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Tue Dec 15, 2020 at 04:58 PM +0100

import re

from pathlib import Path

from pyUTM.common import jp_depop_true
from pyUTM.io import (
    PcadNaiveReader, WirelistNaiveReader,
    write_to_csv
)

from UT_Aux_mapping.const import (
    input_dir, output_dir,
    jp_hybrid_name_inverse
)
from UT_Aux_mapping.helpers import (
    parse_net_jp,
    ppp_sort, ppp_label, ppp_netname_regulator
)
from UT_Aux_mapping.tabular import (
    write_to_latex_ppp,
    boldmath
)

true_p2b2_netlist = input_dir / Path('true_p2b2.net')
true_ppp_netlist = input_dir / Path('true_ppp.wirelist')

output_spec = {
    'C-TOP-MAG-TRUE': {
        'Alpha': {
            'title': boldmath(r'\alpha'),
            'variant': 'Full',
            'color': 'Red',
            'cable_length': 160
        },
        'Beta':  {
            'title': boldmath(r'\beta'),
            'variant': 'Partial',
            'color': 'Green',
            'cable_length': 130
        },
        'Gamma': {
            'title': boldmath(r'\gamma'),
            'variant': 'Partial',
            'color': 'White',
            'cable_length': 100
        }
    }
}
cable_length_adj = {'JPU1': -20, 'JPU2': -10, 'JPU3': 0}


#####################
# Read all netlists #
#####################

TrueP2B2Reader = PcadNaiveReader(true_p2b2_netlist)
true_p2b2_descr = TrueP2B2Reader.read()

TruePPPReader = WirelistNaiveReader(true_ppp_netlist)
true_ppp_descr = TruePPPReader.read()


############################################################
# Fix PPP netname irregularities and only keep JPU entries #
############################################################

# This stores name before and after the fix
ppp_name_errata = {k: ppp_netname_regulator(k) for k in true_ppp_descr.keys()}
ppp_name_errata_inverse = dict(map(reversed, ppp_name_errata.items()))
ppp_descr = {ppp_name_errata[k]: v for k, v in true_ppp_descr.items()}

# For this part, only the JPU connectors are relevant
ppp_descr = {k: v for k, v in ppp_descr.items() if 'JPU' in k}


####################################################
# Make PPP -> P2B2 connections and generate output #
####################################################

variants = ['Full', 'Partial', 'Depopulated']
comp_idx = dict(zip(variants, range(0, 3)))
headers_csv = []
headers_tex = []


def jpu_cable_length(jpu, base_length, adj_length=cable_length_adj):
    return base_length+adj_length[jpu[0]]


for title_pre, attrs in output_spec.items():
    for geo_loc, var_attrs in attrs.items():
        var_attrs['data'] = []
        var_attrs['filename'] = '-'.join(['P2B2toPPP', title_pre, geo_loc])
        var_attrs['title'] = '-'.join([title_pre, var_attrs['title']])

        var = var_attrs['variant']

        for net, ppp_comp_list in ppp_descr.items():
            try:
                p2b2_comp = true_p2b2_descr[net]
            except KeyError:
                print("Warning: net {} doesn't match any net in P2B2. This is like an error in PPP".format(net))
                continue

            try:
                ppp_comp = ppp_comp_list[comp_idx[var]]
            except IndexError:
                # Doesn't exist due to depopulation! Nothing to see here.
                continue

            try:
                jpu = [comp for comp in p2b2_comp
                       if bool(re.search(r'^JPU\d', comp[0]))][0]
            except IndexError:
                print("Warning: net {} doesn't have a matching JPU".format(net))
                continue

            row = []
            first_run = True if (not headers_csv and not headers_tex) else False

            jpu_pin = ' - '.join(jpu)
            row.append(jpu_pin)
            if first_run:
                headers_csv.append('JPU')
                headers_tex.append('JPU')

            ppp_pin = ' - '.join(ppp_comp)
            row.append(ppp_pin)
            if first_run:
                headers_csv.append('PPP label')
                headers_tex.append('PPP label')

            row.append(ppp_label(net))
            if first_run:
                headers_csv.append('Note')
                headers_tex.append('Note')

            row.append(net)
            if first_run:
                headers_csv.append('Netname (P2B2)')

            row.append(ppp_name_errata_inverse[net])
            if first_run:
                headers_csv.append('Netname (PPP)')

            parsed_net = parse_net_jp(net)
            depop = jp_depop_true[parsed_net.jp][
                jp_hybrid_name_inverse[parsed_net.hyb]]
            row.append(depop)
            if first_run:
                headers_csv.append('Depop?')

            row.append(jpu_cable_length(jpu, var_attrs['cable_length']))
            if first_run:
                headers_csv.append('Length [cm]')
                headers_tex.append('Length [cm]')

            var_attrs['data'].append(row)


#################
# Write to file #
#################

headers_tex += ['Cut', 'Labeled', 'Crimped']

for _, attrs in output_spec.items():
    for _, var_attrs in attrs.items():
        data = sorted(var_attrs['data'], key=lambda x: ppp_sort(x[0]))
        filename = var_attrs['filename']
        title = var_attrs['title']
        color = var_attrs['color']

        write_to_csv(
            output_dir / Path(filename+'.csv'),
            data, headers_csv)
        write_to_latex_ppp(
            output_dir / Path(filename+'.tex'),
            title, data, headers_tex, color)
