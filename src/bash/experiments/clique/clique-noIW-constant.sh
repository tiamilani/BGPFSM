#!/bin/bash
#
# Script to run multiple different mrai experiments 

USE_PATH="../../../"
RESULTS_FOLDER="results"
CURRENT_FOLDER=$(pwd)

mkdir -p ${RESULTS_FOLDER}

read foo

source ${USE_PATH}env/bin/activate

cd $USE_PATH

i=1
for elem in $foo; do
	obj=$(echo "$elem" | sed -r 's/,/\./g')
	echo $i
	if [ "${i}" -eq "1" ]; then
		./mrais.sh -c json/clique/clique-noIW.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/pareto-clique-noIW-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -Y
	else
		./mrais.sh -c json/clique/clique-noIW.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/pareto-clique-noIW-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -a
	fi
	i=$(($i + 1))
done
