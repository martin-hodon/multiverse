# The modern age: vehicles, the street, machines, arms, furniture, electronics

Started 2026-11-20. The catalogue had stopped at about 1800 (docs/items.md). This adds the modern world. Most of it is
ITEMS (assets/items/modern/...), built by the one builder `items.js`. Clothes are garments (docs/clothes.md), and
buildings are architecture (docs/architecture.md).

## How it is written

`tools/moderngen.py` runs the generators in `tools/modern/`. Each generator is a module with `GROUPS` (group → catalogue
title) and `write_all()`. It writes `assets/items/modern/<group>/<name>.json` and lists the items under
"Modern: <title>" in `assets/index.json`.

- `python3 tools/moderngen.py` runs every module.
- `python3 tools/moderngen.py rail air` runs only those modules. The catalogue is written under a lock, so modules can
  run side by side.
- `tools/modern/kit.py` holds the parts as small functions (`box rod sphere lathe sweep plate ring loft use hole across
  arc`), `item()`, `write()` and `catalogue()`.
- `node tools/modern/itest.mjs [filter]` builds every modern item in node. It prints the triangles, the bounds, any
  missing material and any NaN.
- `python3 tools/modern/mshot.py OUTDIR name[,name...] [views]` renders review sheets of the items through assets.html.
  - The views are `q side rear front top low in`, or `p:ex/ey/ez:tx/ty/tz` for an eye and a target in metres.
  - It takes one browser at a time, under the shared lock.

THE FRAME (a vehicle, anything standing):

- The origin is on the ground under the item's middle.
- +x is its front, y is up, and z runs across: +z is its right side, like a ship's starboard.
- Lengths are in metres. A part's `at` is `[x, y, z, yaw, pitch, roll]` in degrees.
- `across(x, y)` turns a part's y axis into z, for an axle.
- A wheel's outside face is at +z. Place it with `mirror="z"` to get both sides.

## The primitive added: `loft`

A loft is a body made of ROUNDED-RECTANGLE SECTIONS along +x (items.js `loft`). It is used for a car body, a
glasshouse, a bus, a railway carriage, a fuselage, a fridge's cabinet and anything else smooth and boxy.

- `stations [x, hw, y0, y1, tw?]` give each section's half-width, bottom, top and half-width at the top. A `tw` smaller
  than `hw` makes the sides lean in.
- The stations are smoothed with Catmull-Rom. `seg` sets the pieces per span.
- `round` sets the corners' radius, as [bottom, top] or one number. `corner` sets the corner's samples.
- `holes [{x: [a, b], y: [a, b], side: both|right|left}]` cut windows and doors through the sides, exactly along grid
  lines. Combine with `double: true` to see the inside: the seats through a bus's windows, the door standing open.
- `arches [[x, y, r]]` cut round notches up into both sides for the wheel arches.
- `caps [back, front]` close the ends flat, or leave them open with false.
- A hole or region may also say `z [a, b]` (only that far out from the middle line) and `all: true` (its flat top or
  bottom is cut as well, not only the sides). A car opens its body's top over the cabin this way and keeps the
  shoulders: `{x: [xt, xa], y: [0.9, 9], all: true, z: [0, 0.73]}`.
- `only [regions]` is the complement of `holes`: the loft is kept only inside them. A door is the very body loft it
  closes, with `only` its stretch, so it fits its hole exactly. Several regions make an L (a rear door reaching back
  over its wheel above the arch). An `only` loft has no end caps.
- `bare ["bottom", "top"]` leaves that flat face off. Then the loft is a shell, not a solid: a car's body is open below
  (the floor pan and undertray are their own parts), and its roof is open over the cabin.

## The hinge (2026-11-21)

`{type: "hinge", id, pivot: [x, y, z], axis: [0, 1, 0], max: 65, parts: [...]}` hinges its `parts`. They are written in
the PARENT's frame, exactly where they sit shut, and swing `max` degrees about the axis through `pivot` by a share
open: the part's own `open`, else the item's `open` param, 0..1. A `mirror` on the hinge makes its other side's leaf;
that leaf turns the other way by itself. kit.py has `hinge(id, pivot, parts, axis, max_)` and
`region(x0, x1, y0, y1, side)`.

`buildItem(..., {split: true})` builds the hinged pieces shut into `built.joints` ([{id, pivot, axis, max, open,
groups}]), apart from the rest. `itemObject` hangs each joint on a pivot group, and `userData.setOpen(t, idPrefix)`
swings them. assets.html builds items split and shows an **open** toggle (key O) when there are hinges. mshot.py takes
`open` and `shut` among its views.

**Drawers** (furniture.py `door(..., drawer=depth)`, 2026-11-21): the front on its tray (bottom, two sides, back) as
a `slide` out toward +z by .8 of the depth, the slide placed by `at`, so `door(...) | {"at": [...]}` still stacks
three. The desk's pedestal and the fitted kitchen's drawer and pan-drawer units open with the item's `open`.

**Appliances that open** (electronics.py, street.py, 2026-11-21): a loft cabinet with an inside leaves its front off
(`caps: [true, false]`). A face frame of boxes then covers the gap between the shell and the liner, with a short rod
filling each of the loft's rounded top corners.
- The fridge-freezer has two `double` liner lofts. The fridge holds glass shelves, a crisper and jars. The crisper
  (2026-11-22) is `components/drawer` turned yaw 90: a clear 8 mm slab front (role `bin`, window-glass) with a moulded
  `grip` 8 mm proud, on a clear tray 38 cm deep that slides out .45 of it, `stock` "veg" (three heads of veg, two
  tomatoes); joint `crisper.drawer`. It had been a glass front and a grip over loose veg, with no tray and no slide
  (53 → 50 parts, 15.7 → 15.4 KB). Its door, hinged
  at +z (-110°), carries the liner panel and three bins with bottles, all `inside`. The freezer door hides three
  drawers: slides of .16, all `inside`, kept clear of the door's swing.
- The washing machine's front is two `bitten` plates around the porthole's hole. Behind them are the sleeve, the drum
  and its lifters. The ring door is hinged at -z, and its glass is now `window-glass`, dished into the drum. The
  detergent drawer slides out of a dark housing in a split panel: since 2026-11-22 it is `components/drawer` turned
  yaw 90 (a 14 mm slab front with a moulded `grip` in the `recess` colour, a 25 cm tray, `stock` "powder": two dividers
  and the powder; joint `drawer.drawer`). 32 → 25 parts, 9.4 → 8.1 KB. Its grip is the hand-built one's slim strip
  again (2026-11-22: the slab door's `gh` .012, `gd` .0025 -- 12 mm high, its face 2.5 mm proud, as the old 3 mm box
  centred 1 mm proud stood), not the slab door's default 20 mm, 7 mm proud.
- The microwave's door is hinged at +z, the user's left (-95°). Behind it is the enamel cavity with the light, the
  turntable and a bowl.
