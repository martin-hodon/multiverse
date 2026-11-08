// PERCHERS (2026-11-06): the birds the world only ever showed aloft -- the eagle-owls, the macaws, the golden eagles
// (and the buzzard and the falcon, should the cast take them in) -- now come down and sit. Out and about (the owls by
// night, the rest by day) a flight now and then ends on a perch near it; in their resting time they fly to one and sit
// there till they are out again. Where: the trees' near-level boughs (flora.js makeTree `boughs`), the crowns' upper
// boughs of the tall trees, the gable ends of the roofs' ridges and the ridges of the tall buildings (index.html
// ridgeLines) -- each kind of bird its own (PERCHERS.sites).
//   COMING IN: it steers to a point `fin` m short of the perch and `fin * glide` above it (circling down where it is
//   too high to glide there), glides the last stretch slowing all the way, flares -- tipped up, a few deep beats --
//   and touches down; its wings fold along its flanks and it stands up on the perch (skeleton.js PERCH: an.perch,
//   an.pitch -- legs let down through the flare (an.legs), the toes curled round the bough (an.perchR): skeleton.js PERCH
//   LEGS; a model without them rests its belly on the branch: `foot`).
//   SITTING: still, the head turning now and then (an.look; an owl's far round); a macaw shuffles along its bough.
//   TAKING OFF: the wings out, a drop off the perch with hard beats, away level, and climbing back to its height
//   (index.html wanderStep: w.yFrom, the climb).
// All of it on the wanderer's own seeded stream and the world's tick: as deterministic as the rest of the wanderers.
// What is drawn between ticks is the tracks' blend (index.html track: the pose numbers too).
export const PERCHERS = {
  // pitch: degrees tipped up sitting; flare: tipped up touching down; foot: [x, y] the point of the model (root frame,
  // metres) that rests on the perch when its sculpt has no `foot` (else that foot's underside); sites: { kind: [lowest, highest] metres
  // over the ground }; sit: seconds on a perch between flights; land: the share of its flights that end on one; near:
  // how far it looks for one (metres); fin: the last glide's length (m); glide: its slope; sink: m/s at most coming
  // down; start: the share sitting when the world begins; look: [shortest, longest] seconds between turns of the head,
  // lookMax its reach (radians of the head), lookV its speed; shuffle: a step along the bough now and then (m);
  // group: metres a perch nearer to its own kind counts as nearer (macaws keep together); fold, squeeze: its wings' fold
  // (skeleton.js PERCH -- the default the eagle-owl's), fitted to its model
  owl: { pitch: 62, flare: 30, foot: [-.14, .3], sites: { bough: [3, 11], gable: [3, 30] }, sit: [25, 90], land: .5, near: 90, fin: 8, glide: .32,
         sink: 2.5, start: .35, look: [2.5, 8], lookMax: 2.2, lookV: 5, doze: 3 },
  parrot: { pitch: 50, flare: 28, foot: [-.06, .25], sites: { bough: [3, 15] }, sit: [15, 60], land: .6, near: 70, fin: 6, glide: .3,
            sink: 2.5, start: .5, look: [1.2, 4], lookMax: 1.1, lookV: 4, shuffle: .22, group: 40,
            fold: [[100, -40, 12], [0, 0, 0], [0, 0, 0]], squeeze: [.45, 1, .3] },
  // (2026-11-07) the great hornbill (assets/creatures/birds/hornbill.json, from the macaw's plan): high in the forest's
  // trees, on the boughs and the crowns' tops; a pair or three keep together
  hornbill: { pitch: 30, flare: 26, foot: [-.07, .33], sites: { bough: [5, 20], top: [8, 40] }, sit: [20, 90], land: .55, near: 90, fin: 8, glide: .28,
              sink: 2.5, start: .45, look: [1.5, 5], lookMax: 1.1, lookV: 3, group: 30,
              // (the eagle's fold: the wing laid back along the flank, the hand behind -- the macaw's stacked its wider
              //  barred feathers into rings)
              fold: [[90, 0, 8], [0, 0, 0], [0, -80, 0]], squeeze: [.7, 1, .25] },
  eagle: { pitch: 50, flare: 26, foot: [-.17, .32], sites: { top: [7, 40], high: [8, 60] }, sit: [40, 140], land: .3, near: 170, fin: 14, glide: .22,
           sink: 3.5, start: .3, look: [3, 9], lookMax: 1.3, lookV: 3, fold: [[90, 0, 8], [0, 0, 0], [0, -80, 0]], squeeze: [.7, 1, .25] },
  buzzard: { pitch: 40, flare: 26, foot: [-.1, .19], sites: { top: [6, 40], high: [8, 60], bough: [5, 20] }, sit: [30, 120], land: .35, near: 140, fin: 12, glide: .22,
             sink: 3, start: .3, look: [3, 9], lookMax: 1.3, lookV: 3, fold: [[93, -5, 8], [0, -10, 0], [15, -55, 5]], squeeze: [.8, 1, .25] },
  falcon: { pitch: 45, flare: 28, foot: [-.08, .15], sites: { high: [8, 80], top: [8, 40] }, sit: [30, 120], land: .3, near: 170, fin: 12, glide: .22,
            sink: 4, start: .3, look: [2, 6], lookMax: 1.4, lookV: 4, fold: [[86, -35, 15], [0, 0, 0], [0, -7, 0]], squeeze: [.5, 1, .3] },
};
const TAKEOFF = 1.6, SETTLE = .9, CLIMB = 1.6, RIDGE_R = .05;   // seconds off the perch to flying on; to sit settled; m/s back up to its height
const PER_TREE = 8;   // boughs kept a tree

