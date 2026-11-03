// A WINDOW'S LAYOUT (docs/glass.md): lights and quarries as pieces, panel by panel, each cut on its own so that a window costs what a
// panel costs. A lancet: a border of blocks and pearls, then panels one above another between iron bars; each a medallion on a
// diaper, a saint under a canopy, or white grisaille. Nothing here knows of a picture's name: that's in the generator.
import { lancet, circle, foil, stoneRose } from "./forms.js";
import { buildFigure, placed, curve } from "../medieval/figure.js";
import { stream } from "../story/seed.js";
import { composeScene, personPieces, CANON } from "../story/compose.js";
import { inPoly } from "./panes.js";
import { planLight, planRose, DYE, tintName } from "./window.js";

const clipY = (poly, y0, y1) => {                                     // (a convex polygon between two levels)
  const one = (pts, y, keep) => { const o = []; pts.forEach((a, i) => { const b = pts[(i + 1) % pts.length], ia = keep(a[1]), ib = keep(b[1]); if (ia) o.push(a); if (ia !== ib) { const t = (y - a[1]) / (b[1] - a[1]); o.push([a[0] + (b[0] - a[0]) * t, y]); } }); return o; };
  return one(one(poly, y0, (v) => v >= y0), y1, (v) => v <= y1);
};
// a ring as one polygon, joined by a slit (same piece on both sides of it, so it dissolves)
const ring = (outer, inner) => [...outer, outer[0], inner[0], ...[...inner].reverse().slice(0, -1), inner[0]];

const resample = (pts, n) => {
  const L = pts.map((p, i) => Math.hypot(pts[(i + 1) % pts.length][0] - p[0], pts[(i + 1) % pts.length][1] - p[1])), T = L.reduce((a, b) => a + b, 0), out = [];
  let e = 0, run = 0;
  for (let k = 0; k < n; k++) { const s = k * T / n; while (run + L[e] < s) { run += L[e]; e++; } const t = (s - run) / L[e], a = pts[e], b = pts[(e + 1) % pts.length]; out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]); }
  return out;
};

// THE BORDER: blocks round a light's rectangle between its edge and one `t` inside, the fills in turn. A light's panel stacks on the next, so it's all four sides.
// (what's scratched on a block of the border: France's lily, Castile's tower, a leaf, a chevron. Paint, no lead)
const MOTIF = {
  fleur: (s) => [[[0, 1], [.3, .4], [.2, 0], [.65, .35], [.7, .05], [.28, -.15], [.42, -.42], [.12, -.3], [.1, -.75], [-.1, -.75], [-.12, -.3], [-.42, -.42], [-.28, -.15], [-.7, .05], [-.65, .35], [-.2, 0], [-.3, .4]].map(([x, y]) => [x * s, y * s])],
  castle: (s) => [[[-.7, -.8], [.7, -.8], [.7, .45], [.42, .45], [.42, .8], [.14, .8], [.14, .45], [-.14, .45], [-.14, .8], [-.42, .8], [-.42, .45], [-.7, .45]].map(([x, y]) => [x * s, y * s])],
  leaf: (s) => [[[0, .9], [.5, .45], [.65, -.1], [.3, -.65], [.05, -.35], [0, -.9], [-.05, -.35], [-.3, -.65], [-.65, -.1], [-.5, .45]].map(([x, y]) => [x * s, y * s])],
  chevron: (s) => [[[-.8, -.1], [0, .7], [.8, -.1], [.8, -.6], [0, .2], [-.8, -.6]].map(([x, y]) => [x * s, y * s])],
};
function motifOf(name, a, b, c, d, every = 1, k = 0) {
  if (!name || k % every) return [];
  const mx = (a[0] + b[0] + c[0] + d[0]) / 4, my = (a[1] + b[1] + c[1] + d[1]) / 4, s = Math.min(Math.hypot(b[0] - a[0], b[1] - a[1]), Math.hypot(d[0] - a[0], d[1] - a[1])) * .4;
  return MOTIF[name](s).map((pts) => ({ pts: pts.map(([x, y]) => [mx + x, my + y]), fill: name === "castle" || name === "fleur" ? "#e8c557" : "#efe8cf" }));
}
function border(w, h, t, B, tileH) {
  const block = B.block ?? .16, fills = B.fills ?? [1, 0, 2, 0], X = w / 2 + .01, Y = h / 2 + .01, x = w / 2 - t, y = h / 2 - t, out = [];
  let c = 0;
  const rail = (a, b, p, q) => { const n = Math.max(1, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / block)); for (let i = 0; i < n; i++) { const m = (A, B2, k) => [A[0] + (B2[0] - A[0]) * k / n, A[1] + (B2[1] - A[1]) * k / n]; const P = [m(a, b, i), m(a, b, i + 1), m(p, q, i + 1), m(p, q, i)]; out.push({ pts: P, fill: fills[c % fills.length], role: "border", label: `b${c}`, paint: motifOf(B.motif, ...P, 2, c) }); c++; } };
  // (white glass runs on from one panel to the next, its frame only up the sides: a block lies across each tile's end, so the next panel's goes on in the same colour)
  if (B.sides) {
    const each = fills.length, n = Math.max(1, Math.round(tileH / block / each)) * each, b = tileH / n;
    for (const [e, f, k] of [[X, x, 0], [-X, -x, 1]]) for (let i = 0; i <= n; i++) { const y0 = -tileH / 2 + (i - .5) * b; out.push({ pts: [[e, y0], [e, y0 + b], [f, y0 + b], [f, y0]], fill: fills[(i + k) % each], role: "border", label: `b${k}${i}`, sheet: `b${k}${i % n}` }); }
    return out;
  }
  rail([-X, -Y], [X, -Y], [-x, -y], [x, -y]); rail([X, -Y], [X, Y], [x, -y], [x, y]); rail([X, Y], [-X, Y], [x, y], [-x, y]); rail([-X, Y], [-X, -Y], [-x, y], [-x, -y]);
  return out;
}
// pearls: scratched out of the paint on the strip they sit on, not glass of their own
const pearlsOn = (pts, r, c = "#efe8cf", gap = 2.6) => { const T = pts.reduce((a, p, i) => a + Math.hypot(pts[(i + 1) % pts.length][0] - p[0], pts[(i + 1) % pts.length][1] - p[1]), 0); return resample(pts, Math.round(T / (r * gap))).map((q) => ({ pts: circle(q, r, 8, .4), fill: c })); };

