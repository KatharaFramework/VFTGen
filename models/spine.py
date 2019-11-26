import netutils
from models import node


class Spine(node.Node):
    def __init__(self, name, pod_number, level, pod_total_levels, connected_leafs=0, connected_tofs=0,
                 connected_spines=[]):
        """
        Initialize the spine object assigning name and populating its neighbours
        :param name: (string) the name of the spine node
        :param pod_number: (int) the number of the pod of this spine
        :param spine_number: (int) the number of the spine in its pod
        :param level: (int) the level of this spine
        :param pod_total_levels: (int) the total level of the pods
        :param connected_leafs: (int, default=0) the number of leaf southbound connected to this spine
        :param connected_tofs: (int, default=0) the number of tof northbound connected to this spine
        :param connected_spines: (int list, default=[]) each element of the list in pos x represents the number of
                                 spine in x+1 pod level
        """
        super().__init__()
        self.role = 'spine'
        self.name = name
        self.add_neighbours(pod_number, level, pod_total_levels,
                            connected_leafs, connected_tofs, connected_spines)
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

    def add_neighbours(self, pod_number, level, pod_total_levels,
                       connected_leafs, connected_tofs, connected_spines):
        """
        Adds all the neighbours of this spine in self.neighbours as (neighbour_name, collision_domain)
        :param pod_number: (int) the number of the pod of this spine
        :param level: (int) the level of this spine
        :param pod_total_levels: (int) the total level of the pods
        :param connected_leafs: (int, default=0) the number of leaf southbound connected to this spine
        :param connected_tofs: (int, default=0) the number of tof northbound connected to this spine
        :param connected_spines: (int list, default=[]) each element of the list in pos x represents the number of
                                 spine in x+1 pod level
        :return:
        """
        # if it is the first level of spine then connect this spine to all southbound leafs in this pod
        if level == 1:

            # connects this spine to any leaf at level 0 in this pod
            for leaf_num in range(1, connected_leafs + 1):
                leaf_name = 'leaf_' + str(pod_number) + '_0_' + str(leaf_num)
                self.add_neighbour(leaf_name)

            # if it is the last level of spines then connect this spine to northbound tofs in the aggregation layer
            if pod_total_levels == 1:
                for tof_num in range(1, connected_tofs + 1):
                    tof_name = 'tof_' + str(level + 1) + '_' + str(tof_num)
                    self.add_neighbour(tof_name)
            # if it is not the last level of the pod then connects
            # this spine to northbound spines of level above of this pod
            else:

                for spine_num in range(1, connected_spines[1] + 1):
                    spine_name = 'spine_' + str(pod_number) + '_' + str(level + 1) + '_' + str(spine_num)
                    self.add_neighbour(spine_name)
        # if it is not the first level of spine
        else:
            # connects southbound to this spine all the spine of the previous level of this pod
            for spine_num in range(1, connected_spines[level - 1 - 1] + 1):
                southern_spine_name = 'spine_' + str(pod_number) + '_' + str(level - 1) + '_' + str(spine_num)
                self.add_neighbour(southern_spine_name)
            # if it is the last level of the pod then connects northbound all the tof in the first level of the
            # aggregation layer
            if level == pod_total_levels:
                for tof_num in range(1, connected_tofs[0] + 1):
                    tof_name = 'tof_' + str(level + 1) + '_' + str(tof_num)
                    self.add_neighbour(tof_name)
            # if it is not the last level of spine then connects northbound this spine to all the spine of the
            # above level of this pod
            else:
                for spine_num in range(1, connected_spines[level - 1 + 1]):
                    northern_spine_name = 'spine_' + str(pod_number) + '_' + str(level + 1) + '_' + str(spine_num)
                    self.add_neighbour(northern_spine_name)
