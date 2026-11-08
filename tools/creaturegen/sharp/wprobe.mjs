// wprobe.mjs ASSETPATH[:variant] < {ids:[shape ids], rays:[[[from],[to]]...], grads:[[x,y,z]...], strands:true} : for whiskers.py -- the
// named shapes as resolved (the left one of a mirrored pair: c, r, type), the eyes, where rays from inside leave the
// body's surface, and (strands) the field's distance at each whisker strand's buried root and skin point (pts[0], pts[1])
import { readFileSync } from "fs";
await import("../canvas_shim.mjs");
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature, dressed } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { field } = await import(R + "sculpt.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const [path, vn] = process.argv[2].split(":"), req = JSON.parse(readFileSync(0, "utf8"));
const d0 = bank.get(path), d = vn ? { ...dressed(d0, { variant: vn }), name: d0.name + ":" + vn } : d0;
const def = buildCreature(d, bank), s = def.sculpted ? def : sculptOf(markSculpt(def)), B = s.sculpted;
const prims = B.prims;
const F = field(B.prims.filter((p) => p.op !== "paint"), 0);
const r4 = (v) => (Array.isArray(v) ? v.map(r4) : typeof v === "number" ? +v.toFixed(5) : v);
const out = { shapes: {}, eyes: B.eyes.map((e) => r4(e.at)), hits: [], strands: [] };
for (const id of req.ids ?? []) {
  const q = prims.filter((p) => p.id === id).sort((a, b) => ((b.c ?? b.a ?? b.pts?.[0])[2] - (a.c ?? a.a ?? a.pts?.[0])[2]))[0];
  if (q) out.shapes[id] = { type: q.type, c: r4(q.c ?? q.a ?? q.pts?.[0]), r: r4(q.r ?? q.ra ?? q.pts?.[0]?.[3]), b: r4(q.b) };
}
for (const [a, b] of req.rays ?? []) {
  const dir = b.map((v, k) => v - a[k]), L = Math.hypot(...dir), u = dir.map((v) => v / L), st = L / 400;
  const f = (t) => F.dist(a[0] + u[0] * t, a[1] + u[1] * t, a[2] + u[2] * t), inside = f(0) < 0;
  let hit = null;
  for (let t = 0; t < L * 3; t += st) if ((f(t) < 0) !== inside) { let lo = t - st, hi = t; for (let k = 0; k < 30; k++) { const m = (lo + hi) / 2; if ((f(m) < 0) === inside) lo = m; else hi = m; } hit = a.map((v, k) => +(v + u[k] * hi).toFixed(5)); break; }
  out.hits.push(hit);
}
// (grads: the field's gradient there, normalised -- the skin's outward normal at a point on it)
out.grads = (req.grads ?? []).map(([x, y, z]) => { const e = 1e-4, g = [F.dist(x + e, y, z) - F.dist(x - e, y, z), F.dist(x, y + e, z) - F.dist(x, y - e, z), F.dist(x, y, z + e) - F.dist(x, y, z - e)], l = Math.hypot(...g) || 1; return g.map((v) => +(v / l).toFixed(4)); });
if (req.strands) for (const q of B.details) if (q.strand) out.strands.push({ id: q.id, z: Math.sign(q.pts[0][2]), d0: +F.dist(...q.pts[0].slice(0, 3)).toFixed(5), d1: +F.dist(...q.pts[1].slice(0, 3)).toFixed(5), r: q.pts[0][3] });
console.log(JSON.stringify(out));
