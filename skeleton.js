// The CPU skeleton: species part-list -> flat compiled rig -> world-space
// segment endpoints per frame. Shared by the instanced banner engine
// (instanced.js, one quad per part) and the composite engine (composite.js,
// one quad per animal); both consume the same Float32Arrays of A/B/C
// endpoints, so the pose math lives here exactly once.
//
// Besides the per-part `anim` swing (a sine about one axis on the gait,
// wing or movement clock) this walks the mammal rig's legs: a leg is two
// capsules (upper, lower) whose knee comes from two-bone IK every frame --
// the foot follows a gait (stride forward/back, lift on the swing half of
// the cycle), the knee lands where the two bone lengths meet, so the leg
// straightens when the foot is far from the hip and folds when it is
// lifted. Walk and run are two parameter sets per species (`def.gaits`),
// blended by the animal's `run` factor; `amp` fades the whole stride out
// when an animal stands, so a stopped animal settles on straight legs.
import * as THREE from "three";
import { segmentFor } from "./banner.js";

const PAT = { leaf: 1, bark: 2, stripes: 3, bands: 4, spots: 5, wingspots: 6, scutes: 7, diamond: 8, scales: 17, rosettes: 18, twist: 19, barkH: 20, patches: 21, piebald: 22,   // (17: after the cloth ids)
              // strands (people.js): two colours down a plait or a fall of hair (9-14 were cloth, now clothes.js's fabrics)
              braid: 15, hair: 16 };
export const CYCLES = .8;   // gait cycles per unit of the gait clock (the trot's rate; wanderers scale the clock by travel speed over leg length)

