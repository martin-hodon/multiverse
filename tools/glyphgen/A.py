from common import *
s = {}
def seated(arm_near, arm_far, extra_near=(), extra_far=(), head="head", torso="torso", kilt="kilt-seated", at=(0, 0), legs="legs-seated"):
    x, y = at
    out = [*extra_far, *arm_far,
           P(legs, at=[60 + x, 27 + y]), P(torso, at=[56.5 + x, 62 + y], scale=1.36)]
    if kilt: out.append(P(kilt, at=[60 + x, 27 + y]))
    out += [P(head, at=[56.6 + x, 61 + y], scale=.96), *arm_near, *extra_near]
    return out
HAND = lambda at, rot, sc=1: P("hand", at=at, rot=rot, scale=sc)
s["A1"] = sign("seated man", reading="(I, me: determinative of man)", freq=4, layers=seated(
  [L([[44, 56], [40, 44], [30, 55]], "skin", 7), HAND([30, 55], -48)],
  [L([[70, 56], [69, 40], [52, 37]], "skin", 7)]))
s["A2"] = sign("man with hand to mouth", reading="eat, speak, think (determinative)", freq=3, layers=seated(
  [L([[44, 56], [36, 44], [42, 76]], "skin", 7), HAND([42, 76], -110, .9)],
  [L([[70, 56], [69, 40], [52, 37]], "skin", 7)]))
s["A40"] = sign("seated god", reading="god, I (of a god)", freq=2, layers=[
  P("legs-seated", at=[60, 27]), P("torso", at=[56.5, 62], scale=1.36),
  S([[72, 62, C], [44, 62, C], [36, 40], [32, 12], [34, 2, C], [74, 2, C], [78, 26]], "cloth"),   # wrapped in a cloak from the shoulders down
  P("head-god", at=[56.6, 61], scale=.96)], colors={"wig": "blue", "cloth": "white"})
s["A17"] = sign("child, hand to mouth", reading="child, young (determinative)", freq=2, layers=[
  P("legs-seated", at=[60, 23], scale=[.86, .86]), P("torso", at=[57, 54], scale=1.15),
  P("face", at=[57, 53], scale=.86), {"shape": "spline", "points": [[2, 22], [6, 24], [8, 18], [6, 10], [4, 4], [3, 10], [2, 16]], "at": [57, 53], "scale": .86, "fill": "wig", "_about": "the sidelock of youth"},
  L([[46, 50], [38, 40], [44, 66]], "skin", 6), HAND([44, 66], -110, .8)])
s["A24"] = sign("man striking with a stick", reading="strike, force (determinative)", freq=2, layers=[
  L([[60, 76], [72, 82], [76, 96]], "skin", 6.6), P("fist", at=[76, 96], rot=-90),       # the far arm raised behind, with the stick
  L([[76, 98], [58, 100]], "wood", 3),
  P("legs-standing", at=[52, 50]), P("torso", at=[52, 81], scale=1.15), P("kilt", at=[52, 50]),
  P("head", at=[52, 80], scale=.74),
  L([[42, 76], [36, 62], [26, 60]], "skin", 6.6), P("fist", at=[25, 60], rot=0)])
s["A28"] = sign("man with both arms raised", reading="high, rejoice (determinative)", freq=2, layers=[
  P("legs-together", at=[50, 50]), P("torso", at=[50, 81], scale=1.15), P("kilt", at=[50, 50]),
  P("head", at=[50, 80], scale=.74),
  L([[38, 76], [26, 82], [22, 98]], "skin", 6.4), HAND([22, 98], -82, .8),
  L([[62, 76], [74, 82], [78, 98]], "skin", 6.4), HAND([78, 98], -98, .8)])
category("A", s)
s = {}
s["B1"] = sign("seated woman", reading="woman (determinative)", freq=3, colors={"skin": "skin-woman"}, layers=[
  P("legs-seated", at=[60, 27]),
  S([[66, 49, C], [46, 49, C], [37, 38], [30, 14], [29, 2, C], [74, 2, C], [76, 20]], "cloth"),   # the dress over the knees
  P("torso-woman", at=[56.5, 62], scale=1.36), P("head-woman", at=[56.6, 61], scale=.96)])
category("B", s)
s = {}
s["C1"] = sign("god with sun disc and uraeus (Ra)", reading="Ra", freq=1, colors={"wig": "blue", "cloth": "white", "sun": "red"}, layers=[
  P("legs-seated", at=[60, 27]), P("torso", at=[56.5, 62], scale=1.36),
  S([[72, 62, C], [44, 62, C], [36, 40], [32, 12], [34, 2, C], [74, 2, C], [78, 26]], "cloth"),
  P("head-god", at=[56.6, 61], scale=.96),
  {"shape": "circle", "r": 8.4, "at": [57.6, 94], "fill": "sun"},
  L([[50, 86], [48.4, 91], [50, 93]], "yellow", 2.2)])
s["C10"] = sign("goddess with feather (Maat)", reading="Maat", freq=1, colors={"skin": "skin-woman", "wig": "blue", "cloth": "white"}, layers=[
  P("legs-seated", at=[60, 27]),
  S([[66, 49, C], [46, 49, C], [37, 38], [30, 14], [29, 2, C], [74, 2, C], [76, 20]], "cloth"),
  P("torso-woman", at=[56.5, 62], scale=1.36), P("head-woman", at=[56.6, 61], scale=.96),
  P("feather", at=[60, 85], scale=.5)])
category("C", s)
