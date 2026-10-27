// TRACERY: the stone that divides a Gothic window into LIGHTS and fills its head, drawn as the masons drew it -- with
// compasses, from the window's own arch, nothing placed by eye:
//   the span is split into equal lights by MULLIONS, from the sill up to the springing line;
//   the lights are gathered under SUB-ARCHES of the window's own profile at their smaller span, springing from the
//   same line -- in pairs when the window has an even number (a 4-light window is two 2-light windows under one arch),
//   each light under its own when odd -- and each sub-arch over more than one light is a window in turn: the rule
//   recurses;
//   in the head between the sub-arches and the arch over them the largest CIRCLE that fits on the axis, touching them
//   (in an equilateral 2-light window: a quarter of the span across, √5/4 of the span over the springing -- the
//   classical construction falls out of the rule), and FOILS cusped inside a circle large enough: four over a pair,
//   three over an odd row, each touching its neighbours and the circle.
// Every line is a BAR of one width, centred on it, of one depth, set in the middle of the wall's thickness round the
// glass (build.js glassPanes). The bars' ends are buried in the reveal, the sill or another bar.
import { archCurve } from "./profiles.js";

// how many lights a window of span W has, unless it says: none in a narrow lancet
const autoLights = (W) => (W >= 3.4 ? 4 : W >= 2.4 ? 3 : W >= 1.2 ? 2 : 1);

// the window's head at another half span: the same profile, a rise given in metres scaled with it
const headAt = (head, f) => (head.rise !== undefined ? { ...head, rise: head.rise * f } : head);

function distToLine(p, pts) {
  let best = Infinity;
  for (let i = 0; i + 1 < pts.length; i++) {
    const [ax, ay] = pts[i], [bx, by] = pts[i + 1], dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy;
    const t = L2 > 0 ? Math.max(0, Math.min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2)) : 0;
    best = Math.min(best, Math.hypot(p[0] - ax - dx * t, p[1] - ay - dy * t));
  }
  return best;
}
const circle = (c, r, n, turn = 0) => Array.from({ length: n }, (_, k) => { const t = turn + k * 2 * Math.PI / n; return [c[0] + r * Math.cos(t), c[1] + r * Math.sin(t)]; });

// THE LINES of a window's tracery, in the face's (x, y): [{ pts, closed }], and the bar's width -- or null for a
// window too narrow for any. `o` is a laid-out opening (build.js wallFace: at, a, sill, springing, curve, head);
// `spec` its `tracery`: { style, lights, foils, bar } -- style "geometric" (the default: the rule above),
// "perpendicular" or "bars" (below)
export function traceryLines(o, spec) {
  if (o.foot) return roseLines(o, spec);
  if (spec.style === "perpendicular") return panelLines(o, spec);
  if (spec.style === "bars") return barLines(o, spec);
  const W = 2 * o.a, n = Math.round(spec.lights ?? autoLights(W));
  if (n < 2) return null;
  const b = spec.bar ?? Math.max(.09, Math.min(.2, W * .055));
  const head = o.head ?? {}, per90 = head.per90 ?? 4, lines = [];
  const abs = (cx, pts) => pts.map(([x, y]) => [cx + x, o.springing + y]);
  // the mullions: every light's edge from the sill to the springing
  for (let k = 1; k < n; k++) { const x = o.at - o.a + W * k / n; lines.push({ pts: [[x, o.sill], [x, o.springing]], closed: false }); }
  // a span [x0, x1] of `count` lights under the arch `over` (its line, in the face's frame)
  // (the sub-arches a step coarser than the window's own head: they are small)
  const subHead = { ...head, per90: Math.max(2, per90 - 1) };
  const fill = (x0, x1, count, over, top0 = true) => {
    if (count < 2) return;
    const groups = count % 2 === 0 && count > 2 ? [count / 2, count / 2] : Array(count).fill(1);
    const w = (x1 - x0) / count, subs = [];
    let x = x0;
    for (const g of groups) {
      const a = g * w / 2, cx = x + a, line = abs(cx, archCurve(a, headAt(subHead, a / o.a)));
      lines.push({ pts: line, closed: false });
      subs.push({ x0: x, x1: x + 2 * a, g, line });
      x += 2 * a;
    }
    // THE CIRCLE: on the axis, between the sub-arches' crowns and the arch's, as large as touches both
    const xm = (x0 + x1) / 2, top = Math.max(...over.map(([, y]) => y)), low = Math.max(...subs.flatMap((s) => s.line.map(([, y]) => y)));
    let best = null;
    for (let i = 1; i < 40; i++) {
      const c = [xm, low + (top - low) * i / 40];
      const r = Math.min(distToLine(c, over), ...subs.map((s) => distToLine(c, s.line)));
      if (!best || r > best.r) best = { c, r };
    }
    if (best && best.r > 1.6 * b) {
      const N = Math.max(8, Math.min(12, Math.round(best.r * 2 * Math.PI / .4)));
      lines.push({ pts: circle(best.c, best.r, N, Math.PI / 2), closed: true });
      // the FOILS, cusped inside it: k circles each touching the two beside it and the circle round them (in the
      // window's own head only: the small circles over the sub-arches are left plain)
      const k = groups.length === 2 ? 4 : 3, s = Math.sin(Math.PI / k), rf = best.r * s / (1 + s);
      if (top0 && spec.foils !== false && rf > 1.4 * b) for (let j = 0; j < k; j++) {
        const t = Math.PI / 2 + j * 2 * Math.PI / k, c = [best.c[0] + (best.r - rf) * Math.cos(t), best.c[1] + (best.r - rf) * Math.sin(t)];
        lines.push({ pts: circle(c, rf, rf < .35 ? 6 : 8, t), closed: true });
      }
    }
    for (const s of subs) fill(s.x0, s.x1, s.g, s.line, false);
  };
  fill(o.at - o.a, o.at + o.a, n, abs(o.at, o.curve));
  return { lines, b };
}

