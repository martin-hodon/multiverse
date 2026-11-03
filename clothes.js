// THE TAILOR: what a person wears, cut from flat sheets of cloth and laid on the body (docs/clothes.md).
//
// A garment (assets/clothes/*.json) is a list of COMPONENTS (assets/clothes/components/*.json) with parameters, and a
// component is a list of PIECES: each a sheet on a HOST (the torso, an arm, a leg, the head) between two LANDMARKS,
// closed round it or open over an arc, with an opening cut out of it (a neckline, a window), a band along its edge,
// dagged, pleated -- and cut from one of the garment's FABRICS (a pattern of the fabrics family in a palette of dyes).
// Every number may be an expression over the component's params and the host's landmarks, which are metres down the
// host from its top ("waist + 0.05" is five centimetres under the waist, "(elbow + wrist) / 2" mid-forearm).
//
// What the tailor hands the figure engine is of two kinds, decided by the piece and not by hand:
//   * WORN pieces follow the body: they become LAYERS on the body's own parts (skeleton.js `dress`), outermost
//     first, each in the part's own coordinates -- along its axis from its A end, round it from the figure's front --
//     with its fabric's repeat carried across the joints so a stripe runs on from the chest to the hips;
//   * STANDING pieces (a skirt, a cloak, a bell sleeve, a hood, a hat) are shells of their own: new parts, cut from
//     a cone or a ball, whose cloth is their layers and whose openings are holes.
// people.js builds the body and a FORM of it (the hosts: their parts, landmarks and girths) and asks `tailor`.
import { evalNum } from "./expr.js";
import { fetchAsset } from "./creatures.js";
import { registerPatterns, PALETTES } from "./patterns.js";
import { fabricIndex, periodOf, FOLD_TOP } from "./fabric.js";

// ---- the library ------------------------------------------------------------------------------------------------
registerPatterns({ fabrics: await fetchAsset("patterns/fabrics"), palettes: await fetchAsset("patterns/palettes") });
export const WARDROBE = await fetchAsset("clothes/wardrobe");
const LIB = new Map();                                         // "clothes/tunic", "clothes/components/sleeve" -> definition
async function load(path) {
  if (LIB.has(path)) return;
  const def = await fetchAsset(path);
  LIB.set(path, def);
  await Promise.all((def.use ?? []).map((u) => load(u.use)));
}
await Promise.all(Object.keys(WARDROBE.garments).map((g) => load("clothes/" + g)));
export const garmentDef = (name) => LIB.get(name.includes("/") ? name : "clothes/" + name);
// a definition edited live (the asset viewer): it and whatever it uses (already loaded: the library is)
export async function setClothes(path, def) { LIB.set(path, def); await Promise.all((def.use ?? []).map((u) => load(u.use))); }
export function setClothesNow(path, def) { LIB.set(path, def); }

// ---- colours of a fabric slot --------------------------------------------------------------------------------------
const hex = (c) => typeof c === "number" ? c : parseInt(String(c).replace("#", ""), 16);
// a fabric as the garment or the outfit gives it: { pattern, palette | colors } -> the engine's numbers
function fabricOf(f) {
  const pattern = f?.pattern ?? "fabrics/plain";
  const list = f?.colors ?? PALETTES[f?.palette ?? "undyed"] ?? PALETTES.undyed;
  const colors = [0, 1, 2, 3].map((k) => hex(list[k % list.length]));
  return { index: fabricIndex(pattern), period: periodOf(pattern), colors };
}

// ---- the pieces of a garment ------------------------------------------------------------------------------------
// a garment's `use` list, flattened to pieces with their component's params (the garment's over the component's)
function piecesOf(gdef, over = {}) {
  const out = [];
  const walk = (def, params, depth) => {
    if (depth > 4) throw new Error("clothes: components use each other too deep");
    const P = { ...(def.params ?? {}), ...params };
    for (const pc of def.pieces ?? []) out.push({ ...pc, P });
    for (const u of def.use ?? []) walk(LIB.get(u.use) ?? (() => { throw new Error(`clothes: no ${u.use}`); })(), { ...evalParams(u.params ?? {}, P) }, depth + 1);
  };
  walk(gdef, { ...(gdef.params ?? {}), ...over }, 0);
  return out;
}
// (a component's params given by its user may be expressions over the user's own)
function evalParams(ps, P) {
  const o = {};
  for (const [k, v] of Object.entries(ps)) o[k] = typeof v === "string" && !/^[a-z]+$/i.test(v) ? tryNum(v, P) : (typeof v === "string" && v in P ? P[v] : v);
  return o;
}
const tryNum = (v, P) => { try { return evalNum(v, P); } catch { return v; } };
// a piece's value: a param's value by name, else an expression over params and landmarks
const val = (v, P, marks, d) => {
  if (v === undefined || v === null) return d;
  if (typeof v === "number" || typeof v === "boolean") return v;
  if (typeof v === "string" && v in P && typeof P[v] !== "string") return P[v];
  if (typeof v === "string" && v in P) return val(P[v], P, marks, d);
  return evalNum(v, { ...P, ...marks });
};
const truthy = (v, P) => v === undefined || (typeof v === "string" ? !!P[v] : !!v);
// a piece's word (a param's value by name, else the word itself): `arms` true | "left" | "right"
const word = (v, P) => typeof v === "string" && v in P ? P[v] : v;
// round the body, degrees from the figure's front toward its left (-z: the layers' own angle) -- the sides by name
// (a param naming another param naming a side: a mantle's `edgeHigh` defaults to the shoulder it is worn `over`)
const SIDES = { front: 0, left: 90, back: 180, right: -90 };
const angleOf = (v, P, marks) => { const w = word(word(v, P), P); return typeof w === "string" && w in SIDES ? SIDES[w] : val(v, P, marks, 0); };

// ---- the form: what people.js tells the tailor about a body -------------------------------------------------------
// form = { torso: { parts: [{ id, top, bottom }], collar, half(y), flat, marks: { name: y } }, arms: [{ side, parts:
//   [{ id, len }], radius(d) }], legs: [...same], head: { id, hr }, feet: [ids], pose, h, S }
// A host's landmarks as the pieces see them: metres DOWN the host from its top.
function marksOf(form, host, side) {
  if (host === "torso") { const t = form.torso; return Object.fromEntries(Object.entries(t.marks).map(([k, y]) => [k, t.collar - y])); }
  if (host !== "arm" && host !== "leg") return {};           // (the feet, the neck, the head: a piece covers them whole)
  const limb = (host === "arm" ? form.arms : form.legs).find((l) => l.side === side);
  return limb.marks;
}

