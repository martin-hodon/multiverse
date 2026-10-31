// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- basalt country: the cinder cone, the maar, the neck and the
// dike, the hot spring, the fumaroles. Each stage takes the scene so far, `c`, and adds what it makes to it;
// landscape.js runs them in order.
import { TAU, clamp, smooth, lerp, noise, fbm, rng } from "./core.js";

export function cone(c) {
  const { capK, clim, coast, cross, cu, F, lake, n, outliers, S, scarp2U, scarpU, seed, size, STEP2, streamV, su, toXY } = c;
  // a CINDER CONE: on basalt country the youngest eruption's -- the scoria it threw up heaped round its vent (loose: its
  // flanks at the cinders' angle, ~31 deg), a crater in its top, breached on the side the lava came out; the flow a
  // tongue running down the land from the breach, lobed, its fronts steep. Its own random numbers
  const coneT = new Float32Array(n), coneM = new Uint8Array(n);   // (the cone's loose cinders' thickness, a maar's tuff; 1 cone, 2 flow, 3 maar)
  const cone = (() => {
    if (!S.beds[capK].columns || F.cone === false) return null;
    const RV = rng(seed * 73 + 17); if (RV() > (F.cone?.chance ?? .7)) return null;
    // (where the ground is full of water the rising magma met it and blew out a MAAR instead: see below)
    const maar = F.maar !== false && clim.rain > 1000 && rng(seed * 149 + 67)() < .6;
    for (let t = 0; t < 80; t++) {
      const Rb = 36 + RV() * 16, side = RV() < .5 ? -1 : 1, v = streamV(cross) + side * (Rb + 22 + RV() * size * .3), up = RV() < .6;
      const u = up ? scarpU(v) - Rb - 14 - RV() * 60 : scarpU(v) + Rb + 14 + RV() * 50, [x, y] = toXY(u, v);
      if (x < Rb + 4 || y < Rb + 4 || x > size - Rb - 4 || y > size - Rb - 4 || Math.abs(v - streamV(u)) < Rb + 18) continue;
      if ((lake && lake.r * lake.dist(u, v) < lake.r * 1.3 + Rb + 8) || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + Rb + 10)) continue;
      if ((coast && u + Rb > coast.line(v) - 12) || (!up && STEP2 && u + Rb > scarp2U(v) - 10)) continue;
      return { x, y, u, v, Rb, up, hc: Rb * (.34 + RV() * .06), a0: Math.atan2(su, cu) + (RV() - .5) * 1.4, th: 2.5 + RV() * 2, Lf: 45 + RV() * 50, ph: RV() * 9, maar };
    }
    return null;
  })();
  Object.assign(c, { coneT, coneM, cone });
}

