from sealib import *

# EDIBLE CRAB (Cancer pagurus), the carapace 20 cm across and 13 long. BUILT FACING +z: its side is the model's forward
# (+x), so what the world walks forward a crab walks SIDEWAYS. World x = the crab's right, z = its front, y up.
GS = 0.9                               # (the gait's speed)
Y0 = 0.032                             # (the body's bone: the carapace sits LOW -- v5: 8 mm lower, its underside 1.3 cm off the ground)
DY = -0.008                            # (v5: every shape of the shell and face written for the old height, moved down by this)
R = Rig()
R.add("body", None, [0, Y0, 0], shape={"shape": "sphere", "size": {"r": 0.05}})
def ad(a, s):                          # (yaw for a limb at anatomical angle a -- from the side toward the front -- on side s)
    return -a if s > 0 else 180 + a
def seg_ell(id, bone, a, b, ry, rz, color, yaw, pitch, k=0.002, over=1.1):
    """a flattened limb segment from a to b: tall in its own vertical plane, thin fore and aft"""
    return S("ell", id=id, bone=bone, c=mul(add(a, b), .5), r=[math.dist(a, b) / 2 * over, ry, rz], rot=[0, yaw, pitch], k=k, color=color)
def seg_box(id, bone, a, b, ry, rz, color, yaw, pitch, k=0.0008, over=1.0):
    """(v4) an ANGULAR limb segment from a to b: a rounded box, tall in its own vertical plane, thin fore and aft"""
    return S("box", id=id, bone=bone, c=mul(add(a, b), .5), r=[math.dist(a, b) / 2 * over, ry, rz], round=round(0.85 * min(ry, rz), 5),
             rot=[0, yaw, pitch], k=k, color=color)
