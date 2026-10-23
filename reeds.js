// REEDS along the water's edge: clumps of tall blades and cattails where the bank runs into the shallows -- in the first
// half metre of water and just above it -- leaning and swaying with the grass's wind, greener in summer, straw-gold in
// autumn. Each clump is a few crossed cards whose blades are cut in the shader (tapering leaves, the cattail's brown
// head on a stalk). One mesh for all the banks.
//
//   const reeds = createReeds(scene, { at, seed })   // at(r): a place at the water's edge ({ x, y, z } or null), r random
//   reeds.update(t, { autumn })
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec3, vec4, float, uv, sin, fract, floor, smoothstep, mix, step, abs, max, positionGeometry, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { windAt } from "./grass.js";
import { rng } from "./flora.js";

export const REEDS = { clumps: 900, cards: 3, width: [.6, 1.2], height: [1.2, 2.1] };

export function createReeds(scene, { at, seed = 1 }) {
  const r = rng(seed * 37 + 11);
  const pos = [], uvs = [], sd = [], idx = [];
  let n = 0;
  for (let tries = 0; n < REEDS.clumps && tries < REEDS.clumps * 6; tries++) {
    const c = at(r);
    if (!c) continue;
    n++;
    const w = REEDS.width[0] + r() * (REEDS.width[1] - REEDS.width[0]), h = REEDS.height[0] + r() * (REEDS.height[1] - REEDS.height[0]), s = r();
    for (let k = 0; k < REEDS.cards; k++) {
      const a = r() * Math.PI + k * Math.PI / REEDS.cards, ax = Math.cos(a) * w / 2, az = Math.sin(a) * w / 2, o = pos.length / 3;
      for (const [u, v] of [[0, 0], [1, 0], [1, 1], [0, 1]]) {
        pos.push(c.x + ax * (u * 2 - 1), c.y - .05 + v * h, c.z + az * (u * 2 - 1));
        uvs.push(u, v); sd.push(s + k * .37, h);
      }
      idx.push(o, o + 1, o + 2, o, o + 2, o + 3);
    }
  }
  if (!n) return { count: 0, update() {} };
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  g.setAttribute("seedA", new THREE.Float32BufferAttribute(sd, 2));
  g.setIndex(idx);
  const U = { t: uniform(0), autumn: uniform(0) };
  const S = attribute("seedA", "vec2"), P = positionGeometry, u = uv().x, v = uv().y;
  // the sway: the grass's own wind, more the higher up the blade
  const bend = windAt({ p: P.xz, t: U.t }).mul(.16).add(.1).mul(v.mul(v)).mul(S.y);
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P.add(vec3(bend.mul(.31), bend.abs().mul(-.15), bend.mul(.95))), 1)));
  // the blades: five to a card, each a tapering leaf of its own height and lean; every fourth one a cattail -- a bare
  // stalk with its sausage-brown head
  const lanes = float(5), i = floor(u.mul(lanes)), fu = fract(u.mul(lanes)), h1 = fract(sin(i.mul(12.989).add(S.x.mul(78.2))).mul(43758.5));
  const top = h1.mul(.35).add(.6), lean = h1.sub(.5).mul(.6).mul(v);
  const x = fu.sub(.5).sub(lean), wide = smoothstep(top, 0, v).mul(.6).add(.06);
  const blade = step(abs(x), wide.mul(.5)).mul(step(v, top));
  const cat = step(.75, fract(h1.mul(7.3)));
  const stalk = step(abs(x), .06).mul(step(v, top.add(.25)));
  const head = step(abs(x), .17).mul(step(top.add(.06), v)).mul(step(v, top.add(.2)));
  const shape = mix(blade, max(stalk, head).max(blade.mul(step(v, top.mul(.6)))), cat);
  const green = mix(vec3(.16, .3, .09), vec3(.32, .45, .15), v.mul(.6).add(h1.mul(.3)));
  const straw = mix(vec3(.55, .45, .22), vec3(.75, .64, .36), v.mul(.6).add(h1.mul(.3)));
  const leafCol = mix(green, straw, U.autumn);
  const headCol = vec3(.22, .13, .06);
  mat.colorNode = mix(leafCol, headCol, cat.mul(head));
  mat.opacityNode = shape;
  mat.alphaTest = .5;
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, null, 1); mesh.name = "reeds"; mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  return { count: n, update(t, { autumn = 0 } = {}) { U.t.value = t; U.autumn.value = Math.min(1, autumn); } };
}
