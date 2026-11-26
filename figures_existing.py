import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from config import OUT
plt.rcParams['font.family']=['Noto Sans CJK TC','DejaVu Sans']
INI=set('ㄅㄆㄇㆠㄉㄊㄋㄌㄍㄎㄫㆣㄏㄗㄘㄙㆡㄐㄑㄒㆢ')
TONE=set('ˋ˪ˊ˫˙ˇˆ')
UNUSED=set(['ㄛ','ㄝ'])
COL={'ini':'#dbe9f6','rime':'#fbe3cf','tone':'#e2f0d9','nas':'#eadcf2','none':'#f2f2f2','unused':'#e4e4e4'}
def cat(u):
    if not u: return 'none'
    if u in UNUSED: return 'unused'
    if u in INI: return 'ini'
    if u.startswith('t') and u[1:].isdigit(): return 'tone'
    if u in TONE or u.startswith('入') or u in ('輕聲','neut','ent'): return 'tone'
    if u in ('鼻','nas'): return 'nas'
    return 'rime'
def draw(rows,offs,fn,title,second='Shift layer',space='Space = tones 1 and 4',space_x=3.3,width=None,grey=()):
    W=width or (max(o+len(r) for r,o in zip(rows,offs))+0.2)
    n=len(rows)
    fig,ax=plt.subplots(figsize=(W*1.03,(n+2.3)*0.98));ax.set_xlim(-0.1,W);ax.set_ylim(-1.1,n+1.3);ax.axis('off')
    for ri,(r,o) in enumerate(zip(rows,offs)):
        for i,(k,u,s) in enumerate(r):
            x=o+i;y=n-ri
            ax.add_patch(FancyBboxPatch((x+0.05,y+0.05),0.9,0.9,boxstyle='round,pad=0.0,rounding_size=0.12',fc=COL['unused' if k in grey else cat(u)],ec='#888',lw=0.8))
            if k: ax.text(x+0.13,y+0.82,k,fontsize=8,color='#777',va='top')
            if u:
                fs=20 if len(u)==1 else 11
                ax.text(x+0.5,y+0.42,u,fontsize=fs,ha='center',va='center')
            if s: ax.text(x+0.87,y+0.84,s,fontsize=10 if len(s)<3 else 8,color='#c0392b',ha='right',va='top')
    ax.add_patch(FancyBboxPatch((space_x,-0.2),4.5,0.75,boxstyle='round,pad=0.0,rounding_size=0.12',fc=COL['tone'],ec='#888',lw=0.8))
    ax.text(space_x+2.25,0.17,space,fontsize=11,ha='center',va='center')
    items=[('Initial','ini'),('Rime','rime'),('Tone','tone'),('Nasalization','nas'),('Not used in this study','unused')]
    x0=max(0.2,(W-6.2)/2)
    for k,(lab,cc) in enumerate(items):
        ax.add_patch(FancyBboxPatch((x0+k*1.3,-0.85),0.22,0.22,boxstyle='square,pad=0',fc=COL[cc],ec='#888'))
        ax.text(x0+0.28+k*1.3,-0.74,lab,fontsize=8,va='center')
    ax.set_title(title+f' (red = {second})',fontsize=12)
    fig.savefig(OUT/'figures'/fn,dpi=160,bbox_inches='tight');plt.close(fig)
K=[list('1234567890-'),list('QWERTYUIOP'),list('ASDFGHJKL;'),list('ZXCVBNM,./')]
def grid(m):
    return [[(k,)+tuple(m.get(k.lower(),('',''))) for k in row] for row in K]
