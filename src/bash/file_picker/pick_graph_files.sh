#!/bin/bash
#
# Script to take the graph files that respect some values in the general csv

# USE_PATH="../../"

# cd $USE_PATH

GRAPH_FOLDER="graphs/internet_like/graph-100-nomean"

OUTPUT_FOLDER="graphs/internet_like/study_graph"

INPUT_GENERAL_FILE=""

TIME_VALUE=20
MSG_VALUE=360

make_folder(){
	if [ ! -d "$1" ]; then
		mkdir -p "$1"
	fi
}

directory_exists(){
	if [ ! -d "$1" ]; then
		echo "$1 does not exist."
		exit 1
	fi
}

file_exists(){
	if [ ! -f "$1" ]; then
		echo "$1 does not exist."
		exit 1
	fi
}

get_files_id(){
	res=$(tail -n +2 $1 | sort -t '|' -g -k 3,4 | awk -F '|' -v time=$2 -v msg=$3 '{if ($3 < time && $4 < msg) { print $1 }}')
	for file in $res; do
		IFS='/' read -ra path_array <<< "$file"
		size=$((${#path_array[@]} - 1))
		unset path_array[$size]
		path=${path_array[ ${#path_array[@]} - 1 ]}
		IFS='_' read -ra path_array <<< "$path"
		path=${path_array[ ${#path_array[@]} - 1 ]}
		echo $path
	done
}

while getopts ":g:o:f:t:m:" o; do
	case "${o}" in
		g)
			GRAPH_FOLDER=${OPTARG}
			;;
		o)
			OUTPUT_FOLDER=${OPTARG}
			;;
		f)
			INPUT_GENERAL_FILE=${OPTARG}
			;;
		t)
			TIME_VALUE=${OPTARG}
			;;
		m)
			MSG_VALUE=${OPTARG}
			;;
		*)
			echo "IMPLEMENT USAGE"
			;;
	esac
done
shift $((OPTIND-1))

directory_exists $GRAPH_FOLDER
make_folder $OUTPUT_FOLDER
file_exists $INPUT_GENERAL_FILE

read -p "Do you really want to delete everything is inside $OUTPUT_FOLDER/* [y/n]: " yn
case $yn in
    [Yy]* ) rm -r $OUTPUT_FOLDER/*;;
    [Nn]* ) exit;;
    * ) echo "Please answer yes or no.";;
esac

ids=$(get_files_id $INPUT_GENERAL_FILE $TIME_VALUE $MSG_VALUE)
for id in $ids; do
	cp $GRAPH_FOLDER/*_$id.graphml $OUTPUT_FOLDER/
done

