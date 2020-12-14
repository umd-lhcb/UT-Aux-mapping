#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 02:23 AM +0100

from pathlib import Path

input_dir = Path('input')
output_dir = Path('output')

# PPP-related ##################################################################

jp_hybrid_name = {
    'P1E': 'P1_EAST',
    'P1W': 'P1_WEST',
    'P2E': 'P2_EAST',
    'P2W': 'P2_WEST',
    'P3':  'P3',
    'P4':  'P4'
}

jp_hybrid_name_inverse = dict(map(reversed, jp_hybrid_name.items()))
