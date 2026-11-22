// SCULPTED BODIES ON THE GPU (2026-11-04): every creature drawn as ONE skinned mesh -- a `"kind": "sculpt"` one
// (bodyspec.js sculpted, the hedgehog) or any other converted from its parts when it joined a herd (bodyspec.js
// sculptOf: its parts kept as its bones, their shapes made a field). Its surface, eyeballs, thin details and coat are
// built once per body (bodymesh.js: a field of blended shapes, meshed, simplified to two budgets) -- in WORKERS
// (bodyworker.js), so the world does not stall while a menagerie is meshed, and KEPT in the browser's IndexedDB by
// the body's own hash and the mesher's (a reload finds them built). An animal is not drawn until its mesh is in.
// A body's SHAPE (the meshing: nearly all the work) is built once for every look that shares it -- the coats of a
// species, a variant that only resizes it or changes its horns and fins, its young -- and each look DRESSED on it
// (bodymesh.js buildShape / dressBody; "SHAPES SHARED" below); the coats' geometry is one GPU buffer, their paint one each.
// Each animal its own SkinnedMesh over the shared geometry; its bone matrices written here, straight from the frames
// the composite posed (skeleton.js keeps them: an._bm):
//     bone j = W_j * S(f) * RestInv_j
// (W_j the bone's world frame now, RestInv_j the inverse of its frame in the rest pose the shapes were made in, f the
// animal's size against the definition's: a young one scaled), so three's skinning puts every vertex where its bones
// are. Past `mesh.far` metres from the eye the coarse mesh (and its sparser coat) stands in; once the creature is only a
// few dozen pixels across a third, very coarse one (bodyfar.js); and below a couple of pixels it is not drawn at all,
// nor posed (BODY_LOD, below).
// Shaded as the heads and the manes are (heads.js faceMaterial: half-Lambert ramp; fibres and a softer sheen on
// hairMask; the nose and the eyes wet) -- its paint the vertex colour with the composite's own PATTERNS laid over it
// (banner_wgsl patternAt: stripes, spots, scales... by the frame of the shape each vertex is nearest: bodymesh.js).
import * as THREE from "three";
import { wgslFn, attribute, varying, positionWorld, positionLocal, normalLocal, vec3, vec4, Fn, storage, uint, int, ivec2, add, normalize,
         textureLoad, textureSize, instanceIndex, drawIndex, vertexIndex } from "three/tsl";
import { batchPool } from "./batchpool.js";
import { faceMaterial, SHADE } from "./heads.js";
import { buildShape, dressBody, shapeSpec, paintSpec } from "./bodymesh.js";
import { withVeryFar } from "./bodyfar.js";   // (the third mesh, very far: made with the dress)
import { familyOf } from "./bodyspec.js";   // (the other looks of a body's definition: its coats, variants and young -- they may share its shape)
import { coatAt } from "./coatpat.js";
import { halfOf } from "./bodyhalf.js";   // (the coats: a tiger's stripes, a leopard's rosettes, a feather's eye -- and the composite's patternAt for the rest)

// ---- building: workers, and what they built kept -----------------------------------------------------------------
const WORKERS = Math.max(1, Math.min(4, (globalThis.navigator?.hardwareConcurrency ?? 4) - 2));
let pool = null, jobs = 0;
const waiting = new Map();
function workers() {
  if (pool) return pool;
  pool = [];
  try {
    for (let i = 0; i < WORKERS; i++) {
      const w = new Worker(new URL("./bodyworker.js", import.meta.url), { type: "module" });
      w.onmessage = ({ data }) => { const job = waiting.get(data.id); waiting.delete(data.id); w.busy = 0; pump(); data.error ? job.no(new Error(data.error)) : job.ok(data.B); };
      w.onerror = (e) => console.warn("bodies: a worker failed --", e.message);
      w.busy = 0;
      pool.push(w);
    }
  } catch (e) { console.warn("bodies: no workers, building here --", e.message); pool = []; }
  return pool;
}
// a job for a worker (bodyworker.js): { op: "shape", body, family } | { op: "dress", body, shape } | { op: "body", body }.
// Held here and handed to a worker as one comes free, a DRESS before any shape: a dress is short and puts an animal on
// the screen, a shape is long -- a load asks for every species at once, and a dress queued in a worker behind the
// shapes still to build drew nothing until all of them were done
const queue = [];
function pump() {
  for (const w of pool ?? []) {
    if (w.busy || !queue.length) continue;
    const j = queue.shift();
    w.busy = 1; waiting.set(j.id, j);
    w.postMessage({ id: j.id, ...j.msg });
  }
}
const inWorker = (msg) => new Promise((ok, no) => {
  const P = workers();
  if (!P.length) { try { if (msg.op === "shape") ok(buildShape(msg.body, { family: msg.family })); else { const S = msg.op === "dress" ? msg.shape : buildShape(msg.body); ok(withVeryFar(dressBody(msg.body, S), S)); } } catch (e) { no(e); } return; }
  const j = { id: ++jobs, msg, ok, no };
  if (msg.op === "dress") { const at = queue.findIndex((q) => q.msg.op !== "dress"); queue.splice(at < 0 ? queue.length : at, 0, j); } else queue.push(j);
  pump();
});
// the cache: keyed by the body (its JSON) and the mesher (its source), so a change to either builds afresh
const fnv = (s, h = 2166136261) => { for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619); return (h >>> 0).toString(36); };
let mesherHash = null;
const mesher = () => mesherHash ?? (mesherHash = Promise.all(["./bodymesh.js", "./sculpt.js", "./sharp.js"].map((f) => fetch(new URL(f, import.meta.url)).then((r) => r.text())))
  .then((t) => fnv(t.join("\n"))).catch(() => "x"));
