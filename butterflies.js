// BUTTERFLIES (2026-10-05; docs/butterflies.md): a species is a SHAPE (the forewing's and the hindwing's outlines as
// polar profiles from the wing's root -- scallops, a tail) and two PAINTINGS, the upperside's and the underside's, each
// a list of layers in WING COORDINATES -- `t` from the base (0) to the margin (1) along the ray, `a` from the costa (0)
// to the inner margin (1) -- so one band scheme (the nymphalid ground plan: basal, discal, central, border ocelli,
// submarginal, marginal, fringe) fits every outline. Painted once per species into a texture (fore and hind, upper and
// under, the body); drawn as flat wings -- one plane each, its two faces the two sides, the right the left's mirror --
// flapping in the vertex shader, one instanced draw a species (createButterflies); the asset viewer shows a species
// as a specimen plate (drawSpecimen).
import * as THREE from "three";
import { wgslFn, positionLocal, positionWorld, cameraPosition, attribute, instancedBufferAttribute, texture, uv } from "three/tsl";
import { lightWGSL } from "./light.js";
import { PREGEN, pregenOn, pregenMiss, recordFor, hasher } from "./pregen.js";   // (the wings, painted once by build/pregen.py)

const DEG = Math.PI / 180;
const hexRGB = (c) => { const v = parseInt(String(c).slice(1), 16); return [(v >> 16) & 255, (v >> 8) & 255, v & 255]; };
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const sstep = (e0, e1, x) => { const t = clamp01((x - e0) / (e1 - e0 || 1e-9)); return t * t * (3 - 2 * t); };
const isPlain = (v) => v && typeof v === "object" && !Array.isArray(v);
const merge = (a, b) => { if (!isPlain(a) || !isPlain(b)) return b === undefined ? a : b; const o = { ...a }; for (const [k, v] of Object.entries(b)) o[k] = merge(a[k], v); return o; };

// ---- the species, resolved: its shape (a name out of butterflies/shapes, with the species' own overrides)
export function resolveSpecies(def, shapes) {
  const base = shapes?.[def.shape] ?? {};
  return { ...def, fore: merge(base.fore ?? {}, def.fore ?? {}), hind: merge(base.hind ?? {}, def.hind ?? {}), hindRoot: def.hindRoot ?? base.hindRoot ?? [-.04, 0] };
}

// ---- THE OUTLINE: a polar profile R(phi) through the control points (Catmull-Rom in phi), scalloped between the
// veins; the TAIL a bump of the radius beyond it. R0: the margin the bands are measured to; R: with the tail
export function wingProfile(w) {
  const from = w.from ?? 70, to = w.to ?? 160, pts = [...(w.R ?? [[from, 1], [to, .5]])].sort((p, q) => p[0] - q[0]);
  const n = pts.length, veins = Math.max(2, w.veins ?? 8), sc = w.scallop ?? null, tl = w.tail ?? null;
  const cr = (phi) => {
    if (phi <= pts[0][0]) return pts[0][1];
    if (phi >= pts[n - 1][0]) return pts[n - 1][1];
    let i = 0; while (i < n - 2 && phi > pts[i + 1][0]) i++;
    const p0 = pts[Math.max(0, i - 1)][1], p1 = pts[i][1], p2 = pts[i + 1][1], p3 = pts[Math.min(n - 1, i + 2)][1];
    const t = (phi - pts[i][0]) / (pts[i + 1][0] - pts[i][0]);
    return .5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t);
  };
  const aOf = (phi) => (phi - from) / (to - from);
  // (the scallop: the margin bowed in between the vein tips -- the tips stay where they are)
  const R0 = (phi) => { let r = cr(phi); if (sc?.amp) r *= 1 - sc.amp * Math.pow(Math.sin(Math.PI * (sc.n ?? veins) * aOf(phi)), 2); return r; };
  const tailAt = (phi) => {
    if (!tl?.length) return 0;
    const x = (phi - tl.at) / (tl.width ?? 5);
    return Math.abs(x) < 1 ? tl.length * Math.pow(1 - Math.pow(Math.abs(x), tl.round ?? 3), .5) : 0;
  };
  const R = (phi) => R0(phi) + tailAt(phi);
  // the veins' angles: between the cells, n cells across the wing
  const veinA = Array.from({ length: veins - 1 }, (_, k) => (k + 1) / veins);
  // the outline, densely, and its bounds (the wing's own units: the forewing's length is 1)
  const outline = [];
  for (let i = 0; i <= 160; i++) { const phi = from + (to - from) * i / 160, r = R(phi); outline.push([r * Math.cos(phi * DEG), r * Math.sin(phi * DEG)]); }
  const xs = [0, ...outline.map((p) => p[0])], ys = [0, ...outline.map((p) => p[1])];
  return { from, to, R0, R, aOf, veins, veinA, outline, bounds: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)], tail: tl };
}

