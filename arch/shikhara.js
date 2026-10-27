// THE NAGARA TOWER (shikhara, rekha-prasada): the tower over a north Indian temple's sanctum, as the Shilpa texts and the
// masons of Khajuraho and Bhubaneswar set it out. Nothing in it is drawn freehand; every piece follows from a few numbers:
//
//   PLAN        a square broken into RATHAS -- each side in 2k + 1 offsets, the KARNAS at the corners, the BHADRA in the
//               middle, each offset standing `step` further out than the one beside it toward the middle (tri-, pancha-,
//               sapta-ratha: 3, 5, 7). The offsets run up the whole tower, so its every course is the same plan.
//   CURVE       the plan scaled down as it rises, along the REKHA: nearly upright at the foot, bending in toward the
//               shoulder (skandha), where it is `top` of its width -- 1 - (1 - top) (y / H)^bend.
//   STOREYS     the height in `bhumis`, each closed by a band standing out a little (the bhumi-amalakas that mark the
//               storeys on the karnas, read as one course round the tower).
//   CROWN       on the shoulder the neck (griva), the AMALAKA -- a flattened, ribbed stone disc as wide as the shoulder,
//               named for the amla fruit it is cut like -- a lesser amalaka over it, and the KALASHA, the water pot.
//   SELF-SIMILAR the tower carries smaller copies of itself: URUSHRINGAS on each bhadra, tier over tier (`tiers`: each a
//               `scale` of the tower, its foot `lift` up it, `out` the share of its depth standing proud of the face), each
//               one a whole shikhara with its own storeys and crown -- and copies on the copies, `nest` deep -- and
//               KARNA-SHRINGAS, small spires on the corners. So Kandariya Mahadeva's tower is eighty-four towers.
//
// One part per tier of copies (and one for the corner spires, one for the crowns) -- copies of one tier stand on
// different faces and never cut each other, so each part stays a set of separate solids. Built in the tower's frame,
// its foot at y 0; `put(key)` hands back the mesh a piece goes in.
import { stackMesh, lathe } from "./build.js";

// THE RATHA PLAN: corners of the outline, counter-clockwise as planPoints' (along -z going +x first), `a` from the
// middle to a karna's face, `rathas` offsets a side (odd), the bhadra `bhadra` of the side, every offset `step` out
export function rathaPlan(a, rathas = 5, step = .1, bhadra = .3) {
  const k = Math.max(0, Math.round((rathas - 1) / 2)), side = 2 * a;
  const bw = k ? side * bhadra : side, rest = k ? (side - bw) / (2 * k) : 0;
  const b = [-a];
  for (let j = 0; j < 2 * k + 1; j++) b.push(b[j] + (j === k ? bw : rest));
  const p = (j) => (k - Math.abs(j - k)) * step;                         // (how far offset j stands out)
  const one = [[-a, -a]];
  for (let j = 1; j <= 2 * k; j++) one.push([b[j], -(a + p(j - 1))], [b[j], -(a + p(j))]);
  const out = [];
  for (let q = 0; q < 4; q++) for (const [x, z] of one) {
    let X = x, Z = z;
    for (let r = 0; r < q; r++) [X, Z] = [-Z, X];                          // (a quarter turn: the -z side onto +x)
    out.push([X, Z]);
  }
  // (planPoints' winding, the outside on the left of every edge, as stackMesh wants it; `face`: the bhadra's face
  //  from the middle)
  return { pts: out.reverse(), face: a + k * step };
}

// the measures, defaults filled in
export function shikharaSpec(s) {
  return { a: s.a, H: s.H, rathas: s.rathas ?? 5, step: s.step ?? s.a * .08, bhadra: s.bhadra ?? .3, top: s.top ?? .55,
           bend: s.bend ?? 1.7, bhumis: s.bhumis ?? 7, band: s.band ?? .035, bandH: s.bandH ?? .22,
           tiers: s.tiers ?? [], nest: s.nest ?? 1, corners: s.corners ?? null, ribs: s.ribs ?? 16, crown: s.crown ?? true };
}
// how high the crown reaches over the shoulder, a share of the shoulder's half-width
const CROWN = [["neck", .22], ["amalaka", .5], ["chandrika", .07], ["amalasaraka", .24], ["kalasha", .95]];
export const crownRise = (s) => CROWN.reduce((t, [, h]) => t + h, 0) * shoulder(s);
const shoulder = (s) => s.a * s.top * (1 + s.band);
export const shikharaHeight = (s) => s.H + (s.crown ? crownRise(s) : 0);