const skip = typeof location !== "undefined" && /[?&]bodycache=0/.test(location.search);
// HALF-DRAWN (bodyhalf.js): a mirror-symmetric body's surface sent to the GPU as its +z half, drawn twice -- once as
// it is, once reflected and skinned by each bone's twin. `?halfdraw=1` on, `=0` off
export const HALFDRAW = typeof location !== "undefined" && /[?&]halfdraw=1/.test(location.search);
let dbP = null;
const db = () => dbP ?? (dbP = new Promise((ok) => {
  if (skip || typeof indexedDB === "undefined") return ok(null);
  const r = indexedDB.open("multiverse-bodies", 1);
  r.onupgradeneeded = () => r.result.createObjectStore("b");
  r.onsuccess = () => ok(r.result); r.onerror = () => ok(null);
}));
const idb = async (mode, f) => {
  const D = await db();
  if (!D) return null;
  return new Promise((ok) => { try { const t = D.transaction("b", mode), q = f(t.objectStore("b")); q.onsuccess = () => ok(q.result ?? null); q.onerror = () => ok(null); } catch { ok(null); } });
};
const replacer = (k, v) => (k === "_frame" ? undefined : v);
// SHAPES SHARED (2026-11-08). A body is built in two passes (bodymesh.js): its SHAPE -- sampled, meshed, simplified --
// keyed on what it depends on alone (bodymesh.js shapeSpec: the field's shapes, eyes, bones, budgets, coat, every length
// measured in grid cells), and its DRESS, laid on that shape. Every look of a definition -- its coats, its variants, its
// young (bodyspec.js familyOf) -- whose shapeSpec is the same shares one shape build: the coats, a variant that only
// rescales the body (the field of a body scaled by f is the field scaled by f, its cell among its lengths, so the mesh is
// the shape's scaled -- exactly, to the float) or changes only its DETAILS (horns, fins, feathers: drawn by the dress).
// The shape's simplification holds the colour boundaries of ALL those looks (each its paint read on the fine surface:
// the bay's black legs and the chestnut's white socks), so it serves each of them as well as its own would have; and
// the key holds those looks' paint too, so it is the same for each look of the family and only for them.
// Kept: the dressed body in IndexedDB by its whole JSON (a reload finds it, as before), the shape there by its key (a
// look not yet dressed is dressed on it), and the shapes of this session in memory (SHAPES_KEPT, the latest).
const SHAPES_KEPT = 48;
// BAKED SHAPES (2026-11-08): every species' shapes built ONCE, by `python3 build/pregen.py --bodies` (pregen.html's
// part "bodies": the world's looks of every definition, species.js allLooks), and shipped as files -- pregen/shapes/,
// one gzipped binary a shape (packShape below: about 140 kB, positions and normals as the builder made them, to the
// bit) and index.json: { code: the mesher's hash (bodymesh.js, sculpt.js, sharp.js), shapes: { shape key: file } }.
// A shape not in IndexedDB is looked for there before it is built: a player's first load builds none of the shapes
// the bake has. An index made by other mesher code is ignored whole (the shapes would not be today's), as is one
// whose key is not there (a species edited since: built here, as before). `?bodycache=0` skips it too.
const BAKED = new URL("./pregen/shapes/", import.meta.url).href;
let bakedIx = null;
const bakedIndex = () => bakedIx ?? (bakedIx = skip || typeof fetch === "undefined" || typeof DecompressionStream === "undefined" ? Promise.resolve(null)
  : Promise.all([fetch(BAKED + "index.json", { cache: "no-store" }).then((r) => (r.ok ? r.json() : null)).catch(() => null), mesher()])
      .then(([ix, mh]) => (ix?.code === mh ? ix.shapes : (ix && console.info("bodies: pregen/shapes/ baked by other mesher code -- run build/pregen.py --bodies; shapes built here"), null))));
