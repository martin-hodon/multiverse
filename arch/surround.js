// THE WINDOW SURROUND: how a classical facade dresses an opening -- the counterpart of the Gothic wimperg, and like it
// drawn from the opening it stands round, nothing placed by eye:
//   the ARCHITRAVE, a flat band as wide as a seventh of the opening, framing its jambs and its head (following an
//   arch round, a keystone at its crown);
//   the SILL under a window, a slab reaching past the architrave and standing out to shed the rain;
//   over the head a FRIEZE and a CORNICE -- and on the cornice a PEDIMENT: TRIANGULAR (its rakes at the classical
//   pitch), SEGMENTAL (an arc as wide as the cornice, rising a quarter of its half), or ALTERNATE, the two in turn
//   along the row and the middle one triangular, as Roman palace fronts have them. A head that would rise over the
//   wall's top is left at its cornice, or at the architrave alone.
// `spec`: { band, depth, sill, head: "pediment" | "cornice" | false, pediment: "triangular" | "segmental" | "alternate",
// pitch, keystone, side }. `side` 1 sets it on the face's back (as a wimperg's). `o.turn` (set by the row): which of the alternate pediments it takes.
import { barsMesh } from "./tracery.js";
import { proudOf } from "./wimperg.js";

export function surroundMesh(o, spec, map, m, top = Infinity) {
  if (o.a < .25) return m;
  if (spec.style === "romanesque") return romanesqueMesh(o, spec, map, m, top);
  const C = o.curve, rise = Math.max(0, ...C.map(([, y]) => y)), S = o.springing, x0 = o.at - o.a, x1 = o.at + o.a;
  const b = spec.band ?? Math.max(.12, Math.min(.4, o.a * 2 / 7)), d = spec.depth ?? b * .5;
  const { at, slab: slab_ } = proudOf(map, spec.side ? 1 : 0, m);
  const slab = (pts, d0, d1) => slab_(pts, d0, d1, false);    // (all of it on the wall's face, under its top: no backs)
  const window = o.sill > .3;
  const foot = window ? o.sill : 0;
  // THE ARCHITRAVE: the jambs up to the springing, then the head -- a lintel over a flat one, a band round an arch
  if (rise < 1e-3) {
    slab([[x0 - b, foot], [x0, foot], [x0, S], [x0 - b, S]], 0, d);
    slab([[x1, foot], [x1 + b, foot], [x1 + b, S], [x1, S]], 0, d);
    slab([[x0 - b, S], [x1 + b, S], [x1 + b, S + b], [x0 - b, S + b]], 0, d);
  } else {
    slab([[x0 - b, foot], [x0, foot], [x0, S], [x0 - b, S]], 0, d);
    slab([[x1, foot], [x1 + b, foot], [x1 + b, S], [x1, S]], 0, d);
    const band = C.map(([x, y], i) => {
      const p = C[Math.max(0, i - 1)], q = C[Math.min(C.length - 1, i + 1)], tx = q[0] - p[0], ty = q[1] - p[1], l = Math.hypot(tx, ty) || 1;
      return [o.at + x - ty / l * b / 2, S + y + tx / l * b / 2];
    });
    barsMesh([{ pts: band, closed: false }], b, (x, y, s) => at(x, y, (1 - s) * d), 0, 1, m);
    // the KEYSTONE locking the arch at its crown, standing out of the band
    if (spec.keystone !== false) {
      const k = b * .6, yc = S + rise;
      slab([[o.at - k * .7, yc - b * .2], [o.at + k * .7, yc - b * .2], [o.at + k, yc + b * 1.3], [o.at - k, yc + b * 1.3]], 0, d * 1.5);
    }
  }
  // THE SILL: a window's, wider than the architrave and standing out further
  if (window && spec.sill !== false) slab([[x0 - b * 1.4, foot - b * .6], [x1 + b * 1.4, foot - b * .6], [x1 + b * 1.4, foot], [x0 - b * 1.4, foot]], 0, d * 2);
  // THE HEAD: frieze, cornice, pediment -- each only if it stays under the wall's top
  const head = spec.head ?? "pediment";
  if (!head) return m;
  const yF = S + rise + b * (rise < 1e-3 ? 1 : 1.3), fh = b * .9, ch = b * .7, co = b * .7;
  const xl = x0 - b - co, xr = x1 + b + co, yC = yF + fh + ch;
  if (yC > top - .05) return m;
  slab([[x0 - b, yF], [x1 + b, yF], [x1 + b, yF + fh], [x0 - b, yF + fh]], 0, d * .7);
  slab([[xl, yF + fh], [xr, yF + fh], [xr, yC], [xl, yC]], 0, d + co);
  if (head !== "pediment") return m;
  const kind = spec.pediment === "alternate" ? ((o.turn ?? 0) % 2 ? "segmental" : "triangular") : spec.pediment ?? "triangular";
  const half = (xr - xl) / 2, mid = (xl + xr) / 2, rk = ch * .9;   // (the raking cornice: a little lighter than the level one)
  if (kind === "segmental") {
    const h = half * .25, R = (half * half + h * h) / (2 * h), yc = yC + h - R, a = Math.asin(half / R);
    if (yC + h + rk > top - .05) return m;
    const n = 6, arc = Array.from({ length: n + 1 }, (_, i) => { const t = -a + 2 * a * i / n; return [mid + R * Math.sin(t), yc + R * Math.cos(t)]; });
    // the tympanum, and the arc's cornice over it
    const inner = arc.map(([x, y]) => [mid + (x - mid) * (R - rk) / R, yc + (y - yc) * (R - rk) / R]);
    slab([[inner[0][0], yC], ...inner.slice(1, -1), [inner[n][0], yC]], 0, d * .7);
    barsMesh([{ pts: arc.map(([x, y]) => [mid + (x - mid) * (R - rk / 2) / R, yc + (y - yc) * (R - rk / 2) / R]), closed: false }], rk,
             (x, y, s) => at(x, y, (1 - s) * (d + co)), 0, 1, m);
  } else {
    const t = Math.tan((spec.pitch ?? 22.5) * Math.PI / 180), h = half * t, s = Math.sqrt(1 + t * t);
    if (yC + h + rk * s > top - .05) return m;
    const ap = [mid, yC + h], dy = rk * s;      // (a raking cornice `rk` thick across its own slope)
    slab([[xl, yC], [mid, yC + h - dy], [xr, yC]], 0, d * .7);
    slab([[xl, yC], [ap[0], ap[1]], [ap[0], ap[1] + dy], [xl, yC + dy]], 0, d + co);
    slab([[ap[0], ap[1]], [xr, yC], [xr, yC + dy], [ap[0], ap[1] + dy]], 0, d + co);
  }
  return m;
}

