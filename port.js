// THE PORT'S LAYOUT (2026-11-03): where a culture's harbour pieces stand along a stretch of shore -- a PURE function
// of plain inputs (no scene, no catalogue: node can test it), so the sea's harbourSite (docs/world.md) and the
// integration in index.html only pass numbers through.
//
//   layoutPort({ points, normals, heading, length, level, period, dress, seed, table, gate, groundY, maxLength })
//     points   the shore stretch, ordered: [[x, z], ...] (world metres)
//     normals  per point the SEAWARD unit normal [nx, nz] (out over the water); left out: from `heading`
//     heading  the seaward direction as a yaw (atan2(nx, nz)); used where normals are missing
//     length   the stretch's length (else measured)
//     level    the water's surface height (world y); the quay top stands the culture's F above it
//     period, dress   the world's period (periods.json key) and its dress ({style: weight} or a style): the culture
//     seed     any integer; the same inputs give the same port
//     table    assets/world/ports.json (the cultures)
//     gate     [x, z] of the town's gate (the street leaves the quay toward it), optional
//     groundY  (x, z) => the ground's height, optional: a land piece standing higher than the quay top keeps its ground
//
// returns { culture, finish, compact, quayTop, waterY, quayLine, placements, berths, path, pads, dropped }
//   compact     true for a stretch under 40 m: one straight quay, a pier if there is room, one store, the light (no mole, slips, cranes)
//   placements  [{ id, role, def, params, finish, x, y, z, yaw, w, d }] -- build each with
//               archBuilding(def, { params, finish: ASSETS.get(finish), origin: true }) and set it at x, y, z turned by yaw
//               (the engine's yaw: a piece's local +z, its seaward side, points along (sin yaw, cos yaw))
//   berths      [{ id, kind: "quay"|"pier", a, b, out, length, depth, moor }] -- a hull lies along a..b (the face it lies
//               against, at the waterline), on the `out` side ([nx, nz]); `length` the longest hull it takes, `depth` the water
//               at the face; `moor` the bollards' [x, z] to make fast to
//   path        [[x, z], ...] from the quay apron through the street gap up to the gate (or 30 m inland)
//   pads        [{ x, z, yaw, w, d, y }] rectangles the ground should be levelled to y under (the quay and its apron,
//               every land piece's plot)
//
// Every piece shares one frame (tools/archgen/harbour.py): y 0 its quay top, +z seaward, the water at y -F.

