import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {CELL,LANES,laneObjects,HOME_COLUMNS} from './engine.js';

function combine(root){
 root.updateMatrixWorld(true);const bins=new Map();
 root.traverse(o=>{if(!o.isMesh)return;const key=o.material.uuid;
  if(!bins.has(key))bins.set(key,{material:o.material,geometries:[]});
  const g=o.geometry.clone().applyMatrix4(o.matrixWorld);
  if(!g.attributes.uv)g.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(g.attributes.position.count*2),2));
  bins.get(key).geometries.push(g);
 });
 const group=new THREE.Group();
 for(const bin of bins.values()){
  const geometry=mergeGeometries(bin.geometries,false);if(!geometry)throw Error('Bayou geometry could not be combined');
  bin.geometries.forEach(g=>g.dispose());const m=new THREE.Mesh(geometry,bin.material);m.castShadow=true;m.receiveShadow=true;group.add(m);
 }
 return group;
}
function batch(group,capacity,parent){
 const meshes=[];group.traverse(o=>{if(!o.isMesh)return;const m=new THREE.InstancedMesh(o.geometry,o.material,capacity);m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);m.frustumCulled=false;m.castShadow=true;m.receiveShadow=true;parent.add(m);meshes.push(m)});
 const dummy=new THREE.Object3D();return {set(items){for(const m of meshes){m.count=items.length;for(let i=0;i<items.length;i++){const p=items[i];dummy.position.set(p.x,p.y,p.z);dummy.rotation.set(0,p.rotation||0,0);dummy.scale.set(p.sx||1,p.sy||1,p.sz||1);dummy.updateMatrix();m.setMatrixAt(i,dummy.matrix)}m.instanceMatrix.needsUpdate=true}}};
}
export class BayouView{
 constructor(){this.root=new THREE.Group();this.root.visible=false;this.loaded=false;this.facing=0;this.movers={};this.report=[];this.waterTime={value:0};}
 async load({low=matchMedia('(pointer:coarse)').matches}={}){
  const loader=new GLTFLoader();
  const fetchModel=async name=>{const path=`/assets/bayou/${name}${low?'-vlow':''}.glb`;const g=await loader.loadAsync(path);let triangles=0,meshes=0;g.scene.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3}});this.report.push({path,meshes,triangles});return combine(g.scene)};
  const [world,frog,truck,log,turtle]=await Promise.all(['world','frog','truck','log','turtle'].map(fetchModel));
  world.traverse(o=>{if(!o.isMesh)return;const m=o.material;
   if(m.name==='Generated distant bayou panorama'){o.material=new THREE.MeshBasicMaterial({map:m.map,color:0xaab6c0,fog:false,side:THREE.DoubleSide});o.castShadow=false;}
   else if(m.name==='Moonlit river'){
    m.onBeforeCompile=shader=>{shader.uniforms.bayouTime=this.waterTime;
     shader.vertexShader='varying vec3 vBayouPos;\n'+shader.vertexShader;
     shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvBayouPos = position;');
     shader.fragmentShader='uniform float bayouTime; varying vec3 vBayouPos;\n'+shader.fragmentShader;
     shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>','#include <normal_fragment_maps>\nnormal = normalize(normal + vec3(sin(vBayouPos.x*2.0+vBayouPos.z*11.0+bayouTime*.7)*0.022, cos(vBayouPos.z*17.0+sin(vBayouPos.x)-bayouTime)*0.008,0.0));');
    };m.customProgramCacheKey=()=> 'bayou-water-v1';m.roughness=.3;m.metalness=.15;
   }
   m.envMapIntensity=m.name==='Moonlit river'?.03:m.name==='Wet asphalt'?.12:.45;
  });
  this.root.add(world,frog);this.frog=frog;
  this.movers.truck=batch(truck,45,this.root);this.movers.log=batch(log,27,this.root);this.movers.turtle=batch(turtle,54,this.root);
  const hemi=new THREE.HemisphereLight(0x9daecb,0x25361b,1.1);this.root.add(hemi);
  const response=await fetch('/assets/bayou/lighting.json');if(!response.ok)throw Error('Bayou lighting did not load');const lighting=await response.json();
  for(const fixture of lighting.fixtures){const f=fixture.runtime;const light=f.type==='directional'?new THREE.DirectionalLight(f.colorHex,f.intensity):new THREE.PointLight(f.colorHex,f.intensity,f.distance,2);const [x,y,z]=fixture.position;light.position.set(x,z,-y);this.root.add(light);
   if(f.type==='directional'){const [tx,ty,tz]=fixture.target;light.target.position.set(tx,tz,-ty);light.castShadow=true;light.shadow.mapSize.set(1024,1024);light.shadow.camera.left=-10;light.shadow.camera.right=10;light.shadow.camera.top=12;light.shadow.camera.bottom=-12;light.shadow.bias=-.0006;this.root.add(light.target)}
  }
  this.homes=HOME_COLUMNS.map((x,i)=>{
   const marker=new THREE.Mesh(new THREE.TorusGeometry(.44,.022,6,32),new THREE.MeshBasicMaterial({color:0xe7d6a2,transparent:true,opacity:.4}));marker.rotation.x=Math.PI/2;marker.position.set(x*CELL,.24,-12*CELL);this.root.add(marker);return marker;
  });
  // A persistent world-space HUD is visible inside a headset.
  const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=256;this.labelContext=canvas.getContext('2d');this.labelTexture=new THREE.CanvasTexture(canvas);this.labelTexture.colorSpace=THREE.SRGBColorSpace;
  this.label=new THREE.Mesh(new THREE.PlaneGeometry(4,.9),new THREE.MeshBasicMaterial({map:this.labelTexture,transparent:true,depthWrite:false,side:THREE.DoubleSide}));this.root.add(this.label);
  this.loaded=true;return this.report;
 }
 sceneTriangles(){let total=0;this.root.traverseVisible(o=>{if(o.isMesh)total+=((o.geometry.index?.count||o.geometry.attributes.position.count)/3)*(o.isInstancedMesh?o.count:1)});return total;}
 labelText(text){if(text===this.lastText)return;this.lastText=text;const c=this.labelContext;c.clearRect(0,0,1024,256);c.fillStyle='#071c15dd';c.fillRect(0,0,1024,256);c.fillStyle='#e8efd6';c.textAlign='center';c.font='500 35px sans-serif';text.split('\n').forEach((line,i)=>c.fillText(line,512,65+i*64));this.labelTexture.needsUpdate=true;}
 hop(dx,dy){this.facing=Math.atan2(-dx,dy);}
 update(game,dt,{firstPerson=false,xr=false}={}){
  if(!this.loaded)return;
  const p=game.visualFrog;const road=1<=p.row&&p.row<=5;const river=p.row>=7&&p.row<12;
  this.frog.position.set(p.x,(river?.42:road?.06:.135)+p.height,-p.row*CELL);
  this.frog.rotation.y=THREE.MathUtils.lerp(this.frog.rotation.y,this.facing,Math.min(1,dt*14));
  this.frog.visible=!firstPerson&&game.recovery<=0;
  this.waterTime.value=game.time;
  const trucks=[],logs=[],turtles=[];
  for(const lane of LANES){for(const obj of laneObjects(lane,game.time,game.round)){
   if(Math.abs(obj.x)>8.8)continue;
   if(lane.type==='road')trucks.push({x:obj.x,y:.025,z:-lane.row*CELL,sx:obj.length/2.92,sz:.82,rotation:lane.speed<0?Math.PI:0});
   else if(lane.type==='log')logs.push({x:obj.x,y:0,z:-lane.row*CELL,sx:obj.length/3.1});
   else for(let j=-1;j<=1;j++)turtles.push({x:obj.x+j*obj.length*.30,y:obj.submerged?-.48:obj.warning?Math.sin(game.time*13)*.035:0,z:-lane.row*CELL,sx:obj.length/3,sz:.85});
  }}
  this.movers.truck.set(trucks);this.movers.log.set(logs);this.movers.turtle.set(turtles);
  for(let i=0;i<this.homes.length;i++){const m=this.homes[i];m.material.color.set(game.homes.includes(i)?0x9bf071:0xe7d6a2);m.material.opacity=game.homes.includes(i)?.95:.4;}
  this.label.visible=xr;
  this.label.position.set(p.x,1.8,-p.row*CELL-4);
  const status=game.finished?(game.won?'ALL HOMES REACHED · TRIGGER TO REPLAY':'RUN COMPLETE · TRIGGER TO REPLAY'):game.paused?'PAUSED · TRIGGER TO RESUME':!game.started?'TRIGGER TO START · STICK TO HOP':game.roundDelay>0?'ALL FIVE HOME · NEXT ROUND':`STICK TO HOP · ${Math.ceil(game.timer)} SECONDS`;
  this.labelText(`BAYOU CROSSING · ROUND ${game.round+1}/3\n${game.score} POINTS · ${game.lives} LIVES · ${game.homes.length}/5 HOMES\n${status}`);
 }
}
