# r3.py OUT QUERY WAIT ITEMS [--variant=] [--hf=0.22] [--yf=0.5] [--hk=1] ; ITEMS: comma list of F:view[@ms]  F in b(body, skinned mesh box) h(head) w(wide all meshes)
import sys, json, base64
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
out, q, wait, items = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
opt = lambda k, d: next((a.split("=",1)[1] for a in sys.argv if a.startswith("--"+k+"=")), d)
variant=opt("variant",""); KF=opt("k",""); KB=opt("kb",""); hf=opt("hf","0.22"); yf=opt("yf","0.5"); hk=opt("hk","1"); bk=opt("bk","1")
js = """(async()=>{const t0=Date.now();while(Date.now()-t0<%d&&!window.__assets)await new Promise(r=>setTimeout(r,500));const TH=await import('three');let last=-1,same=0;
while(Date.now()-t0<%d){const b=new TH.Box3();window.__assets.scene.traverse(o=>{if(o.isMesh&&o.visible&&o.geometry&&o.type!=='GridHelper')b.expandByObject(o)});const z=b.isEmpty()?0:b.getSize(new TH.Vector3()).length();
let sk=false;window.__assets.scene.traverse(o=>{if(o.isSkinnedMesh&&o.visible&&(o.geometry?.attributes?.position?.count||0)>500)sk=true});if(sk&&z>0.3&&Math.abs(z-last)<1e-3*z)same++;else same=0;last=z;if(same>=3)break;await new Promise(r=>setTimeout(r,1000));}
await new Promise(r=>setTimeout(r,2000));const A=window.__assets;const THREE=TH;
{const VAR=%s;if(VAR){const el=document.getElementById('json');const dd0=JSON.parse(el.value);const vv=dd0.variants[VAR];const t=dd0.colors?'colors':'c';dd0.params={...(dd0.params||{}),...(vv.params||{})};dd0[t]={...(dd0[t]||{}),...(vv.colors||{})};delete dd0.variants;delete dd0.coats;el.value=JSON.stringify(dd0);el.dispatchEvent(new Event('input'));await new Promise(r=>setTimeout(r,25000));}}
const cv=[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];const res=[];
const HF=%s,YF=%s,HK=%s,BK=%s;
function frames(){let sm=null;A.scene.traverse(o=>{if(o.isSkinnedMesh&&o.visible&&(!sm||o.geometry.attributes.position.count>sm.geometry.attributes.position.count))sm=o});
const F={};const bb=new THREE.Box3().setFromObject(sm);const xl=bb.max.x-bb.min.x,yl=bb.max.y-bb.min.y;
F.b=[new THREE.Vector3(0,(bb.min.y+bb.max.y)/2,(bb.min.x+bb.max.x)/2),Math.max(xl,yl)*1.15*BK];
const P0=sm.geometry.attributes.position,v=new THREE.Vector3();let n=0,sy=0,sx=0,y0=1e9,y1=-1e9;for(let i=0;i<P0.count;i++){v.fromBufferAttribute(P0,i).applyMatrix4(sm.matrixWorld);if(v.x>bb.max.x-HF*xl&&v.y>bb.min.y+YF*yl){n++;sy+=v.y;sx+=v.x;y0=Math.min(y0,v.y);y1=Math.max(y1,v.y)}}
F.h=[new THREE.Vector3(0,sy/Math.max(n,1),sx/Math.max(n,1)),Math.max(HF*xl,y1-y0)*2.2*HK];{let n=0,sy=0,sx=0,y0=1e9,y1=-1e9;for(let i=0;i<P0.count;i++){v.fromBufferAttribute(P0,i).applyMatrix4(sm.matrixWorld);if(v.x<bb.min.x+HF*xl){n++;sy+=v.y;sx+=v.x;y0=Math.min(y0,v.y);y1=Math.max(y1,v.y)}}F.t=[new THREE.Vector3(0,sy/Math.max(n,1),sx/Math.max(n,1)),Math.max(HF*xl,y1-y0)*2.2*HK];}
const b2=new THREE.Box3();A.scene.traverse(o=>{if(o.isMesh&&o.visible&&o.geometry&&o.type!=='GridHelper'&&!(o.geometry.attributes.position&&o.geometry.attributes.position.count<=4))b2.expandByObject(o)});const S=b2.getSize(new THREE.Vector3());
F.w=[b2.getCenter(new THREE.Vector3()),Math.max(S.x,S.y,S.z)*1.25+0.5];F.info=[bb.min.toArray(),bb.max.toArray(),S.toArray()];const KF=%s;if(KF)F.k=[new THREE.Vector3(KF[2]||0,KF[1],KF[0]),KF[3]];const KB=%s;if(KB)F.k=[new THREE.Vector3(0,bb.min.y+KB[1]*yl,bb.min.x+KB[0]*xl),KB[2]*Math.max(xl,yl)];return F;}
let F=frames();window.__F=F.info;
for(const it of '%s'.split(',')){const [kv,ms]=it.split('@');const [f,k]=kv.split(':');if(ms)await new Promise(r=>setTimeout(r,+ms));if(f==='w')F=frames();const [C,d]=F[f];
const P={side:[0,0,d],front:[d,.05*d,0],top:[0,d,.01],q:[d*.7,d*.45,d*.7],back:[-d,.1*d,0],under:[.3*d,-d*.6,.5*d],fq:[d*.75,.2*d,d*.55],low:[.5*d,.02*d,.85*d],qb:[-d*.7,d*.35,d*.7],bq:[-d*.6,.3*d,-d*.6]};const p=P[k];
A.nav.lookAt(new THREE.Vector3(C.x+p[0],C.y+p[1],C.z+p[2]),C);await new Promise(r=>setTimeout(r,ms?80:500));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));res.push([f+'_'+k,cv.toDataURL('image/png')]);}
return JSON.stringify({res,err:document.getElementById('err')?.innerText,stats:document.getElementById('stats')?.innerText,info:window.__F});})()""" % (wait*1000, wait*1000, json.dumps(variant), hf, yf, hk, bk, "["+KF+"]" if KF else "null", "["+KB+"]" if KB else "null", items)
_r = headless.run_page(q, ready="document.readyState === 'complete'", result=js, flags=["--enable-unsafe-webgpu","--enable-features=Vulkan","--use-angle=vulkan","--window-size=1300,800"], timeout=wait+400, log=("--log" in sys.argv))
if not isinstance(_r,str): print(repr(_r)[:2000]); sys.exit(1)
r = json.loads(_r)
for i,(k, v) in enumerate(r.pop("res")): open(f"{out}_{i:02d}_{k}.png", "wb").write(base64.b64decode(v.split(",")[1]))
print(json.dumps(r)[:600])
