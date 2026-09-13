import './style.css';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {Brickstorm,LEVEL_NAMES} from './engine.js';
import {readSave} from './rules.js';
import {BayouCrossing,CELL} from './games/bayou/engine.js';
import {BayouView} from './games/bayou/view.js';
import {keyboardHop,StickHops} from './games/bayou/controls.js';
import {readBayouSave,recordBayouRun,SAVE_KEY} from './games/bayou/save.js';

const $ = s => document.querySelector(s);
const renderer = new THREE.WebGLRenderer({canvas:$('#world'),antialias:true,powerPreference:'high-performance'});
renderer.setSize(innerWidth,innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));
renderer.xr.enabled=true;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=.9;
const scene=new THREE.Scene();
scene.background=new THREE.Color('#080e16');
scene.fog=new THREE.Fog('#080e16',16,50);
const pmrem=new THREE.PMREMGenerator(renderer);
const environment=pmrem.fromScene(new RoomEnvironment(),.05);
scene.environment=environment.texture;scene.environmentIntensity=.35;
const camera=new THREE.PerspectiveCamera(52,innerWidth/innerHeight,.05,100);
const rig=new THREE.Group();rig.add(camera);scene.add(rig);
const comfortFade=new THREE.Mesh(new THREE.PlaneGeometry(2,2),new THREE.MeshBasicMaterial({color:0x020807,transparent:true,opacity:0,depthTest:false,depthWrite:false}));comfortFade.position.z=-.10;comfortFade.renderOrder=9999;comfortFade.visible=false;camera.add(comfortFade);
const arcade=new THREE.Group(),arena=new THREE.Group();scene.add(arcade,arena);arena.visible=false;
const bayouView=new BayouView();scene.add(bayouView.root);const bayouCabinet=new THREE.Group();bayouCabinet.position.set(2.3,0,-4.05);bayouCabinet.rotation.y=-.1;arcade.add(bayouCabinet);
scene.add(new THREE.HemisphereLight(0x9baec2,0x101820,.6));
function areaLight(parent,color,intensity,x,y,z){const l=new THREE.PointLight(color,intensity,14,2);l.position.set(x,y,z);parent.add(l);return l}
areaLight(arcade,0x78d4dd,35,0,2.6,0);
areaLight(arcade,0xffc184,45,-3,3.5,-1);
areaLight(arcade,0x94cadc,45,3,3,-2);
areaLight(arcade,0xf6b16a,50,0,3.8,-4.7);
areaLight(arena,0x85dfe5,75,0,4,-3);
areaLight(arena,0xffb774,70,-4,4,1);
areaLight(arena,0x697dbf,70,4,3,-6);
const spot=new THREE.SpotLight(0xb7e4ef,110,18,Math.PI/4,.65,1.5);
spot.position.set(2,5,2);spot.target.position.set(0,0,-3);spot.castShadow=true;spot.shadow.mapSize.set(1024,1024);spot.shadow.bias=-.0008;arcade.add(spot,spot.target);
const composer=new EffectComposer(renderer);
composer.addPass(new RenderPass(scene,camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),.12,.25,2.3));
composer.addPass(new OutputPass());
const textureLoader=new THREE.TextureLoader();

// The generated nebula is embedded on a Blender-modeled cyclorama inside arena-premium.glb.
// Actual Blender GLBs: retain material identity including the embedded artwork textures.

// Crisp animated CRT attract screens; generated illustrations remain on cabinet sides and wall art.
const crtCanvas=document.createElement('canvas');crtCanvas.width=512;crtCanvas.height=384;
const crtContext=crtCanvas.getContext('2d');const crtTexture=new THREE.CanvasTexture(crtCanvas);crtTexture.colorSpace=THREE.SRGBColorSpace;crtTexture.flipY=false;
const crtMaterial=new THREE.MeshBasicMaterial({map:crtTexture,color:0xc2f4ec});
function drawCRT(time){const c=crtContext;c.fillStyle='#02161e';c.fillRect(0,0,512,384);c.textAlign='center';c.fillStyle='#e4c27e';c.font='bold 34px monospace';c.fillText('BRICKSTORM',256,49);for(let r=0;r<4;r++)for(let j=0;j<9;j++){c.fillStyle=['#57b3aa','#627ebe','#b06ba7','#d6a46b'][r];c.fillRect(59+j*44,85+r*26,37,17)}const x=256+Math.sin(time)*150;c.fillStyle='#89dbd3';c.fillRect(x-35,285,70,8);c.fillStyle='#ffedb8';c.fillRect(256+Math.sin(time*1.4)*160,205+Math.cos(time*1.1)*58,7,7);c.font='14px monospace';c.fillStyle='#abbfae';c.fillText('PRESS START  /  1 PLAYER',256,351);c.fillStyle='#0002';for(let y=0;y<384;y+=3)c.fillRect(0,y,512,1);crtTexture.needsUpdate=true;}
drawCRT(0);
const terrazzoCanvas=document.createElement('canvas');terrazzoCanvas.width=512;terrazzoCanvas.height=512;const tc=terrazzoCanvas.getContext('2d');tc.fillStyle='#24383c';tc.fillRect(0,0,512,512);let seed=1987;function rnd(){seed=(seed*1664525+1013904223)>>>0;return seed/4294967296}for(let i=0;i<16000;i++){const v=rnd();tc.fillStyle=v<.1?'#797462':v<.45?'#3b4b4b':'#1a2d32';tc.fillRect(rnd()*512,rnd()*512,.7+rnd()*2,.7+rnd()*2)}const terrazzoTexture=new THREE.CanvasTexture(terrazzoCanvas);terrazzoTexture.colorSpace=THREE.SRGBColorSpace;terrazzoTexture.wrapS=terrazzoTexture.wrapT=THREE.RepeatWrapping;terrazzoTexture.repeat.set(8,8);

