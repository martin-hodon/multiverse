// THE HEAD, IN SECTION. A vocal tract's shape is decided by a few things a speaker can actually move -- the jaw, the
// body of the tongue, its tip, the lips, the velum, the larynx -- inside walls that do not move: the back of the throat,
// the palate, the teeth. This file is that drawing (mid-sagittal, centimetres, x toward the lips, y up) and the way
// from it to what the acoustics need: how wide the airway is at each place along it.
//
//   the fixed wall      a polyline: up the back of the pharynx, over the velum and the palate, down to the teeth
//   the tongue          a circle (the body: it really is nearly one) carried by the jaw; a straight root from the hyoid
//                       up to it and a straight blade from it out to the tip -- both tangent to it, so the surface is smooth
//   the jaw             turns about its joint: lower teeth, tongue and tip all ride on it
//   the lips            a short tube in front of the teeth: how open (its height) and how far pushed out (its length)
//
// WIDTH TO AREA. The drawing gives the front-to-back distance d across the airway along a set of fixed measuring
// lines (level across the throat, fanned round the bend, upright under the palate -- Maeda's grid). The area is
// alpha * d^beta (Heinz & Stevens): a throat is round-ish, a mouth is a wide slot, so the constants differ by region.
// No imports, no DOM.

export const ANATOMY = {
  // the fixed outer wall, glottis upward and round to the upper teeth
  wall: [[0, 0], [0, 4.3], [0.2, 5.5], [0.85, 6.5], [2.0, 7.15], [3.5, 7.45], [4.9, 7.3], [6.0, 6.8], [6.8, 6.1], [7.3, 5.45], [7.5, 4.75]],
  velumAt: [1.2, 6.75],                         // where the nose joins (drawn; the tube takes the nearest section)
  larynxTube: { length: 2.3, area: 0.9 },      // the narrow tube over the folds, below the pharynx proper
  jawPivot: [0.4, 8.2],
  // tipRest: the tip relative to the body's centre (jaw frame). jawShare: how much of the jaw's turn the tongue body follows
  // (it hangs from the jaw, but its own muscles hold it up against the turn: all of it and an open jaw shuts the throat)
  tongue: { centre: [3.3, 4.05], radius: 2.05, tipRest: [3.1, 0.35], tipReach: [0.45, 3.4], jawShare: 0.45 },
  hyoid: [1.75, 0.9],
  lowerTeeth: [7.25, 4.2],                    // lower incisor tip with the jaw shut (angle 0)
  // mouth width cm; tube length = thickness + protrusion; width shrinks by roundK per cm pushed out.
  // jawShare: THE LOWER LIP IS ON THE CHIN. This much of the jaw's own opening (measured at the teeth) is added to the lip opening:
  // drop the jaw and the mouth opens with it, clamp the jaw for an /s/ and the lips close with it, unless the lips' own muscle says
  // otherwise -- which is what `lipH` is, the opening BEYOND what the jaw gives (below 0: the lips closing over an open jaw).
  lips: { width: 4.4, thickness: 0.7, roundK: 0.62, jawShare: 0.7 },
  teethLeak: 0.9,                              // cm2 that passes between and beside the teeth however shut the jaw is
  grid: { centre: [3.3, 4.2], throatStep: 0.55, fanFrom: 180, fanTo: 38, fanStep: 11, frontStep: 0.5 },
  areaLaw: { throat: [1.9, 1.35], bend: [1.8, 1.4], palate: [2.1, 1.3], front: [2.4, 1.25] },   // [alpha, beta] per region
  contact: 0.05,                               // cm: flesh gives -- a gap this small is shut
  midline: 0.83,                               // the airway's midline is this much shorter than the wall it runs under (it cuts the corner of the bend)
  tipLength: 0.8,                              // cm of the blade that makes the tip's constriction: it has a LENGTH along the tract (as a point it slid from one
                                               // section of the tube into the next and the one it left flew open -- the last of the clicks on t)
  // THE ROOM UNDER THE TONGUE. Raise the tip and the blade lifts off the floor of the mouth: the space under it opens into the tract
  // just behind the tip and is a closed room off it. That room lengthens the front cavity and pulls F3 DOWN, which is what makes a
  // retroflex r an r -- without it, curling the tip only narrows the front and F3 goes up (measured: 1708 -> 2048 Hz). It opens once
  // the tip is `from` cm above its rest (no vowel posture reaches that), and grows `perCm` cm3 for every cm above it, up to `max`;
  // `area` is how wide its mouth is, so its length is the volume over that.
  // opensAt: and only while the air can get PAST the tip. The same contact that makes a /d/ seals the room off from the tract: left
  // open there it was a second cavity hanging off a closure holding the lungs' pressure, and at the release it emptied into the mouth
  // -- a bang instead of a burst, 70% of the loudest vowel where a man's was 17% (whether it bit depended on how the closure fell
  // across the tube's sections, which is why one voice clicked and another did not).
  sublingual: { from: 1.2, perCm: 1.9, max: 3.4, area: 1.1, opensAt: [.06, .22] },
  tipPeel: 0.55,                               // cm: the blade PEELS off the ridge -- until the tip is this far away the opening is only part of the mouth's width
                                               // (area x gap/tipPeel), so a release opens over 15-30ms, not 5: opened at once it is a gust of air, a thump
  // the named places a consonant is made at: points on the fixed wall (the consonant table refers to them by name)
  places: { pharyngeal: [0, 3.0], uvular: [0.85, 6.5], velar: [2.0, 7.15], palatal: [4.2, 7.4], prepalatal: [5.5, 7.05], postalveolar: [6.4, 6.45], alveolar: [7.05, 5.8], dental: [7.42, 5.05] },
  // THE WAY ROUND A LATERAL. The tongue's sides drop and the air goes PAST the closure and back to the midline in front of it, so an
  // /l/ is not a leak through the closure but a road around it: `lateralLeak` cm2 of channel (both sides together, x `lateral`), which
  // leaves the midline behind the closure a dead end `lateralSpan` cm long -- and a dead end is a ZERO in what comes out, which is what
  // a dark l has and a leak has not. `lateralLonger`: the channels go round the tongue, so they are that much longer than the midline.
  lateralLeak: 0.34, lateralSpan: 3.0, lateralPocket: 0.5,
  scale: { oral: 1, pharynx: 1 },              // a woman ~ .91 / .82, a child of seven ~ .78 / .66 (the throat grows last)
};
// what a speaker moves. Each: [min, max, neutral]
export const ARTICULATORS = {
  jaw: [0, 24, 7],            // degrees open
  bodyX: [-1.6, 1.4, 0],      // tongue body, cm forward of rest (in the jaw's frame)
  bodyY: [-1.6, 1.7, 0],      // ...and up
  tipX: [-2.4, 1.6, 0],       // tongue tip, cm forward of where the body would leave it (far back = the blade, under the palate: sh after a front vowel)
  tipY: [-1.0, 3.0, 0],       // ...and up
  lipH: [-1.6, 2.2, 1.0],     // lip opening, cm, BEYOND what the jaw gives (anatomy.lips.jawShare); below 0 the lips close over an open jaw
  lipP: [0, 1.4, 0.2],        // lip protrusion, cm
  velum: [0, 1, 0],           // velar port, 0 shut .. 1 wide open (x 1.6 cm2)
  larynx: [-1, 1, 0],         // larynx height, cm (up shortens the throat)
  lateral: [0, 1, 0],         // the tongue's sides lowered: air passes beside a closed tip
  lipSpread: [-0.5, 1, 0],    // the lips' corners drawn back (a smile): a wider, SHORTER lip opening -- every formant a little higher. Below 0: drawn in
};
// A POSTURE LEARNED IN THE REFERENCE HEAD, TAKEN INTO A RESHAPED ONE (anat.shape, set by synth.js reshape). A tongue aims at a GAP, not at
// a place in space: under a higher palate a high vowel's body rides higher by as much as the palate rose above it, before a throat wall
// that stands further back a back vowel's body goes further back -- each by how much that vowel uses that wall at all. Without this a palate
// 15% lower shut every /i/ and a throat 20% narrower every /u/. What is left over is small, and is that head's own colour; an exact fit
// is the lab's "Re-fit for this voice".
export function adaptPosture(art, anat = ANATOMY) {
  const sh = anat.shape; if (!sh) return art;
  const out = { ...art }, high = Math.max(0, Math.min(1, ((art.bodyY ?? 0) + .3) / 1.3)), back = Math.max(0, Math.min(1, (-(art.bodyX ?? 0) + .1) / .9));
  // (a palate that ROSE rose less toward the teeth, where the blade is: the body follows it only part of the way up, and the tip not at all)
  const rise = sh.palateRise > 0 ? sh.palateRise * .65 : sh.palateRise;
  out.bodyY = (art.bodyY ?? 0) + rise * high * high * (3 - 2 * high); if (rise < 0) out.tipY = (art.tipY ?? 0) + rise * .5 * Math.max(0, Math.min(1, art.tipY ?? 0));
  out.bodyX = (art.bodyX ?? 0) - sh.throatBack * back * back * (3 - 2 * back) * (1 - high);
  return out;
}
export const neutral = () => Object.fromEntries(Object.entries(ARTICULATORS).map(([k, v]) => [k, v[2]]));
export const clampArt = (a) => { for (const k of Object.keys(ARTICULATORS)) a[k] = Math.min(ARTICULATORS[k][1], Math.max(ARTICULATORS[k][0], a[k] ?? ARTICULATORS[k][2])); return a; };

