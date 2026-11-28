"""Section 5.1: the proposed layouts rescored with the Taigi-TPS entering key instead of the
positional rule (the rime carrying the matching nasal coda, then the key of ˙; tones 4 and 8 on
the same key). The layouts are not re-optimized.
Usage: python tps_entering_variant.py"""
import json
import model, layouts
from config import OUT
from evaluate import full

if __name__ == '__main__':
    prop = json.load(open(OUT / 'layouts_proposed.json', encoding='utf-8'))
    ref = model.evaluate(layouts.TPS, allo=True, tps_ent=True)
    for n in ('A', 'B', 'C'):
        for ent in (False, True):
            r = model.evaluate(full(prop[n]), tps_ent=ent)
            comp = 50 * (r['desk'] / ref['desk'] + r['phone'] / ref['phone'])
            print(f"Layout {n} {'entering key' if ent else 'positional  '} keys/syl={r['keys']:.3f} composite={comp:.1f}")
