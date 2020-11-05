#!/usr/bin/python3

import argparse
import os
import shutil

import utils
from model.FatTree import FatTree
from model.Laboratory import Laboratory

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--k_leaf', type=int, required=False)
    parser.add_argument('--k_top', type=int, required=False)
    parser.add_argument('-r', '--redundancy', type=int, required=False)
    parser.add_argument('--pods', type=int, required=False)
    parser.add_argument('--servers', type=int, required=False)
    parser.add_argument('--protocol', type=str, required=False, choices=['bgp', 'rift', 'juniper_rift', 'open_fabric'])
    parser.add_argument('-d', '--dir', type=str, required=False, default=os.path.abspath('.'))
    parser.add_argument('-n', '--name', type=str, required=False, default=None)
    parser.add_argument('--kube_net', action="store_true", required=False, default=False)
    parser.add_argument('--tof_rings', action="store_true", required=False, default=False)
    parser.add_argument('--ls_parallel', type=int, required=False)
    parser.add_argument('--st_parallel', type=int, required=False)
    parser.add_argument('--ring_parallel', type=int, required=False)

    args = parser.parse_args()
    utils.KUBE_NET = args.kube_net
    if args.k_leaf and args.k_top and args.redundancy and args.servers is not None and args.protocol:
        topology_params = {
            "k_leaf": args.k_leaf,
            "k_top": args.k_top,
            "redundancy_factor": args.redundancy,
            "n_pods": args.pods if args.pods else None,
            "servers_for_rack": args.servers,
            "tof_rings": args.tof_rings,
            "leaf_spine_parallel_links": args.ls_parallel if args.ls_parallel else 1,
            "spine_tof_parallel_links": args.st_parallel if args.st_parallel else 1,
            "ring_parallel_links": args.ring_parallel if args.ring_parallel else 1,
            "protocol": args.protocol
        }
    else:
        print("An argument is missing, using config.json...")
        topology_params = utils.read_config('config.json')

    if args.name:
        directory_name = args.name
    else:
        directory_name = 'fat_tree_%d_%d_%d_%s' % (topology_params["k_leaf"], topology_params["k_top"],
                                                   topology_params["redundancy_factor"], topology_params['protocol']
                                                   )

    output_dir = os.path.join(args.dir, directory_name)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    lab_dir = os.path.join(output_dir, 'lab')
    os.makedirs(lab_dir)

    config = utils.three_level_fat_tree_config(
        topology_params["k_leaf"], topology_params["k_top"], topology_params["redundancy_factor"],
        topology_params["n_pods"] if "n_pods" in topology_params else None, topology_params["servers_for_rack"],
        topology_params['protocol'], topology_params['tof_rings'], topology_params['leaf_spine_parallel_links'],
        topology_params["spine_tof_parallel_links"], topology_params["ring_parallel_links"]
    )
    utils.write_json_file(os.path.join(output_dir, "topology_info.json"), config)

    protocol = config["protocol"] if "protocol" in config else None
    number_of_planes = int(topology_params["k_leaf"] / topology_params["redundancy_factor"])

    if args.tof_rings and number_of_planes == 1:
        raise Exception('It is not possible to add ToF rings in a single plane topology!')

    fat_tree = FatTree()
    fat_tree.create(config)

    lab = Laboratory(lab_dir)
    lab.dump(fat_tree)

    if protocol:
        protocol_class_name = "".join(map(lambda x: x.capitalize(), protocol.split("_")))

        protocol_configurator = utils.class_for_name("protocol.%s" % protocol,
                                                     "%sConfigurator" % protocol_class_name
                                                     )()

        protocol_configurator.configure(lab, fat_tree)

    utils.write_json_file(os.path.join(output_dir, "lab.json"), fat_tree.to_dict())
