"""Sensitivity analysis (Section 3.8): rescore the layouts with changed model constants.
Variants: desktop transition penalties halved and doubled; Fitts slope 0.15 s -> 0.25 s;
mobile reach penalty removed. Each variant is normalized by Taigi-TPS scored under the same variant.
Usage: python sensitivity.py   (prints the table; out/sensitivity.csv)"""
import csv, json, math
import model, layouts
from config import OUT
from evaluate import full

BASE = dict(pair=model.desk_pair, fitts=model.fitts, reach=model.REACH)
VARIANTS = {
    'baseline': {},
    'transition x0.5': dict(pair=lambda a, b: 0.5 * BASE['pair'](a, b)),
    'transition x2': dict(pair=lambda a, b: 2.0 * BASE['pair'](a, b)),
    'Fitts slope 0.25 s': dict(fitts=lambda d, w=1.0: 0.10 + 0.25 * math.log2(d / w + 1)),
    'no reach penalty': dict(reach=lambda pos: 0.0),
}

def set_variant(v):
    model.desk_pair = v.get('pair', BASE['pair'])
    model.fitts = v.get('fitts', BASE['fitts'])
    model.REACH = v.get('reach', BASE['reach'])

if __name__ == '__main__':
    prop = json.load(open(OUT / 'layouts_proposed.json', encoding='utf-8'))
    rows = [('Wu Shou-Li (Taiwanese-dedicated)', layouts.WSL, dict(allo=True, precomp=True)),
            ('Taigi Keyboard (Windows)', layouts.TKW, dict(allo=True, precomp=True)),
            ('Layout A', full(prop['A']), {}), ('Layout B', full(prop['B']), {}),
            ('Layout C', full(prop['C']), {})]
    res = {}
    for vn, v in VARIANTS.items():
        set_variant(v)
        ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
        for name, lay, kw in rows:
            r = model.evaluate(lay, **kw)
            res[(vn, name)] = 50 * (r['desk'] / ref['desk'] + r['phone'] / ref['phone'])
    set_variant({})
    with open(OUT / 'sensitivity.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['layout'] + list(VARIANTS) + ['max_change'])
        for name, _, _ in rows:
            vals = [res[(vn, name)] for vn in VARIANTS]
            ch = max(abs(x - vals[0]) for x in vals)
            w.writerow([name] + [round(x, 1) for x in vals] + [round(ch, 1)])
            print(f"{name:34s} " + ' '.join(f'{x:6.1f}' for x in vals) + f'  max change {ch:.1f}')
    for vn in VARIANTS:
        order = sorted((res[(vn, n)], n) for n, _, _ in rows)
        print(vn, '->', ' < '.join(n for _, n in order))
