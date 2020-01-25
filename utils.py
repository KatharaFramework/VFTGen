import importlib
import json


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


def three_level_fat_tree_config(k_leaf, k_top, r, servers_for_rack, protocol):
    # config = {
    #     'k_leaf': k_leaf,
    #     'k_top': k_top,
    #     'redundancy_factor': r,
    #     'number_of_planes': k_leaf / r,
    #     'number_of_pod': (k_leaf+k_top)/r,
    #     'number_of_leaf_per_pod': k_top,
    #     'number_of_top_per_pod': k_leaf,
    #     'number_of_tof': k_top*(k_leaf/r),
    # }
    config = {
        'protocol': protocol,
        'pod_num': int((k_leaf+k_top)/r),
        'pod': {
            'spine_num': [k_leaf],
            'leaf_num': k_top,
            'servers_for_rack': servers_for_rack
        },
        'aggregation_layer': {
            'number_of_planes': int(k_leaf / r),
            'tof_num': [int(k_top*(k_leaf/r))]
        }
    }
    return config
