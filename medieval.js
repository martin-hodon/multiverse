// A MEDIEVAL FIGURE as a pattern layer { kind: "figure", h: metres tall, figure: { pose, robe, ... }, at, seed } (medieval/figure.js), feet on its
// `at`. For a drawing laid over, such as a mosaic: flat colours and solid lines only, since what's faint would turn to stray stones.
import { LAYER_KINDS } from "./patterns.js";
import { buildFigure, placed } from "./medieval/figure.js";
import { stream } from "./greek/rig.js";

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
