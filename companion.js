// A DOG AT YOUR HEEL: whistle (X) and the nearest dog comes running, barks, and from then on keeps at your left heel --
// trotting when you walk, running when you run or ride, standing looking up at you when you stop; whistle again and it
// goes back to its own wandering. Throw a stone (G) while it is with you and it races off to where the stone came down,
// noses about for it a moment, brings it back to your feet and barks: again! (Into the water it will not go: it stops at
// the edge -- though it swims across the river to reach you, its back just under the water.) And when something shy
// is near -- a hare, a cat, a hen, a fox -- off it goes after it, barking, for a few seconds (the prey runs from it as
// from you: index.html shyStep), and trots back to you when it gives up. While it is yours its wanderer is frozen (index.html wanderStep skips it) and it is moved here, every frame.
//
//   const dog = createCompanion({ groundY, wet, runs, bark, prey })   // prey(): the shy wanderers it may chase   // groundY(x, z, y): where it stands; wet(x, z): the water's
//                                                               //   level where it is deep enough to swim, else null
//   dog.call({ w, a })        // this dog (its wanderer and figure) comes to heel
//   dog.release()             // ...and goes off on its own again
//   dog.fetch(x, z)           // a stone came down there
//   dog.update(dt, { x, z, yaw })   // where you are and the way you look
export const DOG = { heel: [1.3, .7], run: 7, swim: 1.3, accel: 12, turn: 7, nose: .9, far: 150, depth: .42,
                     chase: { near: 10, for: 5, again: 20, lost: 25, speed: 4.5, close: 1 } };   // (speed: a romp, not a kill; close: near enough -- a bark, and it lets it go)   // a chase: within near m, at most `for` s, then not for `again` s   // depth: its back under the surface, swimming

export function createCompanion({ groundY, wet = () => null, runs, bark = () => {}, prey = () => [] }) {
  let dog = null, mode = null, goal = null, pause = 0, quarry = null, chaseT = 0, calm = 0;
  const turnTo = (w, dx, dz, dt) => {
    const want = Math.atan2(-dz, dx), dh = ((want - w.heading + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
    w.heading += Math.max(-DOG.turn * dt, Math.min(DOG.turn * dt, dh));
    return Math.cos(dh);
  };
  return {
    get dog() { return dog; },
    get mode() { return mode; },
    get pos() { return dog?.w.p ?? null; },   // (where it is: shy animals run from it too)
    call(d) { dog = d; d.w.frozen = true; d.w.v = 0; mode = "heel"; goal = null; bark(d); },
    release() {
      if (!dog) return;
      const w = dog.w;
      w.frozen = false; w.moving = false; w.until = 0;
      w.setT(w.animT, undefined, undefined, false, false);
      dog = null; mode = null;
    },
    fetch(x, z) { if (dog && wet(x, z) === null) { mode = "fetch"; goal = [x, z]; pause = 0; } },
    update(dt, me) {
      if (!dog) return;
      if (dog.a.down) { dog = null; mode = null; return; }   // (struck down: combat.js holds its wanderer now)
      const w = dog.w, p = w.p;
      if (Math.hypot(p.x - me.x, p.z - me.z) > DOG.far) {   // (left far behind -- a gallop, a flight: it finds you)
        p.x = me.x + Math.sin(me.yaw) * 3; p.z = me.z + Math.cos(me.yaw) * 3; mode = "heel";
      }
      calm = Math.max(0, calm - dt);
      if (mode === "heel" && !calm) {   // something shy close by: after it!
        for (const q of prey()) if (!q.frozen && Math.hypot(q.p.x - p.x, q.p.z - p.z) < DOG.chase.near) { mode = "chase"; quarry = q; chaseT = 0; bark(dog); break; }
      }
      if (mode === "chase") {
        chaseT += dt;
        const qd = Math.hypot(quarry.p.x - p.x, quarry.p.z - p.z);
        if (qd < DOG.chase.close) bark(dog);
        if (chaseT > DOG.chase.for || qd < DOG.chase.close || qd > DOG.chase.lost || quarry.frozen) { mode = "heel"; quarry = null; calm = DOG.chase.again; }
      }
      const sy = Math.sin(me.yaw), cy = Math.cos(me.yaw);   // (your forward on the ground: -sy, -cy)
      let tx, tz;
      if (mode === "fetch") [tx, tz] = goal;
      else if (mode === "chase") { tx = quarry.p.x; tz = quarry.p.z; }
      else if (mode === "back") { tx = me.x - sy * .9; tz = me.z - cy * .9; }   // (to your feet, in front of you)
      else { tx = me.x + sy * DOG.heel[0] - cy * DOG.heel[1]; tz = me.z + cy * DOG.heel[0] + sy * DOG.heel[1]; }   // (behind you, on your left)
      const dx = tx - p.x, dz = tz - p.z, d = Math.hypot(dx, dz);
      let want = 0;
      if (mode === "chase") want = DOG.chase.speed;
      else if (mode === "fetch") {
        if (d < .35) { pause += dt; if (pause > DOG.nose) { mode = "back"; pause = 0; } }   // nosing about for it
        else want = DOG.run;
      } else if (mode === "back") {
        if (d < .35) { mode = "heel"; bark(dog); }   // dropped at your feet: again!
        else want = Math.min(DOG.run, 1 + d * 1.5);
      } else want = d < .3 ? 0 : d < 4 ? Math.max(.7, d * 1.1) : Math.min(DOG.run, d * 1.3);
      // turning toward where it is going -- or, standing, toward you
      const facing = want > 0 ? turnTo(w, dx, dz, dt) : (turnTo(w, me.x - p.x, me.z - p.z, dt), 1);
      want *= Math.max(.2, facing);
      const sw = wet(p.x, p.z);
      if (sw !== null) want = Math.min(want, DOG.swim);   // (paddling: slow)
      w.v = (w.v ?? 0) + Math.max(-DOG.accel * 1.5 * dt, Math.min(DOG.accel * dt, want - (w.v ?? 0)));
      p.x += Math.cos(w.heading) * w.v * dt; p.z -= Math.sin(w.heading) * w.v * dt;
      const lv = wet(p.x, p.z);
      p.y = lv === null ? groundY(p.x, p.z, p.y) : Math.max(groundY(p.x, p.z, p.y), lv - DOG.depth);
      w.apply(w.heading);
      if (w.v > .05) w.animT += dt * w.v / w.base;
      else w.animT += (Math.round(w.animT * 2 * w.hz) / (2 * w.hz) - w.animT) * Math.min(1, dt * 10);
      w.setT(w.animT, undefined, undefined, w.v > .1, w.v > .1 && runs(w.v, w.base));
    },
  };
}
