// GREEK PAINTINGS, scenes (docs/greek.md): a few bodies placed and aimed at each other. Who and what they do are independent
// picks (assets/greek/canon.json: cast, scenes); a seed also mirrors the whole, so a fight reads either way round and the
// shields change sides of the bodies, as flipping a body must not (rig.js). Nothing here knows a scene by name.
import { solvePose, stream, pick, anchor, shieldCentre } from "./rig.js";
import { faults } from "./faults.js";
import { buildFigure } from "./figure.js";
import { solveBeast } from "./beast.js";

// a cast's or scene's value: { p, v } a chance of v, { of: [...] } one of them, plain as it is; down through objects
export function resolve(v, r) {
  if (Array.isArray(v) || v === null || typeof v !== "object") return v;
  if ("of" in v) return resolve(v.of[Math.floor(r() * v.of.length)], r);
  if ("p" in v) return r() < v.p ? resolve("v" in v ? v.v : 1, r) : undefined;
  return Object.fromEntries(Object.entries(v).map(([k, q]) => [k, resolve(q, r)]));
}

// a group at the origin, { pieces, min, max, height, actors } in world units, the ground at 0: of a few tries, further apart and then another draw, the first with nothing wrong, or the one with least
export function solveGroup(data, name, opts = {}) {
  if (opts.key) return composeGroup(data, name, { ...opts, ...opts.key });   // (that same draw again, only its frame told it now)
  let best = null, least = Infinity, off = Infinity;
  const hold = opts.sparse && !data.scenes[name]?.wide;                // (in a panel of its own a pair keeps the span it was solved for: another draw, never further apart; of those as good, the nearest that span)
  for (let a = 0; a < 15 && (least || (opts.want && a < 6)); a++) {
    const key = { seed: (opts.seed ?? 1) + (hold ? a : Math.floor(a / 3)) * 1009, spread: hold ? 1 : [1, 1.22, 1.5][a % 3], tight: opts.tight }, G = composeGroup(data, name, { ...opts, ...key }), n = faults(data, G.actors), d = opts.want ? Math.abs(G.max - G.min - opts.want) : 0;
    if (n < least || (n === least && d < off)) { best = G; best.key = key; least = n; off = d; }
  }
  best.faults = least;
  return best;
}
const lowest = (pieces) => { let low = Infinity; for (const p of pieces) if (!p.shaft) for (const r of p.rings) for (const q of r) if (q[1] < low) low = q[1]; return low; };   // (a spear's butt lifts nobody)
const handAt = (P, side) => P.place((P.nearSide === side ? P.near : P.far).arm.hand);
const lift = (pose, by) => { const place = pose.place; pose.place = (q) => { const w = place(q); return [w[0], w[1] + by]; }; pose.y += by; };   // (drawn higher than solved: so is everything asked of the pose afterwards)
function composeGroup(data, name, { seed = 1, period = "classical", flip, tight = 1, spread = 1, sparse, top, side, not } = {}) {
  const S = data.scenes[name];
  if (!S) throw new Error(`no scene "${name}"`);
  tight = (S.rigid || (S.wide && !sparse) ? 1 : tight) * spread;       // (bodies too wide to tangle closer, but in a panel of their own, as a metope's do; a team yoked to its car never)
  const rl = stream(seed, "layout", name);
  const mirror = (flip ?? rl() < .5) ? -1 : 1, per = data.canon.periods[period];
  let roles = S.roles, beats = S.beats;
  if (S.variants) {                                                    // (what happens, a pick of the whole: each role's pick follows from it)
    const free = S.variants.filter((v) => !Object.entries(roles).some(([k, q]) => { const c = (v[k]?.cast ?? q.cast); return c?.of ? c.of.every((n) => not?.has(n)) : not?.has(c); })), pool = free.length ? free : S.variants;   // (whoever has come already, `not`, isn't drawn again)
    const v = pool[Math.floor(rl() * pool.length)];
    roles = Object.fromEntries(Object.entries(roles).map(([k, q]) => [k, { ...q, ...v[k] }]));
    beats = v.beats ? { ...beats, ...v.beats } : beats;
  }
  if (beats && !sparse) {                                              // (whoever else is there, each where the scene has room; drawn first, and on a stream of their own so the rest keep their poses)
    const rb = stream(seed, "beat", name), pool = [...beats.of], free = { ...S.slots }, extra = {};
    for (let n = Math.round(pick(beats.n, rb)), i = 0; i < n && pool.length; i++) {
      const B = data.beats[pool.splice(Math.floor(rb() * pool.length), 1)[0]], slot = B.slots.find((q) => free[q]);
      if (slot) { extra[`beat${i}`] = { face: free[slot].face, ...B, at: free[slot].at }; delete free[slot]; }
    }
    roles = { ...extra, ...roles };
  }
  if (S.chain) {                                                       // a line of bodies, all alike in kind and each its own
    const n = Math.round(pick(S.chain.n, rl)), step = pick(S.chain.step, rl);
    roles = {};
    for (let i = 0; i < n; i++) {
      const at = -i * step + (rl() - .5) * 6;
      if (S.chain.rider) {                                             // (a chain of riders: each a beast and whoever is on it)
        roles[`h${i}`] = { beast: S.chain.beast, gait: S.chain.gait, face: S.chain.face, at };
        roles[`c${i}`] = { cast: S.chain.cast, action: S.chain.action, face: S.chain.face, on: `h${i}` };
      } else roles[`c${i}`] = { ...S.chain, at, ...(i ? null : S.chain.lead) };   // (the one in front may do what the rest don't: look back at them)
    }
  }
  const actors = {}, order = Object.keys(roles);
  const spot = (A, where) => {                                         // a named place on anyone, in the world
    if (A.beast) return A.beast.place(A.beast.anchors[where] ?? A.beast.anchors.seat);
    return anchor(A.pose, where);
  };
  const solved = [], worn = new Set();
  const armed = (who) => ["R", "L"].find((q) => { const pr = who.props?.[q] && data.parts.props[who.props[q]]; return pr && !pr.at && !pr.staff; });
  const foeOf = (A) => {                                               // (whoever he is turned to and isn't one of his own: what a blow is at unless the scene says)
    let best = null, least = Infinity;
    for (const id of solved) {
      const B = actors[id];
      if (!B.pose || B.id === A.id || B.cast === A.cast || (B.pose.x - A.pose.x) * A.pose.dir <= 0 || !(armed(B.who) || B.down || data.actions[B.pose.action].hurt)) continue;   // (a raised blade isn't laid on the unarmed: a scene links it if it means that)
      const d = Math.abs(B.pose.x - A.pose.x);
      if (d < least) { best = B; least = d; }
    }
    return best;
  };
  for (const id of order) {
    const R = roles[id];
    if (R.p !== undefined && rl() >= R.p) continue;
    if ((R.extra && sparse) || (R.on && !actors[R.on])) continue;     // (more bodies than a panel of its own holds; a rider without a mount)
    const ra = stream(seed, "actor", id, name);
    if (R.beast) {
      const dirB = resolve(R.face, ra) * mirror, xB = pick(R.at, ra) * mirror * tight, gait = resolve(R.gait, ra), B = solveBeast(data, resolve(R.beast, ra), { dir: dirB, x: xB, r: ra, gait, tags: R.tags, size: R.size });
      actors[id] = { id, beast: B, R, gait };
      solved.push(id);
      continue;
    }
    const left = R.cast?.of?.filter((c) => !not?.has(c)), castName = resolve(left?.length ? { of: left } : R.cast, ra), action = R.actionFor?.[castName] ?? resolve(R.action, ra);
    const who = { ...resolve(data.cast[castName], stream(seed, "gear", id, name)), id, rng: stream(seed, "cloth", id, name), seat: R.seat, top: (top ?? data.canon.top) / (S.scale ?? 1), side };
    const tints = data.cast[castName]?.tint?.of;
    if (tints && worn.has(who.tint)) who.tint = tints.find((t) => !worn.has(t)) ?? who.tint;   // (two in the same colour run together)
    worn.add(who.tint);
    if (R.wear) Object.assign(who, R.wear);
    if (R.props) who.props = { ...who.props, ...resolve(R.props, stream(seed, "gear", id, name, "props")) };
    const arms = {}, targets = {};
    for (const [side, name2] of Object.entries(who.props ?? {})) { const at = name2 && data.parts.props[name2]?.at; if (at) arms[side] = { hand: at, bend: 1 }; }   // (where a thing is held, whoever holds it)
    for (const [side, [other, where]] of Object.entries(R.reach ?? {})) if (actors[other]) { const key = `${other}.${where}`; targets[key] = spot(actors[other], where); arms[side] = { ...arms[side], reach: key }; }
    const held = data.actions[action].arms, ahead = (held?.of?.[0] ?? held)?.L?.hand?.[0];
    if (who.shield && !arms.L && !R.reach?.L && (Array.isArray(ahead) ? ahead[1] : ahead ?? 0) < data.canon.shieldAhead) arms.L = { hand: data.canon.shieldHold, bend: 1 };   // (a shield is held at whoever is there, whatever a bare arm would do in that action)
    const dir = resolve(R.face, ra) * mirror, mount = actors[R.on]?.beast, bearer = actors[R.on]?.pose;   // (on a beast: at its seat, sharing its depth; on someone's back: at that place on him, drawn over him)
    const mp = mount?.anchors[R.onAt ?? "seat"], onMan = bearer && anchor(bearer, R.onAt ?? "chest"), x = mount ? mount.place([mp[0] + (R.onDx ?? 0), mp[1]])[0] : bearer ? onMan[0] + bearer.dir * (R.onDx ?? 0) : pick(R.at, ra) * mirror * tight, y = mount ? mp[1] + (R.onDy ?? 0) : bearer ? onMan[1] + (R.onDy ?? 0) : 0;
    const solve = (at, down = 0) => solvePose(data, action, { dir, x: at, y, scale: R.size ?? 1, r: stream(seed, "pose", id, name), targets: Object.fromEntries(Object.entries(targets).map(([k, q]) => [k, [q[0], q[1] - down]])), over: { period: per, arms, shield: !!who.shield } });
    const rests = (at) => {                                            // (one lying down rests on the ground line, a knee doesn't go through it, and he is aimed at there; a hand on someone is solved for where it ends up)
      let P = solve(at);
      const low = lowest(buildFigure(data, P, { ...who, rng: stream(seed, "cloth", id, name) }, period)), by = data.actions[action].ground || (low < 0 && !R.on) ? -low : 0;
      if (by) { if (Object.keys(targets).length) P = solve(at, by); lift(P, by); }
      return P;
    };
    let pose = rests(x);
    const reacher = !mount && !bearer && Object.keys(arms).find((s) => arms[s].reach);   // (a hand that can't get there: the body steps in, the same pose)
    if (reacher) {
      const aim = targets[arms[reacher].reach], hand = handAt(pose, reacher), gap = Math.hypot(hand[0] - aim[0], hand[1] - aim[1]);
      if (gap > 1.5) pose = rests(x + Math.sign(aim[0] - hand[0]) * gap);
    }
    const foe = !mount && !reacher && data.actions[action].attack && armed(who) && foeOf({ id, cast: castName, pose, who });
    if (foe) {                                                         // (a weapon that doesn't get there: he steps in, as far as a step goes)
      const side = armed(who), pr = data.parts.props[who.props[side]], hand = handAt(pose, side), c = anchor(foe.pose, "chest"), len = pr.shaft ? pr.shaft * (1 - pr.grip) : data.canon.closeReach;
      const gap = Math.hypot(hand[0] - c[0], hand[1] - c[1]) - len;
      const room = Math.abs(foe.pose.x - pose.x) - data.canon.closeMin - (who.shield && foe.who.shield ? data.canon.closeShields : 0);
      const across = solved.some((q) => actors[q].down && (actors[q].pose.x - pose.x) * pose.dir > 0 && (foe.pose.x - actors[q].pose.x) * pose.dir >= 0);   // (not onto one lying between them)
      if (gap > 0 && room > 0 && !across) pose = rests(pose.x + pose.dir * Math.min(gap, room, data.canon.closeBy * spread));
    }
    actors[id] = { id, cast: castName, who, pose, R, down: !!data.actions[action].ground, regrip: (arm, q) => { const key = `clutch.${arm}`; targets[key] = q; arms[arm] = { ...arms[arm], reach: key }; return rests(actors[id].pose.x); } };
    if (actors[id].down) tight = Math.max(tight, spread * .62);                              // (someone lying needs some of his length: the one over him may stand across his feet, the `under` fault keeps him off the trunk)
    solved.push(id);
  }
  for (const id of solved) for (const [arm, [other, where]] of Object.entries(actors[id].R.clutch ?? {})) if (actors[other]) actors[id].pose = actors[id].regrip(arm, spot(actors[other], where));   // (a hand on the hand that has hold of him, solved once that one has been)
  const wounds = [];
  const linked = new Set((S.links ?? []).map(([from]) => from));
  const implied = solved.flatMap((id) => {
    const A = actors[id], side = A.pose && armed(A.who), foe = side && !A.R.aim && !linked.has(id) && data.actions[A.pose.action].attack && foeOf(A);
    return foe ? [[id, side, foe.id, "belly"]] : [];
  });
  for (const [from, side, to, where] of [...(S.links ?? []), ...implied]) {
    if (!actors[from] || !actors[to]) continue;
    const a = actors[from].who;
    if (!a.props?.[side]) continue;
    let at = spot(actors[to], resolve(where, stream(seed, "aim", from, name)));
    const P = actors[from].pose, hand = handAt(P, side);
    if (actors[to].who?.shield) {                                      // (a shield in the way takes the point)
      const c = actors[to].pose.place(shieldCentre(actors[to].pose));
      const d = [at[0] - hand[0], at[1] - hand[1]], L = Math.hypot(d[0], d[1]) || 1, t = ((c[0] - hand[0]) * d[0] + (c[1] - hand[1]) * d[1]) / L;
      if (t > 0 && t < L && Math.abs((c[0] - hand[0]) * d[1] - (c[1] - hand[1]) * d[0]) / L < data.canon.shieldR * .85) { (a.aims ??= {})[side] = c; continue; }
    }
    if (actors[to].pose) {                                        // (someone `hurt` has it in him, no point showing; anyone else it hasn't reached yet)
      const L = Math.hypot(at[0] - hand[0], at[1] - hand[1]) || 1, pr = data.parts.props[a.props[side]];
      if (data.actions[actors[to].pose.action].hurt && pr.shaft && L / P.scale <= pr.shaft * (1 - pr.grip)) { (a.hits ??= {})[side] = 1; wounds.push(at); }   // (only what gets there: no wound from a weapon held off, no headless shaft in the air)
      else { const k = Math.max(0, 1 - data.canon.shortOf / L); at = [hand[0] + (at[0] - hand[0]) * k, hand[1] + (at[1] - hand[1]) * k]; }
    }
    (a.aims ??= {})[side] = at;
  }
  for (const id of solved) {                                           // (a shaft carried at an angle, not at anyone)
    const A = actors[id], q = A.R.aim, ra = stream(seed, "carry", id, name);
    if (q && A.who.props?.R) (A.who.aims ??= {}).R = [A.pose.x + A.pose.dir * pick(q[0], ra) * 200, pick(q[1], ra) * 200];
  }
  const pieces = [], weave = sparse && !S.wide && !solved.some((id) => actors[id].beast || actors[id].R.on) ? data.canon.weave : 100;   // (two alone in a panel go through each other: the one's arm over the other's far leg, not one whole body on the other)
  let band = 0;
  solved.forEach((id) => {
    const A = actors[id], i = A.band = A.R.on && actors[A.R.on].beast ? actors[A.R.on].band : band++;
    if (A.beast) { for (const p of A.beast.pieces) { p.z += i * 100; pieces.push(p); } return; }
    const own = buildFigure(data, A.pose, A.who, period);
    const crew = A.R.on && actors[A.R.on].beast && !actors[A.R.on].gait ? solved.filter((q) => actors[q].R.on === A.R.on) : [];   // (two in one car: one behind the other, all under its rail; on a beast, each astride)
    for (const p of own) { p.z = i * weave + (crew.length > 1 ? p.z * .4 + crew.indexOf(id) * 33 : p.z); pieces.push(p); }
  });
  const reins = S.reins ?? (S.chain?.rider ? solved.filter((id) => id[0] === "c").map((id) => [id, `h${id.slice(1)}`]) : []);
  for (const [rider, beast] of reins) {                                 // a thin strap from the bridle hand to the mouth, hanging a little
    const a = actors[rider], b = actors[beast];
    if (!a?.pose || !b?.beast) continue;
    const u = a.pose.place(a.pose.arms.L.hand), v = spot(b, "mouth"), d = Math.hypot(v[0] - u[0], v[1] - u[1]) || 1, nx = -(v[1] - u[1]) / d * .28, ny = (v[0] - u[0]) / d * .28, m = [(u[0] + v[0]) / 2, (u[1] + v[1]) / 2 - d * .07];
    pieces.push({ z: band * 100, owner: rider, role: "wood", shaft: 1, rings: [[[u[0] + nx, u[1] + ny, 1], [m[0] + nx, m[1] + ny], [v[0] + nx, v[1] + ny, 1], [v[0] - nx, v[1] - ny, 1], [m[0] - nx, m[1] - ny], [u[0] - nx, u[1] - ny, 1]]], lines: [], marks: [] });
  }
  for (const [who, where] of S.wounds ?? []) if (actors[who]) wounds.push(spot(actors[who], where));
  const rw = stream(seed, "wound", name), drop = ([x, y], s) => [[x, y + s * 1.7, 1], [x + s, y], [x, y - s], [x - s, y]];
  wounds.forEach((w) => { for (let i = 0; i < data.canon.drops; i++) pieces.push({ z: 9000, role: "blood", noContour: 1, rings: [drop([w[0] + (rw() - .5) * 5, w[1] - 1 - i * (4.5 + rw() * 3)], 1.9 - i * .3)], lines: [], marks: [] }); });
  if (S.scale) { const q = mapPieces(pieces, ([x, y]) => [x * S.scale, y * S.scale]); pieces.length = 0; pieces.push(...q); }
  let min = Infinity, max = -Infinity, height = 0;
  for (const p of pieces) if (!p.shaft) for (const r of p.rings) for (const q of r) { if (q[0] < min) min = q[0]; if (q[0] > max) max = q[0]; if (q[1] > height) height = q[1]; }
  return { pieces, min, max, height, actors, name };
}

// pieces moved and scaled (the only thing a field does to a body)
export function mapPieces(pieces, f) {
  const m = (q) => { const w = f(q); return q[2] ? [w[0], w[1], 1] : w; };
  return pieces.map((p) => ({ ...p, rings: p.rings.map((r) => r.map(m)), lines: p.lines.map((l) => ({ ...l, pts: l.pts.map(m) })), marks: p.marks.map((k) => ({ ...k, at: m(k.at), r: k.r * Math.abs((f([1, 0])[0] - f([0, 0])[0])) })) }));
}
