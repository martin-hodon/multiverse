// SOLIDS, READ FROM THE STONE: an assembled building's triangles, placed and indexed on the ground by 2m cells, and the
// questions asked of them -- how high a triangle stands over a point, how far a point is from one, whether a point is
// inside a part's solid. The stair check, the support check (check.js) and the railings the assembly adds to open
// stair sides (assemble.js) all ask them.

export const cellOf = (x, z) => `${Math.floor(x / 2)},${Math.floor(z / 2)}`;

// every part's triangles, placed, indexed on the ground by 2m cells
export function index(asm) {
  const cells = new Map(), parts = [], vast = [];
  for (const p of asm.parts) {
    const P = p.geometry.position, I = p.geometry.index;
    const own = { name: p.name, shell: !!p.shell || p.kind === "glass", tris: [] };
    parts.push(own);
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const c = Math.cos(yaw), s = Math.sin(yaw);
      const at = (j) => [P[j * 3] * c + P[j * 3 + 2] * s + X, P[j * 3 + 1] + Y, -P[j * 3] * s + P[j * 3 + 2] * c + Z];
      for (let k = 0; k < I.length; k += 3) {
        const a = at(I[k]), b = at(I[k + 1]), d = at(I[k + 2]);
        const t = { a, b, d, part: own, inst, top: Math.max(a[1], b[1], d[1]) };
        own.tris.push(t);
        const x0 = Math.floor(Math.min(a[0], b[0], d[0]) / 2), x1 = Math.floor(Math.max(a[0], b[0], d[0]) / 2);
        const z0 = Math.floor(Math.min(a[2], b[2], d[2]) / 2), z1 = Math.floor(Math.max(a[2], b[2], d[2]) / 2);
        if ((x1 - x0 + 1) * (z1 - z0 + 1) > 4000) { vast.push(t); continue; }   // (a vast slab: its cells are many; kept apart, for a ray to test)
        for (let i = x0; i <= x1; i++) for (let j = z0; j <= z1; j++) {
          const key = `${i},${j}`;
          let l = cells.get(key); if (!l) cells.set(key, l = []);
          l.push(t);
        }
      }
    });
  }
  return { cells, parts, vast };
}

// the heights at which a triangle stands over (x, z), if it does (null for a wall seen edge-on)
export function heightOver(t, x, z) {
  const [ax, ay, az] = t.a, [bx, by, bz] = t.b, [cx, cy, cz] = t.d;
  const den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz);
  if (Math.abs(den) < 1e-9) return null;
  const u = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / den, v = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / den;
  if (u < -1e-6 || v < -1e-6 || u + v > 1 + 1e-6) return null;
  return u * ay + v * by + (1 - u - v) * cy;
}
export const upFacing = (t) => {
  const [ax, ay, az] = t.a, [bx, by, bz] = t.b, [cx, cy, cz] = t.d;
  const ux = bx - ax, uy = by - ay, uz = bz - az, vx = cx - ax, vy = cy - ay, vz = cz - az;
  const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
  return Math.abs(ny) / (Math.hypot(nx, ny, nz) || 1) > .35;
};

