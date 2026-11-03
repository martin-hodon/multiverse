// THE MINE (2026-10-03; fitted to the land 2026-11-03): a mine of the Middle Ages -- silver, copper or salt (`ore`) --
// as an arch-engine definition. One function makes it for any ground: the catalogue's (assets/architecture/village/mine.json,
// written by tools/archgen/mine.mjs on level ground 0) and the game's own, laid into the world's hills (index.html).
//
// Only its ENTRANCE needs level ground: the SHAFT HEAD -- the shaft house over the hauling shaft and the walking shaft
// beside it under its roof -- stands on a small flat spot (`FLAT`, ~15 x 6 m) settled to the ground's own height there
// (`h0`, a hillside's too: ground.js flatZones `y`); the spoil heap, the dressing bench and the pit timber stand each on
// the ground under it. Underground nothing touches the land: the shafts go down 10 m or more (in steps of 5 m: two
// flights of the walking shaft's), the galleries run out from the shaft bottom and keep at least `COVER` metres of rock
// over their heads -- where the land above them falls away (a hill's flank, a valley) they go DOWN, a short flight of
// steps at a time, and never back up: the stopes at their ends are where they arrive.
//
// Layout (the CANONICAL frame: the hauling shaft at 0,0, the main gallery north +z): on the surface the shaft house
// (Kaue) with the WINDLASS (Haspel) and its two men, the kibbles on the rope; the walking shaft (Fahrschacht) with steep
// flights (25 cm on 25 cm) turning on landings at each end; the spoil heap (Halde), the ore-dressing bench, pit
// timber. Down below: the SHAFT BOTTOM (Füllort) chamber with the hooker; the GALLERIES (Strecken) 1.6 m wide and
// 2.1 high, held by door sets every 1.5 m (none in the salt), a plank track for the carts (Hunte); the STOPES (Abbaue)
// at their ends with the vein, the hewers and their lamps. The miners are the mine's own CREW (`crew: "miner"`).
// The definition's ORIGIN is the yard's middle; the whole is turned by `dir` quarter turns (yaw).
//
// Or an ADIT (Stollen, 2026-11-03: `kind: "adit"`) where the land rises steeply: a stone portal with a timber door set
// at the foot of a slope, only a small apron in front of it settled level with its floor (`ADIT.APRON`, the slope behind
// left as it is), the adit driven level into the hill -- a covered PASSAGE first, `pc` metres until the ground over it
// stands `ADIT.RISE` over its floor (the ground is open over it while the slope is under its roof: its `dig`), then `ADIT.LIN` m on
// under the hill -- to the same chamber the shaft's bottom is, the galleries leaving it as before and going down where
// the land over them falls away. Its yard (the heap, the bench, the timber) lies before the portal.

export const MINE = {
  GH: 2.1, GW: 1.6, T: 0.5,     // a gallery's height and width, the rock round it
  COVER: 4,                      // metres of ground (at the least) over a gallery's head -- a chamber's, a stope's
  LS: 2.5,                       // a walking-shaft flight's drop (two of them: the shaft deepens in steps of 5 m)
  DMAX: 2,                       // the most a gallery drops at one flight
  SEG: 4.5,                      // a gallery's level stretches (the most: a flight starts each that drops)
  FLAT: [-3.6, 11.6, -3.2, 3.2], // the entrance's flat spot (canonical x0 x1 z0 z1): the shaft house, the walking shaft's roof
  YARD: [-12.4, 11.8, -6.2, 8.8],// the yard (canonical): the spoil heap to the pit timber -- the site's footprint
  MAIN: [3.0, 30.0], SIDE: [-3.0, -20.0],   // the galleries (canonical z, from the chamber's face out)
  // the adit: its level apron before the portal (m deep), the passage at the most (until the ground stands RISE over
  // its floor), the adit on from there to the chamber's east wall (canonical: the adit runs -x into the hill); SLOPE:
  // what makes a site an adit's (placeMine); DIP: how far its main gallery goes down a stretch, after its vein
  DEEP: 0,   // (no floor of its own opens the ground over it -- only its `dig`: the site's `deep`, index.html GROUND_HOLES and the walk)
  ADIT: { APRON: 4.5, PCMIN: 2, PCMAX: 24, RISE: 6.1, LIN: 10, SLOPE: .3, DIP: .75,
    BANK: { H: 3.3, FADE: 4 } },   // (the earth heaped behind its portal: up to H over the floor, falling away over FADE m)   // (RISE: COVER over the adit's head)
};
const PI = Math.PI, PI2 = PI / 2, R = (v) => Math.round(v * 1e4) / 1e4;
const YC = [(MINE.YARD[0] + MINE.YARD[1]) / 2, (MINE.YARD[2] + MINE.YARD[3]) / 2];   // the yard's middle: the definition's origin
// canonical -> the site's own frame (origin the yard's middle, turned `dir` quarter turns the arch engine's way)
// (`yc`: the origin in the canonical frame -- the shaft's yard middle, or an adit's own)
const turn = (dir, yc = YC) => { const a = dir * PI2, c = Math.round(Math.cos(a)), s = Math.round(Math.sin(a));
  return { a, f: (x, z) => { const u = x - yc[0], v = z - yc[1]; return [u * c + v * s, -u * s + v * c]; } }; };
// a canonical rectangle [x0 x1 z0 z1] in the site's frame (still axis-aligned: quarter turns)
const turnRect = (T, [x0, x1, z0, z1]) => { const [a, b] = T.f(x0, z0), [c, d] = T.f(x1, z1); return [Math.min(a, c), Math.max(a, c), Math.min(b, d), Math.max(b, d)]; };

// the GALLERIES' stretches: [from, to] canonical z along each, chamber outward
const stretches = ([a0, a1]) => { const n = Math.max(1, Math.round(Math.abs(a1 - a0) / MINE.SEG)), out = [];
  for (let i = 0; i < n; i++) out.push([a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n]); return out; };
const GALLERIES = { main: { c: -1.5, along: MINE.MAIN, stope: [-5.0, 2.0, 30.0, 36.0, 3.4] }, side: { c: 1.5, along: MINE.SIDE, stope: [-2.0, 5.0, -26.0, -20.0, 3.2] } };

