// THE PINNACLE AS ITS KINDS. A Gothic skyline is not one spike a hundred times over: a buttress may end in a plain
// square shaft and spire, an octagonal one with a gablet on every face, crockets climbing its edges, small attendant
// spirelets at the shaft's corners, a statue on the point -- or carry two of them side by side. All of it is the same
// few lines, every size from the shaft's width unless told:
//   the SHAFT, `sides` (4 or 8) faces square to the axes, `w` across the flats and `h` tall, a moulded cap on it;
//   the SPIRE, `s` tall, drawn in from the cap to a point -- or to a small plinth, if a FIGURE stands on it;
//   `gablets` (their height): a gablet on every face at the shaft's head (an octagon's four square faces), its ridge running
//     back into the spire;
//   `crockets` (rows up the spire's edges, an octagon's every other edge): a leaf curling out from the edge;
//   `figure` (its height): a robed statue on the point, a turned silhouette at this scale, which is what a statue
//     seventy metres up comes to from the square (Milan has 2,300 of them: `statue` markers are for the few seen close);
//   `attendants` (their width): a spirelet at each of the shaft's corners, its foot in the shaft;
//   `pair` { d, axis: "x" | "z", scale }: DOUBLED -- two of it `d` apart along `axis`, the second scaled (a mass carrying
//     two spires, Milan's facade buttresses). It stands where it is placed either side of the origin.
// Every piece is a closed solid. Returns the mesh; `top`: the height of the point, or of the figure's head.
const ring = (m, n, r, y, cx, cz, turn) => {
  if (r < 1e-6) return [m.vert(cx, y, cz)];
  return Array.from({ length: n }, (_, k) => { const t = turn + k * 2 * Math.PI / n; return m.vert(cx + r * Math.cos(t), y, cz + r * Math.sin(t)); });
};
// a closed turned stack [[r, y], ...], bottom to top, `n` faces
export function stack(m, prof, n, cx = 0, cz = 0, turn = Math.PI / n) {
  const R = prof.map(([r, y]) => ring(m, n, r, y, cx, cz, turn));
  for (let j = 0; j + 1 < R.length; j++) for (let k = 0; k < n; k++) {
    const a = R[j], b = R[j + 1], a0 = a[k % a.length], a1 = a[(k + 1) % a.length], b0 = b[k % b.length], b1 = b[(k + 1) % b.length];
    m.tri(a0, b0, b1); m.tri(a0, b1, a1);
  }
  const lo = R[0], hi = R[R.length - 1];
  if (lo.length > 1) { const c = m.vert(cx, prof[0][1], cz); for (let k = 0; k < n; k++) m.tri(c, lo[k], lo[(k + 1) % n]); }
  if (hi.length > 1) { const c = m.vert(cx, prof[prof.length - 1][1], cz); for (let k = 0; k < n; k++) m.tri(c, hi[(k + 1) % n], hi[k]); }
  return m;
}
// a closed solid from a list of points and faces, wound outward from its middle
const hull = (m, pts, faces) => {
  const c = [0, 1, 2].map((a) => pts.reduce((s, p) => s + p[a], 0) / pts.length), ids = pts.map((p) => m.vert(p[0], p[1], p[2]));
  for (const f of faces) for (let i = 1; i + 1 < f.length; i++) {
    const [p, q, r] = [pts[f[0]], pts[f[i]], pts[f[i + 1]]], u = [q[0] - p[0], q[1] - p[1], q[2] - p[2]], v = [r[0] - p[0], r[1] - p[1], r[2] - p[2]];
    const nx = u[1] * v[2] - u[2] * v[1], ny = u[2] * v[0] - u[0] * v[2], nz = u[0] * v[1] - u[1] * v[0];
    if (nx * (p[0] - c[0]) + ny * (p[1] - c[1]) + nz * (p[2] - c[2]) >= 0) m.tri(ids[f[0]], ids[f[i + 1]], ids[f[i]]); else m.tri(ids[f[0]], ids[f[i]], ids[f[i + 1]]);
  }
  return m;
};
// a robed figure `H` tall, its feet at (x, y, z): five faces a side is a statue at this distance
export function figureMesh(m, H, x = 0, y = 0, z = 0, r = H * .17) {
  const p = [[.95, 0], [1.0, .76], [.42, .84], [.6, .92], [0, 1.02]];
  return stack(m, p.map(([a, b]) => [a * r, y + b * H]), 5, x, z, 0);
}
function one(m, sp, cx, cz, k) {
  const n = sp.sides ?? 4, w = sp.w * k, h = sp.h * k, s = sp.s * k, R = w / 2 / Math.cos(Math.PI / n), fig = (sp.figure ?? 0) * k;
  const capY = h + w * .22, y0 = capY, rFoot = R * .94, tipR = fig ? Math.max(.1, fig * .1) : 0;
  stack(m, [[R, 0], [R, h], [R * 1.14, h + w * .1], [R * 1.14, h + w * .18], [rFoot, capY], [tipR, y0 + s], ...(fig ? [[tipR * 1.5, y0 + s + .02], [tipR * 1.5, y0 + s + tipR], [0, y0 + s + tipR + .01]] : [])], n, cx, cz);
  const inwards = (t, r, u) => [cx + r * Math.cos(t) + u * Math.cos(t), cz + r * Math.sin(t) + u * Math.sin(t)];
  if (sp.gablets) {
    const g = sp.gablets * k, a = R * Math.cos(Math.PI / n), half = R * Math.sin(Math.PI / n) * 1.02, D = a + w * .04, back = rFoot * Math.cos(Math.PI / n) * Math.max(0, 1 - g / s) * .9;   // (no spire to run back into: to the axis)
    for (let f = 0; f < n; f += n === 8 ? 2 : 1) {          // (an octagon's on every other face, the four square to the axes)
      const t = f * 2 * Math.PI / n, c = Math.cos(t), S = Math.sin(t);          // (the face's outward normal)
      const P = (u, v, y) => [cx + u * c - v * S, y, cz + u * S + v * c];
      hull(m, [P(D, -half, h), P(D, half, h), P(D, 0, h + g), P(back, -half * .9, h + .001), P(back, half * .9, h + .001), P(back, 0, h + g * .98)], [[0, 1, 2], [3, 5, 4], [0, 3, 4, 1], [0, 2, 5, 3], [1, 4, 5, 2]]);
    }
  }
  if (sp.crockets) {
    const rows = sp.crockets, leaf = Math.max(.1, Math.min(.5, s * .045));
    for (let c = 0; c < n; c += n === 8 && !sp.allCrockets ? 2 : 1) {
      const t = Math.PI / n + c * 2 * Math.PI / n, x = Math.cos(t), z = Math.sin(t);
      for (let j = 0; j < rows; j++) {
        const f = (j + .75) / (rows + .5), l = leaf * (1 - f * .6), y = y0 + s * f, r = rFoot + (tipR - rFoot) * f, dr = (rFoot - tipR) / s, q = (e, u) => [cx + (r - dr * e + u) * x, y + e, cz + (r - dr * e + u) * z];
        hull(m, [[...q(-l, -.02)], [...q(l * .9, -.02)], [...q(0, -l * .7)], [...q(l * .5, l * .9)]], [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]);
      }
    }
  }
  if (fig) figureMesh(m, fig, cx, y0 + s + tipR + .005, cz);
  if (sp.attendants) {
    const a = sp.attendants * k, rc = R * .98, h0 = Math.max(0, h - a * 2.2);
    for (let c = 0; c < n; c += n === 8 ? 2 : 1) {
      const t = Math.PI / n + c * 2 * Math.PI / n, x = cx + rc * Math.cos(t), z = cz + rc * Math.sin(t);
      stack(m, [[a * .35, h0], [a * .71, h0 + a * .6], [a * .71, h + a * .5], [0, h + a * 3.4]], 4, x, z, 0);
    }
  }
  return y0 + s + (fig ? tipR + fig : tipR ? tipR : 0);
}
// one of a building's kinds at (x, y, z) in a mesh of many: `kind`'s sizes are shaft widths (a `basilica`'s pinnacleKinds)
export function pinnacleAt(m, kind, w, x, y, z) {
  const q = { vert: (a, b, c) => m.vert(a, b + y, c), tri: m.tri, quad: m.quad }, sc = (v) => (v ? v * w : 0);
  return one(q, { sides: kind.sides ?? 4, w, h: kind.h * w, s: kind.s * w, gablets: sc(kind.gablets), crockets: kind.crockets ?? 0, figure: sc(kind.figure), attendants: sc(kind.attendants) }, x, z, 1) + y;
}
export function pinnacleMesh(m, sp) {
  if (!sp.pair) return { m, top: one(m, sp, 0, 0, 1) };
  const d = sp.pair.d / 2, ax = sp.pair.axis ?? "x", k = sp.pair.scale ?? 1, inner = { ...sp, pair: null };
  const a = one(m, inner, ax === "x" ? -d : 0, ax === "x" ? 0 : -d, 1), b = one(m, inner, ax === "x" ? d : 0, ax === "x" ? 0 : d, k);
  return { m, top: Math.max(a, b) };
}

