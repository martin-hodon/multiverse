// THE SKY: a dome round the camera, its colour from the zenith down to the horizon, with the sun in it -- high and
// pale by day, sinking in the west at dusk with the sky round it on fire, gone below the hills at night. One value
// drives it all: `dark`, 0 full day .. 1 deep night (index.html eases it over the dusk, or runs it round a day).
// The fog takes the horizon's colour, so the far land melts into the sky whatever the hour; and the frame's tint --
// the multiply pass that darkens the whole picture at night -- passes through warm evening light on the way.
//
//   const sky = createSky(scene, { radius })
//   sky.update(camera, dark, overcast, bow, { aurora, t }) -> { horizon, tint, sunDir, sunCol, cloud }   (the fog colour, the frame's multiply colour, the sun for the water)
//
// A RAINBOW (bow 0..1, index.html: light rain, or the sun coming out after rain) stands where a real one does: a ring
// 42 degrees round the point straight opposite the sun -- low and flat at noon, a tall arch toward evening -- red
// outside, violet in; the faint second bow at 51 degrees with its colours the other way round, the sky inside the first
// a shade brighter and the band between them (Alexander's) a shade darker. In the dome's own shader: no extra draw.
import * as THREE from "three";
import { uniform, vec3, float, positionWorld, cameraPosition, smoothstep, mix, pow, max, dot, normalize, clamp, acos, fract, abs, wgslFn } from "three/tsl";

const ridges = wgslFn(`
  fn ridges(v: vec3<f32>, up: f32, sky: vec3<f32>, hor: vec3<f32>, zen: vec3<f32>) -> vec3<f32> {
    let a = atan2(v.z, v.x);
    let far = 0.072 + 0.026 * sin(a * 3.0 + 0.4) + 0.014 * sin(a * 7.0 + 2.1) + 0.007 * sin(a * 17.0 + 0.7) + 0.0035 * sin(a * 41.0 + 1.9);
    let near = 0.046 + 0.018 * sin(a * 2.0 + 2.6) + 0.01 * sin(a * 5.0 + 0.3) + 0.005 * sin(a * 13.0 + 1.1) + 0.0025 * sin(a * 37.0 + 2.8);
    let farCol = mix(hor, zen * 0.75, 0.32);
    let nearCol = mix(hor, zen * 0.55, 0.55);
    var col = sky;
    col = mix(col, farCol, smoothstep(far + 0.0015, far - 0.0015, up));
    col = mix(col, nearCol, smoothstep(near + 0.0015, near - 0.0015, up));
    // below the horizon (only ever seen past the land's edge, from high up): the haze over the far plain, the fog's colour
    return mix(col, hor * 0.97, smoothstep(0.004, -0.03, up));
  }
`);

// value noise on a direction (the Milky Way's mottling, the aurora's rays)
const vnoise3 = wgslFn(`
  fn vnoise3(p: vec3<f32>) -> f32 {
    let i = floor(p); let f = fract(p); let u = f * f * (3.0 - 2.0 * f);
    let n = i.x + i.y * 57.0 + i.z * 113.0;
    let h = fract(sin(vec4<f32>(n, n + 1.0, n + 57.0, n + 58.0)) * 43758.5453);
    let g = fract(sin(vec4<f32>(n + 113.0, n + 114.0, n + 170.0, n + 171.0)) * 43758.5453);
    let a = mix(mix(h.x, h.y, u.x), mix(h.z, h.w, u.x), u.y);
    let b = mix(mix(g.x, g.y, u.x), mix(g.z, g.w, u.x), u.y);
    return mix(a, b, u.z);
  }
`);

