current_id1 = "A"
current_id2 = "A"
current_id3 = "A"
current_id4 = "@"

collision_domains = {}


def get_collision_domain(node_name1, node_name2):
    """
    Takes two nodes names and returns a collision domain (a new one if it has not yet been set)
    :param node_name1: (string) a name of a node
    :param node_name2: (string) a name of a node
    :return: a four ascii char collision domain "XXXX" ("XXXX" is a new one if it is the first time that the function
             sees the couple (node_name1, node_name2)
    """
    if (node_name1, node_name2) in collision_domains.keys():
        return collision_domains.get((node_name1, node_name2))
    elif (node_name2, node_name1) in collision_domains.keys():
        return collision_domains.get((node_name2, node_name1))
    else:
        collision_domain = get_new_collision_domain()
        collision_domains[(node_name1, node_name2)] = collision_domain
        return collision_domain


def get_new_collision_domain():
    """
    Returns a new collision domain
    :return: a collision domain not used until now
    """
    global current_id1, current_id2, current_id3, current_id4
    ascii_int1 = ord(current_id1[0])
    ascii_int2 = ord(current_id2[0])
    ascii_int3 = ord(current_id3[0])
    ascii_int4 = ord(current_id4[0])

    if ascii_int4 >= ord('Z'):
        ascii_int3 += 1
        ascii_int4 = ord('A')
    else:
        ascii_int4 += 1

    if ascii_int3 >= ord('Z'):
        ascii_int2 += 1
        ascii_int3 = ord('A')

    if ascii_int2 >= ord('Z'):
        ascii_int1 += 1
        ascii_int2 = ord('A')

    current_id1 = chr(ascii_int1)
    current_id2 = chr(ascii_int2)
    current_id3 = chr(ascii_int3)
    current_id4 = chr(ascii_int4)

    return current_id1 + current_id2 + current_id3 + current_id4

