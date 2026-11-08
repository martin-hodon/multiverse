// THE OPEN WATER'S GIANTS (2026-11-06): a world with a sea (sea.js SEA.kind "sea") gets one or two HUMPBACK WHALES and
// a pod of three ORCAS far offshore in deep water, and a PLESIOSAUR; a world with a big lake (SEA.kind "lake") gets the
// plesiosaur alone -- the Loch Ness wink. Their bodies are the sculpted ones (assets/creatures/sea/{humpback,orca,
// plesiosaurus}.json, species.js makeHumpback...), in a composite herd of their own (bodies.js skins them like any).
//
// They are not wanderers: a 14 m whale turning on a fish's 2.2 rad/s about 30 m legs looks like a toy. Each swims a
// LOOP of its own -- a smooth closed curve (an ellipse with a wobble) laid where the water is deep enough for it all the
// way round (sea.js isOpenWater and depth, checked at every point of the loop and a body's margin either side of it:
// open water only, so never the river's channel), clear of the ships' lanes and the river's mouth, and of the other
// loops. Where it is along its loop, how deep and how it is tipped are a PURE FUNCTION OF THE SHARED CLOCK (T: simTick x
// TICK), like the fish's leaps -- every peer sees the same whale blow at the same moment, and nothing is simulated.
//
//   HUMPBACK: a breathing cycle -- a long cruise deep down, up to the surface for three breaths, the BLOW at each (a
//     bushy V of a spout 4-5 m high: a pool of puffs, breath.js, scheduled up the column) as the head's top breaks the
//     water, sinking under between them; then
//     down again, and every third dive FLUKES-UP (the body tipped 65 degrees nose down, the tail stock and the flukes
//     lifted clear of the water and sliding in after it) where the water is deep enough for that.
//   ORCAS: the pod swims together (one ahead, two staggered behind), cruising a few metres down and then surfacing in a
//     run of shallow arcs, the bull's tall fin breaking the water at each crest, a short puff of a blow.
//   PLESIOSAUR: cruising a couple of metres down on its four flippers; now and then it rises, tipped head-up, until its
//     head and the top of its neck break the surface, holds there looking about, and sinks back.
//
// The loops' depth margins (NEED) are what the deepest any part of the body goes in the cycle -- the root's depth plus
// the body's own reach below it (flippers, and nose-down the head) and a metre to spare -- so no body pokes through the
// bed. Rings (stones.ring) where a body breaks the surface.
//
// (2026-11-07) AND THE SEA'S SMALLER LIFE, in a sea world only:
//   MANTAS: one or two reef mantas (assets/creatures/sea/ray.json, its `manta (reef manta)` variant: 3.4 m across) on
//     loops of their own offshore like the orcas', gliding a few metres down and rising now and then to cruise a
//     metre under the surface, banking into the loop's turns, the wings beating slow (the asset's own wave along them).
//   STINGRAYS: one or two over the shallow sandy bottom off a beach (1-5 m of water), each on a small loop of its own
//     a hand's breadth over the bed, in a coat of the asset's own (the common, the dark, the sandy).
//   NARWHALS: a pod in a COLD sea (the landscape's "alpine" climate) -- a tusked bull, a cow and her calf, and an old
//     pale bull -- and now and then a pair where it is temperate (or the river country) (assets/creatures/sea/narwhal.json:
//     its variants), on a loop of their own offshore like the orcas', cruising a few metres down and surfacing in two slow
//     arcs, the back awash and the bull's tusk lifting clear as the head comes up, a small puff of a blow at each.
//   CRABS: two small groups on a sea's beaches (assets/creatures/sea/crab.json -- an edible crab or two and shore crabs,
//     green or red-orange: the asset's coats), each crab scuttling SIDEWAYS along the wet sand a few metres either way of
//     its own spot and stopping, facing the water; its legs stepping only while it walks. A pure function of the clock too.
//
//   const life = createSeaLife(scene, { SEA, ring, seed, ground, blocked, harbour, climate })   // null if the world has no sea and no big lake
//     (ground(x, z): the land's height -- the crabs stand on it; blocked(x, z): a site or a stand; harbour: the port's points;
//      climate: the landscape's, null in the river country -- the narwhals')
//   life.update(T, t)    // T: the shared sim clock (positions); t: the render clock (the herd's posing, the puffs)
//   life.list            // [{ name, an, loop, ... }]: what swims where (the debug panel); life.callers: for calls.js
import { createComposite } from "./composite.js";
import { createPuffs } from "./breath.js";
import { makeHumpback, makeOrca, makePlesiosaurus, makeNarwhal, coatDef, variantDef } from "./species.js";

