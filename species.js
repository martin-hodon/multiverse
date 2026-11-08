// Abstract animal definitions -- pure data, no rendering-engine imports.
// Any engine (banner.js SDF quads, instanced.js, composite.js)
// consumes the same part lists; a species is nothing but proportions,
// colors and hierarchy expressed in the shared primitive vocabulary
// (sphere, capsule, cone). Each part names its parent by id (root: null).
//
// UNITS: 1 = 1 meter. Species are authored either directly in meters
// (factor 1) or at a convenient working scale and run through scaleParts()
// with a factor that brings them to roughly real-world size, so an elephant
// genuinely dwarfs a cat and leg/head/body ratios stay plausible. The one
// deliberate cheat: eyes get a minimum radius (EYE_MIN_R) so they stay
// readable on small animals (now just a tiny safety floor: real sizes rule).
//
// NOTE: a leg's own foot reaches dropY - (len + r) below the body's local
// origin (capsule geometry extends len/2+r past its own center each way,
// and pivot=[0,-len/2,0] re-centers that onto the drop point) -- so for feet
// to land on the ground, body.pos[1] must equal -dropY + len + r. Uniform
// scaling preserves this invariant. The same pivot trick makes any part
// hang from its attach point (tails, trunk) or grow out of it (hare ears).
//
// Ordering: SPECIES is sorted small -> large so the demo's grid puts small
// animals in the front rows.

import { eyeMark } from "./mammals.js";
import "./winged.js";   // (registers the winged people's kind with creatures.js: assets/creatures/monsters/angel.json)
import "./dragons.js";  // (...and the dragons', one rule for many: assets/creatures/dragons/*.json)
import { markSculpt, lookFamily, sculptPart, trimOverlay } from "./bodyspec.js"; // (...and the sculpted creatures': one surface skinned to its bones -- bodies.js draws them;
                                            //  every creature built here is marked for it -- a person or a hybrid is not)
import { buildCreature, dressed, bareCoat } from "./creatures.js";
import { CATALOGUE, ASSETS } from "./catalogue.js";
import { makePerson } from "./people.js";
import { scalePart, scaleDef } from "./geom.js";

const EYE_MIN_R = .012;

// Eyes must actually sit ON the head sphere: an eye authored (or pushed by
// the EYE_MIN_R boost) too close to the head center is swallowed once depth
// is computed per pixel. Push each eye outward along its own direction until
// it protrudes about half its radius -- its angular position on the head
// (and thus how it rides head rotation) is unchanged. Head scale (hippo) is
// accounted for by measuring in the head's squashed local frame.
function snapEyes(parts) {
  const head = parts.find((p) => p.id === "head");
  if (!head || head.shape !== "sphere") return parts;
  const hs = head.scale ?? [1, 1, 1];
  // what stands proud of the head where an eye looks out (an owl's face disc, a parrot's cheek patch): the eye
  // goes on that outer surface -- the farthest exit along its direction through the head's round children
  const shells = parts.filter((p) => p.parent === "head" && p.shape === "sphere" && !p.id.startsWith("eye"));
  const outer = (d) => shells.reduce((R, p) => {
    const sc = p.scale ?? [1, 1, 1], c = p.pos.map((v, i) => v / hs[i]), r = p.size.r;   // |(t d - c) / sc| = r
    const A = d.reduce((a, v, i) => a + (v / sc[i]) ** 2, 0), B = -2 * d.reduce((a, v, i) => a + v * c[i] / sc[i] ** 2, 0);
    const C = c.reduce((a, v, i) => a + (v / sc[i]) ** 2, 0) - r * r, disc = B * B - 4 * A * C;
    return disc < 0 ? R : Math.max(R, (-B + Math.sqrt(disc)) / (2 * A));
  }, head.size.r);
  return parts.map((p) => {   // (a classic eye -- a sphere on the head -- becomes a face mark on the outer surface: mammals.js eyeMark)
    if (p.parent !== "head" || !p.id.startsWith("eye") || p.shape !== "sphere") return p;
    const E = p.pos.map((v, i) => v / hs[i]), l = Math.hypot(...E) || 1;
    return eyeMark(p.id, "head", [0, 0, 0], outer(E.map((v) => v / l)), E, p.size.r, p.color);
  });
}

