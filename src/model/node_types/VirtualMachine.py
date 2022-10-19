from .Container import Container
from ..node.Node import Node


class VirtualMachine(Node):
    def __init__(self, name, containers_number):
        """
        Initialize the vm object assigning name and creating nested containers
        :param name: (string) the name of the vm node
        """
        super().__init__()
        self.role = 'vm'
        self.name = name
        self.containers_number = containers_number
        self.containers = []
        self._add_containers()

    def _add_containers(self):
        for i in range(1, self.containers_number + 1):
            container_name = f"{self.name.replace('vm', 'container')}_{i}"
            self.containers.append(Container(container_name))
