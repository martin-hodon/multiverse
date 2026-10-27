// THE APPLIED ORDER: pilasters on a facade carrying an entablature -- the classical wall's own grammar, set out as
// Vignola set out every order: from the HEIGHT it has to fill, never by eye.
//   The storey (or the storeys, for a giant order) is divided into MODULES -- the column's radius -- the column taking
//   14 of them (Tuscan), 16 (Doric), 18 (Ionic) or 20 (Corinthian) and the entablature a quarter of that; so the
//   height gives the module and the module gives everything: the pilaster's width (two modules), its base and capital
//   (ORDERS, in the same module), the architrave, frieze and cornice and how far the cornice reaches.
//   The PILASTERS stand on the piers between the openings of their storey -- the middle of each pier, where one is wide
//   enough to take a capital clear of both windows -- and at the face's ends: doubled at a square corner, one on each
//   face, but FOLDED round a shallow one (a polygon's: an octagon's, a rotunda's), one pilaster bent over the arris;
//   the ENTABLATURE runs over them round the whole building as one moulding (a course: courses.js mitres it round every
//   corner), its architrave flush with the pilasters' faces, so they carry it.
// `orders: [{ tier, kind, span }]` on a wall or an enclosure: `tier` the storey it stands in (counted from 0), `span` how
// many storeys it rises through (a giant order: no string course between them), `kind` tuscan | doric | ionic |
// corinthian, `ends` (false: none at the faces' ends), `proj` the pilasters' projection in modules (.5).

// the column and its entablature in modules, and the entablature's three members (Vignola)
export const VIGNOLA = {
  tuscan:     { col: 14, arch: 1,    frieze: 1.17, cornice: 1.33 },
  doric:      { col: 16, arch: 1,    frieze: 1.5,  cornice: 1.5 },
  ionic:      { col: 18, arch: 1.25, frieze: 1.5,  cornice: 1.75 },
  corinthian: { col: 20, arch: 1.5,  frieze: 1.5,  cornice: 2 },
};

// AN ORDER'S SIZES for a height `H` from the pilasters' foot to the entablature's top: { m, col, ent, p, profile }, the
// profile the entablature's section in metres ([out, up], from the face at its foot out and up round to the face at
// its top), the architrave standing as far out as the pilasters (`p`), the cornice reaching out as far as it is tall
export function orderSize(kind, O, H, spec = {}) {
  const V = VIGNOLA[kind];
  if (!V) throw new Error(`order "${kind}" is not one of ${Object.keys(VIGNOLA).join(", ")}`);
  const entM = V.arch + V.frieze + V.cornice, m = H / (V.col + entM);
  const col = V.col * m, ent = entM * m, p = (spec.proj ?? .5) * m;
  const a = V.arch * m, f = V.frieze * m, c = V.cornice * m;
  // the architrave in two fasciae, the taenia over it; the frieze a hair behind; the cornice's bed moulding, the corona
  // with its drip, the cyma
  const profile = [[0, 0], [p, 0], [p, a * .45], [p + m * .06, a * .5], [p + m * .06, a * .85], [p + m * .14, a * .88], [p + m * .14, a],
    [p - m * .02, a], [p - m * .02, a + f],
    [p + c * .18, a + f + c * .12], [p + c * .25, a + f + c * .3], [p + c * .8, a + f + c * .42], [p + c, a + f + c * .45], [p + c, a + f + c * .72],
    [p + c * .85, a + f + c * .8], [p + c * .55, a + f + c], [0, a + f + c]];
  return { m, col, ent, p, profile, O };
}

