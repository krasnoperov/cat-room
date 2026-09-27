import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
await page.goto('http://localhost:8123/index.html?t=21.5&paused=1&clean=1');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.evaluate(() => { const r = window.__room; r.lantern.on = false; r.lantern.auto = false; r.cat.pos.set(0.9, 0, 0.7); r.cat.state = 'sit'; r.cat.decideT = 0; });
for (let i = 0; i < 6; i++) { await page.waitForTimeout(4000); console.log(JSON.stringify(await page.evaluate(() => { const c = window.__room.cat; return [c.state, c.activity, c.pos.toArray().map((v) => +v.toFixed(2))]; }))); }
await browser.close();
