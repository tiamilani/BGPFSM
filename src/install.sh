#!/bin/bash
#
# This script will install all the libraries needed to execute experiments
# and analyze them
# is possible to define a name for the virtualenv different from "env" using
# the argument '-n' and it is also possible to define a python interpreter
# to use in the virtual enviroment using the argument '-p'
#

usage () {
	echo "Usage: $0 [-n ENV_NAME -p Pyton_interpreter_path]"
	echo "options:"
	echo "	'-n' (default = env) Name of the virtual environment that will be"
    echo "		 created"	
	echo "	'-p' (default $which python3) permit to specify a different path"
	echo "		 for a python interpreter different from the one used by the"
	echo "		 system"
	exit 1
}

ENV_NAME='env'
PYTHON_PATH=$(which python3)
RED='\033[0;31m'
NC='\033[0m' # No Color

while getopts ":n:p:" o; do
	case "${o}" in
		n)
			ENV_NAME=${OPTARG}
			;;
		p)
			PYTHON_PATH=${OPTARG}
			;;
		*)
			usage
			;;
	esac
done
shift $((OPTIND-1))

if [ ! -f "${PYTHON_PATH}" ]; then
	echo -e "${RED}Python interpreter not found, be sure to specify a valid path ${NC}"
	exit 1
fi

sudo apt-get install python-virtualenv parallel graphviz

rm -rf "${ENV_NAME}"

mkdir "${ENV_NAME}"
virtualenv --python="${PYTHON_PATH}" "${ENV_NAME}" 
source ${ENV_NAME}/bin/activate
${ENV_NAME}/bin/pip3 install -r requirements.txt 
${ENV_NAME}/bin/pip3 freeze | sed -ne 's/==.*//p' | xargs ${ENV_NAME}/bin/pip3 install -U --
deactivate

echo " "
echo "Virtual environment with all the libraries required created"
echo "Please use 'source ${ENV_NAME}/bin/activate' before using the software"
echo "use 'deactivate' to exit from the virtual environment"
