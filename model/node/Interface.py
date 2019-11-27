class Interface(object):
    __slots__ = ['number', 'collision_domain', 'network', 'ip_address']

    def __init__(self, number, collision_domain, network, ip_address):
        self.number = number
        self.collision_domain = collision_domain
        self.network = network
        self.ip_address = ip_address

    def to_dict(self):
        return {
            "number": self.number,
            "collision_domain": self.collision_domain,
            "network": str(self.network),
            "ip_address": str(self.ip_address)
        }
