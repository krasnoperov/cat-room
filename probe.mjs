import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const [dir, ...ts] = process.argv.slice(2);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
page.on('pageerror', (e) => console.log('pageerror', e.message));
await page.goto('http://localhost:8128/index.html?fixed=1&clean=1&breakdown=1&paused=1&radio=0&t=16.6');
await page.waitForFunction(() => window.__room && window.__room.frames >= 2, null, { timeout: 120000 });
await page.addScriptTag({ path: 'videos/breakdown/timeline.js' });
await page.waitForTimeout(3500);
for (const t of ts) {
  await page.evaluate((T) => { const r = window.__room; for (let k = 0; k < 6; k++) { window.bdAt(r, +T - (5 - k) / 30); r.tick(1); } }, t);
  await page.screenshot({ path: `${dir}/p-${t}.png`, timeout: 120000 });
}
await browser.close();
