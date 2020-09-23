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

    # Change state event
    STATE_CHANGE = 0
    # Transmission event
    TX = 1
    # Reception event
    RX = 2
    # New destination event
    NEW_DST = 3
    # Routing table change event
    RT_CHANGE = 4
    # New path for a destination event
    NEW_PATH = 5
    # Withdraw event
    WITHDRAW = 6
    # Reannouncement event
    REANNOUNCE = 7
    # Rib state change event
    RIB_CHANGE = 8
    # Introduction of a new Network
    DST_ADD = 9
    # Run the UPDATE_SEND_PROCESS
    UPDATE_SEND_PROCESS = 10
    # Share node destinations
    INTRODUCE_NETWORKS = 11
    # Retrieve node destinations
    REMOVE_NETWORKS = 12
    # MRAI timer events
    MRAI = 13
