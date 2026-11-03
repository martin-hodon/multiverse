// DOORS AS THEIR BUILDERS HUNG THEM (2026-11-02). A doorway's leaves, shaped to it (its head is the opening's own:
// arch/profiles.js archCurve) and made the way the culture that built it made doors:
//
//   boards    planks on battens (a barn, a Japanese temple's itatobira -- with `studs`, its rows of nail heads)
//   iron      oak under wrought-iron straps that branch into scrolls (a Gothic portal: Notre-Dame's Biscornet ironwork)
//   trellis   painted boards under a diamond lattice of iron straps, a stud at each crossing (a Russian church)
//   panel     stiles and rails framing raised panels, a brass handle (a baroque church, a palace)
//   bronze    cast bronze in square coffers, a boss in each (the Pantheon's, a Greek temple's, Pisa's, St Isaac's)
//   studded   lacquered red, rows of gilt nail heads and a lion's-head ring on each leaf (a Chinese gate: nine by nine
//             on the emperor's)
//   lattice   a frame, a solid panel below and a lattice over paper above (a Chinese hall's geshan, a Japanese
//             shoji or koshi door -- with `slide`, a door that slides)
//   carved    dark wood carved in lozenges between bosses, a border of studs (a mosque's, a Mughal tomb's)
//   plain     the slab alone
//
// A door is a marker's data (architecture.js lifeOf, or a doors asset: doorsOf) -- `w`, `h`, `spring`, `head` as the
// opening's, and: `look`, `color`, `accent` (the iron, the gilt, the paper), `leaves` (1, 2 or 4; 2 and up parted in the
// middle, each hinged at its own side -- or sliding, `slide`), `post` (metres of a pier the leaves close against: a
// trumeau), `wicket` (a small door cut in the left leaf -- [w, h] or true -- and THEN the great leaves stand fixed: the
// wicket is the way in, as at most cathedrals), `studs`, `rows`, `pane` (a lattice's squares, metres: wide ones are
// a glazed door's glazing bars), `leafH` (the leaves this high, a fixed tympanum over them in `fill`).
//
// doorLeaves(d) -> [{ geo, hinge, sign, x0, x1, kind, open, plain }]: each leaf's geometry in its HINGE's frame (x across
// the doorway away from the hinge -- negative for a leaf hinged on the right, `sign` -1 -- y up from the floor, z through
// it, the outside at +z), where its hinge is (`hinge`, metres from the left jamb), the stretch it closes (`x0`..`x1`, the
// same measure), what it does (`kind`: swing, slide or fixed), how far (`open`: radians, or metres for a slide) and
// whether it is painted plain rather than in the wood's grain (`plain`). One geometry per door of one shape.
import * as THREE from "three";
import { archCurve } from "./arch/profiles.js";
import { paintGeometry, doorPanel } from "./architecture.js";

// what each look is drawn in when the door says nothing (and whether it shows a grain: lacquer and bronze do not)
export const DOOR_LOOKS = {
  boards:  { color: 0x6a4a2c, accent: 0x2b2926 },
  iron:    { color: 0x3e2a1a, accent: 0x1e1c1a },
  trellis: { color: 0x6b2a1e, accent: 0x24211f },
  panel:   { color: 0x4f321e, accent: 0xb08d3c },
  bronze:  { color: 0x5a4628, accent: 0x8c703e, plain: true },
  studded: { color: 0x8c2318, accent: 0xc9a13a, plain: true },
  lattice: { color: 0x8c2318, accent: 0xe6dcc4, plain: true },
  carved:  { color: 0x4a2c18, accent: 0xb38b3e },
  plain:   { color: 0x5a3c22, accent: 0x2b2926 },
};
const shade = (c, k) => { const r = Math.min(255, Math.round(((c >> 16) & 255) * k)), g = Math.min(255, Math.round(((c >> 8) & 255) * k)), b = Math.min(255, Math.round((c & 255) * k)); return (r << 16) | (g << 8) | b; };

const cache = new Map();
export function doorLeaves(d) {
  const key = JSON.stringify([d.w, d.h, d.spring, d.head, d.look, d.color, d.accent, d.leaves, d.wicket, d.slide, d.post, d.studs, d.rows, d.open, d.leafH, d.fill, d.pane]);
  if (!cache.has(key)) cache.set(key, makeLeaves(d));
  return cache.get(key);
}

