// COURSES: the mouldings that run along a wall's outer face -- the PLINTH at its foot, a STRING COURSE at every floor
// line (where one tier of the facade stands on the next), the CORNICE crowning it. None of them is placed by eye: each
// is a PROFILE (a section, out from the face and up the wall) carried along the face's own line at a height the wall
// itself gives -- its foot, its tier joints, its top -- and
//   round a corner it is MITRED: each line of the profile runs on to where it meets its neighbour's offset line, so a
//   cornice turns the corner of a tower as one moulding, out on a convex corner and in on a concave one;
//   at an opening that cuts through its height it STOPS at the jambs, its end closed (a string course is broken by
//   the window it would cross, a plinth by the door), and at a free end of a wall it is closed the same way.
// Sizes follow the wall: the plinth and the cornice from its height, a string course from the tier it runs under, and
// how far each stands out from its own height -- `courses: { plinth, strings, cornice }` may give any of them as
// { h, out, profile } (or false to leave it off; `strings` a list of heights instead of the tier joints, or `at` one
// in its object).
import { earClip, wallFace } from "./build.js";

// THE PROFILES, in a unit section: o out from the face (1: the moulding's projection), u up from its foot (1: its
// height), from the face at the foot round to the face at the top -- counter-clockwise with o to the right
export const PROFILES = {
  // a block with a chamfered top, shedding the rain: the water table
  plinth: [[0, 0], [1, 0], [1, .55], [.45, 1], [0, 1]],
  // a band with a drip under it and a weathered top
  string: [[0, 0], [.35, 0], [1, .4], [1, .7], [0, 1]],
  // corbelled out in steps to the corona, the drip under its edge, a cyma on top
  cornice: [[0, 0], [.18, 0], [.18, .18], [.4, .3], [.5, .45], [1, .55], [1, .8], [.85, .88], [.6, 1], [0, 1]],
  // a plain band: a fascia
  band: [[0, 0], [1, 0], [1, 1], [0, 1]],
  // the TALUS of a fortress wall: its foot spreading in one slope down to the ground (the batter)
  batter: [[0, 0], [1, 0], [0, 1]],
  // the Egyptian TORUS: a roll, a half round standing out from the face (round the corners of a battered mass and
  // under its cornice, as if the reeds of the first shrines were bound there) -- `out` half its `h` keeps it round
  torus: Array.from({ length: 9 }, (_, k) => [Math.sin(k * Math.PI / 8), .5 - .5 * Math.cos(k * Math.PI / 8)]),
  // the CAVETTO or GORGE, the Egyptian cornice: a hollow that rises out of the face and sweeps forward, as palm fronds
  // tied to the top of a reed wall bend out under their weight, a fillet over it
  gorge: [...Array.from({ length: 8 }, (_, k) => { const s = k / 7; return [1 - Math.sqrt(1 - s * s), s * .82]; }), [1, .82], [1, 1], [0, 1]],
  // THE NAGARA PLINTH'S (the adhishthana's) mouldings, foot to top: the KHURA, a hoof -- a block whose top slopes
  // steeply back to the face; the KUMBHA, a pot -- a fillet, then the belly swelling out and drawn in again under a
  // neck; the KALASHA, a smaller roll between fillets; the KAPOTA, the "dovecote" eave -- its underside curving out and
  // down to a drooping beak, its top drawn back to the face
  khura: [[0, 0], [1, 0], [1, .35], [.25, 1], [0, 1]],
  kumbha: [[0, 0], [.6, 0], [.6, .1], ...Array.from({ length: 7 }, (_, k) => { const s = (k + 1) / 8; return [.6 + .4 * Math.sin(Math.PI * s), .1 + .72 * s]; }), [.5, .82], [.5, 1], [0, 1]],
  kalasha: [[0, 0], [.55, 0], [.55, .15], ...Array.from({ length: 5 }, (_, k) => { const s = (k + 1) / 6; return [.55 + .45 * Math.sin(Math.PI * s), .15 + .7 * s]; }), [.55, .85], [.55, 1], [0, 1]],
  kapota: [[0, 0], [.2, 0], [.55, .12], [.82, .32], [.97, .56], [1, .72], [.92, .82], [.7, .9], [0, 1]],
};

