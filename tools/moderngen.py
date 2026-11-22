#!/usr/bin/env python3
"""THE MODERN AGE (2026-11-20; docs/modern.md): writes the modern items -- the shared components, the vehicles, the
street, the furniture and the electronics, the arms, the machines -- from the generators in tools/modern/ (each a
module with GROUPS {group: catalogue title} and write_all()), and lists them in the catalogue (assets/index.json, the
"Modern: ..." categories).

    python3 tools/moderngen.py              every generator
    python3 tools/moderngen.py rail air     only those modules (tools/modern/rail.py, air.py)
"""
import importlib, os, sys
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modern")
sys.path.insert(0, HERE)
import kit

NOT = {"kit", "mshot", "clothesgen"}   # (clothesgen writes garments, not items: run it on its own)
mods = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(HERE) if f.endswith(".py") and f[:-3] not in NOT)
groups = {}
for name in mods:
    m = importlib.import_module(name)
    m.write_all()
    groups.update(getattr(m, "GROUPS", {}))
kit.catalogue(groups)
print({g: len(v) for g, v in kit.WRITTEN.items()})
