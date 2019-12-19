# Fat Tree Generator
The Fat Tree Generator is a tool that allows to create arbitrary size single-plane Fat Tree
topologies and configure them to run on Kathará. 


## Prerequisites

- Python 3
- Docker
- Kathará (https://www.kathara.org/)

## Usage 

### Configure the topology 

The configuration of the topology is described in `config.json` file. 

```
{
  "protocol": "bgp",    
  "pod_num": 2,
  "pod": {
    "spine_num": [2,2],
    "leaf_num" : 2,
    "servers_for_rack": 1
  },
  "aggregation_layer": {
    "tof_num": [2]
  }
}
```
Parameters explanations: 

- `protocol`: 
    - `bgp` (uses the FRR implementation)
    - `open_fabric` (uses the FRR implementation)
    - `rift` (ZTP configuration) (uses the **rift-python** implementation
       of Bruno Rijsman https://github.com/brunorijsman/rift-python)
       
- `pod_num`: used to specify the number of pod in the Clos topology 

- `spine_num`: an array of int used to specify the number of spine on each
  level of the pod (`[2,2]` means that there are two level of spine, composed
   by two spines, for each pod). 

- `leaf_number`: used to specify the number of leaf for each pod 

- `servers_for_rack`: used to specify the number of servers for each leaf 
  (considered as Top of Rack)
  
- `tof_num`: an array of int used to specify the number of ToF on each level
  of the aggregation layer (`[2,2]` means that there are two level of ToF, composed
   by two ToF). 


### Run the tool 

In order to run the tool, type on terminal: 

```
$ ./main.py
```

After that a `lab` directory, with all the configurations files for 
Kathara, is created in the project folder. 
It also creates a `lab.json` file which contains all the information about
the topology and nodes. 

To run the lab, open a terminal in the root project folder and type: 

```
$ cd lab
$ sudo kathara lstart --privileged 
```

The `--privileged` flag is used to allow Kathará containers to use ECMP.

## Connect to a device

To connect to a specific device, run the following command from the `lab` directory:

```
$ kathara connect <machine_name>
```

This will open a shell into the machine `machine_name` root directory.

## Run RIFT protocol

In order to run RIFT protocol, it is required to build the corresponding Docker Image. 
To do so, run the following command (from the root directory of this project):

```
$ docker build -t kathara/rift-python .
```

## Node name's syntax

All the nodes in the lab have a name that depend on their type and their
position in the topology: 
- `server_<pod_number>_<server_number>`
- `leaf_<pod_number>_<level>_<leaf_number>` (level is always 0 for a leaf)
- `spine_<pod_number>_<level>_<spine_number>`
- `tof_<level>_<tof_number>`


## Topology information

It's possible to consult the `lab.json` file to know all the information on
topology and nodes. 
It's also possible to use the `get_ip.py` script to get the nodes IPs 
of the generated lab. 

To get all the IPs in the network type on terminal: 
```
$ ./get_ip.py
```

To get the IPs of a particular type of nodes type on terminal: 
```
$ ./get_ip.py type
```
Possible values for `type` param are: 
 - server
 - leaf
 - spine 
 - tof

