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
const PUPILS = { round: 0, bar: 1, slit: 2 };
// IN FLIGHT (2026-11-04): a beast that flies (a mount's `fly`: the dragons, the manticore) held the pose it stands in
// -- neck reared up, legs planted on nothing, tail hanging to the ground that was not there -- and only beat its wings.
// an.fly (0 on the ground .. 1 aloft, eased toward an.flyT by easeGait) takes it into a pose of its own, worked out
// here from its rest pose so every body plan gets one:
//   neck   swung about its root (with the head and all that nods with it) until it reaches forward this many degrees
//          above level, the head turned back by `head` of that so it looks ahead, not at the sky
//   tail   its root aimed straight back, `tail` degrees (180 = level; less: rising), each link straightened by `straight`
//   legs   folded out of the way, [upper, lower, foot] degrees in their parents: the forelegs drawn up under the chest
//          (`front`), the hind legs trailing back along the tail (`hind`); the feet no longer kept level to the ground
//   wings  spread out (`arm`, `hand`: degrees out from the body's vertical plane, the arm and the parts hung on it), each
//          beat `beat` times as deep as a folded wing's flutter; the body rising and sinking `bob` m (per metre of
//          its leg length) against the downstroke
//   handK  the hand's beat: 1 + (beat - 1) * handK times its flutter (2026-11-05: .45 -> .25, the tip no longer
//          swinging under the belly on the downstroke nor standing up over the back on the upstroke)
//   wave   { deg, lag, speed, trunk, taper }: a wave travelling back down the tail, each link turned up and down by deg,
//          the next `lag` radians behind (speed: waves a second) -- a wingless lung swimming through the air. 0: none.
//          (2026-11-05) It starts in the trunk: a part with `waveAt` -k (k links ahead of the tail's root) rides it
//          too, by `trunk` degrees (default deg), `trunkLag` apart (2.09 for three links: a third of a wave each, their
//          turns summing to nothing, so the head holds its line); and the tail's links lose `taper` of it toward the tip (the last
//          link 1 - taper), so the tip no longer whips into a kink
// A species may write its own: `"flight": { "straight": .3, ... }` (any of these keys) in its definition -- a lung's
// body keeps its waves -- and any part a `flyRot` [x, y, z] (degrees, added aloft: a wing folded at rest, spread in flight).
// A wing part's `anim.side` (+-1) says which way it reaches when its rest pose cannot tell (a hand folded flat in the
// arm's plane, an arm tilted in at rest). THE UPSTROKE FOLD (2026-11-05): a part's `flyUp` [x, y, z] (degrees) is added
// aloft on the upstroke only, on the wing's own clock -- nothing through the downstroke, all of it at mid-upstroke
// (smoothly) -- a bat's hand flexed at the wrist and its fingers drawn together, so the wing is not a board both ways.
// (2026-11-05: neck 12 -> 22 with the head pitched back level, a shallow S rather than a ruler; the tail drooping a
//  little and keeping more of its curve; the forelegs tucked tight under the chest, the hind legs pointed back; the
//  wings at a 16-degree dihedral, beating shallower)
// PERCHED (2026-11-06): a bird whose model is drawn ALOFT -- its wings' rest the glide, no flight pose of its own (the eagle-owl,
// the macaw, the golden eagle: assets/creatures/birds) -- sitting on a branch or a ridge. an.perch (0 aloft .. 1 sat; the
// game sets it, index.html PERCHERS) folds each wing along its flank -- `fold`: [x, y, z] degrees added to the arm (row 0), the
// wrist (1) and the hand (2) of each wing chain, x and y mirrored for the right wing -- and stills its beat, droops the
// tail `tail` degrees, and keeps the head level however far the caller tips the body up (an.pitch): the head turned
// about the plumb line by an.look, not about the tipped body's axis -- an owl looking round on its branch. A rigid wing
// cannot lie on a flank half its depth (a real one folds its forearm and slides its feathers under each other), so the
// arm's frame is also `squeeze`d -- [chord, thickness, span] -- and the hand with it: the feathers stacked, the span shortened
// (the figures' own: an.perchFold { fold, squeeze } in place of these -- PERCHERS gives each species its fit)
// (2026-11-06: the wing hung down the flank about its own chord -- the feathers still pointing back -- the span squeezed
//  to a third, the hand turned back so the primaries reach over the tail: searched against each model's body)
// PERCH LEGS (2026-11-06): a part with `tuck` (degrees about z) or `curl` ({ len, r0, dir }) is a leg's bone, its rest the
// leg STANDING on the perch (tools: scratchpad perchlegs.py) -- aloft (1 - an.perch) it is turned by its tuck, the leg swung
// back under the tail, and a toe (`curl`) opened `open` of its drawn half-arc, lying back along the underside rather
// than hooked down below it (an.legs in place of an.perch where the caller
// lets them down sooner: the flare); sat, a toe drawn curled round a bough of
// radius r0 turns about its root by the difference of its half-arc (len / 2r, at most `curlMax`) on a perch of an.perchR
export const PERCH = { fold: [[80, -15, 10], [0, 0, 0], [15, -50, 0]], squeeze: [.7, 1, .35], tail: 15, open: .9, curlMax: 1.1 };
// LOOKING ROUND (2026-11-08): an.look turns the head toward something. The head's share (`head`) is its own turn about its
// centre; the neck's share (`neck`) is a turn about the VERTICAL through the neck's root, in the body's frame -- and the
// head rides it (a mammal's head hangs beside the neck on the body: it is swung about that same root, as the grazing nod
// swings it). Before, the neck's share was a turn about the neck's own axis -- a pill spun about its length, which shows
// nothing -- so the head turned alone, as if on a pin, and the neck never followed
export const LOOK = { head: .6, neck: .4 };
export const FLIGHT = { neck: 22, head: .9, tail: 174, straight: .55, front: [-75, 140, 70], hind: [-95, 25, -65],
                        arm: 74, hand: 8, beat: 1.9, handK: .25, wave: 0, bob: .06, ease: 1.2 };
