# Task: make Cat Room fast (Lighthouse)

You are in `/home/alv/projects/cat-room-perf`, a git worktree of the Cat Room
project on branch `perf`. It is a single-page Three.js room: `index.html`
(all code inline, Three.js r180 from jsDelivr via an import map), images in
`img/`, audio in `audio/`, glTF models in `models/` and `models/props/`.
`./build.sh` collects the served site into `dist/`; production is
https://rooms.krasnoperov.me (Cloudflare Workers static assets, headers from
`dist/_headers`).

Another agent is actively changing `index.html` on the main branch (props,
cat behaviour). Your changes will be merged into that, so **keep edits to
`index.html` small and surgical** (head tags, loading order, lazy loading,
render-loop throttling) and put everything else in the build step, new
small files, or `_headers`. Do not change how the room looks or behaves.

## Goal

Maximise the Lighthouse **mobile** Performance score (default Lighthouse
throttling) of the built site, and keep Accessibility, Best Practices and
SEO at 90+ (fix what they flag if it is cheap). Also make desktop fast.
Report scores and the key metrics (FCP, LCP, TBT, CLS, Speed Index) before
and after.

## How to measure

1. `./build.sh`
2. Serve `dist/` on port 8124: `python3 -m http.server 8124 --bind 127.0.0.1 --directory dist` (in the background).
3. Lighthouse with the Playwright Chromium:
   `CHROME_PATH=/home/alv/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome npx --yes lighthouse@13 http://127.0.0.1:8124/ --chrome-flags="--headless=new --use-angle=swiftshader --enable-unsafe-swiftshader" --output=json --output-path=/tmp/lh.json --quiet`
   (add `--preset=desktop` for desktop). Read the scores and the top
   opportunities and diagnostics from the JSON. Note that WebGL runs on
   SwiftShader here, so main-thread render cost is exaggerated; that is fine
   for relative comparisons.
4. Also check visually that the page still renders the same:
   `node shot.mjs /tmp/after.png "t=17.6&paused=1&clean=1" 1280 800 4000`
   with `BASE=http://127.0.0.1:8124/` set (shot.mjs reads `BASE`), and
   compare with a render from before your changes.

## Ideas to try (measure each, keep what helps)

- Load-time: `modulepreload` for three.module.js and the addons actually
  used, preconnect, font loading (`display=swap`, fewer weights, or
  self-hosted subsets), inline critical CSS is already inline.
- Assets: compress GLBs (e.g. `npx @gltf-transform/cli optimize` with
  meshopt or quantize + resize; if you use meshopt, wire `MeshoptDecoder`
  into the GLTFLoader in index.html), downsize and re-encode images (webp or
  avif at the sizes actually displayed), audio at lower bitrate. Load props'
  and plants' GLBs and audio lazily, only when needed.
- Main thread: defer the heavy WebGL start until after first paint
  (requestIdleCallback or after `load`), cap devicePixelRatio on mobile,
  lower shadow map and post-processing resolution on small screens, skip
  rendering when the tab is hidden, avoid per-frame allocations that the
  profiler flags (e.g. rebuilding TubeGeometry every frame for the thread,
  new Vector3 in hot loops) if they show up in TBT.
- Caching: long `Cache-Control` for hashed or versioned assets in
  `_headers`, sensible cache for HTML.
- SEO/Best practices: meta description exists; add what is flagged.

Iterate: change, rebuild, re-run Lighthouse, keep or revert. At least five
measured iterations. Commit your work on the `perf` branch in small commits
with clear messages (no co-author lines). Do not deploy. At the end write
`PERF_REPORT.md` with the before/after table, what you changed and why, and
anything you tried that did not help.
