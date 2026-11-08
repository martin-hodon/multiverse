// SKY STEEDS (2026-11-07): the beasts that walk the ground and FLY -- the pegasus (assets/creatures/monsters/pegasus.json)
// and the griffin (griffin.json). On the ground each is an ordinary wanderer in its range (index.html wanderStep), its
// wings folded along its flanks; now and then it takes to the air, circles high over its range, and comes down again.
// Their wings are drawn SPREAD, as they glide; the fold is skeleton.js PERCH (an.perch 1 on the ground, the fit
// an.perchFold: SKYSTEEDS[name].fold, squeeze). PERCH and the FLIGHT pose are one or the other (skeleton.js), so the
// legs are posed here: aloft each is HELD (an.pose, skeleton.js) -- the forelegs folded up under the chest, the hind
// legs trailing back -- blended in from its rest as it leaves the ground and out again as it touches down (`tuck`).
//   TAKING OFF (run): a gallop along the way it faces, the wings opening as it goes, hard beats, and up off the ground.
//   CLIMB: beating steadily, climbing at `climb` m/s to its height, turning onto its circle.
//   SOAR: round a centre over its range, at its own radius, speed and height -- and never lower than the ground under it
//     and ahead allows (`clear` m over it: the trees and roofs are not in the ground's height) -- the wings held out and
//     still, a burst of beats now and then (`flaps`, beats a `slot`), banked into the turn, pitched with the climb.
//   DOWN: to the start of its last glide `fin` m short of a landing place on open, level ground in its range (circling
//     down where it is too high to glide there), then the glide itself, slowing, flaring at the end (tipped up, deep
//     beats), and touching down at a canter that slows to a walk as the wings fold.
// Then it is a wanderer again, its route planned afresh from where it stands (index.html wanderStep), till its next flight.
// All of it on the wanderer's own seeded stream and the world's tick (as perchers.js): deterministic, the same for every
// peer. What is drawn between ticks is the tracks' blend (index.html track: the pose's numbers too).
export const SKYSTEEDS = {
  // fold, squeeze: the wings' fold on the ground (skeleton.js PERCH), fitted to the model; alt: [lowest, highest] m over
  // its range's ground; radius: [smallest, largest] m of its circle; speed: [slowest, fastest] m/s along it; aloft:
  // [shortest, longest] s it soars; ground: [shortest, longest] s on the ground between flights (first: the first one);
  // gallop: m/s on the take-off run; run: s of it; climb: m/s up; sink: m/s down at most; fin: the last glide's length
  // (m); glide: its slope; beatHz: beats a second (hard: taking off and climbing); slot, flaps: the bursts; clear: m over
  // the ground at least; legs: the gait's pace aloft (a share of the ground's at that speed); wingSpeed: the rig's anim.speed;
  // tuck: { front, hind } -- [upper, lower, foot] degrees (about z in its parent: + swings the foot forward) each leg is
  // held at aloft. (2026-11-08: the hind legs TRAIL -- the thigh swung back past level, the shank and the foot nearly in
  // line with it, as a leaping horse's -- where [-50, 25, 30] left them hanging as if the beast stood on the air; the
  // forelegs were right, folded up under the chest)
  pegasus: { fold: [[104, 0, -6], [-33, -74, 0], [33, 0, 0]], squeeze: [.6, .3, .2], alt: [20, 34], radius: [24, 40], speed: [8.5, 10.5],
             aloft: [45, 110], ground: [50, 140], first: [8, 40], gallop: 7.5, run: 3.4, climb: 3, sink: 2.6, fin: 30, glide: .2,
             beatHz: [.75, 1.05], slot: 9, flaps: [3, 0, 4, 2, 0, 5, 0, 3, 0], clear: 16, legs: .45, wingSpeed: .4,
             tuck: { front: [60, -125, -40], hind: [-100, 15, 10] } },
  griffin: { fold: [[94, 0, -6], [-29, -72, 0], [29, 0, 0]], squeeze: [.65, .3, .25], alt: [18, 30], radius: [20, 34], speed: [8, 10],
             aloft: [40, 90], ground: [60, 160], first: [15, 50], gallop: 7, run: 3, climb: 3.2, sink: 2.8, fin: 26, glide: .22,
             beatHz: [.8, 1.15], slot: 8, flaps: [4, 0, 3, 0, 5, 2, 0, 3, 0], clear: 16, legs: .35, wingSpeed: .4,
             tuck: { front: [55, -110, -30], hind: [-105, 20, 15] } },
};
const TAU = Math.PI * 2;
const smooth = (u) => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
const wrap = (v) => ((v + Math.PI) % TAU + TAU) % TAU - Math.PI;
const lerp = (a, b, u) => a + (b - a) * u;
// a rotation's quaternion from Euler XYZ (radians) -- the shape skeleton.js reads an.pose by ({ x, y, z, w }). (2026-11-07:
// and _x.._w too -- skeleton.js hands it to THREE's Matrix4.makeRotationFromQuaternion, whose compose reads a Quaternion's
// own fields, _x, _y, _z, _w: with x..w alone every held leg's matrix was NaN, and the legs vanished aloft, slivers left)
const quatXYZ = (x, y, z) => {
  const c1 = Math.cos(x / 2), c2 = Math.cos(y / 2), c3 = Math.cos(z / 2), s1 = Math.sin(x / 2), s2 = Math.sin(y / 2), s3 = Math.sin(z / 2);
  const qx = s1 * c2 * c3 + c1 * s2 * s3, qy = c1 * s2 * c3 - s1 * c2 * s3, qz = c1 * c2 * s3 + s1 * s2 * c3, qw = c1 * c2 * c3 - s1 * s2 * s3;
  return { x: qx, y: qy, z: qz, w: qw, _x: qx, _y: qy, _z: qz, _w: qw };
};
// THE LEGS ALOFT: each leg's three parts (the upper leg, the lower, the foot) held u of the way from their rest to the
// spec's tuck (an.pose; u 0 lets the gait have them again)
export function tuckLegs(a, u, tuck) {
  const parts = a.parts;
  if (!parts || !tuck) return;
  if (u <= .01) { if (a.pose) a.pose = null; return; }
  const P = a.pose ?? (a.pose = parts.map(() => null)), D = Math.PI / 180;
  parts.forEach((p, i) => {
    let up = null, k = 0;
    if (p.ik && !p.ik.follow) up = p;
    else if (p.ik?.follow) { up = parts[p.parentIdx]; k = 1; }
    else if (p.level && p.parentIdx >= 0 && parts[p.parentIdx].ik?.follow) { up = parts[parts[p.parentIdx].parentIdx]; k = 2; }
    if (!up?.ik) return;
    const T = (up.ik.leg ?? 0) < 2 ? tuck.front : tuck.hind, b = p.baseRot ?? [0, 0, 0];
    P[i] = { q: quatXYZ(b[0] * (1 - u), b[1] * (1 - u), lerp(b[2], T[k] * D, u)), c: null };
  });
}

