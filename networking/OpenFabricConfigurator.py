import os

from model.node.Node import Node

OPENFABRIC_IFACE_CONFIGURATION = """interface eth%d
 ip router openfabric 1
"""

OPENFABRIC_ROUTER_CONFIGURATION = """router openfabric 1
 net %s
"""


class OpenFabricConfigurator(object):
    __instance = None

    @staticmethod
    def get_instance():
        if OpenFabricConfigurator.__instance is None:
            OpenFabricConfigurator()

        return OpenFabricConfigurator.__instance

    def __init__(self):
        if OpenFabricConfigurator.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            OpenFabricConfigurator.__instance = self

    @staticmethod
    def get_net_iso_format(ip_address):
        s = "".join(map(lambda x: '%03d' % int(x), str(ip_address).split('.')))
        return '49.0001.%s.%s.%s.00' % (s[0:4], s[4:8], s[8:12])

    def configure_node(self, node: Node):
        if node.role != 'server':
            with open('lab/lab.conf', 'a') as lab_config:
                lab_config.write('%s[image]="kathara/frr"\n' % node.name)

            os.mkdir('lab/%s/etc/frr' % node.name)
            with open('lab/%s/etc/frr/daemons' % node.name, 'w') as daemons:
                daemons.write('zebra=yes\n')
                daemons.write('fabricd=yes\n')

            with open('lab/%s/etc/frr/fabricd.conf' % node.name, 'w') as openfabric:
                for interface in node.interfaces:
                    openfabric.write(OPENFABRIC_IFACE_CONFIGURATION % interface.number)

                openfabric.write(OPENFABRIC_ROUTER_CONFIGURATION % self.get_net_iso_format(node.interfaces[0].ip_address))
                if node.role == 'leaf':
                    openfabric.write(" redistribute connected\n")

            with open('lab/%s.startup' % node.name, 'a') as startup:
                startup.write('/etc/init.d/frr start\n')
                startup.write('sysctl -w net.ipv4.fib_multipath_hash_policy=1\n')