// THE PLAN for a site: where it is and how deep each part lies, read from the ground. `ground(x, z)` the world's ground
// (index.html groundH), `x z` the site (a shaft's: its yard's middle; an adit's: its portal), `dir`, `kind` "shaft" |
// "adit". -> { kind, x, z (the definition's origin in the world), dir, h0 (the entrance's level: the middle height of
// the ground over its flat spot), Yb (the chamber's floor), main: [floor per stretch], side: [...], depth (the shafts'),
// cover: the least rock over any head, range: how far the flat spot's ground was off level, yc, flat, yard (canonical),
// an adit's pc, xp } -- or { bad } where an adit cannot be (no hill behind it, the chamber or a gallery without rock)
export function minePlan(ground, x, z, dir = 0, kind = "shaft") {
  const { GH, GW, T: RT, COVER, LS, DMAX } = MINE, A = MINE.ADIT;
  let FLAT = MINE.FLAT, YARD = MINE.YARD, yc = YC, W, h0, lo = 1e9, hi = -1e9, pc = 0, XP = 0;
  if (kind === "adit") {
    // the portal at x z, the hill behind it (canonical -x): t metres in, v across
    const rot = turn(dir, [0, 0]).f, P = (t, v) => { const [u, w] = rot(-t, v); return [x + u, z + w]; };
    for (let t = -A.APRON; t <= 1e-6; t += A.APRON / 3) for (const v of [-2.6, 0, 2.6]) { const g = ground(...P(t, v)); lo = Math.min(lo, g); hi = Math.max(hi, g); }
    h0 = (lo + hi) / 2;
    // the passage: until the ground over the adit (its rock either side too) stands RISE over the floor, and stays so
    const N = A.PCMAX + A.LIN + 10, low = [];
    for (let t = 0; t <= N; t++) low.push(Math.min(...[-1.3, 0, 1.3].map((v) => ground(...P(t, v)))));
    for (let t = N - 1; t >= 0; t--) low[t] = Math.min(low[t], low[t + 1]);
    pc = low.findIndex((g, t) => t >= A.PCMIN && g >= h0 + A.RISE);
    if (pc < 0 || pc > A.PCMAX) return { kind, bad: "hill", h0, range: hi - lo };
    XP = 6.3 + A.LIN + pc;
    FLAT = [XP, XP + A.APRON, -2.6, 2.6];
    YARD = [XP - pc - .5, XP + 12.0, -9.0, 8.0];
    yc = [(YARD[0] + YARD[1]) / 2, (YARD[2] + YARD[3]) / 2];
    const T = turn(dir, [XP, 0]); W = (cx, cz) => { const [u, v] = T.f(cx, cz); return [x + u, z + v]; };
  } else {
    const T = turn(dir); W = (cx, cz) => { const [u, v] = T.f(cx, cz); return [x + u, z + v]; };
    // the flat spot's ground (and its level: the middle of what is there, half cut and half filled)
    for (let cx = FLAT[0]; cx <= FLAT[1] + 1e-6; cx += (FLAT[1] - FLAT[0]) / 6) for (let cz = FLAT[2]; cz <= FLAT[3] + 1e-6; cz += (FLAT[3] - FLAT[2]) / 3) {
      const g = ground(...W(cx, cz)); if (g < lo) lo = g; if (g > hi) hi = g;
    }
    h0 = (lo + hi) / 2;
  }
  // the ground over a canonical rectangle, at its lowest (near the entrance never above the flat spot it is settled to)
  const near = kind === "adit" ? 4 : 9;
  const low = (x0, x1, z0, z1) => { let m = 1e9;
    for (let cx = x0; cx <= x1 + 1e-6; cx += Math.max(.5, (x1 - x0) / Math.ceil((x1 - x0) / 1.5))) for (let cz = Math.min(z0, z1); cz <= Math.max(z0, z1) + 1e-6; cz += Math.max(.5, Math.abs(z1 - z0) / Math.ceil(Math.abs(z1 - z0) / 1.5))) {
      let g = ground(...W(cx, cz));
      if (cx > FLAT[0] - near && cx < FLAT[1] + near && cz > FLAT[2] - near && cz < FLAT[3] + near) g = Math.min(g, h0);
      if (g < m) m = g;
    }
    return m; };
  // what each part may be at the most: its head COVER under the lowest ground over it
  const need = {}, cap = {};
  for (const [k, G] of Object.entries(GALLERIES)) {
    const w = GW / 2 + RT;
    need[k] = stretches(G.along).map(([a, b]) => low(G.c - w, G.c + w, a, b) - COVER - GH);
    const [sx0, sx1, sz0, sz1, sh] = G.stope;
    // (the stope at the end is at the last stretch's floor: that stretch keeps its rock too)
    need[k][need[k].length - 1] = Math.min(need[k].at(-1), low(sx0 - RT, sx1 + RT, sz0 - RT, sz1 + RT) - COVER - sh);
    // (back from the far end: no flight drops more than DMAX)
    cap[k] = need[k].slice();
    for (let i = cap[k].length - 2; i >= 0; i--) cap[k][i] = Math.min(cap[k][i], cap[k][i + 1] + DMAX);
  }
  const chamber = low(-3.0 - RT, 5.8 + RT, -3.0 - RT, 3.0 + RT) - COVER - 3.0;
  const want = Math.min(h0 - 10, chamber, cap.main[0], cap.side[0]);   // (the first stretches leave the chamber level)
  let depth = 0, Yb = h0;   // (an adit's chamber: at its floor, the adit level)
  if (kind === "adit") { if (Math.min(chamber, cap.main[0], cap.side[0]) < h0 - 1e-6) return { kind, bad: "rock", h0, range: hi - lo }; }
  else { depth = 2 * LS * Math.ceil((h0 - want) / (2 * LS) - 1e-9); Yb = h0 - depth; }
  const [ox, oz] = W(...yc);
  const out = { kind, x: ox, z: oz, dir, h0: R(h0), Yb: R(Yb), depth, range: R(hi - lo), yc, flat: FLAT, yard: YARD, ...(kind === "adit" ? { pc, xp: XP } : {}) };
  // (outward each stretch at the one before's floor, or lower by whole quarter metres where it must: a flight of at
  //  least two 12.5 cm steps)
  //  An adit's main gallery follows its vein down besides, `ADIT.DIP` a stretch (under a hill the land seldom makes it).
  if (kind === "adit") cap.main = cap.main.map((c, i) => Math.min(c, Yb - A.DIP * i));
  for (const k of Object.keys(GALLERIES)) { let y = Yb; out[k] = cap[k].map((c) => (y = c < y - 1e-6 ? R(y - .25 * Math.ceil((y - c) / .25 - 1e-6)) : y)); }
  // the least rock over any head, as laid out (what the game checks again over the finished ground: index.html __mineInfo)
  out.cover = R(Math.min(chamber + COVER + 3.0 - Yb, ...Object.keys(GALLERIES).flatMap((k) => out[k].map((y, i) => need[k][i] - y + COVER))));
  return out;
}

