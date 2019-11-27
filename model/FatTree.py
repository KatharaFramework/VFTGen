from model.node_types.Leaf import Leaf
from model.node_types.Server import Server
from model.node_types.Spine import Spine
from model.node_types.Tof import Tof


class FatTree:
    """
    Represents a laboratory composed by two dict, one for the aggregation layer and the other for the pods
    """
    __slots__ = ['pods', 'aggregation_layer']

    def __init__(self):
        """
        Initialize the object.
        """
        self.pods = {}

        self.aggregation_layer = {}

    def create(self, config):
        """
        Get the config of the lab (read from "config.json") and creates the corresponding lab inserting pods
        in self.pods and ToFs in self.aggregation_layer
        :param config: the conf read from "config.json"
        :return: void
        """
        pod_levels = len(config['pod']['spine_num'])
        aggregation_layer_levels = len(config['aggregation_layer']['tof_num'])

        for i in range(1, config['pod_num'] + 1):
            self._create_pod(i, config)

        for level in range(pod_levels + 1, pod_levels + aggregation_layer_levels + 1):
            tofs_for_level = config['aggregation_layer']['tof_num']
            southbound_spines = config['pod']['spine_num'][pod_levels - 1]

            self._create_aggregation_layer_level(level,
                                                 aggregation_layer_levels,
                                                 tofs_for_level,
                                                 pod_levels,
                                                 config['pod_num'],
                                                 southbound_spines
                                                 )

    def _create_pod(self, pod_number, config):
        """
        Creates a pod and insert it in self.pods
        :param pod_number: (int) the number of the pod to create
        :param config: (dict) the config info of the lab
        :return: void
        """
        pod_info = config['pod']
        pod_name = 'pod_%d' % pod_number

        self.pods[pod_name] = {}

        for leaf_num in range(1, pod_info['leaf_num'] + 1):
            self._create_rack(pod_name, pod_number, leaf_num, pod_info['spine_num'][0], pod_info['servers_for_rack'])

        for level, spine_nums in enumerate(pod_info['spine_num']):
            for spine_num in range(1, spine_nums + 1):
                spine_name = 'spine_%d_%d_%d' % (pod_number, level, spine_num)

                spine = Spine(spine_name,
                              pod_number,
                              level,
                              len(pod_info['spine_num']),
                              pod_info['leaf_num'],
                              config['aggregation_layer']['tof_num'],
                              pod_info['spine_num']
                              )
                self.pods[pod_name][spine_name] = spine

    def _create_rack(self, pod_name, pod_number, leaf_number, connected_spines, connected_server):
        """
        Considering leaf as ToR creates a leaf and the servers connected
        :param pod_name: (string) the name of the pod of the rack (ex. "pod_21")
        :param pod_number: (int) the number of the pod of the rack
        :param leaf_number: (int) the number of the leaf at the top of this rack
        :param connected_spines: number of spines connected (northbound) to the leaf at the top of this rack
        :param connected_server: number of servers connected (southbound) to the leaf a the top of this rack
        :return: void
         """
        leaf_name = 'leaf_%d_0_%d' % (pod_number, leaf_number)

        leaf = Leaf(leaf_name, pod_number, leaf_number, connected_spines, connected_server)
        self.pods[pod_name][leaf_name] = leaf

        for server_num in range(1, connected_server + 1):
            server_name = 'server_%d_%d_%d' % (pod_number, leaf_number, server_num)

            server = Server(server_name, leaf_name)
            self.pods[pod_name][server_name] = server

    def _create_aggregation_layer_level(self, level, aggregation_layer_levels, tofs_for_level, pod_levels,
                                        number_of_pods,
                                        southbound_spines_connected):
        """
        Creates an aggregation layer level and inserts all the nodes of it in self.aggregation_layer
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
            tof_name = 'tof_%d_%d' % (level, tof_number)

            tof = Tof(tof_name, level, aggregation_layer_levels, tofs_for_level, pod_levels,
                      number_of_pods=number_of_pods,
                      southbound_spines_connected_per_pod=southbound_spines_connected
                      )
            self.aggregation_layer[tof_name] = tof

    def to_dict(self):
        """
        Returns the description of the lab (self) in a dict object
        :return: the description of the lab (self) in a dict object
        """
        lab_dict = {
            "pod": {},
            "aggregation_layer": {}
        }

        for key, pod in self.pods.items():
            lab_dict["pod"][key] = {}

            for pod_key, pod_element in pod.items():
                lab_dict["pod"][key][pod_key] = pod_element.to_dict()

        for key, aggregation_layer_element in self.aggregation_layer.items():
            lab_dict["aggregation_layer"][key] = aggregation_layer_element.to_dict()

        return lab_dict
