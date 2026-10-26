// ICICLES (2026-10-24): in winter, while snow lies (foliage.js SNOW), icicles hang along the houses' eaves -- under the
// level roof edges (architecture.js lifeOf roofEdges, the same lines the fascia boards hang from: windowframes.js), a
// board's depth down, every few hands' breadth, long and short, thicker where they are long. Not up the gables' verges.
// One lit mesh for the town, shown only in winter. (And the SWALLOWS' NESTS under some eaves, all year: their own mesh.)
//
//   const icicles = createIcicles(scene, boards, { seed })   // boards: [{ cx, cz, edges: [[x0, y0, z0, x1, y1, z1]...] }]
//   icicles.update()                                         // shown while the snow lies
import * as THREE from "three";
import { litMaterial } from "./light.js";
import { SNOW } from "./foliage.js";
import { FRAME } from "./windowframes.js";
import { rng } from "./flora.js";

// every: metres between two along an eave (jittered); len: their length [min, max]; r: the root's radius at the
// longest; level: how much an edge may climb over its length and still be an eave; skip: the share of places left bare
export const ICICLES = { every: .2, len: [.07, .55], r: .04, level: .05, skip: .25, colour: "#dcebf5", sides: 5,
                         nest: { share: .33, r: .09, back: .1, colour: "#7d6a52" } };   // (nest: the swallows' -- its eaves' share, radius, how far in from the eave line, its mud)

export function createIcicles(scene, boards, { seed = 1 } = {}) {
  const r = rng(seed * 79 + 13), P = [], N = [], C = [], I = [], c = new THREE.Color(ICICLES.colour), tip = c.clone().multiplyScalar(1.08);
  let n = 0, nests = 0;
  for (const h of boards) for (const [x0, y0, z0, x1, y1, z1] of h.edges) {
    const L = Math.hypot(x1 - x0, z1 - z0);
    if (L < .5 || Math.abs(y1 - y0) > ICICLES.level * L) continue;   // (a verge climbs: no icicles up a gable)
    const y = (y0 + y1) / 2 - FRAME.board.h + .02;   // (from the board's lower edge)
    for (let d = r() * ICICLES.every; d < L; d += ICICLES.every * (.6 + r() * .8)) {
      if (r() < ICICLES.skip) continue;
      const t = d / L, x = x0 + (x1 - x0) * t, z = z0 + (z1 - z0) * t;
      const len = ICICLES.len[0] + (ICICLES.len[1] - ICICLES.len[0]) * r() ** 1.8, rr = ICICLES.r * (.45 + .55 * len / ICICLES.len[1]);
      // a cone down: a ring at the root, the tip below it (a little off plumb)
      const o = P.length / 3, S = ICICLES.sides, tx = x + (r() - .5) * .02, tz = z + (r() - .5) * .02, a0 = r() * 6.28;
      for (let k = 0; k < S; k++) {
        const a = a0 + k / S * Math.PI * 2, ca = Math.cos(a), sa = Math.sin(a);
        P.push(x + ca * rr, y, z + sa * rr); N.push(ca, .25, sa); C.push(c.r, c.g, c.b);
      }
      P.push(tx, y - len, tz); N.push(0, -1, 0); C.push(tip.r, tip.g, tip.b);
      for (let k = 0; k < S; k++) I.push(o + k, o + S, o + (k + 1) % S);
      n++;
    }
  }
  // SWALLOWS' NESTS (all year): a mud cup tucked under an eave here and there -- a half bowl against the wall's top, under
  // the board, on one eave in three, one to three of them
  const mud = new THREE.Color(ICICLES.nest.colour), NP = [], NN = [], NC = [], NI = [];
  for (const h of boards) for (const [x0, y0, z0, x1, y1, z1] of h.edges) {
    const L = Math.hypot(x1 - x0, z1 - z0);
    if (L < 3 || Math.abs(y1 - y0) > ICICLES.level * L || r() > ICICLES.nest.share) continue;
    const ux = (x1 - x0) / L, uz = (z1 - z0) / L;
    let ox = -uz, oz = ux; if (ox * ((x0 + x1) / 2 - h.cx) + oz * ((z0 + z1) / 2 - h.cz) < 0) { ox = -ox; oz = -oz; }   // (outward, away from the house's middle)
    for (let k = 0, m = 1 + Math.floor(r() * 3); k < m; k++) {
      const t = .15 + r() * .7, R = ICICLES.nest.r * (.85 + r() * .3), cx = x0 + (x1 - x0) * t - ox * ICICLES.nest.back, cz = z0 + (z1 - z0) * t - oz * ICICLES.nest.back;
      const cy = (y0 + y1) / 2 - FRAME.board.h - R * .2, o = NP.length / 3, S = 7, RS = 3;
      // a half bowl: rings down from its rim, the open side against the wall (the wall hides it)
      for (let j = 0; j <= RS; j++) for (let q = 0; q <= S; q++) {
        const v = j / RS * Math.PI / 2, a = q / S * Math.PI, ca = Math.cos(a), sa = Math.sin(a);
        const rr = R * Math.cos(v), dx = (ux * ca + ox * sa) * rr, dz = (uz * ca + oz * sa) * rr;
        NP.push(cx + dx, cy - R * Math.sin(v) * .9, cz + dz); NN.push(ux * ca * Math.cos(v) + ox * sa * Math.cos(v), -Math.sin(v), uz * ca * Math.cos(v) + oz * sa * Math.cos(v));
        const kk = .85 + .15 * Math.cos(v); NC.push(mud.r * kk, mud.g * kk, mud.b * kk);
      }
      for (let j = 0; j < RS; j++) for (let q = 0; q < S; q++) { const a0 = o + j * (S + 1) + q, b0 = a0 + S + 1; NI.push(a0, b0, a0 + 1, a0 + 1, b0, b0 + 1); }
      nests++;
    }
  }
  if (nests) {   // (their own mesh: the icicles' is shown in winter only)
    const ng = new THREE.BufferGeometry();
    ng.setAttribute("position", new THREE.Float32BufferAttribute(NP, 3)); ng.setAttribute("normal", new THREE.Float32BufferAttribute(NN, 3));
    ng.setAttribute("color", new THREE.Float32BufferAttribute(NC, 3)); ng.setIndex(NI); ng.computeBoundingSphere();
    const nm = new THREE.Mesh(ng, litMaterial({ side: THREE.DoubleSide })); nm.name = "swallow nests"; nm.userData.noMerge = true; scene.add(nm);
  }
  if (!n) return { count: 0, nests, update() {} };
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(N, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(C, 3));
  g.setIndex(I);
  g.computeBoundingSphere();
  const m = new THREE.Mesh(g, litMaterial({ side: THREE.DoubleSide }));
  m.name = "icicles"; m.userData.noMerge = true; m.visible = false;
  scene.add(m);
  return { count: n, nests, mesh: m, update() { m.visible = SNOW.value > .5; } };
}
