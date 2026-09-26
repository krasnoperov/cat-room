# Task: build the room's props as Blender models from the reference

You are working in `/home/alv/projects/cat-room`, a single-page Three.js room
(`index.html`) with a Blender-built cat (`models/cat_build.py`). Build the
props shown in `assets/props-sheet.png` (attached) as proper models in the
same soft, rounded, lo-fi anime look as the cat and the reference.

Write one script, `models/props_build.py`, that builds and exports one GLB
per prop into `models/props/`. Do not edit `index.html` or any other script
(another agent is working on `models/plants_build.py` at the same time; do
not touch it or the plant GLBs). The room integrates the props against the
contract below, so follow the object names exactly.

## Conventions (all props)

- Blender metres, Z up. The glTF export turns Blender -Y into +Z, so
  **Blender -Y is the prop's front**, the side that faces the room.
- The GLB origin is the centre of the prop's footprint on the surface it
  stands on (z = 0), unless the prop hangs (then the origin is the hook).
- `export_format='GLB'`, no animations, no armatures, modifiers applied.
- Colour with vertex colours (`Col` attribute, exported as COLOR_0) or plain
  glTF base colours per material. No image textures (one exception: the
  easel canvas needs UVs, see below).
- Real geometry for holes and openings; the room draws ink outlines from
  depth and normals. Shade smooth, bevel hard edges slightly.
- Every named object below is a separate object in the GLB with its origin
  where stated, because the room animates or hides it.
- Keep each GLB under about 12k triangles (cat tree under 20k).

## Props, sizes and named parts

1. `box.glb`: open cardboard box, footprint about 0.44 × 0.34, walls 0.2
   high, the four flaps open outward and slightly drooping, visible
   corrugated edge thickness. Objects: `box`. The inside floor must be clear
   (the cat sits inside).
2. `bowls.glb`: an oval woven mat about 0.4 × 0.22 with two ceramic bowls
   side by side (food on the left, i.e. +X, water on the right). Objects:
   `mat`, `foodBowl`, `food` (a mound of kibble, origin at the food bowl's
   inner bottom centre; the room scales it in Z to show how full it is),
   `waterBowl`, `water` (a flat water disc, origin at the water bowl's inner
   bottom centre, scaled in Z likewise).
3. `cat_tree.glb`: footprint about 0.46 × 0.46, about 0.95 m tall: a round
   base, a tall sisal post up to a round cushioned bed with a low rim at the
   top, a short second post with a round cushioned platform about halfway
   up, a pompom toy hanging from the top bed on a string. Objects: `tree`
   (everything static), `perch0` (a tiny object at the centre of the lower
   platform's cushion top), `perch1` (same for the top bed's cushion top),
   `toy` (string and pompom, origin at the string's top so it can swing).
4. `floor_lamp.glb`: about 1.45 m tall, round weighted base, thin brass
   stem, warm linen drum shade, pull chain. Objects: `lamp` (stand and
   chain), `shade` (the drum shade, open at top and bottom), `bulb` (a small
   bulb inside the shade; the room makes it glow).
5. `candle.glb`: small amber glass jar candle about 0.08 wide, 0.1 high.
   Objects: `jar`, `wax`, `wick` (origin at the wick's tip, where the room
   puts the flame).
6. `radio.glb`: vintage wooden tabletop radio about 0.3 wide, 0.13 deep,
   0.2 high, rounded wooden case, fabric speaker grille, a horizontal tuning
   dial window below the grille, two round knobs, small feet. Objects:
   `radio` (case, grille, feet), `dial` (the dial face; the room makes it
   glow), `knobL`, `knobR` (origins at each knob's centre, axis along -Y so
   they can turn).
7. `yarn.glb`: a pink yarn ball about 0.1 across with visible wound strands
   (real ridges, e.g. a few wound tube curves over a sphere). Objects:
   `ball`, origin at the ball's centre (the room rolls it).
8. `watering_can.glb`: small green metal can about 0.32 long including the
   spout, 0.18 high, rose on the spout, top handle and side handle.
   Objects: `can` (origin at the base centre), `spoutTip` (a tiny object at
   the rose's centre, where the room emits water).
9. `bird_feeder.glb`: little wooden house-shaped feeder with a hook,
   about 0.14 wide and 0.2 high, a perch dowel in front, seeds in the tray.
   Origin at the top of the hook. Objects: `feeder`, `perchL`, `perchR`
   (tiny objects on the perch where two birds stand).
10. `bird.glb`: one round chubby sparrow about 0.08 long, brown back, cream
    belly, dark eye, small beak, facing -Y, standing on z = 0 at its feet.
    Objects: `body` (body, tail and legs), `head` (origin at the neck so it
    can peck and turn), `wingL`, `wingR` (origins at the shoulders so they
    can flap).
11. `wind_chime.glb`: wooden top disc about 0.1 across, five pastel metal
    tubes of different lengths (0.08 to 0.16), a clapper disc and a wind
    catcher, all on thin strings. Origin at the top of the hanging string.
    Objects: `top` (disc and strings above it), `tube0` .. `tube4` (each with
    origin at its own hanging point so it can swing), `clapper` (origin at
    its string's top).
12. `easel.glb`: wooden artist's easel about 1.25 m tall, tripod legs, a
    tray holding a small palette with paint dabs. Objects: `easel`
    (everything else), `canvas` (the canvas board, about 0.5 wide and 0.6
    high, facing -Y, with **UVs 0..1 across its front face**, so the room can
    put a painting on it; the frame and sides can share the object).

## Tools

- Blender 5.2: `~/opt/blender-5.2.2-linux-x64/blender -b --factory-startup -P models/props_build.py`
- A local server serves the project at http://localhost:8123 (if not, run
  `python3 -m http.server 8123 --bind 127.0.0.1` in the project root).
- Four-view render of any GLB on white, auto-framed:
  `node vshot.mjs /tmp/radio.png "m=models/props/radio.glb"`.
  Look at the renders and compare them with the reference every iteration.
- `models/cat_build.py` shows working patterns for scripted Blender models,
  vertex colours and GLB export.

## How to work

Build all twelve, then iterate: render each, compare with the reference,
improve the weakest ones. Aim for at least three passes over the whole set.
When done, make a contact sheet of all twelve (one four-view render each is
fine, or a grid of single views) at `assets/props-v2.png`, print each GLB's
object names and triangle count, and summarise what still differs from the
reference.
