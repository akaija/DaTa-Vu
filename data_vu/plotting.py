import os

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import numpy as np

from data_vu.utilities import *
from data_vu.queries import *
from data_vu.files import load_config_file

def plot_points(
        x, y, z_bin,
        run_id, gen,
        config, ax, z_bins, generations,
        labels = None,
        highlight_children='on',
        highlight_parents='off'
    ):
    """Create scatterplot 'x' v. 'y' either by plotting a z-axis slice,
        or all slices at once.

    Args:
        x (str): `ML`, `SA`, `VF`
        y (str): `ML`, `SA`, `VF`
        z_bin (int): None(default), [0, number_of_bins]
        run_id (str): run identification string
        gen (int): [0, number_of_generations]
        config (yaml.load): use `data_vu.files.load_config_file`
        ax : plt.subplot(111)
        labels (str): None(default), `first_only`, `all`
        highlight_children (str): `on`(default), `off`
        highlight_parents (str): `on`, `off`(default)

    Returns:
        None

    """
    x_limits = get_limits(x, config)
    y_limits = get_limits(y, config)
    plt.xlim(x_limits)
    plt.ylim(y_limits)
    
    if labels == None:
        plt.tick_params(
            axis='both', which='both', bottom='off', top='off', labelbottom='off',
            right='off', left='off', labelleft='off'
        )
    elif labels == 'first_only':
        if z_bins.index(z_bin) != 0 or generations.index(gen) != 0:
            ax.tick_params(labelbottom=False, labelleft=False)
        if z_bins.index(z_bin) == 0 and generations.index(gen) == 0:
            x_ticks = np.arange(
                x_limits[0], x_limits[1] + 0.01,
                (x_limits[1] - x_limits[0]) / 2.
            )
            ax.set_xticks(x_ticks)
            y_ticks = np.arange(
                y_limits[0], y_limits[1] + 0.01,
                (y_limits[1] - y_limits[0]) / 2.
            )
            ax.set_yticks(y_ticks)
        if z_bins.index(z_bin) == 0 and generations.index(gen) == 1:
            plt.xlabel(x)
            plt.ylabel(y)
    elif labels == 'all':
        plt.xlabel(x)
        plt.ylabel(y)

    if highlight_children == 'off':
        child_colour = 'k'
    elif highlight_children == 'on':
        child_colour = 'r'

    for i in range(gen):
        values = query_points(x, y, z_bin, run_id, i)
        for i in values:
            plt.scatter(
                i[0], i[1],
                marker='o', 
                facecolors='k',
                edgecolors='none',
                alpha=0.2, s=2
            )

    values = query_points(x, y, z_bin, run_id, gen)
    for i in values:
        plt.scatter(
            i[0], i[1],
            marker='o',
            facecolors=child_colour,
            edgecolors='none',
            alpha=0.6, s=2
        )

    if highlight_parents == 'on':
        if gen != 0:
            values = query_parents(x, y, z_bin, run_id, gen)
            for i in values:
                plt.scatter(
                    i[0][0], i[0][1],
                    marker='o',
                    facecolors='none',
                    edgecolors='y',
                    linewidth='0.2',
                    alpha=0.6, s=4
                )

def add_square(
        x, y, 
        x_value, y_value,
        facecolor,
        edgecolor,
        ax, config,
        linewidth=None,
        linestyle='solid'):
    x_width = get_width(x, config)
    y_width = get_width(y, config)
    x_pos = x_value * x_width
    y_pos = y_value * y_width
    ax.add_patch(
        patches.Rectangle(
            (x_pos, y_pos),
            x_width,
            y_width,
            facecolor = facecolor,
            edgecolor = edgecolor,
            linewidth = linewidth,
            linestyle = linestyle,
            alpha = 1
        )
    )

