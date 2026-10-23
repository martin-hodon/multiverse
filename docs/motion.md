# The body in motion: joints, positions, movements, exercises, reaching

A person is drawn as PARTS on a skeleton (people.js, skeleton.js): the pelvis (the root, an undrawn bone), the trunk
(three flat cuts swept as one: chest, belly, hips), the neck and head, and per side an upper arm, a forearm and a
hand, a thigh, a shin and a foot. Every part's frame has its origin at the JOINT it hangs on -- the shoulder for the
upper arm, the ankle for the foot (since 2026-10-07; the foot used to sit in its own frame under the ankle). What is
added here is the logic on top: how those parts may turn, and what they may not do.

    assets/people/joints.json     the JOINT MODEL: the joints, their movements, ranges, rests; the body's rules
                                  (collision) and how a reach is chosen (reach)
    assets/people/positions.json  POSITIONS: every joint's angles
    assets/people/movements.json  MOVEMENTS: positions in a sequence, with the time to each and holds
    assets/people/exercises.json  EXERCISES: movements repeated, alternated, at a tempo
    joints.js     angles -> the parts' rotations (a RIG on one figure); ranges, mirror, blend; the body on the ground
    bodycheck.js  the body's rules: nothing through the trunk, the head, another limb; and putting a position right
    reach.js      the hand to a point: the arm's triangle, the natural elbow, leaning, crouching
    stance.js     where the feet and hands stand: prints kept while the body moves, steps, hops
    motion.js     the library (positions, movements, exercises) and the PLAYER on a rig

## Joints

A joint turns the part it names in its parent's frame (+x the figure's forward, +y up, +z its right). Each MOVEMENT is
a rotation about one axis of that frame, by an angle in degrees with a range; the movements compose in the order
written, the first turning everything after it. As in the body, the first joint of each limb and the trunk's have
three movements, every joint further out one:

| joint    | part  | movements (degrees: the range)                                                      |
|----------|-------|-------------------------------------------------------------------------------------|
| spine    | chest | flexion -30..90, lateral -35..35, rotation -45..45 (the trunk bends about the pelvis) |
| neck     | head  | flexion -60..70, lateral -40..40, rotation -80..80 (about the top of the neck)        |
| shoulder | arm   | flexion -50..180, abduction -30..180, rotation -90..70 (internal +)                   |
| elbow    | fore  | flexion 0..145                                                                        |
| wrist    | hand  | flexion -90..80 (extension 70 alone, 90 with the weight on a flat palm)               |
| hip      | leg   | flexion -20..125, abduction -25..45, rotation -45..40                                 |
| knee     | shin  | flexion 0..140                                                                        |
| ankle    | foot  | flexion -50..30 (dorsiflexion +; on tiptoe -)                                         |

