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

from route import Route
from routingTable import RoutingTable

class TestRoutingTable():
    
    def test_routing_table_init(self, empty_rt):
        rt = empty_rt
        assert isinstance(rt, RoutingTable)

    def test_routing_table_set(self, empty_rt, empty_route):
        rt = empty_rt
        route = empty_route
        rt[str(route)] = route
        assert id(rt[str(route)]) == id(route)

    @pytest.mark.parametrize("x", [0, 1, "1", "2", None, {'test': "test"}])
    def test_routing_table_set_error(self, empty_rt, x):
        rt = empty_rt
        with pytest.raises(TypeError):
            rt["test"] = x

    def test_routing_table_len(self, empty_rt, empty_route):
        rt = empty_rt
        route = empty_route
        print(rt)
        assert len(rt) == 0
        rt[str(route)] = route
        assert len(rt) == 1
        del rt[str(route)]
        assert len(rt) == 0
        rt[str(route)] = route
        rt[str(route)] = route
        rt[str(route)] = route
        assert len(rt) == 1

    @pytest.mark.parametrize("route, present", [
        ("10.0.0.0/24", True),
        ("20.0.0.0/24", True),
        ("30.0.0.0/24", True),
        ("40.0.0.0/24", False)
    ])
    def test_routing_table_get(self, rt_3, require_route, route, present):
        r = require_route(route)
        obtained = rt_3[str(r)]
        if present:
            assert r == obtained
        else:
            assert obtained == None

    @pytest.mark.parametrize("route, present", [
        ("10.0.0.0/24", True),
        ("20.0.0.0/24", True),
        ("30.0.0.0/24", True),
        ("40.0.0.0/24", False)
    ])
    def test_routing_table_del(self, rt_3, require_route, route, present):
        r = require_route(route)
        del rt_3[str(r)]
        if present:
            assert len(rt_3) == 2
        else:
            assert len(rt_3) == 3

    @pytest.mark.parametrize("route, present", [
        ("10.0.0.0/24", True),
        ("20.0.0.0/24", True),
        ("30.0.0.0/24", True),
        ("40.0.0.0/24", False)
    ])
    def test_routing_table_iter_str(self, rt_3, require_route, route, present):
        r = require_route(route)
        for route in rt_3:
            if route == r:
                assert str(route) == str(r)
                return
        assert rt_3[str(r)] == None

    def test_routing_table_str(self, rt_3, require_route):
        route1 = require_route("10.0.0.0/24")
        route2 = require_route("20.0.0.0/24")
        route3 = require_route("30.0.0.0/24")
        expected_str = "Routing Table:\n"
        expected_str += str(route1) + "\n"
        expected_str += str(route2) + "\n"
        expected_str += str(route3) + "\n"
        assert str(rt_3) == expected_str

