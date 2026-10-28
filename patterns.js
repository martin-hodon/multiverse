// PATTERNS: the surfaces of buildings -- a marble floor, a carpet, a wall of tiles, a painted beam, a roof of glazed
// tiles -- written as MATHEMATICS and drawn into a tile when they are needed. Nothing here is a picture: a pattern is
// a list of shapes (circles, polygons, stars, petals, lenses, bands, waves, paths...) set out on a tile a given number
// of metres across, repeated in grids, turned into symmetries, clipped to one another, filled from a PALETTE by slot --
// so the one pattern is every colouring of it -- and it may USE other patterns inside its shapes, which is how a carpet
// (a border of one pattern round a field of another round a medallion) or an Iznik panel is made of simpler ones.
// Stone that is not geometry (marble's veins, granite's speckle, a plaster's clouds, wood's grain) is a FIELD: a
// periodic function of the point, evaluated per texel.
//   The tile is drawn with Canvas2D paths -- exact, anti-aliased -- at whatever resolution is asked, every shape nine
// times (the tile and its eight neighbours) so it repeats without a seam. The game makes a texture of it (mipmapped,
// so it neither shimmers nor turns to moire in the distance); the asset viewer shows it as it is.
//
// The language (docs/patterns.md has it all):
//   { size: [w, h] metres, repeat: true|false, palette: name, ground: slot, res: texels across, layers: [...] }
//   a layer: { shape, <its numbers>, fill, stroke, line, at, rot, scale, grid, sym, mirror, alpha, shade, vary, clip,
//              layers (a group), use (another pattern), colors (a remap for it), field (a texture function) }
// Colours: a number is a slot of the palette, "#rrggbb" is itself.
import { evalNum } from "./expr.js";

const LIB = new Map();                   // "family/name" -> a pattern definition
export const PALETTES = {};
// the library: family documents ({ patterns: { name: def } }) and the palettes document ({ palettes: { name: [...] } })
export function registerPatterns(families) {
  for (const [fam, doc] of Object.entries(families)) {
    if (doc.palettes) Object.assign(PALETTES, doc.palettes);
    for (const [k, d] of Object.entries(doc.patterns ?? {})) LIB.set(`${fam}/${k}`, d);
  }
}
export const patternOf = (ref) => typeof ref === "string" ? LIB.get(ref) : ref;
export const patternNames = () => [...LIB.keys()];
// the patterns a definition uses (nested), for a page that fetches the library as it needs it
export function usesOfPattern(def, out = new Set()) {
  const walk = (ls) => { for (const l of ls ?? []) { if (l.use) out.add(l.use.split("/")[0]); walk(l.layers); } };
  walk(def.layers);
  return out;
}

// ---- colours ------------------------------------------------------------------------------------------------------
const hex = (s) => { const v = parseInt(s.slice(1), 16); return [(v >> 16) & 255, (v >> 8) & 255, v & 255]; };
const css = ([r, g, b], a = 1) => `rgba(${r | 0},${g | 0},${b | 0},${a})`;
// a palette: a name (palettes.json), a list of "#rrggbb", or the pattern's own
export function paletteOf(def, palette) {
  const p = palette ?? def.palette ?? "stone";
  const list = Array.isArray(p) ? p : PALETTES[p];
  if (!list) throw new Error(`no palette "${p}"`);
  return list.map((c) => (typeof c === "string" ? hex(c) : c));
}
// a small deterministic hash in [0, 1) of integers
const hash = (...k) => { let h = 2166136261; for (const v of k) { h = Math.imul(h ^ (v | 0), 16777619); h ^= h >>> 13; } return ((h >>> 0) % 100003) / 100003; };
const shadeRGB = (c, s) => s >= 0 ? c.map((v) => v + (255 - v) * s) : c.map((v) => v * (1 + s));

// ---- numbers --------------------------------------------------------------------------------------------------------
// every number may be an expression over the pattern's params (and W, H: the tile's size) -- the same parser as the
// buildings' (expr.js)
const numOf = (v, P, d) => v === undefined ? d : typeof v === "number" ? v : evalNum(v, P);
const pairOf = (v, P, d) => v === undefined ? d : Array.isArray(v) ? [numOf(v[0], P), numOf(v[1], P)] : [numOf(v, P), numOf(v, P)];

