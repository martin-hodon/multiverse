// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- dry country: the playa, yardangs, barchans, tinajas, the slot
// canyon, fins, hoodoos. Each stage takes the scene so far, `c`, and adds what it makes to it; landscape.js runs them
// in order.
import { TAU, clamp, smooth, lerp, noise, fbm, rng } from "./core.js";

export function playa(c) {
  const { clim, F, lake, lipZ, n, notes, seed } = c;
  // a PLAYA: where the climate cannot keep the lake and no stream runs all year to fill it, what the storms wash in
  // settles out as the water dries -- a dead-flat floor of mud, salt crusted on it, cracked in polygons as it shrinks;
  // on the bowl's sides the shorelines it left when it stood higher, in wetter times: benches, one over another
  const PLAYA = !!lake && !clim.lakes && !clim.flows && F.playa !== false;
  const playaM = new Uint8Array(n);   // 1 the bowl, 2 its flat floor
  if (PLAYA) { lake.playa = { floor: lake.level - .4 - lake.depth * .5, lines: 2 + (seed % 2) }; }
  (() => {
  if (PLAYA) notes.push(`playa: the climate is too dry to keep a lake -- ${lake.why}, floored dead flat with what the storms washed in, salt crusted on the mud and cracked in polygons; ${lake.playa.lines} old shorelines on its sides, from when it stood higher`);
  else if (lake && !clim.lakes && !clim.flows) notes.push(`lake: the climate is too dry to keep one -- a pan in ${lake.why}`);
  else if (lake) notes.push(`lake: ${Math.round(lake.r * 2)} m across, ${lake.why}; its level the lip's (${lipZ.toFixed(1)} m)`);
  })();
  Object.assign(c, { PLAYA, playaM });
}

export function yardangs(c) {
  const { dx, F, fanBase, H, lake, N, notes, PLAYA, playaM, seed, toXY } = c;
  let { R } = c;
  // YARDANGS: on a playa the wind is the only thing that works -- it scours the old lake's mud where nothing holds it,
  // and what it has not yet taken stands in ridges along its way: blunt and steep to it, tapering away from it (an
  // upturned hull), in rows with the floor scoured flat between -- on the floor and the low benches over it. Its own
  // random numbers
  const yardangs = [];
  (() => {
    if (!PLAYA || F.yardangs === false) return;
    const RY = rng(seed * 251 + 5), wa = RY() * TAU, ca = Math.cos(wa), sa = Math.sin(wa), fl = lake.playa.floor;
    const [lx, ly] = toXY(lake.u, lake.v), sc = 7 + RY() * 2, sl = 15 + RY() * 4, R = lake.r * 1.6;
    const floorAt = (x, y) => { const i = Math.round(x / dx), j = Math.round(y / dx); return i >= 0 && j >= 0 && i < N && j < N && playaM[j * N + i] && H[j * N + i] < fl + 1.2; };
    for (let c = -R; c <= R; c += sc) for (let a = -R + (Math.round(c / sc) & 1) * sl * .5; a <= R; a += sl) {
      const Ly = 9 + RY() * 5, Wy = Ly * (.3 + RY() * .08), hy = 1 + RY() * 1;
      const a0 = a + (RY() - .5) * sl * .4, c0 = c + (RY() - .5) * sc * .4, X = (p, q) => [lx + p * ca - q * sa, ly + p * sa + q * ca];
      if (fbm((lx + a0) / 20, (ly + c0) / 20, seed + 249, 2) < -.25) continue;   // (in patches)
      let ok = true;   // (the whole of it on the floor, a little to spare)
      for (const [p, q] of [[-1.5, 0], [Ly * .2, 0], [Ly * .6, 0], [Ly + 1, 0], [Ly * .3, Wy * .5 + 1.5], [Ly * .3, -Wy * .5 - 1.5], [Ly * .7, Wy * .4 + 1], [Ly * .7, -Wy * .4 - 1]]) ok &&= floorAt(...X(a0 + p, c0 + q));
      if (!ok) continue;
      const [hx, hy2] = X(a0, c0), r0 = Math.ceil((Ly + 2) / dx), i0 = Math.round(hx / dx), j0 = Math.round(hy2 / dx);
      for (let j = Math.max(0, j0 - r0); j <= Math.min(N - 1, j0 + r0); j++) for (let i = Math.max(0, i0 - r0); i <= Math.min(N - 1, i0 + r0); i++) {
        const k = j * N + i, ox = i * dx - hx, oy = j * dx - hy2, t = (ox * ca + oy * sa) / Ly, q = -ox * sa + oy * ca; if (t <= 0 || t >= 1) continue;
        const w = Wy / 2 * (t < .25 ? Math.sqrt(t / .25) : 1 - .85 * ((t - .25) / .75) ** 1.4), hc = hy * (t < .1 ? Math.sqrt(smooth(t / .1)) : 1 - .9 * ((t - .1) / .9) ** 1.2);
        const e = Math.abs(q) / w; if (e >= 1) continue;
        const z = fl + hc * (1 - e * e) ** .35 + .05 * noise(i * dx / 1.5, j * dx / 1.5, seed + 253);
        if (z > H[k]) { H[k] = z; fanBase[k] = Math.max(fanBase[k], z); playaM[k] = 3; }
      }
      yardangs.push({ x: hx, y: hy2, a: wa, L: Ly, w: Wy, h: hy });
    }
    if (yardangs.length) notes.push(`yardangs: ${yardangs.length} ridges of the old lake's mud on the playa, up to ${Math.max(...yardangs.map((y) => y.h)).toFixed(1)} m, streamlined along the wind -- blunt to it, tapering away; the floor between them it scoured`);
  })();
  Object.assign(c, { yardangs, R });
}

