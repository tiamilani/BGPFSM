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
from rib import BaseRib, ADJ_RIB_in, LOC_rib

class TestBaseRib():

    def test_base_rib_init(self):
        r = BaseRib()
        assert isinstance(r, BaseRib)

    def test_base_rib_len(self, base_rib, require_route):
        assert len(base_rib) == 0
        r = require_route("10.0.0.0/24") 
        base_rib.insert(r)
        assert len(base_rib) == 1

    def test_base_rib_get(self, base_rib, require_route):
        r = require_route("10.0.0.0/24")
        r.nh = "f"
        print(base_rib)
        assert len(base_rib[r]) == 1
        base_rib.insert(r)
        assert len(base_rib[r]) == 2
        assert isinstance(base_rib[r], list)

    def test_base_rib_get_keyerror(self, base_rib, require_route):
        r = require_route("20.0.0.0/24")
        with pytest.raises(KeyError):
            base_rib[r]

    def test_base_rib_del(self, populated_rib, require_route):
        assert len(populated_rib) == 3 
        route1 = require_route("10.0.0.0/24")
        del populated_rib[route1]
        assert len(populated_rib) == 2 

    def test_base_rib_del_keyerror(self, populated_rib, require_route):
        r = require_route("25.0.0.0/24")
        with pytest.raises(KeyError):
            del populated_rib[r]

    def test_base_rib_set(self, populated_rib, empty_rib, require_route):
        assert len(populated_rib) == 3 
        assert len(empty_rib) == 0
        route1 = require_route("10.0.0.0/24")
        empty_rib.insert(route1) 
        assert len(empty_rib) == 1 
        assert len(empty_rib[route1]) == 1 
        list_route1 = populated_rib[route1]
        empty_rib[route1] = list_route1
        assert len(empty_rib[route1]) == 3 

    def test_base_rib_set_keyerror(self, populated_rib, empty_rib, require_route):
        assert len(populated_rib) == 3 
        assert len(empty_rib) == 0
        route1 = require_route("10.0.0.0/24")
        route2 = require_route("20.0.0.0/24")
        empty_rib.insert(route1) 
        assert len(empty_rib) == 1 
        assert len(empty_rib[route1]) == 1 
        list_route2 = populated_rib[route2]
        with pytest.raises(KeyError):
            empty_rib[route2] = list_route2

    @pytest.mark.parametrize("addr, nh, contained", [
        ("10.0.0.0/24", "4", True),
        ("10.0.0.0/24", "5", True),
        ("10.0.0.0/24", "7", False)
    ])
    def test_base_rib_contains(self, populated_rib, require_route, addr, nh, contained):
        r = require_route(addr)
        r.nh = nh
        assert populated_rib.contains(r.addr, r) == contained

    def test_base_rib_contains_keyerror(self, populated_rib, require_route):
        r = require_route("100.0.0.0/24")
        with pytest.raises(KeyError):
            populated_rib.contains(r.addr, r)

    def test_base_rib_remove(self, populated_rib, require_route): 
        r = require_route("10.0.0.0/24")
        assert populated_rib.contains(r.addr, r)
        assert populated_rib.remove(r) == None
        assert not populated_rib.contains(r.addr, r)
        r2 = require_route("10.0.0.0/24")
        r2.nh = "27"
        assert not populated_rib.contains(r.addr, r)
        assert populated_rib.remove(r2) == r2 

    def test_base_rib_remove_keyerror(self, populated_rib, require_route):
        r = require_route("100.0.0.0/24")        
        with pytest.raises(KeyError):
            populated_rib.remove(r)

    def test_base_rib_insert(self, populated_rib, require_route):
        r = require_route("40.0.0.0/24")
        populated_rib.insert(r)
        assert len(populated_rib) == 4
        r2 = require_route("40.0.0.0/24")
        r2.nh = "f"
        assert len(populated_rib[r2]) == 1
        assert populated_rib.insert(r2) == r2
        assert len(populated_rib[r2]) == 2
        assert populated_rib.insert(r2) == None
        assert len(populated_rib[r2]) == 2
    
    def test_base_rib_iterator(self, populated_rib, require_route):
        r = require_route("40.0.0.0/24")
        for route_list in populated_rib:
            assert r not in route_list

    def test_base_rib_get_key(self, populated_rib, require_route):
        assert populated_rib.get_key(0) == require_route("10.0.0.0/24")
        assert populated_rib.get_key(5) == None

    def test_base_rib_str(self, populated_rib, populated_rib_str):
        assert str(populated_rib) == populated_rib_str

