# Cat Room

A meditative isometric room you furnish by hand. Evening light from a big
window, a cat that lives there, and small things that affect each other.
One self-contained `index.html`, Three.js from an import map, no build.

## Look

- Style 1 from the brief: lo-fi anime evening by the window, after the
  diloprimero.app room illustration, but with a wider palette.
- Warm ochre sunlight, sky blue, plant greens, honey wood, cream linen.
  Lavender only in shadows and at dusk.
- Soft toon shading, rounded shapes, no hard black outlines.
- Painted textures (window view, posters, rug, book spines) come from
  makefx, space `aleksei-krasnoperov/cat-room`.

## Room

A corner room in isometric view: two walls, floor, a large window with a
window-seat, a paper lantern, shelves with trailing plants, a desk.

## Interaction

- Drag objects on the floor grid; wall items slide along their wall.
- Rotate the view in 90° steps.
- Cutaway: lower the walls to a sill line, or slice the room at a height.
  Cut faces are drawn as clean sections, not as missing geometry.
- Time of day slider: the sun moves, the patch of window light crawls
  across the floor.

## Rules between things

1. Sun patch on a plant: the plant grows (slowly, visibly).
2. Tea cools over time: steam fades; put it on the lamp-warm desk to keep it.
3. Open window: the curtain sways, loose papers drift off the desk.
4. Evening: the lantern switches on, a warm pool of light replaces the sun.
5. The cat walks to the warmest spot: the sun patch by day, under the
   lantern or on the window-seat cushion by night.
6. A cat in the plant pot knocks a leaf off; a cat near papers scatters them.
7. Books on the shelf lean when one is removed.

## Out of scope for the first version

Sound, saving layouts, more than one room.
