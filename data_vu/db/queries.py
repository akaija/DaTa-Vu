from statistics import variance

from sqlalchemy import *

from data_vu import config
from data_vu.utilities import *
from data_vu.db.__init__ import engine, materials, mutation_strengths
from htsohm.db.mutation_strength import *
from htsohm.htsohm import select_parent

def count_generations(run_id):
    """Queries database for last generation in run.

    Args:
        run_id (str): run identification string.

    Returns:
        generations (int): number of generations in run.

    """
    cols = [func.max(materials.c.generation)]
    rows = materials.c.run_id == run_id
    result = engine.execute(select(cols, rows))
    for row in result:
        max_gen = row[0]
    result.close()
    return max_gen

def query_points(x, y, z_bin, run_id, gen):
    """Queries database for two structure-properties.

    Args:
        x (str): `gl`, `sa`, `vf`.
        y (str): `gl`, `sa`, `vf`.
        z_bin (int): None, [0, number_of_bins].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x(float), y(float)]

    If z_bin == None: all z_bins are queried, instead of one slice.

    """
    cols = [get_attr(x), get_attr(y)]
    rows = and_(materials.c.run_id == run_id, materials.c.generation == gen)
    if z_bin != None:
        rows = and_(rows, get_z_attr(x, y) == z_bin)
    return select(cols, rows)

def query_bin_counts(x, y, z_bin, run_id, gen):
    """Queries database for bin_counts.

    Args:
        x (str): `gl`, `sa`, `vf`.
        y (str): `gl`, `sa`, `vf`.
        z_bin (int): None, [0, number_of_bins].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x_bin, y_bin, bin_count]

    If z_bin == None: all z_bins are queried, instead of one slice.

    """
    cols = [get_attr(x), get_attr(y), func.count(materials.c.uuid)]
    rows = and_(materials.c.run_id == run_id, materials.c.generation <= gen)
    sort = [get_attr(x), get_attr(y)]
    if z_bin != None:
        rows = and_(rows, get_z_attr(x, y) == z_bin)
    return select(cols, rows).group_by(*sort)

def get_max_count(x, y, z_bin, run_id, gen):
    """Query database for highest bin-count.

    Args:
        run_id (str): run identification string.

    Returns:
        max_counts (int): highest bin-count.

    """
    cols = [func.count(materials.c.uuid)]
    rows = and_(materials.c.run_id == run_id, materials.c.generation == gen)
    sort = [get_attr(x), get_attr(y)]
    if z_bin != 0:
        rows = and_(rows, get_z_attr(x, y) == z_bin)
    result = engine.execute(select(cols, rows).group_by(*sort))
    counts = [row[0] for row in result]
    result.close()
    if counts != []:
        return min(counts), max(counts), sum(counts) / len(counts)
    else:
        return 0, 0, 0

def find_most_children(x, y, z_bin, run_id, gen):
    cols = [materials.c.parent_id]
    rows = and_(material.c.run_id == run_id, materials.c.generation == gen)
    sort = func.count(materials.c.parent_id)
    s = select(cols, rows).group_by(*cols).order_by(desc(sort))
    result = engine.execute(s)
    parent_ids = []
    for row in result:
        parent_ids.append(row[material.c.parent_id])
    parents = parents[5:]
    values = []
    for parent in parent_ids:
        cols = [get_attr(x), get_attr(y)]
        s = select(cols, materials.c.id == parent)
        result = engine.execute(s)
        for row in result:
            parent = [row[0], row[1]]
        result.close()
        rows = and_(rows, materials.c.parent_id == parent)
        s = select(cols, rows)
        result = engine.execute(s)
        children = []
        for row in result:
            children.append(row[0], row[1])
        result.close()
        line = [parent, children]
        values.append(line)
    return values

def get_bin_coordinate(x_attr, y_attr, x, y, z):
    if x_attr == mutation_strengths.c.gas_loading_bin:
        if y_attr == mutation_strengths.c.surface_area_bin:
            coords = [x, y, z]
        elif y_attr == mutation_strengths.c.void_fraction_bin:
            coords = [x, z, y]
    elif x_attr == mutation_strengths.c.surface_area_bin:
        if y_attr == mutation_strengths.c.gas_loading_bin:
            coords = [y, x, z]
        elif y_attr == mutation_strengths.c.void_fraction_bin:
            coords = [z, x, y]
    elif x_attr == mutation_strengths.c.void_fraction_bin:
        if y_attr == mutation_strengths.c.gas_loading_bin:
            coords = [y, z, x]
        elif y_attr == mutation_strengths.c.surface_area_bin:
            coords = [z, y, x]
    return coords

def last_mutation_strength(run_id, gen, x, y, z):
    cols = [mutation_strengths.c.strength]
    rows = and_(
            mutation_strengths.c.run_id == run_id,
            mutation_strengths.c.generation <= gen,
            mutation_strengths.c.gas_loading_bin == x,
            mutation_strengths.c.surface_area_bin == y,
            mutation_strengths.c.void_fraction_bin == z,
    )
    sort = mutation_strengths.c.generation
    result = engine.execute(select(cols, rows).order_by(asc(sort)))
    for row in result:
        ms = row[0]
    result.close()
    if 'ms' in vars():
        return ms
    else:
        return load_config_file(run_id)['initial_mutation_strength']

