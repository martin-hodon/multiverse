// The terrain, built off the main thread.
//
// Building the ground means asking groundH a few hundred thousand times -- seconds of arithmetic, and the
// page is frozen for every one of them if the main thread does it. None of it touches three or the DOM, so it
// belongs here: the worker rebuilds the same height function from the world's own numbers (ground.js takes
// them as data, so there is no second copy of the terrain's shape anywhere) and posts back the vertex arrays,
// transferred rather than copied.
import { makeGround } from "./ground.js";
import { buildTerrainData } from "./terrain_data.js";

self.onmessage = (e) => {
  const { cfg, opts, grade } = e.data;
  const t0 = performance.now();
  const { groundH } = makeGround(cfg);
  const { blocks, stats } = buildTerrainData({ ...opts, grade, height: groundH });
  stats.ms = Math.round(performance.now() - t0);
  // every array is transferred: the worker hands the memory over instead of the page copying it back
  const transfer = [];
  for (const b of blocks) transfer.push(b.pos.buffer, b.nor.buffer, b.col.buffer, b.idx.buffer);
  self.postMessage({ blocks, stats }, transfer);
};
