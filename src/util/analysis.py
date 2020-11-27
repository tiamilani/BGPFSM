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

import ast
from collections import OrderedDict
import pickle
from typing import List, Dict, Optional
import sys
import os
import pandas as pd

from events import Events
from packet import Packet
from route import Route
from transition import Transition
from policies import PolicyValue

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
    CONVERGENCE_COLUMNS = ['convergence_time', 'in_messages']
    RFD_COLUMNS = ['id', 'time', 'route', 'figure_of_merit', 'suppressed']

    # File names for load and save
    STATES_FILE_NAME = "_states"
    TRANSITIONS_FILE_NAME = "_transitions"
    ROUTES_FILE_NAME = "_routes"
    SIGNAL_FILE_NAME = "_signal"
    CONVERGENCE_FILE_NAME = "_convergence"
    RFD_FILE_NAME = "_rfd"

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
        self.convergence = pd.DataFrame(columns=NodeAnalyzer.CONVERGENCE_COLUMNS)
        self.rfd = pd.DataFrame(columns=NodeAnalyzer.RFD_COLUMNS)
        self.actual_state = set()
        self.experiment_actual_state = set()
        self.route_counter = 0

    def load_pickle(self, input_file: str) -> bool:
        """load_pickle.
        Function used to load the analyzer pickle files
        It returns True if all pickles has been loaded
        Otherwise it will return False

        :param input_file: File prefix for the pickles, with the path
        :type input_file: str
        :rtype: bool
        """
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
        if os.path.isfile(input_file + NodeAnalyzer.CONVERGENCE_FILE_NAME + _format):
            self.convergence = pickle.load(open(input_file + NodeAnalyzer.CONVERGENCE_FILE_NAME\
                                      + _format, "rb"))
        else:
            return False
        if os.path.isfile(input_file + NodeAnalyzer.RFD_FILE_NAME + _format):
            self.rfd = pickle.load(open(input_file + NodeAnalyzer.RFD_FILE_NAME \
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
        self.convergence.to_csv(output_file + NodeAnalyzer.CONVERGENCE_FILE_NAME + _format, '|',
                index=False)
        self.rfd.to_csv(output_file + NodeAnalyzer.RFD_FILE_NAME + _format, '|')

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
            pickle.dump(self.convergence, open(output_file + NodeAnalyzer.CONVERGENCE_FILE_NAME\
                        + _format, "wb"))
            pickle.dump(self.rfd, open(output_file + NodeAnalyzer.RFD_FILE_NAME\
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

    @classmethod
    def __evaluate_rib_change(cls, row_value: str) -> set:
        """__evaluate_rib_change.
        Evaluate a row that contains a row change, it returns
        the new state, if the set is empty it will return None

        :param row: row to evaluate
        :return: None if the set is empty, the str(set) otherwise
        """
        if row_value == "set()":
            return set()
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

    @classmethod
    def hash_state_set(cls, state: set) -> hash:
        """hash_state_set.
        Return the hash of the set.
        This function must be used carefully because it hashes mutable Items
        The state is translated into a list, ordered, converted to a string
        and hashed

        :param state: Set of states to hash
        :type state: set
        :rtype: hash
        """
        return hash(str(sorted(list(state))))

    @classmethod
    def translate(cls, state: set) -> str:
        """translate.
        Translate a state into a string
        The set will be converted into a list, sorted, and then converted into
        a string
        `[` and `]` charachters will be replaced by `{` and `}`

        :param state: State to convert
        :type state: set
        :rtype: str
        """
        res = str(sorted(list(state)))
        res = res.replace('[', '{')
        res = res.replace(']', '}')
        return res

    def __state_analyzer(self, new_state: set, rx_value: str) -> set:
        # The state is changed thanks to this reception message
        if len(self.experiment_actual_state ^ new_state) > 0:
            # If the difference is larger than 1 then there is a problem
            if abs(len(self.experiment_actual_state)-len(new_state)) > 1:
                print("something really bad happened")
                sys.exit(3)

            if abs(len(self.experiment_actual_state)-len(new_state)) == 1:
                new_state = self.__statate_incremental_variation(rx_value, new_state)
            else:
                new_state = self.__statate_swap_variation(rx_value, new_state)

        return new_state

    def __state_register(self, new_state: set) -> None:
        # Check if the state has already been known
        state_hash = NodeAnalyzer.hash_state_set(new_state)
        if state_hash not in self.states.index:
            # Add the state to the states dictionary
            self.states.loc[state_hash] = [str(new_state), 1]
        else:
            # The state is already in the dictionary, increase the counter
            self.states.at[state_hash, NodeAnalyzer.STATES_COLUMNS[2]] += 1


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

        # Check each row of the events caused by the reception
        for row_event, row_value in zip(events_in_between[NodeAnalyzer.EVALUATION_COLUMNS[2]],
                                        events_in_between[NodeAnalyzer.EVALUATION_COLUMNS[5]]):
            # If the event is a change in the state, I update the local
            # variable that keeps the state
            if row_event == Events.RIB_CHANGE:
                new_state = NodeAnalyzer.__evaluate_rib_change(row_value)
            # If the event is a TX i update the corresponding sets
            if row_event == Events.TX:
                elem = self.__evaluate_tx(row_value)
                if elem not in transmitted_routes:
                    transmitted_routes.append(elem)

        # Evaluate the reception event
        received_route = self.__evaluate_rx(rx_value)

        transmitted_routes = None if len(transmitted_routes) == 0 else \
                             sorted(transmitted_routes)

        new_state = self.__state_analyzer(new_state, rx_value)
        self.__state_register(new_state)

        # Create the new transition
        input_state = NodeAnalyzer.hash_state_set(self.actual_state)
        output_state = NodeAnalyzer.hash_state_set(new_state)
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

    def __evaluate_event_mrai(self, mrai_event_time: float, mrai_id: int,
                            data_frame: pd.DataFrame):
        # Events before the MRAI timeout
        events_before = data_frame[data_frame.time < mrai_event_time]
        previous_mrai = None
        if Events.MRAI in events_before.event.values:
            previous_mrai = events_before[events_before.event == Events.MRAI].tail(1).time.values[0]
        if previous_mrai is not None:
            events_before = events_before[(events_before.time > previous_mrai) &\
                                          (events_before.event != Events.MRAI) &\
                                          (events_before.event != Events.TX)]
        # Find events caused by the MRAI
        events_after = pd.DataFrame(columns=NodeAnalyzer.EVALUATION_COLUMNS)
        if mrai_id in data_frame.index:
            events_after = data_frame.loc[[mrai_id], :]

        # Keep a tmp variable with the state that can have been changed
        # thanks to this reception
        new_state = None

        # Keep a list of received and transmitted routes
        received_routes = []
        transmitted_routes = []
        rx_value = None

        memory_actual_state = self.actual_state.copy()

        if len(events_before.index) == 0:
            return

        # Check each row of the events caused by the reception
        for row_event, row_value in zip(events_before[NodeAnalyzer.EVALUATION_COLUMNS[2]],
                                        events_before[NodeAnalyzer.EVALUATION_COLUMNS[5]]):
            # If the event is a change in the state, I update the local
            # variable that keeps the state
            if row_event == Events.RIB_CHANGE:
                if rx_value is not None:
                    if new_state is None:
                        new_state = set()
                    else:
                        self.actual_state = new_state
                    new_state = NodeAnalyzer.__evaluate_rib_change(row_value)
                    new_state = self.__state_analyzer(new_state, rx_value)
            # If the event is a TX i update the corresponding sets
            if row_event == Events.RX:
                rx_value = row_value
                elem = self.__evaluate_rx(row_value)
                if elem not in received_routes:
                    received_routes.append(elem)

        new_state = set() if new_state is None else new_state
        self.actual_state = memory_actual_state
        self.__state_register(new_state)

        # Check each row of the events caused by the reception
        for row_event, row_value in zip(events_after[NodeAnalyzer.EVALUATION_COLUMNS[2]],
                                        events_after[NodeAnalyzer.EVALUATION_COLUMNS[5]]):
            # If the event is a TX i update the corresponding sets
            if row_event == Events.TX:
                elem = self.__evaluate_tx(row_value)
                if elem not in transmitted_routes:
                    transmitted_routes.append(elem)

        received_routes = None if len(received_routes) == 0 else \
                             sorted(received_routes)
        transmitted_routes = None if len(transmitted_routes) == 0 else \
                             sorted(transmitted_routes)

        
        # Create the new transition
        input_state = NodeAnalyzer.hash_state_set(self.actual_state)
        output_state = NodeAnalyzer.hash_state_set(new_state)
        transition = Transition(input_state, output_state,
                                received_routes, transmitted_routes)

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

        tmp_mrai = data_frame[(data_frame.event == Events.MRAI)]

        tmp_mrai.apply(lambda row: self.__evaluate_event_mrai(row.time,
                                                          row.event_id,
                                                          data_frame), axis=1)

    def evaluate_convergence(self, data_frame: pd.DataFrame, start_time: float) -> None:
        """evaluate_convergence.
        Evaluate the convergence time required by the node

        :param data_frame: Dataframe to evaluate
        :type data_frame: pd.DataFrame
        :rtype: None
        """

        rib_events = data_frame[(data_frame.event == Events.RIB_CHANGE)]
        if len(rib_events.index) > 0:
            last_rib = rib_events.tail(1)[NodeAnalyzer.EVALUATION_COLUMNS[3]].values[0]
        else:
            last_rib = start_time 
        conv_time = last_rib - start_time
        conv_df = data_frame[(data_frame.time <= last_rib)]
        messages_rx = len(conv_df[(conv_df.event == Events.RX)].index)
        self.convergence.loc[len(self.convergence.index)] = [conv_time, messages_rx]
        
    def __evaluate_figure_of_merit_event(self, time: str, value: str) -> None:
        obj = ast.literal_eval(value)
        route = Route.fromString(obj[0])
        figure_of_merit = obj[1]
        _id = hash(str(route.addr) + str(route.nh))
        self.rfd = self.rfd.append(dict(zip(NodeAnalyzer.RFD_COLUMNS, 
                            [_id, time, route, figure_of_merit, False])), ignore_index=True)

    def __assign_suppressed(self, idx, value):
        self.rfd.loc[idx, NodeAnalyzer.RFD_COLUMNS[4]] = value

    def __evaluate_rfd_state(self, time: float, event: int, value: str) -> None:
        route = Route.fromString(value)

        if event == Events.ROUTE_REUSABLE or event == Events.END_T_HOLD:
            # The route is now usable again, set every element after as suppressed False
            suppressed = False
        else:
            # The route has been suppressed
            suppressed = True

        _id = hash(str(route.addr) + str(route.nh))
        
        self.rfd.suppressed[(self.rfd.id == _id) & (self.rfd.time >= time)] = suppressed

    def evaluate_rfd(self, data_frame: pd.DataFrame) -> None:
        """evaluate_rfd.
        Evaluate the RFD history

        :param data_frame: Dataframe to evaluate
        :type data_frame: pd.DataFrame
        :rtype: None
        """

        figure_of_merit_evolution = data_frame[(data_frame.event == Events.FIGURE_OF_MERIT_VARIATION)]
        figure_of_merit_evolution.apply(lambda row: self.__evaluate_figure_of_merit_event(row.time,
                                            row.value), axis=1)

        route_state = data_frame[(data_frame.event == Events.ROUTE_REUSABLE) |
                                 (data_frame.event == Events.END_T_HOLD) |
                                 (data_frame.event == Events.ROUTE_SUPPRESSED)]
        route_state.apply(lambda row: self.__evaluate_rfd_state(row.time, row.event,
                                                                row.value),
                          axis=1)

        print(self.rfd)
        
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
    GENERAL_STUDY_COLUMNS = ['id', 'file_name', 'convergence_time', 'total_messages']
    GENERAL_STUDY_FILE_NAME = "general_study"

    NODE_STUDY_COLUMNS = ['node', 'convergence_time', 'convergence_time_std', 
                          'in_messages', 'in_messages_std', 'out_messages',
                          'out_messages_std']

    def __init__(self, input_file_path: str, node_analyzers: Dict[str, NodeAnalyzer],
                 general_study_df: Optional[pd.DataFrame] = None):
        self.file_name = input_file_path.split('/')[-1]
        self._df = pd.read_csv(open(input_file_path), sep='|',
                               index_col=FileAnalyzer.EVALUATION_COLUMNS[1],
                               dtype=FileAnalyzer.EVALUATION_COLUMNS_TYPES)
        self.nodes = node_analyzers
        self.none_type = type(None)
        if isinstance(general_study_df, self.none_type):
            self.general_study = pd.DataFrame(columns=FileAnalyzer.GENERAL_STUDY_COLUMNS)
            self.general_study = self.general_study.set_index(FileAnalyzer.GENERAL_STUDY_COLUMNS[0])
        else:
            self.general_study = general_study_df

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
            node_filtered_df = self.__filter_events([Events.TX, Events.RX, Events.RIB_CHANGE,
                                                     Events.MRAI],
                                                    dataframe=node_df)
            self.nodes[node].evaluate_fsm(node_filtered_df)

    def study_node_convergence(self, nodes: List[str]) -> None:
        """study_node_convergence
        Study the convergence time, number of messages required for the list
        of nodes passed

        :param nodes: list of nodes passed
        :type nodes: List[str]
        :rtype: None
        :raise KeyError: If one of the passed nodes is not in the dictionary
        """
        tx_df = self.__filter_events([Events.TX], dataframe=self._df)
        start_time = tx_df.head(1)[FileAnalyzer.EVALUATION_COLUMNS[3]].values[0]

        for node in nodes:
            if node not in self.nodes.keys():
                raise KeyError("{} Not found in the nodes dictionary".format(node))

            node_df = self.__select_node(node)
            node_filtered_df = self.__filter_events([Events.TX, Events.RX, Events.RIB_CHANGE], dataframe = node_df)
            self.nodes[node].evaluate_convergence(node_filtered_df, start_time)

    def study_rfd(self, nodes: List[str]) -> None:
        """study_rfd
        Study the RFD history evolution for each node in the list of nodes

        :param nodes: list of nodes passed
        :type nodes: List[str]
        :rtype: None
        :raise KeyError: If one of the passed nodes is not in the dictionary
        """
        rfd_events_df = self.__filter_events([Events.ROUTE_REUSABLE, Events.END_T_HOLD,
                                              Events.FIGURE_OF_MERIT_VARIATION,
                                              Events.ROUTE_SUPPRESSED], dataframe=self._df)

        for node in nodes:
            if node not in self.nodes.keys():
                raise KeyError("{} Not found in the nodes dictionary".format(node))

            node_df = self.__select_node(node)
            node_filtered_df = self.__filter_events([Events.ROUTE_REUSABLE, Events.END_T_HOLD,
                                                  Events.FIGURE_OF_MERIT_VARIATION,
                                                  Events.ROUTE_SUPPRESSED], dataframe = node_df)
            self.nodes[node].evaluate_rfd(node_filtered_df)

    def general_file_study(self) -> pd.DataFrame:
        tx_df = self.__filter_events([Events.TX], dataframe=self._df)
        rx_df = self.__filter_events([Events.RX], dataframe=self._df)
        start_time = tx_df.head(1)[FileAnalyzer.EVALUATION_COLUMNS[3]].values[0]
        endup_time = rx_df.tail(1)[FileAnalyzer.EVALUATION_COLUMNS[3]].values[0]
        convergence_time = endup_time - start_time
        number_of_messages = len(self.__filter_events([Events.TX]).index)
        self.general_study.loc[hash(self.file_name)] = (self.file_name, convergence_time, 
                                                        number_of_messages)
        return self.general_study
