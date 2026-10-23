// THE BODY'S OWN RULES: a position must not put a limb through the trunk, through the head, or through another limb
// (assets/people/joints.json `collision`, docs/motion.md).
//
// Every part is tested as what it is drawn as: a round cone between its two ends -- the trunk's cuts flattened front
// to back, so they are tested in a space stretched along the trunk's forward until they are round. Two parts may
// TOUCH (a hand on a thigh, the forearms crossed) but not sink into each other deeper than the tolerance; a part is
// tested only from `skip` of its length away from the joint it hangs on, where it always meets its neighbour.
//   checkBody(rig)            -> the rules a position breaks: [{ a, b, depth }] (part ids, metres)
//   fixBody(rig, angles)      -> the position put right by the joint model's `fix` steps (an arm taken out of the trunk
//                                to the side...), and what is still broken
import * as THREE from "three";
import { MODEL, setAngles, ground, endA, endB, jointAt, radii, clampAngles } from "./joints.js";

// (read from the model at each use: the asset viewer may have handed it a new one)
let RULES = MODEL.collision;

// the pairs this figure is tested for, built once per rig: [{ a, b }] of { i, id, base, group, side }
function pairsOf(rig) {
  if (rig.pairs) return rig.pairs;
  const SIDE_OF = Object.fromEntries(Object.entries(MODEL.sides).map(([side, { tag }]) => [tag, side]));   // "L" -> "right"
  const GROUP_OF = Object.fromEntries(Object.entries(RULES.groups).flatMap(([g, bases]) => bases.map((b) => [b, g])));
  const parts = rig.def.parts.flatMap((p, i) => {
    const m = /^(arm|fore|hand|leg|shin|foot)([LR])$/.exec(p.id), base = m ? m[1] : p.id;
    const group = GROUP_OF[base];
    return group && !p.bone ? [{ i, id: p.id, base, group, side: m ? SIDE_OF[m[2]] : null }] : [];
  });
  const seen = new Set(), out = [];
  for (const [g1, g2raw] of RULES.pairs) {
    const other = g2raw.endsWith("*"), g2 = g2raw.replace("*", "");
    for (const p of parts) if (p.group === g1) for (const q of parts) if (q.group === g2 && q !== p) {
      if (other && !(p.side && q.side && p.side !== q.side)) continue;
      const key = Math.min(p.i, q.i) + ":" + Math.max(p.i, q.i);
      if (seen.has(key)) continue;
      seen.add(key);
      out.push({ a: p, b: q });
    }
  }
  return (rig.pairs = out);
}

// closest points of two segments p1-q1, p2-q2: their parameters s, t (Ericson, Real-Time Collision Detection 5.1.9)
const _d1 = new THREE.Vector3(), _d2 = new THREE.Vector3(), _r = new THREE.Vector3();
function closest(p1, q1, p2, q2) {
  _d1.subVectors(q1, p1); _d2.subVectors(q2, p2); _r.subVectors(p1, p2);
  const a = _d1.dot(_d1), e = _d2.dot(_d2), f = _d2.dot(_r);
  let s, t;
  if (a < 1e-12 && e < 1e-12) return [0, 0];
  if (a < 1e-12) return [0, Math.min(1, Math.max(0, f / e))];
  const c = _d1.dot(_r);
  if (e < 1e-12) return [Math.min(1, Math.max(0, -c / a)), 0];
  const b = _d1.dot(_d2), den = a * e - b * b;
  s = den > 1e-12 ? Math.min(1, Math.max(0, (b * f - c * e) / den)) : 0;
  t = (b * s + f) / e;
  if (t < 0) { t = 0; s = Math.min(1, Math.max(0, -c / a)); }
  else if (t > 1) { t = 1; s = Math.min(1, Math.max(0, (b - c) / a)); }
  return [s, t];
}

// a part as a tested segment: its ends with the end at its own joint drawn in by `skip` of its length
const _j = new THREE.Vector3();
function segment(rig, p, A, B) {
  endA(rig, p.i, A); endB(rig, p.i, B);
  let [r1, r2] = radii(rig, p.i);
  const skip = RULES.skip[p.base] ?? 0;
  if (skip > 0) {
    jointAt(rig, p.i, _j);
    const atA = A.distanceToSquared(_j) <= B.distanceToSquared(_j);
    if (atA) { A.lerp(B, skip); r1 = r1 + (r2 - r1) * skip; } else { B.lerp(A, skip); r2 = r2 + (r1 - r2) * skip; }
  }
  return [r1, r2];
}

