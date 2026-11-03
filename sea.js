// OPEN WATER: THE SEA, THE BIG LAKE (2026-11-03; docs/world.md "Open water").
//
// A world may have, besides its river, a stretch of OPEN WATER far bigger than the river's lake: a SEA COAST the river
// runs out into, or a BIG LAKE the river runs through. `?water=sea|lake|none`; unasked, the seed draws it (its own
// stream: a sixth of the worlds a sea, a sixth a lake, the rest the river alone, as before). Nothing here touches three.
//   PLAN     (openWaterPlan) before the land is shaped: where the water lies -- east of the town, downstream, the river
//            running into it -- so mapgen.js's site search keeps the town, its farms and the monument clear of it
//            (shapeMap `keep`): the town has its river AND its shore
//   SHAPE    (addOpenWater) on the shaped map (mapgen.js shapeMap's, landmap.js's): the water's outline -- a coast with
//            its bays and headlands, a lake's wandering round -- its level the river's where it comes in; the bed under it
//            falling away from the shore, and the land along it shaped as SHORE by what it is made of and how high it
//            stands: a BEACH (sand rising from the waterline to a berm, the bed shelving gently), a ROCKY shore (ledges and
//            boulders, the bed falling steeply), a CLIFF (the land cut off sheer, deep water at its foot); the river's
//            mouth an ESTUARY widening into the sea; the map's grids (ground, water, wet, sd, riverness, surface) made
//            to say so, so the terrain, the water sheet, the grass's mask, waterY and waterSD all follow with no change
//   ASK      (seaAPI) what the others need of it: isOpenWater, depth, the shoreline as a polyline (points with the
//            normal into the water), harbourSite(town) (the best stretch to build a port on), route(a, b) and the
//            sailing lanes over deep water
// Game frame: x east, z SOUTH (the river runs east along z = riverZ(x), the town south of it), y up. Metres.

