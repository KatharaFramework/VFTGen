from model.node.Node import Node
from networking.CollisionDomain import CollisionDomain


class Leaf(Node):
    def __init__(self, name, pod_number, leaf_number, connected_spine, connected_server):
        """
        Initialize the leaf object assigning name and populating self.neighbours
        :param name: (string) the name of the leaf node 'leaf_<pod_num>_<level>_<leaf_num>'
        :param pod_number: (int) the number of the pod of this leaf
        :param leaf_number: (int) the number of this leaf in its pod
        :param connected_spine: (int) the number spines connected northbound to this leaf
        :param connected_server: (int) the number of servers connected southbound to this leaf
        """
        super().__init__()
        self.role = 'leaf'
        self.name = name

        self._add_neighbours(pod_number, leaf_number, connected_spine, connected_server)
        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, pod_number, leaf_number, connected_spine, connected_server):
        """
        Add neighbours to self.neighbours
        :param pod_number: (int) the number of the pod
        :param leaf_number: (int) the number of this leaf (self) in its pod
        :param connected_spine: (int) the number spines connected northbound to this leaf
        :param connected_server: (int) the number of servers connected southbound to this leaf
        :return:
        """
        # Adding spines
        for i in range(1, connected_spine + 1):
            spine_name = "spine_%d_1_%d" % (pod_number, i)
            collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, spine_name)

            self.neighbours.append((spine_name, collision_domain))

        # Adding servers
        for i in range(1, connected_server + 1):
            server_name = "server_%d_%d_%d" % (pod_number, leaf_number, i)
            collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, server_name)

            self.neighbours.append((server_name, collision_domain))
