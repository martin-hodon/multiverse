import { hornMesh, finMesh } from "/home/martin/store/apps/multiverse/sharp.js";
const chk = (name, G) => {
  const nv = G.P.length / 3, bad = G.P.concat(G.N).some((v) => !isFinite(v));
  let maxT = 0; for (const t of G.T) maxT = Math.max(maxT, t);
  let nl = 0; for (let i = 0; i < nv; i++) nl = Math.max(nl, Math.abs(Math.hypot(G.N[3*i], G.N[3*i+1], G.N[3*i+2]) - 1));
  console.log(name, "verts", nv, "tris", G.T.length / 3, "nan", bad, "idx ok", maxT < nv, "normal err", nl.toFixed(4), "C", G.C.length / 3 === nv, "SW", G.SW.length / 4 === nv);
};
const horn = { type: "horn", pts: [[0, 0, 0, .02], [.05, .03, 0, .018], [.08, .08, 0, .012], [.07, .13, 0, .004]], up: [0, 0, 1], flat: .5, keel: .1, color: "#ffffff", tip: "#202020", tipAt: .6, bone: "head", bone2: "jaw" };
for (const li of [0, 1]) chk("horn li" + li, hornMesh(horn, li, (b) => (b === "jaw" ? 2 : 1)));
const H = hornMesh(horn, 0); console.log("apex", H.P.slice(-3 * (13)).slice(0, 3), "expected", horn.pts[3].slice(0, 3));
const fin = { type: "fin", root: [[.1, -.03, 0], [-.2, -.03, 0]], edge: [[.12, .02, 0, 2], [0, .15, 0, 2], [-.2, .26, 0], [-.18, .12, 0], [-.21, .02, 0]], corners: [2], thick: .04, color: "#556070", bone: "body" };
for (const li of [0, 1]) chk("fin li" + li, finMesh(fin, li));
const ear = { type: "fin", root: [[0, 0, -.02], [0, 0, .02]], edge: [[0, .05, -.03], [0, .1, 0], [0, .05, .03]], corners: [1], face: [1, 0, 0], cup: .5, thick: .006, inner: "#f0d0d0", innerRim: .004, color: "#303030" };
const Ge = finMesh(ear, 0); chk("ear", Ge);
// is the tip exact?
let best = 1; for (let i = 0; i < Ge.P.length / 3; i++) best = Math.min(best, Math.hypot(Ge.P[3*i], Ge.P[3*i+1] - .1, Ge.P[3*i+2])); console.log("ear tip dist", best);