// ---- shapes: each a Path2D at the origin, in metres, y up -------------------------------------------------------------
const TAU = Math.PI * 2;
function shapePath(L, P, tile) {
  const p = new Path2D(), N = (k, d) => numOf(L[k], P, d);
  switch (L.shape) {
    case "rect": { const w = N("w", 1), h = N("h", w), r = N("r", 0); if (r > 0) p.roundRect(-w / 2, -h / 2, w, h, r); else p.rect(-w / 2, -h / 2, w, h); break; }
    case "circle": p.arc(0, 0, N("r", .5), 0, TAU); break;
    case "ellipse": p.ellipse(0, 0, N("rx", .5), N("ry", .25), 0, 0, TAU); break;
    case "ring": { const r = N("r", .5), w = N("w", .1); p.arc(0, 0, r, 0, TAU); p.moveTo(r - w, 0); p.arc(0, 0, r - w, 0, TAU, true); break; }
    case "poly": case "star": {
      const n = Math.round(N("n", 6)), r = N("r", .5), inner = L.shape === "star" ? N("inner", .5) : 1, k = L.shape === "star" ? 2 * n : n;
      for (let i = 0; i < k; i++) {
        const a = Math.PI / 2 + i * TAU / k, rr = i % 2 && L.shape === "star" ? r * inner : r;
        if (i) p.lineTo(rr * Math.cos(a), rr * Math.sin(a)); else p.moveTo(rr * Math.cos(a), rr * Math.sin(a));
      }
      p.closePath(); break;
    }
    case "lens": {                        // a vesica along x, `r` from the middle to each point, `w` across
      const r = N("r", .5), w = N("w", .3);
      p.moveTo(-r, 0); p.quadraticCurveTo(0, w, r, 0); p.quadraticCurveTo(0, -w, -r, 0); p.closePath(); break;
    }
    case "petals": {                      // n lenses radiating from `inner` out to `r`, each `w` wide
      const n = Math.round(N("n", 8)), r = N("r", .5), r0 = N("inner", 0), w = N("w", .25 * r);
      for (let i = 0; i < n; i++) {
        const a = Math.PI / 2 + i * TAU / n, c = Math.cos(a), s = Math.sin(a), m = (r0 + r) / 2;
        const at = (u, v) => [u * c - v * s, u * s + v * c];
        p.moveTo(...at(r0, 0)); p.quadraticCurveTo(...at(m, w), ...at(r, 0)); p.quadraticCurveTo(...at(m, -w), ...at(r0, 0)); p.closePath();
      }
      break;
    }
    case "frame": {                       // a rectangle with a rectangle out of it: `t` wide all round (a border, a panel's frame)
      const w = N("w", 1), h = N("h", w), t = N("t", .1);
      p.rect(-w / 2, -h / 2, w, h); p.rect(-w / 2 + t, -h / 2 + t, w - 2 * t, h - 2 * t); break;
    }
    case "cross": { const w = N("w", 1), h = N("h", w), t = N("t", .2); p.rect(-w / 2, -t / 2, w, t); p.rect(-t / 2, -h / 2, t, h); break; }
    case "spline": {                      // a SMOOTH outline through `points` (Catmull-Rom, `tension` 0..1: 0 straight, .5 round);
      // a point [x, y, 1] is a CORNER (the curve comes into it straight); `closed: false` an open curve (stroked, not filled)
      const pts = L.points.map((q) => [numOf(q[0], P), numOf(q[1], P), q[2] ? 1 : 0]), n = pts.length, closed = L.closed !== false;
      const t = numOf(L.tension, P, .5), at = (i) => pts[closed ? ((i % n) + n) % n : Math.max(0, Math.min(n - 1, i))];
      const tan = (i) => { const q = at(i); if (q[2] || (!closed && (i === 0 || i === n - 1))) return [0, 0]; const a = at(i - 1), b = at(i + 1); return [(b[0] - a[0]) * t / 3, (b[1] - a[1]) * t / 3]; };
      p.moveTo(pts[0][0], pts[0][1]);
      for (let i = 0; i < (closed ? n : n - 1); i++) {
        const a = at(i), b = at(i + 1), ta = tan(i), tb = tan(i + 1);
        p.bezierCurveTo(a[0] + ta[0], a[1] + ta[1], b[0] - tb[0], b[1] - tb[1], b[0], b[1]);
      }
      if (closed) p.closePath();
      break;
    }
    case "points": { const pts = L.points.map((q) => [numOf(q[0], P), numOf(q[1], P)]); pts.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y))); p.closePath(); break; }
    case "path": return new Path2D(L.d);  // SVG path syntax, in metres, y up
    case "line": { const [x0, y0] = pairOf(L.from, P), [x1, y1] = pairOf(L.to, P); p.moveTo(x0, y0); p.lineTo(x1, y1); break; }
    case "arc": { const r = N("r", .5), a0 = N("a0", 0) * Math.PI / 180, a1 = N("a1", 180) * Math.PI / 180; p.arc(0, 0, r, a0, a1); break; }
    case "band": {                        // across the whole tile (and past it, for the wrap): `h` tall
      const h = N("h", .1), W = tile[0] * 3; p.rect(-W / 2, -h / 2, W, h); break;
    }
    case "vband": { const w = N("w", .1), H = tile[1] * 3; p.rect(-w / 2, -H / 2, w, H); break; }
    case "wave": case "zigzag": {          // a band `h` thick, swinging `amp` either side, `n` swings across the tile
      const h = N("h", .05), amp = N("amp", .1), n = Math.max(1, Math.round(N("n", 1))), W = tile[0], seg = 24 * n;
      const f = (x) => L.shape === "wave" ? amp * Math.sin(x / W * TAU * n) : amp * (1 - 4 * Math.abs(((x / W * n + .25) % 1 + 1) % 1 - .5)) ;
      const xs = []; for (let i = -seg; i <= 2 * seg; i++) xs.push(-W / 2 + i * W / seg);
      xs.forEach((x, i) => (i ? p.lineTo(x, f(x) + h / 2) : p.moveTo(x, f(x) + h / 2)));
      for (let i = xs.length - 1; i >= 0; i--) p.lineTo(xs[i], f(xs[i]) - h / 2);
      p.closePath(); break;
    }
    default: throw new Error(`pattern shape "${L.shape}" is not one of rect frame circle ellipse ring poly star lens petals cross points spline path line arc band vband wave zigzag`);
  }
  return p;
}

