// A NET: straight segments on a plane that may repeat (a lattice, or none), cut wherever they meet, as a planar graph:
// nodes, edges, faces, and the STRANDS that run straight through its crossings. Both the star patterns (ornament/stars.js)
// and the knots (ornament/knot.js) end here, so the weave (ornament/weave.js) has one thing to draw.
//   Coordinates are one period's worth, unwrapped: an edge runs from a node to a node plus whole lattice steps, and every
// piece that leaves a net (a strand, a face) is unwrapped along its own length, so it runs on across the tile's edge.
const EPS = 1e-6;

// the plane's period: reduce a point into the cell, as its lattice steps [i, j]
export function latticeOf(a, b) {
  const det = a[0] * b[1] - a[1] * b[0];
  const steps = (x, y) => [Math.floor((x * b[1] - y * b[0]) / det + 1e-7), Math.floor((a[0] * y - a[1] * x) / det + 1e-7)];
  return { a, b, steps, at: (i, j) => [i * a[0] + j * b[0], i * a[1] + j * b[1]] };
}

// A NET FROM SEGMENTS: [[x0, y0], [x1, y1]] in any period. `lat` null: a plain plane.
export function buildNet(segs, lat) {
  const nodes = [], index = new Map(), Q = 1e-5;
  const reduce = (p) => {
    if (!lat) return { p, s: [0, 0] };
    const s = lat.steps(p[0], p[1]), o = lat.at(s[0], s[1]);
    return { p: [p[0] - o[0], p[1] - o[1]], s };
  };
  const key = (x, y) => `${Math.round(x / Q)},${Math.round(y / Q)}`;
  const nodeAt = (p0) => {                                        // (a point: its node, and the period it stands in)
    const { p, s } = reduce(p0);
    // near the cell's edge a point may reduce to either side, so look at its neighbours in the rounding and across the cell
    const tries = lat ? [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]] : [[0, 0]];
    for (const [i, j] of tries) {
      const o = lat ? lat.at(i, j) : [0, 0];
      for (const dx of [-Q, 0, Q]) for (const dy of [-Q, 0, Q]) {
        const n = index.get(key(p[0] + o[0] + dx, p[1] + o[1] + dy));
        if (n !== undefined) {
          const q = nodes[n];
          if (Math.hypot(q.x - p[0] - o[0], q.y - p[1] - o[1]) < Q * 2) return { n, s: [s[0] - i, s[1] - j] };
        }
      }
    }
    const n = nodes.length;
    nodes.push({ x: p[0], y: p[1], out: [] });
    index.set(key(p[0], p[1]), n);
    return { n, s };
  };
  // cut: every segment against every other, and against its copies one period away
  const offs = lat ? [-1, 0, 1].flatMap((i) => [-1, 0, 1].map((j) => lat.at(i, j))) : [[0, 0]];
  const cuts = segs.map(() => [0, 1]);
  for (let i = 0; i < segs.length; i++) {
    const [p, q] = segs[i], dx = q[0] - p[0], dy = q[1] - p[1];
    for (let j = 0; j < segs.length; j++) for (const o of offs) {
      if (i === j && !o[0] && !o[1]) continue;
      const r = [segs[j][0][0] + o[0], segs[j][0][1] + o[1]], s = [segs[j][1][0] + o[0], segs[j][1][1] + o[1]];
      const ex = s[0] - r[0], ey = s[1] - r[1], d = dx * ey - dy * ex, wx = r[0] - p[0], wy = r[1] - p[1];
      if (Math.abs(d) < 1e-9) {                                   // (parallel: if on one line, the other's ends cut this one)
        if (Math.abs(wx * dy - wy * dx) > 1e-7 * Math.hypot(dx, dy)) continue;
        const L = dx * dx + dy * dy;
        for (const e of [r, s]) { const t = ((e[0] - p[0]) * dx + (e[1] - p[1]) * dy) / L; if (t > EPS && t < 1 - EPS) cuts[i].push(t); }
        continue;
      }
      const t = (wx * ey - wy * ex) / d, u = (wx * dy - wy * dx) / d;
      if (t > EPS && t < 1 - EPS && u > -EPS && u < 1 + EPS) cuts[i].push(t);
    }
  }
  // edges, each kept once (two copies of a shared polygon's side are one edge)
  const edges = [], seen = new Set();
  const eKey = (a, b, s) => a < b || (a === b && (s[0] > 0 || (s[0] === 0 && s[1] > 0))) ? `${a},${b},${s}` : `${b},${a},${[-s[0], -s[1]]}`;
  segs.forEach(([p, q], i) => {
    const ts = [...new Set(cuts[i].map((t) => Math.round(t * 1e7)))].sort((a, b) => a - b).map((t) => t / 1e7);
    for (let k = 0; k + 1 < ts.length; k++) {
      const at = (t) => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t];
      if ((ts[k + 1] - ts[k]) * Math.hypot(q[0] - p[0], q[1] - p[1]) < Q * 4) continue;
      const A = nodeAt(at(ts[k])), B = nodeAt(at(ts[k + 1])), s = [B.s[0] - A.s[0], B.s[1] - A.s[1]];
      if (A.n === B.n && !s[0] && !s[1]) continue;
      const K = eKey(A.n, B.n, s);
      if (seen.has(K)) continue;
      seen.add(K);
      const e = edges.length;
      edges.push({ a: A.n, b: B.n, s });
      nodes[A.n].out.push({ e, to: B.n, s });
      nodes[B.n].out.push({ e, to: A.n, s: [-s[0], -s[1]] });
    }
  });
  const net = { nodes, edges, lat };
  const off = (s) => lat ? lat.at(s[0], s[1]) : [0, 0];
  for (const n of nodes) {
    for (const o of n.out) { const q = nodes[o.to], w = off(o.s); o.dir = Math.atan2(q.y + w[1] - n.y, q.x + w[0] - n.x); }
    n.out.sort((a, b) => a.dir - b.dir);
  }
  return net;
}

