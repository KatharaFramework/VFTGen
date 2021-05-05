import importlib
import json
import os
import shutil

from .model.FatTree import FatTree
from .model.Laboratory import Laboratory

KUBE_NET = False


def create_fat_tree(topology_params, output_dir_name=None, dir_name=None, is_k8s=False):
    global KUBE_NET
    KUBE_NET = is_k8s

    topology_params['n_pods'] = topology_params['n_pods'] if 'n_pods' in topology_params else None
    topology_params['servers_for_rack'] = topology_params['servers_for_rack'] \
        if 'servers_for_rack' in topology_params else 0
    topology_params['leaf_spine_parallel_links'] = topology_params['leaf_spine_parallel_links'] \
        if 'leaf_spine_parallel_links' in topology_params else 1
    topology_params['spine_tof_parallel_links'] = topology_params['spine_tof_parallel_links'] \
        if 'spine_tof_parallel_links' in topology_params else 1
    topology_params['ring_parallel_links'] = topology_params['ring_parallel_links'] \
        if 'ring_parallel_links' in topology_params else 1

    if dir_name:
        directory_name = dir_name
    else:
        directory_name = 'fat_tree_%d_%d_%d+%d_%d_%d+%s' % (topology_params["k_leaf"], topology_params["k_top"],
                                                            topology_params["redundancy_factor"],
                                                            topology_params['leaf_spine_parallel_links'],
                                                            topology_params['spine_tof_parallel_links'],
                                                            topology_params['ring_parallel_links'],
                                                            topology_params['protocol']
                                                            )

    output_dir_name = output_dir_name if output_dir_name else os.path.abspath('..')
    output_dir = os.path.join(output_dir_name, directory_name)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    lab_dir = os.path.join(output_dir, 'lab')
    os.makedirs(lab_dir)

    config = three_level_fat_tree_config(
        topology_params["k_leaf"], topology_params["k_top"], topology_params["redundancy_factor"],
        topology_params["n_pods"] if "n_pods" in topology_params else None, topology_params["servers_for_rack"],
        topology_params['protocol'], topology_params['tof_rings'], topology_params['leaf_spine_parallel_links'],
        topology_params["spine_tof_parallel_links"], topology_params["ring_parallel_links"]
    )
    write_json_file(os.path.join(output_dir, "topology_info.json"), config)

    protocol = config["protocol"] if "protocol" in config else None
    number_of_planes = int(topology_params["k_leaf"] / topology_params["redundancy_factor"])

    if topology_params['tof_rings'] and number_of_planes == 1:
        raise Exception('It is not possible to add ToF rings in a single plane topology!')

    fat_tree = FatTree()
    fat_tree.create(config)

    lab = Laboratory(lab_dir)
    lab.dump(fat_tree)

    if protocol:
        protocol_class_name = "".join(map(lambda x: x.capitalize(), protocol.split("_")))

        protocol_configurator = class_for_name("protocol.%s" % protocol,
                                               "%sConfigurator" % protocol_class_name
                                               )()

        protocol_configurator.configure(lab, fat_tree)

    write_json_file(os.path.join(output_dir, "lab.json"), fat_tree.to_dict())

    return config, output_dir, lab_dir


def read_config(config):
    """
    read config file in json format and return python corresponding object
    :param config: a file in json format
    :return: a python object corresponding to the configuration
    """
    with open(config, 'r') as file:
        conf = json.load(file)

    return conf


def write_json_file(file, content):
    with open(file, 'w') as json_file:
        json_file.write(json.dumps(content, indent=4, sort_keys=True))


def class_for_name(module_name, class_name):
    m = importlib.import_module("." + module_name + "." + class_name, package=__package__)
    return getattr(m, class_name)


def three_level_fat_tree_config(k_leaf, k_top, r, n_pods, servers_for_rack, protocol, tof_rings,
                                leaf_spine_parallel_links=1, spine_tof_parallel_links=1, ring_parallel_links=1):
    # Formulas used:
    #   Number of Planes: k_leaf / r
    #   Number of PoDs: (k_leaf + k_top) / r
    #   Number of Leaf per PoD: k_top
    #   Number of ToP per PoD: k_leaf
    #   Number of ToFs: k_top * (k_leaf / r)

    config = {
        'protocol': protocol,
        'k_leaf': k_leaf,
        'k_top': k_top,
        'redundancy_factor': r,
        'tof_rings': tof_rings,
        'leaf_spine_parallel_links': leaf_spine_parallel_links,
        'spine_tof_parallel_links': spine_tof_parallel_links,
        'ring_parallel_links': ring_parallel_links,
        'number_of_pods': int((k_leaf + k_top) / r) if n_pods is None else n_pods,
        'pod': {
            'spines_for_level': [k_leaf],
            'leafs_for_pod': k_top,
            'servers_for_rack': servers_for_rack
        },
        'aggregation_layer': {
            'number_of_planes': int(k_leaf / r),
            'tofs_for_plane': k_top
        }
    }

    return config
