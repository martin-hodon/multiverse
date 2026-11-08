// SCULPT (2026-11-04): a shape as a FIELD -- smooth distance functions, blended -- turned into a mesh. No three.js, no
// engine: pure numbers in, arrays out (bodies.js makes creatures of it; docs/engines.md "Sculpted bodies").
//
// Why a field and not parts: a body of pills swept one by one meets itself in seams -- each pill has its own rings and its
// own density, a small part next to a large one is a step in the surface, and a mark laid on a sphere floats off a head
// that is blended into something else. A field is one surface: whatever is blended, the mesher sees only where it is.
//
// THE PRIMITIVES (root space, metres), applied in order, each blended into what came before by its `k` (metres: a smooth
// minimum, 0 a hard union) or, `op: "sub"`, carved out of it (a smooth maximum):
//   sphere { c, r }   ell { c, r: [a, b, c], rot?: [x, y, z] degrees }   cone { a, b, ra, rb } (a round cone: two spheres
//   and the cone tangent to both)   tube { pts: [[x, y, z, r], ...] } (a Catmull-Rom spline through the points, its radius
//   eased along it: a tail, a snout, a leg with its joints)   box { c, r: [a, b, c], round, rot? } (a rounded box)
//   tri { a, b, c, r } (a triangle thickened by r: an ear, a fin)   -- and on any of them lumps: { amp, size } (a fleece)
// Each carries an ATTRIBUTE vector (`attr`: any numbers -- bodies.js puts colour, wetness, bone weights in it), blended
// across the seam exactly as the distance is: where two pieces melt into each other, their colours and their bones do.
//
// THE MESH: the field sampled on a grid `cell` apart, a vertex in every cell the surface passes through (SURFACE NETS:
// the mean of where it crosses the cell's edges), a quad across every grid edge it crosses -- an even mesh, every face
// about one cell, with no seams and no steps. Then SIMPLIFIED to a budget of triangles (edge collapses in the order of
// the error they add -- Garland and Heckbert's quadrics -- never one that turns a face over or leaves a sliver): the broad
// back loses most of its faces, the nose and the eyes' sockets keep theirs, and the density grades smoothly between.
// Then every vertex is put back ON the surface (a Newton step or two along the field's gradient), its normal the
// gradient itself (smooth shading, whatever the faces), its attributes read from the field where it now is.
// A body that is its own MIRROR IMAGE in z (mirrorOf) is meshed as its +z half, its midline held in the plane through
// the simplification, and reflected (mirrorMesh): half the work, an exactly symmetric mesh ("THE MIRROR" below).

const clamp01 = (x) => (x < 0 ? 0 : x > 1 ? 1 : x);
// HYPOT, FAST AND THE SAME (2026-11-08): V8's Math.hypot (its builtin: each |x| over the largest, a Kahan sum of their
// squares, the root times the largest), written out -- the very same float operations, so the very same bits, at
// about a third of the cost (the builtin's call took most of a field sample's time: one for every primitive's bounding
// sphere, at every sample). Checked against Math.hypot on millions of random triples: no difference
export function hyp3(a, b, c) {
  a = a < 0 ? -a : a; b = b < 0 ? -b : b; c = c < 0 ? -c : c;
  let m = a > b ? a : b; if (c > m) m = c;
  if (m === Infinity) return Infinity;
  if (a !== a || b !== b || c !== c) return NaN;
  if (m === 0) return 0;
  let sum = 0, comp = 0, n = a / m, s = n * n, p = s;
  comp = (p - sum) - s; sum = p;
  n = b / m; s = n * n - comp; p = sum + s; comp = (p - sum) - s; sum = p;
  n = c / m; s = n * n - comp; p = sum + s;
  return Math.sqrt(p) * m;
}
// (how far a point may be from a bounding sphere for the test below to need hypot's own bits: the square root of the
//  sum of squares differs from hypot by an ulp or two, so a test this far from its threshold decides alike either way)
const TOL = 1e-12;

// ---- the primitives' distances ----------------------------------------------------------------------------------
function rotM(deg) {   // Euler XYZ (three.js's default order), as a row-major 3x3
  const [x, y, z] = (deg ?? [0, 0, 0]).map((d) => d * Math.PI / 180);
  const a = Math.cos(x), b = Math.sin(x), c = Math.cos(y), d = Math.sin(y), e = Math.cos(z), f = Math.sin(z);
  const ae = a * e, af = a * f, be = b * e, bf = b * f;
  return [c * e, -c * f, d, af + be * d, ae - bf * d, -b * c, bf - ae * d, be + af * d, a * c];
}
// a point into a rotated primitive's own frame: R^T (p - c)
const toLocal = (R, c, x, y, z) => { const u = x - c[0], v = y - c[1], w = z - c[2];
  return [R[0] * u + R[3] * v + R[6] * w, R[1] * u + R[4] * v + R[7] * w, R[2] * u + R[5] * v + R[8] * w]; };

// the round cone between spheres (a, ra) and (b, rb) (Inigo Quilez's, exact)
function roundCone(px, py, pz, a, b, r1, r2) {
  const bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2], l2 = bx * bx + by * by + bz * bz, rr = r1 - r2, a2 = l2 - rr * rr;
  const ax = px - a[0], ay = py - a[1], az = pz - a[2];
  if (a2 <= 1e-12) { const d1 = hyp3(ax, ay, az) - r1, d2 = hyp3(px - b[0], py - b[1], pz - b[2]) - r2; return Math.min(d1, d2); }
  const il2 = 1 / l2, y = ax * bx + ay * by + az * bz, z = y - l2;
  const qx = ax * l2 - bx * y, qy = ay * l2 - by * y, qz = az * l2 - bz * y, x2 = qx * qx + qy * qy + qz * qz;
  const y2 = y * y * l2, z2 = z * z * l2, k = Math.sign(rr) * rr * rr * x2;
  if (Math.sign(z) * a2 * z2 > k) return Math.sqrt(x2 + z2) * il2 - r2;
  if (Math.sign(y) * a2 * y2 < k) return Math.sqrt(x2 + y2) * il2 - r1;
  return (Math.sqrt(x2 * a2 * il2) + y * rr) * il2 - r1;
}
// a Catmull-Rom spline through [x, y, z, r] points, as `per` round cones a span
function tubeSegments(pts, per = 5) {
  const P = pts.map((q) => [q[0], q[1], q[2] ?? 0, q[3]]), n = P.length, at = (i) => P[Math.max(0, Math.min(n - 1, i))];
  const cr = (p0, p1, p2, p3, t) => p1.map((_, k) => .5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t * t * t));
  const out = [];
  for (let i = 0; i < n - 1; i++) for (let s = 0; s < per; s++) {
    const A = cr(at(i - 1), at(i), at(i + 1), at(i + 2), s / per), B = cr(at(i - 1), at(i), at(i + 1), at(i + 2), (s + 1) / per);
    out.push([A, B]);
  }
  return out;
}