// A BUILDING'S DOORS, SHUT, as one group in its own frame (the asset manager's stand: assets.html): each leaf where the
// game hangs it (index.html, the site's door loop) -- the doorway's middle at (x, z), turned by `yaw`, the leaf on its
// hinge; a door marker with no look (a house's) its one plain panel (architecture.js doorPanel), as the game draws it.
// `mats`: { wood, plain } -- the grain, or a colour alone (lacquer, bronze)
export function doorGroup(doors, mats) {
  const g = new THREE.Group();
  for (const d of doors) {
    if (d.panel === false) continue;   // (a doorway with no door: a shop's open arch)
    const base = -(d.yaw ?? 0) * Math.PI / 180, ax = Math.cos(base), az = -Math.sin(base);
    const lx = d.x - ax * d.w / 2, lz = d.z - az * d.w / 2;
    if (!d.look) {
      const m = new THREE.Mesh(doorPanel(d), mats.wood);
      m.position.set(lx, d.y ?? .15, lz); m.rotation.y = base;
      g.add(m); continue;
    }
    for (const lf of doorLeaves(d)) {
      const m = new THREE.Mesh(lf.geo, lf.plain ? mats.plain : mats.wood);
      m.position.set(lx + ax * lf.hinge, d.y ?? .15, lz + az * lf.hinge); m.rotation.y = base;
      g.add(m);
    }
  }
  return g;
}

