#!/usr/bin/env python
#
# License: BSD 2-clause
# Created: Mon Oct 28, 2019 at 1:27 PM
# Last Change: Mon Oct 28, 2019 at 01:40 PM  -bflaggs

import re

from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, './pyUTM')

from pyUTM.io import PcadReader, PcadNaiveReader
from pyUTM.io import write_to_csv
from pyUTM.sim import CurrentFlow

input_dir = Path('input')
output_dir = Path('output')

mirror_bp_netlist = input_dir / Path('mirror_backplane.net')
mirror_custom_bb_netlist = input_dir / Path('mirror_custom_telemetry_bb.net')
#path_finder_netlist = input_dir / Path('path_finder.net')
#dcb_netlist = input_dir / Path('dcb.net')

#debug_comet_mapping_filename = output_dir / Path('DebugCometMapping.csv')
#debug_dcb_path_finder_mapping_filename = output_dir / Path(
#  'DebugDcbPathFinderMapping.csv')

#comet_dcb_full_mapping_filename = output_dir / Path('CometDcbFullMapping.csv')
#comet_dcb_short_mapping_filename = output_dir / Path('CometDcbShortMapping.csv')


###########
# Helpers #
###########

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

def filter_comp(descr, regexp=r'^JD\d+|^JP\d+', netname=None):
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
  def filter_functor(l):
    return True if True in map(functor, l) else False

  return filter_functor


def post_filter_any(functor):
  def filter_functor(l):
    return False if False in map(functor, l) else True

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


#####################
# Read all netlists #
#####################

# NOTE: Net hopping won't work for COMET, nor COMET DB, because of the special
# resistors RNXX that have 8 legs, instead of 2.
#CometHopper = CurrentFlow([r'^R\d+', r'^NT\d+', r'^RN\d+_\d[ABCD]', r'^C\d+'])
#CometDBHopper = CurrentFlow([r'^R\d+', r'^NT\d+', r'^RN\d+[ABCD]'])

#CometReader = PcadNaiveReader(comet_netlist)
#CometDBReader = PcadNaiveReader(comet_db_netlist)

#comet_descr = split_rn(CometReader.read())
#comet_db_descr = split_rn(
#  CometDBReader.read(),
#  regexp=r'^RN((?!5$|6$|9$|12$|15$|18$|21$|24$|27$|39$|30$|33$|36$)\d+)$'
#)

# Manually do net hopping for COMET and COMET DB.
#PcadReader.make_equivalent_nets_identical(
#  comet_descr, CometHopper.do(comet_descr))
#PcadReader.make_equivalent_nets_identical(
#  comet_db_descr, CometDBHopper.do(comet_db_descr))

# Default net hopping should work for Pathfinder and DCB.
NetHopper = CurrentFlow()

#PathFinderReader = PcadReader(path_finder_netlist)
#DcbReader = PcadReader(dcb_netlist)

#path_finder_descr = PathFinderReader.read(NetHopper)
#dcb_descr = DcbReader.read(NetHopper)


MirrorBPReader = PcadNaiveReader(mirror_bp_netlist)
MirrorCustomBBReader = PcadNaiveReader(mirror_custom_bb_netlist)

mirror_bp_descr = MirrorBPReader.read(NetHopper)
mirror_custom_bb_descr = MirrorCustomBBReader.read(NetHopper)


# Will have to do this because using NetHopper errors
#MirrorBPHopper = CurrentFlow([PLACE COMPONENTS TO TREAT AS COPPER HERE])
#MirrorCustomBBHopper = CurrentFlow([PLACE COMPONENTS TO TREAT AS COPPER HERE])


#PcadReader.make_equivalent_nets_identical(
#    mirror_bp_descr, MirrorBPHopper.do(mirror_bp_descr))
#PcadReader.make_equivalent_nets_identical(
#    mirror_custom_bb_descr, MirrorCustomBBHopper.do(mirror_custom_bb_descr))



#mirror_bp_result = filter_comp(mirror_bp_descr, r'$^JDU[0123456789]|^JP')
#mirror_bp_result = filter_comp(mirror_bp_descr, r'$^JD\d|^JP\d')
#mirror_custom_bb_result = filter_comp(mirror_custom_bb_descr, r'$^JD\d|^JP\d')


#############
# Filtering #
#############


####################
# Make connections #
####################


#comet_dcb_data = []

#for gbtx_pin, path_finder_comet_pin in dcb_gbtxs_to_path_finder_comet.items():
#  row = []

#  row.append(dcb_ref[gbtx_pin])
#  row.append('-'.join(gbtx_pin))
#  row.append('-'.join(path_finder_comet_pin))

#  fpga_pin = comet_j1_j2_duo_to_fpga[path_finder_comet_pin]
#  row.append(path_finder_comet_pin[0]+'-'+'-'.join(fpga_pin))

#  row.reverse()

#  comet_dcb_data.append(row)


#################
# Output to csv #
#################

# Debug: COMET -> COMET DB -> COMET ############################################

#comet_j1_j2_fpga_data = [('-'.join(k), '-'.join(v))
#                         for k, v in comet_j1_j2_to_fpga.items()]
#comet_j1_j2_fpga_data.sort(
#  key=lambda x: re.sub(r'-(\d)$', r'-0\g<1>', x[0]))

#write_to_csv(debug_comet_mapping_filename, comet_j1_j2_fpga_data,
#             ['COMET connector', 'COMET FPGA'])


# Debug: DCB -> Pathfinder #####################################################

#dcb_gbtxs_path_finder_comet_data = [
#  (dcb_ref[k], '-'.join(k), '-'.join(v))
#  for k, v in dcb_gbtxs_to_path_finder_comet.items()]
# Make sure '1' appears before '10' and '11'
#dcb_gbtxs_path_finder_comet_data.sort(
#  key=lambda x: re.sub(r'CH(\d)_', r'CH0\g<1>_', x[0]))

#write_to_csv(
#  debug_dcb_path_finder_mapping_filename, dcb_gbtxs_path_finder_comet_data,
#  ['Signal ID', 'DCB data GBTx pin', 'Pathfinder COMET connector']
#)


# COMET FPGA -> DCB data GBTxs, full ###########################################

#comet_dcb_data.sort(
#  key=lambda x: re.sub(r'CH(\d)_', r'CH0\g<1>_', x[-1]))

#write_to_csv(
#  comet_dcb_full_mapping_filename, comet_dcb_data,
#  ['COMET FPGA pin', 'Pathfinder COMET connector', 'DCB data GBTx pin',
#   'Signal ID']
#)


# COMET FPGA -> DCB data GBTxs, short ##########################################

#comet_dcb_data_short = list(map(lambda x: (x[0], x[-1]), comet_dcb_data))

#write_to_csv(
#  comet_dcb_short_mapping_filename, comet_dcb_data_short,
#  ['COMET FPGA pin', 'Signal ID']
#)
