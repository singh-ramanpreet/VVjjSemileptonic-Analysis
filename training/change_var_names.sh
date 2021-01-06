#!/bin/bash

training_dir=$1
old_varlist=$2
new_varlist=$3
dry_run=${4:-false}

old_varlist=($(cat $old_varlist))
new_varlist=($(cat $new_varlist))

if (( ${#old_varlist[@]} != ${#new_varlist[@]} ))
then
  echo "new (${#new_varlist[@]}) and old (${#old_varlist[@]}) not same size"
  exit
fi

for ((i=0;i<${#old_varlist[@]};++i))
do
  echo "changing ${old_varlist[i]} ----> ${new_varlist[i]}"
  change_in=($(grep -Irl "${old_varlist[i]}" $training_dir))
  for thisFile in ${change_in[@]}
  do
    if $dry_run
    then
      echo "sed -i \"s/${old_varlist[i]}/${new_varlist[i]}/g\" $thisFile"
    else
      sed -i "s/${old_varlist[i]}/${new_varlist[i]}/g" $thisFile
    fi
  done
done

