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

"""
RFD module
============

Module used to configure and manage RFD
----------------------------

RFD is used to avoid route flaping through the damping 
of routes.
A route that flaps will be dammped after a certain ammount of flaps.
This process is decribed in RFC [2439]
It has been then updated with the RFC [7196]

This module goal is to have both implementation available

"""

import math

class RFD_conf():
    """RFD generic configuration
    used with only one type of values
    """

    def __init__(self, cut: float, reuse: float, t_hold: int, decay: int, 
                 decay_memory_limit: int, delta_t: int): # pylint: disable=too-many-arguments
        """__init__.
        
        :param cut: cutoff threshold
        :type cut: float
        :param reuse: reuse threshold
        :type reuse: float
        :param t_hold: maximum hold down timer
        :type t_hold: int
        :param decay: Decay half life while reachable
        :type decay: int
        :param decay_memory_limit: Decay memory limit, max history memory
        :type decay_memory_limit: int
        :param delta_t: time granularty for decay operations
        :type delta_t: int
        """

        self._cut = cut
        self._reuse = reuse
        self._t_hold = t_hold
        self._decay = decay
        self._decay_memory_limit = decay_memory_limit
        self._delta_t = delta_t

        # The formula is vague, so I will use the decay_ng
        self._ceiling = self._reuse * (math.exp(self._t_hold/self._decay) * math.log(2))
        self._decay_rate = math.exp((1/(self._decay/self._delta_t)) * math.log(1/2))
        self._decay_array_size = math.ceil(self._decay_memory_limit/self._delta_t)

        self._decay_array = []
        for i in range(self._decay_array_size):
            value = round(self._decay_rate ** i, 3)
            if value > 0:
                self._decay_array.append(value)
            else:
                self._decay_array_size = len(self._decay_array)
                break

    @property
    def delta_t(self) -> int:
        """
        delta_t.
        Returns the delta_t value used
        """
        return self._delta_t

    @property
    def ceiling(self) -> int:
        """
        ceiling.
        Returns the ceiling value used
        """
        return self._ceiling

    @property
    def decay(self) -> float:
        """
        decay.
        Returns the decay value used
        """
        return self._decay

    @property
    def decay_array_size(self) -> int:
        """
        decay_array_size.
        Returns the decay_array_size value used
        """
        return self._decay_array_size

    @property
    def decay_memory_limit(self) -> int:
        """
        decay_memory_limit.
        Returns the decay_memory_limit value used
        """
        return self._decay_memory_limit

    def decay_mult(self, i) -> int:
        """
        decay_mult.
        Returns the multiplier asscociated with an index in the decay array
        """
        return self._decay_array[i]

    def __str__(self):
        res = "Cut: {}\nReuse: {}\nT-hold: {}\nDecay: {}\n" 
        res += "Decay-memory-limit: {}\nDelta-t: {}\n"
        res += "Ceiling: {}\n".format(self._ceiling)
        res += "Decay-rate: {}\n".format(self._decay_rate)
        res += "Decay-array-size: {}\n".format(self._decay_array_size)
        res += "Decay-array: {}\n".format(self._decay_array)
        return res.format(self._cut, self._reuse,
                       self._t_hold, self._decay, self._decay_memory_limit,
                       self._delta_t)

class RFD_2438():
    """RFD_2439
    Class used to handle the RFD described in the RFC [2439]
    """

    def __init__(self, rfd_composed_string):
        rfd_composed_string = rfd_composed_string.replace(' ', '')
        splitted = rfd_composed_string.split(',')
        if len(splitted) != 11:
            raise ValueError(rfd_composed_string + 
                    "doesn't contains the expected parameters, 11 expected")
        self.initialize(float(splitted[0]),
                        float(splitted[1]),
                        float(splitted[2]),
                        float(splitted[3]),
                        float(splitted[4]),
                        int(splitted[5]),
                        int(splitted[6]),
                        int(splitted[7]),
                        int(splitted[8]),
                        int(splitted[9]),
                        int(splitted[10]))

    def initialize(self, w_penalty: float, ra_penalty: float, ac_penalty: float,
            cut: float, reuse: float, t_hold: int, decay_ok: int, 
            decay_ng: int, decay_memory_limit_ok: int, decay_memory_limit_ng: int, 
            delta_t: int): # pylint: disable=too-many-arguments
        """__init__.
        
        :param w_penalty: Penalty used in case of withdraws
        :type w_penalty: float
        :param ra_penalty: Penalty used in case of reannouncement 
        :type ra_penalty: float
        :param ac_penalty: Penalty used in case of attribute change 
        :type ac_penalty: float
        :param cut: cutoff threshold
        :type cut: float
        :param reuse: reuse threshold
        :type reuse: float
        :param t_hold: maximum hold down timer
        :type t_hold: int
        :param decay_ok: Decay half life while reachable
        :type decay_ok: int
        :param decay_ng: Decay half life while unreachable
        :type decay_ng: int
        :param decay_memory_limit_ok: Decay memory limit, max history memory
        :type decay_memory_limit_ok: int
        :param decay_memory_limit_ng: Decay memory limit, max history memory
        :type decay_memory_limit_ng: int
        :param delta_t: time granularty for decay operations
        :type delta_t: int
        """
        self._w_penalty = w_penalty
        self._ra_penalty = ra_penalty
        self._ac_penalty = ac_penalty
        self._cut = cut
        self._reuse = reuse
        self._t_hold = t_hold
        self.rfd_ok = RFD_conf(cut, reuse, t_hold, decay_ok, decay_memory_limit_ok, delta_t)
        self.rfd_ng = RFD_conf(cut, reuse, t_hold, decay_ng, decay_memory_limit_ng, delta_t)

    @property
    def cut(self):
        return self._cut

    @property
    def reuse(self):
        return self._reuse

    @property
    def t_hold(self):
        return self._t_hold

    @property
    def w_penalty(self):
        return self._w_penalty

    @property
    def ra_penalty(self):
        return self._ra_penalty

    @property
    def ac_penalty(self):
        return self._ac_penalty

    def __str__(self):
        res = "w_penalty: {}\nra_penalty: {}\nac_penalty: {}\n".format(self._w_penalty,
                self._ra_penalty, self._ac_penalty)
        res += "--------------------------\n"
        res += "{}\n------------------\n{}".format(self.rfd_ok, self.rfd_ng)
        return res
