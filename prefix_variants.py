"""Prefix-key variants A-P, B-P and C-P: the main layer of Layouts A, B and C unchanged (ㄫ on its key;
ˇ ˆ on 3 and 5 in Layout A, on 0 and - in Layouts B and C), with ㆱ and the panel-only letters on the
prefix page, entered with ` on the desktop (first page; or ` then Tab for a separate page) or the
symbol key on the phone, on the key of a related unit.
Usage: python prefix_variants.py   (out/prefix_variants.json, out/prefix_scores.csv)"""
import json, csv
import model, layouts
from config import OUT
from evaluate import full

RELATED = {'ㄫ': 'ㄍ', 'ㆡ': 'ㄗ', 'ㆭ': 'ㄥ', 'ㆰ': 'ㄢ', 'ㆱ': 'ㆰ', 'ˇ': 'ˋ', 'ˆ': 'ˊ'}
MOVED = ['ㄫ']   # candidates for the prefix page; a unit the layout keeps on the main layer stays there

def with_prefix(lay, merged=False):
    from prefix_panel import panel
    d = {u: (c, 0) for u, c in lay.items()}
    for u, key in panel(lay, MOVED, merged).items():
        if u in RELATED: d[u] = (key, 2)
    for e, b in {'ㆴ': 'ㄅ', 'ㆵ': 'ㄉ', 'ㆻ': 'ㄍ', 'ㆷ': 'ㄏ'}.items(): d[e] = (lay[b], 0)
    return d

def score(res):
    """Score each variant twice: TPS letters on a separate page (` Tab key) and merged into the
    first page of the panel (` key)."""
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    base = json.load(open(OUT / 'layouts_proposed.json', encoding='utf-8'))
    rows = [(n, '-', full(base[n])) for n in ('A', 'B', 'C')]
    for page in ('separate', 'merged'):
        for n in ('A', 'B', 'C'):
            rows.append((f'{n}-P', page, with_prefix(res[f'{n}-P'], page == 'merged')))
    with open(OUT / 'prefix_scores.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['layout', 'prefix_page', 'desk_index', 'phone_index', 'keys_per_syl', 'composite'])
        for name, page, lay in rows:
            model.PREFIX_TAB = page != 'merged'
            r = model.evaluate(lay)
            di, pi = 100 * r['desk'] / ref['desk'], 100 * r['phone'] / ref['phone']
            w.writerow([name, page, round(di, 1), round(pi, 1), round(r['keys'], 3), round((di + pi) / 2, 1)])
            print(f"{name:6s} {page:8s} desk_index={di:.1f} phone_index={pi:.1f} keys={r['keys']:.3f} composite={(di+pi)/2:.1f}")
    model.PREFIX_TAB = True

if __name__ == '__main__':
    base = json.load(open(OUT / 'layouts_proposed.json', encoding='utf-8'))
    res = {f'{n}-P': base[n] for n in ('A', 'B', 'C')}
    json.dump(res, open(OUT / 'prefix_variants.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    score(res)
