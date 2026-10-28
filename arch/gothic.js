// THE VAULTED BASILICA AS ITS STRUCTURE (assemble.js part `basilica`). A Gothic church is not a set of walls with arches
// drawn on them: it is a SKELETON -- piers on a grid of bays, arches between them, a rib vault over every bay, buttresses
// taking the vaults' thrust out over the aisles to the ground -- and walls that only fill it in. So it is described here
// the way it was set out on site, and every element follows from the one below it:
//
//   PLAN        two lines on the ground: the ARCADE line (the piers' centres) and the OUTER line (the aisle wall), both
//               running down the bays and on round the apse, which is a half polygon of `apse` sides -- so the hemicycle
//               is more bays of the same system, not a different building bolted on. A NODE is a point on a line where a
//               bay begins; the two lines' nodes pair up across the aisle (on a ray round the apse).
//   SUPPORTS    a pier at every arcade node, with a shaft for every arch or rib that lands on it (the two arcade arches,
//               the aisle's transverse rib, and the vaulting shaft that runs on up the wall to the high vault); a
//               respond on the outer wall's inside and a BUTTRESS on its outside at every outer node.
//   ARCHES      the arcade between the piers; ALL CROWNS LEVEL -- the pointed arch's whole point: a narrow bay of the
//               hemicycle gets a steeper arch to the same crown as a wide bay of the nave (crownHead).
//   ELEVATION   worked out, not given: the aisle vault crowns over the arcade, the aisle roof leans against the wall
//               above it -- and that strip of wall, where the roof stands outside, is the TRIFORIUM inside; the
//               clerestory's sill is over the roof's ridge, the high vault springs within the clerestory.
//   VAULTS      a RIB VAULT over every bay, whatever its plan (ribVault): webs from each side's wall arch up to the
//               keystone, ribs on the creases. Rectangles in the nave and aisles, trapezoids round the ambulatory, a fan
//               of webs in the apse -- one construction.
//   ABUTMENT    a FLYING BUTTRESS from every outer buttress over the aisle roof to the clerestory, where the high vault's
//               thrust comes out, and a PINNACLE weighting the buttress. Round the apse as along the nave: the same rule.
//   COVER       the high roof over the nave and the apse (a gable that ends in a half-polygon hip), the lean-to over the
//               aisles and the ambulatory -- on the same lines.
//
// Everything comes out as parts in the order it is built -- piers, walls, vaults, ribs, buttresses, flyers, roofs -- each
// standing on the one before, which the support check (check.js floating) can follow down to the ground.
import { mesh, earClip, drum, flyerMesh, tieredWall, stackMesh } from "./build.js";

// ---- arcs ----------------------------------------------------------------------------------------------------------
// LEVEL CROWNS: the head of an opening `2a` wide whose crown is `rise` over its springing -- pointed when it rises more
// than half its span (spread from the crown: a two-centred arch's apex is a sqrt(1 + 2 spread) over the springing),
// round when exactly that, segmental when less
export function crownHead(a, rise, per90) {
  if (rise > a * 1.0001) { const k = rise / a; return { profile: "pointed", spread: (k * k - 1) / 2, per90 }; }
  if (rise > a * .9999) return { profile: "semicircular", per90 };
  return { profile: "segmental", rise, per90 };
}
// HALF AN ARCH, springing to crown: from (0, 0) to (d, c), `n` segments even in angle. Rising more than it reaches
// (c >= d) it springs VERTICAL (its centre on the springing line: one side of a pointed arch, a diagonal rib that climbs
// steeply); rising less it arrives LEVEL at the crown (its centre below: a segmental arch, a flat diagonal rib). The
// same function draws every arch and rib of the system, so two that are the same curve have the same points.
export function halfArch(d, c, n) {
  const out = [];
  if (c >= d) {
    const R = (c * c + d * d) / (2 * d), a1 = Math.atan2(c, d - R);
    for (let i = 0; i <= n; i++) { const t = Math.PI + (a1 - Math.PI) * i / n; out.push([R + R * Math.cos(t), R * Math.sin(t)]); }
  } else {
    const R = (d * d + c * c) / (2 * c), a0 = Math.atan2(R - c, -d);
    for (let i = 0; i <= n; i++) { const t = a0 + (Math.PI / 2 - a0) * i / n; out.push([d + R * Math.cos(t), c - R + R * Math.sin(t)]); }
  }
  out[0] = [0, 0]; out[n] = [d, c];
  return out;
}
const lerp2 = (A, B, f) => [A[0] + (B[0] - A[0]) * f, A[1] + (B[1] - A[1]) * f];
const dist2 = (A, B) => Math.hypot(B[0] - A[0], B[1] - A[1]);
// a rib from A (plan) springing at y0 to the keystone K at crown y1: 3D points, n segments
const ribPts = (A, K, y0, y1, n) => halfArch(dist2(A, K), y1 - y0, n).map(([x, y]) => { const f = x / dist2(A, K); const p = lerp2(A, K, f); return [p[0], y0 + y, p[1]]; });
// a wall arch over A -> B rising `rise`: 2n segments, its two halves the same curve mirrored
const archPts = (A, B, y0, rise, n) => {
  const L = dist2(A, B), h = halfArch(L / 2, rise, n);
  const xs = [...h, ...h.slice(0, -1).reverse().map(([x, y]) => [L - x, y])];
  return xs.map(([x, y]) => { const p = lerp2(A, B, x / L); return [p[0], y0 + y, p[1]]; });
};

// ---- the rib vault over any bay -------------------------------------------------------------------------------------
// A BAY of any convex plan, `corners` round it (in the plane: [x, z]), the KEYSTONE `K` where its ribs meet. Each side
// that is a web's (`webs`, side i from corner i to i + 1) has a WALL ARCH rising `rise(i)`; a RIB runs from every corner
// a web touches up to the keystone at `crown`. Each web is the surface between its wall arch and its two ribs -- a Coons
// patch on the three curves, degenerate at the keystone -- so it carries the wall's arch exactly along the wall and meets
// its neighbour exactly along the rib. Over the webs the masonry is filled to a level extrados `top` (as a vault's
// haunches are), so the bay is one closed solid: the webs' soffits, the vertical faces over its sides (a wall arch, or
// for a side that is no web -- the chord of an apse -- its ribs), and the flat top. `n` segments to every half arch and
// rib, whatever its size: the same curve is then the same points wherever two bays meet on it.
export function ribVault(m, { corners, K, spring, crown, rise, webs, top, n, shared = [] }) {
  const N = corners.length, Ky = crown;
  const rib = corners.map((A) => ribPts(A, K, spring, Ky, n));
  const isWeb = new Set(webs);
  const Kv = [K[0], Ky, K[1]];
  const tri = (a, b, c, flip) => (flip ? m.tri(a, c, b) : m.tri(a, b, c));
  // THE SOFFIT, one web at a time, as it was laid: in COURSES, each from a rib across to the wall arch, the k-th
  // course from the k-th point of the rib to the k-th of the arch -- so the web rises with both and never above
  // either, and the last course is the web's RIDGE, level from the arch's crown to the keystone. A web is two such
  // panels, one from each rib to its half of the arch. Each course is laid DOMED, its middle lifted a little over
  // the straight line from rib to wall (`camber` of its length; less toward the ridge), as webs were built to stand.
  const camber = .06;
  for (const i of webs) {
    const A = corners[i], B = corners[(i + 1) % N], arch = archPts(A, B, spring, rise(i), n);
    const halves = [[rib[i], arch.slice(0, n + 1)], [rib[(i + 1) % N], arch.slice(n).reverse()]];
    for (const [r, h] of halves) {
      // the courses' points: rib end, the domed middle, arch end
      const rows = r.map((p, k) => {
        const q = h[k], len = Math.hypot(q[0] - p[0], q[1] - p[1], q[2] - p[2]), lift = camber * len * (1 - .7 * k / n);
        const mid = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + lift, (p[2] + q[2]) / 2];
        return [p, mid, q];
      });
      // (which way round: a quad halfway up must face down, into the bay)
      const k0 = n >> 1, P0 = rows[k0][0], P1 = rows[k0][2], P2 = rows[k0 + 1][0];
      const flip = (P1[2] - P0[2]) * (P2[0] - P0[0]) - (P1[0] - P0[0]) * (P2[2] - P0[2]) > 0;
      const ids = rows.map((row) => row.map((p) => m.vert(p[0], p[1], p[2])));
      for (let k = 0; k < n; k++) for (let c = 0; c < 2; c++) {
        tri(ids[k][c], ids[k][c + 1], ids[k + 1][c + 1], flip);
        tri(ids[k][c], ids[k + 1][c + 1], ids[k + 1][c], flip);
      }
    }
  }
  // the vertical faces round it: over each web's wall arch, and over the ribs along a side that is not a web
  const side = (pts, out) => {          // pts: the curve, left to right in the side's plane; out: [x, z] away from the bay
    const A = [pts[0][0], pts[0][2]], B = [pts[pts.length - 1][0], pts[pts.length - 1][2]], L = dist2(A, B);
    const flat = pts.map((p) => [dist2(A, [p[0], p[2]]), p[1]]);
    const poly = [...flat, [L, top], [0, top]];
    const ids = [...pts.map((p) => m.vert(p[0], p[1], p[2])), m.vert(B[0], top, B[1]), m.vert(A[0], top, A[1])];
    const e = [(B[0] - A[0]) / L, (B[1] - A[1]) / L], nrm = [e[1], -e[0]];       // (the right of A -> B)
    const flip = nrm[0] * out[0] + nrm[1] * out[1] < 0;
    for (const [a, b, c] of earClip(poly, poly.map((_, i) => i))) tri(ids[a], ids[b], ids[c], !flip);
  };
  const ctr = [corners.reduce((s, p) => s + p[0], 0) / N, corners.reduce((s, p) => s + p[1], 0) / N];
  for (let i = 0; i < N; i++) {
    if (shared.includes(i)) continue;                 // (a side the next bay's vault goes on from: the stone is one)
    const A = corners[i], B = corners[(i + 1) % N], mid = lerp2(A, B, .5), out = [mid[0] - ctr[0], mid[1] - ctr[1]];
    if (isWeb.has(i)) side(archPts(A, B, spring, rise(i), n), out);
    else side([...rib[i], ...rib[(i + 1) % N].slice(0, -1).reverse()], out);
  }
  // the extrados: the plan at `top`, facing up
  const ids = corners.map(([x, z]) => m.vert(x, top, z));
  for (const [a, b, c] of earClip(corners, corners.map((_, i) => i))) m.tri(ids[a], ids[c], ids[b]);
  return { ribs: rib, Kv };
}

