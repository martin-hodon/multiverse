import sys
from PIL import Image
out=sys.argv[1]; fs=sys.argv[2:]
ims=[Image.open(f) for f in fs]
sc=.5; cols=min(3,len(ims)); rows=(len(ims)+cols-1)//cols
W=int(ims[0].width*sc); H=int(ims[0].height*sc)
s=Image.new('RGB',(W*cols,H*rows))
for k,i in enumerate(ims):
    i=i.resize((W,H)); 
    # crop-zoom center? keep
    s.paste(i,((k%cols)*W,(k//cols)*H))
s.save(out)
