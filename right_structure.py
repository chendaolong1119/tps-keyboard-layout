"""Exploratory: Layout C with a structured right half.
  V0 : right half annealed on cost alone (Layout C before the right-half rules; 73.6)
  V1 : the six single vowels ㄚㄧㄨㆤㄜㆦ on the home or bottom row of the right half
  V2 : V1, and ㄚ with its coda rimes ㄢ ㄤ ㆰ in one column (ㄚ on the home row)
  V3 : (adopted as Layout C; 75.2) V2, and ㄧ with the coda letters ㆬ ㄣ ㄥ in another column, each coda letter in the row of
       the a-rime with the same coda (ㆬ beside ㆰ, ㄣ beside ㄢ, ㄥ beside ㄤ)
The left half of Layout C and ˇ ˆ on 0 and - stay fixed; the rest of the right half is annealed,
and every run is rescored with the full model.  Usage: python right_structure.py"""
import json, itertools
from multiprocessing import Pool
import model, layouts, opt
from config import OUT
from evaluate import full

C = json.load(open(OUT / 'layouts_proposed.json', encoding='utf-8'))['C']
RIGHT = [c for c in opt.BC_CELLS if model.FINGER[c] >= 5]
LEFT_FIXED = {u: c for u, c in C.items() if c not in RIGHT and u in opt.U}
VOWELS = ['ㄚ', 'ㄧ', 'ㄨ', 'ㆤ', 'ㄜ', 'ㆦ']
ROWS = {r: [c for c in row if c in RIGHT] for r, row in zip('ntHb', model.ROWS)}
LOWER = ROWS['H'] + ROWS['b']
COLS = [[row[i] for row in model.ROWS] for i in range(min(map(len, model.ROWS)))]
ACOLS = [col for col in COLS if all(c in RIGHT for c in col)]
REF = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
ITERS, SEEDS = 300000, range(6)

def comp(lay):
    e = model.evaluate(full(dict(lay, **opt.BC_TONES)))
    return 50 * (e['desk'] / REF['desk'] + e['phone'] / REF['phone']), e

def job(args):
    name, fixed_extra, seed = args
    fixed = dict(LEFT_FIXED, **fixed_extra)
    free = [c for c in RIGHT if c not in fixed.values()]
    allowed = {u: (LOWER if (u in VOWELS and name != 'V0') else free) for u in opt.U if u not in fixed}
    allowed = {u: [c for c in v if c in free] for u, v in allowed.items()}
    _, lay = opt.anneal(fixed, allowed, iters=ITERS, seed=seed)
    return name, fixed_extra, seed, lay

if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['V3']:
        names = ('V3',); jobs = []
        for ca, cc in itertools.permutations(ACOLS, 2):
            for rows in itertools.permutations([0, 1, 3]):   # rows of the m, n, ng codas
                fx = {'ㄚ': ca[2], 'ㄧ': cc[2]}
                for (a, c), r in zip((('ㆰ', 'ㆬ'), ('ㄢ', 'ㄣ'), ('ㄤ', 'ㄥ')), rows): fx[a] = ca[r]; fx[c] = cc[r]
                jobs.append(('V3', fx, 0))
    else:
        names = ('V0', 'V1', 'V2'); jobs = []
    jobs += [('V0', {}, s) for s in SEEDS] + [('V1', {}, s) for s in SEEDS] if names[0] == 'V0' else []
    for col in (ACOLS if names[0] == 'V0' else []):            # col = [number, top, home, bottom]
        for perm in itertools.permutations(['ㄢ', 'ㄤ', 'ㆰ']):
            fx = {'ㄚ': col[2], perm[0]: col[0], perm[1]: col[1], perm[2]: col[3]}
            jobs += [('V2', fx, s) for s in SEEDS[:2]]
    best = {}
    with Pool() as p:
        for name, fx, seed, lay in p.imap_unordered(job, jobs):
            c, e = comp(lay)
            if name not in best or c < best[name][0]: best[name] = (c, e, lay)
    print('Layout C:', round(comp(C)[0], 2))
    out = {}
    for name in names:
        c, e, lay = best[name]
        print(f"{name}: composite={c:.2f} desk_index={100*e['desk']/REF['desk']:.1f} phone_index={100*e['phone']/REF['phone']:.1f}")
        inv = {v: k for k, v in dict(lay, **opt.BC_TONES).items()}
        for row in model.ROWS: print('   ', ' '.join(inv.get(c, '·') for c in row if c in RIGHT + ['0', '-']))
        out[name] = dict(lay, **opt.BC_TONES)
    fn = OUT / 'right_structure.json'
    prev = json.load(open(fn, encoding='utf-8')) if fn.exists() else {}
    json.dump(dict(prev, **out), open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
