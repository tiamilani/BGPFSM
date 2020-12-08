#!/bin/bash
#
# Script to run multiple different mrai experiments 

names=("complex_line_cisco")
constant_names=()
dpc_names=()
#names=("adaptiveRFD")
#constant_names=("adaptiveRFD")
#dpc_names=()

for name in ${names[*]}; do
	seq -s ' ' 0 50 1200 | ./${name}.sh
done

dir_path=$(pwd)/results/

USE_PATH="../../../../"

cd $USE_PATH

python3 util/pareto_plots/pareto_efficency.py -f results/rfd_tests/cisco/cisco_complex_line/general_avg.csv -m constant -o ${dir_path}cisco_complex_line-constant.pdf

for i in {1..21}; do
	mkdir ${dir_path}mrai${i}
	python3 analyzer.py -f results/rfd_tests/cisco/cisco_complex_line/cisco_line_${i}/output_0.csv -n 2 -o ${dir_path}mrai${i}/mrai${i} -s -F --rfd -r
	python3 analyzer.py -f results/rfd_tests/cisco/cisco_complex_line/cisco_line_${i}/output_0.csv -n 1 -o ${dir_path}mrai${i}/mrai${i} -s -F --rfd -r
done
