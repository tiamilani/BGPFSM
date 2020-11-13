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
import math
import pandas as pd
from graphviz import Digraph
from route import Route
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from analysis import NodeAnalyzer
from policies import PolicyValue
from matplotlib.lines import Line2D

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

    def get_fsm_graphviz(self, dot: Digraph) -> Digraph: # pylint: disable=too-many-locals
        """get_fsm_graphviz.

        :param dot: dot object of graphviz used to create the graph
        :returns: the dot object modified
        """
        # Insert all states like nodes
        for state_hash, state_str in zip(self.node.states.index.tolist(),
                                         self.node.states[NodeAnalyzer.STATES_COLUMNS[1]]):
            state = ast.literal_eval(state_str) if state_str != "set()" else set()
            if len(state) == 0:
                dot.node(str(state_hash), label="{}")
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
            # If the output of the transition is empty (No messages sent)
            # use an empty string to represent it
            trans_output = ""
            if response is not None:
                trans_output = response
            # Insert the edge
            dot.edge(str(input_state), str(output_state), label=" {}:{} ".format(
                cause, trans_output))
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
        for _id, addr, next_hop, path, policy_value in \
                zip(self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[1]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[2]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[3]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[4]],
                    self.node.routes[NodeAnalyzer.ROUTES_COLUMNS[5]],):
            network = ipaddress.ip_network(addr)
            path = ast.literal_eval(path)
            policy_value = PolicyValue(int(policy_value))
            route = Route(network, path, next_hop, policy_value=policy_value)
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
        lns = legend1+legend2+legend3+legend4
        labs = [l.get_label() for l in lns]
        # Shrink current axis's height by 10% on the bottom
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        ax2.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, ncol=2)

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel("# Of messages")
        ax.set_ylabel("Probability [0-1]")
        ax2.set_ylabel("# Of Outputs")
        ax.set_title("Out signaling")

        fig.savefig(output_file, format="pdf")

class GeneralPlotter():
    """
    GeneralPlotter
    --------------

    Class used to plot information for the general study of an experiment
    Convergence time/Number of messages sent/ ecc
    """

    def __init__(self, ges_df: str):
        self.ges = pd.read_csv(ges_df, sep="|", index_col="id")

    def ges_boxplot(self, output_file_name: str, _column: str) -> None:
        boxplot = self.ges.boxplot(column=_column)
        plt.savefig(output_file_name, format="pdf")
        plt.close()

