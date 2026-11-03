// MOSAIC (docs/mosaic.md): tesserae as a technique over any drawing, a pattern layer { kind: "mosaic", layers: [what's drawn], stone, ... }.
// The layers are drawn at twice the tile's texels and read as regions of the palette's stones (mosaic/source.js), stones are
// laid over them (mosaic/lay.js), and coloured (mosaic/paint.js). It replaces the whole tile, drawn once. It reaches no
// further than `layers` for anything: a Greek painting, an ornament, a shape.
import { LAYER_KINDS } from "./patterns.js";
import { sourceOf, segment } from "./mosaic/source.js";
import { layStones } from "./mosaic/lay.js";
import { colourStones, paintStones } from "./mosaic/paint.js";
import { planned } from "./mosaic/floor.js";

const mk = (w, h) => typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(w, h) : Object.assign(document.createElement("canvas"), { width: w, height: h });
const rgbOf = (c, pal) => typeof c === "string" ? [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16)) : pal[((Math.round(c) % pal.length) + pal.length) % pal.length];

const done = new Map(), KEEP = 8, STATS = new WeakMap();
export const lab = { keep: false, fresh: false };   // (the lab keeps each drawing, to compare, and can draw past the cache; nothing else should hold four megabytes for it)
// the whole tile, as a canvas: `grid` texels of the map to one of the tile's
export function renderMosaic(L0, { tile, px, pal: pal0, repeat }) {
  const key = JSON.stringify([L0, tile, px, pal0, repeat]), kept = lab.fresh ? null : done.get(key);
  if (kept) { STATS.set(L0, kept.stats); return kept.cv; }
  const [L, pal] = planned(L0, tile, pal0);                             // (a plan, a seed's: what's to be drawn, decided before the stones)
  // (a tile of two layers is twice the texels of any other: its map 1.5 times the tile's, not twice, its stones as large and its joints as much of a texel lighter. Most of what's slow in a mosaic goes with the map's area)
  const t0 = performance.now(), scale = px[0] * px[1] > 5e5 ? 1.5 : 2, src = sourceOf(L, { tile, px, pal, repeat, scale }), t1 = performance.now();
  const ppm = src.W / tile[0], map = segment(src, pal, repeat, ((L.stone ?? .012) * ppm * (L.dust ?? .45)) ** 2), t2 = performance.now();
  const layout = layStones(map, L, ppm), t3 = performance.now();
  const grout = rgbOf(L.groutColor ?? "#3a352e", pal), colours = colourStones(layout, map, pal, grout, L);
  const img = paintStones(layout, colours, grout, px, scale / 2), cv = mk(px[0], px[1]);
  cv.getContext("2d", { willReadFrequently: true }).putImageData(new ImageData(img.rgba, img.W, img.H), 0, 0);
  const st = layout.stones, S = layout.W * layout.H, live = new Uint8Array(st.x.length); let open = 0;
  for (let i = 0; i < S; i++) { live[layout.cover[i] - 1] = 1; if (layout.mortar[i]) open++; }
  STATS.set(L0, { stones: live.reduce((a, b) => a + b, 0), regions: map.count, pitchPx: +(layout.pitch / scale * Math.min(1, ...Object.values(L.fine ?? {}))).toFixed(2), kinds: st.kind.reduce((a, k) => { a[k] = (a[k] ?? 0) + 1; return a; }, {}), grout: +(open / S * scale / 2).toFixed(3), msSource: Math.round(t1 - t0), msMap: Math.round(t2 - t1), msLay: Math.round(t3 - t2), msPaint: Math.round(performance.now() - t3), source: lab.keep ? src : null });
  done.set(key, { cv, stats: STATS.get(L0) }); if (done.size > KEEP) done.delete(done.keys().next().value);
  return cv;
}
// what a lab reads: the last laying's numbers, and the drawing it was laid over
export const measures = (L) => STATS.get(L);

LAYER_KINDS.mosaic = {
  draw(g, L, { pal, tile, px, copy, repeat }) {
    if (copy && (copy[0] || copy[1])) return;
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.drawImage(renderMosaic(L, { tile, px, pal, repeat: repeat !== false }), 0, 0);
  },
};
