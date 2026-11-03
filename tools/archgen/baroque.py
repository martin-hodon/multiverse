# THE BAROQUE CHURCH'S VOCABULARY north of the Alps (a style library, L2): components written here once as parametric
# definitions, used by any generator that imports this module (fulda.py first):
#   components/baroque-helm.json      the multi-stage HELM of a Baroque tower (Zwiebelhaube, Schweifkuppel): a moulded
#                                     foot, a first BULB of any profile (a bell's concave sweep -- the Schweifkuppel -- or an
#                                     onion), an open LANTERN standing on it where it has narrowed to the lantern's width, a
#                                     second, smaller bulb, a second lantern, the spike, a gilt ball and a cross; `lanterns:
#                                     one` stops at the first lantern with a finial (the ribbed, lanternless
#                                     Renaissance cap -- Munich's -- is components/welsche-haube)
#   components/twin-tower-front.json  the TWIN-TOWER FRONT of a Baroque church: two square towers flanking a centre bay,
#                                     both in two storeys of an applied order (a Doric ground storey under an Ionic or
#                                     Corinthian upper one: order.js sets pilasters and entablature out from the storey),
#                                     engaged columns either side of the portal and the great window, the pediment over the
#                                     centre; over the towers two narrower stages (the clock storey, the belfry) and a
#                                     `baroque-helm` on each -- Fulda, and in its kind Salzburg, Kempten, Einsiedeln, St Gallen
#   basilica_body(add, ...)           (a helper, not a component) a stretch of a pillar basilica's body: aisles, arcade,
#                                     clerestory, the barrel vault with lunettes, the aisles' lean-to roofs
# Every number of a component is a param or an expression over its params; the `_x` keys say what x is. Front +z.
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = lambda rel, doc: open(os.path.join(ROOT, "assets/architecture", rel), "w").write(json.dumps(doc, indent=2) + "\n")
TAN = lambda deg: f"(sin({deg} * 0.0174533) / cos({deg} * 0.0174533))"


