class CollisionDomain(object):
    __slots__ = ['current_collision_domain', 'collision_domain_assignments']

    __instance = None

    @staticmethod
    def get_instance():
        if CollisionDomain.__instance is None:
            CollisionDomain()

        return CollisionDomain.__instance

    def __init__(self):
        if CollisionDomain.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.current_collision_domain = ('A', 'A', 'A', '@')

            self.collision_domain_assignments = {}

            CollisionDomain.__instance = self

    def get_collision_domain(self, first_node, second_node):
        """
        Takes two nodes names and returns a collision domain (a new one if it has not yet been set)
        :param first_node: (string) a name of a node
        :param second_node: (string) a name of a node
        :return: a four ASCII char collision domain "XXXX" ("XXXX" is a new one if it is the first time that the function
                 sees the couple (node_name1, node_name2))
        """
        if (first_node, second_node) in self.collision_domain_assignments:
            return self.collision_domain_assignments[(first_node, second_node)]
        elif (second_node, first_node) in self.collision_domain_assignments:
            return self.collision_domain_assignments[(second_node, first_node)]
        else:
            collision_domain = self._get_new_collision_domain()
            self.collision_domain_assignments[(first_node, second_node)] = collision_domain

            return collision_domain

    def _get_new_collision_domain(self):
        (first, second, third, fourth) = self.current_collision_domain
        first, second, third, fourth = ord(first), ord(second), ord(third), ord(fourth)

        (third, fourth) = self._get_next_char(third, fourth, inc_second=True)
        (second, third) = self._get_next_char(second, third)
        (first, second) = self._get_next_char(second, first)

        first, second, third, fourth = chr(first), chr(second), chr(third), chr(fourth)
        self.current_collision_domain = (first, second, third, fourth)

        return "".join(list(self.current_collision_domain))

    @staticmethod
    def _get_next_char(first_char, second_char, inc_second=False):
        if second_char >= ord('Z'):
            first_char += 1
            second_char = ord('A')
        else:
            if inc_second:
                second_char += 1

        return first_char, second_char
