// A MEDIEVAL FIGURE (docs/story.md): pieces in the Greek schema's spirit but for a frontal age. A body 100 tall, head a seventh of it, narrow
// shoulders, large head and hands, feet splayed down, and the cloth falling in long lines that end on the hem. Not a rig: a saint doesn't stride
// far. A POSE is data (tools/storygen.py, assets/story/canon.json): where the hands are, in units of that 100, facing +x if it faces at all, and the outline of what's below the
// waist. A dress is what's named on the figure: garment `cut`, headgear, what's held. Slots are the palette's, chosen before this (story/compose.js).
//   -> [{ pts, fill, whole?, role, paint: [{ pts, w, closed, alpha }, { pts, fill, alpha }] }], later over earlier, feet at y 0, x 0 centre; .anchors: named places on him.
import CANON from "../assets/story/canon.json" with { type: "json" };
import { twoBone } from "../greek/rig.js";

const slotOf = (name) => CANON.tints.indexOf(name);                    // (a colour by the canon's name where the caller hasn't its own dye)
const TAU = Math.PI * 2;
const INK = "#1d120b";

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
export const oval = (cx, cy, rx, ry, n = 16, turn = 0) => Array.from({ length: n }, (_, k) => { const t = turn + k * TAU / n; return [cx + rx * Math.cos(t), cy + ry * Math.sin(t)]; });
// a limb: a line given widths
export function limb(pts, w0, w1, steps = 4) {
  const line = curve(pts, steps), L = [], R = [];
  line.forEach((p, i) => {
    const a = line[Math.max(0, i - 1)], b = line[Math.min(line.length - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, w = w0 + (w1 - w0) * i / (line.length - 1);
    L.push([p[0] - dy / d * w, p[1] + dx / d * w]); R.push([p[0] + dy / d * w, p[1] - dx / d * w]);
  });
  return [...L, ...R.reverse()];
}
const fold = (pts, w = .36, alpha = .8) => ({ pts: curve(pts, 4), w, alpha });
const along = (poly, s) => { const k = Math.max(0, Math.min(1, s)) * (poly.length - 1), i = Math.min(poly.length - 2, Math.floor(k)), u = k - i; return [poly[i][0] + (poly[i + 1][0] - poly[i][0]) * u, poly[i][1] + (poly[i + 1][1] - poly[i][1]) * u]; };

// A SHAPE OF THE DATA: a part { c: control points, per, closed } or { pts }; { fill, role, whole, paint: [{ c | pts, per, w, closed, alpha, fill }] }. `fill` a slot, or a name `tint` knows ("attr": what the caller says)
export function partsOf(parts, { x = 0, y = 0, s = 1, flip = 1, tint = (f) => f, spin = 0 } = {}) {
  const cs = Math.cos(spin), sn = Math.sin(spin), put = ([a, b]) => { const u = a * cs - b * sn, v = a * sn + b * cs; return [x + flip * u * s, y + v * s]; };
  const shape = (q) => (q.pts ?? curve(q.c, q.per ?? 3, !!q.closed)).map(put);
  return parts.map((q) => ({ pts: shape(q), fill: tint(q.fill), role: q.role ?? "attr", ...(q.whole ? { whole: true } : null), ...(q.label ? { label: q.label } : null), ...(q.span ? { span: q.span } : null),
    paint: (q.paint ?? []).map((l) => ({ pts: shape(l), ...(l.w !== undefined ? { w: l.w * s } : null), ...(l.closed ? { closed: true } : null), ...(l.alpha !== undefined ? { alpha: l.alpha } : null), ...(l.ink !== undefined ? { fill: l.ink } : null), ...(l.c !== undefined && l.pts ? { c: l.c } : null) })) }));
}

// THE FIGURE. { pose, robe, mantle, cut, sleeve, hem, hose, shoes, skin, hair, hairCut, beard, beardCut, veil, crown, mitre, tiara, hood, cap, hat, turban, helmet, wreath, halo, crossNimbus, haloSquare, wings, holdL, holdR, attr, attr2, turn (-1..1: where he looks, 0 at us), short (a tunic to the knee), naked, loin, reach: { L|R: [x, y] }, bust, coarse (small: fewer points) }
export function buildFigure(F, rng = Math.random) {
  const P = CANON.poses[F.pose ?? "stand"] ?? CANON.poses.stand, drop = P.drop ?? 0, skin = F.skin ?? 5, robe = F.robe ?? 0, mantle = F.mantle ?? 1, hair = F.hair ?? 8, turn = F.turn ?? P.turn ?? 0, out = [], attrFill = F.attr ?? 2, c1 = F.coarse ? 1 : 0;
  const sh = 82 - drop, by = (y) => y - drop * (P.kneel ? y / 80 : y > 46 ? 1 : y / 46), wst = P.waist ?? by(60), lean = P.lean ?? 0;
  const top = ([x, y]) => [x + lean * Math.max(0, Math.min(1.25, (y - wst) / Math.max(1, sh - wst))), y], tops = (pts) => pts.map(top);   // (the trunk leaning from the waist: arms say where they end for themselves)
  const hx = turn * 2 + lean * 1.2 + (P.headX ?? 0), hy = 93 - drop + (P.headY ?? 0), jit = () => (rng() - .5) * 1.4;
  const CV = (ctrl, per, closed) => curve(ctrl, Math.max(1, per - c1), closed);
  const cloak = F.cut === "cloak" || F.cut === "chlamys";
  // WHAT'S BELOW THE WAIST: two sides, foot of the waist to the hem; a pose may draw its own, or it's a robe falling wide
  const hem0 = P.hem ?? (P.kneel ? 2 : 7), wide = P.wide ?? (P.kneel ? 20 : 15);
  const sideL = curve(P.skirt?.L ?? [[-8.2, wst], [-10, by(40)], [-wide, by(22)], [-wide, hem0]], 4), sideR = curve(P.skirt?.R ?? [[8.2, wst], [10, by(40)], [wide, by(22)], [wide, hem0]], 4);
  const shortAt = F.short ? (P.shortAt ?? .62) : F.naked ? .36 : 1;
  const sL = sideL.slice(0, Math.max(2, Math.round((sideL.length - 1) * shortAt) + 1)), sR = sideR.slice(0, Math.max(2, Math.round((sideR.length - 1) * shortAt) + 1));
  const eL = sL.at(-1), eR = sR.at(-1), hemY = (eL[1] + eR[1]) / 2, robeC = F.naked ? (F.loin ?? 4) : robe;
  const feet = P.feet ?? (P.kneel ? [] : P.sit ? [[1.8, 0, -1], [-1.8, 0, 1]] : [[0, 0, -1], [0, 0, 1]]);
  const foot = (dx, dy, s) => ({ pts: [[s * 2.2, 8], [s * 8, 8], [s * 9.5, 3], [s * 12, -.4], [s * 7, -.4], [s * 3, 2]].map(([a, b]) => [a + dx, b + dy]), fill: F.shoes ?? 6, role: "foot", paint: [] });

  if (F.wings != null) for (const s of [-1, 1]) {
    const ctrl = [[s * 7, sh - 2], [s * 19, sh + 10], [s * 29, sh + 3], [s * 31, sh - 18], [s * 27, sh - 44], [s * 19, sh - 58], [s * 14, sh - 38], [s * 9, sh - 18]].map(top);
    out.push({ pts: CV(ctrl, 3, true), fill: F.wings, role: "wing", paint: F.coarse ? [] : Array.from({ length: 7 }, (_, i) => fold(tops([[s * (11 + i * 2.6), sh - 5 + i * .6], [s * (14 + i * 2.2), sh - 24 - i * 2], [s * (16 + i * 1.3), sh - 46 - i * .6]]), .5, .75)) });
  }
  if (F.halo != null) {
    if (F.haloSquare) out.push({ pts: [[hx - 9, hy - 7], [hx + 9, hy - 7], [hx + 9, hy + 10], [hx - 9, hy + 10]], fill: F.halo, role: "halo", paint: [] });
    else out.push({ pts: oval(hx, hy + .5, 11, 11, F.coarse ? 16 : 24), fill: F.halo, role: "halo", paint: [{ pts: oval(hx, hy + .5, 9.8, 9.8, 24), w: .5, closed: true, alpha: .8 }, ...(F.crossNimbus ? [{ pts: [[hx - 10, hy + 1], [hx - 6, hy + 1]], w: 1.4 }, { pts: [[hx + 6, hy + 1], [hx + 10, hy + 1]], w: 1.4 }, { pts: [[hx, hy + 7], [hx, hy + 11]], w: 1.4 }] : [])] });
  }
  // A CLOAK hangs behind him from the shoulders, wider than he is
  if (cloak && !F.bust && F.mantle != null) { const a = along(sideL, .78), b = along(sideR, .78); out.push({ pts: CV([top([-9, sh + 1]), top([-14, by(72)]), [a[0] - 5, by(48)], [a[0] - 3, a[1]], [(a[0] + b[0]) / 2, a[1] - 2], [b[0] + 3, b[1]], [b[0] + 5, by(48)], top([14, by(72)]), top([9, sh + 1])], 3), fill: mantle, role: "mantle", paint: [fold([[a[0] - 3, a[1] + 2], [a[0] - 4, by(48)], top([-12, by(70)])], .5), fold([[b[0] + 3, b[1] + 2], [b[0] + 4, by(48)], top([12, by(70)])], .5)] }); }
  // FEET: under the hem, pointing down and out; below a short hem the legs show
  if (!F.bust) {
    for (const [dx, dy, s] of feet) out.push(foot(dx, dy, s));
    if (shortAt < 1) for (const L of P.legs ?? feet.map(([dx, dy, s]) => [[s * 4 + dx * .3, Math.max(hemY + 4, 34)], [s * 5 + dx * .7 + (P.kneeOut ?? 0), (hemY + dy) * .55], [s * 5 + dx, dy + 7]])) out.push({ pts: limb(L, 4.2, 2.8, 2 + (F.coarse ? 0 : 1)), fill: F.naked ? skin : F.hose ?? 10, role: "leg", whole: !!F.naked, paint: [] });
  }
  // THE ROBE: from the shoulders, narrow at the waist, spreading to a hem that waves
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const hemC = [eL, [(eL[0] * 2 + eR[0]) / 3, (eL[1] * 2 + eR[1]) / 3 - 1.6], [...mid(eL, eR).slice(0, 1), (eL[1] + eR[1]) / 2 + .4], [(eL[0] + eR[0] * 2) / 3, (eL[1] + eR[1] * 2) / 3 - 1.6], eR];
  const lower = [...sL.slice(1, -1), ...(shortAt < 1 && !F.naked ? [eL, eR] : curve(hemC, 3)), ...[...sR].reverse().slice(1, -1)];
  if (!F.bust) {
    const folds = [], n = F.naked ? 1 : F.coarse ? 2 : 3;
    for (let i = -n; i <= n; i++) {                                     // (a fold is the two sides mixed: it follows whatever shape the skirt has)
      const t = (i + n + 1) / (2 * n + 2) + (rng() - .5) * .03, at = (s) => { const a = along(sL, s), b = along(sR, s); return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; };
      folds.push(fold([at(.04), at(.42), at(.76), at(1).map((v, q) => q ? v + 1 : v)], .55));
    }
    if (!F.coarse) folds.push({ pts: curve(hemC.map(([a, b]) => [a, b + 3]), 3), w: .9, alpha: .9 });
    folds.push(...(F.coarse ? [] : [-1, 1].map((s) => fold(tops([[s * 6, by(77)], [s * 1.5, by(70)], [s * -.5, by(66)]]), .45, .7))), { pts: curve(tops([[-8.2, wst + 1.2], [0, wst + .2], [8.2, wst + 1.2]]), 3), w: 1, alpha: .95 });
    if (F.short) folds.push({ pts: [[eL[0], eL[1] + 1.6], [eR[0], eR[1] + 1.6]], w: .7, alpha: .9 });
    if (F.clavi != null) for (const s of [-1, 1]) folds.push({ pts: [top([s * 5, sh + .6]), [s * 5, wst], along(s < 0 ? sL : sR, .45).map((v, q) => q ? v : v * .55 + s * 1), along(s < 0 ? sL : sR, 1).map((v, q) => q ? v + 1 : v * .55 + s * 1)], w: 2, c: F.claviC, alpha: 1 });
    if (F.naked) out.push({ pts: [...tops([[-9.5, sh], [-9, by(72)], [-8.2, wst]]), [-8.6, wst - 6], [8.6, wst - 6], ...tops([[8.2, wst], [9, by(72)], [9.5, sh]])], fill: skin, role: "trunk", whole: true, paint: [fold(tops([[-5, by(72)], [0, by(69)], [5, by(72)]]), .5), ...[0, 1, 2].flatMap((k) => [-1, 1].map((s) => fold(tops([[s * 1.5, by(66 - k * 2.4)], [s * 7, by(68 - k * 2.4)]]), .35, .65))), fold(tops([[0, by(72)], [0, wst + 2]]), .4, .7)] });
    out.push({ pts: F.naked ? [[-8.6, wst - 4], ...lower, [8.6, wst - 4]] : [...tops([[-9.5, sh], [-9, by(72)], [-8.2, wst]]), ...lower, ...tops([[8.2, wst], [9, by(72)], [9.5, sh]])], fill: robeC, role: "robe", paint: folds, label: F.id ? `${F.id}r` : undefined });
    if (F.belt != null) out.push({ pts: [...tops([[-8.4, wst + 1.5], [8.4, wst + 1.5]]), [8.3, wst - 1.3], [-8.3, wst - 1.3]], fill: F.belt, role: "belt", whole: true, paint: [] });
    if (F.hem != null) { const h1 = curve(hemC, 2).reverse(), up = hemC.map(([a, b]) => [a * .98, b + 3.2]); out.push({ pts: [...CV(up, 2), ...h1], fill: F.hem, role: "hem", whole: true, paint: [] }); }
    if (F.apron != null) out.push({ pts: [...tops([[-6.5, by(74)], [6.5, by(74)]]), [7.5, wst], [Math.max(7, eR[0] * .55), eR[1] + 4], [Math.min(-7, eL[0] * .55), eL[1] + 4], [-7.5, wst]], fill: F.apron, role: "apron", paint: [{ pts: [[-7.5, wst], [7.5, wst]], w: .7 }] });
  } else out.push({ pts: [...CV([top([-9.5, sh]), top([-11, by(74)]), [-12, by(60)], [-13, by(46)], [-13, by(38)]], 3), [13, by(38)], ...CV([[13, by(46)], [12, by(60)], top([11, by(74)]), top([9.5, sh])], 3)], fill: robeC, role: "robe", paint: [fold([[-4, by(70)], [-3, by(50)], [-5, by(38)]], .5), fold([[4, by(70)], [3, by(50)], [5, by(38)]], .5)] });
  // THE MANTLE, by its cut: over one shoulder and across; a cope, open down the front; a chasuble, a bell; a cloak's front; a veil to the waist
  const sideAt = (s) => [along(sideL, s), along(sideR, s)], cut = F.bust && !["sash", "maphorion", "cloak", "chlamys", "cope", "himation"].includes(F.cut ?? "sash") ? "sash" : F.cut ?? "sash";
  if (F.mantle !== null && !F.bare && !F.naked) {
    const lo = F.bust ? by(40) : P.sit ? by(18) : P.kneel ? by(24) : 26, low = F.bust ? [[-13, by(38)], [13, by(38)]] : sideAt(.72);
    if (cut === "sash" && !F.short) {
      const zz = [], steps = 6, sway = P.kneel ? -6 : 0; for (let i = 0; i <= steps; i++) { const t = i / steps, x = 12 + sway * .6 - t * (21 + sway * .4), y = lo + (i % 2 ? 3.5 : 0) + (1 - t) * 9; zz.push([x, y]); }
      const pts = [...tops([[-9.5, sh + .4], [-7, by(72)], [-9, by(52)]]), [-9, lo + 12], ...zz.reverse(), [13, by(50)], ...tops([[10, by(70)], [9.5, sh + .4], [5.5, sh + 2.4], [0, by(75)], [-5.5, sh + 2.4]])];
      out.push({ pts: CV(pts, 2, true), fill: mantle, role: "mantle", paint: F.coarse ? [] : [...Array.from({ length: 5 }, (_, i) => fold([top([-7 + i * 3.4, by(72) - i]), [-6.5 + i * 3.9 + jit(), by(52)], [-7.5 + i * 4.8 + jit(), lo + 12 + (4 - i) * .9]])), fold([top([9, sh - 2]), [2, by(66)], [-7, by(52)]], .5), fold([[10, by(66)], [4, by(58)], [-5, by(47)]], .4)] });
    } else if (cut === "himation" && !F.short) {                         // (the antique way: over the far shoulder, across the belly, its end falling from the arm. An apostle's)
      const [a, b] = F.bust ? low : sideAt(.82), pts = [...tops([[-9.5, sh + .4], [-3, by(76)], [2, by(66)]]), [7, wst - 3], [b[0] * .7, b[1] + 6], [b[0] * .35, b[1] + 1], [a[0] * .5, a[1] + 3], [a[0] * .9, a[1] + 1], [a[0] * .8, by(40)], ...tops([[-9, by(60)], [-10.5, by(74)]])];
      out.push({ pts: CV(pts, 2, true), fill: mantle, role: "mantle", paint: F.coarse ? [] : [fold([top([-6, by(76)]), [0, by(62)], [8, by(50)]], .55), fold([[-7, by(66)], [-1, by(52)], [6, by(42)]], .5), fold([[-8, by(56)], [-3, by(40)], [b[0] * .6, b[1] + 8]], .5), fold([[-9, by(46)], [a[0] * .6, by(30)], [a[0] * .55, a[1] + 4]], .5)] });
    } else if (cut === "cope" && !F.short) {
      const [a, b] = F.bust ? low : sideAt(.94), gap = (y) => 1.8 + (sh - y) * .1, panel = (s, e) => [...tops([[s * 3, sh + 2], [s * 9.8, sh + .4], [s * 12, by(74)]]), [e[0] * .96, by(46)], e, [s * Math.abs(e[0]) * .45, e[1] + 1], [s * gap(e[1]), e[1]], [s * gap(wst), wst]];
      for (const [s, e] of [[-1, a], [1, b]]) out.push({ pts: panel(s, e), fill: mantle, role: "mantle", paint: F.coarse ? [] : [{ pts: [[s * (gap(wst) + 1.2), wst], [s * (gap(e[1]) + 1.2), e[1]]], w: 2.2, c: F.orphrey ?? "#d9ae38", alpha: 1 }, fold([top([s * 8, by(74)]), [s * 9, by(50)], [e[0] * .8, e[1]]], .5), fold([top([s * 6, by(72)]), [s * 5.5, by(50)], [e[0] * .5, e[1]]], .45)] });
      out.push({ pts: oval(lean, by(72), 2.6, 2.6, 10), fill: F.attr ?? 2, role: "morse", whole: true, paint: [] });
    } else if (cut === "chasuble" && !F.short) {
      const [a, b] = F.bust ? low : sideAt(.62), pts = [...tops([[-5, sh + 1.6], [-10, sh], [-12, by(74)]]), [a[0] * .95, by(48)], [a[0] * .7, a[1]], [0, a[1] - 4], [b[0] * .7, b[1]], [b[0] * .95, by(48)], ...tops([[12, by(74)], [10, sh], [5, sh + 1.6], [0, by(76)]])];
      out.push({ pts: CV(pts, 3, true), fill: mantle, role: "mantle", paint: F.coarse ? [] : [{ pts: tops([[-7, sh + .5], [0, by(70)], [7, sh + .5]]), w: 2.2, c: F.orphrey ?? "#ece8d8", alpha: 1 }, { pts: [top([0, by(70)]), [0, a[1] - 3]], w: 2.2, c: F.orphrey ?? "#ece8d8", alpha: 1 }, fold([[-9, by(60)], [-8, by(46)], [a[0] * .55, a[1]]], .45), fold([[9, by(60)], [8, by(46)], [b[0] * .55, b[1]]], .45)] });
    } else if (cut === "cloak" || cut === "chlamys") {                  // (its front: over the shoulders and caught at the throat, or on the right shoulder with a brooch)
      if (cut === "cloak") { for (const s of [-1, 1]) out.push({ pts: tops([[s * 2, sh + 1], [s * 9.8, sh + .4], [s * 11, by(72)], [s * 8, by(68)], [s * 3.5, by(74)]]), fill: mantle, role: "mantle", paint: [] }); out.push({ pts: oval(lean, by(75), 1.9, 1.9, 8), fill: F.attr ?? 2, role: "morse", whole: true, paint: [] }); }
      else { const [a, b] = F.bust ? low : sideAt(.86); out.push({ pts: CV([...tops([[10, sh + .5], [3, sh + 2], [-9.8, sh]]), [-12.5, by(62)], [a[0] * .9, by(40)], [a[0] * .8, a[1]], [a[0] * .1, a[1] - 1], [2, by(40)], [5, by(60)], top([9, by(74)])], 2, true), fill: mantle, role: "mantle", paint: F.coarse ? [] : [fold(tops([[8, by(77)], [0, by(68)]]).concat([[-6, by(50)], [a[0] * .55, a[1]]]), .5), fold([[9, by(74)], [2, by(50)], [a[0] * .2, a[1]]], .5), { pts: [[a[0] * .55, by(52)], [-2, by(50)], [-2, by(38)], [a[0] * .55, by(38)]], fill: F.tablion ?? "#d9ae38" }] }); out.push({ pts: oval(9.3 + lean, sh - 1, 2, 2, 8), fill: F.attr ?? 2, role: "morse", whole: true, paint: [] }); }
    } else if (cut === "maphorion") {                                    // (the Virgin's: one cloth from the head to the knees, her hands coming out of it)
      const [a, b] = F.bust ? low : sideAt(.8), pts = [...tops([[-7, sh + 3], [-11.5, by(76)], [-13, by(62)]]), [a[0] * 1.02, by(44)], [a[0] * .95, a[1]], [0, a[1] - 3.5], [b[0] * .95, b[1]], [b[0] * 1.02, by(44)], ...tops([[13, by(62)], [11.5, by(76)], [7, sh + 3], [0, by(74)]])];
      out.push({ pts: CV(pts, 3, true), fill: mantle, role: "mantle", paint: F.coarse ? [] : [fold([top([-8, by(74)]), [-6, by(52)], [a[0] * .55, a[1]]], .55), fold([top([8, by(74)]), [6, by(52)], [b[0] * .55, b[1]]], .55), fold([[0, by(66)], [-.8, by(46)], [0, a[1] - 2]], .5), fold(tops([[-9, by(68)], [0, by(60)], [9, by(68)]]), .45, .7)] });
    } else if (cut === "loros") {                                        // (the emperor's jewelled band: down from the neck, a cross of gold on the tunic)
      const [a, b] = F.bust ? low : sideAt(1), w = 2.8, band = [...tops([[-w, by(76)], [-9, sh + .4], [-9, sh - 3], [-w, by(71)]]), [-w, a[1] + 2], [w, a[1] + 2], ...tops([[w, by(71)], [9, sh - 3], [9, sh + .4], [w, by(76)]])];
      out.push({ pts: band, fill: F.attr ?? 2, role: "mantle", whole: true, paint: F.coarse ? [] : Array.from({ length: 7 }, (_, i) => ({ pts: oval(0, by(68) + (a[1] + 6 - by(68)) * i / 6, .8, .8, 6), fill: "#a81f28" })) });
    }
  }
  if (F.mail != null && !F.bust) out.push({ pts: [...tops([[-9.6, sh + .2], [9.6, sh + .2], [10, by(70)]]), [9, wst - 4], [-9, wst - 4], ...tops([[-10, by(70)]])], fill: F.mail, role: "mail", paint: F.coarse ? [] : Array.from({ length: 8 }, (_, i) => ({ pts: [[-9, wst - 2 + i * (sh - wst) / 8], [9, wst - 2 + i * (sh - wst) / 8]], w: .3, alpha: .7 })) });
  // ARMS and HANDS: what's held between the sleeve and the fingers
  const anchors = {};
  for (const s of ["L", "R"]) {
    const sg = s === "L" ? -1 : 1, [e0, h0] = P[s], sx = sg * 9.5, shoulder = top([sx, sh - .5]);
    let eb = [e0[0], e0[1]], hd = [h0[0], h0[1]];
    if (F.reach?.[s]) { const T = twoBone(shoulder, F.reach[s], 22, 24, sg < 0 ? -1 : 1); eb = T.mid; hd = T.end; }
    const wr = [hd[0] * .9 + eb[0] * .1, hd[1] * .9 + eb[1] * .1], dx = hd[0] - eb[0], dy = hd[1] - eb[1], d = Math.hypot(dx, dy) || 1, ax = [dx / d, dy / d], nr = [-ax[1], ax[0]];
    anchors["hand" + s] = hd; anchors["elbow" + s] = eb;
    const held = F[`hold${s}`], attr = held && CANON.attrs[held];
    if (held && !attr) throw new Error(`no attribute "${held}"`);
    const armC = F.naked ? skin : F.sleeve ?? (F.mantle !== null && !F.bare && cut !== "loros" && !F.short ? mantle : robe);
    out.push({ pts: limb([shoulder, eb, wr], F.naked ? 3.2 : 3.7, F.naked ? 2.4 : 3, 4 - c1 * 2), fill: armC, role: "sleeve", whole: !!F.naked, paint: F.coarse || F.naked ? [] : [fold([[shoulder[0] + sg * -1.2, shoulder[1] - 8], [eb[0] + sg * -2, eb[1] + 1], [eb[0] + (wr[0] - eb[0]) * .3, eb[1] + (wr[1] - eb[1]) * .3]], .5, .85), { pts: [[wr[0] - nr[0] * 3, wr[1] - nr[1] * 3], [wr[0] + nr[0] * 3, wr[1] + nr[1] * 3]], w: 1, alpha: .9 }] });
    if (attr) out.push(...partsOf(attr.parts, { x: hd[0], y: hd[1], flip: 1, spin: (P.grip?.[s] ?? F[`grip${s}`] ?? 0) * Math.PI / 180, tint: (f) => f === "attr" ? attrFill : f === "attr2" ? F.attr2 ?? 4 : f === "skin" ? skin : f == null ? attrFill : typeof f === "string" ? (F.dye ?? slotOf)(f) : f }).map((q) => ({ ...q, whole: q.whole })));
    const kind = F.bless === s || P.hand?.[s] === "bless" ? "bless" : held ? "fist" : P.hand?.[s] ?? "open", H = (u, v) => [hd[0] + ax[0] * u + nr[0] * v, hd[1] + ax[1] * u + nr[1] * v];
    // (the thumb goes to the body's side: a palm shown to us, in either hand. Between the fingers a notch in the outline, as the cartoon would cut it, and the painted line that carries it on into the palm)
    const T = (u, v) => H(u, sg * v), up = (v, u) => [hd[0] - sg * v, hd[1] + u];
    // (the Greek blessing, and the size the icon paints it: the first two fingers up, the last two bent over the palm to the thumb)
    if (kind === "bless" && !F.coarse) out.push({ pts: [up(-2.3, -3), up(-3, .2), up(-3.1, 2.5), up(-2.3, 3.6), up(-1.1, 4), up(-.35, 3.9), up(-.4, 8.6), up(.25, 9.4), up(.95, 8.7), up(1.1, 4.7), up(1.25, 8.9), up(1.9, 9.8), up(2.6, 8.9), up(2.7, 3.2), up(3.7, 2.2), up(4, 1.2), up(3.3, .5), up(2.6, .7), up(2.4, -3)], fill: skin, whole: true, role: "hand", paint: [{ pts: [up(-2.7, 2.2), up(-1, .9), up(1, .6), up(3.2, 1.1)], w: .4, alpha: .9 }, { pts: [up(-1.1, 3.9), up(-1, 1)], w: .3, alpha: .8 }, { pts: [up(1.1, 4.7), up(1.05, 3)], w: .3, alpha: .8 }, { pts: [up(2.3, -2.6), up(1.1, -.8), up(1.2, .5)], w: .3, alpha: .55 }] });
    else if (kind === "point" && !F.coarse) out.push({ pts: [T(-2.6, -2.2), T(.6, -2.9), T(3, -2.7), T(3.8, -1.6), T(3.4, -.9), T(9.4, -.8), T(10, -.1), T(9.4, .7), T(3.4, 1), T(3, 2.8), T(1.6, 3.8), T(-.4, 3), T(-2.6, 2.2)], fill: skin, whole: true, role: "hand", paint: [{ pts: [T(.6, -1.6), T(3, -1)], w: .3, alpha: .7 }] });
    else if (kind === "fist" || F.coarse) out.push({ pts: oval(hd[0] + sg * .2, hd[1], 3.3, 3.5, F.coarse ? 8 : 12), fill: skin, whole: true, role: "hand", paint: F.coarse ? [] : [{ pts: [H(-1.6, -1.8), H(-1.6, 1.8)], w: .4, alpha: .7 }] });
    // (the open hand: four fingers, the middle the longest, and the thumb standing off the palm)
    else out.push({ pts: [T(-2.6, -2.1), T(.6, -2.8), T(3.2, -3), T(5.1, -3.1), T(5.7, -2.5), T(5.3, -1.9), T(3.5, -1.6), T(6.7, -1.65), T(7.2, -1), T(6.9, -.4), T(3.9, -.3), T(7.3, -.25), T(7.9, .35), T(7.4, 1), T(3.9, 1.05), T(6.8, 1.15), T(7.3, 1.8), T(6.8, 2.4), T(3.2, 2.5), T(2.6, 3.2), T(4.2, 5.1), T(4.1, 5.9), T(3.2, 5.8), T(.6, 3.8), T(-.6, 2.7), T(-2.6, 2.1)], fill: skin, whole: true, role: "hand", paint: [{ pts: [T(3.5, -1.6), T(2.1, -1.5)], w: .3, alpha: .75 }, { pts: [T(3.9, -.3), T(2.2, -.3)], w: .3, alpha: .75 }, { pts: [T(3.9, 1.05), T(2.2, 1)], w: .3, alpha: .75 }, { pts: [T(2.4, 2.4), T(.8, 1.7), T(-1.4, 1.5)], w: .3, alpha: .55 }] });
  }
  // NECK, BEARD BEHIND, HEAD
  out.push({ pts: [[lean + hx * .4 - 2.8, sh - .6], [lean + hx * .4 + 2.8, sh - .6], [hx * .7 + lean * .4 + 2.5, hy - 4], [hx * .7 + lean * .4 - 2.5, hy - 4]], fill: skin, role: "neck", whole: true, paint: [] });
  const vh = F.veil != null, cutH = F.hairCut ?? "short";
  if (vh) out.push({ pts: CV([[hx - 7, hy + 7.5], [hx - 9.5, hy - 2], ...tops([[-10, sh - 14], [-7.5, sh - 3]]), top([0, sh - .5]), ...tops([[7.5, sh - 3], [10, sh - 14]]), [hx + 9.5, hy - 2], [hx + 7, hy + 7.5], [hx, hy + 9.5]], 3, true), fill: F.veil, role: "veil", paint: [fold([[hx - 7.5, hy - 2], top([-8, sh - 8])], .5), fold([[hx + 7.5, hy - 2], top([8, sh - 8])], .5)] });
  else if (cutH === "long") out.push({ pts: CV([[hx - 6.1, hy + 3], [hx - 7.6, hy - 3], [hx - 8.2, hy - 11], [hx - 5, hy - 14], [hx - 3.6, hy - 7], [hx + 3.6, hy - 7], [hx + 5, hy - 14], [hx + 8.2, hy - 11], [hx + 7.6, hy - 3], [hx + 6.1, hy + 3], [hx + 5.6, hy + 7.2], [hx, hy + 8.4], [hx - 5.6, hy + 7.2]], 3, true), fill: hair, role: "hair", paint: [fold([[hx - 6, hy + 4], [hx - 7, hy - 4], [hx - 6.4, hy - 12]], .4, .7), fold([[hx + 6, hy + 4], [hx + 7, hy - 4], [hx + 6.4, hy - 12]], .4, .7)] });
  else out.push({ pts: CV([[hx - 6.1, hy + 3], [hx - 6.8, hy - 3], [hx - 4.5, hy - 7], [hx + 4.5, hy - 7], [hx + 6.8, hy - 3], [hx + 6.1, hy + 3], [hx + 5.6, hy + 7.2], [hx, hy + 8.4], [hx - 5.6, hy + 7.2]], 3, true), fill: hair, role: "hair", paint: [fold([[hx - 5, hy + 6], [hx - 6, hy + 1], [hx - 5.6, hy - 4]], .4, .7), fold([[hx + 5, hy + 6], [hx + 6, hy + 1], [hx + 5.6, hy - 4]], .4, .7)] });
  // the face: an oval, one sheet; everything on it is paint: arched brows run into the long nose, almond eyes looking where he turns
  const fx = hx + turn * 1.2, E = hy + 1.5, eye = (s) => {
    const cx = fx + s * 2.5, ix = cx + turn * .7;
    return [{ pts: curve([[cx - 1.6, E], [cx, E + .85], [cx + 1.6, E], [cx, E - .55]], 4, true), w: .36, closed: true }, { pts: oval(ix, E + .12, .68, .68, 8), fill: INK }, { pts: curve([[cx - s * -2 * -1 + s * .1, E + 2.3 - .2], [cx + s * .2, E + 2.5], [cx + s * 2, E + 1.8]].sort((a, b) => a[0] - b[0]), 4), w: .5 }];
  };
  const face = F.coarse ? [...[-1, 1].map((s) => ({ pts: oval(fx + s * 2.5, E, 1, .8, 6), fill: INK })), { pts: [[fx, E], [fx, E - 3.4]], w: .6 }, { pts: [[fx - 1.6, E - 5.6], [fx + 1.6, E - 5.6]], w: .6 }] : [
    ...eye(-1), ...eye(1),
    { pts: curve([[fx - .5 + turn * .5, E + 2.2], [fx - .35 + turn * 1, E - 1], [fx - .9 + turn * 1.3, E - 3.2], [fx + .7 + turn * 1.3, E - 3.5]], 3), w: .42 },
    { pts: [[fx - 1.6, E - 5.6], [fx + 1.6, E - 5.6]], w: .42 },
    { pts: curve([[fx - 1.4, E - 5.7], [fx, E - 6.2], [fx + 1.4, E - 5.7]], 3), w: .25, alpha: .75 },
    { pts: curve([[hx - 3.8, E - 2], [hx - 2.6, E - 3.5], [hx - 1.8, E - 2]], 4), w: 2.2, alpha: .09 },
    { pts: curve([[hx + 3.8, E - 2], [hx + 2.6, E - 3.5], [hx + 1.8, E - 2]], 4), w: 2.2, alpha: .09 },
  ];
  out.push({ pts: CV([[hx - 5, hy + 4], [hx - 5.1, hy - .5], [hx - 3.4, hy - 5], [hx, hy - 7], [hx + 3.4, hy - 5], [hx + 5.1, hy - .5], [hx + 5, hy + 4], [hx + 2.8, hy + 6.3], [hx - 2.8, hy + 6.3]], 3, true), fill: skin, whole: true, role: "face", paint: face });
  const headed = F.hood != null || F.cap != null || F.helmet != null || F.turban != null || F.tiara != null || F.mitre != null || F.hat != null;
  if (vh) out.push({ pts: CV([[hx - 5.6, hy + 2.5], [hx - 4.5, hy + 7], [hx, hy + 8.8], [hx + 4.5, hy + 7], [hx + 5.6, hy + 2.5], [hx, hy + 5.7]], 3, true), fill: F.veil, role: "veil", paint: [] });
  else if (cutH === "tonsure") { for (const s of [-1, 1]) out.push({ pts: CV([[hx + s * 5.7, hy + 4.4], [hx + s * 4.6, hy + 6.2], [hx + s * 2, hy + 5.9], [hx + s * 2.8, hy + 4.4], [hx + s * 4.2, hy + 2.8], [hx + s * 4.9, hy - .4], [hx + s * 6, hy + .5]], 2, true), fill: hair, role: "fringe", paint: [] }); }
  else if (cutH === "bald") { /* (Paul's forehead: only what's behind) */ }
  else if (!headed || F.hood == null && F.helmet == null) out.push({ pts: CV([[hx - 5.6, hy + 2.2], [hx - 4.8, hy + 6.8], [hx - 1, hy + 8.4], [hx + 4.8, hy + 6.8], [hx + 5.6, hy + 2.2], [hx + 3.4, hy + 5], [hx, hy + 5.6], [hx - 3.4, hy + 5]], 3, true), fill: hair, role: "fringe", paint: F.coarse ? [] : [fold([[hx - 2, hy + 8], [hx - 1.5, hy + 6]], .35, .7), fold([[hx + 2, hy + 8], [hx + 1.5, hy + 6]], .35, .7)] });
  if (F.beard != null) { const long = F.beardCut === "long", low = long ? hy - 15 : F.beardCut === "short" ? hy - 8.6 : hy - 11.5; out.push({ pts: CV([[hx - 5, hy - 1], [hx - 4.2, (hy - 1 + low) / 2 - 1], [hx, low], [hx + 4.2, (hy - 1 + low) / 2 - 1], [hx + 5, hy - 1], [hx + 2, hy - 3.8], [fx, hy - 4.3], [hx - 2, hy - 3.8]], 3, true), fill: F.beard, role: "beard", paint: F.coarse ? [] : [fold([[hx - 2, hy - 5], [hx - 1, low + 1.5]], .35, .8), fold([[hx, hy - 5], [hx, low + .5]], .35, .8), fold([[hx + 2, hy - 5], [hx + 1, low + 1.5]], .35, .8)] }); }
  // WHAT'S ON HIS HEAD
  const lid = (fill, role, pts, paint = []) => out.push({ pts, fill, whole: true, role, paint });
  if (F.crown != null) lid(F.crown, "crown", [[hx - 5.6, hy + 4.5], [hx + 5.6, hy + 4.5], [hx + 6.2, hy + 10.5], [hx + 3.1, hy + 7.5], [hx, hy + 11.5], [hx - 3.1, hy + 7.5], [hx - 6.2, hy + 10.5]], [{ pts: [[hx - 5.6, hy + 5.8], [hx + 5.6, hy + 5.8]], w: .5 }]);
  if (F.diadem != null) { lid(F.diadem, "crown", [[hx - 5.8, hy + 3.6], [hx + 5.8, hy + 3.6], [hx + 6, hy + 8.6], [hx + 3, hy + 10], [hx - 3, hy + 10], [hx - 6, hy + 8.6]], [...[-3.4, 0, 3.4].map((q) => ({ pts: oval(hx + q, hy + 6.4, .9, .9, 6), fill: "#a81f28" }))]); if (!F.coarse) for (const s of [-1, 1]) lid(F.diadem, "crown", [[hx + s * 5, hy + 3.8], [hx + s * 6.2, hy + 3.8], [hx + s * 6.4, hy - 3], [hx + s * 5.2, hy - 3]], [{ pts: oval(hx + s * 5.8, hy - 1, .7, .7, 6), fill: "#efe8d8" }]); }
  if (F.mitre != null) lid(F.mitre, "mitre", [[hx - 5.4, hy + 4.5], [hx + 5.4, hy + 4.5], [hx + 4.8, hy + 11], [hx, hy + 16], [hx - 4.8, hy + 11]], [{ pts: [[hx, hy + 4.5], [hx, hy + 16]], w: .7 }, { pts: [[hx - 5.4, hy + 6], [hx + 5.4, hy + 6]], w: .7 }]);
  if (F.tiara != null) lid(F.tiara, "mitre", CV([[hx - 5.2, hy + 4.5], [hx + 5.2, hy + 4.5], [hx + 4.8, hy + 9], [hx + 3, hy + 14], [hx, hy + 17], [hx - 3, hy + 14], [hx - 4.8, hy + 9]], 2), [{ pts: [[hx - 5.2, hy + 7], [hx + 5.2, hy + 7]], w: .9 }, { pts: [[hx - 4.2, hy + 11], [hx + 4.2, hy + 11]], w: .9 }]);
  if (F.hood != null) out.push({ pts: CV([[hx - 7, hy - 7], [hx - 7.5, hy + 2], [hx - 5, hy + 9], [hx, hy + 11.5], [hx + 5, hy + 9], [hx + 7.5, hy + 2], [hx + 7, hy - 7], [hx + 5.4, hy - 5.4], [hx + 5.2, hy + 1], [hx + 3.6, hy + 5], [hx, hy + 6], [hx - 3.6, hy + 5], [hx - 5.2, hy + 1], [hx - 5.4, hy - 5.4]], 2, true), fill: F.hood, role: "hood", paint: [] });
  if (F.cap != null) lid(F.cap, "cap", CV([[hx - 5.8, hy + 3.6], [hx - 6, hy + 8], [hx - 2, hy + 11.5], [hx + turn * 6 + (turn >= 0 ? 4 : -4), hy + 12], [hx + 4 * Math.sign(turn || 1), hy + 8.4], [hx + 5.8, hy + 3.6]], 2), [{ pts: [[hx - 5.8, hy + 4.8], [hx + 5.8, hy + 4.8]], w: .5 }]);   // (a Phrygian's or a Magus's, the tip falling forward)
  if (F.hat != null) lid(F.hat, "hat", [...CV([[hx - 11, hy + 4], [hx - 5, hy + 5.8], [hx - 4.4, hy + 10.6], [hx, hy + 11.8], [hx + 4.4, hy + 10.6], [hx + 5, hy + 5.8], [hx + 11, hy + 4]], 2), [hx + 8, hy + 3], [hx - 8, hy + 3]]);
  if (F.turban != null) lid(F.turban, "cap", CV([[hx - 6.4, hy + 3.4], [hx - 7.4, hy + 7.5], [hx - 3.6, hy + 12], [hx + 3.6, hy + 12], [hx + 7.4, hy + 7.5], [hx + 6.4, hy + 3.4]], 2), [{ pts: curve([[hx - 6.6, hy + 7], [hx, hy + 5], [hx + 6.6, hy + 9]], 3), w: .5 }, { pts: curve([[hx - 6, hy + 10], [hx, hy + 8], [hx + 6, hy + 11]], 3), w: .5 }]);
  if (F.helmet != null) lid(F.helmet, "helmet", [...CV([[hx - 5.9, hy + 1.6], [hx - 5.6, hy + 7.5], [hx, hy + 12.5], [hx + 5.6, hy + 7.5], [hx + 5.9, hy + 1.6]], 2), [hx + .9 + turn, hy + 1.6], [hx + .7 + turn, hy - 2.6], [hx - .7 + turn, hy - 2.6], [hx - .9 + turn, hy + 1.6]], [{ pts: [[hx - 5.9, hy + 3], [hx + 5.9, hy + 3]], w: .6 }, { pts: [[hx, hy + 3], [hx, hy + 12]], w: .5 }]);
  if (F.wreath != null) lid(F.wreath, "crown", [[hx - 6.4, hy + 3.2], [hx + 6.4, hy + 3.2], [hx + 6.8, hy + 6.2], [hx + 4.6, hy + 5.6], [hx + 3.2, hy + 7.6], [hx + 1.4, hy + 6], [hx, hy + 8], [hx - 1.4, hy + 6], [hx - 3.2, hy + 7.6], [hx - 4.6, hy + 5.6], [hx - 6.8, hy + 6.2]], [{ pts: [[hx - 5, hy + 4.6], [hx + 5, hy + 4.6]], w: .5 }]);   // (leaves stand up from the band)
  anchors.head = top([0, hy + 4]); anchors.chest = top([0, by(72)]); anchors.throat = top([0, sh]); anchors.belly = [0, wst - 4]; anchors.lap = P.lap ?? [0, by(50)]; anchors.shoulder = top([0, sh + 3]); anchors.foot = [0, 4];
  anchors.shoulderL = top([-9, sh + 3]); anchors.shoulderR = top([9, sh + 3]); anchors.hip = [0, wst - 12];
  if (P.rot) {                                                          // (lying down: stood up, built, and tipped over, about the feet)
    const a = P.rot * Math.PI / 180, cs = Math.cos(a), sn = Math.sin(a), [px, py] = P.rotAt ?? [0, 0], R = ([x, y]) => [px + x * cs - y * sn, py + x * sn + y * cs];
    for (const q of out) { q.pts = q.pts.map(R); if (q.paint) for (const l of q.paint) l.pts = l.pts.map(R); }
    for (const k of Object.keys(anchors)) anchors[k] = R(anchors[k]);
  }
  out.anchors = anchors;
  if (F.bust === "head") { const cut = sh - 13, kept = out.flatMap((p) => { const pts = clipAbove(p.pts, cut); return pts.length < 3 ? [] : [{ ...p, pts, paint: p.paint?.filter((q) => !q.pts || q.pts.some((v) => v[1] > cut)) }]; }); kept.anchors = anchors; return kept; }   // (a season's head as the Romans set it in a corner: head and shoulders, what's below the cut left out)
  return out;
}
const clipAbove = (pts, y) => { const out = []; pts.forEach((a, i) => { const b = pts[(i + 1) % pts.length], A = a[1] >= y, B = b[1] >= y; if (A) out.push(a); if (A !== B) { const t = (y - a[1]) / (b[1] - a[1]); out.push([a[0] + (b[0] - a[0]) * t, y]); } }); return out; };

// pieces, moved and scaled; a line's width scales with them
export const placed = (pieces, s, dx, dy, flip = 1) => pieces.map((p) => ({ ...p, pts: p.pts.map(([x, y]) => [dx + flip * x * s, dy + y * s]), paint: p.paint?.map((q) => ({ ...q, w: q.w === undefined ? undefined : q.w * s, pts: q.pts.map(([x, y]) => [dx + flip * x * s, dy + y * s]) })) }));
