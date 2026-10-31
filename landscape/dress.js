// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- DRESS: what each cell's surface is, the stains, the cover, the
// trees, the boulders -- and the scene returned. Each stage takes the scene so far, `c`, and adds what it makes to it;
// landscape.js runs them in order.
import { TAU, clamp, smooth, noise, fbm, rng, atS } from "./core.js";

export function surfaceGrids(c) {
  const { n } = c;
  // DRESS: what each cell's surface is -- the bed it shows (bare where steep), scree, soil, and what grows on it
  // `veg`: how much of a cell trees cover (0..1): as much as the climate grows, in stands (a patchy field), where there
  // is soil and the ground is not too steep; and by the water, where the land gathers it (the wetness index: much
  // gathered, little slope to shed it) -- in a dry climate the only trees are there
  const surf = new Uint8Array(n), slope = new Float32Array(n), bed = new Uint8Array(n), veg = new Float32Array(n);
  Object.assign(c, { surf, slope, bed, veg });
}

export function stain(c) {
  const { clim, dryness0, n } = c;
  // (a cliff's face streaked where the water runs down it from the rim: in a dry country desert varnish -- the clay and
  // the manganese the dew and the rare runs leave, baked black-brown over centuries, darkest on sandstone; in a wet one
  // the algae and the lichens, grey-green to black, on limestone and granite most. Strongest under a notch, where the
  // runs gather; in stripes along the face. `stain` 0..1, `stainCol` its colour)
  const stain = new Float32Array(n), VARN = dryness0 > .4;
  const stainCol = VARN ? [.2, .12, .07] : [.11, .13, .1], stainK = (r) => VARN ? (r === "sandstone" ? .85 : r === "basalt" ? .25 : .6) * dryness0
    : (r === "limestone" || r === "granite" ? .7 : r === "basalt" ? .2 : .45) * clamp((clim.rain - 300) / 900, 0, 1);
  Object.assign(c, { stain, VARN, stainCol, stainK });
}