// ---- fields: periodic functions of the point, per texel ----------------------------------------------------------------
// gradient (Perlin) noise on a lattice that wraps with the tile -- so the field repeats with it -- in [0, 1]
// (a lattice point's gradient is worked out once, when first wanted, and kept: hashing it and its cos and sin at every
// corner of every texel's every octave was most of a world's startup -- 59 of 85 s cold, 2026-10-28)
function noise2(gx, gy, seed) {
  const C = new Float64Array(gx * gy).fill(NaN), S = new Float64Array(gx * gy);
  const dot = (i, j, dx, dy) => {
    i = ((i % gx) + gx) % gx; j = ((j % gy) + gy) % gy;
    const k = j * gx + i;
    if (C[k] !== C[k]) { const a = TAU * hash(i, j, seed); C[k] = Math.cos(a); S[k] = Math.sin(a); }
    return C[k] * dx + S[k] * dy;
  };
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  return (x, y) => {
    const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j;
    const d00 = dot(i, j, fx, fy), d10 = dot(i + 1, j, fx - 1, fy), d01 = dot(i, j + 1, fx, fy - 1), d11 = dot(i + 1, j + 1, fx - 1, fy - 1);
    const u = fade(fx), v = fade(fy);
    const a = d00 + (d10 - d00) * u, b = d01 + (d11 - d01) * u;
    return .5 + .7 * (a + (b - a) * v);
  };
}
// A FIELD'S VALUES, texel by texel, are the same in any colours: the last few are kept, and the next tile with the same
// field in other colours only colours them (the items' paints are one brushing in sixty colours -- 4.8 of a world's
// 6.6 s of item tiles, 2026-10-28; the woods one grain in their several)
const FIELDS = new Map(), FIELDS_KEPT = 8;
export function fieldImage(L, P, tile, W, H, pal) {
  const kind = L.field, sc = numOf(L.freq, P, 3), amount = numOf(L.amount, P, 1), seed = numOf(L.seed, P, 7);
  if (!["veins", "speckle", "cloud", "grain"].includes(kind)) throw new Error(`pattern field "${kind}" is not one of veins speckle cloud grain`);
  const [c0, c1] = [colorOf(L.colors?.[0] ?? 0, pal), colorOf(L.colors?.[1] ?? 1, pal)];
  const gx = Math.max(1, Math.round(tile[0] * sc)), gy = Math.max(1, Math.round(tile[1] * sc));
  const turns = Math.max(1, Math.round(numOf(L.turns, P, 2)));   // (veins: how many times a vein crosses the tile)
  // (speckle: grains `grain` metres across, on a lattice that wraps with the tile)
  const ggx = Math.max(1, Math.round(tile[0] / numOf(L.grain, P, .008))), ggy = Math.max(1, Math.round(tile[1] / numOf(L.grain, P, .008)));
  const c2 = colorOf(L.colors?.[2] ?? 3, pal);
  const sharp = numOf(L.sharp, P, 18), alpha = 255 * numOf(L.alpha, P, 1);
  const key = [kind, gx, gy, seed, turns, sharp, ggx, ggy, W, H].join();
  let F = FIELDS.get(key);
  if (F) { FIELDS.delete(key); FIELDS.set(key, F); }   // (the most recent last: the first is the next let go)
  else {
    // the field: per texel t -- or, speckled, the grain's n and the mottle's fbm, side by side
    F = new Float64Array(W * H * (kind === "speckle" ? 2 : 1));
    const oct = [0, 1, 2, 3].map((o) => noise2(gx << o, gy << o, seed + o));
    const [f0, f1, f2, f3] = oct;
    const fbm = (u, v) => (((0 + f0(u * gx, v * gy) / 2) + f1(u * (gx << 1), v * (gy << 1)) / 4) + f2(u * (gx << 2), v * (gy << 2)) / 8
      + f3(u * (gx << 3), v * (gy << 3)) / 16) / .9375;
    const grains = kind === "speckle" ? noise2(ggx, ggy, seed + 11) : null;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const u = (x + .5) / W, v = 1 - (y + .5) / H, i = y * W + x;   // (tile coordinates, 0..1, y up)
      if (kind === "veins") {                                     // marble: thin wandering veins, a soft cloud between
        const s = Math.sin(TAU * (turns * (u + v) + 1.6 * fbm(u, v)));
        F[i] = Math.pow(1 - Math.abs(s), sharp) * .9 + .12 * fbm(u * 2 % 1, v * 2 % 1);
      } else if (kind === "speckle") { F[i * 2] = grains(u * ggx, v * ggy); F[i * 2 + 1] = fbm(u, v); }   // granite: grains in a mottled ground
      else if (kind === "cloud") F[i] = fbm(u, v) - .5;           // plaster, weathering: a soft mottle
      else {                                                      // wood: rings stretched along u
        const s = Math.sin(TAU * (turns * v + 1.2 * fbm(u, v) + .3 * fbm(u * 4 % 1, v)));
        F[i] = .5 + .5 * s;
      }
    }
    FIELDS.set(key, F);
    if (FIELDS.size > FIELDS_KEPT) FIELDS.delete(FIELDS.keys().next().value);
  }
  // ...coloured
  const img = new ImageData(W, H), d = img.data;
  for (let j = 0, n = W * H; j < n; j++) {
    const i = j * 4;
    if (kind === "speckle") {                                   // dark grains and pale ones
      const g = F[j * 2], k = Math.max(0, Math.min(1, (g - .66) * 9)) * amount;
      const q = Math.max(0, Math.min(1, (.3 - g) * 9)) * amount, m = 1 + .12 * (F[j * 2 + 1] - .5);
      for (let c = 0; c < 3; c++) d[i + c] = (c0[c] * (1 - k - q) + c1[c] * k + c2[c] * q) * m;
      d[i + 3] = alpha;
      continue;
    }
    const k = Math.max(0, Math.min(1, F[j] * amount));
    d[i] = c0[0] + (c1[0] - c0[0]) * k; d[i + 1] = c0[1] + (c1[1] - c0[1]) * k; d[i + 2] = c0[2] + (c1[2] - c0[2]) * k;
    d[i + 3] = alpha;
  }
  const cv = mkCanvas(W, H);
  cv.getContext("2d").putImageData(img, 0, 0);
  return cv;
}

