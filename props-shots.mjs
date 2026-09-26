import { chromium } from '/home/alv/projects/makefx/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs';
const S = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errs = []; page.on('pageerror', (e) => errs.push(e.message));
await page.goto('http://localhost:8123/index.html?t=13&paused=1&clean=1');
await page.waitForFunction(() => window.__room && window.__room.frames > 5);
await page.evaluate(() => { const r = window.__room; for (const t of ['box', 'bowls', 'catTree', 'floorLamp', 'yarn', 'wateringCan', 'birdFeeder', 'windChime', 'easel']) r.addProp(t); r.addProp('candle', { host: 'Desk', x: -0.3, y: 0.755, z: -0.1 }); });
await page.waitForTimeout(3500);
await page.evaluate(() => { const r = window.__room; r.birds.forEach((b) => { b.state = 'arriving'; b.t = 5; b.stay = 99; }); const y = r.props.find((p) => p.type === 'yarn'); y.vel.set(0.9, 0, -0.4); });
await page.waitForTimeout(2500);
const shots = { box: 'Cardboard box', bowls: 'Food & water', yarn: null, feeder: null, chime: null, can: 'Watering can' };
for (const [name, label] of Object.entries(shots)) {
  await page.evaluate(([name, label]) => {
    const r = window.__room;
    let at;
    if (name === 'yarn') at = r.props.find((p) => p.type === 'yarn').ball.position.clone();
    else if (name === 'feeder') at = r.props.find((p) => p.type === 'birdFeeder').group.position.clone().add({ x: 0.4, y: -0.25, z: 0 });
    else if (name === 'chime') at = r.props.find((p) => p.type === 'windChime').group.position.clone().add({ x: 0, y: -0.15, z: 0 });
    else at = r.items.find((i) => i.name === label).group.getWorldPosition(new r.camera.position.constructor());
    r.view.zoom = 6; r.view.center.copy(at); r.view.center.y += 0.08; r.resize();
  }, [name, label]);
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${S}/pp-${name}.png`, clip: { x: 340, y: 150, width: 600, height: 500 } });
}
console.log(errs.join('\n') || 'no errors');
await browser.close();
