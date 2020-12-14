#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 05:09 AM +0100

import tabulate as tabl

from functools import partial
from collections import defaultdict

latex_dep = defaultdict(list)
latex_dep['booktabs']
latex_dep['geometry'] = ['a4paper',
                         'left=1cm', 'right=2cm', 'top=1cm', 'bottom=1cm']
latex_dep['amssymb']


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


def latex_env(content, env, opts=None, required_opts=None, eol='\n'):
    if opts:
        output = '\\' + env + '[' + ','.join(opts) + ']' + \
            '{' + content + '}'
    else:
        output = '\\' + env + '{' + content + '}'

    if required_opts:
        output += '{' + ','.join(required_opts) + '}'

    return output + eol


def latex_begin(content, env='document', opts=None, required_opts=None):
    output = latex_env(env, 'begin', opts, required_opts)
    output += content
    output += latex_env(env, 'end')
    return output


def latex_packages(packages=latex_dep):
    output = ''

    for pkg, opts in packages.items():
        output += latex_env(pkg, 'usepackage', opts)

    return output


def latex_preamble(template='article', fontsize='10pt'):
    output = latex_env(template, 'documentclass', [fontsize])
    output += latex_packages()

    return output


# Text styles ##################################################################

def monospace(text):
    return latex_env(text, 'texttt', eol='')


def bold(text):
    return latex_env(text, 'textbf', eol='')


def strikethrough(text):
    latex_dep['ulem'] += ['normalem']
    return latex_env(text, 'st', eol='')


def tabular_ppp(data, headers):
    reformatted = defaultdict(list)
    # 'PPP', 'P2B2', 'netname', 'netname (PPP)', 'Depop?', 'Length (appx)'

    for row in data:
        jpu, _ = row[1].split(' - ')
        reformatted_row = [monospace(c) for c in row[0:2]]

        if row[4]:
            netname_formatter = lambda x: strikethrough(monospace(x))
        else:
            netname_formatter = lambda x: monospace(x)

        reformatted_row += [netname_formatter(c) for c in row[2:3]]
        reformatted_row.append(row[5])
        reformatted_row += [r'$\square$'] * 3

        reformatted[jpu].append(reformatted_row)

    output = ''
    for jpu, data in reformatted.items():
        output += latex_env(monospace(jpu), 'subsection*')
        output += tabl.tabulate(
            data, headers=headers, tablefmt='latex_booktabs_raw')
        output += '\n'

    return output


# Output #######################################################################

def write_to_latex_ppp(output_file, title, data, headers):
    output = latex_preamble()
    content = latex_env('empty', 'pagestyle')
    content += bold(title) + '\n'
    content += latex_env('1em', 'vspace')
    content += '\n'
    content += r'\noindent'

    left_table = r'\small' + '\n'
    left_table += tabular_ppp(data, headers)
    content += latex_begin(left_table, 'minipage',
                           required_opts=[r'0.7\textwidth'])

    output += latex_begin(content)

    with open(output_file, 'w') as f:
        f.write(output)