// THE DIAPER: the ground behind a medallion, a lattice of lozenges with a fleuron at each
function diaper(w, h, cy, D) {
  const d = D.d ?? .2, fills = D.fills ?? [1], out = [{ pts: [[-w, cy - h], [w, cy - h], [w, cy + h], [-w, cy + h]], fill: fills[0], role: "ground", label: "dg" }];
  const nx = Math.ceil(w / d) + 1, ny = Math.ceil(h / d) + 1, style = D.style ?? "lattice";
  if (style === "damask") {                                             // (one ground, painted, no lattice of lead: a later age's, and cheap)
    const lines = []; for (let j = -ny; j <= ny; j++) for (let i = -nx; i <= nx; i++) { const x = (i + (j & 1 ? .5 : 0)) * d, y = cy + j * d / 2; lines.push({ pts: foil([x, y], d * .22, 4, Math.PI / 4, .35, 4), fill: "#1d120b", alpha: .5 }); }
    out[0].paint = lines; out[0].fill = fills[0]; return out;
  }
  for (let j = -ny; j <= ny; j++) for (let i = -nx; i <= nx; i++) {
    const x = (style === "squares" ? i : (i + (j & 1 ? .5 : 0))) * d, y = cy + j * d * (style === "squares" ? 1 : .5);
    if (style === "squares") { const q = d * .5; out.push({ pts: [[x - q, y - q], [x + q, y - q], [x + q, y + q], [x - q, y + q]], fill: fills[(i + j + 1000) % fills.length], role: "diaper", label: `d${i},${j}` }); if (D.fleuron !== undefined) out.push({ pts: foil([x, y], d * .2, 4, 0, .3, 5), fill: D.fleuron, role: "fleuron", label: `f${i},${j}` }); continue; }
    if (style === "rings") { out.push({ pts: circle([x, y], d * .36, 12), fill: fills[(i + j + 1000) % fills.length] === fills[0] ? (fills[1] ?? fills[0]) : fills[0], role: "diaper", label: `d${i},${j}` }); continue; }
    out.push({ pts: [[x, y - d / 2], [x + d / 2, y], [x, y + d / 2], [x - d / 2, y]], fill: fills[(i + j + 1000) % fills.length], role: "diaper", label: `d${i},${j}` });
    if (D.fleuron !== undefined) out.push({ pts: foil([x, y], d * .15, 4, Math.PI / 4, .35, 5), fill: D.fleuron, role: "fleuron", label: `f${i},${j}` });
  }
  return out;
}

// A CANOPY: a gable on two shafts over a saint, its towers above, drawn up from y0, x half width w
function canopy(y0, w, top, C) {
  const out = [], f = C.fill ?? 2, g = C.fill2 ?? 4, a = w * .92, sh = (x) => ({ pts: [[x - .1 * w, y0 - .02], [x + .1 * w, y0 - .02], [x + .1 * w, top], [x - .1 * w, top]], fill: g, role: "canopy" });
  out.push(sh(-a), sh(a));
  const arch = lancet(0, y0 - .12 * w, 1.6 * w, 1.5 * w, { point: 1.05, n: 7 });
  out.push({ pts: [[-w, y0 - .13 * w], [w, y0 - .13 * w], [w, y0 + .55 * w], [0, y0 + 1.25 * w], [-w, y0 + .55 * w]], fill: f, role: "canopy", label: "gable", paint: [{ pts: [[-.9 * w, y0 + .52 * w], [0, y0 + 1.15 * w], [.9 * w, y0 + .52 * w]], w: .008 }] });
  out.push({ pts: arch, fill: C.arch ?? 1, role: "canopy", label: "arch" });
  const up = y0 + 1.25 * w;
  out.push({ pts: [[-.38 * w, up - .2 * w], [.38 * w, up - .2 * w], [.38 * w, top], [-.38 * w, top]], fill: g, role: "canopy", paint: Array.from({ length: 3 }, (_, i) => ({ pts: [[-.38 * w, up + i * .2 * w], [.38 * w, up + i * .2 * w]], w: .006 })) });
  for (const s of [-1, 1]) out.push({ pts: [[s * w * .92 - .14 * w, y0 + .4 * w], [s * w * .92 + .14 * w, y0 + .4 * w], [s * w * .92, y0 + 1.1 * w]], fill: f, role: "canopy" });
  return out;
}

