// Generates house.glb, the standing 3D test asset for House View's live
// verification (see ../README.md). Hand-authored geometry, not a
// downloaded/licensed asset -- there's no external license question at
// all, unlike every asset source tried before landing here:
//   - Khronos glTF-Sample-Assets' Sponza: actual model files are under
//     the CRYENGINE Limited License Agreement (a EULA, not CC0/permissive).
//   - Poly Haven (otherwise fully CC0): searched their entire model
//     catalog (521 models, by category and by keyword) -- no standalone
//     house/cottage/cabin exists, only architectural fragments (gates,
//     facades, fortifications).
//   - floor3d-card's own repo/wiki: no bundled example model; its wiki
//     points at an unlicensed third-party .sh3d file.
//
// A few box/cone primitives is a small, honest, obviously house-shaped
// scene -- walls, a pyramidal roof, a door, three windows, a chimney --
// good enough to confirm raycasting/marker-placement across several
// distinct real surfaces, which is the entire point of the 3D test asset.
//
// NOTE: three.js's own GLTFExporter hangs indefinitely under plain
// Node (confirmed: "Detected unsettled top-level await", no thrown
// error) -- it silently depends on browser-only APIs (FileReader,
// Canvas) even for a scene with zero image textures. This script
// hand-assembles the glTF 2.0 JSON + binary buffer directly instead,
// which is well within reach for this few solid-color primitives and
// sidesteps that dependency entirely.
//
// Usage: node generate-test-house.mjs [output-path]
// Requires only `three` (already a frontend/ dependency) -- run from
// this directory after `npm install`, or point node's module resolution
// at frontend/node_modules.

import * as THREE from "three";
import fs from "fs";

const outputPath = process.argv[2] ?? "house.glb";

function primitiveFromGeometry(geometry) {
  const pos = geometry.attributes.position;
  const norm = geometry.attributes.normal;
  const idx = geometry.index;
  return {
    positions: Float32Array.from(pos.array),
    normals: Float32Array.from(norm.array),
    indices: idx.array instanceof Uint32Array ? Uint32Array.from(idx.array) : Uint16Array.from(idx.array),
    vertexCount: pos.count,
  };
}

const parts = [];
function addPart(name, geometry, colorRgb, transform) {
  geometry.applyMatrix4(transform);
  geometry.computeVertexNormals();
  parts.push({ name, color: colorRgb, ...primitiveFromGeometry(geometry) });
}

const WALL_W = 6, WALL_D = 5, WALL_H = 3, ROOF_H = 2;

addPart(
  "Walls",
  new THREE.BoxGeometry(WALL_W, WALL_H, WALL_D),
  [0.85, 0.79, 0.66],
  new THREE.Matrix4().makeTranslation(0, WALL_H / 2, 0),
);

addPart(
  "Roof",
  new THREE.ConeGeometry(Math.hypot(WALL_W, WALL_D) / 2 + 0.6, ROOF_H, 4),
  [0.55, 0.23, 0.23],
  new THREE.Matrix4().multiplyMatrices(
    new THREE.Matrix4().makeTranslation(0, WALL_H + ROOF_H / 2, 0),
    new THREE.Matrix4().makeRotationY(Math.PI / 4),
  ),
);

addPart(
  "Door",
  new THREE.BoxGeometry(0.9, 2, 0.06),
  [0.29, 0.18, 0.11],
  new THREE.Matrix4().makeTranslation(0, 1, WALL_D / 2 + 0.03),
);

addPart(
  "WindowFrontLeft",
  new THREE.BoxGeometry(0.8, 0.8, 0.06),
  [0.62, 0.84, 0.88],
  new THREE.Matrix4().makeTranslation(-1.8, 1.8, WALL_D / 2 + 0.03),
);

addPart(
  "WindowFrontRight",
  new THREE.BoxGeometry(0.8, 0.8, 0.06),
  [0.62, 0.84, 0.88],
  new THREE.Matrix4().makeTranslation(1.8, 1.8, WALL_D / 2 + 0.03),
);

addPart(
  "WindowSide",
  new THREE.BoxGeometry(0.8, 0.8, 0.06),
  [0.62, 0.84, 0.88],
  new THREE.Matrix4().multiplyMatrices(
    new THREE.Matrix4().makeTranslation(WALL_W / 2 + 0.03, 1.8, 0),
    new THREE.Matrix4().makeRotationY(Math.PI / 2),
  ),
);

addPart(
  "Chimney",
  new THREE.BoxGeometry(0.5, 1.4, 0.5),
  [0.42, 0.42, 0.42],
  new THREE.Matrix4().makeTranslation(1.5, WALL_H + ROOF_H * 0.7 + 0.7, -1),
);

