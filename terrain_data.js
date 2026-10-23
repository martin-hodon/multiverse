// The terrain's arithmetic, with nothing of three in it -- so a worker can run it (terrain_worker.js).
// terrain.js wraps what comes out of here in meshes; the comments on WHY the terrain is built this way, and
// on the two things that make its seams invisible, live there.
//
// The lawn's colour by elevation, as plain numbers: lush valleys through dry crests, with faint contour bands
// so the relief reads under flat toon light. grass.js's GRADE holds the numbers and its shaders grade the
// stalks by the same ones, so a blade and the ground it grows out of are the same green. (terrain.js exports
// the THREE.Color-flavoured wrapper for the callers that want one.)
const srgbToLinear = (c) => (c < .04045 ? c * .0773993808 : Math.pow(c * .9478672986 + .0521327014, 2.4));
export function gradeRGB(h, grade, out) {
  const t = Math.min(1, Math.max(0, h / grade.span + .5));
  const a = t < .5 ? grade.lo : grade.mid, b = t < .5 ? grade.mid : grade.hi, f = t < .5 ? t * 2 : (t - .5) * 2;
  const band = Math.floor(h / grade.band) % 2 ? 1.05 : .96;
  for (let i = 0; i < 3; i++) {
    const shift = 16 - i * 8;
    const ca = srgbToLinear(((a >> shift) & 255) / 255), cb = srgbToLinear(((b >> shift) & 255) / 255);
    out[i] = (ca + (cb - ca) * f) * band;
  }
  return out;
}

// Cells across a tile: the tile is the unit the error is judged in, and the coarsest that fits is used.
const LEVELS = [1, 2, 4, 8, 16, 32];

// ONE LATTICE PER TILE, WITH A ROW OF HALO, DOES EVERYTHING.
// The lattice is the tile sampled at its finest candidate cell. From it come three things, without asking the
// ground a second time:
//   the LEVEL -- the coarsest subdivision whose flat cells stay within `tol` of the lattice, judged at the
//     midpoints where a flat cell strays furthest;
//   the HEIGHTS of that level's vertices, which are lattice points;
//   the NORMALS, as central differences on the lattice. Every tile samples the SAME world lattice (they are
//     aligned and all sample at S/LAT), so the neighbour's first interior point is this tile's halo point --
//     the same value -- and two tiles at different subdivisions compute the identical normal along their
//     shared edge. That is what makes the LOD invisible: computeVertexNormals would have drawn a crease along
//     every tile border, and a normal from the triangles would change with the subdivision.
// Sampling the whole world at the finest cell is the floor on the build's cost -- to know where the ground
// needs 3-metre cells you have to look at it at 3 metres -- and it is what the old uniform grid paid too.
const LAT = 32;                        // lattice cells across a tile; every level divides it

function sampleTile(x0, z0, S, height, H) {
  const d = S / LAT, n = LAT + 3;      // one row of halo on each side, for the differences at the border
  for (let j = 0; j < n; j++) {
    const z = z0 + (j - 1) * d;
    for (let i = 0; i < n; i++) H[j * n + i] = height(x0 + (i - 1) * d, z);
  }
}

// the lattice point (i, j) of the tile, 0..LAT, inside the haloed array
const at = (H, i, j) => H[(j + 1) * (LAT + 3) + (i + 1)];

function chooseLevel(H, S, tol, maxCell) {
  for (const L of LEVELS) {
    if (S / L > maxCell) continue;                   // never so coarse that the horizon facets
    if (L >= LAT) return LAT;                        // its cells ARE the lattice: nothing left to judge
    const step = LAT / L;
    let err = 0;
    for (let j = 0; j <= LAT; j++) {
      const cj = Math.min(L - 1, Math.floor(j / step)), fv = (j - cj * step) / step;
      for (let i = 0; i <= LAT; i++) {
        const ci = Math.min(L - 1, Math.floor(i / step)), fu = (i - ci * step) / step;
        const a = at(H, ci * step, cj * step), b = at(H, (ci + 1) * step, cj * step);
        const c = at(H, ci * step, (cj + 1) * step), e = at(H, (ci + 1) * step, (cj + 1) * step);
        const h = (a * (1 - fu) + b * fu) * (1 - fv) + (c * (1 - fu) + e * fu) * fv;
        const dv = Math.abs(at(H, i, j) - h);
        if (dv > err) err = dv;
      }
    }
    if (err <= tol) return L;
  }
  return LAT;
}