// THE PILASTERS of one face: their centres along it, from its storey's openings (`ops`: laid out, x0/x1), the face
// `L` long; `clear` spans [x0, x1] where none may stand (a neighbour's block against it). `ends` [start, end] (or one
// for both): true a pilaster in from that corner, "fold" one FOLDED round it (half on this face, half on the next --
// a shallow corner of a polygon, where two side by side would crowd each other: pilasterMesh draws this half), false
// none
export function pilasterSpots(L, ops, s, { ends = true, clear = [] } = {}) {
  const half = s.m * Math.max(s.O.capR, s.O.baseR), reach = s.p + s.m * (Math.max(s.O.capR, s.O.baseR) - 1);
  const xs = ops.map((o) => [o.x0, o.x1]).sort((u, v) => u[0] - v[0]);
  const [e0, e1] = Array.isArray(ends) ? ends : [ends, ends];
  const free = (x, h) => clear.every(([c0, c1]) => x + h < c0 || x - h > c1);
  const out = [], folds = [];
  for (let i = 0; i + 1 < xs.length; i++) {
    const a = xs[i][1], b = xs[i + 1][0];
    if (b - a > 2 * half + .1) out.push((a + b) / 2);
  }
  // (in from the corner by its own half and by what a pilaster on the next face reaches out: on an inner corner that
  //  one stands across this face's end)
  const e = half + reach + .02, first = xs.length ? xs[0][0] : L, last = xs.length ? xs[xs.length - 1][1] : 0;
  if (e0 === "fold") { if (first - .05 >= half && free(0, half)) folds.push(0); }
  else if (e0 && first - .05 >= e + half && (xs.length || L > 2 * e + .1)) out.push(e);
  if (e1 === "fold") { if (L - last - .05 >= half && free(L, half)) folds.push(L); }
  else if (e1 && L - last - .05 >= e + half && (xs.length || L > 2 * e + .1)) out.push(L - e);
  return { spots: out.filter((x) => free(x, half)).sort((u, v) => u - v), folds };
}

// one pilaster at `x` along the segment (A, e: its start and direction; n: its outward normal), from `y0` -- base,
// shaft, capital (echinus or bell, and abacus), each a block standing out of the wall's face
// (`fold` -1 / 1: only its half after / before `x`, a corner of the face's line, its end there mitred by `k` -- the
//  tangent of half the corner's turn, negative on an inner corner -- to meet the next face's half in one pilaster)
// (`yb`: the foot of the moulding it stands on -- the plinth, a string course -- which BREAKS FORWARD under it, a block
//  as wide and as deep as its base: a base reaching out further than the course would stand on air)
export function pilasterMesh(m, A, e, n, x, y0, s, fold = 0, k = 0, yb = y0) {
  const { m: r, col, p, O } = s, bh = r * Math.max(O.base, .5), ch = r * O.cap, abH = ch * O.abacus;
  const block = (hw, d, ya, yb) => {
    const ua = fold > 0 ? 0 : -hw, ub = fold < 0 ? 0 : hw;
    const P = (u, o, y) => {
      const along = x + u + (fold > 0 && u === ua ? -o * k : fold < 0 && u === ub ? o * k : 0);
      return [A[0] + e[0] * along + n[0] * o, y, A[1] + e[1] * along + n[1] * o];
    };
    const c = [P(ua, -.05, ya), P(ub, -.05, ya), P(ub, d, ya), P(ua, d, ya), P(ua, -.05, yb), P(ub, -.05, yb), P(ub, d, yb), P(ua, d, yb)];
    const id = c.map((v) => m.vert(...v));
    const mid = c.reduce((s, v) => [s[0] + v[0] / 8, s[1] + v[1] / 8, s[2] + v[2] / 8], [0, 0, 0]);
    for (const q of [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]) {
      // (a folded half's mitred end meets its other half: no face there)
      if (fold && (fold > 0 ? q[0] === 3 && q[1] === 7 : q[0] === 1 && q[1] === 5)) continue;
      const [a, b, , d] = q.map((k) => c[k]), u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], v = [d[0] - a[0], d[1] - a[1], d[2] - a[2]];
      const nn = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
      const fc = q.reduce((s, k) => [s[0] + c[k][0] / 4, s[1] + c[k][1] / 4, s[2] + c[k][2] / 4], [0, 0, 0]);
      const out = nn[0] * (fc[0] - mid[0]) + nn[1] * (fc[1] - mid[1]) + nn[2] * (fc[2] - mid[2]) >= 0;
      if (out) m.quad(...q.map((k) => id[k])); else m.quad(...q.map((k) => id[k]).reverse());
    }
  };
  const grow = (k) => p + r * (k - 1);           // (a member k modules wide stands out as much more as it is wider)
  if (yb < y0 - 1e-3) block(r * O.baseR + .04, grow(O.baseR) + .04, yb, y0);
  block(r * O.baseR, grow(O.baseR), y0, y0 + bh);
  block(r, p, y0 + bh, y0 + col - ch);
  block(r * (1 + O.capR) / 2, grow((1 + O.capR) / 2), y0 + col - ch, y0 + col - abH);
  block(r * O.capR, grow(O.capR), y0 + col - abH, y0 + col);
  return m;
}
