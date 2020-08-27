#!/bin/bash

for i in $(seq 0 ${1})
do
	python3 fsm.py -c json/config.json -r ${i} > out.log
	echo ""
done | pv -pt -i0.1 -s$((${1} + 1)) -w 80 > /dev/null

echo "Experiments done"
