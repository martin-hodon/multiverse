// SHARDS (2026-11-02): a tile broken into irregular pieces with joints between -- trencadis (Gaudi's broken glazed tile), crazy
// paving, opus incertum, a rubble wall of field stones. A Voronoi of points jittered off a grid of `n` [nx, ny] cells,
// PERIODIC with the tile (each cell is cut by its neighbours' copies across the edges), every piece shrunk by half the joint
// `gap` from each neighbour, so the mortar is one width everywhere. Pure geometry: the layer kind is ornament.js's.

const hash = (...k) => { let h = 2166136261; for (const v of k) { h = Math.imul(h ^ (v | 0), 16777619); h ^= h >>> 13; } return ((h >>> 0) % 100003) / 100003; };

// a convex polygon cut by the half-plane x.d <= c
function clip(poly, dx, dy, c) {
  const out = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length], fa = a[0] * dx + a[1] * dy - c, fb = b[0] * dx + b[1] * dy - c;
    if (fa <= 0) out.push(a);
    if ((fa < 0) !== (fb < 0) && fa !== fb) { const t = fa / (fa - fb); out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]); }
  }
  return out;
}

// the pieces of a W x H tile (about its middle): [{ pts, c: [x, y], i, j }], `inset` metres in from each joint's middle line
export function shardCells({ W, H, n = [8, 8], jitter = .8, inset = 0, seed = 1 }) {
  const [nx, ny] = n, cw = W / nx, ch = H / ny;
  const site = (i, j) => {
    const ii = ((i % nx) + nx) % nx, jj = ((j % ny) + ny) % ny, ox = Math.floor(i / nx) * W, oy = Math.floor(j / ny) * H;
    return [-W / 2 + (ii + .5 + jitter * (hash(ii, jj, seed, 1) - .5)) * cw + ox, -H / 2 + (jj + .5 + jitter * (hash(ii, jj, seed, 2) - .5)) * ch + oy];
  };
  const cells = [];
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    const p = site(i, j), R = 3 * Math.max(cw, ch);
    let poly = [[p[0] - R, p[1] - R], [p[0] + R, p[1] - R], [p[0] + R, p[1] + R], [p[0] - R, p[1] + R]];
    for (let di = -2; di <= 2; di++) for (let dj = -2; dj <= 2; dj++) {
      if (!di && !dj) continue;
      const q = site(i + di, j + dj), ex = q[0] - p[0], ey = q[1] - p[1], l = Math.hypot(ex, ey);
      if (!l) continue;
      const dx = ex / l, dy = ey / l;
      poly = clip(poly, dx, dy, ((p[0] + q[0]) / 2) * dx + ((p[1] + q[1]) / 2) * dy - inset);
      if (poly.length < 3) break;
    }
    if (poly.length >= 3) cells.push({ pts: poly, c: p, i, j });
  }
  return cells;
}
