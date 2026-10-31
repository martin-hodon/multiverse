// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- the coast: cliffs or beach, the calanque, the dunes, the
// stream's mouth, the causeway, the tombolo. Each stage takes the scene so far, `c`, and adds what it makes to it;
// landscape.js runs them in order.
import { TAU, clamp, smooth, lerp, noise, fbm, rng, nearest, cumOf } from "./core.js";

export function coast(c) {
  const { bench2K, benchK, capK, carved, chanW, clim, cross, cross2, dx, F, FAULT, H, half, lowTop, lowTop2, mStart, n,
    N, notes, R, S, scarp2U, scarpU, seed, size, softK, STEP2, streamV0, tab, TOP, toUV, toXY, U, V } = c;
  // COAST: the lowland runs to the sea. Where the waves meet hard rock standing over them they undercut it and it falls:
  // a sea CLIFF, the waves' PLATFORM at its foot (planed at their level), STACKS where the cliff held a little longer;
  // where the rock is soft or low, a BEACH -- the sand the waves sorted, sloping into them. Where the stream comes out
  // through a cliff, a COVE (the sea in at the weakness the stream made), a pocket beach in it, and the stream falling
  // to it: the waves cut the cliff back faster than the stream cut down. (Its own random numbers: a scene without a
  // coast is the scene it was)
  const coast = (() => {
    if (!F.coast) return null;
    const RC = rng(seed * 53 + 3);
    if (F.coast !== true && RC() >= (F.coast.chance ?? .45)) return null;
    const last = (v) => STEP2 ? scarp2U(v) : scarpU(v), vA = streamV0(last(0) + 45);
    const gap = Math.min(STEP2 ? 30 + RC() * 14 : 50 + RC() * 30, half - 30 - last(vA)), base = last(vA) + gap;
    if (gap < 24) return null;
    const cliffed = (FAULT > 0 || benchK >= 0) && RC() < .7, cH = cliffed ? 6 + RC() * 9 : 0;
    const coveR = 13 + RC() * 7, coveD = 13 + RC() * 8, ph = RC() * 100;
    // (the shore: partly the scarp's line -- the same rock -- partly its own, bays and headlands)
    // (both from tables too)
    const shore = tab((v) => base + (last(v) - last(vA)) * .35 + size * .045 * fbm(v / (size * .3), 9.1 + ph, seed + 41, 3));
    const vS = streamV0(shore(vA) - coveD * .6);   // (where the stream meets it: straight there)
    const cove = (v) => cliffed ? smooth(1 - Math.abs(v - vS) / coveR) : 0;
    const line = tab((v) => shore(v) - coveD * cove(v));
    const uL = line(vS), landAt = (u, v) => STEP2 && u > scarp2U(v) ? lowTop2 - 1.5 - (u - scarp2U(v)) * .035 : lowTop - 1.5 - (u - scarpU(v)) * .035;
    const sea = landAt(shore(vS), vS) - (cliffed ? cH : 1.3);
    const plat = (v) => 6 + 8 * (.5 + .5 * fbm(v / 25, 2.3 + ph, seed + 43, 2));
    return { sea, cliffed, cH, vS, uL, coveR, shore, cove, line, plat, stacks: [] };
  })();
  const LINE = coast ? Float64Array.from(V, coast.line) : null;   // (the shore's line at each cell's v: wanted often, and dear)
  // (where it is cold the stream brings down more gravel than it can move, and braids instead: see BRAIDS)
  const BRAID = F.braids !== false && clim.temp < 4 && !FAULT;
  const dryness0 = clamp((700 - clim.rain) / 500, 0, 1);   // (DRESS's dryness, wanted sooner)
  const COCKPIT = F.cockpits !== false && F.dolines !== false && S.beds[capK].karst && !FAULT && clim.temp >= 18 && clim.rain >= 1500;
  const lam = 22 * chanW, meA = F.meanders && !FAULT && !BRAID ? lam * .26 * (F.meanders.amp ?? 1) : 0, mph = R() * TAU;
  // (straightening as it nears the sea: the cove is where it comes out)
  const meander = (u) => meA * smooth((u - mStart - 12) / 45) * (coast ? smooth((coast.uL - 6 - u) / 35) : 1) * Math.sin(TAU * (u - cross) / lam + mph) * (1 + .25 * fbm(u / 80, 1.3, seed + 23, 2));
  const streamV = tab((u) => streamV0(u) + meander(u));
  const pts = []; for (let u = -half * 1.5; u <= half * 1.5; u += 1) pts.push([u, streamV(u)]);
  const gorgeL = F.ravine ? size * (F.ravine.length ?? .28) : 0;
  const fallU = cross - gorgeL;                                                 // the fall's lip, at the gorge's head
  const cum = cumOf(pts), sOf = (u) => { let k = 0; while (k < pts.length - 1 && pts[k + 1][0] < u) k++; return cum[k] + (u - pts[k][0]); };
  const sFall = sOf(fallU), sCross = sOf(cross);
  // the second step's fall: younger (the first had to step back past it first) -- its gorge shorter
  const gorge2L = STEP2 ? gorgeL * .3 : 0, fall2U = cross2 - gorge2L, sFall2 = STEP2 ? sOf(fall2U) : Infinity, sCross2 = STEP2 ? sOf(cross2) : Infinity;
  const bench2Z = (u) => { const [x, y] = toXY(u, streamV(u)); return S.topOf(x, y, bench2K); };
  const lipZ = (() => { const [x, y] = toXY(fallU, streamV(fallU)); return S.datum(x, y) - .8; })();
  const benchZ = (u) => { const [x, y] = toXY(u, streamV(u)); return FAULT ? S.datum(x, y) - TOP + lowTop : S.topOf(x, y, benchK >= 0 ? benchK : softK); };
  const fallH = lipZ - benchZ(fallU);
  const plan = { stream: pts, fallU, cross, lipZ, fallH, toXY, toUV, streamV, curtain: null, capK, softK, cross2, fall2U, step2: STEP2, lowTop, lowTop2 };
  // (the upland falls to the stream from both sides and down it to the lip: where the beds' dip would take it lower,
  // the water would have left another way and there would be no fall -- so the land there is the valley's side, raised)
  (() => {
  for (let k = 0; k < n; k++) { const u = U[k]; if (u >= scarpU(V[k]) - 4) continue;
    const side = lipZ + .5 + .025 * Math.abs(V[k] - streamV(u)) + .004 * Math.max(0, fallU - u) + .4 * fbm((k % N) * dx / 30, ((k / N) | 0) * dx / 30, seed + 5, 2);
    if (H[k] < side) H[k] = side; }
  })();
  // the coast's shapes: past the line the cliff drops to the platform, and beyond it the sea's floor falls away; in the
  // cove, and along a beach, the sand slopes from a little over the sea's level into it (`shoreK`: 1 beach, 2 platform)
  const shoreK = new Uint8Array(n);
  (() => {
  if (!coast) return;
  const { sea, cliffed, line, cove, plat } = coast, pre = H.slice();
  // (on an open beach CUSPS: the swash, running up and back, sorts the sand at its reach into horns pointing out to sea
  // and the bays between, evenly spaced -- the further apart the bigger the waves)
  const GRC = cliffed && S.beds[FAULT ? capK : benchK].rock === "granite", cw = coast.cH * 1.5;   // (a granite coast's rounded cliff: how far back it reaches)
  const RU = rng(seed * 263 + 1), cL = F.cusps === false || cliffed ? 0 : 12 + RU() * 12, cA = .3 + RU() * .15;
  if (cL) coast.cusps = cL;
  for (let k = 0; k < n; k++) {
    const u = U[k], v = V[k], x = (k % N) * dx, y = ((k / N) | 0) * dx, dc = u - LINE[k];
    if (dc < -30) continue;
    const floor = sea - 7 + 1.5 * fbm(x / 40, y / 40, seed + 45, 2);
    const beach = Math.max(floor, sea + 1.3 - Math.max(0, dc) * (cliffed ? .07 : .09) + (dc < 0 ? -dc * .06 : 0) + .25 * fbm(x / 12, y / 12, seed + 47, 2));
    let z = Infinity, sk = 0;
    if (!cliffed) {
      z = beach; sk = dc > -22 ? 1 : 0;
      const e = beach - sea; if (cL && e > -1.2 && e < 1.6) { const c = Math.cos(TAU * v / cL + .8 * noise(v / 30, 1.7, seed + 255)); z += cA * (c > 0 ? c ** .6 : -((-c) ** 1.4) * .8) * Math.exp(-(((e - .2) / .6) ** 2)); }
    }
    else if (GRC && dc < 0 && dc > -cw && cove(v) < .05) {
      // (granite: the cliff a WHALEBACK -- the sheets it splits off parallel to its face, so it weathers round: steep at
      // the water, rolling over to the land above, the rock bare where the spray reaches)
      const t = -dc / cw, ze = sea + .3 + (H[k] - sea - .3) * (1 - (1 - t) ** 2) + .35 * fbm(x / 6, y / 6, seed + 301, 2) * 4 * t * (1 - t);
      if (ze < H[k]) { H[k] = ze; if (t < .55) shoreK[k] = 2; }
      continue;
    }
    else if (dc >= 0) {
      const w = plat(v), rock = dc < w ? sea + .25 + .7 * fbm(x / 5, y / 5, seed + 49, 2) - .9 * dc / w : Math.max(floor, sea - .5 - (dc - w) * .35);   // (planed at the waves' level: rising a little to the cliff's foot, its knobs out of the water, lower out to its edge)
      const c = cove(v); z = lerp(rock, beach, c); sk = c > .4 ? 1 : dc < w + 2 ? 2 : 0;
    }
    if (z < H[k]) { H[k] = z; shoreK[k] = sk; if (z < sea) carved[k] = 1; }   // (the waves carry off what falls in)
    else if (sk === 1 && H[k] - z < .8) shoreK[k] = 1;
  }
  // the stacks: on the platform, a piece of the cliff's land left standing (its outline where the joints let it break)
  if (cliffed) {
    const RS = rng(seed * 59 + 5), want = 1 + Math.floor(RS() * 4);
    for (let t = 0; t < 60 && coast.stacks.length < want; t++) {
      const v = (RS() - .5) * size * 1.2, r = 2.5 + RS() * 4, u = line(v) + 3 + r * .6 + RS() * (plat(v) + 4), [x, y] = toXY(u, v);
      if (x < r + 6 || y < r + 6 || x > size - r - 6 || y > size - r - 6 || Math.abs(v - coast.vS) < coast.coveR + r + 8) continue;
      if (coast.stacks.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r + 8)) continue;
      // (some the waves have taken down to a STUMP: the stack's foot, awash at a high tide, all that is left of it)
      const stump = coast.stacks.length > 0 && RS() < .4, zs = sea + .6 + RS() * 1.4;
      coast.stacks.push({ x, y, r, stump });
      for (let j = Math.floor((y - r * 1.4) / dx); j <= Math.ceil((y + r * 1.4) / dx); j++) for (let i = Math.floor((x - r * 1.4) / dx); i <= Math.ceil((x + r * 1.4) / dx); i++) {
        if (i < 0 || j < 0 || i >= N || j >= N) continue;
        const k = j * N + i, a = Math.atan2(j * dx - y, i * dx - x), rr = r * (1 + .3 * noise(Math.cos(a) * 1.3 + x, Math.sin(a) * 1.3, seed + 87));
        const d = Math.hypot(i * dx - x, j * dx - y);
        if (GRC && !stump && d < rr * 1.25) { const z = sea + .3 + (pre[k] - sea - .3) * Math.sqrt(Math.max(0, 1 - (d / (rr * 1.25)) ** 2)); if (z > H[k]) { H[k] = Math.min(pre[k], z); carved[k] = 0; shoreK[k] = 2; } }   // (granite's a dome, round as its cliff)
        else if (d < rr) { H[k] = stump ? Math.min(pre[k], zs + .3 * noise(i * dx / 2, j * dx / 2, seed + 89)) : pre[k]; carved[k] = 0; shoreK[k] = stump ? 2 : 0; }
      }
    }
  }
  // a CALANQUE: limestone's coast -- a valley the karst's floods cut when the sea stood lower, drowned when it rose: a
  // narrow inlet winding back into the cliffs, its walls sheer, its floor the sea's, shallowing to a pocket beach at its
  // head (where what the floods still bring down settles), and the dry valley going on up behind it. Its own random
  // numbers
  if (cliffed && !GRC && S.beds[FAULT ? capK : benchK].karst && F.calanque !== false) {
    const RQ = rng(seed * 313 + 11);
    for (let t = RQ() < (F.calanque?.chance ?? .8) ? 0 : 40; t < 40 && !coast.calanque; t++) {
      const vc = (RQ() - .5) * size * .9, Lc = 38 + RQ() * 34, Wm = 6 + RQ() * 4, A = 3 + RQ() * 5, ph = RQ() * TAU, Lv = 25 + RQ() * 25, g = .1 + RQ() * .08;
      const u0 = line(vc) + plat(vc) * .8, vC = (a) => vc + A * Math.sin(a / Lc * Math.PI * 1.3 + ph) * smooth(a / 15) + 1.2 * noise(a / 7, 3.3, seed + 317);
      const wA = (a) => a <= Lc ? Wm * (1 - .35 * a / Lc) : Wm * .65 + (a - Lc) * .4;
      if (Math.abs(vc - coast.vS) < coast.coveR + Wm + 25) continue;
      let ok = true;
      for (let a = -4; a <= Lc + Lv && ok; a += 2) {
        const v = vC(a), u = u0 - a, [x, y] = toXY(u, v), m = wA(a) + 14;   // (its walls inside the scene)
        if (x < m || y < m || x > size - m || y > size - m || Math.abs(v - streamV(u)) < Wm + 16 || coast.stacks.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + Wm + 4)) ok = false;
      }
      if (!ok) continue;
      let beach = 0;
      for (let k = 0; k < n; k++) {
        const a = u0 - U[k]; if (a < -4 || a > Lc + Lv) continue;
        const x = (k % N) * dx, y = ((k / N) | 0) * dx, w = wA(a), e = Math.abs(V[k] - vC(a)) / (w * (1 + .1 * noise(x / 4, y / 4, seed + 319)));
        if (e > 1.6) continue;
        let z;
        if (a <= Lc) {
          // (its floor: the sea's, deep at the mouth, up to the beach at the head; its walls sheer -- the rock's own)
          const f = Math.max(0, a) / Lc, zf = (f < .72 ? sea - .5 - 5 * (1 - f / .72) ** .8 : sea - .5 + 1.8 * (f - .72) / .28) + .3 * fbm(x / 6, y / 6, seed + 317, 2);
          if (e >= 1.3) continue;
          z = e < 1 ? zf : lerp(zf, H[k], smooth((e - 1) / .3));
          if (e < 1 && f > .72 && z > sea - .3) { shoreK[k] = 1; carved[k] = 1; beach++; } else if (z < H[k]) shoreK[k] = 0;   // (the beach: what falls on it the winter's storms take)
        } else {
          // (the dry valley: its floor climbing from the beach, its sides steep, till it comes out on the land)
          const zf = sea + 1.3 + (a - Lc) * g;
          z = lerp(zf, H[k], smooth((e - .35) / 1.25));
        }
        if (z < H[k]) { H[k] = z; if (z < sea) carved[k] = 1; }
      }
      const [mx, my] = toXY(u0, vC(0)), [hx, hy] = toXY(u0 - Lc, vC(Lc));
      coast.calanque = { x: mx, y: my, hx, hy, L: Lc, w: Wm * 2 };
      notes.push(`calanque: a drowned valley winding ${Math.round(Lc)} m back into the cliffs, ${Math.round(Wm * 2)} m wide at its mouth, its walls sheer -- cut by the karst's floods when the sea stood lower` +
        (beach ? "; a pocket beach at its head, and the dry valley on up behind it" : ""));
    }
  }
  if (GRC) coast.rounded = true;
  notes.push(cliffed ? `coast: the lowland ends in sea cliffs ${coast.cH.toFixed(0)} m high in the ${S.beds[FAULT ? capK : benchK].name}${GRC ? " -- rounded whalebacks, the sheets peeling off parallel to the face --" : ""}, the waves' platform at their foot` +
      (coast.stacks.length ? `, ${coast.stacks.length === 1 ? "a stack" : coast.stacks.length + " stacks"} on it where the cliff held` + (coast.stacks.some((o) => o.stump) ? ` (${coast.stacks.filter((o) => o.stump).length} cut down to a stump, awash)` : "") : "") + `; a cove where the stream comes out, a pocket beach in it`
    : `coast: the lowland runs down to the sea in a beach -- ${benchK >= 0 || FAULT ? "low ground" : `the soft ${S.beds[softK].name}`}: the waves sort it, they do not cut a cliff` + (coast.cusps ? `; cusps along its waterline every ${Math.round(coast.cusps)} m` : ""));
  })();
  plan.coast = coast;
  Object.assign(c, { coast, LINE, BRAID, dryness0, COCKPIT, lam, meA, mph, meander, streamV, pts, gorgeL, fallU, cum,
    sOf, sFall, sCross, gorge2L, fall2U, sFall2, sCross2, bench2Z, lipZ, benchZ, fallH, plan, shoreK });
}