// THE PERCHES: built once from what the world has (the trees grow again with the seasons, on the same boughs)
//   trees: index.html treeCols ({ x, z, h, boughs: [{ a, b, r0, r1 }] world space });  ridges: ridgeLines
export function perchSites({ trees, ridges, groundH }) {
  const S = { bough: [], top: [], gable: [], high: [] };
  for (const tr of trees) {
    const g = groundH(tr.x, tr.z), bs = (tr.boughs ?? []).filter((b) => Math.hypot(b.b[0] - b.a[0], b.b[2] - b.a[2]) > .35);
    // (spread through the crown: sorted by height, every n-th)
    bs.sort((p, q) => p.a[1] + p.b[1] - q.a[1] - q.b[1]);
    const step = Math.max(1, bs.length / PER_TREE);
    for (let k = 0; k < bs.length; k += step) {
      const b = bs[Math.floor(k)], u = .55, x = b.a[0] + (b.b[0] - b.a[0]) * u, z = b.a[2] + (b.b[2] - b.a[2]) * u, cy = b.a[1] + (b.b[1] - b.a[1]) * u;
      const L = Math.hypot(b.b[0] - b.a[0], b.b[2] - b.a[2]), r = b.r0 + (b.r1 - b.r0) * u, slope = (b.b[1] - b.a[1]) / L;
      const s = { x, z, y: cy + r * Math.hypot(1, slope), g, ax: (b.b[0] - b.a[0]) / L, az: (b.b[2] - b.a[2]) / L, kind: "bough", tree: tr, seg: b, u, taken: null };
      S.bough.push(s);
      if (tr.h >= 9 && cy - g > tr.h * .55) S.top.push(s);
    }
  }
  for (const rd of ridges) {
    if (rd.hip || rd.share || !rd.roof) continue;   // (a roof's ridge under its tiles: not a hip, nor a wall's top -- flat, the tail would go into it)
    const dx = rd.b[0] - rd.a[0], dz = rd.b[1] - rd.a[1], L = Math.hypot(dx, dz);
    if (L < 2) continue;
    const ax = dx / L, az = dz / L, top = rd.y + (/thatch/.test(rd.roof?.pattern ?? "") ? .11 : .06);   // (on the ridge tiles: ridgecaps.js)
    const at = (u, kind) => { const x = rd.a[0] + dx * u, z = rd.a[1] + dz * u; return { x, z, y: top, g: groundH(x, z), ax, az, kind, ridge: rd, taken: null }; };
    const e = Math.min(.45, .35 / L);   // (a gable end: a hand's breadth in from the end)
    S.gable.push(at(e, "gable"), at(1 - e, "gable"));
    if (top - groundH(rd.a[0] + dx / 2, rd.a[1] + dz / 2) >= 8) S.high.push(at(.5, "high"));
  }
  return S;
}