def helm():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    add("foot", {"type": "prism", "plan": {"sides": "sides", "radius": "R * 1.06"}, "height": "footH", "flatRoof": True, "at": [[0, 0, 0, 0]],
                 "courses": [{"y": "footH * 0.55", "h": "footH * 0.45", "out": "R * 0.04", "profile": "cornice"}],
                 "_about": "the moulded foot the first bulb stands on, on the tower's head"})
    add("bulb", {"type": "dome", "sides": "sides", "radius": "R", "thickness": 0, "at": [[0, "footH", 0, 0]], "standsOn": ["foot"],
                 "head": {"profile": "profile", "bulge": "bulge", "neck": "neck", "waist": "waist", "lift": "lift", "rise": "rise"},
                 "_about": "the first bulb: a bell (concave sweep, round crown: the Schweifkuppel) or an onion"})
    lwin = {"at": 0, "width": "LR * 0.62", "sill": "LH * 0.16", "springing": "LH * 0.78 - LR * 0.31", "head": {"profile": "semicircular"}}
    add("lantern", {"type": "enclosure", "plan": {"sides": "sides", "radius": "LR"}, "thickness": "LR * 0.16", "height": "LH", "openings": [lwin],
                    "glass": "glazed", "at": [[0, "0 - LR * 0.06", 0, 0]], "atop": "bulb", "atopR": "LR", "standsOn": ["bulb"],
                    "_about": "the lantern on the bulb where it has narrowed to LR: an arch in every face (open: glazed 0)"})
    add("lantern head", {"type": "prism", "plan": {"sides": "sides", "radius": "LR * 1.14"}, "height": "LH * 0.1", "flatRoof": True,
                         "at": [[0, 0, 0, 0]], "atop": "lantern", "standsOn": ["lantern"], "_about": "its cornice and the floor of the next bulb"})
    add("bulb 2", {"type": "dome", "sides": "sides", "radius": "R2", "thickness": 0, "at": [[0, 0, 0, 0]], "atop": "lantern head", "standsOn": ["lantern head"],
                   "head": {"profile": "profile2", "bulge": "bulge2", "neck": "neck2", "waist": "waist2", "lift": "lift2", "rise": "rise2"},
                   "when": {"lanterns": "two"}, "_about": "the second, smaller bulb on the lantern"})
    lwin2 = {"at": 0, "width": "L2R * 0.6", "sill": "L2H * 0.2", "springing": "L2H * 0.75 - L2R * 0.3", "head": {"profile": "semicircular"}}
    add("lantern 2", {"type": "enclosure", "plan": {"sides": "sides", "radius": "L2R"}, "thickness": "L2R * 0.2", "height": "L2H", "openings": [lwin2],
                      "glass": "glazed", "at": [[0, "0 - L2R * 0.06", 0, 0]], "atop": "bulb 2", "atopR": "L2R", "standsOn": ["bulb 2"],
                      "when": {"lanterns": "two"}, "_about": "the second lantern, on the second bulb"})
    add("lantern 2 head", {"type": "prism", "plan": {"sides": "sides", "radius": "L2R * 1.16"}, "height": "L2H * 0.12", "flatRoof": True,
                           "at": [[0, 0, 0, 0]], "atop": "lantern 2", "standsOn": ["lantern 2"], "when": {"lanterns": "two"}})
    add("spike", {"type": "dome", "sides": "sides", "radius": "L2R * 0.95", "thickness": 0, "at": [[0, 0, 0, 0]], "atop": "lantern 2 head",
                  "standsOn": ["lantern 2 head"], "head": {"profile": "spikeProfile", "rise": "spikeH", "bulge": 1.15, "neck": 0.9}, "when": {"lanterns": "two"},
                  "_about": "the spike (Spitzhelm) over the second lantern: a cone, or a little onion"})
    add("ball", {"type": "dome", "sides": 8, "radius": "ballR * 0.4", "thickness": 0, "at": [[0, "0 - ballR * 0.1", 0, 0]], "atop": "spike", "atopR": "ballR * 0.4",
                 "standsOn": ["spike"], "head": {"profile": "onion", "bulge": 2.5, "neck": 0.45}, "when": {"lanterns": "two"},
                 "_about": "the gilt ball (a pineapple at Fulda) on the spike's point"})
    add("cross", {"type": "bars", "w": "crossW", "h": "crossW",
                  "lines": [[0, 0, 0, 0, "crossH", 0], ["0 - crossH * 0.28", "crossH * 0.66", 0, "crossH * 0.28", "crossH * 0.66", 0]],
                  "at": [[0, "0 - ballR * 0.2", 0, 0]], "atop": "ball", "standsOn": ["ball"], "when": {"lanterns": "two"}, "_about": "the cross on the ball"})
    add("finial", {"type": "column", "radius": "LR * 0.08", "height": "LH * 0.9", "sides": 6, "at": [[0, 0, 0, 0]], "atop": "lantern head",
                   "standsOn": ["lantern head"], "when": {"lanterns": "one"}, "_about": "a finial on the first lantern: the one-lantern helm's (lanterns: one)"})
    doc = {"name": "baroque helm",
           "_about": "THE MULTI-STAGE HELM OF A BAROQUE TOWER (Zwiebelhaube, Schweifkuppel), set on a tower's head: a moulded foot, a first BULB (profile bell: the concave sweep and round crown of the Schweifkuppel; onion: the Zwiebel), an open LANTERN standing on it where it has narrowed to LR, its cornice, a second smaller BULB, a second LANTERN, the SPIKE, the gilt BALL and the CROSS -- Fulda's towers. lanterns: one stops at the first lantern with a finial (the ribbed, lanternless Renaissance cap is components/welsche-haube). Place it at the middle of the tower's head.",
           "params": {"detail": 4, "sides": 8, "R": 3.6, "footH": 0.6, "profile": "bell", "waist": 0.78, "lift": 0.58, "bulge": 1.25, "neck": 0.85, "rise": "R",
                      "LR": "R * 0.48", "LH": "R * 1.0", "glazed": 0, "lanterns": "two",
                      "R2": "LR * 1.15", "profile2": "bell", "waist2": 0.8, "lift2": 0.6, "bulge2": 1.3, "neck2": 0.8, "rise2": "R2",
                      "L2R": "R2 * 0.36", "L2H": "R2 * 0.8", "spikeProfile": "trigonal", "spikeH": "R * 0.75", "ballR": "R * 0.13",
                      "crossH": "R * 0.7", "crossW": "R * 0.035",
                      "_R": "the first bulb's radius at its foot (the tower's head is a little wider: the foot reaches R * 1.06); sides its plan (8: an octagon)",
                      "_profile": "the first bulb: bell (waist, lift: height R * (lift + waist), the round crown R * waist across) or onion (bulge, neck) or any dome profile",
                      "_lanterns": "two (the bulb, lantern, second bulb, second lantern, spike, ball, cross) or one (the bulb, its lantern and a finial)",
                      "_LR": "the first lantern: LR in radius, LH tall, standing where the bulb has narrowed to LR; glazed 1 puts glass in its arches",
                      "_R2": "the second bulb (profile2 and its own waist2/lift2/bulge2/neck2), standing on the lantern's cornice",
                      "_L2R": "the second lantern, L2R by L2H, on the second bulb",
                      "_spikeH": "the spike over the second lantern (spikeProfile trigonal: a cone spikeH tall; onion: a little bulb), the ball ballR and the cross crossH on it"},
           "build": build, "parts": parts}
    OUT("components/baroque-helm.json", doc)


