// The breakdown film as one function of time: window.bdAt(r, T) sets every knob for second T.
(() => {
  const DEG = Math.PI / 180;
  const cl = (x, a, b) => Math.min(b, Math.max(a, x));
  const sm = (a, b, x) => { const t = cl((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const FULL = { view: 'final' };
  const CLAY = { view: 'final', clay: 1, ink: 1, ao: 1, bloom: 0, grade: 0, finish: 0 };
  const INK = { view: 'final', ink: 1, ao: 0, bloom: 0, grade: 0, finish: 0 };
  const INK_AO = { view: 'final', ink: 1, ao: 1, bloom: 0, grade: 0, finish: 0 };
  let tris = null;
  window.bdAt = (r, T) => {
    const bd = r.bd, c = r.cat;
    tris = tris || r.bdCount();
    // camera: a slow continuous turn; zoom in for the rig
    const a = (45 + T * 0.45) * DEG;
    r.view.angle = r.view.target = a;
    const zRig = sm(10.2, 11.2, T) * (1 - sm(14.0, 14.9, T));
    r.view.zoom = lerp(lerp(0.86, 0.93, T / 36), 4.6, zRig);
    r.view.center.set(lerp(0, 0.1, zRig), lerp(0.85, 0.2, zRig), lerp(0, 0.25, zRig));
    r.resize();
    bd.left = null; bd.wipeX = null; bd.bones = 0; bd.cut = null; bd.portal = 0; bd.assemble = 1;
    r.clock.h = 16.6;
    let L = ['', '', ''];
    if (T < 4) {
      bd.stage = { view: 'wire' };
      bd.assemble = sm(0.2, 3.8, T);
      L = ['01 · geometry', 'Every object is a real mesh', `${tris.toLocaleString('en-US')} triangles · built in Blender`];
    } else if (T < 7) {
      bd.stage = CLAY; bd.left = { view: 'wire' }; bd.wipeX = 1 - sm(4.2, 6.6, T);
      L = ['02 · form', 'Clay: shape and shadow, no colour', 'toon shading · 3 light bands'];
    } else if (T < 10.5) {
      bd.stage = CLAY;
      r.clock.h = lerp(9, 17.2, sm(7.2, 10.3, T));
      L = ['03 · light', 'A sun that walks across the window', 'real-time shadow map · sun from the clock'];
    } else if (T < 14.5) {
      bd.stage = CLAY; bd.bones = sm(10.6, 11.4, T);
      c.pos.set(0.1, 0, 0.25); c.yaw = 2.2; c.decideT = 1e9; c.state = 'walk';
      c.path = [{ walk: { x: 0.1 + Math.sin(2.2) * 9, y: 0, z: 0.25 + Math.cos(2.2) * 9 } }];
      L = ['04 · rig', 'The cat has a skeleton', '23 bones · two-bone IK plants each paw'];
    } else if (T < 18) {
      if (T < 14.6) { c.pos.set(-1.72, 0.52, -0.3); c.state = 'sleep'; c.path = []; c.yaw = 0.35; }
      bd.stage = INK; bd.left = { view: 'normals' }; bd.wipeX = 1 - sm(15.3, 17.6, T);
      L = ['05 · ink', 'Outlines drawn from normals and depth', 'a post pass, not textures'];
    } else if (T < 21.5) {
      bd.stage = INK_AO; bd.left = { view: 'depth' }; bd.wipeX = 1 - sm(18.8, 21.1, T);
      L = ['06 · depth', 'Soft contact shadow from the depth buffer', 'screen-space ambient occlusion'];
    } else if (T < 25) {
      bd.stage = FULL; bd.left = INK_AO; bd.wipeX = 1 - sm(21.8, 24.6, T);
      L = ['07 · finish', 'Bloom, colour grade, paper grain', 'lavender in shadow · apricot in light'];
    } else if (T < 29) {
      bd.stage = FULL;
      const down = sm(25.2, 26.2, T) * (1 - sm(28.2, 28.9, T));
      bd.cut = lerp(2.7, 0.35, down);
      bd.portal = T > 26.1 && T < 28.3 ? 1 : 0;
      L = ['08 · the window', 'The city outside is a painting', 'generated with makefx · seen through a stencil portal'];
    } else {
      bd.stage = FULL;
      r.clock.h = lerp(17.2, 20.6, sm(29.2, 35.5, T));
      L = T < 31 ? ['', '', ''] : ['cat room', 'rooms.krasnoperov.me', 'one HTML file · Three.js · Blender · makefx · Claude'];
    }
    r.bdLabel(...L);
  };
})();
