// PTERANODONS OVER THE WATER (2026-11-06): two or three PTERANODONS (assets/creatures/dinosaurs/pteranodon.json, species.js
// makePteranodon) soar over the open water -- the sea or the big lake (sea.js isOpenWater), else the small lake (ground.js
// LAKE), else over the land -- in slow wide circles, the wings held out and still, a few beats now and then; now and
// again one comes down in a long shallow SWOOP to skim a metre or two over the water and climbs away beating hard.
// Their bodies are the sculpted one, in a composite herd of their own, always in the flight pose (skeleton.js an.fly 1).
//
// They are not wanderers: a 6 m glider turning on a bird's 2.2 rad/s about short legs looks like a toy. Each one's path
// is a PURE FUNCTION OF THE SHARED CLOCK (T: simTick x TICK), like the whales' (sealife.js) -- every peer sees the same
// pteranodon in the same place, and nothing is simulated:
//   CIRCLING: round a centre at its own radius and speed, one way round; every CYCLE (its own length) the centre may move
//     on to another of its ANCHORS (centres where the whole circle lies over open water, found once), gliding there.
//   HEIGHT: its own height over the water, swelling slowly up and down -- and never lower than the ground ahead of it
//     allows: the FLOOR (the ground, or the water where there is water over it, plus CLEAR m over land / SKIM over the
//     water) along its path from LOOK s behind to LOOK s ahead, less CLIMB m/s for each second away, so it climbs
//     smoothly to a rise before it gets there and never clips the terrain (the body or either wingtip).
//   SWOOP: in some cycles (SWOOP.share), once its circle has settled, the root dips to SWOOP.low m over the water and up
//     again over SWOOP.dur s -- only where the water lies under all of that stretch of the path and clear of the ships'
//     lanes; then a burst of beats as it climbs away.
//   BEATS: bursts of a few beats every SLOT s (the pattern FLAPS, beats a slot), the wings otherwise still and level.
//     The wing clock (an.wingT) is each burst's own progress in whole beats, so it starts over each slot unseen.
//   It banks into the turn as its speed and the turn's rate want (roll), and pitches with its climb.
//
//   const pt = createPterosaurs(scene, { SEA, hasLake, lakeSD, waterY, groundH, groundR, seed })   // null if none fly
//   pt.update(T, t)   // T: the shared sim clock (where they are); t: the render clock (the herd's posing)
//   pt.list           // [{ an, anchors, R, v, ... }] (the debug panel); pt.peek(i, T): where one is at clock T
import { createComposite } from "./composite.js";
import { makePteranodon } from "./species.js";

export const PTERO = {
  n: { water: 3, land: 2 },
  radius: [26, 46],     // m: the circle
  speed: [8.2, 10.4],   // m/s along it
  alt: [16, 34],        // m over the water (over the land: LAND_ALT)
  landAlt: [34, 48],
  swell: [5, 3],        // m: the height's two slow swells
  cycle: [80, 120],     // s: how often the centre may move on
  glide: 6,             // m/s: the centre's pace moving to the next anchor (the transition's length by the distance)
  anchors: 3,           // centres each one keeps
  spread: 260,          // m: its anchors within this of its first
  apart: 70,            // m: between different pteranodons' first centres
  clear: 26,            // m over the ground (trees and roofs are not in groundH)
  skim: 1.4,            // m over the water: the floor where there is water
  look: 6, step: .5, climb: 2.6,   // the floor's look behind and ahead (s), its sampling, the climb it allows (m/s)
  span: 3.1,            // m: half the wingspan (the floor sampled under the wingtips too)
  swoop: { share: .5, low: 1.9, dur: 18, lanes: 30 },
  slot: 13, flaps: [3, 4, 0, 3, 5, 0, 4, 2, 0], beatHz: 1.35, wingSpeed: .62, climbBeats: 6,   // (wingSpeed: the rig's anim.speed)
};

const TAU = Math.PI * 2;
const ss = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
const rng = (seed) => { let s = (seed >>> 0) || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; };
const hash = (a, b) => { let h = (Math.imul(a | 0, 2654435761) ^ Math.imul((b | 0) + 0x9e37, 1597334677)) >>> 0; h = Math.imul(h ^ (h >>> 15), 2246822519) >>> 0; return ((h ^ (h >>> 13)) >>> 0) / 4294967296; };
function segDist(x, z, a, b) {
  const ex = b[0] - a[0], ez = b[1] - a[1], l2 = ex * ex + ez * ez || 1, t = Math.max(0, Math.min(1, ((x - a[0]) * ex + (z - a[1]) * ez) / l2));
  return Math.hypot(x - a[0] - ex * t, z - a[1] - ez * t);
}

