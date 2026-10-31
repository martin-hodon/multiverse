// KNOTS: a grid of crossings with some of them BROKEN (Bain's Celtic construction, and the same for Viking knotwork, a Roman
// guilloche and a Byzantine braid). Grid points whose coordinates add up to an odd number are nodes; each has four ports, on
// its diagonals, joined to the next nodes along them. At a crossing a strand goes straight through; at a break it bounces
// off a wall lying east-west (`h`) or north-south (`v`). A grid's border is a line of breaks. No breaks in a narrow strip is
// a plait: one cell high, the two-strand guilloche; two, a braid.
const PORTS = [[1, 1], [-1, 1], [-1, -1], [1, -1]];    // NE NW SW SE
const hash = (...k) => { let h = 2166136261; for (const v of k) { h = Math.imul(h ^ (v | 0), 16777619); h ^= h >>> 13; } return ((h >>> 0) % 100003) / 100003; };

// WHERE THE WALLS ARE: { key "i,j": "h" | "v" }. `breaks` is the share of inner nodes that start a wall, which runs `run` nodes
// on the way it lies, so the knot gets the straight stretches a real one has. `symmetry` (x, y, xy, r2, r4: a square)
// repeats it: each orbit is drawn once, from its smallest member. `walls` lists any by hand.
function breaksOf(L, W, H, seed, wrapX, wrapY) {
  const out = new Map(), p = L.breaks ?? 0, sym = L.symmetry ?? "none", maxRun = L.run ?? 3;
  const mod = (v, m, on) => on ? ((v % m) + m) % m : v, keyOf = (i, j) => `${mod(i, W, wrapX)},${mod(j, H, wrapY)}`;
  const open = (i, j) => (wrapX || (i > 0 && i < W)) && (wrapY || (j > 0 && j < H));
  // (the orbit of a node: [i, j, does its wall turn])
  const orbit = (i, j) => {
    const o = [[i, j, 0]];
    if (sym === "x" || sym === "xy") o.push([W - i, j, 0]);
    if (sym === "y" || sym === "xy") o.push([i, H - j, 0]);
    if (sym === "xy" || sym === "r2") o.push([W - i, H - j, 0]);
    if (sym === "r4") o.push([W - i, H - j, 0], [j, W - i, 1], [H - j, i, 1]);
    return o;
  };
  const turn = (t) => (t === "h" ? "v" : "h");
  for (let i = 0; i <= W; i++) for (let j = 0; j <= H; j++) {
    if ((i + j) % 2 === 0 || !open(i, j)) continue;
    const rep = orbit(i, j).map((q) => [mod(q[0], W, wrapX), mod(q[1], H, wrapY), q[2]]).sort((a, b) => a[0] - b[0] || a[1] - b[1])[0];
    if (mod(i, W, wrapX) !== rep[0] || mod(j, H, wrapY) !== rep[1] || hash(rep[0], rep[1], seed, 7) >= p) continue;
    const t = hash(rep[0], rep[1], seed, 11) < (L.upright ?? .5) ? "v" : "h", len = 1 + Math.floor(hash(rep[0], rep[1], seed, 13) * maxRun);
    // a wall runs on along its own line: the nodes on a line lie two apart
    for (let k = 0; k < len; k++) {
      const a = t === "h" ? i + 2 * k : i, b = t === "h" ? j : j + 2 * k;
      // (a run stops at a node one of its copies already took, or the symmetry would be broken by whichever came last)
      if (!open(a, b) || orbit(a, b).some(([x, y]) => out.has(keyOf(x, y)))) break;
      for (const [x, y, f] of orbit(a, b)) if (open(x, y)) out.set(keyOf(x, y), f ? turn(t) : t);
    }
  }
  for (const [i, j, t] of L.walls ?? []) out.set(keyOf(i, j), t);
  return out;
}

