// THE SMITH'S SPARKS: every blow of a smith's hammer on the anvil throws a spray of sparks -- orange-white, flying out
// low and fast, arcing down, gone in half a second -- and rings the anvil (a bright "ting" you hear near the smithy).
// The blows keep the hammer's own time: the `hammer` gesture (people.js) swings once a second on the world clock and
// strikes at the bottom of the swing, three quarters into each second -- so the sparks fly when the hammer lands.
// Where: the smiths' hands, read every frame (index.html: the villagers holding a hammer at their work).
// One mesh (24 sparks a smith, 6 smiths at most), placed on the GPU from the time.
//
//   const sparks = createForgeSparks(scene, { audio, camera })
//   sparks.update(t, smiths, dark)   // smiths: [[x, y, z], ...] where each hammer meets the anvil
import * as THREE from "three";
import { attribute, uniform, vec3, vec4, float, uv, sin, fract, floor, smoothstep, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { SR, toBuffer, play } from "./dsp.js";

export const SPARKS = { smiths: 6, per: 24, strike: .75, life: .55 };

export function createForgeSparks(scene, { audio = () => null, camera }) {
  const N = SPARKS.smiths * SPARKS.per, at = new Float32Array(N * 4 * 4), sd = new Float32Array(N * 4 * 2), cr = new Float32Array(N * 4 * 2), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    const s = [Math.random(), Math.random()];
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); sd.set(s, (i * 4 + v) * 2); at.set([0, -1e4, 0, 0], (i * 4 + v) * 4); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  const aAt = new THREE.BufferAttribute(at, 4); aAt.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("anvil", aAt);                   // where its smith's hammer lands (w: 1 working, 0 not)
  g.setAttribute("seedA", new THREE.BufferAttribute(sd, 2));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0), night: uniform(0) };
  const A = attribute("anvil", "vec4"), S = attribute("seedA", "vec2"), C = attribute("corner", "vec2");
  const ph = U.t.sub(SPARKS.strike), blow = floor(ph), age = fract(ph);          // which blow, and how long since it landed
  // a new direction every blow: hashed from the spark's seed and the blow's number
  const h = (k) => fract(sin(S.x.mul(127.1).add(S.y.mul(311.7)).add(blow.mul(k))).mul(43758.5));
  const a = h(12.9).mul(6.283), up = h(78.2).mul(.9).add(.15), sp = h(39.4).mul(3.5).add(2);
  const P = A.xyz.add(vec3(sin(a.add(1.5708)).mul(sp).mul(age), up.mul(sp).mul(age).sub(age.mul(age).mul(4.9)), sin(a).mul(sp).mul(age)));
  const alive = smoothstep(SPARKS.life, SPARKS.life * .6, age).mul(A.w).mul(h(5.1).lessThan(.85).select(float(1), float(0)));
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P, 1)).add(vec4(C.mul(.065).mul(alive), 0, 0)));
  const r = uv().sub(.5).mul(2).length();
  // (white-hot to orange as it cools; brighter by night, when the frame's darkening would swallow it)
  mat.colorNode = vec3(1, .78, .45).mul(smoothstep(1, 0, r)).mul(alive).mul(U.night.mul(2.5).add(1.4)).mul(vec3(1, smoothstep(SPARKS.life, 0, age).mul(.4).add(.6), smoothstep(SPARKS.life, 0, age)));
  mat.opacityNode = float(1);
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "forge sparks"; mesh.visible = false;
  scene.add(mesh);

  // the anvil's ring: a bright struck-steel ting with a long, beating tail
  let buf = null, lastBlow = -1;
  const ting = (p) => {
    const ctx = audio?.();
    if (!ctx) return;
    const d = camera.position.distanceTo(p);
    if (d > 35) return;
    buf ??= toBuffer(Float32Array.from({ length: Math.round(.9 * SR) }, (_, i) => { const t = i / SR;
      return .5 * Math.exp(-t * 7) * (Math.sin(2 * Math.PI * 1810 * t) + .6 * Math.sin(2 * Math.PI * 1832 * t) + .4 * Math.sin(2 * Math.PI * 3970 * t) * Math.exp(-t * 6)) + .8 * Math.exp(-t * 180) * (Math.random() * 2 - 1); }));
    const gn = ctx.createGain(); gn.gain.value = Math.min(.5, 2.5 / Math.max(d, 1)) * .5; gn.connect(ctx.destination);
    play(ctx, buf, { dest: gn, rate: .97 + Math.random() * .06 });
  };
  const P0 = new THREE.Vector3();
  return {
    mesh,
    update(t, smiths = [], dark = 0) {
      U.t.value = t; U.night.value = dark;
      const n = Math.min(SPARKS.smiths, smiths.length);
      for (let k = 0; k < SPARKS.smiths; k++) for (let s = 0; s < SPARKS.per; s++) for (let v = 0; v < 4; v++) {
        const q = ((k * SPARKS.per + s) * 4 + v) * 4;
        if (k < n) at.set([smiths[k][0], smiths[k][1], smiths[k][2], 1], q); else at[q + 3] = 0;
      }
      aAt.needsUpdate = true;
      mesh.visible = n > 0;
      const b = Math.floor(t - SPARKS.strike);
      if (n && b !== lastBlow) { lastBlow = b; for (const p of smiths.slice(0, n)) ting(P0.set(p[0], p[1], p[2])); }
    },
  };
}
