#!/bin/bash
#
# Script to run all the fabrikant experiments

RESULTS='results'

if [ ! -d "${RESULTS}" ]; then
	mkdir "${RESULTS}"
fi

experiments=(fabrikant-nomrai fabrikant-30fixed fabrikant-descendent fabrikant-ascendent fabrikant-nomrai-IW fabrikant-30fixed-IW fabrikant-descendent-IW fabrikant-ascendent-IW)

for experiment in ${experiments[*]}
do
	echo "Executing ${experiment}"
	./multiple_experiments.sh -n 239 -c json/config-fabrikant.json -s ${experiment} -j 4
done

echo "All experiments done, analysis..."

nodes=(9)
folders=("fabrikant-30fixed" "fabrikant-nomrai" "fabrikant-descendent" "fabrikant-ascendent" "fabrikant-30fixed-IW" "fabrikant-nomrai-IW" "fabrikant-descendent-IW" "fabrikant-ascendent-IW")
output_folder="bash/experiments/Fabrikant/results"
for folder in ${folders[*]}
do
	echo "Analyzing ${folder}"
	mkdir -p ${output_folder}/${folder}
	python3 analyzer.py -f results/fabrikant/${folder}/output_* -n ${nodes[*]} -o ${output_folder}/${folder}/ -s -r -pi
done

echo "Analyzing compleated"
