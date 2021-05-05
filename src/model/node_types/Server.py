from ..node.Node import Node
from ...networking.CollisionDomain import CollisionDomain


class Server(Node):
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
        self._add_neighbours(connected_leaf_name)
        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, connected_leaf_name):
        self.neighbours.append((connected_leaf_name,
                                CollisionDomain.get_instance().get_collision_domain(self.name, connected_leaf_name)
                                )
                               )
