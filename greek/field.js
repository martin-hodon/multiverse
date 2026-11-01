// GREEK PAINTINGS, the field (docs/greek.md): a painting is a stack of ZONES over its height: a band of ornament, a solid
// stripe, a frieze of scenes along a ground line, or one or more panels each one scene. A frieze is laid out by trying a few
// runs of scenes and keeping the one with the most even gaps (geometry only, nothing drawn); gaps too wide take a filler.
// Everything is one layer; cuts show the ground, which goes in last (paint.js).
import { stream, pick } from "./rig.js";
import { solveGroup } from "./scene.js";
import { silhouette, unlike, notch } from "./measure.js";
import { paintPieces, paintGround, ringPath, linePath, TECHNIQUES } from "./paint.js";

// a band: whole cells across w, between y and y + h (pixels, y down)
export function drawBand(g, O, x, y, w, h, band, orn, squeeze = 1) {
  const n = Math.max(1, Math.round(w * squeeze / (h * O.aspect))), cw = w / n;   // (squeeze: a neck narrower than the body the painting is drawn for takes fewer cells)
  if (band.bg) { g.fillStyle = band.bg; g.fillRect(x, y, w, h); }
  const clear = () => { g.fillStyle = band.fg; g.fillRect(x, y, w, Math.max(1, h * .03)); g.fillRect(x, y + h - Math.max(1, h * .03), w, Math.max(1, h * .03)); };
  const every = O.every, Alt = every && orn?.[every[1]];
  for (let i0 = 0; i0 < n; i0++) {
    const i = i0, alt = Alt && i0 % every[0] === every[0] - 1;
    if (alt) { drawBand(g, Alt, x + i * cw, y, cw, h, band); continue; }
    g.save();
    g.setTransform(cw, 0, 0, -h, x + i * cw, y + h);
    const paint = (O.alt && i % 2) ? band.accent : band.fg;
    if (O.rings?.length) { const p = new Path2D(); for (const r of O.rings) ringPath(p, r); g.fillStyle = paint; g.fill(p); }
    g.restore();
    if (O.lines) for (const l of O.lines) {                            // (lines stroked in pixels, so a stretched cell keeps its weight)
      const q = new Path2D();
      const pts = l.map(([u, v]) => [x + (i + u) * cw, y + h - v * h]);
      if (O.sharp) { q.moveTo(pts[0][0], pts[0][1]); for (const c of pts.slice(1)) q.lineTo(c[0], c[1]); } else linePath(q, pts);
      g.strokeStyle = band.fg; g.lineWidth = Math.max(1, O.w * h); g.lineCap = O.sharp ? "square" : "round"; g.lineJoin = "miter";
      g.stroke(q);
    }
  }
  clear();
}

// (a worker has no document; software-backed, or one drawn while WebGPU starts comes back empty)
const canvasOf = (w, h) => typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(w, h) : Object.assign(document.createElement("canvas"), { width: w, height: h });

// a band bent into a ring round a picture, a cup's tondo: { r, w } shares of the width, [the band's name]
function drawRing(g, O, W, H, R, band, orn) {
  const r1 = (R.r + R.w) * W, len = Math.round(Math.PI * 2 * r1), h = Math.round(R.w * W), strip = canvasOf(len, h);
  drawBand(strip.getContext("2d"), O, 0, 0, len, h, band, orn);
  const n = Math.round(len / 3), step = len / n;
  for (let i = 0; i < n; i++) {
    g.setTransform(1, 0, 0, 1, W / 2, H / 2); g.rotate(i / n * Math.PI * 2);
    g.drawImage(strip, i * step, 0, step, h, -step / 2 - .5, -r1, step + 1, h);
  }
  g.setTransform(1, 0, 0, 1, 0, 0);
}

// how far across the bodies of a group reach, leaving out what they carry on a shaft
function bodySpan(G) {
  const xs = G.pieces.filter((p) => !p.shaft).flatMap((p) => p.rings.flat().map((q) => q[0]));
  return [Math.min(...xs), Math.max(...xs)];
}

