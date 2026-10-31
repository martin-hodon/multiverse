// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- the cold's work: the moraine, braids, the esker, the rock
// glacier, knock and lochan, the cirque, solifluction. Each stage takes the scene so far, `c`, and adds what it makes
// to it; landscape.js runs them in order.
import { TAU, clamp, smooth, lerp, noise, fbm, rng } from "./core.js";

export function moraine(c) {
  const { clim, dx, F, fallU, H, lake, N, n, notes, scarpU, seed, size, streamV, toUV, U, V } = c;
  // a MORAINE: where it is cold the lake's hollow is the ice's, and the ice left what it carried where its snout stood
  // -- a horseshoe of till round the lake's lower end, its sides the lateral moraines, hummocky, the gorge's head cut
  // through it; loose (above `fanBase`: it settles as scree). Erratics on the upland: blocks it carried and dropped
  const moraine = { erratics: [] }, kettleM = new Uint8Array(n);
  (() => {
  if (!lake || clim.temp >= 4 || F.moraine === false) return;
  const RM = rng(seed * 71 + 13), hM = 2.5 + RM() * 2.5, crest = [];
  for (let k = 0; k < n; k++) {
    const du = (U[k] - lake.u) / (lake.r * 1.3), dv = (V[k] - lake.v) / lake.r, x = (k % N) * dx, y = ((k / N) | 0) * dx;
    const q = Math.sqrt(du * du + dv * dv) + .1 * fbm(x / 30, y / 30, seed + 75, 2), w = smooth((du + .45) / .9) * smooth((fallU - 6 - U[k]) / 8);
    if (w <= 0 || Math.abs(q - 1.3) > .45) continue;
    const t = hM * w * Math.exp(-(((q - 1.3) / .13) ** 2)) * (1 + .4 * fbm(x / 9, y / 9, seed + 77, 3));
    if (t > 0) H[k] += t;
    if (Math.abs(q - 1.62) < .1 && w > .6 && k % 3 === 0) crest.push(k);   // (beyond the ridge: the outwash the meltwater spread)
  }
  // (KETTLES: blocks of the ice left buried in the outwash beyond the moraine melted out after it, the gravel over them
  // sank -- round hollows, the water standing in them. Their own random numbers)
  moraine.kettles = [];
  if (F.kettles !== false) { const RK = rng(seed * 307 + 5), want = 2 + Math.floor(RK() * 4);
    for (let t = 0; t < 80 && moraine.kettles.length < want && crest.length; t++) {
      const k0 = crest[Math.floor(RK() * crest.length)], x = (k0 % N) * dx, y = ((k0 / N) | 0) * dx, [u, v] = toUV(x, y), r = 3 + RK() * 3, d = 1.1 + RK() * .9;
      if (Math.abs(v - streamV(u)) < r + 9 || moraine.kettles.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r + 4)) continue;
      moraine.kettles.push({ x, y, r, d });
      for (let j = Math.floor((y - r) / dx); j <= Math.ceil((y + r) / dx); j++) for (let i = Math.floor((x - r) / dx); i <= Math.ceil((x + r) / dx); i++) {
        const q = Math.hypot(i * dx - x, j * dx - y) / (r * (1 + .12 * noise(i * dx / 2, j * dx / 2, seed + 307))); if (q < 1) { H[j * N + i] -= d * (1 - q * q) ** .9; kettleM[j * N + i] = 1; }
      }
    } }
  for (let t = 0, m = 0; t < 200 && m < 18; t++) {
    const x = 8 + RM() * (size - 16), y = 8 + RM() * (size - 16), [u, v] = toUV(x, y);
    if (u > scarpU(v) - 10 || lake.r * lake.dist(u, v) < lake.r * 1.05 || Math.abs(v - streamV(u)) < 8) continue;
    moraine.erratics.push({ x, y, r: 1 + RM() * 1.8 }); m++;
  }
  notes.push(`moraine: ${hM.toFixed(1)} m of till round the lake's lower end, where the ice's snout stood -- the stream cuts through it; ${moraine.erratics.length} erratics on the upland, blocks the ice carried and dropped` + (moraine.kettles.length ? `; ${moraine.kettles.length} kettles beyond it, where ice buried in the outwash melted out` : ""));
  })();
  Object.assign(c, { moraine, kettleM });
}

