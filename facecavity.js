// A FACE'S HOLLOWS AND SMOOTHED NORMALS as plain arrays (heads.js cavityOf, smoothNormals: the sums, moved here
// 2026-11-22 unchanged, so the far heads' worker -- faceworker.js, no three.js -- works them out off the main thread
// too), and the arrays tools.js paintedGeometry lays a built face out in (each group's triangles' corners in order),
// which they are worked out over.
//   P positions, N normals (3 a vertex), hm the hair's mask, wm the wet mask (1 a vertex, or undefined)

// SMOOTHED NORMALS (heads.js smoothNormals: what they are, and why): the new normals, 3 a vertex
export function smoothArrays(P, N, hm, wm, C) {
  const n = P.length / 3;
  // the surface's own points, once each (the geometry repeats a vertex in every triangle it is in: cavityOf's keys), each
  // with its own normal and kind -- and how many copies it stands for, its weight: the same sums as over every copy, with
  // a sixth of the points and a thirty-sixth of the pairs (2026-11-03: over every copy, 73 s of a Greek world's start)
  const uniq = new Map(), of = new Int32Array(n).fill(-1), U = [], W = [];
  for (let i = 0; i < n; i++) {
    if (hm?.[i]) continue;
    const k = (Math.round(P[i * 3] * 2e4) + 8192) + (Math.round(P[i * 3 + 1] * 2e4) + 8192) * 16384 + (Math.round(P[i * 3 + 2] * 2e4) + 8192) * 268435456;
    let l = uniq.get(k); if (!l) uniq.set(k, l = []);
    let u = -1;
    for (const q of l) { const j = U[q]; if (N[j * 3] === N[i * 3] && N[j * 3 + 1] === N[i * 3 + 1] && N[j * 3 + 2] === N[i * 3 + 2] && !!wm?.[j] === !!wm?.[i]) { u = q; break; } }
    if (u < 0) { u = U.length; U.push(i); W.push(0); l.push(u); }
    W[u]++; of[i] = u;
  }
  const R = C.r, cell = new Map(), ck = (a, b, c) => (a + 512) + (b + 512) * 1024 + (c + 512) * 1048576, out = new Float32Array(N), su = new Float32Array(U.length * 3), ok = new Uint8Array(U.length);
  for (let u = 0; u < U.length; u++) {
    const i = U[u], k = ck(Math.floor(P[i * 3] / R), Math.floor(P[i * 3 + 1] / R), Math.floor(P[i * 3 + 2] / R)); let l = cell.get(k); if (!l) cell.set(k, l = []); l.push(u);
  }
  for (let u = 0; u < U.length; u++) {
    const i = U[u], x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], nx = N[i * 3], ny = N[i * 3 + 1], nz = N[i * 3 + 2], wet = !!wm?.[i];
    const cx = Math.floor(x / R), cy = Math.floor(y / R), cz = Math.floor(z / R);
    let sx = 0, sy = 0, sz = 0;
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
      const l = cell.get(ck(cx + a, cy + b, cz + c));
      if (l) for (const q of l) {
        const j = U[q];
        if (!!wm?.[j] !== wet) continue;
        const mx = N[j * 3], my = N[j * 3 + 1], mz = N[j * 3 + 2];
        if (mx * nx + my * ny + mz * nz < C.cos) continue;
        const d = Math.hypot(P[j * 3] - x, P[j * 3 + 1] - y, P[j * 3 + 2] - z);
        if (d < R) { const w = (1 - d / R) * W[q]; sx += mx * w; sy += my * w; sz += mz * w; }
      }
    }
    const L = Math.hypot(sx, sy, sz);
    if (L > 1e-9) { su[u * 3] = sx / L; su[u * 3 + 1] = sy / L; su[u * 3 + 2] = sz / L; ok[u] = 1; }
  }
  for (let i = 0; i < n; i++) { const u = of[i]; if (u >= 0 && ok[u]) { out[i * 3] = su[u * 3]; out[i * 3 + 1] = su[u * 3 + 1]; out[i * 3 + 2] = su[u * 3 + 2]; } }
  return out;
}

