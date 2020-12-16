#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Wed Dec 16, 2020 at 01:20 AM +0100

from pathlib import Path

from pyUTM.io import WirelistNaiveReader
from itertools import permutations

from UT_Aux_mapping.const import input_dir
from UT_Aux_mapping.helpers import ppp_netname_regulator


#####################
# Read all netlists #
#####################

netlists = {}


def read_net(path, name, ext='wirelist', reader=WirelistNaiveReader):
    loc_reader = reader(path / Path(name+'.'+ext))
    return loc_reader.read()


ppp_vars = ['true_ppp', 'mirror_ppp']
netlists.update({k: read_net(input_dir, k) for k in ppp_vars})


##########
# Checks #
##########

netnames = {}


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
                 for k in netlists.keys()})

uniq_ppp = {'in {} not {}'.format(k1, k2):
            uniq_elems(netnames[k1], netnames[k2])
            for k1, k2 in permutations(ppp_vars, 2)}
print_uniq(uniq_ppp)
