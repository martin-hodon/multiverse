// THE PANES (docs/glass.md): a window is cut from sheets, so a picture of stacked PIECES (polygons, later over earlier: the way
// it's drawn) has to become a partition: faces that share every edge, each one colour, every edge a lead that ends on a lead.
// The arrangement of all the pieces' edges (ornament/net.js) is dissolved wherever both sides are one piece's, the slivers given to
// a neighbour, the islands joined by the shortest lead, and whatever can't be cut from one sheet is cut (glass/cuts.js). All in
// metres. A piece: { pts, fill, label?, whole?, hole?, paint? }; `label` makes pieces one pane, `whole` is never cut, `hole` is left to another panel.
import { buildNet, facesOf } from "../ornament/net.js";
import { cutPane, foldLeads } from "./cuts.js";

export const inPoly = (x, y, pts) => {
  let c = false;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    const a = pts[i], b = pts[j];
    if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) c = !c;
  }
  return c;
};
const boxOf = (pts) => { let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity; for (const p of pts) { if (p[0] < a) a = p[0]; if (p[1] < b) b = p[1]; if (p[0] > c) c = p[0]; if (p[1] > d) d = p[1]; } return [a, b, c, d]; };

// a point surely inside a polygon: the middle of its widest span, on a level between two of its corners
export function pointIn(pts) {
  const ys = [...new Set(pts.map((p) => p[1]))].sort((a, b) => a - b);
  let best = null, wide = -1;
  for (const k of [.5, .3, .7, .15, .85]) {
    const i = Math.floor((ys.length - 1) * k), y = (ys[i] + (ys[i + 1] ?? ys[i])) / 2, xs = [];
    pts.forEach((a, n) => { const b = pts[(n + 1) % pts.length]; if ((a[1] > y) !== (b[1] > y)) xs.push(a[0] + (y - a[1]) / (b[1] - a[1]) * (b[0] - a[0])); });
    xs.sort((a, b) => a - b);
    for (let n = 0; n + 1 < xs.length; n += 2) if (xs[n + 1] - xs[n] > wide) { wide = xs[n + 1] - xs[n]; best = [(xs[n] + xs[n + 1]) / 2, y]; }
  }
  return best ?? pts[0];
}

const FOLDED = new Set(["robe", "mantle", "wing"]);
const keyOf = (p, q) => { const a = `${Math.round(p[0] * 2e4)},${Math.round(p[1] * 2e4)}`, b = `${Math.round(q[0] * 2e4)},${Math.round(q[1] * 2e4)}`; return a < b ? a + "|" + b : b + "|" + a; };
const segsOf = (net) => net.edges.map((e) => [[net.nodes[e.a].x, net.nodes[e.a].y], [net.nodes[e.b].x, net.nodes[e.b].y]]);

