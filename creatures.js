// THE CREATURES' DEFINITION LAYER: what an animal IS, as JSON, in terms of what it is made of.
//
// It is the same idea as the buildings' (arch/assemble.js, docs/arch.md), one level down: a building is walls
// and vaults and arches over openings; an animal is a body of two lobes, a neck, a head cluster, four legs of
// two bones and a foot, a tail of linked arcs -- and each of those is written in terms of the one below it,
// down to the capsules, ellipsoids, tubes and membranes the engines draw.
//
//   frames/horse.json     a BODY PLAN at one scale, every number an expression over its params ("0.55*s")
//   horse.json            a SPECIES: the frame it stands on, its size, its colours, what it carries
//   swan.json             ...or the parts themselves, for the animals that share no plan with anything
//
// Nothing here draws: it produces exactly the part lists species.js has always produced, and mammals.js
// mammal() is still what turns a body plan into parts. What has changed is where the numbers live.
import { evalValue } from "./expr.js";
import { merge, chain } from "./defs.js";
import { mammal, COMPONENTS } from "./mammals.js";
import { scaleDef } from "./geom.js";

// ---- the bank: path -> definition, as loaded (the editor keeps its own, with unsaved text in it) -----------
export const ASSET_BASE = new URL("./assets/", import.meta.url).href;   // (the game, the viewer and the harnesses all read the same files)
export const fetchAsset = async (path) => (await fetch(ASSET_BASE + path + ".json")).json();

export async function loadBank(paths, fetchJSON = fetchAsset) {
  const bank = new Map();
  await Promise.all(paths.map(async (path) => bank.set(path, await fetchJSON(path))));
  return bank;
}
// the whole catalogue (assets/index.json): every asset, by category
export async function loadCatalogue(fetchJSON = fetchAsset) {
  const index = await (await fetch(ASSET_BASE + "index.json")).json();
  const paths = index.categories.flatMap((c) => c.paths);
  return { index, bank: await loadBank(paths, fetchJSON) };
}

// ---- resolution -------------------------------------------------------------------------------------------
// (how definitions merge, and the chain one stands on: defs.js, shared with the items)
const isPlain = (v) => v && typeof v === "object" && !Array.isArray(v);

const WORDS = new Set(["name", "kind", "use", "id", "parent", "shape", "pat", "patOn", "pupil", "axis", "frame",
                       "active", "geomRot", "ik", "anim", "colors", "gaits", "mount", "fly", "swim", "_about",
                       "person", "wing", "fleece",   // (a winged person's: makePerson's options and the wing's, as written)
                       "dragon",                     // (a dragon's style: dragons.js reads its words itself)
                       "headForm"]);                 // (a head's family preset, mammals.js FACES: a word, or its numbers as written)
// (NOT "c": that is the tail's arc CENTRE as often as it is a colour table, and the table is taken out before
//  anything is resolved)
const keepKey = (k) => k.startsWith("_") || WORDS.has(k);
// THE SCULPT OVERLAY (`sculpt`: bodyspec.js -- the authored shapes a converted creature is drawn with) is resolved by
// its OWN words: there "shape" is the list of primitives (numbers, expressions over the params, "@colour"s -- all
// resolved), and only these are words: a primitive's type, its bone, its op, its id, a pattern's name, a pupil's,
// the `keep` patterns (regular expressions over the rig's part ids), a feather's outline
const SCULPT_WORDS = new Set(["type", "bone", "op", "id", "pat", "pupil", "keep", "outline", "frame", "_about"]);
const sculptKey = (k) => k.startsWith("_") || SCULPT_WORDS.has(k);

// A VALUE MAY BE A COLOUR OUT OF THE SPECIES' OWN TABLE: "@mane" is whatever it calls its mane, and a list is
// a fallback chain ("@mane" or else "@tail"), which is how a frame says "in its mane's colour" without
// knowing which animals have one.
// ...and a colour is written as it is everywhere else a person reads one: "#8a5a33".
const HEX = /^#[0-9a-fA-F]{6}$/;
const colourOf = (v, colors) => {
  const names = Array.isArray(v) ? v : [v];
  for (const n of names) { const c = colors[String(n).slice(1)]; if (c !== undefined) return c; }
  return undefined;
};
const isColourRef = (v) => (typeof v === "string" && v.startsWith("@")) ||
                           (Array.isArray(v) && v.length > 0 && v.every((x) => typeof x === "string" && x.startsWith("@")));

