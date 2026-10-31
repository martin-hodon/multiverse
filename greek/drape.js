// GREEK PAINTINGS, the clothes (docs/greek.md): cloth derived from the pose, in the pieces' language (figure.js). A garment's
// outline runs down the body and the foremost leg in front and the hindmost behind, in steps along the leg (0 hip, 1 knee,
// 2 ankle), blown back with speed; a fold is the same run at a share u between front and back, so folds follow the legs and
// end on the hem. The period's style: archaic parallel folds over a stacked zigzag hem, classical tension folds from the
// leading knee, the body showing through.
import { pick } from "./rig.js";

const lerp2 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];

// a place on a leg at step s, moved off it by `off` toward the front
function onLeg(L, s, off) {
  const [a, b, t] = s < 1 ? [L.hip, L.knee, s] : [L.knee, L.ankle, s - 1];
  const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, q = lerp2(a, b, Math.min(1, t));
  return [q[0] - dy / l * off, q[1] + dx / l * off];
}

export function drape(data, pose, who, periodName, r) {
  const out = [], st = data.styles[periodName] ?? data.styles.classical, lines = (cls, pts) => ({ cls, pts });
  const piece = (z, role, rings, ls = []) => out.push({ z, owner: who.id ?? 0, role, rings, lines: ls, marks: [], tint: role === "cloth" ? who.tint ?? 0 : role === "cloth2" ? (who.tint ?? 0) + 1 : undefined });
  const legs = [pose.near.leg, pose.far.leg].sort((a, b) => b.ankle[0] - a.ankle[0]), fore = legs[0], hind = legs[1];
  const speed = Math.max(0, fore.ankle[0] - hind.ankle[0] - 30) / 40;
  const up = [Math.sin(pose.lean), Math.cos(pose.lean)], ax = [up[1], -up[0]];
  const trunk = (t, s) => { const c = lerp2(pose.pelvis, pose.chest, t); return [c[0] + ax[0] * s, c[1] + ax[1] * s]; };
  const wide = 8 + 3 * Math.abs(pose.turn);

  if (who.dress) {
    const G = data.dress[who.dress], hem = pick(G.hem, r), wind = pick(st.wind, r) * speed * 7, ease = G.ease;
    const steps = [.25, .6, 1, 1.45, 1.8, 2].filter((s) => s < hem).concat(hem);
    const blown = (s) => wind * (s / 2) ** 1.5;
    const F = steps.map((s) => onLeg(fore, s, 4.6 * (1 - s / 3.2) + ease));
    const B = steps.map((s, k) => { const q = onLeg(hind, s, -(5.6 * (1 - s / 3) + ease)); return [Math.max(q[0] - blown(s), F[k][0] - (G.span ?? Infinity) * (.5 + .25 * s)), q[1] + blown(s) * .12]; });   // (a hem only so wide: past that the rear leg comes out of it, no spike of cloth along it)
    const hemF = F[F.length - 1], hemB = B[B.length - 1];
    const hemPts = [], cuts = Math.max(3, Math.round((hemF[0] - hemB[0]) / 7));
    const hemY = (u) => lerp2(hemF, hemB, u);
    for (let i = 1; i < cuts; i++) {
      const u = i / cuts, q = hemY(u), part = Math.sin(u * Math.PI) * Math.max(0, hemF[0] - hemB[0] - 22) * .16;   // (the hem lifted between parted legs, so a stride shows)
      if (st.hemKind === "zigzag") hemPts.push([q[0], q[1] + part + (i % 2 ? -1.6 : 1.4), 1]);
      else hemPts.push([q[0], q[1] + part + (i % 2 ? -.7 : .7)]);
    }
    const belt = G.belt ? .92 : 1;
    const topF = [trunk(.98, 4), trunk(.75, wide), trunk(.42, wide * belt * .82), trunk(.2, wide)], topB = [trunk(.2, -wide - 1), trunk(.42, -wide * belt * .82), trunk(.75, -wide), trunk(.98, -4)];
    const ring = [...topF, ...F, ...(st.hemKind === "zigzag" ? [[hemF[0], hemF[1], 1]] : []), ...hemPts, ...(st.hemKind === "zigzag" ? [[hemB[0], hemB[1], 1]] : []), ...[...B].reverse(), ...topB];
    const ls = [], n = Math.round(pick(G.folds, r));
    for (let i = 0; i < n; i++) {                                       // the skirt's folds
      let u = (i + .5 + (r() - .5) * .5) / n;
      if (st.foldRule === "tension" && hem > 1.2) u = .34 + u * .66;   // (cloth pulled tight over the leading leg: its folds crowd behind it)
      const lifted = Math.sin(u * Math.PI) * Math.max(0, hemF[0] - hemB[0] - 22) * .16 + 1.2;          // (stopping on the hem, where the stride has lifted it)
      const pts = [lerp2(trunk(.34, wide * .8), trunk(.34, -wide * .8), u), ...steps.map((_, k) => { const q = lerp2(F[k], B[k], u); return k === steps.length - 1 ? [q[0], q[1] + lifted] : q; })];
      const end = pts.length - 1 - (r() < .3 ? 1 : 0);
      ls.push(lines("fold", pts.slice(0, Math.max(2, end + 1))));
    }
    if (st.foldRule === "tension" && hem > 1.2) {                       // catenaries hung from the leading knee toward the rear leg
      const kn = onLeg(fore, 1, 1);
      for (let i = 0; i < 2; i++) { const s = 1.1 + i * .22, a = lerp2(onLeg(fore, s, 2), onLeg(hind, s, 0), .15), b = lerp2(onLeg(fore, s, 0), onLeg(hind, s, 0), .55); ls.push(lines("fine", [kn, lerp2(a, b, .5), b])); }
    }
    if (st.centre) { const a = trunk(.34, 0), m = steps.map((_, k) => lerp2(F[k], B[k], .46)), c = steps.map((_, k) => lerp2(F[k], B[k], .56)); ls.push(lines("hem", [a, ...m]), lines("hem", [a, ...c])); }
    for (let i = 0; i < 3; i++) { const u = (i + 1) / 4; ls.push(lines("fine", [lerp2(trunk(.92, 4), trunk(.92, -4), u), lerp2(trunk(.5, wide), trunk(.5, -wide), u)])); }
    if (G.belt) ls.push(lines("hem", [trunk(.4, wide * .8), trunk(.38, 0), trunk(.4, -wide * .8)]));
    if (G.over) ls.push(lines("hem", [trunk(.56, wide), trunk(.48, 0), trunk(.56, -wide)]));
    piece(45, G.role ?? "cloth", [ring, ...(who.body ? [who.body.torso, ...(hem > 1.2 ? who.body.thighs : [])] : [])], ls);   // (the body under it never shows through its edge)
    if (G.sleeve) for (const [A, z] of [[pose.near.arm, 61], [pose.far.arm, 11]]) {
      const s = lerp2(A.sh, A.el, G.sleeve), d = [A.el[0] - A.sh[0], A.el[1] - A.sh[1]], l = Math.hypot(...d) || 1, n2 = [-d[1] / l, d[0] / l], w = 4.6;
      piece(z, G.role ?? "cloth", [[[A.sh[0] + n2[0] * w - d[0] * .1, A.sh[1] + n2[1] * w - d[1] * .1], [s[0] + n2[0] * w, s[1] + n2[1] * w, 1], [s[0] - n2[0] * w, s[1] - n2[1] * w, 1], [A.sh[0] - n2[0] * w - d[0] * .1, A.sh[1] - n2[1] * w - d[1] * .1]]], [lines("fine", [lerp2(A.sh, s, .1), lerp2(A.sh, s, .9)])]);
    }
  }
  if (who.mantle) {                                                     // a mantle: from the far shoulder across to the near hip, down to the shin
    const hem = 1.4 + r() * .2, steps = [.3, 1, hem], ease = 2.4;
    const F = steps.map((s) => onLeg(fore, s, 5 * (1 - s / 3) + ease)), B = steps.map((s) => onLeg(hind, s, -(6 * (1 - s / 3) + ease)));
    const sf = trunk(.98, 7), sb = trunk(1, -7);
    const ring = [sf, trunk(.72, wide * .8), trunk(.4, wide + 1), ...F, ...[...B].reverse(), trunk(.42, -wide), trunk(.76, -wide), sb];
    const ls = [];
    for (let i = 0; i < 6; i++) { const u = (i + .6) / 6; ls.push(lines("fold", [lerp2(sf, sb, .2 + u * .3), lerp2(trunk(.4, wide), trunk(.2, -wide), u), lerp2(F[1], B[1], u), lerp2(F[2], B[2], u)])); }
    ls.push(lines("hem", [lerp2(F[2], F[1], .08), lerp2(F[2], B[2], .5), lerp2(B[2], B[1], .08)]));
    piece(47, "cloth2", [ring, ...(who.body?.thighs ?? [])], ls);
  }
  if (who.chlamys) {                                                    // a short cloak hung behind the shoulders, lifted with speed
    const fly = 1.5 + speed * 7, n0 = trunk(.98, -2), a = trunk(.04, -wide - 2), m = trunk(.5, -wide - 3);
    const hem = [[a[0] - fly * 1.2, a[1] + fly * .2, 1], [a[0] - fly * .6 + 2.4, a[1] - 3.6, 1], [a[0] + 2.4, a[1] + .6, 1], [a[0] + 5.6, a[1] - 3, 1], [a[0] + 8, a[1] + 1, 1]];
    piece(5, "cloth2", [[n0, [m[0] - fly * .8, m[1]], ...hem, trunk(.5, -2)]], [lines("fold", [n0, [m[0] - fly * .5 + 1, m[1]], [a[0] - fly * .7 + 2, a[1]]]), lines("fold", [n0, [m[0] + 2, m[1]], [a[0] + 3, a[1]]])]);
  }
  if (who.aegis) {                                                      // a scaled cape over the chest, snakes at its edge
    const top = [trunk(.98, 5), trunk(.98, -5)], low = [], k = 7;
    for (let i = 0; i <= k; i++) { const s = lerp2(trunk(.52, wide), trunk(.52, -wide), i / k); low.push(i % 2 ? [s[0], s[1] - 3, 1] : [s[0], s[1] + 1, 1]); }
    const ls = [];
    for (let i = 1; i < 4; i++) for (let j = -2; j <= 2; j++) { const q = lerp2(trunk(.82, j * 3), trunk(.6, j * 3.4), i / 4); ls.push(lines("fine", [[q[0] - 1.1, q[1]], [q[0], q[1] - 1.2], [q[0] + 1.1, q[1]]])); }
    piece(48, "cloth2", [[top[0], ...low, top[1]]], ls);
  }
  return out;
}
