// A MOSAIC FROM ITS SEED (docs/mosaic.md, docs/story.md): a layer's `plan` becomes its drawing before any stone is laid. What's in here says how floors and walls are ARRANGED and what borders
// and fields there are; who's in them comes from the story canon, the same as stained glass's, drawn flat by the `story` layer (medieval.js). The stones never know. Plans: { kind: "floor" | "wall" | "field" | "strip", subject, ... }.
// `keep`: at this seed a pattern stays the drawing it's always had (what the finishes hold), and any other is a new one.
import { LAYER_KINDS } from "../patterns.js";
import { stream, one, shuffled, scramble } from "../story/seed.js";
import { CANON } from "../story/compose.js";
import { renderPainting } from "../greek/field.js";
import { greekData } from "../greek.js";
import { TECHNIQUES } from "../greek/paint.js";

const TAU = Math.PI * 2;
const INK = 1.12;   // (a figure's lines, in stones: what's drawn thinner is laid this wide all the same, and a picture laid darker than its drawing)
const rectAt = (x, y, w, h) => [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2, y + h / 2]];
const ngon = (x, y, r, n, a = 0) => Array.from({ length: n }, (_, i) => [x + r * Math.cos(a + i * TAU / n), y + r * Math.sin(a + i * TAU / n)]);
const disc = (x, y, r, n = 32) => ngon(x, y, r, n);
const octagon = (x, y, r) => ngon(x, y, r / Math.cos(Math.PI / 8), 8, Math.PI / 8);

// LAYER: polygons in slots. { pts, fill, hole, line, w } and `within` a clip
LAYER_KINDS.polys = {
  draw(g, L, { pal }) {
    const css = (c) => typeof c === "string" ? c : `rgb(${pal[c].join(",")})`, trace = (pts, closed) => { pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); if (closed) g.closePath(); };
    g.save(); if (L.within) { g.beginPath(); trace(L.within, true); g.clip(); }
    g.lineCap = "butt"; g.lineJoin = "miter";
    for (const q of L.items) {
      g.beginPath(); trace(q.pts, !q.open); if (q.hole) trace(q.hole, true);
      if (q.fill !== undefined) { g.fillStyle = css(q.fill); g.fill("evenodd"); }
      if (q.line !== undefined) { g.strokeStyle = css(q.line); g.lineWidth = q.w; g.stroke(); }
    }
    g.restore();
  },
};

// LAYER: a scene on the Greek rig (greek/rig.js, beast.js, scene.js), bodies in action, in `tech`: the same solver and the story canon's `rig` names over Greek's own. Bare ground: the frame's own shows through. { scene, seed, frame, within, tech }
TECHNIQUES.mosaic.roles.sea = "#566b70"; TECHNIQUES.mosaic.roles.seaFar = "#3e4f54";
let rigSource = null, rigMerged = null;
const rigged = () => { const D = greekData(), M = CANON.rig; if (!D) return null; if (rigSource !== D) { rigSource = D; rigMerged = { ...D, cast: { ...D.cast, ...M.cast }, scenes: { ...D.scenes, ...M.scenes }, parts: { ...D.parts, beasts: { ...D.parts.beasts, ...M.beasts } } }; } return rigMerged; };
LAYER_KINDS.rig = {
  draw(g, L, C) {
    const { x0, x1, y0, y1 } = L.frame, w = x1 - x0, h = y1 - y0, cv = renderPainting(rigged(), { name: L.scene, tech: L.tech ?? "mosaic", period: "classical", aspect: [w, h], ground: "rgba(0,0,0,0)", zones: [{ h: 1, scenes: [L.scene], single: 1, fill: L.fill ?? .92 }] }, { px: Math.max(16, Math.round(w * C.ppm)), seed: L.seed });   // (not `sparse`: pressed into a square frame a hunt's bodies would stand in each other)
    const G = cv.getContext("2d", { willReadFrequently: true }), I = G.getImageData(0, 0, cv.width, cv.height), a = I.data; let lo = 0, hi = -1, le = cv.width, ri = 0;   // (where it came out: up off the floor of a tall frame, the earth under its feet and a tree into what's left at its side)
    for (let j = 0, i = 3; j < cv.height; j++) for (let k = 0; k < cv.width; k++, i += 4) if (a[i] > 128) { lo = j; if (hi < 0) hi = j; if (k < le) le = k; if (k > ri) ri = k; }
    if (L.mono) { for (let i = 0; i < a.length; i += 4) if (a[i] - a[i + 2] > 40) { a[i] = 30; a[i + 1] = 28; a[i + 2] = 29; } G.putImageData(I, 0, 0); }   // (Ostia's: black figures with no added red)
    const under = cv.height - 1 - lo, wet = rigged().scenes[L.scene].water, up = wet ? h * .1 : Math.max(0, (under + hi) * .42 - under) / cv.height * h, foot = y1 - h * (lo + 1) / cv.height + up, left = le / cv.width * w, right = w - (ri + 1) / cv.width * w, room = Math.max(left, right), r = stream(scramble(L.seed), "rig");
    g.save(); if (L.within) { g.beginPath(); L.within.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); g.clip(); }
    if (L.paper) { g.fillStyle = L.paper; g.fillRect(x0, y0, w, h); }
    if (wet) {                                                          // (the sea to the frame's foot, a crest and a line of swell along it)
      const n = Math.max(6, Math.round(w / (L.stone * 9))), X0 = L.within ? Math.min(...L.within.map((p) => p[0])) : x0, X1 = L.within ? Math.max(...L.within.map((p) => p[0])) : x1, Y0 = L.within ? Math.min(...L.within.map((p) => p[1])) : y0 - h * .02, crest = (Y, A) => Array.from({ length: n * 6 + 1 }, (_, i) => [X0 + i * (X1 - X0) / (n * 6), Y + A * Math.sin(i * TAU / 6)]);
      g.fillStyle = `rgb(${C.pal[L.water].join(",")})`; g.beginPath(); g.moveTo(X0, Y0); for (const p of crest(foot + L.stone * .6, L.stone * 1.3)) g.lineTo(p[0], p[1]); g.lineTo(X1, Y0); g.closePath(); g.fill();
      g.strokeStyle = `rgb(${C.pal[L.foam].join(",")})`; g.lineWidth = L.stone * 1.25; for (const Y of [foot - h * .035, foot - h * .08]) { g.beginPath(); crest(Y, L.stone * 1.1).forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.stroke(); }
    } else if (L.earth !== undefined) {                                        // (a strip of ground in a line of humps and tufts, no further than the picture's frame)
      const t = Math.max(L.stone * 1.6, h * .022), n = Math.max(6, Math.round(w / (t * 2.4))), top = Array.from({ length: n + 1 }, (_, i) => [x0 + i * w / n, foot - t * .1 + t * (i % 2 ? .25 + r() * .5 : -.1)]);
      g.fillStyle = `rgb(${C.pal[L.earth].join(",")})`; g.beginPath(); g.moveTo(x0, foot - t * 1.1); g.lineTo(x1, foot - t * 1.1); for (const p of top.reverse()) g.lineTo(p[0], p[1]); g.closePath(); g.fill();
    }
    if (L.tree && room > w * .16) { const u = Math.min(room * .9, h * .5), at = left > right ? x0 + left * .5 : x1 - right * .5; LAYER_KINDS.story.draw(g, { ...L.tree, scene: "rig-tree", seed: L.seed, frame: { x0: at - u / 2, x1: at + u / 2, y0: foot, y1: Math.min(y1, foot + h * .72) }, float: 0 }, C); }
    g.translate((x0 + x1) / 2, (y0 + y1) / 2 + up); g.scale(1, -1); g.drawImage(cv, -w / 2, -h / 2, w, h); g.restore();
  },
};