function scaleParts(parts, f) {
  return snapEyes(parts.map((p) => {
    const q = scalePart(p, f);
    if (q.id.startsWith("eye")) q.size.r = Math.max(q.size.r, EYE_MIN_R);
    return q;
  }));
}

// a real trot gait: diagonal pairs (FL+BR, FR+BL) swing in sync, half a
// cycle apart, with a proper ~24-degree stride. Cadence is uniform (.8
// cycles/s at gait-clock rate 1); the wanderer scales the clock by actual
// travel speed over leg length, so a cat's legs flicker while an elephant
// strides -- and every leg passes neutral together, letting stops settle
// square. (The old per-species speed/deg tuning is superseded.)
function legs({ len, r, spreadX, spreadZ, dropY, color, pat }) {
  const at = [["legFL", spreadX, spreadZ, 0], ["legFR", spreadX, -spreadZ, Math.PI],
              ["legBL", -spreadX, spreadZ, Math.PI], ["legBR", -spreadX, -spreadZ, 0]];
  return at.map(([id, x, z, phase]) => ({
    id, parent: "body", shape: "capsule", size: { r, len },
    pos: [x, dropY, z], pivot: [0, -len / 2, 0], color, pat,
    anim: { axis: "z", deg: 24, speed: .8, phase },
  }));
}

export { batWing, birdWing } from "./mammals.js";   // (the wing lives with the rig now: a component a definition asks for by name)

// (the butterflies are assets now: assets/butterflies, drawn by butterflies.js)

