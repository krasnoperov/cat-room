import { build } from 'esbuild';
import { createHash } from 'node:crypto';
import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { basename, extname, join } from 'node:path';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptEncoder } from 'meshoptimizer/encoder';

// Keep index.html useful without a build. Only the served copy is bundled.
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex').slice(0, 12);
async function asset(path) {
  const bytes = await readFile(path);
  const ext = extname(path);
  const name = `${basename(path, ext)}.${hash(bytes)}${ext}`;
  await writeFile(`dist/assets/${name}`, bytes);
  return `assets/${name}`;
}

await rm('dist', { recursive: true, force: true });
await mkdir('dist/assets', { recursive: true });
let html = await readFile('index.html', 'utf8');
const script = /<script type="module">([\s\S]*?)<\/script>/;
const match = html.match(script);
if (!match) throw new Error('Expected the inline room module in index.html');
const result = await build({
  stdin: { contents: match[1], resolveDir: process.cwd(), sourcefile: 'room.js' },
  bundle: true, minify: true, format: 'esm', target: 'es2022',
  sourcemap: 'external', outfile: 'room.js',
  plugins: [{ name: 'three-cdn', setup(build) {
    build.onResolve({ filter: /^three$/ }, () => ({ path: 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.min.js', external: true }));
  } }],
  write: false, legalComments: 'eof',
});
const map = result.outputFiles.find((file) => file.path.endsWith('.map')).contents;
const mapName = `room.${hash(map)}.js.map`;
await writeFile(`dist/assets/${mapName}`, map);
const js = Buffer.from(`${result.outputFiles.find((file) => file.path.endsWith('.js')).text}\n//# sourceMappingURL=${mapName}\n`);
const entry = `assets/room.${hash(js)}.js`;
await writeFile(`dist/${entry}`, js);
// Start fetching the room immediately after the shell has had a paint. Two
// animation frames ensure this even when a timer runs before the first paint.
html = html.replace(script, `<script type="module">requestAnimationFrame(() => requestAnimationFrame(() => import('./${entry}')));</script>`)
  .replace(/<script type="importmap">[\s\S]*?<\/script>\s*/, '')
  .replace(/<link[^>]+(?:cdn\.jsdelivr\.net|fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*>\n/g, '');

// These are the exact font files used by the original Google Fonts response.
let fonts = '';
for (const [family, file, style, weight] of [
  ['Fraunces', 'fraunces-normal-latin.woff2', 'normal', '500'],
  ['Fraunces', 'fraunces-italic-latin.woff2', 'italic', '400'],
  ['Nunito', 'nunito-latin.woff2', 'normal', '500 700'],
]) {
  const url = await asset(`fonts/${file}`);
  fonts += `@font-face{font-family:'${family}';font-style:${style};font-weight:${weight};font-display:swap;src:url('${url}') format('woff2');}\n`;
  html = html.replace('</head>', `<link rel="preload" href="${url}" as="font" type="font/woff2" crossorigin>\n</head>`);
}
html = html.replace('<style>', `<style>\n${fonts}`);
await writeFile('dist/index.html', html);
for (const dir of ['img', 'audio']) await cp(dir, `dist/${dir}`, { recursive: true });
await MeshoptEncoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.encoder': MeshoptEncoder });
async function models(dir) {
  await mkdir(`dist/${dir}`, { recursive: true });
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory() && entry.name !== '__pycache__') await models(path);
    else if (entry.isFile() && entry.name.endsWith('.glb')) {
      // Compress original attributes without quantizing, simplifying, joining,
      // or renaming: animation and prop behaviour rely on the named hierarchy.
      const document = await io.read(path);
      document.createExtension(EXTMeshoptCompression).setRequired(true)
        .setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.QUANTIZE });
      await io.write(`dist/${path}`, document);
    }
  }
}
await models('models');
for (const file of ['_headers', 'favicon.ico', 'robots.txt', 'sitemap.xml', 'site.webmanifest']) await cp(file, `dist/${file}`);
await mkdir('dist/licenses', { recursive: true });
for (const [name, path] of [
  ['three', 'three/LICENSE'],
  ['meshoptimizer', 'meshoptimizer/LICENSE.md'],
]) await cp(`node_modules/${path}`, `dist/licenses/${name}.txt`);
for (const family of ['fraunces', 'nunito']) await cp(`fonts/${family}-OFL.txt`, `dist/licenses/${family}.txt`);
console.log(`Built ${entry} (${Math.round(js.length / 1024)} KiB), local fonts and all room models.`);
