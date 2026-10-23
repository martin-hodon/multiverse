// LEAPFROG: two children by the green taking turns -- one crouched, hands on its knees (the frog: skeleton.js an.rest and
// the `puff` gesture), the other running up behind, vaulting over its back with its hands on it, landing a step beyond
// and crouching there in turn; the one that was the frog gets up and goes again. So the pair works its way along a line
// LEAPFROG.length metres long, and back. Display only, on the frame's clock, like the dances: it moves the figures
// (composite animals: position, rotY, animT, ampT, restT/rest, gesture, pitch).
//
//   const leap = createLeapfrog([a, b], { start: [x, z], dir: [dx, dz], groundH })   // figures { an, gait, legs }; legs: legLength
//   leap.update(t, dt)
export const LEAPFROG = { length: 10, takeoff: .75, over: 1.5, cycle: 2.2, legs: [.45, .75], height: .75, crouch: .24, vault: .35, round: 1.1 };

export function createLeapfrog(kids, { start, dir, groundH }) {
  const L = Math.hypot(dir[0], dir[1]) || 1;
  let fx = dir[0] / L, fz = dir[1] / L, gone = 0;                 // the way along the line, how far the frog has come along it
  let frog = kids[0], jumper = kids[1], t0 = 0;
  let F = [start[0], start[1]], S = [start[0] - fx * LEAPFROG.over, start[1] - fz * LEAPFROG.over];   // the frog's spot; where the jumper set off from
  const put = (k, x, z, lift, face) => { k.an.position.set(x, groundH(x, z) + lift, z); k.an.rotY = face; };
  return {
    line: { start, dir: [fx, fz] },   // (the line, as laid out: LEAPFROG.length + LEAPFROG.over along dir)
    update(t, dt) {
      let u = (t - t0) / LEAPFROG.cycle;
      if (u >= 1 || u < 0) {   // a jump done: the jumper is the frog now, a step on; the old frog jumps next, from where it is
        S = F; F = [F[0] + fx * LEAPFROG.over, F[1] + fz * LEAPFROG.over]; gone += LEAPFROG.over;
        if (gone >= LEAPFROG.length) { fx = -fx; fz = -fz; gone = 0; }   // (the line's end: back the other way -- the next one runs round)
        [frog, jumper] = [jumper, frog]; t0 = t; u = 0;
      }
      const face = Math.atan2(-fz, fx);
      // the frog: crouched on its spot, facing along the line
      put(frog, F[0], F[1], 0, face);
      Object.assign(frog.an, { restT: frog.legs * LEAPFROG.crouch, ampT: 0, gesture: "puff", work: 1, pitch: 0 });
      // the jumper: up at once and running from where it set off to just behind the frog (round it, if it set off ahead),
      // then over its back, then down a step beyond it
      const [r0, r1] = LEAPFROG.legs, J = jumper.an, T = [F[0] - fx * LEAPFROG.takeoff, F[1] - fz * LEAPFROG.takeoff];
      let x, z, lift = 0, run = 0, pitch = 0, rot = face;
      if (u < r0) {
        const k = u / r0, ahead = (S[0] - F[0]) * fx + (S[1] - F[1]) * fz > -LEAPFROG.takeoff;
        const C = [(S[0] + T[0]) / 2 - fz * (ahead ? LEAPFROG.round : 0), (S[1] + T[1]) / 2 + fx * (ahead ? LEAPFROG.round : 0)];   // (a curve round the frog)
        x = (1 - k) * (1 - k) * S[0] + 2 * k * (1 - k) * C[0] + k * k * T[0]; z = (1 - k) * (1 - k) * S[1] + 2 * k * (1 - k) * C[1] + k * k * T[1];
        const dx = 2 * (1 - k) * (C[0] - S[0]) + 2 * k * (T[0] - C[0]), dz = 2 * (1 - k) * (C[1] - S[1]) + 2 * k * (T[1] - C[1]);
        if (Math.hypot(dx, dz) > 1e-3) rot = Math.atan2(-dz, dx);
        run = 1;
      } else if (u < r1) {
        const k = (u - r0) / (r1 - r0), s = -LEAPFROG.takeoff + (LEAPFROG.takeoff + LEAPFROG.over) * k;
        x = F[0] + fx * s; z = F[1] + fz * s; lift = 4 * LEAPFROG.height * k * (1 - k); pitch = -LEAPFROG.vault * Math.sin(k * Math.PI);
      } else { x = F[0] + fx * LEAPFROG.over; z = F[1] + fz * LEAPFROG.over; }
      put(jumper, x, z, lift, rot);
      J.restT = u >= r1 ? jumper.legs * LEAPFROG.crouch : 0; J.pitch = pitch;
      if (u < r1) J.rest = Math.min(J.rest ?? 0, jumper.legs * .05);   // (up at once: a child springs up)
      J.ampT = run; J.runT = run; J.animT = (J.animT ?? 0) + (run ? dt * 3.2 / jumper.gait : 0);
      const vaulting = u >= r0 && u < r1;
      J.gesture = vaulting ? "leap" : u >= r1 ? "puff" : undefined; J.work = vaulting || u >= r1 ? 1 : 0;
    },
  };
}
