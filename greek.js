// GREEK PAINTINGS (docs/greek.md): vase and wall painting, drawn from parameters -- rig (greek/rig.js: a body solved from an
// action), figure and clothes (greek/figure.js, drape.js: pieces), scene (greek/scene.js: bodies placed and aimed at each
// other), field (greek/field.js: a painting as a stack of zones), techniques (greek/paint.js). Data: assets/greek/canon.json
// (tools/greekgen.py). Here: its place among the patterns, a layer { kind: "greek", painting, seed }.
import { LAYER_KINDS } from "./patterns.js";
import { renderPainting } from "./greek/field.js";
import { TECHNIQUES } from "./greek/paint.js";

let DATA = null;
const cache = new Map(), MAX = 8;       // (the last few only: a painted tile keeps what it drew)
export function registerGreek(docs) {
  for (const d of Object.values(docs)) if (d?.canon && d?.paintings) DATA = d;
  cache.clear();
}
export const greekData = () => DATA;
export function renderGreek(ref, opts) {
  const spec = typeof ref === "string" ? DATA?.paintings[ref] : ref;
  if (!spec) throw new Error(`no Greek painting "${ref}"`);
  return renderPainting(DATA, spec, opts);
}

// the viewer's sheet: each painting by a few seeds
export function drawGreekSheet(cv, doc, { seeds = 3 } = {}) {
  const g = cv.getContext("2d"), errs = [], list = Object.entries(doc.paintings ?? {});
  const px = Math.floor((cv.width - 10) / seeds) - 8, rows = [];
  for (const [k, P] of list) { const row = []; for (let s = 1; s <= seeds; s++) { try { row.push(renderPainting(doc, P, { px, seed: s })); } catch (e) { errs.push(`${k}: ${e.message}`); } } rows.push([P.name ?? k, row]); }
  cv.height = rows.reduce((a, [, r]) => a + (r[0]?.height ?? 0) + 26, 10);
  g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height);
  g.font = "12px ui-monospace, monospace";
  let y = 6;
  for (const [t, r] of rows) { g.fillStyle = "#d8d4cc"; g.fillText(t, 8, y + 12); r.forEach((c, i) => g.drawImage(c, 6 + i * (px + 8), y + 18)); y += (r[0]?.height ?? 0) + 26; }
  return errs;
}

// ---- on a surface: the painting over the tile (or `box`, metres, where the layer stands), by its own width in pixels
LAYER_KINDS.greek = {
  draw(g, L, { tile, ppm }) {
    const [w, h] = L.box ?? tile, px = Math.max(16, Math.round(w * ppm)), key = `${L.painting}|${px}|${L.seed ?? 1}`;
    let cv = cache.get(key);
    if (!cv) { cv = renderGreek(L.painting, { px, seed: L.seed ?? 1 }); cache.set(key, cv); if (cache.size > MAX) cache.delete(cache.keys().next().value); }
    g.save(); g.scale(1, -1); g.drawImage(cv, -w / 2, -h / 2, w, h); g.restore();
  },
  deps: (L) => ({ painting: L.painting, seed: L.seed ?? 1, spec: DATA?.paintings[L.painting] ?? null, canon: DATA?.canon ?? null, actions: DATA?.actions ?? null, scenes: DATA?.scenes ?? null, cast: DATA?.cast ?? null, legs: DATA?.legs ?? null, beats: DATA?.beats ?? null, styles: DATA?.styles ?? null, techniques: TECHNIQUES, parts: DATA?.parts ?? null, dress: DATA?.dress ?? null }),
};