- The cooker's body is boxes around the oven's lining (runners, a wire rack, a tin). Its framed, glazed door is hinged
  about z along its bottom front edge (-90°, so it drops flat). The storage drawer slides out .36: since 2026-11-22
  it is `components/drawer` turned yaw 90 (a slab front with the slab door's own hbar, a steel tray 45 cm deep,
  `stock` "sheet" for its baking tray; joint `drawer.drawer`). Its bar's posts are the oven handle's kind again
  (2026-11-22): 8 sides, r 5.6 mm, 15 mm in from the ends (`psides`, `pr`, `inset`), as its own bar-handle had them.
- The telephone box's sides are panel frames around `window-glass`, so its inside shows: the phone on its backboard,
  the directory shelf and the lamp. The whole +x side below the fascia is the door, hinged at -z (100°).

**Joints in components** (items.js, 2026-11-21): a hinge or slide inside a `use`d item joins the user's joints,
named under the part that placed it (`drawers~3.drawer`), and the user's `open` rides down into it, so one
`components/drawer` (now a slide with its tray) opens in the chest of drawers, bureau, dresser, armoire, workbench
and kitchen table alike. A part marked `inside` -- within a hinge or slide (a tray), or anywhere in the item whose `open` is 0 (a
fridge's shelves and food, a microwave's turntable: NOT what shows through glass, an oven's rack, a drum) -- is LEFT OUT of a static build -- the game builds items static and shut, so it costs nothing there; the viewer builds `split` and keeps
it. (`open` is reserved for this share: the shears' blade angle is `gape`.)

**Pieces of one loft** (kit.py, 2026-11-21): a vehicle writes each loft ONCE, as a value, and derives the rest.
`cut(L, regions)` is the loft with those openings, and `piece(L, regions, id, **over)` is the part that closes them:
the same stations, rounding and arches, keeping only those regions, each drawn in by the 6 mm shut line, with no
holes or `bare` of its own (`over` can give it some: the lorry door's window). A car's body, its four doors and its
tailgate are `BODY`, `cut(BODY, ...)` and `piece(BODY, ...)`, so a change to the body's shape carries into its doors.

**A slide** (`{type: "slide", id, move: [x, y, z], parts}`, kit.py `slide(id, move, parts)`) moves its parts by
`move` metres times the share open. Examples: a van's side door back along its rail, a coach's plug leaf out and along
the side, a drawer. Split, its joint carries `move` (world) in place of an angle.

**A joint's `range`** `[a, b]` (2026-11-22): it moves only while the share runs from a to b, so joints can follow
one another. kit.py `plug_slide(id, move, parts, out=.25)` nests two slides: `<id>Out` steps the door out of its
opening by move's z over the first quarter, then `<id>` runs it back along the rail by the rest. The door never
passes through the skin. The van's side door and the helicopter's cabin doors use it. The viewer holds a door
part-way with `__assets.openAt(t)`, and mshot takes `open:0.4` as a step.

**Hinges on hinges.** A hinge or slide inside a hinge's parts rides on it. Shut, it is built into the parent joint's
`kids` (its pivot and axis as the item stands shut). `itemObject` nests its pivot group in the parent's, so a
jack-knife bus door is a leaf hinged at the jamb, with the second leaf hinged on its far edge turning back by twice the
angle (vehicles.py `folding_door`). Unsplit builds just compose the matrices.

**Drawers** (furniture.py `door(..., drawer=depth)`) are the period `components/drawer` with `front` "slab": the
`slab-door` on its tray, sliding out .8 of the depth; its joint is `<id>.drawer`. The fridge-freezer's three freezer
drawers are the same component turned yaw 90 (a slab front with a moulded `grip`, `stock` packs coloured by `goods` /
`goods2` on the use). The cooker's storage drawer is one too (`stock` "sheet": a baking sheet on the tray's floor,
role goods; 2026-11-22). Its pull is the slab door's hbar with `stand` .025, `r` .007, `sides` 10 and posts `pr`
.0056, `psides` 8, `inset` .015 -- the oven door handle's kind a size smaller (the oven's: stand 35 mm, r 9, posts r
7.2, 8 sides, 15 mm in), exactly as its own bar-handle was before the drawer became the component (both `slab-door`
and `components/drawer` take `stand`, `r`, `sides`, `pr`, `psides` and `inset` and pass them on to `bar-handle`;
their defaults are the bar's own, so every other front is unchanged). Their `pull` "grip" takes `gh` (its height,
20 mm) and `gd` (how far its face stands proud, 7 mm; 3 mm more is sunk in the front) -- the washing machine's is the
slim 12 mm, 2.5 mm strip. The fridge's crisper is the component too (`stock` "veg"). The fridge's two door handles stay electronics.py `bar_handle` uses of
`bar-handle` (upright, 10 sides): they sit on the doors' lofts, not on a slab, so slab-door has nothing to give them.

**Which way a door stands** (2026-11-22). Both door components look +z, centred on their origin in x and y, and
differ only in where z 0 is: `slab-door` has its BACK at z 0 (the face at t: a carcass front set on the carcass's
front edge, the drawer's `back`), the period `panel-door` has its FACE at z 0 (the frame goes back to -t: a door
flush in its case). Each takes `anchor` -- 0 back at z 0, 1 face at z 0 -- so either stands the other's way;
slab-door's default is 0, panel-door's 1, and every current build is unchanged. A panel-door hinge (`swing` 1)
keeps its pivot on the face's edge wherever the face is. Their roles still differ (`front` vs `wood`), and the
slab has no hinge of its own (furniture.py `door(swing=)` wraps it), so swapping one for the other in a `use`
needs the role mapped and the swing done the right way.

**Shaker fronts** (2026-11-22). `slab-door` takes `frame` (0, the default: the flat slab): above 0 it puts the
period `panel-door` in the slab's place -- `anchor` 0 so it stands as the slab does, `knob` 0 (panel-door's own knob
off; the slab's pull goes on the frame's face), `s` = frame (the stiles' and rails' width), its `wood` mapped to the
slab's `front`. `components/drawer` passes `frame` to its slab, and furniture.py `door(..., frame=)` to either, so a
door, a hinged door and a drawer all take it. The fitted kitchen was tried with 60 mm frames on every front (renders
in the reuse4 scratch, shots-before/k vs shots-trial/k): the frames read close up but hardly at the kitchen's own
distance, the sunk panel is the same colour and lit flat, the 17 cm drawer's panel is a 5 cm strip under its bar.
Not clearly better then.

