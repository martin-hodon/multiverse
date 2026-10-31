// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- the stream's work: its bed, the terraces, the fans, the oxbow,
// the delta, the tributary, the ravines. Each stage takes the scene so far, `c`, and adds what it makes to it;
// landscape.js runs them in order.
import { TAU, clamp, smooth, lerp, noise, fbm, rng } from "./core.js";

export function streamBed(c) {
  const { fallH, S, sCross, sFall, softK } = c;
  // CARVE
  // the stream's bed: on the upland a shallow channel down to the lip's level, through the lake; the gorge from the fall
  // to the scarp, its floor on the bench (in steps where a hard bed crosses it), widening downstream; on the lowland a
  // channel falling to the edge
  const gorgeW = (s) => 7 + 10 * smooth((s - sFall) / Math.max(1, sCross - sFall)) + (S.beds[softK]?.hard < .2 ? 3 : 0);
  const poolR = Math.max(4, fallH * .45);
  // the bed's PROFILE along the stream (its deepest line, a point every 2 m): what the land asks -- the upland's channel
  // (never under the lake's level: the lip holds it), the gorge's floor on the bench, the lowland's channel -- and then
  // never rising downstream (water does not run uphill: a gorge floor under the lowland's channel was a lake)
  Object.assign(c, { gorgeW, poolR });
}

export function terraces(c) {
  const { bench2Z, benchZ, BRAID, chanD, clim, coast, cross, cross2, cum, F, FAULT, gorgeL, half, lipZ, lowTop, lowTop2,
    meA, mStart, plan, pts, S, sCross, sCross2, seed, sFall, sFall2, STEP2, toXY } = c;
  // RIVER TERRACES: on the lowland the stream has cut down into its old floodplain -- the land rose (or the sea fell)
  // and it went down after it, a step at a time: each floodplain it left a bench along the valley, a riser down from it
  // to the next, the youngest the one it wanders on now. Deepest inland (it rose there most; at the sea the stream is
  // at its level). Its own random numbers
  const TERR = (() => {
    if (F.terraces === false || !clim.flows || !meA || BRAID || FAULT) return null;
    const RT = rng(seed * 233 + 7); if (RT() > .75) return null;
    const u0 = mStart + 18, u1 = coast ? coast.uL - 10 : half * 1.5; if (u1 - u0 < 80) return null;
    const D = 2.4 + RT() * 2.6, nL = D > 3.4 && RT() < .8 ? 2 : 1, sides = [-1, 1].map(() => ({ tw: 6 + RT() * 12, gone: RT() < .35, ph: RT() * 9 }));
    return { u0, u1, D, nL, sides, inc: (u) => D * smooth((u - u0) / 30) * (coast ? smooth((coast.uL - 10 - u) / 40) : 1) };
  })();
  const incise = (u) => TERR ? TERR.inc(u) : 0;
  const prof = pts.map(([u, v], p) => {
    const s = cum[p], [x, y] = toXY(u, v);
    if (s < sFall) return Math.max(lipZ - .15, S.datum(x, y) - .6 - chanD);
    if (coast && u >= coast.uL) return coast.sea + .2 - (u - coast.uL) * .05 - chanD;   // (across the beach into the sea)
    if (s <= sCross && gorgeL > 0) return benchZ(u) - .4 - chanD - (s - sFall) / Math.max(1, sCross - sFall) * 2.5;
    if (s < sFall2) return lowTop - 1.8 - (u - cross) * .035 - chanD - incise(u);
    if (s <= sCross2) return bench2Z(u) - .4 - chanD - (s - sFall2) / Math.max(1, sCross2 - sFall2) * 1.5;
    return lowTop2 - 1.8 - (u - cross2) * .035 - chanD - incise(u);
  });
  (() => {
  for (let p = 1; p < prof.length; p++) prof[p] = Math.min(prof[p], prof[p - 1] - (cum[p] - cum[p - 1]) * .002);
  })();
  const profAt = (s) => { let a = 0, b = cum.length - 2; while (a < b) { const m = (a + b + 1) >> 1; if (cum[m] <= s) a = m; else b = m - 1; } const p = a; return lerp(prof[p], prof[p + 1], clamp((s - cum[p]) / ((cum[p + 1] - cum[p]) || 1), 0, 1)); };
  plan.profile = prof;
  const pool2R = STEP2 ? Math.max(3.5, (profAt(sFall2 - 2) - profAt(sFall2 + 2)) * .45) : 0, gorge2W = (s) => 6 + 5 * smooth((s - sFall2) / Math.max(1, sCross2 - sFall2));
  Object.assign(c, { TERR, incise, prof, profAt, pool2R, gorge2W });
}

