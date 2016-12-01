# standard imports
import os

# related third party imports
import yaml

# local application/library specific imports
import data_vu

def load_config_file(run_id):
    """Reads input file.
    Input files must be in .yaml format, see htsohm.sample.yaml
    """
    DV_path = os.path.dirname(data_vu.__file__)
    config_path = os.path.join(DV_path, 'config', run_id + '.yaml')
    with open(config_path) as file:
        config = yaml.load(file)
    return config