// THE FIGURES of a panel: each a figure's spec in the layer, set on a line at (cy) in height s; the order's theirs
function castOf(cast, cx, base, s, seed) {
  const out = [];
  cast.forEach((F, i) => {
    const r = stream(seed, "fig", i), scale = s * (F.size ?? 1), own = placed(buildFigure({ id: `c${i}`, ...F }, r), scale, cx + (F.x ?? 0) * s, base + (F.y ?? 0) * s, 1);
    own.forEach((p, k) => { p.label ??= `c${i}.${k}`; });
    out.push(...own);
  });
  return out;
}

// PROPS: a thing a panel's scene stands among. Pure shapes, called by name from the layer
const PROP = {
  throne: (x, y, s, f) => [{ pts: [[x - 23 * s, y], [x + 23 * s, y], [x + 23 * s, y + 60 * s], [x + 19 * s, y + 64 * s], [x - 19 * s, y + 64 * s], [x - 23 * s, y + 60 * s]], fill: f ?? 2, role: "prop", paint: [{ pts: [[x - 23 * s, y + 42 * s], [x + 23 * s, y + 42 * s]], w: .7 * s }] }],
  ship: (x, y, s, f) => [{ pts: curve([[x - 44 * s, y + 26 * s], [x - 36 * s, y + 4 * s], [x + 36 * s, y + 4 * s], [x + 44 * s, y + 26 * s], [x + 32 * s, y + 16 * s], [x - 32 * s, y + 16 * s]], 4, true), fill: f ?? 8, role: "prop", paint: [{ pts: [[x - 38 * s, y + 10 * s], [x + 38 * s, y + 10 * s]], w: .7 * s }] }],
  wave: (x, y, s, f) => [{ pts: [[x - 60 * s, y - 2 * s], [x + 60 * s, y - 2 * s], ...curve([[x + 60 * s, y + 6 * s], [x + 30 * s, y + 10 * s], [x, y + 6 * s], [x - 30 * s, y + 10 * s], [x - 60 * s, y + 6 * s]], 4)], fill: f ?? 7, role: "prop", paint: [{ pts: curve([[x - 60 * s, y + 2 * s], [x - 20 * s, y + 4 * s], [x + 20 * s, y + 1 * s], [x + 60 * s, y + 3 * s]], 4), w: .5 * s }] }],
  tower: (x, y, s, f, t) => [{ pts: [[x - 12 * s, y], [x + 12 * s, y], [x + 12 * s, y + 60 * s], [x + 15 * s, y + 66 * s], [x, y + 85 * s], [x - 15 * s, y + 66 * s], [x - 12 * s, y + 60 * s]], fill: f ?? 4, role: "prop", paint: [{ pts: [[x - 12 * s, y + 60 * s], [x + 12 * s, y + 60 * s]], w: .7 * s }, { pts: curve([[x - 4 * s, y], [x - 4 * s, y + 14 * s], [x, y + 20 * s], [x + 4 * s, y + 14 * s], [x + 4 * s, y]], 3), w: .6 * s }] }],
  ground: (x, y, s, f) => [{ pts: [[x - 80 * s, y - 40 * s], [x + 80 * s, y - 40 * s], ...curve([[x + 80 * s, y], [x + 30 * s, y + 3 * s], [x - 30 * s, y - 1 * s], [x - 80 * s, y + 2 * s]], 4)], fill: f ?? 3, role: "prop" }],
};
const propsOf = (list, cx, base, s) => (list ?? []).flatMap((p, i) => {
  if (!PROP[p.is]) throw new Error(`no prop "${p.is}"`);
  return PROP[p.is](cx + (p.x ?? 0) * s, base + (p.y ?? 0) * s, s * (p.size ?? 1), p.fill, p.fill2).map((q, k) => ({ ...q, label: q.label ?? `pr${i}.${k}` }));
});

