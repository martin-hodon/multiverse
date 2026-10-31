// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- the relief: the scarp, the upland and the lowland, the stream's
// plan, the outliers, the domes, the lake's hollow. Each stage takes the scene so far, `c`, and adds what it makes to
// it; landscape.js runs them in order.
import { TAU, clamp, smooth, lerp, noise, fbm, rng } from "./core.js";

export function relief(c) {
  const { bench2K, benchK, capK, depthTo, dx, F, H, N, n, relief, S, seed, size, softK, spec, TOP, U, V } = c;
  let { su } = c;
  // RELIEF: the scarp where the cap ends, wandering across the scene; the upland on the cap's top (a little relief:
  // the cap is hard), the lowland down on the beds under it, falling to the edge the water leaves by
  // (the lines along the scene -- the scarps', the stream's -- wanted at every cell, many times over, and dear: each read
  // from a table every 0.25 m)
  const tab = (fn) => { const t = new Float64Array(8 * size + 2); for (let q = 0; q < t.length; q++) t[q] = fn(q / 4 - size);
    return (w) => { const f = clamp((w + size) * 4, 0, t.length - 1.001), q = Math.floor(f); return t[q] + (t[q + 1] - t[q]) * (f - q); }; };
  const scarpU = tab((v) => (spec.scarpAt ?? size * .06) + size * .09 * fbm(v / (size * .45), 3.1, seed + 11, 3));   // (spec.scarpAt: landmap.js)
  // (a stack with no soft bed under its hard one -- granite under its till -- has no scarp of its own weathering: the
  // step is a fault's, the lowland the same rock let down)
  const FAULT = softK < 0 ? (12 + 8 * rng(seed * 31 + 7)()) * relief : 0;   // (how far it slipped: this place's own)
  const lowTop = FAULT ? TOP - depthTo(capK) - FAULT : TOP - depthTo(benchK >= 0 ? benchK : softK) - (benchK >= 0 ? 0 : 6);   // the lowland: on the bench's top
  // (granite rots deep and unevenly along its joints, and what rotted washed away: its upland ROLLS -- low swells and
  // shallow basins a hundred metres across, a few metres deep)
  const ROLL = S.beds[capK].rock === "granite" ? 2.4 : 0;
  const upAt = (x, y, u) => S.datum(x, y) + .9 * fbm(x / 40, y / 40, seed + 3, 3) + ROLL * fbm(x / 95, y / 95, seed + 305, 2) - .6 - u * .004;
  // (a STAIRCASE: where the stack has another hard bed over another soft one, the bench ends in a scarp of its own
  // further down, and the land steps down again -- as many steps as hard beds)
  const STEP2 = F.steps !== false && !FAULT && bench2K >= 0;
  const scarp2U = tab((v) => scarpU(v) + size * .27 + size * .05 * fbm(v / (size * .4), 5.3, seed + 13, 3));
  const lowTop2 = STEP2 ? TOP - depthTo(bench2K) : lowTop;
  (() => {
  for (let k = 0; k < n; k++) {
    const u = U[k], v = V[k], x = (k % N) * dx, y = ((k / N) | 0) * dx;
    const up = upAt(x, y, u), su = scarpU(v);
    if (u < su) { H[k] = up; continue; }   // (the upland: the lowland's numbers not wanted)
    let low = lowTop - 1.5 - (u - su) * .035 + 2.2 * fbm(x / 55, y / 55, seed + 4, 3);
    if (STEP2) { const su2 = scarp2U(v); if (u > su2) low = Math.min(low, lowTop2 - 1.5 - (u - su2) * .035 + 2.2 * fbm(x / 55, y / 55, seed + 6, 3)); }
    H[k] = Math.min(up, low);
  }
  })();
  Object.assign(c, { tab, scarpU, FAULT, lowTop, ROLL, upAt, STEP2, scarp2U, lowTop2, su });
}