// The courses a wall asks for, from its height `H`, its thickness `t` and its tier joints: [{ y, h, out, profile }]
export function coursesOf(spec, H, t, joints = []) {
  if (!spec) return [];
  // (a LIST: the courses outright, each { y, h, out, profile } -- a wall whose mouldings are not plinth, strings and
  //  cornice, as the Egyptian batter, torus and gorge)
  if (Array.isArray(spec)) return spec.filter((c) => c.h > 0 && c.out > 0 && c.y >= -1e-9 && c.y + c.h <= H + 1e-9);
  const s = spec === true ? {} : spec, out = [];
  const one = (v, d) => (v === false ? null : { ...d, ...(typeof v === "object" ? v : {}) });
  const pl = one(s.plinth, { h: Math.max(.35, Math.min(1, H * .045)), profile: "plinth" });
  if (pl) out.push({ y: 0, ...pl, out: pl.out ?? Math.min(.3, Math.max(.12, t * .2)) });
  const st = one(s.strings, { profile: "string" });
  const ys = Array.isArray(s.strings) ? s.strings : s.strings?.at ?? joints;
  if (st) for (const y of ys) { const h = st.h ?? Math.max(.22, Math.min(.5, H * .015)); out.push({ y: y - h * .35, ...st, h, out: st.out ?? h * .55 }); }
  const co = one(s.cornice, { h: Math.max(.4, Math.min(1.4, H * .045)), profile: "cornice" });
  if (co) out.push({ y: H - co.h, ...co, out: co.out ?? co.h * .9 });
  return out.filter((c) => c.h > 0 && c.out > 0 && c.y >= -1e-9 && c.y + c.h <= H + 1e-9);
}

