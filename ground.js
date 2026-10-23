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
  const moatAt = (x, z) => moats.some((m) => { const dr = Math.max(Math.abs(x - m.cx) - m.hw, Math.abs(z - m.cz) - m.hd); return dr > 0 && dr < m.w; });
  const waterY = map ? (x, z) => { const w = gridNear(M.water, x, z); return w === w ? w : moatAt(x, z) ? WLEVEL : -Infinity; } : () => WLEVEL;

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
  const naturalH = (x, z) => {
    const base = map ? gridLin(M.base, x, z)
               : Math.sin(x * .021 + 1.7) * Math.cos(z * .017 - .8) * 2.1
               + Math.sin(x * .043 - 2.1) * Math.sin(z * .038 + 1.3) * 1.0
               + Math.sin(x * .009 + z * .011) * 1.7;
    let k = 1, kc = 1;
    for (const zn of flatZones) {
      const dx = Math.max(0, Math.abs(x - zn.x) - zn.hx), dz = Math.max(0, Math.abs(z - zn.z) - zn.hz);
      const t = Math.min(1, Math.hypot(dx, dz) / 20);
      k = Math.min(k, t * t * (3 - 2 * t));
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
      // cut to tell a channel by, only the water.)
      return (base - gridLin(M.carve, x, z)) * Math.max(k, gridLin(M.wet, x, z)) - moatCut(x, z);
    }
    let y = base * k;
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
      const dr = Math.max(Math.abs(x - m.cx) - m.hw, Math.abs(z - m.cz) - m.hd);
      if (dr > 0 && dr < m.w) c += m.depth * Math.min(1, dr / 2.5, (m.w - dr) / 2.5);
    }
    return c;
  };

  return { WLEVEL, LAKE, RIVER, BASIN, hasLake, hasRiver, lakeSD, riverZ, riverHW, riverLevel, riverSD, waterSD, waterY, groundH, naturalH, roadAt, roads, map,
           // what a worker needs to rebuild exactly this, with no closures: the lists, the two numbers, the map
           config: () => ({ extent, groundR, flatZones, moats, map, roads }) };
}
