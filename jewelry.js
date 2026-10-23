// JEWELRY (2026-10-06; docs/jewelry.md): what is worn ON the body and its clothes -- necklaces, collars, torcs,
// pendants, diadems, wreaths, earrings -- as parts of the items language, laid on GUIDES taken from the layers under
// them rather than placed by numbers. A necklace knows the neck's base, the slope of the shoulders and the chest, and
// the cloth over them; a diadem knows the skull and the hair's cap over it; an earring the ear's lobe.
//
// THE FITS (each `at(th, v)` -> { p, n, t, u }: a point on the outermost surface, its outward normal, the tangent
// round the body (toward +th) and the way DOWN the surface -- th in degrees round from the front, 0 ahead, +90 the
// figure's +z side):
//   neck  -- people.js builds it from the body's FORM and what the tailor dressed it in (clothes.js outerSurface: the
//            torso's oval, the neck and the fillet between them, the worn layers' thickness except where a neckline
//            opens, the standing shells -- a cape, a hood's cape, a cloak -- over them). v is the DROP: metres down the
//            surface from the neck's base (negative: up the neck -- a choker). In the CHEST's frame: its origin on the
//            torso's axis at the shoulders' rim, y up the chest, x the figure's forward (jewels.js places it there).
//   head  -- the face's own skull (face.js headGrid, the forehead this face has) and the hairstyle's cap over it
//            (hair.js capShape: its edge round the head and its thickness): where the hair covers, the band lies on the
//            hair. v is a HEIGHT on the head in the face's canonical frame (the crown +.10, the brows ~.02, the nape
//            -.06), scaled with the head.
//   ear   -- the lobe of each ear (face.js earFrame); th +90 / -90 picks the side.
// An item reaches a fit by name (`fit: "neck"`): the caller's param of that name (people.js hands the neck's), else
// one made from the item's own params (the head and the ears: a headwear item gets its face's head params), else a
// canon one (a neck without a body: the asset sheet).
//
// THE PARTS (items.js part types, every one drawn on its fit):
//   strand -- beads along a curve round the fit at `level` (a number, or [front, back]: a necklace hangs lower in front),
//             `vee` deepening it toward the front, over `th` [from, to] (all round by default); `bead`: round | tube |
//             disc | drop | cube (one bead every `size` + `gap`, the roles of `materials` in turn) or rod | twist | cord
//             (one continuous tube: a torc's twisted bar, a cord), `size` its radius (`length` a bead's), `swell` a rod
//             thicker toward its ends (a torc's terminals), `lift` off the surface
//   collar -- a broad plate from `from` to `to` (levels: numbers or [front, back]) in ROWS across it, inner to outer:
//             { share, kind: band | beads (cells round it, `n` of them, the row's `materials` in turn) | drops (teardrops
//             hanging from its outer edge, `length` long) } -- the Egyptian wesekh, a lunula, a gorget; `thick`
//   band   -- a ribbon round the fit at `level`, `width` across (in the fit's own units), `thick` out, `crest` widening
//             it toward the front (a diadem's brow plate) -- a fillet, a circlet, a choker
// and for any part or component an `on` placement: { fit, th: degrees or a list, ring: { n, from, to }, level (a
// number or [front, back]), lift } -- set on the fit's surface, its x round the body, its y up the surface, its z out
// of it (a pendant, a torc's terminals, a wreath's leaves, a brooch, an earring).
import { headGrid, earFrame } from "./face.js";
import { capShape } from "./hair.js";

const DEG = Math.PI / 180;
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const lerp = (a, b, t) => a + (b - a) * t;

// a frame from the surface's derivatives: t round (toward +th), u down, n out (away from the axis `out0`); `down` the
// sign of the level's own direction (a neck's drop runs down the surface, a head's height up it)
function frameAt(pt, th, v, dth, dv, out0, down = 1) {
  const p = pt(th, v), t = norm(sub(pt(th + dth, v), pt(th - dth, v))), u = mul(norm(sub(pt(th, v + dv), pt(th, v - dv))), down);
  let n = norm(cross(t, u));
  if (dot(n, out0(p)) < 0) n = mul(n, -1);
  return { p, n, t, u };
}

