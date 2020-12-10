#!/bin/bash
#
# Script to run multiple different mrai experiments 

USE_PATH="../../../../"

source ${USE_PATH}env/bin/activate

cd $USE_PATH

MRAI=30

./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_noRFD.json -o cisco_1000_noRFD-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_2439.json -o cisco_1000_RFD_2439-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_aggressive.json -o cisco_1000_RFD_7196_aggressive-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative.json -o cisco_1000_RFD_7196_conservative-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.json -o cisco_1000_RFD_7196_conservative-DPC.pdf -n 1 -j 10 -m dpc2 -l ${MRAI} -M ${MRAI} -Y