// ---- noise for the mottles (a value noise, seeded)
function noise2(seed) {
  const h = (i, j) => { let x = Math.imul(i * 374761393 + j * 668265263 + seed * 2147483647 | 0, 1274126177); x = (x ^ (x >>> 13)) * 1274126177; return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };
  return (x, y) => {
    const i = Math.floor(x), j = Math.floor(y), u = x - i, v = y - j, su = u * u * (3 - 2 * u), sv = v * v * (3 - 2 * v);
    return (h(i, j) * (1 - su) + h(i + 1, j) * su) * (1 - sv) + (h(i, j + 1) * (1 - su) + h(i + 1, j + 1) * su) * sv;
  };
}

// ---- PAINTING A SIDE: per texel, its wing coordinates, then the layers in order over the ground
export function paintWing(side, prof, px, cx, cy, img, W, ox, oy, w, h) {
  const d = img.data, layers = side?.layers ?? [], ground = hexRGB(side?.ground ?? "#c8b090");
  const tailC = side?.tail ? hexRGB(side.tail) : null;
  const L = layers.map((l, k) => ({ ...l, rgb: l.color ? hexRGB(l.color) : null, to: l.to ? hexRGB(l.to) : null, alt: l.alt ? hexRGB(l.alt) : null,
    rings: (l.rings ?? []).map(hexRGB), pupil: l.pupil ? hexRGB(l.pupil) : null, glint: l.glint ? hexRGB(l.glint) : null,
    cols: (l.colors ?? []).map(hexRGB), nz: l.type === "dust" ? noise2(l.seed ?? 7 + k) : null }));
  const span = prof.to - prof.from, cellA = (k) => (k + .5) / prof.veins;
  const at = (a, t) => { const phi = prof.from + span * a, r = t * prof.R0(phi); return [r * Math.cos(phi * DEG), r * Math.sin(phi * DEG)]; };
  const aa = 1.5 / px;   // (a texel, in wing units: the edges' softness)
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
    const x = cx + (i + .5) / px, y = cy - (j + .5) / px, r = Math.hypot(x, y);
    let phi = Math.atan2(y, x) / DEG;
    while (phi < prof.from - 90) phi += 360; while (phi > prof.from + 270) phi -= 360;
    const k4 = ((oy + j) * W + ox + i) * 4;
    const Rt = prof.R(phi);
    if (phi < prof.from - .5 || phi > prof.to + .5 || r > Rt + aa) { d[k4 + 3] = 0; continue; }
    const R0 = prof.R0(phi), t = r / R0, a = (phi - prof.from) / span;
    let c = ground.slice();
    const mix = (rgb, f) => { if (f <= 0) return; for (let q = 0; q < 3; q++) c[q] += (rgb[q] - c[q]) * Math.min(1, f); };
    for (const l of L) {
      const s = l.soft ?? .015, inA = l.a ? sstep(l.a[0] - .01, l.a[0] + .01, a) * sstep(-l.a[1] - .01, -l.a[1] + .01, -a) : 1;
      if (inA <= 0) continue;
      const op = l.alpha ?? 1;
      if (l.type === "band") {
        const sh = (l.slope ?? 0) * a + (l.wave ? l.wave.amp * Math.sin(2 * Math.PI * (l.wave.n ?? 6) * a) : 0);
        const t0 = l.t[0] + sh, t1 = l.t[1] + sh;
        mix(l.rgb, op * inA * sstep(t0 - s, t0 + s, t) * sstep(-t1 - s, -t1 + s, -t));
      } else if (l.type === "gradient") {
        const f = clamp01((t - l.t[0]) / (l.t[1] - l.t[0])), g = l.rgb.map((v, q) => v + (l.to[q] - v) * f);
        mix(g, op * inA * sstep(l.t[0] - s, l.t[0], t) * (l.fade ? 1 - f : 1) * sstep(-l.t[1] - s, -l.t[1], -t));
      } else if (l.type === "veins") {
        const tr = l.t ?? [.15, 1.2], wv = (l.width ?? .012) / 2;   // (from the discal cell out: the veins branch from it, not from the root)
        let best = 1e9;
        for (const va of prof.veinA) best = Math.min(best, r * Math.abs(Math.sin((phi - (prof.from + span * va)) * DEG)));
        if (l.cell) best = Math.min(best, Math.abs(t - l.cell));   // (the discal cell's end, a cross-vein)
        mix(l.rgb, op * inA * sstep(wv + aa, wv - aa, best) * sstep(tr[0] - .02, tr[0], t) * sstep(-tr[1] - .02, -tr[1], -t));
      } else if (l.type === "spots" || l.type === "eye") {
        const cells = l.cells ?? (l.cell !== undefined ? [l.cell] : null);
        const as = cells ? cells.map(cellA) : l.n ? Array.from({ length: l.n }, (_, q) => l.a ? l.a[0] + (l.a[1] - l.a[0]) * (q + .5) / l.n : (q + .5) / l.n) : [l.at ?? .5];
        for (const ac of as) {
          const tt = (l.t ?? .8) + (l.slope ?? 0) * ac, [px0, py0] = at(ac, tt), rad = l.r ?? .04;
          let dx = x - px0, dy = y - py0;
          if (l.aspect) {   // (stretched along the ray: an oval ocellus, a bar)
            const ph = Math.atan2(py0, px0), cu = Math.cos(ph), su = Math.sin(ph), ur = dx * cu + dy * su, vr = -dx * su + dy * cu;
            dx = ur / l.aspect; dy = vr;
          }
          const dd = Math.hypot(dx, dy);
          if (l.type === "eye") {
            const rings = l.rings, nR = rings.length;
            for (let q = 0; q < nR; q++) { const rr = rad * (1 - q / (nR + 1)); mix(rings[q], op * sstep(rr + aa, rr - aa, dd)); }
            if (l.pupil) { const rp = rad * (l.pupilR ?? .35); mix(l.pupil, op * sstep(rp + aa, rp - aa, dd)); }
            if (l.glint) { const g = Math.hypot(dx + rad * .16, dy - rad * .16), rg = rad * .12; mix(l.glint, op * sstep(rg + aa, rg - aa, g)); }
          } else {
            let cov = sstep(rad + aa, rad - aa, dd);
            if (l.shape === "lunule") {   // a crescent: the disc less one nearer the base
              const ph = Math.atan2(py0, px0), sx = x - (px0 - Math.cos(ph) * rad * .55), sy = y - (py0 - Math.sin(ph) * rad * .55);
              cov *= 1 - sstep(rad * .9 + aa, rad * .9 - aa, Math.hypot(sx, sy));
            } else if (l.shape === "chevron") {
              const ph = Math.atan2(py0, px0), u = (x - px0) * Math.cos(ph) + (y - py0) * Math.sin(ph), v = -(x - px0) * Math.sin(ph) + (y - py0) * Math.cos(ph);
              const dist = Math.abs(u + Math.abs(v) * .9) ;
              cov = sstep(rad * .35 + aa, rad * .35 - aa, dist) * sstep(rad + aa, rad - aa, Math.abs(v));
            }
            mix(l.rgb, op * inA * cov);
          }
        }
      } else if (l.type === "dust") {
        const sc = l.scale ?? 30, n1 = l.nz(x * sc, y * sc), n2 = l.nz(x * sc * 3.1 + 17, y * sc * 3.1), v = .65 * n1 + .35 * n2;
        const tr = l.t ?? [0, 1.2];
        const f = op * inA * sstep(tr[0] - .02, tr[0], t) * sstep(-tr[1] - .02, -tr[1], -t);
        const cols = l.cols, q = clamp01(v) * (cols.length - 1), i0 = Math.min(cols.length - 2, Math.floor(q));
        const g = cols[i0].map((vv, z) => vv + (cols[i0 + 1][z] - vv) * (q - i0));
        mix(g, f * (l.amount ?? .6));
      } else if (l.type === "fringe") {
        const fw = l.width ?? .035;
        if (t > 1 - fw - s || r > R0) {
          let cc = l.rgb;
          if (l.alt) { let near = 1e9; for (const va of prof.veinA) near = Math.min(near, Math.abs(a - va)); if (near < (l.chequer ?? .025)) cc = l.alt; }
          mix(cc, op * sstep(1 - fw - s, 1 - fw + s, t) * (r > R0 + (prof.tail ? 0 : 1) ? 1 : 1));
        }
      }
    }
    if (r > R0 && tailC) { const f = sstep(R0, R0 + .01, r); for (let q = 0; q < 3; q++) c[q] += (tailC[q] - c[q]) * f; }
    d[k4] = c[0]; d[k4 + 1] = c[1]; d[k4 + 2] = c[2];
    d[k4 + 3] = 255 * sstep(Rt + aa, Rt - aa, r);
  }
}