export function braids(c) {
  const { bar, BRAID, carved, chanD, coast, dx, H, half, lam, mStart, n, N, notes, profAt, seed, sOf, streamV, T, U, V } = c;
  // BRAIDS: where it is cold the meltwater's floods bring down more gravel than the stream can carry on -- it drops it
  // in its own way, goes round, drops it again: no one channel but a belt of gravel bars, the stream in threads across
  // it that part and join (the threads given water after the WATER stage: its routing finds one way down, not all).
  // On the lowland, below the last step, to the sea. Its own random numbers
  const braidM = new Uint8Array(n);   // 1 the belt's bars, 2 a thread
  const braid = (() => {
    if (!BRAID) return null;
    const RW = rng(seed * 127 + 59), Bw = 9 + RW() * 5, nT = 3 + Math.floor(RW() * 2.5), u0 = mStart + 14, u1 = coast ? coast.uL - 4 : half * 1.5;
    if (u1 - u0 < 30) return null;   // (the sea too close below the last step: no room for a belt)
    const th = []; for (let q = 0; q < nT; q++) th.push({ lam: 35 + RW() * 40, ph: RW() * TAU, ph2: RW() * TAU, A: .6 + RW() * .3, w: 1 + RW() * .6 });
    const zAt = new Float64Array(Math.ceil(u1 - u0) + 2); for (let q = 0; q < zAt.length; q++) zAt[q] = profAt(sOf(u0 + q));
    let cells = 0;
    for (let k = 0; k < n; k++) {
      const u = U[k]; if (u < u0 || u > u1) continue;
      const w = Bw * smooth((u - u0) / 30) * (coast ? smooth((u1 - u) / 16) : 1); if (w < 1.5) continue;
      const c = V[k] - streamV(u), ac = Math.abs(c); if (ac > w + 3) continue;
      const x = (k % N) * dx, y = ((k / N) | 0) * dx, q = u - u0, zP = lerp(zAt[Math.floor(q)], zAt[Math.floor(q) + 1], q % 1);
      let z = zP + chanD - .1 + .35 * clamp(fbm(x / 7, y / 7, seed + 129, 2) + .3, 0, 1), t = 0;
      for (const T of th) {
        const o = clamp(w * T.A * (.8 * Math.sin(TAU * u / T.lam + T.ph + 1.6 * fbm(u / 30, T.ph, seed + 131, 2)) + .35 * Math.sin(TAU * u / (T.lam * .43) + T.ph2)), -w * .85, w * .85), d = Math.abs(c - o);
        if (d < T.w) { z = Math.min(z, zP + chanD * .3 + chanD * .4 * (d / T.w) ** 2); t = 1; }
      }
      if (ac < w) { H[k] = z; carved[k] = t; bar[k] = 0; braidM[k] = t ? 2 : 1; cells++; }
      else { const zb = lerp(z, H[k], smooth((ac - w) / 3)); if (zb < H[k]) H[k] = zb; }
    }
    if (!cells) return null;
    notes.push(`braids: a belt of gravel bars ${Math.round(Bw * 2)} m wide, the stream across it in ${nT} threads -- the meltwater brings down more than it can carry on`);
    return { w: Bw, threads: nT, u0, u1 };
  })();
  Object.assign(c, { braidM, braid });
}

