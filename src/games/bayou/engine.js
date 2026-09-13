// Independent deterministic crossing simulation. No rendering, DOM, or provider dependencies.
export const CELL = 1.3;
export const HOME_COLUMNS = [-4,-2,0,2,4];
export const HOP_SECONDS = .18;
export const ROW_COUNT = 13;
export const LANES = [
  {row:0,type:'bank'},
  {row:1,type:'road',speed:1.45,length:1.8,spacing:5.4,offset:0},
  {row:2,type:'road',speed:-2.1,length:2.5,spacing:6.8,offset:2.7},
  {row:3,type:'road',speed:1.2,length:3.0,spacing:7.8,offset:1.1},
  {row:4,type:'road',speed:-1.85,length:1.8,spacing:5.7,offset:3.8},
  {row:5,type:'road',speed:2.4,length:2.0,spacing:6.6,offset:1.9},
  {row:6,type:'bank'},
  {row:7,type:'log',speed:-.8,length:3.2,spacing:4.6,offset:0},
  {row:8,type:'turtle',speed:.65,length:2.7,spacing:4.4,offset:1.8},
  {row:9,type:'log',speed:1.0,length:3.7,spacing:5.1,offset:.9},
  {row:10,type:'turtle',speed:-.85,length:3.0,spacing:4.5,offset:2.4},
  {row:11,type:'log',speed:.75,length:3.4,spacing:4.8,offset:.4},
  {row:12,type:'homes'}
];
const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
export function laneObjects(lane,time,round=0){
  if(!lane.speed)return [];
  const speed=lane.speed*(1+round*.18), offset=lane.offset+time*speed;
  const phase=((offset%lane.spacing)+lane.spacing)%lane.spacing;
  return Array.from({length:9},(_,i)=>({id:`${lane.row}:${i}`,x:phase+(i-4)*lane.spacing,length:lane.length,speed,submerged:lane.type==='turtle'&&((time+lane.row*1.17)%12)>10.2}));
}
export class BayouCrossing {
 constructor(){this.restart()}
 restart(){
  this.round=0;this.score=0;this.lives=3;this.homes=[];this.time=0;
  this.paused=false;this.started=false;this.finished=false;this.won=false;
  this.events=[];this.recovery=0;this.roundDelay=0;this.resetFrog();
 }
 resetFrog(){this.frog={x:0,row:0};this.hop=null;this.timer=75;this.furthest=0;this.events.push({type:'spawn'})}
 start(){if(!this.finished){this.started=true;this.paused=false}}
 hopDirection(dx,dy){
  if(!this.started||this.paused||this.finished||this.hop||this.recovery>0||this.roundDelay>0)return false;
  if(!Number.isInteger(dx)||!Number.isInteger(dy)||Math.abs(dx)+Math.abs(dy)!==1)return false;
  const to={x:this.frog.x+dx*CELL,row:this.frog.row+dy};
  if(to.row<0||to.row>=ROW_COUNT||Math.abs(to.x)>CELL*4+.02)return false;
  this.hop={from:{...this.frog},to,elapsed:0};this.events.push({type:'hop',dx,dy});return true;
 }
 get visualFrog(){
  if(!this.hop)return {...this.frog,height:0};
  const t=clamp(this.hop.elapsed/HOP_SECONDS,0,1);
  return {x:this.hop.from.x+(this.hop.to.x-this.hop.from.x)*t,row:this.hop.from.row+(this.hop.to.row-this.hop.from.row)*t,height:Math.sin(t*Math.PI)*.3};
 }
 update(dt){
  if(!Number.isFinite(dt)||dt<=0||this.paused||this.finished||!this.started)return;
  // Substeps preserve moving-platform carries and collision behavior under slow frames.
  for(let remain=Math.min(dt,.5);remain>1e-9;){const step=Math.min(remain,1/120);remain-=step;this.tick(step);if(this.finished)break}
 }
 tick(dt){
  this.time+=dt;
  if(this.recovery>0){this.recovery-=dt;if(this.recovery<=0)this.resetFrog();return}
  if(this.roundDelay>0){this.roundDelay-=dt;if(this.roundDelay<=0){this.round++;this.homes=[];this.resetFrog();this.events.push({type:'round',round:this.round})}return}
  this.timer-=dt;
  if(this.timer<=0){this.die('time');return}
  if(this.hop){
   this.hop.elapsed+=dt;
   // Road vehicles can hit during a jump: jumping is movement, not invulnerability.
   const p=this.visualFrog;
   for(const lane of LANES.filter(l=>l.type==='road'))if(Math.abs(p.row-lane.row)<.37&&this.roadHit(p.x,lane)){this.die('traffic');return}
   if(this.hop.elapsed+1e-9<HOP_SECONDS)return;
   this.frog={...this.hop.to};this.hop=null;
   if(this.frog.row>this.furthest){this.score+=(this.frog.row-this.furthest)*10;this.furthest=this.frog.row}
   this.events.push({type:'land'});
  }
  const lane=LANES[this.frog.row];
  if(lane.type==='road'&&this.roadHit(this.frog.x,lane)){this.die('traffic');return}
  if(lane.type==='log'||lane.type==='turtle'){
   const support=laneObjects(lane,this.time,this.round).find(o=>!o.submerged&&Math.abs(this.frog.x-o.x)<o.length/2-.13);
   if(!support){this.die('water');return}
   this.frog.x+=support.speed*dt;
   if(Math.abs(this.frog.x)>CELL*4+.35){this.die('swept');return}
  }
  if(lane.type==='homes')this.reachHome();
 }
 roadHit(x,lane){return laneObjects(lane,this.time,this.round).some(o=>Math.abs(x-o.x)<o.length/2+.2)}
 reachHome(){
  const index=HOME_COLUMNS.findIndex(col=>Math.abs(this.frog.x-col*CELL)<.45*CELL);
  if(index<0||this.homes.includes(index)){this.die('closed-home');return}
  this.homes.push(index);this.score+=200+Math.ceil(this.timer)*2;this.events.push({type:'home',index});
  if(this.homes.length===5){
   this.score+=1000*(this.round+1);
   if(this.round===2){this.finished=true;this.won=true;this.events.push({type:'win'});return}
   this.roundDelay=2;this.events.push({type:'round-clear'});
  }else{this.recovery=.6;this.events.push({type:'return-to-start'})}
 }
 die(reason){if(this.finished||this.recovery>0)return;this.lives--;this.hop=null;this.events.push({type:'death',reason});if(this.lives<=0){this.finished=true;this.events.push({type:'lose'})}else this.recovery=1}
 drainEvents(){const events=this.events;this.events=[];return events}
}
