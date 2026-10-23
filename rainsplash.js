// RAINDROPS SPLASHING on the ground round you: little crowns of spray popping up and gone -- each a card facing the
// eye, a ring of droplets thrown up and falling back in a fifth of a second. A pool of them, each dealt again (to a new
// place within 10 m of you, on the open ground: not where a building stands) as its splash ends, more of them the
// harder it rains. Where a splash is and how far through it, the GPU works out from its start and the time.
//
//   const splashes = createRainSplashes(scene, { groundH, open })   // open(x, z): no roof there
//   splashes.update(t, { camera, rain })                           // rain 0 none .. 1 a downpour
import * as THREE from "three";
import { attribute, uniform, vec2, vec4, float, uv, smoothstep, sin, fract, step, abs, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";

export const SPLASH = { pool: 220, life: .24, near: 10, size: .26 };

export function createRainSplashes(scene, { groundH, open = () => true }) {
  const N = SPLASH.pool, at = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6), t0s = new Float32Array(N).fill(-1e9);
  for (let i = 0; i < N; i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : 0], (i * 4 + v) * 2); at.set([0, -1e4, 0, -1e9], (i * 4 + v) * 4); }   // (the card stands on the ground: its foot at the splash)
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aAt = new THREE.BufferAttribute(at, 4); aAt.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("splashAt", aAt);
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(new Float32Array(N * 8).map((_, j) => (j % 2 ? (cr[j] * 2) : cr[j] + .5)), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0) };
  const A = attribute("splashAt", "vec4"), C = attribute("corner", "vec2");
  const k = U.t.sub(A.w).div(SPLASH.life).clamp(0, 1), live = step(A.w, U.t).mul(step(U.t, A.w.add(SPLASH.life)));
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(A.xyz, 1)).add(vec4(C.mul(SPLASH.size).mul(live), 0, 0)));
  // the crown: droplets on a little arc thrown out and up and falling back (x across, y up from the foot)
  const q = uv(), x = q.x.sub(.5).mul(2), y = q.y;
  const arc = k.mul(.9).add(.1), h = arc.mul(float(1).sub(k)).mul(3.2);   // (how far out, how high: up then down)
  const drops = smoothstep(.16, .05, vec2(abs(x).sub(arc.mul(.8)), y.sub(h.mul(.7)).mul(1.4)).length());
  const mid = smoothstep(.2, .06, vec2(x.mul(1.4), y.sub(h.mul(1.1))).length()).mul(step(k, .55));   // (the drop's own jet, early)
  const ripple = smoothstep(.07, .0, abs(vec2(x, y.mul(4)).length().sub(arc))).mul(step(y, .08));
  mat.colorNode = vec4(.85, .9, .95, 1).xyz;
  mat.opacityNode = drops.add(mid).add(ripple.mul(.6)).min(1).mul(float(1).sub(k.mul(.8))).mul(.9).mul(live);
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "rain splashes"; mesh.visible = false; mesh.renderOrder = 3;
  mesh.userData.noMerge = true;
  scene.add(mesh);
  return {
    mesh,
    update(t, { camera, rain = 0 } = {}) {
      U.t.value = t;
      mesh.visible = rain > .01;
      if (!mesh.visible) return;
      const n = Math.round(N * Math.min(1, rain)), cx = camera.position.x, cz = camera.position.z;
      let dirty = false;
      for (let i = 0; i < n; i++) {
        if (t < t0s[i] + SPLASH.life) continue;
        const a = Math.random() * Math.PI * 2, r = 1 + Math.sqrt(Math.random()) * SPLASH.near, x = cx + Math.cos(a) * r, z = cz + Math.sin(a) * r;
        const start = t + Math.random() * SPLASH.life;   // (never all at once)
        t0s[i] = start;
        const y = open(x, z) ? groundH(x, z) + .02 : -1e4;
        for (let v = 0; v < 4; v++) at.set([x, y, z, start], (i * 4 + v) * 4);
        dirty = true;
      }
      if (dirty) aAt.needsUpdate = true;
    },
  };
}