// a scene solved to a rectangle of w by h pixels, and its pixels a unit. In a panel of its own (`sparse`) the bodies decide the size: closer together
// where they can, as far as nothing goes wrong (a scene's `press` over the zone's: above 1, wider than the square and so smaller, a distance between them), shafts held inside the panel at the size it is drawn; otherwise one height of figure whatever the seed
function fitGroup(data, name, Z, w, h, opts) {
  const wide = data.scenes[name].wide, fill = Z.fill ?? .9, edge = Math.min(.99, fill * (Z.sparse ? Z.press ?? 1 : 1)), press = Z.sparse ? data.scenes[name].press ?? Z.press ?? 1 : 1, solve = (more) => solveGroup(data, name, { ...opts, tight, sparse: Z.sparse, ...more }), span = () => { const [a, b] = bodySpan(G); return b - a; };
  let tight = (wide ? Z.tightWide : null) ?? Z.tight ?? 1, G = solve();
  for (let a = 0, t0, s0; Z.sparse && a < 2; a++) {            // (the span a square wants, as near as a step gets it: the bodies held in a stance, so span runs about straight with `tight`)
    const s = span(), want = (G.height + 3) * w / h * press;
    if (s <= want) break;
    const next = t0 === undefined ? tight * Math.max(.7, want / s) : tight + (want - s) * (tight - t0) / ((s - s0) || 1);
    t0 = tight; s0 = s; tight = Math.max(wide ? .55 : .35, Math.min(tight, next)); G = solve({ want });
  }
  for (let a = 0, top = (wide ? Z.tightWide : null) ?? Z.tight ?? 1; Z.sparse && G.faults && tight < top && a < 3; a++) {   // (pressed until something's wrong: a step back, smaller and read, beats larger and lost)
    tight = Math.min(top, tight * 1.14);
    const H = solve();
    if (H.faults < G.faults) G = H;
  }
  if (Z.sparse) {
    const [b0, b1] = bodySpan(G), size = Math.min(h * fill / (G.height + 3), w * edge / (b1 - b0)), half = w * fill / size / 2, mid = (b0 + b1) / 2;
    const { key, faults } = G;
    G = solve({ key, top: h * .92 / size, side: [mid - half, mid + half] });
    G.key = key; G.faults = faults;
  }
  return { G, ppu: Math.min(h * fill / Math.max(Z.sparse ? 0 : data.canon.man, G.height + 3), w * edge / (G.max - G.min)) };   // (a hand may reach the panel's side, never past: cut off there it is a stump; a scene's `press` asks for distance, and pays for it in size)
}

// which of a zone's scenes a tile's panels get, in order: `must` first, then each `shape` (how bodies are arranged; a scene's own name if it says none) its turn
// in an order the seed picks, so a list longer than a tile leaves out different shapes on different tiles; then no two neighbours alike
function planDeck(data, Z, s0) {
  const r = stream(s0, "plan"), draw = (a) => a.splice(Math.floor(r() * a.length), 1)[0], shape = (i) => data.scenes[Z.scenes[i]].shape ?? Z.scenes[i];
  const left = new Map(), taken = [];
  Z.scenes.forEach((n, i) => { if (Z.must?.includes(n) && !taken.some((q) => Z.scenes[q] === n)) taken.push(i); else left.set(shape(i), [...(left.get(shape(i)) ?? []), i]); });
  const turns = [...left.keys()], order = [], had = new Set(taken.map(shape));
  while (turns.length) order.push(draw(turns));
  order.sort((a, b) => had.has(a) - had.has(b));                       // (a shape `must` has brought comes round last)
  const dealt = [];
  while (order.some((q) => left.get(q).length)) for (const q of order) if (left.get(q).length) dealt.push(draw(left.get(q)));
  const spare = dealt.splice(Math.max(0, Z.panels - taken.length));
  taken.push(...dealt);
  const deck = [];
  while (taken.length) { const ok = taken.filter((i) => !deck.length || shape(i) !== shape(deck.at(-1))); const i = draw(ok.length ? ok : [...taken]); taken.splice(taken.indexOf(i), 1); deck.push(i); }
  deck.spare = spare;                                                  // (whoever didn't get a panel: a stand-in where a panel's own scene looks too like its neighbours)
  return deck;
}

