import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {LANES,laneObjects} from '../src/games/bayou/engine.js';
const path='design/bayou-crossing/runtime/asset-manifest.json';const manifest=JSON.parse(await readFile(path,'utf8'));
for(const asset of manifest.assets){const b=await readFile(asset.path);if(b.length!==asset.bytes||createHash('sha256').update(b).digest('hex')!==asset.sha256)throw Error('Asset manifest mismatch: '+asset.path);if(b.toString('utf8',0,4)!=='glTF')throw Error('Invalid GLB: '+asset.path)}
const triangles=name=>manifest.assets.find(a=>a.path.endsWith('/'+name+'.glb')).triangles;
const base=triangles('world')+triangles('frog')+5*6*32*2+2;
let worst=0;
for(let round=0;round<3;round++)for(let t=0;t<120;t+=.1){let total=base;
 for(const lane of LANES)if(lane.speed){const count=laneObjects(lane,t,round).filter(o=>Math.abs(o.x)<=8.8).length;total+=count*(lane.type==='road'?triangles('truck'):lane.type==='log'?triangles('log'):3*triangles('turtle'))}worst=Math.max(worst,total);
}
const lowBytes=manifest.assets.filter(a=>a.path.includes('-vlow.glb')).reduce((sum,a)=>sum+a.bytes,0);
if(lowBytes>8_000_000)throw Error('Low-tier package exceeds budget');if(worst>250_000)throw Error('Visible scene exceeds polygon budget');
const report={verifiedGLBs:manifest.assets.length,hashes:'all match',lowTierBytes:lowBytes,worstSampledSceneTriangles:worst,triangleBudget:250000,sampling:'All 3 rounds; 120 seconds per round at 0.1-second intervals; includes visible instanced props and five home rings; excludes repeated shadow/postprocess draw work'};
await writeFile('design/bayou-crossing/runtime/asset-validation.json',JSON.stringify(report,null,2)+'\n');console.log(report);
