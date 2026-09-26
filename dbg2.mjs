import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
page.on('pageerror', (e) => console.log('err', e.message));
await page.goto('http://localhost:8123/index.html?t=12&paused=1');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.evaluate(() => { const r = window.__room; r.addProp('bowls'); });
await page.waitForTimeout(2500);
await page.evaluate(() => { const r = window.__room; r.props.find((p) => p.type === 'bowls').food = 0; r.cat.hungry = true; r.cat.decideT = 0; });
for (let i = 0; i < 6; i++) {
  await page.waitForTimeout(2000);
  console.log(JSON.stringify(await page.evaluate(() => { const c = window.__room.cat; return [c.state, c.spot?.kind, c.path.length, c.pos.toArray().map((v) => +v.toFixed(2)), c.activity]; })));
}
await browser.close();
