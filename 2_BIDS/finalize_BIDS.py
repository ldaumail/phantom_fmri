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
path = '/Users/tong_processor/Desktop/Loic/phantom_mri/data/BIDS_conv/Nifti'
os.chdir(path)
# make link to fMRI custom scripts dir
if not op.exists(f"code/utils"):
 os.system(f"ln -s $HOME/Desktop/Loic/mri_code/loic_code/BIDS/utils code/utils")
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
    funcdir = f"{sourcedir}func"
    fmapdir = f"{sourcedir}fmap"
    anatdir = f"{sourcedir}anat"
    sesDir = 'ses-0%s' %sesNum
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
        os.chmod(jsonpath, stat.S_IRWXU | stat.S_IRWXG)
        boldJson = json.load(open(jsonpath, "r+"))

        if "PhaseEncodingDirection" not in boldJson:
            boldJson["PhaseEncodingDirection"] = "j-"
        if "SliceTiming" not in boldJson:
            boldJson["SliceTiming"] = philips_slice_timing(jsonpath)
        if "TotalReadoutTime" not in boldJson:
            boldJson["TotalReadoutTime"] = boldJson["EstimatedTotalReadoutTime"]
        if "B0FieldIdentifier" not in boldJson:
            identifier = 'epi_bold_%s_fmap'%runNum
            boldJson["B0FieldIdentifier"] = identifier
        if "B0FieldSource" not in boldJson:
            source = 'epi_bold_%s_fmap'%runNum
            boldJson["B0FieldSource"] = source
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
            epiJson["TotalReadoutTime"] = epiJson["EstimatedTotalReadoutTime"]
        if "IntendedFor" not in epiJson:
            nifti_target = f"{subject}/{jsonpath[:-5]}.nii.gz"  # link bold run nifti path to the corresponding epi json file for topup
            epiJson["IntendedFor"] = nifti_target[9:]
        if "B0FieldIdentifier" not in epiJson:
            identifier = 'epi_bold_%s_fmap' % runNum
            epiJson["B0FieldIdentifier"] = identifier
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
            scandata = json.load(open(outpath, "r+"))
            if "IntendedFor" not in scandata:
                intendedscans = glob.glob(f"sub-{subject}/ses-{s + 1}/func/*.nii")
                if subject not in ["F016", "M012", "M015"]:
                    intendedscans += glob.glob(f"sub-{subject}/ses-{s + 1}/anat/*.nii")
                scandata["IntendedFor"] = sorted([x[9:] for x in intendedscans])
            if component == "fieldmap" and "Units" not in scandata:
                scandata["Units"] = "Hz"
            json.dump(scandata, open(outpath, "w+"), sort_keys=True, indent=4)



