// GREEK PAINTINGS, the rig (docs/greek.md): a body as joints in a plane, solved from an ACTION (assets/greek/canon.json:
// which legs, how much lean and twist, where the hands go, each a range a seed picks in) and a scene's targets. All in
// units of a figure 100 tall; solved facing +x ("forward"), then `place` puts a point in the world: x flipped for a figure
// facing left. Flipping swaps which arm is NEAR, never which arm holds what: facing right the near arm is the right.

import { stream, pick } from "../story/seed.js";
export { stream, pick };                                                // (the seed's grammar is shared by all the 2D engines: docs/story.md)
const DEG = Math.PI / 180;

// where the middle joint of two bones falls: bend > 0 to the left of the line a -> c, and c pulled in when out of reach
export function twoBone(a, c, la, lb, bend) {
  let dx = c[0] - a[0], dy = c[1] - a[1], d = Math.hypot(dx, dy) || 1e-6;
  const reach = (la + lb) * .998, short = Math.abs(la - lb) * 1.02;
  const miss = Math.max(0, d - reach);
  const k = Math.min(reach, Math.max(short, d)) / d;
  dx *= k; dy *= k; d = Math.hypot(dx, dy);
  const along = (la * la - lb * lb + d * d) / (2 * d), up = Math.sqrt(Math.max(0, la * la - along * along));
  const ux = dx / d, uy = dy / d;
  return { mid: [a[0] + ux * along - uy * up * bend, a[1] + uy * along + ux * up * bend], end: [a[0] + dx, a[1] + dy], miss };
}

