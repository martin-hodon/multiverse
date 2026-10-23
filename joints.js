// THE JOINTS: a person as parts that turn in joints (assets/people/joints.json, docs/motion.md).
//
// A joint is the frame of the part it moves (the shoulder turns the upper arm); each of its movements turns that
// part about one axis of its parent's frame, by an angle in degrees with a range. A POSITION is every joint's
// angles, plus how the whole body lies (`root`: pitch, roll, yaw) and what it stands on (`anchor`). Here:
//   angles      a full set of a position's angles, in the joint model's own names, and the arithmetic on them
//               (rest, read a position, mirror, blend, clamp to the ranges)
//   a RIG       one figure of the composite engine with the joint model on it: angles -> each part's rotation
//               (an.pose, read by skeleton.js writeAnimal), its parts' frames posed (fk), and the body set on
//               the ground (ground)
import * as THREE from "three";
import { JOINTS, BODY } from "./people.js";
import { writeAnimal, lastFrames, DRAPE } from "./skeleton.js";

export const MODEL = { ...JOINTS };
const RAD = Math.PI / 180;

// every joint of the body once per side: { key: "right.shoulder", joint, side, s, part (the rig's part id), def }
export const JOINT_LIST = [];
// THE MODEL IN USE: the file's, or one being edited (the asset viewer hands it the text in its editor)
export function setJointModel(def) {
  for (const k of Object.keys(MODEL)) delete MODEL[k];
  Object.assign(MODEL, def);
  JOINT_LIST.length = 0;
  for (const [name, d] of Object.entries(MODEL.joints)) {
    if (d.sided) for (const [side, { tag, s }] of Object.entries(MODEL.sides)) JOINT_LIST.push({ key: `${side}.${name}`, joint: name, side, s, part: d.part + tag, def: d });
    else JOINT_LIST.push({ key: name, joint: name, side: null, s: 1, part: d.part, def: d });
  }
}
setJointModel(JOINTS);

// a joint's rest: its own (or 0), a "body:<path>" read from the human canon
const restOf = (def, mv) => {
  const v = def.rest?.[mv] ?? 0;
  return typeof v === "string" && v.startsWith("body:") ? v.slice(5).split(".").reduce((o, k) => o?.[k], BODY) ?? 0 : v;
};

// ---- ANGLES: { joints: { [key]: { [movement]: degrees } }, root: { pitch, roll, yaw, lift }, anchor, support }
//   anchor   what keeps its place on the ground (feet, right foot, left foot, hands, knees, pelvis)
//   support  two things the body rests on at once (["forearms", "feet"]: a plank) -- the body's tilt (root pitch) is
//            found so that both touch the ground; supportW how much of that tilt is taken (a transition into it)

export function restAngles() {
  const joints = {};
  for (const j of JOINT_LIST) joints[j.key] = Object.fromEntries(Object.keys(j.def.movements).map((mv) => [mv, restOf(j.def, mv)]));
  return { joints, root: { pitch: 0, roll: 0, yaw: 0, lift: 0 }, anchor: "feet", support: null, supportW: 0 };
}

export const copyAngles = (a) => ({ joints: Object.fromEntries(Object.entries(a.joints).map(([k, v]) => [k, { ...v }])), root: { ...a.root },
                                    anchor: a.anchor, anchors: a.anchors ?? null, support: a.support ?? null, supportW: a.supportW ?? 0 });

// A POSITION as written (assets/people/positions.json): joints named `spine`, `neck`, or `<side> <joint>` with side
// right, left or both ("both shoulders" / "both shoulder"); movements not named keep the base's (the rest)
export function readPosition(pos, base = restAngles()) {
  const a = copyAngles(base);
  for (const [name, mvs] of Object.entries(pos.joints ?? {})) {
    const [w1, w2] = name.trim().split(/\s+/), w = w2 ?? w1;
    const joint = MODEL.joints[w] ? w : w.slice(0, -1);   // ("both knees": the knee)
    const keys = !w2 ? [joint] : w1 === "both" ? [`right.${joint}`, `left.${joint}`] : [`${w1}.${joint}`];
    for (const key of keys) {
      if (!a.joints[key]) throw new Error(`position: no joint "${name}" (${key})`);
      for (const [mv, v] of Object.entries(mvs)) {
        if (!(mv in a.joints[key])) throw new Error(`position: the ${key} has no movement "${mv}" (${Object.keys(a.joints[key]).join(", ")})`);
        a.joints[key][mv] = v;
      }
    }
  }
  if (pos.root) Object.assign(a.root, pos.root);
  if (pos.anchor) a.anchor = pos.anchor;
  if (pos.support) { a.support = pos.support; a.supportW = 1; }
  a.reach = pos.reach ?? null;   // (where the hands go, solved on each body: reach.js reachPosition)
  a.reachLean = pos.lean ?? true;
  return a;
}

