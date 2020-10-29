#!/bin/bash

./mrais.sh -c json/internet_like/constant-30fixed/internet_like.json -o pareto-internet_like-100-constant-fixed30.pdf -n 1 -j 10 -m constant -l 30 -M 30 -Y
./mrais.sh -c json/internet_like/constant-noIW-30fixed/internet_like.json -o pareto-internet_like-100-constant-noIW-fixed30.pdf -n 1 -j 10 -m constant -l 30 -M 30 -Y
./mrais.sh -c json/internet_like/DPC-30fixed/internet_like.json -o pareto-internet_like-100-dpc-fixed30.pdf -n 1 -j 10 -m dpc2 -l 30 -M 30 -Y
./mrais.sh -c json/internet_like/DPC-noIW-30fixed/internet_like.json -o pareto-internet_like-100-dpc-noIW-fixed30.pdf -n 1 -j 10 -m dpc2 -l 30 -M 30 -Y

cp results/internet_like/graph-100-constant-30fixed/csv_output_1/general_study.csv results/internet_like/fixed30-comparison/constant-fixed30.csv
cp results/internet_like/graph-100-constant-noIW-30fixed/csv_output_1/general_study.csv results/internet_like/fixed30-comparison/constant_noIW-fixed30.csv
cp results/internet_like/graph-100-DPC-fixed30/csv_output_1/general_study.csv results/internet_like/fixed30-comparison/DPC-fixed30.csv
cp results/internet_like/graph-100-DPC-noIW-fixed30/csv_output_1/general_study.csv results/internet_like/fixed30-comparison/DPC_noIW-fixed30.csv

python3 util/pareto_plots/box_plotter.py -f results/internet_like/fixed30-comparison/constant-fixed30.csv results/internet_like/fixed30-comparison/DPC-fixed30.csv results/internet_like/fixed30-comparison/constant_noIW-fixed30.csv results/internet_like/fixed30-comparison/DPC_noIW-fixed30.csv -o constant-dpc-100-comparison-30fixed.pdf
