// THE HAIR (2026-09-30): hairstyles GROWN FROM THE HEAD'S OWN VERTICES (face.js headGrid: the scalp's rows and rings),
// as strands -- each a ribbon of a few segments, started at a scalp point along its normal, combed the style's way,
// bent down by gravity, kept off the skull, waved or curled -- since only the outside is seen, a sheet of ribbons is
// enough: no volume inside. A style says which scalp REGIONS grow (by height and angle round the head), how long
// (front to back), which way they are combed, how much they hang, wave and curl, how wide the ribbons are; and what
// GATHERS them (a ponytail's tie, a bun, a topknot: the strands run there and a rope, a knot or a bun goes on), or
// which hang as LOCKS (two long ones in front of the ears). items.js draws it as the part type `hair`
// (assets/items/hair/*.json), on the face it belongs to (a face definition names its `hairstyle`).
import { headGrid } from "./face.js";
import { thornLattice } from "./thorns.js";   // the spikes' lattice (shared with manes.js)

const DEG = Math.PI / 180;
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const lerp = (a, b, t) => a + (b - a) * t;
function rng(seed) {
  let a = (seed >>> 0) || 1;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// a STRAND GROUP (a style's `strands` entry), every number in metres unless said:
//   region: { y: [lo, hi] (heights on the head, in the face's frame: the crown is +.10, the nape -.06), th: [from, to]
//             (degrees round the head from the front: 0 the forehead, 90 the ears, 180 the nape) }, every: k (every
//             k-th scalp point of the region, 1 all of them), extra: n (strands between the points, by the seed)
//   length: [at the front, at the back] (metres, by the strand's angle), or one number
//   comb: "down" | "back" | "forward" | "out" | "up" | [x, y, z] (which way it leaves the scalp, with the normal)
//   hang: 0..1 (how much gravity bends it per metre; 0 sticks out, 1 falls), lift: metres off the scalp it starts
//   wave: { amp, per } (a sideways wave, its amplitude and period along the strand), curl: { r, per } (a helix)
//   width: [at the root, at the tip], seg: segments (6)
//   to: [x, y, z] gathers the strands there (a ponytail's tie, a topknot): each runs to that point instead of hanging
// THE CAP'S SHAPE (a style's `cap`, Q the head's params): the y of its edge at each angle round the head (0 the forehead,
// 180 the nape), and how thick it stands off the skin at a height and an angle -- the cap below draws it, and what is
// worn over the hair (jewelry.js headFit: a diadem, a wreath) lies on it
export function capShape(cap, Q, fringe) {
  if (!cap || typeof cap !== "object") return null;
  const edgeY = (th) => {
    const pts = [[0, fringe && cap.fringe !== undefined ? cap.fringe : cap.front ?? Q.hairline + .01], [45, cap.temple ?? .025], [90, cap.side ?? -.01], [135, cap.back ?? ((cap.side ?? -.01) + (cap.nape ?? -.07)) / 2], [180, cap.nape ?? -.07]];
    for (let i = 1; i < pts.length; i++) if (th <= pts[i][0]) return lerp(pts[i - 1][1], pts[i][1], (th - pts[i - 1][0]) / (pts[i][0] - pts[i - 1][0]));
    return pts[pts.length - 1][1];
  };
  // (thinning toward the edge: hair lies flat along its hairline, no shelf of it)
  const thickAt = (y, th) => ((cap.thick ?? .012) + (cap.crown ?? .01) * Math.max(0, Math.min(1, (y + .03) / .1)) * (.6 + .4 * Math.min(1, th / 90)))
    * (.3 + .7 * Math.max(0, Math.min(1, (y - edgeY(th)) / .035)));
  return { edgeY, thickAt, top: cap.top };
}
export function hairGeometry(p, P, emitFor, prims) {
  const H = headGrid(p, P), { Q, S, lv, grid, cols, nrm, R, C, skinAt, yTop } = H;
  const hair = emitFor("hair"), r = rng((p.seed ?? 1) * 7919 + 3);
  // how far out of the skull a point is: the ring at its height is a superellipse of the level's front, back and
  // side depths (as face.js draws it); 1 on the skin, less inside
  const rho = (q) => {
    const l = H.levelAt(Math.max(H.yBot, Math.min(H.yTop, q[1]))), ax = Math.max(.01, q[0] >= 0 ? l.f : Math.abs(l.b)), n = 2.3;
    return Math.pow(Math.pow(Math.abs(q[0]) / ax, n) + Math.pow(Math.abs(q[2]) / Math.max(.01, l.s), n), 1 / n);
  };
  const outward = (q) => norm([q[0], 0, q[2]]);
  // OFF THE BODY: below the chin, hair lies over the neck and then the shoulders and the back -- a point inside the
  // body's section there (an ellipse growing from the neck's to the shoulders' over 12cm, in the head's canonical
  // frame) is pushed out onto it, so long hair falls over the back rather than into the dress
  const offBody = (q, out = 1.04) => {   // (out: how far over the body's section -- the strands a little over a sheet under them)
    const yN = -.05;   // (from the nape down: the back of the neck and the collar are there before the chin is)
    if (q[1] > yN) return q;
    const t = Math.min(1, (yN - q[1]) / .12), cx = -.015, a = lerp(.06, .145, t), b = lerp(.065, .21, t);
    const k = Math.hypot((q[0] - cx) / a, q[2] / b);
    return k < out && k > 1e-6 ? [cx + (q[0] - cx) * out / k, q[1], q[2] * out / k] : q;
  };
  // a ribbon along a polyline: `w` wide at the root tapering to the tip, its face turned out from the head
  const ribbon = (pts, w0, w1, uv0) => {
    const ids = [];
    for (let i = 0; i < pts.length; i++) {
      const t = i / (pts.length - 1), w = lerp(w0, w1, t);
      const tan = norm(sub(pts[Math.min(pts.length - 1, i + 1)], pts[Math.max(0, i - 1)]));
      let out = outward(pts[i]); out = norm(sub(out, mul(tan, dot(out, tan))));
      if (Math.hypot(...out) < .5) out = [1, 0, 0];
      const across = norm(cross(tan, out));
      const a = add(pts[i], mul(across, w / 2)), b = sub(pts[i], mul(across, w / 2));
      ids.push([hair.vert(mul(a, S), out, [uv0, t]), hair.vert(mul(b, S), out, [uv0 + .02, t])]);
    }
    for (let i = 0; i + 1 < pts.length; i++) hair.quad(ids[i][0], ids[i][1], ids[i + 1][1], ids[i + 1][0]);
  };
  const COMB = { down: [0, -1, 0], back: [-1, -.3, 0], forward: [1, -.3, 0], out: [0, 0, 0], up: [0, 1, 0] };
  const combOf = (c, sg) => { const v = Array.isArray(c) ? c : COMB[c ?? "down"] ?? [0, -1, 0]; return [v[0], v[1], v[2] * (sg ?? 1)]; };
  // one strand from a scalp point q with normal n
  const grow = (q, n0, g, sg, seed) => {
    const n = Math.hypot(...n0) < .5 ? [0, 1, 0] : n0;   // (the crown's vertex has no normal of its own: up)
    const th = Math.atan2(Math.abs(q[2]), q[0]) / DEG;   // its angle round the head, 0 the forehead .. 180 the nape
    const len = (Array.isArray(g.length) ? lerp(g.length[0], g.length[1], th / 180) : g.length ?? .1) * (1 + (r() - .5) * (g.vary ?? .15));
    const seg = Math.max(2, Math.round(g.seg ?? 6)), step = len / seg;
    const comb = combOf(g.comb, sg), hang = g.hang ?? .8, lift = g.lift ?? .006;
    const wave = g.wave, curl = g.curl, ph = seed * 6.28;
    const to = g.to ? [g.to[0], g.to[1], g.to[2] * (g.toMirror ? (sg ?? 1) : 1)] : null;   // (gathered at a point -- one a side when mirrored)
    // it leaves the scalp ALONG it: the comb's direction laid on the surface (at the crown, where "down" has no
    // way along the skin, backward), a little off the skin; "out" stands along the normal
    let tang = sub(comb, mul(n, dot(comb, n)));
    if (Math.hypot(...tang) < .1) tang = sub([-1, 0, 0], mul(n, dot([-1, 0, 0], n)));
    let pos = add(q, mul(n, lift)), dir = Math.hypot(...comb) < .1 ? n : norm(add(norm(tang), mul(n, g.off ?? .2)));
    if (to) dir = norm(add(norm(sub(to, pos)), mul(norm(tang), .5)));
    const pts = [pos];
    // the strand's own frame for its wave and curl: across (round the head) and out
    for (let i = 1; i <= seg; i++) {
      const t = i / seg;
      if (to) { dir = norm(add(mul(dir, .5), mul(norm(sub(to, pos)), .5))); }
      else dir = norm(add(dir, mul([0, -1, 0], hang * step * 14)));                   // gravity bends it down (most of the way within ~10 cm)
      let next = add(pos, mul(dir, step));
      // off the skull: a point that would pass inside is pushed out to just over the skin
      if (!to && next[1] > H.yBot - .03) {
        const k = rho(next);
        if (k < 1.06 && k > 1e-4) { next = [next[0] * 1.06 / k, next[1], next[2] * 1.06 / k]; dir = norm(sub(next, pos)); }
      }
      pos = to ? next : offBody(next, 1.09);
      let q2 = pos;
      if (wave) { const across = norm(cross(dir, outward(pos))); q2 = add(q2, mul(across, wave.amp * Math.sin(t * len / wave.per * 6.2832 + ph))); }
      if (curl) { const across = norm(cross(dir, outward(pos))), o = outward(pos), a = t * len / curl.per * 6.2832 + ph; q2 = add(q2, add(mul(across, curl.r * Math.cos(a)), mul(o, curl.r * (Math.sin(a) + 1) * .5))); }
      pts.push(q2);
    }
    ribbon(pts, g.width?.[0] ?? .02, g.width?.[1] ?? .01, seed);
  };
  // THE CAP: the hair's body as one rounded shell over the skull (the grid's own rows and rings, pushed out by its
  // thickness, closed by a rim down to the skin at its EDGE), reaching further down the sides and the back than the
  // skin's hairline -- over the ears, to the nape -- as hair does; the strands hang from its edge. `cap`:
  //   front: y of the edge at the forehead, temple: at 45 degrees round, side: at the ears (90), nape: at the back (180)
  //   (the edge runs straight between), top: y above which the skull is bare (a tonsure), thick: metres off the skin,
  //   crown: metres more at the crown and the back (its volume), fringe: the front edge's y when the face has a fringe
  const cap = p.cap ?? null, CS = capShape(cap, Q, P.fringe), edgeY = CS?.edgeY ?? null, thickAt = CS?.thickAt;
  if (cap) {
    const top = cap.top ?? yTop + 1, V = new Map(), skin = new Map();   // per column: its vertices top to bottom (out) and the skin edge vertex
    const colOf = (c) => {
      if (V.has(c)) return V.get(c);
      const [th, sg] = cols[c], ye = edgeY(th), out = [];
      for (let rr = 0; rr < R; rr++) {
        const q = grid[rr][c];
        if (q[1] <= ye || q[1] >= top) continue;
        if (rr === 0) { out.push({ y: q[1], id: V.get("vertex") ?? hair.vert(mul([q[0], q[1] + thickAt(q[1], 0), q[2]], S), [0, 1, 0], [0, 1]) }); V.set("vertex", out[0].id); continue; }
        const n = nrm(rr, c), t = thickAt(q[1], th);
        out.push({ y: q[1], id: hair.vert(mul(add(q, mul(n, t)), S), n, [th / 180, q[1]]) });
      }
      if (ye < top) {   // the edge: on the skin's line, pushed out, and a rim vertex on the skin itself
        const q = skinAt(ye, th, sg), n = norm(add(outward(q), [0, -.3, 0])), t = thickAt(ye, th);
        out.push({ y: ye, id: hair.vert(mul(add(q, mul(n, t)), S), n, [th / 180, ye]) });
        skin.set(c, hair.vert(mul(q, S), [n[0] * .3, -1, n[2] * .3], [th / 180, ye]));
      }
      if (cap.top !== undefined && out.length) {   // a tonsure's inner rim: down to the skin at the top too
        const q = skinAt(Math.min(top, yTop - .001), th, sg);
        out.unshift({ y: top, id: hair.vert(mul(q, S), [0, 1, 0], [th / 180, top]), rim: true });
      }
      V.set(c, out);
      return out;
    };
    for (let c = 0; c < C; c++) {
      const A = colOf(c), B = colOf((c + 1) % C);
      if (!A.length || !B.length) continue;
      let i = 0, j = 0;   // zip the two columns top to bottom
      while (i < A.length - 1 || j < B.length - 1) {
        const stepA = j >= B.length - 1 || (i < A.length - 1 && A[i + 1].y >= B[j + 1].y);
        if (stepA) { if (A[i].id !== B[j].id || A[i + 1].id !== B[j].id) hair.tri(A[i].id, A[i + 1].id, B[j].id); i++; }
        else { if (A[i].id !== B[j].id || B[j + 1].id !== A[i].id) hair.tri(A[i].id, B[j + 1].id, B[j].id); j++; }
      }
      if (skin.has(c) && skin.has((c + 1) % C)) hair.quad(A[A.length - 1].id, skin.get(c), skin.get((c + 1) % C), B[B.length - 1].id);
    }
  }
  // SHEETS (2026-10-03): the hair as a CLOTH hung from the cap's edge -- a wavy sheet, not strands. Its first ring IS
  // the cap's edge (the same points, column for column: where the hair leaves the head), and every further ring is a
  // horizontal CUT a `drop` lower, standing `out` off the head (the hair's volume), ZIG-ZAGGED: its points alternately
  // out by `zig` and in, and the out ones down by `zy` -- so between two cuts whose zig-zags are half a tooth apart
  // (`phase`) the cloth folds into facets, pyramid-shaped LOCKS, and the last cut's points are the locks' tips (the
  // drawn, "manga" hair). A ring `onHead` lies back on the skin (a puff between two edges on the head). It covers the
  // columns `region.th` round from the front (both sides): from 60 or so it leaves the face open; [0, 50] is a fringe.
  //   sheet: { region: { th: [from, to] }, sub: points a column (2: a tooth a column), double: both faces,
  //            rings: [{ drop: metres below the edge (or [front, back]), out, zig, zy, phase: 0 | 1, vary, onHead }] }
  for (const g of cap ? p.sheets ?? [] : []) {
    if (g.when && !P[g.when]) continue;
    if (g.unless && P[g.unless]) continue;
    const t0 = g.region?.th?.[0] ?? 60, t1 = g.region?.th?.[1] ?? 180, per = Math.max(1, Math.round(g.sub ?? 2));
    const inArc = (c) => cols[c][0] >= t0 - 1e-6 && cols[c][0] <= t1 + 1e-6;
    // the arc's columns in order round the head (one run: through the back, or through the front for a fringe)
    let start = 0;
    while (start < C && !(inArc(start) && !inArc((start - 1 + C) % C))) start++;
    const closed = start === C, arc = [];
    for (let i = 0, c = closed ? 0 : start; i < C && inArc(c); i++, c = (c + 1) % C) arc.push(c);
    if (arc.length < 2) continue;
    if (closed) arc.push(arc[0]);
    const val = (v, th, d = 0) => v === undefined ? d : Array.isArray(v) ? lerp(v[0], v[1], th / 180) : v;
    // a ring's point at a column, before its zig-zag: under the edge by its drop, hanging straight down from the
    // widest the head is between the edge and there (hair falls past the jaw, not in to the neck), `out` off it
    const base = (c, ring) => {
      const [th, sg] = cols[c], ye = edgeY(th), t = thickAt(ye, th);
      if (!ring) { const q = skinAt(ye, th, sg), n = norm(add(outward(q), [0, -.3, 0])); return add(q, mul(n, t)); }
      const y = ye - val(ring.drop, th, .05);
      let q = skinAt(Math.max(H.yBot + .005, Math.min(yTop, y)), th, sg);
      if (!ring.onHead) for (let i = 0; i <= 4; i++) {
        const qi = skinAt(Math.max(H.yBot + .005, lerp(ye, Math.max(y, H.yBot + .005), i / 4)), th, sg);
        if (Math.hypot(qi[0], qi[2]) > Math.hypot(q[0], q[2])) q = qi;
      }
      const o = outward(q);
      return add([q[0], y, q[2]], mul(o, t + (ring.onHead ? 0 : val(ring.out, th, .01))));
    };
    const rings = [null, ...(g.rings ?? [])], raw = [], rows = [];
    rings.forEach((ring, k) => {
      const row = [];
      for (let i = 0; i < arc.length; i++) {   // (each column, and `per` - 1 points on to the next; the last alone)
        const A = base(arc[i], ring), B = i + 1 < arc.length ? base(arc[i + 1], ring) : null;
        for (let u = 0; u < (B ? per : 1); u++) {
          let q = B ? add(A, mul(sub(B, A), u / per)) : A;
          const j = row.length, th = B ? lerp(cols[arc[i]][0], cols[arc[i + 1]][0], u / per) : cols[arc[i]][0];
          if (ring && !ring.onHead) {   // the zig-zag: a tooth's point out and down, its notch in
            const peak = (j + (ring.phase ?? 0)) % 2 === 0, jit = 1 + (r() - .5) * (ring.vary ?? .4);
            q = add(q, mul(outward(q), (peak ? 1 : -.4) * val(ring.zig, th) * jit));
            if (peak) q = add(q, [0, -val(ring.zy, th) * jit, 0]);
          }
          row.push({ q, th });
        }
      }
      raw.push(row);
    });
    // (between two cuts, rows every 3.5cm, point by point -- the locks' facets keep their shape -- each pushed off the
    //  body: a long fall over the shoulders bends with them instead of cutting through between two cuts)
    raw.forEach((row, k) => {
      const next = raw[k + 1], m = next ? Math.max(0, Math.ceil(Math.abs(row[0].q[1] - next[0].q[1]) / .035) - 1) : 0;
      for (let i = 0; i <= m; i++) {
        const u = i / (m + 1), pts = i ? row.map((a, j) => ({ q: add(a.q, mul(sub(next[j].q, a.q), u)), th: a.th })) : row;
        rows.push(pts.map(({ q, th }) => { const o = k || i ? offBody(q) : q; return hair.vert(mul(o, S), norm(add(outward(o), [0, k || i ? -.15 : .3, 0])), [th / 180, o[1]]); }));
      }
    });
    for (let k = 0; k + 1 < rows.length; k++) {
      const a = rows[k], b = rows[k + 1], n = Math.min(a.length, b.length);
      for (let j = 0; j + 1 < n; j++) {
        hair.quad(a[j], a[j + 1], b[j + 1], b[j]);
        if (g.double !== false) hair.quad(a[j + 1], a[j], b[j], b[j + 1]);   // (its inside: seen under the hem, past the face)
      }
    }
  }
  // SPIKES (2026-10-03): hair standing in THORNS -- a lattice of its own over the cap (`rows` from the cap's edge up toward
  // the crown, `cols` over every 180 degrees round), each point on the cap but a sparse checkerboard of them -- every
  // `every`-th column on every other row, the rows' spikes half a step apart -- pushed far out: `length` [front, back],
  // along the head's normal bent `blend` of the way toward `comb` (back and up, up, out), `vary` its jitter. A far point's
  // neighbours stay on the cap, so each is the apex of a sharp pyramid; the edge rows lie on the cap's edge, so the
  // spikes rise from the hair and fall back to it. Flat facets (each triangle its own normal: the spike's sides read).
  //   spikes: { region: { th: [from, to], y: [lo, hi] }, rows, cols, every, length, comb, blend, vary, top }
  for (const g of cap ? p.spikes ?? [] : []) {
    if (g.when && !P[g.when]) continue;
    if (g.unless && P[g.unless]) continue;
    const t0 = g.region?.th?.[0] ?? 0, t1 = g.region?.th?.[1] ?? 180, NR = Math.max(3, Math.round(g.rows ?? 8)), M = Math.max(2, Math.round((g.cols ?? 16) * (t1 - t0) / 180));
    const every = Math.max(2, Math.round(g.every ?? 3)), yHi = Math.min(g.region?.y?.[1] ?? 1, (g.top ?? yTop - .002));   // (the last ring ~5 degrees from the crown: its thorn closes it)
    // the columns round: ARCS of [th, side] -- all the way round (a ring), through the back (both sides meet at 180), through
    // the front (they meet at 0), or one on each side
    const ths = Array.from({ length: M + 1 }, (_, k) => t0 + (t1 - t0) * k / M);
    const R_ = ths.map((th) => [th, 1]), Lf = ths.map((th) => [th, -1]);
    const ring = t0 <= 0 && t1 >= 180;
    const arcs = ring ? [[...R_, ...Lf.slice(1, -1).reverse()]] : t1 >= 180 ? [[...R_, ...Lf.slice(0, -1).reverse()]]
               : t0 <= 0 ? [[...Lf.slice(1).reverse(), ...R_]] : [R_, Lf.slice().reverse()];
    const len = (th) => (Array.isArray(g.length) ? lerp(g.length[0], g.length[1], th / 180) : g.length ?? .1);
    for (const cs of arcs) {
      // (the lattice, thorns.js: the cap's surface by height and angle; the spikes along the normal bent toward the comb;
      //  a ring's crown closed by one more thorn standing up from it)
      const b = g.blend ?? .5, dirOf = (n, sg) => norm(add(mul(n, 1 - b), mul(norm(combOf(g.comb ?? [-1, .5, 0], sg)), b)));
      thornLattice({ NR, NC: cs.length, ring, every,
        // (rows evenly along the skull's curve, not in height -- near the top a step in height is a long way across, and the
        //  last ring would stand wide open: by the angle from the crown, the last a few degrees from it)
        at: (i, j) => { const [th, sg] = cs[j], ye = Math.max(edgeY(th), g.region?.y?.[0] ?? -1), Rh = yTop + .005;
                        const pe = Math.acos(Math.max(-1, Math.min(1, ye / Rh))), pt = Math.acos(Math.max(-1, Math.min(1, yHi / Rh)));
                        const y = Rh * Math.cos(lerp(pe, pt, i / NR)), q = skinAt(y, th, sg), n = norm(q);
                        return { q: add(q, mul(n, thickAt(y, th) + .004)), n, u: j * .37, v: y }; },
        spike: (i, j, n) => { const [th, sg] = cs[j]; return { d: dirOf(n, sg), L: len(th) * (1 + (r() - .5) * (g.vary ?? .35)) }; },
        apex: (mid) => ({ d: dirOf(norm(mid), 1), L: len(90) * (1 + (r() - .5) * (g.vary ?? .35)) }),
        tri: (A, B, C, n) => { const id = [A, B, C].map((X) => hair.vert(mul(X.q, S), n, [X.u, X.v])); hair.tri(id[0], id[1], id[2]); } });
    }
  }
  // the scalp: the grid's points above the hairline (as the face draws them: the hairline runs down round the temples)
  const onScalp = (rr, c) => { const l = lv[rr], [th] = cols[c], back = th / 180; return l.y >= Q.hairline - .12 * Math.pow(back, 2.5); };
  for (const g of p.strands ?? []) {
    if (g.when && !P[g.when]) continue;   // (a group the face has not got: a fringe)
    if (g.unless && P[g.unless]) continue; // (...or has: the front parted only without one)
    const reg = g.region ?? {}, y0 = reg.y?.[0] ?? -1, y1 = reg.y?.[1] ?? 1, t0 = reg.th?.[0] ?? 0, t1 = reg.th?.[1] ?? 180, every = Math.max(1, Math.round(g.every ?? 1));
    let k = 0;
    if (g.edge && cap) {   // from the cap's edge: one strand a column along it (and `extra` between), hanging from under the cap
      for (let c = 0; c < C; c++) {
        const [th, sg] = cols[c], c2 = (c + 1) % C, [th2, sg2] = cols[c2];
        if (th < t0 || th > t1 || (sg !== sg2 && th2 !== th)) { if (th < t0 || th > t1) continue; }
        if (k++ % every) continue;
        for (let e = 0; e <= (g.extra ?? 0); e++) {
          const u = e === 0 ? 0 : r(), thm = th + (th2 - th) * u, ye = edgeY(thm), q = skinAt(ye, thm, sg), n = norm(add(outward(q), [0, -.2, 0]));
          grow(add(q, mul(n, thickAt(ye, thm) * .6)), n, { ...g, lift: 0 }, sg, r());
        }
      }
      continue;
    }
    for (let rr = 0; rr < R; rr++) for (let c = 0; c < C; c++) {
      const [th, sg] = cols[c], q = grid[rr][c];
      if (!onScalp(rr, c) || q[1] < y0 || q[1] > y1 || th < t0 || th > t1) continue;
      if (rr === 0 && c > 0) continue;   // (the vertex once)
      if (k++ % every) continue;
      grow(q, nrm(rr, c), g, sg, r());
      for (let e = 0; e < (g.extra ?? 0); e++) {   // strands between the points: a little off it along the ring
        const c2 = (c + 1) % C, u = r();
        const qm = [lerp(q[0], grid[rr][c2][0], u), lerp(q[1], grid[rr][c2][1], u), lerp(q[2], grid[rr][c2][2], u)];
        grow(qm, nrm(rr, c), g, sg, r());
      }
    }
  }
  // LOCKS: single long strands from named places (in the face's frame), `n` of them a little apart
  for (const L of p.locks ?? []) {
    for (const sg of L.mirror === false ? [1] : [1, -1]) for (let i = 0; i < (L.n ?? 1); i++) {
      const q = skinAt(L.at[1], L.at[0] + i * 4, sg), n = norm(outward(q));
      grow(q, n, { ...L, comb: L.comb ?? "down" }, sg, r());
    }
  }
  // what GATHERS the hair: a rope (a ponytail, a plait: three ribbons twisted round its path), a knot, a bun
  for (const x0 of p.gather ?? []) for (const sg of x0.mirror ? [1, -1] : [1]) {
    const x = { ...x0, at: [x0.at[0], x0.at[1], x0.at[2] * sg], dir: x0.dir ? [x0.dir[0], x0.dir[1], x0.dir[2] * sg] : x0.dir };
    const at = x.at;
    if (x.kind === "rope" || x.kind === "plait") {
      const len = x.length ?? .3, seg = 8, w = x.width ?? .05, pts = [];
      let pos = at.slice(), dir = norm(x.dir ?? [-.3, -1, 0]);
      for (let i = 0; i <= seg; i++) { pts.push(pos.slice()); dir = norm(add(dir, mul([0, -1, 0], (x.hang ?? .6) * len / seg * 3))); pos = add(pos, mul(dir, len / seg)); }
      if (x.kind === "rope") prims.tube("hair", pts.map((q) => mul(q, S)), [w * .45 * S, w * .55 * S, w * .3 * S]);   // (fuller below the tie than at it, then to a point)
      else for (let s3 = 0; s3 < 3; s3++) {   // a plait: three strands winding round the path, a third of a turn apart
        const tw = pts.map((q, i) => { const t = i / seg, a = t * len / (x.per ?? .08) * 6.2832 + s3 * 2.094, d = norm(sub(pts[Math.min(seg, i + 1)], pts[Math.max(0, i - 1)])), o = norm(cross(d, [0, 0, 1]) ), b = norm(cross(d, o));
          return mul(add(q, add(mul(o, Math.cos(a) * w * .3), mul(b, Math.sin(a) * w * .3))), S); });
        prims.tube("hair", tw, [w * .28 * S, w * .26 * S, w * .15 * S]);
      }
      if (x.tie) { const tie = emitFor("tie"); const t0 = pts[0], d = norm(sub(pts[1], pts[0])); ringAt(tie, t0, d, w * .55, .012 * S); }
    }
    if (x.kind === "bun" || x.kind === "knot") {
      const rr = x.r ?? .045, k = 10, prof = [];
      for (let i = 0; i <= 6; i++) { const a = -Math.PI / 2 + i / 6 * Math.PI; prof.push([rr * Math.cos(a), rr * Math.sin(a) * (x.kind === "knot" ? 1.3 : .8)]); }
      prims.lathe("hair", prof.map(([a, b]) => [a * S, b * S]), k, { capLo: false, capHi: false }, mul(at, S));
      if (x.tie) { const tie = emitFor("tie"); ringAt(tie, at, x.dir ?? [-1, 0, 0], rr * .7, .012 * S); }
    }
  }
  function ringAt(em, c, d, rad, tube) {   // a band round a rope (the tie): a short tube
    const dn = norm(d), o0 = norm(cross(dn, Math.abs(dn[1]) < .9 ? [0, 1, 0] : [1, 0, 0])), o1 = cross(dn, o0), k = 8, ids = [];
    for (let i = 0; i <= k; i++) { const a = i / k * 6.2832, n = add(mul(o0, Math.cos(a)), mul(o1, Math.sin(a))); const q = add(c, mul(n, rad)); ids.push([em.vert(mul(add(q, mul(dn, -.01)), S), n, [i / k, 0]), em.vert(mul(add(q, mul(dn, .01)), S), n, [i / k, 1])]); }
    for (let i = 0; i < k; i++) em.quad(ids[i][0], ids[i][1], ids[i + 1][1], ids[i + 1][0]);
  }
}
