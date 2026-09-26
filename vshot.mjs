import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const [out, q = '', script = ''] = process.argv.slice(2); // q: e.g. m=models/monstera.glb
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
page.on('pageerror', (e) => console.log('pageerror', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.log(m.text()); });
if (script) await page.addInitScript(script);
await page.goto('http://localhost:8123/viewer.html?' + q);
await page.waitForFunction(() => window.done, null, { timeout: 60000 });
await page.screenshot({ path: out });
await browser.close();