const mkCanvas = (w, h) => typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(w, h) : Object.assign(document.createElement("canvas"), { width: w, height: h });
function colorOf(c, pal) {
  if (typeof c === "string") return hex(c);
  return pal[((Math.round(c) % pal.length) + pal.length) % pal.length];
}

// ---- drawing ----------------------------------------------------------------------------------------------------------
// WHERE A LAYER IS DRAWN. Its CENTRES: the cells of its `grid` over the tile (rows from the top down, so a lower row
// overlaps the one above it: fish scales), or the tile's middle. About each centre its `sym` copies are turned and its
// `mirror` copies reflected, and in each of those the shape stands at `at` (one point or a list) -- so a circle `at`
// [0.05, 0] with `sym` 4 is four circles round the centre, and the same with a grid is four round every cell.
function centresOf(L, P, tile) {
  if (!L.grid) return [[0, 0, 0, 0]];
  const g = Array.isArray(L.grid) ? { n: L.grid } : L.grid, [nx, ny] = pairOf(g.n, P).map((v) => Math.max(1, Math.round(v)));
  const [sw, sh] = pairOf(g.span, P, tile), off = numOf(g.offset, P, 0);
  const out = [];
  for (let j = ny - 1; j >= 0; j--) for (let i = 0; i < nx; i++) out.push([-sw / 2 + (i + .5 + (j % 2) * off) * sw / nx, -sh / 2 + (j + .5) * sh / ny, i, j]);
  return out;
}
const atsOf = (L, P) => L.at === undefined ? [[0, 0]] : Array.isArray(L.at[0]) ? L.at.map((q) => pairOf(q, P)) : [pairOf(L.at, P)];