// A MEDALLION panel: circle, quatrefoil or lozenge, its band, its pearls, its scene
const shapeOf = (shape, cy, cx = 0) => (R) => shape === "quatrefoil" ? foil([cx, cy], R * 1.08, 4, 0, .22, 12) : shape === "barbed" ? foil([cx, cy], R * 1.02, 8, 0, .12, 7) : shape === "lozenge" ? [[cx, cy - R * 1.12], [cx + R * 1.12, cy], [cx, cy + R * 1.12], [cx - R * 1.12, cy]] : circle([cx, cy], R, 40);
function medallion(P, w, y0, y1, L, seed) {
  const cy = (y0 + y1) / 2, h = y1 - y0, r = Math.min(w, h) * (P.r ?? .46), shape = P.shape ?? "circle", band = r * .09, make = shapeOf(shape, cy);
  const inner = make(r - band), s = (2 * r * .72) / 100, base = cy - r * .72 + (P.drop ?? 0) * r;
  const hides = make(r * .96), out = [...diaper(w, h, cy, { d: w * .2, fills: L.ground ?? [1, 9], fleuron: L.fleuron, style: L.diaper }).filter((p) => !p.pts.every((q) => inPoly(q[0], q[1], hides))),      // (no lattice under the medallion: it costs, and shows nothing)
    { pts: make(r), fill: P.ground ?? 0, role: "medal", label: "md" }, ...propsOf(P.props, 0, base, s), ...castOf(P.cast ?? [], 0, base, s, seed), ...sceneIn(P, r - band, cy, seed, make, shape),
    { pts: ring(make(r * 1.04), inner), fill: P.band ?? 2, role: "band", label: "band", paint: L.pearl === undefined ? [] : pearlsOn(make(r * .985), band * .3) }];
  return out;
}
// A SCENE IN A FRAME: the story's pieces, none past the frame (`within`: it's the band that hides the edge)
function sceneIn(P, ri, cy, seed, make, shape) {
  if (!P.scene) return [];
  const k = shape === "lozenge" ? .64 : shape === "quatrefoil" ? .84 : .9, within = make(ri * 1.02), frame = { x0: -ri * k, x1: ri * k, y0: cy - ri * (shape === "lozenge" ? .62 : .76), y1: cy + ri * (shape === "lozenge" ? .62 : .8) };
  return composeScene(P.scene, { seed, dye: DYE, ground: tintName(P.ground ?? 0), frame, pxPerUnit: 512 }).pieces.map((p) => ({ ...p, within }));
}
// A CLUSTER: a great roundel and four small in the corners, as at Chartres: busts of those who look on
function cluster(P, w, y0, y1, L, seed) {
  const cy = (y0 + y1) / 2, h = y1 - y0, out = medallion({ ...P, r: Math.min(w, h) * (P.r ?? .4) / Math.min(w, h) * 1 }, w, y0, y1, L, seed), R = Math.min(w, h), m = R * .2, e = m * .7, c = [[-w / 2 + e, y0 + e], [w / 2 - e, y0 + e], [-w / 2 + e, y1 - e], [w / 2 - e, y1 - e]];   // (out into the corner, and over it: a crescent left behind a roundel would be a sliver of no glass)
  c.forEach(([x, y], i) => {
    const r = m, within = circle([x, y], r * .94, 24), who = P.busts?.[i % (P.busts.length || 1)] ?? "angel", ground = (P.ground ?? 0) === 1 ? 0 : 1, s = r * 1.5 / 45;
    out.push({ pts: circle([x, y], r, 24), fill: ground, role: "medal", label: `cm${i}` });
    out.push(...personPieces(who, { seed: seed + i, dye: DYE, ground: tintName(ground), wear: { bust: true, holdL: null, holdR: null, pose: "stand", wings: null }, label: `cp${i}`, coarse: true }).map((p, k) => { const f = ([a, b]) => [x + a * s, y - r * .95 + (b - 62) * s]; return { ...p, label: `cp${i}.${k}`, within, pts: p.pts.map(f), paint: p.paint?.map((l) => ({ ...l, w: (l.w ?? .4) * s, pts: l.pts.map(f) })) }; }));
    out.push({ pts: ring(circle([x, y], r * 1.06, 24), circle([x, y], r * .9, 24)), fill: P.band ?? 2, role: "band", label: `cb${i}` });
  });
  return out;
}
// THE TREE OF JESSE: he sleeps at the foot of the light; a vine out of him carries his line up, ovals of kings, to the Virgin and Christ with the doves about him
function jesse(P, w, y0, y1, L, seed) {
  const h = y1 - y0, out = [{ pts: [[-w, y0 - .01], [w, y0 - .01], [w, y1 + .01], [-w, y1 + .01]], fill: P.ground ?? 0, role: "ground", label: "jg", paint: hatching(w, y0, y1, w * .1) }], levels = Math.max(3, Math.round(h / (w * .78))), step = (h - w * .34) / levels, y = (k) => y0 + w * .34 + (k + .5) * step, W = w * .3;
  const stem = []; for (const s of [-1, 1]) { const L0 = [], R0 = []; for (let k = 0; k <= levels * 4; k++) { const q = k / (levels * 4), Y = y0 + w * .1 + (h - w * .1) * q, x = s * W * Math.sin(q * levels * Math.PI) ; L0.push([x - w * .018, Y]); R0.push([x + w * .018, Y]); } stem.push({ pts: [...L0, ...R0.reverse()], fill: 3, role: "stem", label: `st${s}` }); }
  out.push(...stem);
  for (let k = 0; k < levels * 2; k++) { const s = k % 2 ? 1 : -1, Yl = y0 + w * .3 + (k + .5) * step / 2, xl = s * w * .34; out.push({ pts: foil([xl, Yl], w * .05, 3, Math.PI / 2, .3, 4), fill: 3, role: "leaf", whole: true, label: `lf${k}` }); }
  const line = ["david", "king", "king", "king", "mary-queen", "christ"], who = [...line.slice(0, Math.max(0, levels - 2)), "mary-queen", "christ"];
  who.forEach((n, k) => {
    const Y = y(k), rx = w * .36, ry = step * .47, ov = (a, b) => Array.from({ length: 28 }, (_, i) => [a * Math.cos(i * Math.PI / 14), Y + b * Math.sin(i * Math.PI / 14)]), s = ry * 1.74 / 100, g = P.ground2 ?? 1;
    out.push({ pts: ov(rx, ry), fill: g, role: "medal", label: `jm${k}` });
    const q = personPieces(n, { seed: seed + k * 7, dye: DYE, ground: tintName(g), label: `j${k}`, wear: { pose: n === "christ" ? "bless" : "stand", ...(n === "king" ? null : null) }, coarse: k < levels - 2 });
    out.push(...q.map((p, i) => { const f = ([a, b]) => [a * s, Y - ry * .86 + b * s]; return { ...p, label: `jf${k}.${i}`, within: ov(rx * .96, ry * .96), pts: p.pts.map(f), paint: p.paint?.map((l) => ({ ...l, w: (l.w ?? .4) * s, pts: l.pts.map(f) })) }; }));
    out.push({ pts: ring(ov(rx * 1.08, ry * 1.06), ov(rx * .92, ry * .92)), fill: 2, role: "band", label: `jb${k}` });
  });
  const J = personPieces("jesse", { seed, dye: DYE, ground: tintName(P.ground ?? 0), label: "J", wear: { pose: "lie", holdL: null, holdR: null } });
  let lo = Infinity, hi = -Infinity, bot = Infinity; for (const p of J) for (const q of p.pts) { lo = Math.min(lo, q[0]); hi = Math.max(hi, q[0]); bot = Math.min(bot, q[1]); }
  const sj = w * .92 / (hi - lo), fj = ([a, b]) => [(a - (lo + hi) / 2) * sj, y0 + w * .02 + (b - bot) * sj];
  out.push(...J.map((p, i) => ({ ...p, label: `jj${i}`, pts: p.pts.map(fj), paint: p.paint?.map((l) => ({ ...l, w: (l.w ?? .4) * sj, pts: l.pts.map(fj) })) })));
  return out;
}

