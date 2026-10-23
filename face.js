// THE FACE (2026-09-30, the front rebuilt 2026-10-01): a low-poly head built on the anatomy -- the levels of the face
// (vertex, trichion, glabella, nasion, the eyes, zygion, pronasale, subnasale, the lips, the sulcus, gnathion, gonion)
// and the breadths across them (the canon: Farkas's adult means, in metres) -- LOFTED into one skin: a ring of
// points at each level, fuller or finer with the parameters, with BROW ridges, eye SOCKETS and CHEEKBONES as bumps
// and dips of the skin itself, the CHIN's boss and the JAW's width and angle in the levels. The FRONT of the face is
// then cut not in rings but in SHEETS BETWEEN GUIDE LINES (faceGeometry below): the midline pair, the nasolabial
// line, the cheek line, the face's edge -- the nose's flat sides and ridge, the lips tapering to their corners and
// the creases fall where the lines are, and `detail` splits the sheets. The back of the head stays plain rings
// (regular there, as heads are). On it: EYES (almonds with an iris) in the sockets, EYEBROWS, EARS (a plate with the
// helix's shape, flared), and the NECK under it all.
//
// The frame is the composite head's: the origin at the CRANIUM's centre, +x forward (where the face looks), y up,
// z to the figure's right. items.js draws it as the part type `face` (assets/items/faces/*.json) with the roles
// skin, lip, eye, iris, brow, hair -- and every number below can be turned by a parameter, so a definition is a
// man, a woman, a child, an elder, a stranger, from the same canon.
const DEG = Math.PI / 180;
const G = (v, m, s) => Math.exp(-((v - m) * (v - m)) / (2 * s * s));   // (a bell: how much of a feature at v)
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return a.map((v) => v / l); };

// The CANON, an adult head: at each level its height (from the cranium's centre), the front of the face, the half-
// breadth, and the back of the head (or the neck, below the jaw), in metres. Vertex to gnathion .232, breadth .15,
// length .19, bizygomatic .137, bigonial .10.
//  name        y       front  side   back
const LEVELS = [
  ["vertex",   .100,   .000,  .000,  .000],
  ["crown",    .088,   .050,  .045, -.060],
  ["forehead", .060,   .081,  .072, -.095],
  ["glabella", .015,   .090,  .075, -.100],
  ["nasion",   .000,   .084,  .076, -.100],
  ["eyes",    -.012,   .081,  .076, -.099],
  ["zygion",  -.030,   .085,  .069, -.096],
  ["pronasale",-.044,  .086,  .066, -.091],
  ["nosebase",-.055,   .086,  .062, -.086],
  ["lip up",  -.068,   .085,  .058, -.078],
  ["stomion", -.078,   .081,  .056, -.070],
  ["lip low", -.088,   .084,  .053, -.062],
  ["sulcus",  -.100,   .076,  .049, -.055],
  ["chin",    -.120,   .081,  .040, -.050],
  ["gnathion",-.132,   .070,  .034, -.050],
];
const GONION_Y = -.090;   // the jaw's angle
// the angles round each ring from the front (0) to the back (180): denser over the face
const THETAS = [0, 8, 16, 25, 35, 48, 62, 80, 100, 122, 145, 165, 180];

export const FACE_PARAMS = {   // (every factor 1, every depth in metres; a definition overrides what it likes)
  scale: 1, faceW: 1, jawW: 1, jawY: 1, chinW: 1, chin: 0, brow: .004, browY: 0, cheek: .004, socket: .006,
  forehead: 1, occiput: 1, crown: 1,
  noseL: 1, noseW: 1, noseTip: .028, noseBridge: .004, noseHump: 0, noseDorsum: .7, noseTopW: .008,
  eyeGap: 1, eyeR: .012, mouthW: 1, lipT: .005, lipUp: 1,
  earS: 1.15, earOut: 18, earBack: 8, earY: -.028, browL: 1, browT: 1,
  hairline: .060, neckR: .038, neckL: .07, hair: "hair",
  bare: 1,   // (the height above which the scalp is skin again: a tonsure's shaven crown -- the hairstyle's cap.top)
};

// THE HEAD'S GRID -- what the face and the hair share: the levels as the parameters shape them, the ring of points
// at each, its normals, and a point of the skin at any height and angle
export function headGrid(p, P) {
  const Q = { ...FACE_PARAMS, ...p }, S = Q.scale, det = Math.max(.5, Math.min(2, P.detail ?? 1));
  // ---- the levels as this face has them
  const lv = LEVELS.map(([name, y, f, s, b]) => ({ name, y, f, s, b }));
  const at = (name) => lv.find((l) => l.name === name);
  for (const l of lv) {
    if (l.y > 0) { l.f *= Q.forehead; l.b *= Q.occiput; }                 // (a sloping or a high forehead, a long skull)
    if (l.name === "crown" || l.name === "vertex") { l.y *= Q.crown; }
    if (l.y <= -.03) {                                                 // the jaw: its breadth, its chin
      const t = Math.min(1, (l.y - GONION_Y * Q.jawY) / (-.03 - GONION_Y * Q.jawY));   // 1 at the zygion .. 0 at the gonion
      l.s *= Q.jawW + (Q.faceW - Q.jawW) * Math.max(0, t);
      if (l.y <= -.1) l.s *= Q.chinW;
      if (l.y <= -.1) l.f += Q.chin * G(l.y, -.12, .012) / G(-.12, -.12, .012);
    } else l.s *= Q.faceW;
  }
  const yTop = at("vertex").y, yBot = at("gnathion").y;
  // ---- the skin: a point of the loft at level l, angle th (degrees from the front), side sg (+1 right, -1 left)
  const eyeTh = Math.asin(Math.min(.9, .033 * Q.eyeGap / at("eyes").s)) / DEG;
  const mouthTh = Math.asin(Math.min(.9, .026 * Q.mouthW / at("stomion").s)) / DEG;
  const yStom = at("stomion").y;
  const point = (l, th, sg, plain = false) => {   // (plain: the skull alone -- no features, no jaw: the new face's frame samples it)
    const t = th * DEG, fr = th <= 90;
    // the lips: their band tapers to the mouth's corners (an ellipse's edge), so the corner quads close to a point --
    // the whole level blends into the stomion's there (its depth and breadth too, or three rings of different size
    // would sit at one height: a step round the head)
    let ly = l.y, lf = l.f, ls = l.s, lb = l.b;
    if (l.name === "lip up" || l.name === "lip low") {
      const st = at("stomion"), w = Math.sqrt(Math.max(0, 1 - (th / (mouthTh * 1.15)) ** 2));
      ly = st.y + (l.y - st.y) * w; lf = st.f + (l.f - st.f) * w; ls = st.s + (l.s - st.s) * w; lb = st.b + (l.b - st.b) * w;
    }
    const n = 2.3;   // (the ring's fullness: 2 an ellipse, more a squarer head)
    const c = Math.cos(fr ? t : Math.PI - t), s = Math.sin(t);
    let x = (fr ? lf : lb) * Math.pow(Math.abs(c), 2 / n), z = ls * Math.pow(s, 2 / n);   // (lb is negative: the back)
    if (l.name === "vertex") { x = 0; z = 0; }
    // the features on the front of the face: a push (+) or a dip (-) along the ring's own outward direction
    let d = 0;
    if (fr && !plain) {
      d += Q.brow * (th < 16 ? 1 : G(th, 16, 16)) * G(l.y, .012 + Q.browY, .012);   // the brow ridge, continuous across the glabella
      d -= Q.socket * G(th, eyeTh, 11) * G(l.y, -.012, .014);                                                // the eye sockets
      d += Q.cheek * G(th, 52, 16) * G(l.y, -.03, .016);                                                     // the cheekbones
      d += Q.lipT * (G(l.y, -.068, .006) * Q.lipUp + G(l.y, -.088, .007)) * (th < mouthTh ? 1 : G(th, mouthTh, 6));   // the lips
      d -= Q.lipT * .7 * G(l.y, -.078, .004) * (th < mouthTh ? 1 : G(th, mouthTh, 6));                        // the parting
    }
    const out = norm([x, 0, z]);
    x += out[0] * d; z += out[2] * d;
    // (THIS FACE'S FOREHEAD: the guide-line face brings its forehead to its own profile -- foreheadOf -- and the scalp
    //  the hair grows from comes forward with it, or a child's upright brow stood through the fringe)
    if (fr && !plain) x += fh().push(ly, z);
    // THE JAWLINE: the mandible's lower edge runs from the chin's bottom back and UP to the jaw's angle under the
    // ear, and the skull's base continues it round the back; what lies below that line is not face but neck, so it
    // is drawn in to the neck's circle over a short fall -- a crease along the line, the jaw standing out from the
    // neck as it does (before this the sides narrowed smoothly to the chin: no jaw at all)
    const gnY = at("gnathion").y, goY = GONION_Y * Q.jawY;
    const yJaw = th <= 90 ? gnY + (goY - gnY) * Math.pow(th / 90, 1.6) : goY;
    if (ly < yJaw && !plain) {
      const u = Math.min(1, (yJaw - ly) / .014), ncx = -.005, nr = Q.neckR * 1.02;
      const nx = ncx + (x - ncx) * nr / Math.max(1e-6, Math.hypot(x - ncx, z)), nz = z * nr / Math.max(1e-6, Math.hypot(x - ncx, z));
      if (Math.hypot(x - ncx, z) > nr) { x = x + (nx - x) * u; z = z + (nz - z) * u; }
    }
    return [x, ly, z * sg];
  };
  // a point of the skin at any height (the levels interpolated), for what lies on it
  const levelAt = (y) => {
    for (let k = 1; k < lv.length; k++) if (y >= lv[k].y) { const a = lv[k - 1], b = lv[k], u = (y - a.y) / (b.y - a.y); return { name: "", y, f: a.f + (b.f - a.f) * u, s: a.s + (b.s - a.s) * u, b: a.b + (b.b - a.b) * u }; }
    return lv[lv.length - 1];
  };
  const skinAt = (y, th, sg, plain = false) => point(levelAt(y), th, sg, plain);
  let fh0 = null;
  const fh = () => fh0 ??= foreheadOf({ at, levelAt, point }, Q);
  // the grid: rows = levels top to bottom, columns = the angles right round (right side front to back, then the left back to front)
  const cols = [];
  for (const th of THETAS) cols.push([th, 1]);
  for (let i = THETAS.length - 2; i > 0; i--) cols.push([THETAS[i], -1]);
  const grid = lv.map((l) => cols.map(([th, sg]) => point(l, th, sg)));
  const R = grid.length, C = cols.length;
  const same = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) < 1e-6;
  const nrm = (r, c) => {   // (from the nearest rows that are not this point: where the lips' rows merge at the corners, they shade as one)
    let ru = r - 1, rd = r + 1;
    while (ru > 0 && same(grid[ru][c], grid[r][c])) ru--;
    while (rd < R - 1 && same(grid[rd][c], grid[r][c])) rd++;
    const up = grid[Math.max(0, ru)][c], dn = grid[Math.min(R - 1, rd)][c], lt = grid[r][(c - 1 + C) % C], rt = grid[r][(c + 1) % C];
    return norm(cross(sub(rt, lt), sub(dn, up)));   // (round the ring crossed with down the face: out of the skin)
  };
  return { Q, S, det, lv, at, yTop, yBot, eyeTh, mouthTh, point, levelAt, skinAt, cols, grid, R, C, nrm };
}


