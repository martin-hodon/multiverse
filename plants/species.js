// THE PLANTS' SPECIES (2026-11-18): what the growth model (grow.js) makes of each tree and bush -- its habit, its trunk,
// its branching level by level, its twigs and leaves, its flowers and fruit -- and what the bakes (bake.js) paint
// for it: the bark, the twig sprays, the blossom. Every number is in METRES or DEGREES or a share.
//
// THE DATA is the assets' (2026-11-18): assets/plants/trees/<name>.json, one a species, and assets/plants/bush.json (the
// bush and its fruits) -- edited, and drawn live as the engine draws them, in the asset manager (assets.html, Plants).
// Colours there are "#rrggbb"; here they are numbers again (speciesDef). What follows documents their parameters.
//
// A TREE
//   height [lo, hi]          metres, drawn per variant
//   habit                    "broad" (a trunk that forks into leaders: oak, maple, apple), "excurrent" (one leader to
//                            the top: birch, pine early, spruce, cypress), "weeping" (broad, the outer levels hanging:
//                            willow), "palm" (a bare bole and a crown of fronds), "bottle" (broad on a swollen bole:
//                            the ceiba, the baobab), "forking" (forks of forks, rosettes of sword leaves at the ends: the
//                            dragon blood tree, the Joshua tree -- `fork` below), "shrub" (stems from the ground: the
//                            oleander, the hydrangea, the rhododendron, the bush), "column" (a ribbed cactus column
//                            and its arms: the saguaro -- `arms` below), "pads" (flat pads grown from each other's
//                            rims on a short stem: the prickly pear -- `pads` below). The banana is a "palm" (its
//                            paddle leaves are fronds), the bamboo a "shrub" of canes
//   trunk {
//     r          base radius as a share of the height (above the flare)
//     taper      how fast it narrows, 1 linear .. <1 holds its girth longer (a ceiba's bulge is `bulge`)
//     flare      the root flare: how much wider at the ground (.5: half again), over `flareH` metres
//     buttress   lobes round the foot (0 none), their depth `buttressA`
//     lean       degrees, the most it leans;  sway  its slow S-bends (metres per 10 m)
//     split      broad habits: { at: share of the height where it forks, n: [lo, hi] leaders, angle: degrees off
//                the axis, again: share of leaders that fork once more }
//     bulge      a bottle trunk: { at: share of the trunk, a: how much wider there }
//     knobs      a ceiba's prickles: { n: count on the trunk, len: metres, up: to what share of the trunk }
//     gnarl      0..1: a contorted trunk and leaders (an old olive, a yew)
//   }
//   crown { base: share of the height below the first limbs, shape (an envelope over the trunk's crown part: conical,
//           spherical, hemispherical, flame, cylindrical, tapered, inverse, umbrella), asym: how lopsided toward one
//           side's light (0..1), gaps: share of limbs that are missing (a crown with holes), dead: share of the lowest
//           limbs that are bare snags; a palm's: fronds [n], len [m], width (m), and a banana's bunch { hands [n],
//           fingers [n a hand], gap (m between hands), arc (m: the stalk's bow out of the crown), drop (m of bare
//           rachis below the hands), bud (m) } -- grown as BODIES, tubes of their own (grow.js bunch, mesh.js); a palm's
//           frond shape: rise [lo, hi] degrees (the oldest's, the youngest's), droop (x), fold (the V along the rachis;
//           < 0 the leaflets hang: a coconut's), fan (a FAN leaf: the share of it that is bare stalk), skirt { n [lo, hi],
//           down (m), len (x) } (a fan palm's dead leaves hanging on the trunk), nuts { n [lo, hi], bunches [lo, hi],
//           len (m), r } (a coconut's, as bodies) }
//   levels [ for the children of the trunk (1), of those (2), (3) ] {
//     n          children along a parent of the typical length (scaled by the parent's real length)
//     start      share of the parent bare at its base
//     angle      [at the parent's base, at its tip] degrees off the parent;  jitter  degrees of noise
//     rot        degrees each child turns round the parent from the last (137.5 spiral, 180 two ranks); whorl  children
//                at one place (conifers' whorls)
//     len        share of the parent's length;  lenV  its spread (lognormal)
//     rr         base radius as a share of the parent's there (before the length's own scaling)
//     gravity    droop over the branch (+ down, - up);  photo  how the tip turns up toward the light (+)
//     wiggle     segment noise (radians);  kink  the chance a segment turns sharply (a gnarled oak's sympodial growth)
//     segs       segments a branch is walked in
//   }
//   twig { style: the spray painted (bake.js TWIGS), size [lo, hi] metres of a spray card, start: share of a branch
//          bare of sprays, up: how much the cards face the sky (0..1), hang: cards hanging down along their branch
//          (the willow), dense: more or fewer than the level's count, cover: the cards' area over the crown's surface
//          (mesh.js leafMesh: how full the crown is, 2.4 if not given) }
//          The DEEPEST level with children (`levels`) is not wood: its children are the sprays -- each card a twig
//          or a branchlet with its leaves, laid where it would grow (grow.js). So a level's `n` there is sprays per
//          parent, and the wood is the levels above it: ~25 limbs and ~100 branches in a big tree's ~3k triangles.
//   colors { bark: base hex, barkDark, leaf: [two greens the cards range over], autumn: hex (broadleaves), blossom,
//            fruit } -- tints over the bakes' own colour (the bakes are painted near neutral leaf green and bark grey)
//   season { evergreen, blossom: the spring bloom (orchard trees: white/pink sprays), flowers: share of sprays in flower
//            all year (the ceiba in its flowering season), fruit: share of sprays carrying fruit in summer and autumn }
//   warm / orchard   not in the wild mix (periods.json names the warm ones; orchards are planted by sites)
//
// A FORKING tree (habit "forking") has `fork` instead of levels: { depth: [lo, hi] rounds of forking, three: share
// forking in three, angle: degrees off the parent, len: the first forks as a share of the height, ratio: each round's
// length to the last's, lenV, stop: chance an arm stops early, gravity, photo, wiggle, kink }; its `twig` is a
// rosette { style: "rosette", cards: crossed cards a rosette, mid: where its middle is up the card, rise: how much it
// turns up, along: more rosettes back along the arm, blades, blade: [lo, hi] px long, width, reach: how far round
// they spread (1: right down), dead: share hanging dry, bloom: a cream flower cluster on top (season.flowers) }
//
// A COLUMN (habit "column", the saguaro) has no levels: one column, `trunk.ribs` ribs standing out `ribA` (mesh.js), stiff
// in the wind (`trunk.stiff` 0..1), and `arms` { n: [lo, hi], at: [lo, hi] share of the height, out: [lo, hi] metres level
// before the elbow, up: [lo, hi] share of the height risen after it, r: [lo, hi] girth to the trunk's, droop: share that
// dip first }; its `twig` crowns every top (style "saguaro": the spiny felt, and its flowers and fruit in season)
//
// A PAD cactus (habit "pads", the opuntia): `trunk.stem` metres of woody stem, then `pads` { first: [lo, hi] pads on
// it, depth: [lo, hi] pads deep, kids: [lo, hi] grown from a pad's upper rim, size: [lo, hi] a first pad's card (its
// painted oval: bake.js opuntia), shrink: each pad to its parent's, spread: degrees off its parent's axis, rise: how
// much a pad leans up }. Its pads are never turned to the eye, and the far levels keep them all (mesh.js leafMesh)
//
// A BUSH is a tree of habit "shrub": several stems from the ground (trunk.stems), no crown base.

