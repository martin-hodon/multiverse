// HIEROGLYPHS (2026-10-05): the signs of Egyptian writing, built from the pattern language's shapes (patterns.js -- the
// circles, ellipses, rects, splines, paths and lines every surface is drawn with: one 2D engine, not two) -- each level
// naming only the one below it:
//
//   a shape      patterns.js: { shape: "spline", points, fill, stroke, at, rot, scale, ... }  (and here a `limb`: a
//                thick stroke with its outline -- an arm, a leg, a reed's stem)
//   a part       assets/glyphs/parts.json: an eye, a wig, a bird's body, a seated man's legs -- shapes in its own frame,
//                its colours ROLES ("skin", "wig", "plumage") with defaults
//   a sign       assets/glyphs/<category>.json (Gardiner's list: A man ... Aa unclassified): parts and shapes in the
//                QUADRAT -- 100 units square, x right, y up, the baseline at 0 -- facing LEFT as Gardiner's list and
//                Unicode have them (a line read the other way mirrors them all: `flip`), its roles given the painter's
//                colours (assets/glyphs/colors.json: red ochre, yellow ochre, Egyptian blue, green, black, white)
//   a text       assets/glyphs/textures.json: a wall of them -- an X x Y grid of quadrats, filled by seed, the signs packed
//                as scribes pack them (one tall sign; two flat ones stacked; two small side by side), in columns or rows
//                with dividers, a cartouche now and then, in full colour or one colour (renderTexture; a pattern layer
//                { kind: "hieroglyphs" } draws one on a building's wall)
//
// A layer that is a part or another sign: { part: "eye" | sign: "A1", at, rot, scale, flip, colors: { role: colour } }.
// A colour is a role of the sign (or part) it is in, a name of the painter's palette, or "#rrggbb"; the roles a sign
// sets flow down into every part it uses (a woman's yellow skin reaches her arm), a part's own defaults filling what
// nobody set. Every filled shape is OUTLINED in the "line" role (`outline: false` not; a sign's `outline` its width)
// at one width however far down it is scaled.
import { drawShapes, LAYER_KINDS } from "./patterns.js";

const PARTS = new Map(), SIGNS = new Map(), TEXTURES = new Map();
let COLORS = {}, MODES = {}, DOCS = [];
const cache = new Map();   // bounds and drawn signs: emptied whenever the library changes

// THE LIBRARY: every glyph document -- the colours ({ colors, modes }), parts ({ parts }), a category's signs
// ({ category, signs }), the textures ({ textures }) -- by its path
export function registerGlyphs(docs) {
  for (const [path, d] of Object.entries(docs)) {
    DOCS = DOCS.filter(([p]) => p !== path).concat([[path, d]]);
    if (d.colors) COLORS = { ...COLORS, ...d.colors };
    if (d.modes) MODES = { ...MODES, ...d.modes };
    for (const [k, v] of Object.entries(d.parts ?? {})) PARTS.set(k, v);
    for (const [k, v] of Object.entries(d.signs ?? {})) SIGNS.set(k, { ...v, code: k, category: d.category ?? k.replace(/\d.*$/, "") });
    for (const [k, v] of Object.entries(d.textures ?? {})) TEXTURES.set(k, v);
  }
  cache.clear();
}
export const signCodes = () => [...SIGNS.keys()];
export const signOf = (code) => SIGNS.get(code);
export const partNames = () => [...PARTS.keys()];
export const textureOf = (ref) => (typeof ref === "string" ? TEXTURES.get(ref) : ref);
export const textureNames = () => [...TEXTURES.keys()];
// everything a drawing depends on (a cache's key: pregen.js)
export const glyphLibrary = () => DOCS.map(([p, d]) => [p, d]);