export function plan(c) {
  const { R, scarpU, seed, size, spec, tab } = c;
  // PLAN: the stream -- in at the upland's edge, out at the lowland's -- wandering; where it reaches the scarp the fall
  // was, and it has stepped back up the stream since by the ravine's length, leaving the gorge; the lake above the lip
  const r0 = R(), v0 = spec.streamV ?? (r0 - .5) * size * .25;   // (spec.streamV: where the world wants it -- landmap.js)
  const streamV0 = tab((u) => v0 + size * .07 * (spec.wander ?? 1) * fbm(u / (size * .5), 7.7, seed + 21, 3));
  const cross = scarpU(streamV0(scarpU(0)));                                     // where the stream meets the scarp (u)
  Object.assign(c, { v0, streamV0, cross });
}

export function meanders(c) {
  const { clim, cross, scarp2U, size, STEP2, streamV0 } = c;
  // MEANDERS: down on the lowland's soft ground the stream wanders -- loops some 11 channel widths apart (as streams'
  // are), as wide as a quarter of that; on the upland and in the gorge the rock holds it straighter
  const chanW = clim.flows ? 2.6 : 1.8, chanD = clim.flows ? .9 : .5;
  const cross2 = STEP2 ? scarp2U(streamV0(cross + size * .27)) : Infinity, mStart = STEP2 ? cross2 : cross;   // (they wander below the last step)
  Object.assign(c, { chanW, chanD, cross2, mStart });
}

export function outliers(c) {
  const { capK, coast, cross, dx, F, FAULT, H, N, notes, R, S, scarpU, seed, size, streamV, toXY, U, upAt } = c;
  // OUTLIERS: the scarp has stepped back, and where the cap held a little longer it stands on out in front -- a butte, a
  // pinnacle (the small ones: a hoodoo, its cap on a column of the soft bed), a tower in karst. Planned as a piece of the
  // upland left standing; SETTLE makes the column and its skirt of scree. (A fault leaves none: it did not step back.)
  const outliers = [];
  (() => {
  if (F.outliers && !FAULT) {
    for (let q = 0, tries = 0; q < (F.outliers.count ?? 3) && tries < 40; tries++) {
      const side = R() < .5 ? -1 : 1, v = streamV(cross) + side * (25 + R() * size * .4), u = scarpU(v) + 14 + R() * 70;
      const r = q === 0 ? 18 + R() * 8 : 7 + R() * 3.5, [x, y] = toXY(u, v);   // (planned before the walls settle back: a butte loses some 8 m all round)
      if (x < r + 8 || y < r + 8 || x > size - r - 8 || y > size - r - 8) continue;
      if (Math.abs(v - streamV(u)) < r + 22 || (coast && u + r > coast.line(v) - 12) || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r + 14)) continue;
      outliers.push({ x, y, u, v, r }); q++;
    }
    for (const o of outliers) {
      const R0 = o.r + 2, i0 = Math.max(0, Math.floor((o.x - R0 * 1.5) / dx)), i1 = Math.min(N - 1, Math.ceil((o.x + R0 * 1.5) / dx));
      const j0 = Math.max(0, Math.floor((o.y - R0 * 1.5) / dx)), j1 = Math.min(N - 1, Math.ceil((o.y + R0 * 1.5) / dx));
      for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
        const x = i * dx, y = j * dx, a = Math.atan2(y - o.y, x - o.x), k = j * N + i;
        const rr = o.r * (1 + .3 * noise(Math.cos(a) * 1.4 + o.x, Math.sin(a) * 1.4, seed + 81));   // (its outline: where joints let it break)
        if (Math.hypot(x - o.x, y - o.y) < rr) H[k] = Math.max(H[k], upAt(x, y, U[k]));
      }
    }
    if (outliers.length) notes.push(`outliers: ${outliers.map((o) => o.r > 15 ? (S.beds[capK].karst ? "a tower" : "a butte") : S.beds[capK].karst ? "a pillar" : "a pinnacle").join(", ")} -- the ${S.beds[capK].name} where it held as the scarp stepped back`);
  }
  })();
  Object.assign(c, { outliers });
}

