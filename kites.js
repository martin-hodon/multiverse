// KITES on a breezy day: children on the upwind side of the green fly kites out over it -- a diamond of two colours on
// a long sagging string, its tail of bows snaking out downwind. The kite rides the wind the grass feels (grass.js: its
// way, its strength, the same gusts): it climbs as the line pays out, sways from side to side, banks into its swings,
// lifts in a gust, and now and then turns a loop; when the breeze drops away it sinks and is reeled in, and lies in the
// grass by its flyer until the wind comes back. Display only, moved on the CPU: a few dozen vertices a frame, two draws.
//
//   const kites = createKites(scene, n)
//   kites.update(t, dt, flyers)   // flyers: [{ hand: [x, y, z], ground, fly }] -- hand: where the string is held, ground:
//                                 // the ground's height there, fly: wind and weather would carry it; null: put away
//   -> [{ line, up }]             // per kite: how much string is out (m), and 0 down .. 1 aloft (the flyer's pose)
import * as THREE from "three";
import { WIND, WIND_DIR, gustAt } from "./grass.js";

export const KITES = { line: 24, payOut: 3, reelIn: 2.2, el: .66, sway: .34, loop: [25, 60], loopSecs: 2.4, size: 1.35, tail: 7, seg: .4,
  colours: [[0xc0392b, 0xf4d03f], [0x2e6db4, 0xf2eee2], [0x2c8a4a, 0xe67e22], [0x7d3c98, 0xf5cba7]], string: 0x4a3e32 };

