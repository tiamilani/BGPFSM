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
# Copyright (C) 2016 Michele Segata <segata@ccs-labs.org>

from distribution import Distribution
import json
import simpy

from policies import PolicyFunction

class Link:
    """
    Class defining a link between nodes
    this class contains properties for the link
    like delay or preference
    """

    __link_counter = 0
    __waiter = 0.00001

    DELAY = "delay"
    POLICY_FUNCTION = "policy"

    def __init__(self, env, node, resource, properties):
        """
        Creates a link automatically assign a uniqueid to the link
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

    def transmit(self, msg, delay):
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
        self._node._print("resource obtained, inserting msg: " + str(msg.obj))
        self._node.event_store.put(msg)
        yield self._env.timeout(self.__waiter)
        self._node._print("resource releasing")
        self._res.release(request)
        
    def tx(self, msg, delay):
        """
        Transmission function fot the node
        use this function to trigger a simpy process
        :param msg: message that needs to be transfered
        :param delay: delay that needs to be waited
        """
        self._env.process(self.transmit(msg, delay))

    def test(self, pl):
        return self._policy_function[pl]

    @property
    def id(self):
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

    def __str__(self):
        """
        Prints the link in a human readable format
        :returns: link in a string format
        """
        res = "id: {} ref_node: {}".format(self._id, self._node.id)
        return res