// One beast's flights: `w` its wanderer, `a` its animal in the herd, `spec` its SKYSTEEDS entry, `fence` its range
// ({ x0, x1, z0, z1, inside?, home? }), groundH(x, z) the ground's height, open(x, z) whether a place is clear to land on
// (no tree, no building). -> { R, step(t, dt) }: step is called each tick before its wander step and returns true while
// it has the tick (off the ground, or running to or from it)
export function makeSkysteed(w, a, spec, { fence, groundH, open = () => true }) {
  const R = { st: null, next: null, t0: 0 };
  a.perch = 1; a.pitch = 0; a.roll = 0; a.wingT = 0;
  a.perchFold = { fold: spec.fold, squeeze: spec.squeeze };
  const rnd = (r) => r[0] + w.rng() * (r[1] - r[0]);
  const inRange = (x, z) => x > fence.x0 && x < fence.x1 && z > fence.z0 && z < fence.z1 && (!fence.inside || fence.inside(x, z));
  const centre = () => fence.home ? fence.home() : [(fence.x0 + fence.x1) / 2, (fence.z0 + fence.z1) / 2];
  const beatRate = (hz) => hz / spec.wingSpeed;   // (the wing clock's pace for that many beats a second)
  const floorAt = (x, z, h, v) => {   // the lowest it may fly here: over the ground under it and ahead (a few seconds), and the wingtips'
    let f = -1e9;
    for (const s of [0, 1.5, 3, 4.5]) { const px = x + Math.cos(h) * v * s, pz = z - Math.sin(h) * v * s; f = Math.max(f, groundH(px, pz) - s * spec.climb * .6); }
    return f + spec.clear;
  };
  // the wings: beating (hz beats a second) or held level -- the clock run on to the next level point of the beat
  // (the arm's sine at 0: every 1 / wingSpeed of it) and stopped there
  const level = 1 / spec.wingSpeed;
  const wings = (dt, hz) => {
    if (hz > 0) a.wingT += beatRate(hz) * dt;
    else { const tgt = Math.ceil(a.wingT / level - 1e-6) * level; a.wingT = Math.min(tgt, a.wingT + beatRate(spec.beatHz[0]) * dt); }
  };
  const legs = (dt, v, k = spec.legs) => { w.animT += dt * v * k / w.base; };
  a.tuckU = 0;
  const held = (dt, want) => { a.tuckU += Math.max(-dt * 1.6, Math.min(dt * 1.2, want - a.tuckU)); tuckLegs(a, smooth(a.tuckU), spec.tuck); };
  let lastH = null;
  const bank = (dt, v) => {   // banked into the turn as its speed and the turn's rate want (and eased: the tick is coarse)
    const turn = lastH === null ? 0 : wrap(w.heading - lastH) / dt; lastH = w.heading;
    const want = Math.max(-.5, Math.min(.5, -Math.atan(v * turn / 9.8)));
    a.roll += (want - a.roll) * Math.min(1, dt * 2.5);
  };
  const fly = (dt, v) => { w.p.x += Math.cos(w.heading) * v * dt; w.p.z -= Math.sin(w.heading) * v * dt; };
  const steer = (dt, goal, rate = .55) => { w.heading += Math.max(-rate * dt, Math.min(rate * dt, wrap(goal - w.heading))); };
  // where to come down: open, level ground in its range (the best of a few tries), and the way to face it from
  function landing() {
    let best = null, bs = Infinity;
    for (let k = 0; k < 24; k++) {
      const x = lerp(fence.x0, fence.x1, .1 + .8 * w.rng()), z = lerp(fence.z0, fence.z1, .1 + .8 * w.rng());
      if (!inRange(x, z) || !open(x, z)) continue;
      const g = groundH(x, z), sl = Math.max(...[[3, 0], [-3, 0], [0, 3], [0, -3]].map(([dx, dz]) => Math.abs(groundH(x + dx, z + dz) - g))) / 3;
      const s = sl + w.rng() * .05;
      if (s < bs) { bs = s; best = [x, z]; }
    }
    if (!best) { const c = centre(); best = c; }
    // facing along its own way in: from where it is, round to it
    const [x, z] = best, h = Math.atan2(-(z - w.p.z), x - w.p.x);
    // the last stretch: the touch-down run (a few metres on) must be open too -- else the other way round
    const runOk = (hh) => [3, 6, 9].every((d) => open(x + Math.cos(hh) * d, z - Math.sin(hh) * d) && inRange(x + Math.cos(hh) * d * .5, z - Math.sin(hh) * d * .5));
    const hl = runOk(h) ? h : runOk(h + Math.PI) ? h + Math.PI : h;
    const y = groundH(x, z), fx = Math.cos(hl), fz = -Math.sin(hl);
    R.L = { x, y, z, h: hl };
    R.A = { x: x - fx * spec.fin, y: y + spec.fin * spec.glide, z: z - fz * spec.fin };
  }
  const T = {
    // the take-off run: a gallop, the wings opening, beats, off the ground
    run(t, dt) {
      const u = (t - R.t0) / spec.run, p = w.p;
      const v = lerp(R.v0, spec.gallop, smooth(u / .6));
      fly(dt, v);
      a.perch = 1 - smooth((u - .1) / .35);
      const lift = smooth((u - .55) / .45);
      p.y = groundH(p.x, p.z) + spec.climb * spec.run * .5 * Math.max(0, u - .55) ** 2 / .45;
      wings(dt, u > .3 ? spec.beatHz[1] * 1.15 : 0);
      a.pitch = .14 * lift;
      legs(dt, v, 1); held(dt, lift > .15 ? 1 : 0);
      w.setT(w.animT, a.wingT, undefined, true, true);
      if (u >= 1) { R.st = "climb"; R.t0 = t; R.v = v; }
    },
    // up to its height on steady beats, turning onto its circle
    climb(t, dt) {
      const p = w.p, v = R.v = lerp(R.v, R.speed, Math.min(1, dt * .5));
      steer(dt, circleGoal(), .45);
      fly(dt, v);
      const want = Math.max(R.alt, floorAt(p.x, p.z, w.heading, v));
      p.y += Math.min(spec.climb, Math.max(0, want - p.y)) * dt;
      p.y = Math.max(p.y, groundH(p.x, p.z) + 1);
      wings(dt, spec.beatHz[1]);
      a.pitch += (.16 - a.pitch) * Math.min(1, dt * 2);
      bank(dt, v); legs(dt, v); held(dt, 1); w.setT(w.animT, a.wingT, undefined, true, true);
      if (p.y >= want - .5) { R.st = "soar"; R.t0 = t; R.until = t + rnd(spec.aloft); }
    },
    // round and round, gliding, a burst of beats now and then
    soar(t, dt) {
      const p = w.p, v = R.speed;
      steer(dt, circleGoal());
      fly(dt, v);
      const swell = 3 * Math.sin((t - R.t0) * .07 + R.ph);
      const want = Math.max(R.alt + swell, floorAt(p.x, p.z, w.heading, v)), dy = Math.max(-spec.sink * .5, Math.min(spec.climb, (want - p.y) * .5));
      p.y += dy * dt;
      const slot = Math.floor((t - R.t0) / spec.slot), nb = spec.flaps[(slot + R.k) % spec.flaps.length] + (dy > 1 ? 3 : 0);
      const inSlot = (t - R.t0) - slot * spec.slot;
      wings(dt, inSlot > 1 && inSlot < 1 + nb / R.hz ? R.hz : 0);
      a.pitch += (Math.max(-.12, Math.min(.18, Math.atan2(dy, v))) - a.pitch) * Math.min(1, dt * 1.5);
      bank(dt, v); legs(dt, v); held(dt, 1); w.setT(w.animT, a.wingT, undefined, true, true);
      if (t > R.until) { landing(); R.st = "down"; R.t0 = t; }
    },
    // to the start of the last glide: on toward it, sinking as the way left allows (circling down where it is too high)
    down(t, dt) {
      const p = w.p, A = R.A, dx = A.x - p.x, dz = A.z - p.z, d = Math.hypot(dx, dz), v = R.speed, high = p.y - A.y;
      // (near enough -- within a second's flight, not too high for the glide -- or circling it too long: on to the glide.
      //  An exact hit is not to be had: at its speed and rate of turn it would only orbit the point)
      if ((d < Math.max(4, v * 1.2) && high < 8) || t - R.t0 > 80) { R.st = "fin"; R.t0 = t; R.F = { x: p.x, y: p.y, z: p.z, h: w.heading }; R.len = Math.hypot(R.L.x - p.x, R.L.y - p.y, R.L.z - p.z); return; }
      // (aimed at a point back along the line of the glide, so it comes onto that line rather than across it)
      const lead = Math.min(d * .4, 15), fx = Math.cos(R.L.h), fz = -Math.sin(R.L.h);
      let goal = Math.atan2(-(dz - fz * lead), dx - fx * lead);
      if (high > d * .45 + 2) goal += Math.PI / 2 * R.dir;   // (too high to glide down to it: round, sinking)
      steer(dt, goal, d < 40 ? .9 : .6);
      fly(dt, v);
      const want = high / Math.max(d / v, .5);
      p.y -= Math.max(-1.5, Math.min(spec.sink, want)) * dt;
      p.y = Math.max(p.y, A.y - 1, floorAt(p.x, p.z, w.heading, v) - spec.clear + Math.min(spec.clear, d * spec.glide));
      wings(dt, p.y < A.y - .5 ? R.hz : 0);
      a.pitch += (-.08 - a.pitch) * Math.min(1, dt * 1.5);
      bank(dt, v); legs(dt, v); held(dt, 1); w.setT(w.animT, a.wingT, undefined, true, true);
    },
    // the last glide, slowing all the way in, the flare over its last third: tipped up, deep beats
    fin(t, dt) {
      const F = R.F, L = R.L, Tn = 1.5 * R.len / R.speed, u = Math.min(1, (t - R.t0) / Tn), s = 1 - Math.pow(1 - u, 1.5), p = w.p;
      p.set(lerp(F.x, L.x, s), lerp(F.y, L.y, s), lerp(F.z, L.z, s));
      p.y = Math.max(p.y, groundH(p.x, p.z));
      const along = Math.atan2(-(L.z - F.z), L.x - F.x);   // (facing the way it goes: it may come in off the planned line)
      w.heading = F.h + wrap(along - F.h) * smooth(u / .3);
      const fl = smooth((u - .6) / .3);
      a.pitch = lerp(-.06, .32, fl);
      wings(dt, fl > 0 ? R.hz * 1.3 : 0);
      a.roll += -a.roll * Math.min(1, dt * 3);
      legs(dt, R.speed * (1 - .4 * u), lerp(spec.legs, 1, fl)); held(dt, u > .7 ? 0 : 1);   // (let down for the landing)
      w.setT(w.animT, a.wingT, undefined, true, true);
      if (u >= 1) { R.st = "touch"; R.t0 = t; }
    },
    // down: a canter slowing to a walk, the body level, the wings folding along its flanks
    touch(t, dt) {
      const u = Math.min(1, (t - R.t0) / 2.6), p = w.p, v = lerp(spec.gallop * .75, w.speed, smooth(u));
      fly(dt, v);
      p.y = groundH(p.x, p.z);
      a.pitch *= 1 - Math.min(1, dt * 4); a.roll = 0;
      a.perch = smooth((u - .1) / .6);
      wings(dt, 0);
      legs(dt, v, 1); held(dt * 4, 0);
      w.setT(w.animT, a.wingT, undefined, true, u < .6);
      if (u >= 1) {
        R.st = null; R.next = t + rnd(spec.ground); a.perch = 1; a.pitch = 0; a.roll = 0; a.tuckU = 0; a.pose = null;
        w.lane = null; w.moving = true; w.until = t + 2 + w.rng() * 4; w.yFrom = p.y;   // (wanderStep: its route planned afresh from here)
      }
    },
  };
  // the way round its circle from where it is: along the tangent, pulled in or out toward the radius
  function circleGoal() {
    const p = w.p, cx = R.C[0], cz = R.C[1], dx = p.x - cx, dz = p.z - cz, r = Math.hypot(dx, dz) || 1;
    const tang = Math.atan2(-(R.dir * dx), -R.dir * dz);   // (heading h moves along (cos h, -sin h): the tangent's, its way round)
    return tang - Math.max(-1, Math.min(1, (r - R.rad) / R.rad * 1.6)) * R.dir;   // (outside it: turned in, toward the centre)
  }
  function takeOff(t) {
    const c = centre();
    R.C = [c[0] + (w.rng() - .5) * 20, c[1] + (w.rng() - .5) * 20];
    R.rad = rnd(spec.radius); R.speed = rnd(spec.speed); R.dir = w.rng() < .5 ? 1 : -1; R.k = Math.floor(w.rng() * spec.flaps.length);
    R.alt = groundH(R.C[0], R.C[1]) + rnd(spec.alt); R.ph = w.rng() * TAU; R.hz = rnd(spec.beatHz);
    // (it runs the way it faces, turned toward the middle of its range if that is behind it: the open ground)
    const toC = Math.atan2(-(c[1] - w.p.z), c[0] - w.p.x);
    if (Math.abs(wrap(toC - w.heading)) > Math.PI / 2) w.heading = toC;
    R.st = "run"; R.t0 = t; R.v0 = w.moving ? w.speed : 0; lastH = null;
  }
  return {
    R,
    get aloft() { return R.st !== null; },
    // (2026-11-08) set down on the ground where it stands, its wings folded, its legs its own -- a player mounting it
    // (index.html: ridden, it flies as the rider drives it) or dismounting; its next flight of its own from `t` on
    ground(t) { R.st = null; R.next = t + rnd(spec.ground); a.perch = 1; a.pitch = 0; a.roll = 0; a.tuckU = 0; a.pose = null; w.lane = null; lastH = null; },
    step(t, dt) {
      if (R.next === null) R.next = t + rnd(spec.first);
      if (!R.st) {
        if (t < R.next || a.hidden) return false;
        takeOff(t);
      }
      T[R.st](t, dt);
      w.apply(w.heading);
      return true;
    },
  };
}
