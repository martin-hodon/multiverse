// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- the slopes: the landslide, the couloirs, and SETTLE -- every
// column as steep as its rock stands (and badlands). Each stage takes the scene so far, `c`, and adds what it makes to
// it; landscape.js runs them in order.
import { clamp, noise, fbm, rng, N8 } from "./core.js";
import { SCREE_ANGLE } from "./presets.js";

// SETTLE's sweeps (a function of its own: the hot loop, kept small enough for the JIT to optimise -- inside
// makeLandscape it would not be). Each sweep: every rock column no higher above its lowest neighbour than its bed
// stands (`tanR` of the bed at its surface, times its joints' factor `JT`); what breaks off becomes scree, which runs
// down while it lies steeper than `tanS`; what lands in the stream's bed (`carved`) is carried away.
function relax(N, dx, rock, soil, carved, DAT, base, tanR, JT, tanS, ITER) {
  const n = N * N, dist = N8.map(([a, b]) => Math.hypot(a, b) * dx), nb = base.length;
  const OI = N8.map(([a]) => a), OJ = N8.map(([, b]) => b);
  for (let it = 0; it < ITER; it++) {
    const rev = it & 1;
    for (let kk = 0; kk < n; kk++) {
      const k = rev ? n - 1 - kk : kk, i = k % N, j = (k / N) | 0;
      // 1. the rock: no higher above its lowest neighbour than its bed stands
      const depth = DAT[k] - rock[k] + .05;
      let bk = 0; if (depth >= 0) for (let b = nb - 1; b > 0; b--) if (depth >= base[b]) { bk = b; break; }
      const t = tanR[bk] * JT[bk][k];
      let lim = Infinity;
      for (let q = 0; q < 8; q++) {
        const ii = i + OI[q], jj = j + OJ[q];
        if (ii < 0 || jj < 0 || ii >= N || jj >= N) continue;
        const m = jj * N + ii, L = rock[m] + soil[m] * .5 + dist[q] * t;   // (scree against a wall props it a little)
        if (L < lim) lim = L;
      }
      if (rock[k] > lim + .02) { const drop = Math.min(rock[k] - lim, .6); rock[k] -= drop; soil[k] += drop * 1.25; }   // (broken rock takes more room)
      // 2. the scree: down the steepest way while it lies steeper than SCREE_ANGLE
      if (soil[k] > 0) {
        const h = rock[k] + soil[k];
        let best = -1, bs = 0;
        for (let q = 0; q < 8; q++) {
          const ii = i + OI[q], jj = j + OJ[q];
          if (ii < 0 || jj < 0 || ii >= N || jj >= N) continue;
          const m = jj * N + ii, sl = (h - rock[m] - soil[m]) / dist[q];
          if (sl > bs) { bs = sl; best = q; }
        }
        if (best >= 0 && bs > tanS) {
          const m = (j + OJ[best]) * N + i + OI[best], mv = Math.min(soil[k], (bs - tanS) * dist[best] * .5);
          soil[k] -= mv;
          if (!carved[m]) soil[m] += mv;   // (else the stream carries it away)
        }
      }
    }
  }
}

