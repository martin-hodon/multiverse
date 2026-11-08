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
// are. Past `mesh.far` metres from the eye the coarse mesh (and its sparser coat) stands in.
// Shaded as the heads and the manes are (heads.js faceMaterial: half-Lambert ramp; fibres and a softer sheen on
// hairMask; the nose and the eyes wet) -- its paint the vertex colour with the composite's own PATTERNS laid over it
// (banner_wgsl patternAt: stripes, spots, scales... by the frame of the shape each vertex is nearest: bodymesh.js).
import * as THREE from "three";
import { wgslFn, attribute, varying, positionWorld, vec4 } from "three/tsl";
import { faceMaterial, SHADE } from "./heads.js";
import { buildBody, buildShape, dressBody, shapeSpec, paintSpec } from "./bodymesh.js";
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
  if (!P.length) { try { ok(msg.op === "shape" ? buildShape(msg.body, { family: msg.family }) : msg.op === "dress" ? dressBody(msg.body, msg.shape) : buildBody(msg.body)); } catch (e) { no(e); } return; }
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
  if (hit) { BUILDS.cached++; return { ...hit, cached: true }; }
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
  const stats = { drawn: 0, tris: 0, waiting: 0 };
  return {
    place(herds, eye = null) {
      frame++;
      stats.drawn = stats.tris = stats.waiting = 0;
      const E = eye ? (Array.isArray(eye) ? eye : [eye.x, eye.y, eye.z]) : null;
      for (const herd of herds) for (const an of herd?.animals ?? []) {
        // (one body, the whole figure -- or several inside a bigger figure, each with the index of its first bone among
        //  the figure's parts: a mount under its rider, a pair under a yoke -- bodyspec.js sculptPart)
        const list = an.sculpts ?? (an.sculpted ? (an._one ??= [{ body: an.sculpted, base: 0 }]) : null);
        if (!list || !an._bm) continue;
        let recs = live.get(an);
        if (an.hidden || an._off || an._out) { if (recs) for (const rec of recs) if (rec) { show(rec, false); rec.seen = frame; } continue; }
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
          const far = E && Math.hypot(an.position.x - E[0], an.position.y - E[1], an.position.z - E[2]) > (body.mesh.far ?? 4) ? 1 : 0;
          const geo = kind.geos[Math.min(far, kind.geos.length - 1)];
          if (rec.mesh.geometry !== geo) { rec.mesh.geometry = geo; if (geo.userData.mirror) rec.mirror.geometry = geo.userData.mirror; }
          show(rec, true);
          // bone j: W_j S(f) RestInv_j -- all column-major 4x4s (W: the figure's frames from its first bone on)
          const W = an._bm, out = rec.skel.boneMatrices, nb = kind.nb, B = base * 16;
          const r0 = body.root0, f = r0 > 1e-6 && an.parts?.[base]?.pos ? an.parts[base].pos[1] / r0 : 1;
          for (let j = 0; j < nb; j++) {
            const o = 16 * j, w0 = B + o, Ri = body.restInv[j];
            for (let c = 0; c < 4; c++) {
              const x = Ri[4 * c], y = Ri[4 * c + 1], z = Ri[4 * c + 2], w = Ri[4 * c + 3];
              for (let r = 0; r < 3; r++) out[o + 4 * c + r] = f * (W[w0 + r] * x + W[w0 + 4 + r] * y + W[w0 + 8 + r] * z) + W[w0 + 12 + r] * w;
              out[o + 4 * c + 3] = w;
            }
          }
          stats.drawn++; stats.tris += geo.index.count / 3 + (geo.userData.mirror ? geo.userData.mirror.drawRange.count / 3 : 0);
        }
      }
      // (an animal gone from its herd: its meshes hidden and kept for the next of its kind)
      for (const [an, recs] of live) if (!recs.some((rec) => rec && rec.seen === frame)) {
        for (const rec of recs) if (rec) { show(rec, false); park(rec); }
        live.delete(an);
      }
    },
    stats() { return { ...stats, kinds: [...kinds.values()].filter((k) => k.stats).map((k) => ({ name: k.body.name, ...k.stats })), builds: { ...BUILDS, geometries: geoms.size } }; },
    ready() { return [...kinds.values()].every((k) => k.geos || k.failed); },
    dispose() {
      for (const rec of [...[...live.values()].flat().filter(Boolean), ...[...free.values()].flat()]) { scene.remove(rec.mesh); if (rec.mirror) scene.remove(rec.mirror); rec.skel.dispose?.(); }
      live.clear(); free.clear();
      for (const m of [mat, matM]) if (m) { m.userData.ramp.dispose(); m.dispose(); }
    },
  };
}
