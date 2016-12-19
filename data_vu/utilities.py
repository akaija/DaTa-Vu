import os

import yaml

import data_vu
from data_vu.db.__init__ import materials, mutation_strengths

def load_config_file(run_id):
    """Reads input file.
    Input files must be in .yaml format, see htsohm.sample.yaml
    """
    DV_path = os.path.dirname(data_vu.__file__)
    config_path = os.path.join(DV_path, 'config', run_id + '.yaml')
    with open(config_path) as file:
        config = yaml.load(file)
    return config

def get_limits(x, config):
    if 'gl' in x:
        limits = config['gas_loading_limits']
    elif 'sa' in x:
        limits = config['surface_area_limits']
    elif 'vf' in x:
        limits = config['void_fraction_limits']
    return limits

def get_attr(x):
    if x == 'gl':
        attr = getattr(materials.c, 'gl_absolute_volumetric_loading')
    elif x == 'sa':
        attr = getattr(materials.c, 'sa_volumetric_surface_area')
    elif x == 'vf':
        attr = getattr(materials.c, 'vf_helium_void_fraction')
    elif x == 'gl_mutation_strength':
        attr = getattr(mutation_strengths.c, 'gas_loading_bin')
    elif x == 'sa_mutation_strength':
        attr = getattr(mutation_strengths.c, 'surface_area_bin')
    elif x == 'vf_mutation_strength':
        attr = getattr(mutation_strengths.c, 'void_fraction_bin')
    elif x == 'gl_bin':
        attr = getattr(materials.c, 'gas_loading_bin')
    elif x == 'sa_bin':
        attr = getattr(materials.c, 'surface_area_bin')
    elif x == 'vf_bin':
        attr = getattr(materials.c, 'void_fraction_bin')
    else:
        print('--flag not understood--')

    return attr

def get_width(x, config):
    x_limits = get_limits(x, config)
    return (x_limits[1] - x_limits[0]) / config['number_of_convergence_bins']

def get_z_attr(x, y):
    if x[:2] in ['gl', 'sa'] and y[:2] in ['gl', 'sa']:
        z_attr = getattr(materials.c, 'void_fraction_bin')
    elif x[:2] in ['sa', 'vf'] and y[:2] in ['sa', 'vf']:
        z_attr = getattr(materials.c, 'gas_loading_bin')
    elif x[:2] in ['gl', 'vf'] and y[:2] in ['gl', 'vf']:
        z_attr = getattr(materials.c, 'surface_area_bin')
    else:
        print('--flag not understood')
    return z_attr

def make_list(x):
    if type(x) != type([]):
            x = [x]
    return x
