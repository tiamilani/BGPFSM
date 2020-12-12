#!/bin/bash
#
# Script to run multiple different mrai experiments 

# names=("RFD" "noRFD" "RFD_7196_aggressive" "RFD_7196_conservative")
constant_names=("RFD" "noRFD" "RFD_7196_aggressive" "RFD_7196_conservative")
dpc_names=()
names=("RFD_7196_aggressive" "RFD_7196_conservative")
#constant_names=("adaptiveRFD")
#dpc_names=()

for name in ${names[*]}; do
	seq -s ' ' 0 5 120 | ./cisco_clique10_${name}.sh
done

dir_path=$(pwd)/results/

USE_PATH="../../../../"

cd $USE_PATH

for name in ${constant_names[*]}; do
	python3 util/pareto_plots/pareto_efficency.py -f results/rfd_tests/cisco/cisco_clique10_${name}/general_avg.csv -m constant -o ${dir_path}cisco_clique10_${name}-constant.pdf
done

#for name in ${dpc_names[*]}; do
#	python3 util/pareto_plots/pareto_efficency.py -f results/rfd_tests/cisco/cisco_clique10_${name}/general_avg.csv -m dpc -o ${dir_path}cisco_clique10_${name}-dpc.pdf
#done
#
python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_noRFD results/rfd_tests/cisco/cisco_clique10_RFD -o ${dir_path}cisco_clique10_comparison_constant.pdf
python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_RFD results/rfd_tests/cisco/cisco_clique10_RFD_7196_aggressive results/rfd_tests/cisco/cisco_clique10_RFD_7196_conservative -o ${dir_path}cisco_clique10_RFD_comparison_constant.pdf
python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_RFD_7196_aggressive results/rfd_tests/cisco/cisco_clique10_RFD_7196_conservative -o ${dir_path}cisco_clique10_RFD7192_comparison_constant.pdf

for name in ${names[*]}; do
	for i in {1..21}; do
		mkdir ${dir_path}mrai${i}_${name}
		python3 analyzer.py -f results/rfd_tests/cisco/cisco_clique10_${name}/cisco_clique10_${name}_${i}/output_0.csv -n x -o ${dir_path}mrai${i}_${name}/mrai${i}_${name} -s -F --rfd -r
		python3 analyzer.py -f results/rfd_tests/cisco/cisco_clique10_${name}/cisco_clique10_${name}_${i}/output_0.csv -n 5 -o ${dir_path}mrai${i}_${name}/mrai${i}_${name} -s -F --rfd -r
	done
done