// LAYER KINDS DRAWN ELSEWHERE: a layer `{ kind: "<name>", ... }` is drawn by what another module registered under that
// name -- glyphs.js's "hieroglyphs" (a wall of text). It draws in the layer's frame (metres, y up, about the tile's
// middle) as `draw(g, L, { P, tile, ppm })`; `deps(L)` is the data it depends on beyond the layer (the cache's key,
// pregen.js). A module registering one imports this file, never the other way round.
export const LAYER_KINDS = {};
// (a curve with no inside: stroked, never filled)
const openShape = (L) => L.shape === "line" || L.shape === "arc" || (L.shape === "spline" && L.closed === false);

function drawLayers(g, layers, ctx) {
  for (const L of layers ?? []) drawLayer(g, L, ctx);
}
function drawLayer(g, L, ctx) {
  const { P, pal, tile } = ctx;
  if (L.when !== undefined && !numOf(L.when, P)) return;       // (a layer a param turns off)
  const rot = numOf(L.rot, P, 0) * Math.PI / 180, [sx, sy] = pairOf(L.scale, P, [1, 1]);
  const sym = Math.max(1, Math.round(numOf(L.sym, P, 1)));
  const mirrors = L.mirror === "x" ? [[1, 1], [-1, 1]] : L.mirror === "y" ? [[1, 1], [1, -1]] : L.mirror === "xy" ? [[1, 1], [-1, 1], [1, -1], [-1, -1]] : [[1, 1]];
  const vary = numOf(L.vary, P, 0), seed = numOf(L.seed, P, 1);
  const lw = numOf(L.line, P, .02);
  const ats = atsOf(L, P);
  for (const [x, y, i, j] of centresOf(L, P, tile)) for (let k = 0; k < sym; k++) for (const [mx, my] of mirrors) for (const [ax, ay] of ats) {
    g.save();
    g.translate(x, y); g.rotate(k * TAU / sym); g.scale(mx, my); g.translate(ax, ay); g.rotate(rot); g.scale(sx, sy);
    if (L.clip) {                                                           // (a clip shape may stand `at` a point, turned by `rot`)
      const cp = new Path2D(), [cx, cy] = pairOf(L.clip.at, P, [0, 0]);
      cp.addPath(shapePath(L.clip, P, tile), new DOMMatrix().translate(cx, cy).rotate(numOf(L.clip.rot, P, 0)));
      g.clip(cp, L.clip.rule ?? (L.clip.shape === "frame" || L.clip.shape === "ring" ? "evenodd" : "nonzero"));
    }
    g.globalAlpha = numOf(L.alpha, P, 1);
    const tone = (c) => { let rgb = colorOf(c, pal); if (L.shade) rgb = shadeRGB(rgb, numOf(L.shade, P)); if (vary) rgb = shadeRGB(rgb, vary * (2 * hash(i, j, k, seed) - 1)); return css(rgb); };
    if (L.kind) {                                                            // a kind another module draws
      const k = LAYER_KINDS[L.kind];
      if (!k) throw new Error(`pattern layer kind "${L.kind}" is not registered (${Object.keys(LAYER_KINDS).join(" ") || "none are"})`);
      k.draw(g, L, ctx);
    } else if (L.layers) drawLayers(g, L.layers, { ...ctx, top: false });            // a group, in this frame
    else if (L.use) {                                                         // another pattern, tiled inside the clip
      const sub = patternOf(L.use);
      if (!sub) throw new Error(`pattern "${L.use}" is not in the library`);
      const subPal = L.palette ? paletteOf(sub, L.palette) : L.colors ? L.colors.map((c) => colorOf(c, pal)) : pal;
      const s = numOf(L.useScale, P, 1), subTile = sizeOf(sub, {}).map((v) => v * s);
      const ppm = ctx.ppm, W = Math.max(8, Math.round(subTile[0] * ppm)), H = Math.max(8, Math.round(subTile[1] * ppm));
      const cv = drawTile(sub, { pal: subPal, px: [W, H], params: L.params ?? {}, depth: ctx.depth + 1 });
      const pat = g.createPattern(cv, "repeat");
      pat.setTransform(new DOMMatrix([subTile[0] / W, 0, 0, -subTile[1] / H, -subTile[0] / 2, subTile[1] / 2]));
      g.fillStyle = pat;
      const [w, h] = tile, area = L.shape ? shapePath(L, P, tile) : (() => { const q = new Path2D(); q.rect(-w * 1.5, -h * 1.5, w * 3, h * 3); return q; })();
      g.fill(area, L.rule ?? (L.shape === "ring" || L.shape === "frame" ? "evenodd" : "nonzero"));
    } else if (L.field) {
      // a field covers the tile exactly once, texel on texel: drawn with no transform at all, from the tile itself (not
      // its eight neighbours), unless it is turned, clipped or inside a group -- then it is placed like any shape
      const plain = ctx.top && !L.clip && !L.rot && !L.scale && !L.at && !L.grid && !L.sym && !L.mirror;
      if (plain && !(ctx.copy[0] === 0 && ctx.copy[1] === 0)) { g.restore(); continue; }
      const img = fieldImage(L, P, tile, ctx.px[0], ctx.px[1], pal);
      if (plain) { g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(img, 0, 0); }
      else {
        g.scale(1, -1);                                                        // (the image's rows run down)
        g.drawImage(img, -tile[0] / 2, -tile[1] / 2, tile[0], tile[1]);
      }
    } else {
      const path = shapePath(L, P, tile);
      if (L.fill !== undefined && !openShape(L)) { g.fillStyle = tone(L.fill); g.fill(path, L.rule ?? (L.shape === "ring" || L.shape === "frame" ? "evenodd" : "nonzero")); }
      if (L.stroke !== undefined || openShape(L)) {
        g.strokeStyle = tone(L.stroke ?? L.fill ?? 0); g.lineWidth = lw; g.lineJoin = "round"; g.lineCap = L.cap ?? "butt";
        g.stroke(path);
      }
    }
    g.restore();
  }
}

