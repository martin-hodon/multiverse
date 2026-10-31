// GREEK PAINTINGS, what can be wrong with a group (docs/greek.md): pure reads of its solved actors. The solver redraws to have fewer of them.
import { anchor, shieldCentre } from "./rig.js";

// how many things in a group a painter would not let stand: a shield over a head (its bearer's, or anyone's drawn before them) or over
// someone down; a forearm, a held cup or one's own shaft across a face; a shaft from an arm lost behind its body; two shafts lying as one
export function faults(data, actors, why = null) {
  const men = Object.values(actors).filter((A) => A.pose);
  const off = (h, a, d) => Math.abs((h[0] - a[0]) * d[1] - (h[1] - a[1]) * d[0]) / (Math.hypot(d[0], d[1]) || 1);   // (off the line through a along d)
  const across = (A, q, reach) => {
    const a = A.pose.place(A.pose.near.arm.el), b = A.pose.place(A.pose.near.arm.hand), dx = b[0] - a[0], dy = b[1] - a[1];
    const t = Math.max(0, Math.min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / (dx * dx + dy * dy || 1)));
    return Math.hypot(a[0] + dx * t - q[0], a[1] + dy * t - q[1]) < reach;
  };
  const shafts = [];
  let n = 0;
  const bad = (what, A) => { n++; why?.push(`${what}:${A.pose.action}`); };
  for (const A of men) {
    const h = anchor(A.pose, "head"), th = anchor(A.pose, "throat");
    if (across(A, [h[0] + A.pose.dir * 4, h[1] - 1], 8) || across(A, [(h[0] + th[0]) / 2, (h[1] + th[1]) / 2], 7)) bad("arm", A);
    for (const B of men) if (B !== A) { const g = anchor(B.pose, "head"); if (across(A, [g[0] + B.pose.dir * 4, g[1] - 1], 7)) bad("arm", A); }   // (nor another's: that's a man with an arm for a face)
    const fist = A.pose.place(A.pose.near.arm.hand);
    if (Math.hypot(fist[0] - h[0], fist[1] - h[1]) < 10) bad("fist", A);   // (a near fist on his own head or helmet)
    for (const [side, name] of Object.entries(A.who.props ?? {})) {
      if (!name) continue;
      const q = A.pose.arms[side].hand, hand = A.pose.place(q), aim = A.who.aims?.[side], pr = data.parts.props[name];
      if (pr?.bulk) for (const B of men) { const g = anchor(B.pose, "head"); if (Math.min(Math.hypot(hand[0] - g[0], hand[1] + pr.bulk - g[1]), Math.hypot(hand[0] - g[0], hand[1] - g[1])) < pr.bulk + 9) bad("cup", A); }   // (a big thing held up: where a head should be, his or anyone's)
      if (pr?.short && data.actions[A.pose.action].attack && q[1] < A.pose.chest[1] - 8 && !aim) bad("idle", A);   // (a fight, and a blade down at his hip)
      if (pr?.short) {                                                 // (a blade or club, along the forearm if not aimed: not over a face, nor lying on his own shield like a device)
        const el = A.pose.place(A.pose.arms[side].el), d = aim ? [aim[0] - hand[0], aim[1] - hand[1]] : [hand[0] - el[0], hand[1] - el[1]], L = Math.hypot(d[0], d[1]) || 1;
        const on = (c, r) => { const t = Math.max(0, Math.min(data.canon.closeReach * .8, ((c[0] - hand[0]) * d[0] + (c[1] - hand[1]) * d[1]) / L)); return Math.hypot(hand[0] + d[0] / L * t - c[0], hand[1] + d[1] / L * t - c[1]) < r; };
        for (const B of men) if (B !== A && on(anchor(B.pose, "head"), 8)) bad("blade", A);
        if (A.who.shield && on(A.pose.place(shieldCentre(A.pose)), data.canon.shieldR * .7)) bad("blade", A);
      }
      if (!data.parts.props[name]?.shaft) {
        if (Math.hypot(hand[0] - h[0], hand[1] - h[1]) < 15 && hand[1] < h[1] + 6) bad("cup", A);   // (raised over it, a blow: not over the face)
        if (!data.actions[A.pose.action].blow) for (const B of men) if (B !== A && Math.hypot(hand[0] - anchor(B.pose, "head")[0], hand[1] - anchor(B.pose, "head")[1]) < 13) bad("cup", A);   // (nor in another's, but for a `blow`, which is meant to land there)
        continue;
      }
      if (A.pose.nearSide !== side && Math.abs(q[0] - A.pose.chest[0]) < 12 && q[1] < A.pose.chest[1]) bad("lost", A);
      if (A.pose.nearSide !== side && A.who.shield) { const c = A.pose.place(shieldCentre(A.pose)); if (Math.hypot(hand[0] - c[0], hand[1] - c[1]) < 20) bad("lost", A); }   // (its hand behind his own shield: a shaft out of nowhere)
      if (!aim) continue;
      const d = [aim[0] - hand[0], aim[1] - hand[1]];
      if (off(h, hand, d) < (Math.abs(d[1]) > 3 * Math.abs(d[0]) ? 7 : 11)) bad("shaft", A);   // (a spear stood upright before the face only if it's on it)
      const L = Math.hypot(d[0], d[1]) || 1, reach = data.parts.props[name].shaft;
      for (const B of men) if (B !== A && !A.R.aim) { const g = anchor(B.pose, "head"), t = (g[0] - hand[0]) * d[0] / L + (g[1] - hand[1]) * d[1] / L; if (t > 0 && t < reach && off(g, hand, d) < 11) bad("tip", A); }   // (at the body, not through another's head; a shaft carried at an angle is at no one)
      for (const B of men) if (B !== A && !A.R.aim && B.who.shield) { const c = B.pose.place(shieldCentre(B.pose)), t = (c[0] - hand[0]) * d[0] / L + (c[1] - hand[1]) * d[1] / L; if (t > 0 && L > t + data.canon.shieldR * .85 && off(c, hand, d) < data.canon.shieldR * .85) bad("through", A); }   // (a point stops on a shield: none lands on the man behind it)
      if (A.who.shield && A.pose.nearSide !== side) { const c = A.pose.place(shieldCentre(A.pose)), t = (c[0] - hand[0]) * d[0] / L + (c[1] - hand[1]) * d[1] / L; if (t > 0 && off(c, hand, d) < data.canon.shieldR * .8) bad("own", A); }   // (its point behind his own shield: only the butt to see, aimed the wrong way)
      shafts.push([hand, d, A, Math.min(L, reach * .85) / L]);
    }
  }
  shafts.forEach(([a, d, A], i) => { for (const [b, e] of shafts.slice(0, i)) if (Math.abs(d[0] * e[1] - d[1] * e[0]) / ((Math.hypot(...d) * Math.hypot(...e)) || 1) < .14 && off(b, a, d) < 14) bad("twin", A); });
  shafts.forEach(([a, d, A, k], i) => { for (const [b, e, , u] of shafts.slice(0, i)) if (Math.hypot(a[0] + d[0] * k - b[0] - e[0] * u, a[1] + d[1] * k - b[1] - e[1] * u) < 22) bad("meet", A); });   // (two points on one spot in the air)
  const stance = (A) => [A.pose.place(A.pose.near.leg.ankle)[0], A.pose.place(A.pose.far.leg.ankle)[0]].sort((a, b) => a - b);
  men.forEach((A, i) => { for (const B of men.slice(0, i)) if (!A.down && !B.down && !A.R.on && !B.R.on) {   // (one's feet planted inside another's: whose leg is whose)
    const [a0, a1] = stance(A), [b0, b1] = stance(B);
    if (Math.min(a1, b1) - Math.max(a0, b0) > .2 * Math.min(a1 - a0, b1 - b0)) bad("tangle", A);
  } });
  men.forEach((A, i) => {
    if (!A.who.shield) return;
    const c = A.pose.place(shieldCentre(A.pose)), under = (q) => Math.hypot(q[0] - c[0], q[1] - c[1]) < data.canon.shieldR * 1.25;
    for (const B of men.slice(0, i + 1)) {
      if (B === A && A.pose.nearSide !== "L") continue;
      if (under(anchor(B.pose, "head")) || (B !== A && B.down && under(anchor(B.pose, "chest")))) bad("shield", A);
    }
    for (const B of men) if (B !== A && !B.R.on && [anchor(B.pose, "throat"), anchor(B.pose, "chest"), anchor(B.pose, "belly")].some((q) => Math.hypot(q[0] - c[0], q[1] - c[1]) < data.canon.shieldR * .95)) bad("hidden", A);   // (on another's trunk or under his chin, a bib: whose is it?)
  });
  const inside = (q, ring) => { let c = false; for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) if ((ring[i][1] > q[1]) !== (ring[j][1] > q[1]) && q[0] < ring[j][0] + (ring[i][0] - ring[j][0]) * (q[1] - ring[j][1]) / (ring[i][1] - ring[j][1])) c = !c; return c; };
  for (const C of Object.values(actors)) {                             // (under a horse's near body or legs, not his own: lost in it, a hoof on his head)
    if (!C.beast) continue;
    const rings = C.beast.pieces.filter((p) => p.body).flatMap((p) => p.rings);
    const maw = C.beast.anchors.mouth;
    if (maw) for (const A of men) if (A.R.on !== C.id) { const h = anchor(A.pose, "head"), m = C.beast.place(maw); if (Math.hypot(h[0] - m[0], h[1] - m[1]) < data.canon.crowd * .8) bad("maw", A); }   // (his head in its head: neither reads)
    for (const A of men) if (A.R.on !== C.id && [anchor(A.pose, "head"), anchor(A.pose, "chest"), anchor(A.pose, "belly"), ...(A.who.shield ? [0, 1, 2, 3, 4, 5, 6, 7].map((k) => { const c = A.pose.place(shieldCentre(A.pose)); return [c[0] + Math.cos(k * .785) * data.canon.shieldR * .66, c[1] + Math.sin(k * .785) * data.canon.shieldR * .66]; }) : [])].some((q) => rings.some((r) => inside(q, r)))) bad("buried", A);
  }
  for (const A of men) if (A.down) for (const B of men) if (!B.down && !B.R.on && [anchor(A.pose, "chest"), anchor(A.pose, "belly"), A.pose.place(A.pose.pelvis)].some((q) => { const [f, r] = [B.pose.place(B.pose.near.leg.ankle)[0], B.pose.place(B.pose.far.leg.ankle)[0]]; return q[0] > Math.min(f, r) - 8 && q[0] < Math.max(f, r) + 8; })) bad("under", A);   // (one fallen: not lying through another's legs)
  men.forEach((A, i) => { for (const B of men.slice(0, i)) if (A.who.shield && B.who.shield) { const a = A.pose.place(shieldCentre(A.pose)), b = B.pose.place(shieldCentre(B.pose)); if (Math.hypot(a[0] - b[0], a[1] - b[1]) < data.canon.shieldR * 2.1) bad("shields", A); } });   // (one on another: a stack of plates and no one behind them)
  const crowd = data.canon.crowd, free = men.filter((A) => !A.R.on && !A.down);
  for (const A of free) for (const B of free) {                        // (one body on another's chest: in a flat colour they read as one)
    if (A === B) continue;
    const c = anchor(B.pose, "chest"), d = (q) => Math.hypot(q[0] - c[0], q[1] - c[1]);
    if (A.id < B.id && d(anchor(A.pose, "chest")) < crowd) bad("crowd", A);
    if (A.id < B.id && Math.abs(anchor(A.pose, "belly")[0] - anchor(B.pose, "belly")[0]) < crowd * .8) bad("fused", A);   // (one waist on another: two trunks, one mass)
    if (d(anchor(A.pose, "head")) < crowd * .85) bad("crowd", A);
    if (A.id < B.id) { const a = anchor(A.pose, "head"), b = anchor(B.pose, "head"); if (Math.hypot(a[0] - b[0], a[1] - b[1]) < crowd) bad("crowd", A); }   // (two heads together: whose is whose)
  }
  return n;
}
