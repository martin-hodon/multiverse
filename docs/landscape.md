# Landscape

`landscape.js` makes a SMALL SCENE -- a few hundred metres on a side, at 1 m -- with the components a walker remembers:
a cliff, a gorge, a waterfall and its pool, a lake with an island, a cave, scree, boulders, trees. They are not stamped
on noise. Each is where and how the scene's GEOLOGY and CLIMATE put it: a fall is where a stream crosses a hard bed
over a soft one; its height is the two beds'; the gorge below it is how far it has stepped back; a lake on a karst
upland is a doline, on a basalt one a hollow between lava flows, in an alpine climate what the ice scoured; a cave is an
alcove under a sandstone cap, a spring cave in limestone over marl, a lava tube in basalt. Change the geology and the
same plan comes out as different land; change the climate and the stream runs or does not, the lake fills or is a pan,
forest or scrub or slickrock covers it.

    landscape.js        the model: makeLandscape(spec) -> heights, rock, scree, water, surface, trees, caves (meshes);
                        it runs STAGES, the stages below, in order over one shared context
    landscape/          the stages, a module per family of them, and what they share:
      core.js             the arithmetic: noise, fbm, rng, hash, the heap, clamp/smooth/lerp, nearest, cumOf
      presets.js          ROCKS, GEOLOGY, CLIMATES, climateOf, the strata, DEFAULT_FEATURES
      mesh.js             surfaceNets (the caves' and the bridges' meshes)
      colour.js           the ground's colour per cell from its surface (the lab's, and the world's bare ground)
      frame.js            frame, strata               relief.js   relief, plan, meanders, outliers, domes, the lake
      coastal.js          the coast, dunes, mouth, causeway, tombolo
      desert.js           playa, yardangs, barchans, tinajas, the slot, fins, hoodoos
      volcano.js          cone, maar, neck and dike, hot spring, fumaroles
      river.js            the stream's bed, terraces, fans, oxbow, delta, tributary, ravines
      glacial.js          moraine, braids, esker, rock glacier, knock, cirque, solifluction
      karst.js            tufa, sinking streams, dolines, cockpits, pavement
      slopes.js           relax and the gullies, landslide, couloirs, settle (badlands in it)
      caves.js            caves, bridges         water.js   the water       dress.js   surface, stain, ground, trees, boulders, result
    landscape_lab.html  the lab: the scene drawn (three.js WebGPU), the presets, the features, cameras
    landmap.js          the scene as the game's world (below, "In the world")

`landscape_lab.html?geology=karst&climate=alpine&seed=3&view=1` -- views: 0 above, 1 the fall, 2 over the lake, 3 the
scarp, 4 the lake, 5 the lower fall, 6 the side fall (or its ponor), 7 the coast, 8 the cone, 9 the slot, 10 the landslide, 11 the rock glacier, 12 the dome, 13 the delta, 14 the braids, 15 the hot spring, 16 on: each cave and bridge (a preset camera takes
the trees in its line of sight out of the way, until it is moved by hand); `?no=lake,cave` leaves features out;
`?with=coast` makes one that comes by chance; `?trees=0` draws
none (to see the ground); `?hud=0` neither the notes nor the panel (the view alone); `?cam=x,y,z,tx,ty,tz` a camera of
one's own (scene metres, z up).

## How to make land like this: the choice

What was weighed, for land at walking scale that must be both INTERESTING (named components, of varied shapes) and
CONSISTENT (each where the rock and the climate would put it), controlled by parameters:

| approach | what it gives | why not alone |
|---|---|---|
| noise (fbm, ridged, domain warp) | cheap, endless, any scale | no structure: no beds, no drainage, nothing a geologist would name; features are wherever the noise put them |
| full simulation (uplift, stream power, thermal, the terrain lab) | true structure at 20-100 m | slow at 1 m; hard to steer (no "a fall here, 15 m"); no overhangs |
| example-based (patches of real DEMs) | real texture | needs a corpus; consistency between patches is the hard part; no caves |
| feature stamping (place a lake, a cliff ...) | full control | the components do not agree with one another or the ground |
| **construction from geology, then relaxation (chosen)** | the components PLANNED from the beds and the climate, cut as profiles along curves, then the ground let settle by its rock's own rules | |

The chosen way is a pipeline of stages, each a small model a geologist would recognise, and each reading only what the
stages before it made. The PLAN says what is to be there (a fall, a gorge so long, a lake of this cause); the
RELAXATION makes it look made by weather, not drawn: every column of rock as steep as its bed stands and no steeper,
what falls lying as scree. The water is worked out, not drawn: lakes fill to their spill, the streams go where the
ground takes them. Overhangs are volume patches (below), the one thing a height field cannot hold.

