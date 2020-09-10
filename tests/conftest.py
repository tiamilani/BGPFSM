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

# @pytest.fixture(scope='session', autouse=True)
# def out_file(request):
#     tmp_out = tmpdir_factory.mktemp("logs").join("out.log")

"""
@pytest.fixture(scope='session', autouse=True)
def logger(request, out_file):
    logger = Log(out_file, log_routing_change=True,
                           log_rib_change=True,
                           log_packets=True,
                           log_paths=True,
                           log_states=True)
    return logger
"""

