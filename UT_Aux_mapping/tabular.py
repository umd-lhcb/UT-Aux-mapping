#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Tue Dec 15, 2020 at 11:16 PM +0100

import tabulate as tabl

from functools import partial
from collections import defaultdict

latex_dep = defaultdict(list)
latex_dep['booktabs']
latex_dep['geometry'] = ['a4paper',
                         'left=1cm', 'right=1cm', 'top=1cm', 'bottom=1cm',
                         'includehead', 'includefoot', 'headsep=0.3cm']
latex_dep['amssymb']
latex_dep['fancyhdr']


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
    latex_dep['makecell']
    return latex_env(r'\\\relax '.join(args), 'makecell')


def textblock(content, width, x, y,
              origin=r'\textblockorigin{\paperwidth}{0pt}'):
    latex_dep['textpos'] += ['absolute']
    output = origin + '\n'
    output += latex_begin('({}, {})'.format(x, y)+'\n'+content,
                          'textblock*', required_opts=[width])
    return output


def longtable(data, headers, align,
              left_margin='0pt', penalty='1'):
    raw = tabl.tabulate(data, headers, colalign=align,
                        tablefmt='latex_booktabs_raw').split('\n')
    latex_dep['longtable']

    begin = raw.pop(0)
    end = raw.pop(-1)
    begin = begin.replace('tabular', 'longtable')
    end = end.replace('tabular', 'longtable')

    head_idx = raw.index(r'\midrule') + 1
    for shift, cmd in zip(range(3), [r'\endhead', r'\bottomrule', r'\endfoot']):
        raw.insert(head_idx+shift, cmd)

    return '\n'.join(
        ['{' + r'\makeatletter', r'\mathchardef\LT@end@pen='+penalty,
         r'\makeatother', r'\setlength{\LTleft}{'+left_margin+'}', begin] +
        raw + [end, '}']) + '\n'


def fancystyle(title, rule_width='0pt'):
    return '\n'.join([
        r'\fancypagestyle{worksheet}{',
        r'\fancyhf{}',
        r'\renewcommand{\headrulewidth}{' + rule_width + '}',
        r'\fancyhead[L]{\hspace{1em}\textbf{' + title + '}' + '}',
        '}',
        r'\pagestyle{worksheet}'
    ])


# Special output ###############################################################

def tabular_ppp(data, headers, color,
                tabular_env='longtable',
                group_by=lambda x: x[0].split(' - ')[0],
                count_by=lambda x: x[6],
                col_to_keep=[0, 1, 2, 6],
                col_formatters=[lambda x: monospace(x.split(' - ')[1])] +
                [monospace]*2+[lambda x: x],
                align=['left']*3+['right']+['center']*5,
                msg='Double check wire lengths before proceed!'):
    reformatted = defaultdict(list)
    counter = defaultdict(lambda: 0)
    output = ''

    for row in data:
        key = group_by(row)
        reformatted_row = [
            f(x) for f, x in zip(
                col_formatters, [row[idx] for idx in col_to_keep])]

        extra_boxes = len(headers) - len(col_to_keep)
        reformatted_row += [r'$\square$'] * extra_boxes

        reformatted[key].append(reformatted_row)
        counter[count_by(row)] += 1

    # The auxiliary table that lists cable lengths
    aux_data = [[length, number/2, number/2]
                for length, number in counter.items()]

    aux_table = tabl.tabulate(
        aux_data, headers=['Length', 'Black', color],
        tablefmt='latex_booktabs_raw') + '\n\n'
    output += textblock(
        aux_table+r'\vspace{1em} '+'\n'+r'\noindent '+msg,
        r'0.25\textwidth', r'\dimexpr-0.25\textwidth-1cm', r'0.2\paperheight')

    # The 3 main tables
    for key, data in reformatted.items():
        data = reformatted[key]
        output += latex_env(key, 'subsection*')
        output += longtable(data, headers, align)

    return output, counter


# Output #######################################################################

def write_to_latex_ppp(output_file, title, data, headers, color,
                       *args, **kwargs):
    content, _ = tabular_ppp(data, headers, color, *args, **kwargs)

    output = latex_preamble()
    output += fancystyle(title)
    output += r'\setlength\extrarowheight{1.5pt}'
    output += latex_begin(content)

    with open(output_file, 'w') as f:
        f.write(output)