// ---- THE NECK -----------------------------------------------------------------------------------------------------
// form: people.js's FORM of the body; outer(y, th): the outermost surface's distance from the torso's axis at height y
// (the body's, from its feet), th radians round from the front (clothes.js outerSurface). Each of NT meridians is sampled
// every 2 mm from up the neck to under the armpits; its BASE is where the surface first stands clear of the neck's own
// radius there; the drop is the arc length down it from there.
export function neckFit(form, outer) {
  const rim = form.torso.parts[0].top, S = form.S, NT = 48, dy = .002;
  const y0 = form.neck.top ?? form.torso.collar + .06 * S, y1 = form.torso.parts[0].bottom - .1 * S;
  const rows = [];
  for (let i = 0; i < NT; i++) {
    const th = i / NT * 2 * Math.PI, ys = [], rs = [];
    // (the figure engine draws the surface as rings of points, faces between them: a ring's corners stand out from the
    //  true oval by a share of its radius -- what lies on it clears them, a few millimetres)
    for (let y = y0; y > y1; y -= dy) { ys.push(y); rs.push(outer(y, th) * 1.025 + .0045); }
    let b = rs.findIndex((r) => r > rs[0] + .006);
    if (b < 0) b = 0;
    const d = new Array(ys.length);
    d[b] = 0;
    for (let k = b + 1; k < ys.length; k++) d[k] = d[k - 1] + Math.hypot(rs[k] - rs[k - 1], dy);
    for (let k = b - 1; k >= 0; k--) d[k] = d[k + 1] - Math.hypot(rs[k + 1] - rs[k], dy);
    rows.push({ d, ys, rs });
  }
  const onRow = (row, dd) => {
    const { d, ys, rs } = row, n = d.length;
    if (dd <= d[0]) return [ys[0], rs[0]];
    if (dd >= d[n - 1]) return [ys[n - 1], rs[n - 1]];
    let lo = 0, hi = n - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (d[m] <= dd) lo = m; else hi = m; }
    const u = (dd - d[lo]) / Math.max(1e-9, d[hi] - d[lo]);
    return [lerp(ys[lo], ys[hi], u), lerp(rs[lo], rs[hi], u)];
  };
  const pt = (thDeg, dd) => {
    const f = ((thDeg / 360 * NT) % NT + NT) % NT, i0 = Math.floor(f), i1 = (i0 + 1) % NT, u = f - i0;
    const [ya, ra] = onRow(rows[i0], dd), [yb, rb] = onRow(rows[i1], dd), y = lerp(ya, yb, u), r = lerp(ra, rb, u), th = thDeg * DEG;
    return [r * Math.cos(th), y - rim, r * Math.sin(th)];
  };
  // (its KEY: the surface to 2 mm -- people of one build in one dress share their jewels' meshes)
  let h = 2166136261;
  for (const row of rows) for (let k = 0; k < row.rs.length; k += 6) { h ^= Math.round(row.rs[k] * 500) + 31 * Math.round(row.ys[k] * 500); h = Math.imul(h, 16777619) >>> 0; }
  return { kind: "neck", S: 1, key: h.toString(36), at: (th, v) => frameAt(pt, th, v, 1, .004, (p) => [p[0], 0, p[2]]) };
}

// a canon neck for an item seen without a body (the asset sheet, the viewer's item view): people.js hands over how to
// make it, and it is made the first time it is asked for (the game never asks: a person was half a second of its start)
let CANON_NECK = null;
export const setCanonNeck = (make) => { CANON_NECK = make; };

