// THE SEED'S GRAMMAR (docs/story.md), shared by the 2D engines: Greek paintings, stained glass, mosaic. A seed runs in streams by label, and a value in
// the data may be a choice: nothing here knows of a body or a colour.
// a seed's streams, one per label: changing what one label draws leaves the others as they were
export function stream(seed, ...labels) {
  let h = Math.imul((seed | 0) ^ 0x9e3779b9, 0x2c1b3c6d) ^ 2166136261;
  for (const c of labels.join("/")) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return () => {
    h = (h + 0x6d2b79f5) | 0;
    let t = Math.imul(h ^ (h >>> 15), 1 | h);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
// (neighbouring seeds are near in a stream's first draws: Greek's pictures are fixed by that now, so what's new scrambles first. Seeds 1, 2, 3 then differ as much as any)
export const scramble = (seed) => { let h = (seed | 0) ^ 0x51ed270b; h = Math.imul(h ^ (h >>> 16), 0x85ebca6b); h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35); return (h ^ (h >>> 16)) | 0; };
// a number, or a [low, high] a stream picks in
export const pick = (v, r, d = 0) => v === undefined ? d : Array.isArray(v) ? v[0] + (v[1] - v[0]) * r() : v;
// a value of the data: { p, v } a chance of v, { of: [...] } one of them, plain as it is; down through objects
export function resolve(v, r) {
  if (Array.isArray(v) || v === null || typeof v !== "object") return v;
  if ("of" in v) return resolve(v.of[Math.floor(r() * v.of.length)], r);
  if ("p" in v) return r() < v.p ? resolve("v" in v ? v.v : 1, r) : undefined;
  return Object.fromEntries(Object.entries(v).map(([k, q]) => [k, resolve(q, r)]));
}
// one of a list, and a list in the seed's order
export const one = (list, r) => list[Math.floor(r() * list.length)];
export const shuffled = (list, r) => { const a = [...list]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
