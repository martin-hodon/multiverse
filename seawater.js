// THE OPEN WATER'S LOOK (sea.js; docs/world.md "Open water"): the river's water family -- its reflection, its glitter,
// its Fresnel (index.html waterShade) -- with what open water has of its own:
//   DEPTH COLOUR  the bed showing through the shallows (green-turquoise over a sea's sand, brown-green in a lake),
//                 deepening to the open water's blue, and opaque where it is deep: no bed to see there
//   SWELL         long crests rolling in toward the shore (a sea's ~14 m apart, a lake's chop ~6 m)
//   CHOP          its own ripples, not the river's: four trains at odd angles and lengths over a slowly warped plane, the
//                 short ones fading out with distance -- so a wide stretch of it reads as water, not as tiles; the glitter
//                 (waterShade's `gp`) is read off the same warped, turned plane
//   SHORE FOAM    the swash at the waterline, and bands of surf rolling in over the last metre or so of depth -- where the
//                 shore shelves (a beach, a ledge), not at a cliff's foot
// Only a world with open water builds these nodes (index.html: `SEAW`); a river-only world's water is what it always was.
// The water sheet carries three attributes for it (sea.js openWaterAttributes): `open` (1 the sea's or the lake's water
// and the shore round it, 0 the river, a stream, a moat), `depth` (the water's y less the ground's; < 0 under the bank),
// `surf` (1 where foam may break, 0 against a steep face).
import { wgslFn, attribute, uniform, positionWorld, cameraPosition } from "three/tsl";
import * as THREE from "three";

// (the warped plane the chop and the glitter are read off: a few metres' drift, slow, never the same twice)
const seaWarp = wgslFn(`
  fn seaWarp(p: vec2<f32>, t: f32) -> vec2<f32> {
    return p + vec2<f32>(sin(p.y * 0.023 + 1.7) * 7.0 + sin(p.x * 0.051 - t * 0.07) * 3.0 + sin((p.x + p.y) * 0.0071) * 11.0,
                         sin(p.x * 0.019 + 0.4) * 7.0 + sin(p.y * 0.047 + t * 0.06) * 3.0 + sin((p.x - p.y) * 0.0063 + 2.1) * 11.0);
  }
`);

