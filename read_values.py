import os

from sqlalchemy import func
import yaml

from runDB_declarative import Base, Material, session

def run_ids():
    values = session.query(Material.run_id, func.max(Material.generation),func.count(Material.id)).group_by(Material.run_id).all()[:]
    print('run-id\t\t\t\tgenerations\tmaterials')
    for i in values:
        print('%s\t%s\t\t%s' % (i[0], i[1], i[2]))

def get_data(run_id):
    print('run-id\t\t\t\tgenerations\tmaterials')
    info = session.query(func.max(Material.generation), func.count(Material.id)).filter(Material.run_id==run_id).all()[0]
    print('%s\t%s\t\t%s' % (run_id, info[0], info[1]))
    data = []
    for i in range(info[0]):
        print('Writing generation :\t%s' % i)
        values = session.query(Material.absolute_volumetric_loading, Material.volumetric_surface_area, Material.helium_void_fraction).filter(Material.run_id==run_id, Material.generation==i).all()[:]
        AVL = []
        VSA = []
        HVF = []
        for j in values:
            AVL.append(j[0])
            VSA.append(j[1])
            HVF.append(j[2])
        generation = {
            "generation" : i,
            "absolute-volumetric-methane-loading"  : AVL,
            "volumetric-surface-area"              : VSA,
            "helium-void-fraction"                 : HVF
        }
        data.append(generation)
    with open(run_id + '_data.yaml', 'w') as file:
        yaml.dump(data, file,default_flow_style=False)