// THE HOLLOWS (heads.js cavityOf, cavityShade): how dark each vertex is, 1 a vertex
export function cavityArrays(P, N, hm, C) {
  const n = P.length / 3;
  // the surface's own points, once each (the geometry repeats a vertex in every triangle it is in): numeric keys, a
  // twentieth of a millimetre
  const uniq = new Map(), of = new Int32Array(n), U = [];
  for (let i = 0; i < n; i++) {
    if (hm?.[i]) { of[i] = -1; continue; }   // (not the hair: its strands are dense, and costly, and the sheen shades them)
    const k = (Math.round(P[i * 3] * 2e4) + 8192) + (Math.round(P[i * 3 + 1] * 2e4) + 8192) * 16384 + (Math.round(P[i * 3 + 2] * 2e4) + 8192) * 268435456;
    let u = uniq.get(k); if (u === undefined) { uniq.set(k, u = U.length); U.push(i); } of[i] = u;
  }
  const R = Math.max(...C.r), cell = new Map(), ck = (a, b, c) => (a + 512) + (b + 512) * 1024 + (c + 512) * 1048576;
  for (const i of U) { const k = ck(Math.floor(P[i * 3] / R), Math.floor(P[i * 3 + 1] / R), Math.floor(P[i * 3 + 2] / R)); let l = cell.get(k); if (!l) cell.set(k, l = []); l.push(i); }
  const [r0, r1] = C.r, [k0, k1] = C.k, du = new Float32Array(U.length);
  for (let u = 0; u < U.length; u++) {
    const i = U[u], x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], cx = Math.floor(x / R), cy = Math.floor(y / R), cz = Math.floor(z / R);
    let ax = 0, ay = 0, az = 0, aw = 0, bx = 0, by = 0, bz = 0, bw = 0;
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
      const l = cell.get(ck(cx + a, cy + b, cz + c));
      if (l) for (const j of l) {
        const dx = P[j * 3] - x, dy = P[j * 3 + 1] - y, dz = P[j * 3 + 2] - z, d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (d < r0) { const w = 1 - d / r0; ax += dx * w; ay += dy * w; az += dz * w; aw += w; }
        if (d < r1) { const w = 1 - d / r1; bx += dx * w; by += dy * w; bz += dz * w; bw += w; }
      }
    }
    const nx = N[i * 3], ny = N[i * 3 + 1], nz = N[i * 3 + 2];
    const v = (aw > 0 ? k0 * Math.max(0, (ax * nx + ay * ny + az * nz) / aw / r0) : 0) + (bw > 0 ? k1 * Math.max(0, (bx * nx + by * ny + bz * nz) / bw / r1) : 0);
    du[u] = Math.min(C.max, v);
  }
  const dark = new Float32Array(n);
  for (let i = 0; i < n; i++) dark[i] = of[i] < 0 ? 0 : du[of[i]];
  return dark;
}

// paintedGeometry's layout of a built face, without three.js and without the colours: positions, normals, the hair's
// mask (`strands`: the roles drawn as hair) and the wet mask (`wet`: { role: how wet }) -- the same arrays, in the
// same order, as tools.js paintedGeometry(built, { strands, wet }) gives (faceworker.js; checked identical)
export function faceArrays(built, { strands = ["hair"], wet = null } = {}) {
  let n = 0;
  for (const g of built.groups) n += g.idx.length;
  const P = new Float32Array(n * 3), N = new Float32Array(n * 3), hm = new Float32Array(n), wm = wet ? new Float32Array(n) : undefined;
  let o = 0;
  for (const g of built.groups) {
    const I = g.idx, Pg = g.pos, Ng = g.nor, hairy = strands.some((r) => g.roles?.has(r));
    const wv = wet ? Math.max(0, ...[...(g.roles ?? [])].map((r) => wet[r] ?? 0)) : 0;
    for (let i = 0; i < I.length; i++, o++) {
      const a = I[i] * 3;
      P[o * 3] = Pg[a]; P[o * 3 + 1] = Pg[a + 1]; P[o * 3 + 2] = Pg[a + 2];
      N[o * 3] = Ng[a]; N[o * 3 + 1] = Ng[a + 1]; N[o * 3 + 2] = Ng[a + 2];
      hm[o] = hairy ? 1 : 0;
      if (wm) wm[o] = wv;
    }
  }
  return { P, N, hm, wm };
}