export function maar(c) {
  const { capK, clim, coast, cone, coneM, coneT, cu, dx, F, H, half, n, N, notes, plan, S, scarp2U, scarpU, seed, size,
    STEP2, streamV, su, toUV, U, upAt, V, v0 } = c;
  let { lam } = c;
  // a MAAR: the magma came up into ground full of water, which flashed to steam and blew the rock out -- a crater cut
  // down into the beds below the land round it (its walls the country rock), a low ring of the shattered tuff it threw
  // out round its rim (loose), no lava. Its floor below the water table: a lake at that level, well under the rim
  // (`cone.wt`: the WATER stage lets it out there). Its own random numbers
  (() => {
  if (!cone?.maar) return;
  const { x: cx, y: cy, Rb } = cone, RM = rng(seed * 151 + 71), Rc = Rb * (.52 + RM() * .08), hr = 2.5 + RM() * 2, dm = 9 + RM() * 5;
  const g0 = H[Math.round(cy / dx) * N + Math.round(cx / dx)], zF = g0 - dm;
  for (let j = Math.floor((cy - Rb) / dx); j <= Math.ceil((cy + Rb) / dx); j++) for (let i = Math.floor((cx - Rb) / dx); i <= Math.ceil((cx + Rb) / dx); i++) {
    if (i < 0 || j < 0 || i >= N || j >= N) continue;
    const k = j * N + i, x = i * dx, y = j * dx, a = Math.atan2(y - cy, x - cx), r = Math.hypot(x - cx, y - cy) * (1 + .07 * noise(Math.cos(a) * 2 + cx, Math.sin(a) * 2, seed + 153));
    if (r >= Rb) continue;
    if (r < Rc) H[k] = Math.min(H[k], lerp(zF, g0 + hr, (r / Rc) ** 3.2));
    else { const t = hr * (1 - (r - Rc) / (Rb - Rc)) ** 1.6; H[k] += t; coneT[k] = t; }
    coneM[k] = 3;
  }
  Object.assign(cone, { hc: hr, Rc, floor: zF, wt: g0 - 2 - RM() * 3, flowL: 0 });
  notes.push(`maar: a crater ${Math.round(Rc * 2)} m across blown ${Math.round(dm)} m down into the ${S.beds[capK].name} -- the magma met the wet ground's water, which flashed to steam; a ring of the tuff it threw out round it, ${hr.toFixed(1)} m high, and a lake in it at the water table, ${Math.round(g0 - cone.wt)} m under the land`);
  })();
  (() => {
  if (!cone || cone.maar) return;
  const { x: cx, y: cy, Rb, hc, a0 } = cone, Rc = Rb * .4, cd = hc * .32, GA = .3 + 1.1 * clim.wet, Ng = Math.round(Rb * .7);
  for (let j = Math.floor((cy - Rb) / dx); j <= Math.ceil((cy + Rb) / dx); j++) for (let i = Math.floor((cx - Rb) / dx); i <= Math.ceil((cx + Rb) / dx); i++) {
    if (i < 0 || j < 0 || i >= N || j >= N) continue;
    const x = i * dx, y = j * dx, a = Math.atan2(y - cy, x - cx), r = Math.hypot(x - cx, y - cy) * (1 + .06 * noise(Math.cos(a) * 2 + cx, Math.sin(a) * 2, seed + 121));
    const br = smooth(1 - Math.abs(((a - a0 + 3 * Math.PI) % TAU) - Math.PI) / .75);   // (the breach)
    let z = r < Rc ? hc - cd * (1 - (r / Rc) ** 2) : r < Rb ? hc * (1 - (r - Rc) / (Rb - Rc)) ** 1.15 : 0;
    // (the breach a horseshoe's gap: the crater's floor carried out through the rim and on down the flank -- the flow
    // rafted that side of the cone away)
    const zb = (hc - cd * 1.15) * (r < Rc ? 1 : Math.max(0, 1 - (r - Rc) / (Rb - Rc)) ** 1.6);
    z = lerp(z, Math.min(z, zb), br);
    // (the flanks gullied: the rain's rills down the loose cinders, deeper the wetter -- a few metres apart, branching)
    if (r > Rc && r < Rb) z -= GA * (1 - br) * Math.sin(Math.PI * (r - Rc) / (Rb - Rc)) ** .8 * (.5 + .5 * Math.cos(Ng * a + 2.2 * noise(r / 7, a * 3, seed + 209))) ** 3;
    if (z > 0) { const k = j * N + i; H[k] += z; coneT[k] = z; coneM[k] = 1; }
  }
  // (the flow: from the breach down the land, wandering, widening, its edge lobed, its front and sides steep)
  const lim = (u, v) => cone.up ? scarpU(v) - 14 : Math.min(coast ? coast.line(v) - 10 : Infinity, STEP2 ? scarp2U(v) - 12 : Infinity, half - 6);
  // (a flow on the upland that reaches the scarp's edge pours over it -- a CASCADE down the face, the lava draped on it
  // as steep as it stood when it froze -- and runs on over the land below)
  const lowLim = (u, v) => Math.min(coast ? coast.line(v) - 10 : Infinity, STEP2 ? scarp2U(v) - 12 : Infinity, half - 6);
  let px = cx + Math.cos(a0) * Rb * .8, py = cy + Math.sin(a0) * Rb * .8, len = 0, casc = -1;
  const way = [];
  for (let t = 0; t < cone.Lf + (casc >= 0 ? 25 : 0); t += 1) {
    // (near the stream's valley it turns down along it, as the land falls, and a little away: it ponds against the
    // valley's side rather than crossing it)
    let a = a0 + .35 * Math.sin(t / 23 + cone.ph);
    { const [u0, v0] = toUV(px, py), dv = v0 - streamV(u0), w = smooth((26 - Math.abs(dv)) / 12);
      if (w > 0) { const sg = Math.sign(dv), ex = cu - sg * su * .45, ey = su + sg * cu * .45, bx = lerp(Math.cos(a), ex, w), by = lerp(Math.sin(a), ey, w); a = Math.atan2(by, bx); } }
    px += Math.cos(a); py += Math.sin(a);
    const [u, v] = toUV(px, py);
    if (cone.up && casc < 0 && u > scarpU(v) - 14 && F.cascade !== false && Math.abs(v - streamV(u)) > 30) casc = way.length;
    if (u > (casc >= 0 ? lowLim(u, v) : lim(u, v)) || Math.abs(v - streamV(u)) < 10 || px < 6 || py < 6 || px > size - 6 || py > size - 6) break;
    way.push([px, py, 6 + t * .14]); len = t;
  }
  const flow = new Float32Array(n), fq = new Float32Array(n).fill(-1), fd = new Float32Array(n).fill(9);   // (each cell's nearest point of the way, how far across)
  way.forEach(([wx, wy, w], q) => { const front = smooth((way.length - q) / 6);
    for (let j = Math.floor((wy - w * 1.3) / dx); j <= Math.ceil((wy + w * 1.3) / dx); j++) for (let i = Math.floor((wx - w * 1.3) / dx); i <= Math.ceil((wx + w * 1.3) / dx); i++) {
      if (i < 0 || j < 0 || i >= N || j >= N) continue;
      const k = j * N + i, d = Math.hypot(i * dx - wx, j * dx - wy) / (w * (1 + .25 * fbm(i * dx / 9, j * dx / 9, seed + 123, 2)));
      if (d < 1) flow[k] = Math.max(flow[k], cone.th * smooth((1 - d) * w / 2.5) * (.6 + .4 * front) * (1 + .15 * noise(i * dx / 4, j * dx / 4, seed + 125)));
      if (d < fd[k]) { fd[k] = d; fq[k] = q; }
      if (casc >= 0 && q >= casc - 3 && d < 1) {   // (the cascade: from the edge down the face, its middle thickest)
        const sc = scarpU(V[k]), b = U[k] - (sc - 1); if (b < -1 || b > 30) continue;
        const x = i * dx, y = j * dx, zr = upAt(x, y, sc - 1) + cone.th * .5 - Math.max(0, b) * 1.1, lat = smooth((1 - d) / .4);
        if (zr > H[k]) flow[k] = Math.max(flow[k], (zr - H[k]) * lat);
      }
    } });
  // (its LEVEES: near the vent the lava ran on in a channel down its middle, the edges chilled and stood -- and when the
  // eruption stopped the channel drained, leaving it a trough between two banks; toward the front it stalled whole)
  for (let k = 0; k < n; k++) if (fq[k] >= 0 && fd[k] < 1 && flow[k] > .2) {
    const ch = smooth((.62 - fq[k] / way.length) / .2) * Math.min(1, flow[k] / cone.th * 1.4);
    flow[k] += ch * (.9 * Math.exp(-(((fd[k] - .4) / .11) ** 2)) - 1.1 * smooth((.27 - fd[k]) / .12));
  }
  // (its PRESSURE RIDGES: the crust buckled as the flow behind pushed on the slowing front -- arcs across it, bowed
  // downstream, every 5-8 m, a metre or so high, more toward the front)
  const lam = 5 + rng(seed * 211 + 3)() * 3;
  for (let k = 0; k < n; k++) if (fq[k] >= 0 && fd[k] < .9 && flow[k] > .2) {
    const c = Math.cos(TAU * (fq[k] + 7 * fd[k] * fd[k]) / lam + 1.5 * noise((k % N) * dx / 11, ((k / N) | 0) * dx / 11, seed + 213));
    flow[k] += (.5 + .7 * fq[k] / way.length) * Math.max(0, c) ** 3 * smooth((.9 - fd[k]) / .3);
  }
  // (HORNITOS: over the channel the gas still in the lava burst out through the crust and threw up spatter, which
  // welded where it fell -- small steep cones on the flow, each with a throat down its middle; in a row down the channel,
  // a few. Welded: rock, standing steep. Their own random numbers)
  const horn = [], hornM = new Uint8Array(n);
  if (F.hornitos !== false && way.length > 40) {
    const RH = rng(seed * 283 + 9), nh = 2 + Math.floor(RH() * 4);
    for (let t = 0; t < 30 && horn.length < nh; t++) {
      const q = Math.floor(way.length * (.12 + RH() * .55)), [wx, wy, w] = way[q], off = (RH() - .5) * .3 * w, a = Math.atan2(way[Math.min(way.length - 1, q + 2)][1] - wy, way[Math.min(way.length - 1, q + 2)][0] - wx);
      const x = wx - Math.sin(a) * off, y = wy + Math.cos(a) * off, r = 2 + RH() * 1.6, h = 1.8 + RH() * 2.2;
      if (casc >= 0 && Math.abs(q - casc) < 12) continue;   // (not on the face)
      if (horn.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r + 3)) continue;
      horn.push({ x, y, r, h });
      const R0 = Math.ceil((r + 1) / dx), i0 = Math.round(x / dx), j0 = Math.round(y / dx);
      for (let j = Math.max(0, j0 - R0); j <= Math.min(N - 1, j0 + R0); j++) for (let i = Math.max(0, i0 - R0); i <= Math.min(N - 1, i0 + R0); i++) {
        const k = j * N + i, d = Math.hypot(i * dx - x, j * dx - y) / (r * (1 + .15 * noise(i * dx / 1.7, j * dx / 1.7, seed + 285))); if (d >= 1) continue;
        const z = h * (1 - d) ** 1.1 - (d < .22 ? (h * .55) * (1 - d / .22) : 0);   // (the throat)
        if (fq[k] >= 0 && flow[k] > .2) { flow[k] += z; hornM[k] = 1; }
      }
    }
    if (horn.length) cone.hornitos = horn;
  }
  for (let k = 0; k < n; k++) if (flow[k] > .2 && !coneM[k]) { H[k] += flow[k]; coneM[k] = hornM[k] ? 1 : 2; }   // (the spatter the cinders' red)
  cone.flowL = len;
  if (casc >= 0 && casc < way.length - 3) cone.cascade = { x: way[casc][0], y: way[casc][1] }; else casc = -1;
  notes.push(`cinder cone: ${Math.round(Rb * 2)} m across, ${hc.toFixed(0)} m high, on the ${cone.up ? "upland" : "lowland"} -- the youngest eruption's scoria round its vent; its crater breached where a lava flow came out and ran ${Math.round(len)} m down the land` + (casc >= 0 ? `, over the scarp's edge in a cascade down its face and on over the land below` : "") + (horn.length ? `; ${horn.length} hornitos on it, spatter cones up to ${Math.max(...horn.map((o) => o.h)).toFixed(1)} m over its channel` : ""));
  })();
  plan.cone = cone;
  Object.assign(c, { lam });
}

