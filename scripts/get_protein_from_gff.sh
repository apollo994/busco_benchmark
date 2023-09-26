#!/bin/bash

#check for input arguments
 
function check_args() {
  if [ $# -ne 3 ]; then
    echo "Error: Exactly 3 arguments required!"
    return 1
  fi
  
  echo "gff: $1"
  echo "reference: $2"
  echo "output dir: $3"
}
 
check_args $1 $2 $3

file_name=$(basename -s .gff3 $1)
file_path=$(echo ${3}${file_name}.protein.fa)


# make result folder if not already exists
mkdir -p $3

echo 'Result file will be saved as: '$file_path


# run agtc singularity 
singularity run /nfs/users/rg/fzanarello/images/agat-1.2.0--pl5321hdfd78af_0.simg agat_sp_extract_sequences.pl -f $2 -g $1 -t cds -p -o $file_path
