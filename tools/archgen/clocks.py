# CLOCKS (a style library, L2, shared by any generator; run it, or import it and call dial()): writes
#   components/clock-dial.json   a tower clock's DIAL, set on a wall face: the dial plate (a disc R across), the chapter
#                                ring proud of it, the twelve hour marks (bars) and the two hands, reading `hour`:`minute`.
# Origin at the dial's middle ON the wall's face; it faces +z (yaw it to the face it hangs on, one `at` entry per face).
# Colours by finish, by part name: <part>/dial, /ring, /marks, /hub, /hands (gilt marks and hands on a painted or copper plate),
# or by kind (the plate and ring are `screen`s, marks and hands `bars`). After Drachenburg's castle-tower clock screens.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = lambda rel, doc: open(os.path.join(ROOT, "assets/architecture", rel), "w").write(json.dumps(doc, indent=2) + "\n")
N = 24                                     # the disc's sides


def disc(r):
    return [[f"{r} * {round(math.sin(2 * math.pi * k / N), 4)}", f"{r} * {round(math.cos(2 * math.pi * k / N), 4)}"] for k in range(N)]


def dial():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    add("dial", {"type": "screen", "outline": disc("R"), "t": "t", "at": [[0, 0, "t", 0]],
                 "_about": "the dial plate, R in radius, its back on the wall's face"})
    add("ring", {"type": "screen", "outline": disc("R * 0.92"), "t": "t * 0.3", "at": [[0, 0, "t * 1.3", 0]], "standsOn": ["dial"],
                 "when": {"ring": "yes"}, "_about": "the chapter ring, standing proud of the plate"})
    marks = [[f"R * {round(0.66 * math.sin(a), 4)}", f"R * {round(0.66 * math.cos(a), 4)}", "t * 1.3 + mw / 2",
              f"R * {round(0.84 * math.sin(a), 4)}", f"R * {round(0.84 * math.cos(a), 4)}", "t * 1.3 + mw / 2"]
             for a in (2 * math.pi * k / 12 for k in range(12))]
    add("marks", {"type": "bars", "lines": marks, "w": "mw", "h": "mw", "caps": False, "kind": "marks", "at": [[0, 0, 0, 0]], "standsOn": ["ring"],
                  "when": {"marks": "yes"}, "_about": "the twelve hour marks, from 0.66 R to 0.84 R, lying on the ring"})
    add("hub", {"type": "screen", "outline": disc("R * 0.07"), "t": "mw * 2", "at": [[0, 0, "t * 1.3 + mw * 2", 0]], "standsOn": ["ring"],
                "_about": "the boss in the middle the hands turn on, from the ring's face"})
    # the hands, from a little behind the middle out: the hour hand 0.5 R, the minute hand 0.78 R; angles clockwise from 12
    ha = "((hour + minute / 60) * 0.5236)"
    ma = "(minute * 0.10472)"
    z = "t * 1.3 + mw * 1.5"
    hand = lambda a, L: ["0 - sin(" + a + ") * R * 0.12", "0 - cos(" + a + ") * R * 0.12", z, f"sin({a}) * R * {L}", f"cos({a}) * R * {L}", z]
    add("hands", {"type": "bars", "lines": [hand(ha, 0.5), hand(ma, 0.78)], "w": "hw", "h": "mw", "kind": "hands", "at": [[0, 0, 0, 0]], "standsOn": ["hub"],
                  "_about": "the hour and minute hands, reading hour:minute"})
    doc = {"name": "clock dial",
           "_about": "A TOWER CLOCK'S DIAL on a wall face: the plate (a disc R across, t thick, its back on the face), the chapter ring proud of it, the twelve hour marks on it and the two hands on their hub reading hour:minute. Origin at the dial's middle on the wall's face; it faces +z -- one `at` entry per face, yawed to it. Finish by name (dial, ring, marks, hub, hands) or kind (screen; marks, hands).",
           "params": {"detail": 4, "R": 1.0, "t": 0.1, "ring": "yes", "marks": "yes", "mw": "R * 0.05", "hw": "R * 0.07", "hour": 10, "minute": 9,
                      "_R": "the dial's radius; t the plate's thickness (the ring stands t * 0.3 proud of it)",
                      "_ring": "yes|no: the chapter ring; marks yes|no: the hour marks (mw their width and the hands' depth)",
                      "_hour": "the time the hands show (hour 0-12, minute 0-59); hw the hands' width"},
           "build": build, "parts": parts}
    OUT("components/clock-dial.json", doc)


if __name__ == "__main__":
    dial()