// ---- STRIPS: a band's drawing, [-len/2, len/2] along and [-t/2, t/2] across; each a whole number of its cells ------------------------------
const cells = (len, t, k) => { const n = Math.max(2, Math.round(len / (t * k) / 2) * 2); return [n, len / n]; };   // (even: what alternates comes round again)
const each = (len, n, f) => { const out = []; for (let i = 0; i < n; i++) out.push(...f(-len / 2 + (i + .5) * len / n, i)); return out; };
const ribbon = (path, w) => { const L = [], R = []; path.forEach((p, i) => { const a = path[Math.max(0, i - 1)], b = path[Math.min(path.length - 1, i + 1)], d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, nx = -(b[1] - a[1]) / d * w / 2, ny = (b[0] - a[0]) / d * w / 2; L.push([p[0] + nx, p[1] + ny]); R.unshift([p[0] - nx, p[1] - ny]); }); return [...L, ...R]; };
const STRIPS = {
  guilloche(len, t, C) { // (two strands, one over the other at each crossing, round white eyes)
    const [n, c] = cells(len, t, 1.5), A = t * .3, w = t * .24, out = [], at = (x, s) => [x, s * A * Math.sin(TAU * (x + len / 2) / c)], seg = (x0, s) => Array.from({ length: 11 }, (_, i) => at(x0 + i * c / 20 - c / 4, s));
    const strand = (x, s, fill) => ({ pts: ribbon(seg(x, s), w), fill, line: C.ink, w: t * .035 });
    for (let i = 0; i <= n * 2; i++) { const x = -len / 2 + i * c / 2, o = i % 2 ? 1 : -1; out.push(strand(x, -o, C.b), strand(x, o, C.a)); }
    return out.concat(each(len, n, (x) => [{ pts: disc(x - c / 4, 0, t * .055, 10), fill: C.c }, { pts: disc(x + c / 4, 0, t * .055, 10), fill: C.c }]));
  },
  meander(len, t, C) { // (a key rising from a line, turning in, coming back)
    const [n, c] = cells(len, t, 1.1), h = t * .72, w = t * .15, y0 = -h / 2;
    return each(len, n, (x) => { const o = x - c / 2; return [{ pts: [[o, y0], [o + c * .86, y0], [o + c * .86, y0 + h], [o + c * .12, y0 + h], [o + c * .12, y0 + h * .3], [o + c * .55, y0 + h * .3], [o + c * .55, y0 + h * .62]], open: true, line: C.a, w }, { pts: [[o + c * .86, y0], [o + c + w * .02, y0]], open: true, line: C.a, w }]; });
  },
  tkey(len, t, C) { // (T-keys, up and down in turn, locked into each other)
    const [n, c] = cells(len, t, .8), h = t * .36, w = t * .14;
    return each(len, n, (x, i) => { const s = i % 2 ? 1 : -1; return [{ pts: [[x - c * .32, s * h], [x + c * .32, s * h]], open: true, line: C.a, w }, { pts: [[x, s * h], [x, -s * h * .7]], open: true, line: i % 2 ? C.b : C.a, w }]; });
  },
  wave(len, t, C) { // (the running dog: a crest rolling over, one way)
    const [n, c] = cells(len, t, 1.25), h = t * .4, top = [];
    for (let k = 0; k <= n * 16; k++) { const f = k / 16, p = f * TAU; top.push([-len / 2 + (f + .3 * Math.sin(p)) * c, -h * .1 + h * .75 * Math.cos(p)]); }
    return [{ pts: [[-len / 2, -h * 1.1], ...top, [len / 2, -h * 1.1]], fill: C.a }];
  },
  dentil(len, t, C) { const [n, c] = cells(len, t, .9); return each(len, n, (x) => [{ pts: rectAt(x, -t * .06, c * .56, t * .66), fill: C.a }]); },
  saw(len, t, C) { const [n, c] = cells(len, t, 1); return each(len, n, (x, i) => [{ pts: [[x - c / 2, -t * .38], [x + c / 2, -t * .38], [x, t * .38]], fill: C.a }, { pts: [[x + c / 2, -t * .38], [x + c, t * .38], [x, t * .38]], fill: i % 2 ? C.b : C.c }]); },
  chequer(len, t, C) { const [n, c] = cells(len, t, .34); return each(len, n, (x, i) => [{ pts: rectAt(x, t * .17, c, t * .34), fill: i % 2 ? C.a : C.c }, { pts: rectAt(x, -t * .17, c, t * .34), fill: i % 2 ? C.b : C.a }]); },
  lozenges(len, t, C) { const [n, c] = cells(len, t, 1.25); return each(len, n, (x, i) => [{ pts: [[x - c / 2, 0], [x, t * .42], [x + c / 2, 0], [x, -t * .42]], fill: i % 2 ? C.a : C.b }, { pts: disc(x, 0, t * .11, 8), fill: C.c }]); },
  beads(len, t, C) { const [n, c] = cells(len, t, 1.1); return each(len, n, (x, i) => [{ pts: disc(x - c / 4, 0, t * .25, 12), fill: C.a }, { pts: rectAt(x + c / 4, 0, c * .16, t * .6), fill: i % 2 ? C.b : C.a }]); },
  ivy(len, t, C) { // (a stem winding, a heart-shaped leaf to each turn)
    const [n, c] = cells(len, t, 1.5), A = t * .2, path = []; for (let k = 0; k <= n * 12; k++) { const x = -len / 2 + k * c / 12; path.push([x, A * Math.sin(TAU * (x + len / 2) / c)]); }
    const leaf = (x, y, s) => [[x, y], [x - t * .13, y + s * t * .12], [x - t * .05, y + s * t * .2], [x, y + s * t * .34], [x + t * .05, y + s * t * .2], [x + t * .13, y + s * t * .12]];
    return [{ pts: path, open: true, line: C.a, w: t * .08 }, ...each(len, n, (x) => [{ pts: leaf(x - c / 4 + c * .16, -A * .3, -1), fill: C.b }, { pts: leaf(x + c / 4 - c * .16, A * .3, 1), fill: C.b }])];
  },
  plait(len, t, C) { // (a plait of three: bands crossing at the diagonal, a little weave)
    const [n, c] = cells(len, t, .9), w = t * .24, out = [];
    for (let i = -1; i <= n; i++) { const x = -len / 2 + (i + .5) * c, h = t * .42, a = i % 2 ? 1 : -1; out.push({ pts: ribbon([[x - c / 2, -a * h], [x + c / 2, a * h]], w), fill: C.a, line: C.ink, w: t * .035 }, { pts: ribbon([[x - c / 2, a * h], [x + c / 2, -a * h]], w), fill: C.b, line: C.ink, w: t * .035 }); }
    return out;
  },
};
export const STRIP_NAMES = Object.keys(STRIPS);

