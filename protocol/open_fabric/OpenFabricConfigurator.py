import os

from model.node_types.Server import Server
from .AreaManager import AreaManager
from ..IConfigurator import IConfigurator

# --------------------------- Start of OpenFabric configuration templates ---------------------------------------------

OPENFABRIC_ROUTER_CONFIGURATION = """router openfabric %s
 net %s
"""

OPENFABRIC_IFACE_CONFIGURATION = """
interface %s
 ip router openfabric %s
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
            if type(node) != Server:
                lab_config.write('%s[sysctl]="net.ipv4.fib_multipath_hash_policy=1"\n' % node.name)

        os.mkdir('%s/%s/etc/frr' % (lab.lab_dir_name, node.name))
        with open('%s/%s/etc/frr/daemons' % (lab.lab_dir_name, node.name), 'w') as daemons:
            daemons.write('zebra=yes\n')
            daemons.write('fabricd=yes\n')

        with open('%s/%s/etc/frr/fabricd.conf' % (lab.lab_dir_name, node.name), 'w') as fabricd_configuration:
            fabricd_configuration.write(OPENFABRIC_ROUTER_CONFIGURATION %
                                        (node.name, self._get_net_iso_format(node))
                                        )

            if 'leaf' in node.name:
                fabricd_configuration.write("\nfabric-tier 0\n")

            for interface in node.get_phy_interfaces():
                fabricd_configuration.write(OPENFABRIC_IFACE_CONFIGURATION % (interface.get_name(), node.name))

        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
            startup.write('/etc/init.d/frr start\n')

    @staticmethod
    def _get_net_iso_format(node):
        """
        Takes a node and return a net in iso format from the ipv4 address of the first interface of node
        :param node: (Node) the node for which you want the net id in iso format
        :return: (string) a net identifier in iso format
        """
        s = "".join(map(lambda x: '%03d' % int(x), str(node.interfaces[0].ip_address).split('.')))
        area = AreaManager.get_instance().get_net_number(node)

        return '%s.%s.%s.%s.00' % (area, s[0:4], s[4:8], s[8:12])