const sub = (a, b) => [a[0] - b[0], a[1] - b[1]], add = (a, b) => [a[0] + b[0], a[1] + b[1]], mul = (a, k) => [a[0] * k, a[1] * k];
const len = (a) => Math.hypot(a[0], a[1]), dot = (a, b) => a[0] * b[0] + a[1] * b[1];
const rot = (p, c, deg) => { const t = deg * Math.PI / 180, s = Math.sin(t), co = Math.cos(t), d = sub(p, c); return [c[0] + d[0] * co - d[1] * s, c[1] + d[0] * s + d[1] * co]; };
// the tangent point on circle (C, r) seen from outside point P; side = +1 the one to the left of P->C, -1 to the right
function tangent(P, C, r, side) {
  const d = sub(C, P), L = len(d); if (L <= r + 1e-6) return add(C, mul(sub(P, C), r / Math.max(L, 1e-6)));
  const a = Math.asin(r / L), base = Math.atan2(d[1], d[0]), t = base + side * a, reach = Math.sqrt(L * L - r * r);
  return [P[0] + Math.cos(t) * reach, P[1] + Math.sin(t) * reach];
}
// where ray O + s*u (u unit, s >= 0) first meets segment AB; Infinity if it does not
function hitSeg(O, u, A, B) {
  const v = sub(B, A), den = u[0] * v[1] - u[1] * v[0]; if (Math.abs(den) < 1e-12) return Infinity;
  const w = sub(A, O), s = (w[0] * v[1] - w[1] * v[0]) / den, t = (w[0] * u[1] - w[1] * u[0]) / den;
  return s >= 0 && t >= -1e-9 && t <= 1 + 1e-9 ? s : Infinity;
}
function hitCircle(O, u, C, r) {
  const w = sub(O, C), b = dot(w, u), c = dot(w, w) - r * r; if (c <= 0) return 0;      // the wall point is INSIDE the tongue: shut
  const disc = b * b - c; if (disc < 0) return Infinity; const s = -b - Math.sqrt(disc); return s >= 0 ? s : Infinity;
}
function hitPoly(O, u, pts) { let best = Infinity; for (let i = 0; i + 1 < pts.length; i++) best = Math.min(best, hitSeg(O, u, pts[i], pts[i + 1])); return best; }

