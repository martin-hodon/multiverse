// THE SHAPES OF A WINDOW (docs/glass.md): an opening's outline, and a rose as rings of shapes turned round a centre. All polygons
// in metres, y up, centred on the tile; the arcs fine enough for the tile's resolution and no finer.
import { roseLines } from "../arch/tracery.js";
const TAU = Math.PI * 2;

export const circle = (c, r, n = 48, turn = 0) => Array.from({ length: n }, (_, k) => { const t = turn + k * TAU / n; return [c[0] + r * Math.cos(t), c[1] + r * Math.sin(t)]; });
// a shape with k lobes, cusps between them: quatrefoil, trefoil
export const foil = (c, r, k, turn = 0, cusp = .32, n = 18) => Array.from({ length: k * n }, (_, i) => {
  const t = i * TAU / (k * n), a = Math.abs(Math.sin(k * t / 2)), R = r * (1 - cusp + cusp * Math.sqrt(a));
  return [c[0] + R * Math.cos(t + turn), c[1] + R * Math.sin(t + turn)];
});
// a pointed head on a straight-sided light, w wide and h tall: from the foot up, round, and back
export function lancet(cx, y0, w, h, { point = 1, n = 12 } = {}) {
  const a = w / 2, r = a * 2 * point, head = Math.min(h, Math.sqrt(r * r - (r - a) ** 2)), ys = y0 + h - head, pts = [[cx - a, y0], [cx + a, y0]];
  for (let k = 0; k <= n; k++) { const t = k / n * Math.asin(head / r); pts.push([cx + a - r + r * Math.cos(t), ys + r * Math.sin(t)]); }
  for (let k = n - 1; k >= 0; k--) { const t = k / n * Math.asin(head / r); pts.push([cx - a + r - r * Math.cos(t), ys + r * Math.sin(t)]); }
  return pts;
}

// THE OPENING: { shape: "circle"|"rect", w, h }, in the tile. Whatever's outside it is never glass
export function openingOf(L, tile) {
  const O = L.opening ?? {}, w = O.w ?? tile[0], h = O.h ?? tile[1];
  if (O.shape === "circle") return circle([0, 0], Math.min(w, h) / 2 * .995, 96, Math.PI / 96);
  return [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]];
}

// one shape of a ring: centred on angle t, between radii a and b, `half` radians either side
function ringShape(S, t, a, b, half) {
  const at = (r, q) => [r * Math.cos(q), r * Math.sin(q)], mid = (a + b) / 2, room = Math.min((b - a) / 2, mid * Math.sin(half));
  switch (S) {
    case "sector": {
      const pts = [], n = Math.max(3, Math.ceil(half * 16));
      for (let k = 0; k <= n; k++) pts.push(at(a, t - half + 2 * half * k / n));
      for (let k = n; k >= 0; k--) pts.push(at(b, t - half + 2 * half * k / n));
      return pts;
    }
    case "petal": {                                                 // (straight sides out to the springing, a pointed head to b)
      const rs = a + (b - a) * .42, hw = rs * Math.sin(half), y0 = rs * Math.cos(half), ux = Math.cos(t), uy = Math.sin(t);
      const head = (s, q) => { const x = s * hw * (1 - q) ** .72, y = y0 + (b - y0) * Math.sin(q * Math.PI / 2); return [y * ux - x * uy, y * uy + x * ux]; };
      const pts = [at(a, t - half)];
      for (let k = 0; k < 7; k++) pts.push(head(-1, k / 7));
      pts.push(at(b, t));
      for (let k = 6; k >= 0; k--) pts.push(head(1, k / 7));
      pts.push(at(a, t + half));
      return pts;
    }
    case "round": return circle(at(mid, t), room, 20, t);
    case "square": return circle(at(mid, t), room * 1.3, 4, t + Math.PI / 4);
    case "quatrefoil": return foil(at(mid, t), room, 4, t);
    default: throw new Error(`no ring shape "${S}"`);
  }
}

// the rings: each { r0, r1, n, shape, turn (of one step), gap, fill, fills, inner: { k, fill } } in shares of the radius R
export function ringPieces(rings, R) {
  const out = [];
  rings.forEach((Q, q) => {
    const n = Q.n ?? 1, half = Math.PI / n * (1 - (Q.gap ?? 0)), fills = Q.fills ?? [Q.fill ?? 0];
    if (n === 1 && (Q.shape ?? "round") === "round") { out.push({ pts: circle([0, 0], Q.r1 * R), fill: fills[0], role: "hub", label: `r${q}` }); return; }
    for (let k = 0; k < n; k++) {
      const t = Math.PI / 2 + (k + (Q.turn ?? 0)) * TAU / n, pts = ringShape(Q.shape ?? "round", t, Q.r0 * R, Q.r1 * R, half);
      out.push({ pts, fill: fills[k % fills.length], role: Q.role ?? "ring", label: `r${q}.${k}` });
      if (Q.inner) {
        const cx = pts.reduce((a, p) => a + p[0], 0) / pts.length, cy = pts.reduce((a, p) => a + p[1], 0) / pts.length, s = Q.inner.k ?? .55;
        out.push({ pts: pts.map((p) => [cx + (p[0] - cx) * s, cy + (p[1] - cy) * s]), fill: Q.inner.fills?.[k % Q.inner.fills.length] ?? Q.inner.fill ?? 0, role: "inner", label: `r${q}.${k}i` });
      }
    }
  });
  return out;
}

// the stone's own rose (arch/tracery.js): a pane for each thing the mason's bars enclose, at `lights`, so the two agree
export function stoneRose(L, R) {
  const K = 8 / R, T = roseLines({ a: 8, at: 0, springing: 0 }, { lights: L.lights, bar: .1 });        // (the masons' rule works in a real wall's metres: drawn at 8, brought back)
  if (!T) throw new Error("a rose too small for stone");
  for (const l of T.lines) l.pts = l.pts.map(([x, y]) => [x / K, y / K]);
  const n = Math.round(L.lights ?? 12), fills = L.fills ?? [0, 1], out = [], lines = T.lines;
  const hub = lines[0].pts, arches = lines.slice(1 + n, 1 + 2 * n), circles = lines.slice(1 + 2 * n);
  // (hub and arches are the masons' coarse polygons: the same points, so the bars sit on the leads)
  arches.forEach((A, k) => {
    const spoke0 = lines[1 + k].pts, spoke1 = lines[1 + (k + 1) % n].pts;
    out.push({ pts: [spoke0[0], ...A.pts, spoke1[0]], fill: fills[k % fills.length], role: "light", label: `a${k}` });
  });
  out.push({ pts: hub, fill: L.hub ?? 2, role: "hub", label: "hub" });
  circles.forEach((C, k) => { out.push({ pts: C.pts.length < 16 ? refine(C.pts) : C.pts, fill: (L.roundel ?? [3])[k % (L.roundel ?? [3]).length], role: "roundel", label: `c${k}` }); });
  return out;
}
const refine = (pts) => { const cx = pts.reduce((a, p) => a + p[0], 0) / pts.length, cy = pts.reduce((a, p) => a + p[1], 0) / pts.length, r = Math.hypot(pts[0][0] - cx, pts[0][1] - cy), t = Math.atan2(pts[0][1] - cy, pts[0][0] - cx); return circle([cx, cy], r, 24, t); };