// species def -> flat skeleton: parents come before children in the data,
// so a single forward pass can chain world matrices. Everything static is
// precomputed here: segment endpoints in group-local space (pivot + the
// inverse-scale trick from banner.js baked in) and radii with the ancestor
// mean-scale factor already applied, since the shader never sees matrices.
const compiledCache = new Map();
const nodPivot = (def, part) => {
  const neck = def.parts.find((q) => q.id === "neck");
  if (!neck) return part.id === "head" && def.nodPivot ? new THREE.Vector3(...def.nodPivot) : null;   // (no neck -- a hen: the head dips about the point its definition gives)
  if (part !== neck && !((part.id === "head" || part.nod) && part.parent === neck.parent)) return null;   // (part.nod: a mane along the neck)
  return new THREE.Vector3(...(neck.pos ?? [0, 0, 0]));
};
const PUPILS = { round: 0, bar: 1, slit: 2 };   // a face mark's pupil (composite FACE MARKS)
export function compileDef(def) {
  if (compiledCache.has(def)) return compiledCache.get(def);
  const index = new Map(), drapes = new Set(def.motion?.skirts ?? []);
  const lastLeg = def.parts.reduce((m, q, i) => (q.ik && !q.ik.follow ? i : m), -1);
  const parts = def.parts.map((part, i) => {
    index.set(part.id, i);
    const seg = segmentFor(part);
    const s = part.scale ?? [1, 1, 1];
    const pivot = part.pivot ?? [0, 0, 0];
    const pA = new THREE.Vector3(...seg.a.map((v, k) => pivot[k] + v / s[k]));
    const pB = new THREE.Vector3(...seg.b.map((v, k) => pivot[k] + v / s[k]));
    const pC = seg.c ? new THREE.Vector3(...seg.c.map((v, k) => pivot[k] + v / s[k])) : pB;   // triangle's third corner (unused otherwise)
    let f = 1;   // ancestor mean-scale factor (the part's own scale is baked in by segmentFor)
    for (let pid = part.parent; pid; ) {
      const anc = def.parts[index.get(pid)];
      if (anc.scale) f *= (anc.scale[0] + anc.scale[1] + anc.scale[2]) / 3;
      pid = anc.parent;
    }
    return {
      parentIdx: part.parent ? index.get(part.parent) : -1,
      pos: part.pos ?? [0, 0, 0],
      baseRot: (part.rot ?? [0, 0, 0]).map((d) => d * Math.PI / 180),
      scale: part.scale ?? null,
      anim: part.anim ?? null,
      // struck down (combat.js): `fold` (degrees, added to the rotation) draws a part in -- a spider's legs curled under it; a wing
      // (anim.wing) without one folds back flat against the flank, its flap stilled (side: which way the wing reaches, +z or -z)
      fold: part.fold ? part.fold.map((d) => d * Math.PI / 180) : null,
      side: Math.sign(((seg.b?.[2] ?? 0) + (seg.c?.[2] ?? 0)) || (part.pos?.[2] ?? 0)) || 1,
      ik: part.ik ?? null,        // mammal rig leg: { leg, upper, lower, side, foot, phase } on the upper bone, { leg, follow: true } on the lower
      bob: !!part.bob,            // the body: rides the gait's vertical bob
      spine: !!part.spine,        // a torso cut (mammals.js): these sweep as ONE lathe, whatever their shading
      // body motion (head turns, tail swishes, neck sway) follows MOVEMENT in
      // general -- the gait clock, or a mount's own movement clock while it
      // flies with its legs hanging still. Swimmers and fliers keep
      // everything on the gait clock: their tails and wings ARE the locomotion
      idle: !def.fly && /^(head|neck|tail|ear|mane|trunk|snout|hair)/.test(part.id.replace(/^(r_|L_|R_)/, "")),
      look: part.id === "head" ? .6 : part.id === "neck" ? .4 : 0,   // its share of an.look (the head turned to look at something)
      // an.nod: the head lowered (- down) on its neck -- a grazer cropping the grass. The neck turns about its root, and
      // a head hung beside it on the body (a mammal's) swings about that same root with it: the pivot, in the parent's frame
      nod: nodPivot(def, part),
      pA, pB, pC, r1: seg.r1 * f,
      // r2 = -1 stays the exact triangle flag; a tube packs its end radius and bulge (banner.js tubeUnpack)
      r2: seg.tube ? -2 - (Math.round(seg.r2 * f * 1000) + 4096 * Math.round(seg.bulge * f * 1000)) : seg.r2 < 0 ? -1 : seg.r2 * f,
      pat: PAT[part.pat] ?? 0,
      // bone: posed like any part (what hangs on it, ends() for what rides on it) but never drawn -- a blend
      // radius of -1 marks it and the composite shaders skip it; dot (-2): no SDF either -- a FACE MARK the
      // composite paints onto its parent's surface (eyes, a mouth): { iris, pupil: round|bar|slit, round }
      fur: !!part.fur,          // composite: a strand texture laid over its colour or pattern (mammals' coats)
      fleece: !!part.fleece,    // composite: its surface heaped in lumps (a sheep's wool: shell.js FLEECE)
      stone: part.stone ?? 0,   // composite: carved -- a statue's material (1 marble, 2 bronze, 3 gold, 4 limestone): shell.js stoneAt
      flat: part.flat ?? 0,     // composite: a capsule squashed along the figure's forward to this share of its width (a flat torso)
      // ...and its two end caps, as tall as `a` (the A end) and `b` of their radius and as square as the superellipse
      // exponent `p` (2: an ellipse; a person's shoulders are a low, squared cap) -- a flat part's only
      caps: part.caps ?? null,
      // clothes.js: what the part WEARS -- a stack of layers of sheet, outermost first ({ standing, layers }), each drawn
      // by the shell engine from the static texels composite.js writes for it (see packDress there)
      dress: part.dress ?? null,
      dot: part.dot ? { iris: part.dot.iris !== undefined ? new THREE.Color(part.dot.iris) : null, pupil: PUPILS[part.dot.pupil ?? "round"], round: !!part.dot.round,
                         role: part.dot.role ?? null, side: part.dot.side ?? 0,   // role (eye, brow, mouth) and side (+-1): what an expression does to it (faces.js)
                         // relief: the shape the mark lends the face in the LIGHT alone (composite gRelief) -- 1 a ridge
                         // (a brow over the forehead); an eye's own socket and eyeball come with its iris. reach: how
                         // far out that relief carries, in the mark's own radii, so the cells list it that far
                         relief: part.dot.relief ?? 0, reach: part.dot.reach ?? 1 } : null,
      k: part.bone ? -1 : part.dot ? -2 : (part.k ?? 0) * f,       // composite engine: smooth-union radius into the animal's silhouette (0 = hard union)
      edge: part.edge ?? 1,       // composite engine: 1 = draws its own border band (classic parts), 0 = only the outer outline (rig parts)
      body: part.frame === "body" ? 1 : 0,   // composite engine: pattern in the ANIMAL's frame (torso pieces: stripes run on across seams) instead of the part's
      level: !!part.level,        // keeps the root's orientation whatever its parents do (a foot stays flat on the ground)
      sag: part.sag ?? 0,         // a hanging sleeve's cone: its axis tipped toward the plumb line by up to this (radians), see writeAnimal
      fall: !!part.fall,          // ...and on an arm raised past level it falls to hang plumb from its top (SLIDE.fall)
      drape: drapes.has(part.id) && i > lastLeg,
      trail: part.trail ?? 0,     // a cloak's hem swept back by this at a run (radians; TRAIL), see writeAnimal   // a skirt: carried forward by the thighs under it (DRAPE; the legs are posed before it)
      // a cloak's front panel lifted by the arm under it (LIFT): that arm's index (posed before it), the share of its swing
      follow: part.follow && index.has(part.follow.part) ? index.get(part.follow.part) : -1, followK: part.follow?.k ?? 0,
      // a HINGE (a forearm at the elbow): it only bends, within `bend` [min, max] degrees, in a plane the upper arm's own turn
      // can put it in -- `turn` [min, max] degrees about the arm's length (the shoulder's rotation) -- see writeAnimal
      hinge: part.hinge ? { bend: part.hinge.bend.map((d) => d * Math.PI / 180), turn: part.hinge.turn.map((d) => d * Math.PI / 180) } : null,
      color: new THREE.Color(part.color),
      // composite engine, people's clothing (see people.js): a clip slab
      // along the segment [lo, hi] metres from A, mode 1 = open shell, 2 = solid
      // with flat caps, 3 = a garment's shell whose near cut is always closed (a skirt's waistband); `squash`:
      // the shell flattened front to back to that share of its width (a skirt round a flattened torso); `back` (shells): also cut away everything more than
      // that many metres in FRONT of A along the animal's forward direction
      // (its root segment) -- a fall of hair open where the face is. Packed
      // into one float: mode + 4 * (the offset in mm + 501), 0 when unused.
      // Then a second colour, pattern scale and cloth flags; seams
      clip: part.clip ? [part.clip.lo ?? -1e4, part.clip.hi ?? 1e4,
                         (part.clip.lid ? 3 : part.clip.solid ? 2 : 1) + (part.clip.back !== undefined ? 4 * (Math.round((part.clip.back + .5) * 1000) + 1) : 0),
                         part.clip.squash ?? 0] : null,
      color2: new THREE.Color(part.color2 ?? part.color),
      cloth: part.cloth ?? null,  // { scale }: a strand pattern's (hair, a braid) -- what people wear is `dress`
      seam: part.seam ? 1 : 0,    // composite engine: a dark line where this part meets another colour
      // shell engine: a limb's ROOT -- its top skinned to the body it hangs from: its cap and its first `root` metres keep
      // the bind pose's direction (the body's), the rest of it bends away from there (shell.js "A LIMB'S ROOT")
      root: part.root ?? 0,
    };
  });
  // THE BIND POSE: every part's axis at rest -- its own rotation and its parents', no motion, no gesture -- in the root's
  // frame (composite.js restAxes: the cloth's frame and a limb root's rest are measured from it)
  const bind = [];
  for (const p of parts) {
    const m = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(...p.baseRot));
    if (p.scale) m.scale(new THREE.Vector3(...p.scale));
    if (p.parentIdx >= 0) m.premultiply(bind[p.parentIdx]);
    bind.push(m);
    const d = p.pB.clone().sub(p.pA);
    p.bindDir = d.lengthSq() > 1e-12 ? d.transformDirection(m).toArray() : null;
  }
  parts.gaits = def.gaits ?? null;
  parts.crouch = def.crouch ?? null;   // (a gesture done down low: its share of the legs' length -- people.js CROUCH)
  parts.walkNod = (def.walkNod ?? 0) * Math.PI / 180;   // (the head's nod with each step: mammals.js walkNod, degrees)
  parts.idleSway = parts.some((p) => p.stone) ? 0 : def.idleSway ?? 0;   // (a figure standing about: its weight shifting -- people.js IDLE_SWAY; never a statue)
  parts.legLen = Math.max(0, ...parts.filter((p) => p.ik?.foot != null).map((p) => p.pos[1] - p.ik.foot));
  parts.trails = parts.some((p) => p.trail);   // (a cloak that trails: writeAnimal keeps its spring -- TRAIL)
  parts.follows = parts.some((p, i) => p.follow >= 0 && p.follow < i);   // (a panel lifted by its arm, posed after it -- LIFT)
  for (const [i, p] of parts.entries()) if (p.follow >= i) p.follow = -1;
  // the root's drawn axis is the figure's FORWARD (a flat torso is squashed along it, the cloth and the jewels take
  // their frame from it); `forwardFrom` names the part whose frame turns it instead -- a person's chest, so a trunk
  // turned at the waist faces where it turns (that frame is the root's own at rest)
  parts.forwardFrom = def.forwardFrom ? index.get(def.forwardFrom) ?? -1 : -1;
  compiledCache.set(def, parts);
  return parts;
}