async function bakedShape(key) {
  const f = (await bakedIndex())?.[key];
  if (!f) return null;
  try {
    const r = await fetch(BAKED + f);
    if (!r.ok) return null;
    return unpackShape(await new Response(r.body.pipeThrough(new DecompressionStream("gzip"))).arrayBuffer());
  } catch (e) { console.warn(`bodies: baked shape ${f} unreadable --`, e.message); return null; }
}
// a shape as one binary and back: a JSON head (its cell, stats, each LOD's half, the quills' counts), then its arrays,
// each 8-aligned (pregen.js's layout); a LOD's triangles as 16 bits when its vertices allow
const ARRAYS = { Float32Array, Float64Array, Uint32Array, Uint16Array, Int32Array, Uint8Array };
export function packShape(S) {
  const arrays = [], head = { cell: S.cell, stats: S.stats, lods: [], quills: [] }, add = (a) => arrays.push(a) - 1;
  for (const L of S.lods) {
    const tri = L.pos.length / 3 < 65536 ? Uint16Array.from(L.tri) : L.tri;
    head.lods.push({ pos: add(L.pos), nor: add(L.nor), tri: add(tri), half: L.half ? { n: L.half.n, t: L.half.t, twin: add(L.half.twin) } : null });
  }
  for (const q of S.quills) head.quills.push(q ? Object.fromEntries(Object.entries(q).map(([k, v]) => [k, ArrayBuffer.isView(v) ? { a: add(v) } : v])) : null);
  const meta = new TextEncoder().encode(JSON.stringify({ head, types: arrays.map((a) => [a.constructor.name, a.length]) }));
  let size = Math.ceil((8 + meta.length) / 8) * 8;
  const offs = arrays.map((a) => { const o = size; size = Math.ceil((size + a.byteLength) / 8) * 8; return o; });
  const buf = new ArrayBuffer(size);
  new DataView(buf).setUint32(0, meta.length, true);
  new Uint8Array(buf, 8, meta.length).set(meta);
  arrays.forEach((a, i) => new Uint8Array(buf, offs[i], a.byteLength).set(new Uint8Array(a.buffer, a.byteOffset, a.byteLength)));
  return buf;
}
export function unpackShape(buf) {
  const n = new DataView(buf).getUint32(0, true), { head, types } = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 8, n)));
  let o = Math.ceil((8 + n) / 8) * 8;
  const A = types.map(([t, len]) => { const a = new ARRAYS[t](buf, o, len); o = Math.ceil((o + a.byteLength) / 8) * 8; return a; });
  return { cell: head.cell, stats: head.stats,
           lods: head.lods.map((L) => ({ pos: A[L.pos], nor: A[L.nor], tri: A[L.tri] instanceof Uint32Array ? A[L.tri] : Uint32Array.from(A[L.tri]), half: L.half ? { n: L.half.n, t: L.half.t, twin: A[L.half.twin] } : null })),
           quills: head.quills.map((q) => q && Object.fromEntries(Object.entries(q).map(([k, v]) => [k, v && typeof v === "object" && "a" in v ? A[v.a] : v]))) };
}
const shapes = new Map();   // shape key -> Promise<shape>
export const BUILDS = { shapes: 0, shared: 0, shapeCached: 0, shapeBaked: 0, dressed: 0, cached: 0 };   // (what this session built, shared and found: bodies.stats)
const specs = new WeakMap();   // body -> its shapeSpec as text (a family asks for each of its looks')
const specOf = (b) => { let s = specs.get(b); if (s === undefined) { try { s = JSON.stringify(shapeSpec(b)); } catch { s = null; } specs.set(b, s); } return s; };
const shapeKeys = new WeakMap();
function shapeKeyOf(body) {
  let K = shapeKeys.get(body);
  if (K) return K;
  const own = specOf(body), mine = paintSpec(body), looks = new Set();
  if (own && mine) {
    let fam = [];
    try { fam = familyOf(body); } catch (e) { console.warn(`bodies: ${body.name}: its other looks could not be made --`, e.message ?? e); }
    for (const m of fam) if (m !== body && specOf(m) === own) { const p = paintSpec(m); if (p) looks.add(JSON.stringify(p)); }
  }
  const me = JSON.stringify(mine ?? JSON.parse(JSON.stringify(body, replacer)));   // (paints not all last: a shape of its own)
  looks.add(me);
  const all = [...looks].sort();
  K = { key: fnv(own ?? me) + "." + fnv(all.join("\n")) + "." + all.length, family: all.filter((s) => s !== me).map((s) => JSON.parse(s)) };
  shapeKeys.set(body, K);
  return K;
}
// (a body's shape: shared with a look of its family this session, or from IndexedDB, or baked, or built in a worker)
async function shapeJob(body) {
  const mh = await mesher(), { key: sk0, family } = shapeKeyOf(body), sk = "shape:" + sk0 + ":" + mh;
  let job = shapes.get(sk), how = "shared";
  if (!job) {
    how = null;
    job = (async () => {
      const kept = await idb("readonly", (s) => s.get(sk));
      if (kept) { BUILDS.shapeCached++; return { ...kept, from: "the cache" }; }
      const B = await bakedShape(sk0);
      if (B) { BUILDS.shapeBaked++; idb("readwrite", (s) => s.put(B, sk)); return { ...B, from: "baked" }; }
      const S = await inWorker({ op: "shape", body, family });
      BUILDS.shapes++;
      idb("readwrite", (s) => s.put(S, sk));
      return { ...S, from: "built" };
    })();
    shapes.set(sk, job);
    job.catch(() => shapes.delete(sk));
    for (const k of shapes.keys()) { if (shapes.size <= SHAPES_KEPT) break; shapes.delete(k); }
  } else { shapes.delete(sk); shapes.set(sk, job); BUILDS.shared++; }   // (the latest kept)
  return { job, how, key: sk0, family };
}
// THE SHAPE ALONE, for the bake (pregen.html's part "bodies"): { key, shape } -- built as a load would build it
export async function shapeOf(body) { const { job, key } = await shapeJob(body); return { key, shape: await job }; }
export const mesherCode = () => mesher();
async function built(body) {
  const mh = await mesher(), key = body.name + ":" + fnv(JSON.stringify(body, replacer)) + ":" + mh;
  const hit = await idb("readonly", (s) => s.get(key));
  if (hit?.vfar) { BUILDS.cached++; return { ...hit, cached: true }; }   // (one kept before the very far mesh: dressed again -- bodyfar.js)
  const { job, how, family } = await shapeJob(body);
  const S = await job;
  const B = await inWorker({ op: "dress", body, shape: S });
  BUILDS.dressed++;
  B.shape = { how: how ?? S.from, ms: S.stats.ms.shape, looks: family.length + 1, scaled: B.stats.scaled };
  idb("readwrite", (s) => s.put(B, key));
  return B;
}

