#!/usr/bin/env python
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Sun Dec 13, 2020 at 11:55 PM +0100

from pathlib import Path

from pyUTM.io import PcadNaiveReader
from pyUTM.io import write_to_csv

from UT_Aux_mapping.const import input_dir, output_dir
from UT_Aux_mapping.helpers import ppp_netname_regulator
from UT_Aux_mapping.helpers import gen_filename

true_p2b2_netlist = input_dir / Path('true_p2b2.net')
ppp_netlist = input_dir / Path('ppp.net')

variants = ['Full', 'Partial', 'Depopulated']

output_csv = [output_dir / gen_filename(__file__+var) for var in variants]
output_tex = [output_dir / gen_filename(__file__+var, 'tex')
              for var in variants]


#####################
# Read all netlists #
#####################

TrueP2B2Reader = PcadNaiveReader(true_p2b2_netlist)
true_p2b2_descr = TrueP2B2Reader.read()

PPPReader = PcadNaiveReader(ppp_netlist)
ppp_descr = PPPReader.read()


############################################################
# Fix PPP netname irregularities and only keep JPU entries #
############################################################

# This stores name before and after the fix
ppp_name_errata = {k: ppp_netname_regulator(k) for k in ppp_descr.keys()}
ppp_descr = {ppp_name_errata[k]: v for k, v in ppp_descr.items()}

# For this part, only the JPU connectors are relevant
ppp_descr = {k: v for k, v in ppp_descr.items() if 'JPU' in k}
