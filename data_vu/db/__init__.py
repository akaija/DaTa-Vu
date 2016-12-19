import os

from sqlalchemy import *
import yaml

with open(os.path.join('settings', 'database.yaml'), 'r') as yaml_file:
    dbconfig = yaml.load(yaml_file)
connection_string = dbconfig['connection_string']
engine = create_engine(connection_string)

meta = MetaData(bind=engine)
materials = Table('materials', meta, autoload=True)
mutation_strengths = Table('mutation_strengths', meta, autoload=True)
