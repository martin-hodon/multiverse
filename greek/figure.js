// GREEK PAINTINGS, the figure (docs/greek.md): a solved pose (rig.js) as PIECES, what every technique draws alike --
//   { z, owner, role: "skin"|"hair"|"cloth"|..., rings: [[[x, y, corner?], ...], ...], lines: [{ cls, pts }], marks: [{ cls, at, r }] }
// rings are the piece's outline (filled as one, so a limb is thigh + calf + foot with no line across its joints), in world
// vertices, never transforms, so a field may warp them. Built in the pose's forward space and placed at the end.

import { drape } from "./drape.js";
import { shieldCentre } from "./rig.js";

const lerp = (a, b, t) => a + (b - a) * t;
// an outline round a bone from its widths: [t, in front, behind] ("front" the side a limb bends toward)
function limb(a, b, prof, k = 1) {
  const dx = b[0] - a[0], dy = b[1] - a[1], ax = -dy, ay = dx, l = Math.hypot(dx, dy) || 1, nx = ax / l, ny = ay / l;
  const at = (t, s) => [a[0] + dx * t + nx * s, a[1] + dy * t + ny * s];
  const front = prof.map(([t, f]) => at(t, f * k)), back = prof.map(([t, , h]) => at(t, -h * k)).reverse();
  // (rounded ends past the first and last widths, so a limb's end is never a stump where it shows)
  const e0 = prof[0], e1 = prof[prof.length - 1], cap = (t, f, h, out) => at(t + out * (f + h) * k * .42 / (l || 1), (f - h) * k / 2);
  return { ring: [cap(e0[0], e0[1], e0[2], -1), ...front, cap(e1[0], e1[1], e1[2], 1), ...back], at };
}
// a shape of the data's, from its own origin: scaled, turned, flipped, moved
const shapeAt = (pts, o, s, rot = 0, flip = 1) => {
  const c = Math.cos(rot), n = Math.sin(rot);
  return pts.map(([x, y, k]) => { const X = x * s * flip, Y = y * s, q = [o[0] + X * c + Y * n, o[1] - X * n + Y * c]; return k ? [q[0], q[1], 1] : q; });
};
const angle = (a, b) => Math.atan2(b[0] - a[0], b[1] - a[1]);    // (from up, clockwise: forward positive)

