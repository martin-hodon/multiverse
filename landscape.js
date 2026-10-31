// SMALL-SCALE LANDSCAPES (2026-10-28; docs/landscape.md): a scene a few hundred metres across at a metre a cell -- an
// escarpment, the stream that falls over it and the gorge its fall has cut back, the lake it leaves above the lip, the
// island in it, the cave under the cap -- each where and as its rocks and its climate make it, not drawn.
//
//   GEOLOGY  a stack of beds (the preset's: hard caps over soft shales, limestone, basalt flows), dipping a little and
//            warped; rockAt(x, y, z) is the bed at any point -- what a wall shows, how steep it stands, what it is made of
//   CLIMATE  rain and warmth: whether the stream flows or only runs after storms, how much loose rock frost makes, the
//            soil and what grows on it, what made the lake's hollow
//   RELIEF   the upland on its cap, the scarp where the cap ends, the lowland below
//   PLAN     the components placed as they arise, along the water: the stream across the upland, through the lake, over
//            the lip; the gorge cut back from the scarp to the fall at its head; the plunge pool; the island a hard knob
//   CARVE    each component cut into the ground as a profile along its line -- the walls left standing, vertical
//   SETTLE   every column as steep as its rock stands (hard beds near vertical, shales ~32 deg): what is steeper falls
//            and lies at the foot as scree (34 deg), and the stream carries away what lands in it -- so a wall steps
//            bed by bed, a cliff over a shale slope over a bench, without anyone saying so
//   WATER    the lakes filled to their spill level, the water gathered down the land, the streams, the falls
//   DRESS    what the surface is: bare bed, scree, soil, grass, forest, sand -- for the colours, the plants, the boulders
//
// Pure arithmetic on arrays: no three, no DOM (a worker can make one). makeLandscape(spec) -> the scene.
//
// The engine is in landscape/: core.js (noise, random numbers, the grid), presets.js (rocks, geologies, climates),
// mesh.js, colour.js (the ground's colours, for the lab and the world), and the stages by what makes them -- frame,
// relief, river, glacial, coastal, karst, volcano, desert, slopes, caves, water, dress. Each stage is a function of the
// scene so far (`c`: everything the stages before it made), adding what it makes; STAGES is their order, which
// matters -- the scene's random numbers are drawn in it.

import { frame, strata } from "./landscape/frame.js";
import { relief, plan, meanders, outliers, domes, lake, lakeHollow } from "./landscape/relief.js";
import { coast, dunes, mouth, causeway, tombolo } from "./landscape/coastal.js";
import { playa, yardangs, barchans, tinajas, slot, fins, hoodoos } from "./landscape/desert.js";
import { cone, maar, dike, hotSpring, fumaroles } from "./landscape/volcano.js";
import { streamBed, terraces, fans, oxbow, delta, tributary, ravines } from "./landscape/river.js";
import { moraine, braids, esker, rockGlacier, knock, cirque, solifluction } from "./landscape/glacial.js";
import { tufa, sinking, dolines, cockpit, pavement } from "./landscape/karst.js";
import { landslide, couloirs, settle } from "./landscape/slopes.js";
import { caves, bridge } from "./landscape/caves.js";
import { water } from "./landscape/water.js";
import { surfaceGrids, stain, ground, riparian, forest, trees, boulders, result } from "./landscape/dress.js";

export { noise, fbm, rng } from "./landscape/core.js";
export { ROCKS, SCREE_ANGLE, GEOLOGY, CLIMATES, climateOf, makeStrata, DEFAULT_FEATURES } from "./landscape/presets.js";
export { surfaceNets } from "./landscape/mesh.js";

export const STAGES = [frame, strata, relief, plan, meanders, coast, outliers, domes, lake, playa, cone, maar,
  streamBed, terraces, fans, moraine, dunes, braids, mouth, tufa, oxbow, lakeHollow, esker, yardangs, delta, tributary,
  sinking, dolines, cockpit, landslide, rockGlacier, knock, dike, causeway, tombolo, cirque, couloirs, ravines,
  barchans, settle, tinajas, slot, fins, hotSpring, caves, bridge, pavement, solifluction, water, surfaceGrids,
  fumaroles, stain, ground, riparian, forest, hoodoos, trees, boulders, result];

export function makeLandscape(spec = {}) {
  const c = { spec };
  let scene;
  for (const stage of STAGES) scene = stage(c);
  return scene;
}
