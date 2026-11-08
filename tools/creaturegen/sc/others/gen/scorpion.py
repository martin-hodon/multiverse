import sys; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
PI = math.pi
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def seg(a, b, r): return {"a": [0, 0, 0], "c": lerp([0, 0, 0], sub(b, a), .5), "b": sub(b, a), "r1": r, "r2": r * .85}
BODY = [-.005, .016, 0]; HEAD = [.018, .016, 0]
# the metasoma: five segments, each longer than the last, arching up over the back; the telson hanging forward from it
TL = [.0095, .01, .011, .012, .0135]; TA = [22, 52, 88, 122, 152]
T = [[-.023, .0165, 0]]
for l, a in zip(TL, TA):
    r = math.radians(a); T.append([T[-1][0] - l * math.cos(r), T[-1][1] + l * math.sin(r), 0])
TELE = add(T[-1], [math.cos(math.radians(205 - 180)) * .011, -math.sin(math.radians(25)) * .011, 0])   # (the vesicle's far end: forward and down)
parts = [
    {"id": "body", "parent": None, "shape": "capsule", "size": {"r": .011, "len": .03}, "geomRot": [0, 0, 90], "pos": BODY, "color": "@body"},
    {"id": "head", "parent": "body", "shape": "sphere", "size": {"r": .009}, "pos": sub(HEAD, BODY), "color": "@body"},
]
prev, pa = "body", BODY
for i in range(5):
    parts.append({"id": f"tail{i + 1}", "parent": prev, "shape": "tube", "size": seg(T[i], T[i + 1], .006 - .0004 * i), "pos": sub(T[i], pa), "color": "@body",
                  "anim": {"axis": "y", "deg": 7, "speed": .5, "phase": .6} if i == 0 else {"axis": "z", "deg": 5, "speed": .5, "phase": round(.6 + .6 * i, 3)}})
    prev, pa = f"tail{i + 1}", T[i]
parts.append({"id": "sting", "parent": "tail5", "shape": "tube", "size": seg(T[5], TELE, .004), "pos": sub(T[5], T[4]), "color": "@sting",
              "anim": {"axis": "z", "deg": 6, "speed": .5, "phase": 3.6}})
LEGX = [.03, .0245, .019, .0135]; KX = [.007, .002, -.004, -.009]; FX = [.007, .002, -.005, -.012]
PALP = ([.033, .0125, .0065], [.043, .016, .021], [.055, .0145, .0195], [.07, .0125, .014])
for S, sz in (("L", 1), ("R", -1)):
    z = lambda v: [v[0], v[1], v[2] * sz]
    sh0, el, wr, tip = PALP
    parts += [
        {"id": f"arm{S}", "parent": "head", "shape": "tube", "size": seg(z(sh0), z(el), .003), "pos": z(sub(sh0, HEAD)), "color": "@body",
         "anim": {"axis": "y", "deg": 8, "speed": .4, "phase": 1.0}},
        {"id": f"fore{S}", "parent": f"arm{S}", "shape": "tube", "size": seg(z(el), z(wr), .003), "pos": z(sub(el, sh0)), "color": "@body"},
        {"id": f"claw{S}", "parent": f"fore{S}", "shape": "tube", "size": seg(z(wr), z(tip), .005), "pos": z(sub(wr, el)), "color": "@body"},
        {"id": f"pinch{S}", "parent": f"claw{S}", "shape": "tube", "size": seg(z([.0695, .0128, .0162]), z([.082, .012, .0115]), .0012), "pos": z(sub([.0695, .0128, .0162], wr)), "color": "@body",
         "anim": {"axis": "y", "deg": 14 * sz, "speed": .6, "phase": 0, "flick": 3}},
    ]
    for i in range(4):
        hip = [LEGX[i], .012, .0075]; knee = [LEGX[i] + KX[i], .021, .02]; foot = [knee[0] + FX[i], .0006, .031]
        parts += [
            {"id": f"leg{i}{S}", "parent": "body" if i > 1 else "head", "shape": "tube", "size": seg(z(hip), z(knee), .0022), "pos": z(sub(hip, BODY if i > 1 else HEAD)), "color": "@leg",
             "anim": {"axis": "y", "deg": 16, "speed": .8, "phase": 0 if i % 2 == 0 else 3.1416}},
            {"id": f"shin{i}{S}", "parent": f"leg{i}{S}", "shape": "tube", "size": seg(z(knee), z(foot), .0016), "pos": z(sub(knee, hip)), "color": "@leg"},
        ]
sh = []
def S(id, **k):
    d = {"id": id}; d.update(k); sh.append(d); return d
gl = {"wet": .15}
# ---- prosoma: the carapace with the median eyes on their tubercle; the mesosoma: seven tergites, overlapping plates
S("carapace", type="ell", bone="head", c=[.023, .0155, 0], r=[.0125, .0052, .0098], k=.0015, color="@body", **gl)
S("tubercle", type="ell", bone="head", c=[.026, .0205, 0], r=[.0035, .0016, .0028], k=.001, color="@body", **gl)
for j, dx in enumerate((0, -.0019)):   # two of the lateral eyes each side, on the carapace's front corner
    S(f"lateral{j}", type="sphere", bone="head", c=[.0333 + dx, .0170 - .0003 * j, .0066 + .0006 * j], r=.0011, k=0, color="@eye", wet=.4, mirror=True)