// ---- the tailor ---------------------------------------------------------------------------------------------------
// outfit.wear: [{ garment, fabrics: { slot: { pattern, palette | colors } }, params }], worn in layer order (the
// garment's `layer`). Returns { dress: Map(part id -> { layers }), parts: [standing parts], legsUnder: hem height or
// null (the legs a skirt covers are not drawn), armsUnder: the lowest edge of what hangs over the arms (a cloak) or null,
// skirts: [their parts], layersOf }.
export function tailor(form, outfit, { add, bone }) {
  // (an entry may say the LAYER it is worn at, `layer`: a peplos girded under its overfold, the belt laid on the bodice and
  //  the apoptygma falling over it -- at its own 5, round the overfold's cone, it held the cloth out below it as a tray)
  const wear = (outfit.wear ?? []).map((w, k) => { const def = garmentDef(w.garment); return { ...w, def: def && w.layer !== undefined ? { ...def, layer: w.layer } : def, k }; })
    .filter((w) => w.def && !(form.pose === "ride" && w.def.skirted));
  // OUTERMOST FIRST: the higher a garment's layer the further out; in one garment a later piece lies over an earlier
  wear.sort((a, b) => (b.def.layer ?? 2) - (a.def.layer ?? 2) || b.k - a.k);
  const dress = new Map();                                   // part id -> [layers], outermost first
  const layerOn = (id, L) => { if (!dress.has(id)) dress.set(id, []); dress.get(id).push(L); };
  const standing = [];                                       // [{ part, top, bottom (torso heights), layer }]
  const jobs = [];                                           // (the standing pieces, made once every garment is read)
  let legsUnder = null, armsUnder = null;
  const skirts = [];
  for (const w of wear) {
    const fab = {};
    const fabOf = (slot) => fab[slot] ??= fabricOf(w.fabrics?.[slot] ?? w.def.fabrics?.[slot] ?? w.def.fabrics?.main);
    const pieces = piecesOf(w.def, w.params ?? {});
    for (let pi = pieces.length - 1; pi >= 0; pi--) {        // (later pieces lie over earlier ones)
      const pc = pieces[pi], P = pc.P;
      if (!truthy(pc.if, P)) continue;
      if (pc.unless && truthy(pc.unless, P)) continue;
      const f = fabOf(pc.fabric ?? "main");
      const thick = val(pc.thick, P, {}, w.def.thick ?? .003 * (1 + (w.def.layer ?? 2) * .4));
      const base = { fabric: f.index, period: f.period, colors: f.colors, thick, pleats: val(pc.pleats, P, {}, 0),
                     wear: w.def.wear ?? 1, dags: val(pc.dags, P, {}, 0), band: val(pc.band, P, {}, 0), garmentLayer: w.def.layer ?? 2,
                     // (a CASCADE: the edges of its opening hanging in zigzag folds, [teeth out, one every so far down] metres)
                     ...(pc.cascade && val(pc.cascade[0], P, {}, 0) > 0 ? { cascade: [val(pc.cascade[0], P, {}, 0), val(pc.cascade[1], P, {}, .12)] } : {}) };
      // a HEM: a band of another fabric along the piece's lower edge (an embroidered border, a braid at a cuff)
      const hw = pc.hem ? val(pc.hem.width, P, {}, 0) : 0;
      // (it keeps the piece's pleats: it folds as the cloth does, and its lower edge waves with the hem -- shell.js foldPhase)
      const hem = hw > 0 ? (() => { const hf = fabOf(pc.hem.fabric ?? "trim"); return { ...base, fabric: hf.index, period: hf.period, colors: hf.colors, dags: 0, band: 0, width: hw, thick: base.thick * .5 }; })() : null;
      const kind = pc.kind ?? "wear";
      if (kind === "wear") {
        const sides = pc.on === "arm" || pc.on === "leg" ? (pc.side ? [pc.side] : ["L", "R"]) : [null];
        for (const side of sides) wearPiece(form, pc, P, side, base, layerOn, hem);
      } else jobs.push({ pc, P, base, w, hem, order: pi });
    }
  }
  // STANDING PIECES FROM THE SKIN OUT: each one hung round the torso clears the ones already hung under it (a mail
  // skirt over a gambeson's, a tabard's over both), whatever its own thickness would have made it
  jobs.sort((a, b) => (a.w.def.layer ?? 2) - (b.w.def.layer ?? 2) || a.w.k - b.w.k || a.order - b.order);
  // (a piece the next one of its garment hangs on from -- a hood's cape ending where its fall begins, a mantle's cape
  //  above its body -- is no hem: no wave, no dags, no border cut into that seam)
  const starts = new Set(jobs.map((j) => j.w.k + "|" + j.pc.on + "|" + String(j.pc.from).replace(/\s+/g, "")));
  for (const j of jobs) {
    const cont = starts.has(j.w.k + "|" + j.pc.on + "|" + String(j.pc.to).replace(/\s+/g, ""));
    const made = standPiece(form, cont ? { ...j.pc, seam: true } : j.pc, j.P, j.base, { add, bone }, j.w, j.hem, standing);
    if (!made) continue;
    standing.push(...made);
    for (const m of made) if (m.skirt) {
      skirts.push(m.part);
      legsUnder = legsUnder === null ? m.bottom : Math.min(legsUnder, m.bottom);
    }
    for (const m of made) if (m.arms) armsUnder = armsUnder === null ? m.bottom : Math.min(armsUnder, m.bottom);   // (a cloak, a mantle, a hood's fall: hung over the arms)
  }
  // PIECES HUNG END TO END (a hood's cape and its fall, a cloak's cape and its body) meet in ONE ring: the wider of
  // the two -- else the cape ends a hand's breadth inside the fall that hangs from it
  for (const a of standing) for (const b of standing) {
    if (a === b || !a.torso || !b.torso || a.garment !== b.garment || Math.abs(a.bottom - b.top) > .002) continue;
    const r = Math.max(a.part.size.r2, b.part.size.r);
    a.part.size.r2 = r; b.part.size.r = Math.max(b.part.size.r, r); b.part.size.r2 = Math.max(b.part.size.r2, r);
  }
  // A BELT OVER A SKIRT: whatever is worn OVER a standing piece on the torso (a belt round a kirtle's skirt, a
  // surcoat's hem over the kirtle) is laid on that piece too, where it reaches -- else the belt vanishes under the
  // skirt's top
  for (const st of standing) {
    if (!st.torso) continue;
    const over = new Map();                                  // (one per piece: its layers lie on several torso parts)
    for (const [id, Ls] of dress) {
      if (!form.torso.parts.some((p) => p.id === id)) continue;
      for (const L of Ls) if ((L.garmentLayer ?? 0) > st.layer && L.y0 !== undefined && !over.has(L.pid)) over.set(L.pid, L);
    }
    // (in the standing piece's own s: down its axis from its top, which hangs straight from its ring)
    const mine = [...over.values()].filter((L) => L.y1 < st.top && L.y0 > st.bottom)
      .map((L) => ({ ...L, s0: L.y0 >= st.top ? -1e3 : st.top - L.y0, s1: L.y1 <= st.bottom ? 1e3 : st.top - L.y1, vOffset: (form.torso.collar - st.top) - L.dTop }));
    st.part.dress.layers.unshift(...mine);
  }
  // WHAT CANNOT BE SEEN IS NOT KEPT: a layer an outer one covers everywhere on that part (the chemise under a
  // kirtle's bodice, lacing under a surcoat's front panel) is dropped -- the engine reads six at most
  for (const [id, Ls] of dress) {
    const kept = [];
    for (const L of Ls) if (!kept.some((O) => covers(O, L))) kept.push(L);
    dress.set(id, kept.slice(0, 6));
  }
  // ...NOR A WHOLE PIECE another covers: hung further out from at or above its top to at or below its hem, all round --
  // no wrap, no opening, no edge falling, no mouth the eye sees into (a tunica's skirt under a stola's to the feet).
  // `covered`: a carving leaves it out (statues.js), its cloth one with the stone of what covers it; standing proud of
  // that one's drape where its cone stood further out, its waistband came through the stola a shelf
  // (one of its layers so, down its whole length: what is laid over it -- a stola's stripes, a belt -- need not be)
  const whole = (st) => !st.part.open && st.part.dress.layers.some((L) => !L.wrap && !L.opening && !(L.edge?.[0] > 0) && L.s0 <= 0 && L.s1 >= st.part.clip.hi - 1e-3);
  standing.forEach((a, i) => {
    if (a.torso && standing.some((b, j) => j > i && b.torso && whole(b) && b.top >= a.top - 1e-3 && b.bottom <= a.bottom + 1e-3)) a.part.covered = true;
  });
  return { dress, legsUnder, armsUnder, skirts, standing };
}