// A SAINT panel: a figure standing on a base, a canopy over him, a ground behind
function saint(P, w, y0, y1, L, seed) {
  const h = y1 - y0, base = y0 + h * .06, up = y0 + h * (P.spring ?? .68), s = (up - base) * 1.06 / 100, gw = w * (P.wide ? .46 : .44), ground = P.ground ?? 1;      // (the head stands in the canopy's arch)
  const inFront = [];
  if (P.scene) inFront.push(...composeScene(P.scene, { seed, dye: DYE, ground: tintName(ground), frame: { x0: -gw * .84, x1: gw * .84, y0: base, y1: up + gw * .5 }, pxPerUnit: 512 }).pieces);
  if (P.person) {
    const f = ([a, b]) => [a * s, base + b * s], mv = (p, i, tag) => ({ ...p, label: `${tag}${i}`, pts: p.pts.map(f), paint: p.paint?.map((l) => ({ ...l, w: (l.w ?? .4) * s, pts: l.pts.map(f) })) });
    inFront.push(...personPieces(P.person, { seed, dye: DYE, ground: tintName(ground), label: "s" }).map((p, i) => mv(p, i, "s")));
    if (P.donor) { const k = s * .42, g = ([a, b]) => [a * k - w * .3, base + b * k], who = seed & 1 ? "donor" : "donor-wife"; inFront.push(...personPieces(who, { seed, dye: DYE, ground: tintName(ground), wear: { pose: "kneel" }, label: "d", coarse: true }).map((p, i) => ({ ...p, label: `don${i}`, pts: p.pts.map(g), paint: p.paint?.map((l) => ({ ...l, w: (l.w ?? .4) * k, pts: l.pts.map(g) })) }))); }
  }
  return [{ pts: [[-w, y0 - .01], [w, y0 - .01], [w, y1 + .01], [-w, y1 + .01]], fill: ground, role: "ground", label: "sg", paint: hatching(w, y0, y1, w * .08) },
    { pts: [[-w, y0 - .01], [w, y0 - .01], [w, base], [-w, base]], fill: P.base ?? 3, role: "base", label: "sb", paint: [{ pts: [[-w, base - .02], [w, base - .02]], w: .006 }] },
    ...canopy(up, gw, y1 + .01, { fill: P.canopy ?? 2, fill2: P.canopy2 ?? 4, arch: P.arch ?? ground }), ...propsOf(P.props, 0, base, s), ...castOf(P.cast ?? [], 0, base, s, seed), ...inFront];
}
const hatching = (w, y0, y1, d) => { const out = []; for (let k = -40; k <= 40; k++) { const x = k * d; out.push({ pts: [[x - (y1 - y0), y0], [x + (y1 - y0), y1]], w: .0028, alpha: .3 }, { pts: [[x + (y1 - y0), y0], [x - (y1 - y0), y1]], w: .0028, alpha: .3 }); } return out; };

