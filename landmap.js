// THE WORLD'S LAND FROM A LANDSCAPE (2026-10-29; docs/landscape.md "In the world").
//
// The other way to grow the world's land (mapgen.js grows river country on the GPU): a landscape scene (landscape.js)
// made of the rock and the climate asked for -- the scarp, the fall, the gorge, the lake on the upland, whatever that
// rock in that climate makes -- and scaled up to the world's size, so what it holds is the world's: a 15 m fall a
// 30 m one, a gorge 20 m across a gorge 50 m across. The scene's stream is the world's big river.
//   GROW     the scene, its stream running east (+x), off its middle so the world finds room enough either side of it
//            (the world reaches R + riverZ north of the river, R - riverZ south)
//   SCALE    across by what fits the world into it (~2.7), up by less (the cliffs a little less sheer than the
//            scene's, the land under the town less steep): its grids as a grown land -- the ground, the water's surface
//            (the lakes and the streams the scene holds; dry ground its own), the discharge, the river's inlet and outlet
//   SHAPE    mapgen.js's: the window along the river where its banks are gentlest and the world's open places
//            (the herd's meadow, the facade line) lie nearest the town's height; the scene's 1 m cells bicubic onto
//            the world's 2 m grid with a little detail between them; the sites, the settling, the channels, the water
// Everything comes back as mapgen's map does (ground.js and index.html read it the same), with `kind: "landscape"`,
// the scene's `geology`, `climate`, `scale` and `relief` added.
import { makeLandscape } from "./landscape.js";
import { shapeMap } from "./mapgen.js";
import { surfaceColours, bareOf } from "./landscape/colour.js";

const QS = 3.156e7;   // m3/yr in a m3/s

// (where the scarp crosses the scene: the world's middle -- the herd's meadow, the facade line, the town -- wants one
// tier of the land, not the step between two. UPLAND: the scarp far downstream, the town on the upland by the lake
// with the fall and the gorge east of it; LOWLAND: the scarp far upstream, its gorge short, the town on the lowland
// below it. A seed tries its own first, and the other if its land would have to move more than a few metres)
const VARIANTS = {
  upland: (size) => ({ scarpAt: size * .3 }),
  lowland: (size) => ({ scarpAt: -size * .22, features: { ravine: { length: .12 } } }),
};
// (the world's river runs east all the way across: its loops not so deep that it turns back on itself; its lake, scaled
// up with the rest, a lake the world's size, not a sea)
const WORLD_FEATURES = { coast: false, meanders: { amp: .55 }, lake: { r: .085, islands: 1 } };

export function landscapeMap({ seed = 1, radius = 300, riverZ = 150, res = 2, meadow, facade, geology = "canyon", climate = "temperate",
                               scale = null, relief = null, variant = null, keep = null } = {}) {
  const order = variant ? [variant] : seed % 2 ? ["upland", "lowland"] : ["lowland", "upland"];
  let best = null;
  let err = null;
  for (const v of order) {
    let M;
    try { M = attempt({ seed, radius, riverZ, res, meadow, facade, geology, climate, scale, relief, variant: v, keep }); } catch (e) { err = e; continue; }
    if (!best || M.earthwork < best.earthwork) best = M;
    if (best.earthwork <= 4) break;
  }
  if (!best) throw err;
  return best;
}