function makeLeaves(d) {
  const look = DOOR_LOOKS[d.look] ? d.look : "plain", L = DOOR_LOOKS[look];
  const color = d.color ?? L.color, accent = d.accent ?? L.accent, plain = !!L.plain;
  const w = d.w, head = d.head ?? { profile: "flat" }, sp = d.head ? d.spring ?? d.h : d.h - .02;
  // the opening's top over x (0 at the left jamb): straight jambs to the springing, then its head
  const curve = archCurve(w / 2, head).map(([x, y]) => [Math.min(w, Math.max(0, w / 2 + x)), sp + y - .02]);
  const topAt = (x) => {
    for (let i = 1; i < curve.length; i++) {
      const [ax, ay] = curve[i - 1], [bx, by] = curve[i];
      if (x >= ax - 1e-9 && x <= bx + 1e-9) return bx - ax < 1e-9 ? Math.max(ay, by) : ay + (by - ay) * (x - ax) / (bx - ax);
    }
    return sp - .02;
  };
  // the top of the stretch x0..x1, right to left, cut off at `cap` (the leaves under a tympanum stop at its lintel) --
  // or, `above`, the part of it over `cap` (the tympanum's own top)
  const topLine = (x0, x1, cap = Infinity, above = false) => {
    const pts = [[x1, topAt(x1)], ...curve.filter(([x]) => x > x0 + 1e-3 && x < x1 - 1e-3).reverse(), [x0, topAt(x0)]], out = [];
    for (let i = 0; i < pts.length; i++) {
      const [ax, ay] = pts[i];
      if (i) { const [bx, by] = pts[i - 1]; if ((ay - cap) * (by - cap) < 0) out.push([bx + (ax - bx) * (cap - by) / (ay - by), cap]); }
      if (above ? ay >= cap : true) out.push([ax, above ? ay : Math.min(ay, cap)]);
    }
    return out;
  };
  const leafH = d.leafH ?? Infinity;
  const T = Math.min(.16, Math.max(.07, .05 + .012 * Math.min(d.h, leafH)));   // (a great door is thick: a cathedral's leaves 15cm of oak)
  const n = Math.max(1, Math.round(d.leaves ?? (w > 1.7 ? 2 : 1))), post = d.post ?? 0, gap = .012;
  // the leaves' stretches: parted in the middle (round a trumeau, `post`), each hinged at its outer side
  const spans = [];
  if (n === 1) spans.push([0, w, 0, 1]);
  else {
    const half = (w - post) / 2, per = n / 2;
    for (let k = 0; k < per; k++) spans.push([k * half / per + (k ? gap / 2 : 0), (k + 1) * half / per - gap / 2, k * half / per, 1]);
    for (let k = 0; k < per; k++) { const a = w - (k + 1) * half / per, b = w - k * half / per; spans.push([a + gap / 2, b - (k ? gap / 2 : 0), b, -1]); }
  }
  const slide = !!d.slide, wicket = d.wicket ? (Array.isArray(d.wicket) ? d.wicket : [Math.min(1.0, (spans[0][1] - spans[0][0]) * .6), Math.min(2.1, sp * .5)]) : null;
  const out = [];
  spans.forEach(([x0, x1, hinge, sign], i) => {
    // (a wicket in the left leaf: a notch out of its foot, and a leaf of its own in it, hinged at the notch's side)
    const notch = wicket && i === 0 ? [(x0 + x1) / 2 - wicket[0] / 2, (x0 + x1) / 2 + wicket[0] / 2, wicket[1]] : null;
    const geo = leafGeometry({ x0, x1, top: topLine(x0, x1, leafH), T, look, color, accent, notch, d, hingeSide: sign > 0 ? x0 : x1 });
    geo.translate(-hinge, 0, 0);
    const kind = wicket ? "fixed" : slide ? "slide" : "swing";
    out.push({ geo, hinge, sign, x0, x1, kind, plain, open: slide ? (x1 - x0) * .96 : d.open !== undefined ? d.open * Math.PI / 180 : n > 1 ? 1.45 : 1.6, ...(notch ? { notch } : {}) });
    if (notch) {
      const wg = leafGeometry({ x0: notch[0] + gap, x1: notch[1] - gap, top: [[notch[1] - gap, notch[2] - gap], [notch[0] + gap, notch[2] - gap]], T: T * .8, look, color, accent, notch: null, d: { ...d, wicketOf: true }, hingeSide: notch[0] });
      wg.translate(-(notch[0] + gap), 0, 0);
      out.push({ geo: wg, hinge: notch[0] + gap, sign: 1, x0: notch[0] + gap, x1: notch[1] - gap, kind: "swing", plain, open: 1.6, wicket: true });
    }
  });
  // A TYMPANUM over leaves that stop short of the head (`leafH`): the rest of the opening stone, standing, its lintel a
  // band across under it (`fill` its colour)
  if (leafH < d.h - .05) {
    const stone = d.fill ?? 0xcfc6b2, shape = new THREE.Shape(), top = topLine(0, w, leafH, true);
    shape.moveTo(0, leafH); shape.lineTo(w, leafH); for (const [x, y] of top) shape.lineTo(x, y); shape.lineTo(0, leafH);
    const Tf = Math.max(.25, T * 2), g = new THREE.ExtrudeGeometry(shape, { depth: Tf, bevelEnabled: false, curveSegments: 2 }); g.translate(0, 0, -Tf / 2);
    const lin = new THREE.BoxGeometry(w + .02, .4, Tf + .12); lin.translate(w / 2, leafH + .2, 0);
    const carve = [paintGeometry(g, stone, stone), paintGeometry(lin, shade(stone, .9), shade(stone, .9))], relief = shade(stone, .86);
    // its carving, in outline: a moulding following the arch a hand inside it, and in the middle a mandorla (where the
    // real ones have Christ in majesty, or the Virgin)
    const cx = w / 2, cy = leafH + .4, ring = top.map(([x, y]) => [cx + (x - cx) * .86, cy + (y - cy) * .84]);
    const rise = Math.max(...top.map(([, y]) => y)) - cy;
    if (rise > .8) {
      for (let i = 1; i < ring.length; i++) {
        const [ax, ay] = ring[i - 1], [bx, by] = ring[i], b = new THREE.BoxGeometry(Math.hypot(bx - ax, by - ay) + .06, .12, Tf + .1);
        b.rotateZ(Math.atan2(by - ay, bx - ax)); b.translate((ax + bx) / 2, (ay + by) / 2, 0); carve.push(paintGeometry(b, relief, relief));
      }
      const mh = rise * .62, mw = Math.min(w * .26, mh * .55), m = new THREE.CylinderGeometry(.5, .5, Tf + .16, 16);
      m.rotateX(Math.PI / 2); m.scale(mw, mh, 1); m.translate(cx, cy + rise * .42, 0); carve.push(paintGeometry(m, relief, relief));
    }
    out.push({ geo: merged(carve), hinge: 0, sign: 1, x0: 0, x1: w, kind: "fixed", plain: true, tympanum: true });
  }
  return out;
}
const merged = (parts) => {
  const flat = parts.map((g) => (g.index ? g.toNonIndexed() : g)), geo = new THREE.BufferGeometry();
  for (const name of ["position", "normal", "uv", "aC", "aC2"]) {
    const size = flat[0].attributes[name].itemSize, arr = new Float32Array(flat.reduce((k, g) => k + g.attributes[name].count * size, 0));
    let o = 0; for (const g of flat) { arr.set(g.attributes[name].array, o); o += g.attributes[name].array.length; }
    geo.setAttribute(name, new THREE.BufferAttribute(arr, size));
  }
  return geo;
};

