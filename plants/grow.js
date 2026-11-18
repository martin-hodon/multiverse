// THE GROWTH MODEL (2026-11-18): a plant's SKELETON from its species (species.js) and a seed -- the wood as branches
// (polylines with a radius at every point, each knowing its parent), and where its leaves are as TWIG SPRAYS (cards:
// a base on a branch, an axis, a facing, a size), plus a palm's fronds and a ceiba's prickles. No geometry here:
// mesh.js turns a skeleton into triangles, at each level of detail.
//
// How a tree grows, in order:
//   1. THE TRUNK, walked from the ground in segments, leaning a little and bending in slow S-curves. A broad habit
//      forks at `split.at` into leaders (some fork once more); an excurrent one runs its leader to the top.
//   2. THE LEVELS: along every branch its children, spaced over the part of it that is not bare (`start`), turning
//      round it (the spiral or two ranks: `rot`) or in whorls; each leaves at an angle that changes from the
//      parent's base to its tip, is as long as the crown's envelope allows there (`crown.shape`, over the height
//      in the crown) times its own spread, longer on the side the light comes from (`asym`) -- the crown is never
//      round -- and some never grow (`gaps`) or died young (`dead`: bare snags low in the crown).
//   3. EACH BRANCH is walked like the trunk: gravity pulls it down the more it reaches out (`gravity`), its tip
//      turns up toward the light (`photo`), it wanders (`wiggle`), and a gnarled species' shoots now and then
//      turn sharply where a bud died and a side bud took over (`kink`). Nothing grows into the ground.
//   (a FORKING habit -- the dragon blood tree, the Joshua tree -- has no levels: its trunk forks in two (or three)
//   again and again, each fork shorter, up to `fork.depth` times, and every last shoot ends in a ROSETTE of sword
//   leaves: a few crossed cards round its tip -- forkTree below)
//   4. THE DEEPEST LEVEL IS NOT WOOD: its children become the twig sprays -- each card is one twig with its
//      leaves, painted (bake.js), laid where that twig would grow and turned the way it would grow. So every
//      spray sits on a real branch and the crown's leaves follow its structure, clumped at the shoots' ends.
// The radii follow the pipe model loosely: a child is thinner than its parent where it leaves it, and the
// thinner the shorter it is. The whole tree is then scaled to its drawn height.
import { vAdd, vSub, vSc, vDot, vCross, vNorm, vPerp, vRot } from "../geom.js";
import { rng } from "../rng.js";

const D2R = Math.PI / 180, TAU = 2 * Math.PI, UP = [0, 1, 0];
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
// the crown's envelope: how long a limb grows at height t through the crown (0 its base, 1 its top)
const SHAPES = {
  conical: (t) => 1 - .86 * t,
  spherical: (t) => .25 + .75 * Math.pow(Math.sin(Math.PI * clamp(.06 + .9 * t, 0, 1)), .7),
  hemispherical: (t) => .18 + .82 * Math.pow(Math.cos(t * Math.PI / 2), .55),
  flame: (t) => t < .28 ? .55 + .45 * t / .28 : 1 - .88 * (t - .28) / .72,
  cylindrical: () => 1,
  tapered: (t) => 1 - .5 * t,
  inverse: (t) => .5 + .5 * t,
  umbrella: (t) => t < .62 ? .4 + .6 * t / .62 : 1 - .65 * (t - .62) / .38,
};

