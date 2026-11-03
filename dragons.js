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
    rear: [-.9, 1.9, 0, 1.3, .9, .8], front: [.7, 2, 0, 1.2, .92, .85],
    neck: [1.6, 2.4, 0, 2.75, 3.75, 0, .5, .3], head: [2.95, 3.85, 0, .42],
    muzzle: [3.45, 3.72, 0, .5, .22, .26], nose: [3.93, 3.78, 0, .06],
    ears: [2.72, 4.02, .26, 2.42, 4.08, .46, .1, .02], eyes: [3.2, 4.02, .24, .065],
    legs: { front: [1, 1.6, .6, .8], hind: [-1.3, 1.65, .65, .9], radii: [.3, .22, .16], foot: [.3, .12, .24] },
    tail: [[-2.15, 1.95], [-3.4, 1.85], [-4.6, 1.2], [-5.5, .55], [-6.2, .4]], tr: [.42, .07], sway: 8,
    wings: "bat", wingAt: [.3, 2.55, .55], wingK: 1.6, spike: .38,
  },
  drake: {
    rear: [-1, 1.35, 0, 1.45, .8, .85], front: [.8, 1.4, 0, 1.3, .85, .9],
    neck: [1.8, 1.7, 0, 2.6, 2.35, 0, .52, .36], head: [2.8, 2.45, 0, .44],
    muzzle: [3.3, 2.32, 0, .52, .24, .28], nose: [3.8, 2.38, 0, .065],
    ears: [2.58, 2.62, .27, 2.28, 2.66, .45, .1, .02], eyes: [3.05, 2.6, .25, .065],
    legs: { front: [1.1, 1.1, .75, .55], hind: [-1.4, 1.1, .8, .6], radii: [.32, .23, .17], foot: [.32, .12, .26] },
    tail: [[-2.4, 1.4], [-3.6, 1.25], [-4.8, .75], [-5.9, .35], [-6.7, .3]], tr: [.46, .07], sway: 7,
    wings: "none", wingAt: [.4, 2.05, .6], wingK: 1.5, spike: .34,
  },
  wyvern: {
    rear: [-.5, 2.1, 0, 1.1, .85, .75], front: [.9, 2.35, 0, .95, .8, .72],
    neck: [1.6, 2.7, 0, 2.4, 3.6, 0, .42, .27], head: [2.6, 3.7, 0, .38],
    muzzle: [3.05, 3.58, 0, .45, .2, .23], nose: [3.48, 3.63, 0, .055],
    ears: [2.4, 3.86, .23, 2.12, 3.92, .4, .09, .02], eyes: [2.83, 3.86, .21, .06],
    legs: { front: [.9, 2.1, .5, .8], hind: [-.25, 1.95, .6, .95], radii: [.3, .2, .14], foot: [.32, .12, .22], kneeH: 1, toe: .15, bend: [1, 1.03] },
    biped: true,
    tail: [[-1.55, 2.25], [-2.8, 2.15], [-3.9, 1.7], [-4.9, 1.3], [-5.6, 1.2]], tr: [.36, .06], sway: 9,
    wings: "bat", wingAt: [.6, 2.85, .5], wingK: 2.0, spike: .3,
  },
  lung: {
    rear: [-1.2, 1.15, 0, 1.35, .34, .36], front: [1.0, 1.22, 0, 1.25, .36, .38],
    neck: [2.0, 1.35, 0, 2.75, 2.0, 0, .32, .24], head: [2.9, 2.1, 0, .3],
    muzzle: [2.95, 2.06, 0, 3.5, 1.98, 0, .22, .12], nose: [3.56, 2.03, 0, .065],
    ears: [2.72, 2.32, .17, 2.5, 2.42, .27, .06, .015], eyes: [3.04, 2.22, .19, .07],
    legs: { front: [1.35, 1.0, .4, .45], hind: [-1.6, .95, .4, .45], radii: [.14, .1, .08], foot: [.16, .06, .12] },
    tail: [[-2.5, 1.15], [-3.4, 1.8], [-4.4, .75], [-5.4, 1.6], [-6.3, .85], [-7.0, 1.1]], tr: [.34, .05], sway: 6,
    wings: "none", wingAt: [1.1, 1.5, .35], wingK: 1.3, spike: .2, serpent: true,
  },
};
PLANS.serpent = { ...PLANS.lung, wings: "feather", wingK: 2.6 };

