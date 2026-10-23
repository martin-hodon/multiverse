// MURALS (2026-10-05; docs/murals.md): Egyptian tomb paintings -- a figure is built from the CANON (heights in squares
// of the grid: the hairline at 18, the neck at 16, the knee at 6) and a POSE, its body drawn in composite view (the
// head in profile with a frontal eye, the shoulders frontal, the legs in profile) as tapering limbs between joints,
// then dressed, crowned and given what it holds from the parts (assets/murals/parts.json, the hieroglyphs' language:
// glyphs.js draws them, in the painter's colours); a painting sets figures in registers with an offering table,
// columns of hieroglyphs (glyphs.js renderTexture), a frieze, a dado and a border. Every figure is built facing left
// and mirrored to face right. Units: figure units, a square of the canon is 10; y up, 0 the ground.
import { registerGlyphs, drawGlyphLayers, glyphColour, renderTexture } from "./glyphs.js";
import { LAYER_KINDS } from "./patterns.js";

const FIGURES = new Map(), PAINTINGS = new Map();
const cache = new Map();
export function registerMurals(docs) {
  for (const d of Object.values(docs)) {
    if (d?.parts) registerGlyphs({ "murals/parts": d });
    for (const [k, v] of Object.entries(d?.figures ?? {})) FIGURES.set(k, v);
    for (const [k, v] of Object.entries(d?.paintings ?? {})) PAINTINGS.set(k, v);
  }
  cache.clear();
}
export const figureNames = () => [...FIGURES.keys()];
export const paintingNames = () => [...PAINTINGS.keys()];

const C = 1;   // a corner
const S = (points, fill, k = {}) => ({ shape: "spline", points, fill, ...k });
const P = (part, at, k = {}) => ({ part, at, ...k });

// a TAPERING LIMB: a smooth outline round a line of joints, each its own width -- a thigh into a knee into a calf into an
// ankle, an upper arm into a forearm -- one closed shape, filled and outlined
function tube(pts, widths, fill) {
  const n = pts.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l, w = widths[i] / 2;
    L.push([pts[i][0] + nx * w, pts[i][1] + ny * w]); R.push([pts[i][0] - nx * w, pts[i][1] - ny * w]);
  }
  const e0 = pts[0], e1 = pts[n - 1], d0 = [pts[0][0] - pts[1][0], pts[0][1] - pts[1][1]], d1 = [pts[n - 1][0] - pts[n - 2][0], pts[n - 1][1] - pts[n - 2][1]];
  const nd = (d, k) => { const l = Math.hypot(...d) || 1; return [d[0] / l * k, d[1] / l * k]; };
  const cap0 = nd(d0, widths[0] * .35), cap1 = nd(d1, widths[n - 1] * .3);
  return S([[e0[0] + cap0[0], e0[1] + cap0[1]], ...L, [e1[0] + cap1[0], e1[1] + cap1[1]], ...R.reverse()], fill);
}

