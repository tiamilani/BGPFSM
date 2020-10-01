#!/bin/bash
#
# Script to run all the fabrikant experiments

RESULTS='results'


if [ ! -d "${RESULTS}" ]; then
	mkdir "${RESULTS}"
fi

experiments=(fabrikant-nomrai fabrikant-30fixed fabrikant-desecndent fabrikant-ascendent)

for experiment in ${experiments[*]}
do
	echo "Executing ${experiment}"
	./multiple_experiments.sh -n 539 -c json/config-fabrikant.json -s ${experiment} -j 4
done

echo "All experiments done, analysis..."

nodes=(9)
folders=("results/fabrikant/fabrikant-30fixed" "results/fabrikant/fabrikant-nomrai" "results/fabrikant/fabrikant-desecndent" "results/fabrikant/fabrikant-ascendent")
for folder in ${folders[*]}
do
	echo "Analyzing ${folder}"
	python3 analyzer.py -f ${folder}/output_* -n ${nodes[*]} -o ${folder}/results -s -r -pi
done

echo "Analyzing compleated"