export function esker(c) {
  const { clim, coneM, domeM, dx, F, H, lake, n, N, notes, outliers, PLAYA, seed, size, streamV, toXY } = c;
  let { lam, pts, T } = c;
  // an ESKER: under the ice the meltwater ran in a tunnel, and filled it with the gravel it carried -- when the ice was
  // gone the tunnel's fill stood as a ridge: long, winding the way the ice went, beside the lake's hollow down to the
  // snout; narrow, steep-sided, round-crested, rising and falling along its way; where it swings out over the hollow, a
  // spit into the lake. Loose
  // (above `fanBase`). Its own random numbers
  const eskerM = new Uint8Array(n); let esker = null;
  (() => {
    if (!lake || PLAYA || clim.temp >= 4 || F.esker === false) return;
    const RE = rng(seed * 311 + 9); if (RE() > (F.esker?.chance ?? .75)) return;
    for (let t = 0; t < 30 && !esker; t++) {
      const side = RE() < .5 ? -1 : 1, vL = lake.v + side * lake.r * (1.7 + RE() * .5), uE = lake.u + lake.r * (.3 + RE() * .6);   // (its end at the snout, out beside the lake's moraine)
      const h0 = 2.6 + RE() * 2.4, W = h0 * 2.1, A = 4 + RE() * 6, lam = 45 + RE() * 35, ph = RE() * TAU, drift = (RE() - .5) * .25, len = 80 + RE() * 90;
      const pts = []; let ok = true, edge = false;
      for (let s = 0; s <= len && ok; s += 1) {
        const u = uE - s, v = vL + A * Math.sin(s / lam * TAU + ph) * smooth(s / 25) + drift * s + 1.5 * noise(s / 9, 0, seed + 311), [x, y] = toXY(u, v);
        if (x < 3 || y < 3 || x > size - 3 || y > size - 3) { edge = true; break; }   // (out of the scene: it runs on beyond)
        const k = clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1);
        const dl = lake.dist(u, v);
        if ((dl > 1.05 && Math.abs(v - streamV(u)) < W + 7) || coneM[k] || domeM[k] || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + W + 6)) ok = false;
        pts.push({ x, y, s, inL: dl < 1 });
      }
      if (!ok || pts.length < 45) continue;
      const end = pts[pts.length - 1].s, sp = pts.filter((p) => p.inL).length;
      const T = new Float32Array(n);
      for (const p of pts) {
        // (higher and lower along it -- beads where the tunnel's mouth paused; its end, at the snout, let down)
        const hs = h0 * (.75 + .25 * noise(p.s / 22, 7, seed + 313) + .2 * Math.max(0, Math.sin(p.s / 17 + ph))) * smooth(p.s / 12) * (!edge && end - p.s < 8 ? smooth((end - p.s) / 8) : 1), Wp = W * (.85 + .3 * (hs / h0));
        const r = Math.ceil(Wp / dx), ci = Math.round(p.x / dx), cj = Math.round(p.y / dx);
        for (let j = cj - r; j <= cj + r; j++) for (let i = ci - r; i <= ci + r; i++) {
          if (i < 0 || j < 0 || i >= N || j >= N) continue;
          const d = Math.hypot(i * dx - p.x, j * dx - p.y) / Wp; if (d >= 1) continue;
          const z = hs * (1 - d * d) ** 1.3; if (z > T[j * N + i]) T[j * N + i] = z;
        }
      }
      for (let k = 0; k < n; k++) if (T[k] > .05) {
        const z = Math.max(H[k], lake.level - 1.3) + T[k] * (1 + .06 * noise((k % N) * dx / 3, ((k / N) | 0) * dx / 3, seed + 313));   // (in the lake: from under its water, not from its floor)
        if (z > H[k]) { H[k] = z; eskerM[k] = 1; }
      }
      esker = { pts: pts.filter((p, q) => q % 5 === 0).map(({ x, y }) => ({ x, y })), h: h0, W, len: end, spit: sp };
      notes.push(`esker: a gravel ridge ${Math.round(end)} m long, up to ${(h0 * 1.2).toFixed(1)} m high, winding down the way the ice went -- the fill of the tunnel its meltwater ran in under it` +
        (sp > 4 ? `; for ${Math.round(sp)} m it runs out into the lake, a spit` : ""));
    }
  })();
  Object.assign(c, { eskerM, esker, lam, pts, T });
}