// THE MIRROR IMAGE: right and left swapped; the trunk's and the head's sideways movements, and the body's own roll and
// yaw, turned the other way (a lunge on the right leg -> on the left)
const MIRRORED = new Set(["lateral", "rotation"]);
export function mirrorAngles(a) {
  const m = copyAngles(a);
  for (const j of JOINT_LIST) {
    if (j.side) m.joints[j.key] = { ...a.joints[`${j.side === "right" ? "left" : "right"}.${j.joint}`] };
    else for (const mv of Object.keys(m.joints[j.key])) if (MIRRORED.has(mv)) m.joints[j.key][mv] = -a.joints[j.key][mv];
  }
  m.root.roll = -a.root.roll; m.root.yaw = -a.root.yaw;
  const swap = (nm) => nm.replace(/right|left/, (w) => (w === "right" ? "left" : "right"));
  m.anchor = swap(a.anchor);
  if (a.support) m.support = a.support.map(swap);
  return m;
}

// between two positions: each angle a share u of the way (u already eased by the caller); the anchor of the nearer
export function blendAngles(a, b, u, out = copyAngles(a)) {
  for (const k in a.joints) for (const mv in a.joints[k]) out.joints[k][mv] = a.joints[k][mv] + (b.joints[k][mv] - a.joints[k][mv]) * u;
  for (const k in a.root) out.root[k] = a.root[k] + ((b.root[k] ?? 0) - a.root[k]) * u;
  out.anchor = u < .5 ? a.anchor : b.anchor;
  out.anchors = a.anchor === b.anchor ? null : [[a.anchor, 1 - u], [b.anchor, u]];   // (two anchors: the ground's hold slides from one to the other)
  // (a support held at one end only: its tilt taken in step with the way there)
  out.support = b.support ?? a.support ?? null;
  out.supportW = a.support && b.support ? 1 : b.support ? u : a.support ? 1 - u : 0;
  return out;
}

// every movement inside its range: the angles clamped, and what was out of it
export function clampAngles(a) {
  const out = [];
  for (const j of JOINT_LIST) for (const [mv, d] of Object.entries(j.def.movements)) {
    const v = a.joints[j.key][mv];
    if (v < d.min - 1e-6 || v > d.max + 1e-6) { out.push({ key: j.key, movement: mv, value: v, min: d.min, max: d.max }); a.joints[j.key][mv] = Math.min(d.max, Math.max(d.min, v)); }
  }
  return out;
}

// a joint's rotation in its parent's frame: its movements in order, each about its axis (the first turns the rest)
const _q = new THREE.Quaternion(), AXES = { x: new THREE.Vector3(1, 0, 0), y: new THREE.Vector3(0, 1, 0), z: new THREE.Vector3(0, 0, 1) };
export function jointQuat(j, mvs, out = new THREE.Quaternion()) {
  out.identity();
  for (const [mv, d] of Object.entries(j.def.movements)) {
    const sign = d.sign * (d.sided ? j.s : 1);
    out.multiply(_q.setFromAxisAngle(AXES[d.axis], (mvs[mv] ?? 0) * sign * RAD));
  }
  return out;
}

// ---- A RIG: the joint model on one figure (an: a composite herd's animal; def: the makePerson definition it came from)

