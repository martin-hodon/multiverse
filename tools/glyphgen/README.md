# glyphgen -- the first hieroglyph set (2026-10-05)

These scripts wrote assets/glyphs/*.json (docs/glyphs.md): `parts.py` the parts, `A.py` (A, B, C), `D.py` (D, E, F),
`G.py` (birds), `rest.py` (H ... Aa); `common.py` the helpers (S spline, L limb, P part, sign, category -- the Unicode
code point looked up by Gardiner code), `jdump.py` a compact JSON writer (point lists on one line).

The JSON is the source of truth now -- edit it in the asset viewer; run a script again only on purpose (it rewrites
its files whole). Run from this folder: `python3 parts.py && python3 A.py && python3 D.py && python3 G.py && python3 rest.py`.
