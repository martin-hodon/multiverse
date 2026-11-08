// A SCULPTED CREATURE'S DEFINITION (2026-11-04): `"kind": "sculpt"` (assets/creatures/**.json) -- its body one surface,
// a field of smooth shapes (sculpt.js) made into a mesh and skinned to its bones (bodies.js draws it), not a set of
// pills the shell engine sweeps. This file is data only (no three.js): it turns the definition into what every engine
// takes -- a part list, but every part a BONE (posed, never drawn: the walk, the IK legs, the head's turn are the
// skeleton's own, skeleton.js) -- and hands the shape on as `def.sculpted`.
// And (sculptOf, below) it CONVERTS any creature still made of parts: the same parts become its bones, their shapes
// the field's primitives.
//
//   skeleton: { body: [x, y, z] (the root bone: the trunk's middle), length, girth (the root's own capsule: what riders
//               and collisions read as the body),
//               head: { at: [x, y, z] (its pivot: where the head turns), turn (idle yaw, degrees), r },
//               legs: { front: [hipX, hipY, hipZ], hind: [...], ankle (its height off the ground), knee (the upper bone's
//                       share of hip-to-ankle, default .5), kneeF, kneeH (+1 bends forward, -1 back), bend: [front, hind]
//                       (the bones that much longer than the reach, so they fold a little standing), radii: [hip, knee,
//                       ankle], foot: [half length, half height, half width], color, footColor, k (the thigh's blend
//                       into the body) } -- the legs' shapes are made from these, on their bones }
//   shape: [ primitives (sculpt.js: sphere, ell, cone, tube, box; k, op), each with color, bone (an id: body, head,
//            legFLu ...; default body), wet (a shine: a nose), coat (true: the coat grows here), mirror (true: and its
//            twin across z, on the twin's bone: ...L/...R, FL/FR, HL/HR), seat ({ from, out }: SEATED -- moved along the
//            line from `from` through its centre to where the surface of the shapes that are not seated is, then `out`
//            of its size beyond: an ear set ON the head however much the head swelled where it was blended) ]
//   eyes: { at: [x, y, z] (about where, on the head -- found ON its surface along the line from `from`), from, r, color,
//           sink (of its radius into the head), socket (the hollow round it, x its radius), lid (that hollow's colour) }
//           -- mirrored; eyeballs of their own, set into the head's surface, so they can never float off it (iris,
//           pupil: "round" | "slit" | "bar" -- the eyeball ringed in them round its front)
//   coat: { gap, len, r, sides, lean, vary, skirt, drop, face, rise, tip, dark, darkTip, skin, bands ([[f, colour], ...]: sharp
//           bands along each quill, the colour stepping at each fraction f) } -- quills (bodies.js); a shape's `coat` a
//           number over 1: the quills there that many times longer (a crest, a fan); fan, fanAt (where the coat is over
//           fanAt, the lean drops by fan x the excess: the quills raised -- a rump's fan), sparse (that share dropped on a
//           vertical side, thinning the coat down the flanks)
//   mesh: { cell (the grid, metres), tris: [near, far] (budgets), far (metres: the far mesh past it) }
//
// THE SCULPT OVERLAY (2026-11-04, docs/engines.md "the sculpt overlay"): a CONVERTED creature (a rig of parts, any kind)
// may say how its sculpted body is shaped instead of taking its parts' pills -- `"sculpt": { ... }` in the species JSON
// or its frame (merged as usual: arrays of objects with an `id` merge by id, so a species can retouch a frame's shape).
// Resolved by creatures.js like the rest (colour refs "@body", expressions "0.3*s"), carried through buildCreature,
// scaled with its young (geom.js scaleDef -> sculptScale: every length in it, none of the directions)
//   shape: [ the field's primitives, written in the REST frame (x forward, y up, z left, metres) as the rig stands:
//            type sphere { c, r } | ell { c, r: [rx, ry, rz], rot: [deg x, y, z] } | cone { a, b, ra, rb } |
//            tube { pts: [[x, y, z, r], ...] } | box { c, r } | tri { a, b, c, r } | feathers { rows } (below) |
//            membrane (docs/engines.md) | horn | fin (SHARP PARTS, below: never in the field) | whiskers (below) |
//            sweep (A LONG NECK OR A THIN TAIL as ONE smooth tube, docs/engines.md "Sweeps": sculpt.js prepareSweep) {
//              pts: [[x, y, z, r], ...] (a centripetal Catmull-Rom spline through them, the radius a monotone cubic
//              along its arc: no beads where tubes overlapped), bones: [ the chain it rides, root first: "neck",
//              "neck2", "neck3" ] (each point skinned between the two bones whose joints it lies between, eased;
//              "body" first: its root handed from the body to the neck, not torn off it when the neck turns),
//              blend (how wide that hand-off is, x the radius: default 1), knotsAt: [share, ...] (where along it, as
//              shares of its length, each later bone takes over, in place of at its joint: on the rest curve's bends,
//              so a turned bone carries a straight stretch; nothing moves at rest), spread (each hand-off widened to
//              that share of the stretch to its nearer neighbour: the turn shared out along it -- a neck held out
//              straight in flight, tools/creaturegen/sweep/flynecks.py), aspect (an elliptic section: its depth
//              along `up` over its width, default 1; per point as a fifth number), up (where the section's depth
//              points at the root: default [0, 1, 0], carried along without twisting), end: "point" (the radius eased
//              to 0 at its last point: a tail to a tip; otherwise its end is rounded), bands: [[s0, s1, colour], ...] (rings of colour between those
//              shares of its length: a ringed tail, a dark tip), bandEdge (their soft edge, metres), thin (cells:
//              where its radius falls under that many grid cells it is drawn as an exact tube, sharp.js sweepMesh,
//              joined into the field part over 2 radii; default 2) };
//            bone (the rig bone it rides, default body: an unknown one throws, listing them all), k (its blend, default
//            0), kc (its paint's, default k x paint), op: "sub" (carved, after everything) | "paint" (no shape: the surface inside it takes its colour, kc either side of its edge -- a snake's rings and saddles), color, wet, hair, coat,
//            fleece, mirror (and its twin across z on the twin bone), seat (as above), id (to be merged by);
//            pat (a pattern by name: stripes, zebra, rosettes, spots, giraffe ...) laid in frame "body" (the animal's:
//            one pattern over all the trunk's shapes) or a frame of its own { o (default: its bone's joint), u (what the
//            pattern runs across: stripes are bands across u), v (where round it is measured from: the stripe's root;
//            default up, or a limb's outer side), r (the girth it is drawn for) } -- shapes written with the same frame
//            share it, and paint as one; a vertex paints up to THREE frames at once (bodymesh.js patternsMesh: a
//            cat's cheek, skull and neck below the ear), so four meeting within one triangle still tear there;
//            any point may name a JOINT of the rig: "$legFLl" (the bone's origin: knee, hip, the head's pivot),
//            "$legFLl.end" (its segment's far end), "$tail1.mid", "$snout.a" / ".b", or [ "$head", dx, dy, dz, (r) ] ]
//   keep: [ regular expressions (whole ids) of the rig's parts still drawn as they were: "tail\\d*", "horn.*" ]
//   eyes: { at, from, r, iris, pupil, color, sink, socket, lid, bone (default head) } -- as above, mirrored; without it
//         the rig's own eyes are found on the new head. Or a list of them (a hydra's heads), each with mirror: false to
//         stand alone
//   feathers: false (a bird's wings and tails stay plates instead of becoming feathers: birdFeathers below)
//   shade: { back, belly (colours, or a number under 4: that factor of `on`, so a coat variant keeps its hue), k (the crossfade's half-width, metres: default half the trunk's girth), at (where it
//           is even, metres up from the root joint: default 0, the trunk's middle), up (default [0, 1, 0]), mode: "mul"
//           (default: every vertex scaled by tone / `on`, so markings keep their contrast) | "mix" (only the coat's own
//           colour replaced, by how near the vertex's paint is to `on`: amount (default 1), tol (default .25, linear rgb)),
//           on (the coat colour it is relative to: default the colour of the biggest shapes), low (a tone the legs go to
//           below lowAt, metres from the root joint: default 1.3 girths down -- a pale belly over legs of the coat's colour) } -- COUNTERSHADING: the
//           painted colour crossfaded from the back's tone on top to the belly's below, by rest-pose height (bodymesh.js
//           shadeOf); opt-in, nothing changes without it
//   paint (the share of k its paint blends by, default .5), patScale (the coat pattern's size against a tiger's: default
//   from the root's girth), mesh: { cell, tris, far, anchor, focus: { boneId: factor } -- that bone and those below it kept
//   factor times finer by the simplifier: a face, a paw; symmetric: true | false -- meshed as a half and reflected, or
//   not, said outright instead of detected from the shapes: sculpt.js "THE MIRROR" }, coat (quills, as above)
//   Rig proportions are the frame's own params (legs, tail, head ... in the species JSON over the frame's: defs.js merge)
// FEATHERS (a shape, or made from a bird's plates): { rows: [ { at, dir | to, len, w, bone, up } ...] (the row's root
//   edge, from the first row to the last: the blades between are interpolated, and skinned between the two rows' bones),
//   n (blades), outline: "flight" | "round" | "train", up, camber, curve, lift, stagger, stack, vary, jitter, seed,
//   color (at the root) and tip (at the tip), bars: { n, dark }, ocellus: { at (along it), r (of its half-width) } (an
//   eye: the peacock's) } -- bodymesh.js featherMesh; the vane's fine work per pixel (coatpat.js featherOf)
// SHARP PARTS (2026-11-08, sharp.js; docs/engines.md "Sharp parts"): explicit meshes, never in the field, never blended,
//   skinned to their bone; `mirror`, `pat`, `wet`, `color`, `tip` / `tipAt` (the colour toward the point / rim) as any
//   shape's; points may name joints. The way to draw anything POINTED or EDGED -- a field shape's tip is a blob a cell
//   across and its thin edge a staircase.
// HORN { pts: [[x, y, z, r, (aspect)], ...] (a centreline: the first point buried in the body, the last the TIP -- its
//   radius forced to 0), up (the cross-section's height direction, default [0, 1, 0]), aspect (height / width, default
//   1), flat (0-1: the -up side flattened -- a bill's closing face), keel (a ridge on +up, a share of r), twist (degrees,
//   root to tip), sides (default 12), bone, bone2 + blend: [t0, t1] (the skin passing to bone2 along that share of its
//   length), fair (a ROOT FLARE: metres, or { r, skin }: the horn's surface the smooth union of it and the body where it
//   leaves the body -- a boss, a gum; `skin` the blend's share at which its paint is all the body's, default .3) }
//   -- horns, tusks, tines, claws, talons, nails, teeth, fangs, spikes, beaks and bills. `strand: true`: a HAIR (sharp.js
//   strandMesh: `sides` default 3, `n` segments past the skin default 3, the second point where it leaves the skin; near
//   mesh only unless `far`) -- what WHISKERS are made of
// WHISKERS { at (the pad's centre, its left one), rows, per, gap: [along, between rows], dir, fan: [top, bottom] (pitch,
//   degrees), sweep: [front, back] (degrees back), along, normal, len: [front, back], rowLen: [top, bottom], droop, curl, r, bury,
//   jitter, seed, color, tip, tipAt, bone (default head), mirror (default true) } -- a face's vibrissae, or a brow's: one
//   shape made into rows x per strand horns on the pad (whiskerStrands, below: every parameter there)
// FIN { root: [[x, y, z], ...] (a line buried in the body), edge: [[x, y, z, (b)], ...] (the free rim from root[0] round
//   to root[last]; b blunts it there: 2 a leading edge), corners (indices into edge kept sharp: a tip, a notch), thick
//   (the greatest thickness, metres, default 6% of its span), slope (the thickness gained per metre in from the rim,
//   default .3), face (the side it looks to), cup (a hollow on face, a share of the rim distance), camber, curl +
//   curlAt, inner (the face side's colour) + innerRim (metres of `color` round it), rim (metres: a band of rimColor --
//   default tip, else color -- round the rim on both faces) + rimAt (from that share of the way out), patFace ("back" |
//   "face": a pat on one face only), fair (THE JOIN: metres, or { r, sink, reach, color, edge }: each face near the body the
//   smooth union of it and the body's field -- a fillet grown out of the skin, its paint, wetness, normal and skin the
//   body's; the rim never faired, the fillet fading out within edge [.2, 1.5] r of it; round: opt-in, the rim rounded
//   into the body), swell ([t, len, slope]: thicker toward the root, t held 40% of len), grid ("flow": the inside solved
//   harmonic, columns curving with the outline), rootBy (c: the root shared out by rim length / (distance + c)), thickBy
//   ("rim": the raw rim distance; default a smooth one, no medial ridge), bone, rootBone + rootBlend, n (rim
//   samples, default 36), across (rows root to rim, default 7) } -- fins, flukes, flippers, ears, crests, frills, wattles
import { KINDS } from "./creatures.js";
import { sharpPoints } from "./sharp.js";
import { sweepCurve } from "./sculpt.js";

