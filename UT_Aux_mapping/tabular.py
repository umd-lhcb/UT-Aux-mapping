#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 03:57 AM +0100

import tabulate as tabl

from functools import partial
from collections import defaultdict

latex_dep = defaultdict(list)
latex_dep['booktabs']
latex_dep['geometry'] = ['a4paper',
                         'left=1cm', 'right=2cm', 'top=1cm', 'bottom=1cm']


# LaTeX general ################################################################

# Don't escape '\'
tabl._table_formats["latex_booktabs_raw"] = tabl.TableFormat(
    lineabove=partial(tabl._latex_line_begin_tabular, booktabs=True),
    linebelowheader=tabl.Line("\\midrule", "", "", ""),
    linebetweenrows=None,
    linebelow=tabl.Line("\\bottomrule\n\\end{tabular}", "", "", ""),
    headerrow=partial(tabl._latex_row, escrules={r"_": r"\_"}),
    datarow=partial(tabl._latex_row, escrules={r"_": r"\_"}),
    padding=1,
    with_header_hide=None,
)


def latex_packages(packages=latex_dep):
    output = ''

    for pkg, opts in packages.items():
        if opts:
            output += r'\usepackage' + '[' + ','.join(opts) + ']' + \
                '{' + pkg + '}' + '\n'
        else:
            output += r'\usepackage' + '{' + pkg + '}' + '\n'

    return output


def latex_preamble(template='article'):
    output = r'\documentclass{' + template + '}\n'
    output += latex_packages()

    return output


def latex_begin(content, env='document'):
    output = r'\begin{' + env + '}\n'
    output += content
    output += r'\end{' + env + '}\n'
    return output


# Text styles ##################################################################

def monospace(text):
    return r'\texttt{' + (text) + r'}'


def strikethrough(text):
    latex_dep['ulem'] += ['normalem']
    return r'\st{' + text + r'}'


def tabular_ppp(data, headers):
    reformatted = []
    # 'PPP', 'P2B2', 'netname', 'netname (PPP)', 'Depop?', 'Length (appx)'

    for row in data:
        reformatted_row = [monospace(c) for c in row[0:2]]

        if row[4]:
            netname_formatter = lambda x: strikethrough(monospace(x))
        else:
            netname_formatter = lambda x: monospace(x)

        reformatted_row += [netname_formatter(c) for c in row[2:4]]
        reformatted_row.append(row[5])

        reformatted.append(reformatted_row)

    return tabl.tabulate(
        reformatted, headers=headers, tablefmt='latex_booktabs_raw')


# Output #######################################################################

def write_to_latex_ppp(output_file, data, headers):
    output = latex_preamble()
    content = tabular_ppp(data, headers)
    output += latex_begin(content)

    with open(output_file, 'w') as f:
        f.write(output)