**The sunk panel's role** (2026-11-22). `panel-door`'s panel is role `panel` (its own materials: `"panel": "wood"`,
so every period build is the same), and `slab-door` has `"panel": "front"`, which the shaker use passes down with
the other roles (it maps only `wood` to `front`; it must NOT map `panel` to `panel`, which would hide the parent's).
An item -- or a use of slab-door, the drawer or furniture.py `door(mats=)` -- gives `panel` a colour and the shaker's
panel takes it. A role leaks down by name: an item with a `panel` role of its own (the washing machine's and the
cooker's control panels) would colour a shaker front's panel with it; neither has one. Tried again on the kitchen
with the panel a shade darker (reuse5 scratch: shots-trial/flat-white, shaker-white, shaker-slate, seed3, seed6),
it reads at the kitchen's own distance -- the frames show on every unit, the drawers look like drawers -- so the
kitchen now picks: its `frame` param is `{pick: [0, 0.06]}` (flat slabs or shaker; the 17 cm drawer's frame is
`frame * 2 / 3`), and its fronts are `colourways` pairing each front with its panel (white / #d0d0ca, slate #3f4a57 /
#333c47, cream #c9c1b0 / #b5ad9b, sage #556b5a / #47594b, oak / walnut, red #8c2f2f / #782828). A shaker kitchen is
4632 triangles to the flat one's 4008. (2026-11-22) The colourway is now a param, `colourway: {pick: [white, slate,
cream, sage, oak, red]}` (items.js honours a string `P.colourway`): drawn second, after `frame`, it spreads seeds
1-40 9 red / 5 sage / 6 slate / 5 white / 7 cream / 8 oak; drawn third, as the item's `colourways` had been, the
same seeds gave 13 white to 3 slate. The worktop's pick moves to the next draw.

**Cabinet doors** (furniture.py `door(..., swing="left" | "right")`) wrap the `slab-door` in a hinge at that edge,
opening out toward +z (105°); `mirror="x"` gives the pair. Use it only where there is an inside to see: the
wardrobe's carcass is boards (sides, top, bottom, back) holding the hat shelf, the rail with its clothes and the shoe
board.

**Caps are cut by height only.** A loft's end cap is clipped to the band of y that the `only` regions reaching that
end keep, less the `all` holes (without `z`) reaching it from above or below. That is how a hatch's tailgate takes the
upper part of the body's rear face while the body keeps the lower. A window in a cap is not possible: a cab front with
a windscreen leaves that cap off (`caps`) and puts panels round the glass (the lorry).

## See-through glass (2026-11-21)

A library material may carry `opacity` (below 1). It is then drawn transparent, writing no depth (archmat.js
finishMaterial). `window-glass` (opacity .42, both sides) is a window's glass: the car's glasshouse and door panes.
`glass` stays opaque, because it is a screen's, a lamp's or a phone's face too.

## A car, as built now (vehicles.py car_parts)

- The body is a shell (`bare: bottom`, `double`), cut by the door holes and the cabin's opening in its top.
- The glasshouse is `window-glass`, its door panes cut out. The roof over it is a shell, its side windows cut.
- There is a headliner just inside the glass.
- Each door is a `hinge` at its front edge, mirrored. It holds the body's stretch (`only`), the glass's stretch, its
  waist trim, its handle, a `door-card` inside, and on the front door the wing mirror.
- The tailgate (the spec's `gate`: x, y, hinge, roof) is a `hinge` about z at the roof's edge. A hatch's takes the
  rear face above y .52, the glass and roof behind the hinge, the rear screen, spoiler, wiper, lamps and plate. A
  saloon's boot lid takes the deck and the face above y .72; its rear screen stays fixed.
- Inside: the carpeted floor, the boot floor, the firewall, `car-dash` (its dials, centre screen, vents and the
  `steering-wheel`), the console and gear lever, two `car-seat`s and the rear bench (`car-seat` with `bolster: 0`).
- Under it (2026-11-22): the floor pan (`kit.pan`) under the shell's open bottom, round the wheel gaps
  (`kit.arch_gap`), and the wheel tubs and arch liners (`kit.arches(..., inner, cup=True, skin=, low=, floor=)`). See
  "Undersides and wheel arches" below.

## Undersides and wheel arches (2026-11-22)

The complaint was "the bottom of cars looks wrong as it wraps wheels and there is no insides". From below and low down
(scratch under/b1 before, a2-a7 after), every road vehicle had some of these:

- **The wheelhouse was a drum** (a lathe, radius r + .05, the full 360°) wrapped round and under the tyre to the
  ground.
- **The arch lip was a flat plate** at one z. On a tumblehome it stood proud of the skin, with teeth and tabs hanging
  below the sill.
- **Flat bottoms ran through the wheels:** the bus's and coach's shells, the coach's lining, the lorry's and mixer's
  cab lofts, and the van's ply bay floor.
- **No floor pan** outboard of the undertrays, so the painted or plywood inside of the body showed from below.
- **A loft's arch notch pushed its corner points down** past the section's bottom to the circle's foot (items.js
  `snap`), a spike of skin hanging round the wheel: the car's sill, the bus's lining, and the tram's red skirt.

The helpers now live in kit.py, shared by vehicles.py and machines.py:

- `body_arches(xs, r, gap)` -- the loft's `arches` notches.
- `arches(xs, r, z, track, inner, cup, skin, low, floor, notch, deep)`:
  - With `skin` (z of the body's side at x, y), the lip is a sweep laid on the skin, `deep` thick, reaching in. With
    `low` (the body's bottom at x), its ends stop where the notch meets the bottom. Without `skin` it is the old plate.
  - With `floor` (the pan's underside, a height or a function of x), the house is an arc kept above it, open below.
    A `cup`'s inner wall is then the circle's segment above the floor (`tub{i}`, a plate), not a pie down to the hub.
- `arch_gap(x, r, floor)` -- the x span the house's arc leaves open at the floor's height.
- `pan(id, mat, st, round, x0, x1, gaps, zin)` -- a floor pan following a `bare: ["bottom"]` loft's bottom and its
  rounded sides. With gaps it is a middle strip to `zin` plus full-width strips between the gaps.
  - A loft's flat bottom is ONE quad from z 0 to the corner, and a hole tests the quad's centre. So a z-limited hole
    cannot cut a wheel gap out of it; hence the strips.

items.js `snap`: a point slid out onto an arch's circle no longer goes below the section's bottom; there it slides
along x at its own height. This changes the car, saloon, taxi, bus and tram.

Per vehicle:

- **Car, saloon, taxi:** the pan replaces the undertray and side trays; the arcs and skin lips are added.
- **Van:** pans under the cab (`lower`) and the box (`cargo`). The bay floor is split round the tubs, and the wheel
  box over each rear tub is a ply hood (lathe arc), no longer a box standing in it.
- **Bus, coach:** shell `bare: bottom` plus pan (the coach's lining bare too). Skin lips; the arcs are open below.
- **Lorry:** cab bare bottom plus pan round the front wheels. Skin lip with `notch` r + .08. A `subframe` (runners)
  under the box, which had floated 10 cm over the rails.
- **Mixer truck:** the cab loft is notched (`body_arches`), with a bare bottom, pan, tubs and lips. The cab steps
  moved behind the front tyre, where they had stood in it.
- **Forklift:**
  - The chassis is narrowed to the gap between the wheels (z +-.29), with a full-width `deck` over them.
  - The counterweight is notched round the steered wheels, with a bare bottom, pan and dark wells.
  - It has no lip, because the counterweight ends over the axle.
  - The step is moved under the deck.
  - The front rims had their backs open, and the orange frame showed through them. The `wheel` component has a
    `seal` param (default 0) that adds a tyre-coloured band under the bead, from wall to wall, which closes the open lathe behind the rim. The forklift's wheels use
    `seal: 1`.
- **Tractor:** the cab and cab base are narrowed to z +-.62 (they had stood 4 cm into the rear tyres).
- **Clean:** motorcycle, bicycle, excavator, bulldozer, and the carriages (stagecoach, brougham, hansom, gig,
  omnibus), which have open frames with their wheels outside the bodies.

## Steering (2026-11-22)

**The engine (items.js, architecture.js, assets.html).** A hinge may carry `by: "<param>"`. It is then turned by
that param, not by `open`. The value is signed and clamped to -1..1: `max * P[by]` degrees, 0 when the param is
missing, so a static build is straight and unchanged. Without `by`, a hinge is as before.
- A split build lists the joint with its `by`. `itemObject` clamps such joints to -1..1, and `setOpen` leaves them
  alone. `userData.setDrive(name, t)` turns every joint whose `by` is `name`.
- Joint params are not passed into a `use`d component; only `open` rides down. So a steer joint lives in the
  vehicle, round its `use("wheel")`.
- The field is `by`, not `drive`, because `car-dash` already has a `drive` param (left- or right-hand drive).
- The viewer shows a **steer** slider (-1..1) when an item has a `by: "steer"` joint. `[` and `]` step it by .25,
  and `__assets.drive(name, t)` sets it from a script. The open toggle shows only when some joint has no `by`.
- `mshot.py` takes a view step `steer:0.8`, which applies to the views after it.

**The kit (tools/modern/kit.py).**
- `steer(id, pivot, parts, max_=35, by="steer")` returns two hinges about the vertical through `pivot`. The parts
  are written for the right side (+z). The left one is the same parts with `stretch [1,1,-1]` and `max -max_`, so
  both wheels turn the same way (+1 is full lock to the left).
- `steer_in(track, r, w, lock=35, gap=.03)` is how far in from the centre line the pan and tub inner wall may come,
  so that a tyre of radius r and width w swung to `lock` clears them.
- `arches(inner=...)` and `pan(zin=...)` take a list (per arch, per gap), so the front arches can be deeper than the
  rear ones. The pan's middle strip is built in pieces (`{id}m{k}`).

**Who steers, and what had to move.** Each was checked at -1, -.5, .5 and 1 by a ray-triangle test (the steered
joint's triangles against all the others) and in renders from low and from underneath.
- **Car, saloon, taxi:** 35°. The front pan gap and tub walls come in to `steer_in` (about .51 from the centre);
  the rear stay as they were.
- **Van:** 35°. The cab floor and firewall had always run through the front tyres. They are now 2*zinF wide, with
  outboard floor strips ahead of and behind the wheels. The front pan and arches use zinF.
- **Bus:** 35°. The lining's bottom crossed the wheels; it is now `bare: bottom`.
- **Coach:** 35°. The lining grazed the tyre tops; it now has `body_arches` cut in it (+3.3k tris).
- **Lorry:** 35°. Nothing had to change; its tubs were already wide enough.
- **Mixer truck:** 35°. Each front wheel has a knuckle stub that turns with it. The front axle ends at +-.68.
- **Tractor:** 35°. The front wheels and their guards turn together. The front axle is 1.1 wide (it was 1.2), and
  the bonnet is narrowed (half-width .37 to .32) so the lug tyres clear it.
- **Forklift:** rear steer, 60°. The single trailing wheel turns. The counterweight's front cap is cut away below
  the deck, the chassis is narrowed (1.29 x .58), and the pan and tubs come in to `steer_in(.8, .28, .18, 60)`.
- **Motorcycle:** 30°, about the head tube's own raked axis (-.359, .933, 0) through (.43, 1.0, 0). The front
  wheel, fork, yokes, bars, grips, levers, clocks, lamp, indicators, guard and mirrors all turn. A `headTube` was
  added. The headers, tank front, radiator and frame spars were moved back, and the front guard's arc was
  shortened, so nothing is hit at lock. The yokes and lamp shell still touch the head tube, which is expected
  since they share its axis.
- Not steered: the bicycle, the carriages and the plant machines (excavator and bulldozer are tracked).

## The other vehicles' doors and insides (2026-11-21)

- **The van.**
  - The cab's doors are hinged at the A-pillar; their skins are L-shaped, clear of the front arch.
  - The right side door slides back on its rail.
  - The twin rear leaves are hinged at the corners (100°).
  - Inside the cab: the floor, the firewall, `car-dash`, the driver's `car-seat` and a two-seat bench.
  - A steel bulkhead with a window separates the cab from the bay.
  - The bay has a plywood lining (a shell loft just inside the cargo loft), its floor, the wheel boxes and tie rails.
  - Underneath: an undertray, and the wheel tubs as cups.
- **The city bus.** Its three double doors are jack-knife pairs, shut flush in the side (`folding_door`, nested
  hinges); open, they fold into the bus.
- **The coach.** Its two swing-plug leaves sit shut in the openings; open, they slide out and along the side.
- **The mixer truck** (machines.py, 2026-11-22). The cab is a real cab like the lorry's. It is a `double` loft,
  with door and rear-window openings cut, a bare bottom and arches. The doors are pieces of the cab loft, hinged at
  the front edge (70°), each with a window cut, a `window-glass` pane, a handle and a `door-card`. The front is
  made of panels round a `window-glass` windscreen, with quarter lights. Inside: a rubber-mat floor and engine
  hump, `car-dash`, two `car-seat`s and a grab rod. The seat marker is at the driver's seat.
- **The passenger carriage** (rail.py): its four plug doors sit shut in their doorways; open, they slide out and
  inboard along the side.
- **The lorry.**
  - The cab is a shell; its doors are hinged at the front edge, each with a window cut in its skin, a pane and a
    `door-card`.
  - Its windows are `window-glass`, and its front is panels round the windscreen.
  - Inside: the floor and engine hump, `car-dash`, two `car-seat`s, and the sleeper's bunk with its curtain.
  - The box's rear doors are hinged at the corners and swing 265° round flat against the sides. The box is open
    inside (`double`).
- **The airliner** (air.py). L1 is a `piece` of the fuselage with its own porthole and a lining (a piece of an inset
  loft). It moves in parallel, as on the real door: the arm is hinged at the forward jamb inside the skin (-110°), and
  the door is hinged on the arm's end (+110°). The door stays parallel to the skin and ends ~.95 m forward and ~.45 m
  out. Since 2026-11-22 air.py's `plug_door(name, x0, x1, side)` builds it from an x range and a side (its own
  lining loft, porthole, arm and sill), so all four doors are real: L1/R1 forward, L2/R2 aft by a carpeted aft floor
  and galley. Each opens forward (the right side's angles mirrored). The lavatory moved forward off R1's opening.
- **The light aeroplane.** Its doors are cut from the fuselage and hinged at the front edge, both sides. Each has a
  `window-glass` pane (a piece of the same loft), a trim card and an armrest. The stripe is broken at the door, and
  its middle stretch rides on the door.
- **The helicopter.** The front doors are hinged at the front edge. The rear doors slide out and back (.95 m) under a
  rail. All of them are glazed pieces of the body with a trim card. Open, the rear door's tail stands off the
  narrowing boom.
- **The brougham** (carriages.py). Its doors are hinged at the front edge (72°), mirrored. They moved .16 m forward
  so the rear edge clears the rear wheel as it swings. Each has the drop window let down (a hole, the glass's top
  edge at the sill, the strap), the belt, a cushioned lining and a pull.
- **The hansom.** The knee doors across the front are hinged at the body's sides and fold forward and out (95°),
  clear of the shafts.
- **The stagecoach.** Its doors are now real: cut from the egg-shaped body and hinged at the rear edge (the handle
  is at the front), opening 85°. The bottom is at y 1.12 so the door clears the rear wheel's tyre by the hinge. Each
  has its window let down, the belt and a leather lining.
- **The tram** (rail.py, 2026-11-22). Its sixteen leaves now sit shut in their doorways (they stood open outside
  the body before). Open, each is a `plug_slide`: out 5.5 cm, then .655 m along the side, mirrored across.
- **The box wagon.** Two doorways are cut in each side of the now `double` body. Each door is a `plug_slide` that
  steps out .04 m and runs 2.4 m along the extended rails, carrying its ribs and handle. Inside (`inside`): a plank
  floor, battens, a pallet of cartons and sacks.
- **The electric locomotive.** Each cab door is a `piece` of the body loft, hinged at its rear edge (90°), with
  its window and grip. Inside: a lining loft (`shell_over` the body, .06 in), a bulkhead and nose wall, the floor,
  the desk with screens and the driver's seat.
- **The diesel locomotive.** The cab is a `double` loft open at the back. The rear wall has a door notch, and the
  door is hinged at the hood side (90°), folding flat against the long hood. Inside: the floor, the control stand,
  the front desk, a heater and two seats.
- **The container** (sea.py, `components/container`, `full` only). The end doors are hinged at the corner posts
  and swing 265° round flat against the sides. The box is open inside: a floor, a roof, the sides and the blind
  end. A `load` param (picked 1, 1, 0) puts a pallet of strapped cartons, a crate and a drum inside. The ship's
  stacked boxes (`full` 0) stay solid blocks.
- **The post box** (street.py). The pillar is an open arc behind a door cut from its front (an arc of the same
  lathe), hinged at one edge (110°). Inside (`inside`): a lining, a heap of letters and a parcel.

## Materials added (assets/items/materials.json)

- rubber
- chrome, aluminium, steel-blue, gunmetal
- glass (tinted), glass-light
- plastic-black, plastic-grey, plastic-white, polymer
- the car paints: paint-red, blue, navy, white, silver, black, yellow, green, orange, cream, maroon, grey
- asphalt, concrete, tarmac-line
- screen
- lamp, lamp-red, lamp-amber, lamp-green
- upholstery, upholstery-red, upholstery-grey, carpet-grey
- olive-drab

## What there is (assets/items/modern/<group>/, the generator in brackets)

- **vehicles** (vehicles.py):
  - car (5-door hatchback), saloon, taxi
  - van, lorry, motorcycle, bicycle
  - city bus (open inside: 3 folding double doors, seats, poles, the driver's station)
  - coach (high floor, luggage bays, stairwells)
- **rail** (rail.py):
  - electric, diesel and steam (4-4-0 with tender) locomotives
  - passenger carriage (open inside: seats facing over tables, racks, vestibules)
  - box wagon, container flat
  - two-section tram
- **air** (air.py):
  - airliner (A320 class: the cabin inside through the open L1 door, galley, cockpit)
  - light plane
  - helicopter
- **sea** (sea.py): a 220 m container ship stacked with containers; the 40 ft and 20 ft containers.
- **carriages** (carriages.py): stagecoach, brougham, hansom cab, gig, horse omnibus.
- **machines** (machines.py): excavator, bulldozer, tractor, forklift, tower crane, mixer truck.
- **arms** (arms.py):
  - revolver, pistol
  - bolt rifle (`scope`), pump shotgun
  - assault rifle, submachine gun, light machine gun (`bipod`)
  - Hand guns hold like the flintlock pistol; long guns like the musket, with `grip2` on the fore-end.
- **street** (street.py):
  - traffic and pedestrian lights (`phase`)
  - signs: stop, give way, speed limits, no entry, crossing, parking, direction
  - modern and heritage street lamps
  - bus stop, bollard, crash barrier, guard rail
  - hydrant, post box, litter bin, bench, phone box, parking meter
- **infra** (infra.py):
  - roads: straight, curve, T-junction, crossroads, zebra crossing, roundabout
  - rail track: straight, curve, points, buffer stop, level crossing with barrier
  - platform, train shed, station hall, footbridge, departure board, ticket machine, clock
  - the bus station and its shelters
  - runway, taxiway, terminal, control tower, jet bridge, hangar
  - Tiles meet end to end; each `_about` gives its tile length.
- **furniture** (furniture.py):
  - sofa, armchair, office chair, desk
  - dining table and chair, coffee table, bed, wardrobe, bookshelf, TV stand
  - fitted kitchen, bar stool, floor lamp, desk lamp
  - Furniture keeps the period furniture's frame: front +z, seats marked.
- **electronics** (electronics.py):
  - desktop computer, laptop, television
  - fridge-freezer, washing machine, microwave, cooker
  - smartphone, radio, loudspeaker, printer, desk phone
  - Their front is +x, like `screen`.

## Components (assets/items/modern/components)

| component | what | made in | used by |
|---|---|---|---|
| `wheel` | a pneumatic road wheel: tyre, dished rim, spokes, hub, nuts (`r w rim spokes`) | parts | cars, buses, lorries, machines, aircraft gear |
| `cast-wheel` | a motorcycle's cast wheel with 1-2 brake discs | vehicles | motorcycle |
| `spoked-wheel` | a wire-spoked wheel: tyre, rim, spokes laced from the hub's two flanges (`r t n sr hubW hubR`) | parts | bicycle, wheelchair (its axle turned across, the push rim the chair's own) |
| `carriage-wheel` | a wooden wheel: tapered spokes, felloe, iron tyre, nave | carriages | every carriage |
| `lug-wheel` | a tractor's chevron-lugged tyre | machines | tractor |
| `track` | a crawler track: shoes, sprocket, idler, rollers | machines | excavator, bulldozer |
| `cab` | a glazed operator's cab, its origin on its floor's middle: corner posts, floor, head, overhanging roof, glass all round above a painted `sill`, a door's frame on side `door` (-1/1; 0 none) -- `hx hy hz post`; roles frame, roof, glass (machines.py `cab()` places it by its box) | machines | excavator, bulldozer, tractor, tower crane |
| `loco-wheel` | a spoked driving wheel with crank and counterweight | rail | steam locomotive |
| `bogie` | a two-axle railway truck on the standard gauge | parts | every railway vehicle |
| `seat` / `seat-row` | an upholstered seat; a row of n cheaper ones | parts / rail | cars, bus, coach, carriage, tram, aircraft |
| `steering-wheel`, `wing-mirror`, `door-leaf` | the driver's wheel; a mirror out or hanging; a glazed door leaf | vehicles | cars, bus, coach, lorry, van; the mixer truck's hanging mirror |
| `car-seat`, `car-dash`, `door-card` | a bucket seat or (`bolster` 0) a bench; a dashboard with dials, screen, vents and the wheel; a door's inside trim | vehicles | car, saloon, taxi |
| `door-bin` | a door's bin: `floor`, front `lip` and two `end`s (`w d h lip t`); roles `liner` (floor and ends) and `bin` (the clear front lip, window-glass by default), inherited from the user by name | electronics | the fridge-freezer's three door bins |
| `lamp` / `carriage-lamp` | a round or square lens in its bezel; a coach's lantern | parts / carriages | every vehicle |
| `screen` | a flat screen in a bezel, facing +x | parts | electronics, dashboards, departure boards, the electric loco's desk screens (laid back 60°) |
| `rotor` | blades round a hub | parts | helicopter, propellers |
| `pantograph` | a current collector (`h`) | rail | electric loco, tram |
| `container` | an ISO container (`L W H`), corrugated, doors at one end | sea | ship, container flat, a port |
| `stockless-anchor` | | sea | ship |
| `pole`, `sign-face`, `signal-head` | a street pole; a layered sign face picked by `sign`; a signal's head (`kind`, `phase`) | street | every sign, signal, lamp, meter |
| `slab-door`, `star-base` | a carcass's flat door or drawer front with its pull (`pull` hbar, vbar, knob, lip, grip, none; a bar's `stand`, `r`, `sides`, `pr`, `psides`, `inset` passed on to `bar-handle`; the grip `gh` high, `gd` proud), its BACK at z 0 (`anchor` 1: its face at z 0, as `panel-door`); `frame` > 0: a shaker front (`panel-door`, anchor 0, no knob, role front; its sunk panel role `panel`, the front unless mapped); a swivel chair's base | furniture | kitchen, wardrobe, desk, TV stand, the drawers' slab fronts (the cooker's, the freezer's, the washing machine's too); office chair, bar stool |
| `bar-handle` | a round bar on two posts standing off its face (+z): `l`, `stand`, `along` across / upright, `r`, `pr`, `inset`, `sides`, `psides` | furniture | the slab door's hbar / vbar (so the cooker's drawer pull, its posts `pr psides inset` passed through); the fridge's two door handles, the cooker's oven door handle (electronics.py `bar_handle`, turned yaw 90 to face +x) |
| `components/drawer` (period) | a drawer on a slide, its tray `inside`: `front` joinery (knobs, ring pulls) or slab (the `slab-door`, `t` from `back`, its `pull hx hy hl stand r sides pr psides inset gh gd frame`), the tray's `floor lift wall rise gap`, `travel`, `stock` (1: two packs, roles goods / goods2; "sheet": a baking sheet, role goods; "powder": two dividers, role tray, and powder, role goods; "veg": three heads of veg, role goods, and two tomatoes, role goods2); role `tray`; its face at z 0 (a slab's at `back` + t) | (hand JSON) | the period chests, bureau, dresser, workbench; furniture.py `door(drawer=)` (kitchen, desk); the fridge's freezer drawers; the cooker's storage drawer; the washing machine's detergent drawer; the fridge's crisper |
| `components/panel-door` (period) | a frame-and-panel door, its FACE at z 0 (`anchor` 0: its back at z 0, as `slab-door`); `swing` 1 hinged; `knob` 0: no knob; the sunk panel role `panel` (its `wood` by default) | (hand JSON) | the period cupboard, armoire, dresser, longcase clock, Chinese cabinet, Gothic chest and chair, box bed, four-poster, settle; `slab-door`'s shaker front (the kitchen's shaker seeds) |
| `kiosk-sign` | one side's fascia of the telephone box: the white sign and TELEPHONE in strokes, facing +x | street | phone box (on its four sides, by yaw) |

**Repeats instead of copies** (kit.py, 2026-11-22). The biggest files wrote every pane, post and seat out. Three
helpers now fold them, and every item comes out the same, triangle for triangle (fingerprinted over seeds 1-3, shut
and split into joints, positions to 0.1 mm, each group's material):

- `each(id, copies)` turns a run of parts that differ only by even steps into ONE part laid by items.js `each`: every
  number that changes becomes `b + s * i`. A step that is no round number (a 16 m wall in seven bays) is written
  `round((b + s * i) * 10000) / 10000`, the same 4-decimal rounding each copy had in the json. A run along a curve
  passes `like=`, the part with its expressions written by hand, and `each` checks it against every copy (the points'
  48 timbers under the diverging rail, a barrel roof's facets). A run that does not fold is written out as before.
  A copy's `when` may name its own param: `"w{i}"` (the footbridge's open bays).
- `merge(parts)` makes parts that are the same but for `at` one part with a list of placements (a wall's piers front
  and back, both wings, the bus's seats).
- A group repeated by turning goes into a component: `kiosk-sign`, placed at yaw 0/90/180/-90.
- `kit.window_wall` (was `infra.win_wall`) lays each wall's piers, mullions and solid bays as runs (split where a door
  breaks the run).

| item | parts | json |
|---|---|---|
| infra/station-hall | 248 → 62 | 42.5 → 15.6 KB |
| infra/bus-station | 164 → 54 | 29.5 → 13.9 KB |
| infra/terminal | 102 → 51 | 30.4 → 19.0 KB |
| infra/hangar | 92 → 22 | 22.2 → 10.6 KB |
| infra/points | 77 → 26 | 25.9 → 17.1 KB |
| infra/footbridge | 60 → 18 | 13.5 → 5.6 KB |
| infra/train-shed | 32 → 15 | 13.3 → 11.2 KB |
| street/phone-box | 173 → 25 (+ kiosk-sign, 26) | 52.2 → 8.7 KB (+ 8.9) |
| vehicles/bus | 132 → 71 | 45.1 → 32.5 KB |
| vehicles/coach | 128 → 60 | 41.3 → 25.8 KB |
| rail/carriage | 89 → 40 | 31.0 → 20.9 KB |

**Runs and grids** (2026-11-22, second pass). `kit.runs(id, parts, key=None, least=3)` takes a whole list in order and
cuts it where that gives the fewest parts, each stretch that folds one `each` part (what folds with nothing stays
as it was; `key` keeps apart what must not share a run). A stretch may also fold as a GRID, m copies a row: a number
`b + R * floor(i / m) + C * (i - m * floor(i / m))` -- a 3 x 3 block of kegs, a second course laid in the first's
hollows (a partial last row), toes or butts to alternate sides (m = 2). Every fold is checked against its copies,
and the expressions never use exponent notation (expr.js cannot read `4e-05`; `_num` writes `0.00004`). Parts that
carry a hinge or a slide fold too (2026-11-22, below: their joints are named by the copy). propgen.py and craftgen.py import it from kit (the woodpile, the carts, the harp). The same fingerprints as above,
plus each cart built at every `load`, -1..12:

| item | parts | json |
|---|---|---|
| components/cart-large (propgen) | 208 → 52 | 40.1 → 12.5 KB |
| components/cart-medium | 131 → 45 | 25.8 → 11.0 KB |
| components/cart-small | 55 → 35 | 11.5 → 8.4 KB |
| furniture/woodpile (propgen) | 22 → 10 | 4.7 → 2.9 KB |
| tools/harp (craftgen; strings, one run a straight stretch of the neck) | 24 → 11 | 7.3 → 5.4 KB |
| sea/container-ship (hatch coamings, covers, lashing bridges; the house's windows) | 152 → 102 | 88.5 → 78.7 KB |
| air/airliner (29 seat rows) | 88 → 60 | 49.4 → 41.5 KB |
| infra/railway-station (tracks, platform segments, signals) | 44 → 18 | 11.8 → 5.0 KB |
| electronics/desktop-computer (the numeric pad's rows) | 38 → 35 | 11.3 → 10.4 KB |

Left as they are: the globe's 29 land caps (each its own size, place and colour: data, not a run), the sign faces'
and kiosk signs' letters (each glyph its own outline), the crossroads' and roundabout's four corners (mirrored
outlines: a fold would put an expression on every point).

**Runs that hold joints** (2026-11-22). A hinge or slide laid by `each` is named by its copy: `leafA#3` (`leafA#3~2`
its mirrored twin), and one inside a copied `use` is the copy's, `load 10 crate#2.lid`. Nothing reads a joint's name
but `itemObject`, which names each pivot group by it, and `setOpen(t, prefix)`, which swings the joints whose names
start with the prefix (no caller passes one: assets.html swings them all). The game builds items static and shut,
and nothing saves an open state, so the renaming is free. kit.py `_fold` keeps a part's id inside a run where every
copy has the same id (the tram's inner `leaf` slide). It refuses to fold a run whose inner hinges or slides have
different ids, so no joint loses its name. Fingerprinted as above, with the joints compared by place rather than
name (pivot, axis, max, move, range, open, kids and their own triangles):

The carts' crates (load 10) stood on their sides with their lids against the side boards; they now stand lid up, long side across. The crate has a `lift` param (degrees its lid can rise, 105): a lower-course crate with another on it gets `lift` 0, the front one 88, so it stops upright against the course above (tools/propgen.py `loads`).

| item | parts | json |
|---|---|---|
| components/cart-large (7 crates: one grid run; 4 hampers: two runs) | 52 → 44 | 12.5 → 11.3 KB |
| components/cart-medium | 45 → 43 | 11.0 → 10.7 KB |
| rail/tram (16 plug-sliding leaves: one `each` grid of 4 a section, mirrored) | 58 → 52 | 23.6 → 19.0 KB |

**Seeded runs** (2026-11-22). Item expressions now have `rnd(a, b, ...)` (docs/items.md), a draw from the item's
seed, so a run whose numbers were drawn in the generator by `random.Random` folds too. The bookshelf's books (121
boxes, each width, height and depth drawn by `random.Random(1966)`) are one `each` part a colour per packed run (a row,
or the stretch either side of a leaning book or the flat stack): book j spans edge j to edge j + 1, each edge at
`x0 + s * j + 0.02 * (rnd(run, j) - 0.5)` and the run's ends held still, so the books touch without a gap or an
overlap and every row reaches both sides (the old rows stopped short where the next drawn book did not fit); its
height and depth `rnd(run, j, 1)`, `rnd(run, j, 2)`. 126 → 40 parts, 22.5 → 18.0 KB, and every seed's books are its
own. The other generators' draws were already folded (the container ship's boxes: one `use` a colour with its list of
places; the post box's letters: two parts) or too few to matter (the wardrobe's 8 garments).