function flightPose(def, parts, index) {
  const F = def.flight && typeof def.flight === "object" ? { ...FLIGHT, ...def.flight } : FLIGHT;   // (a species' own numbers: `flight` in its definition)
  const deg = Math.PI / 180, wrap = (a) => Math.atan2(Math.sin(a), Math.cos(a));
  const dirOf = (p) => new THREE.Vector3(0, 1, 0).applyEuler(new THREE.Euler(...p.baseRot));
  const neckI = index.get("neck");
  let neck = 0;
  if (neckI !== undefined) { const d = dirOf(parts[neckI]); if (d.x > .05) neck = wrap(F.neck * deg - Math.atan2(d.y, d.x)); }
  const legs = parts.filter((p) => p.ik && !p.ik.follow);
  const isFront = (p) => legs.length >= 4 && p.ik.leg < 2;
  let speed = 0;
  parts.forEach((p, i) => {
    const id = def.parts[i].id, f = {};
    if (p.nod && neck) f.neck = neck;
    if (id === "head" && neck) f.rz = -neck * F.head;
    if (id === "tail" && p.parentIdx >= 0) {
      const d = dirOf(p);
      if (d.x < 0) f.pre = { c: new THREE.Vector3(...p.pos), a: wrap(F.tail * deg - Math.atan2(d.y, d.x)) };
    }
    if (/^tail\d+$/.test(id)) f.rz = -p.baseRot[2] * F.straight;
    const wk = /^tail\d*$/.test(id) ? (+id.slice(4) || 0) : def.parts[i].waveAt;
    if (F.wave && wk !== undefined) {
      const W = F.wave, nT = def.parts.filter((q) => /^tail\d*$/.test(q.id)).length, tp = wk > 0 && nT > 1 ? 1 - (W.taper ?? 0) * wk / (nT - 1) : 1;
      f.wave = { a: (wk < 0 ? W.trunk ?? W.deg ?? 15 : (W.deg ?? 15) * tp) * deg, ph: -wk * (wk < 0 ? W.trunkLag ?? W.lag ?? .9 : W.lag ?? .9), w: (W.speed ?? .3) * Math.PI * 2 };
    }
    if (p.ik) {
      const up = p.ik.follow ? parts[p.parentIdx] : p, T = isFront(up) ? F.front : F.hind;
      f.to = (p.ik.follow ? T[1] : T[0]) * deg;
      // (splay [front, hind]: degrees each upper leg swings out from the body -- a lung's legs spread wide; or, less
      //  than 0, in -- a dragon's thighs drawn in flush under its flanks as the legs tuck)
      if (!p.ik.follow && F.splay) f.rx = -(Math.sign(p.pos[2]) || 1) * (isFront(p) ? F.splay[0] : F.splay[1]) * deg;
    }
    if (p.level && p.parentIdx >= 0 && parts[p.parentIdx].ik?.follow) {
      const T = isFront(parts[parts[p.parentIdx].parentIdx]) ? F.front : F.hind;
      f.to = T[2] * deg; f.free = true;
    }
    if (p.anim?.wing) {
      let hand = false;   // (a wing part with a wing part anywhere above it -- a dragon's hand beyond its forearm)
      for (let q = p.parentIdx; q >= 0 && !hand; q = parts[q].parentIdx) hand = !!parts[q].anim?.wing;
      const sg = p.anim.side ?? (Math.sign(p.baseRot[0]) || p.side);
      f.rx = sg * (hand ? F.hand : F.arm) * deg - p.baseRot[0];
      f.beat = hand ? 1 + (F.beat - 1) * F.handK : F.beat;   // (the hand follows the arm: a deeper beat of its own folds the tip straight up)
      if (!hand) speed = p.anim.speed;
    }
    // (and any part's own turn aloft, `flyRot` [x, y, z] degrees added as it takes off: a wing folded along the flank at
    //  rest swept out to its spread, a dragon's fingers fanned)
    const fr = def.parts[i].flyRot;
    if (fr) { f.rx = (f.rx ?? 0) + fr[0] * deg; f.ry = (f.ry ?? 0) + fr[1] * deg; f.rz = (f.rz ?? 0) + fr[2] * deg; }
    const fu = def.parts[i].flyUp;
    if (fu) f.up = fu.map((v) => v * deg);
    p.fl = Object.keys(f).length ? f : null;
  });
  return { speed, bob: F.bob * Math.max(.3, parts.legLen || 1) };
}   // a face mark's pupil (composite FACE MARKS)
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
      // bobK (2026-11-09): this part's own SHARE of the bob, 0..1, where its parent has more -- a rider's trunk .45 and head .2
      // (people.js pose "ride"): the hips follow the saddle whole, the seat absorbs the rest, as a rider's does. Without it a
      // part rides its parent's share whole (an idle head, neck or tail on the body: none -- it cancels the body's)
      bobK: typeof part.bobK === "number" ? part.bobK : undefined,
      spine: !!part.spine,        // a torso cut (mammals.js): these sweep as ONE lathe, whatever their shading
      // body motion (head turns, tail swishes, neck sway) follows MOVEMENT in
      // general -- the gait clock, or a mount's own movement clock while it
      // flies with its legs hanging still. Swimmers and fliers keep
      // everything on the gait clock: their tails and wings ARE the locomotion
      idle: !def.fly && /^(head|neck|tail|ear|mane|trunk|snout|hair)/.test(part.id.replace(/^(r_|L_|R_)/, "")),
      tailRoot: /^tail/.test(part.id) && part.parent != null && def.parts[index.get(part.parent)]?.parent == null,   // (a tail hung on the root: UPRIGHT)
      headish: /^(head|neck)/.test(part.id.replace(/^(r_|L_|R_)/, "")),   // (head and every neck link: aloft they hold their line)
      look: part.id === "head" ? LOOK.head : 0,   // the head's own share of an.look (the neck's is taken about the neck's root: LOOK)
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
      facet: !!part.facet,      // composite: lit by its triangles' own planes -- a creature's stylised low-poly look (shell.js FACET)
      detail: !!part.detail,    // shell: a small piece of modelling (a brow, a cheekbone) left out in the distance (SHELL.detail)
      stone: part.stone ?? 0,   // composite: carved -- a statue's material (1 marble, 2 bronze, 3 gold, 4 limestone): shell.js stoneAt
      flat: part.flat ?? 0,     // composite: a capsule squashed along the figure's forward to this share of its width (a flat torso)
      palm: !!part.palm,        // ...squashed across its own axis and the figure's forward instead (a hand: palm in as it hangs, shell.js)
      anat: part.anat ?? 0,     // ...where on the trunk a flat torso's piece is (people.js `anat`: a bare torso carved with its anatomy, shell.js ANATOMY)
      pot: part.pot ?? 0,       // ...and its belly (people.js `pot`: shell.js TRUNK.pot)
      limb: part.limb ?? 0,     // ...and a bare round limb's kind (people.js LIMB: a statue's carved with its muscles, shell.js LIMBS)
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
      fall: !!part.fall,          // ...and on an arm raised past level it slides down the arm, gathered, drooping (SLIDE)
      drape: drapes.has(part.id) && i > lastLeg,
      // ...and DRAPED over them (shell.js CLING): { k: its cling, ease, over: the legs' ids } -- the ids made indices below
      cling: part.cling ? { k: part.cling.k, ease: part.cling.ease ?? 0, over: part.cling.over } : null,
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
  for (const p of parts) if (p.cling) p.cling.over = p.cling.over.map((id) => index.get(id) ?? -1);
  // (and its FOREARMS: where each arm it is draped over -- not the part it hangs from -- has its forearm in the very next
  //  slot, its own child (people.js adds arm, forearm, hand in that order), shell.js reads the forearm there too: CLING)
  for (const p of parts) if (p.cling) { const arms = p.cling.over.slice(4).filter((i) => i >= 0 && i !== p.parentIdx); p.cling.fore = arms.length > 0 && arms.every((i) => parts[i + 1]?.parentIdx === i); }
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
  parts.upright = def.upright ? { a: (def.upright.deg ?? 70) * Math.PI / 180, fold: def.upright.fold ?? .45 } : null;   // (standing up on its hind legs: UPRIGHT)
  parts.idleSway = parts.some((p) => p.stone) ? 0 : def.idleSway ?? 0;   // (a figure standing about: its weight shifting -- people.js IDLE_SWAY; never a statue)
  parts.legLen = Math.max(0, ...parts.filter((p) => p.ik?.foot != null).map((p) => p.pos[1] - p.ik.foot));
  // A FOUR-LEGGED FIGURE'S HIPS, for standing it on the ground it is on (fitGround): each leg's hip in the root's frame
  // (its parents' offsets summed -- a rig's legs hang unturned off the body), and how much further than at rest the leg
  // reaches (its slack: a foot can go that much lower before the body has to come down to it)
  const legs = parts.flatMap((p, i) => p.ik && !p.ik.follow && p.ik.foot != null ? [i] : []);
  if (legs.length === 4 && !def.biped && !def.fly && !def.swim) {
    parts.hips = legs.map((i) => {
      const p = parts[i], at = [...p.pos];
      for (let q = p.parentIdx; q >= 0; q = parts[q].parentIdx) for (let k = 0; k < 3; k++) at[k] += parts[q].pos[k];
      return { i, leg: p.ik.leg, x: at[0], y: at[1], z: at[2], slack: Math.max(0, p.ik.upper + p.ik.lower - .005 - Math.abs(p.pos[1] - p.ik.foot)) };
    });
  }
  if (parts.upright) { const H = parts.hips?.filter((q) => q.leg >= 2) ?? []; parts.upright.x = H.length ? (H[0].x + H[1].x) / 2 : 0; parts.upright.y = H.length ? (H[0].y + H[1].y) / 2 : 0; }
  parts.trails = parts.some((p) => p.trail);   // (a cloak that trails: writeAnimal keeps its spring -- TRAIL)
  parts.follows = parts.some((p, i) => p.follow >= 0 && p.follow < i);   // (a panel lifted by its arm, posed after it -- LIFT)
  for (const [i, p] of parts.entries()) if (p.follow >= i) p.follow = -1;
  // the root's drawn axis is the figure's FORWARD (a flat torso is squashed along it, the cloth and the jewels take
  // their frame from it); `forwardFrom` names the part whose frame turns it instead -- a person's chest, so a trunk
  // turned at the waist faces where it turns (that frame is the root's own at rest)
  parts.forwardFrom = def.forwardFrom ? index.get(def.forwardFrom) ?? -1 : -1;
  parts.flight = def.flight !== false && (def.mount?.fly || def.flight) ? flightPose(def, parts, index) : null;   // (`flight: false`: a flying mount with no FLIGHT pose -- a sky steed, folding its wings by PERCH and tucking its legs by skysteeds.js tuckLegs)
  // (PERCHED: each wing part's place in its chain -- 0 the arm on the body, 1, 2 out along it -- and its side, the arm's)
  if (!parts.flight) for (const [i, p] of parts.entries()) {
    const id = def.parts[i].id, dp = def.parts[i];
    if (dp.tuck !== undefined || dp.curl) p.leg = { tuck: (dp.tuck ?? 0) * Math.PI / 180, curl: dp.curl ?? null };   // (PERCH LEGS)
    else if (p.anim?.wing) {
      let k = 0, q = p;
      while (q.parentIdx >= 0 && parts[q.parentIdx].anim?.wing) { q = parts[q.parentIdx]; k++; }
      p.perch = { k, side: Math.sign(q.pos[2]) || p.side };
      parts.perchable = true;
    } else if (id === "head") p.perch = { head: true };
    else if (id === "tail" && p.parentIdx >= 0 && parts[p.parentIdx].parentIdx < 0) p.perch = { tail: true };
  }
  // TAIL SWAY (2026-11-08): a tail's root link swung about its own x -- right for a tail that HANGS (it swings from side to
  // side), wrong for one carried back or up (a cat's, a dog's, a dinosaur's): there x runs along the tail, so the tail
  // rolled about its own length and its tip stayed put. The sway's axis is now the one across the tail's rest chord (root
  // to tip) and the figure's sideways, in the parent's frame: a hanging tail swings about x as before, a tail held back
  // swings about the vertical -- the whole of it sweeping left and right about where it starts
  for (const [i, p] of parts.entries()) if (p.tailRoot && p.anim?.axis === "x") {
    const M = new Map(), at = (q) => new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(...q.baseRot)).setPosition(q.pos[0], q.pos[1], q.pos[2]).scale(new THREE.Vector3(...(q.scale ?? [1, 1, 1])));
    const o = new THREE.Vector3(p.pos[0], p.pos[1], p.pos[2]), tip = o.clone();
    let best = 0;
    for (let j = i; j < parts.length; j++) {
      const q = parts[j], pm = j === i ? null : M.get(q.parentIdx);
      if (j !== i && !pm) continue;
      const m = pm ? at(q).premultiply(pm) : at(q);
      M.set(j, m);
      for (const v of [new THREE.Vector3(), q.pB.clone()]) { v.applyMatrix4(m); const d = v.distanceTo(o); if (d > best) { best = d; tip.copy(v); } }
    }
    const d = tip.sub(o), ax = new THREE.Vector3(0, 0, 1).cross(d);
    if (ax.length() > d.length() * .2) p.sway = ax.normalize();   // (a tail laid out sideways keeps its old axis)
  }
  compiledCache.set(def, parts);
  return parts;
}

