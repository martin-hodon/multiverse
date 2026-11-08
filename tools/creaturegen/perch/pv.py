# pv.py OUT ASSET SETUPS VIEWS : the asset viewer, a bird posed by JS setups (';;'-separated, each a pose), shot from VIEWS (side,front,q,back,top,under)
# setup JS runs with A (window.__assets), an (person[0].an), SK (skeleton module)
import sys, json, base64
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
out, asset, setups, views = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = float(next((a.split("=",1)[1] for a in sys.argv if a.startswith("--d=")), "2.2"))
js = """(async()=>{try{const t0=Date.now();while(Date.now()-t0<150000&&!(window.__assets&&window.__assets.person))await new Promise(r=>setTimeout(r,500));
const A=window.__assets;const TH=await import('three');const SK=await import(new URL('skeleton.js',location.href).href);
while(Date.now()-t0<200000){let sk=false;A.scene.traverse(o=>{if(o.isSkinnedMesh&&o.visible&&(o.geometry?.attributes?.position?.count||0)>500)sk=true});if(sk)break;await new Promise(r=>setTimeout(r,1000));}
await new Promise(r=>setTimeout(r,3000));
const cv=[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];const res=[];const an=A.person[0].an;
const D=%f;const C=new TH.Vector3(0,.35,0);
const setups=%s.split(';;');
for(let si=0;si<setups.length;si++){ (new Function('A','an','SK','TH',setups[si]))(A,an,SK,TH); await new Promise(r=>setTimeout(r,1200));
 for(const v of '%s'.split(',')){const P={side:[0,0,D],front:[D,.05*D,0],q:[D*.7,D*.3,D*.7],back:[-D,.1*D,0],top:[0,D,.01],under:[.3*D,-D*.6,.5*D],bq:[-D*.6,.3*D,-D*.6],fq:[D*.75,.15*D,-D*.55]}[v];
  A.nav.lookAt(new TH.Vector3(C.x+P[0],C.y+P[1],C.z+P[2]),C);await new Promise(r=>setTimeout(r,400));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));res.push([si+'_'+v,cv.toDataURL('image/png')]);}}
return JSON.stringify({res,err:document.getElementById('err')?.innerText});}catch(e){return JSON.stringify({res:[],x:String(e.stack||e)});}})()""" % (d, json.dumps(setups), views)
_r = headless.run_page("assets.html?a=" + asset, ready="document.readyState === 'complete'", result=js, flags=["--enable-unsafe-webgpu","--enable-features=Vulkan","--use-angle=vulkan","--window-size=1000,800"], timeout=420, log=("--log" in sys.argv))
if not isinstance(_r, str): print(repr(_r)[:2000]); sys.exit(1)
r = json.loads(_r)
for i, (k, v) in enumerate(r.pop("res")): open(f"{out}_{k}.png", "wb").write(base64.b64decode(v.split(",")[1]))
print(json.dumps(r)[:500])
