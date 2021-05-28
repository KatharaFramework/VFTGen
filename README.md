# VFTGen
VFTGen is a tool that allows to create three levels Fat Tree
topologies (single-plane or multi-planes) and configure them to run on Kathará. 

**N.B. :** until now only three-level architectures are possible.

**N.B. :** _Katharà_ works well on Linux, Windows and MacOS, but due to Docker limitations not all the functionalities
are available on non-Linux platform (i.e. ECMP).

## Publication

- **VFTGen: a Tool to Perform Experiments in Virtual Fat Tree Topologies** (at **IM 2021**)
    - [Paper](http://dl.ifip.org/db/conf/im/im2021demo/213179.pdf)
    - [Presentation](https://www.youtube.com/watch?v=ovk7hvn57cc?)

## Prerequisites

- Python 3
- Kathará (https://www.kathara.org/)

## Usage 

### Build a topology 

#### From Configuration File

The parameters to build a topology can be described in a `config.json` file.

```
{
  "k_leaf": 4,
  "k_top": 4,
  "redundancy_factor": 2,
  "n_pods" : 2,
  "servers_for_rack": 1,
  "tof_rings": false,
  "leaf_spine_parallel_links": 1, 
  "spine_tof_parallel_links": 1, 
  "ring_parallel_links": 0,
  "protocol": "bgp"
}
```

- `k_leaf`: the number of ports of a leaf node pointing north or south
- `k_top`: the number of ports of a spine node pointing north or south
- `redundancy_factor`: the number of connections from a ToF node to a PoD
- `servers_for_rack`: used to specify the number of servers for each leaf (considered as Top of Rack)
- `tof_rings`: flag used to create ToF rings in multi-plane topologies
- `n_pods`: used to specify the number of pods in the fabric (if not specified the maximum number of pods is used)
- `leaf_spine_parallel_links`: used to specify the number of parallel links between a leaf and a spine (default=1)
- `spine_tof_parallel_links`: used to specify the number of parallel links between a spine and a tof (default=1)
- `ring_parallel_links`: used to specify the number of parallel links between two tofs connected between tof rings (default=1)
- `protocol`: 
    - `bgp` (uses the FRR implementation)
    - `open_fabric` (uses the FRR implementation)
    - `rift` (ZTP configuration) (uses the **rift-python** implementation of Bruno Rijsman https://github.com/brunorijsman/rift-python)

#### From CLI Arguments

Alternatively, it is possible to pass them from command line using `--k_leaf`, `--k_top`, `--r`
(__redundancy_factor__), `--servers` (__servers_for_rack__), `--protocol`. 
These arguments are required, otherwise the values are read from `config.json` file.

Additional non-mandatory CLI args are: `--tof_rings` (sets __tof_rings__ to `true`), 
`--ls_parallel` to specify __leaf_spine_parallel_links__ value, 
`--st_parallel` to specify __spine_tof_parallel_links__ value,
`--ring_parallel` to specify __ring_parallel_links__ value.

It is also possible to use `-d` param to specify an output directory. If not specified the current
directory is used.

The `--name` parameter specifies a name for the directory where the topology is generated. 
By default, the generated directory name is `fat_tree_<k_leaf>_<k_top>_<r>_<protocol>+<ls_parallel>_<st_parallel>_<ring_parallel>`.

`--kube_net` flag is used to configure the network interfaces to work with Megalos version of Kathará.

### Run the tool 

In order to run the tool, type on terminal: 

```
$ python3 vftgen.py
```

**N.B. :** in this case the params values are taken from `config.json` file. Otherwise, specify
the CLI parameters described above.
 
After that, in the current folder (or in the one specified with `-d` option) a
`fat_tree_<k_leaf>_<k_top>_<r>_<protocol>+<ls_parallel>_<st_parallel>_<ring_parallel>` directory 
(or a directory with the name specified using `-n` option) is created, containing: 

- a `lab` folder: containing all the configurations files for Kathará; 
- a `lab.json` file: which contains all the information about the topology and the nodes;
- a `topology_info.json` file: which contains a schematic view of the built topology.

## Fat Tree Conventions and Formulas

### Formulas
       
The topology is built using the following parameters and formulas: 
- Input Parameters:
```
    k_leaf
    k_top
    redundancy_factor (R)
    servers_for_rack
```
- Output Parameters: 
``` 
    number_of_planes = k_leaf/R
    number_of_pod = (k_leaf+k_top)/r
    number_of_spine_per_pod = k_leaf
    number_of_leaf_per_pod = k_top
    number_of_tof_for_plane = k_top
    servers_for_rack =  servers_for_rack
```

### Node names convention

All the nodes in the lab have a name that depend on their type and their position in the topology: 
- `server_<pod_number>_<server_number>`
- `leaf_<pod_number>_<level>_<leaf_number>` (level is always 0 for a leaf)
- `spine_<pod_number>_<level>_<spine_number>`
- `tof_<plane>_<level>_<tof_number>`

## Topology information

#### `topology_info.json`

The `topology_info.json` file contains all the parameters of the built topology: 
```
{
    "aggregation_layer": {
        "number_of_planes": 2,
        "tofs_for_plane": 4
    },
    "k_leaf": 4,
    "k_top": 4,
    "leaf_spine_parallel_links": 2,
    "number_of_pods": 4,
    "pod": {
        "leafs_for_pod": 4,
        "servers_for_rack": 1,
        "spines_for_level": [
            4
        ]
    },
    "protocol": "bgp",
    "redundancy_factor": 2,
    "ring_parallel_links": 2,
    "spine_tof_parallel_links": 2,
    "tof_rings": true
}
```

- `number_of_pods`: used to specify the number of pod in the Fat Tree 

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

The other parameters have the same meaning explained in "Build a topology".


#### `lab.json`

It's possible to read the `lab.json` file to know all the information of the topology and nodes.

## Run the topology 

To run the lab, open a terminal in the topology directory and type: 

```
$ cd lab
$ kathara lstart
``` 

#### Connect to a device

To connect to a specific device, run the following command from the `lab` directory:

```
$ kathara connect <machine_name>
```

This will open a shell into the machine `machine_name` root directory.

## Build RIFT-Python image

In order to run RIFT protocol, it is required to build the corresponding Docker Image. 
To do so, run the following commands (from the root directory of this project):

```
$ cd Dockerfiles/rift-py
$ docker build -t kathara/rift-py .
```

## Additional tools

#### `get_ip.py`
It's also possible to use the `get_ip.py` script to get the nodes IPs of the generated lab. 

To get all the IPs in the network type on terminal: 
```
$ python3 get_ip.py -d fat_tree_<k_leaf>_<k_top>_<r>_<protocol>+<ls_parallel>_<st_parallel>_<ring_parallel>
```

To get the IPs of a particular type of nodes type on terminal: 
```
$ python3 get_ip.py -d fat_tree_<k_leaf>_<k_top>_<r>_<protocol>+<ls_parallel>_<st_parallel>_<ring_parallel> --type <node_type>
```
Possible values for `<node_type>` param are: 
 - `server`
 - `leaf`
 - `spine` 
 - `tof`
