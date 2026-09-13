import bpy,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent;D=BASE/'design/bayou-crossing';P=BASE/'public/assets/bayou'
review=json.loads((D/'milestone-reviews.json').read_text());assert review['form']['status']=='approved'
manifest=json.loads((D/'runtime/asset-manifest.json').read_text())
for name in ['world','frog','truck','log','turtle']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for im in list(bpy.data.images):
  if im.users==0:bpy.data.images.remove(im)
 path=P/(name+'-vlow.glb');bpy.ops.import_scene.gltf(filepath=str(path))
 for im in bpy.data.images:
  if im.source!='FILE' or not im.size[0]:continue
  limit=1024 if name=='world' else 512
  if max(im.size)>limit:
   ratio=limit/max(im.size);im.scale(max(1,int(im.size[0]*ratio)),max(1,int(im.size[1]*ratio)));im.pack()
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_yup=True,export_apply=True)
 for item in manifest['assets']:
  if item['path'].endswith(name+'-vlow.glb'):item['bytes']=path.stat().st_size;item['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
manifest['lowTextureTier']='1024px maximum environment textures; 512px normal atlases; UV layout retained'
(D/'runtime/asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('BAYOU_LOW_TEXTURES_COMPLETE')
