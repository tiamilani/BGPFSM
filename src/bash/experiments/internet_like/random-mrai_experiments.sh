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

experiments=100
i=1
for elem in $foo; do
	obj=$(echo "$elem" | sed -r 's/,/\./g')
	echo $i
	if [ "${i}" -eq "1" ]; then
		./mrais.sh -c json/internet_like/random-noMean/internet_like.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/random.pdf -n ${experiments} -s ${i} -j 4 -J 2 -M ${obj} -Y -l 120
	else
		./mrais.sh -c json/internet_like/random-noMean/internet_like.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/random.pdf -n ${experiments} -s ${i} -j 4 -J 2 -M ${obj} -a -l 120
	fi
	i=$(( $i + $experiments))
done

