// THE RHENISH HELM (Rautenhelm): the Romanesque tower roof of the Rhineland -- a GABLE on every side of the tower and
// between them the roof's faces, each a RHOMBUS from a corner of the tower up past the two gables' apexes to the spire's
// point. Nothing is chosen but the gables' pitch: a rhombus is flat only if the point stands where the lines from the
// corners through the gables' apexes meet, and that is g / sin^2(pi / n) over the eaves for gables g high on an n-sided
// tower -- twice the gables' height on a square one. (Speyer, Maria Laach, Limburg; Sompting in England.)
// `n` sides on a circumradius `R` (a square: n 4, turn .5 sets its sides across the axes), gables at `pitch`.
// Its foot at y 0, closed underneath. Returns the mesh and its point's height; `frieze` (lombard.js rakeFrieze) on
// every gable if asked.
import { rakeFrieze } from "./lombard.js";

export function helmMesh(m, { n = 4, R, pitch = 60, turn = .5, frieze = null }) {
  const ang = (k) => (k + turn) * 2 * Math.PI / n, C = Array.from({ length: n }, (_, k) => [R * Math.sin(ang(k)), R * Math.cos(ang(k))]);
  const half = R * Math.sin(Math.PI / n), g = half * Math.tan(pitch * Math.PI / 180), H = g / Math.sin(Math.PI / n) ** 2;
  const A = C.map((c, k) => { const d = C[(k + 1) % n]; return [(c[0] + d[0]) / 2, (c[1] + d[1]) / 2]; });
  const tri = (p, q, r) => {   // (wound outward: away from the axis at the face's height)
    const u = [q[0] - p[0], q[1] - p[1], q[2] - p[2]], v = [r[0] - p[0], r[1] - p[1], r[2] - p[2]];
    const nx = u[1] * v[2] - u[2] * v[1], nz = u[0] * v[1] - u[1] * v[0], cx = (p[0] + q[0] + r[0]) / 3, cz = (p[2] + q[2] + r[2]) / 3;
    const out = nx * cx + nz * cz >= 0, ids = [p, q, r].map((w) => m.vert(...w));
    if (out) m.tri(ids[0], ids[1], ids[2]); else m.tri(ids[2], ids[1], ids[0]);
  };
  const top = [0, H, 0];
  for (let k = 0; k < n; k++) {
    const c0 = C[k], c1 = C[(k + 1) % n], a = A[k], ap = A[(k + n - 1) % n];
    tri([c0[0], 0, c0[1]], [c1[0], 0, c1[1]], [a[0], g, a[1]]);                    // the gable
    tri([c0[0], 0, c0[1]], [a[0], g, a[1]], top);                                   // the rhombus over the corner c0,
    tri([c0[0], 0, c0[1]], top, [ap[0], g, ap[1]]);                                 // in two
  }
  // (underneath: a fan, facing down)
  const ids = C.map((c) => m.vert(c[0], 0, c[1])), mid = m.vert(0, 0, 0);
  for (let k = 0; k < n; k++) m.tri(mid, ids[(k + 1) % n], ids[k]);
  if (frieze) for (let k = 0; k < n; k++) {
    const c0 = C[k], c1 = C[(k + 1) % n], L = Math.hypot(c1[0] - c0[0], c1[1] - c0[1]), e = [(c1[0] - c0[0]) / L, (c1[1] - c0[1]) / L];
    const o = [e[1], -e[0]], sg = o[0] * (c0[0] + c1[0]) + o[1] * (c0[1] + c1[1]) >= 0 ? 1 : -1;   // (outward)
    rakeFrieze(frieze.m, (x, y, s) => [c0[0] + e[0] * x - sg * o[0] * s, y, c0[1] + e[1] * x - sg * o[1] * s], 0, L, 0, L / 2, g, frieze.spec);
  }
  return { m, H, g };
}
