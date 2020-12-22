#!/bin/bash
#
# Script to run multiple different mrai experiments 

USE_PATH="../../../../"
CUR_DIR=$(pwd)
RESULTS=results/rfd_tests/cisco/
source ${USE_PATH}env/bin/activate

cd $USE_PATH

mrai=(0 15 30 45 60)
i=1
for MRAI in ${mrai[*]}; do
	DIR=${CUR_DIR}/results_mice_${MRAI}
	mkdir -p ${DIR}

	if [ "${i}" -eq "1" ]; then
		echo "0/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_noRFD.json -o ${DIR}/cisco_1000_noRFD-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_noRFD/cisco_1000_MRAI30_noRFD_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_noRFD/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_noRFD/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_noRFD_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "1/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_2439.json -o ${DIR}/cisco_1000_RFD_2439-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD/cisco_1000_MRAI30_RFD_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "2/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_aggressive.json -o ${DIR}/cisco_1000_RFD_7196_aggressive-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_aggressive/cisco_1000_MRAI30_RFD_7196_aggressive_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD_7196_aggressive/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_aggressive/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_7196_aggressive_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "3/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative.json -o ${DIR}/cisco_1000_RFD_7196_conservative-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -Y
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative/cisco_1000_MRAI30_RFD_7196_conservative_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_7196_conservative_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "4/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.json -o ${DIR}/cisco_1000_RFD_7196_conservative-DPC.pdf -n 1 -s ${i} -j 10 -m dpc2 -l ${MRAI} -M ${MRAI} -Y
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative_DPC/cisco_1000_MRAI30_RFD_7196_conservative_DPC_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative_DPC/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative_DPC/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_7196_conservative_DPC_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "5/5"
	else
		echo "0/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_noRFD.json -o ${DIR}/cisco_1000_noRFD-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -a
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_noRFD/cisco_1000_MRAI30_noRFD_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_noRFD/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_noRFD/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_noRFD_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "1/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_2439.json -o ${DIR}/cisco_1000_RFD_2439-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -a
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD/cisco_1000_MRAI30_RFD_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "2/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_aggressive.json -o ${DIR}/cisco_1000_RFD_7196_aggressive-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -a
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_aggressive/cisco_1000_MRAI30_RFD_7196_aggressive_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD_7196_aggressive/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_aggressive/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_7196_aggressive_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "3/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative.json -o ${DIR}/cisco_1000_RFD_7196_conservative-constant.pdf -n 1 -s ${i} -j 10 -m constant -l ${MRAI} -M ${MRAI} -a
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative/cisco_1000_MRAI30_RFD_7196_conservative_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_7196_conservative_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "4/5"
		./mrais.sh -c json/RFD_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.json -o ${DIR}/cisco_1000_RFD_7196_conservative-DPC.pdf -n 1 -s ${i} -j 10 -m dpc2 -l ${MRAI} -M ${MRAI} -a
		python3 analyzer.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative_DPC/cisco_1000_MRAI30_RFD_7196_conservative_DPC_${i}/output_* -n all -o ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative_DPC/csv_output_${i}/ -s -F
		python3 util/node_convergence_plot.py -f ${RESULTS}cisco_1000_MRAI30_RFD_7196_conservative_DPC/csv_output_${i}/_average_node_convergence.csv -o ${DIR}/cisco_1000_RFD_7196_conservative_DPC_nodeConvergence.pdf -g graphs/rfd_tests/cisco_1000_MRAI30/cisco_1000_RFD_7196_conservative_DPC.graphml
		echo "5/5"
	fi
	
	echo ${MRAI} ${i}
	((i+=1))
done