// `when`: a part, a limb or a whole head that a species may not have. { "when": ["mane", "head"], "v": ... }
// is its value when every named param is true, and nothing at all when one is not -- so one frame serves the
// horse that has a mane and the one that is only a body (a centaur's).
// ...and a WORD may be gated the same way: `"pat": { "when": "tabby", "v": "tabby" }` is the tabby's stripes while the
// param holds and no pattern when it does not (a black cat's coat: its `params`), and a list of them is the first that
// holds -- `[{ "when": "pinto", "v": "piebald" }, { "when": "spotted", "v": "dots" }]` (a horse's coats)
const holds = (when, params) => (Array.isArray(when) ? when : [when]).every((n) => !!params[n]);
const isGated = (v) => (isPlain(v) && "when" in v) || (Array.isArray(v) && v.length > 0 && v.every((g) => isPlain(g) && "when" in g));
const gatedWord = (v, params) => (Array.isArray(v) ? v : [v]).find((g) => holds(g.when, params))?.v;
function resolveDeep(v, params, colors, keep = keepKey) {
  if (Array.isArray(v)) {
    if (isColourRef(v)) return colourOf(v, colors);
    const out = v.map((x) => resolveDeep(x, params, colors, keep)).filter((x) => x !== undefined);
    return out;
  }
  if (isPlain(v)) {
    if ("when" in v) {
      const names = Array.isArray(v.when) ? v.when : [v.when];
      if (!names.every((n) => !!params[n])) return undefined;
      const { when, v: inner, ...rest } = v;            // (the key itself goes, or it would gate its own copy)
      return resolveDeep("v" in v ? inner : rest, params, colors, keep);
    }
    const out = {};
    for (const k of Object.keys(v)) {
      if (v[k] === undefined) continue;
      // (a `frame` that is a word -- "body" -- stays one; an authored frame { o, u, v } is numbers)
      const word = keep(k) && !(k === "frame" && isPlain(v[k]));
      const r = k === "sculpt" && keep === keepKey && isPlain(v[k]) ? resolveDeep(v[k], params, colors, sculptKey)
              : word && isGated(v[k]) ? gatedWord(v[k], params)
              : word ? v[k] : resolveDeep(v[k], params, colors, keep);
      if (r !== undefined) out[k] = r;
    }
    return out;
  }
  if (isColourRef(v)) return colourOf(v, colors);
  if (typeof v === "string" && HEX.test(v)) return parseInt(v.slice(1), 16);
  return typeof v === "string" || typeof v === "number" ? evalValue(v, params) : v;
}

// ---- building ------------------------------------------------------------------------------------------------
// what a definition resolves to, before any engine sees it: the plain object mammal() (or the part list) wants
export function resolveDef(def, bank) {
  const parts = chain(def, bank);
  let flat = {};
  for (const d of parts) flat = merge(flat, d);
  const params = { ...(flat.params ?? {}) };
  const colors = Object.fromEntries(Object.entries(flat.colors ?? flat.c ?? {})
    .map(([k, v]) => [k, typeof v === "string" && HEX.test(v) ? parseInt(v.slice(1), 16) : v]));
  // (its `coats` and `variants` are what it MAY be dressed in -- dressed() below, before it is built: not built with it)
  const out = resolveDeep({ ...flat, params: undefined, use: undefined, colors: undefined, coats: undefined, variants: undefined }, params, colors);
  delete out.params; delete out.use;
  out.c = colors;
  return out;
}

// ---- COATS AND VARIANTS: what one definition may be dressed in (docs/assets.md "Coats and variants") ----------
//   `coats`     a LIST the world picks from by seed (a herd of horses bay, chestnut, grey; a black sheep in the flock):
//               each a colour table laid over the definition's own -- and, if it says, its `name` ("dapple grey") and
//               the `params` it changes too (a black cat's { "tabby": false }, a pinto's { "pinto": true }). A coat
//               written twice is picked twice as often.
//   `variants`  NAMED ones the world asks for by name: { "rooster": { "params": {...}, "colors": {...} } } -- a variant
//               may also carry a `sculpt` of its own: shapes over the base's by id (sculptOver, below)
// ...and either may say its `scale`: the whole creature at that share of the definition's size, once built (geom.js
// scaleDef, as a species' young: the lioness, .8 of the lion) -- what is written in metres stays as written
// Both are taken off what comes back, so a dressed definition is built like any other. The asset viewer dresses with
// the same function: what it shows for a coat is what the world builds.
// (a coat may also nest its colours as `colors`, the way a variant does: both spellings dress alike)
const COAT_WORDS = new Set(["name", "params", "scale", "colors"]);
export const coatColours = (c) => ({ ...Object.fromEntries(Object.entries(c ?? {}).filter(([k]) => !COAT_WORDS.has(k) && !k.startsWith("_"))),
                                     ...(c?.colors && typeof c.colors === "object" ? c.colors : {}) });
