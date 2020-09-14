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
Policies module
===============

Module used to handle policies and filters
------------------------------------------

The goal of this module is to make the use of policies easier
it is possible to use policy values and policy functions.
Values will be used inside policy functions.

A policy function detemines when a message will be transfered and
with which policy value associated

Example of policy function
>>> <0, inf, inf>

This policy function is used between clients and providers.
The function result is given by the position required.
For example

>>> f(0)=0
>>> f(1)=inf
>>> f(5)=inf
>>> f(inf)=inf

The input of the policy function is a policy value and the output of it
is a policy value itself.

Other than numbers the only value accepted by policy values is "inf"

"""


from copy import deepcopy
import collections
import math

class PolicyValue():
    """PolicyValue.
    Class used to handle policy values
    """


    def __init__(self, value):
        """__init__.

        :param value: Policy value to use
        """
        # Check that value is an integer and that is higher than 0
        if value != math.inf and value != -math.inf \
                and not isinstance(value, int):
            raise TypeError("The policy value should be integer or \
                            infinite, {} given".format(value))
        if value < 0:
            raise ValueError("The policy value must be higher than 0, \
                              {} < 0".format(value))
        self._value = value

    @classmethod
    def fromString(cls, string: str): # pylint: disable=invalid-name
        """fromString.

        :param string: String to transform in a policy value
        :type string: str
        :rtype: PolicyValue
        :return: Policy value converted from the string
        """
        return cls(math.inf) if string == "inf" else cls(int(string))

    @property
    def value(self):
        """value.

        :return: the policy value actually handling by the policy
        """
        return self._value

    @value.setter
    def value(self, value):
        """value.

        :param value: Value to substitute to the actual policy value
        :type value: int
        """
        if value != math.inf and value != -math.inf and not isinstance(value, int):
            raise TypeError(value)
        if value < 0:
            raise ValueError("The policy value must be higher than 0, \
                              {} < 0".format(value))
        self._value = value

    def __lt__(self, policy_value) -> bool:
        """__lt__.

        :param policy_value: Policy value to compare
        :type policy_value: PolicyValue
        :rtype: bool
        """
        return self.value < policy_value.value

    def __gt__(self, policy_value) -> bool:
        """__gt__.

        :param policy_value: Policy value to compare
        :type policy_value: PolicyValue
        :rtype: bool
        """
        return not self.__lt__(policy_value)

    def __eq__(self, policy_value) -> bool:
        """__eq__.

        :param policy_value: Policy value to compare
        :type policy_value: PolicyValue
        :rtype: bool
        """
        return self.value == policy_value.value

    def __ne__(self, policy_value) -> bool:
        """__ne__.

        :param policy_value: Policy value to compare
        :type policy_value: PolicyValue
        :rtype: bool
        """
        return not self.__eq__(policy_value)

    def __copy__(self):
        """__copy__.
        Copy of the actual policy value
        """
        return type(self)(self.value)

    def __deepcopy__(self, memo):
        """__deepcopy__.
        Deep copy of the actual policy value

        :param memo:
        """
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                    deepcopy(self.value, memo))
            memo[id_self] = _copy
        return _copy

    def __str__(self):
        """__str__.
        Return the policy value as a string
        """
        return str(self.value)

class PolicyFunction(collections.MutableSequence): # pylint: disable=too-many-ancestors
    """PolicyFunction.
    Class to handle policy functions
    """

    PASS_EVERYTHING = "pass-everything"

    def __init__(self, string):
        """__init__.

        :param string: String from which is possible to get the policy function
                        The string must be composed by valid policy values
                        'inf' will be substituted by math.inf
                        values must be separated by a ','
        """
        self._values = []

        if not isinstance(string, str):
            raise TypeError("{} is not of type str".format(string))
        if len(string) == 0:
            raise ValueError("{} is empty".format(string))

        if string == self.PASS_EVERYTHING:
            self._values = self.PASS_EVERYTHING
        else:
            for elem in string.split(','):
                elem = elem.strip()
                self._values.append(PolicyValue.fromString(elem))

    @property
    def values(self):
        """values.

        :return: the actual list of policy values that is composed the function
        """
        return self._values

    def __len__(self):
        """__len__.

        :return: the len of the policy function
        """
        return len(self.values)

    def __getitem__(self, i):
        """__getitem__.

        :param i: PolicyValue you would like to apply to the function
                  the function would return the policy value of f(i)
        """
        if self.values == self.PASS_EVERYTHING:
            return PolicyValue(i.value)
        if not isinstance(i, PolicyValue):
            raise TypeError("It is possible to get an item only with policy values \
                             {} is not a policy value".format(i))
        return self.values[i.value] if i.value < len(self.values) else PolicyValue(math.inf)

    def __delitem__(self, i):
        """__delitem__.
        This function has no effects
        :param i:
        """
        # An element of a policy function can't be deleted

    def __setitem__(self, i, v):
        """__setitem__.
        This function has no effects
        :param i:
        :param v:
        """
        # The policy function can't be modified

    def insert(self, v): # pylint: disable=arguments-differ
        """insert.
        This function has no effects
        :param i:
        """
        # The policy function can't be amplified

    def __str__(self):
        """__str__.
        Returns the policy function in a readable human format
        """
        res = "<"
        for elem in self.values[:-1]:
            res += str(elem) + ", "
        res += str(self.values[-1]) + ">"
        return res
