import os

from model.node_types.Leaf import Leaf
from model.node_types.Tof import Tof
from ..IConfigurator import IConfigurator

# --------------------------- Start of Juniper Rift configuration templates --------------------------------------------


JUNIPER_RIFT_CONFIG_TEMPLATE = \
    """
set groups rift-defaults protocols rift traceoptions file size 1000000
set groups rift-defaults protocols rift traceoptions file files 4
set groups rift-defaults protocols rift traceoptions level info
set groups rift-defaults protocols rift node-id %s
set groups rift-defaults protocols rift level %s
set groups rift-defaults protocols rift lie-receive-address family inet 224.0.0.120
set groups rift-defaults protocols rift lie-receive-address family inet6 ff02::a1f7
set groups rift-defaults protocols rift interface <*> lie-transmit-address family inet 224.0.0.120
set groups rift-defaults protocols rift interface <*> lie-transmit-address family inet6 ff02::a1f7
set system host-name %s
set system scripts language python3
set system root-authentication encrypted-password "$6$QMRUo$LNAfxi1P1RljyWHeUl6qFSDMzFAn8Kqzt.vo/LfcoAfwstTvc8qT0WUrnMMGhdW4Dn6p8V15nkP6/ySoHBIAP."
set protocols rift apply-groups rift-defaults
set protocols rift name %s
set protocols rift startup-holddown 30
%s
%s
%s
    """

JUNIPER_RIFT_CONFIG_INTERFACE_TEMPLATE = \
    """
set protocols rift interface {iface}
set protocols rift interface {iface} lie-transmit-interval 30
set protocols rift interface {iface} hold-time 600
    """

JUNIPER_RIFT_EXPORT_TEMPLATE = \
    """
set protocols rift export northbound directly
    """

JUNIPER_RIFT_POLICY_TEMPLATE = \
    """
set policy-options policy-statement directly term t1 from protocol direct route-filter %s/24 exact
set policy-options policy-statement directly term t1 then accept
set policy-options policy-statement directly term t2 then reject
    """


# --------------------------- End of Juniper Rift configuration templates ----------------------------------------------


class JuniperRiftConfigurator(IConfigurator):
    def _configure_node(self, lab, node):
        with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
            lab_config.write('%s[image]="kathara/crpd-rift:latest"\n' % node.name)

        interfaces_strings = []
        for interface in node.get_phy_interfaces():
            interfaces_strings.append(JUNIPER_RIFT_CONFIG_INTERFACE_TEMPLATE.format(iface=interface.get_name()))

        interfaces_string = "".join(interfaces_strings)

        if type(node) == Tof:
            node_id = "%d%d%d" % (node.plane, node.level, node.number)
        else:
            node_id = "%d%d%d" % (node.pod_number, node.level, node.number)

        node_level = "top-of-fabric" if type(node) == Tof else "leaf" if type(node) == Leaf else "auto"

        export_content = JUNIPER_RIFT_EXPORT_TEMPLATE if type(node) == Leaf else ""

        policy_content = ""
        if type(node) == Leaf:
            server_interface = list(filter(lambda eth: '/24' in str(eth.network), node.interfaces))
            policy_content = JUNIPER_RIFT_POLICY_TEMPLATE % str(server_interface[0].network.network_address)

        config_path = "%s/%s/etc" % (lab.lab_dir_name, node.name)
        with open("%s/juniper_rift.conf" % config_path, "w") as config_file:
            config_content = JUNIPER_RIFT_CONFIG_TEMPLATE % (node_id, node_level, node.name,
                                                             node.name, export_content, interfaces_string,
                                                             policy_content)

            config_file.write(config_content)

        for service in ['auditd', 'eventd', 'license-check', 'na-grpcd', 'ppmd', 'xmlproxyd', 'bfdd', 'jsd', 'mgd-api',
                        'na-mqttd', 'rsyslog']:
            service_path = '%s/%s/etc/service/%s/supervise' % (lab.lab_dir_name, node.name, service)
            os.makedirs(service_path)
            with open('%s/control' % service_path, 'w') as control_file:
                control_file.write('d')

        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
            startup.write(
                "\nfor d in rpd mgd rift-proxyd; do until pidof $d; do sleep 1; done; done\n" +
                "until cli -c \"show version\" | grep -i junos; do sleep 1; done\n" +
                "until [ -f /config/juniper.conf.gz ]; do sleep 1; done\n" +
                "cli -c \"configure; load set /etc/juniper_rift.conf; commit\" &> /tmp/config.errors"
            )