RIM = lambda t, f=1.0: [0.1 * math.sin(t) * f, -0.003 + 0.064 * math.cos(t) * f]     # (the carapace's outline: x, z)
sh = [
    # the CARAPACE: a broad, low shield, wider than long, widest a third back; the dome over it low
    # (v4, 2026-11-07: the DOME raised -- a shield, not a pancake: its top 3.4 cm over the rim; the margin a thin edge)
    S("ell", id="carapace", c=[0, 0.042, -0.003], r=[0.1, 0.015, 0.064], k=0.005, color="@body"),
    S("ell", id="dome", c=[0, 0.05, -0.006], r=[0.084, 0.026, 0.055], k=0.014, color="@body"),
    S("ell", id="front", c=[0, 0.047, 0.036], r=[0.052, 0.017, 0.026], k=0.01, color="@body"),
    # (the regions of the back: the gastric bulge and the two branchial swellings, low)
    S("ell", id="gastric", c=[0, 0.07, 0.012], r=[0.026, 0.008, 0.022], k=0.008, color="@body"),
    S("ell", id="branchR", c=[0.042, 0.064, -0.014], r=[0.03, 0.008, 0.03], k=0.01, color="@body"),
    S("ell", id="branchL", c=[-0.042, 0.064, -0.014], r=[0.03, 0.008, 0.03], k=0.01, color="@body"),
    # underneath: the sternum, the abdomen folded under it, the mouthparts' frame
    S("ell", id="sternum", c=[0, 0.035, -0.006], r=[0.058, 0.009, 0.041], k=0.008, color="@body"),   # (v5: tucked in under the rim, out of sight from the side)
    S("ell", id="abdomen", c=[0, 0.026, -0.026], r=[0.026, 0.005, 0.036], k=0.004, color="@body"),
    S("ell", id="mouth", c=[0, 0.034, 0.046], r=[0.02, 0.009, 0.013], k=0.005, color="@body"),
    # (v6: the PALE only on the underside's own face -- painted below the rim's lowest line, so from the side and from
    # ground level the shell colour runs right round)
    S("ell", id="pale", c=[0, 0.022, -0.006], r=[0.06, 0.0075, 0.052], op="paint", kc=0.003, color="@under"),
    # the FRONTAL MARGIN between the eye sockets: three small teeth
    S("ell", id="frontal0", c=[0, 0.046, 0.0625], r=[0.0045, 0.0042, 0.0045], k=0.0015, color="@body"),
]
for s in (1, -1):
    S_ = "RL"[s < 0]
    # the PIE-CRUST: ten low rounded lobes, close-set along each front-lateral margin, from the orbit to the widest point
    # (v4: nine bigger lobes standing well out of the outline, the notches between them deep -- cut in the shell's own
    # colour, not dark: dark ones read as holes from above)
    for i in range(9):
        t = math.radians(22 + 7.2 * i)
        x, z = RIM(t, 1.075)
        sh.append(S("ell", id=f"lobe{S_}{i}", c=[s * x, 0.041, z], r=[0.0098, 0.0082, 0.0098], k=0.0014, color="@body"))
        if 0 < i < 8:   # (the notch between two lobes -- v5: down the rim's depth, so they show from the side too; not the last, by the first leg's root: its cut left slivers the mesh's decimation flung out)
            xn, zn = RIM(t - math.radians(3.6), 1.17)
            sh.append(S("ell", id=f"notch{S_}{i}", c=[s * xn, 0.041, zn], r=[0.0048, 0.012, 0.0048], k=0.0008, color="@body", op="sub"))
    sh += [
        S("ell", id=f"frontal{S_}", c=[s * 0.0088, 0.046, 0.0608], r=[0.0042, 0.004, 0.0042], k=0.0015, color="@body"),
        # the eye sockets: notches in the front margin, the EYESTALKS folded into them
        # (v4: the eyestalks RAISED out of their sockets, the eyes standing on them at the front edge)
        S("ell", id=f"orbit{S_}", c=[s * 0.021, 0.05, 0.06], r=[0.0068, 0.005, 0.0062], k=0.002, color="@dark", op="sub"),
        S("tube", id=f"stalk{S_}", pts=[[s * 0.0185, 0.047, 0.055, 0.0032], [s * 0.0205, 0.054, 0.0615, 0.0027], [s * 0.022, 0.0585, 0.0645, 0.0025]], k=0.0012, color="@body"),
        S("ell", id=f"eye{S_}", c=[s * 0.0226, 0.0612, 0.0662], r=[0.0042, 0.0042, 0.0042], k=0.0006, kc=0.0004, color="@eye"),
        S("tube", id=f"antenna{S_}", pts=[[s * 0.006, 0.042, 0.06, 0.0024], [s * 0.008, 0.046, 0.07, 0.0023], [s * 0.0105, 0.048, 0.078, 0.0022]], k=0.0012, color="@body"),
    ]
# (v5: the RIM -- a thick rounded edge right round the shield, 1.9 cm deep, not a knife edge)
sh.append(S("tube", id="rim", pts=[[0.1 * 0.965 * math.sin(t), 0.039, -0.003 + 0.064 * 0.955 * math.cos(t), 0.0095]
                                   for t in (2 * math.pi * (j + 0.5) / 40 for j in range(42))], k=0.007, color="@body"))   # (the loop overlapping its start: an exact close left one vertex flung far out by the mesh's decimation)
for q in sh:                           # (v5: the shell and face down to the new height)
    if "c" in q: q["c"][1] += DY
    if "pts" in q: q["pts"] = [[a, b + DY, c] + r for a, b, c, *r in q["pts"]]
