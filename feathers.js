// FEATHERS (2026-09-30): a fan of feathers as one primitive of the items language (items.js part type `feathers`) --
// the primaries and secondaries of a wing, the tail's fan, a crest -- each feather a flat vane of a few triangles,
// seen from both sides (items.js doubles the type), the fan laid in the part's x-z plane: +z out along the span,
// +x forward (the leading side), +y up off the sheet. Every feather is its own quill so a wing reads as a wing at a
// glance; the coverts over their roots are a plain plate in the wing definition (assets/items/components/wing).
//
//   roots: [[x, z], [x, z]]  the line the quills grow from, the first feather at the first point
//   n: how many        dir: [first, last]  degrees in the x-z plane, 0 pointing out along +z, 90 pointing back (-x)
//   length: [first, last]   width: [first, last] (the vane's whole width at its widest)
//   lead: +1 | -1  which side the narrow (leading) vane is on: +1 toward +x
//   droop: the tips' fall (m per m^2 along the quill: a curve down), lift: each next feather that much higher in y
//   (so they overlap and don't fight), band: the tip's share in the `tips` material (0: none)
//   shape: "pointed" | "rounded" | "square"  the tip
//   tuck: how much of each quill (x its length) runs on INWARD of its root, under the coverts (2026-10-04: from the
//   root itself a vane starts at nothing, and between every two of them a notch of nothing opened along the coverts'
//   edge -- the feathers did not join the wing; tucked, where the coverts end they are already wide and overlapping)
export function feathersGeometry(p, P, emitFor) {
  const n = Math.max(1, Math.round(p.n ?? 8)), [r0, r1] = p.roots ?? [[0, 0], [0, .1]];
  const [a0, a1] = p.dir ?? [60, 10], [L0, L1] = p.length ?? [.1, .1], [W0, W1] = p.width ?? [.02, .02];
  const lead = p.lead ?? 1, droop = p.droop ?? 0, tuck = p.tuck ?? 0, lift = p.lift ?? .0006, band = p.band ?? 0, shape = p.shape ?? "pointed";
  const vane = emitFor(p.material ?? "feather"), tips = band > 0 ? emitFor(p.tips ?? "tips") : null;
  // the vane's half widths along the quill (of the whole width): a leaf widest past the middle
  const PROF = [[0, 0], [.2, .55], [.5, .95], [.8, shape === "pointed" ? .7 : .95], [1, shape === "square" ? .6 : 0]];
  const wAt = (t) => { for (let i = 1; i < PROF.length; i++) if (t <= PROF[i][0]) { const [ta, wa] = PROF[i - 1], [tb, wb] = PROF[i]; return wa + (wb - wa) * (t - ta) / (tb - ta); } return 0; };
  const rows = band > 0 ? [0, .2, .5, 1 - band, 1] : [0, .2, .5, .8, 1];
  for (let i = 0; i < n; i++) {
    const f = n === 1 ? 0 : i / (n - 1);
    const a = (a0 + (a1 - a0) * f) * Math.PI / 180, L = L0 + (L1 - L0) * f, W = W0 + (W1 - W0) * f, y0 = lift * i;
    const rx = r0[0] + (r1[0] - r0[0]) * f, rz = r0[1] + (r1[1] - r0[1]) * f;
    const d = [-Math.sin(a), 0, Math.cos(a)], s = [lead * d[2], 0, -lead * d[0]];   // along the quill; across it toward the leading vane
    const ids = [];   // per row: [leadVert, trailVert] (one vert at the root and a pointed tip)
    for (let k = 0; k < rows.length; k++) {
      const t = rows[k], w = wAt(t) * W * (1 + tuck), tipRow = k === rows.length - 1 && shape !== "square";
      const u = (t * (1 + tuck) - tuck) * L, y = y0 - droop * Math.max(0, u) ** 2;   // (u: along the quill from its root; the tuck behind it, negative)
      const cx = rx + d[0] * u, cz = rz + d[2] * u, nrm = [0, 1, 0];
      const sink = tips && t > 1 - band + 1e-9 ? tips : vane;   // (the band's first row still belongs to the vane's strip)
      const bothSinks = tips && k === rows.length - 2;   // (the row where the band starts belongs to both strips)
      const mk = (e) => (k === 0 || tipRow) ? [e.vert([cx, y, cz], nrm, [0, t]), null]
        : [e.vert([cx + s[0] * w * .35, y, cz + s[2] * w * .35], nrm, [.35, t]), e.vert([cx - s[0] * w * .65, y, cz - s[2] * w * .65], nrm, [-.65, t])];
      ids.push({ v: mk(sink), b: bothSinks ? mk(tips) : null, sink });
    }
    for (let k = 1; k < rows.length; k++) {
      const e = ids[k].sink, A = ids[k - 1].sink === e ? ids[k - 1].v : ids[k - 1].b, B = ids[k].v;
      if (A[1] === null && B[1] === null) continue;
      if (A[1] === null) e.tri(A[0], B[0], B[1]);
      else if (B[1] === null) { e.tri(A[0], B[0], A[1]); }
      else { e.tri(A[0], B[0], B[1]); e.tri(A[0], B[1], A[1]); }
    }
  }
}
