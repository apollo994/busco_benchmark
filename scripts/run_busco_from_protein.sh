#!/bin/bash

#check for input arguments
 
function check_args() {
  if [ $# -ne 3 ]; then
    echo "Error: Exactly 3 arguments required!"
    return 1
  fi
  
  echo "protein_sequence: $1"
  echo "ortho_db: $2"
  echo "output dir: $3"
}
 
check_args $1 $2 $3

singularity run /nfs/users/rg/fzanarello/images/busco-v5.5.0_cv1.simg busco -m protein -i $1 -l $2 -o $3

