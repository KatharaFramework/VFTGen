import os
import shutil

from .node_types.Server import Server


class Laboratory(object):
    """
    This class is used to generate the kathara configuration from a topology object (FatTree)
    """
    __slots__ = ['lab_dir_name']

    def __init__(self, dir_name):
        self.lab_dir_name = dir_name

        if os.path.isdir(self.lab_dir_name):
            shutil.rmtree(self.lab_dir_name)

        os.mkdir(self.lab_dir_name)

    def dump(self, topology):
        """
        write the lab.conf and the node.startup for each node in the topology
        :param topology: a FatTree object that represents a clos topology
        :return:
        """
        for pod_name, pod in topology.pods.items():
            for node_name, node in pod.items():
                self.write_lab_conf(node)
                self.write_startup(node)

        for node_name, node in topology.aggregation_layer.items():
            self.write_lab_conf(node)
            self.write_startup(node)

    def write_lab_conf(self, node):
        """
        append the lab.conf configuration for the node
        :param node: a Node object (Leaf | Spine | Server | Tof)
        :return:
        """
        with open('%s/lab.conf' % self.lab_dir_name, 'a') as lab_config:
            for interface in node.get_phy_interfaces():
                lab_config.write('%s[%d]="%s"\n' % (node.name, interface.number, interface.collision_domain))

    def write_startup(self, node):
        """
        write the (node.name).startup file for the node
        :param node: a Node object (Leaf | Spine | Server | Tof)
        :return:
        """
        if type(node) != Server:
            os.mkdir('%s/%s' % (self.lab_dir_name, node.name))
            os.mkdir('%s/%s/etc' % (self.lab_dir_name, node.name))

        with open('%s/%s.startup' % (self.lab_dir_name, node.name), 'a') as startup:
            for interface in node.interfaces:
                startup.write('ifconfig %s %s/%s up &&\n' % (interface.get_name(),
                                                          str(interface.ip_address),
                                                          str(interface.network.prefixlen)
                                                          )
                              )

            if type(node) == Server:
                startup.write('route add default gw %s\n' % str(node.interfaces[0].neighbours[0][1]))
                startup.write('/etc/init.d/apache2 start\n')
