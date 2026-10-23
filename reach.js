// REACHING: a hand taken to a point in space (assets/people/joints.json `reach`, docs/motion.md).
//
// THE TRIANGLE. The upper arm (shoulder to elbow) and the forearm with the hand (elbow to the middle of the palm) are
// two sides of a triangle whose third runs from the shoulder to the point. Its length fixes how far the elbow bends
// (the law of cosines); the elbow itself may stand anywhere round a circle about that third side -- the SWIVEL. Which
// point of the circle a person uses is a matter of preference, weighed as a cost:
//   the elbow hanging down and a little out (the model's `swivel`), as an arm does by its own weight;
//   the arm raised forward rather than out to the side (above `abductionFree` the shoulder blade must turn);
//   never behind the body when the front will do (extension); the arm not twisted (rotation);
//   every joint inside its range; nothing through the body (bodycheck.js); and, moving, no jump from the last swivel.
// A point beyond the arm's reach is reached by leaning: the trunk bends, turns and tips toward it (`lean`), at its
// own cost, until the hand gets there or as near as it can.
//   solveReach(rig, side, target, base)   -> { angles, side, miss, cost }: the position with the hand at target
//   planReach(rig, from, target, opts)     -> { keys: [angles...], side, target }: the hand along a straight line
//                                             from where it is to the point, each step solved (motion.js plays it)
import * as THREE from "three";
import { MODEL, copyAngles, blendAngles, setAngles, ground, jointAt, endA, endB, clampAngles, limbOf, tipOf, midCircle, limbAngles, limbBase } from "./joints.js";
import { checkBody } from "./bodycheck.js";

const RAD = Math.PI / 180, DEG = 180 / Math.PI;
// (the model read at each reach -- the asset viewer may have handed it a new one)
let R, C, SHOULDER;
function model() { R = MODEL.reach; C = R.cost; SHOULDER = MODEL.joints.shoulder.movements; }
model();

// the arm as a limb (joints.js: its parts, the upper arm's length and the forearm-with-hand's to the palm)
const armOf = (rig, side) => limbOf(rig, side, "arm");
const palm = (rig, arm, out) => tipOf(rig, arm, out);
const _t = new THREE.Vector3();

// THE ARM to a point, the trunk as `base` holds it: every swivel round the circle priced, the best few posed and
// checked against the body, the cheapest kept
function solveArm(rig, arm, target, base, prevSwivel) {
  setAngles(rig, base); ground(rig);
  const { S, Qp } = limbBase(rig, arm), c = midCircle(S, target, arm.L1, arm.L2);
  // the circle's frame: e1 straight down (the trunk's down) square to the third side, e2 round it outward
  const down = new THREE.Vector3(0, -1, 0).applyQuaternion(Qp), out = new THREE.Vector3(0, 0, arm.s).applyQuaternion(Qp);
  let e1 = down.clone().addScaledVector(c.n, -down.dot(c.n));
  if (e1.lengthSq() < 1e-6) { const back = new THREE.Vector3(-1, 0, 0).applyQuaternion(Qp); e1 = back.addScaledVector(c.n, -back.dot(c.n)); }
  e1.normalize();
  const e2 = new THREE.Vector3().crossVectors(c.n, e1);
  if (e2.dot(out) < 0) e2.negate();
  const key = arm.root, ek = arm.mid, sh = SHOULDER, free = R.abductionFree * RAD, el = MODEL.joints.elbow.movements.flexion;
  const cands = [];
  for (let k = -24; k < 24; k++) {
    const phi = k * 7.5 * RAD, E = c.C.clone().addScaledVector(e1, c.h * Math.cos(phi)).addScaledVector(e2, c.h * Math.sin(phi));
    const ang = limbAngles(arm, S, E, c.tip, Qp), vals = ang.root;
    const flex = vals.flexion * RAD, abd = vals.abduction * RAD, rot = vals.rotation * RAD, sw = phi - R.swivel * RAD;
    let cost = C.swivel * sw * sw + C.abductionOver * Math.max(0, abd - free) ** 2 + C.extension * Math.max(0, -flex) ** 2 + C.rotation * rot * rot;
    if (prevSwivel !== undefined) cost += 2 * C.swivel * (phi - prevSwivel) ** 2;
    for (const [mv, v] of Object.entries(vals)) cost += C.limit * Math.max(0, sh[mv].min - v, v - sh[mv].max) * RAD;
    cost += C.limit * Math.max(0, el.min - ang.mid, ang.mid - el.max) * RAD;
    cands.push({ phi, cost, vals, elbow: ang.mid });
  }
  cands.sort((x, y) => x.cost - y.cost);
  // the best few, posed: what the ranges leave of them, what they put through the body, how far the hand still is
  let best = null;
  for (const c of cands.slice(0, 6)) {
    const ang = copyAngles(base);
    Object.assign(ang.joints[key], c.vals); ang.joints[ek].flexion = c.elbow; ang.joints[arm.end].flexion = 0;
    clampAngles(ang);
    setAngles(rig, ang); ground(rig);
    const miss = palm(rig, arm, _t).distanceTo(target);
    // (everything it puts through the body: the arm through the trunk, or -- leaning, bowing -- the trunk onto the shins)
    const hits = checkBody(rig);
    const total = c.cost + C.miss * miss + C.collision * hits.reduce((t, v) => t + v.depth, 0);
    if (!best || total < best.cost) best = { angles: ang, cost: total, miss, swivel: c.phi, hits };
  }
  return best;
}
// which arm: the one on the point's side of the body (its shoulder nearer)
function sideFor(rig, target) {
  const r = armOf(rig, "right"), l = armOf(rig, "left");
  ground(rig);
  return jointAt(rig, r.i0, new THREE.Vector3()).distanceTo(target) <= jointAt(rig, l.i0, new THREE.Vector3()).distanceTo(target) ? "right" : "left";
}

