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
import { wgslFn, attribute, varying, uniform, vec2, vec3, vec4, float, uv, positionGeometry, positionWorld, normalWorld, cameraPosition, cameraProjectionMatrix, cameraViewMatrix, cameraWorldMatrix, normalize } from "three/tsl";
import { sunShade } from "./sunshadow.js";   // (the figures in the buildings' shadows)
import * as LIB from "./banner_wgsl.js";
import { sdRoundCone, texelFor, unpackAw, furAt, strandsAt } from "./composite_wgsl.js";
import { QUADS, onQuads } from "./outline.js";
import { fabricNode, FOLD_TOP } from "./fabric.js";
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
  seam: 1,                                   // ?shellseam=0: the joints as before -- rings spread by fractions, handed over, not mitred, no limb roots
  debug: 0,                                  // ?shelldebug=1: print how each species was split into chains
};

// FLEECE: a woolly part's lumps -- how wide (metres: a few of the near band's points across one, or they would alias
// into a jagged ring) and how far proud of the part at most
export const FLEECE = { size: .24, amp: .05, lock: .075, crease: .24 };   // (lock, crease: the small lumps in the light, how dark between them)

export function shellFromQuery(qp) {
  if (qp.has("shelllod")) SHELL.lod = qp.get("shelllod").split(";").map((g) => g.split(",").map(Number));
  if (qp.has("shellblend")) SHELL.blend = +qp.get("shellblend") ? 1 : 0;
  if (qp.has("shellchain")) SHELL.chain = +qp.get("shellchain") ? 1 : 0;
  if (qp.has("shellseam")) SHELL.seam = +qp.get("shellseam") ? 1 : 0;
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
  // (a cut shell's inner wall runs back down its rings, the outer wall's heights in reverse -- shellPoint's mR: each of
  //  its quads split across the OTHER diagonal, so both walls fold alike: split the same way in the grid, over a sharp
  //  turn of the drape -- a forearm's tent under a mantle -- the lining crossed the cloth by half the turn's height and
  //  showed through it, a dark diamond)
  const mR = Math.max(Math.floor((rings - 1) / 2), 2), idx = [];
  for (let i = 0; i < rings; i++) for (let j = 0; j < divs; j++) {
    const a = i * nv + j, b = a + nv;
    if (i >= mR + 2) idx.push(a, b, b + 1, a, b + 1, a + 1);
    else idx.push(a, b, a + 1, a + 1, b, b + 1);
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
// THE FOLDS' PHASE round a pleated piece (2026-10-24): `pleats` folds round it, not evenly -- warped by a few slow
// waves, more so lower down (t: 0 at the piece's top, 1 at its hem), where folds fan out -> (phase, its rate round)
const foldPhase = wgslFn(`
  fn foldPhase(th: f32, t: f32, pleats: f32) -> vec2<f32> {
    let wq = min(1.0, pleats / 12.0);
    let g = pleats * th + wq * (1.1 * sin(th * 3.0 + 1.7) + 0.7 * sin(th * 5.0 - 0.9) + 0.9 * t * sin(th * 2.0 + 0.4));
    let dg = pleats + wq * (3.3 * cos(th * 3.0 + 1.7) + 3.5 * cos(th * 5.0 - 0.9) + 1.8 * t * cos(th * 2.0 + 0.4));
    return vec2<f32>(g, dg);
  }
`);
// EACH FOLD ITS OWN DEPTH (2026-10-30): folds cut all alike read as a fluted column -- each valley (between two ridges:
// where the depth changes, nothing shows) `lo` to `hi` of the depth folds had all alike, drawn by its number round the
// piece and the piece's slot, and another at the hem: some deepen as they fall, some die out. Seamless: the number
// wraps at `pleats`
const FOLD = { lo: .4, hi: 1.4 };
// A CASCADE's teeth (a layer's `cascade` [out, step]): each step `grow` x its own distance further apart than the last, `top`
// of their depth at the top growing to all of it at the hem, each turning back in over its last `turn`..1
const CASCADE = { grow: .2, top: .4, turn: .75 };
const foldDeep = wgslFn(`
  fn foldDeep(g: f32, pleats: f32, t: f32, seed: f32) -> f32 {
    let fi = floor(g / 6.2831853);
    let fk = fi - pleats * floor(fi / pleats);
    let h1 = fract(sin(fk * 12.9898 + seed * 4.1414) * 43758.5453);
    let h2 = fract(sin(fk * 78.233 + seed * 1.7321 + 0.5) * 43758.5453);
    return ${FOLD.lo.toFixed(4)} + ${(FOLD.hi - FOLD.lo).toFixed(4)} * mix(h1, h2, t);
  }
`);
// PATCH: how many of the worn pieces are patched, and a patch's width and height (metres)
const PATCH = { share: .3, w: .11, h: .13 };
// SOIL: a long skirt's hem (a pleated piece at least `len` long) darkened up to `h` metres, at most `k`
const SOIL = { h: .09, k: .7, len: .45 };
// SWAGS under a falling edge (2026-10-30: a layer's `edge` -- a mantle's top from one shoulder down under the other arm):
// below that edge its folds run ALONG it, not down -- the roll of a himation, a toga's sinus across the chest -- `gap`
// metres apart at the edge and wider by `grow` of the way down, giving way to the hanging folds from `near` to `far`
// metres below it; `tilt` how far a swag turns the normal (the hanging folds' own is 1.25)
const SWAG = { gap: .03, grow: .3, near: .1, far: .32, tilt: 1.1 };
// how far a fold's valley lifts the hem, as a share of a fold's width (the hem waves as the folds do: a standing
// piece is cut there, so its silhouette waves too)
const HEM_WAVE = .12;
const makeDressFns = (W, ST) => {
  const layerIn = wgslFn(`
    fn layerIn(sTex: texture_2d<f32>, ls: i32, s: f32, th: f32, girth: f32, rad: f32) -> f32 {
      let L0 = texel(sTex, ls * ${ST});
      let L3 = texel(sTex, ls * ${ST} + 3);
      let L4 = texel(sTex, ls * ${ST} + 4);
      let L5 = texel(sTex, ls * ${ST} + 5);
      let fl = L3.z;
      let dags = floor(fl / 256.0) - 64.0 * floor(fl / 16384.0);
      var hem = L0.y;
      if (dags > 0.5) {                          // rounded lobes along the lower edge, as deep as half a lobe is wide
        let lobe = 6.2831853 * max(girth, 0.01) / dags;
        let ph = fract(th * dags / 6.2831853) - 0.5;
        hem = hem - 0.5 * lobe * (1.0 - sqrt(max(1.0 - 4.0 * ph * ph, 0.0)));
      }
      let pleats = fl - 64.0 * floor(fl / 64.0);
      if (pleats > 0.5) {                        // a pleated piece's hem waves with its folds: up in the valleys
        let ph = foldPhase(th, 1.0, pleats).x;
        let v = 0.5 - 0.5 * cos(ph);
        hem = hem - ${HEM_WAVE} * 6.2831853 * max(girth, 0.01) / pleats * v * v * foldDeep(ph, pleats, 1.0, f32(ls));
      }
      // (its top falls round it from L5.w by L5.z: a mantle's edge from one shoulder down under the other arm)
      var e = min(s - L0.x - L5.z * (0.5 - 0.5 * cos(th - L5.w)), hem - s);
      if (L0.w < 3.14) {
        var da = th - L0.z;
        da = da - 6.2831853 * floor((da + 3.1415927) / 6.2831853);
        // (a CASCADE down the opening's edges -- a mantle's ends hanging in zigzag folds: up to L4.z metres out, one
        //  every L4.w down it at its top, further apart and deeper as they fall (CASCADE); each eases out and turns
        //  back in short, as a folded end does; only on a piece with no cut-out of its own, whose L4 is free)
        var cz = 0.0;
        if (L4.x < 0.5 && L4.z > 0.0) {
          let sc = max(s, 0.0);   // (down the PIECE, not the layer: its hem band's teeth run on from the cloth's)
          let fq = fract(log(1.0 + ${CASCADE.grow.toFixed(4)} * sc / max(L4.w, 0.01)) / ${CASCADE.grow.toFixed(4)});
          let tc = clamp(sc / max(L0.y, 0.05), 0.0, 1.0);
          cz = L4.z * (${CASCADE.top.toFixed(4)} + ${(1 - CASCADE.top).toFixed(4)} * tc) * fq * fq * (1.0 - smoothstep(${CASCADE.turn.toFixed(4)}, 1.0, fq));
        }
        e = min(e, (L0.w - abs(da)) * max(girth, 0.01) + cz);
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
  `, [texelFor(W), foldPhase, foldDeep]);
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
               radial: vec3<f32>, axial: f32, relief: ptr<function, vec4<f32>>) -> vec4<f32> {
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
        // (the pattern's own lightness, before the folds shade it: w = 1 + it -- what a carving cuts, shellShade)
        let woven = dot(c, vec3<f32>(0.3, 0.59, 0.11));
        let fl = L3.z;
        let pleats = fl - 64.0 * floor(fl / 64.0);
        let wear = floor(fl / 64.0) - 4.0 * floor(fl / 256.0);
        if (pleats > 0.5) {
          // FOLDS (2026-10-24; were even pleats, a ribbed cone): "pleats" of them round it, but not evenly -- the
          // phase is warped by a few slow waves (more so lower down, where they fan out), so they bunch and spread as
          // cloth falls; shallow gathers at the top of the piece, deepening to the hem. Each is a broad lit ridge and
          // a narrow dark valley (v squared), and the same profile tilts the normal, so a fold catches the light.
          let L0 = texel(sTex, ls * ${ST});
          // (a worn piece running on past its part's ends has no top or hem here: gathers half as deep as a hem's folds)
          let t = select(0.25, clamp((s - L0.x) / max(L0.y - L0.x, 0.01), 0.0, 1.0), L0.x > -100.0 && L0.y < 100.0);
          let gd = foldPhase(th, t, pleats);
          let g = gd.x;
          let dg = gd.y;
          let v = 0.5 - 0.5 * cos(g);
          let fine = 1.0 - smoothstep(0.12, 0.3, px * pleats / (6.2832 * max(girth, 0.01)));
          // (none on an end's cap, where the surface turns to face along the axis: folds round it would meet in a star there)
          let cap = 1.0 - smoothstep(0.3, 0.8, axial);
          let tng = cross(normalize(radial), axis);
          // SWAGS (SWAG above): under a falling edge, folds along it -- its distance below the edge their phase, closer
          // near it; the direction down across them the axis, leaning round with the edge's own slope
          let L5 = texel(sTex, ls * ${ST} + 5);
          var sw = 0.0;
          var swRel = vec3<f32>(0.0);
          var swW = 0.0;
          if (L5.z > 0.001) {
            let dTop = max(s - L0.x - L5.z * (0.5 - 0.5 * cos(th - L5.w)), 0.0);
            sw = 1.0 - smoothstep(${sf(SWAG.near)}, ${sf(SWAG.far)}, dTop);
            let ph = 6.2831853 / ${sf(SWAG.grow)} * log(1.0 + ${sf(SWAG.grow / SWAG.gap)} * dTop);
            let dph = 6.2831853 / (${sf(SWAG.gap)} + ${sf(SWAG.grow)} * dTop);
            let vs = 0.5 - 0.5 * cos(ph);
            let aS = sw * cap * (1.0 - smoothstep(0.12, 0.3, px * dph / 6.2832));
            let gdir = normalize(axis + tng * (0.5 * L5.z * sin(th - L5.w) / max(girth, 0.01)));
            c = c * (1.0 - 0.55 * vs * vs * aS) * (1.0 + 0.14 * (1.0 - vs) * aS);
            swRel = gdir * (-${sf(SWAG.tilt)} * aS * vs * sin(ph));
            swW = vs * vs * aS;
          }
          let amp = (0.35 + 0.65 * t) * fine * cap * (1.0 - sw) * foldDeep(g, pleats, t, f32(ls));
          c = c * (1.0 - 0.55 * v * v * amp) * (1.0 + 0.14 * (1.0 - v) * amp);
          // (and how deep in a valley it lies, w: carved, the stone shades it -- shellShade)
          *relief = vec4<f32>((*relief).xyz + swRel + tng * (-1.25 / pleats * amp * v * sin(g) * dg), max(v * v * amp, swW));
        }
        if (wear > 0.5) { c = c * (1.0 - 0.06 * (fract(sin(dot(floor(uv * 3.0), vec2<f32>(12.9898, 78.233))) * 43758.5453) - 0.5)); }
        // A PATCH (2026-10-24): a worn garment's piece now and then (PATCH.share, by its layer's slot) is darned with a
        // square of near-matching cloth -- a shade off its own, edged with a dashed stitch -- at a place drawn from the
        // same hash, round it and down it; gone where it would be finer than a few pixels
        if (wear > 0.5 && L3.w <= 0.0 && girth > 0.05) {
          let h1 = fract(sin(f32(ls) * 12.9898 + L2.x * 4.13) * 43758.5453);
          if (h1 < ${PATCH.share}) {
            let h2 = fract(h1 * 91.71 + 0.37);
            let h3 = fract(h1 * 57.13 + 0.71);
            let L0p = texel(sTex, ls * ${ST});
            let ps = select(0.12 + 0.25 * h2, mix(L0p.x, L0p.y, 0.3 + 0.4 * h2), L0p.x > -100.0 && L0p.y < 100.0);
            var pth = th - (h3 - 0.5) * 5.0;
            pth = pth - 6.2831853 * floor((pth + 3.1415927) / 6.2831853);
            let q = vec2<f32>(pth * girth, s - ps);
            let hp = vec2<f32>(${PATCH.w / 2} * (0.8 + 0.4 * h3), ${PATCH.h / 2} * (0.8 + 0.4 * h2));
            let d = abs(q) - hp;
            let inP = max(d.x, d.y);
            if (inP < 0.0 && px < ${PATCH.w / 6}) {
              c = c * (0.72 + 0.22 * h2) + unpackRGB8(L1.y) * 0.12;
              let along = select(q.y, q.x, abs(d.y) < abs(d.x));
              if (inP > -0.007 && fract(along * 55.0) < 0.5) { c = c * 0.62; }
            }
          }
        }
        if (wear > 0.5 && pleats > 0.5) {
          // SOILED AT THE HEM (2026-10-24): a skirt that sweeps the street is darker and browner along its lowest hand's
          // breadth, the line ragged -- the folds' valleys (nearer the ground in a wave) a little higher
          let L0h = texel(sTex, ls * ${ST});
          let toHem = L0h.y - s;
          let rag = 0.025 * sin(th * 23.0 + 1.3 * sin(th * 7.0)) + 0.015 * sin(th * 51.0);
          let soil = (1.0 - smoothstep(0.0, ${SOIL.h}, toHem + rag)) * ${SOIL.k} * step(${SOIL.len}, L0h.y - L0h.x);
          c = mix(c, c * vec3<f32>(0.62, 0.55, 0.45), soil);
        }
        if (e < px * 1.4 + 0.0015) { c = c * 0.7; }              // the stitched edge: a hem, a neckline, a seam
        // (carved, that edge is a GROOVE -- a band's border, a mantle's edge, a neckline -- a pixel or more wide however far,
        //  where the pattern's own lines fade: the valley the stone shades, as a fold's is)
        let groove = 1.0 - smoothstep(0.6, 1.0, e / (px * 1.4 + 0.0015));
        *relief = vec4<f32>((*relief).xyz, max((*relief).w, ${sf(STONE.groove)} * groove));
        if (kind > 0.5 && kind < 1.5) { c = c * 0.72; }          // the lining
        return vec4<f32>(c, 1.0 + woven);
      }
      return vec4<f32>(skin, 0.0);
    }
  `, [texelFor(W), layerIn, unpackRGB8, foldPhase, foldDeep]);
  // WHETHER AN ANGLE ROUND A STANDING PIECE IS IN ITS OPENING: every layer wrapped short of it (a mantle's wrap) -- what
  // a carved piece's END is open across too, as its side is (seen through the wrap, its hem's lid was a plate round the legs)
  const dressOpen = wgslFn(`
    fn dressOpen(sTex: texture_2d<f32>, head: vec4<f32>, th: f32) -> bool {
      let n = i32(head.y + 0.5);
      let l0 = i32(head.x + 0.5);
      for (var k: i32 = 0; k < 6; k = k + 1) {
        if (k >= n) { break; }
        let L0 = texel(sTex, (l0 + 2 * k) * ${ST});
        if (L0.w >= 3.14) { return false; }
        var da = th - L0.z;
        da = da - 6.2831853 * floor((da + 3.1415927) / 6.2831853);
        if (abs(da) < L0.w) { return false; }
      }
      return n > 0;
    }
  `, [texelFor(W)]);
  // WHERE A STANDING PIECE'S CLOTH BEGINS round it at angle `th`: x the highest top of its layers there (metres down its
  // axis) -- a mantle's falling edge (layerIn's L5) lower on the side it falls to; -1e3 where none; y 1 if a layer's
  // top falls so (the piece has an edge)
  const dressTop = wgslFn(`
    fn dressTop(sTex: texture_2d<f32>, head: vec4<f32>, th: f32) -> vec2<f32> {
      let n = i32(head.y + 0.5);
      let l0 = i32(head.x + 0.5);
      var top = 1.0e3;
      var edged = 0.0;
      for (var k: i32 = 0; k < 6; k = k + 1) {
        if (k >= n) { break; }
        let L0 = texel(sTex, (l0 + 2 * k) * ${ST});
        let L5 = texel(sTex, (l0 + 2 * k) * ${ST} + 5);
        top = min(top, L0.x + L5.z * (0.5 - 0.5 * cos(th - L5.w)));
        if (L5.z > 1e-4) { edged = 1.0; }
      }
      return vec2<f32>(select(-1.0e3, top, n > 0), edged);
    }
  `, [texelFor(W)]);
  // HOW FAR INSIDE ITS CLOTH an angle round a standing piece is from the nearest edge of its wrap (radians; 1e3 where a
  // layer goes the whole way round): how deep the eye looks into the piece's inside there (STONE.hollowIn)
  const dressEdge = wgslFn(`
    fn dressEdge(sTex: texture_2d<f32>, head: vec4<f32>, th: f32) -> f32 {
      let n = i32(head.y + 0.5);
      let l0 = i32(head.x + 0.5);
      var dIn = 0.0;
      for (var k: i32 = 0; k < 6; k = k + 1) {
        if (k >= n) { break; }
        let L0 = texel(sTex, (l0 + 2 * k) * ${ST});
        if (L0.w >= 3.14) { return 1.0e3; }
        var da = th - L0.z;
        da = da - 6.2831853 * floor((da + 3.1415927) / 6.2831853);
        dIn = max(dIn, L0.w - abs(da));
      }
      return dIn;
    }
  `, [texelFor(W)]);
  // HOW DEEP A FOLD'S VALLEY IS at (s, th) round a pleated piece, in metres: the outermost layer there, its folds as
  // dressAt shades them (each its own depth, shallow at the top, none under a swag), as deep as their shading tilts the
  // normal -- 1.25 x their amplitude x the girth over the pleats; `divs` the grid's points round. Carved, the vertex
  // stage cuts them in (STONE.divs)
  const dressFold = wgslFn(`
    fn dressFold(sTex: texture_2d<f32>, head: vec4<f32>, s: f32, th: f32, girth: f32, divs: f32) -> f32 {
      let n = i32(head.y + 0.5);
      let l0 = i32(head.x + 0.5);
      for (var k: i32 = 0; k < 6; k = k + 1) {
        if (k >= n) { break; }
        let ls = l0 + 2 * k;
        if (layerIn(sTex, ls, s, th, girth, girth) <= 0.0) { continue; }
        let L0 = texel(sTex, ls * ${ST});
        let fl = texel(sTex, ls * ${ST} + 3).z;
        let pleats = fl - 64.0 * floor(fl / 64.0);
        if (pleats < 0.5) { return 0.0; }
        let t = select(0.25, clamp((s - L0.x) / max(L0.y - L0.x, 0.01), 0.0, 1.0), L0.x > -100.0 && L0.y < 100.0);
        let g = foldPhase(th, t, pleats).x;
        let v = 0.5 - 0.5 * cos(g);
        let L5 = texel(sTex, ls * ${ST} + 5);
        var sw = 0.0;
        if (L5.z > 0.001) { sw = 1.0 - smoothstep(${sf(SWAG.near)}, ${sf(SWAG.far)}, max(s - L0.x - L5.z * (0.5 - 0.5 * cos(th - L5.w)), 0.0)); }
        let amp = (${sf(FOLD_TOP)} + ${sf(1 - FOLD_TOP)} * t) * (1.0 - sw) * foldDeep(g, pleats, t, f32(ls));
        // (where the grid has three points a fold round it, fading out below two: fewer, and they alias into dents)
        // (no deeper than its ROOM, clothes.js -- at full depth, shallower toward the top as the folds are: the cloth under
        //  it would come through its valleys)
        let room = floor(fl / 16384.0);
        let cap = select(1.0e3, (room - 1.0) * 0.001 * (${sf(FOLD_TOP)} + ${sf(1 - FOLD_TOP)} * t), room > 0.5);
        return min(1.25 * amp * girth / pleats * v * v * smoothstep(2.0, 3.0, divs / pleats), cap);
      }
      return 0.0;
    }
  `, [texelFor(W), layerIn, foldPhase, foldDeep]);
  return { layerIn, dressLift, dressAt, dressOpen, dressTop, dressEdge, dressFold };
};

// THE CLOTH'S FRAME round a part: its front and its left square to its axis `ax`, whence the angle round it counts
// (from the front toward the left, as the garments' openings expect) -- `fw` the figure's forward, `upW` its up (fw
// square to it); `S1` the part's static row: where it keeps a REST axis (w = -1: composite.js restAxes, in the figure's
// frame), forward and left are carried from that rest to the axis now by the least rotation, so the weave turns with a
// swinging arm instead of sliding round the sleeve. The fragment's (the cloth it paints) and the vertex's (where a
// standing piece's cloth begins round it) are one
const clothFrame = wgslFn(`
  fn clothFrame(fw: vec3<f32>, upW: vec3<f32>, S1: vec4<f32>, ax: vec3<f32>) -> mat2x3<f32> {
    let lf0 = normalize(cross(fw, upW));
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
    return mat2x3<f32>(fwT, lf);
  }
`);

// CLING (2026-10-30): a standing piece hung over the LEGS (clothes.js `cling`: a skirt, a gown) falls from them,
// not as a cone of its own -- round each way from its axis it reaches at least as far as the legs do anywhere above
// that height (cloth falls straight on from the furthest it was pushed: a bent knee carries the front out to the hem)
// plus its ease, and where the cone stands further out it comes in that share of the way (`cling`: a chiton's linen
// lies along the leg, a stiff skirt keeps its bell). It comes in over the first `settle` of its top radius below its
// top (the hips are the torso's) -- unless it drapes over the part it hangs from too (a mantle over the chest: LAID ON,
// packed 2^20 in part.w), and that holds it out at its top as the legs do lower down (nor is it held back by the ONSET
// below: the cape's top is above the chest's), lying WHOLLY on it at its top (its own cling coming back over the
// settle: at its share alone, a cape stood out from the shoulders as a brim) -- and its normal is the drape's own, from steps of `ds` metres down and `dphi`
// radians round it. Packed in the chain's spare texels: ch2 the four legs' slots, part.w 2 + cling% + 256 x ease (0.1 mm).
// OVER THE ARMS too (2026-10-30): a mantle hung over them (clothes.js `arms`) falls from the upper arms it covers as
// from the legs -- their slots in its own chain's spare three (ch.yzw): it hung a lampshade's cone from the shoulders,
// clear of the arms and flaring past them to the hem; draped, it lies on the shoulders and the arms, falls straight
// from the elbows and is pushed out by a knee below.
// HUNG ACROSS, NOT DOWN (2026-10-30): cloth falls straight on from the furthest it was pushed only as far as it hangs
// down its axis; tipped (a figure reclining on its side: its gown's axis along the floor) it GIVES -- what pushed it
// out higher up its axis holds it out less by `give` metres a metre past it, the tangent of the axis's tilt from
// straight down (at most `giveMax`): lying, the cloth lies on each leg as it comes to it and falls off a drawn-up knee
// to the shin, where it had held the knee's reach down to the feet, a closed tube round both legs.
// It comes in over an ONSET (2026-10-30): `onset` of its top radius below the highest point of what it drapes over (a
// hip joint) -- just above it, nothing to fall from, the cone stood as it was, and just below it was pulled in whole:
// the wall stepped in across the skirt there and showed its dark lining through the tear, a slot at the hips
// A TENT OVER THE SHOULDERS (2026-10-30): a piece LAID on reaches over what lies below it too, held out less by `tent`
// metres a metre above a part's end -- a cape from the neck spans down onto the shoulders' round as a tent; above the
// chest's top and the arms' joints it had nothing to fall from, and stood a flat millstone out past the shoulders
// FALLING IN UNDER THE ARM (2026-10-30): an ARM it covers (and its forearm, in the slot after it: skeleton.js `fore`, packed
// 2^21 -- a forearm under the cloth came out through it by the wrist; an end raised above the piece's top, out of it,
// none) holds a mantle out only so far below the arm's end -- it gives
// `fall` metres a metre past it, as a tipped gown gives (the torso and the legs do not): wrapped round the body, the
// cloth falls in from the elbow toward the hips, and it hung a box's walls straight down from both elbows to the hem
// THE HEM RISES WHERE IT IS CARRIED OUT (2026-10-30): cloth pushed out over a limb -- a kneeling figure's thigh, a
// striding knee, a forearm under a mantle -- spends its length going out, and hangs the shorter below: round each way
// the piece is taken in by `rise` of its reach at its hem past its own girth (at most `riseMax` of its length), its rings
// laid over what is left. Kept at its length, a kneeler's skirt fell from the knee to the floor a box
// how far past its layers' top a standing piece's near rim is laid (metres): the cloth surely there under it, the angle
// round it counted per vertex (dressTop)
const EDGE_RIM = .01;
// BETWEEN THE LEGS IT SAGS (2026-10-30): its reach is what it is laid over at the most, a hull -- between two legs a
// straight chord, a seated figure's fall a flat sheet before its shins, a drum. A ray from the axis that meets none of
// the legs where they cross its ring passes through the gap between them: the cloth there sinks `sag` of how far the ray
// misses the nearer one (at most `sagMax` metres) -- the valley between the shins, between a clinging gown's knees.
// It comes in over `sagIn` metres below the legs' top (laid on, no onset there).
// Over the LEGS a piece laid on spans down as a gentler tent, `tentLeg`: at the shoulders' 2.2 the cloth stepped out
// over the hip joints in a shelf round a matron's palla drawn close, and the stola under it
export const CLING = { settle: 1.2, onset: .8, ds: .02, dphi: .06, giveMax: 3, fall: .6, tent: 2.2, rise: .8, riseMax: .6, sag: .6, sagMax: .05, sagIn: .12, tentLeg: .7 };
// how far out from a cut shell's axis (a0, ax0) the legs (and the arms it covers, the chest it hangs from) reach toward
// `dir` (square to the axis) anywhere above `s` metres down it (and, laid on, below it by the `tent`) -- each such part a cone, cut there: its ends' reach plus
// their radii, a FLAT part's (the torso: its radius negative, squashed to C.x along the figure's forward `fwd`) as
// deep as it is that way -- round, the chest stood a barrel's depth out front and back; and how far `s` is below the
// highest of them (y: -1e3 where there is none)
const drapeReach = (W) => wgslFn(`
  fn drapeReach(tex: texture_2d<f32>, own: vec4<f32>, legs: vec4<f32>, a0: vec3<f32>, ax0: vec3<f32>, s: f32, dir: vec3<f32>, give: f32, fwd: vec3<f32>, tent: f32, fore: f32, bust: f32) -> vec2<f32> {
    var h = -1.0e3;
    var top = 1.0e3;
    var miss = 1.0e3;   // (how far the ray misses the nearest leg crossing its ring; under 0: it meets one)
    var legTop = 1.0e3;
    // (the legs, then what it hangs over, then -- fore: the piece's length, 0 for none -- the slot after each of those
    //  that is an ARM, a round part: its forearm, where its elbow is within that length -- a cape on the shoulders ends
    //  above it, and a forearm raised before the chest pushed it up off them -- and the slot after that, its HAND, where
    //  its wrist is: a hand hanging in a mantle had its fingers out through the cloth)
    var over = array<f32, 13>(legs.x, legs.y, legs.z, legs.w, own.y, own.z, own.w, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0);
    if (fore > 0.5) {
      for (var j: i32 = 4; j < 7; j = j + 1) {
        if (over[j] > -0.5 && unpackAw(texel(tex, i32(over[j] + 0.5) * 3).w).x >= 0.0) {
          over[j + 3] = over[j] + 1.0;
          // (the hand: the flat part after the forearm -- people.js adds arm, forearm, hand in that order)
          if (unpackAw(texel(tex, i32(over[j] + 2.5) * 3).w).x < 0.0) { over[j + 6] = over[j] + 2.0; }
        }
      }
    }
    for (var j: i32 = 0; j < 13; j = j + 1) {
      if (over[j] < -0.5) { continue; }
      let A = texel(tex, i32(over[j] + 0.5) * 3);
      let B = texel(tex, i32(over[j] + 0.5) * 3 + 1);
      if (B.w < 0.0) { continue; }
      let rA0 = unpackAw(A.w).x;
      // (an arm: a round part it hangs over -- or the HAND after its forearm, flat but the arm's end: the cloth falls in
      //  under it as under the forearm, or it hung walls straight down from both hands to the hem, a box)
      let arm = j >= 4 && (rA0 >= 0.0 || j >= 10);
      if (j >= 7 && dot(A.xyz - a0, ax0) > fore) { continue; }
      let Cq = texel(tex, i32(over[j] + 0.5) * 3 + 2);
      var sc = 1.0;
      if (rA0 < 0.0 && Cq.x > 1e-3) {
        let axP = B.xyz - A.xyz;
        var wq = fwd - axP * (dot(fwd, axP) / max(dot(axP, axP), 1e-10));
        if (Cq.y > 0.5) { wq = cross(axP, fwd); }   // (a hand: squashed across its own axis and the figure's forward, palm in)
        let f = dot(dir, wq) / max(length(wq), 1e-5);
        sc = sqrt(Cq.x * Cq.x * f * f + max(1.0 - f * f, 0.0));
      }
      let rA = abs(rA0) * sc;
      let rB = B.w * sc;
      let pa = dot(A.xyz - a0, ax0);
      let pb = dot(B.xyz - a0, ax0);
      top = min(top, min(pa, pb));
      if (j < 4) { legTop = min(legTop, min(pa, pb)); }
      let gv = select(give, give + ${sf(CLING.fall)}, arm);   // (an arm: the cloth falls in under it)
      // (an arm's end RAISED above the piece's top is out of it: it holds nothing out -- it hung a curtain from the hand)
      if (pa <= s && !(arm && pa < 0.0)) { h = max(h, dot(A.xyz - a0, dir) + rA - gv * (s - pa)); }
      if (pb <= s && !(arm && pb < 0.0)) { h = max(h, dot(B.xyz - a0, dir) + rB - gv * (s - pb)); }
      // (not a forearm's: one raised before the chest pushed a cape up off the shoulder, its lining gaping)
      let tj = select(tent, min(tent, ${sf(CLING.tentLeg)}), j < 4);
      if (tent > 0.0 && j < 7 && pa > s) { h = max(h, dot(A.xyz - a0, dir) + rA - tj * (pa - s)); }
      if (tent > 0.0 && j < 7 && pb > s) { h = max(h, dot(B.xyz - a0, dir) + rB - tj * (pb - s)); }
      if ((pa - s) * (pb - s) < 0.0) {
        let f = (s - pa) / (pb - pa);
        // (carved -- bust: 1 -- a woman's torso is swelled by her BUST, shell.js TRUNK: what lies on it lies on that,
        //  or a himation's cape went in under the bodice the bust lifts, its pleats' crests a row of beads through it)
        var bz = 0.0;
        if (bust > 0.5 && rA0 < 0.0 && Cq.y < 0.5 && Cq.z > 32768.5) {
          let axP = normalize(B.xyz - A.xyz);
          var fq = fwd - axP * dot(fwd, axP);
          var dq = dir - axP * dot(dir, axP);
          if (dot(fq, fq) > 1e-8 && dot(dq, dq) > 1e-8) {
            fq = normalize(fq);
            dq = normalize(dq);
            let c2 = (Cq.z - 1.0) - 16384.0 * floor((Cq.z - 1.0) / 16384.0);
            let tq = mix(c2 - 128.0 * floor(c2 / 128.0), floor(c2 / 128.0), f) * 0.01;
            bz = mix(abs(rA0), B.w, f) * trunkBust(Cq.z, tq, abs(dot(dq, cross(axP, fq))) * sc, dot(dq, fq));
          }
        }
        h = max(h, dot(mix(A.xyz, B.xyz, f) - a0, dir) + mix(rA, rB, f) + bz);
        if (j < 4) {
          let q = mix(A.xyz, B.xyz, f) - a0 - ax0 * s;
          let qd = dot(q, dir);
          if (qd > -mix(rA, rB, f)) { miss = min(miss, length(q - dir * qd) - mix(rA, rB, f)); }
        }
      }
    }
    if (miss < 1.0e2) { h = h - ${sf(CLING.sag)} * clamp(miss, 0.0, ${sf(CLING.sagMax / CLING.sag)}) * smoothstep(0.0, ${sf(CLING.sagIn)}, s - legTop); }
    return vec2<f32>(h, s - top);
  }
`, [texelFor(W), unpackAw, trunkBust]);
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
    let mark = part.w > 0.5 && part.w < 1.5;   // (a cut shell clinging to the legs: 2 and up -- CLING)
    // A PLATE'S ROWS BY NUMBER (a membrane, a face mark: 2026-10-24): the centre of its front face, rings out to its rim,
    // the rim again on the back face, rings in to the back's centre. Laid out by fractions of u (the front to 0.45, the
    // rim to 0.55), a grid of an odd number of rings had no row in the rim's band at all: every wing membrane was drawn
    // shrunk to 89% round its middle on the 5-ring grid, and its shared edges opened into wedges (a manticore's wing).
    let kP = floor(uv.x * nr + 0.5);
    let mF = max(floor((nr - 1.0) * 0.5), 1.0);
    let backP = kP > mF;
    let fP = select(kP / mF, (nr - kP) / max(nr - mF - 1.0, 1.0), backP);   // 0 at a face's centre, 1 on the rim

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
    var liftK = 1.0;                     // how much further what is worn lifts this point (a joint's mitre: below)
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
      let rad2 = fP;                       // 0 at the centre, 1 at the rim, both halves
      let face = select(1.0, -1.0, backP);
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
      // the front face, flat, out to the rim; the back face back from it (the rim between them is the strip from the one
      // to the other -- A PLATE'S ROWS BY NUMBER, above)
      P = mix(g, rim, fP) + nrm * select(th, -th, backP);
      N = select(nrm, -nrm, backP);
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
      // THE RINGS BY NUMBER (2026-10-24): a JOINT is always a ring of its own, at every detail. Spread by fractions
      // of u, an arm's elbow fell between two rings on the middle grid (5 rings: past a few metres), and a bent arm
      // was drawn as one chord from the upper arm to the forearm. Each cap gets its share of the grid's rings, each
      // span of the chain a whole number of the rest, so its joints fall on ring boundaries. (Too few rings for one
      // per span -- a long tail far off -- spreads them by fractions as before.)
      let capF = 0.2;
      var x = 0.0;
      let kR = floor(uv.x * nr + 0.5);
      let capR = max(1.0, floor(nr * capF + 0.5));
      let spanR = nr - 2.0 * capR;
      if (spanR >= f32(cnt) && ${SHELL.seam ? "true" : "false"}) {
        if (kR < capR) { x = (kR / capR - 1.0) * 0.5; }
        else if (kR > nr - capR) { x = f32(cnt) + (kR - (nr - capR)) / capR * 0.5; }
        else {
          let m = kR - capR;
          var j: i32 = 0;
          loop {
            if (j + 1 >= cnt || m < floor(f32(j + 1) * spanR / f32(cnt) + 0.5)) { break; }
            j = j + 1;
          }
          let m0 = floor(f32(j) * spanR / f32(cnt) + 0.5);
          let m1 = floor(f32(j + 1) * spanR / f32(cnt) + 0.5);
          x = f32(j) + (m - m0) / max(m1 - m0, 1.0);
        }
      } else if (uv.x < capF) { x = (uv.x / capF - 1.0) * 0.5; }
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
      //   A JOINT BETWEEN TWO LONG SPANS (an elbow, a knee, a hock: each span longer than the joint is thick) is a
      // MITRE instead -- see "THE JOINT IS A SEAM" below: each span keeps its own axis right up to the joint, and only
      // the girth hands over. (Turning the rings' direction toward the other span over the last half of each, as
      // these still do, pinched a bent elbow to cos(half the bend) of its girth and bowed both bones into it.)
      let tubeI = CB[i].w < -1.5;          // THIS span's own curve (a chain may be all tubes: a tail)
      var mitF = false;                    // the far joint, the near one: mitred
      var mitN = false;
      if (i + 1 < cnt && !tubeI && CB[i + 1].w >= -1.5) {   // the far joint
        let a2 = CA[i + 1].xyz;
        let b2 = CB[i + 1].xyz;
        let L2 = max(length(b2 - a2), 1e-4);
        let rJ = mix(CB[i].w, abs(CK[i + 1].x), 0.5);
        mitF = min(Li, L2) > 2.0 * rJ && ${SHELL.seam ? "true" : "false"};
        let w = smoothstep(0.55, 1.0, t);
        if (w > 0.0) {
          cen = mix(cen, mix(bi, a2, 0.5), w);
          rr = mix(rr, rJ, w);
          if (!mitF) { dir = normalize(mix(dir, (b2 - a2) / L2, w * 0.5)); }
          slope = mix(slope, (CB[i + 1].w - abs(CK[i + 1].x)) / L2, w * 0.5);
        }
      }
      if (i > 0 && !tubeI && CB[i - 1].w >= -1.5) {         // ...and the near one
        let a0 = CA[i - 1].xyz;
        let b0 = CB[i - 1].xyz;
        let L0 = max(length(b0 - a0), 1e-4);
        let rJ = mix(CB[i - 1].w, abs(CK[i].x), 0.5);
        mitN = min(Li, L0) > 2.0 * rJ && ${SHELL.seam ? "true" : "false"};
        let w = 1.0 - smoothstep(0.0, 0.45, t);
        if (w > 0.0) {
          cen = mix(cen, mix(b0, ai, 0.5), w);
          rr = mix(rr, rJ, w);
          if (!mitN) { dir = normalize(mix(dir, (b0 - a0) / L0, w * 0.5)); }
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
        // THE JOINT IS A SEAM (2026-10-24), shared by the two spans that meet there: the ring ON the joint is where
        // both cones cross the plane halfway between their directions (the mitre), and every point of a span is kept
        // on its own side of that plane, moved along its own axis onto it if it lies past (the inside of a bend,
        // where the two would pass through each other). One ring of points, the same seen from either side, which
        // moves with both -- a sleeve bends at the elbow as one sheet. Its normal is the two cones' mean, so the
        // crease shades soft; and what is worn lifts it further along that normal (liftK: the mitre is wider than
        // either cone's ring by 1 / cos of half the bend).
        if (!tubeI && (mitN || mitF)) {
          let seam = mitN && tl < 1e-4;
          var other = vec3<f32>(0.0);
          for (var e: i32 = 0; e < 2; e = e + 1) {
            let k = select(i + 1, i - 1, e == 0);
            if ((e == 0 && !mitN) || (e == 1 && !mitF)) { continue; }
            let dk = normalize(CB[k].xyz - CA[k].xyz);
            let Jk = select(mix(bi, CA[k].xyz, 0.5), mix(CB[k].xyz, ai, 0.5), e == 0);
            let nk = normalize(dir + dk);       // (the plane's normal, pointing on along the chain)
            let sd = dot(P - Jk, nk);
            let past = select(sd > 0.0, sd < 0.0, e == 0) || (seam && e == 0);
            if (past) {
              P = P - dir * (sd / max(dot(dir, nk), 0.2));
              let q = P - Jk;
              other = normalize(q - dk * dot(q, dk));
            }
          }
          if (dot(other, other) > 0.5) {
            let own = N;
            N = normalize(N + other);
            liftK = 1.0 / max(dot(N, own), 0.25);
          }
        }
      }
      // A LIMB'S ROOT (2026-10-24): an arm's top is the shoulder, a leg's the hip -- they belong to the body as much as to
      // the limb. Swept rigidly with the limb, the arm's round top swung out behind the shoulder as the arm came forward
      // (a sleeve that is a separate tube stuck on). A part flagged root (its length in its dress header's z, negative;
      // its rest axis kept by composite.js restAxes, in the figure's frame) keeps its cap at that rest, and its rings turn
      // from the rest to the limb's own axis over its first root metres, about the joint: a skinned shoulder -- the
      // sleeve's top stays sewn in where it was, and the arm bends out of it.
      let RS2 = texel(sTex, i32(sl[0] + 0.5) * ${ST} + 2);
      let RS1 = texel(sTex, i32(sl[0] + 0.5) * ${ST} + 1);
      let rootL = -RS2.z;
      if (rootL > 1e-4 && RS1.w < -0.5 && RS1.w > -1.5 && RS2.w > 0.5 && !tubeI && ${SHELL.seam ? "true" : "false"}) {
        let a0 = CA[0].xyz;
        let d0v = CB[0].xyz - a0;
        let L0r = max(length(d0v), 1e-4);
        let wR = select(1.0 - smoothstep(0.0, rootL / L0r, x), 1.0, x < 0.0);
        if (wR > 0.0) {
          let ur = i32(RS2.w + 0.5);
          var upR = texel(tex, (ur - 1) * 3 + 1).xyz - texel(tex, (ur - 1) * 3).xyz;
          upR = select(upB, normalize(upR), dot(upR, upR) > 1e-10);
          var fwR = fwB - upR * dot(fwB, upR);
          fwR = select(fwB, normalize(fwR), dot(fwR, fwR) > 1e-8);
          let lfR = normalize(cross(fwR, upR));
          let r0 = normalize(fwR * RS1.x + upR * RS1.y + lfR * RS1.z);
          let d0 = d0v / L0r;
          var kx = cross(d0, r0);
          let sn = length(kx);
          if (sn > 1e-4) {
            kx = kx / sn;
            // (held back no further than its length can bend without folding: a ring's inner side passes the next one's once
            //  the turn per metre times the radius passes 1, and smoothstep turns 1.5 times its mean rate at its steepest -- an
            //  arm straight up kept its top hanging, and the inside of that turn came out over the shoulder as a spike)
            let held = min(atan2(sn, dot(d0, r0)), rootL / (1.8 * max(abs(CK[0].x), 0.01)));
            let phi = held * wR;
            let cR = cos(phi);
            let sR = sin(phi);
            let q = P - a0;
            P = a0 + q * cR + cross(kx, q) * sR + kx * (dot(kx, q) * (1.0 - cR));
            N = N * cR + cross(kx, N) * sR + kx * (dot(kx, N) * (1.0 - cR));
          }
        }
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
        // (a PALM -- C.y: a hand -- is squashed across its own axis and the figure's forward instead: it faces in, to
        //  the thigh, as it hangs; down as it is held out to the side; in again raised overhead; and up held out forward,
        //  where the two are one and the fallback below turns it to the world's up. It faced forward hanging: a paddle.)
        var w = select(fwd - ax * dot(fwd, ax), cross(fwd, ax), C4.y > 0.5);
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
          // (the inner rings at the OUTER ones' heights, in reverse: laid at their own spacing, on an even grid one fewer, a
          //  sharp turn of the drape -- a forearm's tent under a mantle -- fell between two outer rings on an inner one, and
          //  the lining came out through the cloth a dark diamond. An even grid's spare ring lies on the low end's.)
          let mR = max(floor((nr - 1.0) * 0.5), 2.0);  // outer rings 1..mR, the high rim mR + 1, inner rings after (shellGrid's too)
          // A STANDING PIECE BEGINS WHERE ITS CLOTH DOES (2026-10-30): round each way, at its layers' top there (dressTop:
          // a mantle's falling edge), not at the cone's -- its rings laid from there and its near rim there. Cut at the
          // cone's top and its cloth cut out below by the fragment, the wall stood on at the cone's girth above the edge,
          // and through the gap to the body under it the lining showed: a dark slot along every himation's edge.
          // (EDGE_RIM past the layers' own top: the cloth is surely there under the rim, the angle counted by vertex)
          var loE = loS;
          var edged = false;
          let PS2 = texel(sTex, i32(sl[0] + 0.5) * ${ST} + 2);
          if (PS2.z > 0.5) {
            var upC = upS;
            let urC = i32(PS2.w + 0.5);
            var fwC = fwS;
            if (urC > 0) {
              let du = texel(tex, (urC - 1) * 3 + 1).xyz - texel(tex, (urC - 1) * 3).xyz;
              upC = select(upC, normalize(du), dot(du, du) > 1e-10);
              let fwp = fwS - upC * dot(fwS, upC);
              fwC = select(fwS, normalize(fwp), dot(fwp, fwp) > 1e-8);
            }
            let cF = clothFrame(fwC, upC, texel(sTex, i32(sl[0] + 0.5) * ${ST} + 1), ax0);
            let rd = frame1 * cos(uv.y * 6.2831853) + frame2 * sin(uv.y * 6.2831853);
            let tE = dressTop(sTex, PS2, atan2(dot(rd, cF[1]), dot(rd, cF[0])));
            edged = tE.y > 0.5;
            loE = clamp(tE.x + ${sf(EDGE_RIM)}, loS, loS + 0.8 * (hiS - loS));
          }
          var sPos = loE;
          var outer = 1.0;
          var rimF = -1.0;                         // -1: not on a rim; else how far across it (0: its inner end)
          if (kR < 0.5) { sPos = loE; rimF = 0.0; }
          else if (kR <= mR) { sPos = mix(loE, hiS, (kR - 1.0) / max(mR - 1.0, 1.0)); }
          else if (kR < mR + 1.5) { sPos = hiS; rimF = 0.0; }
          else { sPos = mix(hiS, loE, min((kR - mR - 2.0) / max(mR - 1.0, 1.0), 1.0)); outer = 0.0; }
          // (its CLING word, CLING above: what it drapes over and how -- read here for the hem's rise, below for the drape)
          let cwF = part.w - 2.0;
          let foreD = floor(cwF / 2097152.0);
          let cwL = cwF - foreD * 2097152.0;
          let laid = floor(cwL / 1048576.0);
          let cw = cwL - laid * 1048576.0;
          let eq = floor(cw / 256.0);
          let eC = eq * 0.0001;
          let upG = ${viewSpace ? "(view * vec4<f32>(0.0, 1.0, 0.0, 0.0)).xyz" : "vec3<f32>(0.0, 1.0, 0.0)"};
          let cG = clamp(-dot(ax0, upG), 0.0, 1.0);
          let give = min(sqrt(1.0 - cG * cG) / max(cG, 1e-3), ${sf(CLING.giveMax)});
          let tentD = select(0.0, ${sf(CLING.tent)}, laid > 0.5);
          let foreL = select(0.0, hiS, foreD > 0.5);   // (forearms, where their elbows are within its length)
          let flB = texel(sTex, i32(sl[0] + 0.5) * ${ST}).w;
          let bustD = select(0.0, 1.0, floor(flB / 2048.0) - 8.0 * floor(flB / 16384.0) > 0.5);   // (carved: over the bust)
          // THE HEM'S RISE (CLING above): the reach at the hem this way round past the cone's girth there, taken off its length
          if (part.w > 1.5 && floor(C4.z * 0.25) < 0.5 && hiS > loE) {
            var oH = (frame1 * cos(uv.y * 6.2831853) + frame2 * sin(uv.y * 6.2831853)) * mix(r0, r1e, clamp(hiS / L0, 0.0, 1.0)) / cos(3.14159265 / max(part.z, 3.0));
            if (C4.w > 0.01 && C4.w < 0.999) {
              var wH = fwS - ax0 * dot(fwS, ax0);
              wH = select(frame1, normalize(wH), dot(wH, wH) > 1e-8);
              oH = oH - wH * (dot(oH, wH) * (1.0 - C4.w));
            }
            let rOH = max(length(oH), 1e-5);
            let hH = drapeReach(tex, ch, ch2, a0, ax0, hiS, oH / rOH, give, fwS, tentD, foreL, bustD).x + eC;
            let rise = select(0.0, min(${sf(CLING.rise)} * max(hH - rOH, 0.0), ${sf(CLING.riseMax)} * (hiS - loE)), hH > -1.0);
            sPos = loE + (sPos - loE) * (1.0 - rise / (hiS - loE));
          }
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
            // CARVED, a garment's shell is full at both: its waistband closed over the gap to the body as painted (mode 3),
            // its hem too, as every carved cut is (statues.js) -- a himation's top had stood off the chiton a hollow shelf
            let atHi = sPos > loS + (hiS - loS) * 0.5;
            let mode = C4.z - 4.0 * floor(C4.z / 4.0);
            let thinSlab = (hiS - loS) < 0.5 * rMax;
            // (painted, a falling edge is cloth's own thickness, open on the gap to the body; carved, it is closed too: the
            //  thick roll of a himation's edge laid round the hips)
            let fl0 = texel(sTex, i32(sl[0] + 0.5) * ${ST}).w;
            let carved = floor(fl0 / 2048.0) - 8.0 * floor(fl0 / 16384.0) > 0.5;
            let farShut = (mode > 1.5 && mode < 2.5) || (mode > 2.5 && carved);
            let lid = select(rc < 0.62 * rMax || thinSlab || !filled || (mode > 2.5 && (carved || !edged)), farShut || thinSlab, atHi);
            let inner = select(rIn, 0.0, lid);
            P = a0 + ax0 * sPos + radial * mix(inner, rc * circ, rimF);
            N = select(ax0, -ax0, sPos <= loE + 1e-5);
          } else {
            // THE LINING'S FIRST RING UNDER A CLOSED HIGH CUT starts at the axis. The high rim runs in to the lid's
            // centre, and the lining's first ring is on that same plane -- at rIn it laid a second disc, a lining's,
            // in the lid's own plane, and the two fought (the underside of every brim: its axis runs down). From the
            // centre the step between them is no surface at all.
            var rLin = rHere;
            if (outer < 0.5 && kR > mR + 1.5 && kR < mR + 2.5) {
              let modeL = C4.z - 4.0 * floor(C4.z / 4.0);
              let flL = texel(sTex, i32(sl[0] + 0.5) * ${ST}).w;
              let shutL = (modeL > 1.5 && modeL < 2.5) || (modeL > 2.5 && floor(flL / 2048.0) - 8.0 * floor(flL / 16384.0) > 0.5);
              if (shutL || (hiS - loS) < 0.5 * max(max(r0, r1e), 1e-4)) { rLin = 0.0; }
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
          // THE CLING (CLING above): over the legs, the outer wall at least their reach above here plus its ease, and the
          // cone's excess taken in by its cling; the lining and the rims moved with it, the cloth's thickness kept
          if (part.w > 1.5) {
            // (and a bell does not stand on its side: tipped, it clings the more, wholly lying along the floor)
            let kS = smoothstep(0.0, ${sf(CLING.settle)} * r0, sPos - loS);
            // (LAID on, it lies wholly on what it is draped over at its top, its own cling coming back over the settle)
            let kC = select(mix((cw - 256.0 * eq) * 0.01, 1.0, 1.0 - cG) * kS, mix(1.0, mix((cw - 256.0 * eq) * 0.01, 1.0, 1.0 - cG), kS), laid > 0.5);
            var oOut = radial * rc * circ;
            if (C4.w > 0.01 && C4.w < 0.999) {
              var wD = fwS - ax0 * dot(fwS, ax0);
              wD = select(frame1, normalize(wD), dot(wD, wD) > 1e-8);
              oOut = oOut - wD * (dot(oOut, wD) * (1.0 - C4.w));
            }
            let rOut = max(length(oOut), 1e-5);
            let dirD = oOut / rOut;
            let rD = drapeReach(tex, ch, ch2, a0, ax0, sPos, dirD, give, fwS, tentD, foreL, bustD);
            let hD = rD.x + eC;
            let gap = select(0.0, max(hD - rOut, -0.8 * rOut), hD > -1.0);   // (no leg above here yet: the cone as it is)
            let wDr = select(kC * max(smoothstep(0.0, ${sf(CLING.onset)} * r0, rD.y), laid), 1.0, gap > 0.0);
            let rP = length(P - (a0 + ax0 * sPos));
            P = P + dirD * (wDr * gap * clamp(rP / max(rOut - 2.0 * thick, 1e-4), 0.0, 1.0));
            if (rimF < 0.0 && wDr > 0.0) {
              let tD = cross(ax0, dirD);
              let dHs = (drapeReach(tex, ch, ch2, a0, ax0, sPos + ${sf(CLING.ds)}, dirD, give, fwS, tentD, foreL, bustD).x + eC - hD) / ${sf(CLING.ds)};
              let dHp = (drapeReach(tex, ch, ch2, a0, ax0, sPos, normalize(dirD + tD * ${sf(CLING.dphi)}), give, fwS, tentD, foreL, bustD).x + eC - hD) / ${sf(CLING.dphi)};
              let nH = normalize(dirD - ax0 * dHs - tD * (dHp / rOut));
              N = normalize(mix(N, select(-nH, nH, outer > 0.5), wDr));
            }
          }
          // ITS FOLDS CUT IN (STONE.divs: a carved piece near by is drawn with points enough round): each valley pushed in as
          // deep as dressFold says -- the outer wall, the lining and the rims alike, the cloth's thickness kept, a lid's
          // centre where it is -- round the angle the fragment paints them at, so the shading and the silhouette agree
          let flF = texel(sTex, i32(sl[0] + 0.5) * ${ST}).w;
          if (floor(flF / 2048.0) - 8.0 * floor(flF / 16384.0) > 0.5 && floor(flF / 1024.0) - 2.0 * floor(flF / 2048.0) > 0.5) {   // (carved, and dressed)
            var upF = upS;
            var fwF = fwS;
            let urF = i32(PS2.w + 0.5);
            if (urF > 0) {
              let du = texel(tex, (urF - 1) * 3 + 1).xyz - texel(tex, (urF - 1) * 3).xyz;
              upF = select(upF, normalize(du), dot(du, du) > 1e-10);
              let fwp = fwS - upF * dot(fwS, upF);
              fwF = select(fwS, normalize(fwp), dot(fwp, fwp) > 1e-8);
            }
            let cFF = clothFrame(fwF, upF, texel(sTex, i32(sl[0] + 0.5) * ${ST} + 1), ax0);
            let sF = dot(P - a0, ax0);
            let rqF = P - a0 - ax0 * sF;
            let rPF = length(rqF);
            if (rPF > 1e-5) {
              let dF = dressFold(sTex, PS2, sF, atan2(dot(rqF, cFF[1]), dot(rqF, cFF[0])), max(rc, 0.004), part.z);
              P = P - rqF / rPF * (dF * clamp(rPF / max(2.0 * thick, 1e-4), 0.0, 1.0));
            }
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
          P = P + N * liftK * dressLift(sTex, texel(sTex, i32(rs + 0.5) * ${ST} + 2), sL, thD, max(length(qd), 0.004), length(qd));
        }
      } else if (floor(rfl / 2048.0) - 8.0 * floor(rfl / 16384.0) > 0.5) {
        ringSlot = rs;   // (carved, bare: its own part too -- a limb's muscles are its own, shell.js LIMBS)
      }
    }
    // CARVED LIMBS: a bare limb's muscles swell its outline too -- the calf, the deltoid, the thigh's teardrop seen against
    // the sky (LIMBS.swell of the field the fragment tilts the light by), eased off toward its joints (limbEase)
    if (!mark && !triPart && !isCut && CK[ringI].z < 0.5 && CK[ringI].x > 0.0) {
      let rsL = i32(CK[ringI].w + 0.5);
      let flL = texel(sTex, rsL * ${ST}).w;
      let cL = texel(tex, rsL * 3 + 2).x;
      if (floor(flL / 2048.0) - 8.0 * floor(flL / 16384.0) > 0.5 && cL > 0.5 && cL < 31.5) {
        var upL = ${viewSpace ? "(view * vec4<f32>(0.0, 1.0, 0.0, 0.0)).xyz" : "vec3<f32>(0.0, 1.0, 0.0)"};
        let urL = i32(texel(sTex, rsL * ${ST} + 2).w + 0.5);
        if (urL > 0) {
          let du = texel(tex, (urL - 1) * 3).xyz - texel(tex, (urL - 1) * 3 + 1).xyz;   // (the chest runs down from its A end)
          upL = select(upL, normalize(du), dot(du, du) > 1e-10);
        }
        var fwL = texel(tex, base * 3 + 1).xyz - texel(tex, base * 3).xyz;
        fwL = fwL - upL * dot(fwL, upL);
        if (dot(fwL, fwL) > 1e-10) {
          let fr = limbCoord(P, CA[ringI].xyz, CB[ringI].xyz, cL, normalize(fwL), upL);
          let kind = i32(fr[2].z + 0.5);
          if (kind > 0) {
            let sA = fr[2].x;
            let rad = mix(abs(CK[ringI].x), CB[ringI].w, clamp(sA, 0.0, 1.0));
            P = P + N * (${sf(LIMBS.relief / .06 * LIMBS.swell)} * select(1.0, ${sf(LIMBS.soft)}, cL > 15.5) * rad * limbH(kind, clamp(sA, 0.0, 1.0), fr[2].y) * limbEase(kind, sA));
          }
        }
      }
    }
    // CARVED TRUNK: a bare torso's outline is its cone's too, a straight line from the armpit to the waist and on to the
    // hip -- swelled by the anatomy the fragment cuts in (the pectorals' plate in profile) and by the TRUNK's masses (the
    // lats' flare under the arms, the flanks over the iliac line, the buttocks), as a limb's by its muscles (trunkSwell)
    if (!mark && !triPart && !isCut && CK[ringI].x < 0.0) {
      let rsT = i32(CK[ringI].w + 0.5);
      let flT = texel(sTex, rsT * ${ST}).w;
      let cT = texel(tex, rsT * 3 + 2);
      if (floor(flT / 2048.0) - 8.0 * floor(flT / 16384.0) > 0.5 && cT.y < 0.5 && cT.z > 0.5) {
        let fwT = texel(tex, base * 3 + 1).xyz - texel(tex, base * 3).xyz;
        let bareT = select(1.0, 0.0, floor(flT / 1024.0) - 2.0 * floor(flT / 2048.0) > 0.5);   // (dressed: the bust alone)
        if (dot(fwT, fwT) > 1e-10) { P = P + N * trunkSwell(P, CA[ringI].xyz, CB[ringI].xyz, abs(CK[ringI].x), CB[ringI].w, cT.z, fwT, bareT); }
      }
    }
    // FLEECE (bit 512): wool heaped in lumps -- the surface pushed out by a field of blobs fixed to the animal (in its
    // root's frame: forward, up, left from the part's A end), ${FLEECE.size} m across, up to ${FLEECE.amp} m proud
    if (!mark && !triPart && !isCut) {
      let fl5 = texel(sTex, i32(CK[ringI].w + 0.5) * ${ST}).w;
      if (floor(fl5 / 512.0) - 2.0 * floor(fl5 / 1024.0) > 0.5) {
        let q0f = texel(tex, base * 3).xyz;
        var fwF = texel(tex, base * 3 + 1).xyz - q0f;
        fwF = select(vec3<f32>(1.0, 0.0, 0.0), normalize(fwF), dot(fwF, fwF) > 1e-10);
        let upF = ${viewSpace ? "(view * vec4<f32>(0.0, 1.0, 0.0, 0.0)).xyz" : "vec3<f32>(0.0, 1.0, 0.0)"};
        let lfF = normalize(cross(fwF, upF));
        let rel = P - q0f;
        let l = vec3<f32>(dot(rel, fwF), dot(rel, upF), dot(rel, lfF)) * ${(6.2832 / FLEECE.size).toFixed(3)};
        let b = sin(l.x + 1.3 * sin(l.z * 0.7)) * sin(l.y + 1.3 * sin(l.x * 0.8)) * sin(l.z + 1.3 * sin(l.y * 0.9));
        P = P + N * (${FLEECE.amp} * (0.55 + 0.45 * b));
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
`, [texelFor(W), unpackAw, sdRoundCone, LIB.capsuleNormal, LIB.tubeUnpack, LIB.tubeR, LIB.bezier3, dressFns(W, ST).dressLift, dressFns(W, ST).dressTop, dressFns(W, ST).dressFold, clothFrame, drapeReach(W), limbCoord, limbH, limbEase, trunkSwell]);

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
// HOW STONE TAKES THE LIGHT (2026-10-29): a carving reads by its shade -- the world's Lambert keeps .62 of the light on
// the side away from the sun (light.js), which leaves a figure flat as paper, so stone keeps less (`ambient`); its
// shade is a little WARM where light comes through the marble (`warm`, the shadow's share); it darkens toward its
// edges as a round form turns from the eye (`rim`: at grazing view, `rimPow` its fall-off) -- the hollows between the
// folds and the limbs' sides; marble's VEINS are soft grey drifts (`veins` how dark, `veinSharp` how thin), not
// cracks. CARVE: what is woven or embroidered into a garment (a meander border, a stripe) is cut into the stone --
// its lines darker where the pattern's colour changes across a pixel (`incise` at most, from a change of `inciseMin`, full `1/inciseK` past it: the weave's own faint grain is not cut) -- as far as the eye can make the lines out: a carved line is `inciseLine` wide, and where that is under a pixel or two the cut fades (a meander seen from across a square was a scatter of broken dashes) -- but a layer's own EDGE, a band's border, a mantle's, is a groove at any distance (`groove` of a fold's valley), a fold's valley in shade (`fold`); an opening's inside, its far wall, in shade (`hollow`: a sleeve's mouth); and a carved head's hollows
// (heads.js CAVITY: the sockets, the creases -- `cavity` their share) and its hair cut in LOCKS (`locks` across the
// hair a unit of its u, `lockDark` the groove between two, `lockWave` how far across, in locks, they wave down it, an S
// every `lockLen` metres, each `lockPhase` radians behind the last (nearly in step: hair waves as a mass, and locks
// each its own way were worms), `lockRelief` metres high: their slope tilts the light across them)
// A HAND'S FINGERS (2026-10-30): a palm part (people.js `palm`, a flat hand) is a mitten -- its fingers are grooves cut
// along its far part, `count` across its broad side (the figure's forward, as shell.js turns the palm), from `from` of
// its length over the tip; each `width` of a finger, its walls turned in by `tilt` (they catch the light as a cut does)
// and its floor `dark` in stone (`paint` of that on a painted hand); finer than a pixel or two, they fade
export const FINGERS = { count: 4, from: .5, width: .22, tilt: .6, dark: .35, paint: .4 };
// CARVED ANATOMY (2026-10-30): a statue's bare torso is a mannequin's smooth flattened cone without it -- the sculptor's
// anatomy is cut in as a relief (a height field over the trunk, its slope tilting the light; its grooves `dark` in shade):
// where on the trunk a point is comes from its piece's `anat` (people.js: its ends' heights from the crotch, 0, to the
// shoulders' rim, 1 -- t below), how far across from the middle line in its half-width (u: 0 the middle, 1 the side).
// A man's: the PECTORALS a plate overhanging the ribs, their lower edge at `pecLow` mid-chest, `pecMid` higher at the
// sternum, rising `pecRise` x (u - .5)^2 to the armpit, the edge `pecEdge` soft; the LINEA ALBA down the middle (`linea`
// wide, `lineaD` deep) from the pubis to the sternum; the RECTUS raised `rectus` inside `absU`, crossed by its
// intersections at `abs` (`absW` wide, `absD` deep); the RIBS' arch outside it, from `rib` at the sternum falling
// `ribSlope` a half-width (raised `ribH`); the ILIAC FURROW -- the line of the classical torso, from the pubis up round
// the hip (t = `iliac` + `iliacK` u^`iliacP`, `iliacW` wide, `iliacD` deep) with the obliques swelling over it (`bulge`);
// the NAVEL (`navel` high, `navelR` round, `navelD` deep). A woman's (her figure is the cone's): the navel and a soft
// middle line. The back: the SPINE's groove and the SHOULDER BLADES (`blade` across, `bladeT` high, raised `bladeH`).
// Over the top, on the shoulders' cap (t past 1): the COLLARBONES, a ridge from `clavIn` out to `clavOut` at t `clav`
// rising `clavRise` a half-width (`clavW` wide, raised `clavH`), and the NOTCH between their heads at the neck's foot
// (`notch` high, `notchR` round, `notchD` deep) -- a woman's half as marked; without them the chest's top was a dome
// Its depth `relief` metres at a half-width of .17 (a colossus's deeper); finer than the pixel, it fades to `far`
export const ANATOMY = { relief: .007, dark: .22, far: .35, pecLow: .66, pecMid: .03, pecRise: .7, pecEdge: .028, pecTop: .9, pecH: 1.8,
  linea: .05, lineaD: .8, rectus: .3, absU: .36, abs: [.585, .5, .42], absW: .024, absD: .35, rib: .6, ribSlope: .17, ribH: .35,
  iliac: .05, iliacK: .27, iliacP: 1.5, iliacW: .028, iliacD: .9, bulge: .5, navel: .37, navelR: .032, navelD: 1.1,
  spine: .055, spineD: .7, blade: .45, bladeT: .8, bladeH: .6,
  clav: 1.02, clavRise: .05, clavW: .024, clavH: .6, clavIn: .07, clavOut: .8, notch: 1.045, notchR: .055, notchD: 1.3 };
