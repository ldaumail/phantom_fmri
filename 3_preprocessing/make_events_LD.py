#Loic Daumail 04/18/2023

'''
makes BIDS and FEAT compliant event files
'''

import os
import os.path as op
import sys
import glob
from argparse import Namespace
import numpy as np
import pandas as pd
from scipy.io import loadmat
import itertools
import json

#sys.path.append(op.expanduser("~/david/masterScripts/fMRI"))

path = '/Users/tong_processor/Desktop/Loic/phantom_mri/data'
bids = 'BIDS_conv/Nifti'
print(f'making event files...')
subjects = pd.read_csv(f"{path}/{bids}/participants.tsv", sep='\t')
# design_data = json.load(open('sourcedata/design.json', 'r+'))

# scans with fixed stimulus order
# scan = 'objectLocaliser'
# params = Namespace(**design_data[scan])
# cond_names = params.conditions['category']
# event_path = f'task-{scan}_events.tsv'
# events = open(event_path, 'w+')
# events.write('onset\tduration\ttrial_type\n')
# event_dir_feat = "derivatives/FEAT/events_3column"
# os.makedirs(event_dir_feat, exist_ok=True)
#
# for c, cond in enumerate(cond_names):
#
#     event_path_feat = f"{event_dir_feat}/task-objectLocaliser_{cond}.txt"
#     these_positions = [np.where(np.array(params.block_order) == c)][0][0]
#     with open(event_path_feat, 'w+') as file:
#         for p in these_positions:
#             start = int(params.initial_fixation + p * (params.block_duration + params.interblock_interval))
#             file.write(f'%i\t%i\t1' % (start, params.block_duration))
#             events.write(f'{start}\t{params.block_duration}\t{cond}\n')
#             if p != these_positions[-1]:
#                 file.write('\n')  # a blank line as last row confuses _feat
#     file.close()
# events.close()

# scans with variable stimulus order
occluder_conversion = {'top': 'upper', 'bot': 'lower', 'n': 'none'}
for subject in subjects.participant_id:
    for s, session in enumerate(subjects.group[subject]):
        subject = subject[4:]
        for scan in ['phantom']:
            event_dir_feat = f"{path}/derivatives/FEAT/events_3column/sub-{subject}/ses-{s + 1}/task-{scan}"
            os.makedirs(event_dir_feat, exist_ok=True)

            params = #Namespace(**design_data[scan])
            num_blocks = #int(((params.dynamics * params.TR) - (params.initial_fixation + params.final_fixation)) / (
                    #params.block_duration + params.interblock_interval))
            variables = #list(params.conditions)
            levels = #[params.conditions[variable] for variable in variables]
            conds = #list(itertools.product(*levels))
            cond_names = []
            for cond in conds:
                cond_names.append(f'{cond[0]}_{cond[1]}')
            eventDir_source = f"/sourceData/{subject}/events/task-{scan}"
            runs = [f for f in os.listdir(f"{path}{eventDir_source}/") if f.endswith('.mat')]  # get all json files
            for run in enumerate(runs):

                log_path = glob.glob(f"{path}{eventDir_source}/*_rn{run}_*")
                assert len(log_path) == 1
                log_path = log_path[0]
                log_data = loadmat(log_path)
                event_data = log_data['ex']
                block_order = []
                num_blocks =event_data[0, 0][26][0][0]
                for b in range(num_blocks):
                    thisCond = []
                    item = event_data[0, 0][27][0][b]
                    image = item[1][0]
                    occlusion_type = item[2][0][0][0]
                    occ_type = occluder_conversion[occlusion_type]
                    thisCond.append(f'{image}_{occ_type}')
                    block_order.append(cond_names.index(thisCond[0]))

                event_path = f"sub-{subject}/ses-{s + 1}/func/sub-{subject}_ses-{s + 1}_task-{scan}_run-{run + 1:02}_events.tsv"
                events = open(event_path, 'w+')
                events.write('onset\tduration\ttrial_type\n')

                for c, cond in enumerate(cond_names):

                    event_path_feat = f"{event_dir_feat}/sub-{subject}_ses-{s + 1}_task-{scan}_run-{run + 1:02}_{cond}.txt"
                    these_positions = [np.where(np.array(block_order) == c)][0][0]
                    with open(event_path_feat, 'w+') as file:
                        for p in these_positions:
                            start = int(
                                params.initial_fixation + p * (params.block_duration + params.interblock_interval))
                            file.write('%i\t%i\t1' % (start, params.block_duration))
                            events.write(f'{start}\t{params.block_duration}\t{cond}\n')
                            if p != these_positions[-1]:
                                file.write('\n')
                    file.close()
                events.close()


# if __name__ == "__main__":
#     os.chdir(op.expanduser("~/david/projects/p022_occlusion/in_vivo/fMRI/exp2"))
#     make_events()