const TAU = Math.PI * 2;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const smooth = (t) => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };
const mix = (a, b, t) => a + (b - a) * t;
const rng = (s) => { let a = s >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
// (smooth value noise, 1-D and 2-D, -1..1)
const hash = (i, j, s) => { let h = Math.imul(i, 374761393) + Math.imul(j, 668265263) + Math.imul(s, 2246822519); h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 2147483648 - 1; };
const noise2 = (x, z, s) => {
  const i = Math.floor(x), j = Math.floor(z), a = x - i, b = z - j, u = a * a * (3 - 2 * a), v = b * b * (3 - 2 * b);
  return mix(mix(hash(i, j, s), hash(i + 1, j, s), u), mix(hash(i, j + 1, s), hash(i + 1, j + 1, s), u), v);
};
const noise1 = (x, s) => noise2(x, 0.5, s);

export const OPEN_WATER = ["none", "lake", "sea"];
// THE WORLD'S OPEN WATER: what was asked (?water=), else the seed's draw -- its own stream, so the world's other draws
// stay as they were
export function openWaterKind(seed, asked = null) {
  if (OPEN_WATER.includes(asked)) return asked;
  const r = rng((seed >>> 0) * 2654435761 + 0x5ea)();
  return r < 1 / 6 ? "sea" : r < 1 / 3 ? "lake" : "none";
}

// THE PLAN: the water's outline as a function of where the river is, chosen before the land is shaped (null: none).
// radius: the world's (groundR); riverZ: where the river is meant to run (mapgen's riverZ). `bind(riverZf, guard)`
// makes the outline against the river as it was laid out: { s(x, z) (+ in the water, ~metres from the shore), u(x, z)
// (where along the shore), ... }, pushed out (downstream) until every rectangle of `guard` stands MARGIN clear.
// `keep(rect)` is what mapgen's site search asks: is this rectangle clear of the water? (the outline bound to the
// river's course there and then)
export const MARGIN = 60;   // m: how far the town's, the farms', the meadow's and the monument's ground keep from the water
export function openWaterPlan(kind, seed, { radius = 300, riverZ = 150, meadow = null, facade = null } = {}) {
  if (kind !== "sea" && kind !== "lake") return null;
  const r = rng((seed >>> 0) * 7919 + (kind === "sea" ? 101 : 202));
  const R = radius;
  const P = { kind, seed, radius, riverZ };
  if (kind === "sea") {
    // the coast crosses the river xc east of the middle, turned by `tilt` (its seaward normal (cos, sin): east, a little
    // south or north of it), wandering in bays and headlands -- the biggest bay where the town will be, south of the mouth
    P.xc = R * (.3 + .2 * r());
    P.tilt = -.3 + .85 * r();
    P.A = [26 + 10 * r(), 9 + 4 * r(), 3 + 2 * r()];
    P.L = [62 + 20 * r(), 24 + 8 * r(), 8 + 3 * r()];
    P.ph = [0, r() * TAU, r() * TAU];
    P.bayU = 70 + 60 * r();
    P.ph[0] = -Math.PI / 2 - P.bayU / P.L[0];
    P.depth = 22;
  } else {
    // the lake: a wandering round east of the town, most of it north of the river (the world's room is there), the river
    // coming in at its south-west shore and out at its south-east
    P.xc = R * (.08 + .14 * r());
    P.a = R * (.33 + .07 * r());          // its half-length along the river
    P.b = P.a * (1.25 + .35 * r());       // across it
    P.f = .55 + .2 * r();                 // how much of it lies north of the river (its middle f b north of it)
    P.W = [[3, .07 * r() + .03, r() * TAU], [5, .05 * r() + .02, r() * TAU], [9, .025, r() * TAU]];
    P.depth = 13;
  }
  P.geoNoise = Math.floor(r() * 1e6);
  // (the monument: where mapgen's search can put it at all -- the westmost of the places it may take, or the middle if its
  //  footprint overlaps the meadow wherever it stands -- is guarded from the start, so the search still finds one)
  let mon = null;
  if (facade && meadow) {
    let mx = null;
    for (let x = -R + facade.w / 2 + 30; x <= R - facade.w / 2 - 30 && mx === null; x += 5)
      if (!(x + facade.w / 2 > meadow.x0 - 10 && x - facade.w / 2 < meadow.x1 + 10 && facade.z + facade.d / 2 > meadow.z0)) mx = x;
    mx ??= 0;
    mon = { x0: mx - facade.w / 2 - 8, x1: mx + facade.w / 2 + 8, z0: facade.z - facade.d / 2 - 8, z1: facade.z + facade.d / 2 + facade.road };
  }
  const own = [meadow, mon].filter(Boolean);
  P.keep = (() => { let bound = null; const at = (riverZf) => (!bound || bound.rz !== riverZf ? bound = bindPlan(P, riverZf, own) : bound);
    const keep = (rect, riverZf) => clearOf(at(riverZf), rect);
    // (and the nearer the town to the water the better: its port a short walk from its gate)
    keep.cost = (a, riverZf) => { const O = at(riverZf); let gap = Infinity;
      for (let x = a.x0; x <= a.x1 + 1e-6; x += (a.x1 - a.x0) / 8) for (let z = a.z0; z <= a.z1 + 1e-6; z += (a.z1 - a.z0) / 8) gap = Math.min(gap, -O.s(x, z));
      return .02 * Math.max(0, gap - MARGIN); };
    return keep; })();
  P.bind = (riverZf, guard = []) => bindPlan(P, riverZf, [...own, ...guard]);
  return P;
}
// (the town's, the farms' rectangles: is all of it MARGIN clear of the water?)
function clearOf(O, a, m = MARGIN) {
  for (let x = a.x0; x <= a.x1 + 1e-6; x += Math.max(1, (a.x1 - a.x0) / 8)) for (let z = a.z0; z <= a.z1 + 1e-6; z += Math.max(1, (a.z1 - a.z0) / 8))
    if (O.s(x, z) > -m) return false;
  return true;
}
function bindPlan(P, riverZf, guard) {
  const R = P.radius;
  let O = null;
  if (P.kind === "sea") {   // (the coast pushed out downstream until it is clear)
    let shift = 0;
    // (and turned, if the seed's own heading would push it far out: the turn that needs the least pushing)
    let best = null;
    for (const dt of [0, .25, -.25, .5, -.5, .8]) {
      const tilt = clamp(P.tilt + dt, -.6, 1.0);
      let shift = 0;
      for (let it = 0; it < 60; it++) { O = seaShape(P, riverZf, shift, tilt); if (guard.every((a) => clearOf(O, a))) break; shift += 6; }
      O.shift = shift;
      if (!best || shift + 40 * Math.abs(dt) < best.shift + 40 * Math.abs(best.dt)) { best = O; best.dt = dt; }
      if (shift === 0) break;
    }
    O = best;
  } else {                  // (the lake: as big as it can be -- moved east, north or south a little first, made smaller last)
    search: for (let k = 1; k >= .5; k -= .05) for (const dx of [0, 15, 30, 45, 60, 80, 100]) for (const dz of [0, -20, 20, -40]) {
      O = lakeShape(P, riverZf, k, dx, dz);
      if (O.fits && O.crosses && guard.every((a) => clearOf(O, a))) { O.shift = [+k.toFixed(2), dx, dz]; break search; }
    }
  }
  O.rz = riverZf;
  return O;
}
// the coast: the seaward normal N = (cos tilt, sin tilt), along it T = (-sin, cos) (southward when tilt is 0); a point's
// v = (p - P0).N, u = (p - P0).T; the shore at v = c(u): s = v - c(u)
function seaShape(P, riverZf, shift, tilt = P.tilt) {
  const xc = P.xc + shift, P0 = [xc, riverZf(xc)], N = [Math.cos(tilt), Math.sin(tilt)], T = [-N[1], N[0]];
  const c = (u) => P.A.reduce((s, A, k) => s + A * Math.sin(u / P.L[k] + P.ph[k]), 0);
  const dc = (u) => P.A.reduce((s, A, k) => s + A / P.L[k] * Math.cos(u / P.L[k] + P.ph[k]), 0);
  const uv = (x, z) => [(x - P0[0]) * T[0] + (z - P0[1]) * T[1], (x - P0[0]) * N[0] + (z - P0[1]) * N[1]];
  return {
    P0, N, T, c, dc,
    s: (x, z) => { const [u, v] = uv(x, z); return (v - c(u)) / Math.sqrt(1 + .35 * dc(u) ** 2); },
    u: (x, z) => uv(x, z)[0],
    at: (u) => [P0[0] + u * T[0] + c(u) * N[0], P0[1] + u * T[1] + c(u) * N[1]],
    bay: (u) => -c(u) / P.A[0],   // (+1 the deepest of a bay, -1 the tip of a headland)
    span: [-2.2 * P.radius, 2.2 * P.radius],
  };
}
// the lake: about C, its radius at angle th the ellipse's (a along x, b across) wandering by a few harmonics; s = r(th) - |p - C|
function lakeShape(P, riverZf, k, dx, dz) {
  const a = P.a * k, b = P.b * k, xc = P.xc + dx;
  const C = [xc + a, riverZf(xc + a) - b * P.f + dz];
  const wig = (th) => P.W.reduce((s, [m, A, p]) => s + A * Math.sin(m * th + p), 0);
  const rr = (th) => a * b / Math.hypot(b * Math.cos(th), a * Math.sin(th)) * (1 + wig(th));
  const rm = Math.sqrt(a * b);
  const at = (u) => { const th = u / rm, r = rr(th); return [C[0] + r * Math.cos(th), C[1] + r * Math.sin(th)]; };
  let fits = true;   // (all of it inside the world, its far shore 20 m short of the edge)
  for (let q = 0; q < 72; q++) { const [x, z] = at(q / 72 * TAU * rm); if (Math.hypot(x, z) > P.radius - 10) fits = false; }
  const s = (x, z) => { const th = Math.atan2(z - C[1], x - C[0]); return (rr(th) - Math.hypot(x - C[0], z - C[1])) * .92; };
  let run = 0;   // (and the river runs through it: 60 m of its course at least)
  for (let x = C[0] - a; x <= C[0] + a; x += 2) if (s(x, riverZf(x)) > 8) run += 2;
  return {
    C, a, b, rr, rm, at, fits, s, crosses: run >= 60,
    u: (x, z) => { let th = Math.atan2(z - C[1], x - C[0]); if (th < 0) th += TAU; return th * rm; },
    bay: (u) => -wig(u / rm) / .1,
    span: [0, TAU * rm], closed: true,
  };
}

// the rock the shore is cut in, by the land's geology (landmap.js's; a grown map's river country: soft beds, mostly beach)
// bias: toward cliffs (+) or beaches (-); hard: how far high land behind the shore makes it a cliff (soft beds slump
// into banks instead: 0); sand: the beach's colour; rock: the cliff's
const SHORE_ROCK = {
  grown:    { bias: -.05, hard: 0, sand: [.80, .71, .53], rock: [.58, .53, .47], name: "river country: soft beds" },
  "sandstone canyon country": { bias: .25, hard: .8, sand: [.84, .64, .45], rock: [.74, .52, .36], name: "sandstone" },
  "limestone karst": { bias: .45, hard: 1, sand: [.88, .85, .76], rock: [.80, .78, .71], name: "limestone" },
  "basalt flows": { bias: .4, hard: .9, sand: [.25, .24, .23], rock: [.27, .26, .26], name: "basalt" },
  "granite upland": { bias: .35, hard: .9, sand: [.76, .70, .62], rock: [.66, .61, .58], name: "granite" },
};

// SHAPE: the open water laid into a shaped map (mapgen.js shapeMap's, landmap.js's) -- M changed in place; M.sea holds
// what was made (plain data: arrays and numbers). plan: openWaterPlan's.
export function addOpenWater(M, plan) {
  if (!plan) return M;
  const t0 = typeof performance !== "undefined" ? performance.now() : Date.now();
  const { n, res, x0, z0, base, carve } = M, NN = n * n, R = plan.radius;
  const RV = M.river, along = (arr, x) => { const f = clamp(x - RV.x0, 0, RV.n - 1.001), k = Math.floor(f); return arr[k] + (arr[k + 1] - arr[k]) * (f - k); };
  const riverZf = (x) => along(RV.z, x), levelf = (x) => along(RV.level, x), hwf = (x) => along(RV.hw, x);
  const O = plan.bind(riverZf, M.areas ?? []);
  const lake = plan.kind === "lake", rock = SHORE_ROCK[M.kind === "landscape" ? M.geology : "grown"] ?? SHORE_ROCK.grown;
  const ground0 = Float32Array.from(base, (b, k) => b - carve[k]);   // the land before
  const gAt = (x, z) => { const fi = clamp((x - x0) / res, 0, n - 1.001), fj = clamp((z - z0) / res, 0, n - 1.001), i = fi | 0, j = fj | 0, a = fi - i, b = fj - j, k = j * n + i;
    return (ground0[k] * (1 - a) + ground0[k + 1] * a) * (1 - b) + (ground0[k + n] * (1 - a) + ground0[k + n + 1] * a) * b; };

  // ---- the LEVEL: the river's where it comes into the open water (its first step into it, west to east); a lake's
  // river leaves it again where it last crosses out
  let xIn = null, xOut = null;
  for (let x = -R; x <= R + 30; x += .5) { const w = O.s(x, riverZf(x)) > 0; if (w && xIn === null) xIn = x; if (w) xOut = x; }
  if (xIn === null) { xIn = O.P0 ? O.P0[0] : O.C[0]; xOut = xIn; }
  const S = levelf(xIn) - .02;
  // ---- along the shore: what kind of shore, every 4 m of it -- the land's height behind it (relief), the geology's
  // bias, bays to beaches and headlands to rock, the river's mouth soft ground
  const u0 = O.span[0], du = 4, nu = Math.ceil((O.span[1] - O.span[0]) / du) + 1;
  const uIn = O.u(xIn, riverZf(xIn)), uOut = O.u(xOut + .5, riverZf(xOut + .5));
  const relief = new Float32Array(nu), type = new Float32Array(nu);
  const normalAt = (x, z) => { const e = 1.5, gx = O.s(x + e, z) - O.s(x - e, z), gz = O.s(x, z + e) - O.s(x, z - e), l = Math.hypot(gx, gz) || 1; return [gx / l, gz / l]; };
  for (let q = 0; q < nu; q++) {
    const u = u0 + q * du, [x, z] = O.at(u), [nx, nz] = normalAt(x, z);
    let s = 0, c = 0;
    for (const w of [10, 20, 30, 40]) { const px = x - nx * w, pz = z - nz * w; if (Math.abs(px) < R + 20 && Math.abs(pz) < R + 20) { s += gAt(px, pz); c++; } }
    relief[q] = c ? s / c - S : 0;
  }
  const mouthD = (u) => { const d = Math.min(Math.abs(u - uIn), lake ? Math.abs(u - uOut) : 1e9); return O.closed ? Math.min(d, O.span[1] - d) : d; };
  for (let q = 0; q < nu; q++) {
    const u = u0 + q * du;
    let rl = 0, c = 0; for (let d = -6; d <= 6; d++) { const p = q + d; if (p >= 0 && p < nu) { rl += relief[p]; c++; } }   // (over ~50 m)
    const rh = rl / c - 4;
    let t = .2 + rock.bias + rock.hard * rh / 12 + (1 - rock.hard) * clamp(rh / 40, -.2, .15) + .35 * (.4 + .6 * rock.hard) * noise1(u / 110, plan.geoNoise) - .3 * clamp(O.bay(u), -1, 1) - (lake ? .2 : 0);
    t *= smooth((mouthD(u) - 25) / 70);   // (the river's mouth: its own silt, low and soft)
    type[q] = clamp(t, 0, 1);
  }
  const typeAt = (u) => { const f = clamp((u - u0) / du, 0, nu - 1.001), q = f | 0; return type[q] + (type[q + 1] - type[q]) * (f - q); };
  const tMean = type.reduce((a, b) => a + b, 0) / nu;   // (out in the open the bed is the water's own, not the nearest shore's)
  const reliefAt = (u) => relief[clamp(Math.round((u - u0) / du), 0, nu - 1)];

  // ---- the SHAPE of the ground, cell by cell: the bed under the water, the shore's profile on the land behind it
  const Dmax = plan.depth, open = new Uint8Array(NN), shoreW = new Float32Array(NN).fill(1e9), tCell = new Float32Array(NN);
  const W = M.water, riv = M.riverness;
  const bedOf = (s, t, x, z) => {   // how deep, s metres out: shelving (a beach's 1:22) to plunging (a cliff's 1:1.6)
    const k = t < .5 ? mix(.045, .22, t / .5) : mix(.22, .6, (t - .5) / .5);
    // (and however gently it shelves, the open water deepens to its own depth 60-140 m out: room for the lanes)
    return Math.max(Dmax * (1 - Math.exp(-k * s / Dmax)), Dmax * .92 * smooth((s - 25) / 110)) + Math.max(0, t - .6) * 3.5 * smooth(s / 4) + .35 * noise2(x / 13, z / 13, 7) * smooth(s / 8);
  };
  const areas = M.areas ?? [], areaD = (x, z) => areas.reduce((m, a) => Math.min(m, Math.hypot(Math.max(a.x0 - x, 0, x - a.x1), Math.max(a.z0 - z, 0, z - a.z1))), 1e9);
  const landOf = (w, t, nat, rel, x, z) => {   // the land w metres in from the waterline
    const Bw = 24 + 8 * noise2(x / 60, z / 60, 3);
    const beach = S + 1.5 * smooth(w / Bw) + .25 * smooth((w - Bw) / 6) * (1 - smooth((w - Bw - 12) / 8)) * (1 + noise2(x / 9, z / 9, 5));   // (a berm, a low dune ridge behind)
    const rocky = S + .3 + 2.2 * smooth(w / 12) + .6 * Math.max(0, noise2(x / 3.1, z / 3.1, 9)) * (1 - smooth(w / 14));   // (ledges and boulders)
    const Hc = clamp(Math.max(rel, 6 + 4 * noise2(x / 40, z / 40, 11)), 5, 20), cliff = S + Hc * smooth(w / 3);
    const prof = t < .5 ? mix(beach, rocky, t / .5) : mix(rocky, cliff, (t - .5) / .5);
    const inW = t < .5 ? mix(Bw, 10, t / .5) : mix(10, 3, (t - .5) / .5);
    let y = mix(prof, nat, smooth((w - inW) / 30));
    // (high land behind a beach or a rocky shore: a BANK rising from it at ~15-22 deg, not a wall -- carried further
    //  inland the higher the land; a cliff stays sheer)
    const bank = prof + (.3 + .08 * noise2(x / 50, z / 50, 13)) * Math.max(0, w - inW * .6);
    if (t < .75) y = Math.min(y, mix(bank, y, smooth((t - .6) / .15)));
    const L = Math.max(58, Math.min(58 + 2.4 * clamp(rel - 8, 0, 22), w + areaD(x, z)));   // (the town's, farms' rectangles: their own)
    y = mix(y, nat, smooth((w - (L - 16)) / 16));       // (nothing changed past 58 m -- up to ~110 under high land: the town's ground is the land's own)
    return Math.max(y, S + Math.min(.3, .15 * w));      // (the shore's land dry: no hollow behind it under the water's level)
  };
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const k = j * n + i, x = x0 + i * res, z = z0 + j * res, s = O.s(x, z);
    if (s < -112) continue;
    const u = O.u(x, z), t = typeAt(u), nat = ground0[k];
    tCell[k] = t; shoreW[k] = s;
    let y;
    if (s > 0) {
      y = Math.min(nat, S - bedOf(s, mix(t, tMean, smooth((s - 20) / 70)), x, z));
      open[k] = 1; W[k] = S;
      riv[k] *= lake ? 0 : clamp(1 - s / 40, 0, 1) * (x < xIn + 60 ? 1 : 0);   // (still water; the river's push fading out past its mouth)
      if (lake) riv[k] = 0;
    } else {
      y = landOf(-s, t, nat, reliefAt(u), x, z);
      // (a lake's river, coming in and going out: its channel and banks left as they are -- the sea's has its estuary)
      if (lake) { const dr = Math.abs(z - riverZf(x)) - hwf(x); if (dr < 12) y = mix(nat, y, smooth((dr - 3) / 9)); }
      if (W[k] === W[k] && W[k] < S + .1 && riv[k] < .3) W[k] = NaN;   // (a brook drowned in the shore's sand: it soaks in at the beach)
    }
    base[k] = y + carve[k];
  }
  // ---- the ESTUARY (the sea's): the river's last 90 m widening to its mouth, its bed deepening, its water the river's
  // own level falling to the sea's
  let mouth = null;
  if (!lake) {
    const Le = 90, E = 14;
    mouth = { x: xIn, z: riverZf(xIn), hw: hwf(xIn) + E };
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const k = j * n + i, x = x0 + i * res, z = z0 + j * res;
      if (x < xIn - Le - 10 || x > xIn + 40) continue;
      const f = smooth((x - (xIn - Le)) / Le), hw = hwf(x) + E * f * f, d = Math.abs(z - riverZf(x)), s = O.s(x, z);
      if (d > hw + 14 || s > 30) continue;
      const lv = x < xIn ? Math.max(S, levelf(x)) : S, depth = 1.6 + 1.6 * f;
      const ny = d < hw ? lv - depth * (1 - (d / hw) ** 2) : lv + Math.min(.6, .3 * (d - hw)) + (ground0[k] - lv) * smooth((d - hw - 4) / 10) * (1 - f) ;
      const cur = base[k] - carve[k];
      if (d < hw) { base[k] = Math.min(cur, ny) + carve[k]; if (!(W[k] >= lv)) W[k] = lv; if (s <= 0) riv[k] = Math.max(riv[k], 1 - smooth((d - hw + 3) / 4)) * (1 - .6 * f); }
      else if (s <= 0 && cur > ny && d < hw + 6) base[k] = ny + carve[k];
      else if (s <= 0 && cur < ny) { base[k] = ny + carve[k]; if (W[k] === W[k] && riv[k] < .3) W[k] = NaN; }
    }
  }
  // ---- the river's own numbers (riverLevel, the barge, the reflection): the sea's level from the mouth on; a lake's
  // across it
  for (let q = 0; q < RV.n; q++) { const x = RV.x0 + q; if (x >= xIn && (!lake || x <= xOut)) RV.level[q] = S; }

  // ---- WET, the distance to the water (+ on land, - in it): mapgen's chamfer again over the new ground
  const isWet = (k) => W[k] > base[k] - carve[k];
  const dist = (wet) => {
    const D = new Float32Array(NN), a = res, b = res * Math.SQRT2;
    for (let k = 0; k < NN; k++) D[k] = wet(k) ? 0 : 1e9;
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const k = j * n + i; let v = D[k];
      if (i > 0) v = Math.min(v, D[k - 1] + a); if (j > 0) v = Math.min(v, D[k - n] + a);
      if (i > 0 && j > 0) v = Math.min(v, D[k - n - 1] + b); if (i < n - 1 && j > 0) v = Math.min(v, D[k - n + 1] + b); D[k] = v; }
    for (let j = n - 1; j >= 0; j--) for (let i = n - 1; i >= 0; i--) { const k = j * n + i; let v = D[k];
      if (i < n - 1) v = Math.min(v, D[k + 1] + a); if (j < n - 1) v = Math.min(v, D[k + n] + a);
      if (i < n - 1 && j < n - 1) v = Math.min(v, D[k + n + 1] + b); if (i > 0 && j < n - 1) v = Math.min(v, D[k + n - 1] + b); D[k] = v; }
    return D;
  };
  const dLand = dist(isWet), dWater = dist((k) => !isWet(k));
  for (let k = 0; k < NN; k++) { const w = isWet(k); M.wet[k] = w ? 1 : 0; M.sd[k] = w ? -dWater[k] : dLand[k]; }

  // ---- the SURFACE: sand on the beach and under the shallows, rock on the cliffs and the ledges, wet sand at the
  // waterline -- bare ground, no lawn over it (a landscape's own surface kept everywhere else)
  const own = M.surface, srf = own ?? { n, res, x0, z0, rgb: new Float32Array(NN * 3), bare: new Float32Array(NN) };
  const sand = lake ? [.62, .57, .48] : rock.sand, rk = rock.rock, wetSand = sand.map((v) => v * .62), mud = [.42, .38, .32];
  if (!own) for (let k = 0; k < NN; k++) srf.rgb.set(sand, k * 3);   // (the colour under bare 0 never shows, but bilinear reads it)
  for (let k = 0; k < NN; k++) {
    const s = shoreW[k]; if (s > 1e8) continue;
    const t = tCell[k], y = base[k] - carve[k], w = -s;
    const rocky = smooth((t - .3) / .35), jit = 1 + .05 * hash(k, 3, 1);
    let col, bare;
    if (s > 0) { col = rocky > .5 ? rk.map((v) => v * .8) : sand; bare = 1; }
    else {
      const sandy = (1 - rocky) * (1 - smooth((w - 26) / 10)), stony = rocky * (1 - smooth((w - (t > .7 ? 5 : 14)) / 8));
      bare = Math.max(sandy, stony);
      if (bare < .02) continue;
      col = sandy >= stony ? (y < S + .45 ? wetSand.map((v, q) => mix(v, sand[q], smooth((y - S - .2) / .25))) : sand) : rk;
    }
    if (mouth && Math.abs(srf.x0 + (k % n) * res - mouth.x) < 70 && Math.abs(z0 + ((k / n) | 0) * res - mouth.z) < mouth.hw + 12) col = col.map((v, q) => mix(v, mud[q], .5));
    const b0 = own ? srf.bare[k] : 0;
    for (let q = 0; q < 3; q++) srf.rgb[k * 3 + q] = mix(own ? srf.rgb[k * 3 + q] : col[q] * jit, col[q] * jit, own ? bare : 1);
    srf.bare[k] = Math.max(b0, bare);
  }
  M.surface = srf;

  // ---- what it made: the open water's cells, the shoreline, the lanes
  const shore = traceShore(M, O, S, typeAt, mouthD, R);
  M.sea = { kind: plan.kind, level: S, open, rock: rock.name, plan: { ...plan, keep: undefined, bind: undefined }, xIn, xOut,
            mouth, inlet: lake ? { x: xIn, z: riverZf(xIn) } : null, outlet: lake ? { x: xOut, z: riverZf(xOut) } : null,
            shore, swell: O.N ? [-O.N[0], -O.N[1]] : null, center: O.C ?? null, shift: O.shift,
            ms: Math.round((typeof performance !== "undefined" ? performance.now() : Date.now()) - t0) };
  M.sea.lanes = makeLanes(M);
  return M;
}