class NodeConvergencePlotter():
    """
    Node Convergence plotter
    ------------------------

    Used to plot the graph of nodes convergence
    """
    
    COLUMNS=["avg_conv_time", "std_conv_time", "avg_in_messages", "std_in_messages"]

    def __init__(self, df: pd.DataFrame, centrality: dict):
        self.df = df
        self.centrality = centrality

    def plot(self, output_file_name, limit=0) -> None:
        if limit > 0:
            _max = limit
        else:
            _max = math.ceil(self.df[NodeConvergencePlotter.COLUMNS[0]].max())
        values=[]
        for i in range(_max+1):
            values.append(len(self.df[self.df[NodeConvergencePlotter.COLUMNS[0]] <= i].index))

        fig, ax = plt.subplots() # pylint: disable=invalid-name

        l = ax.plot(range(_max+1), values, 'r', label="Nodes converged")

        lns = l
        labs = [l.get_label() for l in lns]
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, ncol=2)

        ax.set_xlabel("Time from the starting event [s]")
        ax.set_ylabel("# Converged nodes")

        fig.savefig(output_file_name, format="pdf")

    def plot_centrality_vs_convergence(self, output_file_name, hops, limit=None):

        fig, ax = plt.subplots()
        ax2 = ax.twinx()

        hops_centrality = [self.centrality[node] for node in hops.keys()]
        hops_conv_time = [self.df[self.df.node == int(node)].avg_conv_time.values[0] for node in hops.keys()]

        l = ax.plot(hops.keys(), hops_centrality, 'b', label="DPC centrality", zorder = 10, linewidth=0.7)
        l2 = ax2.plot(hops.keys(), hops_conv_time, 'g', label="Convergence time", zorder = 3, linewidth=0.6)
        
        # Set the tick positions
        ax.set_xticks(list(hops.keys()))
    
        actual_dist = 0
        groups = [[]]
        for node in hops:
            if hops[node] > actual_dist:
                ax.axvline(x=str(node), color='orange', ls='--', zorder=5)
                actual_dist = hops[node]
                groups.append([])
            groups[-1].append(node)

        groups_limits = []
        for group in groups:
            groups_limits.append(group[0])

        avg_times = []
        avg_centr = []
        for i in range(len(groups_limits)):
            group_avg_time = self.df[self.df["node"].isin(groups[i])]["avg_conv_time"].mean()
            avg_times.append(group_avg_time)
            gr1 = groups_limits[i]

            avg_centrality = 0
            for node in groups[i]:
                avg_centrality += self.centrality[node]
            avg_centrality /= len(groups[i])
            avg_centr.append(avg_centrality)

            if i == len(groups_limits) -1:
                ax.hlines(y = avg_centrality, xmin = gr1, xmax = groups[i][-1], color="blue", ls='--', zorder=4)
                ax2.hlines(y = group_avg_time, xmin = gr1, xmax = groups[i][-1], color="r", ls='--', zorder=4)
            else:
                ax.hlines(y = avg_centrality, xmin = gr1, xmax = groups_limits[i+1], color="blue", ls='--', zorder=4)
                ax2.hlines(y = group_avg_time, xmin = gr1, xmax = groups_limits[i+1], color="r", ls='--', zorder=4)

        custom_lines = [Line2D([0], [0], color="orange", ls = '--', label = "Hop group separator"),
                        Line2D([0], [0], color="blue", ls = '--', label = "AVG centrality in the group"),
                        Line2D([0], [0], color="r", ls = '--', label = "AVG convergence time in the group")]
    
        lns = l + l2 + custom_lines
        labs = [l.get_label() for l in lns]
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        lgd = ax.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, ncol=2)

        ax.set_yscale("log")
        ax.set_ylabel("Centrality normalized (log scale)")
        ax.set_xlabel("Nodes ordered by the shortest hop distance \n by the source and by centrality")
        ax2.set_ylabel("Convergence time [s]")

        if limit is not None and limit > 0:
            ax2.set_ylim(0, limit)

        ax.set_zorder(2)
        ax2.set_zorder(1)
        ax.patch.set_visible(False)

        ax.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        ax2.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off

        fig.savefig(output_file_name.rsplit('.', 1)[0] + "_centVStime.pdf", format="pdf",
                    bbox_extra_artists=(lgd,), bbox_inches='tight')

        plt.close()

        fig, ax = plt.subplots()
        ax2 = ax.twinx()

        l = ax.plot(range(len(groups)), avg_centr, 'b', label="DPC centrality group trend")
        l2 = ax2.plot(range(len(groups)), avg_times, 'g', label="Convergence time group trend")

        lns = l + l2
        labs = [l.get_label() for l in lns]
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        lgd = ax.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, ncol=2)

        # ax.set_yscale("log")
        ax.set_ylabel("Centrality normalized")
        ax.set_xlabel("Hop distance groups")
        ax2.set_ylabel("Convergence time [s]")

        if limit is not None and limit > 0:
            ax2.set_ylim(0, limit)

        ax.set_zorder(2)
        ax2.set_zorder(1)
        ax.patch.set_visible(False)

        fig.savefig(output_file_name.rsplit('.', 1)[0] + "_centVStime_trend.pdf", format="pdf",
                    bbox_extra_artists=(lgd,), bbox_inches='tight')

        plt.close()
        
        return avg_times, avg_centr  

    def plot_centrality_vs_messages(self, output_file_name, hops, limit=None):

        fig, ax = plt.subplots()
        ax2 = ax.twinx()

        hops_centrality = [self.centrality[node] for node in hops.keys()]
        hops_conv_time = [self.df[self.df.node == int(node)].avg_in_messages.values[0] for node in hops.keys()]

        l = ax.plot(hops.keys(), hops_centrality, 'b', label="DPC centrality", zorder = 10, linewidth=0.7)
        l2 = ax2.plot(hops.keys(), hops_conv_time, 'purple', label="# In messages to converge", zorder = 3, linewidth=0.6)
        
        # Set the tick positions
        ax.set_xticks(list(hops.keys()))
    
        actual_dist = 0
        groups = [[]]
        for node in hops:
            if hops[node] > actual_dist:
                ax.axvline(x=str(node), color='orange', ls='--', zorder=5)
                actual_dist = hops[node]
                groups.append([])
            groups[-1].append(node)

        groups_limits = []
        for group in groups:
            groups_limits.append(group[0])

        avg_msg = []
        avg_centr = []
        for i in range(len(groups_limits)):
            group_avg_msg = self.df[self.df["node"].isin(groups[i])]["avg_in_messages"].mean()
            avg_msg.append(group_avg_msg)
            gr1 = groups_limits[i]

            avg_centrality = 0
            for node in groups[i]:
                avg_centrality += self.centrality[node]
            avg_centrality /= len(groups[i])
            avg_centr.append(avg_centrality)

            if i == len(groups_limits) -1:
                ax.hlines(y = avg_centrality, xmin = gr1, xmax = groups[i][-1], color="blue", ls='--', zorder=4)
                ax2.hlines(y = group_avg_msg, xmin = gr1, xmax = groups[i][-1], color="magenta", ls='--', zorder=4)
            else:
                ax.hlines(y = avg_centrality, xmin = gr1, xmax = groups_limits[i+1], color="blue", ls='--', zorder=4)
                ax2.hlines(y = group_avg_msg, xmin = gr1, xmax = groups_limits[i+1], color="magenta", ls='--', zorder=4)

        custom_lines = [Line2D([0], [0], color="orange", ls = '--', label = "Hop group separator"),
                        Line2D([0], [0], color="blue", ls = '--', label = "AVG centrality in the group"),
                        Line2D([0], [0], color="magenta", ls = '--', label = "AVG in messages in the group")]
    
        lns = l + l2 + custom_lines
        labs = [l.get_label() for l in lns]
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        lgd = ax.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, ncol=2)

        ax.set_yscale("log")
        ax.set_ylabel("Centrality normalized (log scale)")
        ax.set_xlabel("Nodes ordered by the shortest hop distance \n by the source and by centrality")
        ax2.set_ylabel("# Input messages necessary to converge")

        if limit is not None and limit > 0:
            ax2.set_ylim(ax2.get_ylim()[0], limit)

        ax.set_zorder(2)
        ax2.set_zorder(1)
        ax.patch.set_visible(False)

        ax.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        ax2.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off

        fig.savefig(output_file_name.rsplit('.', 1)[0] + "_centVSmsg.pdf", format="pdf",
                    bbox_extra_artists=(lgd,), bbox_inches='tight')

        plt.close()

        fig, ax = plt.subplots()
        ax2 = ax.twinx()

        l = ax.plot(range(len(groups)), avg_centr, 'b', label="DPC centrality group trend")
        l2 = ax2.plot(range(len(groups)), avg_msg, 'purple', label="Input messages group trend")

        lns = l + l2
        labs = [l.get_label() for l in lns]
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        lgd = ax.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, ncol=2)

        # ax.set_yscale("log")
        ax.set_ylabel("Centrality normalized")
        ax.set_xlabel("Hop distance groups")
        ax2.set_ylabel("Input messages to converge")

        if limit is not None and limit > 0:
            ax2.set_ylim(ax2.get_ylim()[0], limit)

        ax.set_zorder(2)
        ax2.set_zorder(1)
        ax.patch.set_visible(False)

        fig.savefig(output_file_name.rsplit('.', 1)[0] + "_centVSmsg_trend.pdf", format="pdf",
                    bbox_extra_artists=(lgd,), bbox_inches='tight')

        plt.close()

        return avg_msg 

class simple_plotter:
    
    def legends(lns, axes):
        labs = [l.get_label() for l in lns]
        # Shrink current axis's height by 10% on the bottom
        box = axes[0].get_position()
        for ax in axes:
            ax.set_position([box.x0, box.y0 + box.height * 0.15,
                             box.width, box.height * 0.9])
        # Put a legend below current axis
        lgd = axes[0].legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, ncol=2)
        return lgd
    
    def plot_line(x, y, color, label="label", ax=None, marker=None):
        l = ax.plot(x, y, color, label=label, marker=marker)
        return l
    
    def get_axes():
        fig, ax = plt.subplots()
        return (fig, ax)

    def ax_set_labels(ax, ylabel=None,xlabel=None, title=None):
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if title is not None:
            ax.set_title(title)
