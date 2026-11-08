// SHARP PARTS (2026-11-08): what a field of blended shapes cannot draw -- a POINT and an EDGE. Pure numbers (no
// three.js): bodymesh.js calls these for the sculpt overlay's `horn` and `fin` shapes, which are never put into the
// field and never blend with the body's shapes. Each is an explicit mesh, skinned to its bones, drawn as it is.
//
// Why: a horn, a tusk, a claw or a beak made of field shapes is a round cone sampled on the grid -- its tip a blob a cell
// or two across, its surface stepped wherever it is thinner than a few cells, and blended into whatever it touches.
// A fin, an ear, a fluke made of a stack of flat ellipsoids is stepped along its edge (each slice a cell or two of the
// grid) and bumpy across it. Here the point is a vertex and the rim is the authored curve.
//
// HORN { pts: [[x, y, z, r, (aspect)], ...] } -- a CENTRELINE through the points (a centripetal Catmull-Rom spline), the
//   first inside the body (its root end closed), the last the TIP: the radius eased to 0 there, a real apex. A regular
//   cross-section at every station -- an ellipse r wide and r x aspect high along `up` (transported along the curve
//   without turning: a rotation-minimising frame), optionally `flat` underneath (0-1: an upper mandible's flat
//   underside where it closes on the lower), a `keel` along its top (a ridge, a share of r), `twist` (degrees, root to
//   tip: a spiral tusk). Rings are spaced by how much the curve turns and the radius bends, not evenly, so a curve stays
//   smooth with few of them; `sides` round (default 12, half that on the far mesh). Normals from the surface itself.
//   Colour `color` fading to `tip` from `tipAt` (a share of its length); `bone`, and optionally `bone2`: the skin passes
//   from bone to bone2 over `blend` ([from, to], shares of its length, default [0, 1]). `fair` (a ROOT FLARE, metres or
//   { r, skin }): where it leaves the body, each ring's spokes reach out to the smooth union of the horn and the body
//   (fairAt below; smoothed round the ring, never sunk, rings bunched there) -- a boss, a gum -- its paint passing to
//   the body's below ONE LINE round it (where each spoke's share of the body falls through half of `skin`, default .3,
//   smoothed round the ring, and always a little above where that spoke leaves the skin: a clean collar, no blotches).
// FIN { root: [[x, y, z], ...], edge: [[x, y, z, (b)], ...] } -- a SHEET: its ROOT line (buried in the body: the first
//   point where the edge leaves it, the last where it comes back) and its free EDGE from the one to the other, round the
//   outline (smoothed through the points, resampled by arc length; the root's ends and the `corners` -- indices into
//   edge: a fin's tip, a fluke's notch -- kept exactly). Rows run from the root to the rim, the mid-surface is relaxed
//   between them (a smooth sheet even where the outline is not convex); `grid: "flow"` (or `flow`, a weight) solves the
//   inside harmonic instead, the columns curving with the outline (straight columns fanned out of a short root bunch
//   into a line of slivers down a swept fluke or flipper); `rootBy` (c, a share of the root's length) shares the root out
//   over the rim by its length weighted 1 / (distance from the root + c), not by plain length (a long edge running out of
//   a root end had all its columns from that end). Its THICKNESS is a function of the distance to the rim -- a SMOOTH
//   one (smoothRimDist: a Poisson solve over the planform; the true distance has a crease down the medial axis, a ridge
//   line down every blade; `thickBy: "rim"` the old raw distance): `slope` (the full thickness gained per metre in from the rim, default .3: a wedge of ~17 degrees), up to
//   `thick` (metres, the greatest, at the root) -- so the rim is a sharp edge everywhere, a broad fin is thicker than a
//   narrow one, the tip thinner than the root, the cross-section regular. `b` on an edge point (default 1) blunts the rim
//   there (2: twice as thick as near the rest of it -- a fin's leading edge: an airfoil). Two-sided, the rim's vertices
//   split so the edge stays crisp. Shaped toward `face` (the side its front looks to; default the sheet's own normal):
//   `cup` (a hollow on the face side, a share of the distance to the rim: an ear), `camber` (the sheet bowed toward face
//   along its rows, a share of their length), `curl` (its far part folded toward face, a share of the row's length at
//   the rim, from `curlAt` of the way out: the only option that moves the rim; the cup's depth is the rim distance
//   smoothed over the grid -- a round-bottomed hollow, not a V). `inner`: the face side's colour (an ear's hollow),
//   `innerRim` (metres) a band of `color` round its rim on that side; `rim` (metres) a band of `rimColor` (default `tip`)
//   round it on both faces, from `rimAt` of the way out; `patFace` ("back" | "face") paints a `pat` on that face only.
//   `tip` / `tipAt` as a horn's, along the sheet's length from its root. THE JOIN, `fair` (metres, or { r, sink, reach,
//   color, edge }): near the body each face is the SMOOTH UNION of the face and the body's field (fairAt: marched out
//   along the sheet's normal), a fillet `r` wide grown out of the skin with the regular cross-section kept; the rim is
//   never faired (the fillet fades out within `edge`, default [.2, 1.5] r, of it; `round` > 0 instead turns the march
//   toward the rim's own outward direction within `round` r of it -- fairFin, opt-in: where the sheet dives into the
//   body at a grazing angle it folds); sunk under the skin along the body's
//   normal, and back on the sheet's own face where the skin is met well clear of it; its normal the union's gradient,
//   its paint, wetness and skin the body's by the blend's share (bodymesh.js fairContext gives the field); rows bunched
//   where each column leaves the body. `swell` ([t, len, slope]): thicker toward the root -- a fluke's middle as deep as
//   its stock -- on the smoothed rim distance, met by a smooth max (no crease where stock meets sheet). `bone`, and `rootBone`: the rows' first `rootBlend` (share, default .4) pass from it
//   to `bone` (a fluke riding the tail stock and the fluke).
// STRAND (a horn with `strand: true`): a WHISKER -- `sides` (3), `n` segments, no fair, near mesh only (strandMesh below).
// Both: `n` (rings / rim samples) and a fin's `across` (rows from root to rim) override the counts; `wet`; a `pat` is painted as on any detail.

import { sweepCurve, sweepWeights, sweepColour } from "./sculpt.js";
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a, b, t = 1) => [a[0] + b[0] * t, a[1] + b[1] * t, a[2] + b[2] * t];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = (a) => Math.hypot(a[0], a[1], a[2]);
const nrm = (a) => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const lerp = (a, b, t) => a.map((v, k) => v + (b[k] - v) * t);
const sstep = (e0, e1, x) => { const t = Math.min(1, Math.max(0, (x - e0) / ((e1 - e0) || 1e-9))); return t * t * (3 - 2 * t); };
const lin = (c) => (c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4);
const rgb = (c, d = 0x808080) => { const n = c == null ? d : typeof c === "number" ? c : parseInt(String(c).replace("#", ""), 16);
  return [lin(((n >> 16) & 255) / 255), lin(((n >> 8) & 255) / 255), lin((n & 255) / 255)]; };

// a centripetal Catmull-Rom spline through points (any number of components: the first three its position), sampled
// `per` times a span; ends extended by reflection. Returns the samples and, for each, its span index.
function spline(P, per) {
  const n = P.length, out = [];
  if (n === 1) return [P[0].slice()];
  const ext = (a, b) => a.map((v, k) => 2 * v - b[k]);
  const Q = [ext(P[0], P[1]), ...P, ext(P[n - 1], P[n - 2])];
  for (let i = 1; i < n; i++) {
    const p0 = Q[i - 1], p1 = Q[i], p2 = Q[i + 1], p3 = Q[i + 2];
    const d = (a, b) => Math.max(1e-9, Math.sqrt(len(sub(b, a))));   // (alpha .5 on the positions)
    const t0 = 0, t1 = t0 + d(p0, p1), t2 = t1 + d(p1, p2), t3 = t2 + d(p2, p3);
    for (let s = 0; s < per; s++) {
      const t = t1 + (t2 - t1) * s / per;
      const L = (a, b, ta, tb) => a.map((v, k) => (v * (tb - t) + b[k] * (t - ta)) / (tb - ta));
      const A1 = L(p0, p1, t0, t1), A2 = L(p1, p2, t1, t2), A3 = L(p2, p3, t2, t3);
      const B1 = L(A1, A2, t0, t2), B2 = L(A2, A3, t1, t3);
      out.push(L(B1, B2, t1, t2));
    }
  }
  out.push(P[n - 1].slice());
  return out;
}

