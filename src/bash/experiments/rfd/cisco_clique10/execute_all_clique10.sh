#!/bin/bash
#
# Script to run multiple different mrai experiments 

names=("RFD" "noRFD")
constant_names=("RFD" "noRFD" )
dpc_names=()
#names=("adaptiveRFD")
#constant_names=("adaptiveRFD")
#dpc_names=()

for name in ${names[*]}; do
	seq -s ' ' 0 5 240 | ./cisco_clique10_${name}.sh
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

for name in ${names[*]}; do
	for i in {1..21}; do
		mkdir ${dir_path}mrai${i}_${name}
		python3 analyzer.py -f results/rfd_tests/cisco/cisco_clique10_${name}/cisco_clique10_${name}_${i}/output_0.csv -n x -o ${dir_path}mrai${i}_${name}/mrai${i}_${name} -s -F --rfd -r
		python3 analyzer.py -f results/rfd_tests/cisco/cisco_clique10_${name}/cisco_clique10_${name}_${i}/output_0.csv -n 5 -o ${dir_path}mrai${i}_${name}/mrai${i}_${name} -s -F --rfd -r
	done
done
#python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_adaptiveRFD results/rfd_tests/cisco/cisco_clique10_RFD -o ${dir_path}cisco_clique10_comparison_adaptive.pdf
#python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_noRFD results/rfd_tests/cisco/cisco_clique10_RFD results/rfd_tests/cisco/cisco_clique10_adaptiveRFD -o ${dir_path}cisco_clique10_comparison.pdf
#python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_noRFD_DPC results/rfd_tests/cisco/cisco_clique10_RFD_DPC -o ${dir_path}cisco_clique10_comparison_dpc.pdf
#python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_noRFD results/rfd_tests/cisco/cisco_clique10_RFD results/rfd_tests/cisco/cisco_clique10_RFD_DPC results/rfd_tests/cisco/cisco_clique10_noRFD_DPC -o ${dir_path}cisco_clique10_comparison.pdf
#python3 util/pareto_plots/multi_folders.py -f results/rfd_tests/cisco/cisco_clique10_RFD results/rfd_tests/cisco/cisco_clique10_RFD_DPC -o ${dir_path}cisco_clique10_rfdwindows_comparison.pdf

#for name in ${names[*]}; do
#	for i in 1 7 9 11 13; do
#		python3 analyzer.py -f results/rfd_tests/cisco/cisco_clique10_${name}/cisco_clique10_${name}_${i}/output_* -n all -o results/rfd_tests/cisco/cisco_clique10_${name}/csv_output_${i}/ -F
#		python3 util/node_convergence_plot.py -f results/rfd_tests/cisco/cisco_clique10_${name}/csv_output_${i}/_average_node_convergence.csv -o ${dir_path}cisco_clique10_${name}_${i}.pdf -g graphs/rfd_tests/cisco_clique10/cisco_clique10_RFD.graphml
#	done
#done
