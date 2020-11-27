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

"""
Analyzer module
===============

This module is used to analyze the results of the Discrete event simulator
All the events are saved in a csv format that will be loaded and used by
the analyzer.

The analyzer have a lot of different options.

`-f` Used to pass a single file or a list of files to the analyzer
`-n` Used to define the node that we want to study
`-o` Defines where the output of the anlyzer will be save, the last part
of this arguments also define the first part of the name of all the output files
`-r` when this option is used the graph file of the FSM of the node will be renderd
`-d` Display the FSM graph at the end of the analysis
`-S` Security option, if enable will avoid the overwrite of other output files
`-t` will show the time required by each operation of the analyzer
`-v` This will activate the verbose mode
`-p` this option can be used to disabel the use of the progress bar
`-pi` The pickle option, if active the pickle fille will be loaded if present
or saved at the end of the analysis if them does not exists
`-s` option to study a signaling experiment
`-F` option to disable the study of the FSM

All this options can be combined in different commands for example:

>>> python3 analyzer.py -f results/fabrikant/output_file -n 1 -o results/fabrikant/out_n1 -s -r -d -pi # pylint: disable=line-too-long

This is a common use of the anlyzer to study a single experiment but is possible to study more
experiments just using the `*` operator

>>> python3 analyzer.py -f results/fabrikant/output_* -n 9 -o results/fabrikant/out_n9 -s -r -d -pi

"""

import argparse
import os.path
import sys
import timeit
import pandas as pd
import pickle
from graphviz import Digraph

sys.path.insert(1, 'util')
from analysis import FileAnalyzer, NodeAnalyzer
from plotter import Plotter, GeneralPlotter, RFDPlotter
from tqdm import tqdm

# Setup command line parameters
parser = argparse.ArgumentParser(usage="python3 analyzer.py [options]",
                        description="Analize an output file from the fsm bgp "
                                  "simulator to produce the state graph of "
                                  "a node.",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="output_0.csv",
                    nargs='*', action="store", help="File to analize")
parser.add_argument("-n", "--node", nargs='+', dest="node",
                    type=str, action="store",
                    help="Node for which the user want to see the FSM")
parser.add_argument("-o", "--output", dest="outputFile", default="output_fsm",
                    action="store", help="Output file containing the FSM representation")
parser.add_argument("-r", "--render", dest="render", default=False,
                    action='store_true', help="Render the graph on a pdf file in \
                    the same output directory of the gv file")
parser.add_argument("-d", "--display", dest="display", default=False,
                    action='store_true', help="Display the rendering produced")