export function fans(c) {
  const { clim, coast, cross, cross2, dx, F, gorgeL, H, LINE, n, N, notes, scarp2U, scarpU, seed, size, STEP2, streamV,
    toXY, U, V } = c;
  // ALLUVIAL FANS: where a gorge opens onto the land below, the water spreads, slows and drops what it carried -- a cone
  // of gravel and sand, its apex at the gorge's mouth, sloping out a few degrees, lobed where it spilled one way and then
  // another. Big in a dry climate (a flash flood brings much, and no stream runs on to take it away), low in a wet one;
  // the stream runs in a trench cut into its head. (On the land below each scarp, never over the next one; `fanBase`:
  // the ground under it -- what is above is loose, and settles as scree)
  const fanBase = H.slice(), fanT = new Float32Array(n), fans = [];
  (() => {
  if (F.fans === false || F.waterfall === false || gorgeL <= 0) return;
  const dry = clamp(1 - clim.rain / 1000, .15, 1);
  const mouths = STEP2 ? [[cross, Math.min(size * .2, (cross2 - cross) * .5), 1], [cross2, size * .2, 2]] : [[cross, size * .2, 1]];
  for (const [um, room, step] of mouths) {
    const Rf = room * (.45 + .6 * dry), h0 = .8 + 3.5 * dry, [ax, ay] = toXY(um, streamV(um)), [bx, by] = toXY(um + 8, streamV(um + 8)), a0 = Math.atan2(by - ay, bx - ax);
    fans.push({ x: ax, y: ay, r: Rf, h: h0 });
    for (let j = Math.max(0, Math.floor((ay - Rf * 1.3) / dx)); j <= Math.min(N - 1, Math.ceil((ay + Rf * 1.3) / dx)); j++) for (let i = Math.max(0, Math.floor((ax - Rf * 1.3) / dx)); i <= Math.min(N - 1, Math.ceil((ax + Rf * 1.3) / dx)); i++) {
      const k = j * N + i, u = U[k], v = V[k];
      if (step === 1 ? u < scarpU(v) || (STEP2 && u > scarp2U(v) - 4) : u < scarp2U(v)) continue;
      if (coast && u > LINE[k] - 3) continue;
      const x = i * dx, y = j * dx, a = Math.atan2(y - ay, x - ax), off = Math.abs(((a - a0 + 3 * Math.PI) % TAU) - Math.PI);
      const q = Math.hypot(x - ax, y - ay) / (Rf * (1 + .3 * fbm(a * 2.2, step * 5.7, seed + 23, 2))); if (q >= 1 || off > 1.4) continue;
      const t = h0 * (1 - q) ** 1.5 * smooth((1.4 - off) / .6) * (1 + .12 * noise(x / 6, y / 6, seed + 29));
      H[k] += t; fanT[k] = t;
    }
  }
  if (fans.length) notes.push(`fans: ${fans.map((f) => `${Math.round(f.r * 2)} m`).join(", ")} across, ${fans[0].h.toFixed(1)} m high at the apex, where the gorge${fans.length > 1 ? "s open" : " opens"} onto the land below -- ` +
    (dry > .6 ? "a dry country's: the floods drop what they carried, and nothing carries it on" : "low: the stream that always runs carries most of it on"));
  })();
  Object.assign(c, { fanBase, fanT, fans });
}

