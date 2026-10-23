// FISHING from the bank: R casts a line -- the float lands out on the water where you look (a red and white float, a
// ring spreading from it), bobs, and after a while it bobs harder, dips under: a bite! R again quickly and you strike
// and land a fish (what kind, how big, how many today); too slow and it is gone with the bait, and your line comes in.
// R while it floats reels in. Only where the water is deep enough to fish, a few metres out.
//
//   const fishing = createFishing(scene, { waterY, groundH, ring, splash, toast, sound })
//   fishing.key(camera, yaw, t)   // R: cast, strike or reel in
//   fishing.update(t)
import { blockMesh } from "./blocks.js";

export const FISHING = { reach: [4, 9], deep: .5, wait: [4, 14], bite: 1.3, fish: [["a roach", .15, .3], ["a perch", .18, .35], ["a trout", .25, .5], ["a carp", .3, .7], ["a pike", .45, 1]] };

export function createFishing(scene, { waterY, groundH, ring = () => {}, splash = () => {}, toast = () => {}, sound = () => {} }) {
  const float = blockMesh([{ at: [0, .035, 0], size: [.07, .07, .07], shape: "ball", colour: [.85, .12, .1] },
                           { at: [0, -.005, 0], size: [.06, .06, .06], shape: "ball", colour: [.95, .95, .92] },
                           { at: [0, .1, 0], size: [.012, .09, .012], colour: [.9, .8, .2] }], "fishing float");
  float.visible = false;
  scene.add(float);
  let state = null, caught = 0;   // state: { x, z, y, bite: when it bites, phase: "float" | "bite" }
  const wet = (x, z) => waterY(x, z) > groundH(x, z) + FISHING.deep;
  return {
    get caught() { return caught; }, get state() { return state; },
    key(camera, yaw, t) {
      if (!state) {   // cast: the first deep water straight ahead, 4-9 m out
        const fx = -Math.sin(yaw), fz = -Math.cos(yaw);
        let at = null;
        for (let d = FISHING.reach[0]; d <= FISHING.reach[1]; d += .5) { const x = camera.position.x + fx * d, z = camera.position.z + fz * d; if (wet(x, z)) { at = [x, z]; break; } }
        if (!at) { toast("No water deep enough to fish there -- stand on the bank, facing the river"); return; }
        state = { x: at[0], z: at[1], y: waterY(at[0], at[1]), phase: "float", bite: t + FISHING.wait[0] + Math.random() * (FISHING.wait[1] - FISHING.wait[0]) };
        float.visible = true; ring(state.x, state.y, state.z, .35); sound("cast");
        toast("Cast! Watch the float... (R to strike when it goes under)");
        return;
      }
      if (state.phase === "bite") {   // struck in time: a fish
        const [name, lo, hi] = FISHING.fish[Math.floor(Math.random() * FISHING.fish.length)], kg = lo + Math.random() * (hi - lo);
        caught++; splash(state.x, state.y, state.z, .5); sound("catch");
        toast(`You caught ${name}, ${(kg * 1000).toFixed(0)} g! (${caught} today)`);
      } else toast("You reel in your line");
      state = null; float.visible = false;
    },
    update(t) {
      if (!state) return;
      const S = state;
      if (S.phase === "float" && t > S.bite) { S.phase = "bite"; S.until = t + FISHING.bite; ring(S.x, S.y, S.z, .5); sound("bite"); }
      if (S.phase === "bite" && t > S.until) { toast("It got away with the bait -- R to cast again"); state = null; float.visible = false; return; }
      // bobbing on the ripples; nibbling before the bite (little tugs), then pulled under
      const nib = S.phase === "float" && S.bite - t < 2 ? Math.max(0, Math.sin(t * 13)) * .025 : 0;
      const dip = S.phase === "bite" ? -.09 - .03 * Math.sin(t * 20) : 0;
      float.position.set(S.x, S.y + Math.sin(t * 2.1) * .008 - nib + dip, S.z);
    },
  };
}
