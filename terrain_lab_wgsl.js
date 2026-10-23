// THE TERRAIN LAB'S SHADERS (docs/terrain_lab.md). One module of compute kernels for the simulation -- every process a
// pass over the cells, a thread a cell -- one for the view's upscaling, one to draw it.
//
// The parameters are one uniform struct, written from ONE list (PARAMS below): the WGSL struct and the JS packing
// (terrain_lab.js) both come from it, so the two cannot drift.

// ---- the parameters ------------------------------------------------------------------------------------------------
// scalars first (4 bytes each), then the vec4 arrays; `f` f32, `u` u32
export const SCALARS = [
  ["N", "u"], ["L", "u"], ["nPlates", "u"], ["nHot", "u"],
  ["dx", "f"], ["dt", "f"], ["rain", "f"], ["sea", "f"],
  ["K", "f"], ["V", "f"], ["kappa", "f"], ["weather", "f"],
  ["eps", "f"], ["slide", "f"], ["lith", "f"], ["carb", "f"],
  ["carbMud", "f"], ["upliftBg", "f"], ["plateK", "f"], ["plateW", "f"],
  ["riftBasalt", "f"], ["lavaYield", "f"], ["lavaCool", "f"], ["rockVar", "f"],
  ["time", "f"], ["seed", "f"], ["lakeMin", "f"], ["soilH", "f"],
  ["Qc", "f"], ["upNoise", "f"], ["orog", "f"], ["drift", "f"],
  ["waves", "f"], ["waveBase", "f"], ["shelfSlope", "f"], ["nOut", "u"],
  ["fallS", "f"], ["plunge", "f"], ["nIn", "u"], ["pad1", "f"],
];
export const ARRAYS = [["brush", 1], ["mat", 8], ["plates", 8], ["hot", 16], ["outl", 4], ["inl", 4]];   // [name, count of vec4]
export const MAX_PLATES = 8, MAX_HOT = 16, MAX_MATS = 8, MAX_OUT = 4, MAX_IN = 4;
const TY = { f: "f32", u: "u32" };
export const PARAM_STRUCT = `struct P {\n${SCALARS.map(([n, t]) => `  ${n}: ${TY[t]},`).join("\n")}\n` +
  ARRAYS.map(([n, k]) => k === 1 ? `  ${n}: vec4<f32>,` : `  ${n}: array<vec4<f32>, ${k}>,`).join("\n") + "\n}\n";
// float index of each field in the packed buffer
export const PARAM_INDEX = (() => {
  const idx = {}; let i = 0;
  for (const [n] of SCALARS) idx[n] = i++;
  i = Math.ceil(i / 4) * 4;
  for (const [n, k] of ARRAYS) { idx[n] = i; i += 4 * k; }
  idx.__size = i;
  return idx;
})();

// the materials, in the shaders' order: erodibility, weathering, the slope a 100m cell of it stands at before it slides
// (a whole slope's, gentler than a single cliff's), what rain dissolves (m per m of rain), how rough its surface is in
// the view (m), its colour
export const MATS = [
  { name: "granite", erod: .25, weather: .3, angle: 42, dissolve: 0, rough: 14, color: [.66, .58, .56] },
  { name: "basalt", erod: .35, weather: .4, angle: 48, dissolve: 0, rough: 10, color: [.2, .2, .22] },
  { name: "sandstone", erod: 1.0, weather: 1.0, angle: 34, dissolve: 0, rough: 7, color: [.78, .46, .3] },
  { name: "limestone", erod: .6, weather: .4, angle: 40, dissolve: 5e-5, rough: 7, color: [.84, .83, .76] },
  { name: "sediment", erod: 4.0, weather: 0, angle: 27, dissolve: 0, rough: 1, color: [.72, .6, .38] },
];

const COMMON = /* wgsl */`
${PARAM_STRUCT}
const GRANITE = 0u; const BASALT = 1u; const SAND = 2u; const LIME = 3u; const SED = 4u;
const PI = 3.14159265;
// gradient noise in about [-1, 1] (unit gradients, quintic; spread like value noise's, 0.43), on a lattice turned off the
// grid's axes -- value noise's contours run along its lattice, and with the lattice along the grid, cap edges, valleys and
// soft rock came out in straight lines. 's' seeds it.
fn nhash(q: vec2<f32>, s: f32) -> vec2<f32> {
  let a = 6.2831853 * fract(sin(dot(q, vec2<f32>(127.1, 311.7)) + s * 17.13) * 43758.5453);
  return vec2<f32>(cos(a), sin(a));
}
fn gnoise(x0: vec2<f32>, s: f32) -> f32 {
  let x = vec2<f32>(0.8 * x0.x - 0.6 * x0.y, 0.6 * x0.x + 0.8 * x0.y);
  let i = floor(x); let f = x - i; let u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  let a = dot(nhash(i, s), f); let b = dot(nhash(i + vec2<f32>(1.0, 0.0), s), f - vec2<f32>(1.0, 0.0));
  let c = dot(nhash(i + vec2<f32>(0.0, 1.0), s), f - vec2<f32>(0.0, 1.0)); let d = dot(nhash(i + vec2<f32>(1.0, 1.0), s), f - vec2<f32>(1.0, 1.0));
  return clamp(2.0 * mix(mix(a, b, u.x), mix(c, d, u.x), u.y), -1.0, 1.0);
}
`;

