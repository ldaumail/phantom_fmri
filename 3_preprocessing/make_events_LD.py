#Loic Daumail 04/18/2023
'''
makes BIDS and FEAT compliant event files
'''

import os
import glob
import numpy as np
import pandas as pd
from scipy.io import loadmat

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
event_dir_feat = f"{path}/derivatives/FEAT/events_3column"
os.makedirs(event_dir_feat, exist_ok=True)
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
for idx, subject in enumerate(subjects.participant_id):
    subject = subject[4:]
    for s, session in enumerate(np.unique(subjects.group)):
        for scan in ['phantom']:
            event_dir_feat = f"{path}/derivatives/FEAT/events_3column/sub-{subject}/ses-{s + 1}/task-{scan}"
            os.makedirs(event_dir_feat, exist_ok=True)
            eventDir_source = f"/sourceData/{subject}/events/task-{scan}"
            runs = [f for f in os.listdir(f"{path}{eventDir_source}/") if f.endswith('.mat')]  # get all json files
            for r, run in enumerate(runs):

                log_path = glob.glob(f"{path}{eventDir_source}/{run}")
                assert len(log_path) == 1
                log_path = log_path[0]
                log_data = loadmat(log_path)
                event_data = log_data['ex']
                ## task info
                initialFixation = 14
                blockLength = 14
                betweenBlocks = 14
                block_order = []
                cond_order = []
                num_blocks =event_data[0, 0][26][0][0]
                for b in range(num_blocks):
                    item = event_data[0, 0][27][0][b]
                    condName = event_data[0,0][23][0][item-1][0]
                    block_order.append(item)
                    cond_order.append(condName)

                event_path = f"{path}/{bids}/sub-{subject}/ses-{s + 1:02}/func/sub-{subject}_ses-{s + 1:02}_task-{scan}_dir-AP_run-{r + 1:03}_events.tsv"
                events = open(event_path, 'w+')
                events.write('onset\tduration\ttrial_type\n')
                cond_names = np.unique(cond_order)
                for c, cond in enumerate(cond_names):

                    event_path_feat = f"{event_dir_feat}/sub-{subject}_ses-{s + 1:02}_task-{scan}_run-{r + 1:03}_{cond}.txt"
                    these_positions = [np.where(np.array(block_order) == c+1)][0][0]
                    with open(event_path_feat, 'w+') as file:
                        for p in these_positions:
                            start = int(
                                initialFixation + p * (blockLength + betweenBlocks))
                            file.write('%i\t%i\t1' % (start, blockLength))
                            events.write(f'{start}\t{blockLength}\t{cond}\n')
                            if p != these_positions[-1]:
                                file.write('\n')
                    file.close()
                events.close()


# if __name__ == "__main__":
#     os.chdir(op.expanduser("~/david/projects/p022_occlusion/in_vivo/fMRI/exp2"))
#     make_events()

