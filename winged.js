// WINGED PEOPLE (2026-10-04): an angel, a demon -- the mixed monsters that are a whole person with wings. A definition
// (assets/creatures/monsters/angel.json) is of kind "winged": { person: makePerson's options (seed, kind, height, skin,
// outfit), wing: { kind: "bird" | "bat", k, ...the wing's own numbers }, horns, hair }; creatures.js builds it with
// what this registers (KINDS), so the game and the asset viewer build it the same way.
import { makePerson } from "./people.js";
import { batWing, birdWing } from "./mammals.js";   // (the beasts' plain wings: kept for whoever asks for "bird" / "bat" by name)
import { KINDS } from "./creatures.js";

const num = (c) => typeof c === "string" && /^#[0-9a-fA-F]{6}$/.test(c) ? parseInt(c.slice(1), 16) : c;   // ("#rrggbb" as the rig takes a colour)
const hex = (c) => typeof c === "number" ? "#" + c.toString(16).padStart(6, "0") : c;                   // (...and as the mesh head does)

// ---- winged people (an angel's kind, a demon's): the whole person (people.js makePerson) and a pair of wings grown
// from the back of the chest, just inside the shoulder blades -- a bird's, feathered (mammals.js birdWing), or a bat's,
// fingers and skin (batWing). The wings hang on the chest, so they turn and bend with the torso; their root is found
// from the rig itself (the arms' shoulder joint and the chest's girth), so it fits any height and build.
//   wing: { kind: "bird" | "bat", k (span, x the rig's 1 m wing), ...the wing's own numbers }; horns: { r, len (x the head's
//   radius), color }; hair: its colour ("#rrggbb", the mesh head's)
// THE WINGS ALONE, for a person built already (a carved angel's, a Victory's: statues.js): the parts to add after its own
export function wingsFor(man, { kind: wk = "bird", k = 1, ...wo } = {}, height = 1.78, live = false) {
  const byId = (id) => man.parts.find((p) => p.id === id);
  const arm = byId("armL"), chest = byId("chest"), S = height / 1.78;
  const back = -(chest.size.r * (chest.flat || 1)) * .85;   // (just inside the back: the root sinks into the shoulder blade)
  const at = [back, arm.pos[1] - .06 * S, Math.abs(arm.pos[2]) * .45];
  // (2026-11-07: a LIVING winged person's own wings -- featherWing and leatherWing below; a statue's, carved, stay the
  //  plain ones -- a carving is the stone's few planes, and a dressed figure's parts with a whole wing's feathers would
  //  pass composite.js's 160 -- as does a living one's whose kind says "bird-plain" / "bat-plain")
  const plain = !live || /-plain$/.test(wk), mk = /^bat/.test(wk) ? (plain ? batWing : leatherWing) : (plain ? birdWing : featherWing);
  // (a wing is drawn for a beast's back: x its body's forward, y up off the back. An upright figure's body runs UP, and
  //  its back faces -x: a root bone turned a quarter about z maps the one onto the other -- the wings spread behind the
  //  back, their chord hanging down, and flap forward and back about the spine)
  const root = { id: "wingRoot", parent: "chest", shape: "capsule", size: { r: .01, len: .01 }, bone: true, pos: [at[0], at[1], 0], rot: [0, 0, 90] };
  return [root, ...[1, -1].flatMap((s) => mk(s, { k: k * S, parent: "wingRoot", x: 0, y: 0, z: at[2], lift: 35, ...wo }))];
}

// ---- A WINGED PERSON'S WINGS (2026-11-07). The beasts' plain wings (mammals.js) are a few big plates: on a figure the
// eye is held by, an angel's read as two boards with a sawtooth edge and a demon's as two maroon panels. These are
// built the way the real ones are, in the same frame (the arm along +y to the wrist, the trailing edge toward -x, a
// part's own z the wing's thickness) and with the same bones, flap and fold, so they drop in for them. Every piece is
// a part of the figure (composite.js draws at most 160 of a figure's: a person is about 22, each wing here under 65).
const shadeC = (c, f) => { const v = typeof c === "number" ? c : parseInt(String(c).slice(1), 16);
  const ch = (k) => Math.max(0, Math.min(255, Math.round(((v >> k) & 255) * f)));
  return (ch(16) << 16) | (ch(8) << 8) | ch(0); };
