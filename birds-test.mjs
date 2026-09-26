import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const S = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1000, height: 760 } });
page.on('pageerror', (e) => console.log('err', e.message));
await page.goto('http://localhost:8123/index.html?fixed=1&clean=1&t=12.5');
await page.waitForFunction(() => window.__room && window.__room.frames >= 2);
await page.waitForTimeout(2000);
await page.evaluate(() => { const r = window.__room; r.addProp('birdFeeder'); r.view.zoom = 3.4; r.view.center.set(-1.9, 1.35, -0.5); r.resize(); });
await page.waitForTimeout(3000);
await page.evaluate(() => { const r = window.__room; r.tick(10); r.birds.forEach((b) => { b.state = 'arriving'; b.t = -b.i * 0.7; b.stay = 99; }); });
// sample the birds' paths against the casement sweep (x > -2.66 near the window is inside it)
let worst = -9;
for (let f = 0; f < 90; f++) {
  const xs = await page.evaluate(() => { const r = window.__room; r.tick(1); return r.birds.map((b) => b.group.position.x); });
  worst = Math.max(worst, ...xs);
  if (f === 20 || f === 60) await page.screenshot({ path: `${S}/birds-${f}.png` });
}
console.log('closest a bird came to the wall: x =', worst.toFixed(2), '(casements reach to about -2.6)');
await browser.close();
