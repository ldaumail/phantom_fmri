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
bids = 'BIDS_conv/Nifti'
# run mriqc
version = "latest" #downloaded on 04/18/2023 version is 23.1.0rc0
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
indir = ""  # change to a derivative dataset as required, e.g. "derivatives/NORDIC"
version = "latest"
outdir = f"derivatives/fmriprep-{version}"
os.makedirs(outdir, exist_ok=True)
workdir = f"derivatives/fmriprep_work"
os.makedirs(workdir, exist_ok=True)
for subject in subjects:
    if not op.isdir(f"{outdir}/sub-{subject}"):
        cmd = f"docker run --rm " \
              f"--mount type=bind,src={op.abspath(indir)},dst=/data " \
              f"--mount type=bind,src={op.abspath(op.dirname(outdir))},dst=/out " \
              f"--mount type=bind,src={os.environ['SUBJECTS_DIR']},dst=/fs_subjects " \
              f"--mount type=bind,src={op.abspath(workdir)},dst=/work " \
              f"--memory=32g " \
              f"nipreps/fmriprep:{version} " \
              f"--clean-workdir " \
              f"--resource-monitor " \
              f"--nprocs 2 " \
              f"--mem-mb 32000 " \
              f"--fs-license-file /fs_subjects/license.txt " \
              f"--fs-subjects-dir /fs_subjects " \
              f"--output-spaces func " \
              f"-w /work " \
              f"/data /out/{op.basename(outdir)} participant --participant-label {subject}"  # indir, outdir, analysis level
        os.system(cmd)

