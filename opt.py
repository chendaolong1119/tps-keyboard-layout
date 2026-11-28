"""Simulated-annealing layout search (bigram approximation of the cost model).
Usage: python opt.py {A|B|free} SEED ITERATIONS"""
import numpy as np,math,random,collections,json,sys
import model
from model import unit_stream,CELLS,EFF,desk_pair,PHPOS,fitts,dist,REACH
ENTMAP={'ㆴ':'ㄅ','ㆵ':'ㄉ','ㆻ':'ㄍ','ㆷ':'ㄏ'}
RARE={'ㆱ','ˇ','ˆ'}
U=['ㄅ','ㄆ','ㄇ','ㆠ','ㄉ','ㄊ','ㄋ','ㄌ','ㄍ','ㄎ','ㄫ','ㆣ','ㄏ','ㄗ','ㄘ','ㄙ','ㆡ','ㄚ','ㄧ','ㄨ','ㆤ','ㄜ','ㆦ','ㄞ','ㄠ','ㄢ','ㄣ','ㄤ','ㄥ','ㆲ','ㆰ','ㆬ','ㆭ','N','ˋ','˪','ˊ','˫','˙']
INITIALS=U[:17]
idx={u:i for i,u in enumerate(U)};SP=len(U)
n=len(U)+1
c1=np.zeros(n);c2=np.zeros((n,n))
for seq in unit_stream():
    prev=None
    for u in seq:
        u=ENTMAP.get(u,u)
        if u in RARE: prev=None;continue
        i=SP if u=='␣' else idx[u]
        c1[i]+=1
        if prev is not None: c2[prev,i]+=1
        prev=i
nsyl=c1[SP]+sum(c1[idx[t]] for t in 'ˋ˪ˊ˫˙')
C=CELLS+['SP'];m=len(C)
E=np.array([EFF[c] for c in C])
PD=np.array([[desk_pair(a,b) for b in C] for a in C])
def th(c): x=PHPOS[c][0]; return 'L' if x<model.PHONE_CENTER-0.3 else ('R' if x>model.PHONE_CENTER+0.3 else 'C')
PP=np.zeros((m,m))
for i,a in enumerate(C):
    for j,b in enumerate(C):
        ta,tb=th(a),th(b)
        same = ta==tb and ta!='C'
        PP[i,j]=(fitts(dist(PHPOS[a],PHPOS[b])) if same else 0.17)+REACH(PHPOS[b])
# Weights of the annealing objective: the Taigi-TPS desktop and phone costs, the same reference as the composite score.
import layouts
_r=model.evaluate(layouts.TPS,allo=True,tps_ent=True); REF=(_r['desk'],_r['phone'])
def cost(asg):
    # asg: array len n of cell indices (SP fixed to last cell)
    d=(c1*E[asg]).sum()+(c2*PD[np.ix_(asg,asg)]).sum()
    p=(c2*PP[np.ix_(asg,asg)]).sum()
    return d/nsyl/REF[0]+p/nsyl/REF[1], d/nsyl, p/nsyl
def anneal(fixed,allowed,iters=60000,seed=0,T0=0.02):
    """fixed: unit->cell ; allowed: unit->set of cells"""
    rnd=random.Random(seed)
    cellidx={c:i for i,c in enumerate(C)}
    asg=np.full(n,-1);asg[SP]=cellidx['SP']
    used=set([cellidx['SP']])
    for u,c in fixed.items(): asg[idx[u]]=cellidx[c];used.add(cellidx[c])
    free=[i for i in range(n) if asg[i]<0]
    # greedy random init respecting allowed
    order=sorted(free,key=lambda i:len(allowed.get(U[i],CELLS)))
    for i in order:
        opts=[cellidx[c] for c in allowed.get(U[i],CELLS) if cellidx[c] not in used]
        k=rnd.choice(opts);asg[i]=k;used.add(k)
    movable=free
    occupant={asg[i]:i for i in range(n)}
    cur=cost(asg)[0];best=cur;bestasg=asg.copy()
    for it in range(iters):
        T=T0*(1-it/iters)+1e-5
        i=rnd.choice(movable);ui=U[i]
        tgt=cellidx[rnd.choice(list(allowed.get(ui,CELLS)))]
        if tgt==asg[i] or tgt==cellidx['SP']: continue
        j=occupant.get(tgt)
        if j is not None:
            if j not in movable: continue
            if C[asg[i]] not in allowed.get(U[j],CELLS): continue
        old_i=asg[i]
        asg[i]=tgt
        if j is not None: asg[j]=old_i
        new=cost(asg)[0]
        if new<cur or rnd.random()<math.exp((cur-new)/T):
            cur=new
            occupant[tgt]=i
            if j is not None: occupant[old_i]=j
            else: occupant.pop(old_i,None)
            if cur<best: best=cur;bestasg=asg.copy()
        else:
            asg[i]=old_i
            if j is not None: asg[j]=tgt
    return best,{U[i]:C[bestasg[i]] for i in range(len(U))}
DAQIAN={'ㄅ':'1','ㄉ':'2','ˋ':'4','ˊ':'6','˙':'7','ㄚ':'8','ㄞ':'9','ㄢ':'0','ㄆ':'q','ㄊ':'w','ㄍ':'e','ㄗ':'y','ㄧ':'u','ㄣ':'p','ㄇ':'a','ㄋ':'s','ㄎ':'d','ㄘ':'h','ㄨ':'j','ㄜ':'k','ㄠ':'l','ㄤ':';','ㄌ':'x','ㄏ':'c','ㄙ':'n','ㄥ':'/'}
LEFT=[c for c in CELLS if model.FINGER[c]<5]
# Layout A also keeps the Dachien tone keys of the rare tones: ˇ (tone 6) on 3, as Mandarin ˇ,
# and ˆ (tone 9) on 5 beside it. They are not annealed (too rare); their keys are closed to the others.
A_TONES={'ˇ':'3','ˆ':'5'}
A_CELLS=[c for c in CELLS if c not in A_TONES.values()]
def a_allowed(units): return {u:A_CELLS for u in units if u not in DAQIAN}
# Learnability adjustment of Layout A, chosen by the author after the annealing: the two frequent
# Taiwanese tones ˫ and ˪ trade keys with the voiced initials ㆠ and ㆡ, so that every tone mark sits
# in the two upper rows (3-7, R, T) and the initials below; it costs about 1.8 composite points.
def a_learn(lay):
    lay=dict(lay)
    for t,i in (('˫','ㆠ'),('˪','ㆡ')):
        if t in lay and i in lay: lay[t],lay[i]=lay[i],lay[t]
    return lay
A_UPPER=['r','t']   # the keys the adjustment gives to ˫ and ˪
if __name__=='__main__':
    mode=sys.argv[1];seed=int(sys.argv[2])
    # A = Dachien-preserving, B = hand-split (initials on the left half), free = unconstrained
    if mode=='A': fixed=DAQIAN;allowed=a_allowed(U)
    elif mode=='B': fixed={};allowed={u:LEFT for u in INITIALS}
    else: fixed={};allowed={}
    b,lay=anneal(fixed,allowed,iters=int(sys.argv[3]),seed=seed)
    print(json.dumps({'mode':mode,'seed':seed,'cost':b,'layout':lay},ensure_ascii=False))
