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


    NoneType = type(None)
    ROUTE_COUNTER = 0
    col_types = {'event_id': int,
                 'event_cause': int,
                 'event': int,
                 'time': float,
                 'node': str,
                 'value': str}

    def __init__(self, inputFile: str, route_df=None, states_routes=None):
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
        self.actualState = set() 
        # Set of transitions
        self.transitions = {}
        
        if isinstance(route_df, self.NoneType): 
            # Routes associated with the id
            self.route_to_id = {}
            # Id associated with the route
            self.id_to_route = {}
        else:
            self.id_to_route = route_df.to_dict('index')
            self.id_to_route = {int(k): Route.fromString(v['value']) for k, v in self.id_to_route.items()}
            self.route_to_id = {str(v): k for k, v in self.id_to_route.items()}

        if isinstance(states_routes, self.NoneType):
            # Routes associated with the states
            self.states_routes = {}
        else:
            self.states_routes = states_routes.to_dict('index')
            self.states_routes = {k: int(v['value']) for k, v in self.states_routes.items()}

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
            return set()
        else:
            return ast.literal_eval(row_value)

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
        # symmetric_difference between sets
        return self.actualState ^ new_state

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
        if len(self.actualState) != len(new_state):
            # Evaluate the difference in the new state vs the previus one
            if abs(len(self.actualState)-len(new_state)) != 1:
                print("something really bad happened")
                exit(3)

            # resulting_elem = self.__evalaute_state_difference(new_state).pop()
            pkt = Packet.fromString(rx_value)
            route = Route.fromString(pkt.content)
            if pkt.packet_type == Packet.UPDATE:  
                if str(route) not in self.states_routes.keys():
                    self.states_routes[str(route)] = self.route_to_id[str(route)]
                new_state = self.actualState.copy()
                new_state.add(self.states_routes[str(route)])    
            elif pkt.packet_type == Packet.WITHDRAW:
                new_state = self.actualState.copy()
                new_state.remove(self.states_routes[str(route)])   
            # print(self.states_routes)
            # print(self.actualState, new_state)

            # Check if the state has already been known
            if str(new_state) not in self.states.keys():
                # Add the state to the states dictionary
                self.states[str(new_state)] = 1
            else:
                # The state is already in the dictionary, increase the counter
                self.states[str(new_state)] += 1

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

    def get_states_as_df(self, states=None) -> pd.DataFrame:
        if states == None:
            states = self.states
        st_df_dict = {'id': map(hash, states.keys()),
                      'state': map(str, states.keys()),
                      'counter': list(states.values())}
        return pd.DataFrame(data=st_df_dict).set_index(['id', 'state'])

    def get_transitions_as_df(self, transitions=None) -> pd.DataFrame:
        if transitions == None:
            transitions = self.transitions
        tr_df_dict = {'id': map(hash, transitions.values()),
                      'start_node': [str(transitions[trans].init_state) for trans in transitions],
                      'end_node': [str(transitions[trans].output_state) for trans in transitions],
                      'cause': [transitions[trans].input for trans in transitions],
                      'response': [str(transitions[trans].output) for trans in transitions],
                      'counter': [transitions[trans].counter for trans in transitions]}
        return pd.DataFrame(data=tr_df_dict).set_index(['id', 'start_node',
                                                        'end_node', 'cause',
                                                        'response'])

    def get_route_df(self) -> pd.DataFrame:
        d = {'id': [str(id) for id in self.id_to_route.keys()],
             'value': [str(val) for val in self.id_to_route.values()]}
        return pd.DataFrame(data=d).set_index('id')

    def get_states_route_df(self) -> pd.DataFrame:
        d = {'state': [str(s) for s in self.states_routes.keys()],
             'value': [str(val) for val in self.states_routes.values()]}
        return pd.DataFrame(data=d).set_index('state')

    @classmethod
    def dump_df(cls, output_file: str, df: pd.DataFrame):
        df.to_csv(output_file, '|')

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
