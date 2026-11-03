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
  const key = (x, y) => Math.round(x / Q) * 134217728 + Math.round(y / Q);   // (a number, not a string: this is the hot path. Exact to 670 m either way, and the distance below would catch a clash)
  const TRIES = lat ? [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]].map(([i, j]) => [i, j, ...lat.at(i, j)]) : [[0, 0, 0, 0]];
  const S0 = [0, 0], nodeAt = (p0) => {                                        // (a point: its node, and the period it stands in)
    if (!lat) {                                                   // (no period: no period to stand in, nothing to make for the collector. A window builds its net many times over)
      const x = p0[0], y = p0[1], kx = Math.round(x / Q), ky = Math.round(y / Q);
      for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
        const n = index.get((kx + a) * 134217728 + ky + b);
        if (n !== undefined) { const q = nodes[n], dx = q.x - x, dy = q.y - y; if (dx * dx + dy * dy < Q * Q * 4) return { n, s: S0 }; }
      }
      const n = nodes.length; nodes.push({ x, y, out: [] }); index.set(key(x, y), n); return { n, s: S0 };
    }
    const { p, s } = reduce(p0);
    // near the cell's edge a point may reduce to either side, so look at its neighbours in the rounding and across the cell
    for (const [i, j, ox, oy] of TRIES) {
      const X = p[0] + ox, Y = p[1] + oy;
      for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
        const n = index.get(key(X + a * Q, Y + b * Q));
        if (n !== undefined) {
          const q = nodes[n];
          if (Math.hypot(q.x - X, q.y - Y) < Q * 2) return { n, s: [s[0] - i, s[1] - j] };
        }
      }
    }
    const n = nodes.length;
    nodes.push({ x: p[0], y: p[1], out: [] });
    index.set(key(p[0], p[1]), n);
    return { n, s };
  };
  // cut: every segment against every other that its box reaches (the order they come in doesn't matter: they're sorted below)
  const N = segs.length, cuts = new Array(N);
  for (let i = 0; i < N; i++) cuts[i] = [0, 1];
  const cutBy = (i, j, ox, oy) => {
    const P = segs[i][0], R = segs[i][1], A = segs[j][0], B = segs[j][1];
    const dx = R[0] - P[0], dy = R[1] - P[1], rx = A[0] + ox, ry = A[1] + oy, ex = B[0] - A[0], ey = B[1] - A[1], d = dx * ey - dy * ex, wx = rx - P[0], wy = ry - P[1];
    if (Math.abs(d) < 1e-9) {                                     // (parallel: if on one line, the other's ends cut this one)
      if (Math.abs(wx * dy - wy * dx) > 1e-7 * Math.hypot(dx, dy)) return;
      const L = dx * dx + dy * dy;
      let t = (wx * dx + wy * dy) / L; if (t > EPS && t < 1 - EPS) cuts[i].push(t);
      t = ((rx + ex - P[0]) * dx + (ry + ey - P[1]) * dy) / L; if (t > EPS && t < 1 - EPS) cuts[i].push(t);
      return;
    }
    const t = (wx * ey - wy * ex) / d, u = (wx * dy - wy * dx) / d;
    if (t > EPS && t < 1 - EPS && u > -EPS && u < 1 + EPS) cuts[i].push(t);
  };
  const box = new Float64Array(N * 4);                            // (each segment's: left, right, bottom, top)
  let far = 0, x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (let i = 0; i < N; i++) {
    const [p, q] = segs[i], a = Math.min(p[0], q[0]), b = Math.max(p[0], q[0]), c = Math.min(p[1], q[1]), d = Math.max(p[1], q[1]);
    box[i * 4] = a; box[i * 4 + 1] = b; box[i * 4 + 2] = c; box[i * 4 + 3] = d;
    far = Math.max(far, b - a, d - c); x0 = Math.min(x0, a); x1 = Math.max(x1, b); y0 = Math.min(y0, c); y1 = Math.max(y1, d);
  }
  if (lat) {                                                      // (and against its copies one period away; `lo` is what the tolerance on u can reach past a box)
    const lo = 1e-6 + EPS * 2 * far, offs = [-1, 0, 1].flatMap((i) => [-1, 0, 1].map((j) => lat.at(i, j)));
    for (let i = 0; i < N; i++) {
      const a = box[i * 4] - lo, b = box[i * 4 + 1] + lo, c = box[i * 4 + 2] - lo, d = box[i * 4 + 3] + lo;
      for (let j = 0; j < N; j++) for (const o of offs) {
        if (i === j && !o[0] && !o[1]) continue;
        if (box[j * 4 + 1] + o[0] < a || box[j * 4] + o[0] > b || box[j * 4 + 3] + o[1] < c || box[j * 4 + 2] + o[1] > d) continue;
        cutBy(i, j, o[0], o[1]);
      }
    }
  } else if (N) {                                                 // (no period, many segments: a grid of cells, and only those sharing a cell are looked at)
    const lo = 1e-6, G = Math.max(1, Math.ceil(Math.sqrt(N))), cw = Math.max(x1 - x0, 1e-9) / G, ch = Math.max(y1 - y0, 1e-9) / G, cells = new Array(G * G), seen = new Int32Array(N);
    const cx = (x) => Math.max(0, Math.min(G - 1, Math.floor((x - x0) / cw))), cy = (y) => Math.max(0, Math.min(G - 1, Math.floor((y - y0) / ch)));
    for (let i = 0; i < N; i++) for (let v = cy(box[i * 4 + 2] - lo), V = cy(box[i * 4 + 3] + lo); v <= V; v++) for (let u = cx(box[i * 4] - lo), U = cx(box[i * 4 + 1] + lo); u <= U; u++) (cells[v * G + u] ??= []).push(i);
    for (let i = 0; i < N; i++) {
      const a = box[i * 4] - lo, b = box[i * 4 + 1] + lo, c = box[i * 4 + 2] - lo, d = box[i * 4 + 3] + lo;
      for (let v = cy(c), V = cy(d); v <= V; v++) for (let u = cx(a), U = cx(b); u <= U; u++) {
        const cell = cells[v * G + u];
        if (cell) for (const j of cell) {
          if (j === i || seen[j] === i + 1) continue;
          seen[j] = i + 1;
          if (box[j * 4 + 1] < a || box[j * 4] > b || box[j * 4 + 3] < c || box[j * 4 + 2] > d) continue;
          cutBy(i, j, 0, 0);
        }
      }
    }
  }
  // edges, each kept once (two copies of a shared polygon's side are one edge)
  const edges = [], seen = new Set(), BIG = 67108864;
  const eKey = lat ? (a, b, s) => a < b || (a === b && (s[0] > 0 || (s[0] === 0 && s[1] > 0))) ? `${a},${b},${s}` : `${b},${a},${[-s[0], -s[1]]}` : (a, b) => a < b ? a * BIG + b : b * BIG + a;
  for (let i = 0; i < N; i++) {
    const p = segs[i][0], q = segs[i][1], len = Math.hypot(q[0] - p[0], q[1] - p[1]);
    const ts = cuts[i].length === 2 ? cuts[i] : [...new Set(cuts[i].map((t) => Math.round(t * 1e7)))].sort((a, b) => a - b).map((t) => t / 1e7);
    let last = -1, B = null;                                      // (where this piece ended is where the next begins)
    for (let k = 0; k + 1 < ts.length; k++) {
      if ((ts[k + 1] - ts[k]) * len < Q * 4) continue;
      const A = last === k ? B : nodeAt([p[0] + (q[0] - p[0]) * ts[k], p[1] + (q[1] - p[1]) * ts[k]]);
      B = nodeAt([p[0] + (q[0] - p[0]) * ts[k + 1], p[1] + (q[1] - p[1]) * ts[k + 1]]); last = k + 1;
      const s = [B.s[0] - A.s[0], B.s[1] - A.s[1]];
      if (A.n === B.n && !s[0] && !s[1]) continue;
      const K = eKey(A.n, B.n, s);
      if (seen.has(K)) continue;
      seen.add(K);
      const e = edges.length;
      edges.push({ a: A.n, b: B.n, s });
      nodes[A.n].out.push({ e, to: B.n, s });
      nodes[B.n].out.push({ e, to: A.n, s: [-s[0], -s[1]] });
    }
  }
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
  const first = new Int32Array(nodes.length + 1); nodes.forEach((n, i) => { first[i + 1] = first[i] + n.out.length; });
  const done = new Uint8Array(first[nodes.length]), faces = [];     // (each node's way out, walked or not)
  nodes.forEach((n0, a0) => n0.out.forEach((o0, k0) => {
    if (done[first[a0] + k0]) return;
    const pts = []; let a = a0, k = k0, s = [0, 0], guard = 0;
    do {
      done[first[a] + k] = 1;
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
