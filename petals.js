// PETALS (2026-10-06): a WHORL of thin curved blades round the part's y axis -- a flower's petals, its sepals, a leaf
// or two -- as one primitive of the items language (items.js part type `petals`, drawn from both sides like a sail).
// Each blade leaves the axis at `r0`, rising at `cup` degrees over the horizontal (0 a flat open disc, 60 a goblet,
// 85 a closed bud) and bending by `curl` more over its length (+ curling up and in, - reflexed back), cupped ACROSS its
// width by `cupped` (its edges raised: a spoon), its outline the `shape`'s. `n` blades, in `layers` whorls (each
// turned half a step from the one outside it, `shrink` smaller) -- a rose's or a camellia's many petals.
//
//   n, layers, shrink, r0, length, width (the blade's widest, its whole width), cup, curl, cupped, twist (each blade
//   turned about its own midrib, degrees: a pinwheel), droop (the outer whorl's extra fall, degrees), spread (degrees
//   of the circle the whorl fills: 360 all round, less a fan -- an iris's falls, a leaf pair), phase (degrees)
//   shape: "round" | "oval" | "pointed" | "strap" (long, even) | "heart" (a notched tip) | "fringed" (a toothed tip) |
//          "spoon" (narrow at the base, broad at the tip) | "lance" (a leaf: widest a third out, a long point)
//   rows / cols: the blade's quads along it and across it (the detail: rows 4, cols 2 -- 16 triangles a side)
//   materials: `material` the blade (default "petal"); `throat` (the base's share in the "throat" material: a
//   poppy's black blotch, a lily's yellow heart) and `band` (the tip's share in "tips": a picotee's edge)
const DEG = Math.PI / 180;
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };

// the blade's half-width at s (0 its base .. 1 its tip), a share of the widest; and how far the tip's middle is pulled back
function widthAt(shape, s) {
  switch (shape) {
    case "strap": return s < .12 ? .55 + s / .12 * .45 : s > .82 ? Math.sqrt(Math.max(0, 1 - ((s - .82) / .18) ** 2)) : 1;
    case "pointed": return Math.sin(Math.PI * Math.min(1, s * 1.05)) ** .8 * (s < .45 ? 1 : 1 - .15 * (s - .45));
    case "lance": return s < .33 ? Math.sin(s / .33 * Math.PI / 2) ** .7 : Math.max(0, 1 - (s - .33) / .67) ** .9;
    case "spoon": return s < .9 ? .25 + .75 * Math.sin(Math.min(1, s / .8) * Math.PI / 2) : Math.sqrt(Math.max(0, 1 - ((s - .9) / .1) ** 2)) * .95 + .05;
    case "heart": case "fringed": return s < .8 ? .3 + .7 * Math.sin(Math.min(1, s / .6) * Math.PI / 2) : .3 + .7 * Math.sqrt(Math.max(0, 1 - ((s - .8) / .25) ** 2));
    case "oval": return Math.sqrt(Math.max(0, 1 - ((s - .5) / .5) ** 2));
    default: return s < .5 ? .25 + .75 * Math.sin(s / .5 * Math.PI / 2) : Math.sqrt(Math.max(0, 1 - ((s - .5) / .52) ** 2));   // round: a broad tip
  }
}

