// IRON IN THE AIR: straight bars between any two points, and the TRUSS made of them -- what a stone engine has no part for,
// a member that leans in every direction at once. Every bar is a square tube of its own (8 triangles, 12 with its ends),
// not a texture: the sky shows through it, the sun lays its shadow, and it costs a tenth of a carved wall. A `bars` or a
// `truss` part is a shell: nothing is ever inside it, but what comes down on it is held (as an open spire's net).
//   barMesh(m, a, b, w, h, caps): one tube from point a to point b, `w` across (level, square to the bar) and `h` deep.
//   trussBars(def): the lines of a truss. `stations` are its cross sections, one after another along it, each a list of n
//   corners [x, y, z] (n the same for all). Between two stations: a CHORD along every corner, a STRUT across each face at
//   the station, and each face's BRACING -- "x" two diagonals crossing, "n" one, turned by turns (a Warren girder), "none".
//   n = 2 is a flat girder (one face, no strut back), n >= 3 a closed tube of faces unless `open`. `faces` picks which
//   faces are braced and strutted (the index of the corner each starts from): a girder braced only where it shows.
//   A station's section need not lie level or square: a leaning leg, a mast, an arch's curve, a crane's jib, a bridge.
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const unit = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };

export function barMesh(m, a, b, w, h = w, caps = true) {
  const t = unit(sub(b, a));
  if (Math.hypot(...sub(b, a)) < 1e-4) return m;
  const u = unit(Math.abs(t[1]) > .98 ? cross(t, [1, 0, 0]) : cross(t, [0, 1, 0])), v = cross(u, t);
  const ring = (p) => [[1, 1], [-1, 1], [-1, -1], [1, -1]].map(([i, j]) => m.vert(p[0] + u[0] * i * w / 2 + v[0] * j * h / 2,
                                                                                  p[1] + u[1] * i * w / 2 + v[1] * j * h / 2,
                                                                                  p[2] + u[2] * i * w / 2 + v[2] * j * h / 2));
  const A = ring(a), B = ring(b);
  // (the section's corners run clockwise seen along the bar: its sides wound outward)
  for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; m.quad(A[k], B[k], B[k2], A[k2]); }
  if (caps) { m.quad(A[3], A[2], A[1], A[0]); m.quad(B[0], B[1], B[2], B[3]); }
  return m;
}

// the lines of a truss: [{ a, b, kind: "chord" | "strut" | "brace" }, ...]
export function trussBars({ stations, bracing = "x", open = false, faces = null }) {
  const out = [], n = stations[0].length;
  if (stations.some((s) => s.length !== n)) throw new Error("a truss's stations must have the same number of corners");
  const nf = n === 2 || open ? n - 1 : n, want = (f) => !faces || faces.includes(f);
  stations.forEach((S, i) => {
    for (let f = 0; f < nf; f++) if (want(f)) out.push({ a: S[f], b: S[(f + 1) % n], kind: "strut" });
    const T = stations[i + 1];
    if (!T) return;
    for (let c = 0; c < n; c++) out.push({ a: S[c], b: T[c], kind: "chord" });
    for (let f = 0; f < nf; f++) {
      if (!want(f)) continue;
      const g = (f + 1) % n;
      if (bracing === "x" || (bracing === "n" && i % 2 === 0)) out.push({ a: S[f], b: T[g], kind: "brace" });
      if (bracing === "x" || (bracing === "n" && i % 2 === 1)) out.push({ a: S[g], b: T[f], kind: "brace" });
    }
  });
  return out;
}
