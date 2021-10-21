#!/bin/bash

eos_in=${1:-"/eos/uscms/store/group/lnujj/VVjj_aQGC/ntuples/2021-08-18_baseline_sync/"}
year=${2:-"2018"}
eos_out_path=${3:-"root://cmseos.fnal.gov//eos/uscms/store/user/lnujj/VVjj_aQGC/ntuples/2021-08-18_baseline_sync_w_mva"}
is_without_mva=${4:-"No"}

tar_file=condor_logs/${year}_$(basename ${eos_out_path}).tar.gz

list=$(eos root://cmseos.fnal.gov find --xurl -name "*.root" ${eos_in}/${year} | grep -Ev "Run${year}[A-Z]")

output_dir=${year}

$ANALYSIS_BASE/tools/make_tar.sh ${tar_file}

for sample_name in ${list[*]}
do
  condor_submit \
  universe=vanilla \
  executable=run_prepare.sh \
  transfer_input=True \
  transfer_output=True \
  stream_error=True \
  stream_output=True \
  log_filename="condor_logs/${year}_$(basename -s .root ${sample_name})" \
  log="/dev/null" \
  output="\$(log_filename).out" \
  error="\$(log_filename).err" \
  transfer_input_files="run_prepare.sh, ${tar_file}" \
  -append "arguments = $(basename ${tar_file}) ${year} ${output_dir} ${sample_name} ${eos_out_path} ${is_without_mva}" \
  -append "queue 1" \
  /dev/null
done

exit