// ---- THE CANON: a man's and a woman's contours, in figure units (a square is 10) ------------------------------------
export const CANON = {
  hairline: 180, neck: 160, shoulder: 152, armpit: 142, elbow: 118, waist: 110, hip: 96, crotch: 92, knee: 60, ankle: 10,
  man: {
    torso: [[-5, 161], [-22, 159, C], [-23, 153], [-21, 146], [-22.4, 139], [-20.4, 132], [-17, 122], [-15, 110], [-16.4, 100], [-14, 91, C], [14, 91, C], [17, 100], [15, 110], [13, 120], [16, 132], [19.4, 146], [22, 153], [22, 159, C], [5, 161]],
    sh: 19, arm: [9.6, 8, 6.2], leg: [17, 10, 11, 6.6],
  },
  woman: {
    torso: [[-5, 161], [-19, 159, C], [-19.6, 153], [-17.4, 146], [-18.6, 140], [-21.6, 134], [-19, 129.6], [-13.4, 124], [-12, 112], [-13.6, 100], [-12, 91, C], [12, 91, C], [13.6, 100], [11.6, 112], [10.6, 122], [13.6, 134], [16.6, 146], [19, 153], [19, 159, C], [5, 161]],
    sh: 16.5, arm: [8.2, 6.8, 5.4], leg: [14, 8.6, 9.6, 6],
  },
};
// the legs by pose: [hip, knee, calf, ankle] for the front (far, advanced) leg and the back one, and where each foot stands
const LEGS = {
  stride: { front: [[-7, 94], [-21, 60], [-24.4, 38], [-30, 10]], back: [[7, 94], [7, 60], [8, 38], [10, 10]], feet: [-29, 11] },
  stand: { front: [[-5, 94], [-6, 60], [-6.4, 38], [-6, 10]], back: [[5, 94], [4, 60], [4.4, 38], [3, 10]], feet: [-5, 4] },
  sit: { front: [[-2, 56], [-38, 56], [-40, 36], [-41, 10]], back: [[6, 56], [-34, 58], [-36, 36], [-37, 10]], feet: [-40, -36], dy: -38 },
};
// the arms: elbow and wrist for each gesture (the front arm's, the back arm's), the hand, and what the hand does
const ARMS = {
  front: {
    hang: { e: [-20, 118], w: [-21, 93], hand: "m-fist" },
    staff: { e: [-34, 124], w: [-48, 118], hand: "m-fist", staff: "staff" },
    sceptre: { e: [-34, 124], w: [-48, 118], hand: "m-fist", staff: "was" },
    offer: { e: [-38, 136], w: [-56, 144], hand: "m-hand-open", palm: true },
    adore: { e: [-34, 152], w: [-44, 172], hand: "m-hand-open" },
    lotus: { e: [-32, 128], w: [-40, 146], hand: "m-fist", palm: true },
  },
  back: {
    hang: { e: [22, 118], w: [21, 93], hand: "m-fist" },
    ankh: { e: [22, 118], w: [21, 93], hand: "m-fist", grip: "m-ankh" },
    offer: { e: [-2, 120], w: [-32, 124], hand: "m-hand-open", over: true },
    adore: { e: [-6, 148], w: [-24, 168], hand: "m-hand-open", over: true },
  },
};
const rotOf = (a, b) => Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI - 180;   // (a part drawn along -x, turned to point from a to b)
const sh = (p, dy) => [p[0], p[1] + dy];

