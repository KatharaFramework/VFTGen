import utils
from model.FatTree import FatTree


if __name__ == '__main__':
    config = utils.read_config('config.json')

    fat_tree = FatTree()
    fat_tree.create(config)

    utils.write_json_file("lab_new.json", fat_tree.to_dict())
