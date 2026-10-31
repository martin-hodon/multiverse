// GREEK PAINTINGS, the techniques (docs/greek.md): one way to draw pieces (figure.js), every technique only data. A piece is
// STROKED round its outline and then FILLED, so only the outer half of the line stays and it stays only where the piece
// overlaps something: a black-figure painter's incision (the stroke cuts the layer, the clay shows through) and a
// red-figure painter's relief line (the stroke is black, the fill reserved clay) are the same step. Line classes drop out as
// a figure gets too small for them; the ground goes in last, behind everything.

export const TECHNIQUES = {
  // ink: fired black; clay: the pot's orange; roles a piece's fill, lines by class { c: colour | "cut", w: width in figure units, a: alpha }
  "black-figure": { cloths: ["#17110e", "#7c2b21", "#17110e", "#7c2b21"], ground: "#c9733f", contour: { c: "cut", w: .82 }, roles: { flame: "#7c2b21", skin: "#17110e", skinF: "#ece3cf", hair: "#17110e", beard: "#17110e", cloth: "#17110e", cloth2: "#7c2b21", metal: "#17110e", crest: "#7c2b21", wood: "#17110e", horse: "#17110e", horseFar: "#17110e", blazon: "#ece3cf", shieldIn: "#7c2b21" },
    band: { bg: null, fg: "#17110e", accent: "#7c2b21" }, filler: "#17110e",
    lines: { detail: { c: "cut", w: .5 }, fine: { c: "cut", w: .34 }, fold: { c: "cut", w: .4 }, hem: { c: "cut", w: .46 } }, onLight: { c: "#17110e" } },
  "red-figure": { ground: "#15100d", contour: { c: "#15100d", w: .5 }, roles: { flame: "#c9733f", skin: "#c9733f", skinF: "#c9733f", hair: "#15100d", beard: "#15100d", cloth: "#c9733f", cloth2: "#c9733f", metal: "#c9733f", crest: "#15100d", wood: "#c9733f", horse: "#c9733f", horseFar: "#c9733f", blazon: "#15100d", shieldIn: "#c9733f" }, reserve: { hair: { c: "#c9733f", w: .34 }, beard: { c: "#c9733f", w: .3 }, crest: { c: "#c9733f", w: .34 } },
    onInk: { roles: ["hair", "beard", "crest", "blazon"], c: "#c9733f" }, band: { bg: "#c9733f", fg: "#15100d", accent: "#15100d" }, filler: "#c9733f",
    lines: { detail: { c: "#15100d", w: .44 }, fine: { c: "#6b3519", w: .3, a: .85 }, fold: { c: "#15100d", w: .34 }, hem: { c: "#15100d", w: .4 } } },
  "white-ground": { onInk: { roles: ["blazon"], c: "#c9b98e" }, cloths: ["#a8483a", "#c49a4a", "#6f7f6a", "#d9d0ba"], ground: "#e6dcc4", contour: { c: "#5a3a22", w: .42 }, roles: { flame: "#a8483a", skin: "#e6dcc4", skinF: "#efe7d3", hair: "#3a2416", beard: "#3a2416", cloth: "#a8483a", cloth2: "#c49a4a", metal: "#c9b98e", crest: "#a8483a", wood: "#8a6a44", horse: "#b89a70", horseFar: "#9c7f58", blazon: "#3a2416", shieldIn: "#a8483a" },
    band: { bg: null, fg: "#4a2e1a", accent: "#a8483a" }, filler: "#6a4a30",
    lines: { detail: { c: "#4a2e1a", w: .36 }, fine: { c: "#8a6a4a", w: .26 }, fold: { c: "#6a4a30", w: .3 }, hem: { c: "#6a4a30", w: .34 } } },
  polychrome: { onInk: { roles: ["blazon"], c: "#d3a94a" }, cloths: ["#a63a2c", "#d9b24e", "#3f6f78", "#ddd2b8", "#7a4a6a"], shade: { c: "#1c0f08", w: 5.5, a: .2 }, ground: "#2f5f86", contour: { c: "#2a1c14", w: .46 }, roles: { flame: "#d4551e", skin: "#c58a5c", skinD: "#7d5434", skinG: "#9c8457", skinF: "#ecd2ae", hair: "#2c1c12", beard: "#2c1c12", cloth: "#a63a2c", cloth2: "#d9b24e", metal: "#d3a94a", crest: "#a63a2c", wood: "#7c5a3a", horse: "#8a5a38", horseFar: "#6f4628", blazon: "#2a1c14", shieldIn: "#a63a2c" },
    band: { bg: "#d9b24e", fg: "#2a1c14", accent: "#a63a2c" }, filler: "#d9b24e",
    lines: { detail: { c: "#2a1c14", w: .4 }, fine: { c: "#5a3c28", w: .28 }, fold: { c: "#5a2a20", w: .34 }, hem: { c: "#2a1c14", w: .4 } } },
  // carved and painted on a temple: pale figures on a coloured or dark ground, a line of shadow round them
  relief: { onInk: { roles: ["blazon"], c: "#d3b060" }, shade: { c: "#3a3020", w: 4, a: .22 }, ground: "#2b4479", contour: { c: "#1a1a22", w: .7 }, roles: { flame: "#d3b060", skin: "#e8dcc4", skinF: "#f0e6d2", hair: "#b98a4a", beard: "#b98a4a", cloth: "#ddd0b6", cloth2: "#cdbd9c", metal: "#d3b060", crest: "#a63a2c", wood: "#8a6a44", horse: "#e4d6bc", horseFar: "#cfc0a2", blazon: "#a63a2c", shieldIn: "#cdbd9c" },
    band: { bg: "#d9b24e", fg: "#2a1c14", accent: "#a63a2c" }, filler: "#cdbd9c",
    lines: { detail: { c: "#6a5a48", w: .46 }, fine: { c: "#a89878", w: .34 }, fold: { c: "#8a7a60", w: .4 }, hem: { c: "#6a5a48", w: .42 } } },
};
// (a lion's coat: the horse's wherever a technique has one colour for all, its own where it paints in colour)
for (const T of Object.values(TECHNIQUES)) { T.roles.tawny = T.roles.horse; T.roles.tawnyFar = T.roles.horseFar; T.roles.blood ??= "#a8231a"; }
Object.assign(TECHNIQUES.polychrome.roles, { tawny: "#c2914a", tawnyFar: "#94682f" });
Object.assign(TECHNIQUES["black-figure"].roles, { tawny: "#7c2b21", tawnyFar: "#5a1f18" });   // (added red, or a beast merges with what it's on)
Object.assign(TECHNIQUES["red-figure"].roles, { tawny: "#a8602c", tawnyFar: "#8a4a20" });   // (dilute glaze, the same reason)
// (the polychrome palette on a red ground: nothing red that would dissolve into it)
for (const T of Object.values(TECHNIQUES)) T.roles.white = "#efe8d8";   // (an old head, in added white whatever else the painter has)
TECHNIQUES.metope = { ...TECHNIQUES.polychrome, cloths: ["#3f6f78", "#ddd2b8", "#7a4a6a", "#2f5f86", "#d9b24e"], roles: { ...TECHNIQUES.polychrome.roles, cloth: "#3f6f78", crest: "#ddd2b8", shieldIn: "#ddd2b8" } };
const LIGHT = new Set(["skinF"]);

