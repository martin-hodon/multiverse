#!/usr/bin/env python3
"""Pregenerate what the game would otherwise compute at startup, into pregen/ (docs/pregen.md).

Opens pregen.html in headless Chromium, ONE PART AT A TIME (a few landmarks, the towns' tiles, the items, the wings,
the faces, the fabrics -- each in a browser of its own): it builds them through the game's own code and POSTs what it
made -- pattern tiles and fabric layers as PNG, finished building geometry and wall fields as gzipped binaries, and
its part of the manifest, merged here into pregen/manifest.json. Then it opens the game itself to record WORLDS: their
lands, towns and whatever else they make. The game (pregen.js) fetches the entries its world needs; every entry is
filed under a hash of what made it, so after an edit to a building, a finish, a pattern or the code that makes them,
run this again -- until then the game simply builds those from scratch, as it always did.

    python3 build/pregen.py              # all of it: the parts, then the worlds
    python3 build/pregen.py --resume     # carry on a run that stopped (its finished parts are kept in pregen.new/)
    python3 build/pregen.py --worlds-only [--worlds N]   # only record worlds, into the cache as it is

Before each browser it checks the memory free (a part needs ~NEED["part"] MB, a world ~NEED["world"]) and stops,
saying so, if there is not enough -- free some and run it again with --resume (or --worlds-only).
Needs chromium (CHROME to override) and the `websockets` Python module; three.js comes from unpkg.
"""
import argparse, datetime, json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from headless import run_page, room, PROJECT

OUT = os.path.join(PROJECT, "pregen")
NEW = OUT + ".new"                        # written aside, then swapped in: a failed run leaves the old cache alone


