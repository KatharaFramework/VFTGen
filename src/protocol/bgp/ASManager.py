from ...model.node_types.Leaf import Leaf
from ...model.node_types.Spine import Spine
from ...model.node_types.Tof import Tof


class ASManager(object):
    """
    Singleton class that manage the AS number for the BGP configurations
    """
    __slots__ = ['current_as_number', 'max_as_number', 'as_number_assignments']

    __instance = None

    @staticmethod
    def get_instance():
        if ASManager.__instance is None:
            ASManager()

        return ASManager.__instance

    def __init__(self):
        if ASManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.current_as_number = None
            self.max_as_number = None
            self.as_number_assignments = {}

            self.reset()

            ASManager.__instance = self

    def reset(self):
        self.current_as_number = 64512
        self.max_as_number = 65534
        self.as_number_assignments = {}

    def get_as_number(self, node):
        """
        Takes a node Node in input and returns the correct AS number for that node
        :param node:
        :return: (int) the correct AS number for node
        """
        if type(node) == Leaf:
            return self._get_new_as_number()

        if type(node) == Spine:
            if (node.pod_number, node.level) in self.as_number_assignments:
                return self.as_number_assignments[(node.pod_number, node.level)]
            else:
                as_number = self._get_new_as_number()
                self.as_number_assignments[(node.pod_number, node.level)] = as_number

                return as_number

        if type(node) == Tof:
            if (-1, node.level) in self.as_number_assignments:
                return self.as_number_assignments[(-1, node.level)]
            else:
                as_number = self._get_new_as_number()
                self.as_number_assignments[(-1, node.level)] = as_number

                return as_number

    def _get_new_as_number(self):
        """
        Returns a new AS number and increment the current_as_number
        :return: (int) a new AS number
        """
        if self.current_as_number <= self.max_as_number:
            as_number = self.current_as_number
            self.current_as_number += 1

            return as_number
        else:
            raise Exception('Private AS number finished!')
