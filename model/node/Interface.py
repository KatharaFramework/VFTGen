class Interface(object):
    __slots__ = ['number', 'collision_domain', 'network', 'ip_address', 'neighbour_name', 'neighbour_ip']

    def __init__(self, number, collision_domain, network, ip_address, neighbour_name, neighbour_ip):
        self.number = number
        self.collision_domain = collision_domain
        self.network = network
        self.ip_address = ip_address
        self.neighbour_name = neighbour_name
        self.neighbour_ip = neighbour_ip

    def to_dict(self):
        return {
            "number": self.number,
            "collision_domain": self.collision_domain,
            "network": str(self.network),
            "ip_address": str(self.ip_address),
            "neighbour_name": self.neighbour_name,
            "neighbour_ip": str(self.neighbour_ip)
        }