## The stages

    GEOLOGY   the stack: beds from the top down (rock, thickness -- the preset's give or take `vary`, 30%: each place its
              own, so the fall's height is too), dipping and warped; per rock how steep it stands,
              how hard it is, how far apart its joints are, whether it dissolves (karst) or cracks in columns
    CLIMATE   rain and warmth -> does the stream run all year, does a lake stay, frost, soil depth, what grows
    RELIEF    the scarp where the hard cap ends, wandering across the scene; the upland on the cap, the lowland on the
              bench below; the upland falling to the stream from both sides (so the lip is the lake's one outlet);
              a stack with no soft bed under its hard one (granite) steps down at a fault instead, its upland ROLLING
              (swells and basins ~100 m across, ±2.4 m: it rotted deep and unevenly); where under the
              bench there is another soft bed and another hard one, a STAIRCASE: the bench ends in a scarp of its
              own (~0.27 of the scene further on) and the land steps down again; a COAST (by chance, where the
              lowland has room: 24 m at least past the last scarp): the shore across the lowland, partly following
              the scarp (the same rock), bays and headlands. Where the lowland stands on a hard bed, mostly CLIFFED:
              the land cut off 6-15 m over the sea, the waves' PLATFORM at the foot (planed at their level: rising
              a little to the cliff's foot, its knobs out of the water; TIDE POOLS in it where it stands out, up to 40,
              2-4 m across, full of the sea's water: `coast.tidePools`, their count), the sea's floor falling away beyond; STACKS on the platform, pieces of the cliff's
              land left standing (some, never the first, cut down to a STUMP awash at the tide's height); in GRANITE
              the cliff a WHALEBACK (`coast.rounded`): steep at the water, rolling over to the land 1.5 times its
              height back, the stacks domes, the black lichen's band over the water instead of streaks; in LIMESTONE a CALANQUE
              (`coast.calanque`: { x, y, hx, hy, L, w }; most times): a valley the karst's floods cut when the sea stood
              lower, drowned -- a narrow inlet 38-72 m back into the cliffs, 12-20 m wide at its mouth, winding, its
              walls sheer, its floor 5 m under the sea at the mouth shallowing to a pocket beach at its head, the dry
              valley climbing on behind it to the land; a COVE where the stream comes out, a pocket beach in it, and the stream falls to it
              (the waves cut the cliff back faster than the stream cut down; the meanders straighten toward it).
              Else a BEACH: sand from a little over the sea's level sloping into it, CUSPS along its waterline (horns
              out to sea, round bays between, every 12-24 m: the swash sorts the sand at its reach; `coast.cusps`). What falls into the sea the
              waves carry off (the walls stay steep). Its own random numbers: a scene without one is unchanged
    CONE      on basalt country (by chance, 0.7) a CINDER CONE, the youngest eruption's: on the upland or the lowland,
              clear of the stream, the lake, the outliers and the sea; ~0.36 of its base's radius high, its flanks at
              the cinders' angle (~31 deg), loose, GULLIED by the rain (0.3-1.4 m, the wetter the deeper); a crater 0.4
              of it across, BREACHED where a LAVA FLOW came out -- a horseshoe, the crater's floor carried out through
              the rim and down the flank -- the flow a tongue down the land from the breach (to the sea or the edge;
              from the upland over the scarp's edge in a CASCADE, the lava draped down the face at ~48 deg, its middle
              thickest, and on over the land below, unless the gorge is near: `cone.cascade` { x, y }; near the
              stream's valley it turns down along it), widening, lobed, 2.5-4.5 m thick, its fronts steep, LEVEES on its upper 60% (the channel
              the lava ran on in drained to a trough ~1 m deep between two banks ~1 m high), PRESSURE RIDGES across it (arcs bowed
              downstream every 5-8 m, higher toward the front), 2-5 HORNITOS on its channel (spatter cones 4-7 m across,
              1.8-4 m high, a throat down each; welded, so rock; not on the cascade; `cone.hornitos`: each { x, y, r, h }); FUMAROLES (70%, not a maar's): 3-7 vents in
              the crater and on its rim away from the breach, SULFUR crusted round each and the ALTERED ground bleached
              round that, warm (no snow), bare; the lab puffs their steam (`cone.fumaroles`: each { x, y, z, r });
              bare CINDERS and LAVA where it is dry (grass on them where it is wet); its
              crater holds a lake where the climate keeps one. Where it is wet (rain over 1000 mm; by chance, 0.6) a
              MAAR instead: the magma met the ground's water and blew out a crater ~0.55 of the site across, 9-14 m
              down into the beds (its walls the country rock), a low ring of loose tuff round it (2.5-4.5 m), no lava;
              its lake at the water table, 2-5 m under the land (the WATER stage lets it out there)
    DOME      on granite where it is warm (15 C and more) a DOME on the land below the fault -- a bornhardt: where the
              joints were few the rock held while the rest rotted deep and washed away; its sides steepening to its
              foot, longer one way, the sheets it splits off peeling round it; its top under the till's base (so all
              granite: 9-30 m high, 1.2-1.7 times as wide as high); its corestones round its foot (boulders); its flanks
              STREAKED down from where they steepen past 12 deg (DRESS: the runnels' varnish or algae, by the way round it)
    OUTLIERS  where the cap held as the scarp stepped back, a piece of the upland left standing in front of it: a
              butte, pinnacles (a tower, pillars in karst); settling makes the cliffed cap and its skirt of scree
    PLAN      the stream: in at the upland's edge, out at the lowland's; the fall was where it met the scarp and has
              stepped back up it by the ravine's length (the gorge); the plunge pool; the lake above the lip (its level
              the lip's, its hollow's cause the climate's or the rock's), its islands knobs of harder cap; on a
              staircase a second fall where the stream crosses the second scarp, its gorge shorter (0.3 of the first's:
              it is younger -- the first had to step back past it before it began); the meanders begin below the last step;
              a TRIBUTARY: a side stream from the scene's edge across the upland (leaning upstream: side streams join
              pointing down the main one; away from the lake and the outliers) to the gorge's rim, a little below the fall
              -- on karst where the stream runs all year (by chance, 0.75) a SINKING STREAM instead: it goes down a
              PONOR half to two thirds of the way, its valley ending BLIND against a wall (its floor sunk 2-4 m toward
              the hole, the funnel 10-15 m across), on underground and out at the spring cave (`tributary.ponor`)
    CARVE     the stream's bed as a profile along its curve (falling all the way: a gorge floor never ponds), the gorge,
              the pool (each step's); the side stream's valley -- shallow: it HANGS over the gorge, which all the
              stream's water cut down, the side valley only its own; ALLUVIAL FANS where each gorge opens onto the land
              below: a lobed cone of gravel, its apex at the mouth (big in a dry climate, where a flood drops what it
              carried and no stream takes it on; low in a wet one), the stream in a trench cut into its head, the gravel
              loose (it settles as scree); where it is cold a MORAINE: a horseshoe of till round the lake's lower end
              (where the ice's snout stood; its sides the lateral moraines), hummocky, loose, the stream through a notch
              in it and the gorge's head cut through it -- and erratics on the upland (boulders of the hardest bed); beyond
              it on the outwash 2-5 KETTLES, round hollows 6-12 m across where buried ice melted out, the water in
              them (a lake however small: `kettles`, each { x, y, r, d }); and an ESKER: the gravel that filled the
              tunnel the meltwater ran in under the ice -- a ridge 3-6 m high, narrow, round-crested, steep-sided,
              winding 45-170 m down the way the ice went to the snout, out beyond the lake's moraine; beaded, its end
              let down; loose, its steep sides bare gravel, no boulders; should it swing out over the hollow, a spit
              into the lake (`esker`: { pts, h, W, len, spit } or null);
              behind a beach DUNES: ridges along the shore of the sand the wind took from it (2-4, up to 1.6-4.8 m:
              higher and more the drier the country), broken by blowouts, loose; bare sand where it is dry, the grass
              on those behind the first where it is wet -- on a cold coast none: a STORM RIDGE of shingle instead (one,
              1.1-1.9 m, along the top of the beach, steep to the sea; low where the stream comes out); at a beach the stream's MOUTH: the bar built across it, a
              LAGOON behind (shallow, dished, its shore eased into the land, along the shore the way the waves drive
              the sand), its outlet through the bar from the lagoon's far end, slanting on with the drift -- its bed a
              little over the sea's, which holds the lagoon up; where the stream stops in the dry season the bar shut;
              in the wet tropics MANGROVES round it (its shallows and rim, 0.8 m under the sea to 0.7 m over; in
              patches): mud, and low broad trees standing in the water (a tree's `mangrove`);
              and the stream's channel not cut on across the sea's floor; the lake's bowl, its outline what made it
              (the ice's long up the way it came, fingered; a doline's round; lobed between two flows' fronts; squared
              by granite's joints; the lower end where it spills the same in all), and islands (an ice-scoured lake:
              many, low, streamlined -- smooth up-ice, steep down-ice; else their form the rock's: basalt's and
              sandstone's tables, flat-topped and cliffed all round; limestone's towers, sheer, fluted, domed, taller where
              it is warm (but never over 1.4 times as tall as wide); granite's domes -- solid rock, not heaped; now and then a smaller one off the first,
              `lake.isleForm`); where the climate cannot keep it and no stream runs all year, a PLAYA: its floor dead
              flat (the bowl filled half up with what the storms washed in), crusted white with salt and cracked in
              polygons ~6 m across, a skin of brine only where it dips; 2-3 old shorelines as benches on its sides,
              from when it stood higher; the islands rise from it; YARDANGS on it, the old lake's mud the wind has
              not yet taken: ridges 9-14 m long, 1-2 m high, in staggered rows along the wind (its way the scene's
              own), blunt and steep to it, tapering away, on the floor and the low benches, in patches (bare mud;
              `yardangs`: each { x, y, a, L, w, h }); a DELTA where the stream comes into the lake
              (what it carried, dropped where it slows: built out into the water, its top a little over it; the stream
              split across it into arms, each wandering out from the apex and some forking on the way (where a bar grew
              in a mouth), the land their levees -- highest by the channel, narrowing out to each mouth, a bird's foot
              -- its front the sediment's slope down to the bed; the
              bigger the more the stream brings -- the ice's meltwater most, its gravel bare; a wet country's grassed,
              a dry one's sand; loose); on the lowland MEANDERS (loops ~11 channel widths apart), deeper under the cut
              bank, a POINT BAR of sand inside each bend, an OXBOW lake beyond one; RIVER TERRACES (by chance, 0.75,
              where it runs all year and the lowland is 80 m long): the stream 2.4-5 m down in its old floodplain (the
              land rose; less toward the sea, where it is at its level), the floodplain it wanders on now a riser down
              from the land it has not cut into, a bench of gravel midway where it went down 3.4 m or more (on one side
              only, by chance: the stream swung into the other); where the cutting starts a short trench, the step
              working up the stream (`plan.terraces`: { u0, u1, depth, levels }) -- where it is cold BRAIDS instead
              (the meltwater brings more gravel than it carries on: a belt of bare bars 18-28 m wide, the stream
              across it in 3-5 threads that part and join, given water after the WATER stage, whose routing finds one
              way only); TUFA DAMS on a karst stream that runs all year
              where it is not cold (5 deg at least): a flight of pools, each held by a sill of the lime the water drops
              where it tumbles -- on the bench between the steps if there is room, and below the last step till the
              stream slackens into its meanders; the dams closer the warmer the water; each pool laid along the stream
              (it follows a bend), its sill lowest in the middle where it spills; DOLINES on a karst upland, each
              draining at its foot -- in the wet tropics the biggest a CENOTE: a shaft down to the water table (9-14 m
              under the upland), sheer, its pool held at the water table (its outlet there, not at its foot); there
              (18 C and more, rain 1500 mm and more) COCKPIT KARST: the dolines grown into each other -- the upland a
              jittered, turned grid of round-topped cones (24-32 m apart, 3-10 m over the land), the hollows between
              lowered 5-7.5 m, star-shaped where the cones' feet meet, a sink at every low in them; the upland as it
              was by the stream's valley, the lake, the scarp's edge, the side stream and the cenote; DRESS lets the
              jungle hold on the cones' flanks up to 50 deg, the limestone out in patches on the steepest
    SLIDE     where it is wet (rain 700 mm and more) and a soft bed lies under the cap (by chance, 0.75): a LANDSLIDE --
              a horseshoe SCAR bitten 22-32 m into the upland (its headwall the beds bare), the slumped mass in it
              lower, tilted back (a ridge where the block rotated, a sag behind it), and a hummocky LOBE of the debris
              30-55 m out over the land below -- a lens thinning to its edges, ridged across, its toe steep; clear of
              the stream and its gorge. The slip surface is the rock; what slid on it is loose. Where it is cold
              enough for the ground to stay frozen (under 3 C; by chance, 0.8) a ROCK GLACIER: the talus under the
              cliff, ice in its pores, crept out over the land below -- a tongue 50-90 m long, 14-24 m wide, 5-9 m
              thick, flat-topped, its margins and front steep, ridged in arcs bowed downhill; bare blocks (scree, and
              boulders thick on it), loose; where it is cold (under 4 C) COULOIRS: chutes the frost wedged back
              into the cliff along its joints (every 15-45 m along the scarp, clear of the gorge, the slide, the rock
              glacier, the outliers, the fans, the cone and the sea), 12-22 m back, 5-9 m wide at their heads and
              narrowing to the mouth, V-shaped across; under each a CONE of scree laid on the slope after SETTLE,
              2.5-5 m thick along its middle, widening down it (`couloirs`: each { u, v, x, y, L, T, r }) -- and
              (by chance, 0.8) a CIRQUE: an armchair bowl 36-64 m across bitten into the cliff's edge, clear of the
              stream, the lake and the rest: its floor cut half way down the face, nearly flat, overdeepened behind a
              lip of sound rock 1.3-2.5 m over it, the headwall steepening up to the rim, its outline bitten where the
              joints let go; a TARN in it (if the climate keeps lakes), spilling over the lip; erratics on the lip
              (`cirque`: { x, y, u, v, r, floor, lip, depth, wall }); the couloirs keep clear of it; where it is wet
              (450 mm and more) and not frozen (4 C and over) RAVINES instead: every 20-60 m along the scarp, clear
              of the same and the side stream, cut 18-48 m back into the cap by the water off the upland -- V-shaped,
              winding, their floors steep at the head and graded toward the mouth, two in five forked at the head;
              half as many on karst (its valleys dry); a CONE of what each cut at its foot, flatter and wider than a
              couloir's, 1-2.4 m thick (`ravines`: each { u, v, x, y, L, T, r, fork }); in a desert (dry, no stream
              all year; by chance, 0.75) BARCHANS on the lowland, clear of the stream, the fans, the playa and the
              rest: 2-5 crescent dunes, 4-9 if there is sandstone to feed them, 18-48 m from horn to horn, 2-7 m high
              -- a gentle back to the wind (the yardangs': the region's), the brink bowed on ahead to the horns, the
              lee left to SETTLE, which slumps it to the sand's angle: the slip face; bare sand (`barchans`: each
              { x, y, W, h }); on granite
              where it is cold (under 4 C) KNOCK AND LOCHAN: the land below
              the step a scatter of up to 32 bare knolls, each a roche moutonnee (long and smooth up the valley, the
              ice's way in, blunt and rough down it where blocks were plucked out), solid rock, 1.5-5 m; the hollows
              between lowered up to 1.8 m where the rotten rock went, small lakes in them; a third with an erratic;
              in basalt country a NECK (`neck`: { x, y, r, h, up } or null; by chance, 0.7 -- 0.3 by a young cone,
              away from it and its flow: a field's vents of all ages): the magma that set in an old volcano's pipe,
              standing where the cone has worn away -- a tower 16-30 m across, 16-30 m high, on the upland or the
              land below, its outline irregular, sheer (its rock the dike's: SETTLE lets it stand as columns), its
              top ragged and highest off-centre, a loose skirt of fallen columns round its foot;
              (by chance, 0.75) a DIKE: a wall of basalt 90-170 m long, 1.6-3 m thick, 3-6.5 m high
              (higher the drier: the rock round it worn away faster than anything grows on it), out from the cone's
              vent (or the neck) if one reaches the land below, else a crack of its own; broken where it was jointed closest, low
              at its ends, cut through where the stream crosses; SETTLE lets it stand as basalt (its joints' factor
              raised), DRESS shows it as the cap's basalt -- whatever bed it rises through; where basalt meets a
              coast, a CAUSEWAY: the waves took the flow column by column, each broken off at its own cross joint --
              a headland 24-42 m wide of hexagonal tops 4.6-5.4 m across, from 9-14 m inland to 14-24 m out, stepping
              down into the sea in 0.55 m steps (the inland ones 3-6.5 m up), standing like the dike, bare rock;
              off a beach (by chance, 0.65) a TOMBOLO: an island 14-26 m across, 4-9 m high, 35-60 m out (steep round
              its foot, rounded on top, solid), tied to the beach by a bar of sand the waves dropped in its lee --
              bending out to it, widest at its ends, narrowest and lowest (awash at a storm) in its middle
    SETTLE    140 sweeps: no rock column higher above its lowest neighbour than its bed's angle allows (near a joint
              less: buttresses and notches); what is steeper breaks off as scree; scree runs down while steeper than
              34 deg; the stream carries away what lands in it. In a dry country, BADLANDS before the last 12 sweeps:
              rounds of the runoff's erosion (as much as the water gathered down the steepest way and the slope can
              take) where the bed under gives -- scree first, then the soft bed -- so rills join into gullies branching
              up the slope; their walls then settle steeper than the slope at large (a dry soft bed crusts)
    TINAJAS   on a sandstone upland in a dry country (dryness over 0.25): potholes the standing rain ate into the bare
              rock -- up to 4 groups of 3-8 strung along a shallow way, 2-6 m across, 0.85-1.55 m deep, flat-floored;
              the rock round each bare (`tinajas`, each { x, y, r, rim, depth, wet }); the wet ones hold the last
              rain's water (most where it is mediterranean, a third where it is arid), filled after WATER; on GRANITE
              (3 C and over, any rain) GNAMMAS, the same water's work on the feldspar: shallow round pans 1.6-5 m
              across, 0.4-0.7 m deep, in a group of 2-5 on bare rock -- a dome's crown, else on a RUWARE or two:
              a low whaleback of the sound granite just out of the till, 18-32 m across, 0.7-1.8 m high, bare
              (`ruwares`, each { x, y, r, h }; the pans in `tinajas`)
    SLOT      in sandstone country not too wet (rain under 900 mm), a SLOT CANYON: a wash on the upland that found a
              joint and cut down it through the cap faster than its walls could fall back -- 1-3 m wide, widening on
              down, winding, as deep as the cap (to 0.92 of it), its floor never steeper than 0.3; it ends where the
              ground falls away under it, hung over the scarp's face in a pour-off; up to 3 CHOCKSTONES jammed between
              its walls where it is narrowest (1-2.6 m), 1.8 m and more over its floor (boulders, `chock`). Cut after
              SETTLE: its walls sheer
    FINS      in sandstone country that is dry (rain under 700 mm) a set of the cap's joints run out to the scarp,
              widened by the rain into corridors (4-6, 7-10 m apart, 2.5-3.5 m wide, down through the cap over their
              first 10 m, then falling to the brink as the slot does): the rock between left standing in FINS, and
              through a middle one an ARCH (a cave patch)
    HOT SPRING by a young cone (the ground still warm under it): TRAVERTINE down a slope near it, or on the flat
              a mound of its own -- terraces 2.2-3.2 m apart, each a pool held by a curved rim, a step down from the
              last (0.35 m at least); its pools filled after WATER, each to its own rim. Cut after SETTLE: rock
    CAVES     volume patches (below)
    PAVEMENT  bare, near-flat limestone grooved along its joints (grikes between the clints), in patches where the
              soil was stripped, deeper in some; its joints at the surface (`grikeAt`, which the slickrock's joints
              use too) broken -- each runs a few blocks and stops, the next along offset -- not sandstone's long cracks
    SOLIFLUC- where it is cold and wet (under 3 C, rain 400 mm and more): the summer's thawed top creeping over the
    TION      ice below, in LOBES on the soil-covered slopes (5-24 deg, off the streams, the lake, the coast): 6-16 m
              wide, 6-15 m long, a riser 0.6-1.4 m high at the bowed front, the soil showing in it, the tread easing
              back into the slope; 10-24 by the wet (`lobes`, each { x, y, w, l, h })
    WATER     priority flood from the outlets (the lowland's edge, the upland's where it stands over the lip): the
              water surface; discharge down it, the inflow from beyond the scene added at the entry, a spring at a
              spring cave; the sea's edge outlets at its level (the sea: kind 4, whatever the climate); lakes (60 m2 and 0.5 m deep at least; a lake a stream runs through stays full whatever the
              climate), streams, falls; each fall's CURTAIN: from the lip (where it first drops 3 m in 4), thrown, sliding
              down the rock where the rock leans out further than it is thrown, landed where the rock is gentler than
              45 deg for 3 m or in its pool; the main fall's form its rock's (plan.fallForm): over basalt's columns 2-3
              strands between the blocks of the lip ("fall strand" curtains), over a sandstone cap where water runs
              all year a broad sheet, in a dry country a ribbon, else one plunge; the side stream's water from beyond the scene added where it comes in;
              a spring's stream: its way found, smoothed (water on a flat goes cell by cell, in steps), its channel cut,
              and the water routed again
    DRESS     surface (bare rock where steep -- the bed it shows -- scree, soil, grass, forest, sand, snow; slickrock
              where little soil lets a hard bed through -- on the rises, the sand in the hollows and down its joints; GRAVEL on a dry country's fans; TUFA on the dams' sills; SAND on a beach
              and under the sea (`coast.beach`: shingle on a cold coast, black sand under basalt, white sand on a warm
              limestone coast -- the dunes the same), bare rock on the platform; MUD on a lake's bed -- and REEDS in its shallows under .7 m where it is wet and neither
              frozen nor hot (4-26 C), in beds along the shore, the lab tinting the water green there; a SPRING LINE in a dry country under a cap that lets the rain through
              (sandstone, limestone, basalt): green seeps along its foot on the bed that will not, at the joints --
              and in a hot desert (15 C and over) an OASIS: the strongest seep's water followed down to where the
              ground eases, a pool 7-13 m across dug there, full to its rim, date palms in a ring round it (`oasis`:
              { x, y, r, level } or null);
              STREAKS down the cliffs (`stain`, `stainCol`): in a dry country desert varnish, black-brown, darkest on
              sandstone; else the algae's grey-green, on limestone and granite most, the more the wetter -- in stripes
              along the face, strongest under a notch where the runs gather; a PLAYA's floor SALT, the cracks mud;
              BOGS where it is cool and wet (rain over 900 mm, 14 C and under): peat in the flat hollows the water
              gathers in and cannot leave -- not on limestone, which it sinks into -- in patches, no trees, pools in
              the moss;
              PATTERNED GROUND on a cold country's flats, in patches:
              polygons ~6 m across, gravel rims the frost sorted out round their middles), tree cover (the climate's, in
              stands, by the water where the land gathers it: the wetness index; in a dry country a RIPARIAN strip, the
              plants crowding the stream and the washes 4 m either side, the desert's wash floored with the last
              flood's sand), trees (each { x, y, z, h, r, conifer, palm, mangrove?, shape? }: in a warm dry country
              their own forms, `shape` -- a hot desert's acacias "umbrella", flat-topped on a bare stem; in a warm
              scrub among the low oaks the cypress "columnar" (15%) and the stone pine "umbrella" (20%); in a jungle the
              emergents, 7%, "umbrella" 28-38 m, standing clear over the canopy; in a reed bed tufts of "reed" 1.3-2.8 m
              standing out of the water, `z` its level), boulders at
              the walls' feet; SNOW where it is cold, on the
              slopes turned from the sun (`sun`, which the lab lights from), in the hollows the wind drifted it into
              (the rises swept bare), more of it up on the upland; TORS on a granite upland; a FELSENMEER on a cold
              upland with a hard cap (fields of angular blocks the frost split where they lie, in patches on the
              flats, stones between); CORESTONES down a granite stream's bed and banks from the plunge pool
              on (one every 1-3.4 m, biggest in the gorge, smaller downstream); HOODOOS in
              a dry country (rain under 700 mm) where a soft bed lies bare under a hard one (shale under sandstone, tuff
              under basalt, marl under limestone): clusters of columns on the slope below the scarp (14-44 deg) where
              the slope is the soft bed for 3-14 m, each as tall as the hard bed's base above it, waisted, the most
              still capped with a slab of the hard bed, the rest worn to a point; nothing grows on them

Each component's numbers come from the beds: the fall's height is the cap and the soft bed under it (or a fault's step
where there is no soft bed: granite); the pool's size the fall's; the gorge's walls the beds' angles; an alcove's
height where the contact is.

## Caves: volume patches

A cave is a box sampled every 0.5 m: solid where under the ground AND outside the cave's shape -- capsules (flattened:
`r` across, `rz` up), their walls roughened, on a floor of what has settled in it. Surface nets mesh the box (a vertex
in every cell the surface crosses, a quad across every crossed edge; no tables); the ground's cells under the box are
left out (`cut`) and the patch, which reproduces the ground at its edges, is drawn instead. Its vertices carry their bed
and how deep in the dark they are.

| geology | cave | where |
|---|---|---|
| a soft bed under a hard cap (canyon) | ALCOVE: the soft bed weathered back, the cap overhanging | the contact, on the scarp |
| limestone over marl (karst) | SPRING CAVE: a passage along the bedding, turning at joints, a chamber; a stream out of its mouth | the contact (the water can sink no further) |
| basalt (volcanic) | LAVA TUBE, a skylight where the roof fell in | inside the cap |
| any, behind a fall that runs all year | GROTTO behind the curtain | the pool's level |
| granite (no soft bed) | ROCK SHELTER: a sheet joint parallel to the face let the slab under it spall away -- low, wide, the rock above overhanging | the fault scarp's foot |
| a hard cap over the gorge (not a fault) | NATURAL BRIDGE: a span of the cap the stream went under (a meander's neck in sandstone, a cave's roof in karst, a lava tube's in basalt), its deck the cap's top, its underside an arch | across the gorge |
| karst in the wet tropics | CENOTE: the cave the doline's shaft fell into, wider than the shaft -- the rim overhangs the pool | the water table |
| any, on a cliffed coast | SEA CAVE: the waves worked in along a joint at the cliff's foot; by chance (0.6) a BLOWHOLE at its end, a shaft up to the top where the squeezed air opened a joint (`coast.blowhole`: { x, y, r, z }) | the sea's level, aside from the cove |
| sandstone, dry (rain under 700 mm), its FINS | ARCH: a window weathered through a middle fin where the corridors beside it are deep -- from a little over their floors, its span ~1 m thick | over the corridors' floors |
| limestone at a cliffed coast's foot | NOTCH: a groove along the foot 30-60 m long, 1.5-2.3 m deep, ~1.5-2.3 m high, the cliff overhanging it -- the sea dissolves the limestone at its level | the sea's level, clear of the cove and the sea cave |
| any, on a cliffed coast with a stack over 4 m across | SEA ARCH: through the biggest stack, out to sea -- two caves from either side met | the sea's level |

A bridge is the same kind of patch with a different solid: the ground OR a slab (ragged, its underside an elliptic
arch over the gorge). Where a patch is the ground (at its height, open above) it takes the ground's colour, so its edge
does not show. Under a sea cave's and an arch's opening the ground's cells are let down to its floor (`flood`), so the
sea comes in under the roof.

## What it returns

`makeLandscape({ seed, size = 320, dx = 1, geology, climate, relief, features, flow })` -> `{ N, dx, size, H, rock, soil,
W, Q, water, kind (0 dry, 1 lake, 2 stream, 3 fall, 4 sea), flow, surf, SURF, stain (0..1 per cell), stainCol, bed, slope, veg, trees, boulders, couloirs, ravines, yardangs, barchans, caves (each
{ kind, parts, floor, mouth, out, why, pos, idx, bed, shade, box }), cut, falls, fans, dams (each { x, y, s, crest }), mouth ({ x, y, open, sg } or null), delta ({ x, y, u, v, r, arms, out } or null), braid ({ w, threads, u0, u1 } or null), hotSpring ({ x, y, dir, L, W, pools } or null), coast ({ sea, cliffed, cH, vS, uL, coveR, line(v),
stacks (each { x, y, r, stump }), beach (a SURF name), causeway ({ x, y, w, out } or absent), tombolo ({ x, y, r, h, out } or absent), blowhole ({ x, y, r, z } or absent), tidePools (a count, or absent), cusps (their spacing, or absent) } or null), cone ({ x, y, Rb, hc, up, a0, flowL, hornitos, cascade, fumaroles, maar -- a maar's also Rc, floor, wt } or null), dike ({ x0, y0, x1, y1, w, h, radial } or null), hoodoos (each { x, y, z, h, r, cap ({ r, h } or null), bed, capBed }), slot ({ pts (each { x, y, z, w }), depth } or null), fins (each corridor's points { x, y, z, w }), slide ({ x, y, u, v, Wl, Ds, Lb, toe, out } or null), rockGlacier ({ x, y, u, v, W, L, T, root, out } or null), cirque ({ x, y, u, v, r, floor, lip, depth, wall } or null), oasis ({ x, y, r, level } or null), domes (each { x, y, u, v, r, h }), strata, climate, geology, plan
(stream, fallU, cross, lipZ, fallH, profile, curtain, curtains -- one per fall, and a segmented fall's strands --, fallForm, step2, cross2, fall2U, toXY, toUV,
streamV, tributary), lake (a playa's also playa: { floor, lines }), tinajas, ruwares, lobes, kettles, esker, neck, notes, stages, ms }`. `notes` says in
words what was made and why (the lab shows them).

`geology` and `climate` take a preset's name (GEOLOGY: canyon, karst, volcanic, granite; CLIMATES: temperate, arid,
alpine, tropical, mediterranean) or an object of the same shape; `relief` scales the beds' thicknesses; `features` is
DEFAULT_FEATURES with any of them false or changed (`ravine.length` as a fraction of the scene, `lake.r`,
`lake.islands`, `outliers.count`, `bridge.chance`, `meanders.amp`; `steps`, `tributary`, `fans`, `badlands`, `tufa`, `moraine`, `kettles`, `esker` (or `esker.chance`), `dunes`, `calanque` (or `calanque.chance`), `mouth`, `delta`, `braids`, `springs`, `hotspring`, `maar`, `slot`, `fins`, `landslide` (or `landslide.chance`), `rockGlacier` (or `rockGlacier.chance`), `dome`, `cone` (or `cone.chance`), `neck` (or `neck.chance`; true makes one), `playa`, `tinajas`, `gnammas`, `solifluction`, `bogs`, `mangroves`, `chockstones`, `felsenmeer`, `terraces`, `couloirs`, `ravines`, `cirque` (or `cirque.chance`), `yardangs`, `barchans` (or `barchans.chance`), `blowhole`, `cascade`, `hornitos`, `fumaroles` (or `fumaroles.chance`), `notch`, `cusps`, `tidePools`, `riparian`, `oasis`, `reeds`, `ponor` (or `ponor.chance`), `dolines`, `cockpits`, `knolls`, `corestones`, `dike` (or `dike.chance`), `causeway`, `tombolo` (or `tombolo.chance`), `tors`, `hoodoos` on or off; `coast.chance`, or `coast: true` to make one).

Three options steer the plan from outside, for the world (landmap.js): `streamV` where the stream crosses the scene
(m off its middle; by default drawn), `wander` how far it wanders about that (1 the scene's own), `scarpAt` where the
scarp crosses the stream (m along it from the middle; by default a little downstream). Left out, the scene is what it
always was: each stage takes its draws from the one random sequence in the same order, so a seed's scene is the same
one since the stages were split into modules (checked by fingerprinting 80 scenes before and after: none differ).

A 320 m scene takes about 2.5-3 s on the CPU (settle the most: 140 sweeps). The whole of it in one function was too
big for V8 to optimise -- run in it unoptimised the sweeps took 19 s instead of 0.9 -- so the sweeps are a function of
their own (`relax`), and every stage is a function of its own (`landscape/`): each takes what it reads from the shared
context and puts back what it makes (`Object.assign(c, {...})`).

## In the world

`landmap.js` `landscapeMap({ seed, radius, riverZ, res, meadow, facade, geology, climate })` makes the game's land from a
scene, in the shape mapgen.js's grown river country comes in (ground.js and the town read it the same), with
`kind: "landscape"`, `geology`, `climate`, `variant`, `scale`, `relief`, `earthwork`, `fall`, `lake` and `surface`
added. The startup menu offers it after the age and the culture ("Choose the land": a rock, then a climate, or the river
country as before); `?geology=canyon&climate=alpine` asks for it directly (`any` for either: drawn from the seed).

- GROW: the scene with its stream off the middle in the proportion the world wants room either side of the river
  (`streamV`), wandering half as much (`wander: .5`), loops not so deep the river turns back (`meanders.amp .55`), a
  lake the world's size (`lake.r .085`), no coast; and the scarp where the town is not: far downstream (UPLAND: the
  town by the lake above the fall) or far upstream (LOWLAND: the town below it). A seed tries its own variant first and
  keeps whichever moves the land least.
- SCALE: across by what fits the world into the stream's room (~2.9-3.2x: a 15 m fall a 30 m one), up by less (`hs^.6`,
  ~2x). The scene's own stream is the world's river: its cells, west to east, are the course mapgen follows.
- SHAPE (mapgen.js `shapeMap`): the window along the river, judged by mapgen's gentle banks and also by the EARTHWORK
  -- how far the town south of the bridge, its farms north, the herd's meadow and the monument's stretch of the facade
  line lie off the town's height, and a lake over any of them no place at all. The scene's cells bicubic onto the
  world's 2 m grid with a little noise between (`detail .45`), then settled: the places built on eased to 0.
- THE TOWN on it (index.html, town.js `fits`): a house, farm or plot stands only where every 3 m of its footprint is
  dry and within 2 m of level (FLOOR_DELTA); where it is not, it is left out -- more houses where there is room.
- THE GROUND'S COLOUR: `surface` -- the scene's surface on the world's grid, its colour (landscape/colour.js, as the
  lab draws it) and how bare (rock, scree, sand, snow 1; soil under plants .3; grass, forest 0; none where the land was settled to build on,
  fading back over 30 m). terrain_data.js lays
  that colour over the lawn's as bare as it is; grass.js GROUND_BARE keeps the lawn's blades and the grass fringe off it.

