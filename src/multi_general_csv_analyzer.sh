#!/bin/bash
#
# Script to analyze multiple different mrai experiments 

FOLDERS=()
CSV_FILE_NAME="general_study.csv"
OUTPUT_FILE="general_avg.csv"
AGGREGATE_FLAG=false
MRAI_VALUE="None"

usage () {
	echo "Usage: $0 [OPTIONS] (set_of_folders_to_study)"
	echo "options:"
	echo "	-o	[value]	output file name (default = general_avg.csv)"
	echo "	-s	[value]	input csv file name, this is the file that the program"
	echo "			will look for in each directory passed (default = general_study.csv)"
	echo "	-m	[value]	MRAI value to register with the experiments (default = None)"
	echo "	-a		Aggregate flag, use it if you want to aggregate the experiments"
	echo "			results with the already present results"
	exit 1
}

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
	echo "$file|${MRAI_VALUE}|$avg_time|$avg_msg" >> $2
}

known_folders(){
	res=$(awk -F '|' ' {print $1} ' $1 | tail -n +2)
	for path in $res;
	do
		IFS='/' read -ra path_array <<< "$path"
		size=$((${#path_array[@]} - 1))
		unset path_array[$size]
		IFS='/' eval 'path="${path_array[*]}"'
		path="${path}"
		echo $path
	done
}

while getopts ":o:s:m:a" o; do
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
		m)
			MRAI_VALUE=${OPTARG}
			;;
		*)
			usage
			;;
	esac
done
shift $((OPTIND-1))

FOLDERS=$@

if $AGGREGATE_FLAG; then
	file_exists ${OUTPUT_FILE}
	known_folders=$(known_folders ${OUTPUT_FILE})
	l1=()
	for elem in $known_folders; do
		l1+=($elem)
	done
	
	l2=()
	for elem in ${FOLDERS}; do
		l2+=($elem)
	done
	
	printf -- '%s\n' "${l1[@]}" | sort > tmp1.txt
	printf -- '%s\n' "${l2[@]}" | sort > tmp2.txt
	
	FOLDERS=$(comm -13 --nocheck-order tmp1.txt tmp2.txt)
	rm -f tmp1.txt tmp2.txt
fi

for folder in $FOLDERS
do
	if ! $AGGREGATE_FLAG; then
		echo "deleting ${OUTPUT_FILE}"
		sleep 5
		rm -if ${OUTPUT_FILE} 2> /dev/null
		touch ${OUTPUT_FILE}
		echo "id|mrai|avg_time|avg_msg" >> ${OUTPUT_FILE}
		AGGREGATE_FLAG=true
	fi
	study_folder $folder ${OUTPUT_FILE}
done
