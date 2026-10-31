// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- limestone's work: tufa dams, the sinking stream, dolines,
// cockpit karst, pavement. Each stage takes the scene so far, `c`, and adds what it makes to it; landscape.js runs
// them in order.
import { TAU, clamp, smooth, lerp, noise, fbm, rng, atS } from "./core.js";

export function tufa(c) {
  const { capK, carved, chanD, chanW, clim, coast, cum, dx, F, H, meA, n, N, notes, profAt, pts, R, S, sCross, sCross2,
    seed, sFall2, size, sOf, STEP2, streamV, toUV, toXY, v0 } = c;
  // TUFA DAMS: karst water is full of the lime it dissolved, and drops it where it tumbles and the moss takes the CO2 --
  // a dam grows across the stream, the water ponds behind it, spills over it, and drops more at the spill: a flight of
  // pools, each held by its sill (Plitvice). Where a karst stream runs all year and it is warm enough for the moss: on
  // the bench between the steps if there is room, else on the lowland
  const tufa = new Uint8Array(n), dams = [];
  (() => {
  if (F.tufa === false || !S.beds[capK].karst || !clim.flows || clim.temp < 5) return;
  // (the bench's flight, if there is room, and a lower flight below the last step, till the stream slackens into its
  // meanders -- the lime drops where the water tumbles, not where it idles; warmer water drops it faster: the dams closer)
  const low = STEP2 ? sCross2 : sCross, gap = clamp(1.3 - clim.temp / 40, .8, 1.2), runs = [];
  if (STEP2 && sFall2 - sCross > 60) runs.push([sCross + 16, sFall2 - 14]);
  runs.push([low + 16, Math.min(cum[cum.length - 1] - 25, low + (meA ? 48 : 110), coast ? sOf(coast.uL) - 18 : Infinity)]);
  for (const [s0, s1] of runs)
  for (let sd = s0 + 6 + R() * 6; sd < s1; sd += (14 + R() * 8) * gap) {
    const [u0, v0] = atS(pts, cum, sd), [u1, v1] = atS(pts, cum, sd + 1), [cx, cy] = toXY(u0, v0), [ex, ey] = toXY(u1, v1);
    if (cx < 12 || cy < 12 || cx > size - 12 || cy > size - 12) continue;
    const du = Math.max(.3, u1 - u0), dl = Math.hypot(ex - cx, ey - cy) || 1, tx = (ex - cx) / dl, ty = (ey - cy) / dl, L = 10 + R() * 5, Wb = chanW * (2 + R() * .6), crest = Math.min(profAt(sd) + chanD + .9 + R() * .5, profAt(sd) + chanD + 1.6);
    dams.push({ x: cx, y: cy, s: sd, crest });
    for (let j = Math.floor((cy - L - 6) / dx); j <= Math.ceil((cy + L + 6) / dx); j++) for (let i = Math.floor((cx - L - 6) / dx); i <= Math.ceil((cx + L + 6) / dx); i++) {
      if (i < 0 || j < 0 || i >= N || j >= N) continue;
      const k = j * N + i, x = i * dx, y = j * dx, a = (x - cx) * tx + (y - cy) * ty, c = Math.abs(-(x - cx) * ty + (y - cy) * tx);
      // (the pool behind it: a basin wider than the channel, its floor the stream's bed)
      // (its shores sloping up from it: a basin, not a cut)
      // (laid along the stream, not along its tangent here: it follows a bend)
      const [cu_, cv_] = toUV(x, y), as = (cu_ - u0) / du, cs = Math.abs(cv_ - streamV(cu_)) * du;
      if (as < 0 && as > -L - 4) { const e = 1 - ((as + L / 2) / (L / 2 + 2)) ** 2;
        if (e > 0) { const r = Wb * Math.sqrt(e), z = profAt(sd + as) - .35 * e + Math.max(0, cs - r) * .45; if (z < H[k]) { H[k] = z; if (cs < r) carved[k] = 1; } } }
      // (the sill: its crest across the valley, into the banks till they stand over it -- lowest in the middle, where it
      // spills -- rounded downstream)
      if (a > -1.4 && a < 1.8 && c < Wb + 3) { const z = crest + Math.max(0, c - Wb * .7) * .3 - (a > 0 ? .7 * (a / 1.8) ** 2 : 0) - .12 * noise(x / 1.7, y / 1.7, seed + 83); if (z > H[k]) { H[k] = z; carved[k] = 0; tufa[k] = 1; } }
    }
  }
  if (dams.length) notes.push(`tufa dams: ${dams.length} across the stream, each holding a pool -- the karst water drops the lime it carries where it tumbles over them`);
  })();
  Object.assign(c, { tufa, dams });
}

