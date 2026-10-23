// THE WORLD'S LAND, GROWN (2026-09-28; docs/world.md "The grown map").
//
// The ground used to be three sines, with a lake, a river and moats carved into them to ONE water level. Now the terrain
// lab (terrain_lab.js, docs/terrain_lab.md) grows a piece of river country -- a big river from beyond the region cutting
// down through a layer cake as the land rises, the side streams it gathers, the falls where they drop over a hard bed --
// and the world is a window cut out of it:
//   GROW     the lab's "river" preset (20 m cells, 2.6 km across) for `years`, on the renderer's own GPU device
//   CUT      a window of the world's size along the big river, where its banks and the world's open places are
//            gentlest, turned so the river runs east (+x) about `riverZ` south of the middle -- where the old river ran,
//            so the town, the landing, the mill and the barge still find a river that runs east along z = riverZ(x)
//   UPSCALE  the lab's ground onto a 2 m grid (bicubic, with a little detail it could not hold)
//   SITES    the bridge, where both banks are flattest for the town (south) and its farms (north); the monument on the
//            facade line where the ground is flattest
//   SETTLE   the land eased (a smooth warp, ~110 m wide) so the town, the farms, the herd's meadow and the monument sit
//            on the old plain, height 0 -- the buildings are laid out on 0 and stay there -- with the river at the old
//            -2.2 m at the bridge
//   CARVE    the channels into it: the big river and every side stream with water enough, each at ITS OWN level,
//            falling downstream -- in steps where it falls -- not one level for all the water in the world
//   WATER    the surface over the grid (a channel's level in its channel, a lake's where the lab held one), how much of it
//            is river (the waves slide downstream there), and the distance to it (paths and walls keep off the water)
// Everything comes back as plain arrays and numbers: ground.js samples them, a worker can be handed them.
import { createLab, noise2, PRESETS } from "./terrain_lab.js";
import { PREGEN, recordFor, mapKey, fetchMap, packMap, pregenMiss, pregenOn } from "./pregen.js";   // (grown lands kept by build/pregen.py)
import { MAX_PIER_DEPTH } from "./village.js";   // (how deep a bridge pier may stand: the bridge site keeps within it)

const smooth = (t) => t * t * (3 - 2 * t);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const cr = (a, b, c, d, t) => b + 0.5 * t * (c - a + t * (2 * a - 5 * b + 4 * c - d + t * (3 * (b - c) + d - a)));
const QS = 3.156e7;                                                     // m3/yr in a m3/s
const widthOf = (Q) => clamp(4.5 * Math.sqrt(Q / QS), 1.2, 22);          // a channel's width by its discharge (hydraulic geometry)
const depthOf = (Q) => clamp(0.55 * Math.pow(Q / QS, 0.35), 0.25, 2.6);
const blur = (a, r) => a.map((_, k) => { let s = 0, c = 0; for (let q = Math.max(0, k - r); q <= Math.min(a.length - 1, k + r); q++) { s += a[q]; c++; } return s / c; });

// the lab's grid, sampled anywhere (metres in the lab's frame; cell (i, j) at (i dx, j dx))
function sampler(A, N, dx) {
  const get = (i, j) => A[clamp(j, 0, N - 1) * N + clamp(i, 0, N - 1)];
  return {
    cubic(u, v) {
      const x = u / dx, y = v / dx, i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j, r = [];
      for (let k = -1; k <= 2; k++) r.push(cr(get(i - 1, j + k), get(i, j + k), get(i + 1, j + k), get(i + 2, j + k), fx));
      return cr(r[0], r[1], r[2], r[3], fy);
    },
    lin(u, v) {
      const x = u / dx, y = v / dx, i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j;
      return (get(i, j) * (1 - fx) + get(i + 1, j) * fx) * (1 - fy) + (get(i, j + 1) * (1 - fx) + get(i + 1, j + 1) * fx) * fy;
    },
  };
}

