import ipaddress

BASE_IPV4_NET = ipaddress.ip_network("10.0.0.0/8")


class IPAM(object):
    __slots__ = ['ipv4_subnets', 'ipv4_assignments']

    __instance = None

    @staticmethod
    def get_instance():
        if IPAM.__instance is None:
            IPAM()

        return IPAM.__instance

    def __init__(self):
        if IPAM.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.ipv4_subnets = BASE_IPV4_NET.subnets(new_prefix=30)
            self.ipv4_assignments = {}

            IPAM.__instance = self

    def get_new_ipv4_address_pair(self, collision_domain, first_node, second_node):
        if (first_node, second_node) in self.ipv4_assignments:
            return self.ipv4_assignments[(first_node, second_node)]
        elif (second_node, first_node) in self.ipv4_assignments:
            return self.ipv4_assignments[(second_node, first_node)]
        else:
            subnet = next(self.ipv4_subnets)
            ips = subnet.hosts()

            new_assignment = {
                "collision_domain": collision_domain,
                "subnet": subnet,
                first_node: next(ips),
                second_node: next(ips)
            }

            self.ipv4_assignments[(first_node, second_node)] = new_assignment

            return new_assignment
