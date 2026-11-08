// surf3.mjs shapes.json queries.json -> for each {o:[x,y,z], d:[dx,dy,dz]} the distance from o along d to the skin
// (o must be inside), and the colour there. Shapes mirrored as bodyspec does.
import { field } from "/home/martin/store/apps/multiverse/sculpt.js";
import fs from "fs";
const shapes = JSON.parse(fs.readFileSync(process.argv[2]));
const Q = JSON.parse(fs.readFileSync(process.argv[3]));
const z = (v) => [v[0], v[1], -(v[2] ?? 0), ...v.slice(3)];
const all = shapes.flatMap((p) => p.mirror ? [p, { ...p, c: p.c && z(p.c), a: p.a && z(p.a), b: p.b && z(p.b), pts: p.pts && p.pts.map(z), rot: p.rot && [-p.rot[0], -p.rot[1], p.rot[2]] }] : [p]);
const names = [...new Set(all.map((p) => String(p.color)))];
const prims = all.map((p) => ({ ...p, attr: names.map((n) => (n === String(p.color) ? 1 : 0)) }));
const F = field(prims, names.length, { sharp: names.length });
console.log(JSON.stringify(Q.map(({ o, d }) => {
  const L = Math.hypot(...d), u = d.map((v) => v / L);
  if (F.dist(...o) > 0) return { t: null };
  let t = 0; while (t < 2 && F.dist(o[0] + u[0] * t, o[1] + u[1] * t, o[2] + u[2] * t) < 0) t += 0.001;
  return { t: +t.toFixed(4) };
})));