export function dunes(c) {
  const { bar, carved, chanD, chanW, clim, coast, cum, dx, F, fall2U, fallH, fallU, fanBase, gorge2W, gorgeL, gorgeW, H,
    incise, LINE, meA, mStart, n, N, notes, outliers, plan, pool2R, poolR, profAt, pts, sCross, sCross2, seed, sFall,
    sFall2, size, sOf, STEP2, streamV, streamV0, TERR, toXY, U, V } = c;
  // DUNES: behind a beach the wind takes the sand the waves left and heaps it in ridges along the shore -- higher the drier
  // the country (nothing grows to hold it), broken by blowouts; loose (they settle at the sand's angle). In a wet one
  // the grass takes the ridges behind the first
  const dune = new Uint8Array(n);
  (() => {
  if (!coast || coast.cliffed || F.dunes === false) return;
  // (on a cold coast no dunes: the beach is shingle, and the wind cannot lift it -- the storms throw it up instead, one
  // ridge along the top of the beach, steep to the sea, gentler behind; the stream's way through it left low)
  if (clim.temp < 4) {
    const hR = 1.1 + rng(seed * 193 + 7)() * .8; let cells = 0;
    for (let k = 0; k < n; k++) {
      const dc = U[k] - LINE[k]; if (dc > 0 || dc < -16) continue;
      const x = (k % N) * dx, y = ((k / N) | 0) * dx, e = dc + 6 + 1.2 * fbm(x / 30, y / 30, seed + 111, 2), w = e > 0 ? 1.6 : 3.4;
      const t = hR * Math.exp(-((e / w) ** 2)) * (1 + .15 * fbm(x / 9, y / 9, seed + 115, 2)) * smooth((Math.abs(V[k] - coast.vS) - 4) / 6);
      if (t > .12) { H[k] += t; dune[k] = 1; cells++; }
    }
    if (cells) notes.push(`storm ridge: the shingle thrown up along the top of the beach, ${hR.toFixed(1)} m -- too coarse for the wind, no dunes`);
    return;
  }
  const dry = clamp(1 - clim.rain / 1000, 0, 1), hD = 1.6 + 3.2 * dry, rows = 2 + Math.round(dry * 2);
  let any = 0;
  for (let k = 0; k < n; k++) {
    const dc = U[k] - LINE[k]; if (dc > -4 || dc < -12 - rows * 11) continue;
    const x = (k % N) * dx, y = ((k / N) | 0) * dx, wav = 2.5 * fbm(x / 35, y / 35, seed + 111, 2);
    let r = 0; for (let q = 0; q < rows; q++) r = Math.max(r, Math.exp(-(((dc + wav + 10 + q * 11) / (3.2 + q * .6)) ** 2)) * (1 - q * .15));
    const t = hD * r * smooth((fbm(x / 22, y / 22, seed + 113, 3) + .45) / .5) * (1 + .3 * fbm(x / 7, y / 7, seed + 115, 2));
    if (t > .15) { H[k] += t; dune[k] = dry > .4 || dc > -16 ? 1 : 2; any++; }
  }
  if (any) notes.push(`dunes: ${rows} ridges behind the beach, up to ${hD.toFixed(1)} m -- the wind's heaps of the sand the waves left${dry > .4 ? ", bare: nothing grows to hold them" : "; the grass holds those behind the first"}`);
  })();
  // where the stream comes into the square (its first point inside): the water from beyond joins there
  // (the terraces: the floodplain the stream wanders on, each older one a bench a riser up from it, on out to the land
  // it has not cut into; each side its own -- a bench taken on one side by the stream swinging into it. The benches'
  // gravel loose on the rock it planed)
  const terM = new Uint8Array(n);   // 1 the floodplain, 2 a bench, 3 a riser
  (() => {
    if (!TERR) return;
    const { u0, u1, D, nL, sides } = TERR, zAt = new Float64Array(Math.ceil(u1 - u0) + 2);
    for (let q = 0; q < zAt.length; q++) zAt[q] = profAt(sOf(u0 + q));
    let bench = 0;
    for (let k = 0; k < n; k++) {
      const u = U[k]; if (u < u0 || u > u1) continue;
      const g = incise(u) / D; if (g < .02) continue;
      const c = V[k] - streamV0(u), sd = sides[c < 0 ? 0 : 1], e = Math.abs(c), x = (k % N) * dx, y = ((k / N) | 0) * dx;
      if (e > meA + 70 || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + 6)) continue;
      const q = u - u0, zF = lerp(zAt[Math.floor(q)], zAt[Math.floor(q) + 1], q % 1) + chanD + .35 + .2 * fbm(x / 11, y / 11, seed + 235, 2);
      let edge = meA + chanW * 4 + 3 + 4 * fbm(u / 35, sd.ph, seed + 237, 2), z = zF, m = 1;
      // each step: the riser (as steep as the gravel stands, rounded at its foot and lip), then the bench on out
      for (let L = 1; L <= nL; L++) {
        const last = L === nL, dh = last ? 1e3 : incise(u) / nL * (.85 + .3 * noise(u / 30, sd.ph + L, seed + 239)), rw = (last ? 3 : dh) * 1.3 + 1;
        if (e <= edge) break;
        if (last) { z = z + .25 * (e - edge) + .75 * Math.max(0, e - edge - 1.2); m = 3; break; }
        const tw = sd.gone && L === nL - 1 ? 0 : sd.tw * (.75 + .5 * noise(u / 25, sd.ph - L, seed + 241));
        if (e < edge + rw) { z += dh * smooth((e - edge) / rw); m = 3; break; }
        z += dh + .02 * (e - edge - rw) + .15 * fbm(x / 9, y / 9, seed + 243, 2); m = 2;
        edge += rw + tw;
      }
      const t = lerp(H[k], Math.min(H[k], z), g); if (t >= H[k] - .01) continue;
      H[k] = t; terM[k] = m; if (m === 2) { fanBase[k] = Math.min(fanBase[k], H[k] - .8); bench++; }
    }
    if (!bench) TERR.nL = 1;
    notes.push(`terraces: the stream ${D.toFixed(1)} m down in its old floodplain${coast ? " inland (less toward the sea)" : ""}` +
      (TERR.nL > 1 ? `, a bench of gravel midway on ${sides.some((sd) => sd.gone) ? "one side" : "both sides"}` : "") + ` -- the land rose and the stream cut down after it, a step at a time`);
    plan.terraces = { u0, u1, depth: D, levels: TERR.nL };
  })();
  const entry = pts.find(([u, v]) => { const [x, y] = toXY(u, v); return x > 3 * dx && y > 3 * dx && x < size - 3 * dx && y < size - 3 * dx; });
  (() => {
  for (let k = 0; k < n; k++) {
    const u = U[k], v = V[k], x = (k % N) * dx, y = ((k / N) | 0) * dx;
    const p0 = u - pts[0][0], near = nearest(pts, cum, u, v, Math.floor(p0 - 45), Math.ceil(p0 + 45)), s = near.s, d = near.d;   // (pts every 1 m of u: none further than 45 m matter)
    if (d > 40 || (coast && u > LINE[k] + 3)) continue;   // (not on out across the sea's floor)
    const wig = 1.2 * fbm(x / 9, y / 9, seed + 31, 2), z = profAt(s);
    // the gorge: its floor (beside the channel) on the bench, widening downstream
    if (F.waterfall !== false && gorgeL > 0 && s >= sFall && s <= sCross + 6 && d < gorgeW(s) / 2 + wig) { H[k] = Math.min(H[k], z + chanD); if (d < chanW * 1.5) carved[k] = 1; }
    // the plunge pool and the amphitheatre round the fall: the soft bed under the lip worn back in a half bowl
    const [px, py] = toXY(fallU + poolR * .6, streamV(fallU)), dp = Math.hypot(x - px, y - py);
    if (F.waterfall !== false && gorgeL > 0 && dp < poolR * 1.15 + wig) {
      const bowl = profAt(sFall + poolR * .6) + chanD - .5 - Math.min(fallH * .3, 4) * (1 - (dp / (poolR * 1.15)) ** 2);
      H[k] = Math.min(H[k], bowl); carved[k] = 1;
    }
    // the second step's gorge and pool, the same
    if (STEP2 && F.waterfall !== false && s >= sFall2 && s <= sCross2 + 6 && d < gorge2W(s) / 2 + wig) { H[k] = Math.min(H[k], z + chanD); if (d < chanW * 1.5) carved[k] = 1; }
    if (STEP2 && F.waterfall !== false) { const [qx, qy] = toXY(fall2U + pool2R * .6, streamV(fall2U)), dq = Math.hypot(x - qx, y - qy);
      if (dq < pool2R * 1.15 + wig) { H[k] = Math.min(H[k], profAt(sFall2 + pool2R * .6) + chanD - .5 - 2.5 * (1 - (dq / (pool2R * 1.15)) ** 2)); carved[k] = 1; } }
    // the channel: the profile in its middle, rounding up to the banks -- in a bend deeper under the outer bank (the cut
    // bank), and on the inner side the point bar: what the slower water there dropped, low and flat, sand and gravel
    if (d >= chanW * 4 + 1) continue;   // (beyond the channel and its bar: nothing more to cut)
    const bend = u > mStart + 12 ? (streamV(u + 2) - 2 * streamV(u) + streamV(u - 2)) / 4 : 0, inner = bend * (v - streamV(u)) > 0, sharp = Math.min(1, Math.abs(bend) * 12);
    if (d < chanW + wig * .3) { H[k] = Math.min(H[k], z + chanD * (d / chanW) ** 2 - (inner ? 0 : .35 * sharp * (1 - d / chanW))); carved[k] = 1; }
    else if (sharp > .3 && inner && d < chanW * (1.5 + 2.5 * sharp)) {
      const bz = z + chanD + .2 + .08 * (d - chanW), t = smooth((d - chanW) / (chanW * (.5 + 2.5 * sharp)));   // (rising into the bank at its edge)
      H[k] = Math.min(H[k], bz + Math.max(0, H[k] - bz) * t * t); if (t < .7) bar[k] = 1;
    }
  }
  })();
  Object.assign(c, { dune, terM, entry });
}