def plot_bin_counts(
        x, y, z_bin,
        run_id, gen,
        config, ax, z_bins, generations,
        labels = None,
        highlight_children='off',
        highlight_parents='off'
    ):
    """Create bin-plot 'x' v. 'y' either by plotting a z-axis slice,
        or all slices at once. Bins are coloured by bin-count.

    Args:
        x (str): `ML`, `SA`, `VF`
        y (str): `ML`, `SA`, `VF`
        z_bin (int): None(default), [0, number_of_bins]
        run_id (str): run identification string
        gen (int): [0, number_of_generations]
        config (yaml.load): use `data_vu.files.load_config_file`
        ax : plt.subplot(111)
        labels (str): None(default), `first_only`, `all`
        highlight_children (str): `on`(default), `off`
        highlight_parents (str): `on`, `off`(default)

    Returns:
        None

    """
    x_limits = get_limits(x, config)
    y_limits = get_limits(y, config)
    plt.xlim(x_limits)
    plt.ylim(y_limits)
    
    if labels == None:
        plt.tick_params(
            axis='both', which='both', bottom='off', top='off', labelbottom='off',
            right='off', left='off', labelleft='off'
        )
    elif labels == 'first_only':
        if z_bins.index(z_bin) != 0 or generations.index(gen) != 0:
            ax.tick_params(labelbottom=False, labelleft=False)
        if z_bins.index(z_bin) == 0 and generations.index(gen) == 0:
            x_ticks = np.arange(
                x_limits[0], x_limits[1] + 0.01,
                (x_limits[1] - x_limits[0]) / 2.
            )
            ax.set_xticks(x_ticks)
            y_ticks = np.arange(
                y_limits[0], y_limits[1] + 0.01,
                (y_limits[1] - y_limits[0]) / 2.
            )
            ax.set_yticks(y_ticks)
        if z_bins.index(z_bin) == 0 and generations.index(gen) == 1:
            plt.xlabel(x)
            plt.ylabel(y)
    elif labels == 'all':
        plt.xlabel(x)
        plt.ylabel(y)

    max_count = get_max_count(run_id)
    values = query_bin_counts(x, y, z_bin, run_id, gen)
    for i in values:
        color = cm.Reds( float(i[2]) / float(max_count) )
        add_square(
            x, y,
            i[0], i[1],
            color,
            None,
            ax, config
        )

    if highlight_parents == 'on':
        if gen != 0:
            values = query_parents(x, y, z_bin, run_id, gen)
            for i in values:
                add_square(
                    x, y,
                    i[0][0], i[0][1],
                    'none',
                    'y',
                    ax, config,
                    2
                )

    if highlight_children == 'on':
        values = query_child_bins(x, y, z_bin, run_id, gen)
        for i in values:
            add_square(
                x, y,
                i[0], i[1],
                'none',
                'r',
                ax, config,
                1, ':'
            )

def plot_mutation_strengths(
        x, y, z_bin,
        run_id, gen,
        config, ax, z_bins, generations,
        labels = None,
        highlight_children='off',
        highlight_parents='off'
    ):
    """Create bin-plot 'x' v. 'y' either by plotting a z-axis slice,
        or all slices at once. Bins are coloured by mutation strength.

    Args:
        x (str): `ML`, `SA`, `VF`
        y (str): `ML`, `SA`, `VF`
        z_bin (int): None(default), [0, number_of_bins]
        run_id (str): run identification string
        gen (int): [0, number_of_generations]
        config (yaml.load): use `data_vu.files.load_config_file`
        ax : plt.subplot(111)
        labels (str): None(default), `first_only`, `all`
        highlight_children (str): `on`(default), `off`
        highlight_parents (str): `on`, `off`(default)

    Returns:
        None

    """
    x_limits = get_limits(x, config)
    y_limits = get_limits(y, config)
    plt.xlim(x_limits)
    plt.ylim(y_limits)
    
    if labels == None:
        plt.tick_params(
            axis='both', which='both', bottom='off', top='off', labelbottom='off',
            right='off', left='off', labelleft='off'
        )
    elif labels == 'first_only':
        if z_bins.index(z_bin) != 0 or generations.index(gen) != 0:
            ax.tick_params(labelbottom=False, labelleft=False)
        if z_bins.index(z_bin) == 0 and generations.index(gen) == 0:
            x_ticks = np.arange(
                x_limits[0], x_limits[1] + 0.01,
                (x_limits[1] - x_limits[0]) / 2.
            )
            ax.set_xticks(x_ticks)
            y_ticks = np.arange(
                y_limits[0], y_limits[1] + 0.01,
                (y_limits[1] - y_limits[0]) / 2.
            )
            ax.set_yticks(y_ticks)
        if z_bins.index(z_bin) == 0 and generations.index(gen) == 1:
            plt.xlabel(x)
            plt.ylabel(y)
    elif labels == 'all':
        plt.xlabel(x)
        plt.ylabel(y)
 
    values = query_mutation_strength(x, y, z_bin, run_id, gen)
    for i in values:
        color = cm.Reds( i[2] )
        add_square(
            x, y,
            i[0], i[1],
            color,
            None,
            ax, config
        )

    if highlight_parents == 'on':
        if gen != 0:
            values = query_parents(x, y, z_bin, run_id, gen)
            for i in values:
                add_square(
                    x, y,
                    i[0][0], i[0][1],
                    'none',
                    'y',
                    ax, config,
                    2
                )

    if highlight_children == 'on':
        values = query_child_bins(x, y, z_bin, run_id, gen)
        for i in values:
            add_square(
                x, y,
                i[0], i[1],
                'none',
                'r',
                ax, config,
                1, ':'
            )
