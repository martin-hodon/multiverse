// A SCENE AS PIECES (docs/story.md): a seed and a name from assets/story/canon.json -> stacked polygons in a frame of the caller's units, colours in its palette's slots, not yet
// glass or stone. What each engine then does is its own: glass cuts them to panes and leads, a mosaic lays stones on them. Everything that says WHO and WHAT is data; this only places.
import CANON from "../assets/story/canon.json" with { type: "json" };
import { stream, resolve, one, shuffled, scramble } from "./seed.js";
import { rolesOf } from "./roles.js";
import { buildFigure, partsOf } from "../medieval/figure.js";

export { CANON };
const WORN = ["robe", "mantle", "hem", "hose", "shoes", "skin", "hair", "beard", "veil", "crown", "diadem", "mitre", "tiara", "hood", "cap", "hat", "turban", "helmet", "wreath", "halo", "wings", "attr", "attr2", "belt", "apron", "mail", "loin", "sleeve"];
const ALT = { cobalt: "ruby", ruby: "cobalt", gold: "ruby", emerald: "ruby", white: "ruby", sky: "ruby", purple: "emerald", navy: "ruby", amber: "emerald", brown: "emerald", rose: "emerald", olive: "ruby", grey: "ruby", flesh: "ruby" };
// (the same names are all an engine knows: which colours a scene's in, and what's its ground: nothing stands in the colour it stands on)
const dressed = (F, dye, ground) => {
  const O = { skin: "flesh", hair: "amber", shoes: "navy", hose: "brown", attr: "gold", attr2: "white", ...F };
  for (const k of ["robe", "mantle"]) if (O[k] === undefined) O[k] = k === "robe" ? "white" : "ruby";
  if (O.robe && O.robe === O.mantle && O.cut !== "cloak") O.mantle = ALT[O.robe];                   // (a robe and a mantle of one colour are one lump, in lead or in stone)
  for (const k of ["robe", "mantle", "veil", "wings"]) if (O[k] && O[k] === ground) O[k] = ALT[O[k]];
  if (O.robe && O.robe === O.mantle && O.cut !== "cloak") O.robe = ALT[O.mantle];
  if (O.halo && O.halo === ground) O.halo = O.halo === "gold" ? "amber" : "gold";
  for (const k of WORN) if (typeof O[k] === "string") O[k] = dye(O[k]);
  O.dye = dye;
  return O;
};
// the clothes and attributes of a person of the canon, the seed's choices made: `wear` over the cast's own
export function personOf(name, r, wear) {
  const C = CANON.cast[name];
  if (!C) throw new Error(`no person "${name}"`);
  return { ...resolve(C, r), ...(wear ? resolve(wear, r) : null) };
}
const boxOf = (pieces) => { let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity; for (const p of pieces) if (!p.span && !p.loose) for (const q of p.pts) { if (q[0] < a) a = q[0]; if (q[1] < b) b = q[1]; if (q[0] > c) c = q[0]; if (q[1] > d) d = q[1]; } return [a, b, c, d]; };
const moved = (p, f) => ({ ...p, pts: p.pts.map(f), paint: p.paint?.map((l) => ({ ...l, pts: l.pts.map(f) })) });
const scaled = (p, s, dx, dy, flip) => { const q = moved(p, ([x, y]) => [dx + flip * x * s, dy + y * s]); if (q.paint) for (const l of q.paint) if (l.w !== undefined) l.w *= s; return q; };

function thingOf(role, r, tint) {
  const name = role.beast ? (role.gait && CANON.things[`${role.beast}-${role.gait}`] ? `${role.beast}-${role.gait}` : role.beast) : role.thing, T = CANON.things[name];
  if (!T) throw new Error(`no thing "${name}"`);
  const parts = partsOf(T.parts, { tint });
  if (T.stars) for (const p of parts) p.stars = true;
  return { parts, anchors: T.anchors ?? {}, z: T.z ?? 0 };
}

