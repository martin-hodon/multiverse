// A JUGGLER'S BALLS: three balls in a cascade between the two hands of a figure -- throws three a second, each hand in
// turn, every ball flying from one hand over to the other in an arc half a metre high, caught, carried a moment and
// thrown again. Where the hands are comes from the figure as posed this frame (the composite's ends); the arcs are
// worked out here and three cards placed, each a shaded ball facing the eye. One mesh, one draw.
//
//   const balls = createJuggler(scene, { herd, an, hands: [right, left] })   // hands: the hand parts' indices (tools.js handIndex)
//   balls.update(t)   // after the figure is posed
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, vec2, vec3, vec4, uv, smoothstep, mix, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";

export const JUGGLE = { throws: 3, apex: .55, r: .045, colours: [[.85, .18, .14], [.95, .78, .2], [.2, .4, .85]] };

export function createJuggler(scene, { herd, an, hands }) {
  const N = 3, at = new Float32Array(N * 16), cr = new Float32Array(N * 8), cl = new Float32Array(N * 12), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); cl.set(JUGGLE.colours[i].map((c) => c ** 2.2), (i * 4 + v) * 3); at.set([0, -1e4, 0, 1], (i * 4 + v) * 4); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aAt = new THREE.BufferAttribute(at, 4); aAt.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("ball", aAt);
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setAttribute("ballColour", new THREE.BufferAttribute(cl, 3));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const A = attribute("ball", "vec4"), C = attribute("corner", "vec2"), K = attribute("ballColour", "vec3");
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(A.xyz, 1)).add(vec4(C.mul(JUGGLE.r * 2), 0, 0)));
  const q = uv().sub(.5).mul(2), d = q.length();
  // a ball: lit from above and a little to one side, a highlight, darker toward its rim
  const shade = smoothstep(1, -.4, q.sub(vec2(-.35, .45)).length()).mul(.55).add(.55);
  mat.colorNode = mix(K.mul(shade), vec3(1, 1, 1), smoothstep(.3, .05, q.sub(vec2(-.35, .4)).length()).mul(.6));
  mat.opacityNode = smoothstep(1, .9, d);
  mat.alphaTest = .5;
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, [an.position], 2.5); mesh.name = "juggling balls";   // (he stays where he stands) mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  const H = [0, 0].map(() => new THREE.Vector3()), dt = 1 / JUGGLE.throws;
  const handAt = (k, out) => { const [a, b] = herd.ends(an, hands[k]); return out.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + .03, (a[2] + b[2]) / 2); };
  return {
    mesh,
    update(t) {
      mesh.visible = !an.hidden && !an._off && !an._out;
      if (!mesh.visible) return;
      handAt(0, H[0]); handAt(1, H[1]);
      const n0 = Math.floor(t / dt);
      for (let b = 0; b < N; b++) {
        // its last throw: the latest throw number n <= now with n mod 3 == b, by hand n mod 2; two beats in the air
        // to the other hand, held there one beat, thrown again (by that hand: the numbers work out)
        let n = n0 - ((n0 - b) % 3 + 3) % 3;
        const u = (t / dt - n) / 2, from = H[((n % 2) + 2) % 2], to = H[(((n + 1) % 2) + 2) % 2];   // (n may be below 0 at the start)
        let x, y, z;
        if (u < 1) {
          x = from.x + (to.x - from.x) * u; z = from.z + (to.z - from.z) * u;
          y = from.y + (to.y - from.y) * u + 4 * JUGGLE.apex * u * (1 - u);
        } else { x = to.x; y = to.y; z = to.z; }
        for (let v = 0; v < 4; v++) at.set([x, y, z, 1], (b * 4 + v) * 4);
      }
      aAt.needsUpdate = true;
    },
  };
}