// the head's height over x (the curve read where it passes over x): where a bar rising from the sill meets the arch
function headY(o, x) {
  const c = o.curve;
  for (let i = 0; i + 1 < c.length; i++) {
    const x0 = o.at + c[i][0], x1 = o.at + c[i + 1][0];
    if ((x - x0) * (x - x1) <= 0 && x0 !== x1) return o.springing + c[i][1] + (c[i + 1][1] - c[i][1]) * (x - x0) / (x1 - x0);
  }
  return o.springing;
}

// PERPENDICULAR tracery (the English 14th-15th century's, Westminster's): a grid of PANELS -- the mullions rise
// straight from the sill into the arch, TRANSOMS cross the lights, the lowest at the springing and the rest dividing
// the lights below it into tiers about as tall as 1.6 lights' width, and every light is closed under each transom by
// a small pointed head of its own, its crown on the transom
function panelLines(o, spec) {
  const W = 2 * o.a, n = Math.round(spec.lights ?? Math.max(2, Math.min(6, Math.round(W / .75))));
  if (n < 2) return null;
  const b = spec.bar ?? Math.max(.08, Math.min(.18, W * .045)), lw = W / n, lines = [], x0 = o.at - o.a;
  for (let k = 1; k < n; k++) { const x = x0 + lw * k; lines.push({ pts: [[x, o.sill], [x, headY(o, x)]], closed: false }); }
  const H = o.springing - o.sill, tiers = Math.max(1, Math.min(4, Math.round(H / (1.6 * W)))), small = archCurve(lw / 2, { profile: "pointed", spread: .5, per90: 2 });
  const rise = Math.max(...small.map(([, y]) => y));
  for (let t = 1; t <= tiers; t++) {
    const y = o.sill + H * t / tiers;
    if (t < tiers || o.curve.some(([, cy]) => cy > .05)) lines.push({ pts: [[x0, y], [x0 + W, y]], closed: false });
    if (rise < H / tiers * .5) for (let k = 0; k < n; k++) lines.push({ pts: small.map(([sx, sy]) => [x0 + lw * (k + .5) + sx, y - rise + sy]), closed: false });
  }
  return { lines, b };
}

