import test from 'node:test';
import assert from 'node:assert/strict';
import {readBayouSave,recordBayouRun,SAVE_KEY} from './save.js';
test('Bayou scores are isolated from Brickstorm and survive a storage round trip',()=>{
 const store=new Map([['afterhours-v1','existing Brickstorm progress']]);
 const save=recordBayouRun({scores:[],trophy:false},{score:5800,round:2,won:true});
 store.set(SAVE_KEY,JSON.stringify(save));assert.deepEqual(readBayouSave({getItem:key=>store.get(key)}),save);
 assert.equal(store.get('afterhours-v1'),'existing Brickstorm progress');
});
test('invalid stored scores and unavailable storage recover safely',()=>{
 assert.deepEqual(readBayouSave({getItem:()=>{throw Error('blocked')}}),{scores:[],trophy:false});
 const save=readBayouSave({getItem:()=>JSON.stringify({scores:[{score:'bad',round:1},{score:100,round:9},{score:500,round:2}],trophy:'false'})});
 assert.equal(save.scores.length,1);assert.equal(save.trophy,false);
});