export function attachRig(an, def) {
  const index = new Map(def.parts.map((p, i) => [p.id, i]));
  const joints = JOINT_LIST.filter((j) => index.has(j.part)).map((j) => {
    const piv = j.def.pivot ? def.motion?.pivots?.[j.def.pivot] : null;
    return { ...j, idx: index.get(j.part), held: { q: new THREE.Quaternion(), c: piv ? new THREE.Vector3(...piv) : null } };
  });
  const skirts = (def.motion?.skirts ?? []).filter((id) => index.has(id)).map((id) => ({ idx: index.get(id), held: { q: new THREE.Quaternion(), c: null } }));
  const rig = { an, def, index, joints, skirts, rotY0: an.rotY, floor: an.position.y, home: an.position.clone(), angles: restAngles(), anchorRest: null, t: 0,
                ends: { A: new Float32Array(an.parts.length * 3), B: new Float32Array(an.parts.length * 3), C: new Float32Array(an.parts.length * 3) },
                frames: an.parts.map(() => new THREE.Matrix4()) };
  // (a figure's BODY, what it rests on the ground with: its limbs and trunk, not a skirt's hem or a hat)
  const BODY_PARTS = /^(pelvis|chest|belly|hips|neck|head|(arm|fore|hand|leg|shin|foot)[LR])$/;
  rig.body = def.parts.flatMap((p, i) => BODY_PARTS.test(p.id) && !p.bone ? [i] : []);
  rig.flat = def.parts.map((p) => p.flat ?? 0);
  // where each anchor stands at rest, from the figure's position (before anything is held or the body turned)
  an.pose = null; fk(rig);
  rig.anchorRest = Object.fromEntries(ANCHORS.map((nm) => [nm, anchorPoint(rig, nm, new THREE.Vector3()).sub(an.position)]));
  an.pose = an.parts.map(() => null);
  return rig;
}
const ANCHORS = ["feet", "right foot", "left foot", "hands", "knees", "pelvis"];

// the angles onto the figure: each joint's part held in its rotation, a skirt draped over the thighs as they rise
// (skeleton.js DRAPE, as the gait drapes it), the body turned as a whole (root) -- then fk/ground
export function setAngles(rig, a) {
  rig.angles = a;
  const an = rig.an;
  for (const j of rig.joints) { jointQuat(j, a.joints[j.key], j.held.q); an.pose[j.idx] = j.held; }
  if (rig.skirts.length) {   // a skirt hangs from the hips and is carried forward by the thighs under it
    const lift = Math.min(DRAPE.max, DRAPE.k * Math.max(0, (a.joints["right.hip"].flexion + a.joints["left.hip"].flexion) / 2));
    for (const sk of rig.skirts) { sk.held.q.setFromAxisAngle(AXES.z, lift * RAD); an.pose[sk.idx] = sk.held; }
  }
  an.pitch = (a.root.pitch ?? 0) * RAD; an.roll = (a.root.roll ?? 0) * RAD; an.rotY = rig.rotY0 + (a.root.yaw ?? 0) * RAD;
  an.amp = an.ampT = 0;   // (no gait under a held position: no bob, no stride)
}

export function releaseRig(rig) {
  const an = rig.an;
  an.pose = null; an.pitch = 0; an.roll = 0; an.rotY = rig.rotY0; an.position.copy(rig.home);
}

// THE PARTS POSED: every part's two ends and its frame, through the skeleton's own pose (writeAnimal, on a stand-in
// that keeps the figure's state untouched) -- the same numbers the engine draws
export function fk(rig) {
  const an = rig.an, proxy = Object.create(an);
  proxy.base = 0; proxy.hidden = false;
  writeAnimal(proxy, rig.t, rig.ends.A, rig.ends.B, rig.ends.C);
  const m = lastFrames();
  for (let i = 0; i < rig.frames.length; i++) rig.frames[i].copy(m[i]);
  return rig;
}

// a part's ends and joint (its frame's origin), from the last fk
export const endA = (rig, i, out = new THREE.Vector3()) => out.fromArray(rig.ends.A, i * 3);
export const endB = (rig, i, out = new THREE.Vector3()) => out.fromArray(rig.ends.B, i * 3);
export const jointAt = (rig, i, out = new THREE.Vector3()) => out.setFromMatrixPosition(rig.frames[i]);
export const radii = (rig, i) => { const p = rig.an.parts[i]; return [p.r1, p.r2 >= 0 ? p.r2 : p.r1]; };

// how far a part reaches down: its ends less their radius -- a flat part (the torso) less only its depth where it faces
// down (its frame's forward: squashed along it to `flat` of its width)
const _f = new THREE.Vector3(), _a = new THREE.Vector3(), _b = new THREE.Vector3();
export function lowest(rig, i) {
  const [r1, r2] = radii(rig, i), fl = rig.flat[i];
  let k = 1;
  if (fl) { _f.setFromMatrixColumn(rig.frames[i], 0).normalize(); k = Math.sqrt(1 - (1 - fl * fl) * _f.y * _f.y); }
  return Math.min(endA(rig, i, _a).y - r1 * k, endB(rig, i, _b).y - r2 * k);
}

