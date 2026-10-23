// MOTHS round the lanterns at night: round each lit lantern near you a few pale moths flutter in erratic loops, now in
// close to the light, now out, catching it -- a tiny bright card each, beating. The lanterns are the frame's own list
// (index.html poseAll: the wall lamps, the lanterns carried, the watchman's, the skiff's); the CPU hands the nearest
// of them to the moths every frame, the loops and the flutter are the GPU's. In the night's glow scene, so they shine.
//
//   const moths = createMoths(glowScene)
//   moths.update(t, lamps, camera)   // lamps: [[x, y, z, groundY]...]; [] or null: none out
import * as THREE from "three";
import { attribute, uniform, vec2, vec3, vec4, float, sin, cos, uv, smoothstep, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";

export const MOTHS = { lamps: 10, per: 4, size: .045, near: 40 };

export function createMoths(scene) {
  const N = MOTHS.lamps * MOTHS.per, at = new Float32Array(N * 16), sd = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    const s = [Math.random(), Math.random(), Math.random(), Math.random()];
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); sd.set(s, (i * 4 + v) * 4); at.set([0, -1e4, 0, 0], (i * 4 + v) * 4); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aAt = new THREE.BufferAttribute(at, 4); aAt.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("lampAt", aAt);
  g.setAttribute("mothSeed", new THREE.BufferAttribute(sd, 4));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0) };
  const A = attribute("lampAt", "vec4"), S = attribute("mothSeed", "vec4"), C = attribute("corner", "vec2");
  // its loop round the light: two wandering angles and a radius that breathes in and out, jittered
  const t = U.t, a1 = t.mul(S.x.mul(2).add(1.5)).add(S.y.mul(40)), a2 = t.mul(S.z.mul(1.7).add(1.1)).add(S.w.mul(30));
  const r = sin(t.mul(S.w.mul(1.3).add(.7)).add(S.x.mul(9))).mul(.18).add(.38);
  const P = A.xyz.add(vec3(cos(a1).mul(r), sin(a2).mul(.22).add(.05), sin(a1).mul(r)))
    .add(vec3(sin(t.mul(23).add(S.y.mul(70))), sin(t.mul(19).add(S.z.mul(50))), sin(t.mul(29).add(S.w.mul(60)))).mul(.03));
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false });
  const beat = sin(t.mul(40).add(S.x.mul(80))).mul(.4).add(.8);
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P, 1)).add(vec4(C.mul(vec2(beat, 1).mul(MOTHS.size)).mul(A.w), 0, 0)));
  const d = uv().sub(.5).mul(2).length();
  mat.colorNode = vec3(1, .9, .7).mul(smoothstep(1, .2, d)).mul(.9).mul(A.w);
  mat.opacityNode = float(1);
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "moths"; mesh.visible = false;
  scene.add(mesh);
  const order = [];
  return {
    mesh,
    update(time, lamps, camera) {
      U.t.value = time;
      mesh.visible = !!lamps?.length;
      if (!mesh.visible) return;
      // the nearest lamps to you (within MOTHS.near), a few moths each
      order.length = 0;
      for (const L of lamps) { const dd = Math.hypot(L[0] - camera.position.x, L[2] - camera.position.z); if (dd < MOTHS.near) order.push([dd, L]); }
      order.sort((p, q) => p[0] - q[0]);
      for (let k = 0; k < MOTHS.lamps; k++) {
        const L = order[k]?.[1];
        for (let m = 0; m < MOTHS.per; m++) for (let v = 0; v < 4; v++) {
          const o = ((k * MOTHS.per + m) * 4 + v) * 4;
          if (L) at.set([L[0], L[1], L[2], 1], o); else at[o + 3] = 0;
        }
      }
      aAt.needsUpdate = true;
    },
  };
}