// ---- THE TEXTURE: four cells (fore and hind, upper and under) and a body swatch, side by side; and where each is
const PX = 192;   // texels per forewing length
export function speciesAtlas(sp) {
  const fp = wingProfile(sp.fore), hp = wingProfile(sp.hind);
  const cell = (prof) => { const [x0, y0, x1, y1] = prof.bounds; return { cx: x0, cy: y1, w: Math.ceil((x1 - x0) * PX) + 2, h: Math.ceil((y1 - y0) * PX) + 2 }; };
  const cf = cell(fp), ch = cell(hp), H = Math.max(cf.h, ch.h);
  const cells = { upperFore: { ...cf, prof: fp }, upperHind: { ...ch, prof: hp }, underFore: { ...cf, prof: fp }, underHind: { ...ch, prof: hp } };
  let x = 0;
  for (const k of ["upperFore", "upperHind", "underFore", "underHind"]) { cells[k].ox = x; cells[k].oy = 0; x += cells[k].w + 2; }
  const bodyX = x, W = x + 8;
  const cv = typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(W, H) : Object.assign(document.createElement("canvas"), { width: W, height: H });
  const g = cv.getContext("2d", { willReadFrequently: true }), img = g.createImageData(W, H);
  // (PAINTED ONCE: pregen/ keeps each species' atlas under a hash of the species itself -- its shapes, its paintings)
  const pk = pregenOn() ? hasher().str("wing").json({ ...sp, fly: undefined, name: undefined }).hex() : null, cached = pk && PREGEN.wings.get(pk);
  if (cached && cached.width === W && cached.height === H) g.drawImage(cached, 0, 0);
  else {
    const sideOf = (k) => (k.startsWith("upper") ? sp.upper : sp.under)?.[k.endsWith("Fore") ? "fore" : "hind"];
    for (const [k, c] of Object.entries(cells)) paintWing(sideOf(k), c.prof, PX, c.cx, c.cy, img, W, c.ox, c.oy, c.w, c.h);
    const bc = hexRGB(sp.body ?? "#2a2018");
    for (let j = 0; j < H; j++) for (let i = bodyX; i < W; i++) { const k4 = (j * W + i) * 4; img.data[k4] = bc[0]; img.data[k4 + 1] = bc[1]; img.data[k4 + 2] = bc[2]; img.data[k4 + 3] = 255; }
    g.putImageData(img, 0, 0);
    if (pk) { recordFor("wings", pk, cv); pregenMiss("wing", sp.name ?? "", pk); }
  }
  // a wing point (its own units) -> the texture's uv in a cell
  const uvOf = (k, x, y) => { const c = cells[k]; return [(c.ox + 1 + (x - c.cx) * PX) / W, 1 - (c.oy + 1 + (c.cy - y) * PX) / H]; };
  return { canvas: cv, W, H, cells, uvOf, bodyUV: [(bodyX + 4) / W, .5], fp, hp };
}

