// The tile patterns in WGSL -- the twin of textures.js's PATTERN_GLSL, checked against it by
// examples/webgpu_parity.html?lib=pattern. Two users: the tile bake (one full-screen pass per tile, 3x3
// samples a texel) and the building materials, which evaluate the same functions per pixel when the baked
// tiles are switched off.
//
// GLSL's file-scope `gTilePhase` -- which way the wind has the blades leaning while a grass tile is baked --
// has no WGSL equivalent, so patternTile takes it as an argument.
import { wgslFn } from "three/tsl";

export const tileHash = wgslFn(`
  fn tileHash(p: vec2<f32>) -> f32 { return fract(sin(dot(p, vec2<f32>(127.1, 311.7))) * 43758.5); }
`);

// value noise that repeats with the tile: its lattice (cells of ~c metres, a whole number of them to a period)
// wraps every per metres, so a baked tile still tiles seamlessly
export const tileNoise = wgslFn(`
  fn tileNoise(q: vec2<f32>, per: vec2<f32>, c: f32) -> f32 {
    let N = max(floor(per / c + 0.5), vec2<f32>(1.0));
    let g = q / per * N;
    let i = floor(g);
    var f = g - i;
    f = f * f * (3.0 - 2.0 * f);
    let i0 = i - N * floor(i / N);
    let i1 = (i + 1.0) - N * floor((i + 1.0) / N);
    return mix(mix(tileHash(i0), tileHash(vec2<f32>(i1.x, i0.y)), f.x),
               mix(tileHash(vec2<f32>(i0.x, i1.y)), tileHash(i1), f.x), f.y);
  }
`, [tileHash]);

