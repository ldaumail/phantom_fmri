import os
import os.path as op
import sys
import glob
import json
import pandas as pd
import shutil
import subprocess
import time

path = '/Users/tong_processor/Desktop/Loic/phantom_mri/data'
bids = 'BIDS_conv/Nifti_topup'
# run mriqc
version = "v23.1.0rc0" #downloaded on 04/18/2023 version is 23.1.0rc0
outdir = f"{path}/derivatives/mriqc-{version}"
os.makedirs(outdir, exist_ok=True)
subjects = pd.read_csv(f"{path}/{bids}/participants.tsv", sep='\t')
# individual subjects #{op.abspath('')}
for subject in subjects.participant_id:
    subject = subject[4:]
    if not op.isdir(f"{outdir}/sub-{subject}"):
        cmd = f"docker run --memory=\"22g\" --rm " \
              f"-v {path}/{bids}:/data:ro " \ 
              f"-v {path}/derivatives/mriqc-{version}:/out " \
              f"nipreps/mriqc:{version} " \
              f"--n_cpus 8 " \
              f"--verbose-reports " \
              f"/data /out participant --participant_label {subject} --no-sub"  # indir, outdir, analysis level
        os.system(cmd)
#mriqc /data/datasets/hcph-pilot/ /data/derivatives/hcph-pilot/mriqc participant -m T1w -vv -w ./work --omp-nthreads 12 --nprocs 36
# f"--mem_gb=10 "  \
#
# group level
if not os.path.isfile(f"{outdir}/group_bold.html"):
    cmd = cmd[:-(len(" participant_label XXXX --no-sub "))]  # remove subject label from command
    cmd = cmd.replace("participant", "group")  # change analysis level from participant to group
    os.system(cmd)

# run fMRIprep
# TODO: allow to run these in parallel if > 16 available cores, with 8 cores per subject
# https://fmriprep.org/en/stable/faq.html#running-subjects-in-parallel
indir = f"{path}/{bids}"  # change to a derivative dataset as required, e.g. "derivatives/NORDIC"
versionNum = "v23.0.1"
version = "latest"
outdir = f"{path}/derivatives/fmriprep-{versionNum}"
os.makedirs(outdir, exist_ok=True)
workdir = f"{path}/derivatives/fmriprep_work"
os.makedirs(workdir, exist_ok=True)
for subject in subjects.participant_id:
    subject = subject[4:]
    if not op.isdir(f"{outdir}/sub-{subject}"):
        cmd = f"docker run --memory=\"22g\" --rm " \
              f"-v {indir}:/data:ro " \
              f"-v {outdir}:/out "\
              f"-v {workdir}:/work " \
              f"-v $FREESURFER_HOME:/fsDir " \
              f"nipreps/fmriprep:{version} " \
              f"--resource-monitor " \
              f"--nprocs 2 " \
              f"--mem-mb 22000 " \
              f"--low-mem " \
              f"--stop-on-first-crash " \
              f"--use-aroma " \
              f"--fs-license-file /fsDir/license.txt " \
              f"--output-spaces fsaverage " \
              f"-w /work " \
              f"/data /out/ participant --participant-label {subject}"  # indir, outdir, analysis level
        os.system(cmd)

#f"--clean-workdir " \

# convert head motion confounds, including temporal derivatives and quadratics from .tsv to .txt
for confounds_file in glob.glob(f"{outdir}/**/*/*desc-confounds_timeseries.tsv", recursive=True):
    outpath = f"{confounds_file[:-4]}.txt"
    if not op.isfile(outpath):
        confounds = pd.read_csv(confounds_file, delimiter='\t')
        motion_confounds = [x for x in confounds.columns if "trans" in x or "rot" in x]
        extracted_confounds = confounds[motion_confounds]
        extracted_confounds.to_csv(outpath, sep="\t", index=False)