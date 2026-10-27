// THE WIMPERG: the steep gable a Gothic mason set over a portal or a window, standing proud of the wall -- drawn from
// the arch under it, nothing placed by eye:
//   its two COPING ARMS spring at the arch's springing line, outside its archivolt (a band as wide as the coping round
//   the arch's extrados), and meet in a mitre on the axis; their pitch is the one asked (62 degrees by default),
//   steepened until the arms' inner edges clear the archivolt everywhere -- a flat arch under a tall narrow gable
//   keeps its pitch, a wide round one makes the gable steeper;
//   CROCKETS climb their outer edges, a leaf curling up from the stone every three copings' widths, and a FINIAL
//   stands on the apex;
//   in the FIELD between the archivolt and the arms, the largest circle that fits on the axis, a trefoil cusped in it:
//   blind tracery, a bar's depth proud of the wall.
// `spec`: { pitch, coping, depth, crockets, finial, field, side }. `side` 1 sets it on the face's back (`map`'s far
// side), for a wall whose outside is its back.
import { barsMesh } from "./tracery.js";

const circle = (c, r, n, turn = 0) => Array.from({ length: n }, (_, k) => { const t = turn + k * 2 * Math.PI / n; return [c[0] + r * Math.cos(t), c[1] + r * Math.sin(t)]; });

// THE GABLE'S LINES in the face's (x, y), from a laid-out opening (build.js wallFace: at, a, springing, curve): the
// arms' outer and inner lines, the field's circle and foils, and the sizes they were drawn with -- or null for an
// opening too small to carry one
export function wimpergLines(o, spec = {}, top = Infinity) {
  const C = o.curve, a = Math.max(o.a, ...C.map(([x]) => Math.abs(x))), S = o.springing, rise = Math.max(0, ...C.map(([, y]) => y));
  if (a < .3) return null;
  const b = spec.coping ?? Math.max(.22, Math.min(.7, a * .2));      // the coping's width, in the face
  const ring = b;                                                     // the archivolt round the arch
  // the archivolt's outer line: the arch's curve (left to right over the top) offset by `ring` along its outward
  // normal (-ty, tx)
  const off = (r) => C.map(([x, y], i) => {
    const p = C[Math.max(0, i - 1)], q = C[Math.min(C.length - 1, i + 1)], tx = q[0] - p[0], ty = q[1] - p[1], l = Math.hypot(tx, ty) || 1;
    return [x - ty / l * r, y + tx / l * r];
  });
  const out = off(ring);
  // THE ARMS' SPREAD from their pitch: wide enough that their inner edges stand a quarter coping clear of the
  // archivolt everywhere -- at a pointed arch's foot, where it rises straight, as well as over its crown -- and no
  // less than the archivolt's own foot. A gable whose apex would rise over the wall's `top` is tried flatter (a
  // flatter gable spreads wider but may stand lower), and is left off if no pitch down to 40 degrees keeps it in
  const m = b * .25;
  const spread = (th) => Math.max(a + ring + b / Math.sin(th), ...out.map(([x, y]) => Math.abs(x) + (y + m + b / Math.cos(th)) / Math.tan(th)));
  const apexOf = (th) => S + spread(th) * Math.tan(th);
  let pitch = (spec.pitch ?? 62) * Math.PI / 180;
  const roof = spec.top ?? top;
  if (apexOf(pitch) > roof) {
    for (let d = 60; d >= 40; d -= 2) { const th = d * Math.PI / 180; if (th < pitch && apexOf(th) < apexOf(pitch)) pitch = th; }
    if (apexOf(pitch) > roof) return null;
  }
  const H = spread(pitch), t = Math.tan(pitch), c = Math.cos(pitch), apex = S + H * t, apexIn = apex - b / c;
  const R = (x) => o.at + x;
  // the right arm, outer foot -> apex -> inner apex -> inner foot (the left the same, mirrored)
  const armR = [[R(H), S], [R(0), apex], [R(0), apexIn], [R(H - b / Math.sin(pitch)), S]];
  const armL = armR.map(([x, y]) => [2 * o.at - x, y]);
  // THE FIELD: the circle on the axis touching both inner lines and clear of the archivolt's crown
  const Yb = S + rise + ring + b * .5;
  const yc = (Yb + apexIn * c) / (1 + c), rho = (apexIn - yc) * c - b * .25;
  const fb = Math.max(.05, b * .35);
  const field = [];
  if (spec.field !== false && rho > 3 * fb) {
    field.push({ pts: circle([o.at, yc], rho, Math.max(10, Math.min(16, Math.round(rho * 2 * Math.PI / .5))), Math.PI / 2), closed: true });
    const s = Math.sin(Math.PI / 3), rf = rho * s / (1 + s);
    if (rf > 2 * fb) for (let j = 0; j < 3; j++) {
      const th = Math.PI / 2 + j * 2 * Math.PI / 3, cc = [o.at + (rho - rf) * Math.cos(th), yc + (rho - rf) * Math.sin(th)];
      field.push({ pts: circle(cc, rf, 8, th), closed: true });
    }
  }
  // THE ARCHIVOLT: the band round the arch, its middle line; and the SHAFTS the arms' feet stand on, from the sill
  // (down the jambs to the sill as well: a moulding framing the whole opening, standing where the opening does)
  const arch = off(ring / 2).map(([x, y]) => [R(x), S + y]);
  if (S - o.sill > 1e-3) { arch.unshift([arch[0][0], o.sill]); arch.push([arch[arch.length - 1][0], o.sill]); }
  const shafts = S - o.sill > b ? [armR, armL].map(([[x0], , , [x1]]) => [[x0, o.sill], [x1, o.sill], [x1, S], [x0, S]]) : [];
  return { armR, armL, apex, pitch, b, fb, field, H, arch, ring, shafts, room: roof - apex };
}

