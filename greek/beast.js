// GREEK PAINTINGS, the other body plans (docs/greek.md): a four-legged beast from its outline and legs by a gait, its foot in the data, facing +x like a
// man (rig.js), its near legs over its body and its far legs under; a wheeled car. Whoever rides shares the beast's band of
// depth, so a rider's far leg goes behind the horse and the near one over it. All in the data's shapes and gaits.
import { twoBone, pick } from "./rig.js";

const DEG = Math.PI / 180;

// parts: { z, role, roleIf: { tag: role }, rings, lines, if: a tag, unless: a tag }: all a thing without legs is, and what a beast has round its body and legs
export function solveBeast(data, kind, { dir = 1, x = 0, r = Math.random, gait, tags = [], size } = {}) {
  const B = data.parts.beasts[kind], out = [], G = B.gaits?.[gait ?? Object.keys(B.gaits ?? { a: 0 })[0]], has = (t) => tags.includes(t);
  const k = size ?? B.size ?? 1, place = (q) => { const w = [x + dir * q[0] * k, q[1] * k]; return q[2] ? [w[0], w[1], 1] : w; };   // (`size`, to a man: a Greek horse is small; a yoked team keeps its car's)
  const piece = (z, role, rings, lines = [], marks = []) => out.push({ z, owner: kind, role, rings: rings.map((q) => q.map(place)), lines: lines.map((l) => ({ ...l, pts: l.pts.map(place) })), marks: marks.map((m) => ({ ...m, at: place(m.at), r: m.r * k })) });
  const tinted = (p) => Object.entries(p.roleIf ?? {}).find(([t]) => has(t))?.[1] ?? p.role ?? "horse";
  const parts = (f) => { for (const p of B.parts ?? []) if ((!p.if || has(p.if)) && !(p.unless && has(p.unless))) piece(p.z, tinted(p), p.rings.map((q) => q.map(f)), (p.lines ?? []).map((l) => ({ ...l, pts: l.pts.map(f) }))); };
  const solved = (f) => ({ pieces: out, anchors: Object.fromEntries(Object.entries(B.anchors).map(([k, q]) => [k, f(q)])), dir, x, place });
  if (!G) { parts((q) => q); return solved((q) => q); }
  const pitch = pick(G.pitch, r, 0) * DEG, [px, py] = B.pivot, cs = Math.cos(pitch), sn = Math.sin(pitch), lift = pick(G.lift, r, 0);
  const turn = ([a, b, k]) => { const u = a - px, v = b - py, q = [px + u * cs - v * sn, py + u * sn + v * cs + lift]; return k ? [q[0], q[1], 1] : q; };
  const legs = { nearFore: B.fore, farFore: B.fore, ...(B.hind ? { nearHind: B.hind, farHind: B.hind } : null) };   // (no hind legs: what ends in a fish's tail)
  const leg = {}, reach = {};
  for (const name of Object.keys(legs)) reach[name] = pick(G.legs[name][0], r);
  for (const [name, L] of Object.entries(legs)) {
    const fore = name.endsWith("Fore"), far = name.startsWith("far"), other = reach[(fore ? "nearFore" : "nearHind")];
    const root = turn([L.root[0] + (far ? (reach[name] < other ? -3 : 3) : 0), L.root[1], 0]);   // (a far leg leaves the body on the side its foot lands, so a pair doesn't cross)
    const q = G.legs[name], foot = [L.root[0] + reach[name], pick(q[1], r)];
    const [la, lb, lc] = L.bones;                                     // upper, lower, the cannon to the hoof
    const raised = pick(q[2], r, 0) * DEG;                            // (the cannon's swing from straight down)
    const end = [foot[0] - Math.sin(raised) * lc, foot[1] + Math.cos(raised) * lc];
    const s = twoBone(root, end, la, lb, fore ? 1 : -1);
    // one outline down the front and up the back: the forearm tapers to a knee, a thin cannon, a fetlock and its foot
    const l = Math.hypot(foot[0] - end[0], foot[1] - end[1]) || 1, u = [(foot[0] - end[0]) / l, (foot[1] - end[1]) / l], n = [-u[1], u[0]];
    const at = (q, a, b = 0) => [q[0] + n[0] * a + u[0] * b, q[1] + n[1] * a + u[1] * b], coronet = at(foot, 0, -3.4), fet = at(coronet, 0, -3.2);
    const side = (a, b) => { const d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1; return [-(b[1] - a[1]) / d, (b[0] - a[0]) / d]; };
    const n1 = side(root, s.mid), n2 = side(s.mid, s.end), sg = fore ? 1 : -1, off = (q, m, k) => [q[0] + m[0] * k * sg, q[1] + m[1] * k * sg], mid = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
    const stout = has("noHead") || has("stout") ? B.stout ?? 1 : 1, [w0, w1, w2, w3] = L.w.map((v) => v * stout);   // (a man's trunk on it wants more under him than a horse has)
    const front = [off(root, n1, w0), off(mid(root, s.mid, .6), n1, w1 * 1.35), off(s.mid, n1, w1), off(mid(s.mid, s.end, .25), n2, w2 * 1.1), off(s.end, n2, w2), at(fet, sg * w3 * 1.25), at(coronet, sg * w3)];
    const back = [off(s.end, n2, -w2), off(mid(s.mid, s.end, .25), n2, -w2 * 1.1), off(s.mid, n1, -w1), off(mid(root, s.mid, .6), n1, -w1 * 1.35), off(root, n1, -w0)];
    const toes = B.foot.map(([s, a, b, k]) => { const p = at(foot, s * w3 + a, b); return k ? [...p, 1] : p; });   // (a hind leg's outline runs the other way round, its toes too, or it twists at the ankle)
    leg[name] = [[...front, ...(fore ? toes : toes.reverse()), at(coronet, -sg * w3), at(fet, -sg * w3 * 1.35), ...back]];
  }
  const role = tinted(B);
  if (!has("fewLegs")) { piece(16, role + "Far", leg.farHind ?? []); piece(17, role + "Far", leg.farFore); }
  const noHead = has("noHead"), body = (noHead ? B.bodyNoHead : B.body).map(turn);
  const lines = (noHead ? [] : B.lines ?? []).map((l) => ({ cls: "detail", pts: l.map(turn) })).concat((B.muscle ?? []).map((l) => ({ cls: "fine", pts: l.map(turn) })));
  piece(25, role, [body, ...(leg.nearHind ?? []), ...leg.nearFore], lines, noHead ? [] : (B.marks ?? []).map(([a, b, m]) => ({ cls: "detail", at: turn([a, b, 0]), r: m })));
  out.at(-1).body = 1;
  parts(turn);
  return solved(turn);
}
