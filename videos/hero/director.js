// The hero film: window.filmAt(r, i) sets frame i (30 fps). One fixed isometric camera, about
// seventeen seconds: the room is assembled part by part (the breakdown's manual view), sweeps
// into its finished look, and then a cursor uses it: drags two things in from the dresser and
// scrubs the day into night. The cat keeps its seat by the window throughout.
(() => {
  const FPS = 30, LEN = 18.8;
  const cl = (x, a, b) => Math.min(b, Math.max(a, x));
  const ease = (x) => { x = cl(x, 0, 1); return x * x * x * (x * (x * 6 - 15) + 10); };
  const sm = (a, b, t) => ease((t - a) / (b - a));
  const lerp = (a, b, t) => a + (b - a) * t;
  const track = (keys) => (t) => {
    if (t <= keys[0][0]) return keys[0][1];
    for (let k = 1; k < keys.length; k++) {
      const [t1, v1] = keys[k];
      if (t < t1) {
        const [t0, v0] = keys[k - 1], e = sm(t0, t1, t);
        return Array.isArray(v0) ? v0.map((v, j) => lerp(v, v1[j], e)) : lerp(v0, v1, e);
      }
    }
    return keys[keys.length - 1][1];
  };
  // camera: [time, [log zoom, centre y]]; still while the cursor works, away into the night at the end
  const cam = track([[0, [Math.log(1.0), 0.85]], [3.4, [Math.log(1.02), 0.85]], [4.2, [Math.log(1.2), 0.9]], [13.2, [Math.log(1.24), 0.9]], [16.4, [Math.log(0.62), 2.65]], [LEN, [Math.log(0.6), 2.7]]]);
  const clock = track([[0, 15.2], [9.0, 15.4], [11.6, 20.8], [LEN, 21.3]]);
  const ui = track([[4.2, 0], [4.6, 1], [12.8, 1], [13.4, 0]]);
  const UI_SEL = '.brand, .hint, .dock, .world, .dresser, #albumBtn';
  // the cursor: [time, where] with where = [x, y] in CSS px, or a function of the room for targets that move
  let fired = new Set(), cursor = null, V3 = null;
  const once = (key, t, T, fn) => { if (T >= t && !fired.has(key)) { fired.add(key); fn(); } };
  const tile = (label) => [...document.querySelectorAll('#shelfList .pick')].find((b) => b.textContent.trim().startsWith(label));
  const centre = (el) => { const b = el.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; };
  const DROPS = [
    { label: 'Floor lamp', type: 'floorLamp', at: { x: 1.55, z: -1.1 }, t: [4.8, 5.5, 5.6, 6.6] },  // reach, press, drag, drop
    { label: 'Cardboard', type: 'box', at: { x: 0.35, z: 0.55 }, t: [6.9, 7.5, 7.6, 8.5] },
  ];
  const SLIDE = [8.8, 9.0, 11.6, 11.8]; // reach the slider, press, drag through the day, let go
  function cursorAt(r, T) {
    // piecewise: rest → tile → room → tile → room → slider thumb → along the slider → rest
    const slider = document.getElementById('time').getBoundingClientRect();
    const thumbX = (h) => slider.left + 8 + (slider.width - 16) * (h * 60 / 1440);
    const pts = [[4.4, [940, 420]]];
    for (const d of DROPS) {
      const t = tile(d.label); if (!t) continue;
      pts.push([d.t[0], centre(t)], [d.t[1], centre(t)], [d.t[3], r.project([d.at.x, 0, d.at.z])]);
    }
    pts.push([SLIDE[0], [thumbX(clock(SLIDE[0])), slider.top + slider.height / 2]], [SLIDE[1], [thumbX(clock(SLIDE[1])), slider.top + slider.height / 2]]);
    if (T >= SLIDE[1] && T <= SLIDE[2]) return [thumbX(clock(T)), slider.top + slider.height / 2];
    pts.push([SLIDE[2], [thumbX(clock(SLIDE[2])), slider.top + slider.height / 2]], [SLIDE[3] + 0.8, [thumbX(clock(SLIDE[2])) + 60, slider.top - 90]]);
    return track(pts)(T);
  }
  function ensureCursor() {
    if (cursor) return cursor;
    cursor = document.createElement('div');
    cursor.innerHTML = '<svg width="26" height="30" viewBox="0 0 26 30"><path d="M2 2 L2 24 L8 18.5 L12.5 28 L16.5 26.2 L12 16.8 L20 16.8 Z" fill="#fff" stroke="#241f2c" stroke-width="1.8" stroke-linejoin="round"/></svg>';
    Object.assign(cursor.style, { position: 'fixed', left: '0', top: '0', zIndex: 99, pointerEvents: 'none', opacity: '0', transformOrigin: '2px 2px', filter: 'drop-shadow(0 2px 3px rgba(36,31,44,.35))' });
    document.body.appendChild(cursor);
    return cursor;
  }
  window.filmAt = (r, i) => {
    const T = i / FPS, c = r.cat, bd = r.bd;
    V3 ||= r.camera.position.constructor;
    if (i === 0) {
      fired = new Set();
      r.radio.on = false; r.lantern.auto = true;
      for (const el of document.querySelectorAll(UI_SEL + ', #ghost')) el.style.transition = 'none';
    }
    // the cat keeps its seat, facing into the room
    c.pos.set(-1.72, 0.52, -0.3); c.yaw = 1.1; c.yawVel = 0; c.decideT = 1e9; c.path = [];
    if (c.state !== 'sit') c.state = 'sit';
    c.stateT = Math.min(c.stateT, 1);
    // the assembly, then one sweep into the finished look
    bd.assemble = 1; bd.build = T < 4 ? T : null; bd.lines = 0; bd.band = 0.14; bd.cut = null; bd.portal = 0; bd.bones = 0;
    const sweep = sm(3.4, 4.1, T);
    bd.stage = sweep < 1 ? { view: 'diagram' } : { view: 'final' };
    bd.left = sweep > 0 && sweep < 1 ? { view: 'final' } : null;
    bd.wipeX = sweep > 0 && sweep < 1 ? sweep : null;
    bd.labelOpacity = 0; r.bdLabel('', '', '');
    // time of day, lamps, the radio once it is evening
    r.clock.h = clock(T);
    document.getElementById('time').value = Math.round(r.clock.h * 60);
    const lamp = r.props.find((p) => p.type === 'floorLamp');
    if (lamp) lamp.on = r.clock.h > 19.4;
    once('radio', 11.9, T, () => { r.radio.on = true; });
    // the product UI fades in for the cursor and out for the ending
    const u = ui(T);
    for (const el of document.querySelectorAll(UI_SEL)) { el.style.opacity = String(u); el.style.pointerEvents = 'none'; }
    // the cursor: drags a tile's picture into the room and lets go where the thing lands
    const cur = ensureCursor();
    const [cx, cy] = cursorAt(r, T);
    const down = DROPS.some((d) => T >= d.t[1] && T < d.t[3]) || (T >= SLIDE[1] && T < SLIDE[2]);
    cur.style.opacity = String(sm(4.3, 4.6, T) * (1 - sm(12.4, 12.8, T)));
    cur.style.transform = `translate(${cx - 2}px, ${cy - 2}px) scale(${down ? 0.88 : 1})`;
    const ghost = document.getElementById('ghost');
    const dragging = DROPS.find((d) => T >= d.t[2] && T < d.t[3]);
    if (dragging) { const img = tile(dragging.label)?.querySelector('img'); if (img) ghost.src = img.src; ghost.hidden = false; ghost.style.left = cx + 'px'; ghost.style.top = cy + 'px'; }
    else ghost.hidden = true;
    for (const d of DROPS) once('drop-' + d.type, d.t[3], T, () => r.addProp(d.type, d.at));
    // camera
    const [lz, cyw] = cam(T);
    r.view.zoom = Math.exp(lz); r.view.center.set(0, cyw, 0);
    r.look.tilt = r.look.tiltTarget = 0;
    r.resize();
    const shift = (292 / 2) * (r.camera.right - r.camera.left) / innerWidth;
    r.camera.left -= (1 - u) * shift; r.camera.right -= (1 - u) * shift;
    r.camera.updateProjectionMatrix();
  };
  window.filmLength = LEN * FPS;
})();