// a filler standing in a gap
function fillerPieces(F, x, height, r) {
  const stem = F.stem.map(([a, b]) => [x + a, b * height / 100]), rings = [];
  for (let i = 0; i < F.leaves; i++) {
    const t = .3 + .7 * (i + .5) / F.leaves, k = t * (stem.length - 1), j = Math.min(stem.length - 2, Math.floor(k)), u = k - j;
    const p = [stem[j][0] + (stem[j + 1][0] - stem[j][0]) * u, stem[j][1] + (stem[j + 1][1] - stem[j][1]) * u];
    const side = i % 2 ? 1 : -1, a = side * (.7 + r() * .5), [L, W] = F.leaf, ux = Math.sin(a), uy = Math.cos(a);
    rings.push([[p[0], p[1], 1], [p[0] + ux * L * .5 + uy * W, p[1] + uy * L * .5 - ux * W], [p[0] + ux * L, p[1] + uy * L, 1], [p[0] + ux * L * .5 - uy * W, p[1] + uy * L * .5 + ux * W]]);
  }
  return [{ z: -1, role: "filler", rings, lines: [{ cls: "hem", pts: stem }], marks: [] }];
}

// the best of a few runs of scenes along a width in world units
function layoutRun(data, Z, width, period, seed) {
  let best = null;
  for (let c = 0; c < 6; c++) {
    const r = stream(seed, "run", c), groups = [], uses = Z.scenes.map(() => 0);
    let used = 0, last = -1, tries = 0;
    while (tries++ < 24) {
      const least = Math.min(...uses), turn = Z.scenes.flatMap((_, k) => uses[k] === least && (k !== last || Z.scenes.length < 2) ? [k] : []), from = turn.length ? turn : Z.scenes.map((_, k) => k);   // (each scene its turn before any comes again)
      const i = from[Math.floor(r() * from.length)];
      const g = solveGroup(data, Z.scenes[i], { seed: seed * 977 + c * 31 + groups.length * 7, period, flip: Z.flow && Z.flow < 0 }), w = g.max - g.min;
      if (used + w + 16 * (groups.length + 1) > width) { if (groups.length) break; else continue; }
      groups.push(g); used += w; last = i; uses[i]++;
    }
    if (!groups.length) continue;
    const gap = (width - used) / groups.length, score = -Math.abs(gap - 24) - (new Set(groups.map((g) => g.name)).size < Math.min(2, Z.scenes.length) ? 30 : 0);
    if (!best || score > best.score) best = { score, groups, gap };
  }
  return best;
}