// ---- colours ----------------------------------------------------------------------------------------------------------
// a name through the roles in scope, then the palette, to "#rrggbb"
function colourIn(v, scope, where) {
  for (let i = 0; i < 12 && typeof v === "string"; i++) {
    if (v.startsWith("#")) return v;
    if (scope[v] !== undefined && scope[v] !== v) v = scope[v];
    else if (COLORS[v] !== undefined) v = COLORS[v];
    else throw new Error(`${where}: no colour "${v}" (a role set here, or one of ${Object.keys(COLORS).join(" ")})`);
  }
  if (typeof v !== "string" || !v.startsWith("#")) throw new Error(`${where}: colour ${JSON.stringify(v)} goes round in circles`);
  return v;
}
// the roles a used part sees: its own defaults, then the roles of whoever uses it, then what that one says for it here
function scopeFor(sub, outer, colors, where) {
  const own = {};
  for (const [k, v] of Object.entries(sub.colors ?? {})) own[k] = colourIn(v, { ...outer, [k]: undefined }, where);
  const said = {};
  for (const [k, v] of Object.entries(colors ?? {})) said[k] = colourIn(v, outer, where);
  return { ...own, ...outer, ...said };
}

// ---- compiling: a sign (or part) to plain pattern layers ---------------------------------------------------------------
// `k`: how much it is scaled down where it stands (its outline is drawn at one width however deep it is); `mode`: a way
// of painting all of it ({ fill, line }: one colour for every sign; carved; a red draft) -- colors.json `modes`
const OPEN = (L) => L.shape === "line" || L.shape === "arc" || (L.shape === "spline" && L.closed === false);
function compile(layers, scope, { k = 1, mode = null, outline = 1.1, where, depth = 0 }) {
  if (depth > 8) throw new Error(`${where}: parts use each other too deep`);
  const out = [], C = (v) => colourIn(v, scope, where);
  const paint = (v, role) => (mode?.[role] === null ? null : mode?.[role] !== undefined ? C(mode[role]) : C(v));
  for (const L0 of layers ?? []) {
    const { part, sign, flip, colors, outline: ol, ...L } = L0;
    if (part !== undefined || sign !== undefined) {
      const sub = part !== undefined ? PARTS.get(part) : SIGNS.get(sign);
      if (!sub) throw new Error(`${where}: no ${part !== undefined ? "part" : "sign"} "${part ?? sign}"`);
      const sc = Array.isArray(L.scale) ? L.scale : [L.scale ?? 1, L.scale ?? 1], f = Math.sqrt(Math.abs(sc[0] * sc[1])) || 1;
      const inner = compile(sub.layers, scopeFor(sub, scope, colors, where), { k: k * f, mode, outline: ol ?? sub.outline ?? outline, where: `${where} > ${part ?? sign}`, depth: depth + 1 });
      out.push({ ...L, scale: [flip ? -sc[0] : sc[0], sc[1]], layers: inner });
      continue;
    }
    if (L.layers) { out.push({ ...L, layers: compile(L.layers, scope, { k, mode, outline: ol ?? outline, where, depth }) }); continue; }
    const w = (ol === false ? 0 : typeof ol === "number" ? ol : outline) / k;   // (the outline's width, in this frame)
    const lineC = paint("line", "line");
    if (L.shape === "limb") {   // a thick stroke and its outline: the outline a wider stroke under it
      const { shape, w: lw = 6, fill, ...rest } = L, base = { ...rest, shape: "spline", closed: false, cap: L.cap ?? "round" };
      const body = fill !== undefined ? paint(fill, "fill") : null;
      if (w > 0 && lineC) out.push({ ...base, stroke: lineC, line: lw + 2 * w });
      if (body) out.push({ ...base, stroke: body, line: lw });
      continue;
    }
    const M = { ...L };
    if (M.fill !== undefined) { const f = paint(M.fill, "fill"); if (f === null) delete M.fill; else M.fill = f; }
    // (a stroke on a filled shape is its outline; a stroke alone is a fine DETAIL -- an eye's line, a mat's weave -- or,
    //  thicker than 2.5, the sign's very body: the water's zigzag, a house's walls -- painted as a fill is)
    if (M.stroke !== undefined) { const role = L.fill !== undefined ? "line" : (L.line ?? 1.4) > 2.5 ? "fill" : "detail"; const s = paint(M.stroke, role); if (s === null) delete M.stroke; else M.stroke = s; }
    if (M.stroke === undefined && L.fill !== undefined && !OPEN(L) && w > 0 && lineC) { M.stroke = lineC; M.line = w; }
    else if (M.stroke !== undefined && M.line === undefined) M.line = 1.4;
    if (M.fill === undefined && M.stroke === undefined) continue;
    out.push(M);
  }
  return out;
}
const modeOf = (m) => (m && m !== "polychrome" ? (typeof m === "string" ? MODES[m] ?? (() => { throw new Error(`no glyph mode "${m}" (${Object.keys(MODES).join(" ")})`); })() : m) : null);
// a sign's layers, ready to draw (cached by code and mode)
function compiled(code, mode) {
  const key = `c|${code}|${JSON.stringify(mode ?? null)}`;
  if (cache.has(key)) return cache.get(key);
  const s = SIGNS.get(code) ?? PARTS.get(code);
  if (!s) throw new Error(`no sign or part "${code}"`);
  const m = modeOf(mode), scope = scopeFor(s, {}, null, code);
  const out = compile(s.layers, scope, { mode: m, outline: s.outline ?? 1.1, where: code });
  cache.set(key, out);
  return out;
}