// Two-bone IK for one leg, in the body's xy plane with the hip at the
// origin. Returns [upper, lower] z rotations (positive = swings the foot
// forward, the convention of a capsule hanging from its pivot).
//   ik: { upper, lower, side (+1 knee bends forward, -1 backward), foot (foot joint y below the body origin) }
//   g: { stride, lift }  ph: this leg's phase  amp: stride amplitude 0..1  bob: the body's current bob
//   hipY: the hip's y in body space
export function legPose(ik, g, ph, amp, bob, hipY) {
  const stride = g.stride * amp, lift = Math.max(0, Math.cos(ph)) * g.lift * amp;
  let dx = stride * Math.sin(ph), dy = ik.foot - hipY + lift - bob;
  let d = Math.hypot(dx, dy);
  const upper = ik.upper, lower = ik.lower, reach = upper + lower - .005, fold = Math.abs(upper - lower) + .02;
  if (d > reach) { dx *= reach / d; dy *= reach / d; d = reach; }
  if (d < fold) { dx *= fold / Math.max(d, 1e-4); dy = d < 1e-4 ? -fold : dy * fold / d; d = fold; }   // (folded as tight as the leg goes: lying down, an.rest)
  if (d < 1e-6) return [0, 0];
  const a = (upper * upper - lower * lower + d * d) / (2 * d), h = Math.sqrt(Math.max(upper * upper - a * a, 0));
  const ux = dx / d, uy = dy / d;
  const kx = ux * a - uy * h * ik.side, ky = uy * a + ux * h * ik.side;
  const t1 = Math.atan2(kx, -ky);
  const t2 = Math.atan2(dx - kx, -(dy - ky)) - t1;
  return [t1, t2];
}

