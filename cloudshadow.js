// CLOUD SHADOWS: on a sunny day soft dark patches slide over the land with the clouds' drift -- big and few under a few
// clouds, more of them as the sky fills, none under a grey sky or by night (no sun to cast them). One function, shared
// by everything that lies on the land so they darken together: the ground (index.html GroundMaterial), the roads
// (paths.js), the buildings (architecture.js: its materials, finishes and plain stone) and the trees' leaves (foliage.js) -- two octaves of smooth noise over the world's x/z, scrolled
// along +x (the way the clouds drift, ~1.5 m/s). index.html sets the uniforms every frame.
//
//   CLOUD.amount  0 none .. 1 the darkest a shadow gets (CLOUD_SHADOW.dark)
//   CLOUD.cover   0 a few small patches .. 1 most of the land
//   rgb.mul(landShade())   // a node: the shadow where the fragment is (its world position)
import * as THREE from "three";
import { uniform, wgslFn, positionWorld } from "three/tsl";
import { sunShade } from "./sunshadow.js";

export const CLOUD_SHADOW = { dark: .36, drift: 1.5 };
export const CLOUD = { amount: uniform(0), cover: uniform(.4), t: uniform(0) };
// how WET the world is after rain, 0 dry .. 1 soaked (index.html: a minute's rain soaks, four minutes dry it) -- the roads'
// puddles (paths.js ROAD_WET.wet is this same uniform) and the buildings' darkened roofs and walls (archmat.js)
export const WET = uniform(0);

// smooth value noise over a plane, 0..1 (also the puddles' hollows: paths.js)
export const valueNoise = wgslFn(`fn valueNoise2(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let u = f * f * (3.0 - 2.0 * f);
    let k = vec2<f32>(127.1, 311.7);
    let v = fract(sin(vec4<f32>(dot(i, k), dot(i + vec2<f32>(1.0, 0.0), k), dot(i + vec2<f32>(0.0, 1.0), k), dot(i + vec2<f32>(1.0, 1.0), k))) * 43758.5);
    return mix(mix(v.x, v.y, u.x), mix(v.z, v.w, u.x), u.y);
  }`);

// PUDDLES after rain: water standing in the hollows of open ground -- a road's (paths.js, deepest in its ruts), a
// paved square's (archmat.js: a finish rule's `puddles`) -- the wetter (WET), the higher it stands; the
// sky in it (PUDDLE.sky: the horizon's colour), the more the flatter you look across it, and while it rains (`rain`: the
// share of cells with a drop) the drops' rings spreading on it. One function for all of them: they fill and dry
// together. index.html sets PUDDLE every frame (as paths.js ROAD_WET, whose sky, t and rain these are).
//   col = puddleShade(col, wp, bias, mask, WET, PUDDLE.sky, PUDDLE.t, PUDDLE.rain, cam)   // bias: a deeper hollow there (ruts); mask: where water may stand
export const PUDDLE = { sky: uniform(new THREE.Color(.7, .75, .8)), t: uniform(0), rain: uniform(0) };
export const puddleShade = wgslFn(`
  fn puddleShade(col: vec3<f32>, wp: vec3<f32>, bias: f32, mask: f32, wet: f32, sky: vec3<f32>, t: f32, rain: f32, cam: vec3<f32>) -> vec3<f32> {
    if (wet < 0.001) { return col; }
    // the hollows: a smooth lumpiness over the ground; the wetter, the higher the water stands in them
    let low = valueNoise2(wp.xz * 0.45) * 0.7 + valueNoise2(wp.xz * 1.3 + 17.0) * 0.3 + bias;
    let lev = 1.05 - wet * 0.42;
    let pud = smoothstep(lev, lev + 0.05, low) * mask;
    if (pud < 0.001) { return col; }
    // the sky in it -- the more, the flatter you look across it (a puddle at your feet shows the mud) -- over the dark
    // ground beneath, a darker rim of wet earth round it
    let fres = pow(1.0 - abs(normalize(wp - cam).y), 3.0);
    var w = mix(col * 0.45, sky * 0.8, 0.25 + 0.6 * fres);
    w = w * (0.8 + 0.2 * smoothstep(0.0, 0.6, pud));
    // a drop's rings: one a cell at a time, spreading and fading, each cell on its own clock
    let cell = floor(wp.xz * 1.7);
    let k = vec2<f32>(127.1, 311.7);
    let h = fract(sin(dot(cell + 5.0, k)) * 43758.5);
    let ph = fract(t * 0.9 + h);
    let dp = vec2<f32>(0.3 + 0.4 * fract(sin(dot(cell + 9.0, k)) * 43758.5), 0.3 + 0.4 * fract(sin(dot(cell + 13.0, k)) * 43758.5));
    let rr = length(fract(wp.xz * 1.7) - dp);
    let ring = smoothstep(0.05, 0.0, abs(rr - ph * 0.45)) * (1.0 - ph) * step(h, rain);
    w = w + vec3<f32>(0.22) * ring;
    return mix(col, w, pud);
  }
`, [valueNoise]);

export const cloudShade = wgslFn(`
  fn cloudShade(p: vec2<f32>, t: f32, amount: f32, cover: f32) -> f32 {
    if (amount < 0.001) { return 1.0; }
    let q = p + vec2<f32>(-t * ${CLOUD_SHADOW.drift.toFixed(2)}, 0.0);
    let n = valueNoise2(q * 0.0075) * 0.68 + valueNoise2(q * 0.021 + vec2<f32>(31.0, 17.0)) * 0.32;
    let lo = 0.7 - cover * 0.2;   // (the noise's sum clusters round .5: about a sixth of the land in shade under a few clouds, nearly half under many)
    return 1.0 - ${CLOUD_SHADOW.dark.toFixed(2)} * amount * smoothstep(lo, lo + 0.1, n);
  }
`, [valueNoise]);

// THE MEADOWS' PATCHES: the lawn is never one green -- broad drifts a little drier and yellower, others lusher and
// deeper, at two scales (~60 m and ~20 m), gentle enough that it reads as grass, not paint (index.html GroundMaterial)
export const meadowPatches = wgslFn(`
  fn meadowPatches(p: vec2<f32>) -> vec3<f32> {
    let m = valueNoise2(p * 0.017) * 0.65 + valueNoise2(p * 0.052 + vec2<f32>(7.0, 3.0)) * 0.35;
    return mix(vec3<f32>(0.86, 0.95, 0.82), vec3<f32>(1.1, 1.05, 0.88), smoothstep(0.3, 0.72, m));
  }
`, [valueNoise]);

// (and the sun's own shadows -- the buildings', baked once: sunshadow.js -- on everything that lies on the land)
export const landShade = () => cloudShade({ p: positionWorld.xz, t: CLOUD.t, amount: CLOUD.amount, cover: CLOUD.cover }).mul(sunShade());
