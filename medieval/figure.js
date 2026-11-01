// A MEDIEVAL FIGURE (docs/glass.md): pieces in the Greek schema's spirit but for a frontal age. A body 100 tall, head a seventh of it, narrow
// shoulders, large head and hands, feet splayed down, and the cloth falling in long lines that end on the hem. Not a rig: a saint
// doesn't stride. A pose is where his hands are, in units of that 100, from the figure's own left to right as seen.
//   Slots are the palette's. -> [{ pts, fill, whole?, role, paint: [{ pts, w, closed, alpha }, { pts, fill, alpha }] }], later over earlier, feet at y 0, x 0 centre.

const TAU = Math.PI * 2;
const INK = "#1d120b";
const POSES = {
  // each hand's elbow and wrist, and what the body does: drop (the head comes down so far), sit, kneel
  stand:  { L: [[-13, 61], [-11, 44]], R: [[13, 61], [11, 44]] },
  bless:  { L: [[-13, 62], [-9, 76]], R: [[13, 60], [9, 54]] },
  book:   { L: [[-13, 61], [-11, 45]], R: [[13, 60], [6, 58]] },
  orant:  { L: [[-20, 66], [-20, 82]], R: [[20, 66], [20, 82]] },
  point:  { L: [[-20, 72], [-31, 74]], R: [[13, 60], [9, 52]] },
  offer:  { L: [[-14, 66], [-16, 64]], R: [[14, 66], [16, 64]] },
  sit:    { L: [[-15, 56], [-9, 66]], R: [[14, 52], [11, 46]], drop: 14, sit: true },
  kneel:  { L: [[-14, 44], [-20, 54]], R: [[-5, 46], [-16, 54]], drop: 32, kneel: true },
};