// CARVED LIMBS (2026-10-30): a statue's bare arm or leg is a tube without them -- its MUSCLES cut in the way the trunk's
// anatomy is (a height field round the limb, its slope tilting the light, its grooves `dark`). A limb knows its kind
// and side (people.js LIMB, in its third texel); round it the angle `a` counts from its FRONT (the figure's forward, or
// up where the limb points forward: a seated thigh's top) toward its OUTER side (+90; the inner -90, the back 180), and
// t runs down it from its root (0) to its end (1). Each feature an oval in (t, a): [t, a, wt, wa, h, slant] -- `wt`
// and `wa` its half-sizes (wa degrees), `h` its height in reliefs (a groove's negative), `slant` how far it turns
// round the limb a whole length down (the sartorius' diagonal, a deltoid's edge). The thigh: the rectus down its front,
// the vastus medialis' teardrop over the knee, the lateralis outside, the sartorius' groove from the hip's front down
// round to the inner knee, the kneecap under the tendon's dip, the hamstrings and the knee's hollow behind. The shin:
// the tibia's tuberosity and the tibialis beside its edge, the calf's two heads (the inner lower and fuller) parted by
// a groove, the soleus' swell under them, the ankle bones. The upper arm: the deltoid's cap and the V of its lower
// edge, the biceps, the triceps, the groove inside between them. The forearm: the brachioradialis' swell outside below
// the elbow (a third of the way down: at the joint itself the arm above meets it smooth), the extensors behind it,
// the flexors inside. The foot (its front up, t from the heel to the toes): the toes parted by four grooves over its
// tip (the big toe's deepest), the arch's hollow inside, the instep's rise. `relief` metres a reliefs' unit at a radius of .06, `soft` of it on a soft body (people.js LIMB)
export const LIMBS = { relief: .016, dark: .35, far: .35, swell: .7, soft: .35, ease: .12, loose: { shin: [0, 1], foot: [1, 1] },
  thigh: [[.45, 0, .32, 35, 1], [.82, -55, .1, 28, 1.5], [.55, 65, .28, 30, .9], [.45, -20, .38, 9, -.7, -130], [.87, 0, .035, 26, -.3],
          [1, 0, .07, 30, .9], [.5, 180, .3, 50, .5], [.55, 180, .25, 8, -.4], [1, 180, .05, 40, -.6], [.6, 100, .3, 8, -.4]],
  shin: [[0, 0, .075, 30, .9], [0, 180, .055, 40, -.6], [.13, -5, .05, 20, .5], [.3, 35, .25, 25, .8], [.4, 12, .3, 7, -.4], [.26, -150, .13, 32, 1.7], [.23, 150, .12, 30, 1.3],
         [.25, 180, .15, 7, -.5], [.5, -115, .14, 25, .6], [.48, 115, .14, 25, .6], [.985, -90, .03, 25, .9], [1, 95, .03, 25, .8]],
  arm: [[.14, 90, .2, 60, 1.5], [.12, 30, .15, 35, .8], [.25, 55, .14, 8, -.6, 233], [.25, 125, .14, 8, -.6, -233], [.58, 0, .2, 45, 1.4],
        [.42, 180, .22, 50, 1], [.75, 180, .1, 30, -.4], [.55, -90, .3, 10, -.6], [.62, 95, .2, 9, -.4]],
  fore: [[.3, 70, .12, 40, 1.4], [.36, 140, .14, 35, .7], [.34, -60, .14, 45, 1], [.55, -150, .32, 8, -.4]],
  foot: [[1.1, -44, .06, 10, -.8], [1.12, -15, .06, 9, -.7], [1.12, 14, .06, 9, -.65], [1.1, 42, .055, 9, -.6], [.45, -130, .25, 25, -1],
         [.55, 10, .3, 30, .5]] };
