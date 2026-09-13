import { Vector3, Quaternion } from 'three';
import { formation, LEVEL_NAMES } from './rules.js';
export { LEVEL_NAMES };
const identity = new Quaternion();
const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
export class Brickstorm {
  constructor() { this.restart(); }
  restart() {
    this.level = 0; this.score = 0; this.lives = 4; this.hits = 0;
    this.events = []; this.ball = new Vector3(0, 1.7, 0);
    this.velocity = new Vector3(); this.paused = false;
    this.finished = false; this.won = false; this.power = ''; this.powerTime = 0;
    this.loadLevel();
  }
  loadLevel() {
    this.blocks = formation(this.level).map((b, id) => ({...b, id, baseX: b.x}));
    this.bonuses = []; this.launched = false; this.clearTime = 0; this.elapsed = 0;
    this.power = ''; this.powerTime = 0;
    this.events.push({ type: 'level' });
  }
  get speed() { return (4.2 + this.level * .25) * (this.power === 'slow' ? .65 : 1); }
  serve(paddle) {
    if(this.finished || this.clearTime || this.launched) return;
    this.paused = false;
    this.ball.copy(paddle.position).add(new Vector3(0, 0, -.22));
    this.velocity.set(.12, .055, -1).normalize().multiplyScalar(this.speed);
    this.launched = true; this.events.push({type:'serve'});
  }
  update(dt, paddles) {
    if(this.finished || this.paused) return;
    if(this.clearTime > 0) {
      this.clearTime -= dt;
      if(this.clearTime <= 0) {
        if(this.level === 9) { this.finished = true; this.won = true; this.events.push({type:'win'}); }
        else { this.level++; this.loadLevel(); }
      }
      return;
    }
    this.elapsed += dt;
    if(this.powerTime > 0) {
      this.powerTime -= dt;
      if(this.powerTime <= 0) { this.power = ''; if(this.launched) this.velocity.setLength(this.speed); this.events.push({type:'powerend'}); }
    }
    for(const b of this.blocks) if(b.moving) b.x = b.baseX + Math.sin(this.elapsed*1.2)*.25;
    for(const b of this.bonuses) {
      b.position.z += dt * 2.1;
      if(paddles.some(p => p.position.distanceTo(b.position) < .85)) {
        this.power = b.kind; this.powerTime = 10;
        if(b.kind === 'life') this.lives = Math.min(6, this.lives+1);
        if(this.launched) this.velocity.setLength(this.speed);
        b.position.z = 10; this.events.push({type:'power',kind:b.kind});
      }
    }
    this.bonuses = this.bonuses.filter(b=>b.position.z < 2);
    if(!this.launched) { this.ball.copy(paddles[0].position).add(new Vector3(0,0,-.22)); return; }
    const steps = Math.ceil(dt / (1/180));
    for(let i=0;i<steps;i++) {
      const previous = this.ball.clone(); this.ball.addScaledVector(this.velocity, dt/steps);
      for(const axis of ['x','y']) {
        const lo=axis==='x'?-3:.35, hi=axis==='x'?3:4.6;
        if(this.ball[axis] < lo) { this.ball[axis]=lo; this.velocity[axis]=Math.abs(this.velocity[axis]); }
        if(this.ball[axis] > hi) { this.ball[axis]=hi; this.velocity[axis]=-Math.abs(this.velocity[axis]); }
      }
      if(this.ball.z < -7.3) { this.ball.z=-7.3; this.velocity.z=Math.abs(this.velocity.z); }
      for(const p of paddles) {
        const q=p.quaternion || identity, inverse=q.clone().invert();
        const a=previous.clone().sub(p.position).applyQuaternion(inverse);
        const b=this.ball.clone().sub(p.position).applyQuaternion(inverse);
        const width=(p.width||1.2)*(this.power==='wide'?1.6:1), height=(p.height||.72)*(this.power==='wide'?1.4:1);
        if(a.z < -.12 && b.z >= -.12 && Math.abs(b.x)<width/2+.1 && Math.abs(b.y)<height/2+.1) {
          this.velocity.set(b.x/width*1.4, b.y/height*1.2, -1).applyQuaternion(q);
          this.velocity.z = -Math.max(.65,Math.abs(this.velocity.z));
          this.velocity.normalize().multiplyScalar(this.speed);
          this.ball.copy(p.position).add(new Vector3(b.x,b.y,-.15).applyQuaternion(q));
          this.events.push({type:'paddle'}); break;
        }
      }
      for(const b of this.blocks) {
        if(Math.abs(this.ball.x-b.x)<.365 && Math.abs(this.ball.y-b.y)<.31 && Math.abs(this.ball.z-b.z)<.29) {
          if(Math.abs(previous.x-b.x)>=.365) this.velocity.x*=-1;
          else if(Math.abs(previous.y-b.y)>=.31) this.velocity.y*=-1;
          else this.velocity.z*=-1;
          this.ball.copy(previous);
          if(--b.hp<=0) this.breakBlock(b);
          else this.events.push({type:'armor',id:b.id});
          break;
        }
      }
      if(this.ball.z > 1.8) {
        this.lives--; this.launched=false; this.events.push({type:'miss'});
        if(this.lives===0) { this.finished=true; this.events.push({type:'lose'}); }
        return;
      }
      if(this.clearTime) return;
    }
  }
  breakBlock(b) {
    this.blocks=this.blocks.filter(block=>block!==b); this.score+=100; this.hits++;
    this.events.push({type:'hit',id:b.id,position:new Vector3(b.x,b.y,b.z),row:b.row});
    if(this.hits%5===0) this.bonuses.push({id:this.hits,kind:['wide','slow','life'][(this.hits/5-1)%3],position:new Vector3(b.x,b.y,b.z)});
    if(!this.blocks.some(block=>block.row===0)) {
      this.score+=this.blocks.length*100+500*(this.level+1);
      this.events.push({type:'collapse',blocks:this.blocks.map(block=>({...block}))});
      this.blocks=[]; this.clearTime=2.5; this.launched=false;
    }
  }
  drainEvents() { const events=this.events; this.events=[]; return events; }
}
