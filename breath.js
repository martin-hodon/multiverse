// BREATH ON A COLD DAY: people near you breathe out little clouds of steam every few seconds -- a puff from the mouth,
// carried a hand's breadth forward and up, swelling and gone in a second and a half. A pool of puffs (the oldest
// reused); each is placed on the GPU from its own start, place and heading.
//
//   const breath = createBreath(scene)
//   breath.puff(x, y, z, dirX, dirZ, t)   // a breath out of a mouth at x, y, z, facing dirX, dirZ
//   breath.update(t)
// The pool is any soft PUFF -- breath is one kind, the dust a cart's wheels kick up on a dry road another (index.html):
//   createPuffs(scene, { pool, life, colour, size: [at first, at last], out, rise, opacity, name })
import * as THREE from "three";
import { attribute, uniform, vec3, vec4, float, uv, smoothstep, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";

export const BREATH = { pool: 64, life: 1.5, colour: [.93, .95, .97], size: [.06, .38], out: .32, rise: .18, opacity: .5, name: "breath" };
export const createBreath = (scene) => createPuffs(scene, BREATH);

export function createPuffs(scene, P) {
  const N = P.pool, at = new Float32Array(N * 16), dir = new Float32Array(N * 8), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); at.set([0, -1e4, 0, -1e4], (i * 4 + v) * 4); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aAt = new THREE.BufferAttribute(at, 4), aDir = new THREE.BufferAttribute(dir, 2);
  aAt.setUsage(THREE.DynamicDrawUsage); aDir.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("puffAt", aAt); g.setAttribute("puffDir", aDir);
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0) };
  const A = attribute("puffAt", "vec4"), D = attribute("puffDir", "vec2"), C = attribute("corner", "vec2");
  const age = U.t.sub(A.w), k = age.div(P.life).clamp(0, 1);
  const out = k.pow(.5).mul(P.out);                             // (out fast, then hanging)
  const at3 = A.xyz.add(vec3(D.x.mul(out), k.mul(P.rise), D.y.mul(out)));
  const size = k.pow(.6).mul(P.size[1] - P.size[0]).add(P.size[0]);
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(at3, 1)).add(vec4(C.mul(size), 0, 0)));
  const d = uv().sub(.5).mul(2).length();
  mat.colorNode = vec3(...P.colour);
  mat.opacityNode = smoothstep(1, .2, d).mul(smoothstep(0, .1, k)).mul(smoothstep(1, .35, k)).mul(P.opacity).mul(age.greaterThan(0).select(float(1), float(0)));
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = P.name; mesh.renderOrder = 4; mesh.visible = false;
  scene.add(mesh);
  let next = 0, last = -1e9;
  return {
    puff(x, y, z, dx, dz, t) {
      const i = next++ % N;
      for (let v = 0; v < 4; v++) { at.set([x, y, z, t], (i * 4 + v) * 4); dir.set([dx, dz], (i * 4 + v) * 2); }
      aAt.needsUpdate = true; aDir.needsUpdate = true;
      last = t; mesh.visible = true;
    },
    update(t) { U.t.value = t; if (t - last > P.life + .2) mesh.visible = false; },
  };
}