// THE CROWN on a shoulder `r` (half its width) at height `y`, in `m`: the neck, the ribbed AMALAKA, the moon disc
// (chandrika), the lesser amalaka (amalasaraka), the KALASHA -- each a turned solid set on the last; a `bell` first
// (a samvarana roof's ghanta, `bell` high in shares of r). Its lobes are as many as its size calls for: `ribs` on a
// crown 2.2m across the shoulder or more, down to six; a small one is cut as the carver cuts it at that size, the
// amalaka on its neck and the pot, to the same height. Returns the height of its tip.
export function crownMesh(m, r, y, ribs = 16, bell = 0) {
  const sides = Math.max(6, Math.round(ribs * Math.min(1, r / 2.2)));
  const turned = (prof, n) => { lathe(m, prof.map(([pr, py]) => [pr * r, y + py * r]), n); y += prof[prof.length - 1][1] * r; };
  // (a ribbed disc: every other point of its rings sunk into a groove -- the amla's lobes)
  const ribbed = (rad, ht, prof = [[.55, 0], [.86, .16], [1, .5], [.86, .84], [.55, 1]]) => {
    const n = 2 * sides;
    const rings = prof.map(([pr, py]) => Array.from({ length: n }, (_, k) => {
      const t = k * 2 * Math.PI / n, f = rad * r * pr * (k % 2 ? .86 : 1);
      return m.vert(f * Math.cos(t), y + py * ht * r, f * Math.sin(t));
    }));
    for (let j = 0; j + 1 < rings.length; j++) for (let k = 0; k < n; k++) m.quad(rings[j][k], rings[j + 1][k], rings[j + 1][(k + 1) % n], rings[j][(k + 1) % n]);
    const c0 = m.vert(0, y, 0), c1 = m.vert(0, y + ht * r, 0), lo = rings[0], hi = rings[rings.length - 1];
    for (let k = 0; k < n; k++) { m.tri(c0, lo[k], lo[(k + 1) % n]); m.tri(c1, hi[(k + 1) % n], hi[k]); }
    y += ht * r;
  };
  if (bell) turned([[1, 0], [.96, .12 * bell], [.8, .42 * bell], [.55, .74 * bell], [.32, .94 * bell], [.3, bell]], sides);   // the ghanta
  if (r >= .8) {
    turned([[.62, 0], [.62, .22]], sides);                                  // the neck
    ribbed(1.08, .5);                                                       // the amalaka
    turned([[.7, 0], [.7, .07]], sides);                                    // the chandrika
    ribbed(.5, .24);                                                        // the amalasaraka
    turned([[.22, 0], [.36, .2], [.4, .38], [.3, .58], [.12, .68], [.17, .76], [.03, .95]], Math.max(6, Math.round(sides / 2)));   // the kalasha
  } else {
    ribbed(1.08, .72, [[.6, 0], [.62, .3], [1, .65], [.6, 1]]);
    turned([[.22, 0], [.4, .4], [.12, .9], [.03, 1.26]], 6);
  }
  return y;
}

// ONE SHIKHARA, its copies and crowns: `T(x, y, z)` places a point of it (its frame into the caller's), `key` the part
// its body goes in
export function shikharaMesh(put, spec, { T = (x, y, z) => [x, y, z], key = "body", path = "", depth = 0 } = {}) {
  const s = shikharaSpec(spec), { pts, face } = rathaPlan(s.a, s.rathas, s.step, s.bhadra);
  const via = (m) => ({ vert: (x, y, z) => m.vert(...T(x, y, z)), tri: (a, b, c) => m.tri(a, b, c), quad: (a, b, c, d) => m.quad(a, b, c, d) });
  const sc = (y) => 1 - (1 - s.top) * Math.pow(Math.max(0, y) / s.H, s.bend);
  const ring = (y, f) => ({ y, pts: pts.map(([x, z]) => [x * f, z * f]) });
  // THE BODY: storey on storey, each closed by its band
  const N = Math.max(1, Math.round(s.bhumis)), h = s.H / N, bh = h * s.bandH, L = [ring(0, sc(0))];
  for (let i = 0; i < N; i++) {
    const y1 = (i + 1) * h, yb = y1 - bh;
    L.push(ring(yb, sc(yb)), ring(yb, sc(yb) * (1 + s.band)), ring(y1, sc(y1) * (1 + s.band)));
    if (i + 1 < N) L.push(ring(y1, sc(y1)));
  }
  stackMesh(via(put(key)), L);
  // THE CROWN: neck, ribbed amalaka, the moon disc, the lesser amalaka, the pot -- each a turned solid on the last
  if (s.crown) crownMesh(via(put("crown")), shoulder(s), s.H, s.ribs);
  // THE COPIES on each bhadra, tier by tier (a quarter turn per face: their own bhadras look out with the tower's)
  if (depth < s.nest) s.tiers.forEach((t, ti) => {
    const cs = { ...spec, a: s.a * t.scale, H: s.H * t.scale, step: s.step * t.scale, rathas: Math.max(1, s.rathas - 2),
                 bhumis: Math.max(3, Math.round(s.bhumis * t.scale)), corners: null };
    const y0 = t.lift * s.H, d = face * sc(y0) - cs.a + 2 * cs.a * (t.out ?? .45);
    const k = path + (path ? "." : "") + (ti + 1);
    for (let q = 0; q < 4; q++) {
      const ang = q * Math.PI / 2, c = Math.cos(ang), sn = Math.sin(ang);
      // (face q: the copy's own -z face outward on the tower's -z face, turned a quarter at a time as rathaPlan's sides)
      const Tq = (x, y, z) => { const zz = z - d; return T(x * c - zz * sn, y + y0, x * sn + zz * c); };
      shikharaMesh(put, cs, { T: Tq, key: "shringas " + k, path: k, depth: depth + 1 });
    }
  });
  // THE CORNER SPIRES: on each karna, half sunk into the tower's corner
  if (s.corners && depth === 0) for (const lift of s.corners.at ?? [0]) {
    const cs = { ...spec, a: s.a * s.corners.scale, H: s.H * s.corners.scale, step: s.step * s.corners.scale, rathas: 1,
                 bhumis: Math.max(2, Math.round(s.bhumis * s.corners.scale)), tiers: [], corners: null };
    const y0 = lift * s.H, e = s.a * sc(y0) - cs.a * .4;
    for (const [sx, sz] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
      shikharaMesh(put, cs, { T: (x, y, z) => T(x + sx * e, y + y0, z + sz * e), key: "karna shringas", path: "k", depth: s.nest });
    }
  }
}

