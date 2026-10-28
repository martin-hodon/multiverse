// THE TIERED TOWER (a `tiered` part): storeys stacked one on another, each smaller than the one below, a SKIRT ROOF round
// the foot of every storey (the pent: from its eave up to the wall of the storey above) and the top under its own roof --
// a Japanese keep (tenshu) and its turrets (yagura), a pagoda, a Korean gate tower. What is designed is the storeys'
// plans and heights and the roofs' manner; the walls, windows, floors, stairs, skirts, crowning roof and the gables set
// on the skirts follow from them, written as the engine's own parts (enclosures, prisms, flights, roofs).
//   STOREYS: `storeys` [{ w, l, h }, ...] from the ground up -- w along x, l along z, all centred on one axis -- each
//     storey may say `roof: false` (no skirt over it: a floor hidden under the roof of the one below, as a keep's fifth
//     floor is) and `windows`, its own openings spec.
//   WALLS `wall` { t }: `windows` is every face's openings (best a row that fits: `every`), kept clear of the skirt
//     below; `door` { side, at, width, height } in the ground storey (or a list: a passage through) -- a side is "n"
//     (-z), "s" (+z), "e" (+x), "w" (-x), `at` the door's x on a north or south side, its z on an east or west one.
//   SKIRTS `roof` { pitch, overhang, lo, hi, upturn, flare }: the pent form, curved as curvedRoof bends it.
//   THE TOP `top` { form, pitch, overhang, hipH, ... }: over the last storey -- a hip-and-gable (gablet: the irimoya) by
//     default, its ridge along the longer side.
//   GABLES on a skirt or the top roof: a storey's `gables` [{ side, kind, width, at, pitch }] -- "chidori" (a triangular
//     gable sitting on the slope, its back running into the roof above), "irimoya" (the same, larger and lower: it meets
//     the next roof), "kara" (the cusped gable, breaking the eave) -- `at` metres along the side from its middle.
//   BRACKETS `brackets` { use, s, every }: bracket sets (components/dougong) in a row under every eave.
//   THE FINIAL `finial` { height, radius, rings, base } on the apex of a square top: a pagoda's sorin.
//   INSIDE: `floors` (true by default) -- a floor on every storey and a steep stair (the ladder-like flights of a keep)
//     up to each from the one below, along the longer side against alternate long walls, inside the footprint of the
//     storey above, its floor open over it.
//   POLYGONAL STOREYS `sides` n: a Chinese pavilion tower (the Foxiang Ge), an octagonal pagoda -- each storey { r, h }
//     a regular n-gon r to its outer corners (a face on each axis's side: planPoints' `sides` plan), every skirt and the
//     top a `dome` of n faces on the jujia section (`roof` { lo, hi, overhang, t }: the slopes at the eave and at the
//     crown, profiles.js), each SEATED on the wall it covers (assemble.js seatLift: its soffit on the wall head), the
//     skirts cut by an oculus where the storey above rises through them; a door's `side` the face toward it; the
//     brackets along every face; the finial on the top's point. No gables.
import { roofLevels, overhang, restLift, planPoints } from "./build.js";

const SIDES = { n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] };