// ---- FIELDS: what fills an area, whole cells, in step with its size: a tile of them tiles. `m` cells more round the edge, for what's clipped ---------------
const lat = (W, H, ax, ay, m, f) => { const nx = Math.max(2, Math.round(W / ax / 2) * 2), ny = Math.max(2, Math.round(H / ay / 2) * 2), a = W / nx, b = H / ny, out = []; for (let j = -m; j < ny + m; j++) for (let i = -m; i < nx + m; i++) out.push(...f(-W / 2 + (i + .5) * a, -H / 2 + (j + .5) * b, a, b, i, j)); return out; };
const squish = (pts, x, y, a, b, A, B) => pts.map(([u, v]) => [x + (u - x) * a / A, y + (v - y) * b / B]);
const FIELDS = {
  hexagons(W, H, s, C, m, v) { const ax = s * Math.sqrt(3), ay = s * 1.5; return lat(W, H, ax, ay, m, (x0, y, a, b, i, j) => { const x = x0 + (j % 2 ? a / 2 : 0), o = [{ pts: squish(ngon(x, y, s, 6, Math.PI / 6), x, y, a, b, ax, ay), line: C.a, w: s * .15 }]; if (v === 1) o.push({ pts: squish(ngon(x, y, s * .42, 6, Math.PI / 6), x, y, a, b, ax, ay), fill: C.b }); if (v === 2) for (let k = 0; k < 6; k++) { const t = k * TAU / 6; o.push({ pts: [[x, y], [x + s * .4 * Math.cos(t - .32), y + s * .4 * Math.sin(t - .32)], [x + s * .62 * Math.cos(t), y + s * .62 * Math.sin(t)], [x + s * .4 * Math.cos(t + .32), y + s * .4 * Math.sin(t + .32)]], fill: k % 2 ? C.b : C.c }); } if (v === 3) o.push({ pts: disc(x, y, s * .22, 12), fill: C.b }); return o; }); },
  scales(W, H, s, C, m, v) { return lat(W, H, s * 2, s, m + 1, (x0, y0, a, b, i, j) => { const x = x0 + (j % 2 ? a / 2 : 0), rx = a / 2, ry = b, y = y0, q = []; for (let k = 0; k <= 8; k++) { const t = Math.PI + k * Math.PI / 8; q.push([x + rx * Math.cos(t), y + ry * Math.sin(t)]); } for (let k = 1; k < 8; k++) { const t = k / 8 * Math.PI / 2; q.push([x + rx - rx * Math.sin(t), y + ry - ry * Math.cos(t)]); } q.push([x, y + ry]); for (let k = 1; k < 8; k++) { const t = k / 8 * Math.PI / 2; q.push([x - rx + rx * Math.cos(t), y + ry * Math.sin(t) * 0 + ry - ry * Math.sin(t)]); } return [{ pts: q, fill: v === 1 ? (j % 4 < 2 ? C.a : C.b) : v === 2 ? ((i + (j >> 1)) % 2 ? C.a : C.c) : C.bg, line: C.ink, w: s * .1 }]; }); },
  chequer(W, H, s, C, m, v) { return lat(W, H, s, s, m, (x, y, a, b, i, j) => (i + j) % 2 ? [{ pts: rectAt(x, y, a, b), fill: v === 1 && j % 2 ? C.b : C.a }, ...(v === 3 ? [{ pts: rectAt(x, y, a * .44, b * .44), fill: C.c }] : [])] : v === 2 ? [{ pts: [[x - a * .32, y], [x, y + b * .32], [x + a * .32, y], [x, y - b * .32]], fill: C.c }] : []); },   // (the dark squares only, the pale ones the ground showing; a lozenge in each pale one, or a square in each dark)
  octagons(W, H, s, C, m, v) { return lat(W, H, s, s, m, (x, y, a, b, i, j) => { const o = [{ pts: squish(octagon(x, y, s * .5), x, y, a, b, s, s), line: C.a, w: s * .07 }, { pts: [[x + a / 2 - a * .2, y + b / 2], [x + a / 2, y + b / 2 - b * .2], [x + a / 2 + a * .2, y + b / 2], [x + a / 2, y + b / 2 + b * .2]], fill: C.b }]; if (v === 1) o.push({ pts: disc(x, y, s * .2, 12), fill: C.c }); if (v === 2) { const st = []; for (let k = 0; k < 16; k++) { const t = k * TAU / 16 + Math.PI / 16, q = (k % 2 ? .16 : .38) * s; st.push([x + q * Math.cos(t), y + q * Math.sin(t)]); } o.push({ pts: st, fill: C.c }); } return o; }); },
  stars(W, H, s, C, m) { return lat(W, H, s, s, m, (x, y, a, b, i, j) => { const q = []; for (let k = 0; k < 16; k++) { const t = k * TAU / 16, u = (k % 2 ? .3 : .52) * s; q.push([x + u * Math.cos(t) * a / s, y + u * Math.sin(t) * b / s]); } return [{ pts: q, fill: (i + j) % 2 ? C.a : C.b }, { pts: disc(x, y, s * .12, 10), fill: C.bg }]; }); },
  blocks(W, H, s, C, m) { const ax = s * Math.sqrt(3), ay = s * 1.5; return lat(W, H, ax, ay, m, (x0, y, a, b, i, j) => { const x = x0 + (j % 2 ? a / 2 : 0), u = a / 2, h = b * 2 / 3; return [{ pts: [[x, y], [x + u, y + h / 2], [x, y + h], [x - u, y + h / 2]], fill: C.c }, { pts: [[x, y], [x - u, y + h / 2], [x - u, y - h / 2], [x, y - h]], fill: C.a }, { pts: [[x, y], [x + u, y + h / 2], [x + u, y - h / 2], [x, y - h]], fill: C.b }]; }); },
  peltae(W, H, s, C, m) { return lat(W, H, s, s, m, (x, y, a, b, i, j) => { const ang = (i + j) % 2 ? Math.PI / 2 : 0, shape = [[-.46, .3], [-.3, .12], [-.1, .28], [0, .1], [.1, .28], [.3, .12], [.46, .3], [.42, -.02], [.26, -.28], [0, -.38], [-.26, -.28], [-.42, -.02]], cs = Math.cos(ang), sn = Math.sin(ang); return [{ pts: shape.map(([u, v]) => [x + (u * cs - v * sn) * a, y + (u * sn + v * cs) * b]), fill: (i + j) % 2 ? C.a : C.b }]; }); },
  basket(W, H, s, C, m) { return lat(W, H, s, s, m, (x, y, a, b, i, j) => { const out = []; for (let k = -1; k <= 1; k++) out.push({ pts: (i + j) % 2 ? rectAt(x + k * a * .3, y, a * .2, b * .9) : rectAt(x, y + k * b * .3, a * .9, b * .2), fill: k ? C.a : C.b }); return out; }); },
  chevrons(W, H, s, C, m) { return lat(W, H, s, s * .5, m, (x, y, a, b, i, j) => j % 2 ? [] : [{ pts: [[x - a / 2, y - b / 2], [x, y + b / 2], [x + a / 2, y - b / 2], [x + a / 2, y + b / 2], [x, y + b * 1.5], [x - a / 2, y + b / 2]], fill: j % 4 ? C.a : C.b }]); },
  petals(W, H, s, C, m) { return lat(W, H, s, s, m, (x, y, a, b, i, j) => { const out = [], lens = (t) => { const P = [], n = 7; for (let k = 0; k <= n; k++) { const u = k / n; P.push([x + (u * a * .5) * Math.cos(t) - .22 * a * Math.sin(u * Math.PI) * Math.sin(t), y + (u * b * .5) * Math.sin(t) + .22 * b * Math.sin(u * Math.PI) * Math.cos(t)]); } for (let k = n - 1; k > 0; k--) { const u = k / n; P.push([x + (u * a * .5) * Math.cos(t) + .22 * a * Math.sin(u * Math.PI) * Math.sin(t), y + (u * b * .5) * Math.sin(t) - .22 * b * Math.sin(u * Math.PI) * Math.cos(t)]); } return P; }; for (const t of [0, Math.PI / 2, Math.PI, Math.PI * 1.5]) out.push({ pts: lens(t), fill: (i + j) % 2 ? C.a : C.b }); out.push({ pts: disc(x, y, s * .08, 8), fill: C.c }); return out; }); },
  lozenges(W, H, s, C, m) { return lat(W, H, s, s * 1.3, m, (x, y, a, b, i, j) => [{ pts: [[x - a / 2, y], [x, y + b / 2], [x + a / 2, y], [x, y - b / 2]], fill: j % 2 ? C.a : C.b }, { pts: [[x - a * .2, y], [x, y + b * .2], [x + a * .2, y], [x, y - b * .2]], fill: C.c }]); },
  triangles(W, H, s, C, m) { return lat(W, H, s, s * .8, m, (x0, y, a, b, i, j) => { const x = x0 + (j % 2 ? a / 2 : 0); return [{ pts: [[x - a / 2, y - b / 2], [x + a / 2, y - b / 2], [x, y + b / 2]], fill: j % 2 ? C.a : C.b }]; }); },
  rosettes(W, H, s, C, m) { return lat(W, H, s, s, m, (x, y, a, b, i, j) => [{ pts: disc(x, y, s * .46, 28), line: C.a, w: s * .05 }, ...[0, 1, 2, 3, 4, 5, 6, 7].map((k) => { const t = k * TAU / 8; return { pts: [[x, y], [x + s * .2 * Math.cos(t - .4), y + s * .2 * Math.sin(t - .4)], [x + s * .38 * Math.cos(t), y + s * .38 * Math.sin(t)], [x + s * .2 * Math.cos(t + .4), y + s * .2 * Math.sin(t + .4)]], fill: k % 2 ? C.b : C.c }; }), { pts: disc(x + a / 2, y + b / 2, s * .06, 8), fill: C.a }]); },
};
export const FIELD_NAMES = Object.keys(FIELDS);

