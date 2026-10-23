// THE MAYPOLE: in spring a tall pole stands on the children's green, a wreath of leaves and flowers at its top and a
// ribbon for each child running down from under the wreath to their hand as they dance round it. The pole and the
// wreath are blocks (blocks.js); the ribbons a strip each, re-laid every frame from the top to the hand it is held in
// -- sagging a little, fluttering, in the colours of a spring fair.
//
//   const pole = createMaypole(scene, { at: [x, y, z], ribbons: n })
//   pole.update(t, hands)   // hands: [[x, y, z]...] where each ribbon is held (null: let go -- it hangs down the pole)
//   pole.visible = true / false
import * as THREE from "three";
import { blockMesh } from "./blocks.js";

export const MAYPOLE = { height: 6.5, segs: 8, width: .06, colours: [[.85, .2, .2], [.95, .8, .2], [.25, .45, .85], [.95, .95, .95], [.3, .65, .3], [.85, .45, .7]] };

export function createMaypole(scene, { at: [x, y, z], ribbons = 6 }) {
  const H = MAYPOLE.height, group = new THREE.Group();
  group.name = "maypole";
  // the pole (a log stood on end: blocks' log along x, tilted up), the wreath of greenery and flowers round its top
  const B = [{ at: [x, y + H / 2, z], size: [H, .16, .16], tilt: Math.PI / 2, shape: "log", colour: [.78, .72, .6], ends: [.8, .75, .62] }];
  for (let k = 0; k < 14; k++) {
    const a = k / 14 * Math.PI * 2, flower = k % 2;
    B.push({ at: [x + Math.cos(a) * .32, y + H - .55 + (flower ? .04 : 0), z + Math.sin(a) * .32], size: flower ? [.12, .12, .12] : [.2, .2, .2], shape: "ball",
             colour: flower ? MAYPOLE.colours[k % MAYPOLE.colours.length] : [.3, .55, .25] });
  }
  B.push({ at: [x, y + H + .08, z], size: [.22, .22, .22], shape: "ball", colour: [.95, .85, .3] });   // (a gilded knob)
  group.add(blockMesh(B, "maypole wood"));
  // the ribbons: a strip of MAYPOLE.segs quads each, both sides the same colour
  const S = MAYPOLE.segs, n = ribbons, pos = new Float32Array(n * (S + 1) * 2 * 3), col = new Float32Array(n * (S + 1) * 2 * 3), idx = [];
  for (let r = 0; r < n; r++) {
    const c = MAYPOLE.colours[r % MAYPOLE.colours.length].map((v) => v ** 2.2);
    for (let i = 0; i <= S; i++) for (let e = 0; e < 2; e++) col.set(c, ((r * (S + 1) + i) * 2 + e) * 3);
    for (let i = 0; i < S; i++) { const a = (r * (S + 1) + i) * 2; idx.push(a, a + 1, a + 3, a, a + 3, a + 2); }
  }
  const g = new THREE.BufferGeometry();
  const aPos = new THREE.BufferAttribute(pos, 3); aPos.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", aPos); g.setAttribute("color", new THREE.BufferAttribute(col, 3)); g.setIndex(idx);
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(x, y + H / 2, z), H);
  const strips = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));
  strips.name = "maypole ribbons"; strips.userData.noMerge = true;
  group.add(strips);
  group.visible = false;
  scene.add(group);
  const top = [x, y + H - .7, z];
  return {
    group,
    get visible() { return group.visible; }, set visible(v) { group.visible = v; },
    update(t, hands) {
      for (let r = 0; r < n; r++) {
        // from just under the wreath (its own side of the pole) to the hand -- or, let go, straight down the pole
        const a0 = r / n * Math.PI * 2, sx = top[0] + Math.cos(a0) * .1, sz = top[2] + Math.sin(a0) * .1;
        const h = hands[r] ?? [sx, y + .4, sz];
        const dx = h[0] - sx, dz = h[2] - sz, L = Math.hypot(dx, dz) || 1, nx = -dz / L, nz = dx / L;   // (across the ribbon, level)
        for (let i = 0; i <= S; i++) {
          const u = i / S, sag = Math.sin(u * Math.PI) * .25, flap = Math.sin(t * 7 + r * 1.7 + u * 6) * .06 * u;
          const px = sx + dx * u + nx * flap, py = top[1] + (h[1] - top[1]) * u - sag, pz = sz + dz * u + nz * flap;
          const w = MAYPOLE.width / 2, o = ((r * (S + 1) + i) * 2) * 3;
          pos.set([px - nx * w, py + .02, pz - nz * w, px + nx * w, py - .02, pz + nz * w], o);
        }
      }
      aPos.needsUpdate = true;
    },
  };
}