export function createPterosaurs(scene, { SEA = null, hasLake = false, lakeSD = null, waterY, groundH, groundR = 400, seed = 1 } = {}) {
  const R = rng((seed >>> 0) * 2246822519 + 0x97e0), P = PTERO;
  const big = !!SEA && (SEA.kind === "sea" || SEA.kind === "lake");
  const open = (x, z) => (big && SEA.isOpenWater(x, z)) || (!big && hasLake && lakeSD(x, z) < -3);
  const floor = (x, z) => { const g = groundH(x, z), w = waterY(x, z); return w > g + .3 ? w + P.skim : g + P.clear; };
  const lanes = big ? SEA.lanes ?? [] : [];
  const nearLane = (x, z, d) => lanes.some((ln) => ln.pts.some((p, j) => j && segDist(x, z, ln.pts[j - 1], p) < d));
  // a circle of radius r round (x, z) wholly over open water (and a margin), so the swoops have water under them
  const fits = (x, z, r) => {
    if (!open(x, z)) return false;
    for (let k = 0; k < 16; k++) { const a = k / 16 * TAU, q = r + 10; if (!open(x + Math.cos(a) * q, z + Math.sin(a) * q)) return false; }
    return true;
  };
  // the water's centres: a 16 m grid out past the map, nearest the town first
  let water = [];
  if (big || hasLake) {
    const ext = Math.min(700, groundR + 300), st = 16;
    for (let z = -ext; z <= ext; z += st) for (let x = -ext; x <= ext; x += st) if (open(x, z)) water.push([Math.hypot(x, z), x, z]);
    water.sort((a, b) => a[0] - b[0]);
  }
  const list = [], herd = createComposite(3 * 160);
  scene.add(herd.mesh);
  const mode = water.length ? "water" : "land";
  for (let i = 0; i < P.n[mode]; i++) {
    let r = lerp(P.radius[0], P.radius[1], R()), anchors = [];
    if (mode === "water") {
      for (let tries = 0; tries < 3 && !anchors.length; tries++, r *= .72) {
        for (const [, x, z] of water) {
          if (!fits(x, z, r) || list.some((s) => Math.hypot(s.anchors[0][0] - x, s.anchors[0][1] - z) < P.apart)) continue;
          anchors.push([x, z]); break;
        }
      }
      if (!anchors.length) break;
      const [x0, z0] = anchors[0], more = water.filter(([, x, z]) => Math.hypot(x - x0, z - z0) < P.spread && Math.hypot(x - x0, z - z0) > r);
      for (let k = 0; k < 60 && anchors.length < P.anchors && more.length; k++) {
        const [, x, z] = more[Math.floor(R() * more.length)];
        if (fits(x, z, r) && anchors.every((a) => Math.hypot(a[0] - x, a[1] - z) > r * .8)) anchors.push([x, z]);
      }
    } else {   // no water: wide circles over the country round the town, high
      for (let k = 0; k < P.anchors; k++) { const a = R() * TAU, d = groundR * (.35 + R() * .3); anchors.push([Math.cos(a) * d, Math.sin(a) * d]); }
    }
    const W = mode === "water" ? Math.max(...anchors.map(([x, z]) => waterY(x, z))) : Math.max(...anchors.map(([x, z]) => groundH(x, z)));
    const alt = mode === "water" ? lerp(P.alt[0], P.alt[1], R()) : lerp(P.landAlt[0], P.landAlt[1], R());
    const an = herd.add(makePteranodon());
    an.fly = an.flyT = 1; an.rotY = 0; an.animT = 0; an.wingT = 0;
    list.push({ an, anchors, R: r, v: lerp(P.speed[0], P.speed[1], R()), dir: R() < .5 ? 1 : -1, th0: R() * TAU, W, alt, mode,
                cyc: lerp(P.cycle[0], P.cycle[1], R()), off: R() * 500, ph: [R() * TAU, R() * TAU], k: i, swoops: new Map(), floors: new Map() });
  }
  if (!list.length) return null;

  // ---- where one is at clock T: the circle's centre (gliding between anchors), the point on the circle, the planned height
  const centre = (s, c) => s.anchors[Math.floor(hash(s.k * 31 + 7, c) * s.anchors.length)];
  function flat(s, T) {
    const u = T + s.off, c = Math.floor(u / s.cyc), tau = u - c * s.cyc;
    const A = centre(s, c - 1), B = centre(s, c), d = Math.hypot(B[0] - A[0], B[1] - A[1]), tr = Math.min(s.cyc * .4, d / P.glide);
    const m = tr > 0 ? ss(0, tr, tau) : 1, th = s.th0 + s.dir * s.v / s.R * T;
    return [lerp(A[0], B[0], m) + Math.cos(th) * s.R, lerp(A[1], B[1], m) - Math.sin(th) * s.R, c, tau, tr];
  }
  // the swoop of cycle c (memoised: a pure function of the cycle): its start (tau) or null -- where all its stretch of the
  // path, a few seconds either side, lies over open water, away from the lanes
  function swoopOf(s, c) {
    if (s.swoops.has(c)) return s.swoops.get(c);
    let at = null;
    if (s.mode === "water" && hash(s.k * 17 + 3, c) < P.swoop.share) {
      const u0 = c * s.cyc - s.off, [, , , , tr] = flat(s, u0 + 1), t0 = tr + 8, room = s.cyc - t0 - P.swoop.dur - 10;
      if (room > 0) {
        const tau = t0 + hash(s.k * 13 + 5, c) * room;
        let ok = true;
        for (let k = -4 - P.look; k <= P.swoop.dur + 6 + P.look && ok; k += 2) { const [x, z] = flat(s, u0 + tau + k); if (!open(x, z) || nearLane(x, z, P.swoop.lanes)) ok = false; }
        if (ok) at = tau;
      }
    }
    s.swoops.set(c, at);
    if (s.swoops.size > 16) s.swoops.delete(s.swoops.keys().next().value);
    return at;
  }
  // the planned height (before the floor): its height over the water swelling, and the swoop's dip
  function planY(s, T, x, z, c, tau) {
    let y = s.W + s.alt + P.swell[0] * Math.sin(T * .031 + s.ph[0]) + P.swell[1] * Math.sin(T * .077 + s.ph[1]);
    const sw = swoopOf(s, c);
    if (sw !== null) {
      const k = (tau - sw) / P.swoop.dur;
      if (k > 0 && k < 1) { const dip = k < .45 ? ss(0, .45, k) : k < .58 ? 1 : 1 - ss(.58, 1, k); y = lerp(y, waterY(x, z) + P.swoop.low, dip); }
    }
    return y;
  }
  // the floor along the path, from LOOK s behind to LOOK ahead, less CLIMB m/s for every second away -- sampled (with the
  // wingtips', across the way it goes) at fixed STEPs of the clock, each sample memoised: one new one a step, not dozens a frame
  function floorSample(s, q) {
    let g = s.floors.get(q);
    if (g !== undefined) return g;
    const T = q * P.step, [x, z] = flat(s, T), [x2, z2] = flat(s, T + .2), hx = x2 - x, hz = z2 - z, hl = Math.hypot(hx, hz) || 1, nx = -hz / hl * P.span, nz = hx / hl * P.span;
    g = Math.max(floor(x, z), floor(x + nx, z + nz) - P.clear * .6, floor(x - nx, z - nz) - P.clear * .6);
    s.floors.set(q, g);
    if (s.floors.size > 96) s.floors.delete(s.floors.keys().next().value);
    return g;
  }
  function floorAt(s, T) {
    let f = -Infinity;
    const q0 = Math.floor((T - P.look) / P.step), q1 = Math.ceil((T + P.look) / P.step);
    for (let q = q0; q <= q1; q++) f = Math.max(f, floorSample(s, q) - P.climb * Math.abs(q * P.step - T));
    return f;
  }
  function at(s, T) {
    const [x, z, c, tau] = flat(s, T);
    return [x, Math.max(planY(s, T, x, z, c, tau), floorAt(s, T)), z, c, tau];
  }
  // the wing clock: this slot's burst (FLAPS, beats a slot), and the climb out of a swoop -- each its progress in whole
  // beats, so the wings are level (the anim's sine at 0) between bursts and the clock starting over is never seen
  function wingClock(s, T, c, tau) {
    const u = T + s.off * 1.7, slot = Math.floor(u / P.slot), nb = P.flaps[((slot + s.k * 3) % P.flaps.length + P.flaps.length) % P.flaps.length];
    let beats = Math.min(nb, Math.max(0, (u - slot * P.slot - 1) * P.beatHz));
    const sw = swoopOf(s, c);
    if (sw !== null) beats += Math.min(P.climbBeats, Math.max(0, (tau - sw - P.swoop.dur * .6) * P.beatHz * 1.15));
    return beats / P.wingSpeed;
  }

  const api = {
    herd, list, mode,
    shift: 0,   // (debug: seconds added to the clock)
    T: 0,       // (debug: the clock last drawn)
    update(T0, t) {
      const T = api.T = T0 + api.shift;
      for (const s of list) {
        const a = s.an, [x, y, z, c, tau] = at(s, T), [x0, y0, z0] = at(s, T - .3), [x1, y1, z1] = at(s, T + .3);
        a.position.set(x, y, z);
        const h0 = Math.atan2(-(z - z0), x - x0), h1 = Math.atan2(-(z1 - z), x1 - x), h = Math.atan2(-(z1 - z0), x1 - x0);
        const v = Math.hypot(x1 - x0, z1 - z0) / .6, turn = (((h1 - h0 + Math.PI) % TAU + TAU) % TAU - Math.PI) / .3;
        a.rotY = h;
        a.pitch = Math.max(-.4, Math.min(.35, Math.atan2(y1 - y0, v * .6) * .8));
        a.roll = Math.max(-.6, Math.min(.6, -Math.atan(v * turn / 9.8)));
        a.fly = a.flyT = 1;
        a.wingT = wingClock(s, T, c, tau);
        a.animT = T;
      }
      herd.update(t);
    },
    peek(i, T) { const s = list[i]; if (!s) return null; const [x, y, z, c, tau] = at(s, T); return { x, y, z, cycle: c, tau, swoop: swoopOf(s, c), floor: floorAt(s, T), anchors: s.anchors, R: s.R }; },
  };
  console.log(`pterosaurs: ${list.length} over the ${mode}` + list.map((s) => ` -- round ${s.anchors[0].map(Math.round)} r ${Math.round(s.R)} at ${Math.round(s.alt)} m`).join(""));
  return api;
}
