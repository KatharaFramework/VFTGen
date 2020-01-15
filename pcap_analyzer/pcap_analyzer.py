import pyshark
import docker


def _get_bridge_name(network):
    return "kt-%s" % network.id[:12]


if __name__ == '__main__':
    client = docker.from_env()
    network_list = client.networks.list()
    for network in network_list:
        bridge_name = _get_bridge_name(network)
        print(bridge_name)
        capture = pyshark.LiveCapture(output_file="capture.pcap")
        for packet in capture.sniff_continuously(packet_count=5):
            print('Just arrived:', packet)