// ---- THE SIMULATION -----------------------------------------------------------------------------------------------
// col: a column -- base (the basement's top), n (layers), H (the ground), lava (m still molten on it)
// lay: its layers, bottom to top -- thickness, material
// flow: Qs_in (sediment coming in, m3/yr), -, 1/sum of its outflow weights, S (steepest slope of the water surface)
// aux: painted uplift (m/yr), -, the uplift this step (m/yr), -
// wb: the water surface, ping and pong;  acc: discharge Q and sediment out Qs, ping (xy) and pong (zw)
// out8: what a cell sends to each of its 8 neighbours (sliding rock, lava)
export const SIM = /* wgsl */`
${COMMON}
struct It { cur: u32, reset: u32, a: u32, b: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read_write> col: array<vec4<f32>>;
@group(0) @binding(2) var<storage, read_write> lay: array<vec2<f32>>;
@group(0) @binding(3) var<storage, read_write> flow: array<vec4<f32>>;
@group(0) @binding(4) var<storage, read_write> aux: array<vec4<f32>>;
@group(0) @binding(5) var<storage, read_write> wb: array<vec2<f32>>;
@group(0) @binding(6) var<storage, read_write> acc: array<vec4<f32>>;
@group(0) @binding(7) var<storage, read_write> out8: array<f32>;
@group(0) @binding(8) var<uniform> it: It;

var<private> OX: array<i32, 8> = array<i32, 8>(1, 1, 0, -1, -1, -1, 0, 1);
var<private> OY: array<i32, 8> = array<i32, 8>(0, 1, 1, 1, 0, -1, -1, -1);
var<private> OD: array<f32, 8> = array<f32, 8>(1.0, 1.41421356, 1.0, 1.41421356, 1.0, 1.41421356, 1.0, 1.41421356);

fn isEdge(x: u32, y: u32) -> bool { return x == 0u || y == 0u || x == p.N - 1u || y == p.N - 1u; }
// the region's BASE LEVEL: the whole edge (nOut 0), or only its OUTLETS (x, y, half-width in metres) -- elsewhere the edge
// is no base level but a WALL, the land inside it going on (a copy of its inner neighbour: walls), and the land drains out
// through the outlets. A plateau drains by a river or two: base level all round the square wore it back from all four
// sides into a box of scarps, with gullies straight in from them.
// INLETS (x, y metres on the edge, Q m3/yr, Qs m3/yr): a river from beyond the region comes in there -- the region is a
// piece of a larger land, and its big river drains more than the region does. Its water and sediment join the first
// cell inside the edge.
fn inflow(x: u32, y: u32) -> vec2<f32> {
  var r = vec2<f32>(0.0);
  for (var k = 0u; k < p.nIn; k++) {
    let q = clamp(round(p.inl[k].xy / p.dx), vec2<f32>(1.0), vec2<f32>(f32(p.N) - 2.0));
    if (u32(q.x) == x && u32(q.y) == y) { r += p.inl[k].zw; }
  }
  return r;
}
fn isOutlet(x: u32, y: u32) -> bool {
  if (!isEdge(x, y)) { return false; }
  if (p.nOut == 0u) { return true; }
  let q = vec2<f32>(f32(x), f32(y)) * p.dx;
  for (var k = 0u; k < p.nOut; k++) { if (distance(q, p.outl[k].xy) <= p.outl[k].z) { return true; } }
  return false;
}
// (a WALL -- the edge where it is no outlet, a copy of the land inside it -- is no one's neighbour: water, talus, lava,
//  the fill, all go round it; else it took what came to it and passed nothing on)
fn nbr(x: u32, y: u32, k: u32) -> i32 {
  let nx = i32(x) + OX[k]; let ny = i32(y) + OY[k];
  if (nx < 0 || ny < 0 || nx >= i32(p.N) || ny >= i32(p.N)) { return -1; }
  if (p.nOut > 0u && isEdge(u32(nx), u32(ny)) && !isOutlet(u32(nx), u32(ny))) { return -1; }
  return ny * i32(p.N) + nx;
}
fn wcur(c: u32) -> f32 { return select(wb[c].x, wb[c].y, it.cur == 1u); }
// the water surface as everything but the fill reads it: never under the ground (talus fallen into a lake, uplift, raise
// the ground under a surface the fill has not seen since -- read as it stood, that stale surface was a hole the lakes
// round it drained through, a sweep at a time, and the fill between full refills never raises them back); a cell being
// filled from above (1e7) is dry
fn wsurf(c: u32) -> f32 { let w = wcur(c); return select(max(w, col[c].z), col[c].z, w > 1e6); }
// as the fill reads its neighbours: the same, but a cell at the top of a full refill is at the top
fn wfill(c: u32) -> f32 { return max(wcur(c), col[c].z); }
// the steepest way down from a cell, at any angle (D-infinity, Tarboton): of the 8 triangular facets round it (facet f
// between its neighbour in direction 2*(f/2) -- a side -- and the diagonal next to that -- a corner), the one the surface
// falls fastest across; returns (the slope, the facet + the share of the side, or -1: nowhere lower). Of the water
// surface or of the ground. Water and rock that go down it are split between the side and the corner, so what runs
// 20 degrees off the grid runs 20 degrees off the grid, not in steps along it.
fn facetSide(f: u32) -> u32 { return (f / 2u) * 2u; }
fn facetCorner(f: u32) -> u32 { return select((facetSide(f) + 7u) % 8u, facetSide(f) + 1u, f % 2u == 0u); }
fn surfAt(j: u32, onW: bool) -> f32 { return select(col[j].z, wsurf(j), onW); }
fn steepest(x: u32, y: u32, onW: bool) -> vec2<f32> {
  let z0 = surfAt(y * p.N + x, onW);
  var bestS = 0.0; var bestF = 0u; var bestShare = 1.0;
  for (var f = 0u; f < 8u; f++) {
    let js = nbr(x, y, facetSide(f)); let jc = nbr(x, y, facetCorner(f));
    if (js < 0 || jc < 0) { continue; }
    let e1 = surfAt(u32(js), onW); let e2 = surfAt(u32(jc), onW);
    let s1 = (z0 - e1) / p.dx; let s2 = (e1 - e2) / p.dx;
    var r = atan2(s2, s1); var sl = sqrt(s1 * s1 + s2 * s2);
    if (r < 0.0) { r = 0.0; sl = s1; } else if (r > 0.785398) { r = 0.785398; sl = (z0 - e2) / (p.dx * 1.41421356); }
    if (sl > bestS) { bestS = sl; bestF = f; bestShare = 1.0 - r / 0.785398; }
  }
  if (bestS <= 0.0 && onW) {
    // a TIE: no neighbour lower, one exactly as high (a cell cut below its neighbours takes the lowest one's level -- the
    // dry pass -- and the fill lifts it a step only next time): the water goes on to the tied neighbour with the lower
    // index, never back (the order is strict, so there is no loop), at slope 0
    let c = y * p.N + x;
    for (var k = 0u; k < 8u; k++) {
      let j = nbr(x, y, k);
      if (j >= 0 && u32(j) < c && surfAt(u32(j), true) == z0) { return vec2<f32>(0.0, select(f32(k - 1u), f32(k) + 0.9999, k % 2u == 0u)); }
    }
  }
  return vec2<f32>(bestS, select(-1.0, f32(bestF) + min(bestShare, 0.9999), bestS > 0.0));
}
// the share of what goes down from j (by its facet code z) that comes to its neighbour in direction k (from j)
fn facetShare(z: f32, k: u32) -> f32 {
  if (z < 0.0) { return 0.0; }
  let f = u32(z); let sh = fract(z);
  return select(0.0, sh, facetSide(f) == k) + select(0.0, 1.0 - sh, facetCorner(f) == k);
}
fn qcur(c: u32) -> vec2<f32> { return select(acc[c].xy, acc[c].zw, it.a == 1u); }

// ---- the stack: a cell's own layers
fn li(c: u32, k: u32) -> u32 { return c * p.L + k; }
fn topMat(c: u32, n: u32) -> u32 { if (n == 0u) { return GRANITE; } return u32(lay[li(c, n - 1u)].y); }
fn heightOf(c: u32, n: u32) -> f32 { var h = col[c].x; for (var k = 0u; k < n; k++) { h += lay[li(c, k)].x; } return h; }
fn setCol(c: u32, n: u32) { col[c].y = f32(n); col[c].z = heightOf(c, n); }
// lay 't' metres of material m on the top (onto the top layer if it is the same); a full stack first makes two of its
// beds one (below)
fn addLayer(c: u32, n: ptr<function, u32>, m: u32, t: f32) {
  if (t <= 0.0) { return; }
  let k = *n;
  if (k > 0u && u32(lay[li(c, k - 1u)].y) == m) { lay[li(c, k - 1u)].x += t; return; }
  if (k == 0u && m == GRANITE) { col[c].x += t; return; }
  if (k < p.L) { lay[li(c, k)] = vec2<f32>(t, f32(m)); *n = k + 1u; return; }
  // full: the THINNEST PAIR of neighbouring beds (the top one, the surface, stays) becomes one, of the thicker one's rock
  // (two beds of one rock first). Thin beds join each other and a thick bed keeps its rock -- merging the thinnest bed
  // into the one under it, whatever that was, let a 20 m talus bed take in lava flow after lava flow until a ring of the
  // volcano's core came out sediment.
  var kmin = 0u; var tmin = 1e30;
  for (var j = 0u; j + 2u < p.L; j++) {
    let a = lay[li(c, j)]; let b = lay[li(c, j + 1u)];
    let s = select(a.x + b.x, 0.0, a.y == b.y);
    if (s < tmin) { tmin = s; kmin = j; }
  }
  let a = lay[li(c, kmin)]; let b = lay[li(c, kmin + 1u)];
  lay[li(c, kmin)] = vec2<f32>(a.x + b.x, select(a.y, b.y, b.x > a.x));
  for (var j = kmin + 1u; j + 1u < p.L; j++) { lay[li(c, j)] = lay[li(c, j + 1u)]; }
  lay[li(c, p.L - 1u)] = vec2<f32>(t, f32(m));
}
// take 't' metres off the top, whatever it is (on into the basement)
fn removeTop(c: u32, n: ptr<function, u32>, t0: f32) {
  var t = t0;
  loop {
    if (t <= 0.0) { break; }
    let k = *n;
    if (k == 0u) { col[c].x -= t; break; }
    let th = lay[li(c, k - 1u)].x;
    if (th > t) { lay[li(c, k - 1u)].x = th - t; break; }
    t -= th; *n = k - 1u;
  }
}
// a river's cutting: 'pot' metres of rock of erodibility 1, down through the layers as each one's erodibility allows, but
// no more than 'most' metres; returns the metres removed
fn erodeTop(c: u32, n: ptr<function, u32>, pot0: f32, most: f32) -> f32 {
  var pot = pot0; var rem = 0.0; let sf = soft(c);
  loop {
    if (pot <= 1e-9 || rem >= most) { break; }
    let k = *n;
    if (k == 0u) { let d = min(pot * p.mat[GRANITE].x * sf, most - rem); col[c].x -= d; rem += d; break; }
    let th = lay[li(c, k - 1u)].x; let e = p.mat[u32(lay[li(c, k - 1u)].y)].x * sf; let can = min(pot * e, most - rem);
    if (th > can) { lay[li(c, k - 1u)].x = th - can; rem += can; break; }
    rem += th; pot -= th / e; *n = k - 1u;
  }
  return rem;
}
// buried sediment becomes sandstone; thin layers go into the one below; equal neighbours merge
fn settle(c: u32, n: ptr<function, u32>) {
  var over = 0.0;
  for (var r = i32(*n) - 1; r >= 0; r--) {
    let L = lay[li(c, u32(r))];
    if (u32(L.y) == SED && over > p.lith) { lay[li(c, u32(r))].y = f32(SAND); }
    over += L.x;
  }
  var w = 0u;
  for (var r = 0u; r < *n; r++) {
    let L = lay[li(c, r)];
    if (L.x < 0.05 && r + 1u < *n) { lay[li(c, r + 1u)].x += L.x; continue; }   // (a bed of a few cm joins the one above)
    if (w > 0u && lay[li(c, w - 1u)].y == L.y) { lay[li(c, w - 1u)].x += L.x; }
    else { lay[li(c, w)] = L; w++; }
  }
  *n = w;
}

// a smooth field in [-1, 1] over the region (a few km across): the crust is not the same everywhere
fn vnoise(x: vec2<f32>) -> f32 { return gnoise(x, p.seed); }
fn crust(x: vec2<f32>) -> f32 { return 0.65 * vnoise(x / 5000.0) + 0.35 * vnoise(x / 2100.0 + vec2<f32>(7.3, 1.9)); }
// how easily this cell's rock gives, against its material's own: jointing, faulting, facies change it by up to rockVar
// either way, on a scale of a few hundred metres -- a river finds the weaker rock and wanders with it
fn soft(c: u32) -> f32 {
  let x = vec2<f32>(f32(c % p.N), f32(c / p.N)) * p.dx;
  return 1.0 + p.rockVar * (0.6 * vnoise(x / 700.0 + vec2<f32>(3.1, 8.7)) + 0.4 * vnoise(x / 1600.0 + vec2<f32>(9.4, 2.2)));
}
// the rain a cell gets: more on high ground (orographic)
fn rainAt(c: u32) -> f32 { return p.rain * (1.0 + p.orog * max(col[c].z, 0.0) / 1000.0); }

// ---- 1. tectonics: the plates' boundaries raise and lower the columns; rifts and hotspots put out lava
// (uplift m/yr, basalt m/yr) from the two nearest plate seeds: their relative motion across the boundary
fn plateField(x: vec2<f32>) -> vec2<f32> {
  if (p.nPlates < 2u) { return vec2<f32>(0.0); }
  var d1 = 1e30; var d2 = 1e30; var i1 = 0u; var i2 = 0u;
  for (var k = 0u; k < p.nPlates; k++) {
    let d = distance(x, p.plates[k].xy);
    if (d < d1) { d2 = d1; i2 = i1; d1 = d; i1 = k; } else if (d < d2) { d2 = d; i2 = k; }
  }
  let a = p.plates[i1]; let b = p.plates[i2];
  let ab = b.xy - a.xy; let L = max(length(ab), 1.0); let nrm = ab / L;
  let dist = (d2 * d2 - d1 * d1) / (2.0 * L);           // from x to the boundary (the seeds' bisector)
  let conv = dot(a.zw - b.zw, nrm);                      // m/yr, > 0 converging
  let q = dist / p.plateW; let g = exp(-q * q);
  if (conv > 0.0) { return vec2<f32>(p.plateK * conv * g, 0.0); }
  return vec2<f32>(0.8 * p.plateK * conv * g, -conv * g * p.riftBasalt);    // (a rift sinks about half as fast as a collision rises)
}
@compute @workgroup_size(8, 8) fn tect(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  let x = (vec2<f32>(g.xy) + 0.5) * p.dx;
  let pf = plateField(x);
  if (isEdge(g.x, g.y)) { aux[c].z = 0.0; return; }     // the domain's edge is its base level: fixed
  // (the region's rim is its base level: uplift fades out over its last twelfth or so, along a line that wanders with the
  //  crust -- so it rises as a dome with a ragged edge, not a box)
  let L = f32(p.N) * p.dx; let e = min(min(x.x, L - x.x), min(x.y, L - x.y)) + crust(x + vec2<f32>(4000.0, 900.0)) * L / 18.0;
  let rim = select(smoothstep(0.0, L / 12.0, e), 1.0, p.nOut > 0u);     // (with outlets the walls rise with the land)
  let U = (pf.x * (1.0 + p.upNoise * crust(x)) + p.upliftBg + aux[c].x) * rim;
  col[c].x += U * p.dt; col[c].z += U * p.dt;
  // (the water on it rises with it: a lake's spill rises too, and the fill between its full refills only ever lowers)
  if (wb[c].x < 1e6) { wb[c] += vec2<f32>(U * p.dt); }
  aux[c].z = U;
  var lava = pf.y * p.dt;
  for (var h = 0u; h < p.nHot; h++) {
    let s = p.hot[h]; let q = distance(x, s.xy) / s.w;
    lava += s.z * p.dt / (PI * s.w * s.w) * exp(-q * q);
  }
  col[c].w += lava;
}

// ---- 2. lava: flows down the surface while it is steeper than the lava's yield, then cools into basalt
@compute @workgroup_size(8, 8) fn lavaA(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  for (var k = 0u; k < 8u; k++) { out8[c * 8u + k] = 0.0; }
  let L0 = col[c].w;
  if (L0 <= 1e-4) { return; }
  let Z = col[c].z + L0;
  var ex: array<f32, 8>; var tot = 0.0; var mx = 0.0;
  for (var k = 0u; k < 8u; k++) {
    let j = nbr(g.x, g.y, k); if (j < 0) { continue; }
    let jj = u32(j);
    let e = Z - (col[jj].z + col[jj].w) - p.lavaYield * OD[k] * p.dx;
    if (e > 0.0) { ex[k] = e; tot += e; mx = max(mx, e); }
  }
  if (tot <= 0.0) { return; }
  let mv = min(L0, mx * 0.5);
  for (var k = 0u; k < 8u; k++) { out8[c * 8u + k] = mv * ex[k] / tot; }
}
@compute @workgroup_size(8, 8) fn lavaB(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  if (isEdge(g.x, g.y)) { col[c].w = 0.0; return; }      // (out of the domain)
  var d = 0.0;
  for (var k = 0u; k < 8u; k++) {
    d -= out8[c * 8u + k];
    let j = nbr(g.x, g.y, k); if (j >= 0) { d += out8[u32(j) * 8u + (k + 4u) % 8u]; }
  }
  col[c].w = max(0.0, col[c].w + d);
}
@compute @workgroup_size(8, 8) fn lavaCool(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  let L0 = col[c].w;
  if (L0 <= 0.0 || isEdge(g.x, g.y)) { return; }
  let s = L0 * p.lavaCool;                                 // (a share of what stands a step: a flow is instant in geological time)
  var n = u32(col[c].y);
  addLayer(c, &n, BASALT, s);
  col[c].w = L0 - s;
  setCol(c, n);
}

// ---- 3. hillslopes: whatever stands steeper than its rock holds slides down as talus; loose sediment creeps
// (steeper by the TRUE slope, the steepest way down at any angle, and down that way: judged along the 8 directions, a
// slope facing between two of them stood 8 % steeper than one facing along one, and cliffs squared up with the grid)
@compute @workgroup_size(8, 8) fn slideA(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  for (var k = 0u; k < 8u; k++) { out8[c * 8u + k] = 0.0; }
  if (isEdge(g.x, g.y)) { return; }
  let n = u32(col[c].y); let H0 = col[c].z; let m = topMat(c, n); let tanc = p.mat[m].z;
  var cq: array<f32, 8>; var ct = 0.0;
  for (var k = 0u; k < 8u; k++) {
    let j = nbr(g.x, g.y, k); if (j < 0) { continue; }
    let d = OD[k] * p.dx; let dh = H0 - col[u32(j)].z;
    if (dh > 0.0) { cq[k] = p.kappa * p.dt * dh / (d * p.dx) * select(0.5, 1.0, OD[k] < 1.2); ct += cq[k]; }
  }
  var outs: array<f32, 8>;
  let st = steepest(g.x, g.y, false);
  if (st.x > tanc) {
    let mv = (st.x - tanc) * p.dx * 0.5 * p.slide;
    for (var k = 0u; k < 8u; k++) { outs[k] = mv * facetShare(st.y, k); }
  }
  if (m == SED && ct > 0.0) {                              // creep: no more than half the soil a step
    let th = lay[li(c, n - 1u)].x; let sc = min(1.0, 0.5 * th / ct);
    for (var k = 0u; k < 8u; k++) { outs[k] += cq[k] * sc; }
  }
  for (var k = 0u; k < 8u; k++) { out8[c * 8u + k] = outs[k]; }
}
// ---- 3b. the coast: WAVES attack the land at the sea's edge -- a cliff retreats as its rock and its exposure to the open sea
// allow, down to a metre under the sea (the wave-cut platform) -- and below them, down to WAVE BASE, the shelf is planed and
// what lies on it is carried to deeper water, until the shelf slopes no more than it can hold
fn isSea(j: u32) -> bool { return wsurf(j) <= p.sea + 1e-4 && wsurf(j) - col[j].z > 0.3; }
@compute @workgroup_size(8, 8) fn coastA(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  for (var k = 0u; k < 8u; k++) { out8[c * 8u + k] = 0.0; }
  if (isEdge(g.x, g.y) || p.waves <= 0.0) { return; }
  let n = u32(col[c].y); let H0 = col[c].z;
  let e = p.mat[topMat(c, n)].x * soft(c);
  var w: array<f32, 8>; var tot = 0.0;
  if (wsurf(c) <= H0) {                                     // dry land: is it on the coast?
    for (var k = 0u; k < 8u; k++) {
      let j = nbr(g.x, g.y, k); if (j < 0) { continue; }
      if (isSea(u32(j))) { w[k] = select(0.7, 1.0, OD[k] < 1.2); tot += w[k]; }
    }
    if (tot <= 0.0) { return; }
    let cut = min(p.waves * e * min(tot / 3.0, 1.0) * p.dt, 0.5 * (H0 - (p.sea - 1.0)));
    if (cut <= 0.0) { return; }
    for (var k = 0u; k < 8u; k++) { out8[c * 8u + k] = cut * w[k] / tot; }
  } else if (isSea(c)) {                                   // the shelf, above wave base
    let depth = p.sea - H0;
    if (depth >= p.waveBase) { return; }
    let stir = 1.0 - depth / p.waveBase;
    var loose = 0.0; if (n > 0u && topMat(c, n) == SED) { loose = lay[li(c, n - 1u)].x; }
    let wear = p.waves * 0.05 * e * stir * p.dt;          // (abrasion: the bottom worn down, slowly)
    var mx = 0.0;
    for (var k = 0u; k < 8u; k++) {
      let j = nbr(g.x, g.y, k); if (j < 0) { continue; }
      let ex = (H0 - col[u32(j)].z) - p.shelfSlope * OD[k] * p.dx;
      if (ex > 0.0) { w[k] = ex; tot += ex; mx = max(mx, ex); }
    }
    if (tot <= 0.0) { return; }
    let mv = min(mx * 0.25 * stir, loose + wear);
    for (var k = 0u; k < 8u; k++) { out8[c * 8u + k] = mv * w[k] / tot; }
  }
}
// ---- the moves of a pass (the landslides', the coast's): each cell gives what it sent, as the rock it is, and takes what
// came to it, as sediment
@compute @workgroup_size(8, 8) fn moves(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  if (isEdge(g.x, g.y)) { return; }                      // (what moves into the edge leaves the domain)
  var o = 0.0; var i = 0.0;
  for (var k = 0u; k < 8u; k++) {
    o += out8[c * 8u + k];
    let j = nbr(g.x, g.y, k); if (j >= 0) { i += out8[u32(j) * 8u + (k + 4u) % 8u]; }
  }
  if (o <= 0.0 && i <= 0.0) { return; }
  let W = wsurf(c); let H0 = col[c].z;
  var n = u32(col[c].y);
  removeTop(c, &n, o);
  addLayer(c, &n, SED, i);
  setCol(c, n);
  if (W <= H0 && wcur(c) < 1e6) { aux[c].w = 1.0; }   // (dry: its surface follows its ground -- the dry pass)
}
// DRY LAND STAYS DRY (a pass of its own, after the slides and after the rivers, which mark the cells in aux.w): where the
// surface IS the ground (the fill copies it there, exactly) it follows the ground as it changes -- a shore, however
// shallow, is the lake's and keeps the lake's level -- but never below the lowest surface round it. A delta laid up to a
// lake's surface and cut again the next step is still the lake's (set to its new ground it was a hole the lake drained
// through, metres a step); a pit a river digs is a pool to its rim. Read from one half, written to the other: done in
// the passes that change the ground, each cell read its neighbours as they were being written, and no two runs agreed.
@compute @workgroup_size(8, 8) fn dry(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  var o = wcur(c);
  if (aux[c].w > 0.5) {
    var lo = 1e30;
    for (var k = 0u; k < 8u; k++) { let j = nbr(g.x, g.y, k); if (j >= 0) { lo = min(lo, wsurf(u32(j))); } }
    o = select(col[c].z, max(col[c].z, lo), lo < 1e29);
    aux[c].w = 0.0;
  }
  if (it.cur == 0u) { wb[c].y = o; } else { wb[c].x = o; }
}

// ---- 4. weathering, karst, reefs, burial: a column's own chemistry
@compute @workgroup_size(8, 8) fn weather(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  if (isEdge(g.x, g.y)) { return; }
  var n = u32(col[c].y);
  let H0 = col[c].z;
  let depth = wsurf(c) - H0;
  let top = topMat(c, n);
  var soil = 0.0;
  if (n > 0u && top == SED) { soil = lay[li(c, n - 1u)].x; }
  if (depth < p.lakeMin) {                                 // (under water nothing weathers)
    // the rock under the soil turns into soil, fastest where it is bare; limestone also dissolves
    var rk = i32(n) - 1; if (top == SED) { rk = i32(n) - 2; }
    var rm = GRANITE; if (rk >= 0) { rm = u32(lay[li(c, u32(rk))].y); }
    let wr = p.weather * p.mat[rm].y * exp(-soil / p.soilH) * p.dt;
    let dis = p.mat[rm].w * p.rain * exp(-soil / p.soilH) * p.dt;
    var take = wr + dis;
    if (rk >= 0) { take = min(take, lay[li(c, u32(rk))].x); lay[li(c, u32(rk))].x -= take; }
    else { col[c].x -= take; }
    let made = take * wr / max(wr + dis, 1e-12);          // (what dissolved is gone; what weathered is soil)
    if (top == SED && n > 0u) { lay[li(c, n - 1u)].x += made; }
    else { addLayer(c, &n, SED, made); }
  } else if (depth < 60.0) {                              // clear shallow water grows limestone
    let clear = clamp(1.0 - flow[c].x / p.carbMud, 0.0, 1.0);
    addLayer(c, &n, LIME, p.carb * clear * p.dt);
  }
  settle(c, &n);
  setCol(c, n);
}

// ---- 5. the water surface: the ground with every depression filled to where it spills (Planchon-Darboux), the
// domain's edge and the sea its outlets. From above: reset puts the interior high, a warm start keeps the last one
@compute @workgroup_size(8, 8) fn fillInit(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  let H = col[c].z;
  var w = max(wcur(c), H);
  if (isOutlet(g.x, g.y)) { w = max(H, p.sea); } else if (it.reset == 1u) { w = 1e7; }
  wb[c] = vec2<f32>(w, w);
}
@compute @workgroup_size(8, 8) fn fillIter(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  let H = col[c].z;
  var w = max(H, p.sea);
  if (!isOutlet(g.x, g.y)) {
    var m = 1e30; var lo = 1e30;
    for (var k = 0u; k < 8u; k++) { let j = nbr(g.x, g.y, k); if (j >= 0) { m = min(m, wfill(u32(j)) + p.eps * OD[k]); lo = min(lo, wfill(u32(j))); } }
    if (m <= p.sea + 1.5 * p.eps) { m = p.sea; }           // (the sea is level: its surface is the sea level itself)
    w = max(H, min(wfill(c), m));
    // a PIT (no neighbour lower: the water cannot leave): the warm fill only lowers, and a river's bed makes pits between
    // two full fills, where the river's water stopped -- so a pit is RAISED to its lowest neighbour and a step. One cell's
    // pit is gone in a sweep; a wider hollow rises a step a sweep, the full fill finishes it. (Refilling a pit from above
    // instead cascaded up whole lakes -- each cell lost its one lower neighbour to the refill -- and drained them.)
    if (wfill(c) <= lo && lo < 1e6) { w = max(H, m); }
  }
  if (it.cur == 0u) { wb[c].y = w; } else { wb[c].x = w; }
}

// ---- 6. drainage: where the water goes, how much comes through. D-INFINITY (Tarboton 1997): the steepest way down is
// found over the 8 triangular facets round the cell (the cell, a side neighbour, the corner beside it), in any direction,
// and the water is split between the two neighbours that bracket it -- a river is not pulled onto the grid's 8 directions.
// flow.z: the facet (0-7) + the share going to its side neighbour (the rest to its corner); -1: nowhere (an outlet)
@compute @workgroup_size(8, 8) fn route(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  if (isEdge(g.x, g.y)) { flow[c].z = -1.0; flow[c].w = 0.0; return; }
  let st = steepest(g.x, g.y, true);
  var z = st.y;
  // (a CHANNEL is one thread: its water goes all to the side or all to the corner, which by a fixed draw per cell weighted
  //  by the share (Rho8) -- the same direction on average, but not smeared over the valley floor a little more each cell,
  //  a river three cells wide and shallow, cutting nothing. Sheet flow on a hillside spreads, as it does.)
  if (z >= 0.0 && qcur(c).x > p.Qc) {
    let u = fract(sin(f32(c) * 12.9898 + p.seed * 78.233) * 43758.5453);
    z = floor(z) + select(0.0, 0.9999, u < fract(z));
  }
  flow[c].z = z;
  flow[c].w = st.x;
}
// the share of j's water that comes to its neighbour in direction k (from j)
fn shareTo(j: u32, k: u32) -> f32 { return facetShare(flow[j].z, k); }
// the discharge and the sediment flux, relaxed from last step's: Q = rain on the cell + the shares flowing in; the
// sediment it passes on is what came in, plus what the river cuts here, less what settles (SPACE / Davy-Lague)
// (a channel only where the drainage is large enough to hold one: below Qc the land is hillslope)
fn stream(Q: f32) -> f32 { return max(0.0, sqrt(Q) - sqrt(p.Qc)); }
fn cutRate(c: u32, n: u32, Q: f32) -> f32 { return p.K * p.mat[topMat(c, n)].x * soft(c) * stream(Q) * flow[c].w; }
@compute @workgroup_size(8, 8) fn accum(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  let H = col[c].z; let W = wsurf(c); let A = p.dx * p.dx;
  var Qin = 0.0; var Sin = 0.0;
  for (var k = 0u; k < 8u; k++) {
    let j = nbr(g.x, g.y, k); if (j < 0) { continue; }
    let jj = u32(j);
    let f = shareTo(jj, (k + 4u) % 8u);
    if (f > 0.0) { let q = qcur(jj); Qin += f * q.x; Sin += f * q.y; }
  }
  let inl = inflow(g.x, g.y); Sin += inl.y;
  let Q = rainAt(c) * A + Qin + inl.x;
  // (in a lake the sediment settles, but only up to the water's surface a step: the rest goes on across the lake --
  //  a delta grows out into it, it does not stand up out of the water at the river's mouth)
  var E = 0.0; var D = min(Sin / A, max(W - H, 0.0) / p.dt);
  if (!(W - H > p.lakeMin || isEdge(g.x, g.y))) {
    E = cutRate(c, u32(col[c].y), Q);
    D = min(p.V * Sin / Q, Sin / A + E);
  }
  let So = max(0.0, Sin + (E - D) * A);
  if (it.a == 0u) { acc[c] = vec4<f32>(acc[c].xy, Q, So); } else { acc[c] = vec4<f32>(Q, So, acc[c].zw); }
  flow[c].x = Sin;
}
// ---- 7. rivers act: cut down through the layers, lay the sediment that settles; a lake takes all that comes in
// What a cell's river would cut (cutA) is spread over it and its neighbours (an isotropic Gaussian on the grid, 4:2:1):
// the smallest thing a river cuts is a few cells across. Cut a cell at a time, a gully head was a one-cell pit whose side
// neighbours, 100 m off, fell towards it 41 % steeper than its diagonal ones, 141 m off -- so heads grew along the grid's
// axes and side canyons ran dead straight along them. Now a head is a rounded hollow, and where the water comes from
// decides where it grows.
// WATERFALLS: a channel steeper than fallS leaves its bed at the lip -- the water falls free, the lip wears only as a
// reach at fallS would, and the rest of the fall's power (times "plunge") scours a POOL at its foot (sent to the cells
// it falls to: out8[c*8+1]). Where the lip is hard and what lies under it soft -- a basalt or limestone cap on sandstone
// -- the pool undercuts it, the lip breaks off (it slides when it stands higher than its rock holds) and the fall
// steps back upstream, still a fall: Niagara. In one rock a fall steep enough keeps itself; a gentler one wears down
// into rapids. Hanging valleys make them too: a trunk river cuts down faster than its small side streams.
@compute @workgroup_size(8, 8) fn cutA(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  var pot = 0.0; var pool = 0.0;
  if (!isEdge(g.x, g.y) && wsurf(c) - col[c].z <= p.lakeMin) {
    let Q = qcur(c).x; let S = flow[c].w; let sp = p.K * stream(Q) * p.dt;
    if (p.plunge > 0.0 && S > p.fallS && Q > p.Qc) { pot = sp * p.fallS; pool = sp * (S - p.fallS) * p.plunge; }
    else { pot = sp * S; }
  }
  out8[c * 8u] = pot; out8[c * 8u + 1u] = pool;
}
@compute @workgroup_size(8, 8) fn erode(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  if (isEdge(g.x, g.y)) { return; }
  let H = col[c].z; let W = wsurf(c); let A = p.dx * p.dx;
  var n = u32(col[c].y);
  let Sin = flow[c].x; let Q = qcur(c).x; let S = flow[c].w;
  var dep = min(Sin * p.dt / A, W - H);
  // the pool under a fall: what the falls above send down here, and how far they fall to it
  var pool = 0.0; var drop = 0.0;
  for (var k = 0u; k < 8u; k++) {
    let j = nbr(g.x, g.y, k); if (j < 0) { continue; }
    let sh = shareTo(u32(j), (k + 4u) % 8u);
    if (sh > 0.0 && out8[u32(j) * 8u + 1u] > 0.0) { pool += sh * out8[u32(j) * 8u + 1u]; drop = max(drop, wsurf(u32(j)) - W); }
  }
  if (W - H <= p.lakeMin) {
    // (never deeper than half the drop to the next cell, in METRES: as potential in the top bed's terms, a few dm of
    //  loose sand on a knickpoint held the basalt under it to a tenth of its cutting)
    var pot = 0.25 * out8[c * 8u];
    for (var k = 0u; k < 8u; k++) { let j = nbr(g.x, g.y, k); if (j >= 0) { pot += select(0.0625, 0.125, OD[k] < 1.2) * out8[u32(j) * 8u]; } }
    let rem = erodeTop(c, &n, pot, 0.5 * S * p.dx);
    dep = min(p.V * Sin / Q, Sin / A + rem / p.dt) * p.dt;
  }
  if (pool > 0.0) {   // (the pool keeps itself clear, and deepens to half the fall's height at most)
    erodeTop(c, &n, pool, max(0.0, H - W + 0.5 * drop));
    dep = 0.0;
  }
  addLayer(c, &n, SED, dep);
  setCol(c, n);
  // (dry land stays dry, the dry pass: a cell the river has just cut is its own water surface -- else the old surface stood over
  //  the new channel as a "lake" until the fill came down from the outlet to it, and a lake does not cut)
  if (W <= H && wcur(c) < 1e6) { aux[c].w = 1.0; }
}

// ---- the walls (the edge where it is no outlet): each the copy of its inner neighbour's column, water and drainage --
// the land goes on flat across the edge, nothing runs out over it
@compute @workgroup_size(8, 8) fn walls(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  if (!isEdge(g.x, g.y) || isOutlet(g.x, g.y)) { return; }
  let c = g.y * p.N + g.x;
  let ci = clamp(g.y, 1u, p.N - 2u) * p.N + clamp(g.x, 1u, p.N - 2u);
  col[c] = vec4<f32>(col[ci].xyz, 0.0);
  for (var k = 0u; k < p.L; k++) { lay[li(c, k)] = lay[li(ci, k)]; }
  wb[c] = wb[ci]; acc[c] = acc[ci];
}

// ---- tools: paint uplift (m/yr) into the land; brush.z < 0 clears it
@compute @workgroup_size(8, 8) fn paint(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= p.N || g.y >= p.N) { return; }
  let c = g.y * p.N + g.x;
  if (p.brush.z < 0.0) { aux[c].x = 0.0; return; }
  let x = (vec2<f32>(g.xy) + 0.5) * p.dx;
  let q = distance(x, p.brush.xy) / p.brush.z;
  aux[c].x += p.brush.w * exp(-q * q);
}
`;