// ONE PERSON, as a saint stands: his pose, his attributes, what's under his feet or beside him. -> pieces, feet at 0, x 0 at his middle
export function personPieces(name, { seed: seed0 = 1, dye, ground, wear, label = "p", coarse = false, r: r0 } = {}) {
  const seed = scramble(seed0), r = r0 ?? stream(seed, "person", name), P = personOf(name, r, wear), tint = dye, out = [];
  const F = dressed({ ...P, id: label, coarse }, dye, ground);
  if (P.beside) out.push(...partsOf(CANON.things[P.beside].parts, { x: 24, y: 0, s: .5, tint }).map((p) => ({ ...p, loose: 1 })));
  const fig = buildFigure(F, stream(seed, "body", name));
  if (P.underfoot) out.push(...partsOf(CANON.things[P.underfoot].parts, { x: 0, y: -6, s: .55, tint }).map((p) => ({ ...p, loose: 1 })));
  out.push(...fig);
  out.anchors = fig.anchors;
  return out;
}

// ONE SCENE, to fit `frame` { x0, x1, y0, y1 }: { pieces, fit: scale, label }. `dye` a tint's slot; `ground` the tint it's on; `coarse` a floor's px per unit, under which bodies are simplified. Keys of a piece: pts, fill, role, paint, whole, label
export function composeScene(name, { seed: seed0 = 1, dye, ground, frame, pxPerUnit = 2, tag = "", float = 0 } = {}) {
  const S = CANON.scenes[name], seed = scramble(seed0);
  if (!S) throw new Error(`no scene "${name}"`);
  const r = stream(seed, "scene", name), flip = S.flip && r() < .5 ? -1 : 1, seen = rolesOf(S, r, { beatRng: () => stream(seed, "beat", name), beatsData: CANON.beats }), roles = {}, placedAt = {};
  for (const [k, q] of Object.entries(seen)) { if (q.p !== undefined && r() >= q.p) continue; const v = resolve(Object.fromEntries(Object.entries(q).filter(([n]) => n !== "p")), r); if (v.size === 0 || (!v.cast && !v.thing && !v.beast)) continue; roles[k] = v; }
  const tint = dye, built = [];
  for (const [k, Q] of Object.entries(roles)) {                         // (each role in its own place, feet at 0 before it's moved. The order's the data's: later over earlier)
    if (Q.cast) {
      const rp = stream(seed, "who", name, k), P = personOf(Q.cast, rp, Q.wear);
      const pose = Q.pose ?? P.pose ?? "stand", size = Q.size ?? 1, face = Q.face ?? 1;
      const F = dressed({ ...P, pose, ...(Q.bust !== undefined ? { bust: Q.bust } : null), ...(Q.turn !== undefined ? { turn: Q.turn } : P.turn !== undefined ? { turn: P.turn } : null), ...(Q.gripR !== undefined ? { gripR: Q.gripR } : null), id: `${tag}${k}` }, dye, ground);
      built.push({ k, Q, F, size, face, P });
    } else {
      const T = thingOf(Q, r, tint), size = Q.size ?? 1, face = Q.flipIt ? -1 : Q.face ?? 1;
      built.push({ k, Q, T, size, face });
    }
  }
  // WHERE: x and y in the scene's units; what rides on something takes that thing's seat
  const where = {};
  for (const b of built) {
    const { Q } = b;
    if (!Q.on || !where[Q.on]) { where[b.k] = { x: Q.at ?? 0, y: Q.y ?? 0, s: b.size, face: b.face }; continue; }
    const H = where[Q.on], host = built.find((q) => q.k === Q.on), onBeast = !!host.T;
    if (onBeast) {
      const sa = host.T.anchors.seat ?? [0, 60], rideAt = (CANON.poses[b.F.pose]?.drop ?? 30) ? 28 : 40, s = Q.size ?? H.s;
      b.size = s; where[b.k] = { x: H.x + H.face * sa[0] * H.s, y: H.y + sa[1] * H.s - rideAt * s, s, face: b.face };
    } else {
      const pose = CANON.poses[host.F.pose] ?? {}, drop = pose.drop ?? 0;
      const lap = pose.lap ?? [0, 50 - drop], at = Q.onAt === "shoulder" ? [-10, 84 - drop] : lap, s = b.size * H.s;
      b.size = s; where[b.k] = { x: H.x + H.face * at[0] * H.s, y: H.y + at[1] * H.s + (Q.onDy ?? 0) * H.s, s, face: b.face };
    }
  }
  const EST = { head: [0, 97], shoulderR: [9, 85], shoulderL: [-9, 85], chest: [0, 72] };
  for (const b of built) if (b.Q.reach && b.F) {                        // (a hand on something: where that is, in his own units)
    const w = where[b.k], reach = {};
    for (const [s, [who, at]] of Object.entries(b.Q.reach)) {
      const H = where[who], host = built.find((q) => q.k === who); if (!H) continue;
      const a = host.T ? host.T.anchors[at] ?? [0, 50] : EST[at] ?? [0, 80], X = H.x + H.face * a[0] * H.s, Y = H.y + a[1] * H.s;
      reach[s] = [(X - w.x) / (w.s * w.face), (Y - w.y) / w.s];
    }
    b.F = { ...b.F, reach };
  }
  // (a first look, for how big it'll all be: the frame's scale decides how fine the bodies need be)
  const rb = (k) => stream(seed, "body", name, k);
  const assemble = (coarse) => {
    const out = [];
    for (const b of built) {
      const w = where[b.k], fx = flip * w.x, fface = flip * w.face;
      const own = b.T ? b.T.parts.map((p) => p.span ? p : { ...scaled(p, w.s, fx, w.y, fface) }) : buildFigure(coarse ? { ...b.F, coarse: true } : b.F, rb(b.k)).map((p) => scaled(p, w.s, fx, w.y, fface));
      own.forEach((p, n) => { p.label ??= `${tag}${b.k}.${n}`; });
      if (b.T && b.Q.spin) for (const p of own) { const a = b.Q.spin * Math.PI / 180, cs = Math.cos(a), sn = Math.sin(a), R = ([x, y]) => { const u = x - fx, v = y - w.y; return [fx + u * cs - v * sn * fface, w.y + u * sn * fface + v * cs]; }; const q = moved(p, R); p.pts = q.pts; p.paint = q.paint; }
      out.push(...own);
    }
    return out;
  };
  const rough = assemble(true), box = boxOf(rough), bw = Math.max(1, box[2] - box[0]), Fw = frame.x1 - frame.x0, Fh = frame.y1 - frame.y0;
  const fit = Math.min(Fw / bw, Fh / (box[3] - box[1] || 1)), cx = (frame.x0 + frame.x1) / 2 - fit * (box[0] + box[2]) / 2, free = float * Math.max(0, Fh - (box[3] - box[1]) * fit), base = frame.y0 + free - box[1] * fit;   // (`float`: a floor's picture sits up off its frame's foot, on a thin ground of its own, not down on the sill as a window's does)
  const pieces = (fit * 100 * pxPerUnit < 90 ? rough : assemble(false)).map((p) => {
    if (p.span) {                                                       // (what runs out to the frame: its x in frame widths, its y from the frame's foot or head, in the scale of the rest)
      const W = (frame.x1 - frame.x0) * .5, X0 = (frame.x0 + frame.x1) / 2, Y0 = p.span === "top" ? frame.y1 : frame.y0 + free;
      const q = moved(p, ([x, y]) => [X0 + x * W, Y0 + (p.span === "top" ? (y > 0 ? y / 16 * Fh * .5 : y * fit) : (y < 0 ? (float ? (p.role === "water" ? y / 40 * free : y * fit * .3) : y / 40 * Fh) : y * fit))]); if (q.paint) for (const l of q.paint) { if (l.w !== undefined) l.w *= fit; }
      return q;
    }
    if (p.stars) return moved(p, ([x, y]) => [x * Fw * .5 + (frame.x0 + frame.x1) / 2, (y + 1) * Fh * .5 + frame.y0]);
    const q = moved(p, ([x, y]) => [cx + fit * x, base + fit * y]); if (q.paint) for (const l of q.paint) { if (l.w !== undefined) l.w *= fit; }
    return q;
  });
  return { pieces, fit, label: S.label, flip };
}

// A TINT'S SLOT: an engine's dye over the canon's names
export const dyeOf = (map) => (name) => { if (typeof name === "number") return name; const v = map[name]; if (v === undefined) throw new Error(`no colour for "${name}"`); return v; };
export { one, shuffled };