// how far along the wall (from its first point) the wall point nearest to P lies
function alongWall(P, wall) {
  let best = 1e9, at = 0, run = 0;
  for (let i = 0; i + 1 < wall.length; i++) { const a = wall[i], b = wall[i + 1], ab = sub(b, a), L = len(ab), u = Math.max(0, Math.min(1, dot(sub(P, a), ab) / (L * L))), d = len(sub(P, add(a, mul(ab, u)))); if (d < best) { best = d; at = run + u * L; } run += L; }
  return at;
}
// the drawing for one setting of the articulators: outlines, measuring lines, widths and areas
// HOW FAR THE LOWER LIP HAS COME DOWN WITH THE JAW (cm, about the jaw's rest angle): the chin turns about its joint and the lower
// teeth -- and the lip on them -- come down with it. Both the drawing and the lip solver go through this, so they cannot disagree.
export const lipRide = (art, anat = ANATOMY) => rot(anat.lowerTeeth, anat.jawPivot, -ARTICULATORS.jaw[2])[1] - rot(anat.lowerTeeth, anat.jawPivot, -(art.jaw ?? ARTICULATORS.jaw[2]))[1];

export function sagittal(art, anat = ANATOMY) {
  // ANOTHER HEAD IS THE SAME HEAD, STRETCHED (scale.oral along the mouth, scale.pharynx up the throat): everything is worked out in
  // the reference head and then stretched -- walls, tongue and the gaps between them alike. (The tongue used to be a CIRCLE of the
  // mean scale in a vault scaled by the smaller one: in a child's head it stood 1mm nearer the palate, every high vowel was
  // nearly a closure, and "is" between an m and a z was "in".)
  const kx = anat.scale.oral, ky = anat.scale.pharynx, Z = (p) => [p[0] * kx, p[1] * ky], stretch = (u) => Math.hypot(u[0] * kx, u[1] * ky);
  const sx = 1, sy = 1, S = (p) => p;
  const jaw = (p) => rot(p, anat.jawPivot, -art.jaw);                                     // opening turns the chin down and back
  const T = anat.tongue, r = T.radius;
  const jawT = (p) => rot(p, anat.jawPivot, -art.jaw * T.jawShare);
  const C = S(jawT(add(T.centre, [art.bodyX, art.bodyY])));
  let tipRel = add(T.tipRest, [art.tipX, art.tipY]); { const L = len(tipRel), lo = T.radius + T.tipReach[0], hi = T.radius + T.tipReach[1]; tipRel = mul(tipRel, Math.min(hi, Math.max(lo, L)) / L); }
  let tip = S(jawT(add(add(T.centre, [art.bodyX, art.bodyY]), tipRel)));
  { const O0 = S(anat.grid.centre), v = sub(tip, O0), L = len(v), u = mul(v, 1 / Math.max(L, 1e-9)), sw = hitPoly(O0, u, anat.wall.map(S)); if (sw < L + .01) tip = add(O0, mul(u, Math.max(0, sw - .01))); }   // the tip cannot go through the palate: it stops against it
  const hy = S(add(anat.hyoid, [0, art.larynx * .6])), teeth = S(jaw(anat.lowerTeeth));
  const wall = anat.wall.map(S), tRoot = tangent(hy, C, r, -1), tBlade = tangent(tip, C, r, +1);
  // the tongue's surface as the measuring rays see it: root line, the body's circle, blade line, then the floor out to the teeth
  const floor = [tip, [tip[0] + .15 * sx, tip[1] - .55 * sy], [teeth[0] - .25 * sx, teeth[1] - .5 * sy], teeth];
  const inner = (O, u) => Math.min(hitSeg(O, u, hy, tRoot), hitCircle(O, u, C, r), hitSeg(O, u, tBlade, tip), hitPoly(O, u, floor), hitSeg(O, u, [hy[0], 0], hy));
  // the measuring lines, each from a point OUTSIDE the wall inward; its wall point is where it crosses the wall
  const G = anat.grid, O = S(G.centre), lines = [];
  for (let y = G.throatStep * .5; y < G.centre[1] - .2; y += G.throatStep) lines.push({ region: "throat", from: [-1, y * sy], dir: [1, 0] });
  for (let a = G.fanFrom; a >= G.fanTo; a -= G.fanStep) { const t = a * Math.PI / 180, out = [Math.cos(t), Math.sin(t)]; lines.push({ region: a > 100 ? "bend" : "palate", from: add(O, mul(out, 9)), dir: mul(out, -1) }); }
  const xFront = O[0] + Math.cos(G.fanTo * Math.PI / 180) * 3.2 * sx;
  for (let x = xFront + G.frontStep * .7 * sx; x < wall[wall.length - 1][0] - .05; x += G.frontStep * sx) lines.push({ region: "front", from: [x, 14], dir: [0, -1] });
  const cuts = [], wallZ = wall.map(Z);
  for (const ln of lines) {
    const sw = hitPoly(ln.from, ln.dir, wall); if (!isFinite(sw)) continue;
    const W = add(ln.from, mul(ln.dir, sw)), si = inner(W, ln.dir);
    const d = isFinite(si) ? Math.max(0, si) : Math.max(0, W[1] - Math.min(teeth[1], tip[1]));   // (past the tongue's tip: down to the floor of the mouth)
    const [al, be] = anat.areaLaw[ln.region], k = stretch(ln.dir);
    let A = al * Math.pow(Math.max(0, d - anat.contact), be) * k * (kx + ky) / 2;      // (the reference head's area, x the stretch along the gap x the stretch across the head)
    cuts.push({ region: ln.region, wall: Z(W), tongue: Z(add(W, mul(ln.dir, d))), mid: Z(add(W, mul(ln.dir, d / 2))), d: d * k, A, s: alongWall(Z(W), wallZ) });
  }
  // THE TIP ITSELF: it touches the palate BETWEEN two measuring lines as often as on one, and a closure nobody measures
  // is not a closure. So the gap at the tip -- its distance to the nearest point of the wall -- is a cut of its own.
  {
    let best = 1e9, foot = null;
    for (let i = 0; i + 1 < wall.length; i++) { const a = wall[i], b = wall[i + 1], ab = sub(b, a), u = Math.max(0, Math.min(1, dot(sub(tip, a), ab) / dot(ab, ab))), q = add(a, mul(ab, u)), d = len(sub(tip, q)); if (d < best) { best = d; foot = q; } }
    const k = best > 1e-6 ? stretch(mul(sub(tip, foot), 1 / best)) : ky;
    const [al, be] = anat.areaLaw.front, gTip = Math.max(0, best - anat.contact), A = al * Math.pow(gTip, be) * k * Math.min(1, gTip / anat.tipPeel) * (kx + ky) / 2;
    const sTip = alongWall(Z(foot), wallZ); let at = cuts.length; for (let i = 0; i < cuts.length; i++) if (cuts[i].s > sTip) { at = i; break; }
    if (foot[0] > O[0]) cuts.splice(at, 0, { region: "front", wall: Z(foot), tongue: Z(tip), mid: Z(mul(add(foot, tip), .5)), d: best * k, A, tipCut: true, s: sTip });
  }
  // a lowered tongue side lets air past a closed tip (a lateral): the front cuts never quite shut. The channels' LENGTH is the midline's,
  // near enough -- what they add is a dead end (below), which is what a lateral really sounds of.
  if (art.lateral > 0) for (const c of cuts) if (c.region === "front" || c.region === "palate") c.A = Math.max(c.A, art.lateral * anat.lateralLeak);
  // between the teeth: the gap between the upper incisors' tip and whichever is higher, lower teeth or tongue tip
  const upper = Z(wall[wall.length - 1]), gap = Math.max(0, upper[1] - teeth[1] * ky);
  const spread = art.lipSpread ?? 0, lipLen = (anat.lips.thickness * (1 - .5 * Math.max(0, spread)) + art.lipP) * kx, lipW = Math.max(.6, anat.lips.width * (1 + .3 * spread) * kx - anat.lips.roundK * art.lipP * anat.lips.width * kx / 1.4);
  const lipOpen = Math.max(0, art.lipH + anat.lips.jawShare * lipRide(art, anat));      // the lips' own opening plus the jaw's own
  const lipArea = Math.PI / 4 * lipW * lipOpen * ky;
  let wallLength = 0; for (let i = 0; i + 1 < wallZ.length; i++) wallLength += len(sub(wallZ[i + 1], wallZ[i]));
  // (r: the tongue body's mean radius, for whoever wants one number; it is an ellipse rx x ry, and angles on it are the reference head's)
  return { wall: wallZ, wallLength, C: Z(C), r: r * Math.sqrt(kx * ky), rx: r * kx, ry: r * ky, tip: Z(tip), hy: Z(hy), teeth: Z(teeth), tRoot: Z(tRoot), tBlade: Z(tBlade), floor: floor.map(Z), cuts, upper, gap,
    lip: { length: lipLen, width: lipW, height: lipOpen * ky, area: lipArea, x: upper[0] + .15 }, centre: Z(O) };
}