export function oxbow(c) {
  const { benchK, chanW, coast, cross, dx, H, lam, meA, meander, mph, mStart, N, notes, outliers, plan, S, size, softK,
    streamV, toXY } = c;
  // an OXBOW: a loop the stream cut off at its neck, beyond a bend's apex -- a crescent of still water
  (() => {
  if (meA) {
    for (let q = 0; q < 8; q++) {
      const ua = cross + lam * (q + .25 - mph / TAU), sg = Math.sign(meander(ua)), ro = lam * .2, [cx, cy] = toXY(ua, streamV(ua) + sg * (ro + chanW * 3));
      if (ua < mStart + 40 || (coast && ua + ro > coast.uL - 15) || cx < ro + 12 || cy < ro + 12 || cx > size - ro - 12 || cy > size - ro - 12 || outliers.some((o) => Math.hypot(o.x - cx, o.y - cy) < o.r + ro + 10)) continue;
      const [tx, ty] = toXY(ua, streamV(ua)), toS = Math.atan2(ty - cy, tx - cx), w = chanW * 1.1;
      for (let j = Math.floor((cy - ro - 4) / dx); j <= Math.ceil((cy + ro + 4) / dx); j++) for (let i = Math.floor((cx - ro - 4) / dx); i <= Math.ceil((cx + ro + 4) / dx); i++) {
        if (i < 0 || j < 0 || i >= N || j >= N) continue;
        const k = j * N + i, x = i * dx, y = j * dx, e = Math.abs(Math.hypot(x - cx, y - cy) - ro), a = Math.atan2(y - cy, x - cx);
        const off = Math.abs(((a - toS + 3 * Math.PI) % TAU) - Math.PI);   // (how far round from the side toward the stream)
        if (e < w && off > .9) H[k] -= 1.3 * (1 - (e / w) ** 2) * smooth((off - .9) / .5);
      }
      notes.push(`meanders: loops ${Math.round(lam)} m apart on the ${S.beds[benchK >= 0 ? benchK : softK]?.name ?? "lowland"}; point bars inside the bends; an oxbow lake where a loop was cut off`);
      plan.oxbow = { x: cx, y: cy, r: ro };
      break;
    }
  }
  })();
}

