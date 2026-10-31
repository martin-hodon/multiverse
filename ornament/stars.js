// STAR PATTERNS: polygons in contact (Hankin, c. 1925). Lay polygons edge to edge; from the middle of every edge send two
// rays into each polygon at a contact angle; where a ray meets its partner it stops. What comes out is every star, rosette
// and girih of the Islamic tradition, and the lattice below makes whole families from three numbers.
//   THE LATTICE: `n` sided polygons, each sharing an edge with its neighbours along two edge normals, `k` normals apart
// (so `n` 8, `k` 2 is octagons and squares; 12, 2 dodecagons and triangles; 12, 3 dodecagons on a square; 10, 2 the
// ten-point stars). `gap` keeps them that far apart with a rectangle between (12, 2, gap 1 is 4.6.12). What's left between
// the polygons isn't written anywhere: it is the faces of the net, concave or not, and gets its rays like any other.
import { buildNet, facesOf, latticeOf, strandsOf } from "./net.js";

const RAD = Math.PI / 180;
// the cell of a lattice, for an edge of 1: [width, height]
export function cellOf({ n, k = 2, gap = 0 }) {
  const a = 1 / (2 * Math.tan(Math.PI / n)), d = 2 * a + gap, phi = k * Math.PI / n;
  return [2 * d * Math.sin(phi), 2 * d * Math.cos(phi)];
}

function polygonsOf({ n, k = 2, gap = 0 }) {
  const [W, H] = cellOf({ n, k, gap }), a = 1 / (2 * Math.tan(Math.PI / n)), r = 1 / (2 * Math.sin(Math.PI / n));
  const phi = k * Math.PI / n, rot = Math.PI / 2 - phi - Math.PI / n;    // (the corners, so that an edge's normal lies on the first neighbour)
  const centres = [[0, 0], [W / 2, H / 2]], segs = [], polys = [];
  for (const c of centres) {
    const v = [];
    for (let i = 0; i < n; i++) { const t = rot + i * 2 * Math.PI / n; v.push([c[0] + r * Math.cos(t), c[1] + r * Math.sin(t)]); }
    polys.push({ c, v });
    v.forEach((p, i) => segs.push([p, v[(i + 1) % n]]));
  }
  if (gap > 1e-6) {                                                       // (the rectangles between: from an edge straight across to its neighbour's)
    const near = [];
    for (const c of centres) for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) near.push([c[0] + i * W, c[1] + j * H]);
    for (const p of polys) for (let i = 0; i < n; i++) {
      const A = p.v[i], B = p.v[(i + 1) % n], mx = (A[0] + B[0]) / 2 - p.c[0], my = (A[1] + B[1]) / 2 - p.c[1], l = Math.hypot(mx, my), ux = mx / l, uy = my / l;
      const to = [p.c[0] + ux * (2 * a + gap), p.c[1] + uy * (2 * a + gap)];
      if (!near.some((q) => Math.hypot(q[0] - to[0], q[1] - to[1]) < 1e-6)) continue;
      segs.push([A, [A[0] + ux * gap, A[1] + uy * gap]], [B, [B[0] + ux * gap, B[1] + uy * gap]]);
    }
  }
  return { W, H, polys, segs };
}

const inside = (p, poly) => {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i], b = poly[j];
    if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]) c = !c;
  }
  return c;
};

// (is a point on the face's boundary: rays that only meet there have met another's start, not each other)
const edgeNear = (q, P) => P.some((A, i) => {
  const B = P[(i + 1) % P.length], dx = B[0] - A[0], dy = B[1] - A[1], t = Math.max(0, Math.min(1, ((q[0] - A[0]) * dx + (q[1] - A[1]) * dy) / (dx * dx + dy * dy)));
  return Math.hypot(q[0] - A[0] - dx * t, q[1] - A[1] - dy * t) < 1e-4;
});