// a ring as a smooth closed path through the midpoints, sharp at its corners
export function ringPath(P, ring) {
  const n = ring.length;
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const first = ring[0][2] ? ring[0] : mid(ring[n - 1], ring[0]);
  P.moveTo(first[0], first[1]);
  for (let i = 0; i < n; i++) {
    const c = ring[i], d = ring[(i + 1) % n], m = d[2] ? d : mid(c, d);
    if (c[2]) P.lineTo(c[0], c[1]); else P.quadraticCurveTo(c[0], c[1], m[0], m[1]);
    if (c[2] || d[2]) P.lineTo(m[0], m[1]);
  }
  P.closePath();
}
const area = (r) => { let s = 0; for (let i = 0, n = r.length; i < n; i++) { const a = r[i], b = r[(i + 1) % n]; s += a[0] * b[1] - b[0] * a[1]; } return s; };
export function linePath(P, pts, closed) {
  P.moveTo(pts[0][0], pts[0][1]);
  if (closed) { P.lineTo(pts[1][0], pts[1][1]); for (let i = 1; i <= pts.length; i++) { const q = pts[i % pts.length]; P.lineTo(q[0], q[1]); } P.closePath(); return; }
  if (pts.length === 2) { P.lineTo(pts[1][0], pts[1][1]); return; }
  for (let i = 1; i < pts.length - 1; i++) { const c = pts[i], d = pts[i + 1], end = i === pts.length - 2; P.quadraticCurveTo(c[0], c[1], end ? d[0] : (c[0] + d[0]) / 2, end ? d[1] : (c[1] + d[1]) / 2); }
}

