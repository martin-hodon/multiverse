// THE STANCE: where the feet and the hands stand on the ground, and how they stay there while the body moves over them
// (assets/people/joints.json `stance`, docs/motion.md).
//
// Real people do not slide on the floor. A foot (or a hand) on the ground at both ends of a move keeps its PRINT: the
// leg -- the arm -- is solved to it every frame with the same two-bone triangle a reach uses (joints.js reachLimb), its
// knee kept as near as the circle lets it to where the position puts it, and the ankle (the wrist) turned so the foot
// lies as the position has it. Only when the next position wants a foot further than `step` away does it STEP: lifted
// on an arc, set down where it is wanted -- the foot that stepped last is the one that steps back (out of a lunge the
// front foot comes home, the back one stays). A `hop` (a jumping jack) moves every foot at once and lifts the body.
// The BODY between two positions goes from where it stood to where the next position puts it over its prints, eased.
//
//   const st = createStance(rig)          (where the figure stands now: its prints)
//   const plan = st.plan(angles, opts)    a move toward a position: where the body goes, what every foot and hand does
//   st.frame(plan, e, angles)             the body at e (0..1, eased) of that move -- the angles' legs and arms
//                                         solved onto their prints; the figure posed
import * as THREE from "three";
import { MODEL, setAngles, ground, fk, lowest, limbOf, tipOf, reachLimb, aimEnd, endDir, jointAt, limbBase } from "./joints.js";

const CONTACTS = [["right", "leg", "right foot"], ["left", "leg", "left foot"], ["right", "arm", "right hand"], ["left", "arm", "left hand"]];
const UP = new THREE.Vector3(0, 1, 0);

// every foot and hand as the rig is posed now: its tip (the ankle, the palm), its direction, and whether it is down
function contactsNow(rig) {
  const T = MODEL.stance, out = {};
  for (const [side, kind, name] of CONTACTS) {
    const limb = limbOf(rig, side, kind);
    if (limb.i2 === undefined) continue;
    out[name] = { limb, p: tipOf(rig, limb), dir: endDir(rig, limb), down: lowest(rig, limb.i2) <= rig.floor + T.planted };
  }
  return out;
}

