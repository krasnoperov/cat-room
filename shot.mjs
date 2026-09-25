// usage: node shot.mjs out.png "query" [w h] [waitMs]
import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const [out, q = '', w = '1440', h = '900', wait = '2500', script = ''] = process.argv.slice(2);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
const logs = [];
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') logs.push(m.type() + ': ' + m.text()); });
page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
await page.goto('http://localhost:8123/index.html?' + q);
await page.waitForFunction(() => window.__room && window.__room.frames > 5, null, { timeout: 60000 }).catch(() => logs.push('no frames'));
if (script) await page.evaluate(script);
await page.waitForTimeout(+wait);
await page.screenshot({ path: out });
const fps = await page.evaluate(() => window.__room && window.__room.frames).catch(() => null);
console.log('frames', fps, logs.slice(0, 12).join('\n'));
await browser.close();
