import csv,re,unicodedata,sys,collections,json
from config import DATA, OUT
D=str(DATA)+'/'
TONE={'́':2,'̀':3,'̂':5,'̌':6,'̄':7,'̍':8,'̋':9}
def syls(text):
    t=unicodedata.normalize('NFD',text)
    for w in re.findall(r"[A-Za-z̀-ͯ]+(?:-+[A-Za-z̀-ͯ]+)*",t):
        for s in re.split(r'-+',w):
            tone=None;base=''
            for ch in s:
                if ch in TONE: tone=TONE[ch]
                elif unicodedata.category(ch)=='Mn': base='?'
                else: base+=ch.lower()
            yield base,tone
INI=['tsh','ts','ph','th','kh','ng','p','b','m','t','n','l','k','g','h','s','j']
FIN=set('a i u e o oo ai au ia io iu ua ue ui iau uai am an ang ong ap at ak ok ah ih uh eh oh ooh aih auh iah ioh iuh uah ueh uih iauh uaih im in ing ip it ik iam ian iang iong iap iat iak iok un ut uan uat m ng mh ngh ann inn enn onn ainn aunn iann iunn uann uinn iaunn uainn annh innh ennh onnh ainnh iannh iunnh uannh uinnh uainnh iaunnh om op un ionn ionnh'.split())
def parse(b):
    for I in INI+['']:
        if b.startswith(I):
            f=b[len(I):]
            if f in FIN: return I,f
    return None
def main():
    cnt=collections.Counter();bad=collections.Counter();streams=[]
    src=[('ChhoeTaigi_KauiokpooTaigiSutian.csv','KaisoehHanLoKip'),('ChhoeTaigi_TaijitToaSutian.csv','LekuHanLoKip')]
    for fn,col in src:
        for row in csv.DictReader(open(D+fn,encoding='utf-8-sig')):
            st=[]
            for b,t in syls(row[col]):
                p=parse(b)
                if not p or '?' in b: bad[b]+=1;continue
                I,f=p
                ent=f[-1] in 'ptkh' and not f.endswith('nnh') or f.endswith('h')
                if t is None: t=4 if ent else 1
                if ent and t not in (4,8): bad[b+str(t)]+=1;continue
                cnt[(I,f,t)]+=1;st.append((I,f,t))
            if st: streams.append(st)
    json.dump([[list(k),v] for k,v in cnt.items()],open(OUT/'syl.json','w'));json.dump(streams,open(OUT/'streams.json','w'))
    print(sum(cnt.values()),'syllables',len(cnt),'types; bad',sum(bad.values()))
    print(bad.most_common(30))
main()