export function delta(c) {
  const { carved, clim, dx, F, fanBase, H, lake, N, n, notes, seed, streamV, toXY, U, V } = c;
  // a DELTA where the stream comes into the lake: what it carried, dropped where it slowed -- a fan out into the water
  // from where it comes in, its top a little over the lake's level, the stream split across it into arms, each building
  // its own lobe; its front the slope the sediment stands at, down to the bed. The more the stream brings the bigger:
  // the ice's meltwater most (gravel), a wet country's more than a dry one's; loose (under it `fanBase` the bowl's).
  // Its own random numbers
  const deltaM = new Uint8Array(n);
  const delta = (() => {
    if (!lake || F.delta === false || (!clim.lakes && !clim.flows)) return null;
    const RE = rng(seed * 113 + 53), ice = clim.temp < 4, lv = lake.level, lw = lv - .5;   // (lw: where the water will stand -- the lip's notch a little under its level)
    const cellAt = (u, v) => { const [x, y] = toXY(u, v), i = Math.round(x / dx), j = Math.round(y / dx); return i < 0 || j < 0 || i >= N || j >= N ? -1 : j * N + i; };
    // (where it comes in: down the stream from beyond the lake's head to the first of its water deeper than the stream's
    // own -- past any island)
    let ui = null; for (let u = lake.u - lake.r * lake.el * 1.6; u < lake.u; u += .5) { const k = cellAt(u, streamV(u)); if (k >= 0 && lake.dist(u, streamV(u)) < 1.3 && H[k] < lv - .45) { ui = u; break; } }
    if (ui === null) return null;
    const vi = streamV(ui), g = streamV(ui + 1) - vi, cx = 1 / Math.hypot(1, g), cy = g * cx;
    const sup = ice ? 1 : clamp(.3 + clim.rain / 2200, .3, .85) * (clim.flows ? 1 : .6);
    const Rd = lake.r * (.26 + .3 * sup) * (.85 + RE() * .3), nA = 2 + Math.round(RE() * (1 + sup));
    // (the arms: each a channel wandering out from the apex, some forking on the way -- the flow split where a bar grew
    // in its mouth; points every metre, in the inflow's frame: a out into the lake, b across)
    const P = [];   // [a, b, t (0 at the apex .. 1 at its mouth), w (its channel's half width)]
    const walk = (a, b, h, len, t0, w, depth = 0) => {
      const fk = depth < 2 && len > 10 && RE() < .55 + .25 * sup ? .4 + RE() * .25 : 2, wob = RE() * 100, L0 = len;
      for (let q = 0; q < len; q++) {
        const t = t0 + (1 - t0) * q / L0; P.push([a, b, t, w]);
        h += .05 * noise(q / 9, wob, seed + 117); a += Math.cos(h); b += Math.sin(h);
        if (q === Math.round(len * fk)) { const dh = (.3 + RE() * .25) * (RE() < .5 ? 1 : -1); walk(a, b, h + dh, (len - q) * (.6 + RE() * .3), t, w * .75, depth + 1); h -= dh * .6; }
      }
    };
    for (let q = 0; q < nA; q++) { const ang = q === 0 ? (RE() - .5) * .3 : (q % 2 ? 1 : -1) * (.3 + RE() * .35) * Math.ceil(q / 2) ** .5; walk(0, 0, ang, Rd * (q === 0 ? 1.25 : .95 + RE() * .3), 0, q === 0 ? 1.3 : 1.05); }
    const ends = P.filter((p, q) => q === P.length - 1 || P[q + 1][2] < p[2]).length;   // (its mouths)
    let cells = 0;
    for (let k = 0; k < n; k++) {
      const du = U[k] - ui, dv = V[k] - vi, a = du * cx + dv * cy, b = -du * cy + dv * cx;
      if (a < -1.5 || a > Rd * 2.2 || Math.abs(b) > Rd * 2) continue;
      const x = (k % N) * dx, y = ((k / N) | 0) * dx;
      let d = 1e9, t = 0, w = 1; for (const p of P) { const e2 = (a - p[0]) ** 2 + (b - p[1]) ** 2; if (e2 < d) { d = e2; t = p[2]; w = p[3]; } }
      d = Math.sqrt(d);
      // (the land along each arm: its levees, highest by the channel, narrowing out to its mouth; the front under the water)
      const Wl = Rd * (.4 * (1 - t) + .13) * (1 + .3 * fbm(x / 9, y / 9, seed + 115, 2)), e = d / Wl;
      let z = e < 1 ? lw + .08 + .4 * (1 - e) ** .7 * (1 - .5 * t) : lw - .2 - (e - 1) * Wl * .5;
      if (d < w) z = Math.min(z, lw - .45 - .35 * (1 - d / w));   // (the channel: under the water)
      if (z > H[k] && H[k] < lv + .3) { fanBase[k] = Math.min(fanBase[k], H[k]); H[k] = z; carved[k] = 0; if (e < 1 && d >= w) { deltaM[k] = 1; cells++; } }
    }
    if (cells < 30) return null;
    const [x, y] = toXY(ui, vi), [ox, oy] = toXY(ui + cx * Rd, vi + cy * Rd);   // (`r`: its width's half; it reaches ~1.45 r out)
    notes.push(`delta: ${Math.round(Rd * 2)} m across where the stream comes into the lake, in ${ends} arms -- ${ice ? "the meltwater's gravel" : clim.flows ? "the silt and sand it brings" : "what the floods bring"}, dropped where it slows`);
    return { x, y, u: ui, v: vi, r: Rd, arms: ends, out: [(ox - x) / Rd, (oy - y) / Rd] };
  })();
  Object.assign(c, { deltaM, delta });
}