// THE DEFINITION for a plan (minePlan's; the catalogue's: minePlan(() => 0, 0, 0)), `ore`; `ground(x, z)` the world's
// (the yard's things stand each on the ground under it -- none: on h0). Every y in it is the world's.
export function mineDoc(plan, { ore = "silver", ground = null } = {}) {
  const { GH, GW, T, LS } = MINE, { h0, Yb } = plan, TT = turn(plan.dir ?? 0, plan.yc ?? YC), adit = plan.kind === "adit";
  const at0 = (cx, cz) => { const [u, v] = TT.f(cx, cz); return [plan.x + u, plan.z + v]; };
  // the ground under a thing on the yard at canonical cx cz (r: how far it reaches), at its lowest -- it is set in, not
  // hung over a slope
  const gy = (cx, cz, r = 0) => { if (!ground) return h0; let m = 1e9;
    for (const [dx, dz] of [[0, 0], [r, 0], [-r, 0], [0, r], [0, -r], [r * .7, r * .7], [-r * .7, r * .7], [r * .7, -r * .7], [-r * .7, -r * .7]]) m = Math.min(m, ground(...at0(cx + dx, cz + dz)));
    return m; };
  const parts = {}, ROCK = [], TIMBER = [], FLOORS = [], VEINS = [], STONE = [];
  const TIMBERED = { ore: ["silver", "copper"] };
  const pts = (ps) => ps.map((p) => [R(p[0]), R(p[1]), R(p[2]), R(p[3] ?? 0)]);
  const box = (w, l, h, ps, k = {}) => ({ type: "box", width: R(w), length: R(l), height: R(h), at: pts(ps), ...k });
  const rect = (name, x0, x1, z0, z1, y, h, k = {}) => { parts[name] = box(x1 - x0, z1 - z0, h, [[(x0 + x1) / 2, y, (z0 + z1) / 2]], k); };
  const item = (path, ps, k = {}) => ({ type: "item", item: path, at: pts(ps), ...k });
  const marker = (role, ps, data) => ({ type: "marker", role, at: pts(ps), data });
  const minus = (r, holes) => {   // a rectangle (x0, x1, z0, z1) less some inside it: strips of what is left
    const xs = [...new Set([r[0], r[1], ...holes.flatMap((h) => [h[0], h[1]])])].sort((a, b) => a - b), out = [];
    for (let i = 0; i + 1 < xs.length; i++) {
      const a = xs[i], b = xs[i + 1];
      if (b - a < 1e-6 || b <= r[0] || a >= r[1]) continue;
      let zs = [[r[2], r[3]]];
      for (const h of holes) if (h[0] <= a + 1e-6 && h[1] >= b - 1e-6)
        zs = zs.flatMap(([z0, z1]) => [[z0, Math.min(z1, h[2])], [Math.max(z0, h[3]), z1]]).filter((s) => s[1] - s[0] > 1e-6);
      out.push(...zs.map(([z0, z1]) => [a, b, z0, z1]));
    }
    return out;
  };
  // a chamber cut in the rock at floor Y: its floor, its ceiling (less `holes`: shafts coming down into it), its four
  // walls, with `gaps` -- [side, from, to, height] where a gallery or a shaft leaves it ('n' +z, 's' -z, 'e' +x, 'w' -x)
  const room = (name, Y, x0, x1, z0, z1, h, gaps = [], holes = []) => {
    rect(`${name} floor`, x0, x1, z0, z1, Y - .3, .3, { walked: true }); FLOORS.push(`${name} floor`);
    minus([x0 - T, x1 + T, z0 - T, z1 + T], holes).forEach(([a, b, c, d], i) => { rect(`${name} ceiling ${i}`, a, b, c, d, Y + h, .4); ROCK.push(`${name} ceiling ${i}`); });
    for (const side of "nsew") {
      const along = "ns".includes(side) ? [x0 - T, x1 + T] : [z0, z1];
      const gs = gaps.filter((g) => g[0] === side).sort((a, b) => a[1] - b[1]);
      let pos = along[0], k = 0;
      const wall = (s0, s1, y, hh) => {
        const n = `${name} wall ${side}${k++}`;
        if (side === "n") rect(n, s0, s1, z1, z1 + T, y, hh); if (side === "s") rect(n, s0, s1, z0 - T, z0, y, hh);
        if (side === "e") rect(n, x1, x1 + T, s0, s1, y, hh); if (side === "w") rect(n, x0 - T, x0, s0, s1, y, hh);
        ROCK.push(n);
      };
      for (const [, g0, g1, gh] of [...gs, [side, along[1], along[1], 0]]) {
        if (g0 - pos > 1e-6) wall(pos, g0, Y, h);
        if (g1 > g0 && gh < h) wall(g0, g1, Y + gh, h - gh);   // (the rock over the gap, down to its head)
        pos = Math.max(pos, g1);
      }
    }
  };
  // a gallery along z, its middle line at c, out from the chamber in stretches, each at its own floor (`ys`): a stretch
  // with a lower one after it ends in a flight of steps down to it, under its own roof (the rock over that roof is the
  // stretch's own, as the plan measured it); the door sets every 1.5 m and the plank track along the level rest.
  // -> the door sets' [z, y]
  const gallery = (name, c, along, ys) => {
    const w = GW / 2, sg = Math.sign(along[1] - along[0]), sets = [];
    stretches(along).forEach(([a, b], i) => {
      const y = ys[i], yn = ys[i + 1] ?? y, d = y - yn, nm = `${name} ${i}`;
      const r = (n, lo, hi, s0, s1, yy, h, k) => rect(n, lo, hi, Math.min(s0, s1), Math.max(s0, s1), yy, h, k);
      let lv = b;   // (where the level stretch ends)
      if (d > 1e-3) {
        const n = Math.ceil(d / .2 - 1e-9), run = .28, L = n * run, m = b - sg * L;
        // the flight: its foot on the next stretch's floor at b, climbing back toward the chamber to this one's at m
        parts[`${nm} flight`] = { type: "flight", run, width: GW, base: 0, top: R(d), steps: n, landing: 0, railing: false,
                                  at: pts([[c + sg * w, yn, b, sg > 0 ? PI2 : -PI2]]) };
        r(`${nm} flight floor`, c - w, c + w, m, b, yn - .3, .3, { walked: true }); FLOORS.push(`${nm} flight floor`);
        r(`${nm} rock left low`, c - w - T, c - w, m, b, yn, d + GH + .4); r(`${nm} rock right low`, c + w, c + w + T, m, b, yn, d + GH + .4);
        r(`${nm} rock over low`, c - w - T, c + w + T, m, b, y + GH, .4);
        // (the rock face down from this roof to the next stretch's lower one, over the flight's foot)
        r(`${nm} rock head`, c - w - T, c + w + T, b, b + sg * T, yn + GH + .2, d + .2);
        ROCK.push(`${nm} rock left low`, `${nm} rock right low`, `${nm} rock over low`, `${nm} rock head`);
        lv = m;
      }
      r(`${nm} floor`, c - w, c + w, a, lv, y - .3, .3, { walked: true }); FLOORS.push(`${nm} floor`);
      r(`${nm} rock left`, c - w - T, c - w, a, lv, y, GH + .4); r(`${nm} rock right`, c + w, c + w + T, a, lv, y, GH + .4);
      r(`${nm} rock over`, c - w - T, c + w + T, a, lv, y + GH, .4);
      ROCK.push(`${nm} rock left`, `${nm} rock right`, `${nm} rock over`);
      const len = Math.abs(lv - a), k = Math.max(1, Math.floor(len / 1.5));
      const zs = Array.from({ length: k }, (_, j) => a + (lv - a) * (j + .5) / k);
      if (len > .8) {
        parts[`${nm} set posts`] = { ...box(.14, .14, GH - .16, zs.flatMap((s) => [-1, 1].map((g) => [c + g * (w - .1), y, s]))), when: TIMBERED };
        parts[`${nm} set caps`] = { ...box(GW - .04, .16, .16, zs.map((s) => [c, y + GH - .16, s])), when: TIMBERED };
        r(`${nm} track`, c - .42, c - .3, a, lv, y, .04); r(`${nm} track 2`, c + .3, c + .42, a, lv, y, .04);
        TIMBER.push(`${nm} set posts`, `${nm} set caps`, `${nm} track`, `${nm} track 2`);
        sets.push(...zs.map((s) => [s, y]));
      }
    });
    return sets;
  };

  const HX = 1.0, HZ = .8, FW = 1.1, SW = 2.4, X0 = 6.0, Z0 = -1.2, LD = FW, XL = X0 + 2 * LD + LS;
  let XP = 0, xin = 0;   // (an adit's portal; how far in the ground over it is open)
  const w = GW / 2;
  if (adit) {
    // ---- the surface, an ADIT's: the portal at XP, its apron before it (+x), the adit running in (-x) to the chamber --------
    XP = plan.xp; xin = XP - 3;
    rect("adit floor", 5.8, XP, -w, w, Yb - .3, .3, { walked: true }); FLOORS.push("adit floor");
    const XB = XP - 1.0;   // (the headwall's back: it is 1.5 m thick, the bank's earth against it)
    rect("adit rock left", 6.3, XB, -w - T, -w, Yb, GH + .4); rect("adit rock right", 6.3, XB, w, w + T, Yb, GH + .4);
    rect("adit rock over", 6.3, XB, -w - T, w + T, Yb + GH, .4);
    ROCK.push("adit rock left", "adit rock right", "adit rock over");
    // where the slope over it is still under its roof the ground is open over it (`dig`: the ground's shaders and the
    // walk), from the portal in -- beyond, the hill closes over its rock
    // (until the ground stands .7 m over its roof, and 2 m behind the headwall at the least -- the ground's mesh, its
    //  cells 1.3 m, comes down from the bank to the apron somewhere in there -- and the rock over the roof up to the
    //  ground over all of it: no slot down onto the roof. The headwall's own opening is open too: it has the lintel)
    const top = (cx) => Math.max(...[-w - T, -w, 0, w, w + T].map((cz) => ground(...at0(cx, cz))));
    if (ground) for (xin = XB; xin > 6.3 && Math.min(top(xin - .5), top(xin - 1)) < Yb + GH + .4 + .7; xin -= .5);
    xin = Math.max(6.3, Math.min(xin, XB - 2));
    if (ground) for (let x1 = XB, k = 0; x1 > xin + 1e-6; x1 -= 1, k++) {
      const x0 = Math.max(xin - .5, x1 - 1), h = Math.max(top(x0), top(x1)) + .1 - (Yb + GH + .4);
      if (h > .05) { rect(`adit hood ${k}`, Math.max(6.3, x0), x1, -w - T, w + T, Yb + GH + .4, h); ROCK.push(`adit hood ${k}`); }
    }
    const na = Math.max(1, Math.floor((XP - 6.5) / 1.5)), xs = Array.from({ length: na }, (_, j) => 6.3 + (XP - 6.5) * (j + .5) / na);
    parts["adit set posts"] = { ...box(.14, .14, GH - .16, xs.flatMap((x) => [-1, 1].map((g) => [x, Yb, g * (w - .1)]))), when: TIMBERED };
    parts["adit set caps"] = { ...box(.16, GW - .04, .16, xs.map((x) => [x, Yb + GH - .16, 0])), when: TIMBERED };
    rect("adit track", 5.8, XP, -.42, -.3, Yb, .04); rect("adit track 2", 5.8, XP, .3, .42, Yb, .04);
    TIMBER.push("adit set posts", "adit set caps", "adit track", "adit track 2");
    parts["adit lamps"] = marker("fire", xs.filter((_, i) => i % 4 === 2).map((x) => [x, Yb + 1.75, -w + .03]), { r: .035, h: .09, candle: true });
    // the portal: a headwall of rubble stone round the adit's mouth, its wings, the timber door set in the opening
    rect("adit portal pier 0", XB, XP + .5, -2.6, -w, h0, 3.4); rect("adit portal pier 1", XB, XP + .5, w, 2.6, h0, 3.4);
    rect("adit portal lintel", XB, XP + .5, -w, w, h0 + GH, 3.4 - GH);
    // its wing walls, on in the headwall's line either side, stepping down with the bank they hold (mineBank)
    const B = MINE.ADIT.BANK, bank = (d) => { const t = Math.min(1, d / B.FADE); return B.H * (1 - t * t * (3 - 2 * t)); };
    for (let j = 0; j < 3; j++) for (const g of [-1, 1]) {
      const d0 = 2.6 + 1.2 * j, n = `adit portal wing ${2 * j + (g > 0)}`;
      rect(n, XB, XP + .5, g > 0 ? d0 : -d0 - 1.2, g > 0 ? d0 + 1.2 : -d0, h0, bank(1.2 * j) + .15); STONE.push(n);
    }
    rect("adit portal coping", XB - .1, XP + .6, -2.7, 2.7, h0 + 3.4, .2);
    STONE.push("adit portal pier 0", "adit portal pier 1", "adit portal lintel", "adit portal coping");
    parts["portal posts"] = box(.2, .2, GH, [[XP + .62, h0, -w + .08], [XP + .62, h0, w - .08]]);
    parts["portal cap"] = box(.26, GW + .5, .24, [[XP + .62, h0 + GH, 0]]);
    TIMBER.push("portal posts", "portal cap");
    parts["portal cart"] = { type: "component", use: "components/mine-cart", at: pts([[XP + 1.6, h0, -1.2, PI2]]) };
    parts["hauler"] = marker("spot", [[XP + 2.6, h0, -1.2]], { pose: "stand", work: 1, gesture: "lift", face: PI2, crew: "miner" });
    // the yard before it: the spoil heap, the dressing bench, the pit timber -- each on the ground under it
    const yh = gy(XP + 8.6, -5.0, 3.4), yb = gy(XP + 4.6, 5.0, 1.1), yt = gy(XP + 3.2, -4.8, 1.5);
    parts["spoil heap"] = { type: "column", radius: 3.4, height: R(1.8 + Math.min(1.5, gy(XP + 8.6, -5.0) - yh)), sides: 12, taper: .12, at: pts([[XP + 8.6, yh, -5.0]]) };
    parts["dressing bench"] = box(2.2, .7, .8, [[XP + 4.6, yb, 5.0]]);
    parts["ore pile"] = { type: "column", radius: .7, height: .45, sides: 8, taper: .2, at: pts([[XP + 6.6, gy(XP + 6.6, 5.4, .7), 5.4], [XP + 4.6, yb + .8, 5.0]]) };
    parts["dressers"] = marker("spot", [[XP + 4.6, gy(XP + 4.6, 4.05), 4.05]], { pose: "stand", work: 1, gesture: "tend", face: -PI2 });
    parts["baskets"] = item("items/tools/basket", [[XP + 3.4, gy(XP + 3.4, 4.2, .3), 4.2], [XP + 2.8, gy(XP + 2.8, 5.3, .3), 5.3, .6]], { solid: false });
    parts["sacks"] = item("items/tools/sack-standing", [[XP + 6.0, gy(XP + 6.0, 4.0, .3), 4.0], [XP + 6.4, gy(XP + 6.4, 3.6, .3), 3.6, 1.0]], { solid: false });
    parts["pit timber"] = box(3.0, .16, .16, [0, 1, 2].flatMap((i) => Array.from({ length: 4 - i }, (_, j) => [XP + 3.2, yt + .16 * i, -4.5 - .18 * j])));
    TIMBER.push("dressing bench", "pit timber");
} else {
    for (const [nm, [a, b, c, d]] of Object.entries({ n: [-HX - .2, HX + .2, HZ, HZ + .2], s: [-HX - .2, HX + .2, -HZ - .2, -HZ], e: [HX, HX + .2, -HZ, HZ], w: [-HX - .2, -HX, -HZ, HZ] })) {
      rect(`hauling shaft lining ${nm}`, a, b, c, d, Yb + 3.0, h0 + .9 - (Yb + 3.0)); TIMBER.push(`hauling shaft lining ${nm}`);   // (up through the collar: 0.9 over the ground)
    }
    parts["shaft house"] = { type: "enclosure", plan: { rect: [6.4, 5.2] }, thickness: .12, height: 2.6, at: pts([[0, h0, 0]]), openings: [],
                             faces: { 0: [{ at: 1.4, width: 1.3, sill: 0, springing: 2.0, head: { profile: "flat" }, glass: false }],
                                      2: [{ at: 0, width: .8, sill: 1.0, springing: 1.7, head: { profile: "flat" }, glass: false }] } };
    parts["shaft house roof"] = { type: "roof", form: "gable", width: 5.6, length: 6.9, pitch: 40, overhang: .2, at: pts([[0, h0 + 2.6, 0, PI2]]) };
    // the windlass: two posts beyond the collar, the drum over the shaft, its axle, a crank at each end (one hanging, one
    // standing: the two men's strokes half a turn apart), the grips out from the arms' far ends
    parts["windlass posts"] = box(.18, .18, 1.25, [[0, h0, -1.25], [0, h0, 1.25]]);
    parts["windlass drum"] = box(.28, 2.7, .28, [[0, h0 + .92, 0]]);
    parts["windlass axle"] = box(.08, 2.9, .08, [[0, h0 + 1.02, 0]]);
    parts["windlass cranks"] = box(.06, .06, .4, [[0, h0 + .7, -1.42], [0, h0 + 1.02, 1.42]]);
    parts["windlass handles"] = box(.05, .24, .05, [[0, h0 + .7, -1.55], [0, h0 + 1.37, 1.55]]);
    TIMBER.push("windlass posts", "windlass drum", "windlass axle", "windlass cranks", "windlass handles");
    parts["ropes"] = { type: "column", radius: .014, height: R(h0 + .92 - (Yb + .6)), sides: 5, at: pts([[.3, Yb + .6, 0]]) };
    parts["rope up"] = { type: "column", radius: .014, height: 2.4, sides: 5, at: pts([[-.3, h0 - 1.5, 0]]) };
    parts["kibbles"] = item("items/tools/bucket", [[.3, Yb, 0], [-.3, h0 - 1.9, 0]], { solid: false });
    parts["windlass men"] = marker("spot", [[.2, h0, -1.75], [-.2, h0, 1.75]], { pose: "stand", work: 1, gesture: "lift", face: [PI2, -PI2], crew: "miner" });
    // the walking shaft: inside x 6 .. 10.7, z -1.2 .. 1.2; flights of 10 steps 25 cm on 25 cm, turning on landings at each
    // end (each landing as deep as a flight is wide); an even number of them, so the last lands by the chamber's east wall
    const NF = Math.round((h0 - Yb) / LS);
    for (const [nm, [a, b, c, d, y0]] of Object.entries({ n: [X0 - .2, XL + .2, Z0 + SW, Z0 + SW + .2, Yb], s: [X0 - .2, XL + .2, Z0 - .2, Z0, Yb], e: [XL, XL + .2, Z0, Z0 + SW, Yb], w: [X0 - .2, X0, Z0, Z0 + SW, Yb + 2.3] })) {
      rect(`walking shaft lining ${nm}`, a, b, c, d, y0, h0 - y0 + (nm === "w" ? 0 : .9)); TIMBER.push(`walking shaft lining ${nm}`);
    }
    for (let k = 0; k < NF; k++) {
      const top = h0 - LS * k;
      const at = k % 2 === 0 ? [X0 + LD + LS, top - LS, Z0, PI] : [X0 + LD, top - LS, Z0 + SW, 0];   // (down eastward: climbs west from its foot at the east landing; then back)
      parts[`walking flight ${k}`] = { type: "flight", run: .25, width: FW, base: 0, top: LS, steps: 10, steep: true, landing: 0, at: pts([at]) };
    }
    for (let k = 0; k <= NF; k++) {   // the landings: west at h0, h0 - 5, ...; east between
      const y = h0 - LS * k, x0 = k % 2 === 0 ? X0 : X0 + LD + LS, x0b = k === NF ? X0 - .2 - T : x0;   // (the bottom one through the gap in the chamber's wall)
      rect(`walking landing ${k}`, x0b, x0 + LD, Z0, Z0 + SW, y - .2, .2, { walked: true }); TIMBER.push(`walking landing ${k}`);
    }
    rect("walking shaft bottom", X0 + LD, X0 + LD + LS, Z0, Z0 + SW, Yb - .3, .3, { walked: true }); FLOORS.push("walking shaft bottom");
    parts["walking shaft roof posts"] = box(.14, .14, 2.3, [[X0 - .3, h0, Z0 - .35], [XL + .3, h0, Z0 - .35], [X0 - .3, h0, Z0 + SW + .35], [XL + .3, h0, Z0 + SW + .35]]);
    parts["walking shaft roof"] = { type: "roof", form: "gable", width: 3.8, length: R(XL - X0 + 1.3), pitch: 32, overhang: .1, at: pts([[(X0 + XL) / 2, h0 + 2.3, 0, PI2]]) };
    TIMBER.push("walking shaft roof posts");
    // the spoil heap, the dressing bench, the pit timber -- each on the ground under it
    const yh = gy(-8.0, 4.5, 4.2), yb = gy(-6.5, -5.0, 1.1), yt = gy(4.0, 5.8, 1.5);
    parts["spoil heap"] = { type: "column", radius: 4.2, height: R(2.0 + Math.min(1.5, gy(-8.0, 4.5) - yh)), sides: 12, taper: .12, at: pts([[-8.0, yh, 4.5]]) };
    parts["dressing bench"] = box(2.2, .7, .8, [[-6.5, yb, -5.0]]);
    parts["ore pile"] = { type: "column", radius: .7, height: .45, sides: 8, taper: .2, at: pts([[-4.4, gy(-4.4, -5.4, .7), -5.4], [-6.5, yb + .8, -5.0]]) };
    parts["dressers"] = marker("spot", [[-6.5, gy(-6.5, -4.05), -4.05]], { pose: "stand", work: 1, gesture: "tend", face: PI2 });
    parts["baskets"] = item("items/tools/basket", [[-7.5, gy(-7.5, -4.2, .3), -4.2], [-8.2, gy(-8.2, -5.3, .3), -5.3, .6]], { solid: false });
    parts["sacks"] = item("items/tools/sack-standing", [[-5.0, gy(-5.0, -4.0, .3), -4.0], [-4.6, gy(-4.6, -3.6, .3), -3.6, 1.0]], { solid: false });
    parts["pit timber"] = box(3.0, .16, .16, [0, 1, 2].flatMap((i) => Array.from({ length: 4 - i }, (_, j) => [4.0, yt + .16 * i, 5.5 + .18 * j])));
    TIMBER.push("dressing bench", "pit timber");
  }

  // ---- down below ---------------------------------------------------------------------------------------------------
  // the shaft bottom: x -3 .. 5.8, z -3 .. 3, 3 m high; the hauling shaft comes down through its ceiling, the walking
  // shaft opens from its east wall, the main gallery leaves north, the side gallery south
  // (an adit's chamber: the adit comes in through the east wall, no shaft through the ceiling)
  room("shaft bottom", Yb, -3.0, 5.8, -3.0, 3.0, 3.0, [adit ? ["e", -GW / 2, GW / 2, GH] : ["e", Z0, Z0 + SW, 2.3], ["n", -2.3, -.7, GH], ["s", .7, 2.3, GH]], adit ? [] : [[-HX - .2, HX + .2, -HZ - .2, HZ + .2]]);
  parts["hooker"] = marker("spot", [[1.2, Yb, 0]], { pose: "stand", work: 1, gesture: "lift", face: PI, crew: "miner" });
  parts["shaft bottom lamps"] = marker("fire", [[-2.9, Yb + 1.9, -1.5], [5.7, Yb + 1.9, 2.0]], { r: .035, h: .09, candle: true });
  parts["shaft bottom cart"] = { type: "component", use: "components/mine-cart", at: pts([[-1.5, Yb, 1.8]]) };
  const s1 = gallery("main gallery", GALLERIES.main.c, MINE.MAIN, plan.main), s2 = gallery("side gallery", GALLERIES.side.c, MINE.SIDE, plan.side);
  const YN = plan.main.at(-1), YS = plan.side.at(-1);   // (the stopes: where the galleries arrive)
  room("north stope", YN, ...GALLERIES.main.stope, [["s", -2.3, -.7, GH]]);
  room("south stope", YS, ...GALLERIES.side.stope, [["n", .7, 2.3, GH]]);
  // the veins: bands in the stopes' far walls and down their sides, a little proud of the rock; the ore broken out
  parts["vein north"] = box(6.6, .04, 1.3, [[-1.5, YN + .7, 35.98]]);
  parts["vein north side"] = box(.04, 4.0, .9, [[1.98, YN + 1.1, 33.5], [-4.98, YN + .9, 33.0]]);
  parts["vein south"] = box(6.6, .04, 1.1, [[1.5, YS + 1.0, -25.98]]);
  parts["vein south side"] = box(.04, 3.5, .8, [[4.98, YS + .8, -23.5]]);
  parts["broken ore"] = { type: "column", radius: .55, height: .35, sides: 7, taper: .25, at: pts([[.6, YN, 35.0], [-3.6, YN, 34.6], [3.4, YS, -25.0]]) };
  VEINS.push("vein north", "vein north side", "vein south", "vein south side", "broken ore");
  parts["miners north"] = marker("spot", [[-2.6, YN, 35.2], [0, YN, 35.25], [1.3, YN, 33.0]],
                                 { pose: "stand", work: 1, gesture: ["pick", "hammer", "pick"], tool: ["items/tools/pickaxe", "items/tools/hammer", "items/tools/pickaxe"], face: [-PI2, -PI2, 0], crew: "miner" });
  parts["miners south"] = marker("spot", [[.5, YS, -25.2], [4.2, YS, -23.0]],
                                 { pose: "stand", work: 1, gesture: ["hammer", "pick"], tool: ["items/tools/hammer", "items/tools/pickaxe"], face: [PI2, 0], crew: "miner" });
  parts["loader"] = marker("spot", [[-.9, YN, 32.4]], { pose: "stand", work: 1, gesture: "dig", tool: "items/tools/spade", face: -PI2, crew: "miner" });
  // the carts: one by the north face, one on each gallery's longest level run
  const mid = (sets) => sets[Math.floor(sets.length / 2)] ?? [0, Yb];
  const [cm, cs] = [mid(s1), mid(s2)];
  parts["carts"] = { type: "component", use: "components/mine-cart", at: pts([[-1.5, YN, 31.4], [-1.5, cm[1], cm[0]], [1.5, cs[1], cs[0]]]) };
  parts["gallery lamps"] = marker("fire", [...s1.filter((_, i) => i % 4 === 0).map(([z, y]) => [-2.27, y + 1.75, z]), ...s2.filter((_, i) => i % 4 === 0).map(([z, y]) => [.77, y + 1.75, z]),
                                           [-4.9, YN + 2.0, 32.0], [1.9, YN + 2.0, 34.5], [-1.9, YS + 2.0, -21.0], [4.9, YS + 2.0, -24.5]], { r: .035, h: .09, candle: true });
  parts["lanterns"] = item("items/tools/lantern", [[-4.5, YN, 31.0], [4.4, YS, -21.0]], { solid: false });

  // ---- into the site's frame: the yard's middle the origin, turned `dir` quarter turns ----------------------------------
  for (const p of Object.values(parts)) p.at = p.at.map(([x, y, z, a]) => { const [u, v] = TT.f(x, z); return [R(u), y, R(v), R(a + TT.a)]; });
  const dig = (adit ? [[xin, XP + .3, -w, w]] : [[-HX, HX, -HZ, HZ], [X0, XL, Z0, Z0 + SW]]).map((r) => { const [a, b, c, d] = turnRect(TT, r); return [R(a), R(c), R(b), R(d)]; });   // (the shafts' mouths, the adit's mouth: the ground open over them)
  const [fx0, fx1, fz0, fz1] = turnRect(TT, plan.yard ?? MINE.YARD);
  const doc = { name: "Mine",
    _about: "A MINE of the Middle Ages (silver, copper or salt: `ore`): on the surface the shaft house over the hauling shaft with its windlass and kibbles, the walking shaft with its steep flights under a little roof, the spoil heap, the dressing bench, pit timber; ten metres down (or deeper, where the land over the galleries falls away: the game lays it into its hills -- mine.js) the shaft bottom, timbered galleries with a plank track and wooden carts, stepping down where they must, and the stopes where miners work the vein with pick and hammer by the light of their lamps. The ground is open only over the shafts; only the shaft head needs level ground.",
    _generator: "mine.js mineDoc (tools/archgen/mine.mjs writes this catalogue copy, on level ground)",
    site: { origin: true, ...(dig.length ? { dig } : {}) },
    params: { detail: 4, ore, footW: R(fx1 - fx0), footD: R(fz1 - fz0),
              _ore: "silver | copper | salt: the rock and the vein (the finishes mine-<ore>), and whether the galleries are timbered (salt stands without)" },
    parts, build: Object.keys(parts), walked: true };
  return { doc, names: { ROCK, TIMBER, FLOORS, VEINS, STONE } };
}

