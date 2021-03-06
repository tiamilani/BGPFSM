#!/bin/bash
#
# Script to run multiple different mrai experiments 

N_EXP=10
CONFFILE="json/config.json"
MRAI_LIMIT=60
EXP_START=1
PARALLEL_PROCESSES=4
PARALLEL_EXPERIMENTS=1
MRAI_TYPE="random"
OUTPUT_CSV="general_avg.csv"
OUTPUT_PDF="output.pdf"
EXP_DIVISOR=10
U_EXP_PER_PROCESS=0
AGGREGATE_FLAG=false
MRAI_MEAN=30.0
YES_FLAG=false

usage () {
	echo "Usage: $0 [OPTIONS]"
	echo "options:"
	echo "	-n	[value]	Number of experiments to run (default = 10)"
	echo "	-l	[value]	limit to apply to the MRAI setter of the graph (default = 60)"
	echo "	-j	[value]	number of parallel runs to execute (default = 4)"
	echo "	-J	[value]	number of parallel experiments to execute (default = 1)"
	echo "	-c	[value]	configuration file to use (default = json/config.json)"
	echo "	-m	[value]	MRAI type to use [random, constant] (default = random)"
	echo "	-M	[value]	MRAI mean to respect (default = 30.0)"
	echo "	-o	[value]	output file name (default = output.pdf)"
	echo "	-u	[value]	Number of experiments for each process, if 0 experiments will"
	echo "			be divided equally between each process, if J = 1 one process"
	echo "			will execute all the experiments (default 0)"
	echo "	-s	[value]	Number of experiment used as start point (default 1)"
	echo "	-a		Aggregate flag, use it if you want to aggregate the experiments"
	echo "			results with the already present results"
	echo "	-Y		Flag to automatically delete the files in the experiment folder"
	echo "			without asking confirmation, use with consciousness"
	exit 1
}

get_output_folder(){
	path=$(grep "\"output\"" $1 | awk -F ':' '{print $2}' | awk -F '"' '{print $2}')
	IFS='/' read -ra path_array <<< "$path"
	size=$((${#path_array[@]} - 1))
	unset path_array[$size]
	IFS='/' eval 'path="${path_array[*]}"'
	path="${path}/"
	echo $path
}

file_exists(){
	if [ ! -f "$1" ]; then
		echo "$1 does not exist."
		exit 1
	fi
}

get_csv_output_folder(){
	IFS='/' read -ra path_array <<< "$1"
	size=$((${#path_array[@]} - 1))
	unset path_array[$size]
	IFS='/' eval 'path="${path_array[*]}"'
	path="${path}/"
	echo $path	
}

while getopts ":n:l:j:J:c:m:M:o:u:s:aY" o; do
	case "${o}" in
		n)
			N_EXP=${OPTARG}
			;;
		l)
			MRAI_LIMIT=${OPTARG}
			;;
		j)
			PARALLEL_PROCESSES=${OPTARG}
			;;
		J)
			PARALLEL_EXPERIMENTS=${OPTARG}
			;;
		c)
			CONFFILE=${OPTARG}
			;;
		m)
			MRAI_TYPE=${OPTARG}
			;;
		M)
			MRAI_MEAN=${OPTARG}
			;;
		o)
			OUTPUT_PDF=${OPTARG}
			;;
		u)
			U_EXP_PER_PROCESS=${OPTARG}
			;;
		a)
			AGGREGATE_FLAG=true
			;;
		Y)
			YES_FLAG=true
			;;
		s)
			EXP_START=${OPTARG}
			;;
		*)
			usage
			;;
	esac
done
shift $((OPTIND-1))

file_exists $CONFFILE

des_output=$(get_output_folder $CONFFILE)

exp_per_process=$(($N_EXP / ${EXP_DIVISOR}))
resto=$(($N_EXP - ($EXP_DIVISOR * $exp_per_process)))
N_EXP_LIMIT=$(($N_EXP + $EXP_START - 1))

if [ ! "${U_EXP_PER_PROCESS}" -eq "0" ]; then
	exp_per_process=${U_EXP_PER_PROCESS}
	EXP_DIVISOR=$(($N_EXP / $exp_per_process))
	resto=$(($N_EXP - ($EXP_DIVISOR * $exp_per_process)))
fi

IFS='/' read -ra path_array <<< "$des_output"
size=$((${#path_array[@]} - 1))
unset path_array[$size]
IFS='/' eval 'path="${path_array[*]}/"'

if $AGGREGATE_FLAG && $YES_FLAG ; then
	echo "Error, you can't have at the same time the aggregate flag and the yes flags active, be aware of what you are doing"
	exit 1
fi

if ! $AGGREGATE_FLAG; then
	if ! $YES_FLAG; then
		read -p "Do you really want to delete everything is inside $path* [y/n]: " yn
		case $yn in
		    [Yy]* ) rm -r $path*;;
		    [Nn]* ) exit;;
		    * ) echo "Please answer yes or no.";;
		esac
	else
		echo "removing everything in ${path}"
		sleep 5
		rm -r $path*
	fi
fi

if [ ! "${exp_per_process}" -eq "0" ]; then
	seq ${EXP_START} $exp_per_process $((${N_EXP_LIMIT} - $resto)) | parallel -i% -j ${PARALLEL_EXPERIMENTS} --bar ./multiple_mrais.sh -c ${CONFFILE} -n ${exp_per_process} -l ${MRAI_LIMIT} -s % -j ${PARALLEL_PROCESSES} -m ${MRAI_TYPE} -M ${MRAI_MEAN} -v
fi

if ! [ "$resto" -eq "0" ]; then
	start=$((${N_EXP_LIMIT} - $resto + 1))
	./multiple_mrais.sh -c ${CONFFILE} -n ${resto} -l ${MRAI_LIMIT} -s $start -j ${PARALLEL_PROCESSES} -m ${MRAI_TYPE} -M ${MRAI_MEAN} -v
fi

csv_output_folder_name="csv_output_*"
csv_output_folder=$(get_csv_output_folder $des_output)$csv_output_folder_name
general_output=$(get_csv_output_folder $des_output "")
general_output="${general_output%\/}"

if ! $AGGREGATE_FLAG; then
	./multi_general_csv_analyzer.sh -o ${general_output}/${OUTPUT_CSV} -m ${MRAI_MEAN} $csv_output_folder
else
	./multi_general_csv_analyzer.sh -o ${general_output}/${OUTPUT_CSV} -m ${MRAI_MEAN} -a $csv_output_folder
fi

python3 util/pareto_plots/pareto_efficency.py -f ${general_output}/${OUTPUT_CSV} -o ${OUTPUT_PDF} -m ${MRAI_TYPE}