// the area function: positions along the airway's midline (cm from the glottis) and the area at each
export function areaFunction(art, anat = ANATOMY) {
  const sg = sagittal(art, anat), xs = [], As = [];
  const LT = anat.larynxTube, l0 = Math.max(.8, (LT.length - art.larynx * .5) * anat.scale.pharynx);
  xs.push(0, l0); As.push(LT.area * anat.scale.pharynx, LT.area * anat.scale.pharynx);
  // WHERE a cut lies along the tract is read off the FIXED WALL it was measured from (its distance along the palate, less
  // the corner the midline cuts), not off the tongue: measured along the line through the cuts' midpoints, every movement
  // of the tongue tip re-routed that line -- the tract's length jumped by a centimetre between two frames and a closure
  // hopped three sections of the tube, which opened one that was holding the lungs' pressure. Every t and d clicked.
  let at = l0, tipAt = null;
  for (const c of sg.cuts) { at = l0 + .3 + c.s * anat.midline;
    if (c.tipCut) { const h = anat.tipLength / 2, lo = Math.max(xs[xs.length - 1] + .02, at - h); xs.push(lo, at + h); As.push(c.A, c.A); at += h; tipAt = lo; }   // the blade's stretch of it
    else if (at > xs[xs.length - 1] + .02) { xs.push(at); As.push(c.A); }
    else As[As.length - 1] = Math.min(As[As.length - 1], c.A); }
  at = l0 + .3 + sg.wallLength * anat.midline;
  // (EVERY knot from here on is kept in front of the last one. The cuts are measured along the wall and the blade's own cut has a
  //  LENGTH: in a small head the blade could reach past where the teeth knot goes, the array then ran backwards, and areaAt() --
  //  which divides by the gap between two knots -- extrapolated wildly. One frame of a 21 cm2 section behind a /d/'s closure, and
  //  the release was a bang: the woman's "old dog" clicked and the man's did not.)
  const ahead = (x) => Math.max(x, xs[xs.length - 1] + .02);
  // the teeth: a slot as wide as the mouth's front, as high as the gap
  const [al, be] = anat.areaLaw.front; at = ahead(at + .45 * anat.scale.oral); xs.push(at); As.push(Math.min(al * Math.pow(sg.gap, be) + anat.teethLeak, 6));
  const teethX = at; at = ahead(at + .25 * anat.scale.oral); const lipStart = at; xs.push(at); As.push(sg.lip.area); at = ahead(at + sg.lip.length); xs.push(at); As.push(sg.lip.area);
  let vi = 0, vb = 1e9; sg.cuts.forEach((c, i) => { const d = Math.hypot(c.wall[0] - anat.velumAt[0] * anat.scale.oral, c.wall[1] - anat.velumAt[1] * anat.scale.pharynx); if (d < vb) { vb = d; vi = i; } });
  // the way round a lateral closure: from `lateralSpan` behind the tip to just in front of it, and the dead end left between
  // THE DEAD END A LATERAL LEAVES. The air goes round the tongue's sides, and the midline it leaves behind -- the slot between the blade
  // and the palate, shut at the tip -- is a closed room hanging off the tract: that is where a lateral's ZERO comes from, and a leak
  // through the closure (which is all there was) has none. Measured from the TEETH, which do not move: hung off the tip it would hop a
  // section whenever the tongue moved, and a joint that hops while air streams through it is a click (the /ng/ lesson).
  let lat = null;
  if ((art.lateral ?? 0) > .01) { const a0 = Math.max(xs[1] + .2, teethX - .3 * anat.scale.oral - anat.lateralSpan * anat.scale.oral);
    lat = { at: a0, area: art.lateral * anat.lateralPocket * anat.scale.oral, length: anat.lateralSpan * anat.scale.oral }; }
  // the room under a raised blade, and where it opens (just behind the tip's own cut)
  const SL = anat.sublingual; let subl = null;
  if (SL && SL.area > 0) { const rise = (art.tipY ?? 0) - SL.from, tipA = sg.cuts.find((c) => c.tipCut)?.A ?? 1;
    // (open only while the air can get past the tip AND the mouth is not shut somewhere else -- both measured against this head's
    //  own size, or a big head's closure counts as open and the bang comes back)
    let least = 1e9; for (let k = 2; k < As.length; k++) if (As[k] < least) least = As[k];
    const hd = Math.sqrt(anat.scale.oral * anat.scale.pharynx), [lo, hi] = SL.opensAt ?? [0, 0];
    const gate = (a) => { const u = hi > lo ? Math.max(0, Math.min(1, (a / hd - lo) / (hi - lo))) : 1; return u * u * (3 - 2 * u); };
    const open = gate(tipA) * gate(least);
    if (rise > 0 && open > .01) { const V = Math.min(SL.max, SL.perCm * rise) * anat.scale.oral * anat.scale.oral * anat.scale.pharynx, A0 = SL.area * anat.scale.oral * open;
      subl = { at: tipAt ?? teethX, area: A0, length: Math.max(.25, V / (SL.area * anat.scale.oral)) }; } }
  return { xs, As, length: at, lipStart, teethX, velumX: xs[2 + vi], velumArea: art.velum * 1.6 * (anat.scale.oral + anat.scale.pharynx) / 2, subl, lat, sagittal: sg };
}
// onto a tube's equal sections. The array is ANCHORED AT THE LIPS: its last section is the first slice of the lip tube,
// and the rest of that (uniform) tube is the lip-end delay. Whatever the array does not reach at the other end lies
// in the (uniform) tube over the folds, and is the glottis-end delay. So the whole length is exact at every moment.
export function toSections(af, tube) {
  const N = tube.N, dx = tube.dx, out = new Float64Array(N), { xs, As } = af;
  const areaAt = (x) => { if (x <= xs[0]) return As[0]; for (let i = 1; i < xs.length; i++) if (x <= xs[i]) { const u = (x - xs[i - 1]) / Math.max(1e-9, xs[i] - xs[i - 1]); return As[i - 1] + (As[i] - As[i - 1]) * u; } return As[As.length - 1]; };
  const end = af.lipStart + dx, x0 = end - N * dx;                       // the array spans [x0, end]
  // A SECTION'S AREA IS THE HARMONIC MEAN OVER ITS SPAN. What a stretch of pipe does to the air moving through it goes
  // with length / area, so narrow places count for far more than wide ones, and a constriction shorter than a section is
  // still a constriction: it limits the flow. (An arithmetic mean averages it away -- and a rule that switched from "the
  // narrowest point" to "the mean" let a /t/'s opening vanish from the tube in a millisecond: a gust of air, a thump.)
  // The drawing's own points inside the span are sampled too, so a closure that is ONE point wide still shuts the tube.
  for (let i = 0, k0 = 0; i < N; i++) {
    const a = x0 + i * dx, b = a + dx; let inv = 0, cnt = 0, shut = false;
    const take = (v, w = 1) => { if (v < 1e-3) shut = true; inv += w / Math.max(v, 1e-3); cnt += w; };
    for (let k = 0; k < 5; k++) take(areaAt(a + (k + .5) / 5 * dx));
    while (k0 < xs.length && xs[k0] < a) k0++;
    for (let k = k0; k < xs.length && xs[k] <= b; k++) take(As[k], 1.5);
    out[i] = shut ? 0 : cnt / inv;
  }
  out[N - 1] = As[As.length - 1];
  // (the velum's joint is placed ONCE per tube: the array is anchored at the lips, so as the mouth's path lengthens and
  // shortens the velum would wander from section to section -- and a three-way joint that hops a section, among the huge
  // opposing waves of a narrow place, is a click: every /ng/ had one)
  // (so are the piriform sinuses, which open at the top of the larynx tube)
  tube.larynxArea = As[0];                                               // (what lies below the array is the larynx tube)
  if (tube.pirPlaced === undefined) { tube.pirAt = Math.max(0, Math.min(5, Math.round((xs[1] + .2 - x0) / dx) - 1)); tube.pirPlaced = true; }
  if (tube.velumPlaced === undefined) { tube.velumAt = Math.min(N - 2, Math.max(1, Math.round((af.velumX - x0) / dx))); tube.velumPlaced = true; }
  // the room under the tongue: its mouth, its length there and back, and the joint it hangs on (this one DOES move with the tip,
  // but only while the tip is raised, and its area is glided in and out, so it never hands a joint a step)
  if (af.subl) { tube.sublAT = af.subl.area; tube.sublDT = Math.max(1.2, Math.min(40, 2 * af.subl.length / dx)); tube.sublAt = Math.min(N - 3, Math.max(1, Math.round((af.subl.at - x0) / dx) - 1)); }      // (a section BEHIND the tip's own: the joint there is a wide one)
  else tube.sublAT = 0;
  // the road round a lateral closure: where it leaves the midline, where it comes back, and how long it is
  if (af.lat) { tube.latAT = af.lat.area; tube.latAt = Math.min(N - 3, Math.max(1, Math.round((af.lat.at - x0) / dx))); tube.latDT = Math.max(1.2, Math.min(40, 2 * af.lat.length / dx)); }
  else tube.latAT = 0;
  tube.teethAt = Math.round((af.teethX - x0) / dx);
  return { areas: out, lipExtra: Math.max(0, af.length - end), gloExtra: Math.max(0, x0), velum: af.velumArea, short: x0 < 0 ? -x0 : 0 };
}

