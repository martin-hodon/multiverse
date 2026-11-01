// THE CUTS (docs/glass.md): glass breaks along a straight score, and won't turn a deep inward corner, so a pane that's too deep
// a C, too long, or over the largest sheet comes apart. A chord straight on from a deep inward corner, the shortest that parts it evenly;
// failing that, across its waist. Each chord ends on what it first meets: leads meet in T's, as they do. Greedy and deterministic.
const areaOf = (pts) => { let a = 0; pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; a += p[0] * q[1] - q[0] * p[1]; }); return a / 2; };

// how far each corner lies in from the hull: 0 for a convex one
function depths(pts) {
  const idx = pts.map((_, i) => i).sort((a, b) => pts[a][0] - pts[b][0] || pts[a][1] - pts[b][1]), cross = (o, a, b) => (pts[a][0] - pts[o][0]) * (pts[b][1] - pts[o][1]) - (pts[a][1] - pts[o][1]) * (pts[b][0] - pts[o][0]);
  const half = (list) => { const h = []; for (const i of list) { while (h.length > 1 && cross(h[h.length - 2], h[h.length - 1], i) <= 0) h.pop(); h.push(i); } h.pop(); return h; };
  const hull = [...half(idx), ...half([...idx].reverse())];
  return pts.map((p) => {
    let d = Infinity;
    for (let i = 0; i < hull.length; i++) {
      const a = pts[hull[i]], b = pts[hull[(i + 1) % hull.length]], L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
      d = Math.min(d, Math.abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / L);
    }
    return d;
  });
}
const reflexAt = (pts, i) => { const a = pts[(i - 1 + pts.length) % pts.length], p = pts[i], b = pts[(i + 1) % pts.length]; return (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0]) < -1e-12; };

// where a ray or chord from p first meets the polygon, not counting the edges beside corner i: { at, edge, t }
function firstHit(pts, p, d, skip) {
  let best = null;
  for (let e = 0; e < pts.length; e++) {
    if (skip.has(e)) continue;
    const a = pts[e], b = pts[(e + 1) % pts.length], ex = b[0] - a[0], ey = b[1] - a[1], den = ex * d[1] - ey * d[0];
    if (den >= -1e-12) continue;                             // (only an edge met from inside: its left. A lead joining an island is two edges in one place, and only one of them is ours)
    const t = -((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den, u = -((a[0] - p[0]) * d[1] - (a[1] - p[1]) * d[0]) / den;
    if (t > 1e-6 && u >= -1e-9 && u <= 1 + 1e-9 && (!best || t < best.t)) best = { t, edge: e, u: Math.min(1, Math.max(0, u)), at: [p[0] + d[0] * t, p[1] + d[1] * t] };
  }
  return best;
}
// a polygon cut from corner i to a point on edge e (or corner j): the two sides
function split(pts, i, hit) {
  const a = [pts[i]], b = [hit.at];
  for (let k = (i + 1) % pts.length; ; k = (k + 1) % pts.length) { a.push(pts[k]); if (k === hit.edge) break; }
  a.push(hit.at);
  for (let k = (hit.edge + 1) % pts.length; ; k = (k + 1) % pts.length) { b.push(pts[k]); if (k === i) break; }
  const clean = (q) => q.filter((p, n) => { const o = q[(n + 1) % q.length]; return Math.hypot(p[0] - o[0], p[1] - o[1]) > 1e-6; });
  return [clean(a), clean(b)];
}

// a garment's way of coming apart: along its folds, not across them. Of a pane's painted `lines`, `n` spread across it, each as far as it runs inside and straight on from its ends to the pane's edge
export function foldLeads(pts, lines, n) {
  const inside = (p) => { let c = false; pts.forEach((a, i) => { const b = pts[(i + 1) % pts.length]; if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]) c = !c; }); return c; };
  const lenOf = (q) => q.slice(1).reduce((s, p, i) => s + Math.hypot(p[0] - q[i][0], p[1] - q[i][1]), 0), size = Math.sqrt(Math.abs(areaOf(pts))), runs = [];
  for (const line of lines) {
    let best = [], run = [];
    for (const p of [...line, null]) { if (p && inside(p)) run.push(p); else { if (lenOf(run) > lenOf(best)) best = run; run = []; } }
    if (lenOf(best) > size * .5) runs.push(best);
  }
  runs.sort((a, b) => a[0][0] + a.at(-1)[0] - b[0][0] - b.at(-1)[0]);
  const out = [], none = new Set(), past = (a, b) => { const d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1; return firstHit(pts, b, [(b[0] - a[0]) / d, (b[1] - a[1]) / d], none)?.at; };
  for (let k = 1; k <= n && runs.length; k++) {
    const run = runs[Math.min(runs.length - 1, Math.floor(k * runs.length / (n + 1)))], foot = past(run[1], run[0]), head = past(run.at(-2), run.at(-1));
    if (!foot || !head) continue;
    [foot, ...run, head].forEach((p, i, all) => { if (i) out.push([all[i - 1], p]); });
  }
  return out;
}

