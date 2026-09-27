import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errs = []; page.on('pageerror', (e) => errs.push(e.message)); page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto('http://localhost:8123/index.html?t=23&paused=1');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.mouse.click(300, 600); await page.waitForTimeout(2000);
const seen = new Set();
for (let i = 0; i < 8; i++) { seen.add(await page.textContent('#trackTitle')); await page.click('#nextTrack'); await page.waitForTimeout(600); }
console.log('night:', [...seen].join(', '));
const ok = await page.evaluate(async () => { const r = []; for (const t of ['sunny-sill','honey-light','night-window','midnight-tea','rain-window-seat','drizzle-and-books']) r.push((await fetch('audio/' + t + '.mp3', { method: 'HEAD' })).status); return r; });
console.log('files', ok.join(' '));
console.log(errs.join('\n') || 'no errors');
await browser.close();
