// FIREWORKS (F): a show over the town -- rockets climbing on a trail of sparks, then bursting into a PEONY (a sphere of
// stars), a RING, or a WILLOW (gold that hangs and droops a long time), white-hot at first, then their colour, then
// crackling out as they fall. Heard where you stand: the whistle going up, the BANG arriving late by the speed of sound
// (a burst 300 m off is heard a second after it is seen), the crackle after.
//
// All on the GPU: a pool of BURSTS, each a set of sparks whose place at any moment comes from the burst's centre, its
// start, its kind and the spark's own direction (drag and gravity worked out in closed form); the CPU only hands a burst
// its numbers when it is launched. One mesh, one draw, in the night-glow scene (drawn after the darkening, so the sparks
// keep their full brightness).
//
//   const fw = createFireworks(scene, { centre: [x, y, z], audio: () => ctx, camera })
//   fw.show()                // a show of a dozen or so rockets over the next half minute
//   fw.update(t)             // every frame; fw.active() while any burst is in the air
import * as THREE from "three";
import { attribute, uniform, vec3, vec4, float, uv, smoothstep, exp, sin, fract, mix, clamp, max, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { SR, toBuffer, play } from "./dsp.js";

export const FIREWORKS = { pool: 18, sparks: 150, rise: [1.4, 2.0], height: [55, 85], spread: 45, rockets: [12, 18], over: 28 };
const COLOURS = [[1, .25, .2], [.25, 1, .35], [.3, .5, 1], [1, .85, .3], [.85, .4, 1], [1, 1, 1], [1, .55, .15], [.3, .95, 1]];
const KIND = { peony: 0, ring: 1, willow: 2 };

export function createFireworks(scene, { centre, audio = () => null, camera }) {
  const N = FIREWORKS.pool, M = FIREWORKS.sparks, V = N * M * 4;
  const dirA = new Float32Array(V * 4), burstA = new Float32Array(V * 4), colA = new Float32Array(V * 4), riseA = new Float32Array(V * 2), cr = new Float32Array(V * 2), idx = new Uint32Array(N * M * 6);
  const dir = new THREE.Vector3();
  for (let b = 0; b < N; b++) for (let k = 0; k < M; k++) {
    // a direction on the sphere, evenly spread (a Fibonacci sphere), and its own speed and sparkle phase
    const i = k + .5, phi = Math.acos(1 - 2 * i / M), th = Math.PI * (1 + Math.sqrt(5)) * i;
    dir.set(Math.sin(phi) * Math.cos(th), Math.cos(phi), Math.sin(phi) * Math.sin(th));
    const q = (b * M + k) * 4;
    for (let v = 0; v < 4; v++) {
      dirA.set([dir.x, dir.y, dir.z, .85 + Math.random() * .3], (q + v) * 4);
      cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (q + v) * 2);
      burstA.set([0, -1e4, 0, -1e4], (q + v) * 4);   // (x, y, z, start time: never yet)
      colA.set([1, 1, 1, k === 0 ? -1 : 0], (q + v) * 4);   // (colour, kind; the first spark of a burst is its ROCKET: -1)
    }
    idx.set([q, q + 1, q + 3, q, q + 3, q + 2], (b * M + k) * 6);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(V * 3), 3));
  const aDir = new THREE.BufferAttribute(dirA, 4), aBurst = new THREE.BufferAttribute(burstA, 4), aCol = new THREE.BufferAttribute(colA, 4), aRise = new THREE.BufferAttribute(riseA, 2);
  for (const a of [aBurst, aCol, aRise]) a.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("riseA", aRise);
  g.setAttribute("dirA", aDir); g.setAttribute("burst", aBurst); g.setAttribute("colK", aCol);
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));

  const U = { t: uniform(0) };
  const D = attribute("dirA", "vec4"), B = attribute("burst", "vec4"), C = attribute("colK", "vec4"), Q = attribute("corner", "vec2"), RI = attribute("riseA", "vec2");
  const age = U.t.sub(B.w);                                   // since the burst (negative: the rocket still climbing)
  const kind = C.w, rocket = kind.lessThan(-.5).select(float(1), float(0)), willow = kind.greaterThan(1.5).select(float(1), float(0));
  const ring = kind.greaterThan(.5).and(kind.lessThan(1.5)).select(float(1), float(0));
  // the star's way out: v0 slowing under drag k, falling under gravity g -- x(t) = v0 (1 - e^-kt)/k, y also - g t^2/2
  const k = mix(float(1.7), float(.9), willow), v0 = D.w.mul(mix(float(25), float(16), willow)), grav = mix(float(4.5), float(7.5), willow);
  // (a ring: the stars all out in one flat circle -- standing more or less upright, facing a way of its own)
  const rn = vec3(sin(B.x.mul(1.7).add(B.w)), .35, sin(B.z.mul(1.3).add(B.w.mul(.7)))).normalize();
  const d = mix(D.xyz, D.xyz.sub(rn.mul(D.xyz.dot(rn))).normalize(), ring);
  const a = max(age, 0);
  const out = d.mul(v0.mul(float(1).sub(exp(k.negate().mul(a)))).div(k)).sub(vec3(0, grav.mul(a).mul(a).mul(.5), 0));
  // the rocket: below the burst point, climbing the last of its rise (age from -rise to 0), a little wobble
  const climb = vec3(sin(U.t.mul(31).add(B.x)).mul(.15), age.div(RI.x).pow(2).mul(RI.y).negate(), 0);   // (from the ground, slowing to the top)
  const life = mix(float(2.2), float(4.5), willow);
  const alive = rocket.mul(age.lessThan(0).select(float(1), float(0))).add(rocket.oneMinus().mul(age.greaterThan(0).and(age.lessThan(life)).select(float(1), float(0))));
  const P = B.xyz.add(mix(out, climb, rocket));
  const size = mix(mix(float(1.0), float(1.25), willow), float(1.3), rocket).mul(alive).mul(smoothstep(.06, 0, a).mul(rocket.oneMinus()).mul(1.4).add(1));   // (swollen at the bursting instant)
  const view = cameraViewMatrix.mul(vec4(P, 1));
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false });
  mat.vertexNode = cameraProjectionMatrix.mul(view.add(vec4(Q.mul(size), 0, 0)));
  // the light: white-hot, then its colour, then fading -- and crackling (on and off) as it dies; a willow goes gold
  const f = clamp(a.div(life), 0, 1);
  const hot = smoothstep(.12, 0, f), dim = smoothstep(1, .55, f);
  const crackle = mix(float(1), smoothstep(.35, .8, fract(sin(D.x.mul(91).add(U.t.mul(13))).mul(4375.5))).mul(2), smoothstep(.6, .75, f));
  const col = mix(mix(C.xyz, vec3(1, .78, .35), willow), vec3(1, 1, .95), hot).mul(dim).mul(crackle);
  const rcol = vec3(1, .85, .55);
  const r = uv().sub(.5).mul(2).length();
  const spot = smoothstep(1, 0, r).pow(2.4).add(smoothstep(.25, 0, r));
  const vCol = mix(col, rcol, rocket);
  mat.colorNode = vCol.mul(spot).mul(alive).mul(1.6);
  mat.opacityNode = float(1);
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false; mesh.name = "fireworks";
  mesh.visible = false;
  scene.add(mesh);

  // ---- the show: a queue of launches; each takes the oldest burst of the pool
  const queue = [];
  let next = 0, lastEnd = -1;
  const launch = (now) => {
    const b = next++ % N, rise = FIREWORKS.rise[0] + Math.random() * (FIREWORKS.rise[1] - FIREWORKS.rise[0]);
    const x = centre[0] + (Math.random() - .5) * FIREWORKS.spread * 2, z = centre[2] + (Math.random() - .5) * FIREWORKS.spread;
    const y = centre[1] + FIREWORKS.height[0] + Math.random() * (FIREWORKS.height[1] - FIREWORKS.height[0]);
    const kd = Math.random() < .25 ? "willow" : Math.random() < .3 ? "ring" : "peony", c = COLOURS[Math.floor(Math.random() * COLOURS.length)];
    const t0 = now + rise;                                    // the burst's moment; the rocket climbs before it
    for (let s = 0; s < M; s++) for (let v = 0; v < 4; v++) {
      const q = ((b * M + s) * 4 + v) * 4;
      burstA.set([x, y, z, t0], q);
      colA.set([c[0], c[1], c[2], s === 0 ? -1 : KIND[kd]], q);
      riseA.set([rise, y - centre[1]], q / 2);
    }
    aBurst.needsUpdate = true; aCol.needsUpdate = true; aRise.needsUpdate = true;
    lastEnd = Math.max(lastEnd, t0 + 5);
    // the sounds: the whistle now, the bang when the light has gone and its sound has come the distance
    const dist = camera.position.distanceTo(new THREE.Vector3(x, y, z));
    sound("whistle", .5 / Math.max(1, dist / 60), 0);
    sound("bang", Math.min(1, 140 / Math.max(dist, 30)), rise + dist / 343);
    sound("crackle", Math.min(.8, 90 / Math.max(dist, 30)) * (kd === "willow" ? .4 : 1), rise + dist / 343 + 1.1);
  };
  let buf = null;
  const sound = (kind, gain, delay) => {
    const ctx = audio?.();
    if (!ctx) return;
    if (!buf) {
      const make = (dur, fn) => { const n = Math.round(dur * SR), x = new Float32Array(n); for (let i = 0; i < n; i++) x[i] = fn(i / SR, i); return toBuffer(x); };
      const nz = () => Math.random() * 2 - 1;
      let lp = 0, lp2 = 0;
      buf = {
        whistle: make(1.5, (t) => .35 * Math.sin(2 * Math.PI * (1400 + 900 * t) * t) * Math.min(1, t * 6) * Math.exp(-t * 1.2) + .1 * nz() * Math.exp(-t * 2)),
        bang: make(1.6, (t) => (lp = .96 * lp + .04 * nz(), lp2 = .7 * lp2 + .3 * nz(), 9 * lp * Math.exp(-t * 3.2) + 1.2 * lp2 * Math.exp(-t * 25))),
        crackle: make(1.8, (t) => (Math.random() < .004 * (1 + 3 * Math.exp(-t)) ? nz() * 1.2 : 0) * Math.exp(-t * .9)),
      };
    }
    const gnode = ctx.createGain(); gnode.gain.value = gain * .6; gnode.connect(ctx.destination);
    play(ctx, buf[kind], { dest: gnode, at: ctx.currentTime + delay });
  };
  let clock = 0;
  return {
    mesh,
    active: () => clock < lastEnd || queue.length > 0,
    show() {
      const n = FIREWORKS.rockets[0] + Math.floor(Math.random() * (FIREWORKS.rockets[1] - FIREWORKS.rockets[0]));
      for (let i = 0; i < n; i++) queue.push(clock + i * FIREWORKS.over / n + Math.random() * 1.2 + (i > n - 4 ? -1.5 : 0));   // (the finale: the last few close together)
      queue.sort((p, q) => p - q);
    },
    update(t) {
      clock = t; U.t.value = t;
      while (queue.length && queue[0] <= t) { queue.shift(); launch(t); }
      mesh.visible = t < lastEnd || queue.length > 0;
    },
  };
}