export function sinking(c) {
  const { capK, carved, clim, dx, F, FAULT, H, N, n, S, seed, trib } = c;
  // a SINKING STREAM: on karst the side stream need not reach the gorge -- it finds a joint it widens into a PONOR, a
  // swallow hole, and goes down it; below the hole nothing cut its valley on, so the valley ends blind against a wall
  // (its floor sinking toward the hole, deeper than a valley that went on would be); the water runs on underground and
  // out at the spring cave. Its own random numbers
  (() => {
  if (!trib || !S.beds[capK].karst || !clim.flows || FAULT || F.ponor === false) return;
  const RP = rng(seed * 197 + 11); if (RP() > (F.ponor?.chance ?? .75)) return;
  const L = trib.way.length, keep = Math.round(L * (.5 + RP() * .2)); if (keep < 30) return;
  trib.way.length = keep; trib.zs.length = keep;
  const dEnd = 2 + RP() * 2; for (let q = 0; q < keep; q++) trib.zs[q] -= dEnd * smooth((q / keep - .45) / .55);
  const [x, y] = trib.way[keep - 1];
  trib.ponor = { x, y, r: 5 + RP() * 2.5, depth: 2.2 + RP() * 1.6, z: trib.zs[keep - 1], wall: 0 };
  })();
  (() => {
  if (trib) {
    // (a stamp at every point of its way: the channel, then the valley's sides rising from it -- until they meet the ground)
    const { way, zs, w } = trib, Rr = 14;
    way.forEach(([x, y], q) => {
      for (let j = Math.floor((y - Rr) / dx); j <= Math.ceil((y + Rr) / dx); j++) for (let i = Math.floor((x - Rr) / dx); i <= Math.ceil((x + Rr) / dx); i++) {
        if (i < 0 || j < 0 || i >= N || j >= N) continue;
        const k = j * N + i, d = Math.hypot(i * dx - x, j * dx - y); if (d > Rr) continue;
        const t = d < w ? zs[q] - .6 * (1 - (d / w) ** 2) : zs[q] + (d - w) * (.75 - .3 * q / way.length + .15 * noise(i * dx / 7, j * dx / 7, seed + 19));   // (wider down it)
        if (t < H[k]) { H[k] = t; if (d < w) carved[k] = 1; }
      }
    });
    // (the ponor: a funnel at the valley's end, its hole at the foot of the blind wall)
    const P = trib.ponor; if (P) {
      for (let j = Math.floor((P.y - P.r) / dx); j <= Math.ceil((P.y + P.r) / dx); j++) for (let i = Math.floor((P.x - P.r) / dx); i <= Math.ceil((P.x + P.r) / dx); i++) {
        if (i < 0 || j < 0 || i >= N || j >= N) continue;
        const q = Math.hypot(i * dx - P.x, j * dx - P.y) / P.r + .12 * noise(i * dx / 3, j * dx / 3, seed + 199); if (q >= 1) continue;
        const k = j * N + i, t = P.z - .2 - P.depth * (1 - q) ** 1.4; if (t < H[k]) { H[k] = t; carved[k] = 0; }
      }
      const [ex, ey] = trib.way[Math.max(0, trib.way.length - 1)], k0 = clamp(Math.round(ey / dx), 0, N - 1) * N + clamp(Math.round(ex / dx), 0, N - 1);
      P.wall = 0; for (let j = -12; j <= 12; j++) for (let i = -12; i <= 12; i++) { const k = k0 + j * N + i; if (k >= 0 && k < n) P.wall = Math.max(P.wall, H[k] - H[k0]); }
    }
  }
  })();
}

