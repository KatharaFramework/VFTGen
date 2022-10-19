from .VirtualMachine import VirtualMachine
from ..node.Node import Node
from ...networking.CollisionDomain import CollisionDomain


class Server(Node):
    def __init__(self, name, vm_number, containers_per_vm, connected_leaf_name):
        """
        Initialize the server object assigning name and populating its neighbours (only the leaf to which it is
        connected)
        :param name: (string) the name of the server node
        :param connected_leaf_name: (string) the name of the leaf to which this server is connected
        """
        super().__init__()
        self.role = 'server'
        self.name = name
        self.vms_number = vm_number
        self.vms = []
        self._add_neighbours(connected_leaf_name)
        self._assign_ipv4_address_to_interfaces()
        self._add_vms(containers_per_vm)

    def _add_neighbours(self, connected_leaf_name):
        self.neighbours.append((connected_leaf_name,
                                CollisionDomain.get_instance().get_collision_domain(self.name, connected_leaf_name)
                                )
                               )

    def _add_vms(self, containers_per_vm):
        for i in range(1, self.vms_number + 1):
            vm_name = f"{self.name.replace('server', 'vm')}_{i}"
            vm = VirtualMachine(vm_name, containers_per_vm)
            self.vms.append(vm)