// (`divs`: how many times the nearest grid's points round a carved cut shell -- a statue's cloth -- has: its folds CUT
//  IN, its silhouette waving with them, where a painted piece's folds are shading alone; statues are few)
// PAINT on a statue (STONES painted): how much of the marble's mottle shows through it (+-), its waxed sheen, its glow in
// the shade (of the marble's STONE.warm), how much purer than the cloth's dye its drapery is painted, the carving's shade
// per channel (the power its darkening is raised to: under 1 holds on); ivory's own colour
export const PAINT = { mottle: .05, sheen: .07, warm: .5, vivid: .45, shade: [.7, .95, 1.35], ivory: [.93, .86, .72] };
export const STONE = { divs: 4, ambient: .42, warm: .14, rim: .32, rimPow: 2.2, veins: .16, veinSharp: 7, incise: .4, inciseK: 3, inciseMin: .06, inciseLine: .003, groove: .7, fold: .5, hollow: .45, hollowIn: .12, cavity: 1.3, locks: 18, lockDark: .36, lockWave: .35, lockPhase: .55, lockLen: .055, lockRelief: .0022 };
const sf = (v) => Number(v).toFixed(4);
// value noise in 3D, three octaves, 0..1 -- the lattice hashed in integers (a sin() hash in f32 tears at the cells' seams
// far from the origin, where the world's statues stand)
const stoneHash = wgslFn(`
  fn stoneHash(c: vec3<f32>) -> f32 {
    let k = bitcast<vec3<u32>>(vec3<i32>(c));
    var v = (k.x * 73856093u) ^ (k.y * 19349663u) ^ (k.z * 83492791u);
    v = v * 747796405u + 2891336453u;
    v = ((v >> ((v >> 28u) + 4u)) ^ v) * 277803737u;
    return f32((v >> 22u) ^ v) / 4294967295.0;
  }
`);
const stoneNoise = wgslFn(`
  fn stoneNoise(p: vec3<f32>) -> f32 {
    var f = 0.0; var amp = 0.5; var q = p;
    for (var o = 0; o < 3; o = o + 1) {
      let i = floor(q); let u = fract(q); let w = u * u * (3.0 - 2.0 * u);
      let x0 = mix(mix(stoneHash(i), stoneHash(i + vec3<f32>(1.0, 0.0, 0.0)), w.x),
                   mix(stoneHash(i + vec3<f32>(0.0, 1.0, 0.0)), stoneHash(i + vec3<f32>(1.0, 1.0, 0.0)), w.x), w.y);
      let x1 = mix(mix(stoneHash(i + vec3<f32>(0.0, 0.0, 1.0)), stoneHash(i + vec3<f32>(1.0, 0.0, 1.0)), w.x),
                   mix(stoneHash(i + vec3<f32>(0.0, 1.0, 1.0)), stoneHash(i + vec3<f32>(1.0, 1.0, 1.0)), w.x), w.y);
      f = f + amp * mix(x0, x1, w.z); amp = amp * 0.5; q = q * 2.13;
    }
    return f / 0.875;
  }
`, [stoneHash]);
const stoneAt = wgslFn(`
  fn stoneAt(m: f32, pw: vec3<f32>, n: vec3<f32>, eye: vec3<f32>, carve: f32, sh: vec2<f32>, paint: vec4<f32>) -> vec3<f32> {
    // (chryselephantine: its drapery and its hair gold, its flesh ivory -- the surface's own kind, paint.w, decides)
    let chrys = m > 5.5 && m < 6.5;
    let k = select(m, select(7.0, 3.0, paint.w < 0.5 || paint.w > 1.5), chrys);
    let f = stoneNoise(pw * 6.0);          // the mottle
    let fw = stoneNoise(pw * 1.3 + 7.0);   // the slow drift a vein wanders by
    let N = normalize(n);
    let L = vec3<f32>(${SUN.join(", ")});
    let V = normalize(eye - pw);
    let H = normalize(L + V);
    let nl = max(dot(N, L), 0.0) * sh.y;
    // (the world's Lambert with stone's own ambient: the sky's share from above, the sun's; sh its own shade, selfShade)
    let amb = ${sf(STONE.ambient)} * (${sf(1 - LIGHT.sky)} + ${sf(LIGHT.sky)} * (0.5 + 0.5 * N.y)) * sh.x;
    let lam = amb + ${sf(1 - STONE.ambient)} * nl;
    let rim = 1.0 - ${sf(STONE.rim)} * pow(1.0 - clamp(abs(dot(N, V)), 0.0, 1.0), ${sf(STONE.rimPow)});
    let nh = max(dot(N, H), 0.0);
    var base = vec3<f32>(0.86, 0.84, 0.80);
    var spec = 0.0;
    var tint = vec3<f32>(1.0);
    var warm = vec3<f32>(0.0);
    if (k < 1.5) {                       // marble: warm white, a soft mottle, grey veins drifting through it; light in its shade
      let v = abs(sin(pw.x * 1.1 + pw.y * 1.7 + pw.z * 0.8 + 7.0 * fw + 0.6 * f));
      base = vec3<f32>(0.92, 0.9, 0.86) * (0.95 + 0.08 * f) - vec3<f32>(0.62, 0.6, 0.56) * (${sf(STONE.veins)} * pow(1.0 - v, ${sf(STONE.veinSharp)}));
      spec = pow(nh, 24.0) * 0.1;
      warm = vec3<f32>(1.0, 0.82, 0.66) * ${sf(STONE.warm)};
    } else if (k < 2.5) {                // bronze: dark warm metal, greener in its hollows
      base = mix(vec3<f32>(0.36, 0.25, 0.13), vec3<f32>(0.24, 0.36, 0.28), smoothstep(0.55, 0.8, f) * 0.6);
      spec = pow(nh, 36.0) * 0.55; tint = vec3<f32>(1.0, 0.82, 0.55);
    } else if (k < 3.5) {                // gold: bright, a hard highlight
      base = vec3<f32>(0.86, 0.64, 0.22) * (0.92 + 0.12 * f);
      spec = pow(nh, 48.0) * 0.9 + pow(nh, 8.0) * 0.12; tint = vec3<f32>(1.0, 0.9, 0.6);
    } else if (k < 4.5) {                // limestone: warm, pitted
      base = vec3<f32>(0.80, 0.75, 0.64) * (0.88 + 0.2 * f);
      spec = pow(nh, 12.0) * 0.05;
      warm = vec3<f32>(1.0, 0.9, 0.75) * ${sf(STONE.warm * .5)};
    } else if (k < 5.5) {                // painted: the surface's own colour laid on the marble, the stone's mottle under it, a waxed sheen
      // (the drapery's dyes as the painters' mineral pigments, purer than a wool's: its colour pushed off its grey, PAINT.vivid)
      let gr = dot(paint.xyz, vec3<f32>(0.3, 0.55, 0.15));
      let pc = select(paint.xyz, max(mix(vec3<f32>(gr), paint.xyz, ${sf(1 + PAINT.vivid)}), vec3<f32>(0.0)), paint.w < 0.5);
      base = pc * (${sf(1 - PAINT.mottle)} + ${sf(2 * PAINT.mottle)} * f);
      spec = pow(nh, 16.0) * ${sf(PAINT.sheen)};
      warm = vec3<f32>(1.0, 0.86, 0.72) * ${sf(STONE.warm * PAINT.warm)};
    } else {                             // ivory: warm, close-grained, glowing in its shade (chryselephantine's flesh: its own colour, ivory)
      base = select(vec3<f32>(${PAINT.ivory.join(", ")}), paint.xyz, chrys) * (0.96 + 0.06 * f);
      spec = pow(nh, 20.0) * 0.16;
      warm = vec3<f32>(1.0, 0.84, 0.64) * ${sf(STONE.warm * 1.4)};
    }
    // (painted and ivory, the shade is WARM -- the red and the yellow hold on as the light and the carving darken it,
    //  PAINT.shade: grey on a pale skin read as a beard's shadow round the mouth)
    let pv = vec3<f32>(${PAINT.shade.join(", ")});
    let cv = select(vec3<f32>(carve), pow(vec3<f32>(max(carve, 0.0)), pv), k > 4.5);
    let lv = select(vec3<f32>(lam), pow(vec3<f32>(max(lam, 0.0)), pv), k > 4.5);
    let lit = base * cv * rim;
    return lit * lv + lit * warm * (1.0 - nl) * sh.x + tint * spec * carve * sh.y * smoothstep(-0.05, 0.3, dot(N, L));
  }
`, [stoneNoise]);
// A CARVING'S OWN SHADE (2026-10-30): stone keeps its form by the shadows the figure throws on itself -- an arm on the
// flank, the head on the chest, a mantle's fold over the knee -- and by the dark where two forms meet (the armpit, the
// gap between the legs); a white figure without them read flat as a cut-out across a square. Every part of the figure
// (a cone from A to B, its radii r1..r2) is an occluder of the point: its OCCLUSION the cosine-weighted share of the sky
// a ball of its radius at its nearest point hides (`ao` times that: a cone hides more than its ball), and the SUN it
// stands in the way of -- the ray from the point toward the sun passes it nearer than its radius, the shadow's edge
// soft by `pen` of the distance along that ray (a penumbra that widens away from the caster). What holds the point --
// a part it lies inside, its own, a joint's neighbour -- is skipped. A STANDING piece (a skirt, a mantle) casts only
// from its HEM -- on what lies past it, the legs under a tunic, the chiton under a himation's edge: its cone is cloth
// only where its arcs are, and as a whole it threw boxes of shade over the chiton its wrap leaves bare (`inside`: within that share of its radius) --
// and not on one laid over it (a longer himation round a chiton's hem), and
// parts thinner than `minR` (fingers, the strands of hair) cast nothing. `sun` how dark the shadow it throws, `minAo`
// how dark the occlusion goes at most. Parts: the figure's own (its first slot, how many: the static flags' bits from
// 16384 up, composite.js). ?selfshade=0 leaves it out
export const SELF = { ao: 1.3, minAo: .45, sun: .85, pen: .3, inside: 1.04, minR: .02 };
const SELF_OFF = typeof location !== "undefined" && new URLSearchParams(location.search).get("selfshade") === "0";   // (?selfshade=0: without it, to compare)
const selfShade = (W, ST, viewSpace) => wgslFn(`
  fn selfShade(tex: texture_2d<f32>, sTex: texture_2d<f32>, invView: mat4x4<f32>, pw: vec3<f32>, n: vec3<f32>, me: i32, first: i32, count: i32) -> vec2<f32> {
    let L = vec3<f32>(${SUN.join(", ")});
    var occ = 0.0;
    var lit = 1.0;
    let meStands = texel(sTex, me * ${ST} + 2).z > 0.5;
    for (var j = first; j < first + count; j = j + 1) {
      if (j == me) { continue; }
      let A4 = texel(tex, j * 3);
      let B4 = texel(tex, j * 3 + 1);
      let r1 = abs(unpackAw(A4.w).x);
      if (B4.w < 0.0 || max(r1, B4.w) < ${sf(SELF.minR)}) { continue; }
      let A = ${viewSpace ? "(invView * vec4<f32>(A4.xyz, 1.0)).xyz" : "A4.xyz"};
      let D = ${viewSpace ? "(invView * vec4<f32>(B4.xyz, 1.0)).xyz" : "B4.xyz"} - A;
      let dd = max(dot(D, D), 1e-8);
      if (texel(sTex, j * ${ST} + 2).z > 0.5) {
        // (a standing piece casts from its HEM: the point past it along its axis, whose ray to the sun crosses the hem's
        //  plane within its ring, is under it)
        let len = sqrt(dd);
        let ax = D / len;
        let past = dot(pw - A, ax) - len;
        let la = dot(L, ax);
        // (...but not on a standing piece laid OVER it -- laid from the skin out, a later one: a himation round a chiton,
        //  longer, is outside it and lit from outside)
        if (past > 0.0 && la < -0.05 && !(meStands && j < me)) {
          let t = -past / la;
          let q = pw + L * t - A - D;
          let e = clamp((length(q - ax * dot(q, ax)) - B4.w) / (${sf(SELF.pen)} * t + 0.004) + 0.5, 0.0, 1.0);
          lit = min(lit, e * e * (3.0 - 2.0 * e));
        }
        continue;
      }
      let u = clamp(dot(pw - A, D) / dd, 0.0, 1.0);
      let rr = mix(r1, B4.w, u);
      let v = A + D * u - pw;
      let dist = length(v);
      if (dist < rr * ${sf(SELF.inside)}) { continue; }
      // (the occlusion: the ball at the nearest point, as the normal sees it)
      occ = occ + clamp(dot(n, v) / dist, 0.0, 1.0) * (rr * rr) / (dist * dist);
      // (the sun: the ray's nearest pass by the axis -- two steps of nearest-point back and forth)
      var t = max(dot(A + D * u - pw, L), 0.0);
      var u2 = clamp(dot(pw + L * t - A, D) / dd, 0.0, 1.0);
      t = max(dot(A + D * u2 - pw, L), 0.0);
      u2 = clamp(dot(pw + L * t - A, D) / dd, 0.0, 1.0);
      let h = length(pw + L * t - A - D * u2);
      let r2 = mix(r1, B4.w, u2);
      let e = clamp((h - r2) / (${sf(SELF.pen)} * t + 0.004) + 0.5, 0.0, 1.0);
      lit = min(lit, select(1.0, e * e * (3.0 - 2.0 * e), t > 0.0));
    }
    return vec2<f32>(max(1.0 - ${sf(SELF.ao)} * occ, ${sf(SELF.minAo)}), 1.0 - ${sf(SELF.sun)} * (1.0 - lit));
  }
`, [texelFor(W), unpackAw]);
// CARVED HAIR AND HOLLOWS on a mesh head (heads.js: its `hairMask`, the hair's uv -- u across it, v down it in metres --
// and the face's `cavity`): the normal (xyz) and the darkening (w) stoneAt is given. Each lock is a rounded ridge in
// RELIEF, its normal tilted across it as its slope is (the surface gradient of its height, from the pixel's own
// derivatives: no tangents needed), and it waves down the head as an S, a little behind the one before it -- straight grooves
// down the meridians read as a ribbed pot, lit flat; the grooves and the tilt fade where a lock is under a pixel or two
// CARVED CURLS (2026-10-30): a beard's, a Buddha's snail curls -- domes packed over the surface (a Voronoi of jittered
// points `size` apart in the world: statues stand still), each rising from the groove where it meets the next to its
// own middle, a SPIRAL cut round it `turns` times; the normal tilted out from each middle by `relief`, the grooves in
// shade (`dark`, `spiral`), all fading where a curl is under a few pixels. -> the normal (xyz) and the darkness (w)
export const CURLS = { size: .013, relief: 1, dark: .55, spiral: .45, turns: 1.3 };
const stoneCurls = wgslFn(`
  fn stoneCurls(pw: vec3<f32>, n: vec3<f32>) -> vec4<f32> {
    let q = pw / ${sf(CURLS.size)};
    let i = floor(q);
    var d1 = 9.0; var d2 = 9.0; var c1 = vec3<f32>(0.0);
    for (var x = -1; x <= 1; x = x + 1) { for (var y = -1; y <= 1; y = y + 1) { for (var z = -1; z <= 1; z = z + 1) {
      let c = i + vec3<f32>(f32(x), f32(y), f32(z));
      let p = c + 0.15 + 0.7 * vec3<f32>(stoneHash(c), stoneHash(c + vec3<f32>(17.0, 0.0, 0.0)), stoneHash(c + vec3<f32>(0.0, 31.0, 0.0)));
      let d = length(q - p);
      if (d < d1) { d2 = d1; d1 = d; c1 = p; } else if (d < d2) { d2 = d; }
    } } }
    let nn = normalize(n);
    var t = q - c1;
    t = t - nn * dot(t, nn);
    let r = clamp(2.0 * d1 / max(d1 + d2, 1e-4), 0.0, 1.0);
    let h = sqrt(max(1.0 - r * r, 0.0));
    let px = length(fwidth(q));
    let seen = clamp(1.6 - px * 2.5, 0.0, 1.0);
    let tl = max(length(t), 1e-4);
    let tilt = (t / tl) * (${sf(CURLS.relief)} * r / max(h, 0.3));
    var b1 = cross(nn, vec3<f32>(0.0, 1.0, 0.3));
    b1 = normalize(select(b1, vec3<f32>(1.0, 0.0, 0.0), dot(b1, b1) < 1e-6));
    let b2 = cross(nn, b1);
    let sp = fract(atan2(dot(t, b2), dot(t, b1)) / 6.2831853 + r * ${sf(CURLS.turns)});
    let groove = smoothstep(0.2, 0.0, min(sp, 1.0 - sp)) * smoothstep(0.1, 0.3, r) * smoothstep(1.0, 0.8, r) * clamp(1.4 - px * ${sf(CURLS.turns * 2.5)}, 0.0, 1.0);
    let dark = 1.0 - seen * (${sf(CURLS.dark)} * (1.0 - h) + ${sf(CURLS.spiral)} * groove);
    return vec4<f32>(normalize(nn + tilt * seen), dark);
  }
`, [stoneHash]);
const stoneCarve = wgslFn(`
  fn stoneCarve(tv: vec2<f32>, mask: f32, cav: f32, pw: vec3<f32>, n: vec3<f32>, cm: f32) -> vec4<f32> {
    let j = floor(tv.x * ${sf(STONE.locks)});
    let x = tv.x * ${sf(STONE.locks)} + sin(tv.y * ${sf(2 * Math.PI / STONE.lockLen)} + j * ${sf(STONE.lockPhase)}) * ${sf(STONE.lockWave)};
    let f = fract(x);
    let fx = fwidth(x);
    let seen = clamp(1.5 - fx * 2.0, 0.0, 1.0) * mask;
    let ridge = sqrt(max(sin(3.14159265 * f), 0.0));
    let slope = ${sf(STONE.lockRelief * Math.PI)} * cos(3.14159265 * f);
    let nn = normalize(n);
    var dx = dpdx(x);
    var dy = dpdy(x);
    if (abs(dx) > 0.5) { dx = 0.0; }   // (across a lock's edge its phase jumps: no slope there)
    if (abs(dy) > 0.5) { dy = 0.0; }
    let px = dpdx(pw);
    let py = dpdy(pw);
    let r1 = cross(py, nn);
    let r2 = cross(nn, px);
    let det = dot(px, r1);
    let gx = (r1 * dx + r2 * dy) / select(det, 1e-12, abs(det) < 1e-12);
    let lock = 1.0 - ${sf(STONE.lockDark)} * (1.0 - ridge) * seen;
    let hol = 1.0 - min(0.7, ${sf(STONE.cavity)} * cav);
    if (cm > 0.5) { let c = stoneCurls(pw, nn); return vec4<f32>(c.xyz, c.w * hol); }   // (curls, not locks: CURLS)
    return vec4<f32>(normalize(nn - gx * (slope * seen)), lock * hol);
  }
`, [stoneCurls]);

