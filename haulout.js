// THE SHORE'S SEALS AND WALRUSES (2026-11-06): HAUL-OUTS. A world with open water (sea.js SEA) gets groups of HARBOUR
// SEALS (and now and then a group of GREY SEALS) lying out on its shore -- two groups of 4-7 on a sea's beaches and low
// rocks, one of 3-4 on a big lake's (a freshwater colony, as in Lake Iliamna or Saimaa); and on a sea's rocky stretch,
// where it is cold enough, a small herd of WALRUSES (an "alpine" climate, the coldest the landscape worlds have: 3-5),
// or now and then one lone vagrant where it is temperate (as the walruses that have wandered down to Ireland, Wales,
// the Netherlands and Spain); none in a warm one. Their bodies are the sculpted assets/creatures/sea/{seal,walrus}.json
// (species.js makeSeal, makeWalrus), in a composite herd of their own.
//
// WHERE: a stretch of beach or low rock (sea.js SEA.shore: its points' type; never a cliff or the river's mouth) whose
// strip inland is dry, gentle (no step over ~0.45 m a metre), free (the town's sites, the port and its quays, trees,
// props and paths: `blocked`), with water off it deep enough to swim in, kept HAULOUT.harbour m from the port and
// HAULOUT.apart m from the other groups. Each animal has its SPOT a few metres up the shore, lying facing the water
// (a seal hauls out so it can slip off at once), along the shore a body's length or two from the next.
//
// WHEN: a pure function of the shared clock T (like sealife.js: every peer sees the same seal slide in at the same
// moment, nothing is simulated). Each animal has a cycle of its own (HAULOUT period, 3.5-5.5 min a seal's); in some
// cycles (`goes`: drawn per cycle) it GALUMPHS down to the water (a seal humps along on its belly -- its hind flippers
// cannot turn under it; a walrus walks on its four flippers, the hind ones turned forward under the pelvis), SWIMS a
// loop out from the shore (a seal's hind flippers sweeping side to side; a dive or two), BOTTLES at the far end --
// floats upright with its head out, looking about -- swims back, and HAULS OUT to its spot again, turning there to face
// the water. The rest of the time it lies: the head up, looking about, a seal now and then in the "banana" (the head
// and the hind flippers raised together). The poses are an.pose per bone (skeleton.js writeAnimal's held rotations).
//
//   const h = createHaulout(scene, { SEA, ground, blocked, harbour, climate, seed, ring, force })   // null: no open water
//   h.update(T, t)   // T the shared sim clock (where, when), t the render clock (posing)
//   h.list           // [{ name, an, spot, ... }]; h.groups; h.callers (calls.js: seals bark and moan, a walrus bellows)
import * as THREE from "three";
import { createComposite } from "./composite.js";
import { sculptOf } from "./bodyspec.js";
import { makeSeal, makeWalrus } from "./species.js";

export const HAULOUT = {
  // groups (a sea's, a lake's) and their sizes; spacing m along the shore; inland: the spots' range up from the
  // waterline, m; period: of the cycle, s; goes: the share of cycles it goes in; land / swim: speeds, m/s; out: the
  // swim loop's reach from the shore, m; belly: the body's axis over the ground lying (at scale 1), float: under the
  // surface swimming; bottle: how long it floats upright, s; hump: galumphs (steps) a second; len: its body, m
  seal: { groups: { sea: 2, lake: 1 }, size: { sea: [4, 7], lake: [3, 4] }, spacing: 2.4, inland: [2, 5], types: ["beach", "rocky"],
          period: [210, 330], goes: .5, land: .45, swim: 1.15, out: [12, 26], belly: .2, float: .2, bottle: [7, 14], hump: 1.5, len: .9,
          grey: .3 },   // (grey: the share of groups that are grey seals)
  walrus: { size: { cold: [3, 5], temperate: [1, 1] }, vagrant: .35, spacing: 3.8, inland: [2.5, 5.5], types: ["rocky", "beach"],
            period: [300, 460], goes: .4, land: .24, swim: .8, out: [12, 22], belly: .5, float: .36, bottle: [12, 24], hump: .75, len: 1.6 },
  apart: 70,      // m between two groups
  harbour: 70,    // m kept from the port
  climate: { alpine: "cold", temperate: "temperate", grown: "temperate" },   // (arid, tropical, mediterranean: no walrus)
};

