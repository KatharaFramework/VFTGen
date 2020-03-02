from model.node_types.Leaf import Leaf
from model.node_types.Spine import Spine
from model.node_types.Tof import Tof


class AreaManager(object):
    __slots__ = ['net_template', 'net_number', 'net_number_assignments']

    __instance = None

    @staticmethod
    def get_instance():
        if AreaManager.__instance is None:
            AreaManager()

        return AreaManager.__instance

    def __init__(self):
        if AreaManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.net_template = "49.%04d"
            self.net_number = 1
            self.net_number_assignments = {}

            AreaManager.__instance = self

    def get_net_number(self, node):
        """
        Takes a node Node in input and returns the correct Net number for that node
        :param node:
        :return: (string) the correct Net number for node
        """
        if type(node) == Leaf:
            return self._get_new_net_number()

        if type(node) == Spine:
            if (node.pod_number, node.level) in self.net_number_assignments:
                return self.net_number_assignments[(node.pod_number, node.level)]
            else:
                net_number = self._get_new_net_number()
                self.net_number_assignments[(node.pod_number, node.level)] = net_number

                return net_number

        if type(node) == Tof:
            if (-1, node.level) in self.net_number_assignments:
                return self.net_number_assignments[(-1, node.level)]
            else:
                net_number = self._get_new_net_number()
                self.net_number_assignments[(-1, node.level)] = net_number

                return net_number

    # def get_net_number(self, node):
    #     if type(node) == Leaf or type(node) == Spine:
    #         return self._get_new_net_number(node.pod_number)
    #
    #     if type(node) == Tof:
    #         return self._get_new_net_number(0)

    def _get_new_net_number(self):
        """
        Returns a new Net number and increment the current_net_number
        :return: (string) a new Net number
        """
        net_number = self.net_number
        self.net_number += 1

        return self.net_template % net_number

    # def _get_new_net_number(self, pod_number):
    #     return self.net_template % pod_number