## Review log

What each round of looking at the scenes found, and what was done:

- the stream left at the first edge it met -> only the lowland's edge is an outlet, and the upland's where it stands
  over the lip; the upland falls to the stream from both sides so the lip is the lake's outlet
- a lake cut by the scene's edge -> its radius shrinks until it fits with its shore
- the gorge floor ponded -> the stream's bed profile falls all the way (a running minimum)
- cliffs smooth as poured -> joints: two sets per bed (three at 60 deg, close, in basalt); a wall stands less steep near
  one, so it fails along them, leaving notches and the buttresses between
- the fall only a colour on the cells -> the curtain: thrown from the lip (found where the walls settled back to),
  sliding down the rock where it leans out; foam where it lands; no water sheet hung between two levels
- forest in blocky cells -> tree cover as a field (climate, stands, soil, slope, the wetness index over a few metres),
  blurred; trees instanced (conifers where cold); the floor darkened by the cover
- a stream's water spread down every slope -> the banks spread from what was water before each pass only
- a mediterranean lake called dry while its stream ran all year -> a lake a stream runs through all year stays full
- granite: no soft bed, a 0.7 m fall -> the fault step
- dry climates all sand -> slickrock where little soil lets a hard bed through
- outliers planned at their final size eroded to cones -> planned bigger: a butte loses some 8 m all round
- the lowland dull -> meanders, point bars, an oxbow; a point bar's edge left a step in the bank -> blended into it
- a bridge's deck flat below the rim, its patch coloured as rock on the grass -> the deck is the cap's top; a patch is
  coloured as the ground where it is the ground
