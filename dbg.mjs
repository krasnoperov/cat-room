import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await page.goto('http://localhost:8123/index.html?t=13&paused=1&clean=1');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.evaluate(() => window.__room.addProp('birdFeeder'));
await page.waitForTimeout(3000);
console.log(await page.evaluate(() => {
  const r = window.__room, f = r.props.find((p) => p.type === 'birdFeeder');
  const out = { model: !!f.model, perches: f.perches?.length, pos: f.group.position.toArray(), parent: f.group.parent?.type };
  const box = new (r.camera.position.constructor)();
  f.group.updateMatrixWorld(true);
  const meshes = []; f.group.traverse((o) => { if (o.isMesh) meshes.push([o.name, o.getWorldPosition(new (r.camera.position.constructor)()).toArray().map((v) => +v.toFixed(2)), o.visible, o.material.clippingPlanes?.length]); });
  out.meshes = meshes.slice(0, 5);
  out.screen = r.project(f.group.position.toArray());
  return out;
}));
await browser.close();
