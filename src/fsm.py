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

"""
fsm module
==========

Use it to run descrete event simulations for protocols

:Example:

>>> python3 fsm.py -c json/config.json

Arguments
---------

Please refer to the help and the README for a mroe compleate explanation
of the arguments.

`--list` to get the list of available simulations with the configuration file
`--LIST` to have a compleate list of simulations with parameters
`-r` used to define which run will be executed
`-c` MANDATORY argument that defines which configuration file will be used
`-s` Defines the section of the configuration file to use, default: simulation

"""

import argparse
import sys
from bgp_sim import Sim

# setup command line parameters
parser = argparse.ArgumentParser(usage="usage: fsm [options]",
                      description="Runs a simulation configured in the "
                                  "specified config file under the specified "
                                  "section",
                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-l", "--list", dest="list", default=False,
                  action="store_true", help="list the available runs and exit")
parser.add_argument("-L", "--LIST", dest="verbose_list", default=False,
                  action="store_true", help="list the available runs with "
                                            "simulation parameters and exit")
parser.add_argument("-r", "--run", dest="run", default=0, action="store",
                  help="run simulation number RUN", type=int)
parser.add_argument("-c", "--config", dest="config", default="config.json",
                  action="store", help="simulation config file")
parser.add_argument("-s", "--section", dest="section", default="simulation",
                  action="store", help="section inside configuration file")
parser.add_argument("-g", "--graph", dest="graph", default="True",
                    action="store_false", help="Render the graph pdf of the \
                    graphml file with the policies")

if __name__ == "__main__":
    # Parse the arguments
    options = parser.parse_args()

    # Check the config and section to be setted
    if options.config == "" or options.section == "":
        print("Required parameters config and section missing")
        sys.exit(1)

    # Set the configuration
    simulation = Sim.Instance() # pylint: disable=no-member
    simulation.set_config(options.config, options.section)

    # list simulation runs and exit
    if options.list or options.verbose_list:
        runs_count = simulation.get_runs_count()
        for i in range(runs_count):
            if options.list:
                print("./fsm.py -c %s -s %s -r %d" %
                      (options.config, options.section, i))
            else:
                print("./fsm.py -c %s -s %s -r %d: %s" %
                      (options.config, options.section, i, simulation.get_params(i)))
        sys.exit(0)

    # Initialize the simulation
    simulation.initialize(options.run)
    # Run the simulation
    simulation.run()
    # Draw the graph
    if options.graph:
        simulation.plot_graph()