// ---- the geometries, by body (its identity: coats of a species share a name, not a shape) --------------------------
const kinds = new Map();   // body -> { body, geos: [near, far] | null, nb, stats, ready }
function kindOf(body) {
  let k = kinds.get(body);
  if (k) return k;
  k = { body, geos: null, nb: body.bones.length, stats: null, failed: false };
  kinds.set(body, k);
  const t0 = performance.now();
  built(body).then((B) => {
    const t1 = performance.now();
    k.geos = B.lods.map((L) => {
      const H = HALFDRAW ? halfOf(L, B.nb) : null;
      if (!H || H.err[0] > .5) return geometry(L);   // (a skin its twins cannot give back: drawn whole)
      const g = geometry(H.L), m = new THREE.BufferGeometry();
      // (the reflected draw: the same buffers, its own colour and bones, the half's triangles only)
      for (const [name, a] of Object.entries(g.attributes)) if (name !== "color" && name !== "skinIndex") m.setAttribute(name, a);
      // (as long as the near draw's -- three's CPU skinning (a box, a ray) reads every vertex the position has)
      const nv = g.attributes.position.count, col = new Float32Array(nv * 3), si = new Uint16Array(nv * 4);
      col.set(H.col); col.set(H.L.col.subarray(H.col.length), H.col.length); si.set(H.skinIndex); si.set(H.L.skinIndex.subarray(H.skinIndex.length), H.skinIndex.length);
      m.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
      m.setAttribute("skinIndex", new THREE.Uint16BufferAttribute(si, 4));
      m.setIndex(g.index); m.setDrawRange(0, 3 * H.t);
      m.boundingSphere = g.boundingSphere;
      g.userData.mirror = m;
      return g;
    });
    k.geos.forEach((g, lod) => { g.userData.lod = lod; });   // (its level: the draw census reads it)
    k.R = (k.geos[1] ?? k.geos[0]).boundingSphere.radius;   // (its size at rest, for BODY_LOD's pixels)
    k.handMs = performance.now() - t1;
    k.nb = B.nb; k.stats = B.stats;
    // (the log: how its shape came -- built, shared with a look of its family built this session, or from the cache --
    //  and its dress; `shape built` lines count the meshings a load did)
    const sh = B.shape, how = B.cached ? "from the cache" : !sh ? `built in ${B.stats.ms.all} ms`
      : `shape ${sh.how === "built" ? `built in ${sh.ms} ms` : sh.how === "shared" ? "shared" : sh.how === "baked" ? "baked" : "from the cache"}${sh.looks > 1 ? ` (${sh.looks} looks)` : ""}${sh.scaled !== 1 ? ` scaled ${(+sh.scaled).toFixed(3)}` : ""}, dressed in ${B.stats.ms.dress} ms`;
    console.info(`bodies: ${body.name} -- ${B.stats.tris.join(" / ")} triangles${B.stats.quills?.[0] ? `, ${B.stats.quills.join(" / ")} quills` : ""}, ${how} (${Math.round(performance.now() - t0)} ms to hand${k.geos[0].userData.mirror ? `, half-drawn: ${k.handMs.toFixed(1)} ms to halve` : ""}${k.geos[0].userData.shared ? ", its geometry shared" : ""})`);
  }).catch((e) => { k.failed = true; console.warn(`bodies: ${body.name} could not be built --`, e.message ?? e); });
  return k;
}
// A SCULPTED BODY'S BOX at rest, in its species' frame -- [min, max], or null until its mesh is built (the asset viewer
// frames by it: the surface reaches well past the bones, a bear's rump past its hips)
export function restBox(body) {
  const g = kinds.get(body)?.geos?.[0];
  if (!g) return null;
  if (!g.boundingBox) g.computeBoundingBox();
  const lo = g.boundingBox.min.toArray(), hi = g.boundingBox.max.toArray();
  if (g.userData.mirror) [lo[2], hi[2]] = [Math.min(lo[2], -hi[2]), Math.max(hi[2], -lo[2])];   // (a half: and its reflection)
  return [lo, hi];
}
// (TWO interleaved buffers for the floats a vertex carries -- WebGPU allows eight vertex buffers, and a skinned,
//  patterned, haired vertex has thirteen attributes: its GEOMETRY (where it is, its normal, its skin; the quills' uv)
//  and its PAINT. The geometry is SHARED: the coats of a species are one shape with one set of details, so the same
//  arrays to the bit -- one buffer on the GPU (and its index and skin indices), each coat's paint a buffer of its own)
const GEO = [["position", "pos", 3], ["normal", "nor", 3], ["skinWeight", "skinWeight", 4], ["uv", "uv", 2]];
const PAINT = [["color", "col", 3], ["hairMask", "hair", 1], ["wetMask", "wet", 1],
               ["patId", "patId", 3], ["patKT", "patKT", 3], ["patP", "patP", 4], ["patQ", "patQ", 4], ["patR", "patR", 4]];
function interleaved(L, layout, nv) {
  const stride = layout.reduce((s, l) => s + l[2], 0), data = new Float32Array(nv * stride);
  let off = 0;
  for (const [, key, n] of layout) {
    const src = L[key];
    if (src) for (let v = 0; v < nv; v++) for (let k = 0; k < n; k++) data[v * stride + off + k] = src[v * n + k];
    off += n;
  }
  return new THREE.InterleavedBuffer(data, stride);
}
const attach = (g, ib, layout) => { let off = 0; for (const [name, , n] of layout) { g.setAttribute(name, new THREE.InterleavedBufferAttribute(ib, n, off)); off += n; } };
// (the geometry's identity: its arrays' bits, hashed twice over)
const bitsKey = (arrs) => {
  let h = 2166136261, g = 0x9747b28c;
  for (const a of arrs) {
    if (!a) { h = Math.imul(h ^ 7, 16777619); continue; }
    const u = a.byteLength % 4 ? new Uint8Array(a.buffer, a.byteOffset, a.byteLength) : new Uint32Array(a.buffer, a.byteOffset, a.byteLength >> 2);
    for (let i = 0; i < u.length; i++) { const x = u[i]; h = Math.imul(h ^ x, 16777619); g = Math.imul(g ^ (x + i), 0x5bd1e995); g ^= g >>> 15; }
    h = Math.imul(h ^ a.length, 16777619);
  }
  return (h >>> 0).toString(36) + (g >>> 0).toString(36) + ":" + arrs.map((a) => a?.length ?? 0).join(",");
};
const geoms = new Map();   // bits -> { ib, skin, index }
function geometry(L) {
  const g = new THREE.BufferGeometry(), nv = L.pos.length / 3, key = bitsKey([L.pos, L.nor, L.skinWeight, L.uv, L.skinIndex, L.index]);
  let G = geoms.get(key);
  if (G) G.n++;
  else geoms.set(key, G = { ib: interleaved(L, GEO, nv), skin: new THREE.Uint16BufferAttribute(L.skinIndex, 4), index: new THREE.BufferAttribute(L.index, 1), n: 1 });
  attach(g, G.ib, GEO);
  attach(g, interleaved(L, PAINT, nv), PAINT);
  g.setAttribute("skinIndex", G.skin);
  g.setIndex(G.index);
  g.computeBoundingSphere();
  g.userData.shared = G.n > 1;
  return g;
}

const FLIP = vec4(1, 1, -1, 1);
// the paint: the vertex colour, a pattern over it where the shape has one -- three slots (bodymesh.js patternsMesh),
// their ids FLAT across a triangle, kt = (how patterned, slot 1's share, slot 2's share; slot 0 has the rest), each
// slot's footprint in the pixel and the slant of the surface to its frame's axis as the composite measures them
// (shell.js)
const patBase = wgslFn(`
  fn patBase(col: vec3<f32>, id: vec3<f32>, kt: vec3<f32>, pl: vec4<f32>, ql: vec4<f32>, rl: vec4<f32>, pw: vec3<f32>) -> vec3<f32> {
    let patPx = max(max(length(dpdx(pw)), length(dpdy(pw))), 1e-5);
    let nL = cross(dpdx(pl.xyz), dpdy(pl.xyz));
    let patAx = abs(nL.x) / max(length(nL), 1e-9);
    let nQ = cross(dpdx(ql.xyz), dpdy(ql.xyz));
    let qAx = abs(nQ.x) / max(length(nQ), 1e-9);
    let nR = cross(dpdx(rl.xyz), dpdy(rl.xyz));
    let rAx = abs(nR.x) / max(length(nR), 1e-9);
    // (the footprint in the pattern's own units: a coat laid at its body's scale, a feather's metres)
    let pxL = max(max(length(dpdx(pl.xyz)), length(dpdy(pl.xyz))), 1e-6);
    let pxQ = max(max(length(dpdx(ql.xyz)), length(dpdy(ql.xyz))), 1e-6);
    let pxR = max(max(length(dpdx(rl.xyz)), length(dpdy(rl.xyz))), 1e-6);
    if (id.x < 0.5 || kt.x < 0.002) { return col; }
    let c0 = coatAt(col, floor(id.x + 0.5), pl, ql, patPx, patAx, pxL);
    var c = c0;
    if (kt.y > 0.002 && id.y > 0.5) { c += (coatAt(col, floor(id.y + 0.5), ql, vec4<f32>(0.0), patPx, qAx, pxQ) - c0) * clamp(kt.y, 0.0, 1.0); }
    if (kt.z > 0.002 && id.z > 0.5) { c += (coatAt(col, floor(id.z + 0.5), rl, vec4<f32>(0.0), patPx, rAx, pxR) - c0) * clamp(kt.z, 0.0, 1.0); }
    return mix(col, c, clamp(kt.x, 0.0, 1.0));
  }
`, [coatAt]);

