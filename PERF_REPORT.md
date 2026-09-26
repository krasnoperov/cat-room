# Cat Room performance report

Measured September 26, 2026, on branch `perf`, starting at `ec6c4b3`.

## Results

All runs used the requested Python server on port 8124, Lighthouse 13 default
mobile simulated throttling (desktop uses `--preset=desktop`), and Playwright
Chromium 153 with SwiftShader. Browsers were run sequentially. The final mobile
row contains the median of each metric across three unchanged-build runs;
mobile scores were 54, 53, and 51. Baselines and desktop are single runs.

| Configuration | Performance | FCP | LCP | TBT | CLS | Speed Index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mobile before | 31 | 4.60 s | 6.43 s | 7,224 ms | 0.000019 | 8.21 s |
| Mobile after (three-run medians) | 53 | 2.04 s | 4.22 s | 2,699 ms | 0.000010 | 5.09 s |
| Desktop before | 61 | 0.99 s | 1.15 s | 1,657 ms | 0.000400 | 2.50 s |
| Desktop after | 71 | 0.49 s | 0.97 s | 804 ms | 0.000002 | 1.01 s |

| Category | Before, mobile / desktop | After, mobile / desktop |
| --- | ---: | ---: |
| Accessibility | 100 / 100 | 100 / 100 |
| Best Practices | 96 / 96 | 100 / 100 |
| SEO | 100 / 100 | 100 / 100 |

Performance remains below 90 in this software-rendered harness. The changes
improve loading and blocking without reducing pixel ratio, shadow resolution,
postprocessing quality, animation rate, or the source textures/audio. These are
local measurements, not deployed or production-verified scores.

## Retained changes

- The build now includes all 16 plant, prop, bird, and cat GLBs. The old build
  omitted everything except the cat and returned four model 404s at startup.
  Fixing this also restores the intended detailed plants and radio; the final
  scene therefore does more work than the incomplete baseline.
- `build.mjs` bundles/minifies the inline room code and addons, emits source
  maps, and retains the exact Three.js 0.180.0 core on jsDelivr, using its
  minified modules. The local app bundle is about 165 KiB. Source
  `index.html` still works directly with its import map.
- Original Google Fonts Latin files are served locally with inline font-face
  CSS and swap rendering. Normal/italic Fraunces styles and Nunito weights
  were checked against font metadata. Their licenses ship with the build.
- The shell gets a paint opportunity before downloading/initializing the room.
  Construction yields between stages. Initial model loads settle before
  color/normal shader warmup with `compileAsync`; later props remain lazy.
- Meshopt compresses geometry at build time without simplification,
  quantization, hierarchy changes, or source-model edits. Model files shrink
  from 5.20 MiB to 3.34 MiB (36%). Both GLTFLoader instances use Three.js's
  Meshopt decoder. The build preserves material extensions.
- The normals pass reuses the shadow map already updated by the color pass.
  Hidden-document frames skip simulation/rendering; fixed capture stays manual.
- Hashed scripts, maps, and fonts get one-year immutable caching. Unversioned
  HTML/images/models/audio revalidate, so updated assets cannot remain stale
  under a long immutable lifetime. Existing security headers are preserved.
- An inline favicon removes the remaining favicon 404.

## Measured iterations

Each row is a rebuilt mobile run. These are exploratory single-run results,
not isolated causal estimates: software rendering and asynchronous loading
produce variability. The final build restores the two-pass warmup from
iteration 15, yields once after models settle, and includes source maps.

| # | Change tested | Performance | FCP | LCP | TBT | CLS | Speed Index |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Complete model copying, favicon, CDN module hints | 33 | 5.59 s | 6.15 s | 3,899 ms | 0.000016 | 6.02 s |
| 2 | Local minified bundle, local variable fonts, caching headers | 29 | 4.35 s | 6.65 s | 13,095 ms | 0.000011 | 10.91 s |
| 3 | Yield between scene construction stages | 32 | 4.35 s | 5.55 s | 5,726 ms | 0.000029 | 10.02 s |
| 4 | Skip the redundant normal-pass shadow update | 32 | 4.35 s | 5.55 s | 5,959 ms | 0.000031 | 9.85 s |
| 5 | Mobile DPR 1.5 and 1024 shadow experiment | 32 | 4.35 s | 5.55 s | 6,423 ms | 0.000027 | 10.43 s |
| 6 | Start the module after the shell can paint | 38 | 2.56 s | 5.55 s | 3,472 ms | 0.000025 | 8.81 s |
| 7 | Lossless Meshopt geometry compression | 38 | 2.56 s | 5.70 s | 3,098 ms | 0.000030 | 8.75 s |
| 8 | Original font subsets instead of larger font-package variants | 39 | 2.56 s | 5.25 s | 3,143 ms | 0.000029 | 8.63 s |
| 9 | Asynchronous color shader warmup | 49 | 2.56 s | 5.25 s | 1,116 ms | 0.000010 | 5.69 s |
| 10 | Wait for document.fonts.ready (rejected) | 37 | 2.56 s | 5.25 s | 8,796 ms | 0.000004 | 12.55 s |
| 11 | Restore original DPR and 2048 shadows | 45 | 2.56 s | 5.25 s | 1,669 ms | 0.000000 | 6.22 s |
| 12 | Warm up initial models and both scene passes; remove font wait | 43 | 2.56 s | 5.25 s | 2,574 ms | 0.000009 | 5.74 s |
| 13 | Use pinned minified CDN Three.js core; bundle app/addons | 54 | 2.04 s | 4.22 s | 2,742 ms | 0.000010 | 3.40 s |
| 14 | CDN preloads plus visibility guard | 53 | 2.73 s | 3.64 s | 3,157 ms | 0.000009 | 4.77 s |
| 15 | Correct normal/italic font mapping; remove preloads | 52 | 2.04 s | 4.22 s | 2,679 ms | 0.000010 | 4.94 s |
| 16 | Progressive models plus color-only warmup (rejected) | 48 | 2.04 s | 4.22 s | 5,287 ms | 0.000020 | 6.41 s |