export function buildFigure(data, pose, who = {}, periodName = "classical") {
  const D = data.canon, C = D.lengths, per = D.periods[periodName] ?? D.periods.classical, out = [];
  const female = who.sex === "f", skin = who.skin ?? (female ? "skinF" : "skin");
  const piece = (slot, role, rings, lines = [], marks = []) => out.push({ z: slot, owner: who.id ?? 0, role, rings, lines, marks });
  const line = (cls, pts) => ({ cls, pts });

  // ---- a leg: thigh, calf, foot as one
  const legOf = (L, near) => {
    const th = limb(L.hip, L.knee, D.thigh, per.thigh * (female ? 1.04 : 1)), sh = limb(L.knee, L.ankle, D.shin, per.shin * (female ? .92 : 1));
    const footPts = shapeAt(D.foot, L.ankle, 1, L.pitch + 0), kneeR = D.thigh.at(-1)[1] * per.thigh * .96, cap = Array.from({ length: 10 }, (_, i) => [L.knee[0] + Math.cos(-i * .628) * kneeR, L.knee[1] + Math.sin(-i * .628) * kneeR]);   // (the two bones meet in one round knee, not two ends with a notch)
    const lines = [line("detail", [sh.at(-.02, 3.2), sh.at(.03, 1.2), sh.at(.08, 2.4)]), line("fine", [sh.at(.2, -1.2), sh.at(.34, -2.2), sh.at(.54, -1.7)])];
    if (near) lines.push(line("fine", [th.at(.45, 3.2), th.at(.72, 2.6), th.at(.9, 2.6)]));
    lines.push(line("fine", [shapeAt([[-.8, -.2]], L.ankle, 1, L.pitch)[0], shapeAt([[.6, 1]], L.ankle, 1, L.pitch)[0]]));
    if (who.greaves) {                                       // (bronze over the shin, from under the knee to the ankle)
      const gv = limb(L.knee, L.ankle, D.shin.filter(([t]) => t > 0), per.shin * 1.08);
      piece(near ? 42 : 21, "metal", [gv.ring], [line("fine", [gv.at(.25, -1), gv.at(.4, -2.6), gv.at(.62, -1.8)])]);
    }
    if (who.hose) {                                          // (patterned leggings, hip to ankle, zigzag bands across them)
      const zig = (b, t, w) => line("detail", [-1, -.5, 0, .5, 1].map((u, i) => b.at(t + (i % 2 ? .035 : -.035), u * w)));
      piece(near ? 42 : 21, "cloth", [th.ring, sh.ring], [.3, .5, .7, .9].flatMap((t) => [zig(th, t, 4.2), zig(sh, t, 3)]));
      out.at(-1).tint = (who.tint ?? 0) + 1;
    }
    if (near) return { rings: [th.ring, cap, sh.ring, footPts], lines };
    piece(20, skin, [th.ring, cap, sh.ring, footPts], lines);
  };
  // ---- an arm: upper, fore, hand as one
  const armOf = (A, near) => {
    const up = limb(A.sh, A.el, D.upper, per.upper * (female ? .84 : 1)), fo = limb(A.el, A.wr, D.fore, per.fore * (female ? .84 : 1));
    const holds = A.fist || who.props?.[A.side] || (who.shield && A.side === "L");
    const rot = angle(A.wr, A.hand) - Math.PI / 2, hand = shapeAt(holds ? D.handFist : D.handOpen, A.wr, 1, rot);
    const lines = [line("fine", [fo.at(-.04, 1.8), fo.at(.1, .4), fo.at(.3, .3)])];
    if (!holds) for (const l of D.handLines) lines.push(line("fine", shapeAt(l, A.wr, 1, rot)));
    piece(near ? 60 : 10, skin, [up.ring, fo.ring, hand], lines);
  };

  // ---- the trunk: its outline blends side and front views by |turn|, along the bent spine, and the neck
  const T = Math.abs(pose.turn), spineAt = (t) => {
    const pts = [pose.pelvis, pose.waist, pose.chest], ls = [0, .45, 1];
    const tt = Math.max(0, Math.min(1, t)), i = tt < .45 ? 0 : 1, u = (tt - ls[i]) / (ls[i + 1] - ls[i]);
    const p = [lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u)];
    const lean = i ? Math.atan2(pose.chest[0] - pose.waist[0], pose.chest[1] - pose.waist[1]) : Math.atan2(pose.waist[0] - pose.pelvis[0], pose.waist[1] - pose.pelvis[1]);
    const over = t - tt, nx = Math.cos(lean), ny = -Math.sin(lean);
    return { p: [p[0] + Math.sin(lean) * over * C.trunk, p[1] + Math.cos(lean) * over * C.trunk], nx, ny };
  };
  const slim = (t) => {                                           // (a period's waist and chest; a woman's narrower shoulders)
    const w = Math.exp(-(((t - .38) / .2) ** 2)), c = Math.exp(-(((t - .8) / .2) ** 2));
    return 1 + (per.waist - 1) * w + (per.chest - 1) * c - (female ? .1 * c + .05 * w : 0);
  };
  const front = [], back = [];
  D.torsoSide.forEach(([t, sf, sb], i) => {
    const [, ff, fb] = D.torsoFront[i], k = slim(t), { p, nx, ny } = spineAt(t);
    const f = lerp(sf, ff, T) * k, b = lerp(sb, fb, T) * k;
    front.push([p[0] + nx * f, p[1] + ny * f]); back.push([p[0] - nx * b, p[1] - ny * b]);
  });
  const torsoRing = [...front, ...back.reverse()];
  const neck = limb(pose.chest, [pose.headBase[0] + Math.sin(pose.lean) * 3, pose.headBase[1] + Math.cos(pose.lean) * 3], [[0, D.neckW * 1.3, D.neckW * 1.3], [.6, D.neckW, D.neckW], [1, D.neckW, D.neckW]]);
  const tl = [];
  const on = (t, s) => { const q = spineAt(t); return [q.p[0] + q.nx * s, q.p[1] + q.ny * s]; };
  if (pose.turn > .2) {                                           // the chest: the middle line slides forward as the trunk turns away from us, the pectorals, the ribs' arch, the hip's fold
    const mid = (1 - T) * 7.5 * (1 - .15), half = 10.5 * T;
    for (const k of [1, -1]) {
      tl.push(line("detail", [on(.71, mid + k * half * .06), on(.65, mid + k * half * .55), on(.79, mid + k * half * .98)]));
      tl.push(line("fine", [on(.58, mid + k * half * .8), on(.5, mid + k * half * .32), on(.54, mid)]));
    }
    tl.push(line("fine", [on(.84, mid), on(.5, mid), on(.18, mid)]));
    for (const t of [.42, .3]) tl.push(line("fine", [on(t + .01, mid - half * .3), on(t - .01, mid), on(t + .01, mid + half * .3)]));
    tl.push(line("fine", [on(.17, mid + half * .9), on(.08, mid + half * .5)]));   // (a fold at the hip, not two that meet: those read as a garment)
  } else if (pose.turn < -.2) {                                    // a back: the spine's groove, the shoulder blade
    const mid = (1 - T) * -7.5;
    tl.push(line("fine", [on(.92, mid), on(.5, mid * 1.05), on(.1, mid)]), line("fine", [on(.84, mid + 5), on(.68, mid + 7)]));
  } else tl.push(line("fine", [on(.7, 7), on(.62, 8), on(.5, 6.5)]));
  const nearLeg = who.noLegs ? { rings: [], lines: [] } : legOf(pose.near.leg, true);                    // (the near leg and the trunk one outline, parted by the groin's line alone)
  tl.push(line("fine", [on(.05, 8), on(-.03, 4), on(-.1, 1.5)]));
  piece(40, skin, [torsoRing, neck.ring, ...nearLeg.rings], [...tl, ...nearLeg.lines]);

  // ---- the head, drawn over the neck, in profile; the eye frontal or in profile as the period has it
  const hs = C.head * per.head, flip = pose.lookBack ? -1 : 1, ho = pose.headBase, rot = pose.tilt * flip;
  const H = (pts) => shapeAt(pts, ho, hs, rot, flip);
  const eye = per.eye > .5 ? D.eyeFront : D.eyeSide;
  const pupil = shapeAt([[per.eye > .5 ? .275 : .3, .61]], ho, hs, rot, flip)[0];
  const faceLines = [line("detail", H([[.385, .265], [.3, .25]])), line("detail", H(D.brow)), { cls: "detail", pts: H(eye), closed: true }];
  const faceMarks = [{ cls: "detail", at: pupil, r: hs * (per.eye > .5 ? .032 : .024) }];
  piece(50, skin, [H(who.satyr ? D.headSatyr : D.head)], [...faceLines, line("fine", H(D.ear))], faceMarks);
  const rings = [H(who.satyr ? D.hairSatyr : who.hair === "long" ? D.hairLong : D.hairCap)];
  if (who.hair === "bun") rings.push(H(D.bun));
  const hairLines = [];
  const nh = who.hair === "long" ? 4 : 3;
  for (let i = 0; i < nh; i++) { const a = .22 - i * .18; hairLines.push(line("fine", H([[a, .95 - i * .02], [a - .1, .8 - i * .02], [a - .12, .6]]))); }
  piece(52, who.white ? "white" : "hair", rings, who.satyr ? [] : hairLines);
  if (who.beard) piece(53, who.white ? "white" : "beard", [H(D.beard)], [line("fine", H([[.16, .28], [.28, .08], [.34, -.1]])), line("fine", H([[.06, .22], [.14, 0], [.2, -.1]]))]);

  // ---- limbs, near over the trunk and far under it
  if (!who.noLegs) legOf(pose.far.leg, false);
  const farHidden = who.dress && !who.shield && !who.props?.[pose.far.arm.side] && Math.abs(pose.far.arm.hand[0] - pose.pelvis[0]) < 12 && pose.far.arm.hand[1] < pose.chest[1];
  if (!farHidden && !who.noArms) armOf(pose.far.arm, false);                    // (a far hand down inside a long dress does not show)
  if (!who.noArms) armOf(pose.near.arm, true);
  // ---- a cap or a lion's scalp over the head; a satyr's ears and tail
  if (who.gear) {
    const G = data.parts.headgear[who.gear];
    piece(54, G.role ?? "metal", [H(G.ring)], (G.lines ?? []).map((l) => line("fine", H(l))), (G.marks ?? []).map(([a, b, r]) => ({ cls: "detail", at: H([[a, b]])[0], r: r * hs })));
    if (G.role === "cloth2") out.at(-1).tint = (who.tint ?? 0) + 1;   // (a cloth cap in the colours of the clothes)
  }
  if (who.satyr) {
    piece(53.5, skin, [H(D.earSatyr)]);
    piece(7, "hair", [shapeAt(D.tail, pose.pelvis, 1, 0)], [line("fine", shapeAt([[-6, 2], [-20, 1], [-30, -14]], pose.pelvis, 1, 0))]);
  }
  if (who.ivy) for (let i = 0; i < 6; i++) {
    const a = i / 5, q = [.32 - a * .78, .92 - Math.abs(a - .42) * -.14 - a * .24];
    piece(56, "crest", [H([[q[0] - .06, q[1]], [q[0], q[1] + .08, 1], [q[0] + .06, q[1]], [q[0], q[1] - .06, 1]])]);
  }
  // ---- something carried on the head, the raised hand to it
  if (who.carry) {
    const pr = data.parts.props[who.carry], top = H([[.02, 1.02]])[0];
    piece(57, pr.role ?? "metal", pr.rings.map((r) => r.map(([x, y, k]) => k ? [top[0] + x, top[1] + y, 1] : [top[0] + x, top[1] + y])), [line("hem", [[top[0] - 7, top[1] + 4], [top[0], top[1] + 3], [top[0] + 7, top[1] + 4]])]);
  }

  // ---- a helmet over the head, its crest behind it
  if (who.helmet) {
    const hm = data.parts.helmets[who.helmet];
    piece(54, "metal", [H(hm.ring)], (hm.lines ?? []).map((l) => line("fine", H(l))));
    if (hm.eye) piece(55, skin, [H(hm.eye)], [], [{ cls: "detail", at: H([[.3, .6]])[0], r: hs * .03 }]);
    const cr = data.parts.crests[who.crest ?? "tall"];
    if (cr) piece(49, "crest", [H(cr.ring)], cr.hatch.map(([a, b, c, d]) => line("detail", H([[a, b], [c, d]]))));
  }
  // ---- a linen or bronze corslet over the trunk, its flaps below
  if (who.cuirass) {
    const up = D.torsoSide.map(([t], i) => t).filter((t) => t >= 0 && t < 1), f2 = [], b2 = [];
    for (const t of up) {
      const i = D.torsoSide.findIndex((q) => q[0] === t), [, sf, sb] = D.torsoSide[i], [, ff, fb] = D.torsoFront[i], k = slim(t) * 1.04, q = spineAt(t);
      f2.push(on(t, lerp(sf, ff, T) * k)); b2.push(on(t, -lerp(sb, fb, T) * k));
    }
    const flaps = [];
    for (let i = 0, n = 5; i < n; i++) {
      const u0 = i / n, u1 = (i + .88) / n, s0 = lerp(9, -9, u0), s1 = lerp(9, -9, u1);
      flaps.push([[...on(.06, s0)], [...on(-.22, s0), 1], [...on(-.22, s1), 1], [...on(.06, s1)]]);
    }
    piece(46, "metal", flaps, []);
    piece(47, "metal", [[...f2, ...b2.reverse()]], [line("detail", [on(.08, 9), on(.05, 0), on(.08, -9)]), line("fine", [on(.74, 8), on(.84, 2), on(.74, -6)])]);
  }
  // ---- a shield on the left forearm: the near arm shows its face and blazon, the far arm its inside with the arm through it
  if (who.shield) {
    const A = pose.arms.L, nearS = pose.nearSide === "L", R = data.canon.shieldR, open = nearS ? .94 : .76;
    const c = shieldCentre(pose);
    const tilt = angle(A.el, A.wr) * .1;
    const disc = (u, v) => { const X = u * R * open, Y = v * R; return [c[0] + X * Math.cos(tilt) + Y * Math.sin(tilt), c[1] - X * Math.sin(tilt) + Y * Math.cos(tilt)]; };
    const shape = data.parts.shapes[who.shield.shape];
    const ring = (k) => shape ? shape.map(([u, v, q]) => { const w = disc(u * k, v * k); return q ? [w[0], w[1], 1] : w; }) : Array.from({ length: 28 }, (_, i) => disc(Math.cos(i / 28 * Math.PI * 2) * k, Math.sin(i / 28 * Math.PI * 2) * k));
    const closed = (pts, cls) => ({ cls, pts, closed: true });
    if (nearS) {
      piece(70, "metal", [ring(1)], [closed(ring(.88), "detail")]);
      const bz = shape ? null : data.parts.blazons[who.shield.blazon];
      if (bz) {
        const m = (l) => l.map(([u, v, k]) => { const q = disc(u * .68, v * .68); return k ? [q[0], q[1], 1] : q; });
        piece(71, "blazon", bz.rings.map(m), (bz.cut ?? []).map((l) => line("detail", m(l))), (bz.dots ?? []).map(([u, v, d]) => ({ cls: "detail", at: disc(u * .68, v * .68), r: d * R * .68 })));
        out[out.length - 1].noContour = 1;
      }
    } else {
      const mid = disc(0, 0);
      piece(8, shape ? "metal" : "shieldIn", [ring(1)], shape ? [closed(ring(.88), "detail")] : [closed(ring(.88), "detail"), line("detail", [disc(-.8, .4), disc(.6, -.1)]), line("detail", [disc(-.8, -.4), disc(.6, -.3)])]);   // (a round shield's arm-band and strap: a crescent's shape is its own)
    }
  }
  // ---- what a hand holds: a shaft through the fist, aimed; or a thing in the fist
  for (const side of ["R", "L"]) {
    const name = who.props?.[side], pr = name && data.parts.props[name];
    if (!pr) continue;
    const A = pose.arms[side], near = pose.nearSide === side, z = near ? 59 : 9, aim = who.aims?.[side];
    const G = A.hand;
    let dx, dy, tipAt = null;
    const aimed = aim && [(aim[0] - pose.x) * pose.dir / pose.scale, (aim[1] - pose.y) / pose.scale];
    const dist = aimed ? Math.hypot(aimed[0] - G[0], aimed[1] - G[1]) : 0;
    if (aimed && (!pr.short || (dist < 92 && G[0] > pose.chest[0] && aimed[0] - G[0] > Math.abs(aimed[1] - G[1]) * .6))) {   // (a blade or club goes at what is before it: right under the hand, it would only hang)
      dx = aimed[0] - G[0]; dy = aimed[1] - G[1]; tipAt = dist; }
    else if (pr.shaft && pr.tip) { dx = .22; dy = 1; } else if (pr.up || pr.tip) { dx = 1; dy = pr.tip ? -.22 : 0; } else if (pr.staff) { dx = .1; dy = 1; } else { dx = A.hand[0] - A.wr[0]; dy = A.hand[1] - A.wr[1]; if (pr.shaft) { dx = Math.abs(dx) + 4; dy = dy * .4; } }
    const l = Math.hypot(dx, dy) || 1, length = pr.short && !pr.at && !pr.shaft ? Math.max(...[...pr.rings, ...(pr.more?.rings ?? [])].flat().map((q) => q[0])) : 0, over = length && dy > 0 && tipAt === null && who.top ? ((who.top - pose.y) / pose.scale - G[1]) / length : 1;
    const uy = over < dy / l ? Math.max(0, over) : dy / l;
    let ux = over < dy / l ? (dx < 0 || G[0] < pose.chest[0] ? -1 : 1) * Math.sqrt(1 - uy * uy) : dx / l;   // (a raised club or blade swung back or forward rather than through the top of the field)
    if (length && tipAt === null && who.side) { const tip = pose.x + pose.dir * (G[0] + ux * length) * pose.scale; if (tip < who.side[0] || tip > who.side[1]) ux = -ux; }   // (nor through its side: a blade cut off there leaves a man with a hilt)
    const nx = -uy, ny = ux;
    const at = ([x, y, k]) => { const q = [G[0] + ux * x + nx * y, G[1] + uy * x + ny * y]; return k ? [q[0], q[1], 1] : q; };
    if (pr.shaft) {
      // (the point on what it is aimed at, the shaft sliding through the fist, within reason; never through)
      const free = pr.shaft * (1 - pr.grip), tipLen = Math.max(...pr.head.map((q) => q[0])), want = tipAt !== null ? Math.min(pr.shaft * .85, Math.max(free * .5, tipAt - (who.hits?.[side] ? 0 : tipLen))) : free, room = uy > .05 && who.top ? ((who.top - pose.y) / pose.scale - G[1]) / uy - tipLen : Infinity;
      const wx = ux * pose.dir, gx = pose.x + G[0] * pose.dir, ahead = who.side && Math.abs(wx) > .05 ? ((wx > 0 ? who.side[1] : who.side[0]) - gx) / wx : Infinity, behind = who.side && Math.abs(wx) > .05 ? ((wx > 0 ? who.side[0] : who.side[1]) - gx) / wx : -Infinity;   // (a panel's sides, along the shaft)
      const b = Math.max(4, Math.min(want, room, ahead - tipLen)), a = Math.min(-4, Math.max(b - pr.shaft, behind + (pr.butt ?? 0), uy < -.05 && who.top ? ((who.top - pose.y) / pose.scale - G[1]) / uy + (pr.butt ?? 0) : -Infinity, uy > .05 ? -(pose.y + G[1]) / uy + (pr.butt ?? 0) : -Infinity)), w = pr.w;   // (held lower rather than through the top of the field or a panel's side; a butt going there, or into the ground, cut short)
      piece(z, "wood", [[[a, w, 1], [b, w, 1], [b, -w, 1], [a, -w, 1]].map(at)]); out.at(-1).shaft = 1;
      if (!who.hits?.[side]) { piece(z + .1, pr.headRole ?? "metal", [pr.head.map(([x, y, k]) => at([b + x, y, k]))]); out.at(-1).shaft = 1; }
      if (pr.butt) { piece(z + .1, "metal", [[[a, w * 1.4, 1], [a + pr.butt, w * 1.4, 1], [a + pr.butt, -w * 1.4, 1], [a - 1, 0, 1], [a, -w * 1.4, 1]].map(at)]); out.at(-1).shaft = 1; }
    } else {
      piece(z, pr.role ?? "metal", pr.rings.map((r) => r.map(at)), (pr.lines ?? []).map((l) => line("fine", l.map(at))));
      if (length) out.at(-1).shaft = 1;                                // (like a shaft: the bodies size a panel, not what is swung over them)
      if (pr.more) { piece(z + .1, pr.more.role, pr.more.rings.map((r) => r.map(at))); if (length) out.at(-1).shaft = 1; }
    }
  }
  // ---- a stool under whoever sits
  if (who.seat) {
    const hip = pose.pelvis, top = hip[1] - 8, a = hip[0] - 13, b = hip[0] + 13;
    piece(6, "wood", [[[a, top, 1], [b, top, 1], [b, top - 2.6, 1], [a, top - 2.6, 1]], [[a + 3, top, 1], [a + 7, top, 1], [a + 1, 0, 1], [a - 2, 0, 1]], [[b - 7, top, 1], [b - 3, top, 1], [b + 2, 0, 1], [b - 1, 0, 1]]]);
  }
  // ---- clothes
  if (who.dress || who.chlamys || who.mantle || who.aegis) {
    const thigh = (L) => limb(L.hip, L.knee, D.thigh, per.thigh * (female ? 1.04 : 1)).ring;
    out.push(...drape(data, pose, { ...who, body: { torso: torsoRing, thighs: who.noLegs ? [] : [thigh(pose.near.leg), thigh(pose.far.leg)] } }, periodName, who.rng ?? Math.random));
  }

  // to the world
  for (const q of out) {
    q.rings = q.rings.map((ring) => ring.map((p) => { const w = pose.place(p); return p[2] ? [w[0], w[1], 1] : w; }));
    q.lines = q.lines.map((l) => ({ ...l, pts: l.pts.map((p) => { const w = pose.place(p); return p[2] ? [w[0], w[1], 1] : w; }) }));
    q.marks = q.marks.map((m) => ({ ...m, at: pose.place(m.at), r: m.r * pose.scale }));
  }
  return out;
}
