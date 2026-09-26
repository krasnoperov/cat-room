import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
page.on('pageerror', (e) => console.log('err', e.message));
await page.goto('http://localhost:8123/index.html?fixed=1&clean=1&t=11&speed=0.02');
await page.waitForFunction(() => window.__room && window.__room.frames >= 2);
await page.waitForTimeout(2000);
await page.evaluate(() => { const r = window.__room; r.move('Lemon tree',1.6,-0.55,0); r.addProp('box',{x:0.35,z:0.55}); r.cat.pos.set(1.1,0,1.2); r.cat.state='sit'; r.cat.decideT=0.5; });
await page.waitForTimeout(3000);
let last = '';
for (let f = 0; f < 300; f++) {
  const s = await page.evaluate(() => { const r = window.__room; r.tick(1); const c = r.cat; return `${c.state}|${c.spot?.kind}|inBox=${c.inBox}|${c.pos.toArray().map((v) => v.toFixed(2)).join(',')}`; });
  const key = s.split('|').slice(0, 3).join('|');
  if (key !== last) { console.log(f, s); last = key; }
}
await browser.close();