export function ground(c) {
  const { bar, bed, braidM, capK, clim, coast, cockM, coneM, cut, deltaM, dikeM, domeM, domes, dryness, dryness0, dune,
    dx, eskerM, F, fanT, fumes, grikeAt, H, HS, JT, kind, knockM, lobeM, lowTop, mangM, n, N, notes, playaM, Q, R, rgM,
    rock, S, seed, shoreK, slabM, slope, softK, soil, spec, stain, stainK, STREAM, surf, tinM, TOP, travM, tufa, veg,
    water } = c;
  const SURF = ["rock", "scree", "soil", "grass", "forest", "sand", "snow", "gravel", "tufa", "cinders", "lava", "shingle", "black sand", "white sand", "salt", "bog", "mangrove", "reeds", "sulfur", "altered"];
  // (a beach is what the waves had to grind: on a cold coast the frost's shards, too little worn to sand -- shingle;
  // under basalt the basalt's black grains; on a warm limestone coast the shells' and the corals' white -- the land
  // gives little sand that does not dissolve; else the sand the stream brings. The dunes behind it the same)
  const beachS = !coast ? 5 : clim.temp < 4 ? 11 : S.beds[capK].rock === "basalt" ? 12 : S.beds[capK].karst && clim.temp >= 18 ? 13 : 5;
  if (coast) coast.beach = SURF[beachS];
  const sun = spec.sun ?? [-.857, .514];   // (the way to the sun over the ground: the lab lights the scene from it)
  const cover = { forest: .85, jungle: 1, scrub: .3, tundra: .06, desert: .02, none: 0 }[clim.plants];
  // (how far a place is from the edge of its cell in a net of polygons ~6 m across: the second-nearest of jittered
  // points less the nearest, halved)
  const SPRINGS = F.springs !== false && dryness > 0 && capK >= 0 && softK >= 0 && ["sandstone", "limestone", "basalt"].includes(S.beds[capK].rock) && clim.plants !== "none";
  const REEDS = F.reeds !== false && clim.wet > .3 && clim.temp >= 4 && clim.temp < 26; let reeds = 0;
  let springs = 0, bogs = 0, seepBest = .6, seepK = -1, oasis = null;
  const oasisM = new Uint8Array(n);   // (1 an oasis's pool's rim, where its palms stand)
  const BOG = F.bogs !== false && clim.rain > 900 && clim.temp < 14 && clim.temp > -2;
  const polyRim = (x, y) => {
    const P = 6, gi = Math.floor(x / P), gj = Math.floor(y / P); let d1 = 1e9, d2 = 1e9;
    for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) {
      const h = Math.sin((gi + a) * 127.1 + (gj + b) * 311.7 + seed * 7.3) * 43758.5453, rx = h - Math.floor(h), h2 = h * 1.618, ry = h2 - Math.floor(h2);
      const d = Math.hypot((gi + a + .15 + .7 * rx) * P - x, (gj + b + .15 + .7 * ry) * P - y);
      if (d < d1) { d2 = d1; d1 = d; } else if (d < d2) d2 = d;
    }
    return (d2 - d1) / 2;
  };
  // (how far a place stands over the ground round it, ~7 m: the sand and soil the wind and the rain move lie in the
  // hollows, the rises are swept bare)
  const rise = new Float32Array(n);
  { const t = new Float32Array(n), Rr = 4;
    for (let j = 0; j < N; j++) { let a = 0; for (let i = -Rr; i <= Rr; i++) a += H[j * N + clamp(i, 0, N - 1)];
      for (let i = 0; i < N; i++) { t[j * N + i] = a; a += H[j * N + Math.min(N - 1, i + Rr + 1)] - H[j * N + Math.max(0, i - Rr)]; } }
    for (let i = 0; i < N; i++) { let a = 0; for (let j = -Rr; j <= Rr; j++) a += t[clamp(j, 0, N - 1) * N + i];
      for (let j = 0; j < N; j++) { rise[j * N + i] = H[j * N + i] - a / (2 * Rr + 1) ** 2; a += t[Math.min(N - 1, j + Rr + 1) * N + i] - t[Math.max(0, j - Rr) * N + i]; } } }
  (() => {
  for (let k = 0; k < n; k++) {
    const i = k % N, j = (k / N) | 0;
    const hx = (HS[j * N + Math.min(N - 1, i + 1)] - HS[j * N + Math.max(0, i - 1)]) / (2 * dx), hy = (HS[Math.min(N - 1, j + 1) * N + i] - HS[Math.max(0, j - 1) * N + i]) / (2 * dx);
    const sl = Math.hypot(hx, hy); slope[k] = sl;
    bed[k] = dikeM[k] || slabM[k] ? capK : S.bedAt(i * dx, j * dx, H[k] - .05);
    const deg = Math.atan(sl) * 180 / Math.PI;
    let s = 0;
    if (soil[k] > .25 && deg > 22) s = 1;                                                   // scree
    else if (deg < 30 - 10 * (1 - clim.wet)) s = clim.plants === "desert" ? 5 : clim.plants === "none" ? 6 : clim.wet > .25 ? (deg < 24 && fbm(i * dx / 30, j * dx / 30, seed + 61, 3) > -.05 ? 4 : 3) : 2;
    if (s === 3 || s === 4) { if (deg > 26 && R() < .5) s = 2; }
    // (where the climate makes little soil, a hard bed shows through it: slickrock, pavement -- on the rises and where
    // it slopes; the sand in the hollows between and down its joints, the cracks it fills in a grid)
    if (s >= 2 && soil[k] < .15 && S.beds[bed[k]].hard >= .5 && .3 * fbm(i * dx / 30, j * dx / 30, seed + 67, 3) + .22 * fbm(i * dx / 8, j * dx / 8, seed + 139, 2) + clamp(rise[k] * 2, -.7, .7) +
      clamp((deg - 6) / 20, 0, .4) - (grikeAt(bed[k], i * dx, j * dx) > .76 ? .7 * clamp(2 * fbm(i * dx / 22, j * dx / 22, seed + 79, 2), 0, 1) : 0) > clim.soil * 1.6 - .25 + (1 - dryness) * .3 + (S.beds[bed[k]].rock === "granite" ? .3 : 0)) s = 0;   // (granite rots to grus: more of it lies)
    // (a knoll the ice scoured: bare, the tundra only in its cracks)
    if (knockM[k] && !kind[k] && s !== 6 && fbm(i * dx / 7, j * dx / 7, seed + 151, 2) > -.15 - deg / 60) s = 0;
    // (a cockpit cone: the jungle holds on its flanks, steep as they are -- the limestone out in its steepest places)
    if (cockM[k] === 1 && !kind[k] && deg < 50 && s !== 3 && s !== 4 && fbm(i * dx / 12, j * dx / 12, seed + 147, 2) > (deg - 50) / 40) s = deg < 40 ? 4 : 3;
    // (snow: where it is cold, what lies out of the sun all summer -- on the slopes turned from it, in the hollows the
    // wind drifted it into (the rises it swept bare), more of it up high; patchy)
    if (clim.temp < 4 && s !== 0 && !kind[k] && deg < 42) {
      const facing = sl > .02 ? (-hx * sun[0] - hy * sun[1]) / sl : 0, up = clamp((H[k] - lowTop) / (TOP - lowTop), 0, 1.2);
      // (on the open flats the wind takes it, and the sun has it all day: little there but in the hollows; its edges ragged)
      const open = (1 - Math.min(1, sl * 6)) * smooth((rise[k] + .25) / .2);
      if ((4 - clim.temp) / 7 - .11 - facing * .6 * Math.min(1, sl * 4) + .15 * fbm(i * dx / 14, j * dx / 14, seed + 69, 3) + .07 * fbm(i * dx / 4.5, j * dx / 4.5, seed + 345, 2) - clamp(rise[k] * .9, -.45, .3) - .07 * open + .14 * up > .5) s = 6;
    }
    if (bar[k] && !kind[k]) s = 5;   // (a point bar: sand and gravel, bare -- the next flood moves it)
    if (tufa[k] && !kind[k]) s = 8;
    if (shoreK[k] && !kind[k]) s = shoreK[k] === 1 ? (deg < 20 ? beachS : s) : 0;   // (a beach's sand; the platform bare, washed)
    if (dune[k] === 1 && !kind[k] && s !== 6) s = beachS;   // (a dune's bare sand, a storm ridge's shingle: the beach's)
    if (dune[k] === 3 && !kind[k]) s = 5;   // (a barchan's: bare)
    // (a young cone's cinders, its flow's lava: bare -- where it is wet the grass has taken them, but for the steep)
    if (coneM[k] && coneM[k] < 3 && !kind[k] && s !== 6 && (clim.wet < .55 || deg > 26)) s = coneM[k] === 1 ? 9 : 10;
    if (coneM[k] === 1 && fumes.length && !kind[k]) for (const o of fumes) { const d = Math.hypot(i * dx - o.x, j * dx - o.y) / (o.r * (1 + .3 * noise(i * dx / 1.6, j * dx / 1.6, seed + 299)));
      if (d < .45) { s = 18; break; } if (d < 1.15) s = 19; }   // (a fumarole's sulphur, the bleached ground round it)
    if (lobeM[k] === 2 && !kind[k] && s !== 6 && s >= 2) s = 2;   // (a solifluction lobe's riser: the turf torn, the soil showing)
    if (rgM[k] && !kind[k] && s !== 6) s = 1;   // (a rock glacier's blocks, bare)
    if (eskerM[k] && !kind[k] && s !== 6 && (deg > 22 || s < 2)) s = 7;   // (an esker's gravel: out where it is steep)
    if (braidM[k] && !kind[k] && s !== 6) s = 7;
    if (dikeM[k] === 2 && kind[k] !== 1 && s !== 6) s = 0;   // (a causeway's columns: bare, washed)
    // (patterned ground: on the cold country's flats the frost heaves the stones up through the soil and out to the
    // edges of the cells it churns -- polygons of gravel rims round mossy middles, ~6 m across; in patches -- the
    // fines and the water that make them are not everywhere)
    if (clim.temp < 3 && !kind[k] && deg < 5 && s >= 2 && s <= 4 && fbm(i * dx / 45, j * dx / 45, seed + 135, 2) > .1 &&
      polyRim(i * dx, j * dx) < .45 + .15 * noise(i * dx / 2, j * dx / 2, seed + 133)) s = 7;   // (a braid's bars: gravel, bare -- the next flood moves them)
    // (a delta's top: the meltwater's gravel, bare; a dry country's sand; where it is wet the reeds and grass have it)
    if (deltaM[k] && !kind[k] && s !== 6) s = clim.temp < 4 ? 7 : cover < .3 ? 5 : 3;
    // (a playa's floor: the salt's crust, white; the cracks between its polygons the mud under it)
    if (tinM[k] && !kind[k]) s = 0;   // (a tinaja and the slickrock round it)
    if (playaM[k] === 2 && !kind[k]) s = polyRim(i * dx * .9, j * dx * .9) < .26 ? 2 : 14;
    if (playaM[k] === 3) s = 2;   // (a yardang: the lake's mud, bare)
    if (kind[k] === 4) s = shoreK[k] === 2 || dikeM[k] === 2 || deg > 25 ? 0 : 5;   // (under the sea: its sand, the rock where the waves keep it bare)
    if (kind[k] === 1 && s > 1) {   // (a lake's bed: mud -- rock and scree where they are)
      s = 2;
      // (REEDS: in its shallows, where it is wet and not frozen, in beds along the shore -- standing out of the water)
      if (REEDS && water[k] - H[k] < .7 && deg < 6 && !playaM[k] && !tinM[k] && !travM[k] && fbm(i * dx / 11, j * dx / 11, seed + 291, 2) > -.12) { s = 17; reeds++; }
    }
    // (a fan in a dry country: gravel, bare, in the tracks the floods last spread down it)
    if (s >= 2 && s !== 6 && !kind[k] && fanT[k] > .3 && cover < .5 && deg < 16 && fbm(i * dx / 9, j * dx / 9, seed + 27, 3) > -.25) s = 7;
    // (a SPRING LINE: in a dry country the rain that sank into a cap that lets it through comes out where the bed under
    // it will not -- seeps along the contact under the cliff, where the joints brought it down: green on the bare slope)
    let seep = 0;
    if (SPRINGS && !kind[k] && !cut[k] && deg > 10 && deg < 50 && s !== 6 && !coneM[k] && rise[k] < -.8) {   // (rise: under a cliff, not out on the lowland)
      const dz = H[k] - S.topOf(i * dx, j * dx, softK);
      if (dz > -10 && dz < 1) seep = clamp((.95 - JT[capK][k]) * 2.5, 0, 1) * clamp(1.15 + dz / 10, 0, 1) * clamp(.8 + 1.5 * fbm(i * dx / 20, j * dx / 20, seed + 137, 2), 0, 1);   // (and down the slope below, where it runs)
      if (seep > .3) { s = 3; springs++; if (seep > seepBest && Q[k] < STREAM) { seepBest = seep; seepK = k; } }
    }
    if (s >= 2 && s < 9 && !kind[k] && !bar[k] && !braidM[k] && shoreK[k] !== 1 && dune[k] !== 1 && dune[k] !== 3) {
      // (the wetness index from the flow over a few metres, not the one cell its line runs down)
      let q = 0; for (let b = -2; b <= 2; b++) for (let a = -2; a <= 2; a++) q = Math.max(q, Q[clamp(j + b, 0, N - 1) * N + clamp(i + a, 0, N - 1)]);
      const stands = clamp(.5 + 1.6 * fbm(i * dx / 30, j * dx / 30, seed + 61, 3), 0, 1), twi = Math.log(q / (dx * (sl + .02))) - 6;
      veg[k] = clamp(cover * stands * clamp((32 - deg) / 10, 0, 1) * clamp(soil[k] * 4 + .3, 0, 1) + clamp(twi * .12, 0, .7) * (1.1 - cover) * (clim.plants === "none" ? 0 : 1), 0, 1);
      if (seep > .3) veg[k] = Math.max(veg[k], .45 + .4 * seep);
      if (playaM[k] >= 2) veg[k] = 0;   // (nothing grows in the salt)
      // (a BOG: where it is cool and wet and the water cannot get away -- a flat hollow it gathers in, on rock it cannot
      // sink into (not limestone) -- the moss grows faster than it rots and builds peat: no trees, dark, its pools in
      // the hollows of the moss)
      if (BOG && deg < 2.5 && rise[k] < .03 && twi > 1.8 && fbm(i * dx / 45, j * dx / 45, seed + 217, 2) > .12 + rise[k] * 2 && !S.beds[bed[k]].karst && !tinM[k] && !coneM[k]) {
        s = 15; veg[k] = 0; bogs++;
        if (fbm(i * dx / 4, j * dx / 4, seed + 219, 2) > .32) { water[k] = H[k] + .05; kind[k] = 1; }
      }
      if (cockM[k] === 1) veg[k] = Math.max(veg[k], cover * clamp((50 - deg) / 12, 0, 1) * clamp(.6 + fbm(i * dx / 14, j * dx / 14, seed + 145, 2), 0, 1));
    }
    if (mangM[k] && (!kind[k] || water[k] - H[k] < .8)) { s = 16; veg[k] = .95; }   // (the mangroves' mud, their cover)
    surf[k] = s;
    // (a rounded granite coast: no streaks down its slabs -- the BLACK LICHEN's band just over the water, where the
    // spray wets it and the waves do not scour it)
    if (coast?.rounded && s === 0 && !kind[k] && H[k] < coast.sea + coast.cH * .8) stain[k] = .85 * clamp(1 - Math.abs(H[k] - coast.sea - 1.3) / 1.1, 0, 1);
    // (a dome's flanks streaked from where they steepen, the runnels' water down them: the stripes by the way round it)
    else if (domeM[k] && s === 0 && !kind[k] && deg > 12) { const A = stainK(S.beds[bed[k]].rock), d = domes[0], a = Math.atan2(j * dx - d.y, i * dx - d.x);
      if (A > 0) stain[k] = clamp(A * .65 * clamp((deg - 12) / 16, 0, 1) * (.1 + 1.3 * smooth((noise(a * d.r / 4.5, H[k] / 40, seed + 203) + .05) / .2)), 0, 1); }
    else if (s === 0 && !kind[k] && deg > 40) {   // (the stripes by where along the face: down it they run on)
      const A = stainK(S.beds[bed[k]].rock); if (A > 0)
        stain[k] = clamp(A * clamp((deg - 35) / 12, 0, 1) * (.15 + 1.2 * smooth((noise((-hy * i + hx * j) * dx / (sl * 1.3), H[k] / 14, seed + 201) + .02) / .18) + clamp(Math.log10(Q[k] / STREAM * 40 + 1) * .35, 0, .6)), 0, 1);
    }
  }
  if (bogs > 40) notes.push(`bogs: ${bogs} m2 of peat on the flats the water gathers on and cannot leave -- cool and wet, the moss grows faster than it rots; no trees on it, its pools in the moss's hollows`);
  if (reeds > 30) notes.push(`reeds: ${reeds} m2 in the lakes' shallows, in beds along their shores`);
  if (springs > 20) notes.push(`spring line: seeps along the foot of the ${S.beds[capK].name}, where it lies on the ${S.beds[softK].name} -- the rain that sank into it comes out there, at the joints; green under the bare cliff`);
  // (an OASIS: in a hot desert the strongest seep's water runs down to the foot of the slope and stands there in a pool
  // dug into the ground it wets -- date palms round it, the only trees for miles. Its own random numbers)
  if (springs > 20 && seepK >= 0 && dryness0 > .6 && clim.temp >= 15 && F.oasis !== false) {
    const RO = rng(seed * 281 + 1); let k = seepK;
    for (let t = 0; t < 60; t++) {   // (down the steepest way to where the ground eases)
      const i = k % N, j = (k / N) | 0; let kn = k;
      for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) { const i2 = i + a, j2 = j + b; if (i2 < 1 || j2 < 1 || i2 > N - 2 || j2 > N - 2) continue; const k2 = j2 * N + i2; if (H[k2] < H[kn]) kn = k2; }
      if (kn === k || kind[kn] || H[k] - H[kn] < .07 * dx) break;
      k = kn;
    }
    const i0 = k % N, j0 = (k / N) | 0, r = 3.5 + RO() * 3, R0 = Math.ceil((r + 12) / dx);
    let ok = i0 > R0 && j0 > R0 && i0 < N - R0 && j0 < N - R0;
    for (let j = j0 - R0; ok && j <= j0 + R0; j++) for (let i = i0 - R0; i <= i0 + R0; i++) { const k2 = j * N + i; if (Math.hypot(i - i0, j - j0) * dx < r + 2 && (kind[k2] || cut[k2] || playaM[k2] || dune[k2] || coneM[k2])) { ok = false; break; } }
    if (ok) {
      // (the pool: a bowl, its water at its rim's lowest)
      let rim = Infinity; const D = .8 + RO() * .5;
      for (let j = j0 - R0; j <= j0 + R0; j++) for (let i = i0 - R0; i <= i0 + R0; i++) {
        const d = Math.hypot(i - i0, j - j0) * dx * (1 + .12 * noise(i * dx / 3, j * dx / 3, seed + 283)), k2 = j * N + i;
        if (d < r) H[k2] -= D * (1 - (d / r) ** 2) + .25; else if (d < r + 1.2) rim = Math.min(rim, H[k2]);
      }
      let cells = 0;
      for (let j = j0 - R0; j <= j0 + R0; j++) for (let i = i0 - R0; i <= i0 + R0; i++) {
        const k2 = j * N + i, d = Math.hypot(i - i0, j - j0) * dx;
        if (H[k2] < rim - .05 && d < r + 1.5) { water[k2] = rim - .05; kind[k2] = 1; surf[k2] = 2; veg[k2] = 0; cells++; }
        else if (d < r + 11 && !kind[k2] && !cut[k2] && surf[k2] !== 0) { const v = .95 * smooth((r + 11 - d) / 6); if (v > veg[k2]) veg[k2] = v; if (surf[k2] === 5 || surf[k2] === 7 || surf[k2] === 1) surf[k2] = 3; oasisM[k2] = 1; }
      }
      if (cells > 10) { oasis = { x: i0 * dx, y: j0 * dx, r, level: rim - .05 };
        notes.push(`oasis: a pool ${Math.round(r * 2)} m across where the strongest seep's water stands at the foot of the slope, date palms round it -- the only trees for miles`); }
    }
  }
  // (TIDE POOLS: on a cliffed coast's platform, where it stands out of the water at low tide, the waves' stones grind
  // hollows in it -- each full of the sea's water when the tide goes out. Their own random numbers)
  if (coast && coast.cliffed && F.tidePools !== false) {
    const RP = rng(seed * 287 + 5), sea = coast.sea, pools = [], cand = [];
    for (let k = 0; k < n; k++) { const i = k % N, j = (k / N) | 0, e = H[k] - sea; if (shoreK[k] === 2 && !kind[k] && !cut[k] && e > .15 && e < 1.6 && i > 3 && j > 3 && i < N - 4 && j < N - 4) cand.push(k); }
    for (let t = 0; t < 400 && cand.length && pools.length < 40; t++) {
      const k0 = cand[Math.floor(RP() * cand.length)], i0 = k0 % N, j0 = (k0 / N) | 0;
      const r = .9 + RP() * 1.1; if (pools.some((p) => Math.hypot(p[0] - i0, p[1] - j0) * dx < p[2] + r + 1.5)) continue;
      const R0 = Math.ceil((r + 1.5) / dx); let rim = Infinity, ok = true;
      for (let j = j0 - R0; j <= j0 + R0 && ok; j++) for (let i = i0 - R0; i <= i0 + R0; i++) {
        const k = j * N + i, d = Math.hypot(i - i0, j - j0) * dx; if (d >= r + .9) continue;
        if (kind[k] || cut[k]) { ok = false; break; }
        if (d >= r) rim = Math.min(rim, H[k]);
      }
      if (!ok || rim - sea < .1) continue;
      const D = .3 + RP() * .25;
      for (let j = j0 - R0; j <= j0 + R0; j++) for (let i = i0 - R0; i <= i0 + R0; i++) {
        const k = j * N + i, d = Math.hypot(i - i0, j - j0) * dx * (1 + .15 * noise(i * dx / 1.5, j * dx / 1.5, seed + 289)); if (d >= r) continue;
        H[k] = Math.min(H[k], rim - D * (1 - (d / r) ** 2) - .05); water[k] = rim - .03; kind[k] = 1;
      }
      pools.push([i0, j0, r]);
    }
    if (pools.length >= 3) { coast.tidePools = pools.length; notes.push(`tide pools: ${pools.length} on the platform, ground into it by the waves' stones where it stands out of the water at low tide -- the sea's water left in them`); }
  }
  })();
  Object.assign(c, { SURF, beachS, sun, cover, SPRINGS, REEDS, reeds, springs, bogs, seepBest, seepK, oasis, oasisM,
    BOG, polyRim, rise });
}

