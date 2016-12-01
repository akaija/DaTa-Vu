from sqlalchemy import func

from data_vu.utilities import *
from data_vu.db.__init__ import session
from data_vu.db.material import Material
from data_vu.db.mutation_strength import MutationStrength

def count_generations(run_id):
    generations = session \
        .query(func.max(Material.generation)) \
        .filter(Material.run_id == run_id) \
        .all()[0][0]
    return generations

def query_points(x, y, z_bin, run_id, gen):
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    if x in ['ml', 'sa'] and y in ['ml', 'sa']:
        z_attr = getattr(Material, 'void_fraction_bin')
    if x in ['sa', 'vf'] and y in ['sa', 'vf']:
        z_attr = getattr(Material, 'methane_loading_bin')
    if x in ['ml', 'vf'] and y in ['ml', 'vf']:
        z_attr = getattr(Material, 'surface_area_bin')
    values = session \
        .query(x_attr, y_attr) \
        .filter(
            Material.run_id == run_id,
            Material.generation == gen,
            z_attr == z_bin
        ) \
        .all()
    return values

def query_points_all(x, y, run_id, gen):
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    values = session \
        .query(x_attr, y_attr) \
        .filter(
            Material.run_id == run_id,
            Material.generation == gen
        ) \
        .all()
    return values

def query_bin_counts(x, y, z_bin, run_id, gen):
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    if x in ['ml_bin', 'sa_bin'] and y in ['ml_bin', 'sa_bin']:
        z_attr = getattr(Material, 'void_fraction_bin')
    elif x in ['sa_bin', 'vf_bin'] and y in ['sa_bin', 'vf_bin']:
        z_attr = getattr(Material, 'methane_loading_bin')
    elif x in ['ml_bin', 'vf_bin'] and y in ['ml_bin', 'vf_bin']:
        z_attr = getattr(Material, 'surface_area_bin')
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
            y_attr,
            z_attr
        ) \
        .all()
    return values

def query_bin_counts_all(x, y, run_id, gen):
    x_attr = get_attr(x)
    y_attr = get_attr(y)
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
    return values

def get_max_count(run_id):
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

def query_mutation_strength(x, y, z_bin, run_id, gen):
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    if x in ['ml_bin_MS', 'sa_bin_MS'] and y in ['ml_bin_MS', 'sa_bin_MS']:
        z_attr = getattr(MutationStrength, 'void_fraction_bin')
    if x in ['sa_bin_MS', 'vf_bin_MS'] and y in ['sa_bin_MS', 'vf_bin_MS']:
        z_attr = getattr(MutationStrength, 'methane_loading_bin')
    if x in ['ml_bin_MS', 'vf_bin_MS'] and y in ['ml_bin_MS', 'vf_bin_MS']:
        z_attr = getattr(MutationStrength, 'surface_area_bin')
    values = session \
        .query(x_attr, y_attr, MutationStrength.strength) \
        .filter(
            MutationStrength.run_id == run_id,
            MutationStrength.generation == gen,
            z_attr == z_bin
        ) \
        .all()
    return values

def query_mutation_strength_all(x, y, run_id, gen):
    x_attr = get_attr(x)
    y_attr = get_attr(y)
    values = session \
        .query(x_attr, y_attr, MutationStrength.strength) \
        .filter(
            MutationStrength.run_id == run_id,
            MutationStrength.generation == gen
        ) \
        .all()
    return values

def evaluate_convergence(run_id, gen):
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
