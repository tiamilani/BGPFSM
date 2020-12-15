#!/bin/bash
#
# Script to run multiple different mrai experiments 

USE_PATH="../../../../"
DIR=$(pwd)/results
mkdir -p ${DIR}

source ${USE_PATH}env/bin/activate

cd $USE_PATH

MRAI=30

echo "0/5"
#./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_noRFD.json -o ${DIR}/cisco_1000_noRFD-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
python3 analyzer.py -f results/rfd_tests/cisco/cisco_1000_MRAI30_noRFD/cisco_1000_MRAI30_noRFD_1/output_* -n all -o results/rfd_tests/cisco/cisco_1000_MRAI30_noRFD/csv_output_1/ -s -F
echo "1/5"
#./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_2439.json -o ${DIR}/cisco_1000_RFD_2439-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
python3 analyzer.py -f results/rfd_tests/cisco/cisco_1000_MRAI30_RFD/cisco_1000_MRAI30_RFD_1/output_* -n all -o results/rfd_tests/cisco/cisco_1000_MRAI30_RFD/csv_output_1/ -s -F
echo "2/5"
#./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_aggressive.json -o ${DIR}/cisco_1000_RFD_7196_aggressive-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
python3 analyzer.py -f results/rfd_tests/cisco/cisco_1000_MRAI30_RFD_7196_aggressive/cisco_1000_MRAI30_RFD_7196_aggressive_1/output_* -n all -o results/rfd_tests/cisco/cisco_1000_MRAI30_RFD_7196_aggressive/csv_output_1/ -s -F
echo "3/5"
#./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative.json -o ${DIR}/cisco_1000_RFD_7196_conservative-constant.pdf -n 1 -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
python3 analyzer.py -f results/rfd_tests/cisco/cisco_1000_MRAI30_RFD_7196_conservative/cisco_1000_MRAI30_RFD_7196_conservative_1/output_* -n all -o results/rfd_tests/cisco/cisco_1000_MRAI30_RFD_7196_conservative/csv_output_1/ -s -F
echo "4/5"
#./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.json -o ${DIR}/cisco_1000_RFD_7196_conservative-DPC.pdf -n 1 -j 10 -m dpc2 -l ${MRAI} -M ${MRAI} -Y
python3 analyzer.py -f results/rfd_tests/cisco/cisco_1000_MRAI30_RFD_7196_conservative_DPC/cisco_1000_MRAI30_RFD_7196_conservative_DPC_1/output_* -n all -o results/rfd_tests/cisco/cisco_1000_MRAI30_RFD_7196_conservative_DPC/csv_output_1/ -s -F
echo "5/5"