export function dolines(c) {
  const { capK, clim, COCKPIT, dx, F, FAULT, H, lake, N, notes, R, S, scarpU, seed, size, streamV, toUV, trib } = c;
  // DOLINES: on a karst upland the rain goes down, not off -- through joints it widened into funnels, each with a swallow
  // hole at its foot (the WATER stage lets it out there); more the wetter the climate
  const dolines = [];
  (() => {
  if (F.dolines !== false && S.beds[capK].karst && !FAULT) {
    const want = COCKPIT ? 1 : Math.round(2 + clim.rain / 350);   // (in cockpit karst the cockpits are its dolines: one besides, for the cenote)
    for (let t = 0; t < 80 && dolines.length < want; t++) {
      const x = 10 + R() * (size - 20), y = 10 + R() * (size - 20), [u, v] = toUV(x, y), r = COCKPIT ? 7 + R() * 3 : 4 + R() * 8;
      if (u > scarpU(v) - r - 12 || Math.abs(v - streamV(u)) < r + 12 || (lake && lake.r * lake.dist(u, v) < lake.r + r + 8)) continue;
      if (dolines.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r + 6) || trib?.way.some(([tx, ty]) => Math.hypot(tx - x, ty - y) < r + 10)) continue;
      dolines.push({ x, y, r, depth: r * (.3 + R() * .2) });
    }
    for (const o of dolines) for (let j = Math.floor((o.y - o.r) / dx); j <= Math.ceil((o.y + o.r) / dx); j++) for (let i = Math.floor((o.x - o.r) / dx); i <= Math.ceil((o.x + o.r) / dx); i++) {
      if (i < 0 || j < 0 || i >= N || j >= N) continue;
      const q = Math.hypot(i * dx - o.x, j * dx - o.y) / o.r + .15 * noise(i * dx / 3, j * dx / 3, seed + 97);
      if (q < 1) H[j * N + i] -= o.depth * (1 - q * q) ** 1.5;
    }
    // a CENOTE: in the wet tropics the karst is hollowed down to the water table, and where a cave's roof fell in, the
    // biggest doline is a shaft -- sheer walls, the rim overhanging the cave it fell into (the CAVES stage's patch),
    // the water table's pool at the foot (the WATER stage holds its outlet at that level)
    const big = dolines.filter((o) => o.r > 5.5).sort((a, b) => b.r - a.r)[0];
    if (big && clim.temp >= 18 && clim.flows) {
      const RN = rng(seed * 67 + 11), zt = H[clamp(Math.round(big.y / dx), 0, N - 1) * N + clamp(Math.round(big.x / dx), 0, N - 1)];
      Object.assign(big, { cenote: true, r: Math.max(big.r, 7.5), wt: zt - 9 - RN() * 5 });
      big.floor = big.wt - 3 - RN() * 2;
      for (let j = Math.floor((big.y - big.r * 1.3) / dx); j <= Math.ceil((big.y + big.r * 1.3) / dx); j++) for (let i = Math.floor((big.x - big.r * 1.3) / dx); i <= Math.ceil((big.x + big.r * 1.3) / dx); i++) {
        if (i < 0 || j < 0 || i >= N || j >= N) continue;
        const a = Math.atan2(j * dx - big.y, i * dx - big.x), q = Math.hypot(i * dx - big.x, j * dx - big.y) / (big.r * (1 + .15 * noise(Math.cos(a) * 1.5 + big.x, Math.sin(a) * 1.5, seed + 99)));
        if (q < 1) H[j * N + i] = Math.min(H[j * N + i], big.floor + .4 * noise(i * dx / 3, j * dx / 3, seed + 101));
      }
    }
    if (dolines.length && !COCKPIT) notes.push(`dolines: ${dolines.length} on the ${S.beds[capK].name} upland, ${Math.round(Math.min(...dolines.map((o) => o.r * 2)))}-${Math.round(Math.max(...dolines.map((o) => o.r * 2)))} m across -- funnels the rain dissolved down joints; each drains at its foot`);
  }
  })();
  if (trib?.ponor) { const P = trib.ponor; dolines.push({ x: P.x, y: P.y, r: P.r, depth: P.depth, ponor: true });   // (the WATER stage lets the side stream out there)
    notes.push(`sinking stream: the side stream goes down a ponor ${Math.round(P.r * 2)} m across, at the end of its blind valley (the wall over it ${P.wall.toFixed(0)} m) -- underground on, out at the spring cave`); }
  Object.assign(c, { dolines });
}