// ---- THE SWEEP (2026-11-08): a long neck, a thin tail -- ONE smooth tube along a whole chain of bones ------------------
// A neck or a tail drawn as a run of tubes or cones, one a bone, is a string of beads: wherever two of them overlap,
// the smooth union of two surfaces that agree is fatter than either (by up to a quarter of its blend), and a
// Catmull-Rom spline eases its radius through the points with overshoot -- a swell before every narrowing. A SWEEP is
// one shape: its centreline a centripetal Catmull-Rom spline through the points (no cusps, no loops), sampled densely;
// its radius a function of the ARC LENGTH, a monotone cubic through the points' radii (Fritsch-Carlson: C1, never
// swelling past its neighbours), so a taper is a taper; its cross-section a circle -- or an ellipse `aspect` times as
// high along `up` (per point as a fifth number), carried along the curve without twisting (a rotation-minimising frame).
// Its distance: the exact union of the round cones between the dense samples (a canal surface: smooth wherever the
// radius is), or for an ellipse the section's distance at the nearest foot on the curve (Quilez's ellipse bound).
// Its SKIN follows the curve: `chain` (bone ids, the rig's own chain: neck, neck2, neck3) and `knots` ([s, w]: where
// along it, metres of arc, each bone hands over to the next, and over how far either side -- bodyspec.js finds them
// at the rig's joints), so the neck bends as the bones do, with no seam and no bead at a joint. `bands` ([from, to,
// colour] shares of its length: a ringed tail), `end: "point"` (its last radius 0: a tapering tail).
// `cut: [s0, s1]` (metres of arc): only that stretch of it in the field (bodyspec.js hands its too-thin end to the
// detail mesher -- sharp.js sweepMesh -- and keeps the rest here, shrunk under it: `shrink` [s0, s1] by `shrinkBy`).
const sstep01 = (a, b, x) => { const t = clamp01((x - a) / ((b - a) || 1e-12)); return t * t * (3 - 2 * t); };
export function sweepCurve(p) {
  const n = p.pts.length, asp0 = p.aspect ?? 1;
  const P = p.pts.map((q, i) => [q[0], q[1], q[2] ?? 0, i === n - 1 && p.end === "point" ? 0 : q[3], q[4] ?? asp0]);
  if (n < 2) throw new Error("sweep: two points or more");
  const L3 = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
  const rmax = Math.max(...P.map((q) => q[3])), X = [], span = [];
  // (the centreline: centripetal Catmull-Rom, its ends extended by reflection; each span sampled finer the thinner it is)
  const ext = (a, b) => a.map((v, k) => 2 * v - b[k]), Q = [ext(P[0], P[1]), ...P, ext(P[n - 1], P[n - 2])];
  for (let i = 1; i < n; i++) {
    const p0 = Q[i - 1], p1 = Q[i], p2 = Q[i + 1], p3 = Q[i + 2], d = (a, b) => Math.max(1e-9, Math.sqrt(L3(a, b)));
    const t0 = 0, t1 = d(p0, p1), t2 = t1 + d(p1, p2), t3 = t2 + d(p2, p3);
    const rs = Math.max(Math.min(p1[3], p2[3]), rmax * .15), per = Math.max(8, Math.min(64, Math.ceil(L3(p1, p2) / (rs * .3))));
    for (let s = 0; s < per; s++) {
      const t = t1 + (t2 - t1) * s / per;
      const Lp = (a, b, ta, tb) => [0, 1, 2].map((k) => (a[k] * (tb - t) + b[k] * (t - ta)) / (tb - ta));
      const A1 = Lp(p0, p1, t0, t1), A2 = Lp(p1, p2, t1, t2), A3 = Lp(p2, p3, t2, t3), B1 = Lp(A1, A2, t0, t2), B2 = Lp(A2, A3, t1, t3);
      X.push(Lp(B1, B2, t1, t2)); span.push(i - 1);
    }
  }
  X.push(P[n - 1].slice(0, 3)); span.push(n - 1);
  const m = X.length, S = new Float64Array(m);
  for (let i = 1; i < m; i++) S[i] = S[i - 1] + L3(X[i - 1], X[i]);
  // (the points' own arc positions: where the samples were exactly them)
  const Sk = [];
  for (let i = 0; i < m; i++) if (i === 0 || span[i] !== span[i - 1]) Sk.push(S[i]);
  // (radius and aspect by arc length: a monotone cubic -- Fritsch-Carlson -- through the points' values)
  const mono = (Y) => {
    const h = [], dl = [], tg = new Array(n).fill(0);
    for (let i = 0; i < n - 1; i++) { h.push(Math.max(1e-9, Sk[i + 1] - Sk[i])); dl.push((Y[i + 1] - Y[i]) / h[i]); }
    tg[0] = dl[0]; tg[n - 1] = dl[n - 2];
    for (let i = 1; i < n - 1; i++) tg[i] = dl[i - 1] * dl[i] <= 0 ? 0 : (dl[i - 1] + dl[i]) / 2;
    for (let i = 0; i < n - 1; i++) {
      if (dl[i] === 0) { tg[i] = tg[i + 1] = 0; continue; }
      const a = tg[i] / dl[i], b = tg[i + 1] / dl[i], s2 = a * a + b * b;
      if (s2 > 9) { const t = 3 / Math.sqrt(s2); tg[i] = t * a * dl[i]; tg[i + 1] = t * b * dl[i]; }
    }
    return (s) => {
      let i = 0;
      while (i < n - 2 && s > Sk[i + 1]) i++;
      const t = Math.max(0, Math.min(1, (s - Sk[i]) / h[i])), t2 = t * t, t3 = t2 * t;
      return (2 * t3 - 3 * t2 + 1) * Y[i] + (t3 - 2 * t2 + t) * h[i] * tg[i] + (-2 * t3 + 3 * t2) * Y[i + 1] + (t3 - t2) * h[i] * tg[i + 1];
    };
  };
  const rOf = mono(P.map((q) => q[3])), aOf = mono(P.map((q) => q[4]));
  const R = Float64Array.from(S, (s) => Math.max(0, rOf(s))), A = Float64Array.from(S, (s) => Math.max(.05, aOf(s)));
  // (tangents, and the frame carried along without twisting -- double reflection -- from `up` square to the first)
  const T = X.map((_, i) => { const a = X[Math.max(0, i - 1)], b = X[Math.min(m - 1, i + 1)], l = L3(a, b) || 1; return [(b[0] - a[0]) / l, (b[1] - a[1]) / l, (b[2] - a[2]) / l]; });
  const dt = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], nz = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  let up0 = p.up ?? [0, 1, 0];
  if (Math.abs(dt(nz(up0), T[0])) > .98) up0 = Math.abs(T[0][1]) < .9 ? [0, 1, 0] : [1, 0, 0];
  const U = [nz(up0.map((v, k) => v - T[0][k] * dt(up0, T[0])))];
  for (let i = 1; i < m; i++) {
    const v1 = X[i].map((v, k) => v - X[i - 1][k]), c1 = dt(v1, v1) || 1e-12;
    const rL = U[i - 1].map((v, k) => v - v1[k] * 2 * dt(v1, U[i - 1]) / c1), tL = T[i - 1].map((v, k) => v - v1[k] * 2 * dt(v1, T[i - 1]) / c1);
    const v2 = T[i].map((v, k) => v - tL[k]), c2 = dt(v2, v2) || 1e-12;
    U.push(nz(rL.map((v, k) => v - v2[k] * 2 * dt(v2, rL) / c2)));
  }
  return { X, R, A, S, T, U, m, L: S[m - 1], Sk };
}
// the skin along it: each bone of `chain` its weight at arc s (out, one a bone) -- knots [[s, w], ...] hand over from
// one to the next, smoothly, w either side of s
export function sweepWeights(knots, s, out) {
  let prev = 1;
  for (let j = 0; j < knots.length; j++) {
    const [k, w] = knots[j], f = Math.min(prev, sstep01(k - w, k + w, s));
    out[j] = prev - f; prev = f;
  }
  out[knots.length] = prev;
  return out;
}
// its paint along it: `bands` [[from, to, rgb], ...] (shares of the length L) over the base colour c (rgb), edges e wide;
// a band from 0 or to 1 has no edge there (it runs on over the root and the round end: a black tip stays black to its pole)
export function sweepColour(bands, s, L, e, c, out) {
  out[0] = c[0]; out[1] = c[1]; out[2] = c[2];
  for (const [a, b, col] of bands ?? []) {
    const m = (a <= 0 ? 1 : sstep01(a * L - e, a * L + e, s)) * (b >= 1 ? 1 : 1 - sstep01(b * L - e, b * L + e, s));
    if (m > 0) for (let k = 0; k < 3; k++) out[k] += (col[k] - out[k]) * m;
  }
  return out;
}
function prepareSweep(p, q) {
  const C = sweepCurve(p), { X, R, A, S, T, U, L } = C;
  // (only its `cut` in the field, the samples there and one exactly at each end of it; `shrink` under the detail's start)
  const [s0, s1] = p.cut ?? [0, L], idx = [];
  for (let i = 0; i < C.m; i++) if (S[i] > s0 + 1e-9 && S[i] < s1 - 1e-9) idx.push(i);
  const at = (s) => { let i = 0; while (i < C.m - 2 && S[i + 1] < s) i++; const t = clamp01((s - S[i]) / ((S[i + 1] - S[i]) || 1e-12));
    const l = (a, b) => a + (b - a) * t;
    return { x: [0, 1, 2].map((k) => l(X[i][k], X[i + 1][k])), r: l(R[i], R[i + 1]), a: l(A[i], A[i + 1]), s,
             t: T[t < .5 ? i : i + 1], u: U[t < .5 ? i : i + 1] }; };
  const pts = [at(s0), ...idx.map((i) => ({ x: X[i], r: R[i], a: A[i], s: S[i], t: T[i], u: U[i] })), at(s1)];
  if (p.shrink) { const [a, b] = p.shrink, f = p.shrinkBy ?? .08; for (const e of pts) e.r *= 1 - f * sstep01(a, b, e.s); }
  const n = pts.length, ns = n - 1, ell = pts.some((e) => Math.abs(e.a - 1) > 1e-6);
  const px = new Float64Array(3 * n), pr = new Float64Array(n), pa = new Float64Array(n), ps = new Float64Array(n), pu = new Float64Array(3 * n);
  pts.forEach((e, i) => { px.set(e.x, 3 * i); pr[i] = e.r; pa[i] = e.a; ps[i] = e.s; pu.set(e.u, 3 * i); });
  const G = 8, ng = Math.ceil(ns / G), sb = new Float64Array(4 * ns), gb = new Float64Array(4 * ng);
  for (let i = 0; i < ns; i++) {
    const j = i + 1, rr = Math.max(pr[i] * Math.max(1, pa[i]), pr[j] * Math.max(1, pa[j]));
    for (let k = 0; k < 3; k++) sb[4 * i + k] = (px[3 * i + k] + px[3 * j + k]) / 2;
    sb[4 * i + 3] = hyp3(px[3 * j] - px[3 * i], px[3 * j + 1] - px[3 * i + 1], px[3 * j + 2] - px[3 * i + 2]) / 2 + rr;
  }
  for (let g = 0; g < ng; g++) {
    const i0 = g * G, i1 = Math.min(ns, i0 + G);
    let cx = 0, cy = 0, cz = 0;
    for (let i = i0; i < i1; i++) { cx += sb[4 * i]; cy += sb[4 * i + 1]; cz += sb[4 * i + 2]; }
    cx /= i1 - i0; cy /= i1 - i0; cz /= i1 - i0;
    let r = 0;
    for (let i = i0; i < i1; i++) r = Math.max(r, hyp3(sb[4 * i] - cx, sb[4 * i + 1] - cy, sb[4 * i + 2] - cz) + sb[4 * i + 3]);
    gb[4 * g] = cx; gb[4 * g + 1] = cy; gb[4 * g + 2] = cz; gb[4 * g + 3] = r * (1 + 1e-9) + 1e-9;
  }
  const A3 = [0, 0, 0], B3 = [0, 0, 0];
  // (one span's distance: the round cone between its ends -- or, an ellipse, its section's at the foot on the span)
  const spanD = (i, x, y, z) => {
    const j = i + 1;
    if (!ell) { A3[0] = px[3 * i]; A3[1] = px[3 * i + 1]; A3[2] = px[3 * i + 2]; B3[0] = px[3 * j]; B3[1] = px[3 * j + 1]; B3[2] = px[3 * j + 2];
      return roundCone(x, y, z, A3, B3, pr[i], pr[j]); }
    const ex = px[3 * j] - px[3 * i], ey = px[3 * j + 1] - px[3 * i + 1], ez = px[3 * j + 2] - px[3 * i + 2], l2 = ex * ex + ey * ey + ez * ez || 1e-18;
    const vx0 = x - px[3 * i], vy0 = y - px[3 * i + 1], vz0 = z - px[3 * i + 2], t0 = (vx0 * ex + vy0 * ey + vz0 * ez) / l2, t = clamp01(t0);
    const r = pr[i] + (pr[j] - pr[i]) * t, a = pa[i] + (pa[j] - pa[i]) * t;
    const vx = vx0 - ex * t, vy = vy0 - ey * t, vz = vz0 - ez * t, il = 1 / Math.sqrt(l2), tx = ex * il, ty = ey * il, tz = ez * il;
    let ux = pu[3 * i] + (pu[3 * j] - pu[3 * i]) * t, uy = pu[3 * i + 1] + (pu[3 * j + 1] - pu[3 * i + 1]) * t, uz = pu[3 * i + 2] + (pu[3 * j + 2] - pu[3 * i + 2]) * t;
    const ud = ux * tx + uy * ty + uz * tz; ux -= tx * ud; uy -= ty * ud; uz -= tz * ud;
    const ul = Math.sqrt(ux * ux + uy * uy + uz * uz) || 1; ux /= ul; uy /= ul; uz /= ul;
    const wx = ty * uz - tz * uy, wy = tz * ux - tx * uz, wz = tx * uy - ty * ux;
    const cu = vx * ux + vy * uy + vz * uz, cw = vx * wx + vy * wy + vz * wz, ca = vx * tx + vy * ty + vz * tz;
    const rw = Math.max(r, 1e-7), ru = rw * a, rt = Math.min(rw, ru);   // (past a span's end: an ellipsoid, its length its least radius)
    const k0 = hyp3(cw / rw, cu / ru, ca / rt), k1 = hyp3(cw / (rw * rw), cu / (ru * ru), ca / (rt * rt));
    return k1 < 1e-12 ? -rt : k0 * (k0 - 1) / k1;
  };
  const glb = new Float64Array(ng), off = (lb, r, mm) => lb - mm > 1e-6 * (r + Math.abs(lb)) + 1e-9;
  let last = 0;   // (the span the last distance was nearest: its arc position for the attributes, at(); -1 none)
  q.d = (x, y, z) => {
    let lo = Infinity, j = 0;
    for (let g = 0; g < ng; g++) {
      const lb = hyp3(x - gb[4 * g], y - gb[4 * g + 1], z - gb[4 * g + 2]) - gb[4 * g + 3];
      glb[g] = lb;
      if (lb < lo) { lo = lb; j = g; }
    }
    let mm = Infinity, bi = 0;
    for (let t = 0; t < ng; t++) {
      const g = t === 0 ? j : t <= j ? t - 1 : t;
      if (t && off(glb[g], gb[4 * g + 3], mm)) continue;
      for (let i = g * G, i1 = Math.min(ns, i + G); i < i1; i++) {
        const r = sb[4 * i + 3], lb = hyp3(x - sb[4 * i], y - sb[4 * i + 1], z - sb[4 * i + 2]) - r;
        if (off(lb, r, mm)) continue;
        const d = spanD(i, x, y, z);
        if (d < mm) { mm = d; bi = i; }
      }
    }
    // (the arc position of the foot on the nearest span)
    const i = bi, k = i + 1, ex = px[3 * k] - px[3 * i], ey = px[3 * k + 1] - px[3 * i + 1], ez = px[3 * k + 2] - px[3 * i + 2];
    const t = clamp01(((x - px[3 * i]) * ex + (y - px[3 * i + 1]) * ey + (z - px[3 * i + 2]) * ez) / (ex * ex + ey * ey + ez * ez || 1e-18));
    last = ps[i] + (ps[k] - ps[i]) * t;
    return mm;
  };
  // (its ATTRIBUTES at that arc position: the base's, the chain's bones weighted along it, its bands' colour)
  if (q.at && (p.chainIdx || p.bandsRGB)) {
    const base = q.at, buf = Float64Array.from(base), wts = new Float64Array((p.knots?.length ?? 0) + 1), col = [0, 0, 0];
    const e = p.bandEdge ?? Math.max(1e-4, (p.kc ?? 0) || pr[0] * .15);
    q.atf = () => {
      if (p.chainIdx) { sweepWeights(p.knots, last, wts); for (const ix of p.chainIdx) buf[ix] = 0; p.chainIdx.forEach((ix, b) => { buf[ix] += wts[b]; }); }
      if (p.bandsRGB) { sweepColour(p.bandsRGB, last, L, e, base, col); buf[0] = col[0]; buf[1] = col[1]; buf[2] = col[2]; }
      return buf;
    };
  }
  let lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < n; i++) { const rr = pr[i] * Math.max(1, pa[i]); for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], px[3 * i + k] - rr); hi[k] = Math.max(hi[k], px[3 * i + k] + rr); } }
  q.bc = lo.map((v, k) => (v + hi[k]) / 2); q.br = Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) / 2;
}

