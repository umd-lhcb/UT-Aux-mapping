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

# Default net hopping should work for Custom BB.
NetHopper = CurrentFlow()

MirrorCustomBBReader = PcadReader(mirror_custom_bb_netlist)
mirror_custom_bb_descr = MirrorCustomBBReader.read(NetHopper)


MirrorBPReader = PcadNaiveReader(mirror_bp_netlist)
mirror_bp_descr = MirrorBPReader.read()


# Will have to do this because using NetHopper errors

#MirrorBPHopper = CurrentFlow([PLACE COMPONENTS TO TREAT AS COPPER HERE])
#MirrorBPHopper = CurrentFlow(
#  [r'^R\d+', r'^RB_\d+', r'^RBSP_\d+', r'^RSP_\d+', r'^RT\d+',
#   r'^C\d+', r'^CxRB_\d+', r'^NT\d+'])

MirrorBPHopper = CurrentFlow(
  [r'^R\d', r'^RB_\d', r'^RBSP_\d', r'^RSP_\d', r'^RT\d',
   r'^C\d', r'^CxRB_\d', r'^NT\d'])


PcadReader.make_equivalent_nets_identical(
    mirror_bp_descr, MirrorBPHopper.do(mirror_bp_descr))



#############
# Filtering #
#############

mirror_custom_bb_result = filter_comp(
  mirror_custom_bb_descr, r'^J_PT_\d+|^J_1V5_\d+|^J_2V5_\d+|^JT0$|^JT1$|^JT2$')


#mirror_bp_result = filter_comp(
#  mirror_bp_descr, r'^JP\d|^JS_PT_NINE_TEN_\d|^JS_PT_TEN_ELEVEN_\d|^JS_PT_EIGHT_NINE_\d'
#                   r'|^JS_PT_SIX_SEVEN_\d|^JS_PT_FIVE_SIX_\d|^JS_PT_FOUR_FIVE\d'
#                   r'|^JS_PT_TWO_THREE_\d|^JS_PT_ONE_TWO_\d|^JS_PT_ZERO_ONE_\d'
#                   r'|^JS_JPU_ZERO_\d|^JS_JPU_ONE_\d|^JS_JPU_TWO_\d')


mirror_bp_result = filter_comp(
  mirror_bp_descr, r'^JP\d|^JD\d|^JT0$|^JT1$|^JT2$')



# Mirror Custom BB ##########################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later as GND is the current problem)

filter_bb_throw_out = post_filter_any(
    lambda x: x[1] not in ['S1', 'S2', '29'])
mirror_custom_bb_result_filt = filter(filter_bb_throw_out, mirror_custom_bb_result)

mirror_custom_bb_result_list = list(mirror_custom_bb_result_filt)



# Mirror Backplane ##########################################
# NOT USED IN FINDING CONNECTIONS (throw out GND later as GND is the current problem)

filter_bp_throw_gnd = post_filter_any(
    lambda x: x[1] not in ['29'])
mirror_bp_result_filt = filter(filter_bp_throw_gnd, mirror_bp_result)

mirror_bp_result_list = list(mirror_bp_result_filt)


##################################################
# Find Mirror BB to Mirror Backplane Connections #
##################################################
# Mirror Custom Telemetry BB -> Mirror Backplane ######################


mirror_bb_ref = make_comp_netname_dict(mirror_custom_bb_descr)
mirror_bp_ref = make_comp_netname_dict(mirror_bp_descr)

compnames_mirror_bb = mirror_bb_ref.keys()
netnames_mirror_bb = mirror_bb_ref.values()
list_comp_bb = list(compnames_mirror_bb)
list_nets_bb = list(netnames_mirror_bb)

compnames_mirror_bp = mirror_bp_ref.keys()
netnames_mirror_bp = mirror_bp_ref.values()
list_comp_bp = list(compnames_mirror_bp)
list_nets_bp = list(netnames_mirror_bp)

mirror_bb_to_mirror_bp_map = []

for i in range(len(list_nets_bb)):
  row = []
  for j in range(len(list_nets_bp)):
    if (list_comp_bb[i][0] == list_comp_bp[j][0] and list_comp_bb[i][1] == list_comp_bp[j][1]):
      
      row.append(list_nets_bb[i])
      row.append('-'.join(list_comp_bb[i]))
      row.append(list_nets_bp[j])

      mirror_bb_to_mirror_bp_map.append(row)

# THE ABOVE WORKS ALTHOUGH IT SAYS THAT SOME NETS GO TO GROUND WHEN THEY SHOULDN'T
# As of now, I know that the "..._2V5_SENSE_..." lines all go to GND when they actually don't
# These all go to "GND" because they have ""ClassName" "NetTie"" listed underneath their net names




#mirror_bb_to_mirror_bp = [make_comp_comp_dict(
#  mirror_custom_bb_result_list, r'^J_PT_\d+', 'JT{0}'.format(str(i)))
#  for i in range(1, 4)]





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
