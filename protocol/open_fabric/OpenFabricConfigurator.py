import os

from ..IConfigurator import IConfigurator

OPENFABRIC_IFACE_CONFIGURATION = """interface eth%d
 ip router openfabric 1
"""

OPENFABRIC_ROUTER_CONFIGURATION = """
router openfabric 1
 net %s
"""


class OpenFabricConfigurator(IConfigurator):
    def _configure_node(self, lab, node):
        with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
            lab_config.write('%s[image]="kathara/frr"\n' % node.name)

        os.mkdir('%s/%s/etc/frr' % (lab.lab_dir_name, node.name))
        with open('%s/%s/etc/frr/daemons' % (lab.lab_dir_name, node.name), 'w') as daemons:
            daemons.write('zebra=yes\n')
            daemons.write('fabricd=yes\n')

        with open('%s/%s/etc/frr/fabricd.conf' % (lab.lab_dir_name, node.name), 'w') as fabricd_configuration:
            for interface in node.interfaces:
                fabricd_configuration.write(OPENFABRIC_IFACE_CONFIGURATION % interface.number)

            fabricd_configuration.write(OPENFABRIC_ROUTER_CONFIGURATION %
                                        self._get_net_iso_format(node.interfaces[0].ip_address)
                                        )

        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
            startup.write('/etc/init.d/frr start\n')
            startup.write('sysctl -w net.ipv4.fib_multipath_hash_policy=1\n')

    @staticmethod
    def _get_net_iso_format(ip_address):
        s = "".join(map(lambda x: '%03d' % int(x), str(ip_address).split('.')))
        return '49.0001.%s.%s.%s.00' % (s[0:4], s[4:8], s[8:12])