// a primitive made ready: its distance function and a bounding sphere (what lets a far point skip it)
function prepare(p) {
  const q = { k: Math.max(0, p.k ?? 0), sub: p.op === "sub", paint: p.op === "paint", at: p.attr ?? null, src: p };
  q.kc = Math.min(q.k, Math.max(0, p.kc ?? q.k));   // (its PAINT's blend: sharper than its shape's, if it says -- field's `sharp` attributes)
  if (q.paint) q.kc = Math.max(0, p.kc ?? 0);   // (a PAINT, op "paint": no shape at all -- the surface inside it takes its colour, softened kc either side of its edge)
  if (p.type === "sphere") { const c = p.c, r = p.r, c0 = c[0], c1 = c[1], c2 = c[2]; q.d = (x, y, z) => hyp3(x - c0, y - c1, z - c2) - r; q.bc = c; q.br = r; }
  else if (p.type === "ell") {
    // (the bound of Quilez's: |p/r| (|p/r| - 1) / |p/r^2| -- near the surface a distance, further off a fair one)
    // (`axes`: its frame given outright, three unit vectors -- a converted part's, posed by its bones -- instead of `rot`)
    const c = p.c, [ra, rb, rc] = p.r, R = p.axes ? [p.axes[0][0], p.axes[1][0], p.axes[2][0], p.axes[0][1], p.axes[1][1], p.axes[2][1], p.axes[0][2], p.axes[1][2], p.axes[2][2]]
                                                  : p.rot ? rotM(p.rot) : null;
    const c0 = c[0], c1 = c[1], c2 = c[2], ra2 = ra * ra, rb2 = rb * rb, rc2 = rc * rc, rmin = -Math.min(ra, rb, rc);
    q.d = R ? (x, y, z) => {   // (toLocal's arithmetic, inline)
      const u0 = x - c0, v0 = y - c1, w0 = z - c2;
      const u = R[0] * u0 + R[3] * v0 + R[6] * w0, v = R[1] * u0 + R[4] * v0 + R[7] * w0, w = R[2] * u0 + R[5] * v0 + R[8] * w0;
      const k0 = hyp3(u / ra, v / rb, w / rc), k1 = hyp3(u / ra2, v / rb2, w / rc2);
      return k1 < 1e-12 ? rmin : k0 * (k0 - 1) / k1;
    } : (x, y, z) => {
      const u = x - c0, v = y - c1, w = z - c2;
      const k0 = hyp3(u / ra, v / rb, w / rc), k1 = hyp3(u / ra2, v / rb2, w / rc2);
      return k1 < 1e-12 ? rmin : k0 * (k0 - 1) / k1;
    };
    q.bc = c; q.br = Math.max(ra, rb, rc);
  } else if (p.type === "box") {
    const c = p.c, [ra, rb, rc] = p.r, rd = p.round ?? 0, R = p.rot ? rotM(p.rot) : null;
    q.d = (x, y, z) => {
      let u = x - c[0], v = y - c[1], w = z - c[2];
      if (R) { const u0 = u, v0 = v, w0 = w; u = R[0] * u0 + R[3] * v0 + R[6] * w0; v = R[1] * u0 + R[4] * v0 + R[7] * w0; w = R[2] * u0 + R[5] * v0 + R[8] * w0; }
      const ex = Math.abs(u) - ra + rd, ey = Math.abs(v) - rb + rd, ez = Math.abs(w) - rc + rd;
      return hyp3(Math.max(ex, 0), Math.max(ey, 0), Math.max(ez, 0)) + Math.min(Math.max(ex, ey, ez), 0) - rd;
    };
    q.bc = c; q.br = Math.hypot(ra, rb, rc);
  } else if (p.type === "cone") {
    const { a, b, ra, rb } = p;
    q.d = (x, y, z) => roundCone(x, y, z, a, b, ra, rb);
    q.bc = a.map((v, k) => (v + b[k]) / 2); q.br = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) / 2 + Math.max(ra, rb);
  } else if (p.type === "tube") {
    const per = p.per ?? 5, segs = tubeSegments(p.pts, per), ns = segs.length, ng = Math.ceil(ns / per);
    // (each span's bounding sphere, and each group of `per` spans' (one stretch between two of its points): the group
    //  nearest by its sphere measured first, then only the groups and spans whose spheres are not further than the
    //  nearest found -- by more than any rounding of their own distances: the minimum of the rest cannot be theirs. A
    //  minimum is the same whatever the order it is taken in, so this is the very same number, found in fewer steps)
    const sb = new Float64Array(4 * ns), gb = new Float64Array(4 * ng);
    segs.forEach(([A, B], i) => { sb[4 * i] = (A[0] + B[0]) / 2; sb[4 * i + 1] = (A[1] + B[1]) / 2; sb[4 * i + 2] = (A[2] + B[2]) / 2;
                                   sb[4 * i + 3] = Math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2 + (B[2] - A[2]) ** 2) / 2 + Math.max(A[3], B[3]); });
    for (let g = 0; g < ng; g++) {
      const i0 = g * per, i1 = Math.min(ns, i0 + per);
      let cx = 0, cy = 0, cz = 0;
      for (let i = i0; i < i1; i++) { cx += sb[4 * i]; cy += sb[4 * i + 1]; cz += sb[4 * i + 2]; }
      cx /= i1 - i0; cy /= i1 - i0; cz /= i1 - i0;
      let r = 0;
      for (let i = i0; i < i1; i++) r = Math.max(r, Math.sqrt((sb[4 * i] - cx) ** 2 + (sb[4 * i + 1] - cy) ** 2 + (sb[4 * i + 2] - cz) ** 2) + sb[4 * i + 3]);
      gb[4 * g] = cx; gb[4 * g + 1] = cy; gb[4 * g + 2] = cz; gb[4 * g + 3] = r * (1 + 1e-9);
    }
    const span = (i, x, y, z) => { const S = segs[i], A = S[0], B = S[1]; return roundCone(x, y, z, A, B, A[3], B[3]); };
    const glb = new Float64Array(ng), off = (lb, r, m) => lb - m > 1e-6 * (r + Math.abs(lb)) + 1e-9;
    q.d = (x, y, z) => {
      let lo = Infinity, j = 0;
      for (let g = 0; g < ng; g++) {
        const dx = x - gb[4 * g], dy = y - gb[4 * g + 1], dz = z - gb[4 * g + 2], lb = Math.sqrt(dx * dx + dy * dy + dz * dz) - gb[4 * g + 3];
        glb[g] = lb;
        if (lb < lo) { lo = lb; j = g; }
      }
      let m = Infinity;
      for (let t = 0; t < ng; t++) {
        const g = t === 0 ? j : t <= j ? t - 1 : t;   // (the nearest group first, then the others in order)
        if (t && off(glb[g], gb[4 * g + 3], m)) continue;
        for (let i = g * per, i1 = Math.min(ns, i + per); i < i1; i++) {
          const dx = x - sb[4 * i], dy = y - sb[4 * i + 1], dz = z - sb[4 * i + 2], r = sb[4 * i + 3], lb = Math.sqrt(dx * dx + dy * dy + dz * dz) - r;
          if (off(lb, r, m)) continue;
          const d = span(i, x, y, z);
          if (d < m) m = d;
        }
      }
      return m;
    };
    const lo = [0, 1, 2].map((k) => Math.min(...p.pts.map((t) => t[k] - t[3]))), hi = [0, 1, 2].map((k) => Math.max(...p.pts.map((t) => t[k] + t[3])));
    q.bc = lo.map((v, k) => (v + hi[k]) / 2); q.br = Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) / 2;
  } else if (p.type === "sweep") prepareSweep(p, q);
  else if (p.type === "tri") {
    // a TRIANGLE thickened by r: a slab with rounded edges (an ear, a fin, a frill) -- Quilez's exact triangle distance
    const [A, B, C] = [p.a, p.b, p.c], r = p.r ?? 0;
    const sub = (u, v) => [u[0] - v[0], u[1] - v[1], u[2] - v[2]], dt = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
    const cr = (u, v) => [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
    const ba = sub(B, A), cb = sub(C, B), ac = sub(A, C), nor = cr(ba, ac);
    const e0 = cr(ba, nor), e1 = cr(cb, nor), e2 = cr(ac, nor), nn = dt(nor, nor);
    const seg = (pa, e) => { const t = Math.max(0, Math.min(1, dt(e, pa) / dt(e, e))); return (e[0] * t - pa[0]) ** 2 + (e[1] * t - pa[1]) ** 2 + (e[2] * t - pa[2]) ** 2; };
    q.d = (x, y, z) => {
      const pa = [x - A[0], y - A[1], z - A[2]], pb = [x - B[0], y - B[1], z - B[2]], pc = [x - C[0], y - C[1], z - C[2]];
      const inside = Math.sign(dt(e0, pa)) + Math.sign(dt(e1, pb)) + Math.sign(dt(e2, pc)) < 2;
      const d2 = inside ? Math.min(seg(pa, ba), seg(pb, cb), seg(pc, ac)) : dt(nor, pa) ** 2 / nn;
      return Math.sqrt(d2) - r;
    };
    q.bc = [0, 1, 2].map((k) => (A[k] + B[k] + C[k]) / 3);
    q.br = Math.max(...[A, B, C].map((P) => Math.hypot(P[0] - q.bc[0], P[1] - q.bc[1], P[2] - q.bc[2]))) + r;
  } else throw new Error(`sculpt: no primitive "${p.type}"`);
  // LUMPS (a fleece): the surface heaped in rounded bumps `size` across, `amp` high -- a cellular field (each cell's
  // nearest jittered point), so they read as tufts, not waves
  if (p.lumps) {
    const { amp, size } = p.lumps, d0 = q.d, inv = 1 / size;
    const h = (i, j, k, s) => { let v = Math.imul(i, 374761393) + Math.imul(j, 668265263) + Math.imul(k, 2147483647) + s * 1013904223; v = Math.imul(v ^ (v >>> 13), 1274126177); return ((v ^ (v >>> 16)) >>> 0) / 4294967296; };
    q.d = (x, y, z) => {
      const b = d0(x, y, z);
      if (b > amp * 2 || b < -amp * 4) return b;
      const u = x * inv, v = y * inv, w = z * inv, i0 = Math.floor(u), j0 = Math.floor(v), k0 = Math.floor(w);
      let m = 9;
      for (let i = i0 - 1; i <= i0 + 1; i++) for (let j = j0 - 1; j <= j0 + 1; j++) for (let k = k0 - 1; k <= k0 + 1; k++) {
        const dx = i + h(i, j, k, 1) - u, dy = j + h(i, j, k, 2) - v, dz = k + h(i, j, k, 3) - w, e = dx * dx + dy * dy + dz * dz;
        if (e < m) m = e;
      }
      return b - amp * (1 - Math.min(1, Math.sqrt(m) * 1.4));
    };
    q.br += amp;
  }
  return q;
}