const D2R = Math.PI / 180;
// A FEATHERED WING, laid as a bird's is. Over the leading edge the MARGINAL coverts, a smooth rounded mass along the
// arm and the hand (the bones are inside it, never seen); behind it the coverts in two rows of SCALES, each feather's
// broad base along the arm overlapping its neighbours' and the row before covering the bases of the row behind, so the
// fore wing is one closed shingled surface; then the flight feathers -- ten PRIMARIES fanned from the hand, narrow and
// tapered, the outer ones parted at their tips like fingers and darker there; ten SECONDARIES (with the tertials at the
// body) along the forearm, broad with rounded ends. A flight feather is a blade -- two plates on its shaft, the leading
// vane narrow, the trailing one broad and dipped under the next feather -- widest past its middle and closing to a soft
// point; the white warmer toward the body. Every feather is a part (composite.js draws 160 of a figure's: a person is
// about 22, each wing here 65).
const mixC = (a, b, t) => { const ch = (v, k) => (v >> k) & 255, f = (k) => Math.round(ch(a, k) + (ch(b, k) - ch(a, k)) * t);
  return (f(16) << 16) | (f(8) << 8) | f(0); };
export function featherWing(s, { k = 1, x = -.2, y = .5, z = .4, color = 0xf2efe6, tip = null, bone = null, warm = 0xf6e2bf, deg = 14, speed = .45, parent = "body", lift = 0, spread = 62, bend = 0 } = {}) {
  const S = s > 0 ? "L" : "R", E = 1.08 * k, HL = .55 * k, R = .012 * k, zl = .012 * k, col = typeof color === "number" ? color : parseInt(String(color).slice(1), 16);
  const tipC = tip ?? shadeC(col, .8), SPAN = E + HL;
  // (t: how far out along the wing, 0 at the body .. 1 at the tip -- the white is warmer toward the body)
  const tint = (t, f = 1) => shadeC(mixC(col, warm, .4 * (1 - Math.min(1, Math.max(0, t)))), f);
  let nV = 0;
  const jit = () => { const h = Math.sin(++nV * 12.9898 + s * 78.233) * 43758.5453; return h - Math.floor(h) - .5; };
  const tri = (id, par, a, b, c, color) => ({ id, parent: par, shape: "tri", size: { a, b, c, r: R }, pos: [0, 0, 0], color, edge: 0 });
  // a FLIGHT FEATHER: from its root at y0 along the bone, pointing `a` degrees back from the bone (0 on along it, 90 straight
  // back), L long, w wide at its widest (`at` of the way out), `lead` of that before the shaft
  const feather = (id, par, y0, a0, L0, w, z0, c, { at = .6, lead = .25, round = .15, dip = .3 } = {}) => {
    const j = jit(), a = a0 + j * 3, L = L0 * (1 + j * .08);
    const d = [-Math.sin(a * D2R), Math.cos(a * D2R)], tr = [-d[1], d[0]];   // along it; across, toward the trailing edge
    const p = (u, v, dz) => [d[0] * L * u + tr[0] * v, y0 + d[1] * L * u + tr[1] * v, z0 + dz];
    const A = p(.02, 0, 0), T = p(1, w * round, -w * dip * .4), Pl = p(at + .1, -w * lead, w * .05), Pt = p(at, w * (1 - lead), -w * dip);
    return [tri(`${id}a${S}`, par, A, Pl, T, shadeC(c, 1.03)), tri(`${id}b${S}`, par, A, T, Pt, c)];
  };
  // a COVERT, a scale: its base along the bone, y0 +- h (overlapping its neighbours'), xb before (+) or behind (-) the
  // bone, its rounded point Lc back at `a` degrees -- a little in toward the body, as they lie
  const covert = (id, par, y0, h, xb, a, Lc, z0, c) => {
    const j = jit(), d = [-Math.sin((a + j * 4) * D2R), Math.cos((a + j * 4) * D2R)];
    return tri(`${id}${S}`, par, [xb, y0 + h, z0 + zl * .4], [xb, y0 - h, z0 + zl * .4], [xb + d[0] * Lc, y0 + d[1] * Lc - h * .35, z0 - Lc * .06], c);
  };
  const arm = `wArm${S}`, hand = `wHand${S}`, out = [
    // the arm and the hand ARE the marginal coverts: the leading edge's rounded mass, feather-white
    { id: arm, parent, shape: "capsule", size: { r: .05 * k, r2: .034 * k, len: 1.1 * k },
      pos: [x, y, s * z], rot: [s * spread, 0, -lift], pivot: [0, .55 * k, 0], color: bone ?? tint(.25, 1.02), edge: 0,
      anim: { axis: "x", deg: s * deg, speed, phase: 0, wing: true }, fold: [s * 118, 0, 70] },
    { id: hand, parent: arm, shape: "capsule", size: { r: .034 * k, r2: .014 * k, len: HL }, pos: [0, E, 0], rot: [s * 25, 0, bend], pivot: [0, HL / 2, 0],
      color: bone ?? tint(.75, 1.02), edge: 0, anim: { axis: "x", deg: s * deg * 1.4, speed, phase: .5, wing: true }, fold: [-s * 25, 0, 0] },
  ];
  const lay = (n, f) => { for (let i = 0; i < n; i++) f(i, n > 1 ? i / (n - 1) : 0); };
  // PRIMARIES, outermost first: fanned from the hand's tip back to the wrist, the outer ones spread wider apart (the
  // fingers at the wing's tip), narrow and long; the outer four dark-tipped
  const PA = [0, 8, 16, 24, 31, 38, 46, 54, 62, 70];
  lay(10, (i, f) => out.push(...feather(`wPrim${i}`, hand, HL * (1 - f) * .96, PA[i], (.9 - .3 * f) * k, (.08 + .06 * f) * k, -zl * .3 * (i % 2),
                                         i < 4 ? tipC : tint(.7 + .3 * (1 - f), .97), { at: .55, lead: .22, round: .1 })));
  // SECONDARIES and the tertials: along the forearm back to the body, broad, their ends rounded
  lay(10, (i, f) => out.push(...feather(`wSec${i}`, arm, E * (1 - .86 * f), 76 + 18 * f, (.6 - .12 * f) * k, .19 * k, -zl * .3 * (i % 2),
                                        tint((E * (1 - .86 * f)) / SPAN, .97), { at: .7, lead: .3, round: .45 })));
  // the GREATER coverts over the secondaries' roots, the MEDIAN over theirs, the marginal mass over those
  lay(9, (i, f) => { const yc = E * (1 - .86 * f), sp = E * .86 / 8; out.push(covert(`wCovG${i}`, arm, yc, sp * .8, -.04 * k, 84 + 8 * f, .3 * k, zl, tint(yc / SPAN, 1.01))); });
  lay(7, (i, f) => { const yc = E * (1 - .9 * f), sp = E * .9 / 6; out.push(covert(`wCovM${i}`, arm, yc, sp * .78, .01 * k, 86 + 6 * f, .2 * k, zl * 2, tint(yc / SPAN, 1.03))); });
  // the primary coverts on the hand, pointing as the primaries under them do; the alula at the wrist, on along the edge
  lay(5, (i, f) => { const yc = HL * (1 - f) * .82, sp = HL * .82 / 4; out.push(covert(`wCovP${i}`, hand, yc, sp * .8, -.01 * k, 18 + 52 * f, .3 * k, zl, tint((E + yc) / SPAN, 1.01))); });
  lay(2, (i, f) => out.push(covert(`wAlula${i}`, hand, .05 * k, .025 * k, .02 * k, -10 + 14 * f, (.16 - .03 * f) * k, zl * 1.6, tint(E / SPAN, 1.03))));
  return out;
}
// A LEATHER WING (a demon's): a bat's, or a dragon's -- the arm in two bones bent at the elbow, the hand at the wrist
// with a hooked thumb claw, four long fingers each jointed at its knuckle, and the skin stretched between them, its
// free edge scalloped in toward the wrist between every two tips and from the last finger back to the flank; the skin
// in panels a shade apart (a fan of wedges from the wrist), so it reads as membrane on bone, not one sheet.
export function leatherWing(s, { k = 1, x = -.2, y = .5, z = .4, bone = 0x2a1418, mem = 0x5a1e22, deg = 12, speed = .5, parent = "body", lift = 0, scallop = .2, claw = null } = {}) {
  const S = s > 0 ? "L" : "R", E = 1.08 * k, LD = .95 * k, th = .004 * k, clawC = claw ?? shadeC(bone, .7);
  const ang = (p) => Math.atan2(-p[0], p[1]) / D2R;
  const FING = [[6, 1.16], [26, 1.08], [48, .98], [72, .84]].map(([a, L]) => ({ a, L: L * k, t: [-Math.sin(a * D2R) * L * k, Math.cos(a * D2R) * L * k, 0] }));
  const lerp = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
  // (a free edge from P to Q: bowed in toward the joint the skin hangs from, `scallop` of the way at its middle)
  const edge = (P, Q, n = 4, bow = scallop) => Array.from({ length: n + 1 }, (_, j) => { const t = j / n, m = lerp(P, Q, t), b = 1 - bow * Math.sin(Math.PI * t); return [m[0] * b, m[1] * b, 0]; });
  let nP = 0;
  const tri = (id, par, a, b, c) => ({ id, parent: par, shape: "tri", size: { a, b, c, r: th }, pos: [0, 0, 0], color: shadeC(mem, nP++ % 2 ? .9 : 1), edge: 0 });
  const arm = `wArm${S}`, hand = `wHand${S}`;
  const Elb = [-.16 * k, .42 * E, 0], W = [0, E, 0], Root = [-1.0 * k, -.15 * k, 0], Dh = [-LD, 0, 0];   // (D: on the hand's hinge axis, behind the wrist)
  const bseg = (id, par, A, B, r1, r2, c = bone) => { const d = B.map((v, i) => v - A[i]), L = Math.hypot(...d);
    return { id, parent: par, shape: "capsule", size: { r: r1, r2, len: L }, pos: A, rot: [0, 0, ang(d)], pivot: [0, L / 2, 0], color: c, edge: 0 }; };
  const out = [
    // (the shoulder joint is the arm's: an undrawn bone that flaps and folds -- the upper arm drawn from it to the elbow,
    //  which lies behind the line to the wrist, so the bone bends there instead of running square-ended past it)
    { id: arm, parent, shape: "capsule", size: { r: .01 * k, len: .01 * k }, bone: true, pos: [x, y, s * z], rot: [s * 62, 0, -lift], pivot: [0, 0, 0], color: bone, edge: 0,
      anim: { axis: "x", deg: s * deg, speed, phase: 0, wing: true }, fold: [s * 118, 0, 70] },
    bseg(`wHum${S}`, arm, [0, 0, 0], Elb, .032 * k, .022 * k),
    bseg(`wFore${S}`, arm, Elb, W, .022 * k, .016 * k),
    // the arm's skin: from the shoulder and the elbow back to the flank, its edge from D (on the hinge) to the root bowed in
    tri(`wMemA${S}`, arm, [0, 0, 0], Elb, Root),
    ...(() => { const ac = edge([-LD, E, 0], Root, 4, scallop * .6), o = [tri(`wMemA1${S}`, arm, Elb, W, ac[0])];
      for (let j = 0; j < 4; j++) o.push(tri(`wMemA${j + 2}${S}`, arm, Elb, ac[j], ac[j + 1]));
      // (and the skin's own ribs, the tendons that hold it taut, fanned from the elbow to the scallops' points -- on both
      //  faces, a shade darker -- so the broad sheet between the last finger and the flank is not one bare plane)
      for (let j = 1; j < 4; j++) { const P = ac[j], dl = Math.hypot(P[0] - Elb[0], P[1] - Elb[1]), w = .01 * k;
        const pd = [-(P[1] - Elb[1]) / dl * w, (P[0] - Elb[0]) / dl * w];
        for (const [fz, F] of [[1, "f"], [-1, "k"]]) { const z = fz * (th + .006 * k), q = (v) => [v[0], v[1], z];
          o.push({ id: `wTen${j}${F}${S}`, parent: arm, shape: "tri", size: { a: q([Elb[0] + pd[0], Elb[1] + pd[1]]), b: q([Elb[0] - pd[0], Elb[1] - pd[1]]),
                   c: q([Elb[0] + (P[0] - Elb[0]) * .92, Elb[1] + (P[1] - Elb[1]) * .92]), r: th }, pos: [0, 0, 0], color: shadeC(mem, .62), edge: 0 }); } }
      return o; })(),
    { id: hand, parent: arm, shape: "sphere", size: { r: .026 * k }, pos: W, rot: [s * 42, 0, 0], color: bone, edge: 0,
      anim: { axis: "x", deg: s * deg * 1.6, speed, phase: .6, wing: true }, fold: [-s * 42, 0, 0] },
    // the thumb, short and hooked forward off the leading edge
    bseg(`wThumb${S}`, hand, [0, 0, 0], [.04 * k, .12 * k, 0], .022 * k, .014 * k),
    { id: `wClaw${S}`, parent: hand, shape: "cone", size: { r: .022 * k, h: .12 * k }, pos: [.09 * k, .17 * k, 0], rot: [0, 0, -55], color: clawC, edge: 0 },
  ];
  // the fingers, jointed at the knuckle (a little bent back), each tipped dark
  FING.forEach((f, i) => {
    const kn = lerp([0, 0, 0], f.t, .45), bendT = [f.t[0] - .03 * k * Math.cos(f.a * D2R), f.t[1] - .03 * k * Math.sin(f.a * D2R), 0];
    out.push(bseg(`wFinger${i}${S}`, hand, [0, 0, 0], kn, .018 * k, .013 * k), bseg(`wFinger${i}b${S}`, hand, kn, bendT, .013 * k, .006 * k));
    // (and the bone's ridge on either face of the skin: a slim plate laid on each, so the finger reads through the membrane
    //  from before and behind -- the skin is drawn over a round bone lying in its own plane)
    const w = .016 * k, pd = [Math.cos(f.a * D2R) * w, Math.sin(f.a * D2R) * w];
    for (const [fz, F] of [[1, "f"], [-1, "k"]]) { const z = fz * (th + .007 * k);
      out.push({ id: `wRib${i}${F}${S}`, parent: hand, shape: "tri", size: { a: [pd[0], pd[1], z], b: [-pd[0], -pd[1], z], c: [bendT[0], bendT[1], z], r: th }, pos: [0, 0, 0], color: bone, edge: 0 }); }
    f.t = bendT;
  });
  // the skin between the fingers, a fan of wedges from the wrist to the scalloped edge; the last gap back to D
  [...FING.slice(0, -1).map((f, i) => [f.t, FING[i + 1].t]), [FING[FING.length - 1].t, Dh]].forEach(([P, Q], g) => {
    const e = edge(P, Q, g === FING.length - 1 ? 3 : 4, g === FING.length - 1 ? scallop * .7 : scallop);
    for (let j = 0; j + 1 < e.length; j++) out.push(tri(`wMemB${g}${j}${S}`, hand, [0, 0, 0], e[j], e[j + 1]));
  });
  return out;
}

