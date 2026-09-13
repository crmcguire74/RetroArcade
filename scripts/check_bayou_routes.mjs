import {BayouCrossing,CELL} from '../src/games/bayou/engine.js';
const copy=g=>Object.assign(new BayouCrossing(),structuredClone({...g,events:[]}));
const step=(g,action)=>{const n=copy(g);if(action&&!n.hopDirection(...action))return null;n.update(.18);return n.lives===g.lives?n:null};
const game=new BayouCrossing();game.start();let active=game;let hops=0,branches=0;
for(let round=0;round<3;round++){
 for(const col of [0,-2,2,-4,4]){
  let beam=[{g:active,path:[]}],found;
  for(let depth=0;depth<180&&!found;depth++){
   const next=[],seen=new Set();
   for(const node of beam){
    for(const action of [[0,1],[-1,0],[1,0],null,[0,-1]]){
     const g=step(node.g,action);branches++;if(!g)continue;
     const path=[...node.path,action];
     if(g.homes.length>active.homes.length){if(Math.abs(g.frog.x-col*CELL)<.6){found={g,path};break}else continue}
     const key=`${g.frog.row}:${Math.round(g.frog.x*15)}`;if(seen.has(key))continue;seen.add(key);
     const rating=g.frog.row*5-Math.abs(g.frog.x-col*CELL)*1.5-Math.abs(g.frog.row-6)*.02;
     next.push({g,path,rating});
    }if(found)break;
   }
   beam=next.sort((a,b)=>b.rating-a.rating).slice(0,65);
   if(!beam.length)break;
  }
  if(!found)throw new Error(`No route found for round ${round+1}, column ${col}`);
  // Replay only public input and elapsed-time calls against the authoritative simulation.
  for(const action of found.path){if(action){if(!active.hopDirection(...action))throw Error('Replay rejected hop');hops++}active.update(.18)}
  if(active.lives!==3)throw Error('Replay collision');
  console.log(`Round ${round+1}, home ${col}: ${found.path.length} input beats, score ${active.score}`);
  for(let i=0;i<12;i++)active.update(.18);
 }
}
if(!active.won)throw Error('Expected full three-round win');
console.log(JSON.stringify({won:active.won,lives:active.lives,score:active.score,hops,branches},null,2));