// ---- the field ----------------------------------------------------------------------------------------------------
// field(prims, L): { dist(x, y, z), at(x, y, z, out) -> distance with the attributes (L numbers) written to out, box }
// (the first `sharp` attributes -- a body's paint -- blend by each primitive's kc, the rest by its k: a white muzzle
//  keeps its edge on a smoothly blended head, while the bones' weights still fade softly across the joint)
export function field(prims, L = 0, { sharp = 0 } = {}) {
  const P = prims.map(prepare), n = P.length;
  // (the bounding spheres in one array, for the test every sample makes of every primitive)
  const BS = new Float64Array(4 * n);
  P.forEach((q, i) => { BS[4 * i] = q.bc[0]; BS[4 * i + 1] = q.bc[1]; BS[4 * i + 2] = q.bc[2]; BS[4 * i + 3] = q.br; });
  // (too far off to change anything: a union's no nearer than d + k, a carving's no deeper than its k past -d -- its
  //  bounding sphere's distance by a plain square root; only a point within TOL of the threshold asks hypot's bits,
  //  so the test decides exactly as `hypot(...) - br` did)
  const far = (q, i, x, y, z, d) => {
    const dx = x - BS[4 * i], dy = y - BS[4 * i + 1], dz = z - BS[4 * i + 2], br = BS[4 * i + 3], e = Math.sqrt(dx * dx + dy * dy + dz * dz);
    const g = q.sub ? (e - br) - (q.k - d) : (e - br - d) - q.k, tol = TOL * (e + br + Math.abs(d) + q.k);
    if (g > tol) return true;
    if (!(g > -tol)) return false;
    const lb = hyp3(dx, dy, dz) - br;
    return q.sub ? lb >= q.k - d : lb - d >= q.k;
  };
  const dist = (x, y, z) => {
    let d = Infinity;
    for (let i = 0; i < n; i++) {
      const q = P[i];
      if (q.paint) continue;   // (a paint is no shape)
      if (i && far(q, i, x, y, z, d)) continue;
      const b = q.d(x, y, z);
      if (!i) { d = q.sub ? -b : b; continue; }
      if (q.sub) {
        if (q.k > 0) { const h = clamp01(.5 - .5 * (d + b) / q.k); d = d + (-b - d) * h + q.k * h * (1 - h); }
        else d = Math.max(d, -b);
      } else if (q.k > 0) { const h = clamp01(.5 + .5 * (b - d) / q.k); d = b + (d - b) * h - q.k * h * (1 - h); }
      else d = Math.min(d, b);
    }
    return d;
  };
  const at = (x, y, z, out) => {
    let d = Infinity;
    for (let i = 0; i < n; i++) {
      const q = P[i];
      if (q.paint) {   // (only the paint: wherever the point is inside it, kc either side of its edge to fade over; the shape and the bones' weights as they were)
        if (!q.at || hyp3(x - q.bc[0], y - q.bc[1], z - q.bc[2]) - q.br >= q.kc) continue;
        const b = q.d(x, y, z), hc = q.kc > 0 ? clamp01(.5 + .5 * b / q.kc) : (b < 0 ? 0 : 1);
        if (hc < 1) for (let k = 0; k < sharp; k++) out[k] = q.at[k] + (out[k] - q.at[k]) * hc;
        continue;
      }
      if (i && far(q, i, x, y, z, d)) continue;
      const b = q.d(x, y, z), qa = q.atf ? q.atf() : q.at;   // (a sweep's attributes: where along it the point is nearest)
      let h, hc;   // how much of what came before stays (1: all of it) -- of its shape's attributes, and of its paint
      if (!i) { d = q.sub ? -b : b; if (qa) for (let k = 0; k < L; k++) out[k] = qa[k]; continue; }
      if (q.sub) {
        if (q.k > 0) { const s = clamp01(.5 - .5 * (d + b) / q.k); d = d + (-b - d) * s + q.k * s * (1 - s); h = 1 - s; }
        else { h = -b > d ? 0 : 1; d = Math.max(d, -b); }
        if (!q.at) continue;   // (a carving with no attributes of its own: the surface it opens keeps the one it cut)
      } else if (q.k > 0) { h = clamp01(.5 + .5 * (b - d) / q.k); hc = q.kc > 0 ? clamp01(.5 + .5 * (b - d) / q.kc) : (b < d ? 0 : 1); d = b + (d - b) * h - q.k * h * (1 - h); }
      else { h = hc = b < d ? 0 : 1; d = Math.min(d, b); }
      if (q.sub) hc = h;
      if (qa && h < 1) for (let k = sharp; k < L; k++) out[k] = qa[k] + (out[k] - qa[k]) * h;
      if (qa && hc < 1) for (let k = 0; k < sharp; k++) out[k] = qa[k] + (out[k] - qa[k]) * hc;
    }
    return d;
  };
  // the box round it all: every primitive's bounding sphere (a carving takes nothing out of it)
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (const q of P) if (!q.sub && !q.paint) for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], q.bc[k] - q.br); hi[k] = Math.max(hi[k], q.bc[k] + q.br); }
  return { dist, at, box: { lo, hi }, prims: P };   // (prims: each one's own distance `d`, for whoever needs to know which is nearest)
}

