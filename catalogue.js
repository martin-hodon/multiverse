// THE CATALOGUE, loaded once for the whole world: assets/index.json, every asset in it by path -> its definition
// (creatures.js loadCatalogue). A module with a top-level await, so whoever imports it finds it loaded -- the
// animals and people (species.js), the items in hands (tools.js) and in rooms (architecture.js) read the same one.
import { loadCatalogue } from "./creatures.js";
export const { index: CATALOGUE, bank: ASSETS } = await loadCatalogue();
