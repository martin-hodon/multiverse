// THE SWEEP (2026-11-02): a cross-section carried along a curve -- a bench snaking along a terrace's edge, the coping of a
// curved wall, a kerb, a handrail, a viaduct's battered wall, the crest of a park wall. What `loft` cannot do (its rings
// stand square to one straight axis) and `range` will not (its band is a folding line of straight walls).
//
//   path     [[x, z] | [x, y, z], ...]: where the profile's origin runs (y 0 when not given), smoothed on a Catmull-Rom curve
//            through its points (`closed`: a loop), then laid out every `step` metres of its own length
//   profile  [[u, v], ...]: a closed outline across the path, u to the RIGHT of the way it runs, v up. It is kept upright
//            (it never banks), and widened at a bend by its mitre, so the section across stays the profile
//   wave     { amp, length, phase }: the path swung to its right and left, amp * sin(2 pi s / length + phase) along its own
//            length s -- the concave and convex bays of a serpentine bench -- before the rings are set square to the result
//   round    true: the profile's corners smoothed (shared vertices); else each of its edges is a flat face along the curve
//   caps     the two ends closed (not on a loop; default true)
import { earClip } from "./build.js";

const crPoint = (p0, p1, p2, p3, t) => p1.map((_, k) => .5 * (2 * p1[k] + (p2[k] - p0[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t * t * t));

// the path as a dense polyline on its spline, then laid out at a uniform step along its length
export function sweepPath(path, { closed = false, step = .5 } = {}) {
  const q = path.map((p) => (p.length === 2 ? [p[0], 0, p[1]] : [p[0], p[1], p[2]]));
  if (q.length < 2) throw new Error("a sweep's path has two points at least");
  const n = q.length, at = (i) => (closed ? q[(i + n) % n] : q[Math.max(0, Math.min(n - 1, i))]), dense = [];
  const spans = closed ? n : n - 1, K = 12;
  for (let i = 0; i < spans; i++) for (let j = 0; j < K; j++) dense.push(crPoint(at(i - 1), at(i), at(i + 1), at(i + 2), j / K));
  dense.push(closed ? dense[0] : q[n - 1]);
  const len = [0];
  for (let i = 1; i < dense.length; i++) len.push(len[i - 1] + Math.hypot(dense[i][0] - dense[i - 1][0], dense[i][1] - dense[i - 1][1], dense[i][2] - dense[i - 1][2]));
  const L = len[len.length - 1], N = Math.max(1, Math.round(L / step)), out = [];
  for (let k = 0, j = 0; k <= N; k++) {
    if (closed && k === N) break;
    const s = L * k / N;
    while (j + 1 < len.length - 1 && len[j + 1] < s) j++;
    const f = len[j + 1] > len[j] ? (s - len[j]) / (len[j + 1] - len[j]) : 0;
    out.push({ p: dense[j].map((v, c) => v + (dense[j + 1][c] - v) * f), s });
  }
  return { pts: out, length: L };
}

// the right-hand normal (in plan) at each point of a polyline, mitred: its length is 1 / cos of half the bend
function normals(P, closed) {
  const n = P.length, seg = [];
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const a = P[i], b = P[(i + 1) % n], dx = b[0] - a[0], dz = b[2] - a[2], l = Math.hypot(dx, dz) || 1;
    seg.push([-dz / l, dx / l]);
  }
  return P.map((_, i) => {
    const s0 = closed ? seg[(i - 1 + n) % n] : seg[Math.max(0, i - 1)], s1 = closed ? seg[i % n] : seg[Math.min(seg.length - 1, i)];
    const mx = s0[0] + s1[0], mz = s0[1] + s1[1], ml = Math.hypot(mx, mz) || 1, ux = mx / ml, uz = mz / ml;
    const c = Math.max(.35, ux * s1[0] + uz * s1[1]);
    return [ux / c, uz / c];
  });
}

export function sweepMesh(m, { path, profile, closed = false, step = .5, wave = null, round = false, caps = true }) {
  const { pts } = sweepPath(path, { closed, step: wave ? Math.min(step, wave.length / 12) : step });
  let P = pts.map((q) => q.p);
  if (wave && wave.amp) {
    const N0 = normals(P, closed), w = (s) => wave.amp * Math.sin(2 * Math.PI * s / wave.length + (wave.phase ?? 0));
    P = pts.map((q, i) => { const d = w(q.s), l = Math.hypot(...N0[i]) || 1; return [q.p[0] + N0[i][0] / l * d, q.p[1], q.p[2] + N0[i][1] / l * d]; });
  }
  const N = normals(P, closed);
  // the profile counter-clockwise in (u, v) -- u right, v up -- so its faces point out
  let prof = profile.map(([u, v]) => [u, v]);
  const area = prof.reduce((s, p, i) => { const q = prof[(i + 1) % prof.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0);
  if (area < 0) prof = prof.reverse();
  const np = prof.length, rings = P.length;
  const at = (i, k) => { const [u, v] = prof[k], p = P[i], nn = N[i]; return [p[0] + nn[0] * u, p[1] + v, p[2] + nn[1] * u]; };
  // along the path: a quad per profile edge per span. Viewed along the way the path runs, u to the right and v up is a
  // left-handed frame, so a counter-clockwise profile's edge (k -> k+1) faces out with the rings taken (i+1, i)
  const spans = closed ? rings : rings - 1;
  if (round) {
    const V = P.map((_, i) => prof.map((_, k) => m.vert(...at(i, k))));
    for (let i = 0; i < spans; i++) { const i2 = (i + 1) % rings; for (let k = 0; k < np; k++) { const k2 = (k + 1) % np; m.quad(V[i2][k], V[i2][k2], V[i][k2], V[i][k]); } }
  } else {
    for (let k = 0; k < np; k++) {
      const k2 = (k + 1) % np, A = P.map((_, i) => m.vert(...at(i, k))), B = P.map((_, i) => m.vert(...at(i, k2)));
      for (let i = 0; i < spans; i++) { const i2 = (i + 1) % rings; m.quad(A[i2], B[i2], B[i], A[i]); }
    }
  }
  if (caps && !closed) {
    // (each ear counter-clockwise in (u, v) first; the start cap then faces back along the path, the end cap on along it)
    const tris = earClip(prof, prof.map((_, k) => k)).map(([a, b, c]) => {
      const A = prof[a], B = prof[b], C = prof[c];
      return (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0]) > 0 ? [a, b, c] : [a, c, b];
    });
    for (const [i, end] of [[0, false], [rings - 1, true]]) {
      const V = prof.map((_, k) => m.vert(...at(i, k)));
      for (const [a, b, c] of tris) (end ? m.tri(V[c], V[b], V[a]) : m.tri(V[a], V[b], V[c]));
    }
  }
  return m;
}
