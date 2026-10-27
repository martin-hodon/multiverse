// THE FORTIFIED WARD (a `ward` part): a curtain round a plan and the towers that defend it, worked out from the rules a
// thirteenth-century mason built by, not placed by eye. It writes the engine's own parts -- enclosures, walls, prisms,
// spiral stairs -- and assemble.js builds them as any other.
//   FLANKING: a tower stands on every corner of the curtain, centred on the corner of its outer face, so that it
//     projects its whole radius past both faces it joins -- from its loops the foot of each curtain can be seen and
//     shot along. A face longer than `towers.flank` (bowshot between two towers) gets towers between, evenly.
//   THE GATE: a passage through the curtain on face `gate.face`, between two towers that stand close on either side.
//   THE WALL WALK runs on the curtain's head behind a CRENELLATED PARAPET on its outer edge: a breastwork `breast`
//     high, cut by crenels from the top every `step`, the merlons wider than the crenels between them.
//   THE TOWERS rise a storey (`over`) above the walk, floored at the walk and every `storeyH` below it, under a deck
//     with its own parapet. The walk runs through them: a doorway at its level wherever a curtain comes in. Every
//     tower has a NEWEL STAIR from the ward to its deck, passing every floor, its rise worked so each floor is a tread.
//   LOOPS AND WINDOWS: loops look onto the field, staggered storey by storey so no line of the wall is weakened all
//     the way up, and on every storey a loop on the first face clear of each curtain -- the one that rakes its foot;
//     the faces the curtains cover are blind; the face onto the ward has the door below and windows above.
//   THE TALUS: the foot of curtain and towers battered, one level all round; MACHICOLATIONS over every gate.
// The plan is the curtain's OUTER face line, a convex polygon. `def`: { plan, height, thickness, parapet: { breast,
// merlon, t, step, crenel }, towers: { radius, wall, sides, over, storeyH, flank, stair }, gate: { face, width,
// height, radius, at } } -- or `gates`, a list of them -- `talus: { h, out }` or false, `machicolation` false.
import { planPoints } from "./build.js";