// ---- what stands on what. A frame's stack: outside in, each a line or a strip; four sides meeting under a corner block ----------------------
function stripRound(x, y, w, h, t, kind, C, out) {
  const cx = x + w / 2, cy = y + h / 2, side = (len, X, Y, rot) => { const cs = Math.cos(rot), sn = Math.sin(rot), up = Math.abs(sn) > .5, box = rectAt(X, Y, up ? t : len, up ? len : t); if (C.bg !== undefined) out.push({ pts: box, fill: C.bg }); out.push({ items: STRIPS[kind](len, t, C).map((q) => ({ ...q, pts: q.pts.map(([u, v]) => [X + u * cs - v * sn, Y + u * sn + v * cs]) })), within: box }); };
  side(w - 2 * t, cx, y + t / 2, 0); side(w - 2 * t, cx, y + h - t / 2, Math.PI); side(h - 2 * t, x + t / 2, cy, -Math.PI / 2); side(h - 2 * t, x + w - t / 2, cy, Math.PI / 2);
  for (const [a, b] of [[x + t / 2, y + t / 2], [x + w - t / 2, y + t / 2], [x + t / 2, y + h - t / 2], [x + w - t / 2, y + h - t / 2]]) out.push({ pts: rectAt(a, b, t, t), fill: C.a }, { pts: disc(a, b, t * .22, 10), fill: C.c });
}
const lineRound = (x, y, w, h, t, fill, out) => out.push({ pts: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], hole: [[x + t, y + t], [x + w - t, y + t], [x + w - t, y + h - t], [x + t, y + h - t]], fill });
const ringOf = (cx, cy, r, t, fill, out) => out.push({ pts: disc(cx, cy, r, 48), hole: disc(cx, cy, r - t, 48), fill });
// (a line thinner than a stone would be laid a stone wide, and darken what's there: as wide as the stones lay it, or none where it only edges a fill)
const solid = (items, stone) => items.map((q) => { if (q.line === undefined || q.w >= stone * 1.2) return q; if (q.fill !== undefined) { const { line, w, ...rest } = q; return rest; } return { ...q, w: stone * 1.2 }; });
// (edges of cells kept off the tile's own edge, where a seam would be hidden)
const offEdge = (items, W, H) => { const dx = W * .0371, dy = H * .0291; return items.map((q) => ({ ...q, pts: q.pts.map(([a, b]) => [a + dx, b + dy]) })); };
function flatten(out, stone) { const layers = []; let cur = null; for (const q of out) { if (q.items) { cur = null; layers.push({ kind: "polys", items: solid(q.items, stone), within: q.within }); } else if (q.kind) { cur = null; layers.push(q); } else { if (!cur) { cur = { kind: "polys", items: [] }; layers.push(cur); } cur.items.push(...solid([q], stone)); } } return layers; }

// ---- the canon's names to a palette's slots ------------------------------------------------------------------------------------------------
const OPUS = { cobalt: 6, ruby: 9, gold: 8, emerald: 7, white: 0, flesh: 4, purple: 9, sky: 6, amber: 13, navy: 12, brown: 5, rose: 3, olive: 14, grey: 2 };
const GOLD = { cobalt: 4, ruby: 3, gold: 1, emerald: 8, white: 5, flesh: 7, purple: 10, sky: 11, amber: 2, navy: 10, brown: 12, rose: 3, olive: 8, grey: 13 };
const SILHOUETTE = Object.fromEntries(Object.keys(OPUS).map((k) => [k, 1]));
const ROMAN = [
  { ground: 0, name: "white", ink: 1, a: 3, b: 6, c: 8, d: 7 }, { ground: 2, name: "grey", ink: 1, a: 9, b: 5, c: 8, d: 0 }, { ground: 0, name: "white", ink: 5, a: 7, b: 9, c: 8, d: 6 },
  { ground: 0, name: "white", ink: 1, a: 6, b: 3, c: 8, d: 5 }, { ground: 2, name: "grey", ink: 5, a: 3, b: 1, c: 0, d: 7 }, { ground: 0, name: "white", ink: 1, a: 1, b: 9, c: 2, d: 8 }, { ground: 15, name: "white", ink: 1, a: 5, b: 3, c: 8, d: 12 },
];
const ROMAN_STRIPS = ["guilloche", "guilloche", "meander", "tkey", "wave", "dentil", "saw", "chequer", "lozenges", "beads", "ivy", "plait"], ROMAN_FIELDS = ["hexagons", "scales", "chequer", "octagons", "stars", "blocks", "peltae", "basket", "chevrons", "petals", "lozenges", "triangles", "rosettes"];
const ANIMALS = () => CANON.cycles.animals;
const SUBJECTS = { hunt: ["hunt"], arena: ["arena"], triumph: ["triumph"], neptune: ["neptune-triumph", "neptune-sea"], dionysus: ["dionysus-triumph", "dionysus-panther", "vintage"], gladiators: ["gladiators", "retiarius", "venatio"], orpheus: ["orpheus", "orpheus-flock"], sea: ["sea-a", "sea-b", "neptune-sea"], xenia: ["xenia"] };
const sceneOf = (subject, r) => { const q = SUBJECTS[subject] ?? [subject]; const list = q.flatMap((n) => CANON.cycles[n] ?? [n]); return one(list, r); };
const anyRoman = (r) => one(["hunt", "hunt", "arena", "triumph", "orpheus", "sea", "xenia"], r);