// ---- THE DEFINITIONS (assets/creatures/**.json, creatures.js). Everything that is an animal is written out
// there -- a frame it stands on, its size, its colours, what it carries -- and built here into the part lists
// the engines draw. The catalogue (catalogue.js) is loaded before this module runs, so every importer of SPECIES
// sees a world that is ready (a module with a top-level await is awaited by whoever imports it).
const built = new Map();
// (by the NAME the definition gives itself, not by its file: a frame is called horse too, and is not a horse)
const byName = new Map([...ASSETS.values()].filter((d) => d?.name).map((d) => [d.name, d]));
// (a creature, not a person: drawn sculpted -- composite.js converts it when it joins a herd. The winged people are people.)
export const beast = (d, def) => (d?.kind === "winged" ? def : markSculpt(def));   // (assets.html marks what it builds the same way)
// THE LOOKS OF A SPECIES (bodyspec.js lookFamily): its base, each coat, each variant and its young, made as the world
// makes them (and kept) -- told to every one of them, so bodies.js builds ONE shape for the looks that share it
const FAMILY = new Map();
const looksOf = (name) => () => {
  if (!FAMILY.has(name)) {
    const d = byName.get(name), out = [], add = (f) => { try { const x = f(); if (x && !out.includes(x)) out.push(x); } catch { /* (a look that cannot be built is no look) */ } };
    FAMILY.set(name, out);
    add(() => A(name));
    (d?.coats ?? []).forEach((_, i) => add(() => coatDef(name, i)));
    for (const v of Object.keys(d?.variants ?? {})) add(() => variantDef(name, v));
    if (d?.young) add(() => makeYoung(name));
  }
  return FAMILY.get(name);
};
export const A = (name) => {          // a species by name, built once
  if (built.has(name)) return built.get(name);
  const def = byName.get(name);
  if (!def) throw new Error(`species: no definition for "${name}" (assets/index.json)`);
  const made = lookFamily(beast(def, buildCreature(def, ASSETS)), looksOf(name));
  built.set(name, made);
  return made;
};
export const assetCatalogue = () => ({ index: CATALOGUE, bank: ASSETS });
const RIG = new Proxy({}, { get: (_, k) => A(String(k)) });   // (RIG.horse, as it always was)
// a house cat in one of its coats (assets/creatures/mammals/cat.json `coats`: ginger, black, white, grey, tuxedo, cream,
// brown, calico), picked by seed
// (one definition a coat, kept: a sculpted cat's mesh is built once for its coat, not once for every cat in town)
// (2026-11-06: the coats moved out of mammals.js CAT_COATS into the asset, each written out whole -- what makeCat used to
//  work out, a coat's head and chest from its body, the tail's darker rings, is in the coat now -- and a plain one, the
//  black, the white, the tuxedo, the calico, says `"params": { "tabby": false }`: its stripes are gated on that param)
const cats = new Map();
export const makeCat = ({ seed = 1 } = {}) => {
  const d = byName.get("cat"), n = d.coats?.length || 1;
  const i = ((seed * 2654435761) >>> 0) % n;
  if (!cats.has(i)) cats.set(i, lookFamily(beast(d, buildCreature(dressed(d, { coat: d.coats?.length ? i : null }), ASSETS)), looksOf("cat")));
  return cats.get(i);
};
// THE WATER'S CREATURES (2026-11-05: definitions now -- assets/creatures/sea/{fish,dolphin,shark}.json, the "Sea life" of
// the catalogue, and assets/creatures/others/dragonfly.json). The swimmers ride the flier plumbing: constant motion, `fly`'s
// `alt` their depth under the surface (index.html addSwimmer). A fish and a dragonfly are drawn from their definition in
// one of its `coats` and at a size `k` (its param: every length of it written over k), both picked by the seed:
const seeded = (seed) => { let s = (seed * 2246822519) >>> 0 || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; };
const inCoat = (d, i, params) => { const o = dressed(d, { coat: i }); return { ...o, params: { ...o.params, ...params } }; };   // (creatures.js dressed)
// a pond fish, ~0.25-0.45 m: three sizes, not any (k = .8, 1.15, 1.5; its sculpt overlay, written at k = 1, scaled by
// k through `sculptScale`) -- each a sculpted body, built once for its coat and its size
const FISH = new Map();
const fishOf = (vi, ks) => {
  const d = byName.get("fish"), key = vi * 3 + ks;
  if (!FISH.has(key)) FISH.set(key, lookFamily(beast(d, buildCreature(inCoat(d, vi, { k: .8 + ks * .35 }), ASSETS)), fishLooks));
  return FISH.get(key);
};
const fishLooks = () => byName.get("fish").coats.flatMap((_, vi) => [0, 1, 2].map((ks) => fishOf(vi, ks)));   // (its looks: every coat at every size)
export function makeFish({ seed = 1 } = {}) {
  const r = seeded(seed), d = byName.get("fish");
  const vi = Math.floor(r() * d.coats.length);
  return fishOf(vi, Math.min(2, Math.floor(r() * 3)));
}
// a dragonfly, 7-8 cm long: its own size (k .9-1.2) and colours. Not sculpted (its definition's `sculpt: false`): the
// game draws it as its parts, in an instanced herd -- built afresh for each, as it always was
// EVERY LOOK THE WORLD MAKES of every creature definition (2026-11-08, for the bake of their shapes: build/pregen.py
// --bodies, pregen.html's part "bodies", bodies.js "BAKED SHAPES") -- each definition's base, coats, variants and young,
// and the fish in every coat at every size: the very definitions the world builds (and keeps), so their bodies' shape
// keys are the ones a load asks for. `onError(path, e)` hears of a look that cannot be made (none: it is skipped)
export function allLooks(onError = () => {}) {
  const out = [], add = (path, f) => { try { const x = f(); if (x && !out.includes(x)) out.push(x); } catch (e) { onError(path, e); } };
  for (const [path, d] of ASSETS) {
    if (!path.startsWith("creatures/") || path.includes("/frames/") || !d?.name || d.kind === "winged" || byName.get(d.name) !== d) continue;
    if (d.name === "fish") { add(path, () => (fishLooks(), null)); for (const f of FISH.values()) add(path, () => f); continue; }
    add(path, () => A(d.name));
    (d.coats ?? []).forEach((_, i) => add(path, () => coatDef(d.name, i)));
    for (const v of Object.keys(d.variants ?? {})) add(path, () => variantDef(d.name, v));
    if (d.young) add(path, () => makeYoung(d.name));
  }
  return out;
}
export function makeDragonfly({ seed = 1 } = {}) {
  const r = seeded(seed), d = byName.get("dragonfly");
  const vi = Math.floor(r() * d.coats.length), k = .9 + r() * .3;
  return beast(d, buildCreature(inCoat(d, vi, { k }), ASSETS));
}
// the lake's big swimmers, at their real sizes (dolphin ~2.6 m, shark ~3.2 m): the dolphin's tail pitches, the shark's sweeps
export const makeDolphin = () => A("dolphin");
export const makeShark = () => A("shark");
// the open water's giants (2026-11-06: assets/creatures/sea/{orca,humpback,plesiosaurus}.json): a 7 m bull orca, a 14 m
// humpback, a 3.3 m plesiosaur -- not wanderers: sealife.js swims them on loops of their own, a pure function of the clock
export const makeOrca = () => A("orca");
export const makeHumpback = () => A("humpback");
export const makePlesiosaurus = () => A("plesiosaurus");
// (2026-11-07: assets/creatures/sea/narwhal.json) a 4.5 m tusked bull narwhal -- its pod (a cow, a calf, an old pale bull:
// the asset's variants) swum by sealife.js in a cold sea, on a loop of its own like the orcas'
export const makeNarwhal = () => A("narwhal");
// the pteranodon (2026-11-06: assets/creatures/dinosaurs/pteranodon.json), 6 m across the wings -- not a wanderer either:
// pterosaurs.js soars it in circles over the open water, a pure function of the clock
export const makePteranodon = () => A("pteranodon");
export const SQUIRREL = RIG.squirrel;   // not a wanderer: it lives in the trees (squirrels.js)
// A COAT of a species that declares several (its asset's `coats`: colour tables over its own -- a herd of horses bay,
// chestnut, black, grey, dun, some with white socks; a black sheep in the flock): the k-th, built once
const coatCache = new Map();
export const coatDef = (species, k) => {
  const d = byName.get(species), cs = d?.coats;
  if (!cs?.length) return A(species);
  const i = ((k % cs.length) + cs.length) % cs.length, key = species + "|" + i;
  // (creatures.js dressed: its colours over the asset's own table, its `params` over its params -- a coat's `name` is
  //  not a colour; a coat that changes nothing is the species itself)
  if (!coatCache.has(key)) coatCache.set(key, bareCoat(cs[i]) ? A(species) : lookFamily(beast(d, buildCreature(dressed(d, { coat: i }), ASSETS)), looksOf(species)));
  return coatCache.get(key);
};
// A VARIANT a species declares (its asset's `variants`: { name: { params, colors } } -- the hen yard's rooster is the
// chicken with `rooster`, its parts that are `"when": "rooster"`, in a cock's colours): built once, named after it
const variantCache = new Map();
export const variantDef = (species, name) => {
  const d = byName.get(species), v = d?.variants?.[name];
  if (!v) return null;
  const key = species + "|" + name;
  if (!variantCache.has(key)) variantCache.set(key, lookFamily(beast(d, buildCreature({ ...dressed(d, { variant: name }), name }, ASSETS)), looksOf(species)));
  return variantCache.get(key);
};
// THE SHORE'S SEALS AND WALRUSES (2026-11-06: assets/creatures/sea/{seal,walrus}.json): not wanderers -- haulout.js lays
// them out on the shore and moves them, a pure function of the clock. A seal in one of its coats (its `coats`: 0-3
// harbour seals silver grey, dark, brown; 4 a grey seal bull at 1.25x, 5 a grey seal cow at 1.1x), by `coat` or by seed
export const makeSeal = ({ seed = 1, coat = null } = {}) => coatDef("seal", coat ?? ((seed * 2654435761) >>> 0));
export const makeWalrus = () => A("walrus");
// THE YOUNG of a species that declares them (its asset's `young`: { s, n, side, hop, name } -- a lamb, a foal, a calf):
// the species at `s` of its size (geom.js scaleDef), no grazing, resting or coming to you of its own -- it
// follows its mother (index.html, in spring). null for a species without young.
export const makeYoung = (species) => {
  const d = byName.get(species), y = d?.young;
  // (built with its `grown` param false: what only the grown have -- an udder, antlers -- says `"when": "grown"`)
  return y ? lookFamily(beast(d, scaleDef(buildCreature({ ...d, params: { ...(d.params ?? {}), grown: false }, name: y.name ?? species, graze: undefined, rest: undefined, beg: undefined, young: undefined }, ASSETS), y.s)), looksOf(species)) : null;
};

