"""Assemble every building headless and print what archcheck.html finds: stairs that do not lead from a floor to a
floor (foot, approach, headroom, inside, arrival), parts not carried to the ground, and each building's triangles.

    python3 build/archcheck.py [only=florence,notre] [cat=Architecture] [detail=4] [mesh=1] [finish=1] [--all]

Without --all only the buildings with findings are listed in detail; the totals line is always printed.
"""
import json, sys
from headless import run_page

args = [a for a in sys.argv[1:] if "=" in a]
q = "&".join(args)
rows = json.loads(run_page("archcheck.html" + ("?" + q if q else ""), ready="!!window.__archcheck",
                           result="JSON.stringify(window.__archcheck)", timeout=1800))
bad = 0
for r in rows:
    if "error" in r:
        bad += 1; print(f"{r['path']}: ERROR {r['error']}"); continue
    found = r["stairs"] + r["floats"] + r["mesh"] + r.get("mixed", [])
    if found: bad += 1
    if found or "--all" in sys.argv:
        print(f"{r['path']}: {r['parts']} parts, {r['tris']} tris, {r['verts']} verts, {r['ms']} ms")
        for f in r["stairs"]: print(f"   stair {f['kind']:<13} {f['stair']} @{f['at']} {f['by']}")
        for f in r["floats"]: print(f"   support {f['kind']:<11} {f['part']}#{f['inst']} @{f['at']} gap {f['gap']}" + (f" waits for {f['by']}" if f.get('by') else ""))
        for f in r["mesh"]: print(f"   mesh    {f['part']}: open {f['open']} twice {f['twice']} vol {f['vol']} @{f['at']}")
        for f in r.get("mixed", []): print(f"   finish  {f['part']}#{f['inst']} {f['total']}m2 minor {f['minor']} {'cut' if f['cuts'] else 'PATCHY'} {f['by']} {f.get('at', '')}")
ok = [r for r in rows if "error" not in r]
print(f"{len(rows)} buildings, {bad} with findings, {sum(r['tris'] for r in ok)} triangles, {sum(r['verts'] for r in ok)} vertices")
