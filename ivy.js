// IVY (2026-10-24): a creeper up some of the houses' walls -- rooted in the ground beside the door, its stems climbing
// and branching over the wall's outer face, round the windows and the door (never over them), up to where that face
// ends (the eaves, a jetty's overhang, the house's corner: found by probing the wall), in lobed dark leaves, the
// young ones at the stems' ends a fresher green, stirring in the wind (grass.js windAt: their tips, not their stalks).
// One lit mesh for the leaves (snowyLit: wet after rain, the snow on what faces up), one for the stems.
//
//   const ivy = createIvy(scene, doors, windows, { seed, groundH })
//     doors: frameDoors [{ x, y, z, w, h, base, cx, cz, outer, arched, probe(x, y, z) -> the wall's outer face there
//            (metres out from the line through the door, undefined where there is none), pile (-1/1: a woodpile's side) }]
//     windows: the glow's list [{ x, y, z, w, h, base, cx, cz }] (the openings the stems go round)
//   ivy.update(t)
import * as THREE from "three";
import { attribute, uniform, positionGeometry, normalGeometry } from "three/tsl";
import { snowyLit, wallFrame } from "./windowframes.js";
import { windAt } from "./grass.js";
import { rng } from "./flora.js";

// share: of the houses' plain doors, how many have ivy (arched: of the arched ones); root: how far beside the door it is planted (past the jamb);
// reach: how far along the wall it may spread either way, top: how high at most; step: a stem's segment; leaf: their
// size (lower, older leaves bigger), spacing along a stem, how far off the wall; branch: a branch's chance a step, and
// their length by depth; leaves: at most a plant; probe: the wall's sampling (metres)
export const IVY = { share: .45, arched: .7, root: [.5, .9], reach: 2.4, top: 8, step: .05, probe: .3,
                     leaf: { size: [.06, .11], every: .03, out: [.012, .05] }, branch: { p: .16, len: [2.6, 1.6, 1.0, .5] }, leaves: 2400,
                     green: ["#2c4a22", "#34552a", "#3d5f2c", "#2a4226", "#46662f"], young: "#6d8f3c", stem: "#5a4a38" };
// the leaf's outline (x across, y towards its tip, by its size): three lobes and the two lower ones, round a middle
const OUTLINE = [[0, 0], [-.35, -.08], [-.55, .28], [-.18, .42], [0, .95], [.18, .42], [.55, .28], [.35, -.08]];

