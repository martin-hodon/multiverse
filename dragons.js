// DRAGONS: one rule, many beasts. A dragon's definition (assets/creatures/dragons/*.json, kind "dragon") does not
// write out its body -- it says WHAT KIND of dragon it is, in a handful of words, and this builds the body plan and
// everything that grows on it for mammals.js mammal() to turn into parts:
//
//   body      western  four legs and a pair of bat wings, the neck raised: the dragon of the European romances
//             drake    no wings, low and long, heavy in the shoulder: a lindworm, a fire-drake
//             wyvern   two legs and the wings: a heraldic wyvern
//             lung     the Chinese dragon (龍): a long serpent's body in waves, four short legs, no wings -- it flies
//                      all the same -- a long snout with whiskers, antlers, a mane
//             serpent  a feathered serpent (Quetzalcoatl): the lung's body with a bird's wings
//   wings     bat | feather | none        (default by body)     wingSpan: their size
//   horns     swept | straight | curl | crown | antlers | plume | none                hornLen: their size
//   nose      a horn on the snout (true)
//   spikes    spike | plate | fin | tuft | none -- the row down the back, the neck and the tail     spikeSize
//   tailEnd   spade | club | blade | flame | plume | none
//   whiskers, brows, beard, mane, elbows (flames at the elbows): the lung's hair, any dragon may have it
//   claws     toes on each foot (the Chinese count: five the emperor's, four a prince's, three Japan's)
//   s         the whole beast's size (1: the western dragon, ~6 m nose to tail)
//
// Colours come from the definition's own table: body, front (the chest and belly), head, muzzle, leg, foot, tail,
// eye, and the dragon's own -- spike, horn, bone and mem (a bat wing's), feather and tip (a bird wing's), mane,
// whisker, claw. What a table leaves out is worked out from the body's colour.
import { mammal, batWing, birdWing } from "./mammals.js";
import { KINDS } from "./creatures.js";
import { aim, scaleDef } from "./geom.js";

const add = (a, b) => a.map((v, i) => v + b[i]), sub = (a, b) => a.map((v, i) => v - b[i]), mul = (a, k) => a.map((v) => v * k);
const unit = (a) => { const l = Math.hypot(...a) || 1; return a.map((v) => v / l); };
const lerp = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const shade = (hex, f) => {   // f < 1 darker, > 1 lighter (toward white)
  const ch = (sh) => { const v = (hex >> sh) & 255; return Math.round(f <= 1 ? v * f : v + (255 - v) * (f - 1)); };
  return (ch(16) << 16) | (ch(8) << 8) | ch(0);
};
// a tapered pill from A to B in its parent's own frame (mammals.js pillPart with the parent's origin at 0)
const pill = (id, parent, A, B, rA, rB, color, k = 0) => {
  const { len, rot } = aim(sub(B, A));
  return { id, parent, shape: "capsule", size: { r: rB, r2: rA, len }, pos: A, rot, pivot: [0, len / 2, 0], color, edge: 0, k };
};

// ---- THE BODY PLANS, in the species' frame (x forward, y up, z its left), metres at s = 1 ------------------------------
// tail: the points its curve runs through the middles of (mammals.js pathChain); wingAt: the shoulder
const PLANS = {
  western: {
    seat: [.85, 2.83],   // (the rider's: species.js saddle -- root x, the back's height there. At the neck's base, ahead of the wings;
    //  the lobes' own seat came out behind the shoulders, and a lung's by its hips)
    cell: .0835,   // (the sculpt grid's cell, as it was measured: the horns must know it -- see the horns)
    rear: [-.9, 1.9, 0, 1.3, .9, .8], front: [.7, 2, 0, 1.2, .92, .85],
    neck: [1.6, 2.4, 0, 4.1, 4.35, 0, .46, .22], head: [4.3, 4.45, 0, .42],
    muzzle: [4.8, 4.32, 0, .5, .22, .26], nose: [5.28, 4.38, 0, .06],
    ears: [4.07, 4.62, .26, 3.77, 4.68, .46, .1, .02], eyes: [4.55, 4.62, .24, .065],
    legs: { front: [1, 1.6, .44, .8], hind: [-1.3, 1.65, .46, .9], radii: [.3, .22, .16], foot: [.3, .12, .24], bend: [1.04, 1.06] },
    tail: [[-2.15, 1.95], [-3.4, 1.85], [-4.6, 1.2], [-5.5, .55], [-6.2, .4]], tr: [.42, .07], sway: 8,
    // (pass 4: span 1.2 -> 1.6 body lengths -- the arm longer, the fingers longer still)
    wings: "bat", wingAt: [.3, 2.55, .5], wingK: 3.7, wingPose: { arm: 1.15, fingers: [[8, 1.52], [28, 1.45], [52, 1.31], [78, 1.08]] }, spike: .38,
    flight: { beat: 7, handK: .6, neck: 26, splay: [-6, -12] },   // (the legs drawn in under the flanks as they tuck)
  },
  drake: {
    seat: [1.0, 2.16],
    cell: .0548,
    rear: [-1, 1.35, 0, 1.45, .8, .85], front: [.8, 1.4, 0, 1.3, .85, .9],
    neck: [1.8, 1.7, 0, 2.6, 2.35, 0, .52, .38], head: [2.8, 2.45, 0, .49],
    muzzle: [3.3, 2.32, 0, .56, .26, .3], nose: [3.86, 2.38, 0, .07],
    ears: [2.58, 2.62, .27, 2.28, 2.66, .45, .1, .02], eyes: [3.06, 2.64, .27, .07],
    legs: { front: [1.1, 1.1, .75, .55], hind: [-1.4, 1.1, .8, .6], radii: [.36, .26, .19], foot: [.34, .13, .28], bend: [1.04, 1.06] },
    tail: [[-2.4, 1.4], [-3.6, 1.25], [-4.8, .75], [-5.9, .35], [-6.7, .3]], tr: [.46, .07], sway: 7,
    wings: "none", wingAt: [.4, 2.05, .6], wingK: 1.5, spike: .34,
  },
  wyvern: {
    seat: [1.0, 3.07],
    cell: .0721,
    rear: [-.5, 2.1, 0, 1.1, .85, .75], front: [.9, 2.35, 0, .95, .8, .72],
    neck: [1.6, 2.7, 0, 3.45, 4.25, 0, .4, .2], head: [3.65, 4.35, 0, .38],
    muzzle: [4.1, 4.23, 0, .45, .2, .23], nose: [4.53, 4.28, 0, .055],
    ears: [3.45, 4.51, .23, 3.17, 4.57, .4, .09, .02], eyes: [3.88, 4.51, .21, .06],
    legs: { front: [.9, 2.1, .5, .8], hind: [-.25, 1.95, .5, .95], radii: [.34, .23, .15], foot: [.32, .12, .22], kneeH: 1, toe: .15, bend: [1.03, 1.07] },
    biped: true,
    tail: [[-1.55, 2.25], [-2.8, 2.15], [-3.9, 1.7], [-4.9, 1.3], [-5.6, 1.2]], tr: [.36, .06], sway: 9,
    wings: "bat", wingAt: [.6, 2.85, .46], wingK: 3.2, wingPose: { arm: 1.15, fingers: [[8, 1.52], [28, 1.45], [52, 1.31], [78, 1.08]] }, spike: .3,
    flight: { beat: 7, handK: .6, neck: 26, hind: [-100, 30, -70], splay: [0, -12] },
  },
  lung: {
    seat: [1.3, 1.6],
    cell: .052,
    rear: [-1.2, 1.15, 0, 1.35, .34, .36], front: [1.0, 1.22, 0, 1.25, .36, .38],
    neck: [2.0, 1.35, 0, 2.75, 2.0, 0, .32, .24], head: [2.9, 2.1, 0, .3],
    muzzle: [2.95, 2.06, 0, 3.5, 1.98, 0, .22, .12], nose: [3.56, 2.03, 0, .065],
    ears: [2.72, 2.32, .17, 2.5, 2.42, .27, .06, .015], eyes: [2.93, 2.23, .15, .068],
    legs: { front: [1.35, 1.0, .4, .45], hind: [-1.6, .95, .4, .45], radii: [.2, .15, .11], foot: [.22, .08, .16], bend: [1.03, 1.05] },
    tail: [[-2.5, 1.15, 0], [-3.4, 1.75, .35], [-4.4, .8, -.4], [-5.4, 1.55, .35], [-6.3, .9, -.25], [-7.0, 1.1, 0]], tr: [.34, .05], sway: 6,
    wings: "none", wingAt: [1.1, 1.5, .35], wingK: 1.3, spike: .2, serpent: true,
    // (it swims through the air: the head raised, the body loose -- its waves kept and a wave of its own running back down it)
    // (pass 4: the wave from the neck's root -- the trunk's links a third of a wave apart, so the head holds its line
    //  -- tapering down the tail, no kink at its tip; the tail's root aimed so that, over a wave, its chord runs level
    //  (t_pose: 176; 186 hung it down to the ground); the legs trailing back along the body, not crouched -- and,
    //  pass 5, spread out to the sides (splay); pass 6, the forearms trailing back too: they hung straight down)
    flight: { neck: 30, head: .7, tail: 176, straight: 0, front: [-82, 18, 20], hind: [-105, 20, -55], splay: [24, 20], wave: { deg: 13, trunk: 8, lag: .9, trunkLag: 2.09, taper: .55, speed: .25 } },
  },
};
// (the feathered serpent: flying, not swimming -- held near level, its wave gentle: pass 4, it sagged into a dive)
PLANS.serpent = { ...PLANS.lung, wings: "feather", wingK: 1.9, wingAt: [1.0, 1.6, .3],
                  flight: { ...PLANS.lung.flight, beat: 7.5, handK: .5, neck: 18, tail: 177, wave: { deg: 7, trunk: 4, lag: .9, trunkLag: 2.09, taper: .5, speed: .25 } } };