import oak from "../assets/plants/trees/oak.json" with { type: "json" };
import birch from "../assets/plants/trees/birch.json" with { type: "json" };
import pine from "../assets/plants/trees/pine.json" with { type: "json" };
import spruce from "../assets/plants/trees/spruce.json" with { type: "json" };
import willow from "../assets/plants/trees/willow.json" with { type: "json" };
import cypress from "../assets/plants/trees/cypress.json" with { type: "json" };
import maple from "../assets/plants/trees/maple.json" with { type: "json" };
import palm from "../assets/plants/trees/palm.json" with { type: "json" };
import ceiba from "../assets/plants/trees/ceiba.json" with { type: "json" };
import apple from "../assets/plants/trees/apple.json" with { type: "json" };
import cherry from "../assets/plants/trees/cherry.json" with { type: "json" };
import yew from "../assets/plants/trees/yew.json" with { type: "json" };
import olive from "../assets/plants/trees/olive.json" with { type: "json" };
import plane from "../assets/plants/trees/plane.json" with { type: "json" };
import magnolia from "../assets/plants/trees/magnolia.json" with { type: "json" };
import oleander from "../assets/plants/trees/oleander.json" with { type: "json" };
import chestnut from "../assets/plants/trees/chestnut.json" with { type: "json" };
import baobab from "../assets/plants/trees/baobab.json" with { type: "json" };
import jacaranda from "../assets/plants/trees/jacaranda.json" with { type: "json" };
import dragon from "../assets/plants/trees/dragon.json" with { type: "json" };
import joshua from "../assets/plants/trees/joshua.json" with { type: "json" };
import acacia from "../assets/plants/trees/acacia.json" with { type: "json" };
import citrus from "../assets/plants/trees/citrus.json" with { type: "json" };
import hydrangea from "../assets/plants/trees/hydrangea.json" with { type: "json" };
import rhododendron from "../assets/plants/trees/rhododendron.json" with { type: "json" };
import saguaro from "../assets/plants/trees/saguaro.json" with { type: "json" };
import linden from "../assets/plants/trees/linden.json" with { type: "json" };
import tuliptree from "../assets/plants/trees/tuliptree.json" with { type: "json" };
import araucaria from "../assets/plants/trees/araucaria.json" with { type: "json" };
import banana from "../assets/plants/trees/banana.json" with { type: "json" };
import bamboo from "../assets/plants/trees/bamboo.json" with { type: "json" };
import grape from "../assets/plants/trees/grape.json" with { type: "json" };
import hazel from "../assets/plants/trees/hazel.json" with { type: "json" };
import opuntia from "../assets/plants/trees/opuntia.json" with { type: "json" };
import persimmon from "../assets/plants/trees/persimmon.json" with { type: "json" };
import paulownia from "../assets/plants/trees/paulownia.json" with { type: "json" };
import avocado from "../assets/plants/trees/avocado.json" with { type: "json" };
import cacao from "../assets/plants/trees/cacao.json" with { type: "json" };
import delonix from "../assets/plants/trees/delonix.json" with { type: "json" };
import albizia from "../assets/plants/trees/albizia.json" with { type: "json" };
import kiwi from "../assets/plants/trees/kiwi.json" with { type: "json" };
import coconut from "../assets/plants/trees/coconut.json" with { type: "json" };
import fanpalm from "../assets/plants/trees/fanpalm.json" with { type: "json" };
import ginkgo from "../assets/plants/trees/ginkgo.json" with { type: "json" };
import hibiscus from "../assets/plants/trees/hibiscus.json" with { type: "json" };
import bush from "../assets/plants/bush.json" with { type: "json" };