export function riparian(c) {
  const { clim, cut, dryness0, dx, F, kind, N, n, notes, playaM, Q, runoff, seed, slope, surf, tinM, veg } = c;
  // (a RIPARIAN strip: in a dry country the plants crowd along the stream and the washes, their roots down to the water
  // under the bed -- which the rain on the land round them never gives -- a line of green through the bare land)
  (() => {
    if (dryness0 < .15 || clim.plants === "none" || F.riparian === false) return;
    const D = new Uint8Array(n).fill(9), thr = runoff * 3000; let cells = 0;
    for (let k = 0; k < n; k++) if (Q[k] > thr && !playaM[k] && kind[k] !== 1 && kind[k] !== 4) D[k] = 0;   // (a stream's, a wash's line; not a lake's, the sea's)
    for (let j = 1; j < N; j++) for (let i = 1; i < N - 1; i++) { const k = j * N + i; D[k] = Math.min(D[k], D[k - 1] + 1, D[k - N] + 1, D[k - N - 1] + 1, D[k - N + 1] + 1); }
    for (let j = N - 2; j >= 0; j--) for (let i = N - 2; i > 0; i--) { const k = j * N + i; D[k] = Math.min(D[k], D[k + 1] + 1, D[k + N] + 1, D[k + N + 1] + 1, D[k + N - 1] + 1); }
    for (let k = 0; k < n; k++) {
      if (D[k] > 4 || kind[k] || cut[k] || tinM[k]) continue;
      // (in a desert the wash's floor sand, even over the bare rock -- what the last flood left)
      if (D[k] <= 1 && dryness0 > .5 && surf[k] <= 1 && slope[k] < .2) surf[k] = 5;
      const s = surf[k]; if (!(s === 2 || s === 3 || s === 4 || s === 5 || s === 7)) continue;
      const v = (.3 + .45 * dryness0) * (1 - Math.max(0, D[k] - 1) / 4) * clamp(.6 + 1.2 * fbm((k % N) * dx / 9, ((k / N) | 0) * dx / 9, seed + 259, 2), 0, 1);
      if (v > veg[k]) { veg[k] = v; cells++; }
    }
    if (cells > 200) notes.push(`riparian: the plants along the stream and the washes, a line of green through the ${dryness0 > .6 ? "bare desert" : "dry scrub"} -- their roots down to the water under the bed`);
  })();
}

