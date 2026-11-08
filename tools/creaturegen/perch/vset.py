# vset.py BIRD R1,R2 -> prints SETUPS js for pv2 (perched pose on a bough of radius r) and the G point
import sys, json, math
B = sys.argv[1]; RS = [float(x) for x in sys.argv[2].split(",")]
d = json.load(open(f"/home/martin/store/apps/multiverse/assets/creatures/birds/{B}.json"))
by = {p["id"]: p for p in d["parts"]}
fb = by["footL"]; P = fb["perchPitch"] * math.pi / 180
s = [0, 0]; q = fb
while q:
    s[0] += q.get("pos", [0, 0])[0]; s[1] += q.get("pos", [0, 0])[1]; q = by.get(q.get("parent"))
c, n = math.cos(P), math.sin(P); G = [c * s[0] - n * s[1], n * s[0] + c * s[1]]
FOLD = {"parrot": "{fold:[[100,-40,12],[0,0,0],[0,0,0]],squeeze:[.45,1,.3]}", "eagle": "{fold:[[90,0,8],[0,0,0],[0,-80,0]],squeeze:[.7,1,.25]}"}.get(B, "undefined")
out = []
for r in RS:
    out.append(f"""an.position.y=.4;an.perchFold={FOLD};an.perch=1;an.legs=1;an.pitch={P};an.perchR={r};an.rotY=-Math.PI/2;let b=A.scene.getObjectByName('bough');if(!b){{b=new TH.Mesh(new TH.CylinderGeometry(1,1,.6,32),new TH.MeshBasicMaterial({{color:0x7a5a3a}}));b.name='bough';b.rotation.z=Math.PI/2;A.scene.add(b);}}b.scale.set({r},1,{r});const p=an.position;b.position.set(p.x,p.y+{G[1]-r},p.z+{G[0]});""")
print(";;".join(out))
k={"parrot":.7,"eagle":1.15}.get(B,1.0); Y=.4
T=(0,Y+.25*k,G[0]*.55); F=(0,Y+G[1],G[0])
f=lambda a:",".join("%.3f"%x for x in a)
add=lambda a,b,m=1:[a[i]+b[i]*m for i in range(3)]
V={"b_front":(add(T,(0,.15,1.7),k),T),"b_q":(add(T,(-1.2,.35,1.2),k),T),"b_side":(add(T,(-1.7,.1,0),k),T),
 "h_q":(add(T,(-.55,.45,.6),k),add(T,(0,.3*k,.25*k))),"feet_q":(add(F,(-.32,.1,.3),k),F),"feet_front":(add(F,(0,.05,.42),k),F),"feet_under":(add(F,(-.35,-.18,.1),k),F)}
print(";".join(f"{n}@{f(e)}@{f(t)}" for n,(e,t) in V.items()))
print(json.dumps({"G": G, "P": P, "stand": s}), file=sys.stderr)
