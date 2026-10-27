// THE TOWN (2026-09-27): a walled market town on the river's south bank and the farms over the river, laid out by
// SEED from the village assets alone (assets/architecture/village: four kinds of town house, the longhouse, the wall,
// its round towers and gatehouses, the church -- tools/archgen/village.py writes them).
//
// The seed draws a STYLE first -- what the town is built of -- and every building shares it: one stone (the walls,
// the church, the cellars, the flagstones), one roof covering on every roof in town, one wood, a few plasters and
// timber colours the houses choose among, the house kinds the town favours, and the tops of its church tower, its
// wall towers and its gates. A timbered town of the German lands, a grey stone town under slate, a brick town of the
// Baltic, a plastered town of the south: within one, houses differ in their frontage, depth, storeys, pitch, cellar,
// their plaster and their timbers, but never in their roofs, so the town reads as one place.
//
// Then the PLAN (planTown): the streets, every plot along them and every building's params, the wall ring with its
// towers and gates, the square with the market and the fountain, the church, the inn, the shops of the trades, and
// longhouse farmsteads with their fields across the river. It returns the SITES (index.html places them as it places
// every building), the STREETS (paths.js draws them; the villagers walk them), the level ground, and the guards.
//
// Coordinates are the world's: +x east, +z south; the river runs east along z = riverZ(x).
import { archBuilding, archAssembly } from "./architecture.js";
import { rng } from "./flora.js";
import { ASSETS } from "./catalogue.js";

const pickW = (r, w) => {
  const e = Object.entries(w).filter(([, v]) => v > 0), tot = e.reduce((s, [, v]) => s + v, 0);
  let u = r() * tot;
  for (const [k, v] of e) if ((u -= v) < 0) return k;
  return e[e.length - 1][0];
};
const pickOf = (r, list) => list[Math.floor(r() * list.length) % list.length];
const some = (r, list, n) => { const a = list.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a.slice(0, Math.max(1, n)); };
const between = (r, a, b, step = .1) => Math.round((a + r() * (b - a)) / step) * step;

// the way out of a building's door, [x, z] (unit): its doors stand in walls along x or z, and face away from the middle
export function doorNormal(d) {
  const alongZ = Math.abs(Math.abs(d.yaw ?? 0) - 90) < 1;
  return alongZ ? [Math.sign(d.x || 1), 0] : [0, Math.sign(d.z || 1)];
}

// ---- THE STYLES ---------------------------------------------------------------------------------------------------
// weight: how often the seed draws it. houses: the kinds of town house and how often. stones: the stone it quarries
// (one is drawn); masonry: how its stone buildings are laid ("S" is that stone). roofs: [pattern, palette], one drawn
// for the whole town. ground / upper: how a house's ground storey and upper storeys are finished (plaster, frame,
// studs: close studding, masonry). plasters, frames: a few are drawn and each house takes one. church, towers,
// gates: the tops the town builds, by weight.
export const STYLES = {
  timbered: { weight: 3, houses: { jettied: 3, gable: 3, eaves: 2, stone: 1 },
              stones: ["limestone", "sandstone", "sandstone-grey", "red-sandstone"], masonry: [["stone/rubble", "S"]], fine: [["stone/ashlar", "S"]],
              roofs: [["roofs/fish scale", "tile-red"], ["roofs/fish scale", "tile-brown"], ["roofs/slate", "slate"]],
              ground: { plaster: 5, frame: 2, masonry: 2 }, upper: { frame: 6, studs: 2, plaster: 1 },
              plasters: ["plaster-white", "plaster-ochre", "plaster-rose"], frames: ["frame-dark", "frame-oxblood", "frame-ochre", "frame-grey"], wood: ["oak"],
              church: { spire: 3, pyramid: 2, saddleback: 1, onion: 1 }, towers: { cone: 3, tent: 2, merlons: 1, bell: 1 }, gates: { roof: 3, battlements: 1 } },
  stone: { weight: 2, houses: { stone: 4, gable: 2, eaves: 2 },
           stones: ["granite", "limestone", "sandstone-grey"], masonry: [["stone/rubble", "S"], ["stone/ashlar", "S"]], fine: [["stone/ashlar", "S"]],
           roofs: [["roofs/slate", "slate"]],
           ground: { masonry: 1 }, upper: { masonry: 5, plaster: 1 },
           plasters: ["plaster-white"], frames: ["frame-grey"], wood: ["oak-grey", "oak"],
           church: { battlements: 3, pyramid: 2, spire: 2, saddleback: 1 }, towers: { merlons: 3, cone: 2 }, gates: { battlements: 3, roof: 1 } },
  brick: { weight: 2, houses: { gable: 5, eaves: 2, stone: 1 },
           stones: ["sandstone-grey", "limestone"], masonry: [["stone/brick", "brick"]], fine: [["stone/brick flemish", "brick"]],
           roofs: [["roofs/fish scale", "tile-red"], ["roofs/slate", "slate"]],
           ground: { masonry: 3, plaster: 1 }, upper: { masonry: 4, plaster: 1 },
           plasters: ["plaster-white", "plaster-ochre"], frames: ["frame-dark"], wood: ["oak"],
           church: { spire: 3, saddleback: 2, pyramid: 1 }, towers: { cone: 2, tent: 2, merlons: 1 }, gates: { roof: 2, battlements: 1 } },
  plastered: { weight: 2, houses: { eaves: 3, gable: 2, stone: 1, jettied: 1 },
               stones: ["limestone", "sandstone"], masonry: [["stone/rubble", "S"], ["stone/ashlar", "S"]], fine: [["stone/ashlar", "S"]],
               roofs: [["roofs/fish scale", "tile-red"], ["roofs/fish scale", "tile-brown"]],
               ground: { plaster: 4, masonry: 1 }, upper: { plaster: 1 },
               plasters: ["plaster-white", "plaster-ochre", "plaster-rose", "plaster-red"], frames: ["frame-dark"], wood: ["pine", "oak"],
               church: { onion: 3, pyramid: 2, spire: 1 }, towers: { bell: 2, tent: 2, cone: 1 }, gates: { roof: 3, battlements: 1 } },
};
// the town's style, drawn from the seed (`name` forces one: ?townstyle=)
export function townStyle(seed, name = null) {
  const r = rng(seed * 7 + 3);
  const kind = name && STYLES[name] ? name : pickW(r, Object.fromEntries(Object.entries(STYLES).map(([k, s]) => [k, s.weight])));
  const T = STYLES[kind], stone = pickOf(r, T.stones);
  const lay = ([pattern, palette]) => ({ pattern, palette: palette === "S" ? stone : palette });
  const [rp, rpal] = pickOf(r, T.roofs);
  return {
    kind, stone, masonry: lay(pickOf(r, T.masonry)), fine: lay(pickOf(r, T.fine)),
    roof: { pattern: rp, palette: rpal }, roofs: T.roofs.map(([pattern, palette]) => ({ pattern, palette })),
    wood: pickOf(r, T.wood), plasters: some(r, T.plasters, 2 + Math.floor(r() * 2)), frames: some(r, T.frames, 1 + Math.floor(r() * 2)),
    houses: T.houses, ground: T.ground, upper: T.upper,
    church: pickW(r, T.church), tower: pickW(r, T.towers), gate: pickW(r, T.gates),
  };
}

