#Loic Daumail 04/18/2023
'''
makes BIDS and FEAT compliant event files
'''

import os
import glob
import numpy as np
import pandas as pd
from scipy.io import loadmat

path = '/home/tonglab/Loic/phantom_mri_data'
bids = '/Nifti'
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

# scans with variable stimulus order
for idx, subject in enumerate(subjects.participant_id):
    subject = subject[4:]
    for s, session in enumerate(np.unique(subjects.group)):
        for scan in ['phantom']:
            event_dir_feat = f"{path}/derivatives/FEAT/events_3column/sub-{subject}/ses-{s + 1}/task-{scan}"
            os.makedirs(event_dir_feat, exist_ok=True)
            eventDir_source = f"/sourceData/{subject}/0{s+1}/events/task-{scan}"
            runs = [f for f in os.listdir(f"{path}{eventDir_source}/") if (f.endswith('.mat') and f[0].startswith('.') == False)]  # get all json files
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

# scans with fixed stimulus order
#1 Localizer task
blockLength = 12            # in seconds
betweenBlocks = 12          # in seconds
initialFixation = 12        # in seconds
finalFixation = 12          # in seconds
numBlocks = 12
cond_names = ['Inducers', 'Phantom']
#There were 2 conditions, 1 and 2. Blocks were ordered as 1,2,1,2...etc so 6 blocks per condition total
for idx, subject in enumerate(subjects.participant_id):
    subject = subject[4:]
    for s, session in enumerate(np.unique(subjects.group)):
        for scan in ['localizer']:
            event_dir_feat = f"{path}/derivatives/FEAT/events_3column/sub-{subject}/ses-{s + 1}/task-{scan}"
            os.makedirs(event_dir_feat, exist_ok=True)
            eventDir_source = f"/sourceData/{subject}/0{s+1}/events/task-{scan}"
            runs = [f for f in os.listdir(f"{path}{eventDir_source}/") if (f.endswith('.mat') and f[0].startswith('.') == False)]  # get all json files
            for r, run in enumerate(runs):
                #
                log_path = glob.glob(f"{path}{eventDir_source}/{run}")
                assert len(log_path) == 1
                log_path = log_path[0]
                log_data = loadmat(log_path)
                event_data = log_data['experiment']
                cond_order = event_data[0,0][12][0]
                event_path = f"{path}/{bids}/sub-{subject}/ses-{s + 1:02}/func/sub-{subject}_ses-{s + 1:02}_task-{scan}_dir-AP_run-{r + 1:03}_events.tsv"
                with open(event_path, 'w+') as events:
                    events.write('onset\tduration\ttrial_type\n')
                    for c, cond in enumerate(cond_names):

                        event_path_feat = f"{event_dir_feat}/task-Localiser_{cond}.txt"
                        these_positions = [np.where(np.array(cond_order) == c+1)][0][0]
                        with open(event_path_feat, 'w+') as file:
                            for p in these_positions:
                                start = int(initialFixation + p * (blockLength + betweenBlocks))
                                file.write(f'%i\t%i\t1' % (start, blockLength))
                                events.write(f'{start}\t{blockLength}\t{cond}\n')
                                if p != these_positions[-1]:
                                    file.write('\n')  # a blank line as last row confuses _feat
                        file.close()
                events.close()


# prf task
initialFixation = 22        # in seconds
finalFixation = 22          # in seconds
blockLength = 300 - finalFixation
betweenBlocks = 0
cond_names = ['travellingWedge']
for subject in ([subjects.participant_id[1]]):
    subject = subject[4:]
    for s, session in enumerate(np.unique(subjects.group)):
        for scan in ['prfcw', 'prfccw']:
            event_dir_feat = f"{path}/derivatives/FEAT/events_3column/sub-{subject}/ses-{s + 1}/task-{scan[0:3]}"
            os.makedirs(event_dir_feat, exist_ok=True)
            eventDir_source = f"/sourceData/{subject}/0{s + 1}/events/task-{scan[0:3]}"
            runs = [f for f in os.listdir(f"{path}{eventDir_source}/") if
                    (f.endswith('.mat') and f[0].startswith('.') == False)]  # get all json files
            for r, run in enumerate(runs):
                log_path = glob.glob(f"{path}{eventDir_source}/{run}")
                assert len(log_path) == 1
                event_path = f"{path}/{bids}/sub-{subject}/ses-{s + 1:02}/func/sub-{subject}_ses-{s + 1:02}_task-{scan}_dir-AP_run-{r + 1:03}_events.tsv"
                cond_order = 1
                with open(event_path, 'w+') as events:
                    events.write('onset\tduration\ttrial_type\n')
                    for c, cond in enumerate(cond_names):

                        event_path_feat = f"{event_dir_feat}/task-prf_{cond}.txt"
                        these_positions = [np.where(np.array(cond_order) == c+1)][0][0]
                        with open(event_path_feat, 'w+') as file:
                            for p in these_positions:
                                start = int(initialFixation + p * (blockLength + betweenBlocks))
                                file.write(f'%i\t%i\t1' % (start, blockLength))
                                events.write(f'{start}\t{blockLength}\t{cond}\n')
                                if p != these_positions[-1]:
                                    file.write('\n')  # a blank line as last row confuses _feat
                        file.close()
                events.close()

# if __name__ == "__main__":
#     os.chdir(op.expanduser("~/david/projects/p022_occlusion/in_vivo/fMRI/exp2"))
#     make_events()