// where the body holds its place on the ground: the feet (their middle), one foot, the hands, the pelvis
function anchorPoint(rig, name, out) {
  const ids = name === "feet" ? ["footL", "footR"] : name === "right foot" ? ["footL"] : name === "left foot" ? ["footR"]
    : name === "hands" ? ["handL", "handR"] : name === "knees" ? ["shinL", "shinR"] : ["pelvis"];
  out.set(0, 0, 0);
  let n = 0;
  for (const id of ids) {
    const i = rig.index.get(id);
    if (i === undefined) continue;
    // (a shin's knee end, a foot's or hand's middle, the pelvis's joint)
    if (id.startsWith("shin")) out.add(jointAt(rig, i, _a));
    else if (id === "pelvis") out.add(jointAt(rig, i, _a));
    else out.add(endA(rig, i, _a).add(endB(rig, i, _b)).multiplyScalar(.5));
    n++;
  }
  return n ? out.multiplyScalar(1 / n) : out.copy(rig.an.position);
}

// THE BODY ON THE GROUND: its lowest point on the floor, and the anchor where it was standing (so a squat sinks over
// its feet instead of sliding, and a body laid down keeps its feet where they stood). Posed afresh each frame.
// what a body can rest on (a support): its parts
const SUPPORTS = { feet: ["footL", "footR"], "right foot": ["footL"], "left foot": ["footR"], hands: ["handL", "handR"], forearms: ["foreL", "foreR", "handL", "handR"],
                   knees: ["shinL", "shinR"], pelvis: ["hips"], back: ["chest", "belly", "hips"], head: ["head"] };
const lowestOf = (rig, name) => { let low = Infinity; for (const id of SUPPORTS[name] ?? []) { const i = rig.index.get(id); if (i !== undefined) low = Math.min(low, lowest(rig, i)); } return low; };

// THE TILT that rests the body on both its supports: the root's pitch, bisected between half a right angle either side
// of the position's own until the two touch the ground together (the lower of each at the same height)
function supportTilt(rig) {
  const an = rig.an, [s1, s2] = rig.angles.support, p0 = an.pitch;
  const gap = (p) => { an.pitch = p; fk(rig); return lowestOf(rig, s1) - lowestOf(rig, s2); };
  let lo = p0 - .8, hi = p0 + .8, glo = gap(lo), ghi = gap(hi);
  if (Math.sign(glo) === Math.sign(ghi)) { an.pitch = p0; return; }   // (no tilt rests it on both: as written)
  for (let k = 0; k < 18; k++) { const m = (lo + hi) / 2, gm = gap(m); if (Math.sign(gm) === Math.sign(glo)) { lo = m; glo = gm; } else hi = m; }
  an.pitch = p0 + ((lo + hi) / 2 - p0) * (rig.angles.supportW ?? 1);
}

const _p = new THREE.Vector3(), _r = new THREE.Vector3();
export function ground(rig) {
  const an = rig.an;
  an.position.copy(rig.home);
  if (rig.angles.support && rig.angles.supportW > 0) supportTilt(rig);
  fk(rig);
  // the anchor's drift from where it stood (two anchors in a transition: weighed)
  _r.set(0, 0, 0);
  for (const [nm, w] of rig.angles.anchors ?? [[rig.angles.anchor, 1]]) {
    const rest = rig.anchorRest[nm] ?? rig.anchorRest.feet;
    _r.addScaledVector(anchorPoint(rig, nm, _p).sub(rig.home).sub(rest), w);
  }
  let low = Infinity;
  for (const i of rig.body) low = Math.min(low, lowest(rig, i));
  an.position.set(rig.home.x - _r.x, rig.home.y + (rig.floor - low) + (rig.angles.root.lift ?? 0), rig.home.z - _r.z);
  fk(rig);   // (the frames where the body now stands: what the checks and the reach read)
  return rig;
}