export function cutPane(pts0, opts) {
  const { depth = .25, maxArea = Infinity, maxAspect = 4, least = 0 } = opts, out = [];
  const go = (pts, level) => {
    const A = areaOf(pts);
    if (level > 7 || pts.length < 4 || A < 1e-7 || A < least) return;
    const dep = depths(pts), D = depth * Math.sqrt(A);
    let deep = 0; pts.forEach((_, k) => { if (reflexAt(pts, k) && dep[k] > deep) deep = dep[k]; });
    if (deep > D) {
      // from any corner nearly that deep, straight on along its bisector: the chord that's short and parts the pane most evenly
      let best = null, bs = Infinity;
      pts.forEach((p, i) => {
        if (!reflexAt(pts, i) || dep[i] < deep * .6) return;
        const a = pts[(i - 1 + pts.length) % pts.length], b = pts[(i + 1) % pts.length], ua = [p[0] - a[0], p[1] - a[1]], ub = [p[0] - b[0], p[1] - b[1]], la = Math.hypot(...ua) || 1, lb = Math.hypot(...ub) || 1;
        const bx = ua[0] / la + ub[0] / lb, by = ua[1] / la + ub[1] / lb, n = Math.hypot(bx, by);
        if (n < 1e-6) return;
        const h = firstHit(pts, p, [bx / n, by / n], new Set([i, (i - 1 + pts.length) % pts.length]));
        if (!h) return;
        const sides = split(pts, i, h), s0 = areaOf(sides[0]), s1 = areaOf(sides[1]), even = Math.min(s0, s1) / A;
        if (Math.abs(s0 + s1 - A) > A * 1e-6 || even < .1 || Math.min(s0, s1) < least * .5) return;
        const s = h.t / Math.sqrt(A) + (.5 - even) * 2;
        if (s < bs) { bs = s; best = { p, h, sides }; }
      });
      if (best) { out.push([best.p, best.h.at]); go(best.sides[0], level + 1); go(best.sides[1], level + 1); return; }
    }
    // too large or too long: across its long axis, at the shortest of a few chords about the middle
    let xx = 0, yy = 0, xy = 0, cx = 0, cy = 0;
    for (const p of pts) { cx += p[0] / pts.length; cy += p[1] / pts.length; }
    for (const p of pts) { xx += (p[0] - cx) ** 2; yy += (p[1] - cy) ** 2; xy += (p[0] - cx) * (p[1] - cy); }
    const th = .5 * Math.atan2(2 * xy, xx - yy), ax = [Math.cos(th), Math.sin(th)], s = pts.map((p) => (p[0] - cx) * ax[0] + (p[1] - cy) * ax[1]), lo = Math.min(...s), hi = Math.max(...s);
    const w = pts.map((p) => -(p[0] - cx) * ax[1] + (p[1] - cy) * ax[0]), across = Math.max(...w) - Math.min(...w), aspect = (hi - lo) / (across || 1);
    if ((A <= maxArea && aspect <= maxAspect) || A < least * 2) return;
    let best = null;
    for (const f of [.5, .42, .58, .34, .66]) {
      const m = lo + (hi - lo) * f, o = [cx + ax[0] * m, cy + ax[1] * m], d = [-ax[1], ax[0]], hits = [];
      for (let e = 0; e < pts.length; e++) {
        const a = pts[e], b = pts[(e + 1) % pts.length], sa = (a[0] - o[0]) * ax[0] + (a[1] - o[1]) * ax[1], sb = (b[0] - o[0]) * ax[0] + (b[1] - o[1]) * ax[1];
        if ((sa > 0) !== (sb > 0)) { const t = sa / (sa - sb), q = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; hits.push({ edge: e, at: q, s: (q[0] - o[0]) * d[0] + (q[1] - o[1]) * d[1] }); }
      }
      hits.sort((x, y) => x.s - y.s);
      if (hits.length !== 2) continue;                       // (a chord that'd cross it more than once isn't one score)
      const len = hits[1].s - hits[0].s;
      if (!best || len < best.len) best = { len, hits };
    }
    if (!best) return;
    const [p, q] = [...best.hits].sort((x, y) => x.edge - y.edge), cutAt = pts.slice(0, p.edge + 1).concat([p.at]).concat(pts.slice(p.edge + 1, q.edge + 1)).concat([q.at]).concat(pts.slice(q.edge + 1));
    const i0 = p.edge + 1, h1 = { at: q.at, edge: q.edge + 1 };
    const [a, b] = split(cutAt, i0, h1);
    if (areaOf(a) <= 0 || areaOf(b) <= 0) return;
    out.push([p.at, q.at]);
    go(a, level + 1); go(b, level + 1);
  };
  go(pts0, 0);
  return out;
}