// ---- THE HEAD -----------------------------------------------------------------------------------------------------
// the item's params are the face's head params (scale, faceW, forehead, occiput, crown, hairline, the forehead's
// attributes) and its hairstyle's cap (`hairCap`, heads.js) with the face's `fringe`
export function headFit(P) {
  const H = headGrid(P, { detail: 1 }), S = H.S, cs = capShape(P.hairCap ?? null, H.Q, P.fringe);
  const top = cs?.top ?? 1;
  const skin = (th, y) => { const a = Math.min(180, Math.abs(th)), sg = th < 0 ? -1 : 1; return H.skinAt(Math.max(H.yBot + .005, Math.min(H.yTop - .002, y)), a, sg); };
  const outN = (p) => norm([p[0] + .01, 0, p[2]]);
  const nSkin = (th, y) => frameAt(skin, th, y, 1, .003, outN, -1).n;
  // the outermost surface: the skin, and the hair's cap over it where the cap reaches
  const pt = (th, y) => {
    const q = skin(th, y), a = Math.abs(th);
    const off = cs && y > cs.edgeY(a) - .001 && y < top ? cs.thickAt(y, a) : 0;
    return mul(off > 0 ? add(q, mul(nSkin(th, y), off)) : q, S);
  };
  return { kind: "head", S, at: (th, v) => frameAt(pt, th, v, 1, .003, outN, -1) };
}
// ---- THE EARS: the lobe, a little out from the ear's plate
export function earFit(P) {
  const H = headGrid(P, { detail: 1 }), S = H.S, { c, e } = earFrame(H);
  return { kind: "ear", S, at: (th) => {
    const sg = th < 0 ? -1 : 1;
    return { p: mul([c[0] + .001 * e, c[1] - .029 * e, (c[2] + .003) * sg], S), n: [0, 0, sg], t: [sg, 0, 0], u: [0, -1, 0] };
  } };
}

// a fit by name: the caller's, else one made from the item's own params (kept with them: built once an item)
const MADE = new WeakMap();
export function fitOf(name, P) {
  const given = P[name];
  if (given && typeof given.at === "function") return given;
  if (name === "neck") {
    if (!CANON_NECK) throw new Error("jewelry: no neck to lie on (people.js sets the canon one)");
    if (typeof CANON_NECK === "function") CANON_NECK = CANON_NECK();
    return CANON_NECK;
  }
  let m = MADE.get(P);
  if (!m) MADE.set(P, m = {});
  return m[name] ??= name === "head" ? headFit(P) : name === "ear" ? earFit(P) : (() => { throw new Error(`jewelry: no fit "${name}"`); })();
}

// a level at an angle: a number, or [front, back] (eased round the sides), deepened by `vee` toward the front
const levelAt = (lv, th, vee = 0) => {
  const c = Math.cos(th * DEG), base = Array.isArray(lv) ? lv[0] + (lv[1] - lv[0]) * (1 - c) / 2 : lv ?? 0;
  return base + vee * Math.pow(Math.max(0, c), 4);
};
const spanOf = (th) => { const a = th ?? [-180, 180]; return { a0: a[0], a1: a[1], closed: Math.abs(a[1] - a[0]) >= 359.9 }; };

// ---- THE `on` PLACEMENT: 3x4 frames on the fit (x round, y up the surface, z out), for items.js placementsOf
export function onFrames(on, P) {
  const fit = fitOf(on.fit ?? "neck", P), lift = (on.lift ?? 0) * fit.S, out = [];
  let ths = Array.isArray(on.th) ? on.th : [on.th ?? 0];
  if (on.ring) {
    const { n = 8, from = -180, to = 180 } = on.ring, k = Math.max(1, Math.round(n)), full = Math.abs(to - from) >= 359.9;
    ths = Array.from({ length: k }, (_, i) => from + (to - from) * (full ? i / k : k === 1 ? .5 : i / (k - 1)));
  }
  for (const th of ths) {
    const f = fit.at(th, levelAt(on.level, th, on.vee ?? 0)), n = f.n;
    let y = mul(f.u, -1); y = norm(sub(y, mul(n, dot(y, n))));
    const x = cross(y, n), p = add(f.p, mul(n, lift));
    out.push([x[0], y[0], n[0], p[0], x[1], y[1], n[1], p[1], x[2], y[2], n[2], p[2]]);
  }
  return out;
}

