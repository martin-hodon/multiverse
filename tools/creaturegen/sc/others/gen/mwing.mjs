// the rest-frame triangles of a creature's kept rig membranes, as the sculpt overlay converts them (bodyspec.js convert):
// node mwing.mjs NAME 'REGEX' -> [{id, bone, a, b, c, r}]
import { readFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json")));
const d = [...bank.values()].find((x) => x?.name === process.argv[2]);
const def = buildCreature(d, bank);
def.sculpt = { ...def.sculpt, keep: [process.argv[3]], shape: [{ id: "probe", type: "sphere", c: [0, 1, 0], r: .1, bone: "body" }] };
const s = sculptOf(markSculpt(def)).sculpted, re = new RegExp(`^(?:${process.argv[3]})$`);
const out = [...s.prims, ...s.details].filter((q) => q.type === "tri" && re.test(q.bone ?? "")).map((q) => ({ bone: q.bone, a: q.a, b: q.b, c: q.c, r: q.r }));
console.log(JSON.stringify(out));