export function barchans(c) {
  const { carved, clim, coast, cone, domes, dryness0, dune, dx, F, fans, H, knockM, lake, N, notes, outliers, playaM,
    ravines, S, scarp2U, scarpU, seed, size, slide, STEP2, streamV, toUV } = c;
  let { R } = c;
  // BARCHANS: in a desert the wind drives the sand loose over the lowland -- where there is too little to cover it, it
  // gathers in crescents: a long gentle back to the wind, a slip face at the sand's angle on the lee, and the horns
  // running on ahead of the middle (the sand there is thinner, and moves faster). Each its own size, the small ones
  // ahead (they move faster); the wind the yardangs' (the region's). Loose. Their own random numbers
  const barchans = [];
  (() => {
    if (F.barchans === false || dryness0 < .7 || clim.flows) return;
    const RB = rng(seed * 277 + 3), wa = rng(seed * 251 + 5)() * TAU, ca = Math.cos(wa), sa = Math.sin(wa);
    if (RB() > (F.barchans?.chance ?? .75)) return;
    const want = S.beds.some((b) => b.rock === "sandstone") ? 4 + Math.floor(RB() * 6) : 2 + Math.floor(RB() * 4);
    for (let t = 0; t < 400 && barchans.length < want; t++) {
      const W = 18 + RB() ** 1.5 * 30, h = W * (.11 + RB() * .04), x = 10 + RB() * (size - 20), y = 10 + RB() * (size - 20), [u, v] = toUV(x, y), R = W * .9;
      if (Math.min(x, y, size - x, size - y) < R + 4) continue;
      if (u < scarpU(v) + R * .6 + 10 || Math.abs(v - streamV(u)) < R * .7 + 10 || (coast && coast.line(v) - u < R + 22) || (STEP2 && Math.abs(u - scarp2U(v)) < R * .6 + 10)) continue;
      if (lake && lake.r * lake.dist(u, v) < lake.r + R + 8) continue;
      if (fans.some((f) => Math.hypot(f.x - x, f.y - y) < f.r + R * .5) || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + R + 6) || (cone && Math.hypot(cone.x - x, cone.y - y) < cone.Rb + R + 8)) continue;
      if ((slide && Math.hypot(slide.x - x, slide.y - y) < slide.Lb + R) || domes.some((d) => Math.hypot(d.x - x, d.y - y) < d.r + R + 4) || ravines.some((c) => Math.hypot(c.x - x, c.y - y) < c.r + R)) continue;
      if (barchans.some((o) => Math.hypot(o.x - x, o.y - y) < (o.W + W) * .62)) continue;
      const k0 = Math.round(y / dx) * N + Math.round(x / dx); if (knockM[k0] || playaM[k0]) continue;
      barchans.push({ x, y, W, h });
    }
    let cells = 0;
    for (const o of barchans) {
      // (across it, q from -1 to 1 horn to horn: the brink bowed on ahead toward the horns, the toe of the back behind
      // it; the back rising to the crest, the lee left to SETTLE: it slumps to the sand's angle, the slip face)
      const Ra = o.W * .42, Rc = o.W * .5, Rr = Math.ceil(o.W * 1.1 / dx), i0 = Math.round(o.x / dx), j0 = Math.round(o.y / dx);
      for (let j = Math.max(0, j0 - Rr); j <= Math.min(N - 1, j0 + Rr); j++) for (let i = Math.max(0, i0 - Rr); i <= Math.min(N - 1, i0 + Rr); i++) {
        const k = j * N + i, x = i * dx - o.x, y = j * dx - o.y, a = x * ca + y * sa, q = (-x * sa + y * ca) / Rc; if (Math.abs(q) >= 1) continue;
        const at = -Ra * Math.sqrt(1 - q * q), ab = Ra * (.08 + 1.25 * q * q); if (a < at) continue;
        if (a > ab) { if (a < ab + 1.8 * o.h * (1 - q * q) ** .8 + 1 && !carved[k]) dune[k] = 3; continue; }   // (where the slip face will slump to)
        const t = o.h * (1 - q * q) ** .8 * ((a - at) / (ab - at)) ** .85 * (1 + .06 * noise(i * dx / 5, j * dx / 5, seed + 269));
        if (t > .1 && !carved[k]) { H[k] += t; dune[k] = 3; cells++; }
      }
    }
    if (cells) notes.push(`barchans: ${barchans.length} crescent dunes on the lowland, ${Math.round(Math.min(...barchans.map((o) => o.W)))}-${Math.round(Math.max(...barchans.map((o) => o.W)))} m from horn to horn, up to ${Math.max(...barchans.map((o) => o.h)).toFixed(1)} m -- the wind's sand where there is too little to cover the ground: a gentle back to the wind, a slip face on the lee, the horns running on ahead`);
    else barchans.length = 0;
  })();
  Object.assign(c, { barchans, R });
}