// One bird's perching: `w` its wanderer, `a` its animal in the herd, `spec` its PERCHERS entry. -> { step(t, dt, out) }:
// step is called each tick before its wander step and returns true when it took the tick (coming in, sat, taking off);
// out: whether this is its time to be about (else it rests on a perch -- or, finding none, is hidden as before)
// sites: () => the world's perchSites (asked for at its first step: the trees are grown after the herd)
export function makePercher(w, a, spec, sites, def) {
  const R = { st: null, site: null, fresh: true, next: 0, name: def?.name };
  const legs = !!a.parts?.flight;   // (a model standing on its legs with a flight pose of its own: upright already, its feet on the perch)
  // (the feet tucked up under the tail, as an aloft model carries them: their underside is what rests on the perch -- or
  //  failing a sculpted `foot`, the spec's point under the vent)
  const fp = Array.isArray(def?.sculpt?.shape) ? def.sculpt.shape.find((q) => q.id === "foot" && q.type === "ell" && q.c && q.r) : null;
  // (PERCH LEGS -- skeleton.js: a model with legs to stand on, drawn standing: its foot bone's origin is the toes' root on
  //  the perch top, and the pitch they were drawn for its own)
  const byId = new Map((def?.parts ?? []).map((p) => [p.id, p])), fb = byId.get("footL");
  let stand = null;
  if (fb && fb.perchPitch !== undefined) { stand = [0, 0]; for (let q = fb; q; q = q.parent ? byId.get(q.parent) : null) { stand[0] += q.pos?.[0] ?? 0; stand[1] += q.pos?.[1] ?? 0; } }
  const foot = legs ? [0, 0] : stand ?? (fp ? [fp.c[0], fp.c[1] - fp.r[1]] : spec.foot), P0 = legs ? 0 : (stand ? fb.perchPitch : spec.pitch) * Math.PI / 180, PF = legs ? 0 : spec.flare * Math.PI / 180;
  let dedup = null;   // (its kind's perches: built at its first step)
  a.flyT = 1;
  if (spec.fold) a.perchFold = { fold: spec.fold, squeeze: spec.squeeze };   // (its wings' own fold: skeleton.js PERCH)
  const smooth = (u) => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
  // where the root goes for the vent to be on the perch at heading h, tipped up th
  const rootAt = (s, h, th, out) => {
    const cx = foot[0] * Math.cos(th) - foot[1] * Math.sin(th), cy = foot[0] * Math.sin(th) + foot[1] * Math.cos(th);
    out.x = s.x - cx * Math.cos(h); out.y = s.y - cy; out.z = s.z + cx * Math.sin(h);
    return out;
  };
  const _r = { x: 0, y: 0, z: 0 };
  const wrap = (v) => ((v + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
  function pick(maxD) {
    const p = w.p;
    let best = null, bd = maxD;
    const kin = spec.group ? new Set(dedup.filter((q) => q.taken && q.tree && q.taken.spec === spec).map((q) => q.tree)) : null;
    for (const s of dedup) {
      if (s.taken) continue;
      let d = Math.hypot(s.x - p.x, s.z - p.z);
      if (kin?.has(s.tree)) d -= spec.group;   // (its own kind already in that tree)
      if (d < bd) { bd = d; best = s; }
    }
    return best;
  }
  function claim(s) {
    s.taken = R; R.spec = spec; R.site = s;
    a.perchR = s.seg ? s.seg.r0 + (s.seg.r1 - s.seg.r0) * s.u : RIDGE_R;   // (the toes curled round it: skeleton.js PERCH LEGS)
    // it faces across the bough (or the ridge), whichever way is nearer the way it is flying
    const h1 = Math.atan2(s.ax, -s.az), h2 = h1 + Math.PI;   // (perpendicular to (ax, az) in the lanes' convention: forward (cos h, -sin h))
    R.h = Math.abs(wrap(h1 - w.heading)) < Math.abs(wrap(h2 - w.heading)) ? h1 : h2;
  }
  function sitNow(s, t) {
    claim(s); R.st = "sit"; R.t0 = t; R.lookAt = t + 1; R.lookT = 0;
    w.heading = R.h; rootAt(s, R.h, P0, _r); w.p.set(_r.x, _r.y, _r.z);
    a.perch = 1; a.legs = 1; a.pitch = P0; a.flyT = 0; a.look = 0; w.apply(w.heading);
  }
  function release() { if (R.site?.taken === R) R.site.taken = null; R.site = null; }
  function approach(s, t) {
    claim(s); R.st = "in"; R.t0 = t;
    const fx = Math.cos(R.h), fz = -Math.sin(R.h);
    rootAt(s, R.h, PF, _r);
    R.L = { x: _r.x, y: _r.y, z: _r.z };   // where the root is as it touches down
    R.A = { x: _r.x - fx * spec.fin, y: _r.y + spec.fin * spec.glide, z: _r.z - fz * spec.fin };   // the start of the last glide
  }
  const T = {
    // to the start of the last glide: flying on toward it, sinking as the way left allows (circling where it is too high)
    in(t, dt) {
      const p = w.p, A = R.A, dx = A.x - p.x, dz = A.z - p.z, d = Math.hypot(dx, dz), v = w.speed, high = p.y - A.y;
      if (d < Math.max(1.2, v * dt * 1.5) && Math.abs(high) < 1) { R.st = "fin"; R.t0 = t; R.F = { x: p.x, y: p.y, z: p.z, h: w.heading }; R.len = Math.hypot(R.L.x - p.x, R.L.y - p.y, R.L.z - p.z); return; }
      let goal = Math.atan2(-dz, dx);
      if (high > d * .6 + 1.5) goal += Math.PI / 2;   // (too high to glide down to it: round, sinking)
      w.heading += Math.max(-2 * dt, Math.min(2 * dt, wrap(goal - w.heading)));
      p.x += Math.cos(w.heading) * v * dt; p.z -= Math.sin(w.heading) * v * dt;
      const want = high / Math.max(d / v, .5);   // (the sink that brings it in at the right height)
      p.y -= Math.max(-1, Math.min(spec.sink, want)) * dt;
      p.y = Math.max(p.y, A.y - 1);
      w.animT += dt;   // (beating on)
      a.pitch = 0; a.legs = 0;
    },
    // the last glide, slowing all the way in; the flare over its last third: tipped up, a few deep beats
    fin(t, dt) {
      const F = R.F, Tn = 1.6 * R.len / w.speed, u = Math.min(1, (t - R.t0) / Tn), s = 1 - Math.pow(1 - u, 1.6), p = w.p;
      p.set(F.x + (R.L.x - F.x) * s, F.y + (R.L.y - F.y) * s, F.z + (R.L.z - F.z) * s);
      w.heading = F.h + wrap(R.h - F.h) * smooth(u / .7);
      const fl = smooth((u - .62) / .3);
      a.pitch = PF * fl; a.legs = smooth((u - .5) / .35);   // (the legs let down through the flare: on the perch as it touches)
      if (fl > 0) w.animT += dt * 1.7; else w.animT += (Math.round(w.animT * 2 * w.hz) / (2 * w.hz) - w.animT) * Math.min(1, dt * 6);   // (gliding: the wings level)
      if (u >= 1) { R.st = "land"; R.t0 = t; }
    },
    // touched down: the wings folding, tipped up onto the perch, the vent where it was
    land(t, dt) {
      const u = smooth((t - R.t0) / SETTLE);
      a.perch = u; a.legs = 1; a.pitch = PF + (P0 - PF) * u; a.flyT = 0;
      rootAt(R.site, R.h, a.pitch, _r); w.p.set(_r.x, _r.y, _r.z);
      w.animT += dt * .8 * (1 - u);
      if (u >= 1) { R.st = "sit"; R.t0 = t; R.lookAt = t + 1 + w.rng() * 2; R.lookT = 0; R.until = t + spec.sit[0] + w.rng() * (spec.sit[1] - spec.sit[0]); }
    },
    sit(t, dt, out) {
      // its head turning now and then: to a new bearing, quickly, and held -- dozing (an owl in its resting time), seldom
      if (t > R.lookAt) {
        R.lookT = (w.rng() * 2 - 1) * spec.lookMax / .6;   // (an.look is shared: the head takes .6 of it -- skeleton.js)
        if (w.rng() < .35) R.lookT = 0;
        R.lookAt = t + (spec.look[0] + w.rng() * (spec.look[1] - spec.look[0])) * (!out && spec.doze ? spec.doze : 1);
        if (spec.shuffle && R.site.seg && w.rng() < .3) R.step = { u0: R.site.u, u1: Math.max(.2, Math.min(.85, R.site.u + (w.rng() < .5 ? -1 : 1) * spec.shuffle / Math.max(.4, Math.hypot(R.site.seg.b[0] - R.site.seg.a[0], R.site.seg.b[2] - R.site.seg.a[2])))), t0: t };
      }
      a.look = (a.look ?? 0) + Math.max(-spec.lookV * dt, Math.min(spec.lookV * dt, R.lookT - (a.look ?? 0)));
      if (R.step) {   // (a macaw sidling along its bough: the bough's own height under it there)
        const u = smooth((t - R.step.t0) / 1.2), b = R.site.seg, s = R.site, k = R.step.u0 + (R.step.u1 - R.step.u0) * u;
        const L = Math.hypot(b.b[0] - b.a[0], b.b[2] - b.a[2]), r = b.r0 + (b.r1 - b.r0) * k, sl = (b.b[1] - b.a[1]) / L;
        s.x = b.a[0] + (b.b[0] - b.a[0]) * k; s.z = b.a[2] + (b.b[2] - b.a[2]) * k; s.y = b.a[1] + (b.b[1] - b.a[1]) * k + r * Math.hypot(1, sl); s.u = k; a.perchR = r;
        if (u >= 1) R.step = null;
      }
      a.perch = 1; a.legs = 1; a.pitch = P0; a.flyT = 0;
      rootAt(R.site, R.h, P0, _r); w.p.set(_r.x, _r.y, _r.z);
      w.heading = R.h;
      if (out && t > R.until) { R.st = "off"; R.t0 = t; R.y0 = w.p.y; }
    },
    // off: the wings out, a drop off the perch on hard beats, away level -- then flying on, climbing to its height
    off(t, dt) {
      const u = (t - R.t0) / TAKEOFF, p = w.p;
      a.perch = 1 - smooth(u / .25); a.legs = 1 - smooth((u - .1) / .4); a.flyT = 1;   // (pushing off, then the legs drawn up)
      a.pitch = P0 * (1 - smooth(u / .3)) - .12 * Math.sin(Math.PI * Math.min(1, u));
      a.look += -a.look * Math.min(1, dt * 6);
      const v = w.speed * smooth(u);
      p.x += Math.cos(w.heading) * v * dt; p.z -= Math.sin(w.heading) * v * dt;
      p.y = R.y0 - .35 * Math.sin(Math.PI * Math.min(1, u / .5)) + CLIMB * TAKEOFF * Math.max(0, u - .4) ** 2 / 1.2;   // (climbing at CLIMB as it hands over)
      w.animT += dt * 2.2 * Math.min(1, u * 3);
      if (u >= 1) {
        release(); R.st = null; R.next = t + 15 + w.rng() * 20;
        a.pitch = 0; a.look = 0; a.perch = 0; a.legs = 0;
        w.lane = null; w.moving = true; w.until = t + 4 + w.rng() * 8; w.yFrom = p.y;   // (wanderStep: its route planned afresh from here, and the climb)
      }
    },
  };
  return {
    R,
    get perched() { return R.st === "sit" || R.st === "land"; },
    step(t, dt, out) {
      if (!dedup) {
        const S = sites(), by = Object.entries(spec.sites).map(([k, [lo, hi]]) => [k, (S[k] ?? []).filter((s) => s.y - s.g >= lo && s.y - s.g <= hi)]);
        dedup = [...new Set(by.flatMap(([, L]) => L))];
        R.sites = Object.fromEntries(by.map(([k, L]) => [k, L.length]));   // (how many of each kind its kind has: a look from outside)
      }
      if (!dedup.length) return false;
      if (!R.st) {
        if (R.fresh) {   // the world beginning: some of them (all, in their resting time) already sat on a perch near where they are
          R.fresh = false;
          if (!out || w.rng() < spec.start) { const s = pick(out ? spec.near * 2 : Infinity); if (s) { sitNow(s, t); R.until = t + w.rng() * spec.sit[1]; return true; } }
          return false;
        }
        if (a.hidden || t <= R.next) return false;   // (a hidden one stays hidden: it is not seen arriving out of nowhere)
        if (!out) {   // its time to rest: to a perch, however far
          const s = pick(Infinity); if (!s) { R.next = t + 10; return false; }
          approach(s, t);
        } else if (t > w.until && w.moving && w.rng() < spec.land) {   // the end of a flight: now and then, down on a perch near it
          const s = pick(spec.near); if (!s) { R.next = t + 10; return false; }
          approach(s, t);
        } else return false;
      }
      if (R.st === "sit") {   // (resting: sat till it is time to be out, and off a little after)
        if (!out) R.rested = true;
        else if (R.rested) { R.rested = false; R.until = t + w.rng() * 60; }
      }
      T[R.st](t, dt, out);
      w.apply(w.heading);
      w.setT(w.animT);
      return true;
    },
  };
}
