export const SAVE_KEY='afterhours-bayou-v1';
export function readBayouSave(storage){
 try{const v=JSON.parse(storage.getItem(SAVE_KEY));return {scores:Array.isArray(v?.scores)?v.scores.filter(s=>Number.isFinite(s.score)&&s.score>=0&&Number.isInteger(s.round)&&s.round>=1&&s.round<=3).sort((a,b)=>b.score-a.score).slice(0,10):[],trophy:v?.trophy===true}}catch{return {scores:[],trophy:false}}
}
export function recordBayouRun(save,game){
 const scores=game.score>0?[...save.scores,{score:game.score,round:game.round+1,won:game.won}]:[...save.scores];
 return {scores:scores.sort((a,b)=>b.score-a.score).slice(0,10),trophy:save.trophy||game.won};
}