// ---- LIMBS: an arm or a leg as a chain of two bones -- its root joint (three movements), its middle joint (one), its
// end (the wrist, the ankle). What the reach (reach.js) and the stance (stance.js) solve with: one solver for both.
//   the arm's tip is the middle of the palm (the hand held straight), the leg's the ankle (the foot turns about it)
// (`wrist`: the arm to its wrist -- a hand held flat on the floor bends there, so it is solved to the wrist, the palm laid after)
const LIMB_DEF = { arm: { root: "shoulder", mid: "elbow", end: "wrist", parts: ["arm", "fore", "hand"], tip: "palm", point: [0, -1, 0] },
                   wrist: { root: "shoulder", mid: "elbow", end: "wrist", parts: ["arm", "fore", "hand"], tip: "joint", point: [0, -1, 0] },
                   leg: { root: "hip", mid: "knee", end: "ankle", parts: ["leg", "shin", "foot"], tip: "joint", point: [1, 0, 0] } };
const _pb = new THREE.Vector3();
export const tipOf = (rig, limb, out = new THREE.Vector3()) => limb.tip === "palm"
  ? endA(rig, limb.i2, out).add(endB(rig, limb.i2, _pb)).multiplyScalar(.5) : jointAt(rig, limb.i2, out);
export function limbOf(rig, side, kind) {
  rig.limbs ??= {};
  const key = `${side} ${kind}`;
  if (rig.limbs[key]) return rig.limbs[key];
  const d = LIMB_DEF[kind], { tag, s } = MODEL.sides[side];
  const [i0, i1, i2] = d.parts.map((p) => rig.index.get(p + tag));
  const limb = { side, kind, s, i0, i1, i2, parent: rig.index.get(rig.def.parts[i0].parent), tip: d.tip,
                 root: `${side}.${d.root}`, mid: `${side}.${d.mid}`, end: `${side}.${d.end}`,
                 bend: MODEL.joints[d.mid].movements.flexion.sign,   // (which way of its own frame's x the middle joint bends: elbow +, knee -)
                 point: new THREE.Vector3(...d.point) };             // (the end part's own pointing axis: the hand down its length, the foot forward)
  fk(rig);   // (the lengths, whatever the pose: they never change)
  const S = jointAt(rig, i0), E = jointAt(rig, i1);
  limb.L1 = S.distanceTo(E); limb.L2 = tipOf(rig, limb).distanceTo(E);
  return (rig.limbs[key] = limb);
}

// THE MIDDLE JOINT'S CIRCLE: the limb's root at S, its tip wanted at W -- the third side of the limb's triangle runs S->W
// (as long as the limb lets it: `miss` is what is left over); the elbow or knee stands anywhere round the circle (centre
// C, radius h) about it. The law of cosines.
export function midCircle(S, W, L1, L2) {
  const D = W.clone().sub(S), d = D.length(), n = D.divideScalar(d || 1);
  const dd = Math.min(L1 + L2 - 1e-3, Math.max(Math.abs(L1 - L2) + 1e-3, d));
  const a = (L1 * L1 - L2 * L2 + dd * dd) / (2 * dd), h = Math.sqrt(Math.max(0, L1 * L1 - a * a));
  return { n, C: S.clone().addScaledVector(n, a), h, tip: S.clone().addScaledVector(n, dd), miss: Math.max(0, d - dd) };
}

// THE ANGLES that put the limb's root at S, its middle at E and its tip at W (world), its parent's frame turned by Qp:
// the root's three, read back in the model's order (flexion about z, abduction about x, rotation about y -- refused
// otherwise), the middle's one. -> { root: { flexion, abduction, rotation }, mid } in degrees. A limb held nearly
// STRAIGHT has no plane of its own to bend in, so its twist (the root's rotation) is not in the points: below STRAIGHT
// of bend it leans to `keep` (the rotation it had), so a straight leg's foot does not spin about it
const _X = new THREE.Vector3(1, 0, 0), _Z = new THREE.Vector3(0, 0, 1), _Qi = new THREE.Quaternion(), STRAIGHT = Math.sin(15 * Math.PI / 180);
export function limbAngles(limb, S, E, W, Qp, keep = null) {
  const mv = MODEL.joints[limb.root.split(".")[1]].movements;
  if (Object.values(mv).map((m) => m.axis).join("") !== "zxy") throw new Error(`joints: the ${limb.root}'s movements must turn about z, x, y in that order`);
  _Qi.copy(Qp).invert();
  const L1 = S.distanceTo(E), L2 = E.distanceTo(W);
  const u = E.clone().sub(S).divideScalar(L1).applyQuaternion(_Qi), f = W.clone().sub(E).divideScalar(L2).applyQuaternion(_Qi);
  const F = Math.atan2(u.x, -u.y), ax = Math.asin(Math.max(-1, Math.min(1, -u.z)));
  const b = f.clone().addScaledVector(u, -f.dot(u)).multiplyScalar(limb.bend);   // (the way the middle joint must bend, in its own +x)
  const X0 = _X.clone().applyAxisAngle(_X, ax).applyAxisAngle(_Z, F), Z0 = _Z.clone().applyAxisAngle(_X, ax).applyAxisAngle(_Z, F);
  const DEG = 180 / Math.PI, bent = b.length();
  let rot = bent > 1e-6 ? Math.atan2(-b.dot(Z0), b.dot(X0)) / (mv.rotation.sign * limb.s) * DEG : keep ?? 0;
  if (keep !== null && bent < STRAIGHT) rot = keep + (rot - keep) * (bent / STRAIGHT);
  return { root: { flexion: F / mv.flexion.sign * DEG, abduction: ax / (mv.abduction.sign * limb.s) * DEG, rotation: rot },
           mid: Math.acos(Math.max(-1, Math.min(1, u.dot(f)))) * DEG };
}