// the strands of one draw -> [{ pts, closed, shift, nodes }], a node index for a crossing, -1 for a bounce
function trace(L, W, H, u, inset, breaks, wrapX, wrapY) {
  const wx = (i) => wrapX ? ((i % W) + W) % W : i, wy = (j) => wrapY ? ((j % H) + H) % H : j;
  const type = (i, j) => {
    if (!wrapX && (i === 0 || i === W)) return "v";
    if (!wrapY && (j === 0 || j === H)) return "h";
    return breaks.get(`${wx(i)},${wy(j)}`) ?? "x";
  };
  const id = (i, j) => wx(i) * (H + 2) + wy(j);
  const next = (t, port) => t === "x" ? (port + 2) % 4 : t === "h" ? [1, 0, 3, 2][port] : [3, 2, 1, 0][port];
  const seen = new Set(), strands = [], off = L.bounce ?? .42;
  const mark = (i, j, p) => `${wx(i)},${wy(j)},${p}`;
  for (let i0 = 0; i0 <= (wrapX ? W - 1 : W); i0++) for (let j0 = 0; j0 <= (wrapY ? H - 1 : H); j0++) {
    if ((i0 + j0) % 2 === 0) continue;
    for (let p0 = 0; p0 < 4; p0++) {
      if (seen.has(mark(i0, j0, p0))) continue;
      // leave the node by port p0; a border node has ports that lead nowhere
      const [dx0, dy0] = PORTS[p0];
      if ((!wrapX && (i0 + dx0 < 0 || i0 + dx0 > W)) || (!wrapY && (j0 + dy0 < 0 || j0 + dy0 > H))) continue;
      const pts = [], nodes = []; let i = i0, j = j0, p = p0, guard = 0;
      do {
        seen.add(mark(i, j, p));
        const [dx, dy] = PORTS[p];
        i += dx; j += dy;
        const inp = (p + 2) % 4, t = type(i, j), out = next(t, inp);
        seen.add(mark(i, j, inp));
        // the point it passes: the node itself, or off a wall on the side it came from
        const x = (i - W / 2) * u, y = (j - H / 2) * u * (L.squash ?? 1);
        if (t === "x") { pts.push([x, y]); nodes.push(id(i, j)); }
        else if (t === "h") { pts.push([x, y - dy * off * u * (L.squash ?? 1)]); nodes.push(-1); }
        else { pts.push([x - dx * off * u, y]); nodes.push(-1); }
        p = out;
      } while ((wx(i) !== wx(i0) || wy(j) !== wy(j0) || p !== p0) && ++guard < 20000);
      // (a strand that goes round a repeat ends whole periods from where it began)
      const shift = [(i - i0) * u, (j - j0) * u * (L.squash ?? 1)];
      strands.push({ pts, nodes, closed: true, shift, length: pts.length, crossings: nodes.filter((n) => n >= 0).length });
    }
  }
  return strands;
}

// THE KNOT, in metres on the tile: `cols` x `rows` cells (each 2 grid steps), `wrap` "x", "y", "xy" or none. A wild draw
// has many small rings, so draw `tries` and keep the one with the fewest strands, then the longest shortest.
export function knotNet(L, tile) {
  const cols = L.cols ?? 4, rows = L.rows ?? 4, wrap = L.wrap ?? "xy", wrapX = wrap.includes("x"), wrapY = wrap.includes("y");
  const W = cols * 2, H = rows * 2, m = L.margin ?? 0;
  const u = (tile[0] - (wrapX ? 0 : 2 * m)) / W, squash = (tile[1] - (wrapY ? 0 : 2 * m)) / H / u;
  const P = { ...L, squash };
  let best = null;
  for (let t = 0, tries = L.breaks ? (L.tries ?? 40) : 1; t < tries; t++) {
    const breaks = breaksOf(L, W, H, (L.seed ?? 1) * 1000 + t, wrapX, wrapY), strands = trace(P, W, H, u, m, breaks, wrapX, wrapY);
    const shortest = Math.min(...strands.map((s) => s.length));
    const score = strands.length * 100 - shortest + (shortest < 4 ? 500 : 0);
    if (!best || score < best.score) best = { score, strands, breaks };
  }
  return { strands: best.strands, u, squash, W, H, wrapX, wrapY, breaks: best.breaks.size };
}
