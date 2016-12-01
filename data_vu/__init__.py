import os

import yaml

import data_vu
from data_vu.files import load_config_file

config = {}

def _init(run_id):
    data_vu_dir = os.path.dirname(os.path.dirname(data_vu.__file__))
    config_path = os.path.join(data_vu_dir, 'config', run_id + '.yaml')
    config.update(load_config_file(config_path))
    return config