// ---- THE FINISHES the style gives each kind of building (arch/finish.js rules: the first that matches wins) ---------
const TRADES = ["smithy", "bakery", "pottery", "weaver", "tailor", "carpenter", "cooper", "butcher", "tavern-room"];
const SHOP_NAMES = { smithy: "Smithy", bakery: "Bakery", pottery: "Pottery", weaver: "Weaver's", tailor: "Tailor's", carpenter: "Carpenter's", cooper: "Cooper's", butcher: "Butcher's" };
const WOODWORK = ["table", "bed 1", "bed 2", "flight 0", "flight 1", "joists 1", "joists 2", "jetty 1", "jetty 2", "cellar flight", "cellar rail", "cellar rail posts", "cellar casks", "seating", "altar",
                  "beds", "chest", "stalls", "partition", ...TRADES.map((t) => "trade " + t)];
const GROUND_FLOORS = ["floor 0", "floor 0 cellar beside", "floor 0 cellar front", "floor 0 cellar back", "floor 0 cellar col A", "cellar floor"];
// THE TRADES' MATERIALS: a workshop's parts are named by what they are made of (village.py furniture: "forge brick",
// "anvil face iron", "pots clay", "bolts woad"...) -- the last word picks the finish; everything else is the town's wood
const TRADE_MATERIAL = { brick: { pattern: "stone/brick", palette: "brick" }, iron: { pattern: "materials/metal", palette: "iron" },
  clay: { pattern: "stone/plaster", palette: "fired-clay" }, leather: { pattern: "stone/plaster", palette: "leather" },
  cloth: { pattern: "fabrics/linen", palette: "linen" }, wool: { pattern: "fabrics/twill", palette: "wool-white" },
  meat: { pattern: "stone/plaster", palette: "meat" }, linen: { pattern: "fabrics/linen", palette: "linen" },
  madder: { pattern: "fabrics/twill", palette: "madder" }, woad: { pattern: "fabrics/twill", palette: "woad" },
  weld: { pattern: "fabrics/twill", palette: "weld" }, russet: { pattern: "fabrics/twill", palette: "russet" } };
let tradeRules = null;
const tradeMaterials = () => tradeRules ??= (() => {
  const names = new Set(TRADES.flatMap((t) => archAssembly("furniture/" + t).parts.map((p) => p.name.replace(/ \d+$/, ""))));
  return Object.entries(TRADE_MATERIAL).map(([w, look]) => ({ parts: [...names].filter((n) => n.split(" ").pop() === w), ...look })).filter((r) => r.parts.length);
})();
const inside = (S) => [
  { surface: "floor", side: "in", pattern: "timber/boards", palette: S.wood },
  { surface: "ceiling", pattern: "timber/boards", palette: S.wood },
  { surface: "wall", side: "in", pattern: "stone/plaster", palette: "plaster-white" },
];
// a town house: `look` is how its ground storey and its upper storeys (and its gables) are finished
function houseFinish(S, look) {
  return { name: "town house", building: "town", rules: [
    { parts: "roof", surface: "roof", ...(look.roof ?? S.roof) },
    { parts: "chimney", pattern: "stone/brick", palette: "brick" },
    { parts: ["plinth", "plinth shop"], ...S.masonry },   // (the plinth: the town's rough stone)
    { parts: ["course 1", "course 2", "quoins", "quoins b"], ...S.fine },   // (the string courses and the quoins: dressed stone)
    { parts: "hearth/fireback", pattern: "stone/brick", palette: "iron" },   // (the fireback: sooted black)
    { parts: ["hearth", "cellar walls"], pattern: "stone/rubble", palette: S.stone },
    ...tradeMaterials(),
    { parts: WOODWORK, pattern: "timber/wood", palette: S.wood },   // (furniture, stairs, joists: planed wood -- bark read as zebra stripes on a counter)
    { parts: "kind:railing", pattern: "timber/wood", palette: S.wood },   // (the stairs' stringers, balusters and handrails: the flights' wood)
    { parts: GROUND_FLOORS, surface: "floor", pattern: "floors/flagstones", palette: S.stone },
    { parts: "roof", side: "in", pattern: "timber/boards", palette: S.wood },
    ...inside(S),
    { parts: ["walls 0", "walls 0 shop"], ...look.ground },
    { parts: ["walls 1", "walls 2", "roof"], ...look.upper },
  ] };
}
// A HOUSE'S ROOF: mostly the town's own, but every so often (ROOF_MIX) another the style roofs with -- a red-tiled roof
// among the slates, as a town re-roofed over the years has; by where the house stands (a hash: no draw from the seed's
// stream, so everything else the seed picks stays as it was)
const ROOF_MIX = .3;
function roofAt(S, x, z) {
  const others = S.roofs.filter((o) => o.pattern !== S.roof.pattern || o.palette !== S.roof.palette);
  const h = (k) => { const v = Math.sin(x * 12.9898 + z * 78.233 + k * 37.719) * 43758.5453; return v - Math.floor(v); };
  return others.length && h(0) < ROOF_MIX ? others[Math.floor(h(1) * others.length)] : S.roof;
}
// how a storey is finished: plaster (in its colour), a timber frame or close studding (in its timbers), or the town's masonry
const lookOf = (S, how, plaster, frame) => how === "plaster" ? { pattern: "stone/plaster", palette: plaster }
  : how === "frame" ? { pattern: "timber/frame", palette: frame, align: "part" }
  : how === "studs" ? { pattern: "timber/close studding", palette: frame, align: "part" }
  : { ...S.masonry };
