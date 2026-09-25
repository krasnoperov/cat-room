import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const [q = '', secs = '20', outPrefix = ''] = process.argv.slice(2);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const logs = [];
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') logs.push(m.type() + ': ' + m.text()); });
page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
await page.goto('http://localhost:8123/index.html?' + q);
await page.waitForFunction(() => window.__room && window.__room.frames > 5, null, { timeout: 60000 });
const report = () => page.evaluate(() => { const r = window.__room; const c = r.cat; return { h: +r.clock.h.toFixed(2), frames: r.frames, cat: [c.state, c.activity, c.pos.toArray().map((v) => +v.toFixed(2))], monstera: +r.monstera.growth.toFixed(3), lemon: +r.lemon.growth.toFixed(3), papers: r.papers.map((p) => p.state), tea: Math.round(r.tea.temp) }; });
console.log(JSON.stringify(await report()));
const n = +secs;
for (let i = 0; i < n; i += 5) {
  await page.waitForTimeout(5000);
  console.log(JSON.stringify(await report()));
  if (outPrefix) await page.screenshot({ path: `${outPrefix}-${i}.png` });
}
console.log(logs.slice(0, 10).join('\n'));
await browser.close();
