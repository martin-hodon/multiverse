// the snake's coat marks (rings, saddles, zig-zag, spots), laid on its rest-pose surface: op "paint" shapes, written out as JSON
import "./shim.mjs";
import { writeFileSync } from "fs";
const R0 = "/home/martin/store/apps/multiverse/";
const S = await import(R0 + "species.js"), B = await import(R0 + "bodyspec.js"), F = await import(R0 + "sculpt.js");
const o = B.sculptOf(S.A("snake")).sculpted;
const prims = o.prims, byId = (id) => prims.find((p) => p.id === id);
const F0 = F.field(prims.filter((p) => p.op !== "paint"));
const snap = (p) => F.onSurface(F0.dist, p, 8);
// the centreline: the trunk's tubes, head end first
const front = byId("front"), segs = [1, 2, 3, 4, 5, 6, 7].map((i) => byId("seg" + i));
const ctl = [...front.pts.map((q) => [...q]), ...segs.flatMap((t) => [t.pts[2], t.pts[3]].map((q) => [...q]))];
const cr = (a, b, c, d, t) => a.map((_, k) => .5 * (2 * b[k] + (-a[k] + c[k]) * t + (2 * a[k] - 5 * b[k] + 4 * c[k] - d[k]) * t * t + (-a[k] + 3 * b[k] - 3 * c[k] + d[k]) * t * t * t));
const at = (i) => ctl[Math.max(0, Math.min(ctl.length - 1, i))];
const line = [];
for (let i = 0; i < ctl.length - 1; i++) for (let s = 0; s < 24; s++) line.push(cr(at(i - 1), at(i), at(i + 1), at(i + 2), s / 24));
line.push(ctl[ctl.length - 1]);
const cum = [0];
for (let i = 1; i < line.length; i++) cum.push(cum[i - 1] + Math.hypot(line[i][0] - line[i - 1][0], line[i][1] - line[i - 1][1], line[i][2] - line[i - 1][2]));
const LEN = cum[cum.length - 1];
const nrm = (v) => { const l = Math.hypot(...v) || 1; return v.map((x) => x / l); };
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
function axis(s) {
  s = Math.max(0, Math.min(LEN - 1e-6, s));
  let i = 1; while (cum[i] < s) i++;
  const t = (s - cum[i - 1]) / (cum[i] - cum[i - 1]), p = line[i - 1].map((x, k) => x + (line[i][k] - x) * t);
  const T = nrm([line[i][0] - line[i - 1][0], 0, line[i][2] - line[i - 1][2]]), U = [0, 1, 0], Sd = cross(T, U);
  return { A: p.slice(0, 3), r: p[3], T, U, S: Sd };
}
// bones by length along: the body's tube is 0.25, then the segments
const BL = [["body", .25], ["seg1", .2], ["seg2", .2], ["seg3", .2], ["seg4", .2], ["seg5", .18], ["seg6", .15], ["seg7", .13]];
const boneAt = (s) => { let c = 0; for (const [b, l] of BL) { c += l; if (s < c) return b; } return "seg7"; };
const f5 = (x) => +x.toFixed(4);
const gx = (a, b) => (Math.abs(b) < 5e-6 ? f5(a) : `${f5(a)}${b < 0 ? "-" : "+"}${f5(Math.abs(b))}*girth`);
// a point on the surface at s along, phi round from the top (+: one side), with its offset written for any girth
function onBody(s, phi) {
  const { A, r, T, U, S: Sd } = axis(s), N = U.map((u, k) => u * Math.cos(phi) + Sd[k] * Math.sin(phi));
  const P = snap(A.map((a, k) => a + N[k] * r)), D = P.map((x, k) => x - A[k]);
  return { P, A, r, T, U, S: Sd, N, c: A.map((a, k) => gx(a - U[k] * r, D[k] + U[k] * r)) };
}
const out = [];
let n = 0;
// a frame (three unit columns) as Euler XYZ degrees (sculpt.js rotM: three.js's order)
const ax3 = ([e1, e2, e3]) => { const y = Math.asin(Math.max(-1, Math.min(1, e3[0]))), x = Math.atan2(-e3[1], e3[2]), z = Math.atan2(-e2[0], e1[0]);
  return [x, y, z].map((a) => +(a * 180 / Math.PI).toFixed(1)); };
