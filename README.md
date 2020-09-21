# WVAnalysis

## Get the code

```bash
git clone git@github.com:singh-ramanpreet/WVAnalysis.git -b rdataframe
cd WVAnalysis
source setup_env/setup.sh --with-install   # for first time setup only
source setup_env/setup.sh   # for re-setup  
```

## Analysis Flow
**`prepare`** (without MVA) ➡ **`training`** ➡ **`prepare`** (with MVA) ➡ **`plotting`**

### Samples List

Samples for 2016, 2017, 2018 are listed in `datasets_<year>.json`, separated in categories by `sample_tag` (`"data_obs"`, `"VBS_EWK"`, ...). Use the script `verify_dataset.py` to make samples are listed properly and root files are accessible.

```bash
./verify_dataset.py --datasets datasets_2018.json --sample-tag all
```

If the file is accessible, it will print contents of file.


### Prepare

This step basically takes any flat input root files and makes new root file with branches renamed and allows to add new branches like MVA score.

Branches listed in file `variables_map.json` will be in output file and in addition to that `sample_tag`, `xs_weight` branches will also be calculated and added, take a look at `prepare/prepare_dataset.py`. Various  weights are also set to `1.0` in this code for real `data`, to make sure there is no error.

#### 1. Run `prepare` step,

```bash
cd prepare
```

The wrapper `run_prepare.sh` is used to run locally or on condor and, with or without MVA inference.

```
# ./run_prepare.sh {local, condor} <year> <output-folder> <sample-tag-string> <sample number> <eos-location> [--without-mva]
# $1: local -> to run interactively
# $2: year -> example, if 2018, it will look for file datasets_2018.json
# $3: output-folder -> it will create output folder in the cwd
# $4: sample-tag-string -> all or {data_obs, VBS_EWK, ... }
# $5: sample-number -> all or {0, 1, 2 .... }, this is a number of sample within category
# $6: eos-location -> location in eos with xrd redirector to copy output folder there. Only used with condor.
```

##### Without MVA

Interactive example

```bash
./run_prepare.sh local 2018 test_run VBS_EWK 5 NONE --without-mva
```

Interactive run full dataset

```bash
./run_prepare.sh local 2018 test_run all all NONE --without-mva
```

Condor submission (adjust the `vars` accordingly)

```bash
./make_tar.sh
condor_submit year=2018 output_dir=for_training/2018_X eos_path=root://cmseos.fnal.gov//store/user/rsingh without_mva=YES prepare_submit.jdl
```

with this condor submission, I will get output in `root://cmseos.fnal.gov//store/user/rsingh/for_training/2018_X` and logs in `condor_logs`.

##### With MVA (after training)

One would first adjust the path to trainings in `download_training.sh`, then run it to get the training weight files.

Interactive, just remove the `--without-mva` from the command line and for condor remove the `without_mva=YES` completely.

