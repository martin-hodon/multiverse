// ARCH PROFILES: the curve an opening's head follows, as mathematics rather than as a drawing.
//
// Every profile is the same contract -- given the opening's half-width `a` and the rise the definition asks
// for, return the polyline from the LEFT springing point to the RIGHT one, in the opening's own frame (x
// across, y up, the springing line at y = 0). The endpoints are exact: the first point is (-a, 0) and the last
// is (+a, 0), because everything else in the engine meets the arch there and "meets" has to mean the same
// number, not nearly the same number.
//
// The families are the real ones, and they are all the same construction with the centres moved:
//   semicircular   one centre, on the springing line, at the middle
//   segmental      one centre BELOW the springing line: a shallow arc, the rise chosen
//   horseshoe      one centre ABOVE the springing line: the curve turns back in under itself
//   pointed        TWO centres, moved apart horizontally by `spread` half-widths: the gothic family, from
//                  equilateral (spread 1) through lancet (> 1) to drop (< 1)
//   trigonal       two straight chamfers meeting at a point: the triangular head
//   flat           a straight lintel, so an opening can be square-headed without a special case
//
// HOW MANY POINTS A CURVE GETS is one knob for the whole building, in powers of two: `per90` segments per 90
// degrees of arc. Two is the coarse setting a Roman arch reads perfectly well at from across a square (four
// segments over its half-circle); four is the comfortable one; eight and sixteen are for a close look or a
// dome. Deriving it from the ARC each profile actually spans -- rather than a flat count -- is what makes it
// mean the same thing everywhere: a shallow segmental arch gets fewer points than a horseshoe, because it is
// less of a circle. A definition may still say `seg` outright, which is the total for the curve and wins.
//
// Either way the number is a property of the DEFINITION, not of the renderer: two pieces that meet along an
// arch must be told the same number or they will not share its points.

const TAU = Math.PI * 2;

// segments for an arc of `angle` radians, from the building's detail level -- at least one, and the whole
// curve's own `seg` overrides it
export const segsFor = (angle, p, parts = 1) =>
  Math.max(1, p.seg !== undefined ? Math.round(p.seg / parts) : Math.round((p.per90 ?? 2) * Math.abs(angle) / (Math.PI / 2)));

// a circular arc centred at (cx, cy) from angle a0 to a1, n segments, endpoints included
function arc(cx, cy, r, a0, a1, n, out) {
  for (let i = 0; i <= n; i++) {
    const t = a0 + (a1 - a0) * (i / n);
    out.push([cx + r * Math.cos(t), cy + r * Math.sin(t)]);
  }
  return out;
}

// snap a point that is meant to BE the springing point to exactly that, so rounding never leaves a hair's gap
const pin = (pts, a) => {
  pts[0] = [-a, 0];
  pts[pts.length - 1] = [a, 0];
  return pts;
};

