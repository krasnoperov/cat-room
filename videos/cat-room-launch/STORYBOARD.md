---
format: 1920x1080
duration: 41s
message: "A cozy room that lives on its own: the cat follows the sun, and everything you add changes what it does"
arc: Hook → Product intro → Benefit → Feature cascade → Atmosphere → CTA (Feature-Benefit Cascade)
audience: people on X who liked the Opus 5.5 lens-lab / black-hole demos; cozy-game and lo-fi fans
mode: autonomous
music: none
---

<!-- No narration. The room's own generated lo-fi track (golden-hour.mp3) is laid in by hand after assembly; "voiceover" below is the on-screen caption text, set in Fraunces. -->

## Video direction

- **The footage is the product.** Every frame is built on a full-bleed live render of the room (`<video>` clip, `roles: background` at full strength, never dimmed below 85%). Type sits on it; nothing covers the cat.
- **Palette (frame.md):** text in `ink` #41384D on a soft `cream` #FFFAF3 veil or card; `coral` #E0894A as the single accent (the ✱ spike, one underline, the URL). Night frames (7, 8) flip to cream text on a translucent ink veil. Never pure black or white.
- **Type:** display ramp (Fraunces 400, sentence case, italic for the soft lines) for captions; `kicker` (JetBrains Mono, uppercase) only for the tiny clock readout and the credit line.
- **Caption placement:** one caption zone per frame, upper-left or lower-left third inside the top 83%; never over the cat.
- **Motion grammar:** power3 long-tail settles; words enter by per-word staggered reveal or hard-cut word swap on their cue; footage itself carries the camera move (slow push in the renders) so the type layer never pans or breathes. Held reads after each last line.
- **Rhythm:** Frames 2 and 7 are breathers (one slow line, long hold). Frame 5 is the fast climax (three hard-cut sub-shots). Frame 8 holds the URL to the last frame.
- **Negative list:** no bouncy/elastic eases, no infinite loops, no floating bokeh, no purple AI gradients, no fake UI chrome, no cursors except the real page in Frame 4, no text over the cat's face, no slideshow front-loading, no screensaver drift on the type layer.


## Frame 1 — Someone lives here

- type: hook
- blueprint: kinetic-type-beats
- duration: 4s
- poster: 3s
- transition_in: cut
- status: animated
- scene: Close on the ginger cat asleep in the window light; three short serif lines land one by one
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c02-cat-sunbeam.mp4
- src: compositions/frames/01-hook.html
- focal: clips/c02-cat-sunbeam.mp4
- roles: c02-cat-sunbeam = background (full strength)

Adapt (kinetic-type-beats): keep the signature beat-by-beat statement build; the lines stack instead of swapping, over live footage instead of a bare canvas.
Scene 1 (0.0–1.1s): full-bleed clip of the sleeping cat in the sun; "A small room." enters upper-left third by per-word staggered reveal (`dynamic-content-sequencing`), display-italic, ink on a faint cream veil strip. Rule-of-thirds, text ~35% width.
Scene 2 (1.1–2.2s): "A big window." lands beneath it on its cue, same move.
Scene 3 (2.2–4.0s): "And someone who lives here." lands as the third line, the word "someone" in coral; the petting heart rises in the footage; hold still to the cut.


Open on the payoff creature, not the product name. The cat breathing in the sun
patch is the hook; the three beats name the room like a picture book. The heart
that floats up at ~2.3s in the clip (the cat is petted) lands just after the last
line.

## Frame 2 — Cat Room

- type: product_intro
- blueprint: titlecard-reveal
- duration: 4s
- poster: 2.5s
- transition_in: crossfade
- status: animated
- scene: The whole isometric room in morning light, slow push-in; the wordmark "Cat Room" and one line under it
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c01-morning-wide.mp4
- src: compositions/frames/02-intro.html
- focal: clips/c01-morning-wide.mp4
- roles: c01-morning-wide = background (full strength)

