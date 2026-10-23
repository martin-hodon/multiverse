// CHILDREN PLAYING TAG on the green outside the town: one of them is "it" and chases the nearest of the others; they
// scatter, running away when it comes near and curving round along the green's edge rather than out of it, and jog
// about or stand getting their breath back when it is far. A touch and the caught one is it: they stop, count for a
// moment while the rest run off, and go after someone -- never straight back at the one who caught them. A long sprint
// tires a runner (`tire`: seconds to spent, seconds to recover, how much slower spent), and the chaser puts on a burst
// over the last two metres -- so the chase ends in a catch, sooner or later.
// The game is pure logic on the world's fixed tick (index.html wanderStep), from the children's own state and a
// seeded stream: deterministic like every wanderer. It moves the figures (composite animals: position, rotY, animT,
// ampT, runT) and calls onTag(x, z, kid) at each catch.
// YOU CAN PLAY: step on the green (player() gives where you are, null when you are not on foot) and you are one of
// them -- it may come after you, and a touch makes you it (onYou("caught")): then catch one yourself (onYou("tagged")),
// they run from you as from any of them. Walk off the green while you are it and the nearest child takes over
// (onYou("left")); the first time you come near, onYou("near"). (Your part is yours alone: a guest's game would go its own way from there.)
//
// SENT OFF THE GREEN: send(ways, then) takes the children out of the game, each along its own way ([[x, z], ...] from
// where it is; null: it stays where it is) at a run, and THEN, when all have got there: "in" (gone in at a door --
// home at nightfall: k.in, the caller hides them), "held" (standing there until sent on: the maypole's ring), or
// "play" (the game again). Still on the world's tick, and from their own state: deterministic as the game is.
//
//   const game = createTag(kids, { centre: [x, z], radius, groundH, seed, onTag, player, onYou })   // kids: [{ an, base }]
//   game.step(t, dt)
//   game.it()       // which child is it (kids.length: you)
//   game.send(ways, then); game.mode   // "play" | "going" | "in" | "held"
import { rng } from "./flora.js";
import { runs } from "./species.js";
import { laneFrom, alongLane } from "./paths.js";

export const TAG = { radius: 9, chase: 3.4, burst: 1.2, flee: 3.1, tire: [6, 5, .4], jog: 1.1, reach: .5, fear: 6.5, count: 1.8, noBack: 4, turn: 7, accel: 7, rest: [1.5, 5],
  way: 2.3 };   // (way: m/s, running home or wherever they are sent)

