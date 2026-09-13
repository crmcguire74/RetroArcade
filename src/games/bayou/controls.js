const keyboard={ArrowUp:[0,1],KeyW:[0,1],ArrowDown:[0,-1],KeyS:[0,-1],ArrowLeft:[-1,0],KeyA:[-1,0],ArrowRight:[1,0],KeyD:[1,0]};
export function keyboardHop(code,repeat=false){return repeat?null:keyboard[code]||null}
// Require a return to center between moves. No frame-rate-dependent auto-repeat.
export class StickHops{
 constructor(){this.latched=false}
 reset(){this.latched=false}
 sample(x,y){
  if(!Number.isFinite(x)||!Number.isFinite(y))return null;
  if(Math.hypot(x,y)<.3){this.latched=false;return null}
  if(this.latched||Math.max(Math.abs(x),Math.abs(y))<.65)return null;
  this.latched=true;
  return Math.abs(x)>Math.abs(y)?[Math.sign(x),0]:[0,-Math.sign(y)];
 }
}
