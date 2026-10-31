// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- WATER: the lakes filled, the water gathered down the land, the
// streams, the falls. Each stage takes the scene so far, `c`, and adds what it makes to it; landscape.js runs them in
// order.
import { clamp, lerp, rng, N8, heap } from "./core.js";

export function water(c) {
  const { benchK, braid, braidM, capK, carved, caves, chanD, chanW, clim, coast, cone, cu, dolines, dx, entry, F,
    fall2U, fallH, fallU, FAULT, flooded, gorge2L, gorgeL, H, hLin, kettleM, lake, lipZ, mark, mouth, n, N, notes, plan,
    playaM, pool2R, poolR, profAt, rock, S, scarpU, seed, sFall2, size, sOf, soft2K, softK, soil, STEP2, streamV, su,
    tinajas, toXY, travL, travM, trib, U, V } = c;
  let { along, pts, v0 } = c;
  // WATER: every hollow filled to where it spills (priority flood from the edge: the water's surface W), the water
  // gathered down it (each cell's rain and what flows in), the lakes where W stands over the ground, the streams
  const W = new Float32Array(n), done = new Uint8Array(n), order = new Int32Array(n);
  const runoff = Math.max(.02, clim.rain / 1000 - clim.evap / 1000 * .5);   // m/yr that runs off
  const Q = new Float32Array(n), down = new Int32Array(n);
  const route = () => {
    done.fill(0);
    const hp = heap(W); let o = 0;
    // (the water leaves by the edge: all of the lowland's, and the upland's where it stands over the lip -- the land going
    // on, the water that falls there running off it -- but not where the stream comes in, which brings water, not takes it)
    const [ex, ey] = entry ? toXY(...entry) : [-1e9, -1e9], [tx, ty] = trib ? trib.way[0] : [-1e9, -1e9];
    for (let k = 0; k < n; k++) { const i = k % N, j = (k / N) | 0; if (!(i === 0 || j === 0 || i === N - 1 || j === N - 1)) continue;
      if (U[k] > scarpU(V[k]) + 10 || (Math.hypot(i * dx - ex, j * dx - ey) > 30 && Math.hypot(i * dx - tx, j * dx - ty) > 15 && H[k] > lipZ + .5)) { W[k] = coast ? Math.max(H[k], coast.sea) : H[k]; done[k] = 1; hp.push(k); } }   // (the sea: at its level)
    // (and down a doline's swallow hole: its lowest cell)
    for (const o of dolines) { let lo = -1; for (let j = Math.max(0, Math.floor((o.y - o.r) / dx)); j <= Math.min(N - 1, Math.ceil((o.y + o.r) / dx)); j++) for (let i = Math.max(0, Math.floor((o.x - o.r) / dx)); i <= Math.min(N - 1, Math.ceil((o.x + o.r) / dx)); i++) { const k = j * N + i; if (lo < 0 || H[k] < H[lo]) lo = k; }
      if (lo >= 0 && !done[lo]) { W[lo] = Math.max(H[lo], o.wt ?? -Infinity); done[lo] = 1; hp.push(lo); o.sink = lo; } }   // (a cenote's: the water table)
    // (and a maar's: its floor's middle, at the water table)
    if (cone?.maar) { const lo = Math.round(cone.y / dx) * N + Math.round(cone.x / dx); if (!done[lo]) { W[lo] = Math.max(H[lo], cone.wt); done[lo] = 1; hp.push(lo); } }
    while (hp.size) {
      const k = hp.pop(); order[o++] = k;
      const i = k % N, j = (k / N) | 0;
      for (const [a, b] of N8) {
        const ii = i + a, jj = j + b; if (ii < 0 || jj < 0 || ii >= N || jj >= N) continue;
        const m = jj * N + ii; if (done[m]) continue;
        done[m] = 1; W[m] = Math.max(H[m], W[k] + 1e-4); hp.push(m);
      }
    }
    // discharge: in the reverse of the fill's order every cell hands its water to its lowest neighbour on W
    Q.fill(runoff * dx * dx); down.fill(-1);
    for (let o = n - 1; o >= 0; o--) {
      const k = order[o], i = k % N, j = (k / N) | 0;
      let best = -1, bw = W[k];
      for (const [a, b] of N8) { const ii = i + a, jj = j + b; if (ii < 0 || jj < 0 || ii >= N || jj >= N) continue; const m = jj * N + ii; if (W[m] < bw) { bw = W[m]; best = m; } }
      down[k] = best;
      if (best >= 0) Q[best] += Q[k];
    }
  };
  route();
  // a spring's stream: its way down as the water finds it, cell by cell -- in steps across a flat -- smoothed, and its
  // channel cut along that; then the water routed again
  (() => {
    let again = false;
    for (const c of caves) if (c.kind === "spring cave" && clim.flows) {
      const i0 = clamp(Math.round((c.mouth[0] + cu * 2) / dx), 0, N - 1), j0 = clamp(Math.round((c.mouth[1] + su * 2) / dx), 0, N - 1), way = [];
      for (let k = j0 * N + i0, g = 0; k >= 0 && g < 4 * N && !carved[k]; k = down[k], g++) way.push([(k % N) * dx, ((k / N) | 0) * dx, H[k]]);
      if (way.length < 8) continue;
      for (let pass = 0; pass < 4; pass++) for (let q = 2; q < way.length - 2; q++) for (const e of [0, 1]) way[q][e] = (way[q - 2][e] + way[q - 1][e] + way[q][e] + way[q + 1][e] + way[q + 2][e]) / 5;
      for (let q = 1; q < way.length; q++) way[q][2] = Math.min(way[q][2], way[q - 1][2] - .01);   // (its bed falling all the way)
      const w = chanW * .8;
      for (const [x, y, z] of way) for (let j = Math.floor((y - w) / dx); j <= Math.ceil((y + w) / dx); j++) for (let i = Math.floor((x - w) / dx); i <= Math.ceil((x + w) / dx); i++) {
        if (i < 0 || j < 0 || i >= N || j >= N) continue;
        const d = Math.hypot(i * dx - x, j * dx - y); if (d >= w) continue;
        const k = j * N + i, t = z - chanD * .7 * (1 - (d / w) ** 2);
        if (t < H[k]) { H[k] = t; rock[k] = Math.min(rock[k], t); soil[k] = Math.max(0, H[k] - rock[k]); }
      }
      again = true;
    }
    if (again) route();
  })();
  // the stream that comes in from beyond the scene: its catchment upstream, added where it enters
  const inflow = (clim.flows ? 8e6 : 1e6) * runoff;   // m3/yr (a catchment of some 10 km2 above the scene)
  (() => {
  if (entry) { const [x, y] = toXY(...entry); const i = clamp(Math.round(x / dx), 0, N - 1), j = clamp(Math.round(y / dx), 0, N - 1);
    for (let k = j * N + i, g = 0; k >= 0 && g < 4 * N; k = down[k], g++) Q[k] += inflow; }
  // (and the side stream's, a small one's)
  if (trib) { const [x, y] = trib.way[2]; for (let k = clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1), g = 0; k >= 0 && g < 4 * N; k = down[k], g++) Q[k] += inflow * .08; }
  })();
  // a spring: what the karst upland swallowed, out at the cave's mouth (and on down the slope from it)
  (() => {
  for (const c of caves) if (c.kind === "spring cave" && clim.flows) {
    const i = clamp(Math.round((c.mouth[0] + cu * 2) / dx), 0, N - 1), j = clamp(Math.round((c.mouth[1] + su * 2) / dx), 0, N - 1);
    for (let k = j * N + i, g = 0; k >= 0 && g < 4 * N; k = down[k], g++) Q[k] += inflow * (trib?.ponor ? .2 : .12); }   // (and the sinking stream's)
  })();
  // the water: a lake where W stands over the ground (a climate too dry for one leaves a pan: the hollow, damp);
  // a stream where enough gathers -- its surface a little over its bed
  const water = new Float32Array(n).fill(-Infinity), flow = new Float32Array(n), kind = new Uint8Array(n);   // kind: 0 dry, 1 lake, 2 stream, 3 fall
  const STREAM = 2.5e4 * runoff * (clim.flows ? 1 : 4);
  // (a hollow is a lake only if it is one: 60 m2 and half a metre deep at least -- the ground's little dips are not)
  const pond = new Uint8Array(n);
  { const seen = new Uint8Array(n), stack = [];
    for (let k0 = 0; k0 < n; k0++) {
      if (seen[k0] || W[k0] - H[k0] <= .08) continue;
      const cells = []; let deep = 0; stack.push(k0); seen[k0] = 1;
      while (stack.length) { const k = stack.pop(); cells.push(k); deep = Math.max(deep, W[k] - H[k]); const i = k % N, j = (k / N) | 0;
        for (const [a, b] of N8) { const ii = i + a, jj = j + b; if (ii < 0 || jj < 0 || ii >= N || jj >= N) continue; const m = jj * N + ii; if (!seen[m] && W[m] - H[m] > .08) { seen[m] = 1; stack.push(m); } } }
      // (a lake a stream runs through all year stays full whatever the climate takes from it: 2)
      const through = clim.flows && cells.some((k) => Q[k] > STREAM * 4);
      if ((cells.length * dx * dx >= 60 || kettleM[k0]) && deep >= .5) for (const k of cells) pond[k] = through ? 2 : 1;   // (a kettle is one, however small)
    } }
  (() => {
  for (let k = 0; k < n; k++) {
    if (playaM[k]) { if (pond[k] && H[k] < lake.playa.floor - .08) { water[k] = lake.playa.floor - .05; kind[k] = 1; } }   // (dry, but for a skin of brine where the floor dips)
    else if (pond[k] && (clim.lakes || pond[k] === 2 || W[k] - H[k] > 1.5)) { water[k] = clim.lakes || pond[k] === 2 ? W[k] : H[k] + Math.min(.4, W[k] - H[k]); kind[k] = 1; }
    else if (Q[k] > STREAM && (clim.flows || carved[k])) {
      const d = clamp(.08 * Math.log10(Q[k] / STREAM + 1) * (clim.flows ? 2 : .6), .04, .5);
      water[k] = H[k] + d; kind[k] = 2; flow[k] = Q[k];
    }
  }
  })();
  // (a hot spring's pools: each full to its rim)
  for (let k = 0; k < n; k++) if (travM[k] === 2) { water[k] = Math.max(H[k] + .05, travL[k]); kind[k] = 1; }
  // (a braid's threads: each takes a share of the stream)
  if (braid && clim.flows) for (let k = 0; k < n; k++) if (braidM[k] === 2 && !kind[k]) { water[k] = H[k] + .15; kind[k] = 2; flow[k] = STREAM * 2; }
  // the sea: what lies under its level and is open to it -- whatever the climate (kind 4)
  (() => {
  for (const o of tinajas) if (o.wet) { const lv = o.rim - o.depth * .4;   // (a tinaja's water: the last rain's, part gone)
    for (let j = Math.floor((o.y - o.r) / dx); j <= Math.ceil((o.y + o.r) / dx); j++) for (let i = Math.floor((o.x - o.r) / dx); i <= Math.ceil((o.x + o.r) / dx); i++) {
      const k = j * N + i; if (k >= 0 && k < n && H[k] < lv && !kind[k]) { water[k] = lv; kind[k] = 1; } } }
  if (coast) for (let k = 0; k < n; k++) if (H[k] < coast.sea && W[k] <= coast.sea + .01) { water[k] = coast.sea; kind[k] = 4; flow[k] = 0; }
  })();
  // falls: a stream cell whose water drops more than 1.2 m to the next one down
  const falls = [];
  (() => {
  for (let k = 0; k < n; k++) if (kind[k] === 2 && down[k] >= 0 && H[k] - H[down[k]] > 1.2 * dx) { kind[k] = 3; falls.push(k); }
  })();
  // the streams' water spread to their banks (a cell beside a stream cell, under its surface)
  // (from what was water before the pass: else a spread cell spreads it on, down every slope)
  (() => {
  for (let pass = 0; pass < 2; pass++) { const was = kind.slice(); for (let k = 0; k < n; k++) {
    if (kind[k]) continue;
    const i = k % N, j = (k / N) | 0;
    for (const [a, b] of N8) { const ii = i + a, jj = j + b; if (ii < 0 || jj < 0 || ii >= N || jj >= N) continue; const m = jj * N + ii;
      if ((was[m] === 2) && water[m] > H[k] + .02 && water[m] < H[k] + .6) { water[k] = water[m]; kind[k] = 2; flow[k] = flow[m] * .5; break; } }
  } }
  })();
  // the fall's curtain: the water leaves the lip at the speed it ran to it and falls, thrown clear of the wall where the
  // wall stands steep, sliding down it where the rock leans out further than the water is thrown (a cascade)
  // (each step's fall its own: the second's lip on the bench)
  // (`at(u)`: a point along the stream's way; the lip sought from `from` to `to`; `land`: where its pool is)
  const throwCurtain = (name, at, from, to, lipZ, land, wf = 1) => {
    const hAt = (x, y) => { const i = clamp(Math.round(x / dx), 0, N - 1), j = clamp(Math.round(y / dx), 0, N - 1); return H[j * N + i]; };
    const wAt = (x, y) => { const i = clamp(Math.round(x / dx), 0, N - 1), j = clamp(Math.round(y / dx), 0, N - 1); return water[j * N + i]; };
    // the lip as the ground has it: the last step before the drop
    // (the walls have settled back from where the plan drew them -- the lip with them)
    // (the first place it drops 3 m in the next 4 -- a step in the channel above is not the lip -- else where it drops most)
    let lu = to, best = -1;
    for (let u = from; u < to; u += .5) {
      const [x, y] = at(u), h = hAt(x, y); if (h < lipZ - 3) continue;
      let lo = h; for (let e = 1; e <= 4; e++) { const [x1, y1] = at(u + e); lo = Math.min(lo, hAt(x1, y1)); }
      if (h - lo > 3) { lu = u; break; }
      if (h - lo > best) { best = h - lo; lu = u; }
    }
    const [lx, ly] = at(lu), [nx, ny] = at(lu + 1), dl = Math.hypot(nx - lx, ny - ly) || 1, dir = [(nx - lx) / dl, (ny - ly) / dl];
    const top = Math.max(hAt(lx, ly) + .15, wAt(lx, ly)), [px, py] = land; let bot = Math.max(hAt(px, py), wAt(px, py));
    let q = 0; for (let j = -3; j <= 3; j++) for (let i = -3; i <= 3; i++) q = Math.max(q, Q[clamp(Math.round(ly / dx) + j, 0, N - 1) * N + clamp(Math.round(lx / dx) + i, 0, N - 1)]);
    q /= 3.15e7;   // m3/s
    // (in the air thrown: on at v0, down as it falls; on the rock sliding down it, as fast across as the rock lets it -- a
    // ledge it runs over and falls on from; where the rock is gentler than 45 deg for 3 m, it has landed: below, a stream)
    const v0 = clamp(.8 + q * 6, .8, 3), pts = [[lx, ly, top]];
    let x = lx, y = ly, z = top, vz = 0, onRock = false, flat = 0;
    for (let it = 0; it < 400; it++) {
      const step = onRock ? Math.max(v0 * .05, .3) : v0 * .05;
      x += dir[0] * step; y += dir[1] * step; vz += 9.8 * .05; z -= vz * .05;
      const g = hLin(x, y) + .3; onRock = g >= z;
      if (onRock) { z = g; vz = Math.min(vz, 2); }
      flat = onRock && top - z > 2 && hLin(x - dir[0], y - dir[1]) - hLin(x + dir[0], y + dir[1]) < 2 ? flat + step : 0;
      if (flat > 3) { bot = z - .3; pts.push([x, y, z]); break; }
      if (z <= bot + .4) { pts.push([x, y, bot]); break; }
      pts.push([x, y, z]);
    }
    // (smoothed: the cells' steps are not the rock's)
    for (let it = 0; it < 4; it++) for (let r = 1; r < pts.length - 1; r++) pts[r][2] = Math.min(pts[r - 1][2], (pts[r - 1][2] + pts[r][2] * 2 + pts[r + 1][2]) / 4);
    return { name, pts, w: chanW * (clim.flows ? 1.5 : .7) * wf, dir, q, top, bot };
  };
  let sideNote = null;
  const onStream = (u) => toXY(u, streamV(u));
  const curtains = F.waterfall !== false && gorgeL > 0 ? [throwCurtain("fall", onStream, fallU - 30, fallU + poolR, lipZ, toXY(fallU + poolR * .6, streamV(fallU)))] : [];
  if (STEP2 && F.waterfall !== false) curtains.push(throwCurtain("lower fall", onStream, fall2U - 30, fall2U + pool2R, profAt(sFall2 - 2) + chanD, toXY(fall2U + pool2R * .6, streamV(fall2U))));
  if (trib && !trib.ponor) {   // (along its way, and on past its end into the gorge)
    const { way, zs } = trib, L = way.length, [ax, ay] = way[L - 2], [bx, by] = way[L - 1];
    const along = (t) => { if (t < L - 1) { const q = Math.max(0, Math.floor(t)), f = t - q; return [lerp(way[q][0], way[q + 1][0], f), lerp(way[q][1], way[q + 1][1], f)]; } return [bx + (bx - ax) * (t - L + 1), by + (by - ay) * (t - L + 1)]; };
    const C = throwCurtain("side fall", along, L - 25, L + 8, zs[L - 1] + .6, along(L + 5), .45);
    curtains.push(C);
    sideNote = (`a side stream: its valley hangs ${(C.top - C.bot).toFixed(1)} m over the gorge -- the gorge cut down by all the stream's water, the side valley only by its own -- and it falls in over the wall` +
      (clim.flows ? "" : " (after storms)"));
  }
  // (the stream over the sea cliff, onto the cove's beach)
  if (coast?.cliffed) { const sL = sOf(coast.uL); curtains.push(throwCurtain("sea fall", onStream, coast.uL - 20, coast.uL + 6, profAt(sL - 3) + chanD, toXY(coast.uL + 5, streamV(coast.uL + 5)))); }
  plan.tributary = trib;
  // (the fall's form, its rock's: over basalt the columns break the lip into blocks -- the water comes down between
  // them in strands, a segmented fall; over a sandstone cap where much water runs, a broad sheet, the lip worn back
  // round in a curve as wide as the pool; a dry country's fall a ribbon. Its own random numbers)
  let fallForm = "plunge";
  (() => {
  const C0 = curtains[0]; if (!C0 || C0.name !== "fall" || C0.pts.length < 3) return;
  const RF = rng(seed * 157 + 73), px = -C0.dir[1], py = C0.dir[0];
  if (S.beds[capK].columns && clim.flows) {
    const nS = 2 + (RF() < .55 ? 1 : 0), Wt = C0.w * (1.9 + RF() * .4), w0 = C0.w;
    for (let q = 0; q < nS; q++) {
      const o = (q - (nS - 1) / 2) * Wt / nS + (RF() - .5) * .5, dz = q === Math.floor(nS / 2) ? 0 : RF() * .6, ws = w0 * (.2 + RF() * .1);
      const pts = C0.pts.map(([x, y, z], r) => [x + px * o, y + py * o, r === 0 ? z - dz : Math.max(C0.bot, z - dz)]);
      if (q === 0) { C0.pts = pts; C0.w = ws; } else curtains.push({ ...C0, name: "fall strand", pts, w: ws });
    }
    fallForm = "segmented";
  } else if (S.beds[capK].rock === "sandstone" && clim.flows && !FAULT) { C0.w *= 1.4 + RF() * .3; fallForm = "sheet"; }
  else if (!clim.flows) { C0.w *= .7; fallForm = "ribbon"; }
  })();
  plan.fallForm = fallForm;
  const curtain = curtains[0] ?? null;
  (() => {
  if (F.waterfall !== false) notes.push(`fall: ${fallH.toFixed(1)} m ${FAULT ? `over the fault's step in the ${S.beds[capK].name}` : `over the ${S.beds[capK].name} cap and the ${S.beds[softK].name} under it`}, into a pool ${Math.round(poolR * 2)} m across; ` +
    (clim.flows ? "it runs all year" : "a dry fall, a trickle after storms") +
    (fallForm === "segmented" ? "; the columns break its lip -- it comes down in strands between them" : fallForm === "sheet" ? "; a broad sheet off the worn sandstone lip" : ""));
  })();
  (() => {
  if (gorgeL > 0) notes.push(`gorge: ${Math.round(gorgeL)} m back from the scarp -- how far the fall has stepped back -- on the ${S.beds[benchK]?.name ?? S.beds[capK].name}`);
  if (sideNote) notes.push(sideNote);
  })();
  (() => {
  if (STEP2 && F.waterfall !== false) notes.push(`a second step: the ${S.beds[benchK].name} bench ends in a scarp of its own over the ${S.beds[soft2K].name}; ` +
    `the stream falls ${(profAt(sFall2 - 2) - profAt(sFall2 + 2)).toFixed(1)} m over it, its gorge ${Math.round(gorge2L)} m back (younger: the upper fall had stepped back past it first)`);
  })();
  plan.curtain = curtain; plan.curtains = curtains;
  mark("water");

  const HS = flooded.length ? H.slice() : H; for (let q = 0; q < flooded.length; q += 2) HS[flooded[q]] = flooded[q + 1];   // (the ground a flooded cave's patch draws)
  Object.assign(c, { W, done, order, runoff, Q, down, route, inflow, water, flow, kind, STREAM, pond, falls,
    throwCurtain, sideNote, onStream, curtains, fallForm, curtain, HS, along, pts, v0 });
}