// THE MILKY WAY: a band of faint light along a great circle, mottled and split by dark rifts (value-noise fbm on the
// direction), brightest toward its core; only as dark as the stars are out
const milky = wgslFn(`
  fn milky(v: vec3<f32>, k: f32) -> vec3<f32> {
    if (k < 0.01) { return vec3<f32>(0.0); }
    let n = normalize(vec3<f32>(0.32, 0.5, 0.8));
    let d = dot(v, n);
    let band = exp(-d * d * 42.0);
    let core = exp(-dot(v - normalize(vec3<f32>(-0.75, 0.25, 0.45)), v - normalize(vec3<f32>(-0.75, 0.25, 0.45))) * 1.6);
    var f = 0.0; var a = 0.5; var p = v * 11.0;
    for (var i: i32 = 0; i < 5; i = i + 1) { f = f + a * vnoise3(p); p = p * 2.03 + vec3<f32>(1.7, 9.2, 3.1); a = a * 0.5; }
    let rift = smoothstep(0.05, 0.0, abs(d + 0.03 * (f - 0.5))) * 0.55;   // the dark lane down its middle
    let glow = band * (0.3 + 0.7 * core) * smoothstep(0.3, 0.9, f) * (1.0 - rift);
    // ...and its dust of stars too faint to tell apart, thickest where the band is: a fine grain of points
    let cell = floor(v * 700.0);
    let dust = step(0.992 - 0.03 * band, fract(sin(dot(cell, vec3<f32>(12.9898, 78.233, 37.719))) * 43758.5453)) * (0.25 + band);
    return vec3<f32>(0.62, 0.66, 0.82) * glow * 0.8 * k + vec3<f32>(0.85, 0.88, 1.0) * dust * 0.55 * k;   // (bright here: the night's tint pass takes three quarters of it)
  }
`, [vnoise3]);

// THE NORTHERN LIGHTS (some clear nights: index.html AURORA): curtains low over the northern sky (-z) -- a wavy foot
// that folds and drifts, fine rays flickering along it, green at the foot going violet up its height, and a faint
// red haze above; two curtains, the far one fainter and higher. Bright here, like the Milky Way: the night's tint takes
// most of it.
const curtain = wgslFn(`
  fn curtain(a: f32, e: f32, t: f32, o: f32) -> vec3<f32> {
    let fold = 0.09 * sin(a * 3.0 + t * 0.05 + o + 1.6 * sin(a * 1.7 - t * 0.035 + o)) + 0.03 * sin(a * 9.0 - t * 0.1 + o * 2.0);
    let h = e - (0.09 + o * 0.07 + fold);
    let up = max(h, 0.0);
    let body = smoothstep(-0.01, 0.012, h) * (exp(-up / (0.1 + o * 0.04)) + 0.6 * exp(-up / 0.025));   // (the bright lower rim)
    let segs = smoothstep(0.25, 0.65, vnoise3(vec3<f32>(a * 2.5 - t * 0.03, o * 4.0, t * 0.02)));   // (bright stretches and gaps)
    let rays = 0.3 + 0.7 * vnoise3(vec3<f32>(a * 55.0 + fold * 80.0, e * 3.0 + t * 0.4, o * 7.0));
    let col = mix(vec3<f32>(0.22, 1.0, 0.5), vec3<f32>(0.5, 0.25, 0.8) * 0.6, smoothstep(0.06, 0.35, h));
    return col * body * rays * segs + vec3<f32>(0.6, 0.18, 0.35) * smoothstep(0.0, 0.12, h) * exp(-up / 0.3) * 0.04 * segs;
  }
`, [vnoise3]);
const aurora = wgslFn(`
  fn aurora(v: vec3<f32>, t: f32, k: f32) -> vec3<f32> {
    if (k < 0.01 || v.y < -0.02) { return vec3<f32>(0.0); }
    let a = atan2(v.x, -v.z);
    let north = smoothstep(1.8, 0.5, abs(a));
    if (north <= 0.0) { return vec3<f32>(0.0); }
    let e = asin(clamp(v.y, 0.0, 1.0));
    return (curtain(a, e, t, 0.0) + curtain(a + 0.4, e, t * 0.8, 1.0) * 0.5) * north * k * 2.8;
  }
`, [curtain]);

// SUNBEAMS (crepuscular rays) round a low sun: bands of light and of cloud-shadow fanning out of it across its glow,
// drifting slowly -- by the angle round the sun, a sum of a few waves; 1 is no change, the bands brighten and darken
const sunRays = wgslFn(`
  fn sunRays(v: vec3<f32>, dir: vec3<f32>, t: f32) -> f32 {
    let side = normalize(cross(dir, vec3<f32>(0.0, 1.0, 0.0)));
    let up = cross(side, dir);
    let a = atan2(dot(v, up), dot(v, side));
    let w = sin(a * 9.0 + t * 0.03) * 0.5 + sin(a * 23.0 - t * 0.05 + 1.3) * 0.3 + sin(a * 41.0 + t * 0.02 + 4.1) * 0.2;
    return 1.0 + smoothstep(-0.45, 0.75, w) * 0.6 - 0.25;
  }
`);