export function mouth(c) {
  const { carved, chanW, clim, coast, dune, dx, F, H, LINE, N, n, notes, seed, shoreK, streamV, toXY, U, V } = c;
  // the MOUTH on a beach: the waves build the beach on across where the stream comes out and drive its sand along the
  // shore -- the outlet pushed that way, through the bar at the far end of a LAGOON the stream ponds in behind it; where
  // the stream stops in the dry season the bar closes it (open only after a storm's flood). Its own random numbers
  let mouth = null;
  // (in the tropics MANGROVES on the lagoon's shallows and round its rim: the trees that stand in salt water on their
  // stilt roots, and hold the mud they trap -- sheltered water only, the open beach's waves take them)
  const mangM = new Uint8Array(n), MANG = clim.temp >= 20 && clim.rain > 900 && F.mangroves !== false;
  (() => {
  if (!coast || coast.cliffed || F.mouth === false) return;
  const RL = rng(seed * 83 + 23), sea = coast.sea, vS = coast.vS, sg = RL() < .5 ? -1 : 1, open = clim.flows;
  const b0 = -(12 + RL() * 4), wl = 5 + RL() * 4, aB = 7 + RL() * 4, aF = 24 + RL() * 18;   // (its middle's way in from the shore, half width, its reach back and on along the shore)
  const ac = (aF - aB) / 2, al = (aF + aB) / 2, aO = aF - 4, oW = chanW * 1.1, oa = 10 + RL() * 6;   // (the outlet: from the far end, slanting on oa m with the drift)
  let lagoon = 0;
  for (let k = 0; k < n; k++) {
    const u = U[k], v = V[k], a = (v - vS) * sg; if (a < -aB - 8 || a > aF + oa + 8) continue;
    const dc = u - LINE[k]; if (dc < b0 - wl - 9 || dc > 20) continue;
    const x = (k % N) * dx, y = ((k / N) | 0) * dx, nz = .15 * fbm(x / 6, y / 6, seed + 91, 2), t = (a - ac) / al;
    const w = Math.abs(t) < 1 ? wl * Math.sqrt(1 - t * t) * (1 + .25 * fbm(a / 10, 3.1, seed + 93, 2)) : 0, db = Math.abs(dc - b0);
    // (the bar: the stream's old way out filled, seaward of the lagoon)
    const barZ = sea + (open ? 1.2 : 1) + Math.max(0, -dc) * .05 - Math.max(0, dc) * .09 + nz;
    if (dc > b0 + w && Math.abs(v - streamV(u)) < chanW * 3 && H[k] < barZ) { H[k] = barZ; carved[k] = 0; if (dc > -4) shoreK[k] = 1; }
    // (the lagoon: shallow, its floor dished, its rim easing up into the land round it)
    const e = Math.hypot(t, (dc - b0) / (wl * (1 + .25 * fbm(a / 10, 3.1, seed + 93, 2))));   // (1 at its shore: its rim all round)
    if (e < 1 + 7 / wl) {
      const z = db < w ? sea - .25 - 1.1 * (1 - (db / w) ** 2) + nz * .5 : lerp(sea + .3, H[k], smooth((e - 1) * wl / 7));
      if (z < H[k]) { H[k] = z; dune[k] = 0; if (db < w) { carved[k] = 1; shoreK[k] = 0; lagoon++; } else shoreK[k] = 1; }   // (its shore sand)
      if (MANG && H[k] > sea - .8 && H[k] < sea + .7 && fbm(x / 14, y / 14, seed + 221, 2) > -.25) { mangM[k] = 1; shoreK[k] = 0; }
    }
    // (the outlet, if it is open: its bed at the lagoon a little over the sea's level -- what holds the lagoon up)
    if (open) {
      const pa = aO, pb = b0, qa = aO + oa, qb = 8, la = qa - pa, lb = qb - pb, tO = clamp(((a - pa) * la + (dc - pb) * lb) / (la * la + lb * lb), 0, 1);
      const dO = Math.hypot(a - pa - tO * la, dc - pb - tO * lb);
      if (dO < oW + 2.5) {
        const z = dO < oW ? sea + .45 - tO * 1.2 - .3 * (1 - (dO / oW) ** 2) : lerp(sea + .45 - tO * 1.2, H[k], (dO - oW) / 2.5);
        if (z < H[k]) { H[k] = z; dune[k] = 0; if (dO < oW) carved[k] = 1; else shoreK[k] = 1; }
      }
    }
  }
  if (!lagoon) return;
  const [x, y] = toXY(coast.line(vS + sg * ac) + b0, vS + sg * ac);
  mouth = { x, y, open, sg };
  notes.push(`mouth: the waves' sand built across it -- a lagoon behind the bar, ${Math.round(aF + aB)} m along the shore` +
    (open ? `, its outlet pushed ${Math.round(aF)} m along it the way the waves drive the sand` : ", the bar closed: the stream stops in the dry season, and only a flood breaks it"));
  const nM = mangM.reduce((t, v) => t + v, 0);
  if (nM > 30) notes.push(`mangroves: round the lagoon, ${nM} m2 -- standing in the salt water on their stilt roots, the mud they trap under them`);
  })();
  Object.assign(c, { mouth, mangM, MANG });
}