// ------------------------------------------------------------------------------------------------------------------
// HORN
export function hornMesh(q, li = 0, bi = () => 0, ctx = null) {
  if (q.strand) return strandMesh(q, li, bi);   // (a whisker: a few sides, a few rings -- below)
  const fair = q.fair && ctx ? (typeof q.fair === "object" ? q.fair : { r: q.fair }) : null;
  const raw = q.pts.map((p) => [p[0], p[1], p[2], p[3], p[4] ?? q.aspect ?? 1]);
  raw[raw.length - 1][3] = 0;   // (the tip: a point)
  const D = spline(raw, 48);
  for (const d of D) d[3] = Math.max(0, d[3]);
  // (its length and its tangents along the dense samples)
  const m = D.length, s = [0], T = [];
  for (let i = 1; i < m; i++) s.push(s[i - 1] + len(sub(D[i], D[i - 1])));
  const L = s[m - 1] || 1e-6;
  for (let i = 0; i < m; i++) T.push(nrm(sub(D[Math.min(m - 1, i + 1)], D[Math.max(0, i - 1)])));
  const rmax = Math.max(...D.map((d) => d[3]), 1e-5);
  // RINGS where the curve turns or the radius bends: a running cost, a ring each time it passes a whole number
  const far = li > 0, aMax = (far ? 14 : 5) * Math.PI / 180, kMax = far ? .12 : .045, lMax = Math.max(L / (far ? 3 : 6), rmax * (far ? 4 : 2));
  const pick = [0];
  let cost = 0;
  for (let i = 1; i < m - 1; i++) {
    const ang = Math.acos(Math.max(-1, Math.min(1, dot(T[i - 1], T[i])))), ds = s[i] - s[i - 1] || 1e-9;
    const sl0 = (D[i][3] - D[i - 1][3]) / ds, sl1 = (D[i + 1][3] - D[i][3]) / (s[i + 1] - s[i] || 1e-9);
    cost += ang / aMax + Math.abs(sl1 - sl0) / kMax + ds / lMax;
    if (cost >= 1) { pick.push(i); cost = 0; }
  }
  // (and two close to the tip, so the point is a smooth cone and not one long facet)
  const near = [.97, .9].map((f) => s.findIndex((v) => v >= L * f));
  for (const j of near) if (j > 0 && j < m - 1 && !pick.some((p) => Math.abs(s[p] - s[j]) < L * .02)) pick.push(j);
  // (FAIRED: rings close together where its surface comes out of the body, so the fillet is drawn by them)
  if (fair) {
    const fk = fair.r, gap = Math.max(ctx.cell * (far ? 1.6 : .7), fk * (far ? .5 : .25));
    let last = -Infinity;
    for (let i = 1; i < m - 1; i++) {
      const f = ctx.dist(D[i][0], D[i][1], D[i][2]);
      if (f > -D[i][3] - fk && f < D[i][3] * Math.max(1, D[i][4]) + 2.5 * fk && s[i] - last >= gap) {
        last = s[i];
        if (!pick.some((p) => Math.abs(s[p] - s[i]) < gap * .5)) pick.push(i);
      }
    }
  }
  pick.sort((a, b) => a - b);
  // (the frame along it: `up` square to the first tangent, carried without twisting -- double reflection)
  let up0 = q.up ?? [0, 1, 0];
  if (Math.abs(dot(nrm(up0), T[0])) > .98) up0 = Math.abs(T[0][1]) < .9 ? [0, 1, 0] : [1, 0, 0];
  const U = [nrm(sub(up0, T[0].map((v) => v * dot(up0, T[0]))))];
  for (let i = 1; i < m; i++) {
    const v1 = sub(D[i], D[i - 1]), c1 = dot(v1, v1) || 1e-12;
    const rL = sub(U[i - 1], v1.map((v) => v * 2 * dot(v1, U[i - 1]) / c1)), tL = sub(T[i - 1], v1.map((v) => v * 2 * dot(v1, T[i - 1]) / c1));
    const v2 = sub(T[i], tL), c2 = dot(v2, v2) || 1e-12;
    U.push(nrm(sub(rL, v2.map((v) => v * 2 * dot(v2, rL) / c2))));
  }
  const sides = Math.max(4, Math.round((q.sides ?? 12) / (far ? 2 : 1))), flat = Math.min(1, Math.max(0, q.flat ?? 0)), keel = q.keel ?? 0;
  const tw = (q.twist ?? 0) * Math.PI / 180;
  // the cross-section: [across, up] at angle a, unit radius (an ellipse of its aspect, flattened below, keeled above)
  const sec = (a, asp) => {
    const c = Math.cos(a), sn = Math.sin(a);
    let y = sn * asp;
    if (sn < 0) y *= 1 - flat * .96;
    if (keel) { const d = Math.atan2(Math.sin(a - Math.PI / 2), Math.cos(a - Math.PI / 2)); y += keel * asp * Math.exp(-((d / .45) ** 2)); }
    return [c, y];
  };
  const ringAt = (i) => {
    const d = D[i], t = T[i], u = U[i], w = crs(t, u), tt = tw * s[i] / L, out = [];
    for (let k = 0; k < sides; k++) {
      const a = 2 * Math.PI * k / sides + tt, [x, y] = sec(a, d[4]);
      out.push([0, 1, 2].map((j) => d[j] + (w[j] * x + u[j] * y) * d[3]));
    }
    return out;
  };
  const R = pick.map(ringAt), nr = R.length, tipP = D[m - 1].slice(0, 3);
  // (FAIRED: each ring's vertex moved out along its spoke to the smooth union of the horn and the body -- a fillet
  //  that grows out of the skin, its paint and skin the body's where it is the body's)
  //  (no sink: a horn's fillet is never drawn under the skin; and each ring's reach smoothed round it, so the spokes
  //  that just catch the body and those that just miss it do not ruffle the ring)
  const FW = fair ? R.map((ring, i) => {
    const c = D[pick[i]], sp = ring.map((p) => { const d = sub(p, c), h = len(d); return [h > 1e-9 ? d.map((v) => v / h) : U[pick[i]], h]; });
    // (a ring whose centre is deeper in the body than its own radius is under the skin already: left alone -- its spokes
    //  would reach the skin beyond it and draw slivers of horn there)
    const deep = ctx.dist(c[0], c[1], c[2]) < -Math.max(...sp.map(([, h]) => h)) * .9;
    let fw = sp.map(([n, h]) => (deep ? { t: h, w: 0, h } : { ...fairAt(c, n, h, ctx, { ...fair, sink: 0 }, far), h }));
    for (let it = 0; it < 3; it++) fw = fw.map((f, k) => {
      const a = fw[(k + sides - 1) % sides], b = fw[(k + 1) % sides];
      const ext = (x) => x.t - x.h, e = (ext(a) + 2 * ext(f) + ext(b)) / 4, w = (a.w + 2 * f.w + b.w) / 4;
      return { ...f, t: f.h + Math.max(0, e), w, a: f.a ?? a.a ?? b.a };
    });
    fw.forEach((f, k) => { R[i][k] = add(c, sp[k][0], f.t); });
    return fw;
  }) : null;
  // (its PAINT: the body's below one line round it, the horn's above -- where each spoke's share of the body falls
  //  through the half of `skin`, that line smoothed round the ring; painted vertex by vertex from the share alone, the
  //  rings that just catch the skin and those that just miss it gave a ragged collar of blotches)
  const SB = fair && fair.color !== false ? (() => {
    const th = (.02 + (fair.skin ?? .3)) / 2, out = [];
    for (let k = 0; k < sides; k++) {
      let b = s[pick[0]] - 1e-6;
      for (let i = 0; i < nr; i++) {
        const w = FW[i][k].w;
        if (w < th) { if (i > 0) { const w0 = FW[i - 1][k].w; b = s[pick[i - 1]] + (s[pick[i]] - s[pick[i - 1]]) * (w0 - th) / ((w0 - w) || 1e-9); } break; }
        b = s[pick[i]];
      }
      out.push(b);
    }
    // (and never below where that spoke comes out of the skin, by a little more than the line's own blend: the horn's
    //  edge against the body's facets is then skin against skin, not a sawtooth of horn on it)
    const m = fair.r * .55, out2 = out.map((b, k) => {
      let e = s[pick[0]];
      for (let i = 0; i < nr; i++) { const p = R[i][k]; if (ctx.dist(p[0], p[1], p[2]) < 0) e = s[pick[Math.min(nr - 1, i + 1)]]; else break; }
      return e + m;
    });
    let sb = out.map((b, k) => Math.max(b, out2[k]));
    for (let it = 0; it < 4; it++) sb = sb.map((v, k) => Math.max(out2[k], (sb[(k + sides - 1) % sides] + 2 * v + sb[(k + 1) % sides]) / 4));
    return sb;
  })() : null;
  const bw = fair ? fair.r * .3 : 0, ringA = FW ? FW.map((ring) => ring.find((f) => f.a)?.a ?? null) : null;
  const P = [], N = [], C = [], SI = [], SW = [], Tr = [];
  const c0 = rgb(q.color), c1 = q.tip != null ? rgb(q.tip) : null, at = q.tipAt ?? .5;
  const colAt = (f) => (c1 ? c0.map((v, k) => v + (c1[k] - v) * sstep(at, 1, f)) : c0);
  const b1 = bi(q.bone ?? "body"), b2 = q.bone2 ? bi(q.bone2) : b1, [bl0, bl1] = q.blend ?? [0, 1];
  const skin = (f) => { const w2 = b2 === b1 ? 0 : sstep(bl0, bl1, f); SI.push(b1, b2, 0, 0); SW.push(1 - w2, w2, 0, 0); };
  // (each ring's vertex normal: the surface's, from its neighbours round the ring and along it -- the tip the next "ring")
  const ringOf = (i) => (i < 0 ? R[0] : i >= nr ? Array(sides).fill(tipP) : R[i]);
  for (let i = 0; i < nr; i++) {
    const f = s[pick[i]] / L, c = colAt(f), ctr = D[pick[i]];
    for (let k = 0; k < sides; k++) {
      const p = R[i][k], around = sub(R[i][(k + 1) % sides], R[i][(k + sides - 1) % sides]);
      const along = sub(ringOf(i + 1)[k], ringOf(i - 1)[k]);
      let n = nrm(crs(around, along));
      if (dot(n, sub(p, ctr)) < 0) n = n.map((v) => -v);
      const fw = FW?.[i][k];
      if (fw && fw.w > 0) {   // (the fillet: the body's normal, paint and skin as it merges into it)
        const w = fw.w, a = fw.a, b = sstep(0, .2, w);
        n = nrm(n.map((v, j) => v + (nrm(add(n, sub(a.n, n), w))[j] - v) * b));
        const cw = SB ? 1 - sstep(SB[k] - bw, SB[k] + bw, s[pick[i]]) : 0;   // (the skin creeping up the fillet -- a gum, a lip sheath: below the line SB)
        P.push(...p); N.push(...n); C.push(...c.map((v, j) => v + (a.c[j] - v) * cw));
        const ws = sstep(.05, .9, w), wt = new Map();
        const w2 = b2 === b1 ? 0 : sstep(bl0, bl1, f);
        wt.set(b1, (1 - w2) * (1 - ws)); wt.set(b2, (wt.get(b2) ?? 0) + w2 * (1 - ws));
        for (let j = 0; j < 4; j++) if (a.sw[j] > 0) wt.set(a.si[j], (wt.get(a.si[j]) ?? 0) + a.sw[j] * ws);
        const top = [...wt].sort((x, y) => y[1] - x[1]).slice(0, 4), tot = top.reduce((t, e) => t + e[1], 0) || 1;
        for (let j = 0; j < 4; j++) { SI.push(top[j]?.[0] ?? 0); SW.push((top[j]?.[1] ?? 0) / tot); }
        continue;
      }
      const cw = SB && ringA[i] ? 1 - sstep(SB[k] - bw, SB[k] + bw, s[pick[i]]) : 0;   // (below the line though clear of the body: its paint all the same)
      P.push(...p); N.push(...n); C.push(...(cw > 0 ? c.map((v, j) => v + (ringA[i].c[j] - v) * cw) : c)); skin(f);
    }
  }
  for (let i = 0; i + 1 < nr; i++) for (let k = 0; k < sides; k++) {
    const a = i * sides + k, b = i * sides + (k + 1) % sides, c = a + sides, d = b + sides;
    Tr.push(a, c, b, b, c, d);
  }
  // THE TIP: one apex a side (the same point), each with the normal of the cone face it closes
  const t0 = P.length / 3, cT = colAt(1), last = (nr - 1) * sides;
  for (let k = 0; k < sides; k++) {
    const n0 = N.slice(3 * (last + k), 3 * (last + k) + 3), n1 = N.slice(3 * (last + (k + 1) % sides), 3 * (last + (k + 1) % sides) + 3);
    P.push(...tipP); N.push(...nrm(add(n0, n1))); C.push(...cT); skin(1);
    Tr.push(last + k, t0 + k, last + (k + 1) % sides);
  }
  // THE ROOT: closed (it is inside the body), a centre point facing back along it
  const r0 = P.length / 3, back = T[0].map((v) => -v);
  P.push(...D[0].slice(0, 3)); N.push(...back); C.push(...colAt(0)); skin(0);
  for (let k = 0; k < sides; k++) Tr.push(k, (k + 1) % sides, r0);
  return { P, N, T: orient(P, N, Tr), C, SI, SW };
}