const sub = (a, b) => a.map((v, i) => v - b[i]);
// the bone a mirrored shape takes on the other side: legFLu -> legFRu, footHL -> footHR, earL -> earR, earLIn -> earRIn,
// wArmL -> wArmR (FL / HL anywhere, else the last capital L before a lower-case or "In" ending); a bone of the middle
// (body, head, tail) is its own twin
export const twinBone = (id) => (/[FH]L/.test(id) ? id.replace(/([FH])L/, "$1R") : id.replace(/L(?=(?:[a-z0-9]*|In)$)/, "R"));
const zv = (v) => [v[0], v[1], -(v[2] ?? 0), ...v.slice(3)];
const twin = (p) => {
  const z = zv;
  const q = { ...p, mirror: undefined, bone: twinBone(p.bone ?? "body") };
  if (p.c) q.c = z(p.c);
  if (p.a) q.a = z(p.a);
  if (p.b) q.b = z(p.b);
  if (p.pts) q.pts = p.pts.map(z);
  if (p.rot) q.rot = [-p.rot[0], -p.rot[1], p.rot[2]];   // (mirrored across z: the turns about x and y change sign)
  if (p.axes) q.axes = p.axes.map(z);
  if (p.seat?.from) q.seat = { ...p.seat, from: z(p.seat.from) };
  if (p.up) q.up = z(p.up);
  if (p.rows) q.rows = p.rows.map((r) => ({ ...r, at: z(r.at), dir: z(r.dir), ...(r.up ? { up: z(r.up) } : {}), bone: twinBone(r.bone ?? p.bone ?? "body") }));
  if (p.bones) { q.bones = p.bones.map(twinBone); q.tris = p.tris.map((v, i) => p.tris[i - i % 3 + (3 - i % 3) % 3]); }   // (a membrane: each vertex on its bone's twin, its faces wound back the other way)
  if (p.nrm) q.nrm = p.nrm.map(z);
  if (p.root) q.root = p.root.map(z);   // (a fin: its root line and rim, its face; a horn's second bone)
  if (p.edge) q.edge = p.edge.map(z);
  if (p.face) q.face = z(p.face);
  if (p.bone2) q.bone2 = twinBone(p.bone2);
  if (p.chain) q.chain = p.chain.map(twinBone);   // (a sweep's bones along it)
  if (p.twist) q.twist = -p.twist;   // (a horn's spiral: the mirror image turns the other way)
  if (p.rootBone) q.rootBone = twinBone(p.rootBone);
  if (p.patFrame) q.patFrame = { ...p.patFrame, o: z(p.patFrame.o), u: z(p.patFrame.u), v: z(p.patFrame.v) };
  if (p.seed !== undefined) q.seed = p.seed + 101;
  return q;
};
const xRange = (p) => {
  if (p.op === "sub") return null;
  if (p.type === "sphere") return [p.c[0] - p.r, p.c[0] + p.r];
  if (p.type === "ell" || p.type === "box") return [p.c[0] - Math.max(...p.r), p.c[0] + Math.max(...p.r)];
  if (p.type === "cone") return [Math.min(p.a[0] - p.ra, p.b[0] - p.rb), Math.max(p.a[0] + p.ra, p.b[0] + p.rb)];
  if (p.type === "tube" || p.type === "sweep") return [Math.min(...p.pts.map((q) => q[0] - q[3])), Math.max(...p.pts.map((q) => q[0] + q[3]))];
  if (p.type === "horn" || p.type === "fin") { const Q = sharpPoints(p); return [Math.min(...Q.map((q) => q[0] - q[3])), Math.max(...Q.map((q) => q[0] + q[3]))]; }
  return null;
};

export function sculpted(d) {
  const { name, skeleton: S, shape = [], eyes = null, coat = null, mesh = {}, gaits = {}, c, ...flags } = d;
  const R = S.body, parts = [], rest = [];
  const bone = (p, at) => { parts.push({ ...p, bone: true, color: 0 }); rest.push(at); };
  bone({ id: "body", parent: null, shape: "capsule", size: { r: S.girth ?? .03, len: S.length ?? .08 }, geomRot: [0, 0, 90], pos: R, bob: true }, R);
  if (S.head) bone({ id: "head", parent: "body", shape: "sphere", size: { r: S.head.r ?? .02 }, pos: sub(S.head.at, R),
                     ...(S.head.turn ? { anim: { axis: "y", deg: S.head.turn, speed: .3, phase: 0 } } : {}) }, S.head.at);
  const prims = [];
  let legLen = 0;
  if (S.legs) {
    const L = S.legs, ankle = L.ankle ?? .01, share = L.knee ?? .5, bend = L.bend ?? [1.008, 1.032];
    const [rH, rK, rA] = L.radii ?? [.012, .009, .007], foot = L.foot ?? [.015, .006, .009];
    [["FL", L.front, 1, L.kneeF ?? 1, 0], ["FR", L.front, -1, L.kneeF ?? 1, 1], ["HL", L.hind, 1, L.kneeH ?? -1, 2], ["HR", L.hind, -1, L.kneeH ?? -1, 3]].forEach(([tag, h, sz, side, i]) => {
      const hip = [h[0], h[1], h[2] * sz], reach = hip[1] - ankle, fold = bend[i < 2 ? 0 : 1];
      if (reach <= .005) throw new Error(`${name}: leg ${tag}: its hip (${hip[1]}) is not above its ankle (${ankle})`);
      const upper = reach * share * fold, lower = reach * (1 - share) * fold;
      if (i === 0) legLen = upper + lower;
      const knee = [hip[0], hip[1] - reach * share, hip[2]], ank = [hip[0], ankle, hip[2]];
      bone({ id: `leg${tag}u`, parent: "body", shape: "capsule", size: { r: rH * .5, len: upper }, pos: sub(hip, R), pivot: [0, -upper / 2, 0],
             ik: { leg: i, upper, lower, side, foot: ankle - R[1], phase: 0 } }, hip);
      bone({ id: `leg${tag}l`, parent: `leg${tag}u`, shape: "capsule", size: { r: rK * .5, len: lower }, pos: [0, -upper, 0], pivot: [0, -lower / 2, 0],
             ik: { leg: i, follow: true } }, [hip[0], hip[1] - upper, hip[2]]);
      bone({ id: `foot${tag}`, parent: `leg${tag}l`, shape: "sphere", size: { r: rA * .5 }, pos: [0, -lower, 0], level: true }, [hip[0], hip[1] - upper - lower, hip[2]]);
      // (the leg's own shape on those bones: a round cone hip to knee, knee to ankle, the foot under the ankle)
      prims.push({ type: "cone", a: hip, b: knee, ra: rH, rb: rK, k: L.k ?? rH, color: L.color, bone: `leg${tag}u` },
                 { type: "cone", a: knee, b: ank, ra: rK, rb: rA, k: rK * .6, color: L.color, bone: `leg${tag}l` },
                 { type: "ell", c: [ank[0] + foot[0] * .35, foot[1], ank[2]], r: foot, k: rA * .8, color: L.footColor ?? L.color, bone: `foot${tag}` });
    });
  }
  // (the legs come AFTER the body's own shapes: they blend into a trunk that is there)
  const own = shape.flatMap((p) => (p.type === "whiskers" ? whiskerStrands(p) : [p])).flatMap((p) => (p.mirror ? [{ ...p, mirror: undefined }, twin(p)] : [p]));
  const sharp = own.filter((p) => SHARP.has(p.type)), own2 = own.filter((p) => !SHARP.has(p.type));
  const all = [...own2.filter((p) => p.op !== "sub" && p.op !== "paint"), ...prims, ...own2.filter((p) => p.op === "sub"), ...own2.filter((p) => p.op === "paint")];
  const ids = parts.map((p) => p.id);
  for (const p of [...all, ...sharp]) for (const b of [p.bone ?? "body", ...(p.bone2 ? [p.bone2] : []), ...(p.rootBone ? [p.rootBone] : []), ...(p.bones ?? [])]) if (!ids.includes(b)) throw new Error(`${name}: a shape hangs on "${b}", which is no bone (${ids.join(", ")})`);
  // (the bone named BEFORE the twin is made: a twin takes its bone's twin, and an eye's default is the head, not the body)
  const eye0 = eyes && { ...eyes, bone: eyes.bone ?? "head" };
  const eyeList = eye0 ? [eye0, twin({ ...eye0, c: eye0.at, a: eye0.from })].map((e, k) => ({ ...e, at: k ? e.c : e.at, from: k ? e.a : e.from })) : [];
  for (const e of eyeList) { delete e.c; delete e.a; }
  const xs = [...all, ...sharp].map(xRange).filter(Boolean), x0 = Math.min(...xs.map((r) => r[0])), x1 = Math.max(...xs.map((r) => r[1]));
  const Lg = legLen || .1;
  const walk = { offsets: [Math.PI / 2, 3 * Math.PI / 2, 0, Math.PI], stride: .32 * Lg, lift: .12 * Lg, bob: 0, ...(gaits.walk ?? {}) };
  const run = { offsets: [0, .6, Math.PI + .4, Math.PI + 1.0], stride: .48 * Lg, lift: .3 * Lg, bob: .06 * Lg, ...(gaits.run ?? {}) };
  // (a SWEEP: its skin along the bones it names -- their joints are the rest pose's -- and its too-thin end drawn as it is)
  const joint = (b) => rest[ids.indexOf(b.slice(1))];
  const swept = all.flatMap((p) => (p.type === "sweep" ? splitSweep(sweepSkin({ ...p }, joint, name, p.id ?? "?"), mesh.cell ?? .003) : [p]));
  const body = { name, bones: ids, rest, restInv: rest.map((r) => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -r[0], -r[1], -r[2], 1]), root0: R[1],
                 prims: swept.filter((p) => !p.detail), details: [...sharp, ...swept.filter((p) => p.detail)].map((p) => ({ ...p, pat: typeof p.pat === "string" ? PATS[p.pat] ?? 0 : p.pat })), eyes: eyeList, coat, mesh: { cell: .003, tris: [3000, 900], far: 4, ...mesh } };
  return { name, ...flags, walkNod: flags.walkNod ?? 0, rig: true, gaits: { walk, run }, probe: (x1 - x0) / 2, legLen, parts, sculpted: body };
}
KINDS.sculpt = sculpted;


