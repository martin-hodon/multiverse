// CLOTH CLIPPING: does a limb come through a garment that hangs round it -- a knee out through a skirt, a hand out of
// the side of a cloak, a forearm through a bell sleeve? (docs/clothes.md "Checking for clipping")
//
// Every HANGING piece (clothes.js standPiece `hang`: a cut cone from clip lo to hi down its axis, oval front to back --
// its `squash` along the figure's forward -- and perhaps round only part of its circle, its `wrap`) is tested against
// every limb that is drawn (not a bone, within its own clip), as the engines draw both: the limb a round cone between
// its ends, thickened by the cloth worn on it; the piece its cone, its angle round the axis counted from the figure's
// forward as shell.js counts it. A limb's surface past the cloth -- out through it from inside ("out"), or into it from
// outside ("in") -- by more than `tol` is a clip; but not where another hanging piece covers that point of the limb
// (a thigh inside the skirt a sleeve hangs against: nobody sees it), nor at the joint a piece starts from, where it
// always meets the bone above (bodycheck.js skips its joints the same way).
//
//   const pose = poseParts(def, state, t)        // writeAnimal on a stand-in: { parts, A, B } (each part's two ends)
//   clothClips(def, pose, { tol })               -> [{ limb, piece, depth, side: "out" | "in" }]  (part ids, metres)
//   CLIP_STATES                                  // the motions a person is checked in: standing, walking, running, gestures
//
// THE HAIR UNDER A HOOD OR A HAT: the mesh head's hair (heads.js: built at the canon's size, placed by headMatrix as the
// game draws it) against the pieces standing on the head -- a hood's cowl (a ball, cut open at the face: hair in the
// opening shows as it should), a hat's crown (a cone, its top closed). A hair point outside the cloth where the cloth
// is -- out through the cowl, through the crown's side or its top -- by more than `tol` shows through it. Both ride
// the head, so one pose tells.
//   hairClips(def, pose, { tol })                -> [{ piece, depth, share }]  (metres; the share of hair points out)
import * as THREE from "three";
import { compileDef, writeAnimal, CYCLES } from "./skeleton.js";
import { GESTURES } from "./people.js";
import { buildFace, faceShape, headMatrix, SHADE } from "./heads.js";
import { ASSETS } from "./catalogue.js";

const LIMB = /^(arm|fore|hand|leg|shin|foot)[LR]$/;
const UP = new THREE.Vector3(0, 1, 0);

// THE MOTIONS: standing; a walk's and a run's stride at eight points of its cycle; every working gesture at eight
// moments of two seconds (crouching where the gesture crouches: compileDef `crouch`)
export const CLIP_STATES = [
  { name: "stand", an: { amp: 0 }, t: 0 },
  ...[0, 1, 2, 3, 4, 5, 6, 7].map((k) => ({ name: "walk", an: { amp: 1, run: 0, animT: k / 8 / CYCLES }, t: 0 })),
  ...[0, 1, 2, 3, 4, 5, 6, 7].map((k) => ({ name: "run", an: { amp: 1, run: 1, animT: k / 8 / CYCLES }, t: 0 })),
  ...Object.keys(GESTURES).flatMap((g) => [0, 1, 2, 3, 4, 5, 6, 7].map((k) => ({ name: g, an: { amp: 0, work: 1, gesture: g }, t: k / 4 }))),
];

export function poseParts(def, state = {}, t = 0) {
  const parts = compileDef(def), n = parts.length;
  const A = new Float32Array(n * 3), B = new Float32Array(n * 3), C = new Float32Array(n * 3);
  writeAnimal({ parts, position: new THREE.Vector3(), rotY: 0, base: 0, ...state }, t, A, B, C);
  return { parts, A, B };
}

// what of a figure is tested: its drawn limbs and its hanging pieces (from the person's def, once)
function testedOf(def, parts) {
  if (def._clipTested) return def._clipTested;
  const limbs = [], pieces = [];
  def.parts.forEach((p, i) => {
    const c = parts[i].clip;
    if (LIMB.test(p.id) && !p.bone) limbs.push({ i, id: p.id, lo: c ? c[0] : -1e4, hi: c ? c[1] : 1e4,
      thick: (p.dress?.layers ?? []).reduce((s, L) => s + (L.thick ?? 0), 0) });
    else if (p.dress?.standing && c && c[1] < 50)   // (a hanging cone: its clip ends at its hem -- not a hood's ball or a hat)
      pieces.push({ i, id: p.id, lo: c[0], hi: c[1], sq: c[3] || 1, wrap: p.dress.layers.at(-1)?.wrap ?? null,
                    joint: def.parts.find((q) => q.id === p.parent)?.parent ?? null });   // (the bone above its host: a forearm's sleeve, the upper arm)
  });
  return (def._clipTested = { limbs, pieces });
}