// ---- THE WINGS (2026-11-05): their own rigs, so the sculpted body knows where every bone of them lies at rest ----------
// A frame as skeleton.js chains them: an origin and a rotation (three's Euler XYZ, degrees: v -> Rx(Ry(Rz v)))
const D2R = Math.PI / 180;
const eul = ([ax, ay, az]) => (v) => {
  let [x, y, z] = v; const [ca, sa, cb, sb, cc, sc] = [Math.cos(ax * D2R), Math.sin(ax * D2R), Math.cos(ay * D2R), Math.sin(ay * D2R), Math.cos(az * D2R), Math.sin(az * D2R)];
  [x, y] = [x * cc - y * sc, x * sc + y * cc];
  [x, z] = [x * cb + z * sb, -x * sb + z * cb];
  [y, z] = [y * ca - z * sa, y * sa + z * ca];
  return [x, y, z];
};
const frameOf = (o, rot, parent = null) => {
  const R = eul(rot ?? [0, 0, 0]), o2 = parent ? parent.pt(o) : o, R2 = parent ? (v) => parent.dir(R(v)) : R;
  return { o: o2, dir: R2, pt: (v) => add(o2, R2(v)) };
};
// A DRAGON'S BAT WING: the arm in two bones (the humerus, shoulder to elbow; the forearm, elbow to wrist), a thumb
// claw, and the HAND: four long fingers, each its own bone, the skin between two of them in two halves (each finger
// carrying the half on its side, the trailing edge a shallow curve in toward the wrist, bowed a little out of the
// plane), and the arm's skin from the leading edge (shoulder - wrist) back to the ROOT on the flank -- a fan about
// the shoulder on three rays of its own, so the membrane's root never leaves the flank however the wing beats.
// FOLDED (2026-11-05, pass 3: it splayed up off the shoulder in slabs): a bat's fold. The humerus lies back along the
// flank (`rest.az`: the arm's frame from straight up), the forearm doubled forward against it (`rest.fore`) so the
// wrist sits at the withers, the hand turned back (`rest.hand`) so the fingers run back along the flank toward the
// hip, nearly parallel (`rest.close` of their spread) and pleated (alternately `rest.pleat` degrees in and out). The
// arm's skin closes onto the humerus (`rest.skin` of its spread), and every wedge of skin, each its own part, closes onto
// its bone so the whole lies in a narrow pleated bundle. In flight (skeleton.js FLIGHT) each part's `flyRot`
// undoes the fold: the arm swung forward to `fly.az`, the forearm straightened, the fingers fanned open.
// THE UPSTROKE (2026-11-05, pass 4: it stayed a spread board both ways): `up.wrist` degrees of wrist flex and the
// fingers drawn `up.close` of the way back onto the last one -- skeleton.js flyUp, on the upstroke only -- so the hand
// half-folds as it rises and opens again to beat down. (The last finger stays put: the skin from it to the arm's
// never tears.) `arm`: the arm's length (shoulder to wrist) in k.
function dragonBatWing(s, at, { k = 1, bone, mem, deg = 3, speed = .35, rest = {}, fly = {}, up = {}, cam = .045, arm: aK = 1,
                                fingers = [[8, 1.32], [28, 1.26], [52, 1.14], [78, .94]] } = {}) {
  const S = s > 0 ? "L" : "R", E = aK * k, LD = .6 * k, th = .007 * k;   // (ledger pass: .007, was .014 -- see the skin's wedges)
  const R = { az: 66, tilt: 4, yaw: 3, fore: 221, foreOut: 5, hand: -186, out: -2, close: .05, skin: .08, skinTo: 5, skinIn: 7, pleat: 1.5, fpleat: .6, ...rest }, Fz = fly.az ?? 6;
  const U = { wrist: 12, close: .45, ...up }, aLast = fingers[fingers.length - 1][0];
  const FING = fingers.map(([a, L]) => ({ a, L: L * k, t: [-Math.sin(a * D2R) * L * k, Math.cos(a * D2R) * L * k, 0] }));
  const ang = (p) => Math.atan2(-p[0], p[1]) / D2R;   // (a point's angle from the arm's +y, toward its back, -x)
  const Elb = [-.2 * k, .36 * E, 0], W = [0, E, 0], Root = [-.78 * k, 0, 0], D = [-LD, E, 0];
  const FA = sub(W, Elb), Lf = Math.hypot(...FA), af = ang(FA), hA = ang(Elb);
  // a piece of skin: a wedge from its bone's origin (the shoulder, the wrist), its own part turned at rest so that it
  // lies along `to` (a fan closed: every wedge on top of the next, not each spread its own width) and pleated, `pl`
  // degrees in or out -- and turned back aloft
  let nTri = 0;
  // (ledger pass: a wedge is a plate of two faces, open at its rim (bodymesh.js detailMesh) -- two that only met edge to
  //  edge let the sky through the seam from any oblique view aloft, a fan of slits from the wrist. Now the skin is half
  //  as thick, each wedge reaches `GROW` of its chord past both its long edges onto its neighbours, and alternate wedges
  //  stand a little apart in depth, so the overlaps never fight)
  const GROW = .1;
  const tri = (id, par, a, b, c, to = 0, keep = .08, tin = 0) => {
    const odd = nTri % 2, cen = (ang(b) + ang(c)) / 2, rr = (to + keep * (cen - to)) - cen, pl = s * (R.pleat * (nTri++ % 2 ? 1 : -1) - tin);
    const dz = s * (odd ? 1 : -1) * th * .45, m = lerp(b, c, .5), gr = (v) => { const g = add(m, mul(sub(v, m), 1 + GROW)); return [g[0], g[1], v[2] + dz]; };
    return { id, parent: par, shape: "tri", size: { a: [a[0], a[1], a[2] + dz], b: gr(b), c: gr(c), r: th }, pos: [0, 0, 0], rot: [pl, 0, rr], flyRot: [-pl, 0, -rr], color: mem, edge: 0, k: 0 }; };
  const arm = { id: `wArm${S}`, parent: "body", shape: "capsule", size: { r: .05 * k, len: E * .4 }, pos: [0, 0, 0], rot: [s * R.tilt, s * R.yaw, R.az], pivot: [0, E * .2, 0], color: bone, edge: 0,
                anim: { axis: "x", deg: s * deg, speed, phase: 0, wing: true, side: s }, fold: [0, 0, 6], flyRot: [0, -s * R.yaw, Fz - R.az] };
  const fore = { id: `wFore${S}`, parent: `wArm${S}`, shape: "capsule", size: { r: .035 * k, len: Lf }, pos: Elb, pivot: [0, Lf / 2, 0], rot: [-s * R.foreOut, 0, R.fore], color: bone, edge: 0,
                 flyRot: [s * R.foreOut, 0, af - R.fore] };
  const hand = { id: `wHand${S}`, parent: `wFore${S}`, shape: "sphere", size: { r: .03 * k }, pos: [0, Lf, 0], rot: [-s * R.out, 0, R.hand], color: bone, edge: 0,
                 anim: { axis: "x", deg: s * deg * 1.6, speed, phase: .6, wing: true, side: s }, fold: [0, 0, 0], flyRot: [0, 0, -af - R.hand], flyUp: [0, 0, U.wrist] };
  // a finger's own frame: its tip at [0, L, 0]; a point of the SPREAD hand in it (the skin it carries)
  const inF = (a, p) => { const c = Math.cos(a * D2R), sn = Math.sin(a * D2R); return [p[0] * c + p[1] * sn, -p[0] * sn + p[1] * c, p[2]]; };
  // the trailing edge between two tips: a shallow arc in toward the joint, bowed out of the plane (camber)
  const arc = (P, Q, t) => { const m = lerp(P, Q, t), b = 1 - .09 * Math.sin(Math.PI * t), span = Math.hypot(...sub(Q, P)); return [m[0] * b, m[1] * b, -s * cam * span * Math.sin(Math.PI * t)]; };
  // (ledger pass: .0084 k apart, was .021 k -- the two halves of a gap three skins apart showed the sky between them at every
  //  seam from an oblique view aloft, a fan of slits from the wrist; now their skins overlap in depth)
  const zs = (side) => (v) => [v[0], v[1], v[2] + side * th * 1.2];
  // the arm's skin: wedges about the shoulder (to the wrist, to D on the hand's base, back to the root), closed at
  // rest (`rest.skin` of their spread) onto a line `rest.skinTo` degrees above the humerus -- up under the folded
  // fingers, the whole wing one band along the back, not two -- and `rest.skinIn` degrees in toward the flank (pass 5:
  // from above it was a jagged fan outside the fingers)
  const mWD = lerp(W, D, .5), ac = [0, .25, .5, .75, 1].map((t) => arc(D, Root, t)), AS = (id, b, c) => tri(id, `wArm${S}`, [0, 0, 0], b, c, hA + R.skinTo, R.skin, R.skinIn);
  const parts = [arm,
    AS(`wMemA${S}`, W, mWD), AS(`wMemA1${S}`, mWD, D), AS(`wMemA2${S}`, ac[0], ac[1]), AS(`wMemA3${S}`, ac[1], ac[2]), AS(`wMemA4${S}`, ac[2], ac[3]), AS(`wMemA5${S}`, ac[3], ac[4]),
    fore, hand,
    ...FING.map((f, i) => { const pl = s * R.fpleat * (i % 2 ? 1 : -1);   // (the fingers barely pleated: folded, their tips lie together)
      return { id: `wFinger${i}${S}`, parent: `wHand${S}`, shape: "capsule", size: { r: .03 * k, r2: .012 * k, len: f.L }, pos: [0, 0, 0], rot: [pl, 0, f.a * R.close],
               pivot: [0, f.L / 2, 0], color: bone, edge: 0, flyRot: [-pl, 0, f.a * (1 - R.close)], flyUp: [0, 0, (aLast - f.a) * U.close] }; }),
  ];
  // the fingers' skin: each gap's two halves, on the finger each side of it (an offset in z apiece, so that folded they
  // do not fight); the last gap, back to D at the hand's base, all of it on the last finger, folding in with it
  const gaps = [...FING.slice(0, -1).map((f, i) => [f.t, FING[i + 1].t, i, i + 1]), [FING[FING.length - 1].t, [-LD, 0, 0], FING.length - 1, -1]];
  gaps.forEach(([P, Q, i, j], g) => {
    // (the halves on two fingers overlap past the middle, .42 to .58 of the span, so no slit opens between them however
    //  the fingers turn; the last gap's halves lie on the one finger, the same side -- they meet exactly, or they would fight)
    const ov = j >= 0 ? .08 : 0, pts = [0, .25 + ov / 2, .5 + ov, .5 - ov, .75 - ov / 2, 1].map((t) => arc(P, Q, t)), own = (f, list, side) => list.map((v) => zs(side)(inF(f.a, v)));
    const [a0, a1, a2] = own(FING[i], pts.slice(0, 3), 1);
    parts.push(tri(`wMemB${g}${S}`, `wFinger${i}${S}`, [0, 0, 0], a0, a1), tri(`wMemB${g}a${S}`, `wFinger${i}${S}`, [0, 0, 0], a1, a2));
    const [b2, b3, b4] = own(FING[j >= 0 ? j : i], pts.slice(3), j >= 0 ? -1 : 1), on = `wFinger${j >= 0 ? j : i}${S}`;
    parts.push(tri(`wMemB${g}b${S}`, on, [0, 0, 0], b2, b3), tri(`wMemB${g}c${S}`, on, [0, 0, 0], b3, b4));
  });
  // the REST geometry, in the species' frame (for the body's shapes on these bones)
  const fa = frameOf(at, arm.rot), ff = frameOf(fore.pos, fore.rot, fa), fh = frameOf(hand.pos, hand.rot, ff);
  const geo = { k, S0: fa.o, Elb: ff.o, W: fh.o, up: fa.dir([0, 0, -s]), back: fa.dir([-1, 0, 0]),
                // (pass 6: folded, it pointed up over the shoulder -- now forward along the bundle, level, and short; aloft
                //  it lies in along the leading edge toward the shoulder)
                thumb: fh.pt(mul([-.05, -.15, 0], Math.min(k, 2.6) * .75)),
                fingers: FING.map((f, i) => { const fr = frameOf([0, 0, 0], parts.find((q) => q.id === `wFinger${i}${S}`).rot, fh);
                  return { tip: fr.pt([0, f.L, 0]), knuckle: fr.pt([.012 * k, f.L * .42, 0]), L: f.L, bone: `wFinger${i}` }; }) };
  return { parts, geo };
}
// A FEATHERED WING (the feathered serpent's): only its two bones here -- the arm and the hand; the body grows the
// feathers on them (bodymesh.js featherMesh: primaries on the hand, secondaries on the forearm, two rows of coverts).
// Folded (a bird's): the arm laid back along the flank (`rest.az` from straight up), tilted out at the bottom, the
// feathers hanging back and down over the side; flyRot sweeps it forward again into the spread.
// (pass 4: folded closer to the flank -- yaw 22 -> 12, it stood off in a V from above (less and its bones sink into the body); and on the upstroke the hand
//  swept back `up.hand` degrees, the primaries trailing, as a bird's do)
function dragonFeatherWing(s, at, { k = 1, bone, deg = 3, speed = .4, rest = {}, fly = {}, up = {} } = {}) {
  const S = s > 0 ? "L" : "R", E = 1.0 * k, HL = .55 * k, R = { az: 84, tilt: 24, yaw: 12, hand: 6, ...rest }, Fz = fly.az ?? 6, U = { hand: 38, ...up };
  const arm = { id: `wArm${S}`, parent: "body", shape: "capsule", size: { r: .04 * k, len: E }, pos: [0, 0, 0], rot: [-s * R.tilt, s * R.yaw, R.az], pivot: [0, E / 2, 0], color: bone, edge: 0,
                anim: { axis: "x", deg: s * deg, speed, phase: 0, wing: true, side: s }, fold: [0, 0, 4], flyRot: [0, -s * R.yaw, Fz - R.az] };   // (yaw: out from the flank, its bones clear of the body)
  const hand = { id: `wHand${S}`, parent: `wArm${S}`, shape: "capsule", size: { r: .03 * k, r2: .02 * k, len: HL }, pos: [0, E, 0], rot: [0, 0, R.hand], pivot: [0, HL / 2, 0], color: bone, edge: 0,
                 anim: { axis: "x", deg: s * deg * 1.4, speed, phase: .5, wing: true, side: s }, fold: [0, 0, 0], flyRot: [0, 0, -R.hand], flyUp: [0, 0, U.hand] };
  const fa = frameOf(at, arm.rot), fh = frameOf(hand.pos, hand.rot, fa);
  return { parts: [arm, hand], geo: { k, E, HL, fa, fh, S0: fa.o, W: fh.o, up: fa.dir([0, 0, -s]) } };
}