// a coat that changes nothing (a herd's own colour, written to be picked): the definition itself serves
export const bareCoat = (c) => !Object.keys(coatColours(c)).length && !Object.keys(c?.params ?? {}).length && !(typeof c?.scale === "number" && c.scale !== 1);
// the definition in coat `coat` (its index) or variant `variant` (its name); neither: as it is. Its colour table is the
// one it writes, by either name (`colors`, or the older `c`)
export function dressed(def, { coat = null, variant = null } = {}) {
  const table = def.colors || !def.c ? "colors" : "c";
  const over = variant != null ? def.variants?.[variant] : coat != null ? def.coats?.[coat] : null;
  const colours = variant != null ? over?.colors ?? {} : coatColours(over);
  const scale = typeof over?.scale === "number" && over.scale > 0 && over.scale !== 1 ? over.scale : undefined;
  const out = { ...def, params: { ...(def.params ?? {}), ...(over?.params ?? {}) }, [table]: { ...(def[table] ?? {}), ...colours },
                coats: undefined, variants: undefined, scaleBy: scale };
  if (variant != null && over?.sculpt && def.sculpt) out.sculpt = sculptOver(def.sculpt, over.sculpt);
  return out;
}
// A VARIANT'S OWN SCULPT (2026-11-08): `"sculpt": { "shape": [...] }` in a variant -- each of its shapes over the
// base's of the same `id` (its fields over the base's, a field `null` taken out: the fennec's ears, the fox's
// grown), one with `"drop": true` taken out, one of a new id added at the end (a paint: the fennec's dark streak under
// the eye); any other sculpt field (`eyes`, `mesh`...) over the base's. A variant that changes only a fin, a horn or a paint (bodies.js) shares the
// base's shape build and redraws only those.
export function sculptOver(base, over) {
  const { shape = [], ...rest } = over;
  const by = new Map(shape.filter((s) => s?.id).map((s) => [s.id, s]));
  const out = (base.shape ?? []).flatMap((s) => { const o = s?.id && by.get(s.id); if (!o) return [s]; by.delete(s.id); return o.drop ? [] : [Object.fromEntries(Object.entries({ ...s, ...o }).filter(([, v]) => v !== null))]; });
  for (const s of shape) if (!s?.id || (by.has(s.id) && !s.drop)) out.push(s);
  return { ...base, ...rest, shape: out };
}

// A PIECE ASKED FOR BY NAME. `{ "component": "curlHorn", "s": 1.1 }` among the extras is a ram's horns: the
// rule that draws them (mammals.js COMPONENTS), with the definition's own numbers, expanded into the parts it
// comes to. The definition keeps the question ("a curl of four links"); only the engine knows the answer.
function expand(list) {
  if (!Array.isArray(list)) return list;
  return list.flatMap((x) => {
    if (!x?.component) return [x];
    const make = COMPONENTS[x.component];
    if (!make) throw new Error(`creatures: no component "${x.component}"`);
    const { component, ...o } = x;
    return make(o);
  });
}

// KINDS BUILT ELSEWHERE: a module that builds a kind of definition from other engines (winged.js: a person and its
// wings) registers it here -- it imports this file, never the other way round
export const KINDS = {};

// ...and the species definition the engines take (species.js SPECIES entries)
export function buildCreature(def, bank) {
  // (dressed in a variant with a `scale` of its own: built at the definition's size, then scaled as a whole)
  if (def.scaleBy !== undefined) { const { scaleBy, ...own } = def; const b = buildCreature(own, bank); return scaleBy ? scaleDef(b, scaleBy) : b; }
  const d = resolveDef(def, bank);
  if (d.extras) d.extras = expand(d.extras);
  const kind = d.kind ?? "mammal";
  delete d.kind;
  if (kind === "mammal") return mammal(d);
  // (a creature of ready parts -- a bird, a frog, a crocodile -- is FACETED like the mammals: shell.js FACET; `facet: false` keeps it smooth)
  // (`sculpt`, `patScale`: the overlay a converted creature is drawn with, bodyspec.js -- carried on whatever the kind builds)
  const keep = (o) => { if (d.sculpt !== undefined && o && o.sculpt === undefined) o.sculpt = d.sculpt; if (d.patScale !== undefined && o && o.patScale === undefined) o.patScale = d.patScale; return o; };
  if (kind === "parts") return keep({ name: d.name, ...d.flags, parts: d.facet === false ? d.parts : d.parts.map((p) => ({ ...p, facet: true })) });
  if (KINDS[kind]) return keep(KINDS[kind](d));
  throw new Error(`creatures: "${d.name}" is a "${kind}", which nothing here builds`);
}
