#!/bin/bash
#
# Script to run multiple different mrai experiments 

# Folder resources
RESULTS='results'

# File resources
GRAPH_FILE='default.graphml'
CONFFILE="conf.json"

# Environment variables
MRAI_TYPE="random"
MRAI_LIMIT=60
N_EXP=3
EXP_START=1
PARALLEL_PROCESSES=4
VERBOSE=true

make_folder(){
	if [ ! -d "$1" ]; then
		mkdir "$1"
	fi
}

file_exists(){
	if [ ! -f "$1" ]; then
		echo "$1 does not exist."
		exit 1
	fi
}

get_exp_number(){
	python3 fsm.py -c $1 -s $2 -l | awk 'END { print $7 }'
}

get_section(){
	section=$(head --lines=2 $1 | tail --lines=1 | awk '{ print $1 }')
	section="${section%\"}"
	section="${section#\"}"
	echo "${section}"
}

get_output_folder(){
	path=$(grep "\"output\"" $1 | awk '{print $2}')
	path="${path%,}"
	path="${path%\"}"
	path="${path#\"}"
	IFS='/' read -ra path_array <<< "$path"
	size=$((${#path_array[@]} - 1))
	unset path_array[$size]
	IFS='/' eval 'path="${path_array[*]}"'
	path="${path}$2/"
	echo $path
}

get_csv_output_folder(){
	IFS='/' read -ra path_array <<< "$1"
	size=$((${#path_array[@]} - 1))
	unset path_array[$size]
	IFS='/' eval 'path="${path_array[*]}"'
	path="${path}/$2/"
	echo $path	
}

get_file_folder_from_path(){
	IFS='/' read -ra path_array <<< "$1"
	size=$((${#path_array[@]} - 1))
	unset path_array[$size]
	IFS='/' eval 'path="${path_array[*]}"'
	path="${path}/"
	echo $path	
} 

get_graph_file(){
	path=$(grep "\"graph\"" $1 | awk '{print $2}')
	path="${path%,}"
	path="${path%\"}"
	path="${path#\"}"
	echo $path
}

get_mrai_graph(){
	python3 util/graph_generator/mrai_setter.py -f $1 -o $2 -t $3 -m $4 -s $5
} 

change_json_graph_file(){
	sed -i -E "s|\"graph\":.*|\"graph\": \"$2\",|g" $1	
} 

change_json_output_folder(){
	sed -i -E "s|\"output\":.*|\"output\": \"$2\",|g" $1	
} 

do_experiments(){
	./multiple_experiments.sh -n $1 -c $2 -s $3 -j ${PARALLEL_PROCESSES} -S
	python3 analyzer.py -f $4output_* -o $5 -F -p
}

experiment_cicle(){
	if ${VERBOSE}; then
		echo "Experiment: $1/$N_EXP"
	fi

	# Get the output des folder
	new_des_output_folder_suffix="_${1}"
	des_output_folder=$(get_output_folder $2 $new_des_output_folder_suffix)
	# Get the csv output folder
	csv_output_folder_name="csv_output_${1}"
	csv_output_folder=$(get_csv_output_folder $des_output_folder $csv_output_folder_name)
	make_folder $csv_output_folder
	
	# Create the mrai graph
	seed=$1
	mrai_graph_file_name="${MRAI_TYPE}-l${MRAI_LIMIT}-mrai-graph_${1}.graphml"
	graph_folder=$(get_file_folder_from_path $3)
	mrai_graph_path="${graph_folder}$mrai_graph_file_name"
	get_mrai_graph $3 $mrai_graph_path $MRAI_TYPE $MRAI_LIMIT $seed
	
	# Copy the json file and insert the new graph
	new_json_file_name="experiment_${1}.json"
	old_json_folder=$(get_file_folder_from_path $2)
	new_json_file_path="$old_json_folder$new_json_file_name"
	cp $2 $new_json_file_path
	
	change_json_graph_file $new_json_file_path $mrai_graph_path
	des_output_file_name="output_{seed}.csv"
	change_json_output_folder $new_json_file_path "${des_output_folder}${des_output_file_name}"
	
	# Do experiment
	do_experiments $4 $new_json_file_path $5 $des_output_folder $csv_output_folder 
}

while getopts ":n:l:s:j:c:m:v" o; do
	case "${o}" in
		n)
			N_EXP=${OPTARG}
			;;
		l)
			MRAI_LIMIT=${OPTARG}
			;;
		s)
			EXP_START=${OPTARG}
			;;
		j)
			PARALLEL_PROCESSES=${OPTARG}
			;;
		c)
			CONFFILE=${OPTARG}
			;;
		m)
			MRAI_TYPE=${OPTARG}
			;;
		v)
			VERBOSE=false
			;;
		*)
			#TODO write how to use
			exit 1
			;;
	esac
done
shift $((OPTIND-1))

make_folder ${RESULTS}
file_exists "${CONFFILE}"

graph_file_path=$(get_graph_file ${CONFFILE})
file_exists "${graph_file_path}"

json_file_path="${CONFFILE}"

section=$(get_section $json_file_path)
number_of_experiments=$( get_exp_number ${json_file_path} ${section} )
# TODO check if number of experiments is higher than parallel processes

N_EXP=$(($N_EXP + $EXP_START - 1))
for exp in $(seq $EXP_START $N_EXP)
do
 	experiment_cicle $exp $json_file_path $graph_file_path $number_of_experiments $section
done

