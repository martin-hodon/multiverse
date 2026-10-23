from common import *
s = {}
s["D1"] = sign("head in profile", reading="tp: head", freq=2, layers=[P("face", at=[52, 10], scale=3.2), P("wig-short", at=[52, 10], scale=3.2)])
s["D2"] = sign("face", reading="Hr: face, upon", freq=3, layers=[
  S([[50, 92], [70, 88], [80, 70], [80, 46], [74, 26], [62, 12], [50, 8], [38, 12], [26, 26], [20, 46], [20, 70], [30, 88]], "skin"),
  {"shape": "ellipse", "rx": 6, "ry": 9, "at": [17, 56], "fill": "skin"}, {"shape": "ellipse", "rx": 6, "ry": 9, "at": [83, 56], "fill": "skin"},
  P("eye", at=[38, 60], scale=1.6, flip=True), P("eye", at=[62, 60], scale=1.6),
  line([31, 68], [44, 69], w=1.6), line([56, 69], [69, 68], w=1.6),
  S([[50, 60], [46, 40, C], [50, 37], [54, 40, C]], None, stroke="line", line=1.2, closed=False),
  {"shape": "lens", "r": 9, "w": 5, "at": [50, 26], "fill": "lips"}, line([41, 26], [59, 26], w=.8)],
  colors={"lips": "red-dark"})
s["D4"] = sign("eye", reading="ir: make, do", freq=4, layers=[
  S([[6, 46], [24, 62], [50, 68], [76, 60], [92, 48], [72, 40], [50, 36], [26, 38]], "eye"),
  {"shape": "circle", "r": 13, "at": [48, 52], "fill": "pupil"},
  S([[6, 46], [24, 62], [50, 68], [76, 60], [92, 48]], None, stroke="line", line=4, closed=False, cap="round"),
  line([92, 48], [98, 47], w=4, cap="round")], colors={"pupil": "black"})
s["D21"] = sign("mouth", reading="r", freq=8, layers=[
  {"shape": "lens", "r": 42, "w": 28, "at": [50, 30], "fill": "lips"}, line([12, 30], [88, 30], w=1.4)], colors={"lips": "red"})
s["D28"] = sign("two arms raised (ka)", reading="kA: soul, ka", freq=2, layers=[
  L([[30, 54], [26, 54], [26, 92]], "skin", 8), L([[70, 54], [74, 54], [74, 92]], "skin", 8),
  P("hand", at=[26, 92], rot=-90, scale=1.1), P("hand", at=[74, 92], rot=-90, scale=1.1),
  S([[22, 58, C], [78, 58, C], [78, 50, C], [22, 50, C]], "skin")])
s["D36"] = sign("forearm", reading="a", freq=8, layers=[
  L([[92, 30], [36, 30]], "skin", 13), P("hand", at=[36, 30], scale=2.4)])
s["D37"] = sign("forearm with conical loaf", reading="di, rdi: give", freq=4, layers=[
  L([[92, 30], [36, 30]], "skin", 13), P("hand", at=[36, 30], scale=2.4),
  {"shape": "points", "points": [[16, 38], [26, 38], [21, 78]], "fill": "bread"}])
s["D46"] = sign("hand", reading="d", freq=8, layers=[
  S([[90, 22], [84, 34], [62, 36], [30, 35], [14, 32], [8, 28], [12, 22], [32, 20], [62, 19], [84, 18]], "skin"),
  S([[62, 36], [56, 46], [48, 47], [50, 41], [52, 35]], "skin")])
s["D54"] = sign("legs walking", reading="motion (determinative)", freq=3, layers=[
  L([[52, 90], [36, 52], [22, 10]], "skin", 9), S([[24, 4, C], [6, 4, C], [7, 7], [15, 9], [24, 11]], "skin"),
  L([[52, 90], [66, 52], [74, 10]], "skin", 9), S([[78, 4, C], [62, 4, C], [63, 7], [70, 9], [78, 11]], "skin")])
s["D58"] = sign("foot", reading="b", freq=8, layers=[
  L([[78, 96], [76, 30]], "skin", 13),
  S([[84, 30], [86, 16], [84, 8, C], [16, 8, C], [16, 13], [36, 18], [62, 24], [70, 30]], "skin")])
s["D19"] = sign("nose, eye and cheek", reading="fnd: nose; smell (determinative)", freq=1, layers=[
  S([[30, 74], [26, 60], [16, 40, C], [24, 34], [30, 26], [64, 24], [80, 40], [82, 66], [70, 80]], "skin"), P("eye", at=[48, 62], scale=2.6)])
category("D", s)
s = {}
def beast(body, legs, head, tail, colors, extra=()):
    return list(extra) + [*tail, *[P(*l[0], **l[1]) for l in legs], body, *head]