// natural travel speed for a body: one unit of the gait clock per this many
// metres, so a cat's legs flicker while an elephant strides. Rig legs
// (two bones, IK) take .8 of their length per unit, classic swinging
// capsules 1.3 of theirs (tuned for the 24-degree trot)
export function gaitBase(def) {
  // rig legs (mammals, people): the walk's own stride -- a foot sweeps
  // 2 x stride per stance, half a cycle, and a clock unit is CYCLES (.8,
  // skeleton.js) cycles, so 4 x .8 x stride metres per unit keep it planted
  if (def.gaits?.walk?.stride) return Math.max(.08, 3.2 * def.gaits.walk.stride);
  if (def.legLen) return Math.max(.1, .8 * def.legLen);
  // (a leg's length from its shape: a capsule's len, a tube's or a cone's ends -- a tube leg has no len, and NaN froze the walk)
  const lg = def.parts.find((q) => q.id.startsWith("leg")), z = lg?.size;
  const d = (a, b) => (a && b ? Math.hypot(b[0] - a[0], b[1] - a[1], (b[2] ?? 0) - (a[2] ?? 0)) : 0);
  const L = !z ? 0 : (z.len ?? z.h ?? d(z.a, z.b)) + (z.r ?? z.r1 ?? 0);
  return L > 0 ? Math.max(.15, 1.3 * L) : 1;
}
// walk or run at this speed? Legged animals change gait at a Froude number
// v^2 / (g L) of about .5 whatever their size (a cat trots where a horse
// still walks); the base is ~ the leg length for rig legs
export const runs = (speed, base) => speed * speed > 4.8 * base;
// Where a rider sits on a mount -- ONE point for every rider (the player's
// camera, peers, the trotting riders, Shift+D copies): a third of the way
// from the rump lobe to the chest lobe, just behind the withers, on the
// back. rootX in the animal's root space (x forward); bodyX/bodyY in the
// body part's own frame, where fused riders' parts hang.
// `def.saddle` { x, y } (opt-in, 2026-11-05): the seat given outright, in root space -- x forward, y the height of the
// back's surface there (the rider's hips sit 5cm above it, as the lobes' seat does). For a body whose rig lobes no
// longer say where its back is: a sculpted dragon's chest and back are drawn over them (dragons.js PLANS seat: at the
// neck's base, ahead of the wings). Its body part must not be turned (bodyX/bodyY are in its frame); geom.js scaleDef scales it.
export function saddle(def) {
  const body = def.parts.find((q) => q.id === "body") ?? def.parts[0], front = def.parts.find((q) => q.id === "front" && q.parent === "body");
  const bx = body.pos?.[0] ?? 0;
  if (def.saddle) return { rootX: def.saddle.x, bodyX: def.saddle.x - bx, bodyY: def.saddle.y - (body.pos?.[1] ?? 0) + .05 };
  const rootX = front ? bx + front.pos[0] * 2 / 3 : bx + .08;
  return { rootX, bodyX: rootX - bx, bodyY: (partExtent(body).r || .4) + .05 };
}
// a part's girth and length, whatever its shape -- the ONE reader of body sizes (probes, colliders,
// swimmers' depth): a tube's fattest radius and its end-to-end length, a capsule's r and len
export function partExtent(p) {
  const z = p.size ?? {};
  if (p.shape === "tube") return { r: Math.max(z.r1, z.r2 ?? z.r1) + (z.bulge ?? 0), len: Math.hypot(z.b[0] - z.a[0], z.b[1] - z.a[1], z.b[2] - z.a[2]) };
  return { r: z.r ?? 0, len: z.len ?? z.h ?? 0 };
}
// half the body length: where the nose and tail meet the ground
export function bodyProbe(def) {
  if (def.probe) return def.probe;
  const b = def.parts.find((q) => q.id === "body" || q.id === "torso");
  if (!b) return .4;
  const e = partExtent(b);
  return e.len / 2 + e.r;
}

