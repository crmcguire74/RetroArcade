from pathlib import Path
p=Path('src/main.js');s=p.read_text()
def replace(a,b):
 global s
 if a not in s:raise RuntimeError('Missing patch anchor: '+a[:90])
 s=s.replace(a,b,1)
replace("import {readSave} from './rules.js';","""import {readSave} from './rules.js';
import {BayouCrossing,CELL} from './games/bayou/engine.js';
import {BayouView} from './games/bayou/view.js';
import {keyboardHop,StickHops} from './games/bayou/controls.js';
import {readBayouSave,recordBayouRun,SAVE_KEY} from './games/bayou/save.js';""")
replace("scene.add(arcade,arena);arena.visible=false;","scene.add(arcade,arena);arena.visible=false;\nconst bayouView=new BayouView();scene.add(bayouView.root);const bayouCabinet=new THREE.Group();bayouCabinet.position.set(2.3,0,-4.05);bayouCabinet.rotation.y=-.1;arcade.add(bayouCabinet);")
replace("gltf.scene.traverse(o=>{if(o.isMesh){", "gltf.scene.traverse(o=>{if(o.isMesh){let ancestor=o.parent;while(ancestor){if(path.includes('arcade-premium')&&ancestor.name.startsWith('VECTOR'))return;ancestor=ancestor.parent;}")
replace("if(/Convex.*CRT/.test(o.name))o.material=crtMaterial;", "if(!path.includes('/bayou/')&&/Convex.*CRT/.test(o.name))o.material=crtMaterial;")
replace("$('#play-label').textContent='Play Brickstorm';$('#load-note').textContent='Mouse or touch · No headset needed';", "refreshSelection();")
replace("let mode='home',intro=true,banked=false,muted=true,audioContext,twoPaddles=false;", """let mode='home',intro=true,banked=false,muted=true,audioContext,twoPaddles=false;
const crossing=new BayouCrossing(),stickHops=new StickHops(),arcadeStick=new StickHops();
let selectedGame='brickstorm',portalGame='brickstorm',bayouReady=false,bayouBanked=true,frogEye=false;
let bayouSave;try{bayouSave=readBayouSave(localStorage)}catch{bayouSave={scores:[],trophy:false}}
const bayouTrophy=new THREE.Group();bayouTrophy.position.set(-3.2,1.6,2.5);bayouTrophy.scale.setScalar(.4);arcade.add(bayouTrophy);
Promise.all([bayouView.load(),loadModel('/assets/bayou/cabinet.glb',bayouCabinet)]).then(([report])=>{
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
 if(!bayouReady)return;mode='bayou';crossing.restart();bayouBanked=false;arcade.visible=false;arena.visible=false;bayouView.root.visible=true;scene.background.set('#0c1922');scene.fog=new THREE.Fog('#0c1922',20,75);document.body.classList.add('in-game','in-bayou');$('#hud').hidden=false;$('#tour-controls').hidden=true;$('#play-hint').hidden=false;$('#bayou-controls').hidden=false;
 keys.clear();stickHops.reset();bayouView.facing=0;setView(new THREE.Vector3(0,7.8,6.4),new THREE.Vector3(0,0,-4.6));
 if(renderer.xr.isPresenting){rig.position.set(0,-1,0);rig.rotation.set(0,0,0);camera.position.set(0,0,0)}
 updateBayou(0);syncBayouUI();$('#world').focus({preventScroll:true});
}
function bayouHop(dx,dy){if(crossing.hopDirection(dx,dy)){bayouView.hop(dx,dy);sound(340,.06,.025);haptic(.08);return true}return false}
function syncBayouUI(){
 $('#hud-title').textContent='BAYOU CROSSING';$('#level').textContent=`Round ${crossing.round+1} / 3 · ${Math.ceil(crossing.timer)}s`;$('#score').textContent=String(crossing.score).padStart(6,'0');$('#lives').textContent='● '.repeat(crossing.lives).trim();$('#stat-label').textContent='Homes';$('#bricks').textContent=crossing.homes.length+'/5';$('#pause').textContent=crossing.paused?'Resume':'Pause';
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
 const p=crossing.visualFrog;
 if(xr){const eyeY=camera.position.y||1.6;rig.position.set(p.x,.8-eyeY,-p.row*CELL);rig.rotation.set(0,0,0);}
 else if(frogEye){setView(new THREE.Vector3(p.x,.8,-p.row*CELL+.05),new THREE.Vector3(p.x,.8,-p.row*CELL-5));}
 else{const follow=Math.max(0,p.row*CELL-3);setView(new THREE.Vector3(p.x*.18,7.8,6.4-follow),new THREE.Vector3(p.x*.12,0,-4.6-follow));}
 syncBayouUI();$('#world').dataset.bayou=JSON.stringify({started:crossing.started,paused:crossing.paused,row:crossing.frog.row,x:crossing.frog.x,score:crossing.score,lives:crossing.lives,round:crossing.round+1,homes:crossing.homes.length,finished:crossing.finished});
}
for(const button of document.querySelectorAll('[data-hop]'))button.onclick=()=>{bayouHop(...button.dataset.hop.split(',').map(Number));$('#world').focus({preventScroll:true})};
$('#bayou-camera').onclick=()=>{frogEye=!frogEye;$('#bayou-camera').textContent=frogEye?'Elevated view':'Frog-eye view';};
""")
replace("function home(){bank();mode='home';", "function home(){if(mode==='bayou')bankBayou();bank();bayouView.root.visible=false;$('#bayou-controls').hidden=true;document.body.classList.remove('in-bayou');scene.background.set('#080e16');scene.fog=new THREE.Fog('#080e16',16,50);$('#power').textContent='';mode='home';")
replace("function startGame(){\n if(!ready)return;", "function startGame(){\n if(portalGame==='bayou'){startBayou();return}\n if(!ready)return;bayouView.root.visible=false;$('#bayou-controls').hidden=true;document.body.classList.remove('in-bayou');scene.background.set('#080e16');scene.fog=new THREE.Fog('#080e16',16,50);$('#hud-title').textContent='BRICKSTORM';$('#stat-label').textContent='Bricks';$('#hint-action').textContent='Move mouse to catch the ball';$('#hint-secondary').textContent='Space to serve · Esc to pause';")
replace("function play(){if(!ready||mode==='portal')return;mode='portal';", "function play(){if((selectedGame==='bayou'?!bayouReady:!ready)||mode==='portal')return;if(mode==='bayou')bankBayou();portalGame=selectedGame;mode='portal';")
replace("function launch(){if(mode!=='game')return;", "function launch(){if(mode==='bayou'){if(crossing.finished){startBayou();return}crossing.start();syncBayouUI();$('#world').focus({preventScroll:true});return}if(mode!=='game')return;")
replace("function pause(){if(mode!=='game'", "function pause(){if(mode==='bayou'){if(!crossing.finished&&crossing.started){crossing.paused=!crossing.paused;stickHops.reset();syncBayouUI()}return}if(mode!=='game'")
replace("if(mode!=='game')return;\n $('#level')", "if(mode==='bayou'){syncBayouUI();return}\n if(mode!=='game')return;\n $('#level')")
# Append Bayou scores to the existing score dialog without changing existing storage.
replace("$('#scores').onclick=()=>dialog(", "$('#scores').onclick=()=>dialog(`<h2>Bayou Crossing</h2>${bayouSave.scores.length?'<p>'+bayouSave.scores.map((s,i)=>`${i+1}. ${s.score.toLocaleString()} points · Round ${s.round}/3`).join('<br>')+'</p>':'<p>Your first crossing score belongs here.</p>'}`+")
replace("dialog('<h2>Start here.</h2>", "dialog('<h2>Bayou Crossing</h2><p>Select <b>Bayou Crossing</b>, then <b>Play Bayou Crossing</b> and <b>Start crossing</b>. Press an arrow key or WASD once per hop, or use the on-screen direction buttons. Reach five empty lily pads. Turtles bob before diving. In VR, use trigger to start and the left stick to hop; release the stick between hops. In the VR arcade, flick left/right to switch cabinets. Hold both triggers to return.</p><h2>Brickstorm</h2>")
replace("{name:'The prize counter'", "{name:'Your Bayou Crossing machine',position:new THREE.Vector3(3.2,1.65,-1.7),target:new THREE.Vector3(2.3,1.4,-4.05)},{name:'The prize counter'")
replace("$('#tour-label').textContent=views[viewIndex].name;", "$('#tour-label').textContent=views[viewIndex].name;if(viewIndex===1)selectGame('brickstorm');if(viewIndex===2)selectGame('bayou');")
replace("keys.add(event.code);if(mode==='game'){", "keys.add(event.code);if(mode==='bayou'){const hop=keyboardHop(event.code,event.repeat);if(hop){event.preventDefault();bayouHop(...hop)}if(event.code==='Space')launch();if(event.code==='Escape'||event.code==='KeyP')pause();}else if(mode==='game'){")
replace("window.addEventListener('blur',()=>{keys.clear();", "window.addEventListener('blur',()=>{keys.clear();if(mode==='bayou'&&crossing.started&&!crossing.finished){crossing.paused=true;syncBayouUI()}")
replace("document.addEventListener('visibilitychange',()=>{", "document.addEventListener('visibilitychange',()=>{if(document.hidden&&mode==='bayou'&&crossing.started&&!crossing.finished){crossing.paused=true;syncBayouUI()}")
replace("else if(mode==='game')launch()", "else if(mode==='game'||mode==='bayou')launch()")
replace("function xrArcade(){cabinetLabel('BRICKSTORM\\nTRIGGER TO PLAY');bank();", "function xrArcade(){if(mode==='bayou')bankBayou();bayouView.root.visible=false;$('#bayou-controls').hidden=true;document.body.classList.remove('in-bayou');scene.background.set('#080e16');scene.fog=new THREE.Fog('#080e16',16,50);cabinetLabel('BRICKSTORM\\nTRIGGER TO PLAY');bayouCabinetLabel('BAYOU CROSSING\\nTRIGGER TO PLAY');bank();")
replace("rig.position.set(0,0,-1.25);", "rig.position.set(selectedGame==='bayou'?2.3:0,0,selectedGame==='bayou'?-2.5:-1.25);")
replace("const cabinetLabel=makeLabel", "const bayouCabinetLabel=makeLabel(arcade,1.8,.35,2.3,2.7,-4.05);bayouCabinetLabel('');\nconst cabinetLabel=makeLabel")
replace("if(mode==='game'){\n  if(renderer.xr.isPresenting)", "if(mode==='bayou')updateBayou(dt);\n if(mode==='xr-arcade'&&renderer.xr.isPresenting){const source=[...renderer.xr.getSession().inputSources].find(s=>s.gamepad);if(source){const a=source.gamepad.axes,move=arcadeStick.sample(a.length>=4?a[2]:a[0],a.length>=4?a[3]:a[1]);if(move&&move[0]){selectGame(move[0]>0?'bayou':'brickstorm');xrArcade()}}}\n if(mode==='game'){\n  if(renderer.xr.isPresenting)")
replace("if(renderer.xr.isPresenting)renderer.render(scene,camera);else composer.render();", "$('#world').dataset.mode=mode;if(renderer.xr.isPresenting)renderer.render(scene,camera);else composer.render();")
p.write_text(s)
# UI anchors and a compact accessible cabinet selector.
p=Path('index.html');s=p.read_text()
s=s.replace('After Hours — Brickstorm Arena','After Hours — Arcade Worlds').replace('3D arcade and Brickstorm game','3D arcade with Brickstorm and Bayou Crossing')
s=s.replace('<div class="start-panel">','<div class="start-panel"><div class="cabinet-selector" role="group" aria-label="Choose an arcade game"><button id="select-brickstorm" aria-pressed="true">01 · Brickstorm</button><button id="select-bayou" aria-pressed="false">02 · Bayou Crossing</button></div>')
s=s.replace('<span>01</span><div><h2>Brickstorm Arena</h2><p>A first-person breakout experience</p>','<span id="game-number">01</span><div><h2 id="game-name">Brickstorm Arena</h2><p id="game-description">A first-person breakout experience</p>')
s=s.replace('<div class="hud-brand">BRICKSTORM<span','<div class="hud-brand"><b id="hud-title">BRICKSTORM</b><span').replace('<small>Bricks</small>','<small id="stat-label">Bricks</small>')
s=s.replace('<span>Move mouse to catch the ball</span><span>Space to serve · Esc to pause</span>','<span id="hint-action">Move mouse to catch the ball</span><span id="hint-secondary">Space to serve · Esc to pause</span>')
s=s.replace('Ten formations. One high score.','Two machines. Two worlds.')
s=s.replace('<dialog id="dialog">','<div id="bayou-controls" hidden><button id="bayou-camera">Frog-eye view</button><div class="hop-pad" role="group" aria-label="Hop direction"><button data-hop="0,1" aria-label="Hop forward">↑</button><button data-hop="-1,0" aria-label="Hop left">←</button><button data-hop="0,-1" aria-label="Hop backward">↓</button><button data-hop="1,0" aria-label="Hop right">→</button></div></div><dialog id="dialog">')
p.write_text(s)