// ------------------------------------------------------------------------------------------------------------------
// SWEEP (2026-11-08): the THIN END of a sweep (sculpt.js sweepCurve: a neck or a tail along a chain of bones), drawn as
// it is -- what the grid cannot resolve: a tail a cell or two thick is a staircase of facets in the field, and its
// point a blob. bodyspec.js cuts a sweep where it gets thinner than CONVERT.sweepThin cells: the field keeps the rest
// (shrunk a little under the overlap, so this is the surface seen there), this draws from `from` (metres of arc,
// inside the field's part) to the end -- the very same centreline, radius and cross-section, exact rings of `sides`
// (by its girth in cells, default 6 to 16), spaced by how much the curve turns and the radius bends; its end a POINT
// (`end: "point"`: an apex) or ROUND (a hemisphere); its first ring closed (it is buried in the field's part). Its
// skin the sweep's own along the chain; its paint the sweep's colour and bands, countershaded and mottled as the
// body's vertices are (ctx.paint: bodymesh.js fairContext), so the seam does not show.
export function sweepMesh(q, li = 0, bi = () => 0, ctx = null) {
  const C = sweepCurve(q), { X, R, A, S, T, U, m, L } = C, far = li > 0, s0 = Math.max(0, Math.min(L, q.from ?? 0));
  const cell = ctx?.cell ?? Math.max(1e-3, Math.max(...R) / 3);
  // (the samples it draws: from s0 on; a ring where the cost of turning, bending and running on passes one)
  let i0 = 0;
  while (i0 < m - 1 && S[i0 + 1] <= s0) i0++;
  const at = (s) => { let i = Math.max(0, i0 - 1); while (i < m - 2 && S[i + 1] < s) i++; const t = Math.max(0, Math.min(1, (s - S[i]) / ((S[i + 1] - S[i]) || 1e-12)));
    const l = (a, b) => a + (b - a) * t, nv = (a, b) => nrm(lerp(a, b, t));
    return { x: lerp(X[i], X[i + 1], t), r: l(R[i], R[i + 1]), a: l(A[i], A[i + 1]), s, t: nv(T[i], T[i + 1]), u: nv(U[i], U[i + 1]) }; };
  const st = [at(s0)];
  const rmax = Math.max(...R.slice(i0)), aMax = (far ? 16 : 6) * Math.PI / 180, kMax = far ? .12 : .05, lMax = Math.max(rmax * (far ? 4 : 1.5), cell * (far ? 4 : 1.5));
  let cost = 0;
  for (let i = i0 + 1; i < m - 1; i++) {
    if (S[i] <= s0 + 1e-9) continue;
    const ang = Math.acos(Math.max(-1, Math.min(1, dot(T[i - 1], T[i])))), ds = S[i] - S[i - 1] || 1e-9;
    const sl0 = (R[i] - R[i - 1]) / ds, sl1 = (R[i + 1] - R[i]) / (S[i + 1] - S[i] || 1e-9);
    cost += ang / aMax + Math.abs(sl1 - sl0) / kMax + ds / lMax;
    if (cost >= 1) { st.push({ x: X[i], r: R[i], a: A[i], s: S[i], t: T[i], u: U[i] }); cost = 0; }
  }
  const point = q.end === "point", rEnd = R[m - 1];
  if (point) {   // (rings closing in on the point, so it is a smooth cone and not one long facet)
    for (const f of [.9, .97]) { const s = s0 + (L - s0) * f; if (s > st[st.length - 1].s + (L - s0) * .02) st.push(at(s)); }
    st.sort((a, b) => a.s - b.s);
  } else st.push({ x: X[m - 1], r: R[m - 1], a: A[m - 1], s: L, t: T[m - 1], u: U[m - 1] });
  // ROUND: a hemisphere past the last ring, its rings at even angles
  const cap = [];
  if (!point && rEnd > 1e-6) for (const ang of far ? [50, 75] : [30, 50, 68, 82]) {
    const e = st[st.length - 1], c = Math.cos(ang * Math.PI / 180), sn = Math.sin(ang * Math.PI / 180);
    cap.push({ ...e, x: add(e.x, e.t, rEnd * sn), r: rEnd * c, s: L });
  }
  const sides = Math.max(far ? 5 : 6, Math.min(far ? 8 : 16, Math.round((q.sides ?? 2 * Math.PI * rmax / (cell * .9)) / (far ? 2 : 1))));
  const rings = [...st, ...cap], nr = rings.length;
  const P = [], N = [], Cc = [], SI = [], SW = [], Tr = [];
  const chain = q.chain ?? [q.bone ?? "body"], cix = chain.map((b) => bi(b)), wts = new Float64Array(chain.length);
  const base = rgb(q.color), bands = (q.bands ?? []).map(([a, b, c]) => [a, b, rgb(c)]), e = q.bandEdge ?? Math.max(1e-4, (q.kc ?? 0) || R[0] * .15), col = [0, 0, 0];
  const skin = (s) => {
    if (q.knots) sweepWeights(q.knots, s, wts); else wts[0] = 1;
    const w = new Map();
    cix.forEach((b, j) => { if (wts[j] > 1e-4) w.set(b, (w.get(b) ?? 0) + wts[j]); });
    const top = [...w].sort((x, y) => y[1] - x[1]).slice(0, 4), tot = top.reduce((t, x) => t + x[1], 0) || 1;
    for (let j = 0; j < 4; j++) { SI.push(top[j]?.[0] ?? cix[0]); SW.push((top[j]?.[1] ?? 0) / tot); }
  };
  const paint = (x, s) => { sweepColour(bands, s, L, e, base, col); return ctx?.paint ? ctx.paint(x[0], x[1], x[2], col) : col.slice(); };
  for (const g of rings) {
    const w = crs(g.t, g.u);
    for (let k = 0; k < sides; k++) {
      const a = 2 * Math.PI * k / sides, x = add(g.x, add(w.map((v) => v * Math.cos(a)), g.u, Math.sin(a) * g.a), g.r);
      P.push(...x); Cc.push(...paint(x, g.s)); skin(g.s);
    }
  }
  // (the end: the point, or the cap's last pole)
  const last = rings[nr - 1], tipP = point ? X[m - 1].slice() : add(X[m - 1], T[m - 1], rEnd);
  const tipI = P.length / 3; P.push(...tipP); Cc.push(...paint(tipP, L)); skin(L);
  const rootI = P.length / 3; P.push(...rings[0].x); Cc.push(...paint(rings[0].x, rings[0].s)); skin(rings[0].s);
  for (let i = 0; i + 1 < nr; i++) for (let k = 0; k < sides; k++) {
    const a = i * sides + k, b = i * sides + (k + 1) % sides, c = a + sides, d = b + sides;
    Tr.push(a, c, b, b, c, d);
  }
  const lr = (nr - 1) * sides;
  for (let k = 0; k < sides; k++) { Tr.push(lr + k, tipI, lr + (k + 1) % sides); Tr.push(k, (k + 1) % sides, rootI); }
  // (normals: the surface's, from each vertex's neighbours round its ring and along it; the point's the cone's axis
  //  bent to its faces, the root's back along the curve)
  const V = (j) => P.slice(3 * j, 3 * j + 3), ringV = (i, k) => (i < 0 ? V(k) : i >= nr ? tipP : V(i * sides + k));
  for (let i = 0; i < nr; i++) for (let k = 0; k < sides; k++) {
    const p = V(i * sides + k), around = sub(V(i * sides + (k + 1) % sides), V(i * sides + (k + sides - 1) % sides)), along = sub(ringV(i + 1, k), ringV(i - 1, k));
    let n = nrm(crs(around, along));
    if (dot(n, sub(p, rings[i].x)) < 0) n = n.map((v) => -v);
    N.push(...n);
  }
  N.push(...last.t); N.push(...rings[0].t.map((v) => -v));
  return { P, N, T: orient(P, N, Tr), C: Cc, SI, SW, W: q.wet ? new Float32Array(P.length / 3).fill(q.wet) : null };
}

