#!/bin/bash

echo $(date)
seq -s ' ' 0 1 60 | ./internet_like-constant.sh
seq -s ' ' 0 1 60 | ./internet_like-constant-noIW.sh
seq -s ' ' 0 1 60 | ./internet_like-dpc.sh
seq -s ' ' 0 1 60 | ./internet_like-dpc-noIW.sh
echo $(date)

