#!/usr/bin/python3

import argparse
import os

from src.utils import create_fat_tree, read_config

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--k_leaf', type=int, required=False)
    parser.add_argument('--k_top', type=int, required=False)
    parser.add_argument('-r', '--redundancy', type=int, required=False)
    parser.add_argument('--pods', type=int, required=False)
    parser.add_argument('--servers', type=int, required=False)
    parser.add_argument('--vms', type=int, required=False, default=0)
    parser.add_argument('--containers', type=int, required=False, default=0)
    parser.add_argument('--protocol', type=str, required=False, choices=['bgp', 'rift', 'open_fabric', 'isis'])
    parser.add_argument('--tof_rings', action="store_true", required=False, default=False)
    parser.add_argument('--ls_parallel', type=int, required=False)
    parser.add_argument('--st_parallel', type=int, required=False)
    parser.add_argument('--ring_parallel', type=int, required=False)
    parser.add_argument('-d', '--dir', type=str, required=False, default=os.path.abspath('.'))
    parser.add_argument('-n', '--name', type=str, required=False, default=None)
    parser.add_argument('--kube_net', action="store_true", required=False, default=False)

    args = parser.parse_args()
    if args.k_leaf and args.k_top and args.redundancy and args.servers is not None and args.protocol:
        params = {
            "k_leaf": args.k_leaf,
            "k_top": args.k_top,
            "redundancy_factor": args.redundancy,
            "n_pods": args.pods if args.pods else None,
            "servers_for_rack": args.servers,
            "vms_per_server": args.vms,
            "containers_per_vm": args.containers,
            "tof_rings": args.tof_rings,
            "leaf_spine_parallel_links": args.ls_parallel if args.ls_parallel else 1,
            "spine_tof_parallel_links": args.st_parallel if args.st_parallel else 1,
            "ring_parallel_links": args.ring_parallel if args.ring_parallel else 1,
            "protocol": args.protocol
        }
    else:
        missing_params = []
        if not args.k_leaf:
            missing_params.append("--k_leaf")
        if not args.k_top:
            missing_params.append("--k_top")
        if not args.redundancy:
            missing_params.append("-r")
        if not args.servers:
            missing_params.append("--servers")
        if not args.protocol:
            missing_params.append("--protocol")

        print("No parameters specified: %s, using config.json..." % ", ".join(missing_params))
        params = read_config('config.json')

    create_fat_tree(params, args.dir, args.name, args.kube_net)