export function createKites(scene, n) {
  const T = KITES.tail, perMesh = 12 + T * 6, perLine = 2 * 10 + 2 * T;
  const pos = new Float32Array(n * perMesh * 3), col = new Float32Array(n * perMesh * 3), lpos = new Float32Array(n * perLine * 3);
  const c = new THREE.Color();
  for (let k = 0; k < n; k++) {   // the colours stay: the diamond's upper half one, its lower the other; the bows by turns
    const [a, b] = KITES.colours[k % KITES.colours.length].map((h) => c.setHex(h).toArray());
    for (let v = 0; v < perMesh; v++) col.set(v < 6 ? a : v < 12 ? b : ((v - 12) / 6 | 0) % 2 ? a : b, (k * perMesh + v) * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute("color", new THREE.BufferAttribute(col, 3));
  const mesh = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));
  const lg = new THREE.BufferGeometry();
  lg.setAttribute("position", new THREE.BufferAttribute(lpos, 3).setUsage(THREE.DynamicDrawUsage));
  const lines = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: KITES.string }));
  mesh.name = "kites"; lines.name = "kite strings";
  for (const o of [mesh, lines]) { o.visible = false; o.userData.noMerge = true; scene.add(o); }
  const K = Array.from({ length: n }, (_, k) => ({ line: 0, el: .1, az: 0, azV: 0, ph: k * 2.3 + 1, nextLoop: 20 + k * 9, loopAt: -1e9,
    tail: Array.from({ length: T + 1 }, () => new THREE.Vector3()), fresh: true }));
  const W = WIND_DIR, P = new THREE.Vector2(-W.y, W.x);   // (downwind, and across it)
  const H = new THREE.Vector3(), C = new THREE.Vector3(), d = new THREE.Vector3(), u = new THREE.Vector3(), r = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  const tmp = new THREE.Vector3(), q = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
  const out = K.map(() => ({ line: 0, up: 0 }));
  let mi = 0, li = 0;
  const put = (v) => { pos[mi++] = v.x; pos[mi++] = v.y; pos[mi++] = v.z; };
  const seg = (a, b) => { lpos[li++] = a.x; lpos[li++] = a.y; lpos[li++] = a.z; lpos[li++] = b.x; lpos[li++] = b.y; lpos[li++] = b.z; };
  return {
    mesh, lines, kites: K,
    update(t, dt, flyers) {
      const any = flyers?.some((f) => f);
      mesh.visible = lines.visible = !!any;
      if (!any) return out;
      dt = Math.min(dt, .1);
      const s = WIND.strength.value;
      mi = li = 0;
      K.forEach((k, i) => {
        const f = flyers[i];
        if (!f) { for (let v = 0; v < perMesh * 3; v++) pos[mi++] = 0; for (let v = 0; v < perLine * 3; v++) lpos[li++] = 0; k.fresh = true; return; }
        H.set(...f.hand);
        const full = KITES.line * (.85 + .15 * Math.sin(k.ph * 3));
        k.line = f.fly ? Math.min(full, k.line + KITES.payOut * dt) : Math.max(0, k.line - KITES.reelIn * dt);
        const aloft = Math.min(1, k.line / full), gust = gustAt(C.x || H.x, C.z || H.z, t) / 1.85;
        // where it rides: higher with more string out and in a gust; swaying across the wind; now and then a loop
        k.el += (Math.max(.08, Math.min(1.25, .12 + aloft * (KITES.el + .14 * gust + .12 * (s - .85)))) - k.el) * Math.min(1, dt * 1.4);
        const az = (KITES.sway * Math.sin(t * .37 + k.ph) + .14 * Math.sin(t * 1.13 + k.ph * 2) + .05 * Math.sin(t * 3.1 + k.ph)) * aloft;
        if (aloft > .95 && t > k.nextLoop) { k.loopAt = t; k.nextLoop = t + KITES.loop[0] + Math.random() * (KITES.loop[1] - KITES.loop[0]); }
        const lu = (t - k.loopAt) / KITES.loopSecs, loop = lu >= 0 && lu < 1 ? lu * lu * (3 - 2 * lu) * Math.PI * 2 : 0;
        const A = az + Math.sin(loop) * .3 * (k.ph % 2 > 1 ? 1 : -1), E = k.el + (Math.cos(loop) - 1) * .3;
        k.azV += ((A - (k.azLast ?? A)) / Math.max(dt, 1e-3) - k.azV) * Math.min(1, dt * 4); k.azLast = A;
        const ground = k.line < 1.2;   // (in: lying in the grass beside its flyer, face up)
        if (ground) {
          C.set(H.x + W.x * 1.1 + P.x * .5, f.ground + .04, H.z + W.y * 1.1 + P.y * .5);
          u.set(W.x, 0, W.y); r.set(P.x, 0, P.y);
        } else {
          d.set(Math.cos(E) * (Math.cos(A) * W.x + Math.sin(A) * P.x), Math.sin(E), Math.cos(E) * (Math.cos(A) * W.y + Math.sin(A) * P.y));
          C.copy(H).addScaledVector(d, k.line);
          C.y = Math.max(C.y, f.ground + .5);
          u.copy(up).addScaledVector(d, -d.y).normalize(); r.crossVectors(d, u);   // (its face across the line, its top to the sky)
          const roll = (k.ph % 2 > 1 ? -loop : loop) + Math.max(-.6, Math.min(.6, k.azV * .9)), cr = Math.cos(roll), sr = Math.sin(roll);
          tmp.copy(u).multiplyScalar(cr).addScaledVector(r, sr); r.multiplyScalar(cr).addScaledVector(u, -sr); u.copy(tmp);
        }
        const S = KITES.size;
        q[0].copy(C).addScaledVector(u, .32 * S); q[1].copy(C).addScaledVector(r, -.36 * S); q[2].copy(C).addScaledVector(u, -.62 * S); q[3].copy(C).addScaledVector(r, .36 * S);
        for (const v of [q[0], q[1], C, q[0], C, q[3], q[1], q[2], C, C, q[2], q[3]]) put(v);
        // the tail: each bow pulled downwind (and down, and side to side in a snake) and held its length from the last
        const tl = k.tail;
        if (k.fresh) { for (let j = 0; j <= T; j++) tl[j].copy(q[2]).addScaledVector(u, -j * KITES.seg); k.fresh = false; }
        tl[0].copy(q[2]);
        for (let j = 1; j <= T; j++) {
          const w = Math.sin(t * 6 - j * .9 + k.ph) * .9;
          tl[j].x += (W.x * s * 1.6 * (1 + gust * .4) + P.x * w) * dt * 3; tl[j].z += (W.y * s * 1.6 * (1 + gust * .4) + P.y * w) * dt * 3; tl[j].y -= dt * 2.2;
          tl[j].y = Math.max(tl[j].y, f.ground + .03);
          tmp.subVectors(tl[j], tl[j - 1]); const L = tmp.length() || 1; tl[j].copy(tl[j - 1]).addScaledVector(tmp, KITES.seg / L);
        }
        for (let j = 1; j <= T; j++) {   // a bow across the tail at each knot
          tmp.subVectors(tl[j], tl[j - 1]).normalize();
          const a = q[0].copy(tl[j]).addScaledVector(r, -.15).addScaledVector(tmp, -.06), b = q[1].copy(tl[j]).addScaledVector(r, .15).addScaledVector(tmp, -.06);
          const cc = q[3].copy(tl[j]).addScaledVector(r, .15).addScaledVector(tmp, .06), dd = d.copy(tl[j]).addScaledVector(r, -.15).addScaledVector(tmp, .06);
          for (const v of [a, b, cc, a, cc, dd]) put(v);
        }
        // the string: from the hand to the kite, sagging the more the slacker the wind
        const sag = ground ? 0 : k.line * .045 * (1.5 - Math.min(1.2, s)), prev = q[0].copy(H);
        for (let j = 1; j <= 10; j++) {
          const a = j / 10, nx = q[1].lerpVectors(H, C, a); nx.y -= sag * 4 * a * (1 - a);
          seg(prev, nx); prev.copy(nx);
        }
        for (let j = 1; j <= T; j++) seg(tl[j - 1], tl[j]);
        out[i].line = k.line; out[i].up = aloft;
      });
      g.attributes.position.needsUpdate = true; lg.attributes.position.needsUpdate = true;
      // (the bounds: a sphere round the flyers big enough for the strings' reach -- not recomputed from the vertices)
      for (const geo of [g, lg]) { geo.boundingSphere ??= new THREE.Sphere(); geo.boundingSphere.center.copy(H); geo.boundingSphere.radius = KITES.line * 1.2 + 12; }
      return out;
    },
  };
}
