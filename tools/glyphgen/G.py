from common import *
s = {}
def bird(head, colors, freq=2, name="", reading=None, legs=True, head_at=(32, 64), head_scale=1, body_scale=None, extra=(), wing="bird-wing", pre=()):
    lay = list(pre)
    if legs: lay.append(P("bird-legs"))
    lay += [P("bird-body"), P(wing), P(head, at=list(head_at), scale=head_scale), *extra]
    if body_scale: lay = [{"layers": lay, "at": body_scale[0], "scale": body_scale[1]}]
    return sign(name, reading=reading, freq=freq, colors=colors, layers=lay)
s["G1"] = bird("head-vulture", {"plumage": "yellow", "wing": "green", "tips": "blue", "legs": "red", "breast": "white"}, 8, "Egyptian vulture", "A (aleph)")
s["G5"] = bird("head-falcon", {"plumage": "blue", "breast": "white", "wing": "green", "tips": "blue-dark", "legs": "yellow"}, 4, "falcon", "Hr: Horus")
s["G7"] = sign("falcon on a standard", reading="god (determinative)", freq=2, colors={"plumage": "blue", "breast": "white", "wing": "green", "tips": "blue-dark", "legs": "yellow", "perch": "red"}, layers=[
  {"shape": "rect", "w": 66, "h": 6, "at": [56, 24], "fill": "perch"}, L([[56, 21], [56, 2]], "perch", 5), L([[40, 6], [72, 6]], "perch", 3),
  {"layers": [P("bird-legs"), P("bird-body"), P("bird-wing"), P("head-falcon", at=[32, 64])], "at": [14, 24], "scale": .76}])
s["G14"] = bird("head-vulture", {"plumage": "white", "wing": "blue", "tips": "blue-dark", "legs": "red", "neck": "pink"}, 2, "vulture", "mwt: mother", head_scale=.92)
s["G17"] = sign("owl", reading="m", freq=8, colors={"plumage": "yellow", "wing": "yellow-dark", "tips": "brown", "legs": "yellow", "breast": "white"}, layers=[
  P("bird-legs"), P("bird-body"), P("bird-wing"), P("head-owl", at=[30, 64])])
s["G25"] = bird("head-ibis", {"plumage": "green-dark", "wing": "green", "tips": "blue-dark", "legs": "red", "breast": "green"}, 2, "crested ibis", "Ax: spirit", head_at=(31, 64))
s["G35"] = bird("head-cormorant", {"plumage": "black", "wing": "blue-dark", "tips": "black", "legs": "black", "breast": "white"}, 2, "cormorant", "aq: enter")
s["G36"] = bird("head-small", {"plumage": "blue", "breast": "white", "wing": "blue-dark", "tips": "black", "legs": "red", "beak": "black"}, 3, "swallow", "wr: great", head_at=(32, 63))
s["G37"] = bird("head-small", {"plumage": "yellow-dark", "breast": "white", "wing": "brown", "tips": "black", "legs": "red"}, 3, "sparrow", "nDs: small, bad", head_at=(32, 63))
s["G39"] = bird("head-duck", {"plumage": "yellow-dark", "breast": "white", "wing": "green", "tips": "blue", "legs": "red", "neck": "green"}, 3, "pintail duck", "sA: son", head_at=(31, 64))
s["G43"] = sign("quail chick", reading="w", freq=8, colors={"plumage": "yellow", "wing": "yellow-dark", "tips": "brown", "legs": "red", "breast": "white"}, layers=[
  P("bird-legs", at=[0, 0]),
  S([[34, 62], [24, 54], [24, 40], [34, 30], [52, 26], [70, 30], [80, 42], [76, 56], [62, 64], [46, 66]], "plumage"),
  S([[52, 60], [66, 58], [74, 46], [68, 38], [56, 42], [48, 52]], "wing"),
  P("head-small", at=[34, 60], scale=1.1)])
s["G40"] = sign("pintail duck flying", reading="pA: fly", freq=2, colors={"plumage": "yellow-dark", "breast": "white", "wing": "green", "tips": "blue", "legs": "red", "neck": "green"}, layers=[
  S([[52, 52], [62, 74], [80, 92], [92, 96], [88, 80], [74, 62], [62, 48]], "wing"),
  P("bird-body", at=[6, -6], rot=-12), P("head-duck", at=[34, 58], rot=12, scale=.95),
  L([[56, 22], [52, 8], [44, 6]], "legs", 2.6), L([[64, 22], [64, 8], [56, 6]], "legs", 2.6),
  S([[54, 50], [72, 60], [88, 66], [76, 52], [62, 44]], "tips")])
category("G", s)