const TAU = Math.PI * 2;
const rnd = (seed) => { let a = (seed >>> 0) || 1; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
const len = (x, z) => Math.hypot(x, z);
const norm = ([x, z]) => { const l = len(x, z) || 1; return [x / l, z / l]; };
const add = (a, b, k = 1) => [a[0] + b[0] * k, a[1] + b[1] * k];
const yawOf = ([nx, nz]) => Math.atan2(nx, nz);
const r3 = (v) => Math.round(v * 1000) / 1000;
// a piece's local (x, z) in the world, its origin at o turned by yaw (the engine's: x' = x cos + z sin, z' = -x sin + z cos)
const toWorld = (o, yaw, x, z) => [o[0] + x * Math.cos(yaw) + z * Math.sin(yaw), o[1] - x * Math.sin(yaw) + z * Math.cos(yaw)];

// the culture's entry: the period's, else the first dress style's, else default -- `like` resolved
export function portCulture(table, period, dress) {
  const C = table?.cultures ?? {};
  const styles = typeof dress === "string" ? [dress] : Object.keys(dress ?? {});
  const key = C[period] ? period : styles.find((k) => k && C[k]) ?? "default";
  const resolve = (k, depth = 0) => { const e = C[k] ?? {}; return e.like && depth < 4 ? { ...resolve(e.like, depth + 1), ...e, like: undefined } : e; };
  return { key, ...resolve(key) };
}

// Douglas-Peucker on [x, z] points
function simplify(P, tol) {
  if (P.length < 3) return P.slice();
  const keep = new Uint8Array(P.length); keep[0] = keep[P.length - 1] = 1;
  const stack = [[0, P.length - 1]];
  while (stack.length) {
    const [i, j] = stack.pop(); let best = -1, bd = tol;
    const [ax, az] = P[i], [bx, bz] = P[j], L = len(bx - ax, bz - az) || 1;
    for (let k = i + 1; k < j; k++) { const d = Math.abs((bx - ax) * (P[k][1] - az) - (bz - az) * (P[k][0] - ax)) / L; if (d > bd) { bd = d; best = k; } }
    if (best > 0) { keep[best] = 1; stack.push([i, best], [best, j]); }
  }
  return P.filter((_, k) => keep[k]);
}

// two oriented rectangles (centre, yaw, w along local x, d along local z) overlap? (separating axes)
function overlap(A, B, pad = 0) {
  const axes = [A, B].flatMap((R) => [[Math.cos(R.yaw), -Math.sin(R.yaw)], [Math.sin(R.yaw), Math.cos(R.yaw)]]);
  const corners = (R) => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([sx, sz]) => toWorld([R.cx, R.cz], R.yaw, sx * (R.w / 2 + pad / 2), sz * (R.d / 2 + pad / 2)));
  const ca = corners(A), cb = corners(B);
  return axes.every(([ux, uz]) => {
    const pa = ca.map(([x, z]) => x * ux + z * uz), pb = cb.map(([x, z]) => x * ux + z * uz);
    return Math.max(...pa) > Math.min(...pb) && Math.max(...pb) > Math.min(...pa);
  });
}

