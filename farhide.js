// SMALL THINGS, FAR AWAY: not in the graph at all.
//
// three's frustum test stops a mug behind you being DRAWN, but not being VISITED: every object in the graph is
// walked, its visibility and bounds tested and -- if it faces the camera -- a render item made for it, in every one of
// the frame's scene renders. A village's tableware is sixty-odd objects of a few centimetres, its paintings hang
// indoors; from across the green they are not a pixel between them. So the world registers such things as ONE group
// per place with the distance past which it cannot matter, and the group is switched off beyond it: an invisible
// group is not descended into, and its children cost nothing, in any pass.
//   Judged against the MAIN camera only, four times a second, with a tenth of hysteresis so a group on the edge does
// not flicker in and out. A mirror's or a painting's own view takes what the main view has -- at those distances the
// difference is nothing the eye can find.
import * as THREE from "three";

const items = [];
export const FARHIDE = { on: true, hidden: 0, count: 0 };
const _p = new THREE.Vector3();
// group: nobody else may touch its `visible`.  centre: world point it is judged from.  reach: metres.
export function farHide(group, centre, reach) { items.push({ group, centre: _p.set(...centre).clone(), reach, far: false }); FARHIDE.count = items.length; return group; }
let lastT = -1e9;
export function updateFarHide(camera, t) {
  if (t - lastT < .25 && t >= lastT) return; lastT = t;
  let hidden = 0;
  for (const it of items) {
    const d = it.centre.distanceTo(camera.position);
    it.far = FARHIDE.on && d > it.reach * (it.far ? .9 : 1);
    it.group.visible = !it.far; if (it.far) hidden++;
  }
  FARHIDE.hidden = hidden;
}