// THE REACH: the arm alone if it gets there; else the trunk leaning toward the point, the cheapest lean that does
// (`symmetric`: both hands will reach, the other arm the mirror of this one -- the trunk only bends forward, never turns)
export function solveReach(rig, side, target, base, { prevSwivel, lean = true, symmetric = false } = {}) {
  model();
  if (!side || side === "auto") { setAngles(rig, base); side = sideFor(rig, target); }
  const arm = armOf(rig, side);
  let best = solveArm(rig, arm, target, base, prevSwivel);
  const L = R.lean, lean2 = (b, fl, ro, la) => {   // the trunk on top of a body `b`: bent, turned, tipped -- priced
    const c = copyAngles(b);
    c.joints.spine.flexion += fl; c.joints.spine.rotation += ro; c.joints.spine.lateral += la;
    clampAngles(c);
    const s = solveArm(rig, arm, target, c, prevSwivel);
    s.cost += C.lean * ((fl * RAD) ** 2 + (ro * RAD) ** 2 + (la * RAD) ** 2) + (b.leanCost ?? 0);
    if (s.cost < best.cost) best = s;
  };
  if (lean === "spine" && (best.miss > .01 || best.hits.length)) {   // (the trunk's forward bend alone, 0 out to its range)
    for (let fl = L.step; fl <= L.flexion[1] + 1e-6; fl += L.step) lean2(base, fl, 0, 0);
  } else if (lean === true && (best.miss > .01 || best.hits.length)) {
    // (each range tried from 0 out both ways, a step at a time: 0, 15, -15, 30...)
    const steps = ([lo, hi]) => { const out = [0]; for (let v = L.step; v <= Math.max(hi, -lo) + 1e-6; v += L.step) { if (v <= hi) out.push(v); if (-v >= lo) out.push(-v); } return out; };
    const sideways = (r) => (symmetric ? [0] : steps(r));
    for (const fl of steps(L.flexion)) for (const ro of sideways(L.rotation)) for (const la of sideways(L.lateral)) if (fl || ro || la) lean2(base, fl, ro, la);
    // still short, and low: crouch and bow, the trunk bending on top (fewer of its steps: the legs do the work)
    if (best.miss > .01 && L.crouch) {
      for (const share of [0, ...L.crouch.shares]) for (const bow of [0, ...(L.bow?.angles ?? [])]) {
        if (!share && !bow) continue;
        const b = copyAngles(base);
        for (const side of Object.keys(MODEL.sides)) for (const [j, mvs] of Object.entries(L.crouch.joints)) for (const [mv, v] of Object.entries(mvs))
          b.joints[`${side}.${j}`][mv] += (v - b.joints[`${side}.${j}`][mv]) * share;
        b.root.pitch -= bow; for (const side of Object.keys(MODEL.sides)) b.joints[`${side}.hip`].flexion += bow;
        b.leanCost = L.crouch.cost * share * share + (L.bow?.cost ?? 1) * (bow * RAD) ** 2;
        for (const fl of steps(L.flexion)) for (const ro of symmetric ? [0] : [0, -30, 30]) lean2(b, fl, ro, 0);
      }
    }
  }
  setAngles(rig, best.angles); ground(rig);
  return { ...best, side };
}