export function causeway(c) {
  const { capK, carved, coast, dikeM, F, fanBase, H, LINE, n, notes, S, seed, shoreK, size, toXY, U, V } = c;
  let { v0 } = c;
  // a CAUSEWAY: where a basalt flow meets the sea, the waves take it column by column -- each breaks off at its own
  // cross joint -- and leave the stumps: a headland of hexagonal tops, stepping down out into the water, the inland
  // ones standing higher. Its own random numbers
  (() => {
  if (!coast || !S.beds[capK].columns || F.causeway === false) return;
  const RW = rng(seed * 191 + 103), Sh = 4.6 + RW() * .8, hTop = 3 + RW() * 3.5, Wc = 12 + RW() * 9, Lo = 14 + RW() * 10, Li = 9 + RW() * 5;
  let v0 = null; for (let t = 0; t < 40 && v0 === null; t++) { const v = (RW() - .5) * size * .8, [x, y] = toXY(coast.line(v), v); if (Math.abs(v - coast.vS) > coast.coveR + Wc + 14 && x > Wc + 10 && y > Wc + 10 && x < size - Wc - 10 && y < size - Wc - 10) v0 = v; }
  if (v0 === null) return;
  const hsh = (q, r) => { const h = Math.sin(q * 91.7 + r * 47.3 + seed * 3.1) * 15731.7; return h - Math.floor(h); }, s3 = Math.sqrt(3) / 2;
  let cells = 0;
  for (let k = 0; k < n; k++) {
    const b = V[k] - v0; if (Math.abs(b) > Wc * 1.3) continue;
    const a = U[k] - LINE[k]; if (a < -Li - 3 || a > Lo + 3) continue;
    // (its column: the nearest centre of a hexagonal net, in the shore's frame)
    const fr = b / (Sh * s3), r0 = Math.round(fr); let best = 1e9, cq = 0, cr = 0;
    for (let r = r0 - 1; r <= r0 + 1; r++) { const q0 = Math.round(a / Sh - r / 2); for (let q = q0 - 1; q <= q0 + 1; q++) { const d = (a - (q + r / 2) * Sh) ** 2 + (b - r * Sh * s3) ** 2; if (d < best) { best = d; cq = q; cr = r; } } }
    const ac = (cq + cr / 2) * Sh, bc = cr * Sh * s3, t = ac > 0 ? ac / Lo : ac / Li;   // (-1 its inland end .. 1 its far end)
    if (t < -1 || t > 1 || Math.abs(bc) > Wc * (1 - .45 * Math.max(0, t)) * (1 + .15 * (hsh(cq + 7, cr) - .5))) continue;
    const top = coast.sea - 1.1 + Math.round(((hTop + 1.1) * smooth((1 - t) / 1.7) + (hsh(cq, cr) - .5) * 2.2) / .55) * .55;   // (each its own height, in the cross joints' steps)
    if (top < coast.sea - 1.5) continue;
    H[k] = top; fanBase[k] = Math.max(fanBase[k], top); carved[k] = 0; shoreK[k] = 0; dikeM[k] = 2; cells++;
  }
  if (cells > 60) { const [x, y] = toXY(coast.line(v0), v0); coast.causeway = { x, y, w: Wc * 2, out: Lo }; }
  if (cells > 60) notes.push(`causeway: a headland of the basalt's columns, ${Math.round(Wc * 2)} m across, stepping down ${Math.round(Lo)} m out into the sea -- hexagonal tops ~${Sh.toFixed(0)} m across, each broken off at its own joint, the inland ones standing up to ${hTop.toFixed(0)} m`);
  })();
  Object.assign(c, { v0 });
}

