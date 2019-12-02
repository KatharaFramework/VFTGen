from model.FatTree import FatTree
from model.node.Node import Node
from networking.BGPConfigurator import BGPConfigurator
from networking.OpenFabricConfigurator import OpenFabricConfigurator
import os


class Laboratory(object):
    @staticmethod
    def write_kathara_lab_conf(node: Node):
        with open('lab/lab.conf', 'a') as lab_config:
            server_added = False
            for interface in node.interfaces:
                if 'server' not in interface.neighbour_name or not server_added:
                    if 'server' in interface.neighbour_name:
                        server_added = True
                    lab_config.write('%s[%d]="%s"\n' % (node.name, interface.number, interface.collision_domain))

    @staticmethod
    def write_kathara_startup(node: Node):
        os.mkdir('lab/%s' % node.name)
        os.mkdir('lab/%s/etc' % node.name)
        with open('lab/%s.startup' % node.name, 'a') as startup:
            server_added = False
            for interface in node.interfaces:
                if 'server' not in interface.neighbour_name or not server_added:
                    if 'server' in interface.neighbour_name:
                        server_added = True
                    startup.write('ifconfig eth%d %s/%s up\n' % (interface.number, str(interface.ip_address),
                                                             str(interface.network.prefixlen)))
            if node.role == 'server':
                startup.write('route add default gw %s\n' % node.interfaces[0].neighbour_ip)
                startup.write('/etc/init.d/apache2 start\n')

    def write_kathara_configurations(self, topology: FatTree):
        for (pod_name, pod) in topology.pods.items():
            for (node_name, node) in pod.items():
                self.write_kathara_lab_conf(node)
                self.write_kathara_startup(node)

        for (node_name, node) in topology.aggregation_layer.items():
            self.write_kathara_lab_conf(node)
            self.write_kathara_startup(node)

    @staticmethod
    def write_kathara_bgp_configuration(topology: FatTree):
        bgp_configurator = BGPConfigurator()
        for (pod_name, pod) in topology.pods.items():
            for (node_name, node) in pod.items():
                if node.role != 'server':
                    bgp_configurator.write_bgp_configuration(node)

        for (node_name, node) in topology.aggregation_layer.items():
            bgp_configurator.write_bgp_configuration(node)

    @staticmethod
    def write_kathara_openfabric_configuration(topology: FatTree):
        openfabric_configurator = OpenFabricConfigurator()
        for (pod_name, pod) in topology.pods.items():
            for (node_name, node) in pod.items():
                if node.role != 'server':
                    openfabric_configurator.configure_node(node)

        for (node_name, node) in topology.aggregation_layer.items():
            openfabric_configurator.configure_node(node)