export function forest(c) {
  const { N, n, surf, veg } = c;
  let { v0 } = c;
  // (the cover blurred a little: stands have edges, not cells') -- then a cell under enough of it is forest
  (() => {
  for (let pass = 0; pass < 2; pass++) { const v0 = veg.slice();
    for (let j = 1; j < N - 1; j++) for (let i = 1; i < N - 1; i++) { const k = j * N + i; if (!v0[k] && (surf[k] < 2 || surf[k] >= 9)) continue;
      veg[k] = (v0[k] * 4 + v0[k - 1] + v0[k + 1] + v0[k - N] + v0[k + N]) / 8; } }
  })();
  (() => {
  for (let k = 0; k < n; k++) if (surf[k] >= 2 && surf[k] <= 4) surf[k] = veg[k] > .45 ? 4 : surf[k] === 4 ? 3 : surf[k];
  })();
  Object.assign(c, { v0 });
}

export function trees(c) {
  const { clim, cut, deltaM, dx, H, hoodM, kind, N, oasisM, Q, R, runoff, seed, size, surf, TOP, travM, veg, water } = c;
  // the trees: one in a 3 m square where the cover has one, its kind and height by the climate (conifers where it is
  // cold, and higher up), the dry country's few low and broad
  const trees = [];
  { const T3 = 3, RQ = rng(seed * 293 + 7);
    for (let y = T3 / 2; y < size; y += T3) for (let x = T3 / 2; x < size; x += T3) {
      const tx = clamp(x + (R() - .5) * T3 * .9, .5, size - .5), ty = clamp(y + (R() - .5) * T3 * .9, .5, size - .5), i = clamp(Math.round(tx / dx), 0, N - 1), j = clamp(Math.round(ty / dx), 0, N - 1), k = j * N + i;
      const rv = R();
      // (in a reed bed, clumps of reeds standing out of the water -- their own random numbers)
      if (surf[k] === 17) { if (RQ() < .7) for (let m = 0, mm = 2 + Math.floor(RQ() * 3); m < mm; m++) trees.push({ x: clamp(tx + (RQ() - .5) * 1.6, .3, size - .3), y: clamp(ty + (RQ() - .5) * 1.6, .3, size - .3), z: water[k] - .1, h: 1.3 + RQ() * 1.5, r: .3 + RQ() * .3, conifer: false, palm: false, shape: "reed" }); continue; }
      if (rv > veg[k] * .7 || cut[k] || hoodM[k] || travM[k] || (kind[k] && surf[k] !== 16) || (deltaM[k] && (surf[k] === 5 || surf[k] === 7)) || (surf[k] > 10 && surf[k] !== 16)) continue;
      const cold = clim.temp < 6 || (clim.temp < 12 && H[k] > TOP - 4 && R() < .5), dry = clim.plants === "scrub" || clim.plants === "desert";
      const fi = clamp(Math.floor(tx / dx), 0, N - 2), fj = clamp(Math.floor(ty / dx), 0, N - 2), zt = Math.min(H[fj * N + fi], H[fj * N + fi + 1], H[fj * N + N + fi], H[fj * N + N + fi + 1]);   // (its foot on the low side of a slope, not in the air)
      const h = dry ? 2 + R() * 3.5 : clim.plants === "tundra" ? 1.5 + R() * 3 : (cold ? 9 : 11) + R() * (clim.plants === "jungle" ? 18 : 10);
      // (in the tropics, by the water: palms -- a tall bare stem, a crown of fronds)
      let wet = Q[k] > runoff * 150; for (let b = -4; b <= 4 && !wet; b += 2) for (let a = -4; a <= 4 && !wet; a += 2) wet = kind[clamp(j + b, 0, N - 1) * N + clamp(i + a, 0, N - 1)] > 0;
      const palm = (clim.temp > 18 && !dry && wet && R() < .7) || (oasisM[k] === 1 && R() < .9);   // (an oasis's date palms)
      if (surf[k] === 16) { const hm = 4 + R() * 4; trees.push({ x: tx, y: ty, z: zt, h: hm, r: hm * (.4 + R() * .15), conifer: false, palm: false, mangrove: true }); continue; }   // (low, broad, dense)
      // (the dry country's own forms: in a hot desert the acacia, flat-topped on its bare stem; in a warm scrub among the
      // low holm oaks the cypress, a dark flame, and the stone pine's umbrella)
      if (!palm && dry && clim.temp >= 12) { const pick = R();
        const shape = clim.plants === "desert" ? (clim.temp > 18 && pick < .6 ? "umbrella" : null) : pick < .15 ? "columnar" : pick < .35 ? "umbrella" : null;
        if (shape) { const hs = shape === "columnar" ? 7 + R() * 6 : clim.plants === "desert" ? 3 + R() * 3 : 7 + R() * 5;
          trees.push({ x: tx, y: ty, z: zt, h: hs, r: shape === "columnar" ? .9 + R() * .4 : hs * (.4 + R() * .15), conifer: shape === "columnar" || clim.plants !== "desert", palm: false, shape }); continue; } }
      // (in a jungle the EMERGENTS: a tree here and there standing clear over the canopy, its crown spread flat in the sun)
      if (!palm && clim.plants === "jungle" && R() < .07 && Math.min(tx, ty, size - tx, size - ty) > 8) { const hs = 28 + R() * 10; trees.push({ x: tx, y: ty, z: zt, h: hs, r: 5.5 + R() * 2.5, conifer: false, palm: false, shape: "umbrella" }); continue; }
      trees.push({ x: tx, y: ty, z: zt, h: palm ? 9 + R() * 8 : h, r: palm ? 2.6 + R() : h * (cold ? .2 : dry ? .5 : .26) * (.8 + R() * .4), conifer: !palm && (cold || (clim.plants === "forest" && R() < .25)), palm });
    } }
  Object.assign(c, { trees });
}

