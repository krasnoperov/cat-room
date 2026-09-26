import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const list = process.argv.slice(2);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 256, height: 256 } });
await page.addStyleTag?.({ content: '' }).catch(() => {});
for (const m of list) {
  await page.goto(`http://localhost:8123/viewer.html?single=1&m=${m}`);
  await page.evaluate(() => { document.body.style.background = 'transparent'; document.documentElement.style.background = 'transparent'; });
  await page.waitForFunction(() => window.done, null, { timeout: 60000 });
  const name = m.split('/').pop().replace('.glb', '');
  await page.screenshot({ path: `/tmp/claude-1000/-home-alv-projects-makefx--claude-worktrees-competent-bassi-43465d/9b40bd09-1b02-4978-8bc9-8fd3a8a9116f/scratchpad/thumb-${name}.png`, omitBackground: true });
  console.log('thumb', name);
}
await browser.close();
