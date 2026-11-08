// mantwing_probe.mjs JSON -- for mantwing.py: the creature in JSON built and posed (skeleton.js) in node; prints the
// rig's bones, their rest inverses, the frames at rest, SPREAD (aloft, the wing beat stilled) and at 8 phases aloft, and
// the wing's sculpt details (tri / membrane) as the overlay converts them
import { readFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
await import(R + "dragons.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { compileDef, writeAnimal, lastFrames } = await import(R + "skeleton.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const file = process.argv[2] ?? R + "assets/creatures/monsters/manticore.json";
const d = JSON.parse(readFileSync(file));
const def = sculptOf(markSculpt(buildCreature(d, bank)));
const parts = compileDef(def), B = def.sculpted, n = parts.length;
const pose = (fly, wingT, down = false) => {
  writeAnimal({ parts, position: { x: 0, y: 0, z: 0 }, rotY: 0, fly, flyT: fly, wingT, down, base: 0, amp: 0, sculpted: true, idx: 0 }, wingT, new Float32Array(n * 3), new Float32Array(n * 3), new Float32Array(n * 3));
  return lastFrames().map((m) => [...m.elements]);
};
const sp = parts.flight?.speed || .35, NPH = +(process.argv[3] ?? 8);
const out = { bones: B.bones, restInv: B.restInv, rest: pose(0, 0), fly: [] };
{ const keep = parts.map((p) => p.anim?.wing ? p.anim.deg : null); parts.forEach((p) => { if (p.anim?.wing) p.anim.deg = 0; }); out.spread = pose(1, 0); parts.forEach((p, i) => { if (keep[i] != null) p.anim.deg = keep[i]; }); }
for (let k = 0; k < NPH; k++) out.fly.push({ ph: k / NPH, M: pose(1, k / NPH / sp) });
out.det = B.details.filter((q) => /^w/.test(q.bone ?? "") || q.type === "membrane").map((q) => ({ id: q.id, type: q.type, bone: q.bone, a: q.a, b: q.b, c: q.c, r: q.r, pts: q.pts, tris: q.tris, bones: q.bones, skin: q.skin }));
out.prims = [...B.prims, ...B.details].filter((q) => /^w/.test(q.bone ?? "") && q.type !== "tri" && q.type !== "membrane").map((q) => ({ id: q.id, type: q.type, bone: q.bone, a: q.a, b: q.b, c: q.c, r: q.r, ra: q.ra, rb: q.rb }));
console.log(JSON.stringify(out));