// =======================================================================================================================
// THE FACE ON GUIDE LINES (2026-10-05; docs/face.md). The front of the head is no longer the loft with bumps: a set of
// ANATOMICAL ATTRIBUTES (Farkas's measurements and the profile's angles) places the LANDMARKS, each from those it
// depends on -- the brow from the eye under it, the gonion from the jaw's angle and the chin, the mouth's corners from
// the mouth's width -- the landmarks are the nodes of a LATTICE of guide lines (rows: the brow, the lids, the lip
// borders, the jawline...; columns: the midline, the nose's side, the inner line through the endocanthion and the
// mouth's corner, the pupil's line, the outer line, the face's outline), and the skin is the lattice SUBDIVIDED --
// interpolating, so it passes through every guide line -- each new point bowed out by the ROUNDNESS of where it is
// (the forehead nearly flat, the cheeks full). The skull behind the face (the hair's scalp) is headGrid's loft above.
// Expressions and speech move the landmarks (ACTIONS); the lattice's topology never changes, so every build of a head
// has the same vertices in other places -- morph targets, when the game animates faces.
export const FACE_ATTRS = {
  // the profile (metres, degrees)
  faceHeight: .123, foreheadHeight: .062, foreheadAngle: 12, foreheadRound: .002, browRidge: .003,
  noseHeight: .052, noseProjection: .020, nasolabialAngle: 102, noseTip: .004, noseBridge: .003, noseHump: 0, noseWidth: .034, noseRidge: .0045,
  upperLipHeight: .021, upperVermilion: .008, lowerVermilion: .009, lowerLipHeight: .019, upperLipAngle: 8, lipProjection: .002,
  mentolabial: .007, chinProjection: 0, chinHeight: .013,
  // the eyes and the brows
  eyeDistance: .033, eyeWidth: .030, eyeHeight: .010, eyeTilt: 4, eyeLevel: -.010, eyeDepth: .016, irisR: .0058, lashThickness: .0011,
  // the teeth (behind the lips: the arch's width across its back ends, how far the arch curves back, how far behind
  // the stomion its front stands, the crowns' height)
  teeth: 1, teethWidth: .032, teethDepth: .012, teethSet: .005, teethHeight: .009,
  browHeight: .016, browArch: .003, browTail: .006, browThickness: .006,
  // the breadths
  upperWidth: .136, foreheadWidth: .112, lowerWidth: .098, chinWidth: .042, mouthWidth: .052, jawAngle: 122,
  cheekProjection: .003,
  // the soft tissue: `chubby` times each fat pad's own (face.js PADS: the cheeks, the jowls, under the chin, the lips...);
  // 0 bony, 1 the canon, 2 a full face, below 0 gaunt
  chubby: 1, chubForehead: 1, chubTemple: 1, chubEye: 1, chubNose: 1, chubCheek: 1, chubLips: 1, chubChin: 1, chubJaw: 1,
  // the actions (FACS: AU1 browInnerUp, AU2 browOuterUp, AU4 browDown, AU5 lidUp, AU43 blink, AU6 cheekUp, AU12 smile,
  // AU15 mouthDown, AU18 pucker, AU25 lipsPart, AU26 jawOpen), 0..1; `expression` and `viseme` name mixes of them
  browInnerUp: 0, browOuterUp: 0, browDown: 0, lidUp: 0, blink: 0, cheekUp: 0, smile: 0, mouthDown: 0, pucker: 0, lipsPart: 0, jawOpen: 0,
  expression: "neutral", viseme: "none",
};
export const ACTIONS = ["browInnerUp", "browOuterUp", "browDown", "lidUp", "blink", "cheekUp", "smile", "mouthDown", "pucker", "lipsPart", "jawOpen"];
export const EXPRESSIONS = {   // (the emotions, as the actions' mixes: the brows, the lids, the cheeks, the lips, the jaw)
  neutral: {}, smile: { smile: .7, cheekUp: .4 }, laugh: { smile: 1, cheekUp: .9, jawOpen: .35, lipsPart: .8, browOuterUp: .15, blink: .25 },
  frown: { browDown: .8, mouthDown: .35 }, surprise: { browInnerUp: .9, browOuterUp: .9, lidUp: .8, jawOpen: .45, lipsPart: .6 },
  sad: { browInnerUp: .85, mouthDown: .7, blink: .2 }, angry: { browDown: 1, lidUp: .35, mouthDown: .3, lipsPart: .15, pucker: .15 },
  fear: { browInnerUp: .9, browOuterUp: .45, lidUp: .75, lipsPart: .5, jawOpen: .15, mouthDown: .2 }, disgust: { browDown: .5, cheekUp: .7, mouthDown: .5, lipsPart: .1 },
  sleepy: { blink: .8, browOuterUp: -.2, mouthDown: .1 }, pout: { pucker: .8, mouthDown: .3, browInnerUp: .3 },
};
// the mouth shapes of speech (a viseme a phoneme class): jaw drop, the lips parted, rounded (pucker) or spread (smile)
export const VISEMES = {
  none: {}, A: { jawOpen: .65, lipsPart: .7 }, E: { jawOpen: .3, lipsPart: .55, smile: .35 }, I: { jawOpen: .18, lipsPart: .45, smile: .55 },
  O: { jawOpen: .45, lipsPart: .55, pucker: .6 }, U: { jawOpen: .15, lipsPart: .3, pucker: .95 }, MBP: { pucker: .1 }, FV: { jawOpen: .1, lipsPart: .25, mouthDown: .25 },
  L: { jawOpen: .35, lipsPart: .45 }, S: { jawOpen: .06, lipsPart: .25, smile: .3 }, TH: { jawOpen: .15, lipsPart: .35 },
};
const tanD = (a) => Math.tan(a * DEG), sinD = (a) => Math.sin(a * DEG), cosD = (a) => Math.cos(a * DEG);
// THE EAR'S PLACE on headGrid's skull (canonical units, the +z side): its plate's centre, standing just off the widest
// level within its reach, and its size -- the face draws it there, an earring hangs from its lobe (jewelry.js earFit)
export function earFrame(H) {
  const { Q, lv } = H, span = lv.filter((l) => Math.abs(l.y - Q.earY) < .036 * Q.earS);
  return { c: [-.012, Q.earY, Math.max(...span.map((l) => l.s)) + .002], e: Q.earS };
}
// THE FOREHEAD'S PROFILE, from the attributes: the glabella on its brow ridge, the trichion `foreheadHeight` up and
// leaning back by `foreheadAngle`, the mid forehead between them rounded out -- and how far the skin stands in front of
// the plain skull there. faceLattice brings its forehead rows to these points (in full on the midline, none 5 cm out);
// headGrid's skin -- the scalp the hair grows from -- is lifted by the same push, eased off from the trichion to the
// crown row and below the mid forehead to the brow, so a hairstyle lies on the forehead this face has.
// H: { at, levelAt, point } (headGrid's)
export function foreheadOf(H, p) {
  const A = { ...FACE_ATTRS, ...p };
  const gla = H.at("glabella");
  const g = [gla.f + A.browRidge, gla.y, 0];
  const tr = [g[0] - (A.foreheadHeight - g[1]) * tanD(A.foreheadAngle), A.foreheadHeight, 0];
  const fm = [(g[0] + tr[0]) / 2 + A.foreheadRound, (g[1] + tr[1]) / 2, 0];
  const plainX = (y) => H.point(H.levelAt(y), 0, 1, true)[0];
  const dTr = tr[0] - plainX(tr[1]), dFm = fm[0] - plainX(fm[1]), CROWN = .094;
  const ease = (t) => { const u = Math.max(0, Math.min(1, t)); return u * u * (3 - 2 * u); };
  const taper = (z) => Math.max(0, 1 - (z / .05) ** 2);
  const push = (y, z) => taper(z) * (y >= tr[1] ? dTr * (1 - ease((y - tr[1]) / (CROWN - tr[1])))
                                    : y >= fm[1] ? dFm + (dTr - dFm) * (y - fm[1]) / Math.max(1e-6, tr[1] - fm[1])
                                    : dFm * ease((y - g[1]) / Math.max(1e-6, fm[1] - g[1])));
  return { g, tr, fm, taper, push };
}
const L3 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const A3 = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
// the lattice's columns (right half, from the midline out) and rows (top to bottom), by name: the guide lines
export const FACE_COLUMNS = ["midline", "paramedian", "nose side", "inner line", "pupil line", "outer line", "malar line", "outline", "ear", "behind the ear", "occiput", "nape"];
export const FACE_ROWS = ["crown", "trichion", "mid forehead", "brow", "orbital sulcus", "upper lid", "lower lid", "infraorbital", "pronasale", "subnasale",
  "upper lip middle", "upper lip border", "upper lip inside", "lower lip inside", "lower lip border", "mentolabial sulcus", "pogonion", "jawline", "neck"];