const _p = new THREE.Vector3(), _q = new THREE.Vector3(), _fw = new THREE.Vector3(), _la = new THREE.Vector3(), _lb = new THREE.Vector3();
const SAMPLES = 9;   // along each limb

// a piece as posed: its axis, length, radii and the frame its angle is counted in
function frameOf(pc, parts, A, B) {
  const a = new THREE.Vector3().fromArray(A, pc.i * 3), ax = new THREE.Vector3().fromArray(B, pc.i * 3).sub(a), L = ax.length();
  if (L < 1e-4) return null;
  ax.divideScalar(L);
  const f = _fw.clone().addScaledVector(ax, -_fw.dot(ax)).normalize(), l = new THREE.Vector3().crossVectors(f, UP);
  l.addScaledVector(ax, -l.dot(ax)).normalize();
  const r1 = parts[pc.i].r1;
  return { pc, a, ax, L, f, l, r1, r2: parts[pc.i].r2 >= 0 ? parts[pc.i].r2 : r1 };
}
// a point against a piece: null where the piece is not (above or below it, or in its opening), else how far the point
// is from its axis (d) and how far its cloth is (rho), in the point's direction
function against(F, p) {
  const pc = F.pc, s = _q.subVectors(p, F.a).dot(F.ax);
  if (s < Math.max(0, pc.lo) || s > Math.min(F.L, pc.hi)) return null;
  _q.addScaledVector(F.ax, -s);
  const th = Math.atan2(_q.dot(F.l), _q.dot(F.f));
  if (pc.wrap && Math.abs(((th - pc.wrap[0] + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI) > pc.wrap[1]) return null;
  return { d: _q.length(), rho: (F.r1 + (F.r2 - F.r1) * s / F.L) / Math.hypot(Math.cos(th) / pc.sq, Math.sin(th)) };
}

export function clothClips(def, { parts, A, B }, { tol = .01 } = {}) {
  const { limbs, pieces } = testedOf(def, parts), out = [];
  _fw.fromArray(B, 0).sub(_la.fromArray(A, 0)).normalize();   // (the root's drawn axis: the figure's forward)
  const frames = pieces.map((pc) => frameOf(pc, parts, A, B)).filter(Boolean);
  for (const F of frames) for (const lb of limbs) {
    _la.fromArray(A, lb.i * 3); _lb.fromArray(B, lb.i * 3);
    const len = _la.distanceTo(_lb), q1 = parts[lb.i].r1, q2 = parts[lb.i].r2 >= 0 ? parts[lb.i].r2 : q1;
    let worst = 0, side = "";
    for (let k = 0; k < SAMPLES; k++) {
      const u = k / (SAMPLES - 1);
      if (u * len < lb.lo || u * len > lb.hi) continue;   // (a part of the limb not drawn)
      _p.lerpVectors(_la, _lb, u);
      if (lb.id === F.pc.joint && _p.distanceTo(F.a) < F.r1 + q1 * 2) continue;   // (at the joint the piece starts from: it always meets the bone above there -- the elbow in a forearm's sleeve)
      const h = against(F, _p);
      if (!h) continue;
      const r = q1 + (q2 - q1) * u + lb.thick, depth = h.d < h.rho ? h.d + r - h.rho : h.rho - (h.d - r);
      if (depth <= worst) continue;
      // (unseen: inside another hanging piece -- a thigh in the skirt a sleeve hangs against, an upper arm in its own
      //  sleeve where the forearm's crosses it at a bent elbow)
      if (frames.some((G) => G !== F && (() => { const g = against(G, _p); return g && g.d < g.rho; })())) continue;
      worst = depth; side = h.d < h.rho ? "out" : "in";
    }
    if (worst > tol) out.push({ limb: lb.id, piece: F.pc.id, depth: worst, side });
  }
  return out;
}

// a face's hair as points, at the canon's size (by its shape: one build for every person who has it)
const hairOf = new Map();
function hairPoints(face) {
  const sh = faceShape(face), key = JSON.stringify(sh);
  if (!hairOf.has(key)) {
    const built = buildFace(sh, ASSETS, ASSETS.get("items/materials")?.materials ?? {}, SHADE), pts = [];
    for (const g of built.groups.values()) if ([...g.roles].some((r) => /hair/i.test(r))) pts.push(...g.pos);
    hairOf.set(key, new Float32Array(pts));
  }
  return hairOf.get(key);
}

const _h = new THREE.Vector3(), _ha = new THREE.Vector3(), _hx = new THREE.Vector3(), _hp = new THREE.Vector3(), _hi = new THREE.Vector3(), _M = new THREE.Matrix4();
export function hairClips(def, { parts, A, B }, { tol = .005 } = {}) {
  const f = def.face;
  if (!f || f.head < 0 || f.gaze < 0) return [];
  // every standing piece covers what lies inside it (a hood's fall over the nape too); those on the head are checked
  const covers = def.parts.flatMap((p, i) => {
    const c = parts[i].clip;
    const ball = Math.abs(parts[i].r1 - parts[i].r2) < 1e-6;   // (a cowl: a hood, a cap, a turban -- its cut, lo, may lie behind its centre)
    if (!p.dress?.standing || !c || c[1] - c[0] < .05) return [];   // (a brim: a slab a few cm thick, no cover)
    return [{ i, id: p.id, head: p.parent === "head", ball, lo: c[0], hi: c[1], r1: parts[i].r1, r2: parts[i].r2 >= 0 ? parts[i].r2 : parts[i].r1 }];
  });
  const hats = covers.filter((h) => h.head);
  if (!hats.length) return [];
  const pts = hairPoints(f), n = pts.length / 3;
  if (!n) return [];
  const g = (k, X) => [X[k * 3], X[k * 3 + 1], X[k * 3 + 2]];
  headMatrix(g(f.head, A), g(f.head, B), g(f.gaze, A), g(f.gaze, B), 0, f.hr, _M);
  for (const h of covers) { h.a = new THREE.Vector3().fromArray(A, h.i * 3); h.x = new THREE.Vector3().fromArray(B, h.i * 3).sub(h.a); h.L = h.x.length(); h.x.divideScalar(h.L || 1); }
  // (a point inside another piece is hidden by it -- the hair through an official's tall cap is inside his turban)
  const inside = (o, P) => { _hi.copy(P).sub(o.a); const s = _hi.dot(o.x);
    if (o.ball) return s >= o.lo && _hi.length() < o.r1;
    return s >= o.lo && s <= Math.min(o.hi, o.L) && Math.sqrt(Math.max(0, _hi.lengthSq() - s * s)) < o.r1 + (o.r2 - o.r1) * Math.max(0, s) / (o.L || 1); };
  const out = [];
  for (const h of hats) {
    if (!h.ball && h.hi > 50) continue;   // (a pointed crown's tip: above the head, nothing under it)
    _ha.copy(h.a); _hx.copy(h.x);
    const L = h.L;
    let worst = 0, nOut = 0, at = null;
    for (let k = 0; k < n; k++) {
      _hp.set(pts[k * 3], pts[k * 3 + 1], pts[k * 3 + 2]).applyMatrix4(_M);
      _h.copy(_hp).sub(_ha);
      const s = _h.dot(_hx);
      let depth = 0;
      if (h.ball) { if (s >= h.lo) depth = _h.length() - h.r1; }   // (in the face's opening: as it should be)
      else if (s <= h.hi) {
        const rad = Math.sqrt(Math.max(0, _h.lengthSq() - s * s)), rho = h.r1 + (h.r2 - h.r1) * Math.max(0, s) / (L || 1);
        depth = s < h.lo ? (rad < h.r1 ? h.lo - s : 0) : rad - rho;   // (over the closed top, or through the side)
      }
      if (depth > tol && !covers.some((o) => o !== h && inside(o, _hp))) { nOut++; if (depth > worst) { worst = depth; at = [s, Math.sqrt(Math.max(0, _h.lengthSq() - s * s))]; } }
    }
    if (nOut) out.push({ piece: h.id, depth: worst, share: nOut / n, at, lo: h.lo, hi: Math.min(h.hi, L), r: [h.r1, h.r2], others: covers.filter((o) => o !== h).map((o) => `${o.id}${o.ball ? " ball" : ""} ${o.lo.toFixed(3)}..${Math.min(o.hi, o.L).toFixed(3)} r ${o.r1.toFixed(3)}`) });   // (at: the worst point's [along the piece, out from its axis], metres)
  }
  return out;
}
