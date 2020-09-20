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
Distribution module
===================

Used to manage different kind of distributions inside the des simulator
A distribution can be defined in the configuration file and the it will
be applicated.
The metod to get a value from a Distribution is indipendent from the
distribution itself, so the progrm that uses this librarary can avoid to take
in consideration special cases, an just pass the conf file value to the
module and get values.
"""

import random
import sys
import math


class Distribution: # pylint: disable=too-few-public-methods
    """
    Generic distribution class that implements different distributions depending
    on the parameters specified in a configuration
    """

    # distribution type field
    DISTRIBUTION = "distribution"
    # mean field
    MEAN = "mean"
    # lambda field
    LAMBDA = "lambda"
    # min field
    MIN = "min"
    # max field
    MAX = "max"
    # integer distribution field
    INT = "int"
    # constant random variable
    CONSTANT = "const"
    # uniform -f Random variable
    UNIFORM = "unif"
    # exponential random variable
    EXPONENTIAL = "exp"

    def __init__(self, config):
        """
        Instantiates the distribution
        :param config: an object used for configuring the distribution in the
        format {"distribution":NAME,"par1":value[,"par2":value,...]}.
        Accepted values so far are:
        {"distribution" : "const", "mean" : value}, constant variable
        {"distribution" : "exp", "mean" : value}, exponential random variable
        with mean being 1/lambda. "lambda" : value can also be used
        {"distribution" : "unif", "min" : value, "max" : value}, uniform -f Random
        variable between min and max
        """
        try:
            # find the correct distribution depending on the specified name
            if config[Distribution.DISTRIBUTION] == Distribution.CONSTANT:
                self.d = Const(config[Distribution.MEAN]) # pylint: disable=invalid-name
            elif config[Distribution.DISTRIBUTION] == Distribution.UNIFORM:
                integer = False
                try:
                    int_distribution = config[Distribution.INT]
                    if int_distribution == 1:
                        integer = True
                except Exception: # pylint: disable=broad-except
                    integer = False
                self.d = Uniform(config[Distribution.MIN],
                                 config[Distribution.MAX], integer)
            elif config[Distribution.DISTRIBUTION] == Distribution.EXPONENTIAL:
                integer = False
                try:
                    int_distribution = config[Distribution.INT]
                    if int_distribution == 1:
                        integer = True
                except Exception: # pylint: disable=broad-except
                    integer = False
                if Distribution.MEAN in config:
                    self.d = Exp(config[Distribution.MEAN], integer)
                else:
                    self.d = Exp(1.0/config[Distribution.LAMBDA], integer)
            else:
                print("Distribution error: unimplemented distribution %s",
                      config[Distribution.DISTRIBUTION])
        except Exception as e: # pylint: disable=broad-except,invalid-name
            print("Error while reading distribution parameters")
            print(e)
            sys.exit(1)

    def get_value(self):
        """
        get_value

        It retrives a value from the distribution initialized
        """
        return self.d.get_value()


class Const: # pylint: disable=too-few-public-methods
    """
    Constant random variable
    """

    def __init__(self, value):
        """
        Constructor
        :param value: returned constant value
        """
        self.value = value

    def get_value(self):
        """
        get_value

        Return the constant value defined
        """
        return self.value


class Uniform: # pylint: disable=too-few-public-methods
    """
    Uniform -f Random variable
    """

    def __init__(self, _min, _max, integer=False):
        """
        Constructor
        :param _min: _minimum value
        :param _max: _maximum value
        :param integer: whether to use integer or floating point numbers
        """
        self._min = _min
        self._max = _max
        self.integer = integer

    def get_value(self):
        """
        get_value

        Return a value from the uniform Distribution
        """
        value = random.uniform(self._min, self._max)
        if self.integer:
            return round(value)
        return value


class Exp: # pylint: disable=too-few-public-methods
    """
    Exponential random variable
    """

    def __init__(self, mean, integer=False):
        """
        Constructor
        :param mean: mean value (1/lambda)
        :param integer: if set to true, random values are discretized with ceil
        """
        self.l = 1.0/mean # pylint: disable=invalid-name
        self.integer = integer

    def get_value(self):
        """
        get_value

        Return a value from the uniform Distribution
        """
        if self.integer:
            return math.ceil(random.expovariate(self.l))
        return random.expovariate(self.l)
