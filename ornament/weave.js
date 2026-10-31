// THE WEAVE: strands over and under at each crossing, alternating along every strand, and drawn as a flat band.
//   Which strand is on top is a choice for each crossing, and the alternation chains them: a two-colouring. A plane always
// has one; a repeating cell may not (a strand closes on an odd count), and then the tile has to be two cells: `conflicts`
// says so rather than drawing it wrong.
//   Drawn in two passes: every band whole, then at each crossing the top strand again, a short length following its own
// path, wide enough to cover the band under it. So an oblique crossing needs no cut ends, and a strand can't be drawn
// wrong by the order of the tile's copies, since the layer draws all of its own copies itself.
const TAU = Math.PI * 2;

// `cross(node)`: is this node a crossing. -> { byStrand: [[{ i, node, over }]], conflicts }
export function weaveOf(strands, cross) {
  const passes = [], at = new Map(), byStrand = strands.map(() => []);
  strands.forEach((st, si) => st.nodes.forEach((node, i) => {
    if (!cross(node)) return;
    const p = { si, i, node, over: null };
    passes.push(p); byStrand[si].push(p);
    if (!at.has(node)) at.set(node, []);
    at.get(node).push(p);
  }));
  const links = new Map(passes.map((p) => [p, []])), link = (a, b) => { links.get(a).push(b); links.get(b).push(a); };
  for (const l of at.values()) if (l.length === 2) link(l[0], l[1]);
  let conflicts = 0;
  byStrand.forEach((list, si) => {
    for (let i = 0; i + 1 < list.length; i++) link(list[i], list[i + 1]);
    if (!strands[si].closed || !list.length) return;
    if (list.length === 1) conflicts++;                               // (one pass a turn: over one way round, under the next)
    else link(list[list.length - 1], list[0]);
  });
  for (const p0 of passes) {
    if (p0.over !== null) continue;
    p0.over = true;
    const q = [p0];
    while (q.length) {
      const p = q.pop();
      for (const r of links.get(p)) {
        if (r.over === null) { r.over = !p.over; q.push(r); }
        else if (r.over === p.over) conflicts++;
      }
    }
  }
  return { byStrand, conflicts };
}

// A STRAND'S PATH: its points, closing on the copy of its first if it is closed, with the arc length of each, and of each of
// the strand's own points if a curve replaced them.
function pathOf(st, curve) {
  const c = curve ? curve(st) : null, base = c ? c.pts : st.pts;
  const pts = st.closed ? [...base, [base[0][0] + st.shift[0], base[0][1] + st.shift[1]]] : base, cum = [0];
  for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  return { pts, cum, total: cum[cum.length - 1], sOf: c ? (i) => c.at[i] : (i) => cum[i], shift: st.shift };
}
// the path between two arc lengths, running on round a closed strand, each lap a period on
function stretch(path, s0, s1, closed) {
  const { pts, cum, total, shift } = path, out = [];
  const laps = (s) => closed ? Math.floor(s / total) : 0;
  const pointAt = (s) => {
    const n = laps(s), r = closed ? s - n * total : Math.min(total, Math.max(0, s));
    let lo = 1, hi = cum.length - 1;
    while (lo < hi) { const m = (lo + hi) >> 1; if (cum[m] < r) lo = m + 1; else hi = m; }
    const t = cum[lo] > cum[lo - 1] ? (r - cum[lo - 1]) / (cum[lo] - cum[lo - 1]) : 0;
    return [pts[lo - 1][0] + (pts[lo][0] - pts[lo - 1][0]) * t + n * shift[0], pts[lo - 1][1] + (pts[lo][1] - pts[lo - 1][1]) * t + n * shift[1]];
  };
  out.push(pointAt(s0));
  for (let n = laps(s0); n <= laps(s1); n++) for (let i = 0; i < pts.length; i++) {
    const s = cum[i] + n * total;
    if (s > s0 + 1e-9 && s < s1 - 1e-9) out.push([pts[i][0] + n * shift[0], pts[i][1] + n * shift[1]]);
  }
  out.push(pointAt(s1));
  return out;
}

