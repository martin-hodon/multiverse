// Generative people for the figure engine -- the mammal rig's ideas applied
// to humans, dressed from the medieval wardrobe (assets/clothes: shirts and
// chemises, tunics, kirtles, surcoats, houppelandes, hose, cloaks, hoods,
// hats, belts, boots, aprons).
//
// BODY (the unisex canon, assets/people/body.json): ONE torso -- three
// flattened cuts swept as a single lathe through the shoulders' rim, the
// chest, the waist and the hips, its top a low squared cap that is the
// shoulders -- a neck and an ovoid head with nose, mouth and eyes; arms of two
// bones and a hand, hung BESIDE the torso (never through it); legs of two
// bones with a foot. Knees come from the same two-bone IK
// as the mammals' (skeleton.js) on a biped walk and run; feet stay flat
// (`level`); arms, the shoulders' twist, skirts and plaits swing on the
// gait clock and settle when the person stands (`anim.amp`).
//
// CLOTHING is the tailor's (clothes.js, docs/clothes.md): garments cut from
// flat sheets of cloth, each laid on a HOST of the body between two landmarks
// -- worn ON the body's own parts as layers of fabric (a bodice, a sleeve,
// hose), or standing off it as shells of their own (a skirt, a cloak, a hood,
// a hat) -- in fabrics of the pattern language, dyed by the wardrobe. This
// file builds the body and hands the tailor a FORM of it: its hosts, their
// parts, landmarks and girths.
//
// Root space: metres, x forward, y up from the ground (feet on y = 0),
// z to the person's left. Heights run 1.02-1.92m by kind.
import { rng } from "./flora.js";
import { hangRot, vNorm, vSub, vDot, scalePart } from "./geom.js";
import { expression } from "./faces.js";
import { fetchAsset } from "./creatures.js";
import { tailor, drawOutfit, namedOutfit, garmentDef, WARDROBE, outerSurface } from "./clothes.js";
import { neckFit, setCanonNeck } from "./jewelry.js";

// THE CANON (assets/people/body.json): what a person's proportions ARE, as fractions of the stature. Loaded
// before this module is done, so every importer of makePerson sees it (a module with a top-level await is
// awaited by whoever imports it). The asset viewer edits this file and the people change with it.
export const BODY = await fetchAsset("people/body");
// THE JOINTS (assets/people/joints.json, joints.js): where and how far a person bends -- here, the elbow's rest
export const JOINTS = await fetchAsset("people/joints");
// WHAT IS WORN ON TOP (assets/items/jewelry/wear.json): by style of dress and kind of person, a few looks and how often
// -- a necklace (or none), something on the head, earrings -- each a pick of jewelry items
export const JEWEL_WEAR = await fetchAsset("items/jewelry/wear");

const SKIN = [0xf0c8a0, 0xdfb289, 0xc79668, 0xa9764d, 0x7c5236];
const HAIR = [0x241b14, 0x4a2f18, 0x7a4a22, 0xa87433, 0xd9b96a, 0x99928a, 0xb0502c];
const OLD_HAIR = [0x9c968f, 0xc4bfb8, 0xe2ded6, 0x7d7873];   // the old: grey to white
const GREY_HAIR = new Set([0x99928a]);   // (the greys in HAIR: going grey -- never on a child)
// the people's options (index.html fills them from config.json): nose -- a nose on human heads (one SDF part each;
// off by default: a face reads without it, and every person saves a part)
export const PEOPLE = { nose: true, face: true };   // face: the MESH head (face.js, heads.js) instead of the SDF marks and nose
const SCLERA = 0xece6da;
// iris colours, weighted roughly as in real life: mostly browns, then blue, hazel, amber, green, grey
const IRIS = [[0x3b2314, 35], [0x5a3a22, 30], [0x3f6f9a, 10], [0x7a6232, 10], [0x8a5a1a, 5], [0x4f6b3a, 5], [0x7a8590, 5]];
// Work gestures by trade (village-life.js picks one by name; skeleton.js swings it on the world clock
// with strength an.work, on top of the pose): per piece -- upper arm, forearm (s: +1 left, -1 right;
// null = that side holds still) and chest -- { axis, bias, deg, speed (cycles/s), phase } in degrees.
// A forearm's may also carry `twist`: the upper arm turned about its length (the elbow's plane with it; + inward on the
// left, the rig's "L") -- skeleton.js HINGE keeps every forearm to bends the elbow and shoulder can make.
// z swings an arm forward (+) and back and bends the chest forward, x takes an arm out to its side
// (outward = -s), y turns the chest.
const G = (axis, bias, deg, speed, phase = 0) => ({ axis, bias, deg, speed, phase });
const alt = (s) => (s > 0 ? 0 : Math.PI);
export const GESTURES = {
  dig:    { arm: () => G("z", 45, 30, .45), fore: () => G("z", 30, 25, .45, .8), chest: G("z", 15, 12, .45) },           // a spade: thrust, lift
  hoe:    { arm: () => G("z", 70, 35, .5), fore: () => G("z", 15, 30, .5, .5), chest: G("z", 10, 10, .5) },              // chop down, draw back
  mow:    { arm: () => G("z", 40, 8, .35, 1.6), fore: () => G("z", 25, 6, .35, 1.6), chest: G("y", 0, 28, .35) },       // the scythe's sweep: the body turns
  hammer: { arm: (s) => (s < 0 ? G("z", 60, 50, 1) : G("z", 40, 5, 1)), fore: (s) => (s < 0 ? G("z", 40, 40, 1, .6) : G("z", 50, 5, 1)) },
  knead:  { arm: (s) => G("z", 50, 12, .8, alt(s)), fore: (s) => G("z", 45, 20, .8, .5 + alt(s)), chest: G("z", 8, 5, 1.6) },
  sell:   { arm: (s) => (s < 0 ? G("z", 30, 25, .35) : G("x", -s * 15, 10, .25)), fore: (s) => (s < 0 ? G("z", 50, 25, .35, 1) : G("z", 30, 10, .25)) },
  fish:   { arm: (s) => (s < 0 ? G("z", 55, 6, .2) : G("z", 40, 4, .2)), fore: (s) => (s < 0 ? G("z", 30, 8, .2) : G("z", 40, 4, .2)) },
  strum:  { arm: (s) => (s < 0 ? G("z", 25, 4, .3) : G("z", 45, 3, .3)), fore: (s) => (s < 0 ? G("z", 60, 18, 2.2) : G("z", 70, 3, .3)) },
  bless:  { arm: (s) => G("x", -s * 25, 12, .15), fore: () => G("z", 40, 10, .15) },
  eat:    { arm: (s) => (s < 0 ? G("z", 30, 10, .25) : G("z", 20, 3, .25)), fore: (s) => (s < 0 ? G("z", 95, 35, .25) : G("z", 60, 5, .25)) },
  pick:   { arm: (s) => (s < 0 ? G("z", 120, 25, .4) : G("z", 60, 20, .4, Math.PI)), fore: (s) => G("z", 25, 20, .4, alt(s)), crouch: .12 },
  weave:  { arm: (s) => G("z", 45, 15, .7, alt(s)), fore: (s) => G("z", 40, 20, .7, alt(s)) },
  sew:    { arm: () => G("z", 35, 5, .5), fore: (s) => (s < 0 ? G("z", 60, 25, .9) : G("z", 60, 5, .5)) },
  lift:   { arm: () => G("z", 50, 25, .4), fore: () => G("z", 60, 20, .4, .4), chest: G("z", 10, 10, .4) },
  chop:   { arm: (s) => (s < 0 ? G("z", 70, 45, .8) : G("z", 30, 5, .8)), fore: (s) => (s < 0 ? G("z", 40, 35, .8, .5) : G("z", 50, 5, .8)) },   // the cleaver falls, the other hand holds the meat
  jig:    { arm: (s) => (s < 0 ? G("z", -15, 3, .5) : G("z", -10, 2, .3)), fore: (s) => (s < 0 ? G("z", 20, 8, .5) : G("z", 10, 3, .3)) },   // fishing through the ice, seated: the rod hand low before the knees, jigging the line
  split:  { arm: () => G("z", 95, 65, .55), fore: () => G("z", 25, 20, .55, .4), chest: G("z", 15, 15, .55, Math.PI) },   // splitting logs: the axe in both hands up over the head and down, bending into the blow
  pitch:  { arm: () => G("z", 75, 50, .45), fore: () => G("z", 30, 20, .45, .5), chest: G("z", 8, 12, .45, Math.PI) },   // pitching sheaves up onto a wagon: the fork down to the stook, then up high
  saw:    { arm: (s) => (s < 0 ? G("z", 35, 18, .9) : G("z", 40, 3, .9)), fore: (s) => (s < 0 ? G("z", 55, 28, .9, .4) : G("z", 60, 3, .9)), chest: G("z", 12, 6, .9) },
  pour:   { arm: () => G("z", 55, 8, .22), fore: () => G("z", 30, 8, .22, .3), chest: G("z", 22, 5, .22), crouch: .08 },   // tipping a bucket out: both arms forward and down, leaning over it
  scatter: { arm: (s) => (s < 0 ? G("z", 35, 35, .55) : G("z", 20, 4, .3)), fore: (s) => (s < 0 ? G("z", 25, 30, .55, .7) : G("z", 75, 4, .3)), chest: G("y", 0, 8, .55) },   // feeding the hens: one hand casts the grain in a wide swing, the other holds the basket
  tend:   { arm: (s) => G("z", 55, 12, .3, alt(s)), fore: (s) => G("z", 30, 15, .3, alt(s)), chest: G("z", 18, 4, .3), crouch: .15 },            // bent over the hives
  play:   { arm: (s) => G("z", 30, 4, .6, alt(s)), fore: (s) => G("z", 80, 6, 1.1, alt(s)), chest: G("z", 6, 3, .3) },              // at a keyboard: forearms out over the keys, the hands running
  // a greeting: the right arm out and up, turned in the shoulder (`twist`, outward) so the elbow bends up across the body's
  // plane -- the palm toward you -- and the hand to and fro in it (it bent forward before, a chop with the palm sideways)
  wave:   { arm: (s) => (s < 0 ? G("x", 100, 5, .8) : G("z", 0, 2, .3)), fore: (s) => (s < 0 ? { ...G("z", 62, 28, 1.6), twist: -s * 80 } : G("z", 8, 2, .3)) },
  // IDLE, standing about (index.html idleTick): a stretch, a scratch of the head, a hand shading the eyes to look far
  // off, and hands on the knees getting one's breath back (the children at tag)
  stretch: { arm: (s) => G("x", -s * 165, 6, .35), fore: () => G("z", 15, 10, .35), chest: G("z", -6, 3, .35) },
  scratch: { arm: (s) => (s < 0 ? G("x", 145, 3, .3) : G("z", 0, 2, .3)), fore: (s) => (s < 0 ? G("z", 112, 12, 3.2) : G("z", 8, 2, .3)) },
  shade:   { arm: (s) => (s < 0 ? G("z", 105, 3, .2) : G("z", 0, 2, .3)), fore: (s) => (s < 0 ? G("z", 105, 3, .2) : G("z", 8, 2, .3)) },
  puff:    { arm: () => G("z", 52, 3, .9), fore: () => G("z", 5, 2, .9), chest: G("z", -52, 4, 1.4), crouch: .1 },
  // ...and in the rain, hurrying along with both hands held over the head (index.html idleTick)
  cover:   { arm: (s) => G("x", -s * 150, 2, .4), fore: () => G("z", 118, 3, .4), chest: G("z", -10, 2, .4) },
  // the market's juggler (juggler.js): forearms out, the hands bobbing up and down in turn -- three throws a second -- and
  // the crowd's applause: forearms swinging in to meet
  juggle:  { arm: () => G("z", 22, 4, 1.5, 0), fore: (s) => G("z", 80, 18, 1.5, alt(s)) },
  clap:    { arm: () => G("z", 38, 2, .3), fore: (s) => G("x", s * 38, 22, 3.2) },   // (+s: inward -- it was -s, the hands swinging apart)
  // dancing by the bonfire: the arms up, swaying in turn with the steps
  dance:   { arm: (s) => G("x", -s * 125, 22, .9, alt(s)), fore: () => G("z", 35, 18, .9), chest: G("y", 0, 10, .45) },
  // at the river, washing linen: bent over the water, both arms down in it, scrubbing in turn
  scrub:   { arm: () => G("z", 62, 10, 1.1), fore: (s) => G("z", 25, 28, 1.1, alt(s)), chest: G("z", -42, 5, 1.1), crouch: .42 },
  // round the maypole: the right hand raised forward holding the ribbon, the left swinging free
  ribbon:  { arm: (s) => (s < 0 ? G("z", 118, 5, .8) : G("z", 10, 14, .9)), fore: (s) => (s < 0 ? G("z", 18, 5, .8) : G("z", 12, 8, .9)) },   // (a chest's +z tips its top back: the bend is -)
  // flying a kite (kites.js): both hands up before the chest on the string, tugging it now and then, leaning back a little
  kite:    { arm: (s) => G("z", 68, 7, .55, alt(s) * .2), fore: () => G("z", 30, 10, .55, .4), chest: G("z", 7, 2, .3) },
  // blowing soap bubbles (bubbles.js): the wand held up before the mouth in the right hand
  blow:    { arm: (s) => (s < 0 ? G("z", 62, 3, .4) : G("z", 4, 2, .3)), fore: (s) => (s < 0 ? G("z", 98, 4, .4) : G("z", 10, 2, .3)) },
  // on the swing (swing.js, SWING.rate swings a second): hands up on the ropes, leaning back as it goes forward; and the
  // one pushing behind -- arms thrust out each time the seat comes back (the world clock: in step with the seat)
  swing:   { arm: () => G("z", 22, 4, .36), fore: () => G("z", 85, 4, .36), chest: G("z", 2, 12, .36, Math.PI / 2) },
  // an old walker with a staff (index.html OLD): the right hand forward and a little out, the staff clear of the body
  // skimming a stone (index.html SKIM): the right arm drawn back low and whipped round forward, the body turning with it
  skim:    { arm: (s) => (s < 0 ? G("z", 25, 55, .5) : G("z", 10, 6, .5, Math.PI)), fore: (s) => (s < 0 ? G("z", 25, 25, .5, .5) : G("z", 10, 3, .5)), chest: G("y", 0, 14, .5, Math.PI / 2) },
  // leapfrog (leapfrog.js): vaulting -- both arms thrust forward and down, the hands on the frog's back
  // splashing in the river (index.html BATHE): bent forward, both arms sweeping the water up toward someone, in turn
  splash:  { arm: (s) => G("z", 40, 38, 1.6, alt(s)), fore: (s) => G("z", 20, 20, 1.6, alt(s) + .5), chest: G("z", -22, 6, 1.6), crouch: .08 },
  // skating on the frozen river (index.html SKATE): the arms held out to the sides for balance, swinging with the strokes
  skate:   { arm: (s) => G("x", -s * 55, 14, .55, alt(s)), fore: () => G("z", 18, 8, .55), chest: G("y", 0, 9, .55) },
  leap:    { arm: () => G("z", 78, 4, 1), fore: () => G("z", 12, 4, 1) },
  staff:   { arm: (s) => (s < 0 ? G("z", 24, 4, .45) : G("z", 0, 3, .45, Math.PI)), fore: (s) => (s < 0 ? G("z", 32, 4, .45) : G("z", 8, 2, .45)) },
  push:    { arm: () => G("z", 48, 32, .36, Math.PI), fore: () => G("z", 22, 14, .36, Math.PI), chest: G("z", -6, 6, .36, Math.PI) },
};
// CROUCH: a gesture done down low -- scrubbing at the water's edge, picking low fruit, a child's hands on its knees --
// bends the knees by its `crouch`, a share of the legs' length (skeleton.js: added to an.rest, by an.work)
export const CROUCH = Object.fromEntries(Object.entries(GESTURES).filter(([, g]) => g.crouch).map(([k, g]) => [k, g.crouch]));
// UNDER A CLOAK the upper arm stays down: a cloak (a mantle, a hood's fall) is cloth hung over the arms and does not move
// with them, so an arm lifted out to the side or high in front would come out through it. For a figure so dressed
// (people.js: what is hung over the arms reaches below mid upper arm) every gesture's upper-arm swing is kept low and
// forward -- no lift out to the side, at most LOW_ARM.lift forward, a little swing -- and the forearm and hand do the
// rest, out from under the cloak's front, as a cloaked person's do.
const LOW_ARM = { lift: 32, swing: 10, side: 15, fore: 75 };
// STANDING ABOUT a person is never still: the weight shifts from foot to foot and back, the body rocking a little to the
// side and to and fro (radians at most; skeleton.js idleSway, fading out as they walk) -- a statue or a still bench figure not
export const IDLE_SWAY = .022;
// A LIMB'S ROOT: how far down an arm or a leg (in its own top radii) the body holds its top -- the shoulder, the hip --
// as it moves (skeleton.js `root`, shell.js "A LIMB'S ROOT")
export const ROOT = 1.6;
// A BELLY's depth (people.js `pot`, shell.js TRUNK.pot: its forward swell, in the trunk's half-widths at a unit) -- what
// stands off the trunk clears it (the torso's `flat` as clothes.js reads it)
export const POT_CLEAR = .36;
// how much of a hanging arm's radius may lie in the body it hangs beside (people.js `abduction`: a stout body's arms lean out)
export const ARM_TOUCH = .6;
// A LIMB's kind (skeleton.js `limb`, shell.js LIMBS: a statue's bare limb carved with its muscles) -- and `left` added
// for one on the figure's +z side, so its outer side is known whatever the pose crosses; `soft` for a woman's or a
// body given `anatomy: "soft"` (shell.js LIMBS soft: its forms only hinted)
export const LIMB = { thigh: 1, shin: 2, arm: 3, fore: 4, foot: 5, left: 8, soft: 16 };
const lowArm = (g) => g && { ...g, axis: "z", bias: Math.min(g.axis === "z" ? g.bias : LOW_ARM.side, LOW_ARM.lift), deg: Math.min(g.deg, LOW_ARM.swing) };
// (...and a forearm swung out to the side -- a clap's -- swings up in front instead: the hands meet before the chest)
const lowFore = (g) => g && (g.axis === "x" ? { ...g, axis: "z", bias: LOW_ARM.fore, deg: Math.min(Math.abs(g.deg), 20), twist: 0 } : g.twist ? { ...g, twist: 0 } : g);   // (no turn: the arm is down)
const workOf = (piece, s, low = false) => Object.fromEntries(Object.entries(GESTURES).map(([k, g]) => {
  const v = typeof g[piece] === "function" ? g[piece](s) : g[piece];
  return [k, !low ? v : piece === "arm" ? lowArm(v) : piece === "fore" ? lowFore(v) : v];
}).filter(([, v]) => v));

