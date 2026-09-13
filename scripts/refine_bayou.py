"""Material and foliage refinement, native source and Form review only."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent.parent;OUT=BASE/'design/bayou-crossing';random.seed(90)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'meshes/bayou-world.blend'))
scene=bpy.context.scene
# Detailed generated ground albedo bound to the native Blender UV layer for eventual GLB export.
im=bpy.data.images.load(str(OUT/'images/bayou-ground.png'));im.pack()
for name in ['Earth substrate','Soft moss']:
 m=bpy.data.materials[name];p=m.node_tree.nodes.get('Principled BSDF');n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
for o in scene.objects:
 if o.type=='MESH' and any(m and m.name in ['Earth substrate','Soft moss'] for m in o.data.materials):
  if not o.data.uv_layers:o.data.uv_layers.new()
  # World aligned meter-scale UVs to avoid stretched soil on wide banks.
  for poly in o.data.polygons:
   for li in poly.loop_indices:
    p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(p.x/2,p.y/2)
# Replace low-information crown ellipsoids with thousands of individually folded leaf silhouettes.
leaves=[]
for o in list(scene.objects):
 if not o.name.startswith('Cypress foliage crown'):continue
 center=o.location.copy();bpy.data.objects.remove(o,do_unlink=True)
 vs=[];fs=[]
 for i in range(160):
  a=random.random()*math.tau;r=math.sqrt(random.random())*1.3;p=center+Vector((math.cos(a)*r,math.sin(a)*r,random.uniform(-.30,.35)))
  angle=random.random()*math.tau;length=random.uniform(.08,.22);width=length*.32
  dx=Vector((math.cos(angle),math.sin(angle),random.uniform(-.2,.2)))*length;dy=Vector((-math.sin(angle),math.cos(angle),0))*width
  n=len(vs);vs.extend([tuple(p-dx),tuple(p-dy),tuple(p+Vector((0,0,.024))),tuple(p+dy),tuple(p+dx)]);fs.extend([(n,n+1,n+2),(n,n+2,n+3),(n+1,n+4,n+2),(n+2,n+4,n+3)])
 me=bpy.data.meshes.new('Folded leaf clusters');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['Bayou foliage']);me.materials.append(bpy.data.materials['Silver green leaves'])
 for f in me.polygons:f.material_index=1 if random.random()<.2 else 0
 n=bpy.data.objects.new('Cypress individual leaf canopy',me);scene.collection.objects.link(n);n['asset_group']='environment'
# Panoramic distant woodland on a modeled curved cyclorama. Real scene remains in front.
m=bpy.data.materials.new('Generated distant bayou panorama');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'images/bayou-backdrop.png'));tex.image.pack();m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.6;p.inputs['Roughness'].default_value=1
verts=[];faces=[];uv=[]
for i in range(33):
 a=-1.05+i*2.1/32;x=math.sin(a)*33;y=math.cos(a)*33+1
 for z in [-4,20]:verts.append((x,y,z));uv.append((i/32,0 if z==-4 else 1))
for i in range(32):faces.append((i*2,i*2+2,i*2+3,i*2+1))
me=bpy.data.meshes.new('Curved distant woodland');me.from_pydata(verts,[],faces);me.uv_layers.new()
for poly in me.polygons:
 for li in poly.loop_indices:me.uv_layers.active.data[li].uv=uv[me.loops[li].vertex_index]
o=bpy.data.objects.new('Distant bayou cyclorama',me);scene.collection.objects.link(o);me.materials.append(m);o['asset_group']='environment';o['background_exception']='Distant atmosphere outside terrain play bounds; no collision'
# Soften overly bright water and preserve a clear nighttime palette.
p=bpy.data.materials['Moonlit river'].node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.012,.045,.056,1);p.inputs['Metallic'].default_value=.6;p.inputs['Roughness'].default_value=.22
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.23
for o in scene.objects:
 if o.type=='LIGHT':o.data.energy*=.72
# Lily petals remain lit landmarks. Micro fireflies are physical emissive points in source.
glow=bpy.data.materials['Warm headlamp']
for i in range(65):
 x=random.choice([-1,1])*random.uniform(6.3,9.5);y=random.uniform(-2,18);z=random.uniform(.25,2)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.013,location=(x,y,z));o=bpy.context.object;o.name='Warm bank firefly';o.data.materials.append(glow);o['asset_group']='environment'
# Save refined native source. Renders use actual meshes and packed artwork.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'meshes/bayou-world.blend'))
cam=scene.camera;scene.cycles.samples=32

def render(name,p,t,lens=30,w=1400,h=900):
 cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
render('world-overview.png',(17,-15,18),(0,7.2,0),38)
render('production-view.png',(0,-6.4,7.8),(0,4.6,0),29,1400,850)
render('frog-eye.png',(0,-.12,.8),(0,5,.8),22,1400,850)
for i,(p,t) in enumerate([((-10,-4,2),(0,8,1)),((10,-4,2),(0,8,1)),((-10,20,2),(0,8,1)),((10,20,2),(0,8,1))]):render('corner-'+str(i+1)+'.png',p,t,10,1000,700)
render('center-up.png',(0,7,.5),(0,7,20),10,1000,700)
render('overhead-forward.png',(0,-2,1),(0,9,5),14,1000,700)
render('overhead-back.png',(0,18,1),(0,6,5),14,1000,700)
print('BAYOU_REFINED_RENDERS_COMPLETE',flush=True)
