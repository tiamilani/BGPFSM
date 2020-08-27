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

import pandas as pd
from transition import Transition
from graphviz import Digraph
import ast
from route import Route

class Plotter():

    def __init__(self, states: pd.DataFrame, transitions: pd.DataFrame, 
                   route_id: pd.DataFrame):
        self.states_df = states.reset_index(level=['state'])
        self.states = states.to_dict('index')    
        self.states = {k[1]: int(v['counter']) for k, v in self.states.items()}
        self.transitions_df = transitions
        self.transitions = transitions.to_dict('index')
        self.transitions = {k[0]: Transition(k[1], k[2], k[3], k[4],
                            counter=v['counter']) for k, v in self.transitions.items()}
        self.route_identifier_df = route_id
        self.route_identifier = route_id.to_dict('index')
        self.route_identifier = {int(k): Route.fromString(v['value']) \
                                 for k, v in self.route_identifier.items()}

    def get_fsm_graphviz(self, dot: Digraph) -> Digraph:
        """get_fsm_graphviz.

        :param dot: dot object of graphviz used to create the graph
        :returns: the dot object modified
        """
        # Insert all states like nodes
        for state in self.states.keys():
            state = ast.literal_eval(state) if state != "set()" else set()
            if len(state) == 0:
                dot.node("{}")
            else:
                # Find the best known route and put it in bold in the graph
                knowledge = state.copy()
                best_id = knowledge.pop()
                while len(knowledge) > 0:
                    new_elem = knowledge.pop()
                    if self.route_identifier[new_elem] < self.route_identifier[best_id]:
                        best_id = new_elem
                res = "<" + str(state) + ">"
                res = res.replace(str(best_id), "<B>" + str(best_id) + "</B>")
                dot.node(str(state), label=res) 
        # Insert every transition like edge
        for trans in self.transitions.values():
            inp = trans.init_state if trans.init_state != "set()" else "{}"
            out = trans.output_state if trans.output_state != "set()" else "{}"
            # If the output of the transition is empty (No messages sent)
            # use an empty string to represent it
            trans_output = trans.output if trans.output != "None" else ""
            # Insert the edge
            dot.edge(inp, out, label=" {}:{} ".format(trans.input, trans_output))
        return dot

    def __route_to_table_content(self, id_r: int, route: Route) -> str: 
        """__route_to_table_content.
        Given a route it returns the tabular expression of it in graphvizc

        :param id_r: id of the route
        :param route: route to print
        :returns: string format in graphviz of the route
        """
        res = '|{' + str(id_r) + '|' + str(route.addr) + '|' + str(route.nh) +\
               '|' + str(route.path) + '}' 
        return res

    def __message_table(self, table: Digraph) -> Digraph:
        """__message_table.
        Generates the message table

        :param table: table object where to define the nodes
        :returns: table graphviz object modified
        """
        res = r'{{Messages Table}|{id|addr|nh|path}'
        for _id in self.route_identifier:
            res += self.__route_to_table_content(_id, self.route_identifier[_id])
        res += '}'
        table.node('route_table', res)
        return table

    def __get_single_states_ids_set(self) -> set:
        res = set()
        for state_set in self.states.keys():
            state_set = ast.literal_eval(state_set) if state_set != "set()" else set()
            res |= state_set
        return res

    def __states_table(self, table: Digraph) -> Digraph:
        """__states_table.
        Generates the states table

        :param table: table object where to define the nodes
        :returns: table graphviz object modified
        """
        res = r'{{States Table}|{id|addr|nh|path}'
        for _id in self.__get_single_states_ids_set():
            res += self.__route_to_table_content(_id, self.route_identifier[_id])
        res += '}'
        table.node('states_table', res)
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

        # Create the states knowledge table
        with graph.subgraph(node_attr={'shape': 'record'}) as table:
            table = self.__states_table(table)

        return graph 
    
    def states_stage_probability(self):
        self.states_df['level'] = self.states_df.apply(lambda x: len(x.state.split(',')) \
                if x.state != "set()" else 0, axis=1)
        grouped_states = self.states_df.groupby(by=['level']).sum()
        # print(self.states_df.sort_values(by=['counter'], ascending=False))
        # print(grouped_states)
        # print(self.states_df)

    def __str__(self):
        res = "States: \n" + str(self.states) + \
              "Transitions: \n" + str(self.transitions) + \
              "Route identifier: \n" + str(self.route_identifier)
        return res
