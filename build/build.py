#!/usr/bin/env python3
"""
Bannerfield distribution build.

index.html (the 3D root) is the single source of truth: markup, CSS, an
import map pointing at unpkg for three.js, and one inline module script
that imports the local modules (species, engines, architecture, flora,
people, rtc). For development you serve the directory and get real files
in devtools.

This script derives dist/bannerfield.html: one file with all the code
bundled and minified -- three.js and OrbitControls are downloaded into
build/vendor/ and inlined. The assets are still fetched at run time, relative
to the page: serve it from this directory, beside assets/ and pregen/.

esbuild here is old (0.12, no --alias), so instead of aliasing the bare
"three" specifier we copy all sources into build/_tmp/ with their import
specifiers rewritten to relative vendor paths, then run
`esbuild --bundle --minify --format=esm` over the rewritten entry.

Setup (once):  pip install -r build/requirements.txt
Run:           python3 build/build.py
"""
import io
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUT = ROOT / "dist" / "bannerfield.html"
VENDOR = ROOT / "build" / "vendor"
TMP = ROOT / "build" / "_tmp"

THREE_VER = "0.185.1"
VENDORS = {
    # the WEBGPU build (the world's shaders are WGSL: docs/webgpu.md) and the TSL entry point beside it
    "vendor_three.js": f"https://unpkg.com/three@{THREE_VER}/build/three.webgpu.js",
    "three.core.js": f"https://unpkg.com/three@{THREE_VER}/build/three.core.js",   # relative import inside three.webgpu.js
    "vendor_tsl.js": f"https://unpkg.com/three@{THREE_VER}/build/three.tsl.js",
    "vendor_orbit.js": f"https://unpkg.com/three@{THREE_VER}/examples/jsm/controls/OrbitControls.js",
    "vendor_bgu.js": f"https://unpkg.com/three@{THREE_VER}/examples/jsm/utils/BufferGeometryUtils.js",
}
# the bare specifiers the sources use -> the vendored file (the longest first: "three/tsl" before "three")
SPECIFIERS = {"three/addons/controls/OrbitControls.js": "vendor_orbit.js", "three/addons/utils/BufferGeometryUtils.js": "vendor_bgu.js",
              "three/tsl": "vendor_tsl.js", "three/webgpu": "vendor_three.js", "three": "vendor_three.js"}


def fetch_vendors():
    # each vendored file is fetched again when the URL it should come from changes (vendor/sources.json records where
    # each one came from): a file kept under the same name from an older list -- the WebGL build where the WebGPU one
    # is wanted -- would otherwise be bundled for ever
    import json
    VENDOR.mkdir(parents=True, exist_ok=True)
    stamp = VENDOR / "sources.json"
    had = json.loads(stamp.read_text()) if stamp.exists() else {}
    for name, url in VENDORS.items():
        dst = VENDOR / name
        if dst.exists() and had.get(name) == url:
            continue
        print(f"fetching {url}")
        with urllib.request.urlopen(url, timeout=60) as r:
            dst.write_bytes(r.read())
        had[name] = url
        stamp.write_text(json.dumps(had, indent=1))


def rewrite_specifiers(js, up="./"):
    # static imports (from "three") and dynamic ones (await import("three")) alike; `up`: the way back to the staging
    # root from the file's own folder ("../" for arch/*.js)
    pat = "|".join(re.escape(k) for k in SPECIFIERS)
    return re.sub(r"(from\s*|import\(\s*)([\"'])(" + pat + r")\2", lambda m: f'{m.group(1)}"{up}{SPECIFIERS[m.group(3)]}"', js)


# the pip esbuild wrapper ships a 2021 binary that cannot parse modern
# three.js (class static blocks), so fetch a current official binary once
ESBUILD_VER = "0.21.5"

