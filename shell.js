// SHELL ENGINE: the figures as POLYGONS instead of an SDF.
//
// The composite engine draws one quad per figure and finds every part's surface per PIXEL. This draws the same
// parts as real geometry: CUTS along an axis -- a ring of N points per cut, triangles between neighbouring
// rings, the ends closed by poles -- which is what a lathe would turn, and what arch.js does for a vault. Once
// the shape is triangles the hardware does the work it is built for, early-z lives, no shader writes its own
// depth, and the surface normal is exact and free.
//
// WHAT IT DOES NOT REDO. It is not a second world: every part, pose and colour comes from the composite herd
// that owns it. The skeleton walk, the world mirror, the dyn/stat textures, the culling and the per-frame
// upload are all already there (composite.js); this reads the same texels the fragment shader reads and turns
// them into vertices. Switching engines changes which mesh draws and nothing else.
//
// ONE LATHE PER CHAIN, NOT PER PART. A body is not one cone: a crocodile is tail, body, neck, head and snout
// laid end to end, and two shells that each cover the joint land on the SAME surface and fight for the depth
// test -- which is what made the deer look see-through. So the parts that run end to end along one axis are
// found once per species (shellChains) and swept as ONE continuous mesh: `u` walks the whole chain, ring by
// ring, the profile following each part in turn and the colour crossing each joint as a short gradient. Limbs,
// horns, ears and garments are chains of their own: one main axis, the limbs separate.
//
// THE SURFACE. Each ring is a cut square to the local axis, centre and radius interpolated along the part;
// then TWO NEWTON STEPS put it on the true smooth union of the chain's own parts and the few parts of other
// chains it touches:
//     P <- P - n * smin(own, neighbour, k)
// The SDF is unit-gradient, so a step lands on the surface and the second cleans up the taper and the fillet.
// The normal is mixed by the same weights, which matters more than the silhouette -- without it two lobes
// still read as two, because the shading breaks at the seam. What the SDF pays per pixel, this pays per vertex.
//   Where two separate chains (a leg and a body) both cover one fillet, the higher slot sinks 1.5 mm so the
// depth test has a deterministic winner instead of a fight.
//
// THE PARTS THAT ARE NOT ROUND
//   * a TRIANGLE (an ear, a fin, a wing membrane) is a flat EXTRUSION: two flat faces a hair apart with a rim
//     band between them, the rim following the triangle's own edges -- an ear is a plate, not a pillow;
//   * a FLAT part (a garment slab: A.w < 0) is squashed to C.x of its width along the figure's forward, as the
//     SDF squashes it;
//   * a CUT (a garment's slab along its own axis, C.x..C.y metres from its A end: a skirt at waist and hem, a
//     hair cap at the hairline, a hat brim) clamps the rings onto the cutting planes, which leaves the flat
//     cap the "solid" cut asks for;
//   * a TUBE (a spindle drawn as a curve by the composite engine) is the capsule between its ends at its mean
//     girth, as the instanced engine draws it;
//   * a BONE (k < -.5) and a FACE MARK (an eye, a nostril: painted onto the head by the fragment shader, and
//     its A.w is the mark's reach, not a radius) are left out.
//
// LOD, on two axes. By DISTANCE (SHELL.lod: metres, rings, points round a cut) and by LENGTH: a swan's neck,
// an elephant's trunk, a cat's tail and a snake are long curved sweeps and want their rings spread along that
// length, where a stubby part is happy with a handful (LENGTHS). Nine grids, built once, most of them nearly
// empty; as the herd walks the figures it will draw, each chain goes into the bucket its distance and length
// pick, and a figure changes detail by moving between lists. Nothing is rebuilt when it does.
//
// STILL THE FRAGMENT SHADER'S, NOT HERE: patterns, the fabrics a part wears (dressAt), face marks and the outline.
import * as THREE from "three";
import { wgslFn, attribute, varying, uniform, vec3, vec4, float, positionGeometry, positionWorld, normalWorld, cameraPosition, cameraProjectionMatrix, cameraViewMatrix, cameraWorldMatrix } from "three/tsl";
import * as LIB from "./banner_wgsl.js";
import { sdRoundCone, texelFor, unpackAw, furAt, strandsAt } from "./composite_wgsl.js";
import { QUADS, onQuads } from "./outline.js";
import { fabricNode } from "./fabric.js";
import { LIGHT } from "./light.js";   // (the sun's direction: a statue's metal catches it)

export const MAXCH = 8;                      // parts in one chain at most (the shader reads them all per vertex)

// HOW MANY CUTS A CHAIN GETS follows how much it BENDS, not how long it is. A horn, a skirt or a leg bone is
// straight: a handful of cuts draws it exactly, and more is waste. A cat's tail, a swan's neck, an elephant's
// trunk and a snake turn through a large angle and need them spread along that turn. (A tube is one part but a
// curve of its own, so it always counts as bent.)
export const LENGTHS = [.5, 1, 2];           // ring multipliers for straight, bending and curling chains
// ...and a chain of MANY parts needs cuts along it even when it is straight: each span wants its own few, and
// the two caps want theirs, so the demand is the bend plus a share per part after the first.
const classOf = (curve, parts) => { const d = curve + .3 * Math.max(0, parts - 1); return d < .35 ? 0 : d < 1.2 ? 1 : 2; };

export const SHELL = {
  // [out to N times the chain's own GIRTH, rings, points round a cut]. THREE BANDS: the buckets belong to the
  // world's one pool of figures (composite.js), not to a herd, so their number costs a handful of draw calls
  // in total however many herds there are -- and a ladder of three keeps the triangles down where a coarser
  // one would spend them on figures nobody can see the rings of.
  lod: [[25, 16, 20], [70, 10, 12], [1e9, 6, 7]],
  blend: 1,                                  // the joints: Newton steps onto the smooth union with the neighbours
  near: 3,                                   // how many touching parts of OTHER chains a vertex blends with (0-4)
  thin: .012,                                // a triangle part's half-thickness in metres (an ear is a plate)
  mark: 2,                                   // how far a face mark stands proud of the face it lies on, in mm
  skin: .012,                                // how thick a cut shell's wall is (hair, a hood, a skirt), metres
  chain: 1,                                  // 0: one lathe per part again, to see what the chains are worth
  debug: 0,                                  // ?shelldebug=1: print how each species was split into chains
};

export function shellFromQuery(qp) {
  if (qp.has("shelllod")) SHELL.lod = qp.get("shelllod").split(";").map((g) => g.split(",").map(Number));
  if (qp.has("shellblend")) SHELL.blend = +qp.get("shellblend") ? 1 : 0;
  if (qp.has("shellchain")) SHELL.chain = +qp.get("shellchain") ? 1 : 0;
  if (qp.has("shellthin")) SHELL.thin = +qp.get("shellthin");
  if (qp.has("shellmark")) SHELL.mark = +qp.get("shellmark");
  if (qp.has("shellskin")) SHELL.skin = +qp.get("shellskin");
  if (qp.has("shelldebug")) SHELL.debug = 1;
  return SHELL;
}

// ---- what touches what, worked out once per species -------------------------------------------------------
// The skeleton poses the parts but never changes WHICH of them meet, so both the chains and the neighbour
// lists are worked out once, from the first posed figure of that species, and cached on the compiled part list.
//   They have to come from the POSED endpoints (herd.ends): a compiled part's own pA/pB are in its own frame,
// relative to its pivot, so "this part's B end sits on that part's A end" is not a question local coordinates
// can answer -- asking it there chains a head to a tail and sweeps a sail between them.
const isMark = (p) => p.k < -1.5;                 // a face mark (k = -2)
const isBone = (p) => p.k < -.5 && p.k > -1.5;   // rig structure (k = -1): posed, never drawn
const isTube = (p) => p.r2 < -1.5;               // a spindle: its own curve and girth, packed into r2
const PAT_TWIST = 19;                            // skeleton.js PAT.twist: a horn's spiral, drawn as a screw
// what the fillet may join: everything that is drawn as a solid, TUBES INCLUDED
const solidPart = (p) => !isMark(p) && !isBone(p) && (p.r2 >= 0 || isTube(p));
// ...and a tube's girth, as the capsule it is closest to (banner.js packs its far radius and bulge into r2)
function tubeGirth(p) {
  const v = -p.r2 - 2, bu = Math.floor(v / 4096 + 1e-4), r2 = (v - bu * 4096) * .001;
  return (p.r1 + r2) / 2 + bu * .001 * .7;
}
const girthOf = (p) => (isTube(p) ? tubeGirth(p) : Math.max(p.r1, p.r2, 0));
// the radius a part ENDS at -- a tube's is packed into r2 with its bulge, and reading it raw (a big negative)
// makes every gap test pass or fail on nonsense
const endR = (p) => {
  if (!isTube(p)) return Math.max(p.r2, 0);
  const v = -p.r2 - 2, bu = Math.floor(v / 4096 + 1e-4);
  return (v - bu * 4096) * .001;
};
const _ab = [0, 0, 0], _cd = [0, 0, 0];
function segDist(a, b, c, d) {          // distance between segment ab and segment cd (all [x, y, z])
  for (let i = 0; i < 3; i++) { _ab[i] = b[i] - a[i]; _cd[i] = d[i] - c[i]; }
  const dot = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
  const r = [a[0] - c[0], a[1] - c[1], a[2] - c[2]];
  const A = dot(_ab, _ab), B = dot(_ab, _cd), C = dot(_cd, _cd), D = dot(_ab, r), E = dot(_cd, r);
  const den = A * C - B * B;
  let s = den > 1e-9 ? Math.min(1, Math.max(0, (B * E - C * D) / den)) : 0;
  let t = C > 1e-9 ? Math.min(1, Math.max(0, (B * s + E) / C)) : 0;
  s = A > 1e-9 ? Math.min(1, Math.max(0, (B * t - D) / A)) : 0;
  let q = 0;
  for (let i = 0; i < 3; i++) { const v = r[i] + _ab[i] * s - _cd[i] * t; q += v * v; }
  return Math.sqrt(q);
}