// LAYERS DRAWN INTO A GIVEN FRAME, outside any tile -- for a module that draws pictures with this language (glyphs.js:
// a hieroglyph is a list of these layers): `g` already set to the units the layers are written in (y up); colours as
// "#rrggbb" (or slots of `palette`, a list); `tile` what band shapes span; `ppm` texels per unit (a used pattern's)
export function drawShapes(g, layers, { params = {}, palette = [], tile = [1, 1], ppm = 100 } = {}) {
  drawLayers(g, layers, { P: params, pal: palette.map((c) => (typeof c === "string" ? hex(c) : c)), tile, px: [Math.round(tile[0] * ppm), Math.round(tile[1] * ppm)], ppm, depth: 0, top: false, copy: [0, 0] });
}

// a pattern's tile in metres, its params resolved
export function sizeOf(def, params = {}) {
  const P = { ...(def.params ?? {}), ...params };
  return pairOf(def.size, P, [1, 1]);
}

// THE TILE: the pattern drawn into a canvas `px` texels across -- every layer at the tile and its eight neighbours when
// it repeats, so the tile's edges carry whatever crosses them and it repeats without a seam
function drawTile(def, { pal, px, params = {}, depth = 0 }) {
  if (depth > 6) throw new Error("patterns use each other too deep (a pattern using itself?)");
  const P0 = { ...(def.params ?? {}), ...params }, tile = pairOf(def.size, P0, [1, 1]);
  const P = new Proxy(P0, { get: (o, k) => (k === "W" ? tile[0] : k === "H" ? tile[1] : o[k]), has: (o, k) => k === "W" || k === "H" || k in o });
  const [W, H] = px, cv = mkCanvas(W, H), g = cv.getContext("2d");
  g.fillStyle = css(colorOf(def.ground ?? 0, pal)); g.fillRect(0, 0, W, H);
  g.setTransform(W / tile[0], 0, 0, -H / tile[1], W / 2, H / 2);            // metres, centred, y up
  const ctx = { P, pal, tile, px, ppm: W / tile[0], depth };
  const offs = def.repeat === false ? [[0, 0]] : [-1, 0, 1].flatMap((i) => [-1, 0, 1].map((j) => [i * tile[0], j * tile[1]]));
  for (const [ox, oy] of offs) { g.save(); g.translate(ox, oy); drawLayers(g, def.layers, { ...ctx, top: true, copy: [ox, oy] }); g.restore(); }
  return cv;
}

