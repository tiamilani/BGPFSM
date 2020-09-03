#!/bin/bash
#
# This script will install all the libraries needed to execute experiments
# and analyze them
#

sudo apt-get install python-virtualenv parallel graphviz

rm -rf env_test

mkdir env_test
virtualenv --python=$(which python3) env_test
source env_test/bin/activate
env_test/bin/pip3 install -r requirements.txt 
env_test/bin/pip3 freeze |sed -ne 's/==.*//p' |xargs env_test/bin/pip3 install -U --
deactivate

echo " "
echo "Virtual environment with all the libraries required created"
echo "Please use 'source env_test/bin/activate' before using the software"
echo "use 'deactivate' to exit from the virtual environment"