export function tombolo(c) {
  const { carved, coast, dx, F, fanBase, H, LINE, mark, N, n, notes, seed, shoreK, size, toXY, U, V } = c;
  let { v0 } = c;
  // a TOMBOLO: off a beach a knob of the land the sea has not yet taken, cut round; the waves bending round it on both
  // sides meet in its lee and drop their sand there -- a bar from the beach out to it, the island tied to the land,
  // the bar narrowest and lowest in its middle, awash at a storm. Its own random numbers
  (() => {
  if (!coast || coast.cliffed || F.tombolo === false) return;
  const RT = rng(seed * 199 + 17); if (RT() > (F.tombolo?.chance ?? .65)) return;
  const Ri = 7 + RT() * 6, a0 = 28 + Ri + RT() * 14, hI = 4 + RT() * 5, Wt = 3 + RT() * 3, bend = (RT() - .5) * 16, ph = RT() * 100;
  let v0 = null;
  for (let t = 0; t < 40 && v0 === null; t++) { const v = (RT() - .5) * size * .8, [x, y] = toXY(coast.line(v) + a0, v + bend);
    if (Math.abs(v - coast.vS) < 55 || x < Ri + 8 || y < Ri + 8 || x > size - Ri - 8 || y > size - Ri - 8) continue;
    if (coast.causeway && Math.hypot(coast.causeway.x - x, coast.causeway.y - y) < coast.causeway.w + Ri + 20) continue;
    v0 = v; }
  if (v0 === null) return;
  let cells = 0;
  for (let k = 0; k < n; k++) {
    const b = V[k] - v0, a = U[k] - LINE[k]; if (Math.abs(b) > Ri * 1.6 + Math.abs(bend) + 12 || a < -3 || a > a0 + Ri * 1.6) continue;
    const x = (k % N) * dx, y = ((k / N) | 0) * dx, th = Math.atan2(b - bend, a - a0);
    // (the island: steep round its foot where the waves undercut it, its top rounded)
    const di = Math.hypot(a - a0, b - bend) / (Ri * (1 + .2 * noise(Math.cos(th) * 1.3 + ph, Math.sin(th) * 1.3, seed + 203)));
    const zi = di < 1.15 ? coast.sea - .8 + (hI + .8) * smooth((1.05 - di) / .55) ** .7 + .3 * fbm(x / 6, y / 6, seed + 205, 2) : -Infinity;
    // (the bar: along a line bending out to it, widest at its ends)
    const t = clamp(a / a0, 0, 1), d = Math.abs(b - bend * t * t), w = Wt * (1 + 2.2 * (2 * t - 1) ** 2), zc = coast.sea + .35 + .55 * (2 * t - 1) ** 2 + .12 * fbm(x / 9, y / 9, seed + 207, 2);
    const zt = d < w * 1.6 ? zc - 1.4 * (d / w) ** 2 : -Infinity;
    if (Math.max(zi, zt) <= H[k]) continue;
    H[k] = Math.max(zi, zt); carved[k] = 0; cells++;
    if (zi >= zt) { fanBase[k] = Math.max(fanBase[k], H[k]); shoreK[k] = 0; } else shoreK[k] = 1;
  }
  if (cells < 80) return;
  const [x, y] = toXY(coast.line(v0) + a0, v0 + bend);
  coast.tombolo = { x, y, r: Ri, h: hI, out: a0 };
  notes.push(`tombolo: an island ${Math.round(Ri * 2)} m across, ${hI.toFixed(0)} m high, ${Math.round(a0)} m off the beach -- tied to it by a bar of sand the waves dropped in its lee, ${Math.round(Wt * 2)} m wide at its narrowest`);
  })();
  mark("carve");
  Object.assign(c, { v0 });
}