// CHAINS: parts laid end to end along one axis, swept as one mesh. A part follows another when its A end sits
// on the other's B end (within the two radii) and the two axes point the same way -- a tail into a body, a body
// into a neck, a thigh into a shin. Garments (flat, or cut by a slab) stay on their own: their shape is a slab
// or a cut shell, not a continuation of the body under them.
function shellChains(parts, at) {
  if (parts._shellCh) return parts._shellCh;
  const n = parts.length;
  const seg = parts.map((p, i) => at(i));            // [[ax, ay, az], [bx, by, bz]] as the figure stands
  const len = seg.map(([a, b]) => Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]));
  // A BALL IS NOT A SEGMENT. A chain hands over from one part to the next and only its two ends are capped, so
  // a part with no length -- a head modelled as a sphere, a joint blob -- loses its own roundness inside one
  // and becomes a bulge on its neighbour (which is what left a horse's muzzle floating off its head). Those
  // stay their own shells, where a sphere is a sphere and the fillet joins it to what it touches.
  //   (Tried and reverted, 2026-09-24: letting a head ball sweep WITH its neck and muzzle, so that the head's
  // own surface shows the idle head-turn instead of only the horns and ears moving on a sphere that cannot.
  // The chain then carries the head's girth down the neck and out over the muzzle -- a triceratops' frill
  // disappeared inside the bulge, a horse's head came to a point. A ball has no axis, and a lathe is nothing
  // without one.)
  // A RUN OF TUBES IS ONE TAIL. Each link of an arc chain -- a dinosaur's tail, a hydra's neck -- is a tube
  // with a curve of its own, and left out of the chains they are drawn as that many separate spindles, each
  // capped: a stegosaur's tail was a string of beads. The sweep walks a tube span on its own curve (below),
  // so a run of them lathes as one shape. They chain only with each OTHER: a tube's profile is not something
  // a straight span can hand over to.
  // (a FLAT part sweeps only as a torso's cut, with other flat torso cuts: a person's torso is three -- shoulders,
  //  chest, hips -- turned as one flattened lathe, which is how it has a waist and still is one shape)
  const sweepable = parts.map((p, i) => solidPart(p) && (!p.flat || p.spine) && !p.clip
                                        && len[i] > .15 * Math.max(p.r1, girthOf(p), .001));
  const dir = seg.map(([a, b], i) => {
    const l = len[i] || 1;
    return [(b[0] - a[0]) / l, (b[1] - a[1]) / l, (b[2] - a[2]) / l];
  });
  const links = [];
  if (SHELL.chain) for (let i = 0; i < n; i++) {
    if (!sweepable[i]) continue;
    for (let j = 0; j < n; j++) {
      if (j === i || !sweepable[j]) continue;
      const p = parts[i], q = parts[j];
      // A LIMB IS NEVER A CONTINUATION OF THE TORSO. The torso's own cuts carry `spine`; they chain with each
      // other on generous terms (they are one shape by construction), and everything else chains on strict
      // ones. Without the separation a bear's torso reached down and swallowed a hind leg.
      if (!p.spine !== !q.spine || !p.flat !== !q.flat) continue;
      if (isTube(p) !== isTube(q)) continue;
      const gap = Math.hypot(seg[i][1][0] - seg[j][0][0], seg[i][1][1] - seg[j][0][1], seg[i][1][2] - seg[j][0][2]);
      // The two must MEET, which for a pair of body lobes means their end caps touch -- not that their end
      // POINTS nearly coincide. At .7 a giraffe's two torso lobes missed each other by 3% of a radius and
      // stayed two shells: the animal read as two balls. Their spheres touching is the honest test.
      if (gap > (p.spine ? 1 : .7) * (Math.max(endR(p), .001) + Math.max(q.r1, .001))) continue;
      // ...and j must start AHEAD of i, not behind it: on a fat animal "their caps touch" alone will happily
      // link the chest back to the rump and swallow what lies between them
      const ahead = (seg[j][0][0] - seg[i][1][0]) * dir[i][0] + (seg[j][0][1] - seg[i][1][1]) * dir[i][1] +
                    (seg[j][0][2] - seg[i][1][2]) * dir[i][2];
      if (ahead < -.35 * (Math.max(endR(p), .001) + Math.max(q.r1, .001))) continue;
      const cos = dir[i][0] * dir[j][0] + dir[i][1] * dir[j][1] + dir[i][2] * dir[j][2];
      // a limb bends hard at the hock and is still one limb: only a right angle or worse is a new direction.
      // (At .6 a horse's hind legs stayed two shells apiece while the front ones swept as one, which is what
      // made the back legs read differently from the front.)
      if (cos < (p.spine ? .1 : .25)) continue;
      // ...and a COLOUR boundary is not a continuation either. A lathe has one colour per cut, so chaining a
      // crocodile's pale belly plate into its flank paints the pale right round the body; the SDF keeps it
      // where the part actually is. Parts that do not share a colour stay separate shells, as they look --
      // except the TORSO's own cuts, which are one shape by construction and shade from rump to chest.
      const c1 = p.color, c2 = q.color;
      if (!(p.spine && q.spine) &&
          Math.abs(c1.r - c2.r) + Math.abs(c1.g - c2.g) + Math.abs(c1.b - c2.b) > .12) continue;
      links.push([gap - cos * .01, i, j]);
    }
  }
  links.sort((a, b) => a[0] - b[0]);
  const next = new Int32Array(n).fill(-1), prev = new Int32Array(n).fill(-1);
  for (const [, i, j] of links) {
    if (next[i] >= 0 || prev[j] >= 0) continue;
    let head = i, before = 1;
    while (prev[head] >= 0) { head = prev[head]; before++; if (head === j) break; }
    if (head === j) continue;                        // that would close a loop
    let tail = j, after = 1;
    while (next[tail] >= 0) { tail = next[tail]; after++; }
    if (before + after > MAXCH) continue;            // no chain longer than the shader reads
    next[i] = j; prev[j] = i;
  }
  const chains = [], of = new Int32Array(n).fill(-1);
  for (let i = 0; i < n; i++) {
    if (prev[i] >= 0) continue;                      // not the head of a chain
    if (isBone(parts[i])) continue;                  // posed, never drawn
    const c = [];
    for (let w = i; w >= 0; w = next[w]) { c.push(w); of[w] = chains.length; }
    chains.push(c);
  }
  // how big each chain is in the world: its detail should follow what it is worth on SCREEN, not how far away
  // the figure is. A nose and a body at the same distance are not the same problem.
  // HOW BIG IT IS ROUND, not how long. The cuts ROUND a chain are what its girth needs: a horn, an antler or
  // a leg bone is long and thin, and giving it as many points round its ring as a body gets is waste that a
  // frame pays for in every one of them. (How many cuts ALONG it is the bend's business, below.)
  const size = chains.map((c) => {
    let rad = 0, run = 0;
    for (const i of c) { rad = Math.max(rad, girthOf(parts[i])); run += len[i]; }
    // ...EXCEPT where the shape's detail is not its girth. A screw's ridges wind along the whole horn, and
    // measured by girth a horn is always tiny and always lands on the coarsest grid -- the spiral then comes
    // out as a handful of chunky kinks. Its own LENGTH is what the ridges need cuts along, so it asks for
    // detail by that instead, and still loses it in the distance like anything else.
    if (c.some((i) => parts[i].pat === PAT_TWIST)) return Math.max(2 * rad, .3 * run);
    return 2 * rad;
  });
  // ...and how far it turns, in radians, over its joints -- plus what its girth does, since a strong taper is
  // a turn of the surface even where the axis is straight
  const curve = chains.map((c) => {
    // a tube is a curve by itself -- but a LINK of an arc chain only carries its share of the arc
    let bend = 0;
    for (const i of c) bend += isTube(parts[i]) ? (c.length > 1 ? .45 : 1.4) : 0;
    // ...and a CUT SHELL is a curved layer however straight its axis: a cap of hair runs from the hairline over the
    // crown, and on a straight chain's handful of rings its outer wall was one cone from the hairline to a point,
    // deep inside the skull -- a head of hair that vanished a few metres off. It takes the curling grids.
    if (c.some((i) => parts[i].clip)) bend += 1.3;
    // ...and a SCREW turns all the way round every five radii: its rings are what the ridges are made of
    if (c.some((i) => parts[i].pat === PAT_TWIST)) bend += 1.2;
    for (let j = 0; j + 1 < c.length; j++) {
      const a = dir[c[j]], b = dir[c[j + 1]];
      bend += Math.acos(Math.min(1, Math.max(-1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2])));
    }
    for (const i of c) {
      const r1 = parts[i].r1, r2 = endR(parts[i]);
      bend += Math.atan2(Math.abs(r2 - r1), Math.max(len[i], 1e-4)) * .5;
    }
    return bend;
  });
  const nbOf = shellNeighbours(parts, of, seg);
  if (SHELL.debug) {                                 // ?shelldebug=1: what this species was split into
    console.log("shell cut parts: " + parts.map((p, i) => [p, i]).filter(([p]) => p.clip)
      .map(([p, i]) => `#${i} clip[${p.clip.map((v) => v.toFixed ? v.toFixed(3) : v).join(",")}] flat ${p.flat ?? 0} r ${p.r1.toFixed(3)}/${p.r2.toFixed(3)}`).join("  ") || "(none)");
    console.log("shell marks: " + chains.filter((c) => isMark(parts[c[0]])).map((c) =>
      `#${c[0]} r${parts[c[0]].r2.toFixed(3)} nb[${nbOf[c[0]].join(",")}]`).join("  "));
    console.log("shell chains for a figure of " + n + " parts:\n" + chains.map((c, ci) =>
      `  [${ci}] ` + c.map((i) => `#${i} r ${parts[i].r1.toFixed(3)}/${(parts[i].r2 < 0 ? parts[i].r2 : parts[i].r2).toFixed(3)}` +
        ` len ${len[i].toFixed(3)} k ${parts[i].k.toFixed(3)} at ${seg[i][0].map((v) => v.toFixed(2)).join(",")}`).join("  +  ")).join("\n"));
  }
  const out = { chains, of, size, curve, nb: nbOf };
  Object.defineProperty(parts, "_shellCh", { value: out, enumerable: false });
  return out;
}

// the few parts of OTHER chains a chain has to blend with -- a leg's top against the body, an arm against a
// shoulder. Inside a chain the sweep is continuous already and needs no fillet.
function shellNeighbours(parts, of, seg) {
  return parts.map((p, i) => {
    const out = [-1, -1, -1, -1];
    // a FACE MARK needs them as much as a limb does -- it is placed a hair INSIDE the head (the SDF paints it
    // there and depth never mattered), so a solid one has to know what to climb out of
    if (!solidPart(p) && !isMark(p)) return out;
    const near = [];
    for (let j = 0; j < parts.length; j++) {
      const q = parts[j];
      if (j === i || !solidPart(q) || of[j] === of[i]) continue;
      const k = isMark(p) ? Math.max(q.k, .05) : Math.max(p.k, q.k);
      if (k <= 1e-4) continue;
      const gap = segDist(seg[i][0], seg[i][1], seg[j][0], seg[j][1]) - girthOf(p) - girthOf(q);
      if (gap < k) near.push([gap, j]);
    }
    near.sort((x, y) => x[0] - y[0]);
    for (let m = 0; m < Math.min(4, near.length); m++) out[m] = near[m][1];
    return out;
  });
}

// ---- one grid per detail level ----------------------------------------------------------------------------
// (rings+1) x (divs+1) vertices holding (u, v); the seam is duplicated so v wraps without sharing vertices,
// and the pole rows stay in the grid (their quads collapse) to keep the code plain.
function shellGrid(rings, divs) {
  const geo = new THREE.InstancedBufferGeometry();
  const nu = rings + 1, nv = divs + 1, pos = new Float32Array(nu * nv * 3);
  // (z: the grid's own ring count, so a sweep can put a ring EXACTLY where it needs one -- a cut shell's lids)
  for (let i = 0, w = 0; i < nu; i++) for (let j = 0; j < nv; j++, w += 3) { pos[w] = i / rings; pos[w + 1] = j / divs; pos[w + 2] = rings; }
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const idx = [];
  for (let i = 0; i < rings; i++) for (let j = 0; j < divs; j++) {
    const a = i * nv + j, b = a + nv;
    idx.push(a, b, a + 1, a + 1, b, b + 1);
  }
  geo.setIndex(idx);
  geo.instanceCount = 0;
  return geo;
}