// THE MESH: `line` the face's outer line in plan ([x, z] points: an outline, `closed`, or a wall's run), the outside on
// the left of it walking it; `courses` from coursesOf; `gaps[i]` the openings in segment i, [{ x0, x1, y0, y1 }]
// measured along it (what cuts a course through its height stops it there)
// (`skip`: the segments it does not run along -- a face against a neighbouring block, or inside one: a moulding
// coming to such a corner stops flush there, and the neighbour's own course takes up from it)
// (`ghost`: segments not drawn but mitred into -- a bay of a ring is built alone, with its neighbours' first and last
// segments as ghosts, so its courses meet theirs in true mitres when the bay is turned round the ring)
export function coursesMesh(m, line, courses, { closed = false, gaps = [], skip = new Set(), ghost = new Set() } = {}) {
  const N = line.length, S = closed ? N : N - 1;
  const seg = Array.from({ length: S }, (_, i) => {
    const A = line[i], B = line[(i + 1) % N], L = Math.hypot(B[0] - A[0], B[1] - A[1]), e = [(B[0] - A[0]) / L, (B[1] - A[1]) / L];
    return { A, B, L, e, n: [-e[1], e[0]] };
  });
  // how far line `o` out from the face runs past the corner between segments i and j (in each one's own direction):
  // where the two offset lines meet
  const mitre = (i, j, o) => {
    const a = seg[i], b = seg[j], d = [(b.n[0] - a.n[0]) * o, (b.n[1] - a.n[1]) * o];
    const det = a.e[0] * -b.e[1] - a.e[1] * -b.e[0];
    if (Math.abs(det) < 1e-9) return [0, 0];
    const s = (d[0] * -b.e[1] - d[1] * -b.e[0]) / det, r = (a.e[0] * d[1] - a.e[1] * d[0]) / det;
    return [s, r];     // past the end of a, and (negative: before) the start of b
  };
  for (const c of courses) {
    const prof = c.pts ?? (PROFILES[c.profile] ?? PROFILES.band).map(([o, u]) => [o * c.out, u * c.h]);   // (`pts`: a section in metres -- an entablature's)
    const cap = earClip(prof, prof.map((_, k) => k));
    seg.forEach((g, i) => {
      if (skip.has(i) || ghost.has(i)) return;
      // the runs along this segment: all of it, less what the openings through its height take
      const cuts = (gaps[i] ?? []).filter((q) => q.y0 < c.y + c.h - 1e-6 && q.y1 > c.y + 1e-6).map((q) => [q.x0, q.x1]).sort((p, q) => p[0] - q[0]);
      const runs = [];
      let x = 0;
      for (const [x0, x1] of cuts) { if (x0 > x + 1e-6) runs.push([x, x0]); x = Math.max(x, x1); }
      if (g.L > x + 1e-6) runs.push([x, g.L]);
      const prev = closed ? (i + S - 1) % S : i - 1, next = closed ? (i + 1) % S : i + 1;
      for (const [x0, x1] of runs) {
        // an end at a corner of the outline is mitred to the next segment's; any other end is closed
        const atStart = x0 < 1e-6 && prev >= 0 && !skip.has(prev), atEnd = x1 > g.L - 1e-6 && next < S && !skip.has(next);
        const P = (x, k, end) => {
          const [o, u] = prof[k];
          const ext = end ? (atEnd ? mitre(i, next, o)[0] : 0) : (atStart ? mitre(prev, i, o)[1] : 0);
          const along = x + ext;
          return [g.A[0] + g.e[0] * along + g.n[0] * o, c.y + u, g.A[1] + g.e[1] * along + g.n[1] * o];
        };
        for (let k = 0; k + 1 < prof.length; k++) {
          const [o1, u1] = prof[k], [o2, u2] = prof[k + 1];
          // the face's outward normal: (du, -do) in the section, turned into the plan
          const want = [g.n[0] * (u2 - u1), -(o2 - o1), g.n[1] * (u2 - u1)];
          const q = [P(x0, k, false), P(x1, k, true), P(x1, k + 1, true), P(x0, k + 1, false)];
          quadToward(m, q, want);
        }
        // the ends: closed where the moulding stops (at a jamb, or a wall's free end)
        for (const [xe, isEnd, mitred] of [[x0, false, atStart], [x1, true, atEnd]]) {
          if (mitred) continue;
          const ps = prof.map((_, k) => P(xe, k, isEnd)), ids = ps.map((v) => m.vert(...v));
          const dir = isEnd ? 1 : -1, want = [g.e[0] * dir, 0, g.e[1] * dir];
          for (const [a, b, d] of cap) {
            const u = [ps[b][0] - ps[a][0], ps[b][1] - ps[a][1], ps[b][2] - ps[a][2]], v = [ps[d][0] - ps[a][0], ps[d][1] - ps[a][1], ps[d][2] - ps[a][2]];
            const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
            if (n[0] * want[0] + n[1] * want[1] + n[2] * want[2] >= 0) m.tri(ids[a], ids[b], ids[d]); else m.tri(ids[a], ids[d], ids[b]);
          }
        }
      }
    });
  }
  return m;
}

function quadToward(m, q, want) {
  const [p0, p1, , p3] = q, u = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]], v = [p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]];
  const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  const ids = q.map((p) => m.vert(...p));
  if (n[0] * want[0] + n[1] * want[1] + n[2] * want[2] >= 0) m.quad(...ids); else m.quad(ids[3], ids[2], ids[1], ids[0]);
}

// THE GAPS IN A FACE: its openings laid out, tier by tier, as the spans they cut through it -- [{ x0, x1, y0, y1 }]
export function faceGaps(L, tiers) {
  const out = [];
  let y = 0;
  for (const t of tiers) {
    for (const o of wallFace(L, t.h, t.openings ?? []).openings) out.push({ x0: o.x0, x1: o.x1, y0: y + o.sill - (o.foot ? Math.max(0, ...o.foot.map(([, fy]) => -fy)) : 0), y1: y + o.crown });
    y += t.h;
  }
  return out;
}
