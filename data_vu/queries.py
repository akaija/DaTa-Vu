from sqlalchemy import func

from data_vu.utilities import *
from data_vu.db.__init__ import session
from data_vu.db.material import Material
from data_vu.db.mutation_strength import MutationStrength
from data_vu.files import load_config_file
from htsohm.htsohm import select_parent

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
            .query(x_attr, y_attr, func.count(Material.uuid)) \
            .filter(Material.run_id == run_id, Material.generation <= gen) \
            .group_by(x_attr, y_attr) \
            .order_by(func.count(Material.uuid).desc()) \
            .all()
    if z_bin != None:
        values = session \
            .query(x_attr, y_attr, func.count(Material.uuid)) \
            .filter(
                Material.run_id == run_id,
                Material.generation <= gen,\
                z_attr == z_bin
            ) \
            .group_by(x_attr, y_attr) \
            .order_by(func.count(Material.uuid).asc()) \
            .all()
    return values

def get_max_count(run_id, gen):
    """Query database for highest bin-count.

    Args:
        run_id (str): run identification string.

    Returns:
        max_counts (int): highest bin-count.

    """
    counts = session \
        .query(func.count(Material.uuid)) \
        .filter(
            Material.run_id == run_id,
            Material.generation == gen
        ) \
        .group_by(
                Material.methane_loading_bin,
                Material.surface_area_bin,
                Material.void_fraction_bin
        ).all()
    max_counts = max(counts)[0]

    return max_counts

def find_most_children(x, y, z_bin, run_id, gen):
    x_attr = get_attr(x)
    y_attr = get_attr(y)    
    parent_filter = [
        getattr(Material, 'run_id') == run_id,
        getattr(Material, 'generation') == gen
    ]
    print('PARENT_FILTER\t%s' % parent_filter)
    if z_bin != None:
        z_attr = get_z_attr(x, y)
        parent_filter.append(Material.z_attr == z_bin)
    parent_list = session \
        .query(Material.parent_id) \
        .filter(*parent_filter) \
        .group_by(Material.parent_id) \
        .order_by(func.count(Material.parent_id).desc()) \
        .all()
    if len(parent_list) >= 5:
        parent_list = parent_list[:5]

    print('PARENT_LIST\t%s' % parent_list)
    # query children
    values = []
    for parent_id in parent_list:
        parent_data = query_material(x, y, parent_id)
        print('PARENT_DATA\t%s' % parent_data)
        children_data = session \
            .query(x_attr, y_attr) \
            .filter(
                getattr(Material, 'parent_id') == parent_id,
                *parent_filter
            ) \
            .all()
        print('CHILDREN_DATA\t%s' % children_data)
        row = [parent_data, children_data]
        values.append(row)
    return values

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

def last_mutation_strength(run_id, gen, x, y, z):
    ms = session.query(MutationStrength) \
        .filter(
            MutationStrength.run_id == run_id,
            MutationStrength.methane_loading_bin == x,
            MutationStrength.surface_area_bin == y,
            MutationStrength.void_fraction_bin == z,
            MutationStrength.generation <= gen
        ) \
        .order_by(MutationStrength.generation.desc()) \
        .first()
    if ms:
        return ms

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

    x_mat = get_attr(x[:2] + '_bin')
    y_mat = get_attr(y[:2] + '_bin')
    z_mat = get_z_attr(x[:2], y[:2])

    values = []

    if z_bin == None:
        all_bins = session \
            .query(
                x_mat,
                y_mat
            ) \
            .filter(
                Material.run_id == run_id,
                Material.generation <= gen
            ) \
            .all()
        for [x, y] in all_bins:
            all_strengths = []
            for z in range(number_of_bins):
                coords = get_bin_coordinate(x_attr, y_attr, x, y, z)
                key = [run_id, gen] + coords
                ms = last_mutation_strength(*key)
                if ms:
                    all_strengths.append(ms.strength)
#                    
#        if ms:
#            return ms
# 
#
#                    try:
#                        strength = MutationStrength.get_prior(*key)
#                        if type(strength) == int or type(strength) == float:
#                            all_strengths.append(strength)
#                    except KeyError as e:
#                        if e.args[0] != 'initial_mutation_strength':
#                            raise
#                        else:
#                            pass
            average_strength = sum(all_strengths) / float(len(all_strengths))
            value = [x, y, average_strength]
            values.append(value)

    if z_bin != None:
        all_bins = session \
            .query(
                x_mat,
                y_mat,
                z_mat
            ) \
            .filter(
                Material.run_id == run_id,
                Material.generation <= gen
            ) \
            .all()
        for [x, y, z] in all_bins: 
            coords = get_bin_coordinate(x_attr, y_attr, x, y, z)
            key = [run_id, gen] + coords
            ms = last_mutation_strength(*key)
            if ms:
                value = [x, y, ms.strength]
                values.append(value)
#                try:
#                    strength = MutationStrength.get_prior(*key)
#                    if type(strength) == int or type(strength) == float:
#                        value = [x, y, strength]
#                        values.append(value)
#                except KeyError as e:
#                    if e.args[0] != 'initial_mutation_strength':
#                        raise
#                    else:
#                        pass
            
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
    parents = session \
        .query(Material.parent_id) \
        .filter(
            Material.run_id == run_id,
            Material.generation == gen
        ) \
        .all()
    if z_bin != None:
        parents = [id[0] for id in parents if z_bin == query_z_bin(x, y, id[0])[0]]
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
    sum_of_squares = sum(i ** 2 for i in bin_counts) / len(bin_counts)
    square_mean = (sum(bin_counts) / len(bin_counts)) ** 2
    variance = sum_of_squares - square_mean

    print('\nvariance :\t%s\n' % variance)

    return variance