// A GRISAILLE panel: white quarries, a coloured strap over them, and painted vine
function grisaille(P, w, y0, y1, L, seed, tile) {
  const h = y1 - y0, cy = (y0 + y1) / 2, d = P.d ?? w * .2, I = Math.round(tile[0] / d), J = Math.round(tile[1] / d) * 2, out = [{ pts: [[-w, y0 - .01], [w, y0 - .01], [w, y1 + .01], [-w, y1 + .01]], fill: 0, role: "ground", label: "qg" }];
  const fillsW = P.whites ?? [0, 1, 2, 3], nx = Math.ceil(w / d) + 1, ny = Math.ceil(h / d) + 1;
  for (let j = -ny; j <= ny; j++) for (let i = -nx; i <= nx; i++) {
    // (a quarry its own chances, the same at each end of the tile: where tiles meet it's one quarry)
    const x = (i + (j & 1 ? .5 : 0)) * d, y = cy + j * d / 2, vine = [], sheet = ((i % I + I) % I) * 1000 + (j % J + J) % J, r = stream(seed, "gris", sheet);
    if (P.vine !== false) {                                      // (a leaf and a stem on each, painted: no lead in them)
      const a = r() * 6.28, ca = Math.cos(a) * d * .18, sa = Math.sin(a) * d * .18;
      vine.push({ pts: curve([[x - ca * 1.5, y - sa * 1.5], [x + sa * .6, y - ca * .6], [x + ca * 1.5, y + sa * 1.5]], 4), w: .004 }, { pts: foil([x + ca * 1.5, y + sa * 1.5], d * .085, 3, a, .3, 4), w: .0035, closed: true }, { pts: foil([x - ca * 1.5, y - sa * 1.5], d * .07, 3, a + 3, .3, 4), w: .0035, closed: true });
    }
    out.push({ pts: [[x, y - d / 2], [x + d / 2, y], [x, y + d / 2], [x - d / 2, y]], fill: fillsW[Math.floor(r() * fillsW.length)], role: "quarry", whole: true, label: `q${i},${j}`, sheet, paint: vine });
  }
  if (P.strap) {                                                // (the strapwork, in a little white on white, with a colour at the knots)
    const s = P.strap, m = (y1 - y0) / (s.n ?? 2), t = s.t ?? w * .05;
    for (let k = 0; k < (s.n ?? 2); k++) {
      const c = y0 + (k + .5) * m, R = Math.min(w, m / 2) * (s.r ?? .78), make = s.shape === "foil" ? (q) => foil([0, c], q, 4, 0, .22, 10) : (q) => circle([0, c], q, 32);
      out.push({ pts: ring(make(R + t), make(R)), fill: s.fill ?? 4, role: "strap", label: `s${k}` });
      out.push({ pts: circle([0, c], R * .22, 16), fill: s.knot ?? 6, role: "knot", label: `kk${k}` });
      for (let q = 0; q < 4; q++) { const a = q * Math.PI / 2 + Math.PI / 4; out.push({ pts: circle([R * Math.cos(a), c + R * Math.sin(a)], t * 1.1, 10), fill: s.knot2 ?? 5, role: "knot", label: `kn${k}${q}` }); }
    }
  }
  return out;
}
const KIND = { medallion, saint, grisaille, cluster, jesse };

