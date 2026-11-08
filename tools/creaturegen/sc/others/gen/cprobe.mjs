// node cprobe.mjs NAME 'without,ids' '[[x,y,z0,dx,dy,dz],...]' -> distance along each ray (from (x,y,z0) toward d) to the surface
import { readFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { field } = await import(R + "sculpt.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json")));
const d = [...bank.values()].find((x) => x?.name === process.argv[2]);
const s = sculptOf(markSculpt(buildCreature(d, bank))).sculpted, wo = (process.argv[3] || "").split(",");
const RX = process.env.RX ? new RegExp(process.env.RX) : null;
const F = field(s.prims.filter((p) => !wo.some((w) => w && (p.id ?? "").startsWith(w)) && !(RX && RX.test(p.id ?? "")))); const dist = F.dist || F;
for (const [x, y, z, dx, dy, dz] of JSON.parse(process.argv[4])) {
  let t = 0; while (t < .5 && dist(x + dx * t, y + dy * t, z + dz * t) < 0) t += .0002;
  console.log([x, y, z].join(","), "surface at", [x + dx * t, y + dy * t, z + dz * t].map((v) => v.toFixed(4)).join(","));
}