// THE OPENWORK PARAPET: a pierced stone cresting along a line that may rake and step -- a base rail and a top rail on
// the line, posts between them `panel` apart, a pointed arch in each panel -- and every `every` posts a spirelet standing
// out of it, the small change of a Gothic parapet (the "lace" of Milan's roofs and gables). `run`: [[x, y], ...] in the
// part's own plane, its face at z 0 and `t` thick behind it. Posts fall on the run's own corners, so a step in the line
// has one. A vertical step in the run is a post, not a panel.
export function crestingMesh(m, { run, h, panel = 1.5, t = .3, bar = .12, every = 0, spirelet = null }, barsMesh) {
  const map = (x, y, s) => [x, y, -t * s];
  const base = [], top = [], lines = [];
  let count = 0;
  for (let i = 0; i + 1 < run.length; i++) {
    const [ax, ay] = run[i], [bx, by] = run[i + 1], L = Math.abs(bx - ax), n = L < .01 ? 0 : Math.max(1, Math.round(L / panel));
    for (let j = 0; j < n; j++) {
      const u0 = j / n, u1 = (j + 1) / n, x0 = ax + (bx - ax) * u0, x1 = ax + (bx - ax) * u1, y0 = ay + (by - ay) * u0, y1 = ay + (by - ay) * u1, sp = h * .42, ap = h * .84;
      lines.push({ pts: [[x0, y0 + sp], [(x0 + x1) / 2, (y0 + y1) / 2 + ap], [x1, y1 + sp]] });
      if (every && spirelet && count % every === 0) stack(m, [[spirelet.w * .5, y0 - .02], [spirelet.w * .5, y0 + h + .05], [0, y0 + h + spirelet.s]], 4, x0, -t / 2);
      lines.push({ pts: [[x0, y0], [x0, y0 + h]] });
      count++;
    }
    if (L < .01) lines.push({ pts: [[ax, Math.min(ay, by)], [ax, Math.max(ay, by) + h]] });
  }
  const [lx, ly] = run[run.length - 1];
  lines.push({ pts: [[lx, ly], [lx, ly + h]] });
  if (every && spirelet) stack(m, [[spirelet.w * .5, ly - .02], [spirelet.w * .5, ly + h + .05], [0, ly + h + spirelet.s]], 4, lx, -t / 2);
  for (const [x, y] of run) { base.push([x, y]); top.push([x, y + h]); }
  lines.push({ pts: base }, { pts: top });
  return barsMesh(lines, bar, map, 0, 1, m);
}