// a hue from violet (0) to red (1): the rainbow's bands, a soap bubble's film (bubbles.js)
export const spectrum = (t) => clamp(abs(fract(t.oneMinus().mul(.75).add(vec3(1, 2 / 3, 1 / 3))).mul(6).sub(3)).sub(1), 0, 1);

// the hours of the sky, by `dark`: the zenith, the horizon, the sun's glow, the frame's tint
const KEYS = [
  { at: 0,    zen: [.50, .69, .87], hor: [.81, .88, .91], sun: [1.0, .97, .88], tint: [1, 1, 1],         cloud: [1, 1, 1] },
  { at: .22,  zen: [.47, .62, .82], hor: [.93, .86, .76], sun: [1.0, .86, .60], tint: [1, .95, .88],      cloud: [1, .96, .9] },
  { at: .38,  zen: [.33, .42, .68], hor: [.98, .62, .40], sun: [1.0, .55, .25], tint: [1, .80, .66],      cloud: [1, .78, .66] },
  { at: .55,  zen: [.17, .19, .40], hor: [.55, .33, .42], sun: [.85, .30, .22], tint: [.66, .55, .66],    cloud: [.8, .58, .66] },
  { at: .75,  zen: [.06, .08, .19], hor: [.17, .15, .27], sun: [.30, .14, .18], tint: [.30, .31, .46],    cloud: [.5, .48, .6] },
  { at: 1,    zen: [.025, .04, .10], hor: [.063, .09, .157], sun: [.06, .06, .12], tint: [.16, .19, .33], cloud: [.36, .38, .5] },   // (the tint works on linear colour: .16 shows as ~.44 -- moonlit, dark enough for a lamp to tell)
];
export const SKY = { keys: KEYS, sunAz: -.35 };   // the sun's bearing: a little south of west (radians from -x toward +z)

const at = (dark, k) => {
  let i = 0; while (i < KEYS.length - 2 && dark > KEYS[i + 1].at) i++;
  const a = KEYS[i], b = KEYS[i + 1], f = Math.min(1, Math.max(0, (dark - a.at) / (b.at - a.at))), s = f * f * (3 - 2 * f);
  return a[k].map((v, j) => v + (b[k][j] - v) * s);
};

