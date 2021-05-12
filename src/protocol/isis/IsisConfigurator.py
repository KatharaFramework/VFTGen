import os

from ..IConfigurator import IConfigurator
from ...model.node_types.Leaf import Leaf

# --------------------------- Start of ISIS configuration templates ---------------------------------------------

ZEBRA_CONFIG = \
    """hostname frr
password frr
enable password frr

"""

ZEBRA_IFACE_CONFIGURATION = """
interface %s
 ip address %s
"""

ISIS_ROUTER_CONFIGURATION = """router isis 1
 net %s
 is-type level-2-only
 max-lsp-lifetime 65535
 lsp-refresh-interval 65000
 lsp-gen-interval 1
 spf-interval 1
"""

ISIS_IFACE_CONFIGURATION = """
interface %s
 ip router isis 1
 isis network point-to-point
 isis circuit-type level-2-only
"""


# --------------------------- End of ISIS configuration templates -----------------------------------------------


class IsisConfigurator(IConfigurator):
    """
    This class is used to write the ISIS configuration of nodes in a FatTree object
    """

    def _configure_node(self, lab, node):
        """
        Write the ISIS configuration for the node
        :param lab: a Laboratory object (used to take information about the laboratory dir)
        :param node: a Node object of a FatTree topology
        :return:
        """
        with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
            lab_config.write('%s[image]="kathara/frr"\n' % node.name)

        os.mkdir('%s/%s/etc/frr' % (lab.lab_dir_name, node.name))
        with open('%s/%s/etc/frr/daemons' % (lab.lab_dir_name, node.name), 'w') as daemons:
            daemons.write('zebra=yes\n')
            daemons.write('isisd=yes\n')

        with open('%s/%s/etc/frr/isisd.conf' % (lab.lab_dir_name, node.name), 'w') as isisd_configuration:
            isisd_configuration.write(ISIS_ROUTER_CONFIGURATION % (self._get_net_iso_format(node)))

            # We set the overload-bit on the Leaves, in order to avoid transit traffic
            if type(node) == Leaf:
                isisd_configuration.write(" set-overload-bit\n")

            loopback_ip = None
            ips_to_define = {}
            for interface in node.interfaces:
                # Enable ISIS on node interfaces
                isisd_configuration.write(ISIS_IFACE_CONFIGURATION % interface.get_name())

                # Server Interfaces are passive, we do not need to form adjacency with them
                if 'lo' not in interface.get_name() and (type(node) == Leaf and 'server' in interface.neighbours[0][0]):
                    isisd_configuration.write(" isis passive\n")

                    ips_to_define[interface.get_name()] = str(interface.ip_address) + "/" + \
                                                          str(interface.network.prefixlen)

                # Store Loopback IP (it is needed for zebra.conf configuration)
                if 'lo' in interface.get_name():
                    loopback_ip = str(interface.ip_address)

        with open('%s/%s/etc/frr/zebra.conf' % (lab.lab_dir_name, node.name), 'w') as zebra_configuration:
            zebra_configuration.write(ZEBRA_CONFIG)

            # In order to run ISIS with unnumbered p2p networks, the loopback IP should be defined on each interface
            # As stated in https://github.com/FRRouting/frr/issues/8397#issuecomment-813829356
            for interface in node.interfaces:
                zebra_configuration.write(ZEBRA_IFACE_CONFIGURATION % (interface.get_name(), loopback_ip + "/32"))

        # The startup file is overwritten in ISIS
        # Interfaces do not need an IP address (see the zebra.conf description above)
        # The only IP Address assigned is on Leaves, in particular on Server interface, since
        # the test framework needs the Server Prefix written in the routing kernel table
        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'w') as startup:
            for interface_name, ip in ips_to_define.items():
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
