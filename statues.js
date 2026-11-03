// STATUES (2026-10-04): figures CARVED -- the people engine's own figure (people.js makePerson: a dress or another
// time's style, what it holds) with every part, its cloth, its head and its hair marked STONE (skeleton.js `stone`:
// shell.js stoneAt paints it marble, bronze, gold or limestone with the world's light and the metal's highlight, the
// cloth keeping its shape and its folds), and what it holds carved too (tools.js `@stone<m>`). A building says where
// they stand -- `statue` markers (architecture.js lifeOf): on a pedestal it built, in a niche, along a balustrade, in a
// temple's cella -- and how they are: { kind, pose, style, outfit, hold: { R, L } (items: the figure's right hand and
// its left), grip { R, L } (how that hand holds it, statuary.json `grips`, over its pose's), wings (statuary.json `wings`:
// a name, or { of, ...numbers }), wear (garments put on over its dress -- Athena's crested helmet: people.js `add`;
// the dress itself one a statue is carved in, the whole of it: statuary.json `dress`, or its pose's table there),
// stone, scale (x a person: a cult statue's colossus), seed, face }.
// THE POSE (2026-10-29, assets/people/statuary.json): a body POSITION (positions.json: contrapposto, the orator, the
// spear bearer, enthroned...) held on the figure by its joints (joints.js: a rig, the angles set once, the body set on
// its feet), and how each hand holds what it is given (a GRIP: upright, hanging, held forward...). The marker names a
// pose, or a family (`stand`, `guard`, `sit`, `lotus`) and the seed draws one of it whose hands can hold what it is given.
// SEATED ON THE FLOOR (a pose's `floor`: a Buddha cross-legged) it is built standing, its hanging cloth cut at the seat
// (people.js pose "floor"), and set down by its joints with its lowest point on the pedestal.
import * as THREE from "three";
import { makePerson } from "./people.js";
import { compileDef } from "./skeleton.js";
import { wingsFor } from "./winged.js";
import { handIndex, toolItem } from "./tools.js";
import { ASSETS } from "./catalogue.js";
import { STONES } from "./shell.js";
import { fetchAsset } from "./creatures.js";
import { attachRig, setAngles, ground, lowest, fk, mirrorAngles } from "./joints.js";
import { createLibrary } from "./motion.js";
import { reachPosition } from "./reach.js";
import { rng } from "./flora.js";

export const STATUARY = await fetchAsset("people/statuary");
const LIB = createLibrary({ positions: await fetchAsset("people/positions") });

// every pose by name, a mirrored one ("orator left") its own entry: the position's mirror, the hands swapped
const swap = (h) => ({ right: h?.left, left: h?.right }), SIDE = { left: "right", right: "left" };
export const STATUE_POSES = Object.fromEntries(Object.entries(STATUARY.poses).flatMap(([name, p]) => [
  [name, { ...p, name }],
  ...(p.mirror ? [[name + " left", { ...p, name: name + " left", mirrored: true, hands: swap(p.hands), ...(p.head ? { head: SIDE[p.head] } : {}) }]] : []),
]));
// (the marker's hands are the figure's: R its right, L its left)
const HANDS = { R: "right", L: "left" };

// THE POSE a statue takes: the one it names, or one of the family it names (an unknown name: `stand`'s) whose hands
// are not `free` where the marker puts something -- drawn by its seed. A lying one's `head` (left | right: the way its
// head lies along the floor, from the figure's own front) is the marker's `head` where it gives one (a pediment's corner:
// toward the middle).
export function statuePose(st) {
  if (STATUE_POSES[st.pose]) return STATUE_POSES[st.pose];
  const inFamily = (f) => Object.values(STATUE_POSES).filter((p) => p.family?.includes(f) && (!st.head || !p.head || p.head === st.head));
  const all = inFamily(st.pose ?? "stand").length ? inFamily(st.pose ?? "stand") : inFamily("stand");
  const fits = all.filter((p) => Object.entries(HANDS).every(([k, side]) => !st.hold?.[k] || p.hands?.[side] !== "free"));
  const from = fits.length ? fits : all;
  return from[Math.floor(rng((st.seed ?? 1) * 7919 + 13)() * from.length)];
}