export function rockGlacier(c) {
  const { clim, coast, cone, cu, dx, F, fans, H, half, n, N, notes, outliers, scarp2U, scarpU, seed, size, slide, STEP2,
    streamV, su, toXY, U, V } = c;
  let { T } = c;
  // a ROCK GLACIER: where it is cold enough for the ground to stay frozen, the talus under a cliff, ice in its pores,
  // creeps on out over the land below -- a tongue of blocks, flat-topped, its margins and its front steep (the
  // blocks roll down them), its back ridged in arcs bowed downhill where it moved faster in the middle. Bare blocks:
  // nothing grows on it. Loose. Its own random numbers
  const rgM = new Uint8Array(n);
  let rockGlacier = null;
  (() => {
  if (F.rockGlacier === false || clim.temp >= 3) return;
  const RG = rng(seed * 103 + 41); if (RG() >= (F.rockGlacier?.chance ?? .8)) return;
  for (let t = 0; t < 40 && !rockGlacier; t++) {
    const vc = (RG() - .5) * size * .8, W0 = 14 + RG() * 10, Lr = 50 + RG() * 40, T = 5 + RG() * 4, us = scarpU(vc) + 2, uEnd = us + Lr + 4;
    const [cx, cy] = toXY(us, vc), [ex, ey] = toXY(uEnd, vc);
    if (Math.min(cx, cy, ex, ey) < W0 + 6 || Math.max(cx, cy, ex, ey) > size - W0 - 6) continue;
    let near = false; for (let u = us - 10; u < uEnd && !near; u += 4) near = Math.abs(vc - streamV(u)) < W0 + 18;
    if (near || (STEP2 && uEnd > scarp2U(vc) - 6) || (coast && uEnd > coast.line(vc) - 10) || uEnd > half - 8) continue;
    if (slide && Math.abs(slide.v - vc) < slide.Wl * 1.6 + W0) continue;
    if (outliers.some((o) => Math.hypot(o.u - (us + Lr * .5), o.v - vc) < o.r + Lr * .5 + W0 * .5)) continue;
    if (cone && Math.hypot(cone.x - (cx + ex) / 2, cone.y - (cy + ey) / 2) < cone.Rb + Lr * .5 + W0) continue;
    if (fans.some((f) => Math.hypot(f.x - (cx + ex) / 2, f.y - (cy + ey) / 2) < f.r + Lr * .5)) continue;
    const wob = (u) => vc + 5 * fbm(u / 50, 12.1, seed + 117, 2), nR = 5 + RG() * 2;   // (its ridges: how many down its length)
    for (let k = 0; k < n; k++) {
      const u = U[k], b = u - us; if (b < -4 || b > Lr + 2) continue;
      const a = V[k] - wob(u), W = W0 * (1 + .25 * b / Lr), c = 2 * a / W; if (Math.abs(c) >= 1) continue;
      const x = (k % N) * dx, y = ((k / N) | 0) * dx, Le = Lr * (1 - .35 * c * c) * (1 + .05 * fbm(a / 8, 13.3, seed + 119, 2)); if (b >= Le) continue;
      const side = smooth((W / 2 - Math.abs(a)) / 3), front = smooth((Le - b) / 4), root = smooth((b + 4) / 14), q = b / Le;
      const ridges = .7 * Math.sin(TAU * (q - .18 * c * c) * nR + 1.5 * fbm(x / 20, y / 20, seed + 121, 2));
      const t = (T * (.75 + .25 * q) + ridges * (1 - .5 * q) + .5 * fbm(x / 6, y / 6, seed + 123, 2)) * side * front * root;
      if (t > .3) { H[k] += t; if (side * front > .2) rgM[k] = 1; }
    }
    rockGlacier = { x: (cx + ex) / 2, y: (cy + ey) / 2, u: us, v: vc, W: W0, L: Lr, T, root: [cx, cy], out: [cu, su] };
    notes.push(`rock glacier: a tongue of the talus ${Math.round(Lr)} m long, ${Math.round(W0)} m wide, ${T.toFixed(0)} m thick, creeping out from under the cliff -- the ground frozen, ice in its pores; ridged across, its front steep`);
  }
  })();
  Object.assign(c, { rgM, rockGlacier, T });
}

