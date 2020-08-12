import importlib
import json

KUBE_NET = False


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
    m = importlib.import_module(module_name + "." + class_name)
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