// ---- THE SPECIMEN PLATE (the viewer): the upperside spread as in a collection -- forewings drawn forward of the
// hindwings, left and right mirrored -- and the underside beside it
export function drawSpecimen(cv, defs, shapes, { cell = 320 } = {}) {
  const g = cv.getContext("2d", { willReadFrequently: true });
  const list = defs.map((d) => resolveSpecies(d, shapes));
  const cols = 2, PH = .98, rowH = cell * PH + 34;
  cv.height = Math.max(cv.height, list.length * rowH + 20);
  g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height);
  g.font = "12px ui-monospace, monospace";
  const errs = [];
  list.forEach((sp, i) => {
    const y0 = 10 + i * rowH;
    try {
      const A = speciesAtlas(sp);
      ["upper", "under"].forEach((which, k) => {
        const x0 = 10 + k * (cell * 1.25 + 20), s = cell * .55 / PX, mid = x0 + cell * .62;
        g.fillStyle = "#e8e2d6"; g.fillRect(x0, y0, cell * 1.25, cell * PH);
        // (the body's axis upright on the plate: the wing's forward is up, outward is to the side)
        for (const sd of [1, -1]) for (const w of ["Hind", "Fore"]) {
          const c = A.cells[which + w], root = w === "Hind" ? sp.hindRoot : [0, 0];
          g.save();
          g.translate(mid, y0 + cell * .3);
          g.scale(sd, 1);
          // wing (x forward, y outward) -> plate (right = outward, up = forward): rotate -90deg
          g.transform(0, -1, 1, 0, 0, 0);
          g.translate(root[0] * PX * s, root[1] * PX * s);
          g.drawImage(A.canvas, c.ox, c.oy, c.w, c.h, c.cx * PX * s, -c.cy * PX * s, c.w * s, c.h * s);
          g.restore();
        }
        g.fillStyle = sp.body ?? "#2a2018"; g.fillRect(mid - 3, y0 + cell * .3 - cell * .09, 6, cell * .26);
        g.fillStyle = "#555"; g.fillText(which === "upper" ? "upperside" : "underside", x0 + 6, y0 + 14);
      });
      g.fillStyle = "#d8d4cc"; g.fillText(`${sp.name}  ${sp.latin ? "(" + sp.latin + ")" : ""}  ${sp.span ? (sp.span * 100).toFixed(1) + " cm" : ""}`, 10, y0 + cell * PH + 16);
    } catch (e) { errs.push(`${sp.name}: ${e.message}`); g.fillStyle = "#e27a6a"; g.fillText(`${sp.name}: ${e.message}`, 10, y0 + 20); }
  });
  return errs;
}

