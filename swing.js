// A SWING on the green: an A-frame of rough poles with a crossbeam, two ropes and a board seat. A child swings on it
// and another stands behind and pushes each time it comes back; the seat rides a pendulum (SWING.rate swings a second:
// what ropes of SWING.rope metres swing at by themselves) and hangs still when no one is on it. The frame is blocks.js
// logs (one mesh, built once); the seat a little block mesh moved each frame, the ropes two lines.
//
//   const swing = createSwing(scene, { at: [x, y, z], beam: [bx, bz] })   // beam: the crossbeam's way (unit, level)
//   swing.update(t, dt, on) -> { seat: [x, y, z], theta, face }            // on: someone is swinging (the swing eases to rest without)
//   swing.behind                                                           // where the pusher stands, [x, z], and its facing
import * as THREE from "three";
import { blockMesh } from "./blocks.js";

export const SWING = { H: 2.5, rope: 2.0, half: 1.05, splay: .95, swing: .55, rate: .36, ease: .25 };

export function createSwing(scene, { at, beam }) {
  const [cx, gy, cz] = at, bx = beam[0], bz = beam[1], sx = -bz, sz = bx;   // (s: the way it swings, across the beam)
  const wood = [.47, .35, .22], ends = [.78, .66, .48], H = SWING.H, legL = Math.hypot(H, SWING.splay), tilt = Math.atan2(H, SWING.splay);
  const yawOf = (x, z) => Math.atan2(-z, x);
  const B = [{ at: [cx, gy + H, cz], size: [SWING.half * 2 + .3, .15, .15], yaw: yawOf(bx, bz), colour: wood, ends, shape: "log" }];
  const legs = [];   // (where each leg meets the ground: index.html bumps you into them)
  for (const e of [-1, 1]) for (const d of [-1, 1]) {   // each end an A: two legs from the ground either side up to the beam
    const ex = cx + bx * SWING.half * e, ez = cz + bz * SWING.half * e;
    legs.push([ex - sx * d * SWING.splay, ez - sz * d * SWING.splay]);
    B.push({ at: [ex - sx * d * SWING.splay / 2, gy + H / 2, ez - sz * d * SWING.splay / 2], size: [legL, .12, .12], yaw: yawOf(sx * d, sz * d), tilt, colour: wood, ends, shape: "log" });
  }
  const frame = blockMesh(B, "swing frame");
  const seat = blockMesh([{ at: [0, 0, 0], size: [.32, .045, .5], colour: [.56, .42, .27] }], "swing seat");
  seat.rotation.y = yawOf(sx, sz);   // (its long side along the beam)
  const rp = new Float32Array(12), rg = new THREE.BufferGeometry();
  rg.setAttribute("position", new THREE.BufferAttribute(rp, 3).setUsage(THREE.DynamicDrawUsage));
  const ropes = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0x8a7656 }));
  ropes.name = "swing ropes";
  for (const o of [frame, seat, ropes]) { o.userData.noMerge = true; scene.add(o); }
  let amp = 0;
  const out = { seat: [0, 0, 0], theta: 0, face: yawOf(sx, sz) }, axis = new THREE.Vector3(bx, 0, bz), yawQ = seat.quaternion.clone();
  const reach = SWING.rope * Math.sin(SWING.swing);
  return {
    frame, seat, ropes, legs, rate: SWING.rate, at: [cx, cz],   // (at: where it stands -- the frame's blocks are in world coordinates, its position the origin)
    behind: { x: cx - sx * (reach + .6), z: cz - sz * (reach + .6), face: yawOf(sx, sz) },
    update(t, dt, on) {
      amp += ((on ? SWING.swing : 0) - amp) * Math.min(1, dt * SWING.ease);
      const th = amp * Math.sin(t * SWING.rate * Math.PI * 2), py = gy + H;
      const x = cx + sx * Math.sin(th) * SWING.rope, y = py - Math.cos(th) * SWING.rope, z = cz + sz * Math.sin(th) * SWING.rope;
      seat.position.set(x, y, z);
      seat.quaternion.setFromAxisAngle(axis, -th).multiply(yawQ);   // (tipped with the ropes: its board square to them)
      for (let i = 0; i < 2; i++) {
        const e = i ? .23 : -.23, o = i * 6;
        rp[o] = cx + bx * e; rp[o + 1] = py; rp[o + 2] = cz + bz * e; rp[o + 3] = x + bx * e; rp[o + 4] = y + .02; rp[o + 5] = z + bz * e;
      }
      rg.attributes.position.needsUpdate = true; rg.computeBoundingSphere();
      out.seat[0] = x; out.seat[1] = y + .025; out.seat[2] = z; out.theta = th;
      return out;
    },
  };
}
