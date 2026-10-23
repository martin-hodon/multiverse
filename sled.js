// SLEDDING: while snow lies, children take turns down a slope near the town on wooden sleds -- sitting on it, tipped
// with the hill, picking up speed (gravity down the slope against the snow's drag, to a cap), snow kicked up behind;
// at the bottom they get off and trudge back up pulling the sled behind them, wait a moment at the top, and go again.
// Each child is two figures, the one sitting on the sled and the one walking, shown in turn. Display only, on the
// frame's clock (like the dances): it moves the figures (composite animals: position, rotY, pitch, animT, ampT, hidden)
// and the sleds (meshes: position, rotation).
//
//   const sledding = createSledding(scene, { kids: [{ sit, walk }], top: [x, z], dir: [dx, dz], len, groundH, blockMesh, puff })
//     sit / walk: { an, gait, sitAt }; puff(x, y, z, dx, dz, t): snow thrown up (t: the frame's clock)
//   sledding.update(t, dt, on)   // on: snow lies, by day (off: everyone hidden)
import * as THREE from "three";

export const SLED = { accel: 2.6, drag: .35, max: 6.5, push: 1.4, stagger: 3.5, walk: .9, wait: [1.5, 4], behind: 1.15, seat: .2, puff: .04 };

export function createSledding(scene, { kids, top, dir, len, groundH, blockMesh, puff = () => {} }) {
  const L = Math.hypot(dir[0], dir[1]) || 1, fx = dir[0] / L, fz = dir[1] / L, yaw = Math.atan2(-fz, fx);
  const wood = [.55, .38, .22], dark = [.3, .2, .12];
  // a sled in its own frame (x forward): two runners curled up at the front, a slatted seat on them
  const blocks = [];
  for (const s of [-1, 1]) {
    blocks.push({ at: [0, .03, s * .2], size: [1, .04, .04], colour: dark });
    blocks.push({ at: [.55, .1, s * .2], size: [.18, .04, .04], tilt: .9, colour: dark });   // (the runner's curl)
    for (const x of [-.3, .1, .4]) blocks.push({ at: [x, .1, s * .2], size: [.04, .12, .04], colour: dark });   // (the posts)
  }
  for (const x of [-.36, -.18, 0, .18, .36]) blocks.push({ at: [x, .17, 0], size: [.15, .03, .52], colour: wood });   // (the slats)
  // the ropes (one line a sled, from the child's hand to the sled's front while it pulls it up the hill)
  const rp = new Float32Array(kids.length * 6), rg = new THREE.BufferGeometry();
  rg.setAttribute("position", new THREE.BufferAttribute(rp, 3).setUsage(THREE.DynamicDrawUsage));
  const ropes = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0x8a7656 }));
  ropes.name = "sled ropes"; ropes.frustumCulled = false; ropes.visible = false; ropes.userData.noMerge = true; scene.add(ropes);
  const _front = new THREE.Vector3();
  const P = (s) => [top[0] + fx * s, top[1] + fz * s];
  const slope = (s) => { const [ax, az] = P(s - .6), [bx, bz] = P(s + .6); return Math.atan2(groundH(ax, az) - groundH(bx, bz), 1.2); };   // (+: downhill ahead)
  const K = kids.map((k, i) => {
    const sled = blockMesh(blocks, "sled");
    sled.rotation.order = "YZX"; sled.visible = false; scene.add(sled);
    return { ...k, i, sled, mode: "wait", s: 0, v: 0, till: 0, out: false, side: (i - (kids.length - 1) / 2) * 2.2 };
  });
  const place = (k, s, side, yawNow, onIt) => {
    const [x0, z0] = P(s), x = x0 - fz * side, z = z0 + fx * side, g = groundH(x, z), a = slope(s);
    k.sled.position.set(x, g, z); k.sled.rotation.set(0, yawNow, yawNow === yaw ? -a : a);
    if (onIt) {   // sitting on it, tipped with it
      const an = k.sit.an;
      an.position.set(x, k.sit.sitAt(g + SLED.seat), z); an.rotY = yaw; an.pitch = -a;
    }
    return [x, g, z];
  };
  return {
    kids: K, top, dir: [fx, fz], len,   // (the run, as laid out)
    update(t, dt, on) {
      let pulling = false;
      for (const k of K) {
        k.sled.visible = on; k.sit.an.hidden = !on || k.mode === "up"; k.walk.an.hidden = !on || k.mode !== "up";
        if (!on) { k.out = false; continue; }
        if (!k.out) { k.out = true; k.mode = "wait"; k.s = 0; k.till = t + 1 + k.i * SLED.stagger; }   // (just come out: at the top, one after the other)
        if (k.mode === "wait") {   // at the top, sitting on the sled
          place(k, 0, k.side, yaw, true);
          if (t > k.till) { k.mode = "down"; k.v = SLED.push; }   // (a push off with the hands)
        } else if (k.mode === "down") {   // down the hill: faster while it is steep, the snow dragging
          const a = slope(k.s);
          k.v = Math.min(SLED.max, Math.max(.3, k.v + (SLED.accel * Math.sin(a) * 3.8 - SLED.drag * k.v) * dt));
          k.s += k.v * dt;
          const [x, g, z] = place(k, k.s, k.side, yaw, true);
          if (k.v > 2 && Math.random() < k.v * SLED.puff) puff(x - fx * .5, g + .05, z - fz * .5, -fx, -fz, t);
          if (k.s >= len) { k.mode = "up"; k.walk.an.animT = 0; }
        } else {   // back up on foot, the sled pulled behind on its rope
          k.s = Math.max(0, k.s - SLED.walk * dt);
          const [x0, z0] = P(k.s), x = x0 - fz * (k.side + .4), z = z0 + fx * (k.side + .4), an = k.walk.an;
          an.position.set(x, groundH(x, z), z); an.rotY = yaw + Math.PI; an.ampT = 1;
          an.animT += SLED.walk * dt / k.walk.gait;
          place(k, Math.min(len, k.s + SLED.behind), k.side + .4, yaw + Math.PI, false);
          k.sled.updateMatrixWorld(); _front.set(.6, .14, 0).applyMatrix4(k.sled.matrixWorld);   // (the rope: from the hand -- low at its side -- to the sled's curled front)
          rp.set([x - fx * .12, an.position.y + .62, z - fz * .12, _front.x, _front.y, _front.z], k.i * 6); pulling = true;
          if (k.s <= 0) { rp.fill(0, k.i * 6, k.i * 6 + 6); k.mode = "wait"; k.till = t + SLED.wait[0] + Math.random() * (SLED.wait[1] - SLED.wait[0]); }
        }
      }
      ropes.visible = pulling;
      if (pulling) rg.attributes.position.needsUpdate = true;
    },
  };
}