// a blotch: centred on the surface, `al` along, `ar` round (radians of the girth), `rn` deep
function blotch(when, color, s, phi, al, ar, { rn = null, rot = 0, kc = .0007 } = {}) {
  const b = onBody(s, phi), e1 = b.T.map((t, k) => t * Math.cos(rot) + cross(b.N, b.T)[k] * Math.sin(rot)), e2 = b.N, e3 = cross(e1, e2);
  out.push({ id: `pz_${when}${n++}`, when, op: "paint", type: "ell", bone: boneAt(s), c: b.c,
    r: [f5(al), `${f5(rn ?? b.r * .8)}*girth`, `${f5(ar * b.r)}*girth`], rot: ax3([e1, e2, e3]), kc, color });
}
// a ring right round: an ellipsoid on the axis, twice the girth across (its band on the surface ~.87 of its length)
function ring(when, color, s0, s1, kc = .0007) {
  const s = (s0 + s1) / 2, b = axis(s), half = (s1 - s0) / 2 / .866, c = b.A.map((a, k) => gx(a - b.U[k] * b.r, b.U[k] * b.r));
  out.push({ id: `pz_${when}${n++}`, when, op: "paint", type: "ell", bone: boneAt(s), c, r: [f5(half), `${f5(2.1 * b.r)}*girth`, `${f5(2.1 * b.r)}*girth`],
    rot: ax3([b.T, b.U, b.S]), kc, color });
}
// a stroke: a tube along the surface between (s, phi) points, `w` wide
function stroke(when, color, pts, w, kc = .0006) {
  const P = pts.map(([s, phi]) => onBody(s, phi));
  out.push({ id: `pz_${when}${n++}`, when, op: "paint", type: "tube", bone: boneAt(pts[0][0]),
    pts: P.map((b) => [...b.c, `${f5(w / 2)}*girth`]), kc, color });
}
// on the head (no girth): points snapped onto it from a guess
const hp = (p) => snap(p).map(f5);
function hstroke(when, color, pts, w, kc = .0005) { out.push({ id: `pz_${when}${n++}`, when, op: "paint", type: "tube", bone: "head", pts: pts.map((p) => [...hp(p), w / 2]), kc, color }); }
function hblot(when, color, c, r, kc = .0005) { out.push({ id: `pz_${when}${n++}`, when, op: "paint", type: "ell", bone: "head", c: hp(c), r, kc, color }); }
const rnd = ((seed) => () => (seed = (seed * 16807) % 2147483647) / 2147483647)(7);
const D2R = Math.PI / 180;

