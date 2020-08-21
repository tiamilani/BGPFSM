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
from pathlib import Path
from graphviz import Digraph
import sys

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

if __name__ == "__main__":
    # Parse the arguments
    (options, args) = parser.parse_args()

    # Obtain variables
    inputFile_path = options.inputFile
    node = options.node
    outputFile_path = options.outputFile

    inputFile = Path(inputFile_path)
    outputFile = Path(outputFile_path)

    # Check that the input file exists
    try:
        my_abs_path = inputFile.resolve(strict=True)
    except FileNotFoundError:
        # doesn't exist
        print("Input file {} not found".format(inputFile_path))
        raise FileNotFoundError
        
    # Check that the output file does not exists
    try:
        my_abs_path = outputFile.resolve(strict=True)
        print("output file {} already exists".format(outputFile_path))
        exit(1)
    except FileNotFoundError:
        pass

    # Get the dataframe rep of the input file
    sf = SingleFileAnalysis(inputFile_path)
    sf.selectNode(node)
    sf.translation()
    sf.evaluate_fsm()
    dot = Digraph(comment='Node Graph')
    # graph = sf.get_fsm_graphviz(dot)
    graph = sf.get_detailed_fsm_graphviz(dot)
    graph.render(outputFile_path, format="pdf", view=True)

    # Check that the required node is inside the input file