// the distance from a point to a triangle (the closest point on it: Ericson, Real-Time Collision Detection 5.1.5)
export function pointTri(p, t) {
  const sub = (u, v) => [u[0] - v[0], u[1] - v[1], u[2] - v[2]], dot = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
  const a = t.a, b = t.b, c = t.d, ab = sub(b, a), ac = sub(c, a), ap = sub(p, a);
  const at = (u, v) => Math.hypot(p[0] - (a[0] + ab[0] * u + ac[0] * v), p[1] - (a[1] + ab[1] * u + ac[1] * v), p[2] - (a[2] + ab[2] * u + ac[2] * v));
  const d1 = dot(ab, ap), d2 = dot(ac, ap);
  if (d1 <= 0 && d2 <= 0) return at(0, 0);
  const bp = sub(p, b), d3 = dot(ab, bp), d4 = dot(ac, bp);
  if (d3 >= 0 && d4 <= d3) return at(1, 0);
  const vc = d1 * d4 - d3 * d2;
  if (vc <= 0 && d1 >= 0 && d3 <= 0) return at(d1 / (d1 - d3), 0);
  const cp = sub(p, c), d5 = dot(ab, cp), d6 = dot(ac, cp);
  if (d6 >= 0 && d5 <= d6) return at(0, 1);
  const vb = d5 * d2 - d1 * d6;
  if (vb <= 0 && d2 >= 0 && d6 <= 0) return at(0, d2 / (d2 - d6));
  const va = d3 * d6 - d5 * d4;
  if (va <= 0 && d4 - d3 >= 0 && d5 - d6 >= 0) { const w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); return at(1 - w, w); }
  const den = 1 / (va + vb + vc);
  return at(vb * den, vc * den);
}


// the copies of parts whose solid a point is inside: an upward ray from it crosses their surface an odd number of
// times -- counted over ALL the copies of a part (a ring's bays are open slices, closed only together). `skip`: a
// part's name to leave out (the asker's own)
export function insideOf(cells, x, y, z, skip = null) {
  const count = new Map(), rx = x + 1.37e-4, rz = z + 2.71e-4;
  for (const t of cells.get(cellOf(x, z)) ?? []) {
    if (t.top <= y || t.part.shell || t.part.name === skip) continue;
    const h = heightOver(t, rx, rz);
    if (h !== null && h > y) count.set(t.part.name, (count.get(t.part.name) ?? 0) + 1);
  }
  return [...count].filter(([, n]) => n % 2).map(([k]) => k);
}

// A RAY through the building: does it meet stone within `maxT` metres? The triangles are filed in 2m CUBES (a ray at
// the height of a door need not test the bracket sets twenty metres over it, as a column of the ground index would make
// it), the cube a ray is in is walked to the next (Amanatides and Woo), each triangle is tested once (`stamp`), and the
// ray is given up as soon as it leaves the building's bounds -- so one that escapes to the sky costs a few cubes.
const CUBE = 2, K = (i, j, k) => ((i + 2048) * 4096 + (j + 2048)) * 4096 + (k + 2048);
export function rayIndex(asm) {
  const { parts, cells } = index(asm), cubes = new Map();
  const b = { x0: 1e9, x1: -1e9, y0: 1e9, y1: -1e9, z0: 1e9, z1: -1e9 };
  for (const part of parts) for (const t of part.tris) {
    const lo = [0, 1, 2].map((q) => Math.min(t.a[q], t.b[q], t.d[q])), hi = [0, 1, 2].map((q) => Math.max(t.a[q], t.b[q], t.d[q]));
    if (lo[0] < b.x0) b.x0 = lo[0]; if (hi[0] > b.x1) b.x1 = hi[0]; if (lo[1] < b.y0) b.y0 = lo[1]; if (hi[1] > b.y1) b.y1 = hi[1];
    if (lo[2] < b.z0) b.z0 = lo[2]; if (hi[2] > b.z1) b.z1 = hi[2];
    const [i0, j0, k0] = lo.map((v) => Math.floor(v / CUBE)), [i1, j1, k1] = hi.map((v) => Math.floor(v / CUBE));
    for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) for (let k = k0; k <= k1; k++) {
      const key = K(i, j, k); let l = cubes.get(key); if (!l) cubes.set(key, l = []); l.push(t);
    }
  }
  return { cubes, bounds: b, cells };
}
let rayStamp = 1;
const hitTri = (o, d, t) => {                    // Moller-Trumbore: the distance along d, or Infinity
  const [ax, ay, az] = t.a, e1x = t.b[0] - ax, e1y = t.b[1] - ay, e1z = t.b[2] - az, e2x = t.d[0] - ax, e2y = t.d[1] - ay, e2z = t.d[2] - az;
  const px = d[1] * e2z - d[2] * e2y, py = d[2] * e2x - d[0] * e2z, pz = d[0] * e2y - d[1] * e2x, det = e1x * px + e1y * py + e1z * pz;
  if (Math.abs(det) < 1e-12) return Infinity;
  const inv = 1 / det, sx = o[0] - ax, sy = o[1] - ay, sz = o[2] - az, u = (sx * px + sy * py + sz * pz) * inv;
  if (u < 0 || u > 1) return Infinity;
  const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x, v = (d[0] * qx + d[1] * qy + d[2] * qz) * inv;
  if (v < 0 || u + v > 1) return Infinity;
  const tt = (e2x * qx + e2y * qy + e2z * qz) * inv;
  return tt > 1e-4 ? tt : Infinity;
};
export function rayHits({ cubes, bounds: b }, o, d, maxT = 200) {
  const stamp = ++rayStamp;
  const c = [0, 1, 2].map((q) => Math.floor(o[q] / CUBE)), st = [0, 1, 2].map((q) => Math.sign(d[q]));
  const delta = [0, 1, 2].map((q) => (st[q] ? CUBE / Math.abs(d[q]) : Infinity));
  const next = [0, 1, 2].map((q) => (st[q] ? ((st[q] > 0 ? (c[q] + 1) * CUBE : c[q] * CUBE) - o[q]) / d[q] : Infinity));
  const lo = [b.x0, b.y0, b.z0], hi = [b.x1, b.y1, b.z1];
  for (let steps = 0; steps < 1000; steps++) {
    const l = cubes.get(K(c[0], c[1], c[2]));
    if (l) for (const t of l) { if (t.ray === stamp) continue; t.ray = stamp; if (hitTri(o, d, t) < maxT) return true; }
    const q = next[0] < next[1] ? (next[0] < next[2] ? 0 : 2) : (next[1] < next[2] ? 1 : 2), t1 = next[q];
    if (t1 >= maxT) return false;
    c[q] += st[q]; next[q] += delta[q];
    // (out of the bounds and still going out: nothing more to meet)
    const edge = c[q] * CUBE;
    if ((st[q] > 0 && edge > hi[q]) || (st[q] < 0 && edge + CUBE < lo[q])) return false;
  }
  return false;
}