const loader=new GLTFLoader();
let ready=false,brickAsset=null;
const assetReport=[];
async function loadModel(path,parent){
 const gltf=await loader.loadAsync(path);gltf.scene.updateMatrixWorld(true);
 const bins=new Map();let meshes=0,triangles=0;
 gltf.scene.traverse(o=>{if(o.isMesh){let ancestor=o.parent;while(ancestor){if(path.includes('arcade-premium')&&ancestor.name.startsWith('VECTOR'))return;ancestor=ancestor.parent;}if(/Nebula.*cyclorama/.test(o.name))o.material=new THREE.MeshBasicMaterial({map:o.material.map,color:0xb4bccc,fog:false});if(!path.includes('/bayou/')&&/Convex.*CRT/.test(o.name))o.material=crtMaterial;if(o.material.name==='Deep teal terrazzo'){o.material.map=terrazzoTexture;o.material.color.set(0x7c9696);o.material.roughness=.42;}meshes++;triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;const key=o.material.uuid;if(!bins.has(key))bins.set(key,{material:o.material,geometries:[]});const g=o.geometry.clone().applyMatrix4(o.matrixWorld);if(!g.attributes.uv)g.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(g.attributes.position.count*2),2));bins.get(key).geometries.push(g);o.material.envMapIntensity=.3;if(o.material.emissiveIntensity>1)o.material.emissiveIntensity=.65;}});
 if(parent)for(const {material,geometries} of bins.values()){
  const geometry=mergeGeometries(geometries,false);
  if(!geometry)throw new Error('Cannot combine model geometry: '+path);
  const mesh=new THREE.Mesh(geometry,material);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);geometries.forEach(g=>g.dispose());
 }
 assetReport.push({path,meshes,triangles});$('#world').dataset.assets=JSON.stringify(assetReport);return gltf.scene;
}
Promise.all([loadModel('/assets/arcade-premium.glb',arcade),loadModel('/assets/arena-premium.glb',arena),loadModel('/assets/brick-premium.glb')]).then(([, ,asset])=>{
 brickAsset=new THREE.Group();const propBins=new Map();asset.updateMatrixWorld(true);asset.traverse(o=>{if(o.isMesh){const key=o.material.uuid;if(!propBins.has(key))propBins.set(key,{name:o.name,material:o.material,geometries:[]});propBins.get(key).geometries.push(o.geometry.clone().applyMatrix4(o.matrixWorld));}});for(const b of propBins.values()){const m=new THREE.Mesh(mergeGeometries(b.geometries),b.material);m.name=b.name;brickAsset.add(m);}ready=true;$('#play').disabled=false;refreshSelection();
}).catch(error=>{console.error(error);$('#play-label').textContent='Reload the arcade';$('#play').disabled=false;$('#play').onclick=()=>location.reload();$('#load-note').textContent='A 3D asset did not load. Click to retry.';});