// ---- THE GEOMETRY of a species: the body, and each wing a fan from its root, each triangle twice -- the face
// up taking the upperside's painting, the face down the underside's -- the right wing the left's mirror. `side` is
// the wing's side (+1 left, -1 right; 0 the body): the vertex shader turns the wings about the body's axis by it.
// Units: metres at life size (`span`), x forward, y up, z to the left
export function speciesGeometry(sp, A) {
  const FW = (sp.span ?? .06) * .46, bodyR = FW * .045, pos = [], uvs = [], side = [], idx = [];
  const V = (p, u, s) => { pos.push(...p); uvs.push(...u); side.push(s); return pos.length / 3 - 1; };
  for (const sd of [1, -1]) for (const [w, prof, k] of [["Hind", A.hp, 0], ["Fore", A.fp, 1]]) {
    const root = w === "Hind" ? sp.hindRoot : [0, 0], lift = k * FW * .004;   // (the forewing a hair above the hindwing it overlaps)
    const P = (x, y) => [(x + root[0]) * FW, lift, sd * (bodyR + (y + root[1]) * FW)];
    const N = 40, ring = [];
    for (let i = 0; i <= N; i++) { const phi = prof.from + (prof.to - prof.from) * i / N, r = prof.R(phi); ring.push([r * Math.cos(phi * DEG), r * Math.sin(phi * DEG)]); }
    for (const face of ["upper", "under"]) {
      const key = face + w, c0 = V(P(0, 0), A.uvOf(key, 0, 0), sd), vs = ring.map(([x, y]) => V(P(x, y), A.uvOf(key, x, y), sd));
      for (let i = 0; i < N; i++) {
        // (seen from above, the left wing's ring runs counter-clockwise: the upper face; the under face, and the
        //  mirrored right wing, the other way)
        const up = (face === "upper") === (sd > 0);
        if (up) idx.push(c0, vs[i + 1], vs[i]); else idx.push(c0, vs[i], vs[i + 1]);
      }
    }
  }
  // the body: thorax and abdomen as a ring-swept spindle, the head a smaller bead, two antennae
  const bu = A.bodyUV, rings = [[-FW * .62, .3], [-FW * .35, 1], [-FW * .05, 1.15], [FW * .1, 1.35], [FW * .17, 1.1], [FW * .2, .6]], K = 6;
  const ringIdx = rings.map(([x, f]) => Array.from({ length: K }, (_, q) => { const an = q / K * Math.PI * 2; return V([x, Math.sin(an) * bodyR * 1.6 * f, Math.cos(an) * bodyR * 1.6 * f], bu, 0); }));
  for (let r = 1; r < rings.length; r++) for (let q = 0; q < K; q++) { const a0 = ringIdx[r - 1][q], a1 = ringIdx[r - 1][(q + 1) % K], b0 = ringIdx[r][q], b1 = ringIdx[r][(q + 1) % K]; idx.push(a0, b0, b1, a0, b1, a1); }
  const tipB = V([-FW * .68, 0, 0], bu, 0), tipF = V([FW * .24, 0, 0], bu, 0);
  for (let q = 0; q < K; q++) { idx.push(tipB, ringIdx[0][(q + 1) % K], ringIdx[0][q]); idx.push(tipF, ringIdx[rings.length - 1][q], ringIdx[rings.length - 1][(q + 1) % K]); }
  for (const sd of [1, -1]) {   // antennae: thin flat blades, clubbed
    const a = V([FW * .2, bodyR, sd * bodyR * .4], bu, 0), b = V([FW * .2, bodyR * 1.6, sd * bodyR * .4], bu, 0);
    const c = V([FW * .62, FW * .2, sd * FW * .2], bu, 0), e = V([FW * .64, FW * .24, sd * FW * .22], bu, 0);
    idx.push(a, c, b, b, c, e, a, b, c, b, e, c);
  }
  const geo = new THREE.InstancedBufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geo.setAttribute("side", new THREE.Float32BufferAttribute(side, 1));
  geo.setIndex(idx);
  return geo;
}

