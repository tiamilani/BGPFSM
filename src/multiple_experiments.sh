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
CONFFILE='json/config.json'
J=1
nflag=false
oflag=false
silent_flag=false
outdir='/dev/null'

while getopts ":n:c:s:j:o:S" o; do
	case "${o}" in
		n)
			nflag=true
			N=${OPTARG}
			;;
		c)
			CONFFILE=${OPTARG}
			;;
		s)
			SECTION=${OPTARG}
			;;
		j)
			J=${OPTARG}
			;;
		o)
			outdir=${OPTARG}
			oflag=true
			;;
		S)
			silent_flag=true
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

if $oflag; then
	echo "oflag true"
	if [ ! -d "${outdir}" ]; then
		mkdir "${outdir}"
	fi
fi

if $oflag
then 
	if $silent_flag
	then
		seq 0 ${N} | parallel -i% -j ${J} python3 fsm.py -c ${CONFFILE} -s ${SECTION} -r % ">" ${outdir}out_%.log
	else
		seq 0 ${N} | parallel -i% -j ${J} --bar python3 fsm.py -c ${CONFFILE} -s ${SECTION} -r % ">" ${outdir}out_%.log
	fi
else
	if $silent_flag
	then
		seq 0 ${N} | parallel -i% -j ${J} python3 fsm.py -c ${CONFFILE} -s ${SECTION} -r % ">" ${outdir}
	else
		seq 0 ${N} | parallel -i% -j ${J} --bar python3 fsm.py -c ${CONFFILE} -s ${SECTION} -r % ">" ${outdir}
	fi
fi

if ! $silent_flag
then
	echo "Experiments done"
fi