// THE ROMANESQUE OPENING: not framed but RECESSED -- stepped toward the opening in ORDERS, each a strip of jamb
// round which its band of the ARCHIVOLT turns; the outer orders stand furthest out, so the arch reads as cut into
// the wall in steps. In the angle of each step (where an order's strip meets the next one out) a NOOK SHAFT stands
// on its base, under a CUSHION CAPITAL (a block cut from a cube down to the round of the shaft), and the shaft goes
// on over the capital as a ROLL round the head; over the capitals an IMPOST runs across all the orders of the jamb,
// and the arch springs from it. Every measure from the opening: the order's step a ninth of its span, never wider
// than the pier beside it allows (`o.room`, the free wall each side -- a neighbour's half of a shared pier), so an
// arcade of them shares its piers and they never meet; the orders as many as fit under the wall's top.
// `spec`: { style: "romanesque", orders (2), band, depth, shafts (true), side }.
function romanesqueMesh(o, spec, map, m, top) {
  // (the head's curve no finer than its size asks: a segment about 12cm round, six at least -- a belfry's little arch
  //  needs no more points than a portal's)
  let C = o.curve;
  { let L = 0; for (let i = 1; i < C.length; i++) L += Math.hypot(C[i][0] - C[i - 1][0], C[i][1] - C[i - 1][1]);
    const N = Math.max(6, Math.ceil(L / .12));
    if (C.length - 1 > N) C = Array.from({ length: N + 1 }, (_, i) => C[Math.round(i * (C.length - 1) / N)]); }
  const rise = Math.max(0, ...C.map(([, y]) => y)), S = o.springing, x0 = o.at - o.a, x1 = o.at + o.a;
  const room = Math.min(...(o.room ?? [Infinity])) - .02;
  let n = Math.max(1, spec.orders ?? 2), b = spec.band ?? Math.max(.15, Math.min(.45, o.a / 4.5));
  b = Math.min(b, room / (n + .4));
  while (n > 1 && S + rise + n * b > top - .05) n--;
  if (b < .06 || S + rise + n * b > top - .05) return m;
  const d = spec.depth ?? b * .7, r = Math.min(b * .33, d * .48), foot = o.sill > .3 ? o.sill : 0;
  const { at, poly, slab: slab_ } = proudOf(map, spec.side ? 1 : 0, m);
  const slab = (pts, d0, d1) => slab_(pts, d0, d1, false);
  // (a ROLL: a half-round `r` along a line in the face, its axis `dc` proud -- a shaft up a jamb, a moulding round a head)
  const roll = (path, dc, K = r < .06 ? 3 : 4) => {
    const N = path.length, rings = path.map((p, i) => {
      const a = path[Math.max(0, i - 1)], c = path[Math.min(N - 1, i + 1)], l = Math.hypot(c[0] - a[0], c[1] - a[1]) || 1, nx = (c[1] - a[1]) / l, ny = -(c[0] - a[0]) / l;
      return Array.from({ length: K + 1 }, (_, j) => { const t = Math.PI * j / K; return at(p[0] + nx * r * Math.cos(t), p[1] + ny * r * Math.cos(t), dc + r * Math.sin(t)); });
    });
    for (let i = 0; i + 1 < N; i++) {
      const ref = at((path[i][0] + path[i + 1][0]) / 2, (path[i][1] + path[i + 1][1]) / 2, dc);
      for (let j = 0; j < K; j++) poly([rings[i][j], rings[i + 1][j], rings[i + 1][j + 1], rings[i][j + 1]], ref);
    }
  };
  const ih = b * .5, ch = b * 1.1, bh = b * .5, shafts = spec.shafts !== false && S - ih - ch - bh - foot > b * 2;
  // THE IMPOST under the springing, across all the orders of each jamb, standing over the capitals
  const xo = n * b + b * .4, di = n * d + (shafts ? 2.4 * r : 0) + b * .1;
  slab([[x0 - xo, S - ih], [x0, S - ih], [x0, S], [x0 - xo, S]], 0, di);
  slab([[x1, S - ih], [x1 + xo, S - ih], [x1 + xo, S], [x1, S]], 0, di);
  for (let k = 0; k < n; k++) {
    const dk = (k + 1) * d;
    for (const sg of [-1, 1]) {
      // the order's STRIP of jamb, from the floor or the sill to the impost
      const e0 = sg < 0 ? x0 - k * b : x1 + k * b, e1 = e0 + sg * b, lo = Math.min(e0, e1), hi = Math.max(e0, e1);
      slab([[lo, foot], [hi, foot], [hi, S - ih], [lo, S - ih]], 0, dk);
      if (!shafts) continue;
      // its NOOK SHAFT in the angle at its outer edge, on its base, under its cushion capital
      const c = e1 - sg * r, dc = dk;
      slab([[c - 1.25 * r, foot], [c + 1.25 * r, foot], [c + 1.25 * r, foot + bh], [c - 1.25 * r, foot + bh]], dc, dc + 2.5 * r);
      roll([[c, foot + bh], [c, S - ih - ch]], dc);
      slab([[c - r, S - ih - ch], [c + r, S - ih - ch], [c + 1.3 * r, S - ih - ch * .45], [c + 1.3 * r, S - ih], [c - 1.3 * r, S - ih], [c - 1.3 * r, S - ih - ch * .45]], dc, dc + 2.4 * r);
    }
    // the ARCHIVOLT: the order's band round the head (a lintel over a flat one), and the ROLL its shafts go on as
    if (rise < 1e-3) { slab([[x0 - (k + 1) * b, S + k * b], [x1 + (k + 1) * b, S + k * b], [x1 + (k + 1) * b, S + (k + 1) * b], [x0 - (k + 1) * b, S + (k + 1) * b]], 0, dk); continue; }
    const off = (q) => C.map(([x, y], i) => {
      const p = C[Math.max(0, i - 1)], u = C[Math.min(C.length - 1, i + 1)], tx = u[0] - p[0], ty = u[1] - p[1], l = Math.hypot(tx, ty) || 1;
      return [o.at + x - ty / l * q, S + y + tx / l * q];
    });
    barsMesh([{ pts: off((k + .5) * b), closed: false }], b, (x, y, s) => at(x, y, (1 - s) * dk), 0, 1, m);
    if (shafts) roll(off((k + 1) * b - r), dk);
  }
  return m;
}
