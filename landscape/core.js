// THE LANDSCAPE ENGINE's arithmetic (docs/landscape.md): small helpers, the noise, the random numbers, the grid's
// neighbours, a heap, the nearest point on a line

export const TAU = Math.PI * 2;
export const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
export const smooth = (t) => (t = clamp(t, 0, 1), t * t * (3 - 2 * t));
export const lerp = (a, b, t) => a + (b - a) * t;

// ---- noise (gradient noise on a lattice, fbm) ------------------------------------------------------------------------
export function hash(i, j, s) {
  let h = Math.imul(i | 0, 374761393) ^ Math.imul(j | 0, 668265263) ^ Math.imul(s | 0, 1442695041);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
export function noise(x, y, s = 0) {   // in [-1, 1] roughly
  const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j;
  const g = (a, b, dx, dy) => { const t = TAU * hash(a, b, s); return Math.cos(t) * dx + Math.sin(t) * dy; };
  const u = fx * fx * fx * (fx * (fx * 6 - 15) + 10), v = fy * fy * fy * (fy * (fy * 6 - 15) + 10);
  const a = g(i, j, fx, fy), b = g(i + 1, j, fx - 1, fy), c = g(i, j + 1, fx, fy - 1), d = g(i + 1, j + 1, fx - 1, fy - 1);
  return 1.4 * (a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v);
}
export function fbm(x, y, s = 0, oct = 4) {
  let t = 0, a = .5, f = 1;
  for (let o = 0; o < oct; o++) { t += a * noise(x * f, y * f, s + o * 17); a *= .5; f *= 2.03; }
  return t;
}
export function rng(seed) {   // mulberry32
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// ---- the grid ---------------------------------------------------------------------------------------------------------
export const N8 = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]];
// a binary heap of cell indices by a key array (lowest first)
export function heap(key) {
  const a = [];
  const less = (p, q) => key[a[p]] < key[a[q]] || (key[a[p]] === key[a[q]] && a[p] < a[q]);
  const sw = (p, q) => { const t = a[p]; a[p] = a[q]; a[q] = t; };
  return {
    get size() { return a.length; },
    push(k) { a.push(k); for (let i = a.length - 1, p; i > 0 && less(i, p = (i - 1) >> 1); i = p) sw(i, p); },
    pop() {
      const top = a[0], last = a.pop();
      if (a.length) { a[0] = last; for (let i = 0, m = 0; ; i = m) { const l = 2 * i + 1, r = l + 1; if (l < a.length && less(l, m)) m = l; if (r < a.length && less(r, m)) m = r; if (m === i) break; sw(i, m); } }
      return top;
    },
  };
}

// distance from a point to a polyline: { d, s (arc length at the nearest point), side (+1 left / -1 right), seg }
export function nearest(pts, cum, x, y, lo = 0, hi = pts.length - 1) {   // (lo..hi: the segments worth looking at)
  let best = { d: Infinity, s: 0, side: 1 };
  for (let k = Math.max(0, lo); k < Math.min(hi, pts.length - 1); k++) {
    const [ax, ay] = pts[k], [bx, by] = pts[k + 1], ex = bx - ax, ey = by - ay, L2 = ex * ex + ey * ey || 1;
    const t = clamp(((x - ax) * ex + (y - ay) * ey) / L2, 0, 1), px = ax + ex * t, py = ay + ey * t, d = Math.hypot(x - px, y - py);
    if (d < best.d) best = { d, s: cum[k] + t * Math.sqrt(L2), side: ex * (y - ay) - ey * (x - ax) >= 0 ? 1 : -1 };
  }
  return best;
}
export const cumOf = (pts) => { const c = [0]; for (let k = 1; k < pts.length; k++) c.push(c[k - 1] + Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1])); return c; };
export const atS = (pts, cum, s) => {   // the point at arc length s
  let k = 0; while (k < cum.length - 2 && cum[k + 1] < s) k++;
  const t = clamp((s - cum[k]) / ((cum[k + 1] - cum[k]) || 1), 0, 1);
  return [lerp(pts[k][0], pts[k + 1][0], t), lerp(pts[k][1], pts[k + 1][1], t)];
};
