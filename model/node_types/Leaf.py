from ..node.Node import Node
from networking.CollisionDomain import CollisionDomain
from networking.IPAM import IPAM
from model.node.Interface import Interface


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
        self.level = 0
        self.pod_number = pod_number
        self._add_neighbours(leaf_number, connected_spine, connected_server)
        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, leaf_number, connected_spine, connected_server):
        """
        Add neighbours to self.neighbours
        :param leaf_number: (int) the number of this leaf (self) in its pod
        :param connected_spine: (int) the number spines connected northbound to this leaf
        :param connected_server: (int) the number of servers connected southbound to this leaf
        :return:
        """
        # Adding spines
        for i in range(1, connected_spine + 1):
            spine_name = "spine_%d_1_%d" % (self.pod_number, i)
            collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, spine_name)

            self.neighbours.append((spine_name, collision_domain))

        # Adding servers
        for i in range(1, connected_server + 1):
            server_name = "server_%d_%d_%d" % (self.pod_number, leaf_number, i)
            collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, server_name)

            self.neighbours.append((server_name, collision_domain))

    def _assign_ipv4_address_to_interfaces(self):
        for neighbour_name, collision_domain in self.neighbours:
            assignment = IPAM.get_instance().get_ipv4_address_pair(collision_domain, self.name,
                                                                   neighbour_name)
            # if server_interface is empty the node is not a server or the servers interface is not initialized
            server_interface = list(filter(lambda interface: interface.network == assignment['subnet'],
                                           self.interfaces
                                           )
                                    )

            if server_interface:
                server_interface[0].neighbours.append((neighbour_name, assignment[neighbour_name]))
            else:
                network = assignment["subnet"]
                ipv4_address = assignment[self.name]
                ipv4_neighbour_address = assignment[neighbour_name]
                self.interfaces.append(Interface(len(self.interfaces),
                                                 collision_domain,
                                                 network,
                                                 ipv4_address,
                                                 neighbour_name,
                                                 ipv4_neighbour_address
                                                 )
                                       )
