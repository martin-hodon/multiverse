// RIVER MIST: as the evening cools, low banks of mist gather over the water -- soft, wide and flat, a man's height
// deep -- and drift slowly downstream through the night, thinning off at dawn. Each bank is one quad facing the eye,
// sliding along the river from its own place (its stretch: `run` metres, faded in at the start and out at the end, so
// the drift never jumps), its outline broken by slow lobes. All on the GPU from the time: one mesh, one draw, nothing
// touched per frame but the uniforms -- and hidden by day.
//
//   const mist = createMist(scene, banks, { seed })   // banks: [{ x, y, z, tx, tz, hw }] points on the river: the water's
//                                                     //   height, the way downstream, the half width
//   mist.update(t, { amount, light, camera })         // amount 0 none .. 1 a misty night; light the hour's (sky.js cloud)
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec2, vec3, vec4, float, uv, fract, sin, smoothstep, mix, clamp, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { rng } from "./flora.js";

export const MIST = { per: 3, run: 22, speed: .35, size: [[9, 16], [1.6, 2.6]], lift: .7, opacity: .27, near: [4, 14] };

export function createMist(scene, banks, { seed = 1 } = {}) {
  const r = rng(seed * 47 + 11), puffs = [];
  for (const b of banks) for (let k = 0; k < MIST.per; k++)
    puffs.push([b.x, b.y + MIST.lift * (.7 + r() * .6), b.z + (r() * 2 - 1) * b.hw * .6, b.tx, b.tz, r(), MIST.size[0][0] + r() * (MIST.size[0][1] - MIST.size[0][0]), MIST.size[1][0] + r() * (MIST.size[1][1] - MIST.size[1][0])]);
  if (!puffs.length) return { count: 0, update() {} };
  const N = puffs.length, at = new Float32Array(N * 16), sd = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  puffs.forEach(([x, y, z, tx, tz, ph, w, h], i) => {
    for (let v = 0; v < 4; v++) {
      at.set([x, y, z, ph], (i * 4 + v) * 4); sd.set([tx, tz, w, h], (i * 4 + v) * 4);
      cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2);
    }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("bank", new THREE.BufferAttribute(at, 4));
  g.setAttribute("bankSize", new THREE.BufferAttribute(sd, 4));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0), amount: uniform(0), light: uniform(new THREE.Color(1, 1, 1)) };
  const A = attribute("bank", "vec4"), S = attribute("bankSize", "vec4"), C = attribute("corner", "vec2");
  // its stretch: from `run`/2 upstream of its place to `run`/2 down, round and round, each bank at its own phase
  const f = fract(U.t.mul(MIST.speed / MIST.run).add(A.w));
  const P = A.xyz.add(vec3(S.x, 0, S.y).mul(f.sub(.5).mul(MIST.run)));
  const view = cameraViewMatrix.mul(vec4(P, 1));
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(view.add(vec4(C.mul(vec2(S.z, S.w)), 0, 0)));
  // the bank: a soft, wide oval, its top edge rolling in slow lobes; in and out at the ends of its stretch, and thin
  // close to the eye (so walking into it is a haze, not a wall)
  const q = uv().sub(.5).mul(2), ph = A.w.mul(40);
  const top = sin(q.x.mul(4).add(ph).add(U.t.mul(.15))).mul(.12).add(sin(q.x.mul(9).sub(ph.mul(.7))).mul(.06)).add(.75);
  const body = smoothstep(1, .25, vec2(q.x, q.y.mul(q.y.greaterThan(0).select(float(1).div(top), float(1)))).length());
  const life = smoothstep(0, .2, f).mul(smoothstep(1, .8, f));
  const near = smoothstep(MIST.near[0], MIST.near[1], view.z.negate());
  mat.colorNode = mix(U.light.mul(.86), U.light, clamp(q.y.mul(.5).add(.5), 0, 1));   // (a shade darker at the foot)
  mat.opacityNode = clamp(body.mul(life).mul(near).mul(U.amount).mul(MIST.opacity), 0, 1);
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, banks, MIST.run / 2 + MIST.size[0][1]); mesh.name = "river mist"; mesh.renderOrder = 3; mesh.visible = false;
  mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  return {
    count: N, mesh,
    update(t, { amount = 0, light } = {}) {
      U.t.value = t; U.amount.value = amount;
      if (light) U.light.value.copy(light);
      mesh.visible = amount > .01;
    },
  };
}