// GULLIES (badlands): the rain that runs off a bare soft bed cuts it. Each sweep the water is gathered down the steepest
// way (the cells highest first, each handing on all it has), and every cell is lowered by what that water and its slope
// can take (stream power: K * sqrt(A) * S) -- scree first, then the rock where its bed gives (`erod`, per bed) -- never
// below where its water goes. Where much gathers it cuts most: the rills join into gullies, branching up the slope.
// (Module level, as relax is: the JIT optimises it here)
function gully(N, dx, rock, soil, carved, DAT, base, erod, K, ITER) {
  const n = N * N, dist = N8.map(([a, b]) => Math.hypot(a, b) * dx), nb = base.length;
  const OI = N8.map(([a]) => a), OJ = N8.map(([, b]) => b);
  const ord = new Int32Array(n), A = new Float32Array(n), to = new Int32Array(n), h = new Float32Array(n), S = new Float32Array(n);
  for (let it = 0; it < ITER; it++) {
    for (let k = 0; k < n; k++) { h[k] = rock[k] + soil[k]; ord[k] = k; }
    ord.sort((a, b) => h[b] - h[a]);
    A.fill(dx * dx);
    for (let o = 0; o < n; o++) {
      const k = ord[o], i = k % N, j = (k / N) | 0;
      let best = -1, bs = 0;
      for (let q = 0; q < 8; q++) {
        const ii = i + OI[q], jj = j + OJ[q];
        if (ii < 0 || jj < 0 || ii >= N || jj >= N) continue;
        const m = jj * N + ii, sl = (h[k] - h[m]) / dist[q];
        if (sl > bs) { bs = sl; best = m; }
      }
      to[k] = best; S[k] = bs;
      if (best >= 0) A[best] += A[k];
    }
    for (let k = 0; k < n; k++) {
      const m = to[k]; if (m < 0 || carved[k] || S[k] < .2 || S[k] > 1) continue;   // (on a flat it spreads, it does not cut; a wall's foot is the wall's)
      const depth = DAT[k] - rock[k] + .05;
      let bk = 0; if (depth >= 0) for (let b = nb - 1; b > 0; b--) if (depth >= base[b]) { bk = b; break; }
      if (!erod[bk]) continue;   // (where the bed under gives: a hard bed's scree apron stays)
      const e = Math.min(.25, K * (soil[k] > .05 ? 1 : erod[bk]) * Math.sqrt(A[k]) * S[k], h[k] - h[m] - .02);
      if (e <= 0) continue;
      if (soil[k] > .05) soil[k] -= Math.min(soil[k], e); else rock[k] -= e;   // (the scree first, down to the rock)
    }
  }
}