// one statue's figure: the person, carved, built standing or seated as its pose is
export function statueDef(st) {
  const m = STONES[st.stone] ?? STONES.marble;
  const height = 1.78 * (st.scale ?? 1);
  const pose = statuePose(st);
  // (its colours, where its stone has them -- statuary.json `paint`: a painted figure's flesh, a gold-and-ivory one's)
  const paint = STATUARY.paint[st.stone] ?? {}, hexN = (h) => (h ? parseInt(h.slice(1), 16) : null);
  const skin = hexN(typeof paint.skin === "object" ? paint.skin[st.kind ?? "man"] : paint.skin), hair = hexN(paint.hair);
  const pd = makePerson({ seed: st.seed ?? 1, kind: st.kind ?? "man", adult: true, still: true, height, skin, hair,
                          pose: !pose ? "lie" : pose.seat ? "sit" : pose.family?.includes("lie") ? "recline" : pose.floor ? "floor" : undefined,
                          // (a pose's own table names some styles: the others carved as statues are -- a Greek Buddha drew from
                          //  every Greek outfit, a traveller's petasos a disc over the lotus)
                          outfit: { dress: { ...STATUARY.dress, ...STATUARY.dress[pose?.dress] }, full: true, ...(paint.avoid ? { avoid: paint.avoid } : {}), ...st.outfit, ...(st.wear ? { add: st.wear } : {}) },
                          anatomy: st.anatomy ?? pose?.anatomy ?? null,   // (its bare skin's carving: "soft", a Buddha's -- shell.js ANATOMY)
                          physique: st.physique ?? pose?.physique ?? STATUARY.physique?.[st.kind ?? "man"] ?? null,   // (its ideal: body.json physiques)
                          ...(st.style ? { style: st.style } : {}) });
  // (WINGS: a Victory's, an angel's -- a bird's from the back of the chest, set as the marker names them; after the
  //  person's own parts, so its face's part indices stay as they are)
  const wg = typeof st.wings === "string" ? STATUARY.wings[st.wings] : st.wings ? { ...STATUARY.wings[st.wings.of ?? "raised"], ...st.wings } : null;
  if (wg) { const { _about, of, ...w } = wg; pd.parts = [...pd.parts, ...wingsFor(pd, w, height)]; }
  // (carved cloth is FULL: every cut of a garment closed -- a skirt's hem, a sleeve's mouth -- where real cloth is a shell
  //  open at its edge; shell.js closes a SOLID cut's far end. A standing piece's OPENING stays open, as painted: a
  //  mantle's wrap left a smooth slab of stone over the side it leaves bare -- 2026-10-30 -- now the chiton under it shows;
  //  so does a MOUTH the eye sees into -- a part `open` at its end: a sleeve's, closed a disc round a raised arm as it
  //  gathers there, skeleton.js SLIDE; a short skirt's hem on a seated figure's thighs, closed a tray on its knees.
  //  A standing piece's WAISTBAND stays closed as painted -- `lid`, shell.js: carved, its hem shut with it)
  for (const p of pd.parts) { p.stone = m; p.fur = false; if (p.clip) p.clip = { ...p.clip, solid: !p.open, lid: !p.open && !!p.clip.lid }; }
  for (const p of pd.parts) if (p.covered) Object.assign(p, { bone: true, k: 0 });   // (a piece wholly under another: not carved -- clothes.js `covered`)
  // (`broken`: an ancient statue fallen from the waist up -- chest, arms, neck, head and what is on them no longer carved: their bones
  //  stay, as a covered piece's do, the belly and the hips and legs standing alone. Abu Simbel's second colossus)
  if (st.broken) {
    const by = new Map(pd.parts.map((d) => [d.id, d]));
    const gone = (d) => { for (let q = d; q; q = by.get(q.parent)) { if (q.id === "belly" || q.id === "hips" || q.id === "pelvis") return false; if (q.id === "chest") return true; } return false; };
    for (const p of pd.parts) if (gone(p)) Object.assign(p, { bone: true, k: 0 });
    pd.face = null;
  }
  if (pose) fitToPose(pd, pose);
  if (pd.face) pd.face = { ...pd.face, stone: m };
  pd.jewelry = null;   // (no necklace hung painted on a carving: what it wears on its head is carved with the head, heads.js)
  return { pd, m, pose };
}