s["E1"] = sign("bull", reading="kA: bull", freq=1, colors={"body": "red", "horn": "white", "hoof": "black"}, layers=[
  L([[86, 50], [92, 38], [90, 22]], "body", 2.4), S([[90, 24], [94, 14], [88, 14]], "black"),
  P("quadruped-leg", at=[78, 40], colors={}), P("quadruped-leg", at=[34, 40]),
  S([[24, 56], [40, 64], [70, 60], [86, 54], [86, 38], [74, 32], [40, 32], [26, 38]], "body"),
  P("quadruped-leg", at=[72, 40]), P("quadruped-leg", at=[28, 40]),
  S([[30, 60], [20, 64], [10, 56], [6, 46], [12, 42], [20, 46], [28, 48]], "body"),
  L([[20, 62], [26, 72], [34, 74]], "horn", 3.2), L([[18, 62], [12, 72], [6, 74]], "horn", 3.2),
  {"shape": "circle", "r": 1.6, "at": [16, 56], "fill": "black", "outline": False}])
s["E23"] = sign("recumbent lion", reading="rw, l", freq=5, colors={"body": "yellow", "mane": "yellow-dark"}, layers=[
  L([[88, 26], [96, 36], [94, 50], [86, 52]], "body", 3), S([[87, 49], [84, 57], [90, 56]], "mane"),
  S([[26, 32], [44, 38], [64, 38], [82, 34], [92, 24], [92, 8, C], [28, 8, C], [22, 18]], "body"),
  S([[8, 12, C], [32, 12, C], [32, 8, C], [6, 8, C]], "body"),
  S([[22, 24], [24, 44], [34, 48], [42, 40], [42, 24], [34, 16]], "mane"),
  S([[12, 30], [11, 40], [16, 46], [24, 46], [29, 40], [28, 30], [22, 25]], "body"),
  {"shape": "circle", "r": 1.4, "at": [16, 39], "fill": "black", "outline": False}])
s["E34"] = sign("hare", reading="wn", freq=4, colors={"body": "yellow-dark"}, layers=[
  S([[30, 46], [50, 50], [72, 46], [88, 36], [92, 22], [86, 12], [70, 10, C], [26, 10, C], [22, 22]], "body"),
  S([[34, 44], [18, 70], [8, 76], [12, 66], [26, 46]], "body"), S([[40, 44], [34, 72], [26, 80], [28, 68], [32, 46]], "body"),
  S([[30, 44], [16, 42], [8, 34], [12, 26], [26, 28], [32, 34]], "body"),
  {"shape": "circle", "r": 1.6, "at": [18, 36], "fill": "black", "outline": False},
  S([[86, 30], [96, 34], [94, 26]], "white")])
category("E", s)
s = {}
s["F13"] = sign("horns", reading="wp: open, divide", freq=1, colors={"horn": "white"}, layers=[
  S([[50, 26], [36, 30], [20, 46], [12, 70], [14, 76], [20, 66], [30, 46], [44, 36], [56, 36], [70, 46], [80, 66], [86, 76], [88, 70], [80, 46], [64, 30]], "horn"),
  S([[40, 30, C], [60, 30, C], [56, 20], [44, 20]], "body")], **{})
s["F13"]["colors"]["body"] = "red"
s["F31"] = sign("three fox skins tied together", reading="ms: birth", freq=3, colors={"skin": "yellow-dark", "tie": "red"}, layers=[
  *[S([[x - 5, 70], [x + 5, 70], [x + 6, 52], [x + 8, 40], [x + 6, 10], [x, 4], [x - 6, 10], [x - 8, 40], [x - 6, 52]], "skin") for x in (32, 50, 68)],
  *[line([x - 4, y], [x + 4, y - 3], w=1) for x in (32, 50, 68) for y in (46, 36, 26)],
  {"shape": "rect", "w": 46, "h": 6, "at": [50, 72], "fill": "tie"},
  {"shape": "circle", "r": 6, "at": [50, 86], "fill": "tie"}])
s["F34"] = sign("heart", reading="ib: heart", freq=2, colors={"heart": "red"}, layers=[
  S([[36, 76], [30, 60], [32, 38], [42, 16], [50, 10], [58, 16], [68, 38], [70, 60], [64, 76]], "heart"),
  {"shape": "rect", "w": 26, "h": 6, "at": [50, 80], "fill": "heart"}, L([[40, 84], [36, 92]], "heart", 3), L([[60, 84], [64, 92]], "heart", 3)])
s["F35"] = sign("heart and windpipe", reading="nfr: good, beautiful", freq=4, colors={"heart": "red", "pipe": "black"}, layers=[
  L([[50, 34], [50, 96]], "pipe", 3), line([42, 88], [58, 88], w=3), line([44, 80], [56, 80], w=3),
  S([[38, 42], [36, 26], [42, 12], [50, 6], [58, 12], [64, 26], [62, 42], [50, 46]], "heart")])
s["F32"] = sign("animal's belly with teats and tail", reading="X (kh)", freq=6, colors={"hide": "yellow-dark", "teat": "red"}, layers=[
  L([[88, 30], [96, 22], [96, 10]], "hide", 3),
  *[L([[x, 24], [x, 16]], "teat", 3) for x in (34, 44, 54)],
  S([[6, 30], [16, 36], [50, 38], [80, 36], [92, 30], [86, 24], [50, 22], [16, 24]], "hide")])
category("F", s)