export function domes(c) {
  const { capK, clim, coast, dx, F, FAULT, H, mark, N, n, notes, S, scarpU, seed, size, streamV, toXY } = c;
  // a DOME: where it is warm, granite rots deep along its joints, but where they are few it holds -- and when the rotten
  // rock is washed away a dome of the sound rock is left standing over the land (a bornhardt, a sugarloaf), its sides
  // steepening to its foot, the sheets it splits off (unloading) peeling round it in shells; the cores of the rotten
  // blocks left as boulders round its foot. Below the till (the stack's top): it is all granite. Its own random numbers
  const domes = [], domeM = new Uint8Array(n);
  (() => {
  if (F.dome === false || S.beds[capK].rock !== "granite" || clim.temp < 15 || !FAULT) return;
  const RB = rng(seed * 107 + 43);
  for (let t = 0; t < 40 && !domes.length; t++) {
    const v = (RB() - .5) * size * .7, u = scarpU(v) + 35 + RB() * 70, [x, y] = toXY(u, v), i0 = Math.round(x / dx), j0 = Math.round(y / dx);
    if (x < 30 || y < 30 || x > size - 30 || y > size - 30) continue;
    const base = H[j0 * N + i0], hD = Math.min(30, S.datum(x, y) - S.base[1] - base - 1), R0 = clamp(hD * (1.2 + RB() * .5), 14, 30);   // (its top under the till's base; its width by its height)
    if (x < R0 + 10 || y < R0 + 10 || x > size - R0 - 10 || y > size - R0 - 10) continue;
    let near = false; for (let q = -R0; q <= R0 && !near; q += 4) near = Math.abs(v - streamV(u + q)) < R0 + 16;
    if (near || (coast && u + R0 > coast.line(v) - 14)) continue;
    if (hD < 9) continue;
    const a0 = RB() * Math.PI; domes.push({ x, y, u, v, r: R0, h: hD });   // (a0: the way it is longer, along its fewest joints)
    for (let j = Math.max(0, Math.floor((y - R0 * 1.3) / dx)); j <= Math.min(N - 1, Math.ceil((y + R0 * 1.3) / dx)); j++)
      for (let i = Math.max(0, Math.floor((x - R0 * 1.3) / dx)); i <= Math.min(N - 1, Math.ceil((x + R0 * 1.3) / dx)); i++) {
        const k = j * N + i, a = Math.atan2(j * dx - y, i * dx - x), rr = R0 * (1 + .12 * noise(Math.cos(a) * 1.2 + x, Math.sin(a) * 1.2, seed + 125)) * (1 + .15 * Math.cos(2 * (a - a0)));
        const q = Math.hypot(i * dx - x, j * dx - y) / rr; if (q >= 1) continue;
        const shell = .3 * smooth(Math.sin(q * 26 + a * .3) * .5 + .5) * q;   // (the sheets peeling off round it)
        H[k] = Math.max(H[k], base - .5 + hD * (1 - q ** 2.2) ** .6 + shell); domeM[k] = 1;
      }
  }
  if (domes.length) notes.push(`dome: ${Math.round(domes[0].r * 2)} m across, ${Math.round(domes[0].h)} m high -- the sound granite left standing where the rest rotted and washed away, its sheets peeling round it`);
  })();
  mark("relief");
  Object.assign(c, { domes, domeM });
}

