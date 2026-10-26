// RIDGE CAPS (2026-10-24): a roof's ridge was the sharp line where its two slopes met. Now a row of half-round ridge
// tiles runs along it -- in the roof's own colour, a shade darker (the palette's second), each tile's lower end
// darker still where it laps over the next -- and on a thatched roof a thick rounded roll of straw, bound. From the
// ridges the buildings report (architecture.js lifeOf: `part`, the roof the finish rule covers -- index.html
// roofRuleOf); a hipped roof's HIPS (lifeOf roofHips) tiled up their slope as the ridge is; merlons and other perches
// (`share`) have none. Every chimney a capstone. One lit mesh for the town (snowyLit: it takes the snow and the wet).
//
//   createRidgeCaps(scene, ridges, { chimneys })   // ridges: [{ a: [x, z], b: [x, z], y (or ya, yb: a hip climbing), roof: { pattern, palette } | null }];
//                                                // chimneys: their tops' middles [{ x, y, z }] (each gets a capstone)
//   -> { count, mesh }
import * as THREE from "three";
import { snowyLit } from "./windowframes.js";
import { PALETTES } from "./patterns.js";

// tile: half-round tiles r across, `len` long; roll: a thatch's ridge; `sides` round the half
export const RIDGE = { tile: { r: .09, len: .38, lap: .7 }, roll: { r: .17, len: .9, lap: .85 }, sides: 6, drop: .35,
                       cap: { w: .92, t: .08, colour: "#8d8478", course: "#6a4a3c" } };   // (a chimney's capstone: its width, thickness, stone; the brick course under it)

export function createRidgeCaps(scene, ridges, { chimneys = [] } = {}) {
  const P = [], N = [], C = [], I = [], c = new THREE.Color();
  let count = 0;
  // A CHIMNEY'S CAP: a stone slab a little wider than the stack, laid on its top (the town's houses stand square to the
  // world, so their stacks do), and a course of brick under it a shade darker -- RIDGE.cap
  const slab = (x, y, z, hx, hy, hz, col) => {
    const o = P.length / 3;
    for (const [nx, ny, nz, cs] of [[1, 0, 0, [[1, -1, -1], [1, 1, -1], [1, 1, 1], [1, -1, 1]]], [-1, 0, 0, [[-1, -1, 1], [-1, 1, 1], [-1, 1, -1], [-1, -1, -1]]],
                                    [0, 1, 0, [[-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1]]], [0, -1, 0, [[-1, -1, 1], [-1, -1, -1], [1, -1, -1], [1, -1, 1]]],
                                    [0, 0, 1, [[1, -1, 1], [1, 1, 1], [-1, 1, 1], [-1, -1, 1]]], [0, 0, -1, [[-1, -1, -1], [-1, 1, -1], [1, 1, -1], [1, -1, -1]]]]) {
      const b = P.length / 3, k = ny > 0 ? 1.08 : ny < 0 ? .75 : 1;
      for (const [sx, sy, sz] of cs) { P.push(x + sx * hx, y + sy * hy, z + sz * hz); N.push(nx, ny, nz); C.push(col.r * k, col.g * k, col.b * k); }
      I.push(b, b + 1, b + 2, b, b + 2, b + 3);
    }
    return o;
  };
  const cap = new THREE.Color(RIDGE.cap.colour), course = new THREE.Color(RIDGE.cap.course);
  for (const ch of chimneys) {
    const h = RIDGE.cap.w / 2;
    slab(ch.x, ch.y + RIDGE.cap.t / 2 + .01, ch.z, h, RIDGE.cap.t / 2, h, cap);
    slab(ch.x, ch.y - .06, ch.z, h - .06, .07, h - .06, course);
    count++;
  }
  for (const rd of ridges) {
    if (rd.share || !rd.roof) continue;
    const thatch = /thatch/.test(rd.roof.pattern ?? ""), K = thatch ? RIDGE.roll : RIDGE.tile;
    const pal = PALETTES[rd.roof.palette] ?? null;
    c.set(pal ? pal[1] : "#7e4631");
    // (a ridge is level at rd.y; a HIP climbs from rd.ya to rd.yb -- its tiles follow it)
    const ya = rd.ya ?? rd.y, yb = rd.yb ?? rd.y;
    const dx = rd.b[0] - rd.a[0], dz = rd.b[1] - rd.a[1], L = Math.hypot(dx, dz, yb - ya);
    if (L < .5) continue;
    const hl = Math.hypot(dx, dz) || 1, tx = dx / hl, tz = dz / hl, sx = -tz, sz = tx;   // along it (level), and across it
    const n = Math.max(1, Math.round(L / K.len)), y0 = -K.r * RIDGE.drop;
    // each tile a half tube from one side of the ridge over to the other (a little past level, over the slopes), its
    // rings at its two ends: the near end lapped under the last one -- darker
    for (let k = 0; k < n; k++) {
      const t0 = k / n, t1 = (k + 1) / n, base = P.length / 3;
      for (const [t, shade] of [[t0, K.lap], [t1, 1]]) {
        const cx = rd.a[0] + dx * t, cz = rd.a[1] + dz * t, cy = ya + (yb - ya) * t;
        for (let j = 0; j <= RIDGE.sides; j++) {
          const ang = -.25 + (Math.PI + .5) * j / RIDGE.sides, ca = Math.cos(ang), sa = Math.sin(ang);   // (from one side, over the top, to the other)
          P.push(cx + sx * K.r * ca, cy + y0 + K.r * sa, cz + sz * K.r * ca);
          N.push(sx * ca, sa, sz * ca);
          const k2 = shade * (.86 + .14 * sa);
          C.push(c.r * k2, c.g * k2, c.b * k2);
        }
      }
      const R = RIDGE.sides + 1;
      for (let j = 0; j < RIDGE.sides; j++) {
        const a = base + j, b = base + j + 1, a2 = a + R, b2 = b + R;
        I.push(a, a2, b, b, a2, b2);
      }
    }
    count++;
  }
  if (!count) return { count: 0 };
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(N, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(C, 3));
  g.setIndex(I);
  g.computeBoundingSphere();
  const m = new THREE.Mesh(g, snowyLit());   // (wound outward: (a, a2, b) is along x round, which is out; the snow on them as on the roof)
  m.name = "ridge caps"; m.userData.noMerge = true;
  scene.add(m);
  return { count, mesh: m };
}
