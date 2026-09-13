"""Model real arcade, arena, and game props in Blender. Three.js-style coordinates."""
import bpy, math, os, random
from mathutils import Vector
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
random.seed(1987)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def xyz(p):return (p[0],-p[2],p[1])
def mat(name,color,metal=0,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission;return m
ink=mat('Obsidian enamel',(.018,.028,.042),.55,.26);edge=mat('Blue anodized aluminum',(.05,.11,.16),.8,.25);brass=mat('Brushed champagne brass',(.46,.26,.09),.8,.3);rubber=mat('Soft black rubber',(.009,.01,.014),0,.8);wall=mat('Midnight acoustic felt',(.023,.026,.042),0,.9);glass=mat('Smoked CRT glass',(.018,.042,.045),.35,.12);cream=mat('Warm ivory printing',(.85,.73,.49),.1,.5);cyan=mat('Turquoise light',(.04,.65,.7),.15,.3,2);amber=mat('Honey light',(1,.3,.045),.1,.3,2);red=mat('Cherry red plastic',(.45,.016,.022),.15,.25)
# Procedural brushed material microdetail, baked into geometry-friendly material parameters at export.
art=bpy.data.materials.new('Original Brickstorm illustrated side art');art.use_nodes=True;p=art.node_tree.nodes.get('Principled BSDF');im=art.node_tree.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(os.path.join(BASE,'public/assets/brickstorm.png'));art.node_tree.links.new(im.outputs['Color'],p.inputs['Base Color']);art.node_tree.links.new(im.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.18;p.inputs['Roughness'].default_value=.42

def box(n,p,s,m,b=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.name=n;o.dimensions=(s[0],s[2],s[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:mod=o.modifiers.new('Machined bevel','BEVEL');mod.width=b;mod.segments=3;mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def cyl(n,p,r,d,m,axis='y',vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d,location=xyz(p));o=bpy.context.object;o.name=n;o.data.materials.append(m)
 if axis=='z':o.rotation_euler.x=math.pi/2
 if axis=='x':o.rotation_euler.y=math.pi/2
 mod=o.modifiers.new('Rounded machined lip','BEVEL');mod.width=.008;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o

def tube(n,points,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;c.resolution_u=2;sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for a,p in zip(sp.points,points):a.co=(*xyz(p),1)
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);c.materials.append(m);return o

def text(n,body,p,size,m):
 c=bpy.data.curves.new(n,'FONT');c.body=body;c.size=size;c.align_x='CENTER';c.extrude=.0015;c.space_character=1.1;o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.location=xyz(p);o.rotation_euler.x=math.pi/2;c.materials.append(m);return o

def quad(n,points,m):
 mesh=bpy.data.meshes.new(n);mesh.from_pydata([xyz(p) for p in points],[],[(0,1,2,3)]);mesh.uv_layers.new();uv=[(0,0),(1,0),(1,1),(0,1)]
 for i in range(4):mesh.uv_layers[0].data[i].uv=uv[i]
 o=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(m);return o

def cabinet(x,z,yaw=0,name='BRICKSTORM',accent=cyan):
 before=set(bpy.context.scene.objects)
 profile=[(-.57,.1),(.48,.1),(.57,.93),(.55,1.08),(.24,1.2),(.03,1.86),(.34,1.98),(.34,2.27),(-.57,2.27)]
 for side in [-1,1]:
  verts=[xyz((side*.62+dx,y,zz)) for dx in [-.035,.035] for zz,y in profile];l=len(profile);faces=[tuple(range(l-1,-1,-1)),tuple(range(l,l*2))]+[(i,(i+1)%l,(i+1)%l+l,i+l) for i in range(l)];me=bpy.data.meshes.new('Classic cabinet profile');me.from_pydata(verts,[],faces);o=bpy.data.objects.new('Sculpted cabinet side',me);bpy.context.collection.objects.link(o);me.materials.append(ink);mod=o.modifiers.new('T molded edge','BEVEL');mod.width=.018;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');tube('Continuous T molding',[(side*.666,y,zz) for zz,y in profile+[profile[0]]],.012,brass)
  quad('Illustrated side panel',[(side*.661,.22,-.46),(side*.661,.22,.34),(side*.661,1.8,.02),(side*.661,1.8,-.46)],art)
 box('Cabinet lower case',(0,.54,-.01),(1.17,.95,1.04),ink,.04);box('Kick plate',(0,.18,.49),(1.11,.21,.025),rubber)
 for y in [.38,.43,.48,.53,.58]:box('Speaker grille slot',(-.36,y,.505),(.24,.017,.01),rubber,.002)
 box('Recessed coin mechanism',(.22,.64,.521),(.28,.38,.024),edge);box('Coin return',(.22,.53,.542),(.13,.065,.022),rubber)
 box('Illuminated coin slot',(.22,.75,.546),(.16,.06,.025),amber,.007);text('Coin label','25c',(.22,.62,.545),.05,cream)
 for xx in [.105,.335]:
  for yy in [.48,.80]:cyl('Coin plate screw',(xx,yy,.55),.008,.008,brass,'z',12)
 deck=box('Sloping control console',(0,1.065,.3),(1.17,.12,.63),edge,.025);deck.rotation_euler.x=.12
 box('Control panel print',(0,1.135,.31),(1.07,.008,.45),ink,.015)
 cyl('Joystick rubber boot',(-.28,1.16,.32),.095,.025,rubber);cyl('Joystick chrome shaft',(-.28,1.26,.32),.022,.2,brass)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.071,location=xyz((-.28,1.37,.32)));bpy.context.object.data.materials.append(red)
 for xx,zz,m in [(.18,.36,red),(.36,.27,cyan),(.45,.43,amber)]:cyl('Button bezel',(xx,1.16,zz),.066,.02,rubber);cyl('Concave arcade button',(xx,1.18,zz),.049,.032,m)
 text('Controls printing','MOVE',(-.29,1.145,.52),.032,cream)
 box('Monitor housing',(0,1.56,-.17),(1.18,.8,.55),ink,.05)
 bezel=box('Deep CRT surround',(0,1.56,.135),(1.06,.76,.08),rubber,.045);bezel.rotation_euler.x=-.28
 # Subdivided slightly convex glass with UV artwork.
 vs=[];uvs=[];faces=[];N=20
 for j in range(N+1):
  for i in range(N+1):
   u=i/N;v=j/N;xx=(u-.5)*.93;yy=(v-.5)*.6;zz=.21-.28*yy+.035*(1-(xx/.55)**2-(yy/.4)**2);vs.append(xyz((xx,1.56+yy,zz)));uvs.append((u,v))
 for j in range(N):
  for i in range(N):a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
 me=bpy.data.meshes.new('Convex CRT surface');me.from_pydata(vs,[],faces);me.uv_layers.new()
 for poly in me.polygons:
  poly.use_smooth=True
  for li in poly.loop_indices:me.uv_layers[0].data[li].uv=uvs[me.loops[li].vertex_index]
 o=bpy.data.objects.new('Convex illustrated CRT',me);bpy.context.collection.objects.link(o);me.materials.append(art)
 box('Marquee top housing',(0,2.1,-.05),(1.18,.29,.72),ink,.03);box('Backlit marquee',(0,2.11,.323),(1.08,.21,.02),accent,.015);text('Screen printed marquee',name,(0,2.075,.34),.12,ink)
 for xx in [-.5,.5]:
  for yy in [2.04,2.18]:cyl('Marquee screw',(xx,yy,.34),.008,.009,brass,'z',12)
 for xx in [-.44,.44]:box('Rubber foot',(xx,.055,0),(.12,.1,.6),rubber)
 parent=bpy.data.objects.new(name+' cabinet assembly',None);bpy.context.collection.objects.link(parent)
 for o in set(bpy.context.scene.objects)-before:
  if o!=parent:o.parent=parent
 parent.location=xyz((x,0,z));parent.rotation_euler.z=yaw

# The arcade room: panelled walls, inlaid terrazzo, molded cornices, actual metal details.
floor=mat('Deep teal terrazzo',(.025,.042,.048),.35,.3)
box('Arcade terrazzo floor',(0,-.12,0),(13,.24,14),floor)
for x in range(-6,7):box('Brass floor seam',(x,.005,0),(.009,.012,14),brass,.001)
for z in range(-6,8):box('Brass floor seam',(0,.005,z),(13,.012,.009),brass,.001)
box('Back acoustic wall',(0,2.3,-5.8),(13,4.6,.2),wall)
for x in [-6.4,6.4]:box('Side acoustic wall',(x,2.3,0),(.2,4.6,14),wall)
for x in [i*.3 for i in range(-21,22)]:box('Fluted wall timber',(x,2.3,-5.65),(.035,4.3,.055),edge,.008)
for y in [.15,3.3,3.45]:box('Wall architectural trim',(0,y,-5.5),(12.6,.025,.025),brass,.005)
for x in [-6.2,6.2]:
 for y in [.2,3.35]:box('Side architectural neon',(x,y,0),(.015,.02,13),amber,.002)
for z in [-5,-2,1,4]:
 box('Overhead metal beam',(0,4.1,z),(12.5,.16,.22),ink)
 for x in [-3,3]:box('Recessed overhead luminaire',(x,3.99,z),(2.1,.018,.035),amber,.006)
# Arch around the hero cabinet
for r,m in [(2.0,brass),(1.93,cyan)]:tube('Hero cabinet arch',[(math.cos(a)*r,1.9+math.sin(a)*r,-4.4) for a in [i*math.pi/80 for i in range(81)]],.025,m)
for x in [-2,2]:box('Arch pillar',(x,.95,-4.4),(.05,1.9,.06),brass)
text('Arcade main wordmark','AFTER HOURS',(0,3.02,-5.43),.48,cream);text('Arcade secondary wordmark','A R C A D E   -   1 9 8 7',(0,2.72,-5.42),.11,brass)
cabinet(0,-2.7)
for x,name,acc in [(-2.3,'LUNAR RUN',amber),(2.3,'VECTOR',cyan),(-3.95,'NIGHT DRIVE',cyan),(3.95,'STARFALL',amber)]:cabinet(x,-4.05,.1 if x<0 else -.1,name,acc)
# Poster lightboxes at human scale
for x in [-5.3,5.3]:
 box('Framed art lightbox',(x,2,-5.35),(1.15,1.8,.12),brass)
 quad('Generated illustrated wall art',[(x-.54,1.15,-5.27),(x+.54,1.15,-5.27),(x+.54,2.85,-5.27),(x-.54,2.85,-5.27)],art)
# Prize counter, glass shelf frame, trophies, token cup.
box('Prize counter cabinet',(-4,.6,2.5),(3.5,1.2,1.2),ink,.06);box('Counter marble top',(-4,1.24,2.5),(3.65,.1,1.3),edge,.025);text('Prize club title','THE PRIZE CLUB',(-4,.72,3.115),.22,cream)
for x in [-5.5,-2.5]:tube('Counter rail',[(x,1.3,2),(x,2.1,2),(x,2.1,3)],.025,brass)
for x in [-4.8,-4,-3.2]:
 cyl('Prize plinth',(x,1.35,2.5),.19,.12,brass);cyl('Prize stem',(x,1.57,2.5),.04,.3,brass)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.17,location=xyz((x,1.8,2.5)));bpy.context.object.data.materials.append(brass)
for x in [-2.3,2.3]:
 cyl('Stool base',(x,.05,-2.8),.27,.08,edge);cyl('Stool stem',(x,.4,-2.8),.045,.7,brass);cyl('Upholstered stool',(x,.78,-2.8),.29,.14,rubber)

def export(name):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.convert(target='MESH');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'source/blender/'+name+'.blend'));bpy.ops.export_scene.gltf(filepath=os.path.join(BASE,'public/assets/'+name+'.glb'),export_format='GLB',export_yup=True)
export('arcade-premium')
# Separate modeled arena, designed around the actual paddle collision volume.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
platform=mat('Arena graphite ceramic',(.022,.038,.05),.65,.28);stone=mat('Basalt architectural panels',(.028,.033,.045),.3,.6)
for i in range(3):box('Stepped arena dais',(0,-.23-i*.18,-3.7),(7.2+i*.5,.2,11+i*.5),platform,.09)
for x in [-3.4,3.4]:
 box('Court brass curb',(x,-.03,-3.7),(.10,.12,10.8),brass,.025);box('Court luminous edge',(x,.04,-3.7),(.023,.025,10.6),cyan,.007)
 for z in [-7.5,-5,-2.5,0,1.5]:
  box('Peripheral buttress',(x*1.2,1,z),(.38,2,.55),stone,.06);box('Buttress inset light',(x*1.2,1.3,z+.29),(.07,1.1,.025),amber,.01)
for z in [-7,-5,-3,-1,1]:box('Platform inset brass joint',(0,.001,z),(6.7,.012,.012),brass,.002)
for i in range(6):
 z=-8.4-i*1.15;r=4.8+i*.22
 for m,rr,rad in [(edge,r,.16),(brass,r-.19,.025),(cyan,r-.26,.012)]:
  tube('Monumental arena arch',[(math.cos(a)*rr,1+math.sin(a)*rr,z) for a in [j*math.pi/96 for j in range(97)]],rad,m)
 for x in [-r,r]:box('Arch foundation',(x,.25,z),(.38,1.5,.5),stone,.04)
# Side viewing galleries and strong architectural perspective
for side in [-1,1]:
 for tier in range(3):box('Gallery terrace',(side*(6+tier*.6),.1+tier*.35,-6),(1,.25,16),stone,.04)
 tube('Gallery guard rail',[(side*5.3,.7,2),(side*5.3,.7,-14)],.035,brass)
for x in [-2.8,2.8]:
 box('Serve platform marker',(x,.008,.6),(.6,.02,.04),amber,.005)
nebula_mat=bpy.data.materials.new('Generated cosmic cyclorama');nebula_mat.use_nodes=True;np=nebula_mat.node_tree.nodes.get('Principled BSDF');ni=nebula_mat.node_tree.nodes.new('ShaderNodeTexImage');ni.image=bpy.data.images.load(os.path.join(BASE,'public/assets/arena-nebula.png'));nebula_mat.node_tree.links.new(ni.outputs['Color'],np.inputs['Base Color']);nebula_mat.node_tree.links.new(ni.outputs['Color'],np.inputs['Emission Color']);np.inputs['Emission Strength'].default_value=1
quad('Nebula cyclorama',[(-36,-13,-32),(36,-13,-32),(36,35,-32),(-36,35,-32)],nebula_mat)
export('arena-premium')
# Native Blender modeled brick and controller paddle, exported together as a prop library.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
body=box('BRICK_BODY',(0,0,0),(.55,.44,.4),edge,.045);box('BRICK_INLAY',(0,0,.207),(.45,.33,.014),cyan,.025)
for x in [-.215,.215]:
 for y in [-.155,.155]:cyl('BRICK_RIVET',(x,y,.219),.012,.01,brass,'z',12)
export('brick-premium')
print('PREMIUM_ASSET_EXPORT_COMPLETE')