// A RIB: a box section `w` across and `depth` deep hanging under the curve `pts` (3D, in one vertical plane), set
// `inset` into the stone over it so no slit shows. `side`: 0 centred on the curve, 1 all to one side (`toward`, [x, z]):
// a wall rib hangs on its own bay's side of the wall.
function ribUnder(m, pts, { w, depth, toward = null, inset = .05 }) {
  const A = pts[0], B = pts[pts.length - 1], L = Math.hypot(B[0] - A[0], B[2] - A[2]) || 1;
  const e = [(B[0] - A[0]) / L, 0, (B[2] - A[2]) / L];
  let b = [-e[2], 0, e[0]];
  let u0 = -w / 2, u1 = w / 2;
  if (toward) { if (b[0] * toward[0] + b[2] * toward[1] < 0) b = [-b[0], 0, -b[2]]; u0 = 0; u1 = w; }
  const ring = (i) => {
    const p = pts[i], q = pts[Math.min(i + 1, pts.length - 1)], r = pts[Math.max(i - 1, 0)];
    const T = [q[0] - r[0], q[1] - r[1], q[2] - r[2]], tl = Math.hypot(...T) || 1;
    // the curve's normal in its plane, toward the inside of the arch (down at the crown)
    let nn = [b[1] * T[2] - b[2] * T[1], b[2] * T[0] - b[0] * T[2], b[0] * T[1] - b[1] * T[0]].map((v) => v / tl);
    const toAxis = (0.5 - i / (pts.length - 1));
    if (nn[1] > 1e-6 || (Math.abs(nn[1]) <= 1e-6 && (nn[0] * e[0] + nn[2] * e[2]) * toAxis < 0)) nn = nn.map((v) => -v);
    return [[u0, -inset], [u1, -inset], [u1, depth], [u0, depth]].map(([u, v]) => [p[0] + b[0] * u + nn[0] * v, p[1] + nn[1] * v, p[2] + b[2] * u + nn[2] * v]);
  };
  const rings = pts.map((_, i) => ring(i)), mid = rings.map((r) => avg(r));
  for (let i = 0; i + 1 < rings.length; i++) for (let c = 0; c < 4; c++) {
    const c2 = (c + 1) % 4;
    faceAway(m, [rings[i][c], rings[i + 1][c], rings[i + 1][c2], rings[i][c2]], avg([mid[i], mid[i + 1]]));
  }
  faceAway(m, rings[0], mid[1]);
  faceAway(m, rings[rings.length - 1], mid[rings.length - 2]);
}

// A TURNED STACK at (x, z): `prof` [[r, y]] from the bottom up, `sides` round -- a pier's plinth, base, core and capital
// as one closed solid (stacked drums would share their discs face to face)
function lathe(m, x, z, prof, sides) {
  const ring = (r) => Array.from({ length: sides }, (_, k) => { const t = k * 2 * Math.PI / sides; return [x + r * Math.cos(t), z - r * Math.sin(t)]; });
  return stackMesh(m, prof.map(([r, y]) => ({ pts: ring(r), y })));
}
// A STEPPED PRISM: the outline `prof` [[u, y]] (any simple polygon) in the vertical plane through (x, z) along `o`,
// `hw` thick each side of it along `tg` -- a buttress with its set-offs, one solid
function prismAcross(m, x, z, o, tg, prof, hw) {
  const P = (u, y, s) => [x + o[0] * u + tg[0] * s, y, z + o[1] * u + tg[1] * s];
  let area = 0; for (let i = 0; i < prof.length; i++) { const [u0, y0] = prof[i], [u1, y1] = prof[(i + 1) % prof.length]; area += u0 * y1 - u1 * y0; }
  for (let i = 0; i < prof.length; i++) {
    const [u0, y0] = prof[i], [u1, y1] = prof[(i + 1) % prof.length];
    // the edge's outward normal in the profile's plane (the polygon counter-clockwise: to the edge's right)
    let nu = y1 - y0, ny = -(u1 - u0); if (area < 0) { nu = -nu; ny = -ny; }
    const ps = [P(u0, y0, -hw), P(u1, y1, -hw), P(u1, y1, hw), P(u0, y0, hw)], c = avg(ps);
    faceAway(m, ps, [c[0] - o[0] * nu * .01, c[1] - ny * .01, c[2] - o[1] * nu * .01]);
  }
  const mid = avg(prof.map(([u, y]) => P(u, y, 0)));
  for (const s of [-hw, hw]) for (const [a, b, c] of earClip(prof, prof.map((_, i) => i))) {
    const ps = [a, b, c].map((i) => P(prof[i][0], prof[i][1], s)), cc = avg(ps);
    faceAway(m, ps, [cc[0] - tg[0] * s, cc[1], cc[2] - tg[1] * s]);
  }
  void mid;
}
// a convex planar polygon (3D points) added facing away from `ref` (a point inside the solid it bounds)
const avg = (ps) => [0, 1, 2].map((q) => ps.reduce((s, p) => s + p[q], 0) / ps.length);
function faceAway(m, ps, ref) {
  let nx = 0, ny = 0, nz = 0;
  for (let i = 0; i < ps.length; i++) {
    const [x0, y0, z0] = ps[i], [x1, y1, z1] = ps[(i + 1) % ps.length];
    nx += (y0 - y1) * (z0 + z1); ny += (z0 - z1) * (x0 + x1); nz += (x0 - x1) * (y0 + y1);
  }
  const c = avg(ps), out = nx * (c[0] - ref[0]) + ny * (c[1] - ref[1]) + nz * (c[2] - ref[2]) >= 0;
  const ids = (out ? ps : ps.slice().reverse()).map((p) => m.vert(p[0], p[1], p[2]));
  for (let i = 1; i + 1 < ids.length; i++) m.tri(ids[0], ids[i], ids[i + 1]);
}

// ---- lines and walls along them ---------------------------------------------------------------------------------------
// a polyline offset by `d` to its LEFT (seen from above, walking it), its corners mitred; its two ends square
function offsetLine(pts, d) {
  const n = pts.length, out = [];
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[i], c = pts[Math.min(n - 1, i + 1)];
    const e0 = i > 0 ? norm([b[0] - a[0], b[1] - a[1]]) : null, e1 = i < n - 1 ? norm([c[0] - b[0], c[1] - b[1]]) : null;
    const l0 = e0 && [-e0[1], e0[0]], l1 = e1 && [-e1[1], e1[0]];
    if (!l0) { out.push([b[0] + l1[0] * d, b[1] + l1[1] * d]); continue; }
    if (!l1) { out.push([b[0] + l0[0] * d, b[1] + l0[1] * d]); continue; }
    const bis = [l0[0] + l1[0], l0[1] + l1[1]], k = d / (1 + l0[0] * l1[0] + l0[1] * l1[1]);
    out.push([b[0] + bis[0] * k, b[1] + bis[1] * k]);
  }
  return out;
}
const norm = (v) => { const l = Math.hypot(v[0], v[1]) || 1; return [v[0] / l, v[1] / l]; };