// THE ENTRANCE'S FLAT SPOT for a plan, in the world: a ground.js flat zone settled to h0 (`fade`: back to the land over
// that many metres -- a hillside keeps its shape)
export function mineFlat(plan, fade = plan.kind === "adit" ? 3 : 8) {
  const T = turn(plan.dir, plan.yc ?? YC), [a, b, c, d] = turnRect(T, plan.flat ?? MINE.FLAT);
  return { x: plan.x + (a + b) / 2, z: plan.z + (c + d) / 2, hx: (b - a) / 2 + .6, hz: (d - c) / 2 + .6, y: plan.h0, fade };
}

// AN ADIT'S BANK, in the world: a ground.js zone with `raise` -- the earth behind its headwall heaped up to the
// headwall's top (`ADIT.BANK.H` over the floor) and back into the hillside, falling away to the land either side over
// `FADE` m, cut sheer inside the headwall (`cut`: 1.4 m behind its face -- the ground's mesh cells are 1.3 m): the portal is set into the hill, not stood in front of it. From
// the headwall in until the land itself stands that high (`ground`: the world's). null for a shaft
export function mineBank(plan, ground) {
  if (plan.kind !== "adit") return null;
  const B = MINE.ADIT.BANK, XP = plan.xp, T = turn(plan.dir, plan.yc), W = (cx, cz) => { const [u, v] = T.f(cx, cz); return [plan.x + u, plan.z + v]; };
  let L = 2;
  while (L < MINE.ADIT.PCMAX && Math.min(...[-2.6, 0, 2.6].map((cz) => ground(...W(XP - L, cz)))) < plan.h0 + B.H) L++;
  const [a, b, c, d] = turnRect(T, [XP - L, XP - .9, -2.6, 2.6]);
  const a0 = plan.dir * PI2, n = [Math.round(Math.cos(a0)), -Math.round(Math.sin(a0))];
  return { x: plan.x + (a + b) / 2, z: plan.z + (c + d) / 2, hx: (b - a) / 2, hz: (d - c) / 2, y: plan.h0 + B.H, fade: B.FADE,
           raise: true, cut: [n[0], n[1], (L - .9) / 2] };   // (sheer inside the headwall, 0.1 m behind its back face)
}