// A ROMAN FLOOR. One tile, a whole floor, framed; the seed its scheme, its frame, its layout and all that's in it
function planFloor(L, [W, H]) {
  const P = L.plan, seed = L.seed ?? 1, r = stream(scramble(seed), "floor", P.subject ?? "", P.layout ?? ""), bw = !!P.bw, stone = L.stone ?? .012, S = bw ? { ground: 0, name: "white", ink: 1, a: 1, b: 1, c: 0, d: 1 } : one(ROMAN, r), dye = bw ? SILHOUETTE : OPUS, ink = bw ? 0 : S.ink, out = [], line = Math.max(stone * 1.6, .016), C = { a: S.a, b: S.b, c: bw ? 0 : S.c, ink: bw ? 1 : S.ink, bg: S.ground };
  const story = (scene, n, x0, y0, x1, y1, within, ground = S.name) => CANON.rig.of[scene] && rigged() ? { kind: "rig", scene: one(((x1 - x0) / (y1 - y0) < 1.5 && CANON.rig.near[scene]) || CANON.rig.of[scene], r), seed: seed * 7 + n * 31, frame: { x0, x1, y0, y1 }, within, stone, tech: bw ? "black-figure" : "mosaic", mono: bw, earth: bw ? 1 : ground === "grey" ? 5 : 7, water: bw ? 1 : 6, foam: 0, tree: { dye, ink, ground, line: stone * INK, stone } } : ({ kind: "story", scene, seed: seed * 7 + n * 31, frame: { x0, x1, y0, y1 }, dye, ink, ground, line: stone * INK, stone, within });
  const person = (who, n, x0, y0, x1, y1, within) => ({ kind: "story", person: who, wear: { bust: true, holdL: null }, seed: seed * 7 + n * 31, frame: { x0, x1, y0, y1 }, dye, ink, ground: S.name, line: stone * INK, stone, within });
  // the frame: from the outside in
  const pad = .018; let x = -W / 2 + pad, y = -H / 2 + pad, w = W - 2 * pad, h = H - 2 * pad; const rings = bw ? 1 : 1 + Math.floor(r() * 2.4), unit = Math.min(W, H);
  lineRound(x, y, w, h, line, S.ink, out); x += line; y += line; w -= 2 * line; h -= 2 * line;
  const stripsHere = bw ? ["meander", "wave", "tkey", "lozenges", "dentil", "saw", "chequer"] : ROMAN_STRIPS;
  for (let k = 0; k < rings; k++) { const t = unit * (P.band ?? (.055 + r() * .03)), kind = one(stripsHere, r); stripRound(x, y, w, h, t, kind, k % 2 ? { ...C, a: C.b, b: C.a } : C, out); x += t; y += t; w -= 2 * t; h -= 2 * t; lineRound(x, y, w, h, line, S.ink, out); x += line; y += line; w -= 2 * line; h -= 2 * line; }
  const cx = x + w / 2, cy = y + h / 2, wide = w / h > 1.25, subject = P.subject === "any" || !P.subject ? (bw ? one(["triumph", "sea", "hunt", "arena"], r) : anyRoman(r)) : P.subject, fieldC = bw ? { a: 1, b: 1, c: 0, ink: 1, bg: 0 } : { ...C, a: C.ink === 5 ? 5 : one([S.a, S.b, 1], r), b: S.b, c: S.c };
  const layout = P.layout ?? (bw ? "open" : wide ? one(["emblem", "emblem", "panels", "open"], r) : subject === "orpheus" ? "wheel" : subject === "xenia" ? one(["quad", "grid", "lozenge"], r) : subject === "sea" ? "open" : one(["hunt", "arena"].includes(subject) ? ["registers", "registers", "seasons", "grid", "octagons", "field"] : ["emblem", "registers", "seasons", "seasons", "grid", "octagons", "field", "lozenge"], r));
  const fieldIn = (X, Y, W2, H2, s, kind, within, v = Math.floor(r() * 4)) => { const q = FIELDS[kind ?? one(ROMAN_FIELDS, r)](W2, H2, s, fieldC, 2, v).map((t) => ({ ...t, pts: t.pts.map(([a, b]) => [a + X, b + Y]) })); out.push({ items: q, within: within ?? rectAt(X, Y, W2, H2) }); };
  const seas = shuffled(["spring", "summer", "autumn", "winter"], r), beasts = shuffled(subject === "orpheus" ? ANIMALS().filter((n) => n !== "beast-dolphin") : ANIMALS(), r), goods = shuffled(CANON.cycles.xenia, r);
  const subs = (i) => r() < .55 ? beasts[i % beasts.length] : goods[i % goods.length];
  const round = (X, Y, R, scene, n, band = line) => { const within = disc(X, Y, R - band * .6, 48), k = R * .9; ringOf(X, Y, R, band, S.ink, out); out.push(story(scene, n, X - k * 1.06, Y - R * .8, X + k * 1.06, Y + R * .88, within)); };
  if (layout === "emblem") { const b = Math.min(w, h) * .05; lineRound(x + b, y + b, w - 2 * b, h - 2 * b, line, S.ink, out); out.push(story(sceneOf(subject, r), 0, x + b * 1.6, y + b * 1.4, x + w - b * 1.6, y + h - b * 1.6, rectAt(cx, cy, w - 2 * b - 2 * line, h - 2 * b - 2 * line))); }
  else if (layout === "panels") { const n = 2, u = w / n; out.push(...[]); for (let i = 0; i < n; i++) { lineRound(x + i * u + u * .03, y + h * .04, u * .94, h * .92, line, S.ink, out); out.push(story(i ? sceneOf(subject, r) : sceneOf(subject, r), i, x + i * u + u * .07, y + h * .08, x + (i + 1) * u - u * .07, y + h * .9, rectAt(x + (i + .5) * u, y + h * .5, u * .94 - 2 * line, h * .92 - 2 * line))); } }
  else if (layout === "open") { out.push(story(sceneOf(subject, r), 0, x + w * .03, y + h * .03, x + w * .97, y + h * .95, rectAt(cx, cy, w, h))); }
  else if (layout === "seasons") { // (a round in the middle, the seasons' heads in the corners, what's between: stones and swags)
    const R = Math.min(w, h) * .39, corner = Math.min(w, h) * .17, kind = one(ROMAN_FIELDS, r); fieldIn(cx, cy, w, h, Math.min(w, h) * .08, kind, rectAt(cx, cy, w, h));
    out.push({ pts: disc(cx, cy, R, 48), fill: S.ground }); round(cx, cy, R, sceneOf(subject, r), 0, line * 1.3); ringOf(cx, cy, R + line * 2.5, line, S.ink, out);
    seas.forEach((q, i) => { const X = cx + (i % 2 ? 1 : -1) * (w / 2 - corner * 1.05), Y = cy + (i < 2 ? 1 : -1) * (h / 2 - corner * 1.05), within = disc(X, Y, corner * .93, 32); out.push({ pts: disc(X, Y, corner, 32), fill: S.ground }); ringOf(X, Y, corner, line, S.ink, out); out.push(story(q, 10 + i, X - corner * .9, Y - corner * 1.02, X + corner * .9, Y + corner * .8, within)); });
  } else if (layout === "grid") { // (three by three: a story in the middle, beasts and good things round it)
    const u = w / 3, v = h / 3, list = [0, 1, 2, 3, 5, 6, 7, 8]; out.push({ pts: rectAt(cx, cy, w, h), fill: S.ground }); for (let i = 1; i < 3; i++) { out.push({ pts: rectAt(x + u * i, cy, line * 1.5, h), fill: S.ink }, { pts: rectAt(cx, y + v * i, w, line * 1.5), fill: S.ink }); }
    out.push(story(sceneOf(subject, r), 0, x + u + u * .08, y + v + v * .08, x + 2 * u - u * .08, y + 2 * v - v * .1));
    list.forEach((k, i) => { const X = x + (k % 3) * u, Y = y + Math.floor(k / 3) * v; out.push(story(subject === "xenia" ? goods[i % goods.length] : subs(i), i + 1, X + u * .1, Y + v * .1, X + u * .9, Y + v * .88)); });
  } else if (layout === "octagons") { // (five octagons, a lozenge between each)
    const u = Math.min(w, h) / 3, spots = [[0, 0], [-1, -1], [1, -1], [-1, 1], [1, 1]], o = u * .5, ku = (w - u) / 2 / u, kv = (h - u) / 2 / u; out.push({ pts: rectAt(cx, cy, w, h), fill: S.ground });
    for (const [i, j] of [[0, 1], [0, -1], [1, 0], [-1, 0]]) { const X = cx + i * ku * u, Y = cy + j * kv * u; out.push({ pts: [[X - o * .9, Y], [X, Y + o * .9], [X + o * .9, Y], [X, Y - o * .9]], fill: S.a }, { pts: disc(X, Y, o * .3, 12), fill: S.c }); }
    spots.forEach(([i, j], n) => { const X = cx + i * ku * u, Y = cy + j * kv * u, q = o * (n ? .98 : 1.35), pts = octagon(X, Y, q); out.push({ pts, fill: S.ground, line: S.ink, w: line }); out.push(story(n ? subs(n) : sceneOf(subject, r), n, X - q * .8, Y - q * .72, X + q * .8, Y + q * .76, pts)); });
  } else if (layout === "lozenge") { // (a great lozenge inside its rectangle, a field in what's left, a round at the heart)
    const kind = one(ROMAN_FIELDS, r); fieldIn(cx, cy, w, h, Math.min(w, h) * .085, kind); const loz = [[x, cy], [cx, y + h], [x + w, cy], [cx, y]]; out.push({ pts: loz, fill: S.ground, line: S.ink, w: line * 1.4 }); const R = Math.min(w, h) * .3; round(cx, cy, R, sceneOf(subject, r), 0);
  } else if (layout === "field") { // (a field all over, one small picture in it)
    const kind = one(ROMAN_FIELDS, r); fieldIn(cx, cy, w, h, Math.min(w, h) * .09, kind); const b = Math.min(w, h) * .5; out.push({ pts: rectAt(cx, cy, b * 1.1, b * 1.1), fill: S.ground, line: S.ink, w: line * 1.4 }); out.push(story(sceneOf(subject, r), 0, cx - b * .5, cy - b * .5, cx + b * .5, cy + b * .48));
  } else if (layout === "wheel") { // (Orpheus at the hub, his beasts in the compartments of a wheel, what's left in the corners)
    const R = Math.min(w, h) * .49, hub = R * .42, n = 8, Rm = (hub + R) / 2, kind = one(ROMAN_FIELDS, r); fieldIn(cx, cy, w, h, Math.min(w, h) * .08, kind);
    out.push({ pts: disc(cx, cy, R, 64), fill: S.ground });
    for (let k = 0; k < n; k++) { const t = (k + .5) * TAU / n, c0 = Math.cos(t), s0 = Math.sin(t); out.push({ pts: [[cx + hub * Math.cos(t + TAU / n / 2), cy + hub * Math.sin(t + TAU / n / 2)], [cx + R * Math.cos(t + TAU / n / 2), cy + R * Math.sin(t + TAU / n / 2)]], open: true, line: S.ink, w: line }); const q = (R - hub) * .46; out.push(story(beasts[k % beasts.length], k + 2, cx + Rm * c0 - q * 1.05, cy + Rm * s0 - q * .8, cx + Rm * c0 + q * 1.05, cy + Rm * s0 + q * .85)); }
    ringOf(cx, cy, R + line, line * 1.4, S.ink, out); out.push({ pts: disc(cx, cy, hub, 40), fill: S.ground }); round(cx, cy, hub, subject === "orpheus" ? "orpheus-hub" : sceneOf(subject, r), 0, line * 1.3);
  } else if (layout === "quad") { // (two by two, each its own picture, a band between)
    const list = subject === "xenia" ? goods : shuffled(CANON.cycles[subject] ?? goods, r); for (let k = 0; k < 4; k++) { const X = x + (k % 2) * w / 2, Y = y + (k >> 1) * h / 2, u = w / 2, v = h / 2; lineRound(X + u * .03, Y + v * .03, u * .94, v * .94, line, S.ink, out); out.push(story(list[k % list.length], k, X + u * .09, Y + v * .08, X + u * .91, Y + v * .9)); }
  } else if (layout === "registers") { // (two friezes, one over another, a band between: a long story on a square floor)
    const v = h / 2, list = shuffled(CANON.cycles[subject] ?? [sceneOf(subject, r), sceneOf(subject, r)], r); out.push({ pts: rectAt(cx, cy, w, line * 1.5), fill: S.ink }); for (let k = 0; k < 2; k++) out.push(story(list[k % list.length], k, x + w * .03, y + k * v + v * .05, x + w * .97, y + (k + 1) * v - v * .04, rectAt(cx, y + (k + .5) * v, w, v - line * 1.5)));
  }
  else throw new Error(`no floor layout "${layout}"`);
  return { ground: S.ground, ...P.set, layers: flatten(out, stone) };
}

