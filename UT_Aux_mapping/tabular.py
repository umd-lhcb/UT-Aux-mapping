#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 04:38 PM +0100

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


# Special LaTeX environment ####################################################

def tcolorbox(left, right,
              left_width=0.7, right_width=0.3, width=r'\textwidth'):
    left_width = str(left_width)
    right_width = str(right_width)

    latex_dep['tcolorbox'] += ['skins', 'breakable']
    overlay = latex_env(
        right, 'overlay unbroken and first=',
        opts=[r'\node[inner sep=0pt,outer sep=0pt,text width=' +
              str(right_width)+width+',' +
              r'align=none,below left]' +
              'at ([xshift='+right_width+width+']' +
              'frame.north west)'])
    return latex_begin(
        left,  env='tcolorbox',
        opts=['blanker', 'width='+left_width+width,
              'enlarge right by='+right_width+width, 'breakable', overlay])


# Special output ###############################################################

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
    content += r'\noindent'
    content += '\n'

    left_output = r'\small' + '\n'
    left_table, right_table, _ = tabular_ppp(data,  headers, color)
    left_output += left_table
    right_output = right_table

    content += tcolorbox(left_output, right_output)

    output = latex_preamble()
    output += latex_begin(content)

    with open(output_file, 'w') as f:
        f.write(output)