// ======== EVERY OTHER CREATURE: its parts made its bones, their shapes the field's (2026-11-04) ========================
// A creature built of parts (mammals.js's rig, a bird's or a dragon's ready parts) keeps its skeleton exactly -- every
// part is posed as it was (IK legs, wings, tails, the head's turn, riders and shadows reading its ends) but drawn by
// none: its part's SHAPE, where the rest pose puts it, goes into the field instead --
//   a capsule or a cone -> a round cone between its ends; a scaled sphere -> a true ellipsoid in its frame (the shell
//   drew it as a capsule); a tube -> a spline through its Bezier, its radius eased and bulged; a triangle -> a slab
//   its rounding thick; a face mark (`dot`: an eye) -> an eyeball found on its parent's surface
// -- blended by its own k (no more than most of its radius: a big blend melted a small part away). What is too thin
// for the grid (a claw, a whisker, a horn's tip, a wing's membrane) is drawn as explicit geometry on its bone
// (`details`: a smooth cone, a two-sided plate), not lost between the samples. A `pat` goes with it (bodies.js paints
// it per pixel with the composite's own patternAt), `fleece` heaps its surface in lumps.
// Only definitions MARKED as creatures are converted (markSculpt: creatures.js, species.js) -- a person, a hybrid
// built of a person and an animal, a statue stay as they were. `"sculpt": false` on a definition keeps it too.
export const SCULPTABLE = new WeakSet();
export const markSculpt = (d) => { if (d && typeof d === "object" && d.sculpt !== false) SCULPTABLE.add(d); return d; };
const converted = new WeakMap();
const OFF = typeof location !== "undefined" && /[?&]sculpt=0/.test(location.search);   // (?sculpt=0: the parts as they were, to compare)
export function sculptOf(def) {
  if (def?.sculpted && !OWNER.has(def.sculpted)) OWNER.set(def.sculpted, def);
  if (OFF || !def || def.sculpted || !SCULPTABLE.has(def)) return def;
  if (!converted.has(def)) {
    let out = def;
    try { out = convert(def); }
    catch (e) { console.warn(`sculpt: ${def.name} stays as parts --`, e.message); }
    converted.set(def, out);
    if (out.sculpted) OWNER.set(out.sculpted, def);
  }
  return converted.get(def);
}
// A SCULPTED BODY INSIDE A BIGGER FIGURE (2026-11-08): a rider fused onto its mount, a cart's team of two under a yoke,
// a centaur's horse -- a definition made of an animal's parts AND more. Built as parts alone, the animal in it lost its
// sculpt (sculptOf converts only what species.js marked, and a figure put together from one is a new object): the
// riders, the teams and the centaur were drawn as plain pills while the loose horse beside them was a skinned body.
// Now the animal is converted on its own and its body carried as one of the figure's `sculpts`: { body, base } -- base
// the index of its first bone among the figure's parts (its parts, marked bones, in one block in their order) -- and the
// figure's other parts (the man, the yoke, the shafts) are drawn by the composite as before. bodies.js places each.
export function sculptPart(def) {   // -> { parts: its parts as bones, body } -- or null: not sculptable, drawn as it is
  const s = def && sculptOf(def);
  return s?.sculpted ? { parts: s.parts, body: s.sculpted } : null;
}
// ...and an overlay for a definition that has lost some of its bones (a centaur's horse without its head and neck): the
// shapes on the bones that are gone left out, and the eyes with them (they sat on the head)
export function trimOverlay(SC, ids) {
  if (!SC || typeof SC !== "object") return SC;
  const has = (b) => ids.has(b ?? "body");
  const shape = (SC.shape ?? []).filter((p) => [p.bone, p.bone2, p.rootBone, ...(p.bones ?? []), ...(p.chain ?? []), ...(Array.isArray(p.rows) ? p.rows.map((r) => r.bone) : [])].every(has));   // (rows: a feathered shape's, when a list)
  return { ...SC, shape, eyes: [] };
}
// A DEFINITION'S LOOKS (2026-11-08): the other definitions the same asset dresses -- its base, coats, variants and young
// (species.js, assets.html: creatures.js dressed) -- told to a definition by whoever made it, as a function (made only
// when asked). bodies.js asks familyOf(body) for their bodies: those whose shape is this body's share one shape build,
// and its colour boundaries are all of theirs (bodies.js "SHAPES SHARED"). A body with no family is its own.
const OWNER = new WeakMap();   // sculpted body -> the definition it was made from
const LOOKS = new WeakMap();   // definition -> () => [definitions]
export const lookFamily = (def, looks) => { if (def && typeof def === "object") LOOKS.set(def, looks); return def; };
export function familyOf(body) {
  const def = OWNER.get(body), looks = def && LOOKS.get(def);
  if (!looks) return [body];
  const out = [];
  for (const d of looks()) { try { const s = d && sculptOf(d); if (s?.sculpted) out.push(s.sculpted); } catch { /* (a look that cannot be made: not one of the family) */ } }
  return out;
}