// the SKIN's own look (`skinLook` in the definition beside the person: a demon's): `pat` a pattern laid over every bare
// piece (skeleton.js PAT: "scales"), `tone` the bare pieces shaded from the chest out -- the shoulders and chest
// brightest, forearms, shins and then hands and feet darker -- so the body reads in planes, not one flat colour
const TONE = { chest: 1.12, neck: .96, belly: 1.0, hips: .9, pelvis: .9, arm: 1.04, fore: .84, hand: .66, leg: .94, shin: .8, foot: .62 };
export function winged(name, { wing = {}, horns = null, hair = null, call, skinLook = null, ...person }) {
  const man = makePerson(person), byId = (id) => man.parts.find((p) => p.id === id);
  if (skinLook && person.skin != null) for (const p of man.parts) {
    if (p.color !== person.skin) continue;
    const t = TONE[p.id.replace(/[LR]$/, "")];
    if (skinLook.tone && t) p.color = shadeC(p.color, t);
    if (skinLook.pat) p.pat = skinLook.pat;
  }
  const wings = wingsFor(man, wing, person.height ?? 1.78, true);
  const head = byId("head"), extra = [];
  if (horns) for (const s of [1, -1]) {   // (a demon's: two short cones from the brow, curving back)
    // (a cone is centred on its pos: its base on the skull -- a little out, the mesh head is the fuller -- and its
    //  middle half its length on along where it points, out and back)
    // (a mesh head's part is a pin: the face knows its radius)
    const r = man.face?.hr ?? head.size.r, h = (horns.len ?? 1.4) * r, rx = 18, rz = 25, D = Math.PI / 180;
    const d = [-Math.sin(rz * D), Math.cos(rz * D) * Math.cos(rx * D), s * Math.cos(rz * D) * Math.sin(rx * D)];
    const n = [.3, .82, s * .48], nl = Math.hypot(...n), base = n.map((v) => v / nl * r * 1.12);
    extra.push({ id: `horn${s > 0 ? "L" : "R"}`, parent: "head", shape: "cone", size: { r: (horns.r ?? .2) * r, h },
                 pos: base.map((v, i) => v + d[i] * h / 2), rot: [s * rx, 0, rz], color: horns.color ?? 0x2a1a14, edge: 0 });
  }
  if (hair && man.face) man.face = { ...man.face, hair };   // (an angel's gold)
  // (the wings and horns go AFTER the person's parts: its face's part indices stay as they are)
  return { ...man, name, monster: true, call, parts: [...man.parts, ...wings, ...extra] };
}

// the definition's kind: its person and its wing are its own words (creatures.js keeps them as written)
KINDS.winged = (d) => {
  const { person = {}, wing = {}, horns = null, hair = null, skinLook = null, call } = d;
  const w = Object.fromEntries(Object.entries(wing).map(([k, v]) => [k, num(v)]));
  return winged(d.name, { ...person, ...(person.skin ? { skin: num(person.skin) } : {}), wing: w,
                          horns: horns && { ...horns, color: num(horns.color) }, hair: hex(hair), skinLook, call });
};
