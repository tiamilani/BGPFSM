#!/bin/bash
#
# Script to run all the fabrikant experiments

#RESULTS='results'
#
#if [ ! -d "${RESULTS}" ]; then
#	mkdir "${RESULTS}"
#fi
#
#experiments=(fabrikant-nomrai fabrikant-30fixed fabrikant-descendent fabrikant-ascendent fabrikant-nomrai-IW fabrikant-30fixed-IW fabrikant-descendent-IW fabrikant-ascendent-IW)
#
#for experiment in ${experiments[*]}
#do
#	echo "Executing ${experiment}"
#	./multiple_experiments.sh -n 239 -c json/config-fabrikant.json -s ${experiment} -j 4
#done
#
#echo "All experiments done, analysis..."

nodes=(9)
folders=("fabrikant-30fixed" "fabrikant-nomrai" "fabrikant-descendent" "fabrikant-ascendent" "fabrikant-30fixed-IW" "fabrikant-nomrai-IW" "fabrikant-descendent-IW" "fabrikant-ascendent-IW")
signals=("A" "AW" "AWA" "AWAW")
output_folder="bash/experiments/Fabrikant/results"
for signal in ${signals[*]}
do
	for folder in ${folders[*]}
	do
		echo "Analyzing ${signal}/${folder}"
		mkdir -p ${output_folder}/${signal}/${folder}
		python3 analyzer.py -f results/fabrikant/${signal}/${folder}/output_* -n ${nodes[*]} -o ${output_folder}/${signal}/${folder}/ -s -r -pi
	done
done

echo "Analyzing compleated"
