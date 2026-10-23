// SKIPPING STONES (G): a flat pebble thrown from the hand, skimming the lake or the river. It skips while it comes in
// low and fast -- each touch takes some of its speed and kicks up a spray, and leaves rings spreading on the water --
// until it is too slow or too steep, and sinks with a plunk. On land it just lands. The count is shown when it
// sinks ("4 skips"), with a best for the visit.
//
// The water is the world's own (waterY: the surface over carved ground, -Infinity where it is dry). Three meshes, a
// draw each, and only while something is flying or spreading: the stones (lit, instanced), the RINGS on the water
// (flat quads, the rings drawn in the shader from their age) and the SPRAY (droplet cards facing the eye).
//
//   const stones = createStones(scene, { camera, groundH, waterY, audio: () => ctx, toast: (text) => ... })
//   stones.throw()          // from the eye, where it looks; throw({ p, dir }): someone else's, from p along dir (quiet)
//   stones.update(dt, t)    // every frame
import * as THREE from "three";
import { attribute, uniform, vec2, vec4, float, varying, uv, smoothstep, sin, fract, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { litMaterial } from "./light.js";
import { SR, toBuffer, play } from "./dsp.js";

export const STONES = {
  speed: 14,         // m/s out of the hand
  lift: 1.0,         // m/s up, besides the look's own pitch
  skipAngle: .62,    // radians: steeper than this into the water and it sinks (a real stone wants ~20 degrees; the banks here are high)
  skipSpeed: 3.2,    // m/s across the water it needs to skip
  keep: .8,          // of its speed left after a touch
  bounce: .62,       // of its fall turned back up
  rings: 32, drops: 96,
};

export function createStones(scene, { camera, groundH, waterY, audio = () => null, toast = () => {}, land = () => {} }) {   // land(x, z): where one comes down for good
  // ---- the stones: a flattened pebble, grey-brown, spinning flat
  const geo = new THREE.SphereGeometry(1, 10, 6).scale(.045, .014, .035);
  const col = new Float32Array(geo.attributes.position.count * 3);
  for (let i = 0; i < col.length; i += 3) col.set([.48 + Math.random() * .05, .45, .41], i);
  geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  const stoneMesh = new THREE.InstancedMesh(geo, litMaterial(), 8);
  stoneMesh.count = 0; stoneMesh.frustumCulled = false; stoneMesh.name = "skipping stones";
  scene.add(stoneMesh);
  const flying = [];

  // ---- the rings: a flat card on the water each, its rings drawn from its age (two crests and a trough, spreading)
  const U = { t: uniform(0) };
  const N = STONES.rings;
  const ringGeo = new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2);
  const born = new THREE.InstancedBufferAttribute(new Float32Array(N * 2).fill(-1e3), 2);   // start time, strength
  ringGeo.setAttribute("born", born);
  const ringMat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false });
  {
    const B = attribute("born", "vec2");
    const age = U.t.sub(B.x), life = B.y.mul(1.6).add(1.4);
    const k = varying(age.div(life)), str = varying(B.y);
    const d = uv().sub(.5).mul(2).length();                 // 0 the middle .. 1 the card's edge (the card: 2 x 3.2 m x strength)
    const r = k.pow(.6);                                     // the ring's radius, fast at first then easing
    const crest = smoothstep(.07, .0, d.sub(r).abs()).add(smoothstep(.06, .0, d.sub(r.mul(.72)).abs()).mul(.55));
    const fade = smoothstep(1, .35, k).mul(smoothstep(0, .03, k));
    ringMat.colorNode = vec4(.92, .96, 1, 1).xyz;
    ringMat.opacityNode = crest.mul(fade).mul(str.mul(.25).add(.45)).mul(k.lessThan(1).select(1, 0));
  }
  const ringMesh = new THREE.InstancedMesh(ringGeo, ringMat, N);
  ringMesh.frustumCulled = false; ringMesh.renderOrder = 3; ringMesh.name = "water rings";
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), S = new THREE.Vector3(), P = new THREE.Vector3();
  for (let i = 0; i < N; i++) ringMesh.setMatrixAt(i, M.makeScale(0, 0, 0));
  scene.add(ringMesh);
  let ringNext = 0, lastRing = -1e3;
  const ring = (x, y, z, strength, t) => {
    const i = ringNext++ % N;
    ringMesh.setMatrixAt(i, M.compose(P.set(x, y + .015, z), Q.identity(), S.setScalar(3.2 * (.6 + strength))));
    ringMesh.instanceMatrix.needsUpdate = true;
    born.setXY(i, t, strength); born.needsUpdate = true;
    lastRing = t;
  };

  // ---- the spray: droplets thrown up from a touch, falling back; cards facing the eye
  const D = STONES.drops, dropAt = new Float32Array(D * 4 * 4), dc = new Float32Array(D * 4 * 2), di = new Uint32Array(D * 6);
  for (let i = 0; i < D; i++) { for (let v = 0; v < 4; v++) dc.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); di.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6); }
  const dg = new THREE.BufferGeometry(), dropAttr = new THREE.BufferAttribute(dropAt, 4);
  dropAttr.setUsage(THREE.DynamicDrawUsage);
  dg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(D * 12), 3));
  dg.setAttribute("dropAt", dropAttr);
  dg.setAttribute("corner", new THREE.BufferAttribute(dc, 2));
  dg.setAttribute("uv", new THREE.BufferAttribute(dc.map((v) => v + .5), 2));
  dg.setIndex(new THREE.BufferAttribute(di, 1));
  const dropMat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false });
  {
    const A = attribute("dropAt", "vec4"), C = attribute("corner", "vec2");   // xyz, its size (0: gone)
    dropMat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(A.xyz, 1)).add(vec4(C.mul(A.w), 0, 0)));
    const d = uv().sub(.5).mul(2).length();
    dropMat.colorNode = vec4(.93, .97, 1, 1).xyz;
    dropMat.opacityNode = smoothstep(1, .3, d).mul(.85);
  }
  const dropMesh = new THREE.Mesh(dg, dropMat);
  dropMesh.frustumCulled = false; dropMesh.renderOrder = 4; dropMesh.name = "spray";
  scene.add(dropMesh);
  const drops = [];   // { p, v, life, size }
  const spray = (x, y, z, n, up, vx, vz) => {
    for (let i = 0; i < n && drops.length < D; i++) {
      const a = Math.random() * Math.PI * 2, s = .4 + Math.random() * 1.1;
      drops.push({ p: new THREE.Vector3(x, y + .02, z), v: new THREE.Vector3(Math.cos(a) * s + vx * .25, up * (.6 + Math.random() * .7), Math.sin(a) * s + vz * .25),
                   size: .025 + Math.random() * .035, life: 2 });
    }
  };

  // ---- the sounds: a light slap for a skip, a deep plunk for the end
  let buf = null;
  const sound = (kind, p, pitch = 1) => {
    const ctx = audio?.();
    if (!ctx) return;
    if (!buf) {
      const make = (dur, f) => { const n = Math.round(dur * SR), x = new Float32Array(n); for (let i = 0; i < n; i++) x[i] = f(i / SR); return toBuffer(x); };
      let lp = 0; const nz = () => Math.random() * 2 - 1;
      buf = {
        skip: make(.18, (t) => (lp = .45 * lp + .55 * nz(), .9 * Math.exp(-t / .025) * lp + .35 * Math.exp(-t / .05) * Math.sin(2 * Math.PI * (900 - 2500 * t) * t))),
        plunk: make(.6, (t) => (lp = .8 * lp + .2 * nz(), .8 * Math.exp(-t / .12) * Math.sin(2 * Math.PI * (300 + 500 * t) * t) + 1.4 * Math.exp(-t / .07) * lp)),
      };
    }
    const dd = camera.position.distanceTo(p);
    if (dd > 70) return;
    const g = ctx.createGain(); g.gain.value = Math.min(1, 5 / Math.max(dd, 1)) * .5; g.connect(ctx.destination);
    play(ctx, buf[kind], { dest: g, rate: pitch });
  };

  let best = 0;
  const fwd = new THREE.Vector3();
  return {
    best: () => best,
    throw(from = null) {   // from: { p, dir } -- someone else's throw (a child at the bank: index.html), quiet: no count, no fetching
      if (from) fwd.copy(from.dir); else camera.getWorldDirection(fwd);
      const p = from ? from.p.clone() : camera.position.clone().addScaledVector(fwd, .5); if (!from) p.y -= .35;
      const flat = Math.hypot(fwd.x, fwd.z) || 1;
      const pitch = Math.max(-.12, Math.min(.35, fwd.y));   // (looking down at the water still throws it out flat)
      const v = new THREE.Vector3(fwd.x / flat * STONES.speed, STONES.lift + pitch * STONES.speed * .6, fwd.z / flat * STONES.speed);
      if (flying.length >= 8) flying.shift();
      if (!from) this.last = null;
      flying.push({ p, v, spin: 0, skips: 0, rest: 0, quiet: !!from });
    },
    update(dt, t) {
      U.t.value = t;
      dt = Math.min(dt, .05);
      const steps = 4, h = dt / steps;
      for (const s of flying) {
        if (s.rest) { s.rest -= dt; continue; }
        for (let k = 0; k < steps && !s.rest; k++) {
          s.v.y -= 9.81 * h;
          s.p.addScaledVector(s.v, h);
          s.spin += h * 40;
          const w = waterY(s.p.x, s.p.z), g = groundH(s.p.x, s.p.z);
          if (w > g + .05 && s.p.y <= w) {          // on the water: skip, or sink
            const hs = Math.hypot(s.v.x, s.v.z), steep = Math.atan2(-s.v.y, hs);
            if (hs > STONES.skipSpeed && steep < STONES.skipAngle) {
              s.skips++;
              s.p.y = w + .001;
              s.v.y = -s.v.y * STONES.bounce + .4;
              s.v.x *= STONES.keep; s.v.z *= STONES.keep;
              ring(s.p.x, w, s.p.z, .35, t); spray(s.p.x, w, s.p.z, 7, 2.2, s.v.x, s.v.z);
              sound("skip", s.p, 1 + s.skips * .06 + Math.random() * .1);
            } else {
              ring(s.p.x, w, s.p.z, 1, t); spray(s.p.x, w, s.p.z, 16, 3.2, s.v.x * .3, s.v.z * .3);
              sound("plunk", s.p, .9 + Math.random() * .2);
              s.rest = -1;                          // gone
              if (s.quiet) continue;                // (someone else's: no count for you)
              this.last = { sank: [s.p.x, s.p.z], skips: s.skips };   // (where the last one ended: for the tests)
              land(s.p.x, s.p.z);
              if (s.skips) {
                best = Math.max(best, s.skips);
                toast(`${s.skips} skip${s.skips === 1 ? "" : "s"}!${s.skips === best && best > 1 ? "  (your best)" : `  (best ${best})`}`);
              } else toast("plop -- throw it flatter (look lower, at the water's near edge)");
            }
          } else if (s.p.y <= g) {                  // on land: it lands, and lies a moment
            s.p.y = g + .012; s.rest = 2.5;
            if (s.quiet) continue;
            this.last = { landed: [s.p.x, s.p.z], skips: s.skips };
            land(s.p.x, s.p.z);
            if (s.skips) toast(`${s.skips} skip${s.skips === 1 ? "" : "s"} -- and onto the bank!`);
          }
        }
      }
      for (let i = flying.length - 1; i >= 0; i--) if (flying[i].rest < 0) flying.splice(i, 1);
      stoneMesh.count = flying.length;
      flying.forEach((s, i) => stoneMesh.setMatrixAt(i, M.compose(s.p, Q.setFromEuler(new THREE.Euler(0, s.spin, .08)), S.set(1, 1, 1))));
      stoneMesh.instanceMatrix.needsUpdate = true;
      // the spray falls back
      for (const d of drops) { d.v.y -= 9.81 * dt; d.p.addScaledVector(d.v, dt); d.life -= dt; }
      for (let i = drops.length - 1; i >= 0; i--) { const d = drops[i]; if (d.life <= 0 || d.p.y < Math.max(waterY(d.p.x, d.p.z), groundH(d.p.x, d.p.z)) - .02) drops.splice(i, 1); }
      dropAt.fill(0);
      drops.forEach((d, i) => { for (let v = 0; v < 4; v++) dropAt.set([d.p.x, d.p.y, d.p.z, d.size], (i * 4 + v) * 4); });
      dropAttr.needsUpdate = true;
      dg.setDrawRange(0, drops.length * 6);
      dropMesh.visible = drops.length > 0;
      ringMesh.visible = t - lastRing < 5;
      stoneMesh.visible = flying.length > 0;
    },
    // a ring spreading on the water from anything else that touches it (a fish's leap, a duck landing)
    ring: (x, y, z, strength = .5) => ring(x, y, z, strength, U.t.value),
    // ...droplets thrown up from the water (n of them, so fast, leaning dx, dz): a swimmer's or a child's splashing, quiet
    spray: (x, y, z, n, v, dx = 0, dz = 0) => spray(x, y, z, n, v, dx, dz),
    // ...and a SPLASH: something big going in (you, jumping in): a ring, spray as high as it came in hard, a plunge
    splash(x, y, z, strength = 1) {
      ring(x, y, z, Math.min(1.4, .5 + strength * .5), U.t.value);
      spray(x, y, z, Math.round(10 + 22 * Math.min(1.5, strength)), 1.6 + 2.4 * Math.min(1.5, strength), 0, 0);
      sound("plunk", new THREE.Vector3(x, y, z), .55 + Math.random() * .1);
    },
  };
}