const HOWS = ["plaster", "frame", "studs", "masonry"];
function houseLook(S, kind, r) {
  const plaster = pickOf(r, S.plasters), frame = pickOf(r, S.frames), of = (how) => lookOf(S, how, plaster, frame);
  if (kind === "stone") return { ground: of("masonry"), upper: of("masonry") };
  const up = kind === "jettied" ? pickW(r, { frame: 3, studs: 1 }) : pickW(r, S.upper);
  return { ground: of(kind === "jettied" && r() < .4 ? up : pickW(r, S.ground)), upper: of(up) };
}
// the nave's plan inside its walls (the church's own numbers: a rule's `within` is in the building's frame)
const NAVE = () => { const P = archAssembly("village/church").params; return [-P.L / 2 + P.t - .1, -P.B / 2 + P.t - .1, P.L / 2 - P.t + .1, P.B / 2 - P.t + .1]; };
function churchFinish(S) {
  const spire = S.roof.pattern === "roofs/slate" ? S.roof : { pattern: "roofs/slate", palette: "slate" };
  return { name: "church", building: "town", rules: [
    { parts: ["spire", "pyramid", "saddleback"], surface: "roof", ...spire },
    { parts: "onion", surface: "roof", pattern: "roofs/sheet metal", palette: "copper" },
    { parts: ["nave roof", "chancel roof"], surface: "roof", ...S.roof },
    { parts: WOODWORK, pattern: "timber/wood", palette: S.wood },
    { parts: ["nave roof", "chancel roof"], side: "in", pattern: "timber/boards", palette: S.wood },
    { surface: "floor", side: "in", pattern: "floors/flagstones", palette: S.stone },
    { parts: ["nave", "chancel north", "chancel south", "chancel east"], surface: "wall", side: "in", pattern: "stone/plaster", palette: "plaster-white" },   // (the tower's inside stays stone)
    // ...and the tower's east wall IS the nave's west wall where it stands (village.py church): every wall face inside the
    // nave's plan plastered, by region (the strips of the nave's west wall beside the tower read as "out" by the rays)
    { parts: ["nave", "tower"], surface: "wall", within: NAVE(), pattern: "stone/plaster", palette: "plaster-white" },
    { ...S.fine },
  ] };
}
// the wall, its towers and its gatehouses: all the town's stone; roofs as the town's; the walk and the floors flagged
function fortFinish(S) {
  return { name: "town wall", building: "town", rules: [
    { parts: ["cone", "bell", "tent", "roof"], surface: "roof", ...S.roof },
    { parts: ["upper floor", "platform"], surface: "floor", pattern: "timber/boards", palette: S.wood },
    { parts: ["kind:railing", "inner parapet", "inner parapet by the stair", "inner parapet past the stair"], pattern: "timber/wood", palette: S.wood },   // (the walk's and the stairs' balustrades: timber, on stone walls)
    { surface: "floor", pattern: "floors/flagstones", palette: S.stone },
    { ...S.masonry },
  ] };
}
// the farmyards (village/pig-yard, hen-yard, stable-yard: fence, gate, shed as components): wood and thatch in the
// town's style; the fence's STYLE goes with the town's -- rails or picket in a timbered town, dykes in a stone one
const YARD_WOOD = ["fence north west", "fence north east", "fence east", "fence south", "fence west", "gate", "shed",
                   "fence north", "fence south west", "fence south east", "bench", "bench legs", "comb frame"];   // (the apiary's too)
function yardFinish(S) {
  return { name: "farmyard", building: "town", open: true, rules: [   // (open: under the sky -- archmat.js: snow at any height)
    { parts: "shed", surface: "roof", pattern: "roofs/thatch", palette: "thatch" },
    { parts: ["plinth", "end plinths", "dyke", "coping", "trough", "bowl"], pattern: "stone/rubble", palette: S.stone },
    { parts: ["hay", "bales", "grain"], pattern: "roofs/thatch", palette: "thatch" },
    { parts: ["wallow", "wallow rim", "slop", "floor"], pattern: "stone/sand", palette: "earth" },
    { parts: ["wallow wet"], pattern: "stone/sand", palette: "mud" },   // (the wallow's wet middle)
    { parts: ["scratched"], pattern: "stone/sand", palette: "dust" },   // (the hen yard's bare ground: dry, paler than the wallow)
    { parts: "shed", pattern: "timber/boards", palette: S.wood },   // (the sheds' walls: boards, after the hay, the floors and the ground -- the first rule that matches wins, and those are the sheds' own parts too -- the posts and fences below planed wood)
    { parts: YARD_WOOD, pattern: "timber/wood", palette: S.wood },
    { surface: "floor", pattern: "stone/sand", palette: "earth" },
  ] };
}
// the market (village/market): the square's flagstones, the cross in the town's fine stone with a gilt cross on it
function marketFinish(S) {
  return { name: "market", building: "town", open: true, rules: [
    { parts: "paving", pattern: "floors/flagstones", palette: S.stone, puddles: true },   // (puddles after rain: archmat.js)
    { parts: ["cross", "cross arms"], pattern: "materials/metal", palette: "gold" },
    { ...S.fine },
  ] };
}
const FENCE_STYLES = { timbered: ["rails", "rails", "picket", "wattle"], stone: ["stone", "stone", "rails"], brick: ["rails", "picket", "zigzag"], plastered: ["picket", "rails", "wattle"] };
// the longhouse: thatch over an open roof space, timber-framed walls and gables, an earth floor, a boarded loft
function longhouseFinish(S) {
  return { name: "longhouse", building: "town", rules: [
    { parts: "roof", surface: "roof", pattern: "roofs/thatch", palette: "thatch" },
    { parts: "roof", side: "in", pattern: "timber/boards", palette: S.wood },
    { parts: "hay", pattern: "roofs/thatch", palette: "thatch" },
    { parts: "hearth", pattern: "stone/rubble", palette: S.stone },
    { parts: WOODWORK, pattern: "timber/wood", palette: S.wood },
    { parts: ["aisle posts", "purlins", "tie beams", "wall plates", "king posts"], pattern: "timber/wood", palette: S.wood },
    { parts: "ash bed", pattern: "stone/sand", palette: "gravel" },
    { surface: "floor", pattern: "stone/sand", palette: "earth" },
    { parts: ["walls", "roof"], pattern: "timber/frame", palette: S.frames[0], align: "part" },   // (the roof's: its gables)
  ] };
}

