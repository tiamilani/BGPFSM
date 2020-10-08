#!/bin/bash
#
# Script to analyze multiple different mrai experiments 

FOLDERS=()
CSV_FILE_NAME="general_study.csv"
OUTPUT_FILE="general_avg.csv"
AGGREGATE_FLAG=false

file_exists(){
	if [ ! -f "$1" ]; then
		echo "$1 does not exist."
		exit 1
	fi
}

study_folder(){
	file=${1}/${CSV_FILE_NAME}
	file_exists $file
	avg_time=$(awk -F '|' '{x+=$3; next} END{print x/NR}' $file)
	avg_msg=$(awk -F '|' '{x+=$4; next} END{print x/NR}' $file)
	echo "$file|$avg_time|$avg_msg" >> $2
}

while getopts ":o:s:a" o; do
	case "${o}" in
		o)
			OUTPUT_FILE=${OPTARG}
			;;
		s)
			CSV_FILE_NAME=${OPTARG}
			;;
		a)
			AGGREGATE_FLAG=true
			;;
		*)
			#TODO write how to use
			exit 1
			;;
	esac
done
shift $((OPTIND-1))

FOLDERS=$@

if $AGGREGATE_FLAG; then
	file_exists ${OUTPUT_FILE}
fi

for folder in $FOLDERS
do
	if ! $AGGREGATE_FLAG; then
		rm -f ${OUTPUT_FILE}
		touch ${OUTPUT_FILE}
		echo "id|avg_time|avg_msg" >> ${OUTPUT_FILE}
		AGGREGATE_FLAG=true
	fi
	study_folder $folder ${OUTPUT_FILE}
done
