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

Events module
=============

Events has multiple possible types.
All events types are raggruped in this module
inside the class Events

"""

class Events: # pylint: disable=too-few-public-methods
    """
    Defines event types for the simulation
    """

    # process event
    PROCESS = 0
    # Transmission event
    TX = 1
    # Reception event
    RX = 2
    # Routing table change event
    RT_CHANGE = 3
    # New path for a destination event
    NEW_PATH = 4
    # Reannouncement event
    REANNOUNCE = 5
    # Rib state change event
    RIB_CHANGE = 6
    # Introduction of a new Network
    DST_ADD = 7
    # Run the UPDATE_SEND_PROCESS
    UPDATE_SEND_PROCESS = 8
    # Share node destinations
    INTRODUCE_NETWORKS = 9
    # Retrieve node destinations
    REMOVE_NETWORKS = 10
    # MRAI timer events
    MRAI = 11
    # start receptio event
    START_RX = 12
    # Start pkt evaluation
    START_PKT_EVAL = 13
    # End pkt evaluation
    END_PKT_EVAL = 14
    # Start tx event
    START_TX = 15
    # Start update send process
    START_UPDATE_SEND_PROCESS = 16
    # Route reusable event
    ROUTE_REUSABLE = 17
    # T-hold endup event
    END_T_HOLD = 18
    # Figure of merit changed
    FIGURE_OF_MERIT_VARIATION = 19
    # Route suppressed event
    ROUTE_SUPPRESSED = 20
