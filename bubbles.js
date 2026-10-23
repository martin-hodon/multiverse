// SOAP BUBBLES: a small child on the green blows bubbles from a wand, a stream of them at each breath, and the breeze
// takes them -- drifting downwind with the grass's gusts (grass.js), rising and sinking a little, wobbling, each
// swirled with the bands of colour of its thin film (sky.js spectrum) and a bright window of the sky on its shoulder;
// they pop after a few seconds, or when they touch the grass. CPU-moved (a few dozen at most), one draw: a card each,
// facing you, the sphere drawn by the shader.
//
//   const bubbles = createBubbles(scene)   // (the child's on the green, and yours: index.html, Z)
//   bubbles.blow(x, y, z, dx, dz, t, ground)   // one bubble off the wand at x, y, z, sent off along dx, dz; ground: the
//                                              // height it pops at (the ground there: near enough, where it drifts)
//   bubbles.update(t, dt)                      // -> how many are flying
import * as THREE from "three";
import { attribute, uniform, vec2, vec3, vec4, float, sqrt, pow, fract, smoothstep, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { WIND, WIND_DIR, gustAt } from "./grass.js";
import { spectrum } from "./sky.js";

export const BUBBLES = { pool: 48, size: [.035, .11], life: [3.5, 9], drag: 1.6, carry: 1.1, sink: .03, pop: .09 };

export function createBubbles(scene) {
  const N = BUBBLES.pool, at = new Float32Array(N * 12), bub = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  for (let i = 0; i < N; i++) {
    for (let v = 0; v < 4; v++) cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2);
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  }
  const g = new THREE.BufferGeometry();
  const aAt = new THREE.BufferAttribute(at, 3).setUsage(THREE.DynamicDrawUsage), aB = new THREE.BufferAttribute(bub, 4).setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", aAt);
  g.setAttribute("bubble", aB);   // (radius, film seed, fade, -)
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0) };
  const B = attribute("bubble", "vec4"), C = attribute("corner", "vec2");
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(attribute("position", "vec3"), 1)).add(vec4(C.mul(B.x.mul(2)), 0, 0)));
  // the sphere: clear in the middle, coloured toward its rim where the film is seen edge-on; the colours swirl
  const c = C.mul(2), d = c.length(), nz = sqrt(float(1).sub(d.mul(d)).max(0)), rim = pow(float(1).sub(nz), 2.2);
  const film = spectrum(fract(B.y.add(float(1).sub(nz).mul(1.3)).add(U.t.mul(.07)).add(c.y.mul(.25))));
  const spot = smoothstep(.24, .04, c.sub(vec2(-.36, .4)).length()).add(smoothstep(.12, .02, c.sub(vec2(.4, -.42)).length()).mul(.4));
  mat.colorNode = vec3(.92, .96, 1).mul(.35).add(film.mul(.65)).add(spot);
  mat.opacityNode = rim.mul(.8).add(.05).mul(smoothstep(1, .93, d)).add(spot.mul(.85)).min(1).mul(B.z);
  const mesh = new THREE.Mesh(g, mat);
  mesh.name = "bubbles"; mesh.visible = false; mesh.renderOrder = 3; mesh.userData.noMerge = true;
  scene.add(mesh);
  const P = Array.from({ length: N }, () => ({ live: false, x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, r: 0, seed: Math.random(), t0: 0, life: 0, popAt: 0 }));
  let next = 0, hx = 0, hy = 0, hz = 0;
  return {
    mesh,
    blow(x, y, z, dx, dz, t, ground) {
      const b = P[next]; next = (next + 1) % N;
      const s = BUBBLES.size, l = BUBBLES.life;
      Object.assign(b, { live: true, x, y, z, vx: dx * (.5 + Math.random() * .4) + (Math.random() - .5) * .3, vy: .1 + Math.random() * .2, vz: dz * (.5 + Math.random() * .4) + (Math.random() - .5) * .3,
        r: s[0] + (s[1] - s[0]) * Math.random() ** 1.6, ground, t0: t, life: l[0] + (l[1] - l[0]) * Math.random(), popAt: 0, seed: Math.random() });
      hx = x; hy = y; hz = z;
    },
    update(t, dt) {
      U.t.value = t;
      if (!mesh.visible && !P[(next + N - 1) % N].live) return 0;   // (none in the air, none just blown: nothing to do)
      dt = Math.min(dt, .1);
      const s = WIND.strength.value, W = WIND_DIR;
      let n = 0;
      for (let i = 0; i < N; i++) {
        const b = P[i];
        let k = 0;
        if (b.live) {
          // carried by the breeze (its gusts where it is), rising and sinking a little, wobbling
          const gst = 1 + gustAt(b.x, b.z, t) * .35, wob = Math.sin(t * 2.3 + b.seed * 40) * .25;
          const tx = (W.x * BUBBLES.carry - W.y * wob) * s * gst, tz = (W.y * BUBBLES.carry + W.x * wob) * s * gst, ty = -BUBBLES.sink + Math.sin(t * .8 + b.seed * 9) * .11;
          const a = Math.min(1, dt * BUBBLES.drag);
          b.vx += (tx - b.vx) * a; b.vz += (tz - b.vz) * a; b.vy += (ty - b.vy) * a * .6;
          b.x += b.vx * dt; b.y += b.vy * dt; b.z += b.vz * dt;
          if (!b.popAt && (t - b.t0 > b.life || b.y - b.r < b.ground)) b.popAt = t;   // (its time up, or the grass)
          k = b.popAt ? 1 - (t - b.popAt) / BUBBLES.pop : Math.min(1, (t - b.t0) / .15);
          if (b.popAt && k <= 0) { b.live = false; k = 0; } else n++;
        }
        const grow = b.popAt ? 1 + (t - b.popAt) / BUBBLES.pop * .25 : 1;   // (a pop: swells a little and is gone)
        const x = b.live ? b.x : hx, y = b.live ? b.y : hy, z = b.live ? b.z : hz, r = b.live ? b.r * grow : 0;
        for (let v = i * 4; v < i * 4 + 4; v++) { at[v * 3] = x; at[v * 3 + 1] = y; at[v * 3 + 2] = z; bub[v * 4] = r; bub[v * 4 + 1] = b.seed; bub[v * 4 + 2] = k; }
      }
      mesh.visible = n > 0;
      if (n) { aAt.needsUpdate = aB.needsUpdate = true; g.computeBoundingSphere(); g.boundingSphere.radius += .3; }
      return n;
    },
  };
}
