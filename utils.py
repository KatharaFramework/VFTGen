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


