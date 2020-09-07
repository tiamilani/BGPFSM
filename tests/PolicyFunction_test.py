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
import pytest
import math
import random
sys.path.insert(1, 'src/util')

from policies import PolicyFunction
from policies import PolicyValue

class TestPolicyFunction():
    
    @pytest.mark.parametrize("value", ["1, 2, 3", "3, 4, 6", "inf, inf, inf", 
        "1", "inf", PolicyFunction.PASS_EVERYTHING])
    def test_policy_functin_init(self, value):
        pf = PolicyFunction(value)
        assert id(pf) is not None

    @pytest.mark.parametrize("value", [None, 1, -1, set([1, 2]), 1.0])
    def test_policy_functin_init_typeerror(self, value):
        with pytest.raises(TypeError):
            pf = PolicyFunction(value)

    @pytest.mark.parametrize("value", ["", ''])
    def test_policy_functin_init_valueError(self, value):
        with pytest.raises(ValueError):
            pf = PolicyFunction(value)

    @pytest.mark.parametrize("value", ["1, 2, 3", "3, 4, 6", "inf, inf, inf", 
        "1", "inf"])
    def test_policy_functin_values_len(self, value):
        pf = PolicyFunction(value)
        values = pf.values
        assert len(values) == len(value.split(','))
        assert len(pf) == len(value.split(','))

    @pytest.mark.parametrize("value", ["1, 2, 3", "3, 4, 6", "inf, inf, inf", 
        "1", "inf", PolicyFunction.PASS_EVERYTHING])
    def test_policy_functin_values_getitem(self, value):
        pf = PolicyFunction(value)
        if value == PolicyFunction.PASS_EVERYTHING:
            rnd = random.randint(0, 150)
            assert pf[PolicyValue(rnd)].value == rnd
            return
        values = [x.strip() for x in value.split(',')]
        for i in range(len(values)):
            pv = PolicyValue.fromString(i)
            assert pf[pv] == PolicyValue.fromString(values[i])

    @pytest.mark.parametrize("value", ["1, 2, 3", "3, 4, 6", "inf, inf, inf", 
        "1", "inf"])
    @pytest.mark.parametrize("get", [None, 1, -1, set([1, 2]), 1.0])
    def test_policy_functin_values_getitem_error(self, value, get):
        pf = PolicyFunction(value)
        with pytest.raises(TypeError):
            tmp = pf[get]

    @pytest.mark.parametrize("value", ["1, 2, 3", "3, 4, 6", "inf, inf, inf", 
        "1", "inf"])
    def test_policy_functin_values_delitem(self, value):
        pf = PolicyFunction(value)
        values = [x.strip() for x in value.split(',')]
        for i in range(len(values)):
            pv = PolicyValue.fromString(i)
            del pf[pv]
            assert pf[pv] == PolicyValue.fromString(values[i])

    @pytest.mark.parametrize("value", ["1, 2, 3", "3, 4, 6", "inf, inf, inf", 
        "1", "inf"])
    def test_policy_functin_values_setitem(self, value):
        pf = PolicyFunction(value)
        values = [x.strip() for x in value.split(',')]
        for i in range(len(values)):
            pv = PolicyValue.fromString(i)
            pv_t = PolicyValue.fromString(0)
            pf[pv] = pv_t
            assert pf[pv] == PolicyValue.fromString(values[i])

    @pytest.mark.parametrize("value", ["1, 2, 3", "3, 4, 6", "inf, inf, inf", 
        "1", "inf"])
    @pytest.mark.parametrize("ins", ["1", 2, None, "inf", math.inf])
    def test_policy_functin_values_insert(self, value, ins):
        pf = PolicyFunction(value)
        pf.insert(ins)
        assert len(pf) == len(value.split(','))

    @pytest.mark.parametrize("value, expected_str", [
        ("1, 2, 3", "<1, 2, 3>"), 
        ("3, 4, 6", "<3, 4, 6>"), 
        ("inf, inf, inf", "<inf, inf, inf>"), 
        ("1", "<1>"), ("inf", "<inf>")])
    def test_policy_functin_values_str(self, value, expected_str):
        pf = PolicyFunction(value)
        assert str(pf) == expected_str