export function growPlant(S, seed) {
  const r = rng(seed * 7919 + 13);
  const gauss = () => (r() + r() + r() - 1.5) * 1.15;   // (near enough a unit normal)
  const H = lerp(S.height[0], S.height[1], r());
  const T = S.trunk, C = S.crown ?? {}, L = S.levels ?? [];
  // the deepest level with children is the twigs: the sprays, not wood
  const twigLevel = L.reduce((m, P, i) => (P.n ? i + 1 : m), 0);
  const branches = [], cards = [], knobs = [], fronds = [], bodies = [];
  // the side the tree gets its light from: its crown reaches further that way
  const la = r() * 2 * Math.PI, lightDir = [Math.cos(la), 0, Math.sin(la)];

  // ---- walking a branch: segments from p0 along d0, bending as it goes; returns its points and directions
  function walk(p0, d0, len, segs, P, stiff = 0) {
    const pts = [p0], dirs = [d0];
    let p = p0, d = d0;
    const step = len / segs;
    for (let i = 1; i <= segs; i++) {
      const t = i / segs;
      const out = Math.sqrt(Math.max(0, 1 - d[1] * d[1]));   // (how far it reaches out sideways: gravity bends a level branch most)
      let nd = vAdd(d, [0, -(P.gravity ?? 0) * (1.6 / segs) * (.35 + out) * (1 - stiff), 0]);
      nd = vAdd(nd, [0, (P.photo ?? 0) * (1.6 / segs) * t * (1 - stiff * .5), 0]);
      nd = vAdd(nd, vSc([gauss(), gauss() * .5, gauss()], (P.wiggle ?? 0) * (1 - stiff * .7)));
      if (r() < (P.kink ?? 0)) nd = vRot(nd, vRot(vPerp(nd), nd, r() * 2 * Math.PI), (22 + r() * 18) * D2R);
      d = vNorm(nd);
      if (p[1] + d[1] * step < .4 && d[1] < .15) d = vNorm([d[0], .15 + r() * .2, d[2]]);   // (never into the ground)
      p = vAdd(p, vSc(d, step));
      pts.push(p); dirs.push(d);
    }
    return { pts, dirs };
  }
  // a point and direction a share t along a walked branch
  function along(b, t) {
    const n = b.pts.length - 1, f = clamp(t, 0, 1) * n, i = Math.min(n - 1, Math.floor(f)), u = f - i;
    return { p: vAdd(b.pts[i], vSc(vSub(b.pts[i + 1], b.pts[i]), u)), d: vNorm(vAdd(vSc(b.dirs[i], 1 - u), vSc(b.dirs[i + 1], u))),
             r: lerp(b.rad[i], b.rad[i + 1], u) };
  }
  // a branch's radii: from r0 at its base toward r1 at its tip; `hold` < 1 keeps it thick longer
  const radii = (n, r0, r1, hold = 1) => Array.from({ length: n + 1 }, (_, i) => lerp(r0, r1, Math.pow(i / n, hold)));

  function addBranch(level, parent, tParent, w, rad, typ, extra = {}) {
    const b = { level, parent, tParent, pts: w.pts, dirs: w.dirs, rad, len: 0, typ, ...extra };
    for (let i = 1; i < w.pts.length; i++) b.len += Math.hypot(...vSub(w.pts[i], w.pts[i - 1]));
    branches.push(b);
    return b;
  }

  // ---- the children of branch b (level b.level + 1), or its twig sprays when that level is the twigs'
  function sprout(b) {
    const li = b.level;   // children of a level-0 branch use L[0]
    const P = L[li];
    if (!P || !P.n || b.dead) return;
    const isTwig = li + 1 === twigLevel;
    const crownBase = H * (C.base ?? 0), crownTop = H;
    // how many: the level's count for a branch of its typical length, by its real length
    let count = Math.round(P.n * Math.pow(clamp(b.len / b.typ, .25, 1.8), .85) * (.85 + .3 * r()));
    if (isTwig) count = Math.round(count * (S.twig?.dense ?? 2.2));   // (more than enough: mesh.js keeps what the crown needs)
    const start = b.level === 0 && !b.leader ? Math.max(P.start ?? 0, (crownBase - b.pts[0][1]) / Math.max(1, b.len)) : (P.start ?? 0);
    let phi = r() * 2 * Math.PI;
    const whorl = P.whorl ?? 1;
    for (let k = 0; k < count; k++) {
      const slot = whorl > 1 ? Math.floor(k / whorl) : k, slots = whorl > 1 ? Math.ceil(count / whorl) : count;
      let t = start + (1 - start) * clamp((slot + .5 + (whorl > 1 ? .08 : .35) * gauss()) / slots, 0, .985);
      if (isTwig) t = start + (1 - start) * Math.pow((k + r() * .8) / count, .7);   // (twigs crowd toward the shoot's end)
      const at = along(b, t);
      phi += whorl > 1 ? (k % whorl === 0 ? (P.rot ?? 137.5) * D2R : 2 * Math.PI / whorl) + .25 * gauss() : (P.rot ?? 137.5) * D2R + .2 * gauss();
      const ang = (lerp(P.angle[0], P.angle[1], t) + (P.jitter ?? 0) * gauss()) * D2R;
      const side = vRot(vPerp(at.d), at.d, phi);
      let dir = vNorm(vAdd(vSc(at.d, Math.cos(ang)), vSc(side, Math.sin(ang))));
      // its length: the crown's envelope at its height (limbs of the trunk and the leaders), else by where on its parent
      const yRel = clamp((at.p[1] - crownBase) / Math.max(1, crownTop - crownBase), 0, 1);
      let len = b.level === 0 ? H * (b.leader ? .55 : 1) * P.len * (SHAPES[C.shape] ?? SHAPES.spherical)(yRel)
                              : b.len * P.len * (1 - .45 * t);
      len *= Math.exp((P.lenV ?? .2) * gauss());
      const hz = Math.hypot(dir[0], dir[2]) || 1;
      if (li <= 1) len *= 1 + (C.asym ?? 0) * .7 * (dir[0] * lightDir[0] + dir[2] * lightDir[2]) / hz;
      if (isTwig) {
        twigCard(at, dir, b, t);
        continue;
      }
      if (li === 0 && r() < (C.gaps ?? 0)) continue;                 // a limb that never grew: a hole in the crown
      const dead = li === 0 && yRel < .3 && r() < (C.dead ?? 0);     // a bare snag low in the crown
      if (dead) len *= .3 + .25 * r();
      const segs = Math.max(2, Math.round((P.segs ?? 4) * clamp(len / (b.typ * P.len), .5, 1.3)));
      const r0 = Math.min(at.r * .82, at.r * (P.rr ?? .55) * Math.pow(clamp(len / Math.max(.1, b.len), .05, 1), .35));
      const w = walk(vAdd(at.p, vSc(dir, -at.r * .3)), dir, len, segs, P);
      const c = addBranch(li + 1, b, t, w, radii(segs, r0, Math.max(.004, r0 * .22), .9), Math.max(.1, b.typ * P.len), { dead });
      if (P.knobs) for (let j = 0; j < P.knobs; j++) knob(c, .05 + .5 * r());
      sprout(c);
    }
  }

  // ---- a twig spray: a card based at `at` on branch b, growing along `dir`, facing mostly up (or hanging)
  function twigCard(at, dir, b, t) {
    const W = S.twig;
    if (b.dead || t < (W.start ?? 0)) return;
    let ax = dir;
    if (W.hang) ax = vNorm(vAdd(vSc(ax, 1 - W.hang), [0, -W.hang * 1.6, 0]));
    // its face: the plane holding the twig, turned toward the sky by `up` (leaves spread to the light)
    const across = vNorm(vCross(ax, UP)), flat = vNorm(vCross(across, ax));   // (flat: the face of a twig lying level)
    let n = vRot(flat, ax, (r() - .5) * Math.PI * (1.1 - (W.up ?? .5)));   // (up 0: any roll round its axis; 1: flat to the sky)
    if (W.hang) n = vRot(vPerp(ax), ax, r() * 2 * Math.PI);
    const size = lerp(W.size[0], W.size[1], r()) * (b.level >= 2 || twigLevel <= 1 ? 1 : 1.1);
    cards.push({ p: at.p, d: ax, n: vNorm(n), size, level: b.level, shade: r(), flower: r(), on: b, s: t * b.len });
  }

  // ---- a banana's BUNCH (crown.bunch), as BODIES -- tubes { kind, pts, rad }, meshed by mesh.js in their own swatch
  // of the atlas, not painted on a card: a bunch is too big and too solid for one. The stalk leaves the crown's heart,
  // bows out and over and hangs; the HANDS up its hanging part in a spiral, each a crescent of fingers in two rows that
  // leave it level and curve up to the light (the lowest hands smaller); below them the bare rachis, and the purple BUD
  function bunch(top, B) {
    const a = r() * 2 * Math.PI, out = [Math.cos(a), 0, Math.sin(a)], R = B.arc ?? .22, s0 = vAdd(top, [0, -.12, 0]);
    const nh = Math.round(lerp(B.hands[0], B.hands[1], r())), gap = B.gap ?? .11, drop = (B.drop ?? .5) * (.8 + .4 * r());
    const stalk = [], rad = [];
    for (let i = 0; i <= 8; i++) {   // (a half circle: up out of the heart, over, and down)
      const th = i / 8 * Math.PI;
      stalk.push(vAdd(s0, vAdd(vSc(out, R * (1 - Math.cos(th))), [0, R * Math.sin(th) * .8, 0]))); rad.push(.032);
    }
    const hang = stalk[8], lean = vSc(out, .05 + .05 * r());
    const down = (y) => vAdd(hang, vAdd(vSc(lean, y), [0, -y, 0]));   // (the hanging part, y metres below the bow)
    const hangLen = nh * gap + drop;
    for (let y = .1; y <= hangLen + 1e-6; y += .1) { stalk.push(down(y)); rad.push(y < nh * gap ? .028 : .017); }
    bodies.push({ kind: "stalk", pts: stalk, rad });
    const nf = Math.round(lerp(B.fingers[0], B.fingers[1], r()));
    for (let h = 0; h < nh; h++) {
      const y = .06 + h * gap, c = down(y), th0 = h * 2.4 + a, k = 1 - .3 * h / Math.max(1, nh - 1);
      for (let row = 0; row < 2; row++) {
        const n = Math.round(nf / 2) - row;
        for (let i = 0; i < n; i++) {
          const ph = th0 + ((i + .5) / n - .5) * 3.4 + .08 * gauss(), rd = [Math.cos(ph), 0, Math.sin(ph)];
          const kk = k * (.9 + .2 * r()), up = (y2) => [0, y2 * kk, 0], go = (d) => vSc(rd, d * kk);
          const p0 = vAdd(c, vAdd(vSc(rd, .025), [0, row * .035, 0]));
          const p1 = vAdd(p0, vAdd(go(.05), up(-.01))), p2 = vAdd(p1, vAdd(go(.055), up(.04)));
          const p3 = vAdd(p2, vAdd(go(.025), up(.07))), p4 = vAdd(p3, vAdd(go(.002), up(.045)));
          bodies.push({ kind: "finger", pts: [p0, p1, p2, p3, p4], rad: [.007, .016, .019, .016, .006].map((x) => x * (.85 + .15 * kk)) });
        }
      }
    }
    const e = down(hangLen), L = (B.bud ?? .26) * (.85 + .3 * r()), tilt = vSc(out, .15);   // (the bud: a teardrop, hanging)
    const bud = [0, .12, .3, .5, .7, .88, 1].map((t) => vAdd(e, vAdd(vSc(tilt, t * L), [0, -t * L, 0])));
    bodies.push({ kind: "bud", pts: bud, rad: [.018, .042, .052, .05, .04, .022, .003].map((x) => x * L / .26) });
  }

  // ---- a fan palm's SKIRT (`crown.skirt`: { n: [lo, hi] dead fronds, down: metres of trunk it hangs over, len: their
  // length to a live frond's }): the dead leaves kept for years, hanging flat against the trunk under the crown, a
  // shaggy brown thatch -- fronds of their own, painted dry (bake.js: the spray's second column, `dead`). Each is hung
  // by its stalk from high in the crown's foot, so the thatch starts right under the live leaves; the oldest lowest
  function skirt(top, foot, K, shape, rTop) {
    const n = Math.round(lerp(K.n[0], K.n[1], r())), down = Math.min(K.down ?? 3, (top[1] - foot[1]) * .8);
    for (let i = 0; i < n; i++) {
      const a = i * 137.5 * D2R + .3 * gauss(), out = [Math.cos(a), 0, Math.sin(a)];
      const len = lerp(C.len[0], C.len[1], r()) * (K.len ?? .75) * (.85 + .3 * r()), u = Math.pow(i / n, 1.2);
      const y = len * (shape.fan ?? 0) * .7 - .1 - u * Math.max(0, down - len * .8);
      fronds.push({ p: vAdd(vAdd(top, [0, y, 0]), vSc(out, rTop * (1.05 + .25 * u) + .04)), d: vNorm(vAdd(vSc(out, .1 + .1 * r()), [0, -1, 0])), len, droop: .02,
                    width: C.width * (.45 + .2 * r()), ...shape, fold: .6, dead: true });
    }
  }

  // ---- COCONUTS (`crown.nuts`: { n: [lo, hi] a tree, bunches: [lo, hi], len: metres, r: girth to length }): ovoid
  // nuts in bunches round the crown's heart, under the fronds' bases, as BODIES (painted: bake.js paintBodies)
  function nuts(top, K, rTop) {
    const nb = Math.round(lerp((K.bunches ?? [2, 3])[0], (K.bunches ?? [2, 3])[1], r())), n = Math.round(lerp(K.n[0], K.n[1], r()));
    for (let b = 0; b < nb; b++) {
      const a0 = b / nb * TAU + r() * 1.2;
      for (let i = 0; i < Math.round(n / nb); i++) {
        const a = a0 + (r() - .5) * 1.1, out = [Math.cos(a), 0, Math.sin(a)], L = (K.len ?? .28) * (.85 + .25 * r()), R = L * (K.r ?? .42);
        const root = vAdd(top, vAdd(vSc(out, rTop + R * (.7 + .8 * r())), [0, -.25 - .45 * r(), 0]));
        const d = vNorm(vAdd(vSc(out, .5 + .4 * r()), [0, -1, 0]));
        const pts = [0, .1, .28, .5, .72, .9, 1].map((u) => vAdd(root, vSc(d, u * L)));
        bodies.push({ kind: "nut", pts, rad: [.3, .76, .96, 1, .93, .66, .12].map((x) => x * R) });
      }
    }
  }

  // ---- PODS (`pods`: a cacao's) borne on the old wood -- the trunk and the limbs, not the twigs -- each a ridged
  // spindle, as BODIES: hanging off the bark on a short stalk, swinging out a little ({ n: [lo, hi] a tree, len: [lo,
  // hi] metres, r: its girth to its length, up: to what share of the height, on: share of them on the limbs })
  function pods(P) {
    const n = Math.round(lerp(P.n[0], P.n[1], r())), wood = branches.filter((b) => b.level <= 1 && b.rad[0] > .025);
    for (let i = 0, guard = 0; i < n && guard < n * 6; guard++) {
      const b = r() < (P.on ?? .5) && wood.length > 1 ? wood[1 + Math.floor(r() * (wood.length - 1))] : branches[0], t = .1 + .8 * r(), at = along(b, t);
      if (at.p[1] > H * (P.up ?? .6) || at.p[1] < .3) continue;
      const out = vRot(vPerp(at.d), at.d, r() * TAU), L = lerp(P.len[0], P.len[1], r()), R = L * (P.r ?? .2);
      const root = vAdd(at.p, vSc(out, at.r * .9)), d = vNorm(vAdd([0, -1, 0], vSc(out, .45 + .3 * r())));
      const pts = [0, .06, .2, .4, .6, .8, .93, 1].map((u) => vAdd(root, vAdd(vSc(out, .03 + R * .9 * Math.min(1, u * 4)), vSc(d, .02 + u * L))));
      bodies.push({ kind: "pod", pts, rad: [.12, .2, .82, 1, .96, .74, .4, .02].map((x) => x * R), on: b, s: t * b.len });
      i++;
    }
  }

  // ---- a ceiba's prickle on branch b at share t: a stout cone out of the bark, sloping up
  function knob(b, t) {
    const at = along(b, t), out = vRot(vPerp(at.d), at.d, r() * 2 * Math.PI);
    const d = vNorm(vAdd(out, vSc(at.d, .35 + .2 * r())));
    const len = (T.knobs?.len ?? .06) * (.6 + .8 * r()) * clamp(at.r / .2, .45, 1.2);
    knobs.push({ p: vAdd(at.p, vSc(out, at.r * .96)), axis: at.p, trunk: !b.parent, d, len, r: len * (.6 + .25 * r()) });
  }

  // ---- 1. THE TRUNK (or a shrub's stems)
  const lean = (T.lean ?? 0) * D2R * Math.sqrt(r()), la2 = r() * 2 * Math.PI;
  const d0 = vNorm([Math.sin(lean) * Math.cos(la2), Math.cos(lean), Math.sin(lean) * Math.sin(la2)]);
  // (gnarl 0..1: a contorted trunk and leaders -- an old olive's, a yew's -- wandering and kinking as they go)
  const gnarl = T.gnarl ?? 0;
  const trunkP = { gravity: 0, photo: .25, wiggle: .02 + .03 * (T.sway ?? .3) + .1 * gnarl, kink: .1 * gnarl };
  const rBase = (T.r ?? .02) * H;
  // the trunk's girth along it: tapering, a ceiba's bulge, held toward a broad tree's fork
  const trunkRad = (n, len, r1) => Array.from({ length: n + 1 }, (_, i) => {
    const t = i / n;
    let rr = lerp(rBase, r1, Math.pow(t, T.taper ?? .8));
    if (T.bulge) rr *= 1 + T.bulge.a * Math.exp(-(((t - T.bulge.at) / .28) ** 2));
    return rr;
  });
  if (S.habit === "shrub") {
    const ns = Math.round(lerp(T.stems[0], T.stems[1], r()));
    for (let i = 0; i < ns; i++) {
      const a = i / ns * 2 * Math.PI + r() * .9, tilt = (T.spread ?? 25) * D2R * (.4 + .9 * r());
      const d = vNorm([Math.sin(tilt) * Math.cos(a), Math.cos(tilt), Math.sin(tilt) * Math.sin(a)]);
      const len = H * (.75 + .3 * r()), segs = 4, r0 = rBase * (.7 + .5 * r());
      const w = walk([Math.cos(a) * .06, 0, Math.sin(a) * .06], d, len, segs, { gravity: .1, photo: .15, wiggle: .08 });
      sprout(addBranch(0, null, 0, w, radii(segs, r0, r0 * .3, .9), H, { leader: true }));
    }
  } else if (S.habit === "palm") {
    const segs = 10, len = H * .96;
    const w = walk([0, 0, 0], d0, len, segs, { gravity: -.05, photo: .35, wiggle: .025 + .03 * T.sway }, 0);
    addBranch(0, null, 0, w, trunkRad(segs, len, rBase * (1 - (T.taper ?? .2))), len);
    const top = w.pts[segs], nf = Math.round(lerp(C.fronds[0], C.fronds[1], r())), [lo, hi] = C.rise ?? [-35, 72];
    const shape = { fan: C.fan ?? 0, fold: C.fold ?? .35 }, rTop = trunkRad(segs, len, rBase * (1 - (T.taper ?? .2)))[segs];
    for (let i = 0; i < nf; i++) {   // the fronds, oldest (lowest, hanging) to youngest (standing up in the heart), from round the trunk's rim
      const age = i / (nf - 1), a = i * 137.5 * D2R + .2 * gauss();
      const rise = lerp(lo, hi, Math.pow(1 - age, .8)) * D2R + .1 * gauss();
      fronds.push({ p: vAdd(top, [Math.cos(a) * rTop * .7, -.25 * age, Math.sin(a) * rTop * .7]), d: vNorm([Math.cos(a) * Math.cos(rise), Math.sin(rise), Math.sin(a) * Math.cos(rise)]),
                    len: lerp(C.len[0], C.len[1], r()) * (1 - .35 * (1 - age) * (1 - age)), droop: (C.droop ?? 1) * (.35 + .5 * age + .15 * r()),
                    width: C.width * (.85 + .3 * r()), ...shape });
    }
    if (C.skirt) skirt(top, w.pts[0], C.skirt, shape, rTop);
    if (C.bunch) bunch(top, C.bunch);
    if (C.nuts) nuts(top, C.nuts, rTop);
  } else if (S.habit === "forking") {
    forkTree();
  } else if (S.habit === "column") {
    columnCactus();
  } else if (S.habit === "pads") {
    padPlant();
  } else {
    const split = S.habit !== "excurrent" && T.split;
    const hTrunk = split ? H * clamp(split.at + .06 * gauss(), .15, .7) : H * .985;
    const segs = Math.max(6, Math.round(hTrunk / 1.6));
    const w = walk([0, 0, 0], d0, hTrunk, segs, trunkP, .6 * (1 - gnarl));
    const rTop = split ? rBase * (.7 - .15 * r()) : Math.max(.01, rBase * .06);
    const trunk = addBranch(0, null, 0, w, trunkRad(segs, hTrunk, rTop), H);
    sprout(trunk);
    if (T.knobs) for (let j = 0; j < T.knobs.n; j++) knob(trunk, .04 + Math.pow(r(), 1.4) * (T.knobs.up - .04));
    if (split) {   // the leaders
      const lead = (from, dir, len, rad, depth) => {
        const segsL = Math.max(4, Math.round(len / 1.5));
        const wl = walk(from, dir, len, segsL, { gravity: .02, photo: .3, wiggle: .05 + .1 * gnarl, kink: .06 + .14 * gnarl });
        const b = addBranch(0, trunk, 1, wl, radii(segsL, rad, Math.max(.01, rad * .1), .8), len * 1.6, { leader: true });
        if (T.knobs) for (let j = 0; j < 6; j++) knob(b, r() * .5);
        if (depth === 0 && r() < (split.again ?? 0)) {   // a leader forking once more, part way up
          const tf = .3 + .25 * r(), at = along(b, tf), k = 2;
          b.pts.length = b.dirs.length = b.rad.length = Math.max(2, Math.round(tf * segsL) + 1);
          b.len *= tf;
          const base = r() * 2 * Math.PI;
          for (let j = 0; j < k; j++) {
            const side = vRot(vPerp(at.d), at.d, base + j * Math.PI + .3 * gauss());
            const nd = vNorm(vAdd(vSc(at.d, Math.cos(split.angle * .8 * D2R)), vSc(side, Math.sin(split.angle * .8 * D2R))));
            lead(b.pts[b.pts.length - 1], nd, len * (1 - tf) * (.85 + .25 * r()), b.rad[b.rad.length - 1] * .8, 1);
          }
        }
        sprout(b);
      };
      const n = Math.round(lerp(split.n[0], split.n[1], r())), base = r() * 2 * Math.PI, top = w.pts[segs], td = w.dirs[segs];
      for (let i = 0; i < n; i++) {
        const ang = (split.angle + 10 * gauss()) * D2R, side = vRot(vPerp(td), td, base + i / n * 2 * Math.PI + .35 * gauss());
        const nd = vNorm(vAdd(vSc(td, Math.cos(ang)), vSc(side, Math.sin(ang))));
        lead(top, nd, (H - hTrunk) * (.8 + .25 * r()), rTop * Math.pow(1 / n, .45) * (.9 + .2 * r()), 0);
      }
    }
  }

  // ---- a FORKING tree: the trunk to `trunk.split.at`, then forks of forks (fork { depth: [lo, hi] times, n: 2, three:
  // share forking in three, angle: degrees each side of the parent, len: the first forks' length as a share of the
  // height, ratio: each fork's length to its parent's, lenV: spread, stop: chance a shoot stops forking early (a
  // Joshua tree's uneven arms), gravity / photo / wiggle as a level's }), every last shoot ending in a rosette
  function forkTree() {
    const F = S.fork, hTrunk = H * clamp((T.split?.at ?? .4) + .05 * gauss(), .15, .8), segs = Math.max(4, Math.round(hTrunk / 1.2));
    const w = walk([0, 0, 0], d0, hTrunk, segs, trunkP, .6 * (1 - gnarl));
    const rTop = rBase * (.75 - .1 * r());
    const trunk = addBranch(0, null, 0, w, trunkRad(segs, hTrunk, rTop), H);
    const depth = Math.round(lerp(F.depth[0], F.depth[1], r())), P = { gravity: F.gravity ?? 0, photo: F.photo ?? .3, wiggle: F.wiggle ?? .04, kink: F.kink ?? 0 };
    const fork = (b, d, len, rad) => {
      const end = b.pts.length - 1, at = { p: b.pts[end], d: b.dirs[end] }, k = r() < (F.three ?? 0) ? 3 : 2, base = r() * TAU;
      for (let j = 0; j < k; j++) {
        const ang = ((F.angle ?? 30) + 8 * gauss()) * D2R, side = vRot(vPerp(at.d), at.d, base + j / k * TAU + .3 * gauss());
        const dir = vNorm(vAdd(vSc(at.d, Math.cos(ang)), vSc(side, Math.sin(ang))));
        const l = len * Math.exp((F.lenV ?? .12) * gauss()), sg = Math.max(2, Math.round(l / .7));
        const r0 = rad * Math.pow(1 / k, .5) * (.92 + .16 * r());
        // (all level 1: a forking tree's arms are thick to their ends -- the far levels keep them by their girth, so the
        // rosettes never float free of their wood)
        // (from its parent's end girth, swelling the fork as a real one does, down to its own soon after)
        const c = addBranch(1, b, 1, walk(at.p, dir, l, sg, P), radii(sg, Math.max(r0, b.rad[b.rad.length - 1] * .9), r0 * .8, .35), l);
        if (d < depth && !(d >= 2 && r() < (F.stop ?? 0))) fork(c, d + 1, l * (F.ratio ?? .8), r0 * .8);
        else rosette(c);
      }
    };
    fork(trunk, 1, H * (F.len ?? .2), rTop);
  }
  // ---- a COLUMN cactus (the saguaro): one ribbed column, rounded at the top, and `arms` { n: [lo, hi], at: [lo, hi]
  // share of the height they leave from, out: [lo, hi] metres level before they turn, up: [lo, hi] share of the height
  // they then rise, r: [lo, hi] girth as a share of the trunk's there, droop: share that dip before turning up }. The
  // points are dense round an arm's elbow and its dome (mesh.js rings a column at its points); a `rosette` crowns
  // every top (its flowers and fruit)
  function columnCactus() {
    const A = S.arms ?? {}, rr = (x) => lerp(x[0], x[1], r());
    const dome = (pts, dirs, rad) => {   // (the rounded top: rings closing over the last one)
      const p = pts[pts.length - 1], d = dirs[dirs.length - 1], R = rad[rad.length - 1];
      for (const a of [30, 55, 75]) { pts.push(vAdd(p, vSc(d, R * Math.sin(a * D2R) * .85))); dirs.push(d); rad.push(R * Math.cos(a * D2R)); }
    };
    const segs = Math.max(8, Math.round(H / .5));
    const w = walk([0, 0, 0], d0, H * .97, segs, { gravity: 0, photo: .6, wiggle: .008 }, .8);
    const rad = radii(segs, rBase, rBase * (1 - (T.taper ?? .25)), 1.6);
    dome(w.pts, w.dirs, rad);
    const trunk = addBranch(0, null, 0, w, rad, H);
    const n = Math.round(lerp((A.n ?? [0, 3])[0], (A.n ?? [0, 3])[1], Math.pow(r(), .8))), base = r() * TAU;
    for (let i = 0; i < n; i++) {
      const t = rr(A.at ?? [.3, .6]), at = along(trunk, t), ra = at.r * rr(A.r ?? [.6, .8]);
      const az = base + i / n * TAU + .5 * gauss(), out = [Math.cos(az), 0, Math.sin(az)];
      const tilt = (r() < (A.droop ?? 0) ? -15 - 15 * r() : 5 + 15 * r()) * D2R;   // (leaving level, a little up -- or dipping)
      const bend = ra * 1.4 + .15, run = at.r * .7 + rr(A.out ?? [.3, .6]);
      const rise = clamp(H * rr(A.up ?? [.2, .4]), .4, H * (.88 - .1 * r()) - at.p[1] - bend);   // (an arm stays below the top)
      const pts = [], dirs = [], rads = [];
      let p = vAdd(at.p, vSc(out, at.r * .2)), d = vNorm(vAdd(vSc(out, Math.cos(tilt)), [0, Math.sin(tilt), 0]));
      const push = (s) => { pts.push(p); dirs.push(d); rads.push(ra * (.8 + .2 * clamp(s / (ra * 2.5), 0, 1))); };   // (pinched where it joins)
      let s = 0;
      for (const step of Array(Math.ceil(run / .15)).fill(run / Math.ceil(run / .15))) { push(s); p = vAdd(p, vSc(d, step)); s += step; }
      const turn = Math.PI / 2 - tilt + .08 * gauss(), arcN = Math.max(4, Math.round(turn * bend / .1));   // (the elbow)
      for (let k = 0; k < arcN; k++) {
        push(s);
        const a = tilt + turn * (k + 1) / arcN;
        d = vNorm(vAdd(vSc(out, Math.cos(a)), [0, Math.sin(a), 0]));
        p = vAdd(p, vSc(d, turn * bend / arcN)); s += turn * bend / arcN;
      }
      const upN = Math.max(2, Math.round(rise / .5));
      for (let k = 0; k < upN; k++) { push(s); p = vAdd(p, vSc(d, rise / upN)); s += rise / upN; }
      push(s);
      dome(pts, dirs, rads);
      rosette(addBranch(1, trunk, t, { pts, dirs }, rads, rise));
    }
    rosette(trunk);
  }
  // ---- a PAD cactus (the prickly pear): a short woody stem (`trunk.stem` metres), on it `pads.first` flat pads, each
  // growing `kids` more from its upper rim, `depth` deep, each `shrink` the size of its parent, turned off its axis by
  // up to `spread` degrees and leaning up by `rise`. A pad is a card that is never turned to the eye (`flat`: mesh.js)
  // -- on the stem, so it sways as stiffly as the stem does
  function padPlant() {
    const P = S.pads, rr = (x) => lerp(x[0], x[1], r()), ri = (x) => Math.round(rr(x));
    const sl = T.stem ?? .25, w = walk([0, 0, 0], d0, sl, 2, { wiggle: .05 });
    const stem = addBranch(0, null, 0, w, radii(2, rBase, rBase * (1 - (T.taper ?? .3))), H);
    const depth = ri(P.depth), top = w.pts[2];
    const pad = (p, d, size, k) => {
      const n = vRot(vPerp(d), d, r() * TAU), side = vNorm(vCross(d, n));
      cards.push({ p, d, n, size, level: 1, shade: r(), flower: r(), on: stem, s: sl, flat: true });
      if (k >= depth) return;
      const kids = ri(P.kids) - (k > 1 && r() < .3 ? 1 : 0);
      for (let j = 0; j < kids; j++) {   // (on the upper rim: the painted pad -- bake.js opuntia -- is an oval .36 long a side of its middle, .23 wide)
        const phi = ((kids > 1 ? j / (kids - 1) - .5 : 0) * 1.6 + .35 * gauss()), c = vAdd(p, vSc(d, size * .38));
        const q = vAdd(c, vAdd(vSc(d, size * .34 * Math.cos(phi)), vSc(side, size * .21 * Math.sin(phi))));
        const turn = vNorm(vAdd(vSc(d, Math.cos(phi * .7)), vSc(side, Math.sin(phi * .7))));
        const nd = vNorm(vAdd(vRot(turn, vPerp(turn), (P.spread ?? 35) * D2R * .4 * gauss()), [0, P.rise ?? .3, 0]));
        pad(q, nd, size * (P.shrink ?? .9) * (.9 + .2 * r()), k + 1);
      }
    };
    const nf = ri(P.first), base = r() * TAU;
    for (let i = 0; i < nf; i++) {
      const a = base + i / nf * TAU + .4 * gauss(), tilt = (15 + 35 * r()) * D2R;
      pad(vAdd(top, [0, -.03, 0]), vNorm([Math.sin(tilt) * Math.cos(a), Math.cos(tilt), Math.sin(tilt) * Math.sin(a)]), rr(P.size), 1);
    }
  }
  // ---- a ROSETTE of sword leaves round a shoot's tip: `twig.cards` crossed cards turned round its axis (the painting's
  // middle -- bake.js rosette -- a share `twig.mid` up the card, sat on the tip), more along the shoot (`twig.along`:
  // a Joshua tree's arms are leafy a way back from their ends)
  function rosette(b) {
    const W = S.twig, n = W.cards ?? 3, mid = W.mid ?? .38;
    for (let a = 0; a <= (W.along ?? 0); a++) {
      const t = 1 - a * .22, at = along(b, t), ax = vNorm(vAdd(at.d, [0, W.rise ?? .6, 0]));
      const size = lerp(W.size[0], W.size[1], r()) * (1 - .25 * a), base = vSub(at.p, vSc(ax, size * mid)), ph = r() * Math.PI;
      for (let k = 0; k < n; k++)
        cards.push({ p: base, d: ax, n: vRot(vPerp(ax), ax, ph + k / n * Math.PI), size, level: b.level, shade: r(), flower: r(), on: b, s: t * b.len });
    }
  }

  if (S.pods) pods(S.pods);

  // ---- to its drawn height: the top of the leaves (or the wood) is H
  let top = 0;
  for (const b of branches) for (const p of b.pts) top = Math.max(top, p[1]);
  for (const c of cards) top = Math.max(top, c.p[1] + c.d[1] * c.size);
  const k = H / Math.max(top, 1e-3);
  if (Math.abs(k - 1) > 1e-3) {
    for (const b of branches) { b.pts = b.pts.map((p) => vSc(p, k)); b.rad = b.rad.map((x) => x * k); b.len *= k; }
    for (const c of cards) { c.p = vSc(c.p, k); c.s *= k; if (c.flat) c.size *= k; }   // (a pad is wood, near enough: all of it scales)
    for (const q of knobs) { q.p = vSc(q.p, k); q.axis = vSc(q.axis, k); }
    for (const f of fronds) f.p = vSc(f.p, k);
    for (const q of bodies) { q.pts = q.pts.map((p) => vSc(p, k)); if (q.on) q.s *= k; }   // (moved with the plant, not grown: a bunch is a bunch)
  }
  return { H, branches, cards, knobs, fronds, bodies, lightDir, stiff: T.stiff ?? 0 };
}
