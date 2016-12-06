from sqlalchemy import func

from data_vu.utilities import *
from data_vu.db.__init__ import session
from data_vu.db.material import Material
from data_vu.db.mutation_strength import MutationStrength
from data_vu.files import load_config_file

def count_generations(run_id):
    """Queries database for last generation in run.

    Args:
        run_id (str): run identification string.

    Returns:
        generations (int): number of generations in run.

    """
    generations = session \
        .query(func.max(Material.generation)) \
        .filter(Material.run_id == run_id) \
        .all()[0][0]
    return generations

def query_points(x, y, z_bin, run_id, gen):
    """Queries database for two structure-properties.

    Args:
        x (str): `ml`, `sa`, `vf`.
        y (str): `ml`, `sa`, `vf`.
        z_bin (int): None, [0, number_of_bins].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x(float), y(float)]

    If z_bin == None: all z_bins are queried, instead of one slice.

    """
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    if z_bin == None:
        values = session \
            .query(x_attr, y_attr) \
            .filter(
                Material.run_id == run_id,
                Material.generation == gen
            ) \
            .all()
    if z_bin != None:
        z_attr = get_z_attr(x, y)
        values = session \
            .query(x_attr, y_attr) \
            .filter(
                Material.run_id == run_id,
                Material.generation == gen,
                z_attr == z_bin
            ) \
            .all()
    return values

def query_bin_counts(x, y, z_bin, run_id, gen):
    """Queries database for bin_counts.

    Args:
        x (str): `ml`, `sa`, `vf`.
        y (str): `ml`, `sa`, `vf`.
        z_bin (int): None, [0, number_of_bins].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x_bin, y_bin, bin_count]

    If z_bin == None: all z_bins are queried, instead of one slice.

    """
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    z_attr = get_z_attr(x, y)
    if z_bin == None:
        values = session \
            .query(
                x_attr,
                y_attr,
                func.count(Material.uuid)
            ) \
            .filter(
                Material.run_id == run_id,
                Material.generation <= gen
            ) \
            .group_by(
                x_attr,
                y_attr
            ) \
            .all()
    if z_bin != None:
        values = session \
            .query(
                x_attr,
                y_attr,
                func.count(Material.uuid)
            ) \
            .filter(
                Material.run_id == run_id,
                Material.generation <= gen,
                z_attr == z_bin
            ) \
            .group_by(
                x_attr,
                y_attr
            ) \
            .all()
    return values

def get_max_count(run_id):
    """Query database for highest bin-count.

    Args:
        run_id (str): run identification string.

    Returns:
        max_counts (int): highest bin-count.

    """
    counts = session \
        .query(func.count(Material.uuid)) \
        .filter(Material.run_id == run_id) \
        .group_by(
                Material.methane_loading_bin,
                Material.surface_area_bin,
                Material.void_fraction_bin
        ).all()
    max_counts = max(counts)[0]

    return max_counts

def get_bin_coordinate(x_attr, y_attr, x, y, z):
    if x_attr == getattr(MutationStrength, 'methane_loading_bin'):
        if y_attr == getattr(MutationStrength, 'surface_area_bin'):
            coords = [x, y, z]
        elif y_attr == getattr(MutationStrength, 'void_fraction_bin'):
            coords = [x, z, y]
    elif x_attr == getattr(MutationStrength, 'surface_area_bin'):
        if y_attr == getattr(MutationStrength, 'methane_loading_bin'):
            coords = [y, x, z]
        elif y_attr == getattr(MutationStrength, 'void_fraction_bin'):
            coords = [z, x, y]
    elif x_attr == getattr(MutationStrength, 'void_fraction_bin'):
        if y_attr == getattr(MutationStrength, 'methane_loading_bin'):
            coords = [y, z, x]
        elif y_attr == getattr(MutationStrength, 'surface_area_bin'):
            coords = [z, y, x]
    return coords