// ---- small solids, emitted along a frame ------------------------------------------------------------------------
// a lathe round axis `ax` at c: profile [[r, h]...] (h along the axis); b1, b2 square to it
function latheAt(em, c, ax, prof, k, uv0 = 0) {
  const a = norm(ax), ref = Math.abs(a[1]) < .9 ? [0, 1, 0] : [1, 0, 0], b1 = norm(cross(a, ref)), b2 = cross(a, b1);
  const rings = prof.map(([r, h], j) => {
    const nb = j === 0 ? prof[1] : prof[j - 1], na = j === prof.length - 1 ? prof[j - 1] : prof[j + 1];
    const dr = (na[0] - nb[0]) * (j === 0 ? -1 : 1), dh = (na[1] - nb[1]) * (j === 0 ? -1 : 1);   // (the profile's tangent)
    return Array.from({ length: k }, (_, i) => {
      const t = i / k * 2 * Math.PI, rad = add(mul(b1, Math.cos(t)), mul(b2, Math.sin(t)));
      const nn = r < 1e-6 ? mul(a, h > 0 ? 1 : -1) : norm(add(mul(rad, dh), mul(a, -dr)));
      return em.vert(add(add(c, mul(a, h)), mul(rad, r)), dot(nn, nn) > .1 ? nn : rad, [uv0 + i / k, j / (prof.length - 1)]);
    });
  });
  for (let j = 0; j + 1 < rings.length; j++) for (let i = 0; i < k; i++) {
    const i2 = (i + 1) % k;
    em.tri(rings[j][i], rings[j + 1][i], rings[j + 1][i2]); em.tri(rings[j][i], rings[j + 1][i2], rings[j][i2]);
  }
}
const sphereProf = (r, h0 = 0, rows = 3) => Array.from({ length: rows + 2 }, (_, i) => { const a = -Math.PI / 2 + i / (rows + 1) * Math.PI; return [r * Math.cos(a), h0 + r * Math.sin(a)]; });
const BEADS = {
  round: (em, c, f, r, len) => latheAt(em, c, f.t, sphereProf(r, 0, 2), 6),
  tube: (em, c, f, r, len) => latheAt(em, c, f.t, [[0, -len / 2], [r * .85, -len / 2], [r, 0], [r * .85, len / 2], [0, len / 2]], 6),
  disc: (em, c, f, r, len) => latheAt(em, c, f.t, [[0, -len / 2], [r, -len / 2], [r, len / 2], [0, len / 2]], 8),
  drop: (em, c, f, r, len) => latheAt(em, add(c, mul(f.u, r * .4)), f.u, [[0, -r * .9], [r * .55, -r * .7], [r, 0], [r * .8, len * .5], [r * .35, len * .85], [0, len]], 6),
  cube: (em, c, f, r, len) => latheAt(em, c, f.t, [[0, -r], [r * 1.3, -r], [r * 1.3, r], [0, r]], 4),
};
// a tube along a polyline (closed or not): radius per point, `sides`, its section turned along by `turn` radians a point
function tubeAlong(em, pts, ns, rad, sides, closed, turn = 0) {
  const n = pts.length, rings = [];
  for (let i = 0; i < n; i++) {
    const a = pts[closed ? (i - 1 + n) % n : Math.max(0, i - 1)], b = pts[closed ? (i + 1) % n : Math.min(n - 1, i + 1)];
    const t = norm(sub(b, a)), o = norm(sub(ns[i], mul(t, dot(ns[i], t)))), w = cross(t, o);
    rings.push(Array.from({ length: sides }, (_, k) => {
      const ang = k / sides * 2 * Math.PI + turn * i + Math.PI / sides, d = add(mul(o, Math.cos(ang)), mul(w, Math.sin(ang))), q = add(pts[i], mul(d, rad[i]));
      return { q, id: em.vert(q, d, [k / sides, i / n]) };
    }));
  }
  const m = closed ? n : n - 1;
  for (let i = 0; i < m; i++) for (let k = 0; k < sides; k++) {
    const A = rings[i], B = rings[(i + 1) % n], k2 = (k + 1) % sides;
    em.tri(A[k].id, B[k].id, B[k2].id); em.tri(A[k].id, B[k2].id, A[k2].id);
  }
  if (!closed) for (const [i, j] of [[0, 1], [n - 1, n - 2]]) {   // (its ends capped flat)
    const t = norm(sub(pts[i], pts[j])), c = em.vert(pts[i], t, [.5, .5]), ring = rings[i].map(({ q }) => em.vert(q, t, [0, 0]));
    for (let k = 0; k < sides; k++) em.tri(c, ring[k], ring[(k + 1) % sides]);
  }
}
// a flat shape lying on the surface with its thickness: outline [[x across (along t), y down (along u)]...] round its
// own centre `c0`, drawn from the frame f lifted by `lift`; its face, and its rim down to the surface
function plateOn(em, f, outline, c0, lift, thick, uv = [0, 0]) {
  const at = ([x, y], h) => add(add(add(f.p, mul(f.t, x)), mul(f.u, y)), mul(f.n, lift + h));
  const top = outline.map((q) => em.vert(at(q, thick), f.n, uv)), c = em.vert(at(c0, thick), f.n, uv);
  for (let k = 0; k < outline.length; k++) em.tri(c, top[k], top[(k + 1) % outline.length]);
  for (let k = 0; k < outline.length; k++) {
    const q = outline[k], q2 = outline[(k + 1) % outline.length], d = norm(add(mul(f.t, q[0] - c0[0]), mul(f.u, q[1] - c0[1])));
    const d2 = norm(add(mul(f.t, q2[0] - c0[0]), mul(f.u, q2[1] - c0[1])));
    const a = em.vert(at(q, 0), d, uv), b = em.vert(at(q2, 0), d2, uv), A = em.vert(at(q, thick), d, uv), B = em.vert(at(q2, thick), d2, uv);
    em.tri(a, b, B); em.tri(a, B, A);
  }
}

