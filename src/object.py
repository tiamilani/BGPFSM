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

from random import randint
import simpy

# Example obj
def obj(env):
    """obj.

    :param env:
    """
    i = 0
    while i < 5:
        print("Start event at: {}".format(str(env.now)))
        event_duration = randint(0, 9)
        # Yeld returns a generator, pay attention to that
        yield env.timeout(event_duration)
        # Next time it is called code will resume from here
        # The generator will be used untill the function will
        # return nothing
        i += 1

# Object that have to generate an event and wait for a certain ammount of
# time before fulfilling it.
# All the parts of the object could be interrupted
# The waiting is based on the possession of a resource for a certain ammount
# of time.
class waiting_obj(object):
    """waiting_obj class"""


    def __init__(self, env, obj_id, buff):
        """__init__.

        :param env: simulation environment
        :param obj_id: object identifier, used on prints
        :param buff: buffer used for the waiting resources
        """
        self.env = env
        self.buff = buff
        self.id = obj_id
        # Set the action to execute the first env process of the execute function
        # This command will process the function passed in the current tick
        self.action = env.process(self.exe())

    def exe(self):
        """exe.
            Function that executes the object, it waits a certain ammount of time
            and then it execute the action that it requires a certain ammount of time
        """
        while True:

            print("{}-Start event {}".format(self.id, str(self.env.now)))
            event_waiting = randint(1,9)
            # Handling for the possible interruption
            try:
                yield self.env.process(self.waiting(event_waiting))
            except simpy.Interrupt:
                print("{}-Waiting event interrupted".format(self.id))

            print("{}-Event resumed {}".format(self.id, str(self.env.now)))
            event_termination = randint(1,9)
            try:
                yield self.env.timeout(event_termination)
                print("{}-Event terminated {}".format(self.id, str(self.env.now)))
            except simpy.Interrupt:
                print("{}-Termination of the event interrupted".format(self.id))

    def waiting(self, duration):
        """waiting.

        :param duration: How much time the resource must be handled to compleate
        the waiting
        """
        # Request to the buffer the resource
        with self.buff.request() as request:
            print("{}-requiring the waiting resource".format(self.id))
            yield request
            
            print("{}-The waiting resource is now awailable, waiting for {}s".format(
                    self.id, 
                    duration))
            yield self.env.timeout(duration)

class random_interruption(object):
    """random_interruption.
    Class for a random interrupter, this has the only goal to interrupt
    an object time to time"""


    def __init__(self, env, obj):
        """__init__.

        :param env: Environment where to act
        :param obj: Object to periodically interrupt
        """
        self.env = env
        self.obj = obj
        # Random interruption process queuing
        self.action = env.process(self.rnd_interrupt())

    def rnd_interrupt(self):
        """rnd_interrupt.
        It will constantly wait for a certain ammount of time and then interrupt
        the object"""
        while True:
            interruption = randint(9,19)
            # Waiting
            yield self.env.timeout(interruption)
            # Interruption
            self.obj.action.interrupt()

############# Example object form Simpy tutorial
class Car(object):
    """Car."""

    def __init__(self, env):
         """__init__.

         :param env:
         """
         self.env = env
         # Start the run process everytime an instance is created.
         self.action = env.process(self.run())

    def run(self):

         """run."""
         while True:
             print('Start parking and charging at %d' % self.env.now)
             charge_duration = 5
             # We yield the process that process() returns
             # to wait for it to finish
             yield self.env.process(self.charge(charge_duration))

             # The charge process has finished and
             # we can start driving again.
             print('Start driving at %d' % self.env.now)
             trip_duration = 2
             yield self.env.timeout(trip_duration)

    def charge(self, duration):
         """charge.

         :param duration:
         """
         yield self.env.timeout(duration)
