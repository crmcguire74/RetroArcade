export const LEVEL_NAMES=['First light','The staircase','Twin towers','Diamond district','Cross current','The gate','Skyline','Moving pictures','Last defense','After the storm'];
export function formation(level){
 const blocks=[];
 for(let r=0;r<5;r++)for(let c=0;c<9;c++){
 const x=(c-4)*.61,y=.8+r*.55;
 const include=[true,c<=r+3,Math.abs(c-4)>1,Math.abs(c-4)+Math.abs(r-2)<5,r===2||c%2===0,r>2||c<2||c>6,r<2+c%3,(c+r)%2===0,r===0||c%2===0,true][level];
 if(include) blocks.push({x,y,z:-6-r*.09,hp:level>7&&r>2?2:1,moving:level===7||level===4&&r===2,row:r});
 }
 return blocks;
}
export function reflectPaddle(vx,vy,vz,offsetX,offsetY,speed){
 const x=Math.max(-.8,Math.min(.8,offsetX))*.75+vx*.12;
 const y=Math.max(-.8,Math.min(.8,offsetY))*.75+vy*.12;
 const z=-Math.max(.65,Math.abs(vz)); const length=Math.hypot(x,y,z);
 return {x:x/length*speed,y:y/length*speed,z:z/length*speed};
}
export function readSave(storage){try{const v=JSON.parse(storage.getItem('afterhours-v1'));return {scores:Array.isArray(v?.scores)?v.scores.filter(s=>Number.isFinite(s.score)&&s.score>=0).slice(0,10):[],tickets:Math.max(0,Number(v?.tickets)||0),trophy:!!v?.trophy}}catch{return {scores:[],tickets:0,trophy:false}}}