// the role of the k-th thing of a run: a list of roles in turn, or one
const roleOf = (mats, k) => Array.isArray(mats) ? mats[k % mats.length] : mats;

// ---- STRAND -------------------------------------------------------------------------------------------------------
export function strandGeometry(p, P, emitFor) {
  const fit = fitOf(p.fit ?? "neck", P), S = fit.S, { a0, a1, closed } = spanOf(p.th);
  const r = (p.size ?? .004) * S, len = (p.length ?? 2 * (p.size ?? .004)) * S, gap = (p.gap ?? .0008) * S, lift = (p.lift ?? .002) * S;
  const bead = p.bead ?? "round", mats = p.materials ?? p.material ?? "metal";
  // the path, finely: its points on the surface and their frames
  // (beads are placed along it, so it is fine; a tube is drawn along it: a cord, a chain every 6 degrees, a twisted bar every 3)
  const tube = bead === "rod" || bead === "twist" || bead === "cord";
  const N = Math.max(24, Math.round(Math.abs(a1 - a0) / (!tube ? 2 : bead === "twist" && (p.size ?? .004) > .003 ? 3 : 6))), F = [];
  for (let i = 0; i <= N - (closed ? 1 : 0); i++) {
    const th = a0 + (a1 - a0) * i / N;
    F.push({ ...fit.at(th, levelAt(p.level, th, p.vee ?? 0)), th });
  }
  if (tube) {
    // ONE TUBE: a torc's bar (twist: a square section turned along it), a cord; `swell` thicker toward its ends
    const sw = p.swell ?? 0, half = Math.max(1e-6, (a1 - a0) / 2), mid = (a0 + a1) / 2;
    const rad = F.map((f) => r * (1 + sw * Math.pow(Math.abs(f.th - mid) / half, 2)));
    const sides = bead === "twist" ? 4 : bead === "cord" ? 5 : 7, turn = bead === "twist" ? p.twist ?? .45 : 0;
    tubeAlong(emitFor(roleOf(mats, 0)), F.map((f, i) => add(f.p, mul(f.n, lift + rad[i]))), F.map((f) => f.n), rad, sides, closed, turn);
    return;
  }
  // BEADS, one every pitch along the path's own length (the roles in turn)
  const Q = F.map((f) => add(f.p, mul(f.n, lift + r))), cum = [0];
  for (let i = 1; i < Q.length; i++) cum.push(cum[i - 1] + Math.hypot(...sub(Q[i], Q[i - 1])));
  const total = cum[cum.length - 1] + (closed ? Math.hypot(...sub(Q[0], Q[Q.length - 1])) : 0), pitch = len + gap;
  const count = Math.max(1, Math.floor(total / pitch)), step = closed ? total / count : pitch, start = closed ? 0 : (total - (count - 1) * pitch) / 2;
  const shape = BEADS[bead] ?? BEADS.round;
  for (let k = 0, j = 0; k < count; k++) {
    const s = start + k * step;
    while (j + 2 < Q.length && cum[j + 1] < s) j++;
    const u = Math.max(0, Math.min(1, (s - cum[j]) / Math.max(1e-9, cum[j + 1] - cum[j]))), c = add(Q[j], mul(sub(Q[j + 1], Q[j]), u));
    shape(emitFor(roleOf(mats, k)), c, { t: norm(sub(Q[j + 1], Q[j])), u: F[j].u, n: F[j].n }, r, len);
  }
}