// (a smooth line through points)
export function curve(ctrl, per = 5, closed = false) {
  const n = ctrl.length, out = [], at = (i) => closed ? ctrl[(i + n) % n] : ctrl[Math.max(0, Math.min(n - 1, i))];
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const a = at(i - 1), b = at(i), c = at(i + 1), d = at(i + 2);
    for (let k = 0; k < per; k++) {
      const t = k / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((q) => .5 * (2 * b[q] + (c[q] - a[q]) * t + (2 * a[q] - 5 * b[q] + 4 * c[q] - d[q]) * t2 + (3 * b[q] - a[q] - 3 * c[q] + d[q]) * t3)));
    }
  }
  if (!closed) out.push(ctrl[n - 1]);
  return out;
}
// (a bow: a ring as one polygon, with a slit)
const ring8 = (x, y, R, r) => { const at = (q, a) => [x + q * Math.cos(a), y + q * Math.sin(a)], o = Array.from({ length: 13 }, (_, i) => at(R, i * Math.PI / 6)), n = Array.from({ length: 13 }, (_, i) => at(r, -i * Math.PI / 6)); return [...o, ...n]; };
const oval = (cx, cy, rx, ry, n = 16, turn = 0) => Array.from({ length: n }, (_, k) => { const t = turn + k * TAU / n; return [cx + rx * Math.cos(t), cy + ry * Math.sin(t)]; });
// a limb: a line given widths
function limb(pts, w0, w1, steps = 4) {
  const line = curve(pts, steps), L = [], R = [];
  line.forEach((p, i) => {
    const a = line[Math.max(0, i - 1)], b = line[Math.min(line.length - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, w = w0 + (w1 - w0) * i / (line.length - 1);
    L.push([p[0] - dy / d * w, p[1] + dx / d * w]); R.push([p[0] + dy / d * w, p[1] - dx / d * w]);
  });
  return [...L, ...R.reverse()];
}
const fold = (pts, w = .36, alpha = .8) => ({ pts: curve(pts, 4), w, alpha });

// what a hand may hold: drawn upward from the hand
const ATTR = {
  book: (x, y, f) => [{ pts: [[x - 7, y - 4], [x + 6, y - 6.5], [x + 7, y + 8], [x - 6, y + 10]], fill: f, whole: true, role: "attr", paint: [{ pts: [[x - 1, y - 1], [x + 1.5, y + 7]], w: .5 }, { pts: [[x - 3.5, y + 3], [x + 3.5, y + 2.2]], w: .5 }, { pts: [[x - 7, y - 4], [x + 6, y - 6.5], [x + 7, y + 8], [x - 6, y + 10]], w: .5, closed: true }] }],
  staff: (x, y, f) => [{ pts: [[x - 1.1, y - 42], [x + 1.1, y - 42], [x + 1.1, y + 30], [x - 1.1, y + 30]], fill: f, role: "attr" }, { pts: curve([[x - 1, y + 29], [x - 2, y + 38], [x + 3, y + 43], [x + 8, y + 39], [x + 7, y + 34], [x + 4, y + 34], [x + 4, y + 38], [x + 1, y + 37], [x + 1.4, y + 29]], 3), fill: f, role: "attr" }],
  key: (x, y, f) => [{ pts: [[x - 1, y - 6], [x + 1, y - 6], [x + 1, y + 20], [x - 1, y + 20]], fill: f, role: "attr" }, { pts: ring8(x, y + 24, 5, 2.6), fill: f, role: "attr" }, ...[[-6, -2.2], [-1.4, 2.2]].map(([a, b]) => ({ pts: [[x + 1, y + a], [x + 7.5, y + a], [x + 7.5, y + b], [x + 1, y + b]], fill: f, role: "attr" }))],
  sword: (x, y, f) => [{ pts: [[x - 1.3, y + 3], [x + 1.3, y + 3], [x + 1.3, y + 36], [x, y + 40], [x - 1.3, y + 36]], fill: 4, role: "attr" }, { pts: [[x - 5, y + 2], [x + 5, y + 2], [x + 5, y + 4], [x - 5, y + 4]], fill: f, role: "attr" }],
  cross: (x, y, f) => [{ pts: [[x - 1.2, y - 18], [x + 1.2, y - 18], [x + 1.2, y + 30], [x - 1.2, y + 30]], fill: f, role: "attr" }, { pts: [[x - 8, y + 16], [x + 8, y + 16], [x + 8, y + 19], [x - 8, y + 19]], fill: f, role: "attr" }],
  palm: (x, y, f) => [{ pts: limb([[x, y - 4], [x + 2, y + 12], [x + 7, y + 28]], 1.5, .6), fill: f, role: "attr", paint: Array.from({ length: 6 }, (_, i) => ({ pts: [[x + i * 1.2 - 2, y + 8 + i * 4], [x + i * 1.2 + 2, y + 11 + i * 4]], w: .5 })) }],
};

// THE FIGURE. { pose, robe, mantle, skin, hair, beard, veil, crown, mitre, halo, wings, holdL, holdR, attr, turn (-1..1: where he looks, 0 at us), x, bare }
export function buildFigure(F, rng = Math.random) {
  const P = POSES[F.pose ?? "stand"] ?? POSES.stand, drop = P.drop ?? 0, skin = F.skin ?? 5, robe = F.robe ?? 0, mantle = F.mantle ?? 1, hair = F.hair ?? 8, turn = F.turn ?? 0, out = [], attrFill = F.attr ?? 2;
  const hy = 93 - drop, hx = turn * 2, by = (y) => y - drop * (P.kneel ? y / 80 : y > 46 ? 1 : y / 46), sh = 82 - drop;
  const jit = () => (rng() - .5) * 1.4;
  if (F.wings != null) for (const s of [-1, 1]) {
    const ctrl = [[s * 7, sh - 2], [s * 19, sh + 10], [s * 29, sh + 3], [s * 31, sh - 18], [s * 27, sh - 44], [s * 19, sh - 58], [s * 14, sh - 38], [s * 9, sh - 18]];
    out.push({ pts: curve(ctrl, 3, true), fill: F.wings, role: "wing", paint: Array.from({ length: 7 }, (_, i) => fold([[s * (11 + i * 2.6), sh - 5 + i * .6], [s * (14 + i * 2.2), sh - 24 - i * 2], [s * (16 + i * 1.3), sh - 46 - i * .6]], .5, .75)) });
  }
  if (F.halo != null) out.push({ pts: oval(hx, hy + .5, 11, 11, 24), fill: F.halo, role: "halo", paint: [{ pts: oval(hx, hy + .5, 9.8, 9.8, 24), w: .5, closed: true, alpha: .8 }, ...(F.crossNimbus ? [{ pts: [[hx - 10, hy + 1], [hx - 6, hy + 1]], w: 1.4 }, { pts: [[hx + 6, hy + 1], [hx + 10, hy + 1]], w: 1.4 }, { pts: [[hx, hy + 7], [hx, hy + 11]], w: 1.4 }] : [])] });
  // FEET: under the hem, pointing down and out
  if (!P.sit && !P.kneel) for (const s of [-1, 1]) out.push({ pts: [[s * 2.2, 8], [s * 8, 8], [s * 9.5, 3], [s * 12, -.4], [s * 7, -.4], [s * 3, 2]], fill: F.shoes ?? 6, role: "foot", paint: [] });
  else if (P.sit) for (const s of [-1, 1]) out.push({ pts: [[s * 4, 8], [s * 11, 8], [s * 13, 2], [s * 15, -.4], [s * 9, -.4], [s * 4.6, 2]], fill: F.shoes ?? 6, role: "foot", paint: [] });
  // THE ROBE: from the shoulders, narrow at the waist, spreading to a hem that waves
  const wst = by(60), hem = P.sit ? 7 : P.kneel ? 2 : 7, wide = P.sit ? 22 : P.kneel ? 20 : 15, sway = P.kneel ? -6 : 0;
  const robePts = curve([[-9.5, sh], [-9, by(72)], [-8.2, wst], [-10 + sway * .3, by(40)], [-wide + sway, by(22)], [-wide + sway, hem], [-wide / 2 + sway, hem - 1.6], [sway, hem + .4], [wide / 2 + sway, hem - 1.6], [wide + sway, hem], [wide + sway * .4, by(22)], [10, by(40)], [8.2, wst], [9, by(72)], [9.5, sh]], 3);
  const robeFolds = [];
  for (let i = -3; i <= 3; i++) {
    const x0 = i * 2.3, x1 = i * wide / 3.4 + sway;
    robeFolds.push(fold([[x0 + jit() * .4, wst - 1], [(x0 * 1.1 + x1) / 2 + jit(), (wst + hem) / 2], [x1 + jit(), hem + 1]], .55));
  }
  robeFolds.push(...[-1, 1].map((s) => fold([[s * 6, by(77)], [s * 1.5, by(70)], [s * -.5, by(66)]], .45, .7)));
  robeFolds.push({ pts: curve([[-wide + sway, hem + 3], [sway, hem + 3.6], [wide + sway, hem + 3]], 4), w: .9, alpha: .9 }, { pts: curve([[-8.2, wst + 1.2], [0, wst + .2], [8.2, wst + 1.2]], 3), w: 1, alpha: .95 });
  if (P.sit) robeFolds.push(...[-1, 1].map((s) => fold([[s * 8, by(46)], [s * 17, by(32) + 4], [s * 19, by(14)]], .5)), fold([[-10, by(46) + 3], [0, by(39) + 3], [10, by(46) + 3]], .5));
  out.push({ pts: robePts, fill: robe, role: "robe", paint: robeFolds, label: F.id ? `${F.id}r` : undefined });
  // THE MANTLE: over one shoulder and across, ending in a zigzag that shows the robe beneath
  if (!F.bare) {
    const lo = P.sit ? by(18) : P.kneel ? by(24) : 26, zz = [];
    const steps = 6; for (let i = 0; i <= steps; i++) { const t = i / steps, x = 12 + sway * .6 - t * (21 + sway * .4) + 0, y = lo + (i % 2 ? 3.5 : 0) + (1 - t) * 9; zz.push([x, y]); }
    const pts = [[-9.5, sh + .4], [-7, by(72)], [-9, by(52)], [-9, lo + 12], ...zz.reverse(), [13, by(50)], [10, by(70)], [9.5, sh + .4], [5.5, sh + 2.4], [0, by(75)], [-5.5, sh + 2.4]];
    out.push({ pts: curve(pts, 2, true), fill: mantle, role: "mantle", paint: [
      ...Array.from({ length: 5 }, (_, i) => fold([[-7 + i * 3.4, by(72) - i], [-6.5 + i * 3.9 + jit(), by(52)], [-7.5 + i * 4.8 + jit(), lo + 12 + (4 - i) * .9]])),
      fold([[9, sh - 2], [2, by(66)], [-7, by(52)]], .5), fold([[10, by(66)], [4, by(58)], [-5, by(47)]], .4),
    ] });
  }
  // ARMS and HANDS
  for (const s of ["L", "R"]) {
    const sg = s === "L" ? -1 : 1, [e, h] = P[s], sx = sg * 9.5, eb = [e[0], e[1]], hd = [h[0], h[1]], wr = [hd[0] * .9 + eb[0] * .1, hd[1] * .9 + eb[1] * .1];
    out.push({ pts: limb([[sx, sh - .5], eb, wr], 3.7, 3), fill: F.sleeve ?? mantle, role: "sleeve", paint: [fold([[sx + sg * -1.2, sh - 8], [eb[0] + sg * -2, eb[1] + 1], [eb[0] + (wr[0] - eb[0]) * .3, eb[1] + (wr[1] - eb[1]) * .3]], .5, .85), { pts: [[wr[0] - 3, wr[1]], [wr[0] + 3, wr[1]]], w: 1, alpha: .9 }] });
    const up = F.bless === s || (F.pose === "bless" && s === "L");
    if (up) out.push({ pts: [[hd[0] - 2.8, hd[1] - 2], [hd[0] + 2.8, hd[1] - 2], [hd[0] + 3, hd[1] + 2.5], [hd[0] + 1.2, hd[1] + 3.2], [hd[0] + 1.2, hd[1] + 8.5], [hd[0] - .2, hd[1] + 9], [hd[0] - .5, hd[1] + 3.2], [hd[0] - 1.6, hd[1] + 7.5], [hd[0] - 2.8, hd[1] + 7], [hd[0] - 3, hd[1] + 2.5]], fill: skin, whole: true, role: "hand", paint: [{ pts: [[hd[0] - 2, hd[1] + 2], [hd[0] + 2, hd[1] + 1.6]], w: .5, alpha: .9 }] });
    else out.push({ pts: oval(hd[0] + sg * .2, hd[1], 3.3, 3.8, 12), fill: skin, whole: true, role: "hand", paint: [{ pts: [[hd[0] - 1.8, hd[1] - 2], [hd[0] - 1.6, hd[1] + 2]], w: .4, alpha: .7 }, { pts: [[hd[0] + 1.4, hd[1] - 2], [hd[0] + 1.6, hd[1] + 2]], w: .4, alpha: .7 }] });
    const held = F[`hold${s}`];
    if (held) { if (!ATTR[held]) throw new Error(`no attribute "${held}"`); out.push(...ATTR[held](hd[0] + sg * 1.5, hd[1], attrFill)); }
  }
  // NECK, BEARD BEHIND, HEAD
  out.push({ pts: [[hx * .4 - 2.8, sh - .6], [hx * .4 + 2.8, sh - .6], [hx * .7 + 2.5, hy - 4], [hx * .7 - 2.5, hy - 4]], fill: skin, role: "neck", whole: true, paint: [] });
  const vh = F.veil != null;
  if (vh) out.push({ pts: curve([[hx - 7, hy + 7.5], [hx - 9.5, hy - 2], [hx - 10, sh - 14], [hx - 7.5, sh - 3], [hx, sh - .5], [hx + 7.5, sh - 3], [hx + 10, sh - 14], [hx + 9.5, hy - 2], [hx + 7, hy + 7.5], [hx, hy + 9.5]], 3, true), fill: F.veil, role: "veil", paint: [fold([[hx - 7.5, hy - 2], [hx - 8, sh - 8]], .5), fold([[hx + 7.5, hy - 2], [hx + 8, sh - 8]], .5)] });
  else out.push({ pts: curve([[hx - 6.1, hy + 3], [hx - 6.8, hy - 3], [hx - 4.5, hy - 7], [hx + 4.5, hy - 7], [hx + 6.8, hy - 3], [hx + 6.1, hy + 3], [hx + 5.6, hy + 7.2], [hx, hy + 8.4], [hx - 5.6, hy + 7.2]], 3, true), fill: hair, role: "hair", paint: [fold([[hx - 5, hy + 6], [hx - 6, hy + 1], [hx - 5.6, hy - 4]], .4, .7), fold([[hx + 5, hy + 6], [hx + 6, hy + 1], [hx + 5.6, hy - 4]], .4, .7)] });
  // the face: an oval, one sheet; everything on it is paint: arched brows run into the long nose, almond eyes looking where he turns
  const fx = hx + turn * 1.2, E = hy + 1.5, eye = (s) => {
    const cx = fx + s * 2.5, ix = cx + turn * .7;
    return [{ pts: curve([[cx - 1.6, E], [cx, E + .85], [cx + 1.6, E], [cx, E - .55]], 4, true), w: .36, closed: true }, { pts: oval(ix, E + .12, .68, .68, 8), fill: INK }, { pts: curve([[cx - s * -2 * -1 + s * .1, E + 2.3 - .2], [cx + s * .2, E + 2.5], [cx + s * 2, E + 1.8]].sort((a, b) => a[0] - b[0]), 4), w: .5 }];
  };
  const face = [
    ...eye(-1), ...eye(1),
    { pts: curve([[fx - .5 + turn * .5, E + 2.2], [fx - .35 + turn * 1, E - 1], [fx - .9 + turn * 1.3, E - 3.2], [fx + .7 + turn * 1.3, E - 3.5]], 3), w: .42 },
    { pts: [[fx - 1.6, E - 5.6], [fx + 1.6, E - 5.6]], w: .42 },
    { pts: curve([[fx - 1.4, E - 5.7], [fx, E - 6.2], [fx + 1.4, E - 5.7]], 3), w: .25, alpha: .75 },
    { pts: curve([[hx - 3.8, E - 2], [hx - 2.6, E - 3.5], [hx - 1.8, E - 2]], 4), w: 2.2, alpha: .09 },
    { pts: curve([[hx + 3.8, E - 2], [hx + 2.6, E - 3.5], [hx + 1.8, E - 2]], 4), w: 2.2, alpha: .09 },
  ];
  out.push({ pts: curve([[hx - 5, hy + 4], [hx - 5.1, hy - .5], [hx - 3.4, hy - 5], [hx, hy - 7], [hx + 3.4, hy - 5], [hx + 5.1, hy - .5], [hx + 5, hy + 4], [hx + 2.8, hy + 6.3], [hx - 2.8, hy + 6.3]], 3, true), fill: skin, whole: true, role: "face", paint: face });
  if (!vh) out.push({ pts: curve([[hx - 5.6, hy + 2.2], [hx - 4.8, hy + 6.8], [hx - 1, hy + 8.4], [hx + 4.8, hy + 6.8], [hx + 5.6, hy + 2.2], [hx + 3.4, hy + 5], [hx, hy + 5.6], [hx - 3.4, hy + 5]], 3, true), fill: hair, role: "fringe", paint: [fold([[hx - 2, hy + 8], [hx - 1.5, hy + 6]], .35, .7), fold([[hx + 2, hy + 8], [hx + 1.5, hy + 6]], .35, .7)] });
  else out.push({ pts: curve([[hx - 5.6, hy + 2.5], [hx - 4.5, hy + 7], [hx, hy + 8.8], [hx + 4.5, hy + 7], [hx + 5.6, hy + 2.5], [hx, hy + 5.7]], 3, true), fill: F.veil, role: "veil", paint: [] });
  if (F.beard != null) out.push({ pts: curve([[hx - 5, hy - 1], [hx - 4.2, hy - 8], [hx, hy - 11.5], [hx + 4.2, hy - 8], [hx + 5, hy - 1], [hx + 2, hy - 3.8], [fx, hy - 4.3], [hx - 2, hy - 3.8]], 3, true), fill: F.beard, role: "beard", paint: [fold([[hx - 2, hy - 5], [hx - 1, hy - 10]], .35, .8), fold([[hx, hy - 5], [hx, hy - 11]], .35, .8), fold([[hx + 2, hy - 5], [hx + 1, hy - 10]], .35, .8)] });
  if (F.crown != null) { const c = F.crown; out.push({ pts: [[hx - 5.6, hy + 4.5], [hx + 5.6, hy + 4.5], [hx + 6.2, hy + 10.5], [hx + 3.1, hy + 7.5], [hx, hy + 11.5], [hx - 3.1, hy + 7.5], [hx - 6.2, hy + 10.5]], fill: c, whole: true, role: "crown", paint: [{ pts: [[hx - 5.6, hy + 5.8], [hx + 5.6, hy + 5.8]], w: .5 }] }); }
  if (F.mitre != null) { const c = F.mitre; out.push({ pts: [[hx - 5.4, hy + 4.5], [hx + 5.4, hy + 4.5], [hx + 4.8, hy + 11], [hx, hy + 16], [hx - 4.8, hy + 11]], fill: c, whole: true, role: "mitre", paint: [{ pts: [[hx, hy + 4.5], [hx, hy + 16]], w: .7 }, { pts: [[hx - 5.4, hy + 6], [hx + 5.4, hy + 6]], w: .7 }] }); }
  return out;
}

// pieces, moved and scaled; a line's width scales with them
export const placed = (pieces, s, dx, dy, flip = 1) => pieces.map((p) => ({ ...p, pts: p.pts.map(([x, y]) => [dx + flip * x * s, dy + y * s]), paint: p.paint?.map((q) => ({ ...q, w: q.w === undefined ? undefined : q.w * s, pts: q.pts.map(([x, y]) => [dx + flip * x * s, dy + y * s]) })) }));
