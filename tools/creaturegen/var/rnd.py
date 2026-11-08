import json,sys,math
src,dst=sys.argv[1],sys.argv[2]
d=json.load(open(src))
sh=d['sculpt']['shape']
C="#a89474"; TIP="#d2c6ac"
def get(i): return next(s for s in sh if s.get('id')==i)
def norm(v):
    l=math.sqrt(sum(x*x for x in v)); return [x/l for x in v]
def tine(id,base,dirv,L,r0=.015,curl=(0,.25,0),when="bull"):
    dv=norm(dirv); pts=[]
    for i,t in enumerate([0,.2,.45,.7,.86,.95,1.0]):
        bend=t*t*L*0.5
        p=[base[j]+dv[j]*L*t+curl[j]*bend for j in range(3)]
        r=max(.002,r0*(1-t**1.6)) if t<1 else .002
        pts.append([round(x,4) for x in p]+[round(r,4)])
    return {"id":id,"when":when,"type":"tube","bone":"head","pts":pts,"k":0,"color":C,"mirror":True,"tip":TIP,"tipAt":.45}
drop={"palm","palm2"}|{f"palmPt{i}d" for i in range(5)}
out=[s for s in sh if s.get('id') not in drop]
beam=get('beam')
ext=[[0.875,2.456,0.470,0.0232],[0.903,2.483,0.463,0.0226],[0.925,2.514,0.457,0.022],[0.94,2.548,0.452,0.0212],[0.948,2.58,0.448,0.02]]
beam['pts']=beam['pts']+ext
# small crown palmation in the plane of the beam top
crown={"id":"crown","when":"bull","type":"ell","bone":"head","c":[0.93,2.545,0.454],"r":[0.052,0.036,0.012],"rot":[-12,0,62],"k":0.02,"color":C,"mirror":True}
bp=get('bezPalm'); bp['r']=[0.048,0.037,0.013]; bp['k']=0.016
new=[crown,
 tine("topT0d",[0.948,2.578,0.448],[0.3,1,-0.04],.15,curl=(.3,0,0)),
 tine("topT1d",[0.952,2.55,0.449],[1,0.45,-0.05],.15,curl=(0,.4,0)),
 tine("topT2d",[0.91,2.50,0.46],[-0.2,1,0.02],.12,r0=.013,curl=(.3,0,0)),
 tine("back2d",[0.575,2.226,0.496],[-1,0.75,0.04],.115,r0=.013,curl=(0,.4,0)),
]
i=out.index(beam)+1
out[i:i]=new
d['sculpt']['shape']=out
ab=d['sculpt'].get('_about','')
d['sculpt']['_about']=ab+" Round 2: bull beam is a long C sweeping back then forward, topped by a small crown palmation with three short tines (topT*), a back tine and a second upper back tine; the old palm 'hand' (palm, palm2, palmPt*) is gone; bez palm reduced; brow shovel kept."
json.dump(d,open(dst,'w'),indent=1)
print(len(out))
