// A SCULPTED BODY'S THIRD, VERY FAR MESH (2026-11-22): what bodies.js draws once a creature is about a dozen pixels across
// (BODY_LOD there). Made from the dressed FAR mesh where the dress is made (bodyworker.js), so it costs the shape build
// nothing and the baked shapes (pregen/shapes/, keyed on bodymesh.js, sculpt.js and sharp.js) stay as they are:
//   - the body's own surface (the far mesh's first `nv` vertices and `nt` triangles: bodymesh.js assemble lays it first,
//     a closed welded surface) simplified again by the same quadric collapses (sculpt.js simplify) to VFAR.share of its
//     triangles, between VFAR.min and VFAR.max, its colour boundaries held (paintAnchors) -- each vertex left keeps the
//     paint, skin and pattern of the one it was, the normals made again from the coarser surface;
//   - the eyes and the details (horns, ears, fins, feathers, a mane's and a tail's strands: most of a far mesh -- a
//     horse's is 2200 triangles of body and 8600 of tubes) CLUSTERED on a grid of `cells` across the body's box: the
//     vertices in a cell made one (where they average, with the first one's paint and skin), the triangles that no
//     longer span three cells dropped -- a strand thinner than a cell goes, a fin or a wing keeps its outline.
//   - the coat (the far quills: a fringe a pixel wide at that size) left out. (A sheep's fleece is NOT a coat: it is its
//     surface, kept.)
// The near and the far meshes are untouched: a close-up is exactly what it was.
import { simplify } from "./sculpt.js";

export const VFAR = { share: .35, min: 500, max: 1800, cells: 48, anchor: 400 };

