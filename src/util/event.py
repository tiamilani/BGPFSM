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

"""
event module
============

Module that handle events
-------------------------

This module is used to handle different elements
It is possible to create, modify and use events

Events types must be defined in the Events module

"""

class Event:
    """
    Defines the basic structure of an event
    """
    # counter used for assigning unique IDs to events
    event_counter = 0

    def __init__(self, event_duration, event_cause, event_type, source, # pylint: disable=too-many-arguments
                destination, obj=None, sent_time=None):
        """
        Creates an event.
        :param event_duration: time at which the event should be scheduled
        :param event_type: type of event
        :param event_cause: id of the event that caused this event
        :param destination: destination module that should be notified
        :param source: module generating the event
        :param obj: optional object to be attached to the event
        """
        self._event_id = Event.event_counter
        Event.event_counter += 1
        self._event_duration = event_duration
        self._event_type = event_type
        self._destination = destination
        self._source = source
        self._obj = obj
        self._sent_time = sent_time
        self._event_cause = event_cause

    def __eq__(self, other):
        if not isinstance(other, Event):
            return False
        if other.id == self.id:
            return True
        return False

    def __lt__(self, other):
        # if the event is the same, it is not lower than itself
        if other.id == self.id:
            return False
        if self.event_duration < other.event_duration:
            return True
        if self.event_duration > other.event_duration:
            return False
        # if the time is exactly the same, the one with the lower id is the
        # lowest of the two
        return self.id < other.id

    @property
    def id(self): # pylint: disable=invalid-name
        """
        Returns the event id
        """
        return self._event_id

    @id.setter
    def id(self, v): # pylint: disable=invalid-name
        self._event_id = v

    @property
    def event_duration(self):
        """
        Returns event time
        """
        return self._event_duration

    @event_duration.setter
    def event_duration(self, event_duration):
        """
        Set the event duration

        :param event_duration: Duration of the event
        """
        self._event_duration = event_duration

    @property
    def event_type(self):
        """
        Returns event type
        """
        return self._event_type

    @property
    def event_cause(self):
        """
        Returns event type
        """
        return self._event_cause

    @property
    def destination(self):
        """
        Returns event destination
        """
        return self._destination

    @property
    def source(self):
        """
        Returns event generator
        """
        return self._source

    @property
    def obj(self):
        """
        Returns the object attached to the event
        """
        return self._obj

    @obj.setter
    def obj(self, obj):
        """
        set the object attached to the event

        :param obj: object to set
        """
        self._obj = obj

    @property
    def sent_time(self):
        """
        Returns the sent time of the event if present
        """
        return self._sent_time

    def __str__(self):
        """
        Prints the event in a human readable format
        """
        res =  "Event time: {}\n".format(self.event_duration)
        res += "Event type: {}\n".format(self.event_type)
        res += "Source node: {}\n".format(self.source.id)
        res += "Destination node: {}\n".format(self.destination.id)
        return res