const ROW = Object.fromEntries(FACE_ROWS.map((n, i) => [n, i]));

// THE LANDMARKS AND THE LATTICE: the attributes (and the actions) -> the right half's nodes, row by row
export function faceLattice(H, p) {
  const A = { ...FACE_ATTRS, ...p };
  const act = {};
  for (const src of [EXPRESSIONS[A.expression] ?? {}, VISEMES[A.viseme] ?? {}, Object.fromEntries(ACTIONS.map((k) => [k, A[k] ?? 0]))])
    for (const [k, v] of Object.entries(src)) act[k] = (act[k] ?? 0) + v;
  for (const k of ACTIONS) act[k] = Math.max(-1, Math.min(1.2, act[k] ?? 0));
  // the skull's surface at a height and a distance from the midline (the plain loft: no features), or at an angle
  const skAng = (y, th) => H.point(H.levelAt(y), th, 1, true);
  const skull = (y, z) => {
    let lo = 0, hi = 89.5;
    if (z >= skAng(y, hi)[2]) return skAng(y, hi);
    for (let i = 0; i < 22; i++) { const m = (lo + hi) / 2; if (skAng(y, m)[2] < z) lo = m; else hi = m; }
    return skAng(y, (lo + hi) / 2);
  };
  // ---- the profile
  const nas = H.at("nasion");
  const n = [nas.f, 0, 0], { g, tr, fm, taper } = foreheadOf(H, A);
  const sn = [n[0] + .002, -A.noseHeight, 0];
  const phi = A.upperLipAngle, colA = Math.max(-10, Math.min(55, -90 + phi + A.nasolabialAngle));   // (the columella's rise: the nasolabial angle, measured from the upper lip)
  const prn = [sn[0] + A.noseProjection, sn[1] + A.noseProjection * tanD(colA) + A.noseTip, 0];
  const colLen = A.noseProjection / Math.max(.3, cosD(colA));
  const col = [sn[0] + cosD(colA) * colLen * .5, sn[1] + sinD(colA) * colLen * .5 - .0008, 0];
  const stoY = sn[1] - A.upperLipHeight;
  const ls = [sn[0] + (A.upperLipHeight - A.upperVermilion) * tanD(phi) + A.lipProjection, stoY + A.upperVermilion, 0];
  const sto = [ls[0] - .003, stoY, 0];
  const li = [ls[0] - .0015, stoY - A.lowerVermilion, 0];
  const sl = [li[0] - A.mentolabial, stoY - A.lowerLipHeight, 0];
  const pg = [sl[0] + .006 + A.chinProjection, Math.min(sl[1] - .006, -A.faceHeight + A.chinHeight), 0];
  const me = [pg[0] - .011, Math.min(-A.faceHeight, pg[1] - .008), 0];
  const dorsum = (y) => {   // the nose's ridge, nasion to the supratip, the bridge's rise and a hump on it
    const t = Math.max(0, Math.min(1, (n[1] - y) / (n[1] - prn[1])));
    return n[0] + (prn[0] - .004 - n[0]) * Math.pow(t, 1.25) + A.noseBridge * Math.sin(Math.PI * Math.min(1, t * 1.1)) + A.noseHump * Math.exp(-((t - .45) ** 2) / .03);
  };
  // ---- the eyes (the fissure: en to ex, wrapping back round the eyeball, the outer corner lifted by the tilt)
  const ew = A.eyeWidth, back = .012 * ew / .030, rise = ew * sinD(A.eyeTilt);
  const en = [n[0] - A.eyeDepth, A.eyeLevel, A.eyeDistance / 2];
  const ex = [en[0] - back, en[1] + rise, en[2] + Math.sqrt(Math.max(1e-6, ew * ew - back * back - rise * rise))];
  const mid = [en[0] + .0035, (en[1] + ex[1]) / 2 + .0005, en[2] + (ex[2] - en[2]) * .47];
  const lL = [mid[0] - .0005, mid[1] - A.eyeHeight * .45 + .0015 * act.cheekUp + .0005 * act.blink, mid[2] + .0005];
  const uL0 = [mid[0] + .001, mid[1] + A.eyeHeight * .55 + .0025 * act.lidUp, mid[2] - .001];
  const uL = L3(uL0, [lL[0] + .001, lL[1] + .0004, lL[2]], Math.max(0, Math.min(1, act.blink)));   // (a blink brings the upper lid down onto the lower)
  // ---- the brows: HEAD above the endocanthion, APEX above the lateral limbus, TAIL beyond the exocanthion -- on the brow ridge
  const onRidge = (y, z) => { const q = skull(y, z); return [q[0] + A.browRidge * Math.max(0, 1 - z / .07), y, z]; };
  const bh = onRidge(en[1] + A.browHeight + .006 * act.browInnerUp - .005 * act.browDown, en[2] - .0015 - .003 * act.browDown);
  const ba = onRidge(uL0[1] + A.browHeight * .75 + A.browArch + .003 * act.browInnerUp + .006 * act.browOuterUp - .003 * act.browDown, en[2] + (ex[2] - en[2]) * .7);
  const bt = onRidge(ex[1] + A.browHeight * .6 + .005 * act.browOuterUp - .001 * act.browDown, ex[2] + A.browTail);
  // ---- the nose's wings
  const al = [sn[0] - .005, sn[1] + .009, A.noseWidth / 2], ac = [al[0] - .006, sn[1] + .006, al[2] + .002];
  // ---- the mouth's corners
  const ch = [sto[0] - .016 - .003 * act.smile, sto[1] + .001 + .007 * act.smile - .006 * act.mouthDown, A.mouthWidth / 2 + .004 * act.smile];
  ch[2] += (.012 - ch[2]) * .45 * Math.max(0, act.pucker);
  const pk = .004 * Math.max(0, act.pucker);   // (puckered lips push forward)
  const gap = .0018 * Math.max(0, act.lipsPart);
  // ---- the outline and the jaw: zygion (the widest), frontotemporale, the condyle before the ear, the gonion where
  // the ramus coming down from the condyle meets the mandible's body coming back from the chin at the jaw's angle
  const zy = skull(en[1] - .016, A.upperWidth / 2), ft = skull(g[1] + .006, A.foreheadWidth / 2);
  const co = [-.010, en[1] - .020, A.lowerWidth / 2 + .006];
  const jc = [me[0] - .014, me[1] + .004, A.chinWidth / 2];
  const goX = co[0] + .004, goY = Math.max(jc[1] + .015, Math.min(co[1] - .025, jc[1] + (jc[0] - goX) * tanD(A.jawAngle - 90)));
  const go = [goX, goY, A.lowerWidth / 2];
  // the outline below the zygion, down the cheek to the gonion (the masseter a little out): BY THE ROW -- the face's
  // lower rows rise toward the ear as the jawline does, from the infraorbital row (the zygion) to the jawline (the gonion)
  const contourAt = (r) => {
    const t = Math.max(0, Math.min(1, (r - ROW["infraorbital"]) / (ROW["jawline"] - ROW["infraorbital"])));
    return [zy[0] + (go[0] - zy[0]) * t, zy[1] + (go[1] - zy[1]) * t, zy[2] + (go[2] - zy[2]) * Math.pow(t, 1.3) + .003 * Math.sin(Math.PI * t)];
  };
  // the outline above the zygion: the forehead's side at the hairline, then the TEMPLE -- the temporal fossa, narrower
  // than the zygomatic arch below it and a little hollow -- from the frontotemporale at the brow out to the zygion
  const edge = (y) => {
    if (y >= ft[1]) { const t = Math.min(1, (y - ft[1]) / Math.max(.001, .062 - ft[1])); return skull(y, ft[2] * 1.06 + (skAng(y, 74)[2] - ft[2] * 1.06) * t * .5); }
    // (down the temple the outline comes back as well as out, onto the zygomatic arch: its depth eased from the
    //  frontotemporale's to the zygion's, not the skull's -- the skull's side stands well forward of the arch)
    const t = Math.max(0, Math.min(1, (ft[1] - y) / (ft[1] - zy[1]))), z = ft[2] * 1.06 + (zy[2] - ft[2] * 1.06) * t * t;
    const top = skull(ft[1], ft[2] * 1.06), e = t * t * (3 - 2 * t);
    return [top[0] + (zy[0] - top[0]) * e - .003 * Math.sin(Math.PI * t), y, z];
  };
  // the lower face's cheek between the inner line and the outline: a quarter of a superellipse from the one round to
  // the other (seen from above) -- a first place for the free nodes there, which the fill then smooths
  const cheeks = (a, b) => [25, 50, 72].map((ph) => {
    const k = 2 / 2.3, c = Math.pow(Math.cos(ph * DEG), k), sn2 = Math.pow(Math.sin(ph * DEG), k), t = ph / 90;
    return [b[0] + (a[0] - b[0]) * c, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * sn2];
  });
  // a forehead row: the skull at these distances from the midline, its middle brought to the profile's point
  const fore = (pt, zs) => { const d = pt[0] - skull(pt[1], 0)[0]; return zs.map((z) => { const q = skull(pt[1], z); return [q[0] + d * taper(z), pt[1], q[2]]; }); };
  const zF = [0, .006, .013, bh[2], ba[2], bt[2], ft[2]];
  // (the lateral orbital rim: just BEHIND the exocanthion -- the eye's outer corner lies in front of the bone -- and
  //  falling back as it goes out)
  const rim = (y, z) => [ex[0] - .003 - (z - ex[2]) * .3, y, z];
  const nr = A.noseRidge;
  const rows = [];
  rows[ROW["crown"]] = [0, 6, 13, 22, 32, 44, 58, 74].map((th) => skAng(.094, th));   // (high on the dome: the subdivision rounds it from the forehead up)
  rows[ROW["trichion"]] = [...fore(tr, zF), edge(tr[1])];
  rows[ROW["mid forehead"]] = [...fore(fm, zF), edge(fm[1])];
  rows[ROW["brow"]] = [g, onRidge(g[1] - .001, .006), onRidge((g[1] + bh[1]) / 2, (.006 + bh[2]) / 2), bh, ba, bt, skull(bt[1] + .002, bt[2] + .009), edge(bt[1])];
  const r4 = [n, [n[0] - .001, n[1] - .001, nr * 1.3], [en[0] + .009, en[1] + .004, en[2] - .006], [en[0] + .003, en[1] + (bh[1] - en[1]) * .45, en[2] - .001],
              [uL0[0] - .004, uL0[1] + (ba[1] - uL0[1]) * .42, uL0[2]], [ex[0] + .002, ex[1] + (bt[1] - ex[1]) * .4, ex[2] + .001], rim(ex[1] + .007, ex[2] + .009)];
  rows[ROW["orbital sulcus"]] = [...r4, edge(r4[6][1])];
  const yU = en[1] + .002, yD = en[1] - .006;
  rows[ROW["upper lid"]] = [[dorsum(yU), yU, 0], [dorsum(yU) - .0008, yU, nr], [en[0] + .006, en[1] + .001, en[2] - .006], en, uL, ex, rim(ex[1] + .001, ex[2] + .010), edge(ex[1])];
  rows[ROW["lower lid"]] = [[dorsum(yD), yD, 0], [dorsum(yD) - .0008, yD, nr], [en[0] + .005, en[1] - .004, en[2] - .006], en, lL, ex, rim(ex[1] - .004, ex[2] + .010), edge(ex[1] - .004)];
  const yI = lL[1] - .008, cp = A.cheekProjection;
  rows[ROW["infraorbital"]] = [[dorsum(yI), yI, 0], [dorsum(yI) - .001, yI, nr * 1.1], [en[0] + .004, yI, en[2] - .005], [en[0] - .001, lL[1] - .006, en[2] + .001],
    [lL[0] - .001 + cp * .5, lL[1] - .008, lL[2]], [ex[0] + .003 + cp * .6, ex[1] - .010, ex[2] + .001], [ex[0] - .003 + cp * .4, ex[1] - .012, ex[2] + .011], zy];
  // the upper cheek -- the malar eminence below the outer eye -- set from the eye's own landmarks, a little before the lids
  rows[ROW["pronasale"]] = [prn, [prn[0] - .005, prn[1] - .0005, nr * 1.4], al, [al[0] - .006, al[1] + .001, al[2] + .003],
    [lL[0] + .002 + cp, prn[1] + .002, mid[2] + .003], [ex[0] + .006 + cp, prn[1] + .006, ex[2] + .002], [ex[0] - .001 + cp * .6, prn[1] + .006, (ex[2] + zy[2]) / 2 + .004], contourAt(ROW["pronasale"])];
  const r9 = [sn, [sn[0] - .0006, sn[1] - .0012, .0045], [al[0] - .005, sn[1] + .0008, al[2] - .004], [ac[0] - .002, sn[1] - .002, al[2] + .005]];
  const c9 = contourAt(ROW["subnasale"]);
  rows[ROW["subnasale"]] = [...r9, ...cheeks(r9[3], c9), c9];
  // the lips: the borders' nodes and the inner rows', all meeting at the mouth's corner
  const lipRow = (mp, y1, zIn, k) => { const a = [mp[0] + pk, mp[1], 0], b = [mp[0] - .0007 + pk, y1, zIn], c = [mp[0] + (ch[0] - mp[0]) * .5 + pk * .6, mp[1] + k, zIn + (ch[2] - zIn) * .55]; return [a, b, c, ch]; };
  // (the fold beside the corner: a little behind it, never a lump)
  const lipSide = (y, r) => { const c7 = contourAt(r), c4 = [ch[0] - .005, y, ch[2] + .010]; return [c4, ...cheeks(c4, c7).slice(1), c7]; };
  rows[ROW["upper lip border"]] = [...lipRow(ls, ls[1] + .0018, .0048, -.001), ...lipSide(ch[1] + .0055, ROW["upper lip border"])];
  rows[ROW["upper lip inside"]] = [...lipRow([sto[0], sto[1] + gap, 0], sto[1] + gap, .006, -gap * .2), ...lipSide(ch[1] + .002, ROW["upper lip inside"])];
  rows[ROW["lower lip inside"]] = [...lipRow([sto[0], sto[1] - gap, 0], sto[1] - gap, .006, gap * .2), ...lipSide(ch[1] - .002, ROW["lower lip inside"])];
  rows[ROW["lower lip border"]] = [...lipRow(li, li[1] + .0004, .006, .002), ...lipSide(ch[1] - .0055, ROW["lower lip border"])];
  // the upper lip's MIDDLE: halfway from the nose's lower edge to the lip's border (the philtrum's groove, its columns,
  // the lip's side above the corner) -- with the nasolabial fold beside the mouth and the mentolabial sulcus under it,
  // the loop that bounds the area round the mouth
  const S9 = rows[ROW["subnasale"]], LB = rows[ROW["upper lip border"]];
  rows[ROW["upper lip middle"]] = S9.map((q, c) => {
    const m = L3(q, LB[c], .5);
    if (c === 0) return [m[0] - .0012, m[1], 0];
    if (c === 1) return [m[0] + .0004, m[1], m[2]];
    if (c === 3) return [m[0] + .002, m[1], m[2]];
    if (c === 4) return [LB[4][0] + .002, (S9[3][1] + LB[4][1]) / 2, (S9[3][2] + LB[4][2]) / 2 + .002];
    return m;
  });
  const r14 = [sl, [sl[0] - .0005, sl[1], .007], [sl[0] - .003, sl[1] + .001, .014], [ch[0] - .002, ch[1] + (sl[1] - ch[1]) * .65, ch[2] - .001]], c14 = contourAt(ROW["mentolabial sulcus"]);
  rows[ROW["mentolabial sulcus"]] = [...r14, [ch[0] - .007, r14[3][1] - .002, ch[2] + .006], ...cheeks(r14[3], c14).slice(1), c14];   // (the fold's end: the marionette line below the corner)
  const r15 = [pg, [pg[0] - .0008, pg[1], .007], [pg[0] - .007, pg[1] + .002, A.chinWidth / 2], [jc[0] + .004, pg[1] + .006, A.chinWidth / 2 + .009]], c15 = contourAt(ROW["pogonion"]);
  rows[ROW["pogonion"]] = [...r15, ...cheeks(r15[3], c15), c15];
  rows[ROW["jawline"]] = [me, [me[0] - .0006, me[1] + .0003, .008], jc, ...[.2, .45, .7, .88].map((t) => A3(L3(jc, go, t), [0, 0, .004 * Math.sin(Math.PI * t)])), go];
  // the neck's top: the throat under the chin, rising round the side to under the gonion
  const ncx = -.005, nR = (p.neckR ?? H.Q.neckR), cv = [ncx + nR, me[1] + .006, 0];
  const jaw = rows[ROW["jawline"]], aGo = Math.atan2(go[2], go[0] - ncx);
  rows[ROW["neck"]] = jaw.map((q) => { const a = Math.atan2(q[2], q[0] - ncx), t = Math.min(1, a / aGo); return [ncx + nR * Math.cos(a), cv[1] + (go[1] - .016 - cv[1]) * t, nR * Math.sin(a)]; });
  // ---- the jaw's drop: the rows below the upper lip turn about the hinge at the condyle -- all but the mouth's
  // CORNER, where the four lip rows meet: it goes a third of the way with the jaw, and all four keep it, so the lips
  // stay joined at their corners however wide the mouth opens
  const th = -20 * DEG * Math.max(0, act.jawOpen);
  const turn = (q, a) => { const dx = q[0] - co[0], dy = q[1] - co[1]; return [co[0] + dx * Math.cos(a) - dy * Math.sin(a), co[1] + dx * Math.sin(a) + dy * Math.cos(a), q[2]]; };
  if (th) for (let r = ROW["lower lip inside"]; r < rows.length; r++) rows[r] = rows[r].map((q, c) => turn(q, th * (r === ROW["neck"] ? .5 : 1) * (c === 7 ? .8 : 1)));
  const corner = th ? turn(ch, th / 3) : ch;
  for (const r of ["upper lip border", "upper lip inside", "lower lip inside", "lower lip border"]) rows[ROW[r]][3] = corner;
  // THE GUIDE LINES THAT ARE FEATURES: per row, the columns where its nodes are real (the rest of the lattice is free:
  // the smooth fill between them -- the lip rows do not run on across the cheeks, the lids not across the nose; and
  // beside the mouth nothing at all: the cheek from the lips' corner to the face's outline is ONE surface, the
  // nasolabial fold no line of the frame -- each lip row's own node out there put a bump in the cheek)
  const REAL = { "crown": "0-7", "trichion": "0-7", "mid forehead": "0-7", "brow": "0-7", "orbital sulcus": "0 3-5 7", "upper lid": "0 3-5 7", "lower lid": "0 3-5 7",
    "infraorbital": "0-5 7", "pronasale": "0-3 5 7", "subnasale": "0-3 7", "upper lip middle": "0-3 7", "upper lip border": "0-3 7", "upper lip inside": "0-3 7",
    "lower lip inside": "0-3 7", "lower lip border": "0-3 7", "mentolabial sulcus": "0-3 7", "pogonion": "0-2 7", "jawline": "0-7", "neck": "0-7" };
  // (the midline -- the profile -- and the outline are real all the way down: they are the face's silhouettes)
  const realCols = FACE_ROWS.map((n) => { const set = new Set(); for (const t of REAL[n].split(" ")) { const [a, b] = t.split("-").map(Number); for (let c = a; c <= (b ?? a); c++) set.add(c); } return set; });
  const isReal = (r, c) => c >= 8 || realCols[r].has(c);   // (the skull behind the outline is the loft's: real)
  // ...and of the real ones, those that are only SHAPE (the skull's forehead, the brow ridge beside the glabella): real,
  // but no guide line is drawn through them -- the forehead carries the brow line and the hairline, nothing more
  const SHAPE = { "crown": "0-7", "trichion": "1-2", "mid forehead": "1-7", "brow": "1-2" };
  const shapeCols = FACE_ROWS.map((n) => { const set = new Set(); for (const t of (SHAPE[n] ?? "").split(" ").filter(Boolean)) { const [a, b] = t.split("-").map(Number); for (let c = a; c <= (b ?? a); c++) set.add(c); } return set; });
  const isGuide = (r, c) => c < 8 && realCols[r].has(c) && !shapeCols[r].has(c);
  return { A, act, rows, isReal, isGuide, jaw: { th, turn }, lm: { n, g, tr, sn, prn, col, ls, sto, li, sl, pg, me, en, ex, mid, uL, lL, bh, ba, bt, al, ac, ch, zy, ft, co, go, jc, cv }, ncx, nR };
}

