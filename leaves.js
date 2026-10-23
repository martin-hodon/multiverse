// FALLING LEAVES: from the crowns of the trees round you, fluttering and spinning down, drifting with the wind, then
// lying flat on the ground a while before they fade -- a few on a summer day, a shower of them in autumn, in the
// season's colours. Each leaf belongs to one tree for one fall; when it has faded it is dealt again to one of the trees
// nearest you (the CPU writes that leaf's four vertices), so the leaves are always falling where you are. Where a leaf
// is during its fall comes from the time alone, on the GPU. One mesh, one draw. In SPRING they are blossom PETALS --
// smaller, white and pink, drifting down from the trees in flower only (a tree's `bloom`).
//
//   const leaves = createLeaves(scene, { trees, groundH })   // trees: [{ x, z, h, bloom }] (index.html treeCols)
//   leaves.update(t, { camera, autumn, spring })             // autumn 0 summer .. 1 full autumn; spring 0 / 1
import * as THREE from "three";
import { WIND as GUSTS } from "./grass.js";   // (its strength; WIND below is its way)
import { attribute, uniform, vec2, vec3, vec4, float, uv, sin, cos, smoothstep, mix, max, min, step, clamp, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";

export const LEAVES = { max: 720, summer: 60, petals: 240, near: 45, fall: 1.0, lie: 5, size: .11, petal: .075 };
const AUTUMN = [[.85, .42, .1], [.78, .2, .08], [.92, .7, .16], [.55, .32, .14], [.7, .55, .12]], SUMMER = [[.32, .5, .16], [.42, .55, .18]], SPRING = [[.98, .9, .92], [.95, .78, .84], [1, .98, .96]];
const WIND = new THREE.Vector2(.31, .95).normalize();   // (the grass's waves' way: grass.js)

export function createLeaves(scene, { trees, groundH }) {
  const N = LEAVES.max;
  const at = new Float32Array(N * 4 * 4), info = new Float32Array(N * 4 * 4), cr = new Float32Array(N * 4 * 2), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); at.set([0, -1e4, 0, -1e4], (i * 4 + v) * 4); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  const aAt = new THREE.BufferAttribute(at, 4), aInfo = new THREE.BufferAttribute(info, 4);
  aAt.setUsage(THREE.DynamicDrawUsage); aInfo.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("leafAt", aAt);        // where it starts (x, y in the crown, z) and when (t0)
  g.setAttribute("leafInfo", aInfo);    // the ground under it, its seed, and its colour as one number (index into the palette)
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0), c0: uniform(new THREE.Color()), c1: uniform(new THREE.Color()), c2: uniform(new THREE.Color()), size: uniform(LEAVES.size) };
  const A = attribute("leafAt", "vec4"), I = attribute("leafInfo", "vec4"), C = attribute("corner", "vec2");
  const age = U.t.sub(A.w), drop = A.y.sub(I.x), tLand = drop.div(LEAVES.fall).max(.01);
  const landed = step(tLand, age), fly = min(age, tLand);
  const s = I.y;
  // the fall: down at its own pace, swinging from side to side (a leaf falls like a pendulum), carried by the wind
  const swing = sin(fly.mul(s.mul(1.5).add(2.2)).add(s.mul(20))).mul(.55);
  const drift = fly.mul(.55).mul(GUSTS.strength).add(sin(fly.mul(.7).add(s.mul(9))).mul(.4));   // (further downwind the harder it blows: grass.js WIND)
  const P = vec3(A.x.add(drift.mul(WIND.x)).add(swing.mul(WIND.y)),
                 max(A.y.sub(fly.mul(LEAVES.fall)), I.x.add(.015)),
                 A.z.add(drift.mul(WIND.y)).sub(swing.mul(WIND.x)));
  // its turn: spinning about its stalk and rocking as it swings; flat on the ground once it has landed
  const spin = fly.mul(s.mul(4).add(2)).add(s.mul(30)), rock = mix(sin(fly.mul(3.1).add(s.mul(7))).mul(.9).add(.4), float(1.5708), landed);
  const cx = C.x.mul(cos(spin)).sub(C.y.mul(sin(spin))), cy = C.x.mul(sin(spin)).add(C.y.mul(cos(spin)));
  const local = vec3(cx, cy.mul(cos(rock)), cy.mul(sin(rock))).mul(U.size);
  const life = tLand.add(LEAVES.lie);
  const alive = step(0, age).mul(step(age, life));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P.add(local.mul(alive)), 1)));
  // the leaf: a pointed oval with a midrib, its colour one of three, browning on the ground as it fades out
  const q = uv().sub(.5).mul(2), w = float(1).sub(q.y.mul(q.y)).max(0).sqrt().mul(.55).mul(float(1).sub(q.y.mul(.25)));
  const leaf = step(q.x.abs(), w).mul(step(q.y.abs(), .98));
  const k = I.z, col = mix(mix(U.c0, U.c1, step(.5, k)), U.c2, step(1.5, k));
  const rib = smoothstep(.06, .0, q.x.abs()).mul(.25);
  const fade = smoothstep(life, life.sub(1.2), age);
  mat.colorNode = col.mul(float(1).sub(rib)).mul(mix(float(1), float(.7), landed));
  mat.opacityNode = leaf.mul(fade).mul(alive);
  mat.alphaTest = .5;
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "falling leaves"; mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);

  // ---- dealing the leaves to the trees round the camera
  const t0s = new Float32Array(N).fill(-1e9), lives = new Float32Array(N);
  let near = [], lastPick = -1e9, count = LEAVES.summer, petals = false;
  const pickNear = (camera) => {
    const cx = camera.position.x, cz = camera.position.z, R = LEAVES.near;
    near = trees.filter((tr) => Math.abs(tr.x - cx) < R && Math.abs(tr.z - cz) < R && (!petals || tr.bloom));
  };
  const deal = (i, t) => {
    if (!near.length) { t0s[i] = t + 2; lives[i] = 1; return; }
    const tr = near[Math.floor(Math.random() * near.length)], a = Math.random() * Math.PI * 2, rr = Math.sqrt(Math.random()) * tr.h * .3;
    const x = tr.x + Math.cos(a) * rr, z = tr.z + Math.sin(a) * rr, gy = groundH(x, z), y = gy + tr.h * (.45 + Math.random() * .45);
    const start = t + Math.random() * 6;   // (so they never fall all at once)
    const sd = Math.random(), k = Math.floor(Math.random() * 3);
    for (let v = 0; v < 4; v++) { at.set([x, y, z, start], (i * 4 + v) * 4); info.set([gy, sd, k, 0], (i * 4 + v) * 4); }
    t0s[i] = start; lives[i] = (y - gy) / LEAVES.fall + LEAVES.lie;
    dirty = true;
  };
  let dirty = false;
  return {
    mesh,
    update(t, { camera, autumn = 0, spring = 0 } = {}) {
      U.t.value = t;
      if (!!spring !== petals) { petals = !!spring; lastPick = -1e9; for (let i = 0; i < N; i++) t0s[i] = Math.min(t0s[i], t - 1e3); }   // (the season turned: all dealt afresh)
      if (t - lastPick > 3) { pickNear(camera); lastPick = t; }
      count = petals ? LEAVES.petals : Math.round(LEAVES.summer + (N - LEAVES.summer) * Math.min(1, autumn));
      U.size.value = petals ? LEAVES.petal : LEAVES.size;
      const pal = petals ? SPRING : autumn > .25 ? AUTUMN : SUMMER;
      U.c0.value.setRGB(...pal[0]); U.c1.value.setRGB(...pal[1 % pal.length]); U.c2.value.setRGB(...pal[autumn > .6 ? 2 : 0 % pal.length]);
      for (let i = 0; i < N; i++) {
        if (i >= count) { if (t0s[i] > -1e8) { for (let v = 0; v < 4; v++) at[(i * 4 + v) * 4 + 3] = -1e4; t0s[i] = -1e9; dirty = true; } continue; }
        if (t > t0s[i] + lives[i]) deal(i, t);
      }
      if (dirty) { aAt.needsUpdate = true; aInfo.needsUpdate = true; dirty = false; }
      mesh.visible = near.length > 0;
    },
  };
}