// THE SHORELINE: points every ~4 m along the waterline, inside the world (a lake's all round, closed), each with the
// normal INTO the water, its arc length, the kind of shore, the land's height 12 m in and the water's depth 20 m out
function traceShore(M, O, S, typeAt, mouthD, R) {
  const pts = [];
  const g = groundOf(M);
  for (let u = O.span[0]; u <= O.span[1]; u += 4) {
    let [x, z] = O.at(u);
    if (Math.hypot(x, z) > R - 6) { if (!O.closed && pts.length) pts.push(null); continue; }
    const e = 1.5, gx = O.s(x + e, z) - O.s(x - e, z), gz = O.s(x, z + e) - O.s(x, z - e), l = Math.hypot(gx, gz) || 1, nx = gx / l, nz = gz / l;
    const t = typeAt(u), m = mouthD(u) < 20;
    pts.push({ x: +x.toFixed(2), z: +z.toFixed(2), nx: +nx.toFixed(4), nz: +nz.toFixed(4), u: 0,
               type: m ? "mouth" : t < .35 ? "beach" : t < .7 ? "rocky" : "cliff",
               landY: +(g(x - nx * 12, z - nz * 12) - S).toFixed(2), d20: +Math.max(0, S - g(x + nx * 20, z + nz * 20)).toFixed(2) });
  }
  // (one stretch: the longest run inside the world)
  const runs = [[]]; for (const p of pts) { if (p) runs[runs.length - 1].push(p); else runs.push([]); }
  const run = runs.sort((a, b) => b.length - a.length)[0];
  for (let k = 1; k < run.length; k++) run[k].u = +(run[k - 1].u + Math.hypot(run[k].x - run[k - 1].x, run[k].z - run[k - 1].z)).toFixed(2);
  return { pts: run, closed: !!O.closed, length: run.length ? run[run.length - 1].u : 0 };
}

