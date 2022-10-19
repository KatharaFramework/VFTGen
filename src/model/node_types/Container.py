from ..node.Node import Node
from ...networking.CollisionDomain import CollisionDomain


class Container(Node):
    def __init__(self, name):
        """
        Initialize the container object.
        :param name: (string) the name of the container node
        """
        super().__init__()
        self.role = 'container'
        self.name = name