export function landslide(c) {
  const { clim, coast, cone, cu, dx, F, fanBase, FAULT, H, half, lake, n, N, notes, outliers, S, scarp2U, scarpU, seed,
    size, softK, STEP2, streamV, su, toXY, trib, U, V } = c;
  // a LANDSLIDE: where it is wet, a soft bed under the cap gives -- soaked, it slips, and the scarp's edge goes with it:
  // a horseshoe SCAR bitten into the upland (its headwall the beds bare), the slumped mass in it lower and tilted back
  // against the headwall (a ridge where the block rotated, a sag behind it that may hold a pond), and out over the
  // land below a hummocky LOBE of the debris, its toe steep. The slip surface the rock; what slid on it loose (it
  // settles as scree). Its own random numbers
  let slide = null;
  (() => {
  if (F.landslide === false || softK < 0 || FAULT || clim.rain < 700) return;
  const RD = rng(seed * 101 + 37); if (RD() >= (F.landslide?.chance ?? .75)) return;
  const at = (u, v) => { const [x, y] = toXY(u, v); return H[clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1)]; };
  for (let t = 0; t < 40 && !slide; t++) {
    const vc = (RD() - .5) * size * .8, Wl = 18 + RD() * 12, Ds = 22 + RD() * 10, Lb = 30 + RD() * 25, Dl = 4 + RD() * 4, Tl = 3 + RD() * 2, us = scarpU(vc);
    const [cx, cy] = toXY(us, vc), uEnd = us + Lb + 4, [ex, ey] = toXY(uEnd, vc);
    if (Math.min(cx, cy, ex, ey) < Wl + 6 || Math.max(cx, cy, ex, ey) > size - Wl - 6) continue;
    let near = false; for (let u = us - Ds - 10; u < uEnd && !near; u += 4) near = Math.abs(vc - streamV(u)) < Wl * 1.6 + 18;   // (clear of the stream, and its gorge)
    if (near) continue;
    if ((STEP2 && uEnd > scarp2U(vc) - 8) || (coast && uEnd > coast.line(vc) - 10) || uEnd > half - 8) continue;
    if (lake && lake.r * lake.dist(us - Ds, vc) < lake.r + Ds + Wl * .5) continue;
    if (outliers.some((o) => Math.hypot(o.u - (us + Lb * .5), o.v - vc) < o.r + Lb * .5 + Wl * .5)) continue;
    if (cone && Math.hypot(cone.x - (cx + ex) / 2, cone.y - (cy + ey) / 2) < cone.Rb + Lb * .5 + Wl) continue;
    if (trib && trib.way.some(([x, y]) => Math.hypot(x - cx, y - cy) < Wl + Ds + 6)) continue;
    const zU = at(us - Ds - 8, vc), zL = at(us + 14, vc); if (zU - zL < 6) continue;
    for (let k = 0; k < n; k++) {
      const u = U[k], v = V[k], a = v - vc, b = u - scarpU(v); if (Math.abs(a) > Wl * 1.6 || b < -Ds - 2 || b > Lb + 2) continue;
      const x = (k % N) * dx, y = ((k / N) | 0) * dx, hum = fbm(x / 9, y / 9, seed + 103, 3);
      if (b < 0) {   // (the scar)
        const e = Math.hypot(a / Wl, b / Ds) * (1 + .08 * fbm(Math.atan2(b, a) * 3, 4.4, seed + 105, 2)); if (e >= 1) continue;
        const slip = zL - 1 + (zU - zL + 1) * e ** 3;
        const z = zL + Tl + (zU - Dl - zL - Tl) * e ** 2 + 2.4 * Math.exp(-(((e - .72) / .07) ** 2)) - 1.6 * Math.exp(-(((e - .87) / .045) ** 2)) + (1 - e) * hum;
        if (z < H[k]) { H[k] = Math.max(z, slip); fanBase[k] = Math.min(fanBase[k], slip); }
      } else {   // (the lobe: spreading as it goes, its toe steep)
        const Wb = Wl * (1 + .35 * b / Lb), side = 1 - (a / Wb) ** 2, q = b / (Lb * (1 + .12 * fbm(a / 12, 6.6, seed + 107, 2)));
        if (q >= 1 || side <= 0) continue;
        // (a lens, thinning to its edges; ridged across where the front pushed and stopped, and hummocky)
        const z = zL + (Tl * (1 - q * q) ** .7 + (.9 * Math.sin(q * 17 + 2 * fbm(a / 15, 8.8, seed + 109, 2)) * (1 - q) + 1.4 * hum) * Math.min(1, side * 2)) * side ** .6;
        if (z > H[k]) H[k] = z;
      }
    }
    const [sx, sy] = toXY(us - Ds * .6, vc);
    slide = { x: sx, y: sy, u: us, v: vc, Wl, Ds, Lb, toe: [ex, ey], out: [cu, su] };
    notes.push(`landslide: the scarp's edge slipped on the soaked ${S.beds[softK].name} -- a scar ${Math.round(Wl * 2)} m across bitten ${Math.round(Ds)} m into the upland, ` +
      `the slumped mass tilted back against its headwall, and a lobe of the debris ${Math.round(Lb)} m out over the land below`);
  }
  })();
  Object.assign(c, { slide });
}

