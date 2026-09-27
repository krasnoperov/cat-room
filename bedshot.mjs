import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
await page.goto('http://localhost:8123/index.html?t=15&paused=1&clean=1');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.evaluate(() => { const r = window.__room; r.view.zoom = 5; r.view.center.set(0.55, 0.1, 1.25); r.resize(); r.cat.pos.set(0.55, 0.15, 1.25); r.cat.yaw = 0.8; r.cat.state = 'sleep'; r.cat.decideT = 999; });
await page.waitForTimeout(4000);
await page.screenshot({ path: process.argv[2] });
await browser.close();