const game=new Brickstorm();
let mode='home',intro=true,banked=false,muted=true,audioContext,twoPaddles=false;
const crossing=new BayouCrossing(),stickHops=new StickHops(),arcadeStick=new StickHops();
let selectedGame='brickstorm',portalGame='brickstorm',bayouReady=false,bayouBanked=true,frogEye=false;
let bayouSave;try{bayouSave=readBayouSave(localStorage)}catch{bayouSave={scores:[],trophy:false}}
const bayouTrophy=new THREE.Group();bayouTrophy.position.set(-3.2,1.6,2.5);bayouTrophy.scale.setScalar(.4);arcade.add(bayouTrophy);
Promise.all([bayouView.load(),loadModel('/assets/bayou/cabinet.glb',bayouCabinet)]).then(async ([report])=>{
 const preparation=new THREE.Scene();preparation.environment=scene.environment;preparation.environmentIntensity=scene.environmentIntensity;preparation.fog=new THREE.Fog('#0c1922',20,75);for(const light of scene.children.filter(o=>o.isLight))preparation.add(light.clone());bayouView.root.visible=true;preparation.add(bayouView.root);bayouView.update(crossing,0);await renderer.compileAsync(preparation,camera);bayouView.root.visible=false;scene.add(bayouView.root);
 assetReport.push(...report);$('#world').dataset.assets=JSON.stringify(assetReport);bayouReady=true;refreshSelection();
 const prize=bayouView.frog.clone(true);prize.traverse(o=>{if(o.isMesh)o.material=new THREE.MeshStandardMaterial({color:0xd5b56c,metalness:.8,roughness:.26})});bayouTrophy.add(prize);bayouTrophy.visible=bayouSave.trophy;
}).catch(error=>{console.error(error);$('#select-bayou').dataset.failed='true';if(selectedGame==='bayou'){$('#load-note').textContent='Bayou assets did not load. Reload to retry.';}});
function refreshSelection(){
 const bayou=selectedGame==='bayou';$('#game-number').textContent=bayou?'02':'01';$('#game-name').textContent=bayou?'Bayou Crossing':'Brickstorm Arena';$('#game-description').textContent=bayou?'A frog-sized road & river adventure':'A first-person breakout experience';
 $('#play-label').textContent=bayou?(bayouReady?'Play Bayou Crossing':'Preparing Bayou Crossing…'):(ready?'Play Brickstorm':'Preparing your arcade…');$('#play').disabled=bayou?!bayouReady:!ready;
 $('#load-note').textContent=bayou?'Arrow keys, WASD or touch · 3 rounds':'Mouse or touch · No headset needed';
 for(const id of ['brickstorm','bayou'])$('#select-'+id).setAttribute('aria-pressed',String(id===selectedGame));
 $('#tour-play').textContent=bayou?'Play Bayou Crossing':'Play Brickstorm';
}
function selectGame(id){selectedGame=id;refreshSelection();}
$('#select-brickstorm').onclick=()=>selectGame('brickstorm');$('#select-bayou').onclick=()=>selectGame('bayou');
function bankBayou(){if(bayouBanked)return;bayouBanked=true;bayouSave=recordBayouRun(bayouSave,crossing);try{localStorage.setItem(SAVE_KEY,JSON.stringify(bayouSave))}catch{notify('Score saved for this session only')}bayouTrophy.visible=bayouSave.trophy;}
function startBayou(){
 if(!bayouReady)return;mode='bayou';syncBayouUI.last='';crossing.restart();bayouBanked=false;arcade.visible=false;arena.visible=false;bayouView.root.visible=true;scene.background.set('#0c1922');scene.fog=new THREE.Fog('#0c1922',20,75);document.body.classList.add('in-game','in-bayou');$('#hud').hidden=false;$('#tour-controls').hidden=true;$('#play-hint').hidden=false;$('#bayou-controls').hidden=false;
 keys.clear();stickHops.reset();bayouView.facing=0;setView(new THREE.Vector3(0,7.8,6.4),new THREE.Vector3(0,0,-4.6));
 if(renderer.xr.isPresenting){rig.position.set(0,-1,0);rig.rotation.set(0,0,0);camera.position.set(0,0,0)}
 updateBayou(0);syncBayouUI();$('#world').focus({preventScroll:true});
}
function bayouHop(dx,dy){if(crossing.hopDirection(dx,dy)){bayouView.hop(dx,dy);sound(340,.06,.025);haptic(.08);return true}return false}
function syncBayouUI(){
 const signature=[crossing.started,crossing.finished,crossing.paused,crossing.won,crossing.round,Math.ceil(crossing.timer),crossing.score,crossing.lives,crossing.homes.length,crossing.roundDelay>0,crossing.recovery>0,renderer.xr.isPresenting].join(':');if(syncBayouUI.last===signature)return;syncBayouUI.last=signature;
 $('#hud-title').textContent='BAYOU CROSSING';$('#level').textContent=`Round ${crossing.round+1}/3 · ${crossing.homes.length}/5 home · ${Math.ceil(crossing.timer)}s`;$('#score').textContent=String(crossing.score).padStart(6,'0');$('#lives').textContent='● '.repeat(crossing.lives).trim();$('#stat-label').textContent='Homes';$('#bricks').textContent=crossing.homes.length+'/5';$('#pause').textContent=crossing.paused?'Resume':'Pause';
 $('#instruction').hidden=renderer.xr.isPresenting||crossing.started&&!crossing.paused&&!crossing.finished;$('#bayou-controls').hidden=renderer.xr.isPresenting;
 $('#instruction-kicker').textContent=crossing.finished?(crossing.won?'ALL FIVE HOME, THREE TIMES':'RUN COMPLETE'):crossing.paused?'TAKE YOUR TIME':'YOUR FIRST CROSSING';
 $('#instruction-title').textContent=crossing.finished?(crossing.won?'Home before morning.':'Another crossing?'):crossing.paused?'Game paused.':'One hop at a time.';
 $('#instruction-body').innerHTML=crossing.finished?`${crossing.score.toLocaleString()} points saved${crossing.won?' · Golden frog trophy earned':''}.`:crossing.paused?'Your crossing is waiting exactly where you left it.':'Arrow keys or WASD to hop.<br>Avoid traffic. Ride logs and turtles.<br>Reach each of the five glowing homes.';
 $('#serve').textContent=crossing.finished?'Play again':crossing.paused?'Resume crossing':'Start crossing';
 $('#hint-action').textContent='Arrow keys / WASD to hop';$('#hint-secondary').textContent='Space to start · Esc to pause';
 $('#power').textContent=crossing.roundDelay>0?'All five home · Next round…':crossing.recovery>0?'Returning to the bank…':'';
}
function updateBayou(dt){
 if(renderer.xr.isPresenting){
  const source=[...renderer.xr.getSession().inputSources].find(s=>s.handedness==='left'&&s.gamepad)||[...renderer.xr.getSession().inputSources].find(s=>s.gamepad);
  if(source){const a=source.gamepad.axes,move=stickHops.sample(a.length>=4?a[2]:a[0],a.length>=4?a[3]:a[1]);if(move)bayouHop(...move)}
 }
 crossing.update(dt);
 for(const e of crossing.drainEvents()){
  if(e.type==='death'){notify({traffic:'Watch the traffic.',water:'Find a log or a surfaced turtle.',swept:'Hop before the current carries you away.',time:'Time ran out.', 'closed-home':'Choose an empty glowing home.'}[e.reason]);sound(110,.28);haptic(.35)}
  if(e.type==='home'){notify('One more friend home.');sound(850,.25)}
  if(e.type==='round'){notify('The crossing picks up speed.');bayouView.facing=0}
  if(e.type==='spawn')bayouView.facing=0;
  if(e.type==='win'||e.type==='lose')bankBayou();
 }
 const xr=renderer.xr.isPresenting;bayouView.update(crossing,dt,{firstPerson:frogEye||xr,xr});
 comfortFade.visible=xr&&!!crossing.hop;comfortFade.material.opacity=crossing.hop?Math.sin(Math.min(1,crossing.hop.elapsed/.18)*Math.PI)*.72:0;
 const p=crossing.visualFrog;
 if(xr){const eyeY=camera.position.y||1.6;rig.position.set(p.x,.8-eyeY,-p.row*CELL);rig.rotation.set(0,0,0);}
 else if(frogEye){setView(new THREE.Vector3(p.x,.8,-p.row*CELL+.05),new THREE.Vector3(p.x,.8,-p.row*CELL-5));}
 else{const follow=Math.max(0,p.row*CELL-3);setView(new THREE.Vector3(p.x*.18,7.8,6.4-follow),new THREE.Vector3(p.x*.12,0,-4.6-follow));}
 syncBayouUI();$('#world').dataset.bayou=JSON.stringify({started:crossing.started,paused:crossing.paused,row:crossing.frog.row,x:crossing.frog.x,score:crossing.score,lives:crossing.lives,round:crossing.round+1,homes:crossing.homes.length,finished:crossing.finished});
}
for(const button of document.querySelectorAll('[data-hop]'))button.onclick=()=>{bayouHop(...button.dataset.hop.split(',').map(Number));$('#world').focus({preventScroll:true})};
$('#bayou-camera').onclick=()=>{frogEye=!frogEye;$('#bayou-camera').textContent=frogEye?'Elevated view':'Frog-eye view';};