export function couloirs(c) {
  const { chanW, cirque, clim, coast, cone, dx, F, fanBase, fans, gorgeL, gorgeW, H, half, lake, n, N, notes, outliers,
    rockGlacier, scarp2U, scarpU, sCross, seed, size, slide, STEP2, streamV, toXY, U, upAt, V } = c;
  let { su, T } = c;
  // COULOIRS: where it freezes and thaws, the water in the cliff's joints wedges them open -- where a joint runs back
  // into the cap the frost works it into a chute, wide at its head and narrow where it comes out, and all it breaks off
  // pours down it onto a CONE of scree under its mouth, the cones side by side along the foot, the cliff between them
  // buttresses. (The chute cut in the rock before SETTLE; the cone laid on what it left, after: a sheet of scree spread
  // down the slope from the mouth, thickest along its middle.) Its own random numbers
  const couloirs = [];
  (() => {
    if (F.couloirs === false || clim.temp >= 4) return;
    const RC = rng(seed * 241 + 3), sp = 22 + RC() * 12, gw = gorgeL > 0 ? gorgeW(sCross) / 2 : chanW * 3;
    for (let vq = -half * 1.4 + RC() * sp; vq < half * 1.4; vq += sp * (.7 + .6 * RC())) {
      const su = scarpU(vq), Lc = 12 + RC() * 10, wt = 5 + RC() * 4, [mx, my] = toXY(su + 2, vq), [hx, hy] = toXY(su - Lc, vq);
      if (Math.min(mx, my, hx, hy) < 16 || Math.max(mx, my, hx, hy) > size - 16) continue;
      const kL = Math.round(my / dx) * N + Math.round(mx / dx), ztop = upAt(hx, hy, su - Lc), zlow = H[Math.min(n - 1, kL + 0)];
      const ch = ztop - zlow; if (ch < 6) continue;
      const T = clamp(ch * (.2 + RC() * .1), 2.5, 5), rc = ch * (1 + RC() * .4) + 8;
      let ok = Math.abs(vq - streamV(su)) > gw + wt + 10 && (!coast || coast.line(vq) - su > rc + 14) && (!STEP2 || scarp2U(vq) - su > rc + 10);
      ok &&= !rockGlacier || Math.abs(vq - rockGlacier.v) > rockGlacier.W / 2 + rc + 4;
      ok &&= !slide || Math.abs(vq - slide.v) > slide.Wl + rc;
      ok &&= !outliers.some((o) => Math.hypot(o.u - su, o.v - vq) < o.r + rc + 6) && !fans.some((f) => Math.hypot(f.x - mx, f.y - my) < f.r + rc);
      ok &&= !cone || Math.hypot(cone.x - mx, cone.y - my) > cone.Rb + rc + 6;
      ok &&= !lake || lake.dist(su - Lc, vq) > 1.4;
      ok &&= !couloirs.some((c) => Math.abs(c.v - vq) < (c.r + rc) * .6);
      ok &&= !cirque || Math.abs(cirque.v - vq) > cirque.r * 1.2 + wt + 4;
      if (!ok) continue;
      const lean = (RC() - .5) * .5;   // (a joint runs back into the cap a little aslant)
      const R0 = Math.ceil((Lc + rc + 6) / dx), [ox, oy] = toXY(su, vq), i0 = Math.round(ox / dx), j0 = Math.round(oy / dx);
      for (let j = Math.max(0, j0 - R0); j <= Math.min(N - 1, j0 + R0); j++) for (let i = Math.max(0, i0 - R0); i <= Math.min(N - 1, i0 + R0); i++) {
        const k = j * N + i, u = U[k], b = su - u, dv = V[k] - vq - lean * Math.max(0, b), x = i * dx, y = j * dx;
        // the chute: from its head back in the cap down to the foot, V-shaped across, widening up it
        if (b > -3 && b < Lc) {
          const hw = 1.4 + (wt - 1.4) * clamp(b / Lc, 0, 1) ** .8, a = Math.abs(dv) / hw;
          if (a < 1) {
            const zf = zlow + ch * clamp((b + 2) / (Lc + 2), 0, 1) ** 1.25 + .4 * noise(x / 3, y / 3, seed + 245);
            const z = zf + (H[k] - zf) * a ** 1.6; if (z < H[k]) { H[k] = z; fanBase[k] = Math.min(fanBase[k], z); }
          }
        }
      }
      couloirs.push({ u: su, v: vq, x: mx, y: my, L: Lc, T, r: rc });
    }
    if (couloirs.length) notes.push(`couloirs: ${couloirs.length} chutes the frost wedged back into the cliff along its joints, a cone of scree under each, ${Math.round(Math.min(...couloirs.map((c) => c.r)))}-${Math.round(Math.max(...couloirs.map((c) => c.r)))} m down the slope -- the cliff between them buttresses`);
  })();
  Object.assign(c, { couloirs, su, T });
}

