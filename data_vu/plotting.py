import os

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import numpy as np
from sqlalchemy import *
from statistics import median

from data_vu.utilities import *
from data_vu.db.queries import *
from data_vu.db.__init__ import engine

def plot_points(
        x, y, z_bin,
        run_id, gen,
        config, ax, z_bins, generations,
        labels = None,
        highlight_children = 'off',
        highlight_parents = 'off',
        pick_parents = 'off',
        pick_bins = 'off'
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
        pick_parents (str): `on`, `off`(default)

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
    elif labels == 'grid_only':
        ax.tick_params(labelbottom=False, labelleft=False)
        number_of_bins = config['number_of_convergence_bins']
        x_ticks = np.arange(
            x_limits[0], x_limits[1] + 0.01,
            (x_limits[1] - x_limits[0]) / float(number_of_bins)
        )
        ax.set_xticks(x_ticks)
        y_ticks = np.arange(
            y_limits[0], y_limits[1] + 0.01,
            (y_limits[1] - y_limits[0]) / float(number_of_bins)
        )
        ax.set_yticks(y_ticks)
        plt.grid(b = True, which = 'both')
    
    x_ = []
    y_ = []
    for i in range(gen):
        s = query_points(x, y, z_bin, run_id, i)
        result = engine.execute(s)
        for row in result:
            x_.append(row[0])
            y_.append(row[1])
        result.close()
    plt.scatter(
        x_, y_,
        marker='o', 
        facecolors='k',
        edgecolors='none',
        alpha=0.5, s=2
    )

    if highlight_children == 'off':
        child_colour = 'k'
    elif highlight_children == 'on':
        child_colour = 'r'
        s = query_points(x, y, z_bin, run_id, gen)
        result = engine.execute(s)
        x_ = []
        y_ = []
        for row in result:
            x_.append(row[0])
            y_.append(row[1])
        result.close()
        plt.scatter(
            x_, y_,
            marker='o',
            facecolors=child_colour,
            edgecolors='none',
            alpha=0.5, s=2
        )

    elif highlight_children == 'top_five':
        top_five = find_most_children(x, y, z_bin, run_id, gen)
        colors = [
            ['red', 'darkred'],
            ['blue', 'darkblue'],
            ['green', 'darkgreen'],
            ['violet', 'darkviolet'],
            ['orange', 'darkorange']
        ]
        counter = 0
        for values in top_five:
            parent_color = colors[counter][0]
            child_color = colors[counter][1]
            plt.scatter(
                *values[0][0],
                marker='o',
                facecolors=parent_color,
                edgecolors='none',
                s=4
            )
            for child_point in values[1]:
                print(child_point)
                plt.scatter(
                    *child_point,
                    marker='o',
                    facecolors=child_color,
                    edgecolors='none',
                    alpha=0.5, s=2
                )
            counter += 1
    if highlight_parents == 'on':
#        if gen != 0:
        x_, y_ = query_parents(x, y, z_bin, run_id, gen)
        plt.scatter(
            x_, y_,
            marker='o',
            facecolors='none',
            edgecolors='g',
            linewidth='0.2',
            alpha=0.5, s=4
        )
#    if pick_parents == 'on':
#        parents = select_parents(x, y, z_bin, run_id, gen)
#        for id in parents:
#            if z_bin != None:
#                parent_z_bin = query_z_bin(x, y, id)[0]
#                if parent_z_bin == z_bin:
#                    point = query_material(x, y, id)
#                    plt.scatter(
#                        point[0][0], point[0][1],
#                        marker = 'o',
#                        facecolors = 'none',
#                        edgecolors = 'g',
#                        linewidth = '0.2',
#                        alpha = 0.5, s = 4
#                    )
#            else: 
#                point = query_material(x, y, id)
#                plt.scatter(
#                    point[0][0], point[0][1],
#                    marker = 'o',
#                    facecolors = 'none',
#                    edgecolors = 'g',
#                    linewidth = '0.2',
#                    alpha = 0.5, s = 4
#                )
    if pick_bins == 'on':
        BC_x = x + '_bin'
        BC_y = y + '_bin'
        result = engine.execute(
                query_bin_counts(BC_x, BC_y, z_bin, run_id, gen - 1).limit(5))
        bins = []
        for row in result:
            line = [row[0], row[1]]
            bins.append(line)
        result.close()
        for b in bins:
            add_square(
                x, y,
                b[0], b[1],
                'none',
                'g',
                ax, config
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
    
    if labels == None or labels == 'grid_only':
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

#    min_count, max_count, avg_count = get_max_count(x, y, z_bin, run_id, gen)
    result = engine.execute(query_bin_counts(x, y, z_bin, run_id, gen))
    x_ = []
    y_ = []
    c_ = []
    for row in result:
        x_.append(row[0])
        y_.append(row[1])
        c_.append(row[2])
    result.close()
#    avg_count = sum(c_) / len(c_)
    avg_count = median(c_)
#    max_dev = max([abs(avg_count - min(c_)), abs(avg_count - max(c_))])
    for i in range(len(c_)):
        dev = avg_count - c_[i]
#        color = cm.brg(0.5 + dev)        
        if c_[i] >= avg_count:
            max_dev = max(c_) - avg_count
            if max_dev != 0:
                dev = (c_[i] - avg_count) / (2 * max_dev)
                fraction = 0.5 + dev
            else:
                fraction = 0.5
        elif c_[i] < avg_count:
            max_dev = avg_count - min(c_)
            if max_dev != 0:
                dev = (avg_count - c_[i]) / (2 * max_dev)
                fraction = 0.5 - dev
            else:
                fraction = 0.5
        count_range = max(c_) - min(c_)       
        fraction = (count_range - (max(c_) - c_[i])) / count_range
        color = cm.brg(fraction)
        add_square(
            x, y,
            x_[i], y_[i],
            color,
            None,
            ax, config
        )
    result.close()

    if highlight_parents == 'on':
        if gen != 0:
            s = query_parents(x, y, z_bin, run_id, gen)
            result = engine.execute(s)
            for row in result:
                add_square(
                    x, y,
                    row[0][0], i[0][1],
                    'none',
                    'y',
                    ax, config,
                    2
                )
            result.close()

#    if highlight_children == 'on':
#        values = query_child_bins(x, y, z_bin, run_id, gen)
#        for i in values:
#            add_square(
#                x, y,
#                i[0], i[1],
#                'none',
#                'r',
#                ax, config,
#                1, ':'
#            )

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

#    result = engine.execute(get_all_bins(x, y, z_bin, run_id, gen))
#    bins = []
#    for row in result:
#        line = [row[0], row[1]]
#        if line not in bins:
#            print(line)
#            bins.append(line)
#    result.close()
#    for b in bins:
#        add_square(
#            x, y,
#            b[0], b[1],
#            'k',
#            ax, config,
#            4
#        )

    if highlight_parents == 'on':
        if gen != 0:
            values = query_parents(
                x[:2] + '_bin',
                y[:2] + '_bin',
                z_bin,
                run_id, gen)
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
        result = engine.execute( query_child_bins(
            x[:2] + '_bin', y[:2] + '_bin', z_bin, run_id, gen)) 
        for row in result:
            add_square(
                x, y,
                row[0], row[1],
                'none',
                'r',
                ax, config,
                1, ':'
            )

def plot_convergence(run_id, generations):
    fig = plt.figure(figsize = (7, 4))
    plt.tick_params(axis='both', which='both', labelbottom='off', labelleft='off')
    convergence = [evaluate_convergence(run_id, i) for i in range(generations)]
    plt.scatter(
        range(generations), convergence,
        marker='o', facecolors='r', edgecolors='none'
    )
    plt.xlim(0, generations)
    plt.ylim(0, max(convergence))
    plt.savefig(
        '%s_convergence_%sgens.png' % (run_id, generations),
        bbox_inches = 'tight',
        pad_inches = 0,
        dpi = 96 * 8
    )
    plt.cla()
    plt.close(fig)
    print('...done!')