// ---- what a part WEARS (clothes.js; composite.js packDress has the layout) --------------------------------------
// A dressed part carries layers of sheet, outermost first, six static texels each. `layerIn` says how far inside one
// layer's piece a point lies, in metres to its nearest edge (> 0: the cloth is there): inside its stretch along the
// part (a hem DAGGED into rounded lobes if it says so), inside its arc round it, outside its opening -- a neckline
// dipping from its top edge toward the front and the back, or a window (an ellipse or a rounded slot) anywhere; a
// BAND is only the strip of that width inside its edges (a trim). `dressLift` lifts a point of the body by every
// layer over it; `dressAt` finds the outermost and gives its colour: the fabric's slot weights (fabric.js) mixed
// from the layer's four colours, a stitched line along its edges, pleats in the light, a darker lining inside.
const unpackRGB8 = wgslFn(`
  fn unpackRGB8(c: f32) -> vec3<f32> {
    let v = u32(max(c, 0.0) + 0.5);
    return vec3<f32>(f32((v >> 16u) & 255u), f32((v >> 8u) & 255u), f32(v & 255u)) / 255.0;
  }
`);
const dressCache = new Map();
const dressFns = (W, ST) => dressCache.get(W + "/" + ST) ?? dressCache.set(W + "/" + ST, makeDressFns(W, ST)).get(W + "/" + ST);
const makeDressFns = (W, ST) => {
  const layerIn = wgslFn(`
    fn layerIn(sTex: texture_2d<f32>, ls: i32, s: f32, th: f32, girth: f32, rad: f32) -> f32 {
      let L0 = texel(sTex, ls * ${ST});
      let L3 = texel(sTex, ls * ${ST} + 3);
      let L4 = texel(sTex, ls * ${ST} + 4);
      let L5 = texel(sTex, ls * ${ST} + 5);
      let fl = L3.z;
      let dags = floor(fl / 256.0);
      var hem = L0.y;
      if (dags > 0.5) {                          // rounded lobes along the lower edge, as deep as half a lobe is wide
        let lobe = 6.2831853 * max(girth, 0.01) / dags;
        let ph = fract(th * dags / 6.2831853) - 0.5;
        hem = hem - 0.5 * lobe * (1.0 - sqrt(max(1.0 - 4.0 * ph * ph, 0.0)));
      }
      var e = min(s - L0.x, hem - s);
      if (L0.w < 3.14) {
        var da = th - L0.z;
        da = da - 6.2831853 * floor((da + 3.1415927) / 6.2831853);
        e = min(e, (L0.w - abs(da)) * max(girth, 0.01));
      }
      let kind = L4.x;
      var eo = 1e3;                              // how far outside the opening (its edge is where a trim band runs)
      if (kind > 0.5 && kind < 5.5) {
        // A NECKLINE: a ball round the collar point (on the axis at L4.y) whose radius grows from the base L5.y by
        // the back's depth (L4.w) to the front's (L4.z) as the angle comes round to the front -- measured in 3D, so
        // it lies right on the flat shoulders' cap as on the chest below it
        let a = abs(th);
        var f = 0.0;
        if (kind < 1.5) { f = 0.5 + 0.5 * cos(a); }                                  // round
        else if (kind < 2.5) { f = sqrt(max(0.5 + 0.5 * cos(a), 0.0)); }             // scoop
        else if (kind < 3.5) { f = max(0.0, 1.0 - a / max(L5.x, 0.05)); }            // v
        else if (kind < 4.5) { f = 1.0 - smoothstep(L5.x - 0.1, L5.x + 0.1, a); }    // square
        else { f = sin(a) * sin(a); }                                                 // boat: widest at the shoulders
        let reach = L5.y + L4.w + (L4.z - L4.w) * f;
        eo = length(vec2<f32>(rad, s - L4.y)) - reach;
      } else if (kind > 5.5) {                   // a WINDOW round (angle, along)
        var dx = th - L4.y;
        dx = (dx - 6.2831853 * floor((dx + 3.1415927) / 6.2831853)) * max(girth, 0.01);
        let dy = s - L4.z;
        let ax = max(L5.x * max(girth, 0.01), 0.002);
        let ay = max(L5.y, 0.002);
        if (kind < 6.5) { eo = (length(vec2<f32>(dx / ax, dy / ay)) - 1.0) * min(ax, ay); }
        else {
          let rr = min(ax, ay);
          let qq = abs(vec2<f32>(dx, dy)) - vec2<f32>(ax, ay) + rr;
          eo = length(max(qq, vec2<f32>(0.0))) + min(max(qq.x, qq.y), 0.0) - rr;
        }
      }
      // A BAND is only a strip of its width: along its opening's edge if it has one (a neckline's trim), else along
      // all its edges (a hem's border is a band laid at the hem)
      if (L3.w > 0.0) {
        if (kind > 0.5) { return min(e, min(eo, L3.w - eo)); }
        return min(e, L3.w - e);
      }
      return min(e, eo);
    }
  `, [texelFor(W)]);
  const dressLift = wgslFn(`
    fn dressLift(sTex: texture_2d<f32>, head: vec4<f32>, s: f32, th: f32, girth: f32, rad: f32) -> f32 {
      let n = i32(head.y + 0.5);
      let l0 = i32(head.x + 0.5);
      var lift = 0.0;
      for (var k: i32 = 0; k < 6; k = k + 1) {
        if (k >= n) { break; }
        let ls = l0 + 2 * k;
        if (layerIn(sTex, ls, s, th, girth, rad) > 0.0) { lift = lift + texel(sTex, ls * ${ST} + 3).y; }
      }
      return lift;
    }
  `, [texelFor(W), layerIn]);
  const dressAt = wgslFn(`
    fn dressAt(sTex: texture_2d<f32>, fab: texture_2d_array<f32>, fsamp: sampler, head: vec4<f32>, s: f32, th: f32,
               dth: vec2<f32>, ds: vec2<f32>, girth: f32, px: f32, kind: f32, skin: vec3<f32>, axis: vec3<f32>,
               radial: vec3<f32>, relief: ptr<function, vec3<f32>>) -> vec4<f32> {
      let rad = length(radial);
      let n = i32(head.y + 0.5);
      let l0 = i32(head.x + 0.5);
      for (var k: i32 = 0; k < 6; k = k + 1) {
        if (k >= n) { break; }
        let ls = l0 + 2 * k;
        let e = layerIn(sTex, ls, s, th, girth, rad);
        if (e <= 0.0) { continue; }
        let L1 = texel(sTex, ls * ${ST} + 1);
        let L2 = texel(sTex, ls * ${ST} + 2);
        let L3 = texel(sTex, ls * ${ST} + 3);
        // the fabric's coordinates: round it a whole number of repeats (or by the girth), down it from the garment's top
        let per = max(L2.yz, vec2<f32>(0.001));
        let ku = select(max(girth, 0.01) / per.x, L3.x / 6.2831853, L3.x > 0.5);
        let uv = vec2<f32>(th * ku, (L2.w + s) / per.y);
        let w = textureSampleGrad(fab, fsamp, uv, i32(L2.x + 0.5), vec2<f32>(dth.x * ku, ds.x / per.y), vec2<f32>(dth.y * ku, ds.y / per.y));
        let c0 = unpackRGB8(L1.x);
        var c = c0 * max(1.0 - w.r - w.g - w.b, 0.0) + unpackRGB8(L1.y) * w.r + unpackRGB8(L1.z) * w.g + unpackRGB8(L1.w) * w.b;
        let fl = L3.z;
        let pleats = fl - 64.0 * floor(fl / 64.0);
        let wear = floor(fl / 64.0) - 4.0 * floor(fl / 256.0);
        if (pleats > 0.5) {
          // PLEATS: one field -- its valleys darken the cloth and tilt the normal, so a fold catches the light
          let ph = pleats * th;
          c = c * (1.0 - 0.14 * (0.5 - 0.5 * cos(ph)));
          let fine = 1.0 - smoothstep(0.12, 0.3, px * pleats / (6.2832 * max(girth, 0.01)));
          *relief = *relief + cross(normalize(radial), axis) * (-0.018 * 0.5 * pleats * sin(ph) * fine / max(girth, 0.01));
        }
        if (wear > 0.5) { c = c * (1.0 - 0.06 * (fract(sin(dot(floor(uv * 3.0), vec2<f32>(12.9898, 78.233))) * 43758.5453) - 0.5)); }
        if (e < px * 1.4 + 0.0015) { c = c * 0.7; }              // the stitched edge: a hem, a neckline, a seam
        if (kind > 0.5 && kind < 1.5) { c = c * 0.72; }          // the lining
        return vec4<f32>(c, 1.0);
      }
      return vec4<f32>(skin, 0.0);
    }
  `, [texelFor(W), layerIn, unpackRGB8]);
  return { layerIn, dressLift, dressAt };
};

