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
        if ((x1 - x0 + 1) * (z1 - z0 + 1) > 4000) { vast.push({ t, x0, x1, z0, z1 }); continue; }   // (a vast slab: its cells are many; kept apart)
        for (let i = x0; i <= x1; i++) for (let j = z0; j <= z1; j++) {
          const key = `${i},${j}`;
          let l = cells.get(key); if (!l) cells.set(key, l = []);
          l.push(t);
        }
      }
    });
  }
  // (and handed back with every cell it covers: a hill's top ear-clipped into a few great triangles is the ground under
  //  everything on it -- a cell that missed it saw a statue standing on air)
  if (vast.length) {
    const own = cells.get.bind(cells);
    cells.get = (key) => {
      const [i, j] = key.split(",").map(Number), more = vast.filter((v) => i >= v.x0 && i <= v.x1 && j >= v.z0 && j <= v.z1).map((v) => v.t);
      const l = own(key);
      return more.length ? (l ?? []).concat(more) : l;
    };
  }
  return { cells, parts, vast: vast.map((v) => v.t) };
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
// (FLAT: a triangle is nine numbers in one array -- its corners a, b, d -- and a cube's triangles a run of one list
//  (`start`/`list`, filed by the cube's number within the bounds, or through `slot` where the bounds hold too many cubes
//  to number them all): a ray walks typed arrays, not objects, and makes nothing as it goes)
const CUBE = 2, DENSE = 1 << 22;
export function rayIndex(asm) {
  const { parts, cells } = index(asm);
  const T = parts.reduce((n, part) => n + part.tris.length, 0), tri = new Float64Array(T * 9);
  const b = { x0: 1e9, x1: -1e9, y0: 1e9, y1: -1e9, z0: 1e9, z1: -1e9 };
  let n = 0;
  parts.forEach((part) => {
    for (const t of part.tris) {
      tri.set(t.a, n * 9); tri.set(t.b, n * 9 + 3); tri.set(t.d, n * 9 + 6); n++;
      for (const v of [t.a, t.b, t.d]) {
        if (v[0] < b.x0) b.x0 = v[0]; if (v[0] > b.x1) b.x1 = v[0]; if (v[1] < b.y0) b.y0 = v[1]; if (v[1] > b.y1) b.y1 = v[1];
        if (v[2] < b.z0) b.z0 = v[2]; if (v[2] > b.z1) b.z1 = v[2];
      }
    }
  });
  const o = [b.x0, b.y0, b.z0].map((v) => Math.floor(v / CUBE)), dim = [b.x1, b.y1, b.z1].map((v, q) => Math.floor(v / CUBE) - o[q] + 1);
  if (!T) dim.fill(0);
  const total = dim[0] * dim[1] * dim[2], dense = total <= DENSE, slot = dense ? null : new Map();
  // (each triangle's cubes, walked twice: counted, then filed)
  const walk = (fn) => {
    for (let t = 0; t < T; t++) {
      const lo = [0, 1, 2].map((q) => Math.floor(Math.min(tri[t * 9 + q], tri[t * 9 + 3 + q], tri[t * 9 + 6 + q]) / CUBE) - o[q]);
      const hi = [0, 1, 2].map((q) => Math.floor(Math.max(tri[t * 9 + q], tri[t * 9 + 3 + q], tri[t * 9 + 6 + q]) / CUBE) - o[q]);
      for (let i = lo[0]; i <= hi[0]; i++) for (let j = lo[1]; j <= hi[1]; j++) for (let k = lo[2]; k <= hi[2]; k++) fn((i * dim[1] + j) * dim[2] + k, t);
    }
  };
  const count = dense ? new Int32Array(total) : [];
  walk((key) => {
    if (dense) { count[key]++; return; }
    let s = slot.get(key);
    if (s === undefined) { slot.set(key, s = count.length); count.push(0); }
    count[s]++;
  });
  const nc = count.length, start = new Int32Array(nc + 1);
  for (let s = 0; s < nc; s++) start[s + 1] = start[s] + count[s];
  const list = new Int32Array(start[nc]), fill = start.slice(0, nc);
  walk((key, t) => { list[fill[dense ? key : slot.get(key)]++] = t; });
  return { bounds: b, cells, tri, o, dim, slot, start, list, stamp: new Int32Array(T), mark: 0 };
}
// (where a cube's triangles run in `list`, by the cube's place: -1 none)
const cubeAt = (ix, i, j, k) => {
  i -= ix.o[0]; j -= ix.o[1]; k -= ix.o[2];
  if (i < 0 || j < 0 || k < 0 || i >= ix.dim[0] || j >= ix.dim[1] || k >= ix.dim[2]) return -1;
  const key = (i * ix.dim[1] + j) * ix.dim[2] + k;
  return ix.slot ? ix.slot.get(key) ?? -1 : key;
};
const nextMark = (ix) => { if (++ix.mark > 2e9) { ix.stamp.fill(0); ix.mark = 1; } return ix.mark; };
const hitTri = (o, d, tri, t) => {                    // Moller-Trumbore: the distance along d, or Infinity
  const at = t * 9, ax = tri[at], ay = tri[at + 1], az = tri[at + 2];
  const e1x = tri[at + 3] - ax, e1y = tri[at + 4] - ay, e1z = tri[at + 5] - az, e2x = tri[at + 6] - ax, e2y = tri[at + 7] - ay, e2z = tri[at + 8] - az;
  const px = d[1] * e2z - d[2] * e2y, py = d[2] * e2x - d[0] * e2z, pz = d[0] * e2y - d[1] * e2x, det = e1x * px + e1y * py + e1z * pz;
  if (Math.abs(det) < 1e-12) return Infinity;
  const inv = 1 / det, sx = o[0] - ax, sy = o[1] - ay, sz = o[2] - az, u = (sx * px + sy * py + sz * pz) * inv;
  if (u < 0 || u > 1) return Infinity;
  const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x, v = (d[0] * qx + d[1] * qy + d[2] * qz) * inv;
  if (v < 0 || u + v > 1) return Infinity;
  const tt = (e2x * qx + e2y * qy + e2z * qz) * inv;
  return tt > 1e-4 ? tt : Infinity;
};
// the walk from cube to cube both rays share: `first` -- done at the first hit within maxT (rayHits), else the nearest
// (rayDist: a cube's nearest hit is the first only once it lies before the cube's far side)
function walkRay(ix, o, d, maxT, first) {
  const mark = nextMark(ix), { tri, stamp, start, list, bounds: b } = ix;
  let cx = Math.floor(o[0] / CUBE), cy = Math.floor(o[1] / CUBE), cz = Math.floor(o[2] / CUBE);
  const sx = Math.sign(d[0]), sy = Math.sign(d[1]), sz = Math.sign(d[2]);
  const dx = sx ? CUBE / Math.abs(d[0]) : Infinity, dy = sy ? CUBE / Math.abs(d[1]) : Infinity, dz = sz ? CUBE / Math.abs(d[2]) : Infinity;
  let nx = sx ? ((sx > 0 ? (cx + 1) * CUBE : cx * CUBE) - o[0]) / d[0] : Infinity;
  let ny = sy ? ((sy > 0 ? (cy + 1) * CUBE : cy * CUBE) - o[1]) / d[1] : Infinity;
  let nz = sz ? ((sz > 0 ? (cz + 1) * CUBE : cz * CUBE) - o[2]) / d[2] : Infinity;
  let best = Infinity;
  for (let steps = 0; steps < 1000; steps++) {
    const s = cubeAt(ix, cx, cy, cz);
    if (s >= 0) for (let m = start[s], e = start[s + 1]; m < e; m++) {
      const t = list[m];
      if (stamp[t] === mark) continue;
      stamp[t] = mark;
      const h = hitTri(o, d, tri, t);
      if (first) { if (h < maxT) return h; } else if (h < best) best = h;
    }
    const t1 = nx < ny ? (nx < nz ? nx : nz) : (ny < nz ? ny : nz);
    if (!first && best <= t1) return best < maxT ? best : Infinity;
    if (t1 >= maxT) return Infinity;
    // (out of the bounds and still going out: nothing more to meet)
    if (nx < ny && nx < nz) {
      cx += sx; nx += dx;
      if ((sx > 0 && cx * CUBE > b.x1) || (sx < 0 && cx * CUBE + CUBE < b.x0)) return Infinity;
    } else if (ny < nz) {
      cy += sy; ny += dy;
      if ((sy > 0 && cy * CUBE > b.y1) || (sy < 0 && cy * CUBE + CUBE < b.y0)) return Infinity;
    } else {
      cz += sz; nz += dz;
      if ((sz > 0 && cz * CUBE > b.z1) || (sz < 0 && cz * CUBE + CUBE < b.z0)) return Infinity;
    }
  }
  return Infinity;
}
export const rayHits = (ix, o, d, maxT = 200) => walkRay(ix, o, d, maxT, true) < Infinity;
// how far along d the ray first meets stone (Infinity: not within maxT)
export const rayDist = (ix, o, d, maxT = 200) => walkRay(ix, o, d, maxT, false);
