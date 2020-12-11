#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Fri Dec 11, 2020 at 02:11 AM +0100

import re

from collections import defaultdict
from os.path import basename


# Generate default output filename #############################################

def gen_filename(raw):
    return basename(raw).split('.')[0] + '.csv'


# Regularize input #############################################################

def split_rn(descr, regexp=r'^RN\d+_\d$'):
    rn_split_dict = {
        '1': 'A',
        '8': 'A',
        '2': 'B',
        '7': 'B',
        '3': 'C',
        '6': 'C',
        '4': 'D',
        '5': 'D'
    }
    result = defaultdict(list)

    for net, comps in descr.items():
        for c in comps:
            if bool(re.search(regexp, c[0])):
                new_c = list(c)
                new_c[0] += rn_split_dict[c[1]]
                result[net].append(tuple(new_c))

            else:
                result[net].append(c)

    return dict(result)


# Filtering ####################################################################

def filter_comp(descr, regexp=r'^J\d+|^IC3_1+', netname=None):
    filtered = []

    for net, comps in descr.items():
        if netname is not None and netname not in net:
            # We also optionally filter by netname.
            pass

        else:
            processed_comps = [x for x in comps if bool(re.match(regexp, x[0]))]

            # Can't figure out any relationship if a list contains only a single
            # item.
            # We also do deduplication here.
            # Also make sure there's at least a connector component.
            if len(processed_comps) > 1 and processed_comps not in filtered \
                    and True in map(lambda x: x[0].startswith('J'),
                                    processed_comps):
                filtered.append(processed_comps)

    return filtered


def post_filter_exist(functor):
    def filter_functor(lst):
        return True if True in map(functor, lst) else False

    return filter_functor


def post_filter_any(functor):
    def filter_functor(lst):
        return False if False in map(functor, lst) else True

    return filter_functor


# Make dictionaries to find connectivity between components  ###################

def make_comp_netname_dict(descr):
    result = {}

    for net, comps in descr.items():
        for c in comps:
            result[c] = net

    return result


def make_comp_comp_dict(nested, key_comp, value_comp, strip_kw='_1'):
    result = {}

    for comps in nested:
        key_candidates = list(filter(lambda x: x[0] == key_comp, comps))
        value_candidates = list(filter(lambda x: x[0] == value_comp, comps))

        if key_candidates and value_candidates:
            if len(key_candidates) > 1 or len(value_candidates) > 1:
                raise ValueError(
                    'Unable to construct a bijection for key: {}, value: {}'.format(
                        key_candidates, value_candidates
                    ))
            else:
                # We want to strip out the '_1' part
                key = list(key_candidates[0])
                value = list(value_candidates[0])

                key[0] = key[0].replace(strip_kw, '')
                value[0] = value[0].replace(strip_kw, '')

                result[tuple(key)] = tuple(value)

    return result


def make_comp_comp_dict_bidirectional(nested):
    # NOTE: Here 'nested' should be a nx2 tensor
    result = {}

    for key1, key2 in nested:
        result[key1] = key2
        result[key2] = key1

    return result