// L: the far LOD as dressBody made it; shapeL: the shape's far LOD (its surface: pos, tri); quills: the far coat or null
export function veryFar(L, shapeL, quills) {
  const nv = shapeL.pos.length / 3, nt = shapeL.tri.length / 3;
  const V = L.pos.length / 3, T = L.index.length / 3;
  const qv = quills ? quills.pos.length / 3 : 0, qt = quills ? quills.tri.length / 3 : 0;
  const target = Math.max(VFAR.min, Math.min(VFAR.max, Math.round(nt * VFAR.share)));
  const S = nt > target * 1.25 ? simplify({ pos: L.pos.subarray(0, 3 * nv), tri: L.index.subarray(0, 3 * nt) }, target, { anchor: paintAnchors(L, nv, nt) })
    : { pos: L.pos.subarray(0, 3 * nv), tri: L.index.subarray(0, 3 * nt), src: Int32Array.from({ length: nv }, (_, v) => v), same: true };   // (as coarse already)
  const sv = S.pos.length / 3, st = S.tri.length / 3;
  const ev = V - nv - qv, et = T - nt - qt;   // (the eyes and the details: between the surface and the coat)
  const C = cluster(L.pos, L.index, nv, ev, nt, et);
  const cv = C.src.length, ct = C.tri.length / 3, V2 = sv + cv, out = {};
  for (const [key, a] of Object.entries(L)) {
    if (!ArrayBuffer.isView(a) || key === "index") continue;
    const n = a.length / V, b = new a.constructor(V2 * n);
    if (key === "pos") { b.set(S.pos); b.set(C.pos, 3 * sv); }
    else {
      for (let v = 0; v < sv; v++) for (let k = 0; k < n; k++) b[v * n + k] = a[S.src[v] * n + k];
      for (let v = 0; v < cv; v++) for (let k = 0; k < n; k++) b[(sv + v) * n + k] = a[C.src[v] * n + k];
    }
    out[key] = b;
  }
  if (out.nor && !S.same) smoothNormals(out.pos, S.tri, sv, out.nor);   // (the surface's own shading, not the far mesh's vertices')
  const index = new Uint32Array((st + ct) * 3);
  index.set(S.tri);
  for (let i = 0; i < 3 * ct; i++) index[3 * st + i] = C.tri[i] + sv;
  out.index = index;
  return st + ct < .8 * T ? out : null;   // (not much coarser: the far mesh serves)
}
// the surface's colour boundaries held (as bodymesh.js holds them for the near and far meshes: paintAnchors there) --
// a sheep's black face, a cow's blaze, a horse's socks stay where the far mesh drew them; the weight a vertex's
// largest colour step to a neighbour, times VFAR.anchor and the surface's mean squared edge
function paintAnchors(L, nv, nt) {
  const col = L.col, I = L.index, c = new Float32Array(nv), P = L.pos;
  let e2 = 0;
  for (let f = 0; f < 3 * nt; f += 3) for (let e = 0; e < 3; e++) {
    const a = I[f + e], b = I[f + (e + 1) % 3];
    e2 += (P[3 * a] - P[3 * b]) ** 2 + (P[3 * a + 1] - P[3 * b + 1]) ** 2 + (P[3 * a + 2] - P[3 * b + 2]) ** 2;
    if (!col) continue;
    const d = Math.hypot(col[3 * a] - col[3 * b], col[3 * a + 1] - col[3 * b + 1], col[3 * a + 2] - col[3 * b + 2]);
    if (d > c[a]) c[a] = d; if (d > c[b]) c[b] = d;
  }
  e2 /= 3 * nt || 1;
  return Float64Array.from(c, (x) => (x > .06 ? VFAR.anchor * x * e2 : 0));
}
// area-weighted vertex normals of the first n vertices over the triangles T (written into nor, stride 3)
function smoothNormals(P, T, n, nor) {
  const N = new Float64Array(3 * n);
  for (let f = 0; f < T.length; f += 3) {
    const a = T[f], b = T[f + 1], c = T[f + 2];
    const ux = P[3 * b] - P[3 * a], uy = P[3 * b + 1] - P[3 * a + 1], uz = P[3 * b + 2] - P[3 * a + 2];
    const vx = P[3 * c] - P[3 * a], vy = P[3 * c + 1] - P[3 * a + 1], vz = P[3 * c + 2] - P[3 * a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    for (const v of [a, b, c]) { N[3 * v] += nx; N[3 * v + 1] += ny; N[3 * v + 2] += nz; }
  }
  for (let v = 0; v < n; v++) {
    const l = Math.hypot(N[3 * v], N[3 * v + 1], N[3 * v + 2]);
    if (l > 0) { nor[3 * v] = N[3 * v] / l; nor[3 * v + 1] = N[3 * v + 1] / l; nor[3 * v + 2] = N[3 * v + 2] / l; }
  }
}
// the vertices [v0, v0 + n) and triangles [t0, t0 + m) clustered on a grid of VFAR.cells across the whole mesh's box:
// { pos (each cell's mean), src (its first vertex: whose paint and skin it takes), tri (renumbered from 0) }
function cluster(P, I, v0, n, t0, m) {
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < P.length; i++) { const k = i % 3; if (P[i] < lo[k]) lo[k] = P[i]; if (P[i] > hi[k]) hi[k] = P[i]; }
  const c = Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) / VFAR.cells || 1;
  const of = new Map(), id = new Int32Array(n), src = [], sum = [], cnt = [];
  for (let v = 0; v < n; v++) {
    const x = P[3 * (v0 + v)], y = P[3 * (v0 + v) + 1], z = P[3 * (v0 + v) + 2];
    const key = Math.floor((x - lo[0]) / c) + 4096 * (Math.floor((y - lo[1]) / c) + 4096 * Math.floor((z - lo[2]) / c));
    let j = of.get(key);
    if (j === undefined) { of.set(key, j = src.length); src.push(v0 + v); sum.push(0, 0, 0); cnt.push(0); }
    id[v] = j; sum[3 * j] += x; sum[3 * j + 1] += y; sum[3 * j + 2] += z; cnt[j]++;
  }
  const tri = [], seen = new Set(), used = new Int32Array(src.length).fill(-1), keep = [];
  for (let t = t0; t < t0 + m; t++) {
    const a = id[I[3 * t] - v0], b = id[I[3 * t + 1] - v0], d = id[I[3 * t + 2] - v0];
    if (a === b || b === d || a === d) continue;
    const r = a < b && a < d ? [a, b, d] : b < d ? [b, d, a] : [d, a, b], key = (r[0] * 65536 + r[1]) * 65536 + r[2];   // (the same turn: one; a face and its back both kept)
    if (seen.has(key)) continue;
    seen.add(key);
    for (const j of r) { if (used[j] < 0) { used[j] = keep.length; keep.push(j); } tri.push(used[j]); }
  }
  const pos = new Float32Array(keep.length * 3);
  keep.forEach((j, i) => { pos[3 * i] = sum[3 * j] / cnt[j]; pos[3 * i + 1] = sum[3 * j + 1] / cnt[j]; pos[3 * i + 2] = sum[3 * j + 2] / cnt[j]; });
  return { pos, src: keep.map((j) => src[j]), tri };
}
// the dressed body B with its third mesh added (B.lods[2]), made from the shape S it was dressed on
export function withVeryFar(B, S) {
  const L = B.lods[1], sL = S?.lods?.[1];
  if (!L || !sL || B.lods.length !== 2) return B;
  try {
    const far = veryFar(L, sL, S.quills?.[1] ?? null);
    if (far) { B.lods.push(far); B.stats.tris = B.lods.map((o) => o.index.length / 3); }
  } catch (e) { B.stats.vfarError = String(e.message ?? e); }
  B.vfar = 1;   // (made, or none needed: bodies.js does not dress it again)
  return B;
}