OFF=[0,0.5,0.75,1.25]
TPS={'1':('ㄅ',''),'2':('ㄉ',''),'3':('˪',''),'4':('ˋ',''),'5':('˫',''),'6':('ˊ',''),'7':('ent',''),'8':('ㄚ',''),'9':('ㄞ',''),'0':('ㄢ',''),'-':('nas',''),
'q':('ㄆ',''),'w':('ㄊ',''),'e':('ㄍ',''),'r':('ㄐ',''),'t':('ㆣ',''),'y':('ㄗ',''),'u':('ㄧ',''),'i':('ㆦ',''),'o':('ㆤ',''),'p':('ㄣ',''),
'a':('ㄇ',''),'s':('ㄋ',''),'d':('ㄎ',''),'f':('ㄑ',''),'g':('ㄫ',''),'h':('ㄘ',''),'j':('ㄨ',''),'k':('ㄜ',''),'l':('ㄠ',''),';':('ㄤ',''),
'z':('ㆠ',''),'x':('ㄌ',''),'c':('ㄏ',''),'v':('ㄒ',''),'b':('ㆡ','ㆢ'),'n':('ㄙ',''),'m':('ㆬ',''),',':('ㆰ','ㆱ'),'.':('ㆲ',''),'/':('ㆭ','')}
draw(grid(TPS),OFF,'ex_TPS.png','Taigi-TPS (Windows)',second='second symbol on the same key')
TKW={'1':('ㄅ','ㆠ'),'2':('ㄉ',''),'3':('˪','ˇ'),'4':('ˋ',''),'5':('˫',''),'6':('ˊ','ˆ'),'7':('˙',''),'8':('ㄚ','ㆩ'),'9':('ㄞ','ㆮ'),'0':('ㄢ','ㆰ'),'-':('ㆲ','ㆱ'),
'q':('ㄆ',''),'w':('ㄊ',''),'e':('ㄍ','ㆣ'),'r':('ㄐ','ㆢ'),'t':('ㆴ',''),'y':('ㄗ','ㆡ'),'u':('ㄧ','ㆪ'),'i':('ㄛ',''),'o':('ㆤ','ㆥ'),'p':('ㄣ','ㆬ'),
'a':('ㄇ',''),'s':('ㄋ',''),'d':('ㄎ','ㄫ'),'f':('ㄑ',''),'g':('ㆵ',''),'h':('ㄘ',''),'j':('ㄨ','ㆫ'),'k':('ㄜ',''),'l':('ㄠ','ㆯ'),';':('ㄤ',''),
'z':('ㆷ',''),'x':('ㄌ',''),'c':('ㄏ',''),'v':('ㄒ',''),'b':('ㆻ',''),'n':('ㄙ',''),'m':('ㆨ',''),',':('ㄝ',''),'.':('ㆦ','ㆧ'),'/':('ㄥ','ㆭ')}
draw(grid(TKW),OFF,'ex_TKW.png','Taigi Keyboard (Windows)')
WSL={'1':('ㄅ','ㆠ'),'2':('ˋ',''),'3':('˪',''),'4':('',''),'5':('ˊ',''),'6':('',''),'7':('˫',''),'8':('˙',''),'9':('neut',''),'0':('',''),'-':('ㄫ','ㆭ'),
'q':('ㄆ',''),'w':('ㄊ',''),'e':('ㄍ','ㆣ'),'r':('ㄐ','ㆢ'),'t':('ㄚ','ㆩ'),'y':('ㄗ','ㆡ'),'u':('ㄧ','ㆪ'),'i':('ㆦ','ㆧ'),'o':('ㆰ',''),'p':('ㄣ',''),
'a':('ㄇ','ㆬ'),'s':('ㄋ',''),'d':('ㄎ',''),'f':('ㄑ',''),'g':('ㄞ','ㆮ'),'h':('ㄘ',''),'j':('ㄨ','ㆫ'),'k':('ㄜ','eer'),'l':('ㄠ','ㆯ'),';':('ㄤ',''),
'z':('ㄉ','dd'),'x':('ㄌ',''),'c':('ㄏ','ㄬ'),'v':('ㄒ',''),'b':('ㄢ',''),'n':('ㄙ',''),'m':('ㆲ',''),',':('ㆤ','ㆥ'),'.':('ㆱ',''),'/':('ㄥ','')}
g=grid(WSL); g[0]=[('`','ㆨ','')]+g[0]
draw(g,[0,1.5,1.75,2.25],'ex_WSL.png','Wu Shou-li IME, Taiwanese-dedicated keyboard; eer, dd = not yet in Unicode',space='Space = tones 1, 4 (digit = tone number)',space_x=3.8)
AR=[[('1','ㆠ',''),('2','ˋ',''),('3','˪',''),('4','ㆣ',''),('5','ˊ',''),('6','ˇ',''),('7','˫',''),('8','˙',''),('9','ㆪ',''),('0','ㆩ','')],
[('','ㄅ','ㆴ'),('','ㄉ','ㆵ'),('','ㄍ','ㆻ'),('','ㄏ','ㆷ'),('','ㄧ',''),('','ㄚ',''),('','ㄞ',''),('','ㄤ',''),('','ㆫ',''),('','ㆧ','')],
[('','ㄆ',''),('','ㄊ',''),('','ㄎ',''),('','ㄗ','ㄐ'),('','ㄨ',''),('','ㄛ',''),('','ㄠ',''),('','ㆲ',''),('','ㆥ',''),('','ㆮ','ㆯ')],
[('','ㄇ','ㆬ'),('','ㄋ','ㄣ'),('','ㄫ','ㆭㄥ'),('','ㄘ','ㄑ'),('','ㄜ',''),('','ㆦ',''),('','ㄢ',''),('','ㆰ','ㆱ'),('','；','')],
[('','ㄌ',''),('','ㆡ','ㆢ'),('','ㄙ','ㄒ'),('','ㆨ',''),('','ㆤ','ㄝ')]]
draw(AR,[0,0,0,0,1.2],'ex_AND.png','Taigi Keyboard (Android)',second='long press; digits on long press in the top row',space='Space = tones 1 and 4',space_x=5.0)

