"""Pick the best annealing run per configuration, build the structured Layout C,
and score all existing and proposed layouts on the full keystroke streams.
Writes out/layouts_proposed.json and out/scores.csv."""
import json, glob, itertools, csv
import numpy as np
import model, layouts, opt
from config import OUT
from units import syl_units

ENT = {'ㆴ': 'ㄅ', 'ㆵ': 'ㄉ', 'ㆻ': 'ㄍ', 'ㆷ': 'ㄏ'}
def full(lay):
    """Proposed input logic: entering finals on ㄅㄉㄍㄏ, rare units on the secondary layer."""
    d = {u: (c, 0) for u, c in lay.items()}
    for e, b in ENT.items(): d[e] = d[b]
    d['ㆱ'] = (lay['ㆰ'], 1); d['ˇ'] = (lay['ˋ'], 1); d['ˆ'] = (lay['ˊ'], 1)
    return d

def best_run(mode):
    rs = [json.load(open(f, encoding='utf-8')) for f in glob.glob(str(OUT / 'runs' / f'{mode}_*.json'))]
    return min(rs, key=lambda r: r['cost'])['layout']

def structured(base):
    """Layout C: left half as a place-by-manner grid; exhaustive search, then re-anneal the right half."""
    U, idx, C, cost = opt.U, opt.idx, opt.C, opt.cost
    cellidx = {c: i for i, c in enumerate(C)}
    cols = [['1','q','a','z'], ['2','w','s','x'], ['3','e','d','c'], ['4','r','f','v'], ['5','t','g','b']]
    groups = {'lab': ['ㄇ','ㄆ','ㄅ','ㆠ'], 'alv': ['ㄋ','ㄊ','ㄉ','ㄌ'], 'vel': ['ㄫ','ㄎ','ㄍ','ㆣ'], 'aff': [None,'ㄘ','ㄗ','ㆡ']}
    extra = ['ㄙ', 'ㄏ', 'ˋ', 'ˊ', '˫']
    base_asg = np.array([cellidx[base[u]] for u in U] + [cellidx['SP']])
    best = None
    for perm in itertools.permutations(range(5), 4):
        asg = base_asg.copy(); free = []
        for g, ci in zip(groups, perm):
            for r, u in enumerate(groups[g]):
                if u: asg[idx[u]] = cellidx[cols[ci][r]]
                else: free.append(cols[ci][r])
        free += cols[[c for c in range(5) if c not in perm][0]]
        for p2 in itertools.permutations(free, 5):
            for u, c in zip(extra, p2): asg[idx[u]] = cellidx[c]
            v = cost(asg)[0]
            if best is None or v < best[0]: best = (v, perm, p2)
    _, perm, p2 = best
    lay = dict(base)
    for g, ci in zip(groups, perm):
        for r, u in enumerate(groups[g]):
            if u: lay[u] = cols[ci][r]
    for u, c in zip(extra, p2): lay[u] = c
    fixed = {u: c for u, c in lay.items() if u in opt.INITIALS or u in extra}
    right = [c for c in opt.CELLS if c not in fixed.values()]
    runs = [opt.anneal(fixed, {u: right for u in U if u not in fixed}, iters=150000, seed=s) for s in range(4)]
    return min(runs, key=lambda r: r[0])[1]

def shift_share(lay, allo, precomp):
    data = json.load(open(OUT / 'syl.json', encoding='utf-8'))
    tot = sh = 0
    for (I, f, t), c in data:
        seq = model.surface(syl_units(I, f, t), allo=allo, precomp=precomp); tot += c
        if any(u in lay and lay[u][1] == 1 for u in seq): sh += c
    return 100 * sh / tot

if __name__ == '__main__':
    prop = {'A': best_run('A'), 'B': best_run('B'), 'free': best_run('free')}
    prop['C'] = structured(prop['B'])
    json.dump(prop, open(OUT / 'layouts_proposed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    and_lay, and_pos = layouts.android(False)
    rows = [('Taigi-TPS', layouts.TPS, None, dict(allo=True, tps_ent=True)),
            ('Wu Shou-Li (Taiwanese-dedicated)', layouts.WSL, None, dict(allo=True, precomp=True)),
            ('Taigi Keyboard (Windows)', layouts.TKW, None, dict(allo=True, precomp=True)),
            ('Wu Shou-Li (Mandarin-extended)', layouts.WSL_HUA, 'desktop', dict(allo=True, precomp=True)),
            ('Taigi Keyboard (Android)', and_lay, and_pos, dict(allo=True, precomp=True)),
            ('Layout A (Dachien-preserving)', full(prop['A']), None, {}),
            ('Layout B (hand-split)', full(prop['B']), None, {}),
            ('Layout C (structured hand-split)', full(prop['C']), None, {}),
            ('Unconstrained reference', full(prop['free']), None, {})]
    with open(OUT / 'scores.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['layout', 'desk_cost', 'phone_s_per_syl', 'phone_index', 'keys_per_syl', 'shift_or_longpress_pct', 'composite'])
        for name, lay, pos, kw in rows:
            desktop_only = pos == 'desktop'
            if desktop_only:   # no phone version: give extra keys dummy phone positions and drop the phone cost
                pos = dict(model.PHPOS); pos.update({k: (0.0, 0.0) for k in model.EXTRA})
            elif pos is not None:
                for c, _ in lay.values():
                    model.EFF.setdefault(c, 0); model.FINGER.setdefault(c, 0); model.ROW.setdefault(c, 0)
            r = model.evaluate(lay, pos, **kw)
            desk = r['desk'] if (pos is None or desktop_only) else None
            phone = None if desktop_only else r['phone']
            comp = None if (desk is None or phone is None) else 50 * (desk / ref['desk'] + phone / ref['phone'])
            sh = shift_share(lay, kw.get('allo', False), kw.get('precomp', False))
            w.writerow([name, desk and round(desk, 3), phone and round(phone, 3), phone and round(100 * phone / ref['phone'], 1),
                        round(r['keys'], 3), round(sh, 1), comp and round(comp, 1)])
            print(f"{name:34s} desk={desk and round(desk,2)} desk_index={desk and round(100*desk/ref['desk'],1)} phone={phone and round(phone,3)} keys={r['keys']:.2f} shift={sh:.1f}% composite={comp and round(comp,1)}")