- the spring's stream a staircase across the lowland -> its way smoothed and cut, the water routed again
- the lowland one flat bench whatever the stack -> the staircase: each hard bed over a soft one a step, the second with its
  own fall, gorge and pool; the lab's camera for it looked into the bent gorge's wall -> it stands on the stream
- a sheet of the stream's cells sloping down under a curtain, the curtain poking through it -> under a curtain, above its
  pool, no water sheet is drawn
- one stream: a side valley joining the gorge -> the tributary and its hanging fall; the bridge kept from where it comes in
- a curtain started at a step in the channel above the lip (granite: it ran 6 s along the flat) -> the lip is where the
  water first drops 3 m in 4; a curtain sliding down the rock only as fast as it was thrown (it never got down) -> on the
  rock it goes as fast across as the rock lets it, and lands where the rock is gentle
- the side stream a straight ditch -> it wanders (fading to straight where it meets the rim), its valley wider down it
- a dry country's gorge mouths bare bench -> alluvial fans, gravel
- every seed's fall the same height (the preset's beds) -> each bed's thickness varies by place, the fault's slip too
- granite no cave -> the rock shelter; boulders and trees in a cave's patch stood on the ground it replaced (floating in
  its mouth) -> none there
- a dry country's soft slopes smooth -> badlands. Found on the way: soft beds steeper in the whole settle let the scree
  slide off and the cap break back at every joint (a sawtooth rim) -> steeper only in the gullies' last sweeps; those
  sweeps' angles capped every bed at 62 deg (the sandstone stands at 78: every cliff cut back, smooth) -> only the soft
  beds'; and the settle is not done at 140 sweeps -- a wall's flutes and buttresses are what it has not yet worn away,
  so the sweeps stay 140 in all