What did not help:

- Bundling the entire Three.js core locally increased transfer under Python's
  uncompressed server, despite minification. Keeping the pinned minified core
  on its original compressed CDN performed better.
- The font-package variants transferred more data than the original subsets.
  They were replaced; no font-package dependency remains.
- Reduced mobile pixel ratio/shadow size did not show a reliable score gain.
  Both reductions were reverted to preserve quality.
- Waiting on `document.fonts.ready` did not help. Extra CDN module preloads
  also failed to improve the measured score and were removed.
- Color-only warmup while models arrived progressively produced more blocking
  in the final comparison; the final version warms both scene passes after
  initial models settle. Model failures do not reject the room startup.
- Skipping the duplicate shadow pass alone did not move the score. It still
  removes an unnecessary shadow update without changing the rendered scene.

## Validation and reproduction

`npm ci`, `./build.sh`, and `npm run test:models` are the build/asset-check
commands. The model check decodes using the browser's Three.js Meshopt decoder
and compares all 16 models: named hierarchy, vertex attributes, triangle
winding, and skin bindings match. Transform differences are below 1e-6 because
the glTF writer omits nearly identity values.

The exact Lighthouse command used was:

```bash
python3 -m http.server 8124 --bind 127.0.0.1 --directory dist
# In another terminal:
npm_config_cache=/tmp/cat-perf-npm \
CHROME_PATH=/home/alv/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome \
npx --yes lighthouse@13 http://127.0.0.1:8124/ \
  --chrome-flags="--headless=new --use-angle=swiftshader --enable-unsafe-swiftshader" \
  --output=json --output-path=/tmp/cat-lh.json --quiet
# Add --preset=desktop for desktop.
```

Raw reports are in `/tmp/cat-lh-baseline-{mobile,desktop}.json`,
`/tmp/cat-lh-01-mobile.json` through `/tmp/cat-lh-16-mobile.json`,
`/tmp/cat-lh-final-mobile-{1,2,3}.json`, and
`/tmp/cat-lh-final-desktop.json`. The iteration 3 trace was also saved.

Fresh `npm ci`, `./build.sh`, `npm run test:models`, JavaScript/shell syntax
checks, and `git diff --check` passed. A clean dependency reinstall/rebuild
produced identical HTML and application-bundle SHA-256 hashes.

Playwright checks passed for:

- Desktop pause/resume by keyboard, rain on/off, rotation in both directions,
  shelf add/remove, lazy yarn-model loading, and no audio requests before a
  gesture. The cat model was present.
- Photo mode, PNG download, exit photo mode, and a generated room-share URL.
- A synthetic hidden-document probe: no frame-counter growth while hidden,
  then rendering resumes. Browser-native background throttling was not
  separately benchmarked.
- Fixed-step capture: exactly two startup frames, no unsolicited frames, and
  exactly three more after `tick(3)`.
- A 390×844 touch viewport: room rendering, dock bounds, shelf open/close.
- Aborted cat/radio requests: startup and controls still work, with no
  unhandled promise rejection. Normal-load checks had no page errors or HTTP
  failures.

The requested 1280×800 screenshot command was run before and after with
`t=17.6&paused=1&clean=1`. The original screenshot is
`/tmp/cat-before.png`; `/tmp/cat-models-reference.png` is the baseline with
missing models restored. That second reference separates the build repair
from performance changes. The final `/tmp/cat-after.png` was visually compared
with both references: scene layout, materials, lighting, and detailed model
appearance remain consistent. Animation and plant-growth timing prevent a
pixel-identical comparison. UI captures are `/tmp/cat-final-desktop-ui.png`
and `/tmp/cat-final-mobile.png`; the downloaded photo is
`/tmp/cat-photo-download.png`. Screenshots are local artifacts, not committed.

An existing 1280 px layout issue remains: the radio's next-track button covers
the play button. The baseline served on port 8125 reproduced the same hit
target (`nextTrack` at the play button's center). The desktop pause/resume
check therefore used normal keyboard focus and Enter, not a forced click.
This pre-existing layout issue was left outside the performance edits.

Harness boundaries:

- Python's HTTP server does not apply `_headers` or response compression.
  Cloudflare cache behavior was inspected in the generated configuration but
  not tested through a deployment.
- SwiftShader reports that `KHR_parallel_shader_compile` is unsupported;
  Three.js uses the asynchronous API's fallback. Its software rendering cost
  and run-to-run variation limit these scores as predictions of real devices.
- The pre-existing duplicate `windowState` key in `window.__room` triggers
  an esbuild warning. It is unchanged and does not fail the build.

## Delivery boundary

No deployment or PR was made. Repository metadata points outside the writable
workspace, to `/home/alv/projects/cat-room/.git/worktrees/cat-room-perf`.
`git add build.sh index.html` failed with `Read-only file system` when
creating `index.lock`. Consequently the requested commits could not be made;
the validated edits remain in the `perf` worktree, and `PERF_TASK.md` remains
untouched and untracked.

Suggested small commit groups once Git metadata is writable:

1. Build, dependencies, fonts, headers, and model verification.
2. The surgical loading/render changes in `index.html`.
3. README and this measurement report.
