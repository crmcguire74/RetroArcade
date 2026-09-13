import bpy,json,bmesh,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent.parent;OUT=BASE/'design/bayou-crossing'
for source in ['bayou-assets','bayou-world']:
 bpy.ops.wm.open_mainfile(filepath=str(OUT/'meshes'/(source+'.blend')))
 truck=bpy.data.objects.get('TRUCK');me=truck.data;glass={i for i,m in enumerate(me.materials) if m.name=='Blue smoked glass'};ids=set()
 for f in me.polygons:
  if f.material_index in glass:
   pts=[truck.matrix_world@me.vertices[i].co for i in f.vertices]
   if all(p.x>.15 for p in pts):ids.update(f.vertices)
 for i in ids:
  p=truck.matrix_world@me.vertices[i].co;p.x+=.035;me.vertices[i].co=truck.matrix_world.inverted()@p
 for name in ['Frog jade wet skin','Turtle damp skin','Turtle olive shell']:
  for n in bpy.data.materials[name].node_tree.nodes:
   if n.type=='BUMP':n.inputs['Distance'].default_value=.006;n.inputs['Strength'].default_value=.18
 if source=='bayou-world':
  bpy.data.objects['frog-player'].location.z=.135
  for o in bpy.context.scene.objects:
   if o.get('layout_id','').startswith('truck-'):o.location.z=.025
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'meshes'/(source+'.blend')))
 if source=='bayou-world':
  scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();layout=json.loads((OUT/'room-layout.json').read_text());checks={};errors=[]
  for inst in layout['instances']:
   o=scene.objects.get(inst['id']);p=inst['position'];ok=o is not None and abs(o.location.x-p[0])<.001 and abs(o.location.y+p[2])<.001;checks[inst['id']]=ok
   if not ok:errors.append('Layout mismatch '+inst['id'])
  shell={}
  for name in ['terrain','left-berm','right-berm','Five-lane road','Moonlit river surface']:
   o=scene.objects[name];evaluated=o.evaluated_get(dg);me=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(me);shell[name]={'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'dimensions':list(o.dimensions)};bm.free();evaluated.to_mesh_clear()
   if shell[name]['nonManifoldEdges']:errors.append('Nonmanifold substrate '+name)
  bounds={}
  for name in ['FROG','TRUCK','LOG','TURTLE']:
   o=scene.objects[name];pts=[o.matrix_world@Vector(c) for c in o.bound_box];bounds[name]=[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)]
  report={'layoutParity':checks,'substrate':shell,'assetDimensionsBlenderXYZ':bounds,'errors':errors,'exceptions':['Open air: no roof, doors, windows, columns or seating. Associated checks are not applicable.','Foliage blades, petals and eye highlights intentionally use thin decorative surfaces; closed manifold requirement applies to the terrain substrate.','Distant image cyclorama intentionally outside playable terrain bounds.','Frog and vehicle instance heights adjusted to ground their contact surfaces.','Blender-only production approved by user; no accepted Meshy task receipts exist.'],'humanFormApproval':'pending','nativeSource':'meshes/bayou-world.blend','proceduralNormalDetail':'Blender procedural micro-normal shading must be baked or recreated for runtime; it does not survive GLB automatically.'}
  (OUT/'form-geometry-audit.json').write_text(json.dumps(report,indent=2)+'\n')
  cam=scene.camera
  for name,p,t,lens in [('production-view.png',(0,-6.4,7.8),(0,4.6,0),29),('frog-eye.png',(0,-.12,.8),(0,5,.8),22)]:
   cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;scene.render.resolution_x=1400;scene.render.resolution_y=850;scene.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
print('BAYOU_FORM_AUDIT_COMPLETE',flush=True)
