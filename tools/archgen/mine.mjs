// THE MINE's catalogue files (2026-11-03): the definition is made by mine.js (mineDoc) for any ground -- the game lays
// it into the world's hills (index.html) -- and this writes the catalogue's copy of it on level ground 0, with the cart
// and a finish for each ore:
//   assets/architecture/village/mine.json, assets/architecture/components/mine-cart.json, assets/finishes/mine-<ore>.json
//     node tools/archgen/mine.mjs        (tools/archgen/mine.py runs this)
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { minePlan, mineDoc } from "../../mine.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "../..");
const put = (p, v) => writeFileSync(join(ROOT, p), JSON.stringify(v, null, 1) + "\n");
const { doc, names } = mineDoc(minePlan(() => 0, 0, 0, 0));
put("assets/architecture/village/mine.json", doc);
// (the finishes name the parts of an ADIT's mine too -- the game makes one where the land rises behind the entrance:
//  its names, from one driven into a ramp on level ground)
const ramp = (x) => Math.max(0, Math.min(30, -x * .8)), adit = minePlan(ramp, 0, 0, 0, "adit");
if (adit.bad) throw new Error("mine.mjs: the test adit failed: " + adit.bad);
const an = mineDoc(adit).names, both = (k) => [...new Set([...names[k], ...an[k]])];
const [TIMBER, FLOORS, VEINS, STONE] = ["TIMBER", "FLOORS", "VEINS", "STONE"].map(both);

// the cart (Hunt): a plank box on four little wheels, its load of ore
const box = (w, l, h, ...pts) => ({ type: "box", width: w, length: l, height: h, at: pts.map((p) => [...p, 0]) });
const cart = { name: "Mine cart", _about: "a Hunt: the miners' wooden cart, a plank box on four little wheels, loaded with ore", params: { detail: 4 },
               parts: { body: box(.62, 1.0, .42, [0, .2, 0]), load: box(.5, .86, .12, [0, .6, 0]),
                        wheels: box(.08, .22, .22, [-.36, 0, .3], [.36, 0, .3], [-.36, 0, -.3], [.36, 0, -.3]) } };
cart.build = Object.keys(cart.parts);
put("assets/architecture/components/mine-cart.json", cart);

// the finishes: by part name -- a numbered one ("walking landing 6": a deeper mine has more) by its name without the
// number, which the finish matches as well (arch/finish.js)
const strip = (l) => [...new Set(l.map((n) => n.replace(/ \d+$/, "")))];
const ORES = { silver: ["mine-gneiss", "vein-galena"], copper: ["mine-slate", "vein-malachite"], salt: ["rock-salt", "vein-salt"] };
for (const [ore, [rock, vein]] of Object.entries(ORES))
  put(`assets/finishes/mine-${ore}.json`, { name: `Mine (${ore})`, building: "architecture/village/mine",
    _about: `the ${ore} mine: its rock ${rock}, the vein ${vein}, the timber grey oak, the galleries' floors trodden earth, the shaft house boarded under thatch, an adit's portal rubble stone`,
    rules: [{ parts: [...VEINS, "shaft bottom cart/load", "carts/load", "portal cart/load", "ore pile"], pattern: "stone/ore vein", palette: vein },
            { parts: ["shaft house roof", "walking shaft roof"], surface: "roof", pattern: "roofs/thatch", palette: "thatch-grey" },
            { parts: ["shaft house"], pattern: "timber/planks", palette: "oak-grey" },
            { parts: [...strip(TIMBER), "kind:flight", "shaft bottom cart", "carts", "portal cart"], pattern: "timber/bark", palette: "oak-grey" },
            { parts: strip(FLOORS), surface: "floor", pattern: "stone/sand", palette: ore !== "salt" ? "earth" : rock },
            { parts: strip(STONE), pattern: "stone/rubble", palette: "sandstone-grey" },
            { parts: ["spoil heap"], pattern: "stone/rock face", palette: rock },
            { pattern: "stone/rock face", palette: rock }] });
console.log("mine:", Object.keys(doc.parts).length, "parts; footprint", doc.params.footW, "x", doc.params.footD);