export function createSky(scene, { radius = 1500 } = {}) {
  const U = { zen: uniform(new THREE.Color()), hor: uniform(new THREE.Color()), sun: uniform(new THREE.Color()),
              dir: uniform(new THREE.Vector3(-1, .6, 0)), disc: uniform(1), glow: uniform(.2), stars: uniform(0), bow: uniform(0), aurora: uniform(0), t: uniform(0), rays: uniform(0) };
  // (drawn in the transparent pass, first of it: after every opaque thing, so it fills only the pixels nothing covers,
  // and the grass mask and the occluders -- which take opaque meshes only -- never see it)
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.BackSide, depthWrite: false, fog: false, transparent: true });
  const v = normalize(positionWorld.sub(cameraPosition));
  const up = clamp(v.y, -1, 1);
  // zenith to horizon over the upper half (most of the change low down, as the real sky does); below the horizon
  // the horizon's colour, darkened a little -- it is only ever seen past the edge of the land
  const grad = mix(U.hor, U.zen, pow(max(up, 0), .55)).mul(mix(float(.85), float(1), smoothstep(-.2, 0, up)));
  const toSun = max(dot(v, U.dir), 0);
  // the sun: its disc, a tight corona, and the wide glow it lights the sky with (strongest along the horizon)
  const disc = smoothstep(.99955, .99975, toSun).mul(U.disc);
  const corona = pow(toSun, 600).mul(.6).add(pow(toSun, 60).mul(.25)).mul(U.disc);
  const rays = sunRays({ v, dir: U.dir, t: U.t }).sub(1).mul(U.rays).add(1);   // (at sunset only: U.rays)
  const wide = pow(toSun, 6).mul(U.glow).mul(smoothstep(.75, 0, up.abs()).mul(.7).add(.3)).mul(rays);
  const lit = grad.add(U.sun.mul(wide.add(corona))).add(vec3(1, .98, .92).mul(disc)).add(milky({ v, k: U.stars })).add(aurora({ v, t: U.t, k: U.aurora }));
  // the rainbow: by its angle from the anti-solar point; a hue from violet (0) to red (1) across each band
  const ang = acos(clamp(dot(v, U.dir).negate(), -1, 1)).mul(57.2958);
  const hue = spectrum;
  const band = (t) => smoothstep(0, .25, t).mul(smoothstep(1, .75, t));
  const t1 = ang.sub(40.4).div(2), t2 = float(53.8).sub(ang).div(3.4);   // (the second: wider, and its red inside)
  const ground = smoothstep(-.01, .03, up);                                // (the land hides its feet)
  const arcs = hue(t1).mul(band(t1)).add(hue(t2).mul(band(t2)).mul(.38)).mul(U.bow).mul(ground).mul(.5);
  const shade = float(1).add(smoothstep(41, 34, ang).mul(.07)).sub(smoothstep(42.2, 43.5, ang).mul(smoothstep(50.6, 49.4, ang)).mul(.05)).sub(1).mul(U.bow).mul(ground).add(1);
  const sky = lit.mul(shade).add(arcs);
  // DISTANT MOUNTAINS round the edge of the world: two ridges, the far one paler (the air between), silhouettes
  // against the sunset, black under the stars -- a height by bearing, from whole-numbered waves so it closes round
  mat.colorNode = ridges({ v, up, sky, hor: U.hor, zen: U.zen });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(radius, 48, 24), mat);
  dome.frustumCulled = false;
  dome.renderOrder = -10;
  dome.name = "sky";
  dome.userData.noMerge = true;
  scene.add(dome);
  const horizon = new THREE.Color(), tint = new THREE.Color(), sunCol = new THREE.Color(), cloud = new THREE.Color(), _dim = new THREE.Color();
  return {
    dome,
    // overcast 0 clear .. 1 a grey sky (rain, snow: the weather's intensity): the blue and the sunset's colours give way
    // to grey, the sun goes behind the cloud, the light dims
    update(camera, dark, overcast = 0, bow = 0, { aurora: au = 0, t = 0 } = {}) {
      dome.position.copy(camera.position);
      const grey = (c, g) => c.map((v, j) => v + (g * [1, 1.02, 1.06][j] * (1 - dark * .85) - v) * overcast * .85);
      U.zen.value.setRGB(...grey(at(dark, "zen"), .58)); U.hor.value.setRGB(...grey(at(dark, "hor"), .72)); U.sun.value.setRGB(...at(dark, "sun"));
      // the sun's height: high by day, at the horizon at dusk (dark ~ .42), below it once night has come
      const el = THREE.MathUtils.lerp(.62, -.16, Math.min(1, Math.max(0, dark / .6)) ** 1.15);
      U.dir.value.set(-Math.cos(SKY.sunAz) * Math.cos(el), Math.sin(el), Math.sin(SKY.sunAz) * Math.cos(el)).normalize();
      U.disc.value = Math.max(0, Math.min(1, (el + .03) / .05)) * (1 - overcast);   // (the disc sets: gone 2 degrees under; or behind the cloud)
      U.glow.value = (.18 + .9 * Math.max(0, 1 - Math.abs(dark - .4) / .3)) * (1 - overcast * .8);   // (the glow is widest at sunset)
      horizon.setRGB(...grey(at(dark, "hor"), .72));
      tint.setRGB(...at(dark, "tint")).multiply(_dim.setRGB(1 - overcast * .3, 1 - overcast * .27, 1 - overcast * .2));   // (grey light: a third less under a heavy sky)
      sunCol.setRGB(...at(dark, "sun")).multiplyScalar(U.disc.value);   // (the sun as the water sees it: gone once it has set)
      U.bow.value = bow * Math.max(0, Math.min(1, (el + .02) / .08));   // (no sun, no bow)
      U.stars.value = Math.min(1, Math.max(0, (dark - .55) / .35)) * (1 - overcast);   // (the Milky Way: out with the stars, never under cloud)
      U.aurora.value = au * U.stars.value; U.t.value = t;
      U.rays.value = Math.max(0, 1 - Math.abs(dark - .38) / .14) * (1 - overcast);   // (the sunbeams: round sunset, in a clear sky)   // (the northern lights: only in the dark, never under cloud)
      cloud.setRGB(...at(dark, "cloud")).lerp(_dim.setRGB(.62, .64, .68), overcast * .7 * (1 - dark));   // (rain clouds: grey)   // (lit rose-gold by the low sun, slate by night -- over and above the frame's tint)
      return { horizon, tint, sunDir: U.dir.value, sunCol, cloud };
    },
  };
}
