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


## Frame 1 — Shh

- type: hook
- blueprint: zoom-out-workspace-reveal
- duration: 4.5s
- poster: 3.4s
- transition_in: cut
- status: animated
- scene: Extreme close-up of the ginger cat asleep in the sun, shallow miniature focus; a whispered "shh" and a line, then the camera starts to pull back
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c00-hook-pullback.mp4
- src: compositions/frames/01-hook.html
- focal: clips/c00-hook-pullback.mp4
- roles: c00-hook-pullback = background (full strength, data-media-start 0)

Adapt (zoom-out-workspace-reveal): the footage itself carries the signature move — tight on one living detail, then ONE continuous decelerating pull-back to the whole. The type layer only whispers and gets out of the way.
Scene 1 (0.0–0.9s): the frame opens on the sleeping cat filling the screen, blurred edges (tilt-shift in the footage); nothing else for a beat. A warm organic light leak drifts across from the upper-left (adapt the installed `organic-light-leak-overlay` block's look: soft amber blooms, screen blend, low opacity, finite and seek-safe) and fades by 1.6s.
Scene 2 (0.9–2.2s): a tiny lowercase italic "shh." fades in beside the cat's head (upper-right third), cream on a soft ink shadow, display-italic at lead size; at ~0.95s a small heart already rises in the footage.
Scene 3 (2.2–3.4s): "shh." is replaced in place (hard-cut word swap, `discrete-text-sequence`) by "someone is asleep in the sun." in the same spot and style, the word "sun" in coral.
Scene 4 (3.4–4.5s): as the camera pull-back in the footage accelerates, the caption lifts and fades (y −24px, opacity → 0, power3.in) so the reveal is clean; this is the only exit and it is inside the frame because Frame 2 continues the same shot on a hard cut.

Open on a living detail, not a product: the viewer has to lean in to understand what they are looking at, and Frame 2 answers it.

## Frame 2 — Cat Room

- type: product_intro
- blueprint: titlecard-reveal
- duration: 3.5s
- poster: 2.6s
- transition_in: cut
- status: animated
- scene: The same shot continues: the pull-back settles on the whole room floating in the sky; the wordmark lands in the empty sky beside it
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c00-hook-pullback.mp4
- src: compositions/frames/02-intro.html
- focal: clips/c00-hook-pullback.mp4
- roles: c00-hook-pullback = background (full strength, data-media-start 4.5 — seamless continuation of Frame 1)

Reproduce (titlecard-reveal): one restrained move landing in the open sky, then a still hold.
Scene 1 (0.0–1.4s): footage only; the pull-back decelerates and the room settles centre-right, floating in soft blue sky.
Scene 2 (1.4–2.4s): in the open sky upper-left, the wordmark "Cat Room" assembles letter by letter (per-letter rise with a long power3 tail, 0.035s stagger), display-cover size, ink; the coral ✱ spike pops in last beside it (scale 0.6→1, power3.out, no overshoot).
Scene 3 (2.4–3.5s): "a little world that lives on its own" fades up beneath in display-italic at lead size, ink at 80%; hold dead still.

The answer to the hook: the sleeping cat lives in this.

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
- duration: 8s
- poster: 7.2s
- transition_in: crossfade
- status: animated
- scene: Night. The room, every lamp lit, swings round to show its doorway, then recedes into the indigo sky; stars come out; the wordmark and URL settle above it
- voiceover: "(no narration: music bed only; the on-screen copy is quoted in the Scene lines and IS meant to be rendered)"
- asset_candidates: clips/c12-finale.mp4
- src: compositions/frames/08-cta.html
- focal: clips/c12-finale.mp4
- roles: c12-finale = background (full strength; the sky is part of the footage)

Adapt (logo-assemble-lockup, motion borrowed from the installed `logo-brand-close` component): the lockup comes to exist letter by letter in the sky that opens up as the room recedes; keep the build-then-lock signature and end on a dead-still hold.
Scene 1 (0.0–2.8s): footage only; the room turns (lamps glowing, notes rising from the radio). No type while it turns.
Scene 2 (2.8–4.6s): as the room recedes and drops, a field of ~70 tiny cream stars fades in across the upper sky, deterministic positions from a seeded hash, each fading in on its own staggered time with a single finite twinkle (opacity 0.3→1→0.6), none in the lower third; the wordmark "Cat Room" cascades letter by letter into a centered lockup in the upper third (the `logo-brand-close` cascade: per-letter fade + rise with a long expo tail while the whole word settles from scale 1.04 to 1), cream, display-cover.
Scene 3 (4.6–5.6s): the coral ✱ spike arrives last beside the wordmark with a decisive pop (the component's brand-period beat, recoloured to coral); a soft coral glow blooms behind it once and settles.
Scene 4 (5.6–8.0s): "rooms.krasnoperov.me" settles beneath in wide-tracked JetBrains Mono (letter-spacing easing from 0.5em to 0.18em as it fades in, the component's URL tracking settle), coral; at 6.4s a small kicker "made with Claude · Blender · makefx" fades in near the bottom of the safe area, cream at 70%. Everything holds dead still to the last frame; no exit.

End on the invitation, in the room's own night sky.
