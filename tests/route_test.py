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
import copy
import ipaddress
import pytest
sys.path.insert(1, 'src/util')

from route import Route
from policies import PolicyValue

class TestRoute():
    
    @pytest.mark.parametrize("addr, path, nh, policy_value", [
        ("100.0.0.0/24", [], None, 0),
        ("100.0.1.0/24", [1, 2], None, 0),
        ("10.0.0.0/24", [1, 2], None, 1),
        ("10.0.0.0/24", [], None, 26),
        ("10.0.0.0/24", [], 10, 14),
    ])
    def test_route_init(self, addr, path, nh, policy_value):
        ipaddr = ipaddress.ip_network(addr)
        pl = PolicyValue(policy_value)
        route = Route(ipaddr, path, nh, policy_value=pl)
        assert route.addr is ipaddr

    def test_route_init_nopl(self):
        ipaddr = ipaddress.ip_network("10.0.0.0/24")
        route = Route(ipaddr, [], None)
        assert route.policy_value.value == 0

    @pytest.mark.parametrize("addr", ["100.0.0.0/24", "10.0.0.0/24", "192.168.0.0/24"])
    @pytest.mark.parametrize("path", ["NoPath", None, 1, -1, [1, 2]])
    @pytest.mark.parametrize("nh", [None, 10])
    @pytest.mark.parametrize("pv", ["NoPolicy", None, 5, 128])
    def test_route_init_typeerror(self, addr, path, nh, pv):
        ipaddr = ipaddress.ip_network(addr)
        with pytest.raises(TypeError):
            route = Route(ipaddr, path, nh, policy_value=pv)

    @pytest.mark.parametrize("addr, path, nh", [
        ("100.0.0.0/24", [], None),
        ("100.0.1.0/24", [], None),
        ("10.0.0.0/24", [], None),
        ("10.0.0.0/8", [], None)
    ])
    def test_addr(self, addr, path, nh):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        assert route.addr is ipaddr

    @pytest.mark.parametrize("addr, path, nh", [
        ("100.0.0.0/24", [] ,None),
        ("100.0.1.0/24", [1, 2, 3], None),
        ("10.0.0.0/24", [3, 2, 1], None),
        ("10.0.0.0/8", ["1", "3", "3"], None)
    ])
    def test_path(self, addr, path, nh):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        assert route.path == path

    @pytest.mark.parametrize("addr, path, nh", [
        ("100.0.0.0/24", [] , None),
        ("100.0.1.0/24", [1, 2, 3], 1),
        ("10.0.0.0/24", [3, 2, 1], "1"),
        ("10.0.0.0/8", ["1", "3", "3"], "12556")
    ])
    def test_nh(self, addr, path, nh):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        assert route.nh is nh

    @pytest.mark.parametrize("addr, path, nh, new_nh", [
        ("100.0.0.0/24", [] , None, 1),
        ("100.0.1.0/24", [1, 2, 3], 1, 2),
        ("10.0.0.0/24", [3, 2, 1], "1", 6),
        ("10.0.0.0/8", ["1", "3", "3"], "12556", None)
    ])
    def test_nh_change(self, addr, path, nh, new_nh):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        route.nh = new_nh
        assert route.nh is new_nh
 
    @pytest.mark.parametrize("addr, path, nh, policy_value", [
        ("100.0.0.0/24", [], None, 0),
        ("100.0.1.0/24", [1, 2], None, 0),
        ("10.0.0.0/24", [1, 2], None, 1),
        ("10.0.0.0/24", [], None, 26),
        ("10.0.0.0/24", [], 10, 14),
    ])
    def test_policyvalue(self, addr, path, nh, policy_value):
        ipaddr = ipaddress.ip_network(addr)
        pl = PolicyValue(policy_value)
        route = Route(ipaddr, path, nh, policy_value=pl)
        assert route.policy_value.value == pl.value

    @pytest.mark.parametrize("addr, path, nh, policy_value", [
        ("100.0.0.0/24", [], None, 0),
        ("100.0.1.0/24", [1, 2], None, 0),
        ("10.0.0.0/24", [1, 2], None, 1),
        ("10.0.0.0/24", [], None, 26),
        ("10.0.0.0/24", [], 10, 14),
    ])
    def test_policyvalue_setter(self, addr, path, nh, policy_value):
        ipaddr = ipaddress.ip_network(addr)
        pl = PolicyValue(policy_value)
        route = Route(ipaddr, path, nh)
        assert route.policy_value.value == 0 
        route.policy_value = pl
        assert route.policy_value.value == pl.value
        assert id(route.policy_value) == id(pl)

    @pytest.mark.parametrize("addr, path, nh, policy_value, mine", [
        ("100.0.0.0/24", [], None, 0, True),
        ("100.0.1.0/24", [1, 2], None, 0, False),
        ("10.0.0.0/24", [1, 2], None, 1, True),
        ("10.0.0.0/24", [], None, 26, False),
        ("10.0.0.0/24", [], 10, 14, True),
    ])
    def test_mine(self, addr, path, nh, policy_value, mine):
        ipaddr = ipaddress.ip_network(addr)
        pv = PolicyValue(policy_value)
        route = Route(ipaddr, path, nh, policy_value=pv, mine=mine)
        assert route.mine == mine

    @pytest.mark.parametrize("addr, path, nh, new_as", [
        ("100.0.0.0/24", [] , None, 1),
        ("100.0.1.0/24", [1, 2, 3], 1, 4),
        ("10.0.0.0/24", [3, 2, 1], "1", "5"),
        ("10.0.0.0/8", ["1", "3", "3"], "12556", None)
    ])
    def test_path_add(self, addr, path, nh, new_as):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        route.add_to_path(new_as)
        path.insert(0, new_as)
        assert route.path == path
 
    @pytest.mark.parametrize("addr, path, nh, del_as, exception", [
        ("100.0.0.0/24", [] , None, 1, True),
        ("100.0.1.0/24", [1, 2, 3], 1, 1, False),
        ("10.0.0.0/24", [3, 2, 1], "1", 1, False),
        ("10.0.0.0/8", ["1", "3", "4"], "12556", "5", True)
    ])
    def test_path_remove(self, addr, path, nh, del_as, exception):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        if exception:
            with pytest.raises(ValueError):
                route.remove_from_path(del_as)
        else:
            path.remove(del_as)
            route.remove_from_path(del_as)
            assert route.path == path
 
    @pytest.mark.parametrize("addr, path, nh, str_version", [
        ("100.0.0.0/24", [] , None, "{'addr': '100.0.0.0/24', 'nh': None, \
                                      'path': [], 'policy_value': 0}"),
        ("100.0.1.0/24", [1, 2, 3], 1, "{'addr': '100.0.1.0/24', 'nh': 1, \
                                         'path': [1, 2, 3], 'policy_value': 0}"),
        ("10.0.0.0/24", [3, 2, 1], "1", "{'addr': '10.0.0.0/24', 'nh': '1', \
                                          'path': [3, 2, 1], 'policy_value': 0}"),
        ("10.0.0.0/8", ["1", "3", "4"], "12556", "{'addr': '10.0.0.0/8', \
                                                   'nh': '12556', \
                                                   'path': ['1', '3', '4'], \
                                                   'policy_value': 0}")
    ])
    def test_fromString(self, addr, path, nh, str_version):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        route_str = Route.fromString(str_version)
        assert route == Route.fromString(str(route))
        assert route == route_str

    @pytest.mark.parametrize("route1, route2, lt_1", [
        ("{'addr': '100.0.0.0/24', 'nh': 2, 'path': [2], 'policy_value': 0}",
         "{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 1}", 
         True),
        ("{'addr': '100.0.0.0/24', 'nh': 2, 'path': [2], 'policy_value': 1}",
         "{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 0}", 
         False),
        ("{'addr': '100.0.0.0/24', 'nh': 2, 'path': [2], 'policy_value': 0}",
         "{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 0}", True),
        ("{'addr': '100.0.1.0/24', 'nh': 1, 'path': [1, 2, 3], 'policy_value': 0}", 
         "{'addr': '100.0.1.0/24', 'nh': 1, 'path': [1, 2, 3, 4], 'policy_value': 0}", True),
        ("{'addr': '100.0.1.0/24', 'nh': 1, 'path': [1, 3], 'policy_value': 0}", 
         "{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 3], 'policy_value': 0}", True),
        ("{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 4, 3], 'policy_value': 0}", 
         "{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 5, 3], 'policy_value': 0}", True),
        ("{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 6, 3], 'policy_value': 0}", 
         "{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 5, 3], 'policy_value': 0}", False),
        ("{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 6, 3, 28], 'policy_value': 0}", 
         "{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 5, 3], 'policy_value': 0}", False),
    ])
    def test_lt(self, route1, route2, lt_1):
        route1 = Route.fromString(route1)
        route2 = Route.fromString(route2)
        if lt_1:
            assert route1 < route2
        else:
            assert not (route1 < route2)

    @pytest.mark.parametrize("route1, route2, result", [
        ("{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 0}",
         "{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 1}",
         False),
        ("{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 1}",
         "{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 1}",
         True),
        ("{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 0}",
         "{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 0}",
         True),
        ("{'addr': '100.0.1.0/24', 'nh': 1, 'path': [1, 2, 3, 4], 'policy_value': 0}", 
         "{'addr': '100.0.1.0/24', 'nh': 1, 'path': [1, 2, 3, 4], 'policy_value': 0}",
         True),
        ("{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 6, 3], 'policy_value': 0}", 
         "{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 5, 3], 'policy_value': 0}",
         False),
    ])
    def test_eq(self, route1, route2, result):
        route1 = Route.fromString(route1)
        route2 = Route.fromString(route2)
        if result:
            assert route1 == route2
        else:
            assert not (route1 == route2)

    @pytest.mark.parametrize("route1", [
        ("{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 0}"),
        ("{'addr': '100.0.1.0/24', 'nh': 1, 'path': [1, 2, 3, 4], 'policy_value': 1}"),
        ("{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 6, 3], 'policy_value': 2}")
    ])
    def test_copy(self, route1):
        route = Route.fromString(route1)
        route_copy = copy.copy(route)
        assert not id(route) == id(route_copy)
        assert id(route.addr) == id(route_copy.addr)
        assert id(route.nh) == id(route_copy.nh)
        assert id(route.policy_value) == id(route_copy.policy_value)

    @pytest.mark.parametrize("route1", [
        ("{'addr': '100.0.0.0/24', 'nh': 1, 'path': [1, 2], 'policy_value': 0}"),
        ("{'addr': '100.0.1.0/24', 'nh': 1, 'path': [1, 2, 3, 4], 'policy_value': 1}"),
        ("{'addr': '100.0.1.0/24', 'nh': 2, 'path': [2, 6, 3], 'policy_value': 2}")
    ])
    def test_deepcopy(self, route1):
        route = Route.fromString(route1)
        route_copy = copy.deepcopy(route)
        assert not id(route) == id(route_copy)
        assert not id(route.addr) == id(route_copy.addr)
        assert not id(route.path) == id(route_copy.path)
        assert not id(route.policy_value) == id(route_copy.policy_value)
        route_copy.nh=150
        assert route.nh != route_copy.nh

