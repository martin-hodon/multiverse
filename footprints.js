// FOOTPRINTS IN THE SNOW: while snow lies on the ground, your steps leave prints -- left, right, a pace apart,
// pointing the way you walked -- that slowly fill in again; and IN THE MUD of a road soaked by the rain, dark ones. A ring of flat cards on the ground (the oldest reused),
// each print drawn in the shader as a boot sole: a heel and a ball, pressed a shade darker and bluer than the snow.
//
// WHOSE PRINT (2026-10-24): a person's is a boot; an animal's is its kind's (a species' `print`, assets/creatures:
// PRINTS) -- a horse's solid hoof, a cow's or a deer's cloven one, a dog's or a cat's paw (a pad and four toes), a
// hen's three toes and a spur, an elephant's round pad -- sized by its legs (printOf: the foot's length is `k` times the
// leg's, within `min`..`max` metres). Every animal had left the same boot print, a hen's as big as a man's.
//
//   const prints = createFootprints(scene, { groundH })
//   prints.step(x, z, heading, side, t, mud, size, print)  // one print (side -1 left, +1 right; mud: in the mud, not the snow;
//                                                          // size: 1 a boot -- a child's smaller; print: printOf(...) for an animal)
//   printOf(name, legLen)                                  // an animal's print: { shape, L, W, gauge } in metres
//   prints.update(t)
import * as THREE from "three";
import { attribute, uniform, vec2, vec3, vec4, float, uv, smoothstep, max, mix, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";

export const FOOTPRINTS = { max: 900, fill: 150, pace: .72, gauge: .13 };
// shape: the shader's; k: the print's length per metre of leg (within min..max metres -- max: the LARGEST that wears it,
// not the largest living one: at .2 a tyrannosaur's three toes were a hen's); w: its width per length;
// gauge: how far left and right of the line of travel, per metre of leg
export const PRINTS = {
  boot:   { shape: 0 },
  hoof:   { shape: 1, k: .14, w: .95, min: .06, max: .25, gauge: .16 },
  cloven: { shape: 2, k: .12, w: .85, min: .04, max: .3, gauge: .16 },    // (a giraffe's)
  paw:    { shape: 3, k: .17, w: .9, min: .025, max: .4, gauge: .2 },     // (a dragon's, a manticore's)
  bird:   { shape: 4, k: .4, w: 1.05, min: .04, max: .85, gauge: .25 },   // (a hen's 7 cm on a 17 cm leg, a tyrannosaur's 80 cm on 3 m)
  pad:    { shape: 5, k: .25, w: 1, min: .15, max: 1, gauge: .2 },        // (a sauropod's a metre across)
};
export function printOf(name, legLen) {
  const P = PRINTS[name] ?? PRINTS.paw, L = Math.max(P.min, Math.min(P.max, legLen * P.k));
  return { shape: P.shape, L, W: L * P.w, gauge: legLen * P.gauge };
}

export function createFootprints(scene, { groundH }) {
  const N = FOOTPRINTS.max, pos = new Float32Array(N * 12), born = new Float32Array(N * 4), kind = new Float32Array(N * 4), shp = new Float32Array(N * 4), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); born[i * 4 + v] = -1e9; }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aPos = new THREE.BufferAttribute(pos, 3), aBorn = new THREE.BufferAttribute(born, 1), aKind = new THREE.BufferAttribute(kind, 1), aShape = new THREE.BufferAttribute(shp, 1);
  for (const a of [aPos, aBorn, aKind, aShape]) a.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", aPos);
  g.setAttribute("born", aBorn);
  g.setAttribute("printKind", aKind);
  g.setAttribute("printShape", aShape);
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
  // ...and the animals' (q: x across, y forward, -1..1 over the card)
  const blob = (cx, cy, rx, ry) => smoothstep(1, .78, vec2(q.x.sub(cx).div(rx), q.y.sub(cy).div(ry)).length());
  const r1 = vec2(q.x, q.y.mul(1.05)).length();   // a solid HOOF: a rounded wall, open at the heel, the frog's hollow inside
  const hoof = smoothstep(1, .84, r1).mul(smoothstep(.42, .58, r1).max(smoothstep(-.1, .1, q.y.add(.2)).mul(.35))).mul(float(1).sub(blob(0, -.95, .3, .35)));
  const cloven = max(blob(-.33, 0, .3, .9), blob(.33, 0, .3, .9));   // two halves, pointed forward
  const paw = max(max(blob(0, -.38, .48, .38), max(blob(-.56, .2, .2, .24), blob(.56, .2, .2, .24))), max(blob(-.2, .56, .2, .26), blob(.2, .56, .2, .26)));
  // a BIRD's three toes forward and a spur back, strokes from the heel
  const toe = (ax, ay, dx, dy, len, w) => {
    const px = q.x.sub(ax), py = q.y.sub(ay), tt = px.mul(dx).add(py.mul(dy)).clamp(0, len);
    return smoothstep(w, w * .55, vec2(px.sub(tt.mul(dx)), py.sub(tt.mul(dy))).length());
  };
  const bird = max(max(toe(0, -.45, 0, 1, 1.3, .13), max(toe(0, -.45, -.62, .78, 1.2, .12), toe(0, -.45, .62, .78, 1.2, .12))), toe(0, -.45, 0, -1, .45, .11));
  const pad = max(blob(0, -.08, .86, .82), max(blob(-.45, .78, .16, .14), max(blob(0, .9, .16, .14), blob(.45, .78, .16, .14))));   // an elephant's: round, its nails in front
  const S = attribute("printShape", "float"), at = (k) => float(1).sub(S.sub(k).abs()).max(0);
  const shape = sole.mul(at(0)).add(hoof.mul(at(1))).add(cloven.mul(at(2))).add(paw.mul(at(3))).add(bird.mul(at(4))).add(pad.mul(at(5)));
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });   // (its corners wind either way)
  mat.colorNode = mix(vec3(.42, .48, .62), vec3(.025, .017, .01), attribute("printKind", "float"));   // (snow: pressed darker and bluer; mud: dark wet earth -- linear colour: .025 shows as ~.17)
  mat.opacityNode = shape.mul(fresh).mul(.75);
  mat.polygonOffset = true; mat.polygonOffsetFactor = -2; mat.polygonOffsetUnits = -2;
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "footprints"; mesh.renderOrder = 1; mesh.visible = false;
  scene.add(mesh);
  let next = 0, last = -1e9;
  return {
    mesh,
    step(x, z, heading, side, t, mud = false, size = 1, print = null) {   // (print, not `kind`: that is the snow-or-mud array)
      const i = next++ % N, fx = Math.sin(heading), fz = Math.cos(heading), rx = fz, rz = -fx;   // (forward, and right of it)
      const gauge = print ? print.gauge : FOOTPRINTS.gauge * size;
      const cx = x + rx * side * gauge, cz = z + rz * side * gauge, y = groundH(cx, cz) + .07;   // (a hand above the height function: the ground mesh's triangles do not follow it to the centimetre)
      const L = print ? print.L : .3 * size, W = print ? print.W : .12 * size;
      shp.fill(print ? print.shape : 0, i * 4, i * 4 + 4); aShape.needsUpdate = true;
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([u, v], k) => pos.set([cx + rx * W / 2 * u + fx * L / 2 * v, y, cz + rz * W / 2 * u + fz * L / 2 * v], (i * 4 + k) * 3));
      born.fill(t, i * 4, i * 4 + 4); kind.fill(mud ? 1 : 0, i * 4, i * 4 + 4);
      aPos.needsUpdate = true; aBorn.needsUpdate = true; aKind.needsUpdate = true;
      last = t; mesh.visible = true;
    },
    update(t) { U.t.value = t; if (t - last > FOOTPRINTS.fill) mesh.visible = false; },
  };
}
