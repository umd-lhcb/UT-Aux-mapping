#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Fri May 28, 2021 at 03:43 AM +0200

from pathlib import Path
from itertools import permutations
from collections.abc import Iterable

from pyUTM.io import WirelistNaiveReader, PcadNaiveReader

from UT_Aux_mapping.const import input_dir
from UT_Aux_mapping.helpers import ppp_netname_regulator


#####################
# Read all netlists #
#####################

netlists = {}


def read_net(path, name, ext='wirelist', reader=WirelistNaiveReader):
    loc_reader = reader(path / Path(name+'.'+ext))
    return loc_reader.read()


ppp_vars = ['c_true_ppp_mag', 'c_mirror_ppp_mag']
netlists.update({k: read_net(input_dir, k) for k in ppp_vars})

p2b2_vars = ['true_p2b2', 'mirror_p2b2']
netlists.update({k: read_net(input_dir, k, 'net', PcadNaiveReader)
                 for k in p2b2_vars})


##########
# Checks #
##########

netnames = {}


def flatten(iterable, depth=0, max_depth=-1):
    output = []

    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, str):
            if depth == max_depth:
                output.append(item)
            else:
                output += flatten(item, depth+1, max_depth)

        else:
            output.append(item)

    return output


def uniq_elems(l1, l2):
    return [i for i in l1 if i not in l2]


def print_uniq(uniq_d):
    for rule, result in uniq_d.items():
        if result:
            print('The following nets are {}:'.format(rule))
            print('\n'.join(result))
            print('')


# Check if there's nets that a unique to one variant
netnames.update({k: [ppp_netname_regulator(n) for n in netlists[k].keys()]
                 for k in ppp_vars})

uniq_ppp = {'in {} not {}'.format(k1, k2):
            uniq_elems(netnames[k1], netnames[k2])
            for k1, k2 in permutations(ppp_vars, 2)}
print_uniq(uniq_ppp)


# Check nets that are unique to P2B2
netnames.update({k: [n for n in netlists[k].keys()] for k in p2b2_vars})

uniq_p2b2 = {'in {} not {}'.format(k1, k2):
             uniq_elems(netnames[k1], netnames[k2])
             for k1, k2 in
             flatten(map(permutations, zip(ppp_vars, p2b2_vars)), max_depth=1)}
print_uniq(uniq_p2b2)