export const SEALIFE = {
  // loops: [semi-axis along, across] m; speed m/s; NEED: the water's least depth on the loop, m (with the fluke-up dive /
  // without); clear: from the ships' lanes, m; period: of the breathing cycle, s
  humpback: { axes: [78, 40], speed: 1.9, need: [21, 14], clear: 40, period: 110, n: 2 },
  orca:     { axes: [66, 34], speed: 3.0, need: 10, clear: 35, period: 60, pod: [[0, 0], [-7, 5], [-10, -5]] },
  plesio:   { axes: [[24, 14], [40, 22]], speed: 1.3, need: 5, clear: 12, period: 75 },   // (axes: a lake's, the sea's)
  // (2026-11-07) manta: a loop's axes, speed, least depth, lanes' clearance, period of its rise to the surface, how many;
  // stingray: a small loop's axes, speed, the water's depth all round it [least, most], how far out from the beach its
  // centre [m], how many; crab: groups, crabs a group, its cycle (s) and the walk in it (s), how far either way of its
  // spot it goes (m), how far up the beach from the waterline [m], groups apart (m), kept from the port (m), the coats
  // of a group (0 edible, 1 green shore crab, 2 red-orange)
  manta:    { axes: [44, 24], speed: 1.1, need: 7, clear: 25, period: 70, n: 2, variant: "manta (reef manta)" },
  stingray: { axes: [9, 4.5], speed: .45, depth: [1.1, 5], out: [9, 17], n: 2, clear: 8 },
  crab:     { groups: 2, size: [3, 4], period: 11, walk: 5, reach: 3, inland: [.7, 2.2], apart: 30, harbour: 50, coats: [0, 1, 1, 2] },
  // (2026-11-07) narwhal: the pod's loop, speed, least depth (the tusk's point tipped down on a dive), lanes' clearance,
  // breathing cycle; its members [along, across, who] where it is cold, a pair's where it is temperate (`stray`: the
  // share of such worlds that get one); which climates are which (arid, tropical, mediterranean: none)
  narwhal:  { axes: [54, 28], speed: 1.6, need: 9, clear: 30, period: 52, stray: .2,
              pod: [[0, 0, "male"], [-4.5, 3.2, "female"], [-4.4, 1.7, "calf"], [-8.5, -2.8, "old male"]], pair: [[0, 0, "male"], [-4.5, 3, "female"]],
              climate: { alpine: "cold", temperate: "temperate", grown: "temperate" } },
  mouth: 80,    // m: kept from the river's mouth
  blow: { pool: 128, life: 2.8, colour: [.9, .93, .96], size: [.45, 1.9], out: 1.0, rise: .9, opacity: .42, name: "whale blow" },
  puff: { pool: 64, life: 1.9, colour: [.9, .93, .96], size: [.14, .6], out: .45, rise: .35, opacity: .36, name: "orca blow" },
};

const TAU = Math.PI * 2;
const ss = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
const rng = (seed) => { let s = (seed >>> 0) || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; };