export function layoutPort(opts) {
  const { table, seed = 1, level = 0, gate = null, groundY = null } = opts;
  const C = portCulture(table, opts.period, opts.dress);
  const R = rnd(seed * 7919 + 17), pick = (v) => (Array.isArray(v) ? v[0] + R() * (v[1] - v[0]) : v);
  const pickN = (v) => Math.max(0, Math.round(Array.isArray(v) ? v[0] + R() * (v[1] - v[0] + 0.999) - 0.5 : v ?? 1));
  const Q0 = { style: "stone", F: 1.6, D: 3.5, T: 1.6, B: 10, bay: 6, ...(C.quay ?? {}) };
  const { F, D, T, B } = Q0, reach = Q0.reach ?? (Q0.style === "steps" ? 4.6 : 0.3);
  const quayTop = level + F, finish = C.finish ?? "finishes/hanse-port";
  const placements = [], berths = [], pads = [], dropped = [], foot = [];
  const place = (role, def, params, o, yaw, w, d, y = quayTop, box = null) => {
    const p = { id: `${role} ${placements.length}`, role, def, params: params ?? {}, finish, x: r3(o[0]), y: r3(y), z: r3(o[1]), yaw: r3(yaw), w: r3(w), d: r3(d) };
    placements.push(p);
    if (box) foot.push({ pad: 2, ...box, id: p.id });   // (pad: the clearance a land piece keeps from it)
    return p;
  };

  // ---- the shore: its points, seaward normals, arclength
  let pts = (opts.points ?? opts.shore?.points ?? []).map(([x, z]) => [x, z]);
  let nrm = opts.normals ?? opts.shore?.normals ?? null;
  if (pts.length < 2) throw new Error("layoutPort: the shore needs two points at least");
  if (!nrm) {
    const h = opts.heading ?? 0, hs = [Math.sin(h), Math.cos(h)];
    nrm = pts.map((p, i) => { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)], t = norm([b[0] - a[0], b[1] - a[1]]), n = [t[1], -t[0]]; return n[0] * hs[0] + n[1] * hs[1] >= 0 ? n : [-n[0], -n[1]]; });
  }
  nrm = nrm.map(norm);
  const S = [0]; for (let i = 1; i < pts.length; i++) S.push(S[i - 1] + len(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const total = S[S.length - 1];
  const at = (s) => {   // the shore point and its normal at arclength s
    let i = 1; while (i < S.length - 1 && S[i] < s) i++;
    const f = Math.min(1, Math.max(0, (s - S[i - 1]) / ((S[i] - S[i - 1]) || 1)));
    return [[pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f],
            norm([nrm[i - 1][0] + (nrm[i][0] - nrm[i - 1][0]) * f, nrm[i - 1][1] + (nrm[i][1] - nrm[i - 1][1]) * f])];
  };

  // ---- the quay line: the middle of the stretch, as long as the culture builds, straightened into runs
  const Lh = Math.min(total, C.length ?? 140, opts.maxLength ?? 1e9), s0 = (total - Lh) / 2;
  const samp = []; for (let s = s0; s < s0 + Lh - 1e-6; s += 2) samp.push(at(s)[0]); samp.push(at(s0 + Lh)[0]);
  // a stretch under 40 m is a landing, not a harbour: one straight quay, a pier if it has room, one store, the light
  const compact = Lh < 40;
  let Ql = compact ? [samp[0], samp[samp.length - 1]] : simplify(samp, 1.5);
  for (let k = 1; k < Ql.length - 1 && Ql.length > 2;) {   // (no run shorter than 10 m: a corner the pieces would crowd)
    const a = len(Ql[k][0] - Ql[k - 1][0], Ql[k][1] - Ql[k - 1][1]), b = len(Ql[k + 1][0] - Ql[k][0], Ql[k + 1][1] - Ql[k][1]);
    if (Math.min(a, b) < 10) Ql.splice(k, 1); else k++;
  }
  const segs = []; let acc = 0;
  for (let i = 0; i + 1 < Ql.length; i++) {
    const a = Ql[i], b = Ql[i + 1], L = len(b[0] - a[0], b[1] - a[1]), u = norm([b[0] - a[0], b[1] - a[1]]);
    let n = [u[1], -u[0]]; const nm = at(s0 + acc + L / 2)[1];
    if (n[0] * nm[0] + n[1] * nm[1] < 0) n = [-n[0], -n[1]];
    segs.push({ i, a, b, u, n, L, s: acc, yaw: yawOf(n) }); acc += L;
  }
  const Lq = acc;
  const segAt = (s) => (s <= 0 ? segs[0] : segs.find((g) => s >= g.s - 1e-6 && s <= g.s + g.L + 1e-6) ?? segs[segs.length - 1]);
  const onQuay = (s, off = 0) => { const g = segAt(s); return add(add(g.a, g.u, s - g.s), g.n, off); };   // (off: + seaward, - inland)
  const fits = (s, w, margin = 2) => { const g = segAt(s); return s - w / 2 >= g.s + margin && s + w / 2 <= g.s + g.L - margin ? g : null; };
  // intervals of the quay face taken: [s0, s1, what]
  const taken = [];
  const free = (a, b) => taken.every(([x, y]) => b <= x || a >= y);
  const findSpan = (w, from, dir, margin = 2) => {   // the first span w wide on one run, free, scanning from `from` in `dir`
    for (let k = 0; k <= Lq; k += 1) {
      const c = from + dir * (k + w / 2);
      if (c - w / 2 < 0 || c + w / 2 > Lq) continue;
      if (fits(c, w, margin) && free(c - w / 2, c + w / 2)) return c;
    }
    return null;
  };

  // ---- the mole and the light: the mole from one end of the quay, swung in toward the harbour's middle
  const moleSpec = !compact && C.mole && C.mole !== "none" && pickN(C.mole.n ?? [1, 1]) > 0 ? C.mole : null;
  const lightSpec = C.light && C.light !== "none" ? C.light : null;
  const end = R() < 0.5 ? 0 : 1;   // (the end the mole or the light stands at; the slips and sheds keep to the other)
  const endSeg = end ? segs[segs.length - 1] : segs[0], endPt = end ? endSeg.b : endSeg.a, inward = end ? [-endSeg.u[0], -endSeg.u[1]] : endSeg.u;
  // (laid after the piers: it is shortened until it keeps a hull's width off every pier head)
  const moleAndLight = () => {
    let moleW = 0;
    if (moleSpec) {
      const W = moleSpec.W ?? 8, swing = 0.65;
      let ML = Math.round(Math.min(pick(moleSpec.L ?? [40, 60]), Math.max(24, Lq * 0.8)));
      const dir = norm(add([endSeg.n[0] * Math.cos(swing), endSeg.n[1] * Math.cos(swing)], inward, Math.sin(swing)));
      const yaw = yawOf(dir), root = add(add(endPt, dir, -2), inward, -W / 2);
      const boxOf = (L) => ({ cx: add(root, dir, L / 2)[0], cz: add(root, dir, L / 2)[1], yaw, w: W, d: L });
      const near = foot.slice();   // (the piers, slips and sheds already laid)
      while (ML > 20 && near.some((f) => overlap(f, boxOf(ML), f.id.startsWith("pier") ? 24 : 8))) ML -= 4;
      const open = -(inward[0] * Math.cos(yaw) - inward[1] * Math.sin(yaw));   // (the open sea's side, in the mole's own x: away from the harbour)
      place("mole", "components/mole", { L: ML, W, F, D: D + 0.5, side: open >= 0 ? 1 : -1 }, root, yaw, W, ML, quayTop, boxOf(ML));
      moleW = W;
      if (lightSpec && (lightSpec.on ?? "mole") === "mole") {
        const head = add(root, dir, ML);
        place("light", lightSpec.def, lightSpec.params, head, yaw, lightSpec.w ?? 8, lightSpec.d ?? 8, quayTop + 0.4);
      }
    }
    if (lightSpec && (lightSpec.on === "land" || (!moleSpec && lightSpec.on !== "none"))) {   // (past the quay's end, beside the mole's root)
      const w = lightSpec.w ?? 8, d = lightSpec.d ?? w, o = add(add(endPt, inward, -(moleW + w / 2 + 3)), endSeg.n, -(d / 2 + 1));
      const y = groundY ? Math.max(quayTop, groundY(o[0], o[1])) : quayTop;
      place("light", lightSpec.def, lightSpec.params, o, endSeg.yaw, w, d, y, { cx: o[0], cz: o[1], yaw: endSeg.yaw, w, d });
      pads.push({ x: r3(o[0]), z: r3(o[1]), yaw: r3(endSeg.yaw), w: r3(w + 2), d: r3(d + 2), y: r3(y) });
    }
  };

  // ---- the waterfront pieces (ship sheds, slips) from the far end in: they stand in the quay's place
  const far = end ? 0 : Lq, fdir = end ? 1 : -1;
  for (const spec of compact ? [] : C.waterfront ?? []) for (let k = pickN(spec.n); k-- > 0;) {
    const used = taken.reduce((m, [x, y]) => m + y - x, 0);   // (no more than 40 % of the quay given over to them)
    const c = used + spec.w + 4 <= Lq * 0.4 ? findSpan(spec.w + 4, far, fdir, 1) : null;
    if (c === null) { dropped.push(spec.def); continue; }
    const g = segAt(c), o = onQuay(c);
    taken.push([c - spec.w / 2 - 2, c + spec.w / 2 + 2, spec.role]);
    const ctr = add(o, g.n, (spec.out - spec.d) / 2);
    place(spec.role ?? "waterfront", spec.def, { F, D, ...(spec.params ?? {}) }, o, g.yaw, spec.w, spec.d + spec.out, quayTop,
          { cx: ctr[0], cz: ctr[1], yaw: g.yaw, w: spec.w, d: spec.d + spec.out });
  }

  // ---- the piers: spread along the free quay, each square off its run
  const PS = C.piers ?? { n: [1, 1], L: [16, 24] }, nP = compact ? (Lq >= 20 && pickN(PS.n) > 0 ? 1 : 0) : pickN(PS.n), PW = PS.W ?? 3.4;
  const z0 = Q0.style === "steps" ? reach : 0;   // (over a stepped quay the deck spans the steps; its bents stand past the ledge)
  const pierAt = [];
  for (let k = 0; k < nP; k++) {
    let c = (Lq * (k + 1)) / (nP + 1);
    const ok = (c) => fits(c, PW + 2, 1.5) && free(c - PW / 2 - 4, c + PW / 2 + 4) && pierAt.every((p) => Math.abs(p - c) > 16);
    for (let t = 0; t < 2 * Lq && !ok(c); t++) c = (Lq * (k + 1)) / (nP + 1) + (t % 2 ? -1 : 1) * Math.ceil(t / 2);
    if (!ok(c)) { dropped.push("components/pier"); continue; }
    const g = segAt(c), L = Math.round(Math.max(z0 + 10, pick(PS.L ?? [16, 24]) * (compact ? 0.7 : 1))), o = onQuay(c, -0.05);
    taken.push([c - PW / 2 - 1, c + PW / 2 + 1, "pier"]); pierAt.push(c);
    place("pier", "components/pier", { L, W: PW, F, D, z0 }, o, g.yaw, PW, L, quayTop, { cx: add(o, g.n, L / 2)[0], cz: add(o, g.n, L / 2)[1], yaw: g.yaw, w: PW, d: L, pad: 0 });
    const h0 = Math.max(3, z0 + 1);
    for (const side of [-1, 1]) {   // (a hull along each side: the side's line at the waterline, from 3 m out -- or past the steps' ledge -- to the head)
      const x = side * (PW / 2 + 0.3), a = toWorld(o, g.yaw, x, h0), b = toWorld(o, g.yaw, x, L - 0.5), out = [side * Math.cos(g.yaw), -side * Math.sin(g.yaw)];
      berths.push({ id: `pier ${pierAt.length} ${side < 0 ? "west" : "east"}`, kind: "pier", a: a.map(r3), b: b.map(r3), out: out.map(r3), length: r3(L - h0 - 1), depth: D,
                    moor: [toWorld(o, g.yaw, side * (PW / 2 - 0.3), L / 2), toWorld(o, g.yaw, side * (PW / 2 - 0.3), L - 0.4)].map((p) => p.map(r3)) });
    }
  }

  moleAndLight();

  // ---- the quay itself, run by run, where nothing stands in its place; the stair on the longest stone run
  const runs = [];
  let nQ = 0;
  for (const g of segs) {
    let cuts = [[g.s, g.s + g.L]];
    for (const [x, y, what] of taken) if (what !== "pier") cuts = cuts.flatMap(([a, b]) => (y <= a || x >= b ? [[a, b]] : [[a, Math.max(a, x)], [Math.min(b, y), b]]));
    for (const [a, b] of cuts) if (b - a > 2) runs.push({ g, a, b });
  }
  const longest = runs.reduce((m, r) => (r.b - r.a > (m ? m.b - m.a : 0) ? r : m), null);
  for (const r of runs) {
    const { g } = r;
    // (a run meeting the next run at a corner reaches on by the mitre, so the two walls close)
    const ext = (s) => { const h = segs.find((q) => q !== g && Math.abs((q.s === s ? q.s : q.s + q.L) - s) < 1e-6); if (!h) return 0;
      const turn = Math.acos(Math.max(-1, Math.min(1, g.u[0] * h.u[0] + g.u[1] * h.u[1]))); return Math.min(3, (T + B) * Math.tan(turn / 2)); };
    const ea = Math.abs(r.a - g.s) < 1e-6 ? ext(g.s) : 0, eb = Math.abs(r.b - g.s - g.L) < 1e-6 ? ext(g.s + g.L) : 0;
    const L = r.b - r.a + ea + eb, c = (r.a - ea + r.b + eb) / 2, o = add(g.a, g.u, c - g.s);
    const stairs = r === longest && Q0.style === "stone" && L > 16 ? "yes" : "no";
    const back = add(o, g.n, -(T + B) / 2);
    place("quay", "components/quay", { L: r3(L), style: Q0.style, F, D, T, B, bay: Q0.bay ?? 6, stairs }, o, g.yaw, L, T + B, quayTop,
          { cx: back[0], cz: back[1], yaw: g.yaw, w: L, d: T + B, pad: 0 });
    pads.push({ x: r3(back[0]), z: r3(back[1]), yaw: r3(g.yaw), w: r3(L), d: r3(T + B), y: r3(quayTop) });
    // its berths: the free face between the piers (a hull's length clear of each pier), cut to 45 m at most
    let spans = [[r.a + 1, r.b - 1]];
    for (const c of pierAt) spans = spans.flatMap(([a, b]) => (c + PW / 2 + 6 <= a || c - PW / 2 - 6 >= b ? [[a, b]] : [[a, Math.min(b, c - PW / 2 - 6)], [Math.max(a, c + PW / 2 + 6), b]]));
    for (const [a, b] of spans) {
      if (b - a < 12) continue;
      const n = Math.ceil((b - a) / 45), step = (b - a) / n;
      for (let k = 0; k < n; k++) {
        const sa = a + k * step, sb = sa + step, pa = add(onQuay(sa), g.n, reach), pb = add(onQuay(sb), g.n, reach);
        const moor = []; for (let s = sa + 2; s < sb - 1; s += Q0.bay ?? 6) moor.push(onQuay(s, -0.75).map(r3));
        berths.push({ id: `quay ${++nQ}`, kind: "quay", a: pa.map(r3), b: pb.map(r3), out: g.n.map(r3), length: r3(step - 2), depth: D, moor, s: [sa, sb] });
      }
    }
  }

  // ---- the cranes: on the apron at the middle of the longest quay berths
  const qb = berths.filter((b) => b.kind === "quay").sort((x, y) => y.length - x.length);
  for (const spec of compact ? [] : C.cranes ?? []) for (let k = 0, n = pickN(spec.n); k < n && k < qb.length; k++) {
    const b = qb[k], sm = (b.s[0] + b.s[1]) / 2, g = segAt(sm), o = onQuay(sm, spec.set ?? -2), params = { F, ...(spec.params ?? {}) };
    // swung over the berth's hold: a point 2.5 m out from the hull's side, somewhere along its middle half
    const t = 0.25 + 0.5 * R(), hold = add([b.a[0] + (b.b[0] - b.a[0]) * t, b.a[1] + (b.b[1] - b.a[1]) * t], b.out, 2.5);
    const dx = hold[0] - o[0], dz = hold[1] - o[1], c = Math.cos(g.yaw), s = Math.sin(g.yaw);
    const lx = dx * c - dz * s, lz = dx * s + dz * c;   // (the hold in the crane's own frame)
    if (spec.swing === "jib") {
      const ang = Math.max(-70, Math.min(70, Math.atan2(lx, lz) * 180 / Math.PI)), dist = Math.hypot(lx, lz);
      params.jib = Math.round(ang); params.reach = r3(Math.max(2, Math.min(spec.R ? 8 : 12, dist - (spec.R ?? 0))));
    } else if (spec.swing === "lean") params.lean = r3(Math.max(1.5, Math.min(4.5, lz)));
    place("crane", spec.def, params, o, g.yaw, spec.w ?? 8, spec.d ?? 8, quayTop);
  }
  for (const b of berths) delete b.s;

  // ---- the street up to the town: where the quay comes nearest the gate (else its middle), clear of the waterfront
  let sp = Lq / 2;
  if (gate) { let best = 1e18; for (let s = 0; s <= Lq; s += 1) { const p = onQuay(s); const d2 = (p[0] - gate[0]) ** 2 + (p[1] - gate[1]) ** 2; if (d2 < best) { best = d2; sp = s; } } }
  const blocked = (a, b) => taken.some(([x, y, what]) => what === "sheds" && !(b <= x || a >= y));
  for (let t = 0; t < Lq && (blocked(sp - 5, sp + 5) || !fits(sp, 8, 0)); t++) sp = Math.min(Lq - 4, Math.max(4, sp + (t % 2 ? t : -t)));
  const gs = segAt(sp);

  // ---- the row behind the apron: the office by the street, then the rest out to either side
  const row = T + B + 1.5;   // (the row's front line, inland from the face)
  const landList = [];
  if (compact) {   // (one store: the smallest warehouse or store that fits beside the street, else the smallest piece)
    const L0 = C.land ?? [], fit = (r) => L0.filter((p) => r.includes(p.role) && p.w <= Lq + 8).sort((x, y) => x.w - y.w);
    const one = fit(["warehouse", "store"])[0] ?? fit(["office", "market", "warehouse", "store"])[0] ?? L0.slice().sort((x, y) => x.w - y.w)[0];
    if (one) landList.push(one);
  } else for (const spec of C.land ?? []) for (let k = pickN(spec.n); k-- > 0;) landList.push(spec);
  landList.sort((x, y) => (x.role === "office" ? -1 : y.role === "office" ? 1 : 0));
  const cur = [sp + 4, sp - 4];   // (the next free place either side of the street: right, left)
  const st = onQuay(sp, -(row + 20));
  foot.push({ id: "street", cx: st[0], cz: st[1], yaw: gs.yaw, w: 7, d: 40, pad: 1 });
  let side = R() < 0.5 ? 0 : 1, maxD = 0;
  for (const spec of landList) {
    let done = false;
    for (let tries = 0; tries < 2 && !done; tries++, side ^= 1) {
      const dir = side ? -1 : 1;
      for (let guard = 0; guard < 120 && !done; guard++) {
        const c = cur[side] + dir * spec.w / 2;
        if (c - spec.w / 2 < -8 || c + spec.w / 2 > Lq + 8) break;
        // the plot squares off the run its middle lies on (on a bend the plots fan), set back further where a neighbour is in the way
        const g = segAt(Math.min(Lq, Math.max(0, c)));
        for (const push of [0, 2, 4, 7, 10]) {
          const o = add(add(g.a, g.u, c - g.s), g.n, -(row + spec.d / 2 + push)), boxR = { cx: o[0], cz: o[1], yaw: g.yaw, w: spec.w, d: spec.d };
          if (foot.some((f) => overlap(f, boxR, f.pad ?? 2))) continue;
          const y = groundY ? Math.max(quayTop, groundY(o[0], o[1])) : quayTop;
          place(spec.role ?? "land", spec.def, spec.params, o, g.yaw, spec.w, spec.d, y, boxR);
          pads.push({ x: r3(o[0]), z: r3(o[1]), yaw: r3(g.yaw), w: r3(spec.w + 2), d: r3(spec.d + 2), y: r3(y) });
          cur[side] += dir * (spec.w + 2 + R() * 3); maxD = Math.max(maxD, spec.d + push); done = true;
          break;
        }
        if (!done) cur[side] += dir * 3;
      }
    }
    if (!done) dropped.push(spec.def);
  }
  const p0 = onQuay(sp, -(T + B / 2)), p1 = onQuay(sp, -(row + maxD + 4));
  const path = [p0, p1, gate ?? add(p1, gs.n, -30)].map((p) => p.map(r3));

  return { culture: C.key, finish, compact, quayTop: r3(quayTop), waterY: level, quayLine: Ql.map((p) => p.map(r3)), placements, berths, path, pads, dropped };
}