def query_mutation_strength(x, y, z_bin, run_id, gen):
    """Queries database for mutation strengths.

    Args:
        x (str): `ml`, `sa`, `vf`.
        y (str): `ml`, `sa`, `vf`.
        z_bin (int): None, [0, number_of_bins].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x_bin, y_bin, mutation_strength]

    If z_bin == None: all z_bins are queried, instead of one slice.

    """
    number_of_bins = load_config_file(run_id)['number_of_convergence_bins']
    x_attr = get_attr(x)
    y_attr = get_attr(y)

    values = []

    if z_bin == None:
        for x in range(number_of_bins):
            for y in range(number_of_bins):
                all_strengths = []
                for z in range(number_of_bins):
                    coords = get_bin_coordinate(x_attr, y_attr, x, y, z)
                    key = [run_id, gen] + coords
                    try:
                        strength = MutationStrength.get_prior(*key)
                        if type(strength) == int or type(strength) == float:
                            all_strengths.append(strength)
                    except KeyError as e:
                        if e.args[0] != 'initial_mutation_strength':
                            raise
                        else:
                            pass
                average_strength = sum(all_strengths) / float(len(all_strengths))
                value = [x, y, average_strength]
                values.append(value)

    if z_bin != None:
        for x in range(number_of_bins):
            for y in range(number_of_bins):
                coords = get_bin_coordinate(x_attr, y_attr, x, y, z_bin)
                key = [run_id, gen] + coords
                try:
                    strength = MutationStrength.get_prior(*key)
                    if type(strength) == int or type(strength) == float:
                        value = [x, y, strength]
                        values.append(value)
                except KeyError as e:
                    if e.args[0] != 'initial_mutation_strength':
                        raise
                    else:
                        pass
            
    return values

def query_material(x, y, id):
    """Query values `x` and `y` for one material.

    Args:
        x (str): `ml`, `sa`, `vf` or `ml_bin`, `sa_bin`, `vf_bin`
        y (str): `ml`, `sa`, `vf` or `ml_bin`, `sa_bin`, `vf_bin`
        id (int): Material.id

    Returns:
        value (list): [x(float, int), y(float, int)]

    """
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    value = session \
        .query(x_attr, y_attr) \
        .filter(Material.id == id) \
        .all()
    return value

def query_parents(x, y, z_bin, run_id, gen):
    """Find parent-materials and return data.
    
    Args:
        x (str): `ml`, `sa`, `vf` or `ml_bin`, `sa_bin`, `vf_bin`.
        y (str): `ml`, `sa`, `vf` or `ml_bin`, `sa_bin`, `vf_bin`.
        z_bin (int): None, [0, number_of_generations].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x(float, int), y(float, int)]

    """
    if z_bin == None:
        parents = session \
            .query(Material.parent_id) \
            .filter(
                Material.run_id == run_id,
                Material.generation == gen
            ) \
            .all()
    if z_bin != None:
        z_attr = get_z_attr(x, y)
        parents = session \
            .query(Material.parent_id) \
            .filter(
                Material.run_id == run_id,
                Material.generation == gen,
                z_attr == z_bin
            ) \
            .all()
    values = []
    for parent in parents:
        value = query_material(x, y, parent)
        values.append(value)
    return values

def query_child_bins(x, y, z_bin, run_id, gen):
    """Query bin-coordinates for across generation.
    
    Args:
        x (str): `ml`, `sa`, `vf` or `ml_bin`, `sa_bin`, `vf_bin`.
        y (str): `ml`, `sa`, `vf` or `ml_bin`, `sa_bin`, `vf_bin`.
        z_bin (int): None, [0, number_of_generations].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x(float, int), y(float, int)]

    """
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    if z_bin == None:
        values = session \
            .query(
                x_attr,
                y_attr
            ) \
            .filter(
                Material.run_id == run_id,
                Material.generation == gen
            ) \
            .group_by(
                x_attr,
                y_attr
            ) \
            .all()
    if z_bin != None:
        z_attr = get_z_attr(x, y)
        values = session \
            .query(
                x_attr,
                y_attr
            ) \
            .filter(
                Material.run_id == run_id,
                Material.generation == gen,
                z_attr == z_bin
            ) \
            .group_by(
                x_attr,
                y_attr
            ) \
            .all()
    return values

def evaluate_convergence(run_id, gen):
    """Use variance to evaluate convergence.

    Args:
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        variance (float): variance.

    """
    bin_counts = session \
        .query(
            func.count(Material.uuid)
        ) \
        .filter(
            Material.run_id == run_id,
            Material.generation <= gen
        ) \
        .group_by(
            Material.methane_loading_bin,
            Material.surface_area_bin,
            Material.void_fraction_bin
        ) \
        .all()
    bin_counts = [i[0] for i in bin_counts]

    mean_count = sum(bin_counts) / len(bin_counts)
    squared_differences = [(i - mean_count) ** 2 for i in bin_counts]
    variance = sum(squared_differences) / len(squared_differences)

    print('\nvariance :\t%s\n' % variance)

    return variance
