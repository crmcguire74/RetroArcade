"""Approved Bayou art direction -> Blender meshes. Saves native source and review renders.
No GLB export here: Form approval is recorded separately before export.
Coordinates: Blender Z up, +Y toward homes; GLTF maps +Y to runtime -Z.
"""
import bpy, math, os, random, json
from mathutils import Vector
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent;OUT=BASE/'design/bayou-crossing';random.seed(1987)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection' and c.users==0:bpy.data.collections.remove(c)

def material(name,color,rough=.45,metal=0,emission=0,noise=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 if noise:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=noise;n.inputs['Detail'].default_value=3
  b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.25;b.inputs['Distance'].default_value=.04;m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 return m
jade=material('Frog jade wet skin',(.075,.32,.09),.27,noise=80)
cream=material('Frog creamy throat',(.62,.68,.31),.38)
gold=material('Iris amber',(.72,.38,.055),.19,.2)
black=material('Obsidian pupil',(.003,.009,.008),.08)
spot=material('Frog golden freckles',(.33,.44,.065),.34)
teal=material('Truck teal enamel',(.035,.24,.235),.24,.45)
ivory=material('Truck cream paint',(.69,.66,.48),.31,.25)
chrome=material('Satin chrome',(.34,.42,.43),.2,.85)
rubber=material('Tire tread rubber',(.013,.022,.024),.76)
glass=material('Blue smoked glass',(.022,.078,.10),.10,.6)
light=material('Warm headlamp',(.95,.57,.18),.2,emission=3)
red=material('Ruby tail lamp',(.62,.027,.012),.24,emission=.6)
bark=material('Wet cypress bark',(.13,.078,.039),.72,noise=32)
ridge=material('Cypress raised grain',(.235,.14,.07),.68)
endgrain=material('Cypress golden cut grain',(.4,.25,.105),.62)
moss=material('Soft moss',(.16,.26,.055),.9,noise=60)
shell=material('Turtle olive shell',(.19,.26,.07),.37,noise=48)
scute=material('Turtle scute warm rims',(.35,.35,.105),.48)
skin=material('Turtle damp skin',(.16,.235,.11),.42,noise=65)
asphalt=material('Wet asphalt',(.036,.047,.054),.25,.18,noise=90)
water=material('Moonlit river',(.027,.105,.115),.16,.4,noise=3)
ground=material('Earth substrate',(.063,.081,.034),.94)
leaf=material('Bayou foliage',(.075,.17,.062),.82)
leaflight=material('Silver green leaves',(.24,.32,.095),.75)
stripe=material('Weathered lane paint',(.67,.62,.42),.55)
metal=material('Lantern wrought bronze',(.082,.069,.038),.42,.7)
petal=material('Water lily petals',(.73,.67,.79),.3)

def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);return o