let save;try{save=readSave(localStorage)}catch{save={scores:[],tickets:0,trophy:false}}
const blockMeshes=new Map(),bonusMeshes=new Map(),fragments=[];
const colors=[0x50bbbc,0x587fce,0xa55ec4,0xdc6b77,0xe6ac4d];
const sharedFragmentGeo=new RoundedBoxGeometry(.16,.12,.15,1,.02);
const fragmentMaterials=colors.map(c=>new THREE.MeshStandardMaterial({color:c,metalness:.45,roughness:.25,emissive:c,emissiveIntensity:.2}));
function solid(geometry,color,emission=0){return new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color,metalness:.5,roughness:.24,emissive:color,emissiveIntensity:emission}))}
function createPaddle(color){
 const group=new THREE.Group();const shell=solid(new RoundedBoxGeometry(1.2,.72,.09,4,.07),0x213a48);shell.material.transparent=true;shell.material.opacity=.08;shell.material.depthWrite=false;group.add(shell);
 const face=solid(new RoundedBoxGeometry(1.1,.61,.015,3,.055),color,.35);face.position.z=-.055;face.material.transparent=true;face.material.opacity=.12;face.material.depthWrite=false;group.add(face);
 const rim=new THREE.LineSegments(new THREE.EdgesGeometry(new RoundedBoxGeometry(1.15,.67,.10,4,.065),25),new THREE.LineBasicMaterial({color}));group.add(rim);for(const y of [-.335,.335]){const bar=solid(new RoundedBoxGeometry(1.12,.035,.10,3,.017),color,1.1);bar.position.y=y;group.add(bar)}for(const x of [-.565,.565]){const bar=solid(new RoundedBoxGeometry(.035,.63,.10,3,.017),color,1.1);bar.position.x=x;group.add(bar)}
 const grip=solid(new RoundedBoxGeometry(.22,.38,.13,3,.025),0x162a34);grip.position.set(0,-.44,0);group.add(grip);
 for(const x of [-.47,.47]){const stud=solid(new THREE.CylinderGeometry(.023,.023,.12,12),0xbe976a);stud.rotation.x=Math.PI/2;stud.position.x=x;group.add(stud)}
 arena.add(group);return group;
}
const paddle=createPaddle(0x9ceae4),secondPaddle=createPaddle(0xf0b5cf);secondPaddle.visible=false;
paddle.position.set(0,1.7,.35);
const ball=solid(new THREE.SphereGeometry(.10,24,16),0xd6fffa,2.7);arena.add(ball);
const ballLight=areaLight(arena,0x8aece7,2,0,0,0);
const trail=Array.from({length:15},(_,i)=>{const m=new THREE.Mesh(new THREE.SphereGeometry(.08*(1-i/17),10,6),new THREE.MeshBasicMaterial({color:0x96f4ed,transparent:true,opacity:(1-i/15)*.3,depthWrite:false}));arena.add(m);return m});
const aimRing=new THREE.Mesh(new THREE.RingGeometry(.15,.17,40),new THREE.MeshBasicMaterial({color:0xe4bb83,transparent:true,opacity:.6,side:THREE.DoubleSide,depthWrite:false}));arena.add(aimRing);
function makeLabel(parent,w,h,x,y,z){
 const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=256;const context=canvas.getContext('2d');const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false}));mesh.position.set(x,y,z);parent.add(mesh);
 return text=>{context.clearRect(0,0,1024,256);context.textAlign='center';context.fillStyle='#e2d0ab';context.font='500 52px monospace';text.split('\n').forEach((line,i)=>context.fillText(line,512,90+i*85));texture.needsUpdate=true};
}
const arenaLabel=makeLabel(arena,4.5,.8,0,4.4,-8);
const prizeLabel=makeLabel(arcade,2.5,.6,-4,2.5,2.5);
const bayouCabinetLabel=makeLabel(arcade,1.8,.35,2.3,2.7,-4.05);bayouCabinetLabel('');
const cabinetLabel=makeLabel(arcade,1.3,.3,0,2.7,-2.7);cabinetLabel('');
function updatePrize(){prizeLabel(`${save.tickets} TICKETS\nBEST ${String(save.scores[0]?.score||0).padStart(6,'0')}`)}updatePrize();
const trophy=solid(new THREE.IcosahedronGeometry(.23,1),0xe9bb78,.3);trophy.position.set(-4,2.05,2.5);arcade.add(trophy);trophy.visible=save.trophy;
function bank(){if(banked)return;banked=true;if(game.score>0){save.scores.push({score:game.score,level:game.level+1,won:game.won});save.scores.sort((a,b)=>b.score-a.score);save.scores=save.scores.slice(0,10);save.tickets+=Math.floor(game.score/100);save.trophy||=game.won;try{localStorage.setItem('afterhours-v1',JSON.stringify(save))}catch{notify('Score saved for this session only')}updatePrize();trophy.visible=save.trophy}}
function sound(frequency=600,duration=.12,volume=.05){
 if(muted)return;
 audioContext ||= new AudioContext();audioContext.resume();
 const osc=audioContext.createOscillator(),gain=audioContext.createGain();osc.type='triangle';osc.frequency.setValueAtTime(frequency,audioContext.currentTime);osc.frequency.exponentialRampToValueAtTime(frequency*.7,audioContext.currentTime+duration);gain.gain.setValueAtTime(volume,audioContext.currentTime);gain.gain.exponentialRampToValueAtTime(.0001,audioContext.currentTime+duration);osc.connect(gain).connect(audioContext.destination);osc.start();osc.stop(audioContext.currentTime+duration);
}
function notify(message){$('#message').textContent=message;$('#message').style.opacity=1;clearTimeout(notify.timer);notify.timer=setTimeout(()=>$('#message').style.opacity=0,2200)}
function clearModels(map){for(const mesh of map.values()){arena.remove(mesh);mesh.traverse(o=>{if(o.isMesh&&o.userData.ownedMaterial)o.material.dispose()})}map.clear()}
function buildBricks(){
 clearModels(blockMeshes);clearModels(bonusMeshes);
 for(const b of game.blocks){const mesh=brickAsset.clone(true);mesh.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.userData.ownedMaterial=true;if(o.name.startsWith('BRICK_INLAY')){o.material.color.set(colors[b.row]);o.material.emissive.set(colors[b.row]);o.material.emissiveIntensity=.18;o.material.metalness=.4;o.material.roughness=.22;}else if(o.name.startsWith('BRICK_BODY')){o.material.color.set(colors[b.row]).multiplyScalar(.3);o.material.emissiveIntensity=0;}o.castShadow=false;o.receiveShadow=true}});mesh.position.set(b.x,b.y,b.z);arena.add(mesh);blockMeshes.set(b.id,mesh)}
}
function fragment(position,row,count=8,slow=false){for(let i=0;i<count;i++){const mesh=new THREE.Mesh(sharedFragmentGeo,fragmentMaterials[row%5]);mesh.position.copy(position);mesh.userData={velocity:new THREE.Vector3((Math.random()-.5)*2,Math.random()*2,(Math.random()-.5)*2),life:slow?2.5:.65,slow};arena.add(mesh);fragments.push(mesh)}}
function processEvents(){for(const event of game.drainEvents()){
 if(event.type==='level'){buildBricks();intro=game.level===0;syncUI();}
 if(event.type==='hit'){const mesh=blockMeshes.get(event.id);if(mesh){arena.remove(mesh);blockMeshes.delete(event.id)}fragment(event.position,event.row);sound(450+event.row*130);}
 if(event.type==='paddle'){sound(250,.08);haptic(.2)}
 if(event.type==='armor')sound(170,.1);
 if(event.type==='miss'){notify('You have another ball.');sound(100,.3)}
 if(event.type==='power'){notify({wide:'Wide paddle · 10 seconds',slow:'Slow ball · 10 seconds',life:'Extra life'}[event.kind]);sound(1000,.22)}
 if(event.type==='collapse'){notify('Support broken. Watch it fall.');for(const b of event.blocks){const mesh=blockMeshes.get(b.id);if(mesh){mesh.userData={velocity:new THREE.Vector3((Math.random()-.5)*1.1,Math.random(),.5),life:2.5,slow:true,whole:true};fragments.push(mesh);blockMeshes.delete(b.id)}}sound(95,.6);}
 if(event.type==='win'||event.type==='lose'){bank();sound(event.type==='win'?900:110,.5);}
 syncUI();
}}
function setView(position,target){rig.position.set(0,0,0);rig.rotation.set(0,0,0);camera.position.copy(position);camera.lookAt(target);camera.updateMatrixWorld(true)}
const homePosition=new THREE.Vector3(2.4,1.75,1.1),homeTarget=new THREE.Vector3(-1.0,1.4,-2.7);
setView(homePosition,homeTarget);
function home(){comfortFade.visible=false;$('#message').style.opacity=0;if(mode==='bayou')bankBayou();bank();bayouView.root.visible=false;$('#bayou-controls').hidden=true;document.body.classList.remove('in-bayou');scene.background.set('#080e16');scene.fog=new THREE.Fog('#080e16',16,50);$('#power').textContent='';mode='home';game.paused=false;arcade.visible=true;arena.visible=false;document.body.classList.remove('in-game');$('#hud').hidden=true;$('#instruction').hidden=true;$('#play-hint').hidden=true;$('#tour-controls').hidden=true;$('#home').hidden=false;$('#vignette').hidden=false;setView(homePosition,homeTarget);keys.clear();}
function startGame(){
 if(portalGame==='bayou'){startBayou();return}
 if(!ready)return;bayouView.root.visible=false;$('#bayou-controls').hidden=true;document.body.classList.remove('in-bayou');scene.background.set('#080e16');scene.fog=new THREE.Fog('#080e16',16,50);$('#hud-title').textContent='BRICKSTORM';$('#stat-label').textContent='Bricks';$('#hint-action').textContent='Move mouse to catch the ball';$('#hint-secondary').textContent='Space to serve · Esc to pause';
 mode='game';banked=false;game.restart();game.reachAssist=renderer.xr.isPresenting;intro=true;arcade.visible=false;arena.visible=true;document.body.classList.add('in-game');$('#hud').hidden=false;$('#tour-controls').hidden=true;$('#play-hint').hidden=false;
 if(renderer.xr.isPresenting){rig.position.set(0,0,.6);rig.rotation.set(0,0,0);camera.position.set(0,0,0)}
 else setView(new THREE.Vector3(0,2.45,5.3),new THREE.Vector3(0,2.2,-5));
 paddle.position.set(0,1.7,.35);pointerValid=false;keys.clear();processEvents();syncUI();$('#world').focus({preventScroll:true});
}
let portalTime=0;
function play(){if((selectedGame==='bayou'?!bayouReady:!ready)||mode==='portal')return;if(mode==='bayou')bankBayou();portalGame=selectedGame;mode='portal';portalTime=0;$('#play').blur();$('#transition').style.opacity=1;sound(140,.3);}
function launch(){if(mode==='bayou'){if(crossing.finished){startBayou();return}crossing.start();syncBayouUI();$('#world').focus({preventScroll:true});return}if(mode!=='game')return;if(game.finished){play();return}if(game.paused){game.paused=false;syncUI();$('#world').focus({preventScroll:true});return}game.serve(paddle);intro=false;processEvents();$('#world').focus({preventScroll:true})}
function pause(){if(mode==='bayou'){if(!crossing.finished&&crossing.started){crossing.paused=!crossing.paused;stickHops.reset();syncBayouUI()}return}if(mode!=='game'||game.finished||game.clearTime)return;game.paused=!game.paused;keys.clear();syncUI()}
function syncUI(){
 if(mode==='bayou'){syncBayouUI();return}
 if(mode!=='game')return;
 $('#level').textContent=`${LEVEL_NAMES[game.level]} / ${String(game.level+1).padStart(2,'0')}`;
 $('#score').textContent=String(game.score).padStart(6,'0');$('#lives').textContent='● '.repeat(game.lives).trim();$('#bricks').textContent=game.blocks.length;$('#pause').textContent=game.paused?'Resume':'Pause';
 const show=(!game.launched&&!game.clearTime)||game.paused||game.finished;
 $('#instruction').hidden=!show||renderer.xr.isPresenting;
 if(game.finished){$('#instruction-kicker').textContent=game.won?'ALL TEN CLEARED':'RUN COMPLETE';$('#instruction-title').textContent=game.won?'You broke the storm.':'One more game?';$('#instruction-body').textContent=`${game.score.toLocaleString()} points · ${Math.floor(game.score/100)} tickets saved${game.won?' · Trophy earned':''}`;$('#serve').innerHTML='Play again <span>↗</span>'}
 else if(game.paused){$('#instruction-kicker').textContent='TAKE YOUR TIME';$('#instruction-title').textContent='Game paused.';$('#instruction-body').textContent='Your ball is waiting exactly where you left it.';$('#serve').textContent='Resume game'}
 else{$('#instruction-kicker').textContent=intro?'YOUR FIRST SERVE':`LEVEL ${game.level+1} OF 10`;$('#instruction-title').textContent=intro?'Move your paddle.':'Ready for another ball?';$('#instruction-body').innerHTML=intro?'Move your mouse. The paddle follows it.<br>Catch the returning ball and break the wall.':'Aim with your mouse or touch.<br>Break the lowest row to collapse the formation.';$('#serve').innerHTML='Launch ball <span>↗</span>'}
 arenaLabel(`${String(game.score).padStart(6,'0')}     ${game.lives} LIVES\n${game.finished?'TRIGGER TO PLAY AGAIN':game.paused?'PAUSED · TRIGGER TO RESUME':!game.launched?(renderer.xr.isPresenting?'TRIGGER TO SERVE':'SPACE TO SERVE'):LEVEL_NAMES[game.level].toUpperCase()}`);
}
$('#play').onclick=play;$('#serve').onclick=launch;$('#pause').onclick=pause;$('#leave').onclick=()=>{if(renderer.xr.isPresenting)xrArcade();else home()};
$('#audio').onclick=()=>{muted=!muted;$('#audio').textContent=muted?'Sound off':'Sound on';$('#audio').setAttribute('aria-pressed',String(!muted));sound()};
function dialog(html){$('#dialog-content').innerHTML=html;$('#dialog').showModal()}
$('#close').onclick=()=>$('#dialog').close();
$('#scores').onclick=()=>dialog(`<h2>Bayou Crossing</h2>${bayouSave.scores.length?'<p>'+bayouSave.scores.map((s,i)=>`${i+1}. ${s.score.toLocaleString()} points · Round ${s.round}/3`).join('<br>')+'</p>':'<p>Your first crossing score belongs here.</p>'}`+`<h2>Your high scores</h2><p>${save.tickets} tickets collected. Saved on this browser.</p>${save.scores.length?'<table><thead><tr><th>Rank</th><th>Score</th><th>Level</th></tr></thead><tbody>'+save.scores.map((s,i)=>`<tr><td>${i+1}</td><td>${s.score.toLocaleString()}</td><td>${Number(s.level)||1}/10</td></tr>`).join('')+'</tbody></table>':'<p>Your first score belongs here. Close this panel and select Play Brickstorm.</p>'}`);
$('#help').onclick=()=>{dialog('<h2>Bayou Crossing</h2><p>Select <b>Bayou Crossing</b>, then <b>Play Bayou Crossing</b> and <b>Start crossing</b>. Press an arrow key or WASD once per hop, or use the on-screen direction buttons. Reach five empty lily pads. Turtles bob before diving. In VR, use trigger to start and the left stick to hop; release the stick between hops. In the VR arcade, flick left/right to switch cabinets. Hold both triggers to return.</p><h2>Brickstorm</h2><p><b>1.</b> Select <b>Play Brickstorm</b>.<br><b>2.</b> Move your mouse or finger to move the paddle.<br><b>3.</b> Select <b>Launch ball</b> or press Space.</p><p>Catch the ball when it comes back toward you. Hit near the paddle’s edges to change the angle. Break the bottom supports to bring the formation down. Gold bonuses give a wider paddle, slower ball, or extra life.</p><p><b>Pause:</b> use the visible Pause button or Esc. Click Resume game to continue. Arrow keys also move the paddle.</p><p><b>VR:</b> trigger starts and serves. Move your controller to catch the ball. Grip a token near the center cabinet and insert it for the optional physical entry. Hold both triggers to return.</p><label><input type="checkbox" id="two"> Use two paddles in VR</label>');$('#two').checked=twoPaddles;$('#two').onchange=e=>twoPaddles=e.target.checked};
// Guided views replace unreliable free-roaming controls. Playing never requires walking to a cabinet.
const views=[{name:'The arcade floor',position:homePosition,target:homeTarget},{name:'Your Brickstorm machine',position:new THREE.Vector3(1.6,1.65,-.3),target:new THREE.Vector3(0,1.35,-2.7)},{name:'Your Bayou Crossing machine',position:new THREE.Vector3(3.2,1.65,-1.7),target:new THREE.Vector3(2.3,1.4,-4.05)},{name:'The prize counter',position:new THREE.Vector3(-1,1.9,5.3),target:new THREE.Vector3(-4,1.3,2.5)}];let viewIndex=0;
function tour(index){if(!ready)return;mode='tour';viewIndex=(index+views.length)%views.length;$('#home').hidden=true;$('#vignette').hidden=true;$('#tour-controls').hidden=false;$('#tour-label').textContent=views[viewIndex].name;if(viewIndex===1)selectGame('brickstorm');if(viewIndex===2)selectGame('bayou');setView(views[viewIndex].position,views[viewIndex].target)}
$('#tour').onclick=()=>tour(0);$('#tour-prev').onclick=()=>tour(viewIndex-1);$('#tour-next').onclick=()=>tour(viewIndex+1);$('#tour-play').onclick=play;$('#tour-back').onclick=home;