// A FACE'S RAYS, paired shortest first (Kaplan): each edge sends two, leaning either way, from its middle (or `delta` to
// either side of it, the two-point patterns). -> segments, and how many rays found no partner
function raysOf(face, angle, delta, depth = 1) {
  const P = face.raw, n = P.length, rays = [], ca = Math.cos(angle * RAD), sa = Math.sin(angle * RAD);
  for (let i = 0; i < n; i++) {
    const A = P[i], B = P[(i + 1) % n], L = Math.hypot(B[0] - A[0], B[1] - A[1]), tx = (B[0] - A[0]) / L, ty = (B[1] - A[1]) / L, nx = -ty, ny = tx;    // (counter-clockwise: the normal points in)
    const m = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2], d = delta * L;
    // (with `delta` they start on the far side of the middle, crossing just inside the edge)
    rays.push({ e: i, i: rays.length, lean: 1, p: [m[0] - tx * d, m[1] - ty * d], d: [ca * tx + sa * nx, ca * ty + sa * ny] });       // (toward the next edge)
    rays.push({ e: i, i: rays.length, lean: -1, p: [m[0] + tx * d, m[1] + ty * d], d: [-ca * tx + sa * nx, -ca * ty + sa * ny] });      // (toward the last)
  }
  // DEPTH (a regular polygon only): a ray goes on through its first partner to meet the next edge but one, and so on: the
  // star polygon {n/k}, whose crossings make the ring of petals round a smaller star (a rosette)
  if (depth > 1 && n >= 5) {
    const segs = [];
    for (let i = 0; i < n; i++) {
      const a = rays[2 * i], b = rays[2 * ((i + depth) % n) + 1], det = a.d[0] * b.d[1] - a.d[1] * b.d[0];
      const wx = b.p[0] - a.p[0], wy = b.p[1] - a.p[1], t = (wx * b.d[1] - wy * b.d[0]) / det;
      if (Math.abs(det) < 1e-7 || t <= 0) return raysOf(face, angle, delta, depth - 1);
      const q = [a.p[0] + a.d[0] * t, a.p[1] + a.d[1] * t];
      segs.push([a.p, q], [b.p, q]);
    }
    return { segs, loose: 0 };
  }
  const pairs = [];
  for (let i = 0; i < rays.length; i++) for (let j = i + 1; j < rays.length; j++) {
    const a = rays[i], b = rays[j];
    if (a.e === b.e) continue;
    const det = a.d[0] * b.d[1] - a.d[1] * b.d[0], wx = b.p[0] - a.p[0], wy = b.p[1] - a.p[1];
    if (Math.abs(det) < 1e-7) {
      // (one straight line, each ray running at the other's start: a triangle's or a square's lines from middle to middle)
      const along = wx * a.d[0] + wy * a.d[1];
      if (along > 1e-6 && Math.abs(wx * a.d[1] - wy * a.d[0]) < 1e-6 && a.d[0] * b.d[0] + a.d[1] * b.d[1] < 0) pairs.push({ a, b, line: true, cost: 2 * along });
      continue;
    }
    const ta = (wx * b.d[1] - wy * b.d[0]) / det, tb = (wx * a.d[1] - wy * a.d[0]) / det;
    if (ta < 1e-6 || tb < 1e-6) continue;
    const q = [a.p[0] + a.d[0] * ta, a.p[1] + a.d[1] * ta];
    // (in a concave gap a ray may leave the face and come back: both must stay in)
    if (edgeNear(q, P)) continue;
    if (![.25, .5, .75, 1].every((f) => inside([a.p[0] + a.d[0] * ta * f, a.p[1] + a.d[1] * ta * f], P) && inside([b.p[0] + b.d[0] * tb * f, b.p[1] + b.d[1] * tb * f], P))) continue;
    pairs.push({ a, b, q, cost: (ta + tb) * (a.lean === b.lean ? 3 : 1) });
  }
  pairs.sort((x, y) => x.cost - y.cost);
  const segs = [];
  for (const { a, b, q, line } of pairs) {
    if (a.done || b.done) continue;
    a.done = b.done = true;
    if (line) segs.push([a.p, b.p]); else segs.push([a.p, q], [b.p, q]);
  }
  return { segs, loose: rays.filter((r) => !r.done).length };
}

// THE PATTERN, for an edge of 1 in one cell: { W, H, net, strands, faces (each with `rank`, by area, and `who`: which of
// the two polygons it's in), loose }
export function starNet(L) {
  const { W, H, polys, segs } = polygonsOf(L), lat = latticeOf([W, 0], [0, H]);
  const base = buildNet(segs, lat), tileFaces = facesOf(base), out = [];
  let loose = 0;
  for (const f of tileFaces) {
    const big = f.raw.length === L.n && Math.abs(f.area - polyArea(L.n)) < 1e-4;
    // the polygons take the pattern's angle, what's between them `gapAngle` (a kink at the shared edge if they differ)
    const r = raysOf(f, big ? L.angle : L.gapAngle ?? L.angle, L.delta ?? 0, big ? L.depth ?? 1 : 1);
    out.push(...r.segs); loose += r.loose;
  }
  const net = buildNet(out, lat), strands = strandsOf(net), faces = facesOf(net);
  // classes: pieces alike by sides and area, the biggest first
  const classes = [];
  for (const f of faces) {
    let c = classes.find((k) => k.sides === f.sides && Math.abs(k.area - f.area) < .015 * k.area);
    if (!c) classes.push(c = { sides: f.sides, area: f.area });
    f.cls = c;
    // (which of the cell's two polygons is nearest: to colour alternate stars)
    let best = Infinity;
    for (let i = 0; i < 2; i++) for (const [ox, oy] of [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 0], [0, 1], [1, -1], [1, 0], [1, 1]]) {
      const d = Math.hypot(f.c[0] - polys[i].c[0] - ox * W, f.c[1] - polys[i].c[1] - oy * H);
      if (d < best - 1e-6) { best = d; f.who = i; }
    }
  }
  classes.sort((a, b) => b.area - a.area).forEach((c, i) => { c.rank = i; });
  for (const f of faces) f.rank = f.cls.rank;
  // (polygons that overlap leave the cell's faces adding up to more or less than the cell)
  const areaOff = Math.abs(tileFaces.reduce((v, f) => v + f.area, 0) / (W * H) - 1);
  return { W, H, lat, net, strands, faces, classes: classes.length, loose, areaOff };
}
const polyArea = (n) => n / (4 * Math.tan(Math.PI / n));
