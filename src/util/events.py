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