// ONE LEAF, in the doorway's frame: its slab cut to the opening's outline between x0 and x1 (less a wicket's notch),
// and its look on both faces
function leafGeometry({ x0, x1, top, T, look, color, accent, notch, d, hingeSide }) {
  const shape = new THREE.Shape();
  shape.moveTo(x0, 0);
  if (notch) { shape.lineTo(notch[0], 0); shape.lineTo(notch[0], notch[2]); shape.lineTo(notch[1], notch[2]); shape.lineTo(notch[1], 0); }
  shape.lineTo(x1, 0);
  for (const [x, y] of top) shape.lineTo(x, y);   // (its top, right to left)
  shape.lineTo(x0, 0);
  const slab = new THREE.ExtrudeGeometry(shape, { depth: T, bevelEnabled: false, curveSegments: 2 });
  slab.translate(0, 0, -T / 2);
  const parts = [paintGeometry(slab, color, color)];
  const lw = x1 - x0, yTop = Math.min(top[0][1], top[top.length - 1][1]), mid = (x0 + x1) / 2;
  const far = hingeSide === x0 ? x1 : x0, fs = far > hingeSide ? -1 : 1;   // (the latch side, and the way back from it)
  // a box `bw` x `bh`, `pd` proud of both faces, its middle at (x, y); turned `ang` in the face
  const plate = (x, y, bw, bh, pd, c, ang = 0) => {
    for (const zs of [-1, 1]) { const g = new THREE.BoxGeometry(bw, bh, pd); if (ang) g.rotateZ(ang); g.translate(x, y, zs * (T / 2 + pd / 2)); parts.push(paintGeometry(g, c, c)); }
  };
  const stud = (x, y, r, c) => {
    for (const zs of [-1, 1]) { const g = new THREE.SphereGeometry(r, 6, 3, 0, Math.PI * 2, 0, Math.PI / 2); g.rotateX(zs * Math.PI / 2); g.scale(1, 1, .7); g.translate(x, y, zs * T / 2); parts.push(paintGeometry(g, c, c)); }
  };
  const ring = (x, y, r, c) => {
    for (const zs of [-1, 1]) {
      const boss = new THREE.CylinderGeometry(r * .75, r * .9, .03, 10); boss.rotateX(Math.PI / 2); boss.translate(x, y + r * .6, zs * (T / 2 + .015)); parts.push(paintGeometry(boss, c, c));
      const g = new THREE.TorusGeometry(r, r * .14, 5, 14); g.translate(x, y - r * .15, zs * (T / 2 + .045)); parts.push(paintGeometry(g, c, c));
    }
  };
  // a bar from (ax, ay) to (bx, by), `bw` wide
  const bar = (ax, ay, bx, by, bw, pd, c) => plate((ax + bx) / 2, (ay + by) / 2, Math.hypot(bx - ax, by - ay), bw, pd, c, Math.atan2(by - ay, bx - ax));
  // a line at `ang` through (px, py), clipped to the leaf's rectangle -> its two ends, or null
  const clip = (px, py, ang, X0, X1, Y0, Y1) => {
    const dx = Math.cos(ang), dy = Math.sin(ang); let t0 = -1e9, t1 = 1e9;
    for (const [p, dp, lo, hi] of [[px, dx, X0, X1], [py, dy, Y0, Y1]]) {
      if (Math.abs(dp) < 1e-9) { if (p < lo || p > hi) return null; continue; }
      let a = (lo - p) / dp, b = (hi - p) / dp; if (a > b) [a, b] = [b, a];
      t0 = Math.max(t0, a); t1 = Math.min(t1, b);
    }
    return t1 - t0 > .05 ? [px + dx * t0, py + dy * t0, px + dx * t1, py + dy * t1] : null;
  };
  const wk = !!d.wicketOf, m = Math.min(.12, lw * .08);   // (a margin in from the leaf's edges)
  const knobY = Math.min(1.05, yTop - .25), latchX = far + fs * Math.min(.14, lw * .12);
  if (look === "boards" || look === "plain") {
    if (look === "boards") {
      const dark = shade(color, .78), nb = Math.max(1, Math.round(lw / .2));
      for (let k = 1; k < nb; k++) plate(x0 + k * lw / nb, yTop / 2, .012, yTop - .04, .003, dark);
      const battens = Math.max(2, Math.round(yTop / 1.5) + 1);
      for (let k = 0; k < battens; k++) {
        const y = .3 + (yTop - .6) * k / (battens - 1);
        plate(mid, y, lw - .04, .12, .025, dark);
        if (d.studs) for (let s = 0, ns = Math.max(2, Math.round(lw / .25)); s < ns; s++) stud(x0 + (s + .5) * lw / ns, y, .022, accent);
      }
    }
    if (!wk) for (const y of [.3, Math.max(.6, yTop - .35)]) plate(hingeSide + (far - hingeSide) * .36, y, lw * .72, .05, .012, accent);   // (strap hinges, out from the hinge side)
    stud(latchX, knobY, .035, accent);
  } else if (look === "iron") {
    // straps from the hinge side, each branching into scrolls -- a pair of short bars at 35 degrees, twice along it
    const ns = wk ? 2 : Math.max(2, Math.round(yTop / 1.1));
    for (let k = 0; k < ns; k++) {
      const y = .35 + (yTop - .7) * k / Math.max(1, ns - 1), L0 = lw * .86, xe = hingeSide + (far - hingeSide) * .86;
      plate(hingeSide + (xe - hingeSide) / 2, y, L0, .07, .014, accent);
      for (const f of [.4, .75]) {
        const bx = hingeSide + (xe - hingeSide) * f, br = Math.min(.45, lw * .18, (yTop - .7) / Math.max(1, ns - 1) * .45);
        for (const sy of [-1, 1]) bar(bx, y, bx - fs * br * .8, y + sy * br * .6, .035, .012, accent);
      }
      for (let s = 0, n = Math.max(3, Math.round(L0 / .3)); s < n; s++) stud(hingeSide + (xe - hingeSide) * (s + .5) / n, y, .022, accent);
    }
    if (!wk) ring(latchX + fs * .1, knobY, .09, accent); else stud(latchX, knobY, .035, accent);
  } else if (look === "trellis") {
    const p = Math.max(.35, Math.min(.55, lw / 3)), X0 = x0 + m, X1 = x1 - m, Y0 = m, Y1 = yTop - m;
    for (const ang of [Math.PI / 4, -Math.PI / 4]) for (let c = -Math.ceil((yTop + lw) / p); c <= Math.ceil((yTop + lw) / p); c++) {
      const s = clip(X0 + c * p * Math.SQRT2, Y0, ang, X0, X1, Y0, Y1); if (s) bar(s[0], s[1], s[2], s[3], .04, .012, accent);
    }
    plate(mid, Y0, lw - 2 * m, .05, .014, accent); plate(mid, Y1, lw - 2 * m, .05, .014, accent);
    ring(latchX + fs * .1, knobY, .08, accent);
  } else if (look === "panel" || look === "carved") {
    // stiles and rails standing proud, the panels between raised again; carved: lozenges in a grid, bosses between
    const fr = shade(color, 1.12), pn = shade(color, look === "carved" ? .85 : 1.15), st = Math.min(.14, lw * .12);
    plate(x0 + st / 2, yTop / 2, st, yTop, .02, fr); plate(x1 - st / 2, yTop / 2, st, yTop, .02, fr);
    const rows = look === "carved" ? [] : wk ? [[.15, .85]] : yTop > 4 ? [[.05, .2], [.24, .62], [.66, .95]] : [[.06, .32], [.38, .94]];
    // (each panel: a sunk margin in shadow, the field raised out of it, lit -- on a pale painted door a gilt bead round the field)
    const sunk = shade(color, .62), gilt = ((color >> 16) & 255) > 150;
    for (const [a, b] of rows) {
      const y0 = a * yTop, y1 = b * yTop, pw = lw - 2 * st - .06, ph = y1 - y0, ins = Math.min(.1, pw * .14);
      plate(mid, (y0 + y1) / 2, pw, ph, .012, sunk);
      plate(mid, (y0 + y1) / 2, pw - 2 * ins, ph - 2 * ins, .04, shade(color, 1.3));
      if (gilt) for (const [bx, by, bw2, bh2] of [[mid, y0 + ins, pw - 2 * ins, .025], [mid, y1 - ins, pw - 2 * ins, .025], [mid - pw / 2 + ins, (y0 + y1) / 2, .025, ph - 2 * ins], [mid + pw / 2 - ins, (y0 + y1) / 2, .025, ph - 2 * ins]]) plate(bx, by, bw2, bh2, .046, accent);
      plate(mid, y0 - .04, lw, .08, .02, fr); plate(mid, y1 + .04, lw, .08, .02, fr);
    }
    if (look === "carved") {
      const cols = Math.max(1, Math.round((lw - 2 * st) / .5)), cw = (lw - 2 * st) / cols, nr = Math.max(2, Math.round((yTop - .3) / cw));
      const ch = (yTop - .3) / nr;
      for (let r = 0; r < nr; r++) for (let c = 0; c < cols; c++) {
        const cx = x0 + st + (c + .5) * cw, cy = .15 + (r + .5) * ch, s = Math.min(cw, ch) * .5;
        plate(cx, cy, s, s, .03, pn, Math.PI / 4);
        stud(cx, cy, Math.min(.04, s * .18), accent);
        if (c < cols - 1 && r < nr - 1) stud(cx + cw / 2, cy + ch / 2, Math.min(.03, s * .14), accent);
      }
      for (let s = 0, ns = Math.max(4, Math.round(yTop / .3)); s < ns; s++) for (const x of [x0 + st / 2, x1 - st / 2]) stud(x, (s + .5) * yTop / ns, .02, accent);
      if (!wk) ring(latchX + fs * .12, knobY + .15, .1, accent);
    } else plate(latchX + fs * .03, knobY, .03, .32, .04, accent);   // (a brass handle, upright)
  } else if (look === "bronze") {
    // cast in square coffers: a grid of raised bars, a boss in each square
    const cols = Math.max(1, Math.round(lw / 1.0)), cw = lw / cols, nr = Math.max(2, Math.round(yTop / cw)), ch = yTop / nr;
    const rail = Math.min(.12, cw * .12), hi = shade(color, 1.18);
    for (let c = 0; c <= cols; c++) plate(x0 + c * cw + (c === 0 ? rail / 2 : c === cols ? -rail / 2 : 0), yTop / 2, rail, yTop, .03, hi);
    for (let r = 0; r <= nr; r++) plate(mid, r * ch + (r === 0 ? rail / 2 : r === nr ? -rail / 2 : 0), lw, rail, .03, hi);
    for (let r = 0; r < nr; r++) for (let c = 0; c < cols; c++) stud(x0 + (c + .5) * cw, (r + .5) * ch, Math.min(.12, Math.min(cw, ch) * .16), accent);
    if (!wk) ring(latchX + fs * .12, knobY + .2, .11, accent);
  } else if (look === "studded") {
    // nine rows of gilt nail heads (the emperor's), as many across as the leaf takes, and the lion's ring
    const nr = d.rows ?? 9, nc = Math.max(3, Math.min(9, Math.round(lw / .42))), y0 = yTop * .07, y1 = yTop * .93;
    const r = Math.min(.08, (y1 - y0) / nr * .22, lw / nc * .24);
    for (let a = 0; a < nr; a++) for (let b = 0; b < nc; b++) stud(x0 + m + (b + .5) * (lw - 2 * m) / nc, y0 + (a + .5) * (y1 - y0) / nr, r, accent);
    if (!wk) ring(far + fs * Math.min(.35, lw * .2), Math.min(yTop * .45, 1.4), Math.min(.16, lw * .1), accent);
  } else if (look === "lattice") {
    // a frame, a solid panel below, a lattice of thin bars over paper above (or glass: `accent` is what is behind)
    const fr = color, st = Math.min(.09, lw * .1), split = yTop * (d.slide ? .22 : d.pane > .3 ? .26 : .38), top = yTop - st;
    plate(x0 + st / 2, yTop / 2, st, yTop, .02, fr); plate(x1 - st / 2, yTop / 2, st, yTop, .02, fr);
    plate(mid, st / 2, lw, st, .02, fr); plate(mid, split, lw, st, .02, fr); plate(mid, top + st / 2, lw, st, .02, fr);
    plate(mid, (split + top) / 2, lw - 2 * st, top - split - st / 2, .004, accent);   // the paper
    const pw = d.pane ?? .16, nx = Math.max(2, Math.round((lw - 2 * st) / pw)), ny = Math.max(3, Math.round((top - split) / (pw * 1.25)));
    for (let k = 1; k < nx; k++) plate(x0 + st + k * (lw - 2 * st) / nx, (split + top) / 2, .025, top - split, .014, fr);
    for (let k = 1; k < ny; k++) plate(mid, split + k * (top - split) / ny, lw - 2 * st, .025, .014, fr);
    if (!d.slide) stud(latchX, knobY, .03, shade(accent, .7));
  }
  return merged(parts);
}