// WHERE IT GOES: the best of a grid of sites and every quarter turn. `ground` groundH, `wet` waterSD, `busy(x0, z0, x1, z1)`
// a rectangle taken, `R` how far out, `near` [x, z] the village. The kind is the SITE'S: where the land rises steeply
// behind the spot (`ADIT.SLOPE`: 2.4 m within 8 m) an adit is driven in, on level ground or a hilltop a shaft sunk. The yard must
// be dry and free and the entrance's flat spot near level; the galleries may run under anything (they keep their COVER:
// deeper where they must). The higher the better (mines are in the hills), an adit (a hillside) better still, the
// galleries going down better than level, not too far from the village, little cut, shallow shafts.
// -> the plan, with `score` and `why` (the counts of what was turned down); null if nothing fits
export function placeMine({ ground, wet, busy, R: RR, near = [0, 0], step = 8 }) {
  const why = { far: 0, busy: 0, wet: 0, steep: 0, deep: 0, hill: 0 }, cands = [], A = MINE.ADIT;
  const free = (dir, gx, gz, yard, yc) => { const [a, b, c, d] = turnRect(turn(dir, yc), yard);
    if (busy(gx + a - 4, gz + c - 4, gx + b + 4, gz + d + 4)) { why.busy++; return false; }
    for (let x = a - 4; x <= b + 4; x += 4) for (let z = c - 4; z <= d + 4; z += 4) if (wet(gx + x, gz + z) < 8) { why.wet++; return false; }
    return true; };
  for (let gx = -RR; gx <= RR; gx += step) for (let gz = -RR; gz <= RR; gz += step) {
    if (Math.hypot(gx, gz) > RR) { why.far++; continue; }
    const dist = Math.hypot(gx - near[0], gz - near[1]), g0 = ground(gx, gz);
    for (let dir = 0; dir < 4; dir++) {
      // (the land 8 m into the hill this way: an adit's site -- the portal at gx gz)
      const [u, v] = turn(dir, [0, 0]).f(-8, 0), rise = ground(gx + u, gz + v) - g0;
      if (rise >= 8 * A.SLOPE) { cands.push({ kind: "adit", x: gx, z: gz, dir, s: .5 * g0 - .02 * dist }); continue; }
      const T = turn(dir), [f0, f1, f2, f3] = turnRect(T, MINE.FLAT);
      let lo = 1e9, hi = -1e9;
      for (let x = f0; x <= f1 + 1e-6; x += (f1 - f0) / 4) for (let z = f2; z <= f3 + 1e-6; z += (f3 - f2) / 2) { const g = ground(gx + x, gz + z); lo = Math.min(lo, g); hi = Math.max(hi, g); }
      if (hi - lo > 4) { why.steep++; continue; }
      cands.push({ kind: "shaft", x: gx, z: gz, dir, s: .5 * (lo + hi) / 2 - .02 * dist - 1.5 * (hi - lo) });
    }
  }
  // (the best few of each kind planned in full: 40 shafts, 40 adits)
  cands.sort((p, q) => q.s - p.s);
  let best = null;
  const n = { shaft: 0, adit: 0 };
  for (const c of cands) {
    if (n[c.kind] >= 40) continue;
    const p = minePlan(ground, c.x, c.z, c.dir, c.kind);
    if (p.bad) { why.hill++; continue; }
    if (!free(c.dir, p.x, p.z, p.yard, p.yc)) continue;
    n[c.kind]++;
    const descent = p.Yb - Math.min(p.main.at(-1), p.side.at(-1));
    if (p.depth > 30 || descent > 12 || (p.kind === "adit" && p.range > 2.5)) { why.deep++; continue; }
    p.score = .5 * p.h0 - .02 * Math.hypot(p.x - near[0], p.z - near[1]) - 1.5 * p.range - .15 * Math.max(0, p.depth - 10) + .15 * descent + (p.kind === "adit" ? 10 : 0);
    if (!best || p.score > best.score) best = p;
  }
  return best ? { ...best, why } : (console.info("mine: nowhere fits", JSON.stringify(why)), null);
}

