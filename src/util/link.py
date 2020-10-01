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
link module
===========

Module to handle links
----------------------

The goal of this module is to handle the links objects
The class link is able to transmit messages emulating delays

"""

from typing import Any
import json
from distribution import Distribution

from policies import PolicyValue, PolicyFunction

class Link:
    """
    Class defining a link between nodes
    this class contains properties for the link
    like delay or preference and link policy functions
    Every link have a unique id
    A single link can have a specific id
    """

    __link_counter = 0
    __waiter = 0.00001

    DELAY = "delay"
    POLICY_FUNCTION = "policy"
    MRAI = "mrai"

    def __init__(self, env, node, resource, properties):
        """
        Creates a link and automatically assign a uniqueid to the link
        It requires a simpy environment where to operate.
        It also require a simpy resource to operate correctly and
        reserve the channel for a message.

        :param env: Simpy environment
        :param node: Node which the link is refered to
        :param resource: unitary resource used to lock the link
        :param properties: properties of the link in the graphml that
            needs to be evaluated
        """
        self._id = Link.__link_counter
        Link.__link_counter += 1
        self._env = env
        self._node = node
        self._res = resource
        self._delay = None
        if Link.DELAY in properties:
            self._delay = Distribution(json.loads(properties[Link.DELAY]))
        if Link.POLICY_FUNCTION in properties:
            self._policy_function = PolicyFunction(properties[Link.POLICY_FUNCTION])
        else:
            self._policy_function = PolicyFunction(PolicyFunction.PASS_EVERYTHING)
        self._mrai = 30.0
        if Link.MRAI in properties:
            self._mrai = float(properties[Link.MRAI])
        self._mrai_active = False
        self._jitter = Distribution(json.loads('{"distribution": "unif", \
                       "min": 0, "max": ' + str(self._mrai*0.25)  + ', "int": 0.01}'))

    def _print(self, msg: str) -> None:
        """_print.
        Print helper function for the Link
        All messages will be preceded by the time, the link id and the neighbour
        connected

        :param msg: The message that needs to be printed by the link
        :type msg: str
        :rtype: None
        """
        if self._node.verbose:
            print("{}-Lid:{} to {} ".format(self._env.now, self._id, self._node.id) + msg)

    def transmit(self, msg: Any, delay: float) -> None:
        """
        Actual transmitting function

        :param msg: message that needs to be trasfered
        :param delay: time that needs to be waited before the message arrives
            to the destination
        """
        # Request of the unique resource, if the resource is available
        # it means the message is the first in the sequence of messages
        # that needs to be transfered
        # link:[----msg2----msg1+res--->dst]
        # Once a node have the resource and has waited for delay time it
        # can be delivered
        request = self._res.request()
        yield self._env.timeout(delay) & request
        self._print("Transmitting msg: " + str(msg.obj))
        self._node.event_store.put(msg)
        yield self._env.timeout(self.__waiter)
        self._res.release(request)

    def tx(self, msg, delay): # pylint: disable=invalid-name
        """
        Transmission function fot the node
        use this function to trigger a simpy process
        :param msg: message that needs to be transfered
        :param delay: delay that needs to be waited
        """
        self._env.process(self.transmit(msg, delay))

    def test(self, policy_value: PolicyValue) -> PolicyValue:
        """test.
        Test if a policy value is applicable to the policy function of the link

        :param policy_value: policy value to test
        :type policy_value: PolicyValue
        :rtype: PolicyValue
        """
        return self._policy_function[policy_value]

    @property
    def id(self): # pylint: disable=invalid-name
        """
        Returns the link id
        :returns: id of the link
        """
        return self._id

    @property
    def node(self):
        """
        Returns the referenced node
        :returns: node reference
        """
        return self._node

    @property
    def delay(self):
        """
        Returns the delay distribution that needs to be used
        for the link
        :returns: link delay distribution
        """
        return self._delay

    @property
    def mrai(self) -> float:
        """mrai.
        Function to get an MRAI value from the distribution
        If the MRAI is not active will be returned 0 and the MRAI will
        be activated
        For all the other iteration the MRAI will return a value equal
        to the value given minus the jitter

        :rtype: float
        """
        if not self.mrai_state:
            self._mrai_active = True
            return 0
        jitter = self._jitter.get_value()
        return self._mrai - jitter

    @property
    def mrai_state(self) -> bool:
        """mrai_state.
        Get the MRAI state value

        :rtype: bool
        """
        return self._mrai_active

    def mrai_not_active(self) -> None:
        """mrai_not_active.
        Disable the current MRAI
        if the MRAI was already disable this will have no effects

        :rtype: None
        """
        self._mrai_active = False

    def __str__(self):
        """
        Prints the link in a human readable format
        :returns: link in a string format
        """
        res = "id: {} ref_node: {}".format(self._id, self._node.id)
        return res
