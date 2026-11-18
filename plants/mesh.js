// A PLANT'S TRIANGLES (2026-11-18): grow.js's skeleton made into geometry, at two levels of detail, as plain typed
// arrays (render.js makes buffers of them; nothing here needs three):
//
//   WOOD   every branch a tube along its points (each its own frame carried along it, so it never twists), its
//          girth from the skeleton, the trunk's foot flared out over its roots and lobed into buttresses, every
//          section of the trunk and the limbs a little out of round; the sides by its radius (3 for a twig, 12-16
//          for a bole), closed at its tip, sunk into its parent at its base. UVs run round (an integer number of
//          bark tiles, so the seam never shows) and along (in metres over the tile), with the tangent along the
//          branch for the bark's normal map. A ceiba's prickles are small cones; a palm's fronds are ribbons.
//   LEAVES each twig spray a quad from its base along its axis, in the atlas cell of a spray (render.js picks the
//          season's cell in the shader: aTone.y, the card's own random). Its four corners sit on its MIDLINE (the
//          axis, tangent) with its width and facing in aTone.w: the shader turns the card round its axis toward the
//          camera, by at most CARD_TURN, so a spray is never seen edge-on, and flutters its tip (render.js cardCorner).
//
// Every vertex carries, for the shaders:
//   aWind  (bend, phase): how far it moves in the wind (0 at the foot, more the higher and further out on its limb)
//          and the phase its limb sways on, so a limb moves as one and each limb its own way
//   aTone  (ao, tint, x, w): how deep in the crown (inner leaves and wood under the crown darker), a random per card
//          or branch; a card's chance of flower or fruit (x); its width in cm plus its grown facing (w: leafMesh;
//          0: not turned -- a palm's frond)
//   normal on a leaf is not its face's but the CROWN's -- out from the crown's middle -- so the crown is lit as one
//          rounded mass (the shader mixes in the face's own facing)
//
// LOD 0 (near): all the wood the skeleton has, every spray, the prickles.  LOD 1 (middle distance) and 2 (far): the
// SAME tree with its details left out -- the trunk and the limbs on fewer sides, the twigs gone, and a share of the
// same spray cards (FAR_CARDS: the outer ones first), each in its own place and slant, grown about its middle to cover
// for the rest and painted with the filled spray (bake.js column 4). Nothing moves at a switch but what goes. A
// palm's fronds are its leaves at every distance, on fewer segments the further.
import { vAdd, vSub, vSc, vDot, vCross, vNorm, vPerp, vRot } from "../geom.js";
import { rng } from "../rng.js";

const TAU = Math.PI * 2;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

// an append-only vertex store: positions, normals, uvs, tangents, wind, tone; indices
class Geo {
  constructor() { this.P = []; this.N = []; this.UV = []; this.T = []; this.W = []; this.A = []; this.I = []; this.n = 0; }
  v(p, n, uv, t, w, a) { this.P.push(p[0], p[1], p[2]); this.N.push(n[0], n[1], n[2]); this.UV.push(uv[0], uv[1]); this.T.push(t[0], t[1], t[2]); this.W.push(w[0], w[1]); this.A.push(a[0], a[1], a[2], a[3]); return this.n++; }
  tri(a, b, c) { this.I.push(a, b, c); }
  get tris() { return this.I.length / 3; }
  arrays() {
    return { position: new Float32Array(this.P), normal: new Float32Array(this.N), uv: new Float32Array(this.UV), tangent: new Float32Array(this.T),
             aWind: new Float32Array(this.W), aTone: new Float32Array(this.A), index: this.n > 65535 ? new Uint32Array(this.I) : new Uint16Array(this.I), tris: this.tris };
  }
}

