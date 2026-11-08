// probe.mjs SPECIES.json QUERIES.json : rays through the sculpt field without its mane -- each query {o:[x,y,z], d:[dx,dy,dz]}:
// from o (inside the body) along d, the distance to where it leaves the surface; null if o is outside. Rest frame,
// mirrored shapes doubled as bodyspec does; mane shapes (old slab ells, the forelock, new locks) left out.
import { field } from "/home/martin/store/apps/multiverse/sculpt.js";
import fs from "fs";
const d = JSON.parse(fs.readFileSync(process.argv[2]));
const MANE = /^(mane\d+P?|maneT\d+|forelock|lk[A-Z]\w*|fl\d+\w*|brush\w*)$/;
const num = (p) => typeof (p.c?.[0] ?? p.a?.[0] ?? p.pts?.[0]?.[0]) === "number";
const shapes = d.sculpt.shape.filter((p) => !MANE.test(p.id ?? "") && !p.op && p.type !== "feathers" && p.type !== "membrane" && num(p));
const z = (v) => [v[0], v[1], -(v[2] ?? 0), ...v.slice(3)];
const all = shapes.flatMap((p) => p.mirror ? [p, { ...p, c: p.c && z(p.c), a: p.a && z(p.a), b: p.b && z(p.b), pts: p.pts && p.pts.map(z), rot: p.rot && [-p.rot[0], -p.rot[1], p.rot[2]] }] : [p]);
const F = field(all.map((p) => ({ ...p, attr: [1] })), 1, {});
const Q = JSON.parse(fs.readFileSync(process.argv[3]));
console.log(JSON.stringify(Q.map(({ o, d }) => {
  const L = Math.hypot(...d), u = d.map((v) => v / L);
  if (F.dist(...o) > 0) return null;
  let t = 0; while (t < 1.5 && F.dist(...o.map((v, k) => v + u[k] * t)) < 0) t += .0015;
  return +t.toFixed(4);
})));