def esbuild_bin():
    binp = VENDOR / "esbuild"
    if binp.exists():
        return binp
    arch = {"x86_64": "x64", "aarch64": "arm64", "arm64": "arm64"}[platform.machine()]
    osname = {"linux": "linux", "darwin": "darwin"}[sys.platform[:6].rstrip("0123456789")]
    url = f"https://registry.npmjs.org/@esbuild/{osname}-{arch}/-/{osname}-{arch}-{ESBUILD_VER}.tgz"
    print(f"fetching {url}")
    data = urllib.request.urlopen(url, timeout=120).read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        binp.write_bytes(tf.extractfile("package/bin/esbuild").read())
    binp.chmod(0o755)
    return binp


def esbuild(args, stdin=None):
    p = subprocess.run([str(esbuild_bin()), *args], input=stdin, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"esbuild failed:\n{p.stderr}")
    if p.stderr.strip():
        print(p.stderr, file=sys.stderr)
    return p.stdout


def esbuild_stdin(text, loader):
    return esbuild([f"--loader={loader}", "--minify"], stdin=text)


def clean_markup(text):
    no_comments = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return "\n".join(line.strip() for line in no_comments.split("\n") if line.strip())


def build():
    html = INDEX.read_text(encoding="utf-8")

    style_m = re.search(r"<style>(.*?)</style>", html, re.S)
    if not style_m:
        sys.exit("index.html: no <style> block")
    css_min = esbuild_stdin(style_m.group(1), "css").strip()

    module_m = re.search(r'<script type="module">(.*?)</script>', html, re.S)
    if not module_m:
        sys.exit("index.html: no inline module script")
    importmap_m = re.search(r'<script type="importmap">.*?</script>', html, re.S)
    if not importmap_m:
        sys.exit("index.html: no importmap")

    # stage rewritten sources + vendors in a flat temp dir so relative
    # imports keep working after the specifier rewrite
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    for src in ROOT.glob("*.js"):
        (TMP / src.name).write_text(rewrite_specifiers(src.read_text(encoding="utf-8")), encoding="utf-8")
    shutil.copytree(ROOT / "assets", TMP / "assets")   # (the definitions the modules import as JSON: esbuild inlines them)
    for src in ROOT.glob("arch/*.js"):   # (the architecture engine's own folder, its relative imports kept)
        (TMP / "arch").mkdir(exist_ok=True)
        (TMP / "arch" / src.name).write_text(rewrite_specifiers(src.read_text(encoding="utf-8"), "../"), encoding="utf-8")
    for src in ROOT.glob("*.json"):   # config.json: bundled into dist (esbuild inlines JSON imports)
        shutil.copy(src, TMP / src.name)
    for name in VENDORS:
        (TMP / name).write_text(rewrite_specifiers((VENDOR / name).read_text(encoding="utf-8")), encoding="utf-8")
    (TMP / "_entry.js").write_text(rewrite_specifiers(module_m.group(1)), encoding="utf-8")

    # an ES MODULE, not an iife: the game waits at the top level (`await` for its catalogue, its terrain, its pregen),
    # which only a module can do -- and a module script is what the page had anyway
    js_min = esbuild([str(TMP / "_entry.js"), "--bundle", "--minify", "--format=esm", "--target=esnext", "--log-limit=0"])
    shutil.rmtree(TMP)

    # markup: strip the importmap, swap the module script for the bundle
    head = html[: style_m.start()]
    mid = html[style_m.end() : module_m.start()].replace(importmap_m.group(0), "")
    tail = html[module_m.end() :]
    return (f"{clean_markup(head)}\n<style>{css_min}</style>\n{clean_markup(mid)}\n"
            f"<script type=\"module\">{js_min}</script>\n{clean_markup(tail)}\n")


def main():
    fetch_vendors()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    src_bytes = sum(f.stat().st_size for f in ROOT.glob("*.js")) + INDEX.stat().st_size
    print(f"built {OUT.relative_to(ROOT)}: {src_bytes:,} bytes of our source "
          f"(+ three.js) -> {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
