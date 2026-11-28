"""Prefix-key variants: rare units move from the main layer to a prefix page entered with
` (first page; or ` then Tab for a separate page) on the desktop, or the symbol key on the phone,
on the key of a related unit.
  P  : the main layer of Layouts A, B and C unchanged (ㄫ on its key; ˇ ˆ on 3 and 5 in Layout A,
       on 0 and - in Layouts B and C), so only ㆱ and the panel-only letters are on the prefix page.
  P+ : additionally ㄫ, ㆡ, ㆭ and ㆰ (each 0.03-0.4%) move to the prefix page, to show the trend;
       the freed keys are re-optimized, with ˇ ˆ (and ˫ ˪ in Layout A) kept on their keys.
Usage: python prefix_variants.py        (optimize and score; out/prefix_variants.json, out/prefix_scores.csv)
       python prefix_variants.py score  (re-score the saved variants only)"""
import json, itertools, csv, os
from multiprocessing import Pool
import numpy as np
import model, opt
from config import OUT
from evaluate import best_run, full

ITERS = int(os.environ.get('ITERS', 1000000))
SEEDS = range(1, 25)
RELATED = {'ㄫ': 'ㄍ', 'ㆡ': 'ㄗ', 'ㆭ': 'ㄥ', 'ㆰ': 'ㄢ', 'ㆱ': 'ㆰ', 'ˇ': 'ˋ', 'ˆ': 'ˊ'}
VARIANTS = {'P': ['ㄫ'], 'P+': ['ㄫ', 'ㆡ', 'ㆭ', 'ㆰ']}
U0 = list(opt.U)

def reduce_units(moved):
    """Rebuild the annealing statistics without the moved units."""
    U = [u for u in U0 if u not in moved]
    idx = {u: i for i, u in enumerate(U)}; SP = len(U); n = SP + 1
    c1 = np.zeros(n); c2 = np.zeros((n, n))
    for seq in model.unit_stream():
        prev = None
        for u in seq:
            u = opt.ENTMAP.get(u, u)
            if u in opt.RARE or u in moved: prev = None; continue
            i = SP if u == '␣' else idx[u]
            c1[i] += 1
            if prev is not None: c2[prev, i] += 1
            prev = i
    opt.U, opt.idx, opt.SP, opt.n, opt.c1, opt.c2 = U, idx, SP, n, c1, c2

def run(args):
    vname, mode, seed = args
    moved = VARIANTS[vname]; reduce_units(moved)
    ini = [u for u in opt.INITIALS if u not in moved]
    if mode == 'A':   # as Layout A: ˇ on 3, ˆ on 5, and the tones ˫ ˪ on R and T
        fixed, allowed = opt.DAQIAN, opt.a_allowed(opt.U)
        allowed.update({t: opt.A_UPPER for t in ('˫', '˪')})
    else:             # as Layouts B and C: initials on the left half, ˇ ˆ on 0 and -
        fixed = {}
        allowed = {u: (opt.LEFT if u in ini else opt.BC_CELLS) for u in opt.U}
    c, lay = opt.anneal(fixed, allowed, iters=ITERS, seed=seed)
    lay = dict(lay, **(opt.A_TONES if mode == 'A' else opt.BC_TONES))
    return vname, mode, seed, (c, lay)

def structured(base, moved):
    reduce_units(moved)
    U, idx, C, cost = opt.U, opt.idx, opt.C, opt.cost
    cellidx = {c: i for i, c in enumerate(C)}
    cols = [['1','q','a','z'], ['2','w','s','x'], ['3','e','d','c'], ['4','r','f','v'], ['5','t','g','b']]
    g0 = {'lab': ['ㄇ','ㄆ','ㄅ','ㆠ'], 'alv': ['ㄋ','ㄊ','ㄉ','ㄌ'], 'vel': ['ㄫ','ㄎ','ㄍ','ㆣ'], 'aff': [None,'ㄘ','ㄗ','ㆡ']}
    groups = {g: [u if u not in moved else None for u in v] for g, v in g0.items()}
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
    lay = {u: base[u] for u in U}
    for g, ci in zip(groups, perm):
        for r, u in enumerate(groups[g]):
            if u: lay[u] = cols[ci][r]
    for u, c in zip(extra, p2): lay[u] = c
    fixed = {u: c for u, c in lay.items() if u in opt.INITIALS or u in extra}
    right = [c for c in opt.BC_CELLS if c not in fixed.values()]
    runs = [opt.anneal(fixed, {u: right for u in U if u not in fixed}, iters=150000, seed=s) for s in range(4)]
    return dict(min(runs, key=lambda r: r[0])[1], **opt.BC_TONES)

