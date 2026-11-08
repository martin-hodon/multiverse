// fd.mjs ASSETPATH < {exclude:[ids], points:[[x,y,z]...], rays:[[[from],[to]]...]} : the body field's distance at points,
// and where rays from inside come out of the surface (the shapes named excluded)
import { readFileSync } from "fs";
await import("../canvas_shim.mjs");
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { field } = await import(R + "sculpt.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const path = process.argv[2], req = JSON.parse(readFileSync(0, "utf8"));
const d = bank.get(path); const def = buildCreature(d, bank); const s = def.sculpted ? def : sculptOf(markSculpt(def));
const ex = new Set(req.exclude ?? []);
const prims = s.sculpted.prims.filter((p) => !ex.has(p.id) && p.op !== "paint");
const F = field(prims, 0);
const out = { d: (req.points ?? []).map((p) => +F.dist(p[0], p[1], p[2]).toFixed(5)), hits: [] };
for (const [a, b] of req.rays ?? []) {
  const dir = b.map((v, k) => v - a[k]), L = Math.hypot(...dir), u = dir.map((v) => v / L);
  let t = 0, hit = null; const st = L / 400;
  const f = (t) => F.dist(a[0] + u[0] * t, a[1] + u[1] * t, a[2] + u[2] * t);
  const inside = f(0) < 0;
  for (; t < L * 3; t += st) if ((f(t) < 0) !== inside) { let lo = t - st, hi = t; for (let k = 0; k < 30; k++) { const m = (lo + hi) / 2; if ((f(m) < 0) === inside) lo = m; else hi = m; } hit = a.map((v, k) => +(v + u[k] * hi).toFixed(5)); break; }
  out.hits.push(hit);
}
if (req.joints) { const bones = s.sculpted.bones; out.joints = Object.fromEntries(req.joints.map((j) => [j, s.sculpted.rest[bones.indexOf(j)]?.map((v) => +v.toFixed(4))])); }
console.log(JSON.stringify(out));
