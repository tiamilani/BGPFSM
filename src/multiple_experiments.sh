#!/bin/bash
#
# Script to run multiple experiments of the BGP des in this folder
# INPUT:
#	'-n' experiment identifier that limits the sequence of experiments
#	'-j' (default = 1) if setted it will use the parallelize the execution of the experiments
#	The argument given to the j determines how much processes will be executed in parallel

usage () {
	echo "Usage: $0 -n ID [-s SECTION -j PP]"
	echo "	options:"
	echo "	'-n' experiment identifier that limits the sequence of experiments"
	echo "	'-s' (default = simulation) defines which section of the configuration"
	echo "	will be required"
	echo "	'-j' (default = 1) if setted it will use the parallelize the execution of the experiments"
	echo "	The argument given to the j determines how much processes will be executed in parallel"
	exit 1
}

SECTION='simulation'
J=1
nflag=false

while getopts ":n:s:j:" o; do
	case "${o}" in
		n)
			nflag=true
			N=${OPTARG}
			;;
		s)
			SECTION=${OPTARG}
			;;
		j)
			J=${OPTARG}
			;;
		*)
			usage
			;;
	esac
done
shift $((OPTIND-1))

if ! $nflag
then
	usage
fi

if [ -z "${SECTION}" ]
then
	usage
fi

# for i in $(seq 0 ${1})
# do
# 	python3 fsm.py -c json/config.json -s ${2} -r ${i} > out_${i}.log
# 	echo ""
# done | pv -pt -i0.1 -s$((${1} + 1)) -w 80 > /dev/null

seq 0 ${N} | parallel -i% -j ${J} --bar python3 fsm.py -c json/config.json -s ${SECTION} -r % ">" out_%.log

echo "Experiments done"
