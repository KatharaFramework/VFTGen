from ..node.Node import Node
from networking.CollisionDomain import CollisionDomain


class Tof(Node):

    def __init__(self, name, plane, aggregation_layer_level, number_of_pods=0,
                 southbound_spines_connected_per_pod=0):
        """
        Initialize the tof object assigning name and populating its neighbours
        :param name: (string) the name of the tof
        :param plane: (int) the number of the plane of the tof
        :param aggregation_layer_level: (int) the level of the tof in the aggregation layer
        :param number_of_pods: (int, default=0) total number of pods
        :param southbound_spines_connected_per_pod: (int, default=0) number of spines connected southbound per pod
        """
        super().__init__()
        self.role = 'tof'
        self.name = name
        self.level = aggregation_layer_level
        self.plane = plane
        self._add_neighbours(aggregation_layer_level, number_of_pods,
                             southbound_spines_connected_per_pod)
        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, aggregation_layer_level, number_of_pods,
                        southbound_spines_connected_per_pod):
        """
        Add all neighbours to the tof
        :param aggregation_layer_level: (int) the level of the tof in the aggregation layer
        :param number_of_pods: (int, default=0) total number of pods
        :param southbound_spines_connected_per_pod: (int, default=0) number of spines connected southbound per pod
        """
        for pod_number in range(1, number_of_pods + 1):
            for spine_number in range(1, southbound_spines_connected_per_pod + 1):
                southern_spine_name = 'spine_%d_%d_%d' % (pod_number, aggregation_layer_level - 1,
                                                          spine_number + (southbound_spines_connected_per_pod *
                                                                          (self.plane - 1)
                                                                          )
                                                          )
                self._add_neighbour(southern_spine_name)

    def _add_neighbour(self, node_name):
        """
            Selects a collision domain and adds a neighbour
            (represented by (node_name, collision_domain)) to self.neighbours
            :param node_name: the name of the neighbour to add
            :return:
        """
        collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, node_name)
        self.neighbours.append((node_name, collision_domain))