// ---- A FIGURE: its layers, back to front, from its description (assets/murals/figures.json or written out) ------------
export function figureLayers(spec0) {
  const spec = typeof spec0 === "string" ? FIGURES.get(spec0) : spec0;
  if (!spec) throw new Error(`no mural figure "${spec0}"`);
  const woman = spec.kind === "woman", K = woman ? CANON.woman : CANON.man, pose = spec.pose ?? (woman ? "stand" : "stride");
  const mummy = pose === "mummy" || pose === "mummy-seated", seated = pose === "sit" || pose === "mummy-seated";
  const legs = LEGS[seated ? "sit" : pose === "stride" ? "stride" : "stand"], dy = seated ? legs.dy : 0;
  const out = [], behind = [], front = [];
  const [armF, armB] = spec.arms ?? ["hang", "hang"];
  const Sf = [-K.sh, CANON.shoulder + dy], Sb = [K.sh, CANON.shoulder + dy];
  if (seated) out.push(P("m-throne", [-10, 0]));   // (the block under the seated body, the dais under its feet)
  // the arms: the back arm behind the body unless it crosses in front (offering, adoring with both hands)
  const arm = (side, kind) => {
    const A = ARMS[side][kind];
    if (!A) return null;
    const S0 = side === "front" ? Sf : Sb, e = sh(A.e, dy), w = sh(A.w, dy), L = [];
    L.push(tube([S0, e, w], K.arm, "skin"));
    L.push(P(A.hand, w, { rot: rotOf(e, w) }));
    if (A.staff) {   // a staff or the was sceptre, upright in the fist: from the ground to over the head
      const x = w[0] - 6;
      L.unshift({ shape: "limb", points: [[x, 3], [x, 186 + dy]], w: 2.2, fill: "staff" });
      if (A.staff === "was") L.unshift(P("m-was-head", [x, 186 + dy]), P("m-was-fork", [x, 3]));
    }
    if (A.grip) { const r = rotOf(e, w) * Math.PI / 180; L.push(P(A.grip, [w[0] - 6 * Math.cos(r), w[1] - 6 * Math.sin(r)])); }   // (the fist's grip, (-6, 0) in the hand's frame)
    const held = spec.holds?.[side];
    if (held && A.palm) L.push(P(held, [w[0] - 7, w[1] + 2.6]));
    else if (held) L.push(P(held, [w[0] - 6, w[1]]));
    return { L, over: !!A.over };
  };
  const aB = armB ? arm("back", armB) : null, aF = armF ? arm("front", armF) : null;
  if (aB && !aB.over) behind.push(...aB.L);
  out.push(...behind);
  // the legs (unless wrapped), the torso, the garments
  const skinLegs = !mummy;
  if (skinLegs) {
    out.push(tube(legs.front, K.leg, "skin"), P("m-foot", [legs.feet[0], 0]));
    out.push(tube(legs.back, K.leg, "skin"), P("m-foot", [legs.feet[1], 0]));
  }
  if (mummy) {   // the shroud: shoulders to feet (or, enthroned, down over the lap and the shins)
    out.push(seated
      ? S([[-5, 161 + dy], [-18, 158 + dy, C], [-19, 140 + dy], [-17, 110 + dy], [-16, 62], [-42, 60, C], [-44, 6], [-46, 2, C], [-32, 2, C], [-30, 14], [-28, 46], [12, 48], [16, 80], [18, 120 + dy], [18, 158 + dy, C], [5, 161 + dy]], "shroud")
      : S([[-5, 161], [-18, 158, C], [-19, 140], [-17, 110], [-14, 60], [-11, 14], [-12, 6, C], [12, 6, C], [10, 14], [14, 60], [16, 110], [18, 140], [18, 158, C], [5, 161]], "shroud"));
    if (!seated) out.push({ shape: "rect", w: 30, h: 6, at: [0, 3], fill: "plinth" });
  } else out.push(S(K.torso.map((p) => [p[0], p[1] + dy, p[2] ?? 0].slice(0, p[2] ? 3 : 2)), "skin"));
  const g = spec.garment;
  if (g === "kilt" || g === "royal-kilt") {
    const strid = pose === "stride";
    out.push(S(strid ? [[-16, 112 + dy, C], [16, 112 + dy, C], [17.4, 98 + dy], [15.6, 64, C], [-8, 63], [-28, 62, C], [-24, 80], [-18, 98]] : [[-16, 112 + dy, C], [16, 112 + dy, C], [17, 98], [15, 64, C], [-15, 64, C], [-17, 98]], "kilt"));
    if (g === "royal-kilt") {
      out.push({ shape: "points", points: [[-12, 108 + dy], [-2, 108 + dy], [-4, 64], [-16, 64]], fill: "apron" });
      for (const x of [-10, -7, -4]) out.push({ shape: "line", from: [x, 106 + dy], to: [x - 3, 66], stroke: "line", line: .5 });
    } else for (const x of [-12, -6, 0, 6]) out.push({ shape: "line", from: [x, 106 + dy], to: [x - (strid ? 7 : 1), 66], stroke: "line", line: .35 });
    out.push({ shape: "rect", w: 33, h: 4.4, at: [0, 109 + dy], fill: "belt" });
    if (spec.tail) out.push({ shape: "limb", points: [[15, 104], [19, 80], [21, 56]], w: 2.4, fill: "tail" });
  }
  if (g === "dress") {
    out.push({ ...S([[-17.6, 134, C], [-13, 112], [-14, 96], [-12, 60], [-10.6, 12, C], [10.6, 12, C], [12, 60], [13.4, 96], [12, 112], [14, 134, C]], "dress"), alpha: spec.sheer ?? .92 });
    out.push({ shape: "line", from: [-14, 135], to: [-9, 158], stroke: "dress", line: 2 }, { shape: "line", from: [12, 135], to: [8, 158], stroke: "dress", line: 2 });
  }
  if (spec.collar) out.push(P("m-collar", [-1, 160 + dy]));
  // the head, and what it wears
  const H = [-2, 160 + dy];
  out.push({ shape: "rect", w: 12, h: 3, at: [-.5, 160 + dy], fill: "skin", outline: false });   // (where the neck runs into the shoulders: no seam)
  const animal = ["falcon", "jackal", "ibis", "ram", "lion"].includes(spec.head);
  if (animal && spec.wig) out.push(P(spec.wig, H));
  out.push(P(spec.head === "woman" ? "m-head-woman" : animal ? "m-head-" + spec.head : "m-head", H));
  if (!animal && spec.wig) out.push(P(spec.wig, H));
  if (spec.beard) out.push(P(spec.beard === "royal" ? "m-beard-royal" : "m-beard-god", H));
  if (spec.crown) out.push(P(spec.crown, H));
  if (aB?.over) out.push(...aB.L);   // (an arm crossing the chest lies over the collar and the face, never under them)
  // the front arm last, before everything (and the fists' crook and flail, held at an enthroned god's chest)
  if (armF === "crook" || armF === "sceptre-chest") {
    out.push(P("m-fist", [-14, 138 + dy], { rot: 90 }), P("m-fist", [-8, 132 + dy], { rot: 90 }));
    if (armF === "crook") out.push(P("m-crook", [-20, 138 + dy]), P("m-flail", [-10, 132 + dy]));
    else out.push({ shape: "limb", points: [[-24, 3], [-24, 186]], w: 2.4, fill: "staff" }, P("m-was-head", [-24, 186]), P("m-was-fork", [-24, 3]));
  } else if (aF) out.push(...aF.L);
  // the colours: the figure's roles
  const colors = { skin: spec.skin ?? (woman ? "skin-woman" : "skin"), wig: spec.wigColor ?? "black", kilt: spec.kiltColor ?? "white", belt: spec.belt ?? "red",
    apron: spec.apron ?? "gold", tail: "brown", dress: spec.dressColor ?? "white", shroud: spec.shroud ?? "white", plinth: "yellow-dark", staff: spec.staffColor ?? "gold",
    eye: "white", brow: "black" };
  return { layers: out, colors, height: seated ? 210 : 240 };
}

