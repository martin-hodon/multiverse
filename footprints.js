// FOOTPRINTS IN THE SNOW: while snow lies on the ground, your steps leave prints -- left, right, a pace apart,
// pointing the way you walked -- that slowly fill in again; and IN THE MUD of a road soaked by the rain, dark ones. A ring of flat cards on the ground (the oldest reused),
// each print drawn in the shader as a boot sole: a heel and a ball, pressed a shade darker and bluer than the snow.
//
//   const prints = createFootprints(scene, { groundH })
//   prints.step(x, z, heading, side, t, mud, size)   // one print (side -1 left, +1 right; mud: in the mud, not the snow;
//                                                    // size: 1 a boot -- a child's, a sheep's, a horse's smaller or larger)
//   prints.update(t)
import * as THREE from "three";
import { attribute, uniform, vec2, vec3, vec4, float, uv, smoothstep, max, mix, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";

export const FOOTPRINTS = { max: 900, fill: 150, pace: .72, gauge: .13 };

export function createFootprints(scene, { groundH }) {
  const N = FOOTPRINTS.max, pos = new Float32Array(N * 12), born = new Float32Array(N * 4), kind = new Float32Array(N * 4), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); born[i * 4 + v] = -1e9; }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aPos = new THREE.BufferAttribute(pos, 3), aBorn = new THREE.BufferAttribute(born, 1), aKind = new THREE.BufferAttribute(kind, 1);
  aPos.setUsage(THREE.DynamicDrawUsage); aBorn.setUsage(THREE.DynamicDrawUsage); aKind.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", aPos);
  g.setAttribute("born", aBorn);
  g.setAttribute("printKind", aKind);
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0) };
  const B = attribute("born", "float");
  const age = U.t.sub(B), fresh = smoothstep(FOOTPRINTS.fill, FOOTPRINTS.fill * .3, age);
  // a boot sole along the card's length (v): the heel behind, the ball and toes in front, a waist between
  const q = uv().sub(.5).mul(2);
  const heel = smoothstep(1, .8, vec2(q.x.div(.62), q.y.add(.55).div(.4)).length());
  const ball = smoothstep(1, .8, vec2(q.x.div(.75), q.y.sub(.35).div(.55)).length());
  const waist = smoothstep(1, .8, vec2(q.x.div(.45), q.y.add(.1).div(.4)).length()).mul(.6);
  const sole = max(max(heel, ball), waist);
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });   // (its corners wind either way)
  mat.colorNode = mix(vec3(.42, .48, .62), vec3(.025, .017, .01), attribute("printKind", "float"));   // (snow: pressed darker and bluer; mud: dark wet earth -- linear colour: .025 shows as ~.17)
  mat.opacityNode = sole.mul(fresh).mul(.75);
  mat.polygonOffset = true; mat.polygonOffsetFactor = -2; mat.polygonOffsetUnits = -2;
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "footprints"; mesh.renderOrder = 1; mesh.visible = false;
  scene.add(mesh);
  let next = 0, last = -1e9;
  return {
    mesh,
    step(x, z, heading, side, t, mud = false, size = 1) {
      const i = next++ % N, fx = Math.sin(heading), fz = Math.cos(heading), rx = fz, rz = -fx;   // (forward, and right of it)
      const cx = x + rx * side * FOOTPRINTS.gauge * size, cz = z + rz * side * FOOTPRINTS.gauge * size, y = groundH(cx, cz) + .07;   // (a hand above the height function: the ground mesh's triangles do not follow it to the centimetre)
      const L = .3 * size, W = .12 * size;
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([u, v], k) => pos.set([cx + rx * W / 2 * u + fx * L / 2 * v, y, cz + rz * W / 2 * u + fz * L / 2 * v], (i * 4 + k) * 3));
      born.fill(t, i * 4, i * 4 + 4); kind.fill(mud ? 1 : 0, i * 4, i * 4 + 4);
      aPos.needsUpdate = true; aBorn.needsUpdate = true; aKind.needsUpdate = true;
      last = t; mesh.visible = true;
    },
    update(t) { U.t.value = t; if (t - last > FOOTPRINTS.fill) mesh.visible = false; },
  };
}