// ---- THE SURFACE: a smooth field over the lattice's domain (u: the ring's columns, v: the rows) -- the cubic through
// each line's nodes with chord-length tangents (no overshoot where the nodes crowd), along the rows, then down the
// columns. Every vertex of the mesh, at any detail, is a point of it: the detail adds points, never shape.
const same3 = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) < 1e-7;
const dist3 = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
function herm(p0, p1, p2, p3, t) {
  if (same3(p1, p2)) return p1.slice();
  if (!p0 || same3(p0, p1)) p0 = [2 * p1[0] - p2[0], 2 * p1[1] - p2[1], 2 * p1[2] - p2[2]];
  if (!p3 || same3(p3, p2)) p3 = [2 * p2[0] - p1[0], 2 * p2[1] - p1[1], 2 * p2[2] - p1[2]];
  const d01 = dist3(p0, p1), d12 = dist3(p1, p2), d23 = dist3(p2, p3);
  const a = d12 / Math.max(1e-9, d01 + d12), b = d12 / Math.max(1e-9, d12 + d23);
  const t2 = t * t, t3 = t2 * t, h00 = 2 * t3 - 3 * t2 + 1, h10 = t3 - 2 * t2 + t, h01 = -2 * t3 + 3 * t2, h11 = t3 - t2;
  return [0, 1, 2].map((k) => h00 * p1[k] + h10 * (p2[k] - p0[k]) * a + h01 * p2[k] + h11 * (p3[k] - p1[k]) * b);
}
function latticeField(G) {
  const RR = G.length, CC = G[0].length, at = (r, c) => (r < 0 || r >= RR ? null : G[r][((c % CC) + CC) % CC]);
  return (u, v) => {
    const c = Math.floor(u), tu = u - c;
    const r = Math.max(0, Math.min(RR - 2, Math.floor(v))), tv = v - r;
    const row = (rr) => (rr < 0 || rr >= RR ? null : tu < 1e-9 ? at(rr, c).slice() : herm(at(rr, c - 1), at(rr, c), at(rr, c + 1), at(rr, c + 2), tu));
    const q1 = row(r), q2 = row(r + 1);
    if (tv < 1e-9) return q1;
    if (tv > 1 - 1e-9) return q2;
    return herm(row(r - 1), q1, q2, row(r + 2), tv);
  };
}