// THE STONE'S ROSE: each thing its bars enclose is a little window of its own, cut alone. A light has a diaper and a
// medallion towards its head with one of `cast`; a roundel a foil on its colour; the hub whatever `hubCast` is.
export function stonePanels(L0, clipAll, R) {
  const L = L0.plan ? planRose(L0) : L0, pieces = stoneRose(L, R), cast = L.cast ?? [], seed = L.seed ?? 1, d = R * (typeof L.diaper === "number" ? L.diaper : .12), pearls = L.pearl ?? 4, T = L.theme;
  const inLight = (k, cx, cy, r, ground) => {                            // (who's in a light: a figure, or a month at his work)
    if (!T) return castOf(cast.length ? [cast[k % cast.length]] : [], cx, cy - r * .72, 2 * r * .72 / 100, seed + k);
    const within = circle([cx, cy], r * .98, 20), ri = r * .92, frame = { x0: cx - ri * .84, x1: cx + ri * .84, y0: cy - ri * .76, y1: cy + ri * .8 };
    if (T.months) return composeScene(CANON.cycles.months[(k + L.offset) % 12], { seed: seed + k, dye: DYE, ground: tintName(ground), frame, pxPerUnit: 512 }).pieces.map((p) => ({ ...p, within }));
    const who = T.lights[(k + L.offset) % T.lights.length], s = r * 1.85 / 42, f = ([a, b]) => [cx + a * s, cy - r * .92 + (b - 64) * s];   // (head and shoulders: anything more in a light this small is a smear of lead)
    return personPieces(who === "martyr" ? "lucy" : who, { seed: seed + k, dye: DYE, ground: tintName(ground), wear: { bust: true, wings: null, beside: null, underfoot: null, holdL: null, holdR: null, pose: "stand" }, coarse: true, label: `l${k}` }).map((p, i) => ({ ...p, label: `l${k}.${i}`, within, pts: p.pts.map(f), paint: p.paint?.map((l) => ({ ...l, w: (l.w ?? .4) * s, pts: l.pts.map(f) })) }));
  };
  const inHub = (r) => {
    if (!T) return castOf(L.hubCast ?? [], 0, -r * .72, 2 * r * .72 / 100, seed + 500);
    const within = circle([0, 0], r * .9, 28), frame = { x0: -r * .7, x1: r * .7, y0: -r * .66, y1: r * .72 }, name = T.hub === "lamb" ? "lamb-hub" : T.hub === "virgin" ? "virgin-hub" : T.hub === "christ" ? "majesty" : "majesty";
    return composeScene(name, { seed: seed + 500, dye: DYE, ground: "cobalt", frame, pxPerUnit: 512 }).pieces.map((p) => ({ ...p, within }));
  };
  const out = [{ clip: clipAll, pieces: [{ pts: circle([0, 0], R * 1.01, 96), fill: L.ground ?? 0, role: "ground", label: "ground" }, ...pieces.map((p) => ({ pts: p.pts, fill: 0, hole: true, label: "h" + p.label }))] }];
  let nl = 0, nr = 0;
  for (const P of pieces) {
    const mx = P.pts.reduce((a, p) => a + p[0], 0) / P.pts.length, my = P.pts.reduce((a, p) => a + p[1], 0) / P.pts.length;
    const low = Math.min(...P.pts.map((p) => p[1])), high = Math.max(...P.pts.map((p) => p[1])), reach = Math.max(...P.pts.map((p) => Math.hypot(p[0] - mx, p[1] - my)));
    if (P.role === "light") {
      const k = nl++, a = Math.atan2(my, mx), far = Math.max(...P.pts.map((p) => Math.hypot(p[0], p[1]))), near = Math.min(...P.pts.map((p) => Math.hypot(p[0], p[1])));
      const at = near + (far - near) * .6, cx = at * Math.cos(a), cy = at * Math.sin(a), half = Math.PI / Math.round(L.lights ?? 12), r = at * Math.sin(half) * .78, s = 2 * r * .72 / 100;
      const hide = circle([cx, cy], r * .96, 20), mk = (q) => circle([cx, cy], q, 28);
      const ground = diaper(reach * 1.1, reach * 1.1, 0, { d, fills: [P.fill, 9], fleuron: L.fleuron, style: T ? ("lattice") : undefined }).map((p) => ({ ...p, pts: p.pts.map((q) => [q[0] + mx, q[1] + my]) })).filter((p) => p.role === "ground" || !p.pts.every((q) => inPoly(q[0], q[1], hide)));
      out.push({ clip: P.pts, pieces: [...ground, { pts: mk(r), fill: (L.medals ?? [1, 0])[k % (L.medals?.length ?? 2)], role: "medal", label: "md" }, ...inLight(k, cx, cy, r, (L.medals ?? [1, 0])[k % (L.medals?.length ?? 2)]), { pts: ring(mk(r * 1.06), mk(r * .92)), fill: 2, role: "band", label: "band", paint: pearlsOn(mk(r * .99), r * .03) }] });
    } else if (P.role === "hub") {
      const r = reach * .94, s = 2 * r * .72 / 100, mk = (q) => circle([0, 0], q, 40);
      out.push({ clip: P.pts, pieces: [{ pts: circle([0, 0], reach * 1.1, 40), fill: L.hub ?? 2, role: "ground", label: "hg" }, { pts: mk(r * .88), fill: 0, role: "medal", label: "hm" }, ...inHub(r), { pts: ring(mk(reach * 1.1), mk(r * .88)), fill: L.hub ?? 2, role: "band", label: "hb", paint: pearlsOn(mk(r * .94), r * .03) }] });
    } else {
      const k = nr++;
      out.push({ clip: P.pts, pieces: [{ pts: circle([mx, my], reach * 1.1, 24), fill: P.fill, role: "roundel", label: "rg", paint: pearlsOn(circle([mx, my], reach * .86, 24), reach * .045) }, { pts: foil([mx, my], reach * .62, L.foils ?? (k % 2 ? 4 : 6), 0, .28, 8), fill: k % 2 ? 4 : 2, role: "inner", label: "ri" }, { pts: circle([mx, my], reach * .17, 10), fill: pearls === 4 ? 1 : pearls, role: "knot", label: "rk" }] });
    }
  }
  return out;
}

