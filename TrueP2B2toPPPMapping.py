#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Fri Jan 29, 2021 at 02:48 PM +0100

import re

from pathlib import Path

from pyUTM.common import jp_depop_true as jp_depop
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
    boldmath, makecell
)


######################################
# Define parameters for output files #
######################################

p2b2_netlist_spec = {
    'C-TOP-MAG-TRUE': PcadNaiveReader(input_dir / Path('true_p2b2.net')).read()
}
p2b2_netlist_spec['C-BOT-IP-TRUE'] = p2b2_netlist_spec['C-TOP-MAG-TRUE']

ppp_netlist_spec = {
    'C-TOP-MAG-TRUE': WirelistNaiveReader(
        input_dir / Path('true_ppp_mag.wirelist')).read(),
    'C-BOT-IP-TRUE': WirelistNaiveReader(
        input_dir / Path('true_ppp_ip.wirelist')).read(),
}

output_spec = {
    'C-TOP-MAG-TRUE': {
        'Alpha': {
            'title': boldmath(r'\alpha'),
            'color': 'Red',
            'cable_length': 150,
            'cable_length_adj': {'JPU1': -20, 'JPU2': -10, 'JPU3': 0},
            'index': 0
        },
        'Beta':  {
            'title': boldmath(r'\beta'),
            'color': 'Green',
            'cable_length': 120,
            'cable_length_adj': {'JPU1': -20, 'JPU2': -10, 'JPU3': 0},
            'index': 1
        },
        'Gamma': {
            'title': boldmath(r'\gamma'),
            'color': 'White',
            'cable_length': 90,
            'cable_length_adj': {'JPU1': -20, 'JPU2': -10, 'JPU3': 0},
            'index': 2
        }
    },
    'C-BOT-IP-TRUE': {
        'Alpha': {
            'title': boldmath(r'\alpha'),
            'color': 'Red',
            'cable_length': 150,
            'cable_length_adj': {'JPU1': -20, 'JPU2': -10, 'JPU3': 0},
            'index': 0
        },
        'Beta':  {
            'title': boldmath(r'\beta'),
            'color': 'Green',
            'cable_length': 120,
            'cable_length_adj': {'JPU1': -20, 'JPU2': -10, 'JPU3': 0},
            'index': 1
        },
        'Gamma': {
            'title': boldmath(r'\gamma'),
            'color': 'White',
            'cable_length': 90,
            'cable_length_adj': {'JPU1': -20, 'JPU2': -10, 'JPU3': 0},
            'index': 2
        }
    }
}


############################################################
# Fix PPP netname irregularities and only keep JPU entries #
############################################################

def regularize_ppp_descr(raw_ppp_descr):
    # This stores name before and after the fix
    ppp_name_errata = {k: ppp_netname_regulator(k)
                       for k in raw_ppp_descr.keys()}
    ppp_descr = {ppp_name_errata[k]: v for k, v in raw_ppp_descr.items()}

    return {k: v for k, v in ppp_descr.items() if 'JPU' in k}, \
        dict(map(reversed, ppp_name_errata.items()))  # <-- inverse of ppp_name_errata


####################################################
# Make PPP -> P2B2 connections and generate output #
####################################################

headers_csv = []
headers_tex = []


def jpu_cable_length(jpu, base_length, adj_length):
    return base_length+adj_length[jpu[0]]


for loc_in_detector, attrs in output_spec.items():
    print('====')
    print('Working on: {}'.format(loc_in_detector))
    print('====')
    for geo_loc, var_attrs in attrs.items():
        print('----')
        print('working on BP: {}'.format(geo_loc))
        print('----')
        var_attrs['data'] = []
        var_attrs['filename'] = '-'.join(['P2B2toPPP', loc_in_detector, geo_loc])
        var_attrs['title'] = '-'.join([loc_in_detector, var_attrs['title']])

        p2b2_descr = p2b2_netlist_spec[loc_in_detector]
        ppp_descr, ppp_name_errata_inverse = regularize_ppp_descr(
            ppp_netlist_spec[loc_in_detector])

        for net, ppp_comp_list in ppp_descr.items():
            try:
                p2b2_comp = p2b2_descr[net]
            except KeyError:
                print("Warning: net {} doesn't match any net in P2B2. This is like an error in PPP".format(net))
                continue

            try:
                ppp_comp = ppp_comp_list[var_attrs['index']]
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
                headers_tex.append('Pin')

            ppp_pin = ' - '.join(ppp_comp)
            row.append(ppp_pin)
            if first_run:
                headers_csv.append('PPP label')
                headers_tex.append(makecell('PPP', '(label)'))

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
            depop = jp_depop[parsed_net.jp][
                jp_hybrid_name_inverse[parsed_net.hyb]]
            row.append(depop)
            if first_run:
                headers_csv.append('Depop?')

            row.append(jpu_cable_length(jpu, var_attrs['cable_length'],
                                        var_attrs['cable_length_adj']))
            if first_run:
                headers_csv.append('Length [cm]')
                headers_tex.append(makecell('Length', '[cm]'))

            var_attrs['data'].append(row)


#################
# Write to file #
#################

headers_tex += ['Cut', makecell('Crimp', 'P2B2'), 'Label',
                makecell('Crimp', 'PPP'), 'Check']

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
