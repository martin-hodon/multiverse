#!/usr/bin/env python3
"""THE MINE (2026-10-03; 2026-11-03: made by mine.js for any ground). The definition is no longer written here: mine.js
mineDoc makes it -- the game lays it into the world's hills (only the shaft head on a small flat spot, the galleries
underground with their rock over them, stepping down where the land falls away) -- and tools/archgen/mine.mjs writes the
catalogue's copy on level ground (assets/architecture/village/mine.json), the cart and the finishes mine-<ore>.

    python3 tools/archgen/mine.py        (runs: node tools/archgen/mine.mjs)
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.exit(subprocess.run(["node", os.path.join(HERE, "mine.mjs")]).returncode)
