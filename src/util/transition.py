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

class Transition():

    def __init__(self, init_state, output_state, trigger_input, output):
        self.init_state = init_state
        self.output_state = output_state
        self.input = trigger_input
        self.output = output
        self.counter = 1

    def __eq__(self, obj):
        if str(self) == str(obj):
            return True
        return False

    def __ne__(self, obj):
        return not self == obj

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        res = "({}->{}, {}:{})".format(self.init_state, self.output_state,
                                       self.input, self.output)
        return res
