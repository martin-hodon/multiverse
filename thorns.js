// THORNS (2026-10-03): hair standing in sharp spikes -- one lattice for every surface that grows them (hair.js `spikes`
// on a hairstyle's cap, manes.js on a lion's mane). The caller gives the surface: `at(i, j)` -> { q, n, u, v } a point of
// it and its outward normal (rows i = 0 .. NR, columns j = 0 .. NC - 1, `ring` when the columns close round); the
// lattice keeps every point on it but a sparse CHECKERBOARD -- every `every`-th column on every other row, the rows'
// spikes half a step apart, never on the edge rows nor (when it is not a ring) the edge columns -- which it pushes out
// `spike(i, j, n)` -> { d (unit direction), L (length) }. A far point's neighbours stay on the surface, so each is the
// apex of a sharp pyramid, and the edge rows lie on the surface's edge: the thorns rise from it and fall back to it.
// Faces are flat (each triangle its own normal: a spike's sides read), turned to face away from `inside` (a point
// within the surface -- the head's middle -- or a function of the face's middle giving one: a tube's axis beside it), handed to `tri(A, B, C, n)` with A..C the lattice points.
// `apex`: one more spike at the closed end of a ring (the crown), from the last row's middle.
export function thornLattice({ NR, NC, ring = false, every = 3, at, spike, inside = [0, 0, 0], tri, apex = null }) {
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const raw = (i, j) => i > 0 && i < NR && i % 2 === 1 && (j + ((i >> 1) % 2) * Math.floor(every / 2)) % every === 0 && (ring || (j > 0 && j < NC - 1));
  // (round a ring whose columns are no multiple of `every`, the last spike and the first can stand side by side across
  //  the seam -- one thorn with two points: the one before its neighbour gives way)
  const isSpike = (i, j) => raw(i, j) && !(ring && raw(i, (j + 1) % NC));
  const pt = Array.from({ length: NR + 1 }, (_, i) => Array.from({ length: NC }, (_, j) => {
    const b = at(i, j);
    if (!isSpike(i, j)) return b;
    const s = spike(i, j, b.n);
    return { ...b, q: add(b.q, mul(s.d, s.L)), v: b.v + s.L, far: true };
  }));
  const face = (A, B, C) => {
    let n = norm(cross(sub(B.q, A.q), sub(C.q, A.q)));
    const mid = mul(add(add(A.q, B.q), C.q), 1 / 3), inn = typeof inside === "function" ? inside(mid) : inside;   // (a function: a tube's axis beside the face)
    if (dot(n, sub(mid, inn)) < 0) { [B, C] = [C, B]; n = mul(n, -1); }
    tri(A, B, C, n);
  };
  for (let i = 0; i < NR; i++) for (let j = 0; j < NC - (ring ? 0 : 1); j++) {
    const j2 = (j + 1) % NC, a = pt[i][j], b = pt[i][j2], c = pt[i + 1][j2], d = pt[i + 1][j];
    // (the cell's diagonal through its far point, if it has one: the spike's ridges run to its apex)
    if (b.far || d.far) { face(a, b, d); face(b, c, d); } else { face(a, b, c); face(a, c, d); }
  }
  if (apex && ring) {   // the closed end: a fan from the last row to one more thorn standing from its middle
    const last = pt[NR], mid = mul(last.reduce((s, p) => add(s, p.q), [0, 0, 0]), 1 / NC);
    const s = apex(mid), top = { q: add(mid, mul(s.d, s.L)), n: s.d, u: 0, v: (last[0].v ?? 0) + s.L, far: true };
    for (let j = 0; j < NC; j++) face(last[j], last[(j + 1) % NC], top);
  }
}