Reproduce (titlecard-reveal): one restrained move, then a still hold.
Scene 1 (0.0–0.8s): the whole room in morning light, footage only (its own slow push-in is the camera).
Scene 2 (0.8–2.2s): wordmark "Cat Room" rises in by slide-up crossfade upper-left, display-cover size, ink, with the coral ✱ spike beside it. Asymmetric 70/30 against the room.
Scene 3 (2.2–4.0s): the line "a little world that lives on its own" fades up under it in display-italic at lead size; hold.


Name the product over the establishing wide. Restrained: one title, one line,
the room does the rest.

## Frame 3 — The cat follows the sun

- type: benefit_highlight
- blueprint: titlecard-reveal
- duration: 5s
- poster: 3s
- transition_in: cut
- status: animated
- scene: A day in fast-forward: the sun patch sweeps across the floor, dusk falls, the lantern lights up
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c09-timelapse.mp4
- src: compositions/frames/03-sun.html
- focal: clips/c09-timelapse.mp4
- roles: c09-timelapse = background (full strength)

Adapt (titlecard-reveal): two lines instead of one, each on its own cue; a live clock readout is the only moving type.
Scene 1 (0.0–0.4s): day-in-fast-forward footage; a tiny kicker clock readout in the top-left ticks from 09:00 upward (deterministic count tied to the timeline, `counting-dynamic-scale` without the scale), cream pill.
Scene 2 (0.4–2.0s): "The sun moves." enters lower-left third by per-word reveal, headline size.
Scene 3 (2.0–5.0s): "The cat follows it." lands beneath, "follows" underlined by a coral marker sweep (`css-marker-patterns`); hold while the light keeps moving in the footage.


The core loop in one shot: light moves, warmth moves, the cat moves. A small
clock readout ticking in the corner sells "a whole day" without words.

## Frame 4 — Add things

- type: feature_showcase
- blueprint: cursor-ui-demo
- duration: 5s
- poster: 3.5s
- transition_in: crossfade
- status: animated
- scene: The real page with the dresser open; a cat tree, a box and a floor lamp appear in the room one after another
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c11-ui-dresser.mp4
- src: compositions/frames/04-dresser.html
- focal: clips/c11-ui-dresser.mp4
- roles: c11-ui-dresser = background (full strength, real page UI)

Adapt (cursor-ui-demo): the real page recording replaces a reconstructed UI; no synthetic cursor, the items appearing are the state changes.
Scene 1 (0.0–1.1s): the real page with the dresser panel on the right; "Open the dresser." enters as a small cream card top-center-left by slide-up crossfade, headline size.
Scene 2 (1.1–3.3s): as items pop into the room (cat tree 1.2s, box 2.3s), a thin coral hairline draws from the dresser toward each (`svg-path-draw`), then fades.
Scene 3 (3.3–5.0s): "Add things." lands under the first line in display-italic on the lamp's arrival; hold.


The only UI shot: proves it is a real, interactive page. Items pop in at 1.2s,
2.3s and 3.3s of the clip.

## Frame 5 — It notices

- type: feature_showcase
- blueprint: kinetic-type-beats
- duration: 7.5s
- poster: 1.2s
- transition_in: cut
- status: animated
- scene: Three quick behaviours, one per beat: the cat climbs into the box, bats the yarn ball, chases the red laser dot
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c03-box.mp4, clips/c04-yarn.mp4, clips/c05-laser.mp4
- src: compositions/frames/05-mine.html
- focal: clips/c03-box.mp4
- roles: c03-box = background (sub-shot 1) · c04-yarn = background (sub-shot 2) · c05-laser = background (sub-shot 3)

Reproduce (kinetic-type-beats): the fixed line with one swapping slot, hard-cut in step with the footage cuts — the signature in-place token swap.
Scene 1 (0.0–2.5s): box clip (data-media-start 0.6s: the cat reaches the box and hops in); caption upper-left "A box?" then "Mine." hard-cut in at 1.4s in coral italic.
Scene 2 (2.5–5.0s): hard cut to the yarn clip (data-media-start 0.6s); "Yarn?" then "Mine." at 3.9s — same position, the slot swaps.
Scene 3 (5.0–7.5s): hard cut to the laser clip (data-media-start 1.5s); "The red dot?" then a beat, "Mine." at 6.6s; hold.


