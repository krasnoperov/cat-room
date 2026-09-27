import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, acceptDownloads: true, permissions: ['clipboard-read', 'clipboard-write'] });
const page = await ctx.newPage();
const logs = [];
page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
page.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
await page.goto('http://localhost:8123/index.html');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
// photo save
await page.click('#photo');
let dl = page.waitForEvent('download');
await page.click('#snap');
console.log('picture:', (await dl).suggestedFilename());
await page.click('#photoDone');
// record 4 seconds then stop
await page.click('#record');
await page.waitForTimeout(4000);
console.log('rec text:', await page.textContent('#recText'));
dl = page.waitForEvent('download');
await page.click('#recStop');
const vid = await dl;
const path = await vid.path();
const fs = await import('node:fs');
console.log('video:', vid.suggestedFilename(), fs.statSync(path).size, 'bytes');
// share: move the desk, copy link, reload from it
await page.evaluate(() => window.__room.move('Desk', 0.6, 1.4, 1));
await page.click('#share');
await page.waitForTimeout(300);
const url = await page.evaluate(() => navigator.clipboard.readText());
console.log('link length:', url.length, 'toast:', await page.textContent('#toast'));
await page.close(); // one rendering tab at a time on a software GPU
const p2 = await ctx.newPage();
await p2.goto(url);
await p2.waitForFunction(() => window.__room && window.__room.frames > 5, null, { timeout: 90000 });
console.log('desk after reload:', JSON.stringify(await p2.evaluate(() => { const d = window.__room.get('Desk'); return [d.x, d.z, d.rot]; })));
console.log(logs.join('\n') || 'no errors');
await browser.close();
