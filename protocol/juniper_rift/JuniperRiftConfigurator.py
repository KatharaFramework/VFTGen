import gzip
import os

from model.node_types.Leaf import Leaf
from model.node_types.Tof import Tof
from ..IConfigurator import IConfigurator

# --------------------------- Start of Juniper Rift configuration templates --------------------------------------------

# the values for 
# startup-holddown
# lie-transmit-interval 
# hold-time
# are tuned for large topologies on a machine

JUNIPER_RIFT_CONFIG_TEMPLATE = \
    """
version "20201001.232355__devpublish.r3242 [_devpublish]";
groups {
    rift-defaults {
        protocols {
            rift {
                traceoptions {
                    file size 1000000 files 4;
                    level notice;
                }
                node-id %s;
                level %s;
                lie-receive-address {
                    family {
                        inet 224.0.0.120;
                    }
                }
                interface <*> {
                    lie-transmit-address {
                        family {
                            inet 224.0.0.120;
                        }
                    }
                }
            }
        }
    }
}
system {
    host-name %s;
    root-authentication {
        encrypted-password "$6$QMRUo$LNAfxi1P1RljyWHeUl6qFSDMzFAn8Kqzt.vo/LfcoAfwstTvc8qT0WUrnMMGhdW4Dn6p8V15nkP6/ySoHBIAP.";
    }
    scripts {
        language python3;
    }
}

protocols {
    rift {
        apply-groups rift-defaults;
        name %s;
        # startup-holddown 5;
%s
%s
    }
}

%s
"""

JUNIPER_RIFT_CONFIG_INTERFACE_TEMPLATE = \
    "        interface %s {\n" + \
    "            # hold-time 600;\n" + \
    "            # lie-transmit-interval 30;\n" + \
    "        }"

JUNIPER_RIFT_EXPORT_TEMPLATE = \
    "        export {\n" + \
    "            northbound {\n" + \
    "                directly;\n" + \
    "            }\n" + \
    "        }"

JUNIPER_RIFT_POLICY_TEMPLATE = \
    "policy-options {\n" + \
    "    policy-statement directly {\n" + \
    "        term t1 {\n" + \
    "            from {\n" + \
    "                protocol direct;\n" + \
    "                route-filter %s/24 exact;\n" + \
    "            }\n" + \
    "            then accept;\n" + \
    "        }\n" + \
    "        term t2 {\n" + \
    "            then reject;\n" + \
    "        }\n" + \
    "    }\n" + \
    "}"


# --------------------------- End of Juniper Rift configuration templates ----------------------------------------------


class JuniperRiftConfigurator(IConfigurator):
    def _configure_node(self, lab, node):
        with open('%s/lab.conf' % lab.lab_dir_name, 'a') as lab_config:
            lab_config.write('%s[image]="crpd-rift:latest"\n' % node.name)

        interfaces_strings = []
        for interface in node.get_phy_interfaces():
            interfaces_strings.append(JUNIPER_RIFT_CONFIG_INTERFACE_TEMPLATE % interface.get_name())

        interfaces_string = "\n".join(interfaces_strings)

        if type(node) == Tof:
            node_id = "00%02x%02x%02x650000" % (node.plane, node.level, node.number)
        else:
            node_id = "00%02x%02x%02x650000" % (node.pod_number, node.level, node.number)

        node_level = "top-of-fabric" if type(node) == Tof else "leaf" if type(node) == Leaf else "auto"

        export_content = JUNIPER_RIFT_EXPORT_TEMPLATE if type(node) == Leaf else ""

        policy_content = ""
        if type(node) == Leaf:
            server_interface = list(filter(lambda eth: '/24' in str(eth.network), node.interfaces))
            policy_content = JUNIPER_RIFT_POLICY_TEMPLATE % str(server_interface[0].network.network_address)

        config_path = "%s/%s/config" % (lab.lab_dir_name, node.name)
        os.mkdir(config_path)
        with gzip.open("%s/juniper_rift.conf.gz" % config_path, "wb") as config_file:
            config_content = JUNIPER_RIFT_CONFIG_TEMPLATE % (node_id, node_level, node.name,
                                                             node.name, export_content, interfaces_string,
                                                             policy_content)

            config_file.write(config_content.encode('utf-8'))

        with open('%s/%s.startup' % (lab.lab_dir_name, node.name), 'a') as startup:
            startup.write(
                "\nfor d in rpd mgd jsd mgd-api rift-proxyd; do until pidof $d; do sleep 1; done; done\n" +
                "until cli -c \"show version\" | grep -i junos; do sleep 1; done\n" +
                "cli -c \"configure; load replace /config/juniper_rift.conf.gz; commit\" &> /tmp/config.errors"
            )
