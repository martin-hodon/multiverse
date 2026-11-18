// What is left of the old flora module (the trees, the bushes and their leaf cards are plants/ since 2026-11-18:
// docs/plants.md): the seeded random every module draws from (rng.js, re-exported here for the many that import it
// from flora.js) and the names of the mushrooms the woods grow.
import { rng } from "./rng.js";
export { rng };

// mushrooms: the three kinds the woods grow -- items (assets/items/mushrooms/<kind>, tools/mushroomgen.py), drawn by the
// game with the flowers; amanita = fly agaric, boletus = cep, chanterelle = the golden funnel
export const MUSHROOMS = ["amanita", "boletus", "chanterelle"];