// 4x4 matrices, column-major (as three keeps them)
const M4 = {
  mul(A, B) { const o = new Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) { let v = 0; for (let k = 0; k < 4; k++) v += A[k * 4 + r] * B[c * 4 + k]; o[c * 4 + r] = v; } return o; },
  // T(pos) R(euler XYZ, radians) S(scale) -- three's makeRotationFromEuler, then setPosition, then scale
  trs(p, e, s) {
    const a = Math.cos(e[0]), b = Math.sin(e[0]), c = Math.cos(e[1]), d = Math.sin(e[1]), E = Math.cos(e[2]), f = Math.sin(e[2]);
    const ae = a * E, af = a * f, be = b * E, bf = b * f;
    const R = [c * E, af + be * d, bf - ae * d, -c * f, ae - bf * d, be + af * d, d, -b * c, a * c];
    return [R[0] * s[0], R[1] * s[0], R[2] * s[0], 0, R[3] * s[1], R[4] * s[1], R[5] * s[1], 0, R[6] * s[2], R[7] * s[2], R[8] * s[2], 0, p[0], p[1], p[2], 1];
  },
  pt(M, v) { return [0, 1, 2].map((r) => M[r] * v[0] + M[4 + r] * v[1] + M[8 + r] * v[2] + M[12 + r]); },
  dir(M, v) { return [0, 1, 2].map((r) => M[r] * v[0] + M[4 + r] * v[1] + M[8 + r] * v[2]); },
  inv(m) {   // a general inverse (the rest frames may carry a scale)
    const o = new Array(16), [a00, a01, a02, a03, a10, a11, a12, a13, a20, a21, a22, a23, a30, a31, a32, a33] = m;
    const b00 = a00 * a11 - a01 * a10, b01 = a00 * a12 - a02 * a10, b02 = a00 * a13 - a03 * a10, b03 = a01 * a12 - a02 * a11, b04 = a01 * a13 - a03 * a11, b05 = a02 * a13 - a03 * a12;
    const b06 = a20 * a31 - a21 * a30, b07 = a20 * a32 - a22 * a30, b08 = a20 * a33 - a23 * a30, b09 = a21 * a32 - a22 * a31, b10 = a21 * a33 - a23 * a31, b11 = a22 * a33 - a23 * a32;
    const det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06, id = 1 / det;
    o[0] = (a11 * b11 - a12 * b10 + a13 * b09) * id; o[1] = (a02 * b10 - a01 * b11 - a03 * b09) * id; o[2] = (a31 * b05 - a32 * b04 + a33 * b03) * id; o[3] = (a22 * b04 - a21 * b05 - a23 * b03) * id;
    o[4] = (a12 * b08 - a10 * b11 - a13 * b07) * id; o[5] = (a00 * b11 - a02 * b08 + a03 * b07) * id; o[6] = (a32 * b02 - a30 * b05 - a33 * b01) * id; o[7] = (a20 * b05 - a22 * b02 + a23 * b01) * id;
    o[8] = (a10 * b10 - a11 * b08 + a13 * b06) * id; o[9] = (a01 * b08 - a00 * b10 - a03 * b06) * id; o[10] = (a30 * b04 - a31 * b02 + a33 * b00) * id; o[11] = (a21 * b02 - a20 * b04 - a23 * b00) * id;
    o[12] = (a11 * b07 - a10 * b09 - a12 * b06) * id; o[13] = (a00 * b09 - a01 * b07 + a02 * b06) * id; o[14] = (a31 * b01 - a30 * b03 - a32 * b00) * id; o[15] = (a20 * b03 - a21 * b01 + a22 * b00) * id;
    return o;
  },
};
const D2R = Math.PI / 180;
const len3 = (v) => Math.hypot(v[0], v[1], v[2]);
// (and the names the sculpted coats are drawn by, coatpat.js coatAt: 3 a tiger's stripes, 4 a zebra's, 5 a giraffe's
//  patches in their pale net, 18 rosettes, 21 solid spots, 24 a tabby's stripes in the coat's own darker tone -- "zebra", "giraffe" and "dots" say so; the old names stay)
const PATS = { leaf: 1, bark: 2, stripes: 3, bands: 4, spots: 5, wingspots: 6, scutes: 7, diamond: 8, scales: 17, rosettes: 18, twist: 19, barkH: 20, patches: 21, piebald: 22,
               zebra: 4, giraffe: 5, dots: 21, tabby: 24, osteoderms: 25,
               zebratone: 26, palespots: 27, trout: 28, mottle: 29, suckers: 30, clown: 31, rowscales: 32, finrays: 33,   // (the sea's, 2026-11-05: coatpat.js)
               ridges: 34, pangolin: 35, shag: 36, agouti: 37,   // (a horn's rings, a pangolin's plates; the apes' long hair, ticked fur: coatpat.js)
               anteater: 38, skunk: 39, coarse: 40,   // (a giant anteater's white-edged band, a skunk's white, a capybara's coarse hair: in the rest pose's space)
               orca: 41, humpback: 42, plesio: 43,   // (2026-11-06: an orca's black and white, a humpback's pleats and mottling, a plesiosaur's fine skin: in the rest pose's space)
               badger: 44, weasel: 45,   // (2026-11-06: a badger's striped face and grizzled grey, a weasel's russet and white: in the rest pose's space)
               dapple: 46, pinto: 47,   // (2026-11-06: a dapple grey's dapples, a piebald horse's patches: in the rest pose's space)
               seal: 60, greyseal: 61, walrus: 62,   // (2026-11-06: a harbour seal's spots, a grey seal's blotches, a walrus's wrinkled hide: in the rest pose's space)
               lynx: 63,   // (2026-11-06: a Eurasian lynx's spots, fine to bold: the rest pose's space at the body's patScale)
               panda: 64, qinling: 65,   // (2026-11-06: a giant panda's eye patches and shoulder band, black / a Qinling panda's brown: in the rest pose's space)
               koi: 66, rainbow: 67 };   // (2026-11-07: a koi's red patches on white over its row scales, a rainbow trout's black spots and pink band: coatpat.js)
// (paint: how sharply the shapes' colours meet, against how softly their shapes blend -- a muzzle's white has an edge)
export const CONVERT = { faces: 32000, maxCells: 6e6, thin: .8, sweepThin: 2, near: [1600, 3200], far: 4, lumps: [.18, .5], paint: .3,
                          focus: { head: 4 } };   // (mesh.focus unless the overlay says: the face kept finer than the back; {} none)

// a part's segment in its own frame (banner.js segmentFor, without three)
function segmentOf(part) {
  const s = part.scale ?? [1, 1, 1], { shape, size } = part;
  if (shape === "tri") return { a: size.a, b: size.b, c: size.c, r1: size.r ?? .03, tri: true };
  if (shape === "tube") return { a: size.a, b: size.b, c: size.c, r1: size.r1, r2: size.r2 ?? size.r1, bulge: size.bulge ?? 0, tube: true };
  if (shape === "sphere") return { ell: true, r: size.r };
  let dir = [0, 1, 0];
  if (part.geomRot) dir = M4.dir(M4.trs([0, 0, 0], part.geomRot.map((d) => d * D2R), [1, 1, 1]), dir);
  const rMul = (s[0] + s[1] + s[2]) / 3, half = shape === "cone" ? size.h / 2 : size.len / 2;
  const a = [dir[0] * half * s[0], dir[1] * half * s[1], dir[2] * half * s[2]], b = a.map((v) => -v);
  return shape === "cone" ? { a: b, b: a, r1: size.r * rMul, r2: Math.max(size.r * .12, Math.min(.008, size.r * .3)) * rMul }
                          : { a, b, r1: size.r * rMul, r2: (size.r2 ?? size.r) * rMul };
}