const seaWave = wgslFn(`
  fn seaWave(wave: mat4x4<f32>, wp: vec3<f32>, t: f32, open: f32, depth: f32, swell: vec3<f32>, cam: vec3<f32>) -> mat4x4<f32> {
    if (open < 0.001) { return wave; }
    let sea = swell.z;
    let d = max(depth, 0.0);
    let deepK = 1.0 - exp(-d / mix(2.6, 4.5, sea));
    let shallow = mix(vec3<f32>(0.19, 0.34, 0.28), vec3<f32>(0.15, 0.42, 0.42), sea);
    let deepC = mix(vec3<f32>(0.05, 0.19, 0.22), vec3<f32>(0.03, 0.14, 0.27), sea);
    var col = mix(shallow, deepC, deepK);
    let hf = 1.0 - smoothstep(45.0, 220.0, length(cam.xz - wp.xz));   // (the short ripples: gone with distance)
    let q = seaWarp(wp.xz, t);
    // the swell: crests running onshore, wavy along their length
    let dir = normalize(swell.xy + vec2<f32>(0.0001, 0.0));
    let side = vec2<f32>(dir.y, -dir.x);
    let along = dot(q, side);
    let L = mix(6.0, 14.0, sea);
    // (a second train 15 degrees off and 17% longer: the crests come in groups, rising and fading along their length)
    let dir2 = dir * 0.966 + side * 0.259;
    let sw = (sin(dot(q, dir) * 6.2831 / L - t * mix(1.7, 1.2, sea) + 0.8 * sin(along * 0.045) + 0.4 * sin(along * 0.13 + t * 0.2))
            + 0.7 * sin(dot(q, dir2) * 6.2831 / (L * 1.17) - t * mix(1.55, 1.1, sea) + 0.6 * sin(dot(q, dir2.yx) * 0.031))) / 1.45;
    // the chop: four trains, odd angles to the swell, odd lengths
    let d1 = dir * 0.85 + side * 0.53;
    let d2 = dir * 0.70 - side * 0.72;
    let d3 = -dir * 0.32 + side * 0.95;
    let d4 = -dir * 0.74 - side * 0.67;
    let c1 = sin(dot(q, d1) * 1.186 - t * 1.9);
    let c2 = sin(dot(q, d2) * 1.698 - t * 2.3 + 1.1);
    let c3 = sin(dot(q, d3) * 0.706 - t * 1.4 + 2.3);
    let c4 = sin(dot(q, d4) * 2.732 - t * 3.0 + 0.4);
    let chop = (0.45 * c1 + 0.4 * c3 + (0.35 * c2 + 0.25 * c4) * hf) / (0.85 + 0.6 * hf);
    // (wind on the water: wide patches a little darker or brighter)
    let wind = 0.5 + 0.5 * sin(q.x * 0.011 + sin(q.y * 0.013) * 2.0 + t * 0.02) * sin(q.y * 0.009 - t * 0.015 + 1.3);
    col = col * (0.93 + 0.14 * wind)
              + vec3<f32>(0.03) * (0.7 * sw + 0.6 * chop)
              + vec3<f32>(0.15) * smoothstep(0.72, 0.95, sw) * mix(0.45, 1.0, sea) * (0.3 + 0.7 * deepK) * (0.35 + 0.65 * wind) * (0.5 + 0.5 * hf)
              + vec3<f32>(0.07) * smoothstep(0.7, 0.95, chop) * (0.4 + 0.6 * hf);
    let o = clamp(open, 0.0, 1.0);
    var w = wave;
    w[0] = vec4<f32>(wave[0].rgb, mix(wave[0].w, 0.6 * c3 + 0.5 * c1 * hf, o));
    w[1] = vec4<f32>(mix(wave[1].rgb, col, o), mix(wave[1].w, 0.5 * chop + 0.6 * sw, o));
    return w;
  }
`, [seaWarp]);

// (where waterShade reads its glitter: the warped plane turned ~35 degrees, so its facets line up with nothing)
const seaGlitter = wgslFn(`
  fn seaGlitter(wp: vec3<f32>, open: f32, t: f32) -> vec3<f32> {
    let q = seaWarp(wp.xz, t);
    let r = vec2<f32>(q.x * 0.819 - q.y * 0.574, q.x * 0.574 + q.y * 0.819);
    return mix(wp, vec3<f32>(r.x, wp.y, r.y), clamp(open, 0.0, 1.0));
  }
`, [seaWarp]);

const seaFinish = wgslFn(`
  fn seaFinish(c: vec4<f32>, wp: vec3<f32>, t: f32, open: f32, depth: f32, swell: vec3<f32>, ice: f32, surf: f32) -> vec4<f32> {
    if (open < 0.001 || ice > 0.5) { return c; }
    let sea = swell.z;
    let d = depth;
    let broken = 0.6 + 0.4 * sin(wp.x * 1.3 + wp.z * 1.7 + t * 0.6) * sin(wp.x * 0.37 - wp.z * 0.29 - t * 0.4);
    // the swash: a line of white at the water's edge, now up the beach and now back
    let reach = mix(0.12, 0.3, sea) * (0.6 + 0.4 * sin(t * 0.9 + wp.x * 0.05 + wp.z * 0.04));
    let edge = (1.0 - smoothstep(0.0, reach, abs(d - 0.04)));
    // the surf: bands of foam rolling in over the shallows, thinning as they come
    let band = sin(d * mix(4.5, 2.6, sea) * 3.1416 + t * mix(1.4, 1.9, sea));
    let surfB = smoothstep(0.6, 0.97, band) * (1.0 - smoothstep(0.15, mix(0.7, 1.7, sea), d)) * step(0.0, d);
    let foam = clamp(max(edge * 0.85, surfB * mix(0.3, 0.75, sea)) * broken, 0.0, 1.0) * clamp(open, 0.0, 1.0) * clamp(surf, 0.0, 1.0);
    let col = mix(c.rgb, vec3<f32>(0.88, 0.92, 0.93), foam);
    // deep water is opaque: there is no bed to see through it
    let a = mix(c.w, max(c.w, 0.97), smoothstep(2.0, 9.0, d) * clamp(open, 0.0, 1.0));
    return vec4<f32>(col, max(a, foam * 0.92));
  }
`);