// THE STEPPED ROOF of a hall (phamsana; samvarana when bells crown its tiers): the mandapas before the sanctum are
// roofed with pyramids of SLABS, each a course projecting as an eave, its top sloping back to the recessed neck under
// the next -- the same ratha plan as the tower's, narrowing tier by tier from `a` to `top` of it, `tiers` courses up
// `rise`. On a samvarana a small BELL (ghanta) sits on every course at its corners and over its bhadras, and a great
// bell crowns the whole, with the amalaka and kalasha over it. The halls' roofs rise one over another toward the
// tower -- the porch's lowest, the great hall's highest -- like the foothills of the mountain the tower is (Kailasa).
// A hall longer than it is wide (`len`, its length over its width) has every course drawn out along z alike, the crown
// round on the last. `put(key)`: "body", "bells", "crown".
export function samvaranaSpec(s) {
  return { a: s.a, rise: s.rise, tiers: s.tiers ?? 5, top: s.top ?? .3, rathas: s.rathas ?? 3, step: s.step ?? s.a * .06,
           bhadra: s.bhadra ?? .34, bells: s.bells ?? true, ribs: s.ribs ?? 16, len: s.len ?? 1 };
}
const BELL = 1.1;   // (the great bell's height, in shares of the top's half-width)
export const samvaranaHeight = (s) => {
  // (the crown's own height over its bell, as crownMesh builds it: 1.98 of its shoulder, large or small)
  return s.rise + s.a * s.top * (BELL + 1.98);
};
export function samvaranaMesh(put, spec) {
  const s = samvaranaSpec(spec), n = Math.max(1, Math.round(s.tiers)), h = s.rise / n, d = s.a * (1 - s.top) / n;
  const { pts, face } = rathaPlan(s.a, s.rathas, s.step, s.bhadra);
  const ring = (y, a) => ({ y, pts: pts.map(([x, z]) => [x * a / s.a, z * a / s.a * s.len]) }), rec = Math.min(d * .7, s.a * .05);
  const L = [];
  for (let i = 0; i < n; i++) {
    const y0 = i * h, a0 = s.a - i * d, a1 = a0 - d;
    if (i) L.push(ring(y0, a0));
    else L.push(ring(0, a0));
    L.push(ring(y0 + h * .3, a0), ring(y0 + h * .68, a1 - rec), ring(y0 + h, a1 - rec));
  }
  L.push(ring(s.rise, s.a * s.top));
  stackMesh(put("body"), L);
  // the bells on every course: on its sloping top, at the corners and over the bhadras
  if (s.bells) {
    const bm = put("bells");
    for (let i = 0; i < n; i++) {
      const y = i * h + h * .5, a0 = s.a - i * d, a1 = a0 - d, rb = Math.min(d * .55, h * .45), at = (a0 + a1 - rec) / 2 + rb * .15;
      const f = face / s.a;
      for (const [x, z] of [[-at, -at], [at, -at], [at, at], [-at, at], [0, -at * f], [at * f, 0], [0, at * f], [-at * f, 0]]) {
        const prof = [[1, 0], [.95, .25], [.7, .6], [.35, .9], [.12, 1.25]];
        lathe({ vert: (px, py, pz) => bm.vert(px + x, py, pz + z * s.len), tri: bm.tri, quad: bm.quad }, prof.map(([pr, py]) => [pr * rb, y - rb * .25 + py * rb]), 6);
      }
    }
  }
  crownMesh(put("crown"), s.a * s.top, s.rise, s.ribs, BELL);
}
