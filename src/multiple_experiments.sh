#!/bin/bash
#
# Script to run multiple experiments of the BGP des in this folder
# INPUT:
#	'-n' experiment identifier that limits the sequence of experiments
#	'-j' (default = 1) if setted it will use the parallelize the execution of the experiments
#	The argument given to the j determines how much processes will be executed in parallel

usage () {
	echo "Usage: $0 -n ID [-s SECTION -j PP]"
	echo "options:"
	echo "	'-n' experiment identifier that limits the sequence of experiments"
	echo "	'-s' (default = simulation) defines which section of the configuration"
	echo "	will be required"
	echo "	'-j' (default = 1) if setted it will use the parallelize the execution of the experiments"
	echo "	The argument given to the j determines how much processes will be executed in parallel"
	echo "	'-o' (default = .) set the output directory for the log files with the"
	echo "	STDOUT of all the process"
	exit 1
}

SECTION='simulation'
J=1
nflag=false
outdir='./'

while getopts ":n:s:j:o:" o; do
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
		o)
			outdir=${OPTARG}
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

if [ ! -d "${outdir}" ]; then
	mkdir "${outdir}"
fi

seq 0 ${N} | parallel -i% -j ${J} --bar python3 fsm.py -c json/config.json -s ${SECTION} -r % ">" ${outdir}out_%.log

echo "Experiments done"