def query_mutation_strength(x, y, z_bin, run_id, gen):
    """Queries database for mutation strengths.
    
    Args:
        x (str): `gl`, `sa`, `vf`.
        y (str): `gl`, `sa`, `vf`.
        z_bin (int): None, [0, number_of_bins].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x_bin, y_bin, mutation_strength]

    If z_bin == None: all z_bins are queried, instead of one slice.

    """
    number_of_bins = load_config_file(run_id)['number_of_convergence_bins']
    initial_strength = load_config_file(run_id)['initial_mutation_strength']
    x_ = get_attr(x)
    y_ = get_attr(y)
    z_ = [i + '_mutation_strength' for i in ['gl', 'sa', 'vf']]
    z_.remove(x)
    z_.remove(y)
    z_ = get_attr(z_[0])
    vals = []
    for x in range(number_of_bins):
        for y in range(number_of_bins):
            cols = [mutation_strengths.c.strength]
            rows = and_(mutation_strengths.c.generation <= gen,
                    mutation_strengths.c.run_id == run_id,
                    x_ == x, y_ == y)
            if z_bin != None:
                rows = and_(rows, z_ == z_bin)
            s = select(cols, rows) \
                    .order_by(desc(mutation_strengths.c.generation)).limit(1)
            result = engine.execute(s)
            for row in result:
                ms = row[mutation_strengths.c.strength]
            result.close()
            if 'ms' in vars():
                line = [x, y, ms]
            else:
                line = [x, y, initial_strength]
            vals.append(line)
    return vals

def query_material(x, y, id):
    """Query values `x` and `y` for one material.
   
    Args:
        x (str): `gl`, `sa`, `vf` or `gl_bin`, `sa_bin`, `vf_bin`
        y (str): `gl`, `sa`, `vf` or `gl_bin`, `sa_bin`, `vf_bin`
        id (int): Material.id
   
    Returns:
       value (list): [x(float, int), y(float, int)]
   
    """
    return select([get_attr(x), get_attr(y)], materials.c.id == id)

def query_parents(x, y, z_bin, run_id, gen):
    """Find parent-materials and return data.
       
    Args:
        x (str): `gl`, `sa`, `vf` or `gl_bin`, `sa_bin`, `vf_bin`.
        y (str): `gl`, `sa`, `vf` or `gl_bin`, `sa_bin`, `vf_bin`.
        z_bin (int): None, [0, number_of_generations].
        run_id (str): run identification string.
        gen (int): generation.
   
    Returns:
        values (list): [x(float, int), y(float, int)]
  
    """
    cols = [materials.c.parent_id]
    rows = and_(material.c.run_id == run_id, material.c.generation == gen)
    if z_bin != None:
        rows = and_(rows, get_z_attr(x, y) == z_bin)
    vals = []
    result1 = engine.execute(select(cols, rows))
    for row1 in result1:
        result2 = engine.execute(query_material(x, y, row[0]))
        for row2 in result2:
            val = [row2[0], row2[1]]
            vals.append(val)
        result2.close()
    result1.close()
    return vals

def query_child_bins(x, y, z_bin, run_id, gen):
    """Query bin-coordinates for across generation.
    
    Args:
        x (str): `gl`, `sa`, `vf` or `gl_bin`, `sa_bin`, `vf_bin`.
        y (str): `gl`, `sa`, `vf` or `gl_bin`, `sa_bin`, `vf_bin`.
        z_bin (int): None, [0, number_of_generations].
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        values (list): [x(float, int), y(float, int)]

    """
    cols = [get_attr(x), get_attr(y)]
    rows = and_(materials.c.run_id == run_id, materials.c.generation == gen)
    if z_bin != None:
        rows = and_(rows, get_z_attr(x, y) == z_bin)
    return select(cols, rows)

def evaluate_convergence(run_id, gen):
    """Use variance to evaluate convergence.

    Args:
        run_id (str): run identification string.
        gen (int): generation.

    Returns:
        variance (float): variance.

    """
    cols = [func.count(materials.c.uuid)]
    rows = and_(materials.c.run_id == run_id, materials.c.generation <= gen)
    sort = [materials.c.gas_loading_bin,
            materials.c.surface_area_bin,
            materials.c.void_fraction_bin]
    result = engine.execute(select(cols, rows).group_by(*sort))
    counts = [row[0] for row in result]
    result.close()
    return variance(counts)

def select_parents(x, y, z_bin, run_id, gen, number=100):
    config = load_config_file(run_id)
    generation_limit = config['children_per_generation']
    parents = []
    for i in range(number):
        parents.append(
            select_parent(run_id, gen, 100)
        )
    return parents

def query_z_bin(x, y, id):
    s = select([get_z_attr(x, y)], material.c.id == id)
    z_bin = [ row[0] for row in engine.execute(s) ]
    return z_bin

def get_max(run_id, x):
    """Queries database for highest value for inputted parameter.

    Args:
        run_id (str): run identification string.

    Returns:
        generations (int): highest value.

    """
    s = select([get_attr(x)], materials.c.run_id == run_id)
    result = engine.execute(s)
    for row in result:
        print(row)
    result.close()