// A TILE FOR USE: { canvas, size (metres), px, repeat }. `res`: texels across the tile's longer side (the pattern's own
// `res`, else 512), rounded to keep its texels square
export function renderPattern(ref, { palette, params = {}, res } = {}) {
  const def = patternOf(ref);
  if (!def) throw new Error(`no pattern "${ref}"`);
  const size = sizeOf(def, params), R = res ?? def.res ?? 512, long = Math.max(size[0], size[1]);
  const px = [Math.max(8, Math.round(R * size[0] / long)), Math.max(8, Math.round(R * size[1] / long))];
  const canvas = drawTile(def, { pal: paletteOf(def, palette), px, params });
  return { canvas, size, px, repeat: def.repeat !== false };
}

// a sampler for a rendered tile (the headless check renders with it): (u, v) metres -> [r, g, b]
export function tileSampler(tile) {
  const { canvas, size, px, repeat } = tile, d = canvas.getContext("2d").getImageData(0, 0, px[0], px[1]).data;
  return {
    sample(u, v) {
      let x = u / size[0] + .5, y = v / size[1] + .5;
      if (repeat) { x -= Math.floor(x); y -= Math.floor(y); } else { x = Math.min(1, Math.max(0, x)); y = Math.min(1, Math.max(0, y)); }
      const i = (Math.min(px[1] - 1, Math.floor((1 - y) * px[1])) * px[0] + Math.min(px[0] - 1, Math.floor(x * px[0]))) * 4;
      return [d[i], d[i + 1], d[i + 2]];
    },
  };
}