// ---- ADDER: the dark zig-zag down the spine, a row of spots low on each flank, the X on the crown, the stripe behind the eye
{
  const p = .052, A = 34 * D2R, s0 = .02, s1 = LEN - .03;
  const v = []; for (let s = s0, k = 0; s < s1; s += p / 2, k++) v.push([s, (k % 2 ? 1 : -1) * A * Math.min(1, .35 + (LEN - s) / .5)]);
  for (let i = 0; i + 1 < v.length; i++) stroke("zig", "@mark", [v[i], v[i + 1]], .016 * Math.max(.45, axis(v[i][0]).r / .0215));
  for (let s = s0 + p / 4, k = 0; s < LEN - .12; s += p / 2, k++) blotch("zig", "@mark", s, (k % 2 ? 1 : -1) * 84 * D2R, .0075, .26);
  hstroke("zig", "@mark", [[.745, .032, -.0065], [.727, .031, .0055], [.712, .029, .0085]], .0065);   // (the X: one arm, then the other)
  hstroke("zig", "@mark", [[.745, .032, .0065], [.727, .031, -.0055], [.712, .029, -.0085]], .0065);
  for (const z of [1, -1]) hstroke("zig", "@mark", [[.752, .025, .0135 * z], [.735, .022, .0172 * z], [.712, .019, .0175 * z], [.695, .019, .017 * z]], .0058);
}
// ---- SMOOTH SNAKE: two rows of small dark spots down the back (now and then joined across), the crown's dark patch, the eye stripe
{
  const p = .042;
  for (let s = .03, k = 0; s < LEN - .05; s += p, k++) {
    const sz = .55 + .45 * Math.min(1, (LEN - s) / .4);
    if (k % 5 === 2) blotch("dots", "@mark", s, 0, .0055 * sz, .75);
    else for (const z of [1, -1]) blotch("dots", "@mark", s + z * .004, z * 26 * D2R, .0055 * sz, .2);
    for (const z of [1, -1]) blotch("dots", "@mark", s + p / 2, z * 78 * D2R, .0035 * sz, .12);
  }
  hblot("dots", "@mark", [.718, .031, 0], [.02, .007, .011]);
  for (const z of [1, -1]) hstroke("dots", "@mark", [[.776, .025, .006 * z], [.762, .026, .0125 * z], [.735, .023, .0168 * z], [.705, .021, .017 * z], [.685, .022, .018 * z]], .0055);
}
// ---- CORN SNAKE: red saddles edged black down the back, smaller blotches low on the flanks, a chequered belly, the spearpoint between the eyes
{
  const p = .052;
  for (let s = .035, k = 0; s < LEN - .04; s += p, k++) {
    const sz = Math.max(.45, axis(s).r / .0215);
    blotch("saddles", "@mark", s, 0, .019 * sz, 1.32);
    blotch("saddles", "@fill", s, 0, .0158 * sz, 1.12);
    for (const z of [1, -1]) {
      blotch("saddles", "@mark", s + p / 2, z * 92 * D2R, .0085 * sz, .36);
      blotch("saddles", "@fill", s + p / 2, z * 92 * D2R, .0062 * sz, .25);
    }
  }
  hstroke("saddles", "@fill", [[.772, .031, 0], [.752, .032, .006], [.737, .031, .006], [.752, .032, -.006], [.772, .031, 0]], .005);
  for (const z of [1, -1]) hstroke("saddles", "@fill", [[.75, .025, .0135 * z], [.73, .021, .0168 * z], [.712, .02, .017 * z]], .0055);
}
// ---- CORAL SNAKE: black snout, a yellow band over the back of the head, then red, yellow, black, yellow down the body; the tail black and yellow
{
  hblot("rings", "@band", [.712, .024, 0], [.012, .022, .026]);
  const Rw = .052, Yw = .011, Bw = .042, tail = LEN - .2;
  let s = 0;
  ring("rings", "@mark", s, s + .03); s += .03;
  while (s < LEN) {
    ring("rings", "@band", s, s + Yw); s += Yw;
    if (s < tail) { ring("rings", "@fill", s, s + Rw); s += Rw; ring("rings", "@band", s, s + Yw); s += Yw; }
    else { ring("rings", "@mark", s, s + Bw * .8); s += Bw * .8; continue; }
    ring("rings", "@mark", s, s + Bw); s += Bw;
  }
}
// ---- PYTHON: big dark-brown blotches edged black along the back, a row along each flank, the spearhead on the crown
{
  const p = .07;
  for (let s = .04, k = 0; s < LEN - .04; s += p * (.85 + .3 * rnd()), k++) {
    const sz = Math.max(.5, axis(s).r / .0215), w = .9 + .25 * rnd();
    const ph = (rnd() - .5) * .25, lob = (rnd() - .5) * .02;
    blotch("blotch", "@mark", s, ph, .032 * sz, 1.35 * w, { rot: (rnd() - .5) * .5 });
    blotch("blotch", "@mark", s + lob, ph + (rnd() - .5) * .6, .02 * sz, 1.0 * w, { rot: (rnd() - .5) * .8 });
    blotch("blotch", "@fill", s, ph, .027 * sz, 1.15 * w, { rot: (rnd() - .5) * .4 });
    blotch("blotch", "@fill", s + lob, ph + (rnd() - .5) * .4, .016 * sz, .82 * w, { rot: (rnd() - .5) * .6 });
    for (const z of [1, -1]) {
      const t = s + p * (.45 + .1 * rnd());
      blotch("blotch", "@mark", t, z * (100 + 12 * rnd()) * D2R, .011 * sz, .38);
      blotch("blotch", "@fill", t, z * (100 + 12 * rnd()) * D2R, .0085 * sz, .26);
    }
  }
  hblot("blotch", "@mark", [.738, .032, 0], [.03, .006, .0105]);
  hblot("blotch", "@fill", [.737, .032, 0], [.026, .0062, .0078]);
  for (const z of [1, -1]) hstroke("blotch", "@mark", [[.76, .025, .0135 * z], [.73, .021, .0165 * z], [.705, .02, .016 * z]], .005);
}
writeFileSync(process.argv[2], JSON.stringify(out));
console.log("marks", out.length, "length", LEN.toFixed(3), Object.entries(out.reduce((m, q) => (m[q.when] = (m[q.when] ?? 0) + 1, m), {})));