## Reusable parts: the design

The same few constructions recur across the groups, and new items should be built from them:

1. **A loft body, cut and lined.** A car is three lofts: the lower body; the glasshouse in `glass`; and the roof shell
   over the glasshouse, with the side windows cut as holes in it.

   Anything you walk into is a single shell plus a lining loft just inside it, both cut by the same window and door
   holes. Its floor is broken round the wheel housings, and the housings double as seat podiums. This is how the bus,
   coach, carriage, tram, airliner, light plane and helicopter are built, and later a fridge and a stagecoach too.
2. **Running gear as a set.** Two mirrored wheels form an axle set: the arch lip and wheelhouse drum on road vehicles,
   bogies on rail, a wheel pair and axle bed on carriages.

   The same set comes in its other forms: crawler tracks on machines; gear legs on aircraft.
3. **Openings with leaves.** Door jambs with folding, swing or sliding leaves standing open, and glazed panels
   (`door-leaf`, `sliding_door`, `slab-door`). These are on the bus, coach, carriage, tram, aircraft, brougham,
   kitchen and wardrobe.
4. **A station where a person sits and works.** A seat, a control (steering wheel, yoke, levers), a dash with a
   `screen`, and the glazed cab around them.

   The cab of a bulldozer, tractor, excavator, forklift, mixer and lorry is one recipe: frame posts, glass, roof, door.
   (2026-11-22: the machines' is the `cab` component now -- excavator, bulldozer, tractor, tower crane.)
5. **Rails, poles and lettering.** Handrails on posts (walkways, tram poles, vestibules, guard rails); a `pole` with
   something clamped on it (signs, signals, lamps, meters, a bus flag); stroked lettering on fascias and plates (STOP,
   BUS STOP, TELEPHONE, station names).
6. **Machinery idioms.** Hydraulic rams on every machine; lattice trusses (crane mast and jib, later pylons and
   bridges); corrugated panels (containers, sheds).
7. **Small appliance idioms.** Bar handles on standoffs, round knobs, key grids, speaker cones, a lofted cabinet with
   lofted doors.

## Reusable parts: the code

These helpers live in `kit.py`, promoted from the modules where they were first written. The generated output stayed
byte-identical.

- **Loft geometry in Python**, the same sums as items.js. Use it to fit things to a lofted surface:
  - `station_at(stations, x)` gives a section at x.
  - `section_half` and `section_poly` give its outline.
  - `loft_eval(stations, round, x, u)` gives a point on the surface.
  - `on_loft(stations, round, x, y|z, off)` returns the `at` that lays a thin part flat on the surface, for
    windscreens, stripes and grilles.
  - `loft_z(stations, round, x, y)` gives the side's z, for handles, seams and lamps.
  - `shell_over(stations, xs, grow)` gives the stations of a loft just outside another, such as a roof over a
    glasshouse.
  - `cr_at`, `euler`.
- **Small assemblies:**
  - `tube(id, mat, [[r, dx]], x0, y, z)` lays a lathe along +x: barrels, exhausts, pipes, nacelles.
  - `ram(id, a, b, r)` is a hydraulic cylinder between two points.
  - `handrail(id, mat, x0, x1, y, z, posts)` is a rail on posts.

- **Windows** (2026-11-22): one family for every row of panes and the posts between them, on a face -- axis "x" (the
  plane x = c, the row along z) or "z" (z = c, the row along x). A row's layout is a list of spans [(a, b)]:
  - `fill(u0, u1, pane, post, n=None)`: panes filling the stretch with a `post` between each two -- n of them, or as
    many about `pane` long as fit (the bus's and coach's sides; the bus shelter's back; a curtain wall's bays, post 0).
  - `spaced(u0, u1, n, w, ends=False)`: n openings `w` wide, each in the middle of one of n equal cells (the
    carriage's eleven windows), or with `ends` their middles from u0 to u1 (the container ship's deckhouse).
  - `window_holes(spans, y0, y1, side)`: the loft's `holes` for them (bus, coach, carriage, tram, airliner).
  - `face_box(id, mat, axis, c, (u0, u1), (y0, y1), t, off)`: one box on the face by its extents.
  - `panes(id, mat, axis, c, spans, rows, t, over=0)`: a box over every span in every row ([(y0, y1)] or one) -- the
    glass, a deckhouse's grid of windows (one `each` grid: 5 decks x 11), the carriage's sills and heads (`over` 1 cm
    wider), a curtain wall's transoms (one span, a row each).
  - `bars(id, mat, axis, c, spans, y0, y1, t, w=None, over=0, gap=None, ends=False)`: the posts between the spans --
    over each gap, `over` wider (the bus's black panels over its window posts; `gap` 0.6: not over a door), or `w`
    wide on the gap's middle (the shelter's posts, the terminal's mullions every 3 m); `ends` adds one beyond each
    end as if the row went on.
  - `window_wall(id, axis, c, t, u0, u1, y0, y1, rows, ncol, frac, mat, glaze, mull)`: a wall with rows of windows
    cut in it (was `infra.win_wall`): the station hall and its kiosk, the bus station, the hangar's workshop.
  Everything laid is folded by `runs`. Ported with every modern item the same, triangle for triangle (geo4, seeds 1-3,
  shut and split, components too) and the renders pixel-identical:

  | item | parts | json |
  |---|---|---|
  | infra/terminal (mullions, transoms) | 51 → 51 | 19.0 → 15.5 KB |
  | rail/carriage (sills and heads: one 11 x 2 grid) | 40 → 40 | 20.9 → 20.0 KB |
  | sea/container-ship (deckhouse windows: 5 x 11 and 5 x 6 grids, the bridge's side) | 102 → 102 | 76.9 → 76.7 KB |
  | street/bus-stop (back posts as a run from the panes' spans; the front posts their own part) | 29 → 30 | 10.2 → 10.1 KB |
  | vehicles/bus (window posts: a folded run on the left; were merged across both sides) | 78 → 79 | 40.2 → 40.1 KB |
  | vehicles/coach (the same) | 67 → 68 | 33.7 → 33.7 KB |
  | infra/station-hall, bus-station, hangar (`window_wall`); air/airliner, rail/tram (`window_holes`) | unchanged bytes | |

  Left as they were: the footbridge's glazing (each bay's pane gated by its own `w{i}` param), the train shed's end
  screen (mullions up to an arch), the phone box (its sides turned by yaw: bars on a turned frame, already runs),
  machines `cab` (a component written in expressions), the car's glasshouse and door panes (pieces of lofts), and the
  single panes laid on a loft with `on_loft` (windscreens, cab windows).

These are still in their own modules and are the next ones to promote:

- **Text:** `street.text3` + `GLYPHS`, a stroke font (A–Y, 0–9) on any plane, for number plates, shop signs, station
  names and dials.
- **Outlines:** `street.rrect` / `ngon`.
- **Hulls:** `sea.hull_half(lines, B, t, y)` gives the hull's half-breadth, to fit cargo and fittings to any hull.
- **Lattice trusses:** `machines.lattice_mast` / `lattice_jib`.
- **Cab:** `machines.cab(...)` is the glazed operator's cab.
- **Rail and bus pieces:** `rail.end_wall` (a plate in a loft's section, with a doorway), `rail.sliding_door`,
  `vehicles.folding_door`, `vehicles.jambs` (the bus's window posts and pane layout are kit's windows now, below).
- **Aircraft:** `air.surface` (wing, stab or fin) and `air.nacelle`.
- **Appliances:** `electronics.knob`, `bar_handle`, `key_rows`, `cone`, `coiled_cord`.
- **Furniture:** `furniture.splayed_legs`, `upholstered`, `table_spots`.
- **Guns:** `arms.rail` (Picatinny), `arms.handgun_hold` / `longgun_hold`.
- **Roads and buildings** (infra.py):
  - `bx` makes a box from its extents.
  - `flat` lays an outline flat in x and z.
  - `arc_xz`, `on_arc`, `arc_path` and `yaw_of` place parts on curved roads and track.
  - `stripes` draws dashed lines.
  - `shed_roof` builds a barrel roof on ribs.
  - `rail_boxes` and `rail_sweeps` draw rail sections.
  - `ballast` builds the track bed.
  - `digit` draws seven-segment numerals.
  - `ring_at` places a ring of fixtures.

### Gotchas found on the way

- Loft stations must ascend in x.
- A material passed to a component as a self-alias ({"tyre": "tyre"}) breaks it to the fallback beige. Roles inherit
  from the parent, so give a component's roles their own names.
- Pass sweep radius lists as `radii=`, not as `r`.
- A `spot` with an empty `at` list puts a marker at the origin.
- kit's `box`/`rod`/`lathe`/`use` take `at` positionally.
- `around` does not swing a part's offset `at` round the axis. It only adds `r`, so give the radius as `r` or place
  each copy explicitly (`infra.ring_at`).

### What the engine lacks (wishes from every group)

- ~~Transparent glass~~: done, `window-glass` (above).
- **More than one paint per loft.** A roof, skirt or band is a second loft or a laid-on slab.
- **A lit screen material**, for TVs and boards.
- **More materials:** brushed steel that tiles on flat faces, sign colours, retroreflective white, glass-ceramic.
- **Rounded fabric boxes** show ragged light patches at their corners.

## Clothes (assets/clothes, the garment system; docs/clothes.md)

Written by `tools/modern/clothesgen.py`, which can be run again safely.

Garments:
- legs: jeans, shorts, suit-trousers
- tops: t-shirt, polo-shirt, dress-shirt, sweater, hoodie
- jackets and coats: suit-jacket, puffer-jacket, trench-coat
- tie, hi-vis-vest, day-dress, a-line-skirt
- shoes: sneakers, work-boots
- hats: baseball-cap, beanie, hard-hat

Components:
- `collar`: a fold-down collar
- `peak`: a cap's bill
- `patch` and `band`: worn sheets for pockets, plackets, reflective tapes, lapels and hoods

Other changes:
- 27 dyes were added to assets/patterns/palettes.json.
- wardrobe.json has a new `modern` style with office, casual and worker kits, plus named outfits: office-worker,
  casual, construction-worker.
- No world period was added: the periods in periods.json set what every seed draws.

Lessons from building these:
1. A garment's own `pieces` lie under its `use` components, so anything that has to show on top must be a component.
2. A body part holds at most six layers, and the innermost are dropped first.
3. A short sleeve's mouth pokes through a long outer sleeve. Because of this, the modern style lets a figure wear only
   one top.