// nb: the neighbours' subdivisions across the -z, +z, -x and +x borders (this tile's own where there is none)
function tileData(x0, z0, S, seg, colourAt, drop, H, nb = [seg, seg, seg, seg]) {
  // tops: one dropped vertex per border vertex -- seg+1 per side, NOT seg. Allocating four short let the last
  // vertex of each border fall off the end of the typed arrays (silently: a typed array drops an out-of-range
  // write), and the triangles that referenced them read zeros instead -- black, and anchored at (0,0,0), which
  // drew long black wedges fanning out of the origin across the meadow.
  const n = seg + 1, tops = 4 * (seg + 1), d = S / LAT, step = LAT / seg;
  const count = n * n + tops;
  const pos = new Float32Array(count * 3), nor = new Float32Array(count * 3), col = new Float32Array(count * 3);
  const c = [0, 0, 0];
  const write = (k, x, y, z, nx, ny, nz) => {
    pos[k * 3] = x; pos[k * 3 + 1] = y; pos[k * 3 + 2] = z;
    nor[k * 3] = nx; nor[k * 3 + 1] = ny; nor[k * 3 + 2] = nz;
    colourAt(y, c);
    col[k * 3] = c[0]; col[k * 3 + 1] = c[1]; col[k * 3 + 2] = c[2];
  };
  // A BORDER WITH A COARSER NEIGHBOUR FOLLOWS ITS LINE. The coarse tile's edge is a straight chord between its own
  // vertices; this tile's vertices between them sat on the ground instead, above or below that chord, and a sliver
  // of sky showed through along the join. The finer side gives way (the coarse triangle cannot bend to it): its
  // border vertices take the height of the coarse edge at their place. The coarse vertices are lattice points of the
  // same world lattice both tiles sample, so the two edges are then the same line.
  const onCoarse = (li, lj) => {
    const alongX = (row, cs) => { const a = Math.floor(li / cs) * cs, t = (li - a) / cs; return t ? at(H, a, row) + (at(H, a + cs, row) - at(H, a, row)) * t : at(H, li, row); };
    const alongZ = (col, cs) => { const a = Math.floor(lj / cs) * cs, t = (lj - a) / cs; return t ? at(H, col, a) + (at(H, col, a + cs) - at(H, col, a)) * t : at(H, col, lj); };
    if (lj === 0 && nb[0] < seg) return alongX(0, LAT / nb[0]);
    if (lj === LAT && nb[1] < seg) return alongX(LAT, LAT / nb[1]);
    if (li === 0 && nb[2] < seg) return alongZ(0, LAT / nb[2]);
    if (li === LAT && nb[3] < seg) return alongZ(LAT, LAT / nb[3]);
    return at(H, li, lj);
  };
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const li = i * step, lj = j * step;
    const y = onCoarse(li, lj);
    const dx = (at(H, li + 1, lj) - at(H, li - 1, lj)) / (2 * d);   // the ground's own slope, on the lattice
    const dz = (at(H, li, lj + 1) - at(H, li, lj - 1)) / (2 * d);
    const l = Math.hypot(dx, 1, dz);
    write(j * n + i, x0 + li * d, y, z0 + lj * d, -dx / l, 1 / l, -dz / l);
  }
  const idx = [];
  for (let j = 0; j < seg; j++) for (let i = 0; i < seg; i++) {
    const a = j * n + i;
    idx.push(a, a + n, a + 1, a + 1, a + n, a + n + 1);
  }
  // THE SKIRT. A coarse tile's edge is a straight chord where its finer neighbour follows the ground, so a
  // crack can open along the join; every tile hangs a curtain from its border to cover it. Each border is
  // walked in order and the quad between two steps is emitted with whichever winding faces AWAY from the tile
  // -- tested, not assumed, since a skirt culled by its winding would hide nothing.
  //
  // IT MUST BE SHALLOW, and it must be the colour of the ground it hangs from. The crack it has to cover is
  // the disagreement between two tiles along a shared edge, which the error budget bounds at twice `tol` --
  // centimetres. A curtain deep enough to be safe at any scale (a cell's width, which for a coarse tile is
  // ninety metres) is not a patch but a WALL: wherever the ground beyond falls away it stands clear of the
  // terrain and is seen, and at a grazing angle across the meadow those walls read as long dark lines
  // converging on the horizon, one per tile border. And its colour must come from the EDGE, not from the
  // depth it hangs to, or the sliver that does show through a crack is a different green from the ground.
  // a skirt vertex: straight down from a border vertex, wearing that vertex's own colour and normal
  const writeSkirt = (k, top, d) => {
    pos[k * 3] = pos[top * 3]; pos[k * 3 + 1] = pos[top * 3 + 1] - d; pos[k * 3 + 2] = pos[top * 3 + 2];
    nor[k * 3] = nor[top * 3]; nor[k * 3 + 1] = nor[top * 3 + 1]; nor[k * 3 + 2] = nor[top * 3 + 2];
    col[k * 3] = col[top * 3]; col[k * 3 + 1] = col[top * 3 + 1]; col[k * 3 + 2] = col[top * 3 + 2];
  };
  let k = n * n;
  const border = (idxOf, out) => {
    let prevTop = idxOf(0), prevBot = k;
    writeSkirt(k++, prevTop, drop);
    for (let s = 1; s <= seg; s++) {
      const top = idxOf(s), bot = k;
      writeSkirt(k++, top, drop);
      const ax = pos[top * 3] - pos[prevTop * 3], az = pos[top * 3 + 2] - pos[prevTop * 3 + 2];
      if (-az * out[0] + ax * out[1] > 0) idx.push(prevTop, top, prevBot, top, bot, prevBot);
      else idx.push(prevTop, prevBot, top, top, prevBot, bot);
      prevTop = top; prevBot = bot;
    }
  };
  border((s) => s, [0, -1]);                          // the -z edge, facing -z
  border((s) => seg * n + s, [0, 1]);                 // +z
  border((s) => s * n, [-1, 0]);                      // -x
  border((s) => s * n + seg, [1, 0]);                 // +x
  return { pos, nor, col, idx, verts: count };
}


