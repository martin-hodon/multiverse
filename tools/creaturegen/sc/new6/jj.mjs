// jj.mjs name -> JSON of joints {id: {o:[..], a:[..], b:[..]}} plus rig parts sizes
import { readFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
await import(R + "dragons.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch {} }
const d = process.argv[3] ? JSON.parse(readFileSync(process.argv[3])) : JSON.parse(JSON.stringify([...bank.values()].find((x) => x?.name === process.argv[2])));
delete d.sculpt;
const def = buildCreature(d, bank);
const s = sculptOf(markSculpt(def)).sculpted;
const out = {};
s.bones.forEach((b, i) => out[b] = { o: s.rest[i] });
for (const q of s.prims) { const o = out[q.bone] ?? (out[q.bone] = {}); if (o.a) continue; if (q.type === "cone") { o.a = q.a; o.b = q.b; o.ra = q.ra; o.rb = q.rb; } else if (q.type === "ell") { o.c = q.c; o.r = q.r; } else if (q.type === "tube") { o.pts = q.pts; } }
for (const q of s.details) { const o = out[q.bone] ?? (out[q.bone] = {}); if (q.type === "tri") { o.tri = [q.a, q.b, q.c]; } else if (q.a) { o.a = q.a; o.b = q.b; o.ra = q.ra; o.rb = q.rb; } }
console.log(JSON.stringify(out));