def parent_from_uuid(uuid):
    """From uuid, finds parent id/uuid.

    Args:
        uuid (str): material unique identified

    Returns:
        parent_uuid (str): parent-material's uuid

    Prints parent-material's uuid and id.

    """
    parent_id = session \
        .query(Material.parent_id) \
        .filter(Material.uuid == uuid) \
        .all()[0]
    parent_uuid = session \
        .query(Material.uuid) \
        .filter(Material.id == parent_id) \
        .all()[0]

    print('child uuid\t\t%s' % uuid)
    print('parent id\t\t%s' % parent_id)
    print('parent uuid\t\t%s' % parent_uuid)

    return parent_uuid

def select_parents(x, y, z_bin, run_id, gen):
    config = load_config_file(run_id)
    generation_limit = config['children_per_generation']

    parents = []
# CHANGE THIS!!!!
    for i in range(100):
        parents.append(
            select_parent(run_id, gen, 100)
        )

    return parents

def query_z_bin(x, y, id):
    z_attr = get_z_attr(x, y)
    z_bin = session \
        .query(z_attr) \
        .filter(Material.id == id) \
        .all()[0]
    return z_bin

#def query_failed(x, y, z_bin, run_id, gen):
#    """Queries database for two structure-properties.
#
#    Args:
#        x (str): `ml`, `sa`, `vf`.
#        y (str): `ml`, `sa`, `vf`.
#        z_bin (int): None, [0, number_of_bins].
#        run_id (str): run identification string.
#        gen (int): generation.
#
#    Returns:
#        values (list): [x(float), y(float)]
#
#    If z_bin == None: all z_bins are queried, instead of one slice.
#
#    """
#    x_attr = get_attr(x)
#    y_attr = get_attr(y)
#    if z_bin == None:
#        values = session \
#            .query(x_attr, y_attr) \
#            .filter(
#                Material.run_id == run_id,
#                Material.generation == gen
#            ) \
#            .all()
#    if z_bin != None:
#        z_attr = get_z_attr(x, y)
#        values = session \
#            .query(x_attr, y_attr) \
#            .filter(
#                Material.run_id == run_id,
#                Material.generation == gen,
#                z_attr == z_bin
#            ) \
#            .all()
#    return values

def query_parents_and_counts(run_id, gen):
#    """Queries database for bin_counts.
#
#    Args:
#        x (str): `ml`, `sa`, `vf`.
#        y (str): `ml`, `sa`, `vf`.
#        z_bin (int): None, [0, number_of_bins].
#        run_id (str): run identification string.
#        gen (int): generation.
#
#    Returns:
#        values (list): [x_bin, y_bin, z_bin, bin_count, ]
#
#    If z_bin == None: all z_bins are queried, instead of one slice.
#
#    """
    bins_and_counts = session \
        .query(
            Material.methane_loading_bin,
            Material.surface_area_bin,
            Material.void_fraction_bin,
            func.count(Material.id)
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

    selected_parents = session \
        .query(
            Material.methane_loading_bin,
            Material.surface_area_bin,
            Material.void_fraction_bin,    
            func.count(Material.parent_id)
        ) \
        .filter(
            Material.run_id == run_id,
            Material.generation == gen + 1
        ) \
        .group_by(
            Material.methane_loading_bin,
            Material.surface_area_bin,
            Material.void_fraction_bin
        ) \
        .all()
    with open('OUTPUT.txt', 'wa') as file:
        print('\n\nRUN_ID\t%s' % run_id)
        print('\nGeneration\t%s\n' % gen)
        for i in bins_and_counts:
            overall_bin = [ i[0], i[1], i[2] ]
            bin_count = i[3]
            file.write('\nbin\t%s' % overall_bin)
            file.write('\tcount\t%s' % bin_count)
            for j in selected_parents:
                parent_bin == [ j[0], j[1], j[2] ]
                if parent_bin == overall_bin:
                    file.write('\tparents\t%s' % j[3])
                    
#
#
#
#
#    x_attr = get_attr(x)
#    y_attr = get_attr(y)
#    z_attr = get_z_attr(x, y)
#    if z_bin == None:
#        bins_and_counts = session \
#            .query(x_attr, y_attr, func.count(Material.uuid)) \
#            .filter(Material.run_id == run_id, Material.generation <= gen) \
#            .group_by(x_attr, y_attr) \
#            .order_by(func.count(Material.uuid).desc()) \
#            .all()
#    if z_bin != None:
#        values = session \
#            .query(x_attr, y_attr, func.count(Material.uuid)) \
#            .filter(
#                Material.run_id == run_id,
#                Material.generation <= gen,\
#                z_attr == z_bin
#            ) \
#            .group_by(x_attr, y_attr) \
#            .order_by(func.count(Material.uuid).asc()) \
#            .all()
#    return values

def get_max(run_id, x):
    """Queries database for last generation in run.

    Args:
        run_id (str): run identification string.

    Returns:
        generations (int): number of generations in run.

    """
    attr = get_attr(x)
    value = session \
        .query(func.max(attr)) \
        .filter(Material.run_id == run_id) \
        .all()[0][0]
    print('%s\t%s' % (attr, value))
    return value
