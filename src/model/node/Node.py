from .Interface import Interface
from .LoopbackInterface import LoopbackInterface
from ...networking.CollisionDomain import CollisionDomain
from ...networking.IPAM import IPAM


class Node(object):
    """
    Abstract Class
    This class represents a node in a network topology
    """

    __slots__ = ['role', 'name', 'level', 'neighbours', 'interfaces']

    def __init__(self):
        self.neighbours = []
        self.interfaces = []

    def _assign_ipv4_address_to_interfaces(self):
        """
        Assigns ipv4 address to interfaces fetching self.neighbours
        :return:
        """
        for neighbour_name, collision_domain in self.neighbours:
            assignment = IPAM.get_instance().get_ipv4_address_pair(collision_domain, self.name, neighbour_name)

            network = assignment["subnet"]
            ipv4_address = assignment[self.name]
            ipv4_neighbour_address = assignment[neighbour_name]

            self.interfaces.append(Interface(len(self.interfaces), collision_domain, network, ipv4_address,
                                             neighbour_name, ipv4_neighbour_address
                                             )
                                   )

        # Assign the loopback address
        loopback_assignment = IPAM.get_instance().get_ipv4_loopback_address()
        self.interfaces.append(LoopbackInterface(0, loopback_assignment['subnet'], loopback_assignment["ip"]))

    def get_lo_interfaces(self):
        return sorted(list(filter(lambda x: type(x) == LoopbackInterface, self.interfaces)), key=lambda x: x.number)

    def get_phy_interfaces(self):
        return sorted(list(set(self.interfaces) - set(self.get_lo_interfaces())), key=lambda x: x.number)

    def _add_parallel_links_to_neighbour(self, node_name, parallel_links):
        for link_id in range(0, parallel_links):
            self._add_neighbour(node_name, link_id=link_id)

    def _add_neighbour(self, node_name, link_id=0):
        """
        Selects a collision domain and adds a neighbour
        (represented by (node_name, collision_domain)) to self.neighbours
        :param node_name: the name of the neighbour to add
        :param link_id: (int) the id of the link, unique among the links between first_node and second_node
        :return:
        """
        collision_domain = CollisionDomain.get_instance().get_collision_domain(self.name, node_name, link_id)
        self.neighbours.append((node_name, collision_domain))

    def to_dict(self):
        return {
            "role": self.role,
            "name": self.name,
            "neighbours": self.neighbours,
            "interfaces": [x.to_dict() for x in self.interfaces]
        }