The joke of the video: each thing you add rewires the cat. Three hard-cut
sub-shots of ~2.5s, the caption word swapping in place each time.

## Frame 6 — Weather and visitors

- type: benefit_highlight
- blueprint: compose
- duration: 5s
- poster: 3s
- transition_in: crossfade
- status: animated
- scene: Left panel, sparrows land on the feeder outside the window; right panel, rain streaks the glass; two short captions
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c06-birds.mp4, clips/c07-rain.mp4
- src: compositions/frames/06-world.html
- focal: clips/c06-birds.mp4
- roles: c06-birds = supporting (left panel video) · c07-rain = supporting (right panel video)

Compose: a split-screen of two live clips on a cream ground. The videos are hoisted, untransformable host videos, so the panels appear by timing (data-start) and the motion lives in the frame's own layer: a cream ground, rounded card frames with the card shadow drawn around each video slot, and the captions.
Scene 1 (0.0–1.2s): cream ground; left card frame draws in (slide-up crossfade of its border and shadow) around the birds video, which is visible from 0.0s in the left slot (x 96, y 130, 846×476).
Scene 2 (1.2–2.4s): the right card frame draws in the same way; the rain video starts at 1.2s in the right slot (x 978, y 130, 846×476).
Scene 3 (2.4–5.0s): captions under each card in display-italic headline size, ink: "Birds drop by." (left, 2.4s) and "Rain rolls in." (right, 3.2s), per-word staggered reveal; hold. Both captions stay above y 880.

The world outside reaches in. Two panels, equal weight, both live.

## Frame 7 — Dusk

- type: benefit_highlight
- blueprint: titlecard-reveal
- duration: 5s
- poster: 3.5s
- transition_in: crossfade
- status: animated
- scene: Evening falls; the radio plays with notes rising from it, the floor lamp clicks on, the candle flickers
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c08-dusk-radio.mp4
- src: compositions/frames/07-dusk.html
- focal: clips/c08-dusk-radio.mp4
- roles: c08-dusk-radio = background (full strength)

Reproduce (titlecard-reveal): the breather; one restrained move, then stillness.
Scene 1 (0.0–1.5s): dusk footage, the radio's notes rising; nothing else.
Scene 2 (1.5–3.0s): "Lo-fi on the radio." fades up lower-left in cream italic on a translucent ink veil.
Scene 3 (3.0–5.0s): "Lamps at dusk." joins beneath as the floor lamp clicks on in the footage; hold still.


The mood beat and the sound source: the music you are hearing comes from this
radio.

## Frame 8 — Come in

- type: cta
- blueprint: logo-assemble-lockup
- duration: 5.5s
- poster: 4s
- transition_in: crossfade
- status: animated
- scene: The room at night slowly turning; wordmark, URL and a small credit line settle over it
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c10-night-turn.mp4
- src: compositions/frames/08-cta.html
- focal: clips/c10-night-turn.mp4
- roles: c10-night-turn = background (dimmed ~75% under an ink veil)

Adapt (logo-assemble-lockup): the wordmark comes to exist letter by letter over the slowly turning room instead of from abstract parts; keep the build-then-lock signature.
Scene 1 (0.0–1.4s): the night room turning; "Cat Room" assembles letter by letter centered (per-letter staggered rise), display-cover, cream.
Scene 2 (1.4–2.8s): the coral ✱ spike draws in beside it (`svg-path-draw`); the URL "rooms.krasnoperov.me" types in beneath in coral mono.
Scene 3 (2.8–5.5s): a small kicker credit line "made with Claude · Blender · makefx" fades in near the bottom of the safe area; everything holds to the last frame.


End on the invitation. The URL holds to the last frame.