function convert(def) {
  const parts = def.parts, n = parts.length, index = new Map(parts.map((p, i) => [p.id, i]));
  // the REST frames: as skeleton.js chains them, standing still
  const W = [], f = [];
  for (let i = 0; i < n; i++) {
    const p = parts[i], pi = p.parent ? index.get(p.parent) : -1;
    const L = M4.trs(p.pos ?? [0, 0, 0], (p.rot ?? [0, 0, 0]).map((d) => d * D2R), p.scale ?? [1, 1, 1]);
    let w = pi >= 0 ? M4.mul(W[pi], L) : L;
    if (p.level && pi >= 0) { const at = [w[12], w[13], w[14]]; w = L.slice(); w[12] = at[0]; w[13] = at[1]; w[14] = at[2]; }
    W.push(w);
    let k = 1;
    for (let q = pi; q >= 0; q = parts[q].parent ? index.get(parts[q].parent) : -1) { const sc = parts[q].scale; if (sc) k *= (sc[0] + sc[1] + sc[2]) / 3; }
    f.push(k);
  }
  // THE OVERLAY (`sculpt`): the shapes an author wrote for this body, drawn instead of its parts' (all but those it keeps)
  const SC = def.sculpt && typeof def.sculpt === "object" ? scaleOverlay(def.sculpt, def.sculptScale ?? 1) : null;
  const keepRe = SC ? (SC.keep ?? []).map((k) => new RegExp(`^(?:${k})$`)) : [];
  const kept = (id) => !SC || keepRe.some((re) => re.test(id));
  const bird = def.print === "bird" && def.feathers !== false && SC?.feathers !== false;
  const shapes = [], eyes = [];
  // (a pattern laid in the ANIMAL's frame -- `frame: "body"`, the torso's pieces: stripes run on across their seams --
  //  as the shell lays it: along the root's axis from its middle, up, and across)
  const root = parts.findIndex((p) => !p.parent), rg = root >= 0 && !parts[root].bone ? segmentOf(parts[root]) : null;
  const animalFrame = rg && !rg.ell && !rg.tri ? (() => { const A = M4.pt(W[root], rg.a), B = M4.pt(W[root], rg.b), d = B.map((v, k) => v - A[k]), l = len3(d) || 1;
    return { o: A.map((v, k) => (v + B[k]) / 2), u: d.map((v) => v / l), r: (rg.r1 ?? .1) * f[root] }; })() : null;   // (r: one girth for the whole coat, or each piece's stripes would be spaced by its own)
  const local = (i, v) => { const p = parts[i], s = p.scale ?? [1, 1, 1], pv = p.pivot ?? [0, 0, 0]; return M4.pt(W[i], v.map((x, k) => pv[k] + x / s[k])); };
  const centreOf = (i) => { const g = segmentOf(parts[i]); return g.ell ? local(i, [0, 0, 0]) : local(i, g.a.map((v, k) => (v + g.b[k]) / 2)); };
  for (let i = 0; i < n; i++) {
    const p = parts[i];
    if (p.bone || p.hidden) continue;
    // (overlaid: only what it keeps -- and the rig's eyes when it authors none of its own)
    if (SC && !kept(p.id) && !(p.dot && !SC.eyes)) continue;
    const g = segmentOf(p), colour = p.color ?? 0x808080, pat = PATS[p.pat] ?? 0, base = { color: colour, bone: p.id, pat, part: i };
    if (p.dot) {   // a FACE MARK: an eye, found on the surface of what it is painted on
      const pi = p.parent ? index.get(p.parent) : i, at = local(i, g.a.map((v, k) => (v + g.b[k]) / 2));
      eyes.push({ at, from: centreOf(pi), r: g.r1 * f[i], bone: p.id, iris: p.dot.iris ?? null, pupil: p.dot.pupil ?? "round", color: colour, lidOf: pi });
      continue;
    }
    // (a BIRD's wings, tail and train: FEATHERS -- rows of real blades -- instead of the plate the part was)
    if (bird) { const fe = birdFeathers(p, i, g, local, f[i], colour); if (fe) { shapes.push(...fe); continue; } }
    const kk = (r) => Math.min((p.k ?? r * .5) * f[i], r * .8);
    if (g.ell) {
      const c = local(i, [0, 0, 0]), ax = [0, 1, 2].map((k) => M4.dir(W[i], [k === 0 ? g.r : 0, k === 1 ? g.r : 0, k === 2 ? g.r : 0]));
      const r = ax.map(len3), axes = ax.map((v, k) => v.map((x) => x / (r[k] || 1)));
      shapes.push({ ...base, type: "ell", c, r, axes, k: kk(Math.min(...r)), rmin: Math.min(...r), rmax: Math.max(...r) });
    } else if (g.tri) {
      const a = local(i, g.a), b = local(i, g.b), c = local(i, g.c), r = g.r1 * f[i];
      shapes.push({ ...base, type: "tri", a, b, c, r, k: kk(r), rmin: r, rmax: r });
    } else if (g.tube) {
      const a = local(i, g.a), b = local(i, g.b), c = local(i, g.c), N = 7, pts = [];
      for (let j = 0; j <= N; j++) {
        const t = j / N, u = 1 - t, q = [0, 1, 2].map((k) => u * u * a[k] + 2 * u * t * c[k] + t * t * b[k]);
        pts.push([...q, (g.r1 + (g.r2 - g.r1) * t + g.bulge * 4 * t * u) * f[i]]);
      }
      const rs = pts.map((q) => q[3]);
      shapes.push({ ...base, type: "tube", pts, per: 2, k: kk(Math.min(...rs)), rmin: Math.min(...rs), rmax: Math.max(...rs) });
    } else {
      const a = local(i, g.a), b = local(i, g.b), ra = g.r1 * f[i], rb = g.r2 * f[i];
      shapes.push({ ...base, type: "cone", a, b, ra, rb, k: kk(Math.min(ra, rb)), rmin: Math.min(ra, rb), rmax: Math.max(ra, rb) });
    }
    if (p.fleece) shapes[shapes.length - 1].fleece = true;
    if (p.frame === "body" && animalFrame) shapes[shapes.length - 1].animalFrame = animalFrame;
  }
  // ...the authored shapes: placed (their points may name the rig's joints), mirrored, checked against the bones; they
  // come BEFORE what is kept (horns, claws, a mane blend into a body that is there) and their carvings after it all
  let own = [];
  if (SC) {
    const joint = jointsOf(parts, index, W, local, centreOf);
    own = (SC.shape ?? []).flatMap((p) => (p.type === "whiskers" ? whiskerStrands({ ...p, at: point(p.at, joint) }) : [p]))   // (a face's whiskers: strands)
      .map((p, j) => placeShape(p, j, joint, def.name, animalFrame, SC))
      .flatMap((p) => (p.mirror ? [{ ...p, mirror: undefined }, twin(p)] : [p]));
    for (const p of own) {
      for (const b of [p.bone, ...(p.rows ?? []).map((r) => r.bone), ...(p.bones ?? []), ...(p.bone2 ? [p.bone2] : []), ...(p.rootBone ? [p.rootBone] : []), ...(p.chain ?? [])]) if (!index.has(b ?? "body"))
        throw new Error(`${def.name}: sculpt shape ${p.id ?? p.type} hangs on "${b}", which is no bone -- its bones are: ${parts.map((q) => q.id).join(", ")}`);
    }
  }
  // (frames written alike are ONE frame -- bodymesh.js crossfades only between different ones, and a vertex between two
  //  copies of the same would be painted twice over for nothing, or worse, disagree with its neighbour on which is which)
  const frames = new Map();
  for (const p of own) if (p.patFrame) {
    const key = JSON.stringify([p.patFrame.o, p.patFrame.u, p.patFrame.v, p.patFrame.r].flat().map((x) => +x.toFixed(5)));
    p.patFrame = frames.get(key) ?? (frames.set(key, p.patFrame), p.patFrame);
  }
  const all = [...own.filter((q) => q.op !== "sub" && q.op !== "paint"), ...shapes, ...own.filter((q) => q.op === "sub"), ...own.filter((q) => q.op === "paint")];   // (paints last: on the finished surface)
  if (!all.some((q) => q.type !== "feathers" && !SHARP.has(q.type))) throw new Error("nothing to sculpt");
  // THE GRID: as fine as makes about CONVERT.faces faces of surface (its area guessed from the shapes, overlaps and all)
  const solid = all.filter((q) => q.type !== "feathers" && q.type !== "membrane" && !SHARP.has(q.type) && q.op !== "sub" && q.op !== "paint");
  const area = solid.reduce((s, q) => s + areaOf(q), 0) * .55;
  let cell = SC?.mesh?.cell ?? Math.sqrt(2 * area / CONVERT.faces);
  const thick = solid.filter((q) => q.rmax >= cell * CONVERT.thin);
  const lo = [0, 1, 2].map((k) => Math.min(...thick.map((q) => boundsOf(q)[0][k]))), hi = [0, 1, 2].map((k) => Math.max(...thick.map((q) => boundsOf(q)[1][k])));
  const vol = (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2]);
  if (!SC?.mesh?.cell && vol / cell ** 3 > CONVERT.maxCells) cell = Math.cbrt(vol / CONVERT.maxCells);
  const prims = [], details = [];
  for (const q of all) {
    if (q.type === "feathers" || q.type === "membrane" || SHARP.has(q.type)) { details.push(q); continue; }
    if (q.type === "sweep") {   // (a SWEEP: in the field where the grid can draw it, its too-thin end drawn as it is -- splitSweep)
      for (const h of splitSweep(q, cell)) if (h.detail) details.push(h); else prims.push({ ...h, kc: h.kc ?? h.k * CONVERT.paint });
      continue;
    }
    if (q.op !== "sub" && q.op !== "paint" && q.type !== "box" && q.rmax < cell * CONVERT.thin) {   // too thin for the grid: drawn as it is
      if (q.rmax > cell * .15 || q.type === "tri") details.push(q);
      continue;
    }
    const pr = { ...q, kc: q.kc ?? q.k * CONVERT.paint };
    if (q.fleece) pr.lumps = q.fleece.size ? { amp: q.fleece.amp, size: q.fleece.size }   // (`fleece: {amp, size}` in metres: a fine fur's tips)
      : { amp: q.rmin * CONVERT.lumps[0], size: q.rmin * CONVERT.lumps[1] };
    prims.push(pr);
  }
  const ext = Math.max(hi[0] - lo[0], hi[2] - lo[2]) / 2;
  const near = Math.round(Math.min(CONVERT.near[1], Math.max(CONVERT.near[0], 1000 + 22 * prims.length)));
  // (the authored eyes: like the hedgehog's, mirrored -- on the head unless they say)
  let eyeList = eyes.map((e) => ({ ...e, lid: darker(parts[e.lidOf]?.color ?? 0x404040, .55), sink: .3, socket: 1.18 }));
  if (SC?.eyes) {
    const joint = jointsOf(parts, index, W, local, centreOf), P = (v) => (v == null ? v : point(v, joint));
    // (a list of them for a beast of many heads, 2026-11-07: each mirrored unless it says `mirror: false`)
    eyeList = [];
    for (const E of [SC.eyes].flat()) {
      const { mirror = true, ...e } = E;
      const e0 = { sink: .3, socket: 1.18, ...e, bone: e.bone ?? "head", at: P(e.at), from: P(e.from) };
      if (!index.has(e0.bone)) throw new Error(`${def.name}: sculpt eyes on "${e0.bone}", which is no bone`);
      if (e0.lid == null) e0.lid = darker(parts[index.get(e0.bone)]?.color ?? 0x404040, .55);
      eyeList.push(e0);
      if (mirror) eyeList.push({ ...e0, bone: twinBone(e0.bone), at: zv(e0.at), from: e0.from && zv(e0.from) });
    }
  }
  // (the size its coat patterns are laid at: a leopard's rosettes are a leopard's, a cub's the same number on a smaller
  //  coat -- by the root's girth against a tiger's, or as the definition says)
  const rootR = rg ? (rg.ell ? rg.r : rg.r1) * f[root] : PAT_GIRTH;
  const given = SC?.patScale ?? def.patScale;
  const patScale = given != null ? given * (def.sculptScale ?? 1) : Math.min(3, Math.max(.2, rootR / PAT_GIRTH));
  const M = SC?.mesh ?? {};
  const sculpted = {
    name: def.name, bones: parts.map((p) => p.id), rest: W.map((w) => [w[12], w[13], w[14]]), restInv: W.map(M4.inv), root0: parts[0]?.pos?.[1] ?? 0,
    prims, details, eyes: eyeList, patScale,
    ...(SC?.shade ? { shade: { ...SC.shade, o: root >= 0 ? [W[root][12], W[root][13], W[root][14]] : [0, 0, 0], r: rootR } } : {}),
    ...(SC?.mottle ? { mottle: SC.mottle } : {}),   // (the vertex colours' mottle, bodymesh.js MOTTLE: a big body's own)
    coat: SC?.coat ?? null, mesh: { cell, tris: M.tris ?? [near, Math.round(near / 3)], far: M.far ?? Math.max(CONVERT.far, 14 * ext), ...(M.anchor !== undefined ? { anchor: M.anchor } : {}),
            ...(M.symmetric !== undefined ? { symmetric: M.symmetric } : {}),
            ...focusSpec(M.focus === undefined ? CONVERT.focus : M.focus, parts) },
  };
  const out = { ...def, parts: parts.map((p) => (p.bone ? p : { ...p, bone: true })), sculpted };
  return out;
}
// mesh.focus, { boneId: factor } -> { bone index: factor }: each named bone and everything below it (a head's jaw,
// ears, nose) kept that many times finer by the simplifier; a deeper name overrides its ancestor's
function focusSpec(focus, parts) {
  const f = focus ? focusOf(focus, parts) : {};
  return Object.keys(f).length ? { focus: f } : {};
}
function focusOf(focus, parts) {
  const ids = parts.map((p) => p.id), par = new Map(parts.map((p) => [p.id, p.parent])), out = {};
  ids.forEach((id, i) => {
    for (let b = id; b != null; b = par.get(b)) if (focus[b] != null) { if (focus[b] !== 1) out[i] = focus[b]; break; }
  });
  return out;
}
// (a tiger's trunk: the girth its coat patterns are drawn for -- bodymesh.js scales the others' by theirs)
export const PAT_GIRTH = .28;

