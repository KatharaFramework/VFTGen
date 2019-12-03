from model.node_types.Leaf import Leaf
from model.node_types.Spine import Spine
from model.node_types.Tof import Tof


class ASManager(object):
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
            self.current_as_number = 64512
            self.max_as_number = 65534
            self.as_number_assignments = {}

            ASManager.__instance = self

    def get_as_number(self, node):
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
        if self.current_as_number <= self.max_as_number:
            as_number = self.current_as_number
            self.current_as_number += 1

            return as_number
        else:
            raise Exception('Private AS number finished!')