function attempt({ seed, radius, riverZ, res, meadow, facade, geology, climate, scale, relief, variant, keep = null }) {
  const SIZE = 320, half = SIZE / 2, R = radius + 24;
  // ---- GROW: the room the world wants each side of the river, and the stream put where the scene shares out its own
  // in the same proportion
  const north = R + riverZ + 40, south = R - riverZ + 40;
  const V = VARIANTS[variant](SIZE);
  const L = makeLandscape({ seed, geology, climate, flow: 0, streamV: half * .8 * (north - south) / (north + south), wander: .5, scarpAt: V.scarpAt,
                            features: { ...WORLD_FEATURES, ...V.features } });
  const { N, dx, H, water, kind, Q, plan } = L;

  // ---- SCALE: across, so the stream's room either side (its wanders included) holds the world's
  const inside = plan.stream.map(([u, v]) => plan.toXY(u, v)).filter(([x, y]) => x > 2 && y > 2 && x < SIZE - 2 && y < SIZE - 2);
  const ys = inside.map(([, y]) => y), roomN = Math.min(...ys) - 6, roomS = SIZE - Math.max(...ys) - 6;
  const hs = scale ?? Math.max(2, north / roomN, south / roomS) * 1.08;   // (a little over: the window may turn with the river)
  const vs = relief ?? hs ** .6;
  const Hs = new Float32Array(N * N), Ws = new Float32Array(N * N), Qs = new Float32Array(N * N);
  const [ex, ey] = inside[0], [ox, oy] = inside[inside.length - 1];
  const ek = Math.round(ey / dx) * N + Math.round(ex / dx);
  // (the river's discharge: what keeps a mill and a barge going -- less in a dry country's, a river from wetter hills)
  const Qin = (L.climate.flows ? 12 : 5) * QS, qk = Qin / Math.max(1, Q[ek]);
  for (let k = 0; k < N * N; k++) {
    Hs[k] = H[k] * vs;
    Ws[k] = kind[k] === 1 && water[k] > H[k] ? water[k] * vs : Hs[k];   // (the lakes' surfaces; a stream's, mapgen draws its own channel for)
    if (kind[k] === 1) Ws[k] -= (k % N) * 1e-5;   // (a lake's surface tilted east by a hair: the river's course across it goes straight on)
    Qs[k] = kind[k] === 2 || kind[k] === 3 ? Q[k] * qk : Math.min(Q[k] * qk, 4e5);   // (side streams only where the scene runs them)
  }
  // (the big river's cells: the scene's own stream, every cell it crosses, west to east)
  const main = [];
  for (let q = 0; q + 1 < inside.length; q++) {
    const [ax, ay] = inside[q], [bx, by] = inside[q + 1], m = Math.ceil(Math.hypot(bx - ax, by - ay) / (dx * .5));
    for (let t = 0; t < m; t++) { const c = Math.round((ay + (by - ay) * t / m) / dx) * N + Math.round((ax + (bx - ax) * t / m) / dx); if (c !== main[main.length - 1]) main.push(c); }
  }
  const grown = { H: Hs, W: Ws, Q: Qs, N, dx: dx * hs, inlet: [ex * hs, ey * hs, Qin], outlets: [[ox * hs, oy * hs, 14 * hs]],
                  falls: plan.fallH > 0 ? [{ height: plan.fallH * vs }] : [] };

  // ---- SHAPE: mapgen's, its windows and its bridge also judged by the EARTHWORK -- how far the places built on lie
  // from the town's height (2.2 m over the river at the bridge): the town south of the bridge, its farms north of it,
  // the herd's meadow, the monument's stretch of the facade line -- each is settled to it, and the less the land has
  // to move, the less it shows (and the fewer of the town's houses find their ground too far from level to stand).
  // A lake over any of them is no place at all
  const off = (at, wet, townH, x0, x1, z0, z1, st) => {   // how far a rectangle's ground lies off the town's height, m
    let s = 0, w = 0, c = 0;
    for (let x = x0; x <= x1; x += st) for (let z = z0; z <= z1; z += st) { s += at(x, z); w += wet(x, z) ? 1 : 0; c++; }
    return Math.abs(s / c - townH) + 120 * w / c;
  };
  const away = (at, wet, townH) => {   // the meadow's, and the facade line's best stretch for the monument
    let fac = Infinity;
    for (let x = -radius + facade.w / 2 + 30; x <= radius - facade.w / 2 - 30; x += 20)
      fac = Math.min(fac, off(at, wet, townH, x - facade.w / 2, x + facade.w / 2, facade.z - facade.d / 2, facade.z + facade.d / 2 + facade.road, 15));
    return off(at, wet, townH, meadow.x0, meadow.x1, meadow.z0, meadow.z1, 12) + .5 * fac;
  };
  const score = (w, at, river, wet) => {
    if (river.length < 2) return -10;
    let best = Infinity;
    for (let xb = -radius + 95, q = 1; xb <= radius - 135; xb += 15) {
      while (q < river.length - 1 && river[q].x < xb) q++;
      const a = river[q - 1], b = river[q], t = Math.min(1, Math.max(0, (xb - a.x) / Math.max(1e-6, b.x - a.x)));
      const z = a.z + (b.z - a.z) * t, townH = a.level + (b.level - a.level) * t + 2.2;
      best = Math.min(best, off(at, wet, townH, xb - 70, xb + 125, z + 14, z + 122, 15) + .7 * off(at, wet, townH, xb - 65, xb + 105, z - 82, z - 12, 15)
                            + away(at, wet, townH));
    }
    return -best / 4;
  };
  const siteCost = (xb, townH, at, wet, zb) => {
    // (the town's and the farms' own ground: mapgen's roughness and bank terms judge it -- but not a lake over it)
    return away(at, wet, townH) + 120 * wetIn(wet, xb - 70, xb + 125, zb + 14, zb + 122) + 80 * wetIn(wet, xb - 65, xb + 105, zb - 82, zb - 12);
  };
  const M = shapeMap(grown, { seed, radius, riverZ, res, meadow, facade, score, siteCost, detail: .45, round: true, main, keep });   // (keep: sea.js)
  // (where the scene's own features came to lie in the world: the fall, the lake)
  const toGame = (x, y) => { const du = x * hs - M.window.O[0], dv = y * hs - M.window.O[1]; return [du * M.window.e[0] + dv * M.window.e[1], du * M.window.f[0] + dv * M.window.f[1]]; };
  const [fx, fy] = plan.toXY(plan.fallU, plan.streamV(plan.fallU)), [fallX, fallZ] = toGame(fx, fy);
  const lake = L.lake ? (([x, z]) => ({ x, z, r: L.lake.r * hs }))(toGame(...plan.toXY(L.lake.u, L.lake.v))) : null;
  // (what the ground is made of, on the world's grid: where it is bare, its colour -- the rock's beds down a cliff, the
  // scree under it, the sand, the snow -- and how bare, for the ground (terrain_data.js) and the grass (grass.js))
  const col = surfaceColours(L), bare = Float32Array.from(L.surf, (s) => bareOf(L.SURF[s], L.climate));
  const { n, res: r, x0, z0, window: { O, e, f } } = M, sRgb = new Float32Array(n * n * 3), sBare = new Float32Array(n * n);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = x0 + i * r, z = z0 + j * r, fi = (O[0] + x * e[0] + z * f[0]) / (dx * hs), fj = (O[1] + x * e[1] + z * f[1]) / (dx * hs);
    const a = Math.max(0, Math.min(N - 1.001, fi)), b = Math.max(0, Math.min(N - 1.001, fj)), ia = a | 0, jb = b | 0, ta = a - ia, tb = b - jb;
    const k = jb * N + ia, q = j * n + i, w = [(1 - ta) * (1 - tb), ta * (1 - tb), (1 - ta) * tb, ta * tb], ks = [k, k + 1, k + N, k + N + 1];
    for (let m = 0; m < 4; m++) { sBare[q] += w[m] * bare[ks[m]]; for (let c = 0; c < 3; c++) sRgb[q * 3 + c] += w[m] * col[ks[m] * 3 + c]; }
    // (where the land was settled to build on -- the town, its farms, the meadow, the monument's stretch -- it is worked
    // ground: the lawn's, fading back to the scene's own over 30 m)
    const out = Math.min(...M.areas.map((a) => Math.hypot(Math.max(0, a.x0 - x, x - a.x1), Math.max(0, a.z0 - z, z - a.z1))));
    sBare[q] *= Math.min(1, out / 30);
  }
  return { ...M, kind: "landscape", variant, earthwork: Math.max(...M.lift.map(Math.abs)), geology: L.geology.name, climate: L.climate.name,
           scale: hs, relief: vs, notes: L.notes, sceneMs: L.ms, fall: plan.fallH > 0 ? { x: fallX, z: fallZ, height: plan.fallH * vs } : null, lake,
           surface: { n, res: r, x0, z0, rgb: sRgb, bare: sBare } };
}

const wetIn = (wet, x0, x1, z0, z1) => { let w = 0, c = 0; for (let x = x0; x <= x1; x += 15) for (let z = z0; z <= z1; z += 15) { w += wet(x, z) ? 1 : 0; c++; } return w / c; };
