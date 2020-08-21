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

    def __init__(self, packet_type, content, id=None):
        """
        Creates a packet automatically assigning a unique ID to it
        :param packet_type: type of the packet 
        :param content: content of the packet 
        """
        if id == None:
            self._id = Packet.__packets_count
            Packet.__packets_count = Packet.__packets_count + 1
        else:
            self._id = id
        self._packet_type = packet_type
        self._content = content 

    @classmethod
    def fromString(cls, string):
        res = ast.literal_eval(string)
        return cls(res["type"], res["content"], id=res["id"])

    @property
    def id(self):
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
        d = dict()
        d["id"] = self.id
        d["type"] = self.packet_type
        d["content"] = str(self.content)
        res = str(d) 
        return res