// draw pieces, in `g` set to world units (y up), `ppu` pixels to a world unit. A figure is 100 units tall.
export function paintPieces(g, pieces, techName, { ppu = 1, poly } = {}) {
  const T = TECHNIQUES[techName] ?? TECHNIQUES["black-figure"], hpx = 100 * ppu, one = 1 / ppu;
  const stroke = (path, st, onLight) => {
    const cut = st.c === "cut" && !onLight;
    g.globalCompositeOperation = cut ? "destination-out" : "source-over";
    g.strokeStyle = cut ? "#000" : onLight && st.c === "cut" ? T.onLight?.c ?? "#000" : st.c;
    g.globalAlpha = st.a ?? 1;
    g.lineWidth = Math.max(st.w, one * .8);
    g.lineJoin = "round"; g.lineCap = "round";
    g.stroke(path);
    g.globalAlpha = 1; g.globalCompositeOperation = "source-over";
  };
  for (const p of [...pieces].sort((a, b) => a.z - b.z)) {
    const path = new Path2D();
    for (const r of p.rings) {
      const ring = area(r) < 0 ? [...r].reverse() : r;      // (one winding: rings of a piece never cancel where they overlap)
      ringPath(path, ring);
    }
    const base = T.reserve?.[p.role] ?? T.contour, cont = { ...base, w: base.w * 2 };
    if (p.rings.length && !p.noContour) stroke(path, cont, false);
    g.fillStyle = p.role === "filler" ? T.filler : p.tint !== undefined && T.cloths ? T.cloths[p.tint % T.cloths.length] : T.roles[p.role] ?? T.roles.skin;
    if (p.rings.length) g.fill(path, "nonzero");
    if (T.shade && p.rings.length && hpx > 40 && p.role !== "wood") {        // (a wall painter's modelling: a soft dark along the inside of each form)
      g.save(); g.clip(path, "nonzero"); g.strokeStyle = T.shade.c; g.globalAlpha = T.shade.a; g.lineWidth = T.shade.w; g.lineJoin = "round";
      const big = 1e4;                                                       // (each ring's edge only where no other ring of the piece covers it, no ball joints inside a limb)
      p.rings.forEach((r, i) => {
        g.save();
        p.rings.forEach((o, j) => { if (j === i) return; const out = new Path2D(); out.rect(-big, -big, 2 * big, 2 * big); ringPath(out, o); g.clip(out, "evenodd"); });
        const q = new Path2D(); ringPath(q, r); g.stroke(q);
        g.restore();
      });
      g.restore();
    }
    const light = LIGHT.has(p.role) && T.onLight;
    const inked = T.onInk?.roles.includes(p.role);
    for (const l of p.lines) {
      if ((l.cls === "fine" && hpx < 60) || (l.cls === "detail" && hpx < 34)) continue;
      const q = new Path2D(); linePath(q, l.pts, l.closed);
      const st = T.lines[l.cls] ?? T.lines.detail;
      const inside = (l.cls === "fold" || l.cls === "fine" || (l.cls === "hem" && p.role.startsWith("cloth"))) && p.rings.length;   // (a fold stops at its cloth's edge)
      if (inside) { g.save(); g.clip(path, "nonzero"); }
      stroke(q, inked ? { ...st, c: T.onInk.c, a: 1 } : st, light);
      if (inside) g.restore();
    }
    for (const m of p.marks) {
      if (hpx < 40) continue;
      const st = T.lines[m.cls] ?? T.lines.detail, cut = st.c === "cut" && !light;
      g.globalCompositeOperation = cut ? "destination-out" : "source-over";
      g.fillStyle = inked ? T.onInk.c : cut ? "#000" : st.c === "cut" ? T.onLight?.c ?? "#000" : st.c;
      g.beginPath(); g.arc(m.at[0], m.at[1], m.r, 0, Math.PI * 2); g.fill();
      g.globalCompositeOperation = "source-over";
    }
  }
}
// the ground, behind what is drawn
export function paintGround(g, techName, w, h, ground) {
  const T = TECHNIQUES[techName] ?? TECHNIQUES["black-figure"];
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
  g.globalCompositeOperation = "destination-over"; g.fillStyle = ground ?? T.ground; g.fillRect(0, 0, w, h);
  g.restore();
}
