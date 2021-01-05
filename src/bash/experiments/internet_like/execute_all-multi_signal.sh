#!/bin/bash

echo $(date)
seq -s ' ' 0 10 60 | ./internet_like-constant-multi_signal.sh
seq -s ' ' 0 10 60 | ./internet_like-dpc-multi_signal.sh
echo $(date)

cd ../../../

source env/bin/activate

python3 util/pareto_plots/box_plotter.py -f results/internet_like/graph-1000-30Second-comparison/30*-AWA.csv -o bash/experiments/internet_like/results/comparison_AWA.pdf
python3 util/pareto_plots/box_plotter.py -f results/internet_like/graph-1000-30Second-comparison/30*-AWAW.csv -o bash/experiments/internet_like/results/comparison_AWAW.pdf
python3 util/pareto_plots/box_plotter.py -f results/internet_like/graph-1000-30Second-comparison/30*-AWAWA.csv -o bash/experiments/internet_like/results/comparison_AWAWA.pdf
python3 util/pareto_plots/box_plotter.py -f results/internet_like/graph-1000-30Second-comparison/30*-AWA.csv results/internet_like/graph-1000-30Second-comparison/30*-AWAW.csv results/internet_like/graph-1000-30Second-comparison/30*-AWAWA.csv -o bash/experiments/internet_like/results/comparison_allSignals.pdf
