from data_vu.db.material import Material
from data_vu.db.mutation_strength import MutationStrength
from data_vu.files import load_config_file

def get_limits(x, config):
    if 'ml' in x:
        limits = config['methane_loading_limits']
    elif 'sa' in x:
        limits = config['surface_area_limits']
    elif 'vf' in x:
        limits = config['void_fraction_limits']
    return limits

def get_attr(x):
    if x == 'ml':
        attr = getattr(Material, 'ml_absolute_volumetric_loading')
    elif x == 'sa':
        attr = getattr(Material, 'sa_volumetric_surface_area')
    elif x == 'vf':
        attr = getattr(Material, 'vf_helium_void_fraction')
    elif x == 'ml_bin_MS':
        attr = getattr(MutationStrength, 'methane_loading_bin')
    elif x == 'sa_bin_MS':
        attr = getattr(MutationStrength, 'surface_area_bin')
    elif x == 'vf_bin_MS':
        attr = getattr(MutationStrength, 'void_fraction_bin')
    elif x == 'ml_bin':
        attr = getattr(Material, 'methane_loading_bin')
    elif x == 'sa_bin':
        attr = getattr(Material, 'surface_area_bin')
    elif x == 'vf_bin':
        attr = getattr(Material, 'void_fraction_bin')
    else:
        print('--flag not understood--')
    return attr

def get_width(x, config):
    x_limits = get_limits(x, config)
    return (x_limits[1] - x_limits[0]) / config['number_of_convergence_bins']
