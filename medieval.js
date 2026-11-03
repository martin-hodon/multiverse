// A MEDIEVAL FIGURE as a pattern layer { kind: "figure", h: metres tall, figure: { pose, robe, ... }, at, seed } (medieval/figure.js), feet on its
// `at`. For a drawing laid over, such as a mosaic: flat colours and solid lines only, since what's faint would turn to stray stones.
import { LAYER_KINDS } from "./patterns.js";
import { buildFigure, placed } from "./medieval/figure.js";
import { stream } from "./greek/rig.js";
import { composeScene, personPieces, dyeOf } from "./story/compose.js";

const FAINT = .5;
LAYER_KINDS.figure = {
  draw(g, L, { pal }) {
    const css = (c) => typeof c === "string" ? c : `rgb(${pal[c].join(",")})`, line = L.line ?? 0, ink = css(L.ink ?? 6);
    const trace = (pts, closed) => { g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); if (closed) g.closePath(); };
    g.lineCap = g.lineJoin = "round";
    for (const p of placed(buildFigure(L.figure, stream(L.seed ?? 1, "fig", 0)), L.h / 100, 0, 0)) {
      trace(p.pts, true); g.fillStyle = css(p.fill); g.fill();
      for (const q of p.paint ?? []) {
        if ((q.alpha ?? 1) < FAINT) continue;
        trace(q.pts, q.closed || q.fill !== undefined);
        if (q.fill !== undefined) { g.fillStyle = ink; g.fill(); }
        else { g.strokeStyle = ink; g.lineWidth = Math.max(q.w ?? 0, line); g.stroke(); }
      }
    }
  },
};

// A SCENE OF THE CANON, drawn flat for what's laid over it: { kind: "story", scene | person, seed, frame: { x0, x1, y0, y1 }, dye: { name: slot }, ground, ink, line, stone, wear, within }. Every piece has its ink, as a row of dark stones goes round a figure on a floor
LAYER_KINDS.story = {
  draw(g, L, { pal, copy }) {
    if (copy && (copy[0] || copy[1])) return;                           // (a scene stays inside its tile)
    const css = (c) => typeof c === "string" ? c : `rgb(${pal[c].join(",")})`, F = L.frame, dye = dyeOf(L.dye), ink = css(L.ink ?? 6), line = L.line ?? .01, stones = 1 / (L.stone ?? .012);
    let pieces;
    if (L.person) { // (one person, fitted to the frame)
      const P = personPieces(L.person, { seed: L.seed ?? 1, dye, ground: L.ground, wear: L.wear, coarse: (F.y1 - F.y0) * stones < 90, label: "p" });
      let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity; for (const p of P) for (const [x, y] of p.pts) { if (x < a) a = x; if (x > c) c = x; if (y < b) b = y; if (y > d) d = y; }
      const s = Math.min((F.x1 - F.x0) / (c - a), (F.y1 - F.y0) / (d - b)), ox = (F.x0 + F.x1) / 2 - s * (a + c) / 2, oy = F.y0 - s * b, m = ([x, y]) => [ox + s * x, oy + s * y];
      pieces = P.map((p) => ({ ...p, pts: p.pts.map(m), paint: p.paint?.map((q) => ({ ...q, w: (q.w ?? 0) * s, pts: q.pts.map(m) })) }));
    } else pieces = composeScene(L.scene, { seed: L.seed ?? 1, dye, ground: L.ground, frame: F, pxPerUnit: stones, float: L.float ?? .45 }).pieces;
    const trace = (pts, closed) => { g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); if (closed) g.closePath(); };
    const pad = (F.x1 - F.x0) * .05, room = [[F.x0 - pad, F.y0 - pad], [F.x1 + pad, F.y0 - pad], [F.x1 + pad, F.y1 + pad], [F.x0 - pad, F.y1 + pad]];   // (a scene's ground goes no further than its picture)
    g.save(); trace(L.within ?? room, true); g.clip();
    g.lineCap = g.lineJoin = "round";
    for (const p of pieces) {
      trace(p.pts, true); g.fillStyle = css(p.fill); g.fill(); if (!p.stars) { g.strokeStyle = ink; g.lineWidth = line * .8; g.stroke(); }
      if (p.within) { g.save(); trace(p.within, true); g.clip(); }
      for (const q of p.paint ?? []) {
        if ((q.alpha ?? 1) < FAINT) continue;
        trace(q.pts, q.closed || q.fill !== undefined);
        if (q.fill !== undefined || q.w === undefined) { g.fillStyle = q.c ?? ink; g.fill(); }
        else { g.strokeStyle = ink; g.lineWidth = Math.max(q.w, line * .7); g.stroke(); }
      }
      if (p.within) g.restore();
    }
    g.restore();
  },
};