class TestADJRIBin():

    @pytest.mark.parametrize("node_id", ["1", "A", 5])
    @pytest.mark.parametrize("implicit_withdraw", [True, False])
    def test_adj_rib_in_init(self, node_id, implicit_withdraw):
        r = ADJ_RIB_in(node_id, implicit_withdraw)
        assert isinstance(r, ADJ_RIB_in)

    
    def test_adj_rib_in_len(self, base_adj_rib_in, require_route):
        assert len(base_adj_rib_in) == 0
        r = require_route("10.0.0.0/24") 
        base_adj_rib_in.insert(r)
        assert len(base_adj_rib_in) == 1

    def test_base_adj_rib_in_get(self, base_adj_rib_in, require_route):
        r = require_route("10.0.0.0/24")
        r.nh = "f"
        assert len(base_adj_rib_in[r]) == 1
        base_adj_rib_in.insert(r)
        assert len(base_adj_rib_in[r]) == 2
        assert isinstance(base_adj_rib_in[r], list)

    def test_base_adj_rib_in_get_keyerror(self, base_adj_rib_in, require_route):
        r = require_route("20.0.0.0/24")
        with pytest.raises(KeyError):
            base_adj_rib_in[r]
    
    def test_base_adj_rib_in_del(self, populated_adj_rib_in, require_route):
        assert len(populated_adj_rib_in) == 3 
        route1 = require_route("10.0.0.0/24")
        del populated_adj_rib_in[route1]
        assert len(populated_adj_rib_in) == 2 

    def test_base_adj_rib_in_del_keyerror(self, populated_adj_rib_in, require_route):
        r = require_route("25.0.0.0/24")
        with pytest.raises(KeyError):
            del populated_adj_rib_in[r]

    def test_base_adj_rib_in_set(self, populated_adj_rib_in, empty_adj_rib_in, require_route):
        assert len(populated_adj_rib_in) == 3 
        assert len(empty_adj_rib_in) == 0
        route1 = require_route("10.0.0.0/24")
        empty_adj_rib_in.insert(route1) 
        assert len(empty_adj_rib_in) == 1 
        assert len(empty_adj_rib_in[route1]) == 1 
        list_route1 = populated_adj_rib_in[route1]
        empty_adj_rib_in[route1] = list_route1
        assert len(empty_adj_rib_in[route1]) == 3 

    def test_base_adj_rib_in_set_keyerror(self, populated_adj_rib_in, empty_adj_rib_in, require_route):
        assert len(populated_adj_rib_in) == 3 
        assert len(empty_adj_rib_in) == 0
        route1 = require_route("10.0.0.0/24")
        route2 = require_route("20.0.0.0/24")
        empty_adj_rib_in.insert(route1) 
        assert len(empty_adj_rib_in) == 1 
        assert len(empty_adj_rib_in[route1]) == 1 
        list_route2 = populated_adj_rib_in[route2]
        with pytest.raises(KeyError):
            empty_adj_rib_in[route2] = list_route2

    
    @pytest.mark.parametrize("addr, nh, contained", [
        ("10.0.0.0/24", "4", True),
        ("10.0.0.0/24", "5", True),
        ("10.0.0.0/24", "7", False)
    ])
    def test_base_adj_rib_in_contains(self, populated_adj_rib_in, require_route, addr, nh, contained):
        r = require_route(addr)
        r.nh = nh
        assert populated_adj_rib_in.contains(r.addr, r) == contained

    def test_base_adj_rib_in_contains_keyerror(self, populated_adj_rib_in, require_route):
        r = require_route("100.0.0.0/24")
        with pytest.raises(KeyError):
            populated_adj_rib_in.contains(r.addr, r)

    def test_base_adj_rib_in_remove(self, populated_adj_rib_in, require_route):
        r = require_route("10.0.0.0/24")
        assert populated_adj_rib_in.contains(r.addr, r)
        assert populated_adj_rib_in.remove(r) == None
        assert not populated_adj_rib_in.contains(r.addr, r)
        r2 = require_route("10.0.0.0/24")
        r2.nh = "27"
        assert not populated_adj_rib_in.contains(r.addr, r)
        assert populated_adj_rib_in.remove(r2) == r2 

    def test_base_adj_rib_in_remove_keyerror(self, populated_adj_rib_in, require_route):
        r = require_route("100.0.0.0/24")        
        with pytest.raises(KeyError):
            populated_adj_rib_in.remove(r)

    def test_adj_rib_in_check(self, empty_adj_rib_in, require_route):
        r = require_route("10.0.0.0/24")
        assert empty_adj_rib_in.check(r) == None
        r = "hello world!:)"
        with pytest.raises(TypeError):
            empty_adj_rib_in.check(r)

    @pytest.mark.parametrize("addr, path, nh, loop", [
        ("100.0.0.0/24", ["A"], None, False),
        ("100.0.1.0/24", ["1", "2"], None, True),
        ("10.0.0.0/24", ["3", "1", "2"], None, True),
        ("10.0.0.0/24", ["a", "b", "1"], None, True),
        ("10.0.0.0/24", ["2", "a"], 10, False),
    ])
    def test_adj_rib_in_loop_detection(self, empty_adj_rib_in, addr, path, nh, loop):
        ipaddr = ipaddress.ip_network(addr)
        route = Route(ipaddr, path, nh)
        assert empty_adj_rib_in.filter(route) == loop

    def test_base_adj_rib_in_insert(self, populated_adj_rib_in, require_route, empty_adj_rib_in_noiw):
        r = require_route("40.0.0.0/24")
        populated_adj_rib_in.insert(r)
        empty_adj_rib_in_noiw.insert(r)
        assert len(populated_adj_rib_in) == 4
        assert len(empty_adj_rib_in_noiw) == 1
        r2 = require_route("40.0.0.0/24")
        r2.nh = "f"
        assert len(populated_adj_rib_in[r2]) == 1
        assert len(empty_adj_rib_in_noiw[r2]) == 1
        assert populated_adj_rib_in.insert(r2)[0] == r2
        assert empty_adj_rib_in_noiw.insert(r2)[0] == r2
        assert len(populated_adj_rib_in[r2]) == 2
        assert len(empty_adj_rib_in_noiw[r2]) == 2
        assert populated_adj_rib_in.insert(r2)[0] == r2
        assert empty_adj_rib_in_noiw.insert(r2)[0] == None
        assert len(empty_adj_rib_in_noiw[r2]) == 2
        ipaddr = ipaddress.ip_network("40.0.0.0/24")
        r2 = Route(ipaddr, [1,2,3], "K")
        assert populated_adj_rib_in.insert(r2)[0] == r2
        assert empty_adj_rib_in_noiw.insert(r2)[0] == r2
        assert len(populated_adj_rib_in[r2]) == 3
        assert len(empty_adj_rib_in_noiw[r2]) == 3
        ipaddr = ipaddress.ip_network("40.0.0.0/24")
        r2 = Route(ipaddr, [1,3], "K")
        assert populated_adj_rib_in.insert(r2)[0] == r2
        assert empty_adj_rib_in_noiw.insert(r2)[0] == r2
        assert len(populated_adj_rib_in[r2]) == 3
        assert len(empty_adj_rib_in_noiw[r2]) == 4
    
    def test_base_adj_rib_in_insert_loop(self, empty_adj_rib_in):
        ipaddr = ipaddress.ip_network("40.0.0.0/24")
        r2 = Route(ipaddr, ["1"], "K")
        assert empty_adj_rib_in.insert(r2)[0] == None

    def test_base_adj_rib_in_preference_ordering(self, empty_adj_rib_in):
        ipaddr = ipaddress.ip_network("40.0.0.0/24")
        r1 = Route(ipaddr, ["F"], "K")
        ipaddr = ipaddress.ip_network("40.0.0.0/24")
        r2 = Route(ipaddr, ["F", "2", "3"], "4")
        assert empty_adj_rib_in.insert(r2)[0] == r2
        assert empty_adj_rib_in.insert(r1)[0] == r1
        assert empty_adj_rib_in[r2][0] == r2
        empty_adj_rib_in.preference_ordering()
        assert empty_adj_rib_in[r2][0] == r1
    
    def test_base_adj_rib_in_iterator(self, populated_adj_rib_in, require_route):
        r = require_route("40.0.0.0/24")
        for route_list in populated_adj_rib_in:
            assert r not in route_list

    def test_base_adj_rib_in_get_key(self, populated_adj_rib_in, require_route):
        assert populated_adj_rib_in.get_key(0) == require_route("10.0.0.0/24")
        assert populated_adj_rib_in.get_key(5) == None

class TestLOCRIB():

    def test_loc_rib_init(self):
        rib = LOC_rib("1")
        assert isinstance(rib, LOC_rib)

    def test_loc_rib_insert(self, empty_loc_rib, require_route):
        r1 = require_route("100.0.0.0/24")
        r2 = require_route("200.0.0.0/24")
        empty_loc_rib.insert(r1)
        empty_loc_rib.insert(r2)
        assert len(empty_loc_rib) == 2
        assert isinstance(empty_loc_rib[r1], Route)
        assert empty_loc_rib[r1] == r1
        assert isinstance(empty_loc_rib[r2], Route)
        assert empty_loc_rib[r2] == r2
        assert empty_loc_rib.insert(r2) == None
        r3 = require_route("200.0.0.0/24")
        r3.nh = "3"
        empty_loc_rib.insert(r3)
        assert isinstance(empty_loc_rib[r3], Route)
        assert empty_loc_rib[r2] == r3

    def test_loc_rib_get_error(self, empty_loc_rib, require_route):
        r1 = require_route("100.0.0.0/24")
        with pytest.raises(KeyError):
            empty_loc_rib[r1]

