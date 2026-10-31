// ORNAMENT (docs/ornament.md): geometric ornament as layers of the pattern language. `stars`: Islamic star patterns and
// girih, from polygons in contact (ornament/stars.js). `knot`: Celtic and Viking knots, guilloche, braids (ornament/knot.js).
// Both are strands over a net, woven by ornament/weave.js. `scroll`: the arabesque vine (ornament/scroll.js), alone or inside
// a star. Nothing here needs data: a layer says everything.
//   Such a layer draws its own copies, once, for the tile: drawn nine times over by the tile's loop, a neighbour's whole
// strand would land on this tile's crossings. Rather than pieces of a strand, it's all or nothing.
import { LAYER_KINDS } from "./patterns.js";
import { evalNum } from "./expr.js";
import { starNet, cellOf } from "./ornament/stars.js";
import { knotNet } from "./ornament/knot.js";
import { weaveOf, piecesOf, pathsOf, strokeBand, smooth } from "./ornament/weave.js";
import { latticeOf } from "./ornament/net.js";
import { scrollPaths, motifPaths } from "./ornament/scroll.js";

export { cellOf };
const hash = (...k) => { let h = 2166136261; for (const v of k) { h = Math.imul(h ^ (v | 0), 16777619); h ^= h >>> 13; } return ((h >>> 0) % 100003) / 100003; };
const hexOf = (c, pal) => {
  const [r, g, b] = typeof c === "string" ? [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16)) : pal[((Math.round(c) % pal.length) + pal.length) % pal.length];
  return [r, g, b];
};
const cssOf = ([r, g, b]) => `rgb(${r | 0},${g | 0},${b | 0})`;
const shade = (c, s) => s >= 0 ? c.map((v) => v + (255 - v) * s) : c.map((v) => v * (1 + s));

// the layer's numbers may be expressions, as anywhere in the language
const numbered = (L, P) => Object.fromEntries(Object.entries(L).map(([k, v]) => [k, typeof v === "string" && v[0] !== "#" && !["kind", "symmetry", "wrap", "join", "curve"].includes(k) ? evalNum(v, P) : v]));
const nets = new Map();
const cached = (key, make) => { let v = nets.get(key); if (!v) { v = make(); nets.set(key, v); if (nets.size > 24) nets.delete(nets.keys().next().value); } return v; };

// what a pattern's checks read: the net's own count of what went wrong
export const measures = (L, tile) => {
  if (L.kind === "scroll") return {};
  if (L.kind === "stars") {
    const s = starNet(L), w = weaveOf(s.strands, (n) => s.net.nodes[n].out.length === 4);
    return { strands: s.strands.length, faces: s.faces.length, classes: s.classes, loose: s.loose, ends: s.net.ends, crowded: s.net.crowded, conflicts: w.conflicts, areaOff: +s.areaOff.toFixed(3), aspect: +(s.W / s.H).toFixed(4) };
  }
  const k = knotNet(L, tile), w = weaveOf(k.strands, (n) => n >= 0);
  return { strands: k.strands.length, shortest: Math.min(...k.strands.map((s) => s.length)), breaks: k.breaks, conflicts: w.conflicts };
};

function paintVine(g, v, L, pal) {
  g.fillStyle = cssOf(hexOf(L.stem ?? 0, pal)); g.fill(v.stem);
  g.fillStyle = cssOf(hexOf(L.leafColor ?? L.stem ?? 0, pal)); g.fill(v.leaf);
  g.fillStyle = cssOf(hexOf(L.flower ?? 3, pal)); g.fill(v.flower);
  g.fillStyle = cssOf(hexOf(L.heart ?? 0, pal)); g.fill(v.heart);
}

LAYER_KINDS.stars = {
  draw(g, L0, { P, pal, tile, copy }) {
    if (copy && (copy[0] || copy[1])) return;
    const L = numbered(L0, P), cells = L.cells ?? [1, 1], key = JSON.stringify(["s", L.n, L.k, L.gap, L.angle, L.gapAngle, L.delta, L.depth]);
    const s = cached(key, () => {
      const q = starNet(L);
      return { ...q, woven: weaveOf(q.strands, (n) => q.net.nodes[n].out.length === 4) };
    });
    // the frame: an edge of 1 becomes metres, the cell into the tile
    const scale = tile[0] / (cells[0] * s.W);
    g.save(); g.scale(scale, scale);
    const offs = [];
    for (let i = -1; i <= cells[0]; i++) for (let j = -1; j <= cells[1]; j++) offs.push([(i - (cells[0] - 1) / 2) * s.W, (j - (cells[1] - 1) / 2) * s.H]);
    // the pieces
    const fills = L.fills ?? [1, 2, 3, 4], vary = L.vary ?? 0;
    for (const f of s.faces) {
      const pick = fills[f.rank % fills.length], slot = Array.isArray(pick) ? pick[f.who % pick.length] : pick;
      if (slot === null) continue;
      const p = new Path2D();
      f.pts.forEach((q, i) => (i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1]))); p.closePath();
      const base = hexOf(slot, pal);
      // (each piece its own tone, the same in every copy: the tile repeats)
      g.fillStyle = cssOf(vary ? shade(base, vary * (2 * hash(Math.round(f.c[0] * 97), Math.round(f.c[1] * 97), L.seed ?? 1) - 1)) : base);
      for (const [x, y] of offs) { g.save(); g.translate(x, y); g.fill(p); g.restore(); }
      // an inlay: the vine inside the star, turned by its own symmetry, in the frame's units
      if (L.inlay && L.inlay.ranks.includes(f.rank)) {
        const r = Math.min(...f.pts.map((q) => Math.hypot(q[0] - f.c[0], q[1] - f.c[1]))) * (L.inlay.size ?? 1.25);
        const m = cached(JSON.stringify(["m", L.n, r, L.inlay]), () => motifPaths(L.n, r, L.inlay));
        for (const [x, y] of offs) {
          g.save(); g.translate(x, y); g.clip(p); g.translate(f.c[0], f.c[1]);
          paintVine(g, m, L.inlay, pal);
          g.restore();
        }
      }
    }
    // the strapwork
    const band = L.band ?? .08, edge = L.edge ?? 0;
    const wrap = (m) => { const q = s.lat.steps(m[0] + s.W / 2, m[1] + s.H / 2); return s.lat.at(q[0], q[1]); };
    const reach = (node) => {
      const o = s.net.nodes[node].out, phi = Math.abs(o[1].dir - o[0].dir), c = Math.abs(Math.cos(phi)), n = Math.max(.15, Math.abs(Math.sin(phi)));
      return (band / 2 + edge) * (1 + c) / n + edge;
    };
    const strap = hexOf(L.strap ?? 0, pal), rim = hexOf(L.strapEdge ?? 5, pal), core = L.core === undefined ? null : hexOf(L.core, pal);
    const style = { width: band, edgeWidth: edge, fill: cssOf(strap), edge: cssOf(rim), core: core && cssOf(core), coreWidth: L.coreWidth ?? 0 };
    if (L.weave === false) {
      const p = piecesOf(s.strands, { byStrand: s.strands.map(() => []) }, { wrap, reach, lap: 0 });
      strokeBand(g, pathsOf(p.whole), offs, style);
    } else {
      const p = piecesOf(s.strands, s.woven, { wrap, reach, lap: band * .02 });
      strokeBand(g, pathsOf(p.whole), offs, style);
      strokeBand(g, pathsOf(p.over), offs, style);
    }
    g.restore();
  },
};