// THE ROCK OVER IT, measured (a check: index.html window.__mine.cover()): for the shaft bottom, every stretch of the
// galleries and the stopes, its floor, its head, the lowest ground over it (`ground`: the world's, finished) and the
// rock between -- `cover` never under COVER where the land was read right
export function mineCover(plan, ground) {
  const T = turn(plan.dir, plan.yc ?? YC), { GH, GW, T: RT } = MINE, out = [];
  const over = (x0, x1, z0, z1) => { let m = 1e9;
    for (let cx = x0; cx <= x1 + 1e-6; cx += (x1 - x0) / 4) for (let cz = Math.min(z0, z1); cz <= Math.max(z0, z1) + 1e-6; cz += Math.abs(z1 - z0) / 6) {
      const [u, v] = T.f(cx, cz); m = Math.min(m, ground(plan.x + u, plan.z + v));
    }
    return m; };
  const add = (what, y, h, g) => out.push({ what, floor: R(y), head: R(y + h), ground: R(g), cover: R(g - y - h) });
  add("shaft bottom", plan.Yb, 3.0, over(-3.0 - RT, 5.8 + RT, -3.0 - RT, 3.0 + RT));
  // (an adit: past its passage, every 3 m -- its head under the ground, RISE - GH at the least)
  if (plan.kind === "adit") for (let x1 = plan.xp - plan.pc; x1 > 6.3 + 1e-6; x1 -= 3) add(`adit ${R(plan.xp - x1)} m in`, plan.Yb, GH, over(Math.max(6.3, x1 - 3), x1, -GW / 2 - RT, GW / 2 + RT));
  for (const [k, G] of Object.entries(GALLERIES)) {
    stretches(G.along).forEach(([a, b], i) => add(`${k} gallery ${i}`, plan[k][i], GH, over(G.c - GW / 2 - RT, G.c + GW / 2 + RT, a, b)));
    const [sx0, sx1, sz0, sz1, sh] = G.stope;
    add(`${k} stope`, plan[k].at(-1), sh, over(sx0 - RT, sx1 + RT, sz0 - RT, sz1 + RT));
  }
  return out;
}
