import ipaddress

BASE_IPV4_NET = ipaddress.ip_network("10.0.0.0/8")
BASE_IPV4_SERVER_NET = ipaddress.ip_network("200.0.0.0/8")


class IPAM(object):
    __slots__ = ['ipv4_subnets', 'ipv4_server_subnets', 'ipv4_assignments', 'ipv4_server_assignments']

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
            self.ipv4_server_subnets = BASE_IPV4_SERVER_NET.subnets(new_prefix=24)
            self.ipv4_assignments = {}
            self.ipv4_server_assignments = {}
            IPAM.__instance = self

    def get_ipv4_server_address_pair(self, collision_domain, first_node, second_node):
        if first_node in self.ipv4_server_assignments or second_node in self.ipv4_server_assignments:
            leaf_node, server_node = (first_node, second_node) if first_node in self.ipv4_server_assignments else \
                (second_node, first_node)
            assignment = self.ipv4_server_assignments[leaf_node]
            if server_node not in assignment:
                subnet = assignment["subnet"]
                ips = assignment["ips"]
                server_ip = next(ips)
                assignment[server_node] = server_ip
                self.ipv4_server_assignments[leaf_node] = assignment
            return assignment
        else:
            subnet = next(self.ipv4_server_subnets)
            ips = subnet.hosts()

            leaf_node, server_node = (first_node, second_node) if 'leaf' in first_node else (second_node, first_node)
            leaf_ip = next(ips)
            server_ip = next(ips)
            new_assignment = {
                "collision_domain": collision_domain,
                "subnet": subnet,
                "ips": ips,
                leaf_node: leaf_ip,
                server_node: server_ip
            }

            self.ipv4_server_assignments[first_node if 'leaf' in first_node else second_node] = new_assignment
            return new_assignment

    def get_ipv4_address_pair(self, collision_domain, first_node, second_node):
        if 'server' in first_node or 'server' in second_node:
            return self.get_ipv4_server_address_pair(collision_domain, first_node, second_node)
        else:
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
