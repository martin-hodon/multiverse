// MOSAIC, the laying (docs/mosaic.md): every texel of the map goes to one stone, in the order a mosaicist sets them. Lines first, one
// stone wide however thin they are. Then the rows hugging each region's edge (the andamento): each stone runs along its
// isoline from where the last stopped to its own far end, and between isolines across, so stones can't leave holes. Then
// the field: straight rows across the whole tile, a map of (row, column) wrapping with it. Grout is what's left where two
// stones meet (`mortar`): a width of joint, not a gap between rectangles.
//   Texels are the map's, and every write is modulo the tile when it repeats, so a seam can't form.

const rngOf = (seed) => () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const hash2 = (a, b, s) => { let h = Math.imul(a * 31 + b ^ s, 2654435761); h ^= h >>> 15; h = Math.imul(h, 2246822519); return ((h ^ (h >>> 13)) >>> 0) / 4294967296; };
const TAU = Math.PI * 2;

export function layStones(map, L, ppm) {
  const { W, H, wrap, idx, id, dist } = map, n = W * H, rnd = rngOf(L.seed ?? 1), seed = L.seed ?? 1;
  const asked = (L.stone ?? .012) * ppm, pitch0 = wrap ? H / Math.max(1, Math.round(H / asked)) : asked;   // (whole rows up the tile, when it repeats)
  const aspect = L.aspect ?? 1.15, [jL] = L.jitter ?? [.3], turn = (L.wobble ?? 5) * Math.PI / 180, fine = L.fine ?? {}, pitchFor = (s) => pitch0 * (fine[s] ?? 1);
  const cover = new Int32Array(n), st = { x: [], y: [], slot: [], row: [], kind: [], area: [] };
  const at = (x, y) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= W || y >= H) { if (!wrap) return -1; x = ((x % W) + W) % W; y = ((y % H) + H) % H; } return y * W + x; };
  const stone = (x, y, slot, row, kind) => { st.x.push(x); st.y.push(y); st.slot.push(slot); st.row.push(row); st.kind.push(kind); st.area.push(0); return st.x.length; };

  // A STONE'S CLAIM: free texels of its region in a rectangle reaching `front` ahead and `back` behind. Behind it the last stone
  // has already claimed: so `back` is generous and what's taken stops it. A line's stone (`any`) may lie over its neighbours.
  let hits = new Int32Array(4096);
  const claim = (x, y, a, front, back, hw, target, slot, row, kind, any, lo, hi, min) => {
    const c = Math.cos(a), s = Math.sin(a), R = Math.ceil(Math.hypot(Math.max(front, back), hw)) + 1, cx = Math.round(x), cy = Math.round(y);
    if ((2 * R + 1) ** 2 > hits.length) hits = new Int32Array((2 * R + 1) ** 2);
    const inside = cx - R >= 0 && cy - R >= 0 && cx + R < W && cy + R < H; let got = 0;
    for (let v = -R; v <= R; v++) {
      const Y = cy + v - y; let u0 = -R, u1 = R;   // (the rectangle's run along this row, a texel over)
      if (Math.abs(c) > .01) { const p = (-back - Y * s) / c, q = (front - Y * s) / c, o = cx - x; u0 = Math.max(u0, Math.floor(Math.min(p, q) - o) - 1); u1 = Math.min(u1, Math.ceil(Math.max(p, q) - o) + 1); }
      if (Math.abs(s) > .01) { const p = (Y * c - hw) / s, q = (Y * c + hw) / s, o = cx - x; u0 = Math.max(u0, Math.floor(Math.min(p, q) - o) - 1); u1 = Math.min(u1, Math.ceil(Math.max(p, q) - o) + 1); }
      for (let u = u0; u <= u1; u++) {
        const X = cx + u - x, a1 = X * c + Y * s; if (a1 > front || a1 < -back) continue;
        const b1 = -X * s + Y * c; if (b1 > hw || b1 < -hw) continue;
        const i = inside ? (cy + v) * W + cx + u : at(cx + u, cy + v);
        if (i < 0 || cover[i] !== 0 || (!any && id[i] !== target)) continue;
        if (dist[i] < lo || dist[i] > hi) continue;
        hits[got++] = i;
      }
    }
    if (got < Math.max(1, (front + Math.min(back, front)) * 2 * hw * min)) return false;
    const k = stone(x, y, slot, row, kind);
    for (let q = 0; q < got; q++) cover[hits[q]] = k;
    st.area[k - 1] = got;
    return true;
  };

  // the isoline's way at a point, across the distance's slope
  const d = (X, Y) => { const i = at(X, Y); return i < 0 ? 0 : Math.min(dist[i], 1e4); };
  const grad = (x, y) => {
    const r = 2, gx = d(x + r, y) - d(x - r, y), gy = d(x, y + r) - d(x, y - r), m = Math.hypot(gx, gy) || 1;
    return [gx / m, gy / m, m / (2 * r)];
  };

  const edged = map.count > 1 || !wrap;
  // LINES: a texel is thin if no disc about a stone across fits round it inside its region. They're walked along their ridge.
  const thin = new Uint8Array(n);
  if (edged) {
    const coreR = pitch0 * (L.thin ?? .6), reach = new Float32Array(n).fill(-1), q1 = [], q2 = [];
    // (deep inside a core everything round it is core too: nothing to spread to, so only those near its edge start. Two queues, a straight step's and a diagonal's, each in order of reach: the furthest reach first, so a texel is rarely gone over twice)
    for (let i = 0; i < n; i++) if (dist[i] >= coreR) { reach[i] = coreR; if (dist[i] < coreR + 2) q1.push(i); }
    const dd = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, 1.414], [1, -1, 1.414], [-1, 1, 1.414], [-1, -1, 1.414]];
    const ax8 = dd.map((d) => d[0]), ay8 = dd.map((d) => d[1]), cost8 = dd.map((d) => d[2]), step8 = dd.map((d) => d[1] * W + d[0]);
    let h1 = 0, h2 = 0; const v1 = [], v2 = []; for (let k = 0; k < q1.length; k++) v1.push(coreR);
    while (h1 < q1.length || h2 < q2.length) {
      const one = h2 >= q2.length || (h1 < q1.length && v1[h1] >= v2[h2]), i = one ? q1[h1] : q2[h2], at0 = one ? v1[h1++] : v2[h2++];
      if (reach[i] !== at0 && Math.abs(reach[i] - at0) > 1e-3 && reach[i] > at0) continue;   // (it's been reached better since)
      const x = i % W, y = (i - x) / W, own = id[i], inner = x > 0 && y > 0 && x < W - 1 && y < H - 1, base = reach[i];
      for (let k = 0; k < 8; k++) {
        const j = inner ? i + step8[k] : at(x + ax8[k], y + ay8[k]);
        if (j < 0 || id[j] !== own) continue;
        const r = base - cost8[k];
        if (r > reach[j]) { reach[j] = r; if (r > 0) { if (k < 4) { q1.push(j); v1.push(r); } else { q2.push(j); v2.push(r); } } }
      }
    }
    for (let i = 0; i < n; i++) if (reach[i] < 0) thin[i] = 1;
    // (a corner a disc can't turn is thin too, but it's no line: a line is a run of more than a couple of stones' area)
    const seen = new Uint8Array(n), least = 2 * pitch0 * pitch0 * aspect;
    for (let s = 0; s < n; s++) {
      if (!thin[s] || seen[s]) continue;
      const run = [s]; seen[s] = 1;
      for (let h = 0; h < run.length; h++) {
        const x = run[h] % W, y = (run[h] - x) / W;
        const inner = x > 0 && y > 0 && x < W - 1 && y < H - 1, i0 = run[h];
        for (let k = 0; k < 8; k++) { const j = inner ? i0 + step8[k] : at(x + ax8[k], y + ay8[k]); if (j >= 0 && thin[j] && !seen[j] && id[j] === id[s]) { seen[j] = 1; run.push(j); } }
      }
      if (run.length < least) for (const i of run) thin[i] = 0;
    }
    const axisAt = (x, y, target, R) => {   // (its way at a point: the spread of its texels around)
      let xx = 0, yy = 0, xy = 0, mx = 0, my = 0, c = 0;
      for (let v = -R; v <= R; v++) for (let u = -R; u <= R; u++) {
        if (u * u + v * v > R * R) continue;
        const X = x + u, Y = y + v, i = X >= 0 && Y >= 0 && X < W && Y < H ? Y * W + X : at(X, Y);
        if (i >= 0 && id[i] === target && thin[i]) { mx += u; my += v; c++; xx += u * u; yy += v * v; xy += u * v; }
      }
      if (c < 2) return null;
      xx -= mx * mx / c; yy -= my * my / c; xy -= mx * my / c;
      return .5 * Math.atan2(2 * xy, xx - yy);
    };
    const ridge = (x, y, target, R) => {   // (the deepest free thin texel near a point)
      let best = null, bd = -1;
      for (let v = -R; v <= R; v++) for (let u = -R; u <= R; u++) {
        const X = x + u, Y = y + v, i = X >= 0 && Y >= 0 && X < W && Y < H ? Y * W + X : at(X, Y);
        if (i < 0 || id[i] !== target || !thin[i] || cover[i]) continue;
        const d = dist[i] - .05 * Math.hypot(u, v);
        if (d > bd) { bd = d; best = [x + u, y + v]; }
      }
      return best;
    };
    // (deepest first, then in order: thin texels have few depths among them, so by depth, not by a sort of them all)
    const byDepth = new Map();
    for (let i = 0; i < n; i++) if (thin[i]) { const D = dist[i]; let list = byDepth.get(D); if (!list) byDepth.set(D, list = []); list.push(i); }
    const depths = [...byDepth.keys()].sort((a, b) => b - a);
    for (const D of depths) for (const s of byDepth.get(D)) {
      if (cover[s]) continue;
      const target = id[s], slot = idx[s], pitch = pitchFor(slot), len = pitch * aspect, x0 = s % W, y0 = (s - x0) / W, R = Math.ceil(pitch * .9);
      const place = (x, y, a) => claim(x, y, a, len * (.5 + jL * .5 * (rnd() - .5)), len * .55, Math.max(dist[at(x, y)] + .5, pitch * (L.thread ?? .36)), target, slot, 0, 1, true, -Infinity, Infinity, .08);
      const a0 = axisAt(x0, y0, target, R) ?? 0;
      if (!place(x0, y0, a0)) { const k = stone(x0, y0, slot, 0, 1); cover[s] = k; st.area[k - 1] = 1; continue; }
      for (const dir of [0, Math.PI]) {
        let x = x0, y = y0, a = a0 + dir;
        for (let step = 0; step < 4000; step++) {
          const p = ridge(Math.round(x + Math.cos(a) * len), Math.round(y + Math.sin(a) * len), target, Math.ceil(len * .6));
          if (!p) break;
          let a2 = axisAt(p[0], p[1], target, R) ?? a;
          if (Math.cos(a2 - Math.atan2(p[1] - y, p[0] - x)) < 0) a2 += Math.PI;
          a = a2; x = p[0]; y = p[1];
          if (!place(x, y, a)) break;
        }
      }
    }
  }

  // THE ANDAMENTO: rows along an isoline at distance t, from a start both ways round, each step set back onto the line
  const halo = L.halo ?? 1, flows = new Set(L.flow ?? []);
  const rowFrom = (t, band, r, s) => {
    const target = id[s], slot = idx[s], pitch = pitchFor(slot), len = () => pitch * aspect * (1 + jL * (rnd() - .5)), hw = pitch * .9;
    const put = (x, y, a, l) => claim(x, y, a + turn * (rnd() - .5), l, l * 1.1, hw, target, slot, r, 2, false, band[0], band[1], .3);
    const x0 = s % W, y0 = (s - x0) / W, g0 = grad(x0, y0), a0 = Math.atan2(g0[0], -g0[1]);
    if (!put(x0, y0, a0, len() / 2)) return;
    for (const sign of [1, -1]) {
      let x = x0, y = y0, tx = -g0[1] * sign, ty = g0[0] * sign, misses = 0;
      for (let step = 0; step < 6000; step++) {
        const l = len();
        let nx = x + tx * l, ny = y + ty * l;
        for (let k = 0; k < 2; k++) { const i = at(nx, ny); if (i < 0) break; const g = grad(nx, ny); nx += g[0] * (t - dist[i]); ny += g[1] * (t - dist[i]); }
        const i = at(nx, ny);
        if (i < 0 || id[i] !== target || Math.abs(dist[i] - t) > pitch * .7) break;
        const g = grad(nx, ny);
        let qx = -g[1], qy = g[0]; if (qx * tx + qy * ty < 0) { qx = -qx; qy = -qy; }
        if (!put(nx, ny, Math.atan2(qy, qx), l / 2) && ++misses > 1) break;
        x = nx; y = ny; tx = qx; ty = qy;
      }
    }
  };
  if (edged) {
    let maxD = 0; for (let i = 0; i < n; i++) if (dist[i] < 1e5 && dist[i] > maxD) maxD = dist[i];
    const rows = Math.ceil(maxD / Math.min(...Object.values(fine), 1) / pitch0);
    // (which texels might start which row, once: looking through the whole map for each row is most of a laying's time)
    const flowOf = new Uint8Array(256), pOf = new Float64Array(256), starts = Array.from({ length: rows }, () => []);
    for (let s = 0; s < 256; s++) { flowOf[s] = L.fill === "flow" || flows.has(s) ? 1 : 0; pOf[s] = pitchFor(s); }
    for (let i = 0; i < n; i++) {
      if (cover[i] || thin[i]) continue;
      const s = idx[i], p = pOf[s], D = dist[i], top = flowOf[s] ? rows - 1 : Math.min(rows - 1, halo - 1);
      if (D > 1e5) continue;
      const lo = Math.max(0, Math.floor((D - .75) / p - .5) - 1), hi = Math.min(top, Math.ceil((D + .75) / p - .5) + 1);
      for (let r = lo; r <= hi; r++) if (Math.abs(D - (r + .5) * p) <= .75) starts[r].push(i);
    }
    for (let r = 0; r < rows; r++) {
      let any = false; const list = starts[r];
      for (let q = 0; q < list.length; q++) {
        const i = list[q];
        if (cover[i]) continue;
        const p = pOf[idx[i]];
        any = true;
        rowFrom((r + .5) * p, [r * p, (r + 1) * p], r, i);
      }
      starts[r] = null;
      if (!any && r >= halo) break;
    }
  }

  // THE FIELD: rows and columns as a map of the point. Rows wander together (a sine of whole turns: it wraps); each row has its
  // own offset and its own joints, a little aslant
  const horiz = (L.lay ?? "x") === "x", span = horiz ? H : W, long = horiz ? W : H, nRows = Math.max(1, Math.round(span / pitch0)), step = span / nRows;
  const count = Math.max(1, Math.round(long / (pitch0 * aspect))), stepL = long / count, wander = (L.wander ?? .14) * pitch0, wa = rnd() * TAU, wb = rnd() * TAU;
  const kept = new Map(), jit = (r, c) => jL * .5 * (hash2(((c % count) + count) % count, r, seed) - .5);
  const rowsAll = nRows + 4, off = new Float32Array(rowsAll), lean = new Float32Array(rowsAll), joints = new Float32Array(rowsAll * count);   // (a row's values, once: every texel asks)
  const rowOf = (r) => wrap ? ((r % nRows) + nRows) % nRows : r + 2;
  for (let r = 0; r < rowsAll; r++) { off[r] = hash2(r, 77, seed) * 3; lean[r] = .12 * (hash2(r, 5, seed) - .5); for (let c = 0; c < count; c++) joints[r * count + c] = jit(r, c); }
  // (a sine of u + v, from tables of u and of v: this runs for every texel)
  const wave = (fu, fv, ph) => {
    const su = Float64Array.from({ length: long }, (_, u) => Math.sin(TAU * fu * u / long + ph)), cu = Float64Array.from({ length: long }, (_, u) => Math.cos(TAU * fu * u / long + ph));
    const sv = Float64Array.from({ length: span }, (_, v) => Math.sin(TAU * fv * v / span)), cv = Float64Array.from({ length: span }, (_, v) => Math.cos(TAU * fv * v / span));
    return { su, cu, sv, cv };
  };
  const W0 = wave(1, 2, wa), W1 = wave(3, -5, wb), W2 = wave(7, 3, wa + wb), su0 = W0.su, cu0 = W0.cu, sv0 = W0.sv, cv0 = W0.cv, su1 = W1.su, cu1 = W1.cu, sv1 = W1.sv, cv1 = W1.cv, su2 = W2.su, cu2 = W2.cu, sv2 = W2.sv, cv2 = W2.cv;
  let lastKey = -1, lastK = 0;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x;
    if (cover[i]) continue;
    const u = horiz ? x : y, v = horiz ? y : x;
    const vw = v + wander * ((su0[u] * cv0[v] + cu0[u] * sv0[v]) + .6 * (su1[u] * cv1[v] + cu1[u] * sv1[v]) + .4 * (su2[u] * cv2[v] + cu2[u] * sv2[v]));
    const rf = vw / step, r = Math.floor(rf), q = Math.max(0, Math.min(rowsAll - 1, rowOf(r)));
    const uw = u / stepL + off[q] + (rf - r - .5) * lean[q];
    let c = Math.floor(uw), fr = uw - c;
    if (fr < joints[q * count + ((c % count) + count) % count]) c--; else if (fr - 1 > joints[q * count + (((c + 1) % count) + count) % count]) c++;
    const C = wrap ? ((c % count) + count) % count : c + 8, key = (q * 4096 + C) * 65536 + (id[i] & 65535);
    let k = lastK;
    if (key !== lastKey) {
      k = kept.get(key);
      if (k === undefined) { k = stone(x, y, idx[i], 99, 3); kept.set(key, k); }
      lastKey = key; lastK = k;
    }
    cover[i] = k; st.area[k - 1]++;
  }

  // scraps go to neighbouring stones of their colour, one ring at a time; a whole small region keeps its scrap
  const nominal = pitch0 * pitch0 * aspect, scrap = nominal * (L.scrap ?? .22), small = new Uint8Array(st.x.length + 1);
  for (let k = 1; k <= st.x.length; k++) small[k] = st.area[k - 1] < scrap * (fine[st.slot[k - 1]] ?? 1) ** 2 ? 1 : 0;
  for (let i = 0; i < n; i++) if (cover[i] && small[cover[i]]) { cover[i] = -cover[i]; }
  let todo = []; for (let i = 0; i < n; i++) if (cover[i] <= 0) todo.push(i);
  const NX = [1, -1, 0, 0], NY = [0, 0, 1, -1];
  for (let pass = 0; pass < 40 && todo.length; pass++) {
    const next = [], sets = [];
    for (const i of todo) {
      const x = i % W, y = (i - x) / W, own = st.slot[Math.abs(cover[i]) - 1]; let got = 0;
      for (let q = 0; q < 4; q++) { const j = at(x + NX[q], y + NY[q]); if (j >= 0 && cover[j] > 0 && st.slot[cover[j] - 1] === own) { got = cover[j]; break; } }
      if (got) sets.push(i, got); else next.push(i);
    }
    for (let k = 0; k < sets.length; k += 2) cover[sets[k]] = sets[k + 1];
    if (!sets.length) break;
    todo = next;
  }
  for (const i of todo) if (cover[i] < 0) cover[i] = -cover[i];   // (nothing beside it in its region: it's the region)

  // THE MORTAR: the joint between two stones, `joint` of a stone wide (at least a texel of the map). Odd widths lean one way.
  const wide = Math.max(1, Math.round((L.joint ?? .11) * pitch0)), reach = wide >> 1, offs = wide & 1 ? [[reach + 1, 0], [0, reach + 1]] : [];
  for (let v = -reach; v <= reach; v++) for (let u = -reach; u <= reach; u++) if ((u || v) && u * u + v * v <= reach * reach + .5) offs.push([u, v]);
  const mortar = new Uint8Array(n);
  const nOff = offs.length, ou = Int32Array.from(offs, (o) => o[0]), ov = Int32Array.from(offs, (o) => o[1]), hop = Int32Array.from(offs, (o) => o[1] * W + o[0]), rim = reach + 1;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x, c = cover[i];
    if (x >= rim && y >= rim && x < W - rim && y < H - rim) { for (let q = 0; q < nOff; q++) if (cover[i + hop[q]] !== c) { mortar[i] = 1; break; } continue; }
    for (let q = 0; q < nOff; q++) {
      let X = x + ou[q], Y = y + ov[q];
      if (X < 0 || Y < 0 || X >= W || Y >= H) { if (!wrap) continue; X = (X + W) % W; Y = (Y + H) % H; }
      if (cover[Y * W + X] !== c) { mortar[i] = 1; break; }
    }
  }
  return { cover, mortar, stones: st, pitch: pitch0, W, H };
}