// ------------------------------------------------------------------------------------------------------------------
// STRAND (2026-11-08): a WHISKER -- a horn with `strand: true` (bodyspec.js whiskerStrands makes them from one
// `whiskers` shape). A hair a fraction of a millimetre to a few millimetres thick wants none of a horn's care -- no
// fair, no keel, rings by the curve -- and a face of thirty of them must cost a few hundred triangles: `sides` round
// (default 3), `n` segments past the skin (default 3, evenly along it), its first point buried in the head and the
// second where it leaves the skin (the first span is one segment, under the skin), the last the TIP: an exact apex.
// Colour `color` fading to `tip` from `tipAt`; skinned to `bone` alone. Not drawn on the far mesh (li > 0) unless `far`:
// past a few metres it is under a tenth of a pixel across, and a line that thin only sparkles.
function strandMesh(q, li = 0, bi = () => 0) {
  const P = [], N = [], C = [], SI = [], SW = [], Tr = [];
  if (li > 0 && !q.far) return { P, N, T: Tr, C, SI, SW };
  const raw = q.pts.map((p) => [p[0], p[1], p[2], p[3]]);
  raw[raw.length - 1][3] = 0;
  const per = 12, D = spline(raw, per), m = D.length, s = [0];
  for (let i = 1; i < m; i++) s.push(s[i - 1] + len(sub(D[i], D[i - 1])));
  const L = s[m - 1] || 1e-6, skin = s[Math.min(m - 1, per)];
  const n = Math.max(1, q.n ?? 3), sides = Math.max(3, q.sides ?? 3);
  const at = [0, skin];
  for (let k = 1; k < n; k++) at.push(skin + (L - skin) * k / n);
  // (a station at arc length a: its point, radius, tangent)
  const station = (a) => {
    let i = 0;
    while (i < m - 2 && s[i + 1] < a) i++;
    const f = Math.min(1, Math.max(0, (a - s[i]) / ((s[i + 1] - s[i]) || 1e-9))), p = lerp(D[i], D[i + 1], f);
    return { p: p.slice(0, 3), r: Math.max(0, p[3]), t: nrm(sub(D[i + 1], D[i])), a };
  };
  const St = at.map(station), whole = nrm(sub(D[m - 1], D[0]));
  const ref = Math.abs(whole[1]) < .9 ? [0, 1, 0] : [1, 0, 0], u0 = nrm(crs(whole, ref));
  const c0 = rgb(q.color), c1 = q.tip != null ? rgb(q.tip) : null, ta = q.tipAt ?? .5;
  const colAt = (f) => (c1 ? c0.map((v, k) => v + (c1[k] - v) * sstep(ta, 1, f)) : c0);
  const b = bi(q.bone ?? "body"), sk = () => { SI.push(b, 0, 0, 0); SW.push(1, 0, 0, 0); };
  for (let i = 0; i < St.length; i++) {
    const { p, r, t, a } = St[i], u = nrm(sub(u0, t.map((v) => v * dot(u0, t)))), w = crs(t, u), c = colAt(a / L);
    const slope = i + 1 < St.length ? (St[i].r - St[i + 1].r) / ((St[i + 1].a - a) || 1e-9) : r / ((L - a) || 1e-9);
    for (let k = 0; k < sides; k++) {
      const ang = 2 * Math.PI * k / sides, e = [0, 1, 2].map((j) => u[j] * Math.cos(ang) + w[j] * Math.sin(ang));
      P.push(...add(p, e, r)); N.push(...nrm(add(e, t, slope))); C.push(...c); sk();
    }
  }
  const nr = St.length;
  for (let i = 0; i + 1 < nr; i++) for (let k = 0; k < sides; k++) {
    const a = i * sides + k, b2 = i * sides + (k + 1) % sides, c = a + sides, d = b2 + sides;
    Tr.push(a, b2, c, b2, d, c);
  }
  // THE TIP: one apex a side, each with the normal of the face it closes
  const last = (nr - 1) * sides, t0 = P.length / 3, tipP = D[m - 1].slice(0, 3), cT = colAt(1);
  for (let k = 0; k < sides; k++) {
    const n0 = N.slice(3 * (last + k), 3 * (last + k) + 3), n1 = N.slice(3 * (last + (k + 1) % sides), 3 * (last + (k + 1) % sides) + 3);
    P.push(...tipP); N.push(...nrm(add(n0, n1))); C.push(...cT); sk();
    Tr.push(last + k, last + (k + 1) % sides, t0 + k);
  }
  return { P, N, T: orient(P, N, Tr), C, SI, SW };
}

// every triangle wound so it faces its normals (the frames may come out either hand, a mirror flips them)
function orient(P, N, T) {
  for (let f = 0; f < T.length; f += 3) {
    const a = T[f], b = T[f + 1], c = T[f + 2];
    const e1 = [P[3 * b] - P[3 * a], P[3 * b + 1] - P[3 * a + 1], P[3 * b + 2] - P[3 * a + 2]], e2 = [P[3 * c] - P[3 * a], P[3 * c + 1] - P[3 * a + 1], P[3 * c + 2] - P[3 * a + 2]];
    const fn = crs(e1, e2), nn = [N[3 * a] + N[3 * b] + N[3 * c], N[3 * a + 1] + N[3 * b + 1] + N[3 * c + 1], N[3 * a + 2] + N[3 * b + 2] + N[3 * c + 2]];
    if (dot(fn, nn) < 0) { T[f + 1] = c; T[f + 2] = b; }
  }
  return T;
}

// ------------------------------------------------------------------------------------------------------------------
// FIN
// a polyline resampled: `n` points by arc length over spans between kept corners (their indices into pts)
function resample(pts, n, corners) {
  const cs = [...new Set([0, pts.length - 1, ...corners.filter((c) => c > 0 && c < pts.length - 1)])].sort((a, b) => a - b);
  const spans = [];
  for (let j = 0; j + 1 < cs.length; j++) {
    const seg = pts.slice(cs[j], cs[j + 1] + 1), dense = seg.length > 2 ? spline(seg, 24) : spline(seg, 24);
    const acc = [0];
    for (let i = 1; i < dense.length; i++) acc.push(acc[i - 1] + len(sub(dense[i], dense[i - 1])));
    spans.push({ dense, acc, L: acc[acc.length - 1] });
  }
  const Ltot = spans.reduce((a, b) => a + b.L, 0) || 1e-9, out = [];
  spans.forEach((sp, j) => {
    const k = Math.max(2, Math.round(n * sp.L / Ltot));
    for (let i = 0; i < k; i++) {
      const target = sp.L * i / k;
      let lo = 0;
      while (lo < sp.acc.length - 2 && sp.acc[lo + 1] < target) lo++;
      const t = (target - sp.acc[lo]) / ((sp.acc[lo + 1] - sp.acc[lo]) || 1e-9);
      out.push(lerp(sp.dense[lo], sp.dense[lo + 1], t));
    }
    if (j === spans.length - 1) out.push(sp.dense[sp.dense.length - 1].slice());
  });
  return out;
}
// the distance from p to the polyline E (closed: false), each segment's distance times its bluntness (a blunt rim thickens faster)
// (the rim's running length, each piece weighted 1 / (its distance from the root + c): see finMesh `rootBy`)
function rootWeights(E, root0, c) {
  const rE = root0.map((p) => [p[0], p[1], p[2], 1]), acc = [0];
  for (let i = 1; i < E.length; i++) {
    const a = E[i - 1].slice(0, 3), b = E[i].slice(0, 3), m = lerp(a, b, .5);
    acc.push(acc[i - 1] + len(sub(b, a)) / (rimDist(m, rE) + Math.max(c, 1e-6)));
  }
  return acc;
}

function rimDist(p, E) {
  let best = Infinity;
  for (let i = 0; i + 1 < E.length; i++) {
    const a = E[i], b = E[i + 1], ab = sub(b, a), l2 = dot(ab, ab) || 1e-12, t = Math.max(0, Math.min(1, dot(sub(p, a), ab) / l2));
    const d = len(sub(p, add(a, ab, t))) * ((a[3] ?? 1) + ((b[3] ?? 1) - (a[3] ?? 1)) * t);
    if (d < best) best = d;
  }
  return best;
}

// A HARMONIC GRID (a fin's `grid: "flow"`): the inside of the grid G ((NU+1) x (nv+1), rows at shares vs) solved for
// instead of relaxed a little -- each coordinate harmonic over the parameter rectangle (rim, root and the root's end
// columns held), its two directions weighed by the sheet's own proportions (the rim's length against the columns' mean
// length, `flow` scaling the one by the other). Straight columns fanned out of a short root (a fluke's across the stock)
// run on top of one another where the outline sweeps round out of their sight (a fluke's swept tip: a bundle of
// slivers drawn as a line down the blade); harmonic, they curve with the outline -- the rows are the outline smoothed
// more and more toward the root, the columns the lines across them.
function harmonicGrid(G, vs, flow = 1) {
  const NI = G.length - 1, NJ = vs.length - 1, n = (NI - 1) * (NJ - 1);
  if (NI < 2 || NJ < 2) return G;
  let Lr = 0, Lc = 0;
  for (let i = 0; i < NI; i++) Lr += len(sub(G[i + 1][NJ], G[i][NJ]));
  for (let i = 0; i <= NI; i++) for (let j = 0; j < NJ; j++) Lc += len(sub(G[i][j + 1], G[i][j])) / (NI + 1);
  const al = NI * NI / Math.max(1e-12, Lr * Lr) * flow, be = 1 / Math.max(1e-12, Lc * Lc);
  // (symmetric weights: an i-edge al x (the row's share of v), a j-edge be / its length in v)
  const wi = (j) => al * (vs[j + 1] - vs[j - 1]) / 2, wj = (j) => be / (vs[j + 1] - vs[j]);
  const id = (i, j) => (i - 1) * (NJ - 1) + (j - 1), free = (i, j) => i > 0 && i < NI && j > 0 && j < NJ;
  const diag = new Float64Array(n);
  for (let i = 1; i < NI; i++) for (let j = 1; j < NJ; j++) diag[id(i, j)] = 2 * wi(j) + wj(j - 1) + wj(j);
  const mul = (x, out) => {
    for (let i = 1; i < NI; i++) for (let j = 1; j < NJ; j++) {
      const k = id(i, j);
      let s = diag[k] * x[k];
      if (i > 1) s -= wi(j) * x[id(i - 1, j)];
      if (i < NI - 1) s -= wi(j) * x[id(i + 1, j)];
      if (j > 1) s -= wj(j - 1) * x[id(i, j - 1)];
      if (j < NJ - 1) s -= wj(j) * x[id(i, j + 1)];
      out[k] = s;
    }
  };
  const out = G.map((col) => col.map((p) => p.slice()));
  for (let c = 0; c < 3; c++) {
    const b = new Float64Array(n), x = new Float64Array(n);
    for (let i = 1; i < NI; i++) for (let j = 1; j < NJ; j++) {
      const k = id(i, j);
      x[k] = G[i][j][c];
      for (const [ii, jj, w] of [[i - 1, j, wi(j)], [i + 1, j, wi(j)], [i, j - 1, wj(j - 1)], [i, j + 1, wj(j)]]) if (!free(ii, jj)) b[k] += w * G[ii][jj][c];
    }
    // (conjugate gradients, Jacobi-preconditioned, from the straight columns)
    const r = new Float64Array(n), z = new Float64Array(n), p = new Float64Array(n), Ap = new Float64Array(n);
    mul(x, Ap);
    let rz = 0, b2 = 0;
    for (let k = 0; k < n; k++) { r[k] = b[k] - Ap[k]; z[k] = r[k] / diag[k]; p[k] = z[k]; rz += r[k] * z[k]; b2 += b[k] * b[k]; }
    for (let it = 0; it < 4 * n && rz > 1e-24 * b2; it++) {
      mul(p, Ap);
      let pAp = 0;
      for (let k = 0; k < n; k++) pAp += p[k] * Ap[k];
      if (!(pAp > 0)) break;
      const a = rz / pAp;
      let rz1 = 0;
      for (let k = 0; k < n; k++) { x[k] += a * p[k]; r[k] -= a * Ap[k]; z[k] = r[k] / diag[k]; rz1 += r[k] * z[k]; }
      for (let k = 0; k < n; k++) p[k] = z[k] + (rz1 / rz) * p[k];
      rz = rz1;
    }
    if (!x.every(Number.isFinite)) return G;
    for (let i = 1; i < NI; i++) for (let j = 1; j < NJ; j++) out[i][j][c] = x[id(i, j)];
  }
  return out;
}

