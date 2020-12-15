#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Tue Dec 15, 2020 at 09:08 PM +0100

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
        tail_opts = dedupl(tail_opts)
        output += '[' + ','.join(tail_opts) + ']'

    if required_opts:
        required_opts = dedupl(required_opts)
        output += '{' + ','.join(required_opts) + '}'

    return output + eol


def latex_begin(content, env='document', **kwargs):
    output = latex_env(env, 'begin', **kwargs)
    output += content + '\n'
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


def boldmath(symb):
    latex_dep['bm']
    return latex_env('$'+symb+'$', 'bm', eol='')


def strikethrough(text):
    latex_dep['ulem'] += ['normalem']
    return latex_env(text, 'sout', eol='')


# Special LaTeX environment ####################################################

def makecell(*args):
    return latex_env(r'\\\relax '.join(args), 'makecell')


def textblock(content, width, x, y):
    return latex_begin('({}, {})'.format(x, y)+'\n'+content,
                       'textblock*', required_opts=[width])


def longtable(data, headers, align,
              num_of_head=3, left_margin='0pt', penalty='1'):
    raw = tabl.tabulate(data, headers, colalign=align,
                        tablefmt='latex_booktabs_raw').split('\n')
    latex_dep['longtable']

    begin = raw.pop(0)
    end = raw.pop(-1)
    begin = begin.replace('tabular', 'longtable')
    end = end.replace('tabular', 'longtable')

    for shift, cmd in zip(range(3), [r'\endhead', r'\bottomrule', r'\endfoot']):
        raw.insert(num_of_head+shift, cmd)

    return '\n'.join(
        ['{' + r'\makeatletter', r'\mathchardef\LT@end@pen='+penalty,
         r'\makeatother', r'\setlength{\LTleft}{'+left_margin+'}', begin] + raw +
        [end, '}']) + '\n'


# Special output ###############################################################

def tabular_ppp(data, headers, color,
                tabular_env='longtable',
                group_by=lambda x: x[0].split(' - ')[0],
                count_by=lambda x: x[6],
                col_to_keep=[0, 1, 2, 6],
                col_formatters=[lambda x: monospace(x.split(' - ')[1])] +
                [monospace]*2+[lambda x: x],
                align=['left']*3+['right']+['center']*5):
    reformatted = defaultdict(list)
    counter = defaultdict(lambda: 0)

    for row in data:
        key = group_by(row)
        reformatted_row = [
            f(x) for f, x in zip(
                col_formatters, [row[idx] for idx in col_to_keep])]

        extra_boxes = len(headers) - len(col_to_keep)
        reformatted_row += [r'$\square$'] * extra_boxes

        reformatted[key].append(reformatted_row)
        counter[count_by(row)] += 1

    output = ''
    for key, data in reformatted.items():
        data = reformatted[key]
        output += latex_env(bold(monospace(key)), 'subsection*')
        output += longtable(data, headers, align)

    # counter_data = []
    # for length, number in counter.items():
        # counter_data.append([length, number/2, number/2])
    # right_output = tabl.tabulate(
        # counter_data, headers=['Length', 'Black', color],
        # tablefmt='latex_booktabs_raw')
    # right_output += '\n'

    # return left_output, right_output, counter
    return output, '1', counter


# Output #######################################################################

def write_to_latex_ppp(output_file, title, data, headers, color,
                       msg='Double check wire lengths before proceed!'):
    content = latex_env('empty', 'pagestyle')
    content += bold(title) + '\n'
    content += latex_env('1em', 'vspace')
    content += r'\noindent'
    content += '\n'

    left_output = right_output = r'\small' + '\n'
    left_table, right_table, _ = tabular_ppp(data,  headers, color)
    left_output += left_table
    right_output += latex_begin(right_table, 'center')
    right_output += '\n' + r'\vspace{1em}' + msg

    content += left_output

    output = latex_preamble()
    output += latex_begin(content)

    with open(output_file, 'w') as f:
        f.write(output)