// a COURSE across the lab: where water from cell c goes -- each time on to the lowest cell beside those it has reached
// (down the water surface; in a hollow, filling it until it spills over its lowest rim) -- until `stop` says it is there.
// (It followed the lab's discharge before -- to the neighbour carrying the most water -- and lost the big river where the
//  lab's last fill had left a hollow in its bed: the river's water stops there in the lab, and the course stopped with it.)
function course(c, N, W, stop) {
  const from = new Int32Array(N * N).fill(-2), heap = [c];   // (a binary heap of the cells reached, lowest first)
  const less = (a, b) => W[a] < W[b] || (W[a] === W[b] && a < b);
  const swap = (i, j) => { const t = heap[i]; heap[i] = heap[j]; heap[j] = t; };
  const push = (k) => { heap.push(k); for (let i = heap.length - 1, p; i > 0 && less(heap[i], heap[p = (i - 1) >> 1]); i = p) swap(i, p); };
  const pop = () => {
    const top = heap[0], last = heap.pop();
    if (heap.length) {
      heap[0] = last;
      for (let i = 0, m = 0; ; i = m) {
        const l = 2 * i + 1, r = l + 1;
        if (l < heap.length && less(heap[l], heap[m])) m = l;
        if (r < heap.length && less(heap[r], heap[m])) m = r;
        if (m === i) break;
        swap(i, m);
      }
    }
    return top;
  };
  from[c] = -1;
  while (heap.length) {
    const k = pop();
    if (k !== c && stop(k)) { const path = [k]; while (from[path[path.length - 1]] >= 0) path.push(from[path[path.length - 1]]); return path.reverse(); }
    const i = k % N, j = (k / N) | 0;
    for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
      const ii = i + di, jj = j + dj, m = jj * N + ii;
      if ((!di && !dj) || ii <= 0 || jj <= 0 || ii >= N - 1 || jj >= N - 1 || from[m] !== -2) continue;   // (the edge: walls copying what is inside)
      from[m] = k; push(m);
    }
  }
  return [c];
}

