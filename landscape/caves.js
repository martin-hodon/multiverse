// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- what a heightfield cannot hold: the caves, the natural bridge.
// Each stage takes the scene so far, `c`, and adds what it makes to it; landscape.js runs them in order.
import { clamp, lerp, noise, rng, atS } from "./core.js";
import { surfaceNets } from "./mesh.js";

export function caves(c) {
  const { archAt, capK, chanD, clim, coast, cross, cu, dolines, F, fallH, fallU, FAULT, gorgeL, hLin, mouth, n, poolR,
    profAt, R, S, scarpU, seed, sFall, size, softK, streamV, su, toXY } = c;
  let { pts, v0 } = c;
  // CAVES: what a heightfield cannot hold -- a hollow under rock -- as a patch of volume: the rock solid under the ground
  // and outside the cave's shape (capsules, flattened, on a floor of what has settled in it), meshed (surface nets) and
  // put in place of the ground's cells it covers. What hollow the rock makes is the geology's:
  //   a soft bed under a hard cap: an ALCOVE -- the soft bed weathered back from under the cap's edge, an overhang
  //   limestone over marl: a SPRING CAVE -- the rain that sank through the karst runs out at the marl, along a passage
  //   it dissolved, a chamber where two joints cross; the stream comes out of its mouth
  //   basalt: a LAVA TUBE -- a flow's crust went hard while the lava ran on inside; where its roof is thin it fell in
  //   behind a fall that runs all year: a GROTTO -- the spray and the plunge took the soft rock from behind the curtain
  //   granite (no soft bed): a ROCK SHELTER at the fault scarp's foot -- a sheet joint parallel to the face let the
  //   slab under it spall away, the rock above overhanging, low and wide
  const caves = [], cut = new Uint8Array(n), flooded = [];   // (flooded: a flooded cave's cells and their ground before, in pairs)
  const faceAt = (x, y, d, z, max = 90) => { for (let t = 0; t < max; t += .5) { const px = x + d[0] * t, py = y + d[1] * t;
    if (px < 4 || py < 4 || px > size - 4 || py > size - 4) return null; if (hLin(px, py) < z) return [px, py]; } return null; };
  const inward = [-cu, -su], along = [-su, cu];   // into the upland (the scarp faces +u), along the scarp
  const contactAt = (x, y) => S.topOf(x, y, softK);   // the cap's foot: the soft bed's top
  const cave = (kind, parts, floor, mouth, why, out = [cu, su]) => caves.push({ kind, parts, floor, mouth, out, why });   // (out: the way its mouth faces)
  (() => {
  if (F.cave && capK >= 0 && softK >= 0) {
    const cap = S.beds[capK];
    // (on the scarp, well aside from the stream)
    const side = R() < .5 ? -1 : 1, va = streamV(cross) + side * (55 + R() * 45), [sx, sy] = toXY(scarpU(va) - 35, va);
    const zc = contactAt(sx, sy), m = faceAt(sx, sy, [cu, su], zc + 1.5);
    if (m && cap.karst) {
      // the passage: from the mouth into the hill, turning at the joints, rising a little; a chamber halfway
      const parts = []; let [x, y] = [m[0] + cu * 2, m[1] + su * 2], z = zc + 1.2, a = Math.atan2(inward[1], inward[0]);
      for (let q = 0; q < 6; q++) {
        const len = 6 + R() * 4, nx = x + Math.cos(a) * len, ny = y + Math.sin(a) * len, nz = z + .25;
        parts.push({ a: [x, y, z], b: [nx, ny, nz], r: 2 + R() * .9, rz: 1.7 + R() * .8 });
        if (q === 3) parts.push({ a: [nx, ny, nz + .8], b: [nx + Math.cos(a + 1.3) * 4, ny + Math.sin(a + 1.3) * 4, nz + 1], r: 5, rz: 3.4 });
        x = nx; y = ny; z = nz; a += (R() - .5) * 1.1;
      }
      cave("spring cave", parts, zc + .3, m, `a spring cave: the rain that sank through the ${cap.name} runs out over the ${S.beds[softK].name}`);
    } else if (m && cap.columns) {
      const parts = []; let [x, y] = [m[0] + cu * 2, m[1] + su * 2], a = Math.atan2(inward[1], inward[0]); const z = zc + cap.t * .45;
      for (let q = 0; q < 6; q++) { const len = 7 + R() * 3, nx = x + Math.cos(a) * len, ny = y + Math.sin(a) * len;
        parts.push({ a: [x, y, z], b: [nx, ny, z - .2], r: 2.6, rz: 2.1 }); x = nx; y = ny; a += (R() - .5) * .5;
        if (q === 3) parts.push({ a: [x, y, z + 1], b: [x, y, z + 12], r: 2.2, rz: 2.2 });   // (where the roof fell in: a skylight)
      }
      cave("lava tube", parts, z - 1.3, m, `a lava tube in the ${cap.name}: the flow's crust set while the lava ran on inside; a skylight where its roof fell in`);
    } else if (m) {
      const L = 14 + R() * 12, [cx0, cy0] = [m[0] + inward[0] * 1.5, m[1] + inward[1] * 1.5], z = zc + .6;
      cave("alcove", [{ a: [cx0 - along[0] * L / 2, cy0 - along[1] * L / 2, z], b: [cx0 + along[0] * L / 2, cy0 + along[1] * L / 2, z], r: 5 + R() * 2, rz: 3.2 }],
           zc - 1.2, m, `an alcove: the ${S.beds[softK].name} weathered back from under the ${cap.name}, which overhangs it`);
    }
  } else if (F.cave && capK >= 0 && FAULT) {
    const cap = S.beds[capK], side = R() < .5 ? -1 : 1, va = streamV(cross) + side * (50 + R() * 50), [sx, sy] = toXY(scarpU(va) - 30, va);
    const [fx, fy] = toXY(scarpU(va) + 12, va), zf = hLin(fx, fy), m = faceAt(sx, sy, [cu, su], zf + 2.2);
    if (m) {
      const L = 10 + R() * 8, [cx0, cy0] = [m[0] + inward[0] * .8, m[1] + inward[1] * .8], z = zf + 1.4;
      cave("rock shelter", [{ a: [cx0 - along[0] * L / 2, cy0 - along[1] * L / 2, z], b: [cx0 + along[0] * L / 2, cy0 + along[1] * L / 2, z + .4], r: 3.8 + R(), rz: 1.9 }],
           zf + .2, m, `a rock shelter: a sheet joint let the ${cap.name} under it spall away from the fault's face, the rock above overhanging`);
    }
  }
  })();
  (() => {
  if (F.cave && F.waterfall !== false && gorgeL > 0 && clim.flows && softK >= 0) {
    // behind the fall: the wall at the pool's level, found from the lip down the stream
    const [lx, ly] = toXY(fallU - 25, streamV(fallU - 25)), [ax, ay] = toXY(fallU - 24, streamV(fallU - 24)), dl = Math.hypot(ax - lx, ay - ly), d = [(ax - lx) / dl, (ay - ly) / dl];
    const zp = profAt(sFall + poolR * .6) + chanD + .3, m = faceAt(lx, ly, d, zp + 2.5, 60);
    if (m) { const al = [-d[1], d[0]], L = 7 + fallH * .25, c = [m[0] - d[0] * 1.2, m[1] - d[1] * 1.2], z = zp + 1.8;
      cave("grotto", [{ a: [c[0] - al[0] * L / 2, c[1] - al[1] * L / 2, z], b: [c[0] + al[0] * L / 2, c[1] + al[1] * L / 2, z], r: 3.6, rz: 2.8 }], zp + .2, m,
           `a grotto behind the fall: the spray took the ${S.beds[softK].name} from behind the curtain`, d); }
  }
  })();
  // on a cliffed coast the waves work in along a joint at the cliff's foot: a SEA CAVE, the sea in its mouth; and
  // through the biggest stack, where two caves from either side met: a SEA ARCH (`flood`: the ground under its opening let
  // down, so the sea comes in -- the patch stands in for those cells)
  (() => {
  if (!F.cave || !coast?.cliffed) return;
  const RS = rng(seed * 61 + 9), { sea, line, vS, coveR } = coast, out = [cu, su];
  for (let t = 0; t < 30; t++) {
    const v = (RS() - .5) * size * .9; if (Math.abs(v - vS) < coveR + 14) continue;
    const [sx, sy] = toXY(line(v) - 14, v), m = faceAt(sx, sy, out, sea + 1.6, 30); if (!m) continue;
    const L = 9 + RS() * 7, z = sea + 1.1, [ex, ey] = [m[0] - cu * L, m[1] - su * L];
    if (hLin(ex, ey) < sea + 6) continue;   // (rock over it: the cliff, not a notch)
    const parts = [{ a: [m[0] + cu * 1.5, m[1] + su * 1.5, z], b: [ex, ey, z - .3], r: 2.4 + RS(), rz: 2 + RS() * .8 }];
    // (a BLOWHOLE: where a joint crosses its end the waves' blows, the air in it squeezed, opened the joint up to the
    // top -- a shaft the spray comes up)
    const blow = F.blowhole !== false && RS() < .6, top = hLin(ex, ey);
    if (blow) { const r = 1.3 + RS() * .6; parts.push({ a: [ex - cu * .8, ey - su * .8, z + .4], b: [ex - cu * .8, ey - su * .8, top + 3], r, rz: r }); coast.blowhole = { x: ex - cu * .8, y: ey - su * .8, r, z: top }; }
    caves.push({ kind: "sea cave", parts, floor: sea - .5, mouth: m, out,
      flood: true, why: `a sea cave: the waves worked in along a joint at the cliff's foot` + (blow ? `; a blowhole at its end, up ${Math.round(top - sea)} m to the top -- the waves squeezed the air in it and opened a joint over it` : "") });
    break;
  }
  const st = coast.stacks.filter((o) => o.r > 4 && hLin(o.x, o.y) > sea + 6).sort((a, b) => b.r - a.r)[0];
  if (st) {
    const al = [cu, su], hs = hLin(st.x, st.y) - sea, rz = Math.min(hs * .38, st.r * .75), z = sea + rz * .55, e = st.r * 1.6 + 2;
    caves.push({ kind: "sea arch", parts: [{ a: [st.x - al[0] * e, st.y - al[1] * e, z], b: [st.x + al[0] * e, st.y + al[1] * e, z], r: st.r * .42, rz }], floor: sea - 1.2, mouth: [st.x + cu * st.r, st.y + su * st.r], out,
      flood: true, why: `a sea arch through a stack: two caves the waves cut from either side met` });
  }
  // (a NOTCH: where the cliff's foot is limestone the sea dissolves it at its own level -- the snails and the algae
  // grazing it help -- a groove along the foot, the cliff overhanging it)
  if (F.notch === false) return;
  const RN = rng(seed * 257 + 11), sc = caves.find((c) => c.kind === "sea cave");
  for (let t = 0; t < 12; t++) {
    const v0 = (RN() - .5) * size * .8, Ln = 30 + RN() * 30, pts = [];
    for (let v = v0; v <= v0 + Ln; v += 3) {
      if (Math.abs(v - vS) < coveR + 10) break;
      const [sx, sy] = toXY(line(v) - 14, v), m = faceAt(sx, sy, out, sea + 1, 30); if (!m) break;
      if (!S.beds[S.bedAt(m[0], m[1], sea + 1)]?.karst || hLin(m[0] - cu * 4, m[1] - su * 4) < sea + 4 || (sc && Math.hypot(m[0] - sc.mouth[0], m[1] - sc.mouth[1]) < 8)) break;
      pts.push([m[0] - cu * .4, m[1] - su * .4, sea + .9]);
    }
    if (pts.length < 6) continue;
    const parts = []; for (let q = 0; q + 1 < pts.length; q++) parts.push({ a: pts[q], b: pts[q + 1], r: 1.5 + .8 * RN(), rz: .75 + .4 * RN() });   // (deeper where the rock is weaker)
    const mid = pts[pts.length >> 1];
    caves.push({ kind: "notch", parts, floor: sea - .3, mouth: [mid[0], mid[1]], out, flood: true,
      why: `a notch along the cliff's foot, ${(pts.length - 1) * 3} m of it: the sea dissolves the limestone at its own level, the cliff overhanging it` });
    break;
  }
  })();
  // the fin's arch: its window through, from the corridor on one side to the one on the other
  (() => {
  if (!archAt || !F.cave) return;
  const { a, b, z0, rz, r, top } = archAt, z = z0 + .7 + rz, out = [b[0] - a[0], b[1] - a[1]], l = Math.hypot(...out) || 1, m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  caves.push({ kind: "arch", parts: [{ a: [m[0] - out[0] / l * .4, m[1] - out[1] / l * .4, z], b: [m[0] + out[0] / l * .4, m[1] + out[1] / l * .4, z], r, rz }], floor: z0 - 1, mouth: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], out: [out[0] / l, out[1] / l],
    top, why: `an arch: a window weathered through a fin, ${(r * 2).toFixed(0)} m across, ${(rz * 2).toFixed(0)} m high, its span ${(top - z - rz).toFixed(1)} m thick` });
  })();
  // the cenote's bell: the cave its roof fell into, wider than the shaft -- the rim overhangs the pool
  (() => {
  for (const o of dolines) if (o.cenote && F.cave)
    caves.push({ kind: "cenote", parts: [{ a: [o.x, o.y, o.wt - 1.2], b: [o.x, o.y, o.wt + .6], r: o.r * 1.35, rz: 3 }], floor: o.floor, mouth: [o.x, o.y], out: [cu, su], flood: true,
      why: `a cenote: a doline that fell into a cave at the water table -- its walls sheer, its rim overhanging the pool ${Math.round(o.r * 2)} m across` });
  })();
  Object.assign(c, { caves, cut, flooded, faceAt, inward, along, contactAt, cave, pts, v0 });
}

