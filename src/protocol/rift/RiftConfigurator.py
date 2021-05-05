import os

from ..IConfigurator import IConfigurator
from ...model.node_types.Leaf import Leaf
from ...model.node_types.Tof import Tof

# --------------------------- Start of Rift configuration templates ---------------------------------------------

RIFT_CONFIG_TEMPLATE = \
    """
shards:
  - id: 0
    nodes:
      - name: %s
        level: %s
        systemid: %d%d%d
        interfaces:"""

RIFT_CONFIG_INTERFACE_TEMPLATE = \
    """      
         - name: %s"""

RIFT_CONFIG_V4PREFIXES_TEMPLATE = \
    """
        v4prefixes:"""

RIFT_CONFIG_V4PREFIXES_SERVER_TEMPLATE = \
    """     
          - address: %s
            mask: 24
            metric: 1"""


# --------------------------- End of Rift configuration templates ---------------------------------------------


class RiftConfigurator(IConfigurator):
    """
    This class is used to write the RIFT configuration of nodes in a Fat Tree object
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
        with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
            lab_config.write('%s[image]="kathara/rift-py"\n' % node.name)

            os.mkdir('%s/%s/etc/rift' % (lab.lab_dir_name, node.name))

            with open('%s/%s/etc/rift/config.yaml' % (lab.lab_dir_name, node.name), 'w') as rift_config:
                node_level = 'leaf' if type(node) == Leaf else 'top-of-fabric' if type(node) == Tof else \
                    'undefined'

                if type(node) == Tof:
                    rift_config.write(
                        RIFT_CONFIG_TEMPLATE % (node.name, node_level, node.plane, node.level, node.number))
                else:
                    rift_config.write(
                        RIFT_CONFIG_TEMPLATE % (node.name, node_level, node.pod_number, node.level, node.number))

                for interface in node.get_phy_interfaces():
                    rift_config.write(RIFT_CONFIG_INTERFACE_TEMPLATE % interface.get_name())

                # Announce server IPs
                if type(node) == Leaf:
                    rift_config.write(RIFT_CONFIG_V4PREFIXES_TEMPLATE)

                    server_interface = list(filter(lambda eth: '/24' in str(eth.network), node.interfaces))

                    rift_config.write(
                        RIFT_CONFIG_V4PREFIXES_SERVER_TEMPLATE % str(server_interface[0].network.network_address)
                    )

            with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
                startup.write("screen -dmS rift python3 /rift/rift --ipv4-multicast-loopback-disable "
                              "--telnet-port-file /etc/rift/rift.port /etc/rift/config.yaml\n")
