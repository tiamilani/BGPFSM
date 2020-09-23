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
from rib import BaseRib, ADJ_RIB_in, LOC_rib
# from log import Log


@pytest.fixture(scope='function', autouse=True)
def empty_route(request):
    ip_addr = ipaddress.ip_network("10.0.0.0/24")
    return Route(ip_addr, [], None)

@pytest.fixture(scope='function', autouse=True)
def require_route(request):
    def _require_route(addr):
        ip_addr = ipaddress.ip_network(addr)
        return Route(ip_addr, [], None)
    
    return _require_route

@pytest.fixture(scope='function', autouse=True)
def empty_rt(request):
    return RoutingTable()

@pytest.fixture(scope='function', autouse=True)
def rt_3(request, require_route):
    rt = RoutingTable()
    route1 = require_route("10.0.0.0/24")
    route2 = require_route("20.0.0.0/24")
    route3 = require_route("30.0.0.0/24")
    rt[str(route1)] = route1
    rt[str(route2)] = route2
    rt[str(route3)] = route3
    return rt

@pytest.fixture(scope='session', autouse=True)
def base_rib(request):
    r = BaseRib()
    return r

@pytest.fixture(scope='function', autouse=True)
def empty_rib(request):
    r = BaseRib()
    return r

@pytest.fixture(scope='function', autouse=True)
def populated_rib(request, require_route):
    r = BaseRib()
    route1 = require_route("10.0.0.0/24")
    route2 = require_route("20.0.0.0/24")
    route3 = require_route("30.0.0.0/24")
    route4 = require_route("10.0.0.0/24")
    route5 = require_route("20.0.0.0/24")
    route6 = require_route("30.0.0.0/24")
    route7 = require_route("10.0.0.0/24")
    route8 = require_route("20.0.0.0/24")
    route9 = require_route("30.0.0.0/24")
    route4.nh = "4"
    route5.nh = "4"
    route6.nh = "4"
    route7.nh = "5"
    route8.nh = "6"
    route9.nh = "7"
    r.insert(route1)
    r.insert(route2)
    r.insert(route3)
    r.insert(route4)
    r.insert(route5)
    r.insert(route6)
    r.insert(route7)
    r.insert(route8)
    r.insert(route9)
    return r

@pytest.fixture(scope='function', autouse=True)
def populated_rib_str(request, populated_rib):
    res = ""
    res += """["{'addr': '30.0.0.0/24', 'nh': None, 'path': [], 'policy_value': '0'}", "{'addr': '30.0.0.0/24', 'nh': '4', 'path': [], 'policy_value': '0'}", "{'addr': '30.0.0.0/24', 'nh': '7', 'path': [], 'policy_value': '0'}"]""" + "\n"
    res += """["{'addr': '20.0.0.0/24', 'nh': None, 'path': [], 'policy_value': '0'}", "{'addr': '20.0.0.0/24', 'nh': '4', 'path': [], 'policy_value': '0'}", "{'addr': '20.0.0.0/24', 'nh': '6', 'path': [], 'policy_value': '0'}"]""" + "\n"
    res += """["{'addr': '10.0.0.0/24', 'nh': None, 'path': [], 'policy_value': '0'}", "{'addr': '10.0.0.0/24', 'nh': '4', 'path': [], 'policy_value': '0'}", "{'addr': '10.0.0.0/24', 'nh': '5', 'path': [], 'policy_value': '0'}"]""" + "\n"
    return res

@pytest.fixture(scope='session', autouse=True)
def base_adj_rib_in(request):
    r = ADJ_RIB_in("1", True)
    return r

@pytest.fixture(scope='function', autouse=True)
def empty_adj_rib_in(request):
    r = ADJ_RIB_in("1", True)
    return r

@pytest.fixture(scope='function', autouse=True)
def empty_adj_rib_in_noiw(request):
    r = ADJ_RIB_in("1", False)
    return r

@pytest.fixture(scope='function', autouse=True)
def populated_adj_rib_in(request, require_route):
    r = ADJ_RIB_in("1", True)
    route1 = require_route("10.0.0.0/24")
    route2 = require_route("20.0.0.0/24")
    route3 = require_route("30.0.0.0/24")
    route4 = require_route("10.0.0.0/24")
    route5 = require_route("20.0.0.0/24")
    route6 = require_route("30.0.0.0/24")
    route7 = require_route("10.0.0.0/24")
    route8 = require_route("20.0.0.0/24")
    route9 = require_route("30.0.0.0/24")
    route4.nh = "4"
    route5.nh = "4"
    route6.nh = "4"
    route7.nh = "5"
    route8.nh = "6"
    route9.nh = "7"
    r.insert(route1)
    r.insert(route2)
    r.insert(route3)
    r.insert(route4)
    r.insert(route5)
    r.insert(route6)
    r.insert(route7)
    r.insert(route8)
    r.insert(route9)
    return r

@pytest.fixture(scope='function', autouse=True)
def empty_loc_rib(request):
    r = LOC_rib("1")
    return r

# @pytest.fixture(scope='session', autouse=True)
# def out_file(request):
#     tmp_out = tmpdir_factory.mktemp("logs").join("out.log")
