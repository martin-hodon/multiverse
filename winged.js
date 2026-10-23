// WINGED PEOPLE (2026-10-04): an angel, a demon -- the mixed monsters that are a whole person with wings. A definition
// (assets/creatures/monsters/angel.json) is of kind "winged": { person: makePerson's options (seed, kind, height, skin,
// outfit), wing: { kind: "bird" | "bat", k, ...the wing's own numbers }, horns, hair }; creatures.js builds it with
// what this registers (KINDS), so the game and the asset viewer build it the same way.
import { makePerson } from "./people.js";
import { batWing, birdWing } from "./mammals.js";
import { KINDS } from "./creatures.js";

const num = (c) => typeof c === "string" && /^#[0-9a-fA-F]{6}$/.test(c) ? parseInt(c.slice(1), 16) : c;   // ("#rrggbb" as the rig takes a colour)
const hex = (c) => typeof c === "number" ? "#" + c.toString(16).padStart(6, "0") : c;                   // (...and as the mesh head does)

// ---- winged people (an angel's kind, a demon's): the whole person (people.js makePerson) and a pair of wings grown
// from the back of the chest, just inside the shoulder blades -- a bird's, feathered (mammals.js birdWing), or a bat's,
// fingers and skin (batWing). The wings hang on the chest, so they turn and bend with the torso; their root is found
// from the rig itself (the arms' shoulder joint and the chest's girth), so it fits any height and build.
//   wing: { kind: "bird" | "bat", k (span, x the rig's 1 m wing), ...the wing's own numbers }; horns: { r, len (x the head's
//   radius), color }; hair: its colour ("#rrggbb", the mesh head's)
export function winged(name, { wing: { kind: wk = "bird", k = 1, ...wo } = {}, horns = null, hair = null, call, ...person }) {
  const man = makePerson(person), byId = (id) => man.parts.find((p) => p.id === id);
  const arm = byId("armL"), chest = byId("chest"), S = (person.height ?? 1.78) / 1.78;
  const back = -(chest.size.r * (chest.flat || 1)) * .85;   // (just inside the back: the root sinks into the shoulder blade)
  const at = [back, arm.pos[1] - .06 * S, Math.abs(arm.pos[2]) * .45];
  const mk = wk === "bat" ? batWing : birdWing;
  // (a wing is drawn for a beast's back: x its body's forward, y up off the back. An upright figure's body runs UP, and
  //  its back faces -x: a root bone turned a quarter about z maps the one onto the other -- the wings spread behind the
  //  back, their chord hanging down, and flap forward and back about the spine)
  const root = { id: "wingRoot", parent: "chest", shape: "capsule", size: { r: .01, len: .01 }, bone: true, pos: [at[0], at[1], 0], rot: [0, 0, 90] };
  const wings = [root, ...[1, -1].flatMap((s) => mk(s, { k: k * S, parent: "wingRoot", x: 0, y: 0, z: at[2], lift: 35, ...wo }))];
  const head = byId("head"), extra = [];
  if (horns) for (const s of [1, -1]) {   // (a demon's: two short cones from the brow, curving back)
    // (a cone is centred on its pos: its base on the skull -- a little out, the mesh head is the fuller -- and its
    //  middle half its length on along where it points, out and back)
    // (a mesh head's part is a pin: the face knows its radius)
    const r = man.face?.hr ?? head.size.r, h = (horns.len ?? 1.4) * r, rx = 18, rz = 25, D = Math.PI / 180;
    const d = [-Math.sin(rz * D), Math.cos(rz * D) * Math.cos(rx * D), s * Math.cos(rz * D) * Math.sin(rx * D)];
    const n = [.3, .82, s * .48], nl = Math.hypot(...n), base = n.map((v) => v / nl * r * 1.12);
    extra.push({ id: `horn${s > 0 ? "L" : "R"}`, parent: "head", shape: "cone", size: { r: (horns.r ?? .2) * r, h },
                 pos: base.map((v, i) => v + d[i] * h / 2), rot: [s * rx, 0, rz], color: horns.color ?? 0x2a1a14, edge: 0 });
  }
  if (hair && man.face) man.face = { ...man.face, hair };   // (an angel's gold)
  // (the wings and horns go AFTER the person's parts: its face's part indices stay as they are)
  return { ...man, name, monster: true, call, parts: [...man.parts, ...wings, ...extra] };
}

// the definition's kind: its person and its wing are its own words (creatures.js keeps them as written)
KINDS.winged = (d) => {
  const { person = {}, wing = {}, horns = null, hair = null, call } = d;
  const w = Object.fromEntries(Object.entries(wing).map(([k, v]) => [k, num(v)]));
  return winged(d.name, { ...person, ...(person.skin ? { skin: num(person.skin) } : {}), wing: w,
                          horns: horns && { ...horns, color: num(horns.color) }, hair: hex(hair), call });
};