// ---- the vertex stage -------------------------------------------------------------------------------------
// row 0 = the point in VIEW space, row 1 = its world normal, row 2 = (colour, the girth here),
// row 3 = (the point in the PART's own frame, the part's flags) -- which is all a pattern needs: how far along
// the axis it lies, at what angle round it, and how far from it (banner_wgsl patternAt reads exactly that)
const shellPoint = (W, ST, viewSpace) => wgslFn(`
  fn shellPoint(tex: texture_2d<f32>, sTex: texture_2d<f32>, uv: vec2<f32>, nr: f32, part: vec4<f32>,
                ch: vec4<f32>, ch2: vec4<f32>, nb: vec4<f32>,
                view: mat4x4<f32>, invView: mat4x4<f32>, blend: f32, thin: f32, lift: f32, skin: f32) -> mat4x4<f32> {
    let cnt = max(1, i32(part.x + 0.5));
    let base = i32(part.y + 0.5);
    var sl = array<f32, 8>(ch.x, ch.y, ch.z, ch.w, ch2.x, ch2.y, ch2.z, ch2.w);

    var CA = array<vec4<f32>, 8>();      // the chain's parts, read once: A, B and (r1, k, needC, slot)
    var CB = array<vec4<f32>, 8>();
    var CK = array<vec4<f32>, 8>();
    var CC = array<vec4<f32>, 8>();      // ...and the bend point, for the spans that are tubes
    for (var j: i32 = 0; j < 8; j = j + 1) {
      if (j >= cnt) { break; }
      let s = i32(sl[j] + 0.5);
      CA[j] = texel(tex, s * 3);
      CB[j] = texel(tex, s * 3 + 1);
      let ua = unpackAw(CA[j].w);
      CK[j] = vec4<f32>(ua.x, ua.y, ua.z, f32(s));
      if (CB[j].w < -1.5) { CC[j] = texel(tex, s * 3 + 2); }
    }
    let C4 = texel(tex, i32(sl[0] + 0.5) * 3 + 2);
    let sqz = CK[0].x < 0.0;
    // A FACE MARK (an eye, a nostril, a mouth) is a small pill lying ON the head's surface. The SDF paints it
    // there; here it is simply drawn -- but its A.w carries the mark's REACH (how far its relief spreads), not
    // a radius, so its girth comes from B.w at both ends, or it is a balloon.
    let mark = part.w > 0.5;

    var P = CA[0].xyz;
    var N = vec3<f32>(0.0, 1.0, 0.0);
    var girthHere = 0.02;                // the part's girth at this point (patterns scale by it)
    // WHERE A PATTERN SITS IS A PROPERTY OF THE MESH, not of the pose. Taken from the posed ends (partLocal),
    // the frame turns with the part -- and a swinging leg then drags its stripes through the coat. These are
    // the sweep's own numbers: how far ALONG the chain the ring is, and where round it this vertex lies. They
    // are the same whatever the animal is doing.
    var loc = vec3<f32>(0.0);
    var kind = 0.0;                      // 0 the outer surface, 1 the inside of a shell, 2 a cut's flat face
    var squash = 1.0;                    // a flat part's squash (cloth reads it), 1 for a round one
    // a face mark wears its IRIS colour (the second static texel): the first is the darkened rim the SDF
    // uses under the painted iris, and on its own it is invisible against a head
    var col = texel(sTex, i32(sl[0] + 0.5) * ${ST}).xyz;
    if (mark) { let ir = texel(sTex, i32(sl[0] + 0.5) * ${ST} + 1).xyz; if (dot(ir, ir) > 1e-6) { col = ir; } }
    var sink = 0.0;
    var ringI: i32 = 0;                  // the part of the chain this vertex's ring lies on (a dressed part wears its own)
    var isCut = false;                   // ...and whether the part is a cut shell (standing cloth: no lift)

    let tube = CB[0].w < -1.5;             // a spindle: a curve from A to B through C, with its own girth
    let rb = select(vec2<f32>(0.0), tubeUnpack(CB[0].w), tube);

    if (mark) {
      // A FACE MARK IS AN ELLIPSE ON THE FACE, not a pill. The composite engine writes it as centre (A), half
      // WIDTH (B - A) and half HEIGHT (C - A), all three already laid on the head's surface, with A.w the
      // reach its relief paints over and B.w a STYLE CODE -- which is why reading B.w as a radius drew
      // nothing: it is not a size at all. Drawn as a thin plate over that ellipse, which is the "flat surface
      // to paint on" the shape asks for, it is an eye, a brow or a mouth.
      let c0 = CA[0].xyz;
      let uu = CB[0].xyz - c0;
      let vv = C4.xyz - c0;
      var nrm = cross(uu, vv);
      let ln = length(nrm);
      nrm = select(vec3<f32>(0.0, 0.0, 1.0), nrm / ln, ln > 1e-12);
      // it must face OUT of the head: the first neighbour tells which way that is
      var outw = nrm;
      for (var j: i32 = 0; j < 4; j = j + 1) {
        if (nb[j] < -0.5 && nb[j] > -1.5) { continue; }
        let sj = i32(select(nb[j], -nb[j] - 2.0, nb[j] < -1.5) + 0.5);
        let QA = texel(tex, sj * 3);
        if (dot(nrm, c0 - QA.xyz) < 0.0) { outw = -nrm; }
        break;
      }
      let ang = uv.y * 6.2831853;
      let rad2 = select(uv.x / 0.5, (1.0 - uv.x) / 0.5, uv.x > 0.5);   // 0 at the centre, 1 at the rim, both halves
      let face = select(1.0, -1.0, uv.x > 0.5);
      P = c0 + uu * (rad2 * cos(ang)) + vv * (rad2 * sin(ang)) + outw * (0.0006 * face + 0.0012);
      N = outw;
      // an EYE is not one colour: the composite engine paints a dark rim, the iris inside it and a pupil in
      // the middle (its flags say which, and its second static texel carries the iris). The plate shades the
      // same way from its own rim inwards, which is all a flat surface has to do to read as an eye.
      let f0 = texel(sTex, i32(sl[0] + 0.5) * ${ST});
      let fl = f0.w;
      let hasIris = (fl - 2.0 * floor(fl / 2.0)) > 0.5;
      if (hasIris) {
        if (rad2 > 0.72) { col = f0.xyz; }
        else if (rad2 < 0.4) { col = f0.xyz * 0.45; }
      }
    } else if (CB[0].w < 0.0 && !tube) {
      // A TRIANGLE PART, as a thin flat extrusion: front face, rim band, back face.
      //   THE RIM IS THE TRIANGLE'S OWN BOUNDARY, walked by PERIMETER rather than by angle from the centroid.
      // An angle sweep traces the right outline but lands on the corners only by luck, so every corner is cut
      // off by a chord -- and two triangles that share an edge (a wing's membranes) then leave a gap along it.
      // Here the cuts are shared out between the three edges as whole steps, so a corner always falls ON a cut
      // and a shared edge comes out as the same straight line from either side.
      // A MEMBRANE IS FATTER THAN ITS TRIANGLE. The SDF draws it as the Minkowski sum of the triangle with a
      // sphere of radius r1 -- r past every edge -- so two plates that share an edge (a ceratopsian's three
      // frill panels, a wing's membranes) overlap by 2r there and the join cannot be seen. Drawn as the bare
      // triangle each plate stopped exactly on the shared edge and the pair left a slit with the sky behind
      // it.
      //   THE OFFSET PINCHES BACK TO NOTHING AT THE CORNERS. Pushed out all the way round -- mitred, or on
      // the SDF's own corner arc -- two plates that meet at a POINT (the three panels all reach the frill's
      // apex) each carry their corner out in their OWN plane, which is a different direction for each, and
      // the apex came out as a step with a notch beside it. Held back over the last r of each edge, both
      // plates end exactly on the corner they share: the edges still overlap where the seam runs, and the
      // corner is a corner.
      //   THE RIM IS THE TRIANGLE'S OWN BOUNDARY, walked by PERIMETER rather than by angle from the centroid.
      // An angle sweep traces the right outline but lands on the corners only by luck, so every corner is cut
      // off by a chord -- and a shared edge then leaves a gap along it. The cuts are shared out between the
      // three edges as whole steps, so a corner always falls ON a cut and a shared edge comes out as the same
      // straight line from either side.
      let a = CA[0].xyz; let b = CB[0].xyz; let c = C4.xyz;
      let rIn = abs(CK[0].x);
      let g = (a + b + c) / 3.0;
      var nrm = cross(b - a, c - a);
      let ln = length(nrm);
      nrm = select(vec3<f32>(0.0, 1.0, 0.0), nrm / ln, ln > 1e-9);
      let L0 = length(b - a);
      let L1 = length(c - b);
      let L2 = length(a - c);
      let per = max(L0 + L1 + L2, 1e-9);
      let dv = max(part.z, 3.0);            // the cuts round this instance's grid
      var n0 = max(1.0, floor(dv * L0 / per + 0.5));
      var n1 = max(1.0, floor(dv * L1 / per + 0.5));
      if (n0 + n1 > dv - 1.0) { n0 = max(1.0, floor((dv - 1.0) * L0 / (L0 + L1) + 0.5)); n1 = max(1.0, dv - 1.0 - n0); }
      let n2 = max(1.0, dv - n0 - n1);
      // which cut this vertex is on -- the last one IS the first: the ring closes on corner a. (Taken as the third edge's
      // end it carried THAT edge's outward offset, the first cut the first edge's: two points a hair apart, and the
      // fan from the middle left a sliver of nothing between them, from the plate's centre out to its first corner --
      // a dark crack across every wing membrane, ear and fin)
      var j = uv.y * dv;
      if (j > dv - 0.5) { j = 0.0; }
      var rim = a;
      var edge = b - a;
      var ed = 0.0;                         // how far along this edge, and how long it is
      var edL = L0;
      if (j <= n0) { let sE = j / n0; rim = mix(a, b, sE); edge = b - a; ed = sE * L0; edL = L0; }
      else if (j <= n0 + n1) { let sE = (j - n0) / n1; rim = mix(b, c, sE); edge = c - b; ed = sE * L1; edL = L1; }
      else { let sE = (j - n0 - n1) / n2; rim = mix(c, a, sE); edge = a - c; ed = sE * L2; edL = L2; }
      var out = normalize(cross(nrm, normalize(select(vec3<f32>(1.0, 0.0, 0.0), edge, dot(edge, edge) > 1e-12))));
      out = select(out, -out, dot(out, rim - g) < 0.0);
      // ...let go over the last r of the edge, but not all the way: a corner still carries a little of the
      // offset (two plates meeting there overlap by that much), and the outline keeps its shape instead of
      // dipping into a notch between two bulged edges.
      let hold = max(min(rIn, edL / 3.0), 1e-6);
      rim = rim + out * rIn * mix(0.4, 1.0, clamp(min(ed, edL - ed) / hold, 0.0, 1.0));
      // ...and it is as THICK as the SDF's own rounding, which is r: the two plates that meet along a shared
      // edge then overlap in 3D, and the wedge between their planes -- which a pair of wafers left open as a
      // notch at the top of a frill -- is filled from inside. (Floored at SHELL.thin so a plate with no
      // rounding of its own is still a plate, capped by its own size so nothing becomes a brick.)
      let th = clamp(rIn, thin, 0.06 * per / 3.0);
      if (uv.x < 0.45) {                   // the front face, flat
        P = mix(g, rim, uv.x / 0.45) + nrm * th;
        N = nrm;
      } else if (uv.x > 0.55) {            // the back face, flat
        P = mix(g, rim, (1.0 - uv.x) / 0.45) + nrm * (-th);
        N = -nrm;
      } else {                             // the rim
        P = rim + nrm * (th - 2.0 * th * (uv.x - 0.45) / 0.1);
        N = out;                           // (the rim's own outward direction, already squared to the plate)
      }
      girthHere = max(per / 6.0, 0.004);
      let pq = P - g;
      let pu = normalize(select(vec3<f32>(1.0, 0.0, 0.0), b - a, dot(b - a, b - a) > 1e-12));
      loc = vec3<f32>(dot(pq, pu), dot(pq, cross(nrm, pu)), dot(pq, nrm));   // the plate's own frame
    } else {
      // A CHAIN OF ROUND CONES, swept as one lathe: u walks the whole chain, with half a part's worth of rings
      // at each end for the caps -- x < 0 is the first part's A cap, x > cnt the last part's B cap.
      // THE ENDS GET THEIR OWN SHARE OF THE CUTS. Spreading them evenly over (cnt + 1) units gives each cap
      // half a unit, so a four-part body left under one ring per cap and the ends came to a cone. A fifth of
      // the cuts goes to each cap whatever the chain's length; the rest walk its spans.
      let capF = 0.2;
      var x = 0.0;
      if (uv.x < capF) { x = (uv.x / capF - 1.0) * 0.5; }
      else if (uv.x > 1.0 - capF) { x = f32(cnt) + ((uv.x - (1.0 - capF)) / capF) * 0.5; }
      else { x = (uv.x - capF) / (1.0 - 2.0 * capF) * f32(cnt); }
      let i = clamp(i32(floor(x)), 0, cnt - 1);
      ringI = i;
      // the cuts are not evenly spaced along a span: the sweep bends and changes girth at the JOINTS, so the
      // rings gather there and thin out along the straight middle (the derivative runs from 0.4 to 1.6).
      let tl = clamp(x - f32(i), 0.0, 1.0);
      let t = tl - 0.6 * sin(6.2831853 * tl) / 6.2831853;
      // THE CHAIN'S OWN PROFILE. Away from a joint a part keeps exactly the shape it was given -- its own
      // centre line and its own girth. Only ACROSS a joint are the two profiles blended: each part's line is
      // carried a little way into its neighbour's span and the two are averaged, so the hand-over is smooth in
      // position, in direction and in girth, and no crease is left. (A spline through the joints, which is
      // what this was first, carries a chest's girth all the way down a neck -- and a mane lying along that
      // neck disappears inside it.)
      let ai = CA[i].xyz;
      let bi = CB[i].xyz;
      let axis = bi - ai;
      let Li = max(length(axis), 1e-4);
      var cen = mix(ai, bi, t);
      // a mark is drawn a little wider than its own girth so that it clears the surface it lies on: the SDF
      // PAINTS it there and can cover any area it likes, a solid has to stand proud to be seen at all
      // A MARK IS DRAWN THE SIZE IT WAS PAINTED. The SDF paints an eye or a mouth over the area its RELIEF
      // reaches, which is what A.w carries (1.2 x its half length or its radius) -- that is the eye you see in
      // the composite engine, and it is two to three times the little pill the rig gives it. A solid pill at
      // its own girth is a few millimetres and vanishes into the face; drawn at the painted size it reads.
      var rr = mix(abs(CK[i].x), CB[i].w, t);
      // a SPHERE has no length at all (a horse's head is one), and dividing by it collapses the frame and the
      // part with it -- the head vanished and its muzzle was left floating in front of the neck
      // A BALL IN THE MIDDLE OF A CHAIN (a head between a neck and a muzzle) has no axis of its own, and its
      // own zero-length one would collapse the frame: it takes the CHAIN's direction instead.
      let chainDir = CB[cnt - 1].xyz - CA[0].xyz;
      let fallback = select(vec3<f32>(0.0, 1.0, 0.0), normalize(chainDir), dot(chainDir, chainDir) > 1e-10);
      var dir = select(fallback, axis / Li, dot(axis, axis) > 1e-10);
      var slope = clamp((CB[i].w - abs(CK[i].x)) / Li, -4.0, 4.0);
      // At a joint the two parts hand over: the sweep reaches the JOINT's own point and girth (the average of
      // the two ends that meet there) and leaves again from it, so both spans agree at the hand-over and the
      // shape between them is smooth. It does NOT extrapolate the neighbour's cone into this span -- a head
      // between a neck and a muzzle would be squeezed by both of them and come away from its own muzzle.
      let tubeI = CB[i].w < -1.5;          // THIS span's own curve (a chain may be all tubes: a tail)
      if (i + 1 < cnt && !tubeI && CB[i + 1].w >= -1.5) {   // the far joint
        let w = smoothstep(0.55, 1.0, t);
        if (w > 0.0) {
          let a2 = CA[i + 1].xyz;
          let b2 = CB[i + 1].xyz;
          let L2 = max(length(b2 - a2), 1e-4);
          cen = mix(cen, mix(bi, a2, 0.5), w);
          rr = mix(rr, mix(CB[i].w, abs(CK[i + 1].x), 0.5), w);
          dir = normalize(mix(dir, (b2 - a2) / L2, w * 0.5));
          slope = mix(slope, (CB[i + 1].w - abs(CK[i + 1].x)) / L2, w * 0.5);
        }
      }
      if (i > 0 && !tubeI && CB[i - 1].w >= -1.5) {         // ...and the near one
        let w = 1.0 - smoothstep(0.0, 0.45, t);
        if (w > 0.0) {
          let a0 = CA[i - 1].xyz;
          let b0 = CB[i - 1].xyz;
          let L0 = max(length(b0 - a0), 1e-4);
          cen = mix(cen, mix(b0, ai, 0.5), w);
          rr = mix(rr, mix(CB[i - 1].w, abs(CK[i].x), 0.5), w);
          dir = normalize(mix(dir, (b0 - a0) / L0, w * 0.5));
          slope = mix(slope, (CB[i - 1].w - abs(CK[i - 1].x)) / L0, w * 0.5);
        }
      }
      // A TUBE follows its own curve: the quadratic through C, with the girth the engine gives it (a tail
      // drawn as a straight capsule at mean girth -- which is all the banner engines can do -- is far too
      // thick at the tip, and this is a lathe: the true profile costs nothing here)
      let rbI = select(rb, tubeUnpack(CB[i].w), tubeI);
      let cur = bezier3(CA[i].xyz, CC[i].xyz, CB[i].xyz, t);
      var tan = 2.0 * (1.0 - t) * (CC[i].xyz - CA[i].xyz) + 2.0 * t * (CB[i].xyz - CC[i].xyz);
      tan = select(vec3<f32>(0.0, 1.0, 0.0), normalize(tan), dot(tan, tan) > 1e-10);
      let rA = select(rr, tubeR(t, abs(CK[i].x), rbI), tubeI);
      let rB = rA;
      var ax = select(dir, tan, tubeI);
      // the sweep's direction must never flip: where two parts of a chain overlap, the blended direction can
      // point backwards, the rings then wind the other way, and that stretch of the shell faces inward --
      // invisible under backface culling, so you look through the trunk at the leg behind it.
      let fwdChain = CB[cnt - 1].xyz - CA[0].xyz;
      if (dot(ax, fwdChain) < 0.0 && dot(fwdChain, fwdChain) > 1e-10) { ax = -ax; }
      // THE FRAME MUST BE THE CHAIN'S, not the ring's: a frame built from each part's own axis turns by a
      // different amount at every joint, and the rings stop lining up -- the strip between them then spans the
      // chain in long spikes. So one reference across the whole chain, squared to the local axis per ring.
      let span = CB[cnt - 1].xyz - CA[0].xyz;
      let chainAx = select(ax, normalize(span), dot(span, span) > 1e-8);
      // THE ROLL REFERENCE IS THE FIGURE'S OWN SIDE, not the world's up. Squared against the world up, the
      // frame FLIPS the moment a limb's axis passes 26 degrees off vertical (that select) -- so a sleeve's
      // checks jumped a quarter turn round the arm mid-stride -- and it rolls steadily as the limb tilts the
      // rest of the time, which slid them. The figure's side stays square to a limb that swings fore and aft,
      // so the pattern sits still on it however the limb moves. (It is also the camera's up here, not the
      // world's, whenever the ends are kept in view space: the frame turned as the camera walked round.)
      let bi3 = base * 3;
      let rt0 = texel(tex, bi3).xyz;
      let rt1 = texel(tex, bi3 + 1).xyz;
      var fwB = rt1 - rt0;
      fwB = select(vec3<f32>(1.0, 0.0, 0.0), normalize(fwB), dot(fwB, fwB) > 1e-10);
      let upB = ${viewSpace ? "(view * vec4<f32>(0.0, 1.0, 0.0, 0.0)).xyz" : "vec3<f32>(0.0, 1.0, 0.0)"};
      var sideB = cross(upB, fwB);
      sideB = select(vec3<f32>(0.0, 0.0, 1.0), normalize(sideB), dot(sideB, sideB) > 1e-8);
      var rf = sideB - chainAx * dot(sideB, chainAx);
      // ...unless the part runs ALONG that side (a horn, a spread wing, an outstretched arm): there the
      // figure's forward is the one square to it
      if (dot(rf, rf) < 0.04) { rf = fwB - chainAx * dot(fwB, chainAx); }
      rf = select(vec3<f32>(1.0, 0.0, 0.0), normalize(rf), dot(rf, rf) > 1e-8);
      var t1 = rf - ax * dot(rf, ax);
      t1 = select(normalize(cross(vec3<f32>(0.0, 1.0, 0.0), ax) + vec3<f32>(1e-4, 0.0, 0.0)), normalize(t1), dot(t1, t1) > 1e-8);
      let t2 = cross(ax, t1);
      let ang = uv.y * 6.2831853;
      let rad = t1 * cos(ang) + t2 * sin(ang);
      // how far along the whole chain this ring lies (so anything that runs down a part -- a pattern, a
      // screw's ridge -- runs unbroken over its joints)
      var along = 0.0;
      for (var q: i32 = 0; q < 8; q = q + 1) {
        if (q >= i) { break; }
        along = along + length(CB[q].xyz - CA[q].xyz);
      }
      along = along + t * length(CB[i].xyz - CA[i].xyz);
      if (x < 0.0) { along = x * 2.0 * rA; }
      if (x > f32(cnt)) { along = along + (x - f32(cnt)) * 2.0 * rA; }
      // A SCREW IS A SHAPE, not a shade. A horn flagged with the twist pattern (a blackbuck's spiral, a
      // ram's curl) had its ridges painted on a smooth cone: from the side the outline was a straight taper
      // whatever the light did. The ring turns between cuts instead -- its radius rises and falls with the
      // SHADER'S OWN PHASE (one turn per five radii, banner_wgsl pattern 19), so the ridge the light draws and
      // the ridge the silhouette shows are the same ridge. Costs nothing but the cuts it wants: a twisted
      // chain asks for the curling class, and near the camera that is 32 rings.
      let fl = max(texel(sTex, i32(CK[0].w + 0.5) * ${ST}).w, 0.0);
      let patH = floor((fl - 256.0 * floor(fl / 256.0)) / 8.0);
      let screw = patH > 18.5 && patH < 19.5;
      let rG = max(abs(CK[0].x), 0.004);                  // the pitch is the horn's own girth, as the shader reads it
      let ph = 6.2831853 * along / (${LIB.TWIST_PITCH}.0 * rG) + ang;
      let amp = select(0.0, 0.35, screw);
      let rS = rA * (1.0 + amp * cos(ph));
      let dRdA = -rA * amp * sin(ph);                     // ...round the ring
      let dRds = select(slope, 0.0, tubeI) - rA * amp * sin(ph) * 6.2831853 / (${LIB.TWIST_PITCH}.0 * rG);   // ...and along it
      // A FLAT PART'S CAPS (composite capCode, in its third texel's w): each only as tall as its share of the
      // radius and as square as the exponent -- a superellipse, not a hemisphere. A person's torso ends in a
      // low, squared cap, which is the shoulders: a round cap as wide as the shoulders would stand as tall as
      // it is wide and swallow the neck (that is why there was once a second shape across the top, the yoke).
      var capH = 1.0;
      var capE = 2.0;
      // (the A cap is the chain's first part's, the far one its last part's)
      let CL = texel(tex, i32(sl[cnt - 1] + 0.5) * 3 + 2);
      let cw = select(CL.w, C4.w, x < 0.0);
      if (sqz && cw > 0.5) {
        capE = max(floor(cw / 16384.0) * 0.1, 1.2);
        let ab = cw - 16384.0 * floor(cw / 16384.0);
        capH = max(select(floor(ab / 128.0), ab - 128.0 * floor(ab / 128.0), x < 0.0) * 0.01, 0.05);
      }
      let capX = 2.0 / capE;                   // (the superellipse's own exponent on the angle's sine and cosine)
      let capN = 2.0 * (capE - 1.0) / capE;    // ...and on its normal's
      if (x < 0.0) {                       // the A cap: a hemisphere on the first knot
        // by ANGLE, not by height up the axis: even steps in the height put nearly all the rings round the
        // equator and none near the pole, and a big round body (an elephant, a whale) ends in a point.
        let th = clamp(x * 2.0 + 1.0, 0.0, 1.0) * 1.5707963;
        let sn = max(sin(th), 0.0);
        let cs = max(cos(th), 0.0);
        P = CA[0].xyz + rad * (rS * pow(sn, capX)) - ax * (capH * rS * pow(cs, capX));   // (a mark's girth is its own, above)
        N = normalize(rad * pow(sn, capN) - ax * (pow(cs, capN) / capH));
      } else if (x > f32(cnt)) {           // ...and the far end's, on the last
        let th = clamp((x - f32(cnt)) * 2.0, 0.0, 1.0) * 1.5707963;
        let sn = max(sin(th), 0.0);
        let cs = max(cos(th), 0.0);
        let rE = rS * rB / max(rA, 1e-6);
        P = CB[cnt - 1].xyz + rad * (rE * pow(cs, capX)) + ax * (capH * rE * pow(sn, capX));
        N = normalize(rad * pow(cs, capN) + ax * (pow(sn, capN) / capH));
      } else {
        P = select(cen, cur, tubeI) + rad * rS;
        // THE NORMAL IS THE SURFACE'S OWN CROSS PRODUCT: how the point moves round the ring against how it
        // moves along the sweep. For a plain cone that is exactly the old rad - ax * slope (the girth
        // changes along the sweep, so the surface leans); a screw's ridges lean it round the ring as well.
        let vv = t2 * cos(ang) - t1 * sin(ang);
        let dPdA = vv * rS + rad * dRdA;
        let dPds = ax + rad * dRds;
        N = normalize(cross(dPdA, dPds));
      }
      girthHere = max(rS, 0.004);
      loc = vec3<f32>(along, rA * cos(ang), rA * sin(ang));
      // the colour is the part this ring belongs to, crossing each joint as a short gradient
      col = texel(sTex, i32(CK[i].w + 0.5) * ${ST}).xyz;
      if (t > 0.8 && i + 1 < cnt) {
        col = mix(col, texel(sTex, i32(CK[i + 1].w + 0.5) * ${ST}).xyz, (t - 0.8) * 2.5);
      } else if (t < 0.2 && i > 0) {
        col = mix(col, texel(sTex, i32(CK[i - 1].w + 0.5) * ${ST}).xyz, (0.2 - t) * 2.5);
      }

      if (sqz && C4.x > 1e-3) {
        // a flat part: squashed to C.x of its width along the figure's forward, square to its own axis
        let r0 = texel(tex, base * 3).xyz;
        let r1 = texel(tex, base * 3 + 1).xyz;
        var fwd = r1 - r0;
        fwd = select(vec3<f32>(0.0, 0.0, 1.0), normalize(fwd), dot(fwd, fwd) > 1e-10);
        var w = fwd - ax * dot(fwd, ax);
        // A plate whose own axis runs along the figure's forward -- a belly plate, a back plate -- has no
        // squash direction in the forward: the SDF falls back to the VIEW's z there, which is honest for a 2D
        // silhouette and nonsense for a solid (the plate would face the camera and swing as it moves). It lies
        // flat against the body instead: squashed along the world's up, square to its own axis.
        let upW = ${viewSpace ? "(view * vec4<f32>(0.0, 1.0, 0.0, 0.0)).xyz" : "vec3<f32>(0.0, 1.0, 0.0)"};
        var wUp = upW - ax * dot(upW, ax);
        wUp = select(t1, normalize(wUp), dot(wUp, wUp) > 1e-8);
        let lw = length(w);
        w = select(wUp, w / lw, lw > 1e-4);
        let off = P - cen;
        P = cen + off - w * (dot(off, w) * (1.0 - C4.x));
        N = normalize(N + w * (dot(N, w) * (1.0 / max(C4.x, 0.05) - 1.0)));
        squash = C4.x;
      } else if (blend > 0.5 && !mark) {
        // THE FILLET, and only the fillet. A vertex sits on its chain's own swept surface; where another chain
        // comes within its blend radius it bulges out by at most k/4, which is the smooth union's fillet and
        // nothing more. It must NOT be pushed out to the union itself: a horse's neck would then swell out to
        // the surface of the mane lying along its crest and swallow it, and the crocodile's flank would swell
        // over its belly. Where this vertex is INSIDE a neighbour it is covered by that neighbour's own shell,
        // so it is left where it is.
        //   The normal is mixed by the same proximity, which is what makes the seam read as one surface, and
        // the chain that gives way sinks a hair so two fillets can never fight for the depth test.
        var bulge = 0.0;
        var nn = vec3<f32>(0.0);
        var wsum = 0.0;
        var hi = 0.0;                        // the strongest blend with a chain this one gives way to
        for (var j: i32 = 0; j < 4; j = j + 1) {
          if (nb[j] > -1.5 && nb[j] < -0.5) { continue; }   // (-1: no neighbour there)
          let give = nb[j] < -1.5;                          // negative: that chain owns the fillet, this one sinks
          let sj = i32(select(nb[j], -nb[j] - 2.0, give) + 0.5);
          let QA = texel(tex, sj * 3);
          let QB = texel(tex, sj * 3 + 1);
          let qua = unpackAw(QA.w);
          // a TUBE neighbour (a trunk, a tail, an antler) is met at its mean girth: without this it is not
          // joined to the base it grows out of at all, and the two read as separate pieces
          var qrA = abs(qua.x);
          var qrB = QB.w;
          if (QB.w < -1.5) { let g = tubeUnpack(QB.w); let m = (qrA + g.x) * 0.5 + g.y * 0.7; qrA = m; qrB = m; }
          else if (QB.w < 0.0) { continue; }
          // The fillet is THIS part's blend radius, not the wider of the two: a mane asks for a .3 m blend, and
          // taking the wider one bulges a whole neck by a quarter of that and swallows the mane. But where a
          // part runs into something much FATTER than itself -- a neck into a head, a tail into a rump -- its
          // own blend is far too small for the step, and the joint reads as a shoulder. There it takes half of
          // the fat one's, which rounds the step without touching anything a thin part lies on.
          var kk = max(CK[i].y, 0.004);
          if (qrA > rr * 1.5) { kk = max(kk, qua.y * 0.5); }
          let d = sdRoundCone(P, QA.xyz, QB.xyz, qrA, qrB);
          if (d > kk) { continue; }
          let hh = max(kk - max(d, 0.0), 0.0) / kk;
          // BOTH sides build the fillet -- a gap between two parts is bridged by k/4 from each of them, and
          // suppressing one side leaves a horse's muzzle floating off its head. Giving way decides the depth
          // tie-break (the 2 mm sink below), not whether the surface is there.
          if (d >= 0.0) { bulge = max(bulge, hh * hh * kk * 0.25); }
          let w = max(1.0 - abs(d) / (kk + 0.02), 0.0) * 0.5;
          nn = nn + capsuleNormal(P, QA.xyz, QB.xyz) * w;
          wsum = wsum + w;
          if (hh > hi && give) { hi = hh; }
        }
        P = P + N * bulge;
        if (wsum > 1e-6) { N = normalize(mix(N, nn / wsum, min(wsum, 1.0))); }
        if (hi > 0.02) { sink = 0.002; }     // give way, so the depth test has a winner
      }

      // A CUT PART IS A SHELL, not a solid with a lid. Hair, a hood, a hat's crown, a skirt, a sleeve: the
      // rig cuts a ball or a cone with a slab along its own axis, and the composite engine fills the cut with
      // a flat cap. As geometry that cap is a disc standing in the middle of the head -- and since a hair ball
      // is wider than the skull it sits on, its rim comes out all round the face and the two sides meet in
      // front of it. What the shape actually is, and what people.js calls it, is a SHELL round the body: the
      // surface between the two cuts, a few millimetres thick, closed by a rim at each end. That is a bent
      // plate with thickness, and it hugs whatever it covers instead of swallowing it.
      if (!sqz && CK[0].z > 0.5 && C4.z > 0.5 && cnt == 1) {
        isCut = true;
        let a0 = CA[0].xyz;
        let d0 = CB[0].xyz - a0;
        let L0 = max(length(d0), 1e-5);
        let ax0 = select(vec3<f32>(0.0, 1.0, 0.0), d0 / L0, dot(d0, d0) > 1e-10);
        let r0 = abs(CK[0].x);
        let r1e = CB[0].w;
        let loS = max(C4.x, -r0);                  // the kept range, inside the shape's own extent
        let hiS = min(C4.y, L0 + r1e);
        if (hiS > loS + 1e-4) {
          // the same frame the sweep uses, for the same reason: a skirt's stripes should not turn round it
          // as its wearer walks
          let bs3 = base * 3;
          var fwS = texel(tex, bs3 + 1).xyz - texel(tex, bs3).xyz;
          fwS = select(vec3<f32>(1.0, 0.0, 0.0), normalize(fwS), dot(fwS, fwS) > 1e-10);
          let upS = ${viewSpace ? "(view * vec4<f32>(0.0, 1.0, 0.0, 0.0)).xyz" : "vec3<f32>(0.0, 1.0, 0.0)"};
          var sideS = cross(upS, fwS);
          sideS = select(vec3<f32>(0.0, 0.0, 1.0), normalize(sideS), dot(sideS, sideS) > 1e-8);
          var rf0 = sideS - ax0 * dot(sideS, ax0);
          if (dot(rf0, rf0) < 0.04) { rf0 = fwS - ax0 * dot(fwS, ax0); }
          let frame1 = select(vec3<f32>(1.0, 0.0, 0.0), normalize(rf0), dot(rf0, rf0) > 1e-8);
          let frame2 = cross(ax0, frame1);
          // THE RINGS BY NUMBER: ring 0 the low cut's rim (its centre, when it is closed), then the outer surface
          // from the low cut to the high, then the high cut's rim, then the inner surface back. A rim is ONE ring
          // step wide, so its inner end always falls on a ring -- laid out by fractions of u, a lid's centre fell
          // between two rings at every grid the figures use, and every skirt was an open tube at its hem.
          let kR = floor(uv.x * nr + 0.5);
          let mR = max(floor(nr * 0.5), 2.0);          // outer rings 1..mR, the high rim mR + 1, inner rings after
          var sPos = loS;
          var outer = 1.0;
          var rimF = -1.0;                         // -1: not on a rim; else how far across it (0: its inner end)
          if (kR < 0.5) { sPos = loS; rimF = 0.0; }
          else if (kR <= mR) { sPos = mix(loS, hiS, (kR - 1.0) / max(mR - 1.0, 1.0)); }
          else if (kR < mR + 1.5) { sPos = hiS; rimF = 0.0; }
          else { sPos = mix(hiS, loS, (kR - mR - 2.0) / max(nr - mR - 2.0, 1.0)); outer = 0.0; }
          var rc = mix(r0, r1e, clamp(sPos / L0, 0.0, 1.0));
          if (sPos < 0.0) { rc = sqrt(max(r0 * r0 - sPos * sPos, 0.0)); }
          if (sPos > L0) { let e = sPos - L0; rc = sqrt(max(r1e * r1e - e * e, 0.0)); }
          let thick = min(skin, rc * 0.45);
          let rIn = max(rc - thick, 0.0005);
          let rHere = select(rIn, rc, outer > 0.5);
          // A SHELL CUT OPEN AT THE FRONT (people.js clip.back, skeleton.js packs it into this texel): a fall
          // of long hair is a cone round the back of the head and the shoulders, open where the face is. The
          // opening is a plane square to the FIGURE's own forward, that many metres ahead of the shell's start
          // -- and the sweep simply misses the arc in front of it, instead of going the whole way round.
          //   (It was the SDF that used to cut this, and when the figures became polygons it went with it:
          // every long-haired person has been wearing a veil since, hair closed over the face to the chin.)
          var aStart = 0.0;
          var aSpan = 6.2831853;
          let bcode = floor(C4.z * 0.25);
          if (bcode > 0.5) {
            let bk = (bcode - 1.0) * 0.001 - 0.5;
            let rr0 = texel(tex, base * 3).xyz;
            let rr1 = texel(tex, base * 3 + 1).xyz;
            var fw = rr1 - rr0;
            fw = select(vec3<f32>(1.0, 0.0, 0.0), normalize(fw), dot(fw, fw) > 1e-10);
            let fu = dot(frame1, fw);
            let fv = dot(frame2, fw);
            let fm = max(sqrt(fu * fu + fv * fv), 1e-5);
            let alongF = dot(ax0, fw) * sPos;
            // keep the arc whose points lie no further forward than the plane; the rest is the opening
            let tCut = clamp((bk - alongF) / max(rHere * fm, 1e-5), -1.0, 1.0);
            let halfGap = acos(tCut);
            aStart = atan2(fv, fu) + halfGap;
            aSpan = 6.2831853 - 2.0 * halfGap;
          }
          let ang2 = aStart + uv.y * aSpan;
          let radial = frame1 * cos(ang2) + frame2 * sin(ang2);
          // THE OUTER WALL ROUND THE CIRCLE, NOT IN IT: a ring's points on the circle leave its faces inside it by the
          // chord's sag -- a tenth of the radius at the far grid's seven points, a centimetre on a head -- and a cut
          // shell is a layer that thin (hair is 1.2 cm over the scalp). Inscribed, the hair's faces sank under the
          // head's own points and a head of hair was bald past a few metres. Circumscribed, its faces touch the circle
          // from outside, whatever the grid.
          let circ = 1.0 / cos(0.5 * aSpan / max(part.z, 3.0));
          kind = select(1.0, 0.0, outer > 0.5);      // the inner wall of a shell is its lining
          if (rimF >= 0.0) { kind = 2.0; }            // ...and a cut's face is a flat cap
          if (rimF >= 0.0) {
            // WHICH CUTS GET A LID. A hat's crown is cut flat across its top, and a shell alone leaves it open
            // to the sky; a hat's BRIM is a ball cut to a thin slab, and a shell of that is a hoop with a hole
            // where the hat should be. Both are closed with a disc: a cut whose circle is small against the
            // shape's girth (a crown's top), and every cut of a shape kept as a thin slab (a brim, a belt) --
            // there the flat faces ARE the shape, and what they cover is hidden by the head in front of them.
            // A wide cut of a deep shape stays open, which is the hairline, a sleeve's mouth, a skirt's waist.
            let rMax = max(max(r0, r1e), 1e-4);
            // ...and a cut that is NOT inside what the shape covers is a lid too. That is the difference
            // between a hairline -- whose plane passes through the head, which fills it -- and the flat top of
            // a hat's crown, which is cut in free air above it and must be closed or the hat has no top.
            var filled = false;
            for (var jj: i32 = 0; jj < 4; jj = jj + 1) {
              if (nb[jj] < -0.5 && nb[jj] > -1.5) { continue; }
              let sj2 = i32(select(nb[jj], -nb[jj] - 2.0, nb[jj] < -1.5) + 0.5);
              let PA = texel(tex, sj2 * 3);
              let PB = texel(tex, sj2 * 3 + 1);
              let pua2 = unpackAw(PA.w);
              // only a SOLID neighbour fills a cut: another cut shell (the hair under a hat) is a layer with
              // nothing behind it, and taking it for a filler leaves the hat open to the sky
              if (PB.w < 0.0 || pua2.z > 0.5) { continue; }
              if (sdRoundCone(a0 + ax0 * sPos, PA.xyz, PB.xyz, abs(pua2.x), PB.w) < 0.0) { filled = true; }
            }
            // THE FAR CUT IS AN EDGE, not a lid, unless the cut is SOLID (a hat's crown, cut flat) or a thin slab (a
            // brim, where the flat faces ARE the shape): a skirt's hem, a cloak's, a sleeve's mouth, a fall of hair
            // end in their own thickness and stay open -- a disc across a hem is a floor under the skirt. The NEAR
            // one, which is where the shape meets the body it covers, is closed only when nothing fills it, when it
            // is a thin slab or when its circle is small against the shape's girth -- or when a garment standing off
            // the body says so (mode 3: a skirt's waistband over the gap between the round skirt and the torso).
            let atHi = sPos > loS + (hiS - loS) * 0.5;
            let mode = C4.z - 4.0 * floor(C4.z / 4.0);
            let thinSlab = (hiS - loS) < 0.5 * rMax;
            let lid = select(rc < 0.62 * rMax || thinSlab || !filled || mode > 2.5, (mode > 1.5 && mode < 2.5) || thinSlab, atHi);
            let inner = select(rIn, 0.0, lid);
            P = a0 + ax0 * sPos + radial * mix(inner, rc * circ, rimF);
            N = select(ax0, -ax0, sPos <= loS + 1e-5);
          } else {
            // THE LINING'S FIRST RING UNDER A CLOSED HIGH CUT starts at the axis. The high rim runs in to the lid's
            // centre, and the lining's first ring is on that same plane -- at rIn it laid a second disc, a lining's,
            // in the lid's own plane, and the two fought (the underside of every brim: its axis runs down). From the
            // centre the step between them is no surface at all.
            var rLin = rHere;
            if (outer < 0.5 && kR > mR + 1.5 && kR < mR + 2.5) {
              let modeL = C4.z - 4.0 * floor(C4.z / 4.0);
              if ((modeL > 1.5 && modeL < 2.5) || (hiS - loS) < 0.5 * max(max(r0, r1e), 1e-4)) { rLin = 0.0; }
            }
            P = a0 + ax0 * sPos + radial * select(rLin, rHere * circ, outer > 0.5);
            // (the surface's own normal: leaning with the cone's flare along its length, a sphere's over a rounded end
            //  -- a skirt shades as a skirt, a lap's rounded knee as a dome, not both as a drum)
            var nS = radial - ax0 * ((r1e - r0) / L0);
            if (sPos > L0) { nS = radial * rc + ax0 * (sPos - L0); }
            if (sPos < 0.0) { nS = radial * rc + ax0 * sPos; }
            nS = normalize(nS);
            N = select(-nS, nS, outer > 0.5);
          }
          // A GARMENT'S SHELL FLATTENED FRONT TO BACK (its own squash, in its third texel's w): a skirt or a cape hangs
          // oval round a flattened torso -- a round one stands a hand's breadth off the belly to clear the hips
          if (C4.w > 0.01 && C4.w < 0.999) {
            var wS = fwS - ax0 * dot(fwS, ax0);
            wS = select(frame1, normalize(wS), dot(wS, wS) > 1e-8);
            let ctrS = a0 + ax0 * sPos;
            let offS = P - ctrS;
            P = ctrS + offS - wS * (dot(offS, wS) * (1.0 - C4.w));
            N = normalize(N + wS * (dot(N, wS) * (1.0 / C4.w - 1.0)));
            squash = C4.w;
          }
        }
      }
    }

    // A MARK IS PLACED INSIDE WHAT IT MARKS. The composite engine paints eyes, brows and a mouth onto the head
    // wherever they fall, so the rig puts them a hair under its surface -- and a solid drawn there is simply
    // inside the head and never seen (which is why they were missing). Each vertex climbs out along the
    // surface it is buried in and stands SHELL.mark millimetres proud of it, which is where a painted mark
    // looks like it is.
    if (mark) {
      for (var j: i32 = 0; j < 4; j = j + 1) {
        if (nb[j] < -0.5 && nb[j] > -1.5) { continue; }
        let sj = i32(select(nb[j], -nb[j] - 2.0, nb[j] < -1.5) + 0.5);
        let QA = texel(tex, sj * 3);
        let QB = texel(tex, sj * 3 + 1);
        let qua = unpackAw(QA.w);
        if (QB.w < 0.0) { continue; }
        // it must clear that neighbour's SHELL, not its distance field: the shell is bulged outward by up to
        // a quarter of its own blend radius wherever it fillets into something, and a mark lifted by less than
        // that is still buried -- which is exactly why 2 mm was not enough and the faces stayed blank.
        let eps = qua.y * 0.25 + lift * 0.001;
        let d = sdRoundCone(P, QA.xyz, QB.xyz, abs(qua.x), QB.w);
        if (d < eps) {
          P = P - capsuleNormal(P, QA.xyz, QB.xyz) * (d - eps);
        }
      }
    }
    // WHAT A PART WEARS lifts its surface by the thickness of every layer over the point (clothes.js), and the ring
    // hands its OWN part to the fragment (a flat varying), which reads that part's layers -- a sleeve and a bare
    // forearm on one swept arm. (A cut shell is cloth itself: it is not lifted.)
    var ringSlot = sl[0];
    let triPart = CB[0].w < 0.0 && CB[0].w > -1.5;
    if (!mark && !triPart) {
      let rs = CK[ringI].w;
      let rfl = texel(sTex, i32(rs + 0.5) * ${ST}).w;
      if (floor(rfl / 1024.0) - 2.0 * floor(rfl / 2048.0) > 0.5) {   // (dressed: bit 1024 -- the stone material sits above it)
        ringSlot = rs;
        if (!isCut) {
          let pa = CA[ringI].xyz;
          let pd = CB[ringI].xyz - pa;
          let pdn = pd / max(length(pd), 1e-5);
          let sL = dot(P - pa, pdn);
          let qd = P - pa - pdn * sL;
          let q0 = texel(tex, base * 3).xyz;
          let q1 = texel(tex, base * 3 + 1).xyz;
          var fwD = q1 - q0;
          fwD = select(vec3<f32>(1.0, 0.0, 0.0), normalize(fwD), dot(fwD, fwD) > 1e-10);
          let upD = ${viewSpace ? "(view * vec4<f32>(0.0, 1.0, 0.0, 0.0)).xyz" : "vec3<f32>(0.0, 1.0, 0.0)"};
          let lfD = normalize(cross(fwD, upD));
          let thD = atan2(dot(qd, lfD), dot(qd, fwD));
          P = P + N * dressLift(sTex, texel(sTex, i32(rs + 0.5) * ${ST} + 2), sL, thD, max(length(qd), 0.004), length(qd));
        }
      }
    }
    P = P - N * sink;
    let pv = ${viewSpace ? "P" : "(view * vec4<f32>(P, 1.0)).xyz"};
    let pw = ${viewSpace ? "(invView * vec4<f32>(P, 1.0)).xyz" : "P"};
    let nw = ${viewSpace ? "normalize((invView * vec4<f32>(N, 0.0)).xyz)" : "N"};
    // (the fragment fetches the part's own texels by slot -- fewer varyings than carrying them across, and it
    //  reads exactly what the SDF reads: colours, flags, the strands' scale, a dress header, the part's ends)
    let kf = kind * 2.0 + clamp(squash, 0.0, 1.0);
    // (the world point the figure-wide patterns need is rebuilt in the fragment from the view point)
    // a FACE MARK carries its own flags in that texel (iris, pupil, round, relief) -- they are not a pattern,
    // so it is handed a slot of -1 and keeps the colour the vertex gave it
    let sOut = select(ringSlot, -1.0, mark);
    return mat4x4<f32>(vec4<f32>(pv, sOut), vec4<f32>(nw, f32(base)), vec4<f32>(col, girthHere), vec4<f32>(loc, kf));
  }
`, [texelFor(W), unpackAw, sdRoundCone, LIB.capsuleNormal, LIB.tubeUnpack, LIB.tubeR, LIB.bezier3, dressFns(W, ST).dressLift]);

