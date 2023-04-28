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
import sys
path = '/home/tonglab/Loic/phantom_mri_data/Nifti'
os.chdir(path)
sys.path.append("code")
from utils import philips_slice_timing

subjects = pd.read_csv(f"{path}/participants.tsv", sep='\t')

for subject in subjects.participant_id:
    fmapDir = f"{subject}/ses-01/fmap"
    TUnii = [f for f in os.listdir(f"{path}/{fmapDir}") if f.endswith('epi.nii.gz')]
    outPath = f"{path}/{fmapDir}/out"
    os.makedirs(outPath, exist_ok=True)
    #1 resize nifti file (this will also change nifti header dim 3 size)
    for n in TUnii:
        niftiPath = glob.glob(f"{path}/{fmapDir}/{n}")[0]
        hdrdata = os.popen(f"fslinfo {niftiPath}").readlines()
        for line in hdrdata:
            if line.startswith('dim1'):
                 xsize = int(line.split()[-1])
            if line.startswith('dim2'):
                 ysize = int(line.split()[-1])
            if line.startswith('dim3'):
                 zsize = int(line.split()[-1])
            if line.startswith('dim4'):
                 tsize = int(line.split()[-1])
        cmd = f"fslroi {niftiPath} {outPath}/{n} 0 {xsize} 0 {ysize} 4 {zsize-8} 1 {tsize-1}"
        os.system(cmd)
        os.system(f"rm {niftiPath}")
        os.system(f"mv {outPath}/{n} {niftiPath}")

    os.system(f"rm -r {outPath}")

    #2: change slice times in associated json file (we will just recompute the slice times, even though they are wrong, we just want to have as many slice times as slices)

for subject in subjects.participant_id:
    fmapDir = f"{subject}/ses-01/fmap"
    TUjsons = [f for f in os.listdir(f"{path}/{fmapDir}") if f.endswith('epi.json')]
    #1 resize nifti file (this will also change nifti header dim 3 size)

    for n in TUjsons:
        jsonpath = f"{path}/{fmapDir}/{n}"
        epiJson = json.load(open(jsonpath, "r+"))
        epiJson["SliceTiming"] = philips_slice_timing(jsonpath)
        json.dump(epiJson, open(jsonpath, "w+"), sort_keys=True, indent=4)