const TAU = Math.PI * 2;
const ss = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
const rng = (seed) => { let s = (seed >>> 0) || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; };
const hash = (a, b) => { let h = (Math.imul(a | 0, 2654435761) ^ Math.imul(b | 0, 1597334677)) >>> 0; h = Math.imul(h ^ (h >>> 15), 2246822519) >>> 0; return ((h ^ (h >>> 13)) >>> 0) / 4294967296; };
const angTo = (a, b) => { let d = (b - a) % TAU; if (d > Math.PI) d -= TAU; if (d < -Math.PI) d += TAU; return d; };
const headingOf = (dx, dz) => Math.atan2(-dz, dx);   // (rotY that turns the body's +x along (dx, dz): sealife.js's)

// a closed smooth path through points (Catmull-Rom), sampled by arc length: at(d) -> [x, z, heading]
function smoothLoop(P) {
  const n = P.length, S = [];
  for (let i = 0; i < n; i++) {
    const p0 = P[(i - 1 + n) % n], p1 = P[i], p2 = P[(i + 1) % n], p3 = P[(i + 2) % n];
    for (let k = 0; k < 24; k++) {
      const t = k / 24, t2 = t * t, t3 = t2 * t;
      const f = (a, b, c, d) => .5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
      S.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])]);
    }
  }
  S.push(S[0]);
  const L = [0];
  for (let i = 1; i < S.length; i++) L.push(L[i - 1] + Math.hypot(S[i][0] - S[i - 1][0], S[i][1] - S[i - 1][1]));
  const len = L[L.length - 1];
  const at = (d) => {
    d = Math.max(0, Math.min(len, d));
    let lo = 0, hi = S.length - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (L[m] <= d) lo = m; else hi = m; }
    const k = (d - L[lo]) / (L[hi] - L[lo] || 1), p = S[lo], q = S[hi];
    return [p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k, headingOf(q[0] - p[0], q[1] - p[1])];
  };
  return { len, at, pts: S };
}