// the field's gradient, by central differences (e metres apart), normalised; and a point brought onto the surface
export function gradient(dist, x, y, z, e = 2e-4) {
  const gx = dist(x + e, y, z) - dist(x - e, y, z), gy = dist(x, y + e, z) - dist(x, y - e, z), gz = dist(x, y, z + e) - dist(x, y, z - e);
  const l = Math.hypot(gx, gy, gz) || 1;
  return [gx / l, gy / l, gz / l];
}
export function onSurface(dist, p, steps = 3, e = 2e-4) {
  let [x, y, z] = p;
  for (let s = 0; s < steps; s++) {
    const d = dist(x, y, z);
    if (Math.abs(d) < 1e-6) break;
    const gx = (dist(x + e, y, z) - dist(x - e, y, z)) / (2 * e), gy = (dist(x, y + e, z) - dist(x, y - e, z)) / (2 * e), gz = (dist(x, y, z + e) - dist(x, y, z - e)) / (2 * e);
    const g2 = gx * gx + gy * gy + gz * gz;
    if (g2 < 1e-10) break;
    x -= d * gx / g2; y -= d * gy / g2; z -= d * gz / g2;
  }
  return [x, y, z];
}

// ---- SURFACE NETS -------------------------------------------------------------------------------------------------
// dist sampled every `cell` over box (padded two cells): { pos: Float64Array, tri: Int32Array } -- faces wound outward
// (counter-clockwise seen from outside), the mesh closed wherever the shape lies inside the box.
// `half` (a field that is its own mirror image in z -- mirrorOf below): only its +z HALF, sampled on a grid whose middle
// layer of cells straddles z = 0 (samples at z = +-cell/2, +-3cell/2 ...), the layer at -cell/2 a copy of the one at
// +cell/2 -- so no grid edge crosses the plane, every face lies on the +z side, and the vertices of that middle layer
// lie exactly ON the plane (z = 0, flagged in `mid`): the half's open boundary, along the midline. mirrorMesh makes it whole.
export function surfaceNets(dist, box, cell, { half = false } = {}) {
  const lo = box.lo.slice(), hi = box.hi.slice();
  if (half) { hi[2] = Math.max(hi[2], -lo[2]); lo[2] = 0; }
  const o = lo.map((v) => v - 2 * cell), n = hi.map((v, k) => Math.ceil((v + 2 * cell - o[k]) / cell) + 1);
  if (half) { o[2] = -cell / 2; n[2] = Math.ceil((hi[2] + 2 * cell - o[2]) / cell) + 1; }
  const [nx, ny, nz] = n, sxy = nx * ny, f = new Float32Array(nx * ny * nz), k0 = half ? 1 : 0;
  // (a NARROW BAND: the field first every S cells; a sample whose nearest coarse one is further from the surface than
  //  it can be from that sample -- the field's slope is about one -- takes that one's value: only the sign matters there)
  // (the half: its coarse grid from the layer at +cell/2 up, and the layer below it -- at -cell/2 -- that layer's copy)
  const S = 4, mx = Math.ceil((nx - 1) / S) + 1, my = Math.ceil((ny - 1) / S) + 1, mz = Math.ceil((nz - 1 - k0) / S) + 1, g = new Float32Array(mx * my * mz);
  for (let k = 0; k < mz; k++) for (let j = 0; j < my; j++) for (let i = 0; i < mx; i++)
    g[i + mx * (j + my * k)] = dist(o[0] + i * S * cell, o[1] + j * S * cell, o[2] + (k * S + k0) * cell);
  const band = S * cell * 1.25;
  const ri = Int32Array.from({ length: nx }, (_, i) => Math.round(i / S)), rj = Int32Array.from({ length: ny }, (_, j) => mx * Math.round(j / S));
  for (let k = k0; k < nz; k++) { const rk = mx * my * Math.round((k - k0) / S); for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const c = g[ri[i] + rj[j] + rk];
    f[i + nx * j + sxy * k] = Math.abs(c) > band ? c : dist(o[0] + i * cell, o[1] + j * cell, o[2] + k * cell);
  } }
  if (half) f.copyWithin(0, sxy, 2 * sxy);
  // (2026-11-08: the same vertices and faces in the same order as ever, found faster -- each cell's corners read by
  //  their offsets, and the faces looked for only along the stretch of each row that has cells with vertices)
  const cx = nx - 1, cy = ny - 1, cxy = cx * cy, vid = new Int32Array(cx * cy * (nz - 1)).fill(-1), pos = [], mid = [];
  const COx = [0, 1, 0, 1, 0, 1, 0, 1], COy = [0, 0, 1, 1, 0, 0, 1, 1], COz = [0, 0, 0, 0, 1, 1, 1, 1];
  const EA = [0, 2, 4, 6, 0, 1, 4, 5, 0, 1, 2, 3], EB = [1, 3, 5, 7, 2, 3, 6, 7, 4, 5, 6, 7];
  const OFF = COx.map((a, c) => a + nx * COy[c] + sxy * COz[c]);
  const v8 = new Float32Array(8);
  const rowLo = new Int32Array(cy * (nz - 1)).fill(cx), rowHi = new Int32Array(cy * (nz - 1)).fill(-1);   // (each row of cells: its first and last with a vertex)
  for (let k = 0; k < nz - 1; k++) for (let j = 0; j < ny - 1; j++) {
    const r = j + cy * k;
    for (let i = 0; i < nx - 1; i++) {
      const b0 = i + nx * j + sxy * k;
      let m = 0;
      for (let c = 0; c < 8; c++) { const v = f[b0 + OFF[c]]; v8[c] = v; if (v < 0) m |= 1 << c; }
      if (m === 0 || m === 255) continue;
      let sx = 0, sy = 0, sz = 0, cnt = 0;
      for (let e = 0; e < 12; e++) {
        const a = EA[e], b = EB[e];
        if (((m >> a) & 1) === ((m >> b) & 1)) continue;
        const t = v8[a] / (v8[a] - v8[b]);
        sx += COx[a] + (COx[b] - COx[a]) * t; sy += COy[a] + (COy[b] - COy[a]) * t; sz += COz[a] + (COz[b] - COz[a]) * t; cnt++;
      }
      vid[i + cx * j + cxy * k] = pos.length / 3;
      pos.push(o[0] + (i + sx / cnt) * cell, o[1] + (j + sy / cnt) * cell, half && k === 0 ? 0 : o[2] + (k + sz / cnt) * cell);
      if (half) mid.push(k === 0 ? 1 : 0);
      if (i < rowLo[r]) rowLo[r] = i;
      rowHi[r] = i;
    }
  }
  const tri = [];
  // a quad a..d (counter-clockwise about the edge's axis when its low end is inside), split on its shorter diagonal
  const L = (p, q) => (pos[3 * p] - pos[3 * q]) ** 2 + (pos[3 * p + 1] - pos[3 * q + 1]) ** 2 + (pos[3 * p + 2] - pos[3 * q + 2]) ** 2;
  const quad = (a, b, c, d, flip) => {
    if (a < 0 || b < 0 || c < 0 || d < 0) return;
    if (flip) { const t = b; b = d; d = t; }
    if (L(a, c) <= L(b, d)) tri.push(a, b, c, a, c, d); else tri.push(a, b, d, b, c, d);
  };
  for (let k = 0; k < nz; k++) for (let j = 0; j < ny; j++) {
    // (a face needs the four cells round its edge to have vertices: those of the cell rows (j-1|j, k-1|k))
    let lo = cx, hi = -1;
    for (let dk = -1; dk <= 0; dk++) for (let dj = -1; dj <= 0; dj++) {
      const jj = j + dj, kk = k + dk;
      if (jj < 0 || kk < 0 || jj >= cy || kk >= nz - 1) continue;
      const r = jj + cy * kk;
      if (rowLo[r] < lo) lo = rowLo[r];
      if (rowHi[r] > hi) hi = rowHi[r];
    }
    if (hi < 0) continue;
    const iEnd = Math.min(nx - 1, hi + 1);
    for (let i = lo; i <= iEnd; i++) {
      const at = i + nx * j + sxy * k, f0 = f[at] < 0;
      // (x edge: the cells round it in y and z -- y x z is x; y edge: z then x; z edge: x then y)
      if (i < nx - 1 && j > 0 && k > 0 && j < ny - 1 && k < nz - 1 && f0 !== (f[at + 1] < 0))
        quad(vid[i + cx * (j - 1) + cxy * (k - 1)], vid[i + cx * j + cxy * (k - 1)], vid[i + cx * j + cxy * k], vid[i + cx * (j - 1) + cxy * k], !f0);
      if (j < ny - 1 && i > 0 && k > 0 && i < nx - 1 && k < nz - 1 && f0 !== (f[at + nx] < 0))
        quad(vid[i - 1 + cx * j + cxy * (k - 1)], vid[i - 1 + cx * j + cxy * k], vid[i + cx * j + cxy * k], vid[i + cx * j + cxy * (k - 1)], !f0);
      if (k < nz - 1 && i > 0 && j > 0 && i < nx - 1 && j < ny - 1 && f0 !== (f[at + sxy] < 0))
        quad(vid[i - 1 + cx * (j - 1) + cxy * k], vid[i + cx * (j - 1) + cxy * k], vid[i + cx * j + cxy * k], vid[i - 1 + cx * j + cxy * k], !f0);
    }
  }
  if (!half) return { pos: Float64Array.from(pos), tri: Int32Array.from(tri) };
  // (the half: its vertices that no face uses dropped -- a sign change only in the copied layer, at the box's rim)
  const used = new Uint8Array(mid.length), map = new Int32Array(mid.length).fill(-1), P = [], Mid = [];
  for (const v of tri) used[v] = 1;
  for (let v = 0; v < mid.length; v++) if (used[v]) { map[v] = Mid.length; Mid.push(mid[v]); P.push(pos[3 * v], pos[3 * v + 1], pos[3 * v + 2]); }
  return { pos: Float64Array.from(P), tri: Int32Array.from(tri, (v) => map[v]), mid: Uint8Array.from(Mid) };
}

