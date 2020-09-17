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
Plotter Module
==============

This module is used to plot information about the data retrived by the
analyzer.

"""

import ast
import ipaddress
import re
import pandas as pd
from transition import Transition
from graphviz import Digraph
from route import Route
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from analysis import NodeAnalyzer
from policies import PolicyValue

class Plotter():
    """
    Plotter class
    Main class used for the plotting system.
    Initialize the DataFrame variables
    """


    def __init__(self, node: NodeAnalyzer):
        """__init__.

        """
        self.node = node

    def get_fsm_graphviz(self, dot: Digraph) -> Digraph:
        """get_fsm_graphviz.

        :param dot: dot object of graphviz used to create the graph
        :returns: the dot object modified
        """
        # Insert all states like nodes
        for state_hash, state_str in zip(self.node.states.index.tolist(),
                                         self.node.states[NodeAnalyzer.STATES_COLUMNS[1]]):
            state = ast.literal_eval(state_str) if state_str != "set()" else set()
            state_hash = hash(state_str)
            if len(state) == 0:
                dot.node(str(hash("set()")), label="{}")
            else:
                # Find the best known route and put it in bold in the graph
                best_id = state.pop()
                res = "<{" + str(best_id)
                best_route_row = self.node.routes[self.node.routes.value == best_id]
                network = ipaddress.ip_network(best_route_row.addr.values[0])
                path = ast.literal_eval(best_route_row.path.values[0])
                policy_value = PolicyValue(int(best_route_row.policy_value.values[0]))
                best_route = Route(network, path, best_route_row.nh.values[0], 
                                  policy_value=policy_value)
                while len(state) > 0:
                    new_elem = state.pop()
                    new_route_row = self.node.routes[self.node.routes.value == new_elem]
                    network = ipaddress.ip_network(new_route_row.addr.values[0])
                    path = ast.literal_eval(new_route_row.path.values[0])
                    policy_value = PolicyValue(int(new_route_row.policy_value.values[0]))
                    new_route = Route(network, path, new_route_row.nh.values[0], 
                                      policy_value=policy_value)

                    if new_route < best_route:
                        best_id = new_elem
                        best_route = new_route
                    res += ", " + str(new_elem)
                res += "}>"
                regex = "\\b" + str(best_id) + "\\b"
                res = re.sub(regex, "<B>" + str(best_id) + "</B>", res)
                dot.node(str(state_hash), label=res)
        # Insert every transition like edge
        for input_state, output_state, cause, response in \
                zip(self.node.transitions[NodeAnalyzer.TRANSITIONS_COLUMNS[1]],
                    self.node.transitions[NodeAnalyzer.TRANSITIONS_COLUMNS[2]],
                    self.node.transitions[NodeAnalyzer.TRANSITIONS_COLUMNS[3]],
                    self.node.transitions[NodeAnalyzer.TRANSITIONS_COLUMNS[4]],):
            input_state_hash = hash(input_state) if input_state != "{}" else hash("set()")
            output_state_hash = hash(output_state) if output_state != "{}" else hash("set()")
            inp = str(input_state_hash)
            out = str(output_state_hash)
            # If the output of the transition is empty (No messages sent)
            # use an empty string to represent it
            trans_output = ""
            if response != None:
                trans_output = response
            # Insert the edge
            dot.edge(inp, out, label=" {}:{} ".format(cause, trans_output))
        return dot

    @classmethod
    def __route_to_table_content(cls, id_r: int, route: Route) -> str:
        """__route_to_table_content.
        Given a route it returns the tabular expression of it in graphvizc

        :param id_r: id of the route
        :param route: route to print
        :returns: string format in graphviz of the route
        """
        res = '|{' + str(id_r) + '|' + str(route.addr) + '|' + str(route.nh) +\
               '|' + str(route.path) + '|' + str(route.policy_value.value) + '}'
        return res

    def __message_table(self, table: Digraph) -> Digraph:
        """__message_table.
        Generates the message table

        :param table: table object where to define the nodes
        :returns: table graphviz object modified
        """
        res = r'{{Messages Table}|{id|addr|nh|path|policy_value}'
        for _id, addr, nh, path, policy_value in \
                zip(self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[1]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[2]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[3]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[4]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[5]],):
            network = ipaddress.ip_network(addr)
            path = ast.literal_eval(path)
            policy_value = PolicyValue(int(policy_value))
            route = Route(network, path, nh, policy_value=policy_value)
            res += Plotter.__route_to_table_content(_id, route)
        res += '}'
        table.node('route_table', res)
        return table

    def get_detailed_fsm_graphviz(self, graph: Digraph) -> Digraph:
        """get_detailed_fsm_graphviz.
        This function introduce a lot more details in the graph
        it will introduce also a table for the messages to identify to which
        message corresponds which id on the edges
        It will introduce also a table for the states indicating for each
        id in the state knowledge whcich route is really know

        :param graph: dot object of graphviz to modify
        :return: the dot file modified
        """
        # subgraph of the basic fsm graph
        with graph.subgraph() as dot:
            dot = self.get_fsm_graphviz(dot)

        # Create the message table
        with graph.subgraph(node_attr={'shape': 'record'}) as table:
            table = self.__message_table(table)

        return graph

    def states_stage_boxplot(self, output_file):
        """states_stage_boxplot.

        :param output_file:
        """
        self.states_df['level'] = self.states_df.apply(lambda x: len(x.state.split(',')) \
                if x.state != "set()" else 0, axis=1)
        grouped_states = self.states_df.groupby(by=['level']).sum()
        grouped_states = grouped_states.drop(['counter'], axis=1)
        grouped_states = grouped_states.T
        # print(self.states_df.sort_values(by=['counter'], ascending=False))
        # print(grouped_states)
        grouped_states.boxplot()
        plt.savefig(output_file, format="pdf")
        # print(grouped_states)
        # print(self.states_df)

    def signaling_nmessage_probability(self, output_file): # pylint: disable=too-many-locals
        """signaling_nmessage_probability.

        :param output_file:
        """
        experiments = self.node.signaling.counter.sum()
        advertisement = pd.DataFrame()
        withdraw = pd.DataFrame()
        total = pd.DataFrame()

        advertisement['probability'] = self.node.signaling.counter.values / experiments
        withdraw['probability'] =  advertisement['probability']
        total['probability'] =  advertisement['probability']
        advertisement['messages'] = self.node.signaling.advertisements.values
        withdraw['messages'] = self.node.signaling.withdraws.values
        total['messages'] = self.node.signaling.total_messages.values

        advertisement = advertisement.groupby(by=['messages']).sum().reset_index()
        withdraw = withdraw.groupby(by=['messages']).sum().reset_index()
        total_gr = total.groupby(by=['messages']).sum().reset_index()
        total_size = total.groupby(by=['messages']).size().reset_index()

        fig, ax = plt.subplots() # pylint: disable=invalid-name
        ax2 = ax.twinx()

        legend1 = ax.plot(advertisement['messages'], advertisement['probability'],
                      label="Advertisement messages")
        legend2 = ax.plot(withdraw['messages'], withdraw['probability'],
                      label="Withdraw messages")
        legend3 = ax.plot(total_gr['messages'], total_gr['probability'],
                      label="Total messages")
        legend4 = ax2.plot(total_size['messages'].values, total_size[0].values,
                      'r', label="# possible outputs")
        ax.grid()
        ax2.grid()
        # plt.xticks(np.arange(total.messages.max()+1), np.arange(total.messages.max()+1))
        lns = legend1+legend2+legend3+legend4
        labs = [l.get_label() for l in lns]
        ax2.legend(lns, labs)

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel("# Of messages")
        ax.set_ylabel("Probability [0-1]")
        ax2.set_ylabel("# Of Outputs")

        fig.savefig(output_file, format="pdf")

    def __str__(self): # pylint: disable=no-self-use
        """__str__."""
        res = "States: \n" + str(self.states) + \
              "Transitions: \n" + str(self.transitions) + \
              "Route identifier: \n" + str(self.route_identifier)
        return res