const SPIDER = { // ---- spider: a tarantula -- a 7cm body (cephalothorax and a rounder abdomen), hairy, eight legs to a
    // ~14cm span. Each leg: an undrawn coxa bone at the body's side, yawed out (it sweeps the leg fore and aft),
    // the femur rising 30 degrees to the knee (it lifts the leg on the forward swing), the tibia splaying down (55 degrees) to the ground; the
    // legs step in two alternating sets of four (L1 R2 L3 R4 / R1 L2 R3 L4)
    name: "spider",
    parts: scaleParts([
      { id: "body", parent: null, shape: "capsule", size: { r: .011, len: .012 }, geomRot: [0, 0, 90], pos: [0, .024, 0], color: 0x4a3526, fur: true },
      { id: "head", parent: "body", shape: "sphere", size: { r: .009 }, scale: [1, .8, 1], pos: [.009, .002, 0], color: 0x4a3526, fur: true },
      { id: "eyeL", parent: "head", shape: "sphere", size: { r: .0016 }, pos: [.004, .008, .0025], color: 0x0a0806 },
      { id: "eyeR", parent: "head", shape: "sphere", size: { r: .0016 }, pos: [.004, .008, -.0025], color: 0x0a0806 },
      { id: "eye2L", parent: "head", shape: "sphere", size: { r: .0011 }, pos: [.006, .006, .005], color: 0x0a0806 },
      { id: "eye2R", parent: "head", shape: "sphere", size: { r: .0011 }, pos: [.006, .006, -.005], color: 0x0a0806 },
      { id: "abdomen", parent: "body", shape: "sphere", size: { r: .017 }, scale: [1.2, .95, 1], pos: [-.03, .005, 0], color: 0x3a2a1e, fur: true,
        anim: { axis: "z", deg: 3, speed: .4, phase: 0 } },
      ...[1, -1].flatMap((s) => [
        { id: "fang" + (s > 0 ? "L" : "R"), parent: "head", shape: "sphere", size: { r: .0035 }, pos: [.008, -.004, s * .003], color: 0x1a1210 },
        { id: "palp" + (s > 0 ? "L" : "R"), parent: "head", shape: "capsule", size: { r: .0028, r2: .0022, len: .02 }, pos: [.007, -.002, s * .005],
          rot: [-s * 35, 0, 110], pivot: [0, -.01, 0], color: 0x3a2a20, fur: true, anim: { axis: "z", deg: 8, speed: .8, phase: s > 0 ? 0 : 3.14 } },
      ]),
      ...[1, -1].flatMap((s) => [35, 70, 110, 145].flatMap((a, k) => {
        const t = k + (s > 0 ? "L" : "R"), ph = (k + (s > 0 ? 0 : 1)) % 2 * 3.14, f = k === 0 || k === 3 ? 1.1 : 1, lf = .035 * f, lt = .05 * f;
        return [
          { id: "coxa" + t, parent: "body", shape: "capsule", size: { r: .003, len: .002 }, bone: true, pos: [.006 - k * .005, 0, s * .009], rot: [0, -s * a, 0],
            anim: { axis: "y", deg: 14, speed: .8, phase: ph } },
          { id: "femur" + t, parent: "coxa" + t, shape: "capsule", size: { r: .0046, r2: .004, len: lf }, pos: [0, 0, 0], rot: [0, 0, 120], pivot: [0, -lf / 2, 0],
            color: 0x3a2a20, fur: true, fold: [0, 0, 45], anim: { axis: "z", deg: 6, speed: .8, phase: ph + s * 1.57 } },
          { id: "tibia" + t, parent: "femur" + t, shape: "capsule", size: { r: .0038, r2: .0026, len: lt }, pos: [0, -lf, 0], rot: [0, 0, -85], pivot: [0, -lt / 2, 0],
            color: 0x46342a, fur: true, fold: [0, 0, -70] },   // (fold: struck down, the legs curl in -- the femur up over the body, the tibia tucked under)
        ];
      })),
    ], 1),
  };