export const patternTile = wgslFn(`
  fn patternTile(pat: f32, q: vec2<f32>, phase: f32) -> vec3<f32> {
    var k = 1.0; var a = 0.0; var b = 0.0;
    if (pat < 2.5) {                     // 1 ashlar: large courses, staggered joints   2 brick: tight running bond
      let br = pat > 1.5;
      let ch = select(0.8, 0.27, br);
      let bw = select(1.6, 0.56, br);
      let row = floor(q.y / ch);
      var m = step(fract(q.y / ch), select(0.045, 0.1, br));
      m = max(m, step(fract(q.x / bw + (row - 2.0 * floor(row / 2.0)) * 0.5), select(0.028, 0.06, br)));
      k = 1.0 - m * select(0.09, 0.16, br);
    } else if (pat < 3.5) {              // 3 grooves: vertical channels in the accent colour
      a = step(0.62, fract(q.x * 6.0));
    } else if (pat < 4.5) {              // 4 stars: a dot grid in the accent colour
      a = smoothstep(0.19, 0.13, length(fract(q / 0.55) - 0.5));
    } else if (pat < 5.5) {              // 5 marble: hairline joints of Greek precision masonry
      let row = floor(q.y / 1.1);
      var m = step(fract(q.y / 1.1), 0.015);
      m = max(m, step(fract(q.x / 2.3 + (row - 2.0 * floor(row / 2.0)) * 0.5), 0.0075));
      k = 1.0 - m * 0.05;
    } else if (pat < 6.5) {              // 6 tiles: scalloped roof courses
      let row = floor(q.y / 0.36);
      let tu = fract(q.x / 0.32 + (row - 2.0 * floor(row / 2.0)) * 0.5) - 0.5;
      var m = step(fract(q.y / 0.36), 0.14 + 0.2 * (1.0 - 2.0 * abs(tu)));
      m = max(m * 0.8, step(abs(tu), 0.03) * 0.5);
      k = 1.0 - m * 0.2;
    } else if (pat < 7.5) {              // 7 scroll: interfering waves curl into gilded tendrils
      let s = q * 0.76;                  // every frequency a whole multiple of .76: the tile repeats exactly
      let w1 = sin(s.x * 4.0 + sin(s.y * 6.0 + s.x * 2.0) * 1.6);
      let w2 = sin(s.y * 5.0 + sin(s.x * 3.0 - s.y * 2.0) * 1.8 + 1.2);
      let m = smoothstep(0.55, 0.8, w1 * w2);
      let e = smoothstep(0.38, 0.55, w1 * w2) - m;
      a = clamp(m + e * 0.45, 0.0, 1.0);
      b = smoothstep(0.55, 0.82, -(w1 * w2)) * 0.9;
    } else if (pat < 8.5) {              // 8 gothic: pilaster strips, string courses, blind tracery, faint joints
      let du = min(fract(q.x / 3.0), 1.0 - fract(q.x / 3.0)) * 3.0;
      k = k * (1.0 - 0.22 * smoothstep(0.14, 0.05, du));
      k = k * (1.0 + 0.1 * (smoothstep(0.3, 0.17, du) - smoothstep(0.14, 0.05, du)));
      let by = fract(q.y / 6.5);
      k = k * (1.0 - 0.16 * step(by, 0.05));
      k = k * (1.0 + 0.08 * step(0.05, by) * step(by, 0.1));
      k = k * (1.0 - 0.08 * step(0.92, fract(q.x / 0.75)) * step(0.45, by));
      k = k * (1.0 - 0.05 * step(fract(q.y / 0.8125), 0.06));   // 8 joints to a course
    } else if (pat < 9.5) {              // 9 checker: 1.1m marble squares with thin joints
      let cell = floor(q.x / 1.1) + floor(q.y / 1.1);
      a = (cell - 2.0 * floor(cell / 2.0)) * 0.8;
      let j = min(fract(q / 1.1), 1.0 - fract(q / 1.1));
      k = 1.0 - 0.12 * step(min(j.x, j.y), 0.012);
    } else if (pat < 10.5) {             // 10 ornament: a diamond lattice with centre bosses
      let o = q / 0.85;
      let f = abs(fract(o) - 0.5);
      let a1 = smoothstep(0.06, 0.02, abs(f.x + f.y - 0.5)) * 0.55;
      let a2 = smoothstep(0.11, 0.05, length(fract(o) - 0.5)) * 0.6;
      a = 1.0 - (1.0 - a1) * (1.0 - a2);
    } else if (pat < 11.5) {             // 11 parquet: .14m boards in 1.2m lengths, staggered, each its own tone
      let row = floor(q.y / 0.14);
      let sh = (row - 2.0 * floor(row / 2.0)) * 0.5;
      let j = max(step(fract(q.y / 0.14), 0.06), step(fract(q.x / 1.2 + sh), 0.02));
      let r16 = row - 16.0 * floor(row / 16.0);
      let c4 = floor(q.x / 1.2 + sh) - 4.0 * floor(floor(q.x / 1.2 + sh) / 4.0);
      let tone = fract(sin(r16 * 12.99 + c4 * 78.23) * 437.58);
      k = (1.0 - j * 0.22) * (0.9 + 0.16 * tone);
    } else {
      // 99 grass: BLADES -- three to a ~3cm cell, each a tapered streak from its root in the direction it leans,
      // the tip pushed along +x by the tile's wind phase. The nearest blade wins the texel; R is its coverage,
      // G and B its along-the-blade place and its own tone, both PREMULTIPLIED by the coverage so the mip chain
      // averages them the way it averages the coverage (the ground divides them back out).
      let CELLS = 16.0;
      let CELL = 1.0 / CELLS;
      let W0 = 0.004;
      let W1 = 0.0012;
      let BEND = 0.018;
      let gi = floor(q / CELL);
      var cov = 0.0; var tip = 0.0; var tone = 0.0;
      for (var j: i32 = -1; j <= 1; j = j + 1) {
        for (var i: i32 = -1; i <= 1; i = i + 1) {
          let cc = gi + vec2<f32>(f32(i), f32(j));
          let cw = cc - CELLS * floor(cc / CELLS);       // wrapped: the tile repeats seamlessly at its period
          for (var n: i32 = 0; n < 3; n = n + 1) {
            let o = f32(n) * 13.0;
            let h1 = tileHash(cw + o);
            let h2 = tileHash(cw + o + 17.0);
            let h3 = tileHash(cw + o + 41.0);
            let h4 = tileHash(cw + o + 73.0);
            let root = (cc + vec2<f32>(h1, h2)) * CELL;
            let ang = h3 * 6.2832;
            let len = CELL * (0.6 + 0.8 * h4);
            let t = root + vec2<f32>(cos(ang), sin(ang)) * len + vec2<f32>(phase * BEND * (0.6 + 0.8 * h2), 0.0);
            let d = t - root;
            let pq = q - root;
            let u = clamp(dot(pq, d) / max(dot(d, d), 1e-9), 0.0, 1.0);
            let dist = length(pq - d * u);
            let w = mix(W0, W1, u);
            let c = smoothstep(w, w * 0.45, dist);
            if (c > cov) { cov = c; tip = u; tone = h3; }
          }
        }
      }
      return vec3<f32>(cov, cov * tip, cov * tone);
    }
    return vec3<f32>(k, a, b);
  }
`, [tileHash]);

