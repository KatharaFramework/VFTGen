import ipaddress


class IPAM(object):
    """
    This class manage the ipv4 address assignments for the nodes in a FatTree object
    """
    __slots__ = ['ipv4_subnets', 'ipv4_server_subnets', 'ipv4_assignments', 'ipv4_server_assignments',
                 'ipv4_loopback_ips']

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
            self.ipv4_subnets = None
            self.ipv4_server_subnets = None
            self.ipv4_loopback_ips = None

            self.ipv4_assignments = {}
            self.ipv4_server_assignments = {}

            self.reset()

            IPAM.__instance = self

    def reset(self):
        self.ipv4_subnets = ipaddress.ip_network("10.0.0.0/8").subnets(new_prefix=30)
        self.ipv4_server_subnets = ipaddress.ip_network("200.0.0.0/8").subnets(new_prefix=24)
        self.ipv4_loopback_ips = ipaddress.ip_network("192.168.0.0/16").hosts()

        self.ipv4_assignments = {}
        self.ipv4_server_assignments = {}

    def get_ipv4_server_address_pair(self, collision_domain, first_node, second_node):
        """
        Get an ipv4 address pair for a Leaf node and a Server Node (a /24 from 200.0.0.0/8)
        :param collision_domain: the collision domain id of the link between first_node and second_node
        :param first_node: a Node object
        :param second_node: a Node object (one node is a server and the other one a leaf, order is not important)
        :return: an assignment object :
            {
                collision_domain: (string) collision_domain,
                subnet: (IPV4Network) the ipv4 subnet (/24)
                ips: object from IPV4Address that knows the free ip in the subnet
                leaf_node: (IPV4Address) first_node ip address if it is a Leaf else second_node ip address
                server_nodes: (IPV4Address list) list of ips of server nodes already in the subnet +
                              (first_node ip address if is a server else second_node ip address)
            }
        """
        if first_node in self.ipv4_server_assignments or second_node in self.ipv4_server_assignments:
            leaf_node, server_node = (first_node, second_node) if first_node in self.ipv4_server_assignments else \
                (second_node, first_node)

            assignment = self.ipv4_server_assignments[leaf_node]

            if server_node not in assignment:
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
        """
          Get an ipv4 address pair for a nodes pair (not used server-leaf or leaf-server) (a /30 from 10.0.0.0/8)
          :param collision_domain: the collision domain id of the link between first_node and second_node
          :param first_node: a Node object
          :param second_node: a Node object
          :return: an assignment object :
              {
                  collision_domain: (string) collision_domain,
                  subnet: (IPV4Network) the ipv4 subnet (/24)
                  first_node: (IPV4Address) first_node ipv4 address
                  second_node: (IPV4Address) second_node ipv4 address
              }
          """
        if 'server' in first_node or 'server' in second_node:
            return self.get_ipv4_server_address_pair(collision_domain, first_node, second_node)
        else:
            if (first_node, second_node, collision_domain) in self.ipv4_assignments:
                return self.ipv4_assignments[(first_node, second_node, collision_domain)]
            elif (second_node, first_node, collision_domain) in self.ipv4_assignments:
                return self.ipv4_assignments[(second_node, first_node, collision_domain)]
            else:
                subnet = next(self.ipv4_subnets)
                ips = subnet.hosts()

                new_assignment = {
                    "collision_domain": collision_domain,
                    "subnet": subnet,
                    first_node: next(ips),
                    second_node: next(ips)
                }

                self.ipv4_assignments[(first_node, second_node, collision_domain)] = new_assignment

                return new_assignment

    def get_ipv4_loopback_address(self):
        loopback_address = next(self.ipv4_loopback_ips)

        return {
            "subnet": ipaddress.ip_network(str(loopback_address) + "/32"),
            "ip": loopback_address
        }
