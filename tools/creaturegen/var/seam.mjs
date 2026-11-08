import { readFileSync, writeFileSync } from "fs";
import { deflateSync } from "zlib";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature, dressed } = await import(R + "creatures.js").then((m) => ({ ...m, dressed: m.dressed }));
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { buildBody } = await import(R + "bodymesh.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const [name, out, opt] = process.argv.slice(2);
let d = [...bank.values()].find((q) => q?.name === name);
if (!d) { console.log("no", name); process.exit(1); }
d = JSON.parse(JSON.stringify(d));
if (process.env.DROP) { const re = new RegExp(process.env.DROP); d.sculpt.shape = d.sculpt.shape.filter((q) => !re.test(q.id)); }
if (opt) {
  if (opt.startsWith("coat:")) { const c = d.coats[+opt.slice(5)]; const { name: _n, scale, params, ...cols } = c; d.colors = { ...d.colors, ...cols }; d.params = { ...(d.params ?? {}), ...(params ?? {}) }; }
  else { const v = d.variants[opt]; d.colors = { ...d.colors, ...(v.colors ?? {}) }; d.params = { ...(d.params ?? {}), ...(v.params ?? {}) }; }
  delete d.coats; delete d.variants;
}
const def = buildCreature(d, bank);
const s = def.sculpted ? def : sculptOf(markSculpt(def));
const B = buildBody(s.sculpted);
const L = B.lods[0];
const nv = L.pos.length / 3, P = L.pos, C = L.col, N = L.nor, I = L.index;
const pid = L.patId, kt = L.patKT, NS = pid.length / nv, SL = [L.patP, L.patQ, L.patR].slice(0, NS);   // (three slots since 2026-11-08)
console.log("attrs", Object.keys(L).join(","));
const share = (a, k) => kt[NS*a] * (k ? kt[NS*a+k] : 1 - [...Array(NS - 1)].reduce((s, _, j) => s + kt[NS*a+1+j], 0));
const bad = [];
for (let t = 0; t < I.length; t += 3) {
  const v = [I[t], I[t+1], I[t+2]];
  const c = [0,1,2].map((k) => (P[3*v[0]+k]+P[3*v[1]+k]+P[3*v[2]+k])/3);
  if (+process.env.ONLYLEG && !(c[0] > (+process.env.X0 || .3) && c[0] < (+process.env.X1 || .7) && c[1] < .6 && c[1] > (+process.env.YMIN || .05))) continue;
  let el = 0;
  const j = SL.map(() => 0);
  for (let i = 0; i < 3; i++) for (let k = i+1; k < 3; k++) {
    const a = v[i], b = v[k];
    el = Math.max(el, Math.hypot(P[3*a]-P[3*b], P[3*a+1]-P[3*b+1], P[3*a+2]-P[3*b+2]));
    SL.forEach((q, s) => { j[s] = Math.max(j[s], Math.hypot(q[4*a]-q[4*b], q[4*a+1]-q[4*b+1], q[4*a+2]-q[4*b+2])); });
  }
  const w = SL.map((_, s) => Math.max(...v.map((a) => share(a, s))));
  if (SL.some((_, s) => j[s] > 4*el && w[s] > .02)) bad.push({ c: c.map((x)=>+x.toFixed(3)), j: j.map((x) => +x.toFixed(3)), el: +el.toFixed(3), ids: v.map((a)=>[...pid.slice(NS*a, NS*a+NS)].join("/")).join(" "), kt: v.map((a)=>[...kt.slice(NS*a, NS*a+NS)].map((x) => x.toFixed(2)).join("/")).join(" "), r: v.map((a)=>SL.map((q) => q[4*a+3].toFixed(3)).join("|")).join(" ") });
}
console.log("bad", bad.length, "zneg", bad.filter((b)=>b.c[2]<0).length, "zpos", bad.filter((b)=>b.c[2]>0).length);
for (const b of bad.slice(0, +process.env.N || 40)) console.log(JSON.stringify(b));
