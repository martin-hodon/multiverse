// Pattern tiles: the building materials' surface patterns (ashlar, brick,
// marble joints, roof tiles, checker floors, parquet, gothic bands,
// grooves, stars, ornament, scrollwork) and the ground's grass, CALCULATED
// at startup -- the same maths the shaders used to evaluate per pixel,
// rendered once over exactly one period of each pattern into a texture
// with mipmaps and anisotropic filtering. Per pixel the materials then read
// a filtered tile instead of evaluating hard-edged steps: thin joints fade
// instead of flickering at distance, a checker floor seen at a grazing angle
// no longer turns to moire, and the grass stops shimmering.
//
// A tile stores what the pattern DOES, not colours: R = the brightness
// factor k / 1.5, G = how much of the accent colour, B = how much of the dark
// counter-figure colour -- so one tile serves every colour of brick. Mixing
// and multiplying are linear in these, so averaging them down the mip chain
// is exactly averaging the coloured result. (The grass tile holds three
// masks instead: two fleck kinds and a patch value.)
//
// TEXTURES.on (?textures=0) switches it off: the materials then evaluate the
// same GLSL per pixel -- one source of truth, below. textures.html shows the
// tiles; build/textures.py saves them as PNG files into texture/ for looking
// at. Nothing loads those files: the tiles are always calculated.
import * as THREE from "three";
import { wgslFn, uniform, uv } from "three/tsl";
import { patternTile, patternHeight } from "./textures_wgsl.js";

export const TEXTURES = { on: true };
// PARALLAX on the baked architecture tiles (archMaterial): the relief baked in each tile's alpha, walked in `steps`
// layers up to the tile's `depth`, fading out by `far` metres (index.html sets it from config.json)
export const PARALLAX = { on: true, steps: 8, far: 15, shadowSteps: 4 };   // shadowSteps: the relief's own shadows (0: none)

// period: the metres one tile covers in (u, v) -- one exact repeat of the
// pattern (along the face, up) on walls, (x, z) on floors; size: texels a side;
// depth: metres of relief for parallax (0: flat)
export const TILES = {
  ashlar:   { id: 1, period: [1.6, 1.6], size: 512, depth: .03 },          // two courses of large stones
  brick:    { id: 2, period: [.56, .54], size: 512, depth: .018 },          // two courses of running bond
  grooves:  { id: 3, period: [1 / 6, 1 / 6], size: 128, depth: .03 },     // triglyph channels
  stars:    { id: 4, period: [.55, .55], size: 256 },          // a dot grid
  marble:   { id: 5, period: [2.3, 2.2], size: 1024, depth: .004 },         // hairline joints (the veining stays per pixel: smooth)
  tiles:    { id: 6, period: [.32, .72], size: 512, depth: .03 },          // scalloped roof tiles, two courses
  scroll:   { id: 7, period: [2 * Math.PI / .76, 2 * Math.PI / .76], size: 1024 },   // scrollwork, frequencies on one base so it repeats
  gothic:   { id: 8, period: [3, 6.5], size: 1024, depth: .06 },           // a bay by a string course
  checker:  { id: 9, period: [2.2, 2.2], size: 1024, depth: .004 },         // two marble squares each way
  ornament: { id: 10, period: [.85, .85], size: 512, depth: .02 },         // diamond lattice with bosses
  parquet:  { id: 11, period: [4.8, 2.24], size: 1024, depth: .003 },       // 4 lengths x 16 boards, each its own tone
  // GRASS: real blades, one tile per wind phase (bent left, upright, bent right) -- the ground blends the two
  // that bracket the wind where it stands, so the lawn BENDS instead of sliding. A blade is ~4mm wide, so the
  // tile has to be fine: 1m to 512 texels is .2cm each. It repeats every metre, which the broad tone patches
  // and the per-blade tone hide. Mipmapped like every other tile, which is what keeps blades from shimmering.
  grassL:   { id: 99, period: [1, 1], size: 512, phase: -1 },
  grass:    { id: 99, period: [1, 1], size: 512, phase: 0 },
  grassR:   { id: 99, period: [1, 1], size: 512, phase: 1 },
};

// The patterns. q: metres in the pattern's plane. Returns (k, accent, dark);
// the grass returns its masks.
// The patterns live in textures_wgsl.js now; the GLSL they were ported from is kept outside the repo as the
// parity reference (examples/webgpu_parity.html).