// Pointer ray intersects the paddle plane: cursor and visible paddle now share the same coordinate system.
const pointer=new THREE.Vector2(),raycaster=new THREE.Raycaster(),pointerPlane=new THREE.Plane(new THREE.Vector3(0,0,1),-.35),hitPoint=new THREE.Vector3();
let pointerValid=false;const keys=new Set();
function aim(event){if(mode!=='game'||renderer.xr.isPresenting)return;const rect=renderer.domElement.getBoundingClientRect();pointer.set((event.clientX-rect.left)/rect.width*2-1,-((event.clientY-rect.top)/rect.height)*2+1);pointerValid=true;}
$('#world').addEventListener('pointermove',aim);
$('#world').addEventListener('pointerdown',event=>{aim(event);if(mode==='game'){if(!game.launched||game.paused)launch()}$('#world').focus({preventScroll:true});});
window.addEventListener('keydown',event=>{if($('#dialog').open)return;if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Escape'].includes(event.code))event.preventDefault();if(event.repeat&&['Space','Escape','KeyP'].includes(event.code))return;keys.add(event.code);if(mode==='bayou'){const hop=keyboardHop(event.code,event.repeat);if(hop){event.preventDefault();bayouHop(...hop)}if(event.code==='Space')launch();if(event.code==='Escape'||event.code==='KeyP')pause();}else if(mode==='game'){if(event.code==='Space')launch();if(event.code==='Escape'||event.code==='KeyP')pause();if(event.code.startsWith('Arrow'))pointerValid=false}else if(event.code==='Space')play()});
window.addEventListener('keyup',event=>keys.delete(event.code));
window.addEventListener('blur',()=>{keys.clear();if(mode==='bayou'&&crossing.started&&!crossing.finished){crossing.paused=true;syncBayouUI()}if(mode==='game'&&game.launched&&!game.finished){game.paused=true;syncUI()}});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&mode==='bayou'&&crossing.started&&!crossing.finished){crossing.paused=true;syncBayouUI()}if(document.hidden&&mode==='game'&&game.launched){game.paused=true;syncUI()}});

