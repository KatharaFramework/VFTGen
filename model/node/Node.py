from networking.IPAM import IPAM
from model.node.Interface import Interface


class Node(object):
    __slots__ = ['role', 'name', 'level', 'neighbours', 'interfaces']

    def __init__(self):
        self.neighbours = []
        self.interfaces = []

    def _assign_ipv4_address_to_interfaces(self):
        for neighbour_name, collision_domain in self.neighbours:
            assignment = IPAM.get_instance().get_ipv4_address_pair(collision_domain, self.name, neighbour_name)

            network = assignment["subnet"]
            ipv4_address = assignment[self.name]
            ipv4_neighbour_address = assignment[neighbour_name]

            self.interfaces.append(Interface(len(self.interfaces), collision_domain, network, ipv4_address,
                                             neighbour_name, ipv4_neighbour_address))

    def to_dict(self):
        return {
            "role": self.role,
            "name": self.name,
            "neighbours": self.neighbours,
            "interfaces": [x.to_dict() for x in self.interfaces]
        }