// ---- the overlay's pieces ----------------------------------------------------------------------------------------
// its numbers at the definition's size (a young one's: geom.js scaleDef) -- every length, none of the directions
const GEO = new Set(["c", "a", "b", "pts", "r", "ra", "rb", "k", "kc", "round", "at", "lowAt", "from", "to", "len", "w", "lift", "stagger", "gap", "cell", "o", "thick",
                     "root", "edge", "innerRim", "rim", "bury"]);   // (a fin's root line and rim, its bands of rim colour; `thick` above)
const sclNum = (v, f) => (typeof v === "number" ? v * f : Array.isArray(v) ? v.map((x) => sclNum(x, f)) : v);
function scaleOverlay(o, f) {
  if (f === 1) return o;
  const walk = (v) => {
    if (Array.isArray(v)) return v.map(walk);
    if (!v || typeof v !== "object") return v;
    const out = {};
    for (const [k, x] of Object.entries(v)) out[k] = GEO.has(k) || (k === "fair" && typeof x === "number") ? sclNum(x, f)
      : k === "swell" && Array.isArray(x) ? x.map((y, i) => (i < 2 ? y * f : y)) : walk(x);   // (a fin's `fair`: its radius, or { r, ... })
    return out;
  };
  return walk(o);
}
// THE RIG'S JOINTS, by name, for the authored shapes' points: "$legFLl" the bone's own origin (the joint it turns
// about: a hip, a knee, the head's centre, a tail's root), "$legFLl.end" the far end of its part's segment (the next
// joint: the ankle), "$tail1.mid" its middle (a tube's: on its curve), "$snout.a" / "$snout.b" the segment's two ends
function jointsOf(parts, index, W, local, centreOf) {
  return (name) => {
    const [id, which = ""] = name.slice(1).split(".");
    const i = index.get(id);
    if (i === undefined) throw new Error(`sculpt: no joint "${name}" -- the bones are: ${parts.map((q) => q.id).join(", ")}`);
    const o = [W[i][12], W[i][13], W[i][14]];
    if (!which) return o;
    const g = segmentOf(parts[i]);
    if (which === "mid") {
      if (g.tube) { const a = local(i, g.a), b = local(i, g.b), c = local(i, g.c); return a.map((v, k) => .25 * v + .5 * c[k] + .25 * b[k]); }
      return centreOf(i);
    }
    if (g.ell) return local(i, [0, 0, 0]);
    const A = local(i, g.a), B = local(i, g.b);
    if (which === "a") return A;
    if (which === "b") return B;
    if (which === "end") return len3(A.map((v, k) => v - o[k])) > len3(B.map((v, k) => v - o[k])) ? A : B;
    throw new Error(`sculpt: "${name}": a joint is "$id", "$id.end", "$id.mid", "$id.a" or "$id.b"`);
  };
}
// a point as written: [x, y, z] (and whatever follows: a tube point's radius), or a joint "$id", or [ "$id", dx, dy, dz, ...]
function point(v, joint) {
  if (typeof v === "string" && v[0] === "$") return joint(v);
  if (Array.isArray(v) && typeof v[0] === "string" && v[0][0] === "$") { const J = joint(v[0]); return [J[0] + (v[1] ?? 0), J[1] + (v[2] ?? 0), J[2] + (v[3] ?? 0), ...v.slice(4)]; }
  return v;
}
const nrm3 = (v) => { const l = len3(v) || 1; return [v[0] / l, v[1] / l, v[2] / l]; };
const cross3 = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
// WHISKERS (2026-11-08): one shape for a face's vibrissae, made here into thin `horn` strands (strand: true -- sharp.js
// strandMesh: 3 sides, a few rings, an exact tip; drawn on the near mesh only), mirrored and skinned to the head. Details:
// never in the field, so the coats and variants of a species share its shape (bodies.js keys it on the field alone).
// at: the PAD's centre, a little under its skin (the left one, z > 0; or a joint, [ "$id", dx, dy, dz ]); the strands'
// roots a grid on the pad -- `rows` (default 4) of `per` (default 4; or a list, one a row, top first), `gap` [along the
// row fore and aft, between the rows] metres apart -- each buried `bury` (metres, default 4 r) back along its own line.
// dir (the fan's middle line, default [-.3, 0, 1]: out and a little back); each row's pitch from fan[0] (the top row's,
// degrees up) to fan[1] (the bottom's), each strand's sweep from sweep[0] (the row's front one, degrees back round the
// up axis) to sweep[1] (its back one); along (the way the rows run, default fore and aft square to dir); normal (the
// skin's at the pad: the roots' grid laid on its tangent plane, not square to dir); len [front, back] (metres, or one) times rowLen [top, bottom]; droop (the tip's
// drop, a share of its length -- a quadratic sag) and curl (its bend forward toward the snout, a share: a cat's arc);
// r (the root's radius, metres; the strand tapers to a point), jitter (degrees: each one a little off the grid),
// seed, sides, n, color, tip, tipAt, bone (default head), mirror (default true), id (the strands are id0_0, id0_1 ...)
export function whiskerStrands(w) {
  const at = w.at.slice(0, 3), per = [w.per ?? 4].flat(), rows = w.rows ?? (Array.isArray(w.per) ? per.length : 4);
  const gap = w.gap ?? [.003, .003], r = w.r ?? .0005, bury = w.bury ?? 4 * r, jit = (w.jitter ?? 3) * D2R;
  const [len0, len1] = [w.len ?? .05].flat().length > 1 ? w.len : [w.len ?? .05, w.len ?? .05];
  const [rl0, rl1] = w.rowLen ?? [1, 1], [fan0, fan1] = w.fan ?? [15, -25], [sw0, sw1] = w.sweep ?? [-10, 25];
  const d = nrm3(w.dir ?? [-.3, 0, 1]), up0 = [0, 1, 0], du = d[0] * up0[0] + d[1] * up0[1] + d[2] * up0[2];
  let u = nrm3(up0.map((v, k) => v - d[k] * du)), f = cross3(u, d);   // (up, and the fan's own forward)
  if (w.along) { const al = w.along, da = al[0] * d[0] + al[1] * d[1] + al[2] * d[2]; f = nrm3(al.map((v, k) => v - d[k] * da)); u = cross3(d, f); }   // (the rows run along this)
  // (the roots' grid on the skin's own tangent plane when its `normal` is given -- a muzzle narrowing toward the nose
  //  has its front roots no further out than its back ones -- else square to dir)
  const nn = w.normal ? nrm3(w.normal) : d, onPlane = (v) => { const t = v[0] * nn[0] + v[1] * nn[1] + v[2] * nn[2]; return nrm3(v.map((x, k) => x - nn[k] * t)); };
  const fr = onPlane(f), ur = onPlane(u);
  let seed = (w.seed ?? 1) * 2654435761 >>> 0;
  const rnd = () => { seed = (seed + 0x6D2B79F5) >>> 0; let t = seed; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296 * 2 - 1; };
  const lerp1 = (a, b, t) => a + (b - a) * t, ax = (v, s) => v.map((x) => x * s), plus = (...vs) => vs.reduce((a, b) => a.map((x, k) => x + b[k]));
  const out = [];
  for (let i = 0; i < rows; i++) {
    const ti = rows > 1 ? i / (rows - 1) : .5, np = per[Math.min(i, per.length - 1)];
    for (let j = 0; j < np; j++) {
      const tj = np > 1 ? j / (np - 1) : .5;
      const pitch = lerp1(fan0, fan1, ti) * D2R + rnd() * jit, sweep = lerp1(sw0, sw1, tj) * D2R + rnd() * jit;
      const h = plus(ax(d, Math.cos(sweep)), ax(f, -Math.sin(sweep))), dir = nrm3(plus(ax(h, Math.cos(pitch)), ax(u, Math.sin(pitch))));
      const L = lerp1(len0, len1, tj) * lerp1(rl0, rl1, ti) * (1 + .08 * rnd());
      const root = plus(at, ax(fr, gap[0] * ((np - 1) / 2 - j)), ax(ur, gap[1] * ((rows - 1) / 2 - i)));
      const du2 = u[0] * dir[0] + u[1] * dir[1] + u[2] * dir[2], down = nrm3(u.map((v, k) => -(v - dir[k] * du2)));
      const fd = f[0] * dir[0] + f[1] * dir[1] + f[2] * dir[2], fwd = nrm3(f.map((v, k) => v - dir[k] * fd));
      const pt = (t) => plus(root, ax(dir, L * t), ax(down, (w.droop ?? .12) * L * t * t), ax(fwd, (w.curl ?? 0) * L * t * t));
      out.push({ type: "horn", strand: true, id: `${w.id ?? "whisker"}${i}_${j}`, bone: w.bone ?? "head", mirror: w.mirror ?? true,
                 color: w.color ?? 0xf0f0e8, ...(w.tip != null ? { tip: w.tip, tipAt: w.tipAt ?? .5 } : {}),
                 ...(w.sides ? { sides: w.sides } : {}), ...(w.n ? { n: w.n } : {}), ...(w.far ? { far: true } : {}),
                 pts: [[...plus(root, ax(dir, -bury)), r], [...root, r], [...pt(1 / 3), r * .7], [...pt(2 / 3), r * .42], [...pt(1), 0]] });
    }
  }
  return out;
}
// an authored primitive made ready for the field: its points placed, its extent, its pattern and its paint's blend
function placeShape(p0, j, joint, name, animalFrame, SC) {
  const P = (v) => (v == null ? v : point(v, joint));
  const p = { ...p0, bone: p0.bone ?? "body", own: j };
  for (const k of ["c", "a", "b"]) if (p[k] !== undefined) p[k] = P(p[k]).slice(0, 3);
  if (p.pts && p.type !== "membrane") p.pts = p.pts.map((q) => { const v = P(q); if (v.length < 4) throw new Error(`${name}: a ${p.type} point needs its radius: ${JSON.stringify(q)}`); return v; });
  if (p.type === "fin") {   // (a sheet: its root line and its rim -- points or joints; a rim point may carry its bluntness)
    if (!(p.root?.length >= 2) || !(p.edge?.length >= 1)) throw new Error(`${name}: fin ${p.id ?? j} needs a root (2 points or more) and an edge`);
    p.root = p.root.map((q) => P(q).slice(0, 3)); p.edge = p.edge.map((q) => P(q).slice(0, 4));
    if ((p.corners ?? []).some((c) => !(c >= 0 && c < p.edge.length))) throw new Error(`${name}: fin ${p.id ?? j}: a corner out of range`);
  }
  if (p.type === "horn" && !(p.pts?.length >= 2)) throw new Error(`${name}: horn ${p.id ?? j} needs pts (2 or more: its root, ..., its tip)`);
  if (p.seat) p.seat = { ...p.seat, ...(p.seat.from ? { from: P(p.seat.from) } : {}) };
  const t = p.type;
  if (!["sphere", "ell", "cone", "tube", "sweep", "box", "tri", "feathers", "membrane", "horn", "fin"].includes(t)) throw new Error(`${name}: sculpt shape ${j} is a "${t}" -- the types are sphere, ell, cone, tube, sweep, box, tri, feathers, membrane, horn, fin`);
  if (t === "sweep") sweepSkin(p, joint, name, j);
  if (t === "membrane") patOf(p, P, animalFrame);   // (its coat pattern, as any shape's: it returns before the rest)
  if (t === "membrane") {   // (a skin stretched between bones, each vertex on its own: bodymesh.js membraneMesh)
    const n = p.pts?.length ?? 0;
    if (!n || !p.tris?.length || p.tris.length % 3 || p.skin?.length !== n || !p.bones?.length) throw new Error(`${name}: membrane ${p.id ?? j} needs pts, tris (3 a face), bones and a skin entry a point`);
    if (p.tris.some((v) => v < 0 || v >= n) || p.skin.some((e) => (Array.isArray(e) ? [e[0], e[1]] : [e]).some((b) => !(b >= 0 && b < p.bones.length)))) throw new Error(`${name}: membrane ${p.id ?? j}: a face or a skin entry out of range`);
    if (p.nrm && p.nrm.length !== n) throw new Error(`${name}: membrane ${p.id ?? j}: nrm needs one normal a point`);
    p.rmin = p.rmax = p.r ?? .002; p.color = p.color ?? 0x808080; p.k = 0; p.kc = 0;
    return p;
  }
  if (t === "feathers") {
    if (!p.rows?.length) throw new Error(`${name}: feathers ${p.id ?? j} need rows`);
    p.rows = p.rows.map((r) => {
      const at = P(r.at), dir = r.to != null ? P(r.to).slice(0, 3).map((v, k) => v - at[k]) : r.dir;
      if (!dir) throw new Error(`${name}: feathers ${p.id ?? j}: a row needs a dir or a to`);
      return { ...r, at: at.slice(0, 3), dir: nrm3(dir), len: r.len ?? len3(dir), bone: r.bone ?? p.bone, to: undefined };
    });
    p.pat = 23;
    return p;
  }
  if (t === "ell" && p.rot) {   // (its frame as three axes: the detail mesher and a mirror read them as the field does)
    const R = M4.trs([0, 0, 0], p.rot.map((d) => d * D2R), [1, 1, 1]);
    p.axes = [[R[0], R[1], R[2]], [R[4], R[5], R[6]], [R[8], R[9], R[10]]];
    delete p.rot;
  }
  const rs = t === "sphere" ? [p.r] : t === "ell" || t === "box" ? p.r : t === "cone" ? [p.ra, p.rb] : t === "tube" || t === "horn" || t === "sweep" ? p.pts.map((q) => q[3]) : t === "fin" ? [p.thick ?? .01] : [p.r ?? .01];
  p.rmin = Math.min(...rs); p.rmax = Math.max(...rs);
  p.k = p.k ?? 0;
  if (p.kc === undefined) p.kc = p.k * (SC.paint ?? .5);
  p.color = p.color ?? 0x808080;
  patOf(p, P, animalFrame);
  return p;
}
// A SWEEP's SKIN (sculpt.js sweepCurve): `bones` -- the rig's chain it runs along (neck, neck2, neck3), or one `bone` --
// made `chain` and `knots`: where along it (metres of arc) each bone hands over to the next -- the foot on the curve of
// that bone's joint, or `knotsAt` (shares of its length) -- and over how far either side (`blend`, a share of the
// radius there: default 1; `spread` widens each to that share of the gap to its nearer neighbour)
function sweepSkin(p, joint, name, j) {
  if (!(p.pts?.length >= 2)) throw new Error(`${name}: sweep ${p.id ?? j} needs pts (2 or more)`);
  const chain = p.chain ?? p.bones ?? [p.bone ?? "body"];
  p.chain = chain; p.bone = chain[0]; delete p.bones;
  if (chain.length < 2) { p.knots = []; return p; }   // (one bone: all of it on that bone)
  const C = sweepCurve(p), knots = [];
  for (let b = 1; b < chain.length; b++) {
    const J = joint("$" + chain[b]);
    let best = Infinity, s = 0, r = 0;
    // (knotsAt: where along it -- shares of its length -- each hand-off is, said outright instead of at the bones'
    //  joints: a stretch rides its bone rigidly wherever the joint is, so the rest shape is the same either way, and a
    //  hand-off laid on the rest curve's own bend lets the pose undo it)
    if (p.knotsAt?.[b - 1] != null) { s = p.knotsAt[b - 1] * C.L; let i = 0; while (i + 1 < C.m && C.S[i + 1] < s) i++; r = C.R[i]; best = -1; }
    if (best >= 0) for (let i = 0; i + 1 < C.m; i++) {   // (the foot on the dense polyline)
      const A = C.X[i], B = C.X[i + 1], e = [0, 1, 2].map((k) => B[k] - A[k]), l2 = e[0] ** 2 + e[1] ** 2 + e[2] ** 2 || 1e-18;
      const t = Math.max(0, Math.min(1, ((J[0] - A[0]) * e[0] + (J[1] - A[1]) * e[1] + (J[2] - A[2]) * e[2]) / l2));
      const d = Math.hypot(J[0] - A[0] - e[0] * t, J[1] - A[1] - e[1] * t, J[2] - A[2] - e[2] * t);
      if (d < best) { best = d; s = C.S[i] + (C.S[i + 1] - C.S[i]) * t; r = C.R[i] + (C.R[i + 1] - C.R[i]) * t; }
    }
    if (knots.length && s <= knots[knots.length - 1][0]) throw new Error(`${name}: sweep ${p.id ?? j}: its bones' joints are not in order along it (${chain.join(", ")})`);
    knots.push([s, Math.max(1e-4, (p.blend ?? 1) * Math.max(r, C.L * .02))]);
  }
  // (spread: each hand-off widened to that share of the stretch to its nearer neighbouring knot -- or end -- so the turn
  //  between two bones is shared out along the whole stretch, not taken at the joint: an S-shaped neck at rest can lie
  //  straight aloft, its own curve undone by the turn growing along it)
  if (p.spread) knots.forEach((k, i) => { const a = k[0] - (i ? knots[i - 1][0] : 0), b = (i + 1 < knots.length ? knots[i + 1][0] : C.L) - k[0];
    k[1] = Math.max(k[1], p.spread * Math.min(a > 1e-3 ? a : b, b)); });
  p.knots = knots;
  return p;
}
// THE THIN END of a sweep: from where it stays thinner than `thin` cells (CONVERT.sweepThin) to its end -- a tail's
// last stretch, every pointed end -- drawn as it is (sharp.js sweepMesh: exact rings), not left to a grid that would
// draw it as a staircase and its point as a blob. The field keeps the rest, `cut` there, and shrunk a little under the
// stretch the two overlap (2 radii), so the drawn tube is the surface seen there. A sweep thin all along: all drawn.
// Its pieces, each `detail: true` or not.
export function splitSweep(q, cell) {
  const C = sweepCurve(q), thr = (q.thin ?? CONVERT.sweepThin) * cell;
  let i = C.m - 1;
  while (i > 0 && C.R[i - 1] < thr) i--;
  if (C.R[C.m - 1] >= thr) return [q];   // (thick to its end)
  if (i === 0) return [{ ...q, detail: true, from: 0 }];   // (thin all along)
  const sc = C.S[i], ov = Math.min(2 * C.R[i], sc * .5);
  return [{ ...q, cut: [0, sc], shrink: [sc - ov, sc - ov * .3], shrinkBy: .08 }, { ...q, detail: true, from: sc - ov }];
}
// a shape's coat pattern: its name made a number, its frame ("body": the animal's, or one of its own) placed
const SHARP = new Set(["horn", "fin"]);
function patOf(p, P, animalFrame) {
  if (typeof p.pat === "string") p.pat = PATS[p.pat] ?? 0;
  if (p.frame === "body" && animalFrame) p.animalFrame = animalFrame;
  else if (p.frame && typeof p.frame === "object") {   // a frame of its own for its pattern: { o, u (what the stripes run across), v (where they start from), r }
    const u = nrm3(p.frame.u ?? [1, 0, 0]), cz = (p.c ?? p.a ?? p.pts?.[0] ?? p.root?.[0] ?? [0, 0, 0])[2];
    // (v unsaid: up -- or, on a limb (u near the vertical, off the middle), its OUTER side, where a tiger's leg stripes are)
    const v0 = p.frame.v ?? (Math.abs(u[1]) < .7 ? [0, 1, 0] : Math.abs(cz) > 1e-3 ? [0, 0, Math.sign(cz)] : [1, 0, 0]), d = v0[0] * u[0] + v0[1] * u[1] + v0[2] * u[2];
    const v = nrm3(v0.map((x, k) => x - u[k] * d));
    // (o unsaid: the joint of the bone it rides -- so a leg's shapes, all written with the same frame, share one)
    p.patFrame = { o: P(p.frame.o ?? "$" + p.bone).slice(0, 3), u, v, r: p.frame.r ?? p.rmin ?? .05 };
  }
  delete p.frame;
}

