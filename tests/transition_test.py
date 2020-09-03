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
sys.path.insert(1, 'src/util')

from transition import Transition

class TestTransition():
    
    @pytest.mark.parametrize("s1, s2, inp, out, cnt, cnt_present", [
        ("1", "2", "A1", "A2", 1, False),
        ("1", "1", "A1", "A2", 1, False),
        ("1", "2", "A1", "A1", 1, False),
        ("1", "1", "A1", "A1", 1, False),
        ("1", "2", "A1", "A2", 20, True),
        ("1", "1", "A1", "A2", 30, True),
        ("1", "2", "A1", "A1", 50, True),
        ("1", "1", "A1", "A1", 40, True),
        ("1", "2", "A1", set(["A2"]), 1, False),
        ("1", "1", "A1", set(["A2"]), 1, False),
        ("1", "2", "A1", set(["A1", "W1"]), 1, False),
        ("1", "1", "A1", set(["A1", "W2"]), 1, False),
        ("1", "2", "A1", set(["A2"]), 20, True),
        ("1", "1", "A1", set(["A2"]), 30, True),
        ("1", "2", "A1", set(["A1"]), 50, True),
        ("1", "1", "A1", set(["A1"]), 40, True)
    ])
    def test_transition_init(self, s1, s2, inp, out, cnt, cnt_present):
        if not cnt_present:
            t = Transition(s1, s2, inp, out)
        else:
            t = Transition(s1, s2, inp, out, counter=cnt)
        
        assert t.init_state == s1
        assert t.output_state == s2
        assert t.input == inp
        assert t.output == out
        assert t.counter == cnt

    @pytest.mark.parametrize("s1, s2, inp, out, cnt", [
        ("1", "2", "A1", "A1", -50),
        ("1", "1", "A1", "A1", "40"),
    ])
    def test_transition_init_error(self, s1, s2, inp, out, cnt):
        with pytest.raises(ValueError):
            t = Transition(s1, s2, inp, out, cnt)

    @pytest.mark.parametrize("s1, s2, inp, out, cnt, s12, s22, inp2, out2, cnt2", [
        ("1", "2", "A1", "A2", 1, "1", "2", "A1", "A2", 1),
        ("1", "2", "W1", set(["A2"]), 1, "1", "2", "W1", set(["A2"]), 1),
        ("1", "2", "A1", "W2", 1, "1", "2", "A1", "W2", 1),
        ("1", "2", "A1", set(["A2", "W1"]), 10, "1", "2", "A1", set(["A2", "W1"]), 10),
        ("ABRACADABRA", "2", "A1", "A2", 1, "ABRACADABRA", "2", "A1", "A2", 1)
    ])
    def test_eq(self, s1, s2, inp, out, cnt, s12, s22, inp2, out2, cnt2):
        t = Transition(s1, s2, inp, out, cnt)
        t2 = Transition(s12, s22, inp2, out2, cnt2)
        
        assert t == t2

    @pytest.mark.parametrize("s1, s2, inp, out, cnt, s12, s22, inp2, out2, cnt2", [
        ("5", "2", "A1", "A2", 1, "1", "2", "A1", "A2", 1),
        ("1", "22", "W1", "A2", 1, "1", "2", "W1", "A2", 1),
        ("1", "2", "ABRA", "W2", 1, "1", "2", "A1", "W2", 1),
        ("1", "2", "A1", "CADABRA", 10, "1", "2", "A1", "A2", 10)
    ])
    def test_ne(self, s1, s2, inp, out, cnt, s12, s22, inp2, out2, cnt2):
        t = Transition(s1, s2, inp, out, cnt)
        t2 = Transition(s12, s22, inp2, out2, cnt2)
        
        assert t != t2

    @pytest.mark.parametrize("s1, s2, inp, out, cnt, s12, s22, inp2, out2, cnt2, equal", [
        ("1", "2", "A1", "A2", 1, "1", "2", "A1", "A2", 1, True),
        ("1", "2", "W1", "A2", 1, "1", "2", "W1", "A2", 1, True),
        ("1", "2", "A1", "W2", 1, "1", "2", "A1", "W2", 1, True),
        ("1", "2", "A1", "A2", 10, "1", "2", "A1", "A2", 10, True),
        ("ABRACADABRA", "2", "A1", "A2", 1, "ABRACADABRA", "2", "A1", "A2", 1, True),
        ("5", "2", "A1", "A2", 1, "1", "2", "A1", "A2", 1, False),
        ("1", "22", "W1", "A2", 1, "1", "2", "W1", "A2", 1, False),
        ("1", "2", "ABRA", "W2", 1, "1", "2", "A1", "W2", 1, False),
        ("1", "2", "A1", "CADABRA", 10, "1", "2", "A1", "A2", 10, False)
    ])
    def test_hash(self, s1, s2, inp, out, cnt, s12, s22, inp2, out2, cnt2, equal):
        t = Transition(s1, s2, inp, out, cnt)
        t2 = Transition(s12, s22, inp2, out2, cnt2)
        
        assert (hash(t) == hash(t2)) == equal

    @pytest.mark.parametrize("s1, s2, inp, out, cnt, expected_str", [
        ("1", "2", "A1", "A2", 1, "(1->2, A1:A2, 1)"),
        ("1", "1", "A1", "A2", 1, "(1->1, A1:A2, 1)"),
        ("1", "2", "A1", "A1", 1, "(1->2, A1:A1, 1)"),
        ("1", "1", "A1", "A1", 1, "(1->1, A1:A1, 1)"),
        ("1", "2", "A1", "A2", 20, "(1->2, A1:A2, 20)"),
        ("1", "1", "A1", "A2", 30, "(1->1, A1:A2, 30)"),
        ("1", "2", "A1", "A1", 50, "(1->2, A1:A1, 50)"),
        ("1", "1", "A1", "A1", 40, "(1->1, A1:A1, 40)"),
    ])
    def test_str(self, s1, s2, inp, out, cnt, expected_str):
        t = Transition(s1, s2, inp, out, counter=cnt)
        assert str(t) == expected_str

