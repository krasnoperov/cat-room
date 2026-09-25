import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const S = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const logs = [];
page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
page.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
await page.goto('http://localhost:8123/index.html?t=16.5&paused=1');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
const P = (v) => page.evaluate((v) => window.__room.project(v), v);
const state = () => page.evaluate(() => { const r = window.__room; return { open: r.windowState.open, lantern: r.lantern.on, tea: Math.round(r.tea.temp), lemon: [r.get('Lemon tree').x, r.get('Lemon tree').z], lit: r.sunlit({ x: r.get('Lemon tree').x, y: 0.85, z: r.get('Lemon tree').z }), books: r.items.length }; });
console.log('start', JSON.stringify(await state()));
// hover the window seat pillow region -> tooltip
let [x, y] = await P([-2.0, 1.4, -0.4]);
await page.mouse.move(x, y); await page.waitForTimeout(300);
console.log('tip over window:', await page.$eval('#tip', (e) => e.hidden ? '(hidden)' : e.textContent));
await page.mouse.down(); await page.mouse.up(); await page.waitForTimeout(300);
[x, y] = await P([-0.55, 1.98, -0.55]);
await page.mouse.move(x, y); await page.mouse.down(); await page.mouse.up(); await page.waitForTimeout(300);
// drag the lemon tree toward the sun patch
const from = await P([1.55, 0.5, 1.4]);
const to = await P([-0.7, 0.5, -0.4]);
await page.mouse.move(...from); await page.mouse.down();
for (let i = 1; i <= 12; i++) await page.mouse.move(from[0] + (to[0] - from[0]) * i / 12, from[1] + (to[1] - from[1]) * i / 12);
await page.mouse.up(); await page.waitForTimeout(400);
console.log('after', JSON.stringify(await state()));
await page.screenshot({ path: S });
console.log(logs.join('\n'));
await browser.close();