// THE LEVELS A BODY IS DRAWN AT (2026-11-22). A seed-7 medieval town draws some 200 creatures, nearly all of them 100 to
// 450 m off (the birds in the trees, the zoo, the pastures): half of them under 8 pixels across, every one a skinned draw
// of 3 to 11 thousand triangles, posed and skinned as a close one is. Now, for each body of each figure:
//   0 near       nearer than its `mesh.far` (bodyspec.js: 4 m, or 14 x its size) -- exactly as before: a close-up,
//                riding, petting, the asset viewer;
//   1 far        the far mesh, as before;
//   2 very far   under `vfar` pixels across (its rest pose's bounding sphere, at the camera's field of view and the
//                window's height): the third mesh (bodyfar.js, 400-1600 triangles, no coat);
//   3 hidden     under `hide` pixels, a figure that is that one body alone and standing still (a moving speck would
//                blink): not drawn and not posed (the composite skips it: composite.js `_tiny`). Coming back it is
//                posed afresh and drawn from the frame after, never on a stale pose.
// Each switch has its hysteresis -- back from far to near only inside `near` x mesh.far, back up a level only past
// `band` x its threshold -- so a creature at the edge does not flicker between two meshes. A body's bones are
// written only when the composite posed it again (skeleton.js `_bmN`): a distant figure is posed every 2nd or 4th frame.
// From level `batch` on (1: the far and the very far meshes) the bodies of one look on one mesh are ONE draw (below,
// "ONE DRAW A LOOK"); `batch: 9` draws each its own SkinnedMesh, as before.
export const BODY_LOD = { vfar: 12, hide: 2.5, band: 1.2, near: .92, on: true, batch: 1 };
const _defH = 800, _defFov = 45;
// FEWER DRAWS PAST THE NEAR MESH (2026-11-22). Seen from outside the pastures a seed-7 town drew ~200 far and very far
// bodies, each its own SkinnedMesh: a render object, a bind group and a bone upload apiece -- three's ~20 us of CPU a
// draw, whatever its size -- and they were nearly all DIFFERENT looks (the zoo keeps one of each of ~130 species), so
// instancing a look alone would have saved a third of them. Now:
//   - the VERY FAR bodies (level 2) of every look are ONE object, a BatchedMesh (batchpool.js): each look's very far
//     mesh added once (its geometry, colour, hair and wet masks as vertex attributes -- eight vertex buffers, WebGPU's
//     limit -- its pattern slots in a storage buffer of their own, PAT, read by the vertex's index), a copy a body;
//     three walks one object and sends a cheap draw a copy;
//   - the FAR bodies (level 1) of one look are one instanced draw (a plain Mesh drawing `count` copies of the look's
//     far geometry): a herd of sheep in a field is one draw. (Not in the BatchedMesh: the far meshes are 5-10x the
//     very far ones, a copy of every look's would be hundreds of MB.)
// Both skin in the vertex shader from ONE storage buffer of bones shared by all (BONES: a mat4 a bone, each body record
// its own run of nb, written exactly as its skeleton's were: W S(f) RestInv); a copy's run starts at its aBone (the
// instanced draw: an instanced attribute) or at its batch matrix's last element (the BatchedMesh: the matrix is
// otherwise the identity, and that element only ever reaches w -- so per-copy culling and sorting, which would read
// it, are off). The same paint, the same faceMaterial and hair sway, the same bones: a body draws the same pixels
// batched or not. A body record keeps its run for life (records are parked and reused, never dropped), so its bones
// stay put and only the runs written this frame go up (merged where they nearly touch: BATCH.gap). Near bodies and the
// half-drawn ones (bodyhalf.js: their reflection needs its own skeleton) stay SkinnedMeshes. `BODY_LOD.batch: 9`
// draws every body as its own SkinnedMesh, as before (for the A/B: the same frame both ways).
export const BATCH = { bones: 16384, copies: 32, gap: 64, verts: 1 << 17 };   // (room to start: matrices; copies a look; matrices between runs merged into one upload; very far vertices)
// the skinning: positionLocal and normalLocal through the weighted bones of the copy's run (from b), as three's own
// skinning does with a skeleton (bind matrix the identity); called as a material sets up its position
const skinAll = (bones) => Fn(([b]) => {
  const si = attribute("skinIndex", "uvec4"), sw = attribute("skinWeight", "vec4");
  const M = add(bones.element(b.add(si.x)).mul(sw.x), bones.element(b.add(si.y)).mul(sw.y), bones.element(b.add(si.z)).mul(sw.z), bones.element(b.add(si.w)).mul(sw.w));
  positionLocal.assign(M.mul(vec4(positionLocal, 1)).xyz);
  normalLocal.assign(normalize(M.mul(vec4(normalLocal, 0)).xyz));
}, "void");   // (void: three puts the call on the stack it is made in, as its own skinning)
// a copy's run: the instanced draw's aBone, or the BatchedMesh copy's matrix, element 15 (found as three's batch() finds
// the matrix: the draw's id through the indirection texture)
function boneBase(o, builder) {
  if (!o.isBatchedMesh) return uint(attribute("aBone", "float"));
  const id = int(builder.getDrawIndex() === null ? instanceIndex : drawIndex);
  const ni = int(textureSize(textureLoad(o._indirectTexture), 0).x);
  const k = int(textureLoad(o._indirectTexture, ivec2(id.mod(ni), id.div(ni))).x).mul(4);
  const nm = int(textureSize(textureLoad(o._matricesTexture), 0).x);
  return uint(textureLoad(o._matricesTexture, ivec2(k.mod(nm).add(3), k.div(nm))).w);
}
// bone j of a body into out at o (16 floats a bone): W_j S(f) RestInv_j -- all column-major 4x4s (W: the figure's frames
// from its first bone on, B = 16 x that bone)
function writeBones(out, o0, W, B, restInv, nb, f) {
  for (let j = 0; j < nb; j++) {
    const o = o0 + 16 * j, w0 = B + 16 * j, Ri = restInv[j];
    for (let c = 0; c < 4; c++) {
      const x = Ri[4 * c], y = Ri[4 * c + 1], z = Ri[4 * c + 2], w = Ri[4 * c + 3];
      for (let r = 0; r < 3; r++) out[o + 4 * c + r] = f * (W[w0 + r] * x + W[w0 + 4 + r] * y + W[w0 + 8 + r] * z) + W[w0 + 12 + r] * w;
      out[o + 4 * c + 3] = w;
    }
  }
}
export const builtBody = (body) => built(body);   // (for the headless checks: a body built or found as kindOf builds it)
export function createBodies(scene, { shade = {} } = {}) {
  // (the reflected half's pattern coordinates: the near side's with the across axis turned over -- bodyhalf.js)
  const paint = (flip) => patBase({ col: attribute("color", "vec3"), id: varying(attribute("patId", "vec3")).setInterpolation("flat"), kt: attribute("patKT", "vec3"),
                                    pl: flip ? attribute("patP", "vec4").mul(FLIP) : attribute("patP", "vec4"), ql: flip ? attribute("patQ", "vec4").mul(FLIP) : attribute("patQ", "vec4"),
                                    rl: flip ? attribute("patR", "vec4").mul(FLIP) : attribute("patR", "vec4"), pw: positionWorld });
  // (a coat of quills is broad flat spines, not fine hair: the manes' softer sheen)
  const material = (base) => faceMaterial({ ...SHADE, ...shade, base, hair: { s1: .05, s2: .09, ...(shade.hair ?? {}) } });
  const mat = material(paint(false));
  let matM = null;   // (the reflected halves': made with the first)
  const live = new Map();   // animal -> [ { mesh, skel, kind, seen } ] -- one record a body inside it (one, mostly)
  const free = new Map();   // kind -> [ spare records ]
  let frame = 0;
  const I = new THREE.Matrix4();
  // (the batched draws: BONES the shared bone runs; PAT the very far meshes' pattern slots; their materials)
  let bonesCap = 0, bonesUsed = 0, bonesAttr = null, patCap = 0, patAttr = null, matB = null, matV = null, vpool = null;
  const batches = new Map();   // far geometry -> { mesh, slot (aBone), cap, n } -- a look's instanced draw
  const vshapes = new Map();   // very far geometry -> its shape in the BatchedMesh
  const runs = [];   // [start, count] of the bone runs written this frame (matrices)
  // (the paint of a very far copy: as paint() below, its pattern slots from PAT by the vertex's index)
  const paintV = (P) => {
    const at = (k) => P.element(vertexIndex.mul(5).add(k)), a = at(0), c = at(1);
    return patBase({ col: attribute("color", "vec3"), id: varying(a.xyz).setInterpolation("flat"), kt: varying(vec3(a.w, c.x, c.y)),
                     pl: varying(at(2)), ql: varying(at(3)), rl: varying(at(4)), pw: positionWorld });
  };
  // (the two materials, made again when a buffer grows: a bigger buffer is a new node; the old ones dropped later)
  const materials = () => {
    const old = [matB, matV], skin = skinAll(storage(bonesAttr, "mat4", bonesCap).toReadOnly());
    const skinned = (m) => { const base = m.setupPosition; m.setupPosition = function (builder) { skin(boneBase(builder.object, builder)); return base.call(this, builder); }; return m; };
    matB = skinned(material(paint(false)));
    matV = patAttr ? skinned(material(paintV(storage(patAttr, "vec4", patAttr.count).toReadOnly()))) : null;
    for (const b of batches.values()) b.mesh.material = matB;
    if (vpool) vpool.mesh.material = matV;
    setTimeout(() => { for (const m of old) if (m) { m.userData.ramp.dispose(); m.dispose(); } }, 3000);
  };
  // (a storage buffer with room for `need` items of `item` floats, or null if A has it; read as items of `size` floats)
  const grow = (A, need, cap, start, item, size = item) => {
    if (need <= cap) return null;
    let c = Math.max(cap, start);
    while (need > c) c *= 2;
    const a = new THREE.StorageBufferAttribute(new Float32Array(c * item), size);
    if (A) a.array.set(A.array);
    return a;
  };
  const bonesRoom = (n) => {
    const a = grow(bonesAttr, bonesUsed + n, bonesCap, BATCH.bones, 16);
    if (!a) return;
    bonesAttr = a; bonesCap = a.count; materials();
    runs.length = 0; runs.push([0, bonesUsed]);   // (the new buffer: its runs so far sent with it)
  };
  // a look's very far mesh in the BatchedMesh, on its first use: its geometry (eight attributes) and its pattern slots
  const vshape = (geo) => {
    let sh = vshapes.get(geo);
    if (sh) return sh;
    const nv = geo.attributes.position.count;
    if (!patAttr) { patAttr = grow(null, 1, 0, BATCH.verts, 20, 4); patCap = patAttr.count / 5; materials(); }
    // (the material its current one, also for a bigger mesh made later: batchpool.js makes it with the first)
    vpool ??= batchPool(scene, matV, { name: "bodies very far", copies: 256, verts: BATCH.verts, indices: 3 * BATCH.verts,
                                       setup: (m) => { m.perObjectFrustumCulled = false; m.sortObjects = false; if (matV) m.material = matV; } });
    const g = new THREE.BufferGeometry();
    for (const k of ["position", "normal", "skinWeight", "uv", "skinIndex", "color", "hairMask", "wetMask"]) g.setAttribute(k, geo.attributes[k]);
    g.setIndex(geo.index);
    g.boundingSphere = geo.boundingSphere;
    sh = vpool.add(g);
    // (its slots at the vertices the BatchedMesh gave it: patId, patKT, patP, patQ, patR as five vec4s a vertex)
    const v0 = vpool.mesh.getGeometryRangeAt(sh.id).vertexStart, more = grow(patAttr, v0 + nv, patCap, BATCH.verts, 20, 4);
    if (more) { patAttr = more; patCap = more.count / 5; materials(); }
    const A = patAttr.array, G = geo.attributes;
    for (let v = 0; v < nv; v++) {
      const o = 20 * (v0 + v);
      A[o] = G.patId.getX(v); A[o + 1] = G.patId.getY(v); A[o + 2] = G.patId.getZ(v); A[o + 3] = G.patKT.getX(v);
      A[o + 4] = G.patKT.getY(v); A[o + 5] = G.patKT.getZ(v);
      for (const [k, at] of [["patP", 8], ["patQ", 12], ["patR", 16]]) { A[o + at] = G[k].getX(v); A[o + at + 1] = G[k].getY(v); A[o + at + 2] = G[k].getZ(v); A[o + at + 3] = G[k].getW(v); }
    }
    patAttr.addUpdateRange(20 * v0, 20 * nv); patAttr.needsUpdate = true;   // (three clears the ranges once sent)
    vshapes.set(geo, sh);
    return sh;
  };
  const _vm = new THREE.Matrix4();
  const makeBatch = (geo, cap) => {
    const g = new THREE.BufferGeometry();
    for (const [name, a] of Object.entries(geo.attributes)) g.setAttribute(name, a);
    g.setIndex(geo.index);
    const slot = new THREE.InstancedBufferAttribute(new Float32Array(cap), 1);
    g.setAttribute("aBone", slot);
    g.boundingSphere = geo.boundingSphere;
    const mesh = new THREE.Mesh(g, matB);
    mesh.name = "bodies far"; mesh.count = 0; mesh.visible = false;
    mesh.frustumCulled = false; mesh.matrixAutoUpdate = false; mesh.userData.noMerge = true;
    scene.add(mesh);
    return { mesh, slot, cap, n: 0, geo };
  };
  // a body record's copy this frame: in the BatchedMesh (very far) or in its look's instanced draw (a bigger one made
  // when that is full: a new geometry, the old one dropped from the scene -- its buffers are the look's own, still drawn)
  const batchPut = (geo, rec, lv) => {
    if (lv === 2) { const sh = vshape(geo); _vm.identity(); _vm.elements[15] = rec.bone; vpool.put(sh, _vm); return; }   // (vshape makes the pool)
    let b = batches.get(geo);
    if (!b) { batches.set(geo, b = makeBatch(geo, BATCH.copies)); b.mesh.userData.look = rec.kind.body.name; }
    if (b.n === b.cap) {
      const nb = makeBatch(geo, b.cap * 2);
      nb.slot.array.set(b.slot.array); nb.n = b.n; nb.dirty = true; nb.mesh.userData.look = b.mesh.userData.look;
      scene.remove(b.mesh); b.mesh.visible = false;
      batches.set(geo, b = nb);
    }
    const v = rec.bone;
    if (b.slot.array[b.n] !== v) { b.slot.array[b.n] = v; b.dirty = true; }
    b.n++;
  };
  const make = (kind) => {
    const bones = Array.from({ length: kind.nb }, () => new THREE.Bone());
    const skel = new THREE.Skeleton(bones);
    skel.update = () => {};   // (its matrices are written by place(), from the composite's frames)
    const mesh = new THREE.SkinnedMesh(kind.geos[0], mat);
    mesh.bind(skel, I);
    mesh.frustumCulled = false;
    mesh.matrixAutoUpdate = false;
    scene.add(mesh);
    // (a half-drawn body: its reflection, the same skeleton -- bound and placed by M = diag(1, 1, -1), so it skins
    //  M v by the twins its own skinIndex names, and three flips its front face for the negative determinant)
    let mirror = null;
    if (kind.geos.some((g) => g.userData.mirror)) {
      mirror = new THREE.SkinnedMesh(kind.geos.find((g) => g.userData.mirror).userData.mirror, matM ??= material(paint(true)));
      mirror.matrix.makeScale(1, 1, -1); mirror.matrixWorld.copy(mirror.matrix);
      mirror.bind(skel, mirror.matrix);
      mirror.frustumCulled = false;
      mirror.matrixAutoUpdate = false;
      scene.add(mirror);
    }
    return { mesh, mirror, skel, kind, seen: frame };
  };
  const show = (rec, on) => { rec.mesh.visible = on; if (rec.mirror) rec.mirror.visible = on && !!rec.mesh.geometry.userData.mirror; };
  const park = (rec) => { if (!free.has(rec.kind)) free.set(rec.kind, []); free.get(rec.kind).push(rec); };   // (a mesh no figure uses now: kept for the next of its kind)
  const stats = { drawn: 0, tris: 0, waiting: 0, levels: [0, 0, 0, 0], bones: 0, batched: 0, draws: 0 };
  return {
    // eye: where the camera is (or null: every body near); cam: the camera (its field of view sizes the pixels)
    place(herds, eye = null, cam = null) {
      frame++;
      stats.drawn = stats.tris = stats.waiting = stats.bones = stats.batched = 0; stats.levels.fill(0);
      for (const b of batches.values()) b.n = 0;
      vpool?.begin();
      const E = eye ? (Array.isArray(eye) ? eye : [eye.x, eye.y, eye.z]) : null;
      // (pixels a radian at the screen's middle: the window's height over the vertical field of view)
      const pxRad = (typeof innerHeight === "number" && innerHeight > 0 ? innerHeight : _defH) / ((cam?.fov ?? _defFov) * Math.PI / 180);
      const LV = BODY_LOD;
      for (const herd of herds) for (const an of herd?.animals ?? []) {
        // (one body, the whole figure -- or several inside a bigger figure, each with the index of its first bone among
        //  the figure's parts: a mount under its rider, a pair under a yoke -- bodyspec.js sculptPart)
        const list = an.sculpts ?? (an.sculpted ? (an._one ??= [{ body: an.sculpted, base: 0 }]) : null);
        if (!list || !an._bm) continue;
        let recs = live.get(an);
        if (an.hidden || an._off || an._out) { if (recs) for (const rec of recs) if (rec) { show(rec, false); rec.seen = frame; } if (an._tiny) an._tiny = false; continue; }
        if (!recs) live.set(an, recs = []);
        for (let s = 0; s < list.length; s++) {
          const { body, base } = list[s];
          const kind = kindOf(body);
          if (!kind.geos) { stats.waiting++; continue; }
          let rec = recs[s];
          if (!rec || rec.kind !== kind) {
            if (rec) { show(rec, false); park(rec); }
            rec = recs[s] = free.get(kind)?.pop() ?? make(kind);
          }
          rec.seen = frame;
          const r0 = body.root0, f = r0 > 1e-6 && an.parts?.[base]?.pos ? an.parts[base].pos[1] / r0 : 1;
          // its level (BODY_LOD): near by distance, as it always was; past that by its size on the screen
          let lv = 0;
          if (E) {
            const d = Math.hypot(an.position.x - E[0], an.position.y - E[1], an.position.z - E[2]), f0 = body.mesh.far ?? 4;
            if (d > f0 || (rec.lv > 0 && d > f0 * LV.near)) {
              lv = 1;
              if (LV.on) {
                const px = 2 * kind.R * f / Math.max(d, 1e-3) * pxRad, up = (l) => (rec.lv >= l ? LV.band : 1);
                if (list.length === 1 && an.sculpted && !an.moving && px < LV.hide * up(3)) lv = 3;   // (a figure that is this body alone)
                else if (kind.geos.length > 2 && px < LV.vfar * up(2)) lv = 2;
              }
            }
          }
          if (LV.force != null) lv = Math.min(LV.force, kind.geos.length - 1);   // (a check's override: every body on that mesh)
          const wake = rec.lv === 3 && lv !== 3;
          rec.lv = lv; stats.levels[lv]++;
          if (lv === 3) { show(rec, false); an._tiny = true; continue; }
          if (wake || an._tiny) { an._tiny = false; an._posed = false; show(rec, false); continue; }   // (posed afresh this coming frame, drawn then)
          const geo = kind.geos[Math.min(lv, kind.geos.length - 1)];
          stats.drawn++; stats.tris += geo.index.count / 3 + (geo.userData.mirror ? geo.userData.mirror.drawRange.count / 3 : 0);
          // (batched: its copy in the look's draw, its bones in its run of BONES -- or its own skinned mesh)
          const into = lv >= BODY_LOD.batch && !geo.userData.mirror ? 1 : 0;
          if (into) {
            if (rec.bone === undefined) { bonesRoom(kind.nb); rec.bone = bonesUsed; bonesUsed += kind.nb; }
            show(rec, false);
            batchPut(geo, rec, Math.min(lv, kind.geos.length - 1));
            stats.batched++;
          } else {
            if (rec.mesh.geometry !== geo) { rec.mesh.geometry = geo; if (geo.userData.mirror) rec.mirror.geometry = geo.userData.mirror; }
            show(rec, true);
          }
          // (its bones as they were, unless the composite posed it since: skeleton.js counts the poses)
          if (rec.an === an && rec.bmN === an._bmN && rec.f === f && rec.base === base && rec.into === into) continue;
          rec.an = an; rec.bmN = an._bmN; rec.f = f; rec.base = base; rec.into = into; stats.bones++;
          if (into) { writeBones(bonesAttr.array, 16 * rec.bone, an._bm, base * 16, body.restInv, kind.nb, f); runs.push([rec.bone, kind.nb]); }
          else writeBones(rec.skel.boneMatrices, 0, an._bm, base * 16, body.restInv, kind.nb, f);
        }
      }
      // (an animal gone from its herd: its meshes hidden and kept for the next of its kind)
      for (const [an, recs] of live) if (!recs.some((rec) => rec && rec.seen === frame)) {
        for (const rec of recs) if (rec) { show(rec, false); park(rec); }
        live.delete(an);
      }
      // the batches: as many copies as bodies put in them, their runs' starts sent when they changed
      stats.draws = 0;
      if (vpool) { vpool.end(); if (vpool.mesh.visible) stats.draws++; }
      for (const b of batches.values()) {
        b.mesh.count = b.n; b.mesh.visible = b.n > 0; if (b.n) stats.draws++;
        if (b.dirty && b.n) { b.slot.clearUpdateRanges(); b.slot.addUpdateRange(0, b.n); b.slot.needsUpdate = true; }
        b.dirty = false;
      }
      // the bone runs written this frame, those that nearly touch as one upload
      if (runs.length && bonesAttr) {
        runs.sort((a, b) => a[0] - b[0]);
        bonesAttr.clearUpdateRanges();
        let [s0, e0] = [runs[0][0], runs[0][0] + runs[0][1]];
        for (let i = 1; i <= runs.length; i++) {
          const r = runs[i];
          if (r && r[0] <= e0 + BATCH.gap) { e0 = Math.max(e0, r[0] + r[1]); continue; }
          bonesAttr.addUpdateRange(16 * s0, 16 * (e0 - s0));
          if (r) { s0 = r[0]; e0 = r[0] + r[1]; }
        }
        bonesAttr.needsUpdate = true;
        runs.length = 0;
      }
    },
    stats() { return { ...stats, levels: [...stats.levels], kinds: [...kinds.values()].filter((k) => k.stats).map((k) => ({ name: k.body.name, ...k.stats })), builds: { ...BUILDS, geometries: geoms.size } }; },
    ready() { return [...kinds.values()].every((k) => k.geos || k.failed); },
    dispose() {
      for (const rec of [...[...live.values()].flat().filter(Boolean), ...[...free.values()].flat()]) { scene.remove(rec.mesh); if (rec.mirror) scene.remove(rec.mirror); rec.skel.dispose?.(); }
      live.clear(); free.clear();
      for (const b of batches.values()) scene.remove(b.mesh);
      batches.clear(); vpool?.dispose();
      for (const m of [mat, matM, matB, matV]) if (m) { m.userData.ramp.dispose(); m.dispose(); }
    },
  };
}
