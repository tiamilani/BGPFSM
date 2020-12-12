#!/bin/bash
#
# Script to run multiple different mrai experiments 

USE_PATH="../../../../"

read foo

source ${USE_PATH}env/bin/activate

cd $USE_PATH

i=1
for elem in $foo; do
	obj=$(echo "$elem" | sed -r 's/,/\./g')
	echo $i
	if [ "${i}" -eq "1" ]; then
		./mrais.sh -c json/RFD_tests/cisco_clique10/cisco_clique10_RFD_7196_conservative.json -o cisco_clique10_RFD-7196-conservative-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -Y
	else
		./mrais.sh -c json/RFD_tests/cisco_clique10/cisco_clique10_RFD_7196_conservative.json -o cisco_clique10_RFD-7196-conservative-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${obj} -M ${obj} -a
	fi
	i=$(($i + 1))
done
