// WHO IS IN A SCENE, AND WHICH SCENES COME (docs/story.md): the part of a scene that's the same whatever draws its bodies. A scene's `roles`, picked whole by
// its `variants`, its `beats` (who else may be there, each where it has room) and its `chain` (a line of bodies). What a role then IS, a solved Greek body or a medieval
// figure, is its engine's. Also a zone's deal: panels get scenes so that none comes twice before all have.
import { stream, pick } from "./seed.js";

// a scene's roles for this draw: rl the scene's own stream, `beatRng` their own (so the rest keep their poses), not: who has come already
export function rolesOf(S, rl, { sparse, not, beatRng, beatsData, chainRole } = {}) {
  let roles = S.roles, beats = S.beats;
  if (S.variants) {                                                    // (what happens, a pick of the whole: each role's pick follows from it)
    const free = S.variants.filter((v) => !Object.entries(roles).some(([k, q]) => { const c = (v[k]?.cast ?? q.cast); return c?.of ? c.of.every((n) => not?.has(n)) : not?.has(c); })), pool = free.length ? free : S.variants;   // (whoever has come already, `not`, isn't drawn again)
    const v = pool[Math.floor(rl() * pool.length)];
    roles = Object.fromEntries(Object.entries(roles).map(([k, q]) => [k, { ...q, ...v[k] }]));
    beats = v.beats ? { ...beats, ...v.beats } : beats;
  }
  if (beats && !sparse) {                                              // (whoever else is there, each where the scene has room; drawn first, and on a stream of their own so the rest keep their poses)
    const rb = beatRng(), pool = [...beats.of], free = { ...S.slots }, extra = {};
    for (let n = Math.round(pick(beats.n, rb)), i = 0; i < n && pool.length; i++) {
      const B = beatsData[pool.splice(Math.floor(rb() * pool.length), 1)[0]], slot = B.slots.find((q) => free[q]);
      if (slot) { extra[`beat${i}`] = { face: free[slot].face, ...B, at: free[slot].at }; delete free[slot]; }
    }
    roles = { ...extra, ...roles };
  }
  if (S.chain) {                                                       // a line of bodies, all alike in kind and each its own
    const n = Math.round(pick(S.chain.n, rl)), step = pick(S.chain.step, rl);
    roles = {};
    for (let i = 0; i < n; i++) {
      const at = -i * step + (rl() - .5) * 6;
      if (S.chain.rider) {                                             // (a chain of riders: each a beast and whoever is on it)
        roles[`h${i}`] = { beast: S.chain.beast, gait: S.chain.gait, face: S.chain.face, at };
        roles[`c${i}`] = { cast: S.chain.cast, action: S.chain.action, face: S.chain.face, on: `h${i}` };
      } else roles[`c${i}`] = { ...S.chain, at, ...(i ? null : S.chain.lead) };   // (the one in front may do what the rest don't: look back at them)
    }
  }
  return roles;
}

// which of a zone's scenes a tile's panels get, in order: `must` first, then each `shape` (how bodies are arranged; a scene's own name if it says none) its turn
// in an order the seed picks, so a list longer than a tile leaves out different shapes on different tiles; then no two neighbours alike
export function planDeck(scenes, Z, s0) {
  const r = stream(s0, "plan"), draw = (a) => a.splice(Math.floor(r() * a.length), 1)[0], shape = (i) => scenes[Z.scenes[i]].shape ?? Z.scenes[i];
  const left = new Map(), taken = [];
  Z.scenes.forEach((n, i) => { if (Z.must?.includes(n) && !taken.some((q) => Z.scenes[q] === n)) taken.push(i); else left.set(shape(i), [...(left.get(shape(i)) ?? []), i]); });
  const turns = [...left.keys()], order = [], had = new Set(taken.map(shape));
  while (turns.length) order.push(draw(turns));
  order.sort((a, b) => had.has(a) - had.has(b));                       // (a shape `must` has brought comes round last)
  const dealt = [];
  while (order.some((q) => left.get(q).length)) for (const q of order) if (left.get(q).length) dealt.push(draw(left.get(q)));
  const spare = dealt.splice(Math.max(0, Z.panels - taken.length));
  taken.push(...dealt);
  const deck = [];
  while (taken.length) { const ok = taken.filter((i) => !deck.length || shape(i) !== shape(deck.at(-1))); const i = draw(ok.length ? ok : [...taken]); taken.splice(taken.indexOf(i), 1); deck.push(i); }
  deck.spare = spare;                                                  // (whoever didn't get a panel: a stand-in where a panel's own scene looks too like its neighbours)
  return deck;
}
// a zone's scenes shuffled, as indices, `must` first so a list longer than its panels still holds them, those shuffled again
export function shuffledDeck(Z, s0) {
  const n = Z.scenes.length, deck = Z.scenes.map((_, i) => i), rd = stream(s0, "scene");
  for (let i = n - 1; i > 0; i--) { const j = Math.floor(rd() * (i + 1)); [deck[i], deck[j]] = [deck[j], deck[i]]; }
  if (Z.must) for (let i = 0, f = 0; i < n; i++) if (Z.must.includes(Z.scenes[deck[i]])) { [deck[f], deck[i]] = [deck[i], deck[f]]; f++; }   // (`must`: of a list longer than a tile, these always come; then the panels shuffled again, or they'd hold the first ones)
  if (Z.must) for (let i = Math.min(n, Z.panels) - 1; i > 0; i--) { const j = Math.floor(rd() * (i + 1)); [deck[i], deck[j]] = [deck[j], deck[i]]; }
  return deck;
}
