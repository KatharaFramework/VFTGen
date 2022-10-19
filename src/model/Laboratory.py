import os

from .node_types.Container import Container
from .node_types.Server import Server
from .node_types.VirtualMachine import VirtualMachine


class Laboratory(object):
    """
    This class is used to generate the kathara configuration from a topology object (FatTree)
    """
    __slots__ = ['lab_dir_name']

    def __init__(self, dir_name):
        self.lab_dir_name = dir_name

    def dump(self, topology):
        """
        write the lab.conf and the node.startup for each node in the topology
        :param topology: a FatTree object that represents a clos topology
        :return:
        """
        for pod_name, pod in topology.pods.items():
            for node_name, node in pod.items():
                self.write_lab_conf(self.lab_dir_name, node)
                self.write_startup(self.lab_dir_name, node)

        for node_name, node in topology.aggregation_layer.items():
            self.write_lab_conf(self.lab_dir_name, node)
            self.write_startup(self.lab_dir_name, node)

    def write_lab_conf(self, path, node):
        """
        append the lab.conf configuration for the node
        :param path: the path where the lab.conf is created
        :param node: a Node object (Leaf | Spine | Server | Tof)
        :return:
        """
        with open(os.path.join(path, "lab.conf"), 'a') as lab_config:
            for interface in node.get_phy_interfaces():
                lab_config.write('%s[%d]="%s"\n' % (node.name, interface.number, interface.collision_domain))

            if type(node) != Server and type(node) != VirtualMachine and type(node) != Container:
                lab_config.write('%s[sysctl]="net.ipv4.fib_multipath_hash_policy=1"\n' % node.name)

            if (type(node) == Server and node.vms_number > 0) or \
                    (type(node) == VirtualMachine and node.containers_number > 0):
                lab_config.write(f'{node.name}[nested]="true"\n')

            if type(node) == Container:
                lab_config.write(f'{node.name}[mem]="64M"\n')

    def write_startup(self, path, node):
        """
        write the (node.name).startup file for the node
        :param path: the path where the startup file is created
        :param node: a Node object (Leaf | Spine | Server | Tof)
        :return:
        """
        os.mkdir(os.path.join(path, node.name))

        if type(node) != Server:
            os.mkdir('%s/%s/etc' % (self.lab_dir_name, node.name))

        if type(node) == Server:
            if node.vms_number > 0:
                server_sublab_path = os.path.join(self.lab_dir_name, node.name, "sublab")
                os.mkdir(server_sublab_path)
                for vm in node.vms:
                    self.write_lab_conf(server_sublab_path, vm)
                    vm_sublab_path = os.path.join(server_sublab_path, vm.name)
                    os.mkdir(vm_sublab_path)
                    for container in vm.containers:
                        self.write_lab_conf(vm_sublab_path, container)

        with open('%s/%s.startup' % (self.lab_dir_name, node.name), 'a') as startup:
            for interface in node.interfaces:
                startup.write('ifconfig %s %s/%s up\n' % (interface.get_name(),
                                                          str(interface.ip_address),
                                                          str(interface.network.prefixlen)
                                                          )
                              )

            if type(node) == Server:
                startup.write('route add default gw %s\n' % str(node.interfaces[0].neighbours[0][1]))
                startup.write('/etc/init.d/apache2 start\n')