// a figure on a canvas: its feet's middle at (x, y) px, `scale` px per figure unit, facing left or right
export function drawFigure(g, spec, { x, y, scale = 1, face = "left", mode = null }) {
  const f = figureLayers(spec);
  drawGlyphLayers(g, f.layers, { x, y, scale, flip: face === "right", colors: f.colors, outline: 1, mode, where: typeof spec === "string" ? spec : "figure" });
}

// ---- A PAINTING ----------------------------------------------------------------------------------------------------------
const mkCanvas = (w, h) => typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(w, h) : Object.assign(document.createElement("canvas"), { width: w, height: h });
export function renderPainting(ref, { px = 1024, seed = 0 } = {}) {
  const D = typeof ref === "string" ? PAINTINGS.get(ref) : ref;
  if (!D) throw new Error(`no mural "${ref}"`);
  const [W, Hh] = D.size ?? [600, 300], k = px / W, cv = mkCanvas(Math.round(W * k), Math.round(Hh * k));
  const g = cv.getContext("2d", { willReadFrequently: true }), col = (c) => glyphColour(c);
  g.fillStyle = col(D.ground ?? "limestone"); g.fillRect(0, 0, cv.width, cv.height);
  const bw = D.border ? 8 : 0, U = (v) => v * k;
  let top = bw, bottom = Hh - bw;
  // the frieze above, the dado below
  if (D.frieze === "kheker") {
    const h = 24;
    for (let x = bw + 5; x < W - bw; x += 8) drawGlyphLayers(g, [{ part: "m-kheker" }], { x: U(x), y: U(top + h), scale: k, where: "kheker" });
    top += h + 2;
  } else if (D.frieze === "sky") {
    const h = 16; g.fillStyle = col("blue"); g.fillRect(U(bw), U(top), U(W - 2 * bw), U(h));
    g.fillStyle = col("yellow");
    for (let x = bw + 10; x < W - bw - 6; x += 16) { const cx = U(x), cy = U(top + h / 2), r = U(4.4); g.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .4 : r; g.lineTo(cx + rr * Math.cos(a), cy + rr * Math.sin(a)); } g.closePath(); g.fill(); }
    top += h + 2;
  }
  if (D.dado) {
    const h = 26;
    for (const [y0, hh, c] of [[0, 4, "blue"], [4, 2, "black"], [6, 4, "red"], [10, 2, "black"], [12, 14, "yellow-dark"]]) { g.fillStyle = col(c); g.fillRect(U(bw), U(bottom - h + y0), U(W - 2 * bw), U(hh)); }
    bottom -= h;
  }
  // the registers, top to bottom, each on its ground line
  let y = top;
  for (const R of D.registers ?? []) {
    const h = R.h ?? (bottom - top), ground = Math.min(bottom, y + h);
    g.fillStyle = col("blue"); g.fillRect(U(bw), U(ground - 2.4), U(W - 2 * bw), U(2.4));
    const gl = ground - 2.4;
    for (const it of R.items ?? []) {
      if (it.text) {
        const T = it.text, cell = Math.min(it.w / (T.cols ?? 4), it.h / (T.rows ?? 4));
        const tex = renderTexture(T, { seed: (T.seed ?? 1) + seed, cell: Math.max(4, U(cell)) });
        g.drawImage(tex, U(it.x), U(gl - it.y - it.h + (it.h - cell * (T.rows ?? 4))), tex.width, tex.height);
      } else if (it.table) drawGlyphLayers(g, [{ part: "m-offering-table" }], { x: U(it.x), y: U(gl), scale: k * 1.7 * (it.scale ?? 1), where: "table" });   // (waist-high to a figure)
      else if (it.figure) drawFigure(g, it.figure, { x: U(it.x), y: U(gl), scale: k * (it.scale ?? 1), face: it.face ?? "left", mode: it.mode ?? D.mode ?? null });
    }
    y = ground;
  }
  // the border: coloured blocks round it, black between
  if (bw) {
    const cs = ["blue", "red", "green", "yellow"].map(col);
    g.fillStyle = col("black"); g.fillRect(0, 0, cv.width, U(bw)); g.fillRect(0, U(Hh - bw), cv.width, U(bw)); g.fillRect(0, 0, U(bw), cv.height); g.fillRect(U(W - bw), 0, U(bw), cv.height);
    let i = 0;
    const blk = (x, y, w, h) => { g.fillStyle = cs[i++ % 4]; g.fillRect(U(x) + 1, U(y) + 1, U(w) - 2, U(h) - 2); };
    for (let x = 0; x < W; x += 16) { blk(x, 0, Math.min(16, W - x), bw); blk(x, Hh - bw, Math.min(16, W - x), bw); }
    for (let yy = bw; yy < Hh - bw; yy += 16) { blk(0, yy, bw, Math.min(16, Hh - bw - yy)); blk(W - bw, yy, bw, Math.min(16, Hh - bw - yy)); }
  }
  return cv;
}