export function tieredDefs(def, P) {
  if (def.sides !== undefined) return polygonDefs(def, P);
  const S = def.storeys.map((s) => ({ ...s, w: P(s.w), l: P(s.l), h: P(s.h) }));
  if (!S.length) throw new Error("a tiered tower needs a storey");
  const t = P(def.wall?.t, .5), R = def.roof ?? {}, pitch = P(R.pitch, 30), T = Math.tan(pitch * Math.PI / 180), o = P(R.overhang, 1.8);
  const curve = Object.fromEntries(["lo", "hi", "upturn", "flare", "reach", "perSide"].filter((k) => R[k] !== undefined).map((k) => [k, P(R[k])]));
  const floors = def.floors !== false, defs = {};
  // (a curved roof rests on its wall: lifted by its sag over the wall line -- build.js restLift -- and the windows above a
  //  skirt kept clear of it by as much)
  const skirtLift = (k) => {
    const s = S[k], up = S[k + 1], lv0 = roofLevels("pent", { a: s.w / 2, b: s.l / 2, top: [up.w, up.l], pitch });
    return restLift(overhang(lv0, o), lv0[0].y, curve.lo ?? 1, curve.hi ?? 1);
  };
  const ys = S.reduce((a, s) => [...a, a[a.length - 1] + s.h], [0]);    // each storey's foot, and the top
  S.forEach((s, k) => {
    const up = S[k + 1];
    if (up && (up.w > s.w + 1e-6 || up.l > s.l + 1e-6)) throw new Error(`storey ${k + 2} is wider than storey ${k + 1} under it`);
  });
  // (the skirt under storey k reaches this high up its wall: the windows' sills stand clear of it)
  const skirtRise = (k) => k > 0 && S[k - 1].roof !== false ? Math.max(S[k - 1].w - S[k].w, S[k - 1].l - S[k].l) / 2 * T + skirtLift(k - 1) : 0;
  // (planPoints walks a rect round from its south-west corner, east along the south side: face 0 the south (+z) side,
  //  1 the east, 2 the north, 3 the west -- and an opening's `at` runs the way its face does, so a door's, given as a
  //  plain x (on the south or north side) or z (on the east or west), is turned to it)
  const FACE = { s: [0, 1], e: [1, -1], n: [2, -1], w: [3, 1] };
  const doors = [].concat(def.door ?? def.doors ?? []);
  // THE BRACKET SETS' SEAT on storey k, over its foot (null: none on it) -- the windows' heads are kept under it
  const B = def.brackets, Tp = def.top ?? {}, Ttop = Math.tan(P(Tp.pitch, pitch + 6) * Math.PI / 180);
  const bsc = B ? P(B.s, .6) : 0, bh = B ? P(B.height, 1.06) * bsc : 0, breach = B ? P(B.reach, 1.3) * bsc : 0;
  const seat = (k) => {
    const last = k === S.length - 1;
    if (!B || (!last && S[k].roof === false)) return null;
    // (a curved slope sags under its straight pitch line toward the eave: twice the drop keeps the tips under it)
    return S[k].h - bh - 2 * breach * (last ? Ttop : T) - .05;
  };
  S.forEach((s, k) => {
    const y = ys[k], sill = Math.max(0, skirtRise(k) + .35);
    const win = s.windows ?? def.windows ?? { every: 2.2, width: .8, end: 1.0, sill: 1.0, springing: 1.9, head: { profile: "flat" } };
    let spring = Math.max(P(win.springing ?? 1.9), sill + 0.8);
    if (win !== false && seat(k) !== null) {   // (a head that is not flat rises over its springing: by its width at the most)
      const cap = seat(k) - .1 - ((win.head?.profile ?? "flat") === "flat" ? 0 : P(win.width ?? .8));
      if (cap < Math.max(P(win.sill ?? 1), sill) + .5) throw new Error(`storey ${k + 1}: no room for windows between the skirt below and the bracket sets (${cap.toFixed(2)}m)`);
      spring = Math.min(spring, cap);
    }
    const spec = win === false ? [] : { ...win, sill: Math.max(P(win.sill ?? 1), sill), springing: spring };
    const faces = {};
    if (k === 0) for (const d of doors) {
      const [f, sgn] = FACE[d.side ?? "s"], door = { at: sgn * P(d.at, 0), width: P(d.width, 1.6), sill: 0, springing: P(d.height, 2.4), head: { profile: "flat" } };
      if (seat(0) !== null && door.springing > seat(0) - .1) throw new Error(`a door ${door.springing}m high runs into the bracket sets over it (${(seat(0) - .1).toFixed(2)}m at the most)`);
      const was = faces[f] ?? (!Array.isArray(spec) && spec.every !== undefined ? { ...spec, with: [] } : []);
      faces[f] = Array.isArray(was) ? [...was, door] : { ...was, with: [...was.with, door] };
    }
    defs[`storey ${k + 1}`] = { type: "enclosure", plan: { rect: [s.w, s.l] }, thickness: t, height: s.h, glass: false, openings: spec, faces, at: [[0, y, 0, 0]],
                                interior: def.interior ?? true };   // (its rooms: an interior, storey by storey)
    // THE SKIRT over it, up to the storey above
    const up = S[k + 1];
    if (up && s.roof !== false) {
      if (up.w > s.w - .05 || up.l > s.l - .05) throw new Error(`storey ${k + 2} must be set in from storey ${k + 1} for a skirt between them`);
      defs[`skirt ${k + 1}`] = { type: "roof", form: "pent", width: s.w, length: s.l, top: [up.w, up.l], pitch, overhang: o, ...curve, rest: true, at: [[0, y + s.h, 0, 0]] };
    }
    // FLOORS and the stair up to each: in the storey below, climbing along its longer side against one of the long walls
    // (alternately, storey by storey), centred, inside this one's footprint; the floor open over its whole run
    if (floors && k > 0) {
      const lo = S[k - 1], h = lo.h, A = Math.min(s.w, lo.w), B = Math.min(s.l, lo.l), alongX = A >= B;
      const [long, across] = alongX ? [A, B] : [B, A];
      const n = Math.ceil(h / .28), rise = h / n, run = Math.max(.22, Math.min(.3, (long - 2 * t - 3.2) / n));
      const L = n * run, fw = .9, side = k % 2 ? 1 : -1;
      const c = side * (across / 2 - t - .15 - fw / 2), a0 = -L / 2 - .6;
      // (it arrives on this floor beyond the well, no landing of its own; a flight lies over local z -width .. 0, so
      //  climbing +x (yaw 0) it spans z c - fw/2 .. c + fw/2 placed at z c + fw/2, climbing +z (yaw -90deg) at x c - fw/2)
      defs[`stair ${k}`] = { type: "flight", width: fw, run, rise, base: 0, top: h, steep: true, landing: 0,
                             at: [alongX ? [a0, y - h, c + fw / 2, 0] : [c - fw / 2, y - h, a0, -Math.PI / 2]] };
      const well = alongX ? { rect: [L + .1, fw + .1], at: [a0 + L / 2, c] } : { rect: [fw + .1, L + .1], at: [c, a0 + L / 2] };
      defs[`floor ${k + 1}`] = { type: "prism", plan: { rect: [s.w - 2 * t + .02, s.l - 2 * t + .02], well }, height: .3, walked: true, at: [[0, y - .3, 0, 0]] };
    }
  });
  // THE TOP ROOF, its ridge along the longer side
  const top = S[S.length - 1], long = top.w >= top.l;
  const yTop = ys[S.length];
  defs.top = { type: "roof", form: Tp.form ?? "gablet", width: long ? top.l : top.w, length: long ? top.w : top.l, pitch: P(Tp.pitch, pitch + 6),
               overhang: P(Tp.overhang, o), ...(Tp.hipH !== undefined ? { hipH: P(Tp.hipH) } : (Tp.form ?? "gablet") === "gablet" ? { hipH: .55 } : {}),
               ...curve, ...Object.fromEntries(["lo", "hi", "upturn", "flare"].filter((k) => Tp[k] !== undefined).map((k) => [k, P(Tp[k])])),
               rest: true, at: [[0, yTop, 0, long ? Math.PI / 2 : 0]] };
  // THE BRACKET SETS under every eave (`brackets` { use, s, every }: a component built facing +z out of the wall, y 0 on
  // its seat -- components/dougong by default, about 1.06m tall and 1.3m out at s 1): a row along each side of every
  // storey that has a roof over it, corner to corner, set low enough that the slope clears its outer tip
  if (B) {
    const ev = P(B.every, 1.8);
    S.forEach((s, k) => {
      if (seat(k) === null) return;
      const y = ys[k] + seat(k), at = [];
      for (const [side, [nx, nz]] of Object.entries(SIDES)) {
        const len = nx ? s.l : s.w, d = nx ? s.w / 2 : s.l / 2, m = Math.max(2, Math.round((len - .8) / ev) + 1);
        const yaw = { s: 0, n: Math.PI, e: Math.PI / 2, w: -Math.PI / 2 }[side];
        for (let j = 0; j < m; j++) {
          const u = -(len / 2 - .4) + j * (len - .8) / (m - 1);
          at.push(nx ? [nx * d, y, u, yaw] : [u, y, nz * d, yaw]);
        }
      }
      defs[`brackets ${k + 1}`] = { type: "component", use: B.use ?? "components/dougong", params: { s: bsc, ...(B.params ?? {}) }, at };
    });
  }
  // THE FINIAL on the top roof's apex (a pyramid's: a square top storey under a hip): the pagoda's sorin -- a square
  // base, the mast, its `rings` (the nine of a kurin) and the jewel at the top
  if (def.finial) {
    const F = def.finial, h = P(F.height, 6), r = P(F.radius, .18), nr = Math.round(P(F.rings, 9));
    const yA = yTop + Math.min(top.w, top.l) / 2 * Math.tan(P(Tp.pitch, pitch + 6) * Math.PI / 180), b = P(F.base, 1.2);
    defs["finial base"] = { type: "prism", plan: { rect: [b, b] }, height: b * .7, at: [[0, yA - b * .4, 0, 0]] };
    defs["finial mast"] = { type: "prism", plan: { sides: 8, radius: r }, height: h, at: [[0, yA + b * .3, 0, 0]] };
    const y0 = yA + b * .3 + h * .25, dy = h * .55 / nr;
    if (nr > 0) defs["finial rings"] = { type: "prism", plan: { sides: 16, radius: r * 3.2 }, height: .1, at: Array.from({ length: nr }, (_, j) => [0, y0 + j * dy, 0, 0]) };
    defs["finial jewel"] = { type: "prism", plan: { sides: 8, radius: r * 1.8 }, height: r * 3.5, at: [[0, yA + b * .3 + h, 0, 0]] };
  }
  // THE GABLES on each storey's skirt (or, on the last storey, its top roof)
  S.forEach((s, k) => (s.gables ?? []).forEach((g, j) => {
    const side = g.side ?? "s", [nx, nz] = SIDES[side], along = nx !== 0;          // (along x: an east or west side)
    const half = along ? s.w / 2 : s.l / 2, kind = g.kind ?? "chidori", wg = P(g.width, 4), pg = P(g.pitch, 45);
    const isTop = k === S.length - 1, y0 = ys[k] + s.h;
    // the slope on that side: its eave (out and down by the overhang) and where it meets the wall above
    const pt = isTop ? P(Tp.pitch, pitch + 6) : pitch, Tt = Math.tan(pt * Math.PI / 180), oo = isTop ? P(Tp.overhang, o) : o;
    const upHalf = isTop ? 0 : (along ? S[k + 1].w : S[k + 1].l) / 2;
    const run = half - upHalf, rise = isTop ? half * Tt : run * T;
    const sl = run > 1e-6 ? rise / run : Tt, yE = y0 - oo * (isTop ? Tt : T), dE = half + (y0 - yE) / sl;
    let d0, d1, yb;
    if (kind === "kara") { d0 = dE + .2; d1 = half - .1; yb = yE + .05; }
    else {
      const f = kind === "irimoya" ? .12 : .35, dTop = isTop ? half * .4 : upHalf;
      d0 = dE + (dTop - dE) * f; d1 = dTop - .3; yb = yE + (y0 + rise - yE) * f - .25;
    }
    const L = d0 - d1, c = (d0 + d1) / 2, u = P(g.at, 0);
    const pos = along ? [nx * c, nz * c + u] : [nx * c + u, nz * c];
    // (a roof's ridge runs along its local z: square to this side -- along x on an east or west side)
    defs[`gable ${k + 1}.${j + 1}`] = { type: "roof", form: kind === "kara" ? "kara" : "gable", width: wg, length: L, pitch: pg, overhang: .3,
                                         at: [[pos[0], yb, pos[1], along ? Math.PI / 2 : 0]] };
  }));
  return defs;
}