export function bridge(c) {
  const { capK, carved, caves, chanD, cum, cut, dx, F, FAULT, flooded, gorgeL, gorgeW, H, hLin, mark, mouth, n, N,
    notes, profAt, pts, R, rock, S, sCross, seed, sFall, size, soil, toXY, trib, upAt } = c;
  let { half } = c;
  // a NATURAL BRIDGE over the gorge: a span of the cap the stream went under -- through a meander's neck in sandstone,
  // the roof of a cave it ran in (karst), a lava tube's (basalt) -- the rest fell and was carried away
  (() => {
  if (F.bridge && gorgeL > 30 && !FAULT && S.beds[capK].hard >= .6 && R() < (F.bridge.chance ?? 1)) {
    // (not where the side stream comes in)
    const sb = lerp(sFall, sCross, (trib ? .55 : .35) + R() * .3), [c0, c1] = atS(pts, cum, sb), [d0, d1] = atS(pts, cum, sb + 1), [cx, cy] = toXY(c0, c1), [ex, ey] = toXY(d0, d1);
    const dl = Math.hypot(ex - cx, ey - cy) || 1, al = [(ex - cx) / dl, (ey - cy) / dl], ac = [-al[1], al[0]], gw = gorgeW(sb) / 2;
    const zs = profAt(sb) + chanD + 1, zTop = upAt(cx, cy, c0) - .3;   // (its deck the cap's top, as the upland's)
    const w = 5 + R() * 5, crown = zTop - Math.max(2.5, S.beds[capK].t * .7), half = gw + 9;
    if (crown - zs > 3) {
      const why = S.beds[capK].karst ? `the roof of a cave the stream ran in, left when the rest fell` : S.beds[capK].columns ? `the roof of a lava tube the stream found` : `where the stream cut through a meander's neck under the ${S.beds[capK].name}`;
      caves.push({ kind: "bridge", parts: [{ a: [cx - ac[0] * half, cy - ac[1] * half, zs], b: [cx + ac[0] * half, cy + ac[1] * half, zTop], r: w }], floor: zs - 2, mouth: [cx, cy], out: al,
        span: { c: [cx, cy], u: c0, al, ac, w, zTop, zs, rise: crown - zs, halfSpan: gw + 1.5, half }, why: `a natural bridge ${Math.round(gw * 2 + 3)} m across, ${Math.round(crown - zs + 1)} m over the stream: ${why}` });
    }
  }
  })();
  // each cave's volume: a box round it (and down to the ground's lowest in it), sampled every half metre
  const VS = .5;
  (() => {
  for (const c of caves) {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, z0 = c.floor - 1, z1 = -Infinity;
    for (const p of c.parts) for (const e of [p.a, p.b]) { x0 = Math.min(x0, e[0] - p.r - 2); y0 = Math.min(y0, e[1] - p.r - 2); x1 = Math.max(x1, e[0] + p.r + 2); y1 = Math.max(y1, e[1] + p.r + 2); }
    x0 = Math.max(1, Math.floor(x0)); y0 = Math.max(1, Math.floor(y0)); x1 = Math.min(size - 2, Math.ceil(x1)); y1 = Math.min(size - 2, Math.ceil(y1));
    for (let y = y0; y <= y1; y += dx) for (let x = x0; x <= x1; x += dx) { const h = hLin(x, y); z0 = Math.min(z0, h - 1.5); z1 = Math.max(z1, h + 1); }
    if (c.span) z1 = Math.max(z1, c.span.zTop + 2);
    z0 = Math.floor(z0); z1 = Math.ceil(z1);
    const nx = Math.round((x1 - x0) / VS) + 1, ny = Math.round((y1 - y0) / VS) + 1, nz = Math.round((z1 - z0) / VS) + 1, f = new Float32Array(nx * ny * nz);
    const HB = new Float32Array(nx * ny); for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) HB[j * nx + i] = hLin(x0 + i * VS, y0 + j * VS);
    const UB = c.span ? new Float32Array(nx * ny) : null;   // (a bridge's deck: the cap's top, per column)
    if (UB) for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) UB[j * nx + i] = upAt(x0 + i * VS, y0 + j * VS, c.span.u) - .3;
    const wob = (x, y, z) => .35 * noise(x / 2.1 + z * .3, y / 2.1 - z * .2, seed + 91);   // (the walls not smooth)
    for (let k = 0; k < nz; k++) for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
      const x = x0 + i * VS, y = y0 + j * VS, z = z0 + k * VS;
      if (c.span) {   // (the bridge: a slab, ragged, its underside an arch over the gorge -- solid where > 0)
        const B = c.span, s = (x - B.c[0]) * B.al[0] + (y - B.c[1]) * B.al[1], e = (x - B.c[0]) * B.ac[0] + (y - B.c[1]) * B.ac[1];
        const under = Math.abs(e) < B.halfSpan ? B.zs + B.rise * Math.sqrt(1 - (e / B.halfSpan) ** 2) : -Infinity, rag = wob(x, y, z);
        const g = Math.min(B.w / 2 * (1 + .25 * noise(e / 4, z / 3, seed + 93)) - Math.abs(s), UB[j * nx + i] - z + rag * .5, z - under + rag, B.half - Math.abs(e));
        f[i + nx * (j + ny * k)] = Math.max(HB[j * nx + i] - z, g);
        continue;
      }
      let d = Infinity;
      for (const p of c.parts) {
        const [ax, ay, az] = p.a, bx = p.b[0] - ax, by = p.b[1] - ay, bz = p.b[2] - az, L2 = bx * bx + by * by + bz * bz;
        const t = L2 ? clamp(((x - ax) * bx + (y - ay) * by + (z - az) * bz) / L2, 0, 1) : 0;
        const qx = (x - ax - bx * t) / p.r, qy = (y - ay - by * t) / p.r, qz = (z - az - bz * t) / p.rz;
        d = Math.min(d, (Math.hypot(qx, qy, qz) - 1) * Math.min(p.r, p.rz));
      }
      d = Math.max(d + wob(x, y, z), c.floor - z);   // (what has settled in it: the floor)
      f[i + nx * (j + ny * k)] = Math.min(HB[j * nx + i] - z, d);
    }
    const { pos, idx } = surfaceNets(f, nx, ny, nz);
    for (let q = 0; q < pos.length; q += 3) { pos[q] = x0 + pos[q] * VS; pos[q + 1] = y0 + pos[q + 1] * VS; pos[q + 2] = z0 + pos[q + 2] * VS; }
    // each vertex's bed, and how far in the dark it is (under rock, from the mouth)
    const vb = new Uint8Array(pos.length / 3), shade = new Float32Array(pos.length / 3);
    for (let q = 0; q < vb.length; q++) { const x = pos[q * 3], y = pos[q * 3 + 1], z = pos[q * 3 + 2];
      vb[q] = S.bedAt(x, y, z - .05); shade[q] = c.span ? (hLin(x, y) < z - 1 && z < c.span.zs + c.span.rise + 1 ? .7 : 1) : hLin(x, y) - z > 1 ? .3 + .7 * Math.exp(-Math.hypot(x - c.mouth[0], y - c.mouth[1]) / 7) : 1; }
    // the ground's cells under the patch, left out
    for (let j = Math.ceil(y0 / dx + .5); (j + 1) * dx <= y1 - .5; j++) for (let i = Math.ceil(x0 / dx + .5); (i + 1) * dx <= x1 - .5; i++) cut[j * N + i] = 1;
    Object.assign(c, { pos: new Float32Array(pos), idx: new Uint32Array(idx), bed: vb, shade, box: [x0, y0, z0, x1, y1, z1], cells: f.length });
    notes.push(`${c.kind === "bridge" ? "bridge" : "cave"}: ${c.why} (${c.cells} samples, ${idx.length / 3} triangles)`);
  }
  // (the sea in under a sea cave's, an arch's roof: the cells under its opening down to its floor -- `flooded`: each
  // one's ground before, which DRESS reads its slope from: the patch draws that ground, and it is not a cliff's edge)
  for (const c of caves) if (c.flood) for (let k = 0; k < n; k++) { if (!cut[k]) continue;
    const x = (k % N) * dx, y = ((k / N) | 0) * dx, z = c.floor + 1;
    if (c.parts.some((p) => { const [ax, ay, az] = p.a, bx = p.b[0] - ax, by = p.b[1] - ay, bz = p.b[2] - az, L2 = bx * bx + by * by + bz * bz, t = clamp(((x - ax) * bx + (y - ay) * by + (z - az) * bz) / L2, 0, 1);
      return Math.hypot((x - ax - bx * t) / p.r, (y - ay - by * t) / p.r, (z - az - bz * t) / p.rz) < 1; })) { if (H[k] > c.floor) flooded.push(k, H[k]); H[k] = rock[k] = c.floor; soil[k] = 0; carved[k] = 1; } }
  })();
  mark("caves");
  Object.assign(c, { VS, half });
}
