// WAKES behind what swims: a duck or a swan under way draws a V of ripples on the water behind it -- two arms opening
// at the Kelvin angle (19.5 degrees each side, whatever the speed: every boat's and every duck's wake makes it), short
// crests slanting off them, the whole V fading behind; longer and brighter the faster it goes, gone when it rests.
// One card a swimmer, lying on the water, turned to its heading -- placed each frame from where the swimmer is (its
// speed from how far it went); the ripples are the shader's. One mesh, one draw.
//
//   const wakes = createWakes(scene, swimmers)       // swimmers: [{ position, rotY, size }] (size: metres, its body)
//   wakes.update(t, dt, { surface, camera })          // surface(x, z): the water's height there
import * as THREE from "three";
import { attribute, uniform, vec4, float, sin, abs, exp, smoothstep, max } from "three/tsl";

export const WAKES = { len: 6, near: 90, kelvin: Math.tan(19.47 * Math.PI / 180), full: .45 };   // len: wake length per metre of body; full: m/s for the whole wake

export function createWakes(scene, swimmers) {
  const N = swimmers.length;
  if (!N) return { mesh: null, update() {} };
  const pos = new Float32Array(N * 12), wk = new Float32Array(N * 16), idx = new Uint32Array(N * 6), uvA = new Float32Array(N * 8);
  for (let i = 0; i < N; i++) {
    idx.set([i * 4, i * 4 + 1, i * 4 + 2, i * 4, i * 4 + 2, i * 4 + 3], i * 6);
    uvA.set([0, -1, 0, 1, 1, 1, 1, -1], i * 8);   // (u: 0 at its tail .. 1 at the far end of the wake; v: across, -1 .. 1)
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute("wake", new THREE.BufferAttribute(wk, 4).setUsage(THREE.DynamicDrawUsage));   // (length m, width m, strength, ripple size m)
  g.setAttribute("uvw", new THREE.BufferAttribute(uvA, 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0) };
  const W = attribute("wake", "vec4"), Q = attribute("uvw", "vec2");
  const X = Q.x.mul(W.x), Y = abs(Q.y).mul(W.y);                                  // metres behind it, metres off its line
  const arm = Y.sub(X.mul(WAKES.kelvin)).sub(.03);                                // (0 on the V's arm, < 0 inside it)
  const crests = sin(X.mul(.34).add(Y.mul(.94)).div(W.w).mul(6.283).sub(U.t.mul(4))).mul(.5).add(.5);   // slanting off the arms
  const inV = smoothstep(.08, -.02, arm);
  const edge = smoothstep(.09, 0, abs(arm));                                      // the arm itself, brightest
  const fade = exp(Q.x.mul(-2.6)).mul(smoothstep(0, .06, Q.x));                    // dying away behind, rising off its tail
  const a = max(edge.mul(.8), inV.mul(crests).mul(smoothstep(-.6, 0, arm)).mul(.55)).mul(fade).mul(W.z);
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
  mat.colorNode = vec4(.86, .91, .96, 1).xyz;
  mat.opacityNode = a.mul(.42);
  const mesh = new THREE.Mesh(g, mat);
  mesh.name = "wakes"; mesh.renderOrder = 3; mesh.userData.noMerge = true;
  scene.add(mesh);
  const last = swimmers.map((s) => ({ x: s.position.x, z: s.position.z, v: 0 }));
  return {
    mesh,
    update(t, dt, { surface, camera }) {
      U.t.value = t;
      if (!(dt > 0)) return;
      let any = false;
      swimmers.forEach((s, i) => {
        const p = s.position, L = last[i], o = i * 12;
        const v = Math.hypot(p.x - L.x, p.z - L.z) / dt;
        L.v += (Math.min(v, 3) - L.v) * Math.min(1, dt * 3); L.x = p.x; L.z = p.z;
        const k = Math.min(1, L.v / WAKES.full), far = Math.hypot(p.x - camera.position.x, p.z - camera.position.z) > WAKES.near;
        if (k < .05 || far || s.hidden) { for (let j = 0; j < 4; j++) pos.set([p.x, p.y, p.z], o + j * 3); wk.fill(0, i * 16, i * 16 + 16); return; }   // (folded up where it is: the bounds stay tight)
        any = true;
        const size = s.size ?? .5, len = WAKES.len * size * (.4 + .6 * k), wid = len * WAKES.kelvin + .15;
        const fx = Math.cos(s.rotY), fz = -Math.sin(s.rotY), sx = -fz, sz = fx, y = surface(p.x, p.z) + .015;
        const tx = p.x - fx * size * .45, tz = p.z - fz * size * .45;   // (its tail: the wake starts there)
        const C = [[0, -1], [0, 1], [1, 1], [1, -1]];
        C.forEach(([u, w], j) => { pos[o + j * 3] = tx - fx * u * len + sx * w * wid; pos[o + j * 3 + 1] = y; pos[o + j * 3 + 2] = tz - fz * u * len + sz * w * wid; });
        for (let j = 0; j < 4; j++) wk.set([len, wid, k, .22 * size + .08], i * 16 + j * 4);
      });
      mesh.visible = any;
      if (any) { g.attributes.position.needsUpdate = g.attributes.wake.needsUpdate = true; g.computeBoundingSphere(); }
    },
  };
}