// THE MOVEMENT: the hand from where it is to the point along a straight line (as people move their hands), each of
// `steps` points on it solved from the last -- the trunk easing into its lean on the way -- so the swivel turns
// smoothly instead of jumping; motion.js plays the keys along a minimum-jerk clock
export function planReach(rig, from, target, { side = "auto", steps = 6 } = {}) {
  const end = solveReach(rig, side, target, from);
  const arm = armOf(rig, end.side);
  setAngles(rig, from); ground(rig);
  const start = palm(rig, arm, new THREE.Vector3()), keys = [copyAngles(from)];
  let prev;
  for (let k = 1; k < steps; k++) {
    const u = k / steps, p = start.clone().lerp(target, u);
    const trunk = blendAngles(from, end.angles, u);   // (the lean grows on the way; the other arm stays as it was)
    const otherSide = end.side === "right" ? "left" : "right";
    for (const j of ["shoulder", "elbow", "wrist"]) trunk.joints[`${otherSide}.${j}`] = { ...from.joints[`${otherSide}.${j}`] };
    const s = solveArm(rig, arm, p, trunk, prev);
    prev = s.swivel; keys.push(s.angles);
  }
  keys.push(end.angles);
  setAngles(rig, from); ground(rig);
  const dist = start.distanceTo(target);
  return { keys, side: end.side, target: target.clone(), miss: end.miss, time: R.speed.base + R.speed.perMetre * dist };
}

// A POSITION THAT SAYS WHERE THE HANDS GO (positions.json `reach`: { "hands": "toes" }) solved on this body -- its
// proportions decide how far it must bend. `hands`: both, the left arm the mirror of the right (the trunk bending
// straight forward); `right hand` / `left hand`: one. Places: `toes` (just over and before the tip of that side's
// foot), `knees` (before them), `floor` (on the floor just ahead of the shoulder: hands put down to get onto them)
const fwdOf = (rig) => new THREE.Vector3(Math.cos(rig.rotY0), 0, -Math.sin(rig.rotY0));
const outOf = (rig, side) => new THREE.Vector3(0, 1, 0).cross(fwdOf(rig)).multiplyScalar(-MODEL.sides[side].s);   // (the side's own outward)
const PLACES = {
  toes: (rig, side) => {   // the foot's forward end (along the figure's forward), a little above and before it
    const i = rig.index.get("foot" + MODEL.sides[side].tag), a = endA(rig, i), b = endB(rig, i), f = fwdOf(rig);
    return (a.dot(f) > b.dot(f) ? a : b).add(new THREE.Vector3(0, .1, 0)).addScaledVector(f, .05);   // (the palm's middle: the fingertips then just on the toes)
  },
  knees: (rig, side) => jointAt(rig, rig.index.get("shin" + MODEL.sides[side].tag)).addScaledVector(fwdOf(rig), .08),
  floor: (rig, side) => jointAt(rig, rig.index.get("arm" + MODEL.sides[side].tag)).addScaledVector(fwdOf(rig), .2).addScaledVector(outOf(rig, side), .03).setY(rig.floor + .05),   // (a little wider than the shoulder: where a push-up wants them)
};
export function reachPosition(rig, a) {
  let out = copyAngles(a);
  for (const [who, place] of Object.entries(a.reach)) {
    const where = PLACES[place];
    if (!where) throw new Error(`position: no place "${place}" to reach (${Object.keys(PLACES).join(", ")})`);
    setAngles(rig, out); ground(rig);
    const sides = who === "hands" ? ["right"] : [who.split(" ")[0]];
    // (`lean` on the position: what else may move to get there -- true everything, "spine" the trunk's bend alone,
    //  false the arms alone, as the position holds the body)
    for (const side of sides) {
      const r = solveReach(rig, side, where(rig, side), out, { symmetric: who === "hands", lean: a.reachLean ?? true });
      out = r.angles;
    }
    if (who === "hands") for (const j of ["shoulder", "elbow", "wrist"]) out.joints[`left.${j}`] = { ...out.joints[`right.${j}`] };
  }
  out.reach = null;
  setAngles(rig, out); ground(rig);
  return out;
}

export { armOf, palm };
