// The finish tiles, drawn off the main thread while the map grows.
//
// A building's finish draws its patterns once each (patterns.js renderPattern) -- seconds of canvas work, most of the
// buildings' boot. The map grows on the GPU before any building is built, and the main thread only waits on it then; so
// archmat.js drawTilesAhead hands the tiles the world will ask for to a few of these, and each draws them with the same
// library (registered from the same documents) and posts back the layer the tile array wants: the tile stretched to
// its square and flipped bottom row first (archmat.js tileLayer), the pixels transferred rather than copied. A tile it
// cannot draw says so, and the page draws it.
import { registerPatterns, renderPattern } from "./patterns.js";
import { registerGlyphs } from "./glyphs.js";   // (the layer kinds the page registers too: hieroglyphs, tomb paintings)
import { registerMurals } from "./murals.js";

let R = 512, cv = null;
self.onmessage = (e) => {
  const m = e.data;
  if (m.library) { registerPatterns(m.library.families); registerGlyphs(m.library.glyphs); registerMurals(m.library.murals); R = m.res; return; }
  try {
    const tile = renderPattern(m.pattern, { palette: m.palette, params: m.params, res: m.res });
    const cx = (cv ??= new OffscreenCanvas(R, R)).getContext("2d", { willReadFrequently: true });
    cx.clearRect(0, 0, R, R); cx.drawImage(tile.canvas, 0, 0, R, R);
    const px = cx.getImageData(0, 0, R, R).data, row = R * 4, out = new Uint8Array(R * row);
    for (let y = 0; y < R; y++) out.set(px.subarray(y * row, (y + 1) * row), (R - 1 - y) * row);
    self.postMessage({ key: m.key, size: tile.size, repeat: tile.repeat, px: out }, [out.buffer]);
  } catch (err) {
    self.postMessage({ key: m.key, err: String(err?.message ?? err) });
  }
};