// ---- a sheet: every pattern of a family, in each of its palettes -------------------------------------------------------
// (the asset viewer shows a family so; the check harness renders it) -- each pattern a swatch of `span` metres (enough
// for two repeats, or the whole of a panel) and a strip of its other colourings under it
export function drawSheet(cv, family, { cell = 220, small = 70, only = null } = {}) {
  if (family.palettes && !family.patterns) return drawPalettes(cv, family);
  const pats = Object.entries(family.patterns ?? {}).filter(([k]) => !only || k === only);
  const cols = Math.max(1, Math.floor((cv.width - 10) / (cell + 14)));
  const rowH = cell + small + 40, rows = Math.ceil(pats.length / cols);
  cv.height = Math.max(cv.height, rows * rowH + 10);
  const g = cv.getContext("2d", { willReadFrequently: true });   // (a software canvas: a GPU one can be lost, and blanked, while WebGPU starts)
  g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height);
  g.font = "12px ui-monospace, monospace";
  const errors = [];
  pats.forEach(([name, def], i) => {
    const x = 10 + (i % cols) * (cell + 14), y = 10 + Math.floor(i / cols) * rowH;
    // (a panel is drawn whole; a repeating tile as a true repeat -- a canvas pattern -- two tiles across)
    const swatch = (pal, px, X, Y) => {
      const t = renderPattern(def, { palette: pal, res: def.repeat === false ? px : Math.max(64, Math.min(1024, Math.round(px / 2))) });
      if (def.repeat === false) { g.drawImage(t.canvas, X, Y, px, px * t.size[1] / t.size[0]); return t; }
      const f = g.createPattern(t.canvas, "repeat"), k = px / 2 / t.px[0];
      f.setTransform(new DOMMatrix([k, 0, 0, k, X, Y]));
      g.fillStyle = f; g.fillRect(X, Y, px, px);
      return t;
    };
    try {
      g.save(); g.beginPath(); g.rect(x, y, cell, cell); g.clip();
      const t = swatch(undefined, cell, x, y);
      g.restore();
      g.fillStyle = "#d8d4cc"; g.fillText(name, x, y + cell + 14);
      g.fillStyle = "#8d8a84"; g.fillText(`${t.size[0]} x ${t.size[1]} m`, x + cell - 90, y + cell + 14);
      (def.palettes ?? []).slice(0, 3).forEach((pal, k) => {
        g.save(); g.beginPath(); g.rect(x + k * (small + 5), y + cell + 20, small, small); g.clip();
        swatch(pal, small, x + k * (small + 5), y + cell + 20);
        g.restore();
      });
    } catch (e) { g.restore?.(); errors.push(`${name}: ${e.message}`); g.fillStyle = "#e27a6a"; g.fillText(`${name}: ${e.message}`.slice(0, 40), x, y + 20); }
  });
  return errors;
}

// the palettes document: each palette a strip of its slots, numbered
function drawPalettes(cv, doc) {
  const list = Object.entries(doc.palettes), cols = 2, colW = (cv.width - 30) / cols, rowH = 34;
  cv.height = Math.max(cv.height, Math.ceil(list.length / cols) * rowH + 20);
  const g = cv.getContext("2d", { willReadFrequently: true });   // (a software canvas: a GPU one can be lost, and blanked, while WebGPU starts)
  g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height);
  g.font = "12px ui-monospace, monospace";
  list.forEach(([name, cs], i) => {
    const x = 10 + (i % cols) * (colW + 10), y = 10 + Math.floor(i / cols) * rowH;
    g.fillStyle = "#d8d4cc"; g.fillText(name, x, y + 16);
    const sw = Math.min(34, (colW - 130) / cs.length);
    cs.forEach((c, k) => {
      g.fillStyle = c; g.fillRect(x + 120 + k * sw, y, sw - 2, 24);
      g.fillStyle = "rgba(0,0,0,.45)"; g.fillText(String(k), x + 122 + k * sw, y + 20);
    });
  });
  return [];
}