// the same stone on a plain mesh (a statue's sword in its hand) or a carved HEAD (`head`: its hair in locks, its hollows
// -- the geometry carries hairMask, uv and cavity): one material a stone, made once. A PAINTED stone (PAINTED) reads its
// colours from the geometry's own `color` -- a head's skin, eyes, lips and hair, an item's -- the head's hair (its mask)
// as hair, the rest of it as skin, an item as drapery is
const STONE_MATS = new Map();
export function stoneMaterial(m, { head = false } = {}) {
  const key = m + (head ? "h" : "");
  if (!STONE_MATS.has(key)) {
    const mat = new THREE.MeshBasicNodeMaterial();
    const carve = head ? stoneCarve({ tv: uv(), mask: attribute("hairMask", "float"), cav: attribute("cavity", "float"), pw: positionWorld, n: normalWorld, cm: attribute("curl", "float") }) : null;
    const paint = PAINTED.has(m) ? vec4(attribute("color", "vec3"), head ? attribute("hairMask", "float").add(1) : float(0)) : vec4(1, 1, 1, 0);
    mat.colorNode = stoneAt({ m: float(m), pw: positionWorld, n: carve ? carve.xyz : normalWorld, eye: cameraPosition, carve: carve ? carve.w : float(1), sh: vec2(1, 1), paint });
    STONE_MATS.set(key, mat);
  }
  return STONE_MATS.get(key);
}
// A STATUE'S MATERIAL (statues.js `stone`): marble, bronze, gold, limestone -- or PAINTED, as the Greeks' marble was: its
// dress in its colours, its skin, hair and eyes (shell.js paints them from the figure's own: stoneAt's `paint`);
// CHRYSELEPHANTINE, Phidias' gold and ivory: the drapery and hair gold, the flesh ivory; IVORY. (3 bits: composite.js)
export const STONES = { marble: 1, bronze: 2, gold: 3, limestone: 4, painted: 5, chryselephantine: 6, ivory: 7 };
export const PAINTED = new Set([STONES.painted, STONES.chryselephantine]);