// solve a body. opts: dir (1 faces +x), x (the world place of the point under the hips at rest), r (a stream),
// targets ({ name: [x, y] } in the world) for hands that `reach`. canon, legs: the data's.
export function solvePose(data, actionName, { dir = 1, x = 0, y = 0, r = Math.random, targets = {}, scale = 1, over = {} } = {}) {
  const C = data.canon.lengths, act = data.actions[actionName];
  if (!act?.legs) throw new Error(`no action "${actionName}"`);
  const legs = act.legs.of ? act.legs.of[Math.floor(r() * act.legs.of.length)] : act.legs, prog = { ...data.legs[legs], ...(act.leg ?? {}) };   // (one set of arms on any of several legs)
  const L = C.thigh + C.shin, nearSide = dir > 0 ? "R" : "L";
  const leadSide = act.lead ?? "L", leadNear = leadSide === nearSide;
  const foot = (q) => {
    const f = pick(q[0], r) * L, up = pick(q[1], r) * L, pitch = pick(q[2], r) * DEG;
    return { pitch, ankle: [f, C.ankle + up + Math.max(0, Math.sin(pitch)) * 10.5] };
  };
  const lead = foot(prog.lead), rear = foot(prog.rear);
  const shift = pick(prog.shift, r) * L;
  const hipOff = C.hip * .28, reachL = L * .985;
  const standH = (a, s) => a.ankle[1] + Math.sqrt(Math.max(1, reachL * reachL - (a.ankle[0] - s) ** 2));
  let pelvisY = prog.pelvis !== undefined ? pick(prog.pelvis, r) * L : Math.min(standH(lead, shift + hipOff), standH(rear, shift - hipOff));
  pelvisY *= 1 - pick(prog.drop, r);

  // the trunk, leaning from the hips and bending at the waist; the shoulder line turned by `turn`
  let lean = pick(act.lean, r);
  const curve = pick(act.bendSpine, r), turnAmt = pick(act.turn, r), period = over.period ?? {};
  const pelvis = [shift, pelvisY];
  const frontNear = (act.front ?? "L") === nearSide;
  const turn = (frontNear ? -1 : 1) * turnAmt * (period.turn ?? 1);    // chest to us (> 0) when the far shoulder comes forward, the back when the near one does
  const trunk = (ln) => {
    const w = [pelvis[0] + Math.sin(ln - curve) * C.trunk * .45, pelvis[1] + Math.cos(ln - curve) * C.trunk * .45];
    const c = [w[0] + Math.sin(ln + curve) * C.trunk * .55, w[1] + Math.cos(ln + curve) * C.trunk * .55];
    return { waist: w, chest: c };
  };
  let spine = trunk(lean);
  const shoulderAt = (near, s) => {
    const off = C.shoulder / 2 * turn * (near ? -1 : 1), ax = Math.cos(lean + curve), ay = -Math.sin(lean + curve);
    return [s.chest[0] + ax * off - Math.sin(lean + curve) * .8, s.chest[1] + ay * off - Math.cos(lean + curve) * 1.6];
  };

  // hands: a hand [forward, up] from its shoulder in arm lengths, or a world target; out of reach, the trunk leans in (twice) and then the hand stops
  const armLen = C.upper + C.fore + (C.hand * .4);
  const armSet = act.arms?.of && !over.shield ? Math.floor(r() * act.arms.of.length) : 0, set = act.arms?.of?.[armSet] ?? act.arms;   // (one trunk and legs, several ways of holding the arms; a shield stays where the action has it)
  const spec = { R: { ...set?.R, ...over.arms?.R }, L: { ...set?.L, ...over.arms?.L } };
  const aims = {};
  for (const side of ["R", "L"]) aims[side] = { f: pick(spec[side].hand?.[0], r, 0), u: pick(spec[side].hand?.[1], r, -1) };
  const toLocal = (q) => [(q[0] - x) * dir, q[1] - y];
  const handFor = (side, s) => {
    const sh = shoulderAt(side === nearSide, s), t = spec[side].reach && targets[spec[side].reach];
    return { sh, hand: t ? toLocal(t) : [sh[0] + aims[side].f * armLen, sh[1] + aims[side].u * armLen] };
  };
  for (let pass = 0; pass < 2; pass++) for (const side of ["R", "L"]) {
    if (!spec[side].reach) continue;
    const { sh, hand } = handFor(side, spine), d = Math.hypot(hand[0] - sh[0], hand[1] - sh[1]) - armLen;
    if (d > 0 && targets[spec[side].reach]) { lean += Math.sign(hand[0] - sh[0] || 1) * Math.min(.22, d / C.trunk); spine = trunk(lean); }
  }
  let miss = 0;
  const arm = (side) => {
    const { sh, hand } = handFor(side, spine), bend = spec[side].bend ?? 1;
    const s = twoBone(sh, hand, C.upper, C.fore + C.hand * .4, -bend);
    miss = Math.max(miss, s.miss);
    return { side, sh, el: s.mid, wr: lerp2(s.mid, s.end, C.fore / (C.fore + C.hand * .4)), hand: s.end, fist: !!spec[side].fist };
  };
  const arms = { R: arm("R"), L: arm("L") };

  // legs: each from its own hip to its ankle, the knee forward (a leg's `bend` may turn it)
  const hipFor = (near) => [pelvis[0] + (near ? -1 : 1) * Math.abs(turn) * hipOff * (frontNear ? -1 : 1), pelvis[1]];
  const leg = (near, q, name) => {
    const hip = hipFor(near), s = twoBone(hip, q.ankle, C.thigh, C.shin, prog.bend?.[name] ?? 1);
    miss = Math.max(miss, s.miss);
    return { hip, knee: s.mid, ankle: s.end, pitch: q.pitch };
  };
  const legNear = leg(true, leadNear ? lead : rear, leadNear ? "lead" : "rear");
  const legFar = leg(false, leadNear ? rear : lead, leadNear ? "rear" : "lead");

  // neck and head
  const ln = lean + curve, neck = [spine.chest[0] + Math.sin(ln) * C.neck * .1, spine.chest[1] + Math.cos(ln) * C.neck * .1];
  const tilt = pick(act.look, r, 0) + ln * .35;
  const headBase = [neck[0] + Math.sin(ln * .7) * C.neck, neck[1] + Math.cos(ln * .7) * C.neck];

  const place = (q) => [x + dir * q[0] * scale, y + q[1] * scale];
  return {
    legs, armSet,
    action: actionName, dir, x, y, scale, place, nearSide, leadSide, lean: ln, turn, pelvis, ...spine, neck, headBase, tilt, lookBack: !!act.lookBack,
    arms, near: { arm: arms[nearSide], leg: legNear }, far: { arm: arms[nearSide === "R" ? "L" : "R"], leg: legFar }, miss,
  };
}
const lerp2 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];

// where a shield hangs on the left forearm, in the body's space: near the elbow on the near arm, nearer the hand on the far one
export const shieldCentre = (pose) => lerp2(pose.arms.L.el, pose.arms.L.wr, pose.nearSide === "L" ? .55 : .72);

// a named place on a solved body, in the world: what a scene aims at
export function anchor(pose, name) {
  const m = (a, b, t = .5) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const q = { throat: pose.headBase, head: [pose.headBase[0] + 1, pose.headBase[1] + 9], hair: [pose.headBase[0] - 1, pose.headBase[1] + 16], chest: m(pose.chest, pose.waist, .25), belly: pose.waist, thigh: m(pose.near.leg.hip, pose.near.leg.knee),
    shield: shieldCentre(pose), hand: pose.near.arm.hand, wristL: pose.arms.L.wr, wristR: pose.arms.R.wr }[name];
  if (!q) throw new Error(`no anchor "${name}"`);
  return pose.place(q);
}