// ---- THE MATERIAL: the wing turned by its flap about the body's axis, then the instance placed (heading, scale,
// position) -- all in the vertex stage, as the geometry is instanced by hand; lit per pixel by the plane's own normal
const place = wgslFn(`
  fn bflyPlace(p: vec3<f32>, side: f32, flap: f32, at: vec4<f32>, sc: f32) -> vec3<f32> {
    let th = -side * flap;
    let c = cos(th); let s = sin(th);
    let q = vec3<f32>(p.x, p.y * c - p.z * s, p.y * s + p.z * c) * sc;
    let ch = cos(at.w); let sh = sin(at.w);
    return vec3<f32>(q.x * ch + q.z * sh, q.y, -q.x * sh + q.z * ch) + at.xyz;
  }
`);
const shade = wgslFn(`
  fn bflyShade(c: vec4<f32>, pw: vec3<f32>, cam: vec3<f32>) -> vec4<f32> {
    var n = normalize(cross(dpdx(pw), dpdy(pw)));
    if (dot(n, cam - pw) < 0.0) { n = -n; }
    return vec4<f32>(c.rgb * ${lightWGSL("n")}, c.a);
  }
`);
function speciesMaterial(tex, at, sc, flap) {
  const m = new THREE.MeshBasicNodeMaterial({ side: THREE.FrontSide });
  m.positionNode = place({ p: positionLocal, side: attribute("side", "float"), flap: instancedBufferAttribute(flap), at: instancedBufferAttribute(at), sc: instancedBufferAttribute(sc) });
  m.colorNode = shade({ c: texture(tex, uv()), pw: positionWorld, cam: cameraPosition });
  m.alphaTest = .5;
  return m;
}

