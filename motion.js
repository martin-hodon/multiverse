// MOTION: positions held, movements made of them, exercises made of movements -- played on a rig (joints.js), the
// body kept on the ground and inside its own rules (bodycheck.js); and reaching (reach.js). docs/motion.md.
//
//   assets/people/positions.json   POSITIONS: every joint's angles (unnamed: at rest); one may be another's MIRROR
//                                  image, or FROM another with some joints changed
//   assets/people/movements.json   MOVEMENTS: a start position and the KEYS it passes through -- each a position,
//                                  the time to get there and how long it is held; one may mirror another
//   assets/people/exercises.json   EXERCISES: movements in a sequence, repeated (reps), at a tempo
//
// Between two keys every angle moves along a MINIMUM-JERK curve (Flash & Hogan 1985: how a person's limbs speed up
// and slow down -- no jolt at either end), the body set on the ground at every frame.
import * as THREE from "three";
import { MODEL, JOINT_LIST, restAngles, readPosition, mirrorAngles, blendAngles, copyAngles, setAngles, ground, releaseRig } from "./joints.js";
import { fixBody, checkBody } from "./bodycheck.js";
import { planReach, reachPosition, armOf, palm } from "./reach.js";
import { createStance } from "./stance.js";

export const minJerk = (u) => u * u * u * (10 - 15 * u + 6 * u * u);
const swapSides = (name) => name.replace(/right|left/g, (w) => (w === "right" ? "left" : "right"));

// THE LIBRARY: the three files read into positions (as angles) and timelines
export function createLibrary({ positions, movements, exercises }) {
  const P = positions?.positions ?? {}, M = movements?.movements ?? {}, X = exercises?.exercises ?? {};
  const cache = new Map();
  function position(name, seen = []) {
    if (cache.has(name)) return cache.get(name);
    const def = P[name];
    if (!def) throw new Error(`no position "${name}"`);
    if (seen.includes(name)) throw new Error(`position "${name}" is its own source (${seen.join(" -> ")})`);
    const a = def.mirror ? mirrorAngles(position(def.mirror, [...seen, name]))
      : readPosition(def, def.from ? position(def.from, [...seen, name]) : restAngles());
    cache.set(name, a);
    return a;
  }
  // a movement's keys, a mirrored one's with right and left swapped in every position it names
  function movement(name) {
    const def = M[name];
    if (!def) throw new Error(`no movement "${name}"`);
    if (def.mirror) { const m = movement(def.mirror); return { ...m, start: swapSides(m.start), keys: m.keys.map((k) => ({ ...k, to: swapSides(k.to) })) }; }
    return { start: def.start, via: def.via, keys: def.keys, about: def.about };
  }
  // AN EXERCISE (or a movement alone) as a TIMELINE: segments { to, time, hold, label }, from its start position
  function timeline(name, { reps } = {}) {
    if (X[name]) {
      const ex = X[name], seq = ex.sequence ?? [ex.movement], tempo = ex.tempo ?? 1, n = reps ?? ex.reps ?? 1;
      // (onto its start by the way the first movement says -- `via`: down to the floor through a squat, the hands put down)
      const first = movement(seq[0]), segs = [...(first.via ?? []).map((v) => ({ to: position(v), time: 1.0, hold: .15, label: `getting there: ${v}` })),
                                              { to: position(first.start), time: 1.2, hold: .4, label: "start" }];
      for (let r = 1; r <= n; r++) for (const mv of seq) for (const k of movement(mv).keys)
        segs.push({ to: position(k.to), time: (k.time ?? 1) * tempo, hold: (k.hold ?? 0) * (k.holdTempo === false ? 1 : tempo), hop: !!k.hop, label: `${k.to} · ${r}/${n}`, rep: r });
      return { name, about: ex.about, segs };
    }
    const mv = movement(name);
    return { name, about: mv.about, segs: [...(mv.via ?? []).map((v) => ({ to: position(v), time: 1.0, hold: .15, label: `getting there: ${v}` })),
                                           { to: position(mv.start), time: 1, hold: .3, label: "start" }, ...mv.keys.map((k) => ({ to: position(k.to), time: k.time ?? 1, hold: k.hold ?? 0, hop: !!k.hop, label: k.to }))] };
  }
  return { position, movement, timeline, positions: Object.keys(P), movements: Object.keys(M), exercises: Object.keys(X), exercise: (n) => X[n] };
}

