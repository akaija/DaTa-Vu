import matplotlib.pyplot as plt
import yaml

def grab_data(x, gen, data):
    if x == 'ML':
        y = data[gen]['absolute-volumetric-methane-loading']
        lims = [0, 300]
    elif x == 'SA':
        y = data[gen]['volumetric-surface-area']
        lims = [0, 4000]
    elif x == 'VF':
        y = data[gen]['helium-void-fraction']
        lims = [0, 1]
    else:
        print('UNKOWN REQUEST')
    return y, lims

def plot_gen(x, y, gen, data):
    print('Plotting generation %s...' % gen)
    a, a_lims = grab_data(x, gen, data)
    b, b_lims = grab_data(y, gen, data)
    fig = plt.figure(figsize=(6, 6))
    for i in range(gen):
        n, n_lims = grab_data(x, i, data)
        m, m_lims = grab_data(y, i, data)
        plt.scatter(n, m, marker='o', color='k', alpha=0.5)
    plt.scatter(a, b, marker='o', color='r', alpha=0.5)
    plt.xlim(a_lims)
    plt.ylim(b_lims)
    plt.savefig('%s_v_%s_g%s' % (x, y, gen), transparent=False)
    plt.close()

def plot_data(run_id):
    with open(run_id + '.yaml') as file:
        data = yaml.load(file)
    for i in range(len(data)):
        plot_gen('VF', 'ML', i, data)
        plot_gen('VF', 'SA', i, data)
        plot_gen('SA', 'ML', i, data)
    print('Done!')
