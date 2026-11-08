# Pachycephalosaurus wyomingensis (2026-11-05): a bipedal ornithischian on the tyrannosaur's rig (gen_theropods.py helpers)
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import save, Shapes, fix_order, floorR
from gen_theropods import rig, frame, tail, leg, eyelids, finish

def pachycephalosaurus():
    H, hz, s = 1.3, 0.25, 1.3 / 3.15
    hx, hy = 1.45, 1.66
    about = ("PACHYCEPHALOSAURUS WYOMINGENSIS (sculpt overlay, 2026-11-05): 4.5 m, ~400 kg, the hips 1.3 m up -- a bipedal "
             "ornithischian, the body level over the hips with a broad torso and a deep gut slung between the legs; a short thick "
             "S-neck; a 0.55 m skull under a massively thick dome (22 cm of bone), ringed round its back and sides by bony knobs "
             "and short blunt spikes on the squamosal shelf, small knobs along the snout; big forward-facing eyes; a short muzzle "
             "to a pointed beak with small leaf-shaped teeth behind it; short arms with five small fingers; long strong legs with "
             "blunt hoof-like claws; a heavy tail held stiff and level by its ossified tendons. Grey-brown, a paler horn-toned "
             "dome, a cream belly.")
    sh, el, wr = [0.92, 1.06, 0.22], [0.86, 0.9, 0.26], [1.02, 0.84, 0.25]
    col = {"body": "#6b5d48", "front": "#6b5d48", "neck": "#6b5d48", "head": "#625542", "muzzle": "#6b5d48", "eye": "#b88a2c",
           "leg": "#665944", "foot": "#3e3529", "tail": "#6b5d48", "back": "#4c4233", "flank": "#7b6d55", "belly": "#c8b997",
           "lip": "#6e624c", "claw": "#2e2820", "nostril": "#2a241c", "lid": "#3a3226", "mouth": "#3a2a22", "brow": "#574b3a",
           "dome": "#76684f", "domeRim": "#665a46", "knob": "#4e4334", "beak": "#38302a"}
    d = rig("pachycephalosaurus", about, H, hz, 0.58, ([0.95, 1.28], [1.35, 1.6], 0.24, 0.15), [hx, hy, 0.15],
            (-0.22, 1.36, 2.45, 0.12, 0.27), (sh, el, wr), {"h": 2.6, "speed": 1.6}, col)
    d["tail"]["sway"] = 3            # (stiffened by its ossified tendons)
    d["headTurn"] = 10
    sc = {"pat": "scales", "frame": frame(0.3)}
    S = Shapes()
    # ---- the trunk: level over the hips, broad, a deep gut between the legs (the pubis swept back), no rump overhang
    S.ell("hips", [0.0, 1.36, 0], [0.42, 0.2, 0.27], "@back", k=0.09, **sc)
    S.ell("torso", [0.38, 1.2, 0], [0.68, 0.33, 0.34], "@body", k=0.1, **sc)
    S.ell("gut", [0.28, 0.97, 0], [0.55, 0.3, 0.36], "@body", k=0.1, **sc)
    S.ell("spine", [0.3, 1.45, 0], [0.78, 0.11, 0.15], "@back", k=0.08, kc=0.06, **sc)
    S.ell("belly", [0.34, 0.77, 0], [0.46, 0.12, 0.27], "@belly", k=0.08, kc=0.06, **sc)
    S.ell("chest", [0.8, 1.14, 0], [0.28, 0.27, 0.25], "@body", k=0.08, **sc)
    S.ell("breast", [0.88, 0.97, 0], [0.2, 0.14, 0.18], "@belly", k=0.06, kc=0.05, **sc)
    tail(S, H, -0.2, 2.45, 1.36, 1.26, 0.27, sc=sc, root_w=1.1, prof=[(0, 1), (0.23, 0.86), (0.45, 0.71), (0.64, 0.56), (0.82, 0.4), (0.95, 0.25), (1.0, 0.13)])
    # ---- the neck: short, thick, an S up into the back of the skull
    S.tube("neck", [[0.88, 1.2, 0, 0.25], [1.1, 1.36, 0, 0.19], [1.27, 1.52, 0, 0.15], [1.38, 1.6, 0, 0.13]], "@body", bone="neck", k=0.07, **sc)
    S.tube("nape", [[0.85, 1.36, 0, 0.13], [1.1, 1.5, 0, 0.1], [1.3, 1.66, 0, 0.08]], "@back", bone="neck", k=0.06, kc=0.05, **sc)
    S.ell("throat", [1.17, 1.32, 0], [0.18, 0.09, 0.12], "@flank", bone="neck", k=0.05, kc=0.04, **sc)
    # ---- the head: a cranium under a thick dome; the face short, down-sloping, to a beak
    S.box("cranium", [1.47, 1.63, 0], [0.13, 0.1, 0.115], "@head", bone="head", k=0.05, round=0.05, **sc)
    S.ell("dome", [1.49, 1.745, 0], [0.19, 0.14, 0.14], "@dome", bone="head", k=0.08, kc=0.07, rot=[0, 0, 16], pat="scales", frame=frame(0.12))
    S.ell("forehead", [1.6, 1.665, 0], [0.11, 0.075, 0.09], "@head", bone="head", k=0.06, rot=[0, 0, -30], **sc)
    S.ell("domeRim", [1.44, 1.7, 0], [0.18, 0.055, 0.14], "@domeRim", bone="head", k=0.04, kc=0.04, rot=[0, 0, 8], **sc)
    S.ell("shelf", [1.36, 1.675, 0], [0.06, 0.045, 0.125], "@domeRim", bone="head", k=0.04, kc=0.02, **sc)
    S.ell("snout", [1.66, 1.57, 0], [0.15, 0.075, 0.075], "@head", bone="head", k=0.04, rot=[0, 0, -18], **sc)
    S.ell("muzzle", [1.79, 1.51, 0], [0.06, 0.05, 0.05], "@head", bone="head", k=0.03, **sc)
    S.cone("beak", [1.8, 1.5, 0], [1.87, 1.455, 0], 0.042, 0.016, "@beak", bone="head", k=0.015, kc=0.006)
    S.ell("predentary", [1.82, 1.445, 0], [0.045, 0.018, 0.032], "@beak", bone="head", k=0.012, kc=0.005, rot=[0, 0, -15])
    S.ell("jaw", [1.6, 1.48, 0], [0.19, 0.04, 0.08], "@lip", bone="head", k=0.035, rot=[0, 0, -12], **sc)
    S.ell("jawPale", [1.58, 1.45, 0], [0.17, 0.025, 0.07], "@belly", bone="head", k=0.02, kc=0.01, rot=[0, 0, -12])
    S.ell("cheek", [1.53, 1.56, 0.1], [0.08, 0.06, 0.04], "@brow", bone="head", k=0.03, mirror=True)
    S.ell("nostril", [1.8, 1.535, 0.035], [0.018, 0.012, 0.012], "@nostril", bone="head", k=0.004, kc=0.002, mirror=True)
    # the ring of knobs round the back and sides of the dome (the squamosal shelf), longer blunt spikes at its back corners
    for j, th in enumerate(range(100, 181, 20)):     # (degrees round from the front, on the left side; 180 = the back)
        a = math.radians(th)
        cx, cz = 1.43 + 0.215 * math.cos(a), 0.165 * math.sin(a)
        y = 1.7 + 0.025 * math.cos(a)
        r = 0.036 + 0.01 * ((th - 100) / 80)
        S.sph(f"knob{j}", [cx, y, cz], r, "@knob", bone="head", k=0.01, kc=0.004, mirror=th != 180)
    for j, (th, ln) in enumerate([(118, 0.07), (138, 0.08), (158, 0.07)]):
        a = math.radians(th)
        b = [1.43 + 0.21 * math.cos(a), 1.69, 0.16 * math.sin(a)]
        t = [1.43 + (0.21 + ln * 0.6) * math.cos(a), 1.69 - 0.045, (0.16 + ln) * math.sin(a)]
        S.cone(f"spike{j}", b, t, 0.036, 0.015, "@knob", bone="head", k=0.012, kc=0.005, mirror=True)
    for j, x in enumerate([1.6, 1.67, 1.74]):          # small knobs along the snout
        S.sph(f"nasalKnob{j}", [x, 1.663 - (x - 1.6) * 0.4, 0.036], 0.026, "@knob", bone="head", k=0.008, kc=0.004, mirror=True)
    for j, (x, y) in enumerate([(1.54, 1.755), (1.6, 1.715)]):   # nodes over the orbit
        S.sph(f"browKnob{j}", [x, y, 0.108], 0.025, "@knob", bone="head", k=0.008, kc=0.004, mirror=True)
    eye_at = [1.585, 1.665, 0.1]
    eyelids(S, eye_at, 0.027, col="@head")
    # ---- the arms: short; five small fingers
    S.cone("arm", sh, el, 0.055, 0.042, "@body", bone="armL", k=0.025, mirror=True, **sc)
    S.cone("fore", el, wr, 0.042, 0.032, "@body", bone="foreL", k=0.018, mirror=True, **sc)
    S.ell("palm", [1.05, 0.83, 0.25], [0.04, 0.025, 0.03], "@body", bone="foreL", k=0.01, mirror=True)
    for j, dz in enumerate([0.024, 0.008, -0.008, -0.022]):
        ln = [0.045, 0.06, 0.055, 0.035][j]
        S.cone(f"finger{j}", [1.07, 0.825, 0.25 + dz], [1.07 + ln * 0.6, 0.825 - ln * 0.8, 0.25 + dz * 1.3], 0.012, 0.009, "@claw" if False else "@body", bone="foreL", k=0.004, mirror=True)
    # ---- the legs: long and strong, the toes blunt-hoofed
    leg(S, H, hz, 0.58, s, slim=1.05, sc=sc, ankle=0.2, toes=(0.21, 0.16), toe_r=0.04, claw=0.06, hoof=True)
    eye = {"at": eye_at, "from": [1.5, 1.65, 0], "r": 0.027, "iris": "@eye", "pupil": "round", "lid": "@lid"}
    finish(d, S, 0.028, [10000, 3200], eye, {"back": 0.8, "belly": 1.1, "low": 0.96, "on": "@body"}, focus={"head": 5})
    floorR(S, ["claw", "spike"], 0.012)
    d["sculpt"]["shape"] = [fix_order(p) for p in S]
    save("dinosaurs/pachycephalosaurus", d)
    return len(S)

if __name__ == "__main__":
    print("pachycephalosaurus", pachycephalosaurus(), "shapes")
