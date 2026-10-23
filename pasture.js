// THE SHEPHERD'S FLOCK: on the open country beyond the town a shepherd walks a slow round, staff in hand, stopping now
// and then a while to let them graze; his sheep follow in a loose bunch behind him -- each making for its own place in
// the flock behind him, never into another -- heads down to the grass whenever they stand; and his dog runs wide
// circles round them, now one way, now the other. Pure logic on the frame (display only, like the dances): it moves
// the figures (composite animals: position, rotY, animT, ampT, runT, nodT).
//
//   const pasture = createPasture({ shepherd, sheep, dog, route, groundH })   // figures { an, gait, graze, rest }; route [[x, z]...] a loop;
//                                                                             groundH(x, z, figure)
//   pasture.update(t, dt)
export const PASTURE = { walk: .55, stop: [14, 26], go: [20, 40], behind: 4, spread: 2.6, sheep: 1.3, gap: 1.1, dogR: 9, dog: 4.2, lie: .4 };   // lie: the share of the flock lying down through a stop

export function createPasture({ shepherd, sheep, dog, route, groundH, seed = 1 }) {
  let s = 0, stopTill = 0, goTill = PASTURE.go[0], dogA = 0, dogDir = 1, flipAt = 15;
  const L = [0]; for (let i = 1; i <= route.length; i++) { const a = route[i - 1], b = route[i % route.length]; L.push(L[i - 1] + Math.hypot(b[0] - a[0], b[1] - a[1])); }
  const total = L.at(-1), r = (() => { let x = seed * 9301 + 49297; return () => ((x = (x * 9301 + 49297) % 233280) / 233280); })();
  const at = (d) => {   // a point on the loop, and its heading
    d = ((d % total) + total) % total;
    let i = 1; while (L[i] < d) i++;
    const a = route[i - 1], b = route[i % route.length], u = (d - L[i - 1]) / Math.max(1e-6, L[i] - L[i - 1]);
    return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, Math.atan2(-(b[1] - a[1]), b[0] - a[0])];
  };
  const step = (f, x, z, dt, maxV) => {   // a figure toward x, z: turning, walking as fast as the distance asks (up to maxV)
    const an = f.an, p = an.position, dx = x - p.x, dz = z - p.z, d = Math.hypot(dx, dz);
    const v = d < .25 ? 0 : Math.min(maxV, d * .8);
    if (v > 0) {
      const want = Math.atan2(-dz, dx), dh = ((want - an.rotY + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
      an.rotY += Math.max(-3 * dt, Math.min(3 * dt, dh));
      const k = Math.max(.2, Math.cos(dh)) * v * dt;
      p.x += Math.cos(an.rotY) * k; p.z -= Math.sin(an.rotY) * k;
    }
    p.y = groundH(p.x, p.z, f);   // (f: the figure -- the caller may cache by it: index.html groundCached)
    f.animT = (f.animT ?? 0) + v * dt / f.gait; an.animT = f.animT; an.ampT = v > .1 ? 1 : 0;
    return v;
  };
  // (everyone starts where they belong)
  { const [x, z] = at(0); shepherd.an.position.set(x, groundH(x, z), z); sheep.forEach((f, i) => { f.slot = [(r() - .5) * 2 * PASTURE.spread, -PASTURE.behind - r() * PASTURE.spread]; f.an.position.set(x - 3 - i * .4, groundH(x, z), z + (r() - .5) * 3); }); if (dog) dog.an.position.set(x + 6, groundH(x, z), z); }
  return {
    update(t, dt) {
      // the shepherd: along his round, and a while still every so often
      if (t > goTill && t > stopTill) { stopTill = t + PASTURE.stop[0] + r() * (PASTURE.stop[1] - PASTURE.stop[0]); goTill = stopTill + PASTURE.go[0] + r() * (PASTURE.go[1] - PASTURE.go[0]); for (const f of sheep) f.lie = r() < PASTURE.lie; }   // (a long stop: some of them lie down)
      const walking = t > stopTill;
      if (walking) s += PASTURE.walk * dt;
      const [hx, hz, hh] = at(s), sp = shepherd.an;
      step(shepherd, hx, hz, dt, PASTURE.walk * 1.4);
      if (!walking) sp.ampT = 0;
      // the sheep: each to its place in the flock behind him (turned with him), kept apart; grazing when it stands
      const c = Math.cos(hh), sn = Math.sin(hh);
      let cx = 0, cz = 0;
      for (const f of sheep) {
        const [ox, oz] = f.slot;   // (across, behind: in his frame -- x forward, -z left)
        let tx = sp.position.x + c * oz + sn * ox, tz = sp.position.z - sn * oz + c * ox;   // (forward (c, -sn), right (sn, c))
        for (const o of sheep) if (o !== f) { const dx = f.an.position.x - o.an.position.x, dz = f.an.position.z - o.an.position.z, d = Math.hypot(dx, dz); if (d < PASTURE.gap && d > 1e-3) { tx += dx / d * (PASTURE.gap - d) * 2; tz += dz / d * (PASTURE.gap - d) * 2; } }
        const v = step(f, tx, tz, dt, PASTURE.sheep);
        const down = !walking && v < .1 && f.lie && f.rest > 0;   // (lying through the stop, head up -- skeleton.js an.rest)
        f.an.restT = down ? f.rest : 0;
        f.an.nodT = v < .1 && f.graze && !down ? -f.graze : 0;
        cx += f.an.position.x; cz += f.an.position.z;
      }
      // the dog: wide circles round the flock, one way and then the other
      if (dog && sheep.length) {
        cx /= sheep.length; cz /= sheep.length;
        if (t > flipAt) { dogDir = -dogDir; flipAt = t + 12 + r() * 18; }
        dogA += dogDir * dt * PASTURE.dog / PASTURE.dogR;
        const v = step(dog, cx + Math.cos(dogA) * PASTURE.dogR, cz + Math.sin(dogA) * PASTURE.dogR, dt, PASTURE.dog * 1.2);
        dog.an.runT = v > 2 ? 1 : 0;
      }
    },
  };
}
