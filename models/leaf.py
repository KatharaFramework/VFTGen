import netutils
from models import node


class Leaf(node.Node):
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
        self.add_neighbours(pod_number, leaf_number, connected_spine, connected_server)
        self.assign_ipv4_address_to_interfaces()

    def add_neighbours(self, pod_number, leaf_number, connected_spine, connected_server):
        """
        Add neighbours to self.neighbours
        :param pod_number: (int) the number of the pod
        :param leaf_number: (int) the number of this leaf (self) in its pod
        :param connected_spine: (int) the number spines connected northbound to this leaf
        :param connected_server: (int) the number of servers connected southbound to this leaf
        :return:
        """
        # adding spines
        for i in range(1, connected_spine + 1):
            spine_name = "spine_" + str(pod_number) + "_1_" + str(i)
            collision_domain = netutils.get_collision_domain(self.name, spine_name)
            self.neighbours.append((spine_name, collision_domain))

        # adding servers
        for i in range(1, connected_server + 1):
            server_name = "server_" + str(pod_number) + "_" + str(leaf_number) + "_" + str(i)
            collision_domain = netutils.get_collision_domain(self.name, server_name)
            self.neighbours.append((server_name, collision_domain))