// a closed smooth loop through centre c: an ellipse (a along the angle th, b across) with a gentle wobble, sampled by arc
// length so a body swims it at an even speed. at(d) -> [x, z, heading (rotY), curvature]
function makeLoop(c, a, b, th, w1, w2) {
  const N = 256, P = [], cs = Math.cos(th), sn = Math.sin(th);
  for (let i = 0; i <= N; i++) {
    const s = i / N * TAU, u = a * Math.cos(s) + a * .08 * Math.cos(2 * s + w1), v = b * Math.sin(s) + b * .12 * Math.sin(3 * s + w2);
    P.push([c[0] + u * cs - v * sn, c[1] + u * sn + v * cs]);
  }
  const L = [0];
  for (let i = 1; i <= N; i++) L.push(L[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  const len = L[N];
  const at = (d) => {
    d = ((d % len) + len) % len;
    let lo = 0, hi = N;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (L[m] <= d) lo = m; else hi = m; }
    const k = (d - L[lo]) / (L[hi] - L[lo] || 1), p = P[lo], q = P[hi];
    const dx = q[0] - p[0], dz = q[1] - p[1];
    return [p[0] + dx * k, p[1] + dz * k, Math.atan2(-dz, dx)];
  };
  return { c, a, b, th, len, at, pts: P };
}

// does the loop keep to water deep enough, a margin either side, clear of the lanes and the mouth?
function loopFits(SEA, loop, need, margin, clear) {
  const lanes = SEA.lanes ?? [], mouth = SEA.mouth;
  for (let i = 0; i < loop.pts.length - 1; i += 4) {
    const [x, z] = loop.pts[i];
    for (const [ox, oz] of [[0, 0], [margin, 0], [-margin, 0], [0, margin], [0, -margin]]) {
      if (!SEA.isOpenWater(x + ox, z + oz) || SEA.depth(x + ox, z + oz) < need) return false;
    }
    if (mouth && Math.hypot(x - mouth.x, z - mouth.z) < SEALIFE.mouth) return false;
    if (clear > 0) for (const ln of lanes) {
      const P = ln.pts;
      for (let j = 0; j < P.length - 1; j++) if (segDist(x, z, P[j], P[j + 1]) < clear) return false;
    }
  }
  return true;
}
function segDist(x, z, a, b) {
  const ex = b[0] - a[0], ez = b[1] - a[1], l2 = ex * ex + ez * ez || 1, t = Math.max(0, Math.min(1, ((x - a[0]) * ex + (z - a[1]) * ez) / l2));
  return Math.hypot(x - a[0] - ex * t, z - a[1] - ez * t);
}
// the nearest-to-the-town loop of that size that fits (centres on a 20 m grid out to the map and 300 m past it), kept
// clear of the loops already laid; null if none does
function findLoop(SEA, R, [a, b], need, margin, clear, taken, near = [0, 0]) {
  const th = R() * Math.PI, w1 = R() * TAU, w2 = R() * TAU, cand = [];
  const ext = 650, st = 20;
  for (let z = -ext; z <= ext; z += st) for (let x = -ext; x <= ext; x += st) {
    if (!SEA.isOpenWater(x, z) || SEA.depth(x, z) < need) continue;
    if (taken.some((t) => Math.hypot(t.c[0] - x, t.c[1] - z) < t.a + a + 25)) continue;
    if (clear > 0 && (SEA.lanes ?? []).some((ln) => ln.pts.some((p, j) => j && segDist(x, z, ln.pts[j - 1], p) < b + clear))) continue;   // (a loop round a lane would cross it)
    cand.push([Math.hypot(x - near[0], z - near[1]), x, z]);
  }
  cand.sort((p, q) => p[0] - q[0]);
  for (const [, x, z] of cand.slice(0, 1500)) {
    for (const t of [th, th + Math.PI / 2]) {
      const L = makeLoop([x, z], a, b, t, w1, w2);
      if (loopFits(SEA, L, need, margin, clear)) return L;
    }
  }
  return null;
}

// (2026-11-07) a STINGRAY's small loop off a beach: centred `out` m from a beach's waterline, its long axis along the
// shore, the water under all of it between depth[0] and depth[1] -- shallow, sandy -- clear of the lanes, the mouth and
// the other loops; null if none
function findShallow(SEA, R, [a, b], [d0, d1], out, clear, taken) {
  const P = SEA.shore?.pts ?? [], cand = [];
  for (let k = 2; k < P.length - 2; k++) if (P[k].type === "beach") cand.push([R(), k]);
  cand.sort((p, q) => p[0] - q[0]);
  for (const [, k] of cand.slice(0, 240)) {
    const p = P[k];
    for (const o of [out[0], (out[0] + out[1]) / 2, out[1]]) {
      const c = [p.x + p.nx * o, p.z + p.nz * o];
      if (taken.some((t) => Math.hypot(t.c[0] - c[0], t.c[1] - c[1]) < t.a + a + 6)) continue;
      const L = makeLoop(c, a, b, Math.atan2(-p.nx, p.nz), R() * TAU, R() * TAU);
      let ok = true;
      for (let i = 0; i < L.pts.length - 1 && ok; i += 4) {
        const [x, z] = L.pts[i];
        if (!SEA.isOpenWater(x, z)) { ok = false; break; }
        const d = SEA.depth(x, z);
        if (d < d0 || d > d1) ok = false;
        else if (SEA.mouth && Math.hypot(x - SEA.mouth.x, z - SEA.mouth.z) < SEALIFE.mouth) ok = false;
        else for (const ln of SEA.lanes ?? []) for (let j = 1; j < ln.pts.length && ok; j++) if (segDist(x, z, ln.pts[j - 1], ln.pts[j]) < clear) ok = false;
      }
      if (ok) return L;
    }
  }
  return null;
}
// (2026-11-07) the CRABS' beaches: shore points of beach whose wet sand (inland[0]..inland[1] m up from the waterline,
// 8 m either way) is dry, low and free, away from the mouth and the port -- the best few, `apart` m apart
function crabBeaches(SEA, R, ground, blocked, harbour, C) {
  const P = SEA.shore?.pts ?? [], S = SEA.level, out = [];
  const okAt = (k) => {
    const p = P[k]; if (!p || p.type !== "beach") return false;
    for (const w of [C.inland[0], C.inland[1]]) {
      const x = p.x - p.nx * w, z = p.z - p.nz * w, g = ground ? ground(x, z) : S + .2;
      if (g < S + .02 || g > S + 1.5 || blocked(x, z)) return false;
    }
    return true;
  };
  const cand = [];
  for (let k = 3; k < P.length - 3; k++) {
    if (![-2, -1, 0, 1, 2].every((o) => okAt(k + o))) continue;
    const p = P[k];
    if (SEA.mouth && Math.hypot(p.x - SEA.mouth.x, p.z - SEA.mouth.z) < 40) continue;
    if (harbour && harbour.some(([hx, hz]) => Math.hypot(p.x - hx, p.z - hz) < C.harbour)) continue;
    cand.push([Math.hypot(p.x, p.z) / 120 + R() * 1.5, k]);   // (nearer the town rather)
  }
  cand.sort((p, q) => p[0] - q[0]);
  for (const [, k] of cand) {
    if (out.some((j) => Math.hypot(P[j].x - P[k].x, P[j].z - P[k].z) < C.apart)) continue;
    out.push(k); if (out.length >= C.groups) break;
  }
  return out;
}
const hash = (a, b) => { let h = (Math.imul(a | 0, 2654435761) ^ Math.imul(b | 0, 1597334677)) >>> 0; h = Math.imul(h ^ (h >>> 15), 2246822519) >>> 0; return ((h ^ (h >>> 13)) >>> 0) / 4294967296; };

export function createSeaLife(scene, { SEA, ring = () => {}, seed = 1, ground = null, blocked = () => false, harbour = null, climate = null } = {}) {
  if (!SEA || (SEA.kind !== "sea" && SEA.kind !== "lake")) return null;
  const R = rng((seed >>> 0) * 2654435761 + 0x5eaf), S = SEA.level, list = [], taken = [], api0 = {};
  const herd = createComposite(160);
  scene.add(herd.mesh);
  const blows = createPuffs(scene, SEALIFE.blow), puffs = createPuffs(scene, SEALIFE.puff);
  const sea = SEA.kind === "sea";
  if (sea) {
    // the whales: the deep water for the fluke-up dive if there is any in reach, else the shallower dive only
    const H = SEALIFE.humpback;
    for (let i = 0; i < H.n; i++) {
      let L = findLoop(SEA, R, H.axes, H.need[0], 12, H.clear, taken), deep = true;
      if (!L) { L = findLoop(SEA, R, H.axes, H.need[1], 12, H.clear, taken); deep = false; }
      if (!L) break;
      taken.push(L);
      list.push({ name: "humpback", an: herd.add(makeHumpback()), loop: L, deep, off: R() * H.period + i * 47, d0: R() * L.len });
    }
    const O = SEALIFE.orca, L = findLoop(SEA, R, O.axes, O.need, 14, O.clear, taken);
    if (L) {
      taken.push(L);
      const off = R() * O.period, d0 = R() * L.len;
      O.pod.forEach((p, k) => list.push({ name: "orca", an: herd.add(makeOrca()), loop: L, off: off - k * .9, d0, pod: p, k }));
    }
    // (2026-11-07) the MANTAS offshore, the STINGRAYS in the shallows, the CRABS on the beaches
    const M = SEALIFE.manta, mdef = variantDef("ray", M.variant);
    if (mdef) for (let i = 0; i < M.n; i++) {
      const L = findLoop(SEA, R, M.axes, M.need, 6, M.clear, taken);
      if (!L) break;
      taken.push(L);
      list.push({ name: "manta", an: herd.add(mdef), loop: L, off: R() * M.period + i * 29, d0: R() * L.len });
    }
    const SR = SEALIFE.stingray;
    for (let i = 0; i < SR.n; i++) {
      const L = findShallow(SEA, R, SR.axes, SR.depth, SR.out, SR.clear, taken);
      if (!L) break;
      taken.push(L);
      list.push({ name: "stingray", an: herd.add(coatDef("ray", (seed >>> 0) + i)), loop: L, d0: R() * L.len });
    }
    const C = SEALIFE.crab, P = SEA.shore?.pts ?? [];
    crabBeaches(SEA, R, ground, blocked, harbour, C).forEach((k, g) => {
      const n = C.size[0] + Math.floor(R() * (C.size[1] - C.size[0] + 1));
      for (let j = 0; j < n; j++) {
        const coat = C.coats[(j + g + (seed >>> 0)) % C.coats.length];
        list.push({ name: "crab", an: herd.add(coatDef("crab", coat)), home: k, s0: (j - (n - 1) / 2) * 2.6 + (R() - .5), ph: R() * TAU, off: R() * C.period,
                    seed: g * 131 + j * 17 + 3, coat, reach: coat ? C.reach * .6 : C.reach });   // (a shore crab, a third the size: shorter walks)
      }
    });
    // (where along the shore, s metres from point k, w metres up the beach: x, z and the normal into the water)
    api0.shoreAt = (k, s, w) => {
      const f = k + s / 4, i = Math.max(0, Math.min(P.length - 2, Math.floor(f))), u = Math.max(0, Math.min(1, f - i)), p = P[i], q = P[i + 1];
      const nx = lerp(p.nx, q.nx, u), nz = lerp(p.nz, q.nz, u), x = lerp(p.x, q.x, u), z = lerp(p.z, q.z, u);
      return [x - nx * w, z - nz * w, nx, nz];
    };
  }
  {
    const P = SEALIFE.plesio, ax = P.axes[sea ? 1 : 0];
    let L = findLoop(SEA, R, ax, P.need, 4, P.clear, taken, sea ? [0, 0] : SEA.center ?? [0, 0]);
    if (!L) L = findLoop(SEA, R, ax.map((v) => v * .7), P.need, 3, sea ? P.clear : 0, taken, sea ? [0, 0] : SEA.center ?? [0, 0]);   // (a small lake: a smaller loop, under the boats' round if it must)
    if (!L && !sea) L = findLoop(SEA, R, ax.map((v) => v * .55), 3.8, 3, 0, taken, SEA.center ?? [0, 0]);   // (a shallow lake: smaller still, 3.8 m deep is enough -- its lowest flipper tip ~3.3 m down)
    if (L) { taken.push(L); list.push({ name: "plesiosaurus", an: herd.add(makePlesiosaurus()), loop: L, off: R() * P.period, d0: R() * L.len }); }
  }
  // (2026-11-07) the NARWHALS: a pod where the sea is cold, now and then a pair where it is temperate -- last, and on a
  // random stream of their own, so the others' loops are what they were
  if (sea) {
    const N = SEALIFE.narwhal, RN = rng((seed >>> 0) * 2246822519 + 0x6e61), kind = N.climate[climate ?? "grown"] ?? null;
    const who = kind === "cold" ? N.pod : kind === "temperate" && RN() < N.stray ? N.pair : null;
    const L = who && findLoop(SEA, RN, N.axes, N.need, 8, N.clear, taken);
    if (L) {
      taken.push(L);
      const off = RN() * N.period, d0 = RN() * L.len;
      who.forEach(([a, b, w], k) => list.push({ name: "narwhal", an: herd.add(w === "male" ? makeNarwhal() : variantDef("narwhal", w) ?? makeNarwhal()), loop: L,
                                                  off: off - k * .7, d0, pod: [a, b], k, who: w }));
    }
  }
  for (const s of list) { s.an.rotY = 0; s.an.animT = 0; }
  const speedOf = (s) => SEALIFE[s.name === "plesiosaurus" ? "plesio" : s.name].speed;

  // ---- the cycles: T -> the root's height under the surface (m, negative), the pitch, and the moments things happen ----
  // HUMPBACK. tau in [0, 110): 0-55 cruising 9 m down; 55-65 rising; 65-92 at the surface, a breath at 67, 76 and 85
  // (at each the root rising to 0.9 m under and the nose tipping up 0.2, so only the head's top with its blowholes and a
  // little of the back break the water; sinking to 1.75 between, all of it under); 92-110 diving -- every third FLUKES-UP
  const HB = [67, 76, 85];
  function humpback(s, T) {
    const P = SEALIFE.humpback.period, u = T + s.off, tau = ((u % P) + P) % P, cyc = Math.floor(u / P);
    const fluke = s.deep && ((cyc % 3) + 3) % 3 === 1;
    let y = -9 + .8 * Math.sin(T * .09 + s.off), pitch = 0;
    if (tau >= 55 && tau < 65) y = lerp(y, -1.2, ss(55, 65, tau));
    else if (tau >= 65 && tau < 92) {
      let up = 0;
      for (const b of HB) up += Math.exp(-(((tau - b) / 2.6) ** 2));
      y = -1.75 + .87 * up; pitch = .2 * up;
      if (tau < 67) y = lerp(-1.2, y, ss(65, 67, tau));
    } else if (tau >= 92) {
      const k = tau - 92;
      if (fluke) {   // arch, tip over, the flukes up and in, level out
        pitch = -.35 * ss(0, 3, k) - .8 * ss(3, 7, k) + 1.15 * ss(11, 18, k);
        y = lerp(-1.75 - .6 * ss(0, 3, k) - 4.6 * ss(3, 7, k) - 7.2 * ss(7, 11, k), y, ss(11, 18, k));
      } else {
        y = lerp(-1.75, y, ss(0, 12, k));
      }
    }
    return { y, pitch, tau, fluke };
  }
  // ORCA. tau in [0, 60): 0-30 cruising 4 m down; 30-34 up to 2.5 m; three arcs cresting at 37, 44, 51 (the root 0.35 m
  // under: the back awash, the fin 1.8 m out); 53-60 down again
  const OB = [37, 44, 51];
  function orca(s, T) {
    const P = SEALIFE.orca.period, tau = (((T + s.off) % P) + P) % P;
    let y = -4 + .3 * Math.sin(T * .2 + s.k);
    if (tau >= 30 && tau < 53) {
      y = lerp(y, -2.5, ss(30, 34, tau));
      for (const b of OB) y += 2.15 * Math.exp(-(((tau - b) / 1.5) ** 2));
    } else if (tau >= 53) y = lerp(-2.5, y, ss(53, 60, tau));
    return { y, tau };
  }
  // (2026-11-07) NARWHAL. tau in [0, 52): 0-32 cruising 3.5 m down; 32-36 up to 1.6 m; two slow arcs cresting at 39 and
  // 45 (the root 0.3 m under: the back awash, the tusk's point lifting clear as the head comes up); 47-52 down again
  const NB = [39, 45];
  function narwhal(s, T) {
    const P = SEALIFE.narwhal.period, tau = (((T + s.off) % P) + P) % P;
    const up = ss(32, 36, tau) * (1 - ss(47, 52, tau));
    let y = lerp(-3.5 + .3 * Math.sin(T * .17 + s.k), -1.6, up);
    for (const b of NB) y += 1.3 * Math.exp(-(((tau - b) / 1.6) ** 2));
    return { y, tau };
  }
  // PLESIOSAUR. tau in [0, 75): 0-55 cruising 2.6 m down; 55-61 rising head-up (pitched 0.62) until the head and the
  // top of the neck are out; held to 68 looking about; 68-75 sinking back level
  function plesio(s, T) {
    const P = SEALIFE.plesio.period, tau = (((T + s.off) % P) + P) % P;
    let y = -2.6 + .25 * Math.sin(T * .3 + s.off), pitch = 0;
    const up = ss(55, 61, tau) * (1 - ss(68, 75, tau));
    y = lerp(y, -.6, up); pitch = .62 * up;
    return { y, pitch, tau, up };
  }

  // (2026-11-07) MANTA. tau in [0, 70): 0-40 gliding 3.5 m down; 40-47 up to 1 m under (its back plain from above; no
  // shallower: the asset's wing wave lifts a tip ~0.7 m, and a black tip out of the water reads as a shark's fin);
  // cruising there to 60; 60-70 down again
  function manta(s, T) {
    const P = SEALIFE.manta.period, tau = (((T + s.off) % P) + P) % P;
    const deep = -3.5 + .5 * Math.sin(T * .11 + s.off);
    const y = lerp(deep, -1 + .06 * Math.sin(T * .7), ss(40, 47, tau) * (1 - ss(60, 70, tau)));
    return { y, tau };
  }
  // (2026-11-07) CRAB. Its cycle: walking sideways for `walk` s to the next spot (along the shore, s m either way of its
  // own; w m up the beach), then still to the cycle's end. Where it is: i the cycle, the spots j a smooth wander
  function crab(s, T) {
    const C = SEALIFE.crab, u = T + s.off, i = Math.floor(u / C.period), tau = u - i * C.period;
    const spot = (j) => [s.s0 + s.reach * Math.sin(j * .83 + s.ph), C.inland[0] + (C.inland[1] - C.inland[0]) * hash(s.seed, j)];
    const a = spot(i - 1), b = spot(i), k = ss(0, C.walk, tau);
    return { s: lerp(a[0], b[0], k), w: lerp(a[1], b[1], k), walked: i * C.walk + Math.min(tau, C.walk) };
  }

  let lastT = null;
  const fire = (s, key, at, tau, T, fn) => {   // (an event at tau = at in this cycle, once, as T passes it)
    if (lastT === null || T - lastT > 3) return;
    const dt = T - lastT, was = tau - dt;
    if (was < at && tau >= at) fn();
  };
  const pt = (s, fwd, up) => {   // (a point on the body: fwd metres ahead of the root, up above it, as tipped)
    const a = s.an, cp = Math.cos(a.pitch ?? 0), sp = Math.sin(a.pitch ?? 0), h = a.rotY;
    const f = fwd * cp - up * sp, y = fwd * sp + up * cp;
    return [a.position.x + f * Math.cos(h), a.position.y + y, a.position.z - f * Math.sin(h)];
  };
  const spout = (x, z, t, big, hd) => {
    // (a whale's: a BUSHY spout shot ~4 m up in half a second, narrow at the blowholes and opening like a V into a
    //  balloon at the top, then hanging, drifting downwind and fading over ~3 s; an orca's: the same, small -- 1.3 m)
    const P = big ? blows : puffs, n = big ? 56 : 16, top = big ? 4.2 : 1.3, w = big ? 1.0 : .3;
    const wx = Math.cos(hd) * .35, wz = -Math.sin(hd) * .35;
    for (let i = 0; i < n; i++) {
      const k = (i + .5) / n, r = w * (.1 + .9 * k ** 1.5) * (.6 + .4 * Math.sin(i * 1.7) ** 2), a = i * 2.4;
      const o = .25 + 1.5 * k ** 1.5, h = top * Math.min(1, k ** .8 + .06 * Math.sin(i * 3.1));
      P.puff(x + Math.cos(a) * r, S + .15 + h, z + Math.sin(a) * r, wx + Math.cos(a) * o * w, wz + Math.sin(a) * o * w, t + k * (big ? .5 : .35));
    }
  };

  const api = {
    herd, list,
    callers: list.filter((s) => s.name === "humpback" || s.name === "orca").map((s) => ({ name: s.name, p: s.an.position, an: s.an, pitch: .92 + ((s.k ?? 0) * .07) })),
    shift: 0, T: 0, hold: null,   // (debug: seconds added to the clock -- to look at a blow without waiting for one; hold: a clock to stop at, for a still)
    blows: 0, flukes: 0, heads: 0,
    update(T0, t) {
      const T = api.hold ?? T0 + api.shift;
      for (const s of list) {
        if (s.name === "crab") {   // (2026-11-07: sideways along the wet sand, facing the water)
          const a = s.an, c = crab(s, T), [x, z, nx, nz] = api0.shoreAt(s.home, c.s, c.w);
          a.position.set(x, ground ? ground(x, z) : S + .1, z);
          a.rotY = Math.atan2(nx, nz);
          a.animT = c.walked;
          continue;
        }
        const a = s.an, sp = speedOf(s);
        let d = s.d0 + T * sp, lat = 0;
        if (s.pod) { d += s.pod[0]; lat = s.pod[1]; }
        const [x, z, h] = s.loop.at(d);
        const [x2, z2] = s.loop.at(d + 1);
        const nx = -(z2 - z), nz = x2 - x, nl = Math.hypot(nx, nz) || 1;
        a.position.x = x + nx / nl * lat; a.position.z = z + nz / nl * lat;
        a.rotY = h;
        if (s.name === "humpback") {
          const c = humpback(s, T), c2 = humpback(s, T + .5);
          a.position.y = S + c.y;
          // (nose up as it rises, down as it sinks -- as steep as its path -- plus a breath's own nose-up and the dive's
          //  own tipping)
          a.pitch = c.fluke && c.tau >= 92 ? c.pitch : Math.max(-.35, Math.min(.35, Math.atan2(c2.y - c.y, sp * .5) * .8 + c.pitch));   // (diving flukes-up: its own tipping)
          a.animT = T * .9;
          for (const b of HB) fire(s, "blow", b, c.tau, T, () => { const p = pt(s, 2.5, .45); spout(p[0], p[2], t, true, h); ring(p[0], S, p[2], 1.2); api.blows++; });
          if (c.fluke) fire(s, "fluke", 100, c.tau, T, () => { const p = pt(s, -8.5, 0); ring(p[0], S, p[2], 1.4); api.flukes++; });
        } else if (s.name === "orca") {
          const c = orca(s, T), c2 = orca(s, T + .3);
          a.position.y = S + c.y;
          a.pitch = Math.max(-.45, Math.min(.45, Math.atan2(c2.y - c.y, sp * .3)));
          a.animT = T * 1.1 + s.k * .37;
          for (const b of OB) fire(s, "breath", b, c.tau, T, () => { const p = pt(s, 1.65, .5); spout(p[0], p[2], t, false, h); ring(p[0], S, p[2], .7); api.blows++; });
        } else if (s.name === "narwhal") {
          const c = narwhal(s, T), c2 = narwhal(s, T + .4);
          a.position.y = S + c.y;
          a.pitch = Math.max(-.4, Math.min(.4, Math.atan2(c2.y - c.y, sp * .4)));
          a.animT = T * 1.0 + s.k * .41;
          for (const b of NB) fire(s, "breath", b, c.tau, T, () => { const p = pt(s, s.who === "calf" ? .45 : 1.3, .3); spout(p[0], p[2], t, false, h); ring(p[0], S, p[2], .5); api.blows++; });
        } else if (s.name === "manta") {
          const c = manta(s, T), c2 = manta(s, T + .6), [, , h2] = s.loop.at(d + 4);
          a.position.y = S + c.y;
          a.pitch = Math.max(-.3, Math.min(.3, Math.atan2(c2.y - c.y, sp * .6)));
          let dh = h2 - h; dh = ((dh + Math.PI) % TAU + TAU) % TAU - Math.PI;
          const rl = Math.max(.06, Math.min(.32, (-c.y - .75) * .5));   // (less bank near the top: the 1.6 m half-span's tip, on
          a.roll = Math.max(-rl, Math.min(rl, -dh * 1.6));              //  its upbeat, kept under the water)
          a.animT = T * .55;   // (the wings' slow beat)
        } else if (s.name === "stingray") {
          const dep = SEA.depth(x, z), [x2, z2] = s.loop.at(d + 1), dep2 = SEA.depth(x2, z2);
          a.position.y = S - dep + .14;   // (a hand's breadth over the sand)
          a.pitch = Math.max(-.2, Math.min(.2, Math.atan2(dep - dep2, 1)));
          a.animT = T * .8;
        } else {
          const c = plesio(s, T);
          a.position.y = S + c.y;
          a.pitch = c.pitch;
          a.animT = T;
          fire(s, "head", 60, c.tau, T, () => { const p = pt(s, 1.6, 0); ring(p[0], S, p[2], .5); api.heads++; });
          fire(s, "sink", 70, c.tau, T, () => { const p = pt(s, 1.6, 0); ring(p[0], S, p[2], .4); });
        }
      }
      lastT = T; api.T = T;   // (api.T: the clock it last swam to, shift included -- for a probe)
      herd.update(t);
      blows.update(t); puffs.update(t);
    },
    // (debug: where one is and how it is doing at clock T)
    peek(i, T) { const s = list[i]; return s && (s.loop ? { name: s.name, at: s.loop.at(s.d0 + T * speedOf(s)), loop: [s.loop.c, s.loop.a, s.loop.b] } : { name: s.name, at: api0.shoreAt(s.home, crab(s, T).s, crab(s, T).w) }); },
  };
  const crabs = list.filter((s) => s.name === "crab");
  console.log(`sealife: ${list.filter((s) => s.name !== "crab").map((s) => s.name).join(", ") || "none"}${crabs.length ? `, ${crabs.length} crabs (${crabs.map((s) => ["edible", "green", "red-orange"][s.coat]).join(", ")})` : ""} (${SEA.kind})` + list.filter((s) => !s.k && s.loop).map((s) => ` -- ${s.name} round ${s.loop.c.map(Math.round)}${s.deep === false ? " (no fluke-up: shallower)" : ""}`).join("")
              + [...new Set(crabs.map((s) => s.home))].map((k) => ` -- crabs on the beach at ${Math.round(SEA.shore.pts[k].x)}, ${Math.round(SEA.shore.pts[k].z)}`).join(""));
  return api;
}
