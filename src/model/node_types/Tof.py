from ..node.Node import Node


class Tof(Node):
    def __init__(self, number, plane, aggregation_layer_level, number_of_pods=0, southbound_spines_connected_per_pod=0,
                 number_of_planes=1, spine_tof_parallel_links=1, tof2tof=False, ring_parallel_links=1):
        """
        Initialize the tof object assigning name and populating its neighbours
        :param number: (int) the number of the tof in this level and in this plane
        :param plane: (int) the number of the plane of the tof
        :param aggregation_layer_level: (int) the level of the tof in the aggregation layer
        :param number_of_pods: (int, default=0) total number of pods
        :param southbound_spines_connected_per_pod: (int, default=0) number of spines connected southbound per pod
        :param number_of_planes: (int, default=1) the total number of planes in the topology
        :param tof2tof: (bool, default=False) if true add tof to tof links else None
        :param ring_parallel_links (int): number of links between this ToFs and its ring neighbours (if present)
        """
        super().__init__()
        self.role = 'tof'

        self.level = aggregation_layer_level
        self.plane = plane
        self.number = number

        self.name = 'tof_%d_%d_%d' % (self.plane, self.level, self.number)

        self.number_of_planes = number_of_planes

        self._add_neighbours(aggregation_layer_level, number_of_pods,
                             southbound_spines_connected_per_pod, spine_tof_parallel_links,
                             tof2tof, ring_parallel_links)

        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, aggregation_layer_level, number_of_pods,
                        southbound_spines_connected_per_pod, spine_tof_parallel_links, tof2tof, ring_parallel_links):
        """
        Add all neighbours to the tof
        :param aggregation_layer_level: (int) the level of the tof in the aggregation layer
        :param number_of_pods: (int, default=0) total number of pods
        :param southbound_spines_connected_per_pod: (int, default=0) number of spines connected southbound per pod
        :param tof2tof: (bool, default=False) if true add tof to tof links else None
        :param ring_parallel_links (int): number of links between this ToFs and its ring neighbours (if present)
        """
        for pod_number in range(1, number_of_pods + 1):
            for spine_number in range(1, southbound_spines_connected_per_pod + 1):
                southern_spine_name = 'spine_%d_%d_%d' % (pod_number, aggregation_layer_level - 1,
                                                          spine_number + (southbound_spines_connected_per_pod *
                                                                          (self.plane - 1)
                                                                          )
                                                          )
                self._add_parallel_links_to_neighbour(southern_spine_name, spine_tof_parallel_links)

        if tof2tof:
            self._add_tof2tof_links(ring_parallel_links)

    def _add_tof2tof_links(self, ring_parallel_links):
        """
        Add tof to tof (east-west) links as described in the RIFT draft
        :param ring_parallel_links (int): number of links between this ToFs and its ring neighbour
        """
        tof_next_name = None
        if self.plane == 1:
            tof_prev_name = 'tof_%d_%d_%d' % (self.number_of_planes, self.level, self.number)
            if self.number_of_planes > 2:
                tof_next_name = 'tof_%d_%d_%d' % (self.plane + 1, self.level, self.number)
        elif self.plane == self.number_of_planes:
            tof_prev_name = 'tof_%d_%d_%d' % (self.plane - 1, self.level, self.number)
            if self.number_of_planes > 2:
                tof_next_name = 'tof_%d_%d_%d' % (1, self.level, self.number)
        else:
            tof_prev_name = 'tof_%d_%d_%d' % (self.plane - 1, self.level, self.number)
            tof_next_name = 'tof_%d_%d_%d' % (self.plane + 1, self.level, self.number)

        self._add_parallel_links_to_neighbour(tof_prev_name, ring_parallel_links)
        if tof_next_name:
            self._add_parallel_links_to_neighbour(tof_next_name, ring_parallel_links)
