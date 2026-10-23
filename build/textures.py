#!/usr/bin/env python3
"""Save the calculated pattern tiles as PNG files into texture/ -- a way to
LOOK at them (the game never loads these files: textures.js bakes the tiles
at startup from the same maths every time).

It serves the project over a local HTTP server, opens textures.html in
headless Chromium over the DevTools protocol, and writes for every tile
  texture/<name>.png          the stored channels (R brightness / 1.5, G accent, B dark figure)
  texture/<name>_preview.png  the tile applied to a sample stone and accent colour

Needs chromium (CHROME env to override the binary) and the `websockets`
Python module (build/headless.py); three.js comes from unpkg like the dev pages.

    python3 build/textures.py
"""
import base64, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from headless import run_page, PROJECT   # (the server and the headless browser: shared with build/pregen.py)
OUT = os.path.join(PROJECT, "texture")


def main():
    tiles = json.loads(run_page("textures.html", ready="window.__ready === true", result="JSON.stringify(window.__textures())",
                                # the page bakes the tiles on WebGPU now: swiftshader's GL read back black
                                flags=["--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=vulkan"]))
    os.makedirs(OUT, exist_ok=True)
    for t in tiles:
        for key, suffix in (("raw", ""), ("preview", "_preview")):
            path = os.path.join(OUT, f"{t['name']}{suffix}.png")
            with open(path, "wb") as f:
                f.write(base64.b64decode(t[key].split(",", 1)[1]))
    print(f"wrote {2 * len(tiles)} files to {os.path.relpath(OUT)}/: " + ", ".join(t["name"] for t in tiles))


if __name__ == "__main__":
    main()
