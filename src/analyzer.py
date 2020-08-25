#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2020 Mattia Milani <mattia.milani@studenti.unitn.it>

from optparse import OptionParser
from graphviz import Digraph
import os.path
import sys
import timeit

sys.path.insert(1, 'util')
from analysis import SingleFileAnalysis

# Setup command line parameters
parser = OptionParser(usage="usage: %prog [options]",
                      description="Analize an output file from the fsm bgp "
                                  "simulator to produce the state graph of "
                                  "a node.")
parser.add_option("-f", "--file", dest="inputFile", default="output_0.csv",
                  action="store", help="File to analize")
parser.add_option("-n", "--node", dest="node", default="0", type="int",
                  action="store", help="Node that the user want to see the FSM")
parser.add_option("-o", "--output", dest="outputFile", default="output_fsm",
                  action="store", help="Output file containing the FSM representation")
parser.add_option("-r", "--render", dest="render", default=False, 
                  action='store_true', help="Render the graph on a pdf file in \
                  the same output directory of the gv file")
parser.add_option("-d", "--display", dest="display", default=False,
                  action='store_true', help="Display the rendering produced")
parser.add_option("-s", "--security", dest="security", default=False,
                  action='store_true', help="Enable the security checks: \
                  disable output file overwrite")

if __name__ == "__main__":
    # Parse the arguments
    (options, args) = parser.parse_args()

    # Obtain variables
    inputFile_path = options.inputFile
    node = options.node
    outputFile_path = options.outputFile

    # Check that the input file exists
    if not os.path.isfile(inputFile_path):
        # doesn't exist
        print("Input file {} not found".format(inputFile_path))
        raise FileNotFoundError
        
    # Check that the output file does not exists
    if os.path.isfile(outputFile_path) and options.security:
        print("output file {} already exists".format(outputFile_path))
        exit(1)

    # Get the dataframe rep of the input file
    starttime = timeit.default_timer()
    init_time= timeit.default_timer()
    sf = SingleFileAnalysis(inputFile_path)
    print("The init time difference is :", timeit.default_timer() - init_time)
    select_node_time = timeit.default_timer()
    sf.selectNode(node)
    print("The select node time difference is :", timeit.default_timer() - select_node_time)
    keep_events_time = timeit.default_timer()
    sf.keep_only_fsm_events()
    print("The keep fsm events time difference is :", timeit.default_timer() - keep_events_time)
    evaluate_time= timeit.default_timer()
    sf.evaluate_fsm()
    print("The evaluate time difference is :", timeit.default_timer() - evaluate_time)
    print("The total time difference is :", timeit.default_timer() - starttime)
    
    #Generate the graph
    dot = Digraph(comment='Node Graph')
    graph = sf.get_detailed_fsm_graphviz(dot)
    graph.save(outputFile_path.split('/')[-1] + ".gv", 
               '/'.join(outputFile_path.split('/')[:-1]))
    if options.render:
        graph.render(outputFile_path.split('/')[-1], format="pdf", cleanup=True, 
                     view=options.display)
