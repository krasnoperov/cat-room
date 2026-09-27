// Force each moment's situation and check its condition holds, and that no condition throws.
import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errs = []; page.on('pageerror', (e) => errs.push(e.message));
await page.goto((process.env.BASE || 'http://localhost:8126/index.html') + '?t=16.5&paused=1&radio=0');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.evaluate(() => { const r = window.__room; for (const t of ['box', 'bowls', 'catTree', 'floorLamp', 'yarn', 'birdFeeder', 'windChime', 'easel']) r.addProp(t); r.addProp('candle', { host: 'Desk', x: -0.3, y: 0.755, z: -0.1 }); });
await page.waitForTimeout(4000);
const res = await page.evaluate(() => {
  const r = window.__room, c = r.cat, V = r.camera.position.constructor, out = {};
  const P = (t) => r.props.find((p) => p.type === t);
  const freeze = () => { c.decideT = 1e9; c.path = []; };
  const setups = {
    box: () => { c.inBox = true; c.state = 'sit'; },
    sunbath: () => { c.state = 'sleep'; r.clock.h = 16.5; c.pos.set(-1.72, 0.52, -0.3); },
    golden: () => { c.state = 'sleep'; c.pos.set(-1.72, 0.52, -0.3); r.clock.h = 18.8; },
    lantern: () => { c.state = 'sleep'; r.clock.h = 22; r.lantern.on = true; c.pos.set(-0.55, 0, -0.55); },
    rainwatch: () => { r.weather.rain = true; r.weather.k = 1; c.pos.set(-1.72, 0.52, -0.3); },
    birdwatch: () => { c.state = 'watch'; r.birds.forEach((b) => { b.state = 'perched'; }); },
    pounce: () => { c.state = 'pounce'; },
    yarn: () => { c.state = 'bat'; },
    dinner: () => { c.state = 'eat'; },
    mrrp: () => { c.state = 'meow'; },
    summit: () => { c.state = 'sleep'; c.spot = { kind: 'perch', p: c.pos.clone() }; c.pos.y = 0.9; },
    purr: () => { c.petT = 3; c.held = false; },
    lamp: () => { const l = P('floorLamp'); l.on = true; c.state = 'sleep'; c.pos.set(l.item.x + 0.3, 0, l.item.z); },
    lofi: () => { r.radio.on = true; r.radio.el = { paused: false }; r.clock.h = 23; c.state = 'sleep'; },
    mess: () => { r.papers.slice(0, 2).forEach((p) => { p.state = 'floor'; }); },
    leaf: () => { r.fallen.push({ t: 1, mesh: { position: new V(0, 0, 0) } }); },
    tea: () => { r.tea.temp = 25; },
    harvest: () => { r.lemon.growth = 1; },
    jungle: () => { r.monstera.growth = 1; },
    puddle: () => { r.weather.wet = 0.8; },
    gust: () => { r.roomEvents.gust = { t: 1e9, at: new V(0, 1, 0) }; },
    chime: () => { r.roomEvents.chime = { t: 1e9 }; r.windowState.open = true; },
    painter: () => { P('easel').painted = true; },
    'box-sun': () => { c.inBox = true; c.pos.set(-1.72, 0.52, -0.3); r.clock.h = 16.5; },
    storm: () => { r.clock.h = 23; r.weather.rain = true; r.weather.k = 1; r.radio.on = true; r.radio.el = { paused: false }; c.state = 'sleep'; r.lantern.on = true; },
    owl: () => { r.clock.h = 3; c.state = 'sit'; c.held = false; },
  };
  return { ids: r.MOMENTS.map((m) => m.id), setups: Object.keys(setups) };
});
const missing = res.ids.filter((id) => !res.setups.includes(id));
console.log('moments', res.ids.length, 'without a test setup:', missing.join(',') || 'none');
// run each setup in a fresh page state, let one frame settle the sun, then evaluate the condition and its focus
const results = [];
for (const id of res.ids.filter((x) => !process.env.ONLY || x === process.env.ONLY)) {
  await page.reload(); await page.waitForFunction(() => window.__room && window.__room.frames > 5);
  await page.evaluate(() => { const r = window.__room; for (const t of ['box', 'bowls', 'catTree', 'floorLamp', 'yarn', 'birdFeeder', 'windChime', 'easel']) r.addProp(t); r.addProp('candle', { host: 'Desk', x: -0.3, y: 0.755, z: -0.1 }); r.album.got = {}; r.album.busy = true; });
  await page.waitForTimeout(3000);
  const out = await page.evaluate((id) => {
    const r = window.__room, c = r.cat, V = r.camera.position.constructor;
    const P = (t) => r.props.find((p) => p.type === t);
    c.decideT = 1e9; c.path = [];
    const S = {
      box: () => { c.inBox = true; c.state = 'sit'; },
      sunbath: () => { c.state = 'sleep'; r.clock.h = 16.5; c.pos.set(-1.72, 0.52, -0.3); },
      golden: () => { c.state = 'sleep'; c.pos.set(-1.72, 0.52, -0.3); r.clock.h = 19.4; },
      lantern: () => { c.state = 'sleep'; r.clock.h = 22; r.lantern.on = true; r.lantern.auto = false; c.pos.set(-0.55, 0, -0.55); },
      rainwatch: () => { r.weather.rain = true; r.weather.k = 1; c.pos.set(-1.72, 0.52, -0.3); },
      birdwatch: () => { c.state = 'watch'; r.birds.forEach((b) => { b.state = 'perched'; }); },
      pounce: () => { c.state = 'pounce'; c.pounce = [c.pos.clone(), c.pos.clone()]; c.hop = 0; },
      yarn: () => { c.state = 'bat'; },
      dinner: () => { c.state = 'eat'; },
      mrrp: () => { c.state = 'meow'; },
      summit: () => { c.state = 'sleep'; c.spot = { kind: 'perch', p: c.pos.clone() }; c.pos.y = 0.9; },
      purr: () => { c.petT = 3; c.held = false; },
      lamp: () => { const l = P('floorLamp'); l.on = true; c.state = 'sleep'; c.pos.set(l.item.x + 0.3, 0, l.item.z); },
      lofi: () => { r.radio.on = true; r.radio.el = r.radio.el || { paused: false }; r.clock.h = 23; c.state = 'sleep'; },
      mess: () => { r.papers.slice(0, 2).forEach((p) => { p.state = 'floor'; }); },
      leaf: () => { r.fallen.push({ t: 1, mesh: { position: new V(0, 0, 0) } }); },
      tea: () => { r.tea.temp = 25; },
      harvest: () => { r.lemon.growth = 1; },
      jungle: () => { r.monstera.growth = 1; },
      puddle: () => { r.weather.wet = 0.8; },
      gust: () => { r.roomEvents.gust = { t: 1e9, at: new V(0, 1, 0) }; },
      chime: () => { r.roomEvents.chime = { t: 1e9 }; r.windowState.open = true; },
      painter: () => { P('easel').painted = true; },
      'box-sun': () => { c.inBox = true; c.pos.set(-1.72, 0.52, -0.3); r.clock.h = 16.5; },
      storm: () => { r.clock.h = 23; r.weather.rain = true; r.weather.k = 1; r.radio.on = true; r.radio.el = { paused: false }; c.state = 'sleep'; r.lantern.on = true; r.lantern.auto = false; },
      owl: () => { r.clock.h = 3; c.state = 'sit'; c.held = false; },
    };
    S[id]();
    return new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(() => {
      S[id](); // the frame loop may have moved things on; set it again, then read
      const m = r.MOMENTS.find((x) => x.id === id);
      let ok, err = null, focus = null;
      try { ok = !!m.test(); } catch (e) { err = e.message; }
      try { focus = m.focus ? !!m.focus() : 'cat'; } catch (e) { err = (err || '') + ' focus: ' + e.message; }
      res({ id, ok, err, focus, dbg: id === 'storm' ? JSON.stringify({ n: r.sun.night, k: r.weather.k, pl: r.radio.el && !r.radio.el.paused, on: r.radio.on, s: c.state, l: r.lantern.on }) : '' });
    })));
  }, id);
  results.push(out);
}
for (const r of results) console.log(r.ok ? 'PASS' : 'FAIL', r.id, r.err || '', r.focus === false ? '(no focus)' : '', r.dbg || '');
console.log(errs.slice(0, 5).join('\n') || 'no page errors');
await browser.close();
