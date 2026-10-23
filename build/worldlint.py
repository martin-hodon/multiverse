#!/usr/bin/env python3
"""THE PLACEMENT CHECK over many worlds (index.html lintPlaces, docs/world.md "Ground claimed"): each seed's world
loaded headless, one at a time, and every stretch of ground something was laid out on -- the green, the fire, the
kites, the swing, the leapfrog line, the sled run, the pasture, the spots by the river -- checked for walls and yards,
water, the land's edge, trees, props and each other -- and every building's own ground: no water over its floor, no
ground fallen away under it ("site <key>").

    python3 build/worldlint.py [SEED ...] [--random N]   # default: the worlds the cache keeps (pregen/), quickest to load

A world needs ~2 GB while it loads: before each the memory free is checked, and the run stops if there is not enough.
Needs chromium (CHROME to override) and the `websockets` Python module; three.js comes from unpkg.
"""
import argparse, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from headless import run_page, room, PROJECT

NEED = 2200   # MB free before a world loads (pregen.py's NEED["world"])
FLAGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=vulkan", "--window-size=640,400"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("seeds", nargs="*", type=int)
    ap.add_argument("--random", type=int, default=0, help="this many random seeds as well")
    ap.add_argument("--query", default="", help="more of index.html's query, e.g. period=medieval")
    a = ap.parse_args()
    seeds = list(a.seeds)
    if not seeds:
        try:
            seeds = sorted({e["seed"] for e in json.load(open(os.path.join(PROJECT, "pregen", "manifest.json"))).get("maps", {}).values()})
        except (OSError, ValueError):
            pass
    seeds += [random.randrange(1, 2 ** 31) for _ in range(a.random)]
    total = 0
    for i, seed in enumerate(seeds):
        room(NEED, f"seed {seed}", "python3 build/worldlint.py " + " ".join(map(str, seeds[i:])))
        q = f"index.html?probe=px&seed={seed}" + (f"&{a.query}" if a.query else "")
        r = json.loads(run_page(q, ready="window.__ready === true", result="JSON.stringify(window.__dbg.lintPlaces())", timeout=900, flags=FLAGS))
        total += len(r["bad"])
        print(f"seed {seed}: {len(r['claims'])} claims ({', '.join(r['claims'])}) -- {len(r['bad'])} problems", flush=True)
        for b in sorted(r["bad"], key=lambda b: -b["share"]):
            print(f"    {b['claim']:>10} at {b['at']}: {b['what']} ({b['share'] * 100:.0f}% of its ground)")
    print(f"{len(seeds)} worlds, {total} problems")


if __name__ == "__main__":
    main()