// THE ANATOMY's height (in `relief`s) at u across, t up the trunk, zf how far round toward the front (1) or the back (-1)
const anatomyH = wgslFn(`
  fn anatomyH(u: f32, t: f32, zf: f32, fem: f32) -> f32 {
    let low = ${sf(ANATOMY.pecLow)} + ${sf(ANATOMY.pecMid * 2)} * max(0.5 - u, 0.0) + ${sf(ANATOMY.pecRise)} * max(u - 0.5, 0.0) * max(u - 0.5, 0.0);
    let belly = smoothstep(low + 0.02, low - 0.04, t);
    let pec = smoothstep(-${sf(ANATOMY.pecEdge)}, ${sf(ANATOMY.pecEdge)}, t - low) * smoothstep(${sf(ANATOMY.pecTop + .14)}, ${sf(ANATOMY.pecTop)}, t) * smoothstep(1.0, 0.75, u);
    let lin = exp(-(u * u) / ${sf(ANATOMY.linea * ANATOMY.linea)}) * smoothstep(0.1, 0.22, t) * smoothstep(0.95, 0.8, t);
    let inR = smoothstep(${sf(ANATOMY.absU + .06)}, ${sf(ANATOMY.absU - .04)}, u) * smoothstep(0.12, 0.2, t) * belly;
    var ints = 0.0;
    ${ANATOMY.abs.map((ti) => `ints = ints + exp(-(t - ${sf(ti)}) * (t - ${sf(ti)}) / ${sf(ANATOMY.absW * ANATOMY.absW)});`).join(" ")}
    let rib = smoothstep(-0.03, 0.03, t - (${sf(ANATOMY.rib)} - ${sf(ANATOMY.ribSlope)} * u)) * smoothstep(${sf(ANATOMY.absU)}, ${sf(ANATOMY.absU + .12)}, u) * smoothstep(1.05, 0.85, u) * belly;
    let tI = ${sf(ANATOMY.iliac)} + ${sf(ANATOMY.iliacK)} * pow(max(u, 0.0), ${sf(ANATOMY.iliacP)});
    let fur = exp(-(t - tI) * (t - tI) / ${sf(ANATOMY.iliacW * ANATOMY.iliacW)}) * smoothstep(0.08, 0.2, u) * smoothstep(1.1, 0.9, u);
    let obl = exp(-(t - tI - 0.07) * (t - tI - 0.07) / 0.0025) * smoothstep(0.45, 0.75, u);
    let nav = exp(-(u * u + (t - ${sf(ANATOMY.navel)}) * (t - ${sf(ANATOMY.navel)})) / ${sf(ANATOMY.navelR * ANATOMY.navelR)});
    let tC = ${sf(ANATOMY.clav)} + ${sf(ANATOMY.clavRise)} * u;
    let clav = exp(-(t - tC) * (t - tC) / ${sf(ANATOMY.clavW * ANATOMY.clavW)}) * smoothstep(${sf(ANATOMY.clavIn)}, ${sf(ANATOMY.clavIn + .06)}, u) * smoothstep(${sf(ANATOMY.clavOut)}, ${sf(ANATOMY.clavOut - .15)}, u);
    let notch = exp(-(u * u + (t - ${sf(ANATOMY.notch)}) * (t - ${sf(ANATOMY.notch)})) / ${sf(ANATOMY.notchR * ANATOMY.notchR)});
    let man = pec * ${sf(ANATOMY.pecH)} - lin * ${sf(ANATOMY.lineaD)} + inR * (${sf(ANATOMY.rectus)} - ints * ${sf(ANATOMY.absD)}) + rib * ${sf(ANATOMY.ribH)} - fur * ${sf(ANATOMY.iliacD)} + obl * ${sf(ANATOMY.bulge)};
    let front = mix(man, -lin * ${sf(ANATOMY.lineaD * .4)}, fem) - nav * ${sf(ANATOMY.navelD)} + mix(1.0, 0.5, fem) * (clav * ${sf(ANATOMY.clavH)} - notch * ${sf(ANATOMY.notchD)});
    let spine = exp(-(u * u) / ${sf(ANATOMY.spine * ANATOMY.spine)}) * smoothstep(0.12, 0.25, t) * smoothstep(1.0, 0.88, t);
    let blades = exp(-((u - ${sf(ANATOMY.blade)}) * (u - ${sf(ANATOMY.blade)}) / 0.04 + (t - ${sf(ANATOMY.bladeT)}) * (t - ${sf(ANATOMY.bladeT)}) / 0.01));
    let back = blades * ${sf(ANATOMY.bladeH)} - spine * ${sf(ANATOMY.spineD)};
    return smoothstep(-0.1, 0.55, zf) * front + smoothstep(-0.1, 0.55, -zf) * back;
  }
`);
// ...on a torso's piece from A (rA its half-width there) to B (rB), its place on the trunk packed in `code` (people.js
// anat), `fwd` the figure's forward, px the pixel's footprint: the normal's tilt (xyz) and the darkness (w), ANATOMY above
const anatomyAt = wgslFn(`
  fn anatomyAt(pw: vec3<f32>, A: vec3<f32>, B: vec3<f32>, rA: f32, rB: f32, code: f32, fwd: vec3<f32>, px: f32) -> vec4<f32> {
    let d = B - A;
    let len = max(length(d), 1e-5);
    let ax = d / len;
    var fw = fwd - ax * dot(fwd, ax);
    if (dot(fw, fw) < 1e-8) { return vec4<f32>(0.0); }
    fw = normalize(fw);
    let side = cross(ax, fw);
    let c = code - 1.0;
    let c2 = c - 16384.0 * floor(c / 16384.0);
    let fem = min(floor(c / 16384.0), 1.0);
    let tB = floor(c2 / 128.0) * 0.01;
    let tA = (c2 - 128.0 * floor(c2 / 128.0)) * 0.01;
    let sA = dot(pw - A, ax) / len;
    let t = mix(tA, tB, sA);
    let rad = max(mix(rA, rB, clamp(sA, 0.0, 1.0)), 1e-3);
    let q = pw - A - ax * (sA * len);
    let x = dot(q, side) / rad;
    let zf = dot(q, fw) / max(length(q), 1e-5);
    let u = abs(x);
    let h0 = anatomyH(u, t, zf, fem);
    let dhu = (anatomyH(u + 0.01, t, zf, fem) - h0) * 100.0;
    let dht = (anatomyH(u, t + 0.01, zf, fem) - h0) * 100.0;
    let k = ${sf(ANATOMY.relief / .17)} * rad;
    let seen = mix(1.0, ${sf(ANATOMY.far)}, smoothstep(0.5, 2.0, px / (0.18 * rad)));
    let g = k * (dhu * sign(x) * side / rad + dht * ax * ((tB - tA) / len));
    return vec4<f32>(-g * seen, clamp(-h0, 0.0, 1.0) * ${sf(ANATOMY.dark)} * seen);
  }
`, [anatomyH]);
// THE TRUNK's MASSES (2026-10-30), the outline a bare carved torso swells to (shell.js CARVED TRUNK, its vertices) -- each
// [t, w, h]: a swell h of the half-width at t up the trunk (as ANATOMY's), w wide, round its sides or its back: a man's
// LATS flaring under the arms (the V of the athlete's back, seen from before) and his FLANKS, the obliques over the iliac
// line; anyone's HIPS at the great trochanter, a woman's FULL HIP, the BUTTOCKS behind (`buttockU` off the middle), the
// CHEST's arch before and the LUMBAR hollow of the back over them; and the anatomy's relief itself `swell` x as proud
// (the pectorals' plate in profile). Without them the trunk was a cone from armpit to hip, a slab seen from the side.
// And a woman's BUST (`bust` [t, w, h], each breast `bustU` off the middle, `bustW` across): hers dressed too -- the
// bodice is lifted off the swelled surface, so a chiton clings over it as the sculptor's wet drapery does
export const TRUNK = { swell: .7, lats: [.68, .2, .1], flanks: [.3, .08, .05], hips: [.08, .08, .03], fullHip: [.17, .12, .05],
  buttocks: [.17, .07, .2], buttockU: .42,
  chest: [.76, .16, .08], lumbar: [.38, .1, -.06], bust: [.78, .11, .35], bustU: .48, bustW: .2 };