export function knock(c) {
  const { capK, clim, coast, cone, dx, F, fanBase, fans, fanT, H, moraine, n, N, notes, outliers, rgM, S, scarp2U,
    scarpU, seed, size, slide, STEP2, streamV, theta, toUV, U, V } = c;
  let { T } = c;
  // KNOCK AND LOCHAN: where the ice went over granite it scraped the rotten rock out of the joints and left the sound
  // between -- the land below the step a scatter of bare knolls, each a roche moutonnee: smoothed and long on the side
  // the ice came from, plucked steep on the side it went to (down the valley); small lakes in the hollows between,
  // an erratic left on a knoll here and there. Its own random numbers
  const knockM = new Uint8Array(n);   // 1 a knoll's scoured rock
  (() => {
  if (F.knolls === false || S.beds[capK].rock !== "granite" || clim.temp >= 4) return;
  const RQ = rng(seed * 167 + 83), knolls = [], T = new Float32Array(n);
  const zone = (u, v, k) => smooth((u - scarpU(v) - 14) / 12) * smooth((Math.abs(v - streamV(u)) - 9) / 8) * (coast ? smooth((coast.line(v) - u - 12) / 12) : 1) * (STEP2 ? smooth((Math.abs(u - scarp2U(v)) - 14) / 10) : 1) * (rgM[k] ? 0 : 1) * (1 - clamp(fanT[k] * 3, 0, 1));
  for (let t = 0; t < 500 && knolls.length < 32; t++) {
    const x = 8 + RQ() * (size - 16), y = 8 + RQ() * (size - 16), k = Math.round(y / dx) * N + Math.round(x / dx), [u, v] = toUV(x, y);
    const L = 5 + RQ() ** 1.5 * 15, W = L * (.4 + RQ() * .3), h = (1.5 + RQ() * 3.5) * (.5 + .5 * L / 20), rot = (RQ() - .5) * .45;
    if (zone(u, v, k) < .9 || Math.abs(v - streamV(u)) < W + 10) continue;
    if (knolls.some((o) => Math.hypot(o.x - x, o.y - y) < (o.L + L) * .7 + 3) || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + L + 6)) continue;
    if (fans.some((f) => Math.hypot(f.x - x, f.y - y) < f.r + L) || (cone && Math.hypot(cone.x - x, cone.y - y) < cone.Rb + L + 6) || (slide && Math.hypot(slide.x - x, slide.y - y) < slide.Lb + L + 10)) continue;
    knolls.push({ x, y, u, v, L, W, h, rot });
  }
  for (const o of knolls) {
    const ca = Math.cos(theta + o.rot), sa = Math.sin(theta + o.rot), Rr = o.L + 2;
    for (let j = Math.max(0, Math.floor((o.y - Rr) / dx)); j <= Math.min(N - 1, Math.ceil((o.y + Rr) / dx)); j++) for (let i = Math.max(0, Math.floor((o.x - Rr) / dx)); i <= Math.min(N - 1, Math.ceil((o.x + Rr) / dx)); i++) {
      const k = j * N + i, x = i * dx, y = j * dx, a = (x - o.x) * ca + (y - o.y) * sa, b = -(x - o.x) * sa + (y - o.y) * ca;
      const pa = a < 0 ? 1 - (a / o.L) ** 2 : 1 - (a / (o.L * .45)) ** 4, pb = 1 - (b / (o.W * (1 + .1 * noise(x / 5, y / 5, seed + 153)))) ** 2;   // (the lee blunt, steep)
      if (pa <= 0 || pb <= 0) continue;
      const e = pa * pb, z = o.h * e ** .9 + (a > 0 ? .35 * noise(x / 2.2, y / 2.2, seed + 155) * e : 0);   // (the lee rough where blocks were plucked out)
      if (z > T[k]) T[k] = z;
    }
  }
  let lochs = 0;
  for (let k = 0; k < n; k++) {
    const x = (k % N) * dx, y = ((k / N) | 0) * dx;
    if (T[k] > .25) { H[k] += T[k]; fanBase[k] = Math.max(fanBase[k], H[k]); knockM[k] = 1; continue; }   // (sound rock, not heaped)
    const w = zone(U[k], V[k], k); if (w <= 0) continue;
    const d = 1.8 * w * clamp(fbm(x / 14, y / 14, seed + 157, 2) * 2.2 + .1, 0, 1);   // (the hollows: the rotten rock the ice took)
    if (d > 0) { H[k] -= d; if (d > 1) lochs++; }
  }
  if (knolls.length) {
    for (const o of knolls) if (RQ() < .35) moraine.erratics.push({ x: o.x - Math.cos(theta) * o.L * .2, y: o.y - Math.sin(theta) * o.L * .2, r: 1 + RQ() * 1.4 });
    notes.push(`knock and lochan: ${knolls.length} bare knolls on the land below the step, up to ${Math.max(...knolls.map((o) => o.h)).toFixed(0)} m, smoothed on the side the ice came from and plucked steep on the side it went to; small lakes in the hollows between -- the ice scraped the rotten granite out of the joints`);
  }
  })();
  Object.assign(c, { knockM, T });
}

