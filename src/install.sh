#!/bin/bash
#
# This script will install all the libraries needed to execute experiments
# and analyze them
#

sudo apt-get install python-virtualenv prallel

mkdir env_test
virtualenv env_test
source env_test/bin/activate
env_test/bin/pip3 install -r requirements.txt 
deactivate

echo "Virtual environment with all the libraries required created"
echo "Please use 'source env_test/bin/activate' before using the software"
echo "use 'deactivate' to exit from the virtual environment"
