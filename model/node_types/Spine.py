from ..node.Node import Node


class Spine(Node):
    def __init__(self, number, pod_number, level, pod_total_levels, connected_leafs, connected_spines,
                 leaf_spine_parallel_links=1, spine_tof_parallel_links=1, plane=0, tofs_for_plane=0):
        """
        Initialize the spine object assigning name and populating its neighbours
        :param number: (int) the number of the tof in this pod
        :param pod_number: (int) the number of the pod of this spine
        :param level: (int) the level of this spine
        :param pod_total_levels: (int) the total level of the pods
        :param connected_leafs: (int) the number of leaf southbound connected to this spine
        :param connected_spines: (int) number of spines connected northbound
        :param leaf_spine_parallel_links (int): number of links between this Spine and its Leaves
        :param spine_tof_parallel_links (int): number of links between this Spine and its ToFs
        :param plane: (int, default=0) the number of the plane which this spine is connected
        :param tofs_for_plane: (int, default=0) the number of tof for plane
        """
        super().__init__()
        self.role = 'spine'

        self.level = level
        self.pod_number = pod_number
        self.number = number

        self.name = 'spine_%d_%d_%d' % (self.pod_number, self.level, self.number)

        self._add_neighbours(pod_total_levels, connected_leafs, connected_spines, leaf_spine_parallel_links,
                             spine_tof_parallel_links, plane, tofs_for_plane)
        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, pod_total_levels, connected_leafs, connected_spines, leaf_spine_parallel_links,
                        spine_tof_parallel_links, plane, tofs_for_plane):
        """
        Adds all the neighbours of this spine in self.neighbours as (neighbour_name, collision_domain)
        :param pod_total_levels: (int) the total level of the pods
        :param connected_leafs: (int, default=0) the number of leaf southbound connected to this spine
        :param connected_spines: (int) number of spines connected northbound
        :param leaf_spine_parallel_links (int): number of links between this Spine and its Leaves
        :param spine_tof_parallel_links (int): number of links between this Spine and its ToFs
        :param plane: (int, default=0) the number of the plane which this spine is connected
        :param tofs_for_plane: (int, default=0) the number of tof for plane
        :return: void
        """
        if self.level == 1:
            # If it is the first level of spine then connect this spine to all southbound leafs in this pod
            # Connects this spine to any leaf at level 0 in this pod
            for leaf_num in range(1, connected_leafs + 1):
                leaf_name = 'leaf_%d_0_%d' % (self.pod_number, leaf_num)
                self._add_parallel_links_to_neighbour(leaf_name, leaf_spine_parallel_links)

            if pod_total_levels == 1:
                # If it is the last level of spines then connect this spine to northbound tofs in the aggregation layer
                for tof_num in range(1, tofs_for_plane + 1):
                    tof_name = 'tof_%d_%d_%d' % (plane, self.level + 1, tof_num)
                    self._add_parallel_links_to_neighbour(tof_name, spine_tof_parallel_links)
            else:
                # If it is not the last level of the pod then connects this spine to northbound spines of
                # level above of this pod
                for spine_num in range(1, connected_spines[1] + 1):
                    spine_name = 'spine_%d_%d_%d' % (self.pod_number, self.level + 1, spine_num)
                    self._add_neighbour(spine_name)
        else:
            # If it is not the first level of spine
            # Connects southbound to this spine all the spine of the previous level of this pod
            for spine_num in range(1, connected_spines[self.level - 2] + 1):
                southern_spine_name = 'spine_%d_%d_%d' % (self.pod_number, self.level - 1, spine_num)
                self._add_neighbour(southern_spine_name)

            if self.level == pod_total_levels:
                # If it is the last level of the pod then connects northbound all the tof in the first level of the
                # aggregation layer
                for tof_num in range(1, tofs_for_plane + 1):
                    tof_name = 'tof_%d_%d_%d' % (plane, self.level + 1, int(plane * tof_num))
                    self._add_parallel_links_to_neighbour(tof_name, spine_tof_parallel_links)
            else:
                # If it is not the last level of spine then connects northbound this spine to all the spine of the
                # above level of this pod
                for spine_num in range(1, connected_spines[self.level]):
                    northern_spine_name = 'spine_%d_%d_%d' % (self.pod_number, self.level + 1, spine_num)
                    self._add_neighbour(northern_spine_name)
