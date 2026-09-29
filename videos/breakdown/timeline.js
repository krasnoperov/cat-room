// The breakdown film as one function of time: window.bdAt(r, T) sets every knob for second T.
// Fast: about twenty seconds. Each new look sweeps in over the previous one from the left in
// 0.7 s; nothing switches on a hard cut, nothing lingers.
(() => {
  const DEG = Math.PI / 180;
  const cl = (x, a, b) => Math.min(b, Math.max(a, x));
  const sm = (a, b, x) => { const t = cl((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const DIAGRAM = { view: 'diagram' };
  const CLAY = { view: 'final', clay: 1, ink: 1, ao: 1, bloom: 0, grade: 0, finish: 0 };
  const NORMALS = { view: 'normals' };
  const INK = { view: 'final', ink: 1, ao: 0, bloom: 0, grade: 0, finish: 0 };
  const DEPTH = { view: 'depth' };
  const INK_AO = { view: 'final', ink: 1, ao: 1, bloom: 0, grade: 0, finish: 0 };
  const FULL = { view: 'final' };
  const SW = 0.7;
  const LOOKS = [[0, DIAGRAM], [2.9, CLAY], [8.6, NORMALS], [9.9, INK], [11.2, DEPTH], [12.5, INK_AO], [13.8, FULL]];
  let tris = null;
  const LABELS = [
    [0, 3.0, '01 · geometry', 'Every object is a real mesh', () => `${tris.toLocaleString('en-US')} triangles · built in Blender`],
    [3.0, 5.2, '02 · light', 'Clay, and a sun that walks', () => 'toon shading · real-time shadows from the clock'],
    [5.2, 8.6, '03 · rig', 'The cat has a skeleton', () => '23 bones · two-bone IK plants each paw'],
    [8.6, 11.2, '04 · ink', 'Outlines drawn from normals and depth', () => 'a post pass, not textures'],
    [11.2, 13.8, '05 · depth', 'Soft contact shadow from the depth buffer', () => 'screen-space ambient occlusion'],
    [13.8, 16.0, '06 · finish', 'Bloom, colour grade, paper grain', () => 'lavender in shadow · apricot in light'],
    [16.0, 99, 'cat room', 'rooms.krasnoperov.me', () => 'one HTML file · Three.js · Blender · makefx · Claude'],
  ];
  window.bdAt = (r, T) => {
    const bd = r.bd, c = r.cat;
    tris = tris || r.bdCount();
    // camera: a continuous turn; a quick push in on the rig and back
    r.view.angle = r.view.target = (45 + T * 0.9) * DEG;
    const zRig = sm(5.0, 5.9, T) * (1 - sm(7.7, 8.6, T));
    r.view.zoom = Math.exp(lerp(Math.log(lerp(0.86, 0.94, T / 20)), Math.log(4.6), zRig));
    // the push follows the cat as it walks across the rug
    r.view.center.set(lerp(0, c.pos.x, zRig), lerp(0.85, 0.2, zRig), lerp(0, c.pos.z, zRig));
    r.resize();
    // looks and sweeps
    let k = 0;
    while (k + 1 < LOOKS.length && T >= LOOKS[k + 1][0]) k++;
    const [t0, look] = LOOKS[k], prev = LOOKS[k - 1];
    const sweep = prev ? sm(t0, t0 + SW, T) : 1;
    bd.stage = sweep < 1 && prev ? prev[1] : look;
    bd.left = sweep < 1 && prev ? look : null;
    bd.wipeX = sweep < 1 && prev ? sweep : null;
    bd.assemble = 1; bd.build = T < 4 ? T : null;
    // the drawing shows only in the band behind each sweep; nothing is left over a finished look
    bd.band = 0.14; bd.lines = 0;
    // light: the sun walks across the clay, dusk at the end
    r.clock.h = T < 16 ? lerp(9, 16.8, sm(3.2, 5.2, T)) : lerp(16.8, 20.2, sm(16.2, 19.6, T));
    // the rig: the cat walks across the rug with its bones showing
    bd.bones = sm(5.6, 6.0, T) * (1 - sm(7.6, 8.0, T));
    // the cat, as a function of time so film segments rendered apart join up: sitting on the rug,
    // then one walk across it side-on to the camera (the skeleton reads in profile), then sitting
    // again where it stopped (the settling steps as it sits are kept)
    const WALK = [4.6, 8.8], dx = 0.776, dz = -0.631, half = 0.3 * (WALK[1] - WALK[0]) / 2;
    const d = 0.3 * cl(T - WALK[0], 0, WALK[1] - WALK[0]) - half;
    c.pos.set(0.1 + dx * d, 0, 0.25 + dz * d); c.yaw = Math.atan2(dx, dz); c.yawVel = 0; c.decideT = 1e9;
    if (T >= WALK[0] && T < WALK[1]) { c.speed = 0.3; c.state = 'walk'; c.path = [{ walk: { x: 0.1 + dx * 9, y: 0, z: 0.25 + dz * 9 } }]; }
    else { c.path = []; if (c.state !== 'sit') { c.state = 'sit'; } c.stateT = Math.min(c.stateT, 1); } // sits, never dozes off
    bd.cut = null; bd.portal = 0;
    // captions fade across their edges
    const L = LABELS.find(([a, b]) => T >= a && T < b);
    if (L) {
      const [a, b, n, title, sub] = L;
      bd.labelOpacity = Math.min(a === 0 ? sm(0.1, 0.4, T) : sm(a, a + 0.25, T), 1 - sm(b - 0.25, b, T));
      r.bdLabel(n, title, sub());
    } else { bd.labelOpacity = 0; r.bdLabel('', '', ''); }
  };
})();
