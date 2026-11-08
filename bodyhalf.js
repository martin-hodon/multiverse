// HALF-DRAWN BODIES (2026-11-08, bodies.js `?halfdraw=1`): a mirror-symmetric body (bodymesh.js buildBody: its surface
// meshed as its +z half and reflected -- each such LOD says where its half is, `L.half`) sent to the GPU as that half
// only, drawn twice: once as it is, once reflected. Pure: no three.js (tested in Node).
//
// The reflected draw is a second SkinnedMesh over the same buffers whose world matrix and bind matrix are both
// M = diag(1, 1, -1): three skins  M^-1 * sum_k w_k B_{s_k} * M v  and places it by M, so a vertex lands at
// sum_k w_k B_{s_k} (M v) -- the reflected vertex skinned by the bones s_k. Those must be the TWINS of the half's own
// (the left foreleg's for the right's), so the reflected draw has its own skinIndex: each bone's twin. A world matrix
// with a negative determinant makes three flip the front face (its WebGPU pipeline: frontFace CW), and the normals
// come out reflected by the same matrices, so nothing is lit inside out.
//   The MIDLINE's vertices are drawn by both and must land on the same spot to the bit (or the seam along the back
//   sparkles): their weights are made symmetric (a bone and its twin the same weight, the pair kept whole in the four
//   slots) and the reflected draw takes the SAME slots -- the twin set is the set itself, in the same order, so the
//   sums are the same sums.
//   The PAINT of the far side: its own vertex colour (the mottle is not mirrored), and its pattern coordinates the
//   near side's with the across axis turned over (bodies.js, in the material): a twin shape's frame is its twin's
//   reflected -- (u, v, w) -> (Mu, Mv, -Mw) for every frame bodymesh.js lays (a shape's own, the animal's, the rest
//   pose's) -- so a point's coordinates in it are (a, b, -c): the far side's stripes are its own, not a mirror copy.
//   The eyes, the details and the coat are drawn once, by the near draw (they are not halved).

// the twin of each bone, from the mesh itself: where a vertex of the half is weighted to bone b, its reflection is
// weighted to twin(b) about as much (votes by weight); a bone with no say is its own twin (the midline's bones)
export function boneTwins(L, nb) {
  const { n, twin } = L.half, si = L.skinIndex, sw = L.skinWeight, vote = new Float64Array(nb * nb);
  for (let v = 0; v < n; v++) {
    const u = twin[v];
    if (u === v) continue;
    for (let k = 0; k < 4; k++) {
      const w = sw[4 * v + k];
      if (w < .05) continue;
      let best = -1, bd = .15;
      for (let j = 0; j < 4; j++) { const d = Math.abs(sw[4 * u + j] - w); if (d < bd) { bd = d; best = j; } }
      if (best >= 0) { const x = si[4 * v + k], y = si[4 * u + best]; vote[x * nb + y] += w; if (y !== x) vote[y * nb + x] += w; }   // (the reflections' bones are the half's twins, and theirs the half's)
    }
  }
  const T = Int32Array.from({ length: nb }, (_, b) => b);
  for (let b = 0; b < nb; b++) {
    let best = b, bv = 0;
    for (let c = 0; c < nb; c++) if (vote[b * nb + c] > bv) { bv = vote[b * nb + c]; best = c; }
    T[b] = best;
  }
  // (a twin must be mutual: one that is not is a bone the mesh could not tell -- its own)
  for (let b = 0; b < nb; b++) if (T[T[b]] !== b) T[b] = b;
  return T;
}

// a LOD's arrays as the half: { L (the half + the eyes, details and coat: the near draw), col and skinIndex of the
// reflected draw, t (its triangles: the first t of L's), twin (the bones'), err (how far the reflected draw's skin is
// from what the whole mesh had at its reflections: the largest and the mean difference in weight, 0..2) } -- or null
export function halfOf(L, nb, twinB = null) {
  if (!L.half) return null;
  const { n, t, twin } = L.half, nv = twin.length, T = twinB ?? boneTwins(L, nb);
  const V = L.pos.length / 3, drop = nv - n, out = {};
  // (the vertices: the half's, then the extras (eyes, details, coat), the reflections left out)
  for (const [key, x] of Object.entries(L)) {
    if (!ArrayBuffer.isView(x) || key === "index") continue;
    const k = x.length / V, a = new x.constructor((V - drop) * k);
    a.set(x.subarray(0, n * k), 0); a.set(x.subarray(nv * k), n * k);
    out[key] = a;
  }
  const I = L.index, nt = I.length / 3, idx = new Uint32Array((nt - t) * 3);
  idx.set(I.subarray(0, 3 * t), 0);
  for (let i = 6 * t; i < I.length; i++) idx[i - 3 * t] = I[i] - drop;
  out.index = idx;
  const si = out.skinIndex, sw = out.skinWeight;
  // (the midline's weights made symmetric: a bone and its twin each the mean of the two, the pairs kept whole)
  const w = new Float64Array(nb);
  for (let v = 0; v < n; v++) {
    if (twin[v] !== v) continue;
    w.fill(0);
    for (let k = 0; k < 4; k++) w[si[4 * v + k]] += sw[4 * v + k];
    const groups = [];
    for (let b = 0; b < nb; b++) {
      const c = T[b];
      if (c < b) continue;
      const m = c === b ? w[b] : (w[b] + w[c]) / 2;
      if (m > 0) groups.push(c === b ? [m, b] : [m, b, c]);
    }
    groups.sort((x, y) => y[0] - x[0]);
    const slots = [];
    for (const g of groups) if (slots.length + g.length - 1 <= 4) for (const b of g.slice(1)) slots.push([b, g[0]]);
    const s = slots.reduce((a, q) => a + q[1], 0) || 1;
    for (let k = 0; k < 4; k++) { si[4 * v + k] = slots[k]?.[0] ?? 0; sw[4 * v + k] = slots[k] ? slots[k][1] / s : 0; }
  }
  // the reflected draw's own: each vertex's colour where its reflection really is, and its bones' twins (the midline's
  // its own, in its own order)
  const col = new Float32Array(n * 3), sk = new Uint16Array(n * 4);
  let eMax = 0, eSum = 0, eN = 0;
  const a = new Float64Array(nb);
  for (let v = 0; v < n; v++) {
    const u = twin[v];
    col.set(L.col.subarray(3 * u, 3 * u + 3), 3 * v);
    for (let k = 0; k < 4; k++) sk[4 * v + k] = u === v ? si[4 * v + k] : T[si[4 * v + k]];
    if (u === v) continue;
    a.fill(0);
    for (let k = 0; k < 4; k++) { a[sk[4 * v + k]] += sw[4 * v + k]; a[L.skinIndex[4 * u + k]] -= L.skinWeight[4 * u + k]; }
    let e = 0;
    for (let b = 0; b < nb; b++) e += Math.abs(a[b]);
    eMax = Math.max(eMax, e); eSum += e; eN++;
  }
  return { L: out, col, skinIndex: sk, n, t, twin: T, err: [eMax, eN ? eSum / eN : 0] };
}
