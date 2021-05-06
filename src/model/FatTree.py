from .node_types.Leaf import Leaf
from .node_types.Server import Server
from .node_types.Spine import Spine
from .node_types.Tof import Tof
from ..networking.CollisionDomain import CollisionDomain
from ..networking.IPAM import IPAM


class FatTree(object):
    """
    Represents a laboratory composed by two dict, one for the aggregation layer and the other for the pods
    """
    __slots__ = ['pods', 'aggregation_layer']

    def __init__(self):
        IPAM.get_instance().reset()
        CollisionDomain.get_instance().reset()

        self.pods = {}

        self.aggregation_layer = {}

    def create(self, config):
        """
        Get the config of the lab and creates the corresponding topology inserting pods
        in self.pods and ToFs in self.aggregation_layer
        :param config: the configuration of the topology
        :return: void
        """
        pod_levels = len(config['pod']['spines_for_level'])

        for i in range(1, config['number_of_pods'] + 1):
            self._create_pod(i, config)

        aggregation_layer_level = pod_levels + 1
        southbound_spines = config['redundancy_factor']
        for plane in range(1, config['aggregation_layer']['number_of_planes'] + 1):
            tofs_for_plane = config['aggregation_layer']['tofs_for_plane']

            self._create_aggregation_layer_plane(plane, tofs_for_plane, aggregation_layer_level,
                                                 config['number_of_pods'],
                                                 southbound_spines,
                                                 config['spine_tof_parallel_links'],
                                                 config['aggregation_layer']['number_of_planes'],
                                                 config['tof_rings'],
                                                 config['ring_parallel_links'])

    def _create_pod(self, pod_number, config):
        """
        Creates a pod and insert it in self.pods
        :param pod_number: (int) the number of the pod to create
        :param config: (dict) the config info of the topology
        :return: void
        """
        pod_info = config['pod']

        self.pods[pod_number] = {}

        for leaf_num in range(1, pod_info['leafs_for_pod'] + 1):
            self._create_rack(pod_number, leaf_num, pod_info['spines_for_level'][0], pod_info['servers_for_rack'],
                              config['leaf_spine_parallel_links'])

        for level, spine_nums in enumerate(pod_info['spines_for_level']):
            if level == len(pod_info['spines_for_level']) - 1:
                spine_for_plane = int(spine_nums / config['aggregation_layer']['number_of_planes'])
                for plane in range(1, config['aggregation_layer']['number_of_planes'] + 1):
                    for spine_num in range(1, spine_for_plane + 1):
                        spine = Spine(spine_num + int((spine_for_plane * (plane - 1))),
                                      pod_number,
                                      level + 1,
                                      len(pod_info['spines_for_level']),
                                      pod_info['leafs_for_pod'],
                                      pod_info['spines_for_level'],
                                      config['leaf_spine_parallel_links'],
                                      config['spine_tof_parallel_links'],
                                      plane,
                                      config['aggregation_layer']['tofs_for_plane'])
                        self.pods[pod_number][spine.name] = spine
            else:
                for spine_num in range(1, spine_nums + 1):
                    spine = Spine(spine_num,
                                  pod_number,
                                  level + 1,
                                  len(pod_info['spines_for_level']),
                                  pod_info['leafs_for_pod'],
                                  pod_info['spines_for_level'],
                                  config['leaf_spine_parallel_links'],
                                  config['spine_tof_parallel_links'])
                    self.pods[pod_number][spine.name] = spine

    def _create_rack(self, pod_number, leaf_number, connected_spines, connected_server, leaf_spine_parallel_links):
        """
        Considering leaf as ToR creates a leaf and the servers connected
        :param pod_number: (int) the number of the pod of the rack
        :param leaf_number: (int) the number of the leaf at the top of this rack
        :param connected_spines (int): number of spines connected (northbound) to the leaf at the top of this rack
        :param connected_server (int): number of servers connected (southbound) to the leaf a the top of this rack
        :param leaf_spine_parallel_links (int): number of links between a Leaf and a Spine
        :return: void
         """
        leaf = Leaf(pod_number, leaf_number, connected_spines, connected_server, leaf_spine_parallel_links)
        self.pods[pod_number][leaf.name] = leaf

        for server_num in range(1, connected_server + 1):
            server_name = 'server_%d_%d_%d' % (pod_number, leaf_number, server_num)

            server = Server(server_name, leaf.name)
            self.pods[pod_number][server_name] = server

    def _create_aggregation_layer_plane(self, plane, tofs_for_plane, aggregation_layer_level,
                                        number_of_pods, southbound_spines_connected, spine_tof_parallel_links,
                                        number_of_planes, tof_rings, ring_parallel_links):
        """
        Creates an aggregation layer level and inserts all the nodes of it in self.aggregation_layer
        :param plane: (int) the plane number of ToFs to be created
        :param tofs_for_plane: (int) number of ToFs to create for this plane
        :param aggregation_layer_level: (int) the level of this layer in the network
        :param number_of_pods: (int) total number of pods
        :param southbound_spines_connected: (int) number of spines southbound connected
        :param spine_tof_parallel_links (int): number of links between the ToF and southbound Spines
        :param number_of_planes: (int) total number of planes,
        :param tof_rings (bool): indicates whether ToF rings should be created
        :param ring_parallel_links (int): number of links between ToFs connected with a ring (if present)
        :return: void
        """

        for tof_number in range(1, tofs_for_plane + 1):
            tof = Tof(tof_number, plane, aggregation_layer_level,
                      number_of_pods=number_of_pods,
                      southbound_spines_connected_per_pod=southbound_spines_connected,
                      number_of_planes=number_of_planes,
                      spine_tof_parallel_links=spine_tof_parallel_links,
                      tof2tof=tof_rings,
                      ring_parallel_links=ring_parallel_links
                      )
            self.aggregation_layer[tof.name] = tof

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
