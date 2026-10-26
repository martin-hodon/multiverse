// WINDOW FRAMES (2026-10-24): a window was a bare hole in the plaster with a shutter beside it. Now each has a frame on
// the wall's outer face -- two jambs and a lintel standing a little proud, and a sill under it reaching further out
// (where the flower boxes sit: windowbox.js) -- in one colour a house: oak or weathered timber, or painted (green,
// blue-grey, oxblood, white), pale stone round glass (a merchant's or a palace's windows). An arched window (its pane
// shaped to the head) gets its sill and a keystone at its crown. A flat-headed DOORWAY gets jambs and a lintel in its
// house's colour, an arched one a keystone, and either a stone step where its sill stands over the street. A house's
// ROOF EDGES get boards (bargeboards, fascias). One lit mesh for the whole town (snowyLit: it takes the snow and the wet).
//
//   createWindowFrames(scene, windows, { seed, doors, boards, groundH })
//     windows: the glow's list [{ x, y, z, w, h, base, cx, cz, glazed, outer, rec }]
//     doors: [{ x, y (its floor), z, w, h, base, cx, cz, outer, arched }]
//     boards: [{ cx, cz, edges: [[x0, y0, z0, x1, y1, z1]...] }] (a house's roof edges)
//     groundH: (x, z) => the ground's height (for the doorsteps)
//   -> { count, mesh }
import * as THREE from "three";
import { litMaterial } from "./light.js";
import { SNOW } from "./foliage.js";
import { uniform, renderGroup, normalWorld, smoothstep, mix, vec3, float } from "three/tsl";
import { WET } from "./cloudshadow.js";
import { rng } from "./flora.js";

// A LIT MATERIAL THAT TAKES THE SNOW (the frames' sills and lintels, the roofs' ridge tiles, the chimneys' caps, the
// woodpiles): its faces looking up whiten as the snow lies (foliage.js SNOW, as the roofs under it -- a bare terracotta
// ridge on a white roof read as a stripe)
// ...and DARKENS WET after rain, as the walls and roofs do (cloudshadow.js WET: archmat's finishShade)
export function snowyLit() {
  const m = litMaterial(), base = m.colorNode;
  const snow = uniform(0).setGroup(renderGroup).onRenderUpdate(() => SNOW.value);
  const wet = WET.mul(mix(float(.15), float(.3), smoothstep(.2, .7, normalWorld.y)));
  m.colorNode = mix(base.mul(float(1).sub(wet)), vec3(.93, .94, .97), smoothstep(.35, .75, normalWorld.y).mul(snow.min(1)));
  return m;
}

// the frame's jamb width and how proud it stands, the sill's height, reach and overhang past the jambs, the lintel's
// height; a roof edge's board (deep, thick); a keystone's width and height; a doorstep's depth
export const FRAME = { w: .09, proud: .03, sill: { h: .08, out: .12, past: .07 }, lintel: .12, board: { h: .2, t: .035 }, key: { w: .2, h: .28 }, step: { d: .38 } };
const PAINT = ["#5b4330", "#4a3626", "#6b5a48", "#5b4330", "#3f5a46", "#4b5d6e", "#6e2f24", "#e6dfcc"];   // (oak twice: the commonest)
const STONE = "#cfc5ae";