// ---- what grows on it ------------------------------------------------------------------------------------------------
const DEFAULTS = {
  western: { horns: "swept", spikes: "spike", tailEnd: "spade", claws: 3 },
  drake:   { horns: "straight", spikes: "plate", tailEnd: "club", claws: 3 },
  wyvern:  { horns: "swept", spikes: "spike", tailEnd: "blade", claws: 3 },
  lung:    { horns: "antlers", spikes: "tuft", tailEnd: "flame", claws: 5, whiskers: true, brows: true, beard: true, mane: true, elbows: true },
  serpent: { horns: "plume", spikes: "tuft", tailEnd: "plume", claws: 3, mane: true },
};

export function dragonDef(d) {
  const st = d.dragon ?? {}, bodyKind = PLANS[st.body] ? st.body : "western", P = PLANS[bodyKind];
  const o = { ...DEFAULTS[bodyKind], ...st }, c = { ...(d.c ?? {}) };
  const body = c.body ?? 0x4a7040;
  const col = {
    spike: c.spike ?? shade(body, .7), horn: c.horn ?? 0xd8cbb0, bone: c.bone ?? shade(body, .75), mem: c.mem ?? shade(body, .68),
    mane: c.mane ?? shade(body, .6), whisker: c.whisker ?? c.mane ?? shade(body, .6), claw: c.claw ?? 0x2a2620,
    feather: c.feather ?? body, tip: c.tip ?? shade(body, .6),
  };
  const extras = [], hl = o.hornLen ?? 1, sp = (o.spikeSize ?? 1) * P.spike;
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
    for (let x = x0; x <= x1; x += step) stations.push([[x, top(x) - .04, 0], unit([step, top(x + .05) - top(x - .05), 0]), [0, 1, 0], 1]);
    const A = P.neck.slice(0, 3), B = P.neck.slice(3, 6), al = unit(sub(B, A)), up = unit([-al[1], al[0], 0]), nl = Math.hypot(...sub(B, A));
    for (let t = .25; t < .95; t += step * .85 / nl) {
      const r = P.neck[6] + (P.neck[7] - P.neck[6]) * t;
      stations.push([add(lerp(A, B, t), mul(up, r * .8)), al, up, .75 + .25 * (1 - t)]);
    }
  }
  // ...and a spike, plate, fin or tuft at each (back: the -along way, the tail's)
  stations.forEach(([p, al, up, g], i) => {
    const h = sp * g * (o.spikes === "plate" ? 1.3 : 1), back = mul(al, -1), id = `spine${i}`;
    if (o.spikes === "spike") extras.push({ id, parent: "body", from: p, to: add(p, add(mul(up, h), mul(back, h * .55))), r1: h * .3, r2: h * .04, color: col.spike, k: .03 });
    else if (o.spikes === "plate" || o.spikes === "fin") {
      const w = o.spikes === "fin" ? h * .75 : h * .45, tip = add(mul(up, h), mul(back, h * (o.spikes === "fin" ? .6 : .25)));
      extras.push({ raw: { id, parent: "body", shape: "tri", size: { a: mul(al, w), b: mul(back, w), c: tip, r: .025 + h * .02 },
                           color: o.spikes === "fin" ? col.mem : col.spike, k: 0 }, at: [p[0], p[1], i % 2 && o.spikes === "plate" ? .04 : 0] });
    } else if (o.spikes === "tuft") {   // (a flame of hair: two locks, the lean of a fire in the wind)
      extras.push({ id, parent: "body", from: p, to: add(p, add(mul(up, h * .9), mul(back, h))), r1: h * .28, r2: h * .03, color: col.spike, k: .02 });
      if (i % 2 === 0) extras.push({ id: id + "b", parent: "body", from: add(p, mul(back, h * .25)), to: add(p, add(mul(up, h * .5), mul(back, h * 1.15))), r1: h * .2, r2: h * .02, color: col.mane, k: .02 });
    }
  });

  // ---- horns (on the head: they turn with it)
  const Hb = [hx - hr * .35, hy + hr * .78, hr * .42];   // where they grow: the back of the skull, its left
  const pathX = (id, pts, r1, r2, color) => extras.push({ id, parent: "head", mirror: true, color, k: 0, pat: null, path: { path: pts, r1, r2, sway: 0, speed: 0 } });
  const pills = (id, list, color) => list.forEach(([a, b, r1, r2], i) => extras.push({ id: `${id}${i}`, parent: "head", mirror: true, from: a, to: b, r1, r2, color, k: 0 }));
  const L = hr * 2.2 * hl;
  if (o.horns === "swept") pathX("horn", [Hb, add(Hb, [-.45 * L, .35 * L, .08 * L]), add(Hb, [-1.0 * L, .42 * L, .14 * L]), add(Hb, [-1.35 * L, .3 * L, .17 * L])], hr * .24, hr * .03, col.horn);
  else if (o.horns === "straight") pills("horn", [[Hb, add(Hb, [-.9 * L, .75 * L, .2 * L]), hr * .22, hr * .03]], col.horn);
  else if (o.horns === "curl") {   // a ram's: back, down and forward again beside the jaw, drifting out
    const C = add(Hb, [-.32 * L, -.12 * L, 0]), R = .34 * L, a0 = Math.atan2(Hb[1] - C[1], Hb[0] - C[0]);
    const pts = Array.from({ length: 8 }, (_, i) => { const a = a0 + i * .62, rr = R * (1 - i * .045); return [C[0] + rr * Math.cos(a), C[1] + rr * Math.sin(a), Hb[2] + i * .045 * L]; });
    pathX("horn", [Hb, ...pts.slice(1)], hr * .3, hr * .07, col.horn);
  } else if (o.horns === "crown") {   // a crown of them round the back of the skull, the middle pair the longest
    const list = [];
    for (let i = 0; i < 4; i++) {
      const a = .4 + i * .42, root = [hx - hr * (.15 + .25 * Math.sin(a)), hy + hr * .85 * Math.cos(a), hr * (.25 + .5 * Math.sin(a))];
      const l = L * (i === 1 ? 1 : i === 0 ? .8 : .6);
      list.push([root, add(root, [-.8 * l, .45 * l * Math.cos(a), .25 * l * Math.sin(a)]), hr * .16, hr * .025]);
    }
    pills("horn", list, col.horn);
  } else if (o.horns === "antlers") {   // a deer's, as the Chinese draw them: a beam back and up, two tines forward
    const a = [hx - hr * .25, hy + hr * .85, hr * .3], b = add(a, [-.25 * L, .45 * L, .1 * L]), m = add(a, [-.42 * L, .85 * L, .2 * L]), e = add(a, [-.8 * L, 1.05 * L, .3 * L]);
    pathX("antler", [a, b, m, e], hr * .14, hr * .045, col.horn);
    pills("tine", [[lerp(a, b, .7), add(lerp(a, b, .7), [.28 * L, .32 * L, .04 * L]), hr * .08, hr * .025],
                   [lerp(m, e, .2), add(lerp(m, e, .2), [.12 * L, .42 * L, .03 * L]), hr * .07, hr * .02],
                   [lerp(m, e, .75), add(lerp(m, e, .75), [-.05 * L, .3 * L, .06 * L]), hr * .06, hr * .018]], col.horn);
  } else if (o.horns === "plume") {   // a crest of feathers fanned back from the crown
    const list = [];
    for (let i = 0; i < 5; i++) { const root = [hx - hr * .2, hy + hr * .8, hr * (.1 + i * .09)], l = L * (1.3 - i * .15), a = .25 + i * .2;
      list.push([root, add(root, [-l * Math.cos(a), l * Math.sin(a) * .9 + l * .3, i * .06 * L]), hr * .1, hr * .04]); }
    pills("plume", list, col.feather);
    pills("plumeTip", list.map(([r, t]) => [lerp(r, t, .7), add(t, mul(sub(t, r), .12)), hr * .07, hr * .03]), col.tip);
  }
  if (o.nose) extras.push({ id: "noseHorn", parent: "head", from: add(snout, [-hr * .55, hr * .35, 0]), to: add(snout, [-hr * .75, hr * 1.2 * hl, 0]), r1: hr * .17, r2: hr * .02, color: col.horn, k: 0 });

  // ---- the lung's hair: whiskers from the lip, brows streaming back, a beard, a mane down the neck
  if (o.whiskers) {
    const w0 = add(snout, [-hr * .25, -hr * .05, hr * .2]), l = hr * 3.2;
    extras.push({ id: "whisker", parent: "head", mirror: true, color: col.whisker, k: 0, pat: null,
                  path: { path: [w0, add(w0, [.3 * l, -.02 * l, .25 * l]), add(w0, [.35 * l, -.35 * l, .55 * l]), add(w0, [.1 * l, -.75 * l, .7 * l]), add(w0, [-.15 * l, -.95 * l, .75 * l])],
                          r1: hr * .07, r2: hr * .015, sway: 10, speed: .5 } });
  }
  if (o.brows) {
    const b0 = [P.eyes[0] - hr * .05, P.eyes[1] + hr * .25, hr * .3], l = hr * 3.4;
    extras.push({ id: "brow", parent: "head", mirror: true, color: col.whisker, k: 0, pat: null,
                  path: { path: [b0, add(b0, [-.25 * l, .2 * l, .1 * l]), add(b0, [-.6 * l, .15 * l, .25 * l]), add(b0, [-.95 * l, -.1 * l, .3 * l])], r1: hr * .07, r2: hr * .015, sway: 8, speed: .4 } });
  }
  if (o.beard) {
    const chin = [hx + hr * .55, hy - hr * .75, 0], list = [];
    for (let i = 0; i < 3; i++) list.push([add(chin, [-i * hr * .3, 0, hr * .12]), add(chin, [-i * hr * .3 - hr * .5, -hr * (1.1 - i * .2), hr * (.2 + i * .05)]), hr * .14, hr * .03]);
    pills("beard", list, col.mane);
  }
  if (o.mane) {   // locks down the back of the neck and on over the shoulders, streaming back
    const A = P.neck.slice(0, 3), B = P.neck.slice(3, 6), al = unit(sub(B, A)), up = unit([-al[1], al[0], 0]);
    for (let i = 0; i < 5; i++) {
      const t = 1 - i / 5, r = P.neck[6] + (P.neck[7] - P.neck[6]) * t, p = add(lerp(A, B, t), mul(up, r * .7)), l = hr * (1.6 - i * .1);
      for (const z of [1, -1]) extras.push({ id: `mane${i}${z > 0 ? "L" : "R"}`, parent: "body", from: add(p, [0, 0, z * r * .35]),
                                            to: add(p, [-l * .9, l * .25, z * (r * .35 + l * .35)]), r1: hr * .16, r2: hr * .03, color: col.mane, k: .02 });
    }
  }

  // ---- wings
  const wings = o.wings ?? P.wings, wk = P.wingK * (o.wingSpan ?? 1);
  // (as mammals.js COMPONENTS does it: the wing's root placed at the shoulder, each side's at its own z)
  const shoulder = (list, s) => list.map((p, i) => (i === 0 ? { raw: p, at: [P.wingAt[0], P.wingAt[1], s * P.wingAt[2]] } : { raw: p }));
  if (wings === "bat") for (const s of [1, -1]) extras.push(...shoulder(batWing(s, { k: wk, bone: col.bone, mem: col.mem, deg: 11, speed: .35 }), s));
  if (wings === "feather") for (const s of [1, -1]) extras.push(...shoulder(birdWing(s, { k: wk, color: col.feather, tip: col.tip, bone: col.feather, deg: 18, speed: .4, lift: 30, spread: 75 }), s));

  // ---- the tail: its crest (the back's own row, on down it) and what ends it
  const end = [], tr = P.tr[1], el = sp * 1.8;
  if (o.tailEnd === "spade") for (const s of [1, -1]) end.push({ id: `tailSpade${s > 0 ? "L" : "R"}`, shape: "tri", pos: [0, -el * .15, 0], color: col.spike, k: 0, edge: 0,
                                                                 size: { a: [0, 0, 0], b: [0, el * .5, s * el * .42], c: [0, el * 1.05, 0], r: .03 } });
  else if (o.tailEnd === "blade") for (const s of [1, -1]) end.push({ id: `tailBlade${s > 0 ? "L" : "R"}`, shape: "tri", pos: [0, -el * .2, 0], color: col.spike, k: 0, edge: 0,
                                                                      size: { a: [0, 0, 0], b: [s * el * .3, el * .35, 0], c: [0, el * 1.25, 0], r: .025 } });
  else if (o.tailEnd === "club") {
    end.push({ id: "tailClub", shape: "sphere", size: { r: tr * 3.4 }, pos: [0, tr * 2, 0], color: col.spike, k: .03, edge: 0 });
    for (const [x, z] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) end.push(pill(`tailClubSpike${x}${z}`, "", [x * tr * 2.6, tr * 2.4, z * tr * 2.6], [x * tr * 5.5, tr * 3.6, z * tr * 5.5], tr * .9, tr * .12, col.horn));
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
    ...flags, name: d.name, fur: false, pupil: d.pupil ?? "slit", headTurn: d.headTurn ?? (P.serpent ? 14 : 10), biped: !!P.biped,
    rear: P.rear, front: P.front, neck: P.neck, head: P.head, muzzle: P.muzzle, nose: P.nose, ears: o.ears === false ? null : P.ears, eyes: P.eyes,
    legs, tail, extras, c: { ...c, body, tail: c.tail ?? body }, ...(d.pat ? { pat: d.pat, patOn: d.patOn ?? ["body", "front", "neck", "head", "leg", "tail"] } : {}),
  });
  return o.s && o.s !== 1 ? scaleDef(def, o.s) : def;
}

KINDS.dragon = dragonDef;