// THE SURFACE'S OWN COLOUR: the flat fill, then whatever the part carries -- a coat's pattern, a garment's
// cloth, fur over either -- and then the world's light. None of it is new code: the pattern library is the
// composite engine's (banner_wgsl patternAt, composite_wgsl strandsAt and furAt), and it is read with the same
// numbers the SDF hands it. What a pattern wants to know is where the point lies on the part it belongs to --
// how far ALONG the axis, at what ANGLE round it, how far OUT from it -- and that is what partLocal returns
// from the point and the part's two ends, which the sweep knows exactly.
//   The fragment fetches the part's own texels by slot rather than carrying them across as varyings: colours,
// flags (pat * 8 + bodyFrame * 4 + edge * 2 + seam, fur at 256, dressed at 1024), the strands' scale and
// the cut. A cloth pattern laid in the FIGURE's frame (a coat over rump, chest, neck and head, a skirt's
// stripes round the body) reads the figure's root, slot `base`, for that frame.
// STONE (statues.js): a figure carved -- every part, its cloth included, one material lit as the buildings are (the
// world's Lambert, shadeOf) with a grain of its own laid in the WORLD (a statue does not move: the stone is the
// stone's) and, for the metals, the sun's highlight: 1 marble (white, faint grey veins), 2 bronze, 3 gold, 4 limestone
const SUN = (() => { const d = LIGHT.dir, l = Math.hypot(...d) || 1; return d.map((v) => (v / l).toFixed(4)); })();
const stoneAt = wgslFn(`
  fn stoneAt(m: f32, pw: vec3<f32>, n: vec3<f32>, eye: vec3<f32>) -> vec3<f32> {
    // value noise in 3D, three octaves
    var f = 0.0; var amp = 0.5; var q = pw * 6.0;
    for (var o = 0; o < 3; o = o + 1) {
      let i = floor(q); let u = fract(q); let w = u * u * (3.0 - 2.0 * u);
      let h = dot(i, vec3<f32>(127.1, 311.7, 74.7));
      let a = fract(sin(h) * 43758.5453); let b = fract(sin(h + 127.1) * 43758.5453);
      let c = fract(sin(h + 311.7) * 43758.5453); let d = fract(sin(h + 438.8) * 43758.5453);
      let e = fract(sin(h + 74.7) * 43758.5453); let g = fract(sin(h + 201.8) * 43758.5453);
      let k = fract(sin(h + 386.4) * 43758.5453); let l = fract(sin(h + 513.5) * 43758.5453);
      let x0 = mix(mix(a, b, w.x), mix(c, d, w.x), w.y); let x1 = mix(mix(e, g, w.x), mix(k, l, w.x), w.y);
      f = f + amp * mix(x0, x1, w.z); amp = amp * 0.5; q = q * 2.13;
    }
    let N = normalize(n);
    let L = vec3<f32>(${SUN.join(", ")});
    let V = normalize(eye - pw);
    let H = normalize(L + V);
    let lam = shadeOf(N);
    let nh = max(dot(N, H), 0.0);
    var base = vec3<f32>(0.86, 0.84, 0.80);
    var spec = 0.0;
    var tint = vec3<f32>(1.0);
    if (m < 1.5) {                       // marble: white, a faint mottle, thin grey veins wandering through it
      let v = abs(sin(pw.x * 2.3 + pw.y * 3.1 + pw.z * 1.7 + 7.0 * f));
      base = base * (0.94 + 0.1 * f) - vec3<f32>(0.28) * pow(1.0 - v, 22.0);
      spec = pow(nh, 24.0) * 0.12;
    } else if (m < 2.5) {                // bronze: dark warm metal, greener in its hollows
      base = mix(vec3<f32>(0.36, 0.25, 0.13), vec3<f32>(0.24, 0.36, 0.28), smoothstep(0.55, 0.8, f) * 0.6);
      spec = pow(nh, 36.0) * 0.55; tint = vec3<f32>(1.0, 0.82, 0.55);
    } else if (m < 3.5) {                // gold: bright, a hard highlight
      base = vec3<f32>(0.86, 0.64, 0.22) * (0.92 + 0.12 * f);
      spec = pow(nh, 48.0) * 0.9 + pow(nh, 8.0) * 0.12; tint = vec3<f32>(1.0, 0.9, 0.6);
    } else {                             // limestone: warm, pitted
      base = vec3<f32>(0.80, 0.75, 0.64) * (0.88 + 0.2 * f);
      spec = pow(nh, 12.0) * 0.05;
    }
    return base * lam + tint * spec * smoothstep(-0.05, 0.3, dot(N, L));
  }
`, [LIB.shadeOf]);

