#Loic Daumail 04 20 2023
'''
The bold data was collected with less slices (4 less on top, 4 less at the bottom of the brain, along z axis).
Thus, this script's goal is to trim the corresponding top up nifti files to allow topup correction
'''
import os
import os.path as op
import numpy as np
import pandas as pd
import json
import glob

path = '/Users/tong_processor/Desktop/Loic/phantom_mri/data/BIDS_conv/Nifti_copy'

subjects = pd.read_csv(f"{path}/participants.tsv", sep='\t')

for subject in subjects.participant_id:
    fmapDir = f"{subject}/ses-01/fmap"
    TUjsons = [f for f in os.listdir(f"{path}/{fmapDir}") if f.endswith('epi.json')]
    TUnii = [f for f in os.listdir(f"{path}/{fmapDir}") if f.endswith('epi.nii.gz')]
    outPath = f"{path}/{fmapDir}/out"
    os.makedirs(outPath, exist_ok=True)
    #1 resize nifti file
    # for n in TUnii:
    #     niftiPath = glob.glob(f"{path}/{fmapDir}/{n}")[0]
    #     hdrdata = os.popen(f"fslinfo {niftiPath}").readlines()
    #     for line in hdrdata:
    #         if line.startswith('dim1'):
    #             xsize = int(line.split()[-1])
    #         if line.startswith('dim2'):
    #             ysize = int(line.split()[-1])
    #         if line.startswith('dim3'):
    #             zsize = int(line.split()[-1])
    #         if line.startswith('dim4'):
    #             tsize = int(line.split()[-1])
    #     cmd = f"fslroi {niftiPath} {outPath}/{n} 0 {xsize} 0 {ysize} 4 {zsize-8} 0 {tsize}"
    #     os.system(cmd)
    #2: change nifti header
    for n in TUnii:
        niftiPath = glob.glob(f"{path}/{fmapDir}/{n}")[0]
        hdrdata = os.popen(f"fslinfo {niftiPath}").readlines()
        for line in hdrdata:
            if line.startswith('dim3'):
                zsize = int(line.split()[-1])
    #3: change slice times