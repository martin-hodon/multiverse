// BIRDS PASSING OVER: a flock that crosses the sky now and then, out of the haze on one side and into it on the other,
// over you or off to one side, calling as it passes. Two kinds, declared below:
//   GEESE -- in autumn a skein of wild geese going south (in spring coming back north), high up in a ragged V (one arm
//            longer than the other), wings beating slow and heavy in a wave down the line, honking (calls.js goose);
//   ROOKS -- at dusk the rooks going home to roost, lower, in a loose straggling stream, quicker wingbeats, cawing.
// Each bird a chevron (murmuration.js), placed on the GPU from the flock's leader and its own place in the flock
// (metres behind, metres across: a V's rank and arm, or a stream's scatter) and bobbing in it; one draw while a
// flock is up.
//
//   const geese = createFlyover(scene, GEESE, { onCall })   // onCall(x, z): a call from up there, near enough to hear
//   geese.update(t, { camera, way })                        // way: [dx, dz] the way the next flock goes, or null: none now
//   geese.fly(t, camera, way)                               // start one now
import * as THREE from "three";
import { attribute, uniform, vec3, vec4, sin, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { chevronBirds, chevron } from "./murmuration.js";

export const GEESE = { name: "geese", n: 21, formation: "V", rank: 2.6, side: 1.8, every: [70, 170], speed: 15, alt: [60, 100], off: 130, from: 700,
  beat: 15, flap: .34, shape: { beak: .6, tail: .3, span: .8, sweep: -.1 }, colour: [.16, .15, .14], ear: 260, call: [.5, 1.6] };
export const ROOKS = { name: "rooks", n: 28, formation: "loose", length: 40, width: 18, every: [25, 60], speed: 11, alt: [22, 45], off: 90, from: 500,
  beat: 24, flap: .26, shape: { beak: .26, tail: .2, span: .46, sweep: -.06 }, colour: [.05, .05, .06], ear: 140, call: [.4, 1.2] };

export function createFlyover(scene, F, { onCall = () => {} } = {}) {
  // each bird's place in the flock, in metres behind the leader and across its way, and a seed of its own
  const g = chevronBirds(F.n, (i) => {
    if (F.formation === "loose") return [i === 0 ? 0 : Math.random() * F.length, (Math.random() - .5) * F.width, Math.random()];
    // the V: the leader, then by turns down the two arms -- the left one longer
    const split = F.n * .62, k = i === 0 ? 0 : i < split ? Math.ceil(i / 2) : Math.ceil(split / 2) + (i - Math.floor(split)), side = i === 0 ? 0 : i < split ? (i % 2 ? -1 : 1) : -1;
    return [k * F.rank, side * k * F.side, Math.random()];
  });
  const U = { t: uniform(0), lead: uniform(new THREE.Vector3()), dir: uniform(new THREE.Vector3(0, 0, 1)) };
  const S = attribute("seedA", "vec3"), K = attribute("role", "float");
  const across = vec3(U.dir.z.negate(), 0, U.dir.x);
  const here = U.lead.sub(U.dir.mul(S.x)).add(across.mul(S.y))
    .add(vec3(0, sin(U.t.mul(1.1).add(S.z.mul(9))).mul(.35), 0)).add(U.dir.mul(sin(U.t.mul(.7).add(S.z.mul(6))).mul(.5)));
  const flap = sin(U.t.mul(F.beat).sub(S.x.mul(.27)).add(S.z.mul(.4))).mul(F.flap);   // (a wave down a V: each a beat behind the one ahead)
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(chevron(here, U.dir, K, flap, F.shape), 1)));
  mat.colorNode = vec3(...F.colour);
  const mesh = new THREE.Mesh(g, mat);
  mesh.name = F.name; mesh.visible = false; mesh.userData.noMerge = true; mesh.userData.cut = true;
  const reach = F.formation === "loose" ? F.length : F.n * F.rank * .7;
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), reach + 5);
  scene.add(mesh);
  let sk = null, nextAt = F.every[0] * Math.random(), callAt = 0;
  const fly = (t, camera, way) => {
    const a = (Math.random() - .5) * .8, c = Math.cos(a), s = Math.sin(a), l = Math.hypot(way[0], way[1]) || 1;
    const dir = new THREE.Vector3((way[0] * c - way[1] * s) / l, 0, (way[0] * s + way[1] * c) / l);
    const lat = (Math.random() * 2 - 1) * F.off, alt = F.alt[0] + Math.random() * (F.alt[1] - F.alt[0]);
    const start = camera.position.clone().addScaledVector(dir, -F.from).add(new THREE.Vector3(-dir.z * lat, 0, dir.x * lat));
    start.y = camera.position.y + alt;
    sk = { t0: t, start, dir };
    U.dir.value.copy(dir);
  };
  return {
    mesh, fly,
    get flock() { return sk; },
    update(t, { camera, way = null }) {
      U.t.value = t;
      if (!sk && way && t > nextAt) fly(t, camera, way);
      if (sk && (t - sk.t0) * F.speed > F.from * 2) { sk = null; nextAt = t + F.every[0] + Math.random() * (F.every[1] - F.every[0]); }
      mesh.visible = !!sk;
      if (!sk) return;
      U.lead.value.copy(sk.start).addScaledVector(sk.dir, (t - sk.t0) * F.speed);
      g.boundingSphere.center.copy(U.lead.value).addScaledVector(sk.dir, -reach * .45);
      const L = U.lead.value;
      if (t > callAt && Math.hypot(L.x - camera.position.x, L.z - camera.position.z) < F.ear) {
        callAt = t + F.call[0] + Math.random() * (F.call[1] - F.call[0]);
        const back = Math.random() * reach * .6;
        onCall(L.x - sk.dir.x * back, L.z - sk.dir.z * back);
      }
    },
  };
}