def write(path, body):
    full = os.path.normpath(os.path.join(NEW, path))
    if not full.startswith(NEW + os.sep):
        raise ValueError(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(body)


def write_live(path, body):   # (the second pass writes into the cache in place: only new files, and fragments)
    full = os.path.normpath(os.path.join(OUT, path))
    if not full.startswith(OUT + os.sep):
        raise ValueError(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(body)


def merge_fragments():
    fdir = os.path.join(OUT, "fragments")
    if not os.path.isdir(fdir):
        return
    mpath = os.path.join(OUT, "manifest.json")
    man = json.load(open(mpath))
    world = man["buildings"].setdefault("world", {"groups": {}, "walls": {}, "tiles": []})
    added = {"tiles": 0, "wings": 0, "faces": 0, "maps": 0, "towns": 0}
    for name in sorted(os.listdir(fdir)):
        frag = json.load(open(os.path.join(fdir, name)))
        for name2, e in frag.get("buildings", {}).items():
            man["buildings"][name2] = {"groups": e["groups"], "walls": e["walls"], "tiles": e["tiles"]}; added["towns"] += 1
        for kind in ("tiles", "wings", "faces", "maps"):
            for k, v in frag.get(kind, {}).items():
                if k not in man.setdefault(kind, {}):
                    man[kind][k] = v; added[kind] += 1
        world["tiles"] = sorted(set(world["tiles"]) | {k for k in frag.get("used", []) if k in man["tiles"]})
        os.remove(os.path.join(fdir, name))
    os.rmdir(fdir)
    # (a town's tiles are listed by key: keep those the manifest has)
    for name2, b in man["buildings"].items():
        if name2.startswith("world/"): b["tiles"] = [k for k in b["tiles"] if k in man["tiles"]]
    json.dump(man, open(mpath, "w"), indent=1)
    print(f"worlds merged: +{added['tiles']} tiles, +{added['wings']} wings, +{added['faces']} faces, +{added['maps']} lands, +{added['towns']} towns; {len(world['tiles'])} tiles a world uses")


# the memory a browser needs free before it starts, MB: the peaks measured (this PC, 2026-10-23: a part 0.5-1.2 GB, the
# items' the most; a world 1.9 GB at 640x400, its land fetched) and a margin, so the rest of the machine is not squeezed
NEED = {"part": 1500, "world": 2200}


def merge_parts():
    """The parts' manifests (pregen.new/parts/*.json) into one, pregen.new/manifest.json."""
    man = {"made": datetime.datetime.now(datetime.timezone.utc).isoformat(), "sections": None,
           "tiles": {}, "fabrics": {}, "buildings": {}, "wings": {}, "faces": {}, "maps": {}}
    pdir = os.path.join(NEW, "parts")
    for name in sorted(os.listdir(pdir)):
        part = json.load(open(os.path.join(pdir, name)))
        if man["sections"] is None:
            man["sections"] = part["sections"]
        elif part["sections"] != man["sections"]:
            sys.exit(f"pregen.new/parts/{name} was made by other code than the parts before it -- run without --resume")
        for kind in ("tiles", "fabrics", "wings", "faces", "buildings"):
            man[kind].update(part[kind])
    # THE LANDS: growing one is the slowest thing a world does, and the parts make none -- the old cache's are kept
    # when the code that grows them is the same (their seeds are recorded again below, with the towns of today's code)
    try:
        old = json.load(open(os.path.join(OUT, "manifest.json")))
    except (OSError, ValueError):
        old = {}
    if old.get("sections", {}).get("maps") == man["sections"].get("maps"):
        for k, e in old.get("maps", {}).items():
            src = os.path.join(OUT, e["file"])
            if os.path.exists(src):
                write(e["file"], open(src, "rb").read()); man["maps"][k] = e
    json.dump(man, open(os.path.join(NEW, "manifest.json"), "w"), indent=1)
    return man


def first_pass(resume):
    if not resume:
        shutil.rmtree(NEW, ignore_errors=True)
    os.makedirs(os.path.join(NEW, "parts"), exist_ok=True)
    parts = json.loads(run_page("pregen.html?part=list", ready="!!window.__pregenDone", result="JSON.stringify(window.__pregenDone)", timeout=300))["parts"]
    t0 = time.time()
    for part in parts:
        if os.path.exists(os.path.join(NEW, "parts", part + ".json")):
            print(f"{part}: kept from before"); continue
        room(NEED["part"], "part " + part, "python3 build/pregen.py --resume")
        stats = {}
        done = json.loads(run_page(f"pregen.html?part={part}", ready="!!window.__pregenDone", result="JSON.stringify(window.__pregenDone)",
                                   writes={"pregen/": write}, timeout=1800, log=True, stats=stats))
        if done.get("error"):
            sys.exit(f"pregen.html?part={part} failed (pregen.new/ kept: fix it and run with --resume): " + done["error"])
        print(f"{part}: {done} -- browser peak {stats['peak_mb']} MB", flush=True)
    man = merge_parts()
    shutil.rmtree(OUT, ignore_errors=True)
    os.rename(NEW, OUT)
    print(f"pregen/: {len(man['buildings'])} entries, {len(man['tiles'])} tiles, {len(man['fabrics'])} fabrics, {len(man['wings'])} butterflies' wings, "
          f"{len(man['faces'])} faces, {len(man['maps'])} lands kept -- parts made in {time.time() - t0:.0f}s")


def worlds(n):
    """THE SECOND PASS: worlds recorded (pregen.js RECORD_WORLD) -- each writes what it had to make into pregen/ and a
    fragment saying so, merged into the manifest at once. The lands the cache keeps whose towns it has not got are
    recorded first (the same worlds, built by today's code), then new ones until it keeps n."""
    for i in range(n):
        man = json.load(open(os.path.join(OUT, "manifest.json")))
        seeds = sorted({e["seed"] for e in man.get("maps", {}).values()})
        todo = [s for s in seeds if f"world/{s}" not in man["buildings"]]
        if not todo and len(seeds) >= n:
            break
        room(NEED["world"], f"world {i + 1}", f"python3 build/pregen.py --worlds-only --worlds {n}")
        stats = {}
        q = f"&seed={todo[0]}" if todo else ""
        r = json.loads(run_page(f"index.html?pregenrecord=1{q}", ready="!!window.__pregenWorldDone", result="JSON.stringify(window.__pregenWorldDone)",
                                writes={"pregen/": write_live}, timeout=900, log=False, stats=stats,
                                flags=["--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=vulkan", "--window-size=640,400"]))
        print(f"world {i + 1}{' (seed ' + str(todo[0]) + ')' if todo else ''}: {r} -- browser peak {stats['peak_mb']} MB", flush=True)
        merge_fragments()


def main():
    ap = argparse.ArgumentParser(description="Pregenerate the startup cache, pregen/ (docs/pregen.md).")
    ap.add_argument("--resume", action="store_true", help="carry on a run that stopped: keep pregen.new/ and the parts it has")
    ap.add_argument("--worlds-only", action="store_true", help="only record worlds, into pregen/ as it is")
    ap.add_argument("--worlds", type=int, default=int(os.environ.get("WORLDS", "4")), help="worlds the cache keeps (default 4)")
    a = ap.parse_args()
    if not a.worlds_only:
        first_pass(a.resume)
    worlds(a.worlds)


if __name__ == "__main__":
    main()
