// ARABESQUE: the vine scroll of Islamic tile and plaster (islimi), in flat shapes. Space is packed with circles, side by side.
// A STEM runs through each row, over one circle and under the next, so it can't help but be smooth; in each circle a
// BRANCH leaves the stem along its own curve and winds inward, a tapering band ending in a split leaf (the rumi). Leaves
// stand along the outside of the curl, and a small palmette fills each hollow where four circles nearly meet. A second vine,
// thinner and set half a circle off, may run under it: the two levels of a Timurid or Safavid panel.
//   All in the tile's own units. `motif`: the same curl, turned round the middle of a star.
const TAU = Math.PI * 2;

function bandPath(out, pts, w) {
  const n = pts.length, left = [], right = [];
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1;
    const h = w(i / (n - 1)) / 2, nx = -dy / l, ny = dx / l;
    left.push([pts[i][0] + nx * h, pts[i][1] + ny * h]); right.push([pts[i][0] - nx * h, pts[i][1] - ny * h]);
  }
  left.forEach((p, i) => (i ? out.lineTo(p[0], p[1]) : out.moveTo(p[0], p[1])));
  for (let i = n - 1; i >= 0; i--) out.lineTo(right[i][0], right[i][1]);
  out.closePath();
}

// a leaf: from its foot along `dir`, a curved almond bent to `side`
function leafPath(out, x, y, dir, len, side, fat = .55) {
  const c = Math.cos(dir), s = Math.sin(dir), P = (u, v) => [x + (u * c - v * side * s) * len, y + (u * s + v * side * c) * len];
  const tip = P(1, .3), a = P(.4, fat), b = P(.65, -fat * .12), f = P(0, 0);
  out.moveTo(f[0], f[1]);
  out.quadraticCurveTo(a[0], a[1], tip[0], tip[1]);
  out.quadraticCurveTo(b[0], b[1], f[0], f[1]);
  out.closePath();
}
// a palmette: a fan of five lobes, the longest in the middle
function palmette(out, x, y, dir, len) {
  for (const [t, l] of [[1, .62], [.52, .85]]) for (const s of [1, -1]) leafPath(out, x, y, dir + s * t, len * l, -s, .42);
  leafPath(out, x, y, dir, len, 1, .3);
  leafPath(out, x, y, dir, len, -1, .3);
}
// a flower (hatayi)
function flower(out, heart, x, y, r, n = 6) {
  for (let i = 0; i < n; i++) {
    const t = i * TAU / n, c = Math.cos(t), s = Math.sin(t), q = r * .6, w = .62;
    out.moveTo(x, y);
    out.quadraticCurveTo(x + (c * q - s * q * w), y + (s * q + c * q * w), x + c * r, y + s * r);
    out.quadraticCurveTo(x + (c * q + s * q * w), y + (s * q - c * q * w), x, y);
    out.closePath();
  }
  heart.moveTo(x + r * .26, y); heart.arc(x, y, r * .26, 0, TAU);
}

// A CURL round centre c, starting at angle a0 and radius R, winding `sense` (-1 clockwise) inward `turns` times, to `inner` of R.
function curl(paths, c, a0, sense, R, { turns = 1.25, inner = .24, width, leaf, leaves = 6, end = 1.5, bud = false }) {
  const N = Math.max(12, Math.round(40 * turns)), pts = [];   // (it stays a band all the way in: a thread at its end reads as a tail)
  for (let i = 0; i <= N; i++) {
    const t = i / N, a = a0 + sense * t * turns * TAU, r = R * (1 - (1 - inner) * t);
    pts.push([c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]);
  }
  bandPath(paths.stem, pts, (t) => width * (1 - .4 * t));
  for (let k = 0; k < leaves; k++) {
    const i = Math.round((k + .6) / (leaves + .6) * (N - 3)), p = pts[i], q = pts[i + 1], d = Math.atan2(q[1] - p[1], q[0] - p[0]);
    const L = leaf * (1 - .45 * i / N);
    // alternately out and in, leaning on the way it grows, the outer ones the longer
    if (k % 2 === 0) leafPath(paths.leaf, p[0], p[1], d - sense * .55, L, -sense);
    else leafPath(paths.leaf, p[0], p[1], d + sense * .5, L * .7, sense);
  }
  const e = pts[N], f = pts[N - 2], dir = Math.atan2(e[1] - f[1], e[0] - f[0]);
  if (bud) flower(paths.flower, paths.heart, e[0], e[1], leaf * end * .7);
  else palmette(paths.leaf, e[0], e[1], dir, leaf * end);
}