export function wardDefs(def, P, plan) {
  const O = planPoints(plan), N = O.length;
  const H = P(def.height, 9), t = P(def.thickness, 2.2);
  const pp = def.parapet ?? {}, breast = P(pp.breast, 1.1), merlon = P(pp.merlon, .9), tp = Math.min(P(pp.t, .5), t / 2);
  const step = P(pp.step, 2.2), crenel = P(pp.crenel, .75);
  const T = def.towers ?? {}, R0 = P(T.radius, 5), w0 = P(T.wall, Math.max(1, t * .6)), sides = Math.max(8, Math.round(P(T.sides, 16)));
  const flank = P(T.flank, 40), storeyH = P(T.storeyH, 4), stairs = T.stair !== false;
  // THE TALUS: the foot of the curtain and the towers spread in a batter, a quarter of the walk's height, sloping one
  // in three and a half -- it throws a stone dropped from the parapet out at the attackers and thickens the wall where
  // it would be mined; the same level all round, towers and curtain
  const talH = def.talus === false ? 0 : P(def.talus?.h, H * .22), talus = talH > 0
    ? { courses: { plinth: { h: talH, out: P(def.talus?.out, talH / 3.5), profile: "batter" }, strings: false, cornice: false } } : {};
  // MACHICOLATIONS over a gate: its parapet carried forward on corbels, with holes between them over the passage's mouth
  const mach = def.machicolation !== false, mo = tp + .35, corbH = .8, corbW = .45, corbStep = 1.0;
  const gates = def.gates ?? (def.gate ? [def.gate] : []);
  const unit = ([x, z]) => { const l = Math.hypot(x, z) || 1; return [x / l, z / l]; };
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
  const cx = O.reduce((s, p) => s + p[0], 0) / N, cz = O.reduce((s, p) => s + p[1], 0) / N;
  // every face: its direction along, its inward normal (toward the ward's middle)
  const faces = O.map((p, i) => {
    const q = O[(i + 1) % N], L = Math.hypot(q[0] - p[0], q[1] - p[1]), e = unit([q[0] - p[0], q[1] - p[1]]);
    let m = [-e[1], e[0]];
    if (dot(m, [cx - p[0], cz - p[1]]) < 0) m = [e[1], -e[0]];
    return { p, q, L, e, m };
  });
  // THE RISE every stair climbs by: the walk is a whole number of treads, and so is every floor and the deck
  const rise = H / Math.max(1, Math.round(H / .19)), snap = (y) => Math.round(y / rise) * rise;
  const deckT = .4;
  // THE TOWERS: on every corner, then the gate's pair and those a long face needs between
  const towers = [];
  const tower = (c, R, w, curt, inward, gate = false) => { towers.push({ c, R, w, curt, inward: unit(inward), gate }); return towers.length - 1; };
  const corner = O.map((p, i) => {
    const a = faces[(i - 1 + N) % N], b = faces[i];
    const e1 = [-a.e[0], -a.e[1]], e2 = b.e;   // (along each curtain, away from the corner)
    return tower(p, R0, w0, [{ e: e1, m: a.m }, { e: e2, m: b.m }], [e1[0] + e2[0], e1[1] + e2[1]]);
  });
  // the stations along each face: its two corners, and what stands between -- a segment of curtain runs between two
  const runs = [];
  faces.forEach((f, i) => {
    const st = [{ s: 0, k: corner[i] }, { s: f.L, k: corner[(i + 1) % N] }];
    let passage = null;
    for (const G of gates.filter((g) => Math.round(P(g.face, 0)) === i)) {
      const Wp = P(G.width, 3.6), Rg = P(G.radius, R0 * .75), s0 = f.L / 2 + P(G.at, 0), off = Wp / 2 + Rg + .3;   // (the towers clear of the passage)
      for (const sg of [-1, 1]) {
        const s = s0 + sg * off, c = [f.p[0] + f.e[0] * s, f.p[1] + f.e[1] * s];
        st.push({ s, k: tower(c, Rg, Math.min(w0, Rg * .3), [{ e: [-f.e[0], -f.e[1]], m: f.m }, { e: f.e, m: f.m }], f.m, true) });
      }
      passage = { s: s0, w: Wp, h: P(G.height, 4.5) };
    }
    st.sort((a, b) => a.s - b.s);
    // (towers between, where two stations stand further apart than bowshot)
    const all = [];
    st.forEach((a, j) => {
      all.push(a);
      const b = st[j + 1];
      if (!b) return;
      const k = Math.ceil((b.s - a.s) / flank) - 1;
      for (let u = 1; u <= k; u++) {
        const s = a.s + (b.s - a.s) * u / (k + 1), c = [f.p[0] + f.e[0] * s, f.p[1] + f.e[1] * s];
        all.push({ s, k: tower(c, R0, w0, [{ e: [-f.e[0], -f.e[1]], m: f.m }, { e: f.e, m: f.m }], f.m) });
      }
    });
    for (let j = 0; j + 1 < all.length; j++) runs.push({ f, a: all[j], b: all[j + 1], passage: passage && passage.s > all[j].s && passage.s < all[j + 1].s ? passage : null });
  });
  // how far along its line a curtain reaches into a tower: its end square in the tower's wall, clear of the room
  const reach = (k) => { const T_ = towers[k], cs = Math.cos(Math.PI / sides), aIn = T_.R * cs - T_.w; return (aIn / cs + T_.R * cs) / 2; };
  const defs = {};
  // THE CURTAIN and its parapet, segment by segment
  runs.forEach((r, j) => {
    const { f, a, b } = r, s0 = a.s + reach(a.k), s1 = b.s - reach(b.k), L = s1 - s0;
    if (L < .5) return;
    const sm = (s0 + s1) / 2, mid = [f.p[0] + f.e[0] * sm, f.p[1] + f.e[1] * sm];
    // (a wall's front face is its line and its back runs -z: the outward normal is its +z, its length along +x)
    const yaw = Math.atan2(-f.m[0], -f.m[1]), xdir = [Math.cos(yaw), -Math.sin(yaw)], flip = dot(xdir, f.e) < 0;
    const openings = [];
    if (r.passage) {
      const u = r.passage.s - s0, at = flip ? L - u : u, Wp = r.passage.w;
      openings.push({ at, width: Wp, sill: 0, springing: Math.max(1, r.passage.h - Wp / 2), head: { profile: "semicircular" }, glass: false });
    }
    defs[`curtain ${j + 1}`] = { type: "wall", width: L, height: H, thickness: t, glass: false, walked: true, openings, ...talus, at: [[mid[0], 0, mid[1], yaw]] };
    // the parapet: from tower wall to tower wall, its crenels every `step` across the middle of its length -- over a
    // gate standing out on its corbels, the floor of the walk carried out to it between them
    const Lp = L, k = Math.max(0, Math.floor((Lp - 1.2) / step)), first = (Lp - (k - 1) * step) / 2;
    const cren = Array.from({ length: k }, (_, i) => ({ at: first + i * step, width: crenel, sill: breast, springing: breast + merlon, head: { profile: "flat" }, glass: false }));
    const out = r.passage && mach ? mo : 0, pm = [mid[0] - f.m[0] * out, mid[1] - f.m[1] * out];
    if (out) {     // (the corbels first: the parapet is set on them)
      const nc = Math.max(2, Math.floor((Lp - corbW) / corbStep) + 1), sp = (Lp - corbW) / (nc - 1);
      defs[`machicolation ${j + 1}`] = { type: "box", width: corbW, length: mo, height: corbH, at: Array.from({ length: nc }, (_, i) => {
        const u = s0 + corbW / 2 + i * sp - (s0 + s1) / 2, x = mid[0] + f.e[0] * u - f.m[0] * mo / 2, z = mid[1] + f.e[1] * u - f.m[1] * mo / 2;
        return [x, H - corbH, z, yaw];
      }) };
    }
    defs[`parapet ${j + 1}`] = { type: "wall", width: Lp, height: breast + merlon, thickness: tp, glass: false, openings: cren, at: [[pm[0], H, pm[1], yaw]] };
  });
  // THE TOWERS, each from its own measures and the curtains it flanks
  towers.forEach((T_, j) => {
    const { c, R, w, curt, inward } = T_, n = sides, cs = Math.cos(Math.PI / n), aOut = R * cs, aIn = aOut - w;
    const over = P(T.over, 4.2) * (T_.gate ? .9 : 1), deckTop = H + snap(over), HT = deckTop - deckT;
    // its floors: every storeyH under the walk (on a tread of the stair), the walk's own, and the deck
    const m = Math.max(1, Math.round(H / storeyH)), levels = [...Array.from({ length: m - 1 }, (_, i) => snap(H * (i + 1) / m)), H];
    const bounds = [0, ...levels, HT];
    // its faces: face k looks out at bearing (k + 1) 2pi / n -- (sin, cos) -- its middle aOut out
    const bearing = (k) => (k + 1) * 2 * Math.PI / n, nrm = (k) => [Math.sin(bearing(k)), Math.cos(bearing(k))];
    const faceAt = (v) => { let best = 0, bd = -Infinity; for (let k = 0; k < n; k++) { const d = dot(nrm(k), unit(v)); if (d > bd) { bd = d; best = k; } } return best; };
    // (a face the curtain -- or above the walk, its parapet -- stands against: blind)
    const covered = (k, band) => curt.some(({ e, m: mm }) => {
      const v = [nrm(k)[0] * aOut, nrm(k)[1] * aOut], along = dot(v, e), across = dot(v, mm);
      return along > 0 && across > -.35 && across < band + .35;
    });
    const ward = (k) => dot(nrm(k), inward) > .5 && !covered(k, t);
    const door = (() => { let best = -1, bd = -Infinity; for (let k = 0; k < n; k++) if (!covered(k, t) && dot(nrm(k), inward) > bd) { bd = dot(nrm(k), inward); best = k; } return best; })();
    // where the walk comes in: the face its middle line crosses, the parapet's thickness and half the walk in
    const walkDoors = curt.map(({ e, m: mm }) => faceAt([e[0] * aOut + mm[0] * (tp + (t - tp) / 2), e[1] * aOut + mm[1] * (tp + (t - tp) / 2)]));
    // the flanking faces: the first clear of each curtain, on its outer side
    const flankers = new Set();
    for (const { e, m: mm } of curt) {
      let best = -1, bd = Infinity;
      for (let k = 0; k < n; k++) {
        const v = nrm(k);
        if (covered(k, t) || dot(v, mm) > -.05) continue;          // (clear of the wall, and outside its face)
        const ang = Math.acos(Math.max(-1, Math.min(1, dot(v, e))));
        if (ang < bd) { bd = ang; best = k; }
      }
      if (best >= 0) flankers.add(best);
    }
    const loopW = .18, faceW = 2 * R * Math.sin(Math.PI / n);
    const tierOf = (k, s) => {
      const y0 = bounds[s], h = bounds[s + 1] - y0, top = s === bounds.length - 2, ops = [];
      if (s === 0 && k === door) ops.push({ at: 0, width: Math.min(1.3, faceW - .5), sill: 0, springing: Math.min(2.2, h - .6), head: { profile: "semicircular" }, glass: false });
      else if (top && walkDoors.includes(k)) ops.push({ at: 0, width: Math.min(1.2, faceW - .5), sill: 0, springing: Math.min(2.1, h - .8), head: { profile: "semicircular" }, glass: false });
      else if (covered(k, top ? tp : t)) { /* blind */ }
      else if (ward(k)) { if (s > 0 && h > 2.8) ops.push({ at: 0, width: .6, sill: 1.0, springing: Math.min(2.0, h - .9), head: { profile: "semicircular" }, glass: false }); }
      else if ((flankers.has(k) || (k + s) % 2 === 0) && h > 2.2) ops.push({ at: 0, width: loopW, sill: .9, springing: Math.min(2.3, h - .6), head: { profile: "flat" }, glass: false });
      return top ? { openings: ops } : { h, openings: ops };
    };
    const faceTiers = {};
    for (let k = 0; k < n; k++) faceTiers[String(k)] = bounds.slice(0, -1).map((_, s) => tierOf(k, s));
    const name = `tower ${j + 1}`, place = [[c[0], 0, c[1], 0]];
    defs[name] = { type: "enclosure", plan: { sides: n, radius: R }, thickness: w, height: HT, glass: false, faces: faceTiers, tiers: [{ openings: [] }], ...talus, at: place };
    // the newel stair: against the wall a quarter turn round from the door, from the ward to the deck
    const sr = Math.min(1.3, aIn * .42), ang = Math.atan2(inward[0], inward[1]) + Math.PI / 2, ds = aIn - sr - .12;
    const so = [Math.sin(ang) * ds, Math.cos(ang) * ds];
    const well = stairs ? { well: { radius: sr + .1, sides: 12, at: so } } : {};
    const fr = (aOut - w / 2) / cs;     // (a floor's edge laid in the middle of the wall)
    levels.forEach((y, i) => {
      defs[`${name} floor ${i + 1}`] = { type: "prism", plan: { sides: n, radius: fr, ...well }, height: .3, walked: true, at: [[c[0], y - .3, c[1], 0]] };
    });
    defs[`${name} deck`] = { type: "prism", plan: { sides: n, radius: R, ...well }, height: deckT, walked: true, flatRoof: true, at: [[c[0], HT, c[1], 0]] };
    const cw = Math.min(crenel, faceW * .4);
    defs[`${name} parapet`] = { type: "enclosure", plan: { sides: n, radius: R }, thickness: tp, height: breast + merlon, glass: false,
      openings: [{ at: 0, width: cw, sill: breast, springing: breast + merlon, head: { profile: "flat" }, glass: false }], at: [[c[0], deckTop, c[1], 0]] };
    if (stairs) defs[`${name} stair`] = { type: "spiral-stair", radius: sr, newel: .15, turn: 28, top: deckTop, steps: Math.round(deckTop / rise), soffit: .2,
      at: [[c[0] + so[0], 0, c[1] + so[1], ang]] };
  });
  return defs;
}