export function tinajas(c) {
  const { capK, clim, dist, domes, dryness, dx, F, H, lake, n, N, notes, rock, S, scarpU, seed, size, soil, streamV,
    toUV, trib } = c;
  // TINAJAS: on a dry country's bare sandstone the rain that stands in a hollow dissolves the cement round the grains
  // and the wind takes them -- the hollow deepens to a pothole, flat-floored, its sides undercut: in groups along the
  // slickrock's shallow ways, 2-6 m across; after a rain the water stands in them (more of them the wetter). Its own
  // random numbers. On granite the same with the water's own weathering: GNAMMAS -- the rain that stands in a dip rots
  // the feldspar, the next wind or rain takes the grit: round pans, shallow, flat-floored, on the bare slabs (a dome's
  // top if there is one), in any climate but a frozen one
  const tinajas = [], tinM = new Uint8Array(n), slabM = new Uint8Array(n), ruwares = [];   // (tinM: 1 a pothole, 2 the bare rock round it; slabM: a ruware's bare granite)
  (() => {
  const GN = S.beds[capK].rock === "granite" && clim.temp >= 3 && F.gnammas !== false;
  if (F.tinajas === false || !GN && (S.beds[capK].rock !== "sandstone" || dryness < .25)) return;
  const RJ = rng(seed * 223 + 19);
  const slopeAt = (k) => Math.hypot(H[k + 1] - H[k - 1], H[k + N] - H[k - N]) / (2 * dx);
  const flat = (x, y, sl) => { const i = Math.round(x / dx), j = Math.round(y / dx); if (i < 4 || j < 4 || i > N - 5 || j > N - 5) return false;
    const k = j * N + i, [u, v] = toUV(x, y);
    return u < scarpU(v) - 12 && Math.abs(v - streamV(u)) > 16 && !(lake && lake.dist(u, v) < 1.4) && slopeAt(k) < sl && !(trib && trib.way.some(([tx, ty]) => Math.hypot(tx - x, ty - y) < 12)); };
  // (a pothole: its rim the lowest of its edge -- the water stands to the spill -- flat-floored; the rock round it bare)
  const pan = (x, y, r, depth) => {
    const k0 = Math.round(y / dx) * N + Math.round(x / dx), rim = Math.min(H[k0], ...[[-1, 0], [1, 0], [0, -1], [0, 1]].map(([a, b]) => H[k0 + Math.round(b * r / dx) * N + Math.round(a * r / dx)]));
    tinajas.push({ x, y, r, rim, depth, wet: RJ() < 1.15 - dryness * .7 });
    for (let j = Math.floor((y - r * 2.2) / dx); j <= Math.ceil((y + r * 2.2) / dx); j++) for (let i = Math.floor((x - r * 2.2) / dx); i <= Math.ceil((x + r * 2.2) / dx); i++) {
      const k = j * N + i, d = Math.hypot(i * dx - x, j * dx - y) / r; if (d >= 2.2) continue;
      if (d < 1) { const z = rim - depth * smooth((1 - d) / .3); if (z < H[k]) { H[k] = rock[k] = z; soil[k] = 0; } tinM[k] = 1; }
      else if (!tinM[k]) { tinM[k] = 2; H[k] = rock[k] = H[k] - soil[k]; soil[k] = 0; }   // (round it the bare rock: what fills it, the wind took)
    }
  };
  if (!GN) {
    const ok = (x, y) => flat(x, y, .14) && soil[Math.round(y / dx) * N + Math.round(x / dx)] < .4 && S.bedAt(x, y, H[Math.round(y / dx) * N + Math.round(x / dx)] - .3) === capK;
    for (let g = 0, groups = 0; g < 60 && groups < 4; g++) {
      const gx = 20 + RJ() * (size - 40), gy = 20 + RJ() * (size - 40); if (!ok(gx, gy)) continue;
      groups++; const ga = RJ() * TAU, m = 3 + Math.floor(RJ() * 6);
      for (let q = 0; q < m; q++) {
        const t = (q - m / 2) * (4 + RJ() * 3), x = gx + Math.cos(ga) * t + (RJ() - .5) * 4, y = gy + Math.sin(ga) * t + (RJ() - .5) * 4, r = 1 + RJ() * 2;
        if (!ok(x, y) || tinajas.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r + 1)) continue;
        pan(x, y, r, .5 + r * .35);
      }
    }
    if (tinajas.length) notes.push(`tinajas: ${tinajas.length} potholes in the bare ${S.beds[capK].name}, ${Math.round(Math.min(...tinajas.map((o) => o.r * 2)))}-${Math.round(Math.max(...tinajas.map((o) => o.r * 2)))} m across, up to ${Math.max(...tinajas.map((o) => o.depth)).toFixed(1)} m deep -- the rain stood in hollows and ate the cement round the grains; ${tinajas.filter((o) => o.wet).length} hold the last rain's water`);
    return;
  }
  // (granite: the pans want bare rock, and the upland is under its till -- a dome's crown, else a RUWARE or two: a low
  // whaleback of the sound granite just out of the till, the next dome's beginning, a metre or two high, bare)
  const hosts = domes.length ? [{ x: domes[0].x, y: domes[0].y, r: domes[0].r * .3 }] : [];
  const cand = []; for (let y = 24; y < size - 24; y += 4) for (let x = 24; x < size - 24; x += 4) if (flat(x, y, .1)) cand.push([x, y]);
  for (let t = 0; t < 30 && ruwares.length < (domes.length ? 1 : 2) && cand.length; t++) {
    const [x, y] = cand[Math.floor(RJ() * cand.length)], R0 = 9 + RJ() * 7, hR = .7 + RJ() * 1.1, a0 = RJ() * Math.PI, el = 1.15 + RJ() * .35;
    if (hosts.some((o) => Math.hypot(o.x - x, o.y - y) < o.r * 1.6 + R0 + 12) || !flat(x + R0, y, .14) || !flat(x - R0, y, .14) || !flat(x, y + R0, .14) || !flat(x, y - R0, .14)) continue;
    const ca = Math.cos(a0), sa = Math.sin(a0), Rb = R0 * el * 1.15;
    for (let j = Math.floor((y - Rb) / dx); j <= Math.ceil((y + Rb) / dx); j++) for (let i = Math.floor((x - Rb) / dx); i <= Math.ceil((x + Rb) / dx); i++) {
      const px = i * dx - x, py = j * dx - y, q = Math.hypot((px * ca + py * sa) / (R0 * el), (py * ca - px * sa) / (R0 / el)) * (1 + .1 * fbm(i * dx / 7, j * dx / 7, seed + 293, 2)), k = j * N + i;
      if (q >= 1) continue;
      const z = H[k] - soil[k] + (hR + soil[k]) * smooth((1 - q) / .45) + .12 * noise(i * dx / 3, j * dx / 3, seed + 295);   // (its edge out of the till, its back rounded)
      if (z > H[k] - soil[k] * (1 - q)) { H[k] = rock[k] = z; soil[k] = 0; slabM[k] = 1; }
    }
    ruwares.push({ x, y, r: R0, h: hR }); hosts.push({ x, y, r: R0 * .55 });
  }
  for (const o of hosts) for (let q = 0, m = 2 + Math.floor(RJ() * 4); q < m * 3 && tinajas.filter((p) => Math.hypot(p.x - o.x, p.y - o.y) < o.r * 1.2).length < m; q++) {
    const a = RJ() * TAU, rr = Math.sqrt(RJ()) * o.r * .85, x = o.x + Math.cos(a) * rr, y = o.y + Math.sin(a) * rr, r = .8 + RJ() * Math.min(1.7, o.r * .2);
    if (tinajas.some((p) => Math.hypot(p.x - x, p.y - y) < p.r + r + 1)) continue;
    pan(x, y, r, .25 + r * .15);
  }
  if (ruwares.length) notes.push(`ruware${ruwares.length > 1 ? "s" : ""}: ${ruwares.map((o) => `${Math.round(o.r * 2)} m`).join(", ")} across -- low whalebacks of the sound ${S.beds[capK].name} just out of the till, bare`);
  if (tinajas.length) notes.push(`gnammas: ${tinajas.length} pans in the bare ${S.beds[capK].name}${domes.length ? " (on the dome's crown)" : " (on the ruwares)"}, ${Math.round(Math.min(...tinajas.map((o) => o.r * 2)))}-${Math.round(Math.max(...tinajas.map((o) => o.r * 2)))} m across, up to ${Math.max(...tinajas.map((o) => o.depth)).toFixed(1)} m deep -- the standing rain rotted the feldspar and the wind took the grit; ${tinajas.filter((o) => o.wet).length} hold water`);
  })();
  const hLin = (x, y) => { const fx = clamp(x / dx, 0, N - 1.001), fy = clamp(y / dx, 0, N - 1.001), i = fx | 0, j = fy | 0, a = fx - i, b = fy - j, k = j * N + i;
    return lerp(lerp(H[k], H[k + 1], a), lerp(H[k + N], H[k + N + 1], a), b); };
  Object.assign(c, { tinajas, tinM, slabM, ruwares, hLin });
}