export function dike(c) {
  const { capK, carved, chanW, coast, cone, coneM, domes, dryness0, dx, F, fanBase, fanT, H, lake, n, N, notes,
    outliers, rgM, S, scarp2U, scarpU, seed, size, slide, STEP2, streamV, toUV, toXY } = c;
  // a DIKE: in basalt country the magma that fed the flows came up cracks -- radiating from the vent where there is
  // one -- and set in them as walls of basalt; harder than the rock round them, they stand out as it wears away: a
  // long narrow wall across the land below the step, broken here and there, the stream through a notch it cut. Its
  // own random numbers
  const dikeM = new Uint8Array(n);   // 1 the dike's rock (SETTLE: it stands as basalt, whatever bed it rises through)
  // a NECK: where the cone is long gone -- the land worn down round where it stood -- the magma that set in its pipe
  // stands up out of it: a tower of basalt, sheer (its columns on end round its sides: they set at right angles to the
  // pipe's walls they cooled against), its top ragged, a skirt of their fallen pieces round its foot; the dikes run out
  // from it. Its own random numbers
  let neck = null;
  (() => {
  if (F.neck === false || !S.beds[capK].columns) return;
  const RN = rng(seed * 337 + 13); if (F.neck !== true && RN() > (F.neck?.chance ?? (cone ? .3 : .7))) return;   // (by a young cone, an old one's: a field of vents)
  for (let t = 0; t < 60 && !neck; t++) {
    const r = 8 + RN() * 7, h = 16 + RN() * 14, up = RN() < .35, ph = RN() * TAU;
    const v = (RN() - .5) * size * .8, u = up ? scarpU(v) - r - 22 - RN() * 70 : scarpU(v) + r + 20 + RN() * 60, [x, y] = toXY(u, v);
    if (x < r * 1.6 + 8 || y < r * 1.6 + 8 || x > size - r * 1.6 - 8 || y > size - r * 1.6 - 8 || Math.abs(v - streamV(u)) < r * 1.6 + 18) continue;
    if ((lake && lake.r * lake.dist(u, v) < lake.r + r + 14) || outliers.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r * 1.6 + 10) || domes.some((o) => Math.hypot(o.x - x, o.y - y) < o.r + r * 1.6 + 10) || (cone && Math.hypot(cone.x - x, cone.y - y) < cone.Rb + r * 1.6 + 25)) continue;
    if ((coast && u + r * 1.6 > coast.line(v) - 12) || (!up && STEP2 && Math.abs(u - scarp2U(v)) < r * 1.6 + 8) || (slide && Math.hypot(slide.x - x, slide.y - y) < slide.Wl + r * 1.6 + 8)) continue;
    const R2 = r * 1.8, i0 = Math.max(0, Math.floor((x - R2) / dx)), i1 = Math.min(N - 1, Math.ceil((x + R2) / dx)), j0 = Math.max(0, Math.floor((y - R2) / dx)), j1 = Math.min(N - 1, Math.ceil((y + R2) / dx));
    let clear = true, base = Infinity;
    for (let j = j0; j <= j1 && clear; j++) for (let i = i0; i <= i1; i++) { const k = j * N + i; if (rgM[k] || carved[k] || coneM[k] || fanT[k] > .3) { clear = false; break; } if (Math.hypot(i * dx - x, j * dx - y) < R2) base = Math.min(base, H[k]); }
    if (!clear) continue;
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
      const k = j * N + i, X = i * dx, Y = j * dx, a = Math.atan2(Y - y, X - x);
      const rr = r * (1 + .16 * noise(Math.cos(a) * 1.4 + x, Math.sin(a) * 1.4, seed + 339) + .08 * Math.cos(3 * (a - ph))), d = Math.hypot(X - x, Y - y) / rr;
      if (d < 1) {
        // (its top: highest off-centre, broken down in steps where columns fell -- ragged)
        const z = base + h * (1 - .22 * d ** 2.5 - .12 * smooth(d * Math.cos(a - ph) * .5 + .5)) + 1.6 * noise(X / 2.6, Y / 2.6, seed + 341) * smooth(d / .5);
        if (z > H[k]) { H[k] = z; fanBase[k] = z; dikeM[k] = 1; carved[k] = 0; }
      } else if (d < 1.8) {
        const z = base + h * .28 * ((1.8 - d) / .8) ** 1.5 + .6 * noise(X / 2, Y / 2, seed + 343);   // (the skirt: loose)
        if (z > H[k]) H[k] = z;
      }
    }
    neck = { x, y, r, h, up };
    notes.push(`neck: a tower of basalt ${Math.round(r * 2)} m across, ${Math.round(h)} m high, on the ${up ? "upland" : "land below the step"} -- the magma that set in an old volcano's pipe, standing where the cone round it has worn away${cone ? " (older than the young cone's: the field's vents of all ages)" : ""}; its columns on end round its sides, their fallen pieces a skirt round its foot`);
  }
  })();
  let dike = null;
  (() => {
  if (F.dike === false || !S.beds[capK].columns) return;
  const RD = rng(seed * 179 + 97); if (RD() > (F.dike?.chance ?? .75)) return;
  const low = (x, y) => { const [u, v] = toUV(x, y); return x > 6 && y > 6 && x < size - 6 && y < size - 6 && u > scarpU(v) + 12 && (!STEP2 || Math.abs(u - scarp2U(v)) > 10) && (!coast || u < coast.line(v) - 8); };
  for (let t = 0; t < 60 && !dike; t++) {
    const L = 90 + RD() * 80, a = RD() * TAU, ca = Math.cos(a), sa = Math.sin(a);
    const vent = cone ?? neck, rad = !!vent && t < 30;   // (out from the vent if it can reach the land below; else a crack of its own)
    const x0 = rad ? vent.x + ca * ((vent.Rb ?? vent.r) + 8) : 20 + RD() * (size - 40), y0 = rad ? vent.y + sa * ((vent.Rb ?? vent.r) + 8) : 20 + RD() * (size - 40);
    let inLow = 0; for (let q = 0; q <= 20; q++) if (low(x0 + ca * L * q / 20, y0 + sa * L * q / 20)) inLow++;
    if (inLow < 14) continue;
    const hw = .8 + RD() * .7, hd = (3 + RD() * 3.5) * (1 + .4 * dryness0), ph = RD() * 100;
    let cells = 0, top = 0;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const x = i * dx, y = j * dx, al = (x - x0) * ca + (y - y0) * sa; if (al < -2 || al > L + 2) continue;
      const c = Math.abs(-(x - x0) * sa + (y - y0) * ca - 2.2 * fbm(al / 40, ph, seed + 159, 2)); if (c > hw + 1.4) continue;
      const k = j * N + i, [u, v] = toUV(x, y); if (!low(x, y) || Math.abs(v - streamV(u)) < chanW * 1.8 || fanT[k] > .3 || rgM[k] || coneM[k] || (slide && Math.hypot(slide.x - x, slide.y - y) < slide.Wl + 6)) continue;
      const q = al / L, gap = fbm(al / 16, ph + 3, seed + 163, 2) < -.32 ? .12 : 1;   // (broken: where it was jointed closest, it fell)
      const h = hd * (.6 + .4 * clamp(fbm(al / 25, ph + 7, seed + 161, 2) + .5, 0, 1)) * smooth(q / .08) * smooth((1 - q) / .08) * gap * (1 - .3 * smooth((q - .6) / .4));
      const z = c < hw ? h : h * .35 * (1 - (c - hw) / 1.4); if (z < .3) continue;
      H[k] += z; fanBase[k] = Math.max(fanBase[k], H[k]); if (c < hw) { dikeM[k] = 1; cells++; top = Math.max(top, z); }
    }
    if (cells < 40) continue;
    const [mx, my] = [x0 + ca * L / 2, y0 + sa * L / 2], b = S.bedAt(mx, my, H[Math.round(my / dx) * N + Math.round(mx / dx)] - top - .5);
    dike = { x0, y0, x1: x0 + ca * L, y1: y0 + sa * L, w: hw * 2, h: top, radial: rad };
    notes.push(`dike: a wall of basalt ${Math.round(L)} m long, ${(hw * 2).toFixed(1)} m thick, up to ${top.toFixed(1)} m high over the ${S.beds[b].name} -- magma that set in a crack ${dike.radial ? (cone ? "running out from the cone's vent" : "running out from the neck") : "up from below"}, harder than the rock round it, which wore away; broken in places, the stream through a notch`);
  }
  })();
  Object.assign(c, { dikeM, neck, dike });
}