// a town guard's kit (a makePerson outfit): the wardrobe's "soldier" -- gambeson, mail, tabard, steel cap, boots
export const SOLDIER = { named: "soldier", hair: "short", fringe: false };
export const KINDS = ["man", "woman", "child10", "child5"];
export const SEAT_CLEAR = .08;   // hip joint above a seat top: one thigh radius (see sitAt)
export const HAIRS = ["shaved", "short", "bob", "long", "ponytail", "bun", "braid"];
export const GARMENTS = Object.keys(WARDROBE.garments);   // every garment the tailor knows (assets/clothes)

const mixC = (a, b, t) => {
  const ch = (c, s) => (c >> s) & 255;
  return [16, 8, 0].reduce((o, s) => o | (Math.round(ch(a, s) + (ch(b, s) - ch(a, s)) * t) << s), 0);
};

// A person's looks and what they wear, drawn from their own seeded stream (so outfits never shift the body's
// draws): sex (a child's), hair, fringe, nose -- and an outfit from the wardrobe (clothes.js drawOutfit).
// Everything can be overridden: makePerson({ outfit }).
function outfitFor(kind, r, style, seed = 1, work = false, dress = null, full = false, avoid = null) {
  const pick = (a) => a[Math.floor(r() * a.length)];
  const child = kind.startsWith("child"), female = kind === "woman" || (child && r() < .5);
  const o = { female };
  o.hair = female ? pick(child ? ["long", "braid", "ponytail", "bob"] : ["long", "long", "bun", "bun", "braid", "braid", "ponytail", "bob"])
                  : pick(child ? ["short", "short", "crop"] : ["shaved", "short", "short", "short", "short", "crop", "curly"]);   // (a man's: no long locks or bob over a beard)
  // (a style's own hair -- wardrobe.json styles.<style>.hair: { man, woman, child } lists of assets/items/hair: the
  //  Egyptian's, the Chinese topknot -- drawn from its own stream, so the rest of the looks stay as they were)
  const hs = style && WARDROBE.styles?.[style]?.hair, hl = hs && (child ? hs.child ?? (female ? hs.woman : hs.man) : female ? hs.woman : hs.man);
  if (hl?.length) { const hr = rng(seed * 523 + 29); o.hair = hl[Math.floor(hr() * hl.length)]; o.styled = true; }
  o.fringe = r() < .3;
  o.nose = [.75 + r() * .6, .7 + r() * .7];   // width, length
  const worn = drawOutfit(kind, r, { female, style, work, only: dress?.[style]?.[kind.startsWith("child") ? (female ? "girl" : "boy") : kind], full, avoid });
  o.wear = worn.wear; o.style = worn.name;
  if (worn.hair) { o.hair = worn.hair; o.styled = true; }   // (the outfit's own: a Buddha's ushnisha)
  if (worn.beard) o.beard = worn.beard;   // (and its beard, over the face's own draw: a Buddha beardless -- face.js BEARDS)
  o.jewelry = drawJewelry(kind, female, style, seed);
  return o;
}
// THE PERIOD'S DRESS (index.html, assets/world/periods.json `dress`: a style by weight, "" the village's own): who is
// given no style of their own wears it, drawn from their seed -- the same person always dresses alike
let PERIOD_DRESS = null;
export const setPeriodDress = (weights) => { PERIOD_DRESS = weights && Object.keys(weights).length ? weights : null; };
function periodDress(seed) {
  if (!PERIOD_DRESS) return null;
  const ks = Object.keys(PERIOD_DRESS), r = rng(seed * 389 + 11);
  let x = r() * ks.reduce((t, k) => t + PERIOD_DRESS[k], 0);
  for (const k of ks) if ((x -= PERIOD_DRESS[k]) < 0) return k || null;
  return ks[ks.length - 1] || null;
}
// JEWELRY from the jewelry wardrobe, by the style and the kind (a girl's are a child's list); its own seeded stream,
// drawn after everything else, so an outfit never shifts for it -> { neck: [paths], head: path | null, ears: path | null }
function drawJewelry(kind, female, style, seed) {
  const r = rng(seed * 977 + 5), lists = JEWEL_WEAR.styles?.[style ?? "village"] ?? JEWEL_WEAR.styles?.village ?? {};
  const key = kind.startsWith("child") ? kind + (female ? "f" : "m") : kind, looks = lists[key] ?? lists[kind] ?? [];
  const total = looks.reduce((s, l) => s + (l.weight ?? 1), 0);
  let x = r() * total, look = null;
  for (const l of looks) { x -= l.weight ?? 1; if (x <= 0) { look = l; break; } }
  const pick = (a) => Array.isArray(a) ? a[Math.floor(r() * a.length)] ?? null : a ?? null;
  return { neck: [pick(look?.neck)].filter(Boolean), head: pick(look?.head), ears: pick(look?.ears) };
}
// what a garment covers, by its definition (assets/clothes): the head (a hood, a cap, a hat), the feet (shoes)
const wornOnHead = (w) => !!garmentDef(w.garment)?.head, wornOnFeet = (w) => !!garmentDef(w.garment)?.feet;