// A WALL ALONG A LINE: `pts` its centre line, `t` thick, each segment a face in TIERS (`faces[i]`: [{ h, openings }]),
// the segments meeting on their mitres (only the line's two ends are drawn). A face's x runs along the CENTRE line from
// its first node, so an opening `at` the middle of a bay is in the middle between the two piers; the two faces of the wall
// are mapped onto it parallel through the middle, the mitres taken up at the ends (as enclosure's are).
export function wallAlong(m, pts, t, faces, glass = null, y0 = 0) {
  const L = offsetLine(pts, t / 2), R = offsetLine(pts, -t / 2);
  const joints = [...new Set(faces.flatMap((tiers) => { let y = 0; return tiers.slice(0, -1).map((b) => (y += b.h)); }))];
  for (let i = 0; i + 1 < pts.length; i++) {
    const C0 = pts[i], C1 = pts[i + 1], Lc = dist2(C0, C1), e = norm([C1[0] - C0[0], C1[1] - C0[1]]);
    const xs = faces[i].flatMap((tr) => tr.openings.flatMap((o) => [o.at - o.width / 2, o.at + o.width / 2]));
    const e1 = Math.min(...xs, Lc / 2), e2 = Math.max(...xs, Lc / 2);
    const sideMap = (P0, P1) => {
      const Ls = dist2(P0, P1), d0 = (P0[0] - C0[0]) * e[0] + (P0[1] - C0[1]) * e[1];
      const par = e1 - d0 > 1e-6 && Ls - e2 + d0 > 1e-6;
      return (x) => { const u = !par ? x * Ls / Lc : x <= e1 ? x * (e1 - d0) / e1 : x >= e2 ? (e2 - d0) + (x - e2) * (Ls - e2 + d0) / (Lc - e2) : x - d0; return lerp2(P0, P1, u / Ls); };
    };
    const mL = sideMap(L[i], L[i + 1]), mR = sideMap(R[i], R[i + 1]);
    const mapAt = (yb) => (x, y, s) => { const p = s ? mR(x) : mL(x); return [p[0], y0 + yb + y, p[1]]; };
    tieredWall(m, Lc, faces[i], mapAt, { ends: [i > 0, i + 2 < pts.length], endCuts: joints, glass });
  }
  return m;
}

// THE ELEVATION, worked out from the plan and the springing -- every height of the building, which its parts are built
// to and other parts may stand on (assemble.js `atopLevel`): the arcade's crown, the aisle's vault, eave and ridge, the
// clerestory's sill, the high vault's springing, keystone and extrados, the eave (`wallTop`) and the ridge
export function basilicaLevels(d) {
  // (`aisles` of them a side, each `aisleW` from pier line to pier line: the lean-to spans them all)
  const a = d.naveW / 2, w = d.aisleW, t = d.t, tA = d.aisleT, Lb = d.bayLen;
  // THE SUPPORTS' MEASURES. The pier: a round core with a shaft for each arch landing on it; its capital at `spring`;
  // its abacus a block wide enough to take the wall over it and the shafts round it -- the arcade's arches spring from
  // the abacus's edge, so its half length along the line IS the half pier the openings leave
  const rs = d.shaft, rc = Math.max(d.pierR, t / 2 + .05), ha = rc + rs * .9, hn = Math.max(t / 2, rc) + rs + .12;
  const spring = d.spring, capH = .9, abH = .3;
  // THE ELEVATION, from the bottom up. The arcade: every arch's crown level, the nave's straight bay's arch equilateral
  const span0 = Lb - 2 * ha;
  if (d.hall) return hallLevels(d, { a, w, t, tA, Lb, rs, rc, ha, hn, spring, capH, abH, span0 });
  const arcadeCrown = spring + (d.arcadeRise ?? span0 / 2 * Math.sqrt(3));
  // the aisle vault springs from the capitals and crowns just over the arcade's arches; its extrados a fill over that
  const vT = d.vaultT, aisleCrown = arcadeCrown + .35, aisleTop = aisleCrown + vT;
  // the aisle wall stands to its vault's extrados, the lean-to roof from there up against the clerestory wall
  const aisleEave = aisleTop + .3, roofT = .35;
  const aisleRun = Math.max(1, Math.round(d.aisles ?? 1)) * w + tA / 2 + d.overhang - t / 2, aisleRidge = aisleEave + aisleRun * Math.tan(d.aislePitch * Math.PI / 180);
  // THE TRIFORIUM is the strip of wall the aisle roof stands against: inside, from over the arcade to the clerestory sill
  const clerSill = aisleRidge + .5;
  // the high vault springs a little over the clerestory sill; its keystone at `vaultRise` over that (the transverse
  // arch across the nave's clear width equilateral unless said)
  const half = a - t / 2, vSpring = clerSill + d.clerSpring, crown = vSpring + (d.vaultRise ?? half * Math.sqrt(3) * .9);
  const vTop = crown + vT, wallTop = vTop + .3;
  const ridge = wallTop + (a + t / 2 + d.overhang) * Math.tan(d.pitch * Math.PI / 180);
  return { rs, rc, ha, hn, spring, capH, abH, arcadeCrown, vT, aisleCrown, aisleTop, aisleEave, roofT, aisleRidge, clerSill,
           half, vSpring, crown, vTop, wallTop, ridge };
}
// A HALL CHURCH's elevation (`hall`: St Stephen's, St Elisabeth's at Marburg, the Frauenkirche): nave and aisles vaulted
// from the same capitals -- the piers carry the vaults directly, no wall over the arcade but the strip between the
// arch and the vaults, no clerestory, no aisle roof. The aisles' keystones as high as the nave's (or `aisleDrop`
// under them: a stepped hall), the arcade's arch as high as the vaults' wall arches over it allow, the outer wall
// standing to the vaults' extrados with its windows rising under the aisle vault -- the light comes in from the
// sides -- and one roof over all three vessels, its eaves on the outer walls
function hallLevels(d, m) {
  const { a, w, t, tA, Lb, spring, span0 } = m, nA = Math.max(1, Math.round(d.aisles ?? 1));
  const vT = d.vaultT, half = a - t / 2, vSpring = spring, crown = vSpring + (d.vaultRise ?? half * Math.sqrt(3) * .9);
  const aisleCrown = crown - (d.aisleDrop ?? 0), vTop = crown + vT, aisleTop = aisleCrown + vT;
  // (the arcade's arch rises under the lower of the two wall arches over it, the nave's and the aisle's)
  const arcadeCrown = spring + (d.arcadeRise ?? Math.min(wallRise(Lb - t, crown, spring), wallRise(Lb - t, aisleCrown, spring), span0 / 2 * 2.4) - .4);
  const wallTop = vTop + .3, roofT = .35;
  const ridge = wallTop + (a + nA * w + tA / 2 + d.overhang) * Math.tan(d.pitch * Math.PI / 180);
  return { ...m, arcadeCrown, vT, aisleCrown, aisleTop, aisleEave: wallTop, roofT, aisleRidge: wallTop, clerSill: vTop,
           half, vSpring, crown, vTop, wallTop, ridge };
}
// the wall arch along a side: level with the keystone where it can be (a short side is a lancet to it); never more
// than steep enough to stand as a lancet of 1:2.4
const wallRise = (L, crownY, springY) => Math.min(crownY - springY, L / 2 * 2.4);

