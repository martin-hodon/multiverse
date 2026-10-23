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
                       "person", "wing"]);   // (a winged person's: makePerson's options and the wing's, as written)
// (NOT "c": that is the tail's arc CENTRE as often as it is a colour table, and the table is taken out before
//  anything is resolved)
const keepKey = (k) => k.startsWith("_") || WORDS.has(k);

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
function resolveDeep(v, params, colors) {
  if (Array.isArray(v)) {
    if (isColourRef(v)) return colourOf(v, colors);
    const out = v.map((x) => resolveDeep(x, params, colors)).filter((x) => x !== undefined);
    return out;
  }
  if (isPlain(v)) {
    if ("when" in v) {
      const names = Array.isArray(v.when) ? v.when : [v.when];
      if (!names.every((n) => !!params[n])) return undefined;
      const { when, v: inner, ...rest } = v;            // (the key itself goes, or it would gate its own copy)
      return resolveDeep("v" in v ? inner : rest, params, colors);
    }
    const out = {};
    for (const k of Object.keys(v)) {
      if (v[k] === undefined) continue;
      const r = keepKey(k) ? v[k] : resolveDeep(v[k], params, colors);
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
  const out = resolveDeep({ ...flat, params: undefined, use: undefined, colors: undefined }, params, colors);
  delete out.params; delete out.use;
  out.c = colors;
  return out;
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
  const d = resolveDef(def, bank);
  if (d.extras) d.extras = expand(d.extras);
  const kind = d.kind ?? "mammal";
  delete d.kind;
  if (kind === "mammal") return mammal(d);
  if (kind === "parts") return { name: d.name, ...d.flags, parts: d.parts };
  if (KINDS[kind]) return KINDS[kind](d);
  throw new Error(`creatures: "${d.name}" is a "${kind}", which nothing here builds`);
}
