# Fat Tree Generator
The Fat Tree Generator is a tool that allows to create three levels Fat Tree
topologies (single-plane or multi-planes) and configure them to run on Kathará. 

**N.B. :** until now only three-level architectures are possible.

**N.B. :** _Katharà_ works well on Linux, Windows and MacOS, but due to Docker limitations not all the functionalities
are available on non-Linux platform (i.e. ECMP).


## Prerequisites

- Python 3
- Docker
- Kathará (https://www.kathara.org/)

## Usage 

### Build a topology 

The parameters to build a topology are in `config.json` file.

```
{
  "k_leaf": 4,
  "k_top": 4,
  "redundancy_factor": 2,
  "servers_for_rack": 1,
  "protocol": "bgp"
}
```
Parameters explanations: 

- `k_leaf`: the number of ports of a leaf node pointing north or south

- `k_top`: the number of ports of a spine node pointing north or south

- `redundancy_factor`: the number of connections from a ToF node to a PoD

- `servers_for_rack`: used to specify the number of servers for each leaf 
  (considered as Top of Rack)

- `protocol`: 
    - `bgp` (uses the FRR implementation)
    - `open_fabric` (uses the FRR implementation)
    - `rift` (ZTP configuration) (uses the **rift-python** implementation
       of Bruno Rijsman https://github.com/brunorijsman/rift-python)
       
The topology is built using the following parameters and formulas: 
- input parameters:
```
    k_leaf
    k_top
    redundancy_factor (R)
    servers_for_rack
```
- output parameters: 
``` 
    number_of_planes = k_leaf/R
    number_of_pod = (k_leaf+k_top)/r
    number_of_spine_per_pod = k_leaf
    number_of_leaf_per_pod = k_top
    number_of_tof_for_plane = k_top
    servers_for_rack =  servers_for_rack
       
```
       
       
### Run the tool 

In order to run the tool, type on terminal: 

```
$ python3 main.py
```

After that a `lab` directory, with all the configurations files for 
Kathara, is created in the project folder. 

It also creates an `output` folder containing two files:
- the `lab.json`: which contains all the information about
the topology and the nodes;
- the `topology_info.json`: which contains a schematic view of the built topology. 

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

#### `topology_info.json`

The `output\topology_info.json` file contains all the parameters of the built topology: 
```
{
    "aggregation_layer": {
        "number_of_planes": 2,
        "tofs_for_plane": 4
    },
    "k_leaf": 4,
    "k_top": 4,
    "number_of_pods": 4,
    "pod": {
        "leafs_for_pod": 4,
        "servers_for_rack": 1,
        "spines_for_level": [
            4
        ]
    },
    "protocol": "bgp",
    "redundancy_factor": 2
}
```

Parameters explanation: 
- `number_of_pods`: used to specify the number of pod in the Clos topology 

- `spines_for_level`: an array of int used to specify the number of spine on each
  level of the pod (`[2,2]` means that there are two level of spine, composed
   by two spines, for each pod). 

- `leafs_for_pod`: used to specify the number of leaf for each pod 

- `servers_for_rack`: used to specify the number of servers for each leaf 
  (considered as Top of Rack)

- `number_of_planes`: the number of planes in the fabric
  
- `tofs_for_plane`: an array of int used to specify the number of ToF on each level
  of the aggregation layer (`[2,2]` means that there are two level of ToF, composed
   by two ToF). 

The other parameters have the same meaning explained in "Built a topology".


#### `lab.json`

It's possible to consult the `output/lab.json` file to know all the information on
topology and nodes. 

#### `get_ip.py`
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