parser.add_argument("-S", "--security", dest="security", default=False,
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
parser.add_argument("-pi", "--pickle", dest="pickle", default=False,
                    action='store_true', help="if possible use saved pickles \
                            from the input folder instead of load again the  \
                            entire dataset, at the end it will save dataframes \
                            in pickle format in the output folder")
parser.add_argument("-s", "--signaling", dest="signaling", default=False,
                    action="store_true", help="If you want to analyze a\
                            signaling experiment use this option to have a csv \
                            of the output signals")
parser.add_argument("-F", "--fsm", dest="fsm", default=True, action="store_false", \
                    help="Use this argument to disable the fsm study of the nodes")
parser.add_argument("--rfd", "--RFD", dest="rfd", default=False, action="store_true", \
                    help="Use this argument to enable the study of the RFD evolution\
                          for the selected nodes")

def load_pickle(general_file_study: pd.DataFrame, input_file: str) -> pd.DataFrame:
    _format = ".pkl"
    if os.path.isfile(input_file + FileAnalyzer.GENERAL_STUDY_FILE_NAME + _format):
        general_file_study = pickle.load(open(input_file + \
                                              FileAnalyzer.GENERAL_STUDY_FILE_NAME + \
                                              _format, "rb"))
    else:
        return None 
    return general_file_study

def save_gfs_df(df: pd.DataFrame, output_file: str, pickling = False) -> None:
    """save_df
    Function used to save all the dataframes controlled by the FileAnalyzer 

    :param output_file: Output file, this is the path and the first part of
    the name that must be used to save the files
    :type output_file: str
    :param pickling: (Default False) defines if it is required to save also
    the dataframes in pickle format
    :rtype: None
    """
    _format = ".csv"
    df.to_csv(output_file + FileAnalyzer.GENERAL_STUDY_FILE_NAME + \
                              _format, '|')

    if pickling:
        _format = ".pkl"
        pickle.dump(df, open(output_file + FileAnalyzer.GENERAL_STUDY_FILE_NAME\
                    + _format, "wb"))


def main(): # pylint: disable=missing-function-docstring,too-many-locals,too-many-statements
    # Parse the arguments
    options = parser.parse_args()

    output_file_path = options.outputFile
    general_file_study = pd.DataFrame(columns=FileAnalyzer.GENERAL_STUDY_COLUMNS)
    general_file_study = general_file_study.set_index(FileAnalyzer.GENERAL_STUDY_COLUMNS[0])

    # Check that the output file does not exists
    if os.path.isfile(output_file_path) and options.security:
        print("output file {} already exists".format(output_file_path))
        sys.exit(1)

    # Obtain variables
    nodes = options.node

    if nodes is not None and nodes[0] == "all":
        first_file = options.inputFile[0]
        df = pd.read_csv(first_file, '|')
        nodes = list(map(str, list(set(df.node.values))))

    node_analyzers = {}
    pickle_loading = options.pickle
    if nodes is not None and len(nodes) > 0:
        for node in nodes:
            node_analyzers[node] = NodeAnalyzer()
            if options.pickle and pickle_loading:
                res = node_analyzers[node].load_pickle(output_file_path + \
                        "_" + str(node) + "_")
                # Something went wrong with the pickle load
                if not res:
                    del node_analyzers[node]
                    pickle_loading = False
                    node_analyzers[node] = NodeAnalyzer()
    # Load general analyzer file pickle
    if options.pickle and pickle_loading:
        general_file_study = load_pickle(general_file_study, 
                                         "/".join(output_file_path.split("/")[:-1]) + "/")
        if general_file_study is None:
            pickle_loading = False

    # If states is not none means that pickles has been loaded and it is not
    # necessary to parse the files
    if not pickle_loading:
        pbar = tqdm(options.inputFile) if options.progress else options.inputFile
        for input_file_path in pbar:
            if options.progress:
                pbar.set_description("Processing {}".format(input_file_path))
            else:
                if options.verbose:
                    print("Processing {}".format(input_file_path))
            # Check that the input file exists
            if not os.path.isfile(input_file_path):
                # doesn't exist
                print("Input file {} not found".format(input_file_path))
                raise FileNotFoundError

            # Get the dataframe rep of the input file
            if options.time:
                starttime = timeit.default_timer()
                init_time= timeit.default_timer()

            file_name = input_file_path.split("/")[-1].split(".")[0]
            file_analyzer = FileAnalyzer(input_file_path, node_analyzers,
                                         general_study_df=general_file_study)

            if options.time:
                print("The init time has been:", timeit.default_timer() - init_time)
            if options.verbose:
                print("Initialization done, csv file loaded")

            if options.signaling:
                if options.time:
                    signaling_time = timeit.default_timer()

                file_analyzer.study_signaling(nodes)

                if options.time:
                    print("The signaling study time has been:", timeit.default_timer() - \
                                                                signaling_time)
                if options.verbose:
                    print("Signaling study done")


            if options.fsm:
                if options.time:
                    fsm_study = timeit.default_timer()

                file_analyzer.study_fsm(nodes)

                if options.time:
                    print("The fsm study time has been:", timeit.default_timer() - \
                                                          fsm_study)
                if options.verbose:
                    print("fsm study done")

            if options.time:
                general_study = timeit.default_timer()

            general_file_study = file_analyzer.general_file_study()
            if nodes is not None and len(nodes) > 0:
                file_analyzer.study_node_convergence(nodes)

            if options.rfd:
                if nodes is not None and len(nodes) > 0:
                    file_analyzer.study_rfd(nodes)

            if options.time:
                print("The general study time has been:", timeit.default_timer() - \
                                                          general_study)
            if options.verbose:
                print("general study done")

            if options.time:
                print("The total study time has been:", timeit.default_timer() - \
                                                        starttime)
            if options.verbose:
                print("Compleate study done")

            del file_analyzer

    save_gfs_df(general_file_study, output_file_path, pickling=options.pickle)

    if options.render:
        gfs_plt = GeneralPlotter(output_file_path + "general_study.csv")
        gfs_plt.ges_boxplot('/'.join(output_file_path.split("/")[:-1]) + "/" \
                                    + "convergence_time_boxplot.pdf", "convergence_time")
        gfs_plt.ges_boxplot('/'.join(output_file_path.split("/")[:-1]) + "/" \
                                + "messages_boxplot.pdf", "total_messages")

        if options.rfd:
            for node in node_analyzers:
                rfd_plt = RFDPlotter(node_analyzers[node].rfd)
                rfd_plt.line_evolution(output_file_path + "_" + str(node) + "_rfd")
    
    # Save results
    average_nodes_convergence = pd.DataFrame(columns=['node', 'avg_conv_time', 
                                    'std_conv_time', 'avg_in_messages', 'std_in_messages'])
    average_nodes_convergence = average_nodes_convergence.set_index('node')
    for node in node_analyzers:
        node_analyzers[node].save_df(output_file_path + "_" + str(node) + "_",
                                     pickling=options.pickle)
        mean = node_analyzers[node].convergence.mean()
        std = node_analyzers[node].convergence.std()
        average_nodes_convergence.loc[node] = [mean[0], std[0], mean[1], std[1]]

    average_nodes_convergence.to_csv(output_file_path + "_average_node_convergence.csv", '|')

    #Generate the graph
    for node in node_analyzers:
        plt = Plotter(node_analyzers[node])
        out_file = output_file_path + "_" + str(node)
        if options.render:
            plt.signaling_nmessage_probability(out_file + "_signaling_nmessage_prob.pdf")
        # plt.states_stage_boxplot(output_file_path + "_states_boxplot.pdf")
        dot = Digraph(comment='Node Graph')
        graph = plt.get_detailed_fsm_graphviz(dot)
        if options.verbose:
            print("Detailed FSM graph produced")

        graph.save(out_file.split('/')[-1] + ".gv",
                   '/'.join(output_file_path.split('/')[:-1]))
        if options.verbose:
            print("Graph saved in the output file")
        if options.render:
            graph.render(out_file.split('/')[-1], format="pdf", cleanup=True,
                         view=options.display)
            if options.verbose:
                print("Graph rendering produced")

if __name__ == "__main__":
    main()