export function tributary(c) {
  const { chanW, cone, dx, F, fallU, gorgeL, gorgeW, H, lake, N, outliers, R, scarpU, seed, size, sOf, streamV, toXY } = c;
  // a TRIBUTARY: a side stream off the upland into the gorge -- its valley HANGS over it: the gorge was cut down by all
  // the stream's water, the side valley only by its own little, so where they meet it falls in over the gorge's wall.
  // Its way: from the gorge's rim out across the upland (leaning upstream: side streams join pointing down the main
  // one) to the scene's edge, where its own catchment's water comes in; on the side away from the lake and the outliers
  const trib = (() => {
    if (F.tributary === false || F.waterfall === false || gorgeL < 40) return null;
    const uj = fallU + gorgeL * (.22 + R() * .15), lean = .5 + R() * .35, sg0 = R() < .5 ? 1 : -1, rim = gorgeW(sOf(uj)) / 2 + 3;
    for (const sg of [sg0, -sg0]) {
      const way = [];
      for (let t = 0; t < size * 2; t++) {
        const v = streamV(uj) + sg * (rim + t), u = uj - t * lean + (14 * fbm(t / 30, sg * 3.1, seed + 17, 3) + 4 * Math.sin(t / 9 + sg)) * smooth(t / 25), [x, y] = toXY(u, v);
        if (x < 1 || y < 1 || x > size - 1 || y > size - 1) break;
        if (u > scarpU(v) - 8 || (lake && lake.r * lake.dist(u, v) < lake.r + 10) || (cone && Math.hypot(cone.x - x, cone.y - y) < cone.Rb + 8) || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + 10)) { way.length = 0; break; }
        way.push([x, y]);
      }
      if (way.length < 40) continue;
      way.reverse();
      // (its bed: the ground less a valley deepening downstream -- not much: it is a small stream -- never rising)
      const L = way.length, hAt0 = (x, y) => H[clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1)];
      const zs = way.map(([x, y], q) => hAt0(x, y) - 1.2 - 1.8 * q / L);
      for (let q = 1; q < L; q++) zs[q] = Math.min(zs[q], zs[q - 1] - .01);
      return { way, zs, sg, w: chanW * .6 };
    }
    return null;
  })();
  Object.assign(c, { trib });
}

