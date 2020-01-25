#!/usr/bin/python3

import os
import shutil

import utils
from model.FatTree import FatTree
from model.Laboratory import Laboratory

if __name__ == '__main__':
    if os.path.isdir('lab'):
        shutil.rmtree('lab')
    os.mkdir('lab')

    if not os.path.isdir('output'):
        os.mkdir('output')

    topology_params = utils.read_config('config.json')
    config = utils.three_level_fat_tree_config(
        topology_params["k_leaf"], topology_params["k_top"], topology_params["redundancy_factor"],
        topology_params["servers_for_rack"], topology_params['protocol']
    )
    utils.write_json_file("output/topology_info.json", config)
    fat_tree = FatTree()
    fat_tree.create(config)

    lab = Laboratory("lab")
    lab.dump(fat_tree)

    protocol = config["protocol"] if "protocol" in config else None
    if protocol:
        protocol_class_name = "".join(map(lambda x: x.capitalize(), protocol.split("_")))

        protocol_configurator = utils.class_for_name("protocol.%s" % protocol,
                                                     "%sConfigurator" % protocol_class_name
                                                     )()

        protocol_configurator.configure(lab, fat_tree)

    utils.write_json_file("output/lab.json", fat_tree.to_dict())
