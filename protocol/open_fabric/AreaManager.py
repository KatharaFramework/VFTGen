from model.node_types.Leaf import Leaf
from model.node_types.Spine import Spine
from model.node_types.Tof import Tof


class AreaManager(object):
    __slots__ = ['net_template']

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

            AreaManager.__instance = self

    def get_net_number(self, node):
        if type(node) == Leaf or type(node) == Spine:
            return self._get_new_net_number(node.pod_number)

        if type(node) == Tof:
            return self._get_new_net_number(0)

    def _get_new_net_number(self, pod_number):
        return self.net_template % pod_number
