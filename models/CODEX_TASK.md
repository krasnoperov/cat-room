# Task: make the 3D cat match the reference art

You are working in `/home/alv/projects/cat-room`, a single-page Three.js room
(`index.html`) with a skinned cat model built procedurally in Blender.

## Goal

Rework `models/cat_build.py` so the exported `models/cat.glb` looks like the
cat in the reference model sheet `assets/cat-sheet-b.png` (attached; the
secondary reference `assets/cat-sheet-a.png` shows the same character with
slightly different proportions). The current result (`assets/cat-v1-views.png`
and the attached comparison) is far from it. Match the reference as closely
as a smooth stylised 3D model can:

- **Silhouette first.** A big, wide, round head (about 45 % of standing
  height) sitting directly on the body with no visible neck; a fluffy fur
  ruff framing the face whose tufts stick out sideways at cheek level on
  both sides; a round fluffy cream chest bib with tufts; a plump, pear or
  loaf body; short stubby legs; round cream paws; a thick bushy tail that
  widens toward a rounded tip.
- **Ears:** large, wide triangles with softly rounded tips, set far apart
  on the top corners of the head, tilted outward, pink inside with a cream
  fur tuft, ginger outside. Not thin cones, not pink columns.
- **Eyes:** large, round, warm brown irises with a darker pupil and two
  white highlights (one big, one small), set low and wide on the face. Not
  flat black blobs.
- **Face:** cream lower face and muzzle, tiny pink nose, soft pink blush
  ovals on the cheeks, subtle forehead stripes.
- **Colour:** warm ginger (#E8A45E-ish) with soft darker tabby stripes on
  the back, flanks, legs and tail rings; cream bib, belly, paws and muzzle.
  Stripes should read clearly but softly, like the sheet, not washed out.

## Hard constraints (the app depends on these)

- Keep the Blender coordinate convention: the cat faces **-Y**, Z up,
  paws on z = 0, overall size about the same as now (nose to rump about
  0.38 m, ear tip about 0.36 m).
- Keep **one skinned body mesh** with a vertex colour attribute exported as
  COLOR_0, plus separate rigid objects parented to the `head` bone whose
  names start with `eye.`, `glint`, and `nose` (the app hides glints and
  squashes eyes to blink). You may add more rigid face parts (for example
  `iris.L`, `pupil.L`) as long as their names start with `eye` or `glint` so
  the blink logic still finds them; eyes may become several objects.
- Keep the armature and **exact bone names and hierarchy**: `root`, `pelvis`,
  `spine`, `chest`, `neck`, `head`, `upperarm.L/R`, `forearm.L/R`,
  `hand.L/R`, `thigh.L/R`, `shin.L/R`, `foot.L/R`, `tail0`..`tail4`. Legs
  are posed at runtime by two-bone IK from `upperarm`/`thigh` through
  `forearm`/`shin` to `hand`/`foot`, so keep each leg chain straight down
  in rest pose and ending at the paw on the floor. Move bone positions to
  fit the new shape if needed.
- Automatic weights must still bind every vertex (the script prints
  `unweighted verts`; it must be 0). Keep the mesh under about 45k faces.
- Export stays a skinned GLB without animations, at `models/cat.glb`.

## Tools

- Blender 5.2: `~/opt/blender-5.2.2-linux-x64/blender -b --factory-startup -P models/cat_build.py -- $PWD/models/cat.glb`
- A local server already serves the project at http://localhost:8123 (if
  not, start `python3 -m http.server 8123 --bind 127.0.0.1` in the project).
- Four-view render of the model on white: `node vshot.mjs /tmp/cat-views.png`
  (uses `viewer.html`: three-quarter front, side, front, three-quarter back).
  Look at the PNG and compare it with the reference every iteration.
- In-room close-up of a pose (sit/walk/sleep):
  `node shot.mjs /tmp/cat-room.png "t=17.6&paused=1&clean=1" 700 600 4000 "const r=window.__room; r.move('Lemon tree',1.7,1.7,0); r.view.zoom=8; r.view.center.set(0.9,0.17,0.3); r.resize(); r.cat.pos.set(0.9,0,0.3); r.cat.yaw=0.6; r.cat.state='sit'; r.cat.decideT=999;"`
- Metaball calibration: a single metaball element of `radius` r has a
  visible radius of about 0.574 r (threshold 0.6, stiffness 2); the script's
  `ell()` and `cap()` helpers already take visible sizes.

## How to work

Iterate: change the build script, rebuild, render the four views, compare
with the reference, repeat. Do at least six iterations and keep going while
each one visibly improves the match. Prioritise silhouette and face, then
colour. You may use extra metaball tufts, shaped mesh parts joined before
the voxel remesh (ears), sculpt-like displacement, or any Blender technique
that survives the GLB export as a single skinned mesh with vertex colours.

The in-room fur shells in `index.html` (`furShellMat`, `FUR_SHELLS`) currently
produce ragged white rims. If you touch them, make them read as soft fur in
the same ginger/cream colours, or reduce them; do not change anything else
in `index.html` except the `POSES` numbers if the new proportions need them.

When done, leave the final `models/cat.glb`, the final four-view render at
`assets/cat-v2-views.png`, and an in-room sit close-up at
`assets/cat-v2-room.png`. Summarise what you changed and what still differs
from the reference.
