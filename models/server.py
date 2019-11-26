import netutils
from models import node


class Server(node.Node):
    def __init__(self, name, connected_leaf_name):
        """
        Initialize the server object assigning name and populating its neighbours (only the leaf to which it is
        connected)
        :param name: (string) the name of the server node
        :param connected_leaf_name: (string) the name of the leaf to which this server is connected
        """
        super().__init__()
        self.role = 'server'
        self.name = name
        self.add_neighbours(connected_leaf_name)
        self.assign_ipv4_address_to_interfaces()

    def add_neighbours(self, connected_leaf_name):
        self.neighbours.append((connected_leaf_name, netutils.get_collision_domain(self.name, connected_leaf_name)))
