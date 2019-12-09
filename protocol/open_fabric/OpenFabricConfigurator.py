import os

from ..IConfigurator import IConfigurator

# --------------------------- Start of OpenFabric configuration templates ---------------------------------------------

OPENFABRIC_IFACE_CONFIGURATION = """interface eth%d
 ip router openfabric 1
"""

OPENFABRIC_ROUTER_CONFIGURATION = """
router openfabric 1
 net %s
"""

# --------------------------- End of OpenFabric configuration templates -----------------------------------------------


class OpenFabricConfigurator(IConfigurator):
    """
    This class is used to write the OpenFabric configuration of nodes in a FatTree object
    """

    def _configure_node(self, lab, node):
        """
        Write the OpenFabric configuration for the node
        :param lab: a Laboratory object (used to take information about the laboratory dir)
        :param node: a Node object of a FatTree topology
        :return:
        """
        with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
            lab_config.write('%s[image]="kathara/frr"\n' % node.name)

        os.mkdir('%s/%s/etc/frr' % (lab.lab_dir_name, node.name))
        with open('%s/%s/etc/frr/daemons' % (lab.lab_dir_name, node.name), 'w') as daemons:
            daemons.write('zebra=yes\n')
            daemons.write('fabricd=yes\n')

        with open('%s/%s/etc/frr/fabricd.conf' % (lab.lab_dir_name, node.name), 'w') as fabricd_configuration:
            for interface in node.interfaces:
                fabricd_configuration.write(OPENFABRIC_IFACE_CONFIGURATION % interface.number)

            fabricd_configuration.write(OPENFABRIC_ROUTER_CONFIGURATION %
                                        self._get_net_iso_format(node.interfaces[0].ip_address)
                                        )

        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
            startup.write('/etc/init.d/frr start\n')
            startup.write('sysctl -w net.ipv4.fib_multipath_hash_policy=1\n')

    @staticmethod
    def _get_net_iso_format(ip_address):
        """
        Takes an ip_address and return a net in iso format
        :param ip_address: (IPv4Address) the ip address of a node
        :return: (string) a net identifier in iso format
        """
        s = "".join(map(lambda x: '%03d' % int(x), str(ip_address).split('.')))
        return '49.0001.%s.%s.%s.00' % (s[0:4], s[4:8], s[8:12])