// GLAZING BARS (a classical sash's, a palace's): the window glazed in PANES about `pane` wide and a third again as
// tall, a whole number of them across and up its straight part; the bars that divide them, and where the head is
// round, an impost bar at the springing and the fanlight over it divided by bars radiating from the head's centre, as
// many as the panes under it; under a flat or a low head the uprights simply run on to it
function barLines(o, spec) {
  const W = 2 * o.a, pane = spec.pane ?? .5, cols = Math.max(1, Math.round(spec.cols ?? W / pane)), H = o.springing - o.sill;
  const rows = Math.max(1, Math.round(spec.rows ?? H / (pane * 1.35))), b = spec.bar ?? .05, lines = [], x0 = o.at - o.a;
  const rise = Math.max(...o.curve.map(([, y]) => y)), fan = rise > o.a * .6;
  for (let k = 1; k < cols; k++) { const x = x0 + W * k / cols; lines.push({ pts: [[x, o.sill], [x, fan ? o.springing : headY(o, x)]], closed: false }); }
  for (let j = 1; j < rows + (fan ? 1 : 0); j++) { const y = o.sill + H * j / rows; lines.push({ pts: [[x0, y], [x0 + W, y]], closed: false }); }
  if (fan) for (let k = 1; k < cols; k++) {
    const t = Math.PI * (1 - k / cols), far = [o.at + Math.cos(t) * o.a * 2, o.springing + Math.sin(t) * rise * 2];
    // (out from the head's centre until it meets the arch)
    let lo = 0, hi = 1;
    for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2, x = o.at + (far[0] - o.at) * m, y = o.springing + (far[1] - o.springing) * m; if (y < headY(o, x)) lo = m; else hi = m; }
    lines.push({ pts: [[o.at, o.springing], [o.at + (far[0] - o.at) * lo, o.springing + (far[1] - o.springing) * lo]], closed: false });
  }
  return lines.length ? { lines, b } : null;
}