// how far along d the ray first meets stone (Infinity: not within maxT) -- the same walk, but a cube's nearest hit is
// the first only once it lies before the cube's far side
export function rayDist({ cubes, bounds: b }, o, d, maxT = 200) {
  const stamp = ++rayStamp;
  const c = [0, 1, 2].map((q) => Math.floor(o[q] / CUBE)), st = [0, 1, 2].map((q) => Math.sign(d[q]));
  const delta = [0, 1, 2].map((q) => (st[q] ? CUBE / Math.abs(d[q]) : Infinity));
  const next = [0, 1, 2].map((q) => (st[q] ? ((st[q] > 0 ? (c[q] + 1) * CUBE : c[q] * CUBE) - o[q]) / d[q] : Infinity));
  const lo = [b.x0, b.y0, b.z0], hi = [b.x1, b.y1, b.z1];
  let best = Infinity;
  for (let steps = 0; steps < 1000; steps++) {
    const l = cubes.get(K(c[0], c[1], c[2]));
    if (l) for (const t of l) { if (t.ray === stamp) continue; t.ray = stamp; best = Math.min(best, hitTri(o, d, t)); }
    const q = next[0] < next[1] ? (next[0] < next[2] ? 0 : 2) : (next[1] < next[2] ? 1 : 2), t1 = next[q];
    if (best <= t1) return best < maxT ? best : Infinity;
    if (t1 >= maxT) return Infinity;
    c[q] += st[q]; next[q] += delta[q];
    const edge = c[q] * CUBE;
    if ((st[q] > 0 && edge > hi[q]) || (st[q] < 0 && edge + CUBE < lo[q])) return Infinity;
  }
  return Infinity;
}
