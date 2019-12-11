import os
import shutil

import utils
from model.FatTree import FatTree
from model.Laboratory import Laboratory

if __name__ == '__main__':
    if os.path.isdir('lab'):
        shutil.rmtree('lab')
    os.mkdir('lab')

    config = utils.read_config('config.json')

    fat_tree = FatTree()
    fat_tree.create(config)

    lab = Laboratory("lab")
    lab.dump(fat_tree)

    protocol = config["protocol"] if "protocol" in config else None
    if protocol:
        protocol_class_name = "".join(map(lambda x: x.capitalize(), protocol.split("_")))

        protocol_configurator = utils.class_for_name("protocol.%s" % protocol,
                                                     "%sConfigurator" % protocol_class_name
                                                     )()

        protocol_configurator.configure(lab, fat_tree)

    utils.write_json_file("lab.json", fat_tree.to_dict())
