import utils
import os
import shutil
from model.FatTree import FatTree
from model.Laboratory import Laboratory


if __name__ == '__main__':
    if os.path.isdir('lab'):
        shutil.rmtree('lab')
    os.mkdir('lab')

    config = utils.read_config('config.json')

    fat_tree = FatTree()
    fat_tree.create(config)

    lab = Laboratory()
    lab.write_kathara_configurations(fat_tree)
    lab.write_kathara_bgp_configuration(fat_tree)

    utils.write_json_file("lab_new.json", fat_tree.to_dict())
