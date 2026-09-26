// Run after ./build.sh. Decode with the same Meshopt version as GLTFLoader.
import assert from 'node:assert/strict';
import { readdir } from 'node:fs/promises';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
let count = 0;
async function check(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = `${dir}/${entry.name}`;
    if (entry.isDirectory() && entry.name !== '__pycache__') await check(path);
    if (!entry.isFile() || !entry.name.endsWith('.glb')) continue;
    const original = (await io.read(path)).getRoot();
    const built = (await io.read(`dist/${path}`)).getRoot();
    const hierarchy = (root) => root.listNodes().map((node) => [node.getName(), node.listChildren().map((child) => child.getName())]);
    assert.deepEqual(hierarchy(built), hierarchy(original), `${path}: named hierarchy`);
    for (let n = 0; n < original.listNodes().length; n++) {
      for (const method of ['getTranslation', 'getRotation', 'getScale']) {
        const a = original.listNodes()[n][method](), b = built.listNodes()[n][method]();
        // The writer omits near-identity transforms within floating-point noise.
        assert(a.every((v, i) => Math.abs(v - b[i]) < 1e-6), `${path}: transform ${n}`);
      }
    }
    assert.equal(built.listMeshes().length, original.listMeshes().length, path);
    for (let m = 0; m < original.listMeshes().length; m++) {
      const a = original.listMeshes()[m].listPrimitives(), b = built.listMeshes()[m].listPrimitives();
      assert.equal(a.length, b.length, path);
      for (let p = 0; p < a.length; p++) {
        for (const semantic of a[p].listSemantics()) {
          assert.deepEqual(b[p].getAttribute(semantic).getArray(), a[p].getAttribute(semantic).getArray(), `${path}: ${semantic}`);
        }
        const ai = a[p].getIndices()?.getArray(), bi = b[p].getIndices()?.getArray();
        if (ai) {
          assert.equal(ai.length, bi.length, path);
          for (let j = 0; j < ai.length; j += 3) {
            // Meshopt may rotate triangle indices, preserving winding and shape.
            assert([0, 1, 2].some((k) => [0, 1, 2].every((n) => ai[j + n] === bi[j + (n + k) % 3])), `${path}: triangle ${j}`);
          }
        }
      }
    }
    const skins = (root) => root.listSkins().map((skin) => [skin.listJoints().map((joint) => joint.getName()), skin.getInverseBindMatrices()?.getArray()]);
    assert.deepEqual(skins(built), skins(original), `${path}: skin bindings`);
    count++;
  }
}
await check('models');
console.log(`Verified ${count} compressed models: hierarchy, transforms, vertex attributes, triangles and skin bindings.`);