const rectOf = (w, h, y = 0) => [[-w / 2, y - h / 2], [w / 2, y - h / 2], [w / 2, y + h / 2], [-w / 2, y + h / 2]];
// a light: `panels` is [{ form, cast, h (share), ... }] from the foot up, in a rectangle that stacks on itself and goes up to the stone. -> [{ pieces, clip }]
// THE PEOPLE OF A ROSE OF RINGS: a bust in the inner shape of each of a ring's roundels
export function ringBusts(L, R) {
  const B = L.busts, Q = L.rings.filter((q) => q.shape && q.shape !== "sector")[B.ring], n = Q.n, out = [], rm = (Q.r0 + Q.r1) / 2 * R, half = Math.PI / n, room = Math.min((Q.r1 - Q.r0) / 2 * R, rm * Math.sin(half)), r = room * (Q.inner?.k ?? .55);
  for (let k = 0; k < n; k++) {
    const t = Math.PI / 2 + (k + (Q.turn ?? 0)) * 2 * half, x = rm * Math.cos(t), y = rm * Math.sin(t), g = (Q.inner?.fills ?? [2])[k % (Q.inner?.fills?.length ?? 1)], within = circle([x, y], r * .92, 16), s = r * 1.8 / 42, f = ([a, b]) => [x + a * s, y - r * .9 + (b - 64) * s];
    out.push({ pts: circle([x, y], r * .94, 16), fill: g === 2 ? 0 : 1, role: "medal", label: `bm${k}` });
    out.push(...personPieces(B.who[k % B.who.length], { seed: B.seed + k, dye: DYE, ground: tintName(g === 2 ? 0 : 1), wear: { bust: true, pose: "stand", holdL: null, holdR: null, wings: null, beside: null, underfoot: null }, coarse: true, label: `bb${k}` }).map((p, i) => ({ ...p, label: `bb${k}.${i}`, within, pts: p.pts.map(f), paint: p.paint?.map((l) => ({ ...l, w: (l.w ?? .4) * s, pts: l.pts.map(f) })) })));
  }
  return out;
}
// (the line inside a border: four strips, mitred. A ring of one piece would touch the border's leads along neither of its edges, and a net can't find a face with two separate outlines)
const lineRound = (W, H, w, h, fill, pearls) => {
  const X = W / 2, Y = H / 2, x = w / 2, y = h / 2;
  return [[[-X, -Y], [X, -Y], [x, -y], [-x, -y]], [[X, -Y], [X, Y], [x, y], [x, -y]], [[X, Y], [-X, Y], [-x, y], [x, y]], [[-X, Y], [-X, -Y], [-x, -y], [-x, y]]].map((pts, i) => ({ pts, fill, role: "line", label: `bl${i}`, sheet: "bl", paint: pearls.filter((q) => { const c = q.pts.reduce((a, p) => [a[0] + p[0] / q.pts.length, a[1] + p[1] / q.pts.length], [0, 0]), e = i % 2 ? Math.abs(c[0]) / X - Math.abs(c[1]) / Y : Math.abs(c[1]) / Y - Math.abs(c[0]) / X; return e >= 0 && (i === 0 ? c[1] < 0 : i === 1 ? c[0] > 0 : i === 2 ? c[1] > 0 : c[0] < 0); }) }));
};
export function panelsOf(L0, tile, clipAll) {
  const L = L0.plan ? planLight(L0) : L0;
  if (L.form !== "light") throw new Error(`no glass form "${L.form}"`);
  const W = L.opening?.w ?? tile[0], H = L.opening?.h ?? tile[1], B = L.border, t = B ? (B.t ?? W * .1) : 0, tb = B?.sides ? 0 : t, inner = rectOf(W - 2 * t, H - 2 * tb), over = B?.sides ? .04 : 0, out = [];
  if (B) {
    const pearls = B.pearl !== undefined ? pearlsOn(rectOf(W - 2 * t * .86, H - 2 * tb * .86 + over), t * .085, undefined, 3) : [], gap = rectOf(W - 2 * t, H - 2 * tb + over);
    out.push({ clip: clipAll, pieces: [...border(W, H, t, B, tile[1]), ...lineRound(W - 2 * t * .72, H - 2 * tb * .72 + over, W - 2 * t, H - 2 * tb + over, B.line ?? 9, pearls), { pts: gap, fill: 0, hole: true, label: "hole" }] });
  }
  const panels = L.panels ?? [], total = panels.reduce((a, p) => a + (p.h ?? 1), 0), inH = H - 2 * tb, seed = L.seed ?? 1, bars = [];
  let y = -H / 2 + tb;
  panels.forEach((P, i) => {
    const y1 = y + inH * (P.h ?? 1) / total, make = KIND[P.form];
    if (!make) throw new Error(`no panel form "${P.form}"`);
    out.push({ clip: clipY(inner, y, y1), pieces: make(P, W - 2 * t, y, y1, L, seed + i * 17, tile) });
    if (i < panels.length - 1) bars.push(y1);
    y = y1;
  });
  out.bars = bars;
  return out;
}
