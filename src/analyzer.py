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

import argparse 
from graphviz import Digraph
import os.path
import sys
import timeit
from glob import glob
import pandas as pd

sys.path.insert(1, 'util')
from analysis import SingleFileAnalysis
from plotter import Plotter
from tqdm import tqdm

# Setup command line parameters
parser = argparse.ArgumentParser(usage="python2 analyzer.py [options]",
                        description="Analize an output file from the fsm bgp "
                                  "simulator to produce the state graph of "
                                  "a node.",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="output_0.csv",
                    nargs='*', action="store", help="File to analize")
parser.add_argument("-n", "--node", dest="node", default=0, type=str,
                    action="store", help="Node that the user want to see the FSM")
parser.add_argument("-o", "--output", dest="outputFile", default="output_fsm",
                    action="store", help="Output file containing the FSM representation")
parser.add_argument("-r", "--render", dest="render", default=False, 
                    action='store_true', help="Render the graph on a pdf file in \
                    the same output directory of the gv file")
parser.add_argument("-d", "--display", dest="display", default=False,
                    action='store_true', help="Display the rendering produced")
parser.add_argument("-s", "--security", dest="security", default=False,
                    action='store_true', help="Enable the security checks: \
                    disable output file overwrite")
parser.add_argument("-t", "--time", dest="time", default=False,
                    action='store_true', help="Shows the timing that the program \
                          took to analyze the file")
parser.add_argument("-v", "--verbose", dest="verbose", default=False,
                    action='store_true', help="Makes the program more verbose \
                          on standard output ")
parser.add_argument("-p", "--progress", dest="progress", default=True,
                    action='store_false', help="Display a progressbar on stdout")

if __name__ == "__main__":
    # Parse the arguments
    options = parser.parse_args()

    # Obtain variables
    node = options.node
    outputFile_path = options.outputFile

    # Check that the output file does not exists
    if os.path.isfile(outputFile_path) and options.security:
        print("output file {} already exists".format(outputFile_path))
        exit(1)
    
    NoneType = type(None)
    states_df = None
    transitions_df = None
    route_to_id = None
    states_route = None
    i = 0

    pbar = tqdm(options.inputFile) if options.progress else options.inputFile
    for inputFile_path in pbar:
        if options.progress:
            pbar.set_description("Processing {}".format(inputFile_path))
        else:
            print("Processing {}".format(inputFile_path))
        # Check that the input file exists
        if not os.path.isfile(inputFile_path):
            # doesn't exist
            print("Input file {} not found".format(inputFile_path))
            raise FileNotFoundError
    
        # Get the dataframe rep of the input file
        if options.time:
            starttime = timeit.default_timer()
            init_time= timeit.default_timer()

        sf = SingleFileAnalysis(inputFile_path, route_df=route_to_id,
                                states_routes=states_route)

        if options.time:
            print("The init time has been:", timeit.default_timer() - init_time)
        if options.verbose:
            print("Initialization done, csv file loaded")

        if options.time:
            select_node_time = timeit.default_timer()

        # Node selection
        sf.df = sf.selectNode(node)

        if options.time:
            print("The select node time has been:", timeit.default_timer() - select_node_time)
        if options.verbose:
            print("Node selection done, dataframe updated")

        if options.time:
            keep_events_time = timeit.default_timer()

        # Keep only fsm reliable events
        sf.df = sf.keep_only_fsm_events()

        if options.time:
            print("The keep fsm events time has been :", timeit.default_timer() - keep_events_time)
        if options.verbose:
            print("Node fsm reliable events parsing done, dataframe updated")

        if options.time:
            evaluate_time= timeit.default_timer()

        sf.evaluate_fsm()
        
        if options.time:
            print("The evaluate time has been:", timeit.default_timer() - evaluate_time)
            print("The total time required by the evaluation has been:", timeit.default_timer() - starttime)
        if options.verbose:
            print("Evaluation of fsm components done")
        
        sr_df = sf.get_states_as_df()
        if isinstance(states_df, NoneType):
            states_df = sr_df
            states_df[str(i)] = sr_df['counter']
        else:
            sr_df[str(i)] = sr_df['counter']
            sr_df = sr_df.drop(['counter'], axis=1)
            sr_df_states = sr_df.drop([str(i)], axis=1)
            states_df = pd.concat([states_df, sr_df_states])
            states_df = states_df[~states_df.index.duplicated(keep='first')]
            states_df = states_df.fillna(0)
            sr_df = sr_df.drop(['state'], axis=1)
            states_df = pd.concat([states_df, sr_df], axis=1)
            states_df = states_df.fillna(0)
            states_df['counter'] = states_df['counter'] + states_df[str(i)]

        states_df['counter'] = states_df['counter'].astype(int)
        for j in range(0,i):
            states_df[str(j)] = states_df[str(j)].astype(int)

        tr_df = sf.get_transitions_as_df()
        if isinstance(transitions_df, NoneType):
            transitions_df = tr_df
            transitions_df[str(i)] = tr_df['counter']
        else:
            tr_df[str(i)] = tr_df['counter']
            tr_df = tr_df.drop(['counter'], axis=1)
            tr_df_states = tr_df.drop([str(i)], axis=1)
            transitions_df = pd.concat([transitions_df, tr_df_states])
            transitions_df = transitions_df[~transitions_df.index.duplicated(keep='first')]
            transitions_df = transitions_df.fillna(0)
            tr_df = tr_df.drop(['start_node', 'end_node', 'cause', 'response'], axis=1)
            transitions_df = pd.concat([transitions_df, tr_df], axis=1)
            transitions_df = transitions_df.fillna(0)
            transitions_df['counter'] = transitions_df['counter'] + transitions_df[str(i)]
        print(transitions_df)
        for j in range(0,i):
            transitions_df[str(j)] = transitions_df[str(j)].astype(int)
        transitions_df['counter'] = transitions_df['counter'].astype(int)

        route_to_id = sf.get_route_df()
        states_route = sf.get_states_route_df()

        del sf
        i += 1

    # Save results
    SingleFileAnalysis.dump_df(outputFile_path + "_states.csv", states_df)
    SingleFileAnalysis.dump_df(outputFile_path + "_transitions.csv", transitions_df)
    SingleFileAnalysis.dump_df(outputFile_path + "_route_id.csv", route_to_id)
    SingleFileAnalysis.dump_df(outputFile_path + "_states_id.csv", states_route)
    
    #Generate the graph
    plt = Plotter(states_df, transitions_df, route_to_id)
    plt.states_stage_boxplot(outputFile_path + "_states_boxplot.pdf")
    dot = Digraph(comment='Node Graph')
    graph = plt.get_detailed_fsm_graphviz(dot)
    if options.verbose:
        print("Detailed FSM graph produced")

    graph.save(outputFile_path.split('/')[-1] + ".gv", 
               '/'.join(outputFile_path.split('/')[:-1]))
    if options.verbose:
        print("Graph saved in the output file")
    if options.render:
        graph.render(outputFile_path.split('/')[-1], format="pdf", cleanup=True, 
                     view=options.display)
        if options.verbose:
            print("Graph rendering produced")
