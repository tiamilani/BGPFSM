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
from graphviz import Digraph

class SingleFileAnalysis():

    ROUTE_COUNTER = 0

    def __init__(self, inputFile):
        self.inputFile = open(inputFile)
        self.df = pd.read_csv(self.inputFile, sep='|')
        self.states = set()
        self.actualState = None
        self.transitions = set() 
        self.route_to_id = {}

    def selectNode(self, node_id):
        self.df = self.df[self.df.node == node_id]

    def translation(self, df=None):
        NoneType = type(None)
        if type(df) == NoneType:
            df = self.df
        for idx, row in df.iterrows():
            if row["event"] == Events.TX or row["event"] == Events.RX:
                row["value"] = Packet.fromString(row["value"])
                row["value"].content = Route.fromString(row["value"].content)
            if row["event"] == Events.RT_CHANGE or row["event"] == Events.NEW_PATH:
                row["value"] = Route.fromString(row["value"])
        return df

    def evaluate_fsm(self):
        tmp_df = self.df[(self.df.event == Events.RIB_CHANGE) | \
                         (self.df.event == Events.RX) | \
                         (self.df.event == Events.TX)]
        tmp_df = self.translation(df=tmp_df)
        while Events.RX in tmp_df.event.values:
            first_pkt_received = tmp_df[tmp_df.event == Events.RX].iloc[0]
            first_pkt_index = first_pkt_received.name
            tmp_df = tmp_df.drop(first_pkt_index)
            if Events.RX not in tmp_df.event.values:
                break
            second_pkt_received = tmp_df[tmp_df.event == Events.RX].iloc[0]
            second_pkt_index = second_pkt_received.name
            events_in_between = tmp_df.loc[first_pkt_index:second_pkt_index][:-1]
            new_state = None
            transmitted_routes = set()
            for idx, row in events_in_between.iterrows():
                if row["event"] == Events.RIB_CHANGE:
                    if row["value"] == "set()":
                        new_state = None
                    else:
                        new_state = row["value"]
                if row["event"] == Events.TX:
                    packet = Packet.fromString(row["value"])
                    route = packet.content
                    if str(route) not in self.route_to_id.keys():
                        self.route_to_id[str(route)] = self.ROUTE_COUNTER
                        self.ROUTE_COUNTER += 1
                    if packet.packet_type == Packet.UPDATE:
                        transmitted_routes.add("A" + str(self.route_to_id[str(route)]))
                    elif packet.packet_type == Packet.WITHDRAW:
                        transmitted_routes.add("W" + str(self.route_to_id[str(route)]))
                    else:
                        print("Something very bad happened")
                        exit(2)

            packet = Packet.fromString(first_pkt_received["value"])
            route = packet.content
            if str(route) not in self.route_to_id.keys():
                self.route_to_id[str(route)] = self.ROUTE_COUNTER
                self.ROUTE_COUNTER += 1
            if packet.packet_type == Packet.UPDATE:
                inp = "A" + str(self.route_to_id[str(route)])
            elif packet.packet_type == Packet.WITHDRAW:
                inp = "W" + str(self.route_to_id[str(route)])
            else:
                print("Something very bad happened")
                exit(2)
            if len(transmitted_routes) == 0:
                transmitted_routes = None
            transition = Transition(self.actualState, new_state,
                    inp,
                    transmitted_routes)
            self.actualState = new_state
            self.states.add(new_state)
            self.transitions.add(transition)

    def get_fsm_graphviz(self, dot):
        for state in self.states:
            if state == None:
                dot.node("{}")
            else:
                dot.node(str(state))
        for trans in self.transitions:
            inp = str(trans.init_state) if trans.init_state is not None \
                    else "{}"
            out = str(trans.output_state) if trans.output_state is not None \
                    else "{}"
            trans_output = str(trans.output) if trans.output is not None \
                    else ""

            dot.edge(inp, out, label="{}:{}".format(trans.input, trans_output))
        return dot



    def __delitem__(self):
        self.inputFile.close()
        del self.df

    def __str__(self):
        return str(self.df)
