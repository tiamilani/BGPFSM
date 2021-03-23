#!/bin/bash

dir_path=$(pwd)/results/

USE_PATH="../../../"

cd $USE_PATH

python3 util/pareto_plots/multi_folders.py -f results/internet_like/different_levels-1000/* -o ${dir_path}different_levels-1000.pdf
python3 util/pareto_plots/multi_folders.py -f results/internet_like/different_levels-1000/*-l0 results/internet_like/different_levels-1000/*-l4 results/internet_like/different_levels-1000/*-l8 -o ${dir_path}different_levels-1000_hier_1.pdf --tmin 200 --tmax 1200 --mmin 1000 --mmax 100000 -fs 15
python3 util/pareto_plots/multi_folders.py -f results/internet_like/different_levels-1000/*-l1 results/internet_like/different_levels-1000/*-l5 results/internet_like/different_levels-1000/*-l9 -o ${dir_path}different_levels-1000_hier_2.pdf --tmin 200 --tmax 1200 --mmin 1000 --mmax 100000 -fs 15
python3 util/pareto_plots/multi_folders.py -f results/internet_like/different_levels-1000/*-l2 results/internet_like/different_levels-1000/*-l6 results/internet_like/different_levels-1000/*-l10 -o ${dir_path}different_levels-1000_hier_3.pdf --tmin 200 --tmax 1200 --mmin 1000 --mmax 100000 -fs 15
python3 util/pareto_plots/multi_folders.py -f results/internet_like/different_levels-1000/*-l3 results/internet_like/different_levels-1000/*-l7 results/internet_like/different_levels-1000/*-l11 -o ${dir_path}different_levels-1000_hier_4.pdf --tmin 200 --tmax 1200 --mmin 1000 --mmax 100000 -fs 15

# Analyze all results of MRAI mean 30 of all levels

#for name in dpc reverse_dpc; do
#	for i in $(seq 0 11); do
#		python3 analyzer.py -f results/internet_like/different_levels-1000/${name}-l${i}/des_output_4/output_* -n all -o results/internet_like/different_levels-1000/${name}-l${i}/csv_output_4/ -F
#	done
#done
#
#for name in dpc reverse_dpc; do
#	for i in $(seq 0 11); do
#		name2=$(echo "$name" | awk '{print tolower($0)}')
#		diam=0
#		if [ "$i" -gt 2 ]; then
#			diam=1
#		fi
#		if [ "$i" -gt 9 ]; then
#			diam=2
#		fi
#		if [ "$i" == 2 ]; then
#			diam=2
#		fi
#		echo $name $i $diam
#		python3 util/node_convergence_plot.py -f results/internet_like/different_levels-1000/${name}-l${i}/csv_output_4/_average_node_convergence.csv -o ${dir_path}1000-${name}-l${i}_node-conv_MRAI30.pdf -g graphs/internet_like/different_levels-1000/${name2}-l${i}/graph_${i}.graphml -d ${diam} -l 500 -lm 45 > tmp${i}.log
#	done
#done
#
#for name in dpc reverse_dpc; do
#	echo ${name}
#	python3 util/levels_plot.py -f ${dir_path}*-${name}-*.csv -o ${dir_path}${name}_all_levels_comparison.pdf -l 500 -lm 45
#done