// THE FACES of a net, by walking each edge's left side: { pts (unwrapped, counter-clockwise), area, sides, c }. The
// outer boundary of a plain plane comes out with negative area, and is left out.
export function facesOf(net) {
  const { nodes, lat } = net, off = (s) => lat ? lat.at(s[0], s[1]) : [0, 0];
  const done = new Set(), faces = [];
  nodes.forEach((n0, a0) => n0.out.forEach((o0, k0) => {
    if (done.has(`${a0},${k0}`)) return;
    const pts = []; let a = a0, k = k0, s = [0, 0], guard = 0;
    do {
      done.add(`${a},${k}`);
      const w = off(s), n = nodes[a], o = n.out[k];
      pts.push([n.x + w[0], n.y + w[1]]);
      s = [s[0] + o.s[0], s[1] + o.s[1]];
      const b = nodes[o.to], back = b.out.findIndex((q) => q.e === o.e && q.to === a && q.s[0] === -o.s[0] && q.s[1] === -o.s[1]);
      k = (back - 1 + b.out.length) % b.out.length;                 // (the next edge clockwise from the way back: the face on the left)
      a = o.to;
    } while ((a !== a0 || k !== k0) && ++guard < 4000);
    let A = 0, cx = 0, cy = 0;
    pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length], c = p[0] * q[1] - q[0] * p[1]; A += c; cx += (p[0] + q[0]) * c; cy += (p[1] + q[1]) * c; });
    A /= 2;
    if (A > 1e-9) faces.push({ raw: pts, pts: straighten(pts), area: A, c: [cx / (6 * A), cy / (6 * A)] });
  }));
  for (const f of faces) f.sides = f.pts.length;
  return faces;
}
// (a face's corners, without the points on its straight sides where something else ended)
function straighten(pts) {
  const out = pts.filter((p, i) => {
    const a = pts[(i - 1 + pts.length) % pts.length], b = pts[(i + 1) % pts.length];
    return Math.abs((p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])) > 1e-6 * Math.hypot(p[0] - a[0], p[1] - a[1]) * Math.hypot(b[0] - p[0], b[1] - p[1]);
  });
  return out.length >= 3 ? out : pts;
}

// THE STRANDS: from an edge, on through each node. A node of four is a CROSSING, gone straight through; a node of two is a
// bend; a node of one is an end, and so is any odd or crowded node a strand can't tell its way through.
//   -> [{ pts (unwrapped), closed, shift (a closed strand ends a whole period from where it began, on a lattice), nodes
// (the node index at each point) }], and net.ends, its loose ends, and net.crowded, the nodes with more than four edges.
export function strandsOf(net) {
  const { nodes, edges, lat } = net, off = (s) => lat ? lat.at(s[0], s[1]) : [0, 0];
  const onward = (b, comeBy) => {                                    // (at a node, from one of its out-entries: where next)
    const n = nodes[b], m = n.out.length;
    if (m === 2) return n.out[(comeBy + 1) % 2];
    if (m % 2 === 0) return n.out[(comeBy + m / 2) % m];             // (opposite, in the order round the node: straight on)
    return null;
  };
  const used = new Uint8Array(edges.length), out = [];
  const walk = (a0, k0) => {
    const seq = []; let a = a0, k = k0, s = [0, 0], closed = false;
    for (;;) {
      const n = nodes[a], o = n.out[k], w = off(s);
      seq.push({ node: a, x: n.x + w[0], y: n.y + w[1], e: o.e });
      used[o.e] = 1;
      s = [s[0] + o.s[0], s[1] + o.s[1]];
      const b = nodes[o.to], back = b.out.findIndex((q) => q.e === o.e && q.to === a && q.s[0] === -o.s[0] && q.s[1] === -o.s[1]);
      const nx = onward(o.to, back);
      a = o.to;
      if (!nx) { const w2 = off(s); seq.push({ node: a, x: b.x + w2[0], y: b.y + w2[1], e: -1 }); break; }
      k = b.out.indexOf(nx);
      if (a === a0 && k === k0) { closed = true; break; }
    }
    return { closed, seq, shift: closed ? off(s) : [0, 0] };
  };
  // ends first, so an open strand is walked from its end
  nodes.forEach((n, a) => { if (n.out.length % 2) n.out.forEach((o, k) => { if (!used[o.e]) out.push(walk(a, k)); }); });
  nodes.forEach((n, a) => n.out.forEach((o, k) => { if (!used[o.e]) out.push(walk(a, k)); }));
  net.crowded = nodes.filter((n) => n.out.length > 4).length;
  net.ends = nodes.filter((n) => n.out.length % 2).length;
  return out.map(({ closed, seq, shift }) => ({ closed, shift, pts: seq.map((q) => [q.x, q.y]), nodes: seq.map((q) => q.node) }));
}
