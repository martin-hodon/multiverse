// THE LOMBARD BAND (Rundbogenfries und Lisenen): how a Romanesque wall is articulated, from Lombardy over the Rhine
// to Catalonia -- the wall divided into fields by LESENES, flat pilaster strips without base or capital, at its two
// ends and every `bay` between, and under the eaves an ARCHED CORBEL TABLE: a band of small round arches hanging from
// a strip, each arch's feet on a little CORBEL, running from lesene to lesene. All of it from the face: the fields
// as many as `bay` gives (whole ones), the arches in each a whole number about `arch` wide, the band at the face's top
// (or `drop` below it); a lesene that would cross an opening is left out, and an arch over an opening's head is too.
// `spec`: { arch (0.7), band (0.22), depth (0.2), lesene (0.6), bay (5), drop (0), foot (0), lesenes (true), side }.
// Drawn proud of the face (wimperg.js proudOf), into the mesh its openings' dressings go in.
import { proudOf } from "./wimperg.js";

export function lombardMesh(face, spec, map, m, top = face.h) {
  const L = face.w;
  // (`clear`: stretches of the face [from, to] something stands against -- a stair tower, a buttress: the band stops
  //  at them, a lesene at either side, and the rest is laid out stretch by stretch as a face of its own)
  const cl = (spec.clear ?? []).map(([a, b]) => [Math.max(0, Math.min(a, b)), Math.min(L, Math.max(a, b))]).filter(([a, b]) => b > a).sort((p, q) => p[0] - q[0]);
  let x = 0;
  for (const [a, b] of cl) { if (a > x) lombardRun(face, spec, map, m, top, x, a); x = Math.max(x, b); }
  if (L > x) lombardRun(face, spec, map, m, top, x, L);
  return m;
}
function lombardRun(face, spec, map, m, top, X0, X1) {
  const L = X1 - X0, a0 = spec.arch ?? .7, band = spec.band ?? .22, d = spec.depth ?? .2, lw = Math.min(spec.lesene ?? .6, L / 6);
  const yT = Math.min(face.h, top) - (spec.drop ?? 0), foot = spec.foot ?? 0;
  if (L < 2 * lw + a0 || yT - foot < band + a0) return m;
  const { slab: slab_ } = proudOf((x, y, s) => map(x + X0, y, s), spec.side ? 1 : 0, m);
  const slab = (pts, d0, d1, hide) => slab_(pts, d0, d1, false, hide);
  const ops = (face.openings ?? []).map((o) => ({ ...o, x0: o.x0 - X0, x1: o.x1 - X0 }));
  // (does a box of the face cut an opening -- its jambs and its head, with a hand's breadth round it?)
  const hits = (x0, x1, y0, y1) => ops.some((o) => x0 < o.x1 + .1 && x1 > o.x0 - .1 && y0 < o.crown + .1 && y1 > o.sill - .1);
  // THE LESENES: at the ends and every bay, each the whole height under the band -- unless an opening is in its way
  const nb = Math.max(1, Math.round((L - lw) / (spec.bay ?? 5))), step = (L - lw) / nb;
  const les = spec.lesenes === false ? [0, nb] : Array.from({ length: nb + 1 }, (_, i) => i);
  const posts = les.map((i) => i * step).filter((x) => !hits(x, x + lw, foot, yT - band));
  for (const x of posts) slab([[x, foot], [x + lw, foot], [x + lw, yT - band], [x, yT - band]], 0, d, [0, 2]);   // (its foot and its head against the band: unseen)
  // THE BAND the arches hang from, the face's whole length
  slab([[0, yT - band], [L, yT - band], [L, yT], [0, yT]], 0, d);
  // THE ARCHES, field by field: between each lesene and the next (or the face's ends where there are none)
  const edges = [0, ...posts.flatMap((x) => [x, x + lw]), L].sort((p, q) => p - q);
  for (let i = 0; i + 1 < edges.length; i += 2) {
    const f0 = edges[i], f1 = edges[i + 1], span = f1 - f0;
    if (span < a0 * .6) continue;
    const k = Math.max(1, Math.round(span / a0)), w = span / k, r = w / 2, yC = yT - band, yS = yC - r;
    for (let j = 0; j < k; j++) {
      const xa = f0 + j * w, xm = xa + r, xb = xa + w;
      if (hits(xa, xb, yS - .25, yC)) continue;
      // (each half of the spandrel over the arch, drawn as a fan from its top corner -- all of the quarter-circle in
      //  sight of it -- the arch's own curve its lower edge)
      const q = (s) => Array.from({ length: 2 }, (_, t) => { const an = Math.PI / 2 * (t + 1) / 3; return [xm + s * r * Math.cos(an), yS + r * Math.sin(an)]; });
      // (only the curve's sides are drawn -- the top is under the band, the upright against the next arch or a lesene --
      //  but at the face's own ends)
      slab([[xa, yC], [xa, yS], ...q(-1), [xm, yC]], 0, d, xa > 1e-6 ? [0, 4] : [4]);
      slab([[xb, yC], [xm, yC], ...q(1).reverse(), [xb, yS]], 0, d, xb < L - 1e-6 ? [0, 4] : [0]);
      // the CORBEL under the arch's feet (one between two arches carries both)
      for (const xc of j === 0 ? [xa, xb] : [xb]) {
        if (posts.some((x) => Math.abs(x + lw - xc) < 1e-6 || Math.abs(x - xc) < 1e-6)) continue;   // (a lesene carries it)
        const cw = Math.min(.09, r * .4);
        slab([[xc - cw, yS - .22], [xc + cw, yS - .22], [xc + cw * 1.4, yS], [xc - cw * 1.4, yS]], 0, d * 1.3, [2]);
      }
    }
  }
  return m;
}

