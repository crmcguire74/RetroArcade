"""Function-gate engineering study only. Not final composition or a runtime export."""
import bpy, math, os, json
from mathutils import Vector
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(BASE,'design/bayou-crossing')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,v):
 m=bpy.data.materials.new(name);m.diffuse_color=(v,v,v,1);return m
paper=mat('Substrate',.82);road=mat('Asphalt',.33);water=mat('River',.65);dark=mat('Object silhouettes',.12);white=mat('Lane markings',.95);mid=mat('Banks',.54)
def box(n,p,s,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def sphere(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=p);o=bpy.context.object;o.name=n;o.scale=s;o.data.materials.append(m);return o
def cylinder(n,p,r,length,m,along_x=False):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=length,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(m)
 if along_x:o.rotation_euler.y=math.pi/2
 return o
box('Continuous terrain substrate',(0,7.8,-.35),(22,25,.6),paper)
for row in range(13):
 m=road if 1<=row<=5 else water if 7<=row<=11 else mid
 box('Lane '+str(row),(0,row*1.3,-.025),(16,1.28,.10),m)
 if 1<=row<=5:
  for x in range(-7,8,2):box('Road stripe',(x,row*1.3-.6,.04),(.7,.035,.018),white)
for x in [-7.8,7.8]:
 box('Side boundary berm',(x,7.8,.18),(.6,18,.4),mid)
 for y in [-.5,7.8,16.4]:cylinder('Boundary bollard',(x,y,.6),.16,1,dark)
# Grounded truck silhouette with separate cabin, bed, bonnet, and four wheels.
for row in range(1,6):
 x=(-4.5+row*1.6)%8-4;y=row*1.3
 box('Truck chassis',(x,y,.4),(2.3,.88,.3),dark);box('Truck cab',(x-.25,y,.85),(.9,.85,.75),dark);box('Truck bonnet',(x-.9,y,.55),(.6,.82,.25),dark)
 box('Truck bed',(x+.7,y,.53),(.9,.85,.2),dark)
 for xx in [x-.75,x+.75]:
  for yy in [y-.45,y+.45]:o=cylinder('Truck wheel',(xx,yy,.28),.26,.16,dark);o.rotation_euler.x=math.pi/2
# Logs at the identical lane positions used by the simulation.
for row in range(7,12):
 for x in [-5,0,5]:
  if row in [8,10]:
   for dx in [-.75,0,.75]:sphere('Turtle shell',(x+dx,row*1.3,.12),(.45,.42,.22),dark);sphere('Turtle head',(x+dx,row*1.3+.42,.12),(.16,.22,.13),dark)
  else:cylinder('Rideable log',(x,row*1.3,.12),.38,3.1,dark,True);cylinder('Broken log branch',(x+.7,row*1.3,.52),.1,.4,dark)
for x in [-5.2,-2.6,0,2.6,5.2]:
 cylinder('Home lily pad',(x,15.6,.12),.65,.12,dark)
 sphere('Home flower',(x,15.6,.27),(.22,.22,.15),white)
# A readable full-body frog silhouette at the actual start location.
sphere('Frog body',(0,0,.24),(.28,.34,.23),dark);sphere('Frog head',(0,.23,.36),(.3,.25,.21),dark)
for side in [-1,1]:
 sphere('Frog rear leg',(side*.25,-.2,.14),(.21,.23,.13),dark)
 sphere('Frog front foot',(side*.3,.36,.06),(.17,.2,.05),dark)
 sphere('Frog rear foot',(side*.38,-.4,.06),(.2,.15,.05),dark)
# Arrival is a direct cabinet portal onto an open-air bank, not an architectural doorway.
box('Arrival apron',(0,-1.3,.005),(3.4,1.3,.04),white)
for x in [-1.4,1.4]:cylinder('Arrival lamp base',(x,-1.4,.12),.18,.16,dark)
# A lamp boom layer for reflected overhead projection; there is intentionally no roof.
ceiling=[]
for x in [-7.4,7.4]:
 for y in [1.3,5.2]:
  ceiling.append(box('Overhead lamp boom',(x+(1 if x<0 else -1)*.5,y,3.5),(1.3,.1,.1),dark))
  ceiling.append(box('Overhead lamp head',(x+(1 if x<0 else -1)*1.1,y,3.45),(.4,.32,.12),dark))
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True;scene.display.shading.background_type='WORLD';scene.world.color=(1,1,1)
scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera
camera.data.type='ORTHO';camera.data.ortho_scale=27
camera.location=(0,7.8,35);camera.rotation_euler=(0,0,0);camera.rotation_euler=(Vector((0,7.8,0))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.resolution_x=1200;scene.render.resolution_y=1400
for o in ceiling:o.hide_render=True
scene.render.filepath=os.path.join(OUT,'plans/lower-room.png');bpy.ops.render.render(write_still=True)
all_mesh=[o for o in scene.objects if o.type=='MESH']
for o in all_mesh:o.hide_render=o not in ceiling
scene.render.filepath=os.path.join(OUT,'plans/reflected-ceiling.png');bpy.ops.render.render(write_still=True)
for o in all_mesh:o.hide_render=False
camera.data.ortho_scale=25;camera.location=(15,-15,17);camera.rotation_euler=(Vector((0,7,0))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.filepath=os.path.join(OUT,'plans/visual-target.png');bpy.ops.render.render(write_still=True)
camera.data.ortho_scale=24;camera.location=(25,7.8,3);camera.rotation_euler=(Vector((0,7.8,3))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.resolution_x=1400;scene.render.resolution_y=700;scene.render.filepath=os.path.join(OUT,'plans/side-elevation.png');bpy.ops.render.render(write_still=True)
# Empty opening-mask plate: no cut wall, doorway, or roof is proposed in this open-air world.
for o in all_mesh:o.hide_render=True
scene.render.filepath=os.path.join(OUT,'masks/no-architectural-openings.png');bpy.ops.render.render(write_still=True)
for o in all_mesh:o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'meshes/layout-study.blend'))
json.dump({'source':'Blender actual blockout meshes','status':'engineering-study-not-final-art','meshCount':len(all_mesh),'ceiling':'open-air; four lamp booms only','coordinateSystem':'Blender Z up; lane progression +Y'},open(os.path.join(OUT,'plans/provenance.json'),'w'),indent=2)
print('BAYOU_FUNCTION_LAYOUT_STUDY_COMPLETE')
