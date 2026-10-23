// THE DEFINITIONS' OWN RULES, shared by every kind that stands one definition on another (docs/assets.md): the
// creatures (creatures.js), the items and the furniture (items.js). How two definitions MERGE, and the CHAIN a
// definition stands on. One copy, so a species and a sword mean the same thing by `use` and by an `id`.

export const isPlain = (v) => v && typeof v === "object" && !Array.isArray(v);
// deep merge. Objects merge key by key; null removes what the frame had (a species with no tail). Plain
// arrays REPLACE -- a species that gives its own legs means those, not those and the frame's -- but a list of
// NAMED things (everything in it an object with an `id`: the extras a body carries, the parts of a sword) merges
// by that name, so a species adds its horn to the frame's mane instead of replacing it, and can reach in and
// change the mane by naming it. That is the same distinction the definitions themselves draw: what a thing IS,
// against what it carries.
const nameOf = (x) => (isPlain(x) ? x.id ?? x.raw?.id : undefined);   // (a part written out in full carries its id inside `raw`)
const named = (a) => Array.isArray(a) && a.length > 0 && a.every((x) => nameOf(x) !== undefined);
export function merge(base, over) {
  if (over === null) return null;
  if (named(base) && named(over)) {
    const out = base.map((b) => { const o = over.find((x) => nameOf(x) === nameOf(b)); return o ? merge(b, o) : b; });
    for (const o of over) if (!base.some((b) => nameOf(b) === nameOf(o))) out.push(o);
    return out;
  }
  if (!isPlain(base) || !isPlain(over)) return over === undefined ? base : over;
  const out = { ...base };
  for (const k of Object.keys(over)) out[k] = k in base ? merge(base[k], over[k]) : over[k];
  return out;
}
// the chain a definition stands on, oldest first: frames/horse -> horse; items/weapons/sword -> ...gladius
export function chain(def, bank, seen = new Set()) {
  if (!def?.use) return [def];
  if (seen.has(def.use)) throw new Error(`definitions: "${def.use}" uses itself`);
  seen.add(def.use);
  const parent = bank.get(def.use) ?? bank.get(def.use + ".json");
  if (!parent) throw new Error(`definitions: no definition "${def.use}"`);
  return [...chain(parent, bank, seen), def];
}
// a definition with everything it stands on merged in (its `use` gone)
export function flatten(def, bank) {
  let flat = {};
  for (const d of chain(def, bank)) flat = merge(flat, d);
  delete flat.use;
  return flat;
}