// a woman's BUST at t up the trunk, u across it, zf its forward share (anat `code`: people.js -- 0 but for a woman), in its
// half-widths: what the carved trunk swells by dressed (trunkSwell) and what cloth laid on it lies on (drapeReach)
const trunkBust = wgslFn(`
  fn trunkBust(code: f32, t: f32, u: f32, zf: f32) -> f32 {
    let woman = floor((code - 1.0) / 32768.0);
    return woman * ${sf(TRUNK.bust[2])} * exp(-(t - ${sf(TRUNK.bust[0])}) * (t - ${sf(TRUNK.bust[0])}) / ${sf(TRUNK.bust[1] * TRUNK.bust[1])})
           * exp(-(u - ${sf(TRUNK.bustU)}) * (u - ${sf(TRUNK.bustU)}) / ${sf(TRUNK.bustW * TRUNK.bustW)}) * smoothstep(0.2, 0.8, zf);
  }
`);
const trunkSwell = wgslFn(`
  fn trunkSwell(pw: vec3<f32>, A: vec3<f32>, B: vec3<f32>, rA: f32, rB: f32, code: f32, fwd: vec3<f32>, bare: f32) -> f32 {
    let d = B - A;
    let len = max(length(d), 1e-5);
    let ax = d / len;
    var fw = fwd - ax * dot(fwd, ax);
    if (dot(fw, fw) < 1e-8) { return 0.0; }
    fw = normalize(fw);
    let c = code - 1.0;
    let c2 = c - 16384.0 * floor(c / 16384.0);
    let fem = min(floor(c / 16384.0), 1.0);
    let tB = floor(c2 / 128.0) * 0.01;
    let tA = (c2 - 128.0 * floor(c2 / 128.0)) * 0.01;
    let sA = dot(pw - A, ax) / len;
    let t = mix(tA, tB, sA);
    let rad = max(mix(rA, rB, clamp(sA, 0.0, 1.0)), 1e-3);
    let q = pw - A - ax * (sA * len);
    let zf = dot(q, fw) / max(length(q), 1e-5);
    let u = abs(dot(q, cross(ax, fw))) / rad;
    let flank = 1.0 - zf * zf;
    let rear = smoothstep(0.1, 0.7, -zf) * exp(-(u - ${sf(TRUNK.buttockU)}) * (u - ${sf(TRUNK.buttockU)}) / 0.05);
    ${["lats", "flanks", "hips", "fullHip", "buttocks", "chest", "lumbar"].map((k) => `let ${k} = ${sf(TRUNK[k][2])} * exp(-(t - ${sf(TRUNK[k][0])}) * (t - ${sf(TRUNK[k][0])}) / ${sf(TRUNK[k][1] * TRUNK[k][1])});`).join(" ")}
    let fore = smoothstep(0.1, 0.7, zf);
    let spine = smoothstep(0.1, 0.7, -zf) * smoothstep(0.6, 0.2, u);
    let mass = (1.0 - fem) * (lats + flanks) * flank + hips * flank + fem * fullHip * flank + buttocks * rear + chest * fore + lumbar * spine;
    let breasts = trunkBust(code, t, u, zf);
    return rad * (bare * (mass + ${sf(ANATOMY.relief / .17 * TRUNK.swell)} * anatomyH(u, t, zf, fem)) + breasts);
  }
`, [anatomyH, trunkBust]);
// THE LIMB's height (in reliefs) at t down it, a (radians) round it, for its `kind` (people.js LIMB): LIMBS' features
const LIMB_KINDS = ["thigh", "shin", "arm", "fore", "foot"];
const limbH = wgslFn(`
  fn limbH(kind: i32, t: f32, a: f32) -> f32 {
    var h = 0.0;
    ${LIMB_KINDS.map((k, i) => `if (kind == ${i + 1}) {
      ${LIMBS[k].map(([t0, a0, wt, wa, hh, sl = 0]) => `h = h + ${sf(hh)} * exp(-(t - ${sf(t0)}) * (t - ${sf(t0)}) / ${sf(wt * wt)} + (cos(a - ${sf(a0 * Math.PI / 180)}${sl ? ` - ${sf(sl * Math.PI / 180)} * (t - ${sf(t0)})` : ""}) - 1.0) / ${sf((wa * Math.PI / 180) ** 2)});`).join("\n      ")}
    }`).join(" else ")}
    return h;
  }
`);
// ...and how much of it the OUTLINE takes there: none at a joint the next part meets (its own swell eased off by
// LIMBS.ease of its length -- the shade is not: there a feature sits on the joint or keeps off it, LIMBS)
const limbEase = wgslFn(`
  fn limbEase(kind: i32, t: f32) -> f32 {
    var w = 1.0;
    ${LIMB_KINDS.map((k, i) => `if (kind == ${i + 1}) { ${[0, 1].filter((e) => !LIMBS.loose[k]?.[e]).map((e) => `w = w * smoothstep(${e}.0, ${sf(e ? 1 - LIMBS.ease : LIMBS.ease)}, t);`).join(" ")} }`).join(" else ")}
    return w;
  }
`);
// WHERE a point is on a limb from A (its root) to B, its kind and side in `code` (people.js LIMB), `fwd` and `up` the
// figure's: its front and its outer side there, and (t down it, a round it from the front toward the outer side, its
// kind; kind 0 where the frame fails)
const limbCoord = wgslFn(`
  fn limbCoord(pw: vec3<f32>, A: vec3<f32>, B: vec3<f32>, code: f32, fwd: vec3<f32>, up: vec3<f32>) -> mat3x3<f32> {
    let d = B - A;
    let len = max(length(d), 1e-5);
    let ax = d / len;
    let c = code - select(0.0, 16.0, code > 15.5);
    let left = c > 7.5;
    // (its outer side: the figure's side it is on, square to the limb -- or, the limb along it (an arm raised to the
    //  side), up; its front square to both, the figure's forward way)
    let sideW = cross(fwd, up) * select(-1.0, 1.0, left);
    var L = sideW - ax * dot(sideW, ax);
    if (dot(L, L) < 0.04) { L = up - ax * dot(up, ax); }
    if (dot(L, L) < 1e-8) { return mat3x3<f32>(vec3<f32>(0.0), vec3<f32>(0.0), vec3<f32>(0.0)); }
    L = normalize(L);
    var F = cross(L, ax);
    F = F * select(1.0, -1.0, dot(F, fwd + 0.5 * up) < 0.0);
    L = cross(ax, F) * select(1.0, -1.0, dot(cross(ax, F), L) < 0.0);
    let sA = dot(pw - A, ax) / len;
    let q = pw - A - ax * (sA * len);
    // (its angle by how far to the side it is, of its round's radius -- past an end, on the cap, that radius the ball's:
    //  a groove at an angle stays a line along the limb there, the toes' parted to the tip, where by the angle alone all
    //  of them would meet at the cap's pole, a fan)
    let e = select(select(pw - B, pw - A, sA < 0.0), q, sA >= 0.0 && sA <= 1.0);
    let l = clamp(dot(q, L) / max(length(e), 1e-5), -1.0, 1.0);
    let a = select(select(-1.0, 1.0, l >= 0.0) * 3.14159265 - asin(l), asin(l), dot(q, F) >= 0.0);
    return mat3x3<f32>(F, L, vec3<f32>(sA, a, c - select(0.0, 8.0, left)));
  }
`);
// ...its muscles there, rA and rB its radii at A and B, px the pixel's footprint: the normal's tilt (xyz) and the
// darkness (w), LIMBS above
const limbAt = wgslFn(`
  fn limbAt(pw: vec3<f32>, A: vec3<f32>, B: vec3<f32>, rA: f32, rB: f32, code: f32, fwd: vec3<f32>, up: vec3<f32>, px: f32) -> vec4<f32> {
    let fr = limbCoord(pw, A, B, code, fwd, up);
    let lc = fr[2];
    let kind = i32(lc.z + 0.5);
    if (kind < 1) { return vec4<f32>(0.0); }
    let d = B - A;
    let len = max(length(d), 1e-5);
    let ax = d / len;
    let t = clamp(lc.x, -0.1, 1.1);
    let a = lc.y;
    let rad = max(mix(rA, rB, clamp(lc.x, 0.0, 1.0)), 1e-3);
    let h0 = limbH(kind, t, a);
    let dha = (limbH(kind, t, a + 0.02) - h0) * 50.0;
    let dht = (limbH(kind, t + 0.01, a) - h0) * 100.0;
    let k = ${sf(LIMBS.relief / .06)} * rad * select(1.0, ${sf(LIMBS.soft)}, code > 15.5);
    let seen = mix(1.0, ${sf(LIMBS.far)}, smoothstep(0.5, 2.0, px / (0.3 * rad)));
    let tA = cos(a) * fr[1] - sin(a) * fr[0];   // (the way round it, a growing)
    let g = k * (dha * tA / rad + dht * ax / len);
    return vec4<f32>(-g * seen, clamp(-h0, 0.0, 1.0) * ${sf(LIMBS.dark)} * seen * select(1.0, ${sf(LIMBS.soft)}, code > 15.5));
  }
`, [limbH, limbCoord]);
// THE FINGERS on a flat hand from A (the wrist) to B (the tip), `fwd` the figure's forward, r its width's half, px the
// pixel's footprint: the normal's tilt (xyz) and the groove's darkness (w), FINGERS above
const fingersAt = wgslFn(`
  fn fingersAt(pw: vec3<f32>, A: vec3<f32>, B: vec3<f32>, fwd: vec3<f32>, r: f32, px: f32) -> vec4<f32> {
    let d = B - A;
    let len = length(d);
    let ax = d / max(len, 1e-5);
    let q = pw - A;
    let t = dot(q, ax) / max(len, 1e-5);
    var bw = fwd - ax * dot(fwd, ax);
    if (dot(bw, bw) < 1e-8) { return vec4<f32>(0.0); }
    bw = normalize(bw);
    let n = ${sf(FINGERS.count)};
    let k = (dot(q, bw) / max(r, 1e-4) * 0.5 + 0.5) * n;   // 0 at one edge, n at the other: a finger a unit
    let j = round(k);
    let e = k - j;
    let inner = step(0.5, j) * step(j, n - 0.5);           // (between two fingers, not the hand's own edges)
    let g = 1.0 - smoothstep(0.0, ${sf(FINGERS.width * .5)}, abs(e));
    let seen = smoothstep(1.0, 2.5, ${sf(FINGERS.width)} * 2.0 * r / n / px);
    let a = g * inner * seen * smoothstep(${sf(FINGERS.from)}, ${sf(FINGERS.from + .12)}, t);
    return vec4<f32>(-bw * sign(e) * ${sf(FINGERS.tilt)} * a, ${sf(FINGERS.dark)} * a * g);
  }
`);
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
    let fleecy = (floor(flags / 512.0) - 2.0 * floor(flags / 1024.0)) > 0.5;
    let code = floor(max(S1.w, 0.0) + 0.5);
    let ua = unpackAw(A.w);
    let r = max(max(abs(ua.x), B.w), girth);
    var c = col;
    var nn = normalize(n);
    // a flat HAND (its radius negative, C.y its palm flag: shell.js above): its fingers' grooves, the normal's tilt and the darkness
    var fing = vec4<f32>(0.0);
    if (ua.x < 0.0 && C.y > 0.5) {
      let bi = i32(base + 0.5);
      let F0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3).xyz, 1.0)).xyz" : "texel(tex, bi * 3).xyz"};
      let F1 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3 + 1).xyz, 1.0)).xyz" : "texel(tex, bi * 3 + 1).xyz"};
      fing = fingersAt(pw, A.xyz, B.xyz, F1 - F0, r, max(max(length(dpdx(pw)), length(dpdy(pw))), 1e-5));
      nn = normalize(nn + fing.xyz);
    }
    // STONE (a statue: 2048 x its material -- 1 marble, 2 bronze, 3 gold, 4 limestone): the cloth keeps its shape, its
    // holes and its folds, the colour is the stone's
    let stoneM = floor(flags / 2048.0) - 8.0 * floor(flags / 16384.0);
    let eye = invView[3].xyz;
    // (carved, the figure's own shade on it: its parts from its first slot, as many as the flags' top bits say)
    var own = vec2<f32>(1.0);
    if (stoneM > 0.5${SELF_OFF ? " && false" : ""}) { own = selfShade(tex, sTex, invView, pw, nn, i, i32(base + 0.5), i32(floor(flags / 16384.0))); }
    // (carved, a bare TORSO -- a flat piece with its place on the trunk in C.z, people.js anat -- has its anatomy cut in,
    //  ANATOMY: wherever its skin shows)
    var anat = vec4<f32>(0.0);
    if (stoneM > 0.5 && ua.x < 0.0 && C.y < 0.5 && C.z > 0.5) {
      let bi = i32(base + 0.5);
      let T0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3).xyz, 1.0)).xyz" : "texel(tex, bi * 3).xyz"};
      let T1 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3 + 1).xyz, 1.0)).xyz" : "texel(tex, bi * 3 + 1).xyz"};
      anat = anatomyAt(pw, A.xyz, B.xyz, abs(ua.x), B.w, C.z, T1 - T0, max(max(length(dpdx(pw)), length(dpdy(pw))), 1e-5));
    }
    // (...and a bare LIMB -- round, uncut, its kind in C.x, people.js LIMB -- its muscles, LIMBS)
    if (stoneM > 0.5 && ua.x > 0.0 && ua.z < 0.5 && C.x > 0.5 && C.x < 31.5) {
      let bi = i32(base + 0.5);
      let T0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3).xyz, 1.0)).xyz" : "texel(tex, bi * 3).xyz"};
      let T1 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, bi * 3 + 1).xyz, 1.0)).xyz" : "texel(tex, bi * 3 + 1).xyz"};
      var upL = vec3<f32>(0.0, 1.0, 0.0);
      let urL = i32(S2.w + 0.5);
      if (urL > 0) {
        let U0 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, (urL - 1) * 3).xyz, 1.0)).xyz" : "texel(tex, (urL - 1) * 3).xyz"};
        let U1 = ${viewSpace ? "(invView * vec4<f32>(texel(tex, (urL - 1) * 3 + 1).xyz, 1.0)).xyz" : "texel(tex, (urL - 1) * 3 + 1).xyz"};
        let du = U0 - U1;   // (the chest runs down from its A end)
        upL = select(upL, normalize(du), dot(du, du) > 1e-10);
      }
      var fwL = T1 - T0;
      fwL = fwL - upL * dot(fwL, upL);
      if (dot(fwL, fwL) > 1e-10) { anat = limbAt(pw, A.xyz, B.xyz, ua.x, B.w, C.x, normalize(fwL), upL, max(max(length(dpdx(pw)), length(dpdy(pw))), 1e-5)); }
    }
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
      // (the cloth's own frame, clothFrame: from the part's rest axis, if it keeps one)
      let cF = clothFrame(fw, upW, S1, ax);
      let th = atan2(dot(rq, cF[1]), dot(rq, cF[0]));
      // (its change across the pixel without the jump where the angle wraps: whichever of the two ways of counting it
      //  -- the jump at the back, or at the front -- changes less here)
      let th2 = th + select(0.0, 6.2831853, th < 0.0);
      var dth = vec2<f32>(dpdx(th), dpdy(th));
      let dth2 = vec2<f32>(dpdx(th2), dpdy(th2));
      if (dot(dth2, dth2) < dot(dth, dth)) { dth = dth2; }
      let ds = vec2<f32>(dpdx(sL), dpdy(sL));
      let px = max(max(length(dpdx(pw)), length(dpdy(pw))), 1e-5);
      var rel = vec4<f32>(0.0);
      // (on an end's cap -- past either end along the axis, or facing along it -- no folds: they would meet in a star)
      let capS = max(-sL, sL - length(dP)) / max(r, 1e-3);
      let got = dressAt(sTex, fab, fsamp, S2, sL, th, dth, ds, max(girth, 0.004), px, kind, col, ax, rq, max(abs(dot(nn, ax)), smoothstep(0.0, 0.8, capS)), &rel);
      // a standing piece is cloth only where a layer is: its openings are holes (carved, its END is full -- a hem's
      // lid, seen lying or from below -- but an opening in its side, a mantle's wrap, is not, nor its end across it)
      if (got.w < 0.5 && S2.z > 0.5 && (stoneM < 0.5 || capS < -0.01 || dressOpen(sTex, S2, th))) { discard; }
      c = got.xyz;
      // (carved, an opening's INSIDE -- a sleeve's mouth, a hem seen from below: a standing piece's lining, its inner
      //  wall -- is a hollow the chisel cut, in shade; its near cap, the waistband closed over the gap to the body, is not:
      //  it is cloth's top, lit, where the hem's cap is its underside)
      //  ...deepening from its lip: lit at the edge it is seen over, in shade as far in as STONE.hollowIn -- along the wrap
      //  from its edge, up from an open end -- where one flat shade all over was a hole cut through the cloth)
      let hollow = stoneM > 0.5 && S2.z > 0.5 && kind > 0.5 && (kind < 1.5 || sL > 0.5 * length(dP));
      let lipD = min(dressEdge(sTex, S2, th) * max(girth, 0.004), select(1.0e3, C.y - sL, C.z > 0.5 && C.z < 1.5));
      let hollowK = ${sf(STONE.hollow)} * smoothstep(0.0, ${sf(STONE.hollowIn)}, lipD);
      if (got.w < 0.5 && furry) { c = furAt(c, loc, px); }   // (a beast's hide where nothing is worn: its coat)
      if (dot(rel.xyz, rel.xyz) > 1e-12) { nn = normalize(nn - rel.xyz); }
      if (stoneM > 0.5) {   // (carved: the lines the cloth's pattern draws -- where its colour changes, across the pixel -- cut in)
        if (got.w < 0.5) { nn = normalize(nn + anat.xyz); }   // (its skin, where no layer is: the anatomy)
        let lc = got.w - 1.0;
        let seen = smoothstep(1.0, 2.5, ${sf(STONE.inciseLine)} / px);   // (the line's width in pixels)
        let cut = (1.0 - ${sf(STONE.incise)} * seen * smoothstep(${sf(STONE.inciseMin)}, ${sf(STONE.inciseMin + 1 / STONE.inciseK)}, fwidth(lc) / (lc + 0.05)))
                  * (1.0 - ${sf(STONE.fold)} * rel.w) * (1.0 - fing.w) * select(1.0, 1.0 - hollowK, hollow) * select(1.0, 1.0 - anat.w, got.w < 0.5);   // (a fold's valley in shadow, as a chisel's is)
        return stoneAt(stoneM, pw, nn, eye, cut, own, vec4<f32>(c, select(0.0, 1.0, got.w < 0.5)));   // (painted: the cloth's colour, the skin's where none is worn)
      }
      return c * (1.0 - ${sf(FINGERS.paint)} * fing.w) * shadeOf(nn);
    }
    if (stoneM > 0.5) { return stoneAt(stoneM, pw, normalize(nn + anat.xyz), eye, (1.0 - fing.w) * (1.0 - anat.w), own, vec4<f32>(c, select(1.0, 2.0, pat > 14.5 && pat < 16.5))); }   // (painted: skin, or hair -- strands, skeleton.js PAT)
    c = c * (1.0 - ${sf(FINGERS.paint)} * fing.w);
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
      if (fleecy) {   // (FLEECE's small lumps, in the light: dark crevices between the locks -- finer than the vertices can heap)
        let lq = pl0 * ${(6.2832 / FLEECE.lock).toFixed(3)};
        let b = sin(lq.x + 0.9 * sin(lq.z * 0.6)) * sin(lq.y + 0.9 * sin(lq.x * 0.7)) * sin(lq.z + 0.9 * sin(lq.y * 0.8));
        let fade = 1.0 - smoothstep(${FLEECE.lock / 6}, ${FLEECE.lock / 2.5}, patPx);
        c = c * (1.0 - ${FLEECE.crease} * fade * (1.0 - smoothstep(-0.6, 0.4, b)));
      }
    }
    return c * shadeOf(nn);
  }