// ---- the building ---------------------------------------------------------------------------------------------------
// def: { bays, bayLen, naveW (between the arcade's centre lines), aisleW (pier line to pier line), aisles (1, or 2: a line of
// free-standing piers between them), flyerStages (over double aisles: 2, an intermediate pier, or 1, one leap), apse (sides of the
// half polygon; 0: a flat east end), t (the arcade and clerestory walls), aisleT, spring (the arcade's capitals),
// skipAisle: [[from, to]] (bays from the west with no aisle vault, wall, buttress or roof: a tower stands there),
// skipOuter: [[from, to]] (no outer wall, buttress or aisle roof, the vault kept: a transept), pitch, aislePitch,
// flyers (true), pinnacles (true), wimpergs (false: gables over the aisle windows and transept portals), lights (triforium openings a bay), hall (a HALL CHURCH: aisles vaulted to the nave's
// height -- `aisleDrop` under it -- no clerestory, no flyers, one roof over all; see hallLevels), skipButtress: [[from, to]]
// (straight nodes from the west with no buttress: a tower against the wall there) ... } -- numbers already evaluated (P).
// Returns { parts: [{ name, geometry (mesh), kind, glass? }], plan } in the system's own frame: the nave's axis along z,
// its west end at +z (node 0), the apse's centre at z = -bays * bayLen / 2.
export function basilica(d, per90) {
  const n = Math.max(2, per90);                       // segments to every half arch and rib (see ribVault)
  const a = d.naveW / 2, w = d.aisleW, t = d.t, tA = d.aisleT, Lb = d.bayLen, B = d.bays, Lz = B * Lb, zE = -Lz / 2;
  // DOUBLE AISLES (`aisles: 2`, Notre-Dame's and Cologne's five vessels): a line of free-standing piers between each two,
  // `aisleW` apart -- the same polygon round the apse, so a double aisle turns into a double ambulatory
  const nA = Math.max(1, Math.round(d.aisles ?? 1)), sides = d.apse, outerR = a + nA * w, bd = d.buttressD, bdT = bd * .8;
  // THE PLAN: the two lines, left side (x < 0) from the west down the nave, round the apse, and back up the right side
  const zs = Array.from({ length: B + 1 }, (_, i) => Lz / 2 - i * Lb);
  const ring = (r) => Array.from({ length: Math.max(0, sides - 1) }, (_, k) => { const th = Math.PI - (k + 1) * Math.PI / sides; return [r * Math.cos(th), zE - r * Math.sin(th)]; });
  const line = (r) => sides > 0
    ? [...zs.map((z) => [-r, z]), ...ring(r), ...zs.slice().reverse().map((z) => [r, z])]
    : [...zs.map((z) => [-r, z]), ...zs.slice().reverse().map((z) => [r, z])];
  const arc = line(a), out = line(outerR), mids = Array.from({ length: nA - 1 }, (_, j) => line(a + (j + 1) * w));
  const NN = arc.length;
  // which nodes and bays are which: straight left 0..B, apse B..B+sides, straight right after; a bay i is arc[i] -> arc[i+1]
  const bayKind = (i) => (i < B ? "nave" : i < B + Math.max(sides, 1) ? (sides > 0 ? "apse" : "east") : "nave");
  const westIndex = (i) => (i < B ? i : i >= NN - 1 - B ? NN - 2 - i : -1);   // a straight bay's number from the west
  const inSkip = (list, i) => { const k = westIndex(i); return k >= 0 && (list ?? []).some(([f, to]) => k >= f && k <= to); };
  // THE TRANSEPT crosses the nave over the straight bays `transept` [from, to] (counted from the west): there the aisle
  // runs into the transept's arm, the piers between the four of the crossing are left out, and the crossing is vaulted
  // as one square
  if (d.hall && d.transept) throw new Error("basilica: a hall church has no transept here");
  const X = d.transept ?? null, xNode = (k) => (k <= B ? k : NN - 1 - k);           // a straight node's number from the west
  const inCross = (i) => X !== null && westIndex(i) >= X[0] && westIndex(i) <= X[1];
  const crossInterior = (k) => X !== null && (k <= B || k >= NN - 1 - B) && xNode(k) > X[0] && xNode(k) < X[1] + 1;
  const hasAisle = (i) => inCross(i) ? false : sides > 0 || bayKind(i) === "nave" ? !inSkip(d.skipAisle, i) : false;
  const hasOuter = (i) => hasAisle(i) && !inSkip(d.skipOuter, i) && (sides > 0 || bayKind(i) === "nave");
  // (a flat east end: the bay across the east end is the east wall's, not an arcade's)
  const arcadeBay = (i) => sides > 0 || bayKind(i) === "nave";
  // the node's outward direction: from the axis (round the apse, from its centre) out across the aisle
  const normal = (k) => { const [x, z] = arc[k]; return z < zE - 1e-9 ? norm([x, z - zE]) : [Math.sign(x), 0]; };

  const { rs, rc, ha, hn, spring, capH, abH, arcadeCrown, vT, aisleCrown, aisleTop, aisleEave, roofT, aisleRidge, clerSill,
          half, vSpring, crown, vTop, wallTop, ridge: ridgeY } = basilicaLevels(d);

  const parts = [];
  const add = (name, m, kind, extra = {}) => { if (m.counts.tris) parts.push({ name, geometry: m, kind, ...extra }); };
  const glass = mesh();
  // (its windows traceried -- tracery.js -- unless it says not: lights as many as each span allows)
  const tr = d.tracery === false ? {} : { tracery: {} };
  // (and dressed, if it says how: surround.js -- a Romanesque church's windows recessed in orders)
  const dress = d.surround ? { surround: d.surround } : {};
  // (and a WIMPERG over each aisle window and transept portal if it says so -- wimperg.js; `wi(side)`: on the face's
  // front (0) or back (1), whichever is the outside)
  const wi = (side) => (d.wimpergs ? { wimperg: side ? { side: true } : {} } : {});

  // ---- PIERS: one at every arcade node, built for the angle the line turns there
  const piers = mesh(), shafts = mesh(), caps = mesh();
  const sideN = per90 >= 4 ? 12 : 8;
  // a drum at (x, z): a shaft, a core, a capital
  const drumAt = (m, x, z, r0, r1, y0, y1, k) => { const q = mesh(); drum(q, r0, r1, y0, y1, k); appendAt(m, q, x, z); };
  const blockAt = (m, x, z, e, nrm, hx, hz, y0, y1) => {     // a block centred at (x, z), hx along e, hz along nrm
    const c = [[-hx, -hz], [hx, -hz], [hx, hz], [-hx, hz]].map(([u, v]) => [x + e[0] * u + nrm[0] * v, z + e[1] * u + nrm[1] * v]);
    const lo = c.map(([px, pz]) => [px, y0, pz]), hi = c.map(([px, pz]) => [px, y1, pz]), ref = [x, (y0 + y1) / 2, z];
    faceAway(m, lo, ref); faceAway(m, hi, ref);
    for (let k = 0; k < 4; k++) faceAway(m, [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]], ref);
  };
  // a PIER at (x, z) on a line turning from dIn to dOut, `o` out from the axis: its plinth, its base, core and capital
  // turned as one, a shaft under every arch that lands on it (`dirs`), its abacus square to the node
  const pierAt = (x, z, o, dirs) => {
    const tg = [o[1], -o[0]];
    drumAt(piers, x, z, rc + rs + .3, rc + rs + .3, 0, .45, 8);
    lathe(piers, x, z, [[rc + rs + .12, .45], [rc + .02, .75], [rc, .75], [rc, spring - capH], [rc + rs, spring - capH], [rc + rs + .28, spring - abH]], sideN);
    for (const dv of dirs) drumAt(shafts, x + dv[0] * rc, z + dv[1] * rc, rs, rs, .45, spring - capH, 6);
    blockAt(caps, x, z, tg, o, ha, hn, spring - abH, spring);
  };
  const along = (L, k) => { const [x, z] = L[k], prev = L[k - 1], next = L[k + 1];
    return [prev ? norm([prev[0] - x, prev[1] - z]) : null, next ? norm([next[0] - x, next[1] - z]) : null]; };
  for (let k = 0; k < NN; k++) {
    // (the flat east end's corners are the east wall's, not piers)
    if (sides === 0 && (k === B || k === B + 1)) continue;
    if (crossInterior(k)) continue;                   // (the crossing is open from pier to pier)
    const [x, z] = arc[k], o = normal(k), tg = [o[1], -o[0]];
    // a shaft under each arch: along the line both ways, out to the aisle's vault, in to the nave's
    const aisled = hasAisle(Math.min(k, NN - 2)) || hasAisle(Math.max(0, k - 1));
    pierAt(x, z, o, [...along(arc, k), aisled ? o : null, [-o[0], -o[1]]].filter(Boolean));
    // the VAULTING SHAFT: from the abacus up the clerestory wall's inner face to the high vault's springing, its capital there
    // (a hall's vaults spring from the piers' own capitals)
    if (d.hall) continue;
    const vx = x - o[0] * (t / 2 + rs * .5), vz = z - o[1] * (t / 2 + rs * .5);
    lathe(shafts, vx, vz, [[rs, spring], [rs, vSpring - .5], [rs + .2, vSpring - .15]], 6);
    blockAt(caps, vx, vz, tg, o, rs + .25, rs + .25, vSpring - .15, vSpring);
  }
  // ...and between two aisles, free-standing piers wherever an aisle bay begins or ends: a shaft every way, an arch or a
  // rib landing on each
  for (const L of mids) for (let k = 0; k < NN; k++) {
    if (sides === 0 && (k === B || k === B + 1)) continue;
    if (!hasAisle(Math.min(k, NN - 2)) && !hasAisle(Math.max(0, k - 1))) continue;
    const [x, z] = L[k], o = normal(k);
    pierAt(x, z, o, [...along(L, k), o, [-o[0], -o[1]]].filter(Boolean));
  }
  add("piers", piers, "column"); add("shafts", shafts, "column"); add("capitals", caps, "column");

  // ---- THE ARCADE WALL: from the abacus up to the high roof's eave -- arcade arch, triforium, clerestory window
  const arcadeFaces = [], wallNodes = [];
  for (let i = 0; i + 1 < NN; i++) {
    if (crossInterior(i)) continue;
    wallNodes.push(i);
    if (inCross(i)) {
      // THE CROSSING ARCH: the wall over the crossing piers opens on the transept arm's vault, its own section --
      // as wide as the arm between its side walls, springing with the high vault, to the same keystone
      let j = i + 1; while (crossInterior(j)) j++;
      const Lc = dist2(arc[i], arc[j]), cw = Lc - t;
      arcadeFaces.push([{ h: 0, openings: [{ at: Lc / 2, width: cw, sill: 0, springing: vSpring - spring, head: crownHead(cw / 2, crown - vSpring, per90), glass: false }] }]);
      continue;
    }
    const Lc = dist2(arc[i], arc[i + 1]);
    if (!arcadeBay(i)) { arcadeFaces.push([{ h: 0, openings: [] }]); continue; }
    const ow = Lc - 2 * ha, tiers = [];
    const arcH = arcadeCrown - spring + .4;
    tiers.push({ h: arcH, openings: [{ at: Lc / 2, width: ow, sill: 0, springing: 0, head: crownHead(ow / 2, arcadeCrown - spring, per90), glass: false }] });
    // the triforium: a row of small arches in the strip the aisle roof stands against outside (open to the roof space
    // behind it: unglazed), when it is tall enough to hold one
    // (a hall's arcade wall is only the strip from the arch up to the vaults')
    if (d.hall) { tiers.push({ openings: [] }); arcadeFaces.push(tiers); continue; }
    const triH = clerSill - spring - arcH;
    const lights = Math.max(0, Math.round(d.lights * Lc / Lb));
    if (triH > 1.6 && lights > 0) {
      const lw = Math.min(1.1, (Lc - 2 * ha) / lights * .6), gap = (Lc - 2 * ha) / lights;
      const lh = Math.min(triH - .9, 2.6), sp = Math.max(.1, lh - lw / 2 * Math.sqrt(3));
      tiers.push({ h: triH, openings: Array.from({ length: lights }, (_, q) => ({ at: ha + gap * (q + .5), width: lw, sill: .45, springing: .45 + sp,
                                                                               head: crownHead(lw / 2, lh - sp, per90), glass: false })) });
    } else tiers.push({ h: Math.max(.3, triH), openings: [] });
    // the clerestory window: from the sill up under the high vault's wall arch, as wide as the bay allows
    const formRise = wallRise(Lc - 2 * (rs + .25), crown, vSpring), winW = Math.max(.6, Lc - 2 * ha - .5);
    const winCrown = vSpring + formRise - .45 - clerSill, winSpring = Math.max(.3, winCrown - winW / 2 * Math.sqrt(3) * .9);
    tiers.push({ openings: winCrown - winSpring > .2 ? [{ at: Lc / 2, width: winW, sill: .25, springing: winSpring, head: crownHead(winW / 2, winCrown - winSpring, per90), glass: true, ...tr, ...dress }] : [],
                 ...(d.lombard ? { lombard: d.lombard } : {}) });
    arcadeFaces.push(tiers);
  }
  const arcadeTop = (d.hall ? vTop : wallTop) - spring;
  const fix = arcadeFaces.map((tiers) => { const used = tiers.slice(0, -1).reduce((s, q) => s + q.h, 0); return tiers.map((q, j) => (j === tiers.length - 1 ? { ...q, h: arcadeTop - used } : q)); });
  const awall = mesh();
  wallNodes.push(NN - 1);
  wallAlong(awall, wallNodes.map((k) => arc[k]), t, fix, glass, spring);
  add("arcade", awall, "wall");

  // ---- THE OUTER WALL: the aisle's and the ambulatory's, a window a bay between the buttresses; responds inside it
  const runs = [];                                   // the outer line cut where a bay has no outer wall
  for (let i = 0; i + 1 < NN; i++) {
    if (!hasOuter(i)) continue;
    const last = runs[runs.length - 1];
    if (last && last.to === i) { last.to = i + 1; last.bays.push(i); } else runs.push({ from: i, to: i + 1, bays: [i] });
  }
  const responds = mesh(), owallM = mesh();
  const winA = { sill: d.aisleSill, top: aisleCrown - .5 };
  // (the wall's own height: to the aisle roof's eave)
  for (const r of runs) {
    const pts = out.slice(r.from, r.to + 1);
    const faces = r.bays.map((i) => {
      const Lc = dist2(out[i], out[i + 1]), ww = Math.min(d.aisleWin, Lc - d.buttressW - 1.2);
      const spr = Math.max(winA.sill + .5, winA.top - ww / 2 * Math.sqrt(3));
      return [{ h: aisleEave, openings: ww > .5 ? [{ at: Lc / 2, width: ww, sill: winA.sill, springing: spr, head: crownHead(ww / 2, winA.top - spr, per90), glass: true, ...tr, ...wi(1), ...dress }] : [],
                ...(d.aisleLombard ? { lombard: d.aisleLombard } : {}) }];
    });
    wallAlong(owallM, pts, tA, faces, glass, 0);
  }
  add("aisle wall", owallM, "wall");
  // a respond (a half shaft and its capital) on the wall's inside at every node a vault of the aisle springs from
  const outerNodes = new Set();
  for (let i = 0; i + 1 < NN; i++) if (hasAisle(i)) { outerNodes.add(i); outerNodes.add(i + 1); }
  for (const k of outerNodes) {
    const [x, z] = out[k], o = normal(k);
    const px = x - o[0] * tA / 2, pz = z - o[1] * tA / 2;
    lathe(responds, px, pz, [[.32, 0], [.32, spring - capH], [.55, spring - abH]], 8);
    blockAt(responds, px - o[0] * .2, pz - o[1] * .2, [o[1], -o[0]], o, .55, .45, spring - abH, spring);
  }
  add("responds", responds, "column");

  // ---- THE VAULTS. The high vault: a bay of the nave between each pair of arcade nodes facing each other, and the apse
  // a fan of webs round its keystone; the corners on the walls' inner faces, the ribs springing from the vaulting shafts
  const inner = offsetLine(arc, t / 2);               // (the arcade line's LEFT, walking it, is the nave side)
  const outerFace = offsetLine(arc, -t / 2);          // ...and its right the aisle side
  const outInner = offsetLine(out, tA / 2);           // the outer wall's inside face
  const left = (i) => i, right = (i) => NN - 1 - i;   // straight node i from the west, on each side
  const hv = mesh(), hr = mesh(), av = mesh(), ar = mesh();
  const RIB = { w: d.ribW, depth: d.ribD }, TR = { w: d.ribW * 1.35, depth: d.ribD * 1.2 };
  // the nave's cells from the west: one a bay, the crossing one cell over all its bays
  const cells = [];
  for (let i = 0; i < B; i++) {
    if (X !== null && i > X[0] && i <= X[1]) continue;
    cells.push({ i, j: X !== null && i === X[0] ? X[1] + 1 : i + 1, crossing: X !== null && i === X[0] });
  }
  const bands = mesh();
  cells.forEach(({ i, j, crossing }, q) => {
    // (the crossing's corners at its piers' faces: the arm's side walls run on from them, and a band of arch as
    // thick as the wall divides it from the nave's bays either side)
    const dz = crossing ? t / 2 : 0;
    const c = [inner[left(i)], inner[left(j)], inner[right(j)], inner[right(i)]].map(([x, z], k) => [x, z + (k === 0 || k === 3 ? -dz : dz)]);
    const K = [(c[0][0] + c[2][0]) / 2, (c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4];
    const rise = (s) => (s === 1 || s === 3 || crossing ? crown - vSpring : wallRise(dist2(c[s], c[(s + 1) % 4]), crown, vSpring));
    const prev = cells[q - 1], next = cells[q + 1];
    const shared = [...(prev && !prev.crossing && !crossing ? [3] : []), ...((next ? !next.crossing && !crossing : sides > 0) ? [1] : [])];
    const v = ribVault(hv, { corners: c, K, spring: vSpring, crown, rise, webs: [0, 1, 2, 3], top: vTop, n, shared });
    for (const k of [0, 1, 2, 3]) ribUnder(hr, v.ribs[k], RIB);
    // the transverse arch on its west side (the next bay's is its east side; the last bay's is the apse's chord)
    if (!crossing && !(prev && prev.crossing)) ribUnder(hr, archPts(c[3], c[0], vSpring, crown - vSpring, n), TR);
    for (const s of [0, 2]) ribUnder(hr, archPts(c[s], c[(s + 1) % 4], vSpring, rise(s), n), { w: d.ribW * .8, depth: d.ribD * .8, toward: [K[0] - c[s][0], K[1] - c[s][1]] });
    if (!next && sides === 0) ribUnder(hr, archPts(c[1], c[2], vSpring, crown - vSpring, n), TR);
    if (crossing) for (const zc of [arc[left(i)][1], arc[left(j)][1]]) {
      // the crossing's transverse arches: a wall across the nave from vault springing to extrados, open to the vault's section
      // (its ends run on into the arcade walls, over the crossing arches' jambs)
      const L = 2 * half, e = a + t / 2;
      wallAlong(bands, [[-e, zc], [e, zc]], t, [[{ h: vTop - vSpring, openings: [{ at: e, width: L, sill: 0, springing: 0, head: crownHead(L / 2, crown - vSpring, per90), glass: false }] }]], null, vSpring);
    }
  });
  add("crossing arches", bands, "wall");
  if (sides > 0) {
    // the apse: the inner face's nodes round the hemicycle, the keystone on the chord between the first and the last
    const ids = Array.from({ length: sides + 1 }, (_, k) => B + k);
    const c = ids.map((k) => inner[k]).reverse();      // (round from the right side: the polygon's own winding)
    const K = lerp2(c[0], c[c.length - 1], .5);
    const webs = Array.from({ length: sides }, (_, k) => k);
    const v = ribVault(hv, { corners: c, K, spring: vSpring, crown, rise: (s) => wallRise(dist2(c[s], c[s + 1]), crown, vSpring), webs, top: vTop, n, shared: B > 0 ? [sides] : [] });
    for (let k = 1; k < sides; k++) ribUnder(hr, v.ribs[k], RIB);
    ribUnder(hr, [...v.ribs[0], ...v.ribs[sides].slice(0, -1).reverse()], TR);            // the chord: the last transverse arch
    for (const s of webs) ribUnder(hr, archPts(c[s], c[s + 1], vSpring, wallRise(dist2(c[s], c[s + 1]), crown, vSpring), n),
                                   { w: d.ribW * .8, depth: d.ribD * .8, toward: [K[0] - c[s][0], K[1] - c[s][1]] });
  }
  add("high vault", hv, "groin", { abutted: true }); add("high ribs", hr, "ribs");
  // the aisle and the ambulatory: a bay between two arcade nodes and the two outer nodes facing them -- a rectangle in the
  // aisles, a trapezoid round the apse -- its keystone where its diagonals cross
  // (with double aisles, a ring of bays to each: from the arcade wall's face to the piers' line, from there to the outer
  //  wall's inside -- the two meeting over the arches between the free-standing piers, one stone, an arch rib under it)
  const rows = [outerFace, ...mids, outInner];
  for (let j = 0; j < nA; j++) for (let i = 0; i + 1 < NN; i++) {
    if (!hasAisle(i)) continue;
    const I = rows[j], O = rows[j + 1], c = [I[i], O[i], O[i + 1], I[i + 1]];
    const K = cross(c[0], c[2], c[1], c[3]);
    const rise = (s) => wallRise(dist2(c[s], c[(s + 1) % 4]), aisleCrown, spring);
    const shared = [...(i > 0 && hasAisle(i - 1) ? [0] : []), ...(i + 2 < NN && hasAisle(i + 1) ? [2] : []), ...(j + 1 < nA ? [1] : []), ...(j > 0 ? [3] : [])];
    const v = ribVault(av, { corners: c, K, spring, crown: aisleCrown, rise, webs: [0, 1, 2, 3], top: aisleTop, n, shared });
    for (const q of [0, 1, 2, 3]) ribUnder(ar, v.ribs[q], RIB);
    ribUnder(ar, archPts(c[0], c[1], spring, rise(0), n), TR);
    if (!hasAisle(i + 1)) ribUnder(ar, archPts(c[2], c[3], spring, rise(2), n), TR);
    if (j + 1 < nA) ribUnder(ar, archPts(c[1], c[2], spring, rise(1), n), TR);
  }
  add("aisle vault", av, "groin", { abutted: true }); add("aisle ribs", ar, "ribs");

  // ---- THE TRANSEPT'S ARMS, either side of the crossing: the same vessel turned across -- side walls on the crossing
  // piers' lines, open below to the aisles they cross, a clerestory over the aisles' roofs, rib vaults at the nave's
  // height, an end wall with a portal and a rose, angle buttresses at its corners, and a roof across at the nave's
  const tw = mesh(), tb = mesh(), te = mesh(), tbut = mesh(), tpin = mesh(), troof = mesh();
  if (X !== null) {
    const zA = zs[X[0]], zB = zs[X[1] + 1], Lx = zA - zB, tE = d.transeptT ?? t * 1.4;
    const xOut = outerR + tA / 2 + (d.arm ?? 0), xIn = xOut - tE;       // the end wall's outer and inner faces
    const W = Lx - t;                                                  // the arm's clear width, between its side walls
    for (const sx of [-1, 1]) {
      // the cells: over the aisle's width, and on to the end wall when the arm projects far enough to make a bay of
      // its own -- otherwise one cell from the crossing to the end wall
      // (one more over each line of piers between double aisles)
      const x0 = a + t / 2, rM = mids.map((_, j) => a + (j + 1) * w);
      const xs = xIn - (outerR + tA / 2) > .4 * W ? [x0, ...rM, outerR, xIn] : [x0, ...rM, xIn];
      for (let q = 0; q + 1 < xs.length; q++) {
        const c = [[sx * xs[q], zA - t / 2], [sx * xs[q + 1], zA - t / 2], [sx * xs[q + 1], zB + t / 2], [sx * xs[q], zB + t / 2]];
        const K = [sx * (xs[q] + xs[q + 1]) / 2, (zA + zB) / 2];
        const rise = (s) => wallRise(dist2(c[s], c[(s + 1) % 4]), crown, vSpring);
        const shared = [...(q > 0 ? [3] : []), ...(q + 2 < xs.length ? [1] : [])];
        const v = ribVault(hv, { corners: c, K, spring: vSpring, crown, rise, webs: [0, 1, 2, 3], top: vTop, n, shared });
        for (const k of [0, 1, 2, 3]) ribUnder(hr, v.ribs[k], RIB);
        ribUnder(hr, archPts(c[1], c[2], vSpring, rise(1), n), TR);   // (its far side: the next cell's near one, or the end wall's)
        for (const s of [0, 2]) ribUnder(hr, archPts(c[s], c[(s + 1) % 4], vSpring, rise(s), n), { w: d.ribW * .8, depth: d.ribD * .8, toward: [K[0] - c[s][0], K[1] - c[s][1]] });
      }
      // THE SIDE WALLS on the crossing piers' lines: over the aisle an arch as high as the aisle's vault, the
      // clerestory over the aisle roof that leans on it; beyond the aisle wall, the arm's own wall from the ground
      for (const zc of [zA, zB]) {
        // (an arch over each aisle it crosses -- from the arcade wall, or a free-standing pier's abacus, to the next)
        const rs2 = [a, ...rM, outerR];
        const faces = rs2.slice(0, -1).map((r0, j) => {
          const e0 = j === 0 ? t / 2 : ha, e1 = j + 2 === rs2.length ? tA / 2 : ha, L1 = rs2[j + 1] - r0, op = L1 - e0 - e1, mid = e0 + op / 2;
          const winW = Math.min(op - 1.5, 3.2), wTop = crown - .6 - clerSill;
          const ws = Math.max(.5, wTop - winW / 2 * Math.sqrt(3) * .9);
          const upper = { h: wallTop - clerSill, openings: winW > .6 && wTop - ws > .3 ? [{ at: mid, width: winW, sill: .3, springing: ws, head: crownHead(winW / 2, wTop - ws, per90), glass: true, ...tr }] : [] };
          const lower = { h: clerSill - spring, openings: [{ at: mid, width: op, sill: 0, springing: 0, head: crownHead(op / 2, wallRise(op, aisleCrown, spring), per90), glass: false }] };
          return [lower, upper];
        });
        wallAlong(tw, rs2.map((r) => [sx * r, zc]), t, faces, glass, spring);
        if (xIn - outerR > .3) {
          const L2 = xIn - outerR, ww = Math.min(L2 - 1.6, d.aisleWin), spr = Math.max(d.aisleSill + .5, aisleCrown - .5 - ww / 2 * Math.sqrt(3));
          const ops = ww > .6 ? [{ at: L2 / 2, width: ww, sill: d.aisleSill, springing: spr, head: crownHead(ww / 2, aisleCrown - .5 - spr, per90), glass: true, ...tr }] : [];
          wallAlong(te, [[sx * outerR, zc], [sx * xIn, zc]], t, [[{ h: wallTop, openings: ops }]], glass, 0);
        }
      }
      // THE END WALL: a portal, and over it a rose as wide as the wall allows under the eave
      {
        const xc = sx * (xIn + tE / 2), z0 = zA + t / 2, z1 = zB - t / 2, L = z0 - z1;
        const pw = Math.min(5, W / 3), pTop = arcadeCrown - 1, pSpr = pTop - pw / 2 * Math.sqrt(3);
        const h1 = arcadeCrown + .6, D = Math.min(W - 2.4, wallTop - h1 - 1.6);
        const tiers = [{ h: h1, openings: [{ at: L / 2, width: pw, sill: 0, springing: pSpr, head: crownHead(pw / 2, pTop - pSpr, per90), glass: false, ...wi(0) }] },
                       { h: wallTop - h1, openings: D > 1 ? [{ at: L / 2, width: D, sill: (wallTop - h1) / 2, springing: (wallTop - h1) / 2, head: { profile: "semicircular", per90 }, foot: { profile: "semicircular", per90 }, glass: true, ...tr }] : [] }];
        // (walked so its front is outward: the left of the line is +x on the right arm)
        const ln = sx > 0 ? [[xc, z0], [xc, z1]] : [[xc, z1], [xc, z0]];
        wallAlong(tb, ln, tE, [tiers], glass, 0);
        // the angle buttresses: one on each corner, on the side walls' lines carried out past the end
        for (const zc of [zA, zB]) {
          const H = wallTop - 1.5, u0 = xOut, P2 = [[u0, 0], [u0 + bdT, 0], [u0 + bdT, H * .4], [u0 + bdT * .72, H * .4], [u0 + bdT * .72, H * .75], [u0 + bdT * .5, H * .75], [u0 + bdT * .5, H], [u0, H]];
          prismAcross(tbut, 0, zc, [sx, 0], [0, 1], P2, d.buttressW / 2);
          if (d.pinnacles) { const pw2 = Math.min(d.buttressW, bdT * .5) * .8, cx = sx * (u0 + bdT * .25);
            blockAt(tpin, cx, zc, [0, 1], [sx, 0], pw2 / 2, pw2 / 2, H, H + pw2 * 1.6);
            spireAt(tpin, cx, zc, [0, 1], [sx, 0], pw2 / 2 + .08, H + pw2 * 1.6, H + pw2 * 4.8); }
        }
      }
    }
    // THE ROOF ACROSS: a gable from end to end, its eaves on the side walls at the nave's eave height
    {
      const e0 = zA + t / 2 + d.overhang, e1 = zB - t / 2 - d.overhang, rY = wallTop + (e0 - e1) / 2 * Math.tan(d.pitch * Math.PI / 180), zm = (e0 + e1) / 2;
      const xr = xOut + d.overhang, sec = [[e0, wallTop], [zm, rY], [e1, wallTop]];
      const P3 = (x, [z, y]) => [x, y, z], ref = [0, wallTop + .1, zm];
      for (let k = 0; k < 3; k++) faceAway(troof, [P3(-xr, sec[k]), P3(xr, sec[k]), P3(xr, sec[(k + 1) % 3]), P3(-xr, sec[(k + 1) % 3])], [0, (wallTop * 2 + rY) / 3, zm]);
      for (const x of [-xr, xr]) faceAway(troof, sec.map((q) => P3(x, q)), [0, (wallTop * 2 + rY) / 3, zm]);
      void ref;
    }
  }
  add("transept arcade", tw, "wall"); add("transept walls", te, "wall"); add("transept ends", tb, "wall");
  add("transept buttresses", tbut, "buttress"); add("transept pinnacles", tpin, "pinnacle"); add("transept roof", troof, "roof");

  // ---- BUTTRESSES at the outer nodes, flyers to the clerestory, pinnacles on them
  const bw = d.buttressW, flyW = d.flyW;
  const bm = mesh(), fm = mesh(), pm = mesh();
  // A FLIGHT of a flyer: from a pier face at `x0` (out from the axis) in to `x1`, landing at `high` -- springing as low as
  // it may over the aisle roof under its foot (the lean-to: its ridge against the clerestory, its eave over the outer wall),
  // its top a ramp up to 1.5m over where it lands. Returns its measures and the height its pier must reach.
  const roofAt = (x) => aisleRidge + (aisleEave - aisleRidge) * (x - (a + t / 2)) / (outerR + tA / 2 + d.overhang - (a + t / 2));
  const flight = (x0, x1, high) => {
    const span = x0 - x1, low = Math.max(roofAt(x0) + 1, high - span * .8), top1 = high + 1.5, top0 = Math.max(low + 1.2, top1 - span * .45);
    return { span, low, high, top0, top1, pierTop: top0 + .4 };
  };
  // the flyer lands where the high vault's thrust comes out: a quarter of the way up from its springing to its keystone.
  // Over double aisles it is TWO flights (`flyerStages`, Cologne's): an intermediate pier rises from the piers between the
  // aisles over their roof, the upper flight leans from it on the clerestory, the lower from the outer buttress on it --
  // a quarter of the way down its height, where the upper one's thrust comes into it
  const high = vSpring + (crown - vSpring) * .25, stages = nA > 1 ? Math.max(1, Math.min(2, Math.round(d.flyerStages ?? 2))) : 1;
  const rMid = a + (nA - 1) * w, md = Math.min(w * .2, bd * .3);           // the intermediate pier's line and half depth
  const fUp = stages > 1 ? flight(rMid - md, a + t / 2, high) : null;
  const fOut = stages > 1 ? flight(outerR + tA / 2, rMid + md, fUp.low + .2) : flight(outerR + tA / 2, a + t / 2, high);
  // (a hall's buttresses take the vaults' thrust alone, in the wall's plane: they stand to just under the eave)
  const pierTop = d.hall ? wallTop - .6 : fOut.pierTop, midTop = fUp ? fUp.pierTop : 0;
  // (no buttress where something else stands against the wall: a tower beside a hall -- `skipButtress`, straight nodes from the west)
  const noButtress = (k) => (k <= B || k >= NN - 1 - B) && (d.skipButtress ?? []).some(([f, to]) => xNode(k) >= f && xNode(k) <= to);
  const pinnacle = (cx, cz, tg, o, pw, y) => { blockAt(pm, cx, cz, tg, o, pw / 2, pw / 2, y, y + pw * 1.6); spireAt(pm, cx, cz, tg, o, pw / 2 + .08, y + pw * 1.6, y + pw * 4.8); };
  for (const k of outerNodes) {
    // (a node between a bay with an outer wall and one without -- the tower's, the transept's -- is theirs)
    const bays = [k - 1, k].filter((i) => i >= 0 && i + 1 < NN);
    if (!bays.every((i) => hasOuter(i)) || noButtress(k)) continue;
    const [x, z] = out[k], o = normal(k), tg = [o[1], -o[0]];
    const x0 = tA / 2, x1 = tA / 2 + bd;             // along o from the outer line: the wall's outside to the buttress's face
    // in three stages, each set back, up to the aisle eave; then the pier over the wall to the flyer's head
    // (its profile across the wall: from the wall's face out, up its set-offs, back over the wall to it)
    // (a hall's: its head clear of the great roof's eave -- the pinnacle on it stands out past the overhang, in front of
    //  the roof, and the stages under it set back no further than lets it)
    const pw = Math.min(bw, bd * .5) * (d.hall ? .7 : .8), pc = d.hall ? x0 + d.overhang + .1 + pw / 2 : (x0 + tA / 2 + bd * .5) / 2;
    const u3 = d.hall ? Math.max(tA / 2 + bd * .5, pc + pw / 2 + .05) : tA / 2 + bd * .5;
    const u2 = Math.max(tA / 2 + bd * .72, u3 + .25), u1 = Math.max(x1, u2 + .25);
    const y1 = aisleEave * .45, y2 = aisleEave * .8;
    prismAcross(bm, x, z, o, tg, [[x0, 0], [u1, 0], [u1, y1], [u2, y1], [u2, y2], [u3, y2], [u3, pierTop], [x0, pierTop]], bw / 2);
    // the flyer: from the pier's inner face in, in the node's own plane (its +x toward the wall, along -o) -- across the
    // aisles to the clerestory, or to the intermediate pier and on from it
    const fly = (f, px, pz) => { const q = mesh(); flyerMesh(q, { ...f, width: flyW, per90 }); appendTurned(fm, q, px, pz, [-o[0], -o[1]]); };
    if (d.flyers && !d.hall) fly(fOut, x + o[0] * x0, z + o[1] * x0);
    // the pinnacle over the pier: a shaft, a spire, a finial -- the weight that turns the thrust down into the pier
    if (d.pinnacles) pinnacle(x + o[0] * pc, z + o[1] * pc, tg, o, pw, pierTop);
    if (fUp && !d.hall) {
      // the INTERMEDIATE PIER: on the free-standing pier between the aisles, from the vaults' extrados over their roof
      const [mx, mz] = mids[nA - 2][k];
      prismAcross(bm, mx, mz, o, tg, [[-md, aisleTop], [md, aisleTop], [md, midTop], [-md, midTop]], bw / 2);
      if (d.flyers) fly(fUp, mx - o[0] * md, mz - o[1] * md);
      if (d.pinnacles) pinnacle(mx, mz, tg, o, Math.min(bw, 2 * md) * .8, midTop);
    }
  }
  // (all the open air's: over the aisle roof, inside the box of the aisles' interior)
  add("buttresses", bm, "buttress", { side: "out" }); add("flyers", fm, "flyer", { side: "out" }); add("pinnacles", pm, "pinnacle", { side: "out" });

  // ---- ROOFS. The high roof: its eave round the arcade line's outside, a gable down the nave ending in a hip of as many
  // faces as the apse has sides; the ridge from the west end to over the apse's centre
  // (a hall's roof covers all three vessels: its eave round the outer wall)
  const ov = d.overhang, eaveL = d.hall ? offsetLine(out, -(tA / 2 + ov)) : offsetLine(arc, -(t / 2 + ov));
  const roof = mesh();
  {
    const zW = Lz / 2, apex = [0, ridgeY, zE], west = [0, ridgeY, zW];
    const E = eaveL.map(([x, z]) => [x, wallTop, z]);
    // (wound away from the axis just over the eaves, kept a metre short of the west gable)
    const ref = (p) => [0, wallTop + .1, Math.max(zE, Math.min(zW - 1, p[2]))];
    const tri = (p, q, r) => faceAway(roof, [p, q, r], ref(avg([p, q, r])));
    for (let i = 0; i < B; i++) tri(E[i], west, E[i + 1]);
    tri(E[B], west, apex);
    for (let k = B; k < NN - 1 - B; k++) tri(E[k], apex, E[k + 1]);
    tri(E[NN - 1 - B], apex, west);
    for (let i = NN - 1 - B; i < NN - 1; i++) tri(E[i], west, E[i + 1]);
    tri(E[NN - 1], west, E[0]);                      // the west gable
    for (const [p, q, r] of earClip(eaveL, eaveL.map((_, i) => i))) tri(E[p], E[q], E[r]);   // the soffit, at the eave
  }
  add("high roof", roof, "roof");
  // the lean-to over the aisles and the ambulatory: from the outer wall's eave up to the clerestory wall
  const lean = mesh(), lin = offsetLine(arc, -t / 2), lout = offsetLine(out, -(tA / 2 + ov));
  for (const r of d.hall ? [] : runs) {
    const I = lin.slice(r.from, r.to + 1), O = lout.slice(r.from, r.to + 1);
    leanTo(lean, I, O, aisleRidge, aisleEave, roofT);
  }
  add("aisle roof", lean, "roof");
  if (glass.counts.tris) parts.push({ name: "glass", geometry: glass, kind: "glass", shell: true });
  if (glass.tracery?.counts.tris) parts.push({ name: "tracery", geometry: glass.tracery, kind: "tracery", shell: true });
  if (glass.wimperg?.counts.tris) parts.push({ name: "wimpergs", geometry: glass.wimperg, kind: "wimperg", shell: true });
  if (glass.surround?.counts.tris) parts.push({ name: "surrounds", geometry: glass.surround, kind: "moulding", shell: true });
  // ITS INTERIORS (finish.js): the body on the outer wall's middle line, up to the aisle roof's eave (a box cannot follow
  // the lean-to's slope: over the eave it is the open air's -- a tower's flank over the roof -- and what is under the
  // roof there is not seen); a hall's, to its one roof's ridge. The nave on the arcade's line, the transept across the
  // crossing to the middle of its end walls -- both up into the high roof
  const interiors = [{ name: "interior", pts: out, y1: d.hall ? ridgeY : aisleEave }, { name: "nave interior", pts: arc, y1: ridgeY }];
  if (X !== null) {
    const zA = zs[X[0]], zB = zs[X[1] + 1], xE = outerR + tA / 2 + (d.arm ?? 0) - (d.transeptT ?? t * 1.4) / 2;
    interiors.push({ name: "transept interior", pts: [[-xE, zA], [xE, zA], [xE, zB], [-xE, zB]], y1: ridgeY });
  }
  return { parts, interiors, plan: { arc, out, mids, inner, wallTop, ridgeY, crown, vSpring, clerSill, aisleRidge, aisleEave, arcadeCrown, aisleCrown, spring } };
}

