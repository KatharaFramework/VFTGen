import json
from models import leaf as leaf_model
from models import spine as spine_model
from models import tof as tof_model
from models import server as server_model


def obj_to_dict(obj):
    return obj.__dict__


# this class represents a laboratory composed by two dict, one for the aggregation layer and the other for the pods
class Lab:
    def __init__(self, conf):
        """
        initialize the object and creates the laboratory corresponding to conf
        :param conf: configuration read from "config.json"
        """
        self.pods = {}
        self.aggregation_layer = {}
        self.create_lab(conf)

    def create_rack(self, pod_name, pod_number, leaf_number, connected_spines, connected_server):
        """
        considering leaf as tor creates a leaf and the servers connected
        :param pod_name: (string) the name of the pod of the rack (ex. "pod21")
        :param pod_number: (int) the number of the pod of the rack
        :param leaf_number: (int) the number of the leaf at the top of this rack
        :param connected_spines: number of spines connected (northbound) to the leaf at the top of this rack
        :param connected_server: number of servers connected (southbound) to the leaf a the top of this rack
        :return: void
         """
        leaf_name = 'leaf_' + str(pod_number) + '_0_' + str(leaf_number)
        leaf = leaf_model.Leaf(leaf_name, pod_number, leaf_number, connected_spines, connected_server)
        self.pods[pod_name][leaf_name] = leaf
        for server_num in range(1, connected_server + 1):
            server_name = 'server_' + str(pod_number) + '_' + str(leaf_number) + '_' + str(server_num)
            server = server_model.Server(server_name, leaf_name)
            self.pods[pod_name][server_name] = server

    def create_pod(self, pod_number, lab_info):
        """
        creates a pod and insert it in self.pods
        :param pod_number: (int) the number of the pod to create
        :param lab_info: (dict) the config info of the lab
        :return: void
        """
        pod_info = lab_info['pod']
        pod_name = 'pod' + str(pod_number)
        self.pods[pod_name] = {}

        for leaf_num in range(1, pod_info['leaf_num'] + 1):
            self.create_rack(pod_name, pod_number, leaf_num, pod_info['spine_num'][0],
                             pod_info['servers_for_rack'])

        for level in range(1, pod_info['spine_levels'] + 1):
            for spine_num in range(1, pod_info['spine_num'][level - 1] + 1):
                spine_name = 'spine_' + str(pod_number) + '_' + str(level) + '_' + str(spine_num)
                spine = spine_model.Spine(spine_name, pod_number, spine_num, pod_info['leaf_num'], level,
                                          pod_info['spine_levels'],
                                          connected_tofs=lab_info['aggregation_layer']['tof_num'],
                                          connected_spines=pod_info['spine_num'])
                self.pods[pod_name][spine_name] = spine

    def create_aggregation_layer_level(self, level, aggregation_layer_levels, tofs_for_level, pod_levels,
                                       number_of_pods,
                                       southbound_spines_connected):
        """
        creates an aggregation layer level and inserted all the nodes of it in self.aggregation_layer
        :param level: (int) the level of layer to be created
        :param aggregation_layer_levels: (int) the total number of level of the aggregation layer
        :param tofs_for_level: (list) each element of the list at pos x represents the number of tofs at layer level
                                x + 1
        :param pod_levels: (int) total number of level in a pod
        :param number_of_pods: (int) total number of pods
        :param southbound_spines_connected: (int) number of spines southbound connected
        :return: void
        """
        for tof_number in range(1, tofs_for_level[level - pod_levels - 1] + 1):
            tof_name = 'tof_' + str(level) + '_' + str(tof_number)
            tof = tof_model.Tof(tof_name, tof_number, level, aggregation_layer_levels, tofs_for_level,
                                pod_levels,
                                number_of_pods=number_of_pods,
                                southbound_spines_connected_per_pod=southbound_spines_connected)
            self.aggregation_layer[tof_name] = tof

    def create_lab(self, conf):
        """
        get the conf of the lab (read from "config.json") and creates the corresponding lab inserting pods in self.pods
        and tofs in self.aggregation_layer
        :param conf: the conf read from "config.json"
        :return: void
        """
        pod_levels = conf['pod']['spine_levels']
        aggregation_layer_levels = conf['aggregation_layer']['levels']

        for i in range(1, conf['pod_num'] + 1):
            self.create_pod(i, conf)

        for level in range(pod_levels + 1, pod_levels + conf['aggregation_layer']['levels'] + 1):
            tofs_for_level = conf['aggregation_layer']['tof_num']
            southbound_spines = conf['pod']['spine_num'][pod_levels - 1]
            self.create_aggregation_layer_level(level, aggregation_layer_levels, tofs_for_level, pod_levels,
                                                conf['pod_num'],
                                                southbound_spines)

    def lab_to_dict(self):
        """
        returns the description of the lab (self) in a dict object
        :return: the description of the lab (self) in a dict object
        """
        for pod in self.pods.values():
            for key in pod.keys():
                pod[key] = obj_to_dict(pod[key])

        for key in self.aggregation_layer.keys():
            self.aggregation_layer[key] = obj_to_dict(self.aggregation_layer[key])

        lab = obj_to_dict(self)
        return lab

    def to_json(self):
        """
        returns the description of the lab (self) in a json object
        :return: the description of the lab (self) in a json object
        """
        return json.dumps(self.lab_to_dict(), indent=4, sort_keys=True)