// ---- THE VIEW: the grid upscaled -- bicubic, and the smaller waves added -- into the mesh's own grid -------------------
const VIEW_STRUCT = /* wgsl */`
struct V {
  viewProj: mat4x4<f32>,
  eye: vec4<f32>,
  sun: vec4<f32>,
  M: u32, mode: u32, cur: u32, acur: u32,
  exag: f32, size: f32, detail: f32, riverQ: f32,
  section: f32, contour: f32, seaView: f32, rel: f32,
  hLo: f32, hHi: f32, nOut: f32, pad1: f32,
  rough: array<vec4<f32>, 2>,
  mcol: array<vec4<f32>, 8>,
  outl: array<vec4<f32>, 4>,     // the outlets: x, y, radius in the mesh's 0..1
}
`;
export const VIEW_FLOATS = 16 + 4 + 4 + 4 + 4 + 4 + 4 + 8 + 32 + 16;   // (the packing: terrain_lab.js viewData)

export const UP = /* wgsl */`
${COMMON}
${VIEW_STRUCT}
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> col: array<vec4<f32>>;
@group(0) @binding(2) var<storage, read> lay: array<vec2<f32>>;
@group(0) @binding(3) var<storage, read> wb: array<vec2<f32>>;
@group(0) @binding(4) var<storage, read> acc: array<vec4<f32>>;
@group(0) @binding(5) var<storage, read_write> disp: array<vec4<f32>>;
@group(0) @binding(6) var<uniform> v: V;

fn cellAt(i: i32, j: i32) -> u32 { let n = i32(p.N) - 1; return u32(clamp(j, 0, n)) * p.N + u32(clamp(i, 0, n)); }
fn hAt(i: i32, j: i32) -> f32 { return col[cellAt(i, j)].z; }
fn wAt(i: i32, j: i32) -> f32 { let c = cellAt(i, j); let w = select(wb[c].x, wb[c].y, v.cur == 1u); return select(w, col[c].z, w > 1e6); }
fn qAt(i: i32, j: i32) -> f32 { let c = cellAt(i, j); return select(acc[c].x, acc[c].z, v.acur == 1u); }
fn cr(a: f32, b: f32, c: f32, d: f32, t: f32) -> f32 {        // Catmull-Rom
  return b + 0.5 * t * (c - a + t * (2.0 * a - 5.0 * b + 4.0 * c - d + t * (3.0 * (b - c) + d - a)));
}
fn bicubicH(gx: vec2<f32>) -> f32 {
  let b = floor(gx); let f = gx - b; let i = i32(b.x); let j = i32(b.y);
  var r: array<f32, 4>;
  for (var k = 0; k < 4; k++) { r[k] = cr(hAt(i - 1, j + k - 1), hAt(i, j + k - 1), hAt(i + 1, j + k - 1), hAt(i + 2, j + k - 1), f.x); }
  return cr(r[0], r[1], r[2], r[3], f.y);
}
// the discharge, smoothed (a cubic B-spline of its log): a channel is one cell wide and steps between side and corner
// cells, and interpolated it was drawn as a staircase -- smoothed, as a ribbon along its course
fn bspl(t: f32) -> vec4<f32> {
  let s = 1.0 - t;
  return vec4<f32>(s * s * s, 3.0 * t * t * t - 6.0 * t * t + 4.0, -3.0 * t * t * t + 3.0 * t * t + 3.0 * t + 1.0, t * t * t) / 6.0;
}
fn smoothQ(gx: vec2<f32>) -> f32 {
  let b = floor(gx); let f = gx - b; let i = i32(b.x); let j = i32(b.y);
  let wx = bspl(f.x); let wy = bspl(f.y);
  var s = 0.0;
  for (var jj = 0; jj < 4; jj++) { for (var ii = 0; ii < 4; ii++) {
    s += wx[ii] * wy[jj] * log(max(qAt(i + ii - 1, j + jj - 1), 1.0));
  } }
  return exp(s);
}
// the water surface from the WET cells only (a lake's, the sea's: flat), none where no cell around holds water -- the
// shore is then where the ground rises through it, not where the cells' depth happens to pass a threshold
fn waterAt(gx: vec2<f32>) -> f32 {
  let b = floor(gx); let f = gx - b; let i = i32(b.x); let j = i32(b.y);
  var sw = 0.0; var s = 0.0;
  for (var k = 0; k < 4; k++) {
    let ii = i + k % 2; let jj = j + k / 2;
    let wk = select(1.0 - f.x, f.x, k % 2 == 1) * select(1.0 - f.y, f.y, k / 2 == 1);
    if (wAt(ii, jj) - hAt(ii, jj) > p.lakeMin) { sw += wk; s += wk * wAt(ii, jj); }
  }
  if (sw <= 0.0) { return -1e9; }
  return s / sw;
}
// what shows at the surface: soil thinner than a metre shows the rock under it
fn surfaceMat(c: u32) -> u32 {
  let n = u32(col[c].y);
  if (n == 0u) { return GRANITE; }
  let t = lay[c * p.L + n - 1u];
  if (u32(t.y) == SED && t.x < 1.0) { if (n >= 2u) { return u32(lay[c * p.L + n - 2u].y); } return GRANITE; }
  return u32(t.y);
}
// what is there at height h in cell c: the bed h cuts (beds are near flat, so on a slope the bands then run along the
// surface, not in cell-sized steps as the cell's top bed did); above the column, its surface
fn matAt(c: u32, h: f32) -> u32 {
  let n = u32(col[c].y); var z = col[c].x; var m = GRANITE;
  if (h < z) { return GRANITE; }
  for (var k = 0u; k < n; k++) {
    let t = lay[c * p.L + k];
    if (h < z + t.x) { if (u32(t.y) == SED && t.x < 1.0 && k + 1u == n) { return m; } return u32(t.y); }
    m = u32(t.y); z += t.x;
  }
  return surfaceMat(c);
}
// the smaller waves: fractal gradient noise
fn fbm(x: vec2<f32>) -> f32 {
  var s = 0.0; var a = 0.5; var q = x;
  for (var o = 0; o < 5; o++) { s += a * gnoise(q, 0.0); q = q * 2.03 + vec2<f32>(17.3, 9.1); a *= 0.5; }
  return 0.4 * s;
}
@compute @workgroup_size(8, 8) fn up(@builtin(global_invocation_id) g: vec3<u32>) {
  if (g.x >= v.M || g.y >= v.M) { return; }
  let uv = vec2<f32>(g.xy) / f32(v.M - 1u);
  let gx = uv * f32(p.N - 1u);
  var h = bicubicH(gx);
  let q = smoothQ(gx);
  // water only where the cells hold it (a lake, the sea): on dry land the surface IS the ground, and the detail's
  // hollows must not fill
  let w = waterAt(gx);
  let ci = cellAt(i32(round(gx.x)), i32(round(gx.y)));
  let m = matAt(ci, h);
  let sx = bicubicH(gx + vec2<f32>(0.5, 0.0)) - bicubicH(gx - vec2<f32>(0.5, 0.0));
  let sy = bicubicH(gx + vec2<f32>(0.0, 0.5)) - bicubicH(gx - vec2<f32>(0.0, 0.5));
  let slope = length(vec2<f32>(sx, sy)) / p.dx;
  let rough = v.rough[m / 4u][m % 4u];
  let wp = gx * p.dx;
  h += fbm(wp / (2.0 * p.dx)) * rough * (0.25 + min(slope * 2.0, 1.75)) * v.detail;
  // white water: a river over ground steeper than a fall's (a quarter in the material's fraction: flat-interpolated, read
  // back by the drawing)
  let foam = select(0.0, 0.25, log(max(q, 1.0)) / 2.302585 > v.riverQ - 0.5 && slope > p.fallS);
  disp[g.y * v.M + g.x] = vec4<f32>(h, w, f32(m) + foam, q);
}
`;

