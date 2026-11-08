// node birds/dump.mjs "<name>" out.bin -- the near LOD (pos, nor, col, index) of one creature, for rast.py
import { readFileSync, writeFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { buildBody } = await import(R + "bodymesh.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
for (const [path, d] of bank) {
  if (!path.startsWith("creatures/") || d?.name !== process.argv[2]) continue;
  const def = buildCreature(d, bank), s = def.sculpted ? def : sculptOf(markSculpt(def));
  const m = buildBody(s.sculpted).lods[0];
  const n = m.pos.length / 3, t = m.index.length / 3;
  const buf = Buffer.alloc(8 + n * 36 + t * 12);
  buf.writeInt32LE(n, 0); buf.writeInt32LE(t, 4);
  let o = 8;
  for (const a of [m.pos, m.nor, m.col]) { for (let i = 0; i < n * 3; i++) { buf.writeFloatLE(a[i], o); o += 4; } }
  for (let i = 0; i < t * 3; i++) { buf.writeInt32LE(m.index[i], o); o += 4; }
  writeFileSync(process.argv[3], buf); console.log(d.name, n, "verts", t, "tris", "col len", m.col.length / n);
  break;
}
