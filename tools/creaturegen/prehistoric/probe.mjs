// probe.mjs FILE.json < {joints: true, points: [[x,y,z]...], exclude: [ids], rays: [[[from],[to]]...]}
// A species JSON given as a FILE (it need not be in assets/index.json yet): its rig's rest joints, the body field's
// distance at points (the shapes named excluded) and where rays from inside leave the surface. The prehistoric
// generators (gen.py) read the joints to put the legs' shapes on them and sink horn and ear roots in the head.
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
const d = JSON.parse(readFileSync(process.argv[2])), req = JSON.parse(readFileSync(0, "utf8") || "{}");
const def = buildCreature(d, bank), s = def.sculpted ? def : sculptOf(markSculpt(def)), B = s.sculpted;
const out = {};
if (req.joints) out.joints = Object.fromEntries(B.bones.map((b, i) => [b, B.rest[i].map((v) => +v.toFixed(4))]));
if (req.points || req.rays) {
  const ex = new Set(req.exclude ?? []);
  const F = field(B.prims.filter((p) => !ex.has(p.id) && p.op !== "paint"), 0);
  out.d = (req.points ?? []).map((p) => +F.dist(p[0], p[1], p[2]).toFixed(5));
  out.hits = [];
  for (const [a, b] of req.rays ?? []) {
    const dir = b.map((v, k) => v - a[k]), L = Math.hypot(...dir), u = dir.map((v) => v / L), st = L / 400;
    const f = (t) => F.dist(a[0] + u[0] * t, a[1] + u[1] * t, a[2] + u[2] * t), inside = f(0) < 0;
    let hit = null;
    for (let t = 0; t < L * 3; t += st) if ((f(t) < 0) !== inside) { let lo = t - st, hi = t; for (let k = 0; k < 30; k++) { const m = (lo + hi) / 2; if ((f(m) < 0) === inside) lo = m; else hi = m; } hit = a.map((v, k) => +(v + u[k] * hi).toFixed(5)); break; }
    out.hits.push(hit);
  }
}
console.log(JSON.stringify(out));