export function ravines(c) {
  const { capK, chanW, clim, coast, cone, domes, dx, F, fanBase, fans, gorgeL, gorgeW, H, half, lake, N, notes,
    outliers, S, scarp2U, scarpU, sCross, seed, size, slide, STEP2, streamV, toUV, toXY, trib, U, upAt, V } = c;
  let { lam, su, T } = c;
  // RAVINES: where it is wet and not frozen the water off the upland does not go over the cliff's edge as a sheet -- it
  // gathers in hollows and cuts back into the cap, each a ravine with a stream after rain: V-shaped, winding a little,
  // steep at its head (where it is still cutting back) and graded toward its mouth, some forked at the head; what it
  // cut spread as a CONE at its foot, flatter than a couloir's (water laid it, not falling rock). On karst fewer: the
  // rain goes down, and its valleys are dry. Its own random numbers
  const ravines = [];
  (() => {
    if (F.ravines === false || clim.temp < 4 || clim.rain < 450) return;
    const RV = rng(seed * 271 + 7), sp = 28 + RV() * 18, gw = gorgeL > 0 ? gorgeW(sCross) / 2 : chanW * 3, karst = S.beds[capK].karst;
    for (let vq = -half * 1.4 + RV() * sp; vq < half * 1.4; vq += sp * (.75 + .5 * RV())) {
      if (karst && RV() < .5) continue;
      const su = scarpU(vq), Lr = (18 + RV() * 22) * (clim.rain > 1200 ? 1.2 : 1), wh = 6 + RV() * 5, [mx, my] = toXY(su + 2, vq), [hx, hy] = toXY(su - Lr, vq);
      if (Math.min(mx, my, hx, hy) < 18 || Math.max(mx, my, hx, hy) > size - 18) continue;
      const ztop = upAt(hx, hy, su - Lr), zlow = H[Math.round(my / dx) * N + Math.round(mx / dx)] - 1, ch = ztop - zlow; if (ch < 6) continue;
      const T = clamp(ch * (.07 + RV() * .05), 1, 2.4), rc = ch * (.8 + RV() * .4) + 10, fork = RV() < .4 ? (RV() < .5 ? -1 : 1) : 0;
      let ok = Math.abs(vq - streamV(su)) > gw + wh + 12 && Math.abs(vq - streamV(su - Lr)) > wh + 12 && (!coast || coast.line(vq) - su > rc + 14) && (!STEP2 || scarp2U(vq) - su > rc + 10);
      ok &&= !slide || Math.abs(vq - slide.v) > slide.Wl + rc;
      ok &&= !outliers.some((o) => Math.hypot(o.u - su, o.v - vq) < o.r + rc + 6) && !fans.some((f) => Math.hypot(f.x - mx, f.y - my) < f.r + rc);
      ok &&= !cone || (Math.hypot(cone.x - mx, cone.y - my) > cone.Rb + rc + 6 && Math.hypot(cone.x - hx, cone.y - hy) > cone.Rb + 8);
      ok &&= !lake || lake.dist(su - Lr - 4, vq) > 1.4;
      ok &&= !domes.some((d) => Math.hypot(d.x - mx, d.y - my) < d.r + rc);
      ok &&= !trib || !trib.way.some(([x, y]) => { const [u, v] = toUV(x, y); return u > su - Lr - 12 && Math.abs(v - vq) < wh + 12; });
      ok &&= !ravines.some((c) => Math.abs(c.v - vq) < (c.r + rc) * .5 + 8);
      if (!ok) continue;
      // (its axis winding; a fork: a second head branching off two fifths of the way up, aslant)
      const amp = 1.2 + RV() * 2, lam = 16 + RV() * 12, ph = RV() * TAU, b0 = Lr * (.35 + RV() * .15), Lf = Lr * (.85 + RV() * .2);
      const R0 = Math.ceil((Lr + Lf * .7 + rc) / dx), [ox, oy] = toXY(su, vq), i0 = Math.round(ox / dx), j0 = Math.round(oy / dx);
      for (let j = Math.max(0, j0 - R0); j <= Math.min(N - 1, j0 + R0); j++) for (let i = Math.max(0, i0 - R0); i <= Math.min(N - 1, i0 + R0); i++) {
        const k = j * N + i, b = su - U[k], x = i * dx, y = j * dx; if (b < -8) continue;
        const wob = amp * Math.sin(TAU * b / lam + ph) * smooth(b / 8), dv = V[k] - vq - wob;
        let z = Infinity;
        for (let q = 0; q < (fork ? 2 : 1); q++) {
          const off = q ? fork * Math.max(0, b - b0) * .75 : 0, Lq = q ? Lf : Lr; if (q && b < b0) continue;
          if (b > Lq) continue;
          const hw = 1.8 + (wh - 1.8) * clamp((b + 8) / (Lq + 8), 0, 1) ** .7, a = Math.abs(dv - off) / hw; if (a >= 1) continue;
          const zf = zlow + ch * clamp((b + 8) / (Lq + 8), 0, 1) ** 2 + .3 * noise(x / 3.5, y / 3.5, seed + 267);
          z = Math.min(z, zf + (H[k] - zf) * a ** 1.4);
        }
        if (z < H[k]) { H[k] = z; fanBase[k] = Math.min(fanBase[k], z); }
      }
      ravines.push({ u: su, v: vq, x: mx, y: my, L: Lr, T, r: rc, fork: !!fork, wide: true });
    }
    if (ravines.length) notes.push(`ravines: ${ravines.length} cut back ${Math.round(Math.min(...ravines.map((c) => c.L)))}-${Math.round(Math.max(...ravines.map((c) => c.L)))} m into the cliff's edge by the water off the upland${ravines.some((c) => c.fork) ? ", some forked at the head" : ""}; a cone of what they cut at each one's foot${karst ? " -- fewer on the limestone, which the rain goes down" : ""}`);
  })();
  Object.assign(c, { ravines, lam, su, T });
}
