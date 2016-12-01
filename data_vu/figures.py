import os

import matplotlib.pyplot as plt

from data_vu.utilities import *
from data_vu.queries import *
from data_vu.files import load_config_file
from data_vu.plotting import *

def plot_all_data(run_id):
    generations = count_generations(run_id)
    config = load_config_file(run_id)
    number_of_bins  = config['number_of_convergence_bins']
    print('\nrun_id :\t%s' % run_id)
    print('generations :\t%s' % generations)
    print('binning :\t%(bins)s x %(bins)s x %(bins)s' % {'bins': number_of_bins})

    axes = [
        ['vf', 'sa'],
        ['vf', 'ml'],
        ['sa', 'ml']
    ]

    data = [
        'MutationStrength',
        'DataPoints',
        'BinCounts'
    ]

    for data_type in data:
        for axis in axes:
            if data_type == 'MutationStrength':
                x = axis[0] + '_bin_MS'
                y = axis[1] + '_bin_MS'
            elif data_type == 'DataPoints':
                x = axis[0]
                y = axis[1]
            elif data_type == 'BinCounts':
                x = axis[0] + '_bin'
                y = axis[1] + '_bin'
            plot_all(
                x, y, data_type, run_id, config, generations
            )
    print('...done!')

def plot_points_one(run_id, gen, x, y):
    """
    Args:
        run_id, gen, x, y

    """
    config = load_config_file(run_id)
    ax = plt.subplot(111)
    plot_points_all(x, y, run_id, gen, config, ax)
    plt.savefig(
        '%s_gen%s_%sv%s.png' % (run_id, gen, x, y),
        bbox_inches = 'tight',
        pad_inches = 0,
        dpi = 96 * 4
    )

def plot_all(x, y, data, run_id, config, generations):
    print('plotting %s v %s, %s....' % (x, y, data))
    number_of_bins = config['number_of_convergence_bins']
    fig = plt.figure(figsize=(2 * generations, 2 * number_of_bins))
    for gen in range(generations):
        print('generation :\t%s' % gen)
        for z_bin in range(number_of_bins):
            print('z_bin :\t%s' % z_bin)
            ax = plt.subplot(
                number_of_bins,
                generations,
                z_bin * generations + gen + 1
            )
            if data == 'MutationStrength':
                plot_mutation_strengths(x, y, z_bin, run_id, gen, config, ax)
            elif data == 'DataPoints':
                plot_points(x, y, z_bin, run_id, gen, config, ax)
            elif data == 'BinCounts':
                plot_bin_counts(x, y, z_bin, run_id, gen, config, ax)
    plt.savefig(
        '%s_%s_%s_%s.png' % (run_id, x, y, data),
        bbox_inches = 'tight',
        pad_inches = 0,
        dpi = 96
    )

def plot_some_data(run_id, bins, generations):
    """Plots user-defined bin-normals and generations.

    Args:
        run_id (str): identification string for run.
        bins (list): bin-normals(int) to plot.
        generations (list): generations(int) to plot.

    Returns:
        Saves subplot-figures for all data under the user's constraints.

    """
    print('\nrun_id :\t%s' % run_id)
    print('generations :\t%s' % generations)
    print('bins :\t\t\t%s' % bins)
    
    config = load_config_file(run_id)

    axes = [
        ['vf', 'sa'],
        ['vf', 'ml'],
        ['sa', 'ml']
    ]

    data = [:q!
        'MutationStrength',
        'DataPoints',
        'BinCounts'
    ]

    for data_type in data:
        for axis in axes:
            if data_type == 'MutationStrength':
                x = axis[0] + '_bin_MS'
                y = axis[1] + '_bin_MS'
            elif data_type == 'DataPoints':
                x = axis[0]
                y = axis[1]
            elif data_type == 'BinCounts':
                x = axis[0] + '_bin'
                y = axis[1] + '_bin'
            plot_some(
                x, y, data_type, run_id, bins, generations, config
            )
            plot_overall(
                x, y, data_type, run_id, bins, generations, config
            )
    print('...done!')