// ---- ROADS CUT INTO THE TERRAIN (2026-10-06). `roads` are the road surfaces' polygons (paths.js planRoads: each a
// convex piece of a road between two of its samples, [[x, y, z], ...] counter-clockwise from above, its edges already
// split where they cross the terrain's lattice lines) -- the very points the road mesh is made of. A tile any of them
// (or its shoulder) touches is built at the finest level, and each of its cells a road touches is the cell LESS the
// road: the square cut by every road piece over it (a convex difference: the pieces outside each of the road's edges in
// turn), the pieces fanned into triangles. A point of the cut that is a road's own point takes the road's height -- the
// terrain and the road share it -- a point on a cell's side takes the height along that side between the points known
// there (its corners, the roads' crossings), so the neighbour cell meets it; any other the cell's bilinear height.
const EPS = 1e-6;
const area2 = (P) => { let a = 0; for (let i = 0; i < P.length; i++) { const p = P[i], q = P[(i + 1) % P.length]; a += p[0] * q[1] - q[0] * p[1]; } return a; };
// a polygon ([x, z] points, CCW) clipped to the left of the directed line a -> b (keep = 1) or to its right (keep = -1)
function clipHalf(P, a, b, keep) {
  const side = (p) => keep * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]));
  const out = [];
  for (let i = 0; i < P.length; i++) {
    const p = P[i], q = P[(i + 1) % P.length], sp = side(p), sq = side(q);
    if (sp >= -EPS) out.push(p);
    if ((sp > EPS && sq < -EPS) || (sp < -EPS && sq > EPS)) { const t = sp / (sp - sq); out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]); }
  }
  return out.length >= 3 && Math.abs(area2(out)) > 1e-9 ? out : null;
}
// convex P less convex Q -> convex pieces
function subtract(P, Q) {
  const out = [];
  let rest = P;
  for (let i = 0; i < Q.length && rest; i++) {
    const a = Q[i], b = Q[(i + 1) % Q.length];
    if (Math.hypot(b[0] - a[0], b[1] - a[1]) < EPS) continue;
    const o = clipHalf(rest, a, b, -1);
    if (o) out.push(o);
    rest = clipHalf(rest, a, b, 1);
  }
  return out;
}
// a road piece as a clean convex outline in (x, z): repeated and collinear points dropped, counter-clockwise (a piece
// folded at a sharp bend is taken as its hull)
function convexOf(poly) {
  let P = [];
  for (const q of poly) { const p = [q[0], q[2]]; if (!P.length || Math.hypot(p[0] - P[P.length - 1][0], p[1] - P[P.length - 1][1]) > EPS) P.push(p); }
  if (P.length > 1 && Math.hypot(P[0][0] - P[P.length - 1][0], P[0][1] - P[P.length - 1][1]) < EPS) P.pop();
  if (area2(P) < 0) P.reverse();
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const convex = P.every((p, i) => cross(P[(i - 1 + P.length) % P.length], p, P[(i + 1) % P.length]) >= -1e-9);
  if (!convex) {   // the hull (monotone chain)
    const S = [...P].sort((a, b) => a[0] - b[0] || a[1] - b[1]), lo = [], hi = [];
    for (const p of S) { while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
    for (const p of S.reverse()) { while (hi.length >= 2 && cross(hi[hi.length - 2], hi[hi.length - 1], p) <= 0) hi.pop(); hi.push(p); }
    P = lo.slice(0, -1).concat(hi.slice(0, -1));
  }
  return P.filter((p, i) => Math.abs(cross(P[(i - 1 + P.length) % P.length], p, P[(i + 1) % P.length])) > 1e-10 || P.length <= 3);
}
// the roads, prepared once: each piece's outline, its bounds, its own points (with their heights) for the snapping
export function prepareRoads(roads) {
  return (roads ?? []).map((poly) => {
    const P = convexOf(poly), xs = poly.map((q) => q[0]), zs = poly.map((q) => q[2]);
    return { P, pts: poly, b: [Math.min(...xs), Math.min(...zs), Math.max(...xs), Math.max(...zs)] };
  }).filter((r) => r.P.length >= 3);
}
function roadTileData(x0, z0, S, colourAt, drop, H, roads, height, nb = [LAT, LAT, LAT, LAT]) {
  const d = S / LAT;
  const here = roads.filter((r) => r.b[2] >= x0 - EPS && r.b[0] <= x0 + S + EPS && r.b[3] >= z0 - EPS && r.b[1] <= z0 + S + EPS);
  const pos = [], nor = [], col = [], idx = [], c = [0, 0, 0], vid = new Map();
  const key = (x, z) => `${Math.round(x * 1e5)},${Math.round(z * 1e5)}`;
  const vert = (x, y, z, n) => {
    const k = key(x, z);
    if (vid.has(k)) return vid.get(k);
    const i = pos.length / 3;
    pos.push(x, y, z); nor.push(...n); colourAt(y, c); col.push(c[0], c[1], c[2]);
    vid.set(k, i); return i;
  };
  const latN = (li, lj) => { const dx = (at(H, li + 1, lj) - at(H, li - 1, lj)) / (2 * d), dz = (at(H, li, lj + 1) - at(H, li, lj - 1)) / (2 * d), l = Math.hypot(dx, 1, dz); return [-dx / l, 1 / l, -dz / l]; };
  const fnN = (x, z) => { const e = .25, dx = (height(x + e, z) - height(x - e, z)) / (2 * e), dz = (height(x, z + e) - height(x, z - e)) / (2 * e), l = Math.hypot(dx, 1, dz); return [-dx / l, 1 / l, -dz / l]; };
  // the roads over each cell (by their bounds)
  const cellRoads = new Map();
  for (const r of here) {
    const i0 = Math.max(0, Math.floor((r.b[0] - x0) / d - 1e-9)), i1 = Math.min(LAT - 1, Math.floor((r.b[2] - x0) / d + 1e-9));
    const j0 = Math.max(0, Math.floor((r.b[1] - z0) / d - 1e-9)), j1 = Math.min(LAT - 1, Math.floor((r.b[3] - z0) / d + 1e-9));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const k = j * LAT + i; let l = cellRoads.get(k); if (!l) cellRoads.set(k, l = []); l.push(r); }
  }
  for (let j = 0; j < LAT; j++) for (let i = 0; i < LAT; i++) {
    const cx0 = x0 + i * d, cz0 = z0 + j * d, cx1 = cx0 + d, cz1 = cz0 + d;
    const hc = [at(H, i, j), at(H, i + 1, j), at(H, i + 1, j + 1), at(H, i, j + 1)];   // (x0z0, x1z0, x1z1, x0z1)
    const rs = cellRoads.get(j * LAT + i);
    const corner = (ci, cj) => vert(x0 + ci * d, at(H, ci, cj), z0 + cj * d, latN(ci, cj));
    if (!rs) {
      const a = corner(i, j), b = corner(i + 1, j), e = corner(i + 1, j + 1), f = corner(i, j + 1);
      idx.push(a, f, b, b, f, e);
      continue;
    }
    let pieces = [[[cx0, cz0], [cx1, cz0], [cx1, cz1], [cx0, cz1]]];
    for (const r of rs) pieces = pieces.flatMap((P) => subtract(P, r.P));
    if (!pieces.length) continue;
    // the points known on this cell's sides: its corners and the roads' own points lying on them
    const roadPts = rs.flatMap((r) => r.pts);
    const onSide = (p) => Math.abs(p[0] - cx0) < EPS ? 0 : Math.abs(p[0] - cx1) < EPS ? 1 : Math.abs(p[1] - cz0) < EPS ? 2 : Math.abs(p[1] - cz1) < EPS ? 3 : -1;
    const sideKnown = (sd) => {
      const L = [];
      if (sd === 0) L.push([cz0, hc[0]], [cz1, hc[3]]); if (sd === 1) L.push([cz0, hc[1]], [cz1, hc[2]]);
      if (sd === 2) L.push([cx0, hc[0]], [cx1, hc[1]]); if (sd === 3) L.push([cx0, hc[3]], [cx1, hc[2]]);
      for (const q of roadPts) { const s2 = onSide([q[0], q[2]]); if (s2 === sd) L.push([sd < 2 ? q[2] : q[0], q[1]]); }
      return L.sort((a, b) => a[0] - b[0]);
    };
    const heightOf = (p) => {
      for (const q of roadPts) if (Math.abs(q[0] - p[0]) < 1e-5 && Math.abs(q[2] - p[1]) < 1e-5) return { y: q[1], x: q[0], z: q[2], road: true };   // a road's own point: shared
      for (const r of rs) for (let k = 0; k < r.pts.length; k++) {   // on a road's edge between its points
        const a = r.pts[k], b = r.pts[(k + 1) % r.pts.length], dx = b[0] - a[0], dz = b[2] - a[2], L2 = dx * dx + dz * dz;
        if (L2 < 1e-12) continue;
        const t = ((p[0] - a[0]) * dx + (p[1] - a[2]) * dz) / L2;
        if (t > 0 && t < 1 && Math.abs((p[0] - a[0]) * dz - (p[1] - a[2]) * dx) / Math.sqrt(L2) < 1e-5) return { y: a[1] + (b[1] - a[1]) * t, x: p[0], z: p[1], road: true };
      }
      const sd = onSide(p);
      if (sd >= 0) {
        const L = sideKnown(sd), u = sd < 2 ? p[1] : p[0];
        for (let k = 1; k < L.length; k++) if (u <= L[k][0] + EPS) { const t = (u - L[k - 1][0]) / Math.max(EPS, L[k][0] - L[k - 1][0]); return { y: L[k - 1][1] + (L[k][1] - L[k - 1][1]) * Math.max(0, Math.min(1, t)), x: p[0], z: p[1] }; }
      }
      const fu = (p[0] - cx0) / d, fv = (p[1] - cz0) / d;
      return { y: (hc[0] * (1 - fu) + hc[1] * fu) * (1 - fv) + (hc[3] * (1 - fu) + hc[2] * fu) * fv, x: p[0], z: p[1] };
    };
    const V = (p) => {
      if (Math.abs(p[0] - cx0) < EPS && Math.abs(p[1] - cz0) < EPS) return corner(i, j);
      if (Math.abs(p[0] - cx1) < EPS && Math.abs(p[1] - cz0) < EPS) return corner(i + 1, j);
      if (Math.abs(p[0] - cx1) < EPS && Math.abs(p[1] - cz1) < EPS) return corner(i + 1, j + 1);
      if (Math.abs(p[0] - cx0) < EPS && Math.abs(p[1] - cz1) < EPS) return corner(i, j + 1);
      const h = heightOf(p);
      return vert(h.x, h.y, h.z, fnN(h.x, h.z));
    };
    for (const P of pieces) {
      const vs = P.map(V);
      // (counter-clockwise in (x, z) seen from above is clockwise in three's frame: wound to face up)
      for (let k = 1; k + 1 < vs.length; k++) if (vs[0] !== vs[k] && vs[k] !== vs[k + 1] && vs[0] !== vs[k + 1]) idx.push(vs[0], vs[k + 1], vs[k]);
    }
  }
  // THE SKIRT, on the tile's borders: every vertex on a border, in order, a curtain between two -- unless the stretch
  // between them is a road's (no terrain there to hang it from)
  const skirtFrom = (sel, coord, out) => {
    const B = [];
    for (let v = 0; v < pos.length / 3; v++) if (sel(pos[v * 3], pos[v * 3 + 2])) B.push(v);
    B.sort((a, b) => coord(a) - coord(b));
    const inRoad = (x, z) => here.some((r) => x > r.b[0] && x < r.b[2] && z > r.b[1] && z < r.b[3] && r.P.every((p, k) => { const q = r.P[(k + 1) % r.P.length]; return (q[0] - p[0]) * (z - p[1]) - (q[1] - p[1]) * (x - p[0]) > EPS; }));
    for (let k = 1; k < B.length; k++) {
      const a = B[k - 1], b = B[k], mx = (pos[a * 3] + pos[b * 3]) / 2, mz = (pos[a * 3 + 2] + pos[b * 3 + 2]) / 2;
      if (inRoad(mx, mz)) continue;
      const ia = pos.length / 3; pos.push(pos[a * 3], pos[a * 3 + 1] - drop, pos[a * 3 + 2]); nor.push(nor[a * 3], nor[a * 3 + 1], nor[a * 3 + 2]); col.push(col[a * 3], col[a * 3 + 1], col[a * 3 + 2]);
      const ib = pos.length / 3; pos.push(pos[b * 3], pos[b * 3 + 1] - drop, pos[b * 3 + 2]); nor.push(nor[b * 3], nor[b * 3 + 1], nor[b * 3 + 2]); col.push(col[b * 3], col[b * 3 + 1], col[b * 3 + 2]);
      const ax = pos[b * 3] - pos[a * 3], az = pos[b * 3 + 2] - pos[a * 3 + 2];
      if (-az * out[0] + ax * out[1] > 0) idx.push(a, b, ia, b, ib, ia); else idx.push(a, ia, b, b, ia, ib);
    }
  };
  // A BORDER WITH A COARSER NEIGHBOUR FOLLOWS ITS LINE -- as tileData's do (see there): a road tile is at the finest
  // level, and beside an ordinary tile on a slope its border vertices sat on the ground while the neighbour's edge is a
  // straight chord between lattice points: a gap deeper than the skirt opened along the join. Each border vertex takes
  // the height of that chord at its place (the same world lattice both tiles sample, so the edges are the same line).
  const chord = (row, along, cs, alongX) => {
    const a = Math.min(LAT - cs, Math.floor(along / cs + 1e-9) * cs), t = (along - a) / cs;
    const h0 = alongX ? at(H, a, row) : at(H, row, a), h1 = alongX ? at(H, a + cs, row) : at(H, row, a + cs);
    return h0 + (h1 - h0) * t;
  };
  for (let v = 0; v < pos.length / 3; v++) {
    const li = (pos[v * 3] - x0) / d, lj = (pos[v * 3 + 2] - z0) / d;
    let y = null;
    if (Math.abs(lj) < 1e-6 && nb[0] < LAT) y = chord(0, li, LAT / nb[0], true);
    else if (Math.abs(lj - LAT) < 1e-6 && nb[1] < LAT) y = chord(LAT, li, LAT / nb[1], true);
    else if (Math.abs(li) < 1e-6 && nb[2] < LAT) y = chord(0, lj, LAT / nb[2], false);
    else if (Math.abs(li - LAT) < 1e-6 && nb[3] < LAT) y = chord(LAT, lj, LAT / nb[3], false);
    if (y === null) continue;
    pos[v * 3 + 1] = y; colourAt(y, c); col[v * 3] = c[0]; col[v * 3 + 1] = c[1]; col[v * 3 + 2] = c[2];
  }
  const nTop = pos.length / 3;
  const top = (v) => v < nTop;
  skirtFrom((x, z) => Math.abs(z - z0) < EPS, (v) => pos[v * 3], [0, -1]);
  skirtFrom((x, z) => Math.abs(z - z0 - S) < EPS, (v) => pos[v * 3], [0, 1]);
  skirtFrom((x, z) => Math.abs(x - x0) < EPS, (v) => pos[v * 3 + 2], [-1, 0]);
  skirtFrom((x, z) => Math.abs(x - x0 - S) < EPS, (v) => pos[v * 3 + 2], [1, 0]);
  void top;
  return { pos: new Float32Array(pos), nor: new Float32Array(nor), col: new Float32Array(col), idx, verts: pos.length / 3 };
}