// A SMOOTH RIM DISTANCE over the sheet's grid G ((NU+1) x (nv+1): columns root -> rim, the first and last columns the
// root's ends, the last row the rim). The distance to the rim itself has a crease along the sheet's medial axis (two
// rim parts equally near): a thickness made from it is a ridge down the middle of every long blade -- a fluke, a
// flipper. Instead the POISSON solution u (-lap u = 1, u = 0 on the rim, the root free: it is the sheet's symmetry line
// into the body), smooth everywhere inside, linear at the rim. a = sqrt(|grad u|^2 + 2u) is the local half-width
// (exactly, across a strip), tau = u / a^2 runs from 0 at the rim to 1/2 on the medial axis, and the distance is
// a (tau + tau^2): the true distance near the rim (slope 1), flattening smoothly to 3/4 of it on the axis. A P1 finite
// element solve (cotangent weights, Jacobi-preconditioned conjugate gradients); `bl` (the rim's bluntness, per column)
// is carried in harmonically the same way. Returns { D, B } (grids like G) or null if the solve failed.
function smoothRimDist(G, bl) {
  const NI = G.length - 1, NJ = G[0].length - 1, nn = (NI + 1) * (NJ + 1), id = (i, j) => i * (NJ + 1) + j;
  const X = new Float64Array(3 * nn);
  G.forEach((col, i) => col.forEach((p, j) => { const o = 3 * id(i, j); X[o] = p[0]; X[o + 1] = p[1]; X[o + 2] = p[2]; }));
  const fixed = new Uint8Array(nn);
  for (let i = 0; i <= NI; i++) fixed[id(i, NJ)] = 1;
  for (let j = 0; j <= NJ; j++) { fixed[id(0, j)] = 1; fixed[id(NI, j)] = 1; }
  // (the triangles, as drawn; the degenerate ones -- the root ends' columns are points -- left out)
  const tri = [];
  for (let i = 0; i < NI; i++) for (let j = 0; j < NJ; j++) { const a = id(i, j), b = id(i + 1, j), c = id(i, j + 1), d = id(i + 1, j + 1); tri.push([a, b, c], [b, d, c]); }
  const nb = Array.from({ length: nn }, () => new Map()), diag = new Float64Array(nn), mass = new Float64Array(nn), TG = [];
  const v = (k) => [X[3 * k], X[3 * k + 1], X[3 * k + 2]];
  let Amax = 0;
  for (const t of tri) { const A2 = len(crs(sub(v(t[1]), v(t[0])), sub(v(t[2]), v(t[0])))); if (A2 > Amax) Amax = A2; }
  for (const t of tri) {
    const p = t.map(v), n = crs(sub(p[1], p[0]), sub(p[2], p[0])), A2 = len(n);
    if (A2 < Amax * 1e-7) continue;
    for (let k = 0; k < 3; k++) {   // (the cotangent at corner k weighs the edge opposite it)
      const a = t[(k + 1) % 3], b = t[(k + 2) % 3], e1 = sub(p[(k + 1) % 3], p[k]), e2 = sub(p[(k + 2) % 3], p[k]);
      const w = .5 * dot(e1, e2) / A2;
      nb[a].set(b, (nb[a].get(b) ?? 0) - w); nb[b].set(a, (nb[b].get(a) ?? 0) - w); diag[a] += w; diag[b] += w;
      mass[t[k]] += A2 / 6;
    }
    TG.push({ t, n: nrm(n), A2, p });
  }
  // (K x = rhs over the free nodes, the fixed ones held at x0)
  const solve = (rhs, x0) => {
    const x = Float64Array.from(x0), r = new Float64Array(nn), z = new Float64Array(nn), pp = new Float64Array(nn), Ap = new Float64Array(nn);
    const mul = (y, out) => { for (let k = 0; k < nn; k++) { if (fixed[k]) { out[k] = 0; continue; } let s = diag[k] * y[k]; for (const [m, w] of nb[k]) if (!fixed[m]) s += w * y[m]; out[k] = s; } };
    // (the fixed values moved to the right-hand side)
    for (let k = 0; k < nn; k++) { if (fixed[k]) { r[k] = 0; continue; } let s = rhs[k] - diag[k] * x[k]; for (const [m, w] of nb[k]) s -= w * x[m]; r[k] = s; }
    let rz = 0;
    for (let k = 0; k < nn; k++) { z[k] = fixed[k] || diag[k] <= 0 ? 0 : r[k] / diag[k]; pp[k] = z[k]; rz += r[k] * z[k]; }
    const r0 = Math.sqrt(r.reduce((s, x) => s + x * x, 0)) || 1;
    for (let it = 0; it < 4 * nn && rz > 0; it++) {
      mul(pp, Ap);
      let pAp = 0;
      for (let k = 0; k < nn; k++) pAp += pp[k] * Ap[k];
      if (!(pAp > 0)) break;
      const al = rz / pAp;
      let rn = 0, rz1 = 0;
      for (let k = 0; k < nn; k++) { x[k] += al * pp[k]; r[k] -= al * Ap[k]; rn += r[k] * r[k]; }
      if (Math.sqrt(rn) < 1e-10 * r0) break;
      for (let k = 0; k < nn; k++) { z[k] = fixed[k] || diag[k] <= 0 ? 0 : r[k] / diag[k]; rz1 += r[k] * z[k]; }
      for (let k = 0; k < nn; k++) pp[k] = z[k] + (rz1 / rz) * pp[k];
      rz = rz1;
    }
    return x;
  };
  const u = solve(mass, new Float64Array(nn));
  const b0 = new Float64Array(nn);
  for (let i = 0; i <= NI; i++) for (let j = 0; j <= NJ; j++) b0[id(i, j)] = bl[i];
  const bb = solve(new Float64Array(nn), b0);
  // (grad u per triangle, area-weighted onto the vertices)
  const gr = new Float64Array(3 * nn), gw = new Float64Array(nn);
  for (const { t, n, A2, p } of TG) {
    let g = [0, 0, 0];
    for (let k = 0; k < 3; k++) g = add(g, crs(n, sub(p[(k + 2) % 3], p[(k + 1) % 3])), u[t[k]] / A2);
    for (const k of t) { gr[3 * k] += g[0] * A2; gr[3 * k + 1] += g[1] * A2; gr[3 * k + 2] += g[2] * A2; gw[k] += A2; }
  }
  const D = G.map((col, i) => col.map((_, j) => {
    const k = id(i, j), uu = Math.max(0, u[k]);
    if (!(uu > 0) || !(gw[k] > 0)) return 0;
    const g2 = (gr[3 * k] ** 2 + gr[3 * k + 1] ** 2 + gr[3 * k + 2] ** 2) / gw[k] ** 2, a2 = g2 + 2 * uu, a = Math.sqrt(a2), tau = uu / a2;
    return a * (tau + tau * tau);
  }));
  if (D.some((col) => col.some((x) => !Number.isFinite(x)))) return null;
  return { D, B: G.map((col, i) => col.map((_, j) => bb[id(i, j)])) };
}

// (the smooth rim distance solved on the sheet's EVEN grid -- rows vs -- and carried to each column's own rows V (the
//  faired sheet's rows bunched where it leaves the body, a different place on every column: solved on that grid its
//  slivers threw spikes into the gradient and so the thickness) along the column by cubic Hermite in v)
function resampleSD(SD, vs, V) {
  if (!SD) return null;
  const n = vs.length - 1;
  const along = (f, col) => {
    const sl = vs.map((_, j) => (j === 0 ? (f[1] - f[0]) / (vs[1] - vs[0]) : j === n ? (f[n] - f[n - 1]) / (vs[n] - vs[n - 1])
      : ((f[j + 1] - f[j]) / (vs[j + 1] - vs[j]) * (vs[j] - vs[j - 1]) + (f[j] - f[j - 1]) / (vs[j] - vs[j - 1]) * (vs[j + 1] - vs[j])) / (vs[j + 1] - vs[j - 1])));
    return col.map((v) => {
      let j = 0;
      while (j < n - 1 && vs[j + 1] < v) j++;
      const h = vs[j + 1] - vs[j], t = Math.min(1, Math.max(0, (v - vs[j]) / h)), t2 = t * t, t3 = t2 * t;
      return Math.max(0, (2 * t3 - 3 * t2 + 1) * f[j] + (t3 - 2 * t2 + t) * h * sl[j] + (3 * t2 - 2 * t3) * f[j + 1] + (t3 - t2) * h * sl[j + 1]);
    });
  };
  return { D: V.map((col, i) => along(SD.D[i], col)), B: V.map((col, i) => along(SD.B[i], col)) };
}

