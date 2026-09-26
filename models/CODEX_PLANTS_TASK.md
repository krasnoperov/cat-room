# Task: build the three houseplants as Blender models from the reference

You are working in `/home/alv/projects/cat-room`, a single-page Three.js room
(`index.html`). The cat is already a Blender model (`models/cat_build.py`);
the plants are still stiff procedural primitives (`assets/plants-v1.png`,
attached). Build them as proper models that match the reference sheet
`assets/plants-sheet.png` (attached), in the same soft, rounded, lo-fi anime
look as the cat.

Write one script, `models/plants_build.py`, that builds and exports three
GLBs. Do not edit `index.html`; integration into the room is done
separately against the contract below, so follow it exactly.

## Look (from the reference sheet)

1. **Monstera** in a round terracotta pot with a rolled rim and dark soil:
   7 to 9 glossy heart-shaped leaves with real split fenestrations from the
   edge and a few oval holes near the midrib, a lighter midrib and veins,
   leaves at different heights on long gently arching stems, leaf blades
   gently cupped and tilted outward, plus one young rolled leaf unfurling.
   Deep and mid greens with a light glossy highlight side.
2. **Lemon tree** in a cream glazed ceramic pot with soil: a slim brown
   trunk, a round bushy crown made of many small glossy oval leaves (real
   individual leaves, overlapping, two or three greens; not blobs or
   icospheres), five or six ripe yellow lemons hanging inside the crown and a
   few small white five-petal blossoms.
3. **Golden pothos** in a small cream pot: three or four long trailing vines
   of heart-shaped leaves with yellow variegation streaks, leaves alternating
   along each vine and getting smaller toward the tips, vines spilling over
   the pot rim. In the room this pot stands on a wall shelf (no macramé
   hanger), and the vines drape over the front edge of the shelf and hang
   down.

Holes and splits must be real geometry (no alpha cut-outs): the room draws
ink outlines from depth and normals, so holes need to be holes. Colour with
vertex colours (a `Col` attribute exported as COLOR_0) or plain glTF base
colours per material. No image textures. Shade smooth, soft rounded forms.

## Contract with the room (hard constraints)

Blender units are metres, Z up; the glTF export turns Blender -Y into +Z,
so **Blender -Y is "toward the room / toward the viewer"**. Each GLB's origin
is the centre of the pot's bottom, resting on z = 0. Export with
`export_format='GLB'`, no animations, no armatures, apply modifiers.

The room grows plants by scaling named nodes from 0 to 1, so each growing
part is its own object whose origin is where it grows from:

- `models/monstera.glb`, about 1.0 m tall, pot about 0.34 m wide and 0.3 m
  high. Objects: `pot` (pot, rim and soil), and `leaf0` .. `leaf8`, each one
  leaf **with its own stem**, origin at the stem's base in the soil. Order
  them oldest to youngest: the room shows the first N as the plant grows, so
  `leaf0`..`leaf3` alone must already look like a decent small plant, and
  `leaf8` is the young rolled leaf.
- `models/lemon.glb`, about 1.0 m tall, pot about 0.28 m wide and 0.26 m
  high. Objects: `pot`, `trunk`, `crown` (all foliage and blossoms joined),
  and `lemon0` .. `lemon5`, each lemon with its tiny stalk, origin at the
  lemon's own centre. Lemons must sit visibly in the lower and outer part of
  the crown so they read from above at about 30° elevation.
- `models/pothos.glb`, pot about 0.15 m wide and 0.12 m high. Objects:
  `pot`, and for each vine `k` (`0`..`3`) a chain of leaves
  `vine{k}_leaf00`, `vine{k}_leaf01`, ... ordered from the pot to the tip,
  each with origin at the point where it attaches to the vine, and matching
  stem pieces `vine{k}_seg00`, `vine{k}_seg01`, ... where segment i is the
  piece of vine leading to leaf i. The room reveals the first N leaves and
  segments of each vine. The vines leave the pot, go toward -Y (toward the
  room) over the shelf's front edge at about Blender y = -0.10, z = 0, then
  hang straight down to about z = -0.55 with a slight natural sway.

Keep each GLB under about 30k triangles.

## Tools

- Blender 5.2: `~/opt/blender-5.2.2-linux-x64/blender -b --factory-startup -P models/plants_build.py`
- A local server serves the project at http://localhost:8123 (if not, run
  `python3 -m http.server 8123 --bind 127.0.0.1` in the project root).
- Four-view render of any GLB on white, auto-framed:
  `node vshot.mjs /tmp/monstera.png "m=models/monstera.glb"` (same for
  `lemon.glb`, `pothos.glb`). Look at the PNGs and compare them with the
  reference every iteration.
- `models/cat_build.py` shows working patterns for scripted Blender models,
  vertex colours and GLB export.

## How to work

Iterate per plant: build, render, compare with the reference, improve. At
least four iterations per plant; keep going while each one visibly improves
the match. Prioritise silhouette and leaf shapes, then colour.

When done, leave the three GLBs in `models/`, and final four-view renders at
`assets/plants-v2-monstera.png`, `assets/plants-v2-lemon.png`,
`assets/plants-v2-pothos.png`. Print the object names and triangle counts of
each GLB, and summarise what still differs from the reference.