// EVERY finish a town of this style may use, over every option it has (its stones, roofs, woods, plasters, timbers) --
// for build/pregen.py, which bakes the tiles they draw with, so whatever the seed draws is in the cache
export function styleFinishes(kind) {
  const T = STYLES[kind], out = [];
  const base = { ...townStyle(1, kind), plasters: T.plasters, frames: T.frames };
  const variants = [base];
  for (const stone of T.stones) for (const m of T.masonry) for (const f of T.fine) {
    const lay = ([pattern, palette]) => ({ pattern, palette: palette === "S" ? stone : palette });
    variants.push({ ...base, stone, masonry: lay(m), fine: lay(f) });
  }
  for (const [pattern, palette] of T.roofs) variants.push({ ...base, roof: { pattern, palette } });
  for (const wood of T.wood) variants.push({ ...base, wood });
  for (const S of variants) {
    out.push(churchFinish(S), fortFinish(S));
    for (const frame of T.frames) out.push(longhouseFinish({ ...S, frames: [frame] }));
    for (const plaster of T.plasters) for (const frame of T.frames) for (const how of HOWS)
      out.push(houseFinish(S, { ground: lookOf(S, how, plaster, frame), upper: lookOf(S, how, plaster, frame) }));
  }
  return out;
}

// ---- THE HOUSES ---------------------------------------------------------------------------------------------------
// each kind's range of frontage W, depth D, storeys and pitch (the stair needs D >= 7.5: a flight is 3.9m long)
const KINDS = {
  gable: { W: [6.2, 8], D: [9, 12], n: [2, 3], pitch: [50, 58] },
  eaves: { W: [8.5, 11], D: [8, 10], n: [2, 3], pitch: [42, 50] },
  jettied: { W: [6.5, 8], D: [9, 11], n: [2, 3], pitch: [52, 58], j: [.45, .6] },
  stone: { W: [7.5, 9.5], D: [8.5, 10.5], n: [2, 3], pitch: [35, 45] },
};
// a house's params and build list: `n` storeys, a cellar or not, a trade's shop front or not
function houseSpec(kind, r, { trade = null, cellar = r() < .35, big = false } = {}) {
  const K = KINDS[kind];
  const W = big ? K.W[1] + .5 : between(r, ...K.W), D = big ? Math.min(K.D[1], 10) : between(r, ...K.D);
  const n = big ? 2 : r() < .4 ? 3 : 2;
  const params = { W, D, n, pitch: Math.round(between(r, ...K.pitch, 1)) };
  if (K.j) params.j = between(r, ...K.j, .05);
  const build = [trade ? "walls 0 shop" : "walls 0", "walls 1", ...(n > 2 ? ["walls 2"] : []),
    ...(trade ? [] : ["windows 0 front"]), "windows 0 back", "windows 1", ...(n > 2 ? ["windows 2"] : []),   // (their shutters, or glass: the house's `glazed`)
    ...(cellar ? ["floor 0 cellar beside", "floor 0 cellar front", "floor 0 cellar back", "cellar walls", "cellar floor", "cellar flight", "cellar rail posts", "cellar rail", "cellar casks", "cellar casks east", "cellar chest", "cellar stool"] : ["floor 0"]),
    "floor 1 beside", "floor 1 front", "floor 1 back", "joists 1", "flight 0", "way 1", "way 1 top",
    ...(n > 2 ? ["floor 2 beside", "floor 2 front", "floor 2 back", "floor 2 col A", "joists 2", "flight 1", "way 2", "way 2 top", "bed 2"] : []),
    ...(K.j ? ["jetty 1", ...(n > 2 ? ["jetty 2"] : [])] : ["course 1", ...(n > 2 ? ["course 2"] : [])]),   // (string courses at the floors' lines; a jettied house its jetty's joist ends)
    "roof", "chimney", "hearth", "table", "bed 1", trade ? "door shop" : "door", ...(trade ? ["trade " + trade, "sign " + trade] : [])];
  return { params, build };
}

