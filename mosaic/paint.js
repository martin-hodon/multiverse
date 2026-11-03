// MOSAIC, the stones coloured (docs/mosaic.md): each its slot's colour, its own tone, a little of `mix`'s other stones, modelling by
// row. A joint is half mortar, half the dust of the stones beside it. It still changes a floor seen from afar, so stones are
// lifted to make up what the joints take (in linear light, by how much of each colour's area is stone): from a distance a
// floor is as light as what it was drawn from.
const lin = (v) => { v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; };
const srgb = (v) => 255 * (v <= .0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - .055);
const hashOf = (k, seed) => { let h = Math.imul(k ^ seed, 2654435761); h ^= h >>> 15; h = Math.imul(h, 2246822519); return ((h ^ (h >>> 13)) >>> 0) / 4294967296; };

export function colourStones({ stones: st, cover, mortar, W, H }, map, pal, groutRGB, L) {
  const n = st.x.length, out = new Float32Array(n * 3), tone = L.tone ?? .05, gleam = L.gleam ?? 0, seed = L.seed ?? 1, mix = L.mix ?? {}, model = L.model ?? {};
  // (how much of each slot's region lies under its stones)
  const area = new Float64Array(pal.length), under = new Float64Array(pal.length);
  for (let i = 0; i < W * H; i++) { const s = st.slot[cover[i] - 1]; area[s]++; if (!mortar[i]) under[s]++; }
  const G = groutRGB.map(lin), lift = pal.map((c, s) => { const k = Math.max(.4, Math.min(1, under[s] / Math.max(1, area[s]))); return c.map((v, q) => Math.min(1, Math.max(0, (lin(v) - (1 - k) * .5 * G[q]) / (k + (1 - k) * .5)))); });
  for (let k = 0; k < n; k++) {
    let slot = st.slot[k]; const list = mix[slot];
    if (list) slot = list[Math.floor(hashOf(k * 3 + 1, seed) * list.length) % list.length];
    const row = st.row[k], m = model[st.slot[k]], shade = m ? m[Math.min(row, m.length - 1)] ?? 0 : 0;
    // (`gleam`: glass set at its own tilt. Most stones lie a little dull, a few catch the light whole; and the rows' undulation lights patches, in whole turns of the tile)
    const tilt = gleam ? gleam * (hashOf(k * 11 + 5, seed) ** 6 * 1.3 - .1 + .12 * Math.sin(6.283 * (st.x[k] / W * 2 + st.y[k] / H) + seed) * Math.sin(6.283 * (st.y[k] / H * 3 - st.x[k] / W))) : 0;
    const tn = shade + tilt + tone * (2 * hashOf(k, seed) - 1), warm = tone * .25 * (2 * hashOf(k * 7 + 3, seed) - 1), c = lift[slot];
    for (let q = 0; q < 3; q++) out[k * 3 + q] = Math.min(1, Math.max(0, c[q] * (1 + tn + (q === 0 ? warm : q === 2 ? -warm : 0))));
  }
  return out;
}

// the texels: stones and grout at the map's grid, boxed down to the tile's in linear light, as the lift reckoned. { rgba, W, H }
export function paintStones(layout, colours, groutRGB, px, thick = 1) {
  const { cover, mortar, W, H } = layout, [w, h] = px, rgba = new Uint8ClampedArray(w * h * 4), fx = W / w, fy = H / h, G = groutRGB.map(lin), gm = .5 * thick, sm = 1 - gm, out = new Uint8Array(4097).map((_, i) => srgb(i / 4096) + .5);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let r = 0, g = 0, b = 0, c = 0;
    const y0 = Math.floor(y * fy), y1 = Math.max(y0 + 1, Math.floor((y + 1) * fy)), x0 = Math.floor(x * fx), x1 = Math.max(x0 + 1, Math.floor((x + 1) * fx));
    for (let Y = y0; Y < y1; Y++) for (let X = x0; X < x1; X++) {
      const k = cover[Y * W + X];
      const s = (k - 1) * 3;
      if (!mortar[Y * W + X]) { r += colours[s]; g += colours[s + 1]; b += colours[s + 2]; }
      else { r += G[0] * gm + colours[s] * sm; g += G[1] * gm + colours[s + 1] * sm; b += G[2] * gm + colours[s + 2] * sm; }
      c++;
    }
    const i = (y * w + x) * 4;
    rgba[i] = out[Math.round(r / c * 4096)]; rgba[i + 1] = out[Math.round(g / c * 4096)]; rgba[i + 2] = out[Math.round(b / c * 4096)]; rgba[i + 3] = 255;
  }
  return { rgba, W: w, H: h };
}