export function lake(c) {
  const { capK, capT, clim, F, fallU, lipZ, S, size, streamV, toXY } = c;
  let { cu } = c;
  // the lake: a hollow on the upland above the lip, what made it by the climate and the rock
  const lake = F.lake ? (() => {
    // (inside the scene, with its shore and the stream coming into it: a lake cut by the edge is half a lake)
    // (its upper end drawn out by what made it: the ice's longest, up the way it came)
    const el = clim.temp < 4 ? 1.9 : S.beds[capK].karst ? 1.1 : S.beds[capK].rock === "basalt" ? 1.4 : 1.3;
    const room = (r) => { const cu = fallU - r * 1.35 - 13, [x, y] = toXY(cu, streamV(cu)), [xa, ya] = toXY(cu - r * el, streamV(cu - r * el));
      return Math.min(Math.min(x, y, size - x, size - y) - r, Math.min(xa, ya, size - xa, size - ya)) - 14; };
    let r = size * (F.lake.r ?? .13); while (r > 10 && room(r) < 0) r -= 1;
    const cu0 = fallU - r * 1.35 - 13, cv0 = streamV(cu0);
    const why = clim.temp < 4 ? "a hollow the ice scoured out of the cap" : S.beds[capK].karst ? "a doline: the limestone dissolved under it" :
      S.beds[capK].rock === "basalt" ? "a hollow between two lava flows' fronts" : S.beds[capK].rock === "granite" ? "a basin where the granite was jointed closest and rotted deepest, behind a sill of sound rock" :
      "a hollow behind a bar of harder cap the stream cuts through at the lip";
    // (how far out of it a place is, 1 its shore -- roughly: the outline's own wanders a little either side)
    const dist = (u, v) => Math.hypot((u - cu0) / (u > cu0 ? 1.3 : el), v - cv0) / r;
    return { u: cu0, v: cv0, r, el, dist, depth: Math.min(capT * .8, r * .12), level: lipZ, why, islands: F.lake.islands ?? 0 };
  })() : null;
  Object.assign(c, { lake, cu });
}

