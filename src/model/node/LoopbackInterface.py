class LoopbackInterface(object):
    __slots__ = ['number', 'network', 'ip_address']

    def __init__(self, number, network, ip_address):
        self.number = number
        self.network = network
        self.ip_address = ip_address

    def get_name(self):
        return "lo:%d" % self.number if self.number > 0 else "lo"

    def to_dict(self):
        return {
            "network": str(self.network),
            "ip_address": str(self.ip_address),
            "collision_domain": self.get_name()
        }