def plot_some(x, y, data, run_id, bins, generations, config):
    print('plotting %s v %s, %s....' % (x, y, data))
    fig = plt.figure(figsize=(1.5, 1.5))
    if not os.path.exists(run_id):
        os.makedirs(run_id)
    for gen in generations:
        gen_path = os.path.join(run_id, 'gen%s' % gen)
        if not os.path.exists(gen_path):
            os.makedirs(gen_path)
        print('generation :\t%s' % gen)
        for z_bin in bins:
            ax = plt.subplot(111)
            data_path = os.path.join(gen_path, data)
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            if data == 'MutationStrength':
                           plot_mutation_strengths(x, y, z_bin, run_id, gen, config, ax)
            elif data == 'DataPoints':
                plot_points(x, y, z_bin, run_id, gen, config, ax)
            elif data == 'BinCounts':
                plot_bin_counts(x, y, z_bin, run_id, gen, config, ax)
            plot_path = os.path.join(
                data_path,
                '%s_gen%s_%s_%s_%s_%s.png' % (run_id, gen, x, y, z_bin, data)
            )
            plt.savefig(
                plot_path,
                bbox_inches = 'tight',
                pad_inches = 0,
                dpi = 96 * 4
            )
            plt.cla()

def plot_overall(x, y, data, run_id, bins, generations, config):
    print('plotting %s v %s, %s....' % (x, y, data))
    fig = plt.figure(figsize=(1.5, 1.5))
    if not os.path.exists(run_id):
        os.makedirs(run_id)
    for gen in generations:
        gen_path = os.path.join(run_id, 'gen%s' % gen)
        if not os.path.exists(gen_path):
            os.makedirs(gen_path)
        ax = plt.subplot(111)
        data_path = os.path.join(gen_path, data)
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        if data == 'MutationStrength':
            plot_mutation_strengths_all(x, y, run_id, gen, config, ax)
        elif data == 'DataPoints':
            plot_points_all(x, y, run_id, gen, config, ax)
        elif data == 'BinCounts':
            plot_bin_counts_all(x, y, run_id, gen, config, ax)
        plot_path = os.path.join(
            data_path,
            '%s_gen%s_%s_%s_all_%s.png' % (run_id, gen, x, y, data)
        )
        plt.savefig(
            plot_path,
            bbox_inches = 'tight',
            pad_inches = 0,
            dpi = 96 * 4
        )
        plt.cla()

def compare_runs(
        run_id_0, bins_0, generations_0,
        run_id_1, bins_1, generations_1
    ):
    """Plots user-defined bin-normals and generations.

    Args:
        run_id_0, bins_0, generations_0,
        run_id_1, bins_1, generations_1

    Returns:
        None

    """
    config_0 = load_config_file(run_id_0)
    config_1 = load_config_file(run_id_1)

    axes = [
        ['vf', 'sa'],
        ['vf', 'ml'],
        ['sa', 'ml']
    ]

    data = [
        'DataPoints',
        'BinCounts'
    ]

    plt.cla()

    for data_type in data:
        print(data_type)
        for axis in axes:
            print(axis)
            if data_type == 'DataPoints':
                x = axis[0]
                y = axis[1]

                ax_0 = plt.subplot(121)
                plot_points_all(
                    x, y, run_id_0, generations_0, config_0, ax_0
                )
                ax_1 = plt.subplot(122)
                plot_points_all(
                    x, y, run_id_1, generations_1, config_1, ax_1
                )
                plt.savefig(
                    '%s_%s_%s_%s_v_%s.png' % (
                        data_type, x, y, run_id_0, run_id_1
                    ),
                    bbox_inches = 'tight',
                    pad_inches = 0,
                    dpi = 96 * 4
                )
                plt.cla()

            elif data_type == 'BinCounts':
                x = axis[0] + '_bin'
                y = axis[1] + '_bin'

                ax_0 = plt.subplot(121)
                plot_bin_counts_all(
                    x, y, run_id_0, generations_0, config_0, ax_0
                )
                ax_1 = plt.subplot(122)
                plot_bin_counts_all(
                    x, y, run_id_1, generations_1, config_1, ax_1
                )
                plt.savefig(
                    '%s_%s_%s_%s_v_%s.png' % (
                        data_type, x, y, run_id_0, run_id_1
                    ),
                    bbox_inches = 'tight',
                    pad_inches = 0,
                    dpi = 96 * 4
                )
                plt.cla()
