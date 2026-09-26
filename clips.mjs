import { spawn } from 'node:child_process';
const OUT = 'videos/cat-room-launch/capture/assets/clips';
const L = "r.move('Lemon tree',1.6,-0.55,0);";
const cam = (z, x, y, zz) => `r.view.zoom=${z}; r.view.center.set(${x},${y},${zz}); r.resize();`;
const clips = [
  ['c01-morning-wide', 't=9.3&speed=0.1', 150, `const r=window.__room; ${cam(1.5, 0, 0.9, 0)}`, `r.view.zoom=1.5+i*0.0016; r.resize();`],
  ['c02-cat-sunbeam', 't=16.4&speed=0.02', 150, `const r=window.__room; ${cam(4.6, -1.7, 0.62, -0.3)}`, `if(i===70) r.items.find(o=>o.name==='Cat').click(); r.view.zoom=4.6+i*0.004; r.resize();`],
  ['c03-box', 't=11&speed=0.02', 210, `const r=window.__room; ${L} r.addProp('box',{x:0.35,z:0.55}); r.cat.pos.set(1.25,0,1.3); r.cat.yaw=-2.4; r.cat.state='sit'; r.cat.decideT=1.2; ${cam(3.9, 0.3, 0.12, 0.45)}`, ``],
  ['c04-yarn', 't=12&speed=0.02', 210, `const r=window.__room; ${L} Math.random=()=>0.12; r.addProp('yarn',{x:0.3,z:0.45}); r.cat.pos.set(0.9,0,0.95); r.cat.yaw=-2.3; r.cat.state='sit'; r.cat.stateT=0; r.cat.decideT=0.3; ${cam(4.3, 0.3, 0.12, 0.35)}`, `const y=r.props.find(p=>p.type==='yarn'); if(i===2&&y&&y.vel) y.vel.set(-0.5,0,0.25);`],
  ['c05-laser', 't=13&speed=0.02', 210, `const r=window.__room; ${L} r.cat.pos.set(0.2,0,0.3); r.cat.state='sit'; r.laser.on=true; ${cam(3.6, 0.2, 0.1, 0.25)}`, `const V=r.camera.position.constructor; const a=i/210*Math.PI*2*1.4; const x=0.35+Math.sin(a)*0.6, z=0.45+Math.sin(a*2)*0.3; const [sx,sy]=r.project([x,0,z]); document.getElementById('gl').dispatchEvent(new PointerEvent('pointermove',{clientX:sx,clientY:sy,bubbles:true}));`],
  ['c06-birds', 't=12.5&speed=0.02', 180, `const r=window.__room; r.addProp('birdFeeder'); ${cam(4.0, -1.95, 1.3, -0.6)}`, `if(i===15) r.birds.forEach(b=>{b.state='arriving'; b.t=-b.i*0.7; b.stay=99;});`],
  ['c07-rain', 't=14.5&speed=0.02&rain=1&open=1', 150, `const r=window.__room; ${cam(2.3, -1.35, 0.85, -0.35)}`, `r.view.zoom=2.3+i*0.003; r.resize();`],
  ['c08-dusk-radio', 't=19.7&speed=0.22', 180, `const r=window.__room; r.radio.on=true; r.addProp('floorLamp',{x:1.62,z:-1.15}); r.addProp('candle',{host:'Desk',x:-0.3,y:0.755,z:-0.1}); ${cam(1.6, 0.55, 0.95, -0.9)}`, `const l=r.props.find(p=>p.type==='floorLamp'); if(l) l.on=r.clock.h>20.1; r.view.center.x=0.55-i*0.002;`],
  ['c09-timelapse', 't=9&speed=2.6', 150, `const r=window.__room; ${cam(1.5, 0, 0.9, 0)}`, ``],
  ['c10-night-turn', 't=22.2&speed=0.01&rain=0', 180, `const r=window.__room; r.radio.on=true; r.addProp('box',{x:0.9,z:0.65}); r.addProp('floorLamp',{x:1.62,z:-1.15}); r.addProp('catTree',{x:-0.2,z:1.35}); r.addProp('windChime'); ${cam(1.0, 0, 0.9, 0)}`, `const l=r.props.find(p=>p.type==='floorLamp'); if(l) l.on=true; const a=(45+i*0.36)*Math.PI/180; r.view.angle=a; r.view.target=a;`],
  ['c11-ui-dresser', 'ui=1&t=16.6&speed=0.02&radio=0', 150, `const r=window.__room; ${cam(1.2, 0, 0.9, 0)}`, `if(i===35) r.addProp('catTree',{x:1.2,z:0.95}); if(i===70) r.addProp('box',{x:0.3,z:0.6}); if(i===100) r.addProp('floorLamp',{x:1.62,z:-1.15});`],
];
const only = process.argv.slice(2);
const todo = clips.filter((c) => !only.length || only.includes(c[0]));
let running = 0, idx = 0;
await new Promise((done) => {
  const next = () => {
    if (idx >= todo.length && running === 0) return done();
    while (running < 3 && idx < todo.length) {
      const [name, q, n, setup, pf] = todo[idx++];
      running++;
      const p = spawn('node', ['film2.mjs', `${OUT}/${name}.mp4`, q, String(n), setup, pf], { stdio: ['ignore', 'pipe', 'pipe'] });
      p.stdout.on('data', (d) => process.stdout.write(`[${name}] ${d}`));
      p.stderr.on('data', (d) => process.stdout.write(`[${name}] ERR ${d}`));
      p.on('close', (code) => { running--; console.log(`[${name}] exit ${code}`); next(); });
    }
  };
  next();
});
