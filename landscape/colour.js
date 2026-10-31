// THE GROUND'S COLOURS: what each cell of a scene looks like from the surface it holds -- the lab draws its ground in
// them, and the world (landmap.js) takes them where the land is bare: rock, scree, sand, snow.
export const SURF_COL = { scree: [.55, .52, .48], soil: [.47, .38, .27], grass: [.42, .55, .26], forest: [.20, .34, .17], sand: [.83, .72, .52], snow: [.93, .95, .97], gravel: [.66, .6, .52], tufa: [.84, .81, .66], cinders: [.36, .22, .18], lava: [.17, .16, .16], shingle: [.6, .6, .58], "black sand": [.25, .24, .24], "white sand": [.93, .9, .82], salt: [.94, .93, .9], bog: [.33, .35, .2], mangrove: [.36, .31, .23], reeds: [.42, .46, .24], sulfur: [.86, .77, .3], altered: [.8, .74, .62] };
export function grassTone(clim) { return clim.plants === "tundra" ? [.52, .55, .38] : clim.plants === "scrub" ? [.55, .55, .33] : clim.plants === "jungle" ? [.25, .5, .2] : SURF_COL.grass; }

// How BARE each surface is, 0..1: how little of a lawn the world may lay over it (its grass, its own green, where the
// scene's is grass, forest floor or soil under plants; soil in a desert is the ground itself, and a bog or a reed bed
// half its own)
export function bareOf(s, clim) {
  return s === "grass" || s === "forest" ? 0 : s === "soil" ? (clim.plants === "desert" || clim.plants === "none" ? 1 : .3)
       : s === "reeds" ? .3 : s === "bog" ? .5 : 1;
}

// the colour of every cell, N*N*3
export function surfaceColours(L) {
  const { N, dx, H, surf, SURF, bed, strata } = L;
  const col = new Float32Array(N * N * 3);
  const grass = grassTone(L.climate);
  // (scree is the cap broken -- its colour, greyed; soil is the rock under it weathered -- a little of its colour in the
  // brown, red where the tropics leach it to laterite)
  const mix = (a, b, t) => a.map((v, q) => v + (b[q] - v) * t);
  const scree = mix(strata.beds[L.plan.capK].color, [.55, .53, .5], .35);
  // (and on limestone where the summers are dry, TERRA ROSSA: the clay the rock leaves when it dissolves, its iron rusted
  // red -- the brighter for the little the plants add to it)
  const rossa = (b) => b.karst && L.climate.temp >= 12 && L.climate.rain >= 300 && L.climate.rain < 1000;   // (a dry summer, a wet winter: not a desert's)
  const soilOf = strata.beds.map((b) => L.climate.temp > 18 && L.climate.wet > .5 ? mix([.55, .27, .16], b.color, .3) : rossa(b) ? mix([.6, .27, .15], b.color, .12) : mix(SURF_COL.soil, b.color, .3));
  for (let k = 0; k < N * N; k++) {
    const i = k % N, j = (k / N) | 0, x = i * dx, y = j * dx;
    const s = SURF[surf[k]];
    let c;
    if (s === "rock") {
      const b = strata.beds[bed[k]], depth = strata.datum(x, y) - H[k] - strata.base[bed[k]];
      const band = b.rock === "granite" ? 1 : 1 - .07 * ((depth * 1.7) % 1 < .5 ? 1 : 0) - .05 * Math.sin(depth * 5.1);   // (the bedding in it -- granite has none)
      c = b.color.map((v, q) => (v + (L.stainCol[q] - v) * L.stain[k]) * band);   // (and the streaks down its face)
    } else if (s === "grass" || s === "forest" || s === "soil") {   // (the floor under the trees darker, by how much they cover)
      const base = s === "soil" ? soilOf[bed[k]] : grass, v = Math.min(1, L.veg[k] * 1.3);
      c = base.map((b, q) => b + (SURF_COL.forest[q] - b) * v);
    } else c = s === "scree" ? scree : s === "gravel" ? mix(scree, SURF_COL.gravel, .6) : SURF_COL[s];   // (a fan's gravel: the beds above it, worn)
    const jit = 1 + .06 * (Math.sin(i * 12.9898 + j * 78.233) * 43758.5453 % 1);
    col.set(c.map((v) => v * jit), k * 3);
  }
  return col;
}
