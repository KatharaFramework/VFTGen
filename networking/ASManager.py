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

    def get_new_as_number(self):
        if self.current_as_number <= self.max_as_number:
            as_number = self.current_as_number
            self.current_as_number += 1
            return as_number
        else:
            raise Exception('private AS number finished')

    def get_as_number(self, node):
        as_number = 0
        if node.role == 'leaf':
            as_number = self.get_new_as_number()
            self.as_number_assignments[(node.pod_number, node.level)] = as_number
        elif node.role == 'spine':

            if (node.pod_number, node.level) in self.as_number_assignments:
                as_number = self.as_number_assignments[(node.pod_number, node.level)]
            else:
                as_number = self.get_new_as_number()
                self.as_number_assignments[(node.pod_number, node.level)] = as_number
        elif node.role == 'tof':
            if (-1, node.level) in self.as_number_assignments:
                as_number = self.as_number_assignments[(-1, node.level)]
            else:
                as_number = self.get_new_as_number()
                self.as_number_assignments[(-1, node.level)] = as_number
        return as_number