// PIECES: a strand's path from one crossing to the next (a little over, so they join under the band), brought into the cell.
// `wrap(p)` -> the period to take off. -> { whole: [polyline], over: [polyline], tight: how many crossings lack the room }
// `reach(node)`: how far along a strand the band across it extends, either side of the crossing.
export function piecesOf(strands, woven, { curve, reach, wrap, lap = 0 }) {
  const whole = [], over = []; let tight = 0;
  const place = (l, out) => {
    const m = l[l.length >> 1], o = wrap ? wrap(m) : [0, 0];
    out.push(o[0] || o[1] ? l.map((p) => [p[0] - o[0], p[1] - o[1]]) : l);
  };
  strands.forEach((st, si) => {
    const path = pathOf(st, curve), list = woven.byStrand[si], stops = list.map((p) => path.sOf(p.i)), m = stops.length;
    if (!m) {                                                          // (no crossing: the whole of it, in pieces short of a cell)
      const steps = Math.max(1, Math.ceil(path.pts.length / 8));
      for (let k = 0; k < steps; k++) place(stretch(path, k * path.total / steps, (k + 1) * path.total / steps + (st.closed ? lap : 0), st.closed), whole);
      return;
    }
    if (st.closed) for (let k = 0; k < m; k++) place(stretch(path, stops[k] - lap, (k + 1 < m ? stops[k + 1] : stops[0] + path.total) + lap, true), whole);
    else {
      const ends = [0, ...stops, path.total];
      for (let k = 0; k + 1 < ends.length; k++) place(stretch(path, Math.max(0, ends[k] - (k ? lap : 0)), Math.min(path.total, ends[k + 1] + (k + 2 < ends.length ? lap : 0)), false), whole);
    }
    list.forEach((p, k) => {
      if (!p.over) return;
      const s = stops[k], prev = k ? stops[k - 1] : st.closed ? stops[m - 1] - path.total : -Infinity, next = k + 1 < m ? stops[k + 1] : st.closed ? stops[0] + path.total : Infinity;
      const want = reach(p.node), room = Math.min(s - prev, next - s) * .49;
      if (want > room) tight++;
      const L = Math.min(want, room);
      place(stretch(path, st.closed ? s - L : Math.max(0, s - L), st.closed ? s + L : Math.min(path.total, s + L), st.closed), over);
    });
  });
  return { whole, over, tight };
}

export function pathsOf(lists) {
  const path = new Path2D();
  for (const l of lists) l.forEach((q, i) => (i ? path.lineTo(q[0], q[1]) : path.moveTo(q[0], q[1])));
  return path;
}
// A BAND: `edge` under it and wider, `fill` on top, and a thin `core` down its middle (Roman and Celtic bands are often
// grooved). `offs`: the copies it is stroked at.
export function strokeBand(g, path, offs, { width, edgeWidth = 0, fill, edge, core, coreWidth = 0, join = "miter" }) {
  g.lineJoin = join; g.miterLimit = 8; g.lineCap = "butt";
  const each = (style, w) => {
    g.strokeStyle = style; g.lineWidth = w;
    for (const [x, y] of offs) { g.save(); g.translate(x, y); g.stroke(path); g.restore(); }
  };
  if (edgeWidth > 0) each(edge, width + 2 * edgeWidth);
  each(fill, width);
  if (coreWidth > 0) each(core, coreWidth);
}

// a smooth closed or open curve through a strand's points (Catmull-Rom, `samples` to a span) -> { pts, at }
export function smooth(st, samples = 6) {
  const P = st.pts, n = P.length, get = (i) => {
    if (!st.closed) return P[Math.max(0, Math.min(n - 1, i))];
    const lap = Math.floor(i / n), q = P[i - lap * n];
    return [q[0] + lap * st.shift[0], q[1] + lap * st.shift[1]];
  };
  const pts = [], idx = [], spans = st.closed ? n : n - 1;
  for (let i = 0; i < spans; i++) {
    const a = get(i - 1), b = get(i), c = get(i + 1), d = get(i + 2);
    idx.push(pts.length);
    for (let k = 0; k < samples; k++) {
      const t = k / samples, t2 = t * t, t3 = t2 * t;
      pts.push([0, 1].map((e) => .5 * (2 * b[e] + (c[e] - a[e]) * t + (2 * a[e] - 5 * b[e] + 4 * c[e] - d[e]) * t2 + (3 * b[e] - a[e] - 3 * c[e] + d[e]) * t3)));
    }
  }
  if (!st.closed) { idx.push(pts.length); pts.push(P[n - 1]); }
  let s = 0; const cum = [0];
  for (let i = 1; i < pts.length; i++) { s += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); cum.push(s); }
  return { pts, at: idx.map((i) => cum[i]) };
}
export { TAU };