// THE DRESS FITTED TO THE POSE, where each bone points -- the figure posed once on its own, off the herd (its rig's fk);
// the def and its parts as compiled both changed: skeleton.js keeps them by the def, and the herd adds those same ones.
// A HANGING SLEEVE on a bone held more than STATUARY.sleeves.raised out of the plumb -- an arm raised, a forearm held
// out, an arm along a reclining body -- is carved CLOSE round it: not let fall (skeleton.js SLIDE), no sag, no flare,
// no wider than the bone and STATUARY.sleeves.ease (a great sleeve kept its elbow's width, a barrel off the forearm). A
// bell tips toward the plumb by no more than its own half-angle; held out, it stood off the arm in stone like a mace or
// a trumpet. A MANTLE over an arm held out past STATUARY.drape.raised is wrapped UNDER it, as a sculptor frees a raised
// arm: that arm out of what it is draped over, and the cloth drawn close, its cling STATUARY.drape.cling -- cut for the
// arms hanging, its cone stood a wall of stone off the shoulder there, the arm up out of it or a curtain off the hand.
function fitToPose(pd, pose) {
  if (!pd.parts.some((d) => d.fall || d.cling)) return;
  const an = { parts: compileDef(pd), base: 0, idx: 0, position: new THREE.Vector3(), rotY: 0, animT: 0, dots: [] };
  const { index, ends: { A, B } } = holdPose(an, pd, pose), C = an.parts;
  const offPlumb = (k) => {   // (degrees)
    const dx = B[k * 3] - A[k * 3], dy = B[k * 3 + 1] - A[k * 3 + 1], dz = B[k * 3 + 2] - A[k * 3 + 2];
    return Math.acos(Math.max(-1, Math.min(1, -dy / (Math.hypot(dx, dy, dz) || 1)))) * 180 / Math.PI;
  };
  // (and one on an arm a mantle lies over -- in a draped piece's `over`: hanging in its bell, a houppelande's sleeve came
  //  out through the king's mantle at the hand, a fin of stone)
  const draped = new Set(C.flatMap((c) => c.cling ? c.cling.over.slice(4).filter((k) => k >= 0 && k !== c.parentIdx) : []));
  pd.parts.forEach((d, i) => {
    const k = d.fall ? index.get(d.parent) : undefined;
    if (k === undefined || (offPlumb(k) <= STATUARY.sleeves.raised && !draped.has(k) && !draped.has(C[k].parentIdx))) return;
    const f = C[i].r1 / d.size.r, r = Math.min(d.size.r, Math.max(C[k].r1, C[k].r2) / f + STATUARY.sleeves.ease);
    d.fall = false; d.sag = 0; d.size = { ...d.size, r, r2: r };
    C[i].fall = false; C[i].sag = 0; C[i].r1 = C[i].r2 = r * f;
  });
  // (what holds it out -- clothes.js `holds`: a matron's stola skirt under her palla -- is drawn as close, or the palla lay
  //  inside it and its folds showed the palla through them in teeth; one that does not cling at all, a stiff cone, keeps
  //  it out as it is: k 0)
  const byId = new Map(pd.parts.map((d, i) => [d.id, i]));
  // (drawn close, it lies on the TRUNK it hangs over in the slots its arms left -- clothes.js `trunk`: the belly, the
  //  hips; on the chest it hangs from and the legs alone, a woman's hips came out through the palla, bare stone in a
  //  band round them under a step)
  const trunkIn = (d, c) => {
    if (!(c.k > 0) || !c.over.includes(C[byId.get(d.id)].parentIdx)) return;
    for (const id of d.cling.trunk ?? []) {
      const k = byId.get(id), j = c.over.findIndex((q, i) => i >= 4 && q < 0);
      if (k === undefined || c.over.includes(k)) continue;
      const at = j >= 0 ? j : c.over.length < 7 ? Math.max(4, c.over.length) : -1;
      if (at < 0) return;
      while (c.over.length < at) c.over.push(-1);
      c.over[at] = k;
      d.cling.over = Object.assign([...d.cling.over], { [at]: id });
    }
  };
  const drawClose = (d, k) => Math.min(k, ...(d.cling?.holds ?? []).map((id) => {
    const j = byId.get(id), u = pd.parts[j];
    if (j === undefined || !u.cling) return 0;
    const kU = Math.max(u.cling.k, drawClose(u, k));
    // (and LAID ON what it hangs from, as the mantle over it is, where a slot is free -- shell.js CLING: settling in below
    //  its top it stood out there round the mantle laid close, a stola's skirt under the breast)
    const lay = u.cling.over.length <= 4 && C[j].parentIdx >= 0;
    u.cling = { ...u.cling, k: kU, ...(lay ? { over: [...u.cling.over, u.parent] } : {}) };
    C[j].cling.k = kU;
    if (lay) C[j].cling.over = [...C[j].cling.over, C[j].parentIdx];
    trunkIn(u, C[j].cling);
    return kU;
  }));
  pd.parts.forEach((d, i) => {
    const c = C[i].cling;
    if (!c) return;
    // (CARVED, a mantle clings as its own cloth would, what holds it out drawn as close -- clothes.js `want`: held back
    //  to a houppelande's skirt's half, a king's mantle stood a box off his elbows to the calf)
    //  -- and one hung over the arms at least `drape.carved`: what is left of its cone off them, cut to clear a bell
    //  of a gown under it, stood a wall of stone from the elbows down)
    const want = Math.max(d.cling.want ?? 0, c.over.slice(4).some((k) => k >= 0 && k !== C[i].parentIdx) ? STATUARY.drape.carved : 0);
    if (want > c.k) { d.cling = { ...d.cling, k: Math.max(d.cling.k, drawClose(d, want)) }; c.k = d.cling.k; }
    const up = c.over.map((k, j) => j >= 4 && k >= 0 && k !== C[i].parentIdx && offPlumb(k) > STATUARY.drape.raised);
    if (up.some(Boolean)) {
      d.cling = { ...d.cling, k: Math.max(d.cling.k, drawClose(d, STATUARY.drape.cling)), over: d.cling.over.map((id, j) => (up[j] ? null : id)) };
      c.k = d.cling.k; c.over = c.over.map((k, j) => (up[j] ? -1 : k));
    }
    // (its forearms as skeleton.js reads them: each arm left in it with its own forearm next -- none where one of them
    //  is held out past drape.raised over its hanging arm: the cloth falls from the elbow, the forearm out of it)
    const arms = c.over.slice(4).filter((k) => k >= 0 && k !== C[i].parentIdx);
    const out = arms.some((k) => C[k + 1]?.parentIdx === k && offPlumb(k + 1) > STATUARY.drape.raised);
    c.fore = arms.length > 0 && !out && arms.every((k) => C[k + 1]?.parentIdx === k);
    trunkIn(d, c);
  });
}