# Wu Shou-li IME, Mandarin-extended keyboard (Academia Sinica, 2012b): Taiwanese tones on F1-F9
HUA=[[('F1','t1',''),('F2','ˋ',''),('F3','˪',''),('F4','t4',''),('F5','ˊ',''),('F6','ˇ',''),('F7','˫',''),('F8','˙',''),('F9','ˆ','')],
 [('`','ㆨ',''),('1','ㄅ','ㆠ'),('2','ㄉ','dd'),('3','ˇ',''),('4','ˋ',''),('5','ㄓ',''),('6','ˊ',''),('7','˙',''),('8','ㄚ','ㆩ'),('9','ㄞ','ㆮ'),('0','ㄢ',''),('-','ㄦ',''),('=','ㆦ','ㆧ')],
 [('Q','ㄆ',''),('W','ㄊ',''),('E','ㄍ','ㆣ'),('R','ㄐ','ㆢ'),('T','ㄔ',''),('Y','ㄗ','ㆡ'),('U','ㄧ','ㆪ'),('I','ㄛ',''),('O','ㄟ',''),('P','ㄣ',''),('[','ㆰ',''),(']','ㆱ',''),('\\','ㄫ','ㆭ')],
 [('A','ㄇ','ㆬ'),('S','ㄋ',''),('D','ㄎ',''),('F','ㄑ',''),('G','ㄕ',''),('H','ㄘ',''),('J','ㄨ','ㆫ'),('K','ㄜ','eer'),('L','ㄠ','ㆯ'),(';','ㄤ',''),("'",'ㆲ','')],
 [('Z','ㄈ',''),('X','ㄌ',''),('C','ㄏ','ㄬ'),('V','ㄒ',''),('B','ㄖ',''),('N','ㄙ',''),('M','ㄩ',''),(',','ㆤ','ㆥ'),('.','ㄡ',''),('/','ㄥ','')]]
draw(HUA,[1.0,0,1.5,1.75,2.25],'ex_WSL_HUA.png','Wu Shou-li IME, Mandarin-extended keyboard; Taiwanese tones on F1-F9',
     space='Space = tones 1 and 4',space_x=4.5,grey={'3','4','5','6','7','-','T','I','O','G','Z','B','M','.'})
