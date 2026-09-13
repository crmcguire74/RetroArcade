import test from 'node:test';
import assert from 'node:assert/strict';
import {Vector3,Quaternion} from 'three';
import {Brickstorm} from './engine.js';
const paddle=()=>({position:new Vector3(0,1.7,.35),quaternion:new Quaternion(),width:1.2,height:.72});
test('serve, brick collision, miss, and pause are deterministic',()=>{
 const game=new Brickstorm(),p=paddle();game.serve(p);
 for(let i=0;i<300;i++)game.update(1/120,[p]);
 assert.ok(game.score>=100);assert.ok(game.blocks.length<45);
 const before=game.ball.clone();game.paused=true;
 game.update(1,[p]);assert.deepEqual(game.ball,before);
 game.paused=false;p.position.x=-2.9;
 for(let i=0;i<600&&game.launched;i++)game.update(1/120,[p]);
 assert.equal(game.lives,3);assert.equal(game.launched,false);
});
test('paddle catches a returning ball only on an approaching crossing',()=>{
 const game=new Brickstorm(),p=paddle();game.launched=true;game.ball.set(0,1.7,.1);game.velocity.set(0,0,4);
 for(let i=0;i<8;i++)game.update(1/120,[p]);
 assert.ok(game.velocity.z<0);assert.equal(game.drainEvents().filter(e=>e.type==='paddle').length,1);
});
test('all ten levels complete through actual physics with a perfect test paddle',()=>{
 const game=new Brickstorm(),p=paddle();let frames=0,levels=new Set(),returns=0;
 while(!game.finished&&frames++<240000){
  levels.add(game.level);
  if(!game.launched&&!game.clearTime){p.position.set(0,1.7,.35);game.serve(p)}
  if(game.launched&&game.velocity.z>0){
   // Follow the ball; use deterministic alternating offsets to aim across the wall.
   const target=game.blocks.filter(b=>b.row===0).sort((a,b)=>Math.abs(a.x-game.ball.x)-Math.abs(b.x-game.ball.x))[0]||game.blocks[0];
   const distance=.20-target.z;
   const width=1.2*(game.power==='wide'?1.6:1),height=.72*(game.power==='wide'?1.4:1);
   p.position.x=game.ball.x-(target.x-game.ball.x)/distance*width/1.4;
   p.position.y=game.ball.y-(target.y-game.ball.y)/distance*height/1.2;
  }
  game.update(1/120,[p]);
  for(const e of game.drainEvents())if(e.type==='paddle')returns++;
 }
 assert.equal(game.finished,true,`Simulation timed out at level ${game.level+1}, ${game.blocks.length} bricks, ${returns} returns`);
 assert.equal(game.won,true);assert.equal(levels.size,10);assert.ok(game.score>10000);assert.ok(returns>10);
 console.log(`Ten-level physics run: ${frames} frames, ${returns} paddle returns, ${game.score} points`);
});
test('bonuses are caught and timed effects expire without stacking speed',()=>{
 const game=new Brickstorm(),p=paddle();game.serve(p);
 game.bonuses.push({id:1,kind:'slow',position:p.position.clone()});game.update(1/120,[p]);
 assert.equal(game.power,'slow');assert.ok(Math.abs(game.velocity.length()-4.2*.65)<1e-8);
 game.powerTime=.001;game.update(1/120,[p]);assert.equal(game.power,'');assert.ok(Math.abs(game.velocity.length()-4.2)<1e-8);
 game.bonuses.push({id:2,kind:'life',position:p.position.clone()});game.update(1/120,[p]);assert.equal(game.lives,5);
});
test('VR return assistance keeps distant shots within standing reach',()=>{
 const game=new Brickstorm();game.reachAssist=true;game.ball.set(2.8,4,-6);game.velocity.set(1,1,4);game.assistReturn();
 const seconds=(.35-game.ball.z)/game.velocity.z;
 const impact=game.ball.clone().addScaledVector(game.velocity,seconds);
 assert.ok(Math.abs(impact.x)<=.8);assert.ok(impact.y>=.95&&impact.y<=1.95);
});