const targets = new Map();
// the tile's texture (baked by bakeTiles; materials may take it before that)
export function tileTexture(name) {
  let rt = targets.get(name);
  if (!rt) {
    const t = TILES[name];
    rt = new THREE.RenderTarget(t.size, t.size, {
      depthBuffer: false, generateMipmaps: true,
      minFilter: THREE.LinearMipmapLinearFilter, magFilter: t.nearest ? THREE.NearestFilter : THREE.LinearFilter,
      wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping,
    });
    targets.set(name, rt);
  }
  return rt.texture;
}

// The tile bake, in WGSL: one full-screen pass per tile, 3 x 3 samples a texel, mipmaps and anisotropy on.
// Colour carries the pattern, ALPHA its relief (patternHeight) for the parallax to walk down into.
// Call once after the renderer exists, before the first frame.
const bakeFn = wgslFn(`
  fn bakeTile(uv: vec2<f32>, pat: f32, period: vec2<f32>, texel: f32, phase: f32) -> vec4<f32> {
    var s = vec3<f32>(0.0);
    var h = 0.0;
    for (var i: i32 = 0; i < 3; i = i + 1) {
      for (var j: i32 = 0; j < 3; j = j + 1) {
        let q = (uv + (vec2<f32>(f32(i), f32(j)) - 1.0) * texel / 3.0) * period;
        s = s + patternTile(pat, q, phase);       // (the grass tiles are one pattern baked three times, leaning three ways)
        h = h + patternHeight(pat, q, period);
      }
    }
    s = s / 9.0;
    h = h / 9.0;
    if (pat > 98.5) { return vec4<f32>(s, 1.0); }          // grass: the blades' own three channels, no relief
    return vec4<f32>(s.x / 1.5, s.y, s.z, h);
  }
`, [patternTile, patternHeight]);

let baked = false;
export function bakeTiles(renderer) {
  if (baked) return;
  baked = true;
  const uPat = uniform(0), uPeriod = uniform(new THREE.Vector2()), uTexel = uniform(0), uPhase = uniform(0);
  const mat = new THREE.MeshBasicNodeMaterial({ depthTest: false, depthWrite: false, transparent: true });
  mat.blending = THREE.NoBlending;                         // the alpha IS data (the relief), never a blend factor
  const baked4 = bakeFn({ uv: uv(), pat: uPat, period: uPeriod, texel: uTexel, phase: uPhase });
  mat.colorNode = baked4.xyz;
  mat.opacityNode = baked4.w;
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat);
  quad.frustumCulled = false;
  const scene = new THREE.Scene(), cam = new THREE.OrthographicCamera(-1, 1, 1, -1, -1, 1);
  scene.add(quad);
  const prev = renderer.getRenderTarget(), aniso = renderer.getMaxAnisotropy();
  for (const [name, t] of Object.entries(TILES)) {
    const tex = tileTexture(name);
    tex.anisotropy = aniso;
    uPat.value = t.id;
    uPeriod.value.set(t.period[0], t.period[1]);
    uTexel.value = 1 / t.size;
    uPhase.value = t.phase ?? 0;
    renderer.setRenderTarget(targets.get(name));
    renderer.render(scene, cam);
  }
  renderer.setRenderTarget(prev);
  mat.dispose(); quad.geometry.dispose();
}

// a baked tile's texels (RGBA, BOTTOM row first) -- for textures.html and the PNG export
//   THE ROW ORDER IS THIS FUNCTION'S BUSINESS, not its callers'. WebGL's readPixels handed back the bottom
// row first; WebGPU's readback starts at the TOP (its render targets have their origin there), so on the
// switch every exported tile came out upside down. The rows are turned back here, once, so everything that
// reads a tile -- textures.html, the PNG export, the two engines' comparison page -- keeps the one order.
export async function readTile(renderer, name) {
  const rt = targets.get(name), n = TILES[name].size;
  const buf = await renderer.readRenderTargetPixelsAsync(rt, 0, 0, n, n);   // WebGPU reads back asynchronously
  for (let i = 3; i < buf.length; i += 4) buf[i] = 255;   // (the alpha holds the relief, for parallax: the picture shows opaque)
  const row = n * 4, tmp = buf.slice(0, row);
  for (let y = 0; y < n >> 1; y++) {
    const a = y * row, b = (n - 1 - y) * row;
    tmp.set(buf.subarray(a, a + row));
    buf.copyWithin(a, b, b + row);
    buf.set(tmp, b);
  }
  return buf;
}