export function slot(c) {
  const { capK, capT, carved, clim, dist, dx, F, FAULT, H, hLin, lake, n, N, notes, outliers, rock, S, scarpU, seed,
    size, soil, streamV, toXY } = c;
  let { lam, pts, v0 } = c;
  // a SLOT CANYON: in sandstone country not too wet (the floods are flash floods, the rock not rotted), a wash on the
  // upland that found a joint and cut down it through the cap faster than the walls could fall back -- a slot a metre
  // or three wide, as deep as the cap, winding (the joints' and the flood's swirl), widening on down; it ends in a
  // pour-off where it comes out at the scarp, hung over the face. Cut after the settling: its walls are the rock's
  // own, standing sheer. Its own random numbers
  let slot = null;
  (() => {
  if (F.slot === false || S.beds[capK].rock !== "sandstone" || clim.rain > 900 || FAULT) return;
  const RT = rng(seed * 89 + 29);
  for (let t = 0; t < 30 && !slot; t++) {
    const v0 = (RT() - .5) * size * .8, u0 = scarpU(v0) - 45 - RT() * 40, A = 2 + RT() * 3, lam = 14 + RT() * 10, ph = RT() * TAU;
    const pts = []; let phi = ph;   // (its bends not a wave: tighter and looser, wider and narrower as the joints and the flood had it)
    for (let u = u0; u < u0 + 160; u += .5) {
      phi += TAU * .5 / lam * (1 + .45 * noise((u - u0) / 17, 2.9, seed + 321));
      const v = v0 + A * (.75 + .45 * noise((u - u0) / 23, 4.1, seed + 321)) * Math.sin(phi + .6 * Math.sin(2 * phi)) + 6 * fbm(u / 40, 5.3, seed + 95, 2), [x, y] = toXY(u, v);
      if (x < 8 || y < 8 || x > size - 8 || y > size - 8) { pts.length = 0; break; }
      pts.push([x, y, u, v]);
      if (u > scarpU(v) + 14) break;
    }
    if (pts.length < 60 || pts.some(([, , u, v]) => Math.abs(v - streamV(u)) < 32 || (lake && lake.r * lake.dist(u, v) < lake.r + 14) || outliers.some((o) => Math.hypot(o.x - toXY(u, v)[0], o.y - toXY(u, v)[1]) < o.r + 12))) continue;
    // (its floor: deeper on down, never rising, never steeper than 0.3; where the ground falls away under it -- the scarp's
    // face -- the pour-off: it ends)
    const L = pts.length, out = [];
    let fz = Infinity;
    for (let q = 0; q < L; q++) {
      const [x, y] = pts[q], g = hLin(x, y), deep = Math.min(capT * .92, .3 + q * .5 * .35);
      if (q > 8 && g < fz - .3) break;
      fz = q ? Math.max(Math.min(fz - .02, g - deep), fz - .15) : g - deep; out.push([x, y, fz, 1.1 + 1.7 * q / L + .5 * fbm(q * .05, 9.1, seed + 97, 2), g]);
    }
    if (out.length < 50 || out[out.length - 1][2] > hLin(out[0][0], out[0][1]) - capT * .6) continue;
    // (cut: the floor across its width, the walls sheer, a little rounded lip at the top)
    const lowZ = new Float32Array(n).fill(Infinity);
    for (const [x, y, z, w] of out) { const r = w / 2 + 1.2;
      for (let j = Math.floor((y - r) / dx); j <= Math.ceil((y + r) / dx); j++) for (let i = Math.floor((x - r) / dx); i <= Math.ceil((x + r) / dx); i++) {
        const k = j * N + i, d = Math.hypot(i * dx - x, j * dx - y); if (d > r) continue;
        lowZ[k] = Math.min(lowZ[k], d < w / 2 ? z : H[k] - .6 * (1 - (d - w / 2) / 1.2) ** 2);
      } }
    for (let k = 0; k < n; k++) if (lowZ[k] < H[k]) { H[k] = lowZ[k]; rock[k] = Math.min(rock[k], lowZ[k]); soil[k] = Math.max(0, H[k] - rock[k]); carved[k] = 1; }
    slot = { pts: out.map(([x, y, z, w]) => ({ x, y, z, w })), depth: Math.max(...out.map((p) => p[4] - p[2])) };
    notes.push(`slot canyon: ${out.length * .5 | 0} m long, ${slot.pts[0].w.toFixed(1)}-${slot.pts[out.length - 1].w.toFixed(1)} m wide, down to ${slot.depth.toFixed(0)} m deep in the ${S.beds[capK].name} -- a wash that found a joint; it hangs over the scarp in a pour-off`);
  }
  })();
  Object.assign(c, { slot, lam, pts, v0 });
}

