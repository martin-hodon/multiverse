// The plants' shared state, set by index.html and read by every shader that sways or whitens (the leaf cards that lived
// here are plants/render.js since 2026-11-18: docs/plants.md).

// snow lying, 0..1 (index.html sets it with the weather): the roofs, the grass and the leaves' tops whiten with it
export const SNOW = { value: 0 };
// the harvest in, 0 / 1 (index.html: late autumn): the grain fields cut to stubble, the sheaves stood in stooks (architecture.js crops)
export const HARVEST = { value: 0 };
// the one wind clock, seconds: the trees, the grain and the banners sway on it together (index.html ticks it)
export const FOLIAGE_T = { value: 0 };
