#!/bin/bash
#
# Script to run multiple different mrai experiments 

read foo

i=1
for elem in $foo; do
	obj=$(echo "$elem" | sed -r 's/,/\./g')
	echo $i
	if [ "${i}" -eq "1" ]; then
		./mrais.sh -c json/internet_like/internet_like_constant_mrai.json -o pareto-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -Y
	else
		./mrais.sh -c json/internet_like/internet_like_constant_mrai.json -o pareto-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -a
	fi
	i=$(($i + 1))
done