export const PROFILES = {
  // r = a: the classic Roman arch. rise = a.
  semicircular: (a, p) => pin(arc(0, 0, a, Math.PI, 0, segsFor(Math.PI, p), []), a),

  // a shallower arc through the same springing points: the centre drops below the springing line. `rise` is
  // the crown's height above it, and must be < a or this IS a semicircle.
  segmental: (a, p) => {
    const rise = Math.min(p.rise ?? a * .5, a * .999);
    const r = (a * a + rise * rise) / (2 * rise);         // the circle through (-a,0), (0,rise), (a,0)
    const cy = rise - r;
    const half = Math.asin(a / r);
    return pin(arc(0, cy, r, Math.PI / 2 + half, Math.PI / 2 - half, segsFor(2 * half, p), []), a);
  },

  // the centre rises above the springing line and the curve comes back in under itself: the horseshoe. `over`
  // is how far above, as a share of the half-width (Moorish work runs about a third).
  horseshoe: (a, p) => {
    const over = p.over ?? .3, cy = a * over;
    const r = Math.hypot(a, cy);                          // through the springing points, centred high
    const half = Math.atan2(cy, a);                       // the angle below horizontal the springing sits at
    return pin(arc(0, cy, r, Math.PI + half, -half, segsFor(Math.PI + 2 * half, p), []), a);
  },

  // TWO centres on the springing line, `spread` half-widths apart: the pointed family. spread 1 is the
  // equilateral arch (centres at the opposite springing points), > 1 a lancet, < 1 a drop arch.
  pointed: (a, p) => {
    const spread = p.spread ?? 1, c = a * spread, r = a + c;
    const n = segsFor(Math.asin(Math.sqrt(r * r - c * c) / r), p, 2);   // each of the two arcs, from its own span
    const apex = Math.sqrt(r * r - c * c);                // where the two arcs meet, on the centre line
    const half = Math.asin(apex / r);
    const left = arc(c, 0, r, Math.PI, Math.PI - half, n, []);   // centred right, drawn from the left springing
    const right = arc(-c, 0, r, half, 0, n, []);                  // centred left, up to the right springing
    left.pop();                                                   // the apex is one point, not two
    return pin([...left, [0, apex], ...right.slice(1)], a);
  },

  // two straight chamfers to a point: the trigonal head. `rise` is the apex height.
  trigonal: (a, p) => pin([[-a, 0], [0, p.rise ?? a], [a, 0]], a),

  // THE CORBEL VAULT (the Maya "false arch"): no voussoirs, each course laid a little further in than the one under it
  // until the two sides come near enough for a CAPSTONE (`cap`, its half-width; a quarter metre or so) to close the
  // gap -- straight soffits leaning in at `slope` degrees from the horizontal (70: Chichen Itza's), and `steps` courses
  // if the stair of the corbelling is left showing (0: the soffit dressed smooth, as plaster finished it). The span it can
  // close is what limits a Maya room's width.
  corbel: (a, p) => {
    const cap = Math.min(p.cap ?? .15, a * .5), rise = (a - cap) * Math.tan((p.slope ?? 70) * Math.PI / 180), n = Math.round(p.steps ?? 0);
    if (!n) return pin([[-a, 0], [-cap, rise], [cap, rise], [a, 0]], a);
    const left = [[-a, 0]];
    for (let k = 1; k <= n; k++) { const x = -a + (a - cap) * k / n, y = rise * k / n; left.push([left[left.length - 1][0], y], [x, y]); }
    return pin([...left, ...left.slice().reverse().map(([x, y]) => [-x, y])], a);
  },

  // a square head, so a window needs no special case elsewhere
  flat: (a) => pin([[-a, 0], [a, 0]], a),

  // THE S-LINE OF TWO RADII: a convex arc, then a concave one, meeting tangent at the point of inflection
  // and ending on the axis with a vertical tangent -- the onion dome's meridian, and the ogee arch's head.
  // The first arc is centred ON THE AXIS, `bulge` half-widths in radius, so it swells out past the springing
  // exactly as far as `bulge` says and comes back in (bulge 1 puts its centre on the springing line: the
  // curve leaves the springing vertically and does not swell at all, which is the ogee). The second is
  // `neck` half-widths in radius, centred level with the tip and outside the curve; it touches the first,
  // so the two centres are R1 + R2 apart -- and THAT fixes the height: the tip stands where the neck's
  // circle, tangent to the bulb, reaches the axis. Two radii say the whole shape.
  onion: (a, p) => onion(a, p.bulge ?? 1.25, p.neck ?? 1, p),
  ogee: (a, p) => onion(a, p.bulge ?? 1, p.neck ?? .7, p),

  // THE BELL: the onion's reverse -- CONCAVE first, then CONVEX to a level crown. It turns from one to the other
  // where it stands VERTICAL, at its WAIST: `waist` half-widths out from the axis, `lift` half-widths above the
  // springing. Above the waist it is a quarter circle centred on the axis (so the crown is level); below, an
  // arc centred level with the waist and outside it, through the springing -- the skirt that flares out to
  // the drum. Two numbers say the shape, and the height is lift + waist. Dresden's Frauenkirche, the stone bell.
  bell: (a, p) => {
    const R2 = a * Math.min(.98, Math.max(.05, p.waist ?? .78)), cy = a * Math.max(.05, p.lift ?? 1);
    const d = a - R2, R1 = (d * d + cy * cy) / (2 * d);                  // the skirt's circle, through the springing
    const c1x = R2 + R1, a0 = Math.atan2(-cy, a - c1x);                  // (its centre is level with the waist)
    const skirt = arc(c1x, cy, R1, a0 < 0 ? a0 + TAU : a0, Math.PI, segsFor(Math.abs((a0 < 0 ? a0 + TAU : a0) - Math.PI), p, 2), []);
    skirt[skirt.length - 1] = [R2, cy];
    const top = arc(0, cy, R2, 0, Math.PI / 2, segsFor(Math.PI / 2, p, 2), []);
    top[top.length - 1] = [0, cy + R2];
    return pin(mirrorUp([...skirt, ...top.slice(1)]), a);
  },

  // THREE FOILS: two lobes standing on the springing points and one over the middle, each a circle of `lobe`
  // half-widths, their centres a quarter turn apart on a circle round the opening's middle -- so the lobes
  // cross, and where they cross is a CUSP pointing down into the opening. Lobes too small to meet are no
  // trefoil (the head would have gaps), and the engine says so.
  trefoil: (a, p) => {
    const r = a * (p.lobe ?? .45), c = a - r, d = c * Math.SQRT2;
    if (d >= 2 * r) throw new Error(`a trefoil's lobes (${(p.lobe ?? .45)} of the half-width) are too small to meet`);
    const h = Math.sqrt(r * r - d * d / 4);
    const cusp = [c / 2 + h / Math.SQRT2, c / 2 + h / Math.SQRT2];   // the right-hand cusp, away from the middle
    const a1 = Math.atan2(cusp[1], cusp[0] - c);                        // ...seen from the right lobe's centre
    const a2 = Math.atan2(cusp[1] - c, cusp[0]);                        // ...and from the top lobe's
    const side = arc(c, 0, r, 0, a1, segsFor(a1, p, 3), []);
    const top = arc(0, c, r, a2, Math.PI / 2, segsFor(Math.PI / 2 - a2, p, 3), []);
    top[top.length - 1] = [0, c + r];
    return pin(mirrorUp([...side, ...top.slice(1)]), a);
  },

  // TWO ARCS CURVING INWARD to a point: the pointed arch turned inside out, each side bowing toward the
  // opening instead of away from it, its centre outside the arch. `rise` is the apex over the springing
  // (default one and a half half-widths), `bow` how far each side sags in from the straight chamfer, as a
  // share of that chamfer's length.
  inflexed: (a, p) => {
    const H = p.rise ?? a * 1.5, L = Math.hypot(a, H), s = L * Math.max(.01, Math.min(.45, p.bow ?? .15));
    const R = (L * L / 4 + s * s) / (2 * s);
    const nx = H / L, ny = a / L;                                   // the chord's normal, pointing away from the opening
    const cx = a / 2 + nx * (R - s), cy = H / 2 + ny * (R - s);
    const t0 = Math.atan2(0 - cy, a - cx);
    let t1 = Math.atan2(H - cy, 0 - cx);
    if (t1 - t0 > Math.PI) t1 -= TAU; else if (t0 - t1 > Math.PI) t1 += TAU;
    const side = arc(cx, cy, R, t0, t1, segsFor(t1 - t0, p, 2), []);
    side[side.length - 1] = [0, H];
    return pin(mirrorUp(side), a);
  },

  // A CHINESE ROOF'S SECTION -- jujia, the "raising" of the purlins: the half-span is divided into steps from the
  // eave in, and each step is steeper than the one outside it -- `lo` the slope (rise over run) of the step at the
  // eave, `hi` of the step at the crown, the steps between in proportion (the Qing rule reads 0.5, 0.65, 0.75, 0.9
  // for a four-step roof). So the purlins lie on the parabola y(d) = lo d + (hi - lo) d^2 / 2a, d measured in from
  // the eave -- ON it at every step whatever their number, which is why the detail level may change the steps and
  // not the roof -- and the roof is CONCAVE: flat at the eaves, steep at the top. Turned about its axis it is the
  // round roof of a Chinese hall or pavilion, cut short by an `oculus` where the drum of the tier above rises.
  jujia: (a, p) => {
    const lo = p.lo ?? .35, hi = p.hi ?? 1.2, n = Math.max(3, p.seg !== undefined ? Math.round(p.seg) : 2 * (p.per90 ?? 2));
    const right = [];
    for (let k = 0; k <= n; k++) { const d = a * k / n; right.push([a - d, lo * d + (hi - lo) * d * d / (2 * a)]); }
    right[n][0] = 0;
    return pin(mirrorUp(right), a);
  },
};