// the map's ground, bilinear (as ground.js's naturalH reads it, before any plot is levelled)
function groundOf(M) {
  const { n, res, x0, z0, base, carve } = M;
  return (x, z) => {
    const fi = clamp((x - x0) / res, 0, n - 1.001), fj = clamp((z - z0) / res, 0, n - 1.001), i = fi | 0, j = fj | 0, a = fi - i, b = fj - j, k = j * n + i;
    const g = (q) => base[q] - carve[q];
    return (g(k) * (1 - a) + g(k + 1) * a) * (1 - b) + (g(k + n) * (1 - a) + g(k + n + 1) * a) * b;
  };
}

// THE SAILING LANES: over deep water (DEEP m and more, CLEAR m off any shore), smoothed -- the sea's along the coast from
// the world's edge to the world's edge (ships come in over the horizon), the lake's a loop round it
const DEEP = 6, CLEAR = 35;
function makeLanes(M) {
  const { shore, level: S } = M.sea, g = groundOf(M), R = M.sea.plan.radius, sd = sdOf(M);
  const pts = [];
  const step = 24;
  for (let k = 0; k < shore.pts.length; k += Math.max(1, Math.round(step / 4))) {
    const p = shore.pts[k];
    let best = null;
    for (let w = 20; w <= 220; w += 4) {
      const x = p.x + p.nx * w, z = p.z + p.nz * w;
      if (Math.hypot(x, z) > R - 10) break;
      if (S - g(x, z) >= DEEP && -sd(x, z) >= CLEAR) { best = [x, z]; break; }
    }
    if (best) pts.push(best);
  }
  // (smoothed twice; a lake's closed)
  const closed = M.sea.kind === "lake";
  let L = pts;
  for (let it = 0; it < 3; it++) L = L.map((p, k) => {
    const a = L[closed ? (k - 1 + L.length) % L.length : Math.max(0, k - 1)], b = L[closed ? (k + 1) % L.length : Math.min(L.length - 1, k + 1)];
    return [(a[0] + 2 * p[0] + b[0]) / 4, (a[1] + 2 * p[1] + b[1]) / 4];
  });
  L = L.map(([x, z]) => [+x.toFixed(1), +z.toFixed(1)]);
  const lanes = L.length >= 2 ? [{ name: closed ? "round the lake" : "along the coast", pts: L, closed }] : [];
  // (the sea's: where they leave the world -- each end carried on out along its own heading to the edge)
  if (!closed && L.length >= 2) {
    const ends = [[L[1], L[0]], [L[L.length - 2], L[L.length - 1]]].map(([a, b]) => {
      const dx = b[0] - a[0], dz = b[1] - a[1], l = Math.hypot(dx, dz) || 1;
      let x = b[0], z = b[1]; while (Math.hypot(x, z) < R + 30) { x += dx / l * 10; z += dz / l * 10; }
      return [+x.toFixed(1), +z.toFixed(1)];
    });
    lanes[0].pts = [ends[0], ...L, ends[1]];
    lanes[0].entries = ends;
  }
  return lanes;
}
function sdOf(M) {
  const { n, res, x0, z0, sd } = M;
  return (x, z) => { const fi = clamp((x - x0) / res, 0, n - 1.001), fj = clamp((z - z0) / res, 0, n - 1.001), i = fi | 0, j = fj | 0, a = fi - i, b = fj - j, k = j * n + i;
    return (sd[k] * (1 - a) + sd[k + 1] * a) * (1 - b) + (sd[k + n] * (1 - a) + sd[k + n + 1] * a) * b; };
}