// A BYZANTINE WALL. Gold or a night of lapis and stars, a band at the head and foot, one of the church's programmes
const COMPANIES = [["father", "archbishop", "gregory", "ambrose", "augustine", "nicholas"], ["father", "archbishop", "gregory", "ambrose", "augustine", "nicholas"], ["moses", "david", "prophet", "john-baptist", "abraham", "noah"], ["peter", "paul", "andrew", "john", "james", "matthew"], ["stephen", "lawrence", "stephen", "lawrence"], ["catherine", "barbara", "agnes", "cecilia", "lucy", "margaret"], ["george", "michael", "martin-soldier", "sebastian"]];   // (who else stood on a church's walls, in the fathers' places)
const WALL_BANDS = ["plait", "lozenges", "guilloche", "beads", "saw"];   // (no chequer: two rows of it in a band are too fine for these stones)
function planWall(L, [W, H]) {
  const P = L.plan, seed = L.seed ?? 1, r = stream(scramble(seed), "wall", P.subject ?? ""), stone = L.stone ?? .014, blue = P.ground === "blue" || (P.ground === undefined && r() < .24), ground = blue ? 4 : 0, name = blue ? "cobalt" : "gold", ink = 6, out = [], t = Math.max(Math.min(W, H) * (.06 + r() * .03), stone * 10.5), rule = Math.max(t * .08, stone * 1.15), line = Math.max(stone * 1.3, .012);   // (a band ten stones deep at least: what's finer in it goes to its dark, and laid darker than drawn)
  const C = { a: one([3, 3, 4, 8, 5], r), b: one([1, 5, 3], r), c: one([5, 1, 0], r), ink: 6, bg: one([blue ? 0 : 6, 6, 4], r) };
  const story = (scene, n, x0, y0, x1, y1, within) => ({ kind: "story", scene, seed: seed * 11 + n * 31, frame: { x0, x1, y0, y1 }, dye: GOLD, ink, ground: name, line: stone * INK, stone, within, float: .12 });
  const person = (who, n, x0, y0, x1, y1, within, wear, gr = name) => ({ kind: "story", person: who, wear, seed: seed * 11 + n * 31, frame: { x0, x1, y0, y1 }, dye: GOLD, ink, ground: gr, line: stone * INK, stone, within });
  if (blue) out.push({ items: Array.from({ length: Math.round(W * H * 22) }, () => { const a = -W / 2 + r() * W, b = -H / 2 + r() * H, s = stone * (1 + r()); return { pts: [[a - s, b], [a, b + s], [a + s, b], [a, b - s]], fill: 1 }; }) });
  const bands = P.bands ?? r() < .75; let y0 = -H / 2, y1 = -H / 2 + H * (P.reach ?? 1);   // (`reach`: as far up the tile as the wall it's for lets a figure go. Above that, ground: on Hagia Sophia's half dome the rule stops there)
  if (bands) { const kind = one(WALL_BANDS, r); for (const Y of [-H / 2 + t / 2, H / 2 - t / 2]) { const items = STRIPS[kind](W, t * .78, C).map((q) => ({ ...q, pts: q.pts.map(([a, b]) => [a, b + Y]) })); out.push({ pts: rectAt(0, Y, W * 1.02, t), fill: C.bg }, { pts: rectAt(0, Y + t / 2 - rule / 2 - t * .002, W * 1.02, rule), fill: 5 }, { pts: rectAt(0, Y - t / 2 + rule / 2 + t * .002, W * 1.02, rule), fill: 5 }); out.push({ items, within: rectAt(0, Y, W * 1.02, t * .8) }); } y0 += t * 1.15; y1 -= t * 1.2; }
  const meadow = !blue && P.foot === undefined && r() < .55, sub = P.subject && P.subject !== "any" ? P.subject : one(W / H < 1.2 ? ["bust", "bust", "virgin", "virgin", "shepherd", "cross", "arcade"] : ["bust", "virgin", "deesis", "court", "court", "empress", "empress", "apostles", "fathers", "shepherd", "lambs", "cross", "roundels", "arcade", "nativity"], r), inW = W * .47;
  if (meadow && ["court", "empress", "apostles", "fathers", "shepherd", "arcade"].includes(sub)) { const hg = (y1 - y0) * .07; out.push({ pts: rectAt(0, y0 + hg / 2, W * 1.02, hg), fill: 8 }, { pts: rectAt(0, y0 + hg, W * 1.02, line), fill: 3 }); y0 += hg * .55; }
  if (P.sill) out.push({ pts: rectAt(0, P.sill[0], W * 1.02, P.sill[1]), fill: 8 }, { pts: rectAt(0, P.sill[0] + P.sill[1] / 2 + line / 2, W * 1.02, line), fill: 3 });   // (a tile that wraps: its ground stays off the tile's edge)
  const whole = (scene) => out.push(story(scene, 0, -inW, y0, inW, y1 - (y1 - y0) * .02));
  if (sub === "bust") whole("pantocrator-wall");
  else if (sub === "virgin") whole("virgin-child");
  else if (sub === "deesis") whole("deesis");
  else if (sub === "court" || sub === "empress") {                      // (the palace behind them: an entablature over their heads, its columns at the ends, curtains looped back: not gold left over)
    const e = (y1 - y0) * (bands ? .045 : .1), top = y1 - e, cW = W * .022, col = one([3, 5, 8], r), hang = one([3, 8, 4], r), at = [-W * .47, W * .47];
    out.push({ pts: rectAt(0, top + e / 2, W * 1.02, e), fill: C.bg }, { pts: rectAt(0, top + line / 2, W * 1.02, line), fill: 5 }, { pts: rectAt(0, y1 - line / 2, W * 1.02, line), fill: 5 });
    if (!bands) out.push({ items: STRIPS[one(WALL_BANDS, r)](W, e * .7, C).map((q) => ({ ...q, pts: q.pts.map(([a, b]) => [a, b + top + e / 2]) })), within: rectAt(0, top + e / 2, W * 1.02, e * .7) });
    for (const X of at) { const s = X < 0 ? 1 : -1; out.push({ pts: rectAt(X, (y0 + top) / 2, cW, top - y0), fill: col, line: ink, w: line }, { pts: rectAt(X, top - cW * .4, cW * 1.8, cW * .8), fill: 5 }, { pts: rectAt(X, y0 + cW * .4, cW * 1.8, cW * .8), fill: 5 }); out.push({ pts: [[X + s * cW / 2, top], [X + s * W * .1, top], [X + s * W * .045, top - (top - y0) * .34], [X + s * cW * .9, y0 + (top - y0) * .34]], fill: hang, line: ink, w: line }); }
    out.push(story(sub === "court" ? "emperor-court" : "empress-court", 0, -W * .44, y0, W * .44, top - (top - y0) * .03));
  }
  else if (sub === "apostles") whole("apostles-row");
  else if (sub === "fathers") { const piers = P.piers ?? [-W / 3, 0, W / 3], h = P.h ?? (y1 - y0) * .96, foot = P.foot ?? y0, list = shuffled(one(COMPANIES, r), r), half = W / piers.length * .48, niche = one(["none", "arch", "arch", "blue", "shell"], r), rim = one([3, 1, 5], r); piers.forEach((X, i) => {
      if (niche !== "none") { const u = half * .9, sp = Math.max(h * .5, Math.min(h * .8, h - u * 1.03)), top = foot + sp, arc = (q) => Array.from({ length: 15 }, (_, k) => [X + q * Math.cos(Math.PI * k / 14), top + q * Math.sin(Math.PI * k / 14)]), ins = u * .86, nh = [[X + ins, foot], ...arc(ins), [X - ins, foot]]; out.push({ pts: [[X + u, foot], ...arc(u), [X - u, foot]], hole: nh, fill: rim }); if (niche === "blue") out.push({ pts: nh, fill: 4 }); if (niche === "shell") for (let k = 1; k < 8; k += 2) { const a = Math.PI * k / 8; out.push({ pts: [[X, top], [X + ins * .96 * Math.cos(a - .1), top + ins * .96 * Math.sin(a - .1)], [X + ins * .96 * Math.cos(a + .1), top + ins * .96 * Math.sin(a + .1)]], fill: 5 }); } }
      out.push(person(list[i], i, X - half * (niche === "none" ? 1 : .8), foot, X + half * (niche === "none" ? 1 : .8), foot + h * (niche === "none" ? 1 : .96), undefined, undefined, niche === "blue" ? "cobalt" : name)); }); }
  else if (sub === "shepherd") whole(one(["good-shepherd", "shepherd-lamb"], r));
  else if (sub === "lambs") whole("lambs");
  else if (sub === "cross") whole("apse-cross");
  else if (sub === "nativity") whole("nativity-byz");
  else if (sub === "roundels") { const n = W / (y1 - y0) > 1.3 ? 3 : 2, list = shuffled(["peter", "paul", "andrew", "john", "apostle-byz", "archangel", "father", "john-baptist", "theotokos"], r), R = Math.min((y1 - y0) * .46, W / n * .46); for (let k = 0; k < n; k++) { const X = -W / 2 + (k + .5) * W / n, Y = (y0 + y1) / 2, within = disc(X, Y, R * .94, 40); out.push({ pts: disc(X, Y, R, 40), fill: blue ? 0 : 4 }, { pts: disc(X, Y, R, 40), hole: disc(X, Y, R * .92, 40), fill: C.a }); out.push(person(list[k], k, X - R * .85, Y - R * .92, X + R * .85, Y + R * .84, within, { bust: true, holdL: null }, blue ? "gold" : "cobalt")); } }
  else if (sub === "arcade") { const n = W / (y1 - y0) > 1.2 ? 3 : 2, list = shuffled(CANON.cycles.saints ?? ["peter", "paul", "andrew", "archangel", "father", "john", "theotokos"], r), u = W / n, sp = (y1 - y0) * .78; for (let k = 0; k < n; k++) { const X = -W / 2 + (k + .5) * u, a = Array.from({ length: 13 }, (_, i) => [X + u * .4 * Math.cos(Math.PI * i / 12), y0 + sp + u * .3 * Math.sin(Math.PI * i / 12)]), arc = [[X + u * .4, y0], ...a, [X - u * .4, y0]]; out.push({ pts: arc, line: 3, w: line * 1.5 }, { pts: rectAt(X - u / 2, y0 + sp / 2, line * 1.8, sp), fill: 5 }); out.push(person(list[k], k, X - u * .36, y0, X + u * .36, y0 + sp + u * .2)); } }
  else throw new Error(`no wall subject "${sub}"`);
  return { ground, ...P.set, layers: flatten(out, stone) };
}

