import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams['font.family']=['Noto Sans CJK TC','DejaVu Sans']
from model import ROWS
from config import OUT
INITIALS=list('ㄅㄆㄇㆠㄉㄊㄋㄌㄍㄎㄫㆣㄏㄗㄘㄙㆡ')
best=json.load(open(OUT/'layouts_proposed.json',encoding='utf-8'))
SEC={'ㄅ':'ㆴ','ㄉ':'ㆵ','ㄍ':'ㆻ','ㄏ':'ㆷ','ㆰ':'ㆱ','ˋ':'ˇ','ˊ':'ˆ'}
TONES='ˋ˪ˊ˫˙'
COL={'ini':'#dbe9f6','rime':'#fbe3cf','tone':'#e2f0d9','nas':'#eadcf2','none':'#f2f2f2'}
def cat(u):
    if u is None: return 'none'
    if u in INITIALS: return 'ini'
    if u in TONES: return 'tone'
    if u=='N': return 'nas'
    return 'rime'
def draw(m,fn,title):
    inv={c:u for u,c in best[m].items()}
    fig,ax=plt.subplots(figsize=(11.5,4.6));ax.set_xlim(-0.1,11.3);ax.set_ylim(-0.3,5.3);ax.axis('off')
    offs=[0,0.5,0.75,1.25]
    for ri,r in enumerate(ROWS):
        for i,c in enumerate(r):
            x=offs[ri]+i;y=4-ri
            u=inv.get(c)
            ax.add_patch(FancyBboxPatch((x+0.05,y+0.05),0.9,0.9,boxstyle='round,pad=0.0,rounding_size=0.12',fc=COL[cat(u)],ec='#888',lw=0.8))
            ax.text(x+0.13,y+0.82,c.upper(),fontsize=8,color='#777',va='top')
            if u: ax.text(x+0.5,y+0.42,'nas' if u=='N' else u,fontsize=20 if u!='N' else 15,ha='center',va='center')
            if u in SEC: ax.text(x+0.85,y+0.82,SEC[u],fontsize=10,color='#c0392b',ha='right',va='top')
    ax.add_patch(FancyBboxPatch((3.3,-0.2),4.5,0.75,boxstyle='round,pad=0.0,rounding_size=0.12',fc=COL['tone'],ec='#888',lw=0.8))
    ax.text(5.55,0.17,'Space = tones 1 and 4',fontsize=11,ha='center',va='center')
    for k,(lab,cc) in enumerate([('Initial','ini'),('Rime','rime'),('Tone','tone'),('Nasalization','nas')]):
        ax.add_patch(FancyBboxPatch((8.4+k*0.72,0.05),0.22,0.22,boxstyle='square,pad=0',fc=COL[cc],ec='#888'))
        ax.text(8.68+k*0.72,0.16,lab,fontsize=9,va='center')
    ax.set_title(title+' (red = auto-converted or secondary character)',fontsize=12)
    fig.savefig(OUT/'figures'/fn,dpi=160,bbox_inches='tight');plt.close(fig)
draw('A','layout_A.png','Layout A: Dachien-preserving')
draw('B','layout_B.png','Layout B: hand-split (all initials on the left half)')
draw('C','layout_C.png','Layout C: structured hand-split (columns = place, rows = manner)')
draw('free','layout_free.png','Unconstrained reference')
