import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const S = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errs = []; page.on('pageerror', (e) => errs.push(e.message)); page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto((process.env.BASE || 'http://localhost:8126/index.html') + '?t=16.4&speed=0.01&radio=0');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.evaluate(() => localStorage.removeItem('cat-room-album-v1'));
await page.evaluate(() => { const r = window.__room; r.album.got = {}; });
// the cat starts asleep on the sunny seat: sunbath / golden hour should fire
await page.waitForTimeout(6000);
console.log('after 6s', await page.evaluate(() => Object.keys(window.__room.album.got)));
await page.screenshot({ path: `${S}/catch.png` });
// pet the cat
await page.evaluate(() => window.__room.items.find((o) => o.name === 'Cat').click());
await page.waitForTimeout(4000);
// a box
await page.evaluate(() => { const r = window.__room; r.addProp('box', { x: 0.4, z: 0.6 }); r.cat.decideT = 0; });
await page.waitForTimeout(20000);
console.log('after box', await page.evaluate(() => Object.keys(window.__room.album.got)));
await page.click('#albumBtn');
await page.waitForTimeout(600);
await page.screenshot({ path: `${S}/album.png` });
console.log('stored bytes', await page.evaluate(() => (localStorage.getItem('cat-room-album-v1') || '').length));
await page.keyboard.press('Escape');
console.log('closed', await page.evaluate(() => document.getElementById('albumBack').hidden));
console.log(errs.join('\n') || 'no errors');
await browser.close();