export function cockpit(c) {
  const { COCKPIT, dolines, dx, fanBase, H, half, lake, N, n, notes, R, scarpU, seed, size, streamV, trib, U, V } = c;
  // COCKPIT KARST: in the wet tropics the rain dissolves the limestone so fast that the dolines grow into each other --
  // the upland a field of round-topped cones, a hollow (a cockpit) between each few, star-shaped where the cones' feet
  // meet, each drained at its foot like a doline (the WATER stage's sinks). Not by the stream's valley, the lake, the
  // scarp's edge or the cenote: there the upland as it was. Its own random numbers
  const cockM = new Uint8Array(n);   // 1 a cone's flank (DRESS: the jungle holds on its slopes)
  (() => {
  if (!COCKPIT) return;
  const RK = rng(seed * 163 + 79), Sp = 24 + RK() * 8, D = 5 + RK() * 2.5, Rf = .6 + RK() * .08, rot = RK() * TAU, ca = Math.cos(rot), sa = Math.sin(rot);
  const nG = Math.ceil(size * 1.5 / Sp) + 2, cones = [];   // (a jittered grid, turned: the joints' grid the rain worked down)
  for (let b = -nG; b <= nG; b++) for (let a = -nG; a <= nG; a++) {
    const gx = (a + (RK() - .5) * .9) * Sp, gy = (b + (RK() - .5) * .9) * Sp, x = half + gx * ca - gy * sa, y = half + gx * sa + gy * ca;
    cones.push({ a, b, x, y, h: D + 3 + RK() * 7, R: Sp * Rf * (.9 + RK() * .2) });
  }
  const at = new Map(cones.map((c) => [c.a + "," + c.b, c]));
  // (where the upland stays as it was: a distance to the side stream's way, stamped)
  const tD = new Float32Array(n).fill(99);
  if (trib) for (const [wx, wy] of trib.way) for (let j = Math.max(0, Math.floor((wy - 26) / dx)); j <= Math.min(N - 1, Math.ceil((wy + 26) / dx)); j++) for (let i = Math.max(0, Math.floor((wx - 26) / dx)); i <= Math.min(N - 1, Math.ceil((wx + 26) / dx)); i++) {
    const k = j * N + i; tD[k] = Math.min(tD[k], Math.hypot(i * dx - wx, j * dx - wy)); }
  const cen = dolines.find((o) => o.cenote);
  const wAt = (k, x, y) => { const u = U[k], v = V[k];
    let w = smooth((scarpU(v) - u - 12) / 26) * smooth((Math.abs(v - streamV(u)) - 12) / 16) * smooth((tD[k] - 10) / 14);
    if (lake) w *= smooth((lake.dist(u, v) - 1.25) / .6);
    if (cen) w *= smooth((Math.hypot(x - cen.x, y - cen.y) - cen.r - 5) / 10);
    return w; };
  let cells = 0, top = 0;
  for (let k = 0; k < n; k++) {
    const x = (k % N) * dx, y = ((k / N) | 0) * dx, w = wAt(k, x, y);
    if (w <= 0) continue;
    const gx = (x - half) * ca + (y - half) * sa, gy = -(x - half) * sa + (y - half) * ca, ga = Math.round(gx / Sp), gb = Math.round(gy / Sp);
    let cf = 0;
    for (let b = gb - 1; b <= gb + 1; b++) for (let a = ga - 1; a <= ga + 1; a++) { const c = at.get(a + "," + b); if (!c) continue;
      const r = Math.hypot(x - c.x, y - c.y) / (c.R * (1 + .12 * noise(x / 6, y / 6, seed + 141))); if (r < 1) cf = Math.max(cf, c.h * (1 - r ** 1.8) ** 1.4); }
    const z = H[k] - D + .5 * fbm(x / 9, y / 9, seed + 143, 2) + cf, nz = lerp(H[k], z, w);
    if (nz > H[k]) fanBase[k] = Math.max(fanBase[k], nz);   // (solid rock, not heaped: the hollows dissolved round it)
    H[k] = nz; if (w > .9) { cells++; top = Math.max(top, cf - D); }
    cockM[k] = w > .3 && cf > 1 ? 1 : 2;
  }
  // (each hollow's foot drains: a sink at every low in it -- the lowest cell in 9 m round -- and at its deepest)
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const k = j * N + i; if (!cockM[k]) continue;
    let lo = true; for (let b = Math.max(-4, -j); b <= Math.min(4, N - 1 - j) && lo; b++) for (let a = Math.max(-4, -i); a <= Math.min(4, N - 1 - i); a++) { const q = k + b * N + a; if (H[q] < H[k] || (H[q] === H[k] && q < k)) { lo = false; break; } }
    if (lo) { dolines.push({ x: i * dx, y: j * dx, r: dx * .5, depth: D, cockpit: true }); }
  }
  const nC = cones.filter((c) => c.x > 0 && c.y > 0 && c.x < size && c.y < size && wAt(Math.round(c.y / dx) * N + Math.round(c.x / dx), c.x, c.y) > .5).length;
  if (cells > 400) notes.push(`cockpit karst: the upland a field of ${nC} cones ${Math.round(Sp * Rf * 2)} m across, up to ${top.toFixed(0)} m over the land, the hollows between them ${D.toFixed(0)} m deep, star-shaped, each draining at its foot -- in the wet tropics the dolines grew into each other`);
  })();
  Object.assign(c, { cockM });
}

export function pavement(c) {
  const { bedK, capK, carved, clim, dx, grikeAt, H, N, n, rock, S, seed, soil } = c;
  // PAVEMENT: bare limestone, near flat, its joints widened by the rain into grikes between the blocks (clints)
  (() => {
  if (S.beds[capK].karst) for (let k = 0; k < n; k++) {
    const b = bedK(k); if (!S.beds[b].karst || soil[k] > .1 || carved[k]) continue;
    const i = k % N, j = (k / N) | 0, sx = (H[j * N + Math.min(N - 1, i + 1)] - H[j * N + Math.max(0, i - 1)]) / 2, sy = (H[Math.min(N - 1, j + 1) * N + i] - H[Math.max(0, j - 1) * N + i]) / 2;
    // (in patches -- where the soil was stripped, not everywhere it is thin -- the grikes deeper in some than others)
    const f = fbm(i * dx / 25, j * dx / 25, seed + 99, 2) - clim.soil * .8 - .05;
    if (Math.hypot(sx, sy) < .2 && f > 0 && grikeAt(b, i * dx, j * dx) > .76) { const g = .45 * clamp(f * 5, .35, 1); H[k] -= g; rock[k] -= g; }
  }
  })();
}