export function lakeHollow(c) {
  const { capK, carved, clim, dx, fanBase, H, lake, N, n, PLAYA, playaM, R, S, seed, U, V } = c;
  // the lake's hollow, and its islands -- each a hard knob the scouring left
  (() => {
  if (lake) {
    // (a lake the ice scoured has many, low and streamlined along the way the ice went -- smooth up-ice, broken off steep
    // down-ice: roches moutonnees, skerries; in other hollows the few the rest of the hollow left)
    const isl = [], ice = clim.temp < 4, count = ice ? lake.islands * 3 + 1 : lake.islands;
    for (let q = 0, t = 0; q < count && t < 60; t++) {
      const I = ice ? { u: lake.u + (R() - .62) * lake.r * 2.4, v: lake.v + (R() - .5) * lake.r * 1.3, r: lake.r * (.07 + R() * .07), h: .6 + R() * 1.6, el: 1.8 + R() * .6 }
                    : { u: lake.u + (R() - .5) * lake.r * .7, v: lake.v + (R() - .3) * lake.r * .5, r: lake.r * (.18 + R() * .12), h: 1.2 + R() * 2.5, el: 1 };
      if (lake.dist(I.u, I.v) > .72 || isl.some((o) => Math.hypot(o.u - I.u, o.v - I.v) < (o.r + I.r) * 1.6)) continue;
      isl.push(I); q++;
    }
    // (their form the rock's: basalt's and sandstone's a table, flat-topped, cliffs all round -- the bed held, the joints
    // let its edges go; limestone's a tower, the rain dissolving it from the sides, the taller the warmer; granite's a
    // dome; and now and then a smaller one off the first. Their own random numbers)
    const RI = rng(seed * 181 + 101), rk = S.beds[capK], form = ice ? "skerry" : rk.karst ? "tower" : rk.columns || rk.rock === "sandstone" ? "table" : "dome";
    if (!ice && isl.length && RI() < .45) { const I0 = isl[0], a = RI() * TAU, I = { u: I0.u + Math.cos(a) * I0.r * 2.2, v: I0.v + Math.sin(a) * I0.r * 2.2, r: I0.r * (.35 + RI() * .2), h: I0.h * .6, el: 1 };
      if (lake.dist(I.u, I.v) < .75) isl.push(I); }
    for (const I of isl) { if (form === "tower") { I.r *= .9; I.h = Math.min((3 + RI() * 4) * (clim.temp > 18 ? 1.5 : 1), I.r * 1.4) * (I === isl[0] ? 1 : .6); } else if (form === "table") I.h = (1.5 + RI() * 2.5) * (I === isl[0] ? 1 : .7); }
    lake.isles = isl; lake.isleForm = isl.length ? form : null;
    // (its outline what made it: the ice's long up the way it came, fingered; a doline's round; between two flows'
    // fronts lobed; in granite squared where the joints cut it; behind a bar, irregular. Its lower end, where it spills
    // to the lip, the same whatever: the shape is worked in from there round to its head)
    const rock0 = S.beds[capK].rock, RK = rng(seed * 109 + 47);
    const LS = ice ? { A: .2, Nl: 5, na: .26, ns: 10 } : S.beds[capK].karst ? { A: 0, Nl: 0, na: .1, ns: 25 } :
      rock0 === "basalt" ? { A: .32, Nl: 3, na: .14, ns: 20 } : rock0 === "granite" ? { A: .12, Nl: 4, na: .14, ns: 12, sq: 4 } : { A: .22, Nl: 3, na: .26, ns: 18 };
    LS.ph = RK() * TAU; LS.rot = (RK() - .5) * .9;
    for (let k = 0; k < n; k++) {
      const x = (k % N) * dx, y = ((k / N) | 0) * dx, du = (U[k] - lake.u) / (lake.r * (U[k] > lake.u ? 1.3 : lake.el)), dv = (V[k] - lake.v) / lake.r;
      const d = Math.sqrt(du * du + dv * dv); if (d > 1.6) continue;
      const th = Math.atan2(dv, du), m = (1 - Math.cos(th)) / 2;   // (0 at its lower end, 1 at its head)
      let dd = d; if (LS.sq) { const ca = Math.cos(LS.rot), sa = Math.sin(LS.rot), a = Math.abs(du * ca + dv * sa), b = Math.abs(-du * sa + dv * ca); dd = lerp(d, (a ** LS.sq + b ** LS.sq) ** (1 / LS.sq), m); }
      const q = dd / (1 + m * LS.A * Math.cos(LS.Nl * th + LS.ph)) + lerp(.18 * fbm(x / 25, y / 25, seed + 41, 3), LS.na * fbm(x / LS.ns, y / LS.ns, seed + 41, 3), m);
      if (q < 1) {
        let bed = lake.level - .4 - lake.depth * smooth(1 - q) - .3 * fbm(x / 8, y / 8, seed + 43, 2);
        if (PLAYA) {   // (the floor flat; the sides in benches, a riser over the upper third of each step)
          const fl = lake.playa.floor, top = lake.level - .4, Ls = lake.playa.lines + 1, e = clamp((bed - fl) / (top - fl), 0, 1) * Ls, i0 = Math.floor(e);
          bed = bed <= fl + .02 ? fl + .03 * fbm(x / 9, y / 9, seed + 197, 2) : lerp(bed, fl + (top - fl) * Math.min(1, (i0 + smooth((e - i0 - .62) / .38)) / Ls), .75);
          playaM[k] = bed <= fl + .06 ? 2 : 1;
        }
        H[k] = Math.min(H[k], q < .92 ? bed : lerp(bed, H[k], (q - .92) / .08));
        carved[k] = 0;
      }
      for (const I of isl) {
        const tu = (U[k] - I.u) / (I.r * I.el), di = Math.hypot(tu * (ice && tu > 0 ? 1.8 : 1), (V[k] - I.v) / I.r) + .25 * fbm(x / 6, y / 6, seed + 47, 2);
        if (di >= 1) continue;
        const f = form === "table" ? smooth((1 - di) / .25) : form === "tower" ? smooth((1 - di) / .28) : smooth(1 - di);
        const z = lake.level + (form === "tower" ? I.h * (f * (.78 + .08 * noise(x / 2.5, y / 2.5, seed + 51)) + .22 * (1 - Math.min(1, di / .72) ** 2))   // (sheer, fluted, its top domed)
          : I.h * (form === "table" ? f * (1 + .06 * fbm(x / 5, y / 5, seed + 49, 2)) : f ** .7)) - (1 - f) * 1.5;
        if (z > H[k]) { H[k] = z; fanBase[k] = Math.max(fanBase[k], z); if (PLAYA && z > lake.playa.floor + .15) playaM[k] = 1; }   // (rock: what the hollowing left, not a heap)
      }
    }
  }
  })();
}
