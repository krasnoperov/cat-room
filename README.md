# Cat Room

A small isometric room by a big window. Arrange things, watch the light
move, and the cat will find the warm spot.

One `index.html`, Three.js r180 from an import map. Painted
textures were generated with [makefx](https://makefx.app) (space
`aleksei-krasnoperov/cat-room`).

## Run

```bash
python3 -m http.server 8123
```

Open http://localhost:8123/.

To build the production site (Node.js 22+):

```bash
npm ci
./build.sh
python3 -m http.server 8124 --bind 127.0.0.1 --directory dist
```

The build bundles and minifies the room and addons, uses pinned Three.js r180
minified modules on jsDelivr, self-hosts the original fonts, and losslessly
compresses all GLB geometry with Meshopt. Source models and textures stay
unchanged. Content-hashed JavaScript, source maps, and fonts receive immutable
caching; unversioned files revalidate. Cloudflare applies `dist/_headers`;
Python's test server does not. See `PERF_REPORT.md` for measurements.

## What lives in the room

- **The sun** walks across the window through the day. Its patch crawls
  over the floor, dust drifts in the beam, and the light that bounces off
  the patch warms the room around it. At dusk the paper lantern switches
  on and the city outside lights up.
- **Plants grow in the sun.** The monstera unfurls new leaves, the lemon
  tree grows lemons, the pothos trails lengthen. Move them into the patch.
- **Tea cools.** Click the mug for a fresh cup.
- **The open window** lets a breeze in: the curtain billows, steam leans,
  and gusts blow notes off the desk. Click a note on the floor to tidy it.
- **Rain** greys the sky, beads the glass and hides the sun. Leave the
  window open and puddles form under it.
- **The cat** walks to the warmest reachable spot: the sun patch, the
  window seat, under the lantern, its bed. It paths around furniture,
  hops onto the seat, keeps away from a wet window, and now and then
  knocks a leaf off the monstera.
- **Books** can be pulled out; the neighbour leans into the gap.
- **Room radio** plays generated lo-fi (Eleven Music via makefx) and the
  room's own sounds: the city by day and crickets by night through an open
  window, rain when it rains. Pet the cat (click it) and it purrs.
- **The cat** is a small skeleton: the torso pivots at the pelvis, legs are
  drawn from joint to paw every frame and the tail grows from the pelvis,
  so it sits on its haunches, walks with its tail up and sleeps as a loaf.

## Things to add (the + shelf)

Each is a Blender model (`models/props_build.py`, from a makefx reference
sheet) with its own behaviour:

- **Radio**: the music. Click it; the dial glows and the sound comes from
  where it stands. It starts on the bookcase.
- **Cardboard box**: the cat climbs in, ahead of any warm spot, until it
  gets bored.
- **Food & water**: dinner at 08:00 and 19:00; an empty bowl means a cat
  sitting in front of you saying *mrrp?* until you click to refill.
- **Cat tree**: two perches; the top one is where it sleeps at night.
- **Floor lamp**: a warm pool of light and a warm spot after dark.
- **Candle**: flickers; a gust through the open window blows it out.
- **Yarn ball**: rolls and bounces, unwinds a thread, gets batted by the
  cat. Click to wind it back.
- **Watering can**: plants now need water as well as sun. Click the can,
  then a plant; too much water makes a puddle.
- **Bird feeder**: outside the window; sparrows visit in daylight and the
  cat watches them from the window seat.
- **Wind chime**: swings and rings in the breeze (synthesised in the
  browser).
- **Easel**: click it and the room paints itself (a Kuwahara oil filter
  over the current view).
- **Laser pointer** (in the dock): the cat stalks and pounces on the dot,
  and gets bored after a while.

## Controls

- Drag furniture on the floor, prints along the wall; `R` or double-click
  turns a piece. Pick up the cat and put it somewhere else.
- Turn the room in quarter steps (`Q` / `E`), lower the walls to look in
  from any side, scrub the time of day, pause time (`Space`).
- **Photo mode**: tilt-shift miniature focus, tap to focus, save a PNG.
- **Record a day**: 24 hours in 24 seconds, saved as MP4 or WebM, with the radio if it is on.
- **Share**: copies a link that opens this exact room. The room also
  saves itself in the browser.

## How it is drawn

The look comes from a paint pipeline, not from a repaint:

1. Colour pass into a multisampled half-float target, with a stencil
   portal that shows the painted city only through the window.
2. Normals and depth pass. Materials are swapped for normal materials
   that keep each object's clip planes; cut-out leaves use a masked
   shader so their holes stay holes.
3. Bloom: a bright pass at quarter size and two separable blurs.
4. Paint composite: ink edges from depth curvature and normal breaks
   (a slightly wobbly pen), screen-space ambient occlusion reconstructed
   for the orthographic camera, lavender-in-shade / apricot-in-light
   grading, paper grain and fibres, tilt-shift, and the sky.

The walls are cut for viewing only. An invisible full-height shell and
ceiling still cast the sun's shadows, so lowering a wall never floods
the room with light.

## URL parameters (for stills and video)

`t` hour · `rot` quarter turns · `cut` wall height · `open` 0/1 ·
`rain` 0/1 · `grow` plant growth 0–1 · `zoom` · `paused=1` · `clean=1`
hides the UI · `fixed=1` renders only on `window.__room.tick()`, one
1/30 s step at a time · `speed` hours per second.

`film.mjs` renders frame-exact videos with `fixed=1`.
