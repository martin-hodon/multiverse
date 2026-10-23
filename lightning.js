// LIGHTNING in a storm: a bolt -- a jagged channel from the cloud base to the ground, a branch or two forking off it --
// that flickers two or three times in half a second, and the whole sky lit with it. Drawn in the night-glow scene
// (after the darkening: by night the flash is a real one), so it is drawn whenever a strike is under way. The host
// strikes (strike(km, bearing)) and plays the thunder itself, late by the distance (index.html).
//
//   const lt = createLightning(glowScene, camera)
//   lt.strike(km, bearing)    // a bolt km away (0.5 .. 6), in a direction (radians; random if left out)
//   lt.update(t)              // every frame; lt.active() while one is showing
import * as THREE from "three";
import { attribute, uniform, vec3, vec4, float, uv, smoothstep, positionGeometry } from "three/tsl";

const SEGS = 26;

export function createLightning(scene, camera) {
  // the bolt: a ribbon along its points, turned to face the eye when it strikes; a few hundred vertices, rebuilt each strike
  const MAXV = 4 * SEGS * 3;
  const pos = new Float32Array(MAXV * 3), across = new Float32Array(MAXV);
  const g = new THREE.BufferGeometry();
  const pa = new THREE.BufferAttribute(pos, 3); pa.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("position", pa);
  const aa = new THREE.BufferAttribute(across, 1); aa.setUsage(THREE.DynamicDrawUsage);
  g.setAttribute("across", aa);
  g.setDrawRange(0, 0);
  const U = { f: uniform(0) };
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, side: THREE.DoubleSide });
  const A = attribute("across", "float");
  const core = smoothstep(1, 0, A.abs()).pow(1.5);
  mat.colorNode = vec3(.85, .88, 1).mul(core.mul(1.6).add(.25)).mul(U.f);
  mat.opacityNode = float(1);
  const bolt = new THREE.Mesh(g, mat);
  bolt.frustumCulled = false; bolt.name = "lightning"; bolt.visible = false;
  scene.add(bolt);
  // the flash: the whole screen lifted, a cold blue-white, additively
  const flashMat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, fog: false });
  flashMat.vertexNode = vec4(positionGeometry.xy, 0, 1);
  flashMat.colorNode = vec3(.22, .24, .31).mul(U.f).mul(uv().y.mul(.6).add(.4));   // (brighter overhead)
  flashMat.opacityNode = float(1);
  const flash = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), flashMat);
  flash.frustumCulled = false; flash.renderOrder = 99; flash.visible = false;
  scene.add(flash);

  let t0 = -1e9, now = 0, pulses = [];
  const v = new THREE.Vector3(), right = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  const build = (km, bearing) => {
    const d = km * 1000, base = camera.position;
    const gx = base.x + Math.cos(bearing) * d, gz = base.z + Math.sin(bearing) * d, top = 160 + Math.random() * 80;
    // the main channel: down from the cloud in jagged steps, wandering sideways; and a branch or two off it
    const chans = [[]];
    let x = gx + (Math.random() - .5) * d * .05, z = gz + (Math.random() - .5) * d * .05;
    for (let i = 0; i <= SEGS; i++) {
      const y = top * (1 - i / SEGS);
      chans[0].push([x, y, z]);
      x += (Math.random() - .5) * 14; z += (Math.random() - .5) * 14;
    }
    for (let b = 0; b < 2; b++) {
      const at = 4 + Math.floor(Math.random() * 10), p = chans[0][at], ch = [p.slice()];
      let [bx, by, bz] = p; const dx = (Math.random() - .5) * 30, dz = (Math.random() - .5) * 30;
      for (let i = 0; i < 8; i++) { bx += dx * .3 + (Math.random() - .5) * 8; by -= top / SEGS * 1.1; bz += dz * .3 + (Math.random() - .5) * 8; ch.push([bx, by, bz]); }
      chans.push(ch);
    }
    // ribbons facing the eye: each segment widened across the view
    camera.getWorldDirection(v);
    right.crossVectors(v, up).normalize();
    let n = 0;
    const w0 = Math.max(1.2, d * .0016);   // (a few pixels wide at any distance)
    for (const [ci, ch] of chans.entries()) for (let i = 0; i + 1 < ch.length && n + 4 <= MAXV; i++) {
      const w = w0 * (ci ? .55 : 1);
      for (const [p, s] of [[ch[i], -1], [ch[i], 1], [ch[i + 1], -1], [ch[i + 1], 1]]) {
        pos.set([p[0] + right.x * w * s, p[1], p[2] + right.z * w * s], n * 3); across[n] = s; n++;
      }
    }
    const idx = [];
    for (let q = 0; q < n; q += 4) idx.push(q, q + 1, q + 3, q, q + 3, q + 2);
    g.setIndex(idx);
    pa.needsUpdate = true; aa.needsUpdate = true;
    g.setDrawRange(0, idx.length);
  };
  return {
    active: () => now - t0 < .8,
    strike(km = 1 + Math.random() * 4, bearing = Math.random() * Math.PI * 2) {
      build(km, bearing);
      t0 = now;
      // the flicker: two or three return strokes, the first the brightest, closer bolts brighter
      pulses = [[0, 1], [.11 + Math.random() * .05, .65], ...(Math.random() < .6 ? [[.26 + Math.random() * .1, .45]] : [])];
      this.km = km;
    },
    update(t) {
      now = t;
      const a = t - t0;
      let f = 0;
      for (const [at, k] of pulses) f = Math.max(f, k * Math.exp(-Math.max(0, a - at) * 18) * (a >= at ? 1 : 0));
      const near = Math.min(1, 2.2 / Math.max(.6, this.km ?? 2));
      U.f.value = f * (.55 + .45 * near);
      bolt.visible = flash.visible = f > .01;
    },
  };
}