// ---- the viewer's sheets: the figures each in a cell, or the paintings whole ----------------------------------------------
export function drawMuralSheet(cv, doc, { cell = 220 } = {}) {
  const g = cv.getContext("2d", { willReadFrequently: true }), errs = [];
  g.font = "12px ui-monospace, monospace";
  if (doc.figures) {
    const list = Object.entries(doc.figures), cols = Math.max(1, Math.floor((cv.width - 10) / (cell + 12))), rowH = cell * 1.25 + 30;
    cv.height = Math.max(cv.height, Math.ceil(list.length / cols) * rowH + 10);
    g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height);
    list.forEach(([k, f], i) => {
      const x = 10 + (i % cols) * (cell + 12), y = 10 + Math.floor(i / cols) * rowH;
      g.fillStyle = glyphColour("limestone"); g.fillRect(x, y, cell, cell * 1.25);
      try { drawFigure(g, f, { x: x + cell * .55, y: y + cell * 1.22, scale: cell * 1.18 / 260, face: "left" }); } catch (e) { errs.push(`${k}: ${e.message}`); }
      g.fillStyle = "#d8d4cc"; g.fillText(f.name ?? k, x, y + cell * 1.25 + 16);
    });
    return errs;
  }
  const list = Object.entries(doc.paintings ?? {});
  let y = 10;
  const draws = list.map(([k, P]) => { try { return [k, P, renderPainting(P, { px: cv.width - 20 })]; } catch (e) { errs.push(`${k}: ${e.message}`); return [k, P, null]; } });
  cv.height = Math.max(cv.height, draws.reduce((a, [, , c]) => a + (c ? c.height : 20) + 30, 20));
  g.fillStyle = "#1b1d21"; g.fillRect(0, 0, cv.width, cv.height);
  for (const [k, P, c] of draws) { g.fillStyle = "#d8d4cc"; g.fillText(P.name ?? k, 10, y + 12); if (c) { g.drawImage(c, 10, y + 18); y += c.height + 30; } else y += 30; }
  return errs;
}

// ---- on a building: a pattern layer { kind: "mural", painting: name | { ...a painting }, size } -------------------------
LAYER_KINDS.mural = {
  draw(g, L, { tile, ppm }) {
    const [w, h] = Array.isArray(L.size) ? L.size : tile, px = Math.max(16, Math.round(w * ppm));
    const key = `${JSON.stringify(L.painting)}|${px}|${L.seed ?? 0}`;
    if (!cache.has(key)) cache.set(key, renderPainting(L.painting, { px, seed: L.seed ?? 0 }));
    const cv = cache.get(key);
    g.save(); g.scale(1, -1); g.drawImage(cv, -w / 2, -h / 2, w, h); g.restore();
  },
  deps: (L) => ({ painting: typeof L.painting === "string" ? PAINTINGS.get(L.painting) ?? null : L.painting, figures: Object.fromEntries(FIGURES) }),
};