export function wimpergMesh(o, spec, map, m, top = Infinity) {
  const G = wimpergLines(o, spec, top);
  if (!G) return m;
  const { armR, armL, apex, b, fb, field, arch, ring, shafts, room } = G;
  const depth = spec.depth ?? Math.max(.25, Math.min(.6, b * 1.2));
  const { at, poly, slab } = proudOf(map, spec.side ? 1 : 0, m);
  slab(armR, 0, depth);
  slab(armL, 0, depth);
  if (spec.shafts !== false) for (const sh of shafts) slab(sh, 0, depth);
  barsMesh([{ pts: arch, closed: false }], ring, (x, y, s) => at(x, y, (1 - s) * depth * .6), 0, 1, m);
  // CROCKETS up each outer edge: a leaf springing from the coping's top, curling up and out
  if (spec.crockets !== false) {
    const L = Math.hypot(armR[0][0] - armR[1][0], armR[0][1] - armR[1][1]), step = Math.max(.6, 3 * b), n = Math.floor(L / step) - 1;
    const cs = b * 1.1;
    for (const arm of [armR, armL]) {
      const [foot, top] = [arm[0], arm[1]], e = [(top[0] - foot[0]) / L, (top[1] - foot[1]) / L];
      const nrm = [Math.sign(foot[0] - top[0]) * Math.abs(e[1]), Math.abs(e[0])];    // out of the arm, upward
      for (let i = 1; i <= n; i++) {
        const p = [foot[0] + e[0] * step * i, foot[1] + e[1] * step * i];
        const b0 = [p[0] - e[0] * cs / 2, p[1] - e[1] * cs / 2], b1 = [p[0] + e[0] * cs / 2, p[1] + e[1] * cs / 2];
        const tip = at(p[0] + nrm[0] * cs + e[0] * cs * .5, p[1] + nrm[1] * cs + e[1] * cs * .5, depth / 2);
        const base = [at(...b0, depth * .1), at(...b1, depth * .1), at(...b1, depth * .9), at(...b0, depth * .9)];
        const ref = at(p[0] - nrm[0] * b, p[1] - nrm[1] * b, depth / 2);
        for (let k = 0; k < 4; k++) poly([base[k], base[(k + 1) % 4], tip], ref);
      }
    }
  }
  // THE FINIAL on the apex: a pyramid on a square as wide as the coping, as tall as three of them -- or as the room
  // left under the wall's top, if that is less (none, under a coping's height)
  const h = Math.min(Math.max(.5, 3 * b), room + b * .4);
  if (spec.finial !== false && h > b) {
    const w = b * .7, x = o.at, y0 = apex - b * .4;
    const base = [at(x - w, y0, depth * .5 - w), at(x + w, y0, depth * .5 - w), at(x + w, y0, depth * .5 + w), at(x - w, y0, depth * .5 + w)];
    const tip = at(x, y0 + h, depth * .5), ref = at(x, y0 + h * .3, depth * .5);
    for (let k = 0; k < 4; k++) poly([base[k], base[(k + 1) % 4], tip], ref);
    poly(base, at(x, y0 + 1, depth * .5));
  }
  // the blind tracery in the field, a bar's depth proud of the wall
  if (field.length) barsMesh(field, fb, (x, y, s) => at(x, y, (1 - s) * fb * 1.2), 0, 1, m);
  return m;
}