// every part hung (at any depth) under part `id`
function subtree(parts, id) {
  const byId = new Map(parts.map((p) => [p.id, p]));
  return parts.filter((p) => { for (let q = p; q; q = byId.get(q.parent)) if (q.parent === id) return true; return false; });
}

// ---- tauric beasts (the centaur's kind): an animal's trunk, legs and tail -- its rig or classic def without the
// head (and all on it), the neck and `drop` (a mane), scaled by `scale` (for a def whose gait is its parts' own
// anims: a rig's gait strides are in metres) -- and a person's upper body (people.js makePerson, upper: the torso
// pill and all above it) standing on its chest: the pelvis bone hung from the animal's root at `at` (figure
// coordinates after scaling), low enough that the torso grows out of it. The rest: makePerson's options
function tauric(name, base, { scale = 1, at, drop = [], call, ...person }) {
  if (scale !== 1 && base.gaits) throw new Error(`${name}: a rig's gaits do not scale`);
  const gone = new Set(["head", "neck", ...drop, ...subtree(base.parts, "head").map((p) => p.id)]);
  const parts = base.parts.filter((p) => !gone.has(p.id)).map((p) => scale === 1 ? p : { ...scalePart(p, scale), k: p.k && p.k * scale });
  const root = parts.find((p) => !p.parent), man = makePerson({ upper: true, ...person });
  const human = man.parts.map((p) => p.id === "pelvis" ? { ...p, parent: root.id, bob: false, pos: at.map((v, i) => v - (root.pos?.[i] ?? 0)) } : p);
  // (no saddle, yoke or trees for them -- and not the animal's MANE: mammals.js reports it by its neck's and head's part
  //  INDICES, both dropped here, so the old indices fell on whatever moved into their places: a leg wore the horse's mane)
  const { mount, draft, climber, mane, ...rest } = base;
  // (its HEAD is the person's mesh face, heads.js -- found by part index: the person's indices moved past the animal's,
  //  as a fused rider's are; without it the man had no head at all)
  const face = man.face ? { ...man.face, head: parts.length + man.face.head, gaze: parts.length + man.face.gaze } : null;
  // (2026-11-08) the animal's trunk SCULPTED as the animal itself is: what is left of its parts converted as a body of
  // its own (its overlay without the shapes on the bones dropped -- the horse's neck and head -- and without their eyes:
  // bodyspec.js trimOverlay), carried in `sculpts` with its parts as bones; the person's upper body stays the composite's.
  // Put together as parts it was drawn as plain pills, the horse beside it a skinned body
  const trunk = sculptPart(markSculpt({ ...rest, name: `${name} trunk`, parts, ...(base.sculpt ? { sculpt: trimOverlay(base.sculpt, new Set(parts.map((p) => p.id))) } : {}) }));
  return { ...rest, name, monster: true, call, parts: [...(trunk ? trunk.parts : parts), ...human], ...(face ? { face } : {}),
           ...(trunk ? { sculpts: [{ body: trunk.body, base: 0 }] } : {}) };
}