// LAYERS IN THIS LANGUAGE DRAWN ANYWHERE (murals.js: a tomb painting's figures): parts and shapes, their roles given
// `colors` (resolved through the painter's palette), into `g` with the layers' units at `scale` pixels, their origin
// at (x, y) on the canvas, y up, mirrored by `flip`
export function drawGlyphLayers(g, layers, { x = 0, y = 0, scale = 1, flip = false, colors = {}, outline = 1.1, mode = null, where = "drawing" } = {}) {
  const scope = scopeFor({ colors }, {}, null, where);
  const out = compile(layers, scope, { mode: modeOf(mode), outline, where });
  g.save();
  g.transform(flip ? -scale : scale, 0, 0, -scale, x, y);
  drawShapes(g, out, { tile: [100, 100], ppm: scale });
  g.restore();
}
export const glyphColour = (v, roles = {}) => colourIn(v, roles, "colour");

// ---- drawing ------------------------------------------------------------------------------------------------------------
// (2D contexts kept in SOFTWARE -- willReadFrequently: Chromium puts a larger canvas on the GPU, and a GPU canvas can be
//  lost, and come back blank, while WebGPU starts; a text is drawn once and laid on a wall long after)
const ctx2d = (cv) => cv.getContext("2d", { willReadFrequently: true });
const mkCanvas = (w, h) => typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(w, h) : Object.assign(document.createElement("canvas"), { width: w, height: h });
// a sign drawn into `g`: the quadrat's units mapped onto [x, y, size] pixels (y down on the canvas), mirrored by `flip`;
// `view` the units the square shows ([x0, y0, x1, y1]; the quadrat, 0..100, by default)
export function drawGlyph(g, code, { x = 0, y = 0, size = 100, flip = false, mode = null, view = [0, 0, 100, 100] } = {}) {
  const [vx0, vy0, vx1, vy1] = view, k = size / Math.max(vx1 - vx0, vy1 - vy0);
  g.save();
  if (flip) g.transform(-k, 0, 0, -k, x + size + vx0 * k, y + size + vy0 * k);   // (x' = x + size - (u - vx0) k)
  else g.transform(k, 0, 0, -k, x - vx0 * k, y + size + vy0 * k);
  drawShapes(g, compiled(code, mode), { tile: [100, 100], ppm: k });
  g.restore();
}
// a sign on its own canvas, `px` square
export function renderGlyph(code, { px = 128, flip = false, mode = null, ground = null, view } = {}) {
  const cv = mkCanvas(px, px), g = ctx2d(cv);
  if (ground) { g.fillStyle = colourIn(ground, {}, code); g.fillRect(0, 0, px, px); }
  drawGlyph(g, code, { size: px, flip, mode, view });
  return cv;
}
// WHAT A SIGN COVERS, in quadrat units [x0, y0, x1, y1] -- read off a small drawing of it (how the text packs it)
export function boundsOf(code) {
  const key = `b|${code}`;
  if (cache.has(key)) return cache.get(key);
  const N = 120, view = PARTS.has(code) && !SIGNS.has(code) ? [-100, -100, 100, 100] : [-10, -10, 110, 110];
  const cv = renderGlyph(code, { px: N, view, mode: { fill: "black", line: "black", detail: "black" } });
  const d = ctx2d(cv).getImageData(0, 0, N, N).data;
  let x0 = N, x1 = -1, y0 = N, y1 = -1;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) if (d[(j * N + i) * 4 + 3] > 40) { if (i < x0) x0 = i; if (i > x1) x1 = i; if (j < y0) y0 = j; if (j > y1) y1 = j; }
  const u = (view[2] - view[0]) / N;
  const b = x1 < 0 ? [0, 0, 100, 100] : [view[0] + x0 * u, view[1] + (N - 1 - y1) * u, view[0] + (x1 + 1) * u, view[1] + (N - y0) * u];
  cache.set(key, b);
  return b;
}
// its CLASS for packing: tall (a standing man, a reed), wide (water, a mouth), small (a loaf, a stroke), big (a bird)
export function classOf(code) {
  const [x0, y0, x1, y1] = boundsOf(code), w = (x1 - x0) / 100, h = (y1 - y0) / 100;
  if (h >= .6 && w <= .6) return "tall";
  if (w >= .6 && h <= .42) return "wide";
  if (w <= .58 && h <= .58) return "small";
  return "big";
}