// one panel of a window: its pieces, inside `clip`
export function partition(pieces0, { clip = null, minArea = 0, cut = {} } = {}) {
  const t0 = performance.now(), pieces = pieces0.map((p, i) => ({ ...p, label: p.label ?? i, box: boxOf(p.pts) })), clipBox = clip && boxOf(clip);
  // (the topmost piece at a point; nothing outside the clip)
  const at = (x, y) => {
    if (clip && (x < clipBox[0] || x > clipBox[2] || y < clipBox[1] || y > clipBox[3] || !inPoly(x, y, clip))) return null;
    for (let i = pieces.length - 1; i >= 0; i--) { const p = pieces[i], b = p.box; if (x >= b[0] && x <= b[2] && y >= b[1] && y <= b[3] && inPoly(x, y, p.pts)) return p.hole ? null : p; }
    return null;
  };
  const all = [];
  for (const p of pieces) p.pts.forEach((a, i) => all.push([a, p.pts[(i + 1) % p.pts.length]]));
  if (clip) clip.forEach((a, i) => all.push([a, clip[(i + 1) % clip.length]]));
  const arrangement = segsOf(buildNet(all, null));
  // the edges that part two labels
  const leadsNow = () => arrangement.filter(([a, b]) => {
    const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, nx = -(b[1] - a[1]) / d * 2e-4, ny = (b[0] - a[0]) / d * 2e-4;
    const l = at(mx + nx, my + ny), r = at(mx - nx, my - ny);
    return (l && l.label) !== (r && r.label);
  });
  // slivers go to the neighbour they share the most with: a copy of the face under that neighbour's name, on top, and again
  let segs = leadsNow(), slivers = 0;
  for (let round = 0; round < 6 && minArea; round++) {
    const faces = facesOf(buildNet(segs, null)), side = new Map();
    faces.forEach((f) => f.raw.forEach((a, i) => { const k = keyOf(a, f.raw[(i + 1) % f.raw.length]); (side.get(k) ?? side.set(k, []).get(k)).push(f); }));
    let changed = 0;
    for (const f of faces) {
      if (f.area >= minArea) continue;
      const own = at(...pointIn(f.raw));
      if (!own || own.whole) continue;
      const score = new Map();
      f.raw.forEach((a, i) => { const b = f.raw[(i + 1) % f.raw.length], o = side.get(keyOf(a, b))?.find((q) => q !== f); if (o) score.set(o, (score.get(o) ?? 0) + Math.hypot(b[0] - a[0], b[1] - a[1])); });
      let best = null, most = 0;
      for (const [o, s] of score) { const w = at(...pointIn(o.raw)); if (w && !w.whole && s > most) { most = s; best = w; } }
      if (best) { pieces.push({ ...best, pts: f.raw, box: boxOf(f.raw), paint: null }); changed++; slivers++; }
    }
    if (!changed) break;
    segs = leadsNow();
  }
  // (a lead that goes nowhere is no lead: taken back to where it joins. Before the islands are joined, or a join may hang on one)
  let pruned = 0;
  const prune = (N) => {                                       // (all at once: the ends, then what they leave as ends, and the net built once from what's left)
    const deg = N.nodes.map((n) => n.out.length), gone = new Uint8Array(N.edges.length), stack = [];
    N.edges.forEach((e, i) => { if (deg[e.a] === 1 || deg[e.b] === 1) { gone[i] = 1; stack.push(i); } });
    if (!stack.length) return N;
    while (stack.length) {
      const e = N.edges[stack.pop()];
      pruned++;
      for (const v of [e.a, e.b]) if (--deg[v] === 1) for (const o of N.nodes[v].out) if (!gone[o.e]) { gone[o.e] = 1; stack.push(o.e); }
    }
    return buildNet(segsOf({ ...N, edges: N.edges.filter((_, i) => !gone[i]) }), null);
  };
  segs = segsOf(prune(buildNet(segs, null)));
  // islands: each joined to what's round it by the shortest lead there is (shortest, so it crosses nothing)
  const bridges = [], base = buildNet(segs, null), root = base.nodes.map((_, i) => i), find = (i) => { while (root[i] !== i) i = root[i] = root[root[i]]; return i; };
  for (const e of base.edges) root[find(e.a)] = find(e.b);
  const members = new Map(); base.nodes.forEach((_, i) => { const c = find(i); (members.get(c) ?? members.set(c, []).get(c)).push(i); });
  const spanOf = (c) => { let lo = Infinity, hi = -Infinity; for (const i of members.get(c)) { lo = Math.min(lo, base.nodes[i].x); hi = Math.max(hi, base.nodes[i].x); } return hi - lo; };
  const order = [...members.keys()].sort((a, b) => spanOf(a) - spanOf(b) || a - b);   // (the smallest first: an island in an island gets to its surround)
  for (const c0 of order.slice(0, -1)) {
    const c = find(c0), mine = members.get(c0).filter((i) => find(i) === c);
    let lo = Infinity, hi = -Infinity, bot = Infinity, top = -Infinity;
    for (const i of mine) { const n = base.nodes[i]; lo = Math.min(lo, n.x); hi = Math.max(hi, n.x); bot = Math.min(bot, n.y); top = Math.max(top, n.y); }
    const nearest = (reach) => {                               // (what's within a window of it first: what's nearest there is nearest anywhere, if it's closer than the window)
      let best = null, D = Infinity;
      const others = base.edges.filter((e) => { const a = base.nodes[e.a], b = base.nodes[e.b]; return find(e.a) !== c && Math.max(a.x, b.x) >= lo - reach && Math.min(a.x, b.x) <= hi + reach && Math.max(a.y, b.y) >= bot - reach && Math.min(a.y, b.y) <= top + reach; });
      for (const i of mine) {
        const n = base.nodes[i];
        for (const e of others) {
          const a = base.nodes[e.a], b = base.nodes[e.b], dx = b.x - a.x, dy = b.y - a.y, t = Math.max(0, Math.min(1, ((n.x - a.x) * dx + (n.y - a.y) * dy) / (dx * dx + dy * dy || 1)));
          const qx = a.x + dx * t, qy = a.y + dy * t, d = Math.hypot(qx - n.x, qy - n.y);
          if (d < D) { D = d; best = { seg: [[n.x, n.y], [qx, qy]], to: e.a }; }
        }
      }
      return D <= reach ? best : null;
    };
    const best = nearest((hi - lo + top - bot) * .25 + 1e-3) ?? nearest(Infinity);
    if (!best) continue;
    bridges.push(best.seg); root[c] = find(best.to);          // (over nothing it paints nothing: the outside has no lead, and the panes' test drops it)
  }
  let net = buildNet([...segs, ...bridges], null);
  // cuts: a garment too big for a sheet along its folds (those that run up it: a hem or a belt lies across); then chords through what one sheet still won't make, the panes as they stand
  const folds = [], chords = [];
  for (const f of facesOf(net)) {
    const own = at(...pointIn(f.raw)), lines = FOLDED.has(own?.role) ? (own.paint ?? []).filter((q) => q.fill === undefined && !q.closed && q.pts.length > 2 && Math.abs(q.pts.at(-1)[1] - q.pts[0][1]) > Math.abs(q.pts.at(-1)[0] - q.pts[0][0]) * .5).map((q) => q.pts) : [];
    if (lines.length && f.area > (cut.maxArea ?? Infinity)) folds.push(...foldLeads(f.raw, lines, Math.ceil(f.area / cut.maxArea) - 1));
  }
  if (folds.length) net = buildNet([...segs, ...bridges, ...folds], null);
  for (const f of facesOf(net)) {
    const own = at(...pointIn(f.raw));
    if (own && !own.whole) chords.push(...cutPane(f.raw, { least: minArea * 3, ...cut }));
  }
  if (chords.length) net = buildNet([...segs, ...bridges, ...folds, ...chords], null);
  net = prune(net);
  // (a chord or a bridge can leave a pane too small to cut: it goes back to the glass it was cut from, or to any neighbour, one to be kept whole last of all, its lead with it)
  for (let round = 0; round < 8 && minArea; round++) {
    const faces = facesOf(net), side = new Map(), gone = new Set();
    faces.forEach((f) => f.raw.forEach((a, i) => { const k = keyOf(a, f.raw[(i + 1) % f.raw.length]); (side.get(k) ?? side.set(k, []).get(k)).push(f); }));
    for (const f of faces) {
      if (f.area >= minArea * .5) continue;
      const own = at(...pointIn(f.raw)) ?? at(f.c[0], f.c[1]);          // (a sliver's inside can fall through a line)
      if (!own || own.whole) continue;
      let best = null, most = 0;
      f.raw.forEach((a, i) => { const b = f.raw[(i + 1) % f.raw.length], k = keyOf(a, b), o = side.get(k)?.find((q) => q !== f), w = o && at(...pointIn(o.raw)); if (!w || gone.has(k)) return; const L = Math.hypot(b[0] - a[0], b[1] - a[1]) * (w.label === own.label ? 100 : w.whole ? .01 : 1); if (L > most) { most = L; best = k; } });
      if (best) gone.add(best);
    }
    if (!gone.size) break;
    const kept = segsOf(net).filter(([a, b]) => !gone.has(keyOf(a, b)));
    for (const f of faces) if (f.area < minArea * .5) { const w = at(...pointIn(f.raw)); if (w && !w.whole) { const q = f.raw.map((a, i) => keyOf(a, f.raw[(i + 1) % f.raw.length])).find((k) => gone.has(k)); if (q) { const o = side.get(q).find((g) => g !== f), other = at(...pointIn(o.raw)); if (other && other.label !== w.label) pieces.push({ ...other, pts: f.raw, box: boxOf(f.raw), paint: null }); } } }
    net = prune(buildNet(kept, null));
  }
  const panes = [];
  for (const f of facesOf(net)) {
    const own = at(...pointIn(f.raw)) ?? at(f.c[0], f.c[1]);          // (a point on a line of the arrangement can fall through it)
    if (own) panes.push({ pts: f.raw, area: f.area, c: f.c, fill: own.fill, label: own.label, role: own.role, whole: !!own.whole, sheet: own.sheet });
  }
  // the leads, those with a pane on either side
  const paneKeys = new Set(); for (const p of panes) p.pts.forEach((a, i) => paneKeys.add(keyOf(a, p.pts[(i + 1) % p.pts.length])));
  const leads = segsOf(net).filter(([a, b]) => paneKeys.has(keyOf(a, b)));
  // (too small to cut: though not if it's all the glass there is, a corner the stone leaves)
  const edgeUse = new Map(); for (const p of panes) p.pts.forEach((a, i) => { const k = keyOf(a, p.pts[(i + 1) % p.pts.length]); edgeUse.set(k, (edgeUse.get(k) ?? 0) + 1); });
  const alone = (p) => p.pts.every((a, i) => edgeUse.get(keyOf(a, p.pts[(i + 1) % p.pts.length])) < 2);
  const check = buildNet(leads, null), degree = check.nodes.map((n) => n.out.length);
  const area = panes.reduce((s, p) => s + p.area, 0);
  return { panes, leads, pieces, clip, metrics: {
    panes: panes.length, cuts: chords.length, folds: folds.length, slivers, pruned, bridges: bridges.length,
    open: degree.filter((d) => d === 1).length, tiny: panes.filter((p) => minArea && p.area < minArea * .5 && !p.whole && !(alone(p) && p.area >= minArea * .25)).length,
    area, ms: Math.round(performance.now() - t0),
  } };
}
