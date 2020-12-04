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
		./mrais.sh -c json/RFD_tests/cisco_100/cisco_100_DPC.json -o cisco_100_RFD-DPC.pdf -n 1 -s ${i} -j 10 -m dpc2 -l ${obj} -M ${obj} -Y
	else
		./mrais.sh -c json/RFD_tests/cisco_100/cisco_100_DPC.json -o cisco_100_RFD-DPC.pdf -n 1 -s ${i} -j 10 -m dpc2 -l ${obj} -M ${obj} -a
	fi
	i=$(($i + 1))
done

