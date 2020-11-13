#!/bin/bash
#
# Script to run multiple different mrai experiments 

USE_PATH="../../../"

read foo

source ${USE_PATH}env/bin/activate

cd $USE_PATH

i=1
for elem in $foo; do
	obj=$(echo "$elem" | sed -r 's/,/\./g')
	echo $i
	if [ "${i}" -eq "1" ]; then
		./mrais.sh -c json/internet_like/different_destinations/centrality-d1/internet_like.json -o pareto-internet_like-centrality-d1.pdf -n 1 -s ${i} -j 10 -m centrality -l ${obj} -M ${obj} -Y
	else
		./mrais.sh -c json/internet_like/different_destinations/centrality-d1/internet_like.json -o pareto-internet_like-centrality-d1.pdf -n 1 -s ${i} -j 10 -m centrality -l ${obj} -M ${obj} -a
	fi
	i=$(($i + 1))
done