// ---- COLLAR -------------------------------------------------------------------------------------------------------
export function collarGeometry(p, P, emitFor) {
  const fit = fitOf(p.fit ?? "neck", P), S = fit.S, { a0, a1, closed } = spanOf(p.th);
  const lift = (p.lift ?? .002) * S, thick = (p.thick ?? .004) * S, NC = Math.max(16, Math.round(Math.abs(a1 - a0) / (p.step ?? 3.75)));
  const rows = p.rows ?? [{ share: 1, kind: "band", material: p.material ?? "metal" }];
  const body = rows.filter((q) => q.kind !== "drops"), tot = body.reduce((s, q) => s + (q.share ?? 1), 0) || 1;
  const lvl = (th, s) => lerp(levelAt(p.from, th), levelAt(p.to, th, p.vee ?? 0), s);
  const thAt = (i) => a0 + (a1 - a0) * i / NC;
  const P3 = (th, s, h) => { const f = fit.at(th, lvl(th, s)); return { q: add(f.p, mul(f.n, lift + h)), f }; };
  const quad = (em, A, B, C, D, nA = A.f.n, nB = B.f.n) => {
    const v = [em.vert(A.q, nA, [0, 0]), em.vert(B.q, nB, [1, 0]), em.vert(C.q, nB, [1, 1]), em.vert(D.q, nA, [0, 1])];
    em.tri(v[0], v[1], v[2]); em.tri(v[0], v[2], v[3]);
  };
  const role0 = (row) => roleOf(row.materials ?? row.material, 0);
  let s0 = 0;
  for (const row of rows) {
    if (row.kind === "drops") {   // TEARDROPS hanging from the outer edge, lying on the surface
      const n = Math.max(4, Math.round(row.n ?? NC / 2)), L = (row.length ?? .02) * S, rr = (row.width ?? .008) * S / 2;
      const outline = [[0, 0], ...Array.from({ length: 9 }, (_, m) => { const a = (-30 + m * 240 / 8) * DEG; return [rr * Math.cos(a), L - rr + rr * Math.sin(a)]; })];
      for (let k = 0; k < n; k++) {
        const th = a0 + (a1 - a0) * (closed ? k / n : (k + .5) / n), f = fit.at(th, lvl(th, 1) - .002 * S);
        plateOn(emitFor(roleOf(row.materials ?? row.material, k)), f, outline, [0, L - rr], lift, thick * .7);
      }
      continue;
    }
    const s1 = s0 + (row.share ?? 1) / tot;
    if (row.kind === "beads") {
      // BEADS: cells round the row, each its role in turn and a hair apart (they read as beads), over the plate they are
      // strung on (its ground shows between them)
      const cells = Math.max(4, Math.round(row.n ?? NC)), per = NC / cells;
      for (let c = 0; c < cells; c++) {
        const em = emitFor(roleOf(row.materials ?? row.material, c)), k = Math.max(1, Math.round(per));
        for (let a = 0; a < k; a++) {
          const tA = thAt(c * per + a * per / k), tB = thAt(c * per + (a + 1) * per / k);
          const g0 = a === 0 ? .1 : 0, g1 = a === k - 1 ? .1 : 0;
          const tA2 = lerp(tA, tB, g0 / Math.max(1, 1)), tB2 = lerp(tB, tA, g1);
          quad(em, P3(tA2, s0 + (s1 - s0) * .08, thick), P3(tB2, s0 + (s1 - s0) * .08, thick), P3(tB2, s1 - (s1 - s0) * .08, thick), P3(tA2, s1 - (s1 - s0) * .08, thick));
        }
      }
      const g = emitFor(row.ground ?? p.ground ?? role0(row));
      for (let i = 0; i < NC; i++) quad(g, P3(thAt(i), s0, thick * .6), P3(thAt(i + 1), s0, thick * .6), P3(thAt(i + 1), s1, thick * .6), P3(thAt(i), s1, thick * .6));
    } else {
      const em = emitFor(role0(row));
      for (let i = 0; i < NC; i++) quad(em, P3(thAt(i), s0, thick), P3(thAt(i + 1), s0, thick), P3(thAt(i + 1), s1, thick), P3(thAt(i), s1, thick));
    }
    s0 = s1;
  }
  // THE EDGES: the plate's thickness at its inner and outer rims, and at its ends when it is open
  const edge = (s, role, sg) => {
    const em = emitFor(role);
    for (let i = 0; i < NC; i++) { const A = P3(thAt(i), s, 0), B = P3(thAt(i + 1), s, 0); quad(em, A, B, P3(thAt(i + 1), s, thick), P3(thAt(i), s, thick), mul(A.f.u, sg), mul(B.f.u, sg)); }
  };
  edge(0, role0(body[0]), -1);
  edge(1, role0(body[body.length - 1]), 1);
  if (!closed) for (const [th, sg] of [[a0, -1], [a1, 1]]) {
    const em = emitFor(role0(body[0]));
    for (let k = 0; k < 8; k++) { const A = P3(th, k / 8, 0), nn = mul(A.f.t, sg); quad(em, A, P3(th, (k + 1) / 8, 0), P3(th, (k + 1) / 8, thick), P3(th, k / 8, thick), nn, nn); }
  }
}