// THE RANGES: each movement of each joint (the trunk's, the right side's) in turn, out to one limit, the other and
// back to rest -- what the joint model allows, shown (`only`: one joint's key, "right.shoulder")
export function rangeTimeline(only = null) {
  const rest = restAngles(), segs = [];
  for (const j of JOINT_LIST) {
    if (j.side === "left" || (only && only !== j.key)) continue;
    for (const [mv, d] of Object.entries(j.def.movements)) {
      const at = (v) => { const a = copyAngles(rest); a.joints[j.key][mv] = v; return a; };
      segs.push({ to: at(d.min), time: .9, hold: .25, label: `${j.key} ${mv} ${d.min}°` },
                { to: at(d.max), time: 1.4, hold: .25, label: `${j.key} ${mv} ${d.max}°` },
                { to: rest, time: .9, hold: .1, label: `${j.key} ${mv}: rest` });
    }
  }
  return { name: only ? `range of the ${only}` : "every joint's range", segs };
}

// THE PLAYER on one rig: hold a position, play a timeline (looping), reach for points. update(dt) poses the figure.
export function createMotion(rig, lib, { fix = true } = {}) {
  let tl = null, t = 0, loop = true, from = restAngles(), held = restAngles(), info = "rest", reachDemo = null;
  const scratch = copyAngles(held);
  // THE STANCE (stance.js): where the feet and hands stand; each move along a timeline is planned over it when it
  // begins (seg: which one), and every frame of it solved onto it -- `move` the plan in play (kept after the end: held)
  const stance = createStance(rig);
  let seg = -1, move = null, moveE = 0;
  // a position that says where the hands go is solved on THIS body, once (reach.js)
  const solved = new WeakMap();
  const onBody = (a) => { if (!a?.reach) return a; if (!solved.has(a)) solved.set(a, reachPosition(rig, a)); return solved.get(a); };
  const onBodyAll = (tl) => { for (const s of tl.segs) if (s.to) s.to = onBody(s.to); return tl; };
  const self = {
    rig, fix, target: null, broken: [],
    get info() { return info; },
    get angles() { return held; },
    get move() { return move; },   // (the move in play: its stance plan -- what each foot and hand does)
    // hold a position (no transition)
    hold(name) { tl = null; held = onBody(typeof name === "string" ? lib.position(name) : name); info = typeof name === "string" ? name : "held"; reachDemo = null; self.target = null;
                 move = null; stance.hold(held); },
    // play an exercise or a movement from the position held now
    play(name, { loop: lp = true } = {}) { tl = onBodyAll(typeof name === "string" ? lib.timeline(name) : name); t = 0; seg = -1; loop = lp; from = copyAngles(held); reachDemo = null; self.target = null; },
    // the hand to a point (world), along a straight line; then hold there
    reach(target, opts = {}) {
      const plan = planReach(rig, held, target, opts);
      tl = { name: "reach", segs: [{ path: plan.keys, time: plan.time, hold: opts.hold ?? .6, label: `reach ${plan.side}${plan.miss > .01 ? ` (short by ${(plan.miss * 100).toFixed(0)} cm)` : ""}` }] };
      t = 0; seg = -1; loop = false; from = copyAngles(held); self.target = target.clone();
      return plan;
    },
    // REACHING, OVER AND OVER: points round the body in the model's cone (reach.cone), one after another
    reachAround(seed = 1) {
      reachDemo = { rnd: mulberry(seed), back: false };
      next();
    },
    stop() { tl = null; reachDemo = null; releaseRig(rig); },
    update(dt) {
      if (tl) {
        t += dt;
        let t0 = 0, prev = from, a = null;
        for (let k = 0; k < tl.segs.length; k++) {
          const s = tl.segs[k], end = t0 + s.time + (s.hold ?? 0);
          if (t < end) {
            if (k !== seg) { seg = k; move = stance.plan(s.path ? s.path[s.path.length - 1] : s.to, { hop: s.hop }); }   // (a new move begins: planned from where the body is)
            const u = Math.min(1, (t - t0) / Math.max(s.time, 1e-3)), e = minJerk(u);
            if (s.path) {   // a reach: along its solved keys
              const x = e * (s.path.length - 1), i = Math.min(s.path.length - 2, Math.floor(x));
              a = blendAngles(s.path[i], s.path[i + 1], x - i, scratch);
            } else a = blendAngles(prev, s.to, e, scratch);
            moveE = e; info = s.label;
            break;
          }
          t0 = end; prev = s.path ? s.path[s.path.length - 1] : s.to;
        }
        if (!a) {   // the timeline done: loop it, or hold where it ended (the last move's end)
          held = copyAngles(prev); moveE = 1;
          if (reachDemo) next();
          else if (loop) { t = 0; seg = -1; from = copyAngles(held); }
          else tl = null;
        } else held = copyAngles(a);
      }
      // the figure posed: a move's frame over the stance (the body's rules put right on it, `fix`), or a position held
      const pose = (ang) => { if (move) stance.frame(move, moveE, ang); else { setAngles(rig, ang); ground(rig); } };
      if (self.fix) { const r = fixBody(rig, copyAngles(held), { pose }); self.broken = r.broken; }
      else { pose(copyAngles(held)); self.broken = checkBody(rig); }
    },
  };
  // the reach demo's next point: anywhere in the cone round the figure's forward from its shoulders' middle, out to a
  // share of the arm's length (past 1: the trunk must lean); every other reach back to rest
  function next() {
    const d = reachDemo;
    if (d.back) { d.back = false; tl = { name: "rest", segs: [{ to: restAngles(), time: .9, hold: .3, label: "back to rest" }] }; t = 0; seg = -1; from = copyAngles(held); self.target = null; return; }
    const cone = MODEL.reach.cone, arm = armOf(rig, "right");
    setAngles(rig, restAngles()); ground(rig);
    const sh = new THREE.Vector3().fromArray(rig.ends.A, rig.index.get("armL") * 3).add(new THREE.Vector3().fromArray(rig.ends.A, rig.index.get("armR") * 3)).multiplyScalar(.5);
    setAngles(rig, held); ground(rig);
    const fwd = new THREE.Vector3(Math.cos(rig.rotY0), 0, -Math.sin(rig.rotY0));
    const off = Math.acos(1 - d.rnd() * (1 - Math.cos(cone.angle * Math.PI / 180))), round = d.rnd() * Math.PI * 2;
    const up = new THREE.Vector3(0, 1, 0), side = new THREE.Vector3().crossVectors(fwd, up);
    const dir = fwd.clone().multiplyScalar(Math.cos(off)).addScaledVector(up, Math.sin(off) * Math.sin(round)).addScaledVector(side, Math.sin(off) * Math.cos(round));
    const dist = (cone.near + d.rnd() * (cone.far - cone.near)) * (arm.L1 + arm.L2);
    const target = sh.addScaledVector(dir, dist);
    target.y = Math.max(.1, target.y);
    self.reach(target, { hold: .5 });
    reachDemo = d; d.back = true;
  }
  return self;
}

function mulberry(seed) { let a = seed >>> 0; return () => { a = (a + 0x6d2b79f5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

export { palm };
