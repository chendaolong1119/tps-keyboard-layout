import json,collections
INI={'p':'ㄅ','ph':'ㄆ','m':'ㄇ','b':'ㆠ','t':'ㄉ','th':'ㄊ','n':'ㄋ','l':'ㄌ','k':'ㄍ','kh':'ㄎ','ng':'ㄫ','g':'ㆣ','h':'ㄏ','ts':'ㄗ','tsh':'ㄘ','s':'ㄙ','j':'ㆡ','':''}
TONE={1:'␣',4:'␣',2:'ˋ',3:'˪',5:'ˊ',6:'ˇ',7:'˫',8:'˙',9:'ˆ'}
ENT={'p':'ㆴ','t':'ㆵ','k':'ㆻ','h':'ㆷ'}
CODA=[('iong','ㄧㆲ'),('iang','ㄧㄤ'),('uang','ㄨㄤ'),('ang','ㄤ'),('ong','ㆲ'),('ing','ㄧㄥ'),('iam','ㄧㆰ'),('am','ㆰ'),('om','ㆱ'),('im','ㄧㆬ'),('ian','ㄧㄢ'),('uan','ㄨㄢ'),('an','ㄢ'),('in','ㄧㄣ'),('un','ㄨㄣ'),('m','ㆬ'),('ng','ㆭ')]
V={'a':'ㄚ','i':'ㄧ','u':'ㄨ','e':'ㆤ','o':'ㄜ','oo':'ㆦ'}
def rime(f):
    # returns list of units (no tone)
    end=[]
    if f.endswith('h') and f not in ('h',):
        end=['ㆷ'];f=f[:-1]
    elif f[-1] in 'ptk':
        c=f[-1];f=f[:-1]
        # entering after vowel; 'ok','op','iok' use oo
        if f in ('o','io'): f=f[:-1]+'oo'
        if f=='i' and c=='k': pass
        end=[ENT[c]]
    nas=False
    if f.endswith('nn'): nas=True;f=f[:-2]
    for a,b in CODA:
        if f==a: return list(b)+(['N'] if nas else [])+end
    seq=[]
    i=0
    while i<len(f):
        if f[i:i+2]=='oo': seq.append('ㆦ');i+=2;continue
        if f[i:i+2]=='ai' and i+2==len(f) or f[i:i+2]=='ai' and f[i+2:]=='' : seq.append('ㄞ');i+=2;continue
        if f[i:i+2]=='au' and i+2==len(f): seq.append('ㄠ');i+=2;continue
        seq.append(V[f[i]]);i+=1
    if f=='m': seq=['ㆬ']
    if f=='ng': seq=['ㆭ']
    return seq+(['N'] if nas else [])+end
def syl_units(I,f,t):
    u=([INI[I]] if INI[I] else [])+rime(f)+[TONE[t]]
    return u
if __name__=='__main__':
    from config import OUT
    data=json.load(open(OUT/'syl.json'))
    uf=collections.Counter();tot=0
    for (I,f,t),c in data:
        for x in syl_units(I,f,t): uf[x]+=c
        tot+=c
    T=sum(uf.values())
    for k,v in uf.most_common(): print(k,f'{100*v/T:.2f}%',end=' | ')
    print();print('units/syl',T/tot,'n units',len(uf))
    for (I,f,t),c in sorted(data,key=lambda x:-x[1])[:15]: print(I,f,t,syl_units(I,f,t),c)
