import test from 'node:test';
import assert from 'node:assert/strict';
import {BayouCrossing,CELL,LANES,laneObjects} from './engine.js';

const advance=(game,seconds,dt=1/60)=>{for(let t=0;t<seconds-1e-9;t+=dt)game.update(Math.min(dt,seconds-t))};
const started=()=>{const game=new BayouCrossing();game.start();game.drainEvents();return game};

test('hops require start, reject diagonals and repeats, and stop at the bank bounds',()=>{
 const game=new BayouCrossing();
 assert.equal(game.hopDirection(1,0),false);game.start();
 assert.equal(game.hopDirection(1,1),false);
 assert.equal(game.hopDirection(0,-1),false);
 for(let i=0;i<4;i++){
  assert.equal(game.hopDirection(1,0),true);
  assert.equal(game.hopDirection(1,0),false);
  advance(game,.18);
 }
 assert.equal(game.frog.x,4*CELL);assert.equal(game.hopDirection(1,0),false);
});

test('pause freezes a hop, timer and moving world',()=>{
 const game=started();game.hopDirection(1,0);advance(game,.06);game.paused=true;
 const before=JSON.stringify({hop:game.hop,time:game.time,timer:game.timer});
 advance(game,2);assert.equal(JSON.stringify({hop:game.hop,time:game.time,timer:game.timer}),before);
 assert.equal(game.hopDirection(-1,0),false);game.paused=false;advance(game,.12);
 assert.equal(game.frog.x,CELL);
});

test('a vehicle strikes mid-hop and removes only one life during recovery',()=>{
 const game=started();game.time=1.75;game.hopDirection(0,1);advance(game,.18);
 assert.equal(game.lives,2);assert.equal(game.hop,null);
 assert.ok(game.drainEvents().some(e=>e.type==='death'&&e.reason==='traffic'));
 advance(game,.5);assert.equal(game.lives,2);advance(game,.6);assert.equal(game.frog.row,0);
});

test('the first immediate forward hop is safe and diving turtles give advance warning',()=>{
 const game=started();game.hopDirection(0,1);advance(game,.18);
 assert.equal(game.lives,3);assert.equal(game.frog.row,1);
 const objects=laneObjects(LANES[8],0);
 assert.equal(objects[0].warning,true);assert.equal(objects[0].submerged,false);
});

test('logs carry the frog consistently at 30 and 120 frames per second',()=>{
 const run=dt=>{const game=started();game.frog={row:7,x:0};advance(game,1,dt);return game};
 const a=run(1/30),b=run(1/120);
 assert.equal(a.lives,3);assert.ok(Math.abs(a.frog.x+.8)<1e-8);
 assert.ok(Math.abs(a.frog.x-b.frog.x)<1e-8);assert.ok(Math.abs(a.timer-b.timer)<1e-8);
});

test('missing platforms and submerged turtles cause a water death',()=>{
 const game=started();game.frog={row:7,x:2.3};game.update(1/60);
 assert.equal(game.lives,2);assert.ok(game.drainEvents().some(e=>e.reason==='water'));
 const turtle=started();turtle.time=1;
 const platform=laneObjects(LANES[8],turtle.time).find(o=>Math.abs(o.x)<3);
 assert.equal(platform.submerged,true);turtle.frog={row:8,x:platform.x};turtle.update(1/60);
 assert.equal(turtle.lives,2);
});

test('being carried beyond the bank loses a life',()=>{
 const game=started();game.frog={row:9,x:4*CELL+.34};
 // Place the phase so that a supporting log carries toward the right boundary.
 game.time=4.4;advance(game,.05);
 assert.equal(game.lives,2);assert.ok(game.drainEvents().some(e=>e.reason==='swept'));
});

test('homes award points once, reject occupied pads, and reset to the safe bank',()=>{
 const game=started();game.frog={row:12,x:0};game.update(1/60);
 assert.deepEqual(game.homes,[2]);assert.ok(game.score>=348);
 advance(game,.7);assert.equal(game.frog.row,0);
 const score=game.score;game.frog={row:12,x:0};game.update(1/60);
 assert.equal(game.score,score);assert.equal(game.lives,2);
});

test('five homes advance the round; the third complete round wins',()=>{
 const game=started();
 for(let round=0;round<3;round++){
  assert.equal(game.round,round);
  for(const x of [-4,-2,0,2,4]){
   game.frog={row:12,x:x*CELL};game.update(1/60);
   if(x!==4)advance(game,.7);
  }
  if(round<2){assert.ok(game.roundDelay>0);assert.equal(game.hopDirection(0,1),false);advance(game,2.1)}
 }
 assert.equal(game.finished,true);assert.equal(game.won,true);assert.equal(game.lives,3);
 const score=game.score;advance(game,3);assert.equal(game.score,score);
 game.restart();assert.equal(game.started,false);assert.equal(game.finished,false);assert.equal(game.score,0);assert.deepEqual(game.homes,[]);
});

test('timer expires once and the last life ends the run',()=>{
 const game=started();game.lives=1;game.timer=.01;advance(game,.1);
 assert.equal(game.lives,0);assert.equal(game.finished,true);assert.equal(game.won,false);
 assert.equal(game.drainEvents().filter(e=>e.type==='lose').length,1);
 assert.equal(game.hopDirection(0,1),false);
});

test('invalid elapsed time never corrupts the state',()=>{
 const game=started();const time=game.time;
 for(const dt of [NaN,Infinity,-1,0])game.update(dt);
 assert.equal(game.time,time);assert.equal(game.lives,3);
});