// the limb's root joint and its parent's turn, as the last fk posed them
const _m4 = new THREE.Matrix4();
export const limbBase = (rig, limb) => ({ S: jointAt(rig, limb.i0), Qp: new THREE.Quaternion().setFromRotationMatrix(_m4.extractRotation(rig.frames[limb.parent])) });

// THE LIMB TO A POINT -- the angles written into `a` (clamped to their ranges); returns how far the tip stays from the
// point. Its elbow or knee goes round the circle to the side it POINTS to now: a knee's cap faces the upper bone's
// own +x, an elbow its -x (away from where each bends), as the position being played holds the limb -- not to the
// circle's point nearest the joint, which for a limb held straight lies on the line and may as well be the side the
// joint cannot bend toward
const _xu = new THREE.Vector3();
export function reachLimb(rig, limb, target, a) {
  const { S, Qp } = limbBase(rig, limb), c = midCircle(S, target, limb.L1, limb.L2);
  let r = _xu.setFromMatrixColumn(rig.frames[limb.i0], 0).normalize().multiplyScalar(-limb.bend).clone(); r.addScaledVector(c.n, -r.dot(c.n));
  if (r.lengthSq() < 1e-10) r = new THREE.Vector3(1, 0, 0).applyQuaternion(Qp).addScaledVector(c.n, -c.n.dot(new THREE.Vector3(1, 0, 0).applyQuaternion(Qp)));
  const E = c.C.clone().addScaledVector(r.normalize(), c.h), ang = limbAngles(limb, S, E, c.tip, Qp, a.joints[limb.root].rotation);
  Object.assign(a.joints[limb.root], ang.root); a.joints[limb.mid].flexion = ang.mid;
  clampLimb(a, limb);
  return c.miss;
}
const clampLimb = (a, limb) => {
  for (const key of [limb.root, limb.mid, limb.end]) {
    const mvs = MODEL.joints[key.split(".")[1]].movements;
    for (const [mv, d] of Object.entries(mvs)) a.joints[key][mv] = Math.min(d.max, Math.max(d.min, a.joints[key][mv]));
  }
};

// THE END JOINT (wrist, ankle) turned so the end part points along `dir` (world) as near as its one movement allows:
// a planted foot kept flat, a hand kept on the floor. Needs the limb posed (fk) without its end's own angle mattering.
export function aimEnd(rig, limb, dir, a) {
  const m = rig.frames[limb.i1], X = new THREE.Vector3().setFromMatrixColumn(m, 0).normalize(), Y = new THREE.Vector3().setFromMatrixColumn(m, 1).normalize();
  // the end part turns about its parent's z: its pointing axis (x for a foot, -y for a hand) swung by phi
  const px = limb.point.x, py = limb.point.y;   // (one of them is 0, the other +-1)
  const phi = px ? Math.atan2(dir.dot(Y) * px, dir.dot(X) * px) : Math.atan2(-dir.dot(X) * py, dir.dot(Y) * py);
  const d = MODEL.joints[limb.end.split(".")[1]].movements.flexion;
  a.joints[limb.end].flexion = Math.min(d.max, Math.max(d.min, phi / d.sign * 180 / Math.PI));
}
// the end part's pointing direction now (world)
export const endDir = (rig, limb, out = new THREE.Vector3()) => out.copy(limb.point).transformDirection(rig.frames[limb.i2]);