// THE FIGURE IN ITS POSE (on the herd, placed and turned): the position's angles held by the joints, a hand's `reach`
// solved on this body, the body set on its feet where it stood (joints.js ground). Seated, it stays where it sits:
// its floor is wherever the seated position, the pelvis kept, puts its lowest point.
const poseAngles = (pose) => pose.mirrored ? mirrorAngles(LIB.position(pose.position)) : LIB.position(pose.position);
function holdPose(an, pd, pose) {
  const rig = attachRig(an, pd);
  let a = poseAngles(pose);
  if (pose.seat) {
    setAngles(rig, a); an.position.copy(rig.home); fk(rig);
    rig.floor = Math.min(...rig.body.map((i) => lowest(rig, i)));
  }
  if (a.reach) a = reachPosition(rig, a);
  setAngles(rig, a); ground(rig);
  return rig;
}

// the statues of every site into one herd: `sites` [{ x, z, statues }] (the statues' places in the site's frame);
// returns the holders (for tools.place: what each holds, carved, lying in the hand as its pose's grip says)
export function placeStatues(herd, sites) {
  const holders = [];
  for (const s of sites) for (const st of s.statues) {
    const { pd, m, pose } = statueDef(st), p = herd.add(pd);
    p.position.set(s.x + st.x, pose?.seat ? pd.sitAt(st.y) : st.y + .005, s.z + st.z);
    p.rotY = st.h; p.animT = 0;
    // (SEEN ONLY FROM: `seen`, rectangles [x0, x1, z0, z1] about the statue, where the eye must be for it to be drawn at all -- a statue
    //  in a sealed room is not worth its shading from outside. The depth test spares only its pixels, not its vertices: the game hides it, statuesSeen)
    if (st.seen) p.seen = st.seen.map(([a, b, c, d]) => [p.position.x + a, p.position.x + b, p.position.z + c, p.position.z + d]);
    if (pose) p.rig = holdPose(p, pd, pose);
    const sc = st.scale ?? 1;   // (what it holds is as big as it is)
    for (const [k, side] of Object.entries(HANDS)) {
      if (!st.hold?.[k]) continue;
      // (the marker's own GRIP for that hand, where it names one -- `grip: { L: "shield rest" }`: it knows what the figure
      //  carries and how; else an ATTRIBUTE -- a palm, a horn of plenty, a wreath: its item's hold `upright` -- is shown
      //  held up whatever the hand does: on an offering palm the horn stands on it, it does not lie along the fingers
      //  into the body; else the pose's)
      const g = STATUARY.grips[st.grip?.[k]] ?? (ASSETS.get(toolItem(st.hold[k]).path)?.hold?.upright ? STATUARY.grips.upright : STATUARY.grips[pose?.hands?.[side]] ?? {});
      // (the rig's sides are mirrored: its "L" hand is the figure's RIGHT)
      holders.push({ an: p, tool: st.hold[k] + "@stone" + m, hand: handIndex(pd, k === "R" ? "L" : "R"), scale: sc,
                     ...(g.follow !== undefined ? { follow: g.follow } : {}), ...(g.turn ? { turn: g.turn } : {}), ...(g.ground ? { ground: true } : {}) });
    }
  }
  return holders;
}

// each frame, before the herd is posed: a statue with a `seen` is drawn only with the eye inside one of them
export function statuesSeen(herd, eye) {
  for (const a of herd.animals) if (a.seen) a.hidden = !a.seen.some((r) => eye.x > r[0] && eye.x < r[1] && eye.z > r[2] && eye.z < r[3]);
}