export function fins(c) {
  const { capK, capT, carved, clim, dist, dx, F, FAULT, H, hLin, lake, n, N, notes, rock, S, scarpU, seed, size, slot,
    soil, streamV, toXY, trib } = c;
  let { ja, pts, v0 } = c;
  // FINS: in sandstone country that is dry, where the cap's joints run on in a set out to the scarp, the rain going
  // down them widened them into corridors -- the rock between left standing in FINS, a few metres thick, as tall as
  // the cap; and where a fin's softer patch weathered through, a window that grew to an ARCH (a cave patch, below).
  // Each corridor's floor falls to the scarp and ends where the ground falls away under it, as the slot's. Their own
  // random numbers
  const fins = [];
  let archAt = null;
  (() => {
  if (F.fins === false || S.beds[capK].rock !== "sandstone" || clim.rain > 700 || FAULT) return;
  const RF = rng(seed * 97 + 31);
  for (let t = 0; t < 40 && !fins.length; t++) {
    const vc = (RF() - .5) * size * .8, uc = scarpU(vc), P = 7 + RF() * 3, nC = 4 + Math.floor(RF() * 3), Lc = 28 + RF() * 16;
    const ja = (RF() - .5) * .7, d = [Math.cos(ja), Math.sin(ja)];   // (the joints' way in the (u, v) frame: out to the scarp, give or take 20 deg)
    const ok = (u, v) => { const [x, y] = toXY(u, v); return x > 8 && y > 8 && x < size - 8 && y < size - 8 && Math.abs(v - streamV(u)) > 36 &&
      !(lake && lake.r * lake.dist(u, v) < lake.r + 14) && !(slot && slot.pts.some((p) => Math.hypot(p.x - x, p.y - y) < 14)) &&
      !(trib && trib.way.some(([wx, wy]) => Math.hypot(wx - x, wy - y) < 14)); };
    const lines = [], RJ = rng(seed * 331 + 7 + t);   // (each joint opened its own way back from the brink, not quite straight)
    for (let c = 0; c < nC; c++) {
      const off = (c - (nC - 1) / 2) * P, Lj = Lc * (.65 + RJ() * .6), v0 = vc + off * d[0], u0 = uc - Lj - off * d[1], pts = [];
      for (let q = 0; q < (Lj + 20) * 2; q++) { const w = .7 * noise(q * .5 / 11, 6.7 + c * 3.1, seed + 323), u = u0 + d[0] * q * .5 - d[1] * w, v = v0 + d[1] * q * .5 + d[0] * w; if (!ok(u, v)) { pts.length = 0; break; } pts.push(toXY(u, v)); }
      if (!pts.length) break;
      lines.push(pts);
    }
    if (lines.length < nC) continue;
    // (each corridor's floor: down through the cap over its first 10 m, then falling gently out to the brink)
    const cors = lines.map((pts) => { const out = []; let fz = Infinity;
      for (let q = 0; q < pts.length; q++) { const [x, y] = pts[q], g = hLin(x, y), deep = Math.min(capT * .9, .3 + q * .5 * .6);
        if (q > 8 && g < fz - .3) break;
        fz = !q ? g - deep : q < 20 ? Math.min(fz - .02, g - deep) : Math.max(Math.min(fz - .02, g - deep), fz - .15); out.push([x, y, fz, 2.4 + .9 * RF() + .5 * fbm(q * .07, 3.3 + lines.indexOf(pts), seed + 99, 2), g]); }
      return out; });
    if (cors.some((c) => c.length < 40 || Math.max(...c.map((p) => p[4] - p[2])) < capT * .6)) continue;
    // (the arch: in a middle fin, where both corridors beside it are deep; its window from a little over their floors)
    const c = Math.floor((nC - 1) / 2), A = cors[c], B = cors[c + 1], q = Math.floor(Math.min(A.length, B.length) * (.45 + RF() * .2));
    const [ax, ay, az, , ag] = A[q], [bx, by, bz, , bg] = B[q], top = (ag + bg) / 2 - .3, z0 = Math.max(az, bz), rz = Math.min(3.4, (top - z0 - 1.6) / 2);
    if (rz > 1.2) archAt = { a: [ax, ay], b: [bx, by], z0, rz, r: P / 2 + .2 + RF() * .4, top };   // (through the fin, short of the next)
    const lowZ = new Float32Array(n).fill(Infinity);
    for (const cor of cors) for (const [x, y, z, w] of cor) { const r = w / 2 + .8;
      for (let j = Math.floor((y - r) / dx); j <= Math.ceil((y + r) / dx); j++) for (let i = Math.floor((x - r) / dx); i <= Math.ceil((x + r) / dx); i++) {
        const k = j * N + i, dd = Math.hypot(i * dx - x, j * dx - y); if (dd > r) continue;
        lowZ[k] = Math.min(lowZ[k], dd < w / 2 ? z : H[k] - .5 * (1 - (dd - w / 2) / .8) ** 2);
      } }
    for (let k = 0; k < n; k++) if (lowZ[k] < H[k]) { H[k] = lowZ[k]; rock[k] = Math.min(rock[k], lowZ[k]); soil[k] = Math.max(0, H[k] - rock[k]); carved[k] = 1; }
    for (const cor of cors) fins.push(cor.map(([x, y, z, w]) => ({ x, y, z, w })));
    notes.push(`fins: ${nC - 1} of the ${S.beds[capK].name}, ${(P - 3).toFixed(0)} m thick, between corridors its joints were widened into` + (archAt ? `; an arch through one, its window ${(archAt.r * 2).toFixed(0)} m across` : ""));
  }
  })();
  Object.assign(c, { fins, archAt, ja, pts, v0 });
}