// WebXR: direct entry, controller paddles, explicit in-world labels, optional physical token interaction.
const controllers=[],grips=[];let primaryIndex=0;
for(let i=0;i<2;i++){
 const controller=renderer.xr.getController(i),grip=renderer.xr.getControllerGrip(i);rig.add(controller,grip);controllers.push(controller);grips.push(grip);
 controller.addEventListener('connected',e=>{controller.userData.handedness=e.data.handedness;if(e.data.handedness==='right')primaryIndex=i});
 controller.addEventListener('selectstart',()=>{if(mode==='xr-arcade')play();else if(mode==='game'||mode==='bayou')launch()});
 const handle=solid(new RoundedBoxGeometry(.045,.11,.07,2,.01),0x344450);grip.add(handle);
 controller.addEventListener('squeezestart',()=>{if(mode!=='xr-arcade'||token.userData.held)return;const p=controller.getWorldPosition(new THREE.Vector3());if(p.distanceTo(token.getWorldPosition(new THREE.Vector3()))<.35){controller.attach(token);token.position.set(0,-.025,-.08);token.userData.held=true;}});
 controller.addEventListener('squeezeend',()=>{if(token.parent===controller){arcade.attach(token);token.position.set(.23,1.18,-2.15);token.userData.held=false;}});
}
const token=solid(new THREE.CylinderGeometry(.045,.045,.012,32),0xe0b87a,.25);token.rotation.x=Math.PI/2;token.position.set(.23,1.18,-2.15);arcade.add(token);
function xrArcade(){comfortFade.visible=false;if(mode==='bayou')bankBayou();bayouView.root.visible=false;$('#bayou-controls').hidden=true;document.body.classList.remove('in-bayou');scene.background.set('#080e16');scene.fog=new THREE.Fog('#080e16',16,50);cabinetLabel('BRICKSTORM\nTRIGGER TO PLAY');bayouCabinetLabel('BAYOU CROSSING\nTRIGGER TO PLAY');bank();mode='xr-arcade';arcade.visible=true;arena.visible=false;rig.position.set(selectedGame==='bayou'?2.3:0,0,selectedGame==='bayou'?-2.5:-1.25);rig.rotation.set(0,0,0);camera.position.set(0,0,0);$('#instruction').hidden=true;$('#hud').hidden=true;$('#play-hint').hidden=true;document.body.classList.add('in-game');}
$('#vr').onclick=async()=>{if(!ready)return;try{if(!navigator.xr||!await navigator.xr.isSessionSupported('immersive-vr')){dialog('<h2>Play in your headset</h2><p>Open this site in a compatible headset browser over HTTPS, then select Play with a VR headset.</p><p>You can play right here with your mouse using Play Brickstorm.</p>');return}const session=await navigator.xr.requestSession('immersive-vr',{optionalFeatures:['local-floor','bounded-floor']});await renderer.xr.setSession(session);xrArcade()}catch(error){dialog('<h2>VR did not start</h2><p>'+String(error.message).replace(/[<>]/g,'')+'</p><p>You can still select Play Brickstorm for desktop play.</p>')}};
renderer.xr.addEventListener('sessionend',()=>{home()});
function haptic(strength){const inputs=renderer.xr.getSession()?.inputSources;if(inputs)for(const source of inputs)source.gamepad?.hapticActuators?.[0]?.pulse(strength,30)?.catch(()=>{})}
function fold(value,min,max){const length=max-min,phase=((value-min)%(2*length)+2*length)%(2*length);return min+(phase>length?2*length-phase:phase)}
let last=performance.now(),exitHold=0,crtTick=0,performanceTime=0,frameCount=0;renderer.info.autoReset=false;
renderer.setAnimationLoop(now=>{
 const rawDt=Math.max((now-last)/1000,0),dt=Math.min(rawDt,.1);last=now;performanceTime+=rawDt;frameCount++;crtTick+=dt;if(crtTick>.1&&arcade.visible){drawCRT(now/1000);crtTick=0;}
 if(mode==='portal'){
  portalTime+=dt;
  if(portalTime>.3){startGame();$('#transition').style.opacity=0;}
 }
 if(mode==='bayou')updateBayou(dt);
 if(mode==='xr-arcade'&&renderer.xr.isPresenting){const source=[...renderer.xr.getSession().inputSources].find(s=>s.gamepad);if(source){const a=source.gamepad.axes,move=arcadeStick.sample(a.length>=4?a[2]:a[0],a.length>=4?a[3]:a[1]);if(move&&move[0]){selectGame(move[0]>0?'bayou':'brickstorm');xrArcade()}}}
 if(mode==='game'){
  if(renderer.xr.isPresenting){grips[primaryIndex].getWorldPosition(paddle.position);grips[primaryIndex].getWorldQuaternion(paddle.quaternion);secondPaddle.visible=twoPaddles;grips[1-primaryIndex].getWorldPosition(secondPaddle.position);grips[1-primaryIndex].getWorldQuaternion(secondPaddle.quaternion)}
  else{
   paddle.quaternion.identity();secondPaddle.visible=false;
   if(pointerValid){camera.updateMatrixWorld(true);raycaster.setFromCamera(pointer,camera);if(raycaster.ray.intersectPlane(pointerPlane,hitPoint))paddle.position.copy(hitPoint)}
   const movement=new THREE.Vector3((keys.has('ArrowRight')?1:0)-(keys.has('ArrowLeft')?1:0),(keys.has('ArrowUp')?1:0)-(keys.has('ArrowDown')?1:0),0);paddle.position.addScaledVector(movement,dt*3);
   paddle.position.x=THREE.MathUtils.clamp(paddle.position.x,-2.9,2.9);paddle.position.y=THREE.MathUtils.clamp(paddle.position.y,.45,4.45);paddle.position.z=.35;
  }
  paddle.scale.set(game.power==='wide'?1.6:1,game.power==='wide'?1.4:1,1);
  const paddles=[paddle,...(secondPaddle.visible?[secondPaddle]:[])];game.update(dt,paddles);processEvents();
  ball.position.copy(game.ball);ballLight.position.copy(game.ball);ball.visible=!game.finished&&!game.clearTime;
  for(let i=trail.length-1;i>0;i--)trail[i].position.copy(trail[i-1].position);trail[0].position.copy(game.ball);trail.forEach(m=>m.visible=game.launched&&!game.paused);
  aimRing.visible=game.launched&&game.velocity.z>0&&game.ball.z<.2;
  if(aimRing.visible){const travel=(.35-game.ball.z)/game.velocity.z;aimRing.position.set(fold(game.ball.x+game.velocity.x*travel,-3,3),fold(game.ball.y+game.velocity.y*travel,.35,4.6),.30);}
  for(const b of game.blocks){const mesh=blockMeshes.get(b.id);if(mesh)mesh.position.set(b.x,b.y,b.z)}
  for(const bonus of game.bonuses){if(!bonusMeshes.has(bonus.id)){const m=solid(new THREE.IcosahedronGeometry(.18,1),0xedc78a,.8);arena.add(m);bonusMeshes.set(bonus.id,m)}const m=bonusMeshes.get(bonus.id);m.position.copy(bonus.position);m.rotation.y+=dt*2;}
  for(const [id,m] of bonusMeshes)if(!game.bonuses.some(b=>b.id===id)){arena.remove(m);m.geometry.dispose();m.material.dispose();bonusMeshes.delete(id)}
  $('#power').textContent=game.powerTime>0?`${{wide:'Wide paddle',slow:'Slow ball',life:'Extra life'}[game.power]} ${Math.ceil(game.powerTime)}s`:'';
 }
 if(mode==='xr-arcade'&&token.userData.held){if(token.getWorldPosition(new THREE.Vector3()).distanceTo(new THREE.Vector3(.22,.75,-2.154))<.19){arcade.attach(token);token.userData.held=false;token.position.set(.23,1.18,-2.15);play()}}
 if(renderer.xr.isPresenting){const inputs=renderer.xr.getSession().inputSources;let pressed=0;for(const source of inputs)if(source.gamepad?.buttons[0]?.pressed)pressed++;exitHold=pressed===2?exitHold+dt:0;if(exitHold>1.5){exitHold=0;xrArcade()}}
 for(let i=fragments.length-1;i>=0;i--){const f=fragments[i];if(game.paused&&mode==='game')continue;f.userData.life-=dt;f.position.addScaledVector(f.userData.velocity,dt*(f.userData.slow?.4:1));f.userData.velocity.y-=dt*(f.userData.slow?1.4:3);f.rotation.x+=dt*.6;f.rotation.z+=dt*.35;if(f.userData.life<=0){arena.remove(f);fragments.splice(i,1)}}
 trophy.rotation.y+=dt*.3;
 $('#world').dataset.mode=mode;renderer.info.reset();if(renderer.xr.isPresenting)renderer.render(scene,camera);else composer.render();if(performanceTime>=1){$('#world').dataset.performance=JSON.stringify({fps:Math.round(frameCount/performanceTime),drawCalls:renderer.info.render.calls,renderedTriangles:renderer.info.render.triangles,sceneTriangles:mode==='bayou'?bayouView.sceneTriangles():null,mode});performanceTime=0;frameCount=0;}
});
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);composer.setSize(innerWidth,innerHeight)});
// Read-only verification report. No gameplay bypasses are exposed.
window.arcadeDiagnostics=()=>({mode,ready,assets:assetReport,level:game.level+1,score:game.score,lives:game.lives,bricks:game.blocks.length,paused:game.paused,launched:game.launched,drawCalls:renderer.info.render.calls});