// the pattern's RELIEF (baked into the tile's alpha, for parallax): 1 the face, 0 its deepest -- mortar, a
// channel, the gap under a roof tile. The same joints as patternTile; stones' edges bevelled and unevenly worn,
// their faces pitted, bricks chipped, mortar grainy (per: the tile's period -- the noise repeats with it)
export const patternHeight = wgslFn(`
  fn patternHeight(pat: f32, q: vec2<f32>, per: vec2<f32>) -> f32 {
    if (pat < 2.5) {                     // ashlar, brick: stones proud of the mortar, rounded at the arrises
      let br = pat > 1.5;
      let ch = select(0.8, 0.27, br);
      let bw = select(1.6, 0.56, br);
      let wy = select(0.045, 0.1, br);
      let wx = select(0.028, 0.06, br);
      let bev = select(0.035, 0.01, br);
      let row = floor(q.y / ch);
      let fy = fract(q.y / ch);
      let sx = q.x / bw + (row - 2.0 * floor(row / 2.0)) * 0.5;
      let fx = fract(sx);
      let d = min(min(fy - wy, 1.0 - fy) * ch, min(fx - wx, 1.0 - fx) * bw);   // metres inside the stone
      var rough = 0.12 * tileNoise(q, per, 0.08) + 0.07 * tileNoise(q + 3.0, per, 0.025) + 0.04 * tileNoise(q + 9.0, per, 0.01);
      if (br) { rough = 0.1 * tileNoise(q, per, 0.025) + 0.05 * tileNoise(q + 7.0, per, 0.01); }
      // the arris worn unevenly: the bevel wider here, sharper there
      let wear = select(0.5, 0.4, br) * tileNoise(q + 5.0, per, select(0.1, 0.04, br));
      if (d < 0.0) { return 0.1 + 0.06 * tileNoise(q + 11.0, per, 0.02); }
      return 0.5 + 0.5 * smoothstep(0.0, bev * (0.6 + wear * 2.0), d) - 0.1 * tileHash(vec2<f32>(row, floor(sx))) - rough;
    } else if (pat < 3.5) {              // grooves: channels cut in
      let f = fract(q.x * 6.0);
      return 1.0 - 0.9 * smoothstep(0.6, 0.66, f) * (1.0 - smoothstep(0.96, 1.0, f));
    } else if (pat < 5.5 && pat > 4.5) { // marble: hairline joints
      let row = floor(q.y / 1.1);
      let sx = q.x / 2.3 + (row - 2.0 * floor(row / 2.0)) * 0.5;
      let j = min(min(fract(q.y / 1.1), 1.0 - fract(q.y / 1.1)) * 1.1, min(fract(sx), 1.0 - fract(sx)) * 2.3);
      return 0.2 + 0.8 * smoothstep(0.004, 0.012, j);
    } else if (pat < 6.5 && pat > 5.5) { // tiles: each course thick at its lower edge, sunk where the scallops part
      let row = floor(q.y / 0.36);
      let fy = fract(q.y / 0.36);
      let tu = fract(q.x / 0.32 + (row - 2.0 * floor(row / 2.0)) * 0.5) - 0.5;
      let m = step(fy, 0.14 + 0.2 * (1.0 - 2.0 * abs(tu)));
      return mix(0.3 + 0.7 * (1.0 - fy), 0.1, m) - 0.08 * tileNoise(q, per, 0.04);
    } else if (pat < 8.5 && pat > 7.5) { // gothic: strips and courses stand out, tracery and joints cut in
      let du = min(fract(q.x / 3.0), 1.0 - fract(q.x / 3.0)) * 3.0;
      let by = fract(q.y / 6.5);
      var h = 0.55 + 0.45 * smoothstep(0.14, 0.1, du);
      h = max(h, step(by, 0.05));
      h = h - (0.25 * step(0.92, fract(q.x / 0.75)) * step(0.45, by) + 0.15 * step(fract(q.y / 0.8125), 0.06));
      return clamp(h - 0.06 * tileNoise(q, per, 0.1) - 0.03 * tileNoise(q + 3.0, per, 0.03), 0.0, 1.0);
    } else if (pat < 9.5 && pat > 8.5) { // checker: thin joints
      let j = min(fract(q / 1.1), 1.0 - fract(q / 1.1)) * 1.1;
      return 0.1 + 0.9 * smoothstep(0.008, 0.016, min(j.x, j.y));
    } else if (pat < 10.5 && pat > 9.5) {   // ornament: lattice and bosses raised
      let o = q / 0.85;
      let f = abs(fract(o) - 0.5);
      let a1 = smoothstep(0.07, 0.02, abs(f.x + f.y - 0.5));
      let a2 = smoothstep(0.12, 0.04, length(fract(o) - 0.5));
      return 0.4 + 0.6 * max(a1, a2) - 0.04 * tileNoise(q, per, 0.03);
    } else if (pat < 11.5 && pat > 10.5) {  // parquet: the joints between boards
      let row = floor(q.y / 0.14);
      let sh = (row - 2.0 * floor(row / 2.0)) * 0.5;
      return 1.0 - 0.8 * max(step(fract(q.y / 0.14), 0.06), step(fract(q.x / 1.2 + sh), 0.02));
    }
    return 1.0;                          // flat: stars, scroll, grass
  }
`, [tileHash, tileNoise]);
