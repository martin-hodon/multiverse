// The shape of the land: one definition, because more than one thread needs it.
//
// The terrain's geometry is built from `groundH` a few hundred thousand times, which is seconds of arithmetic
// at load -- work a worker should do while the main thread gets on with the world (terrain_worker.js). A
// worker cannot see index.html's closures, so the height function and the water shapes it carves live here and
// both sides import them. Nothing in here touches three or the DOM.
//
// Everything is derived from two numbers (the herd's extent and the ground's radius) plus the two lists the
// world fills in as it lays itself out: the flat zones (a building's plot, the herd's meadow) and the moats.
// Both are passed in BY REFERENCE and read at call time, so the world may keep adding to them after this is
// built -- which it does.
export const WLEVEL = -2.2;            // the one water level for the whole world

// map: a GROWN map (mapgen.js) -- the land, its channels and its water as grids, the big river as functions of x; the
// world is built on it instead of the sines, the lake and the one level (none of which it has)
// roads: the ROADS' SURFACES (paths.js planRoads), by reference like the zones: [{ w, pts: [[x, z, y], ...] }] -- each a
// centreline sampled every ~1.5 m with its surface height. Inside a road the ground IS the road (level across, its
// height along it); over a shoulder of `ROAD_SHOULDER` metres beyond its edge it eases back to the natural ground. The
// terrain mesh is then cut along the roads' edges (terrain_data.js), the road mesh sharing those points (paths.js).
export const ROAD_SHOULDER = 3;
// HOW FAR A POINT IS FROM A MOAT'S ISLAND (a ring) OR INSIDE ITS WATER (a pool): the rectangle hw x hd about its middle, + outside it,
// - inside. A pool may have a SHORE as well -- `shore`, a closed polygon [[x, z], ...] about the same middle, inside the rectangle,
// which stays its bound (Kunming Lake): then it is the signed distance to that. Everything that asks whether it is wet asks here.
// `islands` [[[x, z], ...], ...] as well (with a shore): closed polygons about the same middle that are land, the water all
// round them (the Phoenix Hall's island) -- the pool is the shore's inside less theirs.
export function moatSD(m, x, z) {
  const dr = Math.max(Math.abs(x - m.cx) - m.hw, Math.abs(z - m.cz) - m.hd);
  if (!m.shore || dr > 0) return dr;
  let d = polySD(m.shore, x - m.cx, z - m.cz);
  for (const I of m.islands ?? []) d = Math.max(d, -polySD(I, x - m.cx, z - m.cz));
  return d;
}
// (the signed distance to a closed polygon: - inside)
function polySD(P, qx, qz) {
  let d = 1e18, inside = false;
  for (let i = 0, j = P.length - 1; i < P.length; j = i++) {
    const [ax, az] = P[i], [bx, bz] = P[j], ex = bx - ax, ez = bz - az, wx = qx - ax, wz = qz - az;
    const t = Math.min(1, Math.max(0, (wx * ex + wz * ez) / (ex * ex + ez * ez))), hx = wx - ex * t, hz = wz - ez * t;
    d = Math.min(d, hx * hx + hz * hz);
    if ((az > qz) !== (bz > qz) && qx < ax + ex * (qz - az) / ez) inside = !inside;
  }
  return (inside ? -1 : 1) * Math.sqrt(d);
}
export function makeGround({ extent, groundR, flatZones, moats, map = null, roads = [] }) {
  // the lake: a big C -- a water tube of half-width `w` wrapped around a circular arc of radius `rc`, its
  // opening (`gap` radians) facing north toward the meadow, so the path walks into the lagoon's grassy heart
  const LAKE = { x: 18, z: extent + 120, rc: 70, w: 40, gap: 1.7 };
  LAKE.g0 = -Math.PI / 2 + LAKE.gap / 2;
  LAKE.g1 = -Math.PI / 2 - LAKE.gap / 2 + Math.PI * 2;
  LAKE.e0 = [LAKE.x + Math.cos(LAKE.g0) * LAKE.rc, LAKE.z + Math.sin(LAKE.g0) * LAKE.rc];
  LAKE.e1 = [LAKE.x + Math.cos(LAKE.g1) * LAKE.rc, LAKE.z + Math.sin(LAKE.g1) * LAKE.rc];
  const hasLake = !map && groundR >= LAKE.z + LAKE.rc + LAKE.w + 2;
  const hasRiver = !!map || hasLake;
  // the river: a meandering groove from the west edge into the lake's west arm, 16m bank to bank, carved 4.4m
  // below the plain so the shared water level leaves ~2m of water; it flows east (+x). (A grown map's runs right
  // across, and its channel is in the map.)
  const RIVER = { z: LAKE.z, amp: 12, k: .03, ph: 1.0, hw: 8, bank: 3.5, depth: 4.4,
                  xEnd: map ? groundR + 40 : LAKE.x - LAKE.rc - LAKE.w + 12, flow: 1.6 };   // (a grown map's: past the world's edge)
  const BASIN = map ? map.river.basin : { x: -185, len: 40, add: 10 };   // where the river widens to ~36m around the landing

  // ---- the grown map's grids, sampled: bilinear (the land), nearest (the water: dry is NaN), and the river's functions
  const M = map;
  const gridLin = (A, x, z) => {
    const fi = Math.min(M.n - 1.001, Math.max(0, (x - M.x0) / M.res)), fj = Math.min(M.n - 1.001, Math.max(0, (z - M.z0) / M.res));
    const i = Math.floor(fi), j = Math.floor(fj), a = fi - i, b = fj - j, k = j * M.n + i;
    return (A[k] * (1 - a) + A[k + 1] * a) * (1 - b) + (A[k + M.n] * (1 - a) + A[k + M.n + 1] * a) * b;
  };
  const gridNear = (A, x, z) => {
    const i = Math.round((x - M.x0) / M.res), j = Math.round((z - M.z0) / M.res);
    return i < 0 || j < 0 || i >= M.n || j >= M.n ? NaN : A[j * M.n + i];
  };
  const along = (arr, x) => { const f = Math.min(M.river.n - 1.001, Math.max(0, x - M.river.x0)), k = Math.floor(f); return arr[k] + (arr[k + 1] - arr[k]) * (f - k); };

  const lakeSD = (x, z) => {   // signed distance to the shoreline: negative = in the water zone
    const dx = x - LAKE.x, dz = z - LAKE.z;
    let t2 = Math.atan2(dz, dx);
    while (t2 < LAKE.g0) t2 += Math.PI * 2;
    const dArc = t2 <= LAKE.g1
      ? Math.abs(Math.hypot(dx, dz) - LAKE.rc)
      : Math.min(Math.hypot(x - LAKE.e0[0], z - LAKE.e0[1]), Math.hypot(x - LAKE.e1[0], z - LAKE.e1[1]));
    return dArc - LAKE.w;
  };
  const riverZ = map ? (x) => along(M.river.z, x) : (x) => RIVER.z + RIVER.amp * Math.sin(x * RIVER.k + RIVER.ph);
  const riverHW = map ? (x) => along(M.river.hw, x) : (x) => RIVER.hw + BASIN.add * Math.exp(-(((x - BASIN.x) / BASIN.len) ** 2));
  // the river's surface at x: the one level, or the grown river's own, falling downstream
  const riverLevel = map ? (x) => along(M.river.level, x) : () => WLEVEL;
  const riverSD = (x, z) => !hasRiver || x > RIVER.xEnd ? 1e9 : Math.abs(z - riverZ(x)) - riverHW(x);
  // THE measure of "is it water": signed distance to the nearest shore or bank line, + on land -- the paths
  // keep off the water by it, the enclosure walls stand on land by it (a grown map's: every stream and lake too)
  const waterSD = map ? (x, z) => gridLin(M.sd, x, z) : (x, z) => Math.min(hasLake ? lakeSD(x, z) : 1e9, riverSD(x, z));
  // THE WATER'S SURFACE at a point: the one level everywhere (the old world's sheet hides under the land where there is
  // none), or a grown map's -- a stream's, the river's, a lake's, a moat's -- and -Infinity where it is dry
  const moatAt = (x, z) => moats.some((m) => { const dr = moatSD(m, x, z); return m.pool ? dr < 0 : dr > 0 && dr < m.w; });
  // (a moat's own `y`, set where it is laid out from its `surface`: a garden's pond, level with its own ground wherever the site stands)
  const moatLevel = (x, z) => { const m = moats.find((m) => { const dr = moatSD(m, x, z); return m.pool ? dr < 0 : dr > 0 && dr < m.w; }); return m.y ?? WLEVEL; };
  const waterY = map ? (x, z) => { const w = gridNear(M.water, x, z); return w === w ? w : moatAt(x, z) ? moatLevel(x, z) : -Infinity; } : () => WLEVEL;

  // the ROAD INDEX: every centreline segment in 8 m cells (built when the roads are first asked for, rebuilt if the
  // list grows); roadAt(x, z) -> the nearest road's { y, d } there: d the distance beyond its edge (< 0 inside)
  const RC = 8, roadIdx = { n: -1, cells: new Map() };
  const indexRoads = () => {
    roadIdx.n = roads.length; roadIdx.cells.clear();
    const reach = ROAD_SHOULDER + .5;
    roads.forEach((r, ri) => { for (let i = 0; i + 1 < r.pts.length; i++) {
      const a = r.pts[i], b = r.pts[i + 1], m = r.w / 2 + reach;
      for (let cx = Math.floor((Math.min(a[0], b[0]) - m) / RC); cx <= Math.floor((Math.max(a[0], b[0]) + m) / RC); cx++)
        for (let cz = Math.floor((Math.min(a[1], b[1]) - m) / RC); cz <= Math.floor((Math.max(a[1], b[1]) + m) / RC); cz++) {
          const k = cx * 100003 + cz; let l = roadIdx.cells.get(k); if (!l) roadIdx.cells.set(k, l = []); l.push(ri, i);
        }
    } });
  };
  const roadAt = (x, z) => {
    if (!roads.length) return null;
    if (roadIdx.n !== roads.length) indexRoads();
    const l = roadIdx.cells.get(Math.floor(x / RC) * 100003 + Math.floor(z / RC));
    if (!l) return null;
    let best = null;
    for (let k = 0; k < l.length; k += 2) {
      const r = roads[l[k]], a = r.pts[l[k + 1]], b = r.pts[l[k + 1] + 1];
      const dx = b[0] - a[0], dz = b[1] - a[1], L2 = dx * dx + dz * dz || 1e-9;
      const t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (z - a[1]) * dz) / L2));
      const d = Math.hypot(x - a[0] - dx * t, z - a[1] - dz * t) - r.w / 2;
      if (!best || d < best.d) best = { d, y: a[2] + (b[2] - a[2]) * t };
    }
    return best;
  };
  // (the plots by where they are: one reaches 20 m past its rectangle and no further, and the ground is asked its height
  // a great many times a frame; flatZones grows while the town is laid out, so the index follows its length)
  const ZC = 64, zoneIdx = { n: -1, cells: new Map() }, NO_ZONES = [];
  const indexZones = () => {
    zoneIdx.n = flatZones.length; zoneIdx.cells.clear();
    for (const zn of flatZones)
      for (let cx = Math.floor((zn.x - zn.hx - 20) / ZC); cx <= Math.floor((zn.x + zn.hx + 20) / ZC); cx++)
        for (let cz = Math.floor((zn.z - zn.hz - 20) / ZC); cz <= Math.floor((zn.z + zn.hz + 20) / ZC); cz++) {
          const k = cx * 100003 + cz; let l = zoneIdx.cells.get(k); if (!l) zoneIdx.cells.set(k, l = []); l.push(zn);
        }
  };
  const inPad = (q, x, z) => { const ux = x - q.x, uz = z - q.z; return Math.abs(ux * q.c - uz * q.s) <= q.hw && Math.abs(ux * q.s + uz * q.c) <= q.hd; };
  const levelH = (x, z) => {
    const base = map ? gridLin(M.base, x, z)
               : Math.sin(x * .021 + 1.7) * Math.cos(z * .017 - .8) * 2.1
               + Math.sin(x * .043 - 2.1) * Math.sin(z * .038 + 1.3) * 1.0
               + Math.sin(x * .009 + z * .011) * 1.7;
    // (a zone with its own `y` is settled to that height, not to 0 -- a mine's shaft head on a hillside -- and `fade`
    //  brings the land back over fewer metres than 20: the hill keeps its shape round it)
    let k = 1, kc = 1, ty = 0, onQuay = false;
    if (zoneIdx.n !== flatZones.length) indexZones();
    for (const zn of zoneIdx.cells.get(Math.floor(x / ZC) * 100003 + Math.floor(z / ZC)) ?? NO_ZONES) {
      if (zn.raise || zn.dig) continue;   // (a bank, a berth dredged: below, naturalH)
      const dx = Math.max(0, Math.abs(x - zn.x) - zn.hx), dz = Math.max(0, Math.abs(z - zn.z) - zn.hz);
      const t = Math.min(1, Math.hypot(dx, dz) / (zn.fade ?? 20)), kz = t * t * (3 - 2 * t);
      if (kz < k) { k = kz; ty = zn.y ?? 0; }
      if (zn.pad && !onQuay) onQuay = inPad(zn.pad, x, z);   // (inside the quay's pad as it is turned -- its square, grown to hold it, reaches past its front)
      if (zn.level) {   // a building's plot: level right out to 1m past the footprint, the bank carve fading back in over 2.5m
        const ex = Math.max(0, Math.abs(x - zn.x) - (zn.hx - 2)), ez = Math.max(0, Math.abs(z - zn.z) - (zn.hz - 2));
        const u = Math.min(1, Math.hypot(ex, ez) / 2.5);
        kc = Math.min(kc, u * u * (3 - 2 * u));
      }
    }
    if (map) {
      // a grown map: its finished ground (the channels carved in; the built places settled to 0 when it was grown) is
      // levelled toward 0 under the plots -- but never under water: a plot by the river stops at its edge. (Levelling the
      // land and cutting the channel from it after, as the old plain does, cut it from the wrong height here: the plain
      // is 0 everywhere, a grown map's land is not; and where the land was settled below the river's bed there was no
      // cut to tell a channel by, only the water.) Under a QUAY's own pad (harbour.js zones' `pad`: the quay wall at its
      // seaward edge) it is levelled all the same: the wet mask, a grid, bled a metre or two in behind the wall, and the
      // land there stood through the paving under the coping (2026-11-03)
      return ty + (base - gridLin(M.carve, x, z) - ty) * Math.max(k, onQuay ? 0 : gridLin(M.wet, x, z)) - moatCut(x, z);
    }
    let y = ty + (base - ty) * k;
    // ONE shared water level for the whole world: the plain is kept softly above it (a smooth floor at -1.4m,
    // .8m clear of the water), so only what is deliberately carved -- lake, river, moats -- fills with water
    y = -1.4 + Math.log1p(Math.exp(4 * (y + 1.4))) / 4;
    let carve = 0;
    if (hasLake) {
      const sd = lakeSD(x, z);
      if (sd < 0) { const s = Math.min(1, -sd / LAKE.w); carve = 8.8 * s * s * (3 - 2 * s); }   // 8.8m down: 6.6m of water at the deepest
    }
    if (hasRiver) {
      const sd = riverSD(x, z);
      if (sd < 0) {
        const s = Math.min(1, -sd / RIVER.bank), e = Math.min(1, (RIVER.xEnd - x) / 25);   // banks; fades into the lake bowl
        carve = Math.max(carve, RIVER.depth * s * s * (3 - 2 * s) * e * e * (3 - 2 * e));
      }
    }
    y -= carve * kc;
    return y - moatCut(x, z);
  };
  // A BANK (a zone with `raise`, 2026-11-03: a mine adit's portal): earth heaped up to at least its `y` over the
  // rectangle, falling back to the land over `fade` m round it -- never lowering it -- and none past `cut` [nx, nz, c]
  // (where (x - zn.x) nx + (z - zn.z) nz > c: the face of the wall that holds it, sheer). A BERTH DREDGED (a zone with
  // `dig`, 2026-11-03: harbour.js, one before each quay): the bed taken down to at most its `y` over the strip `D` m out
  // from the quay's face along its `hw` either side, coming back up to the bed as it was over `fade` m -- never behind
  // the face (its local z < 0: the quay's own pad) nor under any quay's pad (two quays meeting at an angle: the one's
  // strip runs over the other's paving), so the wall drops sheer into water, not onto a shelf of the shore
  const naturalH = (x, z) => {
    let y = levelH(x, z);
    const here = zoneIdx.cells.get(Math.floor(x / ZC) * 100003 + Math.floor(z / ZC)) ?? NO_ZONES;
    let paved = null;
    for (const zn of here) {
      if (zn.dig) {
        if ((paved ??= here.some((p) => p.pad && inPad(p.pad, x, z)))) continue;
        const q = zn.dig, ux = x - q.x, uz = z - q.z, lz = ux * q.s + uz * q.c;
        if (y <= zn.y || lz < 0) continue;
        const ex = Math.max(0, Math.abs(ux * q.c - uz * q.s) - q.hw), ez = Math.max(0, lz - q.D);
        const t = Math.min(1, Math.hypot(ex, ez) / (zn.fade ?? 6)), kz = t * t * (3 - 2 * t);
        y += (zn.y - y) * (1 - kz);
        continue;
      }
      if (!zn.raise || y >= zn.y || (zn.cut && (x - zn.x) * zn.cut[0] + (z - zn.z) * zn.cut[1] > zn.cut[2])) continue;
      const dx = Math.max(0, Math.abs(x - zn.x) - zn.hx), dz = Math.max(0, Math.abs(z - zn.z) - zn.hz);
      const t = Math.min(1, Math.hypot(dx, dz) / (zn.fade ?? 20)), kz = t * t * (3 - 2 * t);
      y += (zn.y - y) * (1 - kz);
    }
    return y;
  };
  // THE GROUND: the natural ground, and the roads in it -- level across, easing back to the land over the shoulder
  const groundH = (x, z) => {
    const g = naturalH(x, z), r = roadAt(x, z);
    if (!r || r.d >= ROAD_SHOULDER) return g;
    if (r.d <= 0) return r.y;
    const t = r.d / ROAD_SHOULDER, s2 = t * t * (3 - 2 * t);
    return r.y + (g - r.y) * s2;
  };
  // the castle moats: rectangular rings carved round their islands
  const moatCut = (x, z) => {
    let c = 0;
    for (const m of moats) {
      const dr = moatSD(m, x, z);
      if (m.pool) { if (dr < 0) c += m.depth * Math.min(1, -dr / 2.5); }   // (`pool`: no island -- a stretch of water hw x hd itself, its banks sloping in: a river under a bridge)
      else if (dr > 0 && dr < m.w) c += m.depth * Math.min(1, dr / 2.5, (m.w - dr) / 2.5);
    }
    return c;
  };

  return { WLEVEL, LAKE, RIVER, BASIN, hasLake, hasRiver, lakeSD, riverZ, riverHW, riverLevel, riverSD, waterSD, waterY, groundH, naturalH, roadAt, roads, map,
           // what a worker needs to rebuild exactly this, with no closures: the lists, the two numbers, the map
           config: () => ({ extent, groundR, flatZones, moats, map, roads }) };
}
