import os

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches

from data_vu.utilities import *
from data_vu.queries import *
from data_vu.files import load_config_file

def plot_points(x, y, z_bin, run_id, gen, config, ax):
    """Scatterplot...

    Args:
        x (str): `ML`, `SA`, `VF`
        y (str): `ML`, `SA`, `VF`
        z_bin (int): [0, number_of_bins]
        run_id (str): identification string
        gen (int): [0, number_of_generations]
        config (yaml.load): use `data_vu.files.load_config_file`
        ax : plt.subplot(111)

    """

    plt.tick_params(
        axis='both', which='both', bottom='off', top='off', labelbottom='off',
        right='off', left='off', labelleft='off'
    )
#    if z_bin != 0 or gen != 0:
#        ax.tick_params(labelbottom=False, labelleft=False)
#    if z_bin == 0 and gen == 1:
#        plt.xlabel(x)
#        plt.ylabel(y)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    for i in range(gen):
        values = query_points(x, y, z_bin, run_id, i)
        for i in values:
            plt.scatter(i[0], i[1], marker='o', color='k', alpha=0.2, s=5)
    values = query_points(x, y, z_bin, run_id, gen)
    for i in values:
        plt.scatter(i[0], i[1], marker='o', color='r', alpha=0.7, s=5)

def plot_points_all(x, y, run_id, gen, config, ax):
    plt.tick_params(
        axis='both', which='both', bottom='off', top='off', labelbottom='off',
        right='off', left='off', labelleft='off'
    )
#    if z_bin != 0 or gen != 0:
#        ax.tick_params(labelbottom=False, labelleft=False)
#    if z_bin == 0 and gen == 1:
#        plt.xlabel(x)
#        plt.ylabel(y)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    for i in range(gen):
        values = query_points_all(x, y, run_id, i)
        for i in values:
            plt.scatter(i[0], i[1], marker='o', color='k', alpha=0.5, s=5)
    values = query_points_all(x, y, run_id, gen)
    for i in values:
        # CHANGE THIS!!!!
        plt.scatter(i[0], i[1], marker='o', color='k', alpha=0.5, s=5)

def add_square(x, y, x_value, y_value, strength, ax, config):
    x_width = get_width(x, config)
    y_width = get_width(y, config)
    x_pos = x_value * x_width
    y_pos = y_value * y_width
    ax.add_patch(
        patches.Rectangle(
            (x_pos, y_pos),
            x_width,
            y_width,
            facecolor = cm.Reds(strength),
            alpha = 1
        )
    )

def plot_bin_counts(x, y, z_bin, run_id, gen, config, ax):
    max_count = get_max_count(run_id)
    values = query_bin_counts(x, y, z_bin, run_id, gen)
    plt.tick_params(
        axis='both', which='both', bottom='off', top='off', labelbottom='off',
        right='off', left='off', labelleft='off'
    )
#    if z_bin != 0 or gen != 0:
#        ax.tick_params(labelbottom=False, labelleft=False)
#    if z_bin == 0 and gen == 1:
#        plt.xlabel(x)
#        plt.ylabel(y)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    for i in values:
        strength = float(i[2]) / float(max_count)
        add_square(x, y, i[0], i[1], strength, ax, config)

def plot_bin_counts_all(x, y, run_id, gen, config, ax):
    max_count = get_max_count(run_id)
    values = query_bin_counts_all(x, y, run_id, gen)
    plt.tick_params(
        axis='both', which='both', bottom='off', top='off', labelbottom='off',
        right='off', left='off', labelleft='off'
    )
#    if z_bin != 0 or gen != 0:
#        ax.tick_params(labelbottom=False, labelleft=False)
#    if z_bin == 0 and gen == 1:
#        plt.xlabel(x)
#        plt.ylabel(y)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    for i in values:
        strength = float(i[2]) / float(max_count)
        add_square(x, y, i[0], i[1], strength, ax, config)

def plot_mutation_strengths(x, y, z_bin, run_id, gen, config, ax):
    plt.tick_params(
        axis='both', which='both', bottom='off', top='off', labelbottom='off',
        right='off', left='off', labelleft='off'
    )
#    if z_bin != 0 or gen != 0:
#        ax.tick_params(labelbottom=False, labelleft=False)
#    if z_bin == 0 and gen == 1:
#        plt.xlabel(x)
#        plt.ylabel(y)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    values = query_mutation_strength(x, y, z_bin, run_id, gen)
    ax.tick_params(labelbottom=False, labelleft=False)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    for i in values:
        add_square(x, y, i[0], i[1], i[2], ax, config)

def plot_mutation_strengths_all(x, y, run_id, gen, config, ax):
    plt.tick_params(
        axis='both', which='both', bottom='off', top='off', labelbottom='off',
        right='off', left='off', labelleft='off'
    )
#    if z_bin != 0 or gen != 0:
#        ax.tick_params(labelbottom=False, labelleft=False)
#    if z_bin == 0 and gen == 1:
#        plt.xlabel(x)
#        plt.ylabel(y)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    values = query_mutation_strength_all(x, y, run_id, gen)
    ax.tick_params(labelbottom=False, labelleft=False)
    plt.xlim(get_limits(x, config))
    plt.ylim(get_limits(y, config))
    for i in values:
        add_square(x, y, i[0], i[1], i[2], ax, config)