// THE POLYGONAL TOWER (`sides`): the same storeys, skirts, brackets, floors and finial, on n-gon plans under jujia roofs
function polygonDefs(def, P) {
  const n = Math.round(P(def.sides)), cn = Math.cos(Math.PI / n);
  if (!(n >= 3)) throw new Error("a polygonal tiered tower needs 3 sides or more");
  const S = def.storeys.map((s) => ({ ...s, r: P(s.r), h: P(s.h) }));
  if (!S.length) throw new Error("a tiered tower needs a storey");
  S.forEach((s, k) => { if (S[k + 1] && S[k + 1].r > s.r + 1e-6) throw new Error(`storey ${k + 2} is wider than storey ${k + 1} under it`); });
  const t = P(def.wall?.t, .5), R = def.roof ?? {}, Tp = { ...R, ...(def.top ?? {}) }, floors = def.floors !== false, defs = {};
  const ys = S.reduce((a, s) => [...a, a[a.length - 1] + s.h], [0]);
  // a roof's numbers: its eave's corner radius (the overhang square to the faces), its section, its thickness
  const roofOf = (r, Q) => {
    const o = P(Q.overhang, 1.8), lo = P(Q.lo, .35), hi = P(Q.hi, 1.1), rt = P(Q.t, .3);
    const a = r + o / cn, J = (d) => lo * d + (hi - lo) * d * d / (2 * a);   // (the section's height d in from the eave)
    // (seated: the soffit -- the section drawn rt further in -- on the wall's corner 2 cm under its head)
    const foot = -.02 - J(a - r - rt);
    return { a, lo, hi, rt, J, foot, slope: (d) => lo + (hi - lo) * d / a };
  };
  const roofs = S.map((s, k) => (k < S.length - 1 ? (s.roof !== false ? roofOf(s.r, R) : null) : roofOf(s.r, Tp)));
  // (the skirt under storey k reaches this high up its wall, over its foot: the windows' sills stand clear of it)
  const skirtRise = (k) => { const q = k > 0 && roofs[k - 1]; return q ? q.foot + q.J(q.a - S[k].r) + q.rt : 0; };
  // THE BRACKET SETS' SEAT on storey k, over its foot (as the square tower's, the tips kept under the slope)
  const B = def.brackets, bsc = B ? P(B.s, .6) : 0, bh = B ? P(B.height, 1.06) * bsc : 0, breach = B ? P(B.reach, 1.3) * bsc : 0;
  const seat = (k) => {
    const q = roofs[k];
    if (!B || !q) return null;
    return S[k].h + q.foot + q.J(q.a - S[k].r) - q.J(q.a - S[k].r - breach) - bh - breach * q.slope(q.a - S[k].r) - .05;
  };
  // (the face toward a door's side: planPoints' edges, the outside on their right -- face i from corner i to i + 1)
  const pts = planPoints({ sides: n, radius: 1 });
  const faceOf = (side) => {
    const [dx, dz] = SIDES[side];
    let best = 0, bd = -2;
    for (let i = 0; i < n; i++) {
      const [x0, z0] = pts[i], [x1, z1] = pts[(i + 1) % n], d = ((x0 + x1) * dx + (z0 + z1) * dz) / 2;
      if (d > bd) { bd = d; best = i; }
    }
    return best;
  };
  const doors = [].concat(def.door ?? def.doors ?? []);
  S.forEach((s, k) => {
    const y = ys[k], sill = Math.max(0, skirtRise(k) + .35);
    const win = s.windows ?? def.windows ?? false;
    let spec = [];
    if (win !== false) {
      let spring = Math.max(P(win.springing ?? 1.9), sill + .8);
      if (seat(k) !== null) spring = Math.min(spring, seat(k) - .1 - ((win.head?.profile ?? "flat") === "flat" ? 0 : P(win.width ?? .8)));
      if (spring < Math.max(P(win.sill ?? 1), sill) + .5) throw new Error(`storey ${k + 1}: no room for windows between the skirt below and the bracket sets`);
      spec = { ...win, sill: Math.max(P(win.sill ?? 1), sill), springing: spring };
    }
    const faces = {};
    if (k === 0) for (const d of doors) {
      const f = faceOf(d.side ?? "s"), door = { at: P(d.at, 0), width: P(d.width, 1.6), sill: 0, springing: P(d.height, 2.4), head: { profile: "flat" } };
      if (seat(0) !== null && door.springing > seat(0) - .1) throw new Error(`a door ${door.springing}m high runs into the bracket sets over it`);
      const was = faces[f] ?? (!Array.isArray(spec) && spec.every !== undefined ? { ...spec, with: [] } : []);
      faces[f] = Array.isArray(was) ? [...was, door] : { ...was, with: [...was.with, door] };
    }
    defs[`storey ${k + 1}`] = { type: "enclosure", plan: { sides: n, radius: s.r }, thickness: t, height: s.h, glass: false, openings: spec, faces, at: [[0, y, 0, 0]],
                                interior: def.interior ?? true };
    // THE SKIRT over it (the top over the last): a dome of n faces on the jujia section, seated on this storey's wall
    // (placed at 0: the seat lifts it from there to the wall's head, wherever the wall stands)
    const q = roofs[k], up = S[k + 1];
    if (q) {
      if (up && up.r > s.r - .05) throw new Error(`storey ${k + 2} must be set in from storey ${k + 1} for a skirt between them`);
      defs[up ? `skirt ${k + 1}` : "top"] = { type: "dome", radius: q.a, sides: n, thickness: q.rt, head: { profile: "jujia", lo: q.lo, hi: q.hi },
                                              ...(up ? { oculus: up.r - t / 2 } : {}), seat: `storey ${k + 1}`, at: [[0, 0, 0, 0]] };
    }
    // FLOORS and the stairs up to them: as the square tower's, in the square inside each n-gon's inscribed circle
    if (floors && k > 0) {
      const lo = S[k - 1], h = lo.h, A = Math.SQRT2 * Math.min(s.r, lo.r) * cn;
      const m = Math.ceil(h / .28), rise = h / m, run = Math.max(.22, Math.min(.3, (A - 2 * t - 3.2) / m));
      const L = m * run, fw = .9, side = k % 2 ? 1 : -1, c = side * (A / 2 - t - .15 - fw / 2), a0 = -L / 2 - .6;
      defs[`stair ${k}`] = { type: "flight", width: fw, run, rise, base: 0, top: h, steep: true, landing: 0, at: [[a0, y - h, c + fw / 2, 0]] };
      defs[`floor ${k + 1}`] = { type: "prism", plan: { sides: n, radius: s.r - t / cn + .02, well: { rect: [L + .1, fw + .1], at: [a0 + L / 2, c] } },
                                 height: .3, walked: true, at: [[0, y - .3, 0, 0]] };
    }
  });
  // THE BRACKET SETS along every face of every storey with a roof over it, built facing out of the face
  if (B) {
    const ev = P(B.every, 1.8);
    S.forEach((s, k) => {
      if (seat(k) === null) return;
      const y = ys[k] + seat(k), ap = s.r * cn, len = 2 * s.r * Math.sin(Math.PI / n), m = Math.max(2, Math.round((len - .8) / ev) + 1), at = [];
      for (let f = 0; f < n; f++) {
        const th = f * 2 * Math.PI / n, [ox, oz] = [Math.sin(th), Math.cos(th)];   // (the faces' middles: 0, 1, .. turns of 2pi/n from +z)
        for (let j = 0; j < m; j++) {
          const u = -(len / 2 - .4) + j * (len - .8) / (m - 1);
          at.push([ap * ox + u * oz, y, ap * oz - u * ox, th]);
        }
      }
      defs[`brackets ${k + 1}`] = { type: "component", use: B.use ?? "components/dougong", params: { s: bsc, ...(B.params ?? {}) }, at };
    });
  }
  // THE FINIAL on the top's point (the gilded jewel of a pavilion, a pagoda's mast and rings)
  if (def.finial) {
    const F = def.finial, h = P(F.height, 4), r = P(F.radius, .18), nr = Math.round(P(F.rings, 0)), b = P(F.base, 1.2), q = roofs[S.length - 1];
    const yA = ys[S.length] + q.foot + q.J(q.a) - b * .2;
    defs["finial base"] = { type: "prism", plan: { sides: n, radius: b / 2 }, height: b * .7, at: [[0, yA - b * .4, 0, 0]] };
    defs["finial mast"] = { type: "prism", plan: { sides: 8, radius: r }, height: h, at: [[0, yA + b * .3, 0, 0]] };
    const y0 = yA + b * .3 + h * .25, dy = h * .55 / Math.max(1, nr);
    if (nr > 0) defs["finial rings"] = { type: "prism", plan: { sides: 16, radius: r * 3.2 }, height: .1, at: Array.from({ length: nr }, (_, j) => [0, y0 + j * dy, 0, 0]) };
    defs["finial jewel"] = { type: "dome", radius: r * 2.4, head: { profile: "onion", bulge: 1.3, neck: .3 }, at: [[0, yA + b * .3 + h, 0, 0]] };
  }
  if (S.some((s) => s.gables)) throw new Error("a polygonal tiered tower has no gables");
  return defs;
}