export function boulders(c) {
  const { bed, capK, carved, chanW, clim, coast, coneM, cum, cut, deltaM, dikeM, dist, domes, dune, dx, eskerM, F, H,
    hLin, hoodM, kind, knockM, lake, mark, moraine, n, N, notes, poolR, pts, R, rgM, rock, S, scarpU, sCross, seed,
    sFall, shoreK, size, slope, slot, sOf, soil, streamV, surf, tinM, toUV, toXY, tufa } = c;
  // boulders: the blocks the cap shed, at the foot of the walls (where scree lies deepest), more the harder the cap
  const boulders = [];
  (() => {
  for (let k = 0; k < n; k += 7) if (soil[k] > .6 && kind[k] !== 1 && !cut[k] && !tufa[k] && !eskerM[k] && !carved[k] && !dune[k] && !shoreK[k] && !coneM[k] && !hoodM[k] && R() < (rgM[k] ? .7 : .25) * S.beds[capK].hard && !deltaM[k]) {   // (not in a cave's patch: its ground is not H)
    const i = k % N, j = (k / N) | 0; boulders.push({ x: i * dx + R() * dx, y: j * dx + R() * dx, z: H[k], r: .4 + R() * 1.3 * S.beds[capK].hard, bed: capK });
  }
  // (a dome's corestones: round its foot, rounded)
  for (const d of domes) for (let b = 0, m = 6 + Math.floor(R() * 9); b < m; b++) {
    const a = R() * TAU, rr = d.r * (1 + R() * .35), x = d.x + Math.cos(a) * rr, y = d.y + Math.sin(a) * rr, k = clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1);
    if (!kind[k] && !cut[k]) boulders.push({ x, y, z: H[k], r: .8 + R() * 1.6, bed: capK });
  }
  // (a FELSENMEER: on a cold upland the frost splits the hard cap where it lies -- its joints opened block by block, a
  // field of angular blocks hardly moved, the ground between them stones; in patches on the flats. Its own random numbers)
  if (clim.temp < 4 && S.beds[capK].hard >= .6 && F.felsenmeer !== false) {
    const RF = rng(seed * 229 + 29); let m = 0;
    for (let y = 2; y < size - 2; y += 2.2) for (let x = 2; x < size - 2; x += 2.2) {
      const k = clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1), [u, v] = toUV(x, y);
      if (u > scarpU(v) - 10 || kind[k] || cut[k] || slope[k] > .18 || knockM[k] || coneM[k] || dikeM[k] || tinM[k] || Math.abs(v - streamV(u)) < 10 || (lake && lake.dist(u, v) < 1.25)) continue;
      const f = fbm(x / 35, y / 35, seed + 231, 3); if (f < .18 || RF() > (f - .18) * 3 || S.bedAt(x, y, H[k] - .5) !== capK) continue;
      boulders.push({ x: x + (RF() - .5) * 1.6, y: y + (RF() - .5) * 1.6, z: H[k] - .2, r: .45 + RF() * .8, bed: capK }); m++;
      if (surf[k] >= 2 && surf[k] <= 4) surf[k] = 1;
    }
    if (m > 30) notes.push(`felsenmeer: ${m} blocks in fields on the upland -- the frost split the ${S.beds[capK].name} where it lies, joint by joint`);
  }
  // (a granite stream's corestones: the sound cores the rotting rock round them let go, too big for the water to move
  // -- down its bed and its banks from the plunge pool on, biggest in the gorge, smaller the further they came)
  if (S.beds[capK].rock === "granite" && F.corestones !== false) {
    const RB = rng(seed * 173 + 89), s1 = coast ? sOf(coast.uL) : cum[cum.length - 1]; let m = 0;
    for (let s = sFall + poolR * 1.5; s < s1; s += 1 + RB() * 2.4) {
      const [u, v] = atS(pts, cum, s), [x, y] = toXY(u, v + (RB() - .5) * chanW * 2.6), i = Math.round(x / dx), j = Math.round(y / dx);
      if (i < 1 || j < 1 || i > N - 2 || j > N - 2) continue;
      const k = j * N + i; if (kind[k] === 1 || kind[k] === 4 || cut[k] || tufa[k]) continue;
      boulders.push({ x, y, z: H[k], r: (.5 + RB() * 1.2) * (s < sCross ? 1.25 : clamp(1.2 - (s - sCross) / 260, .45, 1.1)), bed: capK }); m++;
    }
    if (m > 20) notes.push(`corestones: ${m} down the stream's bed -- the granite's sound cores, let go as the rock round them rotted, too big for the water to move; the biggest in the gorge`);
  }
  // (the ice's erratics: of the hardest bed -- what survived the carrying)
  const hardest = S.beds.reduce((b, o, q) => o.hard > S.beds[b].hard ? q : b, 0);
  for (const e of moraine.erratics) { const k = clamp(Math.round(e.y / dx), 0, N - 1) * N + clamp(Math.round(e.x / dx), 0, N - 1); if (!kind[k] && !cut[k]) boulders.push({ x: e.x, y: e.y, z: H[k], r: e.r, bed: hardest }); }
  })();
  // TORS: on a granite upland the blocks the joints cut, the soil washed from round them, stacked where they weathered
  // out -- a few piles, rounded, the biggest at the foot
  (() => {
  if (F.tors !== false && S.beds[capK].rock === "granite") {
    let made = 0;
    for (let t = 0; t < 60 && made < 4; t++) {
      const x = 15 + R() * (size - 30), y = 15 + R() * (size - 30), [u, v] = toUV(x, y);
      if (u > scarpU(v) - 15 || Math.abs(v - streamV(u)) < 20 || (lake && lake.r * lake.dist(u, v) < lake.r + 12)) continue;
      const i = clamp(Math.round(x / dx), 0, N - 1), j = clamp(Math.round(y / dx), 0, N - 1), z0 = H[j * N + i];
      let z = z0 - .4, tiers = 2 + Math.floor(R() * 2.5);
      for (let q = 0; q < tiers; q++) {
        const cnt = Math.max(1, 4 - q * 1.5 + Math.floor(R() * 2)), r = (2.2 - q * .45) * (.8 + R() * .4);
        for (let b = 0; b < cnt; b++) { const a = b / cnt * TAU + R(); boulders.push({ x: x + Math.cos(a) * r * (cnt > 1 ? .9 : 0), y: y + Math.sin(a) * r * (cnt > 1 ? .9 : 0), z: z + r * .2, r, bed: capK, tor: true }); }
        z += r * 1.3;
      }
      made++;
    }
    if (made) notes.push(`tors: ${made} -- the ${S.beds[capK].name}'s joint blocks, the soil washed from round them`);
  }
  // CHOCKSTONES: in the slot, blocks fallen from its rim and jammed between its walls where it is narrow -- held there
  // over the floor, the floods running under them
  if (slot && F.chockstones !== false) {
    const RC = rng(seed * 227 + 23), P = slot.pts; let made = 0;
    for (let t = 0; t < 40 && made < 3; t++) {
      const q = 3 + Math.floor(RC() * (P.length - 6)), p = P[q], p1 = P[Math.min(P.length - 1, q + 1)]; if (!p || p.w > 2.6 || p.w < 1) continue;
      const l = Math.hypot(p1.x - p.x, p1.y - p.y) || 1, nx = -(p1.y - p.y) / l, ny = (p1.x - p.x) / l, r = p.w / 2 + .3;
      const top = Math.min(hLin(p.x + nx * (p.w / 2 + 1.5), p.y + ny * (p.w / 2 + 1.5)), hLin(p.x - nx * (p.w / 2 + 1.5), p.y - ny * (p.w / 2 + 1.5)));
      const zc = p.z + 1.8 + RC() * Math.max(0, top - p.z - 4); if (zc + r > top - .6) continue;
      if (boulders.some((b) => b.chock && Math.hypot(b.x - p.x, b.y - p.y) < 6)) continue;
      boulders.push({ x: p.x, y: p.y, z: zc - r * .3, r, bed: capK, chock: true }); made++;
    }
    if (made) notes.push(`chockstones: ${made} in the slot -- blocks from its rim jammed between its walls, the floods running under them`);
  }
  })();
  // (a loose block rests on the lowest ground under it -- not on its cell's corner up a slope -- and none stays on a
  // face too steep to hold it)
  (() => {
    const hAt = (i, j) => H[clamp(j, 0, N - 1) * N + clamp(i, 0, N - 1)];
    let w = 0;
    for (const b of boulders) {
      if (b.tor || b.chock) { boulders[w++] = b; continue; }
      const i0 = Math.floor(b.x / dx), j0 = Math.floor(b.y / dx), rr = Math.max(1, Math.round(b.r * .7 / dx));
      let lo = Infinity, hi = -Infinity;
      for (let j = j0 - rr + 1; j <= j0 + rr; j++) for (let i = i0 - rr + 1; i <= i0 + rr; i++) { const h = hAt(i, j); if (h < lo) lo = h; if (h > hi) hi = h; }
      if (hi - lo > 2.4 * rr * dx + b.r) continue;   // (a cliff's face)
      b.z = Math.min(b.z, lo); boulders[w++] = b;
    }
    boulders.length = w;
  })();
  mark("dress");
  Object.assign(c, { boulders });
}

export function result(c) {
  const { barchans, bed, boulders, braid, caves, cirque, clim, coast, cone, couloirs, cut, dams, delta, dike, dolines,
    domes, dx, esker, falls, fans, fins, flow, geo, H, hoodoos, hotSpring, kind, lake, lobes, moraine, mouth, N, neck,
    notes, oasis, outliers, plan, Q, ravines, rock, rockGlacier, ruwares, S, size, slide, slope, slot, soil, stain,
    stainCol, sun, SURF, surf, T, tinajas, trees, veg, W, water, yardangs } = c;
  return { N, dx, size, H, rock, soil, W, Q, water, kind, flow, surf, SURF, stain, stainCol, bed, slope, veg, trees, boulders, caves, cut, falls, fans, couloirs, ravines, yardangs, barchans, dams, coast, mouth, delta, braid, hotSpring, cone, dike, hoodoos, slot, fins, slide, rockGlacier, cirque, oasis, domes, strata: S, climate: clim, geology: geo,
           plan, lake, outliers, dolines, tinajas, ruwares, lobes, kettles: moraine.kettles ?? [], esker, neck, sun, notes, stages: T.stages, ms: Math.round(performance.now() - T.t0) };
}
