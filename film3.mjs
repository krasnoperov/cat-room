// node film3.mjs out.mp4 startFrame endFrame  — renders frames [start, end) of the breakdown timeline, 1920x1080 via page screenshots
import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
const [out, a, b] = process.argv.slice(2);
const dir = out.replace(/\.mp4$/, '_frames');
fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
page.on('pageerror', (e) => console.log('pageerror', e.message));
await page.goto((process.env.BASE || 'http://localhost:8128/index.html') + '?fixed=1&clean=1&breakdown=1&paused=1&radio=0&t=16.6');
await page.waitForFunction(() => window.__room && window.__room.frames >= 2, null, { timeout: 120000 });
await page.addScriptTag({ path: 'videos/breakdown/timeline.js' });
await page.waitForTimeout(3500);
// warm up from a little before the segment so the cat and the light have settled
await page.evaluate((s) => { const r = window.__room; for (let k = Math.max(0, s - 20); k < s; k++) { window.bdAt(r, k / 30); r.tick(1); } }, +a);
for (let i = +a; i < +b; i++) {
  await page.evaluate((i) => { const r = window.__room; window.bdAt(r, i / 30); r.tick(1); }, i);
  await page.screenshot({ path: `${dir}/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93, timeout: 120000 });
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '30', '-start_number', a, '-i', `${dir}/f%05d.jpg`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', out]);
fs.rmSync(dir, { recursive: true, force: true });
console.log('done', out);
