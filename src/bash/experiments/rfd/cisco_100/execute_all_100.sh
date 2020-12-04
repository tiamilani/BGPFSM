#!/bin/bash
#
# Script to run multiple different mrai experiments 

names=("RFD" "noRFD" "RFD_DPC" "noRFD_DPC")
constant_names=("RFD" "noRFD")
dpc_names=("RFD_DPC" "noRFD_DPC")
#names=("noRFD_DPC")
#constant_names=()
#dpc_names=("noRFD_DPC")

for name in ${names[*]}; do
	seq -s ' ' 0 50 800 | ./cisco_100_${name}.sh
done

dir_path=$(pwd)/results/

USE_PATH="../../../../"

cd $USE_PATH

for name in ${constant_names[*]}; do
	python3 util/pareto_plots/pareto_efficency.py -f results/rfd_tests/cisco/cisco_100_${name}/general_avg.csv -m constant -o ${dir_path}cisco_100_${name}-constant.pdf
done

for name in ${dpc_names[*]}; do
	python3 util/pareto_plots/pareto_efficency.py -f results/rfd_tests/cisco/cisco_100_${name}/general_avg.csv -m dpc -o ${dir_path}cisco_100_${name}-dpc.pdf
done

python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_100_noRFD results/rfd_tests/cisco/cisco_100_RFD -o ${dir_path}cisco_100_comparison_constant.pdf
python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_100_noRFD_DPC results/rfd_tests/cisco/cisco_100_RFD_DPC -o ${dir_path}cisco_100_comparison_dpc.pdf
python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_100_noRFD results/rfd_tests/cisco/cisco_100_RFD results/rfd_tests/cisco/cisco_100_RFD_DPC results/rfd_tests/cisco/cisco_100_noRFD_DPC -o ${dir_path}cisco_100_comparison.pdf
python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_100_RFD results/rfd_tests/cisco/cisco_100_RFD_DPC -o ${dir_path}cisco_100_rfdwindows_comparison.pdf

for name in ${names[*]}; do
	for i in 1 7 9 11 13 15 17; do
		python3 analyzer.py -f results/rfd_tests/cisco/cisco_100_${name}/cisco_100_${name}_${i}/output_* -n all -o results/rfd_tests/cisco/cisco_100_${name}/csv_output_${i}/ -F
		python3 util/node_convergence_plot.py -f results/rfd_tests/cisco/cisco_100_${name}/csv_output_${i}/_average_node_convergence.csv -o ${dir_path}cisco_100_${name}_${i}.pdf -g graphs/rfd_tests/cisco_100/cisco_100_RFD.graphml
	done
done