export function hotSpring(c) {
  const { carved, coast, cone, coneM, dikeM, dx, F, H, lake, LINE, n, N, notes, rgM, rock, scarpU, seed, size, slide,
    soil, streamV, toUV, tufa } = c;
  let { dist, su } = c;
  // a HOT SPRING: on basalt country with a young cone the ground is still warm below -- water that went down comes up
  // hot, full of lime, out on a slope near the cone, and drops it where it spreads and cools: TRAVERTINE, an apron of
  // terraces down the slope, each a pool held by a rim of it, the rims curved round the way the water spills over
  // them (the pools given water after the WATER stage: each its own level). Its own random numbers
  const travM = new Uint8Array(n), travL = new Float32Array(n);   // 1 the terraces' rock, 2 a pool (travL: its level)
  const hotSpring = (() => {
    if (F.hotspring === false || !cone) return null;
    const RV = rng(seed * 139 + 61), hAt = (x, y) => H[clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1)];
    for (let t = 0; t < 60; t++) {
      const an = RV() * TAU, dist = cone.Rb + 12 + RV() * 40, vx = cone.x + Math.cos(an) * dist, vy = cone.y + Math.sin(an) * dist;
      if (vx < 34 || vy < 34 || vx > size - 34 || vy > size - 34) continue;
      // (down the slope, or on the flat any way: then the apron makes its own slope, a mound)
      const gx0 = (hAt(vx + 3, vy) - hAt(vx - 3, vy)) / 6, gy0 = (hAt(vx, vy + 3) - hAt(vx, vy - 3)) / 6, tS = Math.hypot(gx0, gy0), deg = Math.atan(tS) * 180 / Math.PI;
      if (deg > 16) continue;
      const fa = RV() * TAU, gx = tS > .02 ? gx0 : -Math.cos(fa) * .02, gy = tS > .02 ? gy0 : -Math.sin(fa) * .02;
      const [vu, vv] = toUV(vx, vy), su = scarpU(vv);
      if ((vu > su - 12 && vu < su + 18) || Math.abs(vv - streamV(vu)) < 30 || (lake && lake.dist(vu, vv) < 1.5) || (coast && vu > LINE[clamp(Math.round(vy / dx), 0, N - 1) * N + clamp(Math.round(vx / dx), 0, N - 1)] - 30)) continue;
      const L0 = 22 + RV() * 14, W0 = 6 + RV() * 3, Wl = W0 * (1.7 + RV() * .4), h = 2 + RV() * 1.5, sp = 2.2 + RV(), dxn = -gx / Math.hypot(gx, gy), dyn = -gy / Math.hypot(gx, gy), zv = hAt(vx, vy);
      // (none of it on the cone, the slot, the fins, a slide, a rock glacier, or in the stream's bed)
      let clear = true;
      for (let a = -4; a <= L0 + 3 && clear; a += 2) for (let b = -Wl; b <= Wl; b += 2) {
        const x = vx + dxn * a - dyn * b, y = vy + dyn * a + dxn * b, i = Math.round(x / dx), j = Math.round(y / dx);
        if (i < 1 || j < 1 || i >= N - 1 || j >= N - 1) { clear = false; break; }
        const k = j * N + i; if (coneM[k] || carved[k] || rgM[k] || dikeM[k] || (slide && Math.hypot(slide.x - x, slide.y - y) < slide.Wl + 10)) { clear = false; break; }
      }
      if (!clear) continue;
      // (each pool a step down from the last -- by the slope's fall over it, by 0.35 m at least: on the flat the apron
      // stands up as a mound, and ends where its pools come down to the ground)
      const tDn = Math.min(tS, .28), d = Math.max(.35, (tDn + h / L0) * sp), L = d > tDn * sp ? Math.min(L0, sp * Math.max(3, Math.floor((h + .55) / (d - tDn * sp)))) : L0;
      const lev = (q) => zv + h + .85 - (q + 1) * d;
      let pools = 0;
      const R0 = Math.hypot(L + 4, Wl + 3);
      for (let j = Math.max(0, Math.floor((vy - R0) / dx)); j <= Math.min(N - 1, Math.ceil((vy + R0) / dx)); j++) for (let i = Math.max(0, Math.floor((vx - R0) / dx)); i <= Math.min(N - 1, Math.ceil((vx + R0) / dx)); i++) {
        const k = j * N + i, x = i * dx, y = j * dx, a = (x - vx) * dxn + (y - vy) * dyn, b = -(x - vx) * dyn + (y - vy) * dxn;
        if (a < -4 || a > L + 3) continue;
        const W = W0 + (Wl - W0) * clamp(a / L, 0, 1), e = Math.abs(b) / W * (1 + .12 * fbm(x / 6, y / 6, seed + 141, 2)) + (a < 0 ? -a / 4 : 0);
        if (e > 1.2) continue;
        const ae = Math.max(0, a) + .9 * b * b / W, q = Math.floor(ae / sp), f = ae / sp - q, lv = lev(q);
        let z;
        if (f < .6) z = lv - .05 - .4 * Math.sin(Math.PI * f / .6);                       // (the pool's floor)
        else z = lerp(lv + .15, lev(q + 1) - .05, smooth((f - .8) / .2));                  // (its rim, and over it down to the next)
        const wE = smooth((1.2 - e) / .3), zn = lerp(H[k], z, wE);
        H[k] = zn; rock[k] = zn; soil[k] = 0; carved[k] = 0; tufa[k] = 1;
        travM[k] = 1; if (f < .6 && e < .85) { travM[k] = 2; travL[k] = lv; pools++; }
      }
      notes.push(`hot spring: a travertine apron ${Math.round(L)} m down the slope by the cone, ${Math.round(L / sp)} terraces of rimmed pools -- the warm ground's water, full of lime, drops it as it spreads and cools`);
      return { x: vx, y: vy, dir: [dxn, dyn], L, W: Wl, pools };
    }
    return null;
  })();
  Object.assign(c, { travM, travL, hotSpring, dist, su });
}