def twin_tower_front():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    HT = "H1 + H2"                                           # the towers' and the centre's two storeys
    door = {"at": 0, "width": "doorW", "sill": 0, "springing": "doorH - doorW / 2", "head": {"profile": "semicircular"},
            "surround": {"head": "pediment", "pediment": "segmental", "keystone": True}}
    great = {"at": 0, "width": "winW", "sill": "winSill", "springing": "winSill + winH - winW / 2", "head": {"profile": "semicircular"},
             "surround": {"head": "cornice", "keystone": True}}
    back = {"at": 0, "width": "backW", "sill": 0, "springing": "backH - backW / 2", "head": {"profile": "semicircular"}}
    orders = [{"tier": 0, "kind": "order1"}, {"tier": 1, "kind": "order2"}]
    add("centre", {"type": "enclosure", "plan": {"rect": ["cW", "D"]}, "thickness": "t", "height": HT, "interior": True,
                   "tiers": [{"h": "H1", "openings": []}, {"openings": []}],
                   "faces": {"0": [{"h": "H1", "openings": [door]}, {"openings": [great]}],
                             "2": [{"h": "H1", "openings": [back]}, {"openings": []}]},
                   "orders": orders, "courses": {"skip": [1, 2, 3]}, "at": [[0, 0, "0 - D / 2", 0]],
                   "_about": "the centre between the towers, two storeys: the portal below under its segmental pediment, the great window above (each in its surround), the arch into the church behind (backW), its order of pilasters"})
    twin = {"at": 0, "width": "tWin", "sill": "H1 * 0.32", "springing": "H1 * 0.32 + tWin * 1.7", "head": {"profile": "semicircular"}, "surround": True}
    twin2 = {"at": 0, "width": "tWin", "sill": "H2 * 0.3", "springing": "H2 * 0.3 + tWin * 1.7", "head": {"profile": "semicircular"}, "surround": True}
    tiers = [{"h": "H1", "openings": [twin]}, {"openings": [twin2]}]
    # (portals three: each tower's front a side portal under a cornice in its window's place -- the openings' `when`; one
    #  opening to a tier's stretch of wall, so the window does not stand over it)
    tdoor = {"at": 0, "width": "tDoorW", "sill": 0, "springing": "tDoorH - tDoorW / 2", "head": {"profile": "semicircular"},
             "surround": {"head": "cornice", "keystone": True}, "when": {"portals": "three"}}
    front = [{"h": "H1", "openings": [{**twin, "when": {"portals": "one"}}, tdoor]}, {"openings": [twin2]}]
    for side, x, inner in (("left", "0 - (cW / 2 + tW / 2)", 1), ("right", "cW / 2 + tW / 2", 3)):
        add(f"tower {side}", {"type": "enclosure", "plan": {"rect": ["tW", "tD"]}, "thickness": "t", "height": HT, "tiers": tiers,
                              "faces": {"0": front, str(inner): []}, "orders": orders, "courses": {"skip": [inner]}, "at": [[x, 0, "0 - tD / 2", 0]],
                              **({"_about": "the two towers' lower storeys, the centre's height: a window in each free face (portals three: a door in the front in its place), their order"} if side == "left" else {})})
    TX = ["0 - (cW / 2 + tW / 2)", "cW / 2 + tW / 2"]
    at = lambda y: [[x, y, "0 - tW / 2", 0] for x in TX]
    add("tower floors", {"type": "box", "width": "tW - 2 * t", "length": "tD - 2 * t", "height": 0.4, "flatRoof": True,
                         "at": [[x, f"{HT} - 0.4", "0 - tD / 2", 0] for x in TX],
                         "standsOn": ["tower left"], "_about": "the floor closing each tower at the head of its lower storeys, under the open stages (its roof where the stages do not stand on it: tD past tW)"})
    arch = lambda h, w, sill: {"at": 0, "width": w, "sill": sill, "springing": f"{h} * 0.86 - ({w}) / 2", "head": {"profile": "semicircular"}, "glass": False}
    add("clock stage", {"type": "enclosure", "plan": {"rect": ["tW - 2 * s", "tW - 2 * s"]}, "thickness": "t * 0.8", "height": "H3",
                        "openings": [arch("H3", "clockWinW", "clockWinSill")], "orders": [{"tier": 0, "kind": "order2"}], "courses": True, "at": at(HT),
                        "standsOn": ["tower left"], "when": {"clockStage": "yes"},
                        "_about": "the third stage, set in by s: the clock storey, a tall louvred arch in each face over the dial (clockStage: no and H3 0 leave it out)"})
    add("clock floor", {"type": "box", "width": "tW - 2 * s - 1.6 * t", "length": "tW - 2 * s - 1.6 * t", "height": 0.4, "flatRoof": True,
                        "at": at(f"{HT} + H3 - 0.4"), "standsOn": ["clock stage"], "when": {"clockStage": "yes"}})
    # the dials: on the clock stage's front and outer faces (clockR, its middle clockY up the stage) -- components/clock-dial
    half = "(tW / 2 - s)"
    add("clocks", {"type": "component", "use": "components/clock-dial", "params": {"R": "clockR", "t": "clockR * 0.08"},
                   "at": [*[[x, f"{HT} + clockY", f"0 - tW / 2 + {half}", 0] for x in TX],
                          ["0 - (cW / 2 + tW / 2) - " + half, f"{HT} + clockY", "0 - tW / 2", "0 - 1.5707963"],
                          ["cW / 2 + tW / 2 + " + half, f"{HT} + clockY", "0 - tW / 2", 1.5707963]],
                   "standsOn": ["clock stage"], "when": {"clock": "yes"},
                   "_about": "the clock dials (components/clock-dial) on each tower's front and outer face of the clock stage"})
    add("belfry", {"type": "enclosure", "plan": {"rect": ["tW - 4 * s", "tW - 4 * s"], "chamfer": "chamf"}, "thickness": "t * 0.7", "height": "H4",
                   "faces": {"main": [arch("H4", "belfryWinW", "H4 * 0.16")], "chamfer": []}, "courses": True, "at": at(f"{HT} + H3"), "standsOn": ["clock stage", "tower floors"],
                   "_about": "the belfry, set in again, its corners chamfered (chamf): a tall open arch in each main face"})
    add("tower heads", {"type": "prism", "plan": {"rect": ["tW - 4 * s + 2 * co", "tW - 4 * s + 2 * co"], "chamfer": "chamf + co * 0.8"}, "height": "co * 1.6",
                        "flatRoof": True, "at": at(f"{HT} + H3 + H4"), "standsOn": ["belfry"], "_about": "the belfry's cornice and ceiling: what the helm stands on"})
    HP = ["sides", "footH", "profile", "waist", "lift", "bulge", "neck", "rise", "LR", "LH", "glazed", "lanterns", "R2", "profile2", "waist2", "lift2",
          "bulge2", "neck2", "rise2", "L2R", "L2H", "spikeProfile", "spikeH", "ballR", "crossH", "crossW"]
    hp = {"R": "hR", **{k: "h" + k[0].upper() + k[1:] for k in HP}}
    add("helms", {"type": "component", "use": "components/baroque-helm", "params": hp,
                  "at": at(f"{HT} + H3 + H4 + co * 1.6"), "standsOn": ["tower heads"], "_about": "a `baroque-helm` on each tower, every one of its params passed as h<Param>"})
    # the engaged columns, paired and stacked: the same x in both storeys (colA, colB from the middle: the portal's pair
    # and the pair at the centre's edge), the order's columns proud of its pilasters
    c1 = "(H1 - 0.6) * 0.8"                                  # (Vignola: the column four fifths of the storey, the entablature the rest)
    cx = [["0 - (colA + colB) / 2", 0.6, "pcR * 0.45", 0], ["(colA + colB) / 2", 0.6, "pcR * 0.45", 0]]
    add("portal columns", {"type": "colonnade", "order": "order1", "count": 2, "spacing": "colB - colA", "columnR": "pcR", "height": c1, "taper": 0.9,
                           "at": cx, "standsOn": ["centre"], "_about": "the ground storey's engaged columns, a pair each side of the portal at colA and colB (three-quarter columns: half their radius in the wall)"})
    c2 = "H2 * 0.78"
    add("window columns", {"type": "colonnade", "order": "order2", "count": 2, "spacing": "colB - colA", "columnR": "pcR * 0.85", "height": c2, "taper": 0.9,
                           "at": [[x, "H1 + 0.3", "pcR * 0.4", 0] for x, _, _, _ in cx], "standsOn": ["centre"],
                           "_about": "the upper storey's, stacked over them, framing the great window; the pair's middles (colA + colB) / 2 are where statues stand"})
    add("pediment", {"type": "roof", "form": "gable", "width": "cW + 2 * co", "length": "pedD", "pitch": "pitch", "overhang": "co",
                     "at": [[0, HT, "0 - pedD / 2", 0]], "standsOn": ["centre"], "when": {"pediment": "triangle"},
                     "_about": "the pediment over the centre and the roof behind it, back to the church's (pediment: none leaves it out)"})
    doc = {"name": "twin-tower front",
           "_about": "THE TWIN-TOWER FRONT OF A BAROQUE CHURCH: a centre cW wide between two towers tW across, D deep (the centre) and tD (the towers' lower storeys) back from the front line at z = 0, in two storeys of an applied order (order1 below, order2 above: pilasters and entablature from the storeys' heights), engaged columns paired and stacked at colA and colB, the portal under a segmental pediment, the great window above, the pediment over the centre; the towers go on in two stages set in by s -- the clock storey (its dials: components/clock-dial) with a tall louvred arch in each face, the belfry with chamfered corners and open arches -- and a `baroque-helm` crowns each. Place it at the middle of the front line; the church joins it behind (the arch backW x backH in the centre's back wall).",
           "params": {"detail": 4, "cW": 13.0, "tW": 8.2, "D": 9.0, "tD": "tW", "pedD": "D", "t": 1.4, "H1": 13.0, "H2": 15.4, "H3": 9.4, "H4": 6.0, "s": 0.5, "co": 0.5, "chamf": 0.8,
                      "pitch": 30, "pediment": "triangle", "order1": "doric", "order2": "corinthian",
                      "doorW": 3.6, "doorH": 7.0, "winW": 3.4, "winSill": 2.6, "winH": 8.4, "tWin": 1.3, "backW": 9.0, "backH": 11.0, "pcR": 0.6,
                      "colA": "doorW / 2 + pcR * 2.6", "colB": "cW / 2 + pcR * 1.5",
                      "portals": "one", "tDoorW": "tW * 0.3", "tDoorH": "H1 * 0.5",
                      "clockStage": "yes", "clock": "yes", "clockR": "tW * 0.13", "clockY": "H3 * 0.2", "clockWinW": "tW * 0.32", "clockWinSill": "clockY + clockR + 0.5",
                      "belfryWinW": "tW * 0.32",
                      "hR": "(tW - 4 * s) * 0.44", "hLR": "hR * 0.5", "hLH": "hR * 0.95", "hR2": "hLR * 1.12", "hL2R": "hR2 * 0.4", "hL2H": "hR2 * 0.85",
                      "hSpikeH": "hR * 0.75", "hWaist": 0.78, "hLift": 0.58, "hWaist2": 0.8, "hLift2": 0.6, "hCrossH": "hR * 0.62", "hBallR": "hR * 0.13",
                      "hSides": 8, "hFootH": 0.6, "hProfile": "bell", "hBulge": 1.25, "hNeck": 0.85, "hRise": "hR", "hGlazed": 0, "hLanterns": "two",
                      "hProfile2": "bell", "hBulge2": 1.3, "hNeck2": 0.8, "hRise2": "hR2", "hSpikeProfile": "trigonal", "hCrossW": "hR * 0.035",
                      "_cW": "the centre's width between the towers, D its depth; the towers tW wide, their lower storeys tD deep (tW: square; D: a front block as deep as the centre), the stages over them square; walls t; the pediment's roof pedD deep (short of D where a church roof meets it)",
                      "_H1": "the ground storey (order1, the portal doorW x doorH), H2 the upper (order2, the great window winW wide from winSill, winH tall); pediment triangle|none at `pitch`",
                      "_portals": "one|three: the centre's portal alone, or a side portal in each tower's front too (tDoorW x tDoorH) in place of the tower's window",
                      "_colA": "the engaged columns' x from the middle, the same in both storeys: a pair each side at colA and colB (pcR their radius, the upper 0.85 of it)",
                      "_H3": "over the towers' two storeys: the clock stage H3 (clockStage yes|no: no with H3 0 drops it) and the belfry H4, each set in by s; their arches clockWinW (from clockWinSill) and belfryWinW; the belfry's corners chamfered chamf; co the cornices' reach",
                      "_clock": "yes|no: a dial (components/clock-dial) clockR on each tower's front and outer face, its middle clockY up the clock stage",
                      "_hR": "the helms (`baroque-helm`), each of its params as h + Param: first bulb hR (hProfile bell: hWaist, hLift; onion: hBulge, hNeck), lantern hLR x hLH, hLanterns two|one, second bulb hR2, second lantern hL2R x hL2H, spike hSpikeH, ball hBallR, cross hCrossH",
                      "_backW": "the arch through the centre's back wall into the church"},
           "build": build, "parts": parts}
    OUT("components/twin-tower-front.json", doc)