// ---- a text: a grid of quadrats -------------------------------------------------------------------------------------------
function rng(seed) {
  let a = (seed >>> 0) || 1;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
// the signs a text draws from, each with its weight: `pool` a list of categories and codes, or { category | code: weight }
// ("*" every sign), times each sign's own `freq` (how common it is in texts: the alphabet's signs most)
function poolOf(T) {
  const spec = T.pool ?? { "*": 1 }, ws = Array.isArray(spec) ? Object.fromEntries(spec.map((x) => [x, 1])) : spec;
  const out = [];
  for (const [code, s] of SIGNS) {
    const w = ws[code] ?? ws[s.category] ?? ws["*"] ?? 0;
    if (w > 0 && !s.notext) out.push([code, w * (s.freq ?? 1)]);
  }
  if (!out.length) throw new Error("the text's pool has no signs in it");
  const total = out.reduce((a, [, w]) => a + w, 0);
  return (r) => { let x = r() * total; for (const [c, w] of out) if ((x -= w) <= 0) return c; return out[out.length - 1][0]; };
}
// one quadrat's arrangement: ROWS of signs, top to bottom -- as a scribe groups them
function quadrat(r, pick) {
  const first = pick(r), c = classOf(first), want = (cls, n = 12) => { for (let i = 0; i < n; i++) { const s = pick(r); if (classOf(s) === cls) return s; } return null; };
  const narrow = (s) => { const [x0, , x1] = boundsOf(s); return x1 - x0 <= 42; };
  if (c === "tall") { const two = narrow(first) && r() < .4 ? want("tall") : null; return [two && narrow(two) ? [first, two] : [first]]; }
  if (c === "wide") {
    const u = r(), second = u < .55 ? want("wide") : u < .85 ? want("small") : null;
    if (!second) return [[first]];
    if (classOf(second) === "small") { const third = r() < .6 ? want("small") : null; return r() < .5 ? [[first], third ? [second, third] : [second]] : [third ? [second, third] : [second], [first]]; }
    const third = r() < .25 ? want("wide") : null;
    return third ? [[first], [second], [third]] : [[first], [second]];
  }
  if (c === "small") {
    const u = r();
    if (u < .45) { const b = want("small"); return b ? [[first, b]] : [[first]]; }
    if (u < .8) { const w = want("wide"), b = r() < .5 ? want("small") : null; return w ? [b ? [first, b] : [first], [w]] : [[first]]; }
    const a = want("small"), b = want("small"), d = want("small");
    return a && b && d ? [[first, a], [b, d]] : [[first]];
  }
  return [[first]];
}
// lay a quadrat's rows into a box [x, y, w, h] (canvas pixels, y down), each sign at its own size in the quadrat --
// smaller ones not blown up -- the whole shrunk to fit; `flip` mirrors the signs and their order in a row
function layQuadrat(g, rows, [X, Y, W, H], { flip, mode, gap = .06 }) {
  const dims = rows.map((row) => row.map((s) => { const [x0, y0, x1, y1] = boundsOf(s); return { s, b: [x0, y0, x1, y1], w: (x1 - x0) / 100, h: (y1 - y0) / 100 }; }));
  const rowW = dims.map((row) => row.reduce((a, d) => a + d.w, 0) + gap * (row.length - 1)), rowH = dims.map((row) => Math.max(...row.map((d) => d.h)));
  const totH = rowH.reduce((a, b) => a + b, 0) + gap * (rows.length - 1);
  const k = Math.min(1, (1 - gap) / Math.max(...rowW), (1 - gap) / totH), unit = Math.min(W, H);
  let cy = Y + (H - totH * k * unit) / 2;
  dims.forEach((row, i) => {
    const rw = rowW[i] * k * unit, rh = rowH[i] * k * unit;
    let cx = X + (W - rw) / 2;
    for (const d of flip ? [...row].reverse() : row) {
      const sw = d.w * k * unit, sh = d.h * k * unit, size = k * unit;
      // (the sign's bounds land at [cx, cy + rh - sh]: its square of `size` px placed so; a flat sign sits on its row's base)
      const ox = flip ? cx + sw - (100 - d.b[0]) / 100 * size : cx - d.b[0] / 100 * size;
      const oy = cy + rh - sh - (100 - d.b[3]) / 100 * size;
      drawGlyph(g, d.s, { x: ox, y: oy, size, flip, mode });
      cx += sw + gap * k * unit;
    }
    cy += rh + gap * k * unit;
  });
}
// A WALL OF TEXT: { cols, rows (quadrats), lines: "columns" | "rows", face: "left" | "right" | "alternate" | "random",
// pool, mode, ground, divider: { color, width } (between the lines), border: { color, width }, cartouche (the chance a
// line's next quadrats are a name in a cartouche), seed } -> a canvas `cell` pixels a quadrat
export function renderTexture(ref, { seed, cell, px } = {}) {
  const T = textureOf(ref);
  if (!T) throw new Error(`no hieroglyph texture "${ref}"`);
  const cols = Math.max(1, T.cols ?? 8), rows = Math.max(1, T.rows ?? 6), byCol = (T.lines ?? "columns") === "columns";
  const q = cell ?? (px ? px / cols : T.cell ?? 64), W = Math.round(cols * q), H = Math.round(rows * q);
  const cv = mkCanvas(W, H), g = ctx2d(cv), r = rng((seed ?? T.seed ?? 1) * 7919 + 13), pick = poolOf(T);
  const C = (v) => colourIn(v, {}, "texture"), mode = T.mode ?? null;
  g.fillStyle = C(T.ground ?? "ground"); g.fillRect(0, 0, W, H);
  const nLines = byCol ? cols : rows, perLine = byCol ? rows : cols;
  for (let li = 0; li < nLines; li++) {
    const face = T.face ?? "left";
    const flip = face === "right" ? true : face === "alternate" ? li % 2 === 1 : face === "random" ? r() < .5 : false;
    let named = false;   // (one name a line at most)
    for (let qi = 0; qi < perLine; ) {
      const box = (i, n = 1) => byCol ? [li * q, i * q, q, q * n] : [i * q, li * q, q * n, q];
      const room = perLine - qi;
      if (T.cartouche && !named && room >= 2 && r() < T.cartouche) {
        named = true;   // a NAME: two or three quadrats in an oval ring, the knot at its end
        const n = Math.min(room, 2 + (r() < .4 ? 1 : 0)), [bx, by, bw, bh] = box(qi, n), m = q * .07;
        const lw = Math.max(1, q * .035);
        g.strokeStyle = C(mode && MODES[mode]?.line ? MODES[mode].line : "line"); g.lineWidth = lw;
        g.beginPath(); g.roundRect(bx + m, by + m, bw - 2 * m, bh - 2 * m, (byCol ? bw : bh) / 2 - m); g.stroke();
        g.lineWidth = lw * 1.6; g.beginPath();
        if (byCol) { g.moveTo(bx + m * 1.5, by + bh - m * .3); g.lineTo(bx + bw - m * 1.5, by + bh - m * .3); }
        else { const ex = flip ? bx + m * .3 : bx + bw - m * .3; g.moveTo(ex, by + m * 1.5); g.lineTo(ex, by + bh - m * 1.5); }
        g.stroke();
        for (let i = 0; i < n; i++) { const [x, y, w, h] = box(qi + i); layQuadrat(g, quadrat(r, pick), [x + q * .14, y + q * .14, w - q * .28, h - q * .28], { flip, mode }); }
        qi += n; continue;
      }
      layQuadrat(g, quadrat(r, pick), box(qi), { flip, mode });
      qi++;
    }
  }
  if (T.divider) {
    g.fillStyle = C(T.divider.color ?? "line");
    const w = Math.max(1, (T.divider.width ?? .03) * q);
    for (let li = 1; li < nLines; li++) byCol ? g.fillRect(li * q - w / 2, 0, w, H) : g.fillRect(0, li * q - w / 2, W, w);
    // (and the one between this text and the next copy of it: half at each edge, so a wall of it repeats without a seam)
    if (T.seamless !== false && !T.border) byCol ? (g.fillRect(0, 0, w / 2, H), g.fillRect(W - w / 2, 0, w / 2, H)) : (g.fillRect(0, 0, W, w / 2), g.fillRect(0, H - w / 2, W, w / 2));
  }
  if (T.border) { const w = Math.max(1, (T.border.width ?? .05) * q); g.strokeStyle = C(T.border.color ?? "line"); g.lineWidth = w; g.strokeRect(w / 2, w / 2, W - w, H - w); }
  return cv;
}

// ---- the sheets the viewer shows ---------------------------------------------------------------------------------------
// a category's signs (or the parts, or the colours): each in a quadrat on the ground, its code and name, its mirror small
export function drawGlyphSheet(cv, doc, { cell = 132, only = null, mode = null, seed = 1 } = {}) {
  const g = cv.getContext("2d", { willReadFrequently: true });
  const errors = [];
  if (doc.textures) {   // each text whole, one under the other
    let y = 10;
    const list = Object.entries(doc.textures).filter(([k]) => !only || k === only);
    const draws = list.map(([name, T]) => { try { return [name, renderTexture(T, { seed: (T.seed ?? 1) + seed - 1, cell: Math.min(T.cell ?? 56, (cv.width - 20) / (T.cols ?? 8)) })]; } catch (e) { errors.push(`${name}: ${e.message}`); return [name, null]; } });
    cv.height = Math.max(cv.height, draws.reduce((a, [, c]) => a + (c ? c.height : 20) + 34, 20));
    g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height); g.font = "12px ui-monospace, monospace";
    for (const [name, c] of draws) {
      g.fillStyle = "#d8d4cc"; g.fillText(name + (c ? `  ${doc.textures[name].cols ?? 8} x ${doc.textures[name].rows ?? 6} quadrats` : "  (failed)"), 10, y + 12);
      if (c) { g.drawImage(c, 10, y + 20); y += c.height + 34; } else y += 34;
    }
    return errors;
  }
  if (doc.colors && !doc.parts && !doc.signs) {   // the palette: each colour a swatch, and the modes
    const list = Object.entries(doc.colors), cols = Math.max(1, Math.floor((cv.width - 10) / 170));
    cv.height = Math.max(cv.height, Math.ceil(list.length / cols) * 46 + 20);
    g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height); g.font = "12px ui-monospace, monospace";
    list.forEach(([name, v], i) => {
      const x = 10 + (i % cols) * 170, y = 10 + Math.floor(i / cols) * 46;
      let c; try { c = colourIn(name, {}, "colors"); } catch (e) { errors.push(e.message); c = "#000"; }
      g.fillStyle = c; g.fillRect(x, y, 34, 34); g.strokeStyle = "#555"; g.strokeRect(x + .5, y + .5, 33, 33);
      g.fillStyle = "#d8d4cc"; g.fillText(name, x + 42, y + 14); g.fillStyle = "#8d8a84"; g.fillText(v.startsWith("#") ? v : `= ${v}`, x + 42, y + 29);
    });
    return errors;
  }
  const items = Object.entries(doc.signs ?? doc.parts ?? {}).filter(([k]) => !only || k === only), isPart = !doc.signs;
  const cols = Math.max(1, Math.floor((cv.width - 10) / (cell + 12))), rowH = cell + 46;
  cv.height = Math.max(cv.height, Math.ceil(items.length / cols) * rowH + 10);
  g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height); g.font = "12px ui-monospace, monospace";
  const ground = (() => { try { return colourIn("ground", {}, "sheet"); } catch { return "#e8dcc0"; } })();
  items.forEach(([code, s], i) => {
    const x = 10 + (i % cols) * (cell + 12), y = 10 + Math.floor(i / cols) * rowH;
    g.fillStyle = ground; g.fillRect(x, y, cell, cell);
    try {
      if (isPart) { const b = boundsOf(code), m = Math.max(b[2] - b[0], b[3] - b[1]) * 1.12, cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2; drawGlyph(g, code, { x, y, size: cell, mode, view: [cx - m / 2, cy - m / 2, cx + m / 2, cy + m / 2] }); }
      else {
        g.strokeStyle = "rgba(0,0,0,.12)"; g.strokeRect(x + .5, y + .5, cell - 1, cell - 1);
        drawGlyph(g, code, { x, y, size: cell, mode });
        const sm = 38;   // (its mirror, small, under it by the label: a line read the other way)
        g.fillStyle = ground; g.fillRect(x + cell - sm, y + cell + 4, sm, sm);
        drawGlyph(g, code, { x: x + cell - sm, y: y + cell + 4, size: sm, flip: true, mode });
      }
    } catch (e) { errors.push(`${code}: ${e.message}`); g.fillStyle = "#c0392b"; g.fillText("error", x + 6, y + 18); }
    g.fillStyle = "#d8d4cc"; g.fillText(code, x, y + cell + 14);
    g.fillStyle = "#8d8a84"; g.fillText(String(s.name ?? "").slice(0, Math.floor((cell - (isPart ? 0 : 42)) / 7)), x, y + cell + 28);
    if (s.reading) { g.fillStyle = "#6f8fb0"; g.fillText(String(s.reading).slice(0, Math.floor((cell - 42) / 7)), x, y + cell + 41); }
  });
  return errors;
}

// ---- on a building: a pattern layer { kind: "hieroglyphs", texture: name | { ...a texture }, seed, size: [w, h] } --------
// the text laid once over `size` metres (the tile's, unless said) about the layer's centre
LAYER_KINDS.hieroglyphs = {
  draw(g, L, { tile, ppm }) {
    const [w, h] = Array.isArray(L.size) ? L.size : tile, T = textureOf(L.texture ?? L), px = Math.max(16, Math.round(w * ppm));
    // (a repeating tile draws its layers at its eight neighbours too: the text is made once, and laid nine times)
    const key = `t|${JSON.stringify(T)}|${L.seed ?? ""}|${px}`;
    if (!cache.has(key)) cache.set(key, renderTexture(T, { seed: L.seed, px }));
    const cv = cache.get(key);
    g.save(); g.scale(1, -1); g.drawImage(cv, -w / 2, -h / 2, w, h); g.restore();
  },
  deps: (L) => ({ texture: textureOf(L.texture ?? L) ?? null, library: glyphLibrary() }),
};
