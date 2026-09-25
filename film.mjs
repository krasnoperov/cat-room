// node film.mjs outdir "query" frames [warmup]
import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const [dir, q, n = '720', warm = '30', scale = '1.5'] = process.argv.slice(2);
fs.mkdirSync(dir, { recursive: true });
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: +scale });
page.on('pageerror', (e) => console.log('pageerror', e.message));
await page.goto('http://localhost:8123/index.html?fixed=1&clean=1&' + q);
await page.waitForFunction(() => window.__room && window.__room.frames >= 2);
await page.waitForTimeout(1500); // textures
await page.evaluate((w) => window.__room.tick(+w), warm);
for (let i = 0; i < +n; i++) {
  const url = await page.evaluate(() => { window.__room.tick(1); return document.getElementById('gl').toDataURL('image/jpeg', 0.93); });
  fs.writeFileSync(`${dir}/f${String(i).padStart(4, '0')}.jpg`, Buffer.from(url.split(',')[1], 'base64'));
  if (i % 60 === 0) console.log('frame', i, new Date().toISOString().slice(11, 19));
}
await browser.close();