export function finMesh(q, li = 0, bi = () => 0, ctx = null) {
  const far = li > 0;
  const fair = q.fair && ctx ? { ...(typeof q.fair === "object" ? q.fair : { r: q.fair }) } : null;
  const root0 = q.root.map((p) => p.slice(0, 3));
  let edge0 = q.edge.map((p) => [p[0], p[1], p[2], p[3] ?? 1]);
  let corners = (q.corners ?? []).map((c) => c + 1);
  const A = root0[0], B = root0[root0.length - 1];
  if (len(sub(edge0[0], A)) < 1e-6) { edge0 = edge0.slice(1); corners = corners.map((c) => c - 1); }
  if (len(sub(edge0[edge0.length - 1], B)) < 1e-6) edge0 = edge0.slice(0, -1);
  const ring = [[...A, edge0[0]?.[3] ?? 1], ...edge0, [...B, edge0[edge0.length - 1]?.[3] ?? 1]];
  // (the rim resampled; its bluntness carried along as a fourth number)
  const nu = Math.max(8, Math.round((q.n ?? 36) / (far ? 2.2 : 1)));
  const E = resample(ring, nu, corners), NU = E.length - 1;
  // (the root at the same shares of its own length)
  const Racc = [0];
  for (let i = 1; i < root0.length; i++) Racc.push(Racc[i - 1] + len(sub(root0[i], root0[i - 1])));
  const Eacc = [0];
  for (let i = 1; i < E.length; i++) Eacc.push(Eacc[i - 1] + len(sub(E[i], E[i - 1])));
  const rootAt = (f) => {
    const t = f * Racc[Racc.length - 1];
    let i = 0;
    while (i < Racc.length - 2 && Racc[i + 1] < t) i++;
    return lerp(root0[i], root0[i + 1], (t - Racc[i]) / ((Racc[i + 1] - Racc[i]) || 1e-9));
  };
  // (`rootBy` c: the root shared out over the rim by its length WEIGHTED 1 / (its distance from the root + c root
  //  lengths) -- the rim near a root end takes root as fast as it leaves it. By plain length, a straight leading edge
  //  running out of a root end had its columns all from that one end: a fan of slivers along it, folded)
  const Ew = q.rootBy ? rootWeights(E, root0, Racc[Racc.length - 1] * q.rootBy) : Eacc;
  const Rr = E.map((_, i) => rootAt(Ew[i] / Ew[NU]));
  // ROWS root -> rim, closer toward the rim
  const nv0 = Math.max(2, Math.round((q.across ?? 7) / (far ? 2.3 : 1)));
  const vs = Array.from({ length: nv0 + 1 }, (_, j) => Math.sin(Math.PI / 2 * j / nv0));
  let G = E.map((e, i) => vs.map((v) => lerp(Rr[i], e.slice(0, 3), v)));
  // (relaxed: each inside point toward its neighbours' mean, the rim and the root held -- a smooth sheet across a
  //  concave outline where straight rows would cross)
  const relax = q.relax ?? 24;
  for (let it = 0; it < relax; it++) {
    for (let i = 1; i < NU; i++) for (let j = 1; j < nv0; j++) {
      const ku = 1, wd = 1 / (vs[j] - vs[j - 1]), wp = 1 / (vs[j + 1] - vs[j]), tot = 2 * ku + wd + wp;   // (weights that keep the rows' spacing)
      const avg = [0, 1, 2].map((k) => (ku * (G[i - 1][j][k] + G[i + 1][j][k]) + wd * G[i][j - 1][k] + wp * G[i][j + 1][k]) / tot);
      G[i][j] = lerp(G[i][j], avg, .5);
    }
  }
  if (q.grid === "flow" || q.flow) G = harmonicGrid(G, vs, q.flow ?? 1);
  // (FAIRED: more rows where the sheet comes out of the body -- the fillet is drawn there)
  let V = G.map(() => vs.slice());
  const Gp = G;   // (the even grid: the smooth rim distance is solved on it)
  if (fair) ({ G, V } = fairRows(G, vs, ctx, fair, far));
  const nv = G[0].length - 1;
  // the sheet's own normal (Newell's, over the rim and root) and its FACE
  let Nw = [0, 0, 0];
  const loop = [...E, ...Rr.slice().reverse()];
  for (let i = 0; i < loop.length; i++) { const a = loop[i], b = loop[(i + 1) % loop.length]; Nw = add(Nw, [(a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])]); }
  Nw = nrm(Nw);
  const face = q.face ? nrm(q.face) : Nw;
  // the mid-surface's normals (central differences on the grid), turned to the face
  const midN = () => G.map((col, i) => col.map((_, j) => {
    const iu0 = Math.max(0, i - 1), iu1 = Math.min(NU, i + 1), jv0 = Math.max(0, j - 1), jv1 = Math.min(nv, j + 1);
    let du = sub(G[iu1][j], G[iu0][j]);
    if (len(du) < 1e-9) du = sub(G[iu1][Math.max(1, j)], G[iu0][Math.max(1, j)]);
    const dv = sub(G[i][jv1], G[i][jv0]);
    let n = crs(du, dv);
    if (len(n) < .05 * len(du) * len(dv) || len(n) < 1e-12) return null;   // (the grid pinched here: no sound normal -- its neighbours')
    n = nrm(n);
    return dot(n, face) < 0 ? n.map((v) => -v) : n;
  }));
  // (a normal the grid could not give: the nearest along its row, else along its column, else the face)
  const fillN = (M) => M.map((col, i) => col.map((n, j) => {
    if (n) return n;
    for (let d = 1; d <= M.length; d++) for (const ii of [i - d, i + d]) if (M[ii]?.[j]) return M[ii][j];
    for (let d = 1; d <= col.length; d++) for (const jj of [j - d, j + d]) if (col[jj]) return col[jj];
    return face;
  }));
  let Nm = fillN(midN());
  // (the distance to the rim, and the row's length, at every grid point)
  const Dr = G.map((col) => col.map((p) => rimDist(p, E)));
  const rowL = G.map((col, i) => len(sub(E[i].slice(0, 3), Rr[i])));
  const G0 = G.map((col) => col.map((p) => p.slice()));   // (the planform before it is cupped: the thickness is measured on it)
  // SHAPE: cup, camber, curl -- moved along the normal toward the face
  const cup = q.cup ?? 0, camber = q.camber ?? 0, curl = q.curl ?? 0, curlAt = q.curlAt ?? .6;
  if (cup || camber || curl) {
    // (the cup's depth: the distance to the rim SMOOTHED over the grid -- the distance itself has a ridge along the
    //  sheet's middle, which would crease the hollow into a V; relaxed, rim and root held, it is a round-bottomed bowl)
    const Dc = Dr.map((col) => col.slice()), NI = Dc.length - 1, NJ = Dc[0].length - 1;
    if (cup) for (let it = 0; it < 40; it++) for (let i = 1; i < NI; i++) for (let j = 1; j < NJ; j++)
      Dc[i][j] = Math.min(Dr[i][j] * 1.5, (Dc[i - 1][j] + Dc[i + 1][j] + Dc[i][j - 1] + Dc[i][j + 1]) / 4);
    G.forEach((col, i) => col.forEach((p, j) => {
      const v = V[i][j];
      const dz = -cup * Dc[i][j] + camber * rowL[i] * 4 * v * (1 - v) + curl * rowL[i] * Math.max(0, (v - curlAt) / (1 - curlAt)) ** 2;
      col[j] = add(p, Nm[i][j], dz);
    }));
    Nm = fillN(midN());
  }
  // THICKNESS: by the distance to the rim, up to `thick`
  const span = Math.max(...E.map((e) => len(sub(e.slice(0, 3), A))));
  const thick = q.thick ?? span * .06, slope = q.slope ?? .3;
  // (on the SMOOTH rim distance -- smoothRimDist: no crease down the middle; the old raw distance if the solve fails)
  const SD = q.thickBy === "rim" ? null : fair ? resampleSD(smoothRimDist(Gp, E.map((e) => e[3] ?? 1)), vs, V) : smoothRimDist(G0, E.map((e) => e[3] ?? 1));
  let H = SD ? SD.D.map((col, i) => col.map((d, j) => thick * Math.tanh(slope * SD.B[i][j] * d / thick))) : Dr.map((col) => col.map((d) => thick * Math.tanh(slope * d / thick)));
  // (SWELL [t, len, slope]: thicker toward the root -- t, held for 40% of len from it and gone at len -- the middle of
  //  a fluke as deep as the stock it leaves; its own wedge from the rim, `slope` (default 1.2: blunt), the rim still sharp)
  if (q.swell) {
    const [st, sl, ss = 1.2] = Array.isArray(q.swell) ? q.swell : [q.swell.t, q.swell.len, q.swell.slope];
    // (its rim distance SMOOTHED over the grid as the cup's is: the distance has a ridge along the sheet's middle, and
    //  so steep a wedge creased the fluke along it; and the two thicknesses joined by a smooth max, not a crease)
    const rootE = root0.map((p) => [...p, 1]), Ds = SD ? SD.D : Dr.map((col) => col.slice()), NI = Ds.length - 1, NJ = Ds[0].length - 1;
    if (!SD) for (let it = 0; it < 40; it++) for (let i = 1; i < NI; i++) for (let j = 1; j < NJ; j++)
      Ds[i][j] = Math.min(Dr[i][j] * 1.5, (Ds[i - 1][j] + Ds[i + 1][j] + Ds[i][j - 1] + Ds[i][j + 1]) / 4);
    H = H.map((col, i) => col.map((hh, j) => {
      const dr = rootE.length > 1 ? rimDist(G[i][j], rootE) : len(sub(G[i][j], root0[0]));
      const hs = st * Math.tanh(ss * Ds[i][j] / st) * (1 - sstep(.4, 1, dr / sl)), km = .35 * Math.max(hh, hs, 1e-9), e = Math.max(0, km - Math.abs(hh - hs)) / km;
      return Math.max(hh, hs) + e * e * km / 4;   // (a third of the greater: none at the rim, where both are nothing)
    }));
  }
  // ---- the two faces ----
  const P = [], N = [], C = [], SI = [], SW = [], Tr = [];
  const cO = rgb(q.color), cI = q.inner != null ? rgb(q.inner) : cO, cT = q.tip != null ? rgb(q.tip) : null, tipAt = q.tipAt ?? .6, iRim = q.innerRim ?? 0;
  const axis = nrm(sub(E.reduce((b, e) => (len(sub(e.slice(0, 3), A)) > len(sub(b.slice(0, 3), A)) ? e : b), E[0]).slice(0, 3), lerp(A, B, .5)));
  const rmid = lerp(A, B, .5), reach = Math.max(1e-6, ...E.map((e) => dot(sub(e.slice(0, 3), rmid), axis)));
  const bO = bi(q.bone ?? "body"), bR = q.rootBone ? bi(q.rootBone) : bO, rb = q.rootBlend ?? .4;
  const ix = (side, i, j) => side * (NU + 1) * (nv + 1) + i * (nv + 1) + j;
  const W = [], wet0 = q.wet ?? 0;
  // (`rim` metres: a band of `rimColor` -- default `tip`, else `color` -- round the rim on both faces: an ear's dark edge;
  //  `rimBack` (0..1, default 1): how strongly the band shows on the back face -- an ear pale-haired round its hollow,
