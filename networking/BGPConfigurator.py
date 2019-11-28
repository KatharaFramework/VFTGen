from model.node import Node
from networking.ASManager import ASManager
import os


class BGPConfigurator(object):
    __instance = None

    @staticmethod
    def get_instance():
        if BGPConfigurator.__instance is None:
            BGPConfigurator()

        return BGPConfigurator.__instance

    def __init__(self):
        if BGPConfigurator.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            BGPConfigurator.__instance = self

    @staticmethod
    def write_route_map(bgp_conf):
        bgp_conf.write(
            "\n\n" +
            "ip prefix-list DC_LOCAL_SUBNET 5 permit 10.0.0.0/16 le 26\n"
            + "ip prefix-list DC_LOCAL_SUBNET 10 permit 200.0.0.0/16 le 32\n"
            + "route-map ACCEPT_DC_LOCAL permit 10\n"
            + " match ip-address DC_LOCAL_SUBNET\n\n\n"
        )

    @staticmethod
    def write_bgp_leaf_configuration(node: Node, bgpd_configuration):

        bgpd_configuration.write(
            'router bgp ' + str(ASManager.get_instance().get_as_number(node)) + '\n'
            + ' timers bgp 3 9\n'
            + ' bgp router-id ' + str(node.interfaces[0].ip_address) + '\n'
            + ' bgp bestpath as-path multipath-relax\n'
            + ' bgp bestpath compare-routerid\n'
            + ' neighbor TOR peer-group\n'
            + ' neighbor TOR remote-as external\n'
            + ' neighbor TOR advertisement-interval 0\n'
            + ' neighbor TOR timers connect 5\n')
        for interface in node.interfaces:
            if 'spine' in interface.neighbour_name:
                bgpd_configuration.write(' neighbor eth%d interface peer-group TOR\n' % interface.number)

        bgpd_configuration.write(
            " bgp bestpath as-path multipath-relax\n"
            + " address-family ipv4 unicast\n"
            + "  neighbor TOR activate\n"
            + "  redistribute connected route-map ACCEPT_DC_LOCAL\n"
            + "  maximum-paths 64\n"
            + " exit-address-family\n"
        )

    @staticmethod
    def write_bgp_spine_configuration(node: Node, bgpd_configuration):
        bgpd_configuration.write(
            'router bgp ' + str(ASManager.get_instance().get_as_number(node)) + '\n'
            + ' timers bgp 3 9\n'
            + ' bgp router-id ' + str(node.interfaces[0].ip_address) + '\n'
            + ' bgp bestpath as-path multipath-relax\n'
            + ' bgp bestpath compare-routerid\n'
            + ' neighbor TOR peer-group\n'
            + ' neighbor TOR remote-as external\n'
            + ' neighbor TOR advertisement-interval 0\n'
            + ' neighbor TOR timers connect 5\n')
        for interface in node.interfaces:
            if 'leaf' in interface.neighbour_name:
                bgpd_configuration.write(' neighbor eth%d interface peer-group TOR\n' % interface.number)
        bgpd_configuration.write(
            ' neighbor fabric peer-group\n'
            + ' neighbor fabric remote-as external\n'
            + ' neighbor fabric advertisement-interval 0\n'
            + ' neighbor fabric timers connect 5\n')
        for interface in node.interfaces:
            if 'spine' in interface.neighbour_name or 'tof' in interface.neighbour_name:
                bgpd_configuration.write(' neighbor eth%d interface peer-group fabric\n' % interface.number)

        bgpd_configuration.write(
            " address-family ipv4 unicast\n"
            + "  neighbor fabric activate\n"
            + "  neighbor TOR activate\n"
            + "  redistribute connected route-map ACCEPT_DC_LOCAL\n"
            + "  maximum-paths 64\n"
            + " exit-address-family\n"
        )

    @staticmethod
    def write_bgp_tof_configuration(node: Node, bgpd_configuration):
        bgpd_configuration.write(
            'router bgp ' + str(ASManager.get_instance().get_as_number(node)) + '\n'
            + ' timers bgp 3 9\n'
            + ' bgp router-id ' + str(node.interfaces[0].ip_address) + '\n'
            + ' bgp bestpath as-path multipath-relax\n'
            + ' bgp bestpath compare-routerid\n'
            + ' neighbor fabric peer-group\n'
            + ' neighbor fabric remote-as external\n'
            + ' neighbor fabric advertisement-interval 0\n'
            + ' neighbor fabric timers connect 5\n')
        for interface in node.interfaces:
            if 'spine' in interface.neighbour_name or 'tof' in interface.neighbour_name:
                bgpd_configuration.write(' neighbor eth%d interface peer-group fabric\n' % interface.number)
        bgpd_configuration.write(
            " address-family ipv4 unicast\n"
            + "  neighbor fabric activate\n"
            + "  redistribute connected route-map ACCEPT_DC_LOCAL\n"
            + "  maximum-paths 64\n"
            + " exit-address-family\n"
        )

    def write_bgp_configuration(self, node: Node):
        if node.role != 'server':
            with open('lab/lab.conf', 'a') as lab_config:
                lab_config.write('%s[image]="kathara/frr"\n' % node.name)

            os.mkdir('lab/%s/etc/frr' % node.name)
            with open('lab/%s/etc/frr/daemons' % node.name, 'w') as daemons:
                daemons.write('zebra=yes\n')
                daemons.write('bgpd=yes\n')

            with open('lab/%s/etc/frr/bgpd.conf' % node.name, 'w') as bgpd_configuration:
                bgpd_configuration.write(
                    "hostname frr\n"
                    + "password frr\n"
                    + "enable password frr\n\n"
                )
                self.write_route_map(bgpd_configuration)
                if node.role == 'leaf':
                    self.write_bgp_leaf_configuration(node, bgpd_configuration)
                elif node.role == 'spine':
                    self.write_bgp_spine_configuration(node, bgpd_configuration)
                elif node.role == 'tof':
                    self.write_bgp_tof_configuration(node, bgpd_configuration)

            with open('lab/%s/etc/frr/zebra.conf' % node.name, 'w') as zebra_configuration:
                zebra_configuration.write(
                    "hostname frr\n"
                    + "password frr\n"
                    + "enable password frr\n"
                )

            with open('lab/%s.startup' % node.name, 'a') as startup:
                startup.write('/etc/init.d/frr start\n')
                startup.write('sysctl -w net.ipv4.fib_multipath_hash_policy=1\n')