export function fumaroles(c) {
  const { cone, dx, F, H, N, notes, seed } = c;
  // FUMAROLES: the young cone not done -- its gas still coming up through the cinders at a few vents in the crater and
  // on its rim (the breach side spent): the sulphur crusting yellow round each, the ground round it bleached and
  // rotted to clay by the acid; warm -- no snow lies on them, nothing grows. Its own random numbers
  const fumes = [];
  if (cone && !cone.maar && F.fumaroles !== false) { const RU = rng(seed * 297 + 3);
    if (RU() < (F.fumaroles?.chance ?? .7)) { const Rc = cone.Rb * .4;
      for (let q = 0, m = 3 + Math.floor(RU() * 5); q < m; q++) {
        const a = cone.a0 + Math.PI + (RU() - .5) * Math.PI * 1.5, rr = Rc * (.5 + RU() * .65), x = cone.x + Math.cos(a) * rr, y = cone.y + Math.sin(a) * rr;
        if (fumes.some((o) => Math.hypot(o.x - x, o.y - y) < 5)) continue;
        fumes.push({ x, y, z: H[clamp(Math.round(y / dx), 0, N - 1) * N + clamp(Math.round(x / dx), 0, N - 1)], r: 1.8 + RU() * 2.4 });
      }
      cone.fumaroles = fumes;
      notes.push(`fumaroles: ${fumes.length} vents in the cone's crater and on its rim -- its gas still coming up, the sulphur crusted yellow round them, the ground bleached by the acid; warm, bare`); } }
  Object.assign(c, { fumes });
}
