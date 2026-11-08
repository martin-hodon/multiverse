// surf.mjs shapes.json queries.json -> for each query {x, y, dir:[dy,dz]} the distance along dir (from (x,y,0)) to the surface,
// and the colour that wins there. Shapes: the sculpt's (numbers only), mirrored here as bodyspec does.
import { field } from "/home/martin/store/apps/multiverse/sculpt.js";
import fs from "fs";
const shapes = JSON.parse(fs.readFileSync(process.argv[2]));
const Q = JSON.parse(fs.readFileSync(process.argv[3]));
const z = (v) => [v[0], v[1], -(v[2] ?? 0), ...v.slice(3)];
const all = shapes.flatMap((p) => p.mirror ? [p, { ...p, c: p.c && z(p.c), a: p.a && z(p.a), b: p.b && z(p.b), pts: p.pts && p.pts.map(z), rot: p.rot && [-p.rot[0], -p.rot[1], p.rot[2]] }] : [p]);
const names = [...new Set(all.map((p) => String(p.color)))];
const prims = all.map((p) => { const at = names.map((n) => (n === String(p.color) ? 1 : 0)); return { ...p, attr: at }; });
const F = field(prims, names.length, { sharp: names.length });
const out = Q.map(({ x, y, dir, z0 = 0 }) => {
  const [dy, dz] = dir, L = Math.hypot(dy, dz), uy = dy / L, uz = dz / L;
  let t = 0; const st = 0.002;
  if (F.dist(x, y, z0) > 0) return { t: null };
  while (t < 2 && F.dist(x, y + uy * t, z0 + uz * t) < 0) t += st;
  const o = new Array(names.length).fill(0); F.at(x, y + uy * t, z0 + uz * t, o);
  const i = o.indexOf(Math.max(...o));
  return { t: +t.toFixed(4), col: names[i], w: +o[i].toFixed(2) };
});
console.log(JSON.stringify(out));
