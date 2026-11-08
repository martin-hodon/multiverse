// node tbuild.mjs PATH FILE.json : build time of FILE as if it were asset PATH
await import("../canvas_shim.mjs");
import { readFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
await import(R + "dragons.js").catch(() => {}); await import(R + "winged.js").catch(() => {});
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { buildBody } = await import(R + "bodymesh.js");
const index = JSON.parse(readFileSync(R + "assets/index.json")); const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const d = JSON.parse(readFileSync(process.argv[3])); bank.set(process.argv[2], d);
const def = buildCreature(d, bank); const s = def.sculpted ? def : sculptOf(markSculpt(def));
const t0 = Date.now(); const B = buildBody(s.sculpted);
console.log(process.argv[2].split("/").pop(), "cell", s.sculpted.mesh.cell.toFixed(3), "ms", Date.now() - t0, "tris", B.lods.map((l) => l.index.length / 3).join("/"));
