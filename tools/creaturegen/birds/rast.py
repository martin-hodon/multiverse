# python3 rast.py in.bin out.png cx,cy,cz dist view [size] -- software z-buffer of a dumped mesh (root space: x fwd, y up, z left)
import sys, struct, numpy as np
from PIL import Image
b = open(sys.argv[1], 'rb').read(); n, t = struct.unpack('<ii', b[:8]); o = 8
P = np.frombuffer(b, '<f4', n * 3, o).reshape(n, 3); o += n * 12
N = np.frombuffer(b, '<f4', n * 3, o).reshape(n, 3); o += n * 12
C = np.frombuffer(b, '<f4', n * 3, o).reshape(n, 3); o += n * 12
I = np.frombuffer(b, '<i4', t * 3, o).reshape(t, 3)
cen = np.array([float(v) for v in sys.argv[3].split(',')]); dist = float(sys.argv[4]); view = sys.argv[5]; S = int(sys.argv[6]) if len(sys.argv) > 6 else 700
dirs = {'front': [1, 0, 0], 'q': [.7, .25, .65], 'low': [.8, -.35, .45], 'side': [0, .05, 1], 'back': [-1, .2, 0], 'top': [.3, 1, .1], 'qr': [.7, .25, -.65]}
f = np.array(dirs[view], float); f /= np.linalg.norm(f)          # camera sits at cen + f*dist, looks at cen
up = np.array([0, 1, 0.]); r = np.cross(up, f); r /= np.linalg.norm(r); u = np.cross(f, r)
Q = P - cen; x = Q @ r; y = Q @ u; z = Q @ f                       # z: toward camera
half = dist * .5
sx = ((x / half) * .5 + .5) * S; sy = (.5 - (y / half) * .5) * S
L = np.array([.4, .8, .5]); L /= np.linalg.norm(L)
Nn = N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-9)
lin = np.clip(C, 0, 1) ** (1 / 2.2)
Zb = np.full((S, S), -1e9); img = np.zeros((S, S, 3)) + [.16, .18, .22]
for a, bb, c in I:
    xs = sx[[a, bb, c]]; ys = sy[[a, bb, c]]
    x0, x1 = int(max(0, np.floor(xs.min()))), int(min(S - 1, np.ceil(xs.max()))); y0, y1 = int(max(0, np.floor(ys.min()))), int(min(S - 1, np.ceil(ys.max())))
    if x0 > x1 or y0 > y1: continue
    d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
    if abs(d) < 1e-12: continue
    gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
    w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
    w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
    w2 = 1 - w0 - w1
    m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
    if not m.any(): continue
    zz = w0 * z[a] + w1 * z[bb] + w2 * z[c]
    sub = Zb[y0:y1 + 1, x0:x1 + 1]; m &= zz > sub
    if not m.any(): continue
    nn = w0[..., None] * Nn[a] + w1[..., None] * Nn[bb] + w2[..., None] * Nn[c]
    nn /= np.linalg.norm(nn, axis=-1, keepdims=True) + 1e-9
    if nn[m].mean(0) @ f < 0: nn = -nn
    cc = w0[..., None] * lin[a] + w1[..., None] * lin[bb] + w2[..., None] * lin[c]
    sh = .35 + .75 * np.clip(nn @ L, 0, 1) + .25 * np.clip(nn @ f, 0, 1) ** 8
    sub[m] = zz[m]; img[y0:y1 + 1, x0:x1 + 1][m] = np.clip(cc * sh[..., None], 0, 1)[m]
Image.fromarray((img * 255).astype(np.uint8)).save(sys.argv[2])