// DRAWING PROUD OF A FACE: `at(x, y, d)` the point of the face's (x, y) `d` metres proud of the side it stands on
// (`side` 1: the face's back, `map`'s far side), `poly` a face of corners wound away from a point inside, `slab` a
// convex outline in the face from `d0` to `d1` proud -- front, back and sides (a member rising over the wall's top
// stands free there; one that never does may leave its back off, `back` false: it lies in the wall's face, unseen)
export function proudOf(map, side, m) {
  const at = (x, y, d) => {
    const p = map(x, y, side), q = map(x, y, 1 - side), l = Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]) || 1;
    return [p[0] + (p[0] - q[0]) / l * d, p[1] + (p[1] - q[1]) / l * d, p[2] + (p[2] - q[2]) / l * d];
  };
  const poly = (ps, ref) => {
    const [p, q, r] = ps, u = [q[0] - p[0], q[1] - p[1], q[2] - p[2]], v = [r[0] - p[0], r[1] - p[1], r[2] - p[2]];
    const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
    const c = ps.reduce((s, w) => [s[0] + w[0] / ps.length, s[1] + w[1] / ps.length, s[2] + w[2] / ps.length], [0, 0, 0]);
    let ids = ps.map((w) => m.vert(...w));
    if (n[0] * (c[0] - ref[0]) + n[1] * (c[1] - ref[1]) + n[2] * (c[2] - ref[2]) < 0) ids = ids.reverse();
    for (let i = 1; i + 1 < ids.length; i++) m.tri(ids[0], ids[i], ids[i + 1]);
  };
  // (`hide`: the sides -- edge i from point i to the next -- that stand against something as proud as the slab, and are
  //  never seen: an arch's spandrel under the band it hangs from)
  const slab = (pts, d0, d1, back = true, hide = null) => {
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length, cy = pts.reduce((s, p) => s + p[1], 0) / pts.length, ref = at(cx, cy, (d0 + d1) / 2);
    poly(pts.map(([x, y]) => at(x, y, d1)), ref);
    if (back) poly(pts.map(([x, y]) => at(x, y, d0)), ref);
    for (let i = 0; i < pts.length; i++) {
      if (hide && hide.includes(i)) continue;
      const [p, q] = [pts[i], pts[(i + 1) % pts.length]];
      poly([at(...p, d0), at(...q, d0), at(...q, d1), at(...p, d1)], ref);
    }
  };
  return { at, poly, slab };
}
