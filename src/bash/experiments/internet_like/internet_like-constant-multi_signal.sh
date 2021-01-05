#!/bin/bash
#
# Script to run multiple different mrai experiments 

# "graph": "graphs/internet_like/graph-100-constant/graph.graphml",

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
		#./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -Y
		./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai_AWA.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant_AWA.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -Y
		./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai_AWAW.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant_AWAW.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -Y
		./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai_AWAWA.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant_AWAWA.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -Y
	else
		#./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -a
		./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai_AWA.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant_AWA.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -a
		./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai_AWAW.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant_AWAW.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -a
		./mrais.sh -c json/internet_like/constant/internet_like_constant_mrai_AWAWA.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant_AWAWA.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -a
	fi
	i=$(($i + 1))
done

echo "Executing all the experiments for 30sec fixed"
#./mrais.sh -c json/internet_like/constant-30fixed/internet_like.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant-30fixed.pdf -n 1  -j 10 -m constant -l 30 -M 30 -Y
./mrais.sh -c json/internet_like/constant-30fixed/internet_like_AWA.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant-30fixed_AWA.pdf -n 1  -j 10 -m constant -l 30 -M 30 -Y
./mrais.sh -c json/internet_like/constant-30fixed/internet_like_AWAW.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant-30fixed_AWAW.pdf -n 1  -j 10 -m constant -l 30 -M 30 -Y
./mrais.sh -c json/internet_like/constant-30fixed/internet_like_AWAWA.json -o ${CURRENT_FOLDER}/${RESULTS_FOLDER}/internet_like-constant-30fixed_AWAWA.pdf -n 1  -j 10 -m constant -l 30 -M 30 -Y

for seq in AWA AWAW AWAWA; do cp results/internet_like/graph-1000-constant-30fixed-${seq}/csv_output_1/general_study.csv results/internet_like/graph-1000-30Second-comparison/30Fixed-${seq}.csv; done
