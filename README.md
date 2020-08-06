# BGP as Finite State Machine

## BGP Discrete event simulations
Is possible to perform some discrete event simulations using this software.
The simulation goal is to spread the knowledge of some destinations to
the entire network.

## Requirements

All this libraries should be installable through pip, pip install [library name]
If not pre installed

* sys
* simpy
* time
* random
* networkx 
* optparse
* ipaddress
* copy
* math
* json
* re
* collections

## Input of the software
The input of the software is a configuration file wirtten in json
An example of configuration file is in /src/json/

This fille represent the environment of the simulation.

All parameters can be array of parameters, so is possible to run different
combinations of simulations.
For example is possible to have more delay distributions and more seeds.
To show all the possible runs use the command '-l' or '-L'

Is also possible to define more sections inside the same config file.

The second input file, that will be pointed by the config file, is the graphml
file that describes the network to take in consideration.

For now the graphml file represent a direct graph with just the option of destinations.
The destinations option gives to a node the possibility to export some networks.
A node can export more destinations.
An example of graphml file is given under /src/graphs/

## Ouptut

The software can give two different outputs.
If in the config file the verbose option is active there will be a plain text
printed during the simulation.

The main output of the simulation is in the csv file that will be created
by the software.
The name of the csv output can be configured in the config file and depend
on the run choosen.

The csv file have the following attributes:
* event, this element represent the event which the row referes
* time, this element give the simulation time when the event happened
* node, this element represent which node have triggered the event
* value, this is a variable field, the content of the field depend on the event,
if the event was a routing table change will contain the new route, if it was a
packet reception/transmission will contain the packet representation

Events:
* 0 -> state changed, the value will contain the new state of the node
* 1 -> Transmission event, the value field will contain the packet transmitted
* 2 -> Reception event, the value field will contain the packet transmitted
* 3 -> New destination, a new destination is inserted in the node and needs to be shared
* 4 -> Routing table change, the value field will contain the new route

## Usage

To run a simple experiment try the following command with the example config file
and the example graphml file.

'python3 fsm.py -c json/config.json'

If you run the command with also the '-l' option you will see that there are
multiple run that can be used.
This because the software will create all the possible combination of
parameters that are in the configuration file (all parameters that are vectors
will modify the number of runs)

The example config file will give the possibility to execute 10 different runs
based on 10 different seeds, it's the only parameter that is a vector.

In the output of the '-l' arg there is also a '-s' argument.
This argument represent the section that will be taken in consideration 
in the config.json file, in the example config file there is just one
section.

If you want a more compleate view of what parameters are used in which run
you can use the '-L' command, always with the config file that is taken in
consideration.
This command other than the run number will show also the parameters that will
be used for each specific run.

## Discrete event simulation

All the times inside the simulation are controlled by distributions that
are defined inside the config file.

When a node have to process some information (the reception of a new route)
will wait some time, to simulate a processing unit.

When a node have to send a message it will use the tx\_pkt function.
This function given the packet and the destination node will
put the reception event in the queue of the destination node with the packet
as object.
The delay of the packet transmission is calculated by the transmitter

At the reception of a packet the receiver will evaluate the new route
if the route is not in it's routing table it will put the route in it and advise
all it's neighbors (except the next hop).
If the route was already in the Routing table it will evaluate which route is
the best and it will keep only the better one.
Tie are broken using the length of the path and the next hop id.

FUTURE: it will be included the possibility to keep in memory paths that are
not the best, so it will be possible on a withdraw to fall back on an already
known path.

### References

[1] A Finite State Model Update Propagation for Hard-State Path-Vector Protocols
present in Biblio/FSM\_model.pdf
