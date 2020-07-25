#!/usr/bin/env python
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

from object import waiting_obj
import simpy
from object import Car
from object import random_interruption

# Environment creation
env = simpy.Environment()
# Buffer creation
bcs = simpy.Resource(env, capacity=2)
# Object and interrupter spawning
for i in range(4):
    obj = waiting_obj(env, "ev-{}".format(i), bcs)
    interrupter = random_interruption(env, obj)
# Execute the environment for at most 60 ticks
env.run(until=60)
