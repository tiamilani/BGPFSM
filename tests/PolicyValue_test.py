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
sys.path.insert(1, 'src/util')

from policies import PolicyValue

class TestPolicyValue():
    
    @pytest.mark.parametrize("value", [0, 1, 2, 128, 2200, math.inf])
    def test_policy_value_init(self, value):
        pl = PolicyValue(value)
        assert id(pl) is not None

    @pytest.mark.parametrize("value", [None, "hello", 'test', set([1,2])])
    def test_policy_value_init_typeerror(self, value):
        with pytest.raises(TypeError):
            pl = PolicyValue(value)

    @pytest.mark.parametrize("value", [-1, -20, -250, -math.inf])
    def test_policy_value_init_valueerror(self, value):
        with pytest.raises(ValueError):
            pl = PolicyValue(value)

    @pytest.mark.parametrize("value", ["0", "1", "2", "128", "2200", "inf"])
    def test_policy_value_fromStr(self, value):
        pl = PolicyValue.fromString(value)
        assert id(pl) is not None
        assert isinstance(pl, PolicyValue)
        assert pl.value == int(value) if value != "inf" else math.inf

    @pytest.mark.parametrize("value", [0, 1, 2, 128, 2200, math.inf])
    def test_policy_value_value_getset(self, value):
        pl = PolicyValue(value)
        assert id(pl) is not None
        assert pl.value == value
        pl.value = value + 10
        assert pl.value == value + 10

    @pytest.mark.parametrize("value", [None, "hello", 'test', set([1,2])])
    def test_policy_value_getset_typeerror(self, value):
        with pytest.raises(TypeError):
            pl = PolicyValue(0)
            pl.value = value

    @pytest.mark.parametrize("value", [-1, -20, -250, -math.inf])
    def test_policy_value_getset_valueerror(self, value):
        with pytest.raises(ValueError):
            pl = PolicyValue(0)
            pl.value = value

    @pytest.mark.parametrize("value, test", [
        (0, 1), 
        (2, 128),
        (2, math.inf),
        (2200, 3000)])
    def test_policy_value_lt(self, value, test):
        pl = PolicyValue(value)
        test_pl = PolicyValue(test)
        assert pl < test_pl

    
    @pytest.mark.parametrize("value, test", [
        (0, 1), 
        (2, 128),
        (2, math.inf),
        (2200, 3000)])
    def test_policy_value_gt(self, value, test):
        pl = PolicyValue(test)
        test_pl = PolicyValue(value)
        assert pl > test_pl

    @pytest.mark.parametrize("value, test", [
        (0, 1), 
        (2, 128),
        (2, math.inf),
        (2200, 3000)])
    def test_policy_value_ne(self, value, test):
        pl = PolicyValue(test)
        test_pl = PolicyValue(value)
        assert pl != test_pl
    
    @pytest.mark.parametrize("value, test", [
        (0, 0), 
        (2, 2),
        (math.inf, math.inf),
        (2200, 2200)])
    def test_policy_value_eq(self, value, test):
        pl = PolicyValue(test)
        test_pl = PolicyValue(value)
        assert pl == test_pl

    @pytest.mark.parametrize("value", [0, 1, 2, 128, 2200, math.inf])
    def test_policy_value_copy(self, value):
        pl = PolicyValue(value)
        test = copy.copy(pl)
        assert not id(pl) == id(test)
        assert id(pl.value) == id(test.value)

    @pytest.mark.parametrize("value", [0, 1, 2, 128, 2200, math.inf])
    def test_policy_value_deepcopy(self, value):
        pl = PolicyValue(value)
        test = copy.deepcopy(pl)
        test.value = value + 100
        assert not id(pl) == id(test)
        assert id(pl.value) != id(test.value)

    @pytest.mark.parametrize("value, str_expected", [
        (0, "0"), 
        (1, "1"), 
        (2, "2"), 
        (128, "128"), 
        (2200, "2200"), 
        (math.inf, "inf")])
    def test_policy_value_str(self, value, str_expected):
        pl = PolicyValue(value)
        assert str(pl) == str_expected 
