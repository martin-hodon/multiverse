# a3.py OUT QUERY WAIT VIEWS  -- architecture: frame every visible mesh; VIEWS comma list of side,front,q,qb,top,low or custom "x:y:z" eye offsets as fractions of d
import sys, json, base64
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
out, q, wait, views = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
js = """(async()=>{const t0=Date.now();while(Date.now()-t0<%d&&!window.__assets)await new Promise(r=>setTimeout(r,500));const THREE=await import('three');
let last=-1,same=0;while(Date.now()-t0<%d){const b=new THREE.Box3();window.__assets.scene.traverse(o=>{if(o.isMesh&&o.visible&&o.geometry&&o.type!=='GridHelper')b.expandByObject(o)});
const z=b.isEmpty()?0:b.getSize(new THREE.Vector3()).length();if(z>1&&Math.abs(z-last)<1e-3*z)same++;else same=0;last=z;if(same>=4)break;await new Promise(r=>setTimeout(r,1000));}
await new Promise(r=>setTimeout(r,3000));const A=window.__assets;const b2=new THREE.Box3();A.scene.traverse(o=>{if(o.isMesh&&o.visible&&o.geometry&&o.type!=='GridHelper'&&!(o.geometry.attributes.position&&o.geometry.attributes.position.count<=4))b2.expandByObject(o)});
const C=b2.getCenter(new THREE.Vector3()),S=b2.getSize(new THREE.Vector3()),d=Math.max(S.x,S.y,S.z)*0.9;
const cv=[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];const res=[];
const P={side:[0,.1,1],front:[1,.1,0],q:[.7,.35,.7],qb:[-.7,.35,.7],top:[0,1,.01],low:[.4,.05,.9]};
for(const k of '%s'.split(',')){const p=P[k]||k.split(':').map(Number);A.nav.lookAt(new THREE.Vector3(C.x+p[0]*d,C.y+p[1]*d,C.z+p[2]*d),C);
await new Promise(r=>setTimeout(r,1500));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));res.push([k.replace(/:/g,'_'),cv.toDataURL('image/png')]);}
return JSON.stringify({res,err:document.getElementById('err')?.innerText,box:[b2.min.toArray(),b2.max.toArray()]});})()""" % (wait*1000, wait*1000, views)
_r = headless.run_page(q, ready="document.readyState === 'complete'", result=js, flags=["--enable-unsafe-webgpu","--enable-features=Vulkan","--use-angle=vulkan","--window-size=1300,800"], timeout=wait+400)
if not isinstance(_r,str): print(repr(_r)[:2000]); sys.exit(1)
r = json.loads(_r)
for i,(k, v) in enumerate(r.pop("res")): open(f"{out}_{i:02d}_{k}.png", "wb").write(base64.b64decode(v.split(",")[1]))
print(json.dumps(r)[:600])
