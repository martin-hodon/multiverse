// node --import ../../../reg.mjs lizprobe.mjs NAME RAYS.json OUT.json -- for each ray [ox, oy, oz, dx, dy, dz] (from inside the
// body outward) the first point where it leaves the sculpted surface (marched, then bisected) and the field's normal there:
// [px, py, pz, nx, ny, nz] (null when the ray never leaves within 5 cm). The paints are left out (they are no shape).
// Used by walllizard.py to lay its markings ON the skin.
import { readFileSync, writeFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { field } = await import(R + "sculpt.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const d = [...bank.values()].find((x) => x?.name === process.argv[2]);
const s = sculptOf(markSculpt(buildCreature(d, bank))).sculpted;
const F = field(s.prims.filter((p) => p.op !== "paint" && (p.op !== "sub" || /^cut/.test(p.src?.id ?? p.id ?? "")))), D = F.dist ?? F;   // (the head's cuts kept: they shape it; the ear and the eyes' sockets not)
const rays = JSON.parse(readFileSync(process.argv[3], "utf8"));
const out = rays.map(([x, y, z, dx, dy, dz]) => {
  const l = Math.hypot(dx, dy, dz); dx /= l; dy /= l; dz /= l;
  let t = 0, st = .00005;
  if (D(x, y, z) >= 0) return null;
  while (t < .05 && D(x + dx * t, y + dy * t, z + dz * t) < 0) t += st;
  if (t >= .05) return null;
  let a = t - st, b = t;
  for (let i = 0; i < 30; i++) { const m = (a + b) / 2; if (D(x + dx * m, y + dy * m, z + dz * m) < 0) a = m; else b = m; }
  const p = [x + dx * b, y + dy * b, z + dz * b], e = 1e-5;
  const n = [D(p[0] + e, p[1], p[2]) - D(p[0] - e, p[1], p[2]), D(p[0], p[1] + e, p[2]) - D(p[0], p[1] - e, p[2]), D(p[0], p[1], p[2] + e) - D(p[0], p[1], p[2] - e)];
  const nl = Math.hypot(...n) || 1;
  return [...p, ...n.map((v) => v / nl)].map((v) => +v.toFixed(6));
});
writeFileSync(process.argv[4], JSON.stringify(out));
console.log("probed", out.length, "rays,", out.filter((q) => !q).length, "missed");
