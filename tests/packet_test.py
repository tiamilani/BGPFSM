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


import sys
import pytest
import ipaddress
sys.path.insert(1, 'src/util')

from packet import Packet
from route import Route

class TestPacket():
    
    @pytest.mark.parametrize("type_p, content, id_p, id_present, expected_id", [
        (Packet.UPDATE, "hello", None, False, 0),
        (Packet.WITHDRAW, "hello", None, False, 1),
        (Packet.UPDATE, 27, None, False, 2),
        (Packet.WITHDRAW, 27, None, False, 3),
        (Packet.UPDATE, "hello", 5, True, 5),
        (Packet.WITHDRAW, "hello", 25, True, 25),
        (Packet.UPDATE, 27, 5, True, 5),
        (Packet.WITHDRAW, 27, 25, True, 25)
    ])
    def test_packet_init(self, type_p, content, id_p, id_present, expected_id):
        if id_present:
            p = Packet(type_p, content, id=id_p)
        else:
            p = Packet(type_p, content)
        
        assert p.packet_type == type_p
        assert p.content == content
        assert p.id == expected_id

    @pytest.mark.parametrize("type_p, content, id_p, str_version", [
        (Packet.UPDATE, "hello", None, "{'id': 4, 'type': 0, 'content': 'hello'}"),
        (Packet.WITHDRAW, "hello", None, "{'id': 5, 'type': 1, 'content': 'hello'}"),
        (Packet.UPDATE, 27, None, "{'id': 6, 'type': 0, 'content': 27}"),
        (Packet.WITHDRAW, 27, None, "{'id': 7, 'type': 1, 'content': 27}"),
        (Packet.UPDATE, "hello", 5, "{'id': 5, 'type': 0, 'content': 'hello'}"),
        (Packet.WITHDRAW, "hello", 25, "{'id': 25, 'type': 1, 'content': 'hello'}"),
        (Packet.UPDATE, 27, 5, "{'id': 5, 'type': 0, 'content': 27}"),
        (Packet.WITHDRAW, 27, 25, "{'id': 25, 'type': 1, 'content': 27}")
    ])
    def test_packet_fromstr(self, type_p, content, id_p, str_version):
        p = Packet(type_p, content, id=id_p)
        p2 = Packet.fromString(str_version)

        assert p.packet_type == p2.packet_type
        assert p.content == p2.content
        assert p.id == p2.id

    @pytest.mark.parametrize("type_p, content, id_p", [
        (Packet.UPDATE, "hello", None),
        (Packet.WITHDRAW, "hello", None),
        (Packet.UPDATE, 27, None),
        (Packet.WITHDRAW, 27, None),
        (Packet.UPDATE, "hello", 5),
        (Packet.WITHDRAW, "hello", 25),
        (Packet.UPDATE, 27, 5),
        (Packet.WITHDRAW, 27, 25)
    ])
    def test_packet_setContent(self, type_p, content, id_p):
        p = Packet(type_p, content, id=id_p)
        ip_addr = ipaddress.ip_network("10.0.0.0/24")
        r = Route(ip_addr, [], "5")
        p.content = r
        
        assert str(p.content) == str(r)

    @pytest.mark.parametrize("type_p, content, id_p, id_present, expected_id", [
        (Packet.UPDATE, "hello", None, False, 12),
        (Packet.WITHDRAW, "hello", None, False, 13),
        (Packet.UPDATE, 27, None, False, 14),
        (Packet.WITHDRAW, 27, None, False, 15),
        (Packet.UPDATE, "hello", 5, True, 5),
        (Packet.WITHDRAW, "hello", 25, True, 25),
        (Packet.UPDATE, 27, 5, True, 5),
        (Packet.WITHDRAW, 27, 25, True, 25)
    ])
    def test_packet_str(self, type_p, content, id_p, id_present, expected_id):
        if id_present:
            p = Packet(type_p, content, id=id_p)
        else:
            p = Packet(type_p, content)
        
        d = dict()
        d["id"] = expected_id
        d["type"] = type_p
        d["content"] = str(content)
        res = str(d) 
        assert str(d) == str(p)
