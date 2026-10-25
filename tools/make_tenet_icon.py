import numpy as np, os, sys
from PIL import Image
from scipy import ndimage
S='C:/Users/stavs/AppData/Local/Temp/claude/C--Users-stavs-OneDrive-Documents-Paradox-Interactive-Crusader-Kings-III-mod-jewitup/9a1fcd87-a917-4402-9557-05177f03dafd/'
T='C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/faith_tenets/'
W,H=260,400
rng=np.random.default_rng(7)
SS=3  # supersample
w,h=W*SS,H*SS
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)/SS
cx=130
def strokes(apex_x,apex_y,half,seed,bins=900):
    rg=np.random.default_rng(seed)
    th=np.arctan2(xx-apex_x,yy-apex_y); rr=np.hypot(xx-apex_x,yy-apex_y)
    tb=((th/half+1.6)/3.2*bins).clip(0,bins-1).astype(int)
    line=ndimage.gaussian_filter1d(rg.random(bins),0.6); line=(line-line.min())/(line.max()-line.min())
    seg=ndimage.gaussian_filter(rg.random((bins,80)),(0.4,1.2)); seg=(seg-seg.min())/(seg.max()-seg.min())
    rb=((rr-50)/600*79).clip(0,79).astype(int)
    return line[tb]**1.3*(0.25+0.75*seg[tb,rb])
# main fan from a point above, plus two slightly tilted sets for the cross-hatched brush look
apex_y=-110; half=0.245
theta=np.arctan2(xx-cx,yy-apex_y)
st=np.maximum.reduce([strokes(cx,apex_y,half,1),0.8*strokes(cx-60,apex_y,half,2),0.8*strokes(cx+60,apex_y,half,3)])
edge_j=ndimage.gaussian_filter(rng.random((h,1)).repeat(w,1),(0,0))*0
ang=np.abs(theta)/half
jit=ndimage.gaussian_filter(rng.random((h//4+1,w//4+1)),1.5).repeat(4,0).repeat(4,1)[:h,:w]
fan=np.clip((1.0+0.5*(jit-0.5)-ang)/0.35,0,1)
top=np.clip((yy-(80+40*(jit-0.5)))/50,0,1)
bot=np.clip((340+40*(jit-0.5)-yy)/40,0,1)
core=np.exp(-(((xx-cx)/70)**2+((yy-230)/110)**2))
a=st*fan*top*bot*(0.55+0.45*core)*300 + core*fan*top*bot*30
a=np.clip(a,0,199)
halo=np.zeros((h,w,4),np.float32); halo[...,0]=200; halo[...,1]=203; halo[...,2]=203; halo[...,3]=a
halo=Image.fromarray(halo.astype(np.uint8),'RGBA').resize((W,H),Image.LANCZOS)
def down(im,size):
    arr=np.asarray(im).astype(np.float32)/255
    pm=np.dstack([arr[...,:3]*arr[...,3:4],arr[...,3:4]])
    p=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize(size,Image.LANCZOS)).astype(np.float32)/255
    al=p[...,3:4]; rgb=np.where(al>0,p[...,:3]/np.maximum(al,1e-6),0)
    return Image.fromarray((np.dstack([rgb,al]).clip(0,1)*255).astype(np.uint8),'RGBA')
obj=Image.open(S+'scratchpad/kehunah_cut.png')
ow,oh=obj.size; sc=min(195/ow,235/oh); nw,nh=round(ow*sc),round(oh*sc)
icon=halo.copy(); icon.alpha_composite(down(obj,(nw,nh)),(cx-nw//2,325-nh))
out='gfx/interface/icons/faith_tenets/tenet_kehunah.dds'
hdr=open(T+'tenet_simony.dds','rb').read(128)
open(out,'wb').write(hdr+np.asarray(icon)[...,[2,1,0,3]].tobytes())
print(os.path.getsize(out),os.path.getsize(T+'tenet_simony.dds'))
ims=[Image.open(T+f+'.dds').convert('RGBA') for f in ['tenet_simony','tenet_apostolic_succession']]+[Image.open(out).convert('RGBA'),halo]
sheet=Image.new('RGBA',(W*4,H),(45,40,38,255))
for i,im in enumerate(ims): sheet.alpha_composite(im,(i*W,0))
sheet.save(S+'scratchpad/kehunah_compare.png')