export function petalsGeometry(p, P, emitFor) {
  const n = Math.max(1, Math.round(p.n ?? 5)), layers = Math.max(1, Math.round(p.layers ?? 1)), shrink = p.shrink ?? .8;
  const r0 = p.r0 ?? 0, L0 = p.length ?? .03, W0 = p.width ?? .015, cup0 = p.cup ?? 15, curl = p.curl ?? 0, cupped = p.cupped ?? .2;
  const shape = p.shape ?? "round", twist = (p.twist ?? 0) * DEG, spread = (p.spread ?? 360) * DEG, phase = (p.phase ?? 0) * DEG;
  const rows = Math.max(2, Math.round((p.rows ?? 4) * Math.min(1.5, Math.max(.5, P.detail ?? 1)))), cols = Math.max(1, Math.round(p.cols ?? 2));
  const throat = p.throat ?? 0, band = p.band ?? 0, droop = p.droop ?? 0;
  const blade = emitFor(p.material ?? "petal"), thr = throat > 0 ? emitFor(p.throatMaterial ?? "throat") : null, tip = band > 0 ? emitFor(p.tips ?? "tips") : null;
  // the rows' stations along the blade: evenly, with a station at the throat's and the band's edges
  const st = new Set(Array.from({ length: rows + 1 }, (_, i) => i / rows));
  if (throat > 0 && throat < 1) st.add(throat);
  if (band > 0 && band < 1) st.add(1 - band);
  const S = [...st].sort((a, b) => a - b);
  for (let ly = layers - 1; ly >= 0; ly--) {   // (outer whorl first: the inner ones over it)
    const k = Math.pow(shrink, layers - 1 - ly), L = L0 * k, W = W0 * k, cup = (cup0 + (layers - 1 - ly) * (p.cupStep ?? 12)) * DEG;
    const off = (ly % 2) * .5;
    for (let i = 0; i < n; i++) {
      const a = phase + (spread >= 2 * Math.PI - 1e-6 ? (i + off) / n * spread : (n === 1 ? 0 : (i / (n - 1) - .5) * spread));
      const u = [Math.cos(a), 0, Math.sin(a)], v = [-Math.sin(a), 0, Math.cos(a)];
      const dr = (layers === 1 || ly === 0 ? droop : 0) * DEG;
      // the midrib: integrated along s from the base, its angle cup + curl s - droop
      let rr = r0, yy = 0;
      const steps = 24;
      const at = (s) => { const th = cup + (curl * DEG) * s - dr * s; return th; };
      const pts = [[r0, 0]];
      for (let q = 1; q <= steps; q++) { const th = at((q - .5) / steps); rr += L / steps * Math.cos(th); yy += L / steps * Math.sin(th); pts.push([rr, yy]); }
      const midAt = (s) => { const f = s * steps, q = Math.min(steps - 1, Math.floor(f)), t = f - q; return [pts[q][0] + (pts[q + 1][0] - pts[q][0]) * t, pts[q][1] + (pts[q + 1][1] - pts[q][1]) * t]; };
      const P3 = (s, t) => {   // the blade's point at s along, t across (-1 .. 1)
        const [r, y] = midAt(s), th = at(s), w = widthAt(shape, s) * W / 2;
        const tt = t;
        const nrm = [-Math.sin(th) * u[0], Math.cos(th), -Math.sin(th) * u[2]];   // the blade's own normal (up off its face)
        const ct = Math.cos(twist * s), sn = Math.sin(twist * s);
        const across = [v[0] * ct + nrm[0] * sn, v[1] * ct + nrm[1] * sn, v[2] * ct + nrm[2] * sn];
        const lift = cupped * w * tt * tt;
        let x = u[0] * r + across[0] * w * tt + nrm[0] * lift, yv = y + across[1] * w * tt + nrm[1] * lift, z = u[2] * r + across[2] * w * tt + nrm[2] * lift;
        // a notched tip (heart): the middle pulled back; a fringed tip: teeth
        if ((shape === "heart" || shape === "fringed") && s > .78) {
          const pull = shape === "heart" ? .14 * (1 - Math.abs(tt)) ** 2 : .08 * (.5 + .5 * Math.cos(tt * Math.PI * 3));
          const back = pull * L * (s - .78) / .22;
          const du = Math.cos(th); x -= u[0] * back * du; z -= u[2] * back * du; yv -= Math.sin(th) * back;
        }
        return [x, yv, z];
      };
      const C = Math.max(cols, shape === "fringed" ? 2 : cols);
      const grid = S.map((s) => Array.from({ length: C + 1 }, (_, c) => P3(s, -1 + 2 * c / C)));   // (cols quads across the whole blade)
      const nrmAt = (ri, ci) => {
        const a = grid[Math.max(0, ri - 1)][ci], b = grid[Math.min(S.length - 1, ri + 1)][ci], c = grid[ri][Math.max(0, ci - 1)], d = grid[ri][Math.min(C, ci + 1)];
        let nn = norm(cross(sub(d, c), sub(b, a)));
        const up = [-Math.sin(at(S[ri])) * u[0], Math.cos(at(S[ri])), -Math.sin(at(S[ri])) * u[2]];
        if (nn[0] * up[0] + nn[1] * up[1] + nn[2] * up[2] < 0) nn = nn.map((x) => -x);
        return Math.hypot(...nn) > .5 ? nn : up;
      };
      for (let ri = 1; ri < S.length; ri++) {
        const sm = (S[ri - 1] + S[ri]) / 2, e = thr && sm < throat ? thr : tip && sm > 1 - band ? tip : blade;
        const V = (r2, c2) => e.vert(grid[r2][c2], nrmAt(r2, c2), [(-1 + 2 * c2 / C), S[r2]]);
        const tipRow = ri === S.length - 1 && widthAt(shape, 1) < .02;
        for (let ci = 0; ci < C; ci++) {
          const a = V(ri - 1, ci), b = V(ri - 1, ci + 1), c = V(ri, ci + 1), d = V(ri, ci);
          // (wound so its face is the blade's upper side; the item engine adds the back)
          if (tipRow) e.tri(a, c, b); else { e.tri(a, c, b); e.tri(a, d, c); }
        }
      }
    }
  }
}
