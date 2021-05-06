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
            self.current_collision_domain = None
            self.collision_domain_assignments = {}

            self.reset()

            CollisionDomain.__instance = self

    def reset(self):
        self.current_collision_domain = ('A', 'A', 'A', '@')
        self.collision_domain_assignments = {}

    def get_collision_domain(self, first_node, second_node, link_id=0):
        """
        Takes two nodes names and returns a collision domain (a new one if it has not yet been set)
        :param first_node: (string) a name of a node
        :param second_node: (string) a name of a node
        :param link_id: (int) the id of the link, unique among the links between first_node and second_node
        :return: a four ASCII char collision domain "XXXX" ("XXXX" is a new one if it is the first time that the
                 function sees the tuple (node_name1, node_name2, link_id))
        """
        if 'leaf' in first_node and 'server' in second_node or 'leaf' in second_node and 'server' in first_node:
            leaf_node = first_node if 'leaf' in first_node else second_node
            if (leaf_node, 'servers', link_id) in self.collision_domain_assignments:
                return self.collision_domain_assignments[(leaf_node, 'servers', link_id)]
            else:
                collision_domain = self._get_new_collision_domain()
                self.collision_domain_assignments[(leaf_node, 'servers', link_id)] = collision_domain
                return collision_domain
        elif (first_node, second_node, link_id) in self.collision_domain_assignments:
            return self.collision_domain_assignments[(first_node, second_node, link_id)]
        elif (second_node, first_node, link_id) in self.collision_domain_assignments:
            return self.collision_domain_assignments[(second_node, first_node, link_id)]
        else:
            collision_domain = self._get_new_collision_domain()
            self.collision_domain_assignments[(first_node, second_node, link_id)] = collision_domain

            return collision_domain

    def _get_new_collision_domain(self):
        """
        Get a new collision domain incrementing the string by one
        :return:
        """
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
        """
        :param first_char: the char that you want increment
        :param second_char: the char after the one you want increment
        :param inc_second: a bool used to increment the second_char in case of overflow
        :return: (first_char + 1, second_char): if there's not overflow
                 (A, second_char + 1)         : if there's overflow
        """
        if second_char >= ord('Z'):
            first_char += 1
            second_char = ord('A')
        else:
            if inc_second:
                second_char += 1

        return first_char, second_char
