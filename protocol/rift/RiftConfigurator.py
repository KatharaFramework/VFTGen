import os
import shutil

from ..IConfigurator import IConfigurator
from model.node.Node import Node
from model.node_types.Tof import Tof
from model.node_types.Leaf import Leaf
from model.node_types.Server import Server
from model.node_types.Spine import Spine

# --------------------------- Start of Rift configuration templates ---------------------------------------------

RIFT_CONFIG_TEMPLATE = \
    """
shards:
  - id: 0
    nodes:
      - name: %s
        level: %s
        interfaces:
    """
RIFT_CONFIG_INTERFACE_TEMPLATE = \
    """      
         - name: eth%s
         
"""

RIFT_CONFIG_V4PREFIXES_TEMPLATE = \
    """     
        v4prefixes:
          - address: %s
            mask: 30
            metric: 1 
"""

RIFT_CONFIG_INTERFACE_SERVER_TEMPLATE = \
    """      
             - name: eth%s
               advertise_subnet: true
    """

# --------------------------- End of Rift configuration templates ---------------------------------------------


RIFT_PYTHON_DIR = "D:\\Documenti\\Università\\Magistrale\\Tirocinio\\rift-python"


class RiftConfigurator(IConfigurator):
    """
    This class is used to write the RIFT configuration of nodes in a FatTree object
    RIFT is implemented using rift-python (https://github.com/brunorijsman/rift-python) and deploying it in
    kathara containers
    """
    def _configure_node(self, lab, node: Node):
        """
        Write the rift configuration for the node
        :param lab: a Laboratory object (used to take information about the laboratory dir)
        :param node: a Node object of a FatTree topology
        :return:
        """
        if type(node != Server):
            with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
                lab_config.write('%s[image]="kathara/rift-python"\n' % node.name)
                os.mkdir('%s/%s/etc/rift' % (lab.lab_dir_name, node.name))
                with open('%s/%s/etc/rift/config.yaml' % (lab.lab_dir_name, node.name), 'w') as rift_config:
                    node_level = 'undefined'
                    if type(node) == Leaf:
                        node_level = 'leaf'
                    elif type(node) == Tof:
                        node_level = 'top-of-fabric'

                    rift_config.write(RIFT_CONFIG_TEMPLATE % (node.name, node_level))
                    for interface in node.interfaces:
                        rift_config.write(RIFT_CONFIG_INTERFACE_TEMPLATE % interface.number)
                    if type(node) == Leaf:
                        server_interface = list(filter(lambda interface: '/24' in str(interface.network), node.interfaces))
                        rift_config.write(
                            RIFT_CONFIG_V4PREFIXES_TEMPLATE % str(server_interface[0].network.network_address)
                        )
                with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
                    startup.write(
                        "python3 /shared/rift --ipv4-multicast-loopback-disable /etc/rift/config.yaml &\n")
        if not os.path.isdir("%s/shared/rift" % lab.lab_dir_name):
            shutil.copytree(
                "D:\\Documenti\\Università\\Magistrale\\Tirocinio\\rift-python\\rift", "%s/shared/rift"
                                                                                       % lab.lab_dir_name
            )

    @staticmethod
    def _get_system_id(node: Node):
        """
        Takes a node abject and returns a system_id for that node
        :param node: a Node object of a FatTree topology
        :return:
        """
        name = node.name.split('_')
        if type(node) != Tof:

            pod_number = name[1]
            node_level = name[2]
            node_number = name[3]
            system_id = pod_number + node_level + node_number
            print(system_id)
            return system_id
        else:
            node_level = name[1]
            node_number = name[2]
            system_id = node_level + node_number
            print(system_id)
            return system_id
