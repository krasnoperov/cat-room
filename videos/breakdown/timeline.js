// The breakdown film as one function of time: window.bdAt(r, T) sets every knob for second T.
// Each new look sweeps in over the previous one from the left; nothing switches on a hard cut.
(() => {
  const DEG = Math.PI / 180;
  const cl = (x, a, b) => Math.min(b, Math.max(a, x));
  const sm = (a, b, x) => { const t = cl((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const WIRE = { view: 'wire' };
  const CLAY = { view: 'final', clay: 1, ink: 1, ao: 1, bloom: 0, grade: 0, finish: 0 };
  const NORMALS = { view: 'normals' };
  const INK = { view: 'final', ink: 1, ao: 0, bloom: 0, grade: 0, finish: 0 };
  const DEPTH = { view: 'depth' };
  const INK_AO = { view: 'final', ink: 1, ao: 1, bloom: 0, grade: 0, finish: 0 };
  const FULL = { view: 'final' };
  // [time the sweep starts, look]; each sweep lasts SW seconds
  const SW = 1.3;
  const LOOKS = [[0, WIRE], [3.8, CLAY], [15.0, NORMALS], [17.4, INK], [19.8, DEPTH], [22.0, INK_AO], [24.4, FULL]];
  let tris = null;
  const LABELS = [
    [0, 3.9, '01 · geometry', 'Every object is a real mesh', () => `${tris.toLocaleString('en-US')} triangles · built in Blender`],
    [3.9, 7.6, '02 · form', 'Clay: shape and shadow, no colour', () => 'toon shading · 3 light bands'],
    [7.6, 11.0, '03 · light', 'A sun that walks across the window', () => 'real-time shadow map · sun from the clock'],
    [11.0, 15.0, '04 · rig', 'The cat has a skeleton', () => '23 bones · two-bone IK plants each paw'],
    [15.0, 19.8, '05 · ink', 'Outlines drawn from normals and depth', () => 'a post pass, not textures'],
    [19.8, 24.4, '06 · depth', 'Soft contact shadow from the depth buffer', () => 'screen-space ambient occlusion'],
    [24.4, 27.2, '07 · finish', 'Bloom, colour grade, paper grain', () => 'lavender in shadow · apricot in light'],
    [27.2, 31.4, '08 · the window', 'The city outside is a painting', () => 'generated with makefx · seen through a stencil portal'],
    [32.4, 99, 'cat room', 'rooms.krasnoperov.me', () => 'one HTML file · Three.js · Blender · makefx · Claude'],
  ];
  window.bdAt = (r, T) => {
    const bd = r.bd, c = r.cat;
    tris = tris || r.bdCount();
    // camera: a slow continuous turn; a push-in for the rig
    r.view.angle = r.view.target = (45 + T * 0.42) * DEG;
    const zRig = sm(10.8, 12.0, T) * (1 - sm(13.9, 15.1, T));
    r.view.zoom = lerp(lerp(0.86, 0.94, T / 38), 4.6, zRig);
    r.view.center.set(lerp(0, 0.1, zRig), lerp(0.85, 0.2, zRig), lerp(0, 0.25, zRig));
    r.resize();
    // looks and sweeps
    let k = 0;
    while (k + 1 < LOOKS.length && T >= LOOKS[k + 1][0]) k++;
    const [t0, look] = LOOKS[k], prev = LOOKS[k - 1];
    const sweep = prev ? sm(t0, t0 + SW, T) : 1;
    bd.stage = sweep < 1 && prev ? prev[1] : look;
    bd.left = sweep < 1 && prev ? look : null;
    bd.wipeX = sweep < 1 && prev ? sweep : null;
    bd.assemble = sm(0.2, 3.6, T);
    // the drawing stays under the picture: lines over the clay, a band of them behind every
    // sweep, and the whole drawing back over the room at the end
    bd.band = 0.14;
    bd.lines = Math.max(0.6 * sm(3.9, 4.6, T) * (1 - sm(6.6, 8.2, T)), 0.4 * sm(34.2, 35.8, T));
    // light: the sun walks during 03, dusk at the end
    r.clock.h = T < 7.6 ? 9 : T < 31.4 ? lerp(9, 16.8, sm(7.8, 10.8, T)) : lerp(16.8, 20.6, sm(31.6, 37.5, T));
    // the rig: the cat walks across the rug with its bones showing
    bd.bones = sm(11.4, 12.2, T) * (1 - sm(14.2, 14.9, T));
    if (T >= 10.6 && T < 15) {
      c.pos.set(0.1, 0, 0.25); c.yaw = 2.2; c.decideT = 1e9; c.state = 'walk';
      c.path = [{ walk: { x: 0.1 + Math.sin(2.2) * 9, y: 0, z: 0.25 + Math.cos(2.2) * 9 } }];
    } else if (T >= 15 && T < 15.1) { c.path = []; c.state = 'sit'; c.stateT = 0; }
    // the window: walls down, the painting fades up, then everything back
    const down = sm(27.4, 28.4, T) * (1 - sm(30.6, 31.4, T));
    bd.cut = down > 0 ? lerp(2.7, 0.35, down) : null;
    bd.portal = sm(28.3, 29.0, T) * (1 - sm(30.1, 30.7, T));
    // captions fade across their edges
    const L = LABELS.find(([a, b]) => T >= a && T < b);
    if (L) {
      const [a, b, n, title, sub] = L;
      bd.labelOpacity = Math.min(sm(a, a + 0.35, T), 1 - sm(b - 0.35, b, T));
      r.bdLabel(n, title, sub());
    } else { bd.labelOpacity = 0; r.bdLabel('', '', ''); }
  };
})();