// a flat part's space: stretched along its forward (its frame's x) by 1/flat about its A end, where it is round
function unflatten(rig, i, pts) {
  const fl = rig.flat[i];
  if (!fl) return 1;
  const f = new THREE.Vector3().setFromMatrixColumn(rig.frames[i], 0).normalize(), o = endA(rig, i, new THREE.Vector3());
  for (const v of pts) v.addScaledVector(f, (v.clone().sub(o).dot(f)) * (1 / fl - 1));
  return 1 / fl;
}

const _A1 = new THREE.Vector3(), _B1 = new THREE.Vector3(), _A2 = new THREE.Vector3(), _B2 = new THREE.Vector3(), _c1 = new THREE.Vector3(), _c2 = new THREE.Vector3();
export function checkBody(rig, { tolerance } = {}) {
  RULES = MODEL.collision; tolerance ??= RULES.tolerance;
  const out = [];
  for (const { a, b } of pairsOf(rig)) {
    const [ra1, ra2] = segment(rig, a, _A1, _B1), [rb1, rb2] = segment(rig, b, _A2, _B2);
    // (a trunk part: both segments taken into the space where it is round; the limb's radius grows by as much as the stretch where it faces it)
    const flatOne = rig.flat[b.i] ? b : rig.flat[a.i] ? a : null;
    const k = flatOne ? unflatten(rig, flatOne.i, [_A1, _B1, _A2, _B2]) : 1;
    const [s, t] = closest(_A1, _B1, _A2, _B2);
    _c1.lerpVectors(_A1, _B1, s); _c2.lerpVectors(_A2, _B2, t);
    const d = _c1.distanceTo(_c2);
    let rA = ra1 + (ra2 - ra1) * s, rB = rb1 + (rb2 - rb1) * t;
    if (flatOne) {   // the limb's own radius, seen in the stretched space: longer where it faces the trunk's front
      const f = new THREE.Vector3().setFromMatrixColumn(rig.frames[flatOne.i], 0).normalize(), n = _c2.clone().sub(_c1).normalize();
      const grow = 1 + (k - 1) * Math.abs(n.dot(f));
      if (flatOne === b) rA *= grow; else rB *= grow;
    }
    const depth = rA + rB - d;
    if (depth > tolerance) out.push({ a: a.id, b: b.id, depth, parts: [a, b] });
  }
  return out;
}

// PUT RIGHT: the angles nudged by the model's fix steps until no rule is broken (or the steps run out); the rig left
// holding the result. Returns { angles, broken }
// (`pose`: how the angles are put on the figure -- by default held where it stands, ground(); the player passes its
//  stance's frame, so the fix works on the body as it moves)
export function fixBody(rig, angles, { maxSteps = 30, pose = (a) => { setAngles(rig, a); ground(rig); } } = {}) {
  pose(angles);
  let broken = checkBody(rig);
  const used = new Map();   // how far each fix has gone
  for (let n = 0; n < maxSteps && broken.length; n++) {
    let moved = false;
    const nudged = new Set();   // (a joint's movement nudged once a step, however many rules its part breaks)
    for (const v of broken) for (const part of v.parts) {   // (both parts of a pair that have a fix -- two legs through each other both move)
      for (const f of RULES.fix[part.group] ?? []) {
        const key = part.side ? `${part.side}.${f.joint}` : f.joint, uk = key + "/" + f.movement;
        const done = used.get(uk) ?? 0;
        if (Math.abs(done) >= f.max || !angles.joints[key]) continue;
        if (!nudged.has(uk)) { angles.joints[key][f.movement] += f.step; used.set(uk, done + f.step); nudged.add(uk); moved = true; }
        break;   // (one nudge per broken part per step)
      }
    }
    if (!moved) break;
    clampAngles(angles);
    pose(angles);
    broken = checkBody(rig);
  }
  return { angles, broken };
}
