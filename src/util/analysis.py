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
Analisis module
===============

Used by the anlyzer to apply different filters and transformations
to the input data

"""

import pandas as pd
from collections import OrderedDict
from events import Events
from packet import Packet
from route import Route
from transition import Transition
import ast
from graphviz import Digraph
import timeit
from policies import PolicyValue
import pickle
from typing import List, Dict, Optional
import sys
import os

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
    TEST=0

    def __init__(self, inputFile: str, route_df=None, states_routes=None):
        """__init__.

        :param inputFile: file with the output to analyze
        """
        self.input_file = open(inputFile)
        # Open it in pandas like data frame
        self._df = pd.read_csv(self.input_file, sep='|', index_col="event_cause",
                              dtype=SingleFileAnalysis.col_types)
        # Set of states
        self.states = {}
        # Last state of the node during the evolution
        self.actual_state = set()
        self.experiment_actual_state = set()
        # Set of transitions
        self.transitions = {}

        if isinstance(route_df, self.NoneType):
            # Routes associated with the id
            self.route_to_id = {}
            # Id associated with the route
            self.id_to_route = {}
        else:
            self.id_to_route = route_df.to_dict('index')
            self.id_to_route = {int(k): Route.fromString(v['value']) for k, v \
                    in self.id_to_route.items()}
            self.route_to_id = {str(v): k for k, v in self.id_to_route.items()}
            SingleFileAnalysis.ROUTE_COUNTER = max(self.route_to_id.values()) + 1

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
        tmp_pv = PolicyValue(0)
        route.policy_value = tmp_pv
        # If the route is not in the dictionary of routes add it
        if str(route) not in self.route_to_id.keys():
            self.route_to_id[str(route)] = SingleFileAnalysis.ROUTE_COUNTER
            self.id_to_route[str(SingleFileAnalysis.ROUTE_COUNTER)] = route
            SingleFileAnalysis.ROUTE_COUNTER += 1
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
        return self.actual_state ^ new_state

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
        new_state = self.actual_state

        # Keep a set of transmitted routes, set because we are interested
        # uniquelly in which route has been transmitted and not to who
        transmitted_routes = []

        """print(rx_value)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        print(events_in_between)"""

        # Check each row of the events caused by the reception
        for row_event, row_value in zip(events_in_between['event'],
                                        events_in_between['value']):
            # If the event is a change in the state, I update the local
            # variable that keeps the state
            if row_event == Events.RIB_CHANGE:
                new_state = self.__evaluate_rib_change(row_value)
            # If the event is a TX i update the corresponding sets
            if row_event == Events.TX:
                elem = self.__evaluate_tx(row_value)
                if elem not in transmitted_routes:
                    transmitted_routes.append(elem)

        # Evaluate the reception event
        inp = self.__evaluate_rx(rx_value)

        if len(transmitted_routes) == 0:
            transmitted_routes = None
        else:
            transmitted_routes = sorted(transmitted_routes)

        # The state has changed thanks to this reception message
        if len(self.experiment_actual_state ^ new_state) > 0:
            # print(self.actual_state, self.experiment_actual_state, new_state)
            # Evaluate the differenVce in the new state vs the previus one
            if abs(len(self.experiment_actual_state)-len(new_state)) > 1:
                print(str(rx_event_id), str(rx_value))
                print(str(self.actual_state), str(new_state))
                print("something really bad happened")
                exit(3)

            # resulting_elem = self.__evalaute_state_difference(new_state).pop()
            pkt = Packet.fromString(rx_value)
            route = Route.fromString(pkt.content)
            route.policy_value = PolicyValue(0)
            if abs(len(self.experiment_actual_state)-len(new_state)) == 1:
                if pkt.packet_type == Packet.UPDATE:
                    if str(route) not in self.states_routes.keys():
                        self.states_routes[str(route)] = self.route_to_id[str(route)]
                    self.experiment_actual_state = new_state.copy()
                    new_state = self.actual_state.copy()
                    new_state.add(self.states_routes[str(route)])
                elif pkt.packet_type == Packet.WITHDRAW:
                    self.experiment_actual_state = new_state.copy()
                    new_state = self.actual_state.copy()
                    new_state.remove(self.states_routes[str(route)])
            else:
                self.experiment_actual_state = new_state.copy()
                new_state = self.actual_state.copy()
                for elem in self.route_to_id:
                    old_rt = Route.fromString(elem)
                    if old_rt.nh == route.nh:
                        if self.route_to_id[elem] in new_state:
                            new_state.remove(self.route_to_id[elem])
                if str(route) not in self.states_routes.keys():
                    self.states_routes[str(route)] = self.route_to_id[str(route)]
                new_state.add(self.states_routes[str(route)])
                # print(self.states_routes)
                # print(self.actual_state, new_state)

            # Check if the state has already been known
            if str(new_state) not in self.states.keys():
                # Add the state to the states dictionary
                self.states[str(new_state)] = 1
            else:
                # The state is already in the dictionary, increase the counter
                self.states[str(new_state)] += 1
            # print(new_state)

        # Create the new transition
        transition = Transition(self.actual_state, new_state,
                                inp,transmitted_routes)

        # Change the state
        self.actual_state = new_state
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
        # This will break the event time order, but we already extrapolated
        # RX events in time order
        self.df.sort_index(inplace=True)

        tmp_rx.apply(lambda row: self.__evaluate_event_rx(row.event_id,
                                                           row.value), axis=1)
        return (self.states, self.transitions)

    def get_out_signal(self, values):
        values = values.apply(self.__evaluate_tx)
        return ''.join(list(OrderedDict.fromkeys(values.values)))

    # @profile
    def evaluate_signaling(self, order_by_time=False):
        tmp_df = self.df.sort_values(by=['time']) if order_by_time else self.df
        tmp_df = tmp_df[tmp_df.event == Events.TX][['value']]
        tmp_v = tmp_df.groupby(by=["event_cause"], sort=False).value.agg(self.get_out_signal)
        return ''.join(tmp_v.values)

    def get_states_as_df(self, states=None) -> pd.DataFrame:
        if states == None:
            states = self.states
        st_df_dict = {'id': map(hash, states.keys()),
                      'state': map(str, states.keys()),
                      'counter': list(states.values())}
        return pd.DataFrame(data=st_df_dict).set_index(['id'])

    def get_transitions_as_df(self, transitions=None) -> pd.DataFrame:
        if transitions == None:
            transitions = self.transitions
        tr_df_dict = {'id': map(hash, transitions.values()),
                      'start_node': [str(transitions[trans].init_state) for trans in transitions],
                      'end_node': [str(transitions[trans].output_state) for trans in transitions],
                      'cause': [transitions[trans].input for trans in transitions],
                      'response': [str(transitions[trans].output) for trans in transitions],
                      'counter': [transitions[trans].counter for trans in transitions]}
        return pd.DataFrame(data=tr_df_dict).set_index(['id'])

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
        self.input_file.close()
        del self.df

    def __str__(self):
        """__str__."""
        return str(self.df)

class SignalHandler():
    """
    SignalHandler
    =============

    Class used to handle signal objects, get messages, count messages ecc.
    """
    def __init__(self, signal: str):
        """__init__.
        Initialize method for a single signal handler

        :param signal: starting signal, can be empty
        :type signal: str
        """
        self.__signal = signal

    def len_advert(self) -> int:
        """len_advert.
        Return the number of advertisement messages in the signal

        :rtype: int
        """
        return self.signal.count('A')

    def len_withdraw(self) -> int:
        """len_withdraw.
        Get the number of withdraw messages in the signal

        :rtype: int
        """
        return self.signal.count('W')

    def len(self) -> int:
        """len.
        Get the complessive number of messages in the signal

        :rtype: int
        """
        return self.len_advert() + self.len_withdraw()

    @property
    def signal(self) -> str:
        """signal.
        Get the actual signal

        :rtype: str
        """
        return self.__signal

    @signal.setter
    def signal(self, value: str) -> None:
        """signal.
        Set the current signal

        :param value: Signal to insert
        :type value: str
        :rtype: None
        """
        self.__signal = value

    def __str__(self) -> str:
        """__str__.
        Return the signal in a human readable format

        :rtype: str
        """
        return self.signal

class NodeAnalyzer():
    """
    NodeAnalyzer
    ============
    Class used to analyze a single node in a given file.
    Successive analysis will incrementaly improve the dataframes in the object
    """

    # Columns for the states dataframe
    STATES_COLUMNS = ['id', 'state', 'counter']
    TRANSITIONS_COLUMNS= ['id', 'start_node', 'end_node', 'cause', 'response',
                          'counter']
    ROUTES_COLUMNS = ['id', 'value', 'addr', 'nh', 'path', 'policy_value']
    SIGNAL_COLUMNS = ['id', 'signal', 'advertisements', 'withdraws',
                      'total_messages', 'counter']

    # File names for load and save
    STATES_FILE_NAME = "_states"
    TRANSITIONS_FILE_NAME = "_transitions"
    ROUTES_FILE_NAME = "_routes"
    SIGNAL_FILE_NAME = "_signal"

    # Evaluation dataframe columns expected
    # NEVER CHANGE THE POSITION OF THE ELEMENTS ALREADY IN THE LIST
    EVALUATION_COLUMNS = ['event_id', 'event_cause', 'event', 'time', 'node',
                          'value']

    def __init__(self):
        """__init__
        Function that instantiate the empty dataframes controlled by the node
        """
        self.states = pd.DataFrame(columns=NodeAnalyzer.STATES_COLUMNS)
        self.states = self.states.set_index(NodeAnalyzer.STATES_COLUMNS[0])
        self.transitions = pd.DataFrame(columns=NodeAnalyzer.TRANSITIONS_COLUMNS)
        self.transitions = self.transitions.set_index(NodeAnalyzer.TRANSITIONS_COLUMNS[0])
        self.routes = pd.DataFrame(columns=NodeAnalyzer.ROUTES_COLUMNS)
        self.routes = self.routes.set_index(NodeAnalyzer.ROUTES_COLUMNS[0])
        self.signaling = pd.DataFrame(columns=NodeAnalyzer.SIGNAL_COLUMNS)
        self.signaling = self.signaling.set_index(NodeAnalyzer.SIGNAL_COLUMNS[0])
        self.actual_state = set() 
        self.experiment_actual_state = set()
        self.route_counter = 0

    def load_pickle(self, input_file: str) -> bool:
        _format = ".pkl"
        if os.path.isfile(input_file + NodeAnalyzer.STATES_FILE_NAME + _format):
            self.states = pickle.load(open(input_file + NodeAnalyzer.STATES_FILE_NAME \
                                      + _format, "rb"))
        else:
            return False
        if os.path.isfile(input_file + NodeAnalyzer.TRANSITIONS_FILE_NAME + _format):
            self.transitions = pickle.load(open(input_file + NodeAnalyzer.TRANSITIONS_FILE_NAME \
                                      + _format, "rb"))
        else:
            return False
        if os.path.isfile(input_file + NodeAnalyzer.ROUTES_FILE_NAME + _format):
            self.routes = pickle.load(open(input_file + NodeAnalyzer.ROUTES_FILE_NAME \
                                      + _format, "rb"))
        else:
            return False
        if os.path.isfile(input_file + NodeAnalyzer.SIGNAL_FILE_NAME + _format):
            self.signaling = pickle.load(open(input_file + NodeAnalyzer.SIGNAL_FILE_NAME \
                                      + _format, "rb"))
        else:
            return False
        return True

    def save_df(self, output_file: str, pickling = False) -> None:
        """save_df
        Function used to save all the dataframes controlled by the node

        :param output_file: Output file, this is the path and the first part of
        the name that must be used to save the files
        :type output_file: str
        :param pickling: (Default False) defines if it is required to save also
        the dataframes in pickle format
        :rtype: None
        """
        _format = ".csv"
        self.states.to_csv(output_file + NodeAnalyzer.STATES_FILE_NAME + _format, '|')
        self.transitions.to_csv(output_file + NodeAnalyzer.TRANSITIONS_FILE_NAME + _format, '|')
        self.routes.to_csv(output_file + NodeAnalyzer.ROUTES_FILE_NAME + _format, '|')
        self.signaling.to_csv(output_file + NodeAnalyzer.SIGNAL_FILE_NAME + _format, '|')

        if pickling:
            _format = ".pkl"
            pickle.dump(self.states, open(output_file + NodeAnalyzer.STATES_FILE_NAME \
                        + _format, "wb"))
            pickle.dump(self.transitions, open(output_file + NodeAnalyzer.TRANSITIONS_FILE_NAME \
                        + _format, "wb"))
            pickle.dump(self.routes, open(output_file + NodeAnalyzer.ROUTES_FILE_NAME \
                        + _format, "wb"))
            pickle.dump(self.signaling, open(output_file + NodeAnalyzer.SIGNAL_FILE_NAME \
                        + _format, "wb"))

    def __get_route_data(self, route: Route) -> Dict:
        """__get_route_data.
        Used to return the dictionary with route data that needs to be
        inserted

        :param route: Route that needs to be translated
        :type route: Route
        :rtype: dict
        """
        # Increase the node counter
        self.route_counter += 1
        # Assigne the values at the dictionary and return it
        return {NodeAnalyzer.ROUTES_COLUMNS[1]: self.route_counter,
                NodeAnalyzer.ROUTES_COLUMNS[2]: str(route.addr),
                NodeAnalyzer.ROUTES_COLUMNS[3]: str(route.nh),
                NodeAnalyzer.ROUTES_COLUMNS[4]: str(route.path),
                NodeAnalyzer.ROUTES_COLUMNS[5]: str(route.policy_value)}

    def __evaluate_pkt(self, row_value:str) -> str:
        """__evaluate_pkt.
        Evaluate a single pkt row of the DF, it will return the compressed
        string corresponding to the row, A{ID} for an advertisement or
        W{ID} for a withdraw, the id corresponds to the route in the
        route_to_id DataFrame

        :param row_value: row of the dataframe that contains a packet that needs to
        be analyzed
        :type row_value: str
        :rtype: str
        """
        # Get the packet and the route transmitted
        packet = Packet.fromString(row_value)
        route = Route.fromString(packet.content)
        tmp_pv = PolicyValue(0)
        route.policy_value = tmp_pv
        # If the route is not in the DataFrane of routes add it
        if hash(route) not in self.routes.index:
            self.routes.loc[hash(route)] = self.__get_route_data(route)
        # Check the packet type and return the corresponding compressed version
        if packet.packet_type == Packet.UPDATE:
            return "A" + str(self.routes.loc[hash(route)][NodeAnalyzer.ROUTES_COLUMNS[1]])
        if packet.packet_type == Packet.WITHDRAW:
            return "W" + str(self.routes.loc[hash(route)][NodeAnalyzer.ROUTES_COLUMNS[1]])

        print("Something very bad happened")
        sys.exit(2)

    def __evaluate_tx(self, row_value: str) -> str:
        """__evaluate_tx.
        This function is used to evaluate a transmitted message and get
        the comphressed version, for now is equal to __evaluate_rx

        :param row_value: row value to evaluate
        :type row_value: str
        :rtype: str
        """
        return self.__evaluate_pkt(row_value)

    def __evaluate_rx(self, row_value: str) -> str:
        """__evaluate_rx.
        This function is used to evaluate a received message and get
        the comphressed version, for now is equal to __evaluate_tx

        :param row_value: row value to evaluate
        :type row_value: str
        :rtype: str
        """
        return self.__evaluate_pkt(row_value)

    def get_out_signal(self, values) -> List:
        """get_out_signal.
        Return the output signal given the list transmitting rows

        :param values: Rows to evaluate
        :rtype: list
        """
        values = values.apply(self.__evaluate_tx)
        return ''.join(list(OrderedDict.fromkeys(values.values)))

    def evaluate_signaling(self, df_to_evaluate: pd.DataFrame, order_by_time=False) -> str:
        """evaluate_signaling.
        Evaluate a dataframe to get the signaling output

        :param df_to_evaluate: Dataframe that needs to be evaluated
        :type df_to_evaluate: pd.DataFrame
        :param order_by_time: (Default False) Define if it is necessary to order
        the DataFrame before studying it
        :rtype: str
        """
        # Order if necessary
        tmp_df = df_to_evaluate.sort_values(by=[NodeAnalyzer.EVALUATION_COLUMNS[3]]) \
                    if order_by_time else df_to_evaluate
        # Keep only the trasmitting rowns
        tmp_df = tmp_df[tmp_df.event == Events.TX][[NodeAnalyzer.EVALUATION_COLUMNS[5]]]
        # Group by the event cause
        tmp_v = tmp_df.groupby(by=[NodeAnalyzer.EVALUATION_COLUMNS[1]],
                               sort=False).value.agg(self.get_out_signal)
        # Study and save the signal
        signal = SignalHandler(''.join(tmp_v.values))
        signal_hash = hash(str(signal))
        if signal_hash not in self.signaling.index:
            self.signaling.loc[signal_hash] = [str(signal), signal.len_advert(),
                                                signal.len_withdraw(), signal.len(),
                                                1]
        else:
            self.signaling.at[signal_hash, NodeAnalyzer.SIGNAL_COLUMNS[5]] += 1

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

    def __statate_incremental_variation(self, rx_value: str, new_state: set) -> set:
        pkt = Packet.fromString(rx_value)
        route = Route.fromString(pkt.content)
        route.policy_value = PolicyValue(0)
        if pkt.packet_type == Packet.UPDATE:
            self.experiment_actual_state = new_state.copy()
            new_state = self.actual_state.copy()
            new_state.add(self.routes.loc[hash(route)][NodeAnalyzer.ROUTES_COLUMNS[1]])
        elif pkt.packet_type == Packet.WITHDRAW:
            self.experiment_actual_state = new_state.copy()
            new_state = self.actual_state.copy()
            new_state.remove(self.routes.loc[hash(route)][NodeAnalyzer.ROUTES_COLUMNS[1]])
        return new_state

    def __statate_swap_variation(self, rx_value: str, new_state: set) -> set:
        pkt = Packet.fromString(rx_value)
        route = Route.fromString(pkt.content)
        route.policy_value = PolicyValue(0)
        self.experiment_actual_state = new_state.copy()
        new_state = self.actual_state.copy()
        for row_value, row_nh in zip(self.routes[NodeAnalyzer.ROUTES_COLUMNS[1]],
                                     self.routes[NodeAnalyzer.ROUTES_COLUMNS[3]]):
            if row_nh == route.nh:
                if row_value in new_state:
                    new_state.remove(row_value)
        new_state.add(self.routes.loc[hash(route)][NodeAnalyzer.ROUTES_COLUMNS[1]])
        return new_state

    def hash_state_set(self, state: set) -> hash:
        return hash(str(sorted(list(state))))

    @classmethod
    def translate(cls, state: set) -> str:
        res = str(sorted(list(state)))
        res = res.replace('[', '{')
        res = res.replace(']', '}')
        return res

    def __evaluate_event_rx(self, rx_event_id: int, rx_value: str, 
                            data_frame: pd.DataFrame):

        # Find events caused by the rx
        if rx_event_id not in data_frame.index:
            return
        events_in_between = data_frame.loc[[rx_event_id], : ]

        # Keep a tmp variable with the state that can have been changed
        # thanks to this reception
        new_state = set()

        # Keep a list of transmitted routes
        transmitted_routes = []

        """print(rx_value)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        print(events_in_between)"""

        # Check each row of the events caused by the reception
        for row_event, row_value in zip(events_in_between[NodeAnalyzer.EVALUATION_COLUMNS[2]],
                                        events_in_between[NodeAnalyzer.EVALUATION_COLUMNS[5]]):
            # If the event is a change in the state, I update the local
            # variable that keeps the state
            if row_event == Events.RIB_CHANGE:
                new_state = self.__evaluate_rib_change(row_value)
            # If the event is a TX i update the corresponding sets
            if row_event == Events.TX:
                elem = self.__evaluate_tx(row_value)
                if elem not in transmitted_routes:
                    transmitted_routes.append(elem)

        # Evaluate the reception event
        received_route = self.__evaluate_rx(rx_value)

        transmitted_routes = None if len(transmitted_routes) == 0 else \
                             sorted(transmitted_routes)

        # The state is changed thanks to this reception message
        if len(self.experiment_actual_state ^ new_state) > 0:
            # If the deifference is larger than 1 then there is a problem
            if abs(len(self.experiment_actual_state)-len(new_state)) > 1:
                print("something really bad happened")
                exit(3)

            if abs(len(self.experiment_actual_state)-len(new_state)) == 1:
                new_state = self.__statate_incremental_variation(rx_value, new_state)
            else:
                new_state = self.__statate_swap_variation(rx_value, new_state)

            # Check if the state has already been known
            state_hash = self.hash_state_set(new_state)
            if state_hash not in self.states.index:
                # Add the state to the states dictionary
                self.states.loc[state_hash] = [str(new_state), 1]
            else:
                # The state is already in the dictionary, increase the counter
                self.states.at[state_hash, NodeAnalyzer.STATES_COLUMNS[2]] += 1

        # Create the new transition
        input_state = NodeAnalyzer.translate(self.actual_state)
        output_state = NodeAnalyzer.translate(new_state)
        transition = Transition(input_state, output_state,
                                received_route, transmitted_routes)

        # Change the state
        self.actual_state = new_state
        # Check if the transition has already been known
        if hash(transition) not in self.transitions.index:
            self.transitions.loc[hash(transition)] = [transition.init_state,
                                                      transition.output_state,
                                                      transition.input,
                                                      transition.output,
                                                      transition.counter]
        else:
            # The transition is already in the dictionary, increase the
            self.transitions.at[hash(transition), NodeAnalyzer.TRANSITIONS_COLUMNS[5]] += 1

    # @profile
    def evaluate_fsm(self, data_frame: pd.DataFrame) -> None:
        """evaluate_fsm.
        Evaluate the FSM evolution events of the node,
        New states based on the knowledge
        New transitions ecc

        :param data_frame: Dataframe to evaluate
        :type data_frame: pd.DataFrame
        :rtype: None
        """
        self.actual_state = set()
        self.experiment_actual_state = set()

        tmp_rx = data_frame[(data_frame.event == Events.RX)]

        # To activate a useful O(LogN) index search the datafram must be sorted
        # This will break the event time order, but we already extrapolated
        # RX events in time order
        data_frame = data_frame.sort_index()

        tmp_rx.apply(lambda row: self.__evaluate_event_rx(row.event_id,
                                                          row.value,
                                                          data_frame), axis=1)

    def __delitem__(self, value):
        """__delitem__
        Ensure to delete all the local dataframes
        """
        del self.states
        del self.transitions
        del self.routes
        del self.signaling

    def __str__(self):
        """__str__
        Return all the dataframes controlled by the node analyzer in a human
        readable format
        """
        return str(self.states) + "\n" + \
               str(self.transitions) + "\n" + \
               str(self.routes) + "\n" + \
               str(self.signaling) + "\n"

class FileAnalyzer():
    """
    FileAnalyzer
    ============

    Class to analyze single files, is possible to study multiple nodes
    per file
    A file analyzer object can split filter and operate to the experiment dataframe.
    It can study the file but all studies that referes to nodes must be overtaken
    by the correspective node analyzer.
    """

    # Evaluation dataframe columns expected
    # NEVER CHANGE THE POSITION OF THE ELEMENTS ALREADY IN THE LIST
    EVALUATION_COLUMNS = ['event_id', 'event_cause', 'event', 'time', 'node',
                          'value']
    EVALUATION_COLUMNS_TYPES = {'event_id': int,
                                'event_cause': int,
                                'event': int,
                                'time': float,
                                'node': str,
                                'value': str}

    def __init__(self, input_file_path: str, node_analyzers: Dict[str, NodeAnalyzer]):
        self._df = pd.read_csv(open(input_file_path), sep='|',
                               index_col=FileAnalyzer.EVALUATION_COLUMNS[1],
                               dtype=SingleFileAnalysis.col_types)
        self.nodes = node_analyzers
        self.none_type = type(None)

    def __select_node(self, node_id: str, dataframe: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """selectNode.

        :param node_id: id of the node that needs to be isolated
        :type node_id: int
        :rtype: pd.DataFram
        """
        # Mantain in the dataframe only the rows where the node id is equal
        # to the required one
        data_frame = self._df if isinstance(dataframe, self.none_type) else dataframe
        return data_frame[data_frame.node == node_id]

    def __filter_events(self, events_list: List[Events], dataframe = None) -> pd.DataFrame:
        """keep_only_fsm_events.
        Function that returns a dataframe with only events that are meaningful
        for a FSM study, RIB_CHANGE, TX and RX

        :return: Datafram with only those events
        :rtype: pd.DataFrame
        """
        data_frame = self._df if isinstance(dataframe, self.none_type) else dataframe
        return data_frame[data_frame.event.isin(events_list)]

    def study_signaling(self, nodes: List[str]) -> None:
        """study_signaling.
        Study the signaling in the current file for the list of nodes passed

        :param nodes: list of nodes passed
        :type nodes: List[str]
        :rtype: None
        :raise KeyError: If one of the passed nodes is not in the dictionary
        """
        for node in nodes:
            # Check if the node is in the dict of node alayzers
            if node not in self.nodes.keys():
                raise KeyError("{} Not found in the nodes dictionary")

            node_df = self.__select_node(node)
            node_filtered_df = self.__filter_events([Events.TX], dataframe=node_df)
            self.nodes[node].evaluate_signaling(node_filtered_df, order_by_time=True)

    def study_fsm(self, nodes: List[str]) -> None:
        """study_fsm.
        Study the fsm in the current file for the list of nodes passed

        :param nodes: list of nodes passed
        :type nodes: List[str]
        :rtype: None
        :raise KeyError: If one of the passed nodes is not in the dictionary
        """
        for node in nodes:
            # Check if the node is in the dict of node alayzers
            if node not in self.nodes.keys():
                raise KeyError("{} Not found in the nodes dictionary")

            node_df = self.__select_node(node)
            node_filtered_df = self.__filter_events([Events.TX, Events.RX, Events.RIB_CHANGE], 
                                                    dataframe=node_df)
            self.nodes[node].evaluate_fsm(node_filtered_df)

