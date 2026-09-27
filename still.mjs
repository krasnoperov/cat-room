// node still.mjs out.png "query" "setupJS" [w h ticks]  (fixed-step: renders only on tick; screenshot keeps the HTML overlay)
import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const [out, q, setup = '', w = '1280', h = '720', ticks = '20'] = process.argv.slice(2);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
page.on('pageerror', (e) => console.log('pageerror', e.message));
await page.goto((process.env.BASE || 'http://localhost:8128/index.html') + '?fixed=1&clean=1&' + q);
await page.waitForFunction(() => window.__room && window.__room.frames >= 2, null, { timeout: 90000 });
await page.waitForTimeout(3000);
await page.evaluate(([s, n]) => { const r = window.__room; if (s) (new Function('r', s))(r); r.tick(+n); }, [setup, ticks]);
await page.screenshot({ path: out, timeout: 120000 });
await browser.close();
