import utils
from models import laboratory


config = utils.read_config('config.json')
lab = laboratory.Lab(config)

json_file = open('lab.json', 'w')
json_file.write(lab.to_json())
json_file.close()