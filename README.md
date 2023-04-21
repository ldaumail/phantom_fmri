Analysis pipeline for fMRI experiment
The scripts and their dependencies are listed in order below
Requires docker:  brew install --cask docker 
    1 implement_heudiconv    
    requires classic DICOM data and heudiconv image
    
    2 finalize_BIDS.py
    requires 1

    3 make_events.py
    requires 2 and matlab logfiles in sourcedata

    4 preprocess.py
    requires 2 and mriqc and fmriprep docker images
    docker pull nipreps/mriqc:latest
    docker pull poldracklab/fmriprep:latest
    !Important: make sure to adjust the memory used by Docker on the Docker app settings manually for MRIQC, as some processes use a lot of memory
    !for instance synthstrip can use 2GB per subject

    5 FEAT_runwise.py
    requires 2-4 and a run-wise FEAT design configured for the first subject

    6 FEAT_subjectwise.py
    requires 2-5 and a subject-wise FEAT design configured for the first subject

    7 RSMs.py
    requires 2-6
    
    8 RSA.py
    requires 2-7