export function settle(c) {
  const { carved, clim, coneT, couloirs, dikeM, dx, F, fanBase, H, mark, n, N, notes, R, ravines, S, seed, soil, T, U, V } = c;
  // SETTLE: no column steeper than its rock stands; what is steeper falls as scree, and scree lies at SCREE_ANGLE.
  // The bed under a column is the bed at its rock's surface (the scree is on top of it, `soil`)
  const rock = new Float32Array(H);   // bedrock surface (H = rock + soil)
  (() => {   // (a fan's gravel is loose: scree on the rock, not rock)
  for (let k = 0; k < n; k++) { const f = H[k] - fanBase[k]; if (f > 0) { rock[k] -= f; soil[k] += f; } }
  for (let k = 0; k < n; k++) if (coneT[k] > 0) { rock[k] -= coneT[k]; soil[k] += coneT[k]; }   // (and a cone's cinders)
  })();
  const tanR = S.beds.map((b) => Math.tan(b.angle * Math.PI / 180)), tanS = Math.tan(SCREE_ANGLE * Math.PI / 180);
  const dist = N8.map(([a, b]) => Math.hypot(a, b) * dx);
  const DAT = new Float32Array(n);   // (the stack's datum under each cell, worked out once)
  (() => {
  for (let k = 0; k < n; k++) DAT[k] = S.datum((k % N) * dx, ((k / N) | 0) * dx);
  })();
  const bedK = (k) => { const depth = DAT[k] - rock[k] + .05; if (depth < 0) return 0; for (let b = S.beds.length - 1; b > 0; b--) if (depth >= S.base[b]) return b; return 0; };
  // the joints: two sets square to each other (the region's stress set them, the same through every bed) -- three at 60 deg
  // in a columnar rock; near one a wall stands less steep (it has opened: blocks fall out of it), and every wall a little
  // rougher than its rock's angle (`JT`: each bed's factor on its tan, per cell)
  const ja = R() * Math.PI;
  const byRock = {}, jSets = {};   // (the beds of one rock share their joints' field)
  const JT = S.beds.map((b) => byRock[b.rock] ??= (() => {
    const f = new Float32Array(n).fill(1);
    const sets = jSets[b.rock] = b.columns ? [0, 1, 2].map((q) => ja + q * Math.PI / 3) : b.joint ? [ja, ja + Math.PI / 2 + (R() - .5) * .3] : [];
    for (let k = 0; k < n; k++) {
      const x = (k % N) * dx, y = ((k / N) | 0) * dx;
      let near = 0;
      for (const a of sets) {
        const t = (x * Math.cos(a) + y * Math.sin(a)) / b.joint + .35 * fbm(x / 23, y / 23, seed + 71 + a * 10, 2), d = Math.abs(t - Math.round(t)) * b.joint;
        near = Math.max(near, clamp(1 - d / (b.columns ? .5 : 1.3), 0, 1));
      }
      f[k] = (1 - .72 * near) * (1 + .18 * noise(x / 3.3, y / 3.3, seed + 73));
    }
    return f;
  })());
  if (dikeM.some(v => v)) { const JTs = [...new Set(JT)]; for (let k = 0; k < n; k++) if (dikeM[k]) for (const f of JTs) f[k] = 4; }   // (a dike's basalt, a causeway's columns, stand steep through whatever bed)
  // (a joint at the surface, where the rain widens it: limestone's joints end and start again -- each runs a few blocks
  // and stops, the next along offset -- not one crack across the land as sandstone's run. 0..1, 1 on it)
  const hash2 = (a, b) => { const h = Math.sin(a * 127.1 + b * 311.7 + seed * 7.3) * 43758.5453; return h - Math.floor(h); };
  const grikeAt = (b, x, y) => {
    const B = S.beds[b], sets = jSets[B.rock] ?? []; if (!B.karst) return clamp((1 - JT[b][Math.round(y / dx) * N + Math.round(x / dx)]) / .72, 0, 1);
    let near = 0;
    sets.forEach((a, q) => {
      const ca = Math.cos(a), sa = Math.sin(a), t = (x * ca + y * sa) / B.joint + .35 * fbm(x / 23, y / 23, seed + 71 + a * 10, 2), id = Math.round(t);
      const al = (-x * sa + y * ca) / (B.joint * (2.5 + 2 * hash2(id, q + 9))) + hash2(id, q + 3);
      if (hash2(id * 3 + q, Math.floor(al)) < .45) return;
      near = Math.max(near, clamp(1 - Math.abs(t - id) * B.joint / 1.3, 0, 1));
    });
    return near;
  };
  // BADLANDS: in a dry country nothing holds a bare soft bed -- the runoff cuts it into rills and gullies (cut before
  // the last sweeps, which let their walls settle to what the bed stands; the sweeps 140 all the same -- a wall's flutes
  // and buttresses are what settling has not yet worn away, so more sweeps make smoother walls)
  const dryness = clamp((700 - clim.rain) / 500, 0, 1), erod = S.beds.map((b) => clamp((.45 - b.hard) / .3, 0, 1));
  // (a gully's walls in a soft bed: crusted dry, they stand steeper than its slope at large, which the scree lies on)
  const tanG = S.beds.map((b, q) => Math.tan((erod[q] ? Math.min(62, b.angle + 18 * erod[q] * dryness) : b.angle) * Math.PI / 180));
  const BAD = F.badlands !== false && dryness > 0 && erod.some((e) => e > 0);
  relax(N, dx, rock, soil, carved, DAT, S.base, tanR, JT, tanS, BAD ? 128 : 140);
  if (BAD) {
    gully(N, dx, rock, soil, carved, DAT, S.base, erod, .06 * dryness, 12);
    relax(N, dx, rock, soil, carved, DAT, S.base, tanG, JT, tanS, 12);
    notes.push(`badlands: the ${S.beds.filter((b, q) => erod[q] > .3).map((b) => b.name).filter((v, q, a) => a.indexOf(v) === q).join(" and ")} bare and cut into rills and gullies -- ` +
      (dryness > .7 ? "a dry country's rain runs off it, and nothing holds it" : "where the scrub leaves it bare"));
  }
  (() => {
  for (let k = 0; k < n; k++) { if (carved[k]) soil[k] = Math.min(soil[k], .05); H[k] = rock[k] + soil[k]; }
  })();
  // (the couloirs' cones: from each mouth down the slope, widening, thickest along the middle)
  for (const c of [...couloirs, ...ravines]) {   // (a ravine's spread wider: water laid it)
    const R0 = Math.ceil((c.r + 4) / dx), i0 = Math.round(c.x / dx), j0 = Math.round(c.y / dx), sw = c.wide ? 1.15 : .7;
    for (let j = Math.max(0, j0 - R0); j <= Math.min(N - 1, j0 + R0); j++) for (let i = Math.max(0, i0 - R0); i <= Math.min(N - 1, i0 + R0); i++) {
      const k = j * N + i, b = U[k] - c.u + 1, dv = V[k] - c.v; if (b < 0 || carved[k]) continue;
      const lat = Math.abs(dv) / (2 + sw * b) * (1 + .15 * fbm(i * dx / 6, j * dx / 6, seed + 247, 2)), d = Math.hypot(b, dv) / c.r; if (lat >= 1 || d >= 1) continue;
      const t = c.T * (1 - d) ** .8 * (1 - lat * lat); soil[k] += t; H[k] += t;
    }
  }
  // (no needles: a column a cell across standing metres over all round it -- the joints' blocks left one by one at a
  // cliff's edge -- would not stand; it falls to a stump)
  (() => {
    for (let pass = 0; pass < 2; pass++) for (let j = 1; j < N - 1; j++) for (let i = 1; i < N - 1; i++) {
      const k = j * N + i; let mx = -Infinity;
      for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) if (a || b) mx = Math.max(mx, H[k + b * N + a]);
      if (H[k] > mx + 2.5) { H[k] = mx + .4; fanBase[k] = Math.min(fanBase[k], H[k]); soil[k] = Math.min(soil[k], .4); }
    }
  })();
  mark("settle");
  Object.assign(c, { rock, tanR, tanS, dist, DAT, bedK, ja, byRock, jSets, JT, hash2, grikeAt, dryness, erod, tanG, BAD });
}
