import json,math,collections,random
from units import syl_units
from config import OUT
streams=json.load(open(OUT/'streams.json'))
# ---------- unit streams ----------
def unit_stream():
    for st in streams:
        seq=[]
        for I,f,t in st: seq+=syl_units(I,f,t)
        yield seq
ALLO={'ㄗ':'ㄐ','ㄘ':'ㄑ','ㄙ':'ㄒ','ㆡ':'ㆢ'}
NASMAP={'ㄚ':'ㆩ','ㄧ':'ㆪ','ㄨ':'ㆫ','ㆤ':'ㆥ','ㆦ':'ㆧ','ㄞ':'ㆮ','ㄠ':'ㆯ','ㄜ':'ㆧ'}
def surface(seq,allo=False,precomp=False):
    out=[]
    for i,u in enumerate(seq):
        if allo and u in ALLO and i+1<len(seq) and seq[i+1]=='ㄧ': u=ALLO[u]
        if precomp and u=='N':
            out[-1]=NASMAP.get(out[-1],out[-1]);continue
        out.append(u)
    return out
# ---------- geometry ----------
ROWS=[list('1234567890-'),list('qwertyuiop'),list("asdfghjkl;"),list('zxcvbnm,./')]
CELLS=[c for r in ROWS for c in r]
FINGER={}
for r in ROWS:
    for i,c in enumerate(r):
        f=[0,1,2,3,3,6,6,7,8,9,9][i] if len(r)==11 else [0,1,2,3,3,6,6,7,8,9][i]
        FINGER[c]=f
FINGER['6']=6  # 6 typed by right index (common for zhuyin typists)
ROW={c:ri for ri,r in enumerate(ROWS) for c in r}
EFF={}
eff_rows=[[4.0,3.5,3.0,3.0,3.5,4.0,3.0,3.0,3.5,4.0,4.5],[2.5,1.8,1.3,1.3,2.0,2.3,1.3,1.3,1.8,2.5],[1.5,1.0,0.6,0.4,1.0,1.0,0.4,0.6,1.0,1.5],[2.5,2.0,1.6,1.4,2.3,1.4,1.4,1.6,2.0,2.5]]
for ri,r in enumerate(ROWS):
    for i,c in enumerate(r): EFF[c]=eff_rows[ri][i]
EFF['SP']=0.6;FINGER['SP']=5;ROW['SP']=4
# Keys outside the 41-key grid, used only by desktop-only layouts (Wu Shou-li Mandarin-extended keyboard).
# Row -1 = function-key row. Efforts extrapolate the grid: farther and pinky-heavier keys cost more.
EXTRA={'`':(4.5,0,0),'=':(5.0,9,0),'[':(3.0,9,1),']':(3.5,9,1),'\\':(4.0,9,1),"'":(2.0,9,2),
       'F1':(5.5,0,-1),'F2':(5.0,1,-1),'F3':(5.0,2,-1),'F4':(5.0,3,-1),'F5':(5.0,6,-1),
       'F6':(5.0,6,-1),'F7':(5.0,7,-1),'F8':(5.0,8,-1),'F9':(5.5,9,-1)}
for k,(e,f,r) in EXTRA.items():
    EFF[k]=e;FINGER[k]=f;ROW[k]=r
def hand(c): return 'T' if c=='SP' else ('L' if FINGER[c]<5 else 'R')
def desk_pair(a,b):
    if a is None: return 0
    ha,hb=hand(a),hand(b)
    if 'T' in (ha,hb): return 0
    if ha!=hb: return 0
    if a==b: return 0.3
    if FINGER[a]==FINGER[b]: return 2.5+0.5*abs(ROW[a]-ROW[b])
    return 0.4*max(0,abs(ROW[a]-ROW[b])-1)+0.1
# phone geometry: 大千-style 4 rows, 11-unit wide screen
PHPOS={}
for ri,r in enumerate(ROWS):
    off=0 if len(r)==11 else 0.5
    for i,c in enumerate(r): PHPOS[c]=(off+i+0.5,ri*1.4)
PHPOS['SP']=(5.5,4*1.4)
def fitts(d,w=1.0): return 0.10+0.15*math.log2(d/w+1)
def dist(p,q): return math.hypot(p[0]-q[0],p[1]-q[1])
def thumb(pos,last_thumb): 
    if pos[0]<5.2: return 'L'
    if pos[0]>5.8: return 'R'
    return 'R' if last_thumb=='L' else 'L'
REACH=lambda pos: 0.03*max(0,3*1.4-pos[1])/1.4
LONG=0.35; SHIFT_DESK=(2.0)  # extra cost of shift (extra keystroke + pinky)
# ---------- layout evaluation ----------
def evaluate(layout,phonepos=None,allo=False,precomp=False,detail=False):
    """layout: dict unit-> (cell, layer) layer 0 main,1 secondary. unit 'SP' implicit."""
    pp=phonepos or PHPOS
    D=0;P=0;K=0;nsyl=0;miss=collections.Counter()
    for seq in unit_stream():
        seq=surface(seq,allo,precomp)
        last=None;tpos={'L':None,'R':None};lt=None
        for u in seq:
            if u=='␣': cell,layer='SP',0; nsyl+=1
            elif u in layout: cell,layer=layout[u]
            else: miss[u]+=1;continue
            # desktop
            D+=EFF[cell]+desk_pair(last,cell)+(SHIFT_DESK if layer else 0)
            K+=1+(1 if layer else 0)
            if u in 'ˋ˪ˊˇ˫˙ˆ': nsyl+=1
            # phone
            pos=pp[cell];th=thumb(pos,lt)
            if tpos[th] is None: mt=0.25
            else:
                own=fitts(dist(tpos[th],pos))
                mt=own if th==lt else max(0.12,own-0.10)
            P+=mt+REACH(pos)+(LONG if layer else 0)
            tpos[th]=pos;lt=th;last=cell
    return dict(desk=D/nsyl,phone=P/nsyl,keys=K/nsyl,miss=dict(miss))
