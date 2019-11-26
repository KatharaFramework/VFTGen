import netutils


class Node:
    def __init__(self):
        self.role = 'node'
        self.name = 'node_name'
        self.first_free_interface_number = 0
        self.interfaces = {}
        self.neighbours = []

    def assign_ipv4_address_to_interfaces(self):
        for neighbour in self.neighbours:
            neighbour_name = neighbour[0]
            collision_domain = neighbour[1]
            assignment = netutils.get_new_ipv4_address_pair(collision_domain, self.name, neighbour_name)
            net = assignment[1]
            ipv4_address = assignment[2][1]
            self.interfaces[self.first_free_interface_number] = (self.first_free_interface_number,
                                                                 collision_domain, str(net), neighbour_name,
                                                                 str(ipv4_address))
            self.first_free_interface_number += 1
