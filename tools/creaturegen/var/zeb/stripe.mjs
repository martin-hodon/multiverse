// stripe.mjs DUMP.json POINTS.json : the zebra band (coatpat.js stripesOf, zebra=1) at rest-pose points -- the
// body's pattern frame fitted (affine, least squares) from the dumped crest vertices' own pattern coordinates
// (patId 4, kt 1, scale 1); POINTS {pts: [[x,y,z]...], S: [1, .6]} -> [[m at S0, m at S1, ...] ...]
import { readFileSync } from "fs";
const D = JSON.parse(readFileSync(process.argv[2])), Q = JSON.parse(readFileSync(process.argv[3]));
const f = Math.fround, fract = (x) => f(x - Math.floor(x)), mix = (a, b, t) => a + (b - a) * t;
const hash33x = (c) => fract(f(Math.sin(f(f(c[0] * 127.1) + f(c[1] * 311.7) + f(c[2] * 74.7))) * 43758.55));
const vn3 = (p) => { const g = p.map(Math.floor), fr = p.map((v, k) => { const t = v - g[k]; return t * t * (3 - 2 * t); });
  const h = (i, j, k) => hash33x([g[0] + i, g[1] + j, g[2] + k]);
  return mix(mix(mix(h(0,0,0), h(1,0,0), fr[0]), mix(h(0,1,0), h(1,1,0), fr[0]), fr[1]), mix(mix(h(0,0,1), h(1,0,1), fr[0]), mix(h(0,1,1), h(1,1,1), fr[0]), fr[1]), fr[2]); };
const h11 = (x) => fract(f(Math.sin(f(f(x * 91.37) + 1.73)) * 43758.5453));
const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
function stripesOf(p, r, px = 0) {   // zebra = 1
  const rr = Math.max(r, .015), th = Math.atan2(p[2], p[1]), a = th * rr;
  const sp = Math.min(.15, Math.max(.08, .09 + .16 * rr)), wob = .45;
  const n1 = vn3([p[0] / sp * .45, a / sp * .32, 3.7]) - .5, n2 = vn3([p[0] / sp * 1.3 + 7.1, a / sp * 1.05, 9.2]) - .5;
  const X = p[0] / sp + wob * (.95 * n1 + .3 * n2 + .16 * Math.sin(a / sp * .8)), id = Math.floor(X), fx = X - id - .5;
  const h1 = h11(id * 1.37 + .11), h2 = h11(id * 2.71 + 3.3), h3 = h11(id * 5.13 + 1.9), h4 = h11(id * 9.7 + 4.4);
  const reach = mix(2.7, 3.6, h1), tt = Math.abs(th) / reach, hw0 = mix(.24, .34, h2);
  const hw = hw0 * Math.pow(Math.max(0, 1 - Math.pow(Math.min(tt, 1), 6)), .5);
  let d = Math.abs(fx) - hw; if (tt >= 1) d = 1;
  if (h3 < .22) { const reach2 = reach * mix(.35, .7, h4), t2 = Math.abs(th) / reach2;
    const hw2 = hw0 * .42 * Math.pow(Math.max(0, 1 - Math.min(t2, 1) ** 2), .7), off2 = h4 > .5 ? -.34 : .34;
    if (t2 < 1) d = Math.min(d, Math.abs(fx - off2) - hw2); }
  const aa = px / sp * 1.1 + .012;
  return 1 - smooth(-aa, aa, d);
}
// fit p_k = A_k . [x y z 1] over the crest vertices painted by the body's bands alone
const V = D.crest.filter((r) => r[6] === 4 && r[8] > .999 && r[13] > .1);   // (the animal frame: one girth; the head's own frame is far thinner)
const solve = (k) => {   // normal equations 4x4
  const M = Array.from({ length: 4 }, () => new Array(5).fill(0));
  for (const r of V) { const a = [r[0], r[1], r[2], 1], b = r[10 + k]; for (let i = 0; i < 4; i++) { for (let j = 0; j < 4; j++) M[i][j] += a[i] * a[j]; M[i][4] += a[i] * b; } }
  for (let i = 0; i < 4; i++) { let p = i; for (let j = i + 1; j < 4; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j; [M[i], M[p]] = [M[p], M[i]];
    for (let j = 0; j < 4; j++) if (j !== i) { const c = M[j][i] / M[i][i]; for (let l = i; l < 5; l++) M[j][l] -= c * M[i][l]; } }
  return M.map((row, i) => row[4] / row[i]);
};
const A = [0, 1, 2].map(solve), R0 = V.reduce((s, r) => s + r[13], 0) / V.length;
const pOf = (x) => A.map((c) => c[0] * x[0] + c[1] * x[1] + c[2] * x[2] + c[3]);
const err = Math.max(...V.map((r) => Math.max(...pOf(r).map((v, k) => Math.abs(v - r[10 + k])))));
console.error("fit on", V.length, "verts, max err", err.toFixed(5), "r", R0.toFixed(4), "A", JSON.stringify(A.map((c) => c.map((v) => +v.toFixed(4)))));
console.log(JSON.stringify(Q.pts.map((x) => (Q.S ?? [1]).map((S) => +stripesOf(pOf(x).map((v) => v / S), R0 / S).toFixed(3)))));