// radius: the world's; riverZ: where the river runs; meadow: the rectangle the herd's meadow takes (settled to 0);
// facade: { z, w, d, road } the monument's line (its middle's z), its footprint, and how far its road reaches in front
export async function growMap({ seed = 1, radius = 300, device = null, N = 128, years = 150000, riverZ = 150, res = 2,
                                meadow = { x0: -30, x1: 30, z0: -30, z1: 12 }, facade = { z: -80, w: 60, d: 50, road: 20 },
                                onProgress = null } = {}) {
  // ---- GROW (the lab's ages on the GPU: most of a start's waiting -- so pregen/ keeps the grown land by its seed, the
  //      fields the rest of this reads, and a land it has is fetched instead of grown)
  const mk = pregenOn() ? mapKey({ seed, N, years, preset: "river" }) : null;
  let grown = mk && PREGEN.ok.maps && PREGEN.manifest?.maps?.[mk] ? await fetchMap(mk).catch(() => null) : null;
  if (!grown) {
    const lab = await createLab(null, { N, device });
    lab.reset("river", { seed });
    const steps = Math.round(years / lab.params.dt);
    for (let s = 0; s < steps; s += 100) {
      lab.step(Math.min(100, steps - s));
      await lab.device.queue.onSubmittedWorkDone();
      onProgress?.(Math.min(1, (s + 100) / steps));
    }
    const st = await lab.stats(), { H, W, Q } = lab.last;
    grown = { stats: st, H: Float32Array.from(H), W: Float32Array.from(W), Q: Float32Array.from(Q), dx: lab.params.dx, inlet: [...lab.inlets[0]] };
    lab.destroy();
    if (mk) { pregenMiss("map", String(seed), mk); if (PREGEN.record) recordFor("maps", mk, { buf: packMap(grown), seed }); }
  }
  const { stats, H, W, Q, dx, inlet } = grown, Qin = inlet[2];
  const sH = sampler(H, N, dx), sW = sampler(W, N, dx), sD = sampler(W.map((w, i) => w - H[i]), N, dx);
  const slopeAt = (u, v) => Math.hypot(sH.lin(u + 5, v) - sH.lin(u - 5, v), sH.lin(u, v + 5) - sH.lin(u, v - 5)) / 10;

  // ---- the big river, from where it comes in, smoothed
  // (to where it leaves the lab: the cells along the edge by the preset's outlet)
  const border = (k) => { const i = k % N, j = (k / N) | 0; return i === 1 || j === 1 || i === N - 2 || j === N - 2; };
  const outlets = PRESETS.river.outlets.map(([x, y, w]) => [x * (N - 1) * dx, y * (N - 1) * dx, w]);
  const atOutlet = (k) => border(k) && outlets.some(([u, v, w]) => Math.hypot((k % N) * dx - u, ((k / N) | 0) * dx - v) <= w + 1.5 * dx);
  const main = course(clamp(Math.round(inlet[1] / dx), 1, N - 2) * N + clamp(Math.round(inlet[0] / dx), 1, N - 2), N, W, atOutlet);
  const mu = blur(main.map((c) => (c % N) * dx), 3), mv = blur(main.map((c) => ((c / N) | 0) * dx), 3);
  const arc = [0]; for (let k = 1; k < mu.length; k++) arc.push(arc[k - 1] + Math.hypot(mu[k] - mu[k - 1], mv[k] - mv[k - 1]));
  const along = (s) => {
    let k = 1; while (k < arc.length - 1 && arc[k] < s) k++;
    const t = clamp((s - arc[k - 1]) / Math.max(1e-6, arc[k] - arc[k - 1]), 0, 1);
    return [mu[k - 1] + (mu[k] - mu[k - 1]) * t, mv[k - 1] + (mv[k] - mv[k - 1]) * t];
  };

  // ---- CUT: the window, 2R across; game (x, z) = lab O + x e + z f
  const R = radius + 24, L = (N - 1) * dx;
  const toLab = (w, x, z) => [w.O[0] + x * w.e[0] + z * w.f[0], w.O[1] + x * w.e[1] + z * w.f[1]];
  const toGame = (w, u, v) => { const du = u - w.O[0], dv = v - w.O[1]; return [du * w.e[0] + dv * w.e[1], du * w.f[0] + dv * w.f[1]]; };
  const gentleShare = (w, pts) => pts.filter(([x, z]) => { const [u, v] = toLab(w, x, z); return slopeAt(u, v) < 0.06 && sD.lin(u, v) < 0.5; }).length / pts.length;
  const open = [];   // the open places: the meadow, the facade line
  for (let x = meadow.x0; x <= meadow.x1; x += 10) for (let z = meadow.z0; z <= meadow.z1; z += 10) open.push([x, z]);
  for (let x = -R + 60; x <= R - 60; x += 15) open.push([x, facade.z]);
  let best = null; const why = { tried: 0, outside: 0, back: 0, far: 0 };
  for (const flip of [1, -1]) for (let s = R; s < arc[arc.length - 1] - R; s += 30) {
    why.tried++;
    const a = along(s - R), b = along(s + R), P = along(s), el = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (el < 1) continue;
    const e = [(b[0] - a[0]) / el, (b[1] - a[1]) / el], f = [-e[1] * flip, e[0] * flip];   // (either bank may be the south)
    const w = { e, f, O: [P[0] - riverZ * f[0], P[1] - riverZ * f[1]] };
    if ([[-R, -R], [R, -R], [-R, R], [R, R]].some(([x, z]) => { const [u, v] = toLab(w, x, z); return u < 2 * dx || v < 2 * dx || u > L - 2 * dx || v > L - 2 * dx; })) { why.outside++; continue; }
    let ok = true, lastX = -1e9;   // the river across it always onward (east), within reach of riverZ
    for (let k = 0; k < mu.length && ok; k++) {
      const [x, z] = toGame(w, mu[k], mv[k]);
      if (Math.abs(x) > R + 30 || Math.abs(z) > R + 30) continue;
      if (x < lastX - 1) { ok = false; why.back++; }
      else if (Math.abs(x) < R * .85 && (z < riverZ - 70 || z > riverZ + 40)) { ok = false; why.far++; }
      lastX = Math.max(lastX, x);
    }
    if (!ok) continue;
    const banks = [];
    for (let x = -R + 60; x <= R - 60; x += 12) for (const dz of [-70, -45, -20, 20, 45, 70, 95, 120]) banks.push([x, riverZ + dz]);
    const score = gentleShare(w, banks) + 0.5 * gentleShare(w, open);
    if (!best || score > best.score) best = { ...w, score };
  }
  if (!best) throw new Error(`mapgen: no window along the river fits the world (${JSON.stringify(why)}; river ${main.length} cells, ${arc[arc.length - 1].toFixed(0)} m)`);
  const WIN = best;

  // ---- UPSCALE
  const n = Math.ceil(2 * R / res) + 1, x0 = -R, z0 = -R, NN = n * n;
  const base = new Float32Array(NN);
  const nz = noise2(seed * 7 + 3);
  const fbm = (x, z) => 0.55 * nz(x / 23, z / 23) + 0.3 * nz(x / 9 + 17, z / 9 + 5) + 0.15 * nz(x / 4 + 3, z / 4 + 11);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = x0 + i * res, z = z0 + j * res, [u, v] = toLab(WIN, x, z);
    base[j * n + i] = sH.cubic(u, v) + fbm(x, z) * (0.25 + Math.min(1.2, slopeAt(u, v) * 4));
  }
  const gAt = (i, j) => base[clamp(j, 0, n - 1) * n + clamp(i, 0, n - 1)];
  const groundAt = (x, z) => { const fi = (x - x0) / res, fj = (z - z0) / res, i = Math.floor(fi), j = Math.floor(fj), a = fi - i, b = fj - j;
    return (gAt(i, j) * (1 - a) + gAt(i + 1, j) * a) * (1 - b) + (gAt(i, j + 1) * (1 - a) + gAt(i + 1, j + 1) * a) * b; };

  // ---- the big river on the world's axes: its z, level and half width as functions of x, a metre apart
  const rx0 = -R - 40, nrx = Math.ceil(2 * (R + 40)) + 1;
  const pts = main.map((c, k) => { const [x, z] = toGame(WIN, mu[k], mv[k]); return { x, z, w: W[c] }; })
                  .filter((p) => p.x > rx0 - 60 && p.x < -rx0 + 60);
  const byX = (key) => Float32Array.from({ length: nrx }, (_, k) => {
    const x = rx0 + k; let q = 1; while (q < pts.length - 1 && pts[q].x < x) q++;
    const a = pts[q - 1], b = pts[q], t = clamp((x - a.x) / Math.max(1e-6, b.x - a.x), 0, 1);
    return a[key] + (b[key] - a[key]) * t;
  });
  const rz = Float32Array.from(blur(Array.from(byX("z")), 18));
  const lvl = Float32Array.from(blur(Array.from(byX("w")), 10));
  for (let k = 1; k < nrx; k++) lvl[k] = Math.min(lvl[k], lvl[k - 1]);   // (never rising downstream)
  const rAt = (arr, x) => { const f = clamp(x - rx0, 0, nrx - 1), k = Math.min(nrx - 2, Math.floor(f)), t = f - k; return arr[k] + (arr[k + 1] - arr[k]) * t; };
  const riverZf = (x) => rAt(rz, x);

  // ---- SITES: the bridge where both banks are flattest (the town south of it, x -65..+75 and 110 m deep; its farms
  // north); and no fall on the town's stretch
  const rough = (xa, xb, za, zb) => {   // how far the ground of a rectangle strays from its own mean, and how steep it is
    let s = 0, s2 = 0, k = 0, st = 0;
    for (let x = xa; x <= xb; x += 6) for (let z = za; z <= zb; z += 6) {
      const h = groundAt(x, z); s += h; s2 += h * h; k++;
      st += Math.abs(groundAt(x + 3, z) - groundAt(x - 3, z)) + Math.abs(groundAt(x, z + 3) - groundAt(x, z - 3));
    }
    const m = s / k; return { r: Math.sqrt(Math.max(0, s2 / k - m * m)) + 4 * st / k, mean: m };
  };
  const hw0 = widthOf(Qin) / 2, SWING = 6;   // (SWING: how far, m, the river may bend north or south of the bridge along the town)
  let bridgeX = 0, bestR = Infinity;
  // (all of it inside the world: the town's west wall 70 m up the river, the mill 95 m down it and its yard, the town
  //  110 m and more south of the bank; its river a quiet one -- the mill's wheel and the landing stand at its level --
  //  falling 2.5 m at most past it, more only if nowhere is quieter)
  for (const quiet of [2.5, Infinity]) {
    for (let xb = -radius + 95; xb <= radius - 135; xb += 5) {
      const zc = riverZf(xb), fallAcross = Math.abs(rAt(lvl, xb - 70) - rAt(lvl, xb + 125));
      if (zc + hw0 + 130 > radius || zc - hw0 - 85 < -radius || fallAcross > quiet) continue;
      // (and its piers, 4.9 m either side of the middle (village/bridge zPier), in water a pier can be footed in -- the bridge
      //  stands them on the bed; a gorge's deep channel is no bridge site)
      let deep = 0;
      for (const dz of [-5.6, -4.9, -4.2, 4.2, 4.9, 5.6]) for (const dx of [-2, 0, 2]) deep = Math.max(deep, rAt(lvl, xb) - groundAt(xb + dx, zc + dz));
      if (deep > MAX_PIER_DEPTH && quiet < Infinity) continue;
      // (and the river running PAST the town and the farms, not into them: the town is laid out from the bridge as though the
      //  river ran straight on east -- its streets 30 m and more south of the bank -- so a bend swinging south into it,
      //  or north into the farms, put a gatehouse or a row of houses over the channel, their plots left unlevelled there)
      let swing = 0;
      for (let x = xb - 70; x <= xb + 125; x += 5) swing = Math.max(swing, Math.abs(riverZf(x) - zc));
      if (swing > SWING && quiet < Infinity) continue;
      const t = rough(xb - 65, xb + 75, zc + hw0 + 8, zc + hw0 + 118), f = rough(xb - 60, xb + 60, zc - hw0 - 78, zc - hw0 - 8);
      // (and banks about as high over the water as a town's quay wants, 2.2 m: less to settle)
      const r = t.r + 0.7 * f.r + fallAcross
              + 0.6 * (Math.abs(t.mean - rAt(lvl, xb) - 2.2) + Math.abs(f.mean - rAt(lvl, xb) - 2.2));   // (a terrace over a gorge: all of it cut down to the water)
      if (r < bestR) { bestR = r; bridgeX = xb; }
    }
    if (bestR < Infinity) break;
  }
  const zb = riverZf(bridgeX);
  // the monument: the facade line's flattest stretch, clear of the meadow; it will be settled to 0, so ground already
  // near the town's height costs least
  const townH = rAt(lvl, bridgeX) + 2.2;   // (where the town will stand: 2.2 m over the river at the bridge)
  let monumentX = 0, bestM = Infinity;
  for (let x = -radius + facade.w / 2 + 30; x <= radius - facade.w / 2 - 30; x += 5) {   // (its road's turning loops too)
    if (x + facade.w / 2 > meadow.x0 - 10 && x - facade.w / 2 < meadow.x1 + 10 && facade.z + facade.d / 2 > meadow.z0) continue;
    const q = rough(x - facade.w / 2, x + facade.w / 2, facade.z - facade.d / 2, facade.z + facade.d / 2 + facade.road);
    const r = q.r + 0.15 * Math.abs(q.mean - townH);
    if (r < bestM) { bestM = r; monumentX = x; }
  }

  // ---- SETTLE: the whole land shifted so the river is at -2.2 at the bridge, then every place built on eased to 0
  const areas = [
    { x0: bridgeX - 70, x1: bridgeX + 125, z0: zb + hw0 + 6, z1: zb + hw0 + 122 },   // the town, its wall, the landing yard
    { x0: bridgeX - 65, x1: bridgeX + 105, z0: zb - hw0 - 82, z1: zb - hw0 - 5 },    // the farms, the mill, the quay
    meadow,
    { x0: monumentX - facade.w / 2 - 8, x1: monumentX + facade.w / 2 + 8, z0: facade.z - facade.d / 2 - 8, z1: facade.z + facade.d / 2 + facade.road },
  ];
  // (the river is never moved against its own valley: raised to meet a town on a terrace it ran on levees above it)
  const shift = -townH;
  for (let k = 0; k < NN; k++) base[k] += shift;
  for (let k = 0; k < nrx; k++) lvl[k] += shift;
  const bump = (a, x, z) => 1 - smooth(clamp(Math.hypot(Math.max(0, a.x0 - x, x - a.x1), Math.max(0, a.z0 - z, z - a.z1)) / 110, 0, 1));
  const lift = areas.map(() => 0);
  const warp = (x, z) => areas.reduce((s, a, k) => s + lift[k] * bump(a, x, z), 0);
  for (let it = 0; it < 4; it++) areas.forEach((a, k) => {   // (the bumps overlap: settle each against the others a few times)
    let s = 0, c = 0; for (let x = a.x0; x <= a.x1; x += 8) for (let z = a.z0; z <= a.z1; z += 8) { s += groundAt(x, z) + warp(x, z); c++; }
    lift[k] -= s / c;
  });
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) base[j * n + i] += warp(x0 + i * res, z0 + j * res);
  const levelf = (x) => rAt(lvl, x);

  // ---- CARVE: a channel's say at a sample d from its centre line -- the bed below its level, a low bank raised above it
  const carve = new Float32Array(NN), water = new Float32Array(NN).fill(NaN), riverness = new Float32Array(NN);
  const channel = (i, j, d, level, hw, depth) => {
    const k = j * n + i, nat = base[k] - carve[k];
    let y;
    if (d < hw) y = Math.min(nat, level - depth * (1 - (d / hw) ** 2));
    else {
      if (water[k] === water[k]) return;   // (a bank never fills another channel it crosses)
      const bank = level + Math.min(0.7, 0.35 * (d - hw));
      y = nat > bank ? bank + (nat - bank) * smooth(clamp((d - hw - 2) / 10, 0, 1)) : bank + (nat - bank) * smooth(clamp((d - hw - 6) / 12, 0, 1));
    }
    if (d < hw + 18) carve[k] = base[k] - y;
    if (d < hw + 2.5 && y < level && !(water[k] >= level)) water[k] = level;
  };
  // the landing's basin, 35 m below the bridge: the river widens there to hold the barge's turn
  const basin = { x: bridgeX + 35, len: 40, add: 10 };
  const rhw = Float32Array.from({ length: nrx }, (_, k) => hw0 + basin.add * Math.exp(-(((rx0 + k - basin.x) / basin.len) ** 2)));
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = x0 + i * res, z = z0 + j * res, dzdx = (riverZf(x + 1) - riverZf(x - 1)) / 2;
    const d = Math.abs(z - riverZf(x)) / Math.sqrt(1 + dzdx * dzdx), hw = rAt(rhw, x);
    if (d > hw + 26) continue;
    channel(i, j, d, levelf(x), hw, depthOf(Qin) * (1 + 0.15 * Math.exp(-(((x - basin.x) / basin.len) ** 2))));
    riverness[j * n + i] = Math.max(riverness[j * n + i], 1 - smooth(clamp((d - hw + 3) / 4, 0, 1)));
  }
  // the side streams: from the top down, each course with water enough traced until it meets one already drawn, at
  // its own level (the settled ground along it, never rising downstream: where the ground drops, the stream falls)
  const drawn = new Uint8Array(N * N); for (const c of main) drawn[c] = 1;
  const inWin = (c) => { const [x, z] = toGame(WIN, (c % N) * dx, ((c / N) | 0) * dx); return Math.abs(x) < R && Math.abs(z) < R; };
  const heads = []; for (let c = 0; c < N * N; c++) if (Q[c] > 5e5 && !drawn[c] && inWin(c)) heads.push(c);   // (a brook: 0.016 m3/s)
  heads.sort((a, b) => W[b] - W[a]);
  let nStreams = 0, drop = 0;
  for (const h of heads) {
    if (drawn[h]) continue;
    const path = course(h, N, W, (c) => drawn[c] === 1 || border(c));
    for (const c of path) drawn[c] = 1;
    if (path.length < 3) continue;
    nStreams++;
    const P = path.map((c) => toGame(WIN, (c % N) * dx, ((c / N) | 0) * dx));
    const xs = blur(P.map((p) => p[0]), 1), zs = blur(P.map((p) => p[1]), 1);
    const lv = path.map((_, k) => groundAt(xs[k], zs[k]) - 0.15);
    for (let k = 1; k < lv.length; k++) lv[k] = Math.min(lv[k], lv[k - 1]);
    for (let k = 0; k + 1 < xs.length; k++) {
      const ax = xs[k], az = zs[k], bx = xs[k + 1], bz = zs[k + 1], hw = widthOf(Q[path[k]]) / 2, reach = hw + 20;
      drop = Math.max(drop, (lv[k] - lv[k + 1]) / Math.max(1, Math.hypot(bx - ax, bz - az)));
      const len2 = Math.max(1e-6, (bx - ax) ** 2 + (bz - az) ** 2);
      for (let j = Math.max(0, Math.floor((Math.min(az, bz) - reach - z0) / res)); j <= Math.min(n - 1, Math.ceil((Math.max(az, bz) + reach - z0) / res)); j++)
        for (let i = Math.max(0, Math.floor((Math.min(ax, bx) - reach - x0) / res)); i <= Math.min(n - 1, Math.ceil((Math.max(ax, bx) + reach - x0) / res)); i++) {
          if (riverness[j * n + i] > 0.5) continue;   // (where it meets the big river, the river's banks stand)
          const x = x0 + i * res, z = z0 + j * res, t = clamp(((x - ax) * (bx - ax) + (z - az) * (bz - az)) / len2, 0, 1);
          const d = Math.hypot(x - ax - t * (bx - ax), z - az - t * (bz - az));
          if (d > reach) continue;
          channel(i, j, d, lv[k] + (lv[k + 1] - lv[k]) * t, hw, depthOf(Q[path[k]]));
          riverness[j * n + i] = Math.max(riverness[j * n + i], 0.6 * (1 - smooth(clamp((d - hw + 1) / 2, 0, 1))));
        }
    }
  }
  // the lakes the lab held: their surface (settled with the land under it) over the ground they drown
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = x0 + i * res, z = z0 + j * res, [u, v] = toLab(WIN, x, z);
    if (sD.lin(u, v) < 0.5) continue;
    const lw = sW.lin(u, v) + shift + warp(x, z), k = j * n + i;
    if (base[k] - carve[k] < lw && !(water[k] >= lw)) water[k] = lw;
  }

  // ---- the distance to the water, + on land and - in it: a two-pass chamfer on the grid, in metres
  const isWet = (k) => water[k] > base[k] - carve[k];
  const dist = (wet) => {
    const D = new Float32Array(NN), a = res, b = res * Math.SQRT2;
    for (let k = 0; k < NN; k++) D[k] = wet(k) ? 0 : 1e9;
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const k = j * n + i; let v = D[k];
      if (i > 0) v = Math.min(v, D[k - 1] + a); if (j > 0) v = Math.min(v, D[k - n] + a);
      if (i > 0 && j > 0) v = Math.min(v, D[k - n - 1] + b); if (i < n - 1 && j > 0) v = Math.min(v, D[k - n + 1] + b); D[k] = v; }
    for (let j = n - 1; j >= 0; j--) for (let i = n - 1; i >= 0; i--) { const k = j * n + i; let v = D[k];
      if (i < n - 1) v = Math.min(v, D[k + 1] + a); if (j < n - 1) v = Math.min(v, D[k + n] + a);
      if (i < n - 1 && j < n - 1) v = Math.min(v, D[k + n + 1] + b); if (i > 0 && j < n - 1) v = Math.min(v, D[k + n - 1] + b); D[k] = v; }
    return D;
  };
  const dLand = dist(isWet), dWater = dist((k) => !isWet(k)), sd = new Float32Array(NN), wet = new Float32Array(NN);
  for (let k = 0; k < NN; k++) { sd[k] = isWet(k) ? -dWater[k] : dLand[k]; wet[k] = isWet(k) ? 1 : 0; }

  return {
    seed, res, n, x0, z0, size: 2 * R, base, carve, water, wet, riverness, sd,
    river: { x0: rx0, n: nrx, z: rz, level: lvl, hw: rhw, basin, Q: Qin },
    bridgeX, monumentX, streams: nStreams, steepest: drop,
    falls: stats.falls.length, fallMax: stats.falls[0]?.height ?? 0, score: WIN.score, lift,
  };
}