// ── Pack into a single glTF 2.0 binary (.glb) by hand ──────────────
const bufferChunks = [];
let byteOffset = 0;
function pushChunk(arr) {
  const bytes = new Uint8Array(arr.buffer, arr.byteOffset, arr.byteLength);
  const padded = (bytes.byteLength + 3) & ~3; // glTF buffer views must be 4-byte aligned
  const out = new Uint8Array(padded);
  out.set(bytes);
  bufferChunks.push(out);
  const chunkOffset = byteOffset;
  byteOffset += padded;
  return { byteOffset: chunkOffset, byteLength: bytes.byteLength };
}

const bufferViews = [];
const accessors = [];
const meshes = [];
const materials = [];
const nodes = [];

parts.forEach((part, i) => {
  const posRange = pushChunk(part.positions);
  const posViewIdx = bufferViews.length;
  bufferViews.push({ buffer: 0, byteOffset: posRange.byteOffset, byteLength: posRange.byteLength, target: 34962 });

  const normRange = pushChunk(part.normals);
  const normViewIdx = bufferViews.length;
  bufferViews.push({ buffer: 0, byteOffset: normRange.byteOffset, byteLength: normRange.byteLength, target: 34962 });

  const idxRange = pushChunk(part.indices);
  const idxViewIdx = bufferViews.length;
  bufferViews.push({ buffer: 0, byteOffset: idxRange.byteOffset, byteLength: idxRange.byteLength, target: 34963 });

  let minX = Infinity, minY = Infinity, minZ = Infinity, maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
  for (let v = 0; v < part.vertexCount; v++) {
    const x = part.positions[v * 3], y = part.positions[v * 3 + 1], z = part.positions[v * 3 + 2];
    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minY = Math.min(minY, y); maxY = Math.max(maxY, y);
    minZ = Math.min(minZ, z); maxZ = Math.max(maxZ, z);
  }

  const posAccessorIdx = accessors.length;
  accessors.push({
    bufferView: posViewIdx, componentType: 5126, count: part.vertexCount, type: "VEC3",
    min: [minX, minY, minZ], max: [maxX, maxY, maxZ],
  });
  const normAccessorIdx = accessors.length;
  accessors.push({ bufferView: normViewIdx, componentType: 5126, count: part.vertexCount, type: "VEC3" });
  const idxAccessorIdx = accessors.length;
  accessors.push({
    bufferView: idxViewIdx,
    componentType: part.indices instanceof Uint32Array ? 5125 : 5123,
    count: part.indices.length,
    type: "SCALAR",
  });

  materials.push({
    name: part.name + "Material",
    pbrMetallicRoughness: { baseColorFactor: [...part.color, 1.0], metallicFactor: 0.0, roughnessFactor: 0.9 },
  });

  meshes.push({
    name: part.name,
    primitives: [{ attributes: { POSITION: posAccessorIdx, NORMAL: normAccessorIdx }, indices: idxAccessorIdx, material: i }],
  });

  nodes.push({ name: part.name, mesh: i });
});

const totalBufferBytes = byteOffset;
const binBuffer = new Uint8Array(totalBufferBytes);
let writeOffset = 0;
for (const chunk of bufferChunks) {
  binBuffer.set(chunk, writeOffset);
  writeOffset += chunk.byteLength;
}

const gltf = {
  asset: { version: "2.0", generator: "ChromaCal test-asset generator (hand-authored, no external model)" },
  scene: 0,
  scenes: [{ nodes: nodes.map((_, i) => i) }],
  nodes,
  meshes,
  materials,
  accessors,
  bufferViews,
  buffers: [{ byteLength: totalBufferBytes }],
};

const jsonBytes = new TextEncoder().encode(JSON.stringify(gltf));
const jsonPadded = (jsonBytes.byteLength + 3) & ~3;
const jsonChunk = new Uint8Array(jsonPadded);
jsonChunk.set(jsonBytes);
for (let i = jsonBytes.byteLength; i < jsonPadded; i++) jsonChunk[i] = 0x20; // space-pad per spec

const binPadded = (binBuffer.byteLength + 3) & ~3;
const binChunk = new Uint8Array(binPadded);
binChunk.set(binBuffer);

const totalLength = 12 + (8 + jsonChunk.byteLength) + (8 + binChunk.byteLength);
const out = new Uint8Array(totalLength);
const dv = new DataView(out.buffer);
let o = 0;
dv.setUint32(o, 0x46546c67, true); o += 4; // "glTF"
dv.setUint32(o, 2, true); o += 4; // version
dv.setUint32(o, totalLength, true); o += 4;

dv.setUint32(o, jsonChunk.byteLength, true); o += 4;
dv.setUint32(o, 0x4e4f534a, true); o += 4; // "JSON"
out.set(jsonChunk, o); o += jsonChunk.byteLength;

dv.setUint32(o, binChunk.byteLength, true); o += 4;
dv.setUint32(o, 0x004e4942, true); o += 4; // "BIN\0"
out.set(binChunk, o); o += binChunk.byteLength;

fs.writeFileSync(outputPath, Buffer.from(out));
console.log(`wrote ${outputPath}, ${out.byteLength} bytes, ${parts.length} parts`);
