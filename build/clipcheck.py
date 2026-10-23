#!/usr/bin/env python3
"""The cloth clipping check (clipcheck.html, docs/clothes.md): every limb that comes through a hanging garment, for
people of every style and kind in every pose and motion, worst first.

    python3 build/clipcheck.py [QUERY]     # e.g. "n=8&tol=.02&top=100"

Needs chromium (CHROME to override) and the `websockets` Python module; three.js comes from unpkg.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from headless import run_page

q = sys.argv[1] if len(sys.argv) > 1 else ""
r = json.loads(run_page("clipcheck.html" + ("?" + q if q else ""), ready="!!window.__clipDone", result="JSON.stringify(window.__clipDone)", timeout=900, log=True))
if r.get("error"):
    sys.exit(r["error"])