export function createIvy(scene, doors, windows, { seed = 1, groundH = null } = {}) {
  const r = rng(seed * 61 + 29), lerp = (a, b, t) => a + (b - a) * t;
  const LP = [], LN = [], LC = [], LF = [], LI = [], SP = [], SN = [], SC = [], SI = [];
  const leafCol = new THREE.Color(), young = new THREE.Color(IVY.young), stemCol = new THREE.Color(IVY.stem);
  let plants = 0;
  const roots = [];   // (where each was planted, and its wall's way out: for the checks)
  for (const d of doors) {
    if (d.outer === undefined || !d.probe || !groundH || r() > (d.arched ? IVY.arched : IVY.share)) continue;   // (an arched door -- the church's, a merchant's -- more often: old stone)
    const F = wallFrame(d), { ax, az, nx, nz } = F, side = d.pile ? -d.pile : r() < .5 ? -1 : 1;
    const [mx, mz] = F.at(0);   // (the wall's outer face in front of the door's middle: u along it, y up, the wall at out 0)
    const W = (u, y, out) => [mx + ax * u + nx * out, y, mz + az * u + nz * out];
    const u0 = side * (d.w / 2 + lerp(IVY.root[0], IVY.root[1], r())), [rx, , rz] = W(u0, 0, .1), gy = groundH(rx, rz);
    if (Math.abs(gy - d.y) > .6) continue;   // (an upper storey's door, or a stair's: not from the ground)
    // the wall's face: where it is (at the door's depth, within a few cm -- not a jetty out over it, not a neighbour)
    const wallHas = (u, y) => { const [x, , z] = W(u, y, -d.outer); const o = d.probe(x, y, z); return o !== undefined && Math.abs(o - d.outer) < .07; };
    // the openings on this wall: the door, and the windows of the same house in its plane -- (u, y) boxes, a margin round
    const holes = [[ -d.w / 2 - .12, d.w / 2 + .12, d.y - 1, d.y + d.h + (d.arched ? .45 : .18)]];   // (over an arch: its keystone and voussoirs too)
    for (const w of windows) {
      if (Math.abs(w.cx - d.cx) + Math.abs(w.cz - d.cz) > .5) continue;
      const ox = w.x - mx, oz = w.z - mz;
      if (Math.abs(ox * nx + oz * nz) > .6) continue;   // (another wall of the house)
      const u = ox * ax + oz * az;
      holes.push([u - w.w / 2 - .12, u + w.w / 2 + .12, w.y - w.h / 2 - .2, w.y + w.h / 2 + .18]);
    }
    if (d.lamp) holes.push([d.w / 2 + .08, d.w / 2 + .75, d.y + 1.85, d.y + 2.8]);   // (the wall lamp beside it: nightglow.js, .38 past the jamb, 2.3 m up)
    const inHole = (u, y) => holes.some(([a, b, c, e]) => u > a && u < b && y > c && y < e);
    // how far the face runs either way (at a metre up: the probe steps out from the root until the wall ends) and how
    // high over the root (an opening above is gone round, not an end)
    let lo = u0, hi = u0;
    while (hi - u0 < IVY.reach && (wallHas(hi + IVY.probe, gy + 1) || inHole(hi + IVY.probe, gy + 1))) hi += IVY.probe;
    while (u0 - lo < IVY.reach && (wallHas(lo - IVY.probe, gy + 1) || inHole(lo - IVY.probe, gy + 1))) lo -= IVY.probe;
    let top = gy + .5;
    while (top - gy < IVY.top && (wallHas(u0, top + IVY.probe) || inHole(u0, top + IVY.probe))) top += IVY.probe;
    top -= .25; lo += .1; hi -= .1;
    if (top - gy < 1.5 || hi - lo < .6) continue;   // (too little wall)
    // (the top ragged: a little lower here and there along the wall, so the growth does not end on a ruled line)
    const ph = r() * 6.28, topAt = (u) => top - .3 * (.5 + .5 * Math.sin(u * 3.1 + ph)) - .15 * (.5 + .5 * Math.sin(u * 7.3 + ph * 2));
    const free = (u, y) => u > lo && u < hi && y > gy + .02 && y < topAt(u) && !inHole(u, y);
    // THE STEMS: a walk up the wall from the root, wandering, turned back up as it climbs; branching off to the sides
    // (and they up in turn); a stem that meets an opening or the wall's end tries to turn, and ends if it cannot
    const hue = Math.floor(r() * IVY.green.length);
    let nLeaves = 0;
    const stems = [[u0, gy, Math.PI / 2 + (r() - .5) * .3, IVY.branch.len[0] * lerp(.8, 1.3, r()) * (top - gy) / 3, 0]];
    while (stems.length && nLeaves < IVY.leaves) {
      let [u, y, ang, len, depth] = stems.shift();
      const pts = [[u, y]];
      const want = depth === 0 ? Math.PI / 2 : ang > Math.PI / 2 ? Math.PI * .7 : Math.PI * .3;   // (the trunk up; a branch up and out)
      for (let s = 0, n = Math.ceil(len / IVY.step); s < n; s++) {
        ang += (r() - .5) * .6 + (want - ang) * .12;
        let nu = u + Math.cos(ang) * IVY.step, ny = y + Math.sin(ang) * IVY.step;
        if (!free(nu, ny)) {
          if (ny >= topAt(nu)) break;   // (at the top it ends, it does not run along under it)
          const turn = [.7, -.7, 1.3, -1.3].find((t) => free(u + Math.cos(ang + t) * IVY.step, y + Math.sin(ang + t) * IVY.step));
          if (turn === undefined) break;
          ang += turn; nu = u + Math.cos(ang) * IVY.step; ny = y + Math.sin(ang) * IVY.step;
        }
        u = nu; y = ny; pts.push([u, y]);
        if (depth < IVY.branch.len.length - 1 && r() < IVY.branch.p * (depth ? .7 : 1))
          stems.push([u, y, ang + (r() < .5 ? -1 : 1) * lerp(.7, 1.3, r()), IVY.branch.len[depth + 1] * lerp(.6, 1.3, r()), depth + 1]);
      }
      if (pts.length < 3) continue;
      // the stem: a thin strip on the wall, thicker at the root
      for (let i = 0; i < pts.length - 1; i++) {
        const [ua, ya] = pts[i], [ub, yb] = pts[i + 1], L = Math.hypot(ub - ua, yb - ya) || 1;
        const wd = (depth ? .006 : .016 * (1 - i / pts.length) + .006), pu = -(yb - ya) / L * wd, py = (ub - ua) / L * wd;
        const o = SP.length / 3;
        for (const [uu, yy] of [[ua - pu, ya - py], [ua + pu, ya + py], [ub + pu, yb + py], [ub - pu, yb - py]]) { SP.push(...W(uu, yy, .008)); SN.push(nx, 0, nz); SC.push(stemCol.r, stemCol.g, stemCol.b); }
        SI.push(o, o + 1, o + 2, o, o + 2, o + 3);
      }
      // the leaves along it, on alternate sides, each on its stalk's end off the wall, tilted a little down and aside
      const every = Math.max(1, Math.round(IVY.leaf.every / IVY.step));
      for (let i = 1; i < pts.length && nLeaves < IVY.leaves; i += every) {
        const [u, y] = pts[i], [pu, py] = pts[i - 1], su = u - pu, sy = y - py, sL = Math.hypot(su, sy) || 1;
        const alt = (i / every) % 2 ? 1 : -1, tipT = i / pts.length;
        const age = (1 - tipT) * (1 - depth * .25), size = lerp(IVY.leaf.size[0], IVY.leaf.size[1], Math.min(1, age + r() * .3));
        // the leaf's tip: out to its side of the stem and upward-ish, in the wall's plane; then tipped out from it
        let tu = -sy / sL * alt * .8 + (r() - .5) * .6, ty = su / sL * alt * .8 + .5 + (r() - .3) * .5;
        const tl = Math.hypot(tu, ty) || 1; tu /= tl; ty /= tl;
        const out = lerp(IVY.leaf.out[0], IVY.leaf.out[1], r()), tilt = .35 + r() * .5;   // (how far the blade leans off the wall)
        const cu = u + (-sy / sL) * alt * .015, cy = y + (su / sL) * alt * .015;   // (the stalk's end, a little off the stem)
        if (!free(cu + tu * size * .5, cy + ty * size * .5)) continue;
        // the blade's frame: e1 to its tip (in the wall's plane, leaning out by `tilt`), e2 across it, nn its face
        const e1 = [ax * tu * Math.cos(tilt) + nx * Math.sin(tilt) * .4, ty * Math.cos(tilt), az * tu * Math.cos(tilt) + nz * Math.sin(tilt) * .4];
        const e2 = [ax * ty - 0, -tu, az * ty];
        const nn = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]];
        const nl = Math.hypot(...nn) || 1, fl = nn[0] * nx + nn[2] * nz < 0 ? -1 : 1;
        const [bx, by, bz] = W(cu, cy, out);
        leafCol.set(IVY.green[(hue + Math.floor(r() * 3)) % IVY.green.length]).lerp(young, Math.max(0, tipT - .8) * 4 * (r() * .5 + .5));
        const o = LP.length / 3, mid = [bx + e1[0] * size * .32, by + e1[1] * size * .32, bz + e1[2] * size * .32];
        LP.push(...mid); LN.push(nn[0] / nl * fl, nn[1] / nl * fl, nn[2] / nl * fl); LC.push(leafCol.r * 1.12, leafCol.g * 1.12, leafCol.b * 1.12); LF.push(.35);
        for (const [x, yy] of OUTLINE) {
          LP.push(bx + (e2[0] * x + e1[0] * yy) * size, by + (e2[1] * x + e1[1] * yy) * size, bz + (e2[2] * x + e1[2] * yy) * size);
          LN.push(nn[0] / nl * fl, nn[1] / nl * fl, nn[2] / nl * fl); LC.push(leafCol.r, leafCol.g, leafCol.b); LF.push(Math.max(0, yy));
        }
        for (let k = 0; k < OUTLINE.length; k++) LI.push(o, o + 1 + k, o + 1 + (k + 1) % OUTLINE.length);
        nLeaves++;
      }
    }
    if (nLeaves) { plants++; roots.push({ x: rx, y: gy, z: rz, nx, nz, top, leaves: nLeaves, arched: d.arched }); }
  }
  const U = { t: uniform(0) };
  if (!plants) return { count: 0, roots, update() {} };
  const geo = (P, N, C, I) => { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(P, 3)); g.setAttribute("normal", new THREE.Float32BufferAttribute(N, 3)); g.setAttribute("color", new THREE.Float32BufferAttribute(C, 3)); g.setIndex(I); g.computeBoundingSphere(); return g; };
  const lg = geo(LP, LN, LC, LI);
  lg.setAttribute("flex", new THREE.Float32BufferAttribute(LF, 1));
  const lm = snowyLit(); lm.side = THREE.DoubleSide;
  // (the leaves' tips stir: along their faces, by the wind where they are -- their stalks' ends stay)
  lm.positionNode = positionGeometry.add(normalGeometry.mul(windAt({ p: positionGeometry.xz, t: U.t }).mul(.02).mul(attribute("flex", "float"))));
  const leaves = new THREE.Mesh(lg, lm), sm = snowyLit(); sm.side = THREE.DoubleSide;
  const stems = new THREE.Mesh(geo(SP, SN, SC, SI), sm);
  leaves.name = "ivy"; stems.name = "ivy stems";
  for (const m of [leaves, stems]) { m.userData.noMerge = true; scene.add(m); }
  return { count: plants, roots, leaves: LP.length / 27, update(t) { U.t.value = t; } };
}
