import sys
from PIL import Image, ImageChops
out, ims = sys.argv[1], sys.argv[2:]
crops = []
for p in ims:
    im = Image.open(p).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
    d = ImageChops.difference(im, bg).convert("L").point(lambda x: 255 if x > 40 else 0)
    b = d.getbbox() or (0, 0, im.width, im.height)
    pad = 10
    b = (max(0, b[0]-pad), max(0, b[1]-pad), min(im.width, b[2]+pad), min(im.height, b[3]+pad))
    crops.append(im.crop(b))
H = max(c.height for c in crops)
W = sum(c.width for c in crops)
sh = Image.new("RGB", (W, H), (42, 47, 54))
x = 0
for c in crops: sh.paste(c, (x, 0)); x += c.width
if sh.width > 1800: sh = sh.resize((1800, int(sh.height*1800/sh.width)))
sh.save(out)
