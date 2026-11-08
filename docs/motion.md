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
A value out of its range is clamped (and reported by the tests) -- a LIMBER position (`"limber": true`, the lotus) by
a movement's `limber` range where joints.json gives one: the hip's rotation to -95, the shin's own turn in the knee,
which the model lacks, taken in the hip (in range, the lotus's shins hung down under it; limber, they lie flat on the
floor, crossed). A `from` keeps its base's `limber` and its `lean`. Beside the joints:

- `root` turns the whole body: `pitch` (+ face up: lying on the back is 90), `roll`, `yaw`, `lift` (metres up);
- `anchor` is what keeps its place on the ground: `feet` (their middle, the default), `right foot`, `left foot`,
  `hands`, `knees`, `pelvis`. **The ground rule**: every frame the body's lowest point (its limbs and trunk -- not a
  skirt's hem) is put on the floor and the anchor where it stood at rest, so a squat sinks over its feet, a lunge stays
  on its front foot, a body laid down keeps its pelvis;
- `support` names two things the body rests on at once (`feet`, `hands`, `forearms`, `left forearm`, `right forearm`,
  `knees`, `pelvis`, `back`, `head`): the body's tilt (root pitch) is FOUND, by bisection, so that both touch -- a plank, a push-up, a crunch
  on its back with the feet flat. A transition into a supported position takes that tilt in step with the way there.
  `tilt: "roll"` finds the root's roll instead -- a body on its side propped on one elbow (`left forearm`, `right
  forearm`: one arm's; the statues' `reclining`).

Some positions were TUNED BY SEARCH over their angles (hands on hips: the palm on the waist, nothing through the trunk;
the lunge's back leg: the toes on the floor, the knee just off it; the kneel): the searches live in the test pages
(scratchpad), the results in the file.

`reach` says where the HANDS go instead of how the arms bend -- `{ "hands": "toes" }` (both: the left arm the mirror
of the right, the trunk bending straight forward), or `right hand` / `left hand`; places `toes`, `knees`, `floor`
(ahead of the feet, shoulder-wide), `lap` (before the hips, over the crossed legs: a Buddha's hands) -- and each body finds its own bend with the reach's solver (the spine, the pelvis
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

## Standing about (2026-10-24)

A person standing about is never still: `people.js IDLE_SWAY` (.022 rad) on a standing or carrying figure that is not a
bench's still one, `skeleton.js` rocks its root slowly to the side (.55 rad/s) and less to and fro (.37), each figure on
its own beat (`an.idx`), fading out as the stride comes in. Statues (any stone part) never sway.

## In flight (2026-11-04)

A beast that flies -- a mount with `"fly": true`, the dragons and the manticore -- used to keep the pose it stands
in once it was in the air. Its neck stayed reared up, its legs stood on nothing, its tail hung down to a ground that
was not there, and only the wings beat: it looked like an animal standing in the sky. Now `an.fly`, eased from 0
on the ground to 1 aloft toward `an.flyT` (easeGait, at `FLIGHT.ease` per second), takes it into a flight pose that
`skeleton.js` works out from each rest pose (`flightPose`), so every body plan gets one without writing it down:

- **the neck** swings about its root, together with the head and everything that nods with it, until it reaches
  forward `FLIGHT.neck` degrees above level. The head turns back by `head` of that swing so it looks ahead, not
  at the sky. This is the grazing nod's own pivot: a mammal's head hangs off the body, not the neck, and both
  turn about that pivot.
- **the tail**: its root is aimed straight back (`tail`: 180 is level, less is rising) and each link is
  straightened by `straight` of its droop, so the tail streams out behind.
- **the legs** fold out of the way, toward `[upper, lower, foot]` angles in their parents. The forelegs are drawn
  up under the chest (`front`: the elbow back, the forearm forward). The hind legs trail back along the tail
  (`hind`). The feet are no longer held level to the ground: their orientation is slerped from levelled to hanging
  with the leg. `splay: [front, hind]` (degrees, 2026-11-05) swings each upper leg out from the body, or in when
  the value is negative. A lung spreads its legs out to the sides ([24, 20]), its forearms trailing back (`front` [-82, 18, 20]); a western dragon draws its thighs in under its
  flanks ([-6, -12]).
- **the wings** spread out (`arm`, `hand`: degrees out from the body's vertical plane). The arm beats `beat` times
  as deep as a folded wing's flutter, and the hand `1 + (beat - 1) * handK` times, so the tip is not folded
  straight up. A wing part is a HAND when any part above it is a wing part, so other parts may sit between them
  (a dragon's forearm between its arm and hand). A wing part's `anim.side` (+-1) says which way it spreads when its rest pose cannot tell (an arm laid
  flat back along the flank). Any part's `flyRot` [x, y, z] (degrees) is added aloft: a dragon's wing is folded
  like a bat's at rest, the humerus laid back along the flank, the forearm doubled forward against it, the fingers
  run back toward the hip, nearly closed, every wedge of skin turned onto its bone. `flyRot` opens it all out.
  The body rises and sinks by `bob` (per metre of leg) against the downstroke.
- **the upstroke fold** (2026-11-05): a part's `flyUp` [x, y, z] (degrees) is added on the upstroke only, on the
  wing's own clock. None of it applies through the downstroke, all of it at mid-upstroke, eased in and out. A
  dragon's bat hand uses it to flex at the wrist (12 degrees) and draw its fingers 45% of the way back onto the last
  one, so it half-folds as the wing rises and spreads again to beat down. The feathered wing's hand sweeps back
  38 degrees. The last finger does not move, so the skin between it and the arm never tears.
- **a wave** (`wave: { deg, lag, speed, trunk, trunkLag, taper }`, off by default) runs back down the tail links,
  each turned up and down `deg` degrees, the next `lag` radians behind: a wingless lung swimming through the air.
  Since 2026-11-05 it starts in the trunk. A part with `waveAt` -k (k links ahead of the tail's root) rides it too,
  by `trunk` degrees and `trunkLag` apart. dragons.js splits a serpent's trunk into three bone links, `vert1..3`,
  and puts the chest, the forelegs, the neck and the head on the last one. With three links 2.09 radians apart,
  their turns sum to nothing, so the head holds its line while the trunk undulates. Down the tail the wave loses
  `taper` of its depth toward the tip (the last link turns `1 - taper` as far), so the tip does not whip into a
  kink.

The defaults (2026-11-05): `neck 22, head .9, tail 174, straight .55, front [-75, 140, 70], hind [-95, 25, -65],
arm 74, hand 8, beat 1.9, handK .25`. This gives a shallow S-curved neck with the head level, a tail that droops a
little and keeps some curve, forelegs tucked tight and hind legs pointed back. A species overrides any of them in its
`flight` block. dragons.js writes one per body plan: the bat- and feather-winged plans have `beat 7` with
`handK .6`, because their folded flutter is only 3 degrees, and `neck 26`. The wyvern trails its legs further back.
The lung has `neck 30, tail 176, straight 0` and a wave of `deg 13, trunk 8, taper .55`, so its body keeps its
curves. Its tail's first link rises 34 degrees at rest, and 176 is the aim that keeps the tail's chord level over a
wave; the old 186 hung the tail down to the ground. Its legs trail back (`hind [-105, 25, -60]`). The feathered
serpent flies rather than swims: `neck 18, tail 177` and a gentler wave (`deg 7, trunk 4`), so it stays near level.

In the game a dragon's `flyT` is 1 while you fly it (`mounted.flying`) and 0 once it lands or you get off. A
peer's mount does the same while it is above the ground. The asset viewer's **fly** box (or `?fly=1`) shows the pose.

**A sky steed ridden** (2026-11-08): the pegasus and the griffin can be ridden too (`mount: { fly: true }`), and
they say `"flight": false` -- no FLIGHT pose is made for them (skeleton.js compiles one for any flying mount unless the
definition says so), because their wings fold by PERCH on the ground and must go on doing so. Ridden, they are posed
as skysteeds.js poses them in the air on their own: `steedRide` (index.html) eases `an.perch` from 1 to 0 as you take
off (the wings unfolding, the beat coming in) and holds the legs by `tuckLegs` -- the forelegs folded under the chest,
the hind legs trailing -- and back as you land. A peer's steed the same from its ops. Mounting one sets its own flights
down (`skysteed.ground`): it will take off on its own again a while after you get off.

## Looking round (2026-11-08)

`an.look` turns a figure's head toward something (a villager greeting you, index.html greetTick; an owl on its
branch). It is shared: `LOOK.head` (.6) of it is the head's own turn about its centre; `LOOK.neck` (.4) is a turn of the
neck about the VERTICAL through the neck's root, in the body's frame -- and the head rides that turn, the way the
grazing nod carries it (a mammal's head hangs beside the neck on the body, so it is swung about that same root; a
person's or a bird's head hangs on the neck and follows it anyway; a mane along the neck goes with it). Before, the
neck's share was added to its own y rotation -- a pill spun about its length, which shows nothing -- so the head turned
alone as if on a pin and the neck stood still.

## Tail sway (2026-11-08)

A tail's root link carries the sway (`anim` axis x, `deg`, `speed`: mammals.js tubeChain); the later links are
chained to it and go with it. Swinging it about its own x was right for a tail that HANGS -- x is across such a tail,
so it swings from side to side -- and wrong for one carried back or up (a cat's, a dog's, a dinosaur's): there x runs
along the tail, so the tail rolled about its own length and its tip stayed where it was (the cat's long tail turned
visibly in place). The sway's axis is now worked out in compileDef (`p.sway`) as the one across the tail's rest chord
-- root to tip, over every link -- and the figure's sideways, in the parent's frame: a hanging tail keeps x, a tail
held level behind swings about the vertical, and either way the whole tail sweeps left and right about where it
starts. A tail laid out sideways (the chord along z) keeps the old axis. writeAnimal applies it as a turn about that
axis at the root link's origin (`swayA`), as the nod and the flight pose are applied, instead of an Euler term.

## A ridden mount does not bob (2026-11-08)

The gait's body bob (`gaits.walk.bob`, twice a stride) is skipped for a figure with `an.ridden` (the mount you ride,
or a peer's: index.html `rideOn`). Your eye does not bob with the saddle, so under a level view the whole beast
jumped up and down -- aloft it was smooth, on the ground it hopped. The legs still step (their IK runs with a bob of
0, so the feet stay planted). With it the eye and the mount both stand at `rideY`, eased toward the ground under them
(index.html), so a bumpy track no longer jolts either; before, both stood at the ground's exact height step by step.