export function cirque(c) {
  const { chanW, clim, coast, cone, dx, F, fanBase, fans, gorgeL, gorgeW, H, lake, moraine, N, notes, outliers,
    rockGlacier, scarp2U, scarpU, sCross, seed, size, slide, STEP2, streamV, toUV, toXY, trib, U, upAt, V } = c;
  let { su } = c;
  // a CIRQUE: where the snow lay longest -- in a hollow under the cliff's edge -- it turned to ice and the ice worked the
  // hollow: plucking the rock at its back into a steep headwall, grinding its floor down below the lip of sound rock it
  // left at its mouth. The ice gone, the hollow holds a TARN behind the lip, which spills over it down the scarp. The
  // bowl an armchair: the floor nearly flat, the wall steepening up to the rim. Its own random numbers
  let cirque = null;
  (() => {
    if (F.cirque === false || clim.temp >= 4) return;
    const RQ = rng(seed * 269 + 5); if (RQ() > (F.cirque?.chance ?? .8)) return;
    const gw = gorgeL > 0 ? gorgeW(sCross) / 2 : chanW * 3, hAt = (u, v) => { const [x, y] = toXY(u, v); return H[clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1)]; };
    for (let t = 0; t < 60 && !cirque; t++) {
      const R0 = 18 + RQ() * 14, vc = (RQ() - .5) * size * 1.2, su = scarpU(vc), [bx, by] = toXY(su - R0 * 1.6, vc), [mx, my] = toXY(su + 4, vc);
      if (Math.min(bx, by, mx, my) < R0 + 10 || Math.max(bx, by, mx, my) > size - R0 - 10) continue;
      const zt = upAt(bx, by, su - R0 * 1.6), zlow = hAt(su + 22, vc), ch = zt - zlow; if (ch < 8) continue;
      let ok = Math.abs(vc - streamV(su)) > gw + R0 + 14 && Math.abs(vc - streamV(su - R0 * 1.6)) > R0 + 14 && (!coast || coast.line(vc) - su > 34) && (!STEP2 || scarp2U(vc) - su > 30);
      ok &&= !lake || lake.dist(su - R0 * .8, vc) > 1.3 + R0 / lake.r;
      ok &&= !rockGlacier || Math.abs(vc - rockGlacier.v) > rockGlacier.W / 2 + R0 + 6;
      ok &&= !slide || Math.abs(vc - slide.v) > slide.Wl + R0 + 4;
      ok &&= !outliers.some((o) => Math.hypot(o.u - su, o.v - vc) < o.r + R0 * 1.5 + 8) && !fans.some((f) => Math.hypot(f.x - mx, f.y - my) < f.r + R0);
      ok &&= !cone || Math.hypot(cone.x - mx, cone.y - my) > cone.Rb + R0 * 1.5 + 6;
      ok &&= !trib || !trib.way.some(([x, y]) => { const [u, v] = toUV(x, y); return Math.hypot(u - (su - R0 * .7), v - vc) < R0 * 1.3 + 6; });
      if (!ok) continue;
      // (the lip where the old face is down to it: the floor is cut into the face half way, the lip a little over it)
      const zf = zt - ch * (.42 + RQ() * .14), lipH = 1.3 + RQ() * 1.2, dT = 1.2 + RQ() * 1.6;
      let a0 = 0; while (a0 < 40 && hAt(su - 4 + a0, vc) > zf + lipH) a0 += .5;
      const dL = a0 - 4, Rr = Math.ceil(R0 * 2.2 / dx), [ox, oy] = toXY(su - R0 * .5, vc), i0 = Math.round(ox / dx), j0 = Math.round(oy / dx);
      let cells = 0;
      for (let j = Math.max(0, j0 - Rr); j <= Math.min(N - 1, j0 + Rr); j++) for (let i = Math.max(0, i0 - Rr); i <= Math.min(N - 1, i0 + Rr); i++) {
        const k = j * N + i, x = i * dx, y = j * dx, a = scarpU(V[k]) + dL - U[k], w = V[k] - vc;   // (a: back from the lip)
        if (a < 0) continue;
        const jit = 1 + .1 * fbm(x / 13, y / 13, seed + 261, 2) + .05 * noise(x / 4.5, y / 4.5, seed + 265);   // (the rim bitten back where the joints let go)
        const rho = Math.hypot((a - R0 * .5) / (a < R0 * .5 ? R0 * 1.7 : R0 * .9), w / (R0 * 1.15)) / jit, r0 = .48;
        const base = zf + lipH * smooth(1 - a / (R0 * .32)) - (rho < r0 ? dT * (1 - (rho / r0) ** 2) * smooth((a - R0 * .12) / (R0 * .3)) : 0);
        const z = base + (rho > r0 ? (zt + 3 - base) * ((rho - r0) / (1 - r0)) ** 2.2 : 0) + .25 * noise(x / 4, y / 4, seed + 263);
        if (z < H[k] - .05) { H[k] = z; fanBase[k] = Math.min(fanBase[k], z); cells++; }
      }
      if (cells < R0 * R0) continue;
      const [cx, cy] = toXY(su + dL - R0 * .55, vc);
      for (let e = 0, ne = 1 + Math.floor(RQ() * 3); e < ne; e++) { const vq = vc + (RQ() - .5) * R0 * 1.2, [ex, ey] = toXY(scarpU(vq) + dL - R0 * .06, vq); moraine.erratics.push({ x: ex, y: ey, r: .8 + RQ() * 1.1 }); }   // (on the lip, where the ice let them down)
      cirque = { x: cx, y: cy, u: su + dL - R0 * .55, v: vc, r: R0, floor: zf, lip: zf + lipH, depth: lipH + dT, wall: zt - zf };
      notes.push(`cirque: a bowl ${Math.round(R0 * 2)} m across bitten into the cliff's edge, its headwall ${Math.round(zt - zf)} m -- where the snow lay longest the ice plucked its back and ground its floor down behind a lip of sound rock; ${clim.lakes ? `a tarn in it, ${(lipH + dT).toFixed(1)} m deep, spilling over the lip` : "its floor dry"}`);
    }
  })();
  Object.assign(c, { cirque, su });
}

