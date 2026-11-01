// A WINDOW'S LAYOUT (docs/glass.md): lights and quarries as pieces, panel by panel, each cut on its own so that a window costs what a
// panel costs. A lancet: a border of blocks and pearls, then panels one above another between iron bars; each a medallion on a
// diaper, a saint under a canopy, or white grisaille. Nothing here knows of a picture's name: that's in the generator.
import { lancet, circle, foil, stoneRose } from "./forms.js";
import { buildFigure, placed, curve } from "../medieval/figure.js";
import { stream } from "../greek/rig.js";
import { inPoly } from "./panes.js";

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
function border(w, h, t, B, tileH) {
  const block = B.block ?? .16, fills = B.fills ?? [1, 0, 2, 0], X = w / 2 + .01, Y = h / 2 + .01, x = w / 2 - t, y = h / 2 - t, out = [];
  let c = 0;
  const rail = (a, b, p, q) => { const n = Math.max(1, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / block)); for (let i = 0; i < n; i++) { const m = (A, B2, k) => [A[0] + (B2[0] - A[0]) * k / n, A[1] + (B2[1] - A[1]) * k / n]; out.push({ pts: [m(a, b, i), m(a, b, i + 1), m(p, q, i + 1), m(p, q, i)], fill: fills[c % fills.length], role: "border", label: `b${c}` }); c++; } };
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
  const nx = Math.ceil(w / d) + 1, ny = Math.ceil(h / d) + 1;
  for (let j = -ny; j <= ny; j++) for (let i = -nx; i <= nx; i++) {
    const x = (i + (j & 1 ? .5 : 0)) * d, y = cy + j * d / 2;
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
function medallion(P, w, y0, y1, L, seed) {
  const cy = (y0 + y1) / 2, h = y1 - y0, r = Math.min(w, h) * (P.r ?? .46), shape = P.shape ?? "circle", band = r * .09;
  const make = (R) => shape === "quatrefoil" ? foil([0, cy], R * 1.08, 4, 0, .22, 12) : shape === "lozenge" ? [[0, cy - R * 1.12], [R * 1.12, cy], [0, cy + R * 1.12], [-R * 1.12, cy]] : circle([0, cy], R, 40);
  const inner = make(r - band), s = (2 * r * .72) / 100, base = cy - r * .72 + (P.drop ?? 0) * r;
  const hides = make(r * .96), out = [...diaper(w, h, cy, { d: w * .2, fills: L.ground ?? [1, 9], fleuron: L.fleuron }).filter((p) => !p.pts.every((q) => inPoly(q[0], q[1], hides))),      // (no lattice under the medallion: it costs, and shows nothing)
    { pts: make(r), fill: P.ground ?? 0, role: "medal", label: "md" }, ...propsOf(P.props, 0, base, s), ...castOf(P.cast ?? [], 0, base, s, seed),
    { pts: ring(make(r * 1.04), inner), fill: P.band ?? 2, role: "band", label: "band", paint: L.pearl === undefined ? [] : pearlsOn(make(r * .985), band * .3) }];
  return out;
}

// A SAINT panel: a figure standing on a base, a canopy over him, a ground behind
function saint(P, w, y0, y1, L, seed) {
  const h = y1 - y0, base = y0 + h * .06, up = y0 + h * (P.spring ?? .68), s = (up - base) * 1.06 / 100, gw = w * .44;      // (the head stands in the canopy's arch)
  return [{ pts: [[-w, y0 - .01], [w, y0 - .01], [w, y1 + .01], [-w, y1 + .01]], fill: P.ground ?? 1, role: "ground", label: "sg", paint: hatching(w, y0, y1, w * .08) },
    { pts: [[-w, y0 - .01], [w, y0 - .01], [w, base], [-w, base]], fill: P.base ?? 3, role: "base", label: "sb", paint: [{ pts: [[-w, base - .02], [w, base - .02]], w: .006 }] },
    ...canopy(up, gw, y1 + .01, { fill: P.canopy ?? 2, fill2: P.canopy2 ?? 4, arch: P.arch ?? (P.ground ?? 1) }), ...propsOf(P.props, 0, base, s), ...castOf(P.cast ?? [], 0, base, s, seed)];
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
const KIND = { medallion, saint, grisaille };

// THE STONE'S ROSE: each thing its bars enclose is a little window of its own, cut alone. A light has a diaper and a
// medallion towards its head with one of `cast`; a roundel a foil on its colour; the hub whatever `hubCast` is.
export function stonePanels(L, clipAll, R) {
  const pieces = stoneRose(L, R), cast = L.cast ?? [], seed = L.seed ?? 1, d = R * (L.diaper ?? .12), pearls = L.pearl ?? 4;
  const out = [{ clip: clipAll, pieces: [{ pts: circle([0, 0], R * 1.01, 96), fill: L.ground ?? 0, role: "ground", label: "ground" }, ...pieces.map((p) => ({ pts: p.pts, fill: 0, hole: true, label: "h" + p.label }))] }];
  let nl = 0, nr = 0;
  for (const P of pieces) {
    const mx = P.pts.reduce((a, p) => a + p[0], 0) / P.pts.length, my = P.pts.reduce((a, p) => a + p[1], 0) / P.pts.length;
    const low = Math.min(...P.pts.map((p) => p[1])), high = Math.max(...P.pts.map((p) => p[1])), reach = Math.max(...P.pts.map((p) => Math.hypot(p[0] - mx, p[1] - my)));
    if (P.role === "light") {
      const k = nl++, a = Math.atan2(my, mx), far = Math.max(...P.pts.map((p) => Math.hypot(p[0], p[1]))), near = Math.min(...P.pts.map((p) => Math.hypot(p[0], p[1])));
      const at = near + (far - near) * .6, cx = at * Math.cos(a), cy = at * Math.sin(a), half = Math.PI / Math.round(L.lights ?? 12), r = at * Math.sin(half) * .78, s = 2 * r * .72 / 100;
      const hide = circle([cx, cy], r * .96, 20), mk = (q) => circle([cx, cy], q, 28);
      const ground = diaper(reach * 1.1, reach * 1.1, 0, { d, fills: [P.fill, 9], fleuron: L.fleuron }).map((p) => ({ ...p, pts: p.pts.map((q) => [q[0] + mx, q[1] + my]) })).filter((p) => p.role === "ground" || !p.pts.every((q) => inPoly(q[0], q[1], hide)));
      out.push({ clip: P.pts, pieces: [...ground, { pts: mk(r), fill: k % 2 ? 0 : 1, role: "medal", label: "md" }, ...castOf(cast.length ? [cast[k % cast.length]] : [], cx, cy - r * .72, s, seed + k), { pts: ring(mk(r * 1.06), mk(r * .92)), fill: 2, role: "band", label: "band", paint: pearlsOn(mk(r * .99), r * .03) }] });
    } else if (P.role === "hub") {
      const r = reach * .94, s = 2 * r * .72 / 100, mk = (q) => circle([0, 0], q, 40);
      out.push({ clip: P.pts, pieces: [{ pts: circle([0, 0], reach * 1.1, 40), fill: L.hub ?? 2, role: "ground", label: "hg" }, { pts: mk(r * .88), fill: 0, role: "medal", label: "hm" }, ...castOf(L.hubCast ?? [], 0, -r * .72, s, seed + 500), { pts: ring(mk(reach * 1.1), mk(r * .88)), fill: L.hub ?? 2, role: "band", label: "hb", paint: pearlsOn(mk(r * .94), r * .03) }] });
    } else {
      const k = nr++;
      out.push({ clip: P.pts, pieces: [{ pts: circle([mx, my], reach * 1.1, 24), fill: P.fill, role: "roundel", label: "rg", paint: pearlsOn(circle([mx, my], reach * .86, 24), reach * .045) }, { pts: foil([mx, my], reach * .62, k % 2 ? 4 : 6, 0, .28, 8), fill: k % 2 ? 4 : 2, role: "inner", label: "ri" }, { pts: circle([mx, my], reach * .17, 10), fill: pearls === 4 ? 1 : pearls, role: "knot", label: "rk" }] });
    }
  }
  return out;
}

const rectOf = (w, h, y = 0) => [[-w / 2, y - h / 2], [w / 2, y - h / 2], [w / 2, y + h / 2], [-w / 2, y + h / 2]];
// a light: `panels` is [{ form, cast, h (share), ... }] from the foot up, in a rectangle that stacks on itself and goes up to the stone. -> [{ pieces, clip }]
export function panelsOf(L, tile, clipAll) {
  if (L.form !== "light") throw new Error(`no glass form "${L.form}"`);
  const W = L.opening?.w ?? tile[0], H = L.opening?.h ?? tile[1], B = L.border, t = B ? (B.t ?? W * .1) : 0, tb = B?.sides ? 0 : t, inner = rectOf(W - 2 * t, H - 2 * tb), over = B?.sides ? .04 : 0, out = [];
  if (B) {
    const pearls = B.pearl !== undefined ? pearlsOn(rectOf(W - 2 * t * .86, H - 2 * tb * .86 + over), t * .085, undefined, 3) : [], gap = rectOf(W - 2 * t, H - 2 * tb + over);
    out.push({ clip: clipAll, pieces: [...border(W, H, t, B, tile[1]), { pts: ring(rectOf(W - 2 * t * .72, H - 2 * tb * .72 + over), gap), fill: B.line ?? 9, role: "line", label: "bl", sheet: "bl", paint: pearls }, { pts: gap, fill: 0, hole: true, label: "hole" }] });
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