// ---- THE GAME'S BUTTERFLIES: one instanced mesh a species; add() a flier (a species) -> { position, rotY, animT },
// update(t) writes their places and flaps
export function createButterflies(scene, species, { shapes, scale = 3, cap = 64 } = {}) {
  const kinds = new Map(), all = [];
  const kindOf = (def) => {
    if (kinds.has(def.name)) return kinds.get(def.name);
    const sp = resolveSpecies(def, shapes), A = speciesAtlas(sp), geo = speciesGeometry(sp, A);
    const tex = new THREE.CanvasTexture(A.canvas);
    tex.colorSpace = THREE.SRGBColorSpace; tex.generateMipmaps = true; tex.minFilter = THREE.LinearMipmapLinearFilter; tex.anisotropy = 4;
    const at = new THREE.InstancedBufferAttribute(new Float32Array(cap * 4), 4), sc = new THREE.InstancedBufferAttribute(new Float32Array(cap), 1), flap = new THREE.InstancedBufferAttribute(new Float32Array(cap), 1);
    for (const b of [at, sc, flap]) b.setUsage(THREE.DynamicDrawUsage);
    const mesh = new THREE.Mesh(geo, speciesMaterial(tex, at, sc, flap));
    geo.instanceCount = 0;
    // (culled as a whole: a sphere round where its fliers are now, update() -- a species all behind you is not drawn)
    geo.computeBoundingSphere(); const reach = geo.boundingSphere.radius; geo.boundingSphere = new THREE.Sphere();
    scene.add(mesh);
    const k = { sp, mesh, geo, at, sc, flap, list: [], reach };
    kinds.set(def.name, k);
    return k;
  };
  return {
    add(def) {
      const k = kindOf(def);
      if (k.list.length >= cap) return null;
      const b = { position: new THREE.Vector3(), rotY: 0, animT: 0, phase: all.length * 1.7, hz: def.fly?.hz ?? 4, k };
      k.list.push(b); all.push(b);
      return b;
    },
    update(t) {
      for (const k of kinds.values()) {
        k.list.forEach((b, i) => {
          k.at.array.set([b.position.x, b.position.y, b.position.z, b.rotY], i * 4);   // (the body's forward, +x, turned to the heading as the herds turn theirs)
          k.sc.array[i] = scale * (b.size ?? 1);
          // the flap: up over the back and down below level, on the wanderer's clock (still while it glides)
          k.flap.array[i] = .55 + .8 * Math.sin(2 * Math.PI * b.hz * b.animT + b.phase);
        });
        k.geo.instanceCount = k.list.length;
        k.at.needsUpdate = k.sc.needsUpdate = k.flap.needsUpdate = true;
        const S = k.geo.boundingSphere.makeEmpty();
        for (const b of k.list) S.expandByPoint(b.position);
        S.radius += k.reach * scale * 1.5;   // (a wing's reach at the largest size)
        k.mesh.visible = k.list.length > 0;
      }
    },
    get count() { return all.length; },
    get all() { return all; },   // (every flier: the checks look at one)
  };
}