def with_prefix(lay, moved, merged=False):
    from prefix_panel import panel
    d = full_main(lay)
    for u, key in panel(lay, moved, merged).items():
        if u in RELATED: d[u] = (key, 2)
    for e, b in {'ㆴ': 'ㄅ', 'ㆵ': 'ㄉ', 'ㆻ': 'ㄍ', 'ㆷ': 'ㄏ'}.items(): d[e] = (lay[b], 0)
    return d

def base_layout(name):
    """Variant P keeps the main layer of the base layout."""
    return json.load(open(OUT / 'layouts_proposed.json', encoding='utf-8'))[name]

def full_main(lay):
    return {u: (c, 0) for u, c in lay.items()}

def score(res=None):
    """Score the variants twice: TPS symbols on a separate page (` Tab key) and merged into
    the first page of the panel (` key). The layouts do not depend on this choice, because the
    annealing ignores moved units."""
    import layouts
    if res is None: res = json.load(open(OUT / 'prefix_variants.json', encoding='utf-8'))
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    base = json.load(open(OUT / 'layouts_proposed.json', encoding='utf-8'))
    rows = [(n, '-', full(base[n])) for n in ('A', 'B', 'C')]
    for page in ('separate', 'merged'):
        for v, moved in VARIANTS.items():
            for n in ('A', 'B', 'C'):
                rows.append((f'{n}-{v}', page, with_prefix(res[f'{n}-{v}'], moved, page == 'merged')))
    with open(OUT / 'prefix_scores.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['layout', 'prefix_page', 'desk_index', 'phone_index', 'keys_per_syl', 'composite'])
        for name, page, lay in rows:
            model.PREFIX_TAB = page != 'merged'
            r = model.evaluate(lay)
            di, pi = 100 * r['desk'] / ref['desk'], 100 * r['phone'] / ref['phone']
            w.writerow([name, page, round(di, 1), round(pi, 1), round(r['keys'], 3), round((di + pi) / 2, 1)])
            print(f"{name:8s} {page:8s} desk_index={di:.1f} phone_index={pi:.1f} keys={r['keys']:.3f} composite={(di+pi)/2:.1f}")
    model.PREFIX_TAB = True

if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['score']:
        score(); raise SystemExit
    # Variant P is not optimized (see base_layout); the P+ runs are rescored with the full model (TPS
    # letters on the first page of the panel) and the best run is kept, as in evaluate.best_run.
    jobs = [('P+', m, s) for m in ('A', 'B') for s in SEEDS]
    import layouts
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    model.PREFIX_TAB = False
    best = {}
    with Pool() as p:
        for v, m, s, (c, lay) in p.imap_unordered(run, jobs):
            e = model.evaluate(with_prefix(lay, VARIANTS[v], True))
            comp = e['desk'] / ref['desk'] + e['phone'] / ref['phone']
            key = (round(comp, 9), s)
            if (v, m) not in best or key < best[(v, m)][0]: best[(v, m)] = (key, lay)
    model.PREFIX_TAB = True
    res = {}
    for n in ('A', 'B', 'C'): res[f'{n}-P'] = base_layout(n)
    res['A-P+'] = best[('P+', 'A')][1]
    res['B-P+'] = best[('P+', 'B')][1]
    res['C-P+'] = structured(best[('P+', 'B')][1], VARIANTS['P+'])
    json.dump(res, open(OUT / 'prefix_variants.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    score(res)