# the FOUR PAIRS OF WALKING LEGS: short and flattened (tall in their own plane, thin fore and aft), the merus nearly
# level to the knee, carpus and propodus sloping down, the tapered dactyl to the ground; each lifts in its own plane on
# the gait's clock, alternating (one side's first and third with the other's second and fourth), the knee flexing a
# beat behind the lift
LEGS = [(0.03, 0.068, 40, 0.95), (0.009, 0.075, 12, 1.04), (-0.013, 0.073, -18, 1.0), (-0.032, 0.062, -48, 0.88)]
CP = [-14, 8, -6]                      # (v6: the claw's three pitches, set so the palm lies level)
CY = 0.022                             # (the legs' roots under the carapace's margin)
for s in (1, -1):
    S_ = "RL"[s < 0]
    for i, (f, l, a, sc) in enumerate(LEGS):
        # (v5: SHORTER, and ARCHED -- the merus up and out to a high knee, carpus and propodus down 40 degrees, the
        # dactyl steeply down to its point on the ground)
        L = [0.05 * sc, 0.034 * sc, 0.026 * sc]   # (v6: the merus long enough to carry the knee clear of the rim)
        ph = (0 if (i % 2 == 0) == (s > 0) else math.pi)
        p1, p2 = 18, -54                  # (v6: a LOW arch -- the knee near the rim's top, out beyond it, not a stilt under it)
        yk = CY + L[0] * math.sin(math.radians(p1)) + L[1] * math.sin(math.radians(p1 + p2))
        p3 = -math.degrees(math.asin(min(0.95, max(0.2, (yk - 0.002) / L[2])))) - (p1 + p2)
        m, c, dd = f"leg{i}{S_}m", f"leg{i}{S_}c", f"leg{i}{S_}d"
        yaw = ad(a, s)
        R.add(m, "body", [s * (l + 0.012), CY - Y0, f], rot=[0, yaw, p1], anim={"axis": "z", "deg": 11, "speed": GS, "phase": ph})
        R.add(c, m, [L[0], 0, 0], rot=[0, 0, p2], anim={"axis": "z", "deg": 9, "speed": GS, "phase": ph + 1.3})
        R.add(dd, c, [L[1], 0, 0], rot=[0, 0, p3])
        A0 = R.to_world(m, [-0.008, 0, 0]); K = R.joint(c); D0 = R.joint(dd); T = R.to_world(dd, [L[2], 0, 0])
        # (v4: SEGMENTED -- the merus, the short carpus and the propodus each its own flattened blade, blended tightly so
        # every joint shows as a waist with a darker knuckle on it; the dactyl a tapering spike, its point dark)
        Kc = R.to_world(c, [L[1] * 0.36, 0, 0])
        sh += [
            # (v5: broad flat blades -- the merus 1.9 cm deep)
            seg_box(f"merus{i}{S_}", m, A0, K, 0.0095 * sc, 0.0052 * sc, "@leg", yaw, p1, k=0.0008, over=0.97),
            seg_box(f"carpus{i}{S_}", c, K, Kc, 0.0074 * sc, 0.0047 * sc, "@leg", yaw, p1 + p2, k=0.0007, over=0.9),
            seg_box(f"propod{i}{S_}", c, Kc, D0, 0.0068 * sc, 0.0043 * sc, "@leg", yaw, p1 + p2, k=0.0007, over=0.94),
            S("ell", id=f"knee{i}{S_}", bone=c, c=add(K, [0, 0.0042 * sc, 0]), r=[0.0058 * sc, 0.005 * sc, 0.0048 * sc], k=0.0008, color="@body"),
            S("ell", id=f"wrist{i}{S_}", bone=dd, c=add(D0, [0, 0.0026 * sc, 0]), r=[0.0044 * sc, 0.004 * sc, 0.0038 * sc], k=0.0007, color="@body"),
            S("tube", id=f"dactyl{i}{S_}", bone=dd, pts=[D0 + [0.0044 * sc], R.to_world(dd, [L[2] * 0.5, 0, 0]) + [0.0032 * sc]], k=0.0008, kc=0.0006, color="@leg"),
            S("tube", id=f"dpoint{i}{S_}", bone=dd, pts=[R.to_world(dd, [L[2] * 0.5, 0, 0]) + [0.0032 * sc], R.to_world(dd, [L[2] * 0.8, 0, 0]) + [0.0018 * sc], T + [0.0006]],
              k=0.0006, kc=0.0005, color="@tip"),
        ]
    # the CHELIPEDS, folded in front of the face: a short merus forward and out, the knobbed carpus, the big swollen
    # PALM (the propodus: an oval box) pointing forward and in, its FIXED FINGER, and the movable DACTYL above it that
    # closes against it (it pinches now and then); both fingers toothed along their cutting edges and BLACK-TIPPED
    # (v4: the claws HEAVY -- the palm 9 cm long and 5 deep, the fingers 4 cm, thick and black over their outer half)
    m, c, p, dd = f"cheM{S_}", f"cheC{S_}", f"cheP{S_}", f"cheD{S_}"
    # (v5: held LOW in front of the face -- the merus angled down from under the rim's front, the palm level, its sole
    # near the ground)
    # (v6: FOLDED -- the merus short and out from under the shell's front corner, the carpus at the corner, the palm
    # turned IN along the front margin (168 degrees: nearly across), level and low just before the mouth, the
    # fingertips meeting at the midline)
    CS, MA, CA, PA = 0.78, 45, 85, 168     # (the claw's size against v5's; the merus's, carpus's and palm's headings)
    R.add(m, "body", [s * 0.07, 0.026 - Y0, 0.035], rot=[0, ad(MA, s), CP[0]])
    R.add(c, m, [0.022, 0, 0], rot=[0, -s * (CA - MA), CP[1]])
    R.add(p, c, [0.024, 0, 0], rot=[0, -s * (PA - CA), CP[2]], anim={"axis": "y", "deg": 3, "speed": 0.35, "phase": 0 if s > 0 else 1.7})
    R.add(dd, p, [0.07 * CS, 0.012 * CS, 0], rot=[0, 0, 7], anim={"axis": "z", "deg": 12, "speed": 0.55, "phase": 0 if s > 0 else 2.2, "flick": 3})
    yp = ad(PA, s)
    P = lambda b, v: R.to_world(b, [v[0] * CS, v[1] * CS, v[2] * CS])
    sh += [
        S("tube", id=f"cmerus{S_}", bone=m, pts=[P(m, [-0.008, 0, 0]) + [0.00858], P(m, [0.016, 0.001, 0]) + [0.00975], R.joint(c) + [0.009204]], k=0.003, color="@leg"),
        S("ell", id=f"ccarpus{S_}", bone=c, c=P(c, [0.013, 0.001, 0]), r=[0.01482, 0.01131, 0.01131], k=0.003, color="@body"),
        S("ell", id=f"ccarpusknob{S_}", bone=c, c=P(c, [0.014, 0.009, 0.005 * s]), r=[0.00468, 0.00273, 0.0039], k=0.0015, color="@body"),
        # (the palm: a swollen oval box -- deep, flattened side to side, its upper edge a ridge)
        S("ell", id=f"palm{S_}", bone=p, c=P(p, [0.036, 0.002, 0]), r=[0.03354, 0.01638, 0.01482], rot=[0, yp, -2], k=0.003, color="@body"),
        S("ell", id=f"palmridge{S_}", bone=p, c=P(p, [0.036, 0.017, 0]), r=[0.02808, 0.00351, 0.0078], rot=[0, yp, -2], k=0.003, color="@body"),
        S("ell", id=f"palmheel{S_}", bone=p, c=P(p, [0.066, -0.004, 0]), r=[0.01248, 0.01326, 0.0117], rot=[0, yp, 0], k=0.003, color="@body"),
        # (the fixed finger, red-brown at its root, black over its last half)
        S("tube", id=f"fixed{S_}", bone=p, pts=[P(p, [0.07, -0.007, 0]) + [0.00936], P(p, [0.085, -0.0075, 0]) + [0.00741]], k=0.002, kc=0.0012, color="@body"),
        S("tube", id=f"fixedtip{S_}", bone=p, pts=[P(p, [0.085, -0.0075, 0]) + [0.00741], P(p, [0.098, -0.006, 0]) + [0.005616], P(p, [0.111, -0.002, 0]) + [0.00351], P(p, [0.117, 0.002, 0]) + [0.001716]],
          k=0.0015, kc=0.001, color="@tip"),
        # (the movable finger above it, closing down on it)
        S("tube", id=f"dactylC{S_}", bone=dd, pts=[P(dd, [-0.005, 0, 0]) + [0.00819], P(dd, [0.014, 0.001, 0]) + [0.006864]], k=0.002, kc=0.0012, color="@body"),
        S("tube", id=f"dactyltip{S_}", bone=dd, pts=[P(dd, [0.014, 0.001, 0]) + [0.006864], P(dd, [0.027, -0.002, 0]) + [0.005304], P(dd, [0.039, -0.008, 0]) + [0.003276], P(dd, [0.045, -0.013, 0]) + [0.00156]],
          k=0.0015, kc=0.001, color="@tip"),
    ]
    # (the teeth: low black knobs along both fingers' cutting edges)
    for j, xx in enumerate((0.076, 0.086, 0.096)):
        sh.append(S("ell", id=f"tooth{S_}{j}", bone=p, c=P(p, [xx, 0.0005, 0]), r=[0.002652, 0.002496, 0.00234], k=0.0008, color="@tip"))
    for j, xx in enumerate((0.008, 0.018)):
        sh.append(S("ell", id=f"toothD{S_}{j}", bone=dd, c=P(dd, [xx, -0.0072, 0]), r=[0.002652, 0.002496, 0.00234], k=0.0008, color="@tip"))