// ---- THE MIRROR ---------------------------------------------------------------------------------------------------
// MIRROR-SYMMETRIC BODIES (2026-11-08). Nearly every animal is its own mirror image across z = 0 (x forward, y up): its
// left half is its right half reflected. Such a body is meshed as its +z half only -- half the field's samples, half
// the faces to simplify -- with the vertices on the midline held IN the plane all the way through the simplification,
// and then reflected: the two halves share the midline's vertices (no crack can open there), and the mesh is exactly
// symmetric, where a whole mesh simplified greedily is not (its collapses take one side's edge before the other's
// twin, and a coarse budget leaves one flank cut differently from the other). Only the SHAPE is mirrored: every vertex's
// attributes -- its bones' weights (a left leg's vertex weighted to the left leg), its paint -- are still read from the
// field where the vertex really is, so a zebra's stripes on its left are not its right's.
//
// mirrorOf(F, cell): is the field F's shape its own mirror image? Asked of the primitives, not of samples (a sampled
// test cannot tell the small difference the ORDER of blending makes -- smin(smin(body, left), right) is not quite
// smin(smin(body, right), left) where the two legs both reach the belly -- from a deliberately one-sided mane or
// tusk): every shape must have a twin, the same primitive reflected (or be its own: a sphere on the plane, an ellipsoid
// whose axes the reflection only re-signs, a cone whose ends it swaps), within `tol` of a cell. A fleece's lumps are
// noise, not mirrored: a body with them is not symmetric. -> { ok, why } (why: the first shape without a twin).
const M3 = (v) => [v[0], v[1], -(v[2] ?? 0)];
export function mirrorOf(F, cell, tol = .02) {
  const e = cell * tol, near = (a, b) => Math.abs(a - b) <= e, nearV = (a, b) => near(a[0], b[0]) && near(a[1], b[1]) && near(a[2] ?? 0, b[2] ?? 0);
  // (an ellipsoid's or a box's frame: three axes, each up to its sign, with its radius)
  const frame = (p) => { const R = p.axes ? p.axes : p.rot ? (() => { const m = rotM(p.rot); return [[m[0], m[3], m[6]], [m[1], m[4], m[7]], [m[2], m[5], m[8]]]; })() : [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    return R.map((ax, i) => [ax, p.r[i]]); };
  const sameFrame = (A, B) => A.every(([ax, r]) => B.some(([bx, br]) => near(r, br) && Math.abs(Math.abs(ax[0] * bx[0] + ax[1] * bx[1] + ax[2] * bx[2]) - 1) < 1e-4));
  const twin = (p, q) => {   // (is q the reflection of p?)
    if (p.type !== q.type || (p.op ?? "") !== (q.op ?? "") || !near(p.k ?? 0, q.k ?? 0) || !near(p.kc ?? p.k ?? 0, q.kc ?? q.k ?? 0)) return false;
    switch (p.type) {
      case "sphere": return near(p.r, q.r) && nearV(M3(p.c), q.c);
      case "ell": case "box": return nearV(M3(p.c), q.c) && near(p.round ?? 0, q.round ?? 0) && sameFrame(frame(p).map(([ax, r]) => [M3(ax), r]), frame(q));
      case "cone": return (nearV(M3(p.a), q.a) && nearV(M3(p.b), q.b) && near(p.ra, q.ra) && near(p.rb, q.rb))
                       || (nearV(M3(p.a), q.b) && nearV(M3(p.b), q.a) && near(p.ra, q.rb) && near(p.rb, q.ra));
      case "tube": { if (p.pts.length !== q.pts.length || (p.per ?? 5) !== (q.per ?? 5)) return false;
        const m = p.pts.map((t) => [...M3(t), t[3]]), eq = (A) => A.every((t, i) => nearV(t, q.pts[i]) && near(t[3], q.pts[i][3]));
        return eq(m) || eq(m.slice().reverse()); }
      case "sweep": { if (p.pts.length !== q.pts.length || (p.end ?? "") !== (q.end ?? "") || !near(p.shrinkBy ?? 0, q.shrinkBy ?? 0) || !near(p.aspect ?? 1, q.aspect ?? 1)
                        || JSON.stringify(p.cut ?? null) !== JSON.stringify(q.cut ?? null) || JSON.stringify(p.shrink ?? null) !== JSON.stringify(q.shrink ?? null)) return false;
        if (p.up && q.up ? !nearV(M3(p.up), q.up) : !!p.up !== !!q.up) return false;
        return p.pts.every((t, i) => nearV(M3(t), q.pts[i]) && near(t[3], q.pts[i][3]) && near(t[4] ?? 1, q.pts[i][4] ?? 1)); }
      case "tri": { if (!near(p.r ?? 0, q.r ?? 0)) return false; const m = [p.a, p.b, p.c].map(M3);
        return [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]].some((o) => o.every((i, j) => nearV(m[i], [q.a, q.b, q.c][j]))); }
    }
    return false;
  };
  const P = F.prims.filter((q) => !q.paint).map((q) => q.src), used = new Uint8Array(P.length);
  for (let i = 0; i < P.length; i++) {
    const p = P[i];
    if (p.lumps) return { ok: false, why: `lumps on a ${p.type}` };
    if (twin(p, p)) continue;
    let j = -1;
    for (let t = 0; t < P.length; t++) if (t !== i && !used[t] && twin(p, P[t])) { j = t; break; }
    if (j < 0) return { ok: false, why: `${p.type} ${p.id ?? i} (${p.bone ?? ""}) has no twin` };
    used[j] = 1;
  }
  return { ok: true };
}

// the half made whole: the vertices off the plane reflected (z -> -z), the midline's shared, the reflected faces wound
// the other way (outward still). `twin`: each vertex's reflection (itself on the midline) -- finish keeps them exact
export function mirrorMesh({ pos, tri, mid }) {
  const n = mid.length, twin = new Int32Array(2 * n), P = new Float64Array(6 * n);
  P.set(pos);
  let m = n;
  for (let v = 0; v < n; v++) {
    if (mid[v]) { twin[v] = v; continue; }
    P[3 * m] = pos[3 * v]; P[3 * m + 1] = pos[3 * v + 1]; P[3 * m + 2] = -pos[3 * v + 2];
    twin[v] = m; twin[m] = v; m++;
  }
  const T = new Int32Array(2 * tri.length);
  T.set(tri);
  for (let f = 0; f < tri.length; f += 3) { T[tri.length + f] = twin[tri[f]]; T[tri.length + f + 1] = twin[tri[f + 2]]; T[tri.length + f + 2] = twin[tri[f + 1]]; }
  return { pos: P.slice(0, 3 * m), tri: T, twin: twin.slice(0, m) };
}