// THE OUTERMOST SURFACE ROUND THE TORSO AND THE NECK, as the body and what the tailor dressed it in make it -- what is
// worn on top lies on it (jewelry.js neckFit: a necklace, a collar). (y, th): a height (from the feet) and an angle
// round from the figure's front (radians, toward +z) -> the distance from the torso's axis. It is the torso's oval
// (form.half across, its `flat` share of that front to back) and the neck's round, joined by the fillet the figure
// engine draws between them; lifted by every worn layer over the point (not where a neckline opens -- the same ball
// the shader cuts); and out to any standing shell hung round the torso there (a cape, a hood's cape, a cloak),
// oval as it is squashed -- the same ring the tailor hangs the next shell outside (standPiece `hung`).
export function outerSurface(form, worn) {
  // (the fillet between the neck and the shoulders: the figure engine bridges two parts with the larger of their blends)
  const t = form.torso, nr = form.neck.r, nTop = form.neck.top ?? t.collar + .1, kN = form.neck.k ?? .05 * form.S;
  const smax = (a, b, k) => { const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.max(a, b) + h * h * k * .25; };
  const oval = (r, sq, th) => r / Math.hypot(Math.cos(th) / sq, Math.sin(th));
  // the worn layers on the torso: each piece once (its first part's copy), its opening in heights
  const torsoL = [], seen = new Set();
  for (const tp of t.parts) for (const L of worn.dress.get(tp.id) ?? []) {
    if (L.y0 === undefined || seen.has(L.pid)) continue;
    seen.add(L.pid);
    const op = L.opening?.neckline ? { ...L.opening, kind: L.opening.neckline, yC: tp.top - L.opening.top } : null;
    torsoL.push({ y0: L.y0, y1: L.y1, thick: L.thick, wrap: L.wrap, op });
  }
  const neckThick = (worn.dress.get(form.neck.id) ?? []).reduce((s, L) => s + (L.thick ?? 0), 0);
  const inWrap = (w, th) => !w || Math.abs(((th - w[0] + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI) <= w[1];
  const reach = (op, th) => {
    const a = Math.abs(((th + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI);
    const f = op.kind === "scoop" ? Math.sqrt(Math.max(.5 + .5 * Math.cos(a), 0)) : op.kind === "v" ? Math.max(0, 1 - a / Math.max(op.half, .05))
            : op.kind === "square" ? 1 - Math.min(1, Math.max(0, (a - (op.half - .1)) / .2)) : op.kind === "boat" ? Math.sin(a) ** 2 : .5 + .5 * Math.cos(a);
    return op.base + op.back + (op.front - op.back) * f;
  };
  return (y, th) => {
    const h = t.half(y), rt = h > 0 ? oval(h, t.flat, th) : 0, rn = y <= nTop ? nr : 0;
    let r = rn > 0 && rt > 0 ? smax(rt, rn, kN) : Math.max(rt, rn);
    let lift = rn >= rt ? neckThick : 0;
    for (const L of torsoL) {
      if (y > L.y0 || y < L.y1 || !inWrap(L.wrap, th)) continue;
      if (L.op && Math.hypot(r, L.op.yC - y) < reach(L.op, th)) continue;
      lift += L.thick;
    }
    r += lift;
    for (const st of worn.standing) {
      if (!st.torso || y > st.top || y < st.bottom) continue;
      const k = (st.top - y) / Math.max(st.top - st.bottom, 1e-4), sz = st.part.size, rs = sz.r + (sz.r2 - sz.r) * k;
      r = Math.max(r, oval(rs, st.part.clip?.squash || 1, th) + (st.offZ ?? 0) * Math.sin(th) + .002);   // (set off toward one arm: nearer there)
    }
    return r;
  };
}

// does layer O cover layer L wherever L is on their part? O reaches over L's stretch, round all of L's arc, and has no
// hole there (a band has holes everywhere; a dagged hem at the bottom; a neckline only as far down as it reaches)
function covers(O, L) {
  if (O.band || O.s0 + (O.edge?.[0] ?? 0) > L.s0 || O.s1 < L.s1) return false;
  if (O.dags && O.s1 < 1e2) return false;
  if (O.wrap) {
    if (!L.wrap) return false;
    const d = Math.abs(((L.wrap[0] - O.wrap[0] + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI);
    if (d + L.wrap[1] > O.wrap[1]) return false;
  }
  const op = O.opening;
  if (op?.neckline) return L.s0 > op.top + op.base + Math.max(op.front, op.back);
  return !op;
}

// A WORN PIECE, laid on the parts of its host it reaches: each part gets the stretch of the sheet that lies on it,
// in its own coordinates (metres along its axis from its A end), the fabric's repeat carried on from the part above
function wearPiece(form, pc, P, side, base, layerOn, hem) {
  const marks = marksOf(form, pc.on, side);
  const d0 = val(pc.from, P, marks, 0), d1 = val(pc.to, P, marks, 1e3);
  if (!(d1 > d0)) return;
  if (hem) lay(form, pc, P, side, marks, Math.max(d0, d1 - hem.width), d1, d0, hem, layerOn, false);
  lay(form, pc, P, side, marks, d0, d1, d0, base, layerOn, true);
}
// one layer of a worn piece from d0 to d1 down its host (its fabric's repeat starting at `top`), on every part it reaches
let pieceId = 0;
function lay(form, pc, P, side, marks, d0, d1, top, base, layerOn, withOpening) {
  const pid = ++pieceId;
  const host = pc.on === "torso" ? form.torso.parts.map((p) => ({ id: p.id, off: form.torso.collar - p.top, len: p.top - p.bottom }))
             : pc.on === "arm" || pc.on === "leg" ? (() => { let o = 0; return (pc.on === "arm" ? form.arms : form.legs).find((l) => l.side === side).parts.map((p) => { const r = { id: p.id, off: o, len: p.len }; o += p.len; return r; }); })()
             : pc.on === "foot" ? form.feet.filter((f) => !side || f.endsWith(side)).map((id) => ({ id, off: 0, len: 1e3, whole: true }))
             : pc.on === "neck" ? [{ id: form.neck.id, off: 0, len: 1e3, whole: true }]
             : pc.on === "head" ? [{ id: form.head.id, off: 0, len: 1e3, whole: true }] : [];
  const girth = pc.on === "torso" ? form.torso.circumference : pc.on === "arm" ? 2 * Math.PI * form.arms[0].r : pc.on === "leg" ? 2 * Math.PI * form.legs[0].r : 0;
  const per = base.period, wrap = wrapOf(pc.wrap, P, marks);
  const repeats = wrap || !girth ? 0 : Math.max(1, Math.round(girth / per[0]));
  const op = withOpening ? openingOf(pc.opening, P, marks, form) : null;
  host.forEach((hp, k) => {
    if (hp.whole) { layerOn(hp.id, { ...base, s0: -1e3, s1: 1e3, wrap, repeats: 0, vOffset: 0 }); return; }
    const a = d0 - hp.off, b = d1 - hp.off;
    if (b < -.05 || a > hp.len + .05) return;
    const first = k === 0, last = k === host.length - 1;
    // (a piece that began on the part above, or begins at the host's very top, covers this part's top cap and the
    //  joint; one that goes on past it covers its far end -- the joints' strips belong to one part or the other)
    const s0 = (d0 <= 1e-4 && first) || (!first && a <= 0) ? -1e3 : a;
    const s1 = (!last && b >= hp.len) || (last && d1 >= 1e2) ? 1e3 : b;
    const L = { ...base, s0, s1, wrap, repeats, vOffset: hp.off - top, pid };
    if (pc.on === "torso") { L.y0 = form.torso.collar - d0; L.y1 = form.torso.collar - d1; L.dTop = top; }   // (its whole stretch, in heights: a skirt it lies over takes it too)
    if (op) L.opening = { ...op, top: op.top !== undefined ? op.top - hp.off : undefined, at: op.at !== undefined ? op.at - hp.off : undefined };
    layerOn(hp.id, L);
  });
}

// a piece's opening in the sheet's terms (host distances; wearPiece moves them into each part's own)
// (a NECKLINE is a ball round the collar point: its radius the neck's and a little ease, grown by `back` behind and
//  `front` before; `top` where the collar point lies down the host -- the collar itself unless it says)
function openingOf(o, P, marks, form) {
  if (!o || !truthy(o.if, P)) return null;
  const neck = typeof o.neckline === "string" && o.neckline in P ? P[o.neckline] : o.neckline;
  if (neck) {
    if (neck === "none") return null;
    return { neckline: neck, top: val(o.top, P, marks, 0), front: val(o.front, P, marks, .03), back: val(o.back, P, marks, .01),
             half: val(o.width, P, marks, 60) * Math.PI / 180, base: form.neck.r + val(o.ease, P, marks, .006) };
  }
  if (o.window) return { slot: !!o.slot, angle: val(o.window[0], P, marks, 0) * Math.PI / 180, at: val(o.window[1], P, marks, 0),
                         half: val(o.window[2], P, marks, 20) * Math.PI / 180, halfLength: val(o.window[3], P, marks, .1) };
  return null;
}

// A STANDING PIECE: a shell part of its own. `hang` -- a cone from a ring round its host down to its hem (a skirt, a
// cloak, a capelet from the torso; a bell sleeve from an arm); `cowl` -- a ball round the head cut open for the face
// (a hood, a coif); `crown`, `brim`, `cone` -- a hat's.
// FOLDS A HAND'S WIDTH APART (2026-10-30): a standing piece has its `pleats` folds round it at the least, and on a wide one
// one every FOLD_W metres round its hem -- crowded at a gathered top, spreading to the hem: a bell sleeve's nine round a
// lampshade's mouth were a hand and a half wide each, a smooth cone; a gown's skirt keeps its own. (The layer's word
// packs them under 64; its hem band waves with them.)
const FOLD_W = .14;
function foldsRound(layer, hem, r) {
  if (!(layer.pleats > 0)) return;
  layer.pleats = Math.min(63, Math.max(layer.pleats, Math.round(2 * Math.PI * r / FOLD_W)));
  if (hem) hem.pleats = layer.pleats;
}
const LAYER_TOP = -.25;   // (a standing piece's layers begin this far above its own top: its lid and waistband inside them)
function standPiece(form, pc, P, base, { add, bone }, w, hem, under = []) {
  const kind = pc.kind, id = (pc.id ?? w.def.id ?? w.garment) + (pc.name ? "_" + pc.name : "") + "_" + w.k;
  const wrap = wrapOf(pc.wrap, P, {});
  // AN EDGE THAT FALLS ROUND IT (`edge` [drop, high]): its top at its own top at `high` (degrees round, or a side by
  // name), `drop` metres lower opposite -- a mantle's edge from the shoulder it hangs on across the body under the other arm
  const edge = pc.edge && val(pc.edge[0], P, marksOf(form, pc.on), 0) > 0 ? [val(pc.edge[0], P, marksOf(form, pc.on), 0), angleOf(pc.edge[1], P, {}) * Math.PI / 180] : null;
  const layer = { ...base, s0: -1e3, s1: 1e3, wrap, vOffset: 0, repeats: 0, ...(edge ? { edge } : {}) };
  // (its hem band, if it has one, lies over the last `width` of it: `len` is the piece's own length down its axis)
  // (mouth: the piece ends at the garment's edge -- its hem band, its dags; a sleeve's piece ending at a joint has neither)
  // (a piece ending at the garment's edge -- a skirt's hem, a sleeve's mouth -- has its layers END there, `len` down it:
  //  so the folds know how far down they are and the hem waves with them and is dagged where it says -- shell.js
  //  foldPhase, layerIn; with no end of its own, at 1e3, a standing piece's folds were one depth all down it and its
  //  hem never waved. Its top stays open well above, LAYER_TOP: the waistband and the lid keep their cloth)
  const end = (len, mouth) => (len && mouth ? len : 1e3);
  const dress = (len, mouth = true) => ({ standing: true, layers: [...(hem && len && mouth ? [{ ...hem, s0: len - hem.width, s1: end(len, mouth), wrap, vOffset: 0, repeats: 0 }] : []),
                                                                  mouth ? { ...layer, s0: edge ? 0 : len ? LAYER_TOP : -1e3, s1: end(len, mouth) } : { ...layer, dags: 0 }] });
  const S = form.S, H = form.head.hr;
  if (kind === "hang" && pc.on === "torso") {
    const t = form.torso, marks = marksOf(form, "torso");
    const yT = t.collar - val(pc.from, P, marks, 0), yB = t.collar - val(pc.to, P, marks, 1);
    const len = Math.max(yT - yB, .04 * S);
    const ease = val(pc.ease, P, marks, .006);
    // the ring at its top stands clear of the torso there, and the cone widens at least as fast as the torso under it
    // (a skirt from the waist has the hips to pass)
    // (a cloak or a cape clears the ARMS too, hanging beside the torso down to the hands; `arms` "left" or "right" ONE
    //  of them -- a mantle over one shoulder, the other arm free outside it: its ring set off toward that arm, `offZ`
    //  across, by half what the arm adds to the torso's width at the armpit)
    const arms = word(pc.arms, P), one = arms === "left" || arms === "right";
    const offZ = one ? (arms === "right" ? 1 : -1) * (t.halfArms(t.collar - marks.armpit) - t.half(t.collar - marks.armpit)) / 2 : 0;
    const clear = one ? (y) => Math.max(t.half(y) + Math.abs(offZ), t.halfArms(y) - Math.abs(offZ)) : arms ? t.halfArms : t.half;
    let rTop = Math.max(pc.fromRadius !== undefined ? val(pc.fromRadius, P, marks, 0) * S : t.half(yT), arms ? clear(yT) : 0, form.neck.r) + ease + 2 * base.thick;
    let slope = val(pc.flare, P, marks, .2);
    // (oval, as the torso is: `squash` its depth against its width -- so it clears the torso's depth at that share)
    // (a stout trunk deeper than the oval -- people.js POT_CLEAR -- makes the oval ROUNDER, up to a circle (shell.js clamps
    //  a squash at 1), before it widens the ring: at the canon's squash a fat man's peplum stood out a hand past his hips)
    const sq = Math.max(val(pc.squash, P, marks, one ? .75 : arms ? .62 : .85), arms ? 0 : Math.min(1, t.flat));
    const depthNeed = (y) => t.half(y) * t.flat / sq;
    // (its top ring clears the torso's DEPTH there too -- a stout body's belly at a skirt's waist (people.js POT_CLEAR): the
    //  width alone left the depth to the flare, which then had to make up the belly in the first centimetre, a skirt out flat)
    if (pc.fromRadius === undefined) rTop = Math.max(rTop, depthNeed(yT) + ease + 2 * base.thick);
    // (and whatever already hangs round the torso there, a layer of cloth further out -- in its width and its depth)
    const hung = (y) => {
      let r = 0;
      for (const u of under) {
        if (!u.torso || y > u.top || y < u.bottom) continue;
        const k = (u.top - y) / Math.max(u.top - u.bottom, 1e-4), ru = u.part.size.r + (u.part.size.r2 - u.part.size.r) * k;
        // (the two rings' centres apart by their offsets: a himation's set off toward its shoulder clears a chiton's skirt
        //  on the far side too -- with the skirt's own offset alone, the skirt's flare came out through it under the free arm)
        r = Math.max(r, (ru + Math.abs((u.offZ ?? 0) - offZ) + 2 * base.thick) * Math.max(1, (u.part.clip.squash || 1) / sq));
      }
      return r;
    };
    // HOW IT CLEARS WHAT IS UNDER IT: `fit` "flare" (a cape from the neck, a kirtle's skirt hugging the waist) keeps
    // its ring and widens its flare; "ring" (a hood's fall, a cloak over the arms) keeps its drape and widens its ring
    // (the body as far as the hands or the torso go; the cloth under it as far as that goes -- a chiton's flared hem at
    //  the knee, below a mantle's hands, came out through it)
    const yBody = arms ? t.hands : t.bottom;
    const yLow = Math.max(yB, Math.min(yBody, ...under.filter((u) => u.torso).map((u) => u.bottom)));
    rTop = Math.max(rTop, hung(yT - 1e-4));
    let ring = rTop;
    // ("ring" keeps its drape over the BODY; the cloth under it, a hand's breadth below its top, it clears by its flare --
    //  widened whole for a flared chiton's hem, a himation stood off the chest all the way up)
    const fitRing = word(pc.fit, P) === "ring", below = [];
    for (let k = 1; k <= 32 && yLow < yT; k++) {             // (down to its own hem, or as far as what it clears goes)
      const y = yT - (yT - yLow) * k / 32, body = y >= yBody ? Math.max(clear(y), depthNeed(y)) + ease + 2 * base.thick : 0, h = hung(y);
      if (!fitRing) slope = Math.max(slope, (Math.max(body, h) - rTop) / (yT - y));
      else if (yT - y < .1 * S) ring = Math.max(ring, Math.max(body, h) - slope * (yT - y));
      else { ring = Math.max(ring, body - slope * (yT - y)); below.push([y, h]); }
    }
    for (const [y, h] of below) slope = Math.max(slope, (h - ring) / (yT - y));
    rTop = ring;
    const rHem = rTop + Math.min(slope, 6) * len;   // (a cut shell is a plain cone: it may be nearly flat, a cape over the shoulders)
    if (pc.opening) layer.opening = openingOf(pc.opening, P, Object.fromEntries(Object.entries(marks).map(([k, v]) => [k, v - (t.collar - yT)])));
    // (hung from the HIPS when it starts at the waist or below -- a skirt; from the TRUNK above them when it starts higher -- a
    // cape, a cloak, a tabard -- so it bends and turns with the shoulders it lies on: the two frames are one at rest)
    const host = yT > form.torso.marks.waist + 1e-3 ? form.torso.upperFrom ?? form.torso.hangFrom : form.torso.hangFrom;
    // DRAPED over the legs (`cling`: the share of the cone's excess over them it takes in -- shell.js CLING), clear of them
    // by its ease and of whatever clings under it by that one's; and anything hung over a draped piece is draped too, if
    // only to clear it (cling 0: its cone kept, pushed out only where what is under it is -- a stride under a toga); never
    // clinging closer than what is under it, or it would fall in through it (what hangs on down over the legs, where it
    // clings: a cape over the shoulders, a peplos's overfold to the hips do not hold it out; a skirt there that keeps its
    // own cone keeps this one's too). Hung over the ARMS (a mantle), it is draped over the upper arms it covers as over
    // the legs: the rig's "L" arm is at +z
    const cling = val(pc.cling, P, marks, 0), clingUnder = under.filter((u) => u.torso && u.part.cling);
    const holds = under.filter((u) => u.torso && u.bottom < t.bottom && u.top > yB);   // (under it: a gown's skirt is not under a cape)
    const clingEase = ease + 2 * base.thick + Math.max(0, ...holds.filter((u) => u.part.cling).map((u) => u.part.cling.ease));
    const overArms = form.arms.filter((l) => arms === true || arms === (l.side === "L" ? "right" : "left")).map((l) => l.parts[0].id);
    // (the legs in their four slots -- shell.js reads them there -- then the arms it covers; hung over the arms, the CHEST
    //  it hangs from too: a mantle lies on the chest and the back and falls from them, not a cone standing off the
    //  shoulders -- the cape's was a millstone's brim round them)
    // (its cling never more than what it hangs over clings, or it went in through that one's cloth -- `want`: its own,
    //  carved in stone with what holds it out drawn as close, statues.js)
    // (and the TRUNK it hangs over below that -- `trunk`: the belly, the hips -- for slots left free: statues.js, an arm
    //  raised out of a mantle drawn close)
    const legSlots = [0, 1, 2, 3].map((i) => form.legs.flatMap((l) => l.parts.map((q) => q.id))[i] ?? null);
    foldsRound(layer, hem, rHem);
    // (its ROOM: how far in its cone may go anywhere down it before it meets the body or the cloth under it -- carved, a
    //  fold is cut no deeper, shell.js dressFold: an overfold's valleys over the skirt let the skirt through. Counted at
    //  the folds' full depth: they are shallower toward the top, FOLD_TOP of it there, where a cape sits on the shoulders.
    //  Clinging, it lies where the drape lays it, its cone no measure: unbounded; over a draped piece at cling 0 it keeps
    //  its cone, pushed out where that one reaches it -- there its ease apart)
    if (!(cling > 0)) {
      let room = clingUnder.length ? clingEase - base.thick : 1e3;
      for (let k = 0; k <= 32; k++) {
        const y = yT - (yT - yB) * k / 32, need = Math.max(y >= yBody ? Math.max(clear(y), depthNeed(y)) + ease : 0, hung(y) - 2 * base.thick);
        const tF = (yT - y - LAYER_TOP) / (len - LAYER_TOP);
        if (need > 0) room = Math.min(room, (rTop + Math.min(slope, 6) * (yT - y) - need - base.thick) / (FOLD_TOP + (1 - FOLD_TOP) * tF));
      }
      if (room < 1e3) layer.room = hem ? (hem.room = Math.max(room, 0)) : Math.max(room, 0);
    }
    // (and what it is draped over but not held out by -- a peplos's overfold to the hips under a himation -- lies OVER
    //  its cloth there: that one's folds are not cut, or each valley showed this cloth through it, a row of teeth)
    if (cling > 0) for (const u of under) if (u.torso && u.top > yB && !holds.includes(u)) for (const L of u.part.dress?.layers ?? []) L.room = 0;
    const part = bone(id, host, [0, yT - form.torso.hangY, offZ], [0, -1, 0], len, rTop, rHem, {
      ...((cling > 0 || clingUnder.length) && form.legs?.length ? { cling: { k: Math.min(cling, 1, ...holds.map((u) => u.part.cling?.k ?? 0)), want: Math.min(cling, 1), holds: holds.map((u) => u.part.id), ease: clingEase,
                                                                             trunk: form.torso.parts.filter((q) => q.id !== host && q.bottom < yT && q.top > yB).map((q) => q.id),
                                                                             over: [...legSlots, ...overArms, ...(arms ? [host] : [])] } } : {}),
      color: base.colors[0], clip: { lo: 0, hi: len, lid: pc.lid !== false, squash: sq }, frame: "body",
      // (`open`: its hem a MOUTH the eye sees into -- a cape's over the arms: carved, it stays open, statues.js -- closed,
      //  a cape's hem was a millstone round the shoulders, a disc of stone on the upper arms)
      ...(pc.open ? { open: true } : {}),
      anim: pc.swing === false ? undefined : { axis: "z", deg: 4, speed: .8, phase: -.7, amp: true, sway: 3 }, dress: dress(len, !pc.seam),
      trail: pc.trail ? val(pc.trail, P, marks, 0) * Math.PI / 180 : 0,   // (swept back as its wearer goes: skeleton.js TRAIL)
      // (a panel beside a cloak's opening: lifted by the arm on its side as it swings forward -- skeleton.js LIFT; its
      //  side, the wrap's middle: +z, the rig's "L")
      ...(pc.follow && wrap ? { follow: { part: "arm" + (Math.sin(wrap[0]) > 0 ? "L" : "R"), k: val(pc.follow, P, marks, 1) } } : {}) });
    layer.repeats = layer.wrap ? 0 : Math.max(1, Math.round(2 * Math.PI * (rTop + rHem) / 2 / base.period[0]));
    return [{ part, torso: true, top: yT, bottom: yB, layer: w.def.layer ?? 2, skirt: !!pc.skirt, arms: !!arms, garment: w.k, offZ, lap: !!pc.lap }];
  }
  if (kind === "hang" && pc.on === "arm") {
    return (pc.side ? [pc.side] : ["L", "R"]).map((side) => {
      const limb = form.arms.find((l) => l.side === side), marks = limb.marks;
      const d0 = val(pc.from, P, marks, 0), d1 = val(pc.to, P, marks, 1), len = Math.max(d1 - d0, .03 * S);
      const r0 = limb.radius(d0) + val(pc.ease, P, marks, .004) + base.thick, fl = val(pc.flare, P, marks, .3), rAt = (d) => r0 + fl * (d - d0);
      foldsRound(layer, hem, rAt(d1));
      // ONE PIECE A BONE: a sleeve from the shoulder past the elbow is a cone on the upper arm and another on the forearm,
      // the radius running on unbroken from one to the next (a bell sleeve's flare continues) -- hung on the upper arm
      // alone, the forearm bent out of it at the elbow and stuck out through its side. Each piece but the last reaches
      // a little past its joint (a third of its radius there), so a bent elbow stays covered.
      // (loose cloth does not bend at the wrist: past the forearm it hangs on from it -- the hand's length its own)
      const hand = limb.parts.at(-1), bones = limb.parts.slice(0, -1).map((p, i, a) => i === a.length - 1 ? { ...p, len: p.len + hand.len } : p);
      const out = [];
      let o = 0;
      for (const p of bones) {
        const a = Math.max(d0, o), e = Math.min(d0 + len, o + p.len);
        if (e > a + 1e-4) {
          const last = d0 + len <= o + p.len + 1e-6 || p === bones.at(-1), L =   // (a sleeve may run on past the limb's end)
            (e - a) + (last ? 0 : rAt(e) * .33);
          const part = bone(id + side + (out.length ? out.length : ""), p.id, [0, -(a - o), 0], [0, -1, 0], L, rAt(a), rAt(a + L),
                            { color: base.colors[0], clip: { lo: 0, hi: L }, dress: dress(L, last),
                              sag: last ? Math.max(0, Math.atan(fl) - .08) : 0, fall: true, open: last });   // (the mouth sags with gravity -- skeleton.js; a margin for the arm's own girth. Every piece of it FALLS off a raised arm: a dalmatica's upper sleeve too)
          // (`open`: its far end is a MOUTH the eye sees into -- carved, statues.js leaves it open, the hollow in shade)
          out.push({ part, top: 0, bottom: 0, layer: w.def.layer ?? 2 });
        }
        o += p.len;
      }
      return out;
    }).flat();
  }
  if (kind === "cowl") {   // a ball round the head (head radii), cut open at the face by a plane through `cut` square to `axis`
    const c = (pc.centre ?? [-.12, .05]).map((v) => val(v, P, {}, 0) * H), R = val(pc.radius, P, {}, 1.38) * H;
    const ax = pc.axis ?? [-1, -.3, 0], cut = (pc.cut ?? [.55, 0]).map((v) => val(v, P, {}, 0) * H);
    const n = norm(ax), lo = (cut[0] - c[0]) * n[0] + (cut[1] - c[1]) * n[1];
    // (`length` head radii and `taper`: drawn out behind the head along the axis, narrowing -- a chaperon's soft point at
    //  the back instead of a ball round the head)
    const len = Math.max(.01, val(pc.length, P, {}, 0) * H), r2 = R * val(pc.taper, P, {}, 1);
    const part = bone(id, form.head.id, [c[0], c[1], 0], n, len, R, r2, { color: base.colors[0], clip: { lo, hi: 1e4 }, dress: dress() });
    return [{ part, top: 0, bottom: 0, layer: w.def.layer ?? 2 }];
  }
  if (kind === "crown") {  // a hat's crown: a round cone from above the head down to the brim's height, its top closed (`x`: its middle forward of the head's)
    const top = val(pc.top, P, {}, 1.2), bot = val(pc.bottom, P, {}, .25), len = (top - bot) * H;
    const part = bone(id, form.head.id, [val(pc.x, P, {}, 0) * H, top * H, 0], [0, -1, 0], len, val(pc.rTop, P, {}, .98) * H, val(pc.rBottom, P, {}, 1.08) * H,
                      { color: base.colors[0], clip: { lo: 0, hi: len, solid: true }, dress: dress() });
    return [{ part, top: 0, bottom: 0, layer: w.def.layer ?? 2 }];
  }
  if (kind === "brim") {   // a ball cut to a thin slab: a disc -- level at `at`, or square to `axis` round `centre` [x, y] (head radii: a crest, [0, 0, 1])
    const y = val(pc.at, P, {}, .3) * H, R = val(pc.radius, P, {}, 2.4) * H, t = val(pc.thickness, P, {}, .05) * H;
    const c = pc.centre ? pc.centre.map((v) => val(v, P, {}, 0) * H) : [0, y];
    const part = bone(id, form.head.id, [c[0], c[1], 0], pc.axis ? norm(pc.axis) : [0, -1, 0], .01, R, R, { color: base.colors[0], clip: { lo: -t, hi: t, solid: true }, dress: dress() });
    return [{ part, top: 0, bottom: 0, layer: w.def.layer ?? 2 }];
  }
  if (kind === "cone") {   // a pointed crown's tip
    const at = (pc.at ?? [-.1, .45]).map((v) => val(v, P, {}, 0) * H), len = val(pc.length, P, {}, 2.1) * H;
    const tipOf = (i, pos, dir) => ({ part: bone(id + (i || ""), form.head.id, pos, dir, len, val(pc.radius, P, {}, 1) * H, val(pc.tip, P, {}, .06) * H,
                                                  { color: base.colors[0], clip: { lo: 0, hi: 1e4, solid: true }, dress: dress() }), top: 0, bottom: 0, layer: w.def.layer ?? 2 });
    // (`around`: n of them in a ring `ring` head radii round the head's upright through `at`, the first in front, each
    //  leaning `out` from the upright -- a crown's points)
    if (!pc.around) return [tipOf(0, [at[0], at[1], 0], pc.dir ?? [-.12, 1, 0])];
    const n = Math.round(val(pc.around, P, {}, 4)), R = val(pc.ring, P, {}, 1) * H, out = val(pc.out, P, {}, 0);
    return Array.from({ length: n }, (_, i) => {
      const a = 2 * Math.PI * i / n, c = Math.cos(a), sn = Math.sin(a);
      return tipOf(i, [at[0] + R * c, at[1], R * sn], [out * c, 1, out * sn]);
    });
  }
  return null;
}
const norm = (v) => { const l = Math.hypot(...v) || 1; return v.map((x) => x / l); };
// an open piece's arc, [centre, span] in degrees (either may be a param or an expression) -> [centre, half-width] radians
const wrapOf = (w, P, marks) => w ? [angleOf(w[0], P, marks) * Math.PI / 180, val(w[1], P, marks, 360) * Math.PI / 360] : null;

// ---- the wardrobe: dressing a villager ------------------------------------------------------------------------------
// WARDROBE.people[kind]: a list of OUTFITS, each { weight, wear: [{ garment, p (chance), fabrics: { slot: [choices] } }] }
// -- a choice is "pattern:palette" or { pattern, palette }; `garment` may be a list (one of them). Drawn from the
// person's own seeded stream `r`, so an outfit never moves the body's draws.
// `style`: another time and place's dress (the wardrobe's `styles`: greek, roman, chinese, gothic) instead of the village's
// `only`: the outfits' names it may draw from (where any of them is in the list); `full`: every garment of it worn, none
// left to its chance (a statue's: carved in the whole of it -- a citizen's toga, a matron's palla); `avoid`: palettes not
// drawn where a choice has others (a painted statue's: its drapery dyed, not undyed wool -- statuary.json `paint`)
export function drawOutfit(kind, r, { female = kind === "woman", style = null, work = false, only = null, full = false, avoid = null } = {}) {
  const pick = (a) => a[Math.floor(r() * a.length)];
  const dyed = (cs) => { const k = avoid ? cs.filter((c) => !avoid.includes(typeof c === "string" ? c.split(":")[1] : c.palette)) : cs; return k.length ? k : cs; };
  const byWeight = (list) => { const tot = list.reduce((t, o) => t + (o.weight ?? 1), 0); let e = r() * tot; for (const o of list) if ((e -= o.weight ?? 1) <= 0) return o; return list[list.length - 1]; };
  const key = kind.startsWith("child") ? (female ? "girl" : "boy") : kind;
  const lists = (style && WARDROBE.styles?.[style]) || WARDROBE.people;
  // (an outfit marked `statue` -- a hero's mantle alone, a nude -- is carved, never worn: drawn only where a statue's dress
  //  names it, statuary.json)
  const pool = lists[key] ?? lists.man ?? WARDROBE.people.man, listed = pool.filter((o) => !o.statue), allowed = only ? pool.filter((o) => only.includes(o.name)) : [];
  const all = allowed.length ? allowed : listed;
  // (one at work wears what works: the list's outfits marked `work`, if it has any -- never a lady's gown in a field)
  const working = work ? all.filter((o) => o.work) : [];
  const outfit = byWeight(working.length ? working : all);
  const wear = [];
  for (const g of outfit.wear) {
    if (r() > (full ? 1 : g.p ?? 1)) continue;
    const garment = Array.isArray(g.garment) ? pick(g.garment) : g.garment;
    const choice = (c) => typeof c === "string" ? { pattern: "fabrics/" + c.split(":")[0], palette: c.split(":")[1] } : c;
    const fabrics = Object.fromEntries(Object.entries(g.fabrics ?? {}).map(([slot, cs]) => [slot, choice(pick(dyed(cs)))]));
    // (a param given as a list is drawn from it: a hem band or none, and how wide -- only those draw, so a garment
    //  without one keeps the stream of choices it had)
    const params = Object.fromEntries(Object.entries(g.params ?? {}).map(([k, v]) => [k, Array.isArray(v) ? pick(v) : v]));
    wear.push({ garment, fabrics, params, ...(g.layer !== undefined ? { layer: g.layer } : {}) });   // (`layer`: tailor)
  }
  return { name: outfit.name, wear, ...(outfit.hair ? { hair: outfit.hair } : {}), ...(outfit.beard ? { beard: outfit.beard } : {}) };   // (an outfit's own hair and beard: a Buddha's ushnisha, beardless)
}
// a named outfit of the wardrobe (a guard's kit, a beast-man's), dressed as it stands (first choices)
export function namedOutfit(name) {
  const o = WARDROBE.outfits?.[name];
  if (!o) throw new Error(`clothes: no outfit "${name}"`);
  const choice = (c) => typeof c === "string" ? { pattern: "fabrics/" + c.split(":")[0], palette: c.split(":")[1] } : c;
  return { name, wear: o.wear.map((g) => ({ garment: g.garment, params: g.params ?? {}, ...(g.layer !== undefined ? { layer: g.layer } : {}), fabrics: Object.fromEntries(Object.entries(g.fabrics ?? {}).map(([s, cs]) => [s, choice(Array.isArray(cs) ? cs[0] : cs)])) })) };
}
