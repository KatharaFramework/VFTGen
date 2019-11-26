import netutils
from models import node


class Tof(node.Node):
    def __init__(self, name, tof_number, level, aggregation_layer_levels, tofs_per_level, pod_levels, number_of_pods=0,
                 southbound_spines_connected_per_pod=0):
        """
        Initialize the tof object assigning name and populating its neighbours
        :param name: (string) the name of the tof
        :param tof_number: (int) the number of the tof in its level
        :param level: (int) the level of the tof in the aggregation layer
        :param aggregation_layer_levels: (int) total number of aggregation levels
        :param tofs_per_level: (int list) each element in pos x represents the number of tof at level x+1
        :param pod_levels: (int) total number of level in a pod
        :param number_of_pods: (int, default=0) total number of pods
        :param southbound_spines_connected_per_pod: (int, deafult=0) number of spines at the last level of each pod
        """
        super().__init__()
        self.role = 'tof'
        self.name = name
        self.add_neighbours(level, aggregation_layer_levels, tofs_per_level, pod_levels, number_of_pods,
                            southbound_spines_connected_per_pod)
        self.assign_ipv4_address_to_interfaces()

    def add_neighbour(self, node_name):
        """
            Selects a collision domain and adds a neighbour
            (represented by (node_name, collision_domain)) to self.neighbours
            :param node_name: the name of the neighbour to add
            :return:
        """
        collision_domain = netutils.get_collision_domain(self.name, node_name)
        self.neighbours.append((node_name, collision_domain))

    def add_neighbours(self, level, aggregation_layer_levels, tofs_per_level, pod_levels, number_of_pods,
                       southbound_spines_connected_per_pod):
        """
        Adds all the neighbours of this spine in self.neighbours as (neighbour_name, collision_domain)
        :param level: (int) the level of the tof in the aggregation layer
        :param aggregation_layer_levels: (int) total number of aggregation levels
        :param tofs_per_level: (int list) each element in pos x represents the number of tof at level x+1
        :param pod_levels: (int) total number of level in a pod
        :param number_of_pods: (int, default=0) total number of pods
        :param southbound_spines_connected_per_pod: (int, deafult=0) number of spines at the last level of each pod
        :return:
        """

        current_aggregation_layer_level = level - pod_levels    # the current aggregation layer level

        # if it is the first level of tof (of the aggregation layer)
        if current_aggregation_layer_level == 1:
            # connects southbound to this tof all the spines at the last levels of each pod
            for pod_number in range(1, number_of_pods + 1):
                for spine_number in range(1, southbound_spines_connected_per_pod + 1):
                    southern_spine_name = 'spine_' + str(pod_number) + '_' + str(pod_levels) + '_' + str(spine_number)
                    self.add_neighbour(southern_spine_name)

            # if it is not the last level of the aggregation level
            if current_aggregation_layer_level < aggregation_layer_levels:
                # connects northbound to this tof all the tof in the level above (of the aggregation level)
                for northern_tof_num in range(1, tofs_per_level[current_aggregation_layer_level - 1 + 1] + 1):
                    northern_tof_name = 'tof_' + str(level + 1) + '_' + str(northern_tof_num)
                    self.add_neighbour(northern_tof_name)
        # if it is not the first level of tof
        else:
            # connects southbound to this tof all the tofs in previous level
            for southern_tof_num in range(1, tofs_per_level[current_aggregation_layer_level - 1 - 1] + 1):
                southern_tof_name = 'tof_' + str(level - 1) + '_' + str(southern_tof_num)
                self.add_neighbour(southern_tof_name)

            # if it is not the last level of the aggregation layer
            if current_aggregation_layer_level < aggregation_layer_levels:
                # connects northbound to this tof all the tof in the level above
                for northern_tof_num in range(1, tofs_per_level[current_aggregation_layer_level - 1 + 1] + 1):
                    northern_tof_name = 'tof_' + str(level + 1) + '_' + str(northern_tof_num)
                    self.add_neighbour(northern_tof_name)