export function hoodoos(c) {
  const { bed, coneM, cut, dryness, dune, dx, erod, F, H, kind, n, N, notes, S, seed, shoreK, size, slope, tufa } = c;
  // HOODOOS: in a dry country, where a soft bed lies bare under a hard one (shale under sandstone, tuff under basalt,
  // marl under limestone), the rain cuts the slope below the scarp into pillars -- each a column of the soft bed, its
  // top where the hard bed's base runs (it is what is left of it: a cap, a slab that keeps the rain off it, the column
  // waisted under it), in clusters where the slope is the bed's for its whole height. Some have lost their caps and are
  // wearing to a point. Their own random numbers; nothing grows on them
  const hoodoos = [], hoodM = new Uint8Array(n);
  (() => {
  if (F.hoodoos === false || dryness <= 0) return;
  const RH = rng(seed * 79 + 19);
  const at = (x, y) => {   // (a column's room here: its height, or 0)
    const i = Math.round(x / dx), j = Math.round(y / dx); if (i < 2 || j < 2 || i > N - 3 || j > N - 3) return 0;
    const k = j * N + i, q = bed[k];
    if (!q || erod[q] < .3 || S.beds[q - 1].hard < .5 || kind[k] || cut[k] || coneM[k] || shoreK[k] || dune[k] || tufa[k]) return 0;
    const deg = Math.atan(slope[k]) * 180 / Math.PI, h = S.topOf(x, y, q) - H[k];
    return deg > 14 && deg < 44 && h > 3 && h < Math.min(14, S.beds[q].t) ? h : 0;
  };
  const nC = 1 + Math.round(2 * dryness), per = 4 + Math.round(10 * dryness);
  for (let c = 0, t = 0; c < nC && t < 400; t++) {
    const cx = 10 + RH() * (size - 20), cy = 10 + RH() * (size - 20);
    if (!at(cx, cy) || hoodoos.some((o) => Math.hypot(o.x - cx, o.y - cy) < 30)) continue;
    let made = 0;
    for (let a = 0; a < per * 8 && made < per; a++) {
      const ang = RH() * TAU, d = Math.sqrt(RH()) * (6 + per), x = cx + Math.cos(ang) * d, y = cy + Math.sin(ang) * d, h0 = at(x, y);
      if (!h0) continue;
      const r = clamp(h0 * .19, 1, 2.6) * (.75 + RH() * .5);
      if (hoodoos.some((o) => Math.hypot(o.x - x, o.y - y) < (o.r + r) * 1.15)) continue;
      const q = bed[Math.round(y / dx) * N + Math.round(x / dx)], capped = RH() < .78;
      const h = capped ? h0 - RH() * h0 * .1 : h0 * (.55 + RH() * .3), capH = capped ? Math.min(S.beds[q - 1].t * .5, .5 + RH() * 1.1) : 0;
      hoodoos.push({ x, y, z: H[Math.round(y / dx) * N + Math.round(x / dx)] - .4, h: h + .4, r, cap: capped ? { r: r * (.95 + RH() * .3), h: capH } : null, bed: q, capBed: q - 1 });
      made++;
    }
    if (made >= 3) c++;
    else hoodoos.splice(hoodoos.length - made, made);   // (two make no cluster)
  }
  for (const o of hoodoos) { const rr = Math.ceil(o.r + 1), i0 = Math.round(o.x / dx), j0 = Math.round(o.y / dx);
    for (let b = -rr; b <= rr; b++) for (let a = -rr; a <= rr; a++) { const i = i0 + a, j = j0 + b;
      if (i >= 0 && j >= 0 && i < N && j < N && Math.hypot(a, b) * dx < o.r + .8) hoodM[j * N + i] = 1; } }
  if (hoodoos.length) notes.push(`hoodoos: ${hoodoos.length} -- columns of the ${S.beds[hoodoos[0].bed].name}, the ${S.beds[hoodoos[0].capBed].name} still capping most`);
  })();
  Object.assign(c, { hoodoos, hoodM });
}