// ---- THE API ---------------------------------------------------------------------------------------------------------
// seaAPI(M, { groundH, roads }) -> null (no open water) or the object docs/world.md "Open water" describes. groundH: the
// game's ground (ground.js, the plots levelled; default the map's own); roads: [{ pts: [[x, z, ...], ...] }] (ground.js
// roads, paths.js planRoads) -- harbourSite keeps near them.
export function seaAPI(M, { groundH = null, roads = null } = {}) {
  const D = M?.sea; if (!D) return null;
  const { n, res, x0, z0 } = M, S = D.level, gMap = groundOf(M), ground = groundH ?? gMap, sd = sdOf(M), R = D.plan.radius;
  const cell = (x, z) => { const i = Math.round((x - x0) / res), j = Math.round((z - z0) / res); return i < 0 || j < 0 || i >= n || j >= n ? -1 : j * n + i; };
  const isOpenWater = (x, z) => { const k = cell(x, z); return k < 0 ? (D.kind === "sea" && Math.hypot(x, z) > R && seawardOutside(D, x, z)) : D.open[k] === 1; };
  const waterAt = (x, z) => { const k = cell(x, z); if (k < 0) return isOpenWater(x, z) ? S : -Infinity; const w = M.water[k]; return w === w ? w : -Infinity; };
  const depth = (x, z) => { const w = waterAt(x, z); if (w === -Infinity) return 0; const k = cell(x, z); return Math.max(0, w - (k < 0 ? S - D.plan.depth : ground(x, z))); };

  // ROUTE: over open water at least `minDepth` deep and `clear` m off the shore, A* on an 8 m lattice, then pulled
  // straight wherever the water between allows: [[x, z], ...] from a to b, or null
  const G = 8, gn = Math.ceil(2 * (R + 24) / G) + 1, gx0 = -(R + 24);
  const navCache = new Map();
  const navOf = (minDepth, clear) => {
    const key = minDepth + "/" + clear; if (navCache.has(key)) return navCache.get(key);
    const ok = new Uint8Array(gn * gn);
    for (let j = 0; j < gn; j++) for (let i = 0; i < gn; i++) { const x = gx0 + i * G, z = gx0 + j * G; ok[j * gn + i] = isOpenWater(x, z) && depth(x, z) >= minDepth && -sd(x, z) >= clear ? 1 : 0; }
    navCache.set(key, ok); return ok;
  };
  const route = (a, b, { minDepth = 2.5, clear = 12 } = {}) => {
    const ok = navOf(minDepth, clear);
    const idx = ([x, z]) => [Math.round((x - gx0) / G), Math.round((z - gx0) / G)];
    const snap = (p) => {   // (the nearest navigable node within 80 m)
      const [i0, j0] = idx(p); let best = -1, bd = 1e9;
      for (let dj = -10; dj <= 10; dj++) for (let di = -10; di <= 10; di++) { const i = i0 + di, j = j0 + dj; if (i < 0 || j < 0 || i >= gn || j >= gn || !ok[j * gn + i]) continue; const d = di * di + dj * dj; if (d < bd) { bd = d; best = j * gn + i; } }
      return best;
    };
    const s = snap(a), t = snap(b); if (s < 0 || t < 0) return null;
    const gScore = new Float32Array(gn * gn).fill(Infinity), from = new Int32Array(gn * gn).fill(-1), closed = new Uint8Array(gn * gn);
    const ti = t % gn, tj = (t / gn) | 0, h = (k) => Math.hypot(k % gn - ti, ((k / gn) | 0) - tj);
    const open = [[h(s), s]]; gScore[s] = 0;
    while (open.length) {
      let m = 0; for (let q = 1; q < open.length; q++) if (open[q][0] < open[m][0]) m = q;   // (a few thousand nodes at most: a list will do)
      const [, k] = open[m]; open[m] = open[open.length - 1]; open.pop();
      if (closed[k]) continue; closed[k] = 1;
      if (k === t) break;
      const i = k % gn, j = (k / gn) | 0;
      for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
        const ii = i + di, jj = j + dj, q = jj * gn + ii;
        if ((!di && !dj) || ii < 0 || jj < 0 || ii >= gn || jj >= gn || !ok[q] || closed[q]) continue;
        const near = Math.max(0, 40 + sd(gx0 + ii * G, gx0 + jj * G)) / 40;   // (rather off the shore than along it)
        const c = gScore[k] + Math.hypot(di, dj) * (1 + .6 * near);
        if (c < gScore[q]) { gScore[q] = c; from[q] = k; open.push([c + h(q), q]); }
      }
    }
    if (from[t] < 0 && s !== t) return null;
    const path = []; for (let k = t; k >= 0; k = from[k]) { path.push([gx0 + (k % gn) * G, gx0 + ((k / gn) | 0) * G]); if (k === s) break; }
    path.reverse();
    const clearLine = (p, q) => { const L = Math.hypot(q[0] - p[0], q[1] - p[1]), m = Math.ceil(L / 3); for (let e = 1; e < m; e++) { const x = p[0] + (q[0] - p[0]) * e / m, z = p[1] + (q[1] - p[1]) * e / m; const k = idx([x, z]); if (!ok[k[1] * gn + k[0]]) return false; } return true; };
    const out = [path[0]];
    for (let k = 1; k < path.length; k++) if (k === path.length - 1 || !clearLine(out[out.length - 1], path[k + 1])) out.push(path[k]);
    return [[a[0], a[1]], ...out.slice(1, -1), [b[0], b[1]]].map(([x, z]) => [+x.toFixed(1), +z.toFixed(1)]);
  };

  // HARBOUR SITE: the best `length` m of shore near the town to build a port on -- sheltered (a bay: the land round
  // the water in front of it), deep enough close in (a ship of `draught` m at a quay or a short pier), its land low,
  // gentle and dry behind it, no cliff, not the river's mouth itself, clear of the town's walls and the farms, near the
  // town and its roads. -> { points, normals, mid, normal, tangent, heading, length, depth, landY, shelter, type, score,
  //                          dist, lane } or null
  const areas = M.areas ?? [];
  const shelterAt = (x, z) => {   // (what share of 32 rays from a point 40 m out meets land within 400 m)
    let hit = 0;
    for (let q = 0; q < 32; q++) {
      const a = q / 32 * TAU, dx = Math.cos(a), dz = Math.sin(a);
      for (let r = 8; r <= 400; r += 8) { const px = x + dx * r, pz = z + dz * r; if (cell(px, pz) < 0) break; if (!isOpenWater(px, pz) && waterAt(px, pz) === -Infinity) { hit++; break; } }
    }
    return hit / 32;
  };
  const roadDist = (x, z, rl) => { let d = Infinity; for (const r of rl ?? []) for (const p of r.pts ?? r) d = Math.min(d, Math.hypot(p[0] - x, p[1] - z)); return d; };
  const harbourSite = (town = [0, 0], { length = 100, draught = 3, roads: rl = api.roads, avoid = areas } = {}) => {
    const T = Array.isArray(town) ? town : [town.x, town.z], P = D.shore.pts, m = Math.max(3, Math.round(length / 4));
    if (P.length < m) return null;
    let best = null;
    const N = D.shore.closed ? P.length : P.length - m, why = { tried: 0, outside: 0, built: 0 };
    api.why = why;   // (what ruled the stretches out, when none is left)
    for (let k0 = 0; k0 < N; k0 += 2) {
      const seg = []; for (let q = 0; q < m; q++) seg.push(P[(k0 + q) % P.length]);
      const mid = seg[m >> 1];
      let nx = 0, nz = 0, cliff = 0, mouth = 0, dev = 0, land = 0, slope = 0, d20 = 0, d40 = 0, inArea = 0, outside = 0;
      for (const p of seg) { nx += p.nx; nz += p.nz; }
      const nl = Math.hypot(nx, nz) || 1; nx /= nl; nz /= nl;
      for (const p of seg) {
        if (p.type === "cliff") cliff++; if (p.type === "mouth") mouth++;
        dev = Math.max(dev, Math.acos(clamp(p.nx * nx + p.nz * nz, -1, 1)));
        const a = ground(p.x - p.nx * 12, p.z - p.nz * 12) - S, b = ground(p.x - p.nx * 35, p.z - p.nz * 35) - S;
        land += a; slope += Math.abs(b - a) / 23;
        d20 += depth(p.x + p.nx * 20, p.z + p.nz * 20); d40 += depth(p.x + p.nx * 40, p.z + p.nz * 40);
        if (Math.hypot(p.x, p.z) > R - 25) outside++;
        for (let w = 0; w <= 40; w += 10) { const x = p.x - p.nx * w, z = p.z - p.nz * w; if (avoid.some((r) => x > r.x0 - 4 && x < r.x1 + 4 && z > r.z0 - 4 && z < r.z1 + 4)) { inArea++; break; } }
      }
      land /= m; slope /= m; d20 /= m; d40 /= m;
      why.tried++; if (outside) { why.outside++; continue; } if (inArea > m * .1) { why.built++; continue; }
      const dist = Math.hypot(mid.x - T[0], mid.z - T[1]), shelter = shelterAt(mid.x + nx * 40, mid.z + nz * 40);
      const rd = rl ? roadDist(mid.x - nx * 30, mid.z - nz * 30, rl) : 0;
      const score = dist / 60 + 6 * Math.max(0, .62 - shelter) + .9 * Math.max(0, draught + 1 - d40) + .5 * Math.max(0, draught - d20)
                  + .5 * Math.min(Math.abs(land - 2.2), 6) + 4 * Math.min(slope, .45) + 2.5 * Math.max(0, dev - .35) + 8 * cliff / m + 3 * mouth / m + (rl ? Math.min(rd, 300) / 70 : 0);
      if (!best || score < best.score) best = { k0, seg, mid, nx, nz, dist, shelter, land, slope, d20, d40, cliff, mouth, rd, score };
    }
    if (!best) return null;
    const { seg, nx, nz } = best, types = {};
    for (const p of seg) types[p.type] = (types[p.type] ?? 0) + 1;
    const L = seg.reduce((s, p, q) => s + (q ? Math.hypot(p.x - seg[q - 1].x, p.z - seg[q - 1].z) : 0), 0);
    let lane = null, ld = Infinity;
    for (const ln of D.lanes) for (const p of ln.pts) { const d = Math.hypot(p[0] - best.mid.x, p[1] - best.mid.z); if (d < ld) { ld = d; lane = { name: ln.name, at: p }; } }
    return {
      points: seg.map((p) => [p.x, p.z]), normals: seg.map((p) => [p.nx, p.nz]),
      mid: [best.mid.x, best.mid.z], normal: [+nx.toFixed(4), +nz.toFixed(4)], tangent: [+(-nz).toFixed(4), +nx.toFixed(4)],
      heading: +Math.atan2(nx, nz).toFixed(4), length: +L.toFixed(1),
      depth: { at10: +depth(best.mid.x + nx * 10, best.mid.z + nz * 10).toFixed(2), at20: +best.d20.toFixed(2), at40: +best.d40.toFixed(2) },
      landY: +(S + best.land).toFixed(2), level: S, shelter: +best.shelter.toFixed(2), slope: +best.slope.toFixed(3),
      type: Object.entries(types).sort((a, b) => b[1] - a[1])[0][0], score: +best.score.toFixed(2), dist: +best.dist.toFixed(1),
      road: best.rd === Infinity ? null : +best.rd.toFixed(1), lane,
    };
  };
  // (the reflection's one plane: the open water's level when the camera is nearer it than the river's run upstream)
  const planeY = (x, z, riverLevel) => {
    if (x >= D.xIn - 40 && (D.kind === "sea" || x <= D.xOut + 40)) return S;
    const k = cell(x, z); return k >= 0 && M.sd[k] > 0 && D.open[k] ? S : riverLevel(x);
  };
  const api = {
    kind: D.kind, level: S, rock: D.rock, mouth: D.mouth, inlet: D.inlet, outlet: D.outlet, center: D.center, swell: D.swell,
    shore: D.shore, lanes: D.lanes, entries: D.lanes[0]?.entries ?? [],
    isOpenWater, depth, waterAt, harbourSite, route, planeY,
    // (the open water's far reach for the renderer: beyond the map, the sea's half of the world to the horizon)
    seaward: (x, z) => seawardOutside(D, x, z),
    roads,   // (harbourSite's default roads: index.html sets them once they are planned)
  };
  return api;
}
// (past the map's edge: is this on the sea's side of the coast's line? -- the far water drawn to the horizon)
function seawardOutside(D, x, z) {
  if (D.kind !== "sea") return false;
  const P = D.shore.pts; if (!P.length) return false;
  const a = P[0], b = P[P.length - 1], tx = b.x - a.x, tz = b.z - a.z;   // (the coast's chord: the sea on its normals' side)
  const nx = tz, nz = -tx, side = Math.sign(nx * a.nx + nz * a.nz) || 1;
  return ((x - a.x) * nx + (z - a.z) * nz) * side > 0;
}