// ---- DRAWING: the mesh (one vertex a display cell), coloured by height, material or discharge; water on it ---------------
export const DRAW = /* wgsl */`
${VIEW_STRUCT}
@group(0) @binding(0) var<uniform> v: V;
@group(0) @binding(1) var<storage, read> disp: array<vec4<f32>>;

struct O {
  @builtin(position) pos: vec4<f32>,
  @location(0) h: f32, @location(1) depth: f32, @location(2) @interpolate(flat) mat: u32, @location(3) q: f32,
  @location(4) nrm: vec3<f32>, @location(5) wpos: vec3<f32>, @location(6) grid: vec2<f32>, @location(7) foam: f32,
}
fn surf(i: i32, j: i32) -> f32 {
  let M = i32(v.M) - 1;
  let d = disp[u32(clamp(j, 0, M)) * v.M + u32(clamp(i, 0, M))];
  return max(d.x, d.y);
}
@vertex fn vs(@builtin(vertex_index) vi: u32) -> O {
  let i = i32(vi % v.M); let j = i32(vi / v.M);
  let d = disp[vi];
  let s = max(d.x, d.y);
  let cell = v.size / f32(v.M - 1u);
  let nrm = normalize(vec3<f32>((surf(i - 1, j) - surf(i + 1, j)) * v.exag, 2.0 * cell, (surf(i, j - 1) - surf(i, j + 1)) * v.exag));
  let uv = vec2<f32>(f32(i), f32(j)) / f32(v.M - 1u);
  let wpos = vec3<f32>((uv.x - 0.5) * v.size, s * v.exag, (uv.y - 0.5) * v.size);
  var o: O;
  o.pos = v.viewProj * vec4<f32>(wpos, 1.0);
  o.h = d.x; o.depth = d.y - d.x; o.mat = u32(d.z + 0.5); o.q = d.w; o.nrm = nrm; o.wpos = wpos; o.grid = uv;
  o.foam = fract(d.z + 0.5) - 0.5;
  return o;
}
// land by height: sea-level green through ochre and rock grey to snow
fn hypso(h: f32) -> vec3<f32> {
  let k = array<vec4<f32>, 7>(
    vec4<f32>(-200.0, 0.55, 0.62, 0.45), vec4<f32>(0.0, 0.40, 0.58, 0.32), vec4<f32>(300.0, 0.52, 0.64, 0.34),
    vec4<f32>(800.0, 0.76, 0.70, 0.44), vec4<f32>(1500.0, 0.62, 0.48, 0.34), vec4<f32>(2600.0, 0.58, 0.56, 0.55),
    vec4<f32>(3600.0, 0.96, 0.96, 0.98));
  var c = k[0].yzw;
  for (var i = 0; i < 6; i++) {
    let a = k[i]; let b = k[i + 1];
    if (h >= a.x) { c = mix(a.yzw, b.yzw, clamp((h - a.x) / (b.x - a.x), 0.0, 1.0)); }
  }
  return c;
}
@fragment fn fs(o: O) -> @location(0) vec4<f32> {
  let n = normalize(o.nrm);
  var base: vec3<f32>;
  if (v.mode == 1u) { base = v.mcol[min(o.mat, 7u)].xyz; }
  else if (v.mode == 2u) { let t = clamp((log(max(o.q, 1.0)) / 2.302585 - 5.0) / 4.0, 0.0, 1.0); base = mix(vec3<f32>(0.9, 0.88, 0.8), vec3<f32>(0.05, 0.2, 0.7), t); }
  // (the land's own range, spread over as much of the scale as its relief deserves: a low land stays green and ochre, only
  //  real mountains reach the snow)
  else if (v.rel > 0.5) { let span = min(3600.0, 900.0 + 1.1 * (v.hHi - v.hLo)); base = hypso(clamp((o.h - v.hLo) / max(v.hHi - v.hLo, 1.0), 0.0, 1.0) * span); }
  else { base = hypso(o.h - v.seaView); }
  if (v.contour > 0.0 && v.mode == 0u) {                     // contours every 100 m
    let f = fract(o.h / 100.0); let w = fwidth(o.h / 100.0);
    base *= 1.0 - 0.25 * (1.0 - smoothstep(0.0, 1.5 * w, min(f, 1.0 - f)));
  }
  // rivers: where the discharge is large, a river too narrow for the cell tints it
  let rq = log(max(o.q, 1.0)) / 2.302585;
  if (o.depth <= 0.05 && v.mode != 2u) { base = mix(base, vec3<f32>(0.18, 0.42, 0.72), smoothstep(v.riverQ - 0.9, v.riverQ - 0.1, rq) * 0.85); }   // (smoothed, a channel a cell wide loses about a decade)
  if (o.foam > 0.1 && o.depth <= 0.05 && v.mode != 2u) { base = mix(base, vec3<f32>(0.93, 0.96, 0.98), 0.85); }   // a fall
  if (o.depth > 0.05) {                                      // a lake, the sea: its surface, darker the deeper
    base = mix(vec3<f32>(0.36, 0.62, 0.70), vec3<f32>(0.07, 0.2, 0.4), clamp(o.depth / 120.0, 0.0, 1.0));
  }
  let lit = 0.38 + 0.72 * max(dot(n, normalize(v.sun.xyz)), 0.0);
  var c = base * lit;
  if (abs(o.grid.y - v.section) < 0.0015) { c = mix(c, vec3<f32>(0.95, 0.2, 0.15), 0.8); }   // the cross-section's line
  for (var k = 0u; k < u32(v.nOut); k++) {                   // the outlets: a ring where the land drains out
    let d = distance(o.grid, v.outl[k].xy) / v.outl[k].z;
    if (d > 0.75 && d < 1.0) { c = mix(c, vec3<f32>(0.1, 0.85, 0.9), 0.85); }
  }
  let fog = clamp(distance(o.wpos, v.eye.xyz) / (v.size * 3.0), 0.0, 0.5);
  return vec4<f32>(mix(c, vec3<f32>(0.62, 0.7, 0.78), fog), 1.0);
}
`;