// ---- beast-men: the human rig (people.js makePerson) with an animal's head -- the species' own rig head (its
// head sphere and everything hung on it: muzzle, ears, eye marks, nose, horns, tusks, fangs), scaled to a
// human-sized head -- in the animal's hide, with its tail and, for the hoofed, hooves; they call as the animal;
// outfit: what it wears over the bare hide (makePerson's: a kilt, a tunic, breeches... -- the wardrobe's kit of its
// name, assets/clothes/wardrobe.json `outfits`)
function beastman(name, rig, { seed, height, build = 1.2, hoof = false, headScale, eye, call, outfit } = {}) {
  const head = rig.parts.find((p) => p.id === "head"), body = rig.parts.find((p) => p.id === "body");
  const beast = { hide: body.color, build, hoof, headScale, eye, foot: rig.parts.find((p) => p.id.startsWith("foot"))?.color ?? body.color,
    head: { r: head.size.r, color: head.color, pat: head.pat, parts: subtree(rig.parts, "head") },
    tail: rig.parts.filter((p) => /^tail/.test(p.id) && p.parent === "body").flatMap((p) => [p, ...subtree(rig.parts, p.id)]) };
  return { ...makePerson({ seed, kind: "man", height, beast, outfit }), name, monster: true, call: call ?? rig.name };
}


