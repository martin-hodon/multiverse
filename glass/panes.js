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
  // (which pieces might lie at a point, in the order they were stacked: a window asks this of every edge, several times over, and most pieces are nowhere near)
  let lo0 = Infinity, lo1 = Infinity, hi0 = -Infinity, hi1 = -Infinity; for (const p of pieces) { lo0 = Math.min(lo0, p.box[0]); lo1 = Math.min(lo1, p.box[1]); hi0 = Math.max(hi0, p.box[2]); hi1 = Math.max(hi1, p.box[3]); }
  const GRID = 48, gx = GRID / (hi0 - lo0 || 1), gy = GRID / (hi1 - lo1 || 1), cellsOf = Array.from({ length: GRID * GRID }, () => []);
  const file = (p) => { const b = p.box, a0 = Math.floor((b[0] - lo0) * gx), a1 = Math.floor((b[2] - lo0) * gx), c0 = Math.floor((b[1] - lo1) * gy), c1 = Math.floor((b[3] - lo1) * gy); for (let v = Math.max(0, c0); v <= Math.min(GRID - 1, c1); v++) for (let u = Math.max(0, a0); u <= Math.min(GRID - 1, a1); u++) cellsOf[v * GRID + u].push(p); };
  const cellAt = (x, y) => { const u = Math.floor((x - lo0) * gx), v = Math.floor((y - lo1) * gy); return u < 0 || v < 0 || u >= GRID || v >= GRID ? null : cellsOf[v * GRID + u]; };
  pieces.forEach(file);
  // (the topmost piece at a point; nothing outside the clip)
  const at = (x, y) => {
    if (clip && (x < clipBox[0] || x > clipBox[2] || y < clipBox[1] || y > clipBox[3] || !inPoly(x, y, clip))) return null;
    const list = cellAt(x, y) ?? pieces; for (let i = list.length - 1; i >= 0; i--) { const p = list[i], b = p.box; if (x >= b[0] && x <= b[2] && y >= b[1] && y <= b[3] && inPoly(x, y, p.pts) && !(p.within && !inPoly(x, y, p.within))) return p.hole ? null : p; }   // (`within`: a scene's piece goes no further than its frame)
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
      let best = null, most = 0, whole = null, wm = 0;
      for (const [o, s] of score) { const w = at(...pointIn(o.raw)); if (w && !w.whole && s > most) { most = s; best = w; } else if (w && w.whole && w !== own && s > wm) { wm = s; whole = w; } }
      best ??= whole;                                          // (with nothing else beside it, it goes to what's kept whole: a hair more of a face beats a pane no glazier could cut)
      if (best) { const q = { ...best, pts: f.raw, box: boxOf(f.raw), paint: null }; pieces.push(q); file(q); changed++; slivers++; }
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
      let D2 = Infinity, bn = null, bx = 0, by = 0, bt = 0; const R0 = lo - reach, R1 = hi + reach, R2 = bot - reach, R3 = top + reach, others = [], nodes = base.nodes;
      for (const e of base.edges) { const a = nodes[e.a], b = nodes[e.b]; if ((a.x > b.x ? a.x : b.x) >= R0 && (a.x < b.x ? a.x : b.x) <= R1 && (a.y > b.y ? a.y : b.y) >= R2 && (a.y < b.y ? a.y : b.y) <= R3 && find(e.a) !== c) others.push(e); }
      for (const i of mine) {
        const n = nodes[i], nx = n.x, ny = n.y;
        for (let k = 0; k < others.length; k++) {
          const e = others[k], a = nodes[e.a], b = nodes[e.b], ax = a.x, ay = a.y, dx = b.x - ax, dy = b.y - ay, u = ((nx - ax) * dx + (ny - ay) * dy) / (dx * dx + dy * dy || 1), t = u < 0 ? 0 : u > 1 ? 1 : u;
          const qx = ax + dx * t, qy = ay + dy * t, ex = qx - nx, ey = qy - ny, d = ex * ex + ey * ey;
          if (d < D2) { D2 = d; bn = n; bx = qx; by = qy; bt = e.a; }
        }
      }
      const D = Math.sqrt(D2), best = bn && { seg: [[bn.x, bn.y], [bx, by]], to: bt };
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
    for (const f of faces) if (f.area < minArea * .5) { const w = at(...pointIn(f.raw)); if (w && !w.whole) { const q = f.raw.map((a, i) => keyOf(a, f.raw[(i + 1) % f.raw.length])).find((k) => gone.has(k)); if (q) { const o = side.get(q).find((g) => g !== f), other = at(...pointIn(o.raw)); if (other && other.label !== w.label) { const n = { ...other, pts: f.raw, box: boxOf(f.raw), paint: null }; pieces.push(n); file(n); } } } }
    net = prune(buildNet(kept, null));
  }
  const panes = [];
  for (const f of facesOf(net)) {
    const own = at(...pointIn(f.raw)) ?? at(f.c[0], f.c[1]);          // (a point on a line of the arrangement can fall through it)
    if (own && f.area > 1e-6) panes.push({ pts: f.raw, area: f.area, c: f.c, fill: own.fill, label: own.label, role: own.role, whole: !!own.whole, sheet: own.sheet });
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
