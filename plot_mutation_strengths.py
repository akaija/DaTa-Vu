#------------------------------------------------------------------------------
# File plot_mutation_strengths.py
#------------------------------------------------------------------------------

# standard library imports
import sys

# related third party imports
import yaml
import bpy

# related application/library specific imports
import PseudoMaterial

base_path  = 'C:\\Users\\Alec\\Desktop'
scene      = bpy.context.scene
add_cube   = bpy.ops.mesh.primitive_cube_add

def MakeMaterial(diffuse, specular, alpha):
    material = bpy.data.materials.new(name)
    material.diffuse_color = diffuse
    material.diffuse_shader = 'LAMBERT'
    material.diffuse_intensity = 1.0
    material.specular_color = specular
    material.specular_shader = 'COOKTORR'
    material.specular_intensity = 0.5
    material.alpha = alpha
    material.ambient = 1
    return material

def SetMaterial(bpy_object, material):
    something = bpy_object.data
    something.materials.append(material)

def plot_bin(x, y, z, strength):
    add_cube(location=(x, y, z), size=1)
    bpy.data.objects["Cube"].select = True
    bpy.context.scene.objects[0].name = 'bin_%s_%s_%s' % (x, y, z)
    color = (1, strength, strength)
    material = MakeMaterial(color, (1, 1, 1), 0.2)
    SetMaterial(bpy.context.object, material)

def plotting_loop(strength_file):
    with open(strength_file) as file:
        data = yaml.load(file)
    for i in data:
        x         = i['ML_bin']
        y         = i['SA_bin']
        z         = i['VF_bin']
        strength  = i['strength']
        plot_bin(x, y, z, strength)

#if __name__ == '__main__':
#    plotting_loop(
#        'C:\\Users\\Alec\\Desktop\\yaml\\2016-09-29T22%3A57%3A15.902237_gen1.yaml'
#    )