def basilica_body(add, nm, z0, z1, bays, *, front, back, cfront=(), cback=(), AW, NW, AH, NH, T=1.2, CT=1.0, order="tuscan",
                  aisleWin=(2.4, 4.0, 9.8), clerWin=(2.0, 4.4, 7.4), vault=5.6, aislePitch=20, about=None):
    """A STRETCH OF A BAROQUE PILLAR BASILICA's body, z0 (the +z end) to z1, in `bays` bays (a generator's helper, not a
    component: it adds its parts by `add`): the aisles' outer walls AW across and AH high with a window a bay (aisleWin:
    width, sill, springing) and their `order`; the arcade of piers and round arches down each side; the clerestory NW
    across up to NH on it, a window a bay (clerWin: width, sill and springing over AH) clear of the aisles' lean-to roofs
    (aislePitch); the nave's BARREL VAULT WITH LUNETTES (Stichkappen: a groin vault a bay, round across, its arch along
    pointed to rise `vault` so each window stands in its lunette), springing so its crown is 0.6 under NH; the end faces'
    openings front/back (aisles) and cfront/cback (clerestory) -- an arch where the church runs on, [] where blind. +z east."""
    Q = 1.5707963
    r2 = lambda v: round(v, 3)
    semi = {"profile": "semicircular"}
    L, zm = z0 - z1, (z0 + z1) / 2
    bay = L / bays
    w, sill, spr = aisleWin
    add(f"{nm} aisles", {"type": "enclosure", "plan": {"rect": [AW, r2(L)]}, "thickness": T, "height": AH, "interior": True,
                         "openings": {"pattern": str(bays), "width": w, "gap": r2(bay - w), "end": 1.0, "sill": sill, "springing": spr, "head": semi, "surround": True},
                         "faces": {"0": list(front), "2": list(back)}, "orders": [{"tier": 0, "kind": order}], "courses": {"skip": [0, 2]},
                         "at": [[0, 0, r2(zm), 0]], **({"_about": about} if about else {})})
    PX = NW / 2 - CT / 2                                     # the piers under the clerestory's wall
    piers = [r2(z0 - k * bay) for k in range(1, bays)]
    add(f"{nm} piers", {"type": "box", "width": 1.4, "length": 1.8, "height": AH, "at": [[r2(sx * PX), 0, z, 0] for sx in (1, -1) for z in piers],
                        **({"_about": "the arcade's piers down each side of the nave"} if about else {})})
    stops = [z0 - T] + [z for p in piers for z in (p + 0.9, p - 0.9)] + [z1 + T]
    by = {}
    for a, b in ((stops[i], stops[i + 1]) for i in range(0, len(stops), 2)): by.setdefault(r2(a - b), []).append(r2((a + b) / 2))
    for i, (sw, zs) in enumerate(sorted(by.items())):
        add(f"{nm} arcade {i + 1}", {"type": "barrel", "width": sw, "length": 1.4, "springing": r2(AH - 1.0 - sw / 2), "top": AH, "head": semi,
                                     "at": [[r2(sx * PX + 0.7), 0, z, Q] for sx in (1, -1) for z in zs], "standsOn": [f"{nm} piers"],
                                     **({"_about": "the arcade's arches from pier to pier, carrying the clerestory"} if about and i == 0 else {})})
    w, sill, spr = clerWin
    add(f"{nm} clerestory", {"type": "enclosure", "plan": {"rect": [NW, r2(L)]}, "thickness": CT, "height": NH - AH, "interior": True,
                             "openings": {"pattern": str(bays), "width": w, "gap": r2(bay - w), "end": 1.0, "sill": sill, "springing": spr, "head": semi, "surround": {"head": False}},
                             "faces": {"0": list(cfront), "2": list(cback)}, "courses": {"skip": [0, 2]}, "at": [[0, AH, r2(zm), 0]], "standsOn": [f"{nm} arcade 1"],
                             **({"_about": "the clerestory over the arcade, a window a bay over the aisles' roofs"} if about else {})})
    VW = NW - 2 * CT
    VS = NH - 0.6 - VW / 2
    spread = ((vault / (bay / 2)) ** 2 - 1) / 2
    add(f"{nm} vault", {"type": "groin", "width": r2(VW), "length": r2(bay), "springing": r2(VS), "top": NH, "clears": AH,
                        "across": semi, "along": {"profile": "pointed", "spread": round(spread, 4)},
                        "at": [[0, 0, r2(z0 - (k + 0.5) * bay), 0] for k in range(bays)], "standsOn": [f"{nm} clerestory"],
                        **({"_about": "the barrel vault with lunettes, a bay to each: round across, its arch along each wall pointed up round the window"} if about else {})})
    add(f"{nm} aisle roofs", {"type": "roof", "form": "shed", "width": r2(AW / 2 - NW / 2), "length": r2(L), "pitch": aislePitch, "overhang": 0.4,
                              "at": [[r2(sx * (NW / 2 + (AW - NW) / 4)), AH, r2(zm), (0 if sx > 0 else 2 * Q)] for sx in (1, -1)],
                              "standsOn": [f"{nm} aisles"], **({"_about": "the aisles' lean-to roofs against the clerestory"} if about else {})})


if __name__ == "__main__":
    helm(); twin_tower_front()