// A ROSE: a round window (a head and a foot: a circle) drawn from its centre -- a HUB, SPOKES out from it dividing the
// rose into `lights` (as many as about 1.4m of its rim each, even), every light capped by a pointed ARCH from one
// spoke's end to the next, and between each two arches and the rim, on the spoke's line, the largest CIRCLE that fits
// -- the same rule as a window's head, turned round a centre. The rim is the wall's own edge.
function roseLines(o, spec) {
  const R = o.a, c = [o.at, o.springing], b = spec.bar ?? Math.max(.1, Math.min(.22, R * .035));
  const n = Math.round(spec.lights ?? Math.max(8, Math.min(16, 2 * Math.round(Math.PI * R / 1.4))));
  if (R < 1 || n < 6) return null;
  const lines = [], rh = R * .2, r1 = R * .6, at = (r, t) => [c[0] + r * Math.cos(t), c[1] + r * Math.sin(t)];
  lines.push({ pts: circle(c, rh, Math.max(8, Math.min(12, n)), Math.PI / 2), closed: true });
  const th = (k) => Math.PI / 2 + k * 2 * Math.PI / n;
  for (let k = 0; k < n; k++) lines.push({ pts: [at(rh, th(k)), at(r1, th(k))], closed: false });
  // one light's arch, its chord between two spokes' ends, its crown outward -- the light's own (local: x along the
  // chord, y out from it), turned to each light in turn
  const A = at(r1, th(0)), B = at(r1, th(1)), half = Math.hypot(B[0] - A[0], B[1] - A[1]) / 2;
  const local = archCurve(half, { profile: "pointed", spread: .5, per90: 3 });
  const arch = (k) => {
    const t0 = th(k), t1 = th(k + 1), P = at(r1, t0), Q = at(r1, t1), m = [(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2];
    const ux = (Q[0] - P[0]) / (2 * half), uy = (Q[1] - P[1]) / (2 * half), ox = m[0] - c[0], oy = m[1] - c[1], ol = Math.hypot(ox, oy);
    return local.map(([x, y]) => [m[0] + ux * x + ox / ol * y, m[1] + uy * x + oy / ol * y]);
  };
  const arches = Array.from({ length: n }, (_, k) => arch(k));
  for (const pts of arches) lines.push({ pts, closed: false });
  // the circle on spoke k's line, between the arches either side of it and the rim
  let best = null;
  for (let i = 0; i <= 30; i++) {
    const rc = r1 + (R - r1) * i / 30, p = at(rc, th(0));
    const r = Math.min(R - rc, distToLine(p, arches[0]), distToLine(p, arches[n - 1]));
    if (!best || r > best.r) best = { rc, r };
  }
  if (best && best.r > 1.6 * b) for (let k = 0; k < n; k++) lines.push({ pts: circle(at(best.rc, th(k)), best.r, 8, th(k)), closed: true });
  return { lines, b };
}

// THE BARS into mesh `m`: each line a bar `b` wide and `depth` deep, centred on it, in the middle of the wall's
// thickness -- `map(x, y, s)` the face's point at depth s (0 its front, 1 its back)
export function traceryMesh(o, spec, map, m) {
  const T = traceryLines(o, spec);
  if (!T) return m;
  const { lines, b } = T, y0 = (o.sill + o.springing) / 2;
  const A = map(o.at, y0, 0), B = map(o.at, y0, 1), thick = Math.hypot(B[0] - A[0], B[1] - A[1], B[2] - A[2]);
  const depth = spec.depth ?? b * 1.5, d = Math.min(.45, depth / 2 / Math.max(thick, 1e-6));
  return barsMesh(lines, b, map, .5 - d, .5 + d, m);
}

// BARS ALONG LINES: each line of the face's (x, y) a bar `b` wide, centred on it, between the depths `f` and `k`
// through the wall (`map`'s third coordinate: 0 its front face, 1 its back; past them, proud of a face)
export function barsMesh(lines, b, map, f, k, m) {
  const at = (x, y, s) => { const p = map(x, y, 0), q = map(x, y, 1); return [p[0] + (q[0] - p[0]) * s, p[1] + (q[1] - p[1]) * s, p[2] + (q[2] - p[2]) * s]; };
  const face = (ps, ref) => {
    // (wound to face away from the bar's own line)
    const [p, q, r] = ps, u = [q[0] - p[0], q[1] - p[1], q[2] - p[2]], v = [r[0] - p[0], r[1] - p[1], r[2] - p[2]];
    const nx = u[1] * v[2] - u[2] * v[1], ny = u[2] * v[0] - u[0] * v[2], nz = u[0] * v[1] - u[1] * v[0];
    const c = ps.reduce((s, w) => [s[0] + w[0] / 4, s[1] + w[1] / 4, s[2] + w[2] / 4], [0, 0, 0]);
    const ids = ps.map((w) => m.vert(...w));
    if (nx * (c[0] - ref[0]) + ny * (c[1] - ref[1]) + nz * (c[2] - ref[2]) >= 0) m.quad(...ids); else m.quad(ids[3], ids[2], ids[1], ids[0]);
  };
  for (const { pts, closed } of lines) {
    const N = pts.length;
    // each point's two edges: offset across the line by half the bar, mitred where it turns
    const side = pts.map((p, i) => {
      const pv = closed ? pts[(i + N - 1) % N] : pts[Math.max(0, i - 1)], nx = closed ? pts[(i + 1) % N] : pts[Math.min(N - 1, i + 1)];
      let tx = nx[0] - pv[0], ty = nx[1] - pv[1]; const l = Math.hypot(tx, ty) || 1; tx /= l; ty /= l;
      let kk = 1;
      if (closed || (i > 0 && i < N - 1)) { const e = [p[0] - pv[0], p[1] - pv[1]], le = Math.hypot(...e) || 1; kk = 1 / Math.max(.5, (e[0] * tx + e[1] * ty) / le); }
      const h = b / 2 * kk;
      return [[p[0] - ty * h, p[1] + tx * h], [p[0] + ty * h, p[1] - tx * h]];
    });
    const corner = (i, j, s) => at(side[i][j][0], side[i][j][1], s);
    const segs = closed ? N : N - 1;
    for (let i = 0; i < segs; i++) {
      const i2 = (i + 1) % N, ref = at((pts[i][0] + pts[i2][0]) / 2, (pts[i][1] + pts[i2][1]) / 2, (f + k) / 2);
      face([corner(i, 0, f), corner(i2, 0, f), corner(i2, 1, f), corner(i, 1, f)], ref);   // the front
      face([corner(i, 1, k), corner(i2, 1, k), corner(i2, 0, k), corner(i, 0, k)], ref);   // the back
      face([corner(i, 0, k), corner(i2, 0, k), corner(i2, 0, f), corner(i, 0, f)], ref);   // one side
      face([corner(i, 1, f), corner(i2, 1, f), corner(i2, 1, k), corner(i, 1, k)], ref);   // the other
    }
  }
  return m;
}
