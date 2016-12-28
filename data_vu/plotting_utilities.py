import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches

from data_vu.utilities import *
from data_vu.db.queries import *
from data_vu.db.__init__ import engine

def labeling(labels, ax, config):
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
        plt.grid(b = True, which = 'both', linestyle='-', alpha=0.5)

def highlight_children(children):
    if data_type == 'DataPoints':
        if children == 'off':
            child_colour = 'k'
        elif children == 'on':
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
                alpha=0.7, s=2
            )
        
        elif children == 'top_five':
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
                    plt.scatter(
                        *child_point,
                        marker='o',
                        facecolors=child_color,
                        edgecolors='none',
                        alpha=0.5, s=2
                    )
                counter += 1
#    elif data_type == 'BinCounts':
#    elif data_type == 'MutationStrength':

def hightlight_parents():
    x_, y_ = query_parents(x, y, z_bin, run_id, gen)
    if len(x_) > 0 and len(y_) > 0:
        plt.scatter(
            x_, y_,
            marker='o',
            facecolors='none',
            edgecolors='k',
            linewidth='0.4',
            alpha=0.5, s=5
        )