// THE WORLD'S CAST, in the order the demo grid lays them out (small to large). Every one of them is a
// DEFINITION now -- assets/creatures/**.json, built by creatures.js -- except the hybrids below, which are a
// person and an animal put together and so are built from both.
export const SPECIES = [
  A("chicken"),
  A("rooster"),
  A("cockatiel"),
  A("woodpecker"),
  A("hoopoe"),
  A("puffin"),
  A("parrot"),
  A("cockatoo"),
  A("toucan"),
  A("hornbill"),
  A("tawny owl"),
  A("owl"),
  A("hare"),
  A("cat"),
  A("fox"),
  A("eagle"),
  A("vulture"),
  A("dog"),
  A("sheep"),
  A("ram"),
  A("pig"),
  A("wolf"),
  A("deer"),
  A("reindeer"),
  A("oryx"),
  A("cervicapra"),
  A("tiger"),
  A("lion"),
  A("leopard"),
  A("smilodon"),
  A("cow"),
  A("ox"),
  A("zebra"),
  A("horse"),
  A("bear"),
  A("hippo"),
  A("giraffe"),
  A("elephant"),
  A("rhinoceros"),
  A("snake"),
  A("rat"),
  A("boar"),
  A("swan"),
  A("flamingo"),
  A("heron"),
  A("ibis"),
  A("spoonbill"),
  A("crowned crane"),
  A("penguin"),
  A("pelican"),
  A("duck"),
  A("peacock"),
  A("turkey"),
  A("ostrich"),
  A("cassowary"),
  A("crocodile"),
  A("frog"),
  A("wall lizard"),
  A("turtle"),
  A("hedgehog"),
  A("scorpion"),
  A("spider"),
  A("beaver"),
  A("camel"),
  A("bactrian"),
  A("hyena"),
  A("impala"),
  A("anteater"),
  A("pangolin"),
  A("skunk"),
  A("capybara"),
  A("badger"),
  A("weasel"),
  A("lynx"),
  A("chamois"),
  A("moose"),
  A("bison"),
  A("ibex"),
  A("giantpanda"),
  A("redpanda"),
  A("porcupine"),
  A("bat"),
  A("lemur"),
  A("baboon"),
  A("kangaroo"),
  A("orangutan"),
  A("gorilla"),
  A("unicorn"),
  A("pegasus"),
  A("griffin"),
  tauric("centaur", A("horse"), { at: [.5, 1.45, 0], drop: ["mane"], seed: 11, kind: "man", height: 2.2, outfit: { bare: true, hair: "long" } }),
  tauric("drider", A("spider"), { scale: 25, at: [.28, .95, 0], seed: 31, kind: "woman", height: 1.8, outfit: { named: "drider", hair: "long" } }),
  tauric("sphinx", A("lion"), { at: [.5, 1.0, 0], drop: ["mane"], call: "lion", seed: 41, kind: "man", height: 1.9, outfit: { bare: true, hair: "bob" } }),
  A("angel"),
  A("demon"),
  beastman("minotaur", A("ox"), { seed: 5, height: 2.45, build: 1.3, hoof: true, eye: 0xb03a2a, call: "minotaur", outfit: { named: "minotaur" } }),
  beastman("wolfman", A("wolf"), { seed: 21, height: 2.1, build: 1.1, outfit: { named: "wolfman" } }),
  beastman("boarman", A("boar"), { seed: 22, height: 1.9, build: 1.35, hoof: true, outfit: { named: "boarman" } }),
  beastman("catman", A("cat"), { seed: 23, height: 1.75, build: .95, outfit: { named: "catman" } }),
  beastman("foxman", A("fox"), { seed: 24, height: 1.8, build: .95, outfit: { named: "foxman" } }),
  beastman("bearman", A("bear"), { seed: 25, height: 2.35, build: 1.45, outfit: { named: "bearman" } }),
  beastman("ramman", A("ram"), { seed: 26, height: 2.0, build: 1.15, hoof: true, outfit: { named: "ramman" } }),
  beastman("smilodonman", A("smilodon"), { seed: 27, height: 2.2, build: 1.25, outfit: { named: "smilodonman" } }),
  A("manticore"),
  A("cerberus"),
  A("dragon"),
  A("red dragon"),
  A("black dragon"),
  A("frost dragon"),
  A("gold dragon"),
  A("drake"),
  A("wyvern"),
  A("chinese dragon"),
  A("azure dragon"),
  A("imperial dragon"),
  A("ryu"),
  A("feathered serpent"),
  A("hydra"),
  A("tyrannosaur"),
  A("carnotaurus"),
  A("allosaurus"),
  A("dilophosaurus"),
  A("pachycephalosaurus"),
  A("triceratops"),
  A("styracosaurus"),
  A("diabloceratops"),
  A("stegosaurus"),
  A("ankylosaurus"),
  A("diplodocus"),
  A("parasaurolophus"),
];