Angles are anatomical: 0 is standing straight, the arms hanging; positive is the movement named, for either side
(`sided` movements turn the other way round their axis on the left, so abduction always takes a limb away from the
body). A joint's REST is the standing figure's (the shoulder's abduction is the canon's `arm.abduction`, read as
`"body:arm.abduction"`; the elbow's 12 degrees is also what people.js draws an unposed forearm with). The rig's parts
are named for the side of the DRAWING (`armL` stands at +z, the figure's right); everything here speaks of the body's
right and left (`sides` in joints.json maps them).

**The pose layer** (skeleton.js writeAnimal): `an.pose[i] = { q, c }` holds part i in rotation q (a quaternion in its
parent's frame) about the point c of its frame (null: the joint itself) in place of its own rotation, its gait swing
and its leg IK; a posed foot is no longer kept level. A figure with no `an.pose` is drawn exactly as before.

**The trunk's forward.** A flat torso is squashed along the figure's forward, which the shaders take from the root's
drawn axis. A person's definition now says `forwardFrom: "chest"`: the root's axis is drawn turned by the chest's
frame (identical to the pelvis's at rest), so a twisted trunk faces where it turns, and the cloth and the jewels
turn with it.

## Positions

    "squat": { "joints": { "spine": { "flexion": 38 }, "both hips": { "flexion": 95, "abduction": 12 },
                           "both knees": { "flexion": 125 }, "both ankles": { "flexion": 30 } } }

Joints are named `spine`, `neck` or `<side> <joint>` with side `right`, `left` or `both` (plurals allowed); a
movement not named stays at rest. `mirror` makes a position another's mirror image (right and left swapped, the trunk's
sideways movements and the body's roll and yaw turned round); `from` takes another position and changes some joints.
A value out of its range is clamped (and reported by the tests). Beside the joints:

- `root` turns the whole body: `pitch` (+ face up: lying on the back is 90), `roll`, `yaw`, `lift` (metres up);
- `anchor` is what keeps its place on the ground: `feet` (their middle, the default), `right foot`, `left foot`,
  `hands`, `knees`, `pelvis`. **The ground rule**: every frame the body's lowest point (its limbs and trunk -- not a
  skirt's hem) is put on the floor and the anchor where it stood at rest, so a squat sinks over its feet, a lunge stays
  on its front foot, a body laid down keeps its pelvis;
- `support` names two things the body rests on at once (`feet`, `hands`, `forearms`, `knees`, `pelvis`, `back`,
  `head`): the body's tilt (root pitch) is FOUND, by bisection, so that both touch -- a plank, a push-up, a crunch
  on its back with the feet flat. A transition into a supported position takes that tilt in step with the way there.

Some positions were TUNED BY SEARCH over their angles (hands on hips: the palm on the waist, nothing through the trunk;
the lunge's back leg: the toes on the floor, the knee just off it; the kneel): the searches live in the test pages
(scratchpad), the results in the file.

`reach` says where the HANDS go instead of how the arms bend -- `{ "hands": "toes" }` (both: the left arm the mirror
of the right, the trunk bending straight forward), or `right hand` / `left hand`; places `toes`, `knees`, `floor`
(ahead of the feet, shoulder-wide) -- and each body finds its own bend with the reach's solver (the spine, the pelvis
tipped over the thighs, the knees soft if it must), once, when the position is first played on it. `lean` limits what
else may move to get there: `true` (the trunk, the hips, the knees), `"spine"` (the trunk's forward bend alone),
`false` (the arms alone, the body as the position holds it). The toe touch is written so: its palms end at the toes
on a man, a woman and a child alike; the push-up's way down, "hands down", leans its trunk as a person does (between
wide knees, the head up) and lets the arms alone find the floor.

## The stance (stance.js)

Real people do not slide on the floor. A foot or a hand ON THE GROUND (its lowest point within `stance.planted` of the
floor) at both ends of a move keeps its PRINT -- its place on the floor; how high its ankle stands is the position's
(up on the toes) -- and every frame the leg or arm is solved onto it with the limb solver (joints.js `reachLimb`, the
same triangle as a reach: the knee goes round its circle to the side its cap faces, a straight leg keeps its twist)
and the ankle or wrist turned so the foot or hand lies as the position has it (a hand is solved to its wrist, the palm
laid after, twice: the wrist bends in one plane). The knees and elbows take the change, never the sole: a squat's
hips going out push the knees out; a push-up's hands stay where they were put.

A foot STEPS only when the next position wants it more than `stance.step` away: lifted `lift` at the top of an arc,
set down where it is wanted. Which foot: of the ways the body could be set over its prints (each held, or their
middle) the one with the fewest steps -- the foot that stepped last moving again (out of a lunge the front foot comes
home), the position's own `anchor` naming what stays (a lunge's back foot; `hands` or `feet` a pair: a push-up keeps
its hands where they were put down and the feet step back). A key marked `hop` moves every
foot at once and lifts the body `stance.hop` (a jumping jack). A print the limb cannot get to draws the body toward
it, so a push-up turns about its toes instead of dragging them. Between two positions the PELVIS is eased from where
it was to where it goes (not the figure's ground point, which swings round with the body's tilt), the tilt with it.

A movement may say how it gets to its start, `via` other positions -- onto the floor through a squat and the hands put
down (push-ups, the plank), down to sitting (crunches) -- so no one falls over stiff into a push-up.

## Movements and exercises

    "squat": { "start": "stand", "keys": [{ "to": "squat", "time": 1.4, "hold": 0.3 }, { "to": "stand", "time": 1.2, "hold": 0.3 }] }
    "lunges": { "sequence": ["lunge right", "lunge left"], "reps": 6, "tempo": 1, "works": "thighs, buttocks, balance" }

A movement goes from its `start` through its keys; between two keys every angle follows a MINIMUM-JERK curve
(10u^3 - 15u^4 + 6u^5, Flash & Hogan 1985: a limb's own way of speeding up and slowing down), and the ground rule
holds at every frame. `mirror` is a movement with right and left swapped in every position it names. An exercise is
one `movement` or a `sequence` (alternating sides), `reps` times at a `tempo` (times multiplied; a key with
`holdTempo: false` keeps its hold -- a plank held 15 s). The set: squats, half squats, lunges, jumping jacks, arm
circles, toe touches, side bends, torso twists, high knees, marching, calf raises, push-ups, plank, crunches,
shoulder press, lateral raises, front raises.

## The body's rules (bodycheck.js)

Every part is tested as what it is drawn as -- a round cone between its two ends; the trunk's flat cuts in a space
stretched along the trunk's forward until they are round (a limb's radius grows there by as much as the stretch where
it faces the trunk). `collision.pairs` say what must stay clear of what, by GROUPS (trunk, head, upper/lower arm,
upper/lower leg; `name*` the other side's): an arm and the trunk, a forearm and the head, a leg and the other leg,
the hands and the legs, the forearms and each other... Two parts may TOUCH -- a hand on a thigh, forearms crossed --
but not sink in deeper than `tolerance` (1.2 cm); next to its own joint a part always meets its neighbour, so it is
tested only from `skip` of its length away (the top third of the upper arm fits into the shoulder).

`checkBody(rig)` lists what a position breaks; `fixBody(rig, angles)` puts it right with the model's `fix` steps (an
arm in the trunk is taken out to the side, a leg through the other out the same way -- the knees out of a crouch's
chest -- both parts of a pair that have a fix moving), a step at a time, up to each fix's limit. The player runs the
fix on every frame by default (`fix`, the viewer's checkbox), on the body as the stance holds it. Checked: every frame
of every exercise at 30 fps breaks no rule; planted feet and hands stay within 3 mm of their prints; the pelvis moves
no more than 2-5 cm a frame (no jumps).

## Reaching (reach.js)

THE TRIANGLE: the upper arm (shoulder to elbow) and the forearm with the hand (elbow to the middle of the palm) are two
sides of a triangle whose third runs from the shoulder to the point. Its length fixes the elbow's bend (the law of
cosines); the elbow may stand anywhere round a circle about that third side -- the SWIVEL. The shoulder's three angles
are read back from the upper arm's direction and the plane the elbow bends in (exactly, for the model's flexion z,
abduction x, rotation y order -- reach.js refuses another). Which swivel is natural is a COST (joints.json `reach`):

- the elbow hanging down and a little out (`swivel` 20 degrees outward), as an arm does by its own weight;
- abduction above 70 degrees costs (`abductionOver`: the shoulder blade must turn) -- forward is preferred to sideways;
- extension (the arm behind the body) costs most; rotation (a twisted arm) a little;
- every joint inside its range (`limit`), nothing through the body (`collision`, by bodycheck), the hand on the point
  (`miss`); moving, no jump from the last swivel.

48 swivels are priced, the best six posed and checked. A point the arm cannot get to is reached by LEANING -- the trunk
bent, turned and tipped sideways, each from 0 a step at a time -- and, still short and low, by CROUCHING (both legs a
share of the way to `lean.crouch`'s angles) and BOWING (the pelvis tipped over the thighs, as in a toe touch), each at
its own cost. Measured: in reach 2-4 ms, a lean 20-30 ms, a crouch to the floor ~55 ms (once per reach, not per frame).

`planReach` makes the MOVEMENT: the hand along a straight line from where it is to the point (as people move their
hands), six steps on it each solved from the last, the trunk easing into its lean on the way; the player runs the keys
along a minimum-jerk clock, `time` = 0.45 s + 0.7 s per metre of travel (`reach.speed`: longer reaches are slower).

## In the game

    import { attachRig } from "./joints.js";
    import { createLibrary, createMotion } from "./motion.js";
    const lib = createLibrary({ positions, movements, exercises });        // the three files (fetchAsset)
    const an = herd.add(def); herd.update(t);                               // posed once at rest first (the cloth's frame)
    const m = createMotion(attachRig(an, def), lib);
    m.play("squats");  m.hold("plank");  m.reach(pointInWorld);  m.reachAround(seed);  m.stop();
    // every frame, before herd.update: m.update(dt) -- and if the figure is moved, m.rig.home / m.rig.floor first

The rig keeps the figure's place (`home`, `floor`) and facing (`rotY0`) from when it was attached; a posed figure has
no gait (amp 0). `releaseRig` (m.stop) hands it back to its own animation.

The everyday gestures (people.js GESTURES: work, waving, clapping) and the fixed poses (sit, carry, draw) are not posed
through the rig but added to the parts' rotations. Their forearms still keep to the elbow (2026-10-23): a forearm is a
HINGE (skeleton.js) -- whatever its rotation adds up to, it is aimed by a bend of 0..145 degrees (joints.json elbow) in
a plane turned about the upper arm by no more than the shoulder's rotation (joints.json shoulder, its sign by side);
an aim outside that is pulled to the nearest one it can take, a bend backwards goes straight. A gesture turns that
plane with its forearm's `twist`: the wave's elbow bends up across the body's plane, the palm toward you.

## Clothes

What is WORN lies on the parts as layers (clothes.js `dress`) and moves with them; a sleeve is one cone per arm part,
each reaching a third of its radius past the joint, so a bent elbow stays covered. What STANDS OFF the body hangs on
the trunk: a piece that starts at the waist or below (a skirt) on the pelvis, one that starts higher (a cape, a cloak,
a tabard) on the chest -- so it bends and turns with the shoulders (the two frames are one at rest: nothing changes
for a figure that does not move). A SKIRT is carried forward by the thighs under it: it tilts by .55 of the hips'
mean flexion (up to 70 degrees); the legs under a long skirt are not drawn, as before.

Known limits: a cloak over the arms is one cone on the trunk -- raised arms come out through it; a skirt only tilts
forward (a sideways leg stays under it).

## In the asset viewer

People & clothes -> Body motion: the four documents, read together (the one being edited from its text). The toolbar
picks what is shown and on whom (a bare man, a dressed man, a woman in kirtle and cloak, a soldier):

- **joints**: reaching for points round the body (a yellow ball marks each; the cone is `reach.cone`), every joint's
  range swept (out to one limit, the other, back), or one joint's;
- **positions**: one held, or **all** of them side by side -- the line under the view says which break a rule;
- **movements** and **exercises**: played, looping, the key and the rep shown, and anything through the body; the view
  framed on everywhere the timeline goes (a push-up lies a body's length ahead of where it stood).

**fix** runs the body's rules on every frame. Edits to any of the four files show at once.
