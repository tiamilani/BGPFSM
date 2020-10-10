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

get_output_folder(){
	path=$(grep "\"output\"" $1 | awk -F ':' '{print $2}' | awk -F '"' '{print $2}')
	IFS='/' read -ra path_array <<< "$path"
	size=$((${#path_array[@]} - 1))
	unset path_array[$size]
	IFS='/' eval 'path="${path_array[*]}"'
	path="${path}/"
	echo $path
}

get_csv_output_folder(){
	IFS='/' read -ra path_array <<< "$1"
	size=$((${#path_array[@]} - 1))
	unset path_array[$size]
	IFS='/' eval 'path="${path_array[*]}"'
	path="${path}/"
	echo $path	
}

while getopts ":n:l:j:J:c:m:o:u:s:a" o; do
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
		o)
			OUTPUT_PDF=${OPTARG}
			;;
		u)
			U_EXP_PER_PROCESS=${OPTARG}
			;;
		a)
			AGGREGATE_FLAG=true
			;;
		s)
			EXP_START=${OPTARG}
			;;
		*)
			#TODO write how to use
			exit 1
			;;
	esac
done
shift $((OPTIND-1))

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

if ! $AGGREGATE_FLAG; then
	read -p "Do you really want to delete everything is inside $path* [y/n]: " yn
	case $yn in
	    [Yy]* ) rm -r $path*;;
	    [Nn]* ) exit;;
	    * ) echo "Please answer yes or no.";;
	esac
fi

seq ${EXP_START} $exp_per_process $((${N_EXP_LIMIT} - $resto)) | parallel -i% -j ${PARALLEL_EXPERIMENTS} --bar ./multiple_mrais.sh -c ${CONFFILE} -n ${exp_per_process} -l ${MRAI_LIMIT} -s % -j ${PARALLEL_PROCESSES} -m ${MRAI_TYPE} -v

if ! [ "$resto" -eq "0" ]; then
	start=$((${N_EXP_LIMIT} - $resto + 1))
	./multiple_mrais.sh -c ${CONFFILE} -n ${resto} -l ${MRAI_LIMIT} -s $start -j ${PARALLEL_PROCESSES} -m ${MRAI_TYPE} -v
fi

csv_output_folder_name="csv_output_*"
csv_output_folder=$(get_csv_output_folder $des_output)$csv_output_folder_name
general_output=$(get_csv_output_folder $des_output "")
general_output="${general_output%\/}"

if ! $AGGREGATE_FLAG; then
	./multi_general_csv_analyzer.sh -o ${general_output}/${OUTPUT_CSV} $csv_output_folder
else
	./multi_general_csv_analyzer.sh -o ${general_output}/${OUTPUT_CSV} -a $csv_output_folder
fi

python3 util/pareto_efficency.py -f ${general_output}/${OUTPUT_CSV} -o ${OUTPUT_PDF}
