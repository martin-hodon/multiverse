import re, json, sys
from PIL import Image, ImageDraw
def load(name):
    P = {}
    for l in open(f"s_{name}.log"):
        if "[log] P " in l:
            for tok in l.split("[log] P ")[1].split():
                j, v = tok.split(":")
                if v != "-": P[int(j)] = tuple(map(float, v.split(",")))
    return P
xs = json.load(open("samp_x.json"))
out = {}
for name in ("plains", "grevy"):
    P = load(name); im = Image.open(f"s_{name}/neck.png").convert("RGB"); W, H = im.size
    dr = ImageDraw.Draw(im); res = {}
    for j, (px, py) in P.items():
        if not (2 <= px < W - 2 and 2 <= py < H - 2): continue
        L = [sum(im.getpixel((int(px) + a, int(py) + b))) / 3 for a in (-1, 0, 1) for b in (-1, 0, 1)]
        res[j] = sum(L) / len(L)
    for j, (px, py) in P.items():
        if j in res: dr.point((px, py), fill=(255, 0, 0)); dr.ellipse((px - 1.5, py - 1.5, px + 1.5, py + 1.5), outline=(255, 0, 0))
    im.save(f"mark_{name}.png")
    out[name] = res
    print(name, "in frame", len(res), "of", len(P), "x range", min(xs[j] for j in res), max(xs[j] for j in res))
    print("".join("#" if res.get(j, 999) < 140 else ("." if j in res else " ") for j in range(len(xs))))
json.dump(out, open("lum.json", "w"))
