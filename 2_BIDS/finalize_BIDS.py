# /usr/bin/python
# Created by Loic Daumail on 04 05 2023
"""
Finalizes changes to data after running heudiconv to convert raw data into BIDS
"""

import os
import os.path as op
import sys
import glob
import shutil
from shutil import copytree
import json
import pandas as pd
import stat

#def finalizeBIDS():
path = '/home/tonglab/Loic/phantom_mri_data/Nifti'
os.chdir(path)
# make link to fMRI custom scripts dir
if not op.exists(f"code/utils"):
 os.system(f"ln -s /home/tonglab/Loic/mri_code/phantom_fmri-main/2_BIDS/utils code/utils")
sys.path.append("code")

from utils import philips_slice_timing
    # #from utils import make_anat_slices
print(f"Finalizing BIDS...")
    #subjects = json.load(open("participants.json", "r+"))
subjects = pd.read_csv('participants.tsv', sep='\t')
#filetypes = ["nii", "json"]  # do not include other filetypes that may cause BIDS errors
if 'control' in subjects.group.unique():
    sesNum = 1

for subject in subjects.participant_id:

    sourcedir = f"{path}/{subject}/"
    os.chdir(sourcedir)
    sesDir = 'ses-0%s' %sesNum
    funcdir = f"{sourcedir}{sesDir}/func"
    fmapdir = f"{sourcedir}{sesDir}/fmap"
    anatdir = f"{sourcedir}{sesDir}/anat"

    os.makedirs(sesDir, exist_ok=True)
    # shutil.move(funcdir, f"{sesDir}/func", copy_function=copytree)  # move files, don"t copy
    # shutil.move(fmapdir, f"{sesDir}/fmap", copy_function=copytree)
    # shutil.move(anatdir, f"{sesDir}/anat", copy_function=copytree)
    # tsvf = [f for f in os.listdir(sourcedir) if f.endswith('.tsv')]
    # shutil.move(tsvf[0], f"{sesDir}")

    ### FUNC ###

    ## ADD PHASE ENCODING DIRECTION TO FUNCTIONAL SCANS .JSON FILE AND CORRESPONDING TOPUP SCANS .JSON FILE
    ## ADD TOTAL READOUT TIME
    ## ADD SLICE TIMING
    ## LINK FUNC SCANS TO TOPUP SCANS
    #os.chdir(sesDir)
    jsons = [f for f in os.listdir(f"{sesDir}/func") if f.endswith('.json')] #get all json files
    TUjsons = [f for f in os.listdir(f"{sesDir}/fmap") if f.endswith('epi.json')]  # get corresponding topup json files
    for j in jsons:
        runNum = j[-17:-10]  # make sure you take the topup file of the right run
        jsonpath = f"{sesDir}/func/{j}"
        #os.chmod(jsonpath,stat.S_IRUSR | stat.S_IWUSR | stat.S_IRWXG)#| stat.S_IRGRP | stat.S_IWGRP)
        #os.chmod(jsonpath, stat.S_IRWXU | stat.S_IRWXG)
        # os.system(f"chmod +rwx {jsonpath}")
        boldJson = json.load(open(jsonpath, "r+"))
        if "TaskName" not in boldJson:
            scandata["TaskName"] = j[21:-25]
        if "PhaseEncodingDirection" not in boldJson:
            boldJson["PhaseEncodingDirection"] = "j-"
        if "SliceTiming" not in boldJson:
            boldJson["SliceTiming"] = philips_slice_timing(jsonpath)
        if "TotalReadoutTime" not in boldJson:
            if "EstimatedTotalReadoutTime" in boldJson:
                boldJson["TotalReadoutTime"] = boldJson["EstimatedTotalReadoutTime"]
            elif "EstimatedTotalReadoutTime" not in boldJson:
                boldJson["TotalReadoutTime"] = 0.0325728 #artbitrary value, based on phantom experiment runs
        # if "B0FieldIdentifier" not in boldJson:
        #     identifier = 'epi_bold_%s_fmap'%runNum
        #     boldJson["B0FieldIdentifier"] = identifier
        # if "B0FieldSource" not in boldJson:
        #     source = 'epi_bold_%s_fmap'%runNum
        #     boldJson["B0FieldSource"] = source
        json.dump(boldJson, open(jsonpath, "w+"), sort_keys=True, indent=4)

        # repeat for top up file

        TUjson = [s for s in TUjsons if runNum in s]
        TUjsonpath = f"{sesDir}/fmap/{TUjson[0]}"
        os.chmod(TUjsonpath, stat.S_IRWXU | stat.S_IRWXG)
        epiJson = json.load(open(TUjsonpath, "r+"))
        if "PhaseEncodingDirection" not in epiJson:
            epiJson["PhaseEncodingDirection"] = "j"
        if "SliceTiming" not in epiJson:
            epiJson["SliceTiming"] = philips_slice_timing(TUjsonpath)
        if "TotalReadoutTime" not in epiJson:
            if "EstimatedTotalReadoutTime" in epiJson:
                epiJson["TotalReadoutTime"] = epiJson["EstimatedTotalReadoutTime"]
            elif "EstimatedTotalReadoutTime" not in epiJson:
                epiJson["TotalReadoutTime"] = 0.0333996 #arbitrary realistic value, based on phantom topup runs
        if "IntendedFor" not in epiJson:
            nifti_target = f"{subject}/{jsonpath[:-5]}.nii.gz"  # link bold run nifti path to the corresponding epi json file for topup
            epiJson["IntendedFor"] = nifti_target[9:]
        # if "B0FieldIdentifier" not in epiJson:
        #     identifier = 'epi_bold_%s_fmap' % runNum
        #     epiJson["B0FieldIdentifier"] = identifier
        json.dump(epiJson, open(TUjsonpath, "w+"), sort_keys=True, indent=4)


    # ANAT

    ## 1) Modify filenames of b0 shimmed scans (magnitude file and associated fieldmap file)
    os.chdir(fmapdir)

    for file in os.listdir():
        if 'magnitude1' in file:
            newfile = file.replace('magnitude1', 'magnitude')
            os.rename(file, newfile)
        elif 'magnitude2' in file:
            newfile = file.replace('magnitude2', 'fieldmap')
            os.rename(file, newfile)
    files = os.listdir()
    ## 2) edit .tsv file accordingly
    os.chdir(f"../")
    subjfname = '%s_ses-0%s_scans.tsv' % (subject, sesNum)
    subjscans = pd.read_csv(subjfname, sep='\t')
    subjscans = subjscans.replace('magnitude1', 'magnitude', regex=True)
    subjscans = subjscans.replace('magnitude2', 'fieldmap', regex=True)
    subjscans.to_csv(subjfname, sep='\t')  # save updated table to replace the old one


    # Link b0 shimmed fieldmaps to anat scans
    # add required meta data to json file
    fmapjson = [f for f in os.listdir(fmapdir) if f.endswith('acq-b0shimmed_run-001_fieldmap.json') or f.endswith('acq-b0shimmed_run-001_magnitude.json')]

    for fmap in fmapjson:
        fmapjsonpath = f"{fmapdir}/{fmap}"
        scandata = json.load(open(fmapjsonpath, "r+"))
        if "IntendedFor" not in scandata:
            intendedscans = glob.glob(f"{path}/{subject}/ses-{sesNum:02}/func/*.nii*")
            intendedscans += glob.glob(f"{path}/{subject}/ses-{sesNum:02}/anat/*.nii*")
            scandata["IntendedFor"] = sorted([x[77:] for x in intendedscans])
        json.dump(scandata, open(fmapjsonpath, "w+"), sort_keys=True, indent=4)

## Localizer,rest and prf files:total readout time
# base = '/home/tonglab/Loic/phantom_mri_data'
# for subject in subjects.participant_id:
#
#     niftidir = f"{base}/sourceData/{subject}/0{sesNum}/"