// the same stone on a plain mesh (a statue's mesh head, the sword in its hand): one material a stone, made once
const STONE_MATS = new Map();
export function stoneMaterial(m) {
  if (!STONE_MATS.has(m)) {
    const mat = new THREE.MeshBasicNodeMaterial();
    mat.colorNode = stoneAt({ m: float(m), pw: positionWorld, n: normalWorld, eye: cameraPosition });
    STONE_MATS.set(m, mat);
  }
  return STONE_MATS.get(m);
}
export const STONES = { marble: 1, bronze: 2, gold: 3, limestone: 4 };

const shellShade = (W, ST, viewSpace) => wgslFn(`
  fn shellShade(tex: texture_2d<f32>, sTex: texture_2d<f32>, fab: texture_2d_array<f32>, fsamp: sampler,
                invView: mat4x4<f32>, pv: vec3<f32>,
                loc: vec3<f32>, n: vec3<f32>, col: vec3<f32>, girth: f32, slot: f32, base: f32,
                kf: f32) -> vec3<f32> {
    let pw = ${viewSpace ? "(invView * vec4<f32>(pv, 1.0)).xyz" : "pv"};
    let i = i32(slot + 0.5);
    if (i < 0) { return col * shadeOf(normalize(n)); }
    let kind = floor(kf / 2.0);
    let fq = kf - 2.0 * kind;
    // THE PATTERN'S FRAME IS THE WORLD'S. The engine keeps a part's ends in CAMERA space while the camera is
    // where it is (PIPE.viewSpace: it saves a matrix per part per pixel), so reading them straight and pairing
    // them with a world-space point mixes two frames -- and the pattern then slides over the surface as the
    // camera turns. They are brought back to the world here, as the composite engine brings them back.
    let A4 = texel(tex, i * 3);
    let B4 = texel(tex, i * 3 + 1);
    let C = texel(tex, i * 3 + 2);
    let A = vec4<f32>(${viewSpace ? "(invView * vec4<f32>(A4.xyz, 1.0)).xyz" : "A4.xyz"}, A4.w);
    let B = vec4<f32>(${viewSpace ? "(invView * vec4<f32>(B4.xyz, 1.0)).xyz" : "B4.xyz"}, B4.w);
    let S0 = texel(sTex, i * ${ST});
    let S1 = texel(sTex, i * ${ST} + 1);
    let S2 = texel(sTex, i * ${ST} + 2);
    let flags = max(S0.w, 0.0);
    let low = flags - 256.0 * floor(flags / 256.0);
    let pat = floor(low / 8.0);
    let bodyFrame = (low - 8.0 * floor(low / 8.0)) >= 4.0;
    let furry = (floor(flags / 256.0) - 2.0 * floor(flags / 512.0)) > 0.5;
    let code = floor(max(S1.w, 0.0) + 0.5);
    let ua = unpackAw(A.w);
    let r = max(max(abs(ua.x), B.w), girth);
    var c = col;
    var nn = normalize(n);
    // STONE (a statue: 2048 x its material -- 1 marble, 2 bronze, 3 gold, 4 limestone): the cloth keeps its shape, its
    // holes and its folds, the colour is the stone's
    let stoneM = floor(flags / 2048.0);
    let eye = invView[3].xyz;
    if (floor(flags / 1024.0) - 2.0 * floor(flags / 2048.0) > 0.5) {
      // DRESSED (clothes.js): where the point lies on its part -- along the axis from A, and round it from the
      // figure's front toward its left, the figure's own frame read from its root -- and the outermost layer there
      let dP = B.xyz - A.xyz;
      let ax = dP / max(length(dP), 1e-5);
      let sL = dot(pw - A.xyz, ax);
      let rq = pw - A.xyz - ax * sL;
      let bi = i32(base + 0.5);
      let R0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3).xyz, 1.0)).xyz" : "texel(tex, bi * 3).xyz"};
      let R1 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3 + 1).xyz, 1.0)).xyz" : "texel(tex, bi * 3 + 1).xyz"};
      var fw = R1 - R0;
      fw = select(vec3<f32>(1.0, 0.0, 0.0), normalize(fw), dot(fw, fw) > 1e-10);
      // the figure's UP: its chest's axis (the dress header names the row; a figure struck down lies on its side, and
      // the cloth must turn with it -- with the world's up its left collapses and the weave flattens into lines)
      var upW = vec3<f32>(0.0, 1.0, 0.0);
      let ur = i32(S2.w + 0.5);
      if (ur > 0) {
        let U0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, (ur - 1) * 3).xyz, 1.0)).xyz" : "texel(tex, (ur - 1) * 3).xyz"};
        let U1 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, (ur - 1) * 3 + 1).xyz, 1.0)).xyz" : "texel(tex, (ur - 1) * 3 + 1).xyz"};
        let du = U1 - U0;
        upW = select(upW, normalize(du), dot(du, du) > 1e-10);
        let fwp = fw - upW * dot(fw, upW);
        fw = select(fw, normalize(fwp), dot(fwp, fwp) > 1e-8);
      }
      let lf0 = normalize(cross(fw, upW));
      // (the cloth's own frame: the part's REST axis, kept when it was first posed -- composite.js restAxes -- in the
      //  figure's frame; the figure's forward and left carried from it to the axis now by the least rotation, so the
      //  weave turns with a swinging arm instead of sliding round the sleeve; the angle still counts from the front
      //  toward the left, as the garments' openings expect)
      var fR = fw;
      var lR = lf0;
      if (S1.w < -0.5 && S1.w > -1.5) {
        let r0 = normalize(fw * S1.x + upW * S1.y + lf0 * S1.z);
        let cr = cross(r0, ax);
        let cs = dot(r0, ax);
        if (cs > -0.98) {
          let kk = 1.0 / (1.0 + cs);
          fR = fw * cs + cross(cr, fw) + cr * (dot(cr, fw) * kk);
          lR = lf0 * cs + cross(cr, lf0) + cr * (dot(cr, lf0) * kk);
        }
      }
      let fp = fR - ax * dot(fR, ax);
      let fwT = select(fw, normalize(fp), dot(fp, fp) > 1e-8);
      let lq = lR - ax * dot(lR, ax) - fwT * dot(lR, fwT);
      let lf = select(lf0, normalize(lq), dot(lq, lq) > 1e-8);
      let th = atan2(dot(rq, lf), dot(rq, fwT));
      // (its change across the pixel without the jump where the angle wraps: whichever of the two ways of counting it
      //  -- the jump at the back, or at the front -- changes less here)
      let th2 = th + select(0.0, 6.2831853, th < 0.0);
      var dth = vec2<f32>(dpdx(th), dpdy(th));
      let dth2 = vec2<f32>(dpdx(th2), dpdy(th2));
      if (dot(dth2, dth2) < dot(dth, dth)) { dth = dth2; }
      let ds = vec2<f32>(dpdx(sL), dpdy(sL));
      let px = max(max(length(dpdx(pw)), length(dpdy(pw))), 1e-5);
      var rel = vec3<f32>(0.0);
      let got = dressAt(sTex, fab, fsamp, S2, sL, th, dth, ds, max(girth, 0.004), px, kind, col, ax, rq, &rel);
      if (got.w < 0.5 && S2.z > 0.5 && stoneM < 0.5) { discard; }   // a standing piece is cloth only where a layer is: its openings are holes (carved, it is full)
      c = got.xyz;
      if (got.w < 0.5 && furry) { c = furAt(c, loc, px); }   // (a beast's hide where nothing is worn: its coat)
      if (dot(rel, rel) > 1e-12) { nn = normalize(nn - rel); }
      if (stoneM > 0.5) { return stoneAt(stoneM, pw, nn, eye); }
      return c * shadeOf(nn);
    }
    if (stoneM > 0.5) { return stoneAt(stoneM, pw, nn, eye); }
    if (pat > 0.5 || code > 0.5 || furry) {
      // The point in the part's own frame comes from the SWEEP (loc), not from the posed ends: nailed to the
      // mesh, so a leg can swing without dragging its pattern through the coat. A garment or coat laid over
      // the whole FIGURE is the exception -- that frame is the figure's own, and it is meant to move with it.
      let pl0 = loc;
      var pl = pl0;
      if (bodyFrame) {
        let bi = i32(base + 0.5);
        let A0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3).xyz, 1.0)).xyz" : "texel(tex, bi * 3).xyz"};
        let B0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3 + 1).xyz, 1.0)).xyz" : "texel(tex, bi * 3 + 1).xyz"};
        let dd = B0 - A0;
        let fwW = select(vec3<f32>(1.0, 0.0, 0.0), normalize(dd), length(dd) > 1e-4);
        let lf = cross(vec3<f32>(0.0, 1.0, 0.0), fwW);
        let q = pw - 0.5 * (A0 + B0);
        pl = vec3<f32>(dot(q, fwW), q.y, dot(q, lf));
      }
      // THE PIXEL'S FOOTPRINT AT THE SURFACE, in metres: what a pattern fades by when its cells get smaller
      // than a pixel. fwidth is |ddx| + |ddy|, so measuring it per component and taking the length of the
      // three counts one pixel three or four times over -- and at that size every scale, scute and rosette
      // was already past its fade, which is why a dinosaur's hide came out plain at any distance. It is the
      // step the point itself takes across one pixel, as the SDF measures it (composite_wgsl px).
      let patPx = max(max(length(dpdx(pw)), length(dpdy(pw))), 1e-5);
      let nL = cross(dpdx(pl), dpdy(pl));
      let patAx = abs(nL.x) / max(length(nL), 1e-9);
      if (pat > 14.5 && pat < 16.5) {
        c = strandsAt(c, S1.xyz, pat, code, pl, bodyFrame, pw, A.xyz, B.xyz, r, max(fq, 0.05));
      } else if (pat > 0.5) {
        c = patternAt(c, pat, pl, r, patPx, patAx);
      }
      if (furry) { c = furAt(c, pl0, patPx); }
    }
    return c * shadeOf(nn);
  }
`, [texelFor(W), unpackAw, LIB.partLocal, LIB.patternAt, strandsAt, furAt, LIB.shadeOf, dressFns(W, ST).dressAt, stoneAt]);

