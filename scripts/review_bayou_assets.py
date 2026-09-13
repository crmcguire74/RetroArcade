"""Native Blender cabinet and isolated asset review; no runtime export."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent.parent;OUT=BASE/'design/bayou-crossing'
# Reuse the already-authored cabinet construction, preserving the Arcade's scale and details.
exec((BASE/'scripts/model_premium.py').read_text().split('# The arcade room:')[0])
OUT=Path(BASE)/'design/bayou-crossing';BASE=Path(BASE)
art.node_tree.nodes.get('Image Texture').image=bpy.data.images.load(str(OUT/'images/visual-concept.png'))
ink.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.016,.054,.03,1)
cyan.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.36,.6,.14,1)
cyan.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.36,.6,.14,1)
cabinet(0,0,0,'BAYOU CROSSING',cyan)
for o in bpy.context.scene.objects:
 if o.type=='FONT' and o.data.body=='BAYOU CROSSING':o.data.size=.10
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in ['MESH','CURVE','FONT']:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in bpy.context.selected_objects if o.type=='MESH');bpy.ops.object.convert(target='MESH')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o['asset_group']='cabinet'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'meshes/bayou-cabinet.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.1,.15,.12,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.4
floor=mat('Review neutral floor',(.06,.085,.07),0,.6);box('Review plinth',(0,-.09,0),(200,.1,200),floor)
def area(p,power,size,color):
 d=bpy.data.lights.new('Review softbox','AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new('Review softbox',d);scene.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
area((3,-3,5),650,4,(1,.8,.55));area((-3,-1,3),450,3,(.5,.8,1))
bpy.ops.object.camera_add(location=(3,-4,2.8));cam=bpy.context.object;scene.camera=cam;cam.data.lens=48;cam.rotation_euler=(Vector((0,0,1.15))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/'renders/cabinet.png');bpy.ops.render.render(write_still=True)
# Isolated mesh detail renders, preserving separate source before inspection setup.
bpy.ops.wm.open_mainfile(filepath=str(OUT/'meshes/bayou-assets.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.3,.34,.30,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.6
assets={name:bpy.data.objects[name.upper()] for name in ['frog','truck','log','turtle']}
for o in assets.values():o.hide_render=True;o.hide_set(False)
# Ground with physically coherent contact shadows.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03));ground=bpy.context.object;m=bpy.data.materials.new('Neutral moss grey');m.diffuse_color=(.15,.18,.14,1);ground.data.materials.append(m)
area((2,-3,4),550,4,(1,.88,.65));area((-3,2,3),450,3,(.6,.8,1))
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
for name,o in assets.items():
 o.hide_render=False
 if name=='frog':p=(1.05,1.7,1.0);t=(0,.02,.22);lens=56
 elif name=='truck':p=(3.7,-4.4,2.8);t=(0,0,.68);lens=50
 elif name=='log':p=(3.5,-3.1,2.1);t=(0,0,.12);lens=50;ground.location.z=-.31
 else:p=(1.2,1.7,1.0);t=(0,.05,.08);lens=50;ground.location.z=-.10
 cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;scene.render.filepath=str(OUT/'renders'/('asset-'+name+'.png'));bpy.ops.render.render(write_still=True);o.hide_render=True;ground.location.z=-.03
print('CABINET_AND_ASSET_REVIEW_COMPLETE',flush=True)
