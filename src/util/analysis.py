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
from events import Events
from packet import Packet
from route import Route
from transition import Transition
import ast
from graphviz import Digraph
import timeit

class SingleFileAnalysis():
    """SingleFileAnalysis.
    Class to manage a single file analysis, it is possible to study the
    output of the fsm discrete event simulator
    """


    ROUTE_COUNTER = 0
    col_types = {'event_id': int,
                 'event_cause': int,
                 'event': int,
                 'time': float,
                 'node': str,
                 'value': str}

    def __init__(self, inputFile):
        """__init__.

        :param inputFile: file with the output to analyze
        """
        self.inputFile = open(inputFile)
        # Open it in pandas like data frame
        self._df = pd.read_csv(self.inputFile, sep='|', index_col="event_cause",
                              dtype=SingleFileAnalysis.col_types)
        # Set of states
        self.states = {}
        # Last state of the node during the evolution
        self.actualState = None
        # Set of transitions
        self.transitions = {}
        # Routes associated with the id
        self.route_to_id = {}
        # Id associated with the route
        self.id_to_route = {}
        # Routes associated with the states
        self.states_routes = {}

    def selectNode(self, node_id: str) -> pd.DataFrame:
        """selectNode.

        :param node_id: id of the node that needs to be isolated
        :type node_id: int
        :rtype: pd.DataFram
        """
        # Mantain in the dataframe only the rows where the node id is equal
        # to the required one
        return self.df[self.df.node == node_id]

    def __evaluate_rib_change(self, row_value: str) -> set:
        """__evaluate_rib_change.
        Evaluate a row that contains a row change, it returns
        the new state, if the set is empty it will return None

        :param row: row to evaluate
        :return: None if the set is empty, the str(set) otherwise
        """
        if row_value == "set()":
            return None
        else:
            return row_value

    def __evaluate_pkt(self, row_value:str) -> str:
        """__evaluate_pkt.
        Evaluate a single pkt row of the DF, it will return the compressed
        string corresponding to the row, A{ID} for an advertisement or
        W{ID} for a withdraw, the id corresponds to the route in the
        route_to_id dictionary

        :param row: row of the dataframe that contains a packet that needs to
        be analyzed
        :return: string with the compressed version of the update
        """
        # Get the packet and the route transmitted
        packet = Packet.fromString(row_value)
        route = Route.fromString(packet.content)
        # If the route is not in the dictionary of routes add it
        if str(route) not in self.route_to_id.keys():
            self.route_to_id[str(route)] = self.ROUTE_COUNTER
            self.id_to_route[str(self.ROUTE_COUNTER)] = route
            self.ROUTE_COUNTER += 1
        # Check the packet type and return the corresponding compressed version
        if packet.packet_type == Packet.UPDATE:
            return "A" + str(self.route_to_id[str(route)])
        elif packet.packet_type == Packet.WITHDRAW:
            return "W" + str(self.route_to_id[str(route)])
        else:
            print("Something very bad happened")
            exit(2)

    def __evaluate_tx(self, row_value: str) -> str:
        """__evaluate_tx.
        This function is used to evaluate a transmitted message and get 
        the comphressed version, for now is equal to __evaluate_rx

        :param row_value: row value to evaluate
        :return: compressed string of the packet
        """
        return self.__evaluate_pkt(row_value)

    def __evaluate_rx(self, row_value: str) -> str:
        """__evaluate_rx.
        This function is used to evaluate a received message and get 
        the comphressed version, for now is equal to __evaluate_tx

        :param row_value: row_value to evaluate
        :return: compressed string of the packet
        """
        return self.__evaluate_pkt(row_value)

    def __evalaute_state_difference(self, new_state: str) -> set:
        """__evalaute_state_difference.
        evaluate the difference between the actual state and a new state

        :param new_state: new state to check
        :return: set() containing the different items
        """
        # Take both states to a set
        acst = ast.literal_eval(self.actualState) if self.actualState is not None \
                else set()
        nwst = ast.literal_eval(new_state) if new_state is not None \
                else set()
        # symmetric_difference between sets
        return acst ^ nwst

    # @profile
    def __evaluate_event_rx(self, rx_event_id: int, rx_value: str):
        """__evaluate_event_rx.

        :param rx_event_id:
        :type rx_event_id: int
        :param rx_value:
        :type rx_value: str
        """
        # Find events caused by the rx
        if rx_event_id not in self.df.index:
            return
        events_in_between = self.df.loc[[rx_event_id], : ]

        # Keep a tmp variable with the state that can have been changed 
        # thanks to this reception
        new_state = self.actualState 

        # Keep a set of transmitted routes, set because we are interested
        # uniquelly in which route has been transmitted and not to who
        transmitted_routes = set()

        # Check each row of the events caused by the reception
        for row_event, row_value in zip(events_in_between['event'], 
                                        events_in_between['value']):
            # If the event is a change in the state, I update the local
            # variable that keeps the state
            if row_event == Events.RIB_CHANGE:
                new_state = self.__evaluate_rib_change(row_value)
            # If the event is a TX i update the corresponding sets
            if row_event == Events.TX:
                transmitted_routes.add(self.__evaluate_tx(row_value))
    
        # Evaluate the reception event
        inp = self.__evaluate_rx(rx_value)

        if len(transmitted_routes) == 0:
            transmitted_routes = None

        # The state has changed thanks to this reception message
        if(self.actualState != new_state):
            # Evaluate the difference in the new state vs the previus one
            resulting_elem = self.__evalaute_state_difference(new_state)
            if len(resulting_elem) != 1:
                print("something really bad happened")
                exit(3)
            resulting_elem = resulting_elem.pop()
            if resulting_elem not in self.states_routes.keys():
                pkt = Packet.fromString(rx_value)
                route = Route.fromString(pkt.content)
                self.states_routes[resulting_elem] = route 
            # Check if the state has already been known
            if new_state not in self.states.keys():
                # Add the state to the states dictionary
                self.states[new_state] = 1
            else:
                # The state is already in the dictionary, increase the counter
                self.states[new_state] += 1

        # Create the new transition
        transition = Transition(self.actualState, new_state,
                                inp,transmitted_routes)
        # Change the state
        self.actualState = new_state
        # Check if the transition has already been known
        if hash(transition) not in self.transitions.keys():
            self.transitions[hash(transition)] = transition
        else:
            # The transition is already in the dictionary, increase the 
            self.transitions[hash(transition)].counter += 1

    def keep_only_fsm_events(self) -> pd.DataFrame:
        """keep_only_fsm_events.
        Function that returns a dataframe with only events that are meaningful
        for a FSM study, RIB_CHANGE, TX and RX

        :return: Datafram with only those events
        :rtype: pd.DataFrame
        """
        return self.df[(self.df.event == Events.RIB_CHANGE) | \
                          (self.df.event == Events.RX) | \
                          (self.df.event == Events.TX)]

    # @profile
    def evaluate_fsm(self):
        """evaluate_fsm.
            Function that evaluate the current dataframe objects to obatin
            states and transitions
        """
        
        tmp_rx = self.df[(self.df.event == Events.RX)]

        # To activate a useful O(LogN) index search the datafram must be sorted
        # This will break the event time order, but we already estrapolated
        # RX events in time order
        self.df.sort_index(inplace=True)

        tmp_rx.apply(lambda row: self.__evaluate_event_rx(row.event_id, 
                                                           row.value), axis=1)
        return (self.states, self.transitions)

    def get_fsm_graphviz(self, dot: Digraph) -> Digraph:
        """get_fsm_graphviz.

        :param dot: dot object of graphviz used to create the graph
        :returns: the dot object modified
        """
        # Insert all states like nodes
        for state in self.states.keys():
            if state == None:
                dot.node("{}")
            else:
                # Find the best known route and put it in bold in the graph
                knowledge = ast.literal_eval(state) 
                best_id = knowledge.pop()
                while len(knowledge) > 0:
                    new_elem = knowledge.pop()
                    if self.states_routes[new_elem] < self.states_routes[best_id]:
                        best_id = new_elem
                res = "<" + str(state) + ">"
                res = res.replace(str(best_id), "<B>" + str(best_id) + "</B>")
                dot.node(str(state), label=res) 
        # Insert every transition like edge
        for trans in self.transitions.values():
            inp = str(trans.init_state) if trans.init_state is not None \
                    else "{}"
            out = str(trans.output_state) if trans.output_state is not None \
                    else "{}"
            # If the output of the transition is empty (No messages sent)
            # use an empty string to represent it
            trans_output = str(trans.output) if trans.output is not None \
                    else ""
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
        for _id in self.id_to_route:
            res += self.__route_to_table_content(_id, self.id_to_route[_id])
        res += '}'
        table.node('route_table', res)
        return table

    def __states_table(self, table: Digraph) -> Digraph:
        """__states_table.
        Generates the states table

        :param table: table object where to define the nodes
        :returns: table graphviz object modified
        """
        res = r'{{States Table}|{id|addr|nh|path}'
        for _id in self.states_routes:
            res += self.__route_to_table_content(_id, self.states_routes[_id])
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

    def get_states_as_df(self, states=None) -> pd.DataFrame:
        if states == None:
            states = self.states
        st_df_dict = {'id': map(hash, states.keys()),
                      'state': map(str, states.keys()),
                      'counter': list(states.values())}
        return pd.DataFrame(data=st_df_dict).set_index('id')

    def get_transitions_as_df(self, transitions=None) -> pd.DataFrame:
        if transitions == None:
            transitions = self.transitions
        tr_df_dict = {'id': map(hash, transitions.values()),
                      'start_node': [transitions[trans].init_state for trans in transitions],
                      'end_node': [transitions[trans].output_state for trans in transitions],
                      'cause': [transitions[trans].input for trans in transitions],
                      'response': [str(transitions[trans].output) for trans in transitions],
                      'counter': [transitions[trans].counter for trans in transitions]}
        return pd.DataFrame(data=tr_df_dict).set_index('id')

    def dump_states(self, output_file: str, states=None): 
        """dump_states.
        Write on a file all the states information in csv format
    
        :param output_file: output file
        :type output_file: str
        :param states: optional param, dataframe of states
        """
        if states == None:
            states = self.get_states_as_df()
        states.to_csv(output_file, sep='|')

    def dump_transitions(self, output_file: str, transitions=None): 
        """dump_states.
        Write on a file all the transitions information in csv format
    
        :param output_file: output file
        :type output_file: str
        :param  transitions: optional param, DataFrame of transitions 
        """
        if transitions == None:
            transitions = self.get_transitions_as_df()
        transitions.to_csv(output_file, sep='|')

    @property
    def df(self):
        """df."""
        return self._df

    @df.setter
    def df(self, v):
        """df.

        :param v:
        """
        self._df = v

    def __delitem__(self):
        """__delitem__."""
        self.inputFile.close()
        del self.df

    def __str__(self):
        """__str__."""
        return str(self.df)
