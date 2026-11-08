// dump the zebra's LOD0 vertices near the eye and along the crest: pos, col, pattern id/kt/p
import { readFileSync, writeFileSync } from "fs";
await import("../../canvas_shim.mjs");
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { buildBody } = await import(R + "bodymesh.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const file = process.argv[2] ?? (R + "assets/creatures/mammals/zebra.json");
const d = JSON.parse(readFileSync(file));
const def = buildCreature(d, bank), s = def.sculpted ? def : sculptOf(markSculpt(def));
const B = buildBody(s.sculpted), L = B.lods[0];
console.log("lod keys", Object.keys(L), "patScale", s.sculpted.patScale);
const P = L.pos, n = P.length / 3, out = { eye: [], crest: [] };
const E = s.sculpted.eyes?.[0]?.c ?? s.sculpted.eyes?.[0]?.at ?? null; console.log("eye", E, s.sculpted.eyes?.[0]?.r);
for (let v = 0; v < n; v++) {
  const x = P[3*v], y = P[3*v+1], z = P[3*v+2];
  const rec = [x, y, z, L.col[3*v], L.col[3*v+1], L.col[3*v+2], L.patId[3*v], L.patId[3*v+1], L.patKT[3*v], L.patKT[3*v+1], ...L.patP.slice(4*v, 4*v+4)];
  if (E && Math.hypot(x - E[0], y - E[1], Math.abs(z) - Math.abs(E[2])) < .06) out.eye.push(rec);
  if (Math.abs(z) < .03 && x > .2 && x < 1.25 && y > 1.2) out.crest.push(rec);
}
writeFileSync(process.argv[3] ?? "var/zeb/dump.json", JSON.stringify(out));
console.log("eye verts", out.eye.length, "crest verts", out.crest.length);
