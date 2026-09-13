"""Export reviewed Blender models only after explicit Form approval is recorded."""
import bpy,json,hashlib,os
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent;DESIGN=BASE/'design/bayou-crossing';OUT=BASE/'public/assets/bayou'
review=json.loads((DESIGN/'milestone-reviews.json').read_text())
if review['form']['status']!='approved' or not review['form']['approvedBy']:raise RuntimeError('Explicit Form approval required before export')
OUT.mkdir(parents=True,exist_ok=True)
report=[]
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.hide_render=False;o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 path=OUT/(name+'.glb');dg=bpy.context.evaluated_depsgraph_get();tri=0
 for o in objects:
  if o.type not in ['MESH','CURVE','FONT']:continue
  evaluated=o.evaluated_get(dg);me=evaluated.to_mesh();tri+=sum(len(p.vertices)-2 for p in me.polygons);evaluated.to_mesh_clear()
 report.append({'path':str(path.relative_to(BASE)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':tri})
# Bake Blender's procedural micro-normal detail onto each asset's own UV atlas.
for name in ['frog','truck','log','turtle']:
 bpy.ops.wm.open_mainfile(filepath=str(DESIGN/'meshes/bayou-assets.blend'))
 o=bpy.data.objects[name.upper()];o.hide_set(False);o.hide_render=False
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 image=bpy.data.images.new(name+' baked micro-normal',width=1024,height=1024,alpha=False);image.colorspace_settings.name='Non-Color'
 for slot in o.material_slots:
  m=slot.material.copy();slot.material=m;n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;m.node_tree.nodes.active=n
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=4;scene.render.bake.use_selected_to_active=False;scene.render.bake.margin=8
 bpy.ops.object.bake(type='NORMAL')
 image.filepath_raw=str(OUT/(name+'-normal.png'));image.file_format='PNG';image.save();image.pack()
 for m in o.data.materials:
  p=m.node_tree.nodes.get('Principled BSDF');n=m.node_tree.nodes.new('ShaderNodeNormalMap');t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
 # The full tier is preserved for close inspection; reduced meshes are used in gameplay.
 export(name+'-high',[o])
 dec=o.modifiers.new('Runtime detail reduction','DECIMATE');dec.ratio=.5
 export(name,[o])
 dec.ratio=.25;export(name+'-vlow',[o])
# Separate static room geometry from simulated movable props.
bpy.ops.wm.open_mainfile(filepath=str(DESIGN/'meshes/bayou-world.blend'))
objects=[o for o in bpy.context.scene.objects if o.get('asset_group')=='environment']
export('world',objects)
for o in objects:
 if o.type=='MESH' and len(o.data.polygons)>50:
  dec=o.modifiers.new('VR reduced detail','DECIMATE');dec.ratio=.55
export('world-vlow',objects)
bpy.ops.wm.open_mainfile(filepath=str(DESIGN/'meshes/bayou-cabinet.blend'))
export('cabinet',[o for o in bpy.context.scene.objects if o.type=='MESH'])
(DESIGN/'runtime/asset-manifest.json').write_text(json.dumps({'source':'Native Blender assets and environment','formApproval':review['form'],'assets':report,'normals':'Procedural surface details baked by Blender into 1024px normal atlases','lighting':'lighting-fixtures.json; WebXR approximation requires browser verification'},indent=2)+'\n')
print('BAYOU_APPROVED_EXPORT_COMPLETE',flush=True)
