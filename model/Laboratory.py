import os
import shutil

from .node_types.Server import Server


class Laboratory(object):
    __slots__ = ['lab_dir_name']

    def __init__(self, dir_name):
        self.lab_dir_name = dir_name

        if os.path.isdir(self.lab_dir_name):
            shutil.rmtree(self.lab_dir_name)

        os.mkdir(self.lab_dir_name)

    def dump(self, topology):
        for pod_name, pod in topology.pods.items():
            for node_name, node in pod.items():
                self.write_lab_conf(node)
                self.write_startup(node)

        for node_name, node in topology.aggregation_layer.items():
            self.write_lab_conf(node)
            self.write_startup(node)

    def write_lab_conf(self, node):
        with open('%s/lab.conf' % self.lab_dir_name, 'a') as lab_config:
            for interface in node.interfaces:
                lab_config.write('%s[%d]="%s"\n' % (node.name, interface.number, interface.collision_domain))

    def write_startup(self, node):
        if type(node) != Server:
            os.mkdir('%s/%s' % (self.lab_dir_name, node.name))
            os.mkdir('%s/%s/etc' % (self.lab_dir_name, node.name))

        with open('%s/%s.startup' % (self.lab_dir_name, node.name), 'a') as startup:
            server_added = False

            for interface in node.interfaces:
                startup.write('ifconfig eth%d %s/%s up\n' % (interface.number,
                                                             str(interface.ip_address),
                                                             str(interface.network.prefixlen)
                                                             ))
            if type(node) == Server:
                startup.write('route add default gw %s\n' % str(node.interfaces[0].neighbours[0][1]))
                startup.write('/etc/init.d/apache2 start\n')