export function solifluction(c) {
  const { clim, coast, coneM, cut, dikeM, dist, dx, F, H, knockM, lake, n, N, notes, rgM, seed, soil, streamV, tinM,
    toUV, trib } = c;
  // SOLIFLUCTION: where it is cold and wet the ground thaws on top each summer over the ice still in it below, and the
  // sodden soil creeps down the slope -- in tongues, each held up at its front by the turf: LOBES 6-16 m wide, a riser
  // half a metre to a metre high at their fronts, bowed downslope, the tread behind them easing back into the slope.
  // On the soil-covered slopes of 5-24 deg. Its own random numbers
  const lobes = [], lobeM = new Uint8Array(n);   // (2 a lobe's riser)
  (() => {
  if (F.solifluction === false || clim.temp >= 3 || clim.rain < 400) return;
  const dry = (x, y) => { const [u, v] = toUV(x, y); return Math.abs(v - streamV(u)) > 14 && !(lake && lake.dist(u, v) < 1.3) && !(coast && u > coast.line(v) - 10) && !(trib && trib.way.some(([tx, ty]) => Math.hypot(tx - x, ty - y) < 8)); };
  const RL = rng(seed * 303 + 11), sl = (k) => Math.hypot(H[k + 1] - H[k - 1], H[k + N] - H[k - N]) / (2 * dx);
  const cand = []; for (let j = 12; j < N - 12; j += 3) for (let i = 12; i < N - 12; i += 3) { const k = j * N + i, g = sl(k);
    if (g > .09 && g < .45 && soil[k] > .25 && !cut[k] && !coneM[k] && !rgM[k] && !dikeM[k] && !knockM[k] && !tinM[k] && dry(i * dx, j * dx)) cand.push(k); }
  for (let t = 0; t < 200 && lobes.length < 10 + Math.floor(clim.wet * 14) && cand.length; t++) {
    const k0 = cand[Math.floor(RL() * cand.length)], x0 = (k0 % N) * dx, y0 = ((k0 / N) | 0) * dx;
    const gx = (H[k0 + 1] - H[k0 - 1]) / (2 * dx), gy = (H[k0 + N] - H[k0 - N]) / (2 * dx), g = Math.hypot(gx, gy), ax = -gx / g, ay = -gy / g;   // (a: down the slope)
    const Wl = 3 + RL() * 5, Ll = 6 + RL() * 9, h = .6 + RL() * .8;
    if (lobes.some((o) => Math.hypot(o.x - x0, o.y - y0) < o.w + Wl + 2)) continue;
    let ok = true; for (const [a, b] of [[Ll * .5, 0], [-Ll * .5, 0], [0, Wl], [0, -Wl]]) { const kk = clamp(Math.round((y0 + ay * a + ax * b) / dx), 0, N - 1) * N + clamp(Math.round((x0 + ax * a - ay * b) / dx), 0, N - 1); if (cut[kk] || soil[kk] < .15 || coneM[kk] || tinM[kk]) ok = false; }
    if (!ok) continue;
    lobes.push({ x: x0, y: y0, w: Wl, l: Ll, h });
    const Rr = Math.max(Wl, Ll) + 2;
    for (let j = Math.max(1, Math.floor((y0 - Rr) / dx)); j <= Math.min(N - 2, Math.ceil((y0 + Rr) / dx)); j++) for (let i = Math.max(1, Math.floor((x0 - Rr) / dx)); i <= Math.min(N - 2, Math.ceil((x0 + Rr) / dx)); i++) {
      const px = i * dx - x0, py = j * dx - y0, a = px * ax + py * ay, b = (py * ax - px * ay) / Wl;
      if (Math.abs(b) >= 1) continue;
      const af = Ll * .5 * (1 - b * b) * (1 + .12 * noise(b * 2, x0, seed + 303)) - Ll * .15, ab = -Ll * .5;   // (its front bowed downslope)
      if (a < ab || a > af + 1.4) continue;
      const side = smooth((1 - Math.abs(b)) / .35), tt = a <= af ? h * ((a - ab) / (af - ab)) ** 1.4 : h * (1 - (a - af) / 1.4) ** 1.5;
      const k = j * N + i, z = tt * side; if (z > .02) { H[k] += z; soil[k] += z; if (a > af - .6 && z > .15) lobeM[k] = 2; }
    }
  }
  if (lobes.length) notes.push(`solifluction: ${lobes.length} lobes on the slopes -- the summer's thawed top creeping over the ice below, held up at the front by the turf; risers up to ${Math.max(...lobes.map((o) => o.h)).toFixed(1)} m`);
  })();
  Object.assign(c, { lobes, lobeM });
}
