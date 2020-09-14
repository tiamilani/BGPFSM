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
# Copyright (C) 2016 Michele Segata <segata@ccs-labs.org>

"""
Packet module
=============

Packet controller system
------------------------

In this module is possible to define different packets that will be used
during the simulation

For now a general packet could be an update ora withdraw

"""

import ast

class Packet:
    """
    Class defining a packet to be associated with a transmission event
    """

    # used to create a unique ID for the packet
    __packets_count = 0

    # Types of packets
    UPDATE = 0
    WITHDRAW = 1

    def __init__(self, packet_type, content, id_packet=None):
        """
        Creates a packet automatically assigning a unique ID to it
        :param packet_type: type of the packet
        :param content: content of the packet
        """
        if id_packet is None:
            self._id = Packet.__packets_count
            Packet.__packets_count = Packet.__packets_count + 1
        else:
            self._id = id_packet
        self._packet_type = packet_type
        self._content = content

    @classmethod
    def fromString(cls, string: str): # pylint: disable=invalid-name
        """fromString.
        Function to get the packet object from a string representation

        :param string: string to transform in a packet
        :rtype: Packet
        """
        res = ast.literal_eval(string)
        return cls(res["type"], res["content"], id_packet=res["id"])

    @property
    def id(self): # pylint: disable=invalid-name
        """
        Returns packet id
        :returns: id of the packet
        """
        return self._id

    @property
    def content(self):
        """
        Returns packet content
        :returns: content of the packet
        """
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    @property
    def packet_type(self):
        """
        Returns packet type
        :returns: the type of the packet defined at the initialization
        """
        return self._packet_type

    def __str__(self):
        """
        Prints the packet in a human readable format
        """
        string_dict = dict()
        string_dict["id"] = self.id
        string_dict["type"] = self.packet_type
        string_dict["content"] = str(self.content)
        res = str(string_dict)
        return res