// pose: undefined = standing/walking; "sit" = thighs forward, shins down for a
// bench (place origin at seatY - hipY); "ride" = legs astride a mount's
// flanks; "carry" = both arms round a load held in front, legs still
// walking; "lie" = flat on the back, head toward +x, back on y = 0; "guard" = at the watch: the weapon arm (the
// figure's right) lifted, the forearm forward; "draw" = drawing a bow, the legs still walking; "recline" = built
// standing, to be laid on its side by its joints (statues.js: a pediment's corner) -- its long cloth falls in round the
// legs.
// still: strip every swing and the leg IK so the figure holds perfectly still.
// kind: "man" | "woman" | "child10" | "child5" -- drawn from the seed unless
// given (adult: true keeps to men and women). It sets height, build, hair,
// clothes and the children's proportions (bigger heads, shorter legs), and it
// is what the voice follows: a woman's voice on a woman, a child's on a child.
// style: another time and place's dress, drawn from the wardrobe's `styles` (greek, roman, chinese, gothic) by kind.
// outfit: overrides for the drawn looks and wardrobe -- hair, fringe; `wear`: the garments ([{ garment, fabrics:
// { slot: { pattern, palette | colors } }, params }], clothes.js); `named`: a kit of the wardrobe's (a guard's, a
// beast-man's); `bare`: nothing at all (the canon); `hat: "none"`: nothing on the head; `add`: garments (or their
// names) worn over the drawn ones -- a head's in place of a hat; `dress`: { style: { kind: [outfit names] } } -- which
// of a style's outfits it may be drawn in (a statue's: statuary.json `dress`); `full`: all of that outfit worn.
// work: one at work -- in a field, at a forge, under a sack -- dresses from the wardrobe's working outfits (`work`).
// beast: an animal-headed man (species.js beastman: the minotaur, the wolfman...) -- the same frame, heavier,
// in the animal's hide: its own head parts scaled to a human-sized head, its tail, hooves or paws; no clothes,
// hair or hat. { hide, foot, hoof, build, headScale, eye, head: { r, color, pat, parts (head-local) }, tail: [parts] }
// upper: the upper body alone -- the torso pill and all above it on the pelvis bone, no legs, skirts or
// gait (a centaur's: mammals.js hangs it on the horse's chest); pelvisY reports where the bone sits.
// the KIND a seed is drawn as (its stream's first draw: makePerson's own) -- who someone will be before they are made:
// the villagers' jobs are handed out by it (village-life.js)
const kindFrom = (kr, adult) => adult ? (kr < .5 ? "man" : "woman") : kr < .4 ? "man" : kr < .8 ? "woman" : kr < .9 ? "child10" : "child5";
export const personKind = (seed, adult = false) => kindFrom(rng(seed * 771 + 13)(), adult);
export function makePerson({ seed = 1, height, pose, still, kind, adult, outfit, beast = null, upper = false, body = null, style = null, skin: skinAs = null, hair: hairAs = null, old = false, work = false, anatomy = null, physique = null, fat: fatAs = null } = {}) {
  const B = body ?? BODY;   // `body`: another canon than the world's (the asset viewer, editing it live)
  const r = rng(seed * 771 + 13);
  const kr = r();
  if (!kind) kind = kindFrom(kr, adult);
  const isChild = kind.startsWith("child");
  const st = B.stature[kind] ?? B.stature.man;
  // HOW THIS ONE DIFFERS (body.json build.variety, bodyOf below): a stream of its own, so every other draw keeps its seed --
  // the stature's draw made bell-shaped by a second one, then fat and frame (drawn once the sex is known)
  // (its seed mixed with the KIND: a man and a woman of one seed were the same build)
  const V = B.build.variety, vr = rng(seed * 1931 + 47 + [...kind].reduce((a, c) => a * 31 + c.charCodeAt(0), 0) % 100003), hu = r(), hv = vr();
  const h = height ?? st[0] + st[1] * (V ? hu + (hv - hu) * V.height : hu);
  const skinDrawn = SKIN[Math.floor(r() * SKIN.length)], skin = skinAs ?? (beast ? beast.hide : skinDrawn);   // (skinAs: a demon's red)   // (drawn either way: the seed's stream stays put)
  const hairDrawn = HAIR[Math.floor(r() * HAIR.length)];   // (drawn either way: the seed's stream stays put)
  const hairC = hairAs ?? (old && !isChild ? OLD_HAIR[Math.floor(hairDrawn % OLD_HAIR.length)] : isChild && GREY_HAIR.has(hairDrawn) ? 0xa87433 : hairDrawn);   // (old: grey, or white; a child never grey; hairAs: a gold statue's)
  const bs = B.build;
  const build = (isChild ? bs.child : 1) * (bs.spread[0] + r() * bs.spread[1]) * (beast?.build ?? 1);   // widths
  const headPh = r() * 3;
  style ??= outfit?.named || outfit?.bare || beast ? null : periodDress(seed);   // (one given no style of its own: the period's)
  const drawn = outfitFor(kind, rng(seed * 313 + 7), style, seed, work, outfit?.dress, !!outfit?.full, outfit?.avoid);
  const o = { ...drawn, ...(outfit ?? {}) };
  if (outfit?.named) o.wear = namedOutfit(outfit.named).wear;
  if (outfit?.bare || (beast && !outfit?.named && !outfit?.wear)) o.wear = [];
  if (o.hat === "none") o.wear = o.wear.filter((w) => !wornOnHead(w));
  // (`add`: garments put on over what was drawn -- a statue's helmet; one worn on the head takes the place of a hat)
  if (outfit?.add?.length) {
    const add = outfit.add.map((g) => typeof g === "string" ? { garment: g, fabrics: {}, params: {} } : g);
    o.wear = [...o.wear.filter((w) => !(add.some(wornOnHead) && wornOnHead(w))), ...add];
  }
  // a beast, not a man: the hide all over -- then what it wears, but never human hair, a hat (horns and ears) or
  // footwear (hooves, paws)
  if (beast) { o.hair = "shaved"; o.wear = o.wear.filter((w) => !wornOnHead(w) && !wornOnFeet(w)); }
  // ASTRIDE: no long skirts -- a gown is ridden in as a tunic of the same cloth, and hose go on under it
  if (pose === "ride") {
    o.wear = o.wear.map((w) => (garmentDef(w.garment)?.skirted ? { ...w, garment: "tunic", params: {} } : w)).filter((w) => w.garment !== "apron");
    if (!o.wear.some((w) => w.garment === "hose" || w.garment === "breeches")) o.wear.unshift({ garment: "hose", fabrics: { main: { pattern: "fabrics/plain", palette: "russet" } } });
  }
  const female = !!o.female;

  // ---- proportions: assets/people/body.json, every measure a fraction of the stature (children: bigger
  // heads, shorter legs). The numbers are THERE, not here -- this is the body they describe.
  const Bt = B.torso, Bh = B.head, Ba = B.arm, Bl = B.leg;
  const S = h / 1.75, S0 = 1;   // S0: the adult reference scale (seat depth)
  // the few widths a person's sex moves -- and its PHYSIQUE's (body.json `build.physiques`: a statue's ideal, the heroic
  // athlete's V of a trunk, a Buddha's lion shoulders), multiplied in
  const sx0 = female ? bs.sex.female : bs.sex.male, ph = physique ? bs.physiques?.[physique] : null;
  if (physique && !ph) console.warn(`person: no physique "${physique}" (body.json build.physiques)`);
  const sx1 = ph ? Object.fromEntries([...new Set([...Object.keys(sx0), ...Object.keys(ph)])].filter((k) => k !== "_about").map((k) => [k, (sx0[k] ?? 1) * (ph[k] ?? 1)])) : sx0;
  // ...and THIS ONE's BUILD (body.json build.variety): fat (thin .. stout .. fat) and the frame's breadth -- none for an
  // ideal (a physique: a statue's canon) or a beast; `fat` given, that (the lineups)
  const fz = (vr() + vr() + vr() - 1.5) * 2, frz = (vr() + vr() + vr() - 1.5) * 2;   // (about a unit bell each; drawn either way: the stream stays put)
  const fat = !V || ph || beast ? 0 : fatAs ?? Math.max(V.fat.min, Math.min(V.fat.max, (fz > 0 ? fz * V.fat.sd * (1 + V.fat.skew * fz * V.fat.sd) : fz * V.fat.sd) * (isChild ? V.fat.child : 1) + (old && !isChild ? V.fat.old : 0)));
  const frame = !V || ph || beast ? 0 : frz * V.frame * (isChild ? .5 : 1);
  const pf = V?.perFat?.[female ? "female" : "male"] ?? {}, fe = fat < 0 ? fat * (V?.thinShare ?? 1) : fat;
  const F = (k) => 1 + (pf[k] ?? 0) * fe;   // (a width's factor for this much fat)
  const sx = { ...sx1, shoulders: sx1.shoulders * (1 + frame) * F("shoulders"), chest: (sx1.chest ?? 1) * F("chest"), waist: sx1.waist * F("waist"), hips: sx1.hips * (1 + frame * .8) * F("hips"),
               thighs: sx1.thighs * F("thighs"), arms: (sx1.arms ?? 1) * F("arms"), knees: F("knees"), bust: sx1.bust * F("depth") };
  // (the BELLY: the trunk's forward swell over the waist, shell.js TRUNK.pot -- carried by the torso's cuts; the face's
  //  FULLNESS, one of a few steps of fat, heads.js `full`)
  const pot = Math.max(0, fat) * (pf.belly ?? 0);
  const fb = V?.fullBins ?? [-1, 1, 2], full = fat < fb[0] ? -1 : fat >= fb[2] ? 2 : fat >= fb[1] ? 1 : 0;
  const hr = h * (kind === "child5" ? Bh.r.child5 : kind === "child10" ? Bh.r.child10 : Bh.r.adult);
  const hipY = h * (kind === "child5" ? Bt.hip.child5 : kind === "child10" ? Bt.hip.child10 : Bt.hip.adult);
  const shY = h - Bt.shoulder.heads * hr - Bt.shoulder.fromCrown * h, T = shY - hipY;
  const pelY = hipY + Bt.pelvis * T, waistY = hipY + Bt.waist * T, headY = h - hr;
  // THE TORSO: one shape flattened front to back, through four rings -- the shoulders' rim (sW across), the chest
  // under the armpits (tW), the natural waist (wW), the hips (hW) -- its top a low squared cap up to the collar,
  // the shoulders, and its bottom a rounder one down to the crotch
  const HW = Bt.halfWidth, wid = h * build;
  const sW = HW.shoulder * wid * sx.shoulders, tW = HW.chest * wid * sx.shoulders * (sx.chest ?? 1), wW = HW.waist * wid * sx.waist, hW = HW.hip * wid * sx.hips;
  const rimY = shY - Bt.rim * h, pitY = shY - Bt.armpit * h, collarY = shY + Bt.collar * h, baseY = hipY + Bt.base * h, crotchY = hipY - Bt.crotch * h;
  // (a BELLY stands out of the trunk's front by POT_CLEAR of its half-width a unit, shell.js TRUNK.pot: what stands off the
  //  trunk -- a skirt from the waist, an apron, a cloak -- clears that much more depth)
  const torsoFlat = Bt.depth * sx.bust, torsoClear = (Bt.depthClear ?? Bt.depth) * sx.bust + POT_CLEAR * pot;   // (what is drawn; and what stands off it clears: the shell's masses, shell.js TRUNK, stand out of the drawn depth)
  const RINGS = [[rimY, sW], [pitY, tW], [waistY, wW], [baseY, hW]];
  const torsoHalf = (y) => {   // its half-width at a height: over the shoulders' cap, and between the rings
    if (y >= collarY) return 0;
    if (y >= RINGS[0][0]) { const u = (y - rimY) / (collarY - rimY), p = Bt.capSquare; return sW * Math.pow(Math.max(0, 1 - Math.pow(u, p)), 1 / p); }
    for (let i = 1; i < RINGS.length; i++) if (y >= RINGS[i][0]) { const [y0, r0] = RINGS[i - 1], [y1, r1] = RINGS[i]; return r1 + (r0 - r1) * (y - y1) / (y0 - y1); }
    return hW;
  };
  const armU = Ba.upper * h, armF = Ba.fore * h, rArmU = Ba.rUpper * h * build * (sx.arms ?? 1), rElbow = Ba.rElbow * h * build * sx.knees, rArmF = Ba.rFore * h * build * (sx.arms ?? 1), rWrist = Ba.rWrist * h * build;
  // THE HAND, not a fist. A ball on the wrist left every arm a tenth of a body short: a real hand is .11 of
  // the stature long (the wrist sits at .49 h, the fingertips at .38), as wide as it is thick is thin. It is
  // a flattened pill down the forearm -- no fingers at this scale, a mitten, which is what the coat sleeves
  // and gloves of the period look like anyway.
  const rHand = Ba.rHand * h, handL = Ba.hand * h;
  const ankY = Bl.ankle * h, legU = (hipY - ankY) * Bl.upperShare, legLo = hipY - ankY - legU;
  const rThigh = Bl.rThigh * h * build * sx.thighs, rKnee = Bl.rKnee * h * build * sx.knees, rAnk = Bl.rAnkle * h, rFoot = Bl.rFoot * h;
  const hipZ = Bl.hipZ * h * build * sx.hips;
  // THE ARMS HANG BESIDE THE TORSO, not in it: the shoulder joint a little under the rim at its end, the arm's cap
  // ending the shoulder's line, the arm leaning out by `abduction` -- so below the armpit it clears the chest and the hips,
  // and a sleeve and a bodice are two sheets that meet at the shoulder instead of one passing through the other
  const armY = rimY - Ba.drop * h, shZ = sW + Ba.gap * h;   // (the joint under the end of the shoulder, so the arm's cap is the end of that line; the lean takes it clear of the ribs below the armpit)
  // (...leaning out further where the body is wider below the shoulders than the canon's lean clears -- a stout waist, a
  //  fat woman's hips and thighs: the arm hangs over them, not through them; `ARM_TOUCH` of its radius may lie in them, as
  //  a hand at rest lies against the thigh)
  let abduction = Ba.abduction;
  for (let k = 1; k <= 12; k++) {
    const d = (armU + armF) * k / 12, y = armY - d, ra = d < armU ? rArmU + (rArmF - rArmU) * d / armU : rArmF + (rWrist - rArmF) * (d - armU) / armF;
    const body = Math.max(y >= crotchY ? torsoHalf(y) : 0, y < baseY ? hipZ + rThigh : 0);
    abduction = Math.max(abduction, Math.atan2(body + ra * (1 - ARM_TOUCH) - shZ, d) * 180 / Math.PI);
  }
  // a beast's animal parts (head and tail): scaled so its head sphere is a man's, a little over (the muzzle adds length)
  const bf = beast ? hr * (beast.headScale ?? 1.1) / beast.head.r : 1;
  const beastPart = (p) => { const q = scalePart(p, bf); if (q.k) q.k *= bf; if (beast.eye && q.dot) q.dot = { ...q.dot, iris: beast.eye }; return q; };

  const mouthC = mixC(skin, 0xb8323a, .82);   // lips: clearly red

  const parts = [];
  const add = (p) => { const q = { edge: 0, seam: true, ...p }; parts.push(q); return q; };
  // a bone hanging from `pos` along direction dir: its A end (radius rA) at pos
  const bone = (id, parent, pos, dir, len, rA, rB, extra = {}) => {
    // (a round cone needs its radii to differ by less than its length -- except a garment's CUT shell, which is swept
    //  as a plain cone between its cuts and may be as flat as a cape over the shoulders)
    if (Math.abs(rA - rB) >= len && !extra.clip) console.warn(`person: ${id}: radii ${rA.toFixed(3)}/${rB.toFixed(3)} over ${len.toFixed(3)}m make no round cone (one sphere swallows the other)`);
    return add({ id, parent, shape: "capsule", size: { r: rA, r2: rB, len }, pos, rot: hangRot(dir), pivot: [0, -len / 2, 0], ...extra });
  };
  // a sphere of radius R at c with an axis n (a capsule of 1cm along it), cut by the slab
  // [lo, hi] along n measured from c; lo from a point P0 on the cutting plane
  const ball = (id, parent, c, R, n, P0, extra = {}) => {
    n = vNorm(n);
    const lo = P0 ? vDot(vSub(P0, c), n) : -1e4;
    return bone(id, parent, c, n, .01, R, R, { ...extra, clip: { lo, hi: 1e4, ...(extra.clip ?? {}) } });
  };

  // ---- the torso: ONE flattened round cone (composite `flat`) from the hips to the shoulders -- its depth a
  // share of its width, the shoulders its low squared top cap (`caps`), the crotch its bottom one -- on the pelvis
  // (the root, an x-capsule: the "body frame" of the coat and the figure's forward; an undrawn bone). It stands
  // for four lobes (pelvis, hips, belly, chest) and the yoke that once lay across its top: one shape.
  const kT = .05 * S;
  add({ id: "pelvis", parent: null, shape: "capsule", size: { r: hW, len: .04 * S }, geomRot: [0, 0, 90], pos: [0, pelY, 0], bob: true, bone: true,   // the root: posed (its x axis is the body's forward), not drawn -- the torso takes its girth
        frame: "body", k: kT, color: skin });
  // (its frame -- neck, head, arms and hair hang on it -- has its origin at the pelvis, chestO: a working bend or a
  // twist turns the torso about its bottom, the hips, so it never swings its belly off the legs)
  const chestO = pelY;
  // three cuts laid end to end, SWEPT AS ONE (shell.js: flat `spine` parts chain): the shoulders down to the
  // armpits, the chest down to the waist, the hips below. The first carries the figure's twist and the work
  // gestures; the other two hang on it, so the torso bends about the hips as one piece.
  // (each carries where it is on the trunk -- `anat`: its ends' heights from the crotch to the shoulders' rim, 0..1, and
  //  whether it is SOFT, a woman's or a body given `anatomy: "soft"` (a Buddha's: no muscle cut), 16384, and a WOMAN's,
  //  32768 more (her bust: shell.js TRUNK) -- for the anatomy a statue's torso is carved with, shell.js ANATOMY)
  const trunkAt = (y) => Math.round(Math.max(0, Math.min(1.27, (y - crotchY) / (rimY - crotchY))) * 100);
  const cut = (id, parent, [yA, rA], [yB, rB], extra = {}) => add({ id, parent, shape: "capsule", pos: [0, 0, 0], frame: "body", k: kT, spine: true,
        size: { r: rA, r2: rB, len: yA - yB }, pivot: [0, (yA + yB) / 2 - chestO, 0], flat: torsoFlat, color: skin,
        anat: 1 + trunkAt(yA) + 128 * trunkAt(yB) + (female || anatomy === "soft" ? 16384 : 0) + (female ? 32768 : 0), ...(pot > 0 ? { pot } : {}), ...extra });   // (pot: its belly, shell.js TRUNK.pot)
  cut("chest", "pelvis", RINGS[0], RINGS[1], { caps: { a: (collarY - rimY) / sW, b: 1, p: Bt.capSquare },
        anim: { axis: "y", deg: 4, speed: .8, phase: Math.PI, amp: true, work: workOf("chest", 1) } });
  cut("belly", "chest", RINGS[1], RINGS[2]);
  cut("hips", "chest", RINGS[2], RINGS[3], { caps: { a: 1, b: (baseY - crotchY) / hW, p: 1.6 } });   // (narrowing early, into the thighs: not a hem standing over them)
  // THE NECK STARTS UNDER THE JAW, not inside the skull. The shell engine sweeps a part and its neighbour as
  // ONE LATHE where they meet, share a colour and run the same way -- head and neck do all three -- and the
  // neck's top used to sit ABOVE the chin, so that lathe doubled back on itself and came out as one long
  // smooth funnel from the cranium to the shoulders. That, not the length of anything, is what made every
  // person look long-necked: there was no jaw in the drawn surface at all. Started just inside the jaw's own
  // ball, the sweep runs straight down and the radius steps from jaw to neck in three centimetres -- a
  // jawline.
  const hL = beast ? 0 : Bh.jawLength * hr, hJaw = Bh.jawRadius * hr;
  const neckBot = collarY - .02 * h, neckTop = headY - hL - hJaw * .4;   // (its foot inside the shoulders' cap)
  const neckR = hr * (isChild ? Bh.neckRadius.child : beast ? Bh.neckRadius.beast : ph ? Bh.neckRadius.ideal ?? Bh.neckRadius.adult : female ? Bh.neckRadius.female ?? Bh.neckRadius.adult : Bh.neckRadius.adult) * F("neck");   // (a statue's physique: the sculptor's, `ideal`)
  // (a physique's `neck`: the athlete's strong neck -- its foot that much wider, rising into the shoulders, its top under
  //  the jaw a third of it: as wide all the way up, it stood out before the chin)
  const neckFoot = neckR * (ph?.neck ?? 1) * (Bh.neckFoot ?? 1), neckHead = neckR * (1 + ((ph?.neck ?? 1) - 1) / 3);
  // (leaning forward as it rises, the head carried a little before the chest: `neckLean`, a column stood straight up and the
  //  head sat on it like a ball on a post; its foot wider, the trapezius rising into it: Bh.neckFoot)
  add({ id: "neck", parent: "chest", shape: "capsule", size: { r: neckHead, r2: neckFoot, len: neckTop - neckBot }, pos: [0, (neckTop + neckBot) / 2 - chestO, 0], rot: [0, 0, -(beast ? 0 : Bh.neckLean ?? 0)], color: skin, k: .03 * S });
  // The head is an OVOID, not a ball: a round cone standing on its own axis -- the CRANIUM is the sphere it
  // always was (its top cap centre sits at the part's own origin, so the hair, the hats and the eyes keep
  // exactly the places they had), and below it the head runs on for hL and narrows to hJaw: a jaw and a chin.
  // That, not a symmetric stretch, is what makes a head read as a head -- the stretch hides under the hair,
  // the jaw is the part a face shows. (Round about its axis: it cannot also be narrower across than deep.)
  // (hL, hJaw: the jaw, declared above the neck that hangs under it)
  const headPart = add({ id: "head", parent: "chest", shape: "capsule", size: { r: hr, r2: hJaw, len: hL }, pivot: [0, -hL / 2, 0],
        pos: [(beast ? .01 * S : (Bh.forward ?? .006) * h), headY - chestO, 0], color: skin, k: .02 * S,
        anim: { axis: "y", deg: 14, speed: .22, phase: headPh } });

  // ---- the face (head-local, in head radii)
  const H = (x, y, z = 0) => [x * hr, y * hr, z * hr];
  // ON THE HEAD: where the ray from the head's origin in direction d leaves the ovoid. Inside a round cone is
  // "within the tapered radius of some point of its axis", so this bisects on that -- to well under a
  // millimetre, at build time, once. It keeps every feature's ANGLE, so the face's layout is the one the
  // sphere gave; without it a mark placed at hr would sit a centimetre inside the skin at the chin and the
  // composite, which paints a mark only within a hair of its own plane, would silently drop it (the mouth first).
  const onHead = (d) => {
    const n = vNorm(d);
    const inside = (t) => {
      const p = n.map((c) => c * t);
      for (let i = 0; i <= 48; i++) {   // down the axis: origin (the cranium's centre) to hL below it
        const u = i / 48;
        if (Math.hypot(p[0], p[1] + hL * u, p[2]) <= hr + (hJaw - hr) * u) return true;
      }
      return false;
    };
    let lo = 0, hi = hr + hL + .01;
    for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2; if (inside(m)) lo = m; else hi = m; }
    return n.map((c) => c * lo);
  };
  // a face mark (composite FACE MARKS: drawn flat on the head, no SDF): centred where direction d meets the
  // head, its corners half-angle `half` (radians) to either side about the vertical, half-height h
  const rotYv = (v, a) => [v[0] * Math.cos(a) + v[2] * Math.sin(a), v[1], -v[0] * Math.sin(a) + v[2] * Math.cos(a)];
  const mark = (id, d, half, h, color, iris, style = {}) => {
    const c1 = onHead(rotYv(d, half)), c2 = onHead(rotYv(d, -half)), w = vSub(c2, c1);
    return bone(id, "head", c1, w, Math.hypot(...w), h, h, { color, dot: iris !== undefined ? { iris, ...style } : { ...style } });
  };
  const iris = (() => { const e = rng(seed * 577 + 29)(); let a = 0, tot = IRIS.reduce((t, [, w]) => t + w, 0); for (const [c, w] of IRIS) if ((a += w / tot) >= e) return c; return IRIS[0][0]; })();   // (its own stream: every other trait keeps its seed)
  const eR = Math.max(.012, .15 * hr);
  const meshFace = PEOPLE.face && !beast;
  if (beast) {   // the beast's head: the animal's own -- its head sphere's children (muzzle, ears, eye marks, nose, horns, tusks) -- man-sized
    Object.assign(headPart, { shape: "sphere", size: { r: beast.head.r * bf }, color: beast.head.color, pat: beast.head.pat, fur: true });
    for (const p of beast.head.parts) parts.push(beastPart(p));
  } else if (meshFace) {
    // THE MESH HEAD (face.js: a low-poly head on the anatomy, drawn by heads.js at this head part every frame): the
    // SDF head shrinks to a pin (it stays the parent of the hair and the hat, and the frame the mesh is placed in),
    // and a pin of a nose stays as the GAZE -- the direction the face looks, read back with the head's ends
    // -- both as BONES of the rig (k = -1): posed, never drawn, no shell (the geometry view showed them as a spike)
    headPart.size = { r: .004, r2: .004, len: hL }; headPart.bone = true;
    bone("nose", "head", H(.1, 0), [1, 0, 0], .4 * hr, .002, .002, { color: skin, bone: true });   // (inside the skull: only its direction is read)
  } else {
  for (const s of [1, -1]) {
    const d = vNorm([.87, .16, .4 * s]);
    mark(s > 0 ? "eyeL" : "eyeR", d, .95 * eR / hr, .42 * eR, SCLERA, iris, { role: "eye", side: s, reach: 1.9 });   // white, its iris and pupil; the socket sinks round it (reach)
    // an eyebrow: a thin dark lens above it -- and the BROW RIDGE it lies on, which the head sphere has no shape for:
    // relief 1 gives the forehead its break in the light alone, out to four times the lens's own half-height
    mark(s > 0 ? "browL" : "browR", vNorm([.86, .34, .42 * s]), 1.15 * eR / hr, .13 * eR, mixC(hairC, 0x000000, .35), undefined, { role: "brow", side: s, relief: 1, reach: 4 });
  }
  const [noseW, noseL] = o.nose;
  if (PEOPLE.nose) bone("nose", "head", onHead([.875, .29, 0]), [.29 * noseL, -.46, 0], hr * Math.hypot(.29 * noseL, .46), .09 * hr * noseW, .14 * hr * noseW, { color: skin, k: .01 * S });
  mark("mouth", vNorm([.87, -.5, 0]), .24, .07 * hr, mouthC, undefined, { role: "mouth" });   // the lips: a lens
  }

  // ---- hair: a cap cut at the hairline, plus the style's volumes. The caps are SOLID cuts, not open shells:
  // a shell shows the far wall's inside at the cut (darkened), which at the hairline reads as a gap between the
  // hair and the skin -- hollow hair. Solid, the cut is a filled face and the hair meets the skin along an edge.
  const hairM = { color: hairC, color2: mixC(hairC, 0x000000, .38), pat: "hair", cloth: { scale: 110, wear: 0 } };   // strands (composite pattern 16), darker between them
  const capPlane = (F, N) => { const d = vSub(N, F); let n = [-d[1], d[0], 0]; if (n[1] < 0) n = n.map((c) => -c); return n; };
  // UNDER A HAT THE HAIR LIES FLAT. The cap is a little wider than the skull, and a hat's crown is drawn to
  // fit the skull -- so as SOLIDS the hair came out through the hat all round its brim and over its top. (The
  // SDF never showed it: among the parts covering a pixel it drew the NEAREST surface, which was the hat.)
  const hatOn = o.wear.some(wornOnHead);
  // (...and under a veil that covers it all -- a garment's `hair`: "none", a headscarf, a maphorion -- none shows at all:
  //  not even the flat hair's ends at the nape, which came out below it)
  const hairUnder = o.wear.map((w) => garmentDef(w.garment)?.hair).find(Boolean);
  // the MESH HEAD wears its hair as strands (hair.js, assets/items/hair): the SDF hair below is the capsule head's
  const MESH_HAIR = { shaved: "none", short: "short", bob: "bob", long: "long", ponytail: "ponytail", bun: "bun", braid: "braid" };
  // (a woman's long hair: straight, wavy or drawn in locks by her seed, her bob either way, a man's short hair now and
  //  then in locks; any other word an item hairstyle by its own name -- assets/items/hair)
  const meshHair = !meshFace ? null : hatOn ? (o.hair === "shaved" || hairUnder === "none" ? "none" : "flat")
    : o.styled ? MESH_HAIR[o.hair] ?? o.hair   // (a style's own hair: as it says -- no manga variant in another time)
    : o.hair === "long" && female ? ["long", "long-wavy", "manga-long"][seed % 3]
    : o.hair === "bob" && female && seed % 2 ? "manga-bob"
    : o.hair === "short" && !female && seed % 4 === 3 ? "manga-short"
    : MESH_HAIR[o.hair] ?? o.hair ?? "short";
  if (!meshFace && o.hair !== "shaved") {
    const F = o.fringe ? H(.87, .5) : H(.7, .72),   // the hairline in front: a forelock ends just above the brows, else higher -- a forehead
          N = o.hair === "short" ? H(-.92, -.5) : H(-.95, -.15);
    const cap = hatOn ? 1.015 : (o.hair === "short" ? 1.07 : 1.1);
    ball("hairC", "head", H(-.02, .02), hr * cap, capPlane(F, N), F, { ...hairM, clip: { solid: true } });
  }
  if (!meshFace && (o.hair === "bob" || o.hair === "long"))   // down to the jaw at the back and sides, the face open
    ball("hairB", "head", H(-.12, -.1), hr * (hatOn ? 1.04 : o.hair === "bob" ? 1.22 : 1.18), [-1, -.1, 0], H(.44, 0), { ...hairM, clip: { solid: true } });
  if (!meshFace && o.hair === "long") {   // a fall of hair: ONE curved surface like a skirt -- a round-cone shell
    // from the back of the head down to the shoulder blades, tilted back a little and cut open at
    // the front (clip.back: nothing more than 4cm in front of its top, which sits at the head's
    // centre), so it wraps the back of the head and shoulders and leaves the face and chest free
    // (wide enough at the bottom that the shoulder blades stay under it, not poking past its edges)
    const top = [.01 * S - .05 * hr, headY - chestO + .05 * hr, 0], yB = shY - .1 * h - chestO, len = top[1] - yB;
    bone("hairL", "chest", top, [-.05, -1, 0], len, 1.06 * hr, sW * .95,
         { ...hairM, clip: { lo: 0, hi: len, back: -.26 * hr }, anim: { axis: "z", deg: 3, speed: .8, phase: -.9, amp: true } });
  }
  if (!meshFace && o.hair === "ponytail")
    bone("hairT", "head", H(-.92, .15), [-.35, -1, 0], 2.2 * hr, .32 * hr, .18 * hr, { ...hairM, anim: { axis: "z", deg: 7, speed: .8, phase: -.9, amp: true } });
  if (!meshFace && o.hair === "bun") add({ id: "hairN", parent: "head", shape: "sphere", size: { r: .45 * hr }, pos: H(-.85, .5), ...hairM });
  if (!meshFace && o.hair === "braid")
    bone("hairP", "head", H(-.95, -.25), [-.12, -1, 0], 3.3 * hr, .26 * hr, .15 * hr,
         { color: hairC, color2: mixC(hairC, 0x000000, .4), pat: "braid", cloth: { scale: Math.round(1 / (.5 * hr)) }, anim: { axis: "z", deg: 6, speed: .8, phase: -.9, amp: true } });

  // (an arm's and a leg's ROOT: its top held to the body over ROOT of its own radius -- the shoulder and the hip stay where
  //  they are and the limb bends away from them, as a sleeve sewn in at the shoulder does: skeleton.js `root`)
  // ---- arms: upper (swings on the gait), forearm (bends more as it swings forward), hand -- hung beside the
  // torso (armY, shZ: the proportions above)
  // (the elbow bends only up, as far as joints.json has it, in a plane the shoulder's rotation can turn -- its sign by side)
  const limbOf = (k, s) => LIMB[k] + (s > 0 ? LIMB.left : 0) + (female || anatomy === "soft" ? LIMB.soft : 0);   // (LIMB: its kind, side, softness)
  const EL = JOINTS.joints.elbow.movements.flexion, ROT = JOINTS.joints.shoulder.movements.rotation;
  // (the ELBOW one girth, the upper arm's end and the forearm's root: between the joint's own and the forearm's -- each its
  //  own, the forearm stood out of the elbow a step, or in, as a physique's arms took it fuller: a seam round a carving)
  const rElbowJ = (rElbow + rArmF) / 2;
  for (const [s, tag] of [[1, "L"], [-1, "R"]]) {
    const ph = s > 0 ? Math.PI : 0;   // the left arm swings forward with the right leg
    add({ id: "arm" + tag, parent: "chest", shape: "capsule", size: { r: rArmU, r2: rElbowJ, len: armU },
          pos: [0, armY - chestO, s * shZ], rot: [-s * abduction, 0, 0], pivot: [0, -armU / 2, 0], k: .025 * S, color: skin, root: ROOT * rArmU, limb: limbOf("arm", s),
          anim: { axis: "z", deg: 20, speed: .8, phase: ph, amp: true, work: workOf("arm", s) } });
    add({ id: "fore" + tag, parent: "arm" + tag, shape: "capsule", size: { r: rElbowJ, r2: rWrist, len: armF },
          pos: [0, -armU, 0], rot: [0, 0, JOINTS.joints.elbow.rest.flexion], pivot: [0, -armF / 2, 0], k: .01 * S, color: skin, limb: limbOf("fore", s),
          hinge: { bend: [EL.min, EL.max], turn: s > 0 ? [ROT.min, ROT.max] : [-ROT.max, -ROT.min] },   // (skeleton.js HINGE)
          anim: { axis: "z", deg: 9, speed: .8, phase: ph, amp: true, work: workOf("fore", s) } });
    add({ id: "hand" + tag, parent: "fore" + tag, shape: "capsule", size: { r: rHand * .95, r2: rHand, len: handL }, flat: .5, palm: true, caps: { a: 1, b: .6, p: 2.6 },
          pos: [0, -armF, 0], pivot: [0, -handL / 2, 0], color: skin, k: .008 * S });
  }

  // ---- legs: thigh (IK driver), shin (follows), foot (kept flat)
  for (const [s, tag, i] of [[1, "L", 0], [-1, "R", 1]]) {
    add({ id: "leg" + tag, parent: "pelvis", shape: "capsule", size: { r: rThigh, r2: rKnee, len: legU }, pos: [0, hipY - pelY, s * hipZ],
          pivot: [0, -legU / 2, 0], k: .02 * S, ik: { leg: i, upper: legU, lower: legLo, side: 1, foot: ankY - pelY, phase: 0 }, color: skin, root: ROOT * rThigh, limb: limbOf("thigh", s) });
    add({ id: "shin" + tag, parent: "leg" + tag, shape: "capsule", size: { r: rKnee, r2: rAnk, len: legLo }, pos: [0, -legU, 0],
          pivot: [0, -legLo / 2, 0], k: .01 * S, ik: { leg: i, follow: true }, color: skin, limb: limbOf("shin", s) });
    const fl = Bl.foot * h;
    if (beast?.hoof)   // a hoof, not a foot: a round horn cone from the ankle down to the ground, widening to the tread
      bone("foot" + tag, "shin" + tag, [0, -legLo, 0], [0, -1, 0], ankY * .95, rAnk * 1.15, rAnk * 1.6, { color: beast.foot, level: true, k: .008 * S });
    // (its frame's origin at the ANKLE, the joint it turns in; the foot itself drawn forward of and below it, on the ground:
    //  round at the heel, narrowing to the toes -- tipped toes down by the difference, its sole flat on the ground and its
    //  instep falling to them)
    else {
      const rToe = rFoot * Bl.toe, fLen = fl - rFoot - rToe, tip = Math.asin((rFoot - rToe) / fLen) * 180 / Math.PI;
      add({ id: "foot" + tag, parent: "shin" + tag, shape: "capsule", size: { r: rFoot, r2: rToe, len: fLen }, geomRot: [0, 0, 90 - tip],
            pos: [0, -legLo, 0], pivot: [.055 * S, (rFoot + rToe) / 2 - ankY, 0], level: true, k: .008 * S, color: beast ? beast.foot : skin, ...(beast ? {} : { limb: limbOf("foot", s) }) });
    }
  }

  if (beast?.tail?.length) {   // the animal's own tail (its arc of links, a tuft), scaled with the head, from the rump
    const [first, ...rest] = beast.tail.map(beastPart);
    parts.push({ ...first, parent: "pelvis", pos: [-hW * torsoFlat * .95, .02 * S, 0] }, ...rest);
  }
  if (beast) for (const p of parts) if (p.color === skin && !p.dot) p.fur = true;   // the hide is a coat

  // ---- CLOTHES: the tailor (clothes.js) lays the outfit on the body. It is told the body's FORM -- its hosts (the
  // torso, the arms, the legs, the feet, the neck, the head), the parts each is made of, their landmarks and girths --
  // and it dresses the parts that follow the body (layers of sheet: `dress`) and adds the pieces that stand off it
  // (a skirt, a cloak, a hood, a hat: shells of their own)
  const byId = (id) => parts.find((p) => p.id === id);
  const kneeY = ankY + legLo, handY = armY - armU - armF - handL;
  const abd = Math.sin(abduction * Math.PI / 180);
  const armR = (d) => d < armU ? rArmU + (rElbowJ - rArmU) * d / armU : d < armU + armF ? rElbowJ + (rWrist - rElbowJ) * (d - armU) / armF : rHand;
  const ellipse = (a, b) => { const q = ((a - b) / (a + b)) ** 2; return Math.PI * (a + b) * (1 + 3 * q / (10 + Math.sqrt(4 - 3 * q))); };
  const form = {
    h, S, pose,
    torso: {
      parts: [{ id: "chest", top: rimY, bottom: pitY }, { id: "belly", top: pitY, bottom: waistY }, { id: "hips", top: waistY, bottom: baseY }],
      collar: collarY, bottom: crotchY, half: torsoHalf, flat: torsoClear, circumference: ellipse(tW, tW * torsoFlat),
      // (with the arms: the torso's half-width, or the arms' outer edge where they hang beside it -- what a cloak clears)
      halfArms: (y) => Math.max(torsoHalf(y), (y > armY + rArmU ? 0 : y > armY ? shZ + Math.sqrt(Math.max(0, rArmU * rArmU - (y - armY) ** 2)) : shZ + (armY - y) * abd + armR(armY - y)) + .008 * S),
      hands: handY,
      marks: { collar: collarY, armtop: armY + rArmU, shoulder: rimY, armpit: pitY, chest: pitY - .03 * h, waist: waistY, hip: baseY, crotch: crotchY,
               thigh: (crotchY + kneeY) / 2, knee: kneeY, calf: kneeY - .3 * legLo, ankle: ankY, floor: 0 },
      hangFrom: "pelvis", upperFrom: "chest", hangY: pelY,   // (the chest's frame IS the pelvis's at rest: its origin there too)
    },
    arms: [["L"], ["R"]].map(([t]) => ({ side: t, parts: [{ id: "arm" + t, len: armU }, { id: "fore" + t, len: armF }, { id: "hand" + t, len: handL }],
      marks: { shoulder: 0, biceps: armU * .5, elbow: armU, forearm: armU + armF * .5, wrist: armU + armF, knuckles: armU + armF + handL },
      r: rArmU, radius: armR })),
    legs: [["L"], ["R"]].map(([t]) => ({ side: t, parts: [{ id: "leg" + t, len: legU }, { id: "shin" + t, len: legLo }],
      marks: { hip: 0, thigh: legU * .5, knee: legU, calf: legU + legLo * .3, ankle: legU + legLo, sole: hipY },
      r: rThigh })),
    feet: beast?.hoof ? [] : ["footL", "footR"], neck: { id: "neck", r: neckFoot, top: neckTop, k: Math.max(.03 * S, kT) }, head: { id: "head", hr },
  };
  const worn = tailor(form, o, { add, bone });
  if (worn.armsUnder !== null && worn.armsUnder < armY - armU * .5)   // (cloaked: the upper arms' gestures kept under the cloth -- LOW_ARM)
    for (const [s, tag] of [[1, "L"], [-1, "R"]]) { byId("arm" + tag).anim.work = workOf("arm", s, true); byId("fore" + tag).anim.work = workOf("fore", s, true); }
  // THE NECK'S FIT for what is worn on top (jewelry.js): the outermost surface the body and its clothes make, made when
  // first asked (a person with no necklace never pays for it)
  let fit0 = null;
  const fitNeck = () => fit0 ??= neckFit(form, outerSurface(form, worn));
  for (const [id, layers] of worn.dress) { const p = byId(id); if (p) p.dress = { standing: false, layers }; }
  const skirts = worn.skirts;
  // ---- legs under skirts: what a skirt covers is not drawn at all (the lab
  // kept only the leg below the hem), so a knee swinging forward never pokes
  // through the cloth -- a thigh under a skirt to the knee is cut away
  // entirely, a shin under a long skirt down to its last few centimetres
  const hemY = worn.legsUnder;
  // (seated on the floor every hem is cut at the seat, below: the crossed legs out of it)
  if (hemY !== null && pose !== "floor") for (const [t] of [["L"], ["R"]]) {
    const th = byId("leg" + t), sh = byId("shin" + t);
    // (a BONE: posed, never drawn -- an empty cut, { lo: 1e3, hi: 1e3 }, did not hide it: the shell engine drew it whole, and
    //  a crouch brought it out through the cloth. Only where the hem reaches past the KNEE: hidden from 80% of the thigh
    //  down, a guard's tabard over the mail left the thighs' last hand's breadth missing above the boots -- 2026-10-24)
    if (hemY < hipY - legU - rKnee && pose !== "sit") Object.assign(th, { bone: true, k: 0 });   // (seated, the lap says: below)
    if (hemY < ankY + legLo * .5 && pose !== "sit") Object.assign(sh,   // (seated, the skirt tips forward off the knees: the shins under it show whole)
      { clip: { lo: legLo + ankY - hemY - .03 * S, hi: 1e4, solid: true }, k: 0 });
  }

  // ---- poses
  const sides = [["L", 1], ["R", -1]];
  if (pose === "carry")   // arms round a load held in front of the belly
    for (const [t, s] of sides) {
      Object.assign(byId("arm" + t), { rot: [-s * 12, 0, 32] }); delete byId("arm" + t).anim;
      Object.assign(byId("fore" + t), { rot: [s * 28, 0, 52] }); delete byId("fore" + t).anim;
    }
  // THE PORTERS' WAYS (freight.js, assets/world/goods.json `carry`): the figure's RIGHT is the rig's "L" (s = 1: out to the side is a negative x rotation, forward a positive z);
  // a hand not named keeps its walking swing
  const PORTER = {
    shoulder: { L: [[-25, 0, 55], [0, 0, 95]] },   // a load on the right shoulder, the right hand up before it at the neck
    head: { L: [[-150, 0, 8], [10, 0, 62]] },   // a jar or basket on the head, the right hand up at its side
    pole: { L: [[-10, 0, 42], [0, 0, 62]] },   // a pole on the right shoulder, the right hand on it before him
    back: { L: [[-34, 0, 34], [0, 0, 126]], R: [[34, 0, 34], [0, 0, 126]] },   // a bale high on the back, both hands at the cords at the shoulders
    tumpline: { L: [[-30, 0, 62], [0, 0, 118]], R: [[30, 0, 62], [0, 0, 118]] },   // the strap over the brow, both hands up at it
  }[pose];
  if (PORTER) for (const [t, [a, f]] of Object.entries(PORTER)) {
    Object.assign(byId("arm" + t), { rot: a }); delete byId("arm" + t).anim;
    Object.assign(byId("fore" + t), { rot: f }); delete byId("fore" + t).anim;
  }
  if (pose === "guard") {   // the weapon arm lifted -- the figure's RIGHT, the rig's "L" (its L/R are mirrored: "L" sits at +z) --
    // the upper arm a little forward, the forearm raised about 60 degrees from hanging
    Object.assign(byId("armL"), { rot: [-8, 0, 15] }); delete byId("armL").anim;
    Object.assign(byId("foreL"), { rot: [4, 0, 45] }); delete byId("foreL").anim;
    Object.assign(byId("armR"), { rot: [8, 0, 8] }); delete byId("armR").anim;     // the shield arm: the forearm raised too, the hand at the shield's grip
    Object.assign(byId("foreR"), { rot: [-4, 0, 40] }); delete byId("foreR").anim;
  }
  if (pose === "draw") {   // drawing a bow (the player's own body, archery.js): the bow arm -- the figure's LEFT, the rig's "R" (its L/R are
    // mirrored) -- straight out ahead at shoulder height, the string hand (the right, "L") drawn back to the cheek; the legs still walk
    Object.assign(byId("armR"), { rot: [4, 0, 86] }); delete byId("armR").anim;
    Object.assign(byId("foreR"), { rot: [0, 0, 4] }); delete byId("foreR").anim;
    // (the elbow out and up at the side, the arm turned out in the shoulder, bent all the way: the hand at the cheek -- it
    //  was the elbow bent 125 degrees backwards)
    Object.assign(byId("armL"), { rot: [-110, 0, 35] }); delete byId("armL").anim;
    Object.assign(byId("foreL"), { rot: [0, -50, 145] }); delete byId("foreL").anim;
  }
  if (pose === "sit" || pose === "ride") {
    for (const [t, s] of sides) {
      // NOTE the x-rotation sign: NEGATIVE side swings a hanging capsule
      // toward its own +z side, so the left leg goes left, right goes right
      if (pose === "sit") {
        byId("leg" + t).rot = [-s * 5, 0, 86];                      // thighs FORWARD onto the bench
        byId("shin" + t).rot = [0, 0, -86];                         // shins straight down
        byId("arm" + t).rot = [-s * 4, 0, 14]; byId("fore" + t).rot = [0, 0, 52];   // hands on the thighs
      } else {                                                     // astride: thighs down the mount's flanks, shins back
        byId("leg" + t).rot = [-s * 34, 0, 28];
        byId("leg" + t).pos[2] = s * .12 * S;
        byId("shin" + t).rot = [s * 36, 0, -42];
        byId("arm" + t).rot = [s * 6, 0, 34]; byId("fore" + t).rot = [s * 10, 0, 48];   // hands forward, toward the mount's neck
      }
    }
    // seated: a skirt lies along the thighs as a LAP to the knees -- a short one ends round there; a long one goes on
    // as its FALL (2026-10-29: was the whole skirt tilted forward from the waist, a bell over the knees half again as
    // wide as the lap): a cone of its own hung from the lap's end at the knees straight down in front of the shins to
    // the floor, its hem band and its folds going on from the lap's -- the drape of a seated statue's lap and knees
    // (a SHORT one rides up the thighs, its hem LAP_SHORT of the way to the knees: cut open there, the thighs and the knees
    //  out of it -- it rounded off past the knees, closed, a lens of cloth lying on them like a tray)
    const LAP = 84, LAP_SQUASH = .5, LAP_BACK = .6, LAP_SHORT = .75, FALL_SQUASH = .7, FALL_FLARE = .1, FALL_TUCK = .9;   // (degrees forward from hanging: the thighs' own 86, the lap sloping a little to the knees)
    // (the fall DRAPED over the shins it hangs before -- FALL_CLING of its excess over them taken in, FALL_EASE of the
    //  thigh's radius clear: laid over both shins and narrowing to them, the feet out under its hem -- a drum before them
    //  from the knees to the floor, it stood a column under every seated statue's lap. The shins hang as it does, along
    //  its own axis: no crevice where they meet, as the lap's over the thighs had. The LAP lies on the thighs as well,
    //  LAP_CLING of its excess taken in: left round, it stood a dome over them; between them it sags, shell.js CLING.sag.
    //  The fall is LAID on from its top -- the lap it hangs from among what it is draped over (shell.js: laid) -- so it
    //  rounds over the knees at once: clinging only below its top, its open top stood out round over the clung lap, a
    //  square corner at the knees)
    const FALL_CLING = .7, FALL_EASE = .25, LAP_CLING = .7;
    // (a MANTLE wrapped round the legs too -- the toga, the himation: a piece that says `lap`, reaching below the knees
    //  -- is cut at the seat, and its cloth from the waist down goes on as a skirt of its own, centred on the body and
    //  closed, for the lap and the fall to take: the seated togate figure. A cloak hangs behind as it is.)
    // (and so is a HIGH-WAISTED skirt -- a stola's from under the breast: its lap was hung from there, a slab of cloth
    //  at the belly over a gap where the thighs are; its own cone at the waist, nothing under it to hide but itself)
    const seatedSkirts = [...skirts];
    if (pose === "sit") for (const st of worn.standing) {
      const m = st.part, split = !st.lap && st.skirt && st.top > waistY + .03 * S;
      if (!(st.lap || split) || st.bottom > kneeY) continue;
      const len = m.size.len, cut = Math.min(len, st.top - (hipY - SEAT_CLEAR)), flare = (m.size.r2 - m.size.r) / len;
      const ended = (L) => Math.abs(L.s1 - len) < 1e-6;
      // (its ring at the waist as a skirt's would be: round the torso there and the cloth under it, not the arm the mantle cleared)
      const below = st.top - waistY, sLen = waistY - st.bottom, rW = split ? m.size.r + flare * below : torsoHalf(waistY) + .03 * S;
      const sk = { ...m, id: m.id + "_lap", parent: form.torso.hangFrom, pos: [0, waistY - form.torso.hangY, 0], rot: hangRot([0, -1, 0]),
                   size: { r: rW, r2: rW + flare * sLen, len: sLen }, pivot: [0, -sLen / 2, 0], clip: { ...m.clip, lo: 0, hi: sLen, lid: true }, follow: undefined, trail: 0,
                   dress: { ...m.dress, layers: m.dress.layers.map((L) => ({ ...L, wrap: null, edge: undefined, s0: L.width ? sLen - L.width : -.25, s1: ended(L) ? sLen : L.s1, vOffset: (L.vOffset ?? 0) + below })) } };
      Object.assign(m, { size: { ...m.size, r2: m.size.r + flare * cut, len: cut }, pivot: [0, -cut / 2, 0], clip: { ...m.clip, hi: cut },
                         dress: { ...m.dress, layers: m.dress.layers.filter((L) => !L.width).map((L) => ended(L) ? { ...L, s1: cut } : L) } });
      parts.splice(parts.indexOf(m) + 1, 0, sk);
      // (what is under it -- a tunic's skirt, a chiton's -- is under it everywhere now: a bone, never drawn)
      if (split) { if (seatedSkirts.includes(m)) seatedSkirts.splice(seatedSkirts.indexOf(m), 1, sk); }
      else { for (const u of seatedSkirts.splice(0)) Object.assign(u, { bone: true, k: 0 }); seatedSkirts.push(sk); }
    }
    if (pose === "sit") for (const sk of seatedSkirts) {
      const len = sk.size.len, rT = sk.size.r, rH = sk.size.r2;
      const long = len > legU * 1.2;
      // (a long one's lap ends short of the knees by LAP_BACK of its radius there: its round end, as deep as it is wide,
      //  then rounds just past them)
      const rK = Math.min(rT + (rH - rT) * (legU + rKnee) / len, .2 * S * sx.hips);
      const lap = long ? legU + rKnee - LAP_BACK * rK : Math.min(LAP_SHORT * (legU + rKnee), len);
      // (flattened: a slab over the thighs, as wide as the knees and not as deep -- its oval's depth, turned with it, is now up and down)
      Object.assign(sk, { rot: [0, 0, LAP], size: { r: rT, r2: long ? rK : rT + (rK - rT) * lap / (legU + rKnee), len: lap }, pivot: [0, -lap / 2, 0],
                          clip: { ...sk.clip, lo: 0, hi: long ? 1e4 : lap, lid: true, squash: LAP_SQUASH } });
      const layers = sk.dress.layers;
      if (!long) sk.open = true;   // (its hem on the thighs, the legs out of it: carved, an opening still)
      if (!long) for (const Lr of layers) { if (Lr.width) Lr.s0 = lap - Lr.width; if (Math.abs(Lr.s1 - len) < 1e-6) Lr.s1 = lap; }   // (its hem band and the layers that ended at its hem move with it; an apron keeps its own end)
      else {
        // (hung FORWARD of the lap's end by what its flatter depth lacks: its front under the lap's round end, the cloth
        //  rolling over the knees down into it -- hung at the end itself, that end stood out over it a hand's breadth, a
        //  cushion on the knees; its open top kept a little inside that end, FALL_TUCK, not peeping out under it)
        const at = lap + FALL_TUCK * (1 - FALL_SQUASH) * rK;
        // (the knees' end of the lap, on its axis, down to the seated soles: the fall's length; its cloth as wide as the lap's end, hanging nearly straight)
        const fall = Math.max(.1 * S, pelY + sk.pos[1] - at * Math.cos(LAP * Math.PI / 180) - (hipY - legLo - ankY) - .02 * S);
        const rF = rK + FALL_FLARE * fall;
        const ended = (Lr) => Math.abs(Lr.s1 - len) < 1e-6;
        // (the fall's own s from the knees; the layers that ran to the hem end at its hem, the cloth running on into it unbroken)
        const fallLayers = layers.filter((Lr) => ended(Lr) || Lr.s1 >= 1e2).map((Lr) => ({ ...Lr, s0: Lr.width ? fall - Lr.width : -1e3, s1: ended(Lr) ? fall : Lr.s1, vOffset: (Lr.vOffset ?? 0) + lap }));
        sk.dress = { ...sk.dress, layers: layers.filter((Lr) => !Lr.width).map((Lr) => ended(Lr) ? { ...Lr, s1: 1e3 } : Lr) };
        sk.clip = { ...sk.clip, lid: true };
        sk.cling = { k: LAP_CLING, ease: FALL_EASE * rThigh, over: ["legL", null, "legR", null, null, null, null], seated: true };
        parts.splice(parts.indexOf(sk) + 1, 0, { ...sk, id: sk.id + "_fall", parent: sk.id, pos: [0, -at, 0], rot: [0, 0, -LAP], size: { r: rK, r2: rF, len: fall },
                                                pivot: [0, -fall / 2, 0], clip: { ...sk.clip, lo: 0, hi: fall, lid: false, squash: FALL_SQUASH }, dress: { ...sk.dress, layers: fallLayers },
                                                cling: { k: FALL_CLING, ease: FALL_EASE * rThigh, over: [null, "shinL", null, "shinR", sk.id, null, null], seated: true } });
      }
      if (long) for (const t of ["L", "R"]) { byId("leg" + t).bone = true; byId("leg" + t).k = 0; }   // the skirt hides the thighs (bones: never drawn)
    }
    // (a lap and its fall are hung by the knees themselves: no drape -- shell.js CLING; nor the legs under anything else.
    //  What is draped over the ARMS stays draped over them -- a mantle's cape on the shoulders, its body on the back down
    //  to the seat: undraped, the cape stood a flat millstone and the mantle a bell round the torso. A lap draped over the
    //  thighs came in off its fall at the knees, crevices between them)
    if (pose === "sit") for (const p of parts) {
      if (!p.cling || p.cling.seated) continue;   // (one made for the seated figure: the fall's, over its shins)
      if (p.cling.over.slice(4).some(Boolean) && !seatedSkirts.includes(p) && !seatedSkirts.some((sk) => p.parent === sk.id)) p.cling = { ...p.cling, over: [null, null, null, null, ...p.cling.over.slice(4)] };
      else delete p.cling;
    }
    // the thigh sets how deep a person sits: the hips go where an adult's
    // (40cm thigh) would, pushed forward by what a shorter thigh lacks, so a
    // child sits near the front edge with the knees over it
    if (pose === "sit") byId("pelvis").pos[0] += Math.max(-.03, .4 * S0 - legU);
  }
  // SEATED ON THE FLOOR (2026-10-30: "floor" -- a Buddha cross-legged, statues.js; built standing, its legs crossed by
  // its joints): what hangs from the body below the seat would go down through the floor, so every standing piece on the
  // torso is cut there -- FLOOR_HEM of the thigh's radius under the hip joint: the thighs leave the trunk forward there,
  // and the hem lies along their tops (cut under the crotch, the cling carried it out over the knees a lampshade wider
  // than the figure, the knees through it; the legs' own cloth -- a Buddha's under-robe -- is theirs). Hung its length, a
  // Buddha's robe stood a drum into the pedestal.
  const FLOOR_HEM = .3;
  if (pose === "floor") {
    const seat = hipY - FLOOR_HEM * rThigh;
    for (const st of worn.standing) {
      if (!st.torso || st.bottom >= seat) continue;
      const m = st.part, len = m.size.len;
      if (st.top <= seat) { Object.assign(m, { bone: true, k: 0 }); continue; }
      const cut = len - (seat - st.bottom), ended = (L) => Math.abs(L.s1 - len) < 1e-6;
      Object.assign(m, { size: { ...m.size, r2: m.size.r + (m.size.r2 - m.size.r) * cut / len, len: cut }, pivot: [0, -cut / 2, 0], clip: { ...m.clip, hi: Math.min(m.clip.hi, cut) },
                         dress: { ...m.dress, layers: m.dress.layers.map((L) => L.width && ended(L) ? { ...L, s0: cut - L.width, s1: cut } : ended(L) ? { ...L, s1: cut } : L) } });
      st.bottom = seat;
    }
    // (nor does it drape the legs: they go out from under its hem, flat on the floor -- reached over, it tented out to
    //  the knees; what it lies over on the arms and the chest it keeps, as seated on a bench)
    for (const p of parts) if (p.cling) p.cling = { ...p.cling, over: [null, null, null, null, ...p.cling.over.slice(4)] };
  }
  // reclining: a skirt -- and a mantle wrapped round the legs -- does not stand out from a body lying on its side: its
  // cloth falls in round the legs, the flare taken down to RECLINE_FLARE (a long gown's bell, laid along the floor,
  // was a megaphone wider than the figure was tall) -- and no CASCADE down its opening (shell.js: zigzag teeth hung
  // down the piece, along a body lying on its side they were a torn edge across the hips, shards over the couch)
  const RECLINE_FLARE = .06;
  if (pose === "recline") for (const p of [...skirts, ...worn.standing.filter((st) => st.lap).map((st) => st.part)]) {
    p.size = { ...p.size, r2: Math.min(p.size.r2, p.size.r + RECLINE_FLARE * p.size.len) };
    if (p.dress) p.dress = { ...p.dress, layers: p.dress.layers.map(({ cascade, ...L }) => L) };
  }
  if (pose === "lie") {   // flat on the back along +x, the back on y = 0; feet follow the shins (toes up)
    const root = byId("pelvis");
    root.pos = [pelY, torsoFlat * hW + .02 * S, 0];   // (the back on the ground: half the torso's depth under its axis, and its cloth)
    root.rot = [180, 0, -90];
    for (const p of parts) { delete p.anim; delete p.ik; delete p.level; }
  }
  if (still || pose === "sit" || pose === "ride" || pose === "lie") for (const p of parts) {
    delete p.ik;
    if (pose === "sit" && !still && p.anim?.work) p.anim = { ...p.anim, deg: 0 };   // seated hands still work (a potter, a guest eating): only the gait swing goes
    else delete p.anim;
  }

  // THE MESH HEAD on a list of this person's parts (heads.js finds it by index): the whole person's, or the upper body's
  const hex = (c) => "#" + c.toString(16).padStart(6, "0");
  // (the kind: a child's face for a girl too -- she had a grown woman's; the old their own)
  const faceOf = (list) => meshFace ? { kind: isChild ? "child" : old ? (female ? "old-woman" : "elder") : female ? "woman" : "man", seed, skin: hex(skin), hair: hex(hairC), hr, style: meshHair, fringe: o.fringe && !hatOn ? 1 : 0,   // (no fringe under a hat: the flat hair's forelock came through a coif, a bonnet, a hood's cowl -- clipcheck)
                                        headwear: hatOn ? null : o.jewelry?.head ?? null, ears: o.jewelry?.ears ?? null, ...(o.beard ? { beard: o.beard } : {}), ...(full ? { full } : {}),   // (full: the face's fullness by the body's fat -- heads.js)
                                        head: list.findIndex((p) => p.id === "head"), gaze: list.findIndex((p) => p.id === "nose") } : null;
  // what hangs round the neck (jewels.js): the items, the fit they lie on, the parts that carry it (the chest, and the
  // root whose axis is the figure's forward -- the frame the torso is drawn in)
  const neckHidden = o.wear.some((w) => (JEWEL_WEAR.hidesNeck ?? []).includes(w.garment));   // (a hood's cape over it)
  const jewelOf = (list) => o.jewelry?.neck?.length && !beast && !neckHidden ? { pieces: o.jewelry.neck.map((path, k) => ({ path, seed: seed + k })), fit: fitNeck(),
                                         chest: list.findIndex((p) => p.id === "chest"), root: list.findIndex((p) => p.id === "pelvis") } : null;
  if (upper) {   // (a centaur's man: his upper body -- and his head, the mesh face, or he had none)
    const lower = /^(leg|shin|foot)[LR]$|^tail/, hung = new Set(skirts.map((p) => p.id));
    const kept = parts.filter((p) => !lower.test(p.id) && !hung.has(p.id));
    return { name: "person", kind, parts: kept, pelvisY: pelY, outfit: o, face: faceOf(kept), jewelry: jewelOf(kept), fitNeck };
  }

  // ---- the biped walk and run: legs in antiphase; the hips drop at double support (bob phase)
  const L = legU + legLo;
  const moving = parts.some((p) => p.ik);
  const sk = hemY !== null && hemY < hipY;   // a skirt keeps the stride short (the lab: 60%)
  // ...and never wider than its hem: the cloth does not move with the legs, so a foot swung further than the skirt's
  // lowest edge reaches -- front to back, where it is squashed -- shows outside it with nothing above it (a child
  // running in a gown). The longest skirt's hem, less half a foot.
  const hem = sk ? Math.min(...skirts.filter((q) => q.size?.r2).map((q) => q.size.r2 * (q.clip?.squash ?? 1))) : Infinity;
  // (only where the skirt hides the thighs -- below them a leg swung out shows coming OUT of the hem; a tunic above the
  //  knee leaves the legs free, and its wearer strides as wide as anyone)
  const covers = sk && hemY < hipY - legU * .8;
  const footHalf = (byId("footL")?.size?.len ?? .14 * S) / 2, cap = (st) => covers && Number.isFinite(hem) ? Math.min(st, Math.max(.1 * L, hem - footHalf)) : st;
  const gaits = moving ? {
    walk: { offsets: [0, Math.PI, 0, 0], stride: cap((sk ? .24 : .34) * L), lift: (sk ? .09 : .14) * L, bob: .03 * L, bobPh: Math.PI / 2 },
    run: { offsets: [0, Math.PI, 0, 0], stride: cap(.58 * L), lift: (sk ? .2 : .4) * L, bob: .05 * L, bobPh: Math.PI / 2 },
  } : null;
  // Where the figure's origin goes -- ONE rule for every caller (pews, the
  // cart box, the boat's thwart, a seated player's avatar and copies):
  // sitAt(seatTop) puts the hip joint SEAT_CLEAR above the seat, with hipY
  // reported so the LOWEST seated point (pelvis, hips or thighs, whichever
  // hangs furthest below the joint) rests just on the board; rideAt(backTop)
  // puts the hips on a mount's back (in the mount's frame).
  const drop = Math.max(hipY - crotchY, rThigh) + .012 + .004 * S;
  const hipOut = pose === "sit" ? hipY - (drop - SEAT_CLEAR) : hipY;
  const face = faceOf(parts);
  return { name: "person", kind, parts, expr: pose === "lie" ? expression("asleep") : null, hipY: hipOut,   // expr: the face they rest in (faces.js)
           forwardFrom: "chest",   // (the trunk's frame turns the figure's forward: skeleton.js -- a twist at the waist turns the flat torso)
           idleSway: !o.still && (!pose || pose === "stand" || pose === "carry") ? IDLE_SWAY : 0,   // (standing about, the weight shifts: skeleton.js)
           face,   // the mesh head to stand on the head part (heads.js), or none
           jewelry: jewelOf(parts), fitNeck,   // what hangs round the neck (jewels.js), and the fit it lies on
           eyeAt: [.01 * S + .9 * hr, headY + .16 * hr],   // where the eyes are, standing: forward of the feet and up (a player's own body: index.html updateSelf)
           sitAt: (top) => top + SEAT_CLEAR - hipOut, rideAt: (back) => back - hipOut,
           gaits, crouch: CROUCH, legLen: L, probe: .25, outfit: o, build: { h, fat, frame, pot, full, abduction },   // (build: how this one was drawn -- body.json build.variety)
           // what the JOINTS need (joints.js): the head turns about the top of the neck, not the skull's centre (in the
           // head's frame); the skirts, which hang from the hips and drape over the thighs as they rise
           motion: { pivots: { neck: [-.01 * S, neckTop - headY, 0] }, skirts: pose === "sit" ? [] : skirts.map((p) => p.id), handLen: handL } };   // (seated, a skirt is already a lap and its fall: no thigh drapes it again -- joints.js)
}

// the CANON NECK (a woman's, bare): what a necklace lies on when it is seen without a body (jewelry.js)
setCanonNeck(() => makePerson({ kind: "woman", seed: 3, still: true, outfit: { bare: true, jewelry: { neck: [], head: null, ears: null } } }).fitNeck());