// ---- BAND ---------------------------------------------------------------------------------------------------------
export function bandGeometry(p, P, emitFor) {
  const fit = fitOf(p.fit ?? "head", P), S = fit.S, { a0, a1, closed } = spanOf(p.th);
  const W = p.width ?? .012, thick = (p.thick ?? .003) * S, lift = (p.lift ?? .001) * S, crest = p.crest ?? 0, cPow = p.crestPow ?? 6;
  const NC = Math.max(24, Math.round(Math.abs(a1 - a0) / (p.step ?? 5)));
  // (the width in the fit's own units -- a head's heights, a neck's drops -- so both edges lie on the surface; on a
  //  head the upper edge is the greater height, on a neck the lesser drop; `crest` widens it upward toward the front)
  const up = fit.kind === "neck" ? -1 : 1;
  const ring = [];
  for (let i = 0; i <= NC - (closed ? 1 : 0); i++) {
    const th = a0 + (a1 - a0) * i / NC, lv = levelAt(p.level, th, p.vee ?? 0), w = W / 2, wc = W * crest * Math.pow(Math.max(0, Math.cos(th * DEG)), cPow);
    ring.push({ lo: fit.at(th, lv - up * w), hi: fit.at(th, lv + up * (w + wc)), th });
  }
  const em = emitFor(p.material ?? "metal"), n = ring.length, m = closed ? n : n - 1;
  const corner = (f, out) => add(f.p, mul(f.n, lift + (out ? thick : 0)));
  const V = ring.map(({ lo, hi }) => {
    const dn = sub(lo.p, hi.p), upv = sub(hi.p, lo.p);
    return { lo0: em.vert(corner(lo, false), dn, [0, 0]), lo1e: em.vert(corner(lo, true), dn, [0, 0]), lo1: em.vert(corner(lo, true), lo.n, [0, 0]),
             hi1: em.vert(corner(hi, true), hi.n, [0, 1]), hi1e: em.vert(corner(hi, true), upv, [0, 1]), hi0: em.vert(corner(hi, false), upv, [0, 1]) };
  });
  for (let i = 0; i < m; i++) {
    const A = V[i], B = V[(i + 1) % n];
    em.tri(A.lo1, B.lo1, B.hi1); em.tri(A.lo1, B.hi1, A.hi1);          // (its face)
    em.tri(A.hi0, B.hi0, B.hi1e); em.tri(A.hi0, B.hi1e, A.hi1e);       // (its upper edge)
    em.tri(A.lo0, B.lo0, B.lo1e); em.tri(A.lo0, B.lo1e, A.lo1e);       // (its lower edge)
  }
  if (!closed) for (const [i, sg] of [[0, -1], [n - 1, 1]]) {
    const nn = mul(ring[i].lo.t, sg), q = [corner(ring[i].lo, false), corner(ring[i].lo, true), corner(ring[i].hi, true), corner(ring[i].hi, false)].map((x) => em.vert(x, nn, [0, 0]));
    em.tri(q[0], q[1], q[2]); em.tri(q[0], q[2], q[3]);
  }
}