// A FIELD or a STRIP, one tile of something that goes on
function planField(L, [W, H]) {
  const P0 = L.plan, seed = L.seed ?? 1, r = stream(scramble(seed), "field"), kind = P0.field ?? one(P0.fields ?? ROMAN_FIELDS, r), P = { ...P0, ...P0.sets?.[kind] }, Sa = P.schemes ?? [[1, 1, 2, 1, 0]], [a, b, c, ink, bg] = one(Sa, r), room = Math.floor(Math.min(W, H) / ((P.stone ?? L.stone ?? .012) * 11)), n = Math.max(1, Math.min(room, P.n ?? 3 + Math.floor(r() * 4))), v = P.v ?? Math.floor(r() * 4);   // (a cell of at least eleven stones: what's finer is lost among them. `sets`: a field's own stone and laying)
  return { ground: bg, ...(P.stone ? { stone: P.stone } : null), ...P.set, layers: [{ kind: "polys", items: offEdge(solid(FIELDS[kind](W, H, Math.min(W, H) / n, { a, b, c, ink, bg }, 1, v), P.stone ?? L.stone ?? .012), W, H) }] };
}
function planStrip(L, [W, H]) {
  const P = L.plan, seed = L.seed ?? 1, r = stream(scramble(seed), "strip"), kind = P.strip ?? one(P.strips ?? ROMAN_STRIPS, r), [a, b, c, ink, bg] = one(P.schemes ?? [[1, 1, 2, 1, 0]], r), bar = H * (P.bar ?? .06);
  return { ground: bg, ...(P.stone ? { stone: P.stone } : null), layers: [{ kind: "polys", items: [...offEdge(solid(STRIPS[kind](W, H - 4 * bar, { a, b, c, ink, bg }), P.stone ?? L.stone ?? .012), W, 0), { pts: rectAt(0, H / 2 - bar, W * 1.02, bar), fill: ink }, { pts: rectAt(0, -H / 2 + bar, W * 1.02, bar), fill: ink }] }] };
}