d = {
    "name": "crab",
    "_about": "SCULPTED (2026-11-05; v4 2026-11-07: the dome raised, the pie-crust lobes standing out, eyes up on their stalks, the claws heavy, the legs segmented with pointed dark dactyls; v5: a thick rounded rim, seated lower, the legs shorter, broad and arched knee-up, the claws held low, the shell dark to its rim with the pale only underneath; docs/engines.md 'the sculpt overlay'): an edible crab (Cancer pagurus), the carapace 20 cm across and 13 long -- a broad, low SHIELD, wider than long, widest a third back, its front-lateral margins PIE-CRUST (ten low rounded lobes a side), the frontal margin's three small teeth between the EYE SOCKETS, the eyestalks folded into their notches, the antennules; underneath the sternum and the abdomen folded under; it sits LOW, its underside 2 cm off the ground. The two CHELIPEDS folded in front of the face: a short merus, the knobbed carpus, the big swollen PALM (the propodus, an oval box) pointing forward and in, its fixed finger and the movable dactyl above it, both toothed and BLACK-TIPPED (the dactyl pinches now and then: `flick`). FOUR PAIRS OF WALKING LEGS, short and flattened, the merus nearly level to the knee, carpus and propodus sloping down, the tapered dactyl to the ground (the span about twice the carapace). Red-brown above, cream below. BUILT FACING +z, so its side is the model's forward: what the world walks forward a crab walks SIDEWAYS. The legs lift in their own planes on the gait's clock, alternating (one side's first and third with the other's second and fourth), each knee flexing a beat behind its lift.",
    "kind": "parts",
    "facet": False,
    "flags": {"print": "none", "legLen": 0.07},
    "colors": {"body": "#a4532e", "leg": "#ad5c34", "under": "#e2caa0", "tip": "#141010", "eye": "#0c0a08", "dark": "#3a1a10"},
    "coats": [{"name": "edible crab"}, {"name": "shore crab (green)", "scale": 0.32, "body": "#46522a", "leg": "#56602e", "under": "#c8b45a", "dark": "#1e2410"},
              {"name": "shore crab (red-orange)", "scale": 0.3, "body": "#9a5a2a", "leg": "#a8682e", "under": "#d8b468", "dark": "#3a2010"}],
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0012, "tris": [11000, 3200]},
        "shade": {"back": 0.7, "belly": 1.0, "k": 0.006, "at": -0.004, "on": "@body", "mode": "mix", "tol": 0.03},   # (v5: the shell's top and its rim a deep brick red, darkening only the shell's own colour (`mix`, a tight tol: the legs keep theirs), no pale tone -- the pale underside is the sternum's own colour; `at` is from the root joint)
        "shape": sh,
    },
}
d = keep_coats("crab", d)
write("crab", d)
