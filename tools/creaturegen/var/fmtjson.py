import json,sys
def one(v): return json.dumps(v, ensure_ascii=False)
def fmt(v, ind=0, inlist=False):
    s=one(v)
    if not isinstance(v,(dict,list)) or len(s)<=90 or (inlist and isinstance(v,dict)) or (isinstance(v,list) and all(not isinstance(x,dict) for x in v)):
        return s
    p="  "*(ind+1); q="  "*ind
    if isinstance(v,dict):
        return "{\n"+",\n".join(p+one(k)+": "+fmt(x,ind+1) for k,x in v.items())+"\n"+q+"}"
    return "[\n"+",\n".join(p+fmt(x,ind+1,True) for x in v)+"\n"+q+"]"
for f in sys.argv[1:]:
    d=json.load(open(f)); open(f,'w').write(fmt(d)+"\n")
