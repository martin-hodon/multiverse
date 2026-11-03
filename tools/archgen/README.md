# Architecture asset generators

Some architecture assets carry arithmetic that is easier to set out in a script than by hand -- window heights
that follow a stair, the bays of a floor's hatch, the columns of an interior order at their angles. These
scripts write those JSON files under `assets/architecture/`:

    towers.py     elements/towers.json      square tower, round tower, viewing tower with its gallery
    temples.py    elements/orders.json, hephaestus.json, parthenon.json, didyma.json (Ionic, dipteral, hypaethral)
    pantheon.py   pantheon.json             (reads the current file and rebuilds its parts: safe to run twice)
    byz.py        elements/byzantine.json   the pieces Hagia Sophia is made of
    details.py    elements/details.json     battlements, balustrade, obelisk, buttresses, minaret, aedicula, portal
    st_basil.py   st-basil.json             nine domed-tower components crowded on a platform, rows of kokoshniki, string courses, the tent to 65m, tented porches; round it Red Square on its OSM plan:
                                            the Kremlin wall (`curtain-wall`, forked merlons) and its towers (`kremlin-tower`;
                                            the Spasskaya with Gothic tiers and its tent), the mausoleum, the Lobnoye Mesto
                                            (writes those)
    taj_mahal.py  taj-mahal.json            the tomb's iwans, chhatris and minarets
    frauenkirche.py frauenkirche.json       the stone bell on its drum, corner towers
    zwinger.py    zwinger.json              OSM plan: court, Langgalerie, Bogengalerien with walked roof terraces, corner/Wall/Glockenspiel pavilions with stairs, Kronentor + bridge, Nymphenbad, Sempergalerie halls, Zwingergraben pool (site.moat)
    notre_dame.py notre-dame.json           `gothic()`: the basilica as its nave, flying buttresses, west front, towers
                                            with their stair turrets and terraces, chevet (import it for another)
    cologne.py    cologne.json              `gothic()` with Cologne's numbers, its own `front` and two open spires
    milan.py      milan.json                five aisles in three levels, kinds of pinnacle, the broken gable, open spire, roofs walked on
    shapes.py     (a library)               the profiles' arithmetic: how tall an onion or a bell stands, and where a
                                            tent or an onion has narrowed to a given width (to set a lantern on it)
    florence.py   florence.json             adds the roofs, oculi, tribune morte, lantern buttresses, the pavement, the marble
                                            bands and the nave's seating (safe to rerun)
    dendera.py    dendera.json              the Temple of Hathor (was architecture.js egyptianTemple); its Hathor capitals'
                                            faces come from the `hathoric` order (hathor faces / wigs / features), painted here
    windmill.py   windmill.json             the tower windmill (its sail cross: items/components/windmill-sails)
    dwellings.py  dwellings/*.json          27 tents and houses of other times and peoples, each with its finish
    village.py    village/*.json            ... the houses, church, walls, yards, market, apiary, the stone bridge,
                                            the fountain, six fields, the currant rows and the orchard (with finishes)
    harbour.py    components/{quay,pier,mole,pharos,light-tower,lighthouse,stone-lantern,beacon-pagoda,horreum,speicher,kura,
                  treadwheel-crane,polyspastos,jib-crane,ship-shed,boat-slip,fish-market,customs-house}, finishes/*-port (9)
                                            the port's pieces in one frame (y 0 the quay top, +z the sea) and a finish per tradition
    port_sample.mjs harbour/*.json          (node) one harbour per finish, laid out by port.js on a straight shore
    riverside.py  village/fisher-hut, watermill, landing   the fisherman's hut and jetty, the water mill, the river
                                            landing (were village.js / architecture.js code)
    caerphilly.py caerphilly.json           the concentric water castle, its moat (`site.moat`) and tower lifts
                                            (was architecture.js englishCastle)
    versailles.py versailles.json           the palace: blocks, party walls, enfilades, stairs, the Hall of Mirrors; the corps forward, wings set back,
                                            brick Marble Court, stone arms, Ministers' wings under slate, the chapel, grille, water parterres
                                            (was architecture.js baroquePalace)
    hagia_sophia.py hagia-sophia.json       the Byzantine kit at full size, galleries and their stairs
    melk.py       melk.json                 Stift Melk on OSM's plan: Altane, Library + Marble Hall, Kolomanihof, church (twin-tower front, Emporen, drum-dome), Praelatenhof, Kaiserstiege + Kaisergang, bastions; walkable, own finish
    schwerin.py   schwerin.json             on its OSM plan, irregular: one seven-sided `court` (per-face `depths`, no roofs of its own), differing
                                            wing roofs, town towers, the great tower, gilded dome, copper dome and slender turrets (`stage-tower`:
                                            writes it), portal block, loggia, chapel choir, forecourt, bridge
    karlskirche.py karlskirche.json         round church, drum and dome, portico, the two giant columns
    chichen_itza.py chichen-itza.json       nine battered terraces, four steep stairs, the temple
    sacre_coeur.py sacre-coeur.json         Greek cross on the OSM plan, pendentives, drum + gallery storey + egg dome (`drum-dome`),
                                            4 corner domes, apse mosaic, ambulatory + 6 chapels, campanile, porch + equestrians,
                                            crypt, stair turrets to the roofs and dome galleries (writes its finish)
    horse.py      components/equestrian.json an equestrian statue: horse in lofts, the rider a seated `statue` marker
    stephansdom.py stephansdom.json         hall church, great roof, towers climbed by `tower-stair`
    st_pauls.py   st-pauls.json             (reworked 2026-11-03) Wren's plan from OSM + Parr's plan: outer walls in two storeys
                                            (the upper a screen over the aisles' flats and the hidden flyers), arcades, saucer
                                            domes on pendentives, the crossing octagon, Whispering Gallery, drum, inner dome,
                                            peristyle + Stone Gallery + attic + lead outer dome + lantern (ball and cross at 111 m),
                                            two-storey paired portico, two baroque towers (clock), half-round transept porticoes,
                                            apse, crypt (Nelson); dome stair to the roofs, a shaft stair in the drum to both
                                            galleries, the Geometric Staircase to the loggia (writes its finish)
    parliament.py parliament.json           two `court`s, the ribbed dome, loggias, turrets, pinnacles
    st_isaacs.py  st-isaacs.json            from the Commons plan + OSM: podium, body (giant order), N/S 16-column + W/E 8-column `portico`s,
                                            four corner towers (two `tower-stair`s to the roof) with square belfries and gilded domes, stylobate
                                            walk at 43 m (flight from the roof), `drum-dome` (24-column peristyle, attic, ribbed lantern), 40 bronze
                                            statues; inside three naves, crossing on pendentives, iconostasis (malachite/lapis); writes its finish
    berliner_dom.py berliner-dom.json       square church, `drum-dome` with peristyle, corner domes, portal front, roof walk
    fishermans_bastion.py fishermans-bastion.json  on its OSM plan: folded arcaded `range`s walked behind battlements,
                                            the Schulek stair, seven towers on their feet, St Stephen's court; the Matthias
                                            Church on the hill (hall `basilica`, its two towers), the Holy Trinity Column
    mainz.py      mainz.json                double-choir basilica on OSM's plan: crypt, Gothic chapels, trefoil west choir, Westturm, Memorie + cloister (Dommuseum), Gotthardkapelle; finish, doors; writes `round-stair-tower`
    moritzburg.py moritzburg.json           on OSM's plan: main body, wings, four round towers (red bells, lanterns), chapel with
                                            Dachreiter, Speisesaal risalit; terrace, ramps, lobe stairs, statues; island,
                                            guardhouses, bridges, lake as a `pool` `_moat`; halls with antlers, two dog-leg
                                            stairs; writes its finish
    el_pilar.py   el-pilar.json             on OSM's 131x69m plan: brick hall church of three naves on cruciform piers,
                                            eleven glazed-tile domes with lanterns (great dome on a buttressed drum),
                                            sail vaults, side and end chapels, plaza front (giant order, portals,
                                            niche, saints); four ~89m towers (stages, clocks, copper helms), the NW one
                                            climbed (stair, lift) to its mirador; Santa Capilla, retablo, coro, coreto;
                                            writes its finish and doors
    sultan_qaboos.py sultan-qaboos.json     `arcade-walk` riwaqs round a court, `portal`s, prayer hall and `drum-dome`,
                                            `omani-minaret`s (writes those and `crenellation`)
    ulm.py        ulm.json                  five-aisled basilica, the west tower of `gothic-tower-stage`s, its
                                            `gothic-octagon-stage` and `gothic-spire`, climbable to 143m (writes those)
    blue_mosque.py blue-mosque.json         `dome-cascade` hall, `riwaq` of `domed-arcade`s, `ottoman-minaret`s (writes those)
    temple_of_heaven.py temple-of-heaven.json   the Hall of Prayer on its three-tiered altar, the court, gate and annex halls
                                            (`chinese-hall`, `palace-wall`, `dougong` components)
    himeji.py     himeji.json               the great keep and three small keeps (`tiered`), watari-yagura, the fan-sloped
                                            stone base (`batter`), the approach stair
    horyuji.py    horyuji.json              the five-storeyed pagoda with its sorin, the Golden Hall, the Middle Gate (`tiered`),
                                            the kairo round the court (a roofed `range`)
    kinkakuji.py  kinkakuji.json            the Golden Pavilion (`tiered`, the first storey under no roof of its own), railed balconies, the
                                            phoenix in `bars`, the sosei on piles; the pond IN FRONT, a `pool` moat with its own level (`z`, `surface`),
                                            rocks and islets; no island, no bridge
    giza_sphinx.py giza.json                the plateau's plan on the compass, the lofted Sphinx, its temple, Khafre's causeway and temples, the queens' pyramids, on the hand-written pyramids (re-runnable)
    fushimi_inari.py fushimi-inari.json     the great torii, the tower gate and halls (`tiered`), the senbon torii: two
                                            tunnels of `components/torii` climbing their paths
    summer_palace.py summer-palace.json     the axis of Longevity Hill on its OSM plan: the Foxiang Ge (an octagonal `tiered`,
                                            jujia skirts seated on its walls) on its stone terrace, the Paiyun Dian and its
                                            court, gates, the Dehui Hall, the Sea of Wisdom (`chinese-hall`s), the hill's
                                            terraces and flights, two pailous, the Long Corridor (a roofed `range`), the lake
                                            (a `pool` moat with a `shore` polygon; the meadow round it, South Lake Island)
    sheikh_zayed.py sheikh-zayed.json       on its OSM plan: the sahn, a `riwaq` of small domes on three sides, the prayer hall
                                            behind its `arcade-walk` portico, three crossings under onion `drum-dome`s, roof
                                            domes, the entrance hall and `portal`, four `omani-minaret`s, pools, platform
    borobudur.py  borobudur.json            on its OSM plan, made symmetric: the foot and five redented square terraces (prisms
                                            notched for the axial stairs cut into them), niched balustrades (`enclosure`s, a
                                            seated Buddha in the first's, a small stupa over every niche), three round terraces,
                                            72 bell stupas in rings of 32/24/16, the great stupa
    angkor_wat.py angkor-wat.json           on its OSM plan, facing west: causeway, ponds, Terrace of Honour; the outer gallery,
                                            the cruciform cloister and the second gallery (roofed `range`s through their
                                            gopuras and corner pavilions), libraries, the battered bakan with its steep stairs,
                                            cross galleries and the quincunx of `shikhara` prangs with lotus-bud finials
    imam_mosque.py imam-mosque.json         on its OSM plan, its qibla axis turned west: the four-iwan court (`range`s of two-storey
                                            niches broken by the iwans' `portal`s), the dome chamber (a crossing) under the
                                            `drum-dome` onion, the qibla `minaret`s, the winter halls, the madrasas, and the
                                            entrance portal and vestibule turned to the square
    colosseum.py  colosseum.json            the Flavian amphitheatre on its four-centred `oval`: facade, three
                                            ambulatories, stairs, vomitoria, three maeniana on their walkways, hypogeum
    pont_du_gard.py pont-du-gard.json       the aqueduct at its real counts and lengths: six arches, eleven, thirty-five, the
                                            conduit roofed with slabs and walked; beds of rock up both banks with flights of
                                            `steep` stairs, the Gardon under it as a filled `pool` moat
    abu_simbel.py abu-simbel.json           Ramesses II's Great Temple: the front cut in the cliff, four seated colossi (statues,
                                            pose `colossus`, one `broken`), Ra-Horakhty's niche, 22 baboons; the rooms on one
                                            axis in a slot in the rock: pillared hall with Osirid kings, second hall, sanctuary
                                            (inner statues `seen` only from the rock or the axis); the kilts carved on the
                                            colossi's laps as lofts; the hill a loft with a `hill scree` bell round its foot
    tikal.py      tikal.json                Temple I: nine terraces with recessed corners and aprons, a 102-step `steep` stair,
                                            the shrine's three corbelled rooms, the roof comb in three stages with the king
    pisa.py       pisa.json                 the tower (ground storey, six galleries of thirty arches, belfry) with its curved
                                            `lean` storey by storey, on its catino; the Duomo: nave and transept, apses, the dome
                                            (a `stretch`ed dome on its oval drum), four loggias on the front
    forbidden_city.py forbidden-city.json   the I-shaped marble terrace of three tiers (balustrades, dragon spouts, imperial ways), the Hall of Supreme
                                            Harmony on its 72 columns (a `pent` and a `hip`, `hips` with their beasts, `dougong` under both eaves, the
                                            throne room), the Halls of Central and Preserving Harmony (`chinese-hall`)
    st_marks.py   st-marks.json             five crossings under onion `drum-dome`s, lanterns and crosses; the west front's portals, marble columns, mosaic
                                            lunettes, terrace and horses (`bars`), ogee gables, `pinnacle` tabernacles; the Campanile, Loggetta, paving
    dome_of_the_rock.py dome-of-the-rock.json  the octagon, its two arcades, the rock, the `drum-dome` in blue tile and gold, four porches, the platform and
                                            its qanatir, the Dome of the Chain
    eiffel_tower.py eiffel-tower.json       four `truss` legs on the published widths, `bars` ribs and rails, the arches and spandrels, three platforms, crown and mast
    japanese.py   (a library)               `phoenix_component` (components/phoenix: pedestal, tail rise; Kinkaku-ji's and Byodo-in's),
                                            `hoju` (the jewel finial), `rail`/`rail_path` (railed balconies, mitred at folds), `deck`,
                                            `corridor_wing` (a raised two-storey corridor folded into an L, open on posts below) (writes those)
    byodo_in.py   byodo-in.json             the Phoenix Hall facing east: the core under its mokoshi (per-face bays, the raised front bay over
                                            the window), phoenixes from `top.ridgeEnds`, the folded wings with their towers, the tail corridor on
                                            posts across the channel, the island in the Aji pond (`pool` with `islands`), pebble beach, bridge
    regensburg.py regensburg.json           `gothic()` without ambulatory: three staggered polygonal choirs (`ambulatory: false`, `sideApse`), the
                                            west towers' octagons and open spires through `gothic(spire=...)`, the Eselsturm placed from
                                            gothic's anchors (`more(add, P, A)`), the `triangle-porch` (writes it), copper Dachreiter
    ottoman.py    (a library)               the Ottoman palace kit: `conical-tower` (octagonal or square shaft, gallery, pointed lead cap,
                                            optional paired columns and pediments above), `ottoman-portico` (columns under a sachak, its
                                            ends), `ottoman-kiosk` (domed pavilion in a colonnade, a flight per door) (writes those)
    topkapi.py    topkapi.json              the ceremonial core: Middle Gate, the Second Court's porticoes from shared corners, the Divan
                                            and treasury and kitchens as `domed-arcade` rows (chimney caps), the Tower of Justice, the Gate of
                                            Felicity's canopy, the Audience Chamber
    manueline.py  (a library)               Manueline pieces: portal doorways (splayed jamb orders on twisted shafts), `front_buttresses`
                                            (buttresses run up into pinnacles), crests and pierced balustrades, `manueline-portal` (the
                                            tabernacle screen of tapering niches) and `mitre-tower` (pinnacled stages, belfry, crocketed spire)
                                            (writes those)
    jeronimos.py  jeronimos.json            the hall church on octagonal piers (`column.twist`, candelabra carving), the south portal, the
                                            west portal and narthex, the bell tower by the coro alto, the two-storey chamfered cloister
                                            (`court.arcade` with buttresses and vaulted walks), the south front of 21 arches, the west tower
    gaudi.py      (a library)               Gaudi's kit: `gaudi-pavilion` (lobed `sweep` roofs, merlons, trencadis surrounds, chimneys),
                                            `gaudi-mushroom` chimney, `gaudi-cross` (the four-armed cross), `hyperboloid-tower`, `hypostyle()`
                                            (Doric grid, outer columns leaning, vaults fitted to the bays, medallions), leaning rubble porticoes
                                            (`lean.each`/`lean.local`) (writes those)
    park_guell.py park-guell.json           the Carrer d'Olot front: rubble wall with medallions, the two pavilions, the double stair round the
                                            dragon between planter walls, the hypostyle carrying the Nature Square, the serpentine bench (a
                                            `sweep`), the portico climbing the hill, the hill itself as terrain
    javanese.py   (a library)               candi of Central Java: `candi()` (redented foot, balustraded gallery, body with kala gates and
                                            niches, diminishing tiers ringed with `ratna`s, 1/2/4 stairs, a cheap variant), `ratna` (vajra,
                                            bell, spike), `paduraksa` gate, `finish_rules()` per temple (writes those)
    prambanan.py  prambanan.json            the inner court (Shiva 47m, Vishnu, Brahma, the vahana temples, apit, kelir, patok), the 224
                                            perwara in four rows (corner ones with two stairs), gates, the court walls
    historicism.py (a library)              19th-c. castle-villa kit: `cone-turret` (1-4 storeys, up to 32 sides, conical cap), `oriel`,
                                            `castle-tower` (stages, bartizans, clock via `clock-dial`); `gable()`/`gabled()` (pointed or
                                            stepped gable screens with their roof), `storey_row`, `block`, `crest_rect`, `parapets` (writes those)
    drachenburg.py drachenburg.json         the villa on its terrace and mound, Nordturm, Kunsthalle, round bastion with flank flights and
                                            gatehouse, garden and fountain, the Vorburg
    neoclassical.py (a library)             `block` (storeys, pilasters, balustrade via `Balusters`), `temple_front` (portico + pediment),
                                            `grand_stair`, `dome_on_drum` (peristyle drum, attic, windowed ribbed dome), `tholos` (writes it)
    us_capitol.py us-capitol.json           Bulfinch's centre, the cast-iron dome and tholos, the Senate and House extensions, the west terraces
    baroque.py    (a library)               `baroque-helm` (stacked bulbs/lanterns, `lanterns: one|two`), `twin-tower-front` (stacked paired
                                            orders, pediment, clocks, every helm param as `h<Param>`), `basilica_body()` (nave/aisles/transept
                                            with barrel vaults and lunettes) (writes those)
    clocks.py     (a library)               `clock-dial` (plate, chapter ring, hour marks, hub, hands; R t ring marks mw hw hour minute;
                                            origin on the wall face, facing +z) (writes it)
    fulda.py      fulda.json                Dientzenhofer's twin-tower front over the Domplatz, the nave, the crossing drum dome, the domed
                                            side chapels, the obelisks
    frauenkirche_munich.py frauenkirche-munich.json  the brick hall church (gothic.js `hall` with eaveRise/aisleDoors/buttressIn/pent),
                                            the two towers with `welsche-haube` caps (written here), clocks, the west portal
    roman_baroque.py (a library)            `curved-colonnade` (rows of columns on an arc with entablature, roof, saints, piers),
                                            `arc_points`, `obelisk`, `fountain`, `giant_front` (Maderno-style giant order front) (writes those)
    st_peters.py  st-peters.json            Maderno's front, the cross plan with apses, Michelangelo's dome (drum-dome: paired columns, rib
                                            pairs, lucarnes, lantern), the minor cupolas, Bernini's colonnade, piazza retta, obelisk, fountains
    late_gothic.py (a library)              Saxon late-Gothic kit: curtain-arch (`curtain` head) windows, `castle_window`, `Frame`,
                                            `lucarne_row`, `wing`/`storeys`, `wendelstein` (open spiral stair tower), `lucarne` (writes those)
    albrechtsburg.py albrechtsburg.json     the palace on the Burgberg with the Grosser Wendelstein, and Meissen Cathedral beside it
    neogothic.py  (a library)               Gothic Revival kit: `Rect`, `facade_block` (arcade/loggia/upper storeys, pinnacled piers),
                                            `turret`, `gothic_tower`, `flyer_ring`, `gothic_dome` (16-sided drum, oculi, ribbed dome,
                                            pinnacle rings), `arcade`, `great_gable` (rose), `risalit`
    parliament.py parliament.json           the Hungarian Parliament: river front with arcade and risalits, the dome, the two chambers, end
                                            pavilions, courts, river towers with open spires, the land-front porch
    thai.py       (a library)               Rattanakosin kit: `thai-roof` (stacked, telescoped tiers with green eaves), `thai-gable` (na ban,
                                            bai raka, chofa), `thai-hall`/`thai-cross` (platform, pillars, walls, roofs), `thai-spire`
                                            (prasat spire), `chedi` (bell, lotus rings, spire), `prang` (redented tower, lean variant), `thai-wall`
                                            (merlons), `thai-gate` (prang/crown), `yaksha`, `seated-buddha`; `hall`, `cross`, `gate`, `wall_run` (writes those)
    grand_palace.py grand-palace.json       Grand Palace + Wat Phra Kaew (OSM): the ubosot with the Emerald Buddha, the upper terrace (chedi,
                                            mondop, Thep Bidon, Angkor model), 8 prangs, the cloister with gates and 12 yakshas, Chakri,
                                            Dusit, Maha Monthien, Boromphiman, the outer court's offices as windowed wings and courts
                                            (OSM outlines cut into oblongs), walls, forts, lawns (writes its finish and doors too)

To look at a building's statues in the lab, `arch_lab.html?statues=1` draws its `statue` markers (without them it leaves them out).

Run with `python3 tools/archgen/<name>.py`. Edit the script rather than the JSON when the change is to the
arithmetic; a JSON file's own `params` can still be changed directly for everything that is an expression.
