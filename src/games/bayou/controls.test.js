import test from 'node:test';
import assert from 'node:assert/strict';
import {StickHops,keyboardHop} from './controls.js';
test('keyboard arrows and WASD produce one hop per press',()=>{
 assert.deepEqual(keyboardHop('ArrowUp'),[0,1]);assert.deepEqual(keyboardHop('KeyA'),[-1,0]);
 assert.equal(keyboardHop('ArrowUp',true),null);assert.equal(keyboardHop('Space'),null);
});
test('VR stick jitter does not repeat hops, including diagonal changes while held',()=>{
 const stick=new StickHops();assert.equal(stick.sample(.2,.2),null);
 assert.deepEqual(stick.sample(.9,.4),[1,0]);
 for(let i=0;i<100;i++)assert.equal(stick.sample(.75,-.85),null);
 assert.equal(stick.sample(.1,.1),null);assert.deepEqual(stick.sample(.1,-.85),[0,1]);
 stick.reset();assert.deepEqual(stick.sample(-.9,.1),[-1,0]);assert.equal(stick.sample(NaN,0),null);
});