export function createHaulout(scene, { SEA, ground, blocked = () => false, harbour = null, climate = null, seed = 1, ring = () => {}, force = null } = {}) {
  if (!SEA || (SEA.kind !== "sea" && SEA.kind !== "lake") || !SEA.shore?.pts?.length) return null;
  const R = rng((seed >>> 0) * 2246822519 + 0x5ea1), S = SEA.level, sea = SEA.kind === "sea", P = SEA.shore.pts;
  const list = [], groups = [];

  // ---- WHERE: the stretches that will do, best first ----
  // the strip inland of a shore point: dry from `inland[0]` m up, no step over .45 m a metre, nothing in the way;
  // its steepest step, or null
  const strip = (q, sp) => {
    let prev = ground(q.x, q.z), mx = 0;
    for (let d = 1; d <= sp.inland[1] + 1.5; d += 1) {
      const x = q.x - q.nx * d, z = q.z - q.nz * d, y = ground(x, z);
      if (blocked(x, z)) return null;
      mx = Math.max(mx, Math.abs(y - prev)); prev = y;
      if (d >= sp.inland[0] && (y < S + .08 || SEA.depth(x, z) > 0)) return null;
    }
    return mx > .45 ? null : mx;
  };
  const why = { type: 0, strip: 0, deep: 0, open: 0, port: 0, mouth: 0, ok: 0, noswim: 0 };   // (why stretches failed: the console's line when none will do)
  const sites = (sp) => {
    const out = [];
    for (let k = 3; k < P.length - 3; k += 2) {
      const p = P[k];
      if (!sp.types.includes(p.type)) { why.type++; continue; }
      let worst = 0, ok = true;
      for (let j = k - 3; j <= k + 3 && ok; j++) {
        const q = P[j];
        if (!q || q.type === "mouth" || q.type === "cliff") { ok = false; break; }
        const r = strip(q, sp); if (r === null) ok = false; else worst = Math.max(worst, r);
      }
      if (!ok) { why.strip++; continue; }
      if (SEA.depth(p.x + p.nx * 8, p.z + p.nz * 8) < .8 || SEA.depth(p.x + p.nx * 18, p.z + p.nz * 18) < 1.6) { why.deep++; continue; }
      if (!SEA.isOpenWater(p.x + p.nx * 12, p.z + p.nz * 12)) { why.open++; continue; }
      if (harbour && harbour.some(([hx, hz]) => Math.hypot(p.x - hx, p.z - hz) < HAULOUT.harbour)) { why.port++; continue; }
      if (SEA.mouth && Math.hypot(p.x - SEA.mouth.x, p.z - SEA.mouth.z) < 60) { why.mouth++; continue; }
      why.ok++;
      // (preferred: its kind of shore, gentle, well away from the town's middle)
      out.push({ k, score: sp.types.indexOf(p.type) * 1.2 + worst * 3 - Math.min(1.5, Math.hypot(p.x, p.z) / 200) + R() * 1.5 });
    }
    return out.sort((a, b) => a.score - b.score);
  };
  const free = (k) => groups.every((g) => Math.hypot(P[k].x - g.x, P[k].z - g.z) > HAULOUT.apart);

  // a point along the shore `a` m from point k (interpolated), with its normal
  const along = (k, a) => {
    let j = k, rest = a;
    const step = a >= 0 ? 1 : -1;
    while (P[j + step] && Math.abs(rest) > Math.hypot(P[j + step].x - P[j].x, P[j + step].z - P[j].z)) { rest -= step * Math.hypot(P[j + step].x - P[j].x, P[j + step].z - P[j].z); j += step; }
    const q = P[j + step] ?? P[j], seg = Math.hypot(q.x - P[j].x, q.z - P[j].z) || 1, f = Math.min(1, Math.abs(rest) / seg);
    const nx = lerp(P[j].nx, q.nx, f), nz = lerp(P[j].nz, q.nz, f), nl = Math.hypot(nx, nz) || 1;
    return { x: lerp(P[j].x, q.x, f), z: lerp(P[j].z, q.z, f), nx: nx / nl, nz: nz / nl };
  };

  // ---- ONE ANIMAL: its spot, its way down to the water, its swim ----
  function place(name, sp, def, k, a, gi, idx) {
    const sc = (def.parts.find((p) => p.id === "neck")?.pos?.[0] ?? 0) / (name === "seal" ? .4 : .82) || 1;   // (a coat's `scale`: the grey seal bull's 1.25)
    const q = along(k, a), d = lerp(sp.inland[0], sp.inland[1], R());
    let sx = q.x - q.nx * d + (R() - .5) * .6, sz = q.z - q.nz * d + (R() - .5) * .6;
    if (blocked(sx, sz) || list.some((o) => Math.hypot(o.spot[0] - sx, o.spot[1] - sz) < sp.len * 1.3 * sc)) return null;
    // (facing the water, give or take)
    const rest = headingOf(q.nx, q.nz) + (R() - .5) * 1.6;
    // the way down: straight out along the normal to where it floats (`afloat`), the water's edge on the way (`edge`)
    let ex = sx, ez = sz, edge = null, afloat = null;
    for (let s = .4; s < 40; s += .4) {
      const x = sx + q.nx * s, z = sz + q.nz * s, dep = SEA.depth(x, z);
      if (!edge && dep > .05) edge = [x, z, s];
      if (dep > sp.belly * 2.4 * sc + .1) { afloat = [x, z, s]; break; }
      ex = x; ez = z;
    }
    const s = { name, def, sp, sc, an: null, spot: [sx, sz], rest, n: [q.nx, q.nz], edge, afloat, group: gi, idx,
                period: lerp(sp.period[0], sp.period[1], R()), off: R() * 1000, swim: null, look: R() * TAU, banana: R() < .5 };
    // the swim: a loop out from where it floats and back, through two points out over deeper water; the farthest
    // reach that keeps it in open water 1 m deep or more (bar its first and last metres) -- or none, and it stays out
    if (afloat) {
      const tx = -q.nz, tz = q.nx, side0 = R() < .5 ? 1 : -1, o0 = lerp(sp.out[0], sp.out[1], R());
      // (out as far as it may, either way round: the first that fits)
      for (const [f, side] of [1, .8, .62, .45, .32].flatMap((f) => [[f, side0], [f, -side0]])) {
        const o = o0 * f;
        const A = [afloat[0] + q.nx * o + tx * side * o * .45, afloat[1] + q.nz * o + tz * side * o * .45];
        const B = [afloat[0] + q.nx * o * .7 - tx * side * o * .4, afloat[1] + q.nz * o * .7 - tz * side * o * .4];
        const L = smoothLoop([[afloat[0], afloat[1]], A, B]);
        let ok = true;
        for (let i = 0; i < L.pts.length && ok; i += 3) {
          const [x, z] = L.pts[i];
          const dE = Math.hypot(x - afloat[0], z - afloat[1]);
          if (dE < 2.5) continue;
          if (!SEA.isOpenWater(x, z) || SEA.depth(x, z) < Math.min(1.1, .7 + dE * .07)) ok = false;
        }
        if (ok) { s.swim = L; break; }
      }
    }
    return s;
  }

  // the walruses (first: the rarer, so they get the best rock): where it is cold a small herd, where it is temperate now
  // and then a lone vagrant; a sea only; the seal groups then keep HAULOUT.apart from them as from each other
  const W = HAULOUT.walrus, cold = HAULOUT.climate[climate ?? "grown"] ?? null;
  const wn = force ? Math.max(1, +force || 1) : !sea || !cold ? 0 : cold === "cold" ? W.size.cold[0] + Math.floor(R() * (W.size.cold[1] - W.size.cold[0] + 1)) : R() < W.vagrant ? 1 : 0;
  if (wn) {
    for (const c of sites(W).filter((c) => free(c.k))) {
      const p = P[c.k], gi = groups.length;
      groups.push({ name: wn > 1 ? "walruses" : "a walrus", x: p.x, z: p.z, k: c.k, type: p.type, n: 0 });
      for (let i = 0; i < wn * 2 && groups[gi].n < wn; i++) {
        const a = (groups[gi].n - (wn - 1) / 2) * W.spacing + (R() - .5) * 1.5;
        const s = place("walrus", W, makeWalrus(), c.k, a, gi, groups[gi].n);
        if (s) { list.push(s); groups[gi].n++; }
      }
      if (list.some((s) => s.group === gi && s.swim)) break;
      list.splice(list.length - groups[gi].n); groups.pop();
    }
  }
  const shoreKind = sea ? "sea" : "lake";
  const gsp = HAULOUT.seal;
  {
    const cand = sites(gsp);
    const tried = new Set();
    for (let g = 0; g < gsp.groups[shoreKind];) {
      const c = cand.find((c) => !tried.has(c.k) && free(c.k));
      if (!c) break;
      tried.add(c.k);
      const p = P[c.k], grey = sea && R() < gsp.grey, n = gsp.size[shoreKind][0] + Math.floor(R() * (gsp.size[shoreKind][1] - gsp.size[shoreKind][0] + 1));
      const gi = groups.length;
      groups.push({ name: grey ? "grey seals" : "harbour seals", x: p.x, z: p.z, k: c.k, type: p.type, n: 0 });
      for (let i = 0; i < n * 2 && groups[gi].n < n; i++) {
        const a = (groups[gi].n - (n - 1) / 2) * gsp.spacing + (R() - .5) * 1.2 + (i >= n ? (R() - .5) * 4 : 0);
        // (the coats: harbour seals silver grey, dark or brown -- 0..3; a grey seal colony bulls and cows -- 4, 5)
        const coat = grey ? 4 + (R() < .35 ? 0 : 1) : Math.floor(R() * 4);
        const def = makeSeal({ coat });
        const s = place("seal", gsp, def, c.k, a, gi, groups[gi].n);
        if (s) { list.push(s); groups[gi].n++; }
      }
      // (a shore none of them could swim off -- the water too shallow or shut in: not this one, the next)
      if (!list.some((s) => s.group === gi && s.swim)) { why.noswim++; list.splice(list.length - groups[gi].n); groups.pop(); continue; }
      g++;
    }
  }
  if (!list.length) { console.log(`haulout: none (${SEA.kind}, ${climate ?? "river country"}) -- stretches: ${JSON.stringify(why)}`); return null; }

  const herd = createComposite(list.length + 2);
  scene.add(herd.mesh);
  const BONES = ["neck", "head", "hips", "tail", "hflipL", "hflipR", "fflipL", "fflipR"];
  for (const s of list) {
    s.an = herd.add(s.def);
    s.an.rotY = s.rest; s.an.animT = 0; s.an.amp = 0;
    const ids = sculptOf(s.def).parts.map((p) => p.id);
    s.an.pose = s.an.parts.map(() => null);
    s.bone = {};
    for (const b of BONES) { const i = ids.indexOf(b); if (i >= 0) { s.bone[b] = { q: new THREE.Quaternion(), c: null }; s.an.pose[i] = s.bone[b]; } }
  }

  // ---- WHEN: T -> what it is doing (pure) ----
  // a cycle: lying until t0; down to the water (galumphing, `dn` s); the swim loop (`sw` s, the bottle in its middle);
  // back up (`dn` s); lying to the cycle's end, turning at first to face the water again
  function plan(s, T) {
    const sp = s.sp, u = T + s.off, c = Math.floor(u / s.period), tau = u - c * s.period;
    const goes = s.swim && s.afloat && hash(s.idx * 31 + s.group * 977 + 7, c) < sp.goes;
    if (!goes) return { st: "rest", tau, c, k: 0 };
    const dn = s.afloat[2] / (sp.land * s.sc ** .5), bottle = lerp(sp.bottle[0], sp.bottle[1], hash(s.idx + 5, c));
    const sw = s.swim.len / sp.swim + bottle, t0 = s.period * (.12 + .3 * hash(s.idx + 11, c));
    const t1 = t0 + dn, t2 = t1 + sw, t3 = t2 + dn;
    if (t3 > s.period - 12) return { st: "rest", tau, c, k: 0 };
    if (tau < t0) return { st: "rest", tau, c, k: 0 };
    if (tau < t1) return { st: "down", tau, c, k: (tau - t0) / dn, t0, dn };
    if (tau < t2) {
      // (the swim: along the loop at its speed, held at its middle for the bottle)
      const e = tau - t1, half = s.swim.len / 2 / sp.swim;
      let d, b = 0;
      if (e < half) d = e * sp.swim;
      else if (e < half + bottle) { d = s.swim.len / 2; b = Math.min(1, (e - half) / 2.5, (half + bottle - e) / 2.5); }
      else d = (e - bottle) * sp.swim;
      return { st: "swim", tau, c, k: d / s.swim.len, d, b, e, sw, bottle, half };
    }
    if (tau < t3) return { st: "up", tau, c, k: (tau - t2) / dn, dn };
    return { st: "rest", tau, c, k: 0, since: tau - t3 };
  }

  // ---- THE POSES ----
  const _e = new THREE.Euler(), setB = (s, b, x, y, z) => { const h = s.bone[b]; if (h) h.q.setFromEuler(_e.set(x, y, z)); };
  const wobble = (s, t, f) => Math.sin(t * f + s.off) * .6 + Math.sin(t * f * 2.3 + s.off * 1.7) * .4;
  function poseRest(s, t, T) {
    // lying: the head up and turning slowly now and then; a seal in the banana now and then (the head and the hind
    // flippers raised together), a walrus's head now and then laid down on the ground
    const isSeal = s.name === "seal", ph = T * .05 + s.look;
    const look = .55 * Math.sin(ph) * ss(.2, .6, Math.abs(Math.sin(ph * .37))) + .12 * Math.sin(T * .31 + s.off);
    const ban = isSeal && s.banana ? ss(.55, .85, Math.sin(T * .021 + s.off * 3)) : 0;
    const doze = !isSeal ? ss(.4, .8, Math.sin(T * .017 + s.off * 2)) : 0;
    setB(s, "neck", 0, look * .5, (isSeal ? .3 : .12) + ban * .3 - doze * .32);
    setB(s, "head", 0, look * .5, (isSeal ? -.08 : -.04) + ban * .1 - doze * .1);
    setB(s, "hips", 0, 0, ban * .1);
    setB(s, "tail", 0, .05 * Math.sin(T * .2 + s.off), (isSeal ? .12 : .03) + ban * .38);
    setB(s, "hflipL", 0, 0, 0); setB(s, "hflipR", 0, 0, 0);
    setB(s, "fflipL", 0, 0, 0); setB(s, "fflipR", 0, 0, 0);
    return ban;
  }
  function poseLand(s, t, ph) {
    if (s.name === "seal") {
      // GALUMPHING: the back humped up as the hindquarters are drawn in, then the chest thrown forward, flat
      const a = .5 - .5 * Math.cos(ph);
      setB(s, "neck", 0, 0, .34 - .22 * a);
      setB(s, "head", 0, 0, -.1 + .06 * a);
      setB(s, "hips", 0, 0, -.42 * a);
      setB(s, "tail", 0, 0, .2 + .18 * a);
      setB(s, "hflipL", 0, 0, 0); setB(s, "hflipR", 0, 0, 0);
      setB(s, "fflipL", 0, .25 * Math.sin(ph), -.2 * a); setB(s, "fflipR", 0, -.25 * Math.sin(ph), -.2 * a);
      return { lift: .07 * a * s.sc, pitch: .12 * a - .04 };
    }
    // A WALRUS WALKS: its hind flippers turned forward under the pelvis, the fore flippers stepping in turn, the body
    // rolling from side to side over them
    const st = Math.sin(ph);
    setB(s, "neck", 0, .06 * st, .2);
    setB(s, "head", 0, 0, -.05);
    setB(s, "hips", 0, -.05 * st, -.06);
    setB(s, "tail", 0, 0, -.15);
    setB(s, "hflipL", -.9, .2, 2.0 + .15 * Math.max(0, st)); setB(s, "hflipR", .9, -.2, 2.0 + .15 * Math.max(0, -st));
    setB(s, "fflipL", 0, -.3 * Math.max(0, st), .25 * Math.max(0, st)); setB(s, "fflipR", 0, .3 * Math.max(0, -st), .25 * Math.max(0, -st));
    return { lift: .06 * Math.abs(st) * s.sc, pitch: .05, roll: .05 * st };
  }
  function poseSwim(s, t, b) {
    // SWIMMING: the hind flippers sweep side to side, the hips and tail a wave behind (a seal's ~1.2 a second, a
    // walrus's slower), the fore flippers pressed back to the flanks; BOTTLING (b): upright, the head bent level
    const isSeal = s.name === "seal", f = (isSeal ? 1.2 : .7) * TAU, w = 1 - b;
    setB(s, "neck", 0, .3 * b * Math.sin(t * .4 + s.off), .12 * w - .85 * b);
    setB(s, "head", 0, 0, -.05 * w - .55 * b);
    setB(s, "hips", 0, .16 * w * Math.sin(t * f), .1 * b);
    setB(s, "tail", 0, .34 * w * Math.sin(t * f - .9) + .08 * b * Math.sin(t * .8), .15 * b);
    setB(s, "hflipL", .15 * w * Math.sin(t * f - 1.6), 0, 0); setB(s, "hflipR", .15 * w * Math.sin(t * f - 1.6), 0, 0);
    if (isSeal) { setB(s, "fflipL", 0, .15 * b, .1 * w); setB(s, "fflipR", 0, -.15 * b, .1 * w); }
    else { setB(s, "fflipL", .2, -1.25 * w - .5 * b, -.5 * w); setB(s, "fflipR", -.2, 1.25 * w + .5 * b, -.5 * w); }   // (a walrus's, turned back along its sides)
  }

  // the body lying on the ground: its height there, tipped to the slope under it
  const lie = (s, x, z, h, out) => {
    const L = s.sp.len * s.sc * .6, c = Math.cos(h), n = Math.sin(h);
    const yF = ground(x + c * L, z - n * L), yB = ground(x - c * L, z + n * L);
    const yL = ground(x - n * .35 * s.sc, z - c * .35 * s.sc), yR = ground(x + n * .35 * s.sc, z + c * .35 * s.sc);
    // (the body tipped to the slope, so its middle on the ground between the two ends -- or on a hump under it)
    out.y = Math.max((yF + yB) / 2, ground(x, z) - .02) + s.sp.belly * s.sc - .03;
    out.pitch = Math.atan2(yF - yB, 2 * L); out.roll = Math.atan2(yR - yL, .7 * s.sc) * .7;
    return out;
  };
  const _g = { y: 0, pitch: 0, roll: 0 };

  let lastT = null;
  const crossed = (tau, at, T) => lastT !== null && T - lastT < 3 && tau - (T - lastT) < at && tau >= at;
  const api = {
    herd, list, groups,
    // (the voices: a seal in two barks and moans, the walruses' bull bellowing and grunting -- and a second walrus, if
    //  there is one, ringing its bell)
    callers: list.filter((s) => s.name === "walrus" ? s.idx < 2 : s.idx % 2 === 0)
      .map((s) => ({ name: s.name === "walrus" && s.idx === 1 ? "walrusBell" : s.name, p: s.an.position, an: s.an, pitch: s.name === "seal" ? .9 + hash(s.idx, s.group) * .25 : 1 })),
    shift: 0, T: 0, hold: null,   // (debug: seconds added to the clock; hold: a clock to stop at, for a still)
    rings: 0,
    update(T0, t) {
      const T = api.hold ?? T0 + api.shift;
      for (const s of list) {
        const a = s.an, sp = s.sp, c = plan(s, T);
        let x = s.spot[0], z = s.spot[1], h = s.rest, y, pitch = 0, roll = 0;
        if (c.st === "rest") {
          // (just back from a swim it has come up facing the land: it turns round to face the water over 6 s)
          const back = headingOf(-s.n[0], -s.n[1]);
          if (c.since !== undefined && c.since < 6) h = back + angTo(back, s.rest) * ss(0, 6, c.since);
          poseRest(s, t, T);
          lie(s, x, z, h, _g); y = _g.y; pitch = _g.pitch; roll = _g.roll;
        } else if (c.st === "down" || c.st === "up") {
          // (the way down from its spot to where it floats, and back; the first 2 s of going down turning from where it lay)
          const k = c.st === "down" ? c.k : 1 - c.k, dist = s.afloat[2] * k;
          x = s.spot[0] + s.n[0] * dist; z = s.spot[1] + s.n[1] * dist;
          const out = headingOf(s.n[0], s.n[1]);
          h = c.st === "down" ? s.rest + angTo(s.rest, out) * ss(0, 2 / c.dn, c.k) : out + Math.PI;
          const ph = (c.tau * sp.hump) * TAU, P = poseLand(s, t, ph);
          lie(s, x, z, h, _g);
          const fl = S - sp.float * s.sc, wet = ss(.6, 1, (SEA.depth(x, z) - .05) / (sp.belly * 2.2 * s.sc));
          y = lerp(_g.y + P.lift, Math.max(fl, _g.y + P.lift - sp.belly * s.sc * .8), wet);
          pitch = lerp(_g.pitch + P.pitch, 0, wet); roll = lerp(_g.roll + (P.roll ?? 0), 0, wet);
          if (wet > .3) poseSwim(s, t, 0);
          if (s.edge && crossed(c.tau, c.st === "down" ? c.t0 + c.dn * (s.edge[2] / s.afloat[2]) : -1, T)) { ring(s.edge[0], S, s.edge[1], .5 * s.sc); api.rings++; }
        } else {
          const [lx, lz, lh] = s.swim.at(c.d);
          x = lx; z = lz; h = lh;
          // (swimming at the surface, the head out; two dives on the loop, as deep as the water lets it; bottling: upright)
          const dep = SEA.depth(x, z), dive = Math.min(1.4, Math.max(0, dep - .9)) * s.sc;
          const k = c.k, dv = ss(.12, .2, k) * (1 - ss(.32, .4, k)) + ss(.62, .7, k) * (1 - ss(.82, .88, k));
          const k2 = Math.min(1, k + .01), dv2 = ss(.12, .2, k2) * (1 - ss(.32, .4, k2)) + ss(.62, .7, k2) * (1 - ss(.82, .88, k2));
          // (bottling, tipped up: sunk a little, so the head and the top of the neck are out of the water)
          y = S - sp.float * s.sc - dive * dv - c.b * sp.len * .13 * s.sc;
          pitch = -Math.atan2((dv2 - dv) * dive, .01 * s.swim.len) * .8 + c.b * 1.32;
          roll = .06 * Math.sin(t * .9 + s.off) * (1 - c.b);
          poseSwim(s, t, c.b);
          if (crossed(c.e, c.half + .5, T + 0) && c.b > 0) { ring(x, S, z, .6 * s.sc); api.rings++; }
        }
        a.position.set(x, y, z); a.rotY = h; a.pitch = pitch; a.roll = roll;
        s.state = c.st;
      }
      lastT = T; api.T = T;
      herd.update(t);
    },
    // (debug: what one is doing at clock T)
    peek(i, T = api.T) { const s = list[i]; return s && { name: s.name, group: s.group, spot: s.spot, ...plan(s, T), swim: !!s.swim }; },
    // (debug: the next time from T that animal i is in state st -- to look at a swim without waiting for one)
    next(i, st, T = api.T, step = 2, span = 4000) { for (let u = T; u < T + span; u += step) if (plan(list[i], u).st === st) return u; return null; },
  };
  console.log(`haulout: ${groups.map((g) => `${g.n} ${g.name} on the ${g.type} at ${Math.round(g.x)}, ${Math.round(g.z)}`).join("; ")} (${SEA.kind}, ${climate ?? "river country"})`);
  return api;
}