// ---- a constriction asked for, turned into articulator values ---------------------------------------------------------
// the wall point of a named place and the direction into the mouth there
// (`name` may also be [from, to, share]: a place part of the way from one to another -- a /k/ slides along the palate with
// the vowel, and must SLIDE: jumping from "velar" to "palatal" between two frames moved the tongue a centimetre at once, a click)
export function placeOf(name, anat = ANATOMY) {
  if (Array.isArray(name)) { const a = placeOf(name[0], anat), b = placeOf(name[1], anat), u = name[2], n = [a.n[0] + (b.n[0] - a.n[0]) * u, a.n[1] + (b.n[1] - a.n[1]) * u], L = Math.hypot(n[0], n[1]);
    return { W: [a.W[0] + (b.W[0] - a.W[0]) * u, a.W[1] + (b.W[1] - a.W[1]) * u], n: [n[0] / L, n[1] / L] }; }
  const sx = anat.scale.oral, sy = anat.scale.pharynx, P = anat.places[name]; if (!P) throw new Error(`no place "${name}"`);
  const W = [P[0] * sx, P[1] * sy], wall = anat.wall.map((q) => [q[0] * sx, q[1] * sy]);
  let best = 0, bd = 1e9; for (let i = 0; i + 1 < wall.length; i++) { const m = mul(add(wall[i], wall[i + 1]), .5), d = len(sub(m, W)); if (d < bd) { bd = d; best = i; } }
  const t = sub(wall[best + 1], wall[best]), L = len(t); let n = [t[1] / L, -t[0] / L];
  const O = [anat.grid.centre[0] * sx, anat.grid.centre[1] * sy]; if (dot(n, sub(O, W)) < 0) n = mul(n, -1);
  return { W, n };
}
// the gap that gives an area at the TIP (the inverse of the tip cut's law, peel and all); shut = pressed a little INTO the wall
// (in the REFERENCE head, along the direction n there: the stretched gap is the reference gap x `st`)
const gapFor = (area, region, anat, n) => { if (area <= 0) return -.2; const [al, be] = anat.areaLaw[region], k = al * (anat.scale.oral + anat.scale.pharynx) / 2, st = Math.hypot(n[0] * anat.scale.oral, n[1] * anat.scale.pharynx), g = Math.pow(area / (k * st), 1 / be);
  return (g >= anat.tipPeel ? g : Math.pow(area * anat.tipPeel / (k * st), 1 / (be + 1))) + anat.contact; };