function onion(a, bulge, neck, p) {
  const R1 = a * Math.max(1, bulge), R2 = a * Math.max(.05, neck);
  const yc = Math.sqrt(Math.max(0, R1 * R1 - a * a));          // the bulb's centre, on the axis
  const H = yc + Math.sqrt(R1 * R1 + 2 * R1 * R2);            // the tip: |(R2, H) - (0, yc)| = R1 + R2
  const d = R1 + R2, ux = R2 / d, uy = (H - yc) / d;          // unit vector, bulb centre -> neck centre
  const aS = Math.atan2(-yc, a), aT = Math.atan2(uy, ux);     // the bulb, from the springing to the tangent point
  const bT = Math.atan2(-uy, -ux);                            // the neck, from the tangent point (seen from its centre)...
  const bulb = arc(0, yc, R1, aS, aT, segsFor(aT - aS, p, 2), []);
  const neckArc = arc(R2, H, R2, bT < 0 ? bT + TAU : bT, Math.PI, segsFor(Math.abs((bT < 0 ? bT + TAU : bT) - Math.PI), p, 2), []);
  neckArc[neckArc.length - 1] = [0, H];                       // ...to the tip, exactly on the axis
  return pin(mirrorUp([...bulb, ...neckArc.slice(1)]), a);   // springing -> tip on the right, mirrored
}

// a curve drawn up the RIGHT side (springing -> crown on the axis) as the whole head, left springing to right
const mirrorUp = (right) => [...right.map(([x, y]) => [-x, y]), ...right.slice(0, -1).reverse()];

// the head of an opening, from its definition: { profile, seg, rise, spread, over }
export function archCurve(halfWidth, def = {}) {
  const make = PROFILES[def.profile ?? "semicircular"];
  if (!make) throw new Error(`arch profile "${def.profile}" is not one of ${Object.keys(PROFILES).join(", ")}`);
  const pts = make(halfWidth, def);
  // the curve must run left to right and touch the springing points exactly: everything downstream relies on
  // the first and last point being shared with the pier beside it
  if (Math.abs(pts[0][0] + halfWidth) > 1e-12 || Math.abs(pts[pts.length - 1][0] - halfWidth) > 1e-12) {
    throw new Error(`arch profile "${def.profile}" does not end on its springing points`);
  }
  return pts;
}

export const archRise = (halfWidth, def = {}) => {
  let top = 0;
  for (const [, y] of archCurve(halfWidth, def)) top = Math.max(top, y);
  return top;
};