// ---- A BIRD'S FEATHERS, from the plates it was drawn with (every bird improves without a line of its own) ---------
// a flapping wing's triangle (its tip the corner furthest out): flight feathers rooted along its leading edge, pointing
// back to its trailing edge and out past its tip, two rows of coverts over their roots, and the arm along the edge;
// a folded wing's (its tip the hindmost corner): the plate kept as the wing's body and its feathers laid over it, all
// sweeping back to the tip; a tail's triangle or cone: a fan of rectrices from its base; a train's plume: a fan of long
// slender feathers each ending in an eye (the peacock's)
function birdFeathers(p, i, g, local, f, colour) {
  const id = p.id, sub = (a, b) => a.map((v, k) => v - b[k]), add = (a, b, t = 1) => a.map((v, k) => v + b[k] * t), lerp = (a, b, t) => a.map((v, k) => v + (b[k] - v) * t);
  const D = (a, b) => len3(sub(a, b)), base = { type: "feathers", bone: id, part: i };
  const row = (at, to, w, extra = {}) => ({ at, dir: nrm3(sub(to, at)), len: D(to, at), w, bone: id, ...extra });
  const tone = (c, k) => darker(c, k);
  if (/^wing[LR]?$/.test(id) && g.tri) {
    const C3 = [local(i, g.a), local(i, g.b), local(i, g.c)], N0 = nrm3(cross3(sub(C3[1], C3[0]), sub(C3[2], C3[0])));
    const r = g.r1 * f;
    if (p.anim?.wing) {
      const ti = [0, 1, 2].reduce((a, b) => (Math.abs(C3[b][2]) > Math.abs(C3[a][2]) ? b : a), 0), T = C3[ti], [F, K] = C3.filter((_, k) => k !== ti).sort((a, b) => b[0] - a[0]);
      const up = N0[1] < 0 ? N0.map((v) => -v) : N0, span = D(T, F), chord0 = D(K, F);
      const LE = (u) => lerp(F, T, u), TE = (u) => lerp(K, T, u), at = (u, s) => lerp(LE(u), TE(u), s);
      const us = [0, .25, .5, .75, 1], n = 13, sp = span * .82 / (n - 1);
      const flight = us.map((u) => row(at(.82 * u, .16), add(TE(u), sub(T, F), .1 * u * u), Math.max(sp * .95, chord0 * .07)));
      const cov = us.map((u) => row(at(.86 * u, .05), at(.86 * u, .55), sp * 1.05));
      const les = us.map((u) => row(at(.86 * u, .0), at(.86 * u, .28), sp * .9));
      return [
        { ...base, rows: flight, n, outline: "flight", color: colour, tip: tone(colour, .55), camber: .1, curve: -.03, up, seed: i * 7 + 1 },
        { ...base, rows: cov, n: 11, outline: "round", color: colour, tip: tone(colour, .85), camber: .14, up, lift: chord0 * .012, seed: i * 7 + 2 },
        { ...base, rows: les, n: 10, outline: "round", color: tone(colour, 1.06), tip: colour, camber: .16, up, lift: chord0 * .024, seed: i * 7 + 3 },
        { type: "cone", a: F, b: LE(.86), ra: chord0 * .07, rb: chord0 * .035, k: chord0 * .05, color: colour, bone: id, pat: 0, part: i,
          rmin: chord0 * .035, rmax: chord0 * .07 },
      ];
    }
    const ti = [0, 1, 2].reduce((a, b) => (C3[b][0] < C3[a][0] ? b : a), 0), T = C3[ti], [F, K] = C3.filter((_, k) => k !== ti).sort((a, b) => b[1] - a[1]);
    const cz = (C3[0][2] + C3[1][2] + C3[2][2]) / 3, up = N0[2] * cz < 0 ? N0.map((v) => -v) : N0, lift = r * 1.08;
    const us = [0, .5, 1], n = 9, sp = D(F, K) / (n - 1);
    const flight = us.map((u) => { const R0 = lerp(F, K, u * .9); return row(lerp(R0, T, .3), add(T, sub(K, T), .22 * u), sp * 1.3); });
    const cov = us.map((u) => { const R0 = lerp(F, K, u * .85); return row(lerp(R0, T, .04), lerp(R0, T, .5), sp * 1.2); });
    return [
      { type: "tri", a: C3[0], b: C3[1], c: C3[2], r, k: Math.min((p.k ?? r * .5) * f, r * .8), color: tone(colour, .9), bone: id, pat: 0, part: i, rmin: r, rmax: r },
      { ...base, rows: flight, n, outline: "flight", color: colour, tip: tone(colour, .6), camber: .12, up, lift, seed: i * 7 + 1 },
      { ...base, rows: cov, n: 7, outline: "round", color: tone(colour, 1.04), tip: colour, camber: .16, up, lift: lift * 1.25, seed: i * 7 + 2 },
    ];
  }
  if (/^tail$/.test(id) && (g.tri || p.shape === "cone")) {
    let A1, A2, tipAt, up, side, spread, keep = null;
    if (g.tri) {
      const C3 = [local(i, g.a), local(i, g.b), local(i, g.c)], ti = [0, 1, 2].reduce((a, b) => (C3[b][0] < C3[a][0] ? b : a), 0);
      tipAt = C3[ti]; [A1, A2] = C3.filter((_, k) => k !== ti).sort((a, b) => b[2] - a[2]);
      const N0 = nrm3(cross3(sub(A2, A1), sub(tipAt, A1))); up = N0[1] < 0 ? N0.map((v) => -v) : N0;
      side = nrm3(sub(A1, A2)); spread = D(A1, A2) * .6;
    } else {
      const B0 = local(i, g.a), T0 = local(i, g.b), r1 = g.r1 * f, ax = nrm3(sub(T0, B0));
      side = cross3(ax, [0, 1, 0]); side = len3(side) < .1 ? [0, 0, 1] : nrm3(side);
      const u0 = cross3(side, ax); up = u0[1] < 0 ? u0.map((v) => -v) : u0;
      const L = D(T0, B0) * 1.12;
      spread = Math.max(r1 * 1.2, L * .22);
      A1 = add(B0, side, r1 * .7); A2 = add(B0, side, -r1 * .7); tipAt = add(B0, ax, L);
      keep = { type: "cone", a: B0, b: add(B0, ax, D(T0, B0) * .3), ra: r1, rb: r1 * .7, k: r1 * .4, color: colour, bone: id, pat: 0, part: i, rmin: r1 * .7, rmax: r1 };
    }
    const n = 12;
    const rows = [0, .25, .5, .75, 1].map((u) => {
      const R0 = lerp(A1, A2, u), at = lerp(R0, tipAt, .06), to = add(tipAt, side, (.5 - u) * 2 * spread);
      const rr = row(at, to, 0);
      rr.len *= 1 - .1 * (2 * u - 1) ** 2;
      return rr;
    });
    const wid = Math.max(D(A1, A2), spread * 1.4) / (n - 1) * 1.25;
    for (const rr of rows) rr.w = Math.max(wid, rr.len * .09);
    return [...(keep ? [keep] : []),
      { ...base, rows, n, outline: "round", color: colour, tip: tone(colour, .7), camber: .1, curve: .02, up, seed: i * 7 + 5, bars: p.bars ?? null }];
  }
  if (/^plume\d+$/.test(id) && g.tri) {
    const A = local(i, g.a), B = local(i, g.b), C = local(i, g.c), N0 = nrm3(cross3(sub(B, A), sub(C, A))), up = N0[0] < 0 ? N0.map((v) => -v) : N0;
    // (the plume's wedge opened a third wider each way: the plates stood apart, the feathers of one meet the next's)
    const n = 18, B1 = add(B, sub(B, C), .35), C1 = add(C, sub(C, B), .35), w = D(B1, C1) / n * 1.3, rows = [row(A, B1, w), row(A, C1, w)];
    return [{ ...base, rows, n, outline: "train", color: tone(colour, .8), tip: 0x5a7a2a, camber: .06, curve: .03, up, vary: .55, stagger: w * .1,
              ocellus: { at: .955, r: .88 }, seed: i * 13 + 3 }];
  }
  return null;
}
const darker = (c, k) => {
  const n = typeof c === "number" ? c : parseInt(String(c).replace("#", ""), 16);
  return (Math.round(((n >> 16) & 255) * k) << 16) | (Math.round(((n >> 8) & 255) * k) << 8) | Math.round((n & 255) * k);
};
function areaOf(q) {
  if (q.type === "sphere") return 4 * Math.PI * q.r * q.r;
  if (q.type === "box") { const [a, b, c] = q.r; return 8 * (a * b + b * c + a * c); }
  if (q.type === "ell") { const [a, b, c] = q.r, P = 1.6; return 4 * Math.PI * (((a * b) ** P + (a * c) ** P + (b * c) ** P) / 3) ** (1 / P); }
  if (q.type === "tri") { const u = q.b.map((v, k) => v - q.a[k]), w = q.c.map((v, k) => v - q.a[k]); return len3([u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]); }
  if (q.type === "tube" || q.type === "sweep") { let s = 0; for (let j = 1; j < q.pts.length; j++) s += 2 * Math.PI * (q.pts[j][3] + q.pts[j - 1][3]) / 2 * len3(q.pts[j].map((v, k) => v - q.pts[j - 1][k]).slice(0, 3)); return s; }
  const L = len3(q.a.map((v, k) => v - q.b[k])), r = (q.ra + q.rb) / 2;
  return 2 * Math.PI * r * L + 2 * Math.PI * (q.ra * q.ra + q.rb * q.rb);
}
function boundsOf(q) {
  const pts = q.type === "ell" || q.type === "sphere" ? [q.c.map((v) => v - q.rmax), q.c.map((v) => v + q.rmax)]
            : q.type === "box" ? [q.c.map((v) => v - len3(q.r)), q.c.map((v) => v + len3(q.r))]
            : q.type === "tri" ? [q.a, q.b, q.c].flatMap((P) => [P.map((v) => v - q.r), P.map((v) => v + q.r)])
            : q.type === "tube" || q.type === "sweep" ? q.pts.flatMap((P) => [P.slice(0, 3).map((v) => v - P[3]), P.slice(0, 3).map((v) => v + P[3])])
            : [q.a.map((v) => v - q.ra), q.a.map((v) => v + q.ra), q.b.map((v) => v - q.rb), q.b.map((v) => v + q.rb)];
  return [[0, 1, 2].map((k) => Math.min(...pts.map((P) => P[k]))), [0, 1, 2].map((k) => Math.max(...pts.map((P) => P[k])))];
}