//  only a little paler toward the rim behind; `patFace`: which faces a `pat` is painted on -- "back" (the far side from `face`: an ear's striped back, its hollow
  //  plain), "face", or both)
  const oRim = q.rim ?? 0, rimAt = q.rimAt ?? 0, rimBk = q.rimBack ?? 1, cRim = oRim > 0 ? rgb(q.rimColor ?? q.tip ?? q.color) : null, PM = [];
  const patOn = q.patFace === "back" ? [0, 1] : q.patFace === "face" ? [1, 0] : [1, 1];
  // FAIRED (`fair`): each face where the sheet meets the body is the smooth union of the two (fairAt), so the body
  // swells out into the sheet with a fillet; deeper in, where it is the body's surface, it is drawn inside it
  // (the RIM is never faired: the two faces meet on it as they do unfaired, and their fillet fades out within `edge`
  //  ([from, to], shares of r, default [.2, 1.5]) of it -- where the rim runs into the body a fillet round its end
  //  tore into flaps and beaks, with the faces' points marched off in all directions about a sheet that grazes the
  //  body there. A face point is the body's skin only while that is near: a skin met far off along a face that grazes
  //  the body is the body beyond the fillet -- the face drawn back to its own place, under the skin; and the skin it
  //  meets is drawn `sink` under it along the BODY's normal, so the faces dive in at a definite angle, not a sawtooth)
  const fairF = { deep: [1, 1.5], ...fair, nsink: true }, rnd = fair?.round ?? 0, [e0, e1] = fair?.edge ?? (rnd > 0 ? [0, 0] : [.2, 1.5]);
  // (ROUND, 2026-11-08 pass 2: each point's march turns from its face's normal to the sheet's outward direction in its
  //  plane over `round` r of the rim (fairFin) -- the rim faired in its plane, the fillet run on round it. `round: 0`
  //  the old way: the rim left alone, the fillet faded out within `edge` of it)
  const RN = fair && rnd > 0 ? G.map((col, i) => col.map((p, j) => {
    const r = rimNear(p, E), nm = Nm[i][j];
    let m;
    if (r.d > 1e-5 * span) m = sub(r.q, p);
    else { const a = E[Math.max(0, r.seg)], b = E[Math.min(NU, r.seg + 1)]; m = crs(sub(b.slice(0, 3), a.slice(0, 3)), nm); if (dot(m, sub(E[i].slice(0, 3), G[i][Math.max(0, nv - 1)])) < 0) m = m.map((v) => -v); }
    m = nrm(sub(m, nm.map((v) => v * dot(m, nm))));
    return { d: r.d, m, al: 1 - sstep(0, rnd * fair.r, r.d) };
  })) : null;
  const FW = fair ? [1, -1].map((sg) => G.map((col, i) => col.map((p, j) => {
    const base = add(p, Nm[i][j], sg * H[i][j] / 2), z = e1 > 0 ? sstep(e0 * fair.r, e1 * fair.r, Dr[i][j]) : 1;
    if (RN) { const r = RN[i][j]; return fairFin(p, j === nv ? p : base, Nm[i][j].map((v) => v * sg), r.m, r.al, j === nv ? 0 : H[i][j] / 2, r.d, ctx, fairF, far); }
    if (j === nv || z <= 0) return { t: H[i][j] / 2, w: 0, q: base };
    const f = fairAt(p, Nm[i][j].map((v) => v * sg), H[i][j] / 2, ctx, fairF, far);
    return z >= 1 ? f : { ...f, w: f.w * z, q: base.map((v, k) => v + (f.q[k] - v) * z) };
  }))) : null;
  for (const side of [0, 1]) {
    const sg = side ? -1 : 1;
    const S = G.map((col, i) => col.map((p, j) => (FW ? FW[side][i][j].q : add(p, Nm[i][j], sg * H[i][j] / 2))));
    for (let i = 0; i <= NU; i++) for (let j = 0; j <= nv; j++) {
      const p = S[i][j];
      const iu0 = Math.max(0, i - 1), iu1 = Math.min(NU, i + 1), jv0 = Math.max(0, j - 1), jv1 = Math.min(nv, j + 1);
      let du = sub(S[iu1][j], S[iu0][j]);
      if (len(du) < 1e-9) du = sub(S[iu1][Math.max(1, j - 1)], S[iu0][Math.max(1, j - 1)]);
      let n = crs(du, sub(S[i][jv1], S[i][jv0]));
      if (len(n) < 1e-12) n = Nm[i][j].map((v) => v * sg);
      n = nrm(n);
      if (dot(n, Nm[i][j]) * sg < 0) n = n.map((v) => -v);
      P.push(...p); N.push(...n);
      // (colour: the face side `inner` inside a band of `color` round the rim; toward the far end `tip`)
      let c = side === 0 && q.inner != null ? cO.map((v, k) => v + (cI[k] - v) * (iRim > 0 ? sstep(iRim * .5, iRim * 1.5, Dr[i][j]) : 1)) : cO;
      if (cT) { const f = dot(sub(p, rmid), axis) / reach; c = c.map((v, k) => v + (cT[k] - v) * sstep(tipAt, 1, f)); }
      if (cRim) {   // (`rim`: the edge band, both faces -- from `rimAt` of the way out, default all round)
        const e = (1 - sstep(oRim * .5, oRim * 1.5, Dr[i][j])) * (rimAt > 0 ? sstep(rimAt - .15, rimAt + .05, dot(sub(p, rmid), axis) / reach) : 1) * (side === 0 ? 1 : rimBk);
        c = c.map((v, k) => v + (cRim[k] - v) * e);
      }
      PM.push(patOn[side]);
      c = c.slice(); W.push(wet0);
      const wR = bR === bO ? 0 : 1 - sstep(0, rb, V[i][j]);
      if (FW && FW[side][i][j].w > 0) {   // (faired: the body's paint, wetness, normal and skin where the fillet is the body's)
        const fw = FW[side][i][j], a = fw.a, wc = sstep(.15, .85, fw.w), ws = sstep(.05, .9, fw.w);
        if (fair.color !== false) for (let k = 0; k < 3; k++) c[k] += (a.c[k] - c[k]) * wc;
        W[W.length - 1] += (a.wet - W[W.length - 1]) * wc;
        // (the smooth union's own normal: its gradient is the two gradients mixed by the share -- exact for this blend)
        const ns = fw.ns ?? Nm[i][j].map((v) => v * sg), un = nrm([0, 1, 2].map((k) => ns[k] + (a.n[k] - ns[k]) * fw.w)), o = N.length - 3, wn = sstep(0, .2, fw.w);
        const nn = nrm([0, 1, 2].map((k) => N[o + k] + (un[k] - N[o + k]) * wn));
        N[o] = nn[0]; N[o + 1] = nn[1]; N[o + 2] = nn[2];
        const mix = new Map([[bO, (1 - wR) * (1 - ws)]]);
        mix.set(bR, (mix.get(bR) ?? 0) + wR * (1 - ws));
        a.si.forEach((b, k) => mix.set(b, (mix.get(b) ?? 0) + a.sw[k] * ws));
        const top = [...mix].sort((x, y) => y[1] - x[1]).slice(0, 4), tot = top.reduce((t, e) => t + e[1], 0) || 1;
        for (let k = 0; k < 4; k++) { SI.push(top[k]?.[0] ?? 0); SW.push((top[k]?.[1] ?? 0) / tot); }
      } else { SI.push(bO, bR, 0, 0); SW.push(1 - wR, wR, 0, 0); }
      C.push(...c);
    }
    for (let i = 0; i < NU; i++) for (let j = 0; j < nv; j++) {
      const a = ix(side, i, j), b = ix(side, i + 1, j), c = ix(side, i, j + 1), d = ix(side, i + 1, j + 1);
      Tr.push(a, b, c, b, d, c);
    }
  }
  // (the root closed between the faces: inside the body)
  for (let i = 0; i < NU; i++) { const a = ix(0, i, 0), b = ix(0, i + 1, 0), c = ix(1, i, 0), d = ix(1, i + 1, 0); Tr.push(a, c, b, b, c, d); }
  const T = orientFin(P, N, Tr);
  return { P, N, T, C, SI, SW, ...(FW ? { W } : {}), ...(q.patFace ? { PM } : {}) };
}
// FAIRING (a fin's `fair`): the sheet grown out of the body instead of stuck into it. `ctx` is the body's field: dist
// (signed distance), attr (paint, wetness, normal and skin at a point), cell (its grid). Where the sheet's middle comes
// out through the body's surface the rows are drawn closer (a fillet needs them), and each face is put where the
// SMOOTH UNION of the body and the sheet (a slab, its own half-thickness h either side of the middle) has its surface
// along that face's normal: far from the body that is the sheet, near it a fillet swelling out to meet the body's
// surface tangentially -- a stock running into a fluke, a fin's foot -- and deeper in, the body's surface itself, which
// is drawn `sink` inside it (and, deeper still, at the sheet's own thickness: hidden either way).
const clamp01 = (x) => (x < 0 ? 0 : x > 1 ? 1 : x);
function fairRows(G, vs, ctx, fair, far) {
  const k = fair.r, nx = fair.rows ?? (far ? 3 : 7), nv = G[0].length - 1, per = 8;
  const logi = (x) => 1 / (1 + Math.exp(-1.8 * x));
  const outG = [], outV = [], cols = [];
  for (const col of G) {
    const D = [], acc = [0];
    for (let j = 0; j < nv; j++) for (let s = 0; s < per; s++) D.push(lerp(col[j], col[j + 1], s / per));
    D.push(col[nv].slice());
    for (let i = 1; i < D.length; i++) acc.push(acc[i - 1] + len(sub(D[i], D[i - 1])));
    const L = acc[acc.length - 1];
    if (L < 1e-7) { cols.push({ col, L: 0 }); continue; }   // (a root end: no length -- kept in its place, drawn below as one point)
    // (where the middle comes out of the body: the first sample outside, then bisected)
    let se = L;
    if (ctx.dist(...D[0]) > 0) se = 0;
    else for (let i = 1; i < D.length; i++) if (ctx.dist(...D[i]) > 0) {
      let lo = 0, hi = 1;
      for (let it = 0; it < 18; it++) { const m = (lo + hi) / 2; (ctx.dist(...lerp(D[i - 1], D[i], m)) > 0 ? (hi = m) : (lo = m)); }
      se = acc[i - 1] + (acc[i] - acc[i - 1]) * hi; break;
    }
    cols.push({ col, D, acc, L, ue: Math.min(1, (se + .25 * k) / L), sg: Math.max(.015, .9 * k / L) });
  }
  // (the bunching's place and width smoothed from column to column, so the rows stay in step -- a crumpled grid has no normal;
  //  a root end's taken from its nearest column with a length)
  cols.forEach((c, i) => { if (c.L < 1e-7) { const o = cols.slice(i).find((x) => x.L >= 1e-7) ?? cols.slice(0, i).reverse().find((x) => x.L >= 1e-7); c.ue = o?.ue ?? 1; c.sg = o?.sg ?? 1; } });
  for (let it = 0; it < 6; it++) for (const key of ["ue", "sg"]) {
    const v = cols.map((c) => c[key]);
    for (let i = 1; i + 1 < cols.length; i++) if (cols[i].L > 1e-7) cols[i][key] = (v[i - 1] + 2 * v[i] + v[i + 1]) / 4;
  }
  for (const { col, D, acc, L, ue, sg } of cols) {
    if (L < 1e-7) { outG.push(Array.from({ length: nv + nx + 1 }, () => col[0].slice())); outV.push(Array.from({ length: nv + nx + 1 }, (_, m) => m / (nv + nx))); continue; }
    // (the rows' count as a function of the share along: the old rows' own, plus nx more bunched round the fillet)
    const uj = col.map((_, j) => acc[per * j] / L);
    const base = (u) => { let j = 0; while (j < nv - 1 && uj[j + 1] < u) j++; return (j + clamp01((u - uj[j]) / ((uj[j + 1] - uj[j]) || 1e-9))) / nv; };
    const b0 = logi(-ue / sg), b1 = logi((1 - ue) / sg);
    const cnt = (u) => nv * base(u) + nx * (logi((u - ue) / sg) - b0) / ((b1 - b0) || 1);
    const NS = 600, cu = Array.from({ length: NS + 1 }, (_, i) => cnt(i / NS)), tot = nv + nx;
    const rowsG = [], rowsV = [];
    for (let m = 0; m <= tot; m++) {
      const target = cu[NS] * m / tot;
      let i = 0;
      while (i < NS - 1 && cu[i + 1] < target) i++;
      const u = m === 0 ? 0 : m === tot ? 1 : (i + clamp01((target - cu[i]) / ((cu[i + 1] - cu[i]) || 1e-9))) / NS;
      const a = u * L;
      let lo = 0;
      while (lo < acc.length - 2 && acc[lo + 1] < a) lo++;
      rowsG.push(m === tot ? col[nv].slice() : lerp(D[lo], D[lo + 1], clamp01((a - acc[lo]) / ((acc[lo + 1] - acc[lo]) || 1e-9))));
      // (the row's share in the sheet's own terms: the old rows' v where it falls between them)
      const jj = Math.min(nv - 1, Math.floor(base(u) * nv)), f = base(u) * nv - jj;
      rowsV.push(vs[jj] + (vs[jj + 1] - vs[jj]) * f);
    }
    outG.push(rowsG); outV.push(rowsV);
  }
  return { G: outG, V: outV };
}
// one face point: the middle p, the face's normal n, the sheet's half-thickness h. Returns t (how far out along n the
// face is) and w (how much it is the body's: 0 the sheet, 1 the body) with the body's attributes there
function fairAt(p, n, h, ctx, fair, far) {
  const k = fair.r, sink = (fair.sink ?? 1) * ctx.cell * (far ? 2 : 1);
  const f0 = ctx.dist(p[0], p[1], p[2]);
  const at = (t) => [p[0] + n[0] * t, p[1] + n[1] * t, p[2] + n[2] * t];
  if (f0 > h + k) return { t: h, w: 0, q: at(h) };   // (too far from the body for it to matter)
  const U = (t) => { const f = ctx.dist(...at(t)), g = t - h, m = clamp01(.5 + .5 * (g - f) / k); return [g + (f - g) * m - k * m * (1 - m), m, (g - f) / k]; };
  const cap = h + 2.5 * k + (f0 < 0 ? Math.min(-f0, fair.reach ?? k) : 0);   // (a point inside the body: as far again as it is deep, no further -- a grazing march would land far off)
  let t = 0, u = U(0)[0], hit = null;
  while (t < cap) {
    const t1 = t + Math.max(.8 * Math.abs(u), ctx.cell * .08), u1 = U(t1)[0];
    if (u1 >= 0) { let lo = t, hi = t1; for (let it = 0; it < 22; it++) { const m = (lo + hi) / 2; (U(m)[0] >= 0 ? (hi = m) : (lo = m)); } hit = hi; break; }
    t = t1; u = u1;
  }
  if (hit === null) return { t: h, w: 0, q: at(h) };
  const [, w, e] = U(hit);
  if (w <= 0) return { t: hit, w: 0, q: at(hit) };
  // (the body's own surface: just inside it -- and where it is well clear of the sheet's own face, back down to that face)
  const [d0, d1] = fair.deep ?? [1.6, 3], deep = sstep(d0, d1, e), s = Math.min(sink, hit * .5) * sstep(.5, .95, w);   // (never past the middle)
  if (fair.nsink) {   // (a fin's: sunk along the body's own normal, a real depth whatever the angle the face meets it at)
    const H0 = at(hit), d = ctx.cell * .25, gd = [0, 1, 2].map((c) => { const a = H0.slice(), b = H0.slice(); a[c] += d; b[c] -= d; return ctx.dist(a[0], a[1], a[2]) - ctx.dist(b[0], b[1], b[2]); });
    const gl = Math.hypot(gd[0], gd[1], gd[2]) || 1, tf = hit + (Math.min(hit, h) - hit) * deep, Q = at(tf).map((v, c) => v - gd[c] / gl * s * (1 - deep));
    return { t: tf, w, q: Q, a: ctx.attr(Q[0], Q[1], Q[2]) };
  }
  const tIn = hit - s, tf = tIn + (Math.min(tIn, h) - tIn) * deep, P = at(tf);
  return { t: tf, w, q: P, a: ctx.attr(P[0], P[1], P[2]) };
}
// A FIN's face point faired (2026-11-08, pass 2): fairAt's smooth union, marched along a direction that turns from the
// face's normal n (well in from the rim) to the sheet's own outward direction m at the rim (in its plane, away from
// the sheet) over `al` (0 -> 1). Both faces' rim points march along m and land on one point: the rim is faired IN ITS
// PLANE -- where it runs into the body it bends round into the skin, an in-plane fillet -- and the faces next to it
// round over onto it, so the fillet runs on round the rim without the two faces' points parting (the old flaps and
// beaks) and without the rim standing out of the fillet (the old notch at a leading edge's root). The sheet's distance
// along the march is max(t n.d - h, t m.d - dr) (a slab h thick each side, cut off dr ahead by its rim); the point is
// moved from its own place `base` by how much further out the union's surface is than the sheet's, so away from the
// body nothing moves at all.
function fairFin(p, base, n, m, al, h, dr, ctx, fair, far) {
  const k = fair.r, sink = (fair.sink ?? 1) * ctx.cell * (far ? 2 : 1);
  const c = Math.cos(al * Math.PI / 2), s = Math.sin(al * Math.PI / 2);
  const d = nrm([n[0] * c + m[0] * s, n[1] * c + m[1] * s, n[2] * c + m[2] * s]), dn = Math.max(0, dot(d, n)), dm = Math.max(0, dot(d, m));
  const t0 = Math.min(dn > 1e-6 ? h / dn : Infinity, dm > 1e-6 ? dr / dm : Infinity, 4 * k + h);
  const g = (t) => Math.max(t * dn - h, t * dm - dr);
  const f0 = ctx.dist(p[0], p[1], p[2]);
  const at = (t) => [p[0] + d[0] * t, p[1] + d[1] * t, p[2] + d[2] * t];
  const none = { t: t0, w: 0, q: base };
  if (f0 > t0 + k) return none;
  const U = (t) => { const f = ctx.dist(...at(t)), gg = g(t), w = clamp01(.5 + .5 * (gg - f) / k); return [gg + (f - gg) * w - k * w * (1 - w), w, (gg - f) / k]; };
  const cap = t0 + 2.5 * k + (f0 < 0 ? Math.min(-f0, fair.reach ?? k) : 0);
  let t = 0, u = U(0)[0], hit = null;
  while (t < cap) {
    const t1 = t + Math.max(.8 * Math.abs(u), ctx.cell * .08), u1 = U(t1)[0];
    if (u1 >= 0) { let lo = t, hi = t1; for (let it = 0; it < 22; it++) { const mm = (lo + hi) / 2; (U(mm)[0] >= 0 ? (hi = mm) : (lo = mm)); } hit = hi; break; }
    t = t1; u = u1;
  }
  if (hit === null) return none;
  const [, w, e] = U(hit);
  if (w <= 0) return { t: hit, w: 0, q: add(base, d, Math.max(0, hit - t0)) };
  // (inside the body's own surface: sunk under it along the BODY's normal; where that skin is well clear of the sheet's
  //  own face, back down to the face)
  // (no further out than a fillet carries a point -- `cap` r, approached smoothly: a march that runs on along under the
  //  skin, as one near the sheet's plane does, meets it far off; neighbours that met it near and far stay together)
  const [d0, d1] = fair.deep ?? [1, 1.5], cm = (fair.cap ?? .6) * k, dl = hit - t0, dc = cm * Math.tanh(dl / cm);
  const deep = sstep(d0, d1, e), sk = Math.min(sink, hit * .5) * sstep(.5, .95, w) * (dl > 1e-9 ? dc / dl : 1);
  const H0 = at(t0 + dc), dd = ctx.cell * .25, gd = [0, 1, 2].map((cc) => { const a = H0.slice(), b = H0.slice(); a[cc] += dd; b[cc] -= dd; return ctx.dist(a[0], a[1], a[2]) - ctx.dist(b[0], b[1], b[2]); });
  const gl = Math.hypot(gd[0], gd[1], gd[2]) || 1, tf = t0 + dc * (1 - deep);
  const Q = add(base, d, tf - t0).map((v, cc) => v - gd[cc] / gl * sk * (1 - deep));
  // (the sheet's own normal along the march: its face's, or at the rim its plane's outward m)
  return { t: tf, w, q: Q, a: ctx.attr(Q[0], Q[1], Q[2]), ns: hit * dn - h >= hit * dm - dr ? n : m };
}
// the nearest point of the polyline E (its first three numbers) to p
function rimNear(p, E) {
  let best = Infinity, q = null, seg = 0;
  for (let i = 0; i + 1 < E.length; i++) {
    const a = E[i].slice(0, 3), ab = sub(E[i + 1].slice(0, 3), a), l2 = dot(ab, ab) || 1e-12, t = Math.max(0, Math.min(1, dot(sub(p, a), ab) / l2));
    const c = add(a, ab, t), dd = len(sub(p, c));
    if (dd < best) { best = dd; q = c; seg = i; }
  }
  return { d: best, q, seg };
}
// (a fin's faces wound to their normals -- skipping the slivers at the degenerate ends, which have none to agree with)
function orientFin(P, N, T) {
  const out = [];
  for (let f = 0; f < T.length; f += 3) {
    const a = T[f], b = T[f + 1], c = T[f + 2];
    const e1 = [P[3 * b] - P[3 * a], P[3 * b + 1] - P[3 * a + 1], P[3 * b + 2] - P[3 * a + 2]], e2 = [P[3 * c] - P[3 * a], P[3 * c + 1] - P[3 * a + 1], P[3 * c + 2] - P[3 * a + 2]];
    const fn = crs(e1, e2);
    if (len(fn) < 1e-14) continue;   // (a degenerate face: dropped)
    const nn = [N[3 * a] + N[3 * b] + N[3 * c], N[3 * a + 1] + N[3 * b + 1] + N[3 * c + 1], N[3 * a + 2] + N[3 * b + 2] + N[3 * c + 2]];
    out.push(...(dot(fn, nn) < 0 ? [a, c, b] : [a, b, c]));
  }
  return out;
}

// the extent of a sharp shape (bodyspec.js: its x range, bounds)
export function sharpPoints(q) {
  if (q.type === "horn") return q.pts.map((p) => [p[0], p[1], p[2], p[3]]);
  return [...q.root, ...q.edge].map((p) => [p[0], p[1], p[2], 0]);
}