- a karst stream's bench plain -> tufa dams. Found on the way: sills raised out into the banks (white wings over the
  bench) and crests above the bench -> the sill only a little wider than its pool, its crest at most 1.6 m over the bed;
  pools on the meanders cut straight trenches across the bends -> each pool laid along the stream, and no dams on the
  meanders (slack water drops no lime); boulders on the sills and in the pools -> none there
- every scene's lowland running on to the edge -> the coast (cliffs, platform, stacks, the cove and its fall; a beach).
  Found on the way: the sea's floor dressed as grass, showing past the end of the water at the scene's edge -> sand and
  rock under the sea, and the lab draws the water's side where it meets the edge; the shore's line a staircase of
  cells -> the lab's water at a dry corner keeps the water's level (or just under the ground, where that is lower), so
  the shore is the ground's contour; running water one colour, rapids and steps as smooth as a pool -> as white as
  it drops
- a cliffed coast's cliffs whole -> sea caves and arches. Found on the way: the arch first ran along the shore, so from
  the sea it was the stack's side; a cave's camera past the scene's edge read the ground there as undefined -> the edge's
- tropical karst's dolines all alike -> the cenote. Found on the way: its camera, set as a cave's (in front of the mouth,
  low), was under the pool's surface (drawn from above only) -> from over the rim, its ground read past the bell; a lake's
  bed dressed as grass, green through the water -> mud
