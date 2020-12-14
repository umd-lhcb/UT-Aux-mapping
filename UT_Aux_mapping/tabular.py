#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 04:20 PM +0100

import tabulate as tabl

from functools import partial
from collections import defaultdict

latex_dep = defaultdict(list)
latex_dep['booktabs']
latex_dep['geometry'] = ['a4paper',
                         'left=1cm', 'right=1cm', 'top=1cm', 'bottom=1cm']
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


def latex_env(content, env,
              opts=None, tail_opts=None, required_opts=None, eol='\n'):
    dedupl = lambda x: list(set(x))

    if opts:
        opts = dedupl(opts)
        output = '\\' + env + '[' + ','.join(opts) + ']' + \
            '{' + content + '}'
    else:
        output = '\\' + env + '{' + content + '}'

    if tail_opts:
        tail_opts = dedupl(opts)
        output += '[' + ','.join(tail_opts) + ']'

    if required_opts:
        required_opts = dedupl(required_opts)
        output += '{' + ','.join(required_opts) + '}'

    return output + eol


def latex_begin(content, env='document', **kwargs):
    output = latex_env(env, 'begin', **kwargs)
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
    return latex_env(text, 'sout', eol='')


def tabular_ppp(data, headers, color):
    reformatted = defaultdict(list)
    # 'PPP', 'P2B2', 'netname', 'netname (PPP)', 'Depop?', 'Length (appx)'
    counter = defaultdict(lambda: 0)

    for row in data:
        jpu, _ = row[1].split(' - ')
        reformatted_row = [monospace(c) for c in row[0:2]]

        if row[4]:
            netname_formatter = lambda x: strikethrough(monospace(x))
        else:
            netname_formatter = lambda x: monospace(x)

        reformatted_row += [netname_formatter(c) for c in row[2:3]]
        reformatted_row.append(row[5])
        counter[row[5]] += 1
        reformatted_row += [r'$\square$'] * 3

        reformatted[jpu].append(reformatted_row)

    left_output = ''
    for jpu, data in reformatted.items():
        left_output += latex_env(monospace(jpu), 'subsection*')
        left_output += tabl.tabulate(
            data, headers=headers, tablefmt='latex_booktabs_raw')
        left_output += '\n'

    counter_data = []
    for length, number in counter.items():
        counter_data.append([length, number/2, number/2])
    right_output = tabl.tabulate(
        counter_data, headers=['Length', 'Black', color],
        tablefmt='latex_booktabs_raw')
    right_output += '\n'

    return left_output, right_output, counter


# Output #######################################################################

def write_to_latex_ppp(output_file, title, data, headers, color):
    content = latex_env('empty', 'pagestyle')
    content += bold(title) + '\n'
    content += latex_env('1em', 'vspace')
    content += '\n'
    content += r'\noindent'

    left_table = r'\small' + '\n'
    left_output, right_output, _ = tabular_ppp(data,  headers, color)
    left_table += left_output

    content += latex_begin(left_table, 'minipage',
                           required_opts=[r'0.75\textwidth'])
    content += latex_env('1em', 'hspace')
    content += latex_begin(right_output, 'minipage',
                           required_opts=[r'0.2\textwidth'])

    output = latex_preamble()
    output += latex_begin(content)

    with open(output_file, 'w') as f:
        f.write(output)
