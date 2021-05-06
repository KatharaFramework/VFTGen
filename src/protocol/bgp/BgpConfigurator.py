import os

from .ASManager import ASManager
from ..IConfigurator import IConfigurator

# --------------------------- Start of BGP configuration templates -----------------------------------------------

ZEBRA_CONFIG = \
    """hostname frr
password frr
enable password frr
"""

ROUTE_MAP = \
    """
ip prefix-list DC_LOCAL_SUBNET seq 5 permit 10.0.0.0/8 le 30
ip prefix-list DC_LOCAL_SUBNET seq 10 permit 200.0.0.0/8 le 24
route-map ACCEPT_DC_LOCAL permit 10
 match ip address prefix-list DC_LOCAL_SUBNET
"""

BGPD_BASIC_CONFIG = \
    """
router bgp {as_number}
 timers bgp 3 9
 bgp router-id {router_id}
 no bgp ebgp-requires-policy
 bgp bestpath as-path multipath-relax
 bgp bestpath compare-routerid
{neighbor_config}"""

NEIGHBOR_GROUP_CONFIG = \
    """ 
neighbor {group} peer-group
 neighbor {group} remote-as external
 neighbor {group} advertisement-interval 0
 neighbor {group} timers connect 5
"""

NEIGHBOR_PEER = """ neighbor %s interface peer-group %s\n"""

BGPD_ADDRESS_FAMILY = \
    """
{before}
address-family ipv4 unicast
  {neighbours}
  {announced_networks}
  maximum-paths 64
exit-address-family"""
BGPD_LEAF_CONFIG = BGPD_ADDRESS_FAMILY.format(before="",
                                              neighbours="neighbor TOR activate",
                                              announced_networks="__announced_networks__"
                                              )
BGPD_SPINE_CONFIG = BGPD_ADDRESS_FAMILY.format(before="",
                                               neighbours="neighbor fabric activate\n  neighbor TOR activate",
                                               announced_networks=""
                                               )
BGPD_TOF_CONFIG = BGPD_ADDRESS_FAMILY.format(before="",
                                             neighbours="neighbor fabric activate",
                                             announced_networks=""
                                             )


# ---------------------------  End of BGP configuration templates -----------------------------------------------


class BgpConfigurator(IConfigurator):
    """
    This class is used to write the BGP configuration of nodes in a FatTree object
    """

    def __init__(self):
        ASManager.get_instance().reset()

    def _configure_node(self, lab, node):
        """
        Write the bgp configuration for the node
        :param lab: a Laboratory object (used to take information about the laboratory dir)
        :param node: a Node object of a FatTree topology
        :return:
        """
        with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
            lab_config.write('%s[image]="kathara/frr"\n' % node.name)

        os.mkdir('%s/%s/etc/frr' % (lab.lab_dir_name, node.name))
        with open('%s/%s/etc/frr/daemons' % (lab.lab_dir_name, node.name), 'w') as daemons:
            daemons.write('zebra=yes\n')
            daemons.write('bgpd=yes\n')

        with open('%s/%s/etc/frr/zebra.conf' % (lab.lab_dir_name, node.name), 'w') as zebra_configuration:
            zebra_configuration.write(ZEBRA_CONFIG)

        with open('%s/%s/etc/frr/bgpd.conf' % (lab.lab_dir_name, node.name), 'w') as bgpd_configuration:
            bgpd_configuration.write(ZEBRA_CONFIG)

            self._write_route_map(bgpd_configuration)

            method_name = "_write_bgp_%s_configuration" % node.role
            write_node_configuration = getattr(self, method_name)
            write_node_configuration(node, bgpd_configuration)

        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
            startup.write('/etc/init.d/frr start\n')

    @staticmethod
    def _write_route_map(bgpd_configuration):
        """
        write the route-map ROUTE_MAP in bgpd_configuration file
        :param bgpd_configuration: the /etc/frr/bgpd.conf file of a Node in the FatTree topology
        :return:
        """
        bgpd_configuration.write(ROUTE_MAP)

    @staticmethod
    def _write_bgp_leaf_configuration(node, bgpd_configuration):
        """
        write the bgp configuration of Leaf Node
        :param node: a Leaf node
        :param bgpd_configuration: the /etc/frr/bgpd.conf file of the Leaf node in the FatTree topology
        :return:
        """
        loopback_interface = node.get_lo_interfaces().pop()

        bgpd_configuration.write(
            BGPD_BASIC_CONFIG.format(as_number=ASManager.get_instance().get_as_number(node),
                                     router_id=str(loopback_interface.ip_address),
                                     neighbor_config=NEIGHBOR_GROUP_CONFIG.format(group="TOR")
                                     )
        )

        for interface in node.get_phy_interfaces():
            if 'spine' in interface.neighbours[0][0]:
                bgpd_configuration.write(NEIGHBOR_PEER % (interface.get_name(), "TOR"))

        server_interfaces = list(filter(lambda x: x.network.prefixlen == 24, node.get_phy_interfaces()))
        server_networks = ["network %s" % iface.network for iface in server_interfaces]

        bgpd_configuration.write(
            BGPD_LEAF_CONFIG.replace('__announced_networks__', "\n  ".join(server_networks))
        )

    @staticmethod
    def _write_bgp_spine_configuration(node, bgpd_configuration):
        """
        write the bgp configuration of Spine Node
        :param node: a Spine node
        :param bgpd_configuration: the /etc/frr/bgpd.conf file of the Spine node in the FatTree topology
        :return:
        """
        loopback_interface = node.get_lo_interfaces().pop()

        bgpd_configuration.write(
            BGPD_BASIC_CONFIG.format(as_number=ASManager.get_instance().get_as_number(node),
                                     router_id=str(loopback_interface.ip_address),
                                     neighbor_config="\n".join([NEIGHBOR_GROUP_CONFIG.format(group="TOR"),
                                                                NEIGHBOR_GROUP_CONFIG.format(group="fabric")
                                                                ]
                                                               )
                                     )
        )

        for interface in node.get_phy_interfaces():
            if 'leaf' in interface.neighbours[0][0]:
                bgpd_configuration.write(NEIGHBOR_PEER % (interface.get_name(), "TOR"))

        for interface in node.get_phy_interfaces():
            if 'spine' in interface.neighbours[0][0] or 'tof' in interface.neighbours[0][0]:
                bgpd_configuration.write(NEIGHBOR_PEER % (interface.get_name(), "fabric"))

        bgpd_configuration.write(BGPD_SPINE_CONFIG)

    @staticmethod
    def _write_bgp_tof_configuration(node, bgpd_configuration):
        """
        write the bgp configuration of Tof Node
        :param node: a Tof node
        :param bgpd_configuration: the /etc/frr/bgpd.conf file of the Tof node in the FatTree topology
        :return:
        """
        loopback_interface = node.get_lo_interfaces().pop()

        bgpd_configuration.write(
            BGPD_BASIC_CONFIG.format(as_number=ASManager.get_instance().get_as_number(node),
                                     router_id=str(loopback_interface.ip_address),
                                     neighbor_config=NEIGHBOR_GROUP_CONFIG.format(group="fabric")
                                     )
        )

        for interface in node.get_phy_interfaces():
            if 'spine' in interface.neighbours[0][0] or 'tof' in interface.neighbours[0][0]:
                bgpd_configuration.write(NEIGHBOR_PEER % (interface.get_name(), "fabric"))

        bgpd_configuration.write(BGPD_TOF_CONFIG)