- a cold country's lake an ice-scoured hollow and nothing else of the ice -> its moraine and erratics
- basalt country with nothing younger than its flows -> the cinder cone and its lava flow. Found on the way: boulders
  all over it (cinders are deep loose cover) -> none there
- a beach's land flat behind it -> dunes. Found on the way: the walls' boulders on them (a dune's sand is deep loose
  cover, as scree is) -> none on dunes or the shore
- a dry country's soft bed under a scarp only gullied -> hoodoos. Found on the way: columns on the valley's flat floor
  (where it too was 3 m under the cap's base) -> only on slopes, 14 deg and up; thin and wide-capped, a forest of
  posts -> stouter, the cap little wider than the neck, each a little out of round
- the stream across a beach in a straight trench, and on out across the sea's floor in a cut -> the mouth: a bar, a
  lagoon, the outlet pushed along the shore (shut where the stream stops in the dry season), no channel past the
  shore. Found on the way: the lagoon's rim a 3 m bank of bare rock, and its ends cut off square -> its shore eased in
  over 7 m all round (an ellipse's), sand
- a sandstone upland a smooth plain between the scarp and the lake -> a slot canyon. Found on the way: its floor
  followed the scarp's face down, a notch 15 m into the cliff -> its floor no steeper than 0.3, so it ends at the brink
  in a pour-off; a camera in it saw only a wall (the slot is a cell or two wide) -> from its rim, looking down along it
- slower with each feature, to 4.5 s -> the shore's line worked out once a cell (not again in each loop that wants it:
  the dunes' 350 ms to 20), the scarp's once a cell in the relief, the bend only by the channel; the same scene to the
  bit, 3.6 s at the most
- dry sandstone country's rim plain all one -> fins and an arch. Found on the way: no fins at all (the floor's 0.3 cap
  held the corridors' heads from cutting down, and the depth was judged at the brink, where the ground already falls)
  -> the cap only past the head, the depth the deepest; two windows, the capsule's round ends biting into the fins on
  either side -> a short capsule in the fin, a little wider than half the spacing; the cave's camera in a fin -> from
  beside the fins and above
- a wet country's scarp as clean as a dry one's (the soft bed under the cap is what slides) -> the landslide. Found on
  the way: its lobe a flat table with square sides -> a lens, ridged and hummocky; one against the gorge, the scar lost
  in it -> clear of the stream all along its reach; the scar hardly a notch (the walls settle back 8 m anyway) -> it
  bites 22-32 m in
- a cold country's cliffs with only the warm one's scree under them -> the rock glacier, its blocks bare and many
- warm granite country with nothing but its scarp and its upland's tors -> the dome. Found on the way: a low hill, not
  a dome (its height held under the till, its width its own) -> its width by its height; its camera behind a dune, then
  on the upland looking down at its back -> from the land below, out from the scarp
- every lake a near circle, whatever made it -> its outline by its cause, worked in from the lower end (which keeps the
  lip) round to its head; the exclusions round it (cone, moraine, tors, slot, fins, landslide) by the same measure
  (`lake.dist`). Found on the way: the lake's lower end 7 m from the fall's brink, the sill between them a flat plate
  at the water's level -> the lake set back 13 m, an outlet stream between
- a stream that came into its lake and brought nothing with it -> a delta. Found on the way: its levels set by the
  lake's level, which is the lip's, while the water stands where the lip's notch lets it (~0.45 m under) -- its arms
  dry, its top all land -> set by that; a fan centred on where the stream comes in lay mostly on the shore -> built
  out into the lake 1.45 times its width
- the desert's slickrock and sand in blotches, the same size everywhere, whatever the ground did -> the bare rock on
  the rises and slopes (each place against the ground ~7 m round it), the sand in the hollows and here and there down
  the bed's joints; under scrub less of it bare. Mediterranean karst comes out a limestone pavement, soil in its grikes
- a cold country's lowland stream meandering like a temperate one's -> braids. Found on the way: the threads one
  rope's pattern crossing and recrossing -> each wanders on its own noise
- a cold country's flats the same grass as a temperate one's -> patterned ground. Found on the way: `soil` (the loose
  ground's thickness) taken for the climate's soil, so none came out; then a net over every flat, tiled -> in patches
- a dry country's scarp the same bare slope under the cap whatever the cap lets through -> a spring line. Found on
  the way: the band by the contact's height alone took in a karst country's whole lowland (it lies just under the
  cap's base) -> only under a cliff (the ground well below what is round it)
- a young cone with nothing of its heat about it -> a hot spring's travertine terraces. Found on the way: none, the
  ground round a cone too flat for the 4 deg asked -> on the flat it builds its own mound; terraces 1.3 m apart, at
  1 m cells a hatching under one sheet of water -> 2.2-3.2 m, each a step down, the rims wider
- a wet basalt country's eruption the same cinder cone as a dry one's -> a maar where the ground is full of water: its
  lake held at the water table (a sink in the WATER stage, as a cenote's), not brim-full to the rim's low point
- every main fall the same ribbon, whatever it fell over -> its form by its rock: over basalt a segmented fall (the
  water in 2-3 strands between the columns' blocks; at first too close -- spreading as they fell they merged into one
  -> spaced across twice the ribbon's width, each a quarter of it), over a sandstone cap a broad sheet, a dry fall a
  ribbon
- the tropical karst upland flat but for its dolines and the cenote -> cockpit karst. Found on the way: hollows by the
  valley's edge and the scene's ponded (a sink only at each grid hollow's middle, and none at the edge -- the WATER
  stage lets the upland out at the edge only above the lip) -> a sink at every 9 m low anywhere the field reached; the
  cones bare (steeper than the forest's 32 deg, the slickrock rule taking them) -> the jungle on their flanks
- a Mediterranean karst a grid of lines across the whole land, 7 m squares to the scene's edge (the pavement wherever
  the soil was thin -- there everywhere -- and the slickrock's soil down the same joints, each one crack across the
  scene) -> the pavement in patches, and the surface's limestone joints broken into lengths, offset (the walls' joint
  field as it was: it shapes the cliffs)
- a cold granite country's land below the step a lawn -> knock and lochan. Found on the way: the knolls loaves,
  flat-topped and square-edged (a profile to the power .55) -> .9, rounded, their sizes skewed small
- a granite stream as bare as a sandstone one -> its corestones, the gorge choked with them
- basalt country's land below the step with nothing of how the basalt came up -> the dike. Found on the way: none
  where the cone stood far up the upland (every crack out from it ran on the upland) -> after 30 tries a crack of its
  own; it ponds the drainage behind it in places (left: a dike does)
- a delta of flat wedges with ruler-straight edges (its arms straight from the apex, the land what lay between them)
  -> the arms walked out, wandering, forking; the land built along them. Found on the way: a fork forked without end
  once the arms grew short (the stack overflowed) -> twice at most, and only an arm over 10 m long
- every lake's island the same mound, and loose (raised after `fanBase`: it settled as scree) -> its form by its rock,
  solid; sometimes two. The lab: the water's sheet pulled toward the eye (polygon offset) -- a shallow's bed a few cm
  under it showed through in the triangles' shapes
- basalt country's coast cut like any other rock's -> the causeway. Found on the way: the columns' tops smoothed
  into one lumpy mass (3 m across, heights ±0.6 m: under the cell size's reach) -> wider, their heights in the cross
  joints' steps (±1.1 m, rounded to 0.55 m); its cells stood steep only where a dike also stood (the joints' factor
  raised behind `if (dike)`) -> wherever any dike or causeway cell is
- a karst lake's island a needle (9 m across, 9 m high, its wall ramped over half its radius: a cone) -> a tower: wider,
  its wall over the outer quarter, a domed top, never over 1.4 times as tall as wide
- every coast's beach the same yellow sand, an ice-cold one's dunes too -> the beach of what the waves had to grind
  (shingle, black sand, white sand, sand); a cold coast's shingle a storm ridge, not dunes
- a dry country's lake the wet one's bowl with a puddle in its deepest part -> a playa: flat salt-crusted floor, cracks,
  old shorelines. Found on the way: the salt on the islands' tops and flanks (the floor marked before they rose)
  -> unmarked where an island stands over it; the cracks a maze at 4 m polygons on 1 m cells -> ~6 m, thinner
- every cliff one flat colour, its bedding the only mark on it -> streaks down it: varnish where it is dry, algae where
  it is wet. Found on the way: too faint to see (full only over 58 deg; stripes 2.6 m wide blurred to a wash across a
  face 1-2 cells deep) -> full from 47 deg, stripes ~1.3 m, near on/off; a mediterranean cliff bare of both (neither dry
  enough for varnish nor wet by the evaporation's measure) -> the algae by the rain
  the review after: on a face sloping over several cells the stripes came out a grid of dark squares (the noise
  over the plan) -> by the place along the face only (across the slope), so they run down it
- karst's side stream as any rock's: across the upland and over the gorge's wall -> on karst it sinks: a ponor at the
  end of a blind valley, the water out at the spring cave (which is given the side stream's share)
- a beach coast nothing off it but the sea -> now and then a tombolo: a tied island
- seed 7's dry granite lowland one bare pavement, banded like bedding (the lab drew every rock's beds; granite has none)
  -> no bands on granite (ground and caves); and granite's slickrock rarer -- it rots to grus, which lies in its hollows
- the cinder cone a smooth turned cone, its breach a dip of a quarter of its height, the flow a flat slab -> the breach
  a horseshoe down to the crater's floor, rills down the flanks, pressure ridges on the flow
- a dry sandstone upland's slickrock smooth as a floor -> tinajas: potholes in groups, the rain's water in some
- a cool wet country's flats all grass and forest, the water gathering on them gone nowhere -> bogs. Found on the way:
  by the wetness index alone they were strips down every drainage line (it is highest on the lines the flow takes) ->
  in the flat hollows (lower than the ground round them), in patches, never on limestone
- a tropical lagoon's shore the temperate one's sand -> mangroves round it, standing in the water
- the slot an empty corridor -> chockstones jammed in it over the floor
- a cold upland on hard rock as smooth as a warm one's -> felsenmeer: the frost's block fields
- every stack standing its full height -> some cut down to stumps: the waves' later work, the low rock awash
- the lowland's stream on its plain, no older floodplain anywhere -> river terraces: cut down into it, risers and a bench
- a cold country's scarp one even apron of scree along its foot -> couloirs: chutes cut back into the cliff, a cone
  under each. Found on the way: a cone heaped before SETTLE was lost in the apron (the soft bed's slope is already at
  the scree's angle) -> laid after, a sheet on the slope thickest along its middle
- the playa's salt flat with nothing on it but the cracks -> yardangs: the wind's ridges in the old lake's mud. Found on
  the way: at 5-9 m long they were two cells wide -- pyramids, not hulls -> 9-14 m, out onto the low benches for room
- a cold scene's snow in even blotches over all of it, the lowland's flats more than the upland (up to 37%) -> drifted
  into the hollows, off the rises, more of it up high: 12-25%, the upland's 1.5-6 times the lowland's
- a sea cave with nothing of it to see from the top -> a blowhole up from its end. Found on the way: the ground over
  every flooded cave (sea cave, arch, cenote) drawn as bare rock in a square -- its cells let down to the floor, DRESS
  read the drop as a cliff round them and the lab could not match the patch's top to them -> DRESS takes its slope
  from the ground as it was (`flooded`), the lab the colour of the nearest cell still at the patch's height
- a dry-summered limestone country's soil the same brown as anywhere -> the lab draws it terra rossa (the clay the
  limestone leaves, rusted red), between the white pavement and down its grikes
- the cone's flow one even sheet from the vent to the front but for its ridges -> levees near the vent, the drained
  channel between them; stalled whole toward the front
- an upland cone's flow 15-45 m long, stopped short of the scarp's edge (the cones stand near it) -> over the edge in a
  cascade down the face and on below: 45-100 m
- a limestone sea cliff's foot as plain as a sandstone one's -> the notch the sea dissolves at its level
- slower again with the features since, to 4.1 s -> the lines along the scene (the scarps', the stream's, the shore's:
  fbm on fbm, read at every cell in loop after loop) from tables every 0.25 m: 3.2 s at the most, the relief 800 -> 230 ms
- an open beach's waterline as smooth as the noise under it -> cusps: horns and bays, evenly spaced
- a desert's washes as bare as the land round them, the trees anywhere the wetness index put them -> a riparian
  strip: the plants along every wash and the stream, its floor sand; canyon arid seed 4: trees 41 -> 100, along the washes
- a cold upland's cliff edge as straight under the ice as under the sun -> a cirque: a bowl bitten into the edge, its
  headwall 5-11 m, a tarn 3-4 m deep behind its lip; in 19 of 24 alpine scenes (4 geologies, seeds 1-6)
- a desert playa's yardangs on karst drawn terra rossa red (the rule was warm and under 1000 mm) -> terra rossa wants
  300 mm at least: a dry summer's and a wet winter's soil, not a desert's
- a block hanging on a gorge's wall (each boulder at its cell's corner, its centre jittered up to a metre off it, on a
  steep face metres from the ground under it) -> each loose block on the lowest ground under its footprint, and none
  left on a face too steep to hold it (tors and chockstones keep their own)
- a wet country's scarp one straight wall from end to end, the upland's water going over it as a sheet -> ravines
  cut back into it, some forked, a cone at each foot; 49 in 24 wet scenes (temperate, tropical, mediterranean)
- trees standing out from a slope on their trunks (each at its cell's height, moved up to 1.35 m off it) -> each on the
  lowest corner of the cell it stands in
- a desert lowland's sand lying flat, dunes only behind a beach -> barchans: crescents with their horns on ahead
  down the wind (a first try, a mound less a hollow behind its crest, came out as rings: the hollow fell short of the
  mound's lee end -- the brink and the toe drawn instead); the slip face's slumped sand marked bare sand too, not scree
- a hot desert's spring line a strip of green and nothing more -> an oasis where its strongest seep's water stands:
  a pool at the slope's foot, date palms round it; in 8 of 18 arid scenes
- a sweep of the scenes for what should not be (a cell over all round it, a pit, water under the ground, a tree in a
  lake, a block in the air): needles at the cliffs' edges -- basalt's and limestone's joint blocks left one cell across,
  up to 12 m over all round them -> cut down to a stump at SETTLE's end; a tree or two standing in a lake's water ->
  none in water but the mangroves. (The blocks over the ground were the tors' upper ones and the chockstones: meant.)
- a lava flow's surface only its ridges and levees -> hornitos on its channel: spatter cones, welded, a throat in each
- every steep edge running aslant the grid sawn into teeth (the lab split each square along the one diagonal) -> each
  square split along the diagonal its heights differ least across: a flow's front, a cliff's foot a clean line
- a cliffed coast's platform awash all over but for knobs a cell or two across -> it rises a little to the cliff's foot
  (a shelf out of the water there) and has tide pools in it, 17-29 to a coast. (The pools first came to none: drawn at
  random from the whole square, 1500 tries found the few hundred cells they could go on four times -- now drawn from
  those cells)
- every lake the one flat blue-grey, a tarn under the ice the same as a lowland lake -> the lab shades a lake by its
  depth (lighter over the shallows, the bottom showing) and draws a cold country's milky turquoise (the ice's rock flour)
- a mediterranean scrub's trees and a desert's the same balls as a wet forest's, smaller -> their own forms: cypress
  flames and stone pines' umbrellas among the oaks, acacias flat-topped along the desert's washes
- a jungle's canopy one even sea of balls -> emergents standing clear over it, their crowns spread flat
- a lake's margins the same open water as its middle, right up to a grass shore -> reed beds in its shallows where it
  is wet and mild, in patches along the shore, tufts of stems standing out of the water
- a granite upland one even till-covered lawn but for its tors -> ruwares: low bare whalebacks of the granite just out
  of the till, gnammas in them (and on a dome's crown) holding the rain
- a tinaja's water standing to its rim's highest point -> to the lowest, where it spills
- a young cinder cone as dead as the plain round it -> fumaroles in its crater: sulphur crusts, bleached ground, the
  snow kept off them, steam over them in the lab
- the jungle's emergents flat plates on poles -> deep domed crowns
- a granite sea cliff as sheer and fluted as a sandstone one -> whalebacks rolling over to the land, the stacks domes,
  the black lichen's band over the water
- trees jittered out past the scene's edge (an emergent's crown hanging over the void) -> kept inside it, the
  emergents 8 m in
- an alpine slope's soil as smooth as a lowland's -> solifluction lobes, tongues held up by the turf at their fronts
- a granite dome a blank white bulge -> dark streaks down its flanks where the runnels' water goes, its sheets' ridges
  smoothed (they showed as a honeycomb in the mesh)
- a moraine with nothing beyond it but the stream -> kettles on its outwash, the water standing in them (a lake under
  60 m2 is let stand when it is a kettle)
- a granite upland as flat as a sandstone mesa's top -> rolling, swells and shallow basins, the bogs in them; the dome's
  algae streaks toned down (it looked ribbed)
- a fall's foam a white plate lying on the water (or the grass) -> faint overlapping blotches; and the water its
  stream runs on in at its foot was hidden with the curtain's (the lab veiled all the water near its path) -> only
  where it still falls
- a lake pouring over its lip cut off square in front of it, a flat slab where its water should be (the lab's veil
  was a box round each curtain point, and hid the water it pours from too) -> round, and only water the sheet falls
  past: above its pool, under the point
- the ice's country without what its meltwater left under it -> an esker: a winding gravel ridge down to the snout,
  beside the lake's moraine (first drawn up the lake's head: there the scene's edge left it no room)
- canyon alpine seed 9 threw ("Invalid typed array length"): the sea so close below the last step the braided belt
  had no length -> no belt there
- a limestone coast's cliffs as straight as any other's -> a calanque: a drowned valley winding back into them, sheer-
  walled, a pocket beach at its head and the dry valley above
- a slot canyon winding as a sine wave, its bends all alike -> tighter and looser, wider and narrower along it; the
  fins' corridors all opened the same way back from the brink, ruled straight -> each its own length, not quite straight
- the reeds yellow spikes, a cone each -> clumps of thin blades fanning from one foot, olive
- basalt country with nothing older than its young cone -> a neck: an old volcano's pipe standing as a tower of
  columns where its cone wore away, a skirt of them round its foot, the dikes running out from it
- the cold country's snow in even blotches all over, on the open flats as much as anywhere -> on the flats little but in
  the hollows (the wind takes it, the sun has it all day), its edges ragged; the slopes turned from the sun keep theirs
