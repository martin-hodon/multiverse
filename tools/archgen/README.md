# Architecture asset generators

Some architecture assets carry arithmetic that is easier to set out in a script than by hand -- window heights
that follow a stair, the bays of a floor's hatch, the columns of an interior order at their angles. These
scripts write those JSON files under `assets/architecture/`:

    towers.py     elements/towers.json      square tower, round tower, viewing tower with its gallery
    temples.py    elements/orders.json, hephaestus.json, parthenon.json, didyma.json (Ionic, dipteral, hypaethral)
    pantheon.py   pantheon.json             (reads the current file and rebuilds its parts: safe to run twice)
    byz.py        elements/byzantine.json   the pieces Hagia Sophia is made of
    details.py    elements/details.json     battlements, balustrade, obelisk, buttresses, minaret, aedicula, portal
    st_basil.py   st-basil.json             nine domed-tower components on a platform
    taj_mahal.py  taj-mahal.json            the tomb's iwans, chhatris and minarets
    frauenkirche.py frauenkirche.json       the stone bell on its drum, corner towers
    zwinger.py    zwinger.json              galleries, curved galleries, pavilions, the Kronentor
    notre_dame.py notre-dame.json           `gothic()`: the basilica as its nave, flying buttresses, west front, towers
                                            with their stair turrets and terraces, chevet (import it for another)
    cologne.py    cologne.json              `gothic()` with Cologne's numbers and its two spires
    milan.py      milan.json                five aisles, the forest of pinnacles, the tiburio, roofs walked on
    shapes.py     (a library)               the profiles' arithmetic: how tall an onion or a bell stands, and where a
                                            tent or an onion has narrowed to a given width (to set a lantern on it)
    florence.py   florence.json             adds the roofs, oculi, tribune morte, lantern buttresses, the pavement, the marble
                                            bands and the nave's seating (safe to rerun)
    dendera.py    dendera.json              the Temple of Hathor (was architecture.js egyptianTemple)
    windmill.py   windmill.json             the tower windmill (its sail cross: items/components/windmill-sails)
    dwellings.py  dwellings/*.json          27 tents and houses of other times and peoples, each with its finish
    village.py    village/*.json            ... the houses, church, walls, yards, market, apiary, the stone bridge,
                                            the fountain, six fields, the currant rows and the orchard (with finishes)
    riverside.py  village/fisher-hut, watermill, landing   the fisherman's hut and jetty, the water mill, the river
                                            landing (were village.js / architecture.js code)
    caerphilly.py caerphilly.json           the concentric water castle, its moat (`site.moat`) and tower lifts
                                            (was architecture.js englishCastle)
    versailles.py versailles.json           the palace: blocks, party walls, enfilades, stairs, the Hall of Mirrors
                                            (was architecture.js baroquePalace)
    hagia_sophia.py hagia-sophia.json       the Byzantine kit at full size, galleries and their stairs
    melk.py       melk.json                 palace wings round a court, the church, the terrace and the Altane
    schwerin.py   schwerin.json             wings round a pentagon, corner towers, the gate tower, the bridge
    karlskirche.py karlskirche.json         round church, drum and dome, portico, the two giant columns
    chichen_itza.py chichen-itza.json       nine battered terraces, four steep stairs, the temple
    sacre_coeur.py sacre-coeur.json         Greek cross, pendentives, drum and dome, stair turret to the roofs
    stephansdom.py stephansdom.json         hall church, great roof, towers climbed by `tower-stair`
    st_pauls.py   st-pauls.json             Latin cross, `drum-dome` with peristyle, two-storey `portico`, west towers
    parliament.py parliament.json           two `court`s, the ribbed dome, loggias, turrets, pinnacles
    st_isaacs.py  st-isaacs.json            body, pendentives, `drum-dome` with peristyle, four `portico`s, corner domes
    berliner_dom.py berliner-dom.json       square church, `drum-dome` with peristyle, corner domes, portal front, roof walk
    fishermans_bastion.py fishermans-bastion.json  arcaded hall, terraces, galleries, seven towers, the double stair
    mainz.py      mainz.json                double-choir basilica, stepped west crossing tower, `round-stair-tower`s
    moritzburg.py moritzburg.json           a `court` on its island, round corner towers, terrace, bridge (moat in `_moat`)
    el_pilar.py   el-pilar.json             hall church under a central dome and cupolas, four `baroque-tower`s (writes it)
    sultan_qaboos.py sultan-qaboos.json     `arcade-walk` riwaqs round a court, `portal`s, prayer hall and `drum-dome`,
                                            `omani-minaret`s (writes those and `crenellation`)
    ulm.py        ulm.json                  five-aisled basilica, the west tower of `gothic-tower-stage`s, its
                                            `gothic-octagon-stage` and `gothic-spire`, climbable to 143m (writes those)
    blue_mosque.py blue-mosque.json         `dome-cascade` hall, `riwaq` of `domed-arcade`s, `ottoman-minaret`s (writes those)
    temple_of_heaven.py temple-of-heaven.json   the Hall of Prayer on its three-tiered altar, the court, gate and annex halls
                                            (`chinese-hall`, `palace-wall`, `dougong` components)
    colosseum.py  colosseum.json            the Flavian amphitheatre on its four-centred `oval`: facade, three
                                            ambulatories, stairs, vomitoria, three maeniana on their walkways, hypogeum

Run with `python3 tools/archgen/<name>.py`. Edit the script rather than the JSON when the change is to the
arithmetic; a JSON file's own `params` can still be changed directly for everything that is an expression.