// a smooth point a share t along a polyline (Catmull-Rom through its points), with its tangent and radius
function sampler(b) {
  const P = b.pts, n = P.length - 1, cum = [0];
  for (let i = 1; i <= n; i++) cum.push(cum[i - 1] + Math.hypot(...vSub(P[i], P[i - 1])));
  const len = cum[n] || 1e-6;
  const at = (s) => {   // s: metres along
    s = clamp(s, 0, len);
    let i = 0;
    while (i < n - 1 && cum[i + 1] < s) i++;
    const u = (s - cum[i]) / Math.max(1e-6, cum[i + 1] - cum[i]);
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(n, i + 2)];
    const u2 = u * u, u3 = u2 * u;
    const p = [0, 1, 2].map((k) => .5 * (2 * p1[k] + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u3));
    const d = [0, 1, 2].map((k) => .5 * ((-p0[k] + p2[k]) + 2 * (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u + 3 * (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u2));
    return { p, d: vNorm(d), r: b.rad[i] + (b.rad[i + 1] - b.rad[i]) * u };
  };
  return { at, len };
}

// how many sides a tube of radius r gets at a level of detail
const sidesFor = (r, lod) => lod === 0 ? (r > .3 ? 16 : r > .14 ? 12 : r > .07 ? 8 : r > .03 ? 6 : r > .012 ? 4 : 3)
                           : lod === 1 ? (r > .3 ? 8 : r > .1 ? 6 : r > .04 ? 4 : 3) : (r > .2 ? 5 : r > .08 ? 4 : 3);

// THE WOOD at a level of detail. S: the species, sk: the skeleton, opts.tile: the bark tile in metres; budget: the
// most triangles it may take -- over it, the rings are spaced wider and the thin branches lose a side, until it fits
// (budget: triangles -- the passes coarsen, then drop the thinnest twigs, until it fits; render.js gives level 0
//  what its leaves leave of the tree's)
export function woodMesh(S, sk, lod = 0, { tile = 1, budget = [3200, 900, 260][lod] } = {}) {
  let out;
  for (const [coarse, twigRings, minR] of [[1, 3, 0], [1.4, 2, 0], [1.9, 2, 0], [2.6, 1, 0], [2.6, 1, .012], [2.6, 1, .02], [2.6, 1, .03], [3.2, 1, .045], [3.2, 1, .065]]) {
    out = woodPass(S, sk, lod, tile, coarse, twigRings, minR);
    out.minR = minR;   // (what it pruned: rootCards moves the cards those twigs bore)
    if (out.tris <= budget) break;
  }
  return out;
}
// THE CARDS OF PRUNED TWIGS: woodMesh drops the level-2+ branches thinner than minR when the wood is over its budget,
// and a card on one would hang in the air where its twig was (a yew's dense sprays never hid them). Each such card is
// based where its twig -- or its twig's twig -- left the nearest branch still drawn, and reaches toward where its tip
// was (grown up to 1.5x to get there): its painted stem grows out of wood, the crown keeps its outline, and it sways
// with that branch. From each card's grown place (`home`), so it may be called again with another minR (0: all home).
export function rootCards(sk, minR) {
  const drawn = (b) => !(b.level >= 2 && b.rad[0] < minR);
  for (const c of sk.cards) {
    if (!c.on) continue;
    const h = c.home ??= { p: c.p, d: c.d, n: c.n, size: c.size, on: c.on, s: c.s };
    let p = h.p, b = h.on, s = h.s;
    while (b.parent && !drawn(b)) {
      const par = b.parent, k = par.pts.length - 1, f = clamp(b.tParent, 0, 1) * k, i = Math.min(k - 1, Math.floor(f)), u = f - i;
      p = vAdd(par.pts[i], vSc(vSub(par.pts[i + 1], par.pts[i]), u)); s = b.tParent * par.len; b = par;
    }
    Object.assign(c, h, { p, on: b, s });
    if (b === h.on) continue;
    const reach = vSub(vAdd(h.p, vSc(h.d, h.size)), p), L = Math.hypot(...reach);
    if (L < 1e-3) continue;
    c.d = vSc(reach, 1 / L); c.size = clamp(L, h.size, h.size * 1.5);
    const n = vSub(h.n, vSc(c.d, vDot(h.n, c.d)));   // (its face kept, square to its new axis)
    if (Math.hypot(...n) > 1e-3) c.n = vNorm(n); else c.n = vNorm(vPerp(c.d));
  }
}
// THE WIND on a skeleton (aWind): swayAt(b, pos, s) the weight and phase of the point pos, s along branch b. The
// weight is more up the tree and, on a limb, more out toward the crown's edge; the phase its limb's (the trunk's child
// it grew from: a forking tree's forks of forks are all level 1, but sway with the arm they grew from). At a branch's
// foot both are its parent's, its own a few girths on -- so a joint never opens in the wind; a leaf card takes its
// branch's at its base, so it stays on it (render.js cardCorner flutters only its tip)
function swayer(sk) {
  const H = sk.H, crown = crownShape(sk), r = rng(Math.round(H * 1000) + sk.branches.length * 7 + 3);
  for (const b of sk.branches) b.phase ??= r() * TAU;
  const limbOf = (b) => { let x = b; while (x.parent?.parent) x = x.parent; return x; };
  // (stiff: a saguaro's column hardly moves)
  const bendAt = (pos, level) => (1 - (sk.stiff ?? 0)) * (.25 * Math.pow(Math.max(0, pos[1]) / H, 2) + (level ? .55 * Math.pow(Math.hypot(pos[0], pos[2]) / Math.max(1, crown.R), 1.5) : 0));
  return (b, pos, s) => {
    const own = [bendAt(pos, b.level), limbOf(b).phase];
    if (!b.parent) return own;
    const w = clamp(s / (b.rad[0] * 6 + .15), 0, 1), k = w * w * (3 - 2 * w), up = [bendAt(pos, b.parent.level), limbOf(b.parent).phase];
    const dph = ((own[1] - up[1]) % TAU + TAU * 1.5) % TAU - Math.PI;   // (the phase the short way round)
    return [up[0] + (own[0] - up[0]) * k, up[1] + dph * k];   // (not wrapped: render.js plantPoint multiplies it)
  };
}

function woodPass(S, sk, lod, tile, coarse, twigRings, minR) {
  const g = new Geo(), H = sk.H, T = S.trunk;
  const r = rng(Math.round(H * 1000) + sk.branches.length);
  // (a column cactus is no crown's shade: its few cards crown its tops, its wood is all outside)
  const column = S.habit === "column", ribs = column ? T.ribs ?? 16 : 0;
  const crown = column ? { c: [0, -1e3, 0], R: .5, Hh: .5 } : crownShape(sk), seams = [], swayAt = swayer(sk);
  for (const b of sk.branches) {
    const r0 = b.rad[0];
    if (b.level >= 2 && r0 < minR) continue;   // (over budget even coarse: the finest twigs go -- rootCards moves their cards)
    if (lod === 1 && (b.level >= 2 || r0 < .025)) continue;   // (the middle distance: trunk and limbs only)
    if (lod >= 2 && (b.level >= 2 || (b.level === 1 && r0 < .07))) continue;   // (far: the trunk and the big limbs)
    const smp = sampler(b), isTrunk = !b.parent && S.habit !== "shrub" && !column;
    // (a column: a crest and a groove a rib near, the ribs' crests alone further, half of them far)
    const sides = column ? Math.max(5, Math.round(ribs * [2, 1, .5][lod])) : Math.max(3, sidesFor(r0, lod) - (coarse > 1.2 && r0 < .14 ? 1 : 0));
    // where its rings are: along it every ~ its girth (the trunk: closer at its foot, for the flare)
    const ss = [];
    if (column) {   // (a column: rings at its own points -- dense round an arm's elbow and a top's dome -- thinned
      // to one every `step` metres along it, or wherever it has turned `turn` radians since)
      const step = [.5, 1.3, 2.6][lod] * coarse, turn = [.22, .45, .8][lod] * coarse;
      if (!b.parent) ss.push(-.2);
      ss.push(0);
      let acc = 0, last = 0, bent = 0;
      for (let i = 1; i < b.pts.length - 1; i++) {
        acc += Math.hypot(...vSub(b.pts[i], b.pts[i - 1]));
        bent += Math.acos(clamp(vDot(b.dirs[i - 1], b.dirs[i]), -1, 1));
        if (acc - last >= step || bent >= turn || i >= b.pts.length - 4) { ss.push(Math.min(acc, smp.len - .02)); last = acc; bent = 0; }
      }
    } else if (isTrunk) {
      const fh = T.flareH ?? 1;
      for (const f of lod >= 2 ? [-.25, 0, .3, 1] : [-.25, 0, .08, .2, .38, .65, 1]) ss.push(f * fh);
      for (let s = fh * 1.4; s < smp.len - .5; s += [1.3, 2.6, 4.5][lod] * coarse) ss.push(s);
    } else {   // (a limb a ring every ~6 girths; a branch in at most `twigRings` pieces: it is thin, its bend is all it shows)
      const step = Math.max(lod ? .9 : .5, r0 * (lod ? 10 : 6) * coarse, b.level >= 2 ? smp.len / (lod ? 1 : twigRings) : 0);
      for (let s = 0; s < smp.len - step * .3; s += step) ss.push(s);
    }
    ss.push(smp.len);
    // (the bark round it: a whole number of tiles; along it at the same scale, so a thin branch's bark is fine, not squeezed)
    // (a column: a tile a rib, its crest at the tile's edge -- bake.js cactus)
    const U = column ? ribs : Math.max(1, Math.round(TAU * r0 / tile)), tileL = column ? TAU * Math.max(...b.rad) / U : Math.max(.08, TAU * r0 / U);
    const ring0 = g.n;
    let ref = null, prevD = null;
    const lobes = isTrunk ? (T.buttress ?? 0) : 0, lobePh = r() * TAU, irr = column ? 0 : isTrunk ? .07 : b.level <= 1 ? .05 : 0;
    const ph = [r() * TAU, r() * TAU, r() * TAU];
    for (const s of ss) {
      const below = s < 0, q = smp.at(Math.max(0, s));
      const p = below ? vAdd(q.p, [0, s, 0]) : q.p;
      // carry the frame along (parallel transport): no twist
      if (!ref) ref = vPerp(q.d);
      else { const ax = vCross(prevD, q.d), sn = Math.hypot(...ax); if (sn > 1e-6) ref = vRot(ref, vNorm(ax), Math.asin(clamp(sn, -1, 1))); }
      prevD = q.d;
      ref = vNorm(vSub(ref, vSc(q.d, vDot(ref, q.d))));
      const bi = vCross(q.d, ref);
      let rad = q.r;
      const y = p[1];
      if (isTrunk) rad *= 1 + (T.flare ?? 0) * Math.exp(-Math.max(0, y) / Math.max(.1, T.flareH ?? 1) * 2.2);
      for (let j = 0; j <= sides; j++) {
        const th = j / sides * TAU;
        let rr = rad;
        if (lobes) rr *= 1 + (T.buttressA ?? .1) * Math.pow(Math.max(0, Math.cos(lobes * th + lobePh)), 3) * Math.exp(-Math.max(0, y) / ((T.flareH ?? 1) * 1.2)) * 3;
        if (ribs) rr *= 1 + (T.ribA ?? .07) * Math.cos(ribs * th);
        if (irr) rr *= 1 + irr * (Math.sin(2 * th + ph[0] + s * .7) * .6 + Math.sin(3 * th + ph[1] - s * .45) * .3 + Math.sin(5 * th + ph[2] + s * 1.3) * .15);
        const o = vAdd(vSc(ref, Math.cos(th)), vSc(bi, Math.sin(th)));
        const pos = vAdd(p, vSc(o, rr));
        const ao = woodAO(pos, crown, H);
        g.v(pos, o, [j / sides * U, s / tileL], q.d, swayAt(b, pos, Math.max(0, s)), [ao, b.phase / TAU, 0, 0]);
      }
    }
    const rings = ss.length;
    for (let i = 0; i < rings; i++) seams.push([ring0 + i * (sides + 1), ring0 + i * (sides + 1) + sides]);
    for (let i = 0; i < rings - 1; i++) for (let j = 0; j < sides; j++) {
      const a = ring0 + i * (sides + 1) + j, c = a + sides + 1;
      g.tri(a, a + 1, c); g.tri(a + 1, c + 1, c);   // (counter-clockwise seen from outside: the bark faces out)
    }
    // its tip, closed with a point a little beyond the last ring (blunt on a column or a palm's trunk, hidden in its crown)
    const last = smp.at(smp.len), tipP = vAdd(last.p, vSc(last.d, last.r * (column || S.habit === "palm" && b.level === 0 ? .35 : 1.5))), base = ring0 + (rings - 1) * (sides + 1);
    const tip = g.v(tipP, last.d, [U / 2, smp.len / tileL + .05], last.d, swayAt(b, tipP, smp.len), [woodAO(tipP, crown, H), b.phase / TAU, 0, 0]);
    for (let j = 0; j < sides; j++) g.tri(base + j, base + j + 1, tip);
  }
  smoothNormals(g, seams);
  if (lod === 0) for (const k of sk.knobs) knobMesh(g, k, crown, H, T);
  return g.arrays();
}

// the crown as an ellipsoid round the sprays' middle: its centre, radius across (R) and half-height (Hh)
export function crownShape(sk) {
  const pts = sk.cards.length ? sk.cards.map((c) => vAdd(c.p, vSc(c.d, c.size * .5))) : sk.fronds.map((f) => vAdd(f.p, vSc(f.d, f.len * .5)));
  if (!pts.length) return { c: [0, sk.H * .6, 0], R: sk.H * .3, Hh: sk.H * .3 };
  const c = pts.reduce((a, p) => vAdd(a, p), [0, 0, 0]).map((v) => v / pts.length);
  const hs = pts.map((p) => Math.hypot(p[0] - c[0], p[2] - c[2])).sort((a, b) => a - b), vs = pts.map((p) => Math.abs(p[1] - c[1])).sort((a, b) => a - b);
  return { c, R: Math.max(.5, hs[Math.floor(hs.length * .9)] * 1.08), Hh: Math.max(.5, vs[Math.floor(vs.length * .9)] * 1.08) };
}
// how much light reaches a point of wood: under and in the crown less, the foot of the trunk in its own shade
const woodAO = (p, cr, H) => {
  const dx = (p[0] - cr.c[0]) / cr.R, dz = (p[2] - cr.c[2]) / cr.R, dy = (p[1] - cr.c[1]) / cr.Hh;
  const inside = clamp(1 - Math.sqrt(dx * dx + dy * dy + dz * dz), 0, 1);
  return clamp(1 - .45 * inside - .25 * Math.exp(-Math.max(0, p[1]) / 1.2) - (p[1] < cr.c[1] ? .12 : 0), .3, 1);
};

// normals from the faces round each vertex (the buttresses and the out-of-round sections lit as they are); the
// seam's twin columns (seams: [first, last] vertex of each) share their sum, so no ridge shows down a branch
function smoothNormals(g, seams) {
  const N = new Float64Array(g.n * 3), P = g.P, I = g.I;
  for (let i = 0; i < I.length; i += 3) {
    const a = I[i] * 3, b = I[i + 1] * 3, c = I[i + 2] * 3;
    const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
    const fx = uy * vz - uz * vy, fy = uz * vx - ux * vz, fz = ux * vy - uy * vx;
    for (const v of [a, b, c]) { N[v] += fx; N[v + 1] += fy; N[v + 2] += fz; }
  }
  for (const [u, v] of seams) for (let k = 0; k < 3; k++) { const t = N[u * 3 + k] + N[v * 3 + k]; N[u * 3 + k] = N[v * 3 + k] = t; }
  for (let v = 0; v < g.n; v++) {
    const x = N[v * 3], y = N[v * 3 + 1], z = N[v * 3 + 2], l = Math.hypot(x, y, z);
    if (l < 1e-12) continue;
    if ((x * g.N[v * 3] + y * g.N[v * 3 + 1] + z * g.N[v * 3 + 2]) / l > -.2) { g.N[v * 3] = x / l; g.N[v * 3 + 1] = y / l; g.N[v * 3 + 2] = z / l; }
  }
}

// a prickle: a three-sided cone from the bark (on the trunk: out to where the flare puts the bark at its height)
function knobMesh(g, k0, crown, H, T) {
  let k = k0;
  if (k.trunk && T.flare) { const f = 1 + T.flare * Math.exp(-Math.max(0, k.p[1]) / Math.max(.1, T.flareH ?? 1) * 2.2); k = { ...k, p: vAdd(k.axis, vSc(vSub(k.p, k.axis), f)) }; }
  const ref = vPerp(k.d), bi = vCross(k.d, ref), tip = vAdd(k.p, vSc(k.d, k.len)), base = g.n, ao = woodAO(k.p, crown, H);
  for (let j = 0; j < 3; j++) {
    const th = j / 3 * TAU, o = vAdd(vSc(ref, Math.cos(th)), vSc(bi, Math.sin(th)));
    g.v(vAdd(vSub(k.p, vSc(k.d, k.r * .6)), vSc(o, k.r)), vNorm(vAdd(o, vSc(k.d, .4))), [j / 3, 0], k.d, [.02, 0], [ao * .9, 0, 0, 0]);
  }
  const t = g.v(tip, k.d, [.5, .3], k.d, [.02, 0], [ao, 0, 0, 0]);
  for (let j = 0; j < 3; j++) g.tri(base + j, base + (j + 1) % 3, t);
}

// THE BODIES (grow.js: a banana's bunch, a cacao's pods): tubes, each ring a whole number of sides (fewer, and fewer
// rings, further off: the same bodies at every level, less round -- a finger keeps its bend), wrapped round the kind's
// swatch in the atlas's last column (bake.js paintBodies: a palm's fifth -- it has no far cards, so that column is free
// -- or a sixth of their own). Their uv is the atlas's own (aTone.w -1: render.js cardUv takes it as it is, cardCorner
// turns nothing); they sway with the wood they hang from (a bunch: the trunk's top). Their own part ("body") at every
// level, drawn with the leaves' material. cells: the atlas's columns
export const BODY_BANDS = { finger: [.02, .44], pod: [.02, .44], nut: [.02, .44], bud: [.52, .74], stalk: [.82, .98] };   // (u in the column; a plant has fingers, pods or nuts)
const BODY_LOD = { finger: { sides: [4, 3, 3], step: [1, 2, 2] }, pod: { sides: [7, 5, 4], step: [1, 2, 3] }, nut: { sides: [8, 6, 4], step: [1, 2, 3] }, bud: { sides: [8, 6, 4], step: [1, 2, 3] },
                   stalk: { sides: [6, 4, 3], step: [1, 2, 3] } };
export function bodyMesh(sk, lod, cells) {
  const g = new Geo(), swayAt = swayer(sk), trunk = sk.branches[0], top = swayAt(trunk, trunk.pts.at(-1), trunk.len);
  for (const [bi, q] of sk.bodies.entries()) {
    const sway = q.on ? swayAt(q.on, q.pts[0], q.s) : top;
    const L = BODY_LOD[q.kind], band = BODY_BANDS[q.kind], sides = L.sides[lod], step = L.step[lod];
    const wide = 1 / Math.cos(Math.PI / sides);   // (a few sides round the circle, not in it: as broad as the round one)
    const idx = q.pts.map((_, i) => i).filter((i) => i % step === 0 || i === q.pts.length - 1);
    const cum = [0];
    for (let i = 1; i < q.pts.length; i++) cum.push(cum[i - 1] + Math.hypot(...vSub(q.pts[i], q.pts[i - 1])));
    const len = cum.at(-1) || 1, base = g.n;
    let ref = null;
    for (const i of idx) {
      const d = vNorm(vSub(q.pts[Math.min(i + 1, q.pts.length - 1)], q.pts[Math.max(i - 1, 0)]));
      ref = ref ? vNorm(vSub(ref, vSc(d, vDot(ref, d)))) : cardFrame(d)[0];   // (carried along: no twist)
      const ref2 = vCross(d, ref);
      for (let j = 0; j <= sides; j++) {   // (the seam twice: its two sides of the swatch)
        const th = j / sides * TAU, o = vAdd(vSc(ref, Math.cos(th)), vSc(ref2, Math.sin(th)));
        g.v(vAdd(q.pts[i], vSc(o, q.rad[i] * wide)), o, [(cells - 1 + band[0] + (band[1] - band[0]) * j / sides) / cells, .02 + .96 * cum[i] / len], d, sway,
            [.8 + .2 * Math.max(0, o[1]), (bi * .618) % 1, 0, -1]);
      }
    }
    for (let s = 0; s < idx.length - 1; s++) for (let j = 0; j < sides; j++) {
      const a = base + s * (sides + 1) + j, c = a + sides + 1;
      g.tri(a, c, a + 1); g.tri(a + 1, c, c + 1);
    }
  }
  return g.arrays();
}

// a palm's fronds: each a ribbon down its arching midrib, folded up along it into a shallow V (the pinnae rise from
// the rachis; `fold` < 0: they hang from it, a coconut's), in a spray cell of the atlas (uv: across 0..1, along 0..1)
// -- drawn with the leaves. A FAN palm's (`fan`: the share of it that is bare stalk) is a narrow stalk, then the round
// blade -- its rows where the painting's are (bake.js fanLeaf: FAN_W). A dead one (a fan palm's skirt) shows the
// cell's second column, the dry leaf, and never flowers
export const FAN_W = (s) => Math.max(.3, Math.sqrt(Math.max(0, 1 - ((s - .4) / .62) ** 2)));   // (the blade's half-width, s along it)
function frondMeshes(g, sk, lod) {
  sk.fronds.forEach((f, i) => {
    const ph = (i * 2.399) % TAU, base = g.n, fan = f.fan ?? 0;
    // (the rows: evenly, or a fan's -- its stalk in few, a row just past the hastula where the blade opens, the blade in more)
    const T = fan ? [...Array.from({ length: [3, 2, 1][lod] }, (_, k) => k / [3, 2, 1][lod] * fan), fan, fan + .03,
                     ...Array.from({ length: [6, 4, 2][lod] }, (_, k) => fan + .03 + (1 - fan - .03) * (k + 1) / [6, 4, 2][lod])]
                  : Array.from({ length: [9, 5, 3][lod] + 1 }, (_, k) => k / [9, 5, 3][lod]);
    const halfW = (t) => fan ? (t <= fan + 1e-6 ? .07 : FAN_W((t - fan) / (1 - fan))) : Math.pow(Math.sin(Math.PI * clamp(.08 + t * .92, 0, 1)), .55) * (t < .1 ? t / .1 : 1);
    const tone = f.dead ? [.2, 1] : [fan ? 0 : (i * .618) % 1, (i * .371 + .13) % 1];   // (aTone.y: its column -- render.js cardUv; .z its chance of bearing)
    let p = f.p, d = f.d, side = vCross(f.d, [0, 1, 0]);
    side = vNorm(Math.hypot(...side) > 1e-3 ? side : [1, 0, 0]);
    for (let s = 0; s < T.length; s++) {
      const t = T[s], w = f.width * halfW(t);
      const up = vNorm(vCross(side, d)), fold = f.fold ?? .35;
      const bend = f.dead ? .05 + .1 * t : .1 + .6 * t;
      for (const [k, u] of [[-1, 0], [0, .5], [1, 1]]) {
        const pos = vAdd(p, vAdd(vSc(side, k * w * .5), vSc(up, Math.abs(k) * w * .5 * fold)));
        g.v(pos, vNorm(vAdd(up, vSc(side, -k * .5 * Math.sign(fold || 1)))), [u, t], d, [bend, ph], [.75 + .25 * t, tone[0], tone[1], 0]);
      }
      if (s === T.length - 1) break;
      const step = f.len * (T[s + 1] - t);
      d = vNorm(vAdd(d, [0, -f.droop * 1.8 * (T[s + 1] - t) * (.4 + t), 0]));
      p = vAdd(p, vSc(d, step));
    }
    for (let s = 0; s < T.length - 1; s++) for (let k = 0; k < 2; k++) {
      const a = base + s * 3 + k, c = a + 3;
      g.tri(a, c, a + 1); g.tri(a + 1, c, c + 1);
    }
  });
}

// a card's frame round its axis ax: ref, ref2 square to it and to each other -- render.js cardCorner builds the same
// (ref level, so a tree's turn round the vertical turns it with the tree)
export function cardFrame(ax) {
  let ref = vCross(ax, [0, 1, 0]);
  if (Math.hypot(...ref) < 1e-4) ref = vCross(ax, [1, 0, 0]);
  ref = vNorm(ref);
  return [ref, vCross(ax, ref)];
}

// the far levels' cards: [the share kept, how much bigger] at LOD 1 and 2 -- a little over half the near crown's card
// area, as the filled spray covers more of its card than the near one does; grown about their middles, so the crown
// keeps its outline (their twigs are gone at those levels: nothing to stay on)
const FAR_CARDS = [[.3, 1.15], [.16, 1.3]];

// THE LEAVES: each spray a quad (at LOD 1 and 2 FAR_CARDS of them). aspect: the spray's width over its length (its atlas cell's)
// cover: the cards' area over the crown's surface -- every tree of a species as full, however many sprays it grew
// (grow.js grows more than enough: a share is kept; a thin crown's cards are drawn a little bigger)
// (box: [u0, u1, v0, v1] the part of a spray's cell its painting is in -- bake.js trims: each card cut to it)
export function leafMesh(S, sk, { aspect = .5, maxCards = 950, lod = 0, cover = S.twig?.cover ?? 2.4, box = [0, 1, 0, 1] } = {}) {
  const g = new Geo(), cr = crownShape(sk), r = rng(sk.cards.length * 31 + 7);
  if (sk.fronds.length) { frondMeshes(g, sk, lod); return g.arrays(); }
  let cards = sk.cards;
  const p = 1.6, a = cr.R, c = cr.Hh;   // (an ellipsoid's surface, Knud Thomsen's formula)
  const surface = 4 * Math.PI * Math.pow((Math.pow(a * a, p) + 2 * Math.pow(a * c, p)) / 3, 1 / p);
  const area = cards.reduce((t, q) => t + q.size * q.size * aspect, 0), want = surface * cover;
  let keep = Math.min(1, want / Math.max(1e-6, area), maxCards / Math.max(1, cards.length)), grow = 1;
  if (area * keep < want) grow = Math.min(1.35, Math.sqrt(want / Math.max(1e-6, area * keep)));
  if (keep < 1) cards = cards.filter(() => r() < keep);
  if (cards.length > maxCards) cards = cards.slice(0, maxCards);   // (the thinning is by chance: never over the cap)
  // (the far levels: the outer cards first -- the crown's skin is what is seen. Not a prickly pear's pads: they are its body)
  if (lod > 0 && FAR_CARDS[lod - 1] && !cards.every((q) => q.flat)) {
    const [share, big] = FAR_CARDS[lod - 1];
    const ranked = cards.map((q) => [q, r() + leafAO(vAdd(q.p, vSc(q.d, q.size * .5)), cr)]).sort((x, y) => y[1] - x[1]);
    cards = ranked.slice(0, Math.max(1, Math.round(cards.length * share))).map(([q]) => ({ ...q, p: vSub(q.p, vSc(q.d, q.size * grow * (big - 1) / 2)) }));
    grow *= big;
  }
  if (grow > 1) cards = cards.map((q) => ({ ...q, size: q.size * grow }));
  const swayAt = swayer(sk);
  for (const c of cards) {
    const ax = c.d, w = c.size * aspect, base0 = vSub(c.p, vSc(ax, c.size * .04));
    const mid = vAdd(base0, vSc(ax, c.size * .5));
    const out = crownOut(mid, cr);
    const ao = leafAO(mid, cr);
    // (the whole card sways as its branch does at its base: render.js cardCorner flutters its tip about that)
    const sway = c.on ? swayAt(c.on, c.p, c.s) : [.25 * Math.pow(mid[1] / sk.H, 2) + .06, c.shade * TAU];
    const v0 = g.n;
    // its grown facing, as the angle of its side round its axis from a frame the shader rebuilds (cardFrame): the
    // shader turns it toward the eye by at most CARD_TURN from there. Packed with its width: cm + angle / pi
    const [ref, ref2] = cardFrame(ax), side = vCross(ax, c.n);
    const th = ((Math.atan2(vDot(side, ref2), vDot(side, ref)) % Math.PI) + Math.PI) % Math.PI;
    // (a FLAT card -- a cactus pad -- is never turned: its corners are where they are, and packed 0 the shader leaves them)
    const pack = c.flat ? 0 : Math.max(1, Math.round(w * 100)) + Math.min(th / Math.PI, .999), across = vNorm(side);
    for (const [i, j] of [[box[0], box[2]], [box[1], box[2]], [box[0], box[3]], [box[1], box[3]]]) {
      let pos = vAdd(base0, vSc(ax, c.size * j));   // (on the midline: the shader spreads it to its side)
      if (c.flat) pos = vAdd(pos, vSc(across, (i - .5) * w));
      g.v(pos, c.flat ? c.n : out, [i, j], ax, sway, [c.flat ? ao * .9 + .1 : ao * (.88 + .12 * j), c.shade, c.flower, pack]);
    }
    g.tri(v0, v0 + 2, v0 + 1); g.tri(v0 + 1, v0 + 2, v0 + 3);
  }
  return g.arrays();
}
const crownOut = (p, cr) => vNorm([(p[0] - cr.c[0]) / cr.R, (p[1] - cr.c[1]) / cr.Hh * .8 + .25, (p[2] - cr.c[2]) / cr.R]);
const leafAO = (p, cr) => {
  const dx = (p[0] - cr.c[0]) / cr.R, dz = (p[2] - cr.c[2]) / cr.R, dy = (p[1] - cr.c[1]) / cr.Hh;
  const d = Math.sqrt(dx * dx + dy * dy + dz * dz);   // 0 the middle .. ~1 the outside
  return clamp(.42 + .58 * Math.pow(clamp(d, 0, 1), .8) + .1 * dy, .35, 1.05);
};