// THE OPENWORK SPIRE: the Gothic spire you can see the sky through -- Cologne's, Ulm's, Milan's, Strasbourg's -- not a solid
// cone with ribs drawn on it. `sides` crocketed ribs, `R` to the corners at its foot, draw in over `rise` to `topR`; rings tie
// them every `rows`-th of the way, a lozenge of tracery stands in each panel while the panel has room for one, and a
// `finial` (a cross-flower, turned) closes the top. Bars, not faces: seen from the square it reads as a net against the sky.
export function openSpireMesh(m, { R, rise, sides = 8, rows = 10, rib = R * .07, bar = R * .035, topR = R * .06, crockets = 1, finial = R * .5 }) {
  const rAt = (y) => R + (topR - R) * y / rise, pt = (k, y) => { const t = (k + .5) * 2 * Math.PI / sides, r = rAt(y); return [r * Math.cos(t), y, r * Math.sin(t)]; };
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
  const beam = (a, b, w) => {
    const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], L = Math.hypot(...d), u = d.map((v) => v / L);
    let s = [u[2], 0, -u[0]], sl = Math.hypot(...s); if (sl < 1e-3) { s = [1, 0, 0]; sl = 1; } s = s.map((v) => v / sl);
    const t = [u[1] * s[2] - u[2] * s[1], u[2] * s[0] - u[0] * s[2], u[0] * s[1] - u[1] * s[0]], h = w / 2;
    const c = [[-1, -1], [1, -1], [1, 1], [-1, 1]], P = [];
    for (const e of [a, b]) for (const [i, j] of c) P.push([e[0] + (s[0] * i + t[0] * j) * h, e[1] + (s[1] * i + t[1] * j) * h, e[2] + (s[2] * i + t[2] * j) * h]);
    hull(m, P, [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]);        // (no ends: every bar's end is buried in the next)
  };
  for (let j = 0; j < rows; j++) {
    const y0 = rise * j / rows, y1 = rise * (j + 1) / rows, ym = (y0 + y1) / 2;
    for (let k = 0; k < sides; k++) {
      beam(pt(k, y0), pt(k, y1), rib); beam(pt(k, y0), pt(k + 1, y0), j ? bar : rib);
      const room = 2 * rAt(ym) * Math.sin(Math.PI / sides);
      if (room > bar * 7) {
        const lo = mid(pt(k, y0), pt(k + 1, y0)), hi = mid(pt(k, y1), pt(k + 1, y1)), l = mid(pt(k, ym), mid(pt(k, ym), pt(k + 1, ym))), r = mid(pt(k + 1, ym), mid(pt(k, ym), pt(k + 1, ym)));
        beam(lo, r, bar); beam(r, hi, bar); beam(hi, l, bar); beam(l, lo, bar);
      }
      if (crockets) {                                         // (a leaf on the rib, at each ring)
        const c = pt(k, ym), t = (k + .5) * 2 * Math.PI / sides, o = rib * 1.3, x = Math.cos(t), z = Math.sin(t), l = (y1 - y0) * .18;
        hull(m, [[c[0], c[1] - l, c[2]], [c[0], c[1] + l, c[2]], [c[0] + x * o, c[1] + l * 1.2, c[2] + z * o], [c[0] - z * rib, c[1], c[2] + x * rib]], [[0, 1, 2], [0, 2, 3], [1, 3, 2], [0, 3, 1]]);
      }
    }
  }
  if (finial > 0) stack(m, [[topR * 1.1, rise - rise / rows * .4], [topR * 1.1, rise], [topR * 2.8, rise + finial * .3], [topR * .8, rise + finial * .5], [topR * 1.8, rise + finial * .62], [topR * .5, rise + finial * .78], [0, rise + finial]], 6);
  return { m, top: rise + finial };
}
