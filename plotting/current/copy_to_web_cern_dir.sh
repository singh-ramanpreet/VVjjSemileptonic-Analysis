#!/bin/bash

#copy over with tar/untar on the fly
#args <user@remote> <dir/file 1> <dir/file 2> ... <output dir path>
user_remote=${1}
shift
folders=${@}

inputs=${@:1:$#-1}
output_location=${@:$#}

echo "Running this command ..."
echo "tar zc ${inputs[@]} | ssh ${user_remote} \"tar zx -C ${output_location}\""
tar zc ${inputs[@]} | ssh ${user_remote} "tar zx -C ${output_location}"
exit
