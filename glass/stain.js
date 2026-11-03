// THE GLASS AS PAINT (docs/glass.md): panes filled, each its own sheet (a colour a little its own, and uneven through its thickness),
// what's painted on them, the leads, the bars and the rim; outside the opening a flat colour. What it writes is what light comes
// through: arch materials do the lighting. Deterministic.
import { stream } from "../story/seed.js";

const mk = (w, h) => typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(w, h) : Object.assign(document.createElement("canvas"), { width: w, height: h });
const css = (c) => `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;
const hex = (c) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));

// a value noise that wraps, two octaves: thick and thin in the sheet, a streak along one way
function sheetNoise(W, H, seed, cells) {
  const r = stream(seed, "sheet"), make = (nx, ny) => { const v = new Float32Array(nx * ny); for (let i = 0; i < v.length; i++) v[i] = r(); return { v, nx, ny }; };
  const a = make(cells, Math.max(2, Math.round(cells * .7 + 2))), b = make(cells * 4, Math.max(4, Math.round(cells * 4 * .7))), out = new Float32Array(W * H);
  const smp = ({ v, nx, ny }, x, y) => { const X = x * nx, Y = y * ny, i = Math.floor(X), j = Math.floor(Y), u = X - i, w = Y - j, s = u * u * (3 - 2 * u), t = w * w * (3 - 2 * w); const g = (p, q) => v[(q % ny) * nx + p % nx]; return (g(i, j) * (1 - s) + g(i + 1, j) * s) * (1 - t) + (g(i, j + 1) * (1 - s) + g(i + 1, j + 1) * s) * t; };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) out[y * W + x] = smp(a, x / W, y / H) * .65 + smp(b, x / W, y / H) * .35 - .5;
  return out;
}

export function paintPanes(results, { tile, px, pal, L }) {
  const [W, H] = px, ppm = W / tile[0], cv = mk(W, H), g = cv.getContext("2d", { willReadFrequently: true }), seed = L.seed ?? 1, X = (x) => (x + tile[0] / 2) * ppm, Y = (y) => (tile[1] / 2 - y) * ppm;
  const trace = (ctx, pts, close = true) => { ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); if (close) ctx.closePath(); };
  const outside = "#14110e", leadC = L.leadColor ?? "#100e0c";
  g.fillStyle = outside; g.fillRect(0, 0, W, H);
  const rj = stream(seed, "sheets"), vary = .12;
  // each pane as cut. (The stroke closes the antialiased cracks between neighbours: lead will cover it.)
  g.lineWidth = 1; g.lineJoin = "round";
  for (const R of results) { const sheets = new Map(); for (const p of R.panes) {
    const c = pal[((p.fill % pal.length) + pal.length) % pal.length], drawn = [1 + (rj() - .5) * 2 * vary, (rj() - .5) * vary * .5];
    // (`sheet`: pieces of one quarry or block, cut by the tile's end, are one sheet)
    if (p.sheet !== undefined && !sheets.has(p.sheet)) sheets.set(p.sheet, drawn);
    const [k, warm] = sheets.get(p.sheet) ?? drawn, col = css([c[0] * k * (1 + warm), c[1] * k, c[2] * k * (1 - warm)]);
    g.fillStyle = g.strokeStyle = col; trace(g, p.pts); g.fill(); g.stroke();
  } }
  // the sheet's unevenness, over everything that's glass
  {
    const img = g.getImageData(0, 0, W, H), d = img.data, n = sheetNoise(W, H, seed, 7), m = .3, o = hex(outside);
    for (let i = 0, q = 0; i < n.length; i++, q += 4) { if (d[q] === o[0] && d[q + 1] === o[1] && d[q + 2] === o[2]) continue; const k = 1 + n[i] * m * 2; d[q] *= k; d[q + 1] *= k; d[q + 2] *= k; }
    g.putImageData(img, 0, 0);
  }
  // paint: each piece's lines, hidden by the pieces over it (so a sleeve's fold doesn't run on across what's in front)
  const paint = mk(W, H), q = paint.getContext("2d");
  let any = false;
  for (const R of results) {
    q.save(); if (R.clip) { trace(q, R.clip); q.clip(); }
    for (const P of R.pieces) {
      if (!P.paint && !any) continue;
      if (P.within) { q.save(); trace(q, P.within); q.clip(); }
      q.globalCompositeOperation = "destination-out"; q.fillStyle = "#000"; trace(q, P.pts); q.fill(); q.globalCompositeOperation = "source-over";
      if (!P.paint) { if (P.within) q.restore(); continue; }
      any = true;
      q.save(); trace(q, P.pts); q.clip();
      for (const s of P.paint) {
        if (s.fill !== undefined) { q.fillStyle = s.fill; q.globalAlpha = s.alpha ?? 1; trace(q, s.pts); q.fill(); q.globalAlpha = 1; continue; }
        q.strokeStyle = s.c ?? (L.paintColor ?? "#1d120b"); q.globalAlpha = s.alpha ?? 1; q.lineWidth = Math.max(.7, (s.w ?? .006) * ppm); q.lineCap = q.lineJoin = "round"; trace(q, s.pts, !!s.closed); q.stroke(); q.globalAlpha = 1;
      }
      q.restore();
      if (P.within) q.restore();
    }
    q.restore();
  }
  if (any) g.drawImage(paint, 0, 0);
  // the corrosion and shadow beside the leads, the leads
  const lead = (L.lead ?? .012) * ppm, line = (segs, w, style, alpha = 1) => { g.strokeStyle = style; g.globalAlpha = alpha; g.lineWidth = w; g.lineCap = "round"; g.lineJoin = "round"; g.beginPath(); for (const [a, b] of segs) { g.moveTo(X(a[0]), Y(a[1])); g.lineTo(X(b[0]), Y(b[1])); } g.stroke(); g.globalAlpha = 1; };
  for (const R of results) { line(R.leads, lead * 2.4, "#000", .16); line(R.leads, lead * 1.6, "#000", .22); }
  for (const R of results) line(R.leads, lead, leadC);
  // the iron, and the rim
  const clipAll = L.clipAll;
  if (L.bars) {
    g.save(); if (clipAll) { trace(g, clipAll); g.clip(); }
    g.strokeStyle = leadC; g.lineWidth = (L.bars.w ?? (L.lead ?? .012) * 1.8) * ppm;
    for (const y of L.bars.h ?? []) { g.beginPath(); g.moveTo(X(-tile[0]), Y(y)); g.lineTo(X(tile[0]), Y(y)); g.stroke(); }
    g.restore();
  }
  if (clipAll && L.rim !== 0) { g.strokeStyle = leadC; g.lineWidth = (L.rim ?? (L.lead ?? .012) * 2) * ppm; trace(g, clipAll); g.stroke(); }
  return cv;
}