// ---- THE PLAN -----------------------------------------------------------------------------------------------------
// world: { seed, BUILDINGS, riverZ, riverHW, quayZ, BASIN, bridgeX, groundR, style (a STYLES name, or null) }
// returns { style, sites, routes, flats, guards } -- sites as index.html places them ({ key, x, z, bank }), routes as
// paths.js lays them ({ w, pts }), flats as ground.js levels them
// period: the world's period's town (assets/world/periods.json `town`): `houses` -- its dwellings by weight
// (assets/architecture/dwellings) stand in the rows instead of the village's houses, also for the inn and the farms;
// `church: false` -- none, and no cross on the market; `walls`: [pattern, palette] its stone buildings are laid in
// `furnish`: the word its village houses are furnished under (assets/architecture/furnishing.json `swaps`)
export function planTown({ seed, BUILDINGS, riverZ, riverHW, quayZ, BASIN, bridgeX, groundR, style = null, period = null }) {
  const S = townStyle(seed, style), r = rng(seed * 13 + 5);
  const DW = period?.houses ?? null;
  const FURN = period?.furnish ? { furnish: period.furnish } : {};   // (the period's own furniture in the village's houses: furnishing.json `swaps`)
  if (DW) { S.tower = "merlons"; S.gate = "battlements"; }   // (the walls of an older town: battlements, no spires)
  if (period?.walls) S.masonry = { pattern: period.walls[0], palette: period.walls[1] };   // (its own masonry: mud brick, ashlar)
  // a dwelling of the period, turned to face its street (`yaw`), its footprint along and across it
  const dwellings = new Map();
  const dwelling = (name, yaw) => {
    const k = name + "|" + yaw;
    if (!dwellings.has(k)) dwellings.set(k, archBuilding(`dwellings/${name}`, { params: { yaw } }));
    return dwellings.get(k);
  };
  const sites = [], routes = [], flats = [], guards = [];
  const bank = (x) => riverZ(x) + riverHW(x);                       // the south bank line
  const BR = BUILDINGS.bridge, xB = bridgeX;
  const footS = riverZ(xB) + BR.halfL + BR.ramp;                    // where the bridge's south ramp meets the ground
  // THE FRAME: the main street east-west 30m south of the bridge's foot, the south street 36m beyond, the south wall
  // 26m beyond that; the west and east walls 62m and 70m from the bridge, open to the river at their north ends
  const zM = footS + 30, zS2 = zM + 36, ZS = zS2 + 26;
  const XW = xB - 62, XE = xB + 70;
  const xL = xB - 31, xE2 = xB + 44;                                // the two lanes between the streets
  const HW = 1.75;                                                  // a street's half width (the lanes 1.25)
  let nKey = 0;
  const key = (base) => `${base}${++nKey}`;
  // PLACE a building so its definition's ORIGIN lands at (X, Z): archBuilding centres a site on its bounding box, so the
  // site's middle is the origin moved by that box's offset (already in the turned frame)
  const place = (k, def, X, Z, extra = {}) => {
    BUILDINGS[k] = def;
    const [ox, oz] = def.arch?.offset ?? [0, 0];
    const s = { key: k, x: X - ox, z: Z - oz, bank: "south", ...extra };
    sites.push(s);
    return s;
  };
  const doorOut = (s, d, reach = 1.3) => {   // the point just outside a site's door (the villagers' `out`: village-life.js)
    const [nx, nz] = doorNormal(d);
    return [s.x + d.x + nx * reach, s.z + d.z + nz * reach];
  };

  // ---- the houses along a street: a ROW fills the free stretches of one side of it, house after house, eaves-drip
  // alleys between them; `axis` "x" for a street running east-west at z = at, "z" for one north-south at x = at; `side`
  // -1 the north (or west) side, +1 the south (or east); every house faces the street
  const houses = [];
  const row = ({ axis, at, side, from, to, gaps = [], hw = HW }) => {
    const yaw = axis === "x" ? (side < 0 ? 0 : 180) : (side < 0 ? 90 : -90);
    const free = [[from, to]];
    for (const [a, b] of gaps) for (let i = free.length - 1; i >= 0; i--) {
      const [u, v] = free[i];
      if (b <= u || a >= v) continue;
      free.splice(i, 1, ...[[u, a], [b, v]].filter(([p, q]) => q - p > 1));
    }
    for (const [u, v] of free) {
      const mine = [];
      let p = u;
      for (let tries = 0; tries < 6;) {   // (a house that will not fit: another kind or size, a few times, then the stretch is full)
        if (DW) {   // the period's dwelling: its footprint along the street and across it
          const name = pickW(r, DW), def = dwelling(name, yaw), [fx, fz] = def.footprint;
          const along = axis === "x" ? fx : fz, across = axis === "x" ? fz : fx, w = along + .6;
          if (p + w > v) { tries++; continue; }
          mine.push({ kind: name, def, depth: across / 2, spec: { params: { W: along, D: across } }, axis, at, side, yaw, along: p + w / 2, hw });
          p += w + between(r, .8, 2.4);
          continue;
        }
        const kind = pickW(r, S.houses), spec = houseSpec(kind, r);
        const w = spec.params.W + 2 * .4;                                 // (its roof's verge each side)
        if (p + w > v) { tries++; continue; }
        mine.push({ kind, spec, axis, at, side, yaw, along: p + w / 2, hw });
        p += w + between(r, .3, 1.2) + (r() < .12 ? 2.2 : 0);           // an eaves-drip alley, now and then a passage to the yards
      }
      const spare = Math.max(0, v - (mine.length ? mine[mine.length - 1].along + mine[mine.length - 1].spec.params.W / 2 + .4 : u));
      mine.forEach((h, i) => { h.along += spare * (i + .5) / mine.length; });   // (what is left over, shared out between them)
      houses.push(...mine);
    }
  };
  // the square: north of the main street at the bridge's head, east of the bridge street
  const SQ = { x0: xB + HW + 1.5, x1: xB + 36, z0: footS + 3, z1: zM - HW - 1 };
  // the church: south of the main street facing the square, its tower (and door) toward the bridge street
  const CH = { x0: xB + HW + 1, x1: xB + 42, z0: zM + HW, z1: zM + 24 };
  // THE INN on the square's east side, facing it; a house of the eaves kind at its largest
  const INN = { W: 11, D: 9.5 };
  const lane = (x) => [x - 3, x + 3];
  row({ axis: "x", at: zM, side: -1, from: XW + 9, to: xB - HW - 1, gaps: [] });                                  // main street, north, west of the bridge
  row({ axis: "x", at: zM, side: -1, from: SQ.x1 + INN.D + 3.5, to: XE - 9 });                                  // ...east of the square and the inn
  row({ axis: "x", at: zM, side: 1, from: XW + 9, to: XE - 9, gaps: [lane(xL), [xB - HW - 1, CH.x1], lane(xE2)] });   // main street, south
  row({ axis: "x", at: zS2, side: -1, from: XW + 9, to: XE - 9, gaps: [lane(xL), [xB - HW - 1, xB + HW + 1], lane(xE2)] });   // south street, north
  row({ axis: "x", at: zS2, side: 1, from: XW + 9, to: XE - 9, gaps: [[xB - HW - 1, xB + HW + 1]] });                  // south street, south
  // the bridge street's west side, between the ramp's foot and the main street's corner house
  const corner = Math.max(...houses.filter((h) => h.at === zM && h.side < 0 && h.along < xB).map((h) => h.spec.params.D + 2 * (h.spec.params.j ?? 0)), 10);
  row({ axis: "z", at: xB, side: -1, from: footS + 2, to: zM - HW - 1.2 - corner - 1.5 });
  // THE TRADES: shop fronts on the main street and the bridge street, one trade a house (a house 7m across or more: the
  // arch and the trade's furniture want the room) -- the same house, its ground storey opened to the street
  const shops = DW ? [] : some(r, houses.filter((h) => (h.at === zM || h.axis === "z") && h.spec.params.W >= 7), TRADES.length - 1);   // (a dwelling has no shop front)
  TRADES.filter((t) => t !== "tavern-room").forEach((t, i) => {
    const h = shops[i]; if (!h) return;
    h.spec.build = h.spec.build.filter((b) => b !== "windows 0 front")   // (no shutters in the shop's arch: the front windows went with the wall)
      .map((b) => b === "walls 0" ? "walls 0 shop" : b === "door" ? "door shop" : b).concat("trade " + t, "sign " + t);
    h.trade = t;
  });
  // build them: each its own definition (params, build list, turned to its street), finished in the style
  for (const h of houses) {
    const P = h.spec.params, depth = h.def ? h.depth : P.D / 2 + (P.j ?? 0);   // (the jetty over the street on the upper storeys)
    const set = h.hw + 1.2 + depth;                          // front wall 1.2m back from the street's edge
    const [X, Z] = h.axis === "x" ? [h.along, h.at + h.side * set] : [h.at + h.side * set, h.along];
    // (QUOINS up the corners of a plastered or stone house -- not a framed one: drawn after its look)
    const look = h.def ? null : houseLook(S, h.kind, r);
    const quoins = look && h.kind !== "jettied" && ![look.ground, look.upper].some((l) => l.pattern.startsWith("timber/")) ? ["quoins", "quoins b"] : [];
    const plinth = h.kind === "stone" || h.def ? [] : [h.trade ? "plinth shop" : "plinth"];   // (a plinth of rough stone at the foot: not under a stone house)
    const def = h.def ?? archBuilding(`village/${h.kind}-house`, { name: h.trade ? SHOP_NAMES[h.trade] : "Town house",
      params: { ...P, ...FURN, yaw: h.yaw, build: [...h.spec.build, ...quoins, ...plinth] }, finish: houseFinish(S, { ...look, roof: roofAt(S, X, Z) }) });
    const s = place(key(h.trade ?? "house"), def, X, Z, { home: true, ...(h.trade ? { trade: h.trade } : {}) });   // (a shop's trade: a lamp by its door, nightglow.js)
    const d = def.doors?.[0];
    if (d) {   // its door on the street
      const o = doorOut(s, d, 1.3);
      routes.push({ w: 1.2, pts: [h.axis === "x" ? [o[0], h.at] : [h.at, o[1]], o] });
    }
  }
  {   // the inn: the eaves house at its largest, a cellar, the tavern room in front, facing the square (west)
    const spec = houseSpec("eaves", r, { trade: "tavern-room", cellar: true, big: true });
    Object.assign(spec.params, { W: INN.W, D: INN.D });
    // (a town of the period's dwellings: its inn one of them -- the guests still eat there)
    const def = DW ? dwelling(pickW(r, DW), -90) : archBuilding("village/eaves-house", { name: "The Bridge Inn", params: { ...spec.params, ...FURN, yaw: -90, build: spec.build },
      finish: houseFinish(S, houseLook(S, "eaves", r)) });
    const X = SQ.x1 + 1.2 + (DW ? def.footprint[0] : INN.D) / 2, Z = (SQ.z0 + SQ.z1) / 2;
    const s = place("tavern", def, X, Z, { home: true, role: "inn" });
    if (def.doors?.[0]) { const o = doorOut(s, def.doors[0], 1.3); routes.push({ w: 2, pts: [[o[0], zM], o] }); }   // along the square's east side from the main street
  }
  if (period?.church !== false) {   // the church: its west end (the tower) 3m from the bridge street, its north side (the nave's eave) 2.5m from the main street
    const def = archBuilding("village/church", { name: "Church", params: { build: churchBuild(S.church) }, finish: churchFinish(S) });
    BUILDINGS.church = def;
    const s = { key: "church", x: CH.x0 + 3 + def.footprint[0] / 2, z: zM + HW + 2.5 + def.footprint[1] / 2, bank: "south", role: "church" };
    sites.push(s);
    const o = doorOut(s, def.doors[0], 1.3);
    routes.push({ w: 2, pts: [[xB, o[1]], o] });
  }
  // the market and the fountain on the square (the village's own: stalls, the market cross, the fountain's bard)
  // (assets/architecture/village/market: the stalls are items; no cross in a town with no church)
  const noCross = (ASSETS.get("architecture/village/market")?.build ?? []).filter((b) => !b.startsWith("cross"));
  BUILDINGS.market = archBuilding("village/market", { name: "Market", finish: marketFinish(S), ...(period?.church === false && noCross.length ? { params: { build: noCross } } : {}) });
  place("market", BUILDINGS.market, SQ.x0 + 9, (SQ.z0 + SQ.z1) / 2 - 1.5, { square: true });
  place("fountain", BUILDINGS.fountain, SQ.x1 - 7, (SQ.z0 + SQ.z1) / 2 + 2, { square: true });
  routes.push({ w: 2, pts: [[SQ.x1 - 7, zM], [SQ.x1 - 7, (SQ.z0 + SQ.z1) / 2 + 6.3]] });   // from the main street to the fountain's paving
  // the fisherman's hut on the bank, east of the square (its jetty over the water)
  { const fp = BUILDINGS.fisherHut.footprint, x = xB + 53; sites.push({ key: "fisherHut", x, z: bank(x) + 1 + fp[1] / 2, bank: "south" }); }

  // ---- THE WALL RING: west, south and east, open to the river; a gatehouse on each street that leaves the town, a
  // round tower at each corner and at each river end and between, every stretch at most 34m. The walk runs along the
  // top all the way round: behind the towers (their doors face the town) and through the gatehouses' upper storeys;
  // a flight climbs to it beside each gate. A tower BETWEEN flanks the wall as they were built: out from its field
  // face, its back where the field parapet's inside runs, so the walk passes it full width, the field parapet running
  // into it and the town-side balustrade on unbroken (astride the wall it took half the walk, both parapets stopped
  // short of it). The corner and river-end towers stay astride: they close the wall's turn and its end.
  const G = { W: 7.6, D: 8.4 };
  const TP = archAssembly("village/wall-tower").params, WP = archAssembly("village/wall").params;
  const ASTRIDE = 3.3, FLANK = WP.T / 2 - WP.fp + TP.R;   // (the towers' centres out from the wall's line; fp: the field parapet's thickness)
  const flankStop = Math.sqrt(TP.R ** 2 - (FLANK - WP.T / 2) ** 2) + .05;   // (where the field parapet's outer face meets a flanking tower)
  const fort = fortFinish(S);
  const towerBuild = { merlons: ["merlons"], cone: ["room", "cone"], bell: ["room", "bell"], tent: ["room", "tent"] }[S.tower];
  const towerDefs = new Map();
  const tower = (x, z, yaw, zt = ASTRIDE) => {
    const k = yaw + "|" + zt;
    if (!towerDefs.has(k)) towerDefs.set(k, archBuilding("village/wall-tower", { name: "Wall tower",
      params: { zt, yaw, build: ["base", "stage", "walk door", "stair", "platform", ...towerBuild] }, finish: fort }));
    place(towerDefs.get(k).__key ??= key("tower"), towerDefs.get(k), x, z, { bank: "wall" });
  };
  const gate = (x, z, yaw, armed) => {
    const def = archBuilding("village/gatehouse", { name: "Town gate", params: { yaw, build: ["walls", "upper floor", "passage",
      ...(S.gate === "roof" ? ["roof"] : ["flat roof", "battlements", "battlements x"]), ...(armed ? ["guards"] : [])] }, finish: fort });
    const s = place(key("gate"), def, x, z, { bank: "wall" });
    if (armed) for (const g of def.guards ?? []) guards.push({ x: s.x + g.x, z: s.z + g.z, h: g.h });   // (armed in index.html, out of the kit: assets/items/kits/guard)
  };
  // one side: from P0 to P1 (tower centres; `c0`/`c1` true for a corner), its gate at `g` along it (metres from P0)
  const side = (P0, P1, yaw, c0, c1, g, stairs) => {
    const L = Math.hypot(P1[0] - P0[0], P1[1] - P0[1]), ux = (P1[0] - P0[0]) / L, uz = (P1[1] - P0[1]) / L;
    const at = (t) => [P0[0] + ux * t, P0[1] + uz * t];
    // (the segment's own +x runs along the wall as the side's yaw turns it: west -> +z, south -> +x, east -> -z)
    const Y = yaw * Math.PI / 180, lx = [Math.cos(Y), -Math.sin(Y)], flip = lx[0] * ux + lx[1] * uz < 0;
    const seg = (t0, t1, e0, e1, stair) => {   // e: "tower" | "corner" | "gate" -- what stands at that end
      // (at a corner the town-side balustrades of both walls run to the corner, T/2 - .15 in: one post there, the one
      //  of the wall the corner ends -- the wall it begins leaves its own out)
      // (likewise the balustrades of the two walls either side of a flanking tower meet behind it: one post there)
      const stop = { tower: [2.8, 2.8, 1], flank: [flankStop, 0, 1], flank0: [flankStop, 0, 0], corner: [.7, WP.T / 2 - WP.ri, 1], corner0: [.7, WP.T / 2 - WP.ri, 0], gate: [0, 0, 1] };
      if (e0 === "corner" || e0 === "flank") e0 += "0";
      const [a, b] = flip ? [e1, e0] : [e0, e1], len = t1 - t0;
      const p = { len, pa: stop[a][0], pb: stop[b][0], ia: stop[a][1], ib: stop[b][1], ka: stop[a][2], kb: stop[b][2], yaw };
      let build = ["body", "parapet", "inner parapet"];
      if (stair) {   // the flight climbs toward the gate, its landing 1m short of it
        const Lf = Math.round(6 / .19) * .28, toB = (stair === "b") !== flip;
        p.sx = toB ? len / 2 - p.ib - Lf - 1.3 - 1.0 : -len / 2 + p.ia + 1.0;
        build = ["body", "parapet", "inner parapet by the stair", "inner parapet past the stair", "stair"];
      }
      const def = archBuilding("village/wall", { name: "Town wall", params: { ...p, build }, finish: fort });
      // (a lookout on the walk's middle, looking over the low town-side parapet: the palace's paintings)
      def.lookouts = [[-.45 * Math.sin(Y) + def.arch.offset[0], 7.8, -.45 * Math.cos(Y) + def.arch.offset[1]]];
      const [x, z] = at((t0 + t1) / 2);
      place(key("wall"), def, x, z, { bank: "wall", open: true });   // (open: the walk is under the sky -- no roof for the weather)
    };
    const run = (t0, t1, e0, e1, stairAt) => {   // towers between, stretches of at most 34m
      const k = Math.max(1, Math.ceil((t1 - t0) / 34)), step = (t1 - t0) / k;
      for (let i = 0; i < k; i++) {
        if (i) tower(...at(t0 + i * step), yaw, FLANK);
        seg(t0 + i * step, t0 + (i + 1) * step, i ? "flank" : e0, i === k - 1 ? e1 : "flank",
            stairAt === 1 && i === k - 1 ? "b" : stairAt === 0 && i === 0 ? "a" : null);
      }
    };
    if (g === null) run(0, L, c0 ? "corner" : "tower", c1 ? "corner" : "tower", null);
    else {
      run(0, g - G.W / 2, c0 ? "corner" : "tower", "gate", stairs ? 1 : null);
      run(g + G.W / 2, L, "gate", c1 ? "corner" : "tower", null);
    }
  };
  const nW = bank(XW) + 6, nE = bank(XE) + 6;                       // the river ends: a tower 6m in from the bank
  tower(XW, nW, -90); tower(XE, nE, 90);
  tower(XW, ZS, -45); tower(XE, ZS, 45);                             // the corners
  side([XW, nW], [XW, ZS], -90, false, true, zM - nW, true);           // west, the gate on the main street (watched)
  side([XW, ZS], [XE, ZS], 0, true, true, xB - XW, true);             // south, the gate on the bridge street
  side([XE, ZS], [XE, nE], 90, true, false, ZS - zM, true);            // east, the gate on the main street
  gate(XW, zM, -90, true); gate(xB, ZS, 0, false); gate(XE, zM, 90, true);

  // ---- THE STREETS (paths.js draws them; the villagers walk them): gate to gate, the bridge to the south gate, the
  // lanes between; the door spurs were laid with the houses
  routes.push({ w: 2 * HW, pts: [[XW - 14, zM], [XE + 14, zM]] });
  routes.push({ w: 2 * HW, pts: [[xB, footS], [xB, ZS + 14]] });
  routes.push({ w: 3, pts: [[XW + 8, zS2], [XE - 8, zS2]] });
  routes.push({ w: 2.5, pts: [[xL, zM], [xL, zS2]] }, { w: 2.5, pts: [[xE2, zM], [xE2, zS2]] });
  // the town's ground: level from the river to past the south wall (the river keeps its bed: not `level`)
  flats.push({ x: (XW + XE) / 2, z: (Math.min(bank(XW), bank(XE)) + ZS) / 2, hx: (XE - XW) / 2 + 12, hz: (ZS - Math.min(bank(XW), bank(XE))) / 2 + 12 });

  // ---- THE FARMS over the river: longhouse farmsteads west of the bridge road and one east of the landing, each with
  // its fields, pens and orchard in rows behind it (one plot a row, or two side by side), a farm track along their doors
  // (the WINDMILL stands among the fields of the first farm, as the water mill stands by the river -- unless the
  // period has none: its town's `without`, assets/world/periods.json, drops those plots)
  const FARMS = [{ x: xB - 34, plots: [["ryeField", "barleyField"], ["windmill"], ["pigYard"], ["cabbageField", "beanField"], ["orchard"]] },
                 { x: xB - 70, plots: [["stableYard"], ["soilField", "berries"]] },
                 { x: BASIN.x + 32, plots: [["garlicField", "henYard"], ["apiary"]] }]
    .map((F) => ({ ...F, plots: F.plots.map((q) => q.filter((k) => !period?.without?.includes(k))).filter((q) => q.length) }));
  const lf = longhouseFinish(S), yf = yardFinish(S);
  BUILDINGS.apiary = archBuilding("village/apiary", { name: "Beekeeper's garden", finish: yf });   // (the fence and the bench: the yards' wood)
  for (const [k, doc, name] of [["pigYard", "village/pig-yard", "Pig yard"], ["henYard", "village/hen-yard", "Hen yard"], ["stableYard", "village/stable-yard", "Stable yard"]]) {
    const styles = FENCE_STYLES[S.kind] ?? FENCE_STYLES.timbered;
    BUILDINGS[k] = archBuilding(doc, { name, params: { fence: styles[Math.floor(r() * styles.length)] }, finish: yf });
  }
  const siteOf = (k, X, Z, extra) => { const [ox, oz] = BUILDINGS[k].arch?.offset ?? [0, 0]; return { key: k, x: X - ox, z: Z - oz, ...extra }; };
  const footN = riverZ(xB) - BR.halfL - BR.ramp, trackZ = footN - 8;
  let trackW = xB, westEdge = Infinity;   // (westEdge: the last western farm's plots' west edge)
  for (const F of FARMS) {
    // how far the plots reach either side of the farm's line: a pair stands 1.5 m out each way from it, each plot its own
    // width beyond -- not half their sum (the wider one on the east had the side track running inside its fence)
    const reach = (side) => Math.max(...F.plots.map((q) => q.length === 2 ? 1.5 + BUILDINGS[q[side > 0 ? 1 : 0]].footprint[0] : BUILDINGS[q[0]].footprint[0] / 2));
    const west = reach(-1), eastR = reach(1), east = F.x > BASIN.x;
    // (a farm west of another keeps its side track and the plots beyond it clear of that farm's: moved west if need be)
    if (!east && F.x + eastR + 3 > westEdge) F.x = westEdge - eastR - 3;
    if (F.x - west < -groundR + 6) continue;                          // (a small world: no room this far west)
    const tz = east ? quayZ(F.x) : trackZ;                            // (the east farm fronts the quay road)
    const L = between(r, 16, 19, .5), B = between(r, 6.5, 7.5, .5);
    const def = DW ? dwelling(pickW(r, DW), 0) : archBuilding("village/longhouse", { name: "Longhouse", params: { L, B, ...FURN, pitch: Math.round(between(r, 46, 54, 1)) }, finish: lf });   // (the period's farmhouse)
    const s = place(key("longhouse"), def, F.x, tz - 2.5 - B / 2 - .7, { bank: undefined, home: true });
    const d = def.doors?.find((q) => q.z > 0) ?? def.doors?.[0];
    if (d) { const o = doorOut(s, d, 1.3); routes.push({ w: 1.2, pts: [[o[0], tz], o] }); }
    let z = s.z - def.footprint[1] / 2 - 3;
    for (const q of F.plots) {
      const fps = q.map((k) => BUILDINGS[k].footprint), deep = Math.max(...fps.map((f) => f[1]));
      // (`plot`: a farm's; `farm`: land the farmers work -- a field, the currants, the orchard -- not a yard or the hives)
      const tag = (k) => ({ plot: true, ...(BUILDINGS[k].crop || BUILDINGS[k].plants ? { farm: true } : {}) });
      if (q.length === 1) sites.push(siteOf(q[0], F.x, z - fps[0][1] / 2, tag(q[0])));
      else q.forEach((k, j) => sites.push(siteOf(k, F.x + (j ? 1 : -1) * (fps[j][0] / 2 + 1.5), z - fps[j][1] / 2, tag(k))));
      z -= deep + 3;
    }
    routes.push({ w: 1.2, pts: [[F.x + eastR + 1.5, tz], [F.x + eastR + 1.5, z + 2]] });   // along the farm's side, past its plots
    if (!east) { trackW = Math.min(trackW, F.x - west); westEdge = F.x - west; }
  }
  if (trackW < xB) routes.push({ w: 2, pts: [[xB, footN + .5], [xB, trackZ], [trackW, trackZ]] });   // the farm track from the bridge's foot

  // (walkIn: the wall-walk's middle, in from the wall's line toward the town -- between the field parapet's inner face and
  //  the town-side rail -- where the watchman and the sentry walk, index.html)
  return { style: S, sites, routes, flats, guards, frame: { xB, zM, zS2, ZS, XW, XE, footS, square: SQ, walkIn: (WP.fp - WP.ri) / 2 } };
}
function churchBuild(top) {
  const base = ["nave", "nave floor", "chancel north", "chancel south", "chancel east", "chancel floor", "nave roof", "chancel roof",
                "tower", "tower courses", "tower floor", "tower stair", "seating", "altar", "door"];
  return [...base, ...{ spire: ["spire", "cross"], pyramid: ["pyramid", "cross pyramid"], saddleback: ["saddleback"],
                        onion: ["onion base", "onion drum", "onion"], battlements: ["battlement roof", "battlements", "battlements x"] }[top]];
}
