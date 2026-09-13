import bpy, math, os, random
from mathutils import Vector
random.seed(87)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,e=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=.34
 if e: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=e
 return m
ink=mat('Midnight enamel',(.016,.022,.045)); wall=mat('Plum acoustic wall',(.055,.025,.09)); carpet=mat('Violet carpet',(.035,.015,.065)); pink=mat('Neon rose',(1,.025,.22),4); cyan=mat('Neon ice',(.025,.7,1),4); gold=mat('Amber',(1,.4,.06),3); black=mat('Screen glass',(.006,.009,.018)); chrome=mat('Metal trim',(.14,.18,.24)); white=mat('Lettering',(.7,.85,1),2)
def box(n,loc,scale,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if bevel: mod=o.modifiers.new('Soft manufactured edges','BEVEL'); mod.width=bevel; mod.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def text(n,s,loc,size,m):
 cu=bpy.data.curves.new(n,'FONT'); cu.body=s; cu.align_x='CENTER'; cu.size=size; cu.extrude=.003; o=bpy.data.objects.new(n,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); cu.materials.append(m)
box('Carpet',(0,0,-.1),(16,18,.2),carpet)
box('Back wall',(0,8,2.5),(16,.2,5),wall)
for x in [-8,8]:
 box('Side wall',(x,0,2.5),(.2,18,5),wall)
 for z in [.25,3.5,3.65]: box('Wall neon',(x*.985,0,z),(.035,18,.025),pink if z<3.6 else cyan)
for y in [-7,-3,1,5]:
 box('Ceiling beam',(0,y,4.6),(16,.14,.2),ink); box('Overhead strip',(0,y,4.48),(12,.035,.03),cyan)
for z in [.25,3.5,3.65]: box('Back neon',(0,7.85,z),(16,.025,.025),pink)
# Inlaid geometric carpet pattern
for x in range(-7,8):
 for y in range(-8,8):
  o=box('Carpet fleck',(x+.2,y+.25,.006),(.2,.025,.008),mat('Thread'+str(x)+'_'+str(y),(.16,.04,.15))); o.rotation_euler.z=.65
  if (x+y)%3==0: box('Carpet cyan dash',(x-.25,y-.2,.007),(.035,.13,.008),chrome)
def cabinet(x,y,title,accent,index):
 box('Cabinet base '+title,(x,y,.55),(1.15,.95,1.1),ink,.06)
 box('Cabinet tower '+title,(x,y+.22,1.55),(1.15,.55,1.25),ink,.04)
 for s in [-1,1]:
  box('Colored side trim',(x+s*.56,y,1.15),(.035,1,2.25),accent,.01)
 box('CRT bezel',(x,y-.09,1.53),(.98,.12,.78),chrome,.045)
 box('CRT '+str(index),(x,y-.16,1.53),(.86,.025,.65),black,.03)
 # pixel attract screen
 for j in range(4):
  for k in range(6):
   if random.random()>.22: box('Attract pixel',(x+(k-2.5)*.11,y-.18,1.43+j*.085),(.09,.015,.055),accent)
 box('Marquee',(x,y-.075,2.16),(1.08,.13,.29),accent,.02)
 text('Cabinet title',title,(x,y-.15,2.12),.105,ink)
 box('Control deck',(x,y-.35,1.04),(1.12,.58,.12),chrome,.03)
 box('Coin slot',(x+.26,y-.486,.62),(.14,.02,.2),gold,.01)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.065,location=(x-.2,y-.38,1.25)); bpy.context.object.data.materials.append(pink)
 box('Joystick',(x-.2,y-.38,1.16),(.025,.025,.16),chrome)
 for dx in [.12,.29]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.05,location=(x+dx,y-.4,1.13)); bpy.context.object.scale.z=.4; bpy.context.object.data.materials.append(accent)
for i,x in enumerate([-5.8,-4.3,-2.8,0,2.8,4.3,5.8]): cabinet(x,5,['MOON RUN','VECTOR','NEON DRIFT','BRICKSTORM','STAR FALL','RADIO WAVE','VOID 87'][i],[pink,cyan,gold,cyan,pink,gold,cyan][i],i)
for x in [-6.6,6.6]:
 for y in [-2,0,2]: cabinet(x,y,'AFTER DARK',pink,9)
text('Main sign','AFTER HOURS',(0,7.7,3.98),.7,gold)
text('Sub sign','A R C A D E   /   1 9 8 7',(0,7.68,3.6),.18,white)
box('Prize counter',(-4,-4,.55),(4,1.1,1.1),ink,.08)
box('Prize counter neon',(-4,-4.56,.95),(3.8,.035,.025),pink)
text('Prize counter label','THE PRIZE CLUB',(-4,-4.57,.55),.23,gold)
# stools
for x in [-4.3,2.8,5.8]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.28,depth=.13,location=(x,3.75,.65)); bpy.context.object.data.materials.append(wall)
 box('Stool stem',(x,3.75,.33),(.08,.08,.6),chrome)
base=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(base,'source/blender/after-hours.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(base,'public/assets/arcade.glb'),export_format='GLB',export_yup=True)
