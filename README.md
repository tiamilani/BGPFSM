# BGP as Finite State Machine

The software is composed by two separate programs:
* Discrete event simulator that emulates the behaviour of BGP
* Analyzer that produces the plots and graphs

## Installation

Is possible to install all the required libraries using the script inside the
`src` folder, use the following command:

`./install.sh`

## Requirements

A list of all the required libraries is available in the file: 
`scr/requirements.txt`

## BGP Discrete event simulations
Is possible to perform some discrete event simulations using this software.
The simulation goal is to spread the knowledge of some network to
the entire network.
The DES requires as input two files, a configuration file that describe
all the environment and a graphml file that present the network that should be
simulated.
Through this two levels of abstraction is possible to simulate different
BGP network behaviour.
The output is csv like file that describe the event evolution for each experiment

### Input of the software

#### JSON configuration file
To define environment variables is possible to use a `json` file that must be
passed to the DES.
An example of configuration file is available in: `/src/json/`

The parameters that can be defined inside the json file are:
* `seed`: this variable represent the seed that will be passed to the RNG at the
          environment initialization
* `duration`: Duration of each simulation in seconds
* `graph`: Graphml file that will be used for the simulation
* `output`: Represent the output file of the simulation. is possible to use
			other variables inside the string, for example `{date-time}` will
			be substituted by the actual dateTime of the experiment (up to ms)
			or is possible to use other variables like `{seed}` or `{withdraw_dist.min}`
			to introduce more levels of details to recognize the output csv file
			among many of a multi experiment script
* `verbose`: [True/False] variable, if true the experiment will print the evolution
			 on standard output
* `withdraw`: [True/False] variable, if true a node that previusly shared a network
			  it will produce a withdraw of the network after a delay time described
			  by `withdraw_dist`
* `reannouncement`: [True/False] variable, if true a node that previusly withdrawed
					a route will schedule a reannouncement of the route using the
					distribution described in `reannouncement_dist`
* `withdraw_dist`: Variable that describe a withdraw distribution, for distributions
				   handling explanation please see the next section
* `reannouncement_dist`: Like the withdraw distribution but for reannouncements
* `datarate`: {distribution} Time required to start the actual transmission of 
			  a message after the scheduling
* `processing`: {distribution} Processing time of any information, for example 
				can be used after the reception of a packet to simulate the processing of it
* `delay`: {distrbution} Network delay for the packets

All parameters can be array of parameters, so is possible to run different
combinations of simulations.

An array of parameters could be the following:

`seed: [0, 1, 2, 3]` -> this defines multiple seeds that can be used

`"withdraw_dist": [{"distribution": "unif", "min": 5, "max": 10, "int": 0.1},
				   {"distribution": "unif", "min": 8, "max": 10, "int": 0.1},
				   {"distribution": "unif", "min": 2, "max": 3, "int": 0.1}]
`

Example of an array of possible withdraw distributions

##### Distributions

Up to now the possible distributions that can be itroduced in the environment
are the following:
* Uniform: a uniform distribution will have like name `unif` and 3 parameters
		   `min` that represent the minimum value that can be choose `max`
		   the maximum value `int` that represent the precision used for all
		   the values between min and max, all parameters can be float values
* Exponential: an exponential distribution have like name `exp` and it has
			   a parameter `lambda`, like for the uniform distribution the
			   parameter can be a float value
* Constant: a constant distribution have like name: `const` and it has
			one parameter named `mean`

All the values of the distributions are intended in seconds.

An example of distribution:
`{"distribution": "const", "mean" : 0.00001}`

#### Graphml configuration file

The graphml file represent the graph that will be simulated.
It respect the graphml standard.
It is a directed graph.

Parameters that can be introduced in the nodes:
* `destinations`: this represent the networks that a node will share during
				  the experiment, it is possible to intrudce multiple networs
				  separated by a `,`

Parameters available for edges:
* `delay`: {distribution} is possible to introduce a delay distribution
		   for a single edge, the distribution has to respect what said in the
		   distribution section of the readme.
		   This parameter will override the json delay parameter for the edge
		   
example of graphml files are present on the `src/graphs` folder. 

### parameters

For example is possible to have more delay distributions and more seeds.
To show all the possible runs use the command '-l' or '-L'

Is also possible to define more sections inside the same config file.

The second input file, that will be pointed by the config file, is the graphml
file that describes the network to take in consideration.

For now the graphml file represent a direct graph with just the option of destinations.
The destinations option gives to a node the possibility to export some networks.
A node can export more destinations.
An example of graphml file is given under /src/graphs/

### Multiple experiments

Is possible to run multiple experiments thanks to the `multiple\_expriments.sh`
bash script.
Thanks to parallel [2] is possible to run multiple experiments in parallel.

Params:
* n: mandatory argument, it defines up to which run experiments shuld be run
	 (use fsm.py -l option to see how much run you have in your configuration
	 file)
* s: (default = simulation) Not mandatory argument, it describe which section
	 of the configuration file will be used during the experiments
* j: (default = 1) parallelization level, by default no parallelization, 
	 it defines the number of process that will be run simultaniously

Will be created a log file that register the STD output of each program in current
directory.

**FUTURE** Argument option to disable the cretion of the output file

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

[2] O. Tange (2011): GNU Parallel - The Command-Line Power Tool, ;login: The USENIX Magazine, February 2011:42-47