// ---- SIMPLIFICATION (quadric error edge collapse) -----------------------------------------------------------------
// to `target` triangles at most; { pos, tri } compacted. A collapse is refused when it would turn a face over (its
// normal more than ~70 degrees from where it was), leave a face thinner than `minQ` (4 sqrt3 area / sum of squared
// edges: 1 equilateral) that was not already, or join two sheets (more than two neighbours shared: the mesh would stop
// being a surface). `lock(v)`: a vertex that must not move (none by default).
// `anchor` (one weight a vertex): a quadric holding it where it is besides -- a body's colour boundaries kept sharp
// (bodymesh.js: a muzzle's edge is in the vertices, and the paint between them is only interpolated). `scale` (one
// factor a vertex): its quadric that many times dearer to move -- a face kept finer than the broad back it is cut
// from (bodymesh.js: the overlay's mesh.focus). `maxEdge` (one length a vertex, 0 none): no collapse leaves an edge
// longer than the lesser of its two ends' -- a silhouette drawn in short segments where a gently curved face would
// otherwise be spanned by a few long ones (the budget may then be overrun: what is refused stays).
// The result's `src`: which of the input's vertices each output vertex was.
// A HALF (surfaceNets' `half`, with its `mid`): its midline stays on the plane -- a collapse that takes a midline vertex
// puts the joined one on the plane (z = 0 exactly), two midline vertices are joined only along the boundary they draw
// (never across the half: the whole would pinch there), no face may come to lie flat in the plane, and nothing else may
// cross it. What a vertex on the plane costs to move counts twice (its reflection moves with it: in the whole mesh its
// quadric is its half's and its twin's), so the budget is spent as the whole mesh would spend it. Its result has `mid` too.
export function simplify({ pos: P0, tri: T0, mid: M0 = null }, target, { minQ = .18, anchor = null, scale = null, maxEdge = null } = {}) {
  // (2026-11-08: the same collapses in the same order as ever -- the heap in typed arrays, the rings by stamps, no
  //  arrays made per test -- in about a third of the time)
  const nv = P0.length / 3, nf0 = T0.length / 3, P = Float64Array.from(P0), T = Int32Array.from(T0), mid = M0 ? Uint8Array.from(M0) : null;
  const fAlive = new Uint8Array(nf0).fill(1), vAlive = new Uint8Array(nv).fill(1), ver = new Int32Array(nv);
  const vf = Array.from({ length: nv }, () => []);
  for (let f = 0; f < nf0; f++) for (let c = 0; c < 3; c++) vf[T[3 * f + c]].push(f);
  const Q = new Float64Array(nv * 10);
  const normal = (a, b, c, out) => {
    const ux = P[3 * b] - P[3 * a], uy = P[3 * b + 1] - P[3 * a + 1], uz = P[3 * b + 2] - P[3 * a + 2];
    const vx = P[3 * c] - P[3 * a], vy = P[3 * c + 1] - P[3 * a + 1], vz = P[3 * c + 2] - P[3 * a + 2];
    out[0] = uy * vz - uz * vy; out[1] = uz * vx - ux * vz; out[2] = ux * vy - uy * vx;
    return hyp3(out[0], out[1], out[2]);
  };
  const nn = [0, 0, 0];
  for (let f = 0; f < nf0; f++) {
    const a = T[3 * f], b = T[3 * f + 1], c = T[3 * f + 2], l = normal(a, b, c, nn);
    if (l < 1e-14) continue;
    const x = nn[0] / l, y = nn[1] / l, z = nn[2] / l, d = -(x * P[3 * a] + y * P[3 * a + 1] + z * P[3 * a + 2]), w = l / 2;   // (area-weighted)
    const K = [x * x, x * y, x * z, x * d, y * y, y * z, y * d, z * z, z * d, d * d];
    for (const v of [a, b, c]) for (let k = 0; k < 10; k++) Q[10 * v + k] += K[k] * w;
  }
  if (scale) for (let v = 0; v < nv; v++) { const f = scale[v]; if (f > 0 && f !== 1) for (let k = 0; k < 10; k++) Q[10 * v + k] *= f; }
  if (anchor) for (let v = 0; v < nv; v++) {
    const w = anchor[v];
    if (!(w > 0)) continue;
    const x = P[3 * v], y = P[3 * v + 1], z = P[3 * v + 2], o = 10 * v;
    Q[o] += w; Q[o + 4] += w; Q[o + 7] += w; Q[o + 3] -= w * x; Q[o + 6] -= w * y; Q[o + 8] -= w * z; Q[o + 9] += w * (x * x + y * y + z * z);
  }
  const q = new Float64Array(10);
  const qerr = (x, y, z) => q[0] * x * x + 2 * q[1] * x * y + 2 * q[2] * x * z + 2 * q[3] * x + q[4] * y * y + 2 * q[5] * y * z + 2 * q[6] * y + q[7] * z * z + 2 * q[8] * z + q[9];
  // the best place for the joined vertex: where the summed quadric is least (solved), else the better of the ends and
  // the middle -- into bC (its cost) and bX, bY, bZ; bOK false when there is none
  let bC = 0, bX = 0, bY = 0, bZ = 0, bOK = false;
  const best = (a, b) => {
    for (let k = 0; k < 10; k++) q[k] = Q[10 * a + k] + Q[10 * b + k];
    if (mid && (mid[a] || mid[b])) return bestOnPlane(a, b);
    const ax = P[3 * a], ay = P[3 * a + 1], az = P[3 * a + 2], bx = P[3 * b], by = P[3 * b + 1], bz = P[3 * b + 2];
    const mx = (ax + bx) / 2, my = (ay + by) / 2, mz = (az + bz) / 2;
    let bc = Infinity; bOK = false;
    const cand = (x, y, z) => { if (mid && !(z > 0)) return; const e = qerr(x, y, z); if (e < bc) { bc = e; bX = x; bY = y; bZ = z; bOK = true; } };   // (a half's: none across the plane)
    cand(ax, ay, az); cand(bx, by, bz); cand(mx, my, mz);
    const A0 = q[0], A1 = q[1], A2 = q[2], A3 = q[1], A4 = q[4], A5 = q[5], A6 = q[2], A7 = q[5], A8 = q[7], r0 = -q[3], r1 = -q[6], r2 = -q[8];
    const det = A0 * (A4 * A8 - A5 * A7) - A1 * (A3 * A8 - A5 * A6) + A2 * (A3 * A7 - A4 * A6);
    if (Math.abs(det) > 1e-18) {
      const s0 = (r0 * (A4 * A8 - A5 * A7) - A1 * (r1 * A8 - A5 * r2) + A2 * (r1 * A7 - A4 * r2)) / det,
            s1 = (A0 * (r1 * A8 - A5 * r2) - r0 * (A3 * A8 - A5 * A6) + A2 * (A3 * r2 - r1 * A6)) / det,
            s2 = (A0 * (A4 * r2 - r1 * A7) - A1 * (A3 * r2 - r1 * A6) + r0 * (A3 * A7 - A4 * A6)) / det;
      // (only near the edge: an ill-posed solve throws the point across the body)
      const el = hyp3(ax - bx, ay - by, az - bz);
      if (hyp3(s0 - mx, s1 - my, s2 - mz) < el) cand(s0, s1, s2);
    }
    bC = Math.max(0, bc);
  };
  // (on the plane: the ends that are on it, the middle of the two brought onto it, and the least of the quadric there --
  //  z = 0, a 2x2 solve; its cost twice the half's)
  const bestOnPlane = (a, b) => {
    let bc = Infinity; bOK = false;
    const cand = (x, y) => { const e = qerr(x, y, 0); if (e < bc) { bc = e; bX = x; bY = y; bZ = 0; bOK = true; } };
    const mx = (P[3 * a] + P[3 * b]) / 2, my = (P[3 * a + 1] + P[3 * b + 1]) / 2;
    cand(mx, my);
    if (mid[a]) cand(P[3 * a], P[3 * a + 1]);
    if (mid[b]) cand(P[3 * b], P[3 * b + 1]);
    const det = q[0] * q[4] - q[1] * q[1];
    if (Math.abs(det) > 1e-18) {
      const sx = (-q[3] * q[4] + q[6] * q[1]) / det, sy = (-q[6] * q[0] + q[3] * q[1]) / det;
      const el = hyp3(P[3 * a] - P[3 * b], P[3 * a + 1] - P[3 * b + 1], P[3 * a + 2] - P[3 * b + 2]);
      if (Math.hypot(sx - mx, sy - my) < el) cand(sx, sy);
    }
    bC = Math.max(0, 2 * bc);
  };
  // a binary heap of (cost, a, b, ver a, ver b, x, y, z): the entries in typed arrays by SLOT (a popped entry's slot
  // used again), the heap itself of slots -- the very order of the heap of arrays it replaced, each step moving one int
  let cap = 1024, H = 0, nSlot = 0, nFree = 0, heap = new Int32Array(cap), free = new Int32Array(cap);
  let ec = new Float64Array(cap), ei = new Int32Array(4 * cap), ep = new Float64Array(3 * cap);
  const grow = () => {
    cap *= 2;
    const h2 = new Int32Array(cap), f2 = new Int32Array(cap), c2 = new Float64Array(cap), i2 = new Int32Array(4 * cap), p2 = new Float64Array(3 * cap);
    h2.set(heap); f2.set(free); c2.set(ec); i2.set(ei); p2.set(ep); heap = h2; free = f2; ec = c2; ei = i2; ep = p2;
  };
  const up = (i) => { const s = heap[i], c = ec[s]; while (i > 0) { const j = (i - 1) >> 1, t = heap[j]; if (ec[t] <= c) break; heap[i] = t; i = j; } heap[i] = s; };
  const down = (i) => {
    const s = heap[i], c = ec[s];
    for (;;) {
      const l = 2 * i + 1, r = l + 1;
      let m = -1, mc = c;
      if (l < H && ec[heap[l]] < mc) { m = l; mc = ec[heap[l]]; }
      if (r < H && ec[heap[r]] < mc) m = r;
      if (m < 0) break;
      heap[i] = heap[m]; i = m;
    }
    heap[i] = s;
  };
  const push = (a, b) => {
    best(a, b);
    if (!bOK) return;
    if (H === cap || nSlot === cap) grow();
    const s = nFree ? free[--nFree] : nSlot++;
    ec[s] = bC; ei[4 * s] = a; ei[4 * s + 1] = b; ei[4 * s + 2] = ver[a]; ei[4 * s + 3] = ver[b]; ep[3 * s] = bX; ep[3 * s + 1] = bY; ep[3 * s + 2] = bZ;
    heap[H++] = s; up(H - 1);
  };
  let pa = 0, pb = 0, pva = 0, pvb = 0, px = 0, py = 0, pz = 0;
  const pop = () => {   // (the top into pa..pz, its slot freed; the last moved to the top and sifted down)
    const s = heap[0];
    pa = ei[4 * s]; pb = ei[4 * s + 1]; pva = ei[4 * s + 2]; pvb = ei[4 * s + 3]; px = ep[3 * s]; py = ep[3 * s + 1]; pz = ep[3 * s + 2];
    free[nFree++] = s;
    H--;
    if (H) { heap[0] = heap[H]; down(0); }
  };
  { const seen = new Set();
    for (let f = 0; f < nf0; f++) for (let c = 0; c < 3; c++) {
      const a = T[3 * f + c], b = T[3 * f + (c + 1) % 3], key = Math.min(a, b) * nv + Math.max(a, b);
      if (!seen.has(key)) { seen.add(key); push(Math.min(a, b), Math.max(a, b)); }
    } }
  // a vertex's ring: its live faces' other corners, each once, in the order they are first met (as a Set kept them)
  const stamp = new Int32Array(nv), stampB = new Int32Array(nv);
  let st = 0, stB = 0;
  const ringInto = (v, out, S, s) => {
    let n = 0;
    S[v] = s;
    for (const f of vf[v]) if (fAlive[f]) for (let c = 0; c < 3; c++) { const u = T[3 * f + c]; if (S[u] !== s) { S[u] = s; out[n++] = u; } }
    return n;
  };
  let RA = new Int32Array(64), RB = new Int32Array(64);
  const fit = (v) => { let m = 0; for (const f of vf[v]) if (fAlive[f]) m += 3; return m; };
  const qual = (ax, ay, az, bx, by, bz, cx, cy, cz) => {
    const ux = bx - ax, uy = by - ay, uz = bz - az, vx = cx - ax, vy = cy - ay, vz = cz - az;
    const A2 = hyp3(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx);
    const s = ux * ux + uy * uy + uz * uz + vx * vx + vy * vy + vz * vz + (cx - bx) ** 2 + (cy - by) ** 2 + (cz - bz) ** 2;
    return s > 0 ? 2 * Math.sqrt(3) * A2 / s : 0;
  };
  const o = [0, 0, 0];
  const ok = (a, b, x, y, z) => {
    let m = Math.max(fit(a), fit(b));
    if (m > RA.length) { RA = new Int32Array(2 * m); RB = new Int32Array(2 * m); }
    const na = ringInto(a, RA, stamp, ++st), nb = ringInto(b, RB, stampB, ++stB);
    let shared = 0; for (let i = 0; i < na; i++) if (stampB[RA[i]] === stB && RA[i] !== b) shared++;
    if (mid && mid[a] && mid[b]) {   // (two on the midline: only along it -- an edge of one face, the half's boundary)
      let nf = 0; for (const f of vf[a]) if (fAlive[f] && (T[3 * f] === b || T[3 * f + 1] === b || T[3 * f + 2] === b)) nf++;
      if (nf !== 1 || shared !== 1) return false;
    } else if (shared !== 2) return false;
    if (mid && (mid[a] || mid[b])) {
      // (the joined vertex on the plane: another midline vertex may then share one face with it at most -- two, and the
      //  whole would meet itself along that edge -- and no face may have all three corners on the plane)
      const cnt = new Map();
      for (const v of [a, b]) for (const f of vf[v]) {
        if (!fAlive[f]) continue;
        const t = [T[3 * f], T[3 * f + 1], T[3 * f + 2]];
        if (t.includes(a) && t.includes(b)) continue;
        const others = t.filter((u) => u !== v);
        if (others.every((u) => mid[u])) return false;
        for (const u of others) if (mid[u]) { const c = (cnt.get(u) ?? 0) + 1; if (c > 1) return false; cnt.set(u, c); }
      }
    }
    if (maxEdge) {
      const lim = (v) => (maxEdge[v] > 0 ? maxEdge[v] : Infinity), la = Math.min(lim(a), lim(b));
      for (let s = 0; s < 2; s++) {
        const R = s ? RB : RA, n = s ? nb : na;
        for (let i = 0; i < n; i++) {
          const v = R[i];
          if (v === a || v === b) continue;
          const L = Math.min(la, lim(v));
          if (L < Infinity && hyp3(P[3 * v] - x, P[3 * v + 1] - y, P[3 * v + 2] - z) > L) return false;
        }
      }
    }
    for (let s = 0; s < 2; s++) {
      const v = s ? b : a;
      for (const f of vf[v]) {
        if (!fAlive[f]) continue;
        const i0 = T[3 * f], i1 = T[3 * f + 1], i2 = T[3 * f + 2];
        if ((i0 === a || i1 === a || i2 === a) && (i0 === b || i1 === b || i2 === b)) continue;   // (it goes)
        const lo = normal(i0, i1, i2, o);
        const c0x = i0 === v ? x : P[3 * i0], c0y = i0 === v ? y : P[3 * i0 + 1], c0z = i0 === v ? z : P[3 * i0 + 2];
        const c1x = i1 === v ? x : P[3 * i1], c1y = i1 === v ? y : P[3 * i1 + 1], c1z = i1 === v ? z : P[3 * i1 + 2];
        const c2x = i2 === v ? x : P[3 * i2], c2y = i2 === v ? y : P[3 * i2 + 1], c2z = i2 === v ? z : P[3 * i2 + 2];
        const ux = c1x - c0x, uy = c1y - c0y, uz = c1z - c0z, vx = c2x - c0x, vy = c2y - c0y, vz = c2z - c0z;
        const m0 = uy * vz - uz * vy, m1 = uz * vx - ux * vz, m2 = ux * vy - uy * vx;
        const ln = hyp3(m0, m1, m2);
        if (ln < 1e-14 || lo < 1e-14) return false;
        if ((o[0] * m0 + o[1] * m1 + o[2] * m2) / (lo * ln) < .35) return false;
        const qn = qual(c0x, c0y, c0z, c1x, c1y, c1z, c2x, c2y, c2z);
        if (qn < minQ && qn < qual(P[3 * i0], P[3 * i0 + 1], P[3 * i0 + 2], P[3 * i1], P[3 * i1 + 1], P[3 * i1 + 2], P[3 * i2], P[3 * i2 + 1], P[3 * i2 + 2])) return false;
      }
    }
    return true;
  };
  let faces = nf0;
  while (faces > target && H) {
    pop();
    const a0 = pa, b0 = pb, x = px, y = py, z = pz;
    if (!vAlive[a0] || !vAlive[b0] || ver[a0] !== pva || ver[b0] !== pvb) continue;
    if (!ok(a0, b0, x, y, z)) continue;
    const swp = mid && mid[b0] && !mid[a0], a = swp ? b0 : a0, b = swp ? a0 : b0;   // (the one on the plane stays)
    P[3 * a] = x; P[3 * a + 1] = y; P[3 * a + 2] = z;
    for (let k = 0; k < 10; k++) Q[10 * a + k] += Q[10 * b + k];
    for (const f of vf[b]) {
      if (!fAlive[f]) continue;
      let hasA = false;
      for (let c = 0; c < 3; c++) if (T[3 * f + c] === a) hasA = true;
      if (hasA) { fAlive[f] = 0; faces--; continue; }
      for (let c = 0; c < 3; c++) if (T[3 * f + c] === b) T[3 * f + c] = a;
      vf[a].push(f);
    }
    vAlive[b] = 0; vf[b] = [];
    vf[a] = vf[a].filter((f) => fAlive[f]);
    ver[a]++;
    const m = fit(a);
    if (m > RA.length) { RA = new Int32Array(2 * m); RB = new Int32Array(2 * m); }
    const n = ringInto(a, RA, stamp, ++st);
    for (let i = 0; i < n; i++) { const v = RA[i]; push(Math.min(a, v), Math.max(a, v)); }
  }
  // compact
  const map = new Int32Array(nv).fill(-1), pos = [], tri = [], src = [], midOut = [];
  for (let f = 0; f < nf0; f++) {
    if (!fAlive[f]) continue;
    for (let c = 0; c < 3; c++) {
      const v = T[3 * f + c];
      if (map[v] < 0) { map[v] = pos.length / 3; pos.push(P[3 * v], P[3 * v + 1], P[3 * v + 2]); src.push(v); if (mid) midOut.push(mid[v]); }
      tri.push(map[v]);
    }
  }
  const out = { pos: Float64Array.from(pos), tri: Int32Array.from(tri), src: Int32Array.from(src) };
  if (mid) out.mid = Uint8Array.from(midOut);
  return out;
}