const refHead = (anat) => anat.scale.oral === 1 && anat.scale.pharynx === 1 ? anat : { ...anat, scale: { oral: 1, pharynx: 1 } };
const unplace = (P, art, anat) => rot([P[0] / anat.scale.oral, P[1] / anat.scale.pharynx], anat.jawPivot, art.jaw * anat.tongue.jawShare);   // world -> the tongue's own (jaw) frame
// put the tongue TIP so that the airway at `place` has `area` (0 = shut); the body and jaw are taken as they are in `art`
// (if the tip cannot reach from where the body is, the body comes part of the way: nobody says /t/ with the tongue left in /a/)
export function solveTip(art, place, area, anat = ANATOMY) {
  const ref = refHead(anat), { W, n } = placeOf(place, ref), P = add(W, mul(n, gapFor(area, "front", anat, n))), T = anat.tongue;
  // (the body comes EXACTLY as far as the tip falls short -- in steps of 1.8mm it jumped two steps between frames, 140 cm/s)
  const q = unplace(P, art, ref), hi = T.radius + T.tipReach[1] - .1;
  for (let k = 0; k < 4; k++) {
    const C = add(T.centre, [art.bodyX, art.bodyY]), rel = sub(q, C), L = len(rel), tx = rel[0] - T.tipRest[0], ty = rel[1] - T.tipRest[1];
    art.tipX = tx; art.tipY = ty;
    const far = Math.max(0, L - hi), ox = Math.max(0, tx - ARTICULATORS.tipX[1]), oy = Math.max(0, ty - ARTICULATORS.tipY[1]); if (far + ox + oy < 1e-6) break;
    art.bodyX += rel[0] / L * far + ox; art.bodyY += rel[1] / L * far + oy;
  }
  { const rel = sub(q, add(T.centre, [art.bodyX, art.bodyY])); art.tipX = rel[0] - T.tipRest[0]; art.tipY = rel[1] - T.tipRest[1]; }
  return clampArt(art);
}
// ...and the tongue BODY. Its circle nears a wall about as curved as itself, so the narrowest place is not where a
// single point says it is: the body is walked in along the direction into the mouth at `place` until the narrowest
// measured cut IS the area asked for (bisection on the real drawing), and pressed a little further for a closure.
export function solveBody(art, place, area, anat = ANATOMY) {
  const ref = refHead(anat), { W, n } = placeOf(place, ref), r = anat.tongue.radius, T = anat.tongue;
  const put = (gap) => { const q = unplace(add(W, mul(n, r + gap)), art, ref); art.bodyX = q[0] - T.centre[0]; art.bodyY = q[1] - T.centre[1]; };
  const narrowest = () => { let m = 1e9; for (const c of sagittal(art, anat).cuts) if (!c.tipCut && c.region !== "front") m = Math.min(m, c.A); return m; };
  let lo = -.4, hi = 1.6;                                 // gap: lo shuts, hi is wide open
  for (let k = 0; k < 14; k++) { const mid = (lo + hi) / 2; put(mid); if (narrowest() > Math.max(area, 1e-4)) hi = mid; else lo = mid; }
  put(area <= 0 ? lo - .3 : (lo + hi) / 2);              // (shut: the target lies a little INSIDE the wall -- the body arrives at speed and presses)
  return art;                                             // (not clamped: a posture the ranges forbid is still the one that makes this sound)
}
// ...and the LIPS: their opening for an area
export function solveLips(art, area, anat = ANATOMY) {
  const w = Math.max(.6, anat.lips.width * (1 + .3 * (art.lipSpread ?? 0)) * anat.scale.oral - anat.lips.roundK * art.lipP * anat.lips.width * anat.scale.oral / 1.4);
  // (what the LIPS must do for this opening, the jaw's share of it taken off: asked for a closure with the jaw down, the lips have
  // to come further than shut -- ask them only for zero and a /b/ after an open vowel does not close)
  art.lipH = (area <= 0 ? 0 : area / (Math.PI / 4 * w * anat.scale.pharynx)) - anat.lips.jawShare * lipRide(art, anat); return clampArt(art);
}

