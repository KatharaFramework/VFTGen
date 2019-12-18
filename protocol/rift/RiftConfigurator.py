import os
import shutil

from model.node_types.Leaf import Leaf
from model.node_types.Server import Server
from model.node_types.Tof import Tof
from ..IConfigurator import IConfigurator

# --------------------------- Start of Rift configuration templates ---------------------------------------------
RIFT_CONFIG_TEMPLATE = \
    """
shards:
  - id: 0
    nodes:
      - name: %s
        level: %s
        interfaces:"""

RIFT_CONFIG_INTERFACE_TEMPLATE = \
    """      
         - name: eth%s"""

RIFT_CONFIG_V4PREFIXES_LOOPBACK_TEMPLATE = \
    """     
        v4prefixes:
          - address: %s
            mask: 32
            metric: 1"""

RIFT_CONFIG_V4PREFIXES_SERVER_TEMPLATE = \
    """     
          - address: %s
            mask: 24
            metric: 1"""


# --------------------------- End of Rift configuration templates ---------------------------------------------


class RiftConfigurator(IConfigurator):
    """
    This class is used to write the RIFT configuration of nodes in a FatTree object
    RIFT is implemented using rift-python (https://github.com/brunorijsman/rift-python) of Bruno Rijsman
    and deploying it in kathara containers
    """

    def _configure_node(self, lab, node):
        """
        Write the RIFT configuration for the node
        :param lab: a Laboratory object (used to take information about the laboratory dir)
        :param node: a Node object of a FatTree topology
        :return:
        """
        if type(node) != Server:
            with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
                lab_config.write('%s[image]="kathara/rift-python"\n' % node.name)

                os.mkdir('%s/%s/etc/rift' % (lab.lab_dir_name, node.name))

                with open('%s/%s/etc/rift/config.yaml' % (lab.lab_dir_name, node.name), 'w') as rift_config:
                    node_level = 'leaf' if type(node) == Leaf else 'top-of-fabric' if type(node) == Tof else \
                        'undefined'

                    rift_config.write(RIFT_CONFIG_TEMPLATE % (node.name, node_level))

                    for interface in node.get_phy_interfaces():
                        rift_config.write(RIFT_CONFIG_INTERFACE_TEMPLATE % interface.number)

                    # Announce node loopback
                    loopback_interface = node.get_lo_interfaces().pop()
                    rift_config.write(RIFT_CONFIG_V4PREFIXES_LOOPBACK_TEMPLATE % str(loopback_interface.ip_address))

                    # Announce server ips
                    if type(node) == Leaf:
                        server_interface = list(filter(lambda eth: '/24' in str(eth.network), node.interfaces))

                        rift_config.write(
                            RIFT_CONFIG_V4PREFIXES_SERVER_TEMPLATE % str(server_interface[0].network.network_address)
                        )

                with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
                    startup.write("python3 /shared/rift --ipv4-multicast-loopback-disable /etc/rift/config.yaml &\n")

        # if not os.path.isdir("%s/shared/rift" % lab.lab_dir_name):
        #     shutil.copytree(
        #         "D:\\Documenti\\Università\\Magistrale\\Tirocinio\\rift-python\\rift", "%s/shared/rift"
        #                                                                                % lab.lab_dir_name
        #     )