// where two segments' lines cross (a bay's diagonals: its keystone)
function cross(A, C, Bp, D) {
  const r = [C[0] - A[0], C[1] - A[1]], s = [D[0] - Bp[0], D[1] - Bp[1]], den = r[0] * s[1] - r[1] * s[0];
  if (Math.abs(den) < 1e-12) return lerp2(A, C, .5);
  const u = ((Bp[0] - A[0]) * s[1] - (Bp[1] - A[1]) * s[0]) / den;
  return [A[0] + r[0] * u, A[1] + r[1] * u];
}
// a mesh's triangles copied into another at (x, z): its own frame's origin there
function appendAt(m, q, x, z) {
  const P = q.arrays();
  const ids = []; for (let i = 0; i < P.position.length; i += 3) ids.push(m.vert(P.position[i] + x, P.position[i + 1], P.position[i + 2] + z));
  for (let i = 0; i < P.index.length; i += 3) m.tri(ids[P.index[i]], ids[P.index[i + 1]], ids[P.index[i + 2]]);
}
// ...turned so its +x runs along `dir`
function appendTurned(m, q, x, z, dir) {
  const P = q.arrays(), [cx, cz] = dir, nx = -cz, nz = cx;
  const ids = []; for (let i = 0; i < P.position.length; i += 3) { const u = P.position[i], v = P.position[i + 2]; ids.push(m.vert(x + cx * u + nx * v, P.position[i + 1], z + cz * u + nz * v)); }
  const flip = (cx * nz - cz * nx) < 0;
  for (let i = 0; i < P.index.length; i += 3) flip ? m.tri(ids[P.index[i]], ids[P.index[i + 2]], ids[P.index[i + 1]]) : m.tri(ids[P.index[i]], ids[P.index[i + 1]], ids[P.index[i + 2]]);
}
// a four-sided spire over a square of half side h at (x, z), from y0 to its point at y1
function spireAt(m, x, z, e, nrm, h, y0, y1) {
  const c = [[-h, -h], [h, -h], [h, h], [-h, h]].map(([u, v]) => [x + e[0] * u + nrm[0] * v, y0, z + e[1] * u + nrm[1] * v]);
  const tip = [x, y1, z], ref = [x, y0 + (y1 - y0) / 4, z];
  for (let k = 0; k < 4; k++) faceAway(m, [c[k], c[(k + 1) % 4], tip], ref);
  faceAway(m, c, ref);
}
// A LEAN-TO along a line: its high edge `I` (against a wall) at yI, its low edge `O` (the eave) at yO, `th` thick
// (measured down): the top, the underside, the eave's edge and the band against the wall, the two ends -- closed
function leanTo(m, I, O, yI, yO, th) {
  const n = I.length, P = (q, y) => [q[0], y, q[1]];
  const tI = I.map((q) => P(q, yI)), tO = O.map((q) => P(q, yO)), bI = I.map((q) => P(q, yI - th)), bO = O.map((q) => P(q, yO - th));
  // each segment a slab, every face wound away from its middle
  const mid = (i) => avg([tI[i], tI[i + 1], tO[i], tO[i + 1], bI[i], bI[i + 1], bO[i], bO[i + 1]]);
  for (let i = 0; i + 1 < n; i++) {
    const c = mid(i);
    faceAway(m, [tI[i], tI[i + 1], tO[i + 1], tO[i]], c);       // the top
    faceAway(m, [bO[i], bO[i + 1], bI[i + 1], bI[i]], c);       // the underside
    faceAway(m, [tO[i], tO[i + 1], bO[i + 1], bO[i]], c);       // the eave's edge
    faceAway(m, [bI[i], bI[i + 1], tI[i + 1], tI[i]], c);       // against the wall
  }
  faceAway(m, [tI[0], tO[0], bO[0], bI[0]], mid(0));
  faceAway(m, [tO[n - 1], tI[n - 1], bI[n - 1], bO[n - 1]], mid(n - 2));
}