// the gait parameter set for a run factor 0..1: walk, run, or a blend
const _g = { offsets: [0, 0, 0, 0], stride: 0, lift: 0, bob: 0, bobPh: undefined };
export function gaitFor(gaits, run) {
  if (!gaits) return null;
  const w = gaits.walk, r = gaits.run ?? w;
  if (run <= 0) return w;
  if (run >= 1) return r;
  for (let i = 0; i < 4; i++) _g.offsets[i] = w.offsets[i] + (r.offsets[i] - w.offsets[i]) * run;
  _g.stride = w.stride + (r.stride - w.stride) * run;
  _g.lift = w.lift + (r.lift - w.lift) * run;
  _g.bob = w.bob + (r.bob - w.bob) * run;
  _g.bobPh = w.bobPh;
  return _g;
}

const _mats = [];
const _root = new THREE.Matrix4();
const _pitch = new THREE.Matrix4(), _roll = new THREE.Matrix4();
const _local = new THREE.Matrix4(), _nod = new THREE.Matrix4(), _nodT = new THREE.Matrix4();
const _e = new THREE.Euler();
const _gq = new THREE.Quaternion(), _gl = new THREE.Quaternion(), _gs = new THREE.Vector3(), _gp = new THREE.Vector3(), _gm = new THREE.Matrix4();
const _v = new THREE.Vector3();
const _lower = [];   // per part: the lower bone's angle computed with its upper bone
let _swing = new Float32Array(64);   // per part: its swing forward this pose (rz in its parent) -- LIFT