// MOVE THE JAW AND LEAVE THE TONGUE WHERE IT WAS IN THE HEAD. The body (and the tip with it) rides `tongue.jawShare` of the jaw's
// turn, so a jaw held back carries the tongue with it and every vowel is wrong; a speaker who holds the jaw still puts the tongue
// back where the sound needs it -- which is what people do with a bite block between the teeth, and what lets a clenched speaker
// still be understood. The lips are NOT put back: they are on the chin, and a small jaw really is a smaller mouth (lips.jawShare).
export function setJaw(art, jaw, anat = ANATOMY) {
  const T = anat.tongue, was = rot(add(T.centre, [art.bodyX, art.bodyY]), anat.jawPivot, -art.jaw * T.jawShare);
  const now = rot(was, anat.jawPivot, jaw * T.jawShare);      // the same point, in the new jaw's frame
  return clampArt({ ...art, jaw, bodyX: now[0] - T.centre[0], bodyY: now[1] - T.centre[1] });
}

// ---- for a hand on the drawing: put an organ AT a point --------------------------------------------------------------
export function setBodyAt(art, P, anat = ANATOMY) { const q = unplace(P, art, anat), T = anat.tongue; art.bodyX = q[0] - T.centre[0]; art.bodyY = q[1] - T.centre[1]; return clampArt(art); }
export function setTipAt(art, P, anat = ANATOMY) { const q = unplace(P, art, anat), T = anat.tongue, rel = sub(q, add(T.centre, [art.bodyX, art.bodyY])); art.tipX = rel[0] - T.tipRest[0]; art.tipY = rel[1] - T.tipRest[1]; return clampArt(art); }
export function setJawAt(art, P, anat = ANATOMY) {
  const piv = anat.jawPivot, a0 = Math.atan2(anat.lowerTeeth[1] - piv[1], anat.lowerTeeth[0] - piv[0]), q = [P[0] / anat.scale.oral, P[1] / anat.scale.pharynx];
  art.jaw = (a0 - Math.atan2(q[1] - piv[1], q[0] - piv[0])) * 180 / Math.PI; return clampArt(art);
}

