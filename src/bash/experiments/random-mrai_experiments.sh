#!/bin/bash
#
# Script to run multiple different mrai experiments 

read foo

experiments=100
i=1
for elem in $foo; do
	obj=$(echo "$elem" | sed -r 's/,/\./g')
	echo $i
	if [ "${i}" -eq "1" ]; then
		./mrais.sh -c json/internet_like/random-noMean/internet_like.json -o pareto-random.pdf -n ${experiments} -s ${i} -j 10 -J 2 -M ${obj} -Y -l 240
	else
		./mrais.sh -c json/internet_like/random-noMean/internet_like.json -o pareto-random.pdf -n ${experiments} -s ${i} -j 10 -J 2 -M ${obj} -a -l 240
	fi
	i=$(( $i + $experiments))
done

