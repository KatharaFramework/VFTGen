import os

from ..IConfigurator import IConfigurator
from ...model.node_types.Leaf import Leaf
from ...model.node_types.Spine import Spine
from ...model.node_types.Tof import Tof

# --------------------------- Start of OpenFabric configuration templates ---------------------------------------------

ZEBRA_CONFIG = \
    """hostname frr
password frr
enable password frr

"""

ZEBRA_IFACE_CONFIGURATION = """
interface %s
 ip address %s
"""

OPENFABRIC_ROUTER_CONFIGURATION = """router openfabric 1
 net %s
 fabric-tier %d
 max-lsp-lifetime 65535
 lsp-refresh-interval 65000
 lsp-gen-interval 1
 spf-interval 1
"""

OPENFABRIC_IFACE_CONFIGURATION = """
interface %s
 ip router openfabric 1
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
            tier_n = 0
            if type(node) == Spine:
                tier_n = 1
            elif type(node) == Tof:
                tier_n = 2

            fabricd_configuration.write(OPENFABRIC_ROUTER_CONFIGURATION % (self._get_net_iso_format(node), tier_n))

            # We set the overload-bit on the Leaves, in order to avoid transit traffic
            if type(node) == Leaf:
                fabricd_configuration.write(" set-overload-bit\n")

            ips_to_define = {}
            for interface in node.interfaces:
                # Enable OpenFabric on node interfaces
                fabricd_configuration.write(OPENFABRIC_IFACE_CONFIGURATION % interface.get_name())

                # Loopbacks and Server Interfaces are passive, we do not need to form adjacency with them
                if 'lo' in interface.get_name() or (type(node) == Leaf and 'server' in interface.neighbours[0][0]):
                    fabricd_configuration.write(" openfabric passive\n")

                    # Loopbacks and Server IP Addresses are also written in the zebra.conf file, in order to announce
                    # them on OpenFabric
                    ips_to_define[interface.get_name()] = str(interface.ip_address) + "/" + \
                                                          str(interface.network.prefixlen)

        with open('%s/%s/etc/frr/zebra.conf' % (lab.lab_dir_name, node.name), 'w') as zebra_configuration:
            zebra_configuration.write(ZEBRA_CONFIG)

            # We write the previously saved IP Addresses
            for interface_name, ip in ips_to_define.items():
                zebra_configuration.write(ZEBRA_IFACE_CONFIGURATION % (interface_name, ip))

        # The startup file is overwritten in OpenFabric
        # Interfaces do not need an IP address (if it is defined, it is announced, but we want to skip that)
        # The only IP Address assigned is on Leaves, in particular on Server interface, since
        # the test framework needs the Server Prefix written in the routing kernel table
        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'w') as startup:
            for interface_name, ip in filter(lambda x: '200.' in x[1] and '/24' in x[1], ips_to_define.items()):
                startup.write('ifconfig %s %s up\n' % (interface_name, ip))

            startup.write('/etc/init.d/frr start\n')

    @staticmethod
    def _get_net_iso_format(node):
        """
        Takes a node and return a net in iso format from the ipv4 address of the first interface of node
        :param node: (Node) the node for which you want the net id in iso format
        :return: (string) a net identifier in iso format
        """
        area = "49.0000"
        s = "".join(map(lambda x: '%03d' % int(x), str(node.interfaces[0].ip_address).split('.')))

        return '%s.%s.%s.%s.00' % (area, s[0:4], s[4:8], s[8:12])