LAYER_KINDS.knot = {
  draw(g, L0, { P, pal, tile, copy }) {
    if (copy && (copy[0] || copy[1])) return;
    const L = numbered(L0, P), key = JSON.stringify(["k", L.cols, L.rows, L.wrap, L.breaks, L.symmetry, L.seed, L.margin, L.tries, L.upright, L.bounce, L.walls, tile]);
    const k = cached(key, () => { const q = knotNet(L, tile); return { ...q, woven: weaveOf(q.strands, (n) => n >= 0) }; });
    const band = (L.band ?? .34) * k.u, edge = (L.edge ?? .05) * k.u, round = L.curve !== "straight";
    const lat = latticeOf([tile[0], 0], [0, tile[1]]);
    const wrap = (m) => {
      const q = lat.steps(m[0] + tile[0] / 2, m[1] + tile[1] / 2);
      return lat.at(k.wrapX ? q[0] : 0, k.wrapY ? q[1] : 0);
    };
    const offs = [];
    for (const i of k.wrapX ? [-1, 0, 1] : [0]) for (const j of k.wrapY ? [-1, 0, 1] : [0]) offs.push([i * tile[0], j * tile[1]]);
    const reach = () => band / 2 + 2 * edge + band * .3;
    const curve = round ? (st) => smooth(st, L.samples ?? 6) : null;
    const p = piecesOf(k.strands, k.woven, { curve, wrap, reach, lap: band * .02 });
    const style = { width: band, edgeWidth: edge, fill: cssOf(hexOf(L.strap ?? 1, pal)), edge: cssOf(hexOf(L.strapEdge ?? 5, pal)), core: L.core === undefined ? null : cssOf(hexOf(L.core, pal)), coreWidth: (L.coreWidth ?? 0) * k.u, join: round ? "round" : "miter" };
    strokeBand(g, pathsOf(p.whole), offs, style);
    strokeBand(g, pathsOf(p.over), offs, style);
    // an eye: a dot in the middle of a guilloche's every loop (the grid points that aren't nodes)
    if (L.eye !== undefined) {
      g.fillStyle = cssOf(hexOf(L.eye, pal));
      const r = (L.eyeSize ?? .28) * k.u;
      for (let i = 0; i <= k.W; i++) for (let j = 1; j < k.H; j++) if ((i + j) % 2 === 0 && (k.wrapX ? i < k.W : i > 0 && i < k.W)) {
        for (const [x, y] of offs) { g.beginPath(); g.arc((i - k.W / 2) * k.u + x, (j - k.H / 2) * k.u * k.squash + y, r, 0, Math.PI * 2); g.fill(); }
      }
    }
  },
};

// a vine that fills the tile: its stem is stroked, so it runs on across the tile's edge
LAYER_KINDS.scroll = {
  draw(g, L0, { P, pal, tile, copy }) {
    if (copy && (copy[0] || copy[1])) return;
    const L = numbered(L0, P);
    const v = cached(JSON.stringify(["v", L.cols, L.rows, L.width, L.leaf, L.turns, L.leaves, L.end, L.flowers, L.under, L.underThin, tile]), () => scrollPaths(L, tile));
    const each = (draw) => { for (const i of [-1, 0, 1]) for (const j of [-1, 0, 1]) { g.save(); g.translate(i * tile[0], j * tile[1]); draw(); g.restore(); } };
    const level = (q, style) => each(() => {
      g.strokeStyle = cssOf(hexOf(style.stem ?? 0, pal)); g.lineWidth = q.width; g.lineCap = "round"; g.lineJoin = "round";
      g.stroke(q.line);
      paintVine(g, q, style, pal);
    });
    if (v.under) level(v.under, { stem: L.under, flower: L.under, heart: L.under });
    level(v.top, L);
  },
};
