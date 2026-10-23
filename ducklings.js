// DUCKLINGS: behind each duck on the water a line of three to five ducklings, paddling along in its wake -- each one
// where its mother was a moment before (the duck's own recent path, kept in a ring), bobbing on the ripples, closing
// up when she stops. Each is one card facing the eye: a duckling from the side, fluffy and round -- a dusky back, a
// yellow face and breast, a dark eye stripe, a little bill -- turned to the way it swims. One mesh, one draw; the
// cards are placed from the trail every frame (a few dozen points).
//
//   const ducklings = createDucklings(scene, mothers, { seed })   // mothers: [{ position, rotY }] (the ducks' figures)
//   ducklings.update(t, dt, { surface })                          // surface(x, z): the water's height there
import * as THREE from "three";
import { attribute, uniform, vec2, vec3, vec4, float, uv, sin, smoothstep, mix, max, step, abs, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { rng } from "./flora.js";

export const DUCKLINGS = { per: [3, 5], gap: .38, keep: .06, size: .2, ring: 160 };   // gap: metres between them along her wake; keep: metres between trail points

export function createDucklings(scene, mothers, { seed = 1 } = {}) {
  const r = rng(seed * 71 + 13), broods = [];
  for (const m of mothers) {
    const n = DUCKLINGS.per[0] + Math.floor(r() * (DUCKLINGS.per[1] - DUCKLINGS.per[0] + 1));
    broods.push({ m, n, trail: [], ph: Array.from({ length: n }, () => r() * 6.283) });
  }
  const N = broods.reduce((a, b) => a + b.n, 0);
  if (!N) return { count: 0, update() {} };
  const at = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6), ph = new Float32Array(N * 4);
  let i = 0;
  for (const b of broods) for (let k = 0; k < b.n; k++, i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); ph[i * 4 + v] = b.ph[k]; at.set([0, -1e4, 0, 1], (i * 4 + v) * 4); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aAt = new THREE.BufferAttribute(at, 4); aAt.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("chick", aAt);   // where it is, and (w) which way along the screen it faces: +1 / -1
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setAttribute("phase", new THREE.BufferAttribute(ph, 1));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0) };
  const A = attribute("chick", "vec4"), C = attribute("corner", "vec2"), Ph = attribute("phase", "float");
  const bob = sin(U.t.mul(2.3).add(Ph)).mul(.012);
  const P = A.xyz.add(vec3(0, bob.add(DUCKLINGS.size * .28), 0));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P, 1)).add(vec4(C.mul(DUCKLINGS.size), 0, 0)));
  // the duckling, side on (facing +x on the card, mirrored by A.w): a round fluffy body sitting low, a big head up front
  const q = uv().sub(.5).mul(2), qx = q.x.mul(A.w), fuzz = sin(q.x.mul(37).add(q.y.mul(29))).mul(.03);
  const body = smoothstep(1, .88, vec2(qx.add(.12).div(.62), q.y.add(.3).div(.42)).length().add(fuzz));
  const head = smoothstep(1, .86, vec2(qx.sub(.38).div(.3), q.y.sub(.18).div(.3)).length().add(fuzz));
  const bill = step(abs(q.y.sub(.13)), float(.06)).mul(step(.62, qx)).mul(step(qx, .84));
  const tail = step(qx, -.62).mul(step(-.82, qx)).mul(step(abs(q.y.add(.12)), qx.add(.82).mul(.5)));
  const shape = max(max(body, head), max(bill, tail)).mul(step(-.62, q.y));   // (the water hides the rest)
  const back = vec3(.42, .33, .18), yellow = vec3(.96, .83, .36);
  let col = mix(back, yellow, smoothstep(.05, -.25, q.y.sub(qx.mul(.15))));                       // dusky back, yellow underneath
  col = mix(col, yellow, head.mul(smoothstep(.15, .3, q.y.negate().add(.33))));                    // a yellow face
  const stripe = step(abs(q.y.sub(.2).add(qx.sub(.38).mul(.25))), float(.035)).mul(head).mul(step(.3, qx));
  col = mix(col, vec3(.2, .16, .1), stripe);                                                        // the eye stripe
  col = mix(col, vec3(.85, .55, .2), bill);                                                         // the bill
  mat.colorNode = col;
  mat.opacityNode = shape;
  mat.alphaTest = .5;
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "ducklings"; mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  const _v = new THREE.Vector3(), _r = new THREE.Vector3();
  return {
    count: N, broods, mesh,
    update(t, dt, { surface, camera }) {
      U.t.value = t;
      camera.matrixWorld.extractBasis(_r, _v, _v);   // (the screen's right, for which way a card faces)
      let i = 0;
      for (const b of broods) {
        const m = b.m.position, tr = b.trail;
        if (b.m.hidden) { for (let k = 0; k < b.n; k++, i++) for (let v = 0; v < 4; v++) at[(i * 4 + v) * 4 + 1] = -1e4; continue; }
        // her wake: a point every `keep` metres she has swum (newest first)
        if (!tr.length || Math.hypot(m.x - tr[0][0], m.z - tr[0][1]) > DUCKLINGS.keep) {
          if (!tr.length) for (let k = 0; k < DUCKLINGS.ring; k++) tr.push([m.x - Math.cos(b.m.rotY) * k * DUCKLINGS.keep, m.z + Math.sin(b.m.rotY) * k * DUCKLINGS.keep]);
          else { tr.unshift([m.x, m.z]); if (tr.length > DUCKLINGS.ring) tr.pop(); }
        }
        for (let k = 0; k < b.n; k++, i++) {
          const j = Math.min(tr.length - 2, Math.round((k + 1) * DUCKLINGS.gap / DUCKLINGS.keep) + 1);
          const [x, z] = tr[j], [px, pz] = tr[j - 1];   // (where it is, and the point ahead of it: the way it swims)
          const face = (px - x) * _r.x + (pz - z) * _r.z >= 0 ? 1 : -1;
          const y = surface(x, z);
          for (let v = 0; v < 4; v++) at.set([x, y, z, face], (i * 4 + v) * 4);
        }
      }
      aAt.needsUpdate = true;
    },
  };
}
