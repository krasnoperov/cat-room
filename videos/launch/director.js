// The launch film as one continuous shot: window.launchAt(r, i) sets frame i (30 fps).
// One camera, one afternoon into night, no cuts. Every move eases in and out, the product UI
// fades rather than appears, and lamps warm up. Events fire once, so frames render in order
// (film4.mjs steps earlier frames without drawing them, so segments can render in parallel).
(() => {
  const FPS = 30;
  const cl = (x, a, b) => Math.min(b, Math.max(a, x));
  const ease = (x) => { x = cl(x, 0, 1); return x * x * x * (x * (x * 6 - 15) + 10); };
  const sm = (a, b, t) => ease((t - a) / (b - a));
  const lerp = (a, b, t) => a + (b - a) * t;
  // keyframed value: eased between neighbouring keys, so every move starts and stops softly
  const track = (keys) => (t) => {
    if (t <= keys[0][0]) return keys[0][1];
    for (let k = 1; k < keys.length; k++) {
      const [t1, v1] = keys[k];
      if (t < t1) {
        const [t0, v0] = keys[k - 1];
        const e = sm(t0, t1, t);
        if (!Array.isArray(v0)) return lerp(v0, v1, e);
        // camera keys (log zoom first): the centre travels in step with the frame's width, so a
        // zoom out neither races sideways at the start nor drifts at the end
        const lz = lerp(v0[0], v1[0], e), w0 = Math.exp(-v0[0]), w1 = Math.exp(-v1[0]);
        const ce = Math.abs(w1 - w0) > 1e-3 ? (Math.exp(-lz) - w0) / (w1 - w0) : e;
        return v0.map((v, j) => (j === 0 ? lz : j <= 3 ? lerp(v, v1[j], ce) : lerp(v, v1[j], e)));
      }
    }
    return keys[keys.length - 1][1];
  };
  const SEAT = [-1.98, 1.05, -0.58], ROOM = [0, 0.9, 0]; // the seat, and the feeder outside the window above it
  const L = Math.log;
  // camera: [time, [log zoom, centre x, y, z, tilt]]; while `follow` is 1 the centre is the cat
  const cam = track([
    [0, [L(3.3), ...SEAT, 0.7]], [2.2, [L(3.5), ...SEAT, 0.7]],        // A: the cat watching the birds, drifting in
    [3.8, [L(1.22), ...ROOM, 0]], [6.2, [L(1.25), ...ROOM, 0]],        // B: the whole room, held for the dresser
    [7.4, [L(2.3), ...ROOM, 0.35]], [17.2, [L(2.45), ...ROOM, 0.35]],  // C: along with the cat: yarn, dot, box
    [18.2, [L(2.9), ...ROOM, 0.45]], [20.0, [L(3.0), ...ROOM, 0.45]],  // D: close on the box for the picture
    [21.6, [L(1.6), ...ROOM, 0.1]], [23.0, [L(1.45), ...ROOM, 0]],     // E: dusk around the box
    [26.0, [L(0.62), 0, 2.65, 0, 0]], [28.6, [L(0.6), 0, 2.7, 0, 0]],  // F: the room recedes into the night
  ]);
  const followK = track([[6.2, 0], [7.4, 1], [20.0, 1], [21.6, 0.5], [23.0, 0]]);
  const clock = track([
    [0, 15.9], [6.2, 15.95],
    [17.2, 17.2],               // C: the afternoon goes on while the cat plays
    [20.0, 17.9],               // D: golden
    [21.2, 18.9], [23.0, 20.7], // E: dusk, slowest as the sun goes
    [28.6, 21.2],
  ]);
  const ui = track([[3.8, 0], [4.2, 1], [5.9, 1], [6.3, 0]]);
  const UI_SEL = '.brand, .hint, .dock, .world, .dresser, #albumBtn';
  // the red dot's stops: [time it darts there, x, z]; it starts just ahead of the cat
  const DOT = [[10.8, -0.42, 0.45], [12.4, -0.02, 0.62]], DOT_END = 14.0; // two stops: two pounces, the last beside the box
  let fired = new Set(), f1 = null, f2 = null, V3 = null, dotFrom = null;
  const once = (key, t, T, fn) => { if (T >= t && !fired.has(key)) { fired.add(key); fn(); } };
  const prop = (r, type) => r.props.find((p) => p.type === type);
  window.launchAt = (r, i) => {
    const T = i / FPS, c = r.cat;
    V3 ||= r.camera.position.constructor;
    if (i === 0) {
      fired = new Set(); f1 = f2 = dotFrom = null;
      r.move('Lemon tree', 1.6, -0.55, 0); // out from in front of the rug
      r.addProp('birdFeeder');
      c.pos.set(-1.72, 0.52, -0.3); c.yaw = -Math.PI / 2; c.state = 'sit'; c.stateT = 0; c.decideT = 1e9; c.path = [];
      c.playBoredUntil = 0; c.boxBoredUntil = 0;
      r.radio.on = false;
      for (const el of document.querySelectorAll(UI_SEL + ', #catch, #flash')) el.style.transition = 'none';
    }
    // A: sparrows at the feeder, the cat on the seat watching them
    // the sparrows are already at the feeder when the film starts (they load with it, a frame or two in)
    if (!fired.has('birds') && r.birds.length && r.birds.every((b) => b.head)) { fired.add('birds'); r.birds.forEach((b) => { b.state = 'perched'; b.t = 0; b.stay = 99; }); }
    if (T < 5.0 && c.state === 'sleep') c.state = 'sit'; // awake and watching, not dozing
    // B: things from the dresser
    once('yarn', 4.3, T, () => r.addProp('yarn', { x: -0.95, z: 0.12 })); // a hop and a step from the seat
    once('box', 4.7, T, () => r.addProp('box', { x: 0.45, z: 0.35 }));
    once('tree', 5.1, T, () => r.addProp('catTree', { x: 0.95, z: 0.85 }));
    once('birds-go', 5.6, T, () => { r.birds.forEach((b) => { b.stay = 0; }); prop(r, 'birdFeeder').nextVisit = 1e12; });
    // the cat does what the film asks: its own choices (and the birds' call to the window) wait
    c.decideT = 1e9; c.replan = false;
    // C1: the yarn
    once('play', 5.0, T, () => r.catSeek('play', 3));
    // C2: the red dot: it darts to a spot and waits there, long enough for a stalk and a pounce
    if (T >= DOT[0][0] && T < DOT_END) {
      if (!dotFrom) dotFrom = [c.pos.x + 0.35, c.pos.z + 0.1];
      let k = 0;
      while (k + 1 < DOT.length && T >= DOT[k + 1][0]) k++;
      const [t0, x1, z1] = DOT[k], [x0, z0] = k ? DOT[k - 1].slice(1) : dotFrom;
      const e = sm(t0, t0 + 0.35, T);
      const [sx, sy] = r.project([lerp(x0, x1, e), 0, lerp(z0, z1, e)]);
      r.laser.on = true;
      document.getElementById('gl').dispatchEvent(new PointerEvent('pointermove', { clientX: sx, clientY: sy, bubbles: true }));
    }
    once('dot-off', DOT_END, T, () => { r.laser.on = false; r.laser.visible = false; });
    // C3: the box
    once('to-box', 14.1, T, () => { c.playBoredUntil = 1e9; r.catSeek('box'); });
    // D: the picture
    once('snap', 18.3, T, () => { r.snapMoment('box'); r.showCatch('box', true); });
    once('unsnap', 20.0, T, () => r.showCatch('box', false));
    // E: dusk; the radio on (the cat keeps its box)
    once('radio', 20.4, T, () => { r.radio.on = true; });
    // time of day, lamps
    r.clock.h = clock(T);
    const lamp = prop(r, 'floorLamp');
    if (lamp) lamp.on = r.clock.h > 19.7;
    // the flash and the album card
    const fl = document.getElementById('flash');
    fl.style.opacity = String(0.8 * sm(18.25, 18.3, T) * (1 - sm(18.3, 18.85, T)));
    const card = document.getElementById('catch');
    const ck = sm(18.4, 18.8, T) * (1 - sm(19.6, 20.0, T));
    card.style.opacity = String(ck); card.style.transform = `translateY(${(1 - ck) * 14}px)`;
    // product UI fades; the room glides aside for the dresser instead of jumping
    const u = ui(T);
    for (const el of document.querySelectorAll(UI_SEL)) { el.style.opacity = String(u); el.style.pointerEvents = 'none'; }
    // camera: the cat is followed through two cascaded low-passes, so the frame accelerates
    // and settles smoothly even when the cat pounces
    const target = [c.pos.x, c.pos.y + 0.16, c.pos.z];
    f1 = f1 ? f1.map((v, j) => lerp(v, target[j], 0.05)) : target.slice();
    f2 = f2 ? f2.map((v, j) => lerp(v, f1[j], 0.05)) : target.slice();
    const [lz, x, y, z, tilt] = cam(T), fk = followK(T);
    r.view.zoom = Math.exp(lz);
    r.view.center.set(lerp(x, f2[0], fk), lerp(y, f2[1], fk), lerp(z, f2[2], fk));
    r.look.tilt = r.look.tiltTarget = tilt; r.look.focus = 0.5;
    r.resize();
    // resize() slides the room left of the docked dresser; ease that shift with the UI
    const shift = (292 / 2) * (r.camera.right - r.camera.left) / innerWidth;
    r.camera.left -= (1 - u) * shift; r.camera.right -= (1 - u) * shift;
    r.camera.updateProjectionMatrix();
  };
  window.launchLength = Math.round(28.6 * FPS);
})();
