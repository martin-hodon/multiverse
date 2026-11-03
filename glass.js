// STAINED GLASS (docs/glass.md): a window as a pattern layer { kind: "glass", form, ... }, drawn once over the whole tile, out of
// PIECES (glass/forms.js, glass/layout.js) cut into PANES (glass/panes.js) and painted (glass/stain.js). It holds nothing but
// the layer; the family is assets/patterns/glass.json.
import { LAYER_KINDS } from "./patterns.js";
import { openingOf, ringPieces, circle } from "./glass/forms.js";
import { partition } from "./glass/panes.js";
import { paintPanes } from "./glass/stain.js";
import { panelsOf, stonePanels, ringBusts } from "./glass/layout.js";
import { planRings } from "./glass/window.js";
import { stream } from "./story/seed.js";

// a form's panels: [{ pieces, clip }]. A panel is what's cut as one, which is how a window's kept cheap
function panels(L0, tile, clipAll) {
  const L = L0.form === "rose" && L0.plan ? planRings(L0) : L0, R = Math.min(clipAll.reduce((a, p) => Math.max(a, Math.abs(p[0])), 0), clipAll.reduce((a, p) => Math.max(a, Math.abs(p[1])), 0));
  if (L.form === "rose") return [{ clip: clipAll, pieces: [{ pts: circle([0, 0], R * 1.01, 96), fill: L.ground ?? 0, role: "ground", label: "ground" }, ...ringPieces(L.rings ?? [], R), ...(L.busts ? ringBusts(L, R) : [])] }];
  if (L.form === "stone") return stonePanels(L, clipAll, R);
  return panelsOf(L, tile, clipAll);
}

const done = new Map(), KEEP = 8, STATS = new WeakMap();
export const lab = { keep: false, fresh: false };                     // (the bench's: keep what a window was cut into, draw afresh past the cache)
// (`lie`: the game's tile array only runs sideways, over `across` layers, so a tall window is drawn upright and kept on its side -- up to the left -- at a tile as long as it's high. arch/finish.js turns it back by the rule's turn: 90)
function layDown(cv, [w, h]) {
  const out = new OffscreenCanvas(w, h), g = out.getContext("2d", { willReadFrequently: true });
  g.imageSmoothingEnabled = false; g.translate(0, h); g.rotate(-Math.PI / 2); g.drawImage(cv, 0, 0);
  return out;
}
export function renderGlass(L, { tile, px, pal }) {
  const key = JSON.stringify([L, tile, px, pal]), kept = lab.fresh ? null : done.get(key);
  if (kept) { STATS.set(L, kept.stats); return kept.cv; }
  if (L.plan || L.theme) { const r = stream(L.seed ?? 1, "tune"), warm = (r() - .5) * .1, sat = 1 + (r() - .5) * .22, lit = 1 + (r() - .5) * .14; pal = pal.map(([a, b, c]) => { const m = (a + b + c) / 3, f = (v) => Math.max(0, Math.min(255, (m + (v - m) * sat) * lit)); return [f(a) * (1 + warm), f(b), f(c) * (1 - warm)]; }); }   // (each seed its own batch from the glasshouse, still that palette)
  const lying = px; if (L.lie) { tile = [tile[1], tile[0]]; px = [px[1], px[0]]; }
  const t0 = performance.now(), clipAll = openingOf(L, tile), P = panels(L, tile, clipAll), bars = P.bars ?? [], results = P.map(({ pieces, clip }) => partition(pieces, { clip, minArea: L.minPane ?? 0, cut: { depth: L.depth ?? .25, maxArea: L.maxPane ?? Infinity, maxAspect: L.maxAspect ?? 4 } }));
  const t1 = performance.now(), up = paintPanes(results, { tile, px, pal, L: { ...L, clipAll, bars: L.ironBars === false ? null : { h: bars } } }), cv = L.lie ? layDown(up, lying) : up, sum = {};
  for (const R of results) for (const [k, v] of Object.entries(R.metrics)) sum[k] = (sum[k] ?? 0) + v;
  let want = 0; clipAll.forEach((p, i) => { const q = clipAll[(i + 1) % clipAll.length]; want += (p[0] * q[1] - q[0] * p[1]) / 2; });
  const stats = { ...sum, gap: +Math.abs(1 - sum.area / want).toFixed(4), msCut: Math.round(t1 - t0), msPaint: Math.round(performance.now() - t1), ...(lab.keep ? { results } : {}) };
  STATS.set(L, stats); done.set(key, { cv, stats }); if (done.size > KEEP) done.delete(done.keys().next().value);
  return cv;
}
export const measures = (L) => STATS.get(L);

LAYER_KINDS.glass = {
  draw(g, L, { pal, tile, px, copy }) {
    if (copy && (copy[0] || copy[1])) return;
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.drawImage(renderGlass(L, { tile, px, pal }), 0, 0);
  },
};