// a definition as written (an asset's JSON) made what the engine reads: its colours numbers, its notes dropped
export function speciesDef(doc) {
  const num = (v) => typeof v === "string" && /^#[0-9a-f]{6}$/i.test(v) ? parseInt(v.slice(1), 16) : Array.isArray(v) ? v.map(num) : v;
  const { _about, fruits, ...S } = doc;
  return { ...S, colors: Object.fromEntries(Object.entries(S.colors ?? {}).map(([k, v]) => [k, num(v)])) };
}

export const TREES = Object.fromEntries(Object.entries({ oak, birch, pine, spruce, willow, cypress, maple, palm, ceiba, apple, cherry,
  yew, olive, plane, magnolia, oleander, chestnut, baobab, jacaranda, dragon, joshua, acacia, citrus, hydrangea, rhododendron, saguaro,
  linden, tuliptree, araucaria, banana, bamboo, grape, hazel, opuntia, persimmon, paulownia, avocado, cacao, delonix, albizia, kiwi,
  coconut, fanpalm, ginkgo, hibiscus }).map(([k, d]) => [k, speciesDef(d)]));
// A BUSH: a shrub of several stems from the ground; `fruit` names its berries (BUSH_FRUITS) or none
export const SHRUB = speciesDef(bush);
export const BUSH_FRUITS = bush.fruits.map((f) => ({ name: f.name, color: parseInt(f.color.slice(1), 16) }));

export const TREE_SPECIES = Object.keys(TREES).filter((k) => !TREES[k].orchard && !TREES[k].warm);   // the wild mix
export const WARM_TREES = Object.keys(TREES).filter((k) => TREES[k].warm);
export const FRUIT_TREES = Object.keys(TREES).filter((k) => TREES[k].orchard);
