// node film2.mjs out.mp4 "query" frames "setupJS" "perFrameJS(i)" [warm]
import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
const [out, q, n = '150', setup = '', perFrame = '', warm = '45'] = process.argv.slice(2);
const dir = out.replace(/\.mp4$/, '_frames');
fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
page.on('pageerror', (e) => console.log('pageerror', e.message));
await page.goto('http://localhost:8123/index.html?fixed=1&' + (q.includes('ui=1') ? '' : 'clean=1&') + q);
await page.waitForFunction(() => window.__room && window.__room.frames >= 2);
await page.waitForTimeout(2500);
if (setup) await page.evaluate(setup);
await page.waitForTimeout(3500); // prop models load
await page.evaluate((w) => window.__room.tick(+w), warm);
for (let i = 0; i < +n; i++) {
  const ui = q.includes('ui=1');
  const url = await page.evaluate(([pf, i, ui]) => { const r = window.__room; if (pf) (new Function('r', 'i', pf))(r, i); r.tick(1); return ui ? '' : document.getElementById('gl').toDataURL('image/jpeg', 0.94); }, [perFrame, i, ui]);
  const file = `${dir}/f${String(i).padStart(4, '0')}.jpg`;
  if (ui) await page.screenshot({ path: file, type: 'jpeg', quality: 94 }); // the page with its UI
  else fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '30', '-i', `${dir}/f%04d.jpg`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-movflags', '+faststart', out]);
fs.rmSync(dir, { recursive: true, force: true });
console.log('done', out);
