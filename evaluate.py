"""Pick the best annealing run per configuration, build the structured Layout C (rules on both halves),
and score all existing and proposed layouts on the full keystroke streams.
Writes out/layouts_proposed.json and out/scores.csv."""
import json, glob, itertools, csv
import numpy as np
import model, layouts, opt
from config import OUT
from units import syl_units

ENT = {'ㆴ': 'ㄅ', 'ㆵ': 'ㄉ', 'ㆻ': 'ㄍ', 'ㆷ': 'ㄏ'}
def full(lay):
    """Proposed input logic: entering finals on ㄅㄉㄍㄏ; ㆱ, and ˇ ˆ where the layout has no key for them, on the secondary layer."""
    d = {u: (c, 0) for u, c in lay.items()}
    for e, b in ENT.items(): d[e] = d[b]
    d['ㆱ'] = (lay['ㆰ'], 1)
    for t, b in (('ˇ', 'ˋ'), ('ˆ', 'ˊ')):   # main-layer key in Layouts A, B and C, else the secondary layer
        d[t] = (lay[t], 0) if t in lay else (lay[b], 1)
    return d

def best_run(mode):
    """The annealing optimizes a bigram approximation of the cost model; its runs are rescored with
    the full model (composite score), and the best run is kept."""
    rs = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(str(OUT / 'runs' / f'{mode}_*.json')))]
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    def comp(r):
        e = model.evaluate(full(dict(r['layout'], **(opt.A_TONES if mode == 'A' else {}))))
        return e['desk'] / ref['desk'] + e['phone'] / ref['phone']
    return min(rs, key=lambda r: (round(comp(r), 9), r['seed']))['layout']

VOWELS = ['ㄚ', 'ㄧ', 'ㄨ', 'ㆤ', 'ㄜ', 'ㆦ']
CODAS = (('ㆰ', 'ㆬ'), ('ㄢ', 'ㄣ'), ('ㄤ', 'ㄥ'))   # (a-rime, coda letter) for -m, -n, -ng
RIGHT_ITERS = 300000

def _anneal_job(args):
    fixed, allowed, iters = args
    return opt.anneal(fixed, allowed, iters=iters, seed=0)[1]

def right_rules(left, score, iters=RIGHT_ITERS):
    """Right half of Layout C, under three rules:
      1. the six single vowels ㄚㄧㄨㆤㄜㆦ lie on the home or bottom row;
      2. ㄚ (home row) shares a column with the a-rimes ㆰ, ㄢ, ㄤ;
      3. ㄧ (home row) shares another column with the coda letters ㆬ, ㄣ, ㄥ, each in the row of the
         a-rime with the same coda, so that the rows read -m, -n and -ng.
    Every pair of columns and every row order is tried; the rest of the right half is annealed, and the
    run with the lowest full-model score is kept. Units absent from opt.U (moved away) are skipped."""
    from multiprocessing import Pool
    units = [u for u in opt.U if u not in left]
    right = [c for c in opt.BC_CELLS if model.FINGER[c] >= 5]
    lower = [c for c in model.ROWS[2] + model.ROWS[3] if c in right]
    cols = [[row[i] for row in model.ROWS] for i in range(min(map(len, model.ROWS)))]
    cols = [col for col in cols if all(c in right for c in col)]
    jobs = []
    for ca, cc in itertools.permutations(cols, 2):
        for rows in itertools.permutations([0, 1, 3]):
            fx = {'ㄚ': ca[2], 'ㄧ': cc[2]}
            for (a, c), r in zip(CODAS, rows):
                if a in units: fx[a] = ca[r]
                if c in units: fx[c] = cc[r]
            fixed = dict(left, **fx)
            free = [c for c in right if c not in fixed.values()]
            allowed = {u: [c for c in (lower if u in VOWELS else right) if c in free] for u in units if u not in fixed}
            jobs.append((fixed, allowed, iters))
    with Pool() as p: lays = p.map(_anneal_job, jobs)
    return min(lays, key=lambda l: round(score(l), 9))

def composite(lay):
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    e = model.evaluate(full(dict(lay, **opt.BC_TONES)))
    return 50 * (e['desk'] / ref['desk'] + e['phone'] / ref['phone'])

def structured(base):
    """Layout C: left half as a place-by-manner grid (exhaustive search), right half under the rules of right_rules."""
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
    return right_rules(fixed, composite)

def shift_share(lay, allo, precomp):
    data = json.load(open(OUT / 'syl.json', encoding='utf-8'))
    tot = sh = 0
    for (I, f, t), c in data:
        seq = model.surface(syl_units(I, f, t), allo=allo, precomp=precomp); tot += c
        if any(u in lay and lay[u][1] == 1 for u in seq): sh += c
    return 100 * sh / tot

if __name__ == '__main__':
    prop = {'A': opt.a_learn(dict(best_run('A'), **opt.A_TONES)), 'B': best_run('B'), 'free': best_run('free')}
    assert {prop['A']['˫'], prop['A']['˪']} == set(opt.A_UPPER), 'Layout A: tones not on R and T'
    prop['C'] = structured(prop['B'])
    for m in ('B', 'C'):   # the two keys B and C leave free take the rare tones ˇ and ˆ
        assert not set(opt.BC_TONES.values()) & set(prop[m].values()), f'Layout {m}: 0 or - is taken'
        prop[m] = dict(prop[m], **opt.BC_TONES)
    json.dump(prop, open(OUT / 'layouts_proposed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    and_lay, and_pos = layouts.android(False)
    rows = [('Taigi-TPS', layouts.TPS, None, dict(allo=True, tps_ent=True)),
            ('Wu Shou-Li (Taiwanese-dedicated)', layouts.WSL, None, dict(allo=True, precomp=True)),
            ('Taigi Keyboard (Windows)', layouts.TKW, None, dict(allo=True, precomp=True)),
            ('Wu Shou-Li (Mandarin-extended)', layouts.WSL_HUA, 'desktop', dict(allo=True, precomp=True)),
            ('Taigi Keyboard (Android)', and_lay, and_pos, dict(allo=True, precomp=True, center=layouts.AND_CENTER)),
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
