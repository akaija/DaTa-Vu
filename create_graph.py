import matplotlib.pyplot as plt
import yaml

def plot_data(run_id):
    with open(run_id + '.yaml') as file:
        data = yaml.load(file)
        generations = len(data)
        counter = 0
        for row in data:
            generation = row['generation']
            if row['generation'] == counter:
                print('Plotting data from generation %s....' % generation)
                ML = row['absolute-volumetric-methane-loading']
                SA = row['volumetric-surface-area']
                VF = row['helium-void-fraction']
                # arbitrary boundaries, in excess of expected maxima
                ML_lims = [0, 300]
                SA_lims = [0, 4000]
                VF_lims = [0, 1]
                # surface area v. methane loading
                fig1 = plt.figure(figsize=(6, 6))
                fig1_name = '%s_%s_SAvML' % (run_id, generation)
#                plt.title(fig1_name)
                plt.scatter(SA, ML, marker='o', color='r', alpha=0.5)
                plt.xlim(*SA_lims)
                plt.ylim(*ML_lims)
                plt.savefig(fig1_name, transparent=True)
                plt.close()
                # void fraction v. methane loading
                fig2 = plt.figure(figsize=(6, 6))
                fig2_name = '%s_%s_VFvML' % (run_id, generation)
#                plt.title(fig1_name)
                plt.scatter(VF, ML, marker='o', color='r', alpha=0.5)
                plt.xlim(*VF_lims)
                plt.ylim(*ML_lims)
                plt.savefig(fig2_name, transparent=True)
                plt.close()
                # void fraction v. surface area
                fig3 = plt.figure(figsize=(6, 6))
                fig3_name = '%s_%s_VFvSA' % (run_id, generation)
#                plt.title(fig1_name)
                plt.scatter(VF, SA, marker='o', color='r', alpha=0.5)
                plt.xlim(*VF_lims)
                plt.ylim(*SA_lims)
                plt.savefig(fig3_name, transparent=True)
                plt.close()
            else:
                pass
            counter += 1