S("belly", type="ell", c=[-.004, .0115, 0], r=[.021, .0035, .0092], k=.0015, color="@under")
for i in range(7):
    x = .0095 - i * .0046; w = .0105 - .0002 * abs(i - 2.5) ** 1.6
    # (each a thin plate, its back edge lifted over the front of the next: a shingled back, not a row of beads)
    S(f"tergite{i}", type="ell", c=[x - .0004, .0166, 0], r=[.0036, .0026, w * 1.02], rot=[0, 0, 9], k=.0003, kc=.0003, color="@body" if i % 2 else "@body2", **gl)
S("mesosoma", type="ell", c=[-.0045, .0142, 0], r=[.017, .0036, .0102], k=.0012, color="@body2", **gl)
S("pectines", type="ell", c=[.011, .0095, .0035], r=[.0035, .0008, .0025], rot=[0, -30, 0], k=.0005, color="@pale", mirror=True)
# ---- metasoma: five knobbed segments, a crease at each joint; the telson's bulbous vesicle and the curved aculeus
for i in range(5):
    a, b = T[i], T[i + 1]; r0 = .0052 - .00025 * i
    S(f"meta{i}", type="tube", bone=f"tail{i + 1}", pts=[lerp(a, b, .02) + [r0 * .74], lerp(a, b, .2) + [r0 * .95], lerp(a, b, .62) + [r0], lerp(a, b, .98) + [r0 * .8]], k=.0003, kc=.0005, color="@body" if i % 2 else "@body2", **gl)
    S(f"keel{i}", type="tube", bone=f"tail{i + 1}", pts=[add(lerp(a, b, .1), [0, 0, 0]) + [r0 * .3], add(lerp(a, b, .9), [0, 0, 0]) + [r0 * .3]], k=.0003, color="@body", op="sub") if False else None
sh = [p for p in sh if p]
V0 = T[5]
S("vesicle", type="ell", bone="sting", c=lerp(V0, TELE, .45), r=[.0058, .0045, .0042], rot=[0, 0, -25], k=.0008, color="@sting", **gl)
S("aculeus", type="tube", bone="sting", pts=[lerp(V0, TELE, .85) + [.0024], add(TELE, [.0015, -.002, 0]) + [.0013], add(TELE, [.0005, -.0055, 0]) + [.0007], add(TELE, [-.002, -.0075, 0]) + [.0004]], k=.0004, kc=.0004, color="@tip")
# ---- pedipalps: femur and patella, the swollen chela with its fixed finger and the movable one (it pinches)
sh0, el, wr, tip = PALP
S("palpFemur", type="tube", bone="armL", pts=[sh0 + [.0026], lerp(sh0, el, .5) + [.0027], el + [.0026]], k=.0007, color="@body", mirror=True, **gl)
S("patella", type="tube", bone="foreL", pts=[el + [.0026], lerp(el, wr, .5) + [.0031], wr + [.0032]], k=.0007, color="@body", mirror=True, **gl)
S("hand", type="ell", bone="clawL", c=lerp(wr, tip, .45), r=[.0085, .0045, .0055], rot=[0, 22, 0], k=.001, color="@claw", mirror=True, **gl)
S("fixed", type="tube", bone="clawL", pts=[[.068, .0125, .0118, .0021], [.075, .0122, .0098, .0015], [.0825, .0118, .0078, .0007]], k=.0004, color="@claw", mirror=True, **gl)
S("movable", type="tube", bone="pinchL", pts=[[.0695, .0128, .0162, .0021], [.076, .0124, .0148, .0015], [.0825, .012, .0118, .0007]], k=.0004, color="@claw", mirror=True, **gl)
# ---- walking legs: femur up to the knee, tibia and tarsus down to the ground
for i in range(4):
    hip = [LEGX[i], .012, .0075]; knee = [LEGX[i] + KX[i], .021, .02]; foot = [knee[0] + FX[i], .0006, .031]
    S(f"femur{i}", type="tube", bone=f"leg{i}L", pts=[hip + [.0018], lerp(hip, knee, .5) + [.0017], knee + [.0015]], k=.0006, color="@leg", mirror=True)
    mid = add(lerp(knee, foot, .45), [0, .0015, 0])
    S(f"tibia{i}", type="tube", bone=f"shin{i}L", pts=[knee + [.0015], mid + [.0013], foot + [.0008]], k=.0005, color="@leg", mirror=True)

d = {
    "name": "scorpion",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a scorpion 9 cm long (with its tail laid out) -- the carapace with the median eyes on their tubercle, seven overlapping tergites, the pectines under it; the metasoma five knobbed segments each longer than the last, arched up over the back on a chain of bones that sways, the bulbous vesicle and its curved aculeus hanging forward; pedipalps with a swollen chela, the movable finger pinching now and then; four pairs of walking legs, femur up to the knee and down to the ground; glossy near-black",
    "kind": "parts",
    "flags": {"print": "none", "legLen": .19},   # (legLen: species.js gaitBase reads a capsule leg's len+r, NaN for tube legs; .8 x .19 = the old capsule base)
    "colors": {"body": "#2a221b", "body2": "#241d17", "under": "#4a3a2a", "pale": "#8a7050", "leg": "#3c3024", "claw": "#2e241c", "sting": "#5a2c18", "tip": "#1a1210", "eye": "#0a0808"},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": .0007, "tris": [5200, 1600]},
        "shape": sh,
        "eyes": {"at": [.027, .0215, .0016], "from": [.024, .0185, 0], "r": .0011, "color": "#060404", "iris": "#141010", "pupil": "round", "lid": "@body", "sink": .2},
    },
}
dump("others/scorpion.json", d)
print(len(sh), "shapes")