// One animal's pose: walks the compiled skeleton, writes world-space
// endpoints at rows an.base.. of fA/fB/fC.
//   an.animT: gait clock   an.wingT: wing clock   (head, neck, tail, ears, mane: the world clock t)
//   an.amp: stride amplitude (1 = full gait, 0 = standing)   an.run: 0 walk .. 1 run
//   an.gesture / an.work: which working swing (anim.work[gesture]) and how strongly
//   an.hidden: parked out of sight -- posed once when hidden, then skipped until shown again
//   an.look: the head turned toward something (radians about the vertical)
//   an.nod: the head lowered on its neck (radians, - down; eased toward an.nodT by easeGait); an.peck: a pecking bird's dip
//   an.rest: lying down -- the body lowered so many metres, the legs folding under it (eased toward an.restT by easeGait)
//   an.pose: a POSITION held by its joints (joints.js): per part index null, or { q, c } -- the part's rotation in its
//     parent (a THREE.Quaternion) in place of its own, its swing and its leg IK, turned about the point c of its
//     frame (null: its origin, the joint); a posed foot is not kept level
// A SKIRT OVER RISING THIGHS: hung from the hips, it is carried forward by the thighs under it -- this share of their
// mean swing forward, up to `max` degrees (a crouch, a stoop; a stride's thighs go both ways and leave it hanging).
// writeAnimal for the gait and the gestures' crouch, joints.js setAngles for a held position.
export const DRAPE = { k: .55, max: 70 };
// a hanging sleeve on a raised arm: from how far up (the arm's rise over its length) it no longer stands round the arm
// but hangs plumb from its top -- see writeAnimal. (It used to be shortened instead, to .35 of itself straight up, so its
// mouth would not stand as a disc round the hand: a funnel all the same, and now it falls.)
export const SLIDE = { fall: .35 };
// A CLOAK'S FRONT LIFTED BY THE ARM: the panel either side of a cloak's opening (clothes.js: a piece's `follow`) swings
// forward with the arm under it -- its share of the arm's swing forward in the chest, beyond `from` degrees (an arm
// hanging, a walk's swing, leave it hanging), up to `max` -- so a raised hand lifts the cloth's edge, not comes through it
export const LIFT = { from: 8, max: 45 };
// TRAILING CLOTH: a cloak's hem swept back as its wearer goes -- the piece's own `trail` (clothes.js: degrees at a run),
// `walk` of it at a walk -- following the stride on a damped spring (`w` rad/s, `zeta`: it swings on past when they
// stop); and turned behind the body as it turns, its heading lagging the body's (`turn` /s), twisted by that lag times
// `twist`, at most `maxTwist` radians. Per figure, on the clock writeAnimal is given (display only).
export const TRAIL = { walk: .35, w: 6, zeta: .45, turn: 4, twist: .6, maxTwist: .5 };
export function writeAnimal(an, t, fA, fB, fC) {
  if (an.stillT !== undefined) t = an.stillT;   // (a figure struck down, combat.js: its world clock stopped -- no idle motion)
  if (an.hidden && an._parked) return;   // (its parts already lie parked from the frame it was hidden)
  an._parked = !!an.hidden;
  const tt = an.animT !== undefined ? an.animT : t;   // per-animal gait clock (stops when standing)
  const tw = an.wingT !== undefined ? an.wingT : tt;   // wing clock (a flying mount beats wings, not legs)
  const parts = an.parts, g = gaitFor(parts.gaits, an.run ?? 0), amp = an.amp ?? 1;
  // the gait clock counts distance (animT = metres / the walk's stride base);
  // a run covers more ground per stride, so its cycles stretch by the stride
  // ratio -- feet stay planted instead of pedalling at a walker's speed
  let tg = tt;
  if (g) {
    const gs = parts.gaits, stretch = 1 + (an.run ?? 0) * ((gs.run ?? gs.walk).stride / gs.walk.stride - 1);
    tg = an._tg = an._tt === undefined ? tt : an._tg + (tt - an._tt) / stretch;
    an._tt = tt;
  }
  // head, neck, tail, ears, mane (the `idle` parts): the WORLD clock, for every animal in every state --
  // walking, running, flying -- they look about and swish at one calm pace whatever the legs do
  const tm = t;
  // the head's nod: lowered to graze (an.nod), and -- a pecking bird (an.peck: the dip's angle) -- quick sharp dips to the
  // ground every second or so, each bird on its own beat: the body tipping forward over its feet, the head with it
  const dip = an.peck ? an.peck * Math.pow(Math.max(0, Math.sin(t * 4.3 + (an.idx ?? 0) * 1.7)), 8) : 0;
  let nodNow = (an.nod ?? 0) - dip * .5; const rest = (an.rest ?? 0) + (an.work && parts.crouch?.[an.gesture] ? parts.crouch[an.gesture] * an.work * parts.legLen : 0);
  const phase = tg * CYCLES * Math.PI * 2;
  // A WALKER'S HEAD NODS with each step (parts.walkNod: a horse's, a cow's -- twice a stride, down as a forefoot lands),
  // fading with the stride as the walker stops and halving at a run
  const stepNod = parts.walkNod && g ? parts.walkNod * amp * (1 - .5 * (an.run ?? 0)) * Math.sin(phase * 2 + (g.offsets?.[0] ?? 0) * 2 + .6) : 0;
  nodNow += stepNod;
  const bob = g ? g.bob * amp * Math.sin(phase * 2 + (g.bobPh ?? .5)) : 0;
  _root.makeRotationY(an.rotY);
  if (an.pitch || dip) _root.multiply(_pitch.makeRotationZ((an.pitch ?? 0) - dip * .5));   // an.pitch: the body tipped about its own left axis (+ nose up) -- a squirrel on a trunk
  if (an.roll) _root.multiply(_roll.makeRotationX(an.roll));
  // STANDING ABOUT: the weight shifting -- a slow rock to the side and a slower one to and fro, each figure on its own
  // beat, fading as the stride comes in (a walker's sway is its gait's)
  if (parts.idleSway && !an.down) {
    const k = parts.idleSway * Math.max(0, 1 - amp * 1.5), ph = (an.idx ?? 0) * 2.17;
    if (k > 1e-4) _root.multiply(_roll.makeRotationX(k * Math.sin(t * .55 + ph))).multiply(_pitch.makeRotationZ(k * .45 * Math.sin(t * .37 + ph * 1.3)));
  }   // an.roll: turned about its own forward axis (+ toward its +z) -- a figure struck down lying on its side (combat.js)
  _root.setPosition(an.position.x, an.position.y - rest, an.position.z);   // (an.rest: lying down, the body this much lower)
  let thighs = 0, nThighs = 0;   // (the legs' swing forward, summed: a skirt over them follows -- DRAPE)
  const swing = parts.follows ? (_swing.length < parts.length ? (_swing = new Float32Array(parts.length * 2)) : _swing) : null;   // (each part's forward swing: a panel follows its arm's -- LIFT)
  let trailK = 0, twist = 0;
  if (parts.trails) {   // (the cloak's spring and its lag: TRAIL)
    const want = amp * (TRAIL.walk + (1 - TRAIL.walk) * (an.run ?? 0));
    const c = an._cloth ??= { k: want, v: 0, yaw: an.rotY, t }, dt = Math.min(.1, Math.max(0, t - c.t));
    c.t = t;
    c.v += (TRAIL.w * TRAIL.w * (want - c.k) - 2 * TRAIL.zeta * TRAIL.w * c.v) * dt; c.k += c.v * dt;
    const lag = ((c.yaw - an.rotY + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
    c.yaw = an.rotY + lag * Math.exp(-TRAIL.turn * dt);
    trailK = c.k; twist = Math.max(-TRAIL.maxTwist, Math.min(TRAIL.maxTwist, lag * TRAIL.twist));
  }
  if (an.hidden) _root.setPosition(an.position.x, -100, an.position.z);   // parked out of sight, position untouched
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    let [rx, ry, rz] = p.baseRot;
    if (an.down) {   // struck down: a part's fold, or a wing folded back and laid flat against the flank (Euler XYZ: the sweep back
      // about y, then turned down about x -- the span along the side, the wing's flat facing out; on its side, it lies over the body)
      if (p.fold) { rx += p.fold[0]; ry += p.fold[1]; rz += p.fold[2]; }
      else if (p.anim?.wing) { ry -= p.side * 1.4; rx += p.side * 1.5; }
    }
    // an.look: the head turned to look at something (radians about the vertical, + to its left), shared between the
    // neck (two fifths) and the head (the rest) -- a villager looking at you as it greets you (index.html greetTick)
    if (an.look && p.look) ry += an.look * p.look;
    if (p.anim) {
      const a = p.anim;
      // a.amp: the swing belongs to the gait (a person's arms, a skirt) and fades with the stride when standing
      // (the idle parts each animal on its own beat -- a herd does not look about in step -- and a.flick: that power of
      //  the sine's crest only, a quick twitch now and then -- an ear)
      const ph = (a.wing ? tw : p.idle ? tm : a.amp ? tg : tt) * a.speed * Math.PI * 2 + (a.phase || 0) + (p.idle ? (an.idx ?? 0) * 2.39 : 0);
      const d = an.down && a.wing ? 0 : (a.deg * Math.PI / 180) * (a.flick ? Math.pow(Math.max(0, Math.sin(ph)), a.flick) : Math.sin(ph)) * (a.amp ? amp : 1);
      if (a.axis === "x") rx += d; else if (a.axis === "y") ry += d; else rz += d;
      // a.sway: side to side (about x) once a stride, with the legs -- a skirt swinging as the hips carry it from one
      // foot to the other (degrees; fades with the stride as the swing does)
      if (a.sway) rx += a.sway * Math.PI / 180 * Math.sin(phase + 1.2) * amp;
      // a.work[an.gesture]: a working swing on the world clock (people.js GESTURES: digging, mowing,
      // hammering...), strength an.work (0 = idle), on its own axis -- bias holds, deg swings about it
      const g = an.work && a.work ? a.work[an.gesture] : null;
      if (g) {
        const w = (g.bias + g.deg * Math.sin(t * g.speed * Math.PI * 2 + (g.phase || 0))) * Math.PI / 180 * an.work;
        if (g.axis === "x") rx += w; else if (g.axis === "y") ry += w; else rz += w;
        if (g.twist) ry += g.twist * Math.PI / 180 * an.work;   // (a forearm's: the upper arm turned about its length -- a HINGE's turn)
      }
    }
    if (p.ik && g) {
      if (p.ik.follow) rz += _lower[p.parentIdx] ?? 0;
      else {
        const [t1, t2] = legPose(p.ik, g, phase + g.offsets[p.ik.leg] + (p.ik.phase || 0), amp, bob, p.pos[1] - rest);   // (resting: the feet aimed as much higher as the body lies lower -- the legs fold under it)
        rz += t1; _lower[i] = t2; thighs += t1; nThighs++;
      }
    }
    if (p.drape && nThighs) rz += Math.min(DRAPE.max * Math.PI / 180, DRAPE.k * Math.max(0, thighs / nThighs));
    if (p.trail) { rz -= p.trail * trailK; ry += twist; }
    // A HINGE bends one way only. Whatever the pose and the gestures added up to, the part is aimed the same way by a bend
    // in its hinge's plane turned about the upper arm (a forearm swung out sideways is the arm turned in the shoulder, the
    // elbow bent) -- but never by more turn than the shoulder has, nor bent back past straight: such an aim is pulled to
    // the nearest one the joint can take (bent backwards, it goes straight)
    if (p.hinge && !an.pose?.[i]) {
      const sx = Math.sin(rx), cx = Math.cos(rx), sy = Math.sin(ry), cy = Math.cos(ry), sz = Math.sin(rz), cz = Math.cos(rz);
      const dx = sz * cy, dy = -cz * cx + sz * sy * sx, dz = -cz * sx - sz * sy * cx;   // (the part's length, -y, turned)
      const bend = Math.acos(Math.max(-1, Math.min(1, -dy))), turn = bend > 1e-4 ? Math.atan2(-dz, dx) : 0;
      const [t0, t1] = p.hinge.turn, tc = Math.max(t0, Math.min(t1, turn)), [b0, b1] = p.hinge.bend;
      rx = 0; ry = tc; rz = Math.max(b0, Math.min(b1, bend * Math.max(0, Math.cos(turn - tc))));
    }
    if (swing) swing[i] = an.pose?.[i] ? 0 : rz;
    if (p.follow >= 0) rz += p.followK * Math.min(LIFT.max * Math.PI / 180, Math.max(0, swing[p.follow] - LIFT.from * Math.PI / 180));
    // the body rides the stride's bob; the idle parts hung on it (neck, head, tail) cancel it -- they
    // stay as steady running as they do walking or flying
    const dy = (p.bob ? bob : 0) - (p.idle && p.parentIdx >= 0 && parts[p.parentIdx].bob ? bob : 0);
    const held = an.pose?.[i];
    if (held) {   // held by its joint: that rotation, about the joint's pivot
      _local.makeRotationFromQuaternion(held.q);
      if (held.c) { _v.copy(held.c).applyQuaternion(held.q); _local.setPosition(p.pos[0] + held.c.x - _v.x, p.pos[1] + dy + held.c.y - _v.y, p.pos[2] + held.c.z - _v.z); }
      else _local.setPosition(p.pos[0], p.pos[1] + dy, p.pos[2]);
      if (p.scale) _local.scale(_v.set(p.scale[0], p.scale[1], p.scale[2]));
    } else if (!p.anim && !(p.ik && g) && !(an.down && p.fold) && !(p.drape && nThighs) && !p.trail && p.follow < 0) {   // a part that never moves in its parent: its local transform built once, cached (only the bob added)
      _local.copy(p._lm ?? (p._lm = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(rx, ry, rz)).setPosition(p.pos[0], p.pos[1], p.pos[2])
        .scale(new THREE.Vector3(...(p.scale ?? [1, 1, 1])))));
      _local.elements[13] += dy;
    } else {
      _local.makeRotationFromEuler(_e.set(rx, ry, rz));
      _local.setPosition(p.pos[0], p.pos[1] + dy, p.pos[2]);
      if (p.scale) _local.scale(_v.set(p.scale[0], p.scale[1], p.scale[2]));
    }
    if (nodNow && p.nod && !held) {   // lowered with the neck: about the neck's root, in the parent's frame
      _nod.makeTranslation(p.nod.x, p.nod.y, p.nod.z).multiply(_nodT.makeRotationZ(nodNow)).multiply(_nodT.makeTranslation(-p.nod.x, -p.nod.y, -p.nod.z));
      _local.premultiply(_nod);
    }
    const world = _mats[i] ?? (_mats[i] = new THREE.Matrix4());
    world.multiplyMatrices(p.parentIdx < 0 ? _root : _mats[p.parentIdx], _local);
    if (p.level && !held) {   // placed by the chain, oriented by the root alone
      _v.setFromMatrixPosition(world);
      world.multiplyMatrices(_root, _local).setPosition(_v);
    }
    // A HAND THAT HOLDS SOMETHING (2026-10-24; tools.js sets an.grip[i] = the item's `follow`): the wrist turns it between
    // the figure's own upright frame (0: a spear, a shield stay upright however the arm moves) and the forearm's (1: held
    // rigidly, a hammer swung with the arm) -- slerped by that share (beyond it, a negative one, the head of an axe tipped
    // forward over a falling forearm). The hand itself is drawn so, and its frame kept (an.gripM[i]) for the item, which
    // tools.js lays in that hand rigidly: the hand and what it holds are one. (The item used to be placed by its own
    // frame, rebuilt from the forearm's heading across the ground -- which flips as a forearm passes upright, at the top
    // of every hammer stroke -- while the hand went on with the arm: it swung separately, out of step.)
    const gf = an.grip?.[i];
    if (gf !== undefined && !held) {
      world.decompose(_gp, _gq, _gs);
      _gm.multiplyMatrices(_root, _local).decompose(_v, _gl, _v);
      world.compose(_gp, _gl.slerp(_gq, gf), _gs);
    }
    if (gf !== undefined) (an.gripM ??= {})[i] = (an.gripM[i] ?? new THREE.Matrix4()).copy(world);
    const j = (an.base + i) * 3;
    _v.copy(p.pA).applyMatrix4(world);
    fA[j] = _v.x; fA[j + 1] = _v.y; fA[j + 2] = _v.z;
    _v.copy(p.pB).applyMatrix4(world);
    if (p.sag || p.fall) {   // the cloth sags off the arm: its top rests along the arm, the rest hangs below -- tipped down toward the
      // plumb line (slerped) by no more than the cone's own half-angle, so the arm inside never comes through its side.
      // ...and an arm raised past level lets it FALL (2026-10-24): over the first SLIDE.fall of the rise the limit gives
      // way, and the sleeve hangs plumb from its top ring, the forearm going up out of that ring -- held to the cone, a
      // raised forearm carried the whole bell up round the hand like a funnel
      const ax = _v.x - fA[j], ay = _v.y - fA[j + 1], az = _v.z - fA[j + 2], L = Math.hypot(ax, ay, az) || 1;
      const up = Math.max(0, Math.min(1, ay / L / SLIDE.fall)), lim = p.sag + (Math.PI - p.sag) * up * up * (3 - 2 * up);
      const th = Math.acos(Math.max(-1, Math.min(1, -ay / L))), a = Math.min(th, lim), sn = Math.sin(th);
      if (a > th - 1e-3 && a > 1e-4) _v.set(fA[j], fA[j + 1] - L, fA[j + 2]);   // (all the way: plumb -- also where the arm points straight up and no plane is left to turn in)
      else if (a > 1e-4 && sn > 1e-3) {
        const ku = Math.sin(th - a) / sn, kw = Math.sin(a) / sn;
        _v.set(fA[j] + ax * ku, fA[j + 1] + ay * ku - L * kw, fA[j + 2] + az * ku);
      }
    }
    fB[j] = _v.x; fB[j + 1] = _v.y; fB[j + 2] = _v.z;
    if (p.r2 < 0) {
      _v.copy(p.pC).applyMatrix4(world);
      fC[j] = _v.x; fC[j + 1] = _v.y; fC[j + 2] = _v.z;
    }
  }
  if (parts.forwardFrom > 0) {   // the root's axis, turned by the frame that names the figure's forward
    const j = an.base * 3, m = _mats[parts.forwardFrom];
    _v.copy(parts[0].pA).applyMatrix4(m); fA[j] = _v.x; fA[j + 1] = _v.y; fA[j + 2] = _v.z;
    _v.copy(parts[0].pB).applyMatrix4(m); fB[j] = _v.x; fB[j + 1] = _v.y; fB[j + 2] = _v.z;
  }
}