// THE WATER SHEET's extra numbers for the renderer (index.html mapWater): for each vertex [x, y, z] of the sheet, how
// much it is open water (0 river, stream, moat; 1 sea or lake) and how deep (its y less the ground; < 0 on the dry ring)
export function openWaterAttributes(M, pos) {
  const D = M.sea, g = groundOf(M), nv = pos.length / 3, open = new Float32Array(nv), depth = new Float32Array(nv), surf = new Float32Array(nv);
  const { n, res, x0, z0 } = M;
  for (let v = 0; v < nv; v++) {
    const x = pos[v * 3], y = pos[v * 3 + 1], z = pos[v * 3 + 2];
    const i = Math.round((x - x0) / res), j = Math.round((z - z0) / res);
    let o = 0;   // (an open cell, or a dry one beside it: the shore's own ring takes the sea's look)
    for (let dj = -1; dj <= 1 && !o; dj++) for (let di = -1; di <= 1; di++) { const ii = i + di, jj = j + dj; if (ii >= 0 && jj >= 0 && ii < n && jj < n && D.open[jj * n + ii]) { o = 1; break; } }
    open[v] = o; depth[v] = y - g(x, z);
    // (surf: where foam may break -- the ground's slope there: a beach's or a ledge's, not a cliff's face)
    const sl = Math.hypot(g(x + 2, z) - g(x - 2, z), g(x, z + 2) - g(x, z - 2)) / 4;
    surf[v] = 1 - smooth((sl - .35) / .4);
  }
  return { open, depth, surf };
}
// THE FAR SEA: past the map's square, the sea's half of the world out to `far` m -- a coarse sheet at its level, deep
// (no bed under it to see), for the horizon. -> { pos, idx, open, depth } or null
export function farSea(M, far = 2400) {
  const D = M.sea; if (!D || D.kind !== "sea") return null;
  const lo = M.x0, hi = M.x0 + (M.n - 1) * M.res, S = D.level, pos = [], idx = [], vid = new Map();
  // (the lattice: its lines through the map's own edges, so the two sheets meet without a seam -- 16 m along the map,
  //  coarser out)
  const xs = [];
  for (let k = 0, m = Math.ceil((hi - lo) / 16); k <= m; k++) xs.push(lo + (hi - lo) * k / m);
  for (let x = hi; x < far; ) { x += x < hi + 200 ? 16 : 120; xs.push(Math.min(x, far)); }
  for (let x = lo; x > -far; ) { x -= x > lo - 200 ? 16 : 120; xs.unshift(Math.max(x, -far)); }
  const inside = (x, z) => x > lo && x < hi && z > lo && z < hi;   // (the map square: its own sheet)
  // (past either end of the coast inside the world, its last stretch's own line: the coast bends off the chord there)
  const P = D.shore.pts, A = P[0], B = P[P.length - 1], cl = Math.hypot(B.x - A.x, B.z - A.z) || 1, cx = (B.x - A.x) / cl, cz = (B.z - A.z) / cl;
  const pastEnd = (x, z) => ((x - B.x) * cx + (z - B.z) * cz > 0 && (x - B.x) * B.nx + (z - B.z) * B.nz > -30)
                         || ((x - A.x) * cx + (z - A.z) * cz < 0 && (x - A.x) * A.nx + (z - A.z) * A.nz > -30);
  const sea = (x, z) => seawardOutside(D, x, z) || pastEnd(x, z);
  const vert = (i, j) => { const k = i * 4096 + j; if (!vid.has(k)) { vid.set(k, pos.length / 3); pos.push(xs[i], S, xs[j]); } return vid.get(k); };
  for (let j = 0; j + 1 < xs.length; j++) for (let i = 0; i + 1 < xs.length; i++) {
    const xa = xs[i], xb = xs[i + 1], za = xs[j], zb = xs[j + 1];
    if (inside((xa + xb) / 2, (za + zb) / 2) || Math.hypot((xa + xb) / 2, (za + zb) / 2) > far) continue;
    if (!sea(xa, za) && !sea(xb, za) && !sea(xa, zb) && !sea(xb, zb)) continue;
    const a = vert(i, j), b = vert(i + 1, j), c = vert(i, j + 1), d = vert(i + 1, j + 1);
    idx.push(a, c, b, b, c, d);
  }
  const nv = pos.length / 3;
  return { pos, idx, open: new Float32Array(nv).fill(1), depth: new Float32Array(nv).fill(D.plan.depth), surf: new Float32Array(nv).fill(1) };
}