// ---- THE FRAME'S MESH: the regions the guide lines bound, on the half domain (u 0 .. the nape), each split into
// triangles between its own boundary nodes -- the lowest detail is the frame itself, no vertex that is not a node
// of a guide line (or of the skull's frame behind the face). V[r][c]: a vertex node. A unit edge of the lattice
// between two vertex nodes is a WALL; the cells a flood fill reaches without crossing a wall are one region; its
// boundary is ear-clipped in (u, v).
function frameMesh(V, RR, HC, matOfCell) {
  const NR = RR - 1, NC = HC - 1, reg = Array.from({ length: NR }, () => new Array(NC).fill(-1));
  const wallH = (r, c) => V[r][c] && V[r][c + 1];   // the edge (r, c)-(r, c+1)
  const wallV = (r, c) => V[r][c] && V[r + 1][c];   // the edge (r, c)-(r+1, c)
  let n = 0;
  for (let r0 = 0; r0 < NR; r0++) for (let c0 = 0; c0 < NC; c0++) {
    if (reg[r0][c0] >= 0) continue;
    const st = [[r0, c0]]; reg[r0][c0] = n;
    while (st.length) {
      const [r, c] = st.pop();
      const go = (rr, cc, blocked) => { if (rr < 0 || cc < 0 || rr >= NR || cc >= NC || blocked || reg[rr][cc] >= 0) return; reg[rr][cc] = n; st.push([rr, cc]); };
      go(r - 1, c, wallH(r, c)); go(r + 1, c, wallH(r + 1, c)); go(r, c - 1, wallV(r, c)); go(r, c + 1, wallV(r, c + 1));
    }
    n++;
  }
  const tris = [];
  for (let k = 0; k < n; k++) {
    // the region's boundary: each cell's edges (corners in the order (c, r) (c+1, r) (c+1, r+1) (c, r+1)) whose other side
    // is not the region, chained into loops
    const out = new Map(), cells = [];
    const add = (a, b) => { const key = a.join(","); if (!out.has(key)) out.set(key, []); out.get(key).push(b); };
    for (let r = 0; r < NR; r++) for (let c = 0; c < NC; c++) if (reg[r][c] === k) {
      cells.push([r, c]);
      const inR = (rr, cc) => rr >= 0 && cc >= 0 && rr < NR && cc < NC && reg[rr][cc] === k;
      if (!inR(r - 1, c)) add([c, r], [c + 1, r]);
      if (!inR(r, c + 1)) add([c + 1, r], [c + 1, r + 1]);
      if (!inR(r + 1, c)) add([c + 1, r + 1], [c, r + 1]);
      if (!inR(r, c - 1)) add([c, r + 1], [c, r]);
    }
    const loops = [];
    while (out.size) {
      const startKey = out.keys().next().value, loop = [];
      let cur = startKey.split(",").map(Number), prev = null;
      for (let guard = 0; guard < 10000; guard++) {
        const key = cur.join(","), nexts = out.get(key);
        if (!nexts || !nexts.length) break;
        let pick = 0;
        if (nexts.length > 1 && prev) {   // (a pinch: take the sharpest turn, so the loops do not cross)
          const din = [cur[0] - prev[0], cur[1] - prev[1]];
          let best = -Infinity;
          nexts.forEach((q, i) => { const d = [q[0] - cur[0], q[1] - cur[1]], cr = din[0] * d[1] - din[1] * d[0], dt = din[0] * d[0] + din[1] * d[1], ang = Math.atan2(cr, dt); if (ang > best) { best = ang; pick = i; } });
        }
        const nx = nexts.splice(pick, 1)[0];
        if (!nexts.length) out.delete(key);
        loop.push(cur); prev = cur; cur = nx;
        if (cur.join(",") === startKey && !(out.get(startKey)?.length)) break;
        if (cur.join(",") === startKey) break;
      }
      if (loop.length >= 3) loops.push(loop);
    }
    const area = (L) => L.reduce((s, p, i) => { const q = L[(i + 1) % L.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0) / 2;
    loops.sort((a, b) => Math.abs(area(b)) - Math.abs(area(a)));
    let poly = loops[0];
    for (const hole of loops.slice(1)) {   // (a hole: bridged to the nearest point of the outer loop)
      let bi = 0, bj = 0, bd = Infinity;
      hole.forEach((h, i) => poly.forEach((o, j) => { const d = (h[0] - o[0]) ** 2 + (h[1] - o[1]) ** 2; if (d < bd) { bd = d; bi = i; bj = j; } }));
      poly = [...poly.slice(0, bj + 1), ...hole.slice(bi), ...hole.slice(0, bi + 1), ...poly.slice(bj)];
    }
    const mat = matOfCell(cells);
    for (const t of earClip(poly)) tris.push({ pts: t, mat });
  }
  return tris;
}
// ear clipping in the domain (the boundary's nodes all kept: a neighbour region shares them -- no T-junctions)
function earClip(poly0) {
  let P = poly0.slice();
  const cross = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const sgn = Math.sign(P.reduce((s, p, i) => { const q = P[(i + 1) % P.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0)) || 1;
  const inTri = (p, a, b, c) => { const d1 = cross(a, b, p) * sgn, d2 = cross(b, c, p) * sgn, d3 = cross(c, a, p) * sgn; return d1 >= -1e-9 && d2 >= -1e-9 && d3 >= -1e-9; };
  const out = [];
  for (let guard = 0; P.length > 3 && guard < 20000; guard++) {
    let cut = -1, bestQ = -Infinity;
    for (let i = 0; i < P.length; i++) {
      const a = P[(i - 1 + P.length) % P.length], b = P[i], c = P[(i + 1) % P.length];
      const cr = cross(a, b, c) * sgn;
      if (cr <= 1e-9) continue;
      let ok = true;
      for (const q of P) { if (q === a || q === b || q === c || (q[0] === a[0] && q[1] === a[1]) || (q[0] === b[0] && q[1] === b[1]) || (q[0] === c[0] && q[1] === c[1])) continue; if (inTri(q, a, b, c)) { ok = false; break; } }
      if (!ok) continue;
      // (of the ears, the best shaped: the least sliver)
      const l = Math.max((a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2, (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2, (b[0] - c[0]) ** 2 + (b[1] - c[1]) ** 2), qual = cr / l;
      if (qual > bestQ) { bestQ = qual; cut = i; }
    }
    if (cut < 0) {   // (only collinear tips left: drop one -- the rest is no area)
      const i = P.findIndex((b, k) => Math.abs(cross(P[(k - 1 + P.length) % P.length], b, P[(k + 1) % P.length])) < 1e-9);
      if (i < 0) break;
      P.splice(i, 1); continue;
    }
    out.push([P[(cut - 1 + P.length) % P.length], P[cut], P[(cut + 1) % P.length]]);
    P.splice(cut, 1);
  }
  if (P.length === 3 && Math.abs(cross(P[0], P[1], P[2])) > 1e-9) out.push(P);
  return out;
}

// ---- SOFT TISSUE: the fat pads over the frame (u, v in the half domain), out along the skin's normal -- `chubby`
// times each pad's region (`chubCheek`, ...), metres at 1: a full face is fuller cheeks, jowls, a double chin, not a
// rounder interpolation (which bowed whole spans out: grotesque)
const PADS = [
  { u: 5.0, v: 10.8, su: 1.5, sv: 2.6, k: "chubCheek", m: .0045 },   // the buccal pad, the cheek's fullness
  { u: 5.3, v: 7.9, su: 1.0, sv: 1.1, k: "chubCheek", m: .0018 },    // the malar pad over the cheekbone
  { u: 4.6, v: 16.6, su: 1.8, sv: 1.1, k: "chubJaw", m: .0025 },     // the jowls
  { u: 1.6, v: 17.6, su: 2.4, sv: .8, k: "chubJaw", m: .004 },       // under the chin
  { u: 2.6, v: 1.8, su: 3.0, sv: 1.4, k: "chubForehead", m: .0012 }, // the forehead
  { u: 6.6, v: 4.2, su: 1.0, sv: 2.0, k: "chubTemple", m: .0012 },   // the temple
  { u: 1.3, v: 12.5, su: 1.4, sv: 1.6, k: "chubLips", m: .0010 },    // the lips' fullness
  { u: .7, v: 16.0, su: 1.2, sv: 1.0, k: "chubChin", m: .0015 },     // the chin's pad
  { u: .3, v: 8.3, su: .9, sv: .6, k: "chubNose", m: .0010 },        // the nose's tip
  { u: 4.0, v: 4.4, su: .9, sv: .6, k: "chubEye", m: .0007 },        // the upper lid's fold
];

export const FRAME_DEBUG = { last: null };
export function faceGeometry(p, P, emitFor, prims) {
  const H = headGrid(p, P), { Q, S, lv, yTop } = H;
  // (the attributes: the part's own, or the item's params by the same name -- a definition need not map each one)
  const F = faceLattice(H, { ...Object.fromEntries(Object.keys(FACE_ATTRS).filter((k) => P[k] !== undefined).map((k) => [k, P[k]])), ...p }), { A, rows } = F;
  // ---- the whole ring: the right half's columns, the back of the head behind the outline (the skull's loft, its rows
  // spread evenly toward the nape), the left half mirrored
  const RN = rows.length, TH_BACK = [100, 125, 150, 180], yBackBot = -.115, yBackTop = .094;
  const full = rows.map((row, r) => {
    const y7 = row[7][1], yEven = yBackTop + (yBackBot - yBackTop) * r / (RN - 1);
    return [...row, ...TH_BACK.map((th, k) => H.skinAt(y7 + (yEven - y7) * [.35, .7, 1, 1][k], th, 1))];   // (the loft draws the back in to the neck below the jaw: the nape)
  });
  const RC = full[0].length;   // 12: the midline .. the nape
  const ring = (row) => [...row, ...row.slice(1, RC - 1).reverse().map((q) => [q[0], q[1], -q[2]])];
  const G = full.map(ring);
  const uAbsOf = (c) => (c < RC ? c : 2 * (RC - 1) - c);
  // THE FREE NODES: the fill between the real ones (Gauss-Seidel on the Laplacian, a membrane through the guide lines,
  // which never overshoots them), so the field through the lattice takes its shape from the guides alone
  const RR = G.length, CC = G[0].length, real = G.map((row, r) => row.map((_, c) => F.isReal(r, uAbsOf(c))));
  const P0 = (r, c) => G[r][(c + CC) % CC];
  for (let it = 0; it < 120; it++) for (let r = 1; r < RR - 1; r++) for (let c = 0; c < CC; c++) {
    if (real[r][c]) continue;
    const n4 = [P0(r - 1, c), P0(r + 1, c), P0(r, c - 1), P0(r, c + 1)];
    G[r][c] = [0, 1, 2].map((k) => (n4[0][k] + n4[1][k] + n4[2][k] + n4[3][k]) / 4);
  }
  for (let r = 0; r < RR; r++) G[r][0][2] = 0;   // (the midline stays on the midline)
  const field = latticeField(G);
  // ---- the frame's mesh on the right half, by regions (their material by their cells)
  const V = G.map((_, r) => full[0].map((_, c) => r === 0 || r === RR - 1 || c === 0 || c >= 8 || F.isGuide(r, c)));
  const ROWm = { lipU: ROW["upper lip border"], mouth: ROW["upper lip inside"], lipL: ROW["lower lip inside"], eye: ROW["upper lid"] };
  const matOfCell = (cells) => {
    const kind = (r, c) => c < 3 && r === ROWm.mouth ? "mouth" : c < 3 && (r === ROWm.lipU || r === ROWm.lipL) ? "lip" : c >= 3 && c < 5 && r === ROWm.eye ? "eye" : "skin";
    const n = {}; for (const [r, c] of cells) { const k = kind(r, c); n[k] = (n[k] ?? 0) + 1; }
    return Object.entries(n).sort((a, b) => b[1] - a[1])[0][0];
  };
  const base = frameMesh(V, RR, RC, matOfCell);
  FRAME_DEBUG.last = { V, base };   // (for the checks: the frame's triangles in the domain)
  // ---- the detail: each triangle split in four, `levels` times, in the domain
  const det = P.detail ?? 1, levels = det < .75 ? 0 : det < 1.4 ? 1 : det < 1.9 ? 2 : 3;
  let tris = base;
  for (let i = 0; i < levels; i++) tris = tris.flatMap(({ pts: [a, b, c], mat }) => {
    const m = (p, q) => [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2], ab = m(a, b), bc = m(b, c), ca = m(c, a);
    return [[a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]].map((pts) => ({ pts, mat }));
  });
  // ---- a point of the skin: the field, its normal (across the domain), the fat pads out along it, the eye's white
  // set back behind the lids, the mouth's inside sunk the deeper the wider the lips are apart
  const rUp = ROW["upper lip inside"], rLo = ROW["lower lip inside"];
  const fat = (u, v) => A.chubby * PADS.reduce((s, d) => s + d.m * (A[d.k] ?? 1) * Math.exp(-(((u - d.u) / d.su) ** 2 + ((v - d.v) / d.sv) ** 2) / 2), 0);
  const nOf = (u, v) => {
    for (const e of [.02, .06, .15]) {
      const u0 = Math.max(0, u - e), u1 = Math.min(RC - 1, u + e), v0 = Math.max(0, v - e), v1 = Math.min(RR - 1, v + e);
      const du = sub(field(u1, v), field(u0, v)), dv = sub(field(u, v1), field(u, v0)), nn = cross(du, dv), l = Math.hypot(...nn);
      if (l > 1e-12) return nn.map((x) => x / l);
    }
    return [1, 0, 0];
  };
  const point = (u, v) => {
    let q = field(u, v);
    const nn = nOf(u, v), f = fat(u, v);
    q = [q[0] + nn[0] * f, q[1] + nn[1] * f, q[2] + nn[2] * f];
    if (v > ROW["upper lid"] && v < ROW["lower lid"] && u > 3 && u < 5) q[0] -= .0012;
    return { q, n: nn };
  };
  const pts = new Map(), ptOf = (u, v) => { const key = u.toFixed(6) + "," + v.toFixed(6); if (!pts.has(key)) pts.set(key, point(u, v)); return pts.get(key); };
  // ---- the materials: the regions', the hair above the hairline
  const skin = emitFor("skin"), hairE = Q.hair === "none" ? skin : emitFor("hair");
  const EM = { skin, lip: emitFor("lip"), mouth: emitFor("mouth"), eye: emitFor("eye") };
  const vid = new Map();
  const vert = (em, u, v, side) => {
    if (!vid.has(em)) vid.set(em, new Map());
    const m = vid.get(em), key = (side > 0 || u === 0 ? "" : "L") + u.toFixed(6) + "," + v.toFixed(6);   // (the midline's vertices shared by both halves)
    if (!m.has(key)) {
      const { q, n: nn } = ptOf(u, v);
      m.set(key, em.vert([q[0] * S, q[1] * S, q[2] * S * side], [nn[0], nn[1], nn[2] * side], [u / 22, q[1]]));
    }
    return m.get(key);
  };
  const inner = new Map(), innerVert = (u, v, side) => {
    const key = (side > 0 || u === 0 ? "" : "L") + u.toFixed(6) + "," + v.toFixed(6);
    if (!inner.has(key)) { const { q, n: nn } = ptOf(u, v), d = .0025; inner.set(key, EM.mouth.vert([(q[0] - nn[0] * d) * S, (q[1] - nn[1] * d) * S, (q[2] - nn[2] * d) * S * side], [-nn[0], -nn[1], -nn[2] * side], [0, 0])); }
    return inner.get(key);
  };
  // (the opening's rim -- the edges of the opening's own triangles that lie on the lips' inner rows: the lip's outer skin
  //  and its lining closed there by a strip, so no grazing view slips between them)
  const rimEdges = [];
  for (const { pts, mat } of tris) if (mat === "mouth") for (let k = 0; k < 3; k++) {
    const p0 = pts[k], p1 = pts[(k + 1) % 3];
    if (p0[1] === p1[1] && (p0[1] === ROW["upper lip inside"] || p0[1] === ROW["lower lip inside"])) rimEdges.push([p0, p1]);
  }
  for (const side of [1, -1]) for (const [p0, p1] of rimEdges) {
    const o0 = vert(EM.mouth, p0[0], p0[1], side), o1 = vert(EM.mouth, p1[0], p1[1], side), i0 = innerVert(p0[0], p0[1], side), i1 = innerVert(p1[0], p1[1], side);
    EM.mouth.quad(o0, o1, i1, i0); EM.mouth.quad(o0, i0, i1, o1);
  }
  for (const side of [1, -1]) for (const { pts: [a, b, c], mat } of tris) {
    if (mat === "mouth") continue;   // (the opening between the lips: seen through, to the teeth and the mouth's back wall below)
    let em = EM[mat];
    if (mat === "skin" && hairE !== skin) {
      const qa = ptOf(...a).q, qb = ptOf(...b).q, qc = ptOf(...c).q, yMid = (qa[1] + qb[1] + qc[1]) / 3, z = Math.abs((qa[2] + qb[2] + qc[2]) / 3), x = (qa[0] + qb[0] + qc[0]) / 3;
      const back = Math.min(1, Math.atan2(z, x) / Math.PI);
      if (yMid >= Q.hairline - .12 * Math.pow(back, 2.5) && yMid < Q.bare) em = hairE;
    }
    // (the nape's column is the back's midline: shared by both halves too)
    const V3 = (pt) => vert(em, pt[0], pt[1], pt[0] === RC - 1 ? 1 : side);
    if (side > 0) em.tri(V3(a), V3(b), V3(c)); else em.tri(V3(a), V3(c), V3(b));
    // the INSIDE of the lips and cheeks round the mouth: the same skin turned inward, a little within, in the mouth's
    // dark -- what is seen past the mouth's back wall, between parted lips, is the inside of the cheek
    if ((mat === "lip" || mat === "skin") && [a, b, c].every((q) => q[0] <= 5.5 && q[1] >= ROW["subnasale"] && q[1] <= ROW["pogonion"])) {
      const Vi = (pt) => innerVert(pt[0], pt[1], side);
      if (side > 0) EM.mouth.tri(Vi(a), Vi(c), Vi(b)); else EM.mouth.tri(Vi(a), Vi(b), Vi(c));
    }
  }
  // ---- the crown: a fan from the top row to the vertex; the neck: a tube down from the bottom row
  const edgeRow = (v) => {   // the domain's top or bottom line, right round: (u, side) in order
    const us = [...new Set(tris.flatMap((t) => t.pts.filter((q) => q[1] === v).map((q) => q[0])))].sort((a, b) => a - b);
    return [...us.map((u) => [u, 1]), ...us.slice(1, -1).reverse().map((u) => [u, -1])];
  };
  const topR = edgeRow(0), crownEm = yTop >= Q.bare ? skin : hairE;
  const vtop = crownEm.vert([0, yTop * S, 0], [0, 1, 0], [0, yTop]);
  topR.forEach(([u, sd], i) => { const [u2, sd2] = topR[(i + 1) % topR.length]; crownEm.tri(vtop, vert(crownEm, u2, 0, u2 === RC - 1 ? 1 : sd2), vert(crownEm, u, 0, u === RC - 1 ? 1 : sd)); });
  const botR = edgeRow(RR - 1), neckL = Q.neckL ?? .07;
  const ringPts = botR.map(([u, sd]) => { const q = ptOf(u, RR - 1).q; return [q[0], q[1], q[2] * sd]; });
  const yLow = Math.min(...ringPts.map((q) => q[1])) - neckL;
  const nTop = botR.map(([u, sd]) => vert(skin, u, RR - 1, u === RC - 1 ? 1 : sd)), nBot = ringPts.map((q) => skin.vert([q[0] * S, yLow * S, q[2] * S], norm([q[0] - F.ncx, 0, q[2]]), [0, yLow]));
  for (let i = 0; i < nTop.length; i++) { const j = (i + 1) % nTop.length; skin.quad(nTop[i], nTop[j], nBot[j], nBot[i]); }
  // ---- the eyes: the iris and the pupil, discs facing forward on the eye's white, CUT BY THE LIDS (a falling lid
  // covers them, a blink hides them)
  const irisE = emitFor("iris"), pupilE = emitFor("pupil");
  const lid = (v) => Array.from({ length: 25 }, (_, i) => ptOf(3 + 2 * i / 24, v).q);
  const yOnLine = (line, z) => { for (let i = 1; i < line.length; i++) { const a = line[i - 1], b = line[i]; if ((z - a[2]) * (z - b[2]) <= 0) { const t = (z - a[2]) / ((b[2] - a[2]) || 1); return a[1] + (b[1] - a[1]) * t; } } return null; };
  const up = lid(ROW["upper lid"]), dn = lid(ROW["lower lid"]);
  for (const side of [1, -1]) {
    const m = F.lm.mid;
    // (in front of the white wherever it is -- the field's, or at the lowest detail the flat triangles between the lids)
    const front = Math.max(m[0], ...[0, .25, .5, .75, 1].map((t) => ptOf(4, ROW["upper lid"] + t).q[0]), up[12][0], dn[12][0]);
    const disc = (em, r, k, dy = 0, dz = 0) => {
      const ctr = [front + .0006 + k, m[1] + dy, m[2] + dz], ring = [];
      for (let i = 0; i < 16; i++) {
        const a = i / 16 * Math.PI * 2, z = ctr[2] + r * Math.cos(a), yu = yOnLine(up, z), yd = yOnLine(dn, z);
        ring.push([ctr[0], yu === null || yd === null ? ctr[1] : Math.max(yd + .0003, Math.min(yu - .0003, ctr[1] + r * Math.sin(a))), z]);
      }
      const ys = ring.map((q) => q[1]);
      if (Math.max(...ys) - Math.min(...ys) < .0006) return;   // (the lids closed over it)
      const cy = (Math.max(...ys) + Math.min(...ys)) / 2, vc = em.vert([ctr[0] * S, cy * S, ctr[2] * S * side], [1, 0, 0], [0, 0]);
      const vr = ring.map((q) => em.vert([q[0] * S, q[1] * S, q[2] * S * side], [1, 0, 0], [0, 0]));
      for (let i = 0; i < 16; i++) side > 0 ? em.tri(vc, vr[i], vr[(i + 1) % 16]) : em.tri(vc, vr[(i + 1) % 16], vr[i]);
    };
    // (a LIVING eye: the limbal ring -- the iris's dark rim -- the iris, the pupil, and a CATCHLIGHT, the window of the
    //  sky caught on the wet cornea, up and toward the outer corner; the lids cut them all)
    disc(emitFor("limbus"), A.irisR * 1.1, -.0002); disc(irisE, A.irisR * .9, 0); disc(pupilE, A.irisR * .42, .0003);
    disc(emitFor("glint"), A.irisR * .2, .0006, A.irisR * .38, A.irisR * .3);
  }
  // ---- the LASH LINE: a dark strip along the upper lid from the inner corner to past the outer, its lower edge on the
  // lid's edge -- the shadow the lid casts on the eye's white, and the lashes' line; with the lid it falls in a blink
  const lashE = emitFor("lash"), NL = 12;
  for (const side of [1, -1]) {
    const vt = [], vb = [];
    for (let i = 0; i <= NL; i++) {
      const t = i / NL, { q, n: nn } = ptOf(3 + 2 * t, ROW["upper lid"]), w = A.lashThickness * (.35 + .65 * Math.sin(Math.PI * Math.min(1, t * 1.15)));
      const o = [q[0] + nn[0] * .0007, q[1] + nn[1] * .0007, q[2] + nn[2] * .0007], nS = [nn[0], nn[1], nn[2] * side];
      vt.push(lashE.vert([o[0] * S, (o[1] + w * .6) * S, o[2] * S * side], nS, [t, 1]));
      vb.push(lashE.vert([(o[0] + .0004) * S, (o[1] - w * .4) * S, o[2] * S * side], nS, [t, 0]));
    }
    for (let i = 1; i <= NL; i++) side > 0 ? lashE.quad(vb[i - 1], vb[i], vt[i], vt[i - 1]) : lashE.quad(vb[i], vb[i - 1], vt[i - 1], vt[i]);
  }
  // ---- the eyebrows: a strip of hair along the BROW line from its head to its tail -- wherever the eye under it puts it
  const browE = emitFor("brow"), NB = 4 * 2 ** levels + 1;
  for (const side of [1, -1]) {
    const vt = [], vb = [];
    for (let i = 0; i < NB; i++) {
      const t = i / (NB - 1), u = 3 + 2 * t, { q, n: nn } = ptOf(u, ROW["brow"]);
      // (its "up": the world's, laid in the skin's plane -- not the rows', which cross when the brow is drawn down)
      const upv = norm([-nn[0] * nn[1], 1 - nn[1] * nn[1], -nn[2] * nn[1]]), h = A.browThickness * (1 - .55 * t) * (1 + .3 * Math.sin(Math.PI * t)), lift = .0012;
      const o = [q[0] + nn[0] * lift, q[1] + nn[1] * lift, q[2] + nn[2] * lift], nS = [nn[0], nn[1], nn[2] * side];
      vt.push(browE.vert([(o[0] + upv[0] * h * .55) * S, (o[1] + upv[1] * h * .55) * S, (o[2] + upv[2] * h * .55) * S * side], nS, [t, 1]));
      vb.push(browE.vert([(o[0] - upv[0] * h * .45) * S, (o[1] - upv[1] * h * .45) * S, (o[2] - upv[2] * h * .45) * S * side], nS, [t, 0]));
    }
    for (let i = 1; i < NB; i++) side > 0 ? browE.quad(vb[i - 1], vb[i], vt[i], vt[i - 1]) : browE.quad(vb[i], vb[i - 1], vt[i - 1], vt[i]);
  }
  // ---- the TEETH: an upper and a lower arch behind the lips, along the mouth's curve -- the upper hanging from behind
  // the upper lip to the stomion, the lower rising to meet it and turning with the jaw; closed lips hide them, open
  // lips show them before the mouth's dark inside (which falls back further)
  if (A.teeth) {
    const teeth = emitFor("teeth"), lmS = F.lm.sto, T = A.teethWidth / 2, depth = A.teethDepth, front = lmS[0] - A.teethSet;
    const NT = 12 * 2 ** Math.min(levels, 1);   // (columns across the arch: a tooth a column, its edge scalloped)
    const arch = (t, back = 0) => [front - back - depth * t * t, lmS[1], T * t];   // (t -1..1 across: the front middle, curving back each side)
    const band = (y0, y1, turnIt, sgn, back = 0) => {
      const top = [], bot = [];
      for (let i = 0; i <= NT; i++) {
        const t = -1 + 2 * i / NT, a = arch(t, back), tooth = Math.abs(Math.sin(Math.PI * i / 2)), edge = y1 + sgn * .0004 * (1 - tooth);   // (the incisal edge dips between teeth)
        let p0 = [a[0], y0, a[2]], p1 = [a[0], edge, a[2]];
        if (turnIt && F.jaw.th) { p0 = F.jaw.turn(p0, F.jaw.th); p1 = F.jaw.turn(p1, F.jaw.th); }
        const nn = norm([1 + 0 * t, 0, t * T / Math.max(.001, depth) * .5]);   // (the arch's own normal: out of the curve)
        top.push(teeth.vert(p0.map((v) => v * S), nn, [t, 0])); bot.push(teeth.vert(p1.map((v) => v * S), nn, [t, 1]));
      }
      for (let i = 0; i < NT; i++) { teeth.quad(top[i], top[i + 1], bot[i + 1], bot[i]); teeth.quad(top[i], bot[i], bot[i + 1], top[i + 1]); }   // (both faces: the arch is a thin band)
    };
    // (the upper incisors' edges a little BELOW the lips' line -- they show as soon as the lips part; the lower arch
    //  behind and under them, its edges just above theirs: closed, it overlaps them, hidden; open, the jaw takes it down)
    band(lmS[1] + A.teethHeight * .8, lmS[1] - .0025, false, 1);
    band(lmS[1] - A.teethHeight, lmS[1] - .0015, true, -1, .0018);
  }
  // ---- the MOUTH'S BACK: a dark wall behind the teeth across the whole opening (from above the upper teeth to below
  // the lower lip as the jaw has it), so whatever is seen between parted lips is the teeth or the mouth's dark, never
  // the inside of the head
  {
    const mouthE = emitFor("mouth"), lo = ptOf(1.5, ROW["lower lip inside"]).q, cx = F.lm.sto[0] - A.teethSet - A.teethDepth - .004;
    const yTop = F.lm.sto[1] + A.teethHeight + .004, yBot = Math.min(lo[1], F.lm.sto[1]) - A.teethHeight - .006, zW = A.mouthWidth / 2 + .008;   // (wider than the mouth, curving back: its sides end deep inside the cheeks)
    const cyM = (yTop + yBot) / 2, ry = (yTop - yBot) / 2, NM = 20, c0 = mouthE.vert([cx * S, cyM * S, 0], [1, 0, 0], [0, 0]);
    const ringM = Array.from({ length: NM }, (_, i) => { const a = i / NM * Math.PI * 2; const sq = (x) => Math.sign(x) * Math.abs(x) ** .45, ca = sq(Math.cos(a)), sa = sq(Math.sin(a));   // (a squarer outline: it fills the opening's corners)
      return mouthE.vert([(cx - 2 * A.teethDepth * ca * ca - .016 * ca * ca * sa * sa - .004 * (1 - Math.abs(ca))) * S,   // (the corners back the furthest: inside the cheeks and the chin)
        (cyM + ry * sa) * S, zW * ca * S], [1, 0, 0], [0, 0]); });
    for (let i = 0; i < NM; i++) { mouthE.tri(c0, ringM[i], ringM[(i + 1) % NM]); mouthE.tri(c0, ringM[(i + 1) % NM], ringM[i]); }
  }
  // ---- the ears: the helix's outline as a plate standing off the head, turned out and back
  const EF = earFrame(H);
  for (const sg of [1, -1]) {
    const e = EF.e * S, cx = EF.c[0] * S, cy = EF.c[1] * S, cz = EF.c[2] * S * sg;
    const outline = [[.012, .030], [.004, .034], [-.006, .032], [-.014, .024], [-.018, .010], [-.017, -.006], [-.012, -.022], [-.004, -.032], [.004, -.031], [.010, -.022], [.013, -.008], [.011, .006], [.004, .014], [-.002, .016], [-.006, .010], [-.004, -.004], [.002, -.012], [.007, -.004], [.007, .010], [.010, .020]];
    prims.plate(P.earDebug ? "lip" : "skin", outline.map(([x, y]) => [x * e, y * e]), .004 * e, [cx, cy, cz], sg, Q.earOut, Q.earBack);
  }
  // ---- the GUIDE LINES, for the viewer: each guide span along the skin (only the face's guides, not the skull's frame)
  if (prims.guide) {
    const sc = (q, side) => [q[0] * S, q[1] * S, q[2] * S * side], N = 2 ** Math.max(levels, 2);
    for (const side of [1, -1]) {
      for (let r = 0; r < RR; r++) for (let c = 0; c < 7; c++) if (F.isGuide(r, c) && F.isGuide(r, c + 1))
        prims.guide(Array.from({ length: N + 1 }, (_, i) => sc(ptOf(c + i / N, r).q, side)), FACE_ROWS[r]);
      for (let c = 0; c < 8; c++) for (let r = 0; r < RR - 1; r++) if (F.isGuide(r, c) && F.isGuide(r + 1, c))
        prims.guide(Array.from({ length: N + 1 }, (_, i) => sc(ptOf(c, r + i / N).q, side)), FACE_COLUMNS[c]);
    }
  }
  return { top: yTop * S, bottom: yLow * S, landmarks: F.lm, triangles: tris.length * 2 };
}