// the WORLD MATRICES of the parts as the last writeAnimal posed them (each part's frame: its origin is its joint) --
// read at once, the next call overwrites them (joints.js reads the frames a position puts the parts in)
export const lastFrames = () => _mats;

// stride amplitude and run factor ease toward their targets (ampT, runT)
// so a stopping animal's legs straighten smoothly instead of snapping
// how far a figure's legs reach from hip to foot (the longest): what an.rest is a share of
export const legLength = (an) => an.parts.legLen ?? 0;
export function easeGait(an, dt) {
  if (an.ampT !== undefined) an.amp = (an.amp ?? 1) + (an.ampT - (an.amp ?? 1)) * Math.min(1, dt * 5);
  if (an.runT !== undefined) an.run = (an.run ?? 0) + (an.runT - (an.run ?? 0)) * Math.min(1, dt * 3);
  if (an.nodT !== undefined) an.nod = (an.nod ?? 0) + (an.nodT - (an.nod ?? 0)) * Math.min(1, dt * 1.6);   // (the head goes down slowly, comes up a little quicker: the same ease)
  if (an.restT !== undefined) an.rest = (an.rest ?? 0) + Math.max(-dt * 1.1, Math.min(dt * .35, an.restT - (an.rest ?? 0)));   // (lying down slowly; getting up quicker)
}
