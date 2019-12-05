from ..node.Node import Node
from networking.CollisionDomain import CollisionDomain


class Spine(Node):
    def __init__(self, name, pod_number, level, pod_total_levels, connected_leafs, connected_tofs, connected_spines):
        """
        Initialize the spine object assigning name and populating its neighbours
        :param name: (string) the name of the spine node
        :param pod_number: (int) the number of the pod of this spine
        :param level: (int) the level of this spine
        :param pod_total_levels: (int) the total level of the pods
        :param connected_leafs: (int) the number of leaf southbound connected to this spine
        :param connected_tofs: (int) the number of tof northbound connected to this spine
        :param connected_spines: (int list) each element of the list in pos x represents the number of
                                 spine in x+1 pod level
        """
        super().__init__()
        self.role = 'spine'
        self.name = name
        self.level = level
        self.pod_number = pod_number
        self._add_neighbours(level, pod_total_levels, connected_leafs, connected_tofs, connected_spines)
        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, level, pod_total_levels, connected_leafs, connected_tofs, connected_spines):
        """
        Adds all the neighbours of this spine in self.neighbours as (neighbour_name, collision_domain)
        :param level: (int) the level of this spine
        :param pod_total_levels: (int) the total level of the pods
        :param connected_leafs: (int, default=0) the number of leaf southbound connected to this spine
        :param connected_tofs: (int, default=0) the number of tof northbound connected to this spine
        :param connected_spines: (int list, default=[]) each element of the list in pos x represents the number of
                                 spine in x+1 pod level
        :return: void
        """
        real_level = level+1
        if real_level == 1:
            # If it is the first level of spine then connect this spine to all southbound leafs in this pod
            # Connects this spine to any leaf at level 0 in this pod
            for leaf_num in range(1, connected_leafs + 1):
                leaf_name = 'leaf_%d_0_%d' % (self.pod_number, leaf_num)

                self._add_neighbour(leaf_name)

            if pod_total_levels == 1:
                # If it is the last level of spines then connect this spine to northbound tofs in the aggregation layer

                for tof_num in range(1, connected_tofs + 1):
                    tof_name = 'tof_%d_%d' % (real_level + 1, tof_num)

                    self._add_neighbour(tof_name)
            else:
                # If it is not the last level of the pod then connects this spine to northbound spines of
                # level above of this pod
                for spine_num in range(1, connected_spines[1] + 1):
                    spine_name = 'spine_%d_%d_%d' % (self.pod_number, real_level + 1, spine_num)

                    self._add_neighbour(spine_name)
        else:
            # If it is not the first level of spine
            # Connects southbound to this spine all the spine of the previous level of this pod
            for spine_num in range(1, connected_spines[level - 1] + 1):
                southern_spine_name = 'spine_%d_%d_%d' % (self.pod_number, real_level - 1, spine_num)

                self._add_neighbour(southern_spine_name)

            if real_level == pod_total_levels:
                # If it is the last level of the pod then connects northbound all the tof in the first level of the
                # aggregation layer
                for tof_num in range(1, connected_tofs + 1):
                    tof_name = 'tof_%d_%d' % (real_level + 1, tof_num)

                    self._add_neighbour(tof_name)
            else:
                # If it is not the last level of spine then connects northbound this spine to all the spine of the
                # above level of this pod
                for spine_num in range(1, connected_spines[level + 1]):
                    northern_spine_name = 'spine_%d_%d_%d' % (self.pod_number, real_level + 1, spine_num)

                    self._add_neighbour(northern_spine_name)

    def _add_neighbour(self, node_name):
        """
        Selects a collision domain and adds a neighbour
        (represented by (node_name, collision_domain)) to self.neighbours
        :param node_name: the name of the neighbour to add
        :return:
        """
        collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, node_name)
        self.neighbours.append((node_name, collision_domain))