const PLANS = { floor: planFloor, wall: planWall, field: planField, strip: planStrip };
const tuned = (pal, seed, keep) => { if (keep) return pal; const r = stream(scramble(seed), "tune"), warm = (r() - .5) * .07, lit = 1 + (r() - .5) * .08; return pal.map(([a, b, c]) => [a * lit * (1 + warm), b * lit, c * lit * (1 - warm)].map((v) => Math.max(0, Math.min(255, v)))); };

// the layer to lay: its plan worked out, a nested Greek painting following the seed (`follow`: its seed less the layer's). -> [layer, palette]
export function planned(L, tile, pal) {
  const kept = L.plan && L.seed === L.plan.keep, follows = L.follow !== undefined;
  if (follows && L.layers) { const A = { ...L, layers: L.layers.map((q) => { if (q.kind !== "greek") return q; const list = q.seed !== L.seed + L.follow && rigged() && CANON.rig.emblems[q.painting]; if (!list) return { ...q, seed: L.seed + L.follow }; const [w, h] = q.box ?? tile, stone = L.stone ?? .012; return { kind: "rig", scene: one(list, stream(scramble(L.seed), "emblem", q.painting)), seed: L.seed, frame: { x0: -w / 2, x1: w / 2, y0: -h / 2, y1: h / 2 }, stone, tech: "mosaic", paper: "#e7e0cf", earth: 7, fill: .86, tree: { dye: OPUS, ink: 1, ground: "white", line: stone * INK, stone } }; }) }; return [A, pal]; }
  if (!L.plan || kept) return [L, pal];
  const make = PLANS[L.plan.kind];
  if (!make) throw new Error(`no mosaic plan "${L.plan.kind}"`);
  return [{ ...L, ...make(L, tile) }, tuned(pal, L.seed ?? 1)];
}
