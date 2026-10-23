// A MURMURATION: a few hundred starlings flying as one cloud over the fields, folding, stretching and rippling,
// dark waves running through it. Every bird is a little chevron -- two wings flapping on a short body -- turned
// along its own flight; where it is comes from the time and its own three seeds alone (flockPos, on the GPU), and
// its heading from where it will be a moment later. One mesh, one draw, nothing touched per frame but the clock.
// By day and at dusk; at night they have gone to roost.
//
//   const flock = createMurmuration(scene, { centre: [x, y, z], radius, count, seed })
//   flock.update(t, { dark })
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec3, vec4, float, wgslFn, cameraViewMatrix, cameraProjectionMatrix, normalize, cross, sin, smoothstep } from "three/tsl";
import { rng } from "./flora.js";

// where a bird is at time t: the flock's middle wandering over the land, the bird on its own slow loop inside the
// cloud, the whole cloud warped by a travelling fold and stretched in turn along each axis
const flockPos = wgslFn(`
  fn flockPos(s: vec3<f32>, t: f32, c: vec3<f32>, R: f32) -> vec3<f32> {
    let m = c + vec3<f32>(sin(t * 0.031) * R * 2.6 + sin(t * 0.017 + 1.0) * R, sin(t * 0.05) * R * 0.22, cos(t * 0.023) * R * 2.1);
    var p = vec3<f32>(sin(t * (0.21 + s.x * 0.1) + s.y * 6.283),
                      sin(t * (0.17 + s.y * 0.1) + s.z * 6.283) * 0.55,
                      cos(t * (0.19 + s.z * 0.1) + s.x * 6.283));
    p = p * (0.55 + 0.45 * s.z);
    p = p + 0.45 * vec3<f32>(sin(p.y * 3.1 + t * 0.6), sin(p.z * 2.7 + t * 0.45), sin(p.x * 2.9 + t * 0.5));
    let stretch = vec3<f32>(1.0 + 0.55 * sin(t * 0.23), 0.6 + 0.3 * sin(t * 0.31 + 1.3), 1.0 + 0.55 * cos(t * 0.19));
    return m + p * stretch * R;
  }
`);

// A BIRD AS A CHEVRON (here, and the geese's skeins: geese.js): four corners -- 0 its beak, 1 its tail, 2 the left
// wing's tip, 3 the right's -- two triangles sharing the body. chevronBirds builds n of them (attributes `role`, and
// `seedA` from seeds(i): three numbers a bird); chevron() puts a corner in the world from the bird's place, its way
// (f, unit), its role, the wings' lift (flap) and its measures: beak and tail ahead and behind, the half span, how far
// back the tips sweep.
export function chevronBirds(n, seeds) {
  const sd = new Float32Array(n * 4 * 3), role = new Float32Array(n * 4), idx = new Uint32Array(n * 6);
  for (let i = 0; i < n; i++) {
    const s = seeds(i);
    for (let v = 0; v < 4; v++) { sd.set(s, (i * 4 + v) * 3); role[i * 4 + v] = v; }
    idx.set([i * 4, i * 4 + 1, i * 4 + 2, i * 4, i * 4 + 3, i * 4 + 1], i * 6);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 12), 3));
  g.setAttribute("seedA", new THREE.BufferAttribute(sd, 3));
  g.setAttribute("role", new THREE.BufferAttribute(role, 1));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  return g;
}
export function chevron(here, f, K, flap, { beak, tail, span, sweep }) {
  const right = normalize(cross(f, vec3(0, 1, 0))), up = cross(right, f);
  const one = float(1), zero = float(0);   // (the roles, as weights: beak, tail, left tip, right tip)
  const isB = K.lessThan(.5).select(one, zero), isT = K.greaterThan(.5).and(K.lessThan(1.5)).select(one, zero),
        isL = K.greaterThan(1.5).and(K.lessThan(2.5)).select(one, zero), isR = K.greaterThan(2.5).select(one, zero);
  return here.add(f.mul(isB.mul(beak).sub(isT.mul(tail))))
    .add(right.mul(isR.sub(isL).mul(span)))
    .add(up.mul(isL.add(isR).mul(flap)))
    .add(f.mul(isL.add(isR).mul(sweep)));
}

export function createMurmuration(scene, { centre, radius = 22, count = 600, seed = 3 }) {
  const r = rng(seed * 97 + 13);
  const g = chevronBirds(count, () => [r(), r(), r()]);
  const U = { t: uniform(0), c: uniform(new THREE.Vector3(...centre)), R: uniform(radius) };
  const S = attribute("seedA", "vec3"), K = attribute("role", "float");
  const here = flockPos({ s: S, t: U.t, c: U.c, R: U.R }), ahead = flockPos({ s: S, t: U.t.add(.12), c: U.c, R: U.R });
  const flap = sin(U.t.mul(17).add(S.x.mul(40))).mul(.11);
  const wp = chevron(here, normalize(ahead.sub(here)), K, flap, { beak: .13, tail: .11, span: .21, sweep: -.05 });
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(wp, 1)));
  mat.colorNode = vec3(.07, .07, .08);
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, [centre], radius * 2.5);
  mesh.name = "murmuration";
  mesh.userData.noMerge = true;
  mesh.userData.cut = true;   // (placed by its shader: never an occluder or a ground prop through an override material)
  scene.add(mesh);
  return {
    mesh, centre: U.c.value, radius,
    update(t, { dark = 0 } = {}) { U.t.value = t; mesh.visible = dark < .72; },
  };
}