// One block of tiles, concatenated: a tile is the unit the error is judged in (a levelled plot must not drag
// a quarter of the map down to fine cells), but an object is what three pays for -- world matrix, frustum
// test, render list, bind group -- every pass, so the tiles of a block share one geometry.
function concatBlock(datas) {
  let verts = 0, indices = 0;
  for (const d of datas) { verts += d.verts; indices += d.idx.length; }
  const pos = new Float32Array(verts * 3), nor = new Float32Array(verts * 3), col = new Float32Array(verts * 3);
  const idx = verts > 65535 ? new Uint32Array(indices) : new Uint16Array(indices);
  let vo = 0, io = 0;
  for (const d of datas) {
    pos.set(d.pos, vo * 3); nor.set(d.nor, vo * 3); col.set(d.col, vo * 3);
    for (let i = 0; i < d.idx.length; i++) idx[io + i] = d.idx[i] + vo;
    vo += d.verts; io += d.idx.length;
  }
  return { pos, nor, col, idx };
}

// radius: half the ground's extent, height: groundH, grade: grass.js's GRADE, tol: metres of vertical error
// allowed, maxCell: the coarsest cell anywhere, block: tiles per drawn mesh
export function buildTerrainData({ radius, height, grade, tiles = 16, tol = .15, maxCell = 32, block = 4, roads = null, shoulder = 3 }) {
  const R = prepareRoads(roads);
  const S = 2 * radius / tiles;
  const colourAt = (h, out) => gradeRGB(h, grade, out);
  const blocks = [], stats = { tiles: 0, blocks: 0, tris: 0, cells: {} };
  // every tile sampled and its subdivision chosen FIRST, so each is built knowing its neighbours' (tileData: the
  // finer side of a border follows the coarser one's line)
  const lats = [], segs = [], roadTiles = [];
  for (let tz = 0; tz < tiles; tz++) for (let tx = 0; tx < tiles; tx++) {
    const H = new Float64Array((LAT + 3) * (LAT + 3));
    sampleTile(-radius + tx * S, -radius + tz * S, S, height, H);
    // (a tile a road or its shoulder touches: the finest level, and cut along the roads -- roadTileData)
    const x0 = -radius + tx * S, z0 = -radius + tz * S;
    const roady = R.some((r) => r.b[2] >= x0 - shoulder && r.b[0] <= x0 + S + shoulder && r.b[3] >= z0 - shoulder && r.b[1] <= z0 + S + shoulder);
    lats.push(H); segs.push(roady ? LAT : chooseLevel(H, S, tol, maxCell)); roadTiles.push(roady);
  }
  for (let bz = 0; bz < tiles; bz += block) for (let bx = 0; bx < tiles; bx += block) {
    const datas = [];
    for (let tz = bz; tz < Math.min(bz + block, tiles); tz++) for (let tx = bx; tx < Math.min(bx + block, tiles); tx++) {
      const x0 = -radius + tx * S, z0 = -radius + tz * S, k = tz * tiles + tx, seg = segs[k];
      const nb = [tz > 0 ? segs[k - tiles] : seg, tz < tiles - 1 ? segs[k + tiles] : seg, tx > 0 ? segs[k - 1] : seg, tx < tiles - 1 ? segs[k + 1] : seg];
      // the crack a skirt must cover is two tiles disagreeing along a shared edge: at most twice the error
      // budget. Anything deeper is a wall standing in the meadow (see THE SKIRT in tileData).
      datas.push(roadTiles[k] ? roadTileData(x0, z0, S, colourAt, Math.max(.4, tol * 4), lats[k], R, height, nb)
                              : tileData(x0, z0, S, seg, colourAt, Math.max(.4, tol * 4), lats[k], nb));
      stats.tiles++;
      const cell = +(S / seg).toFixed(1);
      stats.cells[cell] = (stats.cells[cell] ?? 0) + 1;
    }
    const b = concatBlock(datas);
    b.name = `ground ${bx},${bz}`;
    blocks.push(b);
    stats.blocks++;
    stats.tris += b.idx.length / 3;
  }
  return { blocks, stats };
}
