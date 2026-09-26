import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const S = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errs = []; page.on('pageerror', (e) => errs.push(e.message)); page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto((process.env.BASE || 'http://localhost:8123/index.html') + '?t=18.9&grow=0.9');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
const R = (f) => page.evaluate(f);
await R(() => { const r = window.__room; for (const t of ['box', 'bowls', 'catTree', 'floorLamp', 'yarn', 'wateringCan', 'birdFeeder', 'windChime', 'easel']) r.addProp(t); r.addProp('candle', { host: 'Desk', x: -0.3, y: 0.755, z: -0.1 }); });
await page.waitForTimeout(4000);
console.log('props', await R(() => window.__room.props.map((p) => p.type + (p.model ? '' : '(no model)')).join(', ')));
await page.screenshot({ path: `${S}/props-all.png` });
// box pulls the cat in
await R(() => { window.__room.cat.decideT = 0; });
await page.waitForTimeout(9000);
console.log('cat', await R(() => [window.__room.cat.state, window.__room.cat.activity, window.__room.cat.spot?.kind]));
// dinner time
await R(() => { const r = window.__room; r.clock.h = 18.99; r.cat.lastMeal = -1; });
await page.waitForTimeout(9000);
console.log('dinner', await R(() => [window.__room.cat.state, window.__room.cat.activity, window.__room.props.find((p) => p.type === 'bowls').food.toFixed(2)]));
await page.screenshot({ path: `${S}/props-dinner.png` });
// empty bowls -> meow
await R(() => { const r = window.__room; r.props.find((p) => p.type === 'bowls').food = 0; r.cat.hungry = true; r.cat.state = 'sit'; r.cat.decideT = 0; });
await page.waitForTimeout(9000);
console.log('empty', await R(() => [window.__room.cat.state, window.__room.cat.activity]));
await page.screenshot({ path: `${S}/props-meow.png` });
// laser
await R(() => { const r = window.__room; r.props.find((p) => p.type === 'bowls').food = 1; r.cat.hungry = false; r.laser.on = true; r.laser.visible = true; r.laser.target = { x: 0.8, y: 0, z: 0.9, clone() { return { ...this }; } }; });
await page.waitForTimeout(3000);
console.log('laser', await R(() => [window.__room.cat.state, window.__room.cat.activity, window.__room.cat.pos.toArray().map((v) => +v.toFixed(2))]));
await R(() => { window.__room.laser.on = false; });
// easel paints
await R(() => { const r = window.__room; const e = r.props.find((p) => p.type === 'easel'); e.item.click(); });
await page.waitForTimeout(800);
console.log('easel painted', await R(() => window.__room.props.find((p) => p.type === 'easel').painted));
// watering
await R(() => { const r = window.__room; const c = r.props.find((p) => p.type === 'wateringCan'); c.item.click(); });
console.log('water mode', await R(() => window.__room.water.mode));
await page.screenshot({ path: `${S}/props-end.png` });
console.log(errs.slice(0, 8).join('\n') || 'no errors');
await browser.close();
