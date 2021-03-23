#!/bin/bash                                                                     
                                                                                
dir_path=$(pwd)/results/                                                        
                                                                                
USE_PATH="../../../"                                                            
                                                                                
cd $USE_PATH 

python3 util/pareto_plots/multi_folders.py -f results/internet_like/different-destinations-1000/* -o ${dir_path}different_destinations-1000.pdf

for name in constant DPC reverse_dpc; do
    for i in $(seq 0 9); do
        python3 analyzer.py -f results/internet_like/different-destinations-1000/${name}-d${i}/des_output_4/output_* -n all -o results/internet_like/different-destinations-1000/${name}-d${i}/csv_output_4/ -F
    done
done