export function createStance(rig) {
  const an = rig.an;
  let prints = {}, last = null;   // name -> { p, dir }: where each stands (or stood, lifted); the one that stepped last
  let downs = {};                  // name -> on the ground as the last move left it (what the move planned, not a few mm of geometry)
  let now = null;                  // the figure as the last frame left it: { position, pitch, pelvis, contacts }
  const pelvisAt = () => jointAt(rig, rig.index.get("pelvis"));
  const remember = () => { now = { position: an.position.clone(), pitch: an.pitch ?? 0, pelvis: pelvisAt(), contacts: contactsNow(rig) }; };   // (a figure never tipped has no pitch)
  // where the figure stands now (posed already): its prints are its feet and hands that are down
  function reset() {
    fk(rig); remember(); prints = {}; last = null; downs = {};
    for (const [nm, c] of Object.entries(now.contacts)) { downs[nm] = c.down; if (c.down) prints[nm] = { p: c.p.clone(), dir: c.dir.clone() }; }
  }
  reset();

  // A MOVE toward the position `a`: the body set on the ground as the position stands on its own (its lowest point on
  // the floor, its supports, ground()), then moved across the floor so that what stays down keeps its print -- of the
  // ways it could (each print held, or their middle) the one with the fewest steps, the last foot to move moving again
  function plan(a, { hop = false } = {}) {
    const T = MODEL.stance;
    setAngles(rig, a); ground(rig);
    const at = { position: an.position.clone(), pitch: an.pitch ?? 0 }, want = contactsNow(rig);
    const held = Object.keys(want).filter((nm) => want[nm].down && prints[nm]);
    const shiftFor = (names) => {   // the floor shift that puts these where they stand (their middle on their prints' middle)
      const d = new THREE.Vector3();
      for (const nm of names) d.add(prints[nm].p).sub(want[nm].p);
      return d.divideScalar(names.length || 1).setY(0);
    };
    const movesWith = (d) => held.filter((nm) => want[nm].p.clone().add(d).setY(0).distanceTo(prints[nm].p.clone().setY(0)) > T.step);
    let shift = new THREE.Vector3(), moving = [];
    if (held.length) {
      // (the position's anchor names what stays: one foot or hand, or a pair -- `hands`, `feet`: a push-up keeps its
      //  hands where they were put down and the feet go back)
      const anchorNames = { hands: ["right hand", "left hand"], feet: ["right foot", "left foot"] }[a.anchor] ?? (a.anchor ? [a.anchor] : []);
      const named = anchorNames.length && anchorNames.every((nm) => held.includes(nm)) ? [anchorNames] : null;
      const options = named ?? [held, ...held.map((nm) => [nm])];
      let best = null;
      for (const names of options) {
        const d = shiftFor(names), mv = hop ? held : movesWith(d);
        const cost = mv.reduce((t, nm) => t + (nm === last ? .5 : 1), 0) + (names.length > 1 ? 0 : .01);   // (the middle wins a tie)
        if (!best || cost < best.cost) best = { cost, d, mv };
      }
      shift = best.d; moving = best.mv;
    }
    at.position.add(shift);
    // WITHIN REACH: a print the limb cannot get to (a straight leg, the body further from it than the leg is long -- a
    // push-up's chest lowered on angles that put the hips forward) draws the body toward it, so the body turns about
    // what holds it instead of dragging it along
    const kept = Object.entries(want).filter(([nm, c]) => c.down && prints[nm] && !moving.includes(nm) && !hop);
    for (let k = 0; k < 4 && kept.length; k++) {
      an.position.copy(at.position); fk(rig);
      const pull = new THREE.Vector3();
      for (const [nm, c] of kept) {
        const { S } = limbBase(rig, c.limb), to = prints[nm].p.clone().setY(c.p.y), d = to.distanceTo(S), L = c.limb.L1 + c.limb.L2 - .004;
        if (d > L) pull.add(to.sub(S).multiplyScalar((d - L) / d));
      }
      if (pull.lengthSq() < 1e-8) break;
      at.position.add(pull.divideScalar(kept.length));   // (in 3D: a straight-armed push-up comes down a little onto its hands)
    }
    an.position.copy(at.position); fk(rig); at.pelvis = pelvisAt();
    // what each foot and hand does on the way
    const paths = {};
    for (const [nm, c] of Object.entries(want)) {
      const from = now.contacts[nm], wasDown = !!prints[nm] && !!downs[nm];
      const to = c.p.clone().add(shift), toDir = c.dir.clone();
      if (c.down) {
        // (a print holds the foot's PLACE on the floor; how high its ankle stands is the position's -- up on the toes)
        const keep = prints[nm] && !moving.includes(nm) && !hop;
        const target = keep ? { p: prints[nm].p.clone().setY(to.y), dir: prints[nm].dir } : { p: to, dir: toDir };
        paths[nm] = { limb: c.limb, mode: wasDown ? (keep ? "plant" : "step") : "land", a: from.p.clone(), da: from.dir.clone(), b: target.p.clone(), db: target.dir.clone() };
        prints[nm] = { p: target.p.clone(), dir: target.dir.clone() };
      } else paths[nm] = { limb: c.limb, mode: wasDown ? "lift" : "free", a: from.p.clone(), da: from.dir.clone() };
    }
    if (moving.length === 1) last = moving[0];
    downs = Object.fromEntries(Object.entries(want).map(([nm, c]) => [nm, c.down]));
    return { from: { position: now.position.clone(), pitch: now.pitch, pelvis: now.pelvis.clone() }, to: at, paths, hop: hop && held.length > 0 };
  }

  // THE BODY AT e OF A MOVE: its PELVIS eased from where it stood to where it goes (a hop lifting it on the way) -- not
  // the figure's ground point, which swings round with the body's tilt and would drag the pelvis off its line -- the
  // tilt eased, the position's angles on it, and every foot and hand that is down, stepping or coming down solved onto its point
  const _pos = new THREE.Vector3(), _pel = new THREE.Vector3();
  function place(p, e) {
    an.pitch = p.from.pitch + (p.to.pitch - p.from.pitch) * e;
    an.position.lerpVectors(p.from.position, p.to.position, e);
    fk(rig);
    _pel.lerpVectors(p.from.pelvis, p.to.pelvis, e);
    if (p.hop) _pel.y += MODEL.stance.hop * Math.sin(Math.PI * e);
    an.position.add(_pel.sub(pelvisAt()));
  }
  function frame(p, e, a) {
    const T = MODEL.stance;
    setAngles(rig, a); place(p, e); fk(rig);
    const aims = [];
    for (const path of Object.values(p.paths)) {
      if (path.mode === "free") continue;
      const limb = path.limb, here = tipOf(rig, limb), dirHere = endDir(rig, limb);
      let target, dir;
      if (path.mode === "plant") { target = _pos.copy(path.b).setY(path.a.y + (path.b.y - path.a.y) * e).clone(); dir = path.da.clone().lerp(path.db, e).normalize(); }
      else if (path.mode === "step") { target = _pos.lerpVectors(path.a, path.b, e).addScaledVector(UP, T.lift * Math.sin(Math.PI * e)).clone(); dir = path.da.clone().lerp(path.db, e).normalize(); }
      else if (path.mode === "land") { target = path.a.clone().lerp(path.b, e); dir = path.da.clone().lerp(path.db, e).normalize(); }
      else { target = path.a.clone().lerp(here, e); dir = path.da.clone().lerp(dirHere, e).normalize(); }   // lift: let go of the print
      // (a hand: to its WRIST, the palm's half-length back from the point along the way the hand lies -- it bends there)
      if (limb.kind === "arm") { const w = limbOf(rig, limb.side, "wrist"); reachLimb(rig, w, target.clone().addScaledVector(dir, -(limb.L2 - w.L2)), a); }
      else reachLimb(rig, limb, target, a);
      aims.push([limb, dir, target]);
    }
    if (aims.length) {   // the ankles and wrists, once the legs and arms stand where they go
      setAngles(rig, a); place(p, e); fk(rig);
      for (const [limb, dir] of aims) aimEnd(rig, limb, dir, a);
      setAngles(rig, a); place(p, e); fk(rig);
      // a hand once more: the wrist bends only in the forearm's plane, so the palm lies the way it CAN -- its wrist put
      // back from the point along that, and the arm solved again
      const hands = aims.filter(([limb]) => limb.kind === "arm");
      if (hands.length) {
        for (const [limb, , target] of hands) { const w = limbOf(rig, limb.side, "wrist"); reachLimb(rig, w, target.clone().addScaledVector(endDir(rig, limb), -(limb.L2 - w.L2)), a); }
        setAngles(rig, a); place(p, e); fk(rig);
        for (const [limb, dir] of hands) aimEnd(rig, limb, dir, a);
        setAngles(rig, a); place(p, e); fk(rig);
      }
    }
    remember();
    return a;
  }
  // the figure HELD (no move): standing as the position stands, its prints taken afresh
  function hold(a) { setAngles(rig, a); ground(rig); reset(); }
  return { plan, frame, hold, reset, get prints() { return prints; } };
}