// DRY HULLS (2026-11-03): the one water sheet runs flat through every hull afloat, and an open hull's hold (a gaulos's,
// a merchantman's: bottom boards under the waterline) showed the sea's surface inside it, the cargo as if under water.
// Up to 8 hulls (harbour.js: the port's ships, each frame) are cut out of the water: an ellipse a little inside each
// hull's waterline plan -- its centre, its heading, 1 / its half length and half beam -- where the water is not drawn.
// Two vec4 a hull, two hulls a mat4 (columns): (x, z, cos yaw, sin yaw), (1/a, 1/b, on, 0). Nothing set, nothing cut.
const DRY_N = 8, dryM = Array.from({ length: DRY_N / 2 }, () => uniform(new THREE.Matrix4().set(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)));
// hulls: [{ x, z, yaw, a, b }] (a along the heading (cos yaw, -sin yaw), b across it); null or [] clears them
export function setDryHulls(hulls) {
  for (let i = 0; i < DRY_N; i++) {
    const e = dryM[i >> 1].value.elements, o = (i & 1) * 8, h = hulls?.[i];
    if (h && h.a > 0 && h.b > 0) e.splice(o, 8, h.x, h.z, Math.cos(h.yaw), Math.sin(h.yaw), 1 / h.a, 1 / h.b, 1, 0);
    else e[o + 6] = 0;
  }
}
const seaDry = wgslFn(`
  fn seaDry(c: vec4<f32>, wp: vec3<f32>, m0: mat4x4<f32>, m1: mat4x4<f32>, m2: mat4x4<f32>, m3: mat4x4<f32>) -> vec4<f32> {
    var dry = 0.0;
    for (var i = 0; i < 8; i++) {
      var m = m0;
      if (i >= 6) { m = m3; } else if (i >= 4) { m = m2; } else if (i >= 2) { m = m1; }
      let a = m[(i % 2) * 2];
      let b = m[(i % 2) * 2 + 1];
      if (b.z < 0.5) { continue; }
      let d = wp.xz - a.xy;
      let lx = (d.x * a.z - d.y * a.w) * b.x;
      let lz = (d.x * a.w + d.y * a.z) * b.y;
      dry = max(dry, step(lx * lx + lz * lz, 1.0));
    }
    return vec4<f32>(c.rgb, c.w * (1.0 - dry));
  }
`);

// the nodes for a world's open water (sea.js seaAPI's object): wave(waveNode, t) before waterShade, gp(t) its glitter
// plane, finish(outNode, t, ice) after it (the hulls' dry holes cut from it last)
export function seaWaterNodes(SEA) {
  const sw = SEA.swell ?? [.6, .8];
  const swell = uniform(new THREE.Vector3(sw[0], sw[1], SEA.kind === "sea" ? 1 : 0));
  const open = attribute("open", "float"), depth = attribute("depth", "float"), surf = attribute("surf", "float");
  return {
    swell,
    wave: (wave, t) => seaWave({ wave, wp: positionWorld, t, open, depth, swell, cam: cameraPosition }),
    gp: (t) => seaGlitter({ wp: positionWorld, open, t }),
    finish: (out, t, ice) => seaDry({ c: seaFinish({ c: out, wp: positionWorld, t, open, depth, swell, ice, surf }), wp: positionWorld,
                                      m0: dryM[0], m1: dryM[1], m2: dryM[2], m3: dryM[3] }),
  };
}