// THE RISING FRIEZE on a gable (steigender Rundbogenfries): the same arched corbel table run up both rakes of a gable,
// under a band that follows the rake -- each arch's crown under the band, its springing as low as the lower of its two
// feet allows, so the row climbs in steps; corbels under the feet. It begins where the first arch clears the gable's
// foot (the wall's own band is under it) and the two rows meet at the apex.
// `rakeFrieze`: one gable, in a frame of its own -- `map(x, y, s)` its face (s 1 a metre into it), the eaves at x0 and
// x1 at height y0, the apex at xc, yc. `spec`: { arch (0.7), band (0.22), depth (0.2), inset }.
export function rakeFrieze(m, map, x0e, x1e, y0, xc, yc, spec = {}) {
  const d = spec.depth ?? .2, band = spec.band ?? .22, a0 = spec.arch ?? .7;
  const { slab: slab_ } = proudOf(map, 0, m);
  const slab = (pts, d0, d1, hide) => slab_(pts, d0, d1, false, hide);
  for (const xe of [x0e, x1e]) {
    const sl = (yc - y0) / Math.abs(xc - xe), s = Math.sign(xc - xe), bv = band * Math.sqrt(1 + sl * sl);
    const rb = (x) => y0 + Math.abs(x - xe) * sl - bv;                    // (the band's underside over x)
    const x0 = xe + s * Math.max(spec.inset ?? 0, (bv + a0 * 1.2) / sl), span = Math.abs(xc - x0);
    if (span < a0) continue;
    slab([[x0, rb(x0)], [xc, yc - bv], [xc, yc], [x0, rb(x0) + bv]], 0, d);
    const n = Math.max(1, Math.round(span / a0)), w = span / n, r = w / 2, feet = new Map();
    for (let j = 0; j < n; j++) {
      const xa = x0 + s * j * w, xb = xa + s * w, lo = Math.min(xa, xb), hi = Math.max(xa, xb), xm = (lo + hi) / 2;
      const yS = Math.min(rb(lo), rb(hi)) - r, yC = yS + r;
      const q = (sg) => [1, 2].map((t) => { const an = Math.PI / 2 * t / 3; return [xm + sg * r * Math.cos(an), yS + r * Math.sin(an)]; });
      slab([[lo, rb(lo)], [lo, yS], ...q(-1), [xm, yC], [xm, rb(xm)]], 0, d, [4, 5]);
      slab([[hi, rb(hi)], [xm, rb(xm)], [xm, yC], ...q(1).reverse(), [hi, yS]], 0, d, [0, 1]);
      for (const x of [lo, hi]) { const key = x.toFixed(4), f = feet.get(key); feet.set(key, [x, Math.min(f ? f[1] : Infinity, yS)]); }
    }
    // the CORBELS, one under each foot (two arches' feet at one: under the lower)
    const cw = Math.min(.09, r * .4);
    for (const [x, y] of feet.values()) if (Math.abs(x - xc) > 1e-6) slab([[x - cw, y - .22], [x + cw, y - .22], [x + cw * 1.4, y], [x - cw * 1.4, y]], 0, d * 1.3);
  }
  return m;
}
// ...on a gable roof's ends (`levels`: build.js roofLevels with its overhang -- a gable's, the eave level and an apex line
// at x = 0), in the roof's own frame; `spec.ends`: [0] the -z one, [1] the +z one (both by default)
export function gableFriezeMesh(m, levels, spec = {}) {
  const L0 = levels[0], L1 = levels[levels.length - 1];
  if (levels.length !== 2 || Math.abs(L1.x1 - L1.x0) > 1e-6) return m;   // (a gable's apex, not a ridge's top level)
  for (const [k, z] of [[0, L0.z0], [1, L0.z1]]) {
    if (spec.ends && !spec.ends.includes(k)) continue;
    const dir = k ? 1 : -1;
    rakeFrieze(m, (x, y, s) => [x, y, z - dir * s], L0.x0, L0.x1, L0.y, L1.x0, L1.y, spec);
  }
  return m;
}
