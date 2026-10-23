// HIDE AND SEEK (2026-10-23): the two children at leapfrog ask you to play when you come up to them by day (index.html:
// click). You count -- twenty seconds, eyes shut if you play fair -- while each runs off along the paths to a place you
// cannot see from where you stand (round a house's corner, behind a haycock: the caller's `spots`, judged by what stands
// between your eyes and a child crouched there) and crouches. "Ready or not!": you go looking. A child is FOUND when you
// come within HIDE.find metres of it, or face it within HIDE.spot with nothing between you; it laughs and runs back to
// where you counted. All found -- or HIDE.give seconds gone, and they come out of their own accord -- and once they are
// all back there the game is over: back to leapfrog. On the frame's clock, like the leapfrog it interrupts: your part is yours alone (as at tag).
//
//   const hs = createHideSeek(kids, { groundH, route, spots, seen, onYou })
//     kids: [{ an, gait, legs }] (gait: gaitBase's stride); route(a, b) -> [[x, z], ...] the paths' way; spots(from, n) -> up to n places [x, z]
//     unseen from `from`; seen(x, z) -> whether you see a child crouched there now; onYou(what, kid): "count", "ready",
//     "found", "all", "giveup"
//   hs.start(t, [x, z])            // you, where you count
//   hs.step(t, dt, [x, z], facing) -> true while the game is on (facing: [fx, fz], your look along the ground)
import { laneFrom, alongLane } from "./paths.js";

export const HIDE = { count: 20, run: 2.6, find: 1.8, spot: 7, cone: .93, give: 180, crouch: .3, home: 1.2 };

export function createHideSeek(kids, { groundH, route, spots, seen, onYou = () => {} }) {
  let mode = null, t0 = 0, home = null, said = 0;
  const K = kids.map((k) => ({ ...k, way: null, s: 0, hid: false, found: false }));
  const send = (k, to) => { const w = route([k.an.position.x, k.an.position.z], to); k.way = w && w.length > 1 ? laneFrom(w, true) : null; k.s = 0; };
  const pose = (k, x, z, h, moving) => {
    k.an.position.set(x, groundH(x, z), z); k.an.rotY = h;
    k.an.ampT = moving ? 1 : 0; k.an.runT = moving ? 1 : 0; k.an.restT = !moving && k.hid && !k.found ? k.legs * HIDE.crouch : 0;
    k.an.gesture = undefined; k.an.work = 0;
  };
  return {
    kids: K,
    get mode() { return mode; },
    start(t, you) {
      mode = "count"; t0 = t; home = you; said = 0;
      const places = spots(you, K.length);
      K.forEach((k, i) => { k.hid = false; k.found = false; k.to = places[i] ?? null; if (k.to) send(k, k.to); else k.way = null; });
      onYou("count");
    },
    step(t, dt, you, facing) {
      if (!mode) return false;
      for (const k of K) {   // running: to its hiding place, or home once found
        if (!k.way) continue;
        const [x, z, h, done] = alongLane(k, k.way, dt, HIDE.run);
        pose(k, x, z, h, true);
        k.an.animT = (k.an.animT ?? 0) + HIDE.run * dt / k.gait;
        if (done) { k.way = null; k.hid = !k.found; pose(k, x, z, h + Math.PI, false); }
      }
      if (mode === "back") { if (!K.some((k) => k.way)) mode = null; return !!mode; }   // (the game over: home before leapfrog again)
      if (mode === "count") {
        if (t - t0 >= HIDE.count) { mode = "seek"; onYou("ready"); }
        return true;
      }
      // seeking: a child found when you are on it, or look at it with nothing between
      for (const k of K) {
        if (k.found || !k.hid) continue;
        const dx = k.an.position.x - you[0], dz = k.an.position.z - you[1], d = Math.hypot(dx, dz);
        const looking = d < HIDE.spot && (dx * facing[0] + dz * facing[1]) / Math.max(d, 1e-3) > HIDE.cone;
        if (d < HIDE.find || (looking && seen(k.an.position.x, k.an.position.z))) {
          k.found = true; k.hid = false; onYou("found", k);
          send(k, [home[0] + (K.indexOf(k) - .5) * HIDE.home, home[1]]);
        }
      }
      const left = K.filter((k) => !k.found && k.to);
      if (!left.length) { mode = "back"; onYou("all"); return true; }
      if (t - t0 > HIDE.count + HIDE.give) {   // too long: they come out
        for (const k of left) { k.found = true; k.hid = false; send(k, [home[0] + (K.indexOf(k) - .5) * HIDE.home, home[1]]); }
        mode = "back"; onYou("giveup");
      }
      return true;
    },
  };
}