// ---- the finished mesh --------------------------------------------------------------------------------------------
// every vertex back on the surface, its normal the field's gradient, its L attributes the field's there.
// A mirrored mesh (mirrorMesh: its `twin`): each pair placed once and reflected, the midline's kept on the plane (its
// normal along it) -- exactly symmetric still; the attributes read at every vertex where it is (a left leg's bones).
export function finish(F, mesh, L) {
  const nv = mesh.pos.length / 3, pos = new Float32Array(nv * 3), nor = new Float32Array(nv * 3), attr = new Float32Array(nv * L), tmp = new Float64Array(L);
  const tw = mesh.twin ?? null;
  for (let v = 0; v < nv; v++) {
    let p, g;
    if (tw && tw[v] < v) {   // (a reflection: its twin's, already placed)
      const u = tw[v];
      p = [pos[3 * u], pos[3 * u + 1], -pos[3 * u + 2]]; g = [nor[3 * u], nor[3 * u + 1], -nor[3 * u + 2]];
    } else {
      p = onSurface(F.dist, [mesh.pos[3 * v], mesh.pos[3 * v + 1], mesh.pos[3 * v + 2]]);
      if (tw && tw[v] === v) p[2] = 0;
      g = gradient(F.dist, p[0], p[1], p[2]);
      if (tw && tw[v] === v) { const l = Math.hypot(g[0], g[1]); g = l > 1e-6 ? [g[0] / l, g[1] / l, 0] : [0, 1, 0]; }
    }
    pos.set(p, 3 * v); nor.set(g, 3 * v);
    if (!L) continue;   // (none: the shape alone -- bodymesh.js buildShape; its dress reads them later)
    tmp.fill(0); F.at(p[0], p[1], p[2], tmp);
    for (let k = 0; k < L; k++) attr[v * L + k] = tmp[k];
  }
  return { pos, nor, attr, tri: Uint32Array.from(mesh.tri) };
}
