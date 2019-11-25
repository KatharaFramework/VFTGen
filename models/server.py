import netutils


class Server:
    def __init__(self, name, connected_leaf_name):
        """
        Initialize the server object assigning name and populating its neighbours (only the leaf to which it is
        connected)
        :param name: (string) the name of the server node
        :param connected_leaf_name: (string) the name of the leaf to which this server is connected
        """
        self.role = 'server'
        self.name = name
        self.interfaces = {}
        self.neighbours = []
        self.add_neighbours(connected_leaf_name)

    def add_neighbours(self, connected_leaf_name):
        self.neighbours.append((connected_leaf_name, netutils.get_collision_domain(self.name, connected_leaf_name)))
