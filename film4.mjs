// node film4.mjs out.mp4 [from] [to] [every]  — a directed film (DIRECTOR, default videos/launch/director.js; QUERY for the page), one continuous
// shot rendered in order (its events fire once); 1920x1080 page screenshots so the product UI is in it.
// `every` > 1 keeps every Nth frame for a quick preview. Frames before `from` (and those a preview skips) are stepped
// without drawing, so segments can render in parallel and join exactly.
import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
const [out, from = '0', to = '', every = '1'] = process.argv.slice(2);
const dir = out.replace(/\.mp4$/, '_frames');
fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: +(process.env.DSF || 1.5) });
page.on('pageerror', (e) => console.log('pageerror', e.message));
// the same random numbers in every process, so segments rendered in parallel join up
await page.addInitScript(() => { let a = 0x9e3779b9; Math.random = () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; });
await page.goto((process.env.BASE || 'http://localhost:8128/index.html') + '?' + (process.env.QUERY || 'fixed=1&paused=1&radio=0&t=15.9'));
await page.waitForFunction(() => window.__room && window.__room.frames >= 2, null, { timeout: 120000 });
await page.evaluate(() => window.__room.preloadProps()); // every prop model in hand before frame 0
await page.addScriptTag({ path: process.env.DIRECTOR || 'videos/launch/director.js' });
await page.waitForTimeout(3500);
const end = +to || await page.evaluate(() => window.filmLength || window.launchLength);
let n = 0;
for (let i = 0; i < end; i++) {
  await page.evaluate(([i, dry]) => { const r = window.__room; r.dry = dry; (window.filmAt || window.launchAt)(r, i); r.tick(1); }, [i, i < +from || (i - +from) % +every !== 0]);
  if (i >= +from && (i - +from) % +every === 0) {
    await page.screenshot({ path: `${dir}/f${String(n++).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93, timeout: 180000 });
  }
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(30 / +every), '-i', `${dir}/f%05d.jpg`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', out]);
fs.rmSync(dir, { recursive: true, force: true });
console.log('done', out, n, 'frames');
