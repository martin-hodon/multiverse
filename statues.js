// STATUES (2026-10-04): figures CARVED -- the people engine's own figure (people.js makePerson: a pose, a dress or another
// time's style, what it holds) with every part, its cloth, its head and its hair marked STONE (skeleton.js `stone`:
// shell.js stoneAt paints it marble, bronze, gold or limestone with the world's light and the metal's highlight, the
// cloth keeping its shape and its folds), and what it holds carved too (tools.js `@stone<m>`). A building says where
// they stand -- `statue` markers (architecture.js lifeOf): on a pedestal it built, in a niche, along a balustrade, in a
// temple's cella -- and how they are: { kind, pose (stand | guard | sit), style, outfit, hold: { R, L } (items: the
// figure's right hand and its left), stone, scale (x a person: a cult statue's colossus), seed, face }.
import { makePerson } from "./people.js";
import { handIndex } from "./tools.js";
import { STONES } from "./shell.js";

// one statue's figure: the person, carved
export function statueDef(st) {
  const m = STONES[st.stone] ?? STONES.marble;
  const height = 1.78 * (st.scale ?? 1);
  const pd = makePerson({ seed: st.seed ?? 1, kind: st.kind ?? "man", adult: true, still: true, height,
                          pose: st.pose === "sit" ? "sit" : st.pose === "guard" ? "guard" : undefined,
                          ...(st.outfit ? { outfit: st.outfit } : {}), ...(st.style ? { style: st.style } : {}) });
  // (carved cloth is FULL: every cut of a garment closed -- a skirt's hem, a sleeve's mouth -- where real cloth is a shell
  //  open at its edge; shell.js closes a SOLID cut's far end, and fills a standing piece where no layer lies)
  for (const p of pd.parts) { p.stone = m; p.fur = false; if (p.clip) p.clip = { ...p.clip, solid: true, lid: false }; }
  if (pd.face) pd.face = { ...pd.face, stone: m };
  return { pd, m };
}

// the statues of every site into one herd: `sites` [{ x, z, statues }] (the statues' places in the site's frame);
// returns the herd and its holders (for tools.place: what each holds, carved)
export function placeStatues(herd, sites) {
  const holders = [];
  for (const s of sites) for (const st of s.statues) {
    const { pd, m } = statueDef(st), p = herd.add(pd);
    p.position.set(s.x + st.x, st.pose === "sit" ? pd.sitAt(st.y) : st.y + .005, s.z + st.z);
    p.rotY = st.h; p.animT = 0;
    // (the rig's sides are mirrored: its "L" hand is the figure's RIGHT)
    const sc = st.scale ?? 1;   // (what it holds is as big as it is)
    if (st.hold?.R) holders.push({ an: p, tool: st.hold.R + "@stone" + m, hand: handIndex(pd, "L"), scale: sc });
    if (st.hold?.L) holders.push({ an: p, tool: st.hold.L + "@stone" + m, hand: handIndex(pd, "R"), scale: sc });
  }
  return holders;
}
