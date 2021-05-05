from ..node.Node import Node
from ...model.node.Interface import Interface
from ...model.node.LoopbackInterface import LoopbackInterface
from ...networking.CollisionDomain import CollisionDomain
from ...networking.IPAM import IPAM


class Leaf(Node):
    def __init__(self, pod_number, leaf_number, connected_spine, connected_server, leaf_spine_parallel_links=1):
        """
        Initialize the leaf object assigning name and populating self.neighbours
        :param pod_number: (int) the number of the pod of this leaf
        :param leaf_number: (int) the number of this leaf in its pod
        :param connected_spine: (int) the number spines connected northbound to this leaf
        :param connected_server: (int) the number of servers connected southbound to this leaf
        :param leaf_spine_parallel_links (int): number of links between this Leaf and its Spines
        """
        super().__init__()
        self.role = 'leaf'

        self.level = 0
        self.pod_number = pod_number
        self.number = leaf_number

        self.name = 'leaf_%d_%d_%d' % (self.pod_number, self.level, self.number)

        self._add_neighbours(connected_spine, connected_server, leaf_spine_parallel_links)
        self._assign_ipv4_address_to_interfaces()

    def _add_neighbours(self, connected_spine, connected_server, leaf_spine_parallel_links):
        """
        Add neighbours to self.neighbours
        :param connected_spine: (int) the number spines connected northbound to this leaf
        :param connected_server: (int) the number of servers connected southbound to this leaf
        :param leaf_spine_parallel_links (int): number of links between this Leaf and its Spines
        :return:
        """
        # Adding spines
        for i in range(1, connected_spine + 1):
            spine_name = "spine_%d_1_%d" % (self.pod_number, i)
            self._add_parallel_links_to_neighbour(spine_name, leaf_spine_parallel_links)

        # Adding servers
        if connected_server == 0:
            server_name = "server_%d_%d_%d" % (self.pod_number, self.number, 1)
            collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, server_name)
            self.neighbours.append((server_name, collision_domain))
        else:
            for i in range(1, connected_server + 1):
                server_name = "server_%d_%d_%d" % (self.pod_number, self.number, i)
                collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, server_name)

                self.neighbours.append((server_name, collision_domain))

    def _assign_ipv4_address_to_interfaces(self):
        for neighbour_name, collision_domain in self.neighbours:
            assignment = IPAM.get_instance().get_ipv4_address_pair(collision_domain, self.name, neighbour_name)
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

        # Assign the loopback address
        loopback_assignment = IPAM.get_instance().get_ipv4_loopback_address()
        self.interfaces.append(LoopbackInterface(0, loopback_assignment['subnet'], loopback_assignment["ip"]))