export function createTag(kids, { centre, radius = TAG.radius, groundH, seed = 1, onTag = () => {}, player = () => null, onYou = () => {} }) {
  const r = rng(seed * 131 + 9), [cx, cz] = centre;
  const K = kids.map((k, i) => {
    const a = i / kids.length * Math.PI * 2, d = radius * (.3 + r() * .4);
    return { ...k, x: cx + Math.cos(a) * d, z: cz + Math.sin(a) * d, h: r() * Math.PI * 2, v: 0, goal: null, until: 0, animT: r() * 4, tired: 0 };
  });
  const Y = { you: true, x: 0, z: 0, h: 0, v: 0, in: false }, YOU = K.length;   // you, when you are on the green
  let it = 0, countTill = TAG.count, lastIt = -1, noBackTill = 0;
  const near = (o, skip = -1) => { let b = 0, bd = 1e9; K.forEach((k, j) => { const d = Math.hypot(k.x - o.x, k.z - o.z); if (j !== skip && d < bd) { bd = d; b = j; } }); return [b, bd]; };
  const turnTo = (k, dx, dz, dt) => {   // the body turns toward the way it wants to go, so they run in curves
    const want = Math.atan2(-dz, dx);
    const dh = ((want - k.h + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
    k.h += Math.max(-TAG.turn * dt, Math.min(TAG.turn * dt, dh));
    return Math.cos(dh);                // (how much it already faces that way: slow down to turn round)
  };
  const place = (k) => {
    k.an.position.set(k.x, groundH(k.x, k.z), k.z);
    k.an.rotY = k.h; k.an.animT = k.animT;
    k.an.ampT = k.v > .15 ? 1 : 0; k.an.runT = runs(k.v, k.base) ? 1 : 0;
  };
  K.forEach(place);
  let mode = "play", then = "play";
  // along their ways, at a run -- and in, or held, or back to playing, when all are there
  const going = (dt) => {
    let left = 0;
    for (const k of K) {
      if (k.way) {
        let done; [k.x, k.z, k.h, done] = alongLane(k, k.way, dt, TAG.way); k.v = TAG.way;
        k.animT += dt * k.v / k.base;
        if (done) { k.way = null; k.v = 0; k.in = then === "in"; } else left++;
      } else k.v = 0;
      place(k);
    }
    if (!left) mode = then;
  };
  return {
    it: () => it,
    kids: K,
    get mode() { return mode; },
    send(ways, after) {
      then = after; mode = "going";
      K.forEach((k, i) => { const w = ways[i]; k.way = w && w.length > 1 ? laneFrom(w, true) : null; k.s = 0; k.in = false; k.goal = null; });
      if (after === "in") for (const k of K) if (!k.way) k.in = true;   // (no way home: in at once)
    },
    step(t, dt) {
      if (mode === "going") return going(dt);
      if (mode !== "play") return;
      const p = player(), was = Y.in;
      Y.in = !!p && Math.hypot(p.x - cx, p.z - cz) < radius + 2;
      if (p && !Y.told && Math.hypot(p.x - cx, p.z - cz) < radius + 15) { Y.told = true; onYou("near"); }   // (once: an invitation)
      if (Y.in) { const mx = p.x - Y.x, mz = p.z - Y.z; Y.v = was ? Math.hypot(mx, mz) / dt : 0; if (Y.v > .05) Y.h = Math.atan2(-mz, mx); Y.x = p.x; Y.z = p.z; }
      if (it === YOU && !Y.in) { it = near(Y)[0]; countTill = t + TAG.count; lastIt = -1; onYou("left"); }
      const A = Y.in ? [...K, Y] : K, I = A[it];
      if (it === YOU && t >= countTill) {   // you are it: a touch catches whoever you reach
        const [j, d] = near(Y, lastIt !== YOU && t < noBackTill ? lastIt : -1);
        if (d < TAG.reach + .35) { lastIt = YOU; it = j; countTill = t + TAG.count; noBackTill = t + TAG.noBack; K[j].v = 0; onYou("tagged", K[j]); }
      }
      for (const [i, k] of K.entries()) {
        let dx = 0, dz = 0, want = 0;
        if (i === it) {
          if (t < countTill) { dx = cx - k.x; dz = cz - k.z; want = 0; }   // counting (facing the middle)
          else {   // after the nearest it may catch, a little ahead of where they run
            let best = null, bd = 1e9;
            for (const [j, o] of A.entries()) {
              if (j === it || (j === lastIt && t < noBackTill)) continue;
              const d = Math.hypot(o.x - k.x, o.z - k.z);
              if (d < bd) { bd = d; best = o; }
            }
            k.target = best;
            if (best) {
              const lead = Math.min(.5, bd / TAG.chase * .4);
              dx = best.x + Math.cos(best.h) * best.v * lead - k.x; dz = best.z - Math.sin(best.h) * best.v * lead - k.z;
              want = TAG.chase * (bd < 2 ? TAG.burst : 1);
              if (bd < TAG.reach) {   // caught!
                lastIt = it; it = A.indexOf(best); countTill = t + TAG.count; noBackTill = t + TAG.noBack;
                if (best.you) onYou("caught", k); else { best.v = 0; onTag(best.x, best.z, best); }
              }
            }
          }
        } else {
          const ex = k.x - I.x, ez = k.z - I.z, ed = Math.hypot(ex, ez) || 1;
          if (ed < TAG.fear) {   // away from it -- and round, not out, at the edge of the green
            dx = ex / ed; dz = ez / ed; want = TAG.flee * (t < countTill ? .8 : 1) * (1 - TAG.tire[2] * k.tired);
            const ox = k.x - cx, oz = k.z - cz, od = Math.hypot(ox, oz) || 1, edge = Math.max(0, (od - radius * .6) / (radius * .4));
            const side = (ox * ez - oz * ex) > 0 ? 1 : -1;   // (round the side it is already going)
            dx = dx * (1 - edge) + (-oz / od * side - ox / od * .6) * edge; dz = dz * (1 - edge) + (ox / od * side - oz / od * .6) * edge;
            k.goal = null;
          } else {   // safe: jog to somewhere on the green, or stand a while getting their breath back
            if (!k.goal && t > k.until) { const a = r() * Math.PI * 2, d = radius * Math.sqrt(r()) * .8; k.goal = [cx + Math.cos(a) * d, cz + Math.sin(a) * d]; }
            if (k.goal) {
              dx = k.goal[0] - k.x; dz = k.goal[1] - k.z; want = TAG.jog;
              if (Math.hypot(dx, dz) < .4) { k.goal = null; k.until = t + TAG.rest[0] + r() * (TAG.rest[1] - TAG.rest[0]); }
            } else { dx = -ex; dz = -ez; want = 0; }   // (watching it)
          }
        }
        // apart: a child never runs through another (or you) -- but the one it is reaching for
        if (i !== it) k.target = null;
        for (const o of A) if (o !== k && o !== k.target) { const sx = k.x - o.x, sz = k.z - o.z, s = Math.hypot(sx, sz); if (s < .55 && s > 1e-4) { dx += sx / s * 1.5; dz += sz / s * 1.5; } }
        const facing = Math.hypot(dx, dz) > 1e-4 ? turnTo(k, dx, dz, dt) : 1;
        const target = want * Math.max(.25, facing);
        k.tired = Math.min(1, Math.max(0, k.tired + (k.v > 2.4 ? dt / TAG.tire[0] : -dt / TAG.tire[1])));
        k.v += Math.max(-TAG.accel * 1.5 * dt, Math.min(TAG.accel * dt, target - k.v));
        k.x += Math.cos(k.h) * k.v * dt; k.z -= Math.sin(k.h) * k.v * dt;
        const ox = k.x - cx, oz = k.z - cz, od = Math.hypot(ox, oz);
        if (od > radius) { k.x = cx + ox / od * radius; k.z = cz + oz / od * radius; }   // (the green's edge holds)
        if (k.v > .05) k.animT += dt * k.v / k.base;
        else k.animT += (Math.round(k.animT * 1.6) / 1.6 - k.animT) * Math.min(1, dt * 10);   // (legs settle when they stop)
        place(k);
      }
    },
  };
}