// Two-bone IK for one leg, in the body's xy plane with the hip at the
// origin. Returns [upper, lower] z rotations (positive = swings the foot
// forward, the convention of a capsule hanging from its pivot).
//   ik: { upper, lower, side (+1 knee bends forward, -1 backward), foot (foot joint y below the body origin) }
//   g: { stride, lift }  ph: this leg's phase  amp: stride amplitude 0..1  bob: the body's current bob
//   hipY: the hip's y in body space
export function legPose(ik, g, ph, amp, bob, hipY, tip = 0, draw = 0) {
  const stride = g.stride * amp, lift = Math.max(0, Math.cos(ph)) * g.lift * amp;
  let dx = stride * Math.sin(ph), dy = ik.foot - hipY + lift - bob;
  if (draw) { const L0 = ik.upper + ik.lower; dx = dx * (1 - draw) + L0 * .18 * draw; dy = dy * (1 - draw) - L0 * .5 * draw; }   // (UPRIGHT: a foreleg drawn up off the ground, its paw hanging below the chest)
  if (tip) { const c = Math.cos(tip), s = Math.sin(tip); [dx, dy] = [dx * c + dy * s, -dx * s + dy * c]; }   // (UPRIGHT: the body tipped up about the hips -- the foot's place turned back into its frame)
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

// STANDING ON A SLOPE (display only, like the rest of the pose): a four-legged figure was posed level whatever it stood
// on, its origin on the ground under its middle -- on a hillside the uphill feet went into the ground and the downhill
// ones hung in the air. `ground(x, z)` is the terrain's height; fitGround reads it under the four hips and sets an._fit:
//   pitch -- the body tipped (+ nose up) to the line from the hind feet's ground to the front feet's, at most `max`
//   dy[leg] -- each foot raised (+) or lowered off the plane that pitch lays through the origin, to the ground under it
//   (a side slope, a bump), the body coming down `drop` where a foot has to reach further than its leg's slack
// Only for a figure standing on that ground (within `near` of it at its origin: not one on a sill, a floor, a cart);
// recomputed when it has moved or turned, eased toward so it never snaps.
export const FIT = { max: .45, near: .3, ease: 8, moved: .02 };
export function fitGround(an, ground, dt) {
  const hips = an.parts.hips;
  if (!hips || an.down || an.hidden) { an._fit = null; return; }
  const p = an.position, c = Math.cos(an.rotY), s = Math.sin(an.rotY);
  let w = an._fitW;
  if (!w || Math.abs(w.x - p.x) + Math.abs(w.z - p.z) > FIT.moved || Math.abs(w.rotY - an.rotY) > .02 || Math.abs(w.y - p.y) > FIT.moved) {
    const g0 = ground(p.x, p.z);
    w = an._fitW = { x: p.x, y: p.y, z: p.z, rotY: an.rotY, on: Math.abs(g0 - p.y) < FIT.near, pitch: 0, dy: [0, 0, 0, 0], drop: 0 };
    if (w.on) {
      // the ground under each hip (the root's frame turned by rotY: x' = x cos + z sin, z' = -x sin + z cos), off the origin's
      const h = hips.map((q) => ground(p.x + q.x * c + q.z * s, p.z - q.x * s + q.z * c) - g0);
      const F = hips.filter((q) => q.leg < 2), H = hips.filter((q) => q.leg >= 2), mean = (L, f) => L.reduce((a, q) => a + f(q), 0) / L.length;
      const xF = mean(F, (q) => q.x), xH = mean(H, (q) => q.x), hF = mean(F, (q) => h[hips.indexOf(q)]), hH = mean(H, (q) => h[hips.indexOf(q)]);
      const pitch = Math.max(-FIT.max, Math.min(FIT.max, Math.atan2(hF - hH, xF - xH))), tn = Math.tan(pitch), cs = Math.cos(pitch);
      // (the plane through the origin at that pitch, and each foot's ground off it, measured along the tipped body's up --
      //  heights off the ground at the origin, not off the origin: one set a little into the ground stays so)
      const r = hips.map((q, k) => (h[k] - q.x * tn) * cs);
      const drop = Math.max(0, ...hips.map((q, k) => -r[k] - q.slack));
      w.pitch = pitch; w.drop = drop;
      hips.forEach((q, k) => { w.dy[q.leg] = r[k] + drop; });
    }
  }
  const f = an._fit ??= { pitch: 0, dy: [0, 0, 0, 0], drop: 0 }, e = dt > 0 ? 1 - Math.exp(-FIT.ease * dt) : 1;
  f.pitch += (w.pitch - f.pitch) * e; f.drop += (w.drop - f.drop) * e;
  for (let k = 0; k < 4; k++) f.dy[k] += (w.dy[k] - f.dy[k]) * e;
}

// the gait parameter set for a run factor 0..1: walk, run, or a blend
const _g = { offsets: [0, 0, 0, 0], stride: 0, lift: 0, bob: 0, bobPh: undefined, roll: 0, rollPh: undefined, pitch: 0, pitchPh: undefined };
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
  _g.roll = (w.roll ?? 0) + ((r.roll ?? 0) - (w.roll ?? 0)) * run; _g.rollPh = w.rollPh;
  _g.pitch = (w.pitch ?? 0) + ((r.pitch ?? 0) - (w.pitch ?? 0)) * run; _g.pitchPh = r.pitchPh ?? w.pitchPh;
  return _g;
}

