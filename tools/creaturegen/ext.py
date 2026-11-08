import json,sys
for n in sys.argv[1:]:
  d=json.load(open('assets/creatures/%s.json'%n))
  print('==',n,'head',d.get('head'),'legs',json.dumps(d.get('legs'))[:200])
  for s in d['sculpt']['shape']:
    t=s.get('type'); pts=[]
    if t in('ell','sphere','box'):
      c=s.get('c'); r=s.get('r'); r=r if isinstance(r,list) else [r]*3
      if c and isinstance(c[0],(int,float)): pts=[[c[0]-r[0],c[1]-r[1]],[c[0]+r[0],c[1]+r[1]]]
    elif t=='tube': pts=[[p[0]-p[3],p[1]-p[3]] for p in s['pts'] if isinstance(p[0],(int,float))]+[[p[0]+p[3],p[1]+p[3]] for p in s['pts'] if isinstance(p[0],(int,float))]
    elif t=='cone':
      for k in 'ab':
        v=s.get(k)
        if v and isinstance(v[0],(int,float)): pts.append(v[:2])
    if pts:
      xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
      print('  %-12s %-8s %-5s x[%.2f,%.2f] y[%.2f,%.2f]'%(s.get('id'),s.get('bone'),t,min(xs),max(xs),min(ys),max(ys)))
    else: print('  %-12s %-8s %-5s %s'%(s.get('id'),s.get('bone'),t,json.dumps({k:v for k,v in s.items() if k in('c','a','b','pts')})[:120]))