// ---- what grows on it ------------------------------------------------------------------------------------------------
const DEFAULTS = {
  western: { horns: "swept", spikes: "spike", tailEnd: "spade", claws: 3 },
  drake:   { horns: "straight", spikes: "plate", tailEnd: "club", claws: 3 },
  wyvern:  { horns: "swept", spikes: "spike", tailEnd: "blade", claws: 3 },
  lung:    { horns: "antlers", spikes: "tuft", tailEnd: "flame", claws: 5, whiskers: true, brows: true, beard: true, mane: true, elbows: true },
  serpent: { horns: "plume", spikes: "tuft", tailEnd: "plume", claws: 3, mane: true },
};

// ---- THE SCULPTED BODY (2026-11-05): what the overlay (bodyspec.js "sculpt") draws instead of the rig's pills --------
// Written once per body plan in the species' rest frame at s = 1 (scaleDef scales it with the beast), on the rig's bones,
// coloured from the definition's own table: a keeled chest under the wing muscles, a waist, heavy haunches, a sinuous
// neck, a reptile's head (skull, brow ridges over the eyes, the jaw-closing muscles behind them, a long snout with a
// nose pad and flared nostrils, a lower jaw and its teeth), legs of muscle, the belly in plates (scutes) and the back in
// scales; the bat wing's arm and fingers as bone, its membranes the rig's; the feathered wing in real feathers.
// a serpent's trunk: one long body in gentle waves (up and down, and side to side), the legs where it dips -- [x, y, z, r]
function trunkLine(P) {
  const r0 = P.tr[0], y0 = P.tail[0][1], x0 = P.tail[0][0], xF = P.legs.front[0], xH = P.legs.hind[0], g = P.front[4];
  return [[x0 - .05, y0, 0, r0 * .98], [xH, y0 - .03, 0, g * .98], [(xH * 2 + xF) / 3, y0 + .42, .16, g * 1.04], [(xH + 2 * xF) / 3, y0 + .3, -.16, g * 1.06],
          [xF, y0 + .04, 0, g * 1.02], [P.neck[0] - .05, P.neck[1] - .03, 0, P.neck[6] * 1.02]];
}
// A SERPENT'S SPINE (2026-11-05, pass 4: the trunk was one rigid plank, the wave only in the tail): three links from
// behind the hips to the shoulders, `vert1..3` (bones only), the chest, forelegs, neck and head on the last, the trunk's
// skin split along them -- so skeleton.js FLIGHT.wave runs from the neck's root to the tail's tip (`waveAt` -3..-1)
const spineJoints = (P) => { const h = P.legs.hind[0] + .6, f = P.legs.front[0] - .5; return [h, (h + f) / 2, f]; };
// points along a Catmull-Rom spline through pts (as sculpt.js draws a tube), `per` to a span
function crSample(pts, per = 4) {
  const out = [], Q = [pts[0], ...pts, pts[pts.length - 1]];
  for (let i = 1; i < Q.length - 2; i++) for (let j = 0; j < per; j++) {
    const t = j / per, [p0, p1, p2, p3] = [Q[i - 1], Q[i], Q[i + 1], Q[i + 2]];
    out.push(p1.map((_, k) => .5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t * t * t)));
  }
  out.push(pts[pts.length - 1]);
  return out;
}
// a tube through `line` split at the spine's joints, each piece on its own link (a point of overlap either side)
const spineOf = (J, x) => J.filter((j) => x >= j).length;   // (0: the body, 1..3: vert1..3)
const spineBone = (i) => (i ? `vert${i}` : "body");   // (not `spine`: the back's spikes are spine0..)
function splitTube(line, J) {
  const d = crSample(line, 4), out = [];
  for (let s = 0; s <= J.length; s++) {
    const lo = s ? J[s - 1] : -1e9, hi = s < J.length ? J[s] : 1e9;
    let a = d.findIndex((p) => p[0] >= lo), b = d.findLastIndex((p) => p[0] < hi);
    if (a < 0 || b < a) continue;
    a = Math.max(0, a - 1); b = Math.min(d.length - 1, b + 1);
    out.push([spineBone(s), d.slice(a, b + 1)]);
  }
  return out;
}
function spineChain(def, P) {
  const parts = def.parts, body = parts[0], R = body.pos, J = spineJoints(P), line = trunkLine(P);
  const yAt = (x) => { for (let i = 0; i + 1 < line.length; i++) { const [a, b] = [line[i], line[i + 1]]; if (x >= a[0] && x <= b[0]) { const t = (x - a[0]) / (b[0] - a[0]); return [a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; } } return [line[0][1], 0]; };
  const JP = J.map((x) => [x, ...yAt(x)]);
  const links = JP.map((p, i) => ({ id: `vert${i + 1}`, parent: i ? `vert${i}` : "body", shape: "sphere", size: { r: .05 }, bone: true, color: body.color, edge: 0,
                                    pos: sub(p, i ? JP[i - 1] : R), waveAt: i - JP.length }));
  for (const p of parts) {
    if (p.parent !== "body" || /^tail/.test(p.id) || !p.pos) continue;
    const i = spineOf(J, p.pos[0] + R[0]);
    if (i) { p.parent = `vert${i}`; p.pos = sub(add(p.pos, R), JP[i - 1]); }
  }
  parts.splice(1, 0, ...links);
}
// the neck's S: a point and its radius at t (0 its root .. 1 the skull), and its forward-down side
function neckCurve(P) {
  const [nax, nay, , nbx, nby, , nr0, nr1] = P.neck, N = [nax, nay], Bn = [nbx, nby], bow = P.serpent ? .1 : .14;
  const nd = unit(sub(Bn, N)), nn = [nd[1], -nd[0]];
  const at = (t) => { const p = lerp(N, Bn, t), w = Math.sin(t * Math.PI * 2) * bow; return [...add(p, mul([-nn[0], -nn[1]], w)), nr0 + (nr1 - nr0) * Math.min(1, t) ** .8]; };
  return { at, nn, nd };
}
function bodySculpt(kind, P, o, cc, col, wing, parts) {
  const g0 = P.serpent ? P.front[4] : (P.front[4] + P.rear[4]) / 2, FR = { o: [0, P.front[1], 0], u: [1, 0, 0], v: [0, 1, 0], r: g0 * 1.05 }, DR = { ...FR, r: g0 * 2.4 };
  const sh = [], SK = { pat: "scales", frame: FR }, PL = { pat: "scutes", frame: FR }, HF = { pat: "scales", frame: { o: P.head.slice(0, 3), u: [1, 0, 0], v: [0, 1, 0], r: P.head[3] * 1.9 } };
  const body = cc.body, front = cc.front ?? shade(body, 1.3), head = cc.head ?? body, muzzle = cc.muzzle ?? head, leg = cc.leg ?? body,
        foot = cc.foot ?? shade(leg, .8), nose = cc.nose ?? shade(head, .35), tooth = 0xeee6cc;
  const E = (id, c, r, color, x = {}) => sh.push({ id, type: "ell", c, r, color, k: .1, ...SK, ...x });
  const T = (id, pts, color, x = {}) => sh.push({ id, type: "tube", pts, color, k: .08, ...SK, ...x });
  const C = (id, a, b, ra, rb, color, x = {}) => sh.push({ id, type: "cone", a, b, ra, rb, color, k: .04, ...SK, ...x });
  const serpent = !!P.serpent, [fx, fy, , fl, fh, fw] = P.front, [rx, ry, , rl, rh, rw] = P.rear;
  // ---- the trunk
  if (!serpent) {
    // (pass 4: it was a barrel, a ball head-on with saddlebags at the hips: the chest now deep and narrow, tapering to
    //  a slim waist, the haunches and thighs drawn in to the body's line)
    // (pass 5: still a ball head-on -- now a WEDGE: broad over the shoulders, narrowing down the ribs to a keel)
    E("chest", [fx + .05 * fl, fy + .12 * fh, 0], [.76 * fl, .74 * fh, .5 * fw], body, { k: .2 });
    E("keel", [fx + .28 * fl, fy - .5 * fh, 0], [.62 * fl, .48 * fh, .26 * fw], body, { k: .16, rot: [0, 0, -10] });   // (the chest deeper than wide)
    E("withers", [fx - .25 * fl, fy + .6 * fh, 0], [.7 * fl, .28 * fh, .52 * fw], body, { k: .16 });
    const wx = (fx - .4 * fl + rx + .3 * rl) / 2, wy = (fy + ry) / 2;
    E("waist", [wx, wy + .16 * rh, 0], [Math.abs(fx - rx) * .55, .5 * (fh + rh) / 2, .44 * (fw + rw) / 2], body, { k: .26 });

    E("haunch", [rx - .2 * rl, ry + .16 * rh, 0], [.56 * rl, .66 * rh, .58 * rw], body, { k: .22 });
    E("rump", [rx - .62 * rl, ry + .08 * rh, 0], [.4 * rl, .52 * rh, .46 * rw], body, { k: .2 });
    // the belly's plates: one band down the underside, chest to vent, just under the skin of it (the waist tucked up)
    const vr = .24 * (fw + rw) / 2;
    T("ventral", [[fx + .62 * fl, fy - .5 * fh, 0, vr * .8], [fx + .15 * fl, fy - .86 * fh + vr * .75, 0, vr], [wx, wy + .1 * rh - .6 * (fh + rh) / 2 + vr * .7, 0, vr * .92],
                  [rx + .05 * rl, ry - .62 * rh + vr * .75, 0, vr * .95], [rx - .7 * rl, ry - .3 * rh, 0, vr * .7]], front, { k: .06, kc: .025, ...PL });
    // the back's ridge: a low band along the spine, its scales twice the flanks'
    const top = (fh + rh) / 2 * .62 + .1 * rh, dr = .3 * (fw + rw) / 2;
    T("dorsum", [[fx - .1 * fl, fy + .8 * fh - dr * .6, 0, dr * .8], [wx, wy + top - dr * .62, 0, dr], [rx - .2 * rl, ry + .86 * rh - dr * .62, 0, dr * .95],
                 [rx - .75 * rl, ry + .5 * rh - dr * .62, 0, dr * .8]], body, { k: .1, pat: "scales", frame: DR });
    if (wing) {   // the flight muscles over the shoulder blades, the wing's root in them
      const S0 = wing.geo.S0;
      E("wingMound", [S0[0] - .05 * fl, S0[1] - .1 * fh, S0[2] * .72], [.48 * fl, .3 * fh, .3 * fw], body, { k: .14, rot: [-18, 0, -6], mirror: true });
      E("scapula", [S0[0] - .35 * fl, S0[1] - .04 * fh, S0[2] * .45], [.4 * fl, .2 * fh, .22 * fw], body, { k: .12, rot: [0, 0, 14], mirror: true });
    }
  } else {   // a serpent's trunk: one long body in gentle waves, the legs where it dips
    const y0 = P.tail[0][1], xF = P.legs.front[0], xH = P.legs.hind[0], line = trunkLine(P), J = spineJoints(P), on = (x) => spineBone(spineOf(J, x));
    for (const [b, pts] of splitTube(line, J)) {   // (on the spine's links: it bends with the wave)
      T(`trunk_${b}`, pts, body, { k: .1, bone: b });
      T(`dorsum_${b}`, pts.map(([x, y, z, r]) => [x, y + r * .42, z, r * .62]), body, { k: .06, pat: "scales", frame: DR, bone: b });
      T(`trunkBelly_${b}`, pts.map(([x, y, z, r]) => [x, y - r * .42, z, r * .66]), front, { k: .05, kc: .02, ...PL, bone: b });
    }
    E("shoulder", [xF + .05, y0 + .02, .12], [.32, .2, .17], body, { k: .12, mirror: true, bone: on(xF) });
    E("hip", [xH, y0 - .02, .1], [.3, .2, .16], body, { k: .12, mirror: true });
    if (wing) E("wingMound", add(wing.geo.S0, [-.05, -.12, -wing.geo.S0[2] * .4]), [.32, .16, .18], body, { k: .1, rot: [-20, 0, 0], mirror: true, bone: on(wing.geo.S0[0]) });
  }
  // ---- the neck: an S, from the chest up and forward to the back of the skull, its throat in plates
  const [nax, nay, , nbx, nby, , nr0, nr1] = P.neck, [hx, hy, , hr] = P.head, N = [nax, nay], Bn = [nbx, nby];
  const NC = neckCurve(P), nn = NC.nn, nPts = [0, .25, .5, .75, 1.04].map((t) => { const [x, y, r] = NC.at(t); return [x, y, 0, r]; });
  if (!serpent) nPts.unshift([nax - .25 * fl, nay - .15, 0, nr0 * 1.15]);
  T("neck", nPts, body, { bone: "neck", k: .14 });
  T("throat", nPts.slice(serpent ? 0 : 1).map(([x, y, , r]) => [x + nn[0] * r * .38, y + nn[1] * r * .38, 0, r * .68]), front, { bone: "neck", k: .06, kc: .02, ...PL });
  // ---- the head (H its pivot; the snout runs on to the nose, the plan's own)
  const H = [hx, hy, 0], nz = P.nose, Lh = Math.hypot(nz[0] - hx, nz[1] - hy), dn = unit([nz[0] - hx, nz[1] - hy, 0]), up = [-dn[1], dn[0], 0];
  const at = (a, u, z = 0) => add(add(H, mul(dn, a * Lh)), [up[0] * u * hr, up[1] * u * hr, z * hr]);   // a: along to the nose (0..1), u: up, z: out (head radii)
  const HB = { bone: "head", ...HF }, hk = hr * .22;
  E("skull", at(-.04, .14), [.78 * hr, .62 * hr, .64 * hr], head, { ...HB, k: hk });
  E("occiput", at(-.26, .02), [.5 * hr, .56 * hr, .52 * hr], head, { ...HB, k: hk });
  E("brow", at(.22, .6, .5), [.52 * hr, .16 * hr, .22 * hr], head, { ...HB, k: hk * .45, rot: [0, 0, -12], mirror: true });   // (overhanging the eye)
  E("cheek", at(-.08, -.18, .44), [.52 * hr, .42 * hr, .34 * hr], head, { ...HB, k: hk * .7, mirror: true });
  E("snout", at(.5, -.02), [.5 * Lh, .33 * hr, .44 * hr], muzzle, { ...HB, k: hk * .8, rot: [0, 0, Math.atan2(dn[1], dn[0]) / D2R] });
  C("bridge", at(.18, .42), at(.84, .2), .22 * hr, .14 * hr, head, { ...HB, k: hk * .5 });
  E("nosePad", at(.93, .0), [.24 * hr, .26 * hr, .3 * hr], muzzle, { ...HB, k: hk * .6 });
  E("nostril", at(.95, .16, .17), [.12 * hr, .03 * hr, .07 * hr], shade(muzzle, .5), { ...HB, k: hk * .2, kc: .004, pat: 0, mirror: true, rot: [0, 25, 12] });   // (a slit, sunk in the pad)
  // the lip: a dark groove from the corner of the mouth to the snout's tip, the teeth hanging from it
  const lipZ = (a) => (.5 - .26 * a * a) * .7, lipU = (a) => -.24 - .04 * a;   // (pass 5: seated -- at .5 it stood off the cheek, a rod past the mouth)
  // (pass 6: its ends sunk and thinned -- the back end deep in the cheek crumpled the mouth's corner, the front stood out)
  //  -- and each point set to just touch the surface, so it reads as one even line, not specks where it broke through)
  const lipF = [1.1, 1.1, 1.24, 1.17, .58];
  T("lip", [.2, .36, .55, .8, .97].map((a, i) => [...at(a, lipU(a), lipZ(a) * lipF[i]), .028 * hr * (i === 0 || i === 4 ? .55 : 1)]), shade(muzzle, .4), { ...HB, k: .01 * hr, pat: 0, mirror: true });
  E("jaw", at(.42, -.42), [.5 * Lh, .2 * hr, .36 * hr], muzzle, { ...HB, k: hk * .6, rot: [0, 0, Math.atan2(dn[1], dn[0]) / D2R + 4] });
  E("chin", at(.86, -.36), [.2 * hr, .15 * hr, .22 * hr], muzzle, { ...HB, k: hk * .5 });
  E("gular", at(-.08, -.6), [.6 * hr, .26 * hr, .34 * hr], front, { ...HB, k: hk * .6, kc: .01, ...PL });
  for (let i = 0; i < 5; i++) {   // the teeth along the upper jaw, the fourth the longest (a fang)
    const a = .3 + i * .14, l = (i === 3 ? .3 : .17) * hr, A = at(a, lipU(a) + .02, lipZ(a) * 1.18 - .05);   // (the teeth just outside the lip that seats them)
    C(`tooth${i}`, A, add(A, mul(up, -l)), .055 * hr, .008 * hr, tooth, { ...HB, k: 0, pat: 0, mirror: true });
  }
  if (serpent) E("noseKnob", at(.72, .38), [.22 * hr, .13 * hr, .2 * hr], head, { ...HB, k: hk * .5 });
  // frill spines behind the jaw (no mammal's ears): three, fanned back and out
  for (let i = 0; i < 3; i++) {
    const A = at(-.38 - i * .06, .2 - i * .28, .5 - i * .04), d = unit([-1, .35 - i * .3, .55]), l = (.62 - i * .12) * hr;
    // (pass 7: rooted a third of its length back inside the head -- set on the surface, the lowest floated a centimetre off the jaw)
    C(`frill${i}`, add(A, mul(d, -.3 * l)), add(A, mul(d, l)), .1 * hr, .01 * hr, col.spike, { ...HB, k: .015 * hr, pat: 0, mirror: true });
  }
  // ---- the legs: muscle on the IK bones, each leg its own frame
  const [rH, rK, rA] = P.legs.radii, ft = P.legs.foot, uF = P.legs.front[3], uH = P.legs.hind[3];
  for (const [tag, u] of P.biped ? [["H", uH]] : [["F", uF], ["H", uH]]) {
    const hip = `$leg${tag}Lu`, knee = `$leg${tag}Ll`, ank = `$foot${tag}L`, L = { mirror: true };
    if (tag === "F") {
      T("upperArm", [[hip, .05 * u, .1 * u, -.06 * u, rH * 1.15], [hip, .02 * u, -.4 * u, 0, rH * 1.05], [knee, -.04 * u, .04 * u, 0, rK * .9]], leg, { ...L, bone: `leg${tag}Lu`, k: .1 });
      E("triceps", [hip, -.12 * u, -.35 * u, 0], [rH * .7, .42 * u, rH * .75], leg, { ...L, bone: `leg${tag}Lu`, k: .08 });
    } else {
      E("thigh", [hip, .1 * u, -.16 * u, -.14 * u], [rH * 1.6, .58 * u, rH * .7], leg, { ...L, bone: `leg${tag}Lu`, k: .16, rot: [0, 0, 16] });   // (in against the flank: no saddlebag)
      T("upperLeg", [[hip, 0, 0, -.07 * u, rH * 1.05], [knee, .02 * u, .06 * u, 0, rK * 1.02]], leg, { ...L, bone: `leg${tag}Lu`, k: .1 });
    }
    T(`shin${tag}`, [[knee, 0, 0, 0, rK * 1.08], [knee, tag === "F" ? .03 : -.04, -.3 * u, 0, rK * .92], [ank, 0, .08, 0, rA * .82]], leg, { ...L, bone: `leg${tag}Ll`, k: .07 });
    E(`foot${tag}`, [ank, ft[0] * .3, -ft[1] * .25, 0], [ft[0] * .85, ft[1] * .85, ft[2] * .95], foot, { ...L, bone: `foot${tag}L`, k: .05 });
    // the toes, splayed, each with its claw (an eagle's on a lung: five, four or three -- the definition's count)
    const nT = o.claws ?? 3, J = P.legs.foot;
    for (let i = 0; i < nT; i++) {
      const a = ((i - (nT - 1) / 2) / Math.max(1, (nT - 1) / 2)) * (nT > 3 ? .55 : .5), dir = [Math.cos(a), 0, Math.sin(a)];
      const A0 = [ank, J[0] * .45, -J[1] * .35, 0], tl = J[0] * (1.05 - .25 * Math.abs(a)), Tt = [ank, J[0] * .45 + dir[0] * tl, -J[1] * .62, dir[2] * tl];
      C(`toe${tag}${i}`, A0, Tt, J[2] * .3, J[2] * .17, foot, { ...L, bone: `foot${tag}L`, k: J[2] * .12, pat: 0 });
      C(`claw${tag}${i}`, Tt, [ank, J[0] * .45 + dir[0] * (tl + J[0] * .42), -J[1] * .98, dir[2] * (tl + J[0] * .42)], J[2] * .15, J[2] * .02, col.claw, { ...L, bone: `foot${tag}L`, k: 0, pat: 0 });
    }
  }
  // ---- the tail: on the rig's own links (their tubes no longer drawn), the underside in plates
  const links = parts.filter((p) => /^tail\d*$/.test(p.id) && p.shape === "tube");
  links.forEach((p, i) => {
    const id = p.id, nx = links[i + 1] ? `$${links[i + 1].id}` : `$${id}.end`, ra = p.size.r1, rb = p.size.r2, rm = (ra + rb) / 2;
    T(`tailSkin${i}`, [[`$${id}`, 0, 0, 0, ra], [`$${id}.mid`, 0, 0, 0, rm], [nx, 0, 0, 0, rb]], cc.tail ?? body, { bone: id, k: .06 });   // (scaled like the trunk: the rig's tube wore no pattern)
    T(`tailBelly${i}`, [[`$${id}`, 0, -ra * .48, 0, ra * .62], [`$${id}.mid`, 0, -rm * .48, 0, rm * .62], [nx, 0, -rb * .48, 0, rb * .62]], front, { bone: id, k: .03, kc: .015, ...PL });
  });
  if (!serpent) T("tailRoot", [[rx - .7 * rl, ry + .05, 0, rh * .62], [P.tail[0][0], P.tail[0][1], 0, P.tr[0] * 1.02], [`$tail.mid`, 0, 0, 0, P.tr[0] * .92]], body, { bone: "tail", k: .12 });
  // ---- the wings
  if (wing && wing.geo.fingers) {   // bat: the arm's bones and the fingers, a thumb claw at the wrist
    const g = wing.geo, k = g.k, kb = Math.min(k, 2.6), A = { bone: "wArmL", mirror: true, pat: 0 }, Hd = { bone: "wHandL", mirror: true, pat: 0 }, Fo = { bone: "wForeL", mirror: true, pat: 0 };
    T("wingRoot", [[...g.S0, .085 * k], [...lerp(g.S0, g.Elb, .3), .058 * k]], body, { ...SK, bone: "wArmL", mirror: true, k: .06 });
    // (the bones' girth that of a 2.6 wing however long they grow: thicker, the grid would melt them into webs)
    C("humerus", lerp(g.S0, g.Elb, .22), g.Elb, .02 * kb, .018 * kb, col.bone, { ...A, k: 0 });
    C("forearm", g.Elb, g.W, .019 * kb, .016 * kb, col.bone, { ...Fo, k: 0 });
    C("thumb", g.W, g.thumb, .019 * kb, .004 * kb, col.claw, { ...Hd, k: 0 });
    g.fingers.forEach((f, i) => {
      const Fd = { bone: `${f.bone}L`, mirror: true, pat: 0, k: 0 };
      // (thin enough to be drawn as they are: in the grid, closed together at rest, they would melt into one web
      //  that stretches as the hand opens in flight)
      C(`finger${i}`, g.W, f.knuckle, .018 * kb, .016 * kb, col.bone, Fd);
      C(`finger${i}b`, f.knuckle, f.tip, .016 * kb, .006 * kb, col.bone, Fd);
    });
  }
  if (wing && wing.geo.fh) {   // feathered: primaries on the hand, secondaries along the forearm, coverts over their roots
    const { k, E: Ea, HL, fa, fh, up: wu } = wing.geo, d = (a) => [-Math.sin(a * D2R), Math.cos(a * D2R), 0];
    const row = (F, y, a, len, w, bone) => ({ at: F.pt([0, y, 0]), dir: F.dir(d(a)), len, w, bone });
    const fcol = col.feather, ftip = col.tip, base = { type: "feathers", mirror: true, up: wu, color: fcol };
    sh.push({ ...base, id: "primaries", rows: [row(fh, HL, 6, .78 * k, .12 * k, "wHandL"), row(fh, HL * .5, 34, .7 * k, .12 * k, "wHandL"), row(fh, 0, 66, .58 * k, .12 * k, "wHandL")],
              n: 7, outline: "flight", tip: ftip, camber: .1, curve: -.03, seed: 11 });
    sh.push({ ...base, id: "secondaries", rows: [row(fa, Ea, 80, .55 * k, .12 * k, "wArmL"), row(fa, Ea * .55, 88, .5 * k, .12 * k, "wArmL"), row(fa, Ea * .12, 96, .46 * k, .12 * k, "wArmL")],
              n: 7, outline: "flight", tip: shade(ftip, 1.15), camber: .1, curve: -.02, seed: 12 });
    sh.push({ ...base, id: "coverts", rows: [row(fh, HL * .9, 30, .32 * k, .07 * k, "wHandL"), row(fa, Ea, 85, .3 * k, .08 * k, "wArmL"), row(fa, Ea * .1, 95, .28 * k, .08 * k, "wArmL")],
              n: 7, outline: "round", color: shade(fcol, 1.08), tip: fcol, camber: .14, lift: .015 * k, seed: 13 });
    T("wingArm", [[...fa.o, .05 * k], [...fa.pt([0, Ea * .5, 0]), .034 * k], [...fa.pt([0, Ea, 0]), .028 * k]], fcol, { bone: "wArmL", mirror: true, pat: 0, k: .02 });
    // (the hand's bone out to the outermost primary's root, HL: it ended at .9 HL, and that feather hung 7 cm off its end)
    T("wingHand", [[...fh.pt([0, 0, 0]), .028 * k], [...fh.pt([0, HL, 0]), .016 * k]], fcol, { bone: "wHandL", mirror: true, pat: 0, k: .02 });
  }
  const keep = ["tail\\d*Crest\\d+", "tail(Spade|Blade|Club|Flame)\\S*", "spine\\d+b?", "horn\\S*", "noseHorn", "antler\\S*", "tine\\S*", "plume\\S*",
                "wMem\\S*", "whisker\\S*", "lock\\S*", "beard\\S*", "mane\\S*", "elbow\\S*"];
  const [ex, ey, ez, er] = P.eyes;
  const eyes = { at: [ex, ey, ez], from: [hx - .1 * hr, ey - .1 * hr, 0], r: er, iris: cc.eye ?? 0xe0b030, pupil: "slit", sink: serpent ? .55 : .45, socket: 1.35, lid: shade(head, .6) };
  return { shape: sh, keep, eyes, patScale: P.patScale ?? 3, mesh: { tris: serpent ? [wing ? 4400 : 5400, 1300] : wing ? [6200, 1500] : [6600, 1700], cell: P.cell } };
}

export function dragonDef(d) {
  const st = d.dragon ?? {}, bodyKind = PLANS[st.body] ? st.body : "western", P = PLANS[bodyKind];
  const o = { ...DEFAULTS[bodyKind], ...st }, c = { ...(d.c ?? {}) };
  const body = c.body ?? 0x4a7040;
  const col = {
    spike: c.spike ?? shade(body, .78), horn: c.horn ?? 0xd8cbb0, bone: c.bone ?? shade(body, .85), mem: c.mem ?? shade(body, .55),
    mane: c.mane ?? shade(body, .6), whisker: c.whisker ?? c.mane ?? shade(body, .6), claw: c.claw ?? 0x2a2620,
    feather: c.feather ?? body, tip: c.tip ?? shade(body, .6),
  };
  const extras = [], hl = o.hornLen ?? 1, sp = (o.spikeSize ?? 1) * P.spike, skinC = c.head ?? body;
  const [hx, hy, , hr] = P.head, H = [hx, hy, 0];
  const snout = P.muzzle.length === 8 ? [P.muzzle[3] + P.muzzle[7] * .6, P.muzzle[4], 0] : [P.muzzle[0] + P.muzzle[3] * .8, P.muzzle[1], 0];

  // ---- the line of the back: its top at x (the two lobes' soft maximum, as mammal() draws the torso)
  const ellR = (el, x) => { const t = (x - el[0]) / el[3]; return Math.abs(t) >= 1 ? 0 : Math.sqrt(1 - t * t) * (el[4] + el[5]) / 2; };
  const top = (x) => {
    const a = ellR(P.rear, x), b = ellR(P.front, x), f = Math.min(1, Math.max(0, (x - P.rear[0]) / (P.front[0] - P.rear[0])));
    return P.rear[1] + (P.front[1] - P.rear[1]) * f + Math.cbrt(a ** 3 + b ** 3);
  };
  // the dorsal stations: [point, along (unit, toward the head), up (unit)] down the back and up the neck
  const stations = [];
  if (o.spikes !== "none") {
    const step = Math.max(.18, sp * (o.spikes === "fin" ? .9 : o.spikes === "plate" ? 1.25 : o.spikes === "tuft" ? 1.6 : 1.2));
    const x0 = P.rear[0] - P.rear[3] * .75, x1 = P.front[0] + P.front[3] * .45;
    if (P.serpent) {   // (along the trunk's crest, side to side with it)
      const L = trunkLine(P), seg = [];
      for (let i = 0; i + 1 < L.length; i++) seg.push([L[i], L[i + 1], Math.hypot(L[i + 1][0] - L[i][0], L[i + 1][1] - L[i][1], L[i + 1][2] - L[i][2])]);
      const tot = seg.reduce((a, q) => a + q[2], 0);
      for (let d = step * .5; d < tot - step * .3; d += step) {
        let e = d, j = 0; while (j < seg.length - 1 && e > seg[j][2]) e -= seg[j++][2];
        const [A, B, l] = seg[j], t = Math.min(1, e / l), p = A.map((v, m) => v + (B[m] - v) * t), al = unit(sub(B.slice(0, 3), A.slice(0, 3))), up = unit([-al[1], al[0], 0]);
        stations.push([add(p.slice(0, 3), mul(up, p[3] * .9)), al, up, 1]);
      }
    } else for (let x = x0; x <= x1; x += step) stations.push([[x, top(x) - .04, 0], unit([step, top(x + .05) - top(x - .05), 0]), [0, 1, 0], 1]);
    const NC = neckCurve(P), nl = Math.hypot(P.neck[3] - P.neck[0], P.neck[4] - P.neck[1]);
    for (let t = .25; t < .95; t += step * .85 / nl) {   // (up the neck's S: they nod with it -- skeleton.js part.nod, the flight pose's neck too)
      const [x, y, r] = NC.at(t), [x2, y2] = NC.at(t + .02), al = unit([x2 - x, y2 - y, 0]), up = unit([-al[1], al[0], 0]);
      stations.push([add([x, y, 0], mul(up, r * .8)), al, up, .75 + .25 * (1 - t), true]);
    }
  }
  // ...and a spike, plate, fin or tuft at each (back: the -along way, the tail's)
  stations.forEach(([p, al, up, g, nod], i) => {
    if (P.seat && !nod && Math.abs(p[0] - P.seat[0]) < .38) return;   // (a gap in the row where the rider sits: species.js saddle)
    const h = sp * g * (o.spikes === "plate" ? 1.3 : 1), back = mul(al, -1), id = `spine${i}`;
    const N = nod ? { nod: true } : {};
    // (pass 6: from above, their dark round bases read as a row of holes down the spine -- slimmer now, leaning back)
    if (o.spikes === "spike") extras.push({ id, parent: "body", from: p, to: add(p, add(mul(up, h), mul(back, h * .85))), r1: h * .22, r2: h * .035, color: col.spike, k: .03, ...N });
    else if (o.spikes === "plate" || o.spikes === "fin") {
      const w = o.spikes === "fin" ? h * .75 : h * .45, tip = add(mul(up, h), mul(back, h * (o.spikes === "fin" ? .6 : .25)));
      extras.push({ raw: { id, parent: "body", shape: "tri", size: { a: mul(al, w), b: mul(back, w), c: tip, r: .025 + h * .02 },
                           color: o.spikes === "fin" ? col.mem : col.spike, k: 0, ...N }, at: [p[0], p[1] - (o.spikes === "plate" ? .07 : 0), i % 2 && o.spikes === "plate" ? .04 : 0] });   // (pass 7: a plate's base sunk -- on the back's ridge its corners stood off it)
    } else if (o.spikes === "tuft") {   // (a flame of hair: two locks, the lean of a fire in the wind)
      extras.push({ id, parent: "body", from: p, to: add(p, add(mul(up, h * .9), mul(back, h))), r1: h * .28, r2: h * .03, color: col.spike, k: .02, ...N });
      if (i % 2 === 0) extras.push({ id: id + "b", parent: "body", from: add(p, mul(back, h * .25)), to: add(p, add(mul(up, h * .5), mul(back, h * 1.15))), r1: h * .2, r2: h * .02, color: col.mane, k: .02, ...N });
    }
  });

  // ---- horns (on the head: they turn with it)
  // (pass 7: ONE CLEAN PIECE EACH. A horn was a few pills meeting end to end, and some were half in the sculpt's grid
  //  and half drawn as details (bodyspec.js: a piece under .8 of the grid's cell is drawn exactly, a thicker one goes
  //  in the grid). Where they met it came out pinched or broken: the grid can't hold a tube less than a cell or two
  //  across. At each kink, too, the outside of the bend opened a wedge. Now the whole horn is a chain of exact pieces
  //  along one smooth curve -- one tube (a single lathe: pills end to end showed a knob at every joint) or one straight cone. Where the horn is thicker than that at its
  //  root, a short boss in the grid blends it into the skull. t_horns.mjs checks the chain.)
  const Hb = [hx - hr * .35, hy + hr * .78, hr * .42];   // where they grow: the back of the skull, its left
  const rcap = .75 * P.cell;                              // (the thickest a piece may be and still be drawn exactly)
  const pills = (id, list, color) => list.forEach(([a, b, r1, r2], i) => extras.push({ id: `${id}${i}`, parent: "head", mirror: true, from: a, to: b, r1, r2, color, k: 0 }));
  // the curve a horn runs along: at(t), t 0 at its root to 1 at its tip, and on past either end in a straight line
  const poly = (pts) => {   // (by arc length along a dense polyline)
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(...sub(pts[i], pts[i - 1])));
    const tot = cum.at(-1);
    return (t) => {
      const d = t * tot; let i = 0; while (i < pts.length - 2 && cum[i + 1] < d) i++;
      return lerp(pts[i], pts[i + 1], (d - cum[i]) / (cum[i + 1] - cum[i]));
    };
  };
  const bspline = (p, per = 10) => {   // (the curve a path chain draws: through the sides' middles, its corners the controls)
    if (p.length < 3) return p;
    const mid = (a, b) => lerp(a, b, .5), out = [p[0]];
    p.slice(1, -1).forEach((C, i) => { const A = i ? mid(p[i], C) : p[0], B = i === p.length - 3 ? p.at(-1) : mid(C, p[i + 2]);
      for (let j = 1; j <= per; j++) { const t = j / per, u = 1 - t; out.push(A.map((v, k) => u * u * v + 2 * u * t * C[k] + t * t * B[k])); } });
    return out;
  };
  // a horn along the control polygon `ctrl` (the curve a path chain draws through it), radius r0 at the root to r1
  // at the tip: ONE TUBE (n 0) -- a single lathe, no joints -- or, straight, n exact cones end to end
  const horn = (id, ctrl, r0, r1, color, n = 0, back = .12) => {
    const rd0 = Math.min(rcap, r0), at = poly(bspline(ctrl)), root = add(ctrl[0], mul(sub(ctrl[0], ctrl[1]), back * 1.6));
    if (!n) extras.push({ id, parent: "head", mirror: true, color, k: 0, pat: null, path: { path: [root, ...ctrl.slice(1)], r1: rd0, r2: r1, sway: 0, speed: 0 } });
    else for (let i = 0; i < n; i++) {
      const t0 = i ? i / n : -back, t1 = (i + 1) / n, rd = (t) => rd0 + (r1 - rd0) * Math.max(0, t);
      extras.push({ id: `${id}${i}`, parent: "head", mirror: true, from: at(t0), to: at(t1), r1: rd(t0), r2: rd(t1), color, k: 0 });
    }
    // (the boss: short, and only a little thicker than the horn where it leaves it -- a collar read as a block)
    // (ledger pass: in the head's own scales and blended into the skull, k a third of its girth -- horn-coloured and
    //  unblended it stood on the scales as a faceted cream block; now a scaly mound the horn grows out of)
    if (r0 > rcap * 1.1) extras.push({ id: `${id}Boss`, parent: "head", mirror: true, from: at(-back * 1.4), to: at(.05), r1: r0, r2: rcap * 1.02, color: skinC, k: r0 * .35 });
  };
  const L = hr * 2.2 * hl;
  if (o.horns === "swept") {   // (back, out and gently down at the tip, one curve)
    horn("horn", [Hb, add(Hb, [-.5 * L, .4 * L, .07 * L]), add(Hb, [-1.0 * L, .45 * L, .14 * L]), add(Hb, [-1.35 * L, .3 * L, .17 * L])], hr * .24, hr * .02, col.horn);
  }
  else if (o.horns === "straight") {   // (one exact cone: in the grid its thin tip came out wavy)
    horn("horn", [Hb, add(Hb, [-.9 * L, .75 * L, .2 * L])], hr * .22, hr * .015, col.horn, 1);
  }
  else if (o.horns === "curl") {   // a ram's: back, down and forward again beside the jaw, drifting out
    const C = add(Hb, [-.32 * L, -.12 * L, 0]), R = .34 * L, a0 = Math.atan2(Hb[1] - C[1], Hb[0] - C[0]);
    // (its plane tilted 32 degrees, flaring out as it comes down: a tube's rings twist where it runs within ~25 degrees
    //  of the vertical, which an upright curl must -- and a ram's horn spirals outward anyway)
    const tc = Math.cos(.56), ts = Math.sin(.56);
    const pts = Array.from({ length: 8 }, (_, i) => { const a = a0 + i * .62, rr = R * (1 - i * .045), dy = C[1] + rr * Math.sin(a) - Hb[1], dz = i * .045 * L;
      return [C[0] + rr * Math.cos(a), Hb[1] + dy * tc - dz * ts, Hb[2] - dy * ts + dz * tc]; });
    horn("horn", [Hb, ...pts.slice(1)], hr * .3, hr * .07, col.horn);
  } else if (o.horns === "crown") {   // a crown of them round the back of the skull, the middle pair the longest
    for (let i = 0; i < 4; i++) {
      // (ledger pass: the roots in on the skull -- at .25 + .5 the lower pair stood off the cheek, their cut ends showing)
      const a = .4 + i * .42, root = [hx - hr * (.15 + .25 * Math.sin(a)), hy + hr * .8 * Math.cos(a), hr * (.2 + .36 * Math.sin(a))];
      const l = L * (i === 1 ? 1 : i === 0 ? .8 : .6);
      horn(`horn${"abcd"[i]}`, [root, add(root, [-.8 * l, .45 * l * Math.cos(a), .25 * l * Math.sin(a)])], hr * .16, hr * .025, col.horn, 1, .25);   // (sunk a quarter of its length: its root end inside the skull)
    }
  } else if (o.horns === "antlers") {   // a deer's, as the Chinese draw them: a beam back and up, two tines forward
    const a = [hx - hr * .25, hy + hr * .85, hr * .3], b = add(a, [-.28 * L, .45 * L, .1 * L]), m = add(a, [-.48 * L, .85 * L, .25 * L]), e = add(a, [-.84 * L, 1.05 * L, .33 * L]);   // (no steeper than ~60 degrees: see the curl)
    const beam = poly(bspline([add(a, mul(sub(a, b), .12 * 1.6)), b, m, e])), r0 = hr * .14, r1 = hr * .045;   // (the tube's own curve, from its root inside the skull)
    horn("antler", [a, b, m, e], r0, r1, col.horn);
    // (the tines grow from the beam's own axis -- they were set on the corners' lines, off the curve it draws)
    const beamR = (t) => Math.min(rcap, r0) + (r1 - Math.min(rcap, r0)) * t;
    [[.3, [.28 * L, .32 * L, .04 * L], .08], [.55, [.12 * L, .42 * L, .03 * L], .07], [.82, [-.05 * L, .3 * L, .06 * L], .06]].forEach(([t, dir, r], i) => {
      const at = beam(t), rr = Math.min(hr * r, beamR(t) * .85);
      extras.push({ id: `tine${i}`, parent: "head", mirror: true, from: at, to: add(at, dir), r1: rr, r2: hr * r * .3, color: col.horn, k: 0 });
    });
  } else if (o.horns === "plume") {   // a crest of feathers fanned back from the crown
    const list = [];
    for (let i = 0; i < 5; i++) { const root = [hx - hr * .2, hy + hr * .8, hr * (.1 + i * .09)], l = L * (1.3 - i * .15), a = .25 + i * .2;
      list.push([root, add(root, [-l * Math.cos(a), l * Math.sin(a) * .9 + l * .3, i * .06 * L]), hr * .1, hr * .04]); }
    pills("plume", list, col.feather);
    pills("plumeTip", list.map(([r, t]) => [lerp(r, t, .7), add(t, mul(sub(t, r), .12)), hr * .07, hr * .03]), col.tip);
  }
  if (o.nose) {   // (a rhino's, on the snout; one exact cone too)
    const A = add(snout, [-hr * .55, hr * .35, 0]), B = add(snout, [-hr * .75, hr * 1.2 * hl, 0]), r0 = hr * .17, rd0 = Math.min(rcap, r0);
    extras.push({ id: "noseHorn", parent: "head", from: lerp(A, B, -.1), to: B, r1: rd0, r2: hr * .02, color: col.horn, k: 0 });
    if (r0 > rcap * 1.1) extras.push({ id: "hornNoseBoss", parent: "head", from: lerp(A, B, -.18), to: lerp(A, B, .07), r1: r0, r2: Math.max(rcap * 1.1, r0 * .78), color: col.horn, k: .015 });
  }

  // ---- the lung's hair: whiskers from the lip, brows streaming back, a beard, a mane down the neck
  if (o.whiskers) {
    const w0 = add(snout, [-hr * .25, -hr * .05, hr * .2]), l = hr * 3.2;
    extras.push({ id: "whisker", parent: "head", mirror: true, color: col.whisker, k: 0, pat: null,
                  path: { path: [w0, add(w0, [.1 * l, -.03 * l, .12 * l]), add(w0, [.1 * l, -.05 * l, .26 * l]), add(w0, [-.04 * l, -.05 * l, .36 * l]), add(w0, [-.24 * l, -.02 * l, .44 * l]),
                                         add(w0, [-.47 * l, .04 * l, .5 * l]), add(w0, [-.72 * l, .12 * l, .54 * l])],   // (rising back: the head is pitched down)
                          r1: hr * .065, r2: hr * .008, sway: 10, speed: .5 } });   // (trailing back along the neck, not arcing to the ground)
  }
  if (o.brows) {
    const b0 = [P.eyes[0] - hr * .05, P.eyes[1] + hr * .25, hr * .3], l = hr * 3.4;
    extras.push({ id: "lock", parent: "head", mirror: true, color: col.whisker, k: 0, pat: null,
                  path: { path: [b0, add(b0, [-.25 * l, .2 * l, .1 * l]), add(b0, [-.6 * l, .15 * l, .25 * l]), add(b0, [-.95 * l, -.1 * l, .3 * l])], r1: hr * .07, r2: hr * .015, sway: 8, speed: .4 } });
  }
  if (o.beard) {
    const chin = [hx + hr * .55, hy - hr * .75, 0], list = [];
    // (2026-11-07: curved locks, each thin enough to be drawn exactly -- thick straight pills were half in the grid and
    //  came out as a fringe of jagged white shards)
    const rl = Math.min(rcap * .92, hr * .1);
    for (let i = 0; i < 3; i++) {
      const b0 = add(chin, [-i * hr * .3, 0, hr * (.1 + i * .02)]), l = hr * (1.25 - i * .2);
      extras.push({ id: `beard${i}`, parent: "head", mirror: true, color: col.mane, k: 0, pat: null,
                    path: { path: [b0, add(b0, [-.15 * l, -.4 * l, .06 * l]), add(b0, [-.45 * l, -.75 * l, .12 * l]), add(b0, [-.85 * l, -.9 * l, .16 * l])], r1: rl, r2: hr * .012, sway: 6, speed: .45 } });
    }
  }
  if (o.mane) {   // locks down the back of the neck and on over the shoulders, streaming back
    const NC = neckCurve(P);
    for (let i = 0; i < 7; i++) {
      const t = .95 - i / 7 * .8, [x, y, r] = NC.at(t), [x2, y2] = NC.at(t + .02), al = unit([x2 - x, y2 - y, 0]), up = unit([-al[1], al[0], 0]), p = add([x, y, 0], mul(up, r * .7)), l = hr * (2.3 - i * .1);
      // (2026-11-07: each side two curved locks, an upper streaming back and out, a lower falling over the neck's side --
      //  hair, drawn exactly; straight pills this thick sat half in the grid and read as shards)
      const rl = Math.min(rcap * .92, hr * .13), sw = { sway: 6, speed: .4, phase: i * .7 };
      const a0 = add(p, [0, 0, r * .3]), b0 = add(add(p, mul(up, -r * .35)), [0, 0, r * .62]), lb = l * .72;
      extras.push({ id: `mane${i}`, parent: "body", mirror: true, nod: true, color: col.mane, k: 0, pat: null,
                    path: { path: [a0, add(a0, [-.3 * l, .2 * l, .08 * l]), add(a0, [-.66 * l, .2 * l, .17 * l]), add(a0, [-.98 * l, .02 * l, .24 * l])], r1: rl, r2: hr * .014, ...sw } });
      extras.push({ id: `mane${i}b`, parent: "body", mirror: true, nod: true, color: col.mane, k: 0, pat: null,
                    path: { path: [b0, add(b0, [-.3 * lb, .04 * lb, .16 * lb]), add(b0, [-.62 * lb, -.2 * lb, .26 * lb]), add(b0, [-.9 * lb, -.5 * lb, .3 * lb])], r1: rl * .9, r2: hr * .012, ...sw, phase: i * .7 + 1.3 } });
    }
  }

  // ---- wings
  const wings = o.wings ?? P.wings, wk = P.wingK * (o.wingSpan ?? 1);
  // (the wing's root placed at the shoulder, each side's at its own z; the left one's REST geometry kept for the body)
  const wAt = P.wingAt;
  let wing = null;
  for (const s of [1, -1]) {
    const W = wings === "bat" ? dragonBatWing(s, [wAt[0], wAt[1], s * wAt[2]], { k: wk, bone: col.bone, mem: col.mem, speed: .35, ...P.wingPose })
            : wings === "feather" ? dragonFeatherWing(s, [wAt[0], wAt[1], s * wAt[2]], { k: wk, bone: col.feather, speed: .4, ...P.wingPose }) : null;
    if (!W) continue;
    extras.push(...W.parts.map((p, i) => (i === 0 ? { raw: p, at: [wAt[0], wAt[1], s * wAt[2]] } : { raw: p })));
    if (s > 0) wing = W;
  }

  // ---- the tail: its crest (the back's own row, on down it) and what ends it
  const end = [], tr = P.tr[1], el = sp * 1.8;
  if (o.tailEnd === "spade") for (const s of [1, -1]) end.push({ id: `tailSpade${s > 0 ? "L" : "R"}`, shape: "tri", pos: [0, -el * .15, 0], color: col.spike, k: 0, edge: 0,
                                                                 size: { a: [0, 0, 0], b: [0, el * .5, s * el * .42], c: [0, el * 1.05, 0], r: .03 } });
  else if (o.tailEnd === "blade") for (const s of [1, -1]) end.push({ id: `tailBlade${s > 0 ? "L" : "R"}`, shape: "tri", pos: [0, -el * .2, 0], color: col.spike, k: 0, edge: 0,
                                                                      size: { a: [0, 0, 0], b: [s * el * .3, el * .35, 0], c: [0, el * 1.25, 0], r: .025 } });
  else if (o.tailEnd === "club") {
    end.push({ id: "tailClub", shape: "sphere", size: { r: tr * 5.2 }, pos: [0, tr * 3, 0], color: col.spike, k: .03, edge: 0 });
    for (const [x, z] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) end.push(pill(`tailClubSpike${x}${z}`, "", [x * tr * 4, tr * 3.4, z * tr * 4], [x * tr * 8.5, tr * 5, z * tr * 8.5], tr * 1.5, tr * .15, col.horn));
  } else if (o.tailEnd === "flame" || o.tailEnd === "plume") {   // a fan of locks (the lung's flame) or of feathers
    const cc = o.tailEnd === "flame" ? col.mane : col.feather, l = sp * 4;
    for (let i = 0; i < 7; i++) {
      const a = (i - 3) * .32, z = Math.sin(a), x = (i % 2 ? .35 : -.35) * (1 - Math.abs(z));
      end.push(pill(`tailFlame${i}`, "", [0, -tr, 0], [x * l * .45, l * (1 - .25 * Math.abs(z)), z * l * .5], tr * 2.2, tr * .4, i % 2 ? cc : (o.tailEnd === "plume" ? col.tip : col.spike)));
    }
  }
  const crest = o.spikes === "none" ? null : o.spikes === "plate" || o.spikes === "fin"
    ? { h: sp * 1.1, n: 2, shape: "tri", w: sp * .45, lean: o.spikes === "fin" ? .5 : .2, color: o.spikes === "fin" ? col.mem : col.spike, r: .08 }
    : { h: sp * (o.spikes === "tuft" ? 1.0 : .9), n: 2, lean: o.spikes === "tuft" ? 1.1 : .5, color: col.spike, r: sp * .22 };
  const tail = { path: P.tail, r1: P.tr[0], r2: P.tr[1], sway: P.sway, speed: .4, crest, end };

  // ---- flames at the elbows (the lung's): a lock on each upper leg, streaming back -- it swings with it
  if (o.elbows) for (const [tag, leg] of [["FL", P.legs.front], ["FR", P.legs.front], ["HL", P.legs.hind], ["HR", P.legs.hind]]) {
    const u = leg[3], l = hr * 1.5;
    extras.push({ raw: pill(`elbow${tag}`, `leg${tag}u`, [0, -u * .55, 0], [-l, -u * .45 + l * .25, (tag[1] === "L" ? 1 : -1) * l * .15], hr * .12, hr * .02, col.mane) });
  }

  // ---- the claws
  const legs = { ...P.legs, ...(o.claws ? { toes: { n: o.claws, len: P.legs.foot[0] * (o.claws > 3 ? 1.0 : 1.2), r: [P.legs.foot[2] * .28, P.legs.foot[2] * .1], spread: o.claws > 3 ? .32 : .42, color: col.claw } } : {}) };

  const { dragon: _st, c: _c, ...flags } = d;
  const def = mammal({
    headForm: "dragon", ...flags, name: d.name, fur: false, pupil: d.pupil ?? "slit", headTurn: d.headTurn ?? (P.serpent ? 14 : 10), biped: !!P.biped,
    rear: P.rear, front: P.front, neck: P.neck, head: P.head, muzzle: P.muzzle, nose: P.nose, ears: o.ears === false ? null : P.ears, eyes: P.eyes,
    legs, tail, extras, c: { ...c, body, tail: c.tail ?? body }, ...(d.pat ? { pat: d.pat, patOn: d.patOn ?? ["body", "front", "neck", "head", "leg", "tail"] } : {}),
  });
  if (P.flight || d.flight) def.flight = { ...P.flight, ...d.flight };   // (skeleton.js FLIGHT: this plan's own numbers)
  if (P.serpent) spineChain(def, P);   // (the trunk in links, for the flight's wave)
  if (d.sculpt !== false) def.sculpt = bodySculpt(bodyKind, P, o, { ...c, body }, col, wing, def.parts);
  if (P.seat) def.saddle = { x: P.seat[0], y: P.seat[1] };   // (scaleDef scales it with the rest)
  return o.s && o.s !== 1 ? scaleDef(def, o.s) : def;
}

KINDS.dragon = dragonDef;