// an opening's wall: along it (ax, az), out of the building (nx, nz), and the point `out` metres off the wall's outer
// face in front of its middle (o: { x, z, base, cx, cz, outer } -- a window or a door of the glow's and frames' lists;
// index.html's woodpiles stand by it too)
export function wallFrame(o) {
  const ax = Math.cos(o.base), az = -Math.sin(o.base);
  let nx = az, nz = -ax; if (nx * (o.x - o.cx) + nz * (o.z - o.cz) < 0) { nx = -nx; nz = -nz; }
  return { ax, az, nx, nz, at: (out) => [o.x + nx * (o.outer + out), o.z + nz * (o.outer + out)] };
}
export function createWindowFrames(scene, windows, { seed = 1, doors = [], boards = [], groundH = null } = {}) {
  const r = rng(seed * 53 + 11), house = new Map();
  const P = [], N = [], C = [], I = [], c = new THREE.Color();
  // a box on the wall: its middle (x, y, z), half sizes along the wall (u), up (v) and out of it (n); its top lighter
  const box = (x, y, z, ax, az, nx, nz, u, v, n, col) => {
    const flip = -az * nx + ax * nz > 0;   // (the faces below are wound for a left-handed along-up-out frame: on a wall where it is right-handed, the other way)
    const corner = (s, t, q) => [x + ax * u * s + nx * n * q, y + v * t, z + az * u * s + nz * n * q];
    const faces = [[[1, 0, 0], [[1, -1, -1], [1, -1, 1], [1, 1, 1], [1, 1, -1]]], [[-1, 0, 0], [[-1, -1, 1], [-1, -1, -1], [-1, 1, -1], [-1, 1, 1]]],
                   [[0, 1, 0], [[-1, 1, -1], [1, 1, -1], [1, 1, 1], [-1, 1, 1]]], [[0, -1, 0], [[-1, -1, 1], [1, -1, 1], [1, -1, -1], [-1, -1, -1]]],
                   [[0, 0, 1], [[1, -1, 1], [-1, -1, 1], [-1, 1, 1], [1, 1, 1]]], [[0, 0, -1], [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]]]];
    for (const [[fs, ft, fq], cs] of faces) {
      const o = P.length / 3, k = ft > 0 ? 1.1 : ft < 0 ? .8 : 1;
      for (const [s, t, q] of cs) { P.push(...corner(s, t, q)); N.push(ax * fs + nx * fq, ft, az * fs + nz * fq); C.push(col.r * k, col.g * k, col.b * k); }
      if (flip) I.push(o, o + 2, o + 1, o, o + 3, o + 2); else I.push(o, o + 1, o + 2, o, o + 2, o + 3);
    }
  };
  let count = 0;
  // (a house's colour, drawn the first time one of its openings asks; the wall's way out at an opening)
  const colourOf = (o) => { const k = `${o.cx.toFixed(1)},${o.cz.toFixed(1)}`; if (!house.has(k)) house.set(k, PAINT[Math.floor(r() * PAINT.length)]); return house.get(k); };
  const frameAt = wallFrame;
  for (const w of windows) {
    if (w.outer === undefined) continue;   // (no wall face found round it: nothing to stand on)
    c.set(w.glazed ? STONE : colourOf(w));
    const { ax, az, nx, nz, at } = frameAt(w), F = FRAME, hw = w.w / 2, hh = w.h / 2;
    // the sill: under the opening, wider than it, reaching out over the wall below
    const [sx, sz] = at(F.sill.out / 2 - .01);
    box(sx, w.y - hh - F.sill.h / 2, sz, ax, az, nx, nz, hw + F.w + F.sill.past, F.sill.h / 2, F.sill.out / 2, c);
    if (w.rec?.geo) {   // (an arched head: a keystone at its crown, a little proud, in pale stone)
      const [kx, kz] = at(F.proud / 2), ks = new THREE.Color(STONE).multiplyScalar(1.05);
      box(kx, w.y + hh - FRAME.key.h * .25, kz, ax, az, nx, nz, FRAME.key.w / 2, FRAME.key.h / 2, F.proud / 2 + .01, ks);
    }
    if (!w.rec?.geo) {   // (a flat head: the jambs up its sides and a lintel over it)
      const [fx, fz] = at(F.proud / 2 - .005);
      for (const s of [-1, 1]) box(fx + ax * s * (hw + F.w / 2), w.y, fz + az * s * (hw + F.w / 2), ax, az, nx, nz, F.w / 2, hh, F.proud / 2, c);
      box(fx, w.y + hh + F.lintel / 2, fz, ax, az, nx, nz, hw + F.w + .03, F.lintel / 2, F.proud / 2 + .005, c);
    }
    count++;
  }
  // BOARDS along a roof's open edges (architecture.js lifeOf roofEdges: its eaves and its gables' verges): a plank
  // hanging under each, upright, in the house's paint -- a bargeboard up a gable, a fascia along the eaves
  for (const h of boards) {
    c.set(colourOf(h));
    for (const [x0, y0, z0, x1, y1, z1] of h.edges) {
      const dx = x1 - x0, dz = z1 - z0, L = Math.hypot(dx, dz);
      if (L < .1) continue;
      const ax = dx / L, az = dz / L, nx = az, nz = -ax, T = FRAME.board.t / 2, Hh = FRAME.board.h;
      const o = P.length / 3, flip = false;
      // (eight corners: along the edge a..b, down by the board's depth, either side by its thickness)
      const corner = (t, down, side) => [x0 + dx * t + nx * T * side, (y0 + (y1 - y0) * t) - down * Hh + .01, z0 + dz * t + nz * T * side];
      const faces = [[[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1], nx, 0, nz], [[1, 0, -1], [0, 0, -1], [0, 1, -1], [1, 1, -1], -nx, 0, -nz],
                     [[0, 1, 1], [1, 1, 1], [1, 1, -1], [0, 1, -1], 0, -1, 0]];
      for (const [p0, p1, p2, p3, fx, fy, fz] of faces) {
        const b = P.length / 3;
        for (const q of [p0, p1, p2, p3]) { P.push(...corner(...q)); N.push(fx, fy, fz); C.push(c.r * (fy < 0 ? .75 : 1), c.g * (fy < 0 ? .75 : 1), c.b * (fy < 0 ? .75 : 1)); }
        I.push(b, b + 2, b + 1, b, b + 3, b + 2, b, b + 1, b + 2, b, b + 2, b + 3);   // (both windings: a board is seen from either side)
      }
      count++;
    }
  }
  const step = new THREE.Color(STONE).multiplyScalar(.82);
  // a DOORSTEP of stone where the sill stands above the street: a slab out in front, from the ground to the sill
  const doorstep = (d, { ax, az, nx, nz, at }, F) => {
    if (!groundH) return;
    const [sx, sz] = at(F.step.d / 2), gy = groundH(sx, sz), rise = d.y - gy;
    if (rise > .05 && rise < .5) box(sx, gy + rise / 2 - .02, sz, ax, az, nx, nz, d.w / 2 + F.w + .06, rise / 2 + .02, F.step.d / 2, step);
  };
  for (const d of doors) {   // a doorway: its jambs from the floor up, and the lintel (an arched one: a keystone at its crown)
    if (d.outer === undefined) continue;
    if (d.arched) {
      const { ax, az, nx, nz, at } = frameAt(d), [kx, kz] = at(FRAME.proud / 2);
      box(kx, d.y + d.h - FRAME.key.h * .2, kz, ax, az, nx, nz, FRAME.key.w * .65, FRAME.key.h * .6, FRAME.proud / 2 + .01, new THREE.Color(STONE).multiplyScalar(1.05));
      doorstep(d, frameAt(d), FRAME); count++; continue;
    }
    c.set(colourOf(d));
    const { ax, az, nx, nz, at } = frameAt(d), F = FRAME, hw = d.w / 2, [fx, fz] = at(F.proud / 2 - .005);
    for (const s of [-1, 1]) box(fx + ax * s * (hw + F.w / 2), d.y + d.h / 2, fz + az * s * (hw + F.w / 2), ax, az, nx, nz, F.w / 2, d.h / 2, F.proud / 2, c);
    box(fx, d.y + d.h + F.lintel / 2, fz, ax, az, nx, nz, hw + F.w + .04, F.lintel / 2, F.proud / 2 + .005, c);
    doorstep(d, { ax, az, nx, nz, at }, F);
    count++;
  }
  if (!count) return { count: 0 };
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(N, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(C, 3));
  g.setIndex(I);
  g.computeBoundingSphere();
  const m = new THREE.Mesh(g, snowyLit());
  m.name = "window frames"; m.userData.noMerge = true;
  scene.add(m);
  return { count, mesh: m };
}