// ---- one shell set for one composite herd -----------------------------------------------------------------
//   nDyn/nStat  the herd's texture nodes (the same ones its own material reads)
//   cap         how many parts the herd has room for (a chain is at most one instance per part)
//   touch       composite.js's partial upload: only the instances a frame listed go up
//   ends        the herd's posed world endpoints for a part: what the chains are worked out from
const SLOTS = ["part", "ch", "ch2", "nb"];
const attrName = (n) => "a" + n[0].toUpperCase() + n.slice(1);
export function createShell({ nDyn, nStat, W, ST, viewSpace, cap, touch, ends }) {
  const uBlend = uniform(SHELL.blend), uThin = uniform(SHELL.thin), uLift = uniform(SHELL.mark), uSkin = uniform(SHELL.skin);
  const point = shellPoint(W, ST, viewSpace);
  const material = (() => {
    const q = point({
      tex: nDyn, sTex: nStat, uv: positionGeometry.xy, nr: positionGeometry.z,
      part: attribute("aPart", "vec4"), ch: attribute("aCh", "vec4"), ch2: attribute("aCh2", "vec4"),
      nb: attribute("aNb", "vec4"),
      view: cameraViewMatrix, invView: cameraWorldMatrix, blend: uBlend, thin: uThin, lift: uLift, skin: uSkin,
    });
    // (the part a ring lies on is handed over FLAT: every triangle takes its first vertex's, so the strip across a
    //  joint belongs wholly to one part and never reads a slot halfway between two)
    const vS = varying(q.element(0).w, "vShellS").setInterpolation("flat");
    const vP = varying(q.element(0), "vShellP"), vN = varying(q.element(1), "vShellN"),
          vC = varying(q.element(2), "vShellC"), vL = varying(q.element(3), "vShellL");
    const mat = new THREE.MeshBasicNodeMaterial();
    mat.side = THREE.DoubleSide;   // a shell is a closed solid; never let a winding decide whether it is there
    mat.vertexNode = cameraProjectionMatrix.mul(vec4(q.element(0).xyz, 1.0));
    // THE GEOMETRY VIEW (T). A shell's triangles are built in the vertex shader, so the wire mesh the world
    // builds on the CPU (index.html buildWire) cannot see them: the material draws them itself instead, as the
    // wireframe of the very triangles being drawn, in the blue the SDF cards used. Switched rarely (a key
    // press), so it swaps the colour node and lets the pipeline rebuild rather than paying a live uniform.
    const shaded = shellShade(W, ST, viewSpace)({ tex: nDyn, sTex: nStat, fab: fabricNode, fsamp: fabricNode, invView: cameraWorldMatrix,
                                                 pv: vP.xyz, loc: vL.xyz, n: vN.xyz, col: vC.xyz,
                                                 girth: vC.w, slot: vS, base: vN.w, kf: vL.w });
    const wire = () => {
      const on = QUADS.value > .5;
      mat.wireframe = on;
      mat.colorNode = on ? vec3(0.15, 0.5, 1.0) : shaded;
      mat.needsUpdate = true;
    };
    wire();
    onQuads(wire);
    return mat;
  })();

  const setArrays = (b, room) => {
    for (const name of SLOTS) {
      const arr = new Float32Array(room * 4);
      if (b[name]) arr.set(b[name].subarray(0, Math.min(b[name].length, arr.length)));
      b[name] = arr;
      b[name + "A"] = new THREE.InstancedBufferAttribute(arr, 4);
      b.geo.setAttribute(attrName(name), b[name + "A"]);
    }
    b.room = room;
  };
  let dumped = false;
  const buckets = [];
  for (const [far, rings, divs] of SHELL.lod) for (let c = 0; c < LENGTHS.length; c++) {
    const b = { far, cls: c, rings: Math.max(4, Math.round(rings * LENGTHS[c])), divs, n: 0, want: 0 };
    b.geo = shellGrid(b.rings, divs);
    setArrays(b, 64);                          // grown as a bucket fills: most of the nine stay small
    b.mesh = new THREE.Mesh(b.geo, material);
    b.mesh.frustumCulled = false;
    b.mesh.userData.sdf = true;   // its triangles are built in the vertex shader: no override material, no CPU wire
    b.mesh.visible = false;
    buckets.push(b);
  }

  return {
    meshes: buckets.map((b) => b.mesh),
    begin() { for (const b of buckets) { b.n = 0; b.dirty = false; } },
    // one figure's chains, into the bucket its distance picks
    push(an, dist) {
      // A FIGURE THAT HAS NOT BEEN POSED YET HAS NO GEOMETRY. One added in the middle of a frame -- the rider
      // an arrow parts from his horse, a felled figure moved to another herd -- still has zeroed rows, and
      // drawing it stretches its shells from the world's origin. Worse, it is usually the FIRST of its species
      // to be drawn, and the chains worked out from those zeros would then be cached and wrong for every
      // figure of that species from then on. It waits a frame.
      if (!an._posed) return;
      const parts = an.parts, { chains, of, size, curve, nb } = shellChains(parts, (i) => ends(an, i));
      for (let ci = 0; ci < chains.length; ci++) {
        const c = chains[ci];
        const cls = classOf(curve[ci], c.length);
        // the bucket is picked by distance in CHAIN LENGTHS, so a muzzle or an ear falls to the coarse grid
        // while a body a hundred times its size keeps the fine one at the same distance
        const far = dist / Math.max(size[ci], .04);
        let b = buckets[buckets.length - LENGTHS.length + cls];
        for (const q of buckets) if (far <= q.far && q.cls === cls) { b = q; break; }
        // A BUCKET THAT IS FULL WAITS. push() runs inside the render (the herd syncs in onBeforeRender), and
        // swapping a geometry's attributes there hands three a buffer it has already bound for this frame --
        // which is a GPU validation error and a lost device a moment later. The bucket asks for room instead,
        // and grow(), called from the herd's update() between frames, gives it. One frame without a chain in
        // an over-full bucket is invisible; a crash is not.
        if (b.n >= b.room) { b.want = Math.min(cap, Math.max(b.want ?? 0, b.room * 4)); continue; }
        // WHAT A FRAME WRITES HERE HARDLY EVER CHANGES. A figure that walks across the world keeps the same
        // parts in the same slots: only appearing, disappearing or crossing into another detail bucket moves
        // anything. So each value is compared before it is stored, and a bucket whose list came out identical
        // is not uploaded at all -- it was four attribute uploads a bucket, nine buckets a herd, every frame.
        const w = b.n * 4;
        const put = (arr, i, v) => { if (arr[i] !== v) { arr[i] = v; b.dirty = true; } };
        put(b.part, w, c.length); put(b.part, w + 1, an.base); put(b.part, w + 2, b.divs);
        put(b.part, w + 3, isMark(parts[c[0]]) ? 1 : 0);   // a face mark: its own girth, not the packed reach
        for (let j = 0; j < 4; j++) put(b.ch, w + j, j < c.length ? an.base + c[j] : -1);
        for (let j = 4; j < 8; j++) put(b.ch2, w + j - 4, j < c.length ? an.base + c[j] : -1);
        // the chain's joint: its first part's neighbours. WHO GIVES WAY is decided here, once, and carried in
        // the sign: two chains that both bulge into one fillet land on the same surface and fight for the
        // depth test, so the one whose chain starts later sinks a hair. Comparing the two PART slots in the
        // shader is not enough -- chains interleave, and then both sides think they have won.
        // A MARK'S ONE NEIGHBOUR IS ITS PARENT -- the head it is painted on. Handing it the nearest parts
        // instead let an eye climb out of the HAT ball it happened to sit inside, which put it a hand's width
        // off the face (and the mouth with it).
        const mine = c[0];
        if (isMark(parts[mine])) {
          const par = parts[mine].parentIdx;
          put(b.nb, w, par >= 0 ? an.base + par : -1);
          for (let j = 1; j < 4; j++) put(b.nb, w + j, -1);
        } else {
          const list = nb[mine];
          for (let j = 0; j < 4; j++) {
            const o = j < SHELL.near ? list[j] : -1;
            put(b.nb, w + j, o < 0 ? -1 : (chains[of[o]][0] < mine ? -(an.base + o + 2) : an.base + o));
          }
        }
        b.n++;
      }
    },
    // between frames (the herd's update): give any bucket that ran out of room the space it asked for
    grow() {
      for (const b of buckets) if (b.want > b.room) { setArrays(b, b.want); b.want = 0; }
    },
    // HOW FINE THE SWEEP IS, live. Each bucket is a GRID -- so many rings up the chain, so many points round a
    // cut -- and `k` multiplies both: 2 is twice the rings and twice the points (four times the triangles), .5
    // is half. The grid is the only thing that changes; the instances riding on it are untouched, so it is a
    // new geometry and the same attributes. (The asset viewer's + and -; the same knob a quality setting would
    // turn.)
    setDetail(k) {
      const m = Math.max(.25, Math.min(6, k));
      for (const b of buckets) {
        const base = SHELL.lod.find(([far]) => far === b.far) ?? SHELL.lod[SHELL.lod.length - 1];
        const rings = Math.max(4, Math.round(base[1] * m * LENGTHS[b.cls])), divs = Math.max(3, Math.round(base[2] * m));
        if (rings === b.rings && divs === b.divs) continue;
        b.rings = rings; b.divs = divs;
        b.geo.dispose();
        b.geo = shellGrid(rings, divs);
        b.mesh.geometry = b.geo;
        setArrays(b, b.room);            // the instance attributes go onto the new grid
      }
    },
    detailOf: () => buckets.map((b) => `${b.rings}x${b.divs}`).join(" "),
    end() {
      if (SHELL.debug && !dumped) {               // once: what the frame actually listed
        dumped = true;
        console.log("shell buckets: " + buckets.map((b) => `${b.rings}x${b.divs}:${b.n}`).join(" ") +
                    "  total " + buckets.reduce((a, b) => a + b.n, 0));
      }
      for (const b of buckets) {
        b.geo.instanceCount = b.n;
        b.mesh.visible = b.n > 0;
        if (b.n && (b.dirty || b.n !== b.sent)) for (const name of SLOTS) touch(b[name + "A"], b.n);
        b.sent = b.n;
      }
    },
    resize() { },                              // (the buckets grow on their own as they fill)
    stats: () => buckets.filter((b) => b.n).map((b) => ({ far: b.far, rings: b.rings, divs: b.divs,
      chains: b.n, tris: b.n * b.rings * b.divs * 2 })),
  };
}
