import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const S = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 700, height: 560 } });
const errs = []; page.on('pageerror', (e) => errs.push(e.message));
await page.goto('http://localhost:8123/index.html?t=15&paused=1&clean=1&fixed=1');
await page.waitForFunction(() => window.__room && window.__room.frames >= 2);
await page.waitForTimeout(2500);
// put the cat on the floor and send it to the seat, then film the hop frame by frame
await page.evaluate(() => {
  const r = window.__room, c = r.cat;
  c.pos.set(-0.6, 0, 0.1); c.state = 'sit'; c.inBox = false; c.landing = null;
  r.view.zoom = 3.4; r.view.center.set(-1.3, 0.35, -0.2); r.resize();
  r.goTo({ p: new r.camera.position.constructor(-1.72, 0.52, -0.3), seat: true, kind: 'rest', hops: [new r.camera.position.constructor(-1.19, 0, -0.3)] });
});
let n = 0, overlaps = 0;
for (let f = 0; f < 150; f++) {
  const st = await page.evaluate(() => { window.__room.tick(1); const c = window.__room.cat; return [c.state, +c.pos.x.toFixed(3), +c.pos.y.toFixed(3), +c.pos.z.toFixed(3)]; });
  // the cat's chest must never be inside the seat box below its top
  const [state, x, y] = st;
  if (x < -1.45 + 0.02 && y < 0.5 && state !== 'walk') overlaps++;
  if (state === 'hop' && n < 6 && f % 2 === 0) { await page.screenshot({ path: `${S}/hop-${n}.png` }); n++; }
}
console.log('frames inside the seat below its top:', overlaps, 'final', JSON.stringify(await page.evaluate(() => { const c = window.__room.cat; return [c.state, c.pos.toArray().map((v) => +v.toFixed(2))]; })));
console.log(errs.join('\n') || 'no errors');
await browser.close();
