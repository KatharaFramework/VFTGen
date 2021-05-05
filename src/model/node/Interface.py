from ... import utils


class Interface(object):
    __slots__ = ['number', 'collision_domain', 'network', 'ip_address', 'neighbours']

    def __init__(self, number, collision_domain, network, ip_address, neighbour_name, neighbour_ip):
        self.number = number
        self.collision_domain = collision_domain
        self.network = network
        self.ip_address = ip_address
        self.neighbours = [(neighbour_name, neighbour_ip)]

    def get_name(self):
        return ("net%d" if utils.KUBE_NET else "eth%d") % self.number

    def to_dict(self):
        return {
            "number": self.number,
            "collision_domain": self.collision_domain,
            "network": str(self.network),
            "ip_address": str(self.ip_address),
            "neighbours": [(neighbour_name, str(ip)) for (neighbour_name, ip) in self.neighbours],
        }