const emptyPaths = () => ({ stem: new Path2D(), leaf: new Path2D(), flower: new Path2D(), heart: new Path2D(), line: new Path2D() });

// ONE VINE over the tile: `cols` x `rows` circles, both even for the rows to meet
function vine(L, tile, { dx = 0, dy = 0, thin = 1 } = {}) {
  const p = emptyPaths(), cols = L.cols ?? 4, rows = L.rows ?? 4, cw = tile[0] / cols, ch = tile[1] / rows, R = Math.min(cw, ch) / 2;
  const width = (L.width ?? .07) * R * thin, leaf = (L.leaf ?? .3) * R * thin;
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const c = [-tile[0] / 2 + (i + .5) * cw + dx, -tile[1] / 2 + (j + .5) * ch + dy], up = (i + j) % 2 === 0;
    // the stem: over the top of this circle or under the bottom, west to east
    p.line.moveTo(c[0] - R, c[1]);
    p.line.arc(c[0], c[1], R, Math.PI, 0, up);                                   // (canvas: y is up here, so "anticlockwise" runs over the top)
    const sense = up ? -1 : 1, a0 = up ? Math.PI * .72 : -Math.PI * .72;
    curl(p, c, a0, sense, R, { turns: L.turns ?? 1.2, width: width * .9, leaf, leaves: L.leaves ?? 6, end: L.end ?? 1.5, bud: !!L.flowers && (i + j) % 2 === 0 });
    // leaves on the stem's outside, and a palmette in the hollow it leaves
    for (const a of [.3, .7]) {
      const t = up ? Math.PI * (1 - a) : -Math.PI * (1 - a), q = [c[0] + R * Math.cos(t), c[1] + R * Math.sin(t)];
      leafPath(p.leaf, q[0], q[1], t - sense * 1.1, leaf * .8, sense);
    }
    // (every hollow has one above or below it: rooted on the stem where two circles touch)
    if ((i + j) % 2 === 0) for (const d of [1, -1]) palmette(p.leaf, c[0] + R, c[1], d * Math.PI / 2, R * .62);
  }
  return { ...p, width };
}

// THE FIELD -> { top, under }
export function scrollPaths(L, tile) {
  const cols = L.cols ?? 4, rows = L.rows ?? 4;
  return {
    top: vine(L, tile),
    under: L.under === undefined ? null : vine(L, tile, { dx: tile[0] / cols / 2, dy: tile[1] / rows / 2, thin: L.underThin ?? .65 }),
  };
}

// A MOTIF inside a star: curls round its middle, `fold` of them with their mirrors, in a circle of radius r
export function motifPaths(n, r, { fold, width = .035, leaf = .13, turns = 1 } = {}) {
  const p = emptyPaths(), m = fold ?? (n % 2 ? n : n / 2), Rc = r * .27;
  for (let k = 0; k < m; k++) {
    const t = k * TAU / m;
    for (const side of [1, -1]) {
      const a = t + side * Math.PI / m * .5, c = [Math.cos(a) * r * .55, Math.sin(a) * r * .55];
      curl(p, c, a + Math.PI - side * .3, side, Rc, { turns, width: width * r, leaf: leaf * r, leaves: 3, end: 1.2 });
    }
    palmette(p.leaf, Math.cos(t) * r * .68, Math.sin(t) * r * .68, t, leaf * r * 1.5);
  }
  flower(p.flower, p.heart, 0, 0, r * .2, Math.max(5, Math.min(8, n)));
  return p;
}