const _mats = [];
const _root = new THREE.Matrix4();
const _pitch = new THREE.Matrix4(), _roll = new THREE.Matrix4();
const _local = new THREE.Matrix4(), _nod = new THREE.Matrix4(), _nodT = new THREE.Matrix4();
const _e = new THREE.Euler();
const _gq = new THREE.Quaternion(), _gl = new THREE.Quaternion(), _gs = new THREE.Vector3(), _gp = new THREE.Vector3(), _gm = new THREE.Matrix4(), _gr = new THREE.Matrix4();
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
// A HANGING SLEEVE ON A RAISED ARM SLIDES DOWN IT: as the arm rises past level (its rise over its length, full by
// `span`) the sleeve gathers toward its top, to `gather` of its length, and its mouth -- still round the arm, the hand
// coming out through it -- droops as far as the gathered cone's own flare lets it, its top along the arm and the rest
// hanging below. See writeAnimal. (It was held to the arm, a funnel stood round the raised hand; then it fell plumb from
// its top ring, the forearm going up out of the cloth with the hand left inside it.)
export const SLIDE = { span: .8, gather: .45 };
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
  const fly = parts.flight && !an.down ? an.fly ?? 0 : 0;   // (aloft: FLIGHT)
  const perch = parts.perchable && !an.down ? an.perch ?? 0 : 0;   // (sat on a branch: PERCH)
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
  nodNow += stepNod * (1 - fly);   // (2026-11-08: aloft no step nods the head -- a pegasus, a griffin; it fades out with an.fly)
  // (2026-11-09: a RIDDEN mount bobs like any -- its rider's hips go with the saddle and its trunk and head take a share
  //  (bobK), the camera the head's: index.html; before, a ridden mount did not bob at all and rode dead under a level view)
  const bobOwn = g ? g.bob * amp * Math.sin(phase * 2 + (g.bobPh ?? .5)) : 0;
  const bob = bobOwn + (an.bobExt ?? 0);   // (bobExt: a bob given from outside -- the player's own rider figure, hung on its mount's, index.html updateSelf)
  an.bobNow = bobOwn; an.gaitPhase = phase; an.gaitAmp = amp;   // (read back by whoever rides it: the eye's share of the bob, the sway in step)
  _root.makeRotationY(an.rotY);
  const fit = an._fit;   // (stood on a slope: fitGround)
  if (fit) _root.multiply(_pitch.makeRotationZ(fit.pitch));
  if (an.pitch || dip) _root.multiply(_pitch.makeRotationZ((an.pitch ?? 0) - dip * .5));   // an.pitch: the body tipped about its own left axis (+ nose up) -- a squirrel on a trunk
  if (an.roll) _root.multiply(_roll.makeRotationX(an.roll));
  // STANDING ABOUT: the weight shifting -- a slow rock to the side and a slower one to and fro, each figure on its own
  // beat, fading as the stride comes in (a walker's sway is its gait's)
  if (parts.idleSway && !an.down) {
    const k = parts.idleSway * Math.max(0, 1 - amp * 1.5), ph = (an.idx ?? 0) * 2.17;
    if (k > 1e-4) _root.multiply(_roll.makeRotationX(k * Math.sin(t * .55 + ph))).multiply(_pitch.makeRotationZ(k * .45 * Math.sin(t * .37 + ph * 1.3)));
  }   // an.roll: turned about its own forward axis (+ toward its +z) -- a figure struck down lying on its side (combat.js)
  // A GAIT'S ROCK (gaits: roll, pitch -- radians, once a stride, rollPh / pitchPh its phase): a badger's rolling waddle side
  // to side; a bounding weasel tipping nose up as its forefeet leave the ground and down as they land. Fades with the stride
  if (g && !an.down && !fly) {
    if (g.roll) _root.multiply(_roll.makeRotationX(g.roll * amp * Math.sin(phase + (g.rollPh ?? 0))));
    if (g.pitch) _root.multiply(_pitch.makeRotationZ(g.pitch * amp * Math.sin(phase + (g.pitchPh ?? 0))));
  }
  // UPRIGHT (a species' `upright`: { deg, fold }; an.upright 0..1, eased toward an.uprightT): a weasel's look-out, standing
  // up on its hind legs -- the body tipped nose up about its hind hips by deg, the hind feet kept on the ground under them,
  // the forelegs drawn up to the chest by `fold`, the tail laid back along the ground. The root's frame is untouched (the
  // feet stay level): the tip is the body part's own
  const U = parts.upright, up = U && an.upright > 1e-3 && !an.down && !fly ? U.a * an.upright : 0;
  _root.setPosition(an.position.x, an.position.y - rest - (fit ? fit.drop : 0), an.position.z);   // (an.rest: lying down, the body this much lower)
  if (fly) _root.elements[13] -= fly * parts.flight.bob * Math.sin(tw * parts.flight.speed * Math.PI * 2 + .6);   // (rising on the downstroke: FLIGHT)
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
    let [rx, ry, rz] = p.baseRot, swayA = 0;   // (swayA: a tail root's sway, taken about its own axis below -- TAIL SWAY)
    if (an.down) {   // struck down: a part's fold, or a wing folded back and laid flat against the flank (Euler XYZ: the sweep back
      // about y, then turned down about x -- the span along the side, the wing's flat facing out; on its side, it lies over the body)
      if (p.fold) { rx += p.fold[0]; ry += p.fold[1]; rz += p.fold[2]; }
      else if (p.anim?.wing) { ry -= p.side * 1.4; rx += p.side * 1.5; }
    }
    // an.look: the head turned to look at something (radians about the vertical, + to its left), shared between the
    // neck (two fifths) and the head (the rest) -- a villager looking at you as it greets you (index.html greetTick)
    const pk = perch && p.perch;
    if (pk) {   // (PERCH: the wing folded along the flank, the tail drooped; the head is turned below, once its matrix is made)
      if (pk.k !== undefined) { const FF = (an.perchFold ?? PERCH).fold, F = FF[Math.min(pk.k, FF.length - 1)], d2r = Math.PI / 180 * perch; rx += pk.side * F[0] * d2r; ry += pk.side * F[1] * d2r; rz += F[2] * d2r; }
      else if (pk.tail) rz += PERCH.tail * Math.PI / 180 * perch;
    }
    if (p.leg) {   // (PERCH LEGS: drawn standing on the perch; aloft swung back under the tail and the toes laid back; sat, each toe
      //  turned to lie round a perch of radius an.perchR from the r0 it is drawn round)
      const L = p.leg, u = 1 - (parts.perchable && !an.down ? an.legs ?? perch : 0);   // (an.legs: let down ahead of the wings' fold -- the flare)
      rz += L.tuck * u;
      if (L.curl) { const C = L.curl, A = (r) => Math.min(PERCH.curlMax, C.len / (2 * r)); rz -= C.dir * ((A(an.perchR ?? C.r0) - A(C.r0)) * (1 - u) - PERCH.open * A(C.r0) * u); }
    }
    if (an.look && p.look && !(pk && pk.head)) ry += an.look * p.look;
    if (p.anim) {
      const a = p.anim;
      // a.amp: the swing belongs to the gait (a person's arms, a skirt) and fades with the stride when standing
      // (the idle parts each animal on its own beat -- a herd does not look about in step -- and a.flick: that power of
      //  the sine's crest only, a quick twitch now and then -- an ear)
      const ph = (a.wing ? tw : p.idle ? tm : a.amp ? tg : tt) * a.speed * Math.PI * 2 + (a.phase || 0) + (p.idle ? (an.idx ?? 0) * 2.39 : 0);
      const d = an.down && a.wing ? 0 : (a.deg * Math.PI / 180) * (a.flick ? Math.pow(Math.max(0, Math.sin(ph)), a.flick) : Math.sin(ph)) * (a.amp ? amp : 1) * (a.wing && perch ? 1 - perch : 1)
        * (fly && p.fl?.beat ? 1 + fly * (p.fl.beat - 1) : 1);
      // (2026-11-08) ALOFT THE HEAD HOLDS ITS LINE: the head's and neck's up-and-down swing (about z) fades out with an.fly --
      //  a pegasus or a griffin no longer nods as it flies; it still looks left and right (about y)
      const dz = fly && !a.wing && p.headish ? d * (1 - fly) : d;
      if (p.sway) swayA = d; else if (a.axis === "x") rx += d; else if (a.axis === "y") ry += d; else rz += dz;
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
        const [t1, t2] = legPose(p.ik, g, phase + g.offsets[p.ik.leg] + (p.ik.phase || 0), amp, bob, p.pos[1] - rest - (fit ? fit.dy[p.ik.leg] : 0), up, up && p.ik.leg < 2 ? U.fold * an.upright : 0);   // (resting: the feet aimed as much higher as the body lies lower -- the legs fold under it)
        rz += t1; _lower[i] = t2; thighs += t1; nThighs++;
      }
    }
    if (fly && p.fl) {   // aloft (FLIGHT): the pose's own turns, the legs drawn toward their folded angles
      const f = p.fl;
      if (f.rz) rz += f.rz * fly;
      if (f.rx) rx += f.rx * fly;
      if (f.ry) ry += f.ry * fly;
      if (f.to !== undefined) rz += (f.to - rz) * fly;
      if (f.wave) rz += f.wave.a * Math.sin(t * f.wave.w + f.wave.ph) * fly;   // (the travelling wave: FLIGHT.wave)
      if (f.up) {   // (the upstroke fold: flyUp, on the wing's clock -- 0 through the downstroke, all of it at mid-upstroke)
        const c = Math.max(0, -Math.cos(tw * parts.flight.speed * Math.PI * 2 - .25)), u = c * c * (3 - 2 * c) * fly;
        rx += f.up[0] * u; ry += f.up[1] * u; rz += f.up[2] * u;
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
    // stay as steady running as they do walking or flying. Each part's SHARE of the bob: the body's 1, an idle part's on it 0,
    // a part's own `bobK` where it says, else its parent's; a part moves by its share less its parent's (so a rider's pelvis
    // marked bob on a bobbing mount rides it once, not twice)
    const pShare = p.parentIdx >= 0 ? parts[p.parentIdx]._share : 0;
    p._share = p.bob ? 1 : p.bobK !== undefined ? p.bobK : p.idle && p.parentIdx >= 0 && parts[p.parentIdx].bob ? 0 : pShare;
    const dy = bob * (p._share - pShare);
    const held = an.pose?.[i];
    if (held) {   // held by its joint: that rotation, about the joint's pivot
      _local.makeRotationFromQuaternion(held.q);
      if (held.c) { _v.copy(held.c).applyQuaternion(held.q); _local.setPosition(p.pos[0] + held.c.x - _v.x, p.pos[1] + dy + held.c.y - _v.y, p.pos[2] + held.c.z - _v.z); }
      else _local.setPosition(p.pos[0], p.pos[1] + dy, p.pos[2]);
      if (p.scale) _local.scale(_v.set(p.scale[0], p.scale[1], p.scale[2]));
    } else if (!p.anim && !(p.ik && g) && !(an.down && p.fold) && !(p.drape && nThighs) && !p.trail && p.follow < 0 && !(fly && p.fl) && !pk && !p.leg) {   // a part that never moves in its parent: its local transform built once, cached (only the bob added)
      _local.copy(p._lm ?? (p._lm = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(rx, ry, rz)).setPosition(p.pos[0], p.pos[1], p.pos[2])
        .scale(new THREE.Vector3(...(p.scale ?? [1, 1, 1])))));
      _local.elements[13] += dy;
    } else {
      _local.makeRotationFromEuler(_e.set(rx, ry, rz));
      _local.setPosition(p.pos[0], p.pos[1] + dy, p.pos[2]);
      if (p.scale) _local.scale(_v.set(p.scale[0], p.scale[1], p.scale[2]));
    }
    if (swayA) {   // (TAIL SWAY: the whole tail swung about the axis across it, at its root)
      _nod.makeTranslation(p.pos[0], p.pos[1] + dy, p.pos[2]).multiply(_nodT.makeRotationAxis(p.sway, swayA)).multiply(_nodT.makeTranslation(-p.pos[0], -p.pos[1] - dy, -p.pos[2]));
      _local.premultiply(_nod);
    }
    if (pk && pk.k === 0) { const Q = (an.perchFold ?? PERCH).squeeze; _local.scale(_v.set(1 + (Q[0] - 1) * perch, 1 + (Q[1] - 1) * perch, 1 + (Q[2] - 1) * perch)); }   // (PERCH: the folded wing's feathers stacked)
    if (pk && pk.head) {   // (PERCH: the head kept level on the tipped body, and turned about the plumb line by an.look)
      _nod.makeTranslation(p.pos[0], p.pos[1] + dy, p.pos[2]).multiply(_nodT.makeRotationZ(-(an.pitch ?? 0) * perch)).multiply(_nodT.makeRotationY((an.look ?? 0) * p.look))
        .multiply(_nodT.makeTranslation(-p.pos[0], -p.pos[1] - dy, -p.pos[2]));
      _local.premultiply(_nod);
    }
    if (up && p.parentIdx < 0) {   // (UPRIGHT: the body tipped about the hind hips)
      _nod.makeTranslation(U.x, U.y, 0).multiply(_nodT.makeRotationZ(up)).multiply(_nodT.makeTranslation(-U.x, -U.y, 0));
      _local.premultiply(_nod);
    }
    if (up && p.tailRoot) { const c = _v.setFromMatrixPosition(_local); _nod.makeTranslation(c.x, c.y, c.z).multiply(_nodT.makeRotationZ(-up * .9)).multiply(_nodT.makeTranslation(-c.x, -c.y, -c.z)); _local.premultiply(_nod); }   // (its tail laid back)
    const nodA = nodNow + (fly && p.fl?.neck ? p.fl.neck * fly : 0);
    if (nodA && p.nod && !held) {   // lowered with the neck: about the neck's root, in the parent's frame
      _nod.makeTranslation(p.nod.x, p.nod.y, p.nod.z).multiply(_nodT.makeRotationZ(nodA)).multiply(_nodT.makeTranslation(-p.nod.x, -p.nod.y, -p.nod.z));
      _local.premultiply(_nod);
    }
    if (an.look && p.nod && !held && !(pk && pk.head)) {   // LOOK: the neck's share of the turn, about the vertical through the neck's root -- the neck, the head beside it, a mane along it
      _nod.makeTranslation(p.nod.x, p.nod.y, p.nod.z).multiply(_nodT.makeRotationY(an.look * LOOK.neck)).multiply(_nodT.makeTranslation(-p.nod.x, -p.nod.y, -p.nod.z));
      _local.premultiply(_nod);
    }
    if (fly && p.fl?.pre && !held) {   // (aloft: the tail's root swung straight back about where it joins)
      const c = p.fl.pre.c;
      _nod.makeTranslation(c.x, c.y, c.z).multiply(_nodT.makeRotationZ(p.fl.pre.a * fly)).multiply(_nodT.makeTranslation(-c.x, -c.y, -c.z));
      _local.premultiply(_nod);
    }
    const world = _mats[i] ?? (_mats[i] = new THREE.Matrix4());
    world.multiplyMatrices(p.parentIdx < 0 ? _root : _mats[p.parentIdx], _local);
    if (p.level && !held && !(fly >= 1 && p.fl?.free)) {   // placed by the chain, oriented by the root alone
      if (fly && p.fl?.free) {   // (aloft: the foot hangs with its leg -- the two orientations slerped by how far up it is)
        world.decompose(_gp, _gq, _gs);
        _gm.multiplyMatrices(_root, _local).decompose(_v, _gl, _v);
        world.compose(_gp, _gl.slerp(_gq, fly), _gs);
      } else {
        _v.setFromMatrixPosition(world);
        world.multiplyMatrices(_root, _local).setPosition(_v);
      }
    }
    // A HAND THAT HOLDS SOMETHING (2026-10-24; tools.js sets an.grip[i] = the item's `follow`): the wrist turns it between
    // the figure's own upright frame (0: a spear, a shield stay upright however the arm moves) and the forearm's (1: held
    // rigidly, a hammer swung with the arm) -- slerped by that share (beyond it, a negative one, the head of an axe tipped
    // forward over a falling forearm). The hand itself is drawn so, and its frame kept (an.gripM[i]) for the item, which
    // tools.js lays in that hand rigidly: the hand and what it holds are one. (The item used to be placed by its own
    // frame, rebuilt from the forearm's heading across the ground -- which flips as a forearm passes upright, at the top
    // of every hammer stroke -- while the hand went on with the arm: it swung separately, out of step.)
    // (a hand HELD by its joint -- a position, a statue's pose -- takes the same share: its upright frame is the hand's
    //  rest in the figure's, as a hanging hand's is)
    const gf = an.grip?.[i];
    if (gf !== undefined) {
      world.decompose(_gp, _gq, _gs);
      _gm.multiplyMatrices(_root, held ? _gr.makeRotationFromEuler(_e.set(p.baseRot[0], p.baseRot[1], p.baseRot[2])) : _local).decompose(_v, _gl, _v);
      world.compose(_gp, _gl.slerp(_gq, gf), _gs);
    }
    if (gf !== undefined) (an.gripM ??= {})[i] = (an.gripM[i] ?? new THREE.Matrix4()).copy(world);
    const j = (an.base + i) * 3;
    _v.copy(p.pA).applyMatrix4(world);
    fA[j] = _v.x; fA[j + 1] = _v.y; fA[j + 2] = _v.z;
    _v.copy(p.pB).applyMatrix4(world);
    if (p.sag || p.fall) {   // the cloth sags off the arm: its top rests along the arm, the rest hangs below -- tipped down toward the
      // plumb line (slerped) by no more than the cone's own half-angle, so the arm inside never comes through its side.
      // ...and on an arm raised past level it SLIDES down the arm (SLIDE): shorter, gathered toward its top, and so flaring
      // wider for its length -- which lets its mouth droop further, the arm still inside it and out through the mouth
      const ax = _v.x - fA[j], ay = _v.y - fA[j + 1], az = _v.z - fA[j + 2], L = Math.hypot(ax, ay, az) || 1;
      let Ls = L, lim = p.sag;
      if (p.fall) {
        const u = Math.max(0, Math.min(1, ay / L / SLIDE.span)), k = u * u * (3 - 2 * u), g = 1 - (1 - SLIDE.gather) * k;
        const rest = p.pB.distanceTo(p.pA) || 1, flare = Math.max(0, p.r2 - p.r1) / rest;
        Ls = L * g;
        // (the gathered cone's half-angle, less a margin for the arm's girth -- coming in with the rise: on an arm at or
        // below level a sleeve's upper piece stays on the arm, its last piece sags as it always did)
        lim = p.sag + Math.max(0, Math.atan(flare / g) - .08 - p.sag) * k;
      }
      const th = Math.acos(Math.max(-1, Math.min(1, -ay / L))), a = Math.min(th, lim), sn = Math.sin(th);
      let dx = ax / L, dy = ay / L, dz = az / L;
      if (a > 1e-4 && sn > 1e-3) {
        const ku = Math.sin(th - a) / sn, kw = Math.sin(a) / sn;
        dx *= ku; dy = dy * ku - kw; dz *= ku;
      } else if (a > 1e-4) {   // (an arm straight up: no plane to turn in -- it droops away from the body)
        const r = an.base * 3, ox = fA[j] - fA[r], oz = fA[j + 2] - fA[r], ol = Math.hypot(ox, oz) || 1;
        dx = Math.sin(a) * ox / ol; dy = Math.sign(dy || 1) * Math.cos(a); dz = Math.sin(a) * oz / ol;
      }
      _v.set(fA[j] + dx * Ls, fA[j + 1] + dy * Ls, fA[j + 2] + dz * Ls);
    }
    fB[j] = _v.x; fB[j + 1] = _v.y; fB[j + 2] = _v.z;
    // (a HELD arm's swing forward -- what a cloak's panel follows, LIFT -- is read from where it points in the figure's
    //  frame, and from where its forearm's end has gone: a position's forearm held out before the body over an upper arm
    //  hanging -- a statue's offering, a book carried -- lifts the cloth clear of the hand, not the hand through it)
    if (swing && held) {
      const e = _root.elements, ang = (k) => {
        const dx = fB[j] - fA[k], dy = fB[j + 1] - fA[k + 1], dz = fB[j + 2] - fA[k + 2];
        return Math.atan2(dx * e[0] + dy * e[1] + dz * e[2], -(dx * e[4] + dy * e[5] + dz * e[6]));
      };
      swing[i] = ang(j);
      if (p.parentIdx >= 0 && an.pose[p.parentIdx]) swing[p.parentIdx] = Math.max(swing[p.parentIdx], ang((an.base + p.parentIdx) * 3));
    }
    if (p.r2 < 0) {
      _v.copy(p.pC).applyMatrix4(world);
      fC[j] = _v.x; fC[j + 1] = _v.y; fC[j + 2] = _v.z;
    }
  }
  if (an.sculpted || an.sculpts) {   // a SCULPTED body (bodies.js) is skinned to these frames: kept on the animal, the next figure overwrites _mats (sculpts: the bodies inside a bigger figure -- a mount under its rider)
    const bm = an._bm?.length === parts.length * 16 ? an._bm : (an._bm = new Float32Array(parts.length * 16));
    for (let i = 0; i < parts.length; i++) bm.set(_mats[i].elements, i * 16);
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
  if (an.flyT !== undefined) an.fly = (an.fly ?? 0) + Math.max(-dt * FLIGHT.ease, Math.min(dt * FLIGHT.ease, an.flyT - (an.fly ?? 0)));   // (taking off, landing: FLIGHT)
  if (an.uprightT !== undefined) an.upright = (an.upright ?? 0) + Math.max(-dt * 2.5, Math.min(dt * 2.5, an.uprightT - (an.upright ?? 0)));   // (UPRIGHT: up in under half a second)
  if (an.restT !== undefined) an.rest = (an.rest ?? 0) + Math.max(-dt * 1.1, Math.min(dt * .35, an.restT - (an.rest ?? 0)));   // (lying down slowly; getting up quicker)
}