`, [texelFor(W), unpackAw, LIB.partLocal, LIB.patternAt, strandsAt, furAt, LIB.shadeOf, dressFns(W, ST).dressAt, dressFns(W, ST).dressOpen, dressFns(W, ST).dressEdge, clothFrame, stoneAt, fingersAt, anatomyAt, limbAt, selfShade(W, ST, viewSpace)]);

// ---- one shell set for one composite herd -----------------------------------------------------------------
//   nDyn/nStat  the herd's texture nodes (the same ones its own material reads)
//   cap         how many parts the herd has room for (a chain is at most one instance per part)
//   touch       composite.js's partial upload: only the instances a frame listed go up
//   ends        the herd's posed world endpoints for a part: what the chains are worked out from
const SLOTS = ["part", "ch", "ch2", "nb"];
const SHELL_ROOM = 4096;   // chains a bucket has room for from the start (grow(): growing later is broken)
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
      mat.colorNode = on ? vec3(0.15, 0.5, 1.0) : shaded.mul(sunShade(viewSpace ? cameraWorldMatrix.mul(vec4(vP.xyz, 1.0)).xyz : vP.xyz, normalize(vN.xyz)));   // (in a building's shadow too: sunshadow.js)
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
  // (and CARVED CLOTH's own, near by: the nearest grid with STONE.divs times its points round -- its folds cut in)
  const lods = [...SHELL.lod.map(([far, rings, divs]) => [far, rings, divs, false]), [SHELL.lod[0][0], SHELL.lod[0][1], SHELL.lod[0][2] * STONE.divs, true]];
  for (const [far, rings, divs, carved] of lods) for (let c = 0; c < LENGTHS.length; c++) {
    const b = { far, cls: c, rings: Math.max(4, Math.round(rings * LENGTHS[c])), divs, carved, n: 0, want: 0 };
    b.geo = shellGrid(b.rings, divs);
    setArrays(b, SHELL_ROOM);                  // (room for a whole town's crowd from the start: see grow())
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
        // (a CARVED chain -- a statue's -- a class finer: its muscles swell it and its joints want rings to bend
        //  smooth, where a person's limb is a plain tube a few rings draw; statues are few)
        const cls = Math.min(LENGTHS.length - 1, classOf(curve[ci], c.length) + (parts[c[0]]?.stone ? 1 : 0));
        // the bucket is picked by distance in CHAIN LENGTHS, so a muzzle or an ear falls to the coarse grid
        // while a body a hundred times its size keeps the fine one at the same distance
        const far = dist / Math.max(size[ci], .04);
        const carved = !!parts[c[0]]?.stone && !!parts[c[0]].clip && c.length === 1 && far <= SHELL.lod[0][0];
        let b = buckets[buckets.length - 2 * LENGTHS.length + cls];
        for (const q of buckets) if (far <= q.far && q.cls === cls && q.carved === carved) { b = q; break; }
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
        // a face mark: its own girth, not the packed reach; a cut shell DRAPED over the legs: its cling and ease (CLING),
        // and the legs' slots where a one-part chain has no more of its own (ch2), the arms' it hangs over after its own (ch)
        const cl = c.length === 1 ? parts[c[0]].cling : null;
        // (and LAID ON from its top -- 2^20 -- where it drapes over the part it hangs from: a mantle over the chest)
        const laid = cl && cl.over.includes(parts[c[0]].parentIdx);
        // (and its arms' FOREARMS in the slots after theirs -- 2^21: skeleton.js found them there)
        put(b.part, w + 3, isMark(parts[c[0]]) ? 1 : cl ? 2 + Math.round(cl.k * 100) + 256 * Math.round(cl.ease * 1e4) + (laid ? 1048576 : 0) + (cl.fore ? 2097152 : 0) : 0);
        for (let j = 0; j < 4; j++) put(b.ch, w + j, j < c.length ? an.base + c[j] : cl && j > 0 && (cl.over[3 + j] ?? -1) >= 0 ? an.base + cl.over[3 + j] : -1);
        for (let j = 4; j < 8; j++) put(b.ch2, w + j - 4, cl ? (cl.over[j - 4] ?? -1) < 0 ? -1 : an.base + cl.over[j - 4] : j < c.length ? an.base + c[j] : -1);
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
    // A BUCKET GROWN AFTER IT HAS BEEN DRAWN STILL DRAWS ONLY ITS OLD ROOM (found 2026-10-24, not solved): a
    // hedgehog of 137 chains in a near bucket grown 64 -> 256 showed its first 64 -- the stats say all 137 were
    // listed. Disposing the geometry, giving the bucket a new grid as setDetail does, or setting the shared material's
    // needsUpdate, or a brand-new Mesh for the bucket (a fresh render object) changed nothing -- so it is not three's
    // binding or caching. Nor the fill: after the growth the CPU arrays hold every chain and three uploads them (the
    // versions move, the ranges clear), and full uploads every frame (DynamicDrawUsage) changed nothing either; a bucket
    // BORN with the room draws them all, and so does one grown before its first draw (the far ones, at startup). So
    // every bucket starts with SHELL_ROOM (a far bucket held 3224 chains in a
    // whole town; 4 x 16 bytes a chain, nine buckets: ~2.4 MB, and a frame draws and uploads only what it lists).
    // Past it the bucket still grows, as before -- and would show the bug
    grow() {
      for (const b of buckets) if (b.want > b.room) {
        if (b.room >= SHELL_ROOM) console.warn(`shell: a bucket (${b.rings}x${b.divs}) grew past ${b.room} chains after drawing -- the known bucket bug (docs/engines.md): parts past the old room may go undrawn; raise SHELL_ROOM`);
        setArrays(b, b.want); b.want = 0;
      }
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
        const rings = Math.max(4, Math.round(base[1] * m * LENGTHS[b.cls])), divs = Math.max(3, Math.round(base[2] * m * (b.carved ? STONE.divs : 1)));
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
      chains: b.n, room: b.room, want: b.want, tris: b.n * b.rings * b.divs * 2 })),
  };
}