def box(name,p,s,mat,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Rounded manufactured edges','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Corner normals','WEIGHTED_NORMAL')
 return o

def sphere(name,p,s,mat,seg=20,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=1,location=p);o=bpy.context.object;o.name=name;o.scale=s;o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=True
 return o

def cyl(name,p,r,d,mat,axis='z',vertices=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d,location=p);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 if axis=='x':o.rotation_euler.y=math.pi/2
 if axis=='y':o.rotation_euler.x=math.pi/2
 return o

def tube(name,points,r,mat,res=2):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=res;sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for a,p in zip(sp.points,points):a.co=(*p,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(mat);return o

def capsule(name,a,b,r,mat):
 o=sphere(name,(Vector(a)+Vector(b))*.5,(r,r,(Vector(b)-Vector(a)).length*.5+r),mat,12,8);o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler();return o

def text(name,body,p,size,mat):
 c=bpy.data.curves.new(name,'FONT');c.body=body;c.align_x='CENTER';c.size=size;c.extrude=.001;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.location=p;o.rotation_euler.x=math.pi/2;c.materials.append(mat);return o

def finish_asset(name,before):
 parts=[o for o in bpy.context.scene.objects if o not in before and o.type in ['MESH','CURVE','FONT']]
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o.hide_render=True;o.hide_set(True)
 o['asset_id']=name;o['authoring']='Blender procedural authored mesh from approved generated reference';return o

# FROG: continuous silhouette, distinct eye sockets, thighs, shins and splayed toes.
before=set(bpy.context.scene.objects)
sphere('Pear shaped body',(0,-.07,.22),(.235,.29,.19),jade,28,18)
sphere('Broad head',(0,.19,.31),(.265,.22,.14),jade,28,16)
sphere('Pale lower jaw',(0,.225,.237),(.235,.195,.062),cream,24,10)
tube('Curved mouth seam',[(-.205,.29,.267),(-.13,.369,.265),(0,.395,.263),(.13,.369,.265),(.205,.29,.267)],.006,black,1)
for side in [-1,1]:
 sphere('Raised eye socket',(side*.166,.207,.42),(.101,.103,.10),jade)
 sphere('Amber iris',(side*.172,.279,.45),(.069,.046,.07),gold)
 sphere('Vertical glossy pupil',(side*.172,.316,.452),(.025,.019,.057),black,16,10)
 sphere('Eye glint',(side*.157,.333,.478),(.008,.004,.01),ivory,8,6)
 capsule('Front upper arm',(side*.20,.16,.24),(side*.28,.21,.10),.045,jade)
 capsule('Front forearm',(side*.28,.21,.10),(side*.29,.37,.045),.036,jade)
 sphere('Powerful rear thigh',(side*.233,-.16,.16),(.133,.185,.11),jade)
 capsule('Folded rear shin',(side*.33,-.24,.14),(side*.26,-.36,.065),.043,jade)
 for front in [False,True]:
  base=(side*(.29 if front else .29),.37 if front else -.38,.043)
  for j in range(3):
   tip=(base[0]+side*(j-1)*.062,base[1]+(.1 if front else -.08)+abs(j-1)*.025,.022)
   capsule('Webbed toe',base,tip,.016,jade);sphere('Sticky toe pad',tip,(.028,.03,.012),spot,10,6)
  mesh('Webbing',[(base[0],base[1],.031),(base[0]-.065,base[1]+(.08 if front else -.07),.023),(base[0]+.065,base[1]+(.08 if front else -.07),.023)],[(0,1,2)],jade)
 for j in range(20):
  y=random.uniform(-.25,.15);x=side*random.uniform(.08,.17);z=.22+.18*math.sqrt(max(.1,1-(y+.07)**2/.29**2-x*x/.235**2))
  sphere('Golden skin fleck',(x,y,z),(.01,.015,.003),spot,6,4)
frog=finish_asset('FROG',before)

# PICKUP: shaped sheet metal, wheel arches, glazing, bed cavity, trim, grille and mirrors.
before=set(bpy.context.scene.objects)
box('Chassis',(0,0,.34),(2.58,.88,.18),rubber,.04)
box('Lower teal body',(0,0,.5),(2.7,.98,.24),teal,.075)
box('Long bonnet',(.85,0,.75),(.86,.98,.32),teal,.07)
box('Cab lower sill',(.02,0,.72),(.96,1,.33),teal,.05)
# Slanted windshield and cab roof from an extruded side profile.
profile=[(-.49,.69),(-.49,1.35),(.16,1.35),(.47,.9),(.47,.69)]
vs=[(x,y,z) for y in [-.47,.47] for x,z in profile];N=len(profile)
body=mesh('Shaped cab pillars',vs,[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],ivory)
be=body.modifiers.new('Cab seams bevel','BEVEL');be.width=.035;be.segments=2
for side in [-1,1]:
 mesh('Side glass', [(-.415,side*.481,.9),(-.415,side*.481,1.28),(.115,side*.481,1.28),(.355,side*.481,.93)],[(0,1,2,3)],glass)
 tube('Window gasket',[(-.415,side*.487,.9),(-.415,side*.487,1.28),(.115,side*.487,1.28),(.355,side*.487,.93),(-.415,side*.487,.9)],.014,rubber,1)
 box('Door panel',(-.025,side*.499,.745),(.84,.025,.28),teal,.02)
 box('Door handle',(-.31,side*.525,.85),(.11,.024,.025),chrome,.005)
 tube('Wing mirror arm',[(.30,side*.49,.95),(.32,side*.65,.96)],.014,chrome,1)
 box('Wing mirror',(.32,side*.67,1.0),(.12,.07,.16),chrome,.02)
 box('Bed side rail',(-.92,side*.455,.79),(.85,.08,.4),teal,.025)
 box('Body cream trim',(0,side*.507,.62),(2.56,.02,.035),ivory,.004)
mesh('Sloped windshield',[(.191,-.41,1.285),(.191,.41,1.285),(.438,.41,.94),(.438,-.41,.94)],[(0,1,2,3)],glass)
for y in [-.21,.21]:tube('Wiper',[(.43,y,.947),(.36,y-.11,1.06)],.009,rubber,1)
box('Rear cab glass',(-.512,0,1.1),(.015,.73,.28),glass,.018)
box('Bed floor',(-.93,0,.58),(.8,.79,.08),teal,.018)
box('Tailgate',(-1.31,0,.78),(.09,.98,.38),teal,.023)
for yy in [-.3,-.15,0,.15,.3]:box('Bed rib',(-.9,yy,.635),(.7,.025,.018),chrome,.003)
for x in [-.85,.84]:
 for side in [-1,1]:
  cyl('Tire',(x,side*.505,.31),.285,.17,rubber,'y',24)
  cyl('Wheel rim',(x,side*.6,.31),.171,.024,chrome,'y',20)
  cyl('Wheel hub',(x,side*.617,.31),.062,.025,metal,'y',12)
  for j in range(6):
   a=j*math.tau/6;cyl('Wheel lug',(x+math.cos(a)*.1,side*.622,.31+math.sin(a)*.1),.016,.01,black,'y',8)
  tube('Raised wheel arch',[(x+math.cos(a)*.326,side*.52,.31+math.sin(a)*.326) for a in [j*math.pi/16 for j in range(17)]],.025,teal,1)
for xx in [-1.39,1.4]:box('Chrome bumper',(xx,0,.43),(.13,1.08,.12),chrome,.025)
box('Radiator grille',(1.321,0,.71),(.025,.57,.22),rubber,.008)
for y in [-.23,-.15,-.075,0,.075,.15,.23]:box('Grille slat',(1.341,y,.71),(.014,.015,.18),chrome,.002)
for side in [-1,1]:
 box('Headlight lens',(1.33,side*.36,.76),(.024,.22,.18),light,.013)
 box('Turn indicator',(1.35,side*.36,.595),(.025,.19,.055),gold,.008)
 box('Tail lamp',(-1.365,side*.4,.78),(.026,.09,.23),red,.009)
truck=finish_asset('TRUCK',before)

# LOG: irregular radial bark surface, longitudinal ridges and concentric end grain.
before=set(bpy.context.scene.objects)
verts=[];faces=[];segments=28;rings=9
for i in range(rings):
 x=-1.55+i*3.1/(rings-1)
 for j in range(segments):
  a=j*math.tau/segments;r=.34+random.uniform(-.04,.04);verts.append((x,r*math.cos(a),.08+r*math.sin(a)))
for i in range(rings-1):
 for j in range(segments):a=i*segments+j;b=i*segments+(j+1)%segments;faces.append((a,b,b+segments,a+segments))
faces.extend([tuple(range(segments-1,-1,-1)),tuple(range((rings-1)*segments,rings*segments))]);mesh('Irregular cypress cylinder',verts,faces,bark)
for j in range(18):
 a=j*math.tau/18;tube('Lengthwise bark ridge',[(x,(.349+math.sin(x*8+j)*.012)*math.cos(a),.08+(.349+math.sin(x*8+j)*.012)*math.sin(a)) for x in [-1.5+k*.3 for k in range(11)]],.019,ridge if j%3 else moss,1)
for side in [-1,1]:
 cyl('Cut end',(side*1.553,0,.08),.295,.009,endgrain,'x',28)
 for r in [.08,.145,.205,.266]:tube('Growth ring',[(side*1.56,r*math.cos(a),.08+r*math.sin(a)) for a in [j*math.tau/28 for j in range(29)]],.005,bark,1)
 for a in [0,1.9,3.8]:tube('End split',[(side*1.57,.1*math.cos(a),.08+.1*math.sin(a)),(side*1.57,.29*math.cos(a+.1),.08+.29*math.sin(a+.1))],.007,bark,1)
for x,y in [(-.6,.05),(.2,-.12),(.85,.02)]:sphere('Moss cushion',(x,y,.393),(.26,.15,.035),moss,12,6)
capsule('Broken branch',(.65,.08,.32),(.83,.1,.63),.075,bark)
log=finish_asset('LOG',before)

# TURTLE: flattened lower shell, domed back with geometric scute network, four feet.
before=set(bpy.context.scene.objects)
sphere('Broad turtle carapace',(0,0,.08),(.43,.39,.21),shell,24,12)
sphere('Shell lip',(0,0,.04),(.445,.405,.055),scute,24,8)
# Curved surface panels, with darker gaps between individually modeled scutes.
for row in range(-2,3):
 for col in range(-2,3):
  x=col*.145+(row%2)*.07;y=row*.145
  if (x/.38)**2+(y/.34)**2>.85:continue
  pts=[]
  for k in range(6):
   a=k*math.tau/6;xx=x+.095*math.cos(a);yy=y+.085*math.sin(a);zz=.09+.208*math.sqrt(max(.02,1-(xx/.435)**2-(yy/.395)**2));pts.append((xx,yy,zz))
  mesh('Raised hexagonal shell scute',pts,[tuple(range(6))],shell);tube('Scute ridge',pts+[pts[0]],.007,scute,1)
capsule('Extended turtle neck',(0,.29,.045),(0,.52,.08),.088,skin)
sphere('Turtle head',(0,.54,.10),(.115,.15,.092),skin,16,10)
for side in [-1,1]:
 sphere('Turtle black eye',(side*.098,.59,.133),(.017,.016,.019),black,10,6)
 for y in [-.21,.20]:
  capsule('Turtle leg',(side*.29,y,.035),(side*.49,y+.055,-.015),.065,skin)
  for k in range(3):capsule('Turtle toe',(side*.48,y+.05,-.018),(side*(.54+k*.014),y+.018+k*.035,-.026),.013,scute)
capsule('Small turtle tail',(0,-.35,.02),(0,-.53,-.008),.035,skin)
turtle=finish_asset('TURTLE',before)
assets={'frog':frog,'truck':truck,'log':log,'turtle':turtle}
asset_stats={k:{'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':len(o.data.materials)} for k,o in assets.items()}
# Separate native asset source library; preserve all genuine meshes.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'meshes/bayou-assets.blend'))

# Environment supports exactly the approved row layout and arrival reserve.
env_before=set(bpy.context.scene.objects)
layout=json.loads((OUT/'room-layout.json').read_text())
for s in layout['surfaces']:
 p=s['center'];d=s['dimensions'];box(s['id'],(p[0],-p[2],p[1]),(d[0],d[2],d[1]),ground,.1)
box('Five-lane road',(0,3.9,.005),(15,6.5,.09),asphalt,.01)
box('Moonlit river surface',(0,11.7,-.035),(15,6.5,.10),water,.01)
for row in [0,6,12]:box('Grassy safe bank '+str(row),(0,row*1.3,.045),(15,1.23,.17),moss,.09)
for row in range(1,6):
 for x in range(-7,8,2):box('Dashed lane divider',(x,row*1.3-.62,.058),(.73,.025,.005),stripe,0)
for y in [.63,7.17]:
 for yy in [y-.05,y+.05]:box('Road edge marking',(0,yy,.058),(15,.024,.005),stripe,0)
for x in [-7.8,7.8]:
 for y in [1.3,5.2]:
  cyl('Streetlight post',(x,y,1.8),.047,3.6,metal,vertices=12)
  sign=1 if x<0 else -1;tube('Curved light arm',[(x,y,3.5),(x+sign*.4,y,3.7),(x+sign*.95,y,3.6)],.035,metal,1)
  box('Streetlight housing',(x+sign*1.05,y,3.55),(.4,.28,.10),metal,.03)
  box('Streetlight diffuser',(x+sign*1.05,y,3.49),(.32,.21,.016),light,.005)
# Lily pads: five visible goal landmarks, modeled petals and warm lamp center.
for index,x in enumerate([-5.2,-2.6,0,2.6,5.2]):
 pts=[(x,15.6,.19)]+[(x+.61*math.cos(a),15.6+.55*math.sin(a),.19+.018*math.cos(3*a)) for a in [j*math.tau/24 for j in range(23)]]
 pad=mesh('HOME_PAD_'+str(index),pts,[(0,j,j+1) for j in range(1,23)],leaflight)
 for a in [k*math.tau/8 for k in range(8)]:tube('Lily vein',[(x,15.6,.203),(x+.49*math.cos(a),15.6+.45*math.sin(a),.211)],.006,moss,1)
 for k in range(9):
  a=k*math.tau/9;o=sphere('Lotus petal',(x+math.cos(a)*.16,15.75+math.sin(a)*.16,.29),(.10,.20,.037),petal,10,6);o.rotation_euler.z=a-math.pi/2;o.rotation_euler.x=.22
 sphere('Glowing lotus heart',(x,15.75,.29),(.10,.10,.06),light,12,8)
# Banks with deliberate vegetation envelopes, never inside a landing lane.
for side in [-1,1]:
 for i in range(20):
  x=side*random.uniform(8.3,10.5);y=random.uniform(-3,19)
  sphere('Bank moss rock',(x,y,random.uniform(-.03,.12)),(random.uniform(.22,.65),random.uniform(.25,.65),random.uniform(.18,.38)),moss if i%2 else ground,10,6)
 for i in range(45):
  x=side*random.uniform(7.9,10.8);y=random.uniform(-2,19);height=random.uniform(.2,.65)
  for a in [0,2.2,4.3]:
   tip=(x+math.cos(a)*.16,y+math.sin(a)*.16,height);mesh('Reed blade',[(x-.013,y,0),(x+.013,y,0),tip],[(0,1,2)],leaflight if i%3==0 else leaf)
  if i%3==0:
   tube('Cattail stem',[(x,y,0),(x+.05,y,height+.22)],.009,leaf,0);cyl('Cattail seed head',(x+.05,y,height+.21),.027,.16,bark,vertices=8)
 # Cypress trunks form a peripheral canopy; sculpted flared roots visibly meet soil.
 for i in range(6):
  x=side*(8.8+(i%2)*1.2);y=-1+i*3.8;height=5+random.random()*2
  tube('Tapered cypress trunk',[(x,y,0),(x+.12,y+.07,height*.45),(x-.17,y+.1,height)],.18,bark,2)
  for a in [j*math.tau/5 for j in range(5)]:
   mesh('Cypress buttress root',[(x+math.cos(a)*.8,y+math.sin(a)*.8,0),(x+math.cos(a+.3)*.18,y+math.sin(a+.3)*.18,0),(x,y,1.35)],[(0,1,2)],bark)
  for j in range(3):
   a=j*2.1+i;end=(x+math.cos(a)*1.25,y+math.sin(a)*1.25,height-.7)
   capsule('Canopy branch',(x,y,height-1.8),end,.07,bark)
   sphere('Cypress foliage crown',end,(1.25,1.1,.52),leaf,12,8)
   for k in range(3):
    xx=end[0]+random.uniform(-.7,.7);yy=end[1]+random.uniform(-.7,.7)
    tube('Hanging Spanish moss',[(xx,yy,end[2]-.1),(xx+.08,yy+.06,end[2]-.6),(xx-.02,yy+.08,end[2]-1.2)],.021,moss,1)
# Arrival lanterns and restrained road reflectors.
for x in [-1.4,1.4]:
 cyl('Arrival lantern base',(x,-1.4,.15),.14,.24,metal)
 box('Arrival lantern glass',(x,-1.4,.42),(.18,.18,.29),light,.03)
 for dx in [-.11,.11]:
  for dy in [-.11,.11]:cyl('Lantern upright',(x+dx,-1.4+dy,.42),.011,.34,metal,vertices=8)
 box('Lantern cap',(x,-1.4,.60),(.30,.30,.08),metal,.035)
# Use generated concept as explicitly credited far scenic backdrop in Blender source; runtime uses it only on cabinet.
environment_objects=[o for o in bpy.context.scene.objects if o not in env_before]
for o in environment_objects:o['asset_group']='environment'
# Approved instance positions read from manifest, not a separate hand-authored layout.
instances=[]
for inst in layout['instances']:
 a=assets[inst['assetId']];o=a.copy();o.data=a.data;bpy.context.collection.objects.link(o);o.name=inst['id'];o.hide_render=False;o.hide_set(False)
 p=inst['position'];o.location=(p[0],-p[2],p[1]);o['layout_id']=inst['id'];o['asset_group']='dynamic';instances.append(o)
# Review lighting is an explicit fixture manifest; runtime will consume its converted positions.
fixtures=[{'name':'Moon key','type':'AREA','position':[1,8,11],'target':[0,8,0],'color':[.56,.68,1.0],'power':2200,'size':10},
 {'name':'Warm arrival fill','type':'AREA','position':[-3,-3,6],'target':[0,3,0],'color':[1,.65,.29],'power':1100,'size':7},
 {'name':'River rim','type':'AREA','position':[-5,17,6],'target':[0,11,0],'color':[.41,.8,.78],'power':1500,'size':7}]
for f in fixtures:
 d=bpy.data.lights.new(f['name'],f['type']);d.energy=f['power'];d.color=f['color'];d.shape='DISK';d.size=f['size'];o=bpy.data.objects.new(f['name'],d);bpy.context.collection.objects.link(o);o.location=f['position'];o.rotation_euler=(Vector(f['target'])-o.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.14,.20,.31,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.4
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1400;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='Production desktop follow camera';scene.camera=camera;camera.data.lens=30
# Pull back enough to review whole layout, plus actual near-start production view.
def render(name,position,target,lens=30,width=1400,height=950):
 camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens;scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
json.dump({'assets':asset_stats,'instances':len(instances),'environmentObjects':len(environment_objects),'source':'model_bayou.py','referenceApproval':'explicit user approval in conversation','exported':False},open(OUT/'meshes/model-provenance.json','w'),indent=2)
json.dump(fixtures,open(OUT/'lighting-fixtures.json','w'),indent=2)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'meshes/bayou-world.blend'))
render('world-overview.png',(17,-15,18),(0,7.2,0),38)
render('production-view.png',(0,-5,6),(0,6,0),28,1400,850)
# Four wide corner views and overhead coverage for the room skill's review suite.
for i,(p,t) in enumerate([((-10,-4,2),(0,8,1)),((10,-4,2),(0,8,1)),((-10,20,2),(0,8,1)),((10,20,2),(0,8,1))]):render('corner-'+str(i+1)+'.png',p,t,10,1000,700)
render('center-up.png',(0,7,.5),(0,7,20),10,1000,700)
render('overhead-forward.png',(0,-2,1),(0,9,5),14,1000,700)
render('overhead-back.png',(0,18,1),(0,6,5),14,1000,700)
print('BAYOU_MODELS_AND_FORM_RENDERS_COMPLETE',flush=True)