// a painting on a new canvas: spec { tech, period, aspect, ground, ink, zones }, px its width
export function renderPainting(data, spec, { px = 1024, seed = 1 } = {}) {
  const [aw, ah] = spec.aspect ?? [2, 1], W = Math.round(px), H = Math.round(px * ah / aw);
  const cv = canvasOf(W, H);
  const g = cv.getContext("2d", { willReadFrequently: true }), T = TECHNIQUES[spec.tech] ?? TECHNIQUES["black-figure"], tech = spec.tech;
  const period = spec.period ?? "classical", orn = data.parts.ornaments;
  const total = spec.zones.reduce((a, z) => a + z.h, 0);
  const inkFill = T.band.fg, Tb = T.band;
  const zoneClip = (x, y, w, h) => { g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); };

  // one scene or a run of them over a rectangle
  const choose = (Z, w, h, s, k = 0, s0 = s, seen = Object.assign(new Set(), { sils: [] })) => {
    const n = Z.scenes.length, deck = Z.scenes.map((_, i) => i), rd = stream(s0, "scene");
    for (let i = n - 1; i > 0; i--) { const j = Math.floor(rd() * (i + 1)); [deck[i], deck[j]] = [deck[j], deck[i]]; }
    if (Z.must) for (let i = 0, f = 0; i < n; i++) if (Z.must.includes(Z.scenes[deck[i]])) { [deck[f], deck[i]] = [deck[i], deck[f]]; f++; }   // (`must`: of a list longer than a tile, these always come; then the panels shuffled again, or they'd hold the first ones)
    if (Z.must) for (let i = Math.min(n, Z.panels) - 1; i > 0; i--) { const j = Math.floor(rd() * (i + 1)); [deck[i], deck[j]] = [deck[j], deck[i]]; }
    const plan = Z.plan && planDeck(data, Z, s0), name = Z.scenes[plan ? plan[k % plan.length] : Z.deal ? (seed * (Z.panels ?? 1) + k) % n : deck[k % n]];   // (panels deal from a shuffled list, so none comes twice before all have; `deal`: a pot's few paintings each their own, by seed)
    let G, ppu, keep;
    for (let t = 0; t < 12; t++) {                           // (a panel doesn't look like one already there, its two bodies aren't one mass, nothing wrong in it; above all, not anyone who comes `one` to a zone)
      const stand = plan && t >= 4 && plan.spare.length && !Z.must?.includes(name) ? Z.scenes[plan.spare[(t - 4) % plan.spare.length]] : name;
      ({ G, ppu } = fitGroup(data, stand, Z, w, h, { seed: s + t * 101, period, not: seen }));
      const once = Object.values(G.actors).filter((A) => A.who?.one).map((A) => A.cast);
      if (once.some((c) => seen.has(c))) continue;             // (only when everyone has been)
      const sil = silhouette(G), far = Math.min(data.canon.distinct * 2, ...seen.sils.map((q) => unlike(sil, q))), marks = Object.values(G.actors).flatMap((A) => A.who?.shield?.blazon ? ["blazon" + A.who.shield.blazon] : []), fresh = marks.filter((q) => !seen.has(q)).length;
      const score = far + notch(sil) * data.canon.notched + fresh * .02 - (G.faults ?? 0) * data.canon.faulted;
      if (!keep || score > keep.score) keep = { G, ppu, sil, marks, once, score };
      if (far >= data.canon.distinct && !G.faults && fresh === marks.length) break;
    }
    if (!keep) return { G, ppu, once: [], spent: true };     // (no one left who hasn't been)
    keep.marks.forEach((q) => seen.add(q)); keep.once.forEach((c) => seen.add(c));
    return keep;
  };
  const single = (x, y, w, h, { G, ppu }) => {
    const cx = x + w / 2 - (G.min + G.max) / 2 * ppu, base = y + h - h * .04;
    zoneClip(x, y, w, h);
    g.setTransform(ppu, 0, 0, -ppu, cx, base);
    paintPieces(g, G.pieces, tech, { ppu });
    g.restore(); g.setTransform(1, 0, 0, 1, 0, 0);
  };
  const run = (Z, x, y, w, h, s) => {
    let ppu = h * .94 / data.canon.man, L = layoutRun(data, Z, w / ppu, period, s);
    const tall = Math.max(0, ...(L?.groups ?? []).map((G) => G.height));
    if (tall > data.canon.top) { ppu *= data.canon.top / tall; L = layoutRun(data, Z, w / ppu, period, s); }   // (someone taller than a man: the whole band smaller, no head under the border)
    const base = y + h - h * .035;
    zoneClip(x, y, w, h);
    if (L) {
      let at = L.gap / 2;
      const r = stream(s, "filler"), step = [];
      for (const G of L.groups) {
        const gw = G.max - G.min, cx = at - G.min;
        g.setTransform(ppu, 0, 0, -ppu, x + cx * ppu, base);
        paintPieces(g, G.pieces, tech, { ppu });
        at += gw + L.gap; step.push(at - L.gap / 2);
      }
      const filler = (data.styles[period]?.fillers ?? []).filter(([gap]) => L.gap > gap).at(-1)?.[1];   // (what a period puts in a gap of a given width)
      if (filler) for (const q of step.slice(0, -1)) {
        g.setTransform(ppu, 0, 0, -ppu, x + q * ppu, base);
        paintPieces(g, fillerPieces(data.parts.fillers[filler], 0, 100, r), tech, { ppu });
      }
    }
    g.restore(); g.setTransform(1, 0, 0, 1, 0, 0);
    g.fillStyle = Tb.fg === T.ground ? Tb.bg ?? T.filler : Tb.fg; g.fillRect(x, base, w, Math.max(1, h * .012));
  };

  let y = 0;
  const kin = [...(spec.name ?? "")].reduce((a, c) => (a * 31 + c.charCodeAt(0)) % 9973, 0);     // (one seed on two paintings, two pictures)
  spec.zones.forEach((Z, i) => {
    const h = Z.h / total * H, y0 = Math.round(y), y1 = Math.round(y + h), zh = y1 - y0, s = seed * 131 + i + kin;
    y += h;
    if (Z.band) return drawBand(g, orn[Z.band.of ? Z.band.of[seed % Z.band.of.length] : Z.band], 0, y0, W, zh, Tb, orn, Z.squeeze);
    if (Z.solid) { g.fillStyle = inkFill; g.fillRect(0, y0, W, zh); return; }
    if (Z.panels) {
      if (spec.ink) { g.fillStyle = inkFill; g.fillRect(0, y0, W, zh); }
      const cell = W / Z.panels, pw = cell * (Z.width ?? .62), seen = Object.assign(new Set(), { sils: [] }), top = Z.top ? Math.round(zh * .13) : 0;
      const fits = [], order = Array.from({ length: Z.panels }, (_, k) => [stream(s, "order", k)(), k]).sort((a, b) => a[0] - b[0]);   // (drawn in no set order, or whoever is left over always lands on the last panel)
      for (const [, k] of order) { fits[k] = choose(Z, pw, zh - top, s + k * 17, k, s, seen); if (fits[k].sil) seen.sils.push(fits[k].sil); }
      const man = (f) => f.ppu * (data.scenes[f.G.name].scale ?? 1), mid = fits.map(man).sort((a, b) => a - b)[Z.panels >> 1];
      for (let k = 0; Z.even && k < Z.panels; k++) for (let t = 1; t < 7 && man(fits[k]) < mid / Z.even; t++) {   // (`even`: a panel far under the others draws again, handing back whoever it had; then no one's body is larger than this times the smallest, so a run keeps one scale)
        fits[k].once.forEach((c) => seen.delete(c));
        const f = choose(Z, pw, zh - top, s + k * 17 + t * 7001, k, s, seen), better = !f.spent && man(f) > man(fits[k]);
        (better ? fits[k] : f).once.forEach((c) => seen.delete(c));
        if (better) { seen.sils.splice(seen.sils.indexOf(fits[k].sil), +!!fits[k].sil, f.sil); fits[k] = f; }
        fits[k].once.forEach((c) => seen.add(c));
      }
      const most = Z.even ? Math.max(Math.min(...fits.map(man)), mid * (Z.floor ?? 0)) * Z.even : Infinity;   // (`floor`: one panel of someone lying, its length filling the width, doesn't shrink the rest with it)
      for (let k = 0; k < Z.panels; k++) {
        const px0 = Math.round((Z.at ? Z.at[k] * W : cell * (k + .5)) - pw / 2);
        g.save(); g.globalCompositeOperation = "destination-out"; g.fillRect(px0, y0, pw, zh); g.restore();
        if (Z.top) drawBand(g, orn[Z.top], px0, y0, pw, top, { ...Tb, bg: null });
        single(px0, y0 + top, pw, zh - top, { G: fits[k].G, ppu: Math.min(fits[k].ppu, most / (data.scenes[fits[k].G.name].scale ?? 1)) });
      }
      return;
    }
    if (Z.single) return single(0, y0, W, zh, choose(Z, W, zh, s));
    run(Z, 0, y0, W, zh, s);
  });
  if (spec.round) drawRing(g, orn[spec.round.band], W, H, spec.round, Tb, orn);
  paintGround(g, tech, W, H, spec.ground);
  return cv;